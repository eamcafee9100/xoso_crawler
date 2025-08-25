"""
Backtesting Framework for Lottery Prediction System
Implements comprehensive validation and performance measurement
"""

import json
import logging
from collections import defaultdict
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple

import numpy as np
import pandas as pd


@dataclass
class BacktestResult:
    """Single backtest result"""

    date: datetime
    predicted_numbers: List[int]
    actual_numbers: List[int]
    hit_count: int
    accuracy: float
    confidence_score: float
    prediction_method: str


@dataclass
class BacktestSummary:
    """Comprehensive backtest summary"""

    total_tests: int
    avg_accuracy: float
    hit_rate: float
    best_accuracy: float
    worst_accuracy: float
    confidence_correlation: float
    method_performance: Dict[str, float]
    monthly_performance: Dict[str, float]


class BacktestingFramework:
    """
    Comprehensive backtesting framework for lottery prediction validation
    """

    def __init__(self, results_model, prediction_service):
        self.results_model = results_model
        self.prediction_service = prediction_service
        self.logger = logging.getLogger(__name__)

    def run_historical_backtest(
        self,
        start_date: datetime,
        end_date: datetime,
        prediction_methods: List[str] = None,
    ) -> BacktestSummary:
        """
        Run comprehensive historical backtest

        Args:
            start_date: Start date for backtesting
            end_date: End date for backtesting
            prediction_methods: List of prediction methods to test

        Returns:
            BacktestSummary with comprehensive results
        """
        if prediction_methods is None:
            prediction_methods = ["hybrid", "statistical", "frequency", "cycle"]

        results = []
        current_date = start_date

        while current_date <= end_date:
            # Skip weekends (lottery only on weekdays)
            if current_date.weekday() < 5:  # Monday = 0, Friday = 4
                try:
                    # Get actual result for this date
                    actual_result = self.results_model.objects.filter(
                        ngay=current_date
                    ).first()

                    if actual_result:
                        actual_numbers = actual_result.get_all_2digit_numbers()

                        # Test each prediction method
                        for method in prediction_methods:
                            predicted_numbers, confidence = self._predict_for_date(
                                current_date, method
                            )

                            if predicted_numbers:
                                hit_count = len(
                                    set(predicted_numbers) & set(actual_numbers)
                                )
                                accuracy = (hit_count / len(predicted_numbers)) * 100

                                results.append(
                                    BacktestResult(
                                        date=current_date,
                                        predicted_numbers=predicted_numbers,
                                        actual_numbers=actual_numbers,
                                        hit_count=hit_count,
                                        accuracy=accuracy,
                                        confidence_score=confidence,
                                        prediction_method=method,
                                    )
                                )

                except Exception as e:
                    self.logger.error(f"Error in backtest for {current_date}: {e}")

            current_date += timedelta(days=1)

        return self._generate_summary(results)

    def _predict_for_date(self, date: datetime, method: str) -> Tuple[List[int], float]:
        """
        Generate prediction for specific date using historical data only

        Args:
            date: Target date
            method: Prediction method

        Returns:
            Tuple of (predicted_numbers, confidence_score)
        """
        try:
            # Get historical data up to (but not including) target date
            historical_data = self.results_model.objects.filter(ngay__lt=date).order_by(
                "-ngay"
            )[
                :100
            ]  # Use last 100 days

            if len(historical_data) < 30:  # Need minimum data
                return [], 0.0

            # Apply prediction method based on historical data
            if method == "hybrid":
                return self._hybrid_prediction(historical_data)
            elif method == "statistical":
                return self._statistical_prediction(historical_data)
            elif method == "frequency":
                return self._frequency_prediction(historical_data)
            elif method == "cycle":
                return self._cycle_prediction(historical_data)
            else:
                return [], 0.0

        except Exception as e:
            self.logger.error(f"Prediction error for {date}, method {method}: {e}")
            return [], 0.0

    def _hybrid_prediction(self, historical_data) -> Tuple[List[int], float]:
        """Hybrid prediction using multiple strategies"""
        # Frequency analysis
        freq_numbers = {}
        for result in historical_data:
            for num in result.get_all_2digit_numbers():
                freq_numbers[num] = freq_numbers.get(num, 0) + 1

        # Recent trend analysis (last 10 days)
        recent_numbers = {}
        for result in historical_data[:10]:
            for num in result.get_all_2digit_numbers():
                recent_numbers[num] = recent_numbers.get(num, 0) + 2  # Higher weight

        # Combine scores
        combined_scores = {}
        all_numbers = set(freq_numbers.keys()) | set(recent_numbers.keys())

        for num in all_numbers:
            freq_score = freq_numbers.get(num, 0)
            recent_score = recent_numbers.get(num, 0)
            combined_scores[num] = freq_score + recent_score

        # Select top 15 numbers
        top_numbers = sorted(combined_scores.items(), key=lambda x: x[1], reverse=True)[
            :15
        ]
        predicted_numbers = [num for num, _ in top_numbers]

        # Calculate confidence
        total_score = sum(combined_scores.values())
        top_score = sum(score for _, score in top_numbers)
        confidence = (top_score / total_score * 100) if total_score > 0 else 0

        return predicted_numbers, confidence

    def _statistical_prediction(self, historical_data) -> Tuple[List[int], float]:
        """Statistical-based prediction"""
        # Calculate statistical metrics for each number
        number_stats = {}

        for num in range(100):  # 00-99
            appearances = []
            for i, result in enumerate(historical_data):
                if num in result.get_all_2digit_numbers():
                    appearances.append(i)

            if appearances:
                # Calculate statistical indicators
                avg_gap = (
                    np.mean(np.diff(appearances))
                    if len(appearances) > 1
                    else len(historical_data)
                )
                last_appearance = (
                    appearances[0] if appearances else len(historical_data)
                )
                frequency = len(appearances) / len(historical_data)

                # Statistical score
                expected_appearance = last_appearance / avg_gap if avg_gap > 0 else 0
                number_stats[num] = frequency * (1 + expected_appearance)

        # Select top numbers
        top_numbers = sorted(number_stats.items(), key=lambda x: x[1], reverse=True)[
            :15
        ]
        predicted_numbers = [num for num, _ in top_numbers]

        # Confidence based on statistical significance
        confidence = min(80, len(historical_data) / 2)  # Max 80% confidence

        return predicted_numbers, confidence

    def _frequency_prediction(self, historical_data) -> Tuple[List[int], float]:
        """Simple frequency-based prediction"""
        freq_count = {}

        for result in historical_data:
            for num in result.get_all_2digit_numbers():
                freq_count[num] = freq_count.get(num, 0) + 1

        top_numbers = sorted(freq_count.items(), key=lambda x: x[1], reverse=True)[:15]
        predicted_numbers = [num for num, _ in top_numbers]

        # Confidence based on data volume
        confidence = min(70, len(historical_data))

        return predicted_numbers, confidence

    def _cycle_prediction(self, historical_data) -> Tuple[List[int], float]:
        """Cycle-based prediction"""
        # Analyze 7-day and 14-day cycles
        cycle_patterns = {7: {}, 14: {}}

        for cycle_length in [7, 14]:
            for i in range(0, len(historical_data), cycle_length):
                cycle_data = historical_data[i : i + cycle_length]
                if len(cycle_data) == cycle_length:
                    cycle_numbers = set()
                    for result in cycle_data:
                        cycle_numbers.update(result.get_all_2digit_numbers())

                    for num in cycle_numbers:
                        cycle_patterns[cycle_length][num] = (
                            cycle_patterns[cycle_length].get(num, 0) + 1
                        )

        # Combine cycle scores
        combined_scores = {}
        for cycle_length, patterns in cycle_patterns.items():
            weight = 2 if cycle_length == 7 else 1  # Prefer weekly cycles
            for num, count in patterns.items():
                combined_scores[num] = combined_scores.get(num, 0) + (count * weight)

        top_numbers = sorted(combined_scores.items(), key=lambda x: x[1], reverse=True)[
            :15
        ]
        predicted_numbers = [num for num, _ in top_numbers]

        confidence = min(
            60, len(historical_data) * 0.8
        )  # Lower confidence for cycle method

        return predicted_numbers, confidence

    def _generate_summary(self, results: List[BacktestResult]) -> BacktestSummary:
        """Generate comprehensive backtest summary"""
        if not results:
            return BacktestSummary(0, 0, 0, 0, 0, 0, {}, {})

        # Basic metrics
        total_tests = len(results)
        avg_accuracy = np.mean([r.accuracy for r in results])
        hit_rate = np.mean([1 if r.hit_count > 0 else 0 for r in results])
        best_accuracy = max(r.accuracy for r in results)
        worst_accuracy = min(r.accuracy for r in results)

        # Confidence correlation
        accuracies = [r.accuracy for r in results]
        confidences = [r.confidence_score for r in results]
        confidence_correlation = (
            np.corrcoef(accuracies, confidences)[0, 1] if len(accuracies) > 1 else 0
        )

        # Method performance
        method_performance = {}
        for method in set(r.prediction_method for r in results):
            method_results = [r for r in results if r.prediction_method == method]
            method_performance[method] = np.mean([r.accuracy for r in method_results])

        # Monthly performance
        monthly_performance = {}
        for result in results:
            month_key = result.date.strftime("%Y-%m")
            if month_key not in monthly_performance:
                monthly_performance[month_key] = []
            monthly_performance[month_key].append(result.accuracy)

        for month in monthly_performance:
            monthly_performance[month] = np.mean(monthly_performance[month])

        return BacktestSummary(
            total_tests=total_tests,
            avg_accuracy=avg_accuracy,
            hit_rate=hit_rate,
            best_accuracy=best_accuracy,
            worst_accuracy=worst_accuracy,
            confidence_correlation=confidence_correlation,
            method_performance=method_performance,
            monthly_performance=monthly_performance,
        )

    def generate_report(self, summary: BacktestSummary) -> Dict:
        """Generate detailed backtest report"""
        return {
            "overview": {
                "total_tests": summary.total_tests,
                "average_accuracy": f"{summary.avg_accuracy:.2f}%",
                "hit_rate": f"{summary.hit_rate:.2f}%",
                "accuracy_range": f"{summary.worst_accuracy:.2f}% - {summary.best_accuracy:.2f}%",
            },
            "method_ranking": sorted(
                summary.method_performance.items(), key=lambda x: x[1], reverse=True
            ),
            "monthly_trends": summary.monthly_performance,
            "confidence_reliability": {
                "correlation": f"{summary.confidence_correlation:.3f}",
                "interpretation": self._interpret_correlation(
                    summary.confidence_correlation
                ),
            },
            "recommendations": self._generate_recommendations(summary),
        }

    def _interpret_correlation(self, correlation: float) -> str:
        """Interpret confidence-accuracy correlation"""
        if correlation > 0.7:
            return "Strong positive correlation - confidence scores are reliable"
        elif correlation > 0.3:
            return "Moderate correlation - confidence has some predictive value"
        elif correlation > -0.3:
            return "Weak correlation - confidence scores need improvement"
        else:
            return "Negative correlation - confidence scores are misleading"

    def _generate_recommendations(self, summary: BacktestSummary) -> List[str]:
        """Generate improvement recommendations"""
        recommendations = []

        if summary.avg_accuracy < 20:
            recommendations.append(
                "Overall accuracy is low - consider ensemble methods"
            )

        if summary.confidence_correlation < 0.3:
            recommendations.append("Improve confidence calculation methodology")

        if summary.hit_rate < 0.5:
            recommendations.append("Focus on increasing hit rate over pure accuracy")

        # Method-specific recommendations
        best_method = max(summary.method_performance.items(), key=lambda x: x[1])
        recommendations.append(
            f"Best performing method: {best_method[0]} ({best_method[1]:.2f}%)"
        )

        return recommendations

    def export_results(self, summary: BacktestSummary, filepath: str):
        """Export backtest results to JSON file"""
        report = self.generate_report(summary)

        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(report, f, ensure_ascii=False, indent=2)

        self.logger.info(f"Backtest results exported to {filepath}")
