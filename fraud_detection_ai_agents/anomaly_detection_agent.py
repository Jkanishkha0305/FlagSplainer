#!/usr/bin/env python3
"""
Anomaly Detection Agent for Fraud Detection System
Specialized AI agent for detecting anomalies in transaction data
"""

import asyncio
import json
import logging
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import statistics

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class AnomalyDetectionAgent:
    """
    AI Agent specialized in detecting anomalies in transaction data
    """
    
    def __init__(self):
        self.agent_name = "AnomalyDetectionAgent"
        self.transaction_history = []
        self.customer_profiles = {}
        self.merchant_profiles = {}
        self.start_time = datetime.now()
        
        logger.info(f"🤖 {self.agent_name} initialized")
        logger.info("📊 Specialized in statistical and behavioral anomaly detection")
    
    async def detect_anomalies(self, transaction: Dict[str, Any]) -> Dict[str, Any]:
        """
        Detect anomalies in transaction data
        """
        try:
            # Update transaction history
            self.transaction_history.append(transaction)
            
            # Run multiple anomaly detection methods
            statistical_anomaly = await self._detect_statistical_anomaly(transaction)
            behavioral_anomaly = await self._detect_behavioral_anomaly(transaction)
            pattern_anomaly = await self._detect_pattern_anomaly(transaction)
            
            # Combine anomaly scores
            anomaly_scores = {
                'statistical_anomaly_score': statistical_anomaly,
                'behavioral_anomaly_score': behavioral_anomaly,
                'pattern_anomaly_score': pattern_anomaly
            }
            
            # Calculate overall anomaly score
            overall_anomaly_score = self._calculate_overall_anomaly_score(anomaly_scores)
            
            # Generate anomaly report
            anomaly_report = {
                'overall_anomaly_score': overall_anomaly_score,
                'anomaly_scores': anomaly_scores,
                'anomaly_indicators': self._get_anomaly_indicators(anomaly_scores),
                'confidence': self._calculate_confidence(anomaly_scores),
                'recommendation': self._get_anomaly_recommendation(overall_anomaly_score)
            }
            
            return anomaly_report
            
        except Exception as e:
            logger.error(f"Error detecting anomalies: {e}")
            return {'error': str(e)}
    
    async def _detect_statistical_anomaly(self, transaction: Dict[str, Any]) -> float:
        """
        Detect statistical anomalies using Z-score analysis
        """
        try:
            amount = transaction.get('amount', 0)
            
            # Get recent transaction amounts for comparison
            recent_amounts = [t.get('amount', 0) for t in self.transaction_history[-100:]]
            
            if len(recent_amounts) < 10:
                return 0.0  # Not enough data for statistical analysis
            
            # Calculate Z-score
            mean_amount = statistics.mean(recent_amounts)
            std_amount = statistics.stdev(recent_amounts) if len(recent_amounts) > 1 else 0
            
            if std_amount == 0:
                return 0.0
            
            z_score = abs((amount - mean_amount) / std_amount)
            
            # Convert Z-score to anomaly score (0-1)
            anomaly_score = min(1.0, z_score / 3.0)  # Z-score > 3 is highly anomalous
            
            return anomaly_score
            
        except Exception as e:
            logger.error(f"Statistical anomaly detection error: {e}")
            return 0.0
    
    async def _detect_behavioral_anomaly(self, transaction: Dict[str, Any]) -> float:
        """
        Detect behavioral anomalies based on customer patterns
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
                    'max_amount': 0
                }
            
            profile = self.customer_profiles[customer_id]
            profile['transaction_count'] += 1
            profile['total_amount'] += amount
            profile['merchants'].add(merchant)
            profile['categories'].add(category)
            profile['avg_amount'] = profile['total_amount'] / profile['transaction_count']
            profile['max_amount'] = max(profile['max_amount'], amount)
            
            # Calculate behavioral anomaly score
            anomaly_score = 0.0
            
            # Amount anomaly
            if profile['transaction_count'] > 1:
                if amount > profile['avg_amount'] * 3:
                    anomaly_score += 0.4
                elif amount > profile['max_amount']:
                    anomaly_score += 0.3
            
            # Merchant anomaly
            if merchant not in profile['merchants']:
                anomaly_score += 0.2
            
            # Category anomaly
            if category not in profile['categories']:
                anomaly_score += 0.1
            
            return min(1.0, anomaly_score)
            
        except Exception as e:
            logger.error(f"Behavioral anomaly detection error: {e}")
            return 0.0
    
    async def _detect_pattern_anomaly(self, transaction: Dict[str, Any]) -> float:
        """
        Detect pattern anomalies in transaction sequences
        """
        try:
            # Time-based pattern analysis
            current_time = datetime.now()
            hour = current_time.hour
            
            # Check for unusual transaction times
            time_anomaly = 0.0
            if hour in [0, 1, 2, 3, 4, 5]:  # Late night/early morning
                time_anomaly += 0.3
            
            # Frequency pattern analysis
            recent_transactions = [t for t in self.transaction_history[-10:] 
                                 if (current_time - datetime.fromisoformat(t.get('timestamp', current_time.isoformat()))).seconds < 3600]
            
            frequency_anomaly = 0.0
            if len(recent_transactions) > 5:  # High frequency
                frequency_anomaly += 0.4
            
            # Geographic pattern analysis
            location = transaction.get('location', {})
            country = location.get('country', '')
            
            geographic_anomaly = 0.0
            if country and country != 'USA':
                geographic_anomaly += 0.2
            
            # Combine pattern anomalies
            pattern_anomaly_score = min(1.0, time_anomaly + frequency_anomaly + geographic_anomaly)
            
            return pattern_anomaly_score
            
        except Exception as e:
            logger.error(f"Pattern anomaly detection error: {e}")
            return 0.0
    
    def _calculate_overall_anomaly_score(self, anomaly_scores: Dict[str, float]) -> float:
        """
        Calculate overall anomaly score from individual scores
        """
        try:
            scores = list(anomaly_scores.values())
            if not scores:
                return 0.0
            
            # Weighted average of anomaly scores
            weights = [0.4, 0.4, 0.2]  # Statistical, Behavioral, Pattern
            weighted_score = sum(score * weight for score, weight in zip(scores, weights))
            
            return min(1.0, weighted_score)
            
        except Exception as e:
            logger.error(f"Error calculating overall anomaly score: {e}")
            return 0.0
    
    def _get_anomaly_indicators(self, anomaly_scores: Dict[str, float]) -> List[str]:
        """
        Get list of anomaly indicators
        """
        indicators = []
        
        for score_type, score in anomaly_scores.items():
            if score > 0.7:
                indicators.append(f"High {score_type.replace('_', ' ')}")
            elif score > 0.4:
                indicators.append(f"Moderate {score_type.replace('_', ' ')}")
        
        return indicators
    
    def _calculate_confidence(self, anomaly_scores: Dict[str, float]) -> float:
        """
        Calculate confidence in anomaly detection
        """
        try:
            # Confidence based on number of indicators and transaction history
            num_indicators = sum(1 for score in anomaly_scores.values() if score > 0.3)
            history_size = len(self.transaction_history)
            
            confidence = min(1.0, (num_indicators * 0.2) + (min(history_size, 100) * 0.001))
            return confidence
            
        except Exception as e:
            logger.error(f"Error calculating confidence: {e}")
            return 0.5
    
    def _get_anomaly_recommendation(self, overall_score: float) -> str:
        """
        Get recommendation based on anomaly score
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
    Main function to test anomaly detection agent
    """
    agent = AnomalyDetectionAgent()
    
    # Test transaction
    test_transaction = {
        'transaction_id': 'TEST-123456',
        'customer_id': 'CUST-001',
        'amount': 1000.0,
        'merchant': 'Test Merchant',
        'category': 'Electronics',
        'timestamp': datetime.now().isoformat(),
        'location': {'country': 'USA'}
    }
    
    # Detect anomalies
    result = await agent.detect_anomalies(test_transaction)
    logger.info(f"Anomaly detection result: {result}")

if __name__ == "__main__":
    asyncio.run(main())
