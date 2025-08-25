# lottery_prediction/monitoring/health.py
from django.http import JsonResponse
from django.db import connection
from django.core.cache import cache
import redis
import os
from datetime import datetime, timedelta

class HealthChecker:
    def __init__(self):
        self.checks = {
            'database': self.check_database,
            'redis': self.check_redis,
            'models': self.check_models,
            'disk_space': self.check_disk_space,
            'recent_predictions': self.check_recent_predictions
        }

    def check_database(self):
        """Check database connectivity"""
        try:
            with connection.cursor() as cursor:
                cursor.execute('SELECT 1')
                return {'status': 'healthy', 'latency_ms': 0}
        except Exception as e:
            return {'status': 'unhealthy', 'error': str(e)}

    def check_redis(self):
        """Check Redis connectivity"""
        try:
            cache.set('health_check', 'ok', 10)
            result = cache.get('health_check')
            if result == 'ok':
                return {'status': 'healthy'}
            else:
                return {'status': 'unhealthy', 'error': 'Cache read/write failed'}
        except Exception as e:
            return {'status': 'unhealthy', 'error': str(e)}

    def check_models(self):
        """Check if ML models are available"""
        try:
            from lottery_prediction.ml.models.model_manager import ModelManager
            manager = ModelManager()
            models = manager.list_available_models()
            
            if models:
                return {'status': 'healthy', 'available_models': len(models)}
            else:
                return {'status': 'unhealthy', 'error': 'No models available'}
        except Exception as e:
            return {'status': 'unhealthy', 'error': str(e)}

    def check_disk_space(self):
        """Check available disk space"""
        try:
            import shutil
            total, used, free = shutil.disk_usage('/')
            free_percent = (free / total) * 100
            
            if free_percent > 10:  # More than 10% free
                return {'status': 'healthy', 'free_percent': round(free_percent, 2)}
            else:
                return {'status': 'warning', 'free_percent': round(free_percent, 2)}
        except Exception as e:
            return {'status': 'unhealthy', 'error': str(e)}

    def check_recent_predictions(self):
        """Check if recent predictions exist"""
        try:
            from lottery_prediction.models import PredictionResult
            recent_prediction = PredictionResult.objects.filter(
                created_at__gte=datetime.now() - timedelta(days=1)
            ).first()
            
            if recent_prediction:
                return {'status': 'healthy', 'last_prediction': recent_prediction.created_at.isoformat()}
            else:
                return {'status': 'warning', 'message': 'No recent predictions'}
        except Exception as e:
            return {'status': 'unhealthy', 'error': str(e)}

    def run_all_checks(self):
        """Run all health checks"""
        results = {}
        overall_status = 'healthy'
        
        for check_name, check_func in self.checks.items():
            try:
                result = check_func()
                results[check_name] = result
                
                if result['status'] == 'unhealthy':
                    overall_status = 'unhealthy'
                elif result['status'] == 'warning' and overall_status == 'healthy':
                    overall_status = 'warning'
                    
            except Exception as e:
                results[check_name] = {'status': 'unhealthy', 'error': str(e)}
                overall_status = 'unhealthy'

        return {
            'overall_status': overall_status,
            'timestamp': datetime.now().isoformat(),
            'checks': results
        }

def health_check_view(request):
    """Health check endpoint"""
    checker = HealthChecker()
    health_data = checker.run_all_checks()
    
    status_code = 200
    if health_data['overall_status'] == 'unhealthy':
        status_code = 503
    elif health_data['overall_status'] == 'warning':
        status_code = 200  # Still return 200 for warnings

    return JsonResponse(health_data, status=status_code)