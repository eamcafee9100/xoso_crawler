"""
Adaptive Weight Optimization System
Implements dynamic weight adjustment based on performance feedback
"""

import json
import logging
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple

import numpy as np
import pandas as pd
from scipy.optimize import minimize
from sklearn.metrics import mean_absolute_error, mean_squared_error


@dataclass
class WeightConfig:
    """Configuration for adaptive weights"""

    method_weights: Dict[str, float] = field(default_factory=dict)
    feature_weights: Dict[str, float] = field(default_factory=dict)
    time_decay_factor: float = 0.95
    learning_rate: float = 0.01
    adaptation_threshold: float = 0.05
    min_weight: float = 0.01
    max_weight: float = 0.8


@dataclass
class PerformanceMetrics:
    """Performance metrics for weight optimization"""

    accuracy: float
    hit_rate: float
    precision: float
    recall: float
    f1_score: float
    confidence_correlation: float
    stability_score: float


@dataclass
class AdaptationResult:
    """Result of weight adaptation"""

    old_weights: Dict[str, float]
    new_weights: Dict[str, float]
    improvement: float
    adaptation_reason: str
    confidence_score: float


class AdaptiveWeightOptimizer:
    """
    Dynamic weight optimization system that learns from prediction performance
    """

    def __init__(self, config: WeightConfig = None):
        self.config = config or WeightConfig()
        self.performance_history = []
        self.weight_history = []
        self.logger = logging.getLogger(__name__)

        # Initialize default weights
        self.current_weights = {
            "frequency": 0.25,
            "recent_trend": 0.20,
            "cycle_analysis": 0.20,
            "gap_analysis": 0.15,
            "ml_prediction": 0.20,
        }

        # Performance tracking
        self.method_performance = {}
        self.adaptation_count = 0
        self.last_adaptation = None

    def update_performance(
        self,
        predictions: List[int],
        actual_results: List[int],
        method_contributions: Dict[str, float],
        prediction_date: datetime,
    ) -> PerformanceMetrics:
        """
        Update performance metrics and trigger adaptation if needed

        Args:
            predictions: Predicted numbers
            actual_results: Actual winning numbers
            method_contributions: Contribution of each method to final prediction
            prediction_date: Date of prediction

        Returns:
            PerformanceMetrics for this prediction
        """

        # Calculate performance metrics
        metrics = self._calculate_performance_metrics(predictions, actual_results)

        # Store performance data
        performance_data = {
            "date": prediction_date,
            "metrics": metrics,
            "method_contributions": method_contributions,
            "weights": self.current_weights.copy(),
        }
        self.performance_history.append(performance_data)

        # Check if adaptation is needed
        if self._should_adapt():
            adaptation_result = self._adapt_weights()
            if adaptation_result:
                self.logger.info(
                    f"Weights adapted: {adaptation_result.adaptation_reason}"
                )

        return metrics

    def _calculate_performance_metrics(
        self, predictions: List[int], actual_results: List[int]
    ) -> PerformanceMetrics:
        """Calculate comprehensive performance metrics"""

        if not predictions or not actual_results:
            return PerformanceMetrics(0, 0, 0, 0, 0, 0, 0)

        # Basic metrics
        hits = set(predictions) & set(actual_results)
        hit_count = len(hits)

        accuracy = hit_count / len(predictions) if predictions else 0
        hit_rate = 1 if hit_count > 0 else 0

        # Precision and recall
        true_positives = hit_count
        false_positives = len(predictions) - hit_count
        false_negatives = len(actual_results) - hit_count

        precision = (
            true_positives / (true_positives + false_positives)
            if (true_positives + false_positives) > 0
            else 0
        )
        recall = (
            true_positives / (true_positives + false_negatives)
            if (true_positives + false_negatives) > 0
            else 0
        )

        f1_score = (
            2 * (precision * recall) / (precision + recall)
            if (precision + recall) > 0
            else 0
        )

        # Confidence correlation (placeholder - would need actual confidence scores)
        confidence_correlation = 0.6  # Would be calculated from actual data

        # Stability score based on recent performance variance
        stability_score = self._calculate_stability_score()

        return PerformanceMetrics(
            accuracy=accuracy,
            hit_rate=hit_rate,
            precision=precision,
            recall=recall,
            f1_score=f1_score,
            confidence_correlation=confidence_correlation,
            stability_score=stability_score,
        )

    def _calculate_stability_score(self) -> float:
        """Calculate stability score based on recent performance variance"""
        if len(self.performance_history) < 5:
            return 0.5

        recent_accuracies = [
            p["metrics"].accuracy for p in self.performance_history[-10:]
        ]

        variance = np.var(recent_accuracies)
        stability = max(0, 1 - variance * 10)  # Normalize variance

        return stability

    def _should_adapt(self) -> bool:
        """Determine if weights should be adapted"""

        # Need minimum history
        if len(self.performance_history) < 10:
            return False

        # Don't adapt too frequently
        if self.last_adaptation and (datetime.now() - self.last_adaptation).days < 7:
            return False

        # Check performance trend
        recent_performance = np.mean(
            [p["metrics"].accuracy for p in self.performance_history[-5:]]
        )

        older_performance = np.mean(
            [p["metrics"].accuracy for p in self.performance_history[-15:-5]]
        )

        # Adapt if performance is declining
        performance_decline = older_performance - recent_performance

        return performance_decline > self.config.adaptation_threshold

    def _adapt_weights(self) -> Optional[AdaptationResult]:
        """Adapt weights based on performance history"""

        old_weights = self.current_weights.copy()

        # Analyze method performance
        method_analysis = self._analyze_method_performance()

        # Optimize weights using performance data
        new_weights = self._optimize_weights(method_analysis)

        if new_weights:
            improvement = self._calculate_weight_improvement(old_weights, new_weights)

            self.current_weights = new_weights
            self.adaptation_count += 1
            self.last_adaptation = datetime.now()

            # Store weight history
            self.weight_history.append(
                {
                    "date": datetime.now(),
                    "old_weights": old_weights,
                    "new_weights": new_weights,
                    "improvement": improvement,
                }
            )

            return AdaptationResult(
                old_weights=old_weights,
                new_weights=new_weights,
                improvement=improvement,
                adaptation_reason=self._get_adaptation_reason(method_analysis),
                confidence_score=method_analysis.get("confidence", 0.5),
            )

        return None

    def _analyze_method_performance(self) -> Dict:
        """Analyze performance of individual methods"""

        method_stats = {}

        for method in self.current_weights.keys():
            method_accuracies = []
            method_contributions = []

            for perf_data in self.performance_history[-20:]:  # Last 20 predictions
                if method in perf_data["method_contributions"]:
                    contribution = perf_data["method_contributions"][method]
                    accuracy = perf_data["metrics"].accuracy

                    method_accuracies.append(accuracy)
                    method_contributions.append(contribution)

            if method_accuracies:
                # Calculate correlation between method contribution and accuracy
                correlation = (
                    np.corrcoef(method_contributions, method_accuracies)[0, 1]
                    if len(method_accuracies) > 1
                    else 0
                )

                method_stats[method] = {
                    "avg_accuracy": np.mean(method_accuracies),
                    "contribution_correlation": correlation,
                    "stability": 1 - np.var(method_accuracies),
                    "sample_size": len(method_accuracies),
                }

        return method_stats

    def _optimize_weights(self, method_analysis: Dict) -> Optional[Dict[str, float]]:
        """Optimize weights using performance analysis"""

        if not method_analysis:
            return None

        # Define objective function
        def objective(weights):
            """Objective function for weight optimization"""
            total_score = 0

            for i, (method, weight) in enumerate(
                zip(self.current_weights.keys(), weights)
            ):
                if method in method_analysis:
                    stats = method_analysis[method]

                    # Score based on accuracy, correlation, and stability
                    method_score = (
                        stats["avg_accuracy"] * 0.4
                        + stats["contribution_correlation"] * 0.3
                        + stats["stability"] * 0.3
                    )

                    total_score += weight * method_score

            return -total_score  # Minimize negative score (maximize positive score)

        # Constraints
        def constraint_sum(weights):
            return np.sum(weights) - 1.0  # Weights must sum to 1

        def constraint_min(weights):
            return weights - self.config.min_weight  # Minimum weight constraint

        def constraint_max(weights):
            return self.config.max_weight - weights  # Maximum weight constraint

        # Initial guess (current weights)
        initial_weights = list(self.current_weights.values())

        # Bounds
        bounds = [
            (self.config.min_weight, self.config.max_weight)
            for _ in range(len(initial_weights))
        ]

        # Constraints
        constraints = [
            {"type": "eq", "fun": constraint_sum},
            {"type": "ineq", "fun": constraint_min},
            {"type": "ineq", "fun": constraint_max},
        ]

        try:
            # Optimize
            result = minimize(
                objective,
                initial_weights,
                method="SLSQP",
                bounds=bounds,
                constraints=constraints,
            )

            if result.success:
                # Convert back to dictionary
                optimized_weights = {}
                for i, method in enumerate(self.current_weights.keys()):
                    optimized_weights[method] = result.x[i]

                return optimized_weights

        except Exception as e:
            self.logger.error(f"Weight optimization failed: {e}")

        return None

    def _calculate_weight_improvement(
        self, old_weights: Dict, new_weights: Dict
    ) -> float:
        """Calculate expected improvement from weight changes"""

        # This is a simplified calculation
        # In practice, you'd simulate performance with new weights

        improvement_score = 0

        for method in old_weights.keys():
            weight_change = new_weights[method] - old_weights[method]

            # If method performance is good and weight increased, positive improvement
            if method in self.method_performance:
                method_perf = self.method_performance[method].get("avg_accuracy", 0.2)
                improvement_score += weight_change * method_perf

        return improvement_score

    def _get_adaptation_reason(self, method_analysis: Dict) -> str:
        """Generate human-readable adaptation reason"""

        if not method_analysis:
            return "Insufficient performance data"

        # Find best and worst performing methods
        best_method = max(
            method_analysis.keys(), key=lambda m: method_analysis[m]["avg_accuracy"]
        )
        worst_method = min(
            method_analysis.keys(), key=lambda m: method_analysis[m]["avg_accuracy"]
        )

        best_accuracy = method_analysis[best_method]["avg_accuracy"]
        worst_accuracy = method_analysis[worst_method]["avg_accuracy"]

        return f"Boosted {best_method} (accuracy: {best_accuracy:.3f}), reduced {worst_method} (accuracy: {worst_accuracy:.3f})"

    def get_current_weights(self) -> Dict[str, float]:
        """Get current weight configuration"""
        return self.current_weights.copy()

    def set_weights(self, new_weights: Dict[str, float]):
        """Manually set weights (for testing or override)"""
        # Validate weights
        if abs(sum(new_weights.values()) - 1.0) > 0.01:
            raise ValueError("Weights must sum to 1.0")

        for weight in new_weights.values():
            if not (self.config.min_weight <= weight <= self.config.max_weight):
                raise ValueError(
                    f"Weights must be between {self.config.min_weight} and {self.config.max_weight}"
                )

        self.current_weights = new_weights.copy()

    def get_performance_summary(self) -> Dict:
        """Get performance summary and trends"""

        if not self.performance_history:
            return {"message": "No performance data available"}

        recent_data = self.performance_history[-10:]

        summary = {
            "total_predictions": len(self.performance_history),
            "adaptation_count": self.adaptation_count,
            "current_weights": self.current_weights,
            "recent_performance": {
                "avg_accuracy": np.mean([p["metrics"].accuracy for p in recent_data]),
                "avg_hit_rate": np.mean([p["metrics"].hit_rate for p in recent_data]),
                "stability_score": np.mean(
                    [p["metrics"].stability_score for p in recent_data]
                ),
            },
            "performance_trend": self._calculate_performance_trend(),
            "weight_evolution": self._get_weight_evolution(),
        }

        return summary

    def _calculate_performance_trend(self) -> str:
        """Calculate overall performance trend"""

        if len(self.performance_history) < 6:
            return "Insufficient data"

        first_half = self.performance_history[: len(self.performance_history) // 2]
        second_half = self.performance_history[len(self.performance_history) // 2 :]

        first_avg = np.mean([p["metrics"].accuracy for p in first_half])
        second_avg = np.mean([p["metrics"].accuracy for p in second_half])

        improvement = second_avg - first_avg

        if improvement > 0.02:
            return f"Improving (+{improvement:.3f})"
        elif improvement < -0.02:
            return f"Declining ({improvement:.3f})"
        else:
            return f"Stable ({improvement:.3f})"

    def _get_weight_evolution(self) -> List[Dict]:
        """Get evolution of weights over time"""
        return self.weight_history[-5:]  # Last 5 weight changes

    def export_optimization_data(self, filepath: str):
        """Export optimization data for analysis"""

        export_data = {
            "performance_history": [
                {
                    "date": p["date"].isoformat(),
                    "accuracy": p["metrics"].accuracy,
                    "hit_rate": p["metrics"].hit_rate,
                    "weights": p["weights"],
                }
                for p in self.performance_history
            ],
            "weight_history": [
                {
                    "date": w["date"].isoformat(),
                    "old_weights": w["old_weights"],
                    "new_weights": w["new_weights"],
                    "improvement": w["improvement"],
                }
                for w in self.weight_history
            ],
            "current_config": {
                "weights": self.current_weights,
                "adaptation_count": self.adaptation_count,
                "config": {
                    "learning_rate": self.config.learning_rate,
                    "adaptation_threshold": self.config.adaptation_threshold,
                },
            },
        }

        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(export_data, f, ensure_ascii=False, indent=2)

        self.logger.info(f"Optimization data exported to {filepath}")

    def load_optimization_data(self, filepath: str):
        """Load optimization data from file"""

        try:
            with open(filepath, "r", encoding="utf-8") as f:
                data = json.load(f)

            # Restore current weights
            if "current_config" in data:
                self.current_weights = data["current_config"]["weights"]
                self.adaptation_count = data["current_config"]["adaptation_count"]

            self.logger.info(f"Optimization data loaded from {filepath}")

        except Exception as e:
            self.logger.error(f"Failed to load optimization data: {e}")
