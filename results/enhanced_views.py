"""
Django Views for Enhanced Prediction System
Production-ready views with real data integration
"""

import json
import logging
from datetime import datetime, timedelta
from typing import Dict

from django.conf import settings
from django.core.cache import cache
from django.http import JsonResponse
from django.shortcuts import render
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.cache import cache_page
from django.views.decorators.csrf import csrf_exempt

from .django_enhanced_system import DjangoEnhancedPredictionSystem, ProductionConfig

logger = logging.getLogger(__name__)

# Global system instance
_system_instance = None


def get_enhanced_system():
    """Get or create enhanced system instance"""
    global _system_instance

    if _system_instance is None:
        try:
            config = ProductionConfig()
            _system_instance = DjangoEnhancedPredictionSystem(config)
            _system_instance.initialize_with_real_data()
            logger.info("Enhanced system initialized")
        except Exception as e:
            logger.error(f"Failed to initialize enhanced system: {e}")
            raise

    return _system_instance


class EnhancedPredictionView(View):
    """Enhanced prediction view with production integration"""

    def get(self, request):
        """GET request - render prediction page"""

        try:
            # Get system dashboard data
            system = get_enhanced_system()
            dashboard_data = system.get_production_dashboard_data()

            context = {
                "dashboard_data": dashboard_data,
                "system_status": dashboard_data.get("system_health", {}).get(
                    "status", "unknown"
                ),
                "last_update": datetime.now().isoformat(),
            }

            return render(request, "results/predict/enhanced_prediction.html", context)

        except Exception as e:
            logger.error(f"Enhanced prediction view error: {e}")
            return render(
                request,
                "results/predict/enhanced_prediction.html",
                {"error": str(e), "system_status": "error"},
            )

    def post(self, request):
        """POST request - make prediction"""

        try:
            data = json.loads(request.body)
            target_date_str = data.get("target_date")

            if not target_date_str:
                target_date = datetime.now() + timedelta(days=1)
            else:
                target_date = datetime.fromisoformat(target_date_str)

            # Make prediction
            system = get_enhanced_system()
            result = system.make_production_prediction(target_date)

            return JsonResponse(result)

        except Exception as e:
            logger.error(f"Enhanced prediction POST error: {e}")
            return JsonResponse(
                {
                    "success": False,
                    "error": str(e),
                    "fallback_prediction": list(range(10, 25)),
                }
            )


@method_decorator(cache_page(60 * 5), name="dispatch")  # Cache for 5 minutes
class EnhancedPredictionAPIView(View):
    """API view for enhanced predictions"""

    @method_decorator(csrf_exempt)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def get(self, request):
        """Get prediction for specified date"""

        try:
            # Get parameters
            target_date_str = request.GET.get("date")
            if target_date_str:
                target_date = datetime.fromisoformat(target_date_str)
            else:
                target_date = datetime.now() + timedelta(days=1)

            # Check cache first
            cache_key = f"enhanced_prediction_{target_date.date()}"
            cached_result = cache.get(cache_key)

            if cached_result:
                cached_result["from_cache"] = True
                return JsonResponse(cached_result)

            # Make fresh prediction
            system = get_enhanced_system()
            result = system.make_production_prediction(target_date)

            # Cache result for 30 minutes
            if result.get("success"):
                cache.set(cache_key, result, 60 * 30)

            return JsonResponse(result)

        except Exception as e:
            logger.error(f"Enhanced API error: {e}")
            return JsonResponse(
                {
                    "success": False,
                    "error": str(e),
                    "timestamp": datetime.now().isoformat(),
                }
            )

    def post(self, request):
        """Update prediction with actual result"""

        try:
            data = json.loads(request.body)

            prediction_date_str = data.get("prediction_date")
            performance_record_id = data.get("performance_record_id")

            if not prediction_date_str:
                return JsonResponse(
                    {"success": False, "error": "prediction_date required"}
                )

            prediction_date = datetime.fromisoformat(prediction_date_str)

            # Update with actual result
            system = get_enhanced_system()
            success = system.update_with_real_result(
                prediction_date=prediction_date,
                performance_record_id=performance_record_id,
            )

            return JsonResponse(
                {"success": success, "updated_at": datetime.now().isoformat()}
            )

        except Exception as e:
            logger.error(f"Enhanced API update error: {e}")
            return JsonResponse({"success": False, "error": str(e)})


