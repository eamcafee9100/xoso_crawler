"""
Confidence Interval System for Lottery Predictions
Provides uncertainty quantification and reliability scoring
"""

import logging
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple

import numpy as np
import pandas as pd
from scipy import stats


@dataclass
class ConfidenceMetrics:
    """Confidence metrics for predictions"""

    point_estimate: float
    confidence_interval: Tuple[float, float]
    confidence_level: float
    prediction_interval: Tuple[float, float]
    reliability_score: float
    uncertainty_level: str


@dataclass
class PredictionConfidence:
    """Comprehensive prediction confidence assessment"""

    predicted_numbers: List[int]
    individual_confidences: Dict[int, float]
    overall_confidence: float
    confidence_metrics: ConfidenceMetrics
    risk_assessment: str
    recommendation: str


class ConfidenceCalculator:
    """
    Advanced confidence calculation system for lottery predictions
    """

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.historical_accuracy = {}  # Cache for method accuracy history

    def calculate_prediction_confidence(
        self,
        predicted_numbers: List[int],
        historical_data: List,
        method_name: str,
        confidence_level: float = 0.95,
    ) -> PredictionConfidence:
        """
        Calculate comprehensive confidence metrics for predictions

        Args:
            predicted_numbers: List of predicted numbers
            historical_data: Historical lottery results
            method_name: Name of prediction method
            confidence_level: Statistical confidence level

        Returns:
            PredictionConfidence with detailed metrics
        """

        # Calculate individual number confidences
        individual_confidences = self._calculate_individual_confidences(
            predicted_numbers, historical_data
        )

        # Calculate overall confidence
        overall_confidence = self._calculate_overall_confidence(
            predicted_numbers, historical_data, method_name
        )

        # Generate confidence metrics
        confidence_metrics = self._generate_confidence_metrics(
            predicted_numbers, historical_data, confidence_level
        )

        # Risk assessment
        risk_assessment = self._assess_prediction_risk(
            overall_confidence, confidence_metrics
        )

        # Generate recommendation
        recommendation = self._generate_recommendation(
            overall_confidence, confidence_metrics, risk_assessment
        )

        return PredictionConfidence(
            predicted_numbers=predicted_numbers,
            individual_confidences=individual_confidences,
            overall_confidence=overall_confidence,
            confidence_metrics=confidence_metrics,
            risk_assessment=risk_assessment,
            recommendation=recommendation,
        )

    def _calculate_individual_confidences(
        self, predicted_numbers: List[int], historical_data: List
    ) -> Dict[int, float]:
        """Calculate confidence for each predicted number"""
        confidences = {}

        for number in predicted_numbers:
            # Historical frequency
            frequency = self._calculate_number_frequency(number, historical_data)

            # Recent trend
            recent_trend = self._calculate_recent_trend(number, historical_data[:30])

            # Cycle consistency
            cycle_consistency = self._calculate_cycle_consistency(
                number, historical_data
            )

            # Gap analysis
            gap_score = self._calculate_gap_score(number, historical_data)

            # Combine factors with weights
            confidence = (
                frequency * 0.3
                + recent_trend * 0.25
                + cycle_consistency * 0.25
                + gap_score * 0.2
            )

            # Normalize to 0-100 scale
            confidences[number] = min(100, max(0, confidence * 100))

        return confidences

    def _calculate_overall_confidence(
        self, predicted_numbers: List[int], historical_data: List, method_name: str
    ) -> float:
        """Calculate overall prediction confidence"""

        # Method historical performance
        method_accuracy = self._get_method_accuracy(method_name, historical_data)

        # Data quality score
        data_quality = self._assess_data_quality(historical_data)

        # Prediction diversity
        diversity_score = self._calculate_prediction_diversity(predicted_numbers)

        # Market conditions (volatility)
        volatility_adjustment = self._calculate_volatility_adjustment(historical_data)

        # Combine factors
        base_confidence = (
            method_accuracy * 0.4
            + data_quality * 0.25
            + diversity_score * 0.2
            + volatility_adjustment * 0.15
        )

        # Apply conservative adjustment
        adjusted_confidence = base_confidence * 0.85  # Conservative factor

        return min(95, max(5, adjusted_confidence))  # Cap between 5-95%

    def _generate_confidence_metrics(
        self,
        predicted_numbers: List[int],
        historical_data: List,
        confidence_level: float,
    ) -> ConfidenceMetrics:
        """Generate detailed confidence metrics"""

        # Calculate expected hit rate
        expected_hits = self._calculate_expected_hits(
            predicted_numbers, historical_data
        )

        # Standard error calculation
        n = len(historical_data)
        p = expected_hits / len(predicted_numbers)
        se = np.sqrt(p * (1 - p) / n) if n > 0 and 0 < p < 1 else 0.1

        # Confidence interval for hit rate
        z_score = stats.norm.ppf((1 + confidence_level) / 2)
        ci_lower = max(0, p - z_score * se)
        ci_upper = min(1, p + z_score * se)

        # Prediction interval (wider than CI)
        pi_factor = 1.5  # Adjustment for prediction vs estimation
        pi_lower = max(0, p - z_score * se * pi_factor)
        pi_upper = min(1, p + z_score * se * pi_factor)

        # Reliability score
        reliability = self._calculate_reliability_score(
            expected_hits, se, len(historical_data)
        )

        # Uncertainty level classification
        uncertainty_level = self._classify_uncertainty_level(se, reliability)

        return ConfidenceMetrics(
            point_estimate=expected_hits,
            confidence_interval=(
                ci_lower * len(predicted_numbers),
                ci_upper * len(predicted_numbers),
            ),
            confidence_level=confidence_level,
            prediction_interval=(
                pi_lower * len(predicted_numbers),
                pi_upper * len(predicted_numbers),
            ),
            reliability_score=reliability,
            uncertainty_level=uncertainty_level,
        )

    def _calculate_number_frequency(self, number: int, historical_data: List) -> float:
        """Calculate normalized frequency for a number"""
        count = 0
        total_possible = 0

        for result in historical_data:
            if hasattr(result, "get_all_2digit_numbers"):
                all_numbers = result.get_all_2digit_numbers()
                if number in all_numbers:
                    count += 1
                total_possible += 1

        return count / total_possible if total_possible > 0 else 0

    def _calculate_recent_trend(self, number: int, recent_data: List) -> float:
        """Calculate recent trend score for a number"""
        if not recent_data:
            return 0.5

        appearances = []
        for i, result in enumerate(recent_data):
            if hasattr(result, "get_all_2digit_numbers"):
                if number in result.get_all_2digit_numbers():
                    appearances.append(i)

        if not appearances:
            return 0.3  # No recent appearances

        # Weight recent appearances more heavily
        weighted_score = sum(1 / (i + 1) for i in appearances)
        max_possible_score = sum(1 / (i + 1) for i in range(len(recent_data)))

        return weighted_score / max_possible_score if max_possible_score > 0 else 0.5

    def _calculate_cycle_consistency(self, number: int, historical_data: List) -> float:
        """Calculate how consistently a number appears in cycles"""
        if len(historical_data) < 14:
            return 0.5

        # Check 7-day and 14-day cycles
        cycle_scores = []

        for cycle_length in [7, 14]:
            cycle_appearances = []
            for i in range(0, len(historical_data), cycle_length):
                cycle_data = historical_data[i : i + cycle_length]
                if len(cycle_data) == cycle_length:
                    appeared = any(
                        number in result.get_all_2digit_numbers()
                        for result in cycle_data
                        if hasattr(result, "get_all_2digit_numbers")
                    )
                    cycle_appearances.append(appeared)

            if cycle_appearances:
                consistency = sum(cycle_appearances) / len(cycle_appearances)
                cycle_scores.append(consistency)

        return np.mean(cycle_scores) if cycle_scores else 0.5

    def _calculate_gap_score(self, number: int, historical_data: List) -> float:
        """Calculate score based on gap since last appearance"""
        last_appearance = None

        for i, result in enumerate(historical_data):
            if hasattr(result, "get_all_2digit_numbers"):
                if number in result.get_all_2digit_numbers():
                    last_appearance = i
                    break

        if last_appearance is None:
            return 0.8  # Long gap might indicate due for appearance

        # Calculate expected gap based on frequency
        frequency = self._calculate_number_frequency(number, historical_data)
        expected_gap = 1 / frequency if frequency > 0 else len(historical_data)

        # Score based on how current gap compares to expected
        if last_appearance < expected_gap:
            return 0.3  # Recently appeared, lower chance
        elif last_appearance > expected_gap * 2:
            return 0.9  # Long overdue
        else:
            return 0.6  # Normal range

    def _get_method_accuracy(self, method_name: str, historical_data: List) -> float:
        """Get historical accuracy for prediction method"""
        # This would typically be loaded from a database or cache
        # For now, return estimated accuracies based on method type
        method_accuracies = {
            "hybrid": 0.25,
            "statistical": 0.22,
            "frequency": 0.20,
            "cycle": 0.18,
            "ml": 0.28,
        }

        return method_accuracies.get(method_name, 0.20)

    def _assess_data_quality(self, historical_data: List) -> float:
        """Assess quality of historical data"""
        if not historical_data:
            return 0.1

        # Factors affecting data quality
        data_volume = min(1.0, len(historical_data) / 100)  # Prefer 100+ days

        # Consistency check (all results should have similar structure)
        consistency_score = 1.0  # Assume good for now

        # Recency factor
        if hasattr(historical_data[0], "ngay"):
            days_old = (datetime.now().date() - historical_data[0].ngay).days
            recency_score = max(0.7, 1.0 - days_old / 365)  # Decay over year
        else:
            recency_score = 0.8

        return data_volume * 0.5 + consistency_score * 0.3 + recency_score * 0.2

    def _calculate_prediction_diversity(self, predicted_numbers: List[int]) -> float:
        """Calculate diversity score for predictions"""
        if not predicted_numbers:
            return 0.5

        # Check spread across number ranges
        ranges = [(0, 24), (25, 49), (50, 74), (75, 99)]
        range_counts = [
            sum(1 for num in predicted_numbers if r[0] <= num <= r[1]) for r in ranges
        ]

        # Calculate diversity using entropy
        total = len(predicted_numbers)
        if total == 0:
            return 0.5

        proportions = [count / total for count in range_counts if count > 0]
        entropy = -sum(p * np.log2(p) for p in proportions if p > 0)
        max_entropy = np.log2(4)  # Maximum for 4 ranges

        diversity_score = entropy / max_entropy if max_entropy > 0 else 0.5

        return diversity_score

    def _calculate_volatility_adjustment(self, historical_data: List) -> float:
        """Calculate volatility adjustment factor"""
        if len(historical_data) < 10:
            return 0.5

        # Calculate day-to-day variation in winning numbers
        daily_counts = []
        for result in historical_data[:30]:  # Last 30 days
            if hasattr(result, "get_all_2digit_numbers"):
                daily_counts.append(len(result.get_all_2digit_numbers()))

        if len(daily_counts) < 2:
            return 0.7

        volatility = np.std(daily_counts) / np.mean(daily_counts)

        # Lower volatility = higher confidence
        adjustment = max(0.3, 1.0 - volatility)

        return adjustment

    def _calculate_expected_hits(
        self, predicted_numbers: List[int], historical_data: List
    ) -> float:
        """Calculate expected number of hits"""
        total_expected = 0

        for number in predicted_numbers:
            frequency = self._calculate_number_frequency(number, historical_data)
            total_expected += frequency

        return total_expected

    def _calculate_reliability_score(
        self, expected_hits: float, standard_error: float, sample_size: int
    ) -> float:
        """Calculate reliability score for predictions"""
        # Higher sample size and lower standard error = higher reliability
        sample_factor = min(1.0, sample_size / 100)
        precision_factor = max(0.1, 1.0 - standard_error * 10)

        reliability = (sample_factor * 0.6 + precision_factor * 0.4) * 100

        return min(100, max(0, reliability))

    def _classify_uncertainty_level(
        self, standard_error: float, reliability_score: float
    ) -> str:
        """Classify uncertainty level"""
        if standard_error < 0.05 and reliability_score > 80:
            return "Low"
        elif standard_error < 0.1 and reliability_score > 60:
            return "Moderate"
        elif standard_error < 0.2 and reliability_score > 40:
            return "High"
        else:
            return "Very High"

    def _assess_prediction_risk(
        self, overall_confidence: float, metrics: ConfidenceMetrics
    ) -> str:
        """Assess risk level of predictions"""
        if overall_confidence > 70 and metrics.reliability_score > 80:
            return "Low Risk - High confidence prediction with reliable historical data"
        elif overall_confidence > 50 and metrics.reliability_score > 60:
            return "Moderate Risk - Reasonable confidence with adequate historical validation"
        elif overall_confidence > 30 and metrics.reliability_score > 40:
            return "High Risk - Lower confidence, use with caution"
        else:
            return "Very High Risk - Unreliable prediction, not recommended for use"

    def _generate_recommendation(
        self,
        overall_confidence: float,
        metrics: ConfidenceMetrics,
        risk_assessment: str,
    ) -> str:
        """Generate actionable recommendation"""
        if "Low Risk" in risk_assessment:
            return f"✅ Strong prediction (confidence: {overall_confidence:.1f}%). Expected hits: {metrics.point_estimate:.1f}-{metrics.confidence_interval[1]:.1f}"
        elif "Moderate Risk" in risk_assessment:
            return f"⚠️ Moderate prediction (confidence: {overall_confidence:.1f}%). Use as guidance, expected hits: {metrics.point_estimate:.1f}±{(metrics.confidence_interval[1]-metrics.confidence_interval[0])/2:.1f}"
        elif "High Risk" in risk_assessment:
            return f"🔶 Weak prediction (confidence: {overall_confidence:.1f}%). High uncertainty, consider alternative methods"
        else:
            return f"❌ Unreliable prediction (confidence: {overall_confidence:.1f}%). Do not use for decision making"

    def generate_confidence_report(
        self, prediction_confidence: PredictionConfidence
    ) -> Dict:
        """Generate detailed confidence report"""
        return {
            "summary": {
                "overall_confidence": f"{prediction_confidence.overall_confidence:.1f}%",
                "expected_hits": f"{prediction_confidence.confidence_metrics.point_estimate:.1f}",
                "confidence_interval": f"[{prediction_confidence.confidence_metrics.confidence_interval[0]:.1f}, {prediction_confidence.confidence_metrics.confidence_interval[1]:.1f}]",
                "uncertainty_level": prediction_confidence.confidence_metrics.uncertainty_level,
                "risk_assessment": prediction_confidence.risk_assessment,
            },
            "individual_numbers": [
                {"number": num, "confidence": f"{conf:.1f}%", "ranking": rank + 1}
                for rank, (num, conf) in enumerate(
                    sorted(
                        prediction_confidence.individual_confidences.items(),
                        key=lambda x: x[1],
                        reverse=True,
                    )
                )
            ],
            "statistical_metrics": {
                "reliability_score": f"{prediction_confidence.confidence_metrics.reliability_score:.1f}%",
                "prediction_interval": f"[{prediction_confidence.confidence_metrics.prediction_interval[0]:.1f}, {prediction_confidence.confidence_metrics.prediction_interval[1]:.1f}]",
                "confidence_level": f"{prediction_confidence.confidence_metrics.confidence_level*100:.0f}%",
            },
            "recommendation": prediction_confidence.recommendation,
        }
