"""
🎯 ENSEMBLE INTELLIGENCE SERVICE - REVOLUTIONARY APPROACH TO LOTTERY PREDICTION

Thay vì dự đoán số, chúng ta dự đoán:
1. Method nào sẽ perform tốt trong context nào
2. Anomaly patterns trong xổ số
3. Meta-features từ method behaviors
4. Dynamic ensemble weighting
"""

import logging
from collections import defaultdict
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple

import numpy as np
import pandas as pd

logger = logging.getLogger(__name__)


@dataclass
class MethodPerformance:
    """Tracking performance của từng method"""

    method_id: str
    hit_rate: float
    consistency: float  # Variance của hit rate
    recent_trend: float  # Slope của performance trong 7 ngày gần đây
    correlation_with_others: float
    temporal_pattern: Dict[
        str, float
    ]  # Performance theo ngày trong tuần, tuần trong tháng


@dataclass
class PredictionContext:
    """Context cho prediction"""

    date: datetime
    day_of_week: int
    week_of_month: int
    recent_results: List[Dict]
    method_recent_performances: Dict[str, MethodPerformance]
    anomaly_score: float


class EnsembleIntelligenceService:
    """
    🧠 REVOLUTIONARY APPROACH: META-PREDICTION SYSTEM

    Thay vì dự đoán số, chúng ta dự đoán:
    - Method nào sẽ perform tốt trong context nào
    - Khi nào hệ thống deviate từ randomness
    - Làm sao combine predictions optimally
    """

    def __init__(self, data_service):
        self.data_service = data_service
        self.method_performances = {}
        self.correlation_matrix = None
        self.baseline_performance = None
        self.anomaly_detector = None

    def initialize_intelligence(self):
        """🔥 Initialize the intelligence system"""
        logger.info("🚀 Initializing Ensemble Intelligence System...")

        # 1. Calculate baseline performance
        self.baseline_performance = self._calculate_baseline_performance()

        # 2. Analyze method correlations
        self.correlation_matrix = self._analyze_method_correlations()

        # 3. Initialize anomaly detector
        self.anomaly_detector = self._initialize_anomaly_detector()

        # 4. Calculate method performances
        self._calculate_method_performances()

        logger.info("✅ Ensemble Intelligence System initialized successfully!")

    def _calculate_baseline_performance(self) -> float:
        """
        🎯 Calculate random baseline performance

        Tính hit rate của random selection để so sánh
        """
        logger.info("📊 Calculating baseline performance...")

        # Lấy historical data từ 30 ngày gần đây
        historical_data = self.data_service.get_pattern_data_for_analysis(30)

        total_predictions = 0
        total_hits = 0

        for data_point in historical_data:
            # Simulate random selection
            random_numbers = np.random.choice(range(100), 2, replace=False)
            random_numbers = [str(num).zfill(2) for num in random_numbers]

            # Check hit rate
            actual_results = data_point.get("results", {})
            hit_count = self._count_hits(random_numbers, actual_results)

            total_predictions += len(random_numbers)
            total_hits += hit_count

        baseline_hit_rate = (
            total_hits / total_predictions if total_predictions > 0 else 0
        )

        logger.info(f"🎲 Baseline (Random) Hit Rate: {baseline_hit_rate:.2%}")
        return baseline_hit_rate

    def _analyze_method_correlations(self) -> np.ndarray:
        """
        🔍 Analyze correlations between methods

        Tìm hiểu methods nào giống nhau để group chúng
        """
        logger.info("🔗 Analyzing method correlations...")

        # Lấy predictions của tất cả methods trong 30 ngày
        historical_data = self.data_service.get_pattern_data_for_analysis(30)

        # Tạo matrix predictions
        method_predictions = defaultdict(list)

        for data_point in historical_data:
            date = data_point.get("date")

            # Lấy predictions của tất cả methods cho ngày này
            for method in self.data_service.get_available_methods():
                try:
                    predictions = method.calculate(data_point)
                    # Convert predictions to binary vector
                    prediction_vector = self._encode_predictions(predictions)
                    method_predictions[method.get_code()].append(prediction_vector)
                except Exception as e:
                    logger.warning(f"Error calculating {method.get_code()}: {e}")
                    method_predictions[method.get_code()].append(np.zeros(100))

        # Tính correlation matrix
        method_names = list(method_predictions.keys())
        n_methods = len(method_names)
        correlation_matrix = np.zeros((n_methods, n_methods))

        for i, method1 in enumerate(method_names):
            for j, method2 in enumerate(method_names):
                if i == j:
                    correlation_matrix[i, j] = 1.0
                else:
                    corr = np.corrcoef(
                        np.array(method_predictions[method1]).flatten(),
                        np.array(method_predictions[method2]).flatten(),
                    )[0, 1]
                    correlation_matrix[i, j] = corr if not np.isnan(corr) else 0

        logger.info(f"🔗 Correlation matrix calculated for {n_methods} methods")
        return correlation_matrix

    def _initialize_anomaly_detector(self):
        """
        🚨 Initialize anomaly detection system

        Detect when lottery results deviate from pure randomness
        """
        logger.info("🚨 Initializing anomaly detector...")

        # Implement statistical tests for randomness
        class AnomalyDetector:
            def __init__(self):
                self.historical_distributions = {}

            def detect_anomalies(self, recent_results: List[Dict]) -> float:
                """
                Detect anomalies in recent results
                Returns anomaly score (0-1, higher = more anomalous)
                """
                if not recent_results:
                    return 0.0

                # Chi-square test for uniformity
                numbers = []
                for result in recent_results:
                    for prize, value in result.items():
                        if isinstance(value, str) and value.isdigit():
                            numbers.extend(
                                [int(value[i : i + 2]) for i in range(0, len(value), 2)]
                            )

                if not numbers:
                    return 0.0

                # Calculate chi-square statistic
                observed = np.histogram(numbers, bins=100, range=(0, 100))[0]
                expected = np.full(100, len(numbers) / 100)

                chi_square = np.sum((observed - expected) ** 2 / expected)

                # Normalize to 0-1 range
                # Chi-square with 99 degrees of freedom has mean 99
                anomaly_score = min(1.0, chi_square / 200)  # Normalize

                return anomaly_score

        return AnomalyDetector()

    def _calculate_method_performances(self):
        """
        📈 Calculate comprehensive performance metrics for each method
        """
        logger.info("📈 Calculating method performances...")

        historical_data = self.data_service.get_pattern_data_for_analysis(30)

        for method in self.data_service.get_available_methods():
            method_id = method.get_code()

            # Calculate various performance metrics
            hit_rates = []
            daily_performances = []

            for data_point in historical_data:
                try:
                    predictions = method.calculate(data_point)
                    actual_results = data_point.get("results", {})

                    hit_count = self._count_hits(predictions, actual_results)
                    hit_rate = hit_count / len(predictions) if predictions else 0

                    hit_rates.append(hit_rate)
                    daily_performances.append(
                        {
                            "date": data_point.get("date"),
                            "hit_rate": hit_rate,
                            "day_of_week": (
                                data_point.get("date").weekday()
                                if data_point.get("date")
                                else 0
                            ),
                        }
                    )

                except Exception as e:
                    logger.warning(
                        f"Error calculating performance for {method_id}: {e}"
                    )
                    hit_rates.append(0)

            # Calculate metrics
            avg_hit_rate = np.mean(hit_rates) if hit_rates else 0
            consistency = (
                1 - np.std(hit_rates) if hit_rates else 0
            )  # Higher = more consistent

            # Calculate recent trend (slope of last 7 days)
            recent_hit_rates = hit_rates[-7:] if len(hit_rates) >= 7 else hit_rates
            recent_trend = (
                np.polyfit(range(len(recent_hit_rates)), recent_hit_rates, 1)[0]
                if len(recent_hit_rates) > 1
                else 0
            )

            # Calculate temporal patterns
            temporal_pattern = self._calculate_temporal_patterns(daily_performances)

            # Store performance
            self.method_performances[method_id] = MethodPerformance(
                method_id=method_id,
                hit_rate=avg_hit_rate,
                consistency=consistency,
                recent_trend=recent_trend,
                correlation_with_others=0,  # Will be calculated later
                temporal_pattern=temporal_pattern,
            )

        logger.info(
            f"📈 Calculated performances for {len(self.method_performances)} methods"
        )

    def _calculate_temporal_patterns(
        self, daily_performances: List[Dict]
    ) -> Dict[str, float]:
        """Calculate performance patterns by day of week, week of month"""
        patterns = {}

        # Group by day of week
        dow_performance = defaultdict(list)
        for perf in daily_performances:
            dow = perf["day_of_week"]
            dow_performance[dow].append(perf["hit_rate"])

        # Average performance by day of week
        for dow, rates in dow_performance.items():
            patterns[f"dow_{dow}"] = np.mean(rates) if rates else 0

        return patterns

    def predict_optimal_strategy(self, prediction_date: datetime) -> Dict:
        """
        🎯 MAIN PREDICTION FUNCTION

        Predict optimal strategy for given date
        """
        logger.info(f"🎯 Predicting optimal strategy for {prediction_date}")

        # 1. Create prediction context
        context = self._create_prediction_context(prediction_date)

        # 2. Calculate method weights based on context
        method_weights = self._calculate_dynamic_weights(context)

        # 3. Generate ensemble predictions
        ensemble_predictions = self._generate_ensemble_predictions(
            context, method_weights
        )

        # 4. Apply anomaly-based adjustments
        adjusted_predictions = self._apply_anomaly_adjustments(
            ensemble_predictions, context
        )

        # 5. Calculate confidence scores
        confidence_scores = self._calculate_confidence_scores(
            adjusted_predictions, context
        )

        return {
            "predictions": adjusted_predictions,
            "confidence_scores": confidence_scores,
            "method_weights": method_weights,
            "context": context,
            "anomaly_score": context.anomaly_score,
            "recommended_strategy": self._recommend_strategy(
                context, confidence_scores
            ),
        }

    def _create_prediction_context(
        self, prediction_date: datetime
    ) -> PredictionContext:
        """Create context for prediction"""
        # Get recent results
        recent_results = self.data_service.get_pattern_data_for_analysis(7)

        # Calculate anomaly score
        anomaly_score = self.anomaly_detector.detect_anomalies(recent_results)

        return PredictionContext(
            date=prediction_date,
            day_of_week=prediction_date.weekday(),
            week_of_month=(prediction_date.day - 1) // 7 + 1,
            recent_results=recent_results,
            method_recent_performances=self.method_performances,
            anomaly_score=anomaly_score,
        )

    def _calculate_dynamic_weights(
        self, context: PredictionContext
    ) -> Dict[str, float]:
        """
        🧠 Calculate dynamic weights for methods based on context

        This is where the magic happens - we predict which methods
        will perform best in current context
        """
        weights = {}

        for method_id, performance in context.method_recent_performances.items():
            # Base weight from historical performance
            base_weight = performance.hit_rate

            # Adjust for recent trend
            trend_adjustment = 1 + (
                performance.recent_trend * 0.5
            )  # Amplify recent trends

            # Adjust for consistency
            consistency_adjustment = 1 + (performance.consistency * 0.3)

            # Adjust for temporal context
            temporal_key = f"dow_{context.day_of_week}"
            temporal_adjustment = 1 + (
                performance.temporal_pattern.get(temporal_key, 0) * 0.2
            )

            # Adjust for anomaly score
            anomaly_adjustment = 1 + (
                context.anomaly_score * 0.1
            )  # Slightly favor during anomalies

            # Calculate final weight
            final_weight = (
                base_weight
                * trend_adjustment
                * consistency_adjustment
                * temporal_adjustment
                * anomaly_adjustment
            )
            weights[method_id] = max(0, final_weight)  # Ensure non-negative

        # Normalize weights
        total_weight = sum(weights.values())
        if total_weight > 0:
            weights = {k: v / total_weight for k, v in weights.items()}

        return weights

    def _generate_ensemble_predictions(
        self, context: PredictionContext, method_weights: Dict[str, float]
    ) -> List[str]:
        """Generate ensemble predictions using weighted methods"""
        # This is a simplified version - in real implementation,
        # you'd aggregate predictions from all methods

        # For now, return top weighted methods' predictions
        top_methods = sorted(method_weights.items(), key=lambda x: x[1], reverse=True)[
            :3
        ]

        # Generate predictions from top methods
        predictions = []
        for method_id, weight in top_methods:
            # Get method predictions (simplified)
            method_predictions = self._get_method_predictions(method_id, context)
            predictions.extend(method_predictions)

        # Remove duplicates and return top predictions
        unique_predictions = list(set(predictions))
        return unique_predictions[:10]  # Return top 10 unique predictions

    def _get_method_predictions(
        self, method_id: str, context: PredictionContext
    ) -> List[str]:
        """Get predictions from specific method"""
        # This would interface with your existing methods
        # For now, return dummy predictions
        return [f"{i:02d}" for i in range(10)]  # Simplified

    def _apply_anomaly_adjustments(
        self, predictions: List[str], context: PredictionContext
    ) -> List[str]:
        """Apply adjustments based on anomaly score"""
        if context.anomaly_score > 0.7:  # High anomaly
            # During high anomaly periods, favor less common numbers
            logger.info(
                f"🚨 High anomaly detected ({context.anomaly_score:.2f}), adjusting strategy"
            )
            # Implement anomaly-based adjustments

        return predictions

    def _calculate_confidence_scores(
        self, predictions: List[str], context: PredictionContext
    ) -> Dict[str, float]:
        """Calculate confidence scores for predictions"""
        confidence_scores = {}

        for pred in predictions:
            # Base confidence from method consensus
            base_confidence = 0.5

            # Adjust based on anomaly score
            if context.anomaly_score > 0.5:
                base_confidence *= 0.8  # Lower confidence during anomalies

            # Adjust based on recent performance
            avg_performance = np.mean(
                [p.hit_rate for p in context.method_recent_performances.values()]
            )
            performance_adjustment = (
                avg_performance / self.baseline_performance
                if self.baseline_performance > 0
                else 1
            )

            final_confidence = base_confidence * performance_adjustment
            confidence_scores[pred] = min(1.0, final_confidence)

        return confidence_scores

    def _recommend_strategy(
        self, context: PredictionContext, confidence_scores: Dict[str, float]
    ) -> str:
        """Recommend overall strategy based on context"""
        avg_confidence = np.mean(list(confidence_scores.values()))

        if context.anomaly_score > 0.7:
            return "ANOMALY_DETECTED"
        elif avg_confidence > 0.7:
            return "AGGRESSIVE"
        elif avg_confidence > 0.4:
            return "MODERATE"
        else:
            return "CONSERVATIVE"

    def _count_hits(self, predictions: List[str], actual_results: Dict) -> int:
        """Count hits between predictions and actual results"""
        hits = 0
        prediction_set = set(predictions)

        for prize, value in actual_results.items():
            if isinstance(value, str) and value.isdigit():
                # Extract 2-digit numbers from result
                result_numbers = [value[i : i + 2] for i in range(0, len(value), 2)]
                hits += len(prediction_set.intersection(set(result_numbers)))

        return hits

    def _encode_predictions(self, predictions: List[str]) -> np.ndarray:
        """Encode predictions as binary vector"""
        vector = np.zeros(100)
        for pred in predictions:
            try:
                num = int(pred)
                if 0 <= num < 100:
                    vector[num] = 1
            except ValueError:
                continue
        return vector

    def generate_performance_report(self) -> Dict:
        """Generate comprehensive performance report"""
        report = {
            "baseline_performance": self.baseline_performance,
            "method_performances": {},
            "correlation_analysis": {},
            "recommendations": [],
        }

        # Method performances
        for method_id, performance in self.method_performances.items():
            report["method_performances"][method_id] = {
                "hit_rate": performance.hit_rate,
                "vs_baseline": (
                    performance.hit_rate / self.baseline_performance
                    if self.baseline_performance > 0
                    else 0
                ),
                "consistency": performance.consistency,
                "recent_trend": performance.recent_trend,
                "temporal_patterns": performance.temporal_pattern,
            }

        # Correlation analysis
        if self.correlation_matrix is not None:
            high_corr_pairs = []
            method_names = list(self.method_performances.keys())

            for i in range(len(method_names)):
                for j in range(i + 1, len(method_names)):
                    corr = self.correlation_matrix[i, j]
                    if abs(corr) > 0.8:  # High correlation
                        high_corr_pairs.append(
                            {
                                "method1": method_names[i],
                                "method2": method_names[j],
                                "correlation": corr,
                            }
                        )

            report["correlation_analysis"]["high_correlation_pairs"] = high_corr_pairs

        # Recommendations
        best_methods = sorted(
            self.method_performances.items(), key=lambda x: x[1].hit_rate, reverse=True
        )[:5]

        report["recommendations"] = [
            f"Top performing method: {best_methods[0][0]} (Hit rate: {best_methods[0][1].hit_rate:.2%})",
            f"Baseline performance: {self.baseline_performance:.2%}",
            (
                f"Best vs baseline improvement: {best_methods[0][1].hit_rate / self.baseline_performance:.1f}x"
                if self.baseline_performance > 0
                else "N/A"
            ),
        ]

        return report
