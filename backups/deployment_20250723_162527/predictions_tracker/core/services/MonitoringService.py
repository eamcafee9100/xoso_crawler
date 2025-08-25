import logging
from datetime import date, datetime, timedelta
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from collections import defaultdict, deque
from threading import Lock
import json

from django.core.cache import cache
from django.db.models import Count, Avg, Max, Min
from django.utils import timezone

from predictions_tracker.models import (
    PredictionMethod,
    MethodCyclicalPerformance,
    CyclicalContextEngine,
    ABTestVariant,
    ABTestResult
)
from predictions_tracker.core.services.CyclicalValidationService import cyclical_validation_service
from predictions_tracker.core.services.ParameterOptimizationService import parameter_optimization_service

logger = logging.getLogger(__name__)


@dataclass
class SystemHealthMetrics:
    """Cấu trúc metrics về system health"""
    timestamp: str
    api_response_time_ms: float
    prediction_accuracy: float
    active_methods_count: int
    failed_predictions_count: int
    memory_usage_mb: float
    database_connection_status: bool
    cache_hit_rate: float


@dataclass 
class PerformanceAlert:
    """Cấu trúc alert về performance"""
    alert_id: str
    severity: str  # 'low', 'medium', 'high', 'critical'
    alert_type: str  # 'accuracy_drop', 'response_time', 'system_error'
    message: str
    details: Dict[str, Any]
    timestamp: str
    resolved: bool = False


@dataclass
class MonitoringDashboardData:
    """Cấu trúc data cho monitoring dashboard"""
    current_metrics: SystemHealthMetrics
    recent_alerts: List[PerformanceAlert]
    performance_trends: Dict[str, List[float]]
    method_performance: Dict[str, Dict[str, float]]
    ab_test_status: Dict[str, Any]
    optimization_status: Dict[str, Any]


