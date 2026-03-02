#!/usr/bin/env python3
"""
LLM Narrative Agent for Enhanced Fraud Detection Explanations
This agent uses OpenAI to generate natural language explanations for fraud alerts
"""

import os
import json
import logging
from datetime import datetime
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
import openai

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class NarrativeAlert:
    transaction_id: str
    customer_id: str
    risk_score: float
    narrative: str
    confidence: float
    recommendation: str
    key_indicators: List[str]
    timestamp: datetime

class LLMNarrativeAgent:
    """
    AI Agent for generating natural language fraud detection narratives
    """
    
    def __init__(self, openai_api_key: Optional[str] = None):
        """
        Initialize the LLM Narrative Agent
        
        Args:
            openai_api_key: OpenAI API key. If None, will try to get from environment
        """
        self.api_key = openai_api_key or os.getenv('OPENAI_API_KEY')
        
        if not self.api_key:
            logger.warning("No OpenAI API key provided. LLM features will be disabled.")
            self.enabled = False
        else:
            openai.api_key = self.api_key
            self.enabled = True
            logger.info("LLM Narrative Agent initialized with OpenAI")
    
    def generate_fraud_narrative(self, transaction: Dict[str, Any], 
                               risk_score: float, 
                               risk_factors: List[str]) -> NarrativeAlert:
        """
        Generate a natural language narrative for a fraud alert
        
        Args:
            transaction: Transaction data
            risk_score: Calculated risk score (0.0-1.0)
            risk_score: List of risk factors identified
            
        Returns:
            NarrativeAlert with enhanced explanation
        """
        if not self.enabled:
            return self._generate_fallback_narrative(transaction, risk_score, risk_factors)
        
        try:
            # Prepare context for LLM
            context = self._prepare_llm_context(transaction, risk_score, risk_factors)
            
            # Generate narrative using OpenAI
            narrative = self._call_openai_api(context)
            
            # Extract structured information
            structured_info = self._parse_llm_response(narrative)
            
            return NarrativeAlert(
                transaction_id=transaction.get('transaction_id', 'unknown'),
                customer_id=transaction.get('customer_id', 'unknown'),
                risk_score=risk_score,
                narrative=structured_info['narrative'],
                confidence=structured_info['confidence'],
                recommendation=structured_info['recommendation'],
                key_indicators=structured_info['key_indicators'],
                timestamp=datetime.now()
            )
            
        except Exception as e:
            logger.error(f"Error generating LLM narrative: {e}")
            return self._generate_fallback_narrative(transaction, risk_score, risk_factors)
    
    def _prepare_llm_context(self, transaction: Dict[str, Any], 
                           risk_score: float, 
                           risk_factors: List[str]) -> str:
        """
        Prepare context for LLM analysis
        """
        # Extract key transaction details
        amount = transaction.get('amount', 0)
        merchant = transaction.get('merchant', 'Unknown')
        category = transaction.get('category', 'Unknown')
        location = transaction.get('location', {})
        timestamp = transaction.get('timestamp', '')
        
        # Format location
        location_str = f"{location.get('city', 'Unknown')}, {location.get('state', 'Unknown')}, {location.get('country', 'Unknown')}"
        
        # Get time context
        try:
            dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
            time_context = f"{dt.strftime('%H:%M')} on {dt.strftime('%A, %B %d')}"
        except:
            time_context = "unknown time"
        
        # PayPal specific context
        paypal_context = ""
        if 'paypal-transactions' in str(transaction.get('transaction_id', '')):
            fraud_indicators = transaction.get('fraud_indicators', {})
            if fraud_indicators:
                paypal_context = f"""
PayPal Account Details:
- Foreign Account: {fraud_indicators.get('is_foreign_account', False)}
- High Amount: {fraud_indicators.get('is_high_amount', False)}
- Account Age: {fraud_indicators.get('account_age_days', 'Unknown')} days
- Marked as Fraud: {transaction.get('is_fraud', False)}
"""
        
        context = f"""
Transaction Analysis Request:

Transaction Details:
- ID: {transaction.get('transaction_id', 'Unknown')}
- Customer: {transaction.get('customer_id', 'Unknown')}
- Amount: ${amount:,.2f}
- Merchant: {merchant}
- Category: {category}
- Location: {location_str}
- Time: {time_context}
- Risk Score: {risk_score:.2f}
- Risk Factors: {', '.join(risk_factors)}

{paypal_context}

Provide a brief fraud analysis (under 50 words) that explains the risk and key indicators.

Format as JSON:
{{
    "narrative": "Brief risk explanation...",
    "confidence": 0.85,
    "recommendation": "BLOCK_TRANSACTION",
    "key_indicators": ["indicator1", "indicator2"]
}}
"""
        return context
    
    def _call_openai_api(self, context: str) -> str:
        """
        Call OpenAI API to generate narrative
        """
        try:
            # Use the new OpenAI client format
            client = openai.OpenAI(api_key=self.api_key)
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {
                        "role": "system",
                        "content": "You are a fraud detection expert. Analyze transaction data and provide clear, actionable fraud assessments. Always respond with valid JSON format."
                    },
                    {
                        "role": "user",
                        "content": context
                    }
                ],
                max_tokens=300,
                temperature=0.3
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            logger.error(f"OpenAI API error: {e}")
            raise
    
    def _parse_llm_response(self, response: str) -> Dict[str, Any]:
        """
        Parse LLM response and extract structured information
        """
        try:
            # Try to parse as JSON
            data = json.loads(response)
            
            return {
                'narrative': data.get('narrative', 'Analysis unavailable'),
                'confidence': float(data.get('confidence', 0.5)),
                'recommendation': data.get('recommendation', 'REVIEW_REQUIRED'),
                'key_indicators': data.get('key_indicators', [])
            }
            
        except json.JSONDecodeError:
            # Fallback if JSON parsing fails
            logger.warning("Failed to parse LLM response as JSON, using fallback")
            return {
                'narrative': response[:200] + "..." if len(response) > 200 else response,
                'confidence': 0.7,
                'recommendation': 'REVIEW_REQUIRED',
                'key_indicators': ['LLM analysis provided']
            }
    
    def _generate_fallback_narrative(self, transaction: Dict[str, Any], 
                                   risk_score: float, 
                                   risk_factors: List[str]) -> NarrativeAlert:
        """
        Generate fallback narrative when LLM is not available
        """
        amount = transaction.get('amount', 0)
        merchant = transaction.get('merchant', 'Unknown')
        
        # Generate basic narrative
        if risk_score >= 0.8:
            narrative = f"🚨 CRITICAL FRAUD ALERT: ${amount:,.2f} transaction to {merchant} shows multiple fraud indicators. Risk score: {risk_score:.2f}"
            recommendation = "BLOCK_TRANSACTION"
        elif risk_score >= 0.5:
            narrative = f"⚠️ HIGH-RISK TRANSACTION: ${amount:,.2f} transaction to {merchant} requires immediate review. Risk score: {risk_score:.2f}"
            recommendation = "REQUIRE_VERIFICATION"
        else:
            narrative = f"📊 MODERATE RISK: ${amount:,.2f} transaction to {merchant} shows some risk indicators. Risk score: {risk_score:.2f}"
            recommendation = "MONITOR_CLOSELY"
        
        return NarrativeAlert(
            transaction_id=transaction.get('transaction_id', 'unknown'),
            customer_id=transaction.get('customer_id', 'unknown'),
            risk_score=risk_score,
            narrative=narrative,
            confidence=0.6,
            recommendation=recommendation,
            key_indicators=risk_factors,
            timestamp=datetime.now()
        )
    
    def generate_customer_summary(self, customer_id: str, 
                                transaction_history: List[Dict[str, Any]]) -> str:
        """
        Generate a customer behavior summary using LLM
        """
        if not self.enabled or not transaction_history:
            return f"Customer {customer_id}: No LLM analysis available"
        
        try:
            # Prepare customer context
            total_spent = sum(tx.get('amount', 0) for tx in transaction_history)
            avg_transaction = total_spent / len(transaction_history) if transaction_history else 0
            merchants = list(set(tx.get('merchant', 'Unknown') for tx in transaction_history))
            categories = list(set(tx.get('category', 'Unknown') for tx in transaction_history))
            
            context = f"""
Customer Behavior Analysis:

Customer ID: {customer_id}
Transaction Count: {len(transaction_history)}
Total Spent: ${total_spent:,.2f}
Average Transaction: ${avg_transaction:,.2f}
Unique Merchants: {len(merchants)}
Categories: {', '.join(categories[:5])}

Recent Transactions:
{json.dumps(transaction_history[-3:], indent=2)}

Provide a brief customer behavior summary (under 100 words) highlighting:
1. Spending patterns
2. Risk indicators
3. Behavioral consistency
"""
            
            client = openai.OpenAI(api_key=self.api_key)
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {
                        "role": "system",
                        "content": "You are a fraud analyst. Provide concise customer behavior summaries."
                    },
                    {
                        "role": "user",
                        "content": context
                    }
                ],
                max_tokens=150,
                temperature=0.3
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            logger.error(f"Error generating customer summary: {e}")
            return f"Customer {customer_id}: Analysis failed"

