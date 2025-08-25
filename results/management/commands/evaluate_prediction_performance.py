from django.core.management.base import BaseCommand
from django.utils import timezone
import logging
from datetime import datetime , timedelta
from results.analytics.performance_evaluator import PerformanceEvaluator

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Đánh giá hiệu suất các phương pháp dự đoán trên dữ liệu lịch sử'

    def add_arguments(self, parser):
        parser.add_argument(
            '--days',
            type=int,
            default=30,
            help='Số ngày cần phân tích'
        )
        parser.add_argument(
            '--end-date',
            type=str,
            help='Ngày kết thúc phân tích (YYYY-MM-DD), mặc định là hôm qua'
        )
        parser.add_argument(
            '--update-frequency',
            action='store_true',
            help='Cập nhật thống kê tần suất số'
        )
        parser.add_argument(
            '--target-date',
            type=str,
            help='Ngày cần tạo dự đoán (YYYY-MM-DD), mặc định là hôm nay'
        )

    def handle(self, *args, **options):
        days = options['days']
        end_date = None
        target_date = None
        
        if options['end_date']:
            try:
                end_date = datetime.strptime(options['end_date'], '%Y-%m-%d').date()
            except Exception as e:
                self.stderr.write(f"Lỗi khi phân tích end-date: {e}")
                end_date = timezone.now().date() - timedelta(days=1)
        else:
            end_date = timezone.now().date() - timedelta(days=1)
            
        if options['target_date']:
            try:
                target_date = datetime.strptime(options['target_date'], '%Y-%m-%d').date()
            except Exception as e:
                self.stderr.write(f"Lỗi khi phân tích target-date: {e}")
                target_date = timezone.now().date()
        else:
            target_date = timezone.now().date()
            
        self.stdout.write(f"Đánh giá hiệu suất dự đoán cho {days} ngày gần nhất kết thúc vào {end_date}")
        
        evaluator = PerformanceEvaluator(target_date=target_date, historical_days=days)
        
        try:
            results = evaluator.run_historical_evaluation(end_date=end_date, days=days)
            
            self.stdout.write(self.style.SUCCESS(f"Đánh giá hoàn thành thành công"))
            
            # In thống kê tổng quan
            self.stdout.write("\nThống kê tổng quan:")
            overall_stats = results.get('overall_stats', {})
            
            for method, stats in overall_stats.get('method_stats', {}).items():
                self.stdout.write(f"Phương pháp: {method}")
                self.stdout.write(f"  Tỷ lệ trúng: {stats.get('hit_rate', 0):.2f}%")
                self.stdout.write(f"  Tỷ lệ ngày trúng: {stats.get('day_hit_rate', 0):.2f}%")
                self.stdout.write(f"  Tỷ lệ mệt mỏi: {stats.get('tired_rate', 0):.2f}%")
                self.stdout.write(f"  Tổng số trúng: {stats.get('correct_predictions', 0)}/{stats.get('total_predictions', 0)}")
                
            # In trọng số đã cập nhật
            self.stdout.write("\nTrọng số phương pháp đã cập nhật:")
            weights = evaluator.get_current_method_weights()
            
            for method, weight in weights.items():
                self.stdout.write(f"  {method}: {weight:.2f}")
                
            # Cập nhật thống kê tần suất nếu được yêu cầu
            if options['update_frequency']:
                self.stdout.write("\nCập nhật thống kê tần suất số...")
                
                # Cập nhật 90 ngày gần nhất
                start_date = end_date - timedelta(days=90)
                current_date = start_date
                
                update_dates = []
                while current_date <= end_date:
                    update_dates.append(current_date)
                    current_date += timedelta(days=1)
                
                evaluator.update_number_frequency_stats(update_dates)
                self.stdout.write(self.style.SUCCESS(f"Đã cập nhật thống kê tần suất cho {len(update_dates)} ngày"))
                
        except Exception as e:
            self.stderr.write(self.style.ERROR(f"Lỗi trong quá trình đánh giá: {e}"))
            logger.error(f"Lỗi trong lệnh evaluate_prediction_performance: {e}", exc_info=True)