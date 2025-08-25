#!/usr/bin/env python3
"""
🚀 PORTFOLIO OPTIMIZATION SERVICE - Modern Portfolio Theory cho Lottery Prediction
Implements revolutionary portfolio optimization algorithms
"""

import numpy as np
import logging
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from datetime import date, datetime
from scipy.optimize import minimize
from scipy.stats import pearsonr
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
class MethodCorrelation:
    """Immutable data contract for method correlation"""
    method_1: str
    method_2: str
    correlation: float
    confidence: float
    sample_size: int

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

@dataclass(frozen=True)
class PortfolioOptimizationResult:
    """Immutable data contract for portfolio optimization result"""
    optimal_weights: Dict[str, float]
    expected_return: float
    portfolio_risk: float
    sharpe_ratio: float
    kelly_fractions: Dict[str, float]
    optimization_status: str
    optimization_details: Dict[str, Any]

@dataclass(frozen=True)
class MarketRegime:
    """Immutable data contract for market regime"""
    regime_type: str  # 'bull', 'bear', 'sideways', 'volatile'
    confidence: float
    volatility_level: float
    trend_strength: float
    regime_duration: int

class MarketRegimeEnum(Enum):
    """Market regime enumeration"""
    BULL = "bull"
    BEAR = "bear"
    VOLATILE = "volatile"
    SIDEWAYS = "sideways"

