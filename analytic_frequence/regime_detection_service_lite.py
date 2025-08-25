"""
🎯 Regime Detection Service - Lite Version (Phase 1B)
=====================================================

Market regime detection without heavy ML dependencies.
Uses statistical methods and pattern recognition to identify different market states.

Features:
- Volatility regime detection
- Trend regime identification
- Pattern regime classification
- Regime transition prediction
"""

import numpy as np
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass, field
from datetime import datetime, date, timedelta
from enum import Enum
import json
import logging

logger = logging.getLogger(__name__)

class RegimeType(Enum):
    """Market regime types"""
    STABLE = "stable"
    VOLATILE = "volatile"
    TRENDING_UP = "trending_up"
    TRENDING_DOWN = "trending_down"
    SIDEWAYS = "sideways"
    BREAKOUT = "breakout"
    REVERSAL = "reversal"
    UNKNOWN = "unknown"

@dataclass(frozen=True)
class RegimeFeatures:
    """Statistical features for regime detection"""
    volatility: float
    trend_strength: float
    momentum: float
    autocorrelation: float
    volatility_of_volatility: float
    skewness: float
    kurtosis: float
    hurst_exponent: Optional[float] = None

@dataclass(frozen=True)
class RegimeState:
    """Current regime state"""
    regime_type: RegimeType
    confidence: float
    features: RegimeFeatures
    probability_distribution: Dict[RegimeType, float]
    duration: int  # Days in current regime
    stability_score: float
    timestamp: datetime = field(default_factory=datetime.now)

@dataclass(frozen=True)
class RegimeTransition:
    """Regime transition prediction"""
    from_regime: RegimeType
    to_regime: RegimeType
    transition_probability: float
    expected_duration: int
    trigger_conditions: List[str]
    confidence: float

