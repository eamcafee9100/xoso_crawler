"""
🚀 Phase 2.1: Method Performance Tracker
Core system for tracking and analyzing method performance in real-time
"""

import logging
import statistics
from collections import defaultdict
from datetime import date, timedelta
from decimal import Decimal
from typing import Any, Dict, List, Optional, Tuple

from django.db import transaction
from django.db.models import Q
from django.utils import timezone

from .models import PredictionMethod
from .phase2_models import MethodPerformanceHistory, PerformanceAlerts

logger = logging.getLogger(__name__)


class MethodPerformanceTracker:
    """
    🎯 Core system for tracking method performance and generating insights
    """

    def __init__(self):
        self.tracking_sessions = {}
        self.performance_cache = {}

    def track_method_accuracy(
        self,
        method_id: str,
        predictions: List[str],
        actual_results: List[str],
        tracking_date: date = None,
        market_conditions: Dict = None,
    ) -> Dict[str, Any]:
        """
        Track accuracy of a specific method for a given date

        Args:
            method_id: Unique identifier of the prediction method
            predictions: List of predicted numbers
            actual_results: List of actual winning numbers
            tracking_date: Date of tracking (default: today)
            market_conditions: Context about market conditions

        Returns:
            Dict with tracking results and performance metrics
        """
        try:
            if tracking_date is None:
                tracking_date = timezone.now().date()

            # Get or create method
            try:
                method = PredictionMethod.objects.get(code=method_id)
            except PredictionMethod.DoesNotExist:
                logger.error(f"Method {method_id} not found")
                return {"error": f"Method {method_id} not found"}

            # Calculate hits
            hits = self._calculate_hits(predictions, actual_results)
            predictions_made = len(predictions)
            hits_count = len(hits)

            # Calculate accuracy rate
            accuracy_rate = (
                (hits_count / predictions_made * 100) if predictions_made > 0 else 0
            )

            # Calculate weighted score (considering prediction difficulty)
            weighted_score = self._calculate_weighted_score(
                hits, predictions, actual_results, market_conditions
            )

            # Store performance data
            with transaction.atomic():
                performance, created = (
                    MethodPerformanceHistory.objects.update_or_create(
                        method=method,
                        tracking_date=tracking_date,
                        defaults={
                            "predictions_made": predictions_made,
                            "hits_count": hits_count,
                            "accuracy_rate": Decimal(str(round(accuracy_rate, 2))),
                            "weighted_score": Decimal(str(round(weighted_score, 4))),
                            "market_conditions": market_conditions or {},
                            "performance_metadata": {
                                "hits": hits,
                                "predictions": predictions,
                                "actual_results": actual_results,
                                "tracking_timestamp": timezone.now().isoformat(),
                            },
                        },
                    )
                )

            # Generate insights
            insights = self._generate_performance_insights(method, performance)

            # Check for alerts
            self._check_performance_alerts(method, performance, insights)

            logger.info(
                f"✅ Tracked {method.name}: {hits_count}/{predictions_made} "
                f"({accuracy_rate:.1f}%) on {tracking_date}"
            )

            return {
                "success": True,
                "method_id": method_id,
                "method_name": method.name,
                "tracking_date": tracking_date.isoformat(),
                "predictions_made": predictions_made,
                "hits_count": hits_count,
                "accuracy_rate": accuracy_rate,
                "weighted_score": weighted_score,
                "hits": hits,
                "insights": insights,
                "created": created,
            }

        except Exception as e:
            logger.error(f"Error tracking method accuracy: {str(e)}")
            return {"error": str(e)}

    def calculate_performance_metrics(
        self, method_id: str, time_period: int = 30
    ) -> Dict[str, Any]:
        """
        Calculate comprehensive performance metrics for a method

        Args:
            method_id: Method identifier
            time_period: Number of days to analyze

        Returns:
            Dict with comprehensive performance metrics
        """
        try:
            method = PredictionMethod.objects.get(code=method_id)
            end_date = timezone.now().date()
            start_date = end_date - timedelta(days=time_period)

            # Get performance history
            performances = MethodPerformanceHistory.objects.filter(
                method=method,
                tracking_date__gte=start_date,
                tracking_date__lte=end_date,
            ).order_by("tracking_date")

            if not performances.exists():
                return {
                    "method_id": method_id,
                    "method_name": method.name,
                    "period_days": time_period,
                    "error": "No performance data found for this period",
                }

            # Basic metrics
            accuracy_rates = [
                float(p.accuracy_rate) for p in performances if p.accuracy_rate
            ]
            weighted_scores = [
                float(p.weighted_score) for p in performances if p.weighted_score
            ]

            total_predictions = sum(p.predictions_made for p in performances)
            total_hits = sum(p.hits_count for p in performances)

            # Statistical analysis
            metrics = {
                "method_id": method_id,
                "method_name": method.name,
                "period_days": time_period,
                "data_points": performances.count(),
                # Basic performance
                "total_predictions": total_predictions,
                "total_hits": total_hits,
                "overall_accuracy": (
                    (total_hits / total_predictions * 100)
                    if total_predictions > 0
                    else 0
                ),
                # Accuracy statistics
                "avg_accuracy": (
                    statistics.mean(accuracy_rates) if accuracy_rates else 0
                ),
                "median_accuracy": (
                    statistics.median(accuracy_rates) if accuracy_rates else 0
                ),
                "min_accuracy": min(accuracy_rates) if accuracy_rates else 0,
                "max_accuracy": max(accuracy_rates) if accuracy_rates else 0,
                "accuracy_std_dev": (
                    statistics.stdev(accuracy_rates) if len(accuracy_rates) > 1 else 0
                ),
                # Weighted score statistics
                "avg_weighted_score": (
                    statistics.mean(weighted_scores) if weighted_scores else 0
                ),
                "weighted_score_trend": self._calculate_trend(weighted_scores),
                # Performance consistency
                "consistency_score": self._calculate_consistency_score(accuracy_rates),
                "volatility_score": self._calculate_volatility_score(accuracy_rates),
                # Recent performance (last 7 days)
                "recent_performance": self._get_recent_performance(method, 7),
                # Performance grade
                "performance_grade": self._get_performance_grade(accuracy_rates),
                # Trend analysis
                "accuracy_trend": self._calculate_trend(accuracy_rates),
                "trend_direction": self._get_trend_direction(accuracy_rates),
                # Activity metrics
                "active_days": performances.count(),
                "avg_predictions_per_day": (
                    total_predictions / performances.count()
                    if performances.count() > 0
                    else 0
                ),
            }

            return metrics

        except PredictionMethod.DoesNotExist:
            return {"error": f"Method {method_id} not found"}
        except Exception as e:
            logger.error(f"Error calculating performance metrics: {str(e)}")
            return {"error": str(e)}

    def get_method_rankings(
        self, criteria: str = "accuracy", time_range: int = 30, limit: int = 20
    ) -> List[Dict[str, Any]]:
        """
        Get method rankings based on specified criteria

        Args:
            criteria: Ranking criteria ('accuracy', 'consistency', 'weighted_score')
            time_range: Number of days to consider
            limit: Maximum number of methods to return

        Returns:
            List of methods ranked by criteria
        """
        try:
            end_date = timezone.now().date()
            start_date = end_date - timedelta(days=time_range)

            # Get performance data for all methods
            method_performances = defaultdict(list)

            performances = MethodPerformanceHistory.objects.filter(
                tracking_date__gte=start_date, tracking_date__lte=end_date
            ).select_related("method")

            for perf in performances:
                method_performances[perf.method.code].append(perf)

            # Calculate rankings
            rankings = []

            for method_id, perfs in method_performances.items():
                if not perfs:
                    continue

                method = perfs[0].method
                accuracy_rates = [
                    float(p.accuracy_rate) for p in perfs if p.accuracy_rate
                ]
                weighted_scores = [
                    float(p.weighted_score) for p in perfs if p.weighted_score
                ]

                if not accuracy_rates:
                    continue

                # Calculate ranking metrics
                avg_accuracy = statistics.mean(accuracy_rates)
                consistency = self._calculate_consistency_score(accuracy_rates)
                avg_weighted_score = (
                    statistics.mean(weighted_scores) if weighted_scores else 0
                )

                ranking_data = {
                    "method_id": method_id,
                    "method_name": method.name,
                    "method_category": method.category,
                    "avg_accuracy": round(avg_accuracy, 2),
                    "consistency_score": round(consistency, 2),
                    "avg_weighted_score": round(avg_weighted_score, 4),
                    "data_points": len(perfs),
                    "total_predictions": sum(p.predictions_made for p in perfs),
                    "total_hits": sum(p.hits_count for p in perfs),
                    "recent_trend": self._get_trend_direction(
                        accuracy_rates[-7:]
                        if len(accuracy_rates) >= 7
                        else accuracy_rates
                    ),
                }

                # Add ranking score based on criteria
                if criteria == "accuracy":
                    ranking_data["ranking_score"] = avg_accuracy
                elif criteria == "consistency":
                    ranking_data["ranking_score"] = consistency
                elif criteria == "weighted_score":
                    ranking_data["ranking_score"] = avg_weighted_score
                else:
                    # Combined score
                    ranking_data["ranking_score"] = (
                        avg_accuracy * 0.5 + consistency * 0.3 + avg_weighted_score * 20
                    )

                rankings.append(ranking_data)

            # Sort by ranking score
            rankings.sort(key=lambda x: x["ranking_score"], reverse=True)

            logger.info(
                f"📊 Generated rankings for {len(rankings)} methods based on {criteria}"
            )

            return rankings[:limit]

        except Exception as e:
            logger.error(f"Error generating method rankings: {str(e)}")
            return []

    def export_performance_report(
        self,
        format: str = "json",
        date_range: Tuple[date, date] = None,
        methods: List[str] = None,
    ) -> Dict[str, Any]:
        """
        Export comprehensive performance report

        Args:
            format: Export format ('json', 'csv', 'excel')
            date_range: Tuple of (start_date, end_date)
            methods: List of method IDs to include (None for all)

        Returns:
            Dict with report data and metadata
        """
        try:
            # Set default date range
            if date_range is None:
                end_date = timezone.now().date()
                start_date = end_date - timedelta(days=30)
                date_range = (start_date, end_date)

            start_date, end_date = date_range

            # Build query
            query = Q(tracking_date__gte=start_date, tracking_date__lte=end_date)

            if methods:
                query &= Q(method__code__in=methods)

            # Get performance data
            performances = (
                MethodPerformanceHistory.objects.filter(query)
                .select_related("method")
                .order_by("method__name", "tracking_date")
            )

            # Generate report data
            report_data = {
                "report_metadata": {
                    "generated_at": timezone.now().isoformat(),
                    "date_range": {
                        "start_date": start_date.isoformat(),
                        "end_date": end_date.isoformat(),
                        "days_covered": (end_date - start_date).days + 1,
                    },
                    "total_records": performances.count(),
                    "methods_included": methods or "all",
                    "format": format,
                },
                "summary_statistics": {},
                "method_performances": [],
                "daily_summary": {},
                "insights": [],
            }

            # Group by method
            method_data = defaultdict(list)
            for perf in performances:
                method_data[perf.method.code].append(perf)

            # Process each method
            for method_id, perfs in method_data.items():
                method = perfs[0].method

                # Calculate method summary
                accuracy_rates = [
                    float(p.accuracy_rate) for p in perfs if p.accuracy_rate
                ]
                total_predictions = sum(p.predictions_made for p in perfs)
                total_hits = sum(p.hits_count for p in perfs)

                method_summary = {
                    "method_id": method_id,
                    "method_name": method.name,
                    "method_category": method.category,
                    "total_predictions": total_predictions,
                    "total_hits": total_hits,
                    "overall_accuracy": (
                        (total_hits / total_predictions * 100)
                        if total_predictions > 0
                        else 0
                    ),
                    "avg_accuracy": (
                        statistics.mean(accuracy_rates) if accuracy_rates else 0
                    ),
                    "best_accuracy": max(accuracy_rates) if accuracy_rates else 0,
                    "worst_accuracy": min(accuracy_rates) if accuracy_rates else 0,
                    "consistency_score": self._calculate_consistency_score(
                        accuracy_rates
                    ),
                    "active_days": len(perfs),
                    "daily_details": [],
                }

                # Add daily details
                for perf in perfs:
                    method_summary["daily_details"].append(
                        {
                            "date": perf.tracking_date.isoformat(),
                            "predictions_made": perf.predictions_made,
                            "hits_count": perf.hits_count,
                            "accuracy_rate": (
                                float(perf.accuracy_rate) if perf.accuracy_rate else 0
                            ),
                            "weighted_score": (
                                float(perf.weighted_score) if perf.weighted_score else 0
                            ),
                            "market_conditions": perf.market_conditions,
                        }
                    )

                report_data["method_performances"].append(method_summary)

            # Calculate summary statistics
            all_accuracies = []
            for method_perf in report_data["method_performances"]:
                all_accuracies.extend(
                    [day["accuracy_rate"] for day in method_perf["daily_details"]]
                )

            if all_accuracies:
                report_data["summary_statistics"] = {
                    "total_methods": len(method_data),
                    "total_predictions": sum(
                        p["total_predictions"]
                        for p in report_data["method_performances"]
                    ),
                    "total_hits": sum(
                        p["total_hits"] for p in report_data["method_performances"]
                    ),
                    "avg_system_accuracy": statistics.mean(all_accuracies),
                    "best_system_accuracy": max(all_accuracies),
                    "worst_system_accuracy": min(all_accuracies),
                    "system_consistency": self._calculate_consistency_score(
                        all_accuracies
                    ),
                }

            # Generate insights
            report_data["insights"] = self._generate_report_insights(report_data)

            logger.info(
                f"📋 Generated performance report: {len(method_data)} methods, {performances.count()} records"
            )

            return report_data

        except Exception as e:
            logger.error(f"Error exporting performance report: {str(e)}")
            return {"error": str(e)}

    # Private helper methods
    def _calculate_hits(
        self, predictions: List[str], actual_results: List[str]
    ) -> List[str]:
        """Calculate which predictions were hits"""
        predictions_set = set(predictions)
        actual_set = set(actual_results)
        return list(predictions_set.intersection(actual_set))

    def _calculate_weighted_score(
        self,
        hits: List[str],
        predictions: List[str],
        actual_results: List[str],
        market_conditions: Dict = None,
    ) -> float:
        """Calculate weighted score considering prediction difficulty"""
        if not predictions:
            return 0.0

        base_score = len(hits) / len(predictions)

        # Adjust for market conditions
        difficulty_multiplier = 1.0

        if market_conditions:
            volatility = market_conditions.get("volatility", 0)
            consistency = market_conditions.get("consistency", 1)

            # Higher volatility = more difficult = higher multiplier for success
            difficulty_multiplier = 1.0 + (volatility / 100 * 0.5)

            # Lower consistency = more difficult = higher multiplier for success
            difficulty_multiplier *= 2.0 - consistency

        return base_score * difficulty_multiplier

    def _calculate_consistency_score(self, accuracy_rates: List[float]) -> float:
        """Calculate consistency score (0-100, higher is more consistent)"""
        if len(accuracy_rates) <= 1:
            return 100.0

        std_dev = statistics.stdev(accuracy_rates)
        mean_accuracy = statistics.mean(accuracy_rates)

        # Coefficient of variation (lower is more consistent)
        cv = std_dev / mean_accuracy if mean_accuracy > 0 else float("inf")

        # Convert to consistency score (0-100)
        consistency = max(0, 100 - (cv * 20))
        return min(100, consistency)

    def _calculate_volatility_score(self, accuracy_rates: List[float]) -> float:
        """Calculate volatility score (0-100, higher is more volatile)"""
        if len(accuracy_rates) <= 1:
            return 0.0

        std_dev = statistics.stdev(accuracy_rates)
        return min(100, std_dev * 2)  # Scale standard deviation to 0-100

    def _calculate_trend(self, values: List[float]) -> float:
        """Calculate trend slope (-1 to 1, positive = improving)"""
        if len(values) < 2:
            return 0.0

        n = len(values)
        x_values = list(range(n))

        # Simple linear regression slope
        x_mean = statistics.mean(x_values)
        y_mean = statistics.mean(values)

        numerator = sum((x - x_mean) * (y - y_mean) for x, y in zip(x_values, values))
        denominator = sum((x - x_mean) ** 2 for x in x_values)

        if denominator == 0:
            return 0.0

        slope = numerator / denominator

        # Normalize to -1 to 1 range
        max_possible_slope = max(values) / (n - 1) if n > 1 else 0
        if max_possible_slope > 0:
            return max(-1, min(1, slope / max_possible_slope))

        return 0.0

    def _get_trend_direction(self, values: List[float]) -> str:
        """Get trend direction as string"""
        if not values:
            return "unknown"

        trend = self._calculate_trend(values)

        if trend > 0.1:
            return "improving"
        elif trend < -0.1:
            return "declining"
        else:
            return "stable"

    def _get_performance_grade(self, accuracy_rates: List[float]) -> str:
        """Get overall performance grade"""
        if not accuracy_rates:
            return "N/A"

        avg_accuracy = statistics.mean(accuracy_rates)

        if avg_accuracy >= 80:
            return "A+"
        elif avg_accuracy >= 70:
            return "A"
        elif avg_accuracy >= 60:
            return "B+"
        elif avg_accuracy >= 50:
            return "B"
        elif avg_accuracy >= 40:
            return "C"
        else:
            return "D"

    def _get_recent_performance(
        self, method: PredictionMethod, days: int = 7
    ) -> Dict[str, Any]:
        """Get recent performance summary"""
        end_date = timezone.now().date()
        start_date = end_date - timedelta(days=days)

        recent_perfs = MethodPerformanceHistory.objects.filter(
            method=method, tracking_date__gte=start_date, tracking_date__lte=end_date
        ).order_by("-tracking_date")

        if not recent_perfs.exists():
            return {"error": "No recent data"}

        accuracy_rates = [
            float(p.accuracy_rate) for p in recent_perfs if p.accuracy_rate
        ]

        return {
            "days": days,
            "data_points": recent_perfs.count(),
            "avg_accuracy": statistics.mean(accuracy_rates) if accuracy_rates else 0,
            "trend": self._get_trend_direction(accuracy_rates),
            "latest_accuracy": accuracy_rates[0] if accuracy_rates else 0,
        }

    def _generate_performance_insights(
        self, method: PredictionMethod, performance: MethodPerformanceHistory
    ) -> List[str]:
        """Generate insights for method performance"""
        insights = []

        # Get historical context
        recent_perfs = MethodPerformanceHistory.objects.filter(
            method=method, tracking_date__lt=performance.tracking_date
        ).order_by("-tracking_date")[:10]

        if recent_perfs.exists():
            recent_accuracies = [
                float(p.accuracy_rate) for p in recent_perfs if p.accuracy_rate
            ]

            if recent_accuracies:
                avg_recent = statistics.mean(recent_accuracies)
                current_accuracy = (
                    float(performance.accuracy_rate) if performance.accuracy_rate else 0
                )

                if current_accuracy > avg_recent + 10:
                    insights.append(
                        "📈 Significant improvement compared to recent average"
                    )
                elif current_accuracy < avg_recent - 10:
                    insights.append("📉 Performance decline compared to recent average")

                trend = self._get_trend_direction(
                    recent_accuracies + [current_accuracy]
                )
                if trend == "improving":
                    insights.append("🚀 Shows improving trend")
                elif trend == "declining":
                    insights.append("⚠️ Shows declining trend")

        # Performance level insights
        if performance.accuracy_rate:
            if performance.accuracy_rate >= 80:
                insights.append("🏆 Excellent performance level")
            elif performance.accuracy_rate >= 60:
                insights.append("✅ Good performance level")
            elif performance.accuracy_rate < 30:
                insights.append("🔴 Low performance - needs attention")

        return insights

    def _check_performance_alerts(
        self,
        method: PredictionMethod,
        performance: MethodPerformanceHistory,
        insights: List[str],
    ):
        """Check if performance alerts should be triggered"""
        try:
            current_accuracy = (
                float(performance.accuracy_rate) if performance.accuracy_rate else 0
            )

            # Get recent average for comparison
            recent_perfs = MethodPerformanceHistory.objects.filter(
                method=method, tracking_date__lt=performance.tracking_date
            ).order_by("-tracking_date")[:7]

            if recent_perfs.exists():
                recent_accuracies = [
                    float(p.accuracy_rate) for p in recent_perfs if p.accuracy_rate
                ]

                if recent_accuracies:
                    avg_recent = statistics.mean(recent_accuracies)

                    # Check for significant drops
                    if current_accuracy < avg_recent - 20:  # 20% drop
                        PerformanceAlerts.objects.create(
                            alert_type="accuracy_drop",
                            method=method,
                            severity_level="high",
                            message=f"{method.name} accuracy dropped significantly: {current_accuracy:.1f}% vs {avg_recent:.1f}% average",
                            alert_data={
                                "current_accuracy": current_accuracy,
                                "recent_average": avg_recent,
                                "drop_amount": avg_recent - current_accuracy,
                                "tracking_date": performance.tracking_date.isoformat(),
                            },
                        )

                    # Check for exceptional performance
                    elif current_accuracy > avg_recent + 25:  # 25% improvement
                        PerformanceAlerts.objects.create(
                            alert_type="performance_spike",
                            method=method,
                            severity_level="medium",
                            message=f"{method.name} shows exceptional performance: {current_accuracy:.1f}% vs {avg_recent:.1f}% average",
                            alert_data={
                                "current_accuracy": current_accuracy,
                                "recent_average": avg_recent,
                                "improvement_amount": current_accuracy - avg_recent,
                                "tracking_date": performance.tracking_date.isoformat(),
                            },
                        )

            # Check for method failure (very low accuracy)
            if current_accuracy < 10:  # Less than 10% accuracy
                PerformanceAlerts.objects.create(
                    alert_type="method_failure",
                    method=method,
                    severity_level="critical",
                    message=f"{method.name} shows very low accuracy: {current_accuracy:.1f}%",
                    alert_data={
                        "current_accuracy": current_accuracy,
                        "predictions_made": performance.predictions_made,
                        "hits_count": performance.hits_count,
                        "tracking_date": performance.tracking_date.isoformat(),
                    },
                )

        except Exception as e:
            logger.error(f"Error checking performance alerts: {str(e)}")

    def _generate_report_insights(self, report_data: Dict[str, Any]) -> List[str]:
        """Generate insights for performance report"""
        insights = []

        try:
            summary = report_data.get("summary_statistics", {})
            methods = report_data.get("method_performances", [])

            if summary:
                avg_accuracy = summary.get("avg_system_accuracy", 0)

                # System-level insights
                if avg_accuracy > 60:
                    insights.append(
                        f"🎯 System performing well with {avg_accuracy:.1f}% average accuracy"
                    )
                elif avg_accuracy < 40:
                    insights.append(
                        f"⚠️ System accuracy below target at {avg_accuracy:.1f}%"
                    )

                # Best and worst performers
                if methods:
                    methods.sort(key=lambda x: x["avg_accuracy"], reverse=True)

                    best_method = methods[0]
                    worst_method = methods[-1]

                    insights.append(
                        f"🏆 Best performer: {best_method['method_name']} ({best_method['avg_accuracy']:.1f}%)"
                    )

                    if len(methods) > 1:
                        insights.append(
                            f"📉 Needs improvement: {worst_method['method_name']} ({worst_method['avg_accuracy']:.1f}%)"
                        )

                    # Consistency insights
                    high_consistency_methods = [
                        m for m in methods if m["consistency_score"] > 80
                    ]
                    if high_consistency_methods:
                        insights.append(
                            f"🎖️ {len(high_consistency_methods)} methods show high consistency"
                        )

                    # Trend insights
                    improving_methods = [
                        m for m in methods if m.get("recent_trend") == "improving"
                    ]
                    if improving_methods:
                        insights.append(
                            f"📈 {len(improving_methods)} methods showing improvement trend"
                        )

        except Exception as e:
            logger.error(f"Error generating report insights: {str(e)}")

        return insights
