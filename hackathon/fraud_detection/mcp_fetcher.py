"""
Helpers for pulling transaction data from Lenses MCP without relying on an LLM.
"""

from __future__ import annotations

import asyncio
import json
import os
from pathlib import Path
from typing import Dict, Iterable, List, Tuple

import sys

# Ensure the project src/ directory (which hosts lenses_mcp) is importable.
ROOT_DIR = Path(__file__).resolve().parents[2]
SRC_DIR = ROOT_DIR / "src"
if SRC_DIR.exists() and str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))
LENSES_MCP_DIR = SRC_DIR / "lenses_mcp"
if LENSES_MCP_DIR.exists() and str(LENSES_MCP_DIR) not in sys.path:
    sys.path.insert(0, str(LENSES_MCP_DIR))

IMPORT_ERROR: Exception | None = None

try:  # pragma: no cover - optional dep lives in src
    from lenses_mcp.clients.websocket_client import (
        LENSES_API_WEBSOCKET_BASE_URL,
        LensesWebSocketClient,
        websocket_client,
    )
except ImportError as exc:  # noqa: F401
    IMPORT_ERROR = exc
    LensesWebSocketClient = None  # type: ignore[assignment]
    websocket_client = None  # type: ignore[assignment]
    LENSES_API_WEBSOCKET_BASE_URL = None  # type: ignore[assignment]


class MCPConfigError(RuntimeError):
    """Raised when mandatory MCP configuration is missing."""


class MCPFetchError(RuntimeError):
    """Raised when MCP data retrieval fails."""


def _resolve_environment() -> str:
    candidates = (
        os.getenv("LENSES_ENVIRONMENT"),
        os.getenv("LENSES_ENV"),
        os.getenv("LENSES_DEFAULT_ENV"),
        "financial-data",
    )
    for value in candidates:
        if value:
            return value
    raise MCPConfigError("Lenses environment not configured (set LENSES_ENVIRONMENT or LENSES_ENV).")


async def _fetch_topic_records(
    env: str,
    topic: str,
    limit: int,
    client: LensesWebSocketClient,
) -> List[Dict]:
    endpoint = f"/api/v1/environments/{env}/proxy/api/ws/v2/sql/execute"
    # `_ts` is provided by Lenses for ingestion ordering; fall back to timestamp when missing.
    sql = f"""
        SELECT *
        FROM `{topic}`
        ORDER BY
            COALESCE(_ts, ts, timestamp, event_timestamp) DESC
        LIMIT {limit}
    """
    try:
        records = await client._make_request(endpoint=endpoint, sql=sql)  # type: ignore[union-attr]
    except Exception as exc:  # pragma: no cover - network boundary
        raise MCPFetchError(f"Failed to fetch records for topic '{topic}': {exc}") from exc

    return _normalise_records(records)


def _normalise_records(records: Iterable) -> List[Dict]:
    normalised: List[Dict] = []
    for record in records or []:
        candidate = record
        if isinstance(record, dict) and "value" in record:
            candidate = record["value"]

        if isinstance(candidate, str):
            candidate = candidate.strip()
            if not candidate:
                continue
            try:
                candidate = json.loads(candidate)
            except json.JSONDecodeError:
                continue

        if isinstance(candidate, dict):
            normalised.append(candidate)
    return normalised


async def _fetch_all_async(limit: int) -> Tuple[List[Dict], List[Dict]]:
    if websocket_client is None:
        base_msg = "lenses_mcp package is unavailable. Install project dependencies to enable MCP fetch."
        if IMPORT_ERROR is not None:
            base_msg += f" (import error: {IMPORT_ERROR})"
        raise MCPConfigError(base_msg)

    env = _resolve_environment()
    api_key = os.getenv("LENSES_API_KEY")
    if not api_key:
        raise MCPConfigError("LENSES_API_KEY not configured; update your .env to enable MCP fetch.")

    cc_topic = os.getenv("CC_TOPIC_NAME", "credit-card-transactions")
    paypal_topic = os.getenv("PAYPAL_TOPIC_NAME", "paypal-transactions")

    cc_records, paypal_records = await asyncio.gather(
        _fetch_topic_records(env, cc_topic, limit, websocket_client),
        _fetch_topic_records(env, paypal_topic, limit, websocket_client),
    )

    return cc_records, paypal_records


def fetch_transactions_from_mcp(limit: int = 20) -> Tuple[List[Dict], List[Dict]]:
    """
    Retrieve recent credit card and PayPal transactions directly from MCP.

    Returns:
        Tuple of (credit_card_transactions, paypal_transactions)
    """
    try:
        return asyncio.run(_fetch_all_async(limit))
    except RuntimeError as exc:
        if "asyncio.run()" in str(exc):
            # Already inside an event loop – create a dedicated loop.
            loop = asyncio.new_event_loop()
            try:
                return loop.run_until_complete(_fetch_all_async(limit))
            finally:
                loop.close()
        raise
