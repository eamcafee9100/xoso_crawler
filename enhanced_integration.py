"""
Django Integration for Enhanced Prediction System
Integrates the enhanced system with existing Django views and templates
"""

import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional

from django.http import JsonResponse
from django.shortcuts import render
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.csrf import csrf_exempt

from ml_validation.enhanced_system import (
    EnhancedPredictionResult,
    EnhancedPredictionSystem,
)

# Global enhanced system instance
enhanced_system = None


def get_enhanced_system():
    """Get or create enhanced prediction system instance"""
    global enhanced_system

    if enhanced_system is None:
        enhanced_system = EnhancedPredictionSystem(enable_monitoring=True)
        enhanced_system.initialize_system(historical_days=100)
        logging.info("Enhanced Prediction System initialized")

    return enhanced_system


def enhanced_predict_view(request):
    """
    Enhanced version of the predict view with validation and optimization
    """
    from results.models import KetQuaXoSo

    try:
        # Get enhanced system
        system = get_enhanced_system()

        # Get selected date
        selected_date = datetime.now().date()
        if request.method == "POST":
            date_str = request.POST.get("selected_date")
            if date_str:
                selected_date = datetime.strptime(date_str, "%Y-%m-%d").date()

        # Make enhanced prediction
        target_datetime = datetime.combine(selected_date, datetime.min.time())
        prediction_result = system.make_enhanced_prediction(
            target_date=target_datetime, include_validation=True, confidence_level=0.95
        )

        # Get actual result if available
        actual_result = None
        actual_numbers = []

        try:
            actual_result = KetQuaXoSo.objects.filter(ngay=selected_date).first()
            if actual_result:
                actual_numbers = actual_result.get_all_2digit_numbers()

                # Update system with actual result
                system.update_with_actual_result(
                    prediction_result=prediction_result,
                    actual_numbers=actual_numbers,
                    prediction_date=target_datetime,
                )
        except Exception as e:
            logging.warning(f"Could not get actual result: {e}")

        # Prepare context for template
        context = {
            "selected_date": selected_date,
            "enhanced_prediction": {
                "predicted_numbers": prediction_result.predicted_numbers,
                "overall_confidence": prediction_result.confidence_metrics.overall_confidence,
                "individual_confidences": prediction_result.confidence_metrics.individual_confidences,
                "expected_hits": prediction_result.expected_hits,
                "uncertainty_level": prediction_result.uncertainty_level,
                "recommendation": prediction_result.recommendation,
                "performance_score": prediction_result.performance_score,
                "risk_assessment": prediction_result.confidence_metrics.risk_assessment,
            },
            "statistical_validation": {
                "is_available": prediction_result.statistical_validation is not None,
                "is_significant": (
                    prediction_result.statistical_validation.is_significant
                    if prediction_result.statistical_validation
                    else False
                ),
                "p_value": (
                    prediction_result.statistical_validation.p_value
                    if prediction_result.statistical_validation
                    else None
                ),
                "interpretation": (
                    prediction_result.statistical_validation.interpretation
                    if prediction_result.statistical_validation
                    else None
                ),
            },
            "weight_optimization": prediction_result.weight_optimization,
            "actual_result": actual_result,
            "actual_numbers": actual_numbers,
            "system_health": system._assess_system_health(),
            "confidence_metrics": {
                "confidence_interval": prediction_result.confidence_metrics.confidence_metrics.confidence_interval,
                "prediction_interval": prediction_result.confidence_metrics.confidence_metrics.prediction_interval,
                "reliability_score": prediction_result.confidence_metrics.confidence_metrics.reliability_score,
            },
        }

        # Calculate hits if actual result available
        if actual_numbers:
            hits = set(prediction_result.predicted_numbers) & set(actual_numbers)
            hit_count = len(hits)
            accuracy = hit_count / len(prediction_result.predicted_numbers)

            context["prediction_accuracy"] = {
                "hits": sorted(hits),
                "hit_count": hit_count,
                "total_predicted": len(prediction_result.predicted_numbers),
                "accuracy": accuracy,
                "accuracy_percentage": accuracy * 100,
            }

        return render(request, "results/enhanced_predict.html", context)

    except Exception as e:
        logging.error(f"Enhanced predict view error: {e}")
        import traceback

        traceback.print_exc()

        # Fallback to basic prediction
        return render(
            request,
            "results/enhanced_predict.html",
            {
                "error": f"Enhanced prediction failed: {str(e)}",
                "selected_date": selected_date,
            },
        )


