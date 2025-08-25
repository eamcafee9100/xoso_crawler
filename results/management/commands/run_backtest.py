# management/commands/run_backtest.py
from django.core.management.base import BaseCommand
from results.predictors import EnhancedCyclePredictor

class Command(BaseCommand):
    help = 'Chạy backtest cho mô hình dự đoán'

    def handle(self, *args, **options):
        predictor = EnhancedCyclePredictor()
        results = []
        
        data = KetQuaXoSo.objects.all().order_by('ngay')
        window_size = 365  # 1 năm làm dữ liệu huấn luyện
        
        for i in range(window_size, len(data)):
            train_data = data[i-window_size:i]
            test_data = data[i]
            
            # Huấn luyện và dự đoán
            predictor.predict(train_data)
            predictions = predictor.predictions
            
            # Đánh giá
            actual = test_data.get_all_2digit_numbers()
            metrics = predictor.evaluate(predictions, actual)
            
            # Lưu kết quả
            results.append(metrics)
            
            # Cập nhật model
            predictor.update_weights(predictions, actual)
            
        self._generate_report(results)

    def _generate_report(self, results):
        avg_precision = sum(r['precision'] for r in results) / len(results)
        avg_recall = sum(r['recall'] for r in results) / len(results)
        print(f"Báo cáo Backtesting:\nĐộ chính xác trung bình: {avg_precision:.2%}\nRecall trung bình: {avg_recall:.2%}")