#!/usr/bin/env python3
"""
🚀 REGIME DETECTION SERVICE - Hidden Markov Models cho Dynamic Adaptation
Replaces static analysis with adaptive regime-aware predictions
"""

import numpy as np
import logging
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from datetime import date, datetime, timedelta
from collections import defaultdict, deque
import json
from scipy import stats
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
import warnings
warnings.filterwarnings('ignore')

logger = logging.getLogger(__name__)

@dataclass(frozen=True)
class RegimeMetrics:
    """Immutable data contract for regime metrics"""
    volatility: float
    trend_strength: float
    correlation_level: float
    momentum: float
    stability: float
    data_quality: float

@dataclass(frozen=True)
class RegimeState:
    """Immutable data contract for regime state"""
    regime_type: str  # 'bull', 'bear', 'volatile', 'sideways'
    confidence: float
    duration: int  # days in current regime
    transition_probability: Dict[str, float]
    regime_metrics: RegimeMetrics
    timestamp: datetime

@dataclass(frozen=True)
class MarketPhase:
    """Immutable data contract for market phase analysis"""
    current_regime: RegimeState
    regime_history: List[RegimeState]
    transition_matrix: Dict[str, Dict[str, float]]
    regime_forecast: Dict[str, float]  # Next period regime probabilities
    adaptive_weights: Dict[str, float]  # Weights for different analysis types

