#!/usr/bin/env python3
"""
Generate realistic sample transaction data for fraud detection testing.
"""

import json
import random
from datetime import datetime, timedelta
from typing import List, Dict


def generate_cc_transaction(transaction_id: int, is_fraud: bool = False) -> Dict:
    """Generate a credit card transaction."""
    customer_id = f"CUST-{random.randint(1000, 9999):06d}"

    # Normal merchants vs suspicious ones
    if is_fraud:
        # Create category mismatches (fraud pattern)
        merchants = [
            ("Shell Gas", "Clothing"),
            ("Exxon", "Electronics"),
            ("Starbucks", "Gas"),
            ("McDonald's", "Jewelry"),
        ]
        merchant, category = random.choice(merchants)
        amount = random.uniform(100, 1500)
        status = random.choice(["approved", "approved", "declined"])
    else:
        merchant_categories = [
            ("Walmart", "Grocery"),
            ("Amazon", "Shopping"),
            ("Target", "Retail"),
            ("Whole Foods", "Grocery"),
            ("Best Buy", "Electronics"),
        ]
        merchant, category = random.choice(merchant_categories)
        amount = random.uniform(10, 300)
        status = "approved"

    states = ["CA", "NY", "TX", "FL", "IL", "PA"]
    cities = ["Los Angeles", "New York", "Houston", "Miami", "Chicago", "Philadelphia"]

    return {
        "transaction_id": f"CC-{transaction_id:010d}",
        "customer_id": customer_id,
        "merchant": merchant,
        "category": category,
        "amount": round(amount, 2),
        "status": status,
        "timestamp": (datetime.now() - timedelta(minutes=random.randint(0, 120))).isoformat(),
        "location": {
            "city": random.choice(cities),
            "state": random.choice(states)
        },
        "is_fraud": is_fraud
    }


def generate_paypal_transaction(transaction_id: int, is_fraud: bool = False) -> Dict:
    """Generate a PayPal transaction."""
    customer_id = f"CUST-{random.randint(1000, 9999):06d}"

    if is_fraud:
        # Foreign account + high amounts (fraud pattern)
        countries = ["FR", "RU", "CN", "BR", "NG"]
        account_country = random.choice(countries)
        amount = random.uniform(500, 2000)
        status = random.choice(["completed", "pending", "failed"])

        # Category mismatch
        merchants = [
            ("Starbucks", "Gas"),
            ("Shell Gas", "Clothing"),
            ("Apple Store", "Automotive"),
        ]
        merchant, category = random.choice(merchants)
    else:
        account_country = "US"
        amount = random.uniform(10, 200)
        status = "completed"

        merchant_categories = [
            ("PayPal Transfer", "Transfer"),
            ("eBay", "Shopping"),
            ("Etsy", "Handmade"),
        ]
        merchant, category = random.choice(merchant_categories)

    return {
        "transaction_id": f"PP-{transaction_id:010d}",
        "customer_id": customer_id,
        "merchant": merchant,
        "category": category,
        "amount": round(amount, 2),
        "status": status,
        "account_country": account_country,
        "timestamp": (datetime.now() - timedelta(minutes=random.randint(0, 120))).isoformat(),
        "location": {
            "city": "Various",
            "state": "Online",
            "country": account_country
        },
        "is_fraud": is_fraud,
        "fraud_indicators": {
            "is_foreign_account": account_country != "US",
            "account_age_days": random.randint(1, 1000)
        }
    }


def generate_dataset(num_cc: int = 20, num_paypal: int = 20, fraud_rate: float = 0.3) -> Dict[str, List[Dict]]:
    """Generate a complete dataset with specified fraud rate."""

    print(f"Generating {num_cc} credit card and {num_paypal} PayPal transactions...")
    print(f"Fraud rate: {fraud_rate * 100:.0f}%")

    cc_transactions = []
    for i in range(num_cc):
        is_fraud = random.random() < fraud_rate
        cc_transactions.append(generate_cc_transaction(i + 1, is_fraud))

    paypal_transactions = []
    for i in range(num_paypal):
        is_fraud = random.random() < fraud_rate
        paypal_transactions.append(generate_paypal_transaction(i + 1, is_fraud))

    actual_fraud_cc = sum(1 for tx in cc_transactions if tx["is_fraud"])
    actual_fraud_pp = sum(1 for tx in paypal_transactions if tx["is_fraud"])

    print(f"\n✓ Generated {len(cc_transactions)} CC transactions ({actual_fraud_cc} fraudulent)")
    print(f"✓ Generated {len(paypal_transactions)} PayPal transactions ({actual_fraud_pp} fraudulent)")

    return {
        "cc_transactions": cc_transactions,
        "paypal_transactions": paypal_transactions
    }


if __name__ == "__main__":
    # Generate sample data
    data = generate_dataset(num_cc=20, num_paypal=20, fraud_rate=0.3)

    # Save to file
    output_file = "sample_transactions.json"
    with open(output_file, "w") as f:
        json.dump(data, f, indent=2)

    print(f"\n✓ Saved to {output_file}")

    # Show samples
    print("\n" + "=" * 60)
    print("Sample Credit Card Transaction:")
    print("=" * 60)
    print(json.dumps(data["cc_transactions"][0], indent=2))

    print("\n" + "=" * 60)
    print("Sample PayPal Transaction:")
    print("=" * 60)
    print(json.dumps(data["paypal_transactions"][0], indent=2))
