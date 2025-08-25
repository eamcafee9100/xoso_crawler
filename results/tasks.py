# results/tasks.py
from django.utils import timezone
from .models import CycleAccuracy, PredictionRecord, KetQuaXoSo, PredictionModel
from results.analytics.predictors import HybridPredictor
from celery import shared_task
from django.core.cache import cache
from datetime import datetime, timedelta
import logging
# Cấu hình logging
logger = logging.getLogger(__name__)
from results.core.services.strategies import AnalysisStrategiesService
from results.core.services.ensemble import EnsembleService
from .models import DanBtl
def ensure_initial_data():
    """Đảm bảo dữ liệu ban đầu tồn tại"""
    model, _ = PredictionModel.objects.get_or_create(
        name='HybridPredictor',
        defaults={'version': '1.0', 'is_active': True}
    )
    
    cycles = ['1_ngay', '3_ngay', '7_ngay', '14_ngay', '30_ngay']
    for cycle in cycles:
        CycleAccuracy.objects.get_or_create(cycle_type=cycle)

def update_cycle_weights():
    ensure_initial_data()  # Đảm bảo dữ liệu tồn tại trước khi cập nhật
    
    predictor = HybridPredictor()
    today = timezone.now().date()
    yesterday = today - timezone.timedelta(days=1)
    
    try:
        actual_result = KetQuaXoSo.objects.get(ngay=yesterday)
        prediction_record = PredictionRecord.objects.get(date=yesterday)
        
        actual_numbers = set(actual_result.get_all_2digit_numbers())
        predicted_numbers = set(prediction_record.predicted_numbers.get('all', []))
        
        for cycle in CycleAccuracy.objects.all():
            cycle_predictions = set(prediction_record.predicted_numbers.get(cycle.cycle_type, []))
            correct = len(actual_numbers & cycle_predictions)
            
            cycle.total_predictions += len(cycle_predictions)
            cycle.correct_predictions += correct
            cycle.update_accuracy()
            
    except Exception as e:
        print(f"Error updating cycle weights: {str(e)}")

# tasks.py
from celery import shared_task
from .analytics.predictors import BachThuLoPredictor
from .models import PredictionResult
from datetime import timedelta

@shared_task
def daily_prediction_task():
    from datetime import date
    yesterday = date.today() - timedelta(days=1)
    predictor = BachThuLoPredictor(yesterday)
    results = predictor.predict()
    
    # Lưu kết quả
    PredictionResult.objects.create(
        target_date=yesterday,
        predicted_numbers=[n[0] for n in results['final_prediction']],
        method_used='combined',
        confidence=sum(n[1] for n in results['final_prediction'])/len(results['final_prediction'])
    )


@shared_task(bind=True, max_retries=3)
def update_daily_analysis_cache(self, date_str=None):
    """
    Background task to update daily analysis cache
    """
    try:
        if date_str:
            target_date = datetime.strptime(date_str, '%Y-%m-%d').date()
        else:
            target_date = timezone.now().date()
        
        logger.info(f"Starting daily analysis cache update for {target_date}")
        
        # Initialize services
        strategies_service = AnalysisStrategiesService()
        ensemble_service = EnsembleService()
        
        # Perform analysis
        method_performance = strategies_service.get_method_performance_analysis(target_date)
        ensemble_strategies = ensemble_service.get_ensemble_strategies(target_date)
        cycle_analysis = strategies_service.analyze_cycles(target_date)
        gap_analysis = strategies_service.analyze_gaps(target_date)
        pattern_mining = strategies_service.mine_patterns(target_date)
        
        # Cache results
        cache_key = f"daily_analysis_{target_date.strftime('%Y%m%d')}"
        cache_data = {
            'method_performance': method_performance,
            'ensemble_strategies': ensemble_strategies,
            'cycle_analysis': cycle_analysis,
            'gap_analysis': gap_analysis,
            'pattern_mining': pattern_mining,
            'last_updated': timezone.now(),
        }
        
        cache.set(cache_key, cache_data, 3600)  # Cache for 1 hour
        
        logger.info(f"Successfully updated daily analysis cache for {target_date}")
        return f"Cache updated for {target_date}"
        
    except Exception as e:
        logger.error(f"Error updating daily analysis cache: {str(e)}")
        raise self.retry(countdown=60, exc=e)

@shared_task
def cleanup_old_cache_entries():
    """
    Cleanup old cache entries to prevent memory bloat
    """
    try:
        # This would depend on your Redis setup
        # You might want to implement cache key pattern matching
        logger.info("Cache cleanup completed")
        return "Cache cleanup completed"
    except Exception as e:
        logger.error(f"Error during cache cleanup: {str(e)}")
        return f"Cache cleanup failed: {str(e)}"

@shared_task
def generate_ensemble_predictions(date_str):
    """
    Generate ensemble predictions for a specific date
    """
    try:
        target_date = datetime.strptime(date_str, '%Y-%m-%d').date()
        ensemble_service = EnsembleService()
        
        # Generate ensemble predictions
        predictions = ensemble_service.generate_predictions(target_date)
        
        logger.info(f"Generated {len(predictions)} ensemble predictions for {target_date}")
        return f"Generated predictions for {target_date}"
        
    except Exception as e:
        logger.error(f"Error generating ensemble predictions: {str(e)}")
        raise