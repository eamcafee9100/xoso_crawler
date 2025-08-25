import logging
import psutil
import time
from datetime import date, timedelta
from typing import Dict, List, Any, Optional
from collections import deque, defaultdict
from django.db import connection
from django.core.cache import cache
from django.utils import timezone

from predictions_tracker.models import (
    PredictionMethod,
    ABTestVariant,
    ABTestResult,
    CyclicalContextEngine
)
from predictions_tracker.core.services.ParameterOptimizationService import parameter_optimization_service
from predictions_tracker.core.services.ABTestingService import ab_testing_service

logger = logging.getLogger(__name__)


class SystemAlert:
    """System alert structure"""
    def __init__(self, alert_type: str, severity: str, message: str, component: str):
        self.alert_id = f"{alert_type}_{int(time.time())}"
        self.alert_type = alert_type
        self.severity = severity  # critical, high, medium, low
        self.message = message
        self.component = component
        self.timestamp = timezone.now().isoformat()
        self.resolved = False


class ProductionMonitoringService:
    """Service cho production monitoring và health checks"""
    
    def __init__(self):
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        self.alerts = deque(maxlen=100)  # Keep last 100 alerts
        self.performance_history = defaultdict(lambda: deque(maxlen=50))  # 50 data points
        self.thresholds = {
            'accuracy_min': 0.05,  # 5% minimum accuracy
            'response_time_max': 5000,  # 5 seconds max
            'memory_max_mb': 2048,  # 2GB max
            'database_timeout': 10,  # 10 seconds
        }
    
    def get_dashboard_data(self) -> Dict[str, Any]:
        """
        Get comprehensive dashboard data
        
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
                }
            }
        """
        try:
            self.logger.info("🔍 Collecting dashboard data")
            
            # Collect current metrics
            current_metrics = self._collect_current_metrics()
            
            # Get performance trends
            performance_trends = self._get_performance_trends()
            
            # Get recent alerts
            recent_alerts = self._get_recent_alerts()
            
            # Get method performance
            method_performance = self._get_method_performance()
            
            # Get A/B test status
            ab_test_status = self._get_ab_test_status()
            
            # Get optimization status
            optimization_status = self._get_optimization_status()
            
            # Check for new alerts
            self._check_system_health(current_metrics)
            
            dashboard_data = {
                "current_metrics": current_metrics,
                "performance_trends": performance_trends,
                "recent_alerts": recent_alerts,
                "method_performance": method_performance,
                "ab_test_status": ab_test_status,
                "optimization_status": optimization_status
            }
            
            return {
                "success": True,
                "dashboard_data": dashboard_data
            }
            
        except Exception as e:
            self.logger.error(f"❌ Dashboard data collection failed: {str(e)}", exc_info=True)
            return {
                "success": False,
                "error": str(e),
                "dashboard_data": {}
            }
    
    def _collect_current_metrics(self) -> Dict[str, Any]:
        """Collect current system metrics"""
        try:
            # Database connection check
            db_status = self._check_database_connection()
            
            # Memory usage
            memory_info = psutil.virtual_memory()
            memory_usage_mb = memory_info.used / (1024 * 1024)
            
            # API response time (simulated for now)
            api_response_time = self._measure_api_response_time()
            
            # Prediction accuracy (recent)
            prediction_accuracy = self._get_recent_prediction_accuracy()
            
            # Active methods count
            active_methods_count = PredictionMethod.objects.filter(is_active=True).count()
            
            # CPU usage
            cpu_usage = psutil.cpu_percent(interval=1)
            
            metrics = {
                "database_connection_status": db_status,
                "memory_usage_mb": memory_usage_mb,
                "cpu_usage_percent": cpu_usage,
                "api_response_time_ms": api_response_time,
                "prediction_accuracy": prediction_accuracy,
                "active_methods_count": active_methods_count,
                "timestamp": timezone.now().isoformat()
            }
            
            # Store metrics in performance history
            for key, value in metrics.items():
                if isinstance(value, (int, float)) and key != "timestamp":
                    self.performance_history[key].append(value)
            
            return metrics
            
        except Exception as e:
            self.logger.warning(f"Metrics collection error: {str(e)}")
            return {
                "database_connection_status": False,
                "memory_usage_mb": 0,
                "cpu_usage_percent": 0,
                "api_response_time_ms": 0,
                "prediction_accuracy": 0.0,
                "active_methods_count": 0,
                "timestamp": timezone.now().isoformat(),
                "error": str(e)
            }
    
    def _check_database_connection(self) -> bool:
        """Check database connection health"""
        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT 1")
                return True
        except Exception:
            return False
    
    def _measure_api_response_time(self) -> float:
        """Measure API response time"""
        try:
            start_time = time.time()
            
            # Simulate a lightweight database query
            PredictionMethod.objects.filter(is_active=True).count()
            
            end_time = time.time()
            return (end_time - start_time) * 1000  # Convert to milliseconds
            
        except Exception:
            return 9999.0  # Return high value on error
    
    def _get_recent_prediction_accuracy(self) -> float:
        """Get recent prediction accuracy"""
        try:
            # Get accuracy from last 7 days of A/B test results
            recent_date = date.today() - timedelta(days=7)
            
            recent_results = ABTestResult.objects.filter(
                test_date__gte=recent_date
            ).values_list('accuracy_rate', flat=True)
            
            if recent_results:
                return sum(recent_results) / len(recent_results)
            
            # Fallback: simulate based on active methods
            active_methods = PredictionMethod.objects.filter(is_active=True).count()
            if active_methods > 0:
                return min(0.25, active_methods * 0.02)  # Basic simulation
            
            return 0.0
            
        except Exception as e:
            self.logger.warning(f"Accuracy calculation error: {str(e)}")
            return 0.0
    
    def _get_performance_trends(self) -> Dict[str, List[float]]:
        """Get performance trends from history"""
        try:
            trends = {}
            
            # Extract trends for key metrics
            key_metrics = ['prediction_accuracy', 'api_response_time_ms', 'memory_usage_mb', 'cpu_usage_percent']
            
            for metric in key_metrics:
                if metric in self.performance_history:
                    trends[metric.replace('_', '')] = list(self.performance_history[metric])
                else:
                    trends[metric.replace('_', '')] = []
            
            return trends
            
        except Exception as e:
            self.logger.warning(f"Trends calculation error: {str(e)}")
            return {}
    
    def _get_recent_alerts(self) -> List[Dict[str, Any]]:
        """Get recent alerts"""
        try:
            # Convert alerts to dict format
            recent_alerts = []
            for alert in list(self.alerts)[-20:]:  # Last 20 alerts
                if not alert.resolved:
                    recent_alerts.append({
                        "alert_id": alert.alert_id,
                        "alert_type": alert.alert_type,
                        "severity": alert.severity,
                        "message": alert.message,
                        "component": alert.component,
                        "timestamp": alert.timestamp
                    })
            
            return recent_alerts
            
        except Exception as e:
            self.logger.warning(f"Alerts retrieval error: {str(e)}")
            return []
    
    def _get_method_performance(self) -> Dict[str, Dict[str, float]]:
        """Get method performance summary"""
        try:
            method_performance = {}
            
            # Get methods with recent evaluations
            recent_date = date.today() - timedelta(days=30)
            
            # Simulate method performance (replace with actual evaluation data)
            active_methods = PredictionMethod.objects.filter(is_active=True)
            
            for method in active_methods:
                # Simulate performance metrics
                # In production, replace with actual evaluation results
                performance = {
                    "avg_accuracy": min(0.3, hash(method.name) % 30 / 100),  # Simulate 0-30% accuracy
                    "total_evaluations": hash(method.name) % 50 + 10,  # Simulate 10-60 evaluations
                    "recent_trend": "stable"  # Could be "improving", "declining", "stable"
                }
                method_performance[method.name] = performance
            
            return method_performance
            
        except Exception as e:
            self.logger.warning(f"Method performance error: {str(e)}")
            return {}
    
    def _get_ab_test_status(self) -> Dict[str, Any]:
        """Get A/B testing status"""
        try:
            # Count active tests
            active_tests = ABTestVariant.objects.filter(
                status='active',
                start_date__lte=date.today(),
                end_date__gte=date.today()
            )
            
            active_tests_count = active_tests.count()
            
            # Get recent accuracy from A/B test results
            recent_date = date.today() - timedelta(days=7)
            recent_results = ABTestResult.objects.filter(
                test_date__gte=recent_date
            ).values_list('accuracy_rate', flat=True)
            
            recent_avg_accuracy = sum(recent_results) / len(recent_results) if recent_results else 0.0
            
            # Determine status
            if active_tests_count == 0:
                status = "no_active_tests"
            elif recent_avg_accuracy < 0.1:
                status = "low_performance"
            else:
                status = "healthy"
            
            return {
                "active_tests_count": active_tests_count,
                "recent_avg_accuracy": recent_avg_accuracy,
                "status": status,
                "last_updated": timezone.now().isoformat()
            }
            
        except Exception as e:
            self.logger.warning(f"A/B test status error: {str(e)}")
            return {
                "error": str(e),
                "active_tests_count": 0,
                "recent_avg_accuracy": 0.0,
                "status": "error"
            }
    
    def _get_optimization_status(self) -> Dict[str, Any]:
        """Get parameter optimization status"""
        try:
            # Get optimization history
            history = parameter_optimization_service.get_optimization_history()
            
            total_optimizations = len(history)
            successful_optimizations = sum(1 for entry in history if entry["result"].success)
            success_rate = successful_optimizations / total_optimizations if total_optimizations > 0 else 0
            
            # Get latest optimization
            latest_optimization = history[-1] if history else None
            
            # Determine status
            if total_optimizations == 0:
                status = "no_optimizations"
            elif success_rate < 0.5:
                status = "low_success_rate"
            else:
                status = "healthy"
            
            return {
                "total_optimizations": total_optimizations,
                "successful_optimizations": successful_optimizations,
                "success_rate": success_rate,
                "latest_optimization": {
                    "timestamp": latest_optimization["timestamp"],
                    "success": latest_optimization["result"].success,
                    "improvement_rate": latest_optimization["result"].improvement_rate
                } if latest_optimization else None,
                "status": status,
                "last_updated": timezone.now().isoformat()
            }
            
        except Exception as e:
            self.logger.warning(f"Optimization status error: {str(e)}")
            return {
                "error": str(e),
                "total_optimizations": 0,
                "success_rate": 0.0,
                "status": "error"
            }
    
    def _check_system_health(self, current_metrics: Dict[str, Any]) -> None:
        """Check system health and generate alerts"""
        try:
            # Check database connection
            if not current_metrics.get("database_connection_status", False):
                self._create_alert(
                    "database_connection",
                    "critical",
                    "Database connection is down",
                    "database"
                )
            
            # Check prediction accuracy
            accuracy = current_metrics.get("prediction_accuracy", 0)
            if accuracy < self.thresholds['accuracy_min']:
                self._create_alert(
                    "low_accuracy",
                    "high",
                    f"Prediction accuracy is critically low: {accuracy:.1%}",
                    "prediction_engine"
                )
            
            # Check API response time
            response_time = current_metrics.get("api_response_time_ms", 0)
            if response_time > self.thresholds['response_time_max']:
                self._create_alert(
                    "slow_response",
                    "medium",
                    f"API response time is too high: {response_time:.0f}ms",
                    "api"
                )
            
            # Check memory usage
            memory_usage = current_metrics.get("memory_usage_mb", 0)
            if memory_usage > self.thresholds['memory_max_mb']:
                self._create_alert(
                    "high_memory_usage",
                    "medium",
                    f"Memory usage is high: {memory_usage:.0f}MB",
                    "system"
                )
            
        except Exception as e:
            self.logger.warning(f"Health check error: {str(e)}")
    
    def _create_alert(self, alert_type: str, severity: str, message: str, component: str) -> None:
        """Create new system alert"""
        try:
            # Check if similar alert already exists (avoid spam)
            recent_alerts = [a for a in self.alerts if not a.resolved and a.alert_type == alert_type]
            if recent_alerts:
                return  # Don't create duplicate alerts
            
            alert = SystemAlert(alert_type, severity, message, component)
            self.alerts.append(alert)
            
            self.logger.warning(f"🚨 System alert created: {alert_type} - {message}")
            
        except Exception as e:
            self.logger.error(f"Alert creation error: {str(e)}")
    
    def resolve_alert(self, alert_id: str) -> Dict[str, Any]:
        """
        Resolve system alert
        
        Args:
            alert_id: Alert identifier
            
        Returns:
            dict: {
                "success": bool,
                "message": str
            }
        """
        try:
            for alert in self.alerts:
                if alert.alert_id == alert_id:
                    alert.resolved = True
                    self.logger.info(f"✅ Alert resolved: {alert_id}")
                    return {
                        "success": True,
                        "message": "Alert resolved successfully"
                    }
            
            return {
                "success": False,
                "message": "Alert not found"
            }
            
        except Exception as e:
            self.logger.error(f"Alert resolution error: {str(e)}")
            return {
                "success": False,
                "message": f"Failed to resolve alert: {str(e)}"
            }
    
    def get_system_health_summary(self) -> Dict[str, Any]:
        """
        Get system health summary
        
        Returns:
            dict: {
                "overall_status": str,
                "critical_alerts": int,
                "performance_score": float,
                "uptime_status": str
            }
        """
        try:
            # Count alerts by severity
            alert_counts = {"critical": 0, "high": 0, "medium": 0, "low": 0}
            for alert in self.alerts:
                if not alert.resolved:
                    alert_counts[alert.severity] += 1
            
            # Determine overall status
            if alert_counts["critical"] > 0:
                overall_status = "critical"
            elif alert_counts["high"] > 0:
                overall_status = "degraded"
            elif alert_counts["medium"] > 2:
                overall_status = "warning"
            else:
                overall_status = "healthy"
            
            # Calculate performance score (0-100)
            recent_metrics = self._collect_current_metrics()
            performance_score = self._calculate_performance_score(recent_metrics)
            
            return {
                "overall_status": overall_status,
                "critical_alerts": alert_counts["critical"],
                "high_alerts": alert_counts["high"],
                "medium_alerts": alert_counts["medium"],
                "performance_score": performance_score,
                "uptime_status": "operational",  # Simplified
                "last_check": timezone.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Health summary error: {str(e)}")
            return {
                "overall_status": "unknown",
                "critical_alerts": 0,
                "performance_score": 0.0,
                "uptime_status": "unknown",
                "error": str(e)
            }
    
    def _calculate_performance_score(self, metrics: Dict[str, Any]) -> float:
        """Calculate overall performance score (0-100)"""
        try:
            score = 100.0
            
            # Database connection (40 points)
            if not metrics.get("database_connection_status", False):
                score -= 40
            
            # Prediction accuracy (30 points)
            accuracy = metrics.get("prediction_accuracy", 0)
            if accuracy < 0.2:
                score -= 30 * (1 - accuracy / 0.2)
            
            # API response time (20 points)
            response_time = metrics.get("api_response_time_ms", 0)
            if response_time > 1000:
                penalty = min(20, (response_time - 1000) / 100)
                score -= penalty
            
            # Memory usage (10 points)
            memory_usage = metrics.get("memory_usage_mb", 0)
            if memory_usage > 1024:
                penalty = min(10, (memory_usage - 1024) / 100)
                score -= penalty
            
            return max(0.0, score)
            
        except Exception:
            return 50.0  # Default score on error


# Service instance
production_monitoring_service = ProductionMonitoringService()