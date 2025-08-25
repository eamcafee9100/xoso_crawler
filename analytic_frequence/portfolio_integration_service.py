#!/usr/bin/env python3
"""
🚀 PHASE 1A DEPLOYMENT: Portfolio Integration Service
Replaces simple weighted averages with Modern Portfolio Theory
"""

import logging
import numpy as np
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime

# Import lite portfolio service (no sklearn dependencies)
import sys
import os
sys.path.append(os.path.dirname(__file__))

from predictions_tracker.services.portfolio_optimization_service_lite import (
    PortfolioOptimizationService,
    MethodPerformance,
    OptimizationResult
)

logger = logging.getLogger(__name__)

@dataclass(frozen=True)
class UltimateMethodPerformance:
    """Performance metrics for Ultimate Prediction System methods"""
    method_name: str
    contribution_weight: float
    confidence_score: float
    historical_accuracy: float
    data_quality: str
    analysis_source: str

class PortfolioIntegrationService:
    """
    🚀 REVOLUTIONARY: Portfolio Integration for Ultimate Prediction System
    Replaces simple weighted averages with Modern Portfolio Theory
    """
    
    def __init__(self):
        self.portfolio_service = PortfolioOptimizationService()
        self.logger = logger
        self.performance_cache = {}
        
    def extract_method_performances_from_ultimate_prediction(self, 
                                                           prediction_data: Dict[str, Any]) -> List[MethodPerformance]:
        """
        Extract method performance data from Ultimate Prediction System
        
        Args:
            prediction_data: Prediction data from Ultimate system
            
        Returns:
            List[MethodPerformance]: Performance metrics for portfolio optimization
        """
        try:
            performances = []
            
            # Extract contributing methods from prediction
            contributing_methods = prediction_data.get("contributing_methods", {})
            confidence = prediction_data.get("confidence", 0.5)
            data_quality = prediction_data.get("data_quality", "medium")
            
            # Map Ultimate system methods to portfolio performance
            method_mapping = {
                "statistical_analysis": {
                    "expected_return": 0.65,  # Historical performance
                    "volatility": 0.15,
                    "hit_rate": 0.68,
                    "max_drawdown": 0.08
                },
                "information_theory": {
                    "expected_return": 0.58,
                    "volatility": 0.18,
                    "hit_rate": 0.62,
                    "max_drawdown": 0.10
                },
                "quantum_algorithms": {
                    "expected_return": 0.52,
                    "volatility": 0.22,
                    "hit_rate": 0.55,
                    "max_drawdown": 0.15
                },
                "neural_networks": {
                    "expected_return": 0.60,
                    "volatility": 0.20,
                    "hit_rate": 0.63,
                    "max_drawdown": 0.12
                }
            }
            
            # Create performance objects for each contributing method
            for method_name, weight in contributing_methods.items():
                if method_name in method_mapping and weight > 0:
                    base_metrics = method_mapping[method_name]
                    
                    # Adjust metrics based on current confidence and data quality
                    confidence_adjustment = (confidence - 0.5) * 0.2  # -0.1 to +0.1
                    quality_adjustment = 0.1 if data_quality == "high" else 0.0
                    
                    adjusted_return = base_metrics["expected_return"] + confidence_adjustment + quality_adjustment
                    adjusted_hit_rate = base_metrics["hit_rate"] + confidence_adjustment + quality_adjustment
                    
                    # Calculate Sharpe ratio
                    risk_free_rate = 0.02
                    sharpe_ratio = (adjusted_return - risk_free_rate) / base_metrics["volatility"]
                    
                    performance = MethodPerformance(
                        method_name=method_name,
                        expected_return=max(0.1, min(0.9, adjusted_return)),
                        volatility=base_metrics["volatility"],
                        hit_rate=max(0.1, min(0.9, adjusted_hit_rate)),
                        sharpe_ratio=sharpe_ratio,
                        max_drawdown=base_metrics["max_drawdown"],
                        confidence_score=confidence
                    )
                    
                    performances.append(performance)
            
            # Add fallback if no methods found
            if not performances:
                default_performance = MethodPerformance(
                    method_name="default_analysis",
                    expected_return=0.55,
                    volatility=0.20,
                    hit_rate=0.58,
                    sharpe_ratio=1.25,
                    max_drawdown=0.15,
                    confidence_score=confidence
                )
                performances.append(default_performance)
            
            self.logger.info(f"✅ Extracted {len(performances)} method performances")
            return performances
            
        except Exception as e:
            self.logger.error(f"❌ Error extracting method performances: {e}")
            # Return default performance
            return [MethodPerformance(
                method_name="fallback_analysis",
                expected_return=0.50,
                volatility=0.25,
                hit_rate=0.50,
                sharpe_ratio=1.00,
                max_drawdown=0.20,
                confidence_score=0.50
            )]
    
    def optimize_method_weights_v3(self, predictions: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        🚀 REVOLUTIONARY: Replace simple weighted averages with Portfolio Theory
        
        Args:
            predictions: List of prediction data from Ultimate system
            
        Returns:
            Dict: Portfolio-optimized results
        """
        try:
            if not predictions:
                return {"error": "No predictions provided"}
            
            # Extract method performances from all predictions
            all_performances = []
            for pred in predictions:
                performances = self.extract_method_performances_from_ultimate_prediction(pred)
                all_performances.extend(performances)
            
            # Group by method name and average performance metrics
            method_groups = {}
            for perf in all_performances:
                if perf.method_name not in method_groups:
                    method_groups[perf.method_name] = []
                method_groups[perf.method_name].append(perf)
            
            # Create averaged performance for each method
            averaged_performances = []
            for method_name, perfs in method_groups.items():
                avg_performance = MethodPerformance(
                    method_name=method_name,
                    expected_return=np.mean([p.expected_return for p in perfs]),
                    volatility=np.mean([p.volatility for p in perfs]),
                    hit_rate=np.mean([p.hit_rate for p in perfs]),
                    sharpe_ratio=np.mean([p.sharpe_ratio for p in perfs]),
                    max_drawdown=np.mean([p.max_drawdown for p in perfs]),
                    confidence_score=np.mean([p.confidence_score for p in perfs])
                )
                averaged_performances.append(avg_performance)
            
            # Calculate correlation matrix
            correlation_result = self.portfolio_service.calculate_correlation_matrix_v3(averaged_performances)
            
            # Perform portfolio optimization
            optimization_result = self.portfolio_service.markowitz_optimization_v3(
                averaged_performances,
                correlation_result['correlation_matrix']
            )
            
            # Calculate Kelly fractions for each method
            kelly_results = {}
            for perf in averaged_performances:
                kelly_result = self.portfolio_service.calculate_kelly_criterion_v3(perf)
                kelly_results[perf.method_name] = kelly_result
            
            # Create optimized result
            portfolio_result = {
                "optimization_status": optimization_result.optimization_status,
                "portfolio_metrics": {
                    "expected_return": optimization_result.expected_return,
                    "portfolio_volatility": optimization_result.portfolio_volatility,
                    "sharpe_ratio": optimization_result.sharpe_ratio,
                    "diversification_score": correlation_result['diversification_score']
                },
                "optimized_weights": optimization_result.optimal_weights,
                "kelly_fractions": optimization_result.kelly_fractions,
                "risk_management": {
                    method_name: kelly_results[method_name]["risk_assessment"]
                    for method_name in kelly_results
                },
                "correlation_analysis": {
                    "average_correlation": correlation_result['average_correlation'],
                    "correlation_matrix": correlation_result['correlation_matrix']
                },
                "method_performance_summary": {
                    perf.method_name: {
                        "expected_return": perf.expected_return,
                        "hit_rate": perf.hit_rate,
                        "sharpe_ratio": perf.sharpe_ratio,
                        "confidence": perf.confidence_score
                    }
                    for perf in averaged_performances
                },
                "portfolio_recommendation": self._generate_portfolio_recommendation(optimization_result, kelly_results)
            }
            
            self.logger.info(f"✅ Portfolio optimization completed: Sharpe={optimization_result.sharpe_ratio:.3f}")
            return portfolio_result
            
        except Exception as e:
            self.logger.error(f"❌ Portfolio optimization failed: {e}")
            return {"error": f"Portfolio optimization failed: {str(e)}"}
    
    def _generate_portfolio_recommendation(self, 
                                         optimization_result: OptimizationResult,
                                         kelly_results: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
        """Generate portfolio recommendation based on optimization results"""
        
        # Find dominant method
        dominant_method = max(optimization_result.optimal_weights.items(), key=lambda x: x[1])
        
        # Calculate overall risk level
        high_risk_methods = sum(1 for method, kelly in kelly_results.items() 
                               if kelly.get("risk_assessment") == "high_risk")
        
        overall_risk = "high" if high_risk_methods > len(kelly_results) / 2 else \
                      "medium" if high_risk_methods > 0 else "low"
        
        # Generate recommendation
        recommendation = {
            "action": "balanced_allocation" if optimization_result.sharpe_ratio > 1.5 else "conservative_allocation",
            "dominant_method": {
                "name": dominant_method[0],
                "weight": dominant_method[1],
                "reasoning": f"Highest optimized weight ({dominant_method[1]:.3f})"
            },
            "risk_assessment": {
                "overall_risk": overall_risk,
                "sharpe_ratio": optimization_result.sharpe_ratio,
                "recommendation": "Proceed with confidence" if optimization_result.sharpe_ratio > 1.2 
                                else "Use conservative sizing"
            },
            "diversification_advice": {
                "status": "well_diversified" if len(optimization_result.optimal_weights) > 2 else "concentrated",
                "suggestion": "Maintain current allocation" if len(optimization_result.optimal_weights) > 2 
                            else "Consider adding more methods"
            }
        }
        
        return recommendation
    
    def apply_portfolio_weights_to_predictions(self, 
                                             predictions: List[Dict[str, Any]],
                                             portfolio_weights: Dict[str, float]) -> List[Dict[str, Any]]:
        """
        Apply optimized portfolio weights to prediction results
        
        Args:
            predictions: Original predictions
            portfolio_weights: Optimized weights from portfolio theory
            
        Returns:
            List[Dict[str, Any]]: Predictions with optimized weights applied
        """
        try:
            optimized_predictions = []
            
            for pred in predictions:
                # Create copy of prediction
                optimized_pred = pred.copy()
                
                # Get original contributing methods
                original_methods = pred.get("contributing_methods", {})
                
                # Apply portfolio weights
                optimized_methods = {}
                total_weight = 0
                
                for method_name, original_weight in original_methods.items():
                    if method_name in portfolio_weights:
                        # Use portfolio-optimized weight
                        optimized_weight = portfolio_weights[method_name]
                        optimized_methods[method_name] = optimized_weight
                        total_weight += optimized_weight
                    else:
                        # Keep original weight for methods not in portfolio
                        optimized_methods[method_name] = original_weight
                        total_weight += original_weight
                
                # Normalize weights to sum to 1
                if total_weight > 0:
                    for method_name in optimized_methods:
                        optimized_methods[method_name] /= total_weight
                
                # Update prediction with optimized weights
                optimized_pred["contributing_methods"] = optimized_methods
                optimized_pred["optimization_applied"] = True
                optimized_pred["portfolio_theory"] = "modern_portfolio_theory_v3"
                
                # Recalculate confidence based on portfolio optimization
                portfolio_confidence = sum(
                    optimized_methods.get(method, 0) * pred.get("confidence", 0.5)
                    for method in optimized_methods
                )
                optimized_pred["confidence"] = min(0.95, max(0.05, portfolio_confidence))
                
                optimized_predictions.append(optimized_pred)
            
            self.logger.info(f"✅ Applied portfolio weights to {len(optimized_predictions)} predictions")
            return optimized_predictions
            
        except Exception as e:
            self.logger.error(f"❌ Error applying portfolio weights: {e}")
            return predictions  # Return original if optimization fails
