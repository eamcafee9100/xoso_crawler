from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth import get_user_model
from datetime import datetime, timedelta

from lokhung.models import PhuongPhapTinhToan
from lokhung.utils.method_executor import method_executor

User = get_user_model()

class Command(BaseCommand):
    help = 'Chạy các phương pháp dự đoán đã import để tạo dự đoán tự động'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--analysis-date',
            type=str,
            help='Ngày phân tích (YYYY-MM-DD), mặc định là hôm qua',
        )
        parser.add_argument(
            '--prediction-date',
            type=str,
            help='Ngày dự đoán (YYYY-MM-DD), mặc định là hôm nay',
        )
        parser.add_argument(
            '--days',
            type=int,
            default=1,
            help='Số ngày để chạy dự đoán (tính từ analysis-date, mặc định: 1)',
        )
        parser.add_argument(
            '--method-id',
            type=int,
            help='ID của phương pháp cụ thể (nếu không có sẽ chạy tất cả)',
        )
        parser.add_argument(
            '--user-id',
            type=int,
            default=1,
            help='ID của user tạo dự đoán (mặc định: 1)',
        )
        parser.add_argument(
            '--test-only',
            action='store_true',
            help='Chỉ test không tạo dự đoán thực tế',
        )
    
    def handle(self, *args, **options):
        # Chuẩn bị tham số
        self.setup_parameters(options)
        
        # Lấy các phương pháp cần chạy
        methods = self.get_methods(options.get('method_id'))
        
        if not methods:
            self.stdout.write(
                self.style.WARNING('⚠️  Không tìm thấy phương pháp nào để chạy')
            )
            return
        
        total_predictions = 0
        
        # Chạy cho từng ngày trong khoảng thời gian
        for day_offset in range(options['days']):
            current_analysis_date = self.analysis_date - timedelta(days=day_offset)
            current_prediction_date = self.prediction_date - timedelta(days=day_offset)
            
            self.stdout.write(
                self.style.SUCCESS(
                    f'\n🚀 Bắt đầu chạy {len(methods)} phương pháp cho ngày phân tích {current_analysis_date} '
                    f'(dự đoán cho ngày {current_prediction_date})'
                )
            )
            
            for method in methods:
                try:
                    self.stdout.write(f'\n📊 Đang chạy: {method.ten_phuong_phap}')
                    
                    if options['test_only']:
                        # Chỉ test
                        result = method_executor.execute_method(method, current_analysis_date)
                        if result:
                            self.stdout.write(f'   ✅ Test thành công: {result["data"]}')
                        else:
                            self.stdout.write(f'   ❌ Test thất bại')
                    else:
                        # Tạo dự đoán thực tế
                        predictions = method_executor.create_predictions_from_method(
                            method, current_analysis_date, current_prediction_date, self.user
                        )
                        
                        if predictions:
                            self.stdout.write(
                                f'   ✅ Tạo thành công {len(predictions)} dự đoán'
                            )
                            for pred in predictions:
                                self.stdout.write(f'      - {pred.so_du_doan} ({pred.diem_tin_cay}%)')
                            total_predictions += len(predictions)
                        else:
                            self.stdout.write(f'   ⚠️  Không tạo được dự đoán nào')
                            
                except Exception as e:
                    self.stdout.write(
                        self.style.ERROR(f'   ❌ Lỗi khi chạy {method.ten_phuong_phap}: {e}')
                    )
        
        if not options['test_only']:
            self.stdout.write(
                self.style.SUCCESS(
                    f'\n🎉 Hoàn thành! Tổng cộng đã tạo {total_predictions} dự đoán '
                    f'cho {options["days"]} ngày'
                )
            )
    
    def setup_parameters(self, options):
        """Chuẩn bị các tham số cần thiết"""
        # Ngày phân tích (mặc định là hôm qua)
        if options['analysis_date']:
            self.analysis_date = datetime.strptime(options['analysis_date'], '%Y-%m-%d').date()
        else:
            self.analysis_date = datetime.now().date() - timedelta(days=1)
        
        # Ngày dự đoán (mặc định là hôm nay)
        if options['prediction_date']:
            self.prediction_date = datetime.strptime(options['prediction_date'], '%Y-%m-%d').date()
        else:
            self.prediction_date = datetime.now().date()
        
        # User
        try:
            self.user = User.objects.get(id=options['user_id'])
        except User.DoesNotExist:
            raise CommandError(f'❌ Không tìm thấy user với ID {options["user_id"]}')
    
    def get_methods(self, method_id=None):
        """Lấy danh sách phương pháp cần chạy"""
        if method_id:
            try:
                return [PhuongPhapTinhToan.objects.get(id=method_id)]
            except PhuongPhapTinhToan.DoesNotExist:
                raise CommandError(f'❌ Không tìm thấy phương pháp với ID {method_id}')
        else:
            # Lấy tất cả phương pháp auto-generated và đang hoạt động
            return PhuongPhapTinhToan.objects.filter(
                tham_so_config__auto_generated=True,
                trang_thai__in=['active', 'testing']
            )