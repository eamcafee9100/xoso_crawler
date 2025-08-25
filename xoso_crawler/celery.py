# celery.py
from celery import Celery
from django.conf import settings
import os
from celery.schedules import crontab

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'xoso_crawler.settings')
app = Celery('xoso_crawler')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()

# Thiết lập lịch trình tổng hợp
app.conf.beat_schedule = {
    # Task bảo trì hàng ngày hiện có
    'daily-maintenance': {
        'task': 'lokhung.tasks.daily_maintenance',
        'schedule': crontab(hour=23, minute=30),  # Chạy lúc 23h30 hàng ngày
    },
    
    # Task dự đoán ML hàng ngày mới
    'daily-ml-prediction': {
        'task': 'services.ml_service.MLPredictor.daily_prediction_task',
        'schedule': crontab(hour=22, minute=0),  # Chạy lúc 22h hàng ngày (trước task bảo trì)
        'args': ('random_forest', 15),  # Sử dụng random_forest và lấy top 15 số
        'options': {'queue': 'ml'}  # Có thể dùng queue riêng cho task ML
    },
    
    # Task huấn luyện lại model hàng tuần
    'weekly-ml-retraining': {
        'task': 'services.ml_tasks.train_ml_model',
        'schedule': crontab(day_of_week=0, hour=2),  # Chủ nhật hàng tuần lúc 2h sáng
        'args': ('random_forest', {'n_estimators': 100, 'max_depth': 10}),
        'options': {'queue': 'ml'}
    },
}

# Cấu hình thêm cho Celery (nếu cần)
app.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='Asia/Ho_Chi_Minh',
    enable_utc=True,
)

# Cấu hình queue riêng cho các task ML (tuỳ chọn)
app.conf.task_routes = {
    'services.ml_service.*': {'queue': 'ml'},
    'services.ml_tasks.*': {'queue': 'ml'},
    'lokhung.tasks.*': {'queue': 'default'},
}