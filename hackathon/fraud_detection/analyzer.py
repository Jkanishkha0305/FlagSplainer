"""
Agent that inspects transactions and generates fraud alerts.
"""

from __future__ import annotations

import json
from typing import Dict, List

try:
    from openai import OpenAI
except ImportError:
    OpenAI = None  # type: ignore[assignment]

from ..config import Config
from .state import FraudState


def _build_customer_map(cc_txns: List[Dict], pp_txns: List[Dict]) -> Dict[str, Dict[str, List[Dict]]]:
    """Group transactions by customer and channel."""
    customer_data: Dict[str, Dict[str, List[Dict]]] = {}

    for tx in cc_txns:
        cust_id = tx.get("customer_id")
        customer_data.setdefault(cust_id, {"cc": [], "paypal": []})["cc"].append(tx)

    for tx in pp_txns:
        cust_id = tx.get("customer_id")
        customer_data.setdefault(cust_id, {"cc": [], "paypal": []})["paypal"].append(tx)

    return customer_data


def _ai_powered_analysis(cc_txns: List[Dict], pp_txns: List[Dict], rule_based_alerts: List[Dict]) -> Dict[str, any]:
    """
    Use OpenAI to provide intelligent fraud analysis beyond rule-based detection.
    """
    if OpenAI is None:
        return {
            "ai_insights": "OpenAI not available - install with: pip install openai",
            "additional_alerts": []
        }

    if not Config.OPENAI_API_KEY:
        return {
            "ai_insights": "OpenAI API key not configured",
            "additional_alerts": []
        }

    try:
        client = OpenAI(api_key=Config.OPENAI_API_KEY)

        # Prepare transaction summary for AI analysis
        summary_data = {
            "total_cc_transactions": len(cc_txns),
            "total_paypal_transactions": len(pp_txns),
            "total_cc_amount": sum(tx.get("amount", 0) for tx in cc_txns),
            "total_pp_amount": sum(tx.get("amount", 0) for tx in pp_txns),
            "rule_based_alerts_count": len(rule_based_alerts),
            "sample_cc_transactions": cc_txns[:5] if cc_txns else [],
            "sample_pp_transactions": pp_txns[:5] if pp_txns else [],
            "rule_patterns_detected": [alert["pattern"] for alert in rule_based_alerts[:10]]
        }

        prompt = f"""You are a fraud detection expert analyzing credit card and PayPal transactions.

Transaction Summary:
{json.dumps(summary_data, indent=2)}

Rule-based system detected {len(rule_based_alerts)} potential fraud cases.

Your task:
1. Analyze the transaction patterns for additional fraud indicators not caught by rules
2. Assess the overall fraud risk level (LOW, MEDIUM, HIGH, CRITICAL)
3. Identify any sophisticated fraud patterns (e.g., velocity attacks, card testing, account takeover)
4. Provide actionable recommendations

Return a JSON response with:
{{
  "risk_level": "LOW|MEDIUM|HIGH|CRITICAL",
  "confidence": 0-100,
  "ai_insights": "detailed analysis",
  "additional_patterns": ["pattern1", "pattern2"],
  "recommendations": ["action1", "action2"]
}}
"""

        response = client.chat.completions.create(
            model=Config.OPENAI_MODEL,
            messages=[
                {"role": "system", "content": "You are a fraud detection AI assistant. Respond only with valid JSON."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3,
            max_tokens=1000
        )

        ai_response = response.choices[0].message.content
        # Clean up markdown code blocks if present
        ai_response = ai_response.replace("```json", "").replace("```", "").strip()
        result = json.loads(ai_response)

        return result

    except Exception as exc:
        print(f"  ⚠️  AI analysis error: {exc}")
        return {
            "ai_insights": f"AI analysis failed: {str(exc)}",
            "additional_alerts": []
        }


def analyzer_agent(state: FraudState) -> FraudState:
    """
    Inspect transactions for known fraud patterns and populate the state.
    """
    print("\n" + "=" * 60)
    print("🔬 ANALYZER AGENT - Detecting Fraud Patterns")
    print("=" * 60)

    cc_txns = state["cc_transactions"]
    pp_txns = state["paypal_transactions"]
    print(f"\nAnalyzing {len(cc_txns)} CC + {len(pp_txns)} PayPal transactions...")

    customer_data = _build_customer_map(cc_txns, pp_txns)
    fraud_alerts: List[Dict] = []

    # FRAUD PATTERN 1: Foreign PayPal + Domestic CC (Account Takeover)
    print("\n→ Pattern 1: Foreign PayPal + Domestic CC...")
    for cust_id, data in customer_data.items():
        foreign_pp = [
            tx for tx in data["paypal"] if tx.get("account_country") not in ["US", None]
        ]
        domestic_cc = [
            tx
            for tx in data["cc"]
            if tx.get("location", {}).get("state") in ["CA", "NY", "TX", "FL", "IL", "PA"]
        ]

        if foreign_pp and domestic_cc:
            alert = {
                "customer_id": cust_id,
                "pattern": "FOREIGN_PAYPAL_DOMESTIC_CC",
                "risk_score": 8,
                "description": (
                    "Customer has foreign PayPal "
                    f"({foreign_pp[0].get('account_country')}) "
                    "but domestic CC transactions"
                ),
                "evidence": {
                    "paypal_country": foreign_pp[0].get("account_country"),
                    "cc_state": domestic_cc[0].get("location", {}).get("state"),
                    "pp_amount": foreign_pp[0].get("amount"),
                    "cc_amount": domestic_cc[0].get("amount"),
                },
                "recommendation": "FLAG_FOR_REVIEW",
            }
            fraud_alerts.append(alert)
            print(f"  🚨 Alert: {cust_id} - Foreign account activity")

    # FRAUD PATTERN 2: Category Mismatch (Merchant Fraud)
    print("\n→ Pattern 2: Category Mismatch...")
    all_txns = cc_txns + pp_txns
    mismatches = [
        ("gas", "clothing"),
        ("shell", "clothing"),
        ("exxon", "clothing"),
        ("starbucks", "gas"),
        ("coffee", "gas"),
        ("walmart", "gas"),
        ("target", "gas"),
    ]
    for tx in all_txns:
        merchant = tx.get("merchant", "").lower()
        category = tx.get("category", "").lower()

        for merchant_keyword, wrong_category in mismatches:
            if merchant_keyword in merchant and wrong_category in category:
                alert = {
                    "customer_id": tx.get("customer_id"),
                    "pattern": "CATEGORY_MISMATCH",
                    "risk_score": 6,
                    "description": (
                        f"Merchant '{tx.get('merchant')}' categorized as '{category}' (suspicious)"
                    ),
                    "evidence": {
                        "transaction_id": tx.get("transaction_id"),
                        "merchant": tx.get("merchant"),
                        "category": category,
                        "amount": tx.get("amount"),
                    },
                    "recommendation": "VERIFY_MERCHANT",
                }
                fraud_alerts.append(alert)
                print(f"  ⚠️  Alert: Category mismatch at {tx.get('merchant')}")

    # FRAUD PATTERN 3: High Amount Foreign Transactions
    print("\n→ Pattern 3: High Amount Foreign Transactions...")
    for tx in pp_txns:
        if tx.get("amount", 0) > 1000 and tx.get("account_country") not in ["US", None]:
            alert = {
                "customer_id": tx.get("customer_id"),
                "pattern": "HIGH_AMOUNT_FOREIGN",
                "risk_score": 7,
                "description": (
                    f"High amount (${tx.get('amount')}) from foreign account ({tx.get('account_country')})"
                ),
                "evidence": {
                    "transaction_id": tx.get("transaction_id"),
                    "amount": tx.get("amount"),
                    "country": tx.get("account_country"),
                    "merchant": tx.get("merchant"),
                },
                "recommendation": "REQUIRE_VERIFICATION",
            }
            fraud_alerts.append(alert)
            print(f"  🚨 Alert: High foreign transaction ${tx.get('amount')}")

    # FRAUD PATTERN 4: Multiple Failed Transactions
    print("\n→ Pattern 4: Multiple Failed Transactions...")
    for cust_id, data in customer_data.items():
        failed_txns = [
            tx for tx in data["cc"] + data["paypal"] if tx.get("status") in ["failed", "declined"]
        ]

        if len(failed_txns) >= 2:
            alert = {
                "customer_id": cust_id,
                "pattern": "MULTIPLE_FAILURES",
                "risk_score": 9,
                "description": f"{len(failed_txns)} failed transactions (possible card testing)",
                "evidence": {
                    "failed_count": len(failed_txns),
                    "transaction_ids": [tx.get("transaction_id") for tx in failed_txns],
                },
                "recommendation": "BLOCK_ACCOUNT",
            }
            fraud_alerts.append(alert)
            print(f"  🚨 Alert: {cust_id} - {len(failed_txns)} failed transactions")

    # FRAUD PATTERN 5: Same Customer, Same Amount, Different Platforms
    print("\n→ Pattern 5: Duplicate Amounts Across Platforms...")
    for cust_id, data in customer_data.items():
        if data["cc"] and data["paypal"]:
            for cc_tx in data["cc"]:
                for pp_tx in data["paypal"]:
                    if abs(cc_tx.get("amount", 0) - pp_tx.get("amount", 0)) < 1:
                        alert = {
                            "customer_id": cust_id,
                            "pattern": "DUPLICATE_AMOUNT",
                            "risk_score": 5,
                            "description": (
                                f"Similar amounts (${cc_tx.get('amount')}) on both CC and PayPal"
                            ),
                            "evidence": {
                                "cc_transaction": cc_tx.get("transaction_id"),
                                "pp_transaction": pp_tx.get("transaction_id"),
                                "amount": cc_tx.get("amount"),
                            },
                            "recommendation": "INVESTIGATE",
                        }
                        fraud_alerts.append(alert)
                        print(f"  ⚠️  Alert: {cust_id} - Duplicate amounts detected")

    state["fraud_alerts"] = fraud_alerts

    # Run AI-powered analysis
    print("\n→ Running AI-powered analysis with OpenAI...")
    ai_analysis = _ai_powered_analysis(cc_txns, pp_txns, fraud_alerts)

    if fraud_alerts:
        critical = [a for a in fraud_alerts if a["risk_score"] >= 8]
        high = [a for a in fraud_alerts if 6 <= a["risk_score"] < 8]
        medium = [a for a in fraud_alerts if a["risk_score"] < 6]

        summary = f"""
FRAUD DETECTION SUMMARY
========================
Total Alerts: {len(fraud_alerts)}
  - Critical (8-10): {len(critical)}
  - High (6-7): {len(high)}
  - Medium (1-5): {len(medium)}

Top Patterns Detected:
"""
        pattern_counts: Dict[str, int] = {}
        for alert in fraud_alerts:
            pattern = alert["pattern"]
            pattern_counts[pattern] = pattern_counts.get(pattern, 0) + 1

        for pattern, count in sorted(pattern_counts.items(), key=lambda item: item[1], reverse=True):
            summary += f"  - {pattern}: {count} cases\n"

        # Add AI insights
        if ai_analysis and "ai_insights" in ai_analysis:
            summary += f"\n🤖 AI-POWERED ANALYSIS\n"
            summary += f"========================\n"
            summary += f"Risk Level: {ai_analysis.get('risk_level', 'UNKNOWN')}\n"
            summary += f"Confidence: {ai_analysis.get('confidence', 'N/A')}%\n"
            summary += f"\nInsights:\n{ai_analysis.get('ai_insights', 'No insights available')}\n"

            if ai_analysis.get('additional_patterns'):
                summary += f"\nAdditional Patterns Detected:\n"
                for pattern in ai_analysis.get('additional_patterns', []):
                    summary += f"  - {pattern}\n"

            if ai_analysis.get('recommendations'):
                summary += f"\nRecommendations:\n"
                for rec in ai_analysis.get('recommendations', []):
                    summary += f"  - {rec}\n"
    else:
        summary = "✅ No fraud patterns detected. All transactions appear normal."

        # Even with no alerts, get AI opinion
        if ai_analysis and "ai_insights" in ai_analysis:
            summary += f"\n\n🤖 AI Analysis: {ai_analysis.get('ai_insights', '')}"

    state["summary"] = summary

    print(f"\n✓ Analysis complete: {len(fraud_alerts)} rule-based alerts generated")
    if ai_analysis:
        print(f"✓ AI analysis complete: Risk level {ai_analysis.get('risk_level', 'UNKNOWN')}")
    return state
