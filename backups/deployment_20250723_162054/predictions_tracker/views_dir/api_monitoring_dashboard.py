import logging
from datetime import datetime, timedelta
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.utils import timezone

from predictions_tracker.core.services.MonitoringService import monitoring_service

logger = logging.getLogger(__name__)


@csrf_exempt
@require_http_methods(["GET"])
def api_monitoring_dashboard(request):
    """
    Get comprehensive monitoring dashboard data
    
    Returns:
        Dict[str, Any]: {
            "success": bool,
            "dashboard_data": {
                "current_metrics": dict,
                "recent_alerts": list,
                "performance_trends": dict,
                "method_performance": dict,
                "ab_test_status": dict,
                "optimization_status": dict
            },
            "metadata": dict
        }
    """
    try:
        logger.info("📊 Fetching monitoring dashboard data")
        
        # Get comprehensive dashboard data
        dashboard_data = monitoring_service.get_dashboard_data()
        
        response_data = {
            "success": True,
            "dashboard_data": {
                "current_metrics": {
                    "timestamp": dashboard_data.current_metrics.timestamp,
                    "api_response_time_ms": dashboard_data.current_metrics.api_response_time_ms,
                    "prediction_accuracy": dashboard_data.current_metrics.prediction_accuracy,
                    "active_methods_count": dashboard_data.current_metrics.active_methods_count,
                    "failed_predictions_count": dashboard_data.current_metrics.failed_predictions_count,
                    "memory_usage_mb": dashboard_data.current_metrics.memory_usage_mb,
                    "database_connection_status": dashboard_data.current_metrics.database_connection_status,
                    "cache_hit_rate": dashboard_data.current_metrics.cache_hit_rate
                },
                "recent_alerts": [
                    {
                        "alert_id": alert.alert_id,
                        "severity": alert.severity,
                        "alert_type": alert.alert_type,
                        "message": alert.message,
                        "details": alert.details,
                        "timestamp": alert.timestamp,
                        "resolved": alert.resolved
                    }
                    for alert in dashboard_data.recent_alerts
                ],
                "performance_trends": dashboard_data.performance_trends,
                "method_performance": dashboard_data.method_performance,
                "ab_test_status": dashboard_data.ab_test_status,
                "optimization_status": dashboard_data.optimization_status
            },
            "metadata": {
                "retrieved_at": timezone.now().isoformat(),
                "api_version": "v4_monitoring",
                "data_freshness": "real_time"
            }
        }
        
        return JsonResponse(response_data, json_dumps_params={'ensure_ascii': False})
        
    except Exception as e:
        logger.error(f"❌ Monitoring dashboard API error: {str(e)}", exc_info=True)
        return JsonResponse({
            "success": False,
            "error": "internal_server_error",
            "message": f"Failed to fetch dashboard data: {str(e)}"
        }, status=500)


@csrf_exempt
@require_http_methods(["GET"])
def api_system_health(request):
    """
    Get quick system health check
    
    Returns:
        Dict[str, Any]: {
            "success": bool,
            "health_status": str,
            "current_metrics": dict,
            "alerts_count": int,
            "metadata": dict
        }
    """
    try:
        # Collect current system metrics
        current_metrics = monitoring_service.collect_system_metrics()
        
        # Get recent alerts count
        recent_alerts = monitoring_service._get_recent_alerts(hours=1)
        high_priority_alerts = [
            alert for alert in recent_alerts 
            if alert.severity in ['high', 'critical']
        ]
        
        # Determine overall health status
        if high_priority_alerts:
            health_status = "critical"
        elif len(recent_alerts) > 0:
            health_status = "warning"
        elif current_metrics.prediction_accuracy < 0.1:
            health_status = "degraded"
        elif not current_metrics.database_connection_status:
            health_status = "critical"
        else:
            health_status = "healthy"
        
        response_data = {
            "success": True,
            "health_status": health_status,
            "current_metrics": {
                "timestamp": current_metrics.timestamp,
                "api_response_time_ms": current_metrics.api_response_time_ms,
                "prediction_accuracy": current_metrics.prediction_accuracy,
                "active_methods_count": current_metrics.active_methods_count,
                "database_connection_status": current_metrics.database_connection_status,
                "memory_usage_mb": current_metrics.memory_usage_mb
            },
            "alerts_summary": {
                "total_alerts": len(recent_alerts),
                "high_priority_alerts": len(high_priority_alerts),
                "alert_types": list(set(alert.alert_type for alert in recent_alerts))
            },
            "metadata": {
                "checked_at": timezone.now().isoformat(),
                "api_version": "v4_monitoring"
            }
        }
        
        return JsonResponse(response_data, json_dumps_params={'ensure_ascii': False})
        
    except Exception as e:
        logger.error(f"❌ System health API error: {str(e)}", exc_info=True)
        return JsonResponse({
            "success": False,
            "error": "internal_server_error",
            "message": f"Health check failed: {str(e)}",
            "health_status": "unknown"
        }, status=500)


