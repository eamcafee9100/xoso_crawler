#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
🚀 ENHANCED DEEP FREQUENCY ANALYZER VIEWS
Professional analyst interface for advanced lottery prediction system
"""

import json
import logging
from datetime import date, datetime, timedelta
from typing import Dict, List, Optional

from django.contrib import messages
from django.core.cache import cache
from django.core.paginator import Paginator
from django.http import HttpResponse, JsonResponse
from django.shortcuts import redirect, render
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods


class CustomJSONEncoder(json.JSONEncoder):
    """Custom JSON encoder to handle boolean, numpy, and datetime objects"""

    def default(self, o):
        import numpy as np

        # Handle numpy arrays first (before other checks)
        if hasattr(o, "tolist") and hasattr(o, "dtype"):
            return o.tolist()
        # Handle numpy scalars specifically
        elif isinstance(o, (np.integer, np.floating, np.complexfloating)):
            return o.item()  # Convert to Python native type
        elif isinstance(o, np.ndarray):
            return o.tolist()
        elif isinstance(o, np.bool_):
            return "enabled" if bool(o) else "disabled"
        # Handle regular booleans
        elif isinstance(o, bool):
            return "enabled" if o else "disabled"
        # Handle numpy scalars by dtype check (fallback)
        elif hasattr(o, "dtype"):
            if "bool" in str(o.dtype):
                return "enabled" if bool(o) else "disabled"
            elif "int" in str(o.dtype) or "float" in str(o.dtype):
                return o.item() if hasattr(o, "item") else float(o)
        # Handle datetime objects
        elif isinstance(o, datetime):
            return o.isoformat()
        elif isinstance(o, date):
            return o.isoformat()
        # Handle objects with __dict__
        elif hasattr(o, "__dict__"):
            return o.__dict__
        return super().default(o)

    def encode(self, o):
        """Override encode to handle booleans in nested structures"""
        return super().encode(self._convert_booleans(o))

    def _convert_booleans(self, obj):
        """Recursively convert all boolean values (including numpy) to strings"""
        import numpy as np

        # Handle numpy arrays first (before checking dtype)
        if hasattr(obj, "tolist") and hasattr(obj, "dtype"):
            return self._convert_booleans(obj.tolist())
        # Handle numpy scalars specifically
        elif isinstance(obj, (np.integer, np.floating, np.complexfloating)):
            return obj.item()  # Convert to Python native type
        elif isinstance(obj, np.ndarray):
            return self._convert_booleans(obj.tolist())
        elif isinstance(obj, np.bool_):
            return "enabled" if bool(obj) else "disabled"
        # Handle regular Python booleans
        elif isinstance(obj, bool):
            return "enabled" if obj else "disabled"
        # Handle numpy scalars by dtype check (fallback)
        elif hasattr(obj, "dtype"):
            if "bool" in str(obj.dtype):
                return "enabled" if bool(obj) else "disabled"
            elif "int" in str(obj.dtype) or "float" in str(obj.dtype):
                return obj.item() if hasattr(obj, "item") else float(obj)
            else:
                return obj.tolist() if hasattr(obj, "tolist") else obj
        # Handle dictionaries
        elif isinstance(obj, dict):
            return {key: self._convert_booleans(value) for key, value in obj.items()}
        # Handle lists
        elif isinstance(obj, list):
            return [self._convert_booleans(item) for item in obj]
        # Handle tuples
        elif isinstance(obj, tuple):
            return tuple(self._convert_booleans(item) for item in obj)
        # Handle objects with __dict__ (but avoid strings, numbers, etc.)
        elif hasattr(obj, "__dict__") and not isinstance(
            obj, (str, int, float, datetime, date)
        ):
            return {
                key: self._convert_booleans(value)
                for key, value in obj.__dict__.items()
            }
        else:
            return obj


def safe_json_response(data, status=200):
    """Create a JsonResponse with custom encoder to handle boolean values"""
    json_data = json.dumps(data, cls=CustomJSONEncoder, ensure_ascii=False)
    return HttpResponse(json_data, content_type="application/json", status=status)


from analytic_frequence.enhanced_deep_frequency_analyzer import (
    EnhancedDeepFrequencyAnalyzer,
    export_lottery_analysis_report,
    generate_lottery_visualization_data,
    get_adaptive_lottery_predictions,
    get_enhanced_frequency_insights,
    validate_lottery_predictions,
)

logger = logging.getLogger(__name__)


# =====================================
# 🔧 INTERACTIVE ANALYSIS TOOL VIEWS
# =====================================


def enhanced_analyzer_dashboard(request):
    """
    🎯 MAIN DASHBOARD: Interactive Analysis Tool
    Real-time analysis interface for professional analysts
    """
    try:
        context = {
            "page_title": "Enhanced Frequency Analyzer - Interactive Dashboard",
            "current_date": timezone.now().date(),
            "default_start_date": (
                timezone.now().date() - timedelta(days=180)
            ).isoformat(),
            "default_end_date": timezone.now().date().isoformat(),
            "significance_levels": [0.01, 0.05, 0.1],
            "analysis_methods": [
                "hot_numbers",
                "cold_numbers",
                "cyclical_patterns",
                "mean_reversion",
                "momentum_patterns",
                "seasonal_effects",
            ],
            "user_type": "analyst",
        }

        # Check for cached recent analysis
        cached_analysis = cache.get("enhanced_analyzer_recent_analysis")
        if cached_analysis:
            context["recent_analysis"] = cached_analysis
            context["has_recent_data"] = True
        else:
            context["has_recent_data"] = False

        return render(
            request, "predictions_tracker/enhanced_analyzer_dashboard.html", context
        )

    except Exception as e:
        logger.error(f"❌ Dashboard view error: {e}")
        messages.error(request, f"Dashboard loading failed: {e}")
        return render(
            request,
            "predictions_tracker/enhanced_analyzer_dashboard.html",
            {"error": str(e), "page_title": "Enhanced Frequency Analyzer - Error"},
        )


def cyclical_analysis_workstation(request):
    """
    🎯 ADVANCED WORKSTATION: Multi-tab analyst interface with cyclical focus
    Professional workstation for detailed cyclical pattern analysis
    """
    try:
        context = {
            "page_title": "Cyclical Analysis Workstation - Professional Interface",
            "current_date": timezone.now().date(),
            "default_start_date": (
                timezone.now().date() - timedelta(days=180)
            ).isoformat(),
            "default_end_date": timezone.now().date().isoformat(),
            "significance_levels": [0.01, 0.05, 0.1],
            "cycle_types": ["monthly", "weekly", "daily"],
            "focus_cycle": "monthly",  # Primary focus as requested
            "analysis_methods": [
                "overdue_numbers",
                "momentum_cycles",
                "seasonal_patterns",
                "cyclical_predictions",
                "timing_signals",
            ],
            "user_type": "professional_analyst",
            "interface_type": "workstation",
        }

        # Check for cached recent analysis
        cached_analysis = cache.get("enhanced_analyzer_recent_analysis")
        if cached_analysis:
            context["recent_analysis"] = cached_analysis
            context["has_recent_data"] = True

            # Extract cyclical insights for immediate display
            cyclical_insights = _extract_cyclical_insights(cached_analysis)
            context["cyclical_insights"] = cyclical_insights
        else:
            context["has_recent_data"] = False
            context["cyclical_insights"] = None

        return render(
            request, "predictions_tracker/cyclical_analysis_workstation.html", context
        )

    except Exception as e:
        logger.error(f"❌ Cyclical Analysis Workstation error: {e}")
        messages.error(request, f"Workstation loading failed: {e}")
        return render(
            request,
            "predictions_tracker/cyclical_analysis_workstation.html",
            {"error": str(e), "page_title": "Cyclical Analysis Workstation - Error"},
        )


@csrf_exempt
@require_http_methods(["POST"])
def run_enhanced_analysis(request):
    """
    ⚡ REAL-TIME ANALYSIS: AJAX endpoint for instant analysis
    """
    try:
        # Parse request parameters
        data = json.loads(request.body)
        start_date = datetime.strptime(data.get("start_date"), "%Y-%m-%d").date()
        end_date = datetime.strptime(data.get("end_date"), "%Y-%m-%d").date()

        # Handle significance level with proper validation
        significance_level_str = data.get("significance_level", "0.05")
        try:
            significance_level = (
                float(significance_level_str) if significance_level_str else 0.05
            )
        except (ValueError, TypeError):
            significance_level = 0.05

        enable_full_pipeline = data.get("enable_full_pipeline", True)

        logger.info(f"🚀 Running enhanced analysis: {start_date} to {end_date}")

        # Run analysis
        analyzer = EnhancedDeepFrequencyAnalyzer()

        if enable_full_pipeline:
            results = analyzer.analyze_with_full_pipeline(
                start_date=start_date,
                end_date=end_date,
                significance_level=significance_level,
            )
        else:
            results = analyzer.analyze_frequency_patterns_enhanced(
                start_date=start_date,
                end_date=end_date,
                significance_level=significance_level,
            )

        # Cache results for 15 minutes
        cache.set("enhanced_analyzer_recent_analysis", results, 900)

        # Generate visualization data
        viz_data = analyzer.generate_visualization_data(results)

        # Prepare response with formatted data
        response_data = {
            "status": "success",
            "analysis_results": results,
            "visualization_data": viz_data,
            "analysis_metadata": {
                "execution_time": timezone.now().isoformat(),
                "date_range": f"{start_date} to {end_date}",
                "significance_level": significance_level,
                "total_components": len(results),
            },
            "quick_insights": _extract_predictive_insights(results, end_date),
        }

        # DEBUG: Log data types before JSON serialization
        logger.info("🔍 Debugging response_data before JSON serialization:")
        _debug_log_boolean_values(response_data, "response_data")

        # SAFETY: Pre-convert all boolean values before JSON response
        encoder = CustomJSONEncoder()
        safe_response_data = encoder._convert_booleans(response_data)

        logger.info("✅ Pre-converted boolean values to strings")

        return safe_json_response(safe_response_data)

    except Exception as e:
        logger.error(f"❌ Analysis execution failed: {e}")

        error_data = {
            "status": "error",
            "error_message": str(e),
            "error_type": type(e).__name__,
        }

        # SAFETY: Pre-convert any boolean values in error response
        encoder = CustomJSONEncoder()
        safe_error_data = encoder._convert_booleans(error_data)

        return safe_json_response(safe_error_data, status=500)


@csrf_exempt
@require_http_methods(["POST"])
def validate_predictions(request):
    """
    🔍 VALIDATION INTERFACE: Test predictions against actual results
    """
    try:
        data = json.loads(request.body)
        actual_results = data.get("actual_results", [])
        prediction_date = datetime.strptime(
            data.get("prediction_date"), "%Y-%m-%d"
        ).date()

        # Get recent analysis results
        cached_analysis = cache.get("enhanced_analyzer_recent_analysis")
        if not cached_analysis:
            return safe_json_response(
                {
                    "status": "error",
                    "error_message": "No recent analysis found. Please run analysis first.",
                },
                status=400,
            )

        # Run validation
        analyzer = EnhancedDeepFrequencyAnalyzer()
        validation_results = analyzer.validate_predictions_against_actual(
            cached_analysis, actual_results, prediction_date
        )

        # Learn from validation (feedback loop)
        analyzer.learn_from_results(validation_results)
        learning_progress = analyzer.get_learning_progress()

        response_data = {
            "status": "success",
            "validation_results": validation_results,
            "learning_progress": learning_progress,
            "validation_metadata": {
                "validated_at": timezone.now().isoformat(),
                "actual_results_count": len(actual_results),
                "prediction_date": prediction_date.isoformat(),
            },
        }

        return safe_json_response(response_data)

    except Exception as e:
        logger.error(f"❌ Validation failed: {e}")
        return safe_json_response(
            {"status": "error", "error_message": str(e)}, status=500
        )


@csrf_exempt
@require_http_methods(["POST"])
def get_adaptive_predictions(request):
    """
    🎯 ADAPTIVE PREDICTIONS: Get learning-enhanced predictions
    """
    try:
        data = json.loads(request.body)

        # Get recent analysis
        cached_analysis = cache.get("enhanced_analyzer_recent_analysis")
        if not cached_analysis:
            return safe_json_response(
                {
                    "status": "error",
                    "error_message": "No base analysis found. Please run analysis first.",
                },
                status=400,
            )

        # Generate adaptive predictions
        analyzer = EnhancedDeepFrequencyAnalyzer()
        adaptive_predictions = analyzer.get_adaptive_predictions(cached_analysis)
        learning_summary = analyzer.get_learning_progress()

        response_data = {
            "status": "success",
            "adaptive_predictions": adaptive_predictions,
            "learning_summary": learning_summary,
            "generation_metadata": {
                "generated_at": timezone.now().isoformat(),
                "base_analysis_components": len(cached_analysis),
                "adaptive_recommendations_count": len(
                    adaptive_predictions.get("adaptive_weighted_recommendations", [])
                ),
            },
        }

        return safe_json_response(response_data)

    except Exception as e:
        logger.error(f"❌ Adaptive predictions failed: {e}")
        return safe_json_response(
            {"status": "error", "error_message": str(e)}, status=500
        )


# =====================================
# 📊 COMPREHENSIVE REPORT VIEWER VIEWS
# =====================================


def analysis_reports_center(request):
    """
    📋 REPORTS CENTER: Historical analysis and performance tracking
    """
    try:
        # Get pagination parameters
        page = request.GET.get("page", 1)
        per_page = int(request.GET.get("per_page", 20))

        # Get filter parameters
        date_from = request.GET.get("date_from")
        date_to = request.GET.get("date_to")
        report_type = request.GET.get("report_type", "all")

        # Initialize analyzer for historical data
        analyzer = EnhancedDeepFrequencyAnalyzer()

        # Get validation history (simulated for now - replace with actual DB queries)
        validation_history = analyzer.validator.validation_history

        # Apply filters
        filtered_reports = validation_history
        if date_from:
            filtered_reports = [
                r
                for r in filtered_reports
                if datetime.fromisoformat(r["prediction_date"]).date()
                >= datetime.strptime(date_from, "%Y-%m-%d").date()
            ]
        if date_to:
            filtered_reports = [
                r
                for r in filtered_reports
                if datetime.fromisoformat(r["prediction_date"]).date()
                <= datetime.strptime(date_to, "%Y-%m-%d").date()
            ]

        # Pagination
        paginator = Paginator(filtered_reports, per_page)
        reports_page = paginator.get_page(page)

        # Performance metrics
        performance_summary = analyzer.validator.get_performance_summary()
        recent_validation_report = analyzer.validator.generate_validation_report(
            days_back=30
        )

        context = {
            "page_title": "Analysis Reports Center",
            "reports_page": reports_page,
            "performance_summary": performance_summary,
            "recent_validation_report": recent_validation_report,
            "total_reports": len(validation_history),
            "filter_params": {
                "date_from": date_from,
                "date_to": date_to,
                "report_type": report_type,
            },
            "pagination_info": {
                "current_page": page,
                "per_page": per_page,
                "total_pages": paginator.num_pages,
                "has_previous": reports_page.has_previous(),
                "has_next": reports_page.has_next(),
            },
        }

        return render(
            request, "predictions_tracker/analysis_reports_center.html", context
        )

    except Exception as e:
        logger.error(f"❌ Reports center error: {e}")
        messages.error(request, f"Reports loading failed: {e}")
        return render(
            request,
            "predictions_tracker/analysis_reports_center.html",
            {"error": str(e), "page_title": "Analysis Reports Center - Error"},
        )


def export_analysis_report(request):
    """
    📄 EXPORT FUNCTIONALITY: Generate and download reports
    """
    try:
        # Get export parameters
        format_type = request.GET.get("format", "json")
        date_from = request.GET.get("date_from")
        date_to = request.GET.get("date_to")

        start_date = (
            datetime.strptime(date_from, "%Y-%m-%d").date() if date_from else None
        )
        end_date = datetime.strptime(date_to, "%Y-%m-%d").date() if date_to else None

        # Generate report
        report_path = export_lottery_analysis_report(
            start_date=start_date, end_date=end_date, format=format_type
        )

        if not report_path:
            messages.error(request, "Report generation failed")
            return redirect("analysis_reports_center")

        # Read and serve file
        with open(report_path, "r", encoding="utf-8") as f:
            report_content = f.read()

        response = HttpResponse(
            report_content,
            content_type="application/json" if format_type == "json" else "text/csv",
        )
        response["Content-Disposition"] = (
            f'attachment; filename="{report_path.split("/")[-1]}"'
        )

        return response

    except Exception as e:
        logger.error(f"❌ Export failed: {e}")
        messages.error(request, f"Export failed: {e}")
        return redirect("analysis_reports_center")


def get_performance_trends(request):
    """
    📈 PERFORMANCE TRENDS: AJAX endpoint for trend charts
    """
    try:
        days_back = int(request.GET.get("days_back", 30))
        chart_type = request.GET.get("chart_type", "performance_timeline")

        analyzer = EnhancedDeepFrequencyAnalyzer()

        # Get validation history
        validation_history = analyzer.validator.validation_history
        recent_validations = (
            validation_history[-days_back:] if validation_history else []
        )

        # Generate trend data based on chart type
        if chart_type == "performance_timeline":
            trend_data = [
                {
                    "date": v["prediction_date"],
                    "precision": v["overall_performance"]["precision"],
                    "recall": v["overall_performance"]["recall"],
                    "f1_score": v["overall_performance"]["f1_score"],
                }
                for v in recent_validations
            ]
        elif chart_type == "roi_analysis":
            trend_data = [
                {
                    "date": v["prediction_date"],
                    "profit_loss": v.get("roi_analysis", {}).get("profit_loss", 0),
                    "roi_percentage": v.get("roi_analysis", {}).get(
                        "roi_percentage", 0
                    ),
                }
                for v in recent_validations
            ]
        elif chart_type == "method_weights_evolution":
            learning_summary = analyzer.feedback_system.get_learning_summary()
            trend_data = learning_summary.get("weight_evolution", {})
        else:
            trend_data = []

        return safe_json_response(
            {
                "status": "success",
                "chart_type": chart_type,
                "trend_data": trend_data,
                "metadata": {
                    "days_back": days_back,
                    "data_points": len(trend_data),
                    "generated_at": timezone.now().isoformat(),
                },
            }
        )

    except Exception as e:
        logger.error(f"❌ Performance trends failed: {e}")
        return safe_json_response(
            {"status": "error", "error_message": str(e)}, status=500
        )


# =====================================
# 🛠️ UTILITY FUNCTIONS
# =====================================


def _extract_cyclical_insights(analysis_results: Dict) -> Dict:
    """
    Extract specialized cyclical insights for the workstation interface.
    Focus on overdue analysis, momentum cycles, and seasonal patterns.
    """
    try:
        cyclical_data = {
            "overdue_analysis": {},
            "momentum_cycles": {},
            "seasonal_patterns": {},
            "cycle_wheels": {},
            "real_time_tracking": {},
            "monthly_heat_map": {},
        }

        if not analysis_results or not isinstance(analysis_results, dict):
            return cyclical_data

        # Extract digit frequency for cyclical analysis
        digit_freq = analysis_results.get("digit_frequency", {}).get("analysis", {})
        timing_analysis = analysis_results.get("timing_analysis", {})

        # Overdue Analysis - Primary focus
        current_date = timezone.now().date()
        for digit, freq_data in digit_freq.items():
            if isinstance(freq_data, dict):
                frequency = freq_data.get("frequency", 0)
                last_seen = freq_data.get("last_seen", 30)  # days since last appearance
                expected_frequency = freq_data.get("expected_frequency", 10)

                # Calculate overdue status
                days_overdue = max(0, last_seen - expected_frequency)
                overdue_severity = (
                    "critical"
                    if days_overdue > 20
                    else "moderate" if days_overdue > 10 else "normal"
                )

                cyclical_data["overdue_analysis"][digit] = {
                    "days_since_last": last_seen,
                    "days_overdue": days_overdue,
                    "severity": overdue_severity,
                    "probability_next": min(0.95, days_overdue / 25.0),
                    "cycle_position": (last_seen % 30)
                    / 30.0,  # Position in 30-day cycle
                    "color_code": (
                        "#dc3545"
                        if overdue_severity == "critical"
                        else "#fd7e14" if overdue_severity == "moderate" else "#28a745"
                    ),
                }

        # Momentum Cycles - Secondary focus
        for digit, freq_data in digit_freq.items():
            if isinstance(freq_data, dict):
                trend = freq_data.get("trend", "stable")
                percentage = freq_data.get("percentage", 0)
                recent_appearances = freq_data.get("recent_appearances", 0)

                momentum_strength = (
                    "high"
                    if trend == "up" and percentage > 12
                    else "medium" if trend == "up" else "low"
                )

                cyclical_data["momentum_cycles"][digit] = {
                    "trend": trend,
                    "strength": momentum_strength,
                    "acceleration": (
                        "increasing" if recent_appearances > percentage else "stable"
                    ),
                    "confidence": min(1.0, percentage / 15.0),
                    "momentum_score": percentage
                    * (2 if trend == "up" else 1 if trend == "stable" else 0.5),
                }

        # Cycle Wheels Data - Visual representation
        for digit in range(10):
            digit_str = str(digit)
            if digit_str in cyclical_data["overdue_analysis"]:
                overdue_data = cyclical_data["overdue_analysis"][digit_str]
                cyclical_data["cycle_wheels"][digit_str] = {
                    "angle": (
                        overdue_data["cycle_position"] * 360
                    ),  # Position on wheel
                    "radius": min(
                        100, overdue_data["days_since_last"] * 3
                    ),  # Distance from center
                    "color": overdue_data["color_code"],
                    "size": max(10, overdue_data["probability_next"] * 20),  # Dot size
                    "label": f"{digit_str} ({overdue_data['days_since_last']}d)",
                }

        # Real-time Tracking
        cyclical_data["real_time_tracking"] = {
            "total_overdue": len(
                [
                    d
                    for d in cyclical_data["overdue_analysis"].values()
                    if d["severity"] in ["moderate", "critical"]
                ]
            ),
            "critical_count": len(
                [
                    d
                    for d in cyclical_data["overdue_analysis"].values()
                    if d["severity"] == "critical"
                ]
            ),
            "high_momentum": len(
                [
                    d
                    for d in cyclical_data["momentum_cycles"].values()
                    if d["strength"] == "high"
                ]
            ),
        }

        # Set cycle health based on critical count
        cyclical_data["real_time_tracking"]["cycle_health"] = (
            "good"
            if cyclical_data["real_time_tracking"]["critical_count"] < 2
            else "warning"
        )

        return cyclical_data

    except Exception as e:
        logger.error(f"❌ Cyclical insights extraction failed: {e}")
        return {
            "overdue_analysis": {},
            "momentum_cycles": {},
            "seasonal_patterns": {},
            "cycle_wheels": {},
            "real_time_tracking": {"error": str(e)},
            "monthly_heat_map": {},
        }


def _find_digit_frequency_data(data, max_depth=5, current_depth=0):
    """
    Recursively search for digit frequency data in nested structures
    """
    if current_depth > max_depth or not isinstance(data, dict):
        return None

    # Check if current level contains digit-like keys
    keys = list(data.keys())
    digit_keys = [
        k for k in keys if (isinstance(k, str) and k.isdigit()) or k in range(10)
    ]

    if len(digit_keys) >= 5:  # Likely digit frequency data
        return data

    # Recursively search in nested dictionaries
    for key, value in data.items():
        if isinstance(value, dict):
            result = _find_digit_frequency_data(value, max_depth, current_depth + 1)
            if result:
                return result

    return None


def _get_data_structure_summary(data, max_depth=3, current_depth=0):
    """
    Get a summary of the data structure for debugging
    """
    if current_depth > max_depth:
        return "..."

    if isinstance(data, dict):
        if not data:
            return "{}"

        summary = {}
        for key, value in list(data.items())[:5]:  # Limit to first 5 keys
            if isinstance(value, dict):
                summary[key] = _get_data_structure_summary(
                    value, max_depth, current_depth + 1
                )
            elif isinstance(value, list):
                summary[key] = f"[{len(value)} items]"
            else:
                summary[key] = type(value).__name__

        if len(data) > 5:
            summary["..."] = f"and {len(data) - 5} more keys"

        return summary
    elif isinstance(data, list):
        return f"[{len(data)} items]"
    else:
        return type(data).__name__


def _debug_log_boolean_values(obj, path="", max_depth=3, current_depth=0):
    """Debug function to log all boolean values in nested structure"""
    if current_depth > max_depth:
        return

    if isinstance(obj, bool):
        logger.warning(f"🔍 BOOLEAN FOUND at {path}: {obj} (type: {type(obj)})")
    elif isinstance(obj, dict):
        for key, value in obj.items():
            _debug_log_boolean_values(
                value, f"{path}.{key}" if path else key, max_depth, current_depth + 1
            )
    elif isinstance(obj, list):
        for i, item in enumerate(obj):
            if i < 5:  # Only check first 5 items to avoid spam
                _debug_log_boolean_values(
                    item, f"{path}[{i}]", max_depth, current_depth + 1
                )


def _diagnose_data_quality(digit_freq: Dict) -> Dict:
    """
    Phân tích chất lượng dữ liệu để hiểu tại sao điểm số thấp
    """
    diagnosis = {
        "data_completeness": 0,
        "trend_strength": 0,
        "frequency_distribution": {},
        "percentage_distribution": {},
        "issues": [],
        "recommendations": [],
    }

    if not digit_freq:
        diagnosis["issues"].append("No digit frequency data found")
        return diagnosis

    # Analyze data completeness
    complete_records = 0
    missing_frequency = 0
    missing_percentage = 0
    missing_trend = 0

    frequencies = []
    percentages = []
    trends = {"up": 0, "down": 0, "stable": 0}

    for digit, data in digit_freq.items():
        if isinstance(data, dict):
            freq = data.get("frequency", data.get("count", data.get("total", 0)))
            perc = data.get("percentage", data.get("percent", data.get("ratio", 0)))
            trend = data.get("trend", data.get("direction", "stable"))

            if freq and perc and trend:
                complete_records += 1

            if not freq:
                missing_frequency += 1
            else:
                frequencies.append(freq)

            if not perc:
                missing_percentage += 1
            else:
                percentages.append(perc)

            if not trend or trend in ["stable", "none", ""]:
                missing_trend += 1
            else:
                # Normalize trend
                if trend in ["increasing", "rise", "rising", "hot"]:
                    trends["up"] += 1
                elif trend in ["decreasing", "fall", "falling", "cold"]:
                    trends["down"] += 1
                else:
                    trends["stable"] += 1

    total_digits = len(digit_freq)
    diagnosis["data_completeness"] = (
        (complete_records / total_digits) * 100 if total_digits else 0
    )

    # Frequency analysis
    if frequencies:
        avg_freq = sum(frequencies) / len(frequencies)
        max_freq = max(frequencies)
        min_freq = min(frequencies)
        diagnosis["frequency_distribution"] = {
            "average": round(avg_freq, 2),
            "max": max_freq,
            "min": min_freq,
            "range": max_freq - min_freq,
        }

        if max_freq < 10:
            diagnosis["issues"].append(f"Low frequency values (max: {max_freq})")
            diagnosis["recommendations"].append(
                "Consider using relative frequencies or adjusting frequency normalization"
            )

    # Percentage analysis
    if percentages:
        avg_perc = sum(percentages) / len(percentages)
        max_perc = max(percentages)
        min_perc = min(percentages)
        diagnosis["percentage_distribution"] = {
            "average": round(avg_perc, 2),
            "max": round(max_perc, 2),
            "min": round(min_perc, 2),
            "range": round(max_perc - min_perc, 2),
        }

        if max_perc < 15:
            diagnosis["issues"].append(f"Low percentage values (max: {max_perc:.1f}%)")
            diagnosis["recommendations"].append(
                "Data may be too evenly distributed - consider different time periods"
            )

    # Trend analysis
    total_trends = sum(trends.values())
    diagnosis["trend_strength"] = (
        ((trends["up"] + trends["down"]) / total_trends * 100) if total_trends else 0
    )

    if trends["stable"] > trends["up"] + trends["down"]:
        diagnosis["issues"].append(
            "Most digits have stable trends - low predictive signal"
        )
        diagnosis["recommendations"].append(
            "Consider shorter analysis periods to capture more dynamic trends"
        )

    # Data quality issues
    if missing_frequency > total_digits * 0.3:
        diagnosis["issues"].append(
            f"Missing frequency data: {missing_frequency}/{total_digits} digits"
        )

    if missing_percentage > total_digits * 0.3:
        diagnosis["issues"].append(
            f"Missing percentage data: {missing_percentage}/{total_digits} digits"
        )

    if missing_trend > total_digits * 0.5:
        diagnosis["issues"].append(
            f"Missing trend data: {missing_trend}/{total_digits} digits"
        )

    return diagnosis


def _extract_predictive_insights(
    analysis_results: Dict, target_date: Optional[date] = None
) -> Dict:
    """
    Extract focused, actionable predictive insights from analysis results.
    Behaves like a top 0.1% analyst: focuses on high-confidence predictions with clear rationale.
    """
    try:
        insights = {
            "predictions": {
                "high_probability": [],
                "medium_probability": [],
                "cyclical_predictions": {},
            },
            "timing_signals": {"overdue_analysis": {}, "momentum_signals": {}},
            "confidence_scores": {},
            "recommendations": {
                "top_picks": [],
                "risk_assessment": "MEDIUM",
                "expected_roi": 1.2,
            },
        }

        if not analysis_results or not isinstance(analysis_results, dict):
            logger.warning("No valid analysis results provided")
            return insights

        # Debug log the analysis results structure
        logger.info(f"🔍 Analysis results keys: {list(analysis_results.keys())}")

        # Extract digit frequency analysis - try multiple possible paths
        digit_freq = None

        # Try different possible paths for digit frequency data
        possible_paths = [
            ("digit_frequency", "analysis"),
            ("digit_frequency", "digit_analysis"),
            ("frequency_analysis", "digits"),
            ("analysis", "digit_frequency"),
            ("digit_analysis",),
            ("frequency_analysis",),
        ]

        for path in possible_paths:
            temp_data = analysis_results
            for key in path:
                temp_data = (
                    temp_data.get(key, {}) if isinstance(temp_data, dict) else {}
                )

            if temp_data and isinstance(temp_data, dict):
                # Check if this looks like digit frequency data
                sample_keys = list(temp_data.keys())[:3]
                if sample_keys and all(
                    k.isdigit()
                    or k in ["0", "1", "2", "3", "4", "5", "6", "7", "8", "9"]
                    for k in sample_keys
                ):
                    digit_freq = temp_data
                    logger.info(
                        f"✅ Found digit frequency data at path: {' → '.join(path)}"
                    )
                    break

        # If still no digit frequency data, try to extract from any nested structure
        if not digit_freq:
            logger.warning("🔍 Searching for digit data in nested structures...")
            digit_freq = _find_digit_frequency_data(analysis_results)

        if not digit_freq:
            logger.warning(
                "❌ No digit frequency analysis found in any expected location"
            )
            # Log the structure for debugging
            logger.info(
                f"🔍 Available data structure: {_get_data_structure_summary(analysis_results)}"
            )
            return insights

        # Diagnose data quality before processing
        data_diagnosis = _diagnose_data_quality(digit_freq)
        logger.info(f"📊 Data Quality Analysis:")
        logger.info(f"  ✓ Completeness: {data_diagnosis['data_completeness']:.1f}%")
        logger.info(f"  ✓ Trend Strength: {data_diagnosis['trend_strength']:.1f}%")

        if data_diagnosis["frequency_distribution"]:
            freq_dist = data_diagnosis["frequency_distribution"]
            logger.info(
                f"  ✓ Frequency Range: {freq_dist['min']}-{freq_dist['max']} (avg: {freq_dist['average']})"
            )

        if data_diagnosis["percentage_distribution"]:
            perc_dist = data_diagnosis["percentage_distribution"]
            logger.info(
                f"  ✓ Percentage Range: {perc_dist['min']:.1f}%-{perc_dist['max']:.1f}% (avg: {perc_dist['average']:.1f}%)"
            )

        if data_diagnosis["issues"]:
            logger.warning("⚠️ Data Quality Issues:")
            for issue in data_diagnosis["issues"]:
                logger.warning(f"  • {issue}")

        if data_diagnosis["recommendations"]:
            logger.info("💡 Recommendations:")
            for rec in data_diagnosis["recommendations"]:
                logger.info(f"  • {rec}")

        # Position analysis for hot/cold digits
        position_analysis = analysis_results.get("position_analysis", {})
        timing_analysis = analysis_results.get("timing_analysis", {})

        # Multi-factor prediction scoring
        prediction_scores = {}

        logger.info(f"✅ Processing {len(digit_freq)} digits from frequency data")

        for digit, freq_data in digit_freq.items():
            # Handle different data formats
            if not isinstance(freq_data, dict):
                # If freq_data is a simple number, create a basic structure
                if isinstance(freq_data, (int, float)):
                    freq_data = {
                        "frequency": freq_data,
                        "percentage": freq_data,
                        "trend": "stable",
                    }
                else:
                    logger.warning(
                        f"⚠️ Unexpected data format for digit {digit}: {type(freq_data)}"
                    )
                    continue

            # Extract values with fallbacks
            frequency = freq_data.get(
                "frequency", freq_data.get("count", freq_data.get("total", 0))
            )
            percentage = freq_data.get(
                "percentage", freq_data.get("percent", freq_data.get("ratio", 0))
            )
            trend = freq_data.get("trend", freq_data.get("direction", "stable"))

            # Normalize trend values
            if trend in ["increasing", "rise", "rising", "hot"]:
                trend = "up"
            elif trend in ["decreasing", "fall", "falling", "cold"]:
                trend = "down"
            else:
                trend = "stable"

            # Calculate multi-factor score
            frequency_score = min(1.0, frequency / 100.0) if frequency else 0
            momentum_score = 0.8 if trend == "up" else 0.5 if trend == "stable" else 0.2
            significance_score = (
                min(1.0, percentage / 15.0) if percentage else 0
            )  # Normalize to 15% as high

            # Combined score with weights
            total_score = (
                frequency_score * 0.3 + momentum_score * 0.4 + significance_score * 0.3
            ) * 100

            # Debug log for score calculation
            logger.info(
                f"🔢 Digit {digit}: freq={frequency}, %={percentage:.1f}, trend={trend} "
                f"→ freq_score={frequency_score:.2f}, momentum={momentum_score:.2f}, "
                f"sig_score={significance_score:.2f} → TOTAL={total_score:.2f}"
            )

            prediction_scores[digit] = {
                "score": round(total_score, 2),
                "frequency": frequency,
                "trend": trend,
                "percentage": percentage,
            }

        logger.info(
            f"✅ Generated prediction scores for {len(prediction_scores)} digits"
        )

        # Sort by score and categorize
        sorted_predictions = sorted(
            prediction_scores.items(), key=lambda x: x[1]["score"], reverse=True
        )

        # Log top scores for debugging
        logger.info("🏆 Top 5 prediction scores:")
        for i, (digit, data) in enumerate(sorted_predictions[:5]):
            logger.info(f"  #{i+1}: Digit {digit} = {data['score']:.2f} points")

        # High probability predictions (top 5)
        high_prob_count = 0
        for i, (digit, data) in enumerate(sorted_predictions[:5]):
            if data["score"] >= 70:  # High confidence threshold
                rationale = f"Strong {data['trend']} trend with {data['percentage']:.1f}% frequency"
                insights["predictions"]["high_probability"].append(
                    {"digit": digit, "score": data["score"], "rationale": rationale}
                )
                high_prob_count += 1
                logger.info(f"✅ HIGH confidence: Digit {digit} = {data['score']:.2f}")
            else:
                logger.info(
                    f"❌ Below HIGH threshold (70): Digit {digit} = {data['score']:.2f}"
                )

        # Medium probability predictions (next 5)
        medium_prob_count = 0
        for i, (digit, data) in enumerate(sorted_predictions[5:10]):
            if data["score"] >= 50:  # Medium confidence threshold
                rationale = f"Moderate {data['trend']} trend with {data['percentage']:.1f}% frequency"
                insights["predictions"]["medium_probability"].append(
                    {"digit": digit, "score": data["score"], "rationale": rationale}
                )
                medium_prob_count += 1
                logger.info(
                    f"✅ MEDIUM confidence: Digit {digit} = {data['score']:.2f}"
                )
            else:
                logger.info(
                    f"❌ Below MEDIUM threshold (50): Digit {digit} = {data['score']:.2f}"
                )

        logger.info(
            f"📊 Confidence analysis: {high_prob_count} HIGH, {medium_prob_count} MEDIUM predictions"
        )

        # Timing signals from overdue analysis
        overdue_numbers = timing_analysis.get("overdue_numbers", [])
        recent_hot = timing_analysis.get("recent_hot", [])

        for num in overdue_numbers[:3]:  # Top 3 overdue
            if num in prediction_scores:
                days_overdue = 15  # Simplified calculation
                insights["timing_signals"]["overdue_analysis"][num] = {
                    "days_overdue": days_overdue,
                    "probability_next_draw": min(0.9, days_overdue / 20.0),
                    "rationale": f"Overdue {days_overdue} days",
                }

        for num in recent_hot[:3]:  # Top 3 hot numbers
            if num in prediction_scores:
                insights["timing_signals"]["momentum_signals"][num] = {
                    "momentum": "HIGH",
                    "confidence": prediction_scores[num]["score"] / 100.0,
                    "rationale": f"Recently hot with {prediction_scores[num]['trend']} trend",
                }

        # Cyclical predictions
        cyclical_indicators = timing_analysis.get("cyclical_indicators", {})
        short_term = cyclical_indicators.get("short_term", "stable")

        if short_term == "increasing":
            # Find digits that align with increasing cycle
            for digit, data in sorted_predictions[:3]:
                if data["trend"] == "up":
                    insights["predictions"]["cyclical_predictions"][digit] = {
                        "cycle_strength": 0.75,
                        "cycle_phase": "increasing",
                        "rationale": "Aligns with short-term increasing cycle",
                    }

        # Confidence scores
        total_predictions = len(insights["predictions"]["high_probability"]) + len(
            insights["predictions"]["medium_probability"]
        )

        # If no predictions were generated, create fallback predictions
        if total_predictions == 0 and prediction_scores:
            logger.warning(
                "⚠️ No predictions met confidence thresholds. Generating fallback predictions."
            )
            logger.info("🔧 Current thresholds: HIGH ≥ 70, MEDIUM ≥ 50")

            # Analyze score distribution
            all_scores = [data["score"] for data in prediction_scores.values()]
            max_score = max(all_scores) if all_scores else 0
            avg_score = sum(all_scores) / len(all_scores) if all_scores else 0

            logger.info(
                f"📈 Score distribution: MAX={max_score:.2f}, AVG={avg_score:.2f}"
            )

            # Dynamic threshold adjustment based on data quality
            if max_score < 50:
                high_threshold = max_score * 0.8  # 80% of max score
                medium_threshold = max_score * 0.6  # 60% of max score
                logger.info(
                    f"🔧 Lowering thresholds: HIGH ≥ {high_threshold:.1f}, MEDIUM ≥ {medium_threshold:.1f}"
                )
            else:
                high_threshold = 45  # Slightly lower than 50
                medium_threshold = 30  # Keep original fallback threshold
                logger.info(
                    f"🔧 Using adjusted thresholds: HIGH ≥ {high_threshold:.1f}, MEDIUM ≥ {medium_threshold:.1f}"
                )

            # Re-categorize with adjusted thresholds
            for digit, data in sorted_predictions:
                if (
                    data["score"] >= high_threshold
                    and len(insights["predictions"]["high_probability"]) < 3
                ):
                    rationale = f"Adjusted: Strong {data['trend']} trend with {data['percentage']:.1f}% frequency"
                    insights["predictions"]["high_probability"].append(
                        {"digit": digit, "score": data["score"], "rationale": rationale}
                    )
                elif (
                    data["score"] >= medium_threshold
                    and len(insights["predictions"]["medium_probability"]) < 5
                ):
                    rationale = f"Adjusted: {data['trend']} trend with {data['percentage']:.1f}% frequency"
                    insights["predictions"]["medium_probability"].append(
                        {"digit": digit, "score": data["score"], "rationale": rationale}
                    )

            total_predictions = len(insights["predictions"]["high_probability"]) + len(
                insights["predictions"]["medium_probability"]
            )
            logger.info(f"✅ Generated {total_predictions} adjusted predictions")

        overall_confidence = (
            0.8 if total_predictions >= 5 else 0.6 if total_predictions >= 3 else 0.4
        )

        insights["confidence_scores"] = {
            "overall_confidence": overall_confidence,
            "prediction_count": total_predictions,
            "signal_strength": (
                "STRONG"
                if overall_confidence > 0.75
                else "MODERATE" if overall_confidence > 0.5 else "WEAK"
            ),
        }

        # Final recommendations (top picks)
        top_high_prob = insights["predictions"]["high_probability"][:3]
        top_medium_prob = insights["predictions"]["medium_probability"][:2]

        all_top_picks = top_high_prob + top_medium_prob

        insights["recommendations"]["top_picks"] = [
            {
                "digit": pred["digit"],
                "confidence": pred["score"],
                "rationale": pred["rationale"],
            }
            for pred in all_top_picks
        ]

        # Risk assessment
        if overall_confidence > 0.8:
            insights["recommendations"]["risk_assessment"] = "LOW"
            insights["recommendations"]["expected_roi"] = 1.8
        elif overall_confidence > 0.6:
            insights["recommendations"]["risk_assessment"] = "MEDIUM"
            insights["recommendations"]["expected_roi"] = 1.4
        else:
            insights["recommendations"]["risk_assessment"] = "HIGH"
            insights["recommendations"]["expected_roi"] = 1.0

        logger.info(
            f"✅ Extracted {total_predictions} focused predictions with {overall_confidence:.1%} confidence"
        )
        return insights

    except Exception as e:
        logger.error(f"Predictive insights extraction failed: {e}")
        return {
            "predictions": {
                "high_probability": [],
                "medium_probability": [],
                "cyclical_predictions": {},
            },
            "timing_signals": {"overdue_analysis": {}, "momentum_signals": {}},
            "confidence_scores": {"overall_confidence": 0.0, "prediction_count": 0},
            "recommendations": {
                "top_picks": [],
                "risk_assessment": "HIGH",
                "expected_roi": 1.0,
            },
            "error": f"Analysis failed: {str(e)}",
        }


def health_check(request):
    """System health check endpoint"""
    try:
        analyzer = EnhancedDeepFrequencyAnalyzer()

        # Basic system checks
        health_status = {
            "status": "healthy",
            "timestamp": timezone.now().isoformat(),
            "components": {
                "analyzer": "operational",
                "validator": "operational",
                "feedback_system": "operational",
                "visualization_generator": "operational",
            },
            "cache_status": "available" if cache else "unavailable",
            "recent_analysis": (
                "available"
                if cache.get("enhanced_analyzer_recent_analysis")
                else "not_cached"
            ),
        }

        return safe_json_response(health_status)

    except Exception as e:
        return safe_json_response(
            {
                "status": "unhealthy",
                "error": str(e),
                "timestamp": timezone.now().isoformat(),
            },
            status=500,
        )
