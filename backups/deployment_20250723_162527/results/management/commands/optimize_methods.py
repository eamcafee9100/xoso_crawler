from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import datetime, timedelta
import logging
import time

from results.models import DanDeDacBietAllPrize, OptimalMethodEnsemble
from results.optimizers import MethodOptimizerService

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Tối ưu hóa tập hợp phương pháp dự đoán cho một hoặc nhiều ngày'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--date',
            type=str,
            help='Ngày cụ thể cần tối ưu hóa (YYYY-MM-DD)',
        )
        
        parser.add_argument(
            '--days',
            type=int,
            default=7,
            help='Số ngày gần đây cần tối ưu hóa (mặc định: 7)',
        )
        
        parser.add_argument(
            '--force',
            action='store_true',
            help='Buộc tính toán lại ngay cả khi đã có kết quả',
        )
        
        parser.add_argument(
            '--max-methods',
            type=int,
            default=5,
            help='Số lượng phương pháp tối đa trong tập hợp tối ưu (mặc định: 5)',
        )
    
    def handle(self, *args, **options):
        date_str = options['date']
        days = options['days']
        force = options['force']
        max_methods = options['max_methods']
        
        dates_to_process = []
        
        if date_str:
            # Xử lý một ngày cụ thể
            try:
                specific_date = datetime.strptime(date_str, '%Y-%m-%d').date()
                dates_to_process.append(specific_date)
            except ValueError:
                self.stderr.write(self.style.ERROR(f"Định dạng ngày không hợp lệ: {date_str}. Sử dụng định dạng YYYY-MM-DD"))
                return
        else:
            # Xử lý n ngày gần nhất
            end_date = timezone.now().date()
            for i in range(days):
                date = end_date - timedelta(days=i)
                dates_to_process.append(date)
        
        # Thống kê
        total_count = len(dates_to_process)
        success_count = 0
        error_count = 0
        skipped_count = 0
        
        self.stdout.write(f"Chuẩn bị tối ưu hóa cho {total_count} ngày")
        
        for date in dates_to_process:
            # Kiểm tra xem có dữ liệu DanDeDacBietAllPrize cho ngày này không
            if not DanDeDacBietAllPrize.objects.filter(analysis_date=date).exists():
                self.stdout.write(self.style.WARNING(f"Không có dữ liệu DanDeDacBietAllPrize cho ngày {date}, bỏ qua"))
                skipped_count += 1
                continue
            
            # Kiểm tra xem đã có kết quả tối ưu hóa chưa
            existing = OptimalMethodEnsemble.objects.filter(analysis_date=date).first()
            if existing and not force:
                self.stdout.write(self.style.WARNING(f"Đã có kết quả tối ưu hóa cho ngày {date}, bỏ qua (sử dụng --force để tính lại)"))
                skipped_count += 1
                continue
            
            # Thực hiện tối ưu hóa
            self.stdout.write(f"Đang tối ưu hóa phương pháp cho ngày {date}...")
            start_time = time.time()
            
            optimizer = MethodOptimizerService(date)
            result = optimizer.optimize_methods(max_methods=max_methods)
            
            elapsed = time.time() - start_time
            
            if result:
                success_count += 1
                self.stdout.write(self.style.SUCCESS(f"✓ Tối ưu hóa thành công cho ngày {date} trong {elapsed:.2f}s"))
            else:
                error_count += 1
                self.stdout.write(self.style.ERROR(f"✗ Không thể tối ưu hóa cho ngày {date}"))
        
        # Hiển thị thống kê
        self.stdout.write("\n--- Thống kê ---")
        self.stdout.write(f"Tổng số ngày: {total_count}")
        self.stdout.write(f"Thành công: {success_count}")
        self.stdout.write(f"Lỗi: {error_count}")
        self.stdout.write(f"Bỏ qua: {skipped_count}")
        
        if success_count > 0:
            self.stdout.write(self.style.SUCCESS("\nTối ưu hóa phương pháp hoàn tất!"))
        else:
            self.stdout.write(self.style.WARNING("\nKhông có ngày nào được tối ưu hóa thành công!"))