"""
Shared state definitions for the fraud detection workflow.
"""

from typing import Dict, List, TypedDict


class FraudState(TypedDict):
    """Typed state shared across agents."""

    # Data fetched from sources
    cc_transactions: List[Dict]
    paypal_transactions: List[Dict]

    # Results produced by analysis
    fraud_alerts: List[Dict]
    summary: str

