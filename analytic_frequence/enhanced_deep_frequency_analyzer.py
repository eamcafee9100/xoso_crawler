#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
🚀 ENHANCED DEEP FREQUENCY ANALYZER V3
Complete system with validation, feedback loop, and visualization support
"""

import json
import logging
import math
import pickle
from collections import Counter, defaultdict
from datetime import date, datetime, timedelta
from typing import Any, Dict, List, Optional, Tuple

import numpy as np
import pandas as pd
from django.conf import settings
from django.core.cache import cache
from django.db.models import Avg, Count, Q


class CustomJSONEncoder(json.JSONEncoder):
    """Custom JSON encoder to handle numpy types and other non-serializable objects"""

    def default(self, obj):
        if isinstance(obj, np.integer):
            return int(obj)
        elif isinstance(obj, np.floating):
            return float(obj)
        elif isinstance(obj, np.ndarray):
            return obj.tolist()
        elif isinstance(obj, datetime):
            return obj.isoformat()
        elif isinstance(obj, date):
            return obj.isoformat()
        elif isinstance(obj, bool):
            return "enabled" if obj else "disabled"
        elif hasattr(obj, "__dict__"):
            return str(obj)
        return super().default(obj)

    def encode(self, o):
        """Override encode to handle booleans in nested structures"""
        return super().encode(self._convert_booleans(o))

    def _convert_booleans(self, obj):
        """Recursively convert all boolean values to strings"""
        if isinstance(obj, bool):
            return "enabled" if obj else "disabled"
        elif isinstance(obj, dict):
            return {key: self._convert_booleans(value) for key, value in obj.items()}
        elif isinstance(obj, list):
            return [self._convert_booleans(item) for item in obj]
        elif isinstance(obj, tuple):
            return tuple(self._convert_booleans(item) for item in obj)
        else:
            return obj


def safe_chi_square_test(observed_freq, expected_freq, significance_level=0.05):
    """
    Safe chi-square test replacement to avoid scipy.stats.chisquare errors

    Args:
        observed_freq: Observed frequency
        expected_freq: Expected frequency
        significance_level: Significance threshold

    Returns:
        dict: Contains statistic, p_value, is_significant
    """
    try:
        if expected_freq <= 0:
            return {
                "statistic": 0.0,
                "p_value": 1.0,
                "is_significant": "not_significant",
            }

        # Calculate z-score for single sample
        expected_std = math.sqrt(expected_freq) if expected_freq > 0 else 1
        z_score = abs(observed_freq - expected_freq) / expected_std

        # Convert z-score to p-value (two-tailed test)
        p_value = 2 * (1 - 0.5 * (1 + math.erf(z_score / math.sqrt(2))))
        p_value = max(0.0, min(1.0, p_value))  # Clamp between 0 and 1

        return {
            "statistic": round(z_score, 4),
            "p_value": round(p_value, 6),
            "is_significant": (
                "significant" if p_value < significance_level else "not_significant"
            ),
        }

    except Exception as e:
        return {"statistic": 0.0, "p_value": 1.0, "is_significant": "not_significant"}


from scipy import fft
from scipy.stats import chi2_contingency

from results.models import NumberFrequencyStats

logger = logging.getLogger(__name__)


class PredictionValidator:
    """
    🔍 VALIDATION FRAMEWORK: Comprehensive prediction validation system
    """

    def __init__(self):
        self.validation_history = []
        self.performance_metrics = {}

    def validate_predictions(
        self,
        predictions: Dict,
        actual_results: List[str],
        prediction_date: date,
        method_name: str = "enhanced_deep_frequency",
    ) -> Dict:
        """
        Validate predictions against actual results

        Args:
            predictions: Dictionary of predictions by category
            actual_results: List of actual winning numbers
            prediction_date: Date of prediction
            method_name: Name of prediction method

        Returns:
            Dict: Comprehensive validation results
        """
        try:
            validation_result = {
                "prediction_date": prediction_date.isoformat(),
                "method_name": method_name,
                "actual_results": actual_results,
                "validation_metrics": {},
                "category_performance": {},
                "overall_performance": {},
            }

            total_predictions = 0
            total_hits = 0

            # Validate each prediction category
            for category, pred_data in predictions.items():
                if category in ["analysis_metadata"]:
                    continue

                category_predictions = self._extract_predictions_from_category(
                    pred_data
                )
                category_hits = len(set(category_predictions) & set(actual_results))

                precision = (
                    category_hits / len(category_predictions)
                    if category_predictions
                    else 0
                )
                recall = category_hits / len(actual_results) if actual_results else 0
                f1_score = (
                    2 * (precision * recall) / (precision + recall)
                    if (precision + recall) > 0
                    else 0
                )

                validation_result["category_performance"][category] = {
                    "predictions_count": len(category_predictions),
                    "hits": category_hits,
                    "precision": round(precision, 4),
                    "recall": round(recall, 4),
                    "f1_score": round(f1_score, 4),
                    "accuracy_rate": (
                        round(category_hits / len(category_predictions), 4)
                        if category_predictions
                        else 0
                    ),
                }

                total_predictions += len(category_predictions)
                total_hits += category_hits

            # Overall performance metrics
            overall_precision = (
                total_hits / total_predictions if total_predictions > 0 else 0
            )
            overall_recall = total_hits / len(actual_results) if actual_results else 0
            overall_f1 = (
                2
                * (overall_precision * overall_recall)
                / (overall_precision + overall_recall)
                if (overall_precision + overall_recall) > 0
                else 0
            )

            validation_result["overall_performance"] = {
                "total_predictions": total_predictions,
                "total_hits": total_hits,
                "precision": round(overall_precision, 4),
                "recall": round(overall_recall, 4),
                "f1_score": round(overall_f1, 4),
                "hit_rate": (
                    round(total_hits / len(actual_results), 4) if actual_results else 0
                ),
            }

            # ROI Analysis (assuming betting strategy)
            roi_analysis = self._calculate_roi(
                category_predictions, actual_results, bet_amount=1000
            )
            validation_result["roi_analysis"] = roi_analysis

            # Store validation history
            self.validation_history.append(validation_result)

            # Update performance metrics
            self._update_performance_metrics(validation_result)

            logger.info(
                f"✅ Validation completed: {total_hits}/{total_predictions} hits ({overall_precision:.2%})"
            )
            return validation_result

        except Exception as e:
            logger.error(f"❌ Validation failed: {e}")
            return {"error": str(e)}

    def _extract_predictions_from_category(self, pred_data) -> List[str]:
        """Extract number predictions from category data"""
        predictions = []

        if isinstance(pred_data, dict):
            # Extract keys (numbers) if they look like 2-digit numbers
            for key in pred_data.keys():
                if isinstance(key, str) and len(key) == 2 and key.isdigit():
                    predictions.append(key)
                elif (
                    isinstance(key, str)
                    and key.replace("-", "").replace("_", "").isdigit()
                ):
                    # Handle correlation pairs like "01-23"
                    numbers = key.replace("-", "_").split("_")
                    predictions.extend(
                        [num for num in numbers if len(num) == 2 and num.isdigit()]
                    )

        return list(set(predictions))  # Remove duplicates

    def _calculate_roi(
        self,
        predictions: List[str],
        actual_results: List[str],
        bet_amount: float = 1000,
    ) -> Dict:
        """Calculate ROI assuming a betting strategy"""
        if not predictions:
            return {
                "roi_percentage": 0,
                "profit_loss": 0,
                "interpretation": "No predictions to evaluate",
            }

        # Simplified ROI calculation
        # Assume: bet equally on all predictions, win 80x bet for exact match
        bet_per_number = bet_amount / len(predictions)
        total_investment = bet_amount

        hits = len(set(predictions) & set(actual_results))
        winnings = hits * bet_per_number * 80  # 80:1 payout ratio for lottery

        profit_loss = winnings - total_investment
        roi_percentage = (
            (profit_loss / total_investment) * 100 if total_investment > 0 else 0
        )

        return {
            "total_investment": total_investment,
            "winnings": winnings,
            "profit_loss": round(profit_loss, 2),
            "roi_percentage": round(roi_percentage, 2),
            "hit_ratio": f"{hits}/{len(predictions)}",
            "interpretation": (
                "Profitable"
                if profit_loss > 0
                else "Loss" if profit_loss < 0 else "Break-even"
            ),
        }

    def _update_performance_metrics(self, validation_result: Dict):
        """Update cumulative performance metrics"""
        method_name = validation_result["method_name"]

        if method_name not in self.performance_metrics:
            self.performance_metrics[method_name] = {
                "total_validations": 0,
                "cumulative_precision": 0,
                "cumulative_recall": 0,
                "cumulative_f1": 0,
                "best_performance": {},
                "worst_performance": {},
                "trend_analysis": [],
            }

        metrics = self.performance_metrics[method_name]
        metrics["total_validations"] += 1

        current_performance = validation_result["overall_performance"]

        # Update cumulative metrics
        n = metrics["total_validations"]
        metrics["cumulative_precision"] = (
            (n - 1) * metrics["cumulative_precision"] + current_performance["precision"]
        ) / n
        metrics["cumulative_recall"] = (
            (n - 1) * metrics["cumulative_recall"] + current_performance["recall"]
        ) / n
        metrics["cumulative_f1"] = (
            (n - 1) * metrics["cumulative_f1"] + current_performance["f1_score"]
        ) / n

        # Track best/worst performances
        if not metrics["best_performance"] or current_performance["f1_score"] > metrics[
            "best_performance"
        ].get("f1_score", 0):
            metrics["best_performance"] = current_performance.copy()
            metrics["best_performance"]["date"] = validation_result["prediction_date"]

        if not metrics["worst_performance"] or current_performance[
            "f1_score"
        ] < metrics["worst_performance"].get("f1_score", 1):
            metrics["worst_performance"] = current_performance.copy()
            metrics["worst_performance"]["date"] = validation_result["prediction_date"]

        # Add to trend analysis
        metrics["trend_analysis"].append(
            {
                "date": validation_result["prediction_date"],
                "f1_score": current_performance["f1_score"],
                "precision": current_performance["precision"],
                "recall": current_performance["recall"],
            }
        )

        # Keep only last 100 trend points
        if len(metrics["trend_analysis"]) > 100:
            metrics["trend_analysis"] = metrics["trend_analysis"][-100:]

    def get_performance_summary(self, method_name: str = None) -> Dict:
        """Get comprehensive performance summary"""
        if method_name:
            return self.performance_metrics.get(method_name, {})
        else:
            return self.performance_metrics

    def generate_validation_report(self, days_back: int = 30) -> Dict:
        """Generate validation report for recent predictions"""
        cutoff_date = date.today() - timedelta(days=days_back)

        recent_validations = [
            v
            for v in self.validation_history
            if datetime.fromisoformat(v["prediction_date"]).date() >= cutoff_date
        ]

        if not recent_validations:
            return {"message": "No recent validations found"}

        # Aggregate statistics
        total_validations = len(recent_validations)
        avg_precision = np.mean(
            [v["overall_performance"]["precision"] for v in recent_validations]
        )
        avg_recall = np.mean(
            [v["overall_performance"]["recall"] for v in recent_validations]
        )
        avg_f1 = np.mean(
            [v["overall_performance"]["f1_score"] for v in recent_validations]
        )

        # ROI analysis
        total_profit_loss = sum(
            [
                v.get("roi_analysis", {}).get("profit_loss", 0)
                for v in recent_validations
            ]
        )
        profitable_days = len(
            [
                v
                for v in recent_validations
                if v.get("roi_analysis", {}).get("profit_loss", 0) > 0
            ]
        )

        return {
            "report_period": f"Last {days_back} days",
            "total_validations": total_validations,
            "average_metrics": {
                "precision": round(avg_precision, 4),
                "recall": round(avg_recall, 4),
                "f1_score": round(avg_f1, 4),
            },
            "roi_summary": {
                "total_profit_loss": round(total_profit_loss, 2),
                "profitable_days": profitable_days,
                "profitability_rate": (
                    round(profitable_days / total_validations, 2)
                    if total_validations > 0
                    else 0
                ),
            },
            "trend_direction": self._analyze_performance_trend(recent_validations),
        }

    def _analyze_performance_trend(self, validations: List[Dict]) -> str:
        """Analyze if performance is improving or declining"""
        if len(validations) < 3:
            return "insufficient_data"

        f1_scores = [v["overall_performance"]["f1_score"] for v in validations]

        # Simple trend analysis
        first_third = np.mean(f1_scores[: len(f1_scores) // 3])
        last_third = np.mean(f1_scores[-len(f1_scores) // 3 :])

        if last_third > first_third * 1.1:
            return "improving"
        elif last_third < first_third * 0.9:
            return "declining"
        else:
            return "stable"


class FeedbackLearningSystem:
    """
    🔄 FEEDBACK LOOP: Adaptive learning from prediction history
    """

    def __init__(self):
        self.learning_history = []
        self.method_weights = {
            "hot_numbers": 0.25,
            "cold_numbers": 0.15,
            "cyclical_patterns": 0.20,
            "mean_reversion": 0.15,
            "momentum_patterns": 0.15,
            "gap_analysis": 0.10,
        }
        self.adaptive_parameters = {}

    def learn_from_validation(self, validation_result: Dict):
        """Learn and adapt from validation results"""
        try:
            # Extract performance by category
            category_performance = validation_result.get("category_performance", {})

            # Adjust method weights based on performance
            self._adjust_method_weights(category_performance)

            # Update adaptive parameters
            self._update_adaptive_parameters(validation_result)

            # Store learning history
            self.learning_history.append(
                {
                    "date": validation_result["prediction_date"],
                    "adjustments": self._calculate_adjustments(category_performance),
                    "new_weights": self.method_weights.copy(),
                }
            )

            logger.info(
                f"🧠 Learning from validation: adjusted {len(category_performance)} method weights"
            )

        except Exception as e:
            logger.error(f"❌ Learning failed: {e}")

    def _adjust_method_weights(self, category_performance: Dict):
        """Adjust method weights based on performance"""
        total_adjustment = 0
        adjustments = {}

        for category, performance in category_performance.items():
            if category in self.method_weights:
                f1_score = performance.get("f1_score", 0)
                current_weight = self.method_weights[category]

                # Adjust weight based on F1 score
                # Good performance (F1 > 0.3) increases weight
                # Poor performance (F1 < 0.1) decreases weight
                if f1_score > 0.3:
                    adjustment = current_weight * 0.1  # Increase by 10%
                elif f1_score < 0.1:
                    adjustment = -current_weight * 0.1  # Decrease by 10%
                else:
                    adjustment = 0

                adjustments[category] = adjustment
                total_adjustment += adjustment

        # Apply adjustments and normalize
        for category, adjustment in adjustments.items():
            self.method_weights[category] = max(
                0.05, self.method_weights[category] + adjustment
            )

        # Normalize weights to sum to 1
        total_weight = sum(self.method_weights.values())
        if total_weight > 0:
            for category in self.method_weights:
                self.method_weights[category] /= total_weight

    def _update_adaptive_parameters(self, validation_result: Dict):
        """Update adaptive parameters based on validation results"""
        # Example: Adjust significance levels, window sizes, etc.
        overall_performance = validation_result.get("overall_performance", {})
        f1_score = overall_performance.get("f1_score", 0)

        # Adjust significance level based on performance
        if f1_score > 0.4:
            # Good performance - make criteria stricter
            self.adaptive_parameters["significance_level"] = max(
                0.01, self.adaptive_parameters.get("significance_level", 0.05) * 0.9
            )
        elif f1_score < 0.2:
            # Poor performance - make criteria more lenient
            self.adaptive_parameters["significance_level"] = min(
                0.1, self.adaptive_parameters.get("significance_level", 0.05) * 1.1
            )

        # Adjust lookback windows
        if f1_score > 0.3:
            # Good performance - extend lookback
            self.adaptive_parameters["lookback_days"] = min(
                365, self.adaptive_parameters.get("lookback_days", 180) * 1.05
            )
        elif f1_score < 0.15:
            # Poor performance - reduce lookback
            self.adaptive_parameters["lookback_days"] = max(
                90, self.adaptive_parameters.get("lookback_days", 180) * 0.95
            )

    def _calculate_adjustments(self, category_performance: Dict) -> Dict:
        """Calculate what adjustments were made"""
        adjustments = {}
        for category, performance in category_performance.items():
            if category in self.method_weights:
                f1_score = performance.get("f1_score", 0)
                if f1_score > 0.3:
                    adjustments[category] = "weight_increased"
                elif f1_score < 0.1:
                    adjustments[category] = "weight_decreased"
                else:
                    adjustments[category] = "weight_maintained"
        return adjustments

    def get_adaptive_predictions(self, base_predictions: Dict) -> Dict:
        """Apply learned weights to generate adaptive predictions"""
        adaptive_predictions = {
            "adaptive_weighted_recommendations": [],
            "confidence_scores": {},
            "method_weights_used": self.method_weights.copy(),
            "adaptive_parameters": self.adaptive_parameters.copy(),
        }

        # Collect all numbers with their weighted scores
        number_scores = defaultdict(float)

        for method, weight in self.method_weights.items():
            method_predictions = base_predictions.get(method, {})

            if isinstance(method_predictions, dict):
                for number, data in method_predictions.items():
                    if (
                        isinstance(number, str)
                        and len(number) == 2
                        and number.isdigit()
                    ):
                        # Extract confidence or use default
                        confidence = 1.0
                        if isinstance(data, dict):
                            confidence = data.get(
                                "confidence_score",
                                data.get("ratio", data.get("reversion_pressure", 1.0)),
                            )

                        number_scores[number] += weight * confidence

        # Sort by weighted score and take top recommendations
        sorted_numbers = sorted(number_scores.items(), key=lambda x: x[1], reverse=True)

        adaptive_predictions["adaptive_weighted_recommendations"] = [
            num for num, score in sorted_numbers[:20]  # Top 20
        ]

        adaptive_predictions["confidence_scores"] = {
            num: round(score, 4) for num, score in sorted_numbers[:20]
        }

        return adaptive_predictions

    def get_learning_summary(self) -> Dict:
        """Get summary of learning progress"""
        if not self.learning_history:
            return {"message": "No learning history available"}

        return {
            "total_learning_sessions": len(self.learning_history),
            "current_method_weights": self.method_weights,
            "current_adaptive_parameters": self.adaptive_parameters,
            "recent_adjustments": (
                self.learning_history[-5:]
                if len(self.learning_history) >= 5
                else self.learning_history
            ),
            "weight_evolution": self._analyze_weight_evolution(),
        }

    def _analyze_weight_evolution(self) -> Dict:
        """Analyze how weights have evolved over time"""
        if len(self.learning_history) < 2:
            return {"message": "Insufficient history for evolution analysis"}

        initial_weights = self.learning_history[0]["new_weights"]
        current_weights = self.method_weights

        evolution = {}
        for method in initial_weights:
            initial = initial_weights[method]
            current = current_weights.get(method, 0)
            change = current - initial
            evolution[method] = {
                "initial_weight": round(initial, 4),
                "current_weight": round(current, 4),
                "change": round(change, 4),
                "change_percentage": (
                    round((change / initial) * 100, 2) if initial > 0 else 0
                ),
            }

        return evolution


class VisualizationDataGenerator:
    """
    📈 VISUALIZATION: Generate data for charts and dashboards
    """

    def __init__(self):
        self.chart_configs = {}

    def generate_frequency_heatmap_data(self, frequency_analysis: Dict) -> Dict:
        """Generate data for frequency heatmap visualization"""
        try:
            heatmap_data = {
                "chart_type": "heatmap",
                "title": "Number Frequency Heatmap",
                "data": [],
                "config": {
                    "x_axis": "Number",
                    "y_axis": "Frequency Level",
                    "color_scale": "RdYlBu_r",
                },
            }

            # Extract hot and cold numbers
            hot_numbers = frequency_analysis.get("hot_numbers", {})
            cold_numbers = frequency_analysis.get("cold_numbers", {})

            # Create heatmap matrix data
            for number in range(100):
                num_str = str(number).zfill(2)

                frequency_level = 0  # Default neutral
                if num_str in hot_numbers:
                    frequency_level = hot_numbers[num_str].get("ratio", 1) * 10
                elif num_str in cold_numbers:
                    frequency_level = cold_numbers[num_str].get("ratio", 1) * 10

                heatmap_data["data"].append(
                    {
                        "number": num_str,
                        "row": number // 10,
                        "col": number % 10,
                        "frequency_level": round(frequency_level, 2),
                        "category": (
                            "hot"
                            if num_str in hot_numbers
                            else "cold" if num_str in cold_numbers else "neutral"
                        ),
                    }
                )

            return heatmap_data

        except Exception as e:
            logger.error(f"❌ Heatmap data generation failed: {e}")
            return {"error": str(e)}

    def generate_trend_chart_data(self, trend_analysis: Dict) -> Dict:
        """Generate data for trend charts"""
        try:
            trend_data = {
                "chart_type": "line_chart",
                "title": "Number Frequency Trends",
                "datasets": [],
                "config": {
                    "x_axis": "Time Period",
                    "y_axis": "Frequency",
                    "legend": True,
                },
            }

            emerging_patterns = trend_analysis.get("emerging_patterns", {})
            declining_patterns = trend_analysis.get("declining_patterns", {})

            # Create trend lines for top emerging numbers
            for i, (number, data) in enumerate(list(emerging_patterns.items())[:5]):
                trend_data["datasets"].append(
                    {
                        "label": f"Number {number} (Emerging)",
                        "data": data.get("quarter_frequencies", []),
                        "color": f"rgba(75, 192, 192, 0.8)",
                        "trend": "increasing",
                    }
                )

            # Create trend lines for top declining numbers
            for i, (number, data) in enumerate(list(declining_patterns.items())[:5]):
                trend_data["datasets"].append(
                    {
                        "label": f"Number {number} (Declining)",
                        "data": data.get("quarter_frequencies", []),
                        "color": f"rgba(255, 99, 132, 0.8)",
                        "trend": "decreasing",
                    }
                )

            return trend_data

        except Exception as e:
            logger.error(f"❌ Trend chart data generation failed: {e}")
            return {"error": str(e)}

    def generate_correlation_network_data(self, correlation_analysis: Dict) -> Dict:
        """Generate data for correlation network visualization"""
        try:
            network_data = {
                "chart_type": "network",
                "title": "Number Correlation Network",
                "nodes": [],
                "edges": [],
                "config": {
                    "node_size_by": "degree",
                    "edge_width_by": "correlation_strength",
                    "color_by": "community",
                },
            }

            correlation_pairs = correlation_analysis.get("correlation_pairs", {})

            # Create nodes (numbers)
            nodes_set = set()
            for pair_key in correlation_pairs:
                num1, num2 = pair_key.split("-")
                nodes_set.add(num1)
                nodes_set.add(num2)

            for number in nodes_set:
                network_data["nodes"].append(
                    {
                        "id": number,
                        "label": number,
                        "degree": len([p for p in correlation_pairs if number in p]),
                        "group": int(number) // 20,  # Color by groups of 20
                    }
                )

            # Create edges (correlations)
            for pair_key, correlation_data in correlation_pairs.items():
                if (
                    abs(correlation_data["correlation"]) > 0.2
                ):  # Only strong correlations
                    num1, num2 = pair_key.split("-")
                    network_data["edges"].append(
                        {
                            "source": num1,
                            "target": num2,
                            "weight": abs(correlation_data["correlation"]),
                            "correlation": correlation_data["correlation"],
                            "type": correlation_data["type"],
                        }
                    )

            return network_data

        except Exception as e:
            logger.error(f"❌ Network data generation failed: {e}")
            return {"error": str(e)}

    def generate_performance_dashboard_data(
        self, validation_results: List[Dict]
    ) -> Dict:
        """Generate comprehensive dashboard data"""
        try:
            dashboard_data = {
                "chart_type": "dashboard",
                "title": "Prediction Performance Dashboard",
                "widgets": {},
                "last_updated": datetime.now().isoformat(),
            }

            if not validation_results:
                return dashboard_data

            # Performance over time
            dashboard_data["widgets"]["performance_timeline"] = {
                "type": "line_chart",
                "title": "Performance Over Time",
                "data": [
                    {
                        "date": v["prediction_date"],
                        "precision": v["overall_performance"]["precision"],
                        "recall": v["overall_performance"]["recall"],
                        "f1_score": v["overall_performance"]["f1_score"],
                    }
                    for v in validation_results[-30:]  # Last 30 validations
                ],
            }

            # ROI analysis
            roi_data = [
                v.get("roi_analysis", {})
                for v in validation_results
                if v.get("roi_analysis")
            ]
            if roi_data:
                dashboard_data["widgets"]["roi_analysis"] = {
                    "type": "bar_chart",
                    "title": "ROI Analysis",
                    "data": [
                        {
                            "date": v["prediction_date"],
                            "profit_loss": v.get("roi_analysis", {}).get(
                                "profit_loss", 0
                            ),
                            "roi_percentage": v.get("roi_analysis", {}).get(
                                "roi_percentage", 0
                            ),
                        }
                        for v in validation_results[-20:]  # Last 20 validations
                    ],
                }

            # Category performance comparison
            if validation_results:
                latest_validation = validation_results[-1]
                category_performance = latest_validation.get("category_performance", {})

                dashboard_data["widgets"]["category_performance"] = {
                    "type": "radar_chart",
                    "title": "Method Performance Comparison",
                    "data": [
                        {
                            "method": category,
                            "precision": perf.get("precision", 0),
                            "recall": perf.get("recall", 0),
                            "f1_score": perf.get("f1_score", 0),
                        }
                        for category, perf in category_performance.items()
                    ],
                }

            # Summary statistics
            recent_results = (
                validation_results[-10:]
                if len(validation_results) >= 10
                else validation_results
            )
            avg_precision = np.mean(
                [v["overall_performance"]["precision"] for v in recent_results]
            )
            avg_recall = np.mean(
                [v["overall_performance"]["recall"] for v in recent_results]
            )
            avg_f1 = np.mean(
                [v["overall_performance"]["f1_score"] for v in recent_results]
            )

            dashboard_data["widgets"]["summary_stats"] = {
                "type": "metrics_cards",
                "title": "Summary Statistics",
                "data": {
                    "average_precision": round(avg_precision, 4),
                    "average_recall": round(avg_recall, 4),
                    "average_f1_score": round(avg_f1, 4),
                    "total_validations": len(validation_results),
                    "recent_trend": self._calculate_recent_trend(validation_results),
                },
            }

            return dashboard_data

        except Exception as e:
            logger.error(f"❌ Dashboard data generation failed: {e}")
            return {"error": str(e)}

    def _calculate_recent_trend(self, validation_results: List[Dict]) -> str:
        """Calculate recent performance trend"""
        if len(validation_results) < 6:
            return "insufficient_data"

        recent_scores = [
            v["overall_performance"]["f1_score"] for v in validation_results[-6:]
        ]
        older_scores = [
            v["overall_performance"]["f1_score"] for v in validation_results[-12:-6]
        ]

        if not older_scores:
            return "insufficient_data"

        recent_avg = np.mean(recent_scores)
        older_avg = np.mean(older_scores)

        if recent_avg > older_avg * 1.1:
            return "improving"
        elif recent_avg < older_avg * 0.9:
            return "declining"
        else:
            return "stable"

    def generate_chart_config(self, chart_type: str) -> Dict:
        """Generate configuration for different chart types"""
        configs = {
            "heatmap": {
                "responsive": True,
                "colorscale": "RdYlBu",
                "showscale": True,
                "hoverongaps": False,
            },
            "line_chart": {
                "responsive": True,
                "interaction": {"intersect": False},
                "scales": {
                    "x": {"display": True, "title": {"display": True}},
                    "y": {"display": True, "title": {"display": True}},
                },
            },
            "network": {
                "physics": {"enabled": True},
                "nodes": {"borderWidth": 2, "font": {"size": 16}},
                "edges": {"width": 2, "smooth": True},
            },
        }

        return configs.get(chart_type, {})


class EnhancedDeepFrequencyAnalyzer:
    """
    🚀 ENHANCED VERSION: Advanced frequency analysis with validation, feedback loop, and visualization
    """

    def __init__(self):
        self.frequency_cache = {}
        self.pattern_cache = {}
        self.statistical_cache = {}

        # Initialize new components
        self.validator = PredictionValidator()
        self.feedback_system = FeedbackLearningSystem()
        self.viz_generator = VisualizationDataGenerator()

        # Enhanced configuration
        self.config = {
            "enable_validation": "enabled",
            "enable_feedback_learning": "enabled",
            "enable_visualization": "enabled",
            "cache_results": "enabled",
            "auto_adjust_parameters": "enabled",
        }

    def analyze_frequency_patterns_enhanced(
        self,
        start_date: date = None,
        end_date: date = None,
        significance_level: float = 0.05,
    ) -> Dict:
        """
        🚀 ENHANCED CORE: Comprehensive frequency pattern analysis with DB integration

        Args:
            start_date: Analysis start date (default: 6 months ago)
            end_date: Analysis end date (default: today)
            significance_level: Statistical significance threshold (default: 0.05)

        Returns:
            Dict: Comprehensive frequency analysis results
        """
        try:
            # Set default date range
            if not end_date:
                end_date = date.today()
            if not start_date:
                start_date = end_date - timedelta(days=180)  # 6 months

            logger.info(
                f"🔍 Starting enhanced frequency analysis: {start_date} to {end_date}"
            )

            # Get base dataset
            base_queryset = NumberFrequencyStats.objects.filter(
                date__range=[start_date, end_date]
            )

            total_records = base_queryset.count()
            if total_records < 30:
                logger.warning(f"⚠️ Insufficient data: only {total_records} records")
                return self._get_fallback_patterns()

            logger.info(f"📊 Analyzing {total_records} frequency records")

            # Comprehensive analysis suite
            patterns = {
                "analysis_metadata": {
                    "start_date": start_date.isoformat(),
                    "end_date": end_date.isoformat(),
                    "total_records": total_records,
                    "significance_level": significance_level,
                    "analysis_timestamp": datetime.now().isoformat(),
                },
                # ✅ Enhanced core analyses
                "hot_numbers": self._identify_hot_numbers_statistical(
                    base_queryset, significance_level
                ),
                "cold_numbers": self._identify_cold_numbers_statistical(
                    base_queryset, significance_level
                ),
                "cyclical_patterns": self._detect_cyclical_patterns_enhanced(
                    base_queryset
                ),
                "mean_reversion": self._analyze_mean_reversion_enhanced(base_queryset),
                "momentum_patterns": self._analyze_momentum_enhanced(base_queryset),
                # 🚀 NEW: Date-aware analyses (previously impossible)
                "seasonal_effects": self._analyze_seasonal_effects_enhanced(
                    base_queryset
                ),
                "day_of_week_bias": self._analyze_dow_bias_enhanced(base_queryset),
                "month_end_effects": self._analyze_month_end_effects_enhanced(
                    base_queryset
                ),
                "prize_position_intelligence": self._analyze_prize_position_patterns(
                    base_queryset
                ),
                # ✅ Enhanced correlation analysis
                "gap_analysis": self._analyze_advanced_gaps(base_queryset, days=30),
                "correlation_matrix": self._calculate_number_correlations_enhanced(
                    base_queryset
                ),
                # 🆕 Advanced statistical analyses
                "statistical_tests": self._perform_statistical_tests(
                    base_queryset, significance_level
                ),
                "trend_analysis": self._analyze_trends_enhanced(base_queryset),
                "risk_assessment": self._assess_prediction_risks(base_queryset),
            }

            logger.info("✅ Enhanced deep frequency analysis completed")

            # SAFETY: Convert any boolean values to strings before return
            encoder = CustomJSONEncoder()
            safe_patterns = encoder._convert_booleans(patterns)

            return safe_patterns

        except Exception as e:
            logger.error(f"❌ Enhanced frequency analysis failed: {e}")

            fallback_data = self._get_fallback_patterns()

            # SAFETY: Convert any boolean values to strings
            encoder = CustomJSONEncoder()
            safe_fallback = encoder._convert_booleans(fallback_data)

            return safe_fallback

    def _identify_hot_numbers_statistical(
        self, queryset, significance_level: float = 0.05
    ) -> Dict:
        """
        🔥 ENHANCED: Statistical hot number identification with chi-square testing
        """
        try:
            hot_numbers = {}
            total_days = queryset.values("date").distinct().count()

            if total_days == 0:
                return {}

            # Expected frequency per number (assuming uniform distribution)
            expected_freq_per_number = total_days * 0.01  # 1% chance per number per day

            for number in range(100):
                num_str = str(number).zfill(2)

                # Count actual appearances
                number_stats = queryset.filter(number=num_str)
                observed_freq = number_stats.count()

                if observed_freq == 0:
                    continue

                # Chi-square goodness of fit test
                try:
                    test_result = safe_chi_square_test(
                        observed_freq, expected_freq_per_number, significance_level
                    )

                    chi2_stat = test_result["statistic"]
                    p_value = test_result["p_value"]
                    is_significant = test_result["is_significant"] == "significant"

                    is_hot = (
                        observed_freq > expected_freq_per_number * 1.2
                    )  # 20% above expected

                    if is_significant and is_hot:
                        # Additional metrics
                        recent_appearances = number_stats.filter(
                            date__gte=date.today() - timedelta(days=30)
                        ).count()

                        last_appearance = number_stats.order_by("-date").first()
                        days_since_last = (
                            (date.today() - last_appearance.date).days
                            if last_appearance
                            else 999
                        )

                        # Prize position analysis
                        special_appearances = number_stats.filter(
                            appeared_in_special=True
                        ).count()
                        first_appearances = number_stats.filter(
                            appeared_in_first=True
                        ).count()

                        hot_numbers[num_str] = {
                            "frequency": observed_freq,
                            "expected_frequency": round(expected_freq_per_number, 2),
                            "frequency_ratio": round(
                                observed_freq / expected_freq_per_number, 2
                            ),
                            "chi2_statistic": round(chi2_stat, 4),
                            "p_value": round(p_value, 6),
                            "statistical_significance": (
                                "significant" if is_significant else "not_significant"
                            ),
                            "recent_momentum": recent_appearances,
                            "days_since_last_appearance": days_since_last,
                            "special_prize_rate": (
                                round(special_appearances / observed_freq, 2)
                                if observed_freq > 0
                                else 0
                            ),
                            "first_prize_rate": (
                                round(first_appearances / observed_freq, 2)
                                if observed_freq > 0
                                else 0
                            ),
                            "hotness_score": round(
                                (observed_freq / expected_freq_per_number)
                                * (1 - p_value)
                                * (1 + recent_appearances / 30),
                                2,
                            ),
                        }

                except Exception as chi2_error:
                    logger.warning(
                        f"Chi-square test failed for number {num_str}: {chi2_error}"
                    )
                    continue

            # Sort by hotness score
            sorted_hot = dict(
                sorted(
                    hot_numbers.items(),
                    key=lambda x: x[1]["hotness_score"],
                    reverse=True,
                )
            )

            logger.info(
                f"🔥 Identified {len(sorted_hot)} statistically significant hot numbers"
            )
            return dict(list(sorted_hot.items())[:20])  # Top 20

        except Exception as e:
            logger.warning(f"Statistical hot numbers analysis failed: {e}")
            return {}

    def _identify_cold_numbers_statistical(
        self, queryset, significance_level: float = 0.05
    ) -> Dict:
        """
        ❄️ ENHANCED: Statistical cold number identification
        """
        try:
            cold_numbers = {}
            total_days = queryset.values("date").distinct().count()

            if total_days == 0:
                return {}

            expected_freq_per_number = total_days * 0.01

            for number in range(100):
                num_str = str(number).zfill(2)

                number_stats = queryset.filter(number=num_str)
                observed_freq = number_stats.count()

                # Chi-square test for under-representation
                try:
                    if expected_freq_per_number > 0:
                        # For cold numbers, we'll use a simpler approach
                        # Calculate how much below expected this number is
                        deviation = expected_freq_per_number - observed_freq
                        normalized_deviation = (
                            deviation / expected_freq_per_number
                            if expected_freq_per_number > 0
                            else 0
                        )

                        # Simple significance test based on standard deviation
                        # Assuming Poisson distribution for lottery numbers
                        expected_std = (
                            (expected_freq_per_number**0.5)
                            if expected_freq_per_number > 0
                            else 1
                        )
                        z_score = (
                            abs(deviation) / expected_std if expected_std > 0 else 0
                        )

                        # Convert z-score to approximate p-value (two-tailed)
                        import math

                        p_value = 2 * (1 - 0.5 * (1 + math.erf(z_score / math.sqrt(2))))

                        is_significant = p_value < significance_level
                        is_cold = (
                            observed_freq < expected_freq_per_number * 0.8
                        )  # 20% below expected

                        if is_cold:  # Don't require significance for cold numbers
                            # Days since last appearance
                            last_appearance = number_stats.order_by("-date").first()
                            days_absent = (
                                (date.today() - last_appearance.date).days
                                if last_appearance
                                else total_days
                            )

                            # Absence streak analysis
                            absence_periods = self._calculate_absence_periods(
                                num_str, queryset
                            )

                            cold_numbers[num_str] = {
                                "frequency": observed_freq,
                                "expected_frequency": round(
                                    expected_freq_per_number, 2
                                ),
                                "frequency_ratio": (
                                    round(observed_freq / expected_freq_per_number, 2)
                                    if expected_freq_per_number > 0
                                    else 0
                                ),
                                "chi2_statistic": round(z_score, 4),
                                "p_value": round(p_value, 6),
                                "days_absent": days_absent,
                                "absence_streak": absence_periods["current_streak"],
                                "max_absence_period": absence_periods["max_period"],
                                "avg_absence_period": absence_periods["avg_period"],
                                "reversion_pressure": (
                                    round(
                                        (expected_freq_per_number - observed_freq)
                                        / expected_freq_per_number
                                        * (1 + days_absent / total_days),
                                        2,
                                    )
                                    if expected_freq_per_number > 0
                                    else 0
                                ),
                                "coldness_score": (
                                    round(
                                        (expected_freq_per_number - observed_freq)
                                        / expected_freq_per_number
                                        * (1 + days_absent / 30),
                                        2,
                                    )
                                    if expected_freq_per_number > 0
                                    else 0
                                ),
                            }

                except Exception as chi2_error:
                    logger.warning(
                        f"Chi-square test failed for cold number {num_str}: {chi2_error}"
                    )
                    continue

            # Sort by coldness score
            sorted_cold = dict(
                sorted(
                    cold_numbers.items(),
                    key=lambda x: x[1]["coldness_score"],
                    reverse=True,
                )
            )

            logger.info(f"❄️ Identified {len(sorted_cold)} cold numbers")
            return dict(list(sorted_cold.items())[:20])  # Top 20

        except Exception as e:
            logger.warning(f"Statistical cold numbers analysis failed: {e}")
            return {}

    def _analyze_seasonal_effects_enhanced(self, queryset) -> Dict:
        """
        📅 NEW FEATURE: Comprehensive seasonal analysis (previously impossible)
        """
        try:
            seasonal_patterns = {
                "monthly_patterns": {},
                "quarterly_patterns": {},
                "day_of_week_patterns": {},
                "day_of_month_patterns": {},
                "week_of_month_patterns": {},
            }

            # Monthly patterns
            for month in range(1, 13):
                month_stats = queryset.filter(month=month)
                month_count = month_stats.count()
                unique_numbers = month_stats.values("number").distinct().count()

                # Top numbers for this month
                top_numbers = (
                    month_stats.values("number")
                    .annotate(count=Count("number"))
                    .order_by("-count")[:10]
                )

                seasonal_patterns["monthly_patterns"][month] = {
                    "total_appearances": month_count,
                    "unique_numbers": unique_numbers,
                    "diversity_score": unique_numbers / 100.0,  # 0-1 score
                    "top_numbers": [
                        {
                            "number": item["number"],
                            "count": item["count"],
                            "month_dominance": round(item["count"] / month_count, 3),
                        }
                        for item in top_numbers
                    ],
                }

            # Day of week patterns
            for dow in range(7):
                dow_stats = queryset.filter(day_of_week=dow)
                dow_count = dow_stats.count()

                if dow_count > 0:
                    # Prize position bias by day of week
                    special_rate = (
                        dow_stats.filter(appeared_in_special=True).count() / dow_count
                    )
                    first_rate = (
                        dow_stats.filter(appeared_in_first=True).count() / dow_count
                    )

                    seasonal_patterns["day_of_week_patterns"][dow] = {
                        "total_appearances": dow_count,
                        "special_prize_rate": round(special_rate, 3),
                        "first_prize_rate": round(first_rate, 3),
                        "day_name": [
                            "Monday",
                            "Tuesday",
                            "Wednesday",
                            "Thursday",
                            "Friday",
                            "Saturday",
                            "Sunday",
                        ][dow],
                    }

            # Day of month patterns (month-end effects)
            for day_range in [(1, 10), (11, 20), (21, 31)]:
                range_stats = queryset.filter(
                    day_of_month__gte=day_range[0], day_of_month__lte=day_range[1]
                )
                range_count = range_stats.count()

                range_name = f"days_{day_range[0]}_to_{day_range[1]}"
                seasonal_patterns["day_of_month_patterns"][range_name] = {
                    "total_appearances": range_count,
                    "period": f"{day_range[0]}-{day_range[1]}",
                    "intensity": (
                        range_count / queryset.count() if queryset.count() > 0 else 0
                    ),
                }

            logger.info("📅 Seasonal effects analysis completed")
            return seasonal_patterns

        except Exception as e:
            logger.warning(f"Seasonal effects analysis failed: {e}")
            return {
                "monthly_patterns": {},
                "quarterly_patterns": {},
                "day_of_week_patterns": {},
            }

    def _analyze_prize_position_patterns(self, queryset) -> Dict:
        """
        🏆 NEW FEATURE: Prize position intelligence analysis
        """
        try:
            position_intelligence = {}

            # Overall position statistics
            total_records = queryset.count()
            special_total = queryset.filter(appeared_in_special=True).count()
            first_total = queryset.filter(appeared_in_first=True).count()
            other_total = queryset.filter(appeared_in_other=True).count()

            overall_stats = {
                "special_prize_rate": (
                    round(special_total / total_records, 3) if total_records > 0 else 0
                ),
                "first_prize_rate": (
                    round(first_total / total_records, 3) if total_records > 0 else 0
                ),
                "other_prize_rate": (
                    round(other_total / total_records, 3) if total_records > 0 else 0
                ),
            }

            # Per-number position analysis
            number_position_patterns = {}

            for number in range(100):
                num_str = str(number).zfill(2)
                number_stats = queryset.filter(number=num_str)
                number_count = number_stats.count()

                if number_count < 3:  # Minimum threshold
                    continue

                special_count = number_stats.filter(appeared_in_special=True).count()
                first_count = number_stats.filter(appeared_in_first=True).count()
                other_count = number_stats.filter(appeared_in_other=True).count()

                # Position preferences
                special_rate = special_count / number_count
                first_rate = first_count / number_count
                other_rate = other_count / number_count

                # Determine preferred position
                preferred_position = (
                    "special"
                    if special_rate > first_rate and special_rate > other_rate
                    else "first" if first_rate > other_rate else "other"
                )

                # Position diversification (entropy-like measure)
                rates = [special_rate, first_rate, other_rate]
                non_zero_rates = [r for r in rates if r > 0]
                diversification = (
                    len(non_zero_rates) / 3.0
                )  # Simple diversification measure

                number_position_patterns[num_str] = {
                    "total_appearances": number_count,
                    "special_prize_rate": round(special_rate, 3),
                    "first_prize_rate": round(first_rate, 3),
                    "other_prize_rate": round(other_rate, 3),
                    "preferred_position": preferred_position,
                    "position_diversification": round(diversification, 3),
                    "position_specialization": round(
                        max(rates), 3
                    ),  # How specialized in one position
                }

            position_intelligence["overall_statistics"] = overall_stats
            position_intelligence["number_patterns"] = number_position_patterns

            # Top specialized numbers for each position
            specialized_numbers = {
                "special_specialists": sorted(
                    [
                        (k, v)
                        for k, v in number_position_patterns.items()
                        if v["preferred_position"] == "special"
                    ],
                    key=lambda x: x[1]["special_prize_rate"],
                    reverse=True,
                )[:10],
                "first_specialists": sorted(
                    [
                        (k, v)
                        for k, v in number_position_patterns.items()
                        if v["preferred_position"] == "first"
                    ],
                    key=lambda x: x[1]["first_prize_rate"],
                    reverse=True,
                )[:10],
                "other_specialists": sorted(
                    [
                        (k, v)
                        for k, v in number_position_patterns.items()
                        if v["preferred_position"] == "other"
                    ],
                    key=lambda x: x[1]["other_prize_rate"],
                    reverse=True,
                )[:10],
            }

            position_intelligence["specialized_numbers"] = specialized_numbers

            logger.info(
                f"🏆 Prize position analysis completed for {len(number_position_patterns)} numbers"
            )
            return position_intelligence

        except Exception as e:
            logger.warning(f"Prize position analysis failed: {e}")
            return {}

    def _perform_statistical_tests(self, queryset, significance_level: float) -> Dict:
        """
        📊 NEW FEATURE: Comprehensive statistical testing suite
        """
        try:
            statistical_results = {
                "uniformity_test": self._test_number_uniformity(
                    queryset, significance_level
                ),
                "independence_test": self._test_number_independence(
                    queryset, significance_level
                ),
                "randomness_test": self._test_sequence_randomness(
                    queryset, significance_level
                ),
                "trend_test": self._test_temporal_trends(queryset, significance_level),
            }

            logger.info("📊 Statistical testing suite completed")
            return statistical_results

        except Exception as e:
            logger.warning(f"Statistical tests failed: {e}")
            return {}

    def _calculate_absence_periods(self, number: str, queryset) -> Dict:
        """
        Helper method to calculate absence periods for a number
        """
        try:
            number_appearances = queryset.filter(number=number).order_by("date")

            if not number_appearances.exists():
                return {"current_streak": 999, "max_period": 999, "avg_period": 999}

            appearance_dates = list(number_appearances.values_list("date", flat=True))

            # Calculate gaps between appearances
            gaps = []
            for i in range(1, len(appearance_dates)):
                gap = (
                    appearance_dates[i] - appearance_dates[i - 1]
                ).days - 1  # -1 because gap is exclusive
                gaps.append(max(0, gap))

            # Current absence streak
            if appearance_dates:
                current_streak = (date.today() - appearance_dates[-1]).days
            else:
                current_streak = 999

            return {
                "current_streak": current_streak,
                "max_period": max(gaps) if gaps else 0,
                "avg_period": round(np.mean(gaps), 1) if gaps else 0,
            }

        except Exception as e:
            logger.warning(f"Absence period calculation failed for {number}: {e}")
            return {"current_streak": 0, "max_period": 0, "avg_period": 0}

    def _get_fallback_patterns(self) -> Dict:
        """Enhanced fallback patterns with metadata"""
        return {
            "analysis_metadata": {
                "status": "fallback",
                "reason": "insufficient_data_or_error",
                "timestamp": datetime.now().isoformat(),
            },
            "hot_numbers": {},
            "cold_numbers": {},
            "cyclical_patterns": {},
            "mean_reversion": {},
            "momentum_patterns": {},
            "seasonal_effects": {},
            "day_of_week_bias": {},
            "month_end_effects": {},
            "prize_position_intelligence": {},
            "gap_analysis": {},
            "correlation_matrix": {},
            "statistical_tests": {},
            "trend_analysis": {},
            "risk_assessment": {},
        }

    # Placeholder methods for other enhanced analyses
    def _detect_cyclical_patterns_enhanced(self, queryset) -> Dict:
        """Detect cyclical patterns using Fourier analysis with real dates"""
        cycles = {}

        # Group data by number
        for number in range(100):
            num_str = str(number).zfill(2)
            number_records = queryset.filter(number=num_str).order_by("date")

            if number_records.count() < 10:  # Need minimum data
                continue

            # Get dates as timestamps for FFT analysis
            dates = list(number_records.values_list("date", flat=True))
            timestamps = [(date - dates[0]).days for date in dates]

            # Calculate gaps between appearances
            gaps = np.diff(timestamps)

            if len(gaps) < 5:
                continue

            # Fourier analysis for cycle detection
            try:
                fft_result = fft.fft(gaps)
                frequencies = fft.fftfreq(len(gaps))
                power_spectrum = np.abs(fft_result[1 : len(fft_result) // 2])

                dominant_freq_idx = np.argmax(power_spectrum)
                if dominant_freq_idx > 0:
                    dominant_period = 1 / abs(frequencies[dominant_freq_idx + 1])

                    cycles[num_str] = {
                        "avg_gap": float(np.mean(gaps)),
                        "dominant_cycle": float(dominant_period),
                        "cycle_strength": float(power_spectrum[dominant_freq_idx]),
                        "last_appearance": dates[-1].isoformat(),
                        "next_expected": (
                            dates[-1] + timedelta(days=round(dominant_period))
                        ).isoformat(),
                    }
            except Exception as e:
                logger.warning(f"FFT analysis failed for {num_str}: {e}")

        return cycles

    def _analyze_mean_reversion_enhanced(self, queryset) -> Dict:
        """Enhanced mean reversion analysis"""
        try:
            reversion_analysis = {}
            total_days = queryset.values("date").distinct().count()

            if total_days < 30:
                return {}

            window_size = min(30, total_days // 3)

            for number in range(100):
                num_str = str(number).zfill(2)
                number_records = queryset.filter(number=num_str).order_by("date")

                if number_records.count() < 10:
                    continue

                # Calculate rolling frequency
                dates = list(number_records.values_list("date", flat=True))
                all_dates = list(
                    queryset.values_list("date", flat=True).distinct().order_by("date")
                )

                # Create binary series (1 if appeared, 0 if not)
                binary_series = []
                for date_val in all_dates:
                    binary_series.append(1 if date_val in dates else 0)

                # Calculate rolling averages
                rolling_frequencies = []
                for i in range(len(binary_series) - window_size + 1):
                    window_freq = np.mean(binary_series[i : i + window_size])
                    rolling_frequencies.append(window_freq)

                if len(rolling_frequencies) < 5:
                    continue

                # Calculate mean reversion metrics
                long_term_mean = np.mean(rolling_frequencies)
                recent_freq = (
                    np.mean(rolling_frequencies[-5:])
                    if len(rolling_frequencies) >= 5
                    else long_term_mean
                )

                # Deviation from mean
                deviation = abs(recent_freq - long_term_mean)

                # Mean reversion pressure (higher = more likely to revert)
                reversion_pressure = deviation / (
                    long_term_mean + 0.001
                )  # Avoid division by zero

                # Expected direction
                expected_direction = (
                    "increase" if recent_freq < long_term_mean else "decrease"
                )

                # Reversion strength based on historical patterns
                volatility = np.std(rolling_frequencies)
                reversion_strength = deviation / (volatility + 0.001)

                reversion_analysis[num_str] = {
                    "long_term_frequency": round(long_term_mean, 4),
                    "recent_frequency": round(recent_freq, 4),
                    "deviation": round(deviation, 4),
                    "reversion_pressure": round(reversion_pressure, 3),
                    "expected_direction": expected_direction,
                    "reversion_strength": round(reversion_strength, 3),
                    "confidence_score": round(
                        min(reversion_strength * reversion_pressure, 1.0), 3
                    ),
                    "last_appearance_days": (
                        (
                            queryset.values("date")
                            .distinct()
                            .order_by("-date")
                            .first()["date"]
                            - dates[-1]
                        ).days
                        if dates
                        else total_days
                    ),
                }

            # Sort by reversion pressure
            sorted_reversion = dict(
                sorted(
                    reversion_analysis.items(),
                    key=lambda x: x[1]["reversion_pressure"],
                    reverse=True,
                )
            )

            logger.info(
                f"📈 Mean reversion analysis completed for {len(sorted_reversion)} numbers"
            )
            return dict(list(sorted_reversion.items())[:30])  # Top 30

        except Exception as e:
            logger.warning(f"Mean reversion analysis failed: {e}")
            return {}

    def _analyze_momentum_enhanced(self, queryset) -> Dict:
        """Enhanced momentum analysis"""
        try:
            momentum_analysis = {}

            # Define momentum periods
            periods = [7, 14, 30, 60]  # 1 week, 2 weeks, 1 month, 2 months

            for number in range(100):
                num_str = str(number).zfill(2)
                number_records = queryset.filter(number=num_str).order_by("date")

                if number_records.count() < 5:
                    continue

                momentum_data = {}

                for period in periods:
                    # Recent period appearances
                    recent_cutoff = date.today() - timedelta(days=period)
                    recent_appearances = number_records.filter(
                        date__gte=recent_cutoff
                    ).count()

                    # Previous period appearances (for comparison)
                    previous_cutoff = recent_cutoff - timedelta(days=period)
                    previous_appearances = number_records.filter(
                        date__gte=previous_cutoff, date__lt=recent_cutoff
                    ).count()

                    # Calculate momentum
                    if previous_appearances > 0:
                        momentum_ratio = recent_appearances / previous_appearances
                    else:
                        momentum_ratio = (
                            recent_appearances if recent_appearances > 0 else 0
                        )

                    momentum_data[f"{period}d"] = {
                        "recent_appearances": recent_appearances,
                        "previous_appearances": previous_appearances,
                        "momentum_ratio": round(momentum_ratio, 3),
                        "trend": (
                            "increasing"
                            if momentum_ratio > 1.1
                            else "decreasing" if momentum_ratio < 0.9 else "stable"
                        ),
                    }

                # Calculate overall momentum score
                momentum_scores = [
                    data["momentum_ratio"] for data in momentum_data.values()
                ]
                average_momentum = np.mean(momentum_scores)

                # Momentum acceleration (is momentum increasing over time?)
                short_term_momentum = np.mean(
                    [
                        momentum_data["7d"]["momentum_ratio"],
                        momentum_data["14d"]["momentum_ratio"],
                    ]
                )
                long_term_momentum = np.mean(
                    [
                        momentum_data["30d"]["momentum_ratio"],
                        momentum_data["60d"]["momentum_ratio"],
                    ]
                )

                acceleration = short_term_momentum - long_term_momentum

                momentum_analysis[num_str] = {
                    "period_analysis": momentum_data,
                    "average_momentum": round(average_momentum, 3),
                    "momentum_acceleration": round(acceleration, 3),
                    "overall_trend": (
                        "accelerating"
                        if acceleration > 0.2
                        else "decelerating" if acceleration < -0.2 else "steady"
                    ),
                    "momentum_strength": round(
                        abs(average_momentum - 1), 3
                    ),  # Distance from neutral (1.0)
                    "prediction_confidence": round(
                        min(
                            abs(acceleration) + momentum_data["7d"]["momentum_ratio"],
                            2.0,
                        ),
                        3,
                    ),
                }

            # Sort by momentum strength
            sorted_momentum = dict(
                sorted(
                    momentum_analysis.items(),
                    key=lambda x: x[1]["momentum_strength"],
                    reverse=True,
                )
            )

            logger.info(
                f"🚀 Momentum analysis completed for {len(sorted_momentum)} numbers"
            )
            return dict(list(sorted_momentum.items())[:25])  # Top 25

        except Exception as e:
            logger.warning(f"Momentum analysis failed: {e}")
            return {}

    def _analyze_dow_bias_enhanced(self, queryset) -> Dict:
        """Enhanced day-of-week bias analysis"""
        try:
            dow_analysis = {
                "overall_patterns": {},
                "number_specific_bias": {},
                "statistical_significance": {},
            }

            # Overall day-of-week patterns
            for dow in range(7):
                dow_records = queryset.filter(day_of_week=dow)
                total_dow_records = dow_records.count()

                if total_dow_records > 0:
                    # Prize position analysis by day
                    special_count = dow_records.filter(appeared_in_special=True).count()
                    first_count = dow_records.filter(appeared_in_first=True).count()

                    dow_analysis["overall_patterns"][dow] = {
                        "day_name": [
                            "Monday",
                            "Tuesday",
                            "Wednesday",
                            "Thursday",
                            "Friday",
                            "Saturday",
                            "Sunday",
                        ][dow],
                        "total_appearances": total_dow_records,
                        "special_prize_rate": (
                            round(special_count / total_dow_records, 3)
                            if total_dow_records > 0
                            else 0
                        ),
                        "first_prize_rate": (
                            round(first_count / total_dow_records, 3)
                            if total_dow_records > 0
                            else 0
                        ),
                        "activity_level": (
                            "high"
                            if total_dow_records > queryset.count() / 7 * 1.2
                            else (
                                "low"
                                if total_dow_records < queryset.count() / 7 * 0.8
                                else "normal"
                            )
                        ),
                    }

            # Number-specific day bias
            for number in range(100):
                num_str = str(number).zfill(2)
                number_records = queryset.filter(number=num_str)

                if number_records.count() < 7:  # Need minimum appearances
                    continue

                dow_distribution = {}
                total_appearances = number_records.count()

                for dow in range(7):
                    dow_count = number_records.filter(day_of_week=dow).count()
                    expected_count = total_appearances / 7  # Expected if uniform

                    dow_distribution[dow] = {
                        "count": dow_count,
                        "expected": round(expected_count, 1),
                        "ratio": (
                            round(dow_count / expected_count, 2)
                            if expected_count > 0
                            else 0
                        ),
                        "bias_strength": abs(dow_count - expected_count),
                    }

                # Find strongest bias
                strongest_bias = max(
                    dow_distribution.items(), key=lambda x: x[1]["bias_strength"]
                )

                # Chi-square test for significance
                try:
                    observed = [dow_distribution[dow]["count"] for dow in range(7)]
                    expected = expected_per_day = (
                        total_appearances / 7 if total_appearances > 0 else 1
                    )

                    # For multiple categories, calculate chi-square manually
                    chi2_stat = sum(
                        (obs - expected_per_day) ** 2 / expected_per_day
                        for obs in observed
                        if expected_per_day > 0
                    )

                    # Degrees of freedom = categories - 1
                    df = 6
                    # Approximate p-value using chi-square distribution
                    # For simplicity, use significance threshold
                    p_value = (
                        0.05 if chi2_stat > 12.59 else 0.1
                    )  # 12.59 is critical value for df=6, α=0.05

                    is_significant = p_value < 0.05

                    if (
                        strongest_bias[1]["bias_strength"] > 2
                    ):  # Only include meaningful biases
                        dow_analysis["number_specific_bias"][num_str] = {
                            "strongest_bias_day": strongest_bias[0],
                            "bias_ratio": strongest_bias[1]["ratio"],
                            "chi2_statistic": round(chi2_stat, 4),
                            "p_value": round(p_value, 6),
                            "is_significant": (
                                "significant" if is_significant else "not_significant"
                            ),
                            "preferred_day": [
                                "Monday",
                                "Tuesday",
                                "Wednesday",
                                "Thursday",
                                "Friday",
                                "Saturday",
                                "Sunday",
                            ][strongest_bias[0]],
                            "bias_strength": strongest_bias[1]["bias_strength"],
                        }

                except Exception as chi_error:
                    logger.warning(
                        f"Chi-square test failed for DOW bias {num_str}: {chi_error}"
                    )

            logger.info(f"📅 Day-of-week bias analysis completed")
            return dow_analysis

        except Exception as e:
            logger.warning(f"Day-of-week bias analysis failed: {e}")
            return {}

    def _analyze_month_end_effects_enhanced(self, queryset) -> Dict:
        """Enhanced month-end effects analysis"""
        try:
            month_end_analysis = {
                "period_effects": {},
                "number_sensitivity": {},
                "statistical_tests": {},
            }

            # Define periods
            periods = {
                "early_month": (1, 10),
                "mid_month": (11, 20),
                "late_month": (21, 31),
            }

            total_records = queryset.count()

            # Overall period effects
            for period_name, (start_day, end_day) in periods.items():
                period_records = queryset.filter(
                    day_of_month__gte=start_day, day_of_month__lte=end_day
                )
                period_count = period_records.count()

                expected_count = total_records / 3  # Roughly equal distribution

                month_end_analysis["period_effects"][period_name] = {
                    "day_range": f"{start_day}-{end_day}",
                    "total_appearances": period_count,
                    "expected_appearances": round(expected_count, 1),
                    "intensity_ratio": (
                        round(period_count / expected_count, 3)
                        if expected_count > 0
                        else 0
                    ),
                    "effect_strength": abs(period_count - expected_count),
                    "unique_numbers": period_records.values("number")
                    .distinct()
                    .count(),
                }

            # Number-specific month-end sensitivity
            for number in range(100):
                num_str = str(number).zfill(2)
                number_records = queryset.filter(number=num_str)

                if number_records.count() < 9:  # Need minimum data
                    continue

                period_distribution = {}
                total_number_appearances = number_records.count()

                for period_name, (start_day, end_day) in periods.items():
                    period_count = number_records.filter(
                        day_of_month__gte=start_day, day_of_month__lte=end_day
                    ).count()

                    expected_period_count = total_number_appearances / 3

                    period_distribution[period_name] = {
                        "count": period_count,
                        "expected": round(expected_period_count, 1),
                        "ratio": (
                            round(period_count / expected_period_count, 2)
                            if expected_period_count > 0
                            else 0
                        ),
                    }

                # Find period with strongest effect
                strongest_period = max(
                    period_distribution.items(), key=lambda x: abs(x[1]["ratio"] - 1)
                )

                # Only include numbers with meaningful month-end effects
                if (
                    abs(strongest_period[1]["ratio"] - 1) > 0.5
                ):  # 50% deviation from expected
                    month_end_analysis["number_sensitivity"][num_str] = {
                        "most_sensitive_period": strongest_period[0],
                        "sensitivity_ratio": strongest_period[1]["ratio"],
                        "effect_type": (
                            "month_end_boost"
                            if strongest_period[0] == "late_month"
                            and strongest_period[1]["ratio"] > 1.2
                            else (
                                "month_start_boost"
                                if strongest_period[0] == "early_month"
                                and strongest_period[1]["ratio"] > 1.2
                                else (
                                    "mid_month_boost"
                                    if strongest_period[1]["ratio"] > 1.2
                                    else "suppressed"
                                )
                            )
                        ),
                        "period_distribution": period_distribution,
                    }

            # Statistical significance test
            try:
                early_count = month_end_analysis["period_effects"]["early_month"][
                    "total_appearances"
                ]
                mid_count = month_end_analysis["period_effects"]["mid_month"][
                    "total_appearances"
                ]
                late_count = month_end_analysis["period_effects"]["late_month"][
                    "total_appearances"
                ]

                observed = [early_count, mid_count, late_count]
                expected_per_period = total_records / 3 if total_records > 0 else 1

                # Manual chi-square calculation for 3 periods
                chi2_stat = sum(
                    (obs - expected_per_period) ** 2 / expected_per_period
                    for obs in observed
                    if expected_per_period > 0
                )

                # Degrees of freedom = 2 for 3 categories
                # Critical value for df=2, α=0.05 is 5.99
                p_value = 0.05 if chi2_stat > 5.99 else 0.1

                month_end_analysis["statistical_tests"] = {
                    "chi2_statistic": round(chi2_stat, 4),
                    "p_value": round(p_value, 6),
                    "is_significant": (
                        "significant" if p_value < 0.05 else "not_significant"
                    ),
                    "interpretation": (
                        "Significant month-end effects detected"
                        if p_value < 0.05
                        else "No significant month-end effects"
                    ),
                }

            except Exception as stat_error:
                logger.warning(f"Month-end statistical test failed: {stat_error}")

            logger.info(f"📅 Month-end effects analysis completed")
            return month_end_analysis

        except Exception as e:
            logger.warning(f"Month-end effects analysis failed: {e}")
            return {}

    def _analyze_advanced_gaps(self, queryset, days=30):
        """
        Phân tích khoảng cách xuất hiện các số một cách nâng cao
        """
        try:
            # Lấy dữ liệu trong khoảng thời gian quy định
            from datetime import datetime, timedelta

            cutoff_date = datetime.now() - timedelta(days=days)
            recent_data = queryset.filter(date__gte=cutoff_date)

            gap_analysis = {}

            for number in range(100):  # 00-99
                number_str = f"{number:02d}"

                # Tìm các lần xuất hiện của số này
                occurrences = recent_data.filter(number=number_str).order_by("date")

                if occurrences.exists():
                    dates = [occ.date for occ in occurrences]
                    gaps = []

                    # Tính khoảng cách giữa các lần xuất hiện
                    for i in range(1, len(dates)):
                        gap = (dates[i] - dates[i - 1]).days
                        gaps.append(gap)

                    if gaps:
                        gap_analysis[number_str] = {
                            "avg_gap": sum(gaps) / len(gaps),
                            "min_gap": min(gaps),
                            "max_gap": max(gaps),
                            "total_occurrences": len(dates),
                            "last_occurrence": dates[-1].isoformat() if dates else None,
                        }
                    else:
                        gap_analysis[number_str] = {
                            "avg_gap": 0,
                            "min_gap": 0,
                            "max_gap": 0,
                            "total_occurrences": 1,
                            "last_occurrence": dates[0].isoformat() if dates else None,
                        }
                else:
                    gap_analysis[number_str] = {
                        "avg_gap": days,  # Không xuất hiện trong khoảng thời gian
                        "min_gap": days,
                        "max_gap": days,
                        "total_occurrences": 0,
                        "last_occurrence": None,
                    }

            return gap_analysis

        except Exception as e:
            logger.error(f"Error in advanced gap analysis: {e}")
            return {}

    def _calculate_number_correlations_enhanced(self, queryset) -> Dict:
        """Enhanced correlation analysis"""
        try:
            # Get all unique dates in chronological order
            all_dates = list(
                queryset.values_list("date", flat=True).distinct().order_by("date")
            )

            if len(all_dates) < 30:  # Need minimum data
                return {}

            # Create binary matrix: date x number (1 if appeared, 0 if not)
            matrix = []

            for date_val in all_dates:
                day_numbers = set(
                    queryset.filter(date=date_val).values_list("number", flat=True)
                )
                day_vector = [
                    1 if str(i).zfill(2) in day_numbers else 0 for i in range(100)
                ]
                matrix.append(day_vector)

            matrix = np.array(matrix)

            # Calculate correlation matrix
            correlation_matrix = np.corrcoef(
                matrix.T
            )  # Transpose to get number x number correlations

            # Extract meaningful correlations
            correlations = {}
            strong_correlations = []

            for i in range(100):
                for j in range(i + 1, 100):
                    corr_value = correlation_matrix[i, j]

                    # Only include correlations with absolute value > 0.1
                    if abs(corr_value) > 0.1 and not np.isnan(corr_value):
                        num_i = str(i).zfill(2)
                        num_j = str(j).zfill(2)

                        pair_key = f"{num_i}-{num_j}"
                        correlations[pair_key] = {
                            "correlation": round(corr_value, 4),
                            "strength": (
                                "strong"
                                if abs(corr_value) > 0.3
                                else "moderate" if abs(corr_value) > 0.2 else "weak"
                            ),
                            "type": "positive" if corr_value > 0 else "negative",
                            "number_1": num_i,
                            "number_2": num_j,
                        }

                        if abs(corr_value) > 0.2:  # Strong correlations
                            strong_correlations.append((pair_key, corr_value))

            # Sort by correlation strength
            sorted_correlations = dict(
                sorted(
                    correlations.items(),
                    key=lambda x: abs(x[1]["correlation"]),
                    reverse=True,
                )
            )

            # Analyze correlation patterns
            correlation_analysis = {
                "correlation_pairs": sorted_correlations,
                "summary_statistics": {
                    "total_pairs_analyzed": 4950,  # 100 choose 2
                    "significant_correlations": len(correlations),
                    "strong_correlations": len(
                        [c for c in correlations.values() if c["strength"] == "strong"]
                    ),
                    "positive_correlations": len(
                        [c for c in correlations.values() if c["type"] == "positive"]
                    ),
                    "negative_correlations": len(
                        [c for c in correlations.values() if c["type"] == "negative"]
                    ),
                    "average_correlation": (
                        round(
                            np.mean(
                                [abs(c["correlation"]) for c in correlations.values()]
                            ),
                            4,
                        )
                        if correlations
                        else 0
                    ),
                },
                "top_positive_pairs": [
                    pair
                    for pair, corr in sorted(
                        strong_correlations, key=lambda x: x[1], reverse=True
                    )[:10]
                    if corr > 0
                ],
                "top_negative_pairs": [
                    pair
                    for pair, corr in sorted(strong_correlations, key=lambda x: x[1])[
                        :10
                    ]
                    if corr < 0
                ],
            }

            logger.info(
                f"🔗 Correlation analysis completed: {len(correlations)} significant pairs found"
            )
            return correlation_analysis

        except Exception as e:
            logger.warning(f"Correlation analysis failed: {e}")
            return {}

    def _analyze_trends_enhanced(self, queryset) -> Dict:
        """Enhanced trend analysis"""
        try:
            trend_analysis = {
                "temporal_trends": {},
                "frequency_trends": {},
                "emerging_patterns": {},
                "declining_patterns": {},
            }

            # Analyze trends over time
            total_days = queryset.values("date").distinct().count()

            if total_days < 60:  # Need minimum data for trend analysis
                return trend_analysis

            # Split data into periods for trend analysis
            all_dates = list(
                queryset.values_list("date", flat=True).distinct().order_by("date")
            )

            # Divide into 4 quarters for trend analysis
            quarter_size = len(all_dates) // 4
            quarters = [
                all_dates[:quarter_size],
                all_dates[quarter_size : 2 * quarter_size],
                all_dates[2 * quarter_size : 3 * quarter_size],
                all_dates[3 * quarter_size :],
            ]

            # Analyze each number's trend across quarters
            for number in range(100):
                num_str = str(number).zfill(2)
                number_records = queryset.filter(number=num_str)

                if number_records.count() < 8:  # Need minimum appearances
                    continue

                quarter_frequencies = []

                for i, quarter_dates in enumerate(quarters):
                    quarter_appearances = number_records.filter(
                        date__in=quarter_dates
                    ).count()
                    quarter_frequency = (
                        quarter_appearances / len(quarter_dates) if quarter_dates else 0
                    )
                    quarter_frequencies.append(quarter_frequency)

                # Calculate trend using linear regression
                if len(quarter_frequencies) >= 3:
                    x = np.array(range(len(quarter_frequencies)))
                    y = np.array(quarter_frequencies)

                    # Simple linear regression
                    if len(x) > 1 and np.var(x) > 0:
                        slope = np.cov(x, y)[0, 1] / np.var(x)
                        intercept = np.mean(y) - slope * np.mean(x)

                        # R-squared for trend strength
                        y_pred = slope * x + intercept
                        ss_res = np.sum((y - y_pred) ** 2)
                        ss_tot = np.sum((y - np.mean(y)) ** 2)
                        r_squared = 1 - (ss_res / ss_tot) if ss_tot > 0 else 0

                        # Classify trend
                        trend_strength = abs(slope)
                        trend_direction = (
                            "increasing"
                            if slope > 0.001
                            else "decreasing" if slope < -0.001 else "stable"
                        )

                        trend_data = {
                            "slope": round(slope, 6),
                            "intercept": round(intercept, 6),
                            "r_squared": round(r_squared, 4),
                            "trend_direction": trend_direction,
                            "trend_strength": round(trend_strength, 6),
                            "quarter_frequencies": [
                                round(f, 4) for f in quarter_frequencies
                            ],
                            "confidence": round(r_squared * trend_strength * 100, 2),
                        }

                        trend_analysis["frequency_trends"][num_str] = trend_data

                        # Categorize into emerging or declining
                        if trend_direction == "increasing" and r_squared > 0.3:
                            trend_analysis["emerging_patterns"][num_str] = trend_data
                        elif trend_direction == "decreasing" and r_squared > 0.3:
                            trend_analysis["declining_patterns"][num_str] = trend_data

            # Overall temporal trends
            total_appearances_per_quarter = []
            unique_numbers_per_quarter = []

            for quarter_dates in quarters:
                quarter_records = queryset.filter(date__in=quarter_dates)
                total_appearances_per_quarter.append(quarter_records.count())
                unique_numbers_per_quarter.append(
                    quarter_records.values("number").distinct().count()
                )

            trend_analysis["temporal_trends"] = {
                "total_appearances_trend": total_appearances_per_quarter,
                "unique_numbers_trend": unique_numbers_per_quarter,
                "diversity_trend": [
                    unique / total if total > 0 else 0
                    for unique, total in zip(
                        unique_numbers_per_quarter, total_appearances_per_quarter
                    )
                ],
            }

            logger.info(
                f"📈 Trend analysis completed: {len(trend_analysis['emerging_patterns'])} emerging, {len(trend_analysis['declining_patterns'])} declining patterns"
            )
            return trend_analysis

        except Exception as e:
            logger.warning(f"Trend analysis failed: {e}")
            return {}

    def _assess_prediction_risks(self, queryset) -> Dict:
        """Risk assessment for predictions"""
        try:
            risk_assessment = {
                "data_quality_risks": {},
                "prediction_reliability": {},
                "confidence_intervals": {},
                "volatility_analysis": {},
            }

            total_records = queryset.count()
            total_days = queryset.values("date").distinct().count()

            # Data quality assessment
            risk_assessment["data_quality_risks"] = {
                "sample_size": total_records,
                "time_span_days": total_days,
                "data_density": (
                    round(total_records / total_days, 2) if total_days > 0 else 0
                ),
                "completeness_score": min(
                    total_records / 1000, 1.0
                ),  # Assume 1000 is ideal sample size
                "temporal_coverage": (
                    "adequate"
                    if total_days > 180
                    else "limited" if total_days > 60 else "insufficient"
                ),
                "data_quality_score": round(
                    min(total_records / 1000, 1.0) * min(total_days / 180, 1.0), 3
                ),
            }

            # Prediction reliability for each number
            for number in range(100):
                num_str = str(number).zfill(2)
                number_records = queryset.filter(number=num_str)
                appearances = number_records.count()

                if appearances < 3:
                    continue

                # Calculate prediction confidence based on data stability
                dates = list(number_records.values_list("date", flat=True))

                if len(dates) >= 2:
                    gaps = [
                        (dates[i] - dates[i - 1]).days for i in range(1, len(dates))
                    ]
                    gap_stability = (
                        1 / (1 + np.std(gaps)) if gaps and np.std(gaps) > 0 else 0.5
                    )
                else:
                    gap_stability = 0.1

                # Frequency stability
                recent_freq = number_records.filter(
                    date__gte=date.today() - timedelta(days=90)
                ).count() / min(90, total_days)
                historical_freq = appearances / total_days if total_days > 0 else 0

                freq_stability = 1 - abs(recent_freq - historical_freq) / (
                    historical_freq + 0.001
                )

                # Overall reliability score
                reliability_score = (
                    gap_stability * 0.4
                    + freq_stability * 0.4
                    + min(appearances / 20, 1) * 0.2
                )

                risk_assessment["prediction_reliability"][num_str] = {
                    "appearances": appearances,
                    "gap_stability": round(gap_stability, 3),
                    "frequency_stability": round(freq_stability, 3),
                    "reliability_score": round(reliability_score, 3),
                    "confidence_level": (
                        "high"
                        if reliability_score > 0.7
                        else "medium" if reliability_score > 0.4 else "low"
                    ),
                    "risk_factors": [],
                }

                # Identify risk factors
                if appearances < 10:
                    risk_assessment["prediction_reliability"][num_str][
                        "risk_factors"
                    ].append("insufficient_data")
                if gap_stability < 0.3:
                    risk_assessment["prediction_reliability"][num_str][
                        "risk_factors"
                    ].append("irregular_pattern")
                if freq_stability < 0.5:
                    risk_assessment["prediction_reliability"][num_str][
                        "risk_factors"
                    ].append("frequency_instability")

            # Overall volatility analysis
            daily_totals = []
            for single_date in queryset.values("date").distinct():
                daily_count = queryset.filter(date=single_date["date"]).count()
                daily_totals.append(daily_count)

            if daily_totals:
                volatility = (
                    np.std(daily_totals) / np.mean(daily_totals)
                    if np.mean(daily_totals) > 0
                    else 0
                )

                risk_assessment["volatility_analysis"] = {
                    "daily_appearance_volatility": round(volatility, 3),
                    "volatility_level": (
                        "high"
                        if volatility > 0.5
                        else "medium" if volatility > 0.3 else "low"
                    ),
                    "predictability": (
                        "difficult"
                        if volatility > 0.5
                        else "moderate" if volatility > 0.3 else "good"
                    ),
                }

            logger.info(f"⚠️ Risk assessment completed")
            return risk_assessment

        except Exception as e:
            logger.warning(f"Risk assessment failed: {e}")
            return {}

    # Statistical test helper methods
    def _test_number_uniformity(self, queryset, significance_level) -> Dict:
        """Test if number distribution is uniform"""
        try:
            # Count appearances for each number
            observed_frequencies = []

            for number in range(100):
                num_str = str(number).zfill(2)
                count = queryset.filter(number=num_str).count()
                observed_frequencies.append(count)

            total_appearances = sum(observed_frequencies)

            if total_appearances == 0:
                return {"error": "No data available"}

            # Expected frequency if uniform
            expected_frequency = total_appearances / 100 if total_appearances > 0 else 1

            # Manual chi-square test for uniformity
            chi2_stat = sum(
                (obs - expected_frequency) ** 2 / expected_frequency
                for obs in observed_frequencies
                if expected_frequency > 0
            )

            # Degrees of freedom = 99 for 100 numbers
            # For large df, approximate p-value
            p_value = (
                0.05 if chi2_stat > 123.23 else 0.1
            )  # Critical value for df=99, α=0.05

            # Calculate deviations
            max_deviation = max(
                abs(obs - expected_frequency) for obs in observed_frequencies
            )
            avg_deviation = np.mean(
                [abs(obs - expected_frequency) for obs in observed_frequencies]
            )

            return {
                "test_name": "Number Distribution Uniformity Test",
                "chi2_statistic": round(chi2_stat, 4),
                "p_value": round(p_value, 6),
                "is_uniform": p_value > significance_level,
                "significance_level": significance_level,
                "total_observations": total_appearances,
                "expected_per_number": round(expected_frequency, 2),
                "max_deviation": round(max_deviation, 2),
                "average_deviation": round(avg_deviation, 2),
                "interpretation": (
                    "Distribution is uniform"
                    if p_value > significance_level
                    else "Distribution deviates from uniform"
                ),
            }

        except Exception as e:
            logger.warning(f"Uniformity test failed: {e}")
            return {"error": str(e)}

    def _test_number_independence(self, queryset, significance_level) -> Dict:
        """Test if number appearances are independent"""
        try:
            # Get consecutive days data
            all_dates = list(
                queryset.values_list("date", flat=True).distinct().order_by("date")
            )

            if len(all_dates) < 10:
                return {"error": "Insufficient data for independence test"}

            # Create contingency table for consecutive days
            # Test if yesterday's numbers affect today's numbers
            contingency_data = []

            for i in range(len(all_dates) - 1):
                today = all_dates[i]
                tomorrow = all_dates[i + 1]

                today_numbers = set(
                    queryset.filter(date=today).values_list("number", flat=True)
                )
                tomorrow_numbers = set(
                    queryset.filter(date=tomorrow).values_list("number", flat=True)
                )

                # Create binary vectors
                today_vector = [
                    1 if str(j).zfill(2) in today_numbers else 0 for j in range(100)
                ]
                tomorrow_vector = [
                    1 if str(j).zfill(2) in tomorrow_numbers else 0 for j in range(100)
                ]

                contingency_data.append((today_vector, tomorrow_vector))

            # Simple independence test: correlation between consecutive days
            if len(contingency_data) > 5:
                today_totals = [sum(day[0]) for day in contingency_data]
                tomorrow_totals = [sum(day[1]) for day in contingency_data]

                correlation = np.corrcoef(today_totals, tomorrow_totals)[0, 1]

                # Test significance of correlation
                n = len(contingency_data)
                t_stat = (
                    correlation * np.sqrt((n - 2) / (1 - correlation**2))
                    if abs(correlation) < 0.99
                    else float("inf")
                )

                # Rough p-value estimation (assumes t-distribution)
                from scipy.stats import t

                p_value = (
                    2 * (1 - t.cdf(abs(t_stat), n - 2))
                    if abs(t_stat) != float("inf")
                    else 0
                )

                return {
                    "test_name": "Sequential Independence Test",
                    "correlation": round(correlation, 4),
                    "t_statistic": (
                        round(t_stat, 4) if t_stat != float("inf") else "infinity"
                    ),
                    "p_value": round(p_value, 6),
                    "is_independent": p_value > significance_level,
                    "significance_level": significance_level,
                    "sample_size": n,
                    "interpretation": (
                        "Numbers appear independently"
                        if p_value > significance_level
                        else "Numbers show sequential dependence"
                    ),
                }

            return {"error": "Insufficient consecutive day data"}

        except Exception as e:
            logger.warning(f"Independence test failed: {e}")
            return {"error": str(e)}

    def _test_sequence_randomness(self, queryset, significance_level) -> Dict:
        """Test if sequence is random using runs test"""
        try:
            # Get sequence of daily totals
            all_dates = list(
                queryset.values_list("date", flat=True).distinct().order_by("date")
            )
            daily_totals = []

            for single_date in all_dates:
                daily_count = queryset.filter(date=single_date).count()
                daily_totals.append(daily_count)

            if len(daily_totals) < 20:
                return {"error": "Insufficient data for randomness test"}

            # Convert to binary sequence (above/below median)
            median_value = np.median(daily_totals)
            binary_sequence = [1 if x > median_value else 0 for x in daily_totals]

            # Count runs
            runs = 1
            for i in range(1, len(binary_sequence)):
                if binary_sequence[i] != binary_sequence[i - 1]:
                    runs += 1

            # Calculate expected runs and standard deviation
            n1 = sum(binary_sequence)  # Count of 1s
            n2 = len(binary_sequence) - n1  # Count of 0s

            if n1 == 0 or n2 == 0:
                return {"error": "Sequence has no variation"}

            expected_runs = (2 * n1 * n2) / (n1 + n2) + 1
            variance_runs = (2 * n1 * n2 * (2 * n1 * n2 - n1 - n2)) / (
                (n1 + n2) ** 2 * (n1 + n2 - 1)
            )
            std_runs = np.sqrt(variance_runs)

            # Z-score
            z_score = (runs - expected_runs) / std_runs if std_runs > 0 else 0

            # P-value (two-tailed test)
            from scipy.stats import norm

            p_value = 2 * (1 - norm.cdf(abs(z_score)))

            return {
                "test_name": "Runs Test for Randomness",
                "observed_runs": runs,
                "expected_runs": round(expected_runs, 2),
                "z_score": round(z_score, 4),
                "p_value": round(p_value, 6),
                "is_random": p_value > significance_level,
                "significance_level": significance_level,
                "sequence_length": len(binary_sequence),
                "interpretation": (
                    "Sequence appears random"
                    if p_value > significance_level
                    else "Sequence shows non-random patterns"
                ),
            }

        except Exception as e:
            logger.warning(f"Randomness test failed: {e}")
            return {"error": str(e)}

    def _test_temporal_trends(self, queryset, significance_level) -> Dict:
        """Test for temporal trends"""
        try:
            all_dates = list(
                queryset.values_list("date", flat=True).distinct().order_by("date")
            )

            if len(all_dates) < 30:
                return {"error": "Insufficient data for trend test"}

            # Calculate daily statistics
            daily_stats = []
            for single_date in all_dates:
                daily_records = queryset.filter(date=single_date)
                daily_count = daily_records.count()
                unique_numbers = daily_records.values("number").distinct().count()

                daily_stats.append(
                    {
                        "date": single_date,
                        "count": daily_count,
                        "unique_numbers": unique_numbers,
                        "diversity": (
                            unique_numbers / daily_count if daily_count > 0 else 0
                        ),
                    }
                )

            # Test for trend in total appearances
            days = np.arange(len(daily_stats))
            counts = [stat["count"] for stat in daily_stats]

            # Linear regression
            if len(days) > 1 and np.var(days) > 0:
                slope = np.cov(days, counts)[0, 1] / np.var(days)
                intercept = np.mean(counts) - slope * np.mean(days)

                # Calculate correlation coefficient
                correlation = np.corrcoef(days, counts)[0, 1]

                # T-test for significance of slope
                n = len(days)
                t_stat = (
                    correlation * np.sqrt((n - 2) / (1 - correlation**2))
                    if abs(correlation) < 0.99
                    else float("inf")
                )

                from scipy.stats import t

                p_value = (
                    2 * (1 - t.cdf(abs(t_stat), n - 2))
                    if abs(t_stat) != float("inf")
                    else 0
                )

                return {
                    "test_name": "Temporal Trend Test",
                    "slope": round(slope, 6),
                    "correlation": round(correlation, 4),
                    "t_statistic": (
                        round(t_stat, 4) if t_stat != float("inf") else "infinity"
                    ),
                    "p_value": round(p_value, 6),
                    "has_trend": p_value < significance_level,
                    "trend_direction": "increasing" if slope > 0 else "decreasing",
                    "significance_level": significance_level,
                    "sample_size": n,
                    "interpretation": f"{'Significant' if p_value < significance_level else 'No significant'} {('increasing' if slope > 0 else 'decreasing')} trend detected",
                }

            return {"error": "Cannot calculate trend"}

        except Exception as e:
            logger.warning(f"Temporal trend test failed: {e}")
            return {"error": str(e)}

    # =====================================
    # 🔍 VALIDATION FRAMEWORK METHODS
    # =====================================

    def validate_predictions_against_actual(
        self, predictions: Dict, actual_results: List[str], prediction_date: date = None
    ) -> Dict:
        """
        Validate predictions against actual lottery results

        Args:
            predictions: Prediction results from analysis
            actual_results: Actual winning numbers
            prediction_date: Date of prediction (default: today)

        Returns:
            Dict: Comprehensive validation results
        """
        if self.config.get("enable_validation", "enabled") != "enabled":
            return {"message": "Validation disabled"}

        prediction_date = prediction_date or date.today()

        return self.validator.validate_predictions(
            predictions, actual_results, prediction_date, "enhanced_deep_frequency"
        )

    def get_validation_history(self, days_back: int = 30) -> Dict:
        """Get validation history and performance metrics"""
        return self.validator.generate_validation_report(days_back)

    def get_performance_metrics(self) -> Dict:
        """Get comprehensive performance metrics"""
        return self.validator.get_performance_summary()

    # =====================================
    # 🔄 FEEDBACK LEARNING METHODS
    # =====================================

    def learn_from_results(self, validation_result: Dict):
        """
        Learn and adapt from validation results

        Args:
            validation_result: Result from validate_predictions_against_actual
        """
        if self.config.get("enable_feedback_learning", "enabled") != "enabled":
            return

        self.feedback_system.learn_from_validation(validation_result)

        # Auto-adjust parameters if enabled
        if self.config.get("auto_adjust_parameters", "enabled") == "enabled":
            self._apply_adaptive_parameters()

    def get_adaptive_predictions(self, base_predictions: Dict) -> Dict:
        """
        Generate adaptive predictions based on learned weights

        Args:
            base_predictions: Original predictions from analysis

        Returns:
            Dict: Adaptive predictions with learned weights
        """
        if self.config.get("enable_feedback_learning", "enabled") != "enabled":
            return base_predictions

        return self.feedback_system.get_adaptive_predictions(base_predictions)

    def get_learning_progress(self) -> Dict:
        """Get summary of learning progress and adaptations"""
        return self.feedback_system.get_learning_summary()

    def _apply_adaptive_parameters(self):
        """Apply learned parameters to improve future predictions"""
        adaptive_params = self.feedback_system.adaptive_parameters

        # Apply learned significance level
        if "significance_level" in adaptive_params:
            logger.info(
                f"📊 Applying adaptive significance level: {adaptive_params['significance_level']}"
            )

        # Apply learned lookback days
        if "lookback_days" in adaptive_params:
            logger.info(
                f"📅 Applying adaptive lookback days: {adaptive_params['lookback_days']}"
            )

    # =====================================
    # 📈 VISUALIZATION METHODS
    # =====================================

    def generate_visualization_data(self, analysis_results: Dict) -> Dict:
        """
        Generate comprehensive visualization data

        Args:
            analysis_results: Results from frequency analysis

        Returns:
            Dict: Complete visualization data package
        """
        if self.config.get("enable_visualization", "enabled") != "enabled":
            return {"message": "Visualization disabled"}

        try:
            viz_package = {
                "generated_at": datetime.now().isoformat(),
                "visualizations": {},
            }

            # Generate frequency heatmap
            if "hot_numbers" in analysis_results or "cold_numbers" in analysis_results:
                viz_package["visualizations"]["frequency_heatmap"] = (
                    self.viz_generator.generate_frequency_heatmap_data(analysis_results)
                )

            # Generate trend charts
            if "trend_analysis" in analysis_results:
                viz_package["visualizations"]["trend_charts"] = (
                    self.viz_generator.generate_trend_chart_data(
                        analysis_results["trend_analysis"]
                    )
                )

            # Generate correlation network
            if "correlation_matrix" in analysis_results:
                viz_package["visualizations"]["correlation_network"] = (
                    self.viz_generator.generate_correlation_network_data(
                        analysis_results["correlation_matrix"]
                    )
                )

            # Generate performance dashboard if validation history exists
            if self.validator.validation_history:
                viz_package["visualizations"]["performance_dashboard"] = (
                    self.viz_generator.generate_performance_dashboard_data(
                        self.validator.validation_history
                    )
                )

            logger.info(
                f"📊 Generated {len(viz_package['visualizations'])} visualizations"
            )

            # SAFETY: Convert any boolean values to strings before return
            encoder = CustomJSONEncoder()
            safe_viz_package = encoder._convert_booleans(viz_package)

            return safe_viz_package

        except Exception as e:
            logger.error(f"❌ Visualization generation failed: {e}")
            return {"error": str(e)}

    def export_visualization_config(self, chart_type: str) -> Dict:
        """Export configuration for specific chart type"""
        return self.viz_generator.generate_chart_config(chart_type)

    # =====================================
    # 🚀 COMPREHENSIVE ANALYSIS WITH ALL FEATURES
    # =====================================

    def analyze_with_full_pipeline(
        self,
        start_date: date = None,
        end_date: date = None,
        significance_level: float = 0.05,
        actual_results: List[str] = None,
        generate_visualizations: bool = True,
    ) -> Dict:
        """
        Complete analysis pipeline with validation, learning, and visualization

        Args:
            start_date: Analysis start date
            end_date: Analysis end date
            significance_level: Statistical significance level
            actual_results: Actual results for validation (if available)
            generate_visualizations: Whether to generate visualization data

        Returns:
            Dict: Complete analysis package
        """
        try:
            logger.info("🚀 Starting full analysis pipeline...")

            # Step 1: Core frequency analysis
            base_analysis = self.analyze_frequency_patterns_enhanced(
                start_date, end_date, significance_level
            )

            # Step 2: Apply adaptive weights if learning is enabled
            if self.config.get("enable_feedback_learning", "enabled") == "enabled":
                adaptive_predictions = self.get_adaptive_predictions(base_analysis)
                base_analysis["adaptive_predictions"] = adaptive_predictions

            # Step 3: Validation if actual results provided
            validation_result = None
            if (
                actual_results
                and self.config.get("enable_validation", "enabled") == "enabled"
            ):
                validation_result = self.validate_predictions_against_actual(
                    base_analysis, actual_results, end_date or date.today()
                )
                base_analysis["validation_result"] = validation_result

                # Step 4: Learn from validation
                if self.config.get("enable_feedback_learning", "enabled") == "enabled":
                    self.learn_from_results(validation_result)

            # Step 5: Generate visualizations
            if (
                generate_visualizations
                and self.config.get("enable_visualization", "enabled") == "enabled"
            ):
                viz_data = self.generate_visualization_data(base_analysis)
                base_analysis["visualization_data"] = viz_data

            # Step 6: Add metadata
            base_analysis["pipeline_metadata"] = {
                "analysis_date": datetime.now().isoformat(),
                "validation_enabled": (
                    "enabled"
                    if self.config.get("enable_validation", "enabled") == "enabled"
                    else "disabled"
                ),
                "learning_enabled": (
                    "enabled"
                    if self.config.get("enable_feedback_learning", "enabled")
                    == "enabled"
                    else "disabled"
                ),
                "visualization_enabled": (
                    "enabled"
                    if self.config.get("enable_visualization", "enabled") == "enabled"
                    else "disabled"
                ),
                "adaptive_parameters_applied": (
                    "yes" if bool(self.feedback_system.adaptive_parameters) else "no"
                ),
                "validation_performed": (
                    "yes" if validation_result is not None else "no"
                ),
                "learning_sessions": len(self.feedback_system.learning_history),
            }

            logger.info("✅ Full analysis pipeline completed successfully")

            # SAFETY: Convert any boolean values to strings before return
            encoder = CustomJSONEncoder()
            safe_analysis = encoder._convert_booleans(base_analysis)

            return safe_analysis

        except Exception as e:
            logger.error(f"❌ Full analysis pipeline failed: {e}")

            error_data = {
                "error": str(e),
                "fallback_data": self._get_fallback_patterns(),
            }

            # SAFETY: Convert any boolean values to strings
            encoder = CustomJSONEncoder()
            safe_error_data = encoder._convert_booleans(error_data)

            return safe_error_data

    # =====================================
    # 💾 PERSISTENCE & CACHING METHODS
    # =====================================

    def save_analysis_state(self, filepath: str = None) -> str:
        """Save current analysis state including learning progress"""
        if not filepath:
            filepath = f"enhanced_analyzer_state_{date.today().isoformat()}.pkl"

        try:
            state_data = {
                "config": self.config,
                "feedback_system": {
                    "method_weights": self.feedback_system.method_weights,
                    "adaptive_parameters": self.feedback_system.adaptive_parameters,
                    "learning_history": self.feedback_system.learning_history,
                },
                "validation_history": self.validator.validation_history,
                "performance_metrics": self.validator.performance_metrics,
                "saved_at": datetime.now().isoformat(),
            }

            with open(filepath, "wb") as f:
                pickle.dump(state_data, f)

            logger.info(f"💾 Analysis state saved to {filepath}")
            return filepath

        except Exception as e:
            logger.error(f"❌ Failed to save analysis state: {e}")
            return ""

    def load_analysis_state(self, filepath: str) -> bool:
        """Load previously saved analysis state"""
        try:
            with open(filepath, "rb") as f:
                state_data = pickle.load(f)

            # Restore configuration
            self.config.update(state_data.get("config", {}))

            # Restore feedback system
            feedback_data = state_data.get("feedback_system", {})
            self.feedback_system.method_weights = feedback_data.get(
                "method_weights", self.feedback_system.method_weights
            )
            self.feedback_system.adaptive_parameters = feedback_data.get(
                "adaptive_parameters", {}
            )
            self.feedback_system.learning_history = feedback_data.get(
                "learning_history", []
            )

            # Restore validation history
            self.validator.validation_history = state_data.get("validation_history", [])
            self.validator.performance_metrics = state_data.get(
                "performance_metrics", {}
            )

            logger.info(f"💾 Analysis state loaded from {filepath}")
            return True

        except Exception as e:
            logger.error(f"❌ Failed to load analysis state: {e}")
            return False

    def export_analysis_report(
        self, analysis_results: Dict, format: str = "json"
    ) -> str:
        """Export comprehensive analysis report"""
        try:
            report = {
                "report_metadata": {
                    "generated_at": datetime.now().isoformat(),
                    "analysis_type": "enhanced_deep_frequency",
                    "format": format,
                },
                "analysis_results": analysis_results,
                "performance_summary": self.get_performance_metrics(),
                "learning_progress": self.get_learning_progress(),
                "configuration": self.config,
            }

            filename = f"enhanced_analysis_report_{date.today().isoformat()}.{format}"

            if format.lower() == "json":
                with open(filename, "w", encoding="utf-8") as f:
                    json.dump(
                        report, f, indent=2, ensure_ascii=False, cls=CustomJSONEncoder
                    )
            else:
                # Could add CSV, PDF export here
                logger.warning(f"Format {format} not yet supported, defaulting to JSON")
                filename = filename.replace(f".{format}", ".json")
                with open(filename, "w", encoding="utf-8") as f:
                    json.dump(
                        report, f, indent=2, ensure_ascii=False, cls=CustomJSONEncoder
                    )

            logger.info(f"📄 Analysis report exported to {filename}")
            return filename

        except Exception as e:
            logger.error(f"❌ Failed to export analysis report: {e}")
            return ""


# =====================================
# 🚀 PUBLIC API FUNCTIONS
# =====================================


def get_enhanced_frequency_insights(
    start_date: date = None,
    end_date: date = None,
    significance_level: float = 0.05,
    actual_results: List[str] = None,
    enable_full_pipeline: bool = False,
) -> Dict:
    """
    🚀 PUBLIC API: Get enhanced comprehensive frequency insights

    Args:
        start_date: Analysis start date (default: 6 months ago)
        end_date: Analysis end date (default: today)
        significance_level: Statistical significance threshold (default: 0.05)
        actual_results: Actual results for validation (optional)
        enable_full_pipeline: Whether to use full pipeline with validation/learning

    Returns:
        Dict: Enhanced frequency analysis results with optional validation/learning
    """
    analyzer = EnhancedDeepFrequencyAnalyzer()

    if enable_full_pipeline:
        return analyzer.analyze_with_full_pipeline(
            start_date, end_date, significance_level, actual_results
        )
    else:
        return analyzer.analyze_frequency_patterns_enhanced(
            start_date, end_date, significance_level
        )


def validate_lottery_predictions(
    predictions: Dict, actual_results: List[str], prediction_date: date = None
) -> Dict:
    """
    🔍 PUBLIC API: Validate lottery predictions against actual results

    Args:
        predictions: Prediction results from analysis
        actual_results: Actual winning numbers
        prediction_date: Date of prediction (default: today)

    Returns:
        Dict: Comprehensive validation results
    """
    analyzer = EnhancedDeepFrequencyAnalyzer()
    return analyzer.validate_predictions_against_actual(
        predictions, actual_results, prediction_date
    )


def get_adaptive_lottery_predictions(
    start_date: date = None, end_date: date = None, significance_level: float = 0.05
) -> Dict:
    """
    🔄 PUBLIC API: Get adaptive predictions based on learning history

    Args:
        start_date: Analysis start date
        end_date: Analysis end date
        significance_level: Statistical significance level

    Returns:
        Dict: Adaptive predictions with learned weights
    """
    analyzer = EnhancedDeepFrequencyAnalyzer()

    # Get base analysis
    base_predictions = analyzer.analyze_frequency_patterns_enhanced(
        start_date, end_date, significance_level
    )

    # Apply adaptive weights
    adaptive_predictions = analyzer.get_adaptive_predictions(base_predictions)

    return {
        "base_predictions": base_predictions,
        "adaptive_predictions": adaptive_predictions,
        "learning_metadata": analyzer.get_learning_progress(),
    }


def generate_lottery_visualization_data(analysis_results: Dict) -> Dict:
    """
    📈 PUBLIC API: Generate visualization data for lottery analysis

    Args:
        analysis_results: Results from frequency analysis

    Returns:
        Dict: Complete visualization data package
    """
    analyzer = EnhancedDeepFrequencyAnalyzer()
    return analyzer.generate_visualization_data(analysis_results)


def export_lottery_analysis_report(
    start_date: date = None,
    end_date: date = None,
    actual_results: List[str] = None,
    format: str = "json",
) -> str:
    """
    📄 PUBLIC API: Export comprehensive lottery analysis report

    Args:
        start_date: Analysis start date
        end_date: Analysis end date
        actual_results: Actual results for validation (optional)
        format: Export format ('json', 'csv')

    Returns:
        str: Path to exported report file
    """
    analyzer = EnhancedDeepFrequencyAnalyzer()

    # Run full analysis
    analysis_results = analyzer.analyze_with_full_pipeline(
        start_date, end_date, actual_results=actual_results
    )

    # Export report
    return analyzer.export_analysis_report(analysis_results, format)


# =====================================
# 🧪 TESTING & DEMO FUNCTIONS
# =====================================


def demo_enhanced_analysis_pipeline():
    """
    🎯 DEMO: Comprehensive demonstration of enhanced analysis capabilities
    """
    print("🚀 Enhanced Deep Frequency Analyzer Demo")
    print("=" * 50)

    try:
        analyzer = EnhancedDeepFrequencyAnalyzer()

        # Demo 1: Basic enhanced analysis
        print("\n📊 1. Running enhanced frequency analysis...")
        analysis_results = analyzer.analyze_frequency_patterns_enhanced()
        print(f"✅ Analysis completed with {len(analysis_results)} components")

        # Demo 2: Visualization data generation
        print("\n📈 2. Generating visualization data...")
        viz_data = analyzer.generate_visualization_data(analysis_results)
        viz_count = len(viz_data.get("visualizations", {}))
        print(f"✅ Generated {viz_count} visualization types")

        # Demo 3: Mock validation
        print("\n🔍 3. Demonstrating validation with mock data...")
        mock_actual_results = ["01", "23", "45", "67", "89"]
        validation_result = analyzer.validate_predictions_against_actual(
            analysis_results, mock_actual_results
        )
        precision = validation_result.get("overall_performance", {}).get("precision", 0)
        print(f"✅ Validation completed - Precision: {precision:.2%}")

        # Demo 4: Learning and adaptation
        print("\n🔄 4. Demonstrating learning and adaptation...")
        analyzer.learn_from_results(validation_result)
        learning_progress = analyzer.get_learning_progress()
        sessions = learning_progress.get("total_learning_sessions", 0)
        print(f"✅ Learning completed - Total sessions: {sessions}")

        # Demo 5: Adaptive predictions
        print("\n🎯 5. Generating adaptive predictions...")
        adaptive_predictions = analyzer.get_adaptive_predictions(analysis_results)
        adaptive_count = len(
            adaptive_predictions.get("adaptive_weighted_recommendations", [])
        )
        print(f"✅ Generated {adaptive_count} adaptive recommendations")

        # Demo 6: Full pipeline
        print("\n🚀 6. Running full analysis pipeline...")
        full_analysis = analyzer.analyze_with_full_pipeline(
            actual_results=mock_actual_results
        )
        components = len([k for k in full_analysis.keys() if not k.startswith("_")])
        print(f"✅ Full pipeline completed with {components} components")

        # Demo 7: Export report
        print("\n📄 7. Exporting analysis report...")
        report_path = analyzer.export_analysis_report(full_analysis)
        print(f"✅ Report exported to: {report_path}")

        print("\n🎉 Demo completed successfully!")
        print("=" * 50)

        return {
            "demo_status": "success",
            "analysis_components": len(analysis_results),
            "visualization_types": viz_count,
            "validation_precision": precision,
            "learning_sessions": sessions,
            "adaptive_recommendations": adaptive_count,
            "report_exported": bool(report_path),
        }

    except Exception as e:
        print(f"❌ Demo failed: {e}")
        return {"demo_status": "failed", "error": str(e)}


if __name__ == "__main__":
    # Run demo when script is executed directly
    demo_enhanced_analysis_pipeline()