class MonitoringService:
    """Service cho real-time monitoring và alerting"""
    
    def __init__(self):
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        self._metrics_history = deque(maxlen=1000)  # Keep last 1000 metrics
        self._active_alerts = {}
        self._lock = Lock()
        
        # Alert thresholds
        self._alert_thresholds = {
            'accuracy_drop_threshold': 0.10,  # 10% drop in accuracy
            'response_time_threshold': 5000,  # 5 seconds
            'failed_predictions_threshold': 5,  # 5 failed predictions
            'memory_usage_threshold': 1024,   # 1GB memory usage
        }
    
    def collect_system_metrics(self) -> SystemHealthMetrics:
        """
        Collect current system health metrics
        
        Returns:
            SystemHealthMetrics: Current system metrics với đầy đủ thông tin
        """
        try:
            timestamp = timezone.now().isoformat()
            
            # 1. API Response Time (simulate - trong production sẽ track thực tế)
            api_response_time = self._measure_api_response_time()
            
            # 2. Prediction Accuracy (recent 7 days)
            prediction_accuracy = self._calculate_recent_accuracy()
            
            # 3. Active Methods Count
            active_methods_count = PredictionMethod.objects.filter(is_active=True).count()
            
            # 4. Failed Predictions Count (today)
            failed_predictions_count = self._count_failed_predictions_today()
            
            # 5. Memory Usage (simulate)
            memory_usage_mb = self._get_memory_usage()
            
            # 6. Database Connection
            db_connection_status = self._check_database_connection()
            
            # 7. Cache Hit Rate
            cache_hit_rate = self._calculate_cache_hit_rate()
            
            metrics = SystemHealthMetrics(
                timestamp=timestamp,
                api_response_time_ms=api_response_time,
                prediction_accuracy=prediction_accuracy,
                active_methods_count=active_methods_count,
                failed_predictions_count=failed_predictions_count,
                memory_usage_mb=memory_usage_mb,
                database_connection_status=db_connection_status,
                cache_hit_rate=cache_hit_rate
            )
            
            # Store metrics history
            with self._lock:
                self._metrics_history.append(metrics)
            
            # Check for alerts
            self._check_and_trigger_alerts(metrics)
            
            self.logger.debug(f"📊 Metrics collected: accuracy={prediction_accuracy:.1%}, response_time={api_response_time:.0f}ms")
            
            return metrics
            
        except Exception as e:
            self.logger.error(f"❌ Failed to collect system metrics: {str(e)}", exc_info=True)
            return SystemHealthMetrics(
                timestamp=timezone.now().isoformat(),
                api_response_time_ms=0.0,
                prediction_accuracy=0.0,
                active_methods_count=0,
                failed_predictions_count=0,
                memory_usage_mb=0.0,
                database_connection_status=False,
                cache_hit_rate=0.0
            )
    
    def get_dashboard_data(self) -> MonitoringDashboardData:
        """
        Get comprehensive data cho monitoring dashboard
        
        Returns:
            MonitoringDashboardData: Comprehensive monitoring data
        """
        try:
            # 1. Current metrics
            current_metrics = self.collect_system_metrics()
            
            # 2. Recent alerts (last 24 hours)
            recent_alerts = self._get_recent_alerts(hours=24)
            
            # 3. Performance trends (last 7 days)
            performance_trends = self._calculate_performance_trends()
            
            # 4. Method performance summary
            method_performance = self._get_method_performance_summary()
            
            # 5. A/B test status
            ab_test_status = self._get_ab_test_status()
            
            # 6. Optimization status
            optimization_status = self._get_optimization_status()
            
            dashboard_data = MonitoringDashboardData(
                current_metrics=current_metrics,
                recent_alerts=recent_alerts,
                performance_trends=performance_trends,
                method_performance=method_performance,
                ab_test_status=ab_test_status,
                optimization_status=optimization_status
            )
            
            return dashboard_data
            
        except Exception as e:
            self.logger.error(f"❌ Failed to get dashboard data: {str(e)}", exc_info=True)
            return MonitoringDashboardData(
                current_metrics=self.collect_system_metrics(),
                recent_alerts=[],
                performance_trends={},
                method_performance={},
                ab_test_status={"error": str(e)},
                optimization_status={"error": str(e)}
            )
    
    def _measure_api_response_time(self) -> float:
        """
        Measure API response time (simplified simulation)
        
        Returns:
            float: Response time in milliseconds
        """
        # Simulate API response time measurement
        # In production, this would track actual API response times
        import random
        import time
        
        start_time = time.time()
        
        # Simulate some work
        time.sleep(0.001)  # 1ms simulation
        
        end_time = time.time()
        response_time_ms = (end_time - start_time) * 1000
        
        # Add some realistic variation
        variation = random.uniform(0.8, 1.5)
        simulated_response_time = response_time_ms * variation * random.uniform(50, 200)
        
        return round(simulated_response_time, 2)
    
    def _calculate_recent_accuracy(self) -> float:
        """
        Calculate prediction accuracy for recent period
        
        Returns:
            float: Accuracy rate (0.0 to 1.0)
        """
        try:
            # Get recent 7 days validation
            end_date = date.today() - timedelta(days=1)
            start_date = end_date - timedelta(days=7)
            
            validation_result = cyclical_validation_service.validate_cyclical_approach(
                start_date, end_date
            )
            
            if "error" in validation_result:
                return 0.0
            
            return validation_result["overall_metrics"]["accuracy"]
            
        except Exception as e:
            self.logger.warning(f"Failed to calculate recent accuracy: {str(e)}")
            return 0.0
    
    def _count_failed_predictions_today(self) -> int:
        """
        Count failed predictions for today
        
        Returns:
            int: Number of failed predictions
        """
        # Simulate failed predictions count
        # In production, this would track actual failed predictions
        import random
        return random.randint(0, 3)
    
    def _get_memory_usage(self) -> float:
        """
        Get current memory usage
        
        Returns:
            float: Memory usage in MB
        """
        try:
            import psutil
            process = psutil.Process()
            memory_mb = process.memory_info().rss / 1024 / 1024
            return round(memory_mb, 2)
        except ImportError:
            # Simulate memory usage if psutil not available
            import random
            return round(random.uniform(200, 800), 2)
    
    def _check_database_connection(self) -> bool:
        """
        Check database connection status
        
        Returns:
            bool: True if database is accessible
        """
        try:
            from django.db import connection
            with connection.cursor() as cursor:
                cursor.execute("SELECT 1")
                return True
        except Exception as e:
            self.logger.error(f"Database connection check failed: {str(e)}")
            return False
    
    def _calculate_cache_hit_rate(self) -> float:
        """
        Calculate cache hit rate
        
        Returns:
            float: Cache hit rate (0.0 to 1.0)
        """
        # Simulate cache hit rate
        # In production, this would track actual cache statistics
        import random
        return round(random.uniform(0.7, 0.95), 3)
    
    def _check_and_trigger_alerts(self, metrics: SystemHealthMetrics) -> None:
        """Check metrics against thresholds và trigger alerts nếu cần"""
        try:
            # Check accuracy drop
            if metrics.prediction_accuracy < self._alert_thresholds['accuracy_drop_threshold']:
                self._trigger_alert(
                    alert_type='accuracy_drop',
                    severity='high',
                    message=f"Prediction accuracy dropped to {metrics.prediction_accuracy:.1%}",
                    details={'current_accuracy': metrics.prediction_accuracy, 'threshold': self._alert_thresholds['accuracy_drop_threshold']}
                )
            
            # Check response time
            if metrics.api_response_time_ms > self._alert_thresholds['response_time_threshold']:
                self._trigger_alert(
                    alert_type='response_time',
                    severity='medium',
                    message=f"API response time is {metrics.api_response_time_ms:.0f}ms",
                    details={'current_response_time': metrics.api_response_time_ms, 'threshold': self._alert_thresholds['response_time_threshold']}
                )
            
            # Check failed predictions
            if metrics.failed_predictions_count >= self._alert_thresholds['failed_predictions_threshold']:
                self._trigger_alert(
                    alert_type='failed_predictions',
                    severity='medium',
                    message=f"{metrics.failed_predictions_count} failed predictions today",
                    details={'failed_count': metrics.failed_predictions_count, 'threshold': self._alert_thresholds['failed_predictions_threshold']}
                )
            
            # Check memory usage
            if metrics.memory_usage_mb > self._alert_thresholds['memory_usage_threshold']:
                self._trigger_alert(
                    alert_type='memory_usage',
                    severity='medium',
                    message=f"High memory usage: {metrics.memory_usage_mb:.0f}MB",
                    details={'memory_usage': metrics.memory_usage_mb, 'threshold': self._alert_thresholds['memory_usage_threshold']}
                )
            
            # Check database connection
            if not metrics.database_connection_status:
                self._trigger_alert(
                    alert_type='database_connection',
                    severity='critical',
                    message="Database connection failed",
                    details={'status': 'disconnected'}
                )
                
        except Exception as e:
            self.logger.error(f"Alert checking failed: {str(e)}")
    
    def _trigger_alert(
        self, 
        alert_type: str, 
        severity: str, 
        message: str, 
        details: Dict[str, Any]
    ) -> None:
        """Trigger performance alert"""
        alert_id = f"{alert_type}_{int(timezone.now().timestamp())}"
        
        # Check if similar alert already active
        existing_alert_key = f"{alert_type}_{severity}"
        if existing_alert_key in self._active_alerts:
            # Update existing alert instead of creating new one
            self._active_alerts[existing_alert_key].details.update(details)
            self._active_alerts[existing_alert_key].timestamp = timezone.now().isoformat()
            return
        
        alert = PerformanceAlert(
            alert_id=alert_id,
            severity=severity,
            alert_type=alert_type,
            message=message,
            details=details,
            timestamp=timezone.now().isoformat(),
            resolved=False
        )
        
        self._active_alerts[existing_alert_key] = alert
        
        # Log alert
        self.logger.warning(f"🚨 Alert triggered [{severity.upper()}]: {message}")
        
        # Store alert in cache for persistence
        cache_key = f"monitoring_alert_{alert_id}"
        cache.set(cache_key, alert, timeout=86400)  # 24 hours
    
    def _get_recent_alerts(self, hours: int = 24) -> List[PerformanceAlert]:
        """
        Get recent alerts
        
        Returns:
            List[PerformanceAlert]: Recent alerts sorted by timestamp
        """
        recent_alerts = []
        
        # Get from active alerts
        for alert in self._active_alerts.values():
            alert_time = datetime.fromisoformat(alert.timestamp.replace('Z', '+00:00'))
            if (timezone.now() - alert_time).total_seconds() < hours * 3600:
                recent_alerts.append(alert)
        
        # Sort by timestamp (newest first)
        recent_alerts.sort(key=lambda x: x.timestamp, reverse=True)
        
        return recent_alerts
    
    def _calculate_performance_trends(self) -> Dict[str, List[float]]:
        """
        Calculate performance trends từ metrics history
        
        Returns:
            Dict[str, List[float]]: Performance trends cho multiple metrics
        """
        trends = {
            'accuracy': [],
            'response_time': [],
            'memory_usage': [],
            'cache_hit_rate': []
        }
        
        with self._lock:
            metrics_list = list(self._metrics_history)
        
        # Take last 50 data points for trends
        recent_metrics = metrics_list[-50:] if len(metrics_list) >= 50 else metrics_list
        
        for metrics in recent_metrics:
            trends['accuracy'].append(metrics.prediction_accuracy)
            trends['response_time'].append(metrics.api_response_time_ms)
            trends['memory_usage'].append(metrics.memory_usage_mb)
            trends['cache_hit_rate'].append(metrics.cache_hit_rate)
        
        return trends
    
    def _get_method_performance_summary(self) -> Dict[str, Dict[str, float]]:
        """
        Get performance summary for all methods
        
        Returns:
            Dict[str, Dict[str, float]]: Method performance metrics
        """
        try:
            # Get recent performance data (last 30 days)
            end_date = date.today()
            start_date = end_date - timedelta(days=30)
            
            performance_data = MethodCyclicalPerformance.objects.filter(
                evaluation_date__range=[start_date, end_date]
            ).values('method__name').annotate(
                avg_hit_rate=Avg('hit_rate'),
                avg_accuracy=Avg('accuracy_score'),
                total_evaluations=Count('id'),
                latest_performance=Max('hit_rate')
            )
            
            method_performance = {}
            for data in performance_data:
                method_name = data['method__name']
                method_performance[method_name] = {
                    'avg_hit_rate': round(data['avg_hit_rate'] or 0, 3),
                    'avg_accuracy': round(data['avg_accuracy'] or 0, 3),
                    'total_evaluations': data['total_evaluations'],
                    'latest_performance': round(data['latest_performance'] or 0, 3)
                }
            
            return method_performance
            
        except Exception as e:
            self.logger.warning(f"Failed to get method performance summary: {str(e)}")
            return {}
    
    def _get_ab_test_status(self) -> Dict[str, Any]:
        """
        Get A/B testing status summary
        
        Returns:
            Dict[str, Any]: A/B test status information
        """
        try:
            # Count active tests
            active_tests = ABTestVariant.objects.filter(
                status='active',
                start_date__lte=date.today(),
                end_date__gte=date.today()
            ).values('test_name').distinct().count()
            
            # Get recent test results
            recent_results = ABTestResult.objects.filter(
                test_date__gte=date.today() - timedelta(days=7)
            ).aggregate(
                avg_accuracy=Avg('accuracy_rate'),
                total_tests=Count('id')
            )
            
            return {
                'active_tests_count': active_tests,
                'recent_avg_accuracy': round(recent_results['avg_accuracy'] or 0, 3),
                'total_recent_results': recent_results['total_tests'],
                'status': 'healthy' if active_tests > 0 else 'no_active_tests'
            }
            
        except Exception as e:
            self.logger.warning(f"Failed to get A/B test status: {str(e)}")
            return {'error': str(e), 'status': 'error'}
    
    def _get_optimization_status(self) -> Dict[str, Any]:
        """
        Get parameter optimization status
        
        Returns:
            Dict[str, Any]: Optimization status information
        """
        try:
            # Get optimization history
            history = parameter_optimization_service.get_optimization_history()
            
            if not history:
                return {
                    'status': 'no_optimizations',
                    'message': 'No optimization history found'
                }
            
            latest = history[-1]
            successful_optimizations = sum(1 for entry in history if entry['result'].success)
            
            return {
                'total_optimizations': len(history),
                'successful_optimizations': successful_optimizations,
                'latest_optimization': {
                    'timestamp': latest['timestamp'],
                    'success': latest['result'].success,
                    'improvement_rate': latest['result'].improvement_rate
                },
                'success_rate': round(successful_optimizations / len(history), 3),
                'status': 'healthy' if latest['result'].success else 'needs_attention'
            }
            
        except Exception as e:
            self.logger.warning(f"Failed to get optimization status: {str(e)}")
            return {'error': str(e), 'status': 'error'}
    
    def resolve_alert(self, alert_id: str) -> Dict[str, Any]:
        """
        Resolve an active alert
        
        Args:
            alert_id: ID of alert to resolve
            
        Returns:
            Dict[str, Any]: {"success": bool, "message": str}
        """
        try:
            # Find alert in active alerts
            alert_key_to_remove = None
            for key, alert in self._active_alerts.items():
                if alert.alert_id == alert_id:
                    alert.resolved = True
                    alert_key_to_remove = key
                    break
            
            if alert_key_to_remove:
                del self._active_alerts[alert_key_to_remove]
                self.logger.info(f"✅ Alert resolved: {alert_id}")
                return {"success": True, "message": f"Alert {alert_id} resolved"}
            else:
                return {"success": False, "message": f"Alert {alert_id} not found"}
                
        except Exception as e:
            self.logger.error(f"Failed to resolve alert: {str(e)}")
            return {"success": False, "message": f"Failed to resolve alert: {str(e)}"}


# Service instance
monitoring_service = MonitoringService()