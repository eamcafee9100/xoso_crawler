"""
🚀 Phase 2.3: Historical Analysis Engine
Advanced system for historical pattern analysis and correlation discovery
"""

import logging
import statistics
from collections import Counter, defaultdict
from datetime import date, datetime, timedelta
from decimal import Decimal
from typing import Any, Dict, List, Optional, Tuple

import numpy as np
import pandas as pd
from django.db import transaction
from django.db.models import Avg, Count, F, Max, Min, Q, StdDev
from django.utils import timezone
from scipy import stats
from scipy.stats import pearsonr, spearmanr

from .method_performance_tracker import MethodPerformanceTracker
from .models import PredictionMethod
from .phase2_models import (
    MethodCorrelationMatrix,
    MethodPerformanceHistory,
    PerformanceAlerts,
)

logger = logging.getLogger(__name__)


class HistoricalAnalysisEngine:
    """
    🎯 Advanced historical analysis system for pattern discovery and correlation analysis
    """

    def __init__(self):
        self.performance_tracker = MethodPerformanceTracker()
        self.analysis_cache = {}

    def analyze_method_correlations(
        self,
        analysis_period: int = 90,
        min_shared_dates: int = 10,
        correlation_types: List[str] = None,
    ) -> Dict[str, Any]:
        """
        Analyze correlations between different prediction methods

        Args:
            analysis_period: Days of data to analyze
            min_shared_dates: Minimum shared prediction dates required
            correlation_types: Types of correlation to calculate ['pearson', 'spearman', 'kendall']

        Returns:
            Dict with correlation analysis results
        """
        try:
            if correlation_types is None:
                correlation_types = ["pearson", "spearman"]

            end_date = timezone.now().date()
            start_date = end_date - timedelta(days=analysis_period)

            logger.info(
                f"🔍 Analyzing method correlations for period {start_date} to {end_date}"
            )

            # Get performance data
            performances = (
                MethodPerformanceHistory.objects.filter(
                    tracking_date__gte=start_date, tracking_date__lte=end_date
                )
                .select_related("method")
                .order_by("tracking_date")
            )

            if not performances.exists():
                return {
                    "error": "No performance data available for correlation analysis"
                }

            # Organize data by method and date
            method_performance_data = defaultdict(dict)
            all_dates = set()

            for perf in performances:
                method_id = perf.method.code
                tracking_date = perf.tracking_date
                accuracy = float(perf.accuracy_rate) if perf.accuracy_rate else 0

                method_performance_data[method_id][tracking_date] = accuracy
                all_dates.add(tracking_date)

            all_dates = sorted(all_dates)
            method_ids = list(method_performance_data.keys())

            if len(method_ids) < 2:
                return {"error": "Need at least 2 methods for correlation analysis"}

            # Calculate correlations between method pairs
            correlation_results = {}
            correlation_matrix = {}

            for i, method_a in enumerate(method_ids):
                correlation_matrix[method_a] = {}

                for j, method_b in enumerate(method_ids):
                    if i >= j:  # Skip duplicate pairs and self-correlation
                        if i == j:
                            correlation_matrix[method_a][method_b] = 1.0
                        continue

                    # Get shared dates with data for both methods
                    shared_dates = []
                    values_a = []
                    values_b = []

                    for date in all_dates:
                        if (
                            date in method_performance_data[method_a]
                            and date in method_performance_data[method_b]
                        ):
                            shared_dates.append(date)
                            values_a.append(method_performance_data[method_a][date])
                            values_b.append(method_performance_data[method_b][date])

                    if len(shared_dates) < min_shared_dates:
                        correlation_matrix[method_a][method_b] = None
                        correlation_matrix[method_b] = correlation_matrix.get(
                            method_b, {}
                        )
                        correlation_matrix[method_b][method_a] = None
                        continue

                    # Calculate different types of correlations
                    correlations = {}

                    try:
                        if "pearson" in correlation_types:
                            pearson_corr, pearson_p = pearsonr(values_a, values_b)
                            correlations["pearson"] = {
                                "coefficient": pearson_corr,
                                "p_value": pearson_p,
                                "significance": (
                                    "significant"
                                    if pearson_p < 0.05
                                    else "not_significant"
                                ),
                            }

                        if "spearman" in correlation_types:
                            spearman_corr, spearman_p = spearmanr(values_a, values_b)
                            correlations["spearman"] = {
                                "coefficient": spearman_corr,
                                "p_value": spearman_p,
                                "significance": (
                                    "significant"
                                    if spearman_p < 0.05
                                    else "not_significant"
                                ),
                            }

                        if "kendall" in correlation_types:
                            kendall_corr, kendall_p = stats.kendalltau(
                                values_a, values_b
                            )
                            correlations["kendall"] = {
                                "coefficient": kendall_corr,
                                "p_value": kendall_p,
                                "significance": (
                                    "significant"
                                    if kendall_p < 0.05
                                    else "not_significant"
                                ),
                            }

                    except Exception as e:
                        logger.warning(
                            f"Error calculating correlation for {method_a}-{method_b}: {str(e)}"
                        )
                        correlations = {"error": str(e)}

                    # Store results
                    pair_key = f"{method_a}_{method_b}"
                    correlation_results[pair_key] = {
                        "method_a": method_a,
                        "method_b": method_b,
                        "shared_dates": len(shared_dates),
                        "correlations": correlations,
                        "data_quality": {
                            "mean_accuracy_a": statistics.mean(values_a),
                            "mean_accuracy_b": statistics.mean(values_b),
                            "std_accuracy_a": (
                                statistics.stdev(values_a) if len(values_a) > 1 else 0
                            ),
                            "std_accuracy_b": (
                                statistics.stdev(values_b) if len(values_b) > 1 else 0
                            ),
                        },
                    }

                    # Store in matrix (use primary correlation type)
                    primary_corr = correlations.get(
                        "pearson", correlations.get("spearman", {})
                    )
                    correlation_matrix[method_a][method_b] = primary_corr.get(
                        "coefficient"
                    )
                    correlation_matrix[method_b] = correlation_matrix.get(method_b, {})
                    correlation_matrix[method_b][method_a] = primary_corr.get(
                        "coefficient"
                    )

            # Store correlation results in database
            self._store_correlation_results(correlation_results, end_date)

            # Generate insights
            insights = self._generate_correlation_insights(
                correlation_results, correlation_matrix
            )

            logger.info(
                f"📊 Correlation analysis completed: {len(correlation_results)} method pairs analyzed"
            )

            return {
                "success": True,
                "analysis_period": {
                    "start_date": start_date.isoformat(),
                    "end_date": end_date.isoformat(),
                    "days": analysis_period,
                },
                "methods_analyzed": len(method_ids),
                "correlation_pairs": len(correlation_results),
                "correlation_types": correlation_types,
                "correlation_results": correlation_results,
                "correlation_matrix": correlation_matrix,
                "insights": insights,
                "summary_statistics": self._calculate_correlation_summary(
                    correlation_results
                ),
            }

        except Exception as e:
            logger.error(f"Error in correlation analysis: {str(e)}")
            return {"error": str(e)}

    def discover_historical_patterns(
        self,
        pattern_types: List[str] = None,
        lookback_period: int = 365,
        pattern_confidence_threshold: float = 0.7,
    ) -> Dict[str, Any]:
        """
        Discover patterns in historical performance data

        Args:
            pattern_types: Types of patterns to discover
            lookback_period: Days of historical data to analyze
            pattern_confidence_threshold: Minimum confidence for pattern detection

        Returns:
            Dict with discovered patterns and analysis
        """
        try:
            if pattern_types is None:
                pattern_types = [
                    "seasonal",
                    "cyclical",
                    "trend",
                    "volatility",
                    "performance_clusters",
                    "anomaly_detection",
                ]

            end_date = timezone.now().date()
            start_date = end_date - timedelta(days=lookback_period)

            logger.info(
                f"🔍 Discovering historical patterns for period {start_date} to {end_date}"
            )

            # Get performance data
            performances = (
                MethodPerformanceHistory.objects.filter(
                    tracking_date__gte=start_date, tracking_date__lte=end_date
                )
                .select_related("method")
                .order_by("method", "tracking_date")
            )

            if not performances.exists():
                return {"error": "No performance data available for pattern discovery"}

            # Organize data by method
            method_data = defaultdict(list)
            for perf in performances:
                method_data[perf.method.code].append(
                    {
                        "date": perf.tracking_date,
                        "accuracy": (
                            float(perf.accuracy_rate) if perf.accuracy_rate else 0
                        ),
                        "weighted_score": (
                            float(perf.weighted_score) if perf.weighted_score else 0
                        ),
                        "predictions_made": perf.predictions_made,
                        "hits_count": perf.hits_count,
                    }
                )

            discovered_patterns = {}

            # Analyze patterns for each method
            for method_id, data in method_data.items():
                if len(data) < 30:  # Need sufficient data
                    continue

                method_patterns = {}

                # Extract time series data
                dates = [d["date"] for d in data]
                accuracies = [d["accuracy"] for d in data]
                weighted_scores = [d["weighted_score"] for d in data]

                # 1. Seasonal Patterns
                if "seasonal" in pattern_types:
                    seasonal_patterns = self._detect_seasonal_patterns(
                        dates, accuracies
                    )
                    if seasonal_patterns["confidence"] >= pattern_confidence_threshold:
                        method_patterns["seasonal"] = seasonal_patterns

                # 2. Cyclical Patterns
                if "cyclical" in pattern_types:
                    cyclical_patterns = self._detect_cyclical_patterns(accuracies)
                    if cyclical_patterns["confidence"] >= pattern_confidence_threshold:
                        method_patterns["cyclical"] = cyclical_patterns

                # 3. Trend Analysis
                if "trend" in pattern_types:
                    trend_patterns = self._detect_trend_patterns(dates, accuracies)
                    if trend_patterns["confidence"] >= pattern_confidence_threshold:
                        method_patterns["trend"] = trend_patterns

                # 4. Volatility Patterns
                if "volatility" in pattern_types:
                    volatility_patterns = self._detect_volatility_patterns(accuracies)
                    if (
                        volatility_patterns["confidence"]
                        >= pattern_confidence_threshold
                    ):
                        method_patterns["volatility"] = volatility_patterns

                # 5. Performance Clusters
                if "performance_clusters" in pattern_types:
                    cluster_patterns = self._detect_performance_clusters(data)
                    if cluster_patterns["confidence"] >= pattern_confidence_threshold:
                        method_patterns["performance_clusters"] = cluster_patterns

                # 6. Anomaly Detection
                if "anomaly_detection" in pattern_types:
                    anomaly_patterns = self._detect_anomalies(dates, accuracies)
                    if anomaly_patterns["confidence"] >= pattern_confidence_threshold:
                        method_patterns["anomaly_detection"] = anomaly_patterns

                if method_patterns:
                    discovered_patterns[method_id] = method_patterns

            # Generate cross-method pattern insights
            cross_method_insights = self._analyze_cross_method_patterns(
                discovered_patterns
            )

            # Generate overall insights
            overall_insights = self._generate_pattern_insights(discovered_patterns)

            logger.info(
                f"🎯 Pattern discovery completed: {len(discovered_patterns)} methods with patterns"
            )

            return {
                "success": True,
                "analysis_period": {
                    "start_date": start_date.isoformat(),
                    "end_date": end_date.isoformat(),
                    "days": lookback_period,
                },
                "pattern_types_analyzed": pattern_types,
                "confidence_threshold": pattern_confidence_threshold,
                "methods_with_patterns": len(discovered_patterns),
                "discovered_patterns": discovered_patterns,
                "cross_method_insights": cross_method_insights,
                "overall_insights": overall_insights,
                "pattern_summary": self._summarize_patterns(discovered_patterns),
            }

        except Exception as e:
            logger.error(f"Error in pattern discovery: {str(e)}")
            return {"error": str(e)}

    def generate_performance_forecast(
        self, method_id: str, forecast_days: int = 30, confidence_interval: float = 0.95
    ) -> Dict[str, Any]:
        """
        Generate performance forecast for a specific method

        Args:
            method_id: Method to forecast
            forecast_days: Number of days to forecast
            confidence_interval: Confidence interval for forecast

        Returns:
            Dict with forecast results
        """
        try:
            # Get historical data
            lookback_period = min(
                365, forecast_days * 10
            )  # Use 10x forecast period or 1 year
            end_date = timezone.now().date()
            start_date = end_date - timedelta(days=lookback_period)

            try:
                method = PredictionMethod.objects.get(code=method_id)
            except PredictionMethod.DoesNotExist:
                return {"error": f"Method {method_id} not found"}

            performances = MethodPerformanceHistory.objects.filter(
                method=method,
                tracking_date__gte=start_date,
                tracking_date__lte=end_date,
            ).order_by("tracking_date")

            if performances.count() < 10:
                return {
                    "error": "Insufficient historical data for forecasting (minimum 10 data points)"
                }

            # Prepare time series data
            dates = []
            accuracies = []
            weighted_scores = []

            for perf in performances:
                dates.append(perf.tracking_date)
                accuracies.append(
                    float(perf.accuracy_rate) if perf.accuracy_rate else 0
                )
                weighted_scores.append(
                    float(perf.weighted_score) if perf.weighted_score else 0
                )

            # Convert to pandas for easier analysis
            df = pd.DataFrame(
                {
                    "date": dates,
                    "accuracy": accuracies,
                    "weighted_score": weighted_scores,
                }
            )
            df["date"] = pd.to_datetime(df["date"])
            df.set_index("date", inplace=True)

            # Generate forecasts using multiple methods
            forecasts = {}

            # 1. Simple Moving Average
            forecasts["moving_average"] = self._forecast_moving_average(
                df["accuracy"], forecast_days, confidence_interval
            )

            # 2. Exponential Smoothing
            forecasts["exponential_smoothing"] = self._forecast_exponential_smoothing(
                df["accuracy"], forecast_days, confidence_interval
            )

            # 3. Linear Trend
            forecasts["linear_trend"] = self._forecast_linear_trend(
                df["accuracy"], forecast_days, confidence_interval
            )

            # 4. Seasonal Decomposition (if enough data)
            if len(df) >= 60:  # Need at least 2 months for seasonal analysis
                forecasts["seasonal"] = self._forecast_seasonal(
                    df["accuracy"], forecast_days, confidence_interval
                )

            # Ensemble forecast (combine multiple methods)
            ensemble_forecast = self._create_ensemble_forecast(forecasts)

            # Generate forecast dates
            forecast_dates = []
            current_date = end_date + timedelta(days=1)
            for i in range(forecast_days):
                forecast_dates.append((current_date + timedelta(days=i)).isoformat())

            # Calculate forecast confidence and reliability
            forecast_quality = self._assess_forecast_quality(df["accuracy"], forecasts)

            logger.info(f"📈 Generated {forecast_days}-day forecast for {method.name}")

            return {
                "success": True,
                "method_id": method_id,
                "method_name": method.name,
                "forecast_period": {
                    "start_date": (end_date + timedelta(days=1)).isoformat(),
                    "end_date": (end_date + timedelta(days=forecast_days)).isoformat(),
                    "days": forecast_days,
                },
                "historical_period": {
                    "start_date": start_date.isoformat(),
                    "end_date": end_date.isoformat(),
                    "data_points": len(df),
                },
                "confidence_interval": confidence_interval,
                "forecast_dates": forecast_dates,
                "individual_forecasts": forecasts,
                "ensemble_forecast": ensemble_forecast,
                "forecast_quality": forecast_quality,
                "insights": self._generate_forecast_insights(
                    df["accuracy"], ensemble_forecast, forecast_quality
                ),
            }

        except Exception as e:
            logger.error(f"Error generating performance forecast: {str(e)}")
            return {"error": str(e)}

    def create_performance_report(
        self,
        report_type: str = "comprehensive",
        time_periods: List[int] = None,
        include_forecasts: bool = True,
    ) -> Dict[str, Any]:
        """
        Create comprehensive performance analysis report

        Args:
            report_type: Type of report ('summary', 'detailed', 'comprehensive')
            time_periods: Time periods to analyze [7, 30, 90, 365]
            include_forecasts: Whether to include performance forecasts

        Returns:
            Dict with comprehensive performance report
        """
        try:
            if time_periods is None:
                time_periods = (
                    [7, 30, 90] if report_type == "summary" else [7, 30, 90, 365]
                )

            logger.info(f"📊 Creating {report_type} performance report")

            report = {
                "report_metadata": {
                    "report_type": report_type,
                    "generated_at": timezone.now().isoformat(),
                    "time_periods_analyzed": time_periods,
                    "include_forecasts": include_forecasts,
                },
                "executive_summary": {},
                "method_analysis": {},
                "correlation_analysis": {},
                "pattern_analysis": {},
                "performance_trends": {},
                "forecasts": {} if include_forecasts else None,
                "recommendations": [],
            }

            # Get all active methods
            methods = PredictionMethod.objects.all()

            # Analyze each time period
            for period in time_periods:
                period_analysis = {}

                # Get method performance for this period
                for method in methods:
                    method_metrics = (
                        self.performance_tracker.calculate_performance_metrics(
                            method.code, period
                        )
                    )

                    if "error" not in method_metrics:
                        period_analysis[method.code] = method_metrics

                report["method_analysis"][f"{period}_days"] = period_analysis

            # Correlation Analysis (for longest period)
            max_period = max(time_periods)
            correlation_results = self.analyze_method_correlations(max_period)
            if "error" not in correlation_results:
                report["correlation_analysis"] = correlation_results

            # Pattern Discovery (for longest period)
            pattern_results = self.discover_historical_patterns(
                lookback_period=max_period
            )
            if "error" not in pattern_results:
                report["pattern_analysis"] = pattern_results

            # Performance Trends
            report["performance_trends"] = self._analyze_performance_trends(
                time_periods
            )

            # Generate Forecasts
            if include_forecasts:
                forecast_results = {}
                for method in methods:
                    forecast = self.generate_performance_forecast(method.code, 30)
                    if "error" not in forecast:
                        forecast_results[method.code] = forecast
                report["forecasts"] = forecast_results

            # Executive Summary
            report["executive_summary"] = self._create_executive_summary(report)

            # Generate Recommendations
            report["recommendations"] = self._generate_performance_recommendations(
                report
            )

            logger.info(
                f"📋 Performance report completed: {len(methods)} methods analyzed"
            )

            return report

        except Exception as e:
            logger.error(f"Error creating performance report: {str(e)}")
            return {"error": str(e)}

    # Private helper methods for pattern detection
    def _detect_seasonal_patterns(
        self, dates: List[date], accuracies: List[float]
    ) -> Dict[str, Any]:
        """Detect seasonal patterns in performance data"""
        try:
            # Group by day of week
            day_of_week_performance = defaultdict(list)

            for date_val, accuracy in zip(dates, accuracies):
                day_of_week = date_val.weekday()  # 0 = Monday
                day_of_week_performance[day_of_week].append(accuracy)

            # Calculate average performance by day of week
            day_averages = {}
            for day, accs in day_of_week_performance.items():
                if accs:
                    day_averages[day] = statistics.mean(accs)

            if len(day_averages) < 5:  # Need at least 5 days
                return {"confidence": 0.0, "pattern": "insufficient_data"}

            # Check if there's significant variation
            avg_values = list(day_averages.values())
            if statistics.stdev(avg_values) < 5:  # Less than 5% variation
                return {"confidence": 0.0, "pattern": "no_significant_variation"}

            # Find best and worst days
            best_day = max(day_averages.items(), key=lambda x: x[1])
            worst_day = min(day_averages.items(), key=lambda x: x[1])

            day_names = [
                "Monday",
                "Tuesday",
                "Wednesday",
                "Thursday",
                "Friday",
                "Saturday",
                "Sunday",
            ]

            return {
                "confidence": min(
                    1.0, statistics.stdev(avg_values) / 20
                ),  # Scale to 0-1
                "pattern": "day_of_week_variation",
                "best_day": {
                    "day": day_names[best_day[0]],
                    "average_accuracy": best_day[1],
                },
                "worst_day": {
                    "day": day_names[worst_day[0]],
                    "average_accuracy": worst_day[1],
                },
                "day_averages": {
                    day_names[day]: acc for day, acc in day_averages.items()
                },
            }

        except Exception as e:
            return {"confidence": 0.0, "error": str(e)}

    def _detect_cyclical_patterns(self, accuracies: List[float]) -> Dict[str, Any]:
        """Detect cyclical patterns using FFT"""
        try:
            if len(accuracies) < 20:
                return {"confidence": 0.0, "pattern": "insufficient_data"}

            # Perform FFT to detect cyclical patterns
            fft_result = np.fft.fft(accuracies)
            freqs = np.fft.fftfreq(len(accuracies))

            # Find dominant frequencies
            power_spectrum = np.abs(fft_result)
            dominant_freq_idx = (
                np.argmax(power_spectrum[1 : len(power_spectrum) // 2]) + 1
            )
            dominant_freq = freqs[dominant_freq_idx]

            if abs(dominant_freq) < 0.01:  # Very low frequency
                return {"confidence": 0.0, "pattern": "no_significant_cycle"}

            cycle_length = 1 / abs(dominant_freq)
            confidence = min(
                1.0, power_spectrum[dominant_freq_idx] / np.mean(power_spectrum)
            )

            return {
                "confidence": min(1.0, confidence / 10),  # Scale appropriately
                "pattern": "cyclical",
                "cycle_length_days": round(cycle_length),
                "dominant_frequency": dominant_freq,
                "cycle_strength": confidence,
            }

        except Exception as e:
            return {"confidence": 0.0, "error": str(e)}

    def _detect_trend_patterns(
        self, dates: List[date], accuracies: List[float]
    ) -> Dict[str, Any]:
        """Detect trend patterns using linear regression"""
        try:
            if len(accuracies) < 10:
                return {"confidence": 0.0, "pattern": "insufficient_data"}

            # Convert dates to numeric values (days since first date)
            first_date = dates[0]
            x_values = [(d - first_date).days for d in dates]

            # Perform linear regression
            slope, intercept, r_value, p_value, std_err = stats.linregress(
                x_values, accuracies
            )

            # Determine trend direction and strength
            if abs(slope) < 0.01:  # Very small slope
                trend_direction = "stable"
            elif slope > 0:
                trend_direction = "improving"
            else:
                trend_direction = "declining"

            # Confidence based on R-squared and p-value
            r_squared = r_value**2
            significance = "significant" if p_value < 0.05 else "not_significant"

            return {
                "confidence": r_squared,
                "pattern": "trend",
                "trend_direction": trend_direction,
                "slope": slope,
                "r_squared": r_squared,
                "p_value": p_value,
                "significance": significance,
                "trend_strength": abs(slope)
                * 100,  # Convert to percentage points per day
            }

        except Exception as e:
            return {"confidence": 0.0, "error": str(e)}

    def _detect_volatility_patterns(self, accuracies: List[float]) -> Dict[str, Any]:
        """Detect volatility patterns and regime changes"""
        try:
            if len(accuracies) < 20:
                return {"confidence": 0.0, "pattern": "insufficient_data"}

            # Calculate rolling volatility (standard deviation over windows)
            window_size = min(10, len(accuracies) // 3)
            rolling_volatilities = []

            for i in range(window_size, len(accuracies)):
                window_data = accuracies[i - window_size : i]
                volatility = (
                    statistics.stdev(window_data) if len(window_data) > 1 else 0
                )
                rolling_volatilities.append(volatility)

            if not rolling_volatilities:
                return {"confidence": 0.0, "pattern": "insufficient_data"}

            # Detect volatility regimes
            avg_volatility = statistics.mean(rolling_volatilities)
            volatility_std = (
                statistics.stdev(rolling_volatilities)
                if len(rolling_volatilities) > 1
                else 0
            )

            high_volatility_threshold = avg_volatility + volatility_std
            low_volatility_threshold = avg_volatility - volatility_std

            # Count regime periods
            high_vol_periods = sum(
                1 for v in rolling_volatilities if v > high_volatility_threshold
            )
            low_vol_periods = sum(
                1 for v in rolling_volatilities if v < low_volatility_threshold
            )

            volatility_pattern = "stable"
            if high_vol_periods > len(rolling_volatilities) * 0.3:
                volatility_pattern = "high_volatility"
            elif low_vol_periods > len(rolling_volatilities) * 0.3:
                volatility_pattern = "low_volatility"

            return {
                "confidence": (
                    min(1.0, volatility_std / avg_volatility)
                    if avg_volatility > 0
                    else 0
                ),
                "pattern": "volatility",
                "volatility_pattern": volatility_pattern,
                "average_volatility": avg_volatility,
                "volatility_std": volatility_std,
                "high_volatility_periods": high_vol_periods,
                "low_volatility_periods": low_vol_periods,
            }

        except Exception as e:
            return {"confidence": 0.0, "error": str(e)}

    def _detect_performance_clusters(
        self, data: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Detect performance clusters and regimes"""
        try:
            if len(data) < 20:
                return {"confidence": 0.0, "pattern": "insufficient_data"}

            accuracies = [d["accuracy"] for d in data]

            # Simple clustering based on performance levels
            high_threshold = np.percentile(accuracies, 75)
            low_threshold = np.percentile(accuracies, 25)

            high_performance_periods = []
            medium_performance_periods = []
            low_performance_periods = []

            for i, acc in enumerate(accuracies):
                if acc >= high_threshold:
                    high_performance_periods.append(i)
                elif acc <= low_threshold:
                    low_performance_periods.append(i)
                else:
                    medium_performance_periods.append(i)

            # Calculate cluster statistics
            total_periods = len(accuracies)

            cluster_stats = {
                "high_performance": {
                    "count": len(high_performance_periods),
                    "percentage": len(high_performance_periods) / total_periods * 100,
                    "average_accuracy": (
                        statistics.mean(
                            [accuracies[i] for i in high_performance_periods]
                        )
                        if high_performance_periods
                        else 0
                    ),
                },
                "medium_performance": {
                    "count": len(medium_performance_periods),
                    "percentage": len(medium_performance_periods) / total_periods * 100,
                    "average_accuracy": (
                        statistics.mean(
                            [accuracies[i] for i in medium_performance_periods]
                        )
                        if medium_performance_periods
                        else 0
                    ),
                },
                "low_performance": {
                    "count": len(low_performance_periods),
                    "percentage": len(low_performance_periods) / total_periods * 100,
                    "average_accuracy": (
                        statistics.mean(
                            [accuracies[i] for i in low_performance_periods]
                        )
                        if low_performance_periods
                        else 0
                    ),
                },
            }

            # Confidence based on cluster separation
            high_avg = cluster_stats["high_performance"]["average_accuracy"]
            low_avg = cluster_stats["low_performance"]["average_accuracy"]
            confidence = (
                min(1.0, (high_avg - low_avg) / 50) if high_avg > low_avg else 0
            )

            return {
                "confidence": confidence,
                "pattern": "performance_clusters",
                "cluster_stats": cluster_stats,
                "thresholds": {
                    "high_threshold": high_threshold,
                    "low_threshold": low_threshold,
                },
            }

        except Exception as e:
            return {"confidence": 0.0, "error": str(e)}

    def _detect_anomalies(
        self, dates: List[date], accuracies: List[float]
    ) -> Dict[str, Any]:
        """Detect anomalies in performance data"""
        try:
            if len(accuracies) < 20:
                return {"confidence": 0.0, "pattern": "insufficient_data"}

            # Use Z-score method for anomaly detection
            mean_accuracy = statistics.mean(accuracies)
            std_accuracy = statistics.stdev(accuracies) if len(accuracies) > 1 else 0

            if std_accuracy == 0:
                return {"confidence": 0.0, "pattern": "no_variation"}

            anomalies = []
            anomaly_threshold = 2.0  # Z-score threshold

            for i, (date_val, accuracy) in enumerate(zip(dates, accuracies)):
                z_score = abs(accuracy - mean_accuracy) / std_accuracy

                if z_score > anomaly_threshold:
                    anomaly_type = (
                        "positive" if accuracy > mean_accuracy else "negative"
                    )
                    anomalies.append(
                        {
                            "date": date_val.isoformat(),
                            "accuracy": accuracy,
                            "z_score": z_score,
                            "type": anomaly_type,
                            "severity": "high" if z_score > 3 else "medium",
                        }
                    )

            confidence = (
                min(1.0, len(anomalies) / len(accuracies) * 5) if anomalies else 0
            )

            return {
                "confidence": confidence,
                "pattern": "anomalies",
                "anomaly_count": len(anomalies),
                "anomaly_rate": len(anomalies) / len(accuracies) * 100,
                "anomalies": anomalies,
                "detection_threshold": anomaly_threshold,
            }

        except Exception as e:
            return {"confidence": 0.0, "error": str(e)}

    # Helper methods continued in next part due to length limit...
