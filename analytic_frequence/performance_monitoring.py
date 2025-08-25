#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
📊 PERFORMANCE MONITORING DASHBOARD
Real-time monitoring and alerting for Ultimate Prediction System
"""

import logging
import time
from datetime import datetime, timedelta
from typing import Dict, List, Any

from django.core.cache import cache
from django.http import JsonResponse
from django.utils import timezone
from django.views.generic import View

from .service_manager import ServiceManager
from .intelligent_cache import IntelligentCache

logger = logging.getLogger(__name__)


class PerformanceMonitoringDashboard(View):
    """
    📊 REAL-TIME PERFORMANCE MONITORING
    
    Features:
    - Real-time performance metrics
    - Cache hit rate monitoring
    - Service health status
    - Alert system for performance degradation
    - Historical performance trends
    """

    def get(self, request):
        """Get comprehensive performance dashboard"""
        try:
            dashboard_data = self._collect_dashboard_data()
            return JsonResponse(dashboard_data)
            
        except Exception as e:
            logger.error(f"❌ Dashboard data collection failed: {e}")
            return JsonResponse({
                'error': 'Dashboard temporarily unavailable',
                'timestamp': timezone.now().isoformat()
            }, status=500)

    def _collect_dashboard_data(self) -> Dict[str, Any]:
        """Collect comprehensive dashboard data"""
        
        # System overview
        system_overview = self._get_system_overview()
        
        # Performance metrics
        performance_metrics = self._get_performance_metrics()
        
        # Cache analytics
        cache_analytics = IntelligentCache.get_performance_stats()
        
        # Service health
        service_health = ServiceManager.get_status()
        
        # Alerts and warnings
        alerts = self._check_performance_alerts()
        
        # Recent trends
        trends = self._get_performance_trends()
        
        return {
            'dashboard': {
                'system_overview': system_overview,
                'performance_metrics': performance_metrics,
                'cache_analytics': cache_analytics,
                'service_health': service_health,
                'alerts': alerts,
                'trends': trends,
                'last_updated': timezone.now().isoformat(),
                'dashboard_version': '2.0.0'
            }
        }

    def _get_system_overview(self) -> Dict[str, Any]:
        """Get high-level system overview"""
        try:
            # Calculate uptime
            service_status = ServiceManager.get_status()
            init_time = service_status.get('initialization_time', 0)
            uptime_hours = (time.time() - (time.time() - (init_time or 0))) / 3600 if init_time else 0
            
            # Get overall health score
            health_score = self._calculate_health_score()
            
            return {
                'status': 'operational' if health_score > 0.8 else 'degraded' if health_score > 0.5 else 'critical',
                'health_score': f"{health_score * 100:.1f}%",
                'uptime_hours': f"{uptime_hours:.1f}h",
                'services_healthy': ServiceManager.is_healthy(),
                'optimization_level': 'revolutionary_v2',
                'last_restart': service_status.get('initialization_time', 'unknown')
            }
            
        except Exception as e:
            logger.error(f"❌ System overview collection failed: {e}")
            return {'status': 'error', 'error': str(e)}

    def _get_performance_metrics(self) -> Dict[str, Any]:
        """Get detailed performance metrics"""
        try:
            # Get endpoint metrics
            endpoint_key = 'performance_metrics:/analytic_frequence/ultimate-prediction/'
            endpoint_metrics = cache.get(endpoint_key, {})
            
            # Calculate performance indicators
            avg_response_time = endpoint_metrics.get('avg_time', 0)
            total_requests = endpoint_metrics.get('total_requests', 0)
            slow_requests = endpoint_metrics.get('slow_requests', 0)
            critical_requests = endpoint_metrics.get('critical_requests', 0)
            
            # Calculate rates
            slow_rate = (slow_requests / total_requests * 100) if total_requests > 0 else 0
            critical_rate = (critical_requests / total_requests * 100) if total_requests > 0 else 0
            
            return {
                'avg_response_time': f"{avg_response_time:.2f}ms",
                'total_requests': total_requests,
                'slow_request_rate': f"{slow_rate:.2f}%",
                'critical_request_rate': f"{critical_rate:.2f}%",
                'performance_grade': self._calculate_performance_grade(avg_response_time),
                'target_compliance': {
                    'sub_200ms': avg_response_time < 200,
                    'sub_500ms': avg_response_time < 500,
                    'reliability': critical_rate < 1.0
                }
            }
            
        except Exception as e:
            logger.error(f"❌ Performance metrics collection failed: {e}")
            return {'error': str(e)}

    def _check_performance_alerts(self) -> List[Dict[str, Any]]:
        """Check for performance alerts and warnings"""
        alerts = []
        
        try:
            # Check service health
            if not ServiceManager.is_healthy():
                alerts.append({
                    'level': 'critical',
                    'message': 'One or more core services are unhealthy',
                    'timestamp': timezone.now().isoformat(),
                    'action': 'Investigate service status and consider restart'
                })
            
            # Check response time
            endpoint_metrics = cache.get('performance_metrics:/analytic_frequence/ultimate-prediction/', {})
            avg_time = endpoint_metrics.get('avg_time', 0)
            
            if avg_time > 500:
                alerts.append({
                    'level': 'critical',
                    'message': f'Average response time {avg_time:.2f}ms exceeds 500ms threshold',
                    'timestamp': timezone.now().isoformat(),
                    'action': 'Investigate performance bottlenecks'
                })
            elif avg_time > 200:
                alerts.append({
                    'level': 'warning',
                    'message': f'Average response time {avg_time:.2f}ms exceeds 200ms target',
                    'timestamp': timezone.now().isoformat(),
                    'action': 'Monitor and consider optimization'
                })
            
            # Check cache performance
            cache_stats = IntelligentCache.get_performance_stats()
            overall_hit_rate = cache_stats.get('overall_hit_rate', '0%')
            hit_rate_num = float(overall_hit_rate.replace('%', ''))
            
            if hit_rate_num < 50:
                alerts.append({
                    'level': 'warning',
                    'message': f'Cache hit rate {overall_hit_rate} below optimal threshold',
                    'timestamp': timezone.now().isoformat(),
                    'action': 'Review caching strategy and TTL settings'
                })
            
            # Check error rates
            critical_requests = endpoint_metrics.get('critical_requests', 0)
            total_requests = endpoint_metrics.get('total_requests', 1)
            error_rate = (critical_requests / total_requests * 100) if total_requests > 0 else 0
            
            if error_rate > 5:
                alerts.append({
                    'level': 'critical',
                    'message': f'High error rate: {error_rate:.2f}% of requests are critical',
                    'timestamp': timezone.now().isoformat(),
                    'action': 'Immediate investigation required'
                })
            
        except Exception as e:
            logger.error(f"❌ Alert checking failed: {e}")
            alerts.append({
                'level': 'error',
                'message': f'Alert system error: {e}',
                'timestamp': timezone.now().isoformat()
            })
        
        return alerts

    def _get_performance_trends(self) -> Dict[str, Any]:
        """Get performance trends over time"""
        try:
            # For now, return current snapshot
            # In production, this would query historical data
            
            current_time = timezone.now()
            
            return {
                'response_time_trend': 'improving',  # Mock data
                'cache_hit_rate_trend': 'stable',
                'request_volume_trend': 'increasing',
                'error_rate_trend': 'stable',
                'trend_period': '24h',
                'trend_analysis': {
                    'overall': 'positive',
                    'recommendations': [
                        'Continue current optimization strategy',
                        'Monitor cache hit rates',
                        'Prepare for increased load'
                    ]
                }
            }
            
        except Exception as e:
            logger.error(f"❌ Trend analysis failed: {e}")
            return {'error': str(e)}

    def _calculate_health_score(self) -> float:
        """Calculate overall system health score (0-1)"""
        try:
            score_components = []
            
            # Service health (30%)
            service_health = 1.0 if ServiceManager.is_healthy() else 0.0
            score_components.append(('service_health', service_health, 0.3))
            
            # Response time performance (40%)
            endpoint_metrics = cache.get('performance_metrics:/analytic_frequence/ultimate-prediction/', {})
            avg_time = endpoint_metrics.get('avg_time', 1000)  # Default to poor if no data
            
            if avg_time < 100:
                response_score = 1.0
            elif avg_time < 200:
                response_score = 0.8
            elif avg_time < 500:
                response_score = 0.5
            else:
                response_score = 0.2
            
            score_components.append(('response_time', response_score, 0.4))
            
            # Cache performance (20%)
            cache_stats = IntelligentCache.get_performance_stats()
            hit_rate = cache_stats.get('overall_hit_rate', '0%')
            hit_rate_num = float(hit_rate.replace('%', ''))
            cache_score = min(hit_rate_num / 100, 1.0)
            
            score_components.append(('cache_performance', cache_score, 0.2))
            
            # Error rate (10%)
            critical_requests = endpoint_metrics.get('critical_requests', 0)
            total_requests = endpoint_metrics.get('total_requests', 1)
            error_rate = (critical_requests / total_requests * 100) if total_requests > 0 else 0
            error_score = max(0, 1.0 - (error_rate / 10))  # 10% error rate = 0 score
            
            score_components.append(('error_rate', error_score, 0.1))
            
            # Calculate weighted average
            total_score = sum(score * weight for _, score, weight in score_components)
            
            return max(0.0, min(1.0, total_score))
            
        except Exception as e:
            logger.error(f"❌ Health score calculation failed: {e}")
            return 0.5  # Default to medium health

    def _calculate_performance_grade(self, avg_response_time: float) -> str:
        """Calculate performance grade based on response time"""
        if avg_response_time < 50:
            return 'A+'
        elif avg_response_time < 100:
            return 'A'
        elif avg_response_time < 200:
            return 'B+'
        elif avg_response_time < 300:
            return 'B'
        elif avg_response_time < 500:
            return 'C'
        else:
            return 'D'


class PerformanceAlertSystem:
    """
    🚨 PERFORMANCE ALERT SYSTEM
    Real-time alerting for performance issues
    """
    
    @staticmethod
    def check_and_alert():
        """Check performance and send alerts if needed"""
        try:
            dashboard = PerformanceMonitoringDashboard()
            dashboard_data = dashboard._collect_dashboard_data()
            
            alerts = dashboard_data['dashboard']['alerts']
            critical_alerts = [a for a in alerts if a['level'] == 'critical']
            
            if critical_alerts:
                logger.critical(f"🚨 {len(critical_alerts)} critical performance alerts detected!")
                for alert in critical_alerts:
                    logger.critical(f"ALERT: {alert['message']}")
                
                # In production, send to monitoring system (Slack, email, etc.)
                PerformanceAlertSystem._send_alerts(critical_alerts)
                
        except Exception as e:
            logger.error(f"❌ Alert system check failed: {e}")
    
    @staticmethod
    def _send_alerts(alerts: List[Dict]):
        """Send alerts to monitoring systems"""
        # Implementation for actual alert sending
        # (Slack, email, PagerDuty, etc.)
        logger.info(f"📧 Would send {len(alerts)} alerts to monitoring systems")


# Health check endpoint
class HealthCheckView(View):
    """Simple health check endpoint"""
    
    def get(self, request):
        """Return system health status"""
        try:
            health_data = {
                'status': 'healthy' if ServiceManager.is_healthy() else 'unhealthy',
                'timestamp': timezone.now().isoformat(),
                'services': ServiceManager.get_status(),
                'cache': 'operational',
                'version': '2.0.0'
            }
            
            status_code = 200 if ServiceManager.is_healthy() else 503
            return JsonResponse(health_data, status=status_code)
            
        except Exception as e:
            return JsonResponse({
                'status': 'error',
                'error': str(e),
                'timestamp': timezone.now().isoformat()
            }, status=500)


# Global performance monitor instance
performance_monitor = PerformanceMonitoringDashboard()