class RegimeDetectionServiceLite:
    """
    🎯 Regime Detection Service - Lite Implementation
    
    Detects market regimes using statistical methods without heavy ML dependencies.
    Provides real-time regime identification and transition prediction.
    """
    
    def __init__(self, lookback_window: int = 30):
        """Initialize regime detection service"""
        self.lookback_window = lookback_window
        self.regime_history = []
        self.current_regime = None
        self.transition_matrix = self._initialize_transition_matrix()
        self.regime_thresholds = self._initialize_thresholds()
        
        logger.info(f"✅ Regime Detection Service initialized (window: {lookback_window})")
    
    def detect_current_regime(self, data: List[float]) -> RegimeState:
        """
        🎯 Detect Current Market Regime
        
        Analyzes recent data to identify the current market regime
        """
        try:
            if len(data) < self.lookback_window:
                logger.warning(f"Insufficient data: {len(data)} < {self.lookback_window}")
                return self._create_unknown_regime()
            
            # Extract statistical features
            features = self._extract_regime_features(data)
            
            # Calculate regime probabilities
            regime_probabilities = self._calculate_regime_probabilities(features)
            
            # Determine most likely regime
            most_likely_regime = max(regime_probabilities.items(), key=lambda x: x[1])
            regime_type = most_likely_regime[0]
            confidence = most_likely_regime[1]
            
            # Calculate stability score
            stability_score = self._calculate_stability_score(regime_probabilities)
            
            # Determine duration in current regime
            duration = self._calculate_regime_duration(regime_type)
            
            regime_state = RegimeState(
                regime_type=regime_type,
                confidence=confidence,
                features=features,
                probability_distribution=regime_probabilities,
                duration=duration,
                stability_score=stability_score
            )
            
            # Update history
            self._update_regime_history(regime_state)
            
            logger.info(f"✅ Detected regime: {regime_type.value} "
                       f"(confidence: {confidence:.3f}, stability: {stability_score:.3f})")
            
            return regime_state
            
        except Exception as e:
            logger.error(f"❌ Error detecting regime: {e}")
            return self._create_unknown_regime()
    
    def predict_regime_transition(self, current_regime: RegimeState, 
                                 forecast_horizon: int = 7) -> List[RegimeTransition]:
        """
        🔮 Predict Regime Transitions
        
        Predicts likely regime transitions in the near future
        """
        try:
            transitions = []
            
            for target_regime in RegimeType:
                if target_regime == current_regime.regime_type or target_regime == RegimeType.UNKNOWN:
                    continue
                
                # Calculate transition probability
                transition_prob = self._calculate_transition_probability(
                    current_regime.regime_type, target_regime, current_regime.features
                )
                
                if transition_prob > 0.1:  # Only include meaningful transitions
                    # Estimate duration
                    expected_duration = self._estimate_regime_duration(target_regime)
                    
                    # Identify trigger conditions
                    triggers = self._identify_trigger_conditions(
                        current_regime.regime_type, target_regime, current_regime.features
                    )
                    
                    # Calculate overall confidence
                    confidence = min(1.0, transition_prob * current_regime.confidence)
                    
                    transition = RegimeTransition(
                        from_regime=current_regime.regime_type,
                        to_regime=target_regime,
                        transition_probability=transition_prob,
                        expected_duration=expected_duration,
                        trigger_conditions=triggers,
                        confidence=confidence
                    )
                    
                    transitions.append(transition)
            
            # Sort by probability
            transitions.sort(key=lambda x: x.transition_probability, reverse=True)
            
            logger.info(f"✅ Predicted {len(transitions)} potential transitions")
            
            return transitions
            
        except Exception as e:
            logger.error(f"❌ Error predicting transitions: {e}")
            return []
    
    def analyze_regime_stability(self, data: List[float], 
                               window_size: int = 10) -> Dict[str, float]:
        """
        📊 Analyze Regime Stability
        
        Analyzes how stable the current regime is over different time windows
        """
        try:
            if len(data) < window_size:
                return {"stability": 0.0, "consistency": 0.0, "persistence": 0.0}
            
            # Analyze regime consistency over different windows
            windows = [window_size // 2, window_size, window_size * 2]
            regime_consistency = []
            
            for window in windows:
                if len(data) >= window:
                    window_data = data[-window:]
                    regime = self.detect_current_regime(window_data)
                    regime_consistency.append(regime.confidence)
            
            # Calculate stability metrics
            consistency = np.mean(regime_consistency) if regime_consistency else 0.0
            stability = 1.0 - np.std(regime_consistency) if len(regime_consistency) > 1 else consistency
            
            # Calculate persistence (how long regime has lasted)
            persistence = min(1.0, self.current_regime.duration / 30.0) if self.current_regime else 0.0
            
            stability_analysis = {
                "stability": float(stability),
                "consistency": float(consistency), 
                "persistence": float(persistence),
                "regime_age": self.current_regime.duration if self.current_regime else 0
            }
            
            logger.info(f"📊 Stability analysis: {stability_analysis}")
            
            return stability_analysis
            
        except Exception as e:
            logger.error(f"❌ Error analyzing stability: {e}")
            return {"stability": 0.0, "consistency": 0.0, "persistence": 0.0}
    
    def get_regime_insights(self) -> Dict[str, Any]:
        """Get comprehensive regime insights"""
        try:
            insights = {
                "current_regime": None,
                "regime_history_summary": {},
                "transition_probabilities": {},
                "stability_metrics": {},
                "regime_characteristics": {}
            }
            
            if self.current_regime:
                insights["current_regime"] = {
                    "type": self.current_regime.regime_type.value,
                    "confidence": self.current_regime.confidence,
                    "duration": self.current_regime.duration,
                    "stability": self.current_regime.stability_score
                }
            
            # Regime history summary
            if self.regime_history:
                regime_counts = {}
                for regime_state in self.regime_history[-50:]:  # Last 50 states
                    regime_type = regime_state.regime_type.value
                    regime_counts[regime_type] = regime_counts.get(regime_type, 0) + 1
                
                total_count = sum(regime_counts.values())
                insights["regime_history_summary"] = {
                    regime: count / total_count 
                    for regime, count in regime_counts.items()
                }
            
            # Transition matrix insights
            insights["transition_probabilities"] = self._get_transition_insights()
            
            return insights
            
        except Exception as e:
            logger.error(f"❌ Error getting regime insights: {e}")
            return {}
    
    # =================== PRIVATE METHODS ===================
    
    def _extract_regime_features(self, data: List[float]) -> RegimeFeatures:
        """Extract statistical features for regime detection"""
        try:
            data_array = np.array(data)
            
            # Calculate returns
            returns = np.diff(data_array) / data_array[:-1]
            returns = returns[~np.isnan(returns)]  # Remove NaN values
            
            if len(returns) == 0:
                return self._create_default_features()
            
            # Volatility (standard deviation of returns)
            volatility = float(np.std(returns))
            
            # Trend strength (correlation with time)
            time_index = np.arange(len(data_array))
            trend_strength = float(abs(np.corrcoef(data_array, time_index)[0, 1]))
            if np.isnan(trend_strength):
                trend_strength = 0.0
            
            # Momentum (recent vs older returns)
            if len(returns) > 10:
                recent_momentum = np.mean(returns[-5:])
                older_momentum = np.mean(returns[-15:-10])
                momentum = float(recent_momentum - older_momentum)
            else:
                momentum = 0.0
            
            # Autocorrelation
            if len(returns) > 1:
                autocorr = float(np.corrcoef(returns[:-1], returns[1:])[0, 1])
                if np.isnan(autocorr):
                    autocorr = 0.0
            else:
                autocorr = 0.0
            
            # Volatility of volatility
            if len(returns) > 10:
                rolling_vol = []
                window = 5
                for i in range(window, len(returns)):
                    vol = np.std(returns[i-window:i])
                    rolling_vol.append(vol)
                vol_of_vol = float(np.std(rolling_vol)) if rolling_vol else 0.0
            else:
                vol_of_vol = 0.0
            
            # Skewness and Kurtosis
            if len(returns) > 3:
                skewness = float(self._calculate_skewness(returns))
                kurtosis = float(self._calculate_kurtosis(returns))
            else:
                skewness = 0.0
                kurtosis = 0.0
            
            # Hurst exponent (simplified calculation)
            hurst = self._calculate_hurst_exponent(data_array) if len(data_array) > 20 else None
            
            features = RegimeFeatures(
                volatility=volatility,
                trend_strength=trend_strength,
                momentum=momentum,
                autocorrelation=autocorr,
                volatility_of_volatility=vol_of_vol,
                skewness=skewness,
                kurtosis=kurtosis,
                hurst_exponent=hurst
            )
            
            return features
            
        except Exception as e:
            logger.error(f"❌ Error extracting features: {e}")
            return self._create_default_features()
    
    def _calculate_regime_probabilities(self, features: RegimeFeatures) -> Dict[RegimeType, float]:
        """Calculate probability of each regime given features"""
        try:
            probabilities = {}
            
            # STABLE regime: Low volatility, low momentum
            stable_score = (
                (1.0 - min(1.0, features.volatility / 0.05)) * 0.4 +
                (1.0 - min(1.0, abs(features.momentum) / 0.02)) * 0.3 +
                (1.0 - min(1.0, features.volatility_of_volatility / 0.01)) * 0.3
            )
            probabilities[RegimeType.STABLE] = stable_score
            
            # VOLATILE regime: High volatility, high vol-of-vol
            volatile_score = (
                min(1.0, features.volatility / 0.03) * 0.5 +
                min(1.0, features.volatility_of_volatility / 0.01) * 0.3 +
                min(1.0, abs(features.kurtosis) / 2.0) * 0.2
            )
            probabilities[RegimeType.VOLATILE] = volatile_score
            
            # TRENDING_UP regime: Positive momentum, high trend strength
            trending_up_score = (
                max(0.0, features.momentum / 0.02) * 0.4 +
                features.trend_strength * 0.4 +
                max(0.0, -features.autocorrelation) * 0.2  # Negative autocorr in trends
            )
            probabilities[RegimeType.TRENDING_UP] = min(1.0, trending_up_score)
            
            # TRENDING_DOWN regime: Negative momentum, high trend strength
            trending_down_score = (
                max(0.0, -features.momentum / 0.02) * 0.4 +
                features.trend_strength * 0.4 +
                max(0.0, -features.autocorrelation) * 0.2
            )
            probabilities[RegimeType.TRENDING_DOWN] = min(1.0, trending_down_score)
            
            # SIDEWAYS regime: Low trend strength, high autocorrelation
            sideways_score = (
                (1.0 - features.trend_strength) * 0.5 +
                max(0.0, features.autocorrelation) * 0.3 +
                (1.0 - min(1.0, abs(features.momentum) / 0.01)) * 0.2
            )
            probabilities[RegimeType.SIDEWAYS] = sideways_score
            
            # BREAKOUT regime: High volatility, high momentum, low autocorr
            breakout_score = (
                min(1.0, features.volatility / 0.04) * 0.4 +
                min(1.0, abs(features.momentum) / 0.03) * 0.4 +
                max(0.0, -features.autocorrelation) * 0.2
            )
            probabilities[RegimeType.BREAKOUT] = breakout_score
            
            # REVERSAL regime: High skewness, high kurtosis
            reversal_score = (
                min(1.0, abs(features.skewness) / 1.0) * 0.5 +
                min(1.0, abs(features.kurtosis) / 3.0) * 0.3 +
                min(1.0, features.volatility_of_volatility / 0.02) * 0.2
            )
            probabilities[RegimeType.REVERSAL] = reversal_score
            
            # Normalize probabilities
            total_prob = sum(probabilities.values())
            if total_prob > 0:
                probabilities = {
                    regime: prob / total_prob 
                    for regime, prob in probabilities.items()
                }
            else:
                # Default uniform distribution
                probabilities = {regime: 1.0 / len(RegimeType) for regime in RegimeType}
            
            return probabilities
            
        except Exception as e:
            logger.error(f"❌ Error calculating regime probabilities: {e}")
            return {regime: 1.0 / len(RegimeType) for regime in RegimeType}
    
    def _calculate_stability_score(self, probabilities: Dict[RegimeType, float]) -> float:
        """Calculate regime stability score"""
        try:
            # Entropy-based stability (lower entropy = more stable)
            entropy = -sum(p * np.log(p + 1e-10) for p in probabilities.values())
            max_entropy = np.log(len(probabilities))
            
            # Stability is inverse of normalized entropy
            stability = 1.0 - (entropy / max_entropy)
            
            return float(stability)
            
        except Exception as e:
            logger.error(f"❌ Error calculating stability: {e}")
            return 0.0
    
    def _calculate_regime_duration(self, regime_type: RegimeType) -> int:
        """Calculate how long we've been in current regime"""
        try:
            if not self.regime_history:
                return 1
            
            duration = 1
            for i in range(len(self.regime_history) - 1, -1, -1):
                if self.regime_history[i].regime_type == regime_type:
                    duration += 1
                else:
                    break
            
            return duration
            
        except Exception as e:
            logger.error(f"❌ Error calculating duration: {e}")
            return 1
    
    def _calculate_transition_probability(self, from_regime: RegimeType, 
                                       to_regime: RegimeType, 
                                       features: RegimeFeatures) -> float:
        """Calculate transition probability between regimes"""
        try:
            # Base transition probability from historical data
            base_prob = self.transition_matrix.get(from_regime, {}).get(to_regime, 0.1)
            
            # Feature-based adjustment
            feature_adjustment = self._get_feature_transition_adjustment(
                from_regime, to_regime, features
            )
            
            # Final probability
            final_prob = base_prob * feature_adjustment
            
            return min(1.0, max(0.0, final_prob))
            
        except Exception as e:
            logger.error(f"❌ Error calculating transition probability: {e}")
            return 0.1
    
    def _get_feature_transition_adjustment(self, from_regime: RegimeType, 
                                         to_regime: RegimeType, 
                                         features: RegimeFeatures) -> float:
        """Get feature-based adjustment for transition probability"""
        try:
            # High volatility makes breakout/volatile regimes more likely
            if features.volatility > 0.03:
                if to_regime in [RegimeType.BREAKOUT, RegimeType.VOLATILE]:
                    return 1.5
                elif to_regime == RegimeType.STABLE:
                    return 0.5
            
            # Strong trend makes trending regimes more likely
            if features.trend_strength > 0.7:
                if to_regime in [RegimeType.TRENDING_UP, RegimeType.TRENDING_DOWN]:
                    return 1.3
                elif to_regime == RegimeType.SIDEWAYS:
                    return 0.7
            
            # High momentum suggests continuation or reversal
            if abs(features.momentum) > 0.02:
                if to_regime == RegimeType.REVERSAL and from_regime in [RegimeType.TRENDING_UP, RegimeType.TRENDING_DOWN]:
                    return 1.2
            
            return 1.0
            
        except Exception as e:
            logger.error(f"❌ Error getting feature adjustment: {e}")
            return 1.0
    
    def _estimate_regime_duration(self, regime_type: RegimeType) -> int:
        """Estimate expected duration of regime"""
        # Typical durations based on regime characteristics
        duration_map = {
            RegimeType.STABLE: 20,
            RegimeType.VOLATILE: 10,
            RegimeType.TRENDING_UP: 15,
            RegimeType.TRENDING_DOWN: 12,
            RegimeType.SIDEWAYS: 25,
            RegimeType.BREAKOUT: 5,
            RegimeType.REVERSAL: 3,
            RegimeType.UNKNOWN: 7
        }
        
        return duration_map.get(regime_type, 10)
    
    def _identify_trigger_conditions(self, from_regime: RegimeType, 
                                   to_regime: RegimeType, 
                                   features: RegimeFeatures) -> List[str]:
        """Identify conditions that would trigger regime transition"""
        triggers = []
        
        # Volatility-based triggers
        if features.volatility < 0.02:
            triggers.append("Low volatility environment")
        elif features.volatility > 0.04:
            triggers.append("High volatility spike")
        
        # Momentum-based triggers
        if abs(features.momentum) > 0.02:
            triggers.append("Strong momentum shift")
        
        # Trend-based triggers
        if features.trend_strength > 0.7:
            triggers.append("Strong trend development")
        elif features.trend_strength < 0.3:
            triggers.append("Trend breakdown")
        
        # Mean reversion triggers
        if features.autocorrelation > 0.5:
            triggers.append("Mean reversion pattern")
        
        return triggers
    
    def _update_regime_history(self, regime_state: RegimeState):
        """Update regime history"""
        self.regime_history.append(regime_state)
        self.current_regime = regime_state
        
        # Keep limited history
        if len(self.regime_history) > 1000:
            self.regime_history = self.regime_history[-500:]
    
    def _create_unknown_regime(self) -> RegimeState:
        """Create unknown regime state for error cases"""
        return RegimeState(
            regime_type=RegimeType.UNKNOWN,
            confidence=0.0,
            features=self._create_default_features(),
            probability_distribution={RegimeType.UNKNOWN: 1.0},
            duration=0,
            stability_score=0.0
        )
    
    def _create_default_features(self) -> RegimeFeatures:
        """Create default features for error cases"""
        return RegimeFeatures(
            volatility=0.0,
            trend_strength=0.0,
            momentum=0.0,
            autocorrelation=0.0,
            volatility_of_volatility=0.0,
            skewness=0.0,
            kurtosis=0.0
        )
    
    def _initialize_transition_matrix(self) -> Dict[RegimeType, Dict[RegimeType, float]]:
        """Initialize transition probability matrix"""
        # Simplified transition matrix based on market behavior
        return {
            RegimeType.STABLE: {
                RegimeType.STABLE: 0.7,
                RegimeType.VOLATILE: 0.1,
                RegimeType.TRENDING_UP: 0.08,
                RegimeType.TRENDING_DOWN: 0.07,
                RegimeType.SIDEWAYS: 0.05
            },
            RegimeType.VOLATILE: {
                RegimeType.VOLATILE: 0.4,
                RegimeType.BREAKOUT: 0.2,
                RegimeType.REVERSAL: 0.15,
                RegimeType.STABLE: 0.15,
                RegimeType.SIDEWAYS: 0.1
            },
            RegimeType.TRENDING_UP: {
                RegimeType.TRENDING_UP: 0.6,
                RegimeType.REVERSAL: 0.15,
                RegimeType.SIDEWAYS: 0.1,
                RegimeType.VOLATILE: 0.1,
                RegimeType.STABLE: 0.05
            },
            RegimeType.TRENDING_DOWN: {
                RegimeType.TRENDING_DOWN: 0.6,
                RegimeType.REVERSAL: 0.15,
                RegimeType.SIDEWAYS: 0.1,
                RegimeType.VOLATILE: 0.1,
                RegimeType.STABLE: 0.05
            },
            RegimeType.SIDEWAYS: {
                RegimeType.SIDEWAYS: 0.5,
                RegimeType.BREAKOUT: 0.2,
                RegimeType.TRENDING_UP: 0.1,
                RegimeType.TRENDING_DOWN: 0.1,
                RegimeType.STABLE: 0.1
            },
            RegimeType.BREAKOUT: {
                RegimeType.TRENDING_UP: 0.3,
                RegimeType.TRENDING_DOWN: 0.25,
                RegimeType.VOLATILE: 0.2,
                RegimeType.REVERSAL: 0.15,
                RegimeType.SIDEWAYS: 0.1
            },
            RegimeType.REVERSAL: {
                RegimeType.TRENDING_UP: 0.25,
                RegimeType.TRENDING_DOWN: 0.25,
                RegimeType.SIDEWAYS: 0.2,
                RegimeType.VOLATILE: 0.15,
                RegimeType.STABLE: 0.15
            }
        }
    
    def _initialize_thresholds(self) -> Dict[str, float]:
        """Initialize regime detection thresholds"""
        return {
            'volatility_low': 0.02,
            'volatility_high': 0.04,
            'trend_strong': 0.7,
            'trend_weak': 0.3,
            'momentum_high': 0.02,
            'autocorr_high': 0.5
        }
    
    def _get_transition_insights(self) -> Dict[str, Any]:
        """Get insights from transition matrix"""
        insights = {}
        
        for from_regime in self.transition_matrix:
            regime_transitions = self.transition_matrix[from_regime]
            most_likely = max(regime_transitions.items(), key=lambda x: x[1])
            
            insights[from_regime.value] = {
                'most_likely_next': most_likely[0].value,
                'transition_probability': most_likely[1],
                'stability': regime_transitions.get(from_regime, 0.0)
            }
        
        return insights
    
    def _calculate_skewness(self, data: np.ndarray) -> float:
        """Calculate skewness"""
        try:
            n = len(data)
            if n < 3:
                return 0.0
            
            mean = np.mean(data)
            std = np.std(data)
            
            if std == 0:
                return 0.0
            
            skew = np.sum(((data - mean) / std) ** 3) / n
            return skew
            
        except Exception:
            return 0.0
    
    def _calculate_kurtosis(self, data: np.ndarray) -> float:
        """Calculate kurtosis"""
        try:
            n = len(data)
            if n < 4:
                return 0.0
            
            mean = np.mean(data)
            std = np.std(data)
            
            if std == 0:
                return 0.0
            
            kurt = np.sum(((data - mean) / std) ** 4) / n - 3  # Excess kurtosis
            return kurt
            
        except Exception:
            return 0.0
    
    def _calculate_hurst_exponent(self, data: np.ndarray) -> Optional[float]:
        """Calculate Hurst exponent (simplified R/S analysis)"""
        try:
            n = len(data)
            if n < 20:
                return None
            
            # Calculate returns
            returns = np.diff(data) / data[:-1]
            returns = returns[~np.isnan(returns)]
            
            if len(returns) < 10:
                return None
            
            # R/S analysis for different time scales
            scales = [5, 10, 15]
            rs_values = []
            
            for scale in scales:
                if len(returns) >= scale:
                    # Calculate R/S for this scale
                    segments = len(returns) // scale
                    rs_segment = []
                    
                    for i in range(segments):
                        segment = returns[i*scale:(i+1)*scale]
                        
                        # Cumulative sum
                        cumsum = np.cumsum(segment - np.mean(segment))
                        
                        # Range
                        R = np.max(cumsum) - np.min(cumsum)
                        
                        # Standard deviation
                        S = np.std(segment)
                        
                        if S > 0:
                            rs_segment.append(R / S)
                    
                    if rs_segment:
                        rs_values.append((scale, np.mean(rs_segment)))
            
            if len(rs_values) < 2:
                return None
            
            # Linear regression to find Hurst exponent
            scales_log = [np.log(scale) for scale, _ in rs_values]
            rs_log = [np.log(rs) for _, rs in rs_values if rs > 0]
            
            if len(scales_log) == len(rs_log) and len(rs_log) > 1:
                hurst = np.polyfit(scales_log, rs_log, 1)[0]
                return float(np.clip(hurst, 0.0, 1.0))
            
            return None
            
        except Exception:
            return None

# =================== DEMONSTRATION FUNCTIONS ===================

def demo_regime_detection_lite():
    """Demonstrate Regime Detection Service Lite capabilities"""
    print("🎯 REGIME DETECTION SERVICE LITE - DEMONSTRATION")
    print("=" * 55)
    
    # Initialize service
    regime_service = RegimeDetectionServiceLite(lookback_window=30)
    
    # Generate sample data for different regimes
    print("\n📊 Testing Different Market Scenarios:")
    
    # 1. Stable market data
    np.random.seed(42)
    stable_data = 100 + np.cumsum(np.random.normal(0, 0.5, 50))
    stable_regime = regime_service.detect_current_regime(stable_data.tolist())
    print(f"\n1. Stable Market:")
    print(f"   Detected: {stable_regime.regime_type.value}")
    print(f"   Confidence: {stable_regime.confidence:.3f}")
    print(f"   Volatility: {stable_regime.features.volatility:.4f}")
    
    # 2. Volatile market data
    volatile_data = 100 + np.cumsum(np.random.normal(0, 2.0, 50))
    volatile_regime = regime_service.detect_current_regime(volatile_data.tolist())
    print(f"\n2. Volatile Market:")
    print(f"   Detected: {volatile_regime.regime_type.value}")
    print(f"   Confidence: {volatile_regime.confidence:.3f}")
    print(f"   Volatility: {volatile_regime.features.volatility:.4f}")
    
    # 3. Trending market data
    trend_data = 100 + np.cumsum(np.random.normal(0.5, 1.0, 50))  # Upward trend
    trend_regime = regime_service.detect_current_regime(trend_data.tolist())
    print(f"\n3. Trending Market:")
    print(f"   Detected: {trend_regime.regime_type.value}")
    print(f"   Confidence: {trend_regime.confidence:.3f}")
    print(f"   Trend Strength: {trend_regime.features.trend_strength:.3f}")
    print(f"   Momentum: {trend_regime.features.momentum:.4f}")
    
    # Test regime transition prediction
    print(f"\n🔮 REGIME TRANSITION PREDICTIONS:")
    transitions = regime_service.predict_regime_transition(trend_regime)
    
    for i, transition in enumerate(transitions[:3], 1):
        print(f"\n{i}. {transition.from_regime.value} → {transition.to_regime.value}")
        print(f"   Probability: {transition.transition_probability:.3f}")
        print(f"   Expected Duration: {transition.expected_duration} days")
        print(f"   Triggers: {', '.join(transition.trigger_conditions[:2])}")
    
    # Stability analysis
    print(f"\n📈 STABILITY ANALYSIS:")
    stability = regime_service.analyze_regime_stability(trend_data.tolist())
    for metric, value in stability.items():
        print(f"   {metric.title()}: {value:.3f}")
    
    # Regime insights
    print(f"\n🔍 REGIME INSIGHTS:")
    insights = regime_service.get_regime_insights()
    if insights.get("current_regime"):
        current = insights["current_regime"]
        print(f"   Current: {current['type']} (duration: {current['duration']} days)")
        print(f"   Stability: {current['stability']:.3f}")
    
    print(f"\n✅ Regime Detection Service Lite demonstration completed!")

if __name__ == "__main__":
    demo_regime_detection_lite()
