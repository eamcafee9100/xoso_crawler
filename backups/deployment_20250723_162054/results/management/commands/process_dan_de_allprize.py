# results/management/commands/process_dan_de.py
from django.core.management.base import BaseCommand
from results.models import DanDeDacBietAllPrize, KetQuaXoSo,PredictionDeAllPrizeResult
from datetime import date, timedelta
import logging
import time
from django.db import transaction

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    """
    Command để tạo dàn đề đặc biệt cho các ngày trong quá khứ
    
    Sử dụng:
        python manage.py process_dan_de --days=500
        python manage.py process_dan_de --start=2023-01-01 --end=2023-12-31
        python manage.py process_dan_de --date=2023-05-15
    """
    help = 'Xử lý dàn đề đặc biệt cho các ngày trong quá khứ'
    
    def add_arguments(self, parser):
        # Nhóm tham số 1: Số ngày trong quá khứ
        parser.add_argument(
            '--days',
            type=int,
            default=None,
            help='Số ngày trong quá khứ cần xử lý (mặc định: 30)'
        )
        
        # Nhóm tham số 2: Khoảng thời gian cụ thể
        parser.add_argument(
            '--start',
            type=str,
            help='Ngày bắt đầu (định dạng YYYY-MM-DD)'
        )
        
        parser.add_argument(
            '--end',
            type=str,
            help='Ngày kết thúc (định dạng YYYY-MM-DD, mặc định là ngày hiện tại)'
        )
        
        parser.add_argument(
        '--clean-all',
        action='store_true',
        help='Xóa tất cả dữ liệu dự đoán trước khi chạy lại'
    )
        # Nhóm tham số 3: Ngày cụ thể
        parser.add_argument(
            '--date',
            type=str,
            help='Ngày cụ thể cần xử lý (định dạng YYYY-MM-DD)'
        )
        
        # Tham số bổ sung
        parser.add_argument(
            '--force',
            action='store_true',
            help='Bắt buộc tạo lại ngay cả khi dàn đề đã tồn tại'
        )
        
        parser.add_argument(
            '--batch-size',
            type=int,
            default=10,
            help='Số lượng ngày xử lý trong một lần (mặc định: 10)'
        )
    
    def handle(self, *args, **options):
        from results.models import DanDeDacBietAllPrize, KetQuaXoSo, PredictionDeAllPrizeResult
        start_time = time.time()
        # Xóa dữ liệu nếu cần
        if options['clean_all']:
            from results.models import DanDeDacBietAllPrize, PredictionDeAllPrizeResult
            
            self.stdout.write(self.style.WARNING("Xóa tất cả dữ liệu dự đoán cũ..."))
            
            # Lấy ID của tất cả DanDeDacBietAllPrize trước khi xóa
            dan_de_ids = list(DanDeDacBietAllPrize.objects.values_list('id', flat=True))
            
            # Xóa tất cả PredictionDeAllPrizeResult
            prediction_count = PredictionDeAllPrizeResult.objects.filter(dan_de_id__in=dan_de_ids).count()
            PredictionDeAllPrizeResult.objects.filter(dan_de_id__in=dan_de_ids).delete()
            
            # Xóa tất cả DanDeDacBietAllPrize
            dande_count = DanDeDacBietAllPrize.objects.count()
            DanDeDacBietAllPrize.objects.all().delete()
            
            self.stdout.write(self.style.SUCCESS(f"Đã xóa {dande_count} bản ghi DanDeDacBietAllPrize và {prediction_count} bản ghi PredictionDeAllPrizeResult"))

        # Xác định khoảng thời gian cần xử lý
        if options['date']:
            try:
                single_date = date.fromisoformat(options['date'])
                start_date = single_date
                end_date = single_date
                self.stdout.write(f"Xử lý dàn đề cho ngày cụ thể: {single_date}")
            except ValueError:
                self.stderr.write(self.style.ERROR(f"Định dạng ngày không hợp lệ: {options['date']} (sử dụng định dạng YYYY-MM-DD)"))
                return
        elif options['start']:
            try:
                start_date = date.fromisoformat(options['start'])
                end_date = date.today()
                if options['end']:
                    try:
                        end_date = date.fromisoformat(options['end'])
                    except ValueError:
                        self.stderr.write(self.style.ERROR(f"Định dạng ngày kết thúc không hợp lệ: {options['end']} (sử dụng định dạng YYYY-MM-DD)"))
                        return
                self.stdout.write(f"Xử lý dàn đề từ {start_date} đến {end_date}")
            except ValueError:
                self.stderr.write(self.style.ERROR(f"Định dạng ngày bắt đầu không hợp lệ: {options['start']} (sử dụng định dạng YYYY-MM-DD)"))
                return
        elif options['days'] is not None:
            days = options['days']
            end_date = date.today()
            start_date = end_date - timedelta(days=days)
            self.stdout.write(f"Xử lý dàn đề cho {days} ngày gần đây (từ {start_date} đến {end_date})")
        else:
            # Mặc định xử lý 30 ngày gần đây
            days = 30
            end_date = date.today()
            start_date = end_date - timedelta(days=days)
            self.stdout.write(f"Xử lý dàn đề cho 30 ngày gần đây (từ {start_date} đến {end_date})")
        
        force = options['force']
        batch_size = options['batch_size']
        
        processed = 0
        skipped = 0
        errors = 0
        
        # Hiển thị thông tin về kết quả xổ số đã có
        total_days = (end_date - start_date).days + 1
        xoso_days = KetQuaXoSo.objects.filter(ngay__gte=start_date, ngay__lte=end_date).count()
        dande_days = DanDeDacBietAllPrize.objects.filter(analysis_date__gte=start_date, analysis_date__lte=end_date).count()
        
        self.stdout.write(f"Tổng số ngày cần xử lý: {total_days}")
        self.stdout.write(f"Số ngày có kết quả xổ số: {xoso_days}")
        self.stdout.write(f"Số ngày đã có dàn đề: {dande_days}")
        
        if force:
            self.stdout.write(self.style.WARNING("Chế độ FORCE được bật: Sẽ tạo lại tất cả dàn đề"))
        
        # Chuẩn bị danh sách các ngày cần xử lý
        dates_to_process = []
        current_date = start_date
        while current_date <= end_date:
            dates_to_process.append(current_date)
            current_date += timedelta(days=1)
        
        # Xử lý theo batch
        for i in range(0, len(dates_to_process), batch_size):
            batch = dates_to_process[i:i+batch_size]
            self.stdout.write(f"Đang xử lý batch {i//batch_size + 1}/{(len(dates_to_process)-1)//batch_size + 1}...")
            
            for current_date in batch:
                try:
                    # Kiểm tra xem có kết quả xổ số cho ngày hiện tại không
                    if KetQuaXoSo.objects.filter(ngay=current_date).exists():
                        # Kiểm tra xem dàn đề đã tồn tại chưa
                        dande_exists = DanDeDacBietAllPrize.objects.filter(analysis_date=current_date).exists()
                        
                        if not dande_exists or force:
                            self.stdout.write(f"Đang xử lý ngày {current_date}...")
                            # Sử dụng atomic cho mỗi ngày riêng biệt
                            with transaction.atomic():
                                result = DanDeDacBietAllPrize.create_for_date_allprize(current_date)
                                
                                if result:
                                    action = "Đã tạo" if not dande_exists else "Đã tạo lại"
                                    self.stdout.write(f"{action} dàn đề cho ngày {current_date}")
                                    processed += 1
                                else:
                                    self.stdout.write(self.style.ERROR(f"Lỗi khi tạo dàn đề cho ngày {current_date}"))
                                    errors += 1
                        else:
                            self.stdout.write(f"Bỏ qua: Dàn đề cho ngày {current_date} đã tồn tại")
                            skipped += 1
                    else:
                        self.stdout.write(f"Bỏ qua: Không có kết quả xổ số cho ngày {current_date}")
                        skipped += 1
                        
                except Exception as e:
                    self.stderr.write(self.style.ERROR(f"Lỗi khi xử lý ngày {current_date}: {str(e)}"))
                    logger.exception(f"Lỗi khi xử lý ngày {current_date}")
                    errors += 1
        
        # Tính toán thời gian thực thi
        execution_time = time.time() - start_time
        minutes, seconds = divmod(execution_time, 60)
        hours, minutes = divmod(minutes, 60)
        
        # Hiển thị thống kê kết quả
        self.stdout.write(self.style.SUCCESS(f"""
        ========== HOÀN THÀNH ==========
        Thời gian thực thi: {int(hours)}h {int(minutes)}m {seconds:.2f}s
        Đã xử lý thành công: {processed} ngày
        Đã bỏ qua: {skipped} ngày
        Lỗi: {errors} ngày
        ==================================
        """))