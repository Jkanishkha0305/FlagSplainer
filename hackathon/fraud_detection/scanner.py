"""
Agent responsible for fetching transaction data from MCP sources.
"""

from __future__ import annotations

import asyncio
from typing import Dict, List

from ..config import Config
from .mcp_fetcher import MCPConfigError, MCPFetchError, fetch_transactions_from_mcp
from .state import FraudState


def _parse_transaction_data(raw_data: List[Dict], transaction_type: str) -> List[Dict]:
    """Parse and normalize transaction data from MCP."""
    transactions = []

    for record in raw_data:
        try:
            # Handle nested data structure from Kafka
            data = record.get("value", record) if "value" in record else record

            if transaction_type == "cc":
                transactions.append({
                    "transaction_id": data.get("transaction_id", data.get("id", "unknown")),
                    "customer_id": data.get("customer_id", "unknown"),
                    "merchant": data.get("merchant", "unknown"),
                    "category": data.get("category", "unknown"),
                    "amount": float(data.get("amount", 0)),
                    "status": data.get("status", "unknown"),
                    "location": data.get("location", {}),
                    "is_fraud": data.get("is_fraud", False),
                })
            else:  # paypal
                transactions.append({
                    "transaction_id": data.get("transaction_id", data.get("id", "unknown")),
                    "customer_id": data.get("customer_id", "unknown"),
                    "merchant": data.get("merchant", "unknown"),
                    "category": data.get("category", "unknown"),
                    "amount": float(data.get("amount", 0)),
                    "status": data.get("status", "unknown"),
                    "account_country": data.get("account_country", "US"),
                    "location": data.get("location", {}),
                    "is_fraud": data.get("is_fraud", False),
                    "fraud_indicators": data.get("fraud_indicators", {}),
                })
        except Exception as exc:
            print(f"  ⚠️  Error parsing transaction: {exc}")
            continue

    return transactions


def _fallback_sample_data() -> Dict[str, List[Dict]]:
    """Return sample transactions if fetching fails."""
    return {
        "cc_transactions": [
            {
                "transaction_id": "CC-7646760370",
                "customer_id": "CUST-007413",
                "merchant": "Shell Gas",
                "category": "Clothing",
                "amount": 412.72,
                "status": "approved",
                "location": {"city": "Houston", "state": "FL"},
                "is_fraud": False,
            }
        ],
        "paypal_transactions": [
            {
                "transaction_id": "PP-9859481656",
                "customer_id": "CUST-001933",
                "merchant": "Starbucks",
                "category": "Gas",
                "amount": 412.19,
                "status": "completed",
                "account_country": "FR",
                "location": {"city": "Philadelphia", "state": "IL", "country": "FR"},
                "is_fraud": False,
                "fraud_indicators": {
                    "is_foreign_account": False,
                    "account_age_days": 423,
                },
            }
        ],
    }


async def scanner_agent_async(state: FraudState) -> FraudState:
    """
    Fetch transactions from both credit card and PayPal topics using MCP.
    """
    print("\n" + "=" * 60)
    print("🔍 SCANNER AGENT - Fetching Transactions via MCP")
    print("=" * 60)

    # Fast path: use direct MCP client helpers if configured.
    try:
        print("→ Attempting direct MCP fetch using lenses_mcp clients...")
        cc_raw, pp_raw = await asyncio.to_thread(fetch_transactions_from_mcp, Config.FETCH_LIMIT)
        cc_tx = _parse_transaction_data(cc_raw, "cc")
        pp_tx = _parse_transaction_data(pp_raw, "paypal")
        if cc_tx or pp_tx:
            state["cc_transactions"] = cc_tx
            state["paypal_transactions"] = pp_tx
            print(f"✓ MCP client fetch succeeded: {len(cc_tx)} credit card, {len(pp_tx)} PayPal records")
            return state
        print("⚠️  MCP client fetch returned no records – using sample data.")
    except (MCPConfigError, MCPFetchError) as exc:
        print(f"⚠️  MCP client unavailable: {exc}")
    except Exception as exc:  # pragma: no cover - safety net
        print(f"⚠️  Unexpected MCP client error: {exc}")

    fallback = _fallback_sample_data()
    state["cc_transactions"] = fallback["cc_transactions"]
    state["paypal_transactions"] = fallback["paypal_transactions"]
    return state



def scanner_agent(state: FraudState) -> FraudState:
    """
    Synchronous wrapper for scanner_agent_async.
    """
    import asyncio

    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

    return loop.run_until_complete(scanner_agent_async(state))