class EnhancedPredictionAPIView(View):
    """
    API endpoint for enhanced predictions
    """

    @method_decorator(csrf_exempt)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def post(self, request):
        """Handle enhanced prediction API requests"""

        try:
            data = json.loads(request.body)

            # Get parameters
            date_str = data.get("date", datetime.now().strftime("%Y-%m-%d"))
            include_validation = data.get("include_validation", True)
            confidence_level = data.get("confidence_level", 0.95)

            # Parse date
            target_date = datetime.strptime(date_str, "%Y-%m-%d")

            # Get enhanced system
            system = get_enhanced_system()

            # Make prediction
            prediction_result = system.make_enhanced_prediction(
                target_date=target_date,
                include_validation=include_validation,
                confidence_level=confidence_level,
            )

            # Format response
            response_data = {
                "success": True,
                "prediction": {
                    "date": date_str,
                    "predicted_numbers": prediction_result.predicted_numbers,
                    "confidence": {
                        "overall": prediction_result.confidence_metrics.overall_confidence,
                        "individual": prediction_result.confidence_metrics.individual_confidences,
                        "expected_hits": {
                            "lower": prediction_result.expected_hits[0],
                            "upper": prediction_result.expected_hits[1],
                        },
                        "uncertainty_level": prediction_result.uncertainty_level,
                        "reliability_score": prediction_result.confidence_metrics.confidence_metrics.reliability_score,
                    },
                    "recommendation": prediction_result.recommendation,
                    "performance_score": prediction_result.performance_score,
                    "risk_assessment": prediction_result.confidence_metrics.risk_assessment,
                },
                "system_info": {
                    "weights": prediction_result.weight_optimization,
                    "health": system._assess_system_health(),
                    "statistical_validation": {
                        "available": prediction_result.statistical_validation
                        is not None,
                        "significant": (
                            prediction_result.statistical_validation.is_significant
                            if prediction_result.statistical_validation
                            else False
                        ),
                    },
                },
            }

            return JsonResponse(response_data)

        except Exception as e:
            logging.error(f"Enhanced prediction API error: {e}")
            return JsonResponse({"success": False, "error": str(e)}, status=500)

    def get(self, request):
        """Get system status and monitoring data"""

        try:
            system = get_enhanced_system()

            # Get monitoring data
            monitoring_data = {}
            if system.performance_monitor:
                monitoring_data = system.performance_monitor.get_dashboard_data()

            # Get system health
            system_health = system._assess_system_health()

            # Get recent performance
            performance_summary = system.weight_optimizer.get_performance_summary()

            response_data = {
                "success": True,
                "system_status": {
                    "initialized": system.is_initialized,
                    "monitoring_active": system.performance_monitor is not None,
                    "prediction_count": len(system.prediction_history),
                    "adaptation_count": system.weight_optimizer.adaptation_count,
                },
                "health": system_health,
                "monitoring": monitoring_data,
                "performance": performance_summary,
            }

            return JsonResponse(response_data)

        except Exception as e:
            logging.error(f"System status API error: {e}")
            return JsonResponse({"success": False, "error": str(e)}, status=500)


