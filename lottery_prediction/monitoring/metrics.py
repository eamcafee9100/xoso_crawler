# lottery_prediction/monitoring/metrics.py
from prometheus_client import Counter, Histogram, Gauge, generate_latest
from django.http import HttpResponse
import time
import psutil
from django.db import connection

# Metrics
prediction_requests = Counter('lottery_prediction_requests_total', 'Total prediction requests', ['status'])
prediction_duration = Histogram('lottery_prediction_duration_seconds', 'Prediction request duration')
model_accuracy = Gauge('lottery_model_accuracy', 'Current model accuracy', ['model_name'])
system_memory = Gauge('lottery_system_memory_usage_bytes', 'System memory usage')
database_connections = Gauge('lottery_database_connections', 'Active database connections')

class MetricsCollector:
    @staticmethod
    def collect_system_metrics():
        """Collect system-level metrics"""
        # Memory usage
        memory = psutil.virtual_memory()
        system_memory.set(memory.used)
        
        # Database connections
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT count(*) 
                FROM pg_stat_activity 
                WHERE datname = current_database()
            """)
            db_conns = cursor.fetchone()[0]
            database_connections.set(db_conns)

    @staticmethod
    def record_prediction_request(status_code, duration):
        """Record prediction request metrics"""
        status = 'success' if status_code < 400 else 'error'
        prediction_requests.labels(status=status).inc()
        prediction_duration.observe(duration)

    @staticmethod
    def update_model_accuracy(model_name, accuracy):
        """Update model accuracy metric"""
        model_accuracy.labels(model_name=model_name).set(accuracy)

def metrics_view(request):
    """Prometheus metrics endpoint"""
    MetricsCollector.collect_system_metrics()
    return HttpResponse(generate_latest(), content_type='text/plain')