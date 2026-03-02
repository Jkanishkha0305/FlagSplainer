"""
Command helpers for executing the fraud detection workflow.
"""

from __future__ import annotations

from typing import Dict

from .graph import build_fraud_detection_graph
from .state import FraudState


def run_fraud_detection() -> FraudState:
    """Execute the entire fraud detection pipeline."""
    print("\n" + "=" * 60)
    print("🚨 2-AGENT FRAUD DETECTION SYSTEM")
    print("=" * 60)
    print("Data Sources: Credit Card + PayPal Transactions")
    print("=" * 60)

    app = build_fraud_detection_graph()
    initial_state: Dict[str, object] = {
        "cc_transactions": [],
        "paypal_transactions": [],
        "fraud_alerts": [],
        "summary": "",
    }

    final_state = app.invoke(initial_state)  # type: ignore[assignment]

    print("\n" + "=" * 60)
    print("📊 FINAL RESULTS")
    print("=" * 60)
    print(final_state["summary"])

    if final_state["fraud_alerts"]:
        print("\n" + "=" * 60)
        print("🚨 DETAILED ALERTS")
        print("=" * 60)

        sorted_alerts = sorted(final_state["fraud_alerts"], key=lambda item: item["risk_score"], reverse=True)

        for index, alert in enumerate(sorted_alerts, 1):
            print(f"\n[{index}] Customer: {alert['customer_id']}")
            print(f"    Pattern: {alert['pattern']}")
            print(f"    Risk Score: {alert['risk_score']}/10")
            print(f"    Description: {alert['description']}")
            print(f"    Recommendation: {alert['recommendation']}")
            print(f"    Evidence: {alert['evidence']}")

    print("\n" + "=" * 60)
    print("✅ Fraud detection complete!")
    print("=" * 60)

    return final_state  # type: ignore[return-value]


if __name__ == "__main__":
    run_fraud_detection()