def main():
    """
    Test the LLM Narrative Agent
    """
    # Initialize agent
    agent = LLMNarrativeAgent()
    
    # Sample transaction
    sample_transaction = {
        'transaction_id': 'pp_tx_12345',
        'customer_id': 'cust_67890',
        'amount': 1500.0,
        'merchant': 'Suspicious Merchant',
        'category': 'Electronics',
        'timestamp': '2024-01-15T02:30:00Z',
        'location': {
            'city': 'New York',
            'state': 'NY',
            'country': 'USA'
        },
        'is_fraud': True,
        'fraud_indicators': {
            'is_foreign_account': True,
            'is_high_amount': True,
            'account_age_days': 5
        }
    }
    
    risk_factors = ['Foreign account', 'High amount', 'New account', 'Night time']
    
    # Generate narrative
    logger.info("Generating LLM narrative...")
    narrative_alert = agent.generate_fraud_narrative(
        sample_transaction, 0.85, risk_factors
    )
    
    logger.info(f"Narrative Alert:")
    logger.info(f"Transaction: {narrative_alert.transaction_id}")
    logger.info(f"Risk Score: {narrative_alert.risk_score}")
    logger.info(f"Narrative: {narrative_alert.narrative}")
    logger.info(f"Confidence: {narrative_alert.confidence}")
    logger.info(f"Recommendation: {narrative_alert.recommendation}")
    logger.info(f"Key Indicators: {narrative_alert.key_indicators}")

if __name__ == "__main__":
    main()