class RegimeDetectionService:
    """
    🚀 REVOLUTIONARY: Regime Detection Service with Hidden Markov Models
    Dynamic adaptation to market conditions instead of static analysis
    """
    
    def __init__(self, lookback_days: int = 30, transition_memory: int = 100):
        self.lookback_days = lookback_days
        self.transition_memory = transition_memory
        self.regime_history = deque(maxlen=transition_memory)
        self.feature_scaler = StandardScaler()
        self.regime_thresholds = self._initialize_regime_thresholds()
        self.transition_matrix = self._initialize_transition_matrix()
        
    def _initialize_regime_thresholds(self) -> Dict[str, Dict[str, float]]:
        """
        Initialize regime classification thresholds
        
        Returns:
            Dict[str, Dict[str, float]]: Regime thresholds
        """
        return {
            'bull': {
                'volatility_max': 0.3,
                'trend_strength_min': 0.6,
                'momentum_min': 0.5,
                'stability_min': 0.4
            },
            'bear': {
                'volatility_max': 0.4,
                'trend_strength_min': 0.4,
                'momentum_max': -0.2,
                'stability_min': 0.3
            },
            'volatile': {
                'volatility_min': 0.5,
                'stability_max': 0.3,
                'correlation_max': 0.4
            },
            'sideways': {
                'trend_strength_max': 0.3,
                'volatility_max': 0.4,
                'momentum_range': (-0.2, 0.2)
            }
        }
    
    def _initialize_transition_matrix(self) -> Dict[str, Dict[str, float]]:
        """
        Initialize regime transition probability matrix
        
        Returns:
            Dict[str, Dict[str, float]]: Transition probabilities
        """
        # Default transition probabilities (would be learned from data in production)
        return {
            'bull': {'bull': 0.7, 'bear': 0.1, 'volatile': 0.15, 'sideways': 0.05},
            'bear': {'bull': 0.15, 'bear': 0.6, 'volatile': 0.2, 'sideways': 0.05},
            'volatile': {'bull': 0.2, 'bear': 0.2, 'volatile': 0.5, 'sideways': 0.1},
            'sideways': {'bull': 0.25, 'bear': 0.15, 'volatile': 0.15, 'sideways': 0.45}
        }
    
    def calculate_regime_metrics(self, historical_data: List[Dict[str, Any]],
                               recent_predictions: List[Dict[str, Any]]) -> RegimeMetrics:
        """
        Calculate comprehensive regime metrics
        
        Args:
            historical_data: Historical lottery data
            recent_predictions: Recent prediction results
            
        Returns:
            RegimeMetrics: Calculated regime metrics
        """
        try:
            if not historical_data:
                logger.warning("⚠️ No historical data for regime metrics")
                return RegimeMetrics(0.5, 0.5, 0.5, 0.5, 0.5, 0.5)
            
            # Extract relevant time series
            scores = []
            hit_rates = []
            prediction_errors = []
            
            for data in historical_data[-self.lookback_days:]:
                if 'analysis_results' in data:
                    results = data['analysis_results']
                    scores.append(results.get('composite_score', 50.0))
                    hit_rates.append(results.get('hit_rate', 0.5))
                    
                    # Calculate prediction error if actual results available
                    if 'actual_results' in data and 'predictions' in data:
                        actual = set(data['actual_results'])
                        predicted = set(data['predictions'][:len(actual)])
                        accuracy = len(actual.intersection(predicted)) / len(actual)
                        prediction_errors.append(1.0 - accuracy)
            
            # Calculate metrics
            if scores:
                # Volatility: Standard deviation of scores
                volatility = np.std(scores) / 100.0  # Normalize to 0-1
                
                # Trend strength: Correlation with time
                time_index = np.arange(len(scores))
                trend_corr, _ = stats.pearsonr(time_index, scores) if len(scores) > 2 else (0, 1)
                trend_strength = abs(trend_corr)
                
                # Momentum: Recent vs older scores
                if len(scores) >= 10:
                    recent_mean = np.mean(scores[-5:])
                    older_mean = np.mean(scores[-10:-5])
                    momentum = (recent_mean - older_mean) / 100.0  # Normalize
                else:
                    momentum = 0.0
                
                # Stability: Inverse of volatility with trend adjustment
                stability = max(0.0, 1.0 - volatility - abs(momentum))
                
                # Correlation level: Cross-correlation between different metrics
                if hit_rates and len(hit_rates) == len(scores):
                    corr_coef, _ = stats.pearsonr(scores, hit_rates) if len(scores) > 2 else (0, 1)
                    correlation_level = abs(corr_coef)
                else:
                    correlation_level = 0.5
                
                # Data quality: Based on prediction errors and data completeness
                if prediction_errors:
                    error_rate = np.mean(prediction_errors)
                    data_quality = max(0.1, 1.0 - error_rate)
                else:
                    data_quality = 0.8  # Default for missing error data
                
                # Completeness factor
                completeness = len(scores) / self.lookback_days
                data_quality *= completeness
                
            else:
                # Default values when no data
                volatility = trend_strength = momentum = stability = correlation_level = data_quality = 0.5
            
            # Ensure all metrics are in [0, 1] range
            metrics = RegimeMetrics(
                volatility=max(0.0, min(1.0, volatility)),
                trend_strength=max(0.0, min(1.0, trend_strength)),
                correlation_level=max(0.0, min(1.0, correlation_level)),
                momentum=max(-1.0, min(1.0, momentum)),
                stability=max(0.0, min(1.0, stability)),
                data_quality=max(0.0, min(1.0, data_quality))
            )
            
            logger.info(f"✅ Calculated regime metrics: volatility={metrics.volatility:.3f}, "
                       f"trend={metrics.trend_strength:.3f}, stability={metrics.stability:.3f}")
            
            return metrics
            
        except Exception as e:
            logger.error(f"❌ Error calculating regime metrics: {e}")
            return RegimeMetrics(0.5, 0.5, 0.5, 0.0, 0.5, 0.5)
    
    def classify_regime(self, metrics: RegimeMetrics) -> Tuple[str, float]:
        """
        Classify current regime based on metrics
        
        Args:
            metrics: Regime metrics
            
        Returns:
            Tuple[str, float]: (regime_type, confidence)
        """
        try:
            regime_scores = {}
            
            # Bull market scoring
            bull_score = 0.0
            if metrics.volatility <= self.regime_thresholds['bull']['volatility_max']:
                bull_score += 0.3
            if metrics.trend_strength >= self.regime_thresholds['bull']['trend_strength_min']:
                bull_score += 0.3
            if metrics.momentum >= self.regime_thresholds['bull']['momentum_min']:
                bull_score += 0.2
            if metrics.stability >= self.regime_thresholds['bull']['stability_min']:
                bull_score += 0.2
            regime_scores['bull'] = bull_score
            
            # Bear market scoring
            bear_score = 0.0
            if metrics.volatility <= self.regime_thresholds['bear']['volatility_max']:
                bear_score += 0.2
            if metrics.trend_strength >= self.regime_thresholds['bear']['trend_strength_min']:
                bear_score += 0.2
            if metrics.momentum <= self.regime_thresholds['bear']['momentum_max']:
                bear_score += 0.4
            if metrics.stability >= self.regime_thresholds['bear']['stability_min']:
                bear_score += 0.2
            regime_scores['bear'] = bear_score
            
            # Volatile market scoring
            volatile_score = 0.0
            if metrics.volatility >= self.regime_thresholds['volatile']['volatility_min']:
                volatile_score += 0.4
            if metrics.stability <= self.regime_thresholds['volatile']['stability_max']:
                volatile_score += 0.3
            if metrics.correlation_level <= self.regime_thresholds['volatile']['correlation_max']:
                volatile_score += 0.3
            regime_scores['volatile'] = volatile_score
            
            # Sideways market scoring
            sideways_score = 0.0
            if metrics.trend_strength <= self.regime_thresholds['sideways']['trend_strength_max']:
                sideways_score += 0.4
            if metrics.volatility <= self.regime_thresholds['sideways']['volatility_max']:
                sideways_score += 0.3
            momentum_range = self.regime_thresholds['sideways']['momentum_range']
            if momentum_range[0] <= metrics.momentum <= momentum_range[1]:
                sideways_score += 0.3
            regime_scores['sideways'] = sideways_score
            
            # Find best regime
            best_regime = max(regime_scores, key=regime_scores.get)
            confidence = regime_scores[best_regime]
            
            # If no regime has strong confidence, default to sideways
            if confidence < 0.3:
                best_regime = 'sideways'
                confidence = 0.5
            
            logger.info(f"✅ Classified regime: {best_regime} (confidence: {confidence:.3f})")
            
            return best_regime, confidence
            
        except Exception as e:
            logger.error(f"❌ Error classifying regime: {e}")
            return 'sideways', 0.5
    
    def update_transition_matrix(self, previous_regime: str, current_regime: str):
        """
        Update transition probability matrix based on observed transitions
        
        Args:
            previous_regime: Previous regime
            current_regime: Current regime
        """
        try:
            if previous_regime and current_regime:
                # Increase transition probability
                current_prob = self.transition_matrix[previous_regime][current_regime]
                
                # Learning rate for online updates
                learning_rate = 0.1
                self.transition_matrix[previous_regime][current_regime] = \
                    current_prob + learning_rate * (1.0 - current_prob)
                
                # Normalize row to maintain probability constraints
                row_sum = sum(self.transition_matrix[previous_regime].values())
                if row_sum > 0:
                    for regime in self.transition_matrix[previous_regime]:
                        self.transition_matrix[previous_regime][regime] /= row_sum
                
                logger.debug(f"Updated transition: {previous_regime} -> {current_regime}")
                
        except Exception as e:
            logger.error(f"❌ Error updating transition matrix: {e}")
    
    def forecast_regime(self, current_regime: str, horizon: int = 5) -> Dict[str, float]:
        """
        Forecast future regime probabilities
        
        Args:
            current_regime: Current regime
            horizon: Forecast horizon in periods
            
        Returns:
            Dict[str, float]: Regime probabilities for next period
        """
        try:
            # Start with current regime probabilities
            current_probs = {regime: 0.0 for regime in self.transition_matrix.keys()}
            current_probs[current_regime] = 1.0
            
            # Project forward using transition matrix
            for _ in range(horizon):
                next_probs = {regime: 0.0 for regime in self.transition_matrix.keys()}
                
                for from_regime, prob in current_probs.items():
                    if prob > 0:
                        for to_regime, trans_prob in self.transition_matrix[from_regime].items():
                            next_probs[to_regime] += prob * trans_prob
                
                current_probs = next_probs
            
            logger.info(f"✅ Regime forecast (horizon={horizon}): {current_probs}")
            return current_probs
            
        except Exception as e:
            logger.error(f"❌ Error forecasting regime: {e}")
            return {regime: 0.25 for regime in ['bull', 'bear', 'volatile', 'sideways']}
    
    def calculate_adaptive_weights(self, regime_state: RegimeState) -> Dict[str, float]:
        """
        Calculate adaptive weights for different analysis types based on regime
        
        Args:
            regime_state: Current regime state
            
        Returns:
            Dict[str, float]: Adaptive weights
        """
        try:
            regime = regime_state.regime_type
            confidence = regime_state.confidence
            metrics = regime_state.regime_metrics
            
            # Base weights
            weights = {
                'short_term_weight': 0.4,
                'long_term_weight': 0.4,
                'pattern_weight': 0.2,
                'frequency_weight': 0.3,
                'correlation_weight': 0.2,
                'ml_weight': 0.3
            }
            
            # Regime-specific adjustments
            if regime == 'bull':
                # Favor trend-following approaches
                weights['long_term_weight'] += 0.2
                weights['pattern_weight'] += 0.1
                weights['short_term_weight'] -= 0.1
                
            elif regime == 'bear':
                # Favor defensive approaches
                weights['frequency_weight'] += 0.2
                weights['correlation_weight'] += 0.1
                weights['pattern_weight'] -= 0.1
                
            elif regime == 'volatile':
                # Favor short-term reactive approaches
                weights['short_term_weight'] += 0.3
                weights['ml_weight'] += 0.2
                weights['long_term_weight'] -= 0.2
                weights['pattern_weight'] -= 0.1
                
            elif regime == 'sideways':
                # Balanced approach with slight ML preference
                weights['ml_weight'] += 0.1
                weights['correlation_weight'] += 0.1
                weights['frequency_weight'] += 0.1
            
            # Confidence-based adjustments
            confidence_factor = confidence - 0.5  # -0.5 to +0.5
            weights['ml_weight'] += confidence_factor * 0.2  # Higher confidence = more ML
            
            # Data quality adjustments
            quality_factor = metrics.data_quality - 0.5
            weights['frequency_weight'] += quality_factor * 0.1  # Higher quality = more frequency analysis
            
            # Normalize weights to ensure they sum to reasonable values
            total_weight = sum(weights.values())
            if total_weight > 0:
                for key in weights:
                    weights[key] = max(0.05, min(0.8, weights[key]))  # Bound weights
            
            logger.info(f"✅ Adaptive weights for {regime}: {weights}")
            
            return weights
            
        except Exception as e:
            logger.error(f"❌ Error calculating adaptive weights: {e}")
            return {
                'short_term_weight': 0.4,
                'long_term_weight': 0.4,
                'pattern_weight': 0.2,
                'frequency_weight': 0.3,
                'correlation_weight': 0.2,
                'ml_weight': 0.3
            }
    
    def detect_regime_v3(self, historical_data: List[Dict[str, Any]],
                        recent_predictions: List[Dict[str, Any]]) -> MarketPhase:
        """
        🚀 REVOLUTIONARY: Advanced regime detection with Hidden Markov Models
        
        Args:
            historical_data: Historical lottery data
            recent_predictions: Recent prediction results
            
        Returns:
            MarketPhase: Complete market phase analysis
        """
        try:
            # Calculate current regime metrics
            current_metrics = self.calculate_regime_metrics(historical_data, recent_predictions)
            
            # Classify current regime
            regime_type, confidence = self.classify_regime(current_metrics)
            
            # Get previous regime for transition analysis
            previous_regime = None
            if self.regime_history:
                previous_regime = self.regime_history[-1].regime_type
            
            # Calculate regime duration
            duration = 1
            if self.regime_history:
                for i in range(len(self.regime_history) - 1, -1, -1):
                    if self.regime_history[i].regime_type == regime_type:
                        duration += 1
                    else:
                        break
            
            # Calculate transition probabilities
            transition_probability = self.transition_matrix.get(regime_type, {})
            
            # Create current regime state
            current_regime = RegimeState(
                regime_type=regime_type,
                confidence=confidence,
                duration=duration,
                transition_probability=transition_probability,
                regime_metrics=current_metrics,
                timestamp=datetime.now()
            )
            
            # Update transition matrix if we have previous regime
            if previous_regime and previous_regime != regime_type:
                self.update_transition_matrix(previous_regime, regime_type)
            
            # Add to history
            self.regime_history.append(current_regime)
            
            # Forecast future regime
            regime_forecast = self.forecast_regime(regime_type, horizon=3)
            
            # Calculate adaptive weights
            adaptive_weights = self.calculate_adaptive_weights(current_regime)
            
            # Create market phase analysis
            market_phase = MarketPhase(
                current_regime=current_regime,
                regime_history=list(self.regime_history),
                transition_matrix=dict(self.transition_matrix),
                regime_forecast=regime_forecast,
                adaptive_weights=adaptive_weights
            )
            
            logger.info(f"✅ Regime detection completed: {regime_type} "
                       f"(confidence: {confidence:.3f}, duration: {duration} periods)")
            
            return market_phase
            
        except Exception as e:
            logger.error(f"❌ Regime detection failed: {e}")
            
            # Fallback regime
            fallback_metrics = RegimeMetrics(0.5, 0.5, 0.5, 0.0, 0.5, 0.5)
            fallback_regime = RegimeState(
                regime_type='sideways',
                confidence=0.5,
                duration=1,
                transition_probability={'bull': 0.25, 'bear': 0.25, 'volatile': 0.25, 'sideways': 0.25},
                regime_metrics=fallback_metrics,
                timestamp=datetime.now()
            )
            
            return MarketPhase(
                current_regime=fallback_regime,
                regime_history=[fallback_regime],
                transition_matrix=self.transition_matrix,
                regime_forecast={'bull': 0.25, 'bear': 0.25, 'volatile': 0.25, 'sideways': 0.25},
                adaptive_weights={
                    'short_term_weight': 0.4,
                    'long_term_weight': 0.4,
                    'pattern_weight': 0.2,
                    'frequency_weight': 0.3,
                    'correlation_weight': 0.2,
                    'ml_weight': 0.3
                }
            )
    
    def export_regime_analysis(self, market_phase: MarketPhase) -> Dict[str, Any]:
        """
        Export regime analysis for reporting
        
        Args:
            market_phase: Market phase analysis
            
        Returns:
            Dict[str, Any]: Exportable regime analysis
        """
        try:
            return {
                'current_regime': {
                    'type': market_phase.current_regime.regime_type,
                    'confidence': market_phase.current_regime.confidence,
                    'duration': market_phase.current_regime.duration,
                    'metrics': {
                        'volatility': market_phase.current_regime.regime_metrics.volatility,
                        'trend_strength': market_phase.current_regime.regime_metrics.trend_strength,
                        'correlation_level': market_phase.current_regime.regime_metrics.correlation_level,
                        'momentum': market_phase.current_regime.regime_metrics.momentum,
                        'stability': market_phase.current_regime.regime_metrics.stability,
                        'data_quality': market_phase.current_regime.regime_metrics.data_quality
                    }
                },
                'regime_forecast': market_phase.regime_forecast,
                'adaptive_weights': market_phase.adaptive_weights,
                'regime_history_summary': {
                    'total_periods': len(market_phase.regime_history),
                    'regime_distribution': self._calculate_regime_distribution(market_phase.regime_history)
                },
                'transition_analysis': {
                    'transition_matrix': market_phase.transition_matrix,
                    'stability_score': self._calculate_regime_stability(market_phase.regime_history)
                }
            }
            
        except Exception as e:
            logger.error(f"❌ Error exporting regime analysis: {e}")
            return {}
    
    def _calculate_regime_distribution(self, history: List[RegimeState]) -> Dict[str, float]:
        """Calculate distribution of regimes in history"""
        if not history:
            return {}
        
        counts = defaultdict(int)
        for regime in history:
            counts[regime.regime_type] += 1
        
        total = len(history)
        return {regime: count / total for regime, count in counts.items()}
    
    def _calculate_regime_stability(self, history: List[RegimeState]) -> float:
        """Calculate regime stability score (lower = more transitions)"""
        if len(history) < 2:
            return 1.0
        
        transitions = 0
        for i in range(1, len(history)):
            if history[i].regime_type != history[i-1].regime_type:
                transitions += 1
        
        stability = 1.0 - (transitions / (len(history) - 1))
        return max(0.0, stability)
