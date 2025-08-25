"""
🚀 PHASE 1.3: ADVANCED NUMBER FUSION SYSTEM
Sophisticated prediction fusion with uncertainty quantification and confidence intervals
"""

import logging
import warnings
from collections import Counter, defaultdict
from typing import Dict, List, Optional, Tuple

import numpy as np
from scipy.stats import norm
from sklearn.ensemble import VotingRegressor

logger = logging.getLogger(__name__)

warnings.filterwarnings("ignore")


class AdvancedNumberFusion:
    """
    🚀 Advanced fusion system for combining multiple prediction sources
    """

    def __init__(self):
        self.fusion_methods = {
            "weighted_voting": self._weighted_voting,
            "stacking": self._stacking_fusion,
            "bayesian_fusion": self._bayesian_fusion,
            "confidence_weighted": self._confidence_weighted_fusion,
        }
        self.history = []

    def fuse_predictions_with_uncertainty(
        self,
        method_numbers: List[str],
        cyclical_numbers: List[str],
        historical_features: Optional[Dict] = None,
        deep_frequency_insights: Optional[Dict] = None,
        fusion_method: str = "confidence_weighted",
    ) -> Dict:
        """
        🚀 MAIN FUSION: Combine predictions with uncertainty quantification
        """
        try:
            logger.info(f"🔄 Starting advanced fusion: {fusion_method}")
            logger.info(
                f"📊 Input: {len(method_numbers)} method numbers, {len(cyclical_numbers)} cyclical numbers"
            )

            # Prepare fusion inputs
            fusion_inputs = {
                "method_numbers": method_numbers,
                "cyclical_numbers": cyclical_numbers,
                "historical_features": historical_features or {},
                "frequency_insights": deep_frequency_insights or {},
            }

            # Select and apply fusion method
            fusion_func = self.fusion_methods.get(
                fusion_method, self._confidence_weighted_fusion
            )
            fusion_results = fusion_func(fusion_inputs)

            # Calculate uncertainty metrics
            uncertainty_metrics = self._calculate_uncertainty_metrics(
                fusion_results, fusion_inputs
            )

            # Generate confidence intervals
            confidence_intervals = self._calculate_confidence_intervals(
                fusion_results, uncertainty_metrics
            )

            # Final result compilation
            final_result = {
                "fused_numbers": fusion_results.get("numbers", [])[:15],
                "fusion_scores": fusion_results.get("scores", {}),
                "uncertainty_metrics": uncertainty_metrics,
                "confidence_intervals": confidence_intervals,
                "fusion_metadata": {
                    "method_used": fusion_method,
                    "input_sources": len(fusion_inputs),
                    "total_candidates": len(set(method_numbers + cyclical_numbers)),
                    "fusion_timestamp": np.datetime64("now").astype(str),
                },
            }

            logger.info(
                f"✅ Fusion completed: {len(final_result['fused_numbers'])} numbers with uncertainty"
            )
            return final_result

        except Exception as e:
            logger.error(f"❌ Advanced fusion failed: {e}")
            return self._get_fallback_fusion(method_numbers, cyclical_numbers)

    def _confidence_weighted_fusion(self, fusion_inputs: Dict) -> Dict:
        """
        🚀 ENHANCED: Confidence-weighted fusion with statistical validation
        """
        method_numbers = fusion_inputs["method_numbers"]
        cyclical_numbers = fusion_inputs["cyclical_numbers"]
        historical_features = fusion_inputs["historical_features"]
        frequency_insights = fusion_inputs["frequency_insights"]

        final_scores = defaultdict(float)
        confidence_scores = defaultdict(float)

        # 🚀 DYNAMIC WEIGHTS based on historical performance
        method_confidence = historical_features.get("weekly_consistency", 0.5)
        cyclical_confidence = historical_features.get("cyclical_strength", 0.5)

        # Normalize weights
        total_confidence = method_confidence + cyclical_confidence
        if total_confidence > 0:
            method_weight = method_confidence / total_confidence
            cyclical_weight = cyclical_confidence / total_confidence
        else:
            method_weight = 0.6  # Default fallback
            cyclical_weight = 0.4

        # 🚀 FREQUENCY INTELLIGENCE INTEGRATION
        hot_numbers = frequency_insights.get("hot_numbers", {})
        momentum_patterns = frequency_insights.get("momentum_patterns", {})
        mean_reversion = frequency_insights.get("mean_reversion", {})

        # Process method predictions
        for i, number in enumerate(method_numbers[:20]):
            position_weight = (20 - i) / 20.0
            base_score = position_weight * method_weight * 100

            # 🚀 FREQUENCY INTELLIGENCE BOOST
            frequency_multiplier = 1.0

            # Hot number boost
            if number in hot_numbers:
                hot_ratio = hot_numbers[number].get("ratio", 1.0)
                frequency_multiplier *= 1.0 + min(hot_ratio - 1.0, 0.5)  # Max 50% boost

            # Momentum boost
            if number in momentum_patterns:
                if momentum_patterns[number].get("trend") == "increasing":
                    avg_momentum = momentum_patterns[number].get("average_momentum", 0)
                    frequency_multiplier *= 1.0 + min(
                        avg_momentum, 0.3
                    )  # Max 30% boost

            # Mean reversion consideration
            if number in mean_reversion:
                reversion_pressure = mean_reversion[number].get("reversion_pressure", 0)
                if mean_reversion[number].get("expected_direction") == "increase":
                    frequency_multiplier *= 1.0 + min(
                        reversion_pressure, 0.2
                    )  # Max 20% boost

            final_score = base_score * frequency_multiplier
            final_scores[number] += final_score
            confidence_scores[number] += method_weight * frequency_multiplier

        # Process cyclical predictions
        for i, number in enumerate(cyclical_numbers[:20]):
            position_weight = (20 - i) / 20.0
            base_score = position_weight * cyclical_weight * 100

            # Apply same frequency intelligence
            frequency_multiplier = 1.0

            if number in hot_numbers:
                hot_ratio = hot_numbers[number].get("ratio", 1.0)
                frequency_multiplier *= 1.0 + min(
                    hot_ratio - 1.0, 0.4
                )  # Slightly less for cyclical

            final_score = base_score * frequency_multiplier
            final_scores[number] += final_score
            confidence_scores[number] += cyclical_weight * frequency_multiplier

        # 🚀 CONSENSUS BONUS: Numbers appearing in both sources
        overlap_numbers = set(method_numbers[:10]) & set(cyclical_numbers[:10])
        for number in overlap_numbers:
            final_scores[number] *= 1.3  # 30% consensus bonus
            confidence_scores[number] *= 1.2  # Confidence boost

        # Sort and return results
        sorted_results = sorted(final_scores.items(), key=lambda x: x[1], reverse=True)

        return {
            "numbers": [num for num, score in sorted_results],
            "scores": dict(final_scores),
            "confidence_scores": dict(confidence_scores),
            "weights_used": {"method": method_weight, "cyclical": cyclical_weight},
            "overlap_count": len(overlap_numbers),
        }

    def _bayesian_fusion(self, fusion_inputs: Dict) -> Dict:
        """
        🚀 ADVANCED: Bayesian inference for prediction fusion
        """
        try:
            method_numbers = fusion_inputs["method_numbers"]
            cyclical_numbers = fusion_inputs["cyclical_numbers"]

            # Calculate prior probabilities (uniform for now)
            all_numbers = list(set(method_numbers + cyclical_numbers))
            prior_prob = 1.0 / len(all_numbers) if all_numbers else 0

            bayesian_scores = {}

            for number in all_numbers:
                # Calculate likelihood based on multiple sources
                method_likelihood = (method_numbers.count(number) + 1) / (
                    len(method_numbers) + 2
                )
                cyclical_likelihood = (cyclical_numbers.count(number) + 1) / (
                    len(cyclical_numbers) + 2
                )

                # Combine likelihoods
                combined_likelihood = method_likelihood * cyclical_likelihood

                # Bayesian posterior
                posterior = prior_prob * combined_likelihood
                bayesian_scores[number] = posterior

            # Normalize probabilities
            total_prob = sum(bayesian_scores.values())
            if total_prob > 0:
                normalized_scores = {
                    k: v / total_prob for k, v in bayesian_scores.items()
                }
            else:
                normalized_scores = bayesian_scores

            sorted_results = sorted(
                normalized_scores.items(), key=lambda x: x[1], reverse=True
            )

            return {
                "numbers": [num for num, score in sorted_results],
                "scores": normalized_scores,
                "method": "bayesian_inference",
            }

        except Exception as e:
            logger.warning(
                f"Bayesian fusion failed: {e}, falling back to weighted voting"
            )
            return self._weighted_voting(fusion_inputs)

    def _weighted_voting(self, fusion_inputs: Dict) -> Dict:
        """Traditional weighted voting fusion"""
        method_numbers = fusion_inputs["method_numbers"]
        cyclical_numbers = fusion_inputs["cyclical_numbers"]

        vote_counts = defaultdict(float)

        # Method votes (weight: 0.6)
        for i, number in enumerate(method_numbers):
            vote_counts[number] += 0.6 * (len(method_numbers) - i) / len(method_numbers)

        # Cyclical votes (weight: 0.4)
        for i, number in enumerate(cyclical_numbers):
            vote_counts[number] += (
                0.4 * (len(cyclical_numbers) - i) / len(cyclical_numbers)
            )

        sorted_results = sorted(vote_counts.items(), key=lambda x: x[1], reverse=True)

        return {
            "numbers": [num for num, score in sorted_results],
            "scores": dict(vote_counts),
            "method": "weighted_voting",
        }

    def _stacking_fusion(self, fusion_inputs: Dict) -> Dict:
        """Placeholder for stacking fusion (would need trained meta-model)"""
        logger.info("🔄 Stacking fusion not fully implemented, using weighted voting")
        return self._weighted_voting(fusion_inputs)

    def _calculate_uncertainty_metrics(
        self, fusion_results: Dict, fusion_inputs: Dict
    ) -> Dict:
        """
        🚀 UNCERTAINTY QUANTIFICATION: Calculate prediction uncertainty
        """
        try:
            scores = fusion_results.get("scores", {})

            if not scores:
                return {"error": "No scores available for uncertainty calculation"}

            score_values = list(scores.values())

            # Statistical uncertainty metrics
            uncertainty_metrics = {
                "score_variance": float(np.var(score_values)),
                "score_std": float(np.std(score_values)),
                "score_range": float(max(score_values) - min(score_values)),
                "coefficient_of_variation": (
                    float(np.std(score_values) / np.mean(score_values))
                    if np.mean(score_values) > 0
                    else 0
                ),
                "entropy": self._calculate_entropy(score_values),
                "prediction_spread": len(scores),
                "top_score_dominance": (
                    float(max(score_values) / sum(score_values))
                    if sum(score_values) > 0
                    else 0
                ),
            }

            # Uncertainty level classification
            cv = uncertainty_metrics["coefficient_of_variation"]
            if cv < 0.2:
                uncertainty_level = "low"
            elif cv < 0.5:
                uncertainty_level = "medium"
            else:
                uncertainty_level = "high"

            uncertainty_metrics["uncertainty_level"] = uncertainty_level

            return uncertainty_metrics

        except Exception as e:
            logger.warning(f"Uncertainty calculation failed: {e}")
            return {"error": str(e), "uncertainty_level": "unknown"}

    def _calculate_confidence_intervals(
        self, fusion_results: Dict, uncertainty_metrics: Dict
    ) -> Dict:
        """
        🚀 CONFIDENCE INTERVALS: Bootstrap-style confidence intervals
        """
        try:
            scores = fusion_results.get("scores", {})

            if not scores:
                return {}

            confidence_intervals = {}
            score_std = uncertainty_metrics.get("score_std", 0)

            # Calculate confidence intervals for top numbers
            for number, score in list(scores.items())[:15]:
                # Simple normal approximation (could be enhanced with bootstrap)
                ci_95_lower = max(0, score - 1.96 * score_std)
                ci_95_upper = score + 1.96 * score_std
                ci_99_lower = max(0, score - 2.58 * score_std)
                ci_99_upper = score + 2.58 * score_std

                confidence_intervals[number] = {
                    "point_estimate": float(score),
                    "ci_95": {"lower": float(ci_95_lower), "upper": float(ci_95_upper)},
                    "ci_99": {"lower": float(ci_99_lower), "upper": float(ci_99_upper)},
                    "confidence_width_95": float(ci_95_upper - ci_95_lower),
                    "confidence_width_99": float(ci_99_upper - ci_99_lower),
                }

            return confidence_intervals

        except Exception as e:
            logger.warning(f"Confidence interval calculation failed: {e}")
            return {}

    def _calculate_entropy(self, values: List[float]) -> float:
        """Calculate Shannon entropy of score distribution"""
        try:
            if not values or sum(values) == 0:
                return 0.0

            # Normalize to probabilities
            total = sum(values)
            probabilities = [v / total for v in values if v > 0]

            # Calculate entropy
            entropy = -sum(p * np.log2(p) for p in probabilities if p > 0)
            return float(entropy)

        except Exception:
            return 0.0

    def _get_fallback_fusion(
        self, method_numbers: List[str], cyclical_numbers: List[str]
    ) -> Dict:
        """Fallback fusion when advanced methods fail"""
        combined = list(set(method_numbers[:10] + cyclical_numbers[:10]))

        return {
            "fused_numbers": combined[:15],
            "fusion_scores": {num: 1.0 for num in combined[:15]},
            "uncertainty_metrics": {
                "uncertainty_level": "high",
                "error": "fallback_mode",
            },
            "confidence_intervals": {},
            "fusion_metadata": {
                "method_used": "fallback",
                "error": "advanced_fusion_failed",
            },
        }


def perform_advanced_fusion(
    method_numbers: List[str],
    cyclical_numbers: List[str],
    historical_features: Optional[Dict] = None,
    deep_frequency_insights: Optional[Dict] = None,
    fusion_method: str = "confidence_weighted",
) -> Dict:
    """
    🚀 PUBLIC API: Advanced number fusion with uncertainty quantification
    """
    fusion_engine = AdvancedNumberFusion()
    return fusion_engine.fuse_predictions_with_uncertainty(
        method_numbers=method_numbers,
        cyclical_numbers=cyclical_numbers,
        historical_features=historical_features,
        deep_frequency_insights=deep_frequency_insights,
        fusion_method=fusion_method,
    )
