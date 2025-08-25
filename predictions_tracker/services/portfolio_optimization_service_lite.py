#!/usr/bin/env python3
"""
🚀 PORTFOLIO OPTIMIZATION SERVICE - LIGHTWEIGHT VERSION
Modern Portfolio Theory without heavy ML dependencies
"""

import numpy as np
import logging
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from datetime import date, datetime
from enum import Enum
import warnings
warnings.filterwarnings('ignore')

logger = logging.getLogger(__name__)

@dataclass(frozen=True)
class MethodPerformance:
    """Immutable data contract for method performance metrics"""
    method_name: str
    expected_return: float
    volatility: float
    hit_rate: float
    sharpe_ratio: float
    max_drawdown: float
    confidence_score: float

@dataclass(frozen=True)
class OptimizationResult:
    """Immutable data contract for optimization result"""
    optimal_weights: Dict[str, float]
    expected_return: float
    portfolio_volatility: float
    sharpe_ratio: float
    kelly_fractions: Dict[str, float]
    optimization_status: str
    additional_metrics: Dict[str, Any]

class MarketRegimeEnum(Enum):
    """Market regime enumeration"""
    BULL = "bull"
    BEAR = "bear"
    VOLATILE = "volatile"
    SIDEWAYS = "sideways"

class PortfolioOptimizationService:
    """
    🚀 LIGHTWEIGHT: Portfolio Optimization Service
    Modern Portfolio Theory without heavy ML dependencies
    """
    
    def __init__(self):
        self.risk_free_rate = 0.02  # 2% risk-free rate
        self.logger = logger
        
    def calculate_correlation_matrix_v3(self, performances: List[MethodPerformance]) -> Dict[str, Any]:
        """
        Calculate correlation matrix between methods
        
        Args:
            performances: List of method performance data
            
        Returns:
            Dict containing correlation matrix and metrics
        """
        try:
            if len(performances) < 2:
                return {
                    'correlation_matrix': {},
                    'diversification_score': 1.0,
                    'average_correlation': 0.0
                }
            
            # Simple correlation calculation based on performance metrics
            correlation_matrix = {}
            
            for i, perf1 in enumerate(performances):
                correlation_matrix[perf1.method_name] = {}
                
                for j, perf2 in enumerate(performances):
                    if i == j:
                        correlation_matrix[perf1.method_name][perf2.method_name] = 1.0
                    else:
                        # Simple correlation based on performance similarity
                        return_diff = abs(perf1.expected_return - perf2.expected_return)
                        vol_diff = abs(perf1.volatility - perf2.volatility)
                        hit_diff = abs(perf1.hit_rate - perf2.hit_rate)
                        
                        # Inverse correlation based on differences
                        correlation = max(0.0, 1.0 - (return_diff + vol_diff + hit_diff) / 3.0)
                        correlation_matrix[perf1.method_name][perf2.method_name] = correlation
            
            # Calculate diversification score
            correlations = []
            for method1 in correlation_matrix:
                for method2 in correlation_matrix[method1]:
                    if method1 != method2:
                        correlations.append(correlation_matrix[method1][method2])
            
            avg_correlation = np.mean(correlations) if correlations else 0.0
            diversification_score = max(0.0, 1.0 - avg_correlation)
            
            self.logger.info(f"✅ Correlation matrix calculated: {len(performances)} methods")
            
            return {
                'correlation_matrix': correlation_matrix,
                'diversification_score': diversification_score,
                'average_correlation': avg_correlation
            }
            
        except Exception as e:
            self.logger.error(f"❌ Error calculating correlation matrix: {e}")
            return {
                'correlation_matrix': {},
                'diversification_score': 0.5,
                'average_correlation': 0.5
            }
    
    def markowitz_optimization_v3(self, performances: List[MethodPerformance], 
                                 correlation_matrix: Dict[str, Dict[str, float]]) -> OptimizationResult:
        """
        Simple Markowitz-style optimization
        
        Args:
            performances: Method performance data
            correlation_matrix: Correlation matrix
            
        Returns:
            OptimizationResult: Optimization results
        """
        try:
            if not performances:
                raise ValueError("No performance data provided")
            
            # Simple optimization: weight by Sharpe ratio with diversification bonus
            total_sharpe = sum(max(0.1, perf.sharpe_ratio) for perf in performances)
            
            optimal_weights = {}
            for perf in performances:
                base_weight = max(0.1, perf.sharpe_ratio) / total_sharpe
                
                # Diversification bonus for low correlation
                diversification_bonus = 0.0
                if correlation_matrix and perf.method_name in correlation_matrix:
                    avg_corr = np.mean([
                        correlation_matrix[perf.method_name][other_method]
                        for other_method in correlation_matrix[perf.method_name]
                        if other_method != perf.method_name
                    ])
                    diversification_bonus = (1.0 - avg_corr) * 0.1
                
                optimal_weights[perf.method_name] = base_weight + diversification_bonus
            
            # Normalize weights
            total_weight = sum(optimal_weights.values())
            if total_weight > 0:
                for method in optimal_weights:
                    optimal_weights[method] /= total_weight
            
            # Calculate portfolio metrics
            expected_return = sum(
                optimal_weights[perf.method_name] * perf.expected_return
                for perf in performances
            )
            
            portfolio_volatility = np.sqrt(sum(
                (optimal_weights[perf.method_name] * perf.volatility) ** 2
                for perf in performances
            ))
            
            sharpe_ratio = (expected_return - self.risk_free_rate) / max(0.001, portfolio_volatility)
            
            # Kelly fractions (simplified)
            kelly_fractions = {}
            for perf in performances:
                if perf.volatility > 0:
                    kelly_fraction = (perf.expected_return - self.risk_free_rate) / (perf.volatility ** 2)
                    kelly_fractions[perf.method_name] = max(0.0, min(0.5, kelly_fraction))
                else:
                    kelly_fractions[perf.method_name] = 0.0
            
            self.logger.info(f"✅ Portfolio optimization completed: Sharpe={sharpe_ratio:.3f}")
            
            return OptimizationResult(
                optimal_weights=optimal_weights,
                expected_return=expected_return,
                portfolio_volatility=portfolio_volatility,
                sharpe_ratio=sharpe_ratio,
                kelly_fractions=kelly_fractions,
                optimization_status="success",
                additional_metrics={
                    'num_methods': len(performances),
                    'diversification_score': 1.0 - portfolio_volatility / max(0.001, expected_return)
                }
            )
            
        except Exception as e:
            self.logger.error(f"❌ Portfolio optimization failed: {e}")
            
            # Fallback: equal weights
            equal_weight = 1.0 / len(performances) if performances else 0.0
            fallback_weights = {perf.method_name: equal_weight for perf in performances}
            
            return OptimizationResult(
                optimal_weights=fallback_weights,
                expected_return=0.5,
                portfolio_volatility=0.2,
                sharpe_ratio=1.0,
                kelly_fractions={perf.method_name: 0.1 for perf in performances},
                optimization_status="fallback",
                additional_metrics={}
            )
    
    def calculate_kelly_criterion_v3(self, performance: MethodPerformance) -> Dict[str, Any]:
        """
        Calculate Kelly Criterion for method
        
        Args:
            performance: Method performance data
            
        Returns:
            Dict: Kelly criterion results
        """
        try:
            if performance.volatility <= 0:
                return {
                    'kelly_fraction': 0.0,
                    'recommended_weight': 0.0,
                    'risk_assessment': 'high_risk'
                }
            
            # Kelly fraction calculation
            excess_return = performance.expected_return - self.risk_free_rate
            kelly_fraction = excess_return / (performance.volatility ** 2)
            
            # Cap at 50% for safety
            kelly_fraction = max(0.0, min(0.5, kelly_fraction))
            
            # Recommended weight (conservative Kelly)
            recommended_weight = kelly_fraction * 0.5  # Half Kelly for safety
            
            # Risk assessment
            if performance.max_drawdown > 0.2:
                risk_assessment = 'high_risk'
            elif performance.volatility > 0.3:
                risk_assessment = 'medium_risk'
            else:
                risk_assessment = 'low_risk'
            
            return {
                'kelly_fraction': kelly_fraction,
                'recommended_weight': recommended_weight,
                'risk_assessment': risk_assessment,
                'excess_return': excess_return,
                'risk_adjusted_return': excess_return / max(0.001, performance.volatility)
            }
            
        except Exception as e:
            self.logger.error(f"❌ Kelly criterion calculation failed: {e}")
            return {
                'kelly_fraction': 0.1,
                'recommended_weight': 0.1,
                'risk_assessment': 'unknown'
            }
