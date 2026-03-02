#!/usr/bin/env python3
"""
Data Analysis Agent for Fraud Detection System
Specialized AI agent for analyzing customer behavior and merchant patterns
"""

import asyncio
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import statistics

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class DataAnalysisAgent:
    """
    AI Agent specialized in data analysis for fraud detection
    """
    
    def __init__(self):
        self.agent_name = "DataAnalysisAgent"
        self.customer_profiles = {}
        self.merchant_profiles = {}
        self.transaction_history = []
        self.start_time = datetime.now()
        
        logger.info(f"🤖 {self.agent_name} initialized")
        logger.info("📊 Specialized in customer behavior and merchant pattern analysis")
    
    async def analyze_transaction(self, transaction: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze transaction data for fraud indicators
        """
        try:
            # Update transaction history
            self.transaction_history.append(transaction)
            
            # Run multiple analysis methods
            customer_analysis = await self._analyze_customer_behavior(transaction)
            merchant_analysis = await self._analyze_merchant_patterns(transaction)
            geographic_analysis = await self._analyze_geographic_patterns(transaction)
            temporal_analysis = await self._analyze_temporal_patterns(transaction)
            
            # Combine analysis results
            analysis_results = {
                'customer_risk_score': customer_analysis,
                'merchant_risk_score': merchant_analysis,
                'geographic_risk_score': geographic_analysis,
                'temporal_risk_score': temporal_analysis
            }
            
            # Calculate overall risk score
            overall_risk_score = self._calculate_overall_risk_score(analysis_results)
            
            # Generate analysis report
            analysis_report = {
                'overall_risk_score': overall_risk_score,
                'risk_scores': analysis_results,
                'risk_indicators': self._get_risk_indicators(analysis_results),
                'confidence': self._calculate_confidence(analysis_results),
                'recommendation': self._get_risk_recommendation(overall_risk_score)
            }
            
            return analysis_report
            
        except Exception as e:
            logger.error(f"Error analyzing transaction: {e}")
            return {'error': str(e)}
    
    async def _analyze_customer_behavior(self, transaction: Dict[str, Any]) -> float:
        """
        Analyze customer behavior patterns
        """
        try:
            customer_id = transaction.get('customer_id', '')
            amount = transaction.get('amount', 0)
            merchant = transaction.get('merchant', '')
            category = transaction.get('category', '')
            
            # Update customer profile
            if customer_id not in self.customer_profiles:
                self.customer_profiles[customer_id] = {
                    'transaction_count': 0,
                    'total_amount': 0,
                    'merchants': set(),
                    'categories': set(),
                    'avg_amount': 0,
                    'max_amount': 0,
                    'last_transaction_time': None,
                    'transaction_frequency': 0
                }
            
            profile = self.customer_profiles[customer_id]
            profile['transaction_count'] += 1
            profile['total_amount'] += amount
            profile['merchants'].add(merchant)
            profile['categories'].add(category)
            profile['avg_amount'] = profile['total_amount'] / profile['transaction_count']
            profile['max_amount'] = max(profile['max_amount'], amount)
            
            # Calculate customer risk score
            risk_score = 0.0
            
            # Amount-based risk
            if profile['transaction_count'] > 1:
                if amount > profile['avg_amount'] * 5:
                    risk_score += 0.4
                elif amount > profile['max_amount']:
                    risk_score += 0.3
            
            # Merchant diversity risk
            if merchant not in profile['merchants']:
                risk_score += 0.2
            
            # Category diversity risk
            if category not in profile['categories']:
                risk_score += 0.1
            
            # Frequency risk
            current_time = datetime.now()
            if profile['last_transaction_time']:
                time_diff = (current_time - profile['last_transaction_time']).seconds
                if time_diff < 300:  # Less than 5 minutes
                    risk_score += 0.3
            
            profile['last_transaction_time'] = current_time
            
            return min(1.0, risk_score)
            
        except Exception as e:
            logger.error(f"Customer behavior analysis error: {e}")
            return 0.0
    
    async def _analyze_merchant_patterns(self, transaction: Dict[str, Any]) -> float:
        """
        Analyze merchant patterns and risk
        """
        try:
            merchant = transaction.get('merchant', '')
            amount = transaction.get('amount', 0)
            category = transaction.get('category', '')
            
            # Update merchant profile
            if merchant not in self.merchant_profiles:
                self.merchant_profiles[merchant] = {
                    'transaction_count': 0,
                    'total_amount': 0,
                    'categories': set(),
                    'avg_amount': 0,
                    'max_amount': 0,
                    'risk_level': 'LOW'
                }
            
            profile = self.merchant_profiles[merchant]
            profile['transaction_count'] += 1
            profile['total_amount'] += amount
            profile['categories'].add(category)
            profile['avg_amount'] = profile['total_amount'] / profile['transaction_count']
            profile['max_amount'] = max(profile['max_amount'], amount)
            
            # Calculate merchant risk score
            risk_score = 0.0
            
            # High-risk categories
            high_risk_categories = ['Gambling', 'Adult Entertainment', 'Cash Advance']
            if category in high_risk_categories:
                risk_score += 0.4
                profile['risk_level'] = 'HIGH'
            
            # Amount-based risk
            if amount > profile['avg_amount'] * 3:
                risk_score += 0.3
            
            # New merchant risk
            if profile['transaction_count'] == 1:
                risk_score += 0.2
            
            # Category mismatch risk
            if category not in profile['categories'] and profile['transaction_count'] > 1:
                risk_score += 0.1
            
            return min(1.0, risk_score)
            
        except Exception as e:
            logger.error(f"Merchant pattern analysis error: {e}")
            return 0.0
    
    async def _analyze_geographic_patterns(self, transaction: Dict[str, Any]) -> float:
        """
        Analyze geographic patterns and risk
        """
        try:
            location = transaction.get('location', {})
            country = location.get('country', '')
            state = location.get('state', '')
            city = location.get('city', '')
            
            risk_score = 0.0
            
            # International transaction risk
            if country and country != 'USA':
                risk_score += 0.3
            
            # High-risk locations
            high_risk_states = ['NV', 'FL', 'CA']  # Nevada, Florida, California
            if state in high_risk_states:
                risk_score += 0.2
            
            # High-risk cities
            high_risk_cities = ['Las Vegas', 'Miami', 'Los Angeles']
            if city in high_risk_cities:
                risk_score += 0.1
            
            return min(1.0, risk_score)
            
        except Exception as e:
            logger.error(f"Geographic pattern analysis error: {e}")
            return 0.0
    
    async def _analyze_temporal_patterns(self, transaction: Dict[str, Any]) -> float:
        """
        Analyze temporal patterns and risk
        """
        try:
            current_time = datetime.now()
            hour = current_time.hour
            day_of_week = current_time.weekday()
            
            risk_score = 0.0
            
            # Late night/early morning risk
            if hour in [0, 1, 2, 3, 4, 5]:
                risk_score += 0.3
            
            # Weekend risk
            if day_of_week in [5, 6]:  # Saturday, Sunday
                risk_score += 0.1
            
            # Business hours risk (lower risk during business hours)
            if 9 <= hour <= 17:
                risk_score -= 0.1
            
            # High-frequency transaction risk
            recent_transactions = [t for t in self.transaction_history[-10:] 
                                 if (current_time - datetime.fromisoformat(t.get('timestamp', current_time.isoformat()))).seconds < 3600]
            
            if len(recent_transactions) > 5:
                risk_score += 0.4
            
            return max(0.0, min(1.0, risk_score))
            
        except Exception as e:
            logger.error(f"Temporal pattern analysis error: {e}")
            return 0.0
    
    def _calculate_overall_risk_score(self, risk_scores: Dict[str, float]) -> float:
        """
        Calculate overall risk score from individual scores
        """
        try:
            scores = list(risk_scores.values())
            if not scores:
                return 0.0
            
            # Weighted average of risk scores
            weights = [0.3, 0.3, 0.2, 0.2]  # Customer, Merchant, Geographic, Temporal
            weighted_score = sum(score * weight for score, weight in zip(scores, weights))
            
            return min(1.0, weighted_score)
            
        except Exception as e:
            logger.error(f"Error calculating overall risk score: {e}")
            return 0.0
    
    def _get_risk_indicators(self, risk_scores: Dict[str, float]) -> List[str]:
        """
        Get list of risk indicators
        """
        indicators = []
        
        for score_type, score in risk_scores.items():
            if score > 0.7:
                indicators.append(f"High {score_type.replace('_', ' ')}")
            elif score > 0.4:
                indicators.append(f"Moderate {score_type.replace('_', ' ')}")
        
        return indicators
    
    def _calculate_confidence(self, risk_scores: Dict[str, float]) -> float:
        """
        Calculate confidence in risk assessment
        """
        try:
            # Confidence based on number of indicators and transaction history
            num_indicators = sum(1 for score in risk_scores.values() if score > 0.3)
            history_size = len(self.transaction_history)
            
            confidence = min(1.0, (num_indicators * 0.2) + (min(history_size, 100) * 0.001))
            return confidence
            
        except Exception as e:
            logger.error(f"Error calculating confidence: {e}")
            return 0.5
    
    def _get_risk_recommendation(self, overall_score: float) -> str:
        """
        Get recommendation based on risk score
        """
        if overall_score >= 0.8:
            return "BLOCK_TRANSACTION"
        elif overall_score >= 0.6:
            return "REQUIRE_VERIFICATION"
        elif overall_score >= 0.3:
            return "MONITOR_CLOSELY"
        else:
            return "PROCESS_NORMALLY"
    
    def get_agent_status(self) -> Dict[str, Any]:
        """
        Get agent status and statistics
        """
        return {
            'agent_name': self.agent_name,
            'uptime': datetime.now() - self.start_time,
            'transactions_processed': len(self.transaction_history),
            'customers_profiled': len(self.customer_profiles),
            'merchants_profiled': len(self.merchant_profiles)
        }

async def main():
    """
    Main function to test data analysis agent
    """
    agent = DataAnalysisAgent()
    
    # Test transaction
    test_transaction = {
        'transaction_id': 'TEST-123456',
        'customer_id': 'CUST-001',
        'amount': 1000.0,
        'merchant': 'Test Merchant',
        'category': 'Electronics',
        'timestamp': datetime.now().isoformat(),
        'location': {'country': 'USA', 'state': 'CA', 'city': 'Los Angeles'}
    }
    
    # Analyze transaction
    result = await agent.analyze_transaction(test_transaction)
    logger.info(f"Data analysis result: {result}")

if __name__ == "__main__":
    asyncio.run(main())
