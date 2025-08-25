# tasks.py
import logging
from datetime import datetime, timedelta
from django.utils import timezone
from celery import shared_task

from .bac_nho_analyzer import BacNhoAnalyzer

logger = logging.getLogger(__name__)

@shared_task
def update_bac_nho_results():
    """Task cập nhật kết quả thực tế cho các dự đoán bạc nhớ"""
    try:
        analyzer = BacNhoAnalyzer()
        result = analyzer.update_prediction_results()
        
        logger.info(f"Đã cập nhật kết quả bạc nhớ: {result}")
        return result
    except Exception as e:
        logger.error(f"Lỗi khi cập nhật kết quả bạc nhớ: {e}")
        return {"status": "error", "message": str(e)}

@shared_task
def generate_bac_nho_prediction():
    """Task tạo dự đoán bạc nhớ hàng ngày"""
    try:
        # Dự đoán cho ngày mai
        target_date = timezone.now().date() + timedelta(days=1)
        
        analyzer = BacNhoAnalyzer(target_date=target_date)
        result = analyzer.analyze_and_predict()
        
        logger.info(f"Đã tạo dự đoán bạc nhớ cho ngày {target_date}")
        return {"status": "success", "target_date": target_date.strftime("%Y-%m-%d")}
    except Exception as e:
        logger.error(f"Lỗi khi tạo dự đoán bạc nhớ: {e}")
        return {"status": "error", "message": str(e)}

@shared_task
def discover_new_bac_nho_patterns():
    """Task định kỳ phát hiện quy luật bạc nhớ mới"""
    try:
        analyzer = BacNhoAnalyzer()
        result = analyzer.discover_new_patterns()
        
        logger.info(f"Đã phát hiện quy luật bạc nhớ mới: {result.get('message', 'Unknown')}")
        return {"status": "success", "message": result.get('message', 'Completed')}
    except Exception as e:
        logger.error(f"Lỗi khi phát hiện quy luật bạc nhớ mới: {e}")
        return {"status": "error", "message": str(e)}
    
from celery import shared_task
from datetime import date, timedelta
import logging

from .core.services.ensemble import combine_strategies, get_historical_hits
from .models import BtlAnalytics, OptimalMethodEnsemble

logger = logging.getLogger(__name__)

@shared_task
def precompute_daily_analysis(analysis_date_str: str):
    """
    Task tính toán trước phân tích cho một ngày
    """
    try:
        analysis_date = date.fromisoformat(analysis_date_str)
        
        # Lấy dữ liệu lịch sử
        history_data = get_historical_hits(analysis_date)
        
        # Kết hợp chiến lược
        recommendations = combine_strategies(analysis_date, history_data)
        
        # Lưu kết quả vào OptimalMethodEnsemble
        optimal_methods = [
            {
                'method_name': rec['number'], 
                'score': rec['score'],
                'strategies': rec['strategies']
            } 
            for rec in recommendations[:20]
        ]
        
        ensemble, created = OptimalMethodEnsemble.objects.get_or_create(
            analysis_date=analysis_date,
            defaults={
                'optimal_methods_json': json.dumps(optimal_methods),
                'method_count': len(optimal_methods)
            }
        )
        
        if not created:
            ensemble.optimal_methods_json = json.dumps(optimal_methods)
            ensemble.method_count = len(optimal_methods)
            ensemble.save()
        
        logger.info(f"Precomputed analysis for {analysis_date}")
        return f"Completed analysis for {analysis_date}"
        
    except Exception as e:
        logger.error(f"Error in precompute_daily_analysis: {e}")
        raise

@shared_task
def batch_precompute_analysis(days_ahead: int = 7):
    """
    Task tính toán batch cho nhiều ngày
    """
    today = date.today()
    
    for i in range(days_ahead):
        target_date = today + timedelta(days=i)
        precompute_daily_analysis.delay(target_date.isoformat())
    
    return f"Scheduled analysis for {days_ahead} days"