class PortfolioOptimizationService:
    """
    🚀 REVOLUTIONARY: Modern Portfolio Theory Service
    Implements Markowitz optimization, Kelly Criterion, and regime-aware selection
    """
    
    def __init__(self):
        self.correlation_cache = {}
        self.regime_cache = {}
        
    def calculate_method_correlations(self, method_data: Dict[str, List[bool]]) -> Dict[Tuple[str, str], MethodCorrelation]:
        """
        Calculate correlations between prediction methods
        
        Args:
            method_data: Dict[method_id, List[hit_results]]
            
        Returns:
            Dict[Tuple[method_id_1, method_id_2], MethodCorrelation]
        """
        try:
            correlations = {}
            method_ids = list(method_data.keys())
            
            for i, method_1 in enumerate(method_ids):
                for j, method_2 in enumerate(method_ids[i+1:], i+1):
                    # Get data for both methods
                    data_1 = method_data[method_1]
                    data_2 = method_data[method_2]
                    
                    # Ensure same length
                    min_length = min(len(data_1), len(data_2))
                    if min_length < 10:  # Minimum sample size
                        continue
                        
                    data_1 = data_1[-min_length:]
                    data_2 = data_2[-min_length:]
                    
                    # Convert boolean to numeric
                    numeric_1 = [1 if x else 0 for x in data_1]
                    numeric_2 = [1 if x else 0 for x in data_2]
                    
                    # Calculate correlation
                    if np.std(numeric_1) > 0 and np.std(numeric_2) > 0:
                        correlation, p_value = pearsonr(numeric_1, numeric_2)
                        confidence = 1 - p_value if p_value < 1.0 else 0.0
                    else:
                        correlation = 0.0
                        confidence = 0.0
                    
                    correlations[(method_1, method_2)] = MethodCorrelation(
                        method_1=method_1,
                        method_2=method_2,
                        correlation=correlation,
                        confidence=confidence,
                        sample_size=min_length
                    )
            
            logger.info(f"✅ Calculated {len(correlations)} method correlations")
            return correlations
            
        except Exception as e:
            logger.error(f"❌ Error calculating correlations: {e}")
            return {}
    
    def build_correlation_matrix(self, method_correlations: Dict[Tuple[str, str], MethodCorrelation], 
                                method_ids: List[str]) -> np.ndarray:
        """
        Build correlation matrix from method correlations
        
        Args:
            method_correlations: Correlation data
            method_ids: List of method IDs
            
        Returns:
            np.ndarray: Correlation matrix
        """
        try:
            n = len(method_ids)
            matrix = np.eye(n)  # Identity matrix (1.0 on diagonal)
            
            method_to_idx = {method_id: idx for idx, method_id in enumerate(method_ids)}
            
            for (method_1, method_2), corr_data in method_correlations.items():
                if method_1 in method_to_idx and method_2 in method_to_idx:
                    i = method_to_idx[method_1]
                    j = method_to_idx[method_2]
                    
                    # Symmetric matrix
                    matrix[i, j] = corr_data.correlation
                    matrix[j, i] = corr_data.correlation
            
            # Ensure positive semi-definite
            eigenvals, eigenvecs = np.linalg.eigh(matrix)
            eigenvals = np.maximum(eigenvals, 0.01)  # Regularize small eigenvalues
            matrix = eigenvecs @ np.diag(eigenvals) @ eigenvecs.T
            
            return matrix
            
        except Exception as e:
            logger.error(f"❌ Error building correlation matrix: {e}")
            return np.eye(len(method_ids))
    
    def detect_market_regime(self, historical_performance: Dict[str, List[float]], 
                           analysis_date: date) -> MarketRegime:
        """
        Detect current market regime based on historical performance
        
        Args:
            historical_performance: Dict[method_id, List[hit_rates]]
            analysis_date: Analysis date
            
        Returns:
            MarketRegime: Detected market regime
        """
        try:
            if not historical_performance:
                return MarketRegime(
                    regime_type='sideways',
                    confidence=0.5,
                    volatility_level=0.5,
                    trend_strength=0.0,
                    regime_duration=30
                )
            
            # Aggregate performance across all methods
            all_performances = []
            for method_performances in historical_performance.values():
                all_performances.extend(method_performances[-30:])  # Last 30 data points
            
            if len(all_performances) < 10:
                return MarketRegime(
                    regime_type='sideways',
                    confidence=0.3,
                    volatility_level=0.5,
                    trend_strength=0.0,
                    regime_duration=10
                )
            
            # Calculate regime indicators
            mean_performance = np.mean(all_performances)
            volatility = np.std(all_performances)
            
            # Calculate trend (linear regression slope)
            x = np.arange(len(all_performances))
            trend_slope = np.polyfit(x, all_performances, 1)[0]
            
            # Determine regime type
            if trend_slope > 0.01 and mean_performance > 0.5:
                regime_type = 'bull'
                confidence = min(0.9, abs(trend_slope) * 10)
            elif trend_slope < -0.01 and mean_performance < 0.4:
                regime_type = 'bear'
                confidence = min(0.9, abs(trend_slope) * 10)
            elif volatility > 0.3:
                regime_type = 'volatile'
                confidence = min(0.8, volatility * 2)
            else:
                regime_type = 'sideways'
                confidence = 0.6
            
            return MarketRegime(
                regime_type=regime_type,
                confidence=confidence,
                volatility_level=volatility,
                trend_strength=abs(trend_slope),
                regime_duration=len(all_performances)
            )
            
        except Exception as e:
            logger.error(f"❌ Error detecting market regime: {e}")
            return MarketRegime(
                regime_type='sideways',
                confidence=0.3,
                volatility_level=0.5,
                trend_strength=0.0,
                regime_duration=10
            )
    
    def markowitz_optimization(self, expected_returns: List[float], 
                             correlation_matrix: np.ndarray,
                             risk_tolerance: float = 0.5) -> PortfolioOptimizationResult:
        """
        Perform Markowitz mean-variance optimization
        
        Args:
            expected_returns: Expected returns for each method
            correlation_matrix: Method correlation matrix
            risk_tolerance: Risk tolerance parameter (0-1)
            
        Returns:
            PortfolioOptimizationResult: Optimization result
        """
        try:
            n = len(expected_returns)
            if n == 0:
                raise ValueError("No methods to optimize")
            
            returns = np.array(expected_returns)
            
            # Convert correlation to covariance (assume uniform volatility)
            volatilities = np.full(n, 0.2)  # Assume 20% volatility
            covariance_matrix = correlation_matrix * np.outer(volatilities, volatilities)
            
            # Objective function: minimize risk - risk_tolerance * return
            def objective(weights):
                portfolio_return = np.dot(weights, returns)
                portfolio_risk = np.sqrt(np.dot(weights, np.dot(covariance_matrix, weights)))
                return portfolio_risk - risk_tolerance * portfolio_return
            
            # Constraints
            constraints = [
                {'type': 'eq', 'fun': lambda x: np.sum(x) - 1}  # Sum to 1
            ]
            
            # Bounds (0 to 1 for each weight)
            bounds = [(0, 1) for _ in range(n)]
            
            # Initial guess (equal weights)
            x0 = np.full(n, 1.0 / n)
            
            # Optimize
            result = minimize(
                objective, x0, method='SLSQP',
                bounds=bounds, constraints=constraints,
                options={'maxiter': 1000, 'ftol': 1e-9}
            )
            
            if result.success:
                optimal_weights = result.x
                portfolio_return = np.dot(optimal_weights, returns)
                portfolio_risk = np.sqrt(np.dot(optimal_weights, np.dot(covariance_matrix, optimal_weights)))
                sharpe_ratio = portfolio_return / portfolio_risk if portfolio_risk > 0 else 0
                
                # Calculate Kelly fractions
                kelly_fractions = self._calculate_kelly_fractions(returns, covariance_matrix, optimal_weights)
                
                return PortfolioOptimizationResult(
                    optimal_weights={f"method_{i}": weight for i, weight in enumerate(optimal_weights)},
                    expected_return=portfolio_return,
                    portfolio_risk=portfolio_risk,
                    sharpe_ratio=sharpe_ratio,
                    kelly_fractions=kelly_fractions,
                    optimization_status="success",
                    optimization_details={
                        "iterations": result.nit,
                        "function_value": result.fun,
                        "risk_tolerance": risk_tolerance
                    }
                )
            else:
                raise ValueError(f"Optimization failed: {result.message}")
                
        except Exception as e:
            logger.error(f"❌ Markowitz optimization failed: {e}")
            # Fallback to equal weights
            n = len(expected_returns)
            equal_weights = {f"method_{i}": 1.0/n for i in range(n)}
            
            return PortfolioOptimizationResult(
                optimal_weights=equal_weights,
                expected_return=np.mean(expected_returns) if expected_returns else 0.0,
                portfolio_risk=0.2,
                sharpe_ratio=0.5,
                kelly_fractions=equal_weights,
                optimization_status="fallback_equal_weights",
                optimization_details={"error": str(e)}
            )
    
    def _calculate_kelly_fractions(self, returns: np.ndarray, covariance_matrix: np.ndarray, 
                                 optimal_weights: np.ndarray) -> Dict[str, float]:
        """
        Calculate Kelly criterion fractions for optimal bet sizing
        
        Args:
            returns: Expected returns
            covariance_matrix: Covariance matrix
            optimal_weights: Optimal portfolio weights
            
        Returns:
            Dict[str, float]: Kelly fractions for each method
        """
        try:
            # Kelly fraction = (expected_return - risk_free_rate) / variance
            # Assuming risk_free_rate = 0 for lottery prediction
            
            kelly_fractions = {}
            for i, (return_val, weight) in enumerate(zip(returns, optimal_weights)):
                variance = covariance_matrix[i, i]
                kelly_fraction = return_val / variance if variance > 0 else 0.0
                
                # Cap Kelly fraction to avoid over-leveraging
                kelly_fraction = min(kelly_fraction, 0.25)  # Max 25%
                kelly_fraction = max(kelly_fraction, 0.0)   # Min 0%
                
                kelly_fractions[f"method_{i}"] = kelly_fraction
            
            # Normalize Kelly fractions to sum to 1
            total_kelly = sum(kelly_fractions.values())
            if total_kelly > 0:
                kelly_fractions = {k: v/total_kelly for k, v in kelly_fractions.items()}
            
            return kelly_fractions
            
        except Exception as e:
            logger.error(f"❌ Error calculating Kelly fractions: {e}")
            n = len(returns)
            return {f"method_{i}": 1.0/n for i in range(n)}
    
    def get_regime_multiplier(self, market_regime: MarketRegime) -> float:
        """
        Get regime-specific risk multiplier
        
        Args:
            market_regime: Detected market regime
            
        Returns:
            float: Risk multiplier
        """
        multipliers = {
            'bull': 1.2,      # More aggressive in bull markets
            'bear': 0.7,      # More conservative in bear markets
            'volatile': 0.8,  # Conservative in volatile markets
            'sideways': 1.0   # Normal allocation in sideways markets
        }
        
        base_multiplier = multipliers.get(market_regime.regime_type, 1.0)
        confidence_adjustment = 0.8 + (market_regime.confidence * 0.4)  # 0.8 to 1.2
        
        return base_multiplier * confidence_adjustment
    
    def revolutionary_method_selection_v3(self, hybrid_results: Dict[str, Any], 
                                        analysis_date: date,
                                        target_hit_rate: float = 0.4) -> Dict[str, Any]:
        """
        🚀 REVOLUTIONARY: Modern Portfolio Theory method selection
        
        Args:
            hybrid_results: Method analysis results
            analysis_date: Analysis date
            target_hit_rate: Target hit rate
            
        Returns:
            Dict[str, Any]: Optimized method selection results
        """
        try:
            if not hybrid_results:
                return {"error": "No hybrid results provided"}
            
            # Extract method data
            method_ids = list(hybrid_results.keys())
            expected_returns = [
                hybrid_results[mid].get("expected_hit_rate", 0.0) 
                for mid in method_ids
            ]
            
            # Build performance history for correlation calculation
            method_performance_data = {}
            for method_id in method_ids:
                # Simulate performance history (in real implementation, get from database)
                performance = hybrid_results[method_id].get("performance_history", [])
                if not performance:
                    performance = [np.random.random() > 0.5 for _ in range(30)]  # Fallback
                method_performance_data[method_id] = performance
            
            # Calculate correlations
            method_correlations = self.calculate_method_correlations(method_performance_data)
            correlation_matrix = self.build_correlation_matrix(method_correlations, method_ids)
            
            # Detect market regime
            performance_history = {
                mid: [0.8 if x else 0.2 for x in method_performance_data[mid]]
                for mid in method_ids
            }
            market_regime = self.detect_market_regime(performance_history, analysis_date)
            
            # Get regime-aware risk tolerance
            risk_tolerance = 0.5 * self.get_regime_multiplier(market_regime)
            
            # Perform Markowitz optimization
            optimization_result = self.markowitz_optimization(
                expected_returns, correlation_matrix, risk_tolerance
            )
            
            # Apply portfolio selection
            selected_methods = {}
            for i, method_id in enumerate(method_ids):
                weight_key = f"method_{i}"
                if weight_key in optimization_result.optimal_weights:
                    weight = optimization_result.optimal_weights[weight_key]
                    kelly_fraction = optimization_result.kelly_fractions.get(weight_key, 0.0)
                    
                    # Only include methods with significant weight
                    if weight >= 0.05:  # Minimum 5% allocation
                        selected_methods[method_id] = {
                            **hybrid_results[method_id],
                            "portfolio_weight": weight,
                            "kelly_fraction": kelly_fraction,
                            "selection_reason": f"Portfolio optimization (weight: {weight:.3f})"
                        }
            
            logger.info(f"✅ Portfolio optimization completed: {len(selected_methods)} methods selected")
            
            return {
                "selected_methods": selected_methods,
                "optimization_result": optimization_result,
                "market_regime": market_regime,
                "method_correlations": method_correlations,
                "portfolio_metrics": {
                    "expected_return": optimization_result.expected_return,
                    "portfolio_risk": optimization_result.portfolio_risk,
                    "sharpe_ratio": optimization_result.sharpe_ratio,
                    "diversification_score": len(selected_methods) / len(method_ids)
                },
                "analysis_metadata": {
                    "analysis_date": analysis_date.isoformat(),
                    "target_hit_rate": target_hit_rate,
                    "optimization_status": optimization_result.optimization_status,
                    "total_methods_analyzed": len(method_ids),
                    "methods_selected": len(selected_methods)
                }
            }
            
        except Exception as e:
            logger.error(f"❌ Revolutionary method selection failed: {e}")
            return {
                "error": str(e),
                "fallback_methods": hybrid_results,
                "analysis_metadata": {
                    "analysis_date": analysis_date.isoformat(),
                    "optimization_status": "failed_fallback_used"
                }
            }
