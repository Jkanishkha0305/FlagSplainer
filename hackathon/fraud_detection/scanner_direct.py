"""
Direct Lenses API scanner - bypasses MCP for direct Kafka access.
"""

from __future__ import annotations

import json
from typing import Dict, List

from ..config import Config
from .lenses_client import create_lenses_client
from .state import FraudState


async def _fetch_via_lenses_sql(client, topic: str, limit: int) -> List[Dict]:
    """
    Fetch transactions directly from Lenses API using SQL.
    This is what the MCP server does internally.
    """
    try:
        sql_query = f"SELECT * FROM `{topic}` LIMIT {limit}"

        result = await client.execute_sql(
            environment=Config.LENSES_ENVIRONMENT,
            sql=sql_query
        )

        return result if result else []

    except Exception as exc:
        print(f"  ✗ Error fetching from {topic}: {exc}")
        return []


def _parse_transaction_data(raw_data: List[Dict], transaction_type: str) -> List[Dict]:
    """Parse and normalize transaction data."""
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


async def scanner_agent_direct_async(state: FraudState) -> FraudState:
    """
    Fetch transactions directly from Lenses API (bypasses MCP).
    """
    print("\n" + "=" * 60)
    print("🔍 SCANNER AGENT - Fetching via Direct Lenses API")
    print("=" * 60)

    # Create Lenses WebSocket client
    client = create_lenses_client()

    if client is None:
        print("⚠️  Lenses WebSocket client not available – using sample data.")
        fallback = _fallback_sample_data()
        state["cc_transactions"] = fallback["cc_transactions"]
        state["paypal_transactions"] = fallback["paypal_transactions"]
        return state

    try:
        print(f"→ Connecting to Lenses at {Config.LENSES_API_WEBSOCKET_URL}:{Config.LENSES_API_WEBSOCKET_PORT}")
        print(f"→ Environment: '{Config.LENSES_ENVIRONMENT}'")

        print(f"→ Fetching from topic '{Config.CC_TOPIC}'...")
        cc_raw = await _fetch_via_lenses_sql(client, Config.CC_TOPIC, Config.FETCH_LIMIT)

        print(f"→ Fetching from topic '{Config.PAYPAL_TOPIC}'...")
        pp_raw = await _fetch_via_lenses_sql(client, Config.PAYPAL_TOPIC, Config.FETCH_LIMIT)

        # Parse the data
        state["cc_transactions"] = _parse_transaction_data(cc_raw, "cc")
        state["paypal_transactions"] = _parse_transaction_data(pp_raw, "paypal")

        print(f"✓ Found {len(state['cc_transactions'])} credit card transactions")
        print(f"✓ Found {len(state['paypal_transactions'])} PayPal transactions")

    except Exception as exc:
        print(f"✗ Lenses API Error: {exc}")
        print(f"  Using sample data for demo")
        fallback = _fallback_sample_data()
        state["cc_transactions"] = fallback["cc_transactions"]
        state["paypal_transactions"] = fallback["paypal_transactions"]

    return state


def scanner_agent_direct(state: FraudState) -> FraudState:
    """Synchronous wrapper for direct scanner."""
    import asyncio

    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

    return loop.run_until_complete(scanner_agent_direct_async(state))
