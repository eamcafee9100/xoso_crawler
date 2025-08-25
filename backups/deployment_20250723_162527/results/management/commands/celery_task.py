# tasks.py
from celery import shared_task
from django.utils import timezone
from django.core.cache import cache
from results.analytics.predictors import BachThuLoPredictor
from datetime import timedelta

@shared_task
def precompute_predictions(days_ahead=2, history_periods=None):
    if history_periods is None:
        history_periods = [30, 60, 90]
    
    today = timezone.now().date()
    results = []
    
    for day in range(days_ahead + 1):
        target_date = today + timedelta(days=day)
        
        for history_days in history_periods:
            cache_key = f"predictions_{target_date}_{history_days}"
            
            # Chỉ tính toán nếu chưa có trong cache
            if not cache.get(cache_key):
                try:
                    predictor = BachThuLoPredictor(
                        target_date=target_date,
                        history_days=history_days
                    )
                    predictions = predictor.predict()
                    cache.set(cache_key, predictions, timeout=24*3600)  # Cache 24h
                    results.append(f"Success: {target_date} ({history_days} days)")
                except Exception as e:
                    results.append(f"Failed: {target_date} ({history_days} days) - {str(e)}")
    
    return results