@csrf_exempt
@require_http_methods(["POST"])
def api_resolve_alert(request):
    """
    Resolve a monitoring alert
    
    POST params:
        - alert_id: str
        
    Returns:
        Dict[str, Any]: {
            "success": bool,
            "message": str,
            "alert_id": str
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
        result = monitoring_service.resolve_alert(alert_id)
        
        return JsonResponse({
            "success": result["success"],
            "message": result["message"],
            "alert_id": alert_id,
            "resolved_at": timezone.now().isoformat()
        }, json_dumps_params={'ensure_ascii': False})
        
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
    
    GET params:
        - period: str ('1h', '6h', '24h', '7d') - default: '24h'
        - metric_type: str ('all', 'accuracy', 'response_time', 'memory') - default: 'all'
        
    Returns:
        Dict[str, Any]: {
            "success": bool,
            "metrics": dict,
            "trends": dict,
            "metadata": dict
        }
    """
    try:
        period = request.GET.get('period', '24h')
        metric_type = request.GET.get('metric_type', 'all')
        
        # Validate period
        period_mapping = {
            '1h': 1,
            '6h': 6, 
            '24h': 24,
            '7d': 24 * 7
        }
        
        if period not in period_mapping:
            return JsonResponse({
                "success": False,
                "error": "invalid_period",
                "message": "Period must be one of: 1h, 6h, 24h, 7d"
            }, status=400)
        
        hours = period_mapping[period]
        
        # Get performance trends
        dashboard_data = monitoring_service.get_dashboard_data()
        trends = dashboard_data.performance_trends
        
        # Filter by metric type if specified
        if metric_type != 'all':
            if metric_type in trends:
                filtered_trends = {metric_type: trends[metric_type]}
            else:
                filtered_trends = {}
        else:
            filtered_trends = trends
        
        # Calculate summary statistics
        metrics_summary = {}
        for metric_name, values in filtered_trends.items():
            if values:
                metrics_summary[metric_name] = {
                    "current": values[-1] if values else 0,
                    "average": sum(values) / len(values),
                    "min": min(values),
                    "max": max(values),
                    "trend": "increasing" if len(values) > 1 and values[-1] > values[0] else "decreasing" if len(values) > 1 else "stable"
                }
        
        response_data = {
            "success": True,
            "metrics": metrics_summary,
            "trends": filtered_trends,
            "metadata": {
                "period": period,
                "metric_type": metric_type,
                "data_points": len(list(filtered_trends.values())[0]) if filtered_trends else 0,
                "retrieved_at": timezone.now().isoformat()
            }
        }
        
        return JsonResponse(response_data, json_dumps_params={'ensure_ascii': False})
        
    except Exception as e:
        logger.error(f"❌ Performance metrics API error: {str(e)}", exc_info=True)
        return JsonResponse({
            "success": False,
            "error": "internal_server_error",
            "message": f"Failed to fetch performance metrics: {str(e)}"
        }, status=500)