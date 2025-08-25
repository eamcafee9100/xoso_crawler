import logging
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.utils import timezone

from predictions_tracker.core.services.ProductionMonitoringService import production_monitoring_service

logger = logging.getLogger(__name__)


@csrf_exempt
@require_http_methods(["GET"])
def api_production_dashboard(request):
    """
    Production monitoring dashboard API
    
    Returns:
        dict: {
            "success": bool,
            "dashboard_data": {
                "current_metrics": dict,
                "performance_trends": dict,
                "recent_alerts": list,
                "method_performance": dict,
                "ab_test_status": dict,
                "optimization_status": dict
            },
            "metadata": dict
        }
    """
    try:
        logger.info("🔍 Production dashboard data requested")
        
        # Get dashboard data
        dashboard_result = production_monitoring_service.get_dashboard_data()
        
        if dashboard_result["success"]:
            response_data = {
                "success": True,
                "dashboard_data": dashboard_result["dashboard_data"],
                "metadata": {
                    "generated_at": timezone.now().isoformat(),
                    "api_version": "v3_production",
                    "data_freshness": "real_time"
                }
            }
        else:
            response_data = {
                "success": False,
                "error": dashboard_result.get("error", "unknown_error"),
                "message": "Failed to collect dashboard data",
                "dashboard_data": dashboard_result.get("dashboard_data", {})
            }
        
        return JsonResponse(response_data, json_dumps_params={'ensure_ascii': False})
        
    except Exception as e:
        logger.error(f"❌ Production dashboard API error: {str(e)}", exc_info=True)
        return JsonResponse({
            "success": False,
            "error": "internal_server_error",
            "message": f"Dashboard API failed: {str(e)}",
            "dashboard_data": {}
        }, status=500)


@csrf_exempt
@require_http_methods(["GET"])
def api_system_health_check(request):
    """
    System health check API
    
    Returns:
        dict: {
            "success": bool,
            "health_summary": dict,
            "status_code": str
        }
    """
    try:
        # Get system health summary
        health_summary = production_monitoring_service.get_system_health_summary()
        
        # Determine HTTP status based on health
        overall_status = health_summary.get("overall_status", "unknown")
        
        if overall_status == "critical":
            status_code = 503  # Service Unavailable
        elif overall_status in ["degraded", "warning"]:
            status_code = 200  # OK but with warnings
        else:
            status_code = 200  # OK
        
        response_data = {
            "success": True,
            "health_summary": health_summary,
            "status_code": overall_status,
            "timestamp": timezone.now().isoformat()
        }
        
        return JsonResponse(response_data, status=status_code, json_dumps_params={'ensure_ascii': False})
        
    except Exception as e:
        logger.error(f"❌ Health check API error: {str(e)}", exc_info=True)
        return JsonResponse({
            "success": False,
            "error": "health_check_failed",
            "message": f"Health check failed: {str(e)}",
            "status_code": "error"
        }, status=500)


@csrf_exempt
@require_http_methods(["POST"])
def api_resolve_production_alert(request):
    """
    Resolve production alert
    
    POST params:
        - alert_id: str (required)
        
    Returns:
        dict: {
            "success": bool,
            "message": str
        }
    """
    try:
        alert_id = request.POST.get('alert_id')
        
        if not alert_id:
            return JsonResponse({
                "success": False,
                "error": "missing_alert_id",
                "message": "alert_id parameter is required"
            }, status=400)
        
        # Resolve alert
        result = production_monitoring_service.resolve_alert(alert_id)
        
        if result["success"]:
            logger.info(f"✅ Production alert resolved: {alert_id}")
        else:
            logger.warning(f"❌ Failed to resolve alert: {alert_id}")
        
        return JsonResponse(result, json_dumps_params={'ensure_ascii': False})
        
    except Exception as e:
        logger.error(f"❌ Resolve alert API error: {str(e)}", exc_info=True)
        return JsonResponse({
            "success": False,
            "error": "internal_server_error",
            "message": f"Failed to resolve alert: {str(e)}"
        }, status=500)


@csrf_exempt
@require_http_methods(["GET"])
def api_performance_metrics(request):
    """
    Get detailed performance metrics
    
    Returns:
        dict: {
            "success": bool,
            "performance_metrics": dict,
            "trends": dict
        }
    """
    try:
        # Collect current metrics
        current_metrics = production_monitoring_service._collect_current_metrics()
        
        # Get performance trends
        performance_trends = production_monitoring_service._get_performance_trends()
        
        response_data = {
            "success": True,
            "performance_metrics": current_metrics,
            "trends": performance_trends,
            "metadata": {
                "collection_timestamp": timezone.now().isoformat(),
                "metrics_count": len(current_metrics),
                "trend_data_points": {
                    key: len(values) for key, values in performance_trends.items()
                }
            }
        }
        
        return JsonResponse(response_data, json_dumps_params={'ensure_ascii': False})
        
    except Exception as e:
        logger.error(f"❌ Performance metrics API error: {str(e)}", exc_info=True)
        return JsonResponse({
            "success": False,
            "error": "metrics_collection_failed",
            "message": f"Failed to collect metrics: {str(e)}"
        }, status=500)