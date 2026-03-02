"""
Sample data scanner - simulates MCP data streaming.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, List

from ..config import Config
from .state import FraudState


def load_sample_transactions() -> Dict[str, List[Dict]]:
    """Load sample transactions from file or generate them."""
    sample_file = Path(__file__).parent.parent / "sample_transactions.json"

    if sample_file.exists():
        with open(sample_file, "r") as f:
            return json.load(f)
    else:
        # Inline sample data if file doesn't exist
        return {
            "cc_transactions": [
                {
                    "transaction_id": "CC-0000000001",
                    "customer_id": "CUST-007413",
                    "merchant": "Shell Gas",
                    "category": "Clothing",
                    "amount": 412.72,
                    "status": "approved",
                    "location": {"city": "Houston", "state": "FL"},
                    "is_fraud": True,
                },
                {
                    "transaction_id": "CC-0000000002",
                    "customer_id": "CUST-008521",
                    "merchant": "Walmart",
                    "category": "Grocery",
                    "amount": 87.23,
                    "status": "approved",
                    "location": {"city": "Los Angeles", "state": "CA"},
                    "is_fraud": False,
                },
            ],
            "paypal_transactions": [
                {
                    "transaction_id": "PP-0000000001",
                    "customer_id": "CUST-001933",
                    "merchant": "Starbucks",
                    "category": "Gas",
                    "amount": 412.19,
                    "status": "completed",
                    "account_country": "FR",
                    "location": {"city": "Philadelphia", "state": "IL", "country": "FR"},
                    "is_fraud": True,
                    "fraud_indicators": {
                        "is_foreign_account": True,
                        "account_age_days": 423,
                    },
                },
                {
                    "transaction_id": "PP-0000000002",
                    "customer_id": "CUST-002145",
                    "merchant": "eBay",
                    "category": "Shopping",
                    "amount": 52.99,
                    "status": "completed",
                    "account_country": "US",
                    "location": {"city": "New York", "state": "NY", "country": "US"},
                    "is_fraud": False,
                    "fraud_indicators": {
                        "is_foreign_account": False,
                        "account_age_days": 850,
                    },
                },
            ],
        }


def scanner_agent_sample(state: FraudState) -> FraudState:
    """
    Scanner using sample data (simulates MCP streaming).
    """
    print("\n" + "=" * 60)
    print("🔍 SCANNER AGENT - Loading Sample Data (MCP Simulation)")
    print("=" * 60)
    print("💡 This simulates what MCP would return from Kafka topics")
    print("=" * 60)

    try:
        # Load sample data
        print(f"→ Simulating MCP fetch from '{Config.CC_TOPIC}'...")
        print(f"→ Simulating MCP fetch from '{Config.PAYPAL_TOPIC}'...")

        data = load_sample_transactions()

        state["cc_transactions"] = data["cc_transactions"][: Config.FETCH_LIMIT]
        state["paypal_transactions"] = data["paypal_transactions"][: Config.FETCH_LIMIT]

        print(f"✓ Loaded {len(state['cc_transactions'])} credit card transactions")
        print(f"✓ Loaded {len(state['paypal_transactions'])} PayPal transactions")

        # Show what was loaded
        fraud_cc = sum(1 for tx in state["cc_transactions"] if tx.get("is_fraud"))
        fraud_pp = sum(1 for tx in state["paypal_transactions"] if tx.get("is_fraud"))

        print(
            f"📊 Data summary: {fraud_cc + fraud_pp} fraudulent out of {len(state['cc_transactions']) + len(state['paypal_transactions'])} total"
        )

    except Exception as exc:
        print(f"✗ Error loading sample data: {exc}")
        state["cc_transactions"] = []
        state["paypal_transactions"] = []

    return state