class MonitoringDashboardView(View):
    """Monitoring dashboard for production system"""

    def get(self, request):
        """Render monitoring dashboard"""

        try:
            system = get_enhanced_system()
            dashboard_data = system.get_production_dashboard_data()

            # Add additional monitoring info
            dashboard_data["server_time"] = datetime.now().isoformat()
            dashboard_data["cache_status"] = self._get_cache_status()

            if request.GET.get("format") == "json":
                return JsonResponse(dashboard_data)

            return render(
                request,
                "results/predict/monitoring_dashboard.html",
                {"dashboard_data": dashboard_data},
            )

        except Exception as e:
            logger.error(f"Monitoring dashboard error: {e}")

            error_data = {
                "error": str(e),
                "system_available": False,
                "server_time": datetime.now().isoformat(),
            }

            if request.GET.get("format") == "json":
                return JsonResponse(error_data)

            return render(
                request,
                "results/predict/monitoring_dashboard.html",
                {"dashboard_data": error_data},
            )

    def _get_cache_status(self):
        """Get cache status information"""

        try:
            # Test cache
            test_key = "cache_test_key"
            cache.set(test_key, "test_value", 10)
            test_result = cache.get(test_key)

            return {
                "available": test_result == "test_value",
                "backend": getattr(settings, "CACHES", {})
                .get("default", {})
                .get("BACKEND", "unknown"),
            }
        except Exception:
            return {"available": False, "backend": "unknown"}


class SystemHealthView(View):
    """System health check endpoint"""

    def get(self, request):
        """Get system health status"""

        try:
            system = get_enhanced_system()
            health_data = system._assess_system_health()

            # Add system-level checks
            health_data.update(
                {
                    "django_available": True,
                    "cache_available": self._check_cache(),
                    "database_available": self._check_database(),
                    "timestamp": datetime.now().isoformat(),
                }
            )

            # Determine HTTP status code
            status_code = 200
            if health_data["score"] < 60:
                status_code = 503  # Service Unavailable
            elif health_data["score"] < 80:
                status_code = 200  # OK but with warnings

            return JsonResponse(health_data, status=status_code)

        except Exception as e:
            logger.error(f"System health check error: {e}")
            return JsonResponse(
                {
                    "status": "error",
                    "score": 0,
                    "error": str(e),
                    "timestamp": datetime.now().isoformat(),
                },
                status=503,
            )

    def _check_cache(self) -> bool:
        """Check if cache is available"""
        try:
            cache.set("health_check", "ok", 10)
            return cache.get("health_check") == "ok"
        except Exception:
            return False

    def _check_database(self) -> bool:
        """Check if database is available"""
        try:
            from results.models import KetQuaXoSo

            KetQuaXoSo.objects.count()
            return True
        except Exception:
            return False


# Context processor for template integration
def enhanced_system_context(request):
    """Add enhanced system data to template context"""

    try:
        system = get_enhanced_system()

        # Get basic system info
        context = {
            "enhanced_system_available": True,
            "system_health": system._assess_system_health(),
            "current_time": datetime.now().isoformat(),
        }

        # Add dashboard data for specific pages
        if hasattr(request, "resolver_match") and request.resolver_match:
            view_name = request.resolver_match.view_name
            if view_name in ["enhanced_prediction", "monitoring_dashboard"]:
                context["dashboard_data"] = system.get_production_dashboard_data()

        return context

    except Exception as e:
        logger.warning(f"Enhanced system context processor error: {e}")
        return {"enhanced_system_available": False, "system_error": str(e)}


# Management command helper
def reset_enhanced_system():
    """Reset enhanced system (for management commands)"""
    global _system_instance

    if _system_instance:
        _system_instance.cleanup()
        _system_instance = None

    logger.info("Enhanced system reset")