class ValidationReportView(View):
    """
    View for comprehensive validation reports
    """

    def get(self, request):
        """Generate and display validation report"""

        try:
            system = get_enhanced_system()

            # Get report parameters
            days_back = int(request.GET.get("days", 30))

            # Run comprehensive validation
            validation_results = system.run_comprehensive_validation(
                days_back=days_back
            )

            context = {
                "validation_results": validation_results,
                "days_back": days_back,
                "report_timestamp": datetime.now(),
            }

            return render(request, "results/validation_report.html", context)

        except Exception as e:
            logging.error(f"Validation report error: {e}")
            return render(request, "results/validation_report.html", {"error": str(e)})


def performance_dashboard_view(request):
    """
    Performance monitoring dashboard
    """

    try:
        system = get_enhanced_system()

        if not system.performance_monitor:
            return render(
                request,
                "results/performance_dashboard.html",
                {"error": "Performance monitoring is not enabled"},
            )

        # Get dashboard data
        dashboard_data = system.performance_monitor.get_dashboard_data()

        # Get recent alerts
        recent_alerts = system.performance_monitor.get_recent_alerts(hours=24)

        # Get performance report
        performance_report = system.performance_monitor.get_performance_report(days=7)

        context = {
            "dashboard_data": dashboard_data,
            "recent_alerts": recent_alerts,
            "performance_report": performance_report,
            "system_health": system._assess_system_health(),
        }

        return render(request, "results/performance_dashboard.html", context)

    except Exception as e:
        logging.error(f"Performance dashboard error: {e}")
        return render(request, "results/performance_dashboard.html", {"error": str(e)})


# Template context processor for enhanced system data
def enhanced_system_context(request):
    """
    Context processor to add enhanced system data to all templates
    """

    try:
        system = get_enhanced_system()

        return {
            "enhanced_system_available": True,
            "system_health_score": system._assess_system_health()["score"],
            "monitoring_active": system.performance_monitor is not None,
            "prediction_count": len(system.prediction_history),
        }
    except:
        return {
            "enhanced_system_available": False,
            "system_health_score": 0,
            "monitoring_active": False,
            "prediction_count": 0,
        }


# Utility functions for templates
def format_confidence_level(uncertainty_level):
    """Format uncertainty level for display"""

    level_mapping = {
        "Low": {"class": "success", "icon": "✅"},
        "Moderate": {"class": "warning", "icon": "⚠️"},
        "High": {"class": "danger", "icon": "🔶"},
        "Very High": {"class": "danger", "icon": "❌"},
    }

    return level_mapping.get(uncertainty_level, {"class": "secondary", "icon": "❓"})


def format_performance_score(score):
    """Format performance score for display"""

    if score >= 80:
        return {"class": "success", "label": "Excellent", "icon": "🌟"}
    elif score >= 60:
        return {"class": "info", "label": "Good", "icon": "✅"}
    elif score >= 40:
        return {"class": "warning", "label": "Fair", "icon": "⚠️"}
    else:
        return {"class": "danger", "label": "Poor", "icon": "❌"}


# Custom template tags
from django import template

register = template.Library()


@register.filter
def confidence_class(uncertainty_level):
    """Template filter for confidence level CSS class"""
    return format_confidence_level(uncertainty_level)["class"]


@register.filter
def confidence_icon(uncertainty_level):
    """Template filter for confidence level icon"""
    return format_confidence_level(uncertainty_level)["icon"]


@register.filter
def performance_class(score):
    """Template filter for performance score CSS class"""
    return format_performance_score(score)["class"]


@register.filter
def performance_label(score):
    """Template filter for performance score label"""
    return format_performance_score(score)["label"]


@register.filter
def performance_icon(score):
    """Template filter for performance score icon"""
    return format_performance_score(score)["icon"]


@register.simple_tag
def system_health_badge(health_data):
    """Template tag for system health badge"""

    score = health_data.get("score", 0)
    status = health_data.get("status", "unknown")

    class_mapping = {
        "excellent": "success",
        "good": "info",
        "fair": "warning",
        "poor": "danger",
        "unknown": "secondary",
    }

    css_class = class_mapping.get(status, "secondary")

    return f'<span class="badge bg-{css_class}">{score}/100 ({status.title()})</span>'
