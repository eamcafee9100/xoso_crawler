# lottery_prediction/tasks.py
from celery import shared_task
from django.utils import timezone
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

@shared_task(bind=True, max_retries=3)
def retrain_models_task(self):
    """Automated model retraining task"""
    try:
        from lottery_prediction.ml.models.model_manager import ModelManager
        from lottery_prediction.monitoring.alerts import AlertManager, AlertLevel
        
        manager = ModelManager()
        alert_manager = AlertManager()
        
        # Check if retraining is needed
        if manager.should_retrain():
            logger.info("Starting automated model retraining...")
            
            # Perform retraining
            results = manager.retrain_all_models()
            
            # Send success alert
            alert_manager.send_alert(
                title="Model Retraining Completed",
                message="Automated model retraining completed successfully",
                level=AlertLevel.INFO,
                metadata={
                    'retrained_models': len(results),
                    'best_model': results.get('best_model'),
                    'performance_improvement': results.get('improvement', 0)
                }
            )
            
            return results
        else:
            logger.info("No retraining needed")
            return {"status": "no_retraining_needed"}
            
    except Exception as e:
        logger.error(f"Model retraining failed: {e}")
        
        # Send failure alert
        from lottery_prediction.monitoring.alerts import AlertManager, AlertLevel
        alert_manager = AlertManager()
        alert_manager.send_alert(
            title="Model Retraining Failed",
            message=f"Automated model retraining failed: {str(e)}",
            level=AlertLevel.CRITICAL,
            metadata={'error': str(e)}
        )
        
        # Retry the task
        raise self.retry(exc=e, countdown=60 * 5)  # Retry after 5 minutes

@shared_task
def daily_performance_check():
    """Daily performance monitoring"""
    try:
        from lottery_prediction.monitoring.alerts import AlertMonitor
        
        monitor = AlertMonitor()
        
        # Run all monitoring checks
        monitor.check_model_performance()
        monitor.check_system_resources()
        monitor.check_prediction_failures()
        
        logger.info("Daily performance check completed")
        
    except Exception as e:
        logger.error(f"Daily performance check failed: {e}")

@shared_task
def generate_daily_predictions():
    """Generate predictions for the next day"""
    try:
        from lottery_prediction.api.views import PredictionAPIView
        from datetime import datetime, timedelta
        
        tomorrow = datetime.now().date() + timedelta(days=1)
        
        # Generate prediction
        view = PredictionAPIView()
        result = view.generate_prediction_for_date(tomorrow)
        
        logger.info(f"Daily prediction generated for {tomorrow}")
        return result
        
    except Exception as e:
        logger.error(f"Daily prediction generation failed: {e}")
        raise

@shared_task
def cleanup_old_data():
    """Clean up old data to manage storage"""
    try:
        from lottery_prediction.models import PredictionResult, NumberFrequencyStats
        from datetime import datetime, timedelta
        
        # Keep only last 2 years of prediction results
        cutoff_date = datetime.now() - timedelta(days=730)
        
        deleted_predictions = PredictionResult.objects.filter(
            created_at__lt=cutoff_date
        ).delete()
        
        # Keep only last 3 years of frequency stats
        stats_cutoff = datetime.now().date() - timedelta(days=1095)
        deleted_stats = NumberFrequencyStats.objects.filter(
            date__lt=stats_cutoff
        ).delete()
        
        logger.info(f"Cleanup completed: {deleted_predictions[0]} predictions, {deleted_stats[0]} stats deleted")
        
        return {
            'deleted_predictions': deleted_predictions[0],
            'deleted_stats': deleted_stats[0]
        }
        
    except Exception as e:
        logger.error(f"Data cleanup failed: {e}")
        raise

@shared_task
def backup_database():
    """Create database backup"""
    try:
        import subprocess
        import os
        from django.conf import settings
        
        # Generate backup filename
        backup_filename = f"lottery_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.sql"
        backup_path = os.path.join('/backup', backup_filename)
        
        # Create backup
        db_url = settings.DATABASES['default']
        cmd = [
            'pg_dump',
            f"--host={db_url.get('HOST', 'localhost')}",
            f"--port={db_url.get('PORT', 5432)}",
            f"--username={db_url['USER']}",
            f"--dbname={db_url['NAME']}",
            f"--file={backup_path}",
            '--verbose'
        ]
        
        env = os.environ.copy()
        env['PGPASSWORD'] = db_url['PASSWORD']
        
        result = subprocess.run(cmd, env=env, capture_output=True, text=True)
        
        if result.returncode == 0:
            logger.info(f"Database backup created: {backup_filename}")
            
            # Clean up old backups (keep last 7 days)
            cleanup_old_backups()
            
            return {"backup_file": backup_filename, "status": "success"}
        else:
            raise Exception(f"Backup failed: {result.stderr}")
            
    except Exception as e:
        logger.error(f"Database backup failed: {e}")
        raise

def cleanup_old_backups():
    """Remove backups older than 7 days"""
    import os
    import glob
    from datetime import datetime, timedelta
    
    backup_dir = '/backup'
    cutoff_time = datetime.now() - timedelta(days=7)
    
    for backup_file in glob.glob(os.path.join(backup_dir, 'lottery_backup_*.sql')):
        file_time = datetime.fromtimestamp(os.path.getctime(backup_file))
        if file_time < cutoff_time:
            os.remove(backup_file)
            logger.info(f"Removed old backup: {backup_file}")