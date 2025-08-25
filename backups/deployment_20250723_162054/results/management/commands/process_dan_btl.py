from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone
from datetime import datetime, timedelta
import logging

from results.models import DanBtl, KetQuaXoSo

# Thiết lập logging
logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Tạo dữ liệu Dàn Bạch Thủ Lô cho một hoặc nhiều ngày'

    def add_arguments(self, parser):
        # Thêm các đối số cho command
        parser.add_argument(
            '--date',
            type=str,
            help='Ngày phân tích cụ thể (format: YYYY-MM-DD)',
        )
        
        parser.add_argument(
            '--start-date',
            type=str,
            help='Ngày bắt đầu phân tích (format: YYYY-MM-DD)',
        )
        
        parser.add_argument(
            '--end-date',
            type=str,
            help='Ngày kết thúc phân tích (format: YYYY-MM-DD)',
        )
        
        parser.add_argument(
            '--days',
            type=int,
            help='Số ngày trong quá khứ cần phân tích (tính từ hôm nay)',
        )
        
        parser.add_argument(
            '--force',
            action='store_true',
            help='Buộc tạo lại dữ liệu ngay cả khi đã tồn tại',
        )

    def handle(self, *args, **options):
        # Lấy các tham số từ command line
        date_str = options['date']
        start_date_str = options['start_date']
        end_date_str = options['end_date']
        days = options['days']
        force = options['force']
        
        # Xác định ngày cần phân tích
        dates_to_process = []
        
        if date_str:
            # Nếu có tham số date, chỉ xử lý ngày cụ thể
            try:
                specific_date = datetime.strptime(date_str, '%Y-%m-%d').date()
                dates_to_process.append(specific_date)
                self.stdout.write(f"Đang xử lý cho ngày: {specific_date}")
            except ValueError:
                raise CommandError(f"Định dạng ngày không hợp lệ: {date_str}. Vui lòng sử dụng định dạng YYYY-MM-DD")
        
        elif start_date_str and end_date_str:
            # Nếu có cả start-date và end-date, xử lý khoảng ngày
            try:
                start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
                end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()
                
                if start_date > end_date:
                    raise CommandError("Ngày bắt đầu không thể sau ngày kết thúc")
                
                current_date = start_date
                while current_date <= end_date:
                    dates_to_process.append(current_date)
                    current_date += timedelta(days=1)
                
                self.stdout.write(f"Đang xử lý từ ngày {start_date} đến ngày {end_date}")
            except ValueError:
                raise CommandError("Định dạng ngày không hợp lệ. Vui lòng sử dụng định dạng YYYY-MM-DD")
        
        elif days:
            # Nếu có tham số days, xử lý n ngày gần đây
            if days <= 0:
                raise CommandError("Số ngày phải là số dương")
            
            end_date = timezone.now().date()
            start_date = end_date - timedelta(days=days-1)
            
            current_date = start_date
            while current_date <= end_date:
                dates_to_process.append(current_date)
                current_date += timedelta(days=1)
            
            self.stdout.write(f"Đang xử lý {days} ngày gần đây (từ {start_date} đến {end_date})")
        
        else:
            # Nếu không có tham số nào, xử lý ngày hôm nay
            today = timezone.now().date()
            dates_to_process.append(today)
            self.stdout.write(f"Không có tham số ngày, mặc định xử lý cho ngày hôm nay: {today}")
        
        # Kiểm tra trước nếu có kết quả xổ số cho các ngày cần xử lý
        valid_dates = []
        for date in dates_to_process:
            try:
                KetQuaXoSo.objects.get(ngay=date)
                valid_dates.append(date)
            except KetQuaXoSo.DoesNotExist:
                self.stdout.write(self.style.WARNING(f"Không có kết quả xổ số cho ngày {date}, bỏ qua"))
        
        # Tạo DanBtl cho mỗi ngày hợp lệ
        success_count = 0
        error_count = 0
        
        for date in valid_dates:
            # Kiểm tra xem dữ liệu đã tồn tại chưa
            existing = DanBtl.objects.filter(analysis_date=date).exists()
            
            if existing and not force:
                self.stdout.write(self.style.SUCCESS(f"Đã có dữ liệu cho ngày {date}, bỏ qua (sử dụng --force để tạo lại)"))
                continue
            
            try:
                self.stdout.write(f"Đang tạo dữ liệu DanBtl cho ngày {date}...")
                dan_btl = DanBtl.create_for_date(date)
                
                if dan_btl:
                    success_count += 1
                    self.stdout.write(self.style.SUCCESS(f"✓ Tạo thành công dữ liệu cho ngày {date}"))
                else:
                    error_count += 1
                    self.stdout.write(self.style.ERROR(f"✗ Không thể tạo dữ liệu cho ngày {date}"))
            except Exception as e:
                error_count += 1
                self.stdout.write(self.style.ERROR(f"✗ Lỗi khi xử lý ngày {date}: {str(e)}"))
                logger.error(f"Lỗi khi tạo DanBtl cho ngày {date}", exc_info=True)
        
        # Hiển thị thống kê
        self.stdout.write("\nThống kê:")
        self.stdout.write(f"- Tổng số ngày xử lý: {len(valid_dates)}")
        self.stdout.write(f"- Thành công: {success_count}")
        self.stdout.write(f"- Lỗi: {error_count}")
        
        if success_count > 0:
            self.stdout.write(self.style.SUCCESS("\nHoàn thành việc tạo dữ liệu DanBtl!"))
        else:
            self.stdout.write(self.style.WARNING("\nKhông có dữ liệu nào được tạo thành công!"))