# results/cron.py
from django_cron import CronJobBase, Schedule
from .models import KetQuaXoSo, CycleAccuracy
from .hybrid_predictor import HybridPredictor
from datetime import date, timedelta
from .tasks import update_cycle_weights

class UpdateWeightsCronJob(CronJobBase):
    RUN_AT_TIMES = ['03:00']  # Chạy lúc 3h sáng hàng ngày
    
    schedule = Schedule(run_at_times=RUN_AT_TIMES)
    code = 'results.update_weights'
    
    def do(self):
        update_cycle_weights()

class UpdateCycleAccuracyJob(CronJobBase):
    RUN_AT_TIMES = ['00:01']  # Chạy lúc 00:01 hàng ngày
    
    schedule = Schedule(run_at_times=RUN_AT_TIMES)
    code = 'results.update_cycle_accuracy'
    
    def do(self):
        from .tasks import update_cycle_accuracy
        update_cycle_accuracy()


class UpdateCycleWeightsJob(CronJobBase):
    RUN_AT_TIMES = ['03:00']  # Chạy lúc 3h sáng hàng ngày
    schedule = Schedule(run_at_times=RUN_AT_TIMES)
    code = 'results.update_cycle_weights'
    
    def do(self):
        predictor = HybridPredictor()
        today = date.today()
        history = KetQuaXoSo.objects.filter(ngay__lt=today).order_by('-ngay')[:30]
        
        if len(history) < 30:
            return  # Không đủ dữ liệu
        
        # Lấy kết quả hôm qua để kiểm tra
        yesterday = today - timedelta(days=1)
        yesterday_result = KetQuaXoSo.objects.filter(ngay=yesterday).first()
        
        if not yesterday_result:
            return
        
        actual_numbers = set(yesterday_result.get_all_2digit_numbers())
        
        for cycle in ['1_ngay', '3_ngay', '7_ngay', '14_ngay', '30_ngay']:
            # Lấy dự đoán từ model tương ứng
            predictions = predictor.predict(yesterday, history)
            predicted_numbers = {num for num, _ in predictions['predicted_numbers']}
            
            # Tính độ chính xác
            correct = len(actual_numbers & predicted_numbers)
            total = len(predicted_numbers)
            
            # Cập nhật vào database
            cycle_acc, _ = CycleAccuracy.objects.get_or_create(cycle_type=cycle)
            cycle_acc.total_predictions += total
            cycle_acc.correct_predictions += correct
            cycle_acc.accuracy = (correct / total * 100) if total > 0 else 0
            cycle_acc.save()