from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone
from datetime import datetime, timedelta
import logging
from chamde.models import ChamAnalysis, ChamDau, ChamDuoi, QuaTramPattern, NumberStatistics, NumberFrequencyTimeSeriesStats
from results.models import KetQuaXoSo
from chamde.ChamAnalyzer import ChamAnalyzer

# Thiết lập logging
logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Cập nhật phân tích chạm tự động'
    
    def add_arguments(self, parser):
        # Thêm các tham số cho command
        parser.add_argument(
            '--start-date',
            type=str,
            help='Ngày bắt đầu phân tích (YYYY-MM-DD)',
        )
        
        parser.add_argument(
            '--end-date', 
            type=str,
            help='Ngày kết thúc phân tích (YYYY-MM-DD)',
        )
        
        parser.add_argument(
            '--days',
            type=int,
            default=90,
            help='Số ngày phân tích từ hôm nay trở về trước (mặc định: 90)',
        )
        
        parser.add_argument(
            '--force-update',
            action='store_true',
            help='Buộc cập nhật lại dữ liệu đã tồn tại',
        )
        
        parser.add_argument(
            '--analyze-only',
            choices=['cham_dau', 'cham_duoi', 'cau_cham', 'qua_tram', 'statistics'],
            help='Chỉ phân tích một loại dữ liệu cụ thể',
        )
        
        parser.add_argument(
            '--verbose',
            action='store_true',
            help='Hiển thị thông tin chi tiết',
        )
        
        parser.add_argument(
            '--clean',
            action='store_true',
            help='Xóa dữ liệu cũ trước khi phân tích',
        )
    
    def handle(self, *args, **options):
        """
        Xử lý chính của command
        """
        try:
            # Thiết lập logging level
            if options['verbose']:
                logging.basicConfig(level=logging.INFO)
            
            # Xác định khoảng thời gian phân tích
            start_date, end_date = self._get_date_range(options)
            
            self.stdout.write(
                self.style.SUCCESS(
                    f'Bắt đầu phân tích dữ liệu chạm từ {start_date} đến {end_date}'
                )
            )
            
            # Xóa dữ liệu cũ nếu được yêu cầu
            if options['clean']:
                self._clean_old_data(start_date, end_date)
            
            # Khởi tạo analyzer
            analyzer = ChamAnalyzer(start_date=start_date, end_date=end_date)
            
            # Thực hiện phân tích
            if options['analyze_only']:
                self._analyze_specific(analyzer, options['analyze_only'], options)
            else:
                self._analyze_all(analyzer, options)
            
            self.stdout.write(
                self.style.SUCCESS('Hoàn thành phân tích dữ liệu chạm!')
            )
            
        except Exception as e:
            logger.error(f"Lỗi khi thực hiện phân tích: {str(e)}")
            raise CommandError(f'Lỗi khi thực hiện phân tích: {str(e)}')
    
    def _get_date_range(self, options):
        """
        Xác định khoảng thời gian phân tích
        """
        if options['start_date'] and options['end_date']:
            try:
                start_date = datetime.strptime(options['start_date'], '%Y-%m-%d').date()
                end_date = datetime.strptime(options['end_date'], '%Y-%m-%d').date()
            except ValueError:
                raise CommandError('Định dạng ngày không hợp lệ. Sử dụng YYYY-MM-DD')
        else:
            end_date = timezone.now().date()
            start_date = end_date - timedelta(days=options['days'])
        
        if start_date > end_date:
            raise CommandError('Ngày bắt đầu không thể lớn hơn ngày kết thúc')
        
        return start_date, end_date
    
    def _clean_old_data(self, start_date, end_date):
        """
        Xóa dữ liệu cũ trong khoảng thời gian
        """
        self.stdout.write('Đang xóa dữ liệu cũ...')
        
        # Xóa dữ liệu phân tích chạm
        ChamAnalysis.objects.filter(
            ngay__gte=start_date,
            ngay__lte=end_date
        ).delete()
        
        # Xóa dữ liệu chạm đầu
        ChamDau.objects.filter(
            ngay__gte=start_date,
            ngay__lte=end_date
        ).delete()
        
        # Xóa dữ liệu chạm đuôi
        ChamDuoi.objects.filter(
            ngay__gte=start_date,
            ngay__lte=end_date
        ).delete()
        
        # Xóa dữ liệu mẫu quả trám
        QuaTramPattern.objects.filter(
            ngay__gte=start_date,
            ngay__lte=end_date
        ).delete()
        
        # Xóa dữ liệu thống kê chuỗi thời gian
        NumberFrequencyTimeSeriesStats.objects.filter(
            period_start__gte=start_date,
            period_end__lte=end_date
        ).delete()
        
        self.stdout.write(self.style.SUCCESS('Đã xóa dữ liệu cũ'))
    
    def _analyze_all(self, analyzer, options):
        """
        Phân tích tất cả các loại dữ liệu
        """
        # Lấy tất cả kết quả xổ số trong khoảng thời gian
        ket_qua_list = KetQuaXoSo.objects.filter(
            ngay__gte=analyzer.start_date,
            ngay__lte=analyzer.end_date
        ).order_by('ngay')
        
        total_results = ket_qua_list.count()
        
        if total_results == 0:
            self.stdout.write(
                self.style.WARNING(
                    f'Không tìm thấy kết quả xổ số nào trong khoảng {analyzer.start_date} - {analyzer.end_date}'
                )
            )
            return
        
        self.stdout.write(f'Tìm thấy {total_results} kết quả xổ số để phân tích')
        
        # Phân tích từng ngày
        processed = 0
        for ket_qua in ket_qua_list:
            try:
                
                self._analyze_single_day(analyzer, ket_qua, options)
                processed += 1
                
                if options['verbose'] and processed % 10 == 0:
                    self.stdout.write(f'Đã xử lý {processed}/{total_results} kết quả')
                    
            except Exception as e:
                logger.error(f"Lỗi khi phân tích ngày {ket_qua.ngay}: {str(e)}")
                self.stdout.write(
                    self.style.ERROR(f'Lỗi khi phân tích ngày {ket_qua.ngay}: {str(e)}')
                )
        
        # Tạo báo cáo thống kê
        self._generate_and_display_stats(analyzer)
        
        self.stdout.write(
            self.style.SUCCESS(f'Đã phân tích thành công {processed}/{total_results} kết quả')
        )
    
    def _analyze_specific(self, analyzer, analyze_type, options):
        """
        Phân tích một loại dữ liệu cụ thể
        """
        ket_qua_list = KetQuaXoSo.objects.filter(
            ngay__gte=analyzer.start_date,
            ngay__lte=analyzer.end_date
        ).order_by('ngay')
        
        total_results = ket_qua_list.count()
        
        if total_results == 0:
            self.stdout.write(
                self.style.WARNING('Không tìm thấy kết quả xổ số nào để phân tích')
            )
            return
        
        self.stdout.write(f'Bắt đầu phân tích {analyze_type} cho {total_results} kết quả')
        
        processed = 0
        for ket_qua in ket_qua_list:
            try:
                if analyze_type == 'cham_dau':
                    self._analyze_cham_dau(ket_qua, options)
                elif analyze_type == 'cham_duoi':
                    self._analyze_cham_duoi(ket_qua, options)
                elif analyze_type == 'cau_cham':
                    self._analyze_cau_cham(ket_qua, options)
                elif analyze_type == 'qua_tram':
                    self._analyze_qua_tram(ket_qua, options)
                elif analyze_type == 'statistics':
                    analyzer.update_number_statistics(ket_qua)
                
                processed += 1
                
                if options['verbose'] and processed % 10 == 0:
                    self.stdout.write(f'Đã xử lý {processed}/{total_results} kết quả')
                    
            except Exception as e:
                logger.error(f"Lỗi khi phân tích {analyze_type} cho ngày {ket_qua.ngay}: {str(e)}")
        
        self.stdout.write(
            self.style.SUCCESS(f'Đã phân tích {analyze_type} thành công cho {processed}/{total_results} kết quả')
        )
    def _analyze_single_day_debug(self, analyzer, ket_qua, options):
        """
        Phân tích dữ liệu cho một ngày cụ thể
        """
        try:
            print(f"Phân tích ngày trong khối try{ket_qua.ngay} - {ket_qua.giai_db}")
            # Lấy hoặc tạo mới ChamAnalysis
            analysis, created = ChamAnalysis.objects.get_or_create(
                ngay=ket_qua.ngay,
                defaults={'ket_qua': ket_qua}
            )
            print(f"Phân tích ngày trong try {ket_qua.ngay} - {ket_qua.giai_db}")
            # Cập nhật thông tin cơ bản
            analysis.ket_qua = ket_qua
            print(f"Phân tích ngày {ket_qua.ngay} - {'Tạo mới' if created else 'Cập nhật'}")
            # Xử lý giải đặc biệt
            giai_db = ket_qua.giai_db
            print(f"Phân tích giải đặc biệt: {giai_db}")
            if giai_db and len(giai_db) > 0:
                analysis.db_full = giai_db
                analysis.db_cham_dau = giai_db[0] if len(giai_db) > 0 else '0'
                analysis.db_cham_duoi = giai_db[-1] if len(giai_db) > 0 else '0'
                
                # 2 số cuối
                analysis.db_last2 = giai_db[-2:] if len(giai_db) >= 2 else giai_db.zfill(2)
                
                # Từng chữ số (đảm bảo có đủ 6 chữ số)
                giai_db_padded = giai_db.zfill(6)
                analysis.db_digit1 = giai_db_padded[0] if len(giai_db_padded) > 0 else '0'
                analysis.db_digit2 = giai_db_padded[1] if len(giai_db_padded) > 1 else '0'
                analysis.db_digit3 = giai_db_padded[2] if len(giai_db_padded) > 2 else '0'
                analysis.db_digit4 = giai_db_padded[3] if len(giai_db_padded) > 3 else '0'
                analysis.db_digit5 = giai_db_padded[4] if len(giai_db_padded) > 4 else '0'
                analysis.db_digit6 = giai_db_padded[5] if len(giai_db_padded) > 5 else '0'
                
                # Tính tổng
                analysis.db_total = sum(int(digit) for digit in giai_db if digit.isdigit())
                analysis.db_last2_total = sum(int(digit) for digit in analysis.db_last2 if digit.isdigit())
            else:
                # Nếu không có giải đặc biệt, set giá trị mặc định
                analysis.db_full = ''
                analysis.db_cham_dau = '0'
                analysis.db_cham_duoi = '0'
                analysis.db_last2 = '00'
                analysis.db_digit1 = '0'
                analysis.db_digit2 = '0'
                analysis.db_digit3 = '0'
                analysis.db_digit4 = '0'
                analysis.db_digit5 = '0'
                analysis.db_digit6 = '0'
                analysis.db_total = 0
                analysis.db_last2_total = 0
            
            # Xử lý giải nhất
            giai_nhat = ket_qua.giai_1
            if giai_nhat and len(giai_nhat) >= 5:
                analysis.giai_nhat_full = giai_nhat
                analysis.giai_nhat_mid_digit = giai_nhat[2]  # Chữ số giữa (vị trí thứ 3)
            else:
                analysis.giai_nhat_full = giai_nhat or ''
                analysis.giai_nhat_mid_digit = '0'
            
            # Thông tin ngày tháng
            analysis.day_of_week = ket_qua.ngay.weekday()
            analysis.month = ket_qua.ngay.month
            analysis.week_number = ket_qua.ngay.isocalendar()[1]
            
            # XỬ LÝ CÁC TRƯỜNG BOOLEAN - QUAN TRỌNG!
            # Reset tất cả về False trước
            analysis.is_sunday = False
            analysis.is_monday = False
            analysis.is_tuesday = False
            analysis.is_wednesday = False
            analysis.is_thursday = False
            analysis.is_friday = False
            analysis.is_saturday = False
            
            # Set đúng ngày trong tuần
            weekday = ket_qua.ngay.weekday()  # 0=Monday, 6=Sunday
            if weekday == 0:
                analysis.is_monday = True
            elif weekday == 1:
                analysis.is_tuesday = True
            elif weekday == 2:
                analysis.is_wednesday = True
            elif weekday == 3:
                analysis.is_thursday = True
            elif weekday == 4:
                analysis.is_friday = True
            elif weekday == 5:
                analysis.is_saturday = True
            elif weekday == 6:
                analysis.is_sunday = True
            
            # XỬ LÝ CÁC TRƯỜNG CHẠM ĐẦU/ĐUÔI - QUAN TRỌNG!
            # Reset tất cả về False
            for i in range(10):
                setattr(analysis, f'cham_dau_{i}', False)
                setattr(analysis, f'cham_duoi_{i}', False)
            
            # Set đúng giá trị chạm đầu
            if analysis.db_cham_dau and analysis.db_cham_dau.isdigit():
                cham_dau_digit = int(analysis.db_cham_dau)
                setattr(analysis, f'cham_dau_{cham_dau_digit}', True)
            
            # Set đúng giá trị chạm đuôi
            if analysis.db_cham_duoi and analysis.db_cham_duoi.isdigit():
                cham_duoi_digit = int(analysis.db_cham_duoi)
                setattr(analysis, f'cham_duoi_{cham_duoi_digit}', True)
            
            # Xử lý cầu chạm (nếu cần)
            analysis.cau_cham1_value = self._calculate_cau_cham1(analysis)
            analysis.cau_cham2_value = self._calculate_cau_cham2(analysis)
            
            # Lưu vào database
            analysis.save()
            
            if options.get('verbose'):
                self.stdout.write(f'✓ Đã phân tích ngày {ket_qua.ngay}')
                
        except Exception as e:
            # Log chi tiết để debug
            logger.error(f"Chi tiết lỗi khi phân tích ngày {ket_qua.ngay}:")
            logger.error(f"- Giải đặc biệt: {getattr(ket_qua, 'giai_dac_biet', 'N/A')}")
            logger.error(f"- Giải nhất: {getattr(ket_qua, 'giai_nhat', 'N/A')}")
            logger.error(f"- Lỗi: {str(e)}")
            raise e

    def _calculate_cau_cham1(self, analysis):
        """Tính toán cầu chạm kiểu 1"""
        try:
            if analysis.is_sunday and analysis.giai_nhat_mid_digit:
                return analysis.giai_nhat_mid_digit
            return None
        except:
            return None

    def _calculate_cau_cham2(self, analysis):
        """Tính toán cầu chạm kiểu 2"""
        try:
            # Logic tính cầu chạm kiểu 2
            # Ví dụ: tổng đề CN + đuôi đề thứ 6
            if analysis.is_sunday:
                return analysis.db_last2
            return None
        except:
            return None

    def _validate_boolean_field(self, value, field_name):
        """Validate giá trị cho BooleanField"""
        if value is None or value == '':
            return False
        elif isinstance(value, bool):
            return value
        elif isinstance(value, str):
            if value.lower() in ['true', '1', 'yes']:
                return True
            elif value.lower() in ['false', '0', 'no']:
                return False
            else:
                logger.warning(f"Giá trị không hợp lệ cho {field_name}: {value}")
                return False
        else:
            logger.warning(f"Kiểu dữ liệu không hợp lệ cho {field_name}: {type(value)}")
            return False

    def _validate_char_field(self, value, max_length=1):
        """Validate giá trị cho CharField"""
        if value is None:
            return '0'
        elif isinstance(value, str):
            return value[:max_length] if len(value) > max_length else value
        else:
            return str(value)[:max_length]
    
    def _analyze_cham_dau(self, ket_qua, options):
        """
        Phân tích riêng chạm đầu
        """
        force_update = options.get('force_update', False)
        
        if force_update:
            ChamDau.objects.filter(ngay=ket_qua.ngay).delete()
        
        if hasattr(ChamDau.objects, 'create_for_date'):
            ChamDau.objects.create_for_date(ket_qua.ngay, ket_qua)
    
    def _analyze_cham_duoi(self, ket_qua, options):
        """
        Phân tích riêng chạm đuôi
        """
        force_update = options.get('force_update', False)
        
        if force_update:
            ChamDuoi.objects.filter(ngay=ket_qua.ngay).delete()
        
        if hasattr(ChamDuoi.objects, 'create_for_date'):
            ChamDuoi.objects.create_for_date(ket_qua.ngay, ket_qua)
    
    def _analyze_cau_cham(self, ket_qua, options):
        """
        Phân tích riêng cầu chạm
        """
        force_update = options.get('force_update', False)
        
        if force_update:
            ChamAnalysis.objects.filter(ngay=ket_qua.ngay).delete()
        
        if hasattr(ChamAnalysis.objects, 'create_from_ketqua'):
            ChamAnalysis.objects.create_from_ketqua(ket_qua)
    
    def _analyze_qua_tram(self, ket_qua, options):
        """
        Phân tích riêng mẫu quả trám
        """
        force_update = options.get('force_update', False)
        
        if force_update:
            QuaTramPattern.objects.filter(ngay=ket_qua.ngay).delete()
        
        if hasattr(QuaTramPattern.objects, 'find_patterns'):
            QuaTramPattern.objects.find_patterns(ket_qua)
    
    def _generate_and_display_stats(self, analyzer):
        """
        Tạo và hiển thị báo cáo thống kê
        """
        try:
            self.stdout.write('Đang tạo báo cáo thống kê...')
            stats = analyzer.generate_statistics()
            
            # Hiển thị thống kê tổng quan
            period = stats['period']
            self.stdout.write(
                self.style.SUCCESS(
                    f"\n=== BÁO CÁO THỐNG KÊ ===\n"
                    f"Khoảng thời gian: {period['start_date']} - {period['end_date']}\n"
                    f"Tổng số ngày: {period['total_days']}\n"
                    f"Tổng số kết quả: {period['total_results']}\n"
                )
            )
            
            # Hiển thị thống kê chạm đầu
            self.stdout.write("=== THỐNG KÊ CHẠM ĐẦU ===")
            for cham_value, stat in stats['cham_dau_stats'].items():
                self.stdout.write(
                    f"Chạm đầu {cham_value}: {stat['hits']} lần ({stat['hit_rate']:.2f}%)"
                )
            
            # Hiển thị thống kê chạm đuôi
            self.stdout.write("\n=== THỐNG KÊ CHẠM ĐUÔI ===")
            for cham_value, stat in stats['cham_duoi_stats'].items():
                self.stdout.write(
                    f"Chạm đuôi {cham_value}: {stat['hits']} lần ({stat['hit_rate']:.2f}%)"
                )
            
            # Hiển thị thống kê quả trám
            if stats['qua_tram_stats']:
                self.stdout.write(
                    f"\n=== THỐNG KÊ QUẢ TRÁM ===\n"
                    f"Tỷ lệ trúng trung bình: {stats['qua_tram_hit_rate']:.2f}%"
                )
                
                # Hiển thị top 5 số có tỷ lệ trúng cao nhất
                sorted_qua_tram = sorted(
                    stats['qua_tram_stats'].items(),
                    key=lambda x: x[1]['hit_rate'] if isinstance(x[1], dict) else 0,
                    reverse=True
                )[:5]
                
                for number, stat in sorted_qua_tram:
                    if isinstance(stat, dict):
                        self.stdout.write(
                            f"Số {number}: {stat['hit_rate']:.2f}% ({len(stat['patterns'])} mẫu)"
                        )
            
        except Exception as e:
            logger.error(f"Lỗi khi tạo báo cáo thống kê: {str(e)}")
            self.stdout.write(
                self.style.ERROR(f'Lỗi khi tạo báo cáo thống kê: {str(e)}')
            )
    
    def _get_cham_analysis_defaults(self, ket_qua):
        """
        Lấy giá trị mặc định cho ChamAnalysis
        """
        # Tính toán các giá trị cần thiết từ kết quả xổ số
        db_total = 0
        if hasattr(ket_qua, 'giai_db') and ket_qua.giai_db:
            try:
                db_total = sum(int(digit) for digit in str(ket_qua.giai_db) if digit.isdigit())
            except (ValueError, TypeError):
                db_total = 0
        
        # Xác định ngày trong tuần
        is_sunday = ket_qua.ngay.weekday() == 6
        is_monday = ket_qua.ngay.weekday() == 0
        is_tuesday = ket_qua.ngay.weekday() == 1
        is_wednesday = ket_qua.ngay.weekday() == 2
        is_thursday = ket_qua.ngay.weekday() == 3
        is_friday = ket_qua.ngay.weekday() == 4
        is_saturday = ket_qua.ngay.weekday() == 5
        
        return {
            'ket_qua': ket_qua,
            'db_total': db_total,
            'cham_dau_0': '',
            'cham_dau_1': '',
            'cham_dau_2': '',
            'cham_dau_3': '',
            'cham_dau_4': '',
            'cham_dau_5': '',
            'cham_dau_6': '',
            'cham_dau_7': '',
            'cham_dau_8': '',
            'cham_dau_9': '',
            'cham_duoi_0': '',
            'cham_duoi_1': '',
            'cham_duoi_2': '',
            'cham_duoi_3': '',
            'cham_duoi_4': '',
            'cham_duoi_5': '',
            'cham_duoi_6': '',
            'cham_duoi_7': '',
            'cham_duoi_8': '',
            'cham_duoi_9': '',
            'cau_cham1_value': '',
            'cau_cham2_value': '',
            'is_sunday': is_sunday,
            'is_monday': is_monday,
            'is_tuesday': is_tuesday,
            'is_wednesday': is_wednesday,
            'is_thursday': is_thursday,
            'is_friday': is_friday,
            'is_saturday': is_saturday,
        }
    
    def _manual_create_cham_analysis(self, cham_analysis, ket_qua):
        """
        Tạo dữ liệu phân tích chạm thủ công
        """
        try:
            # Lấy tất cả số 2 chữ số từ kết quả
            all_numbers = []
            if hasattr(ket_qua, 'get_all_2digit_numbers'):
                all_numbers = ket_qua.get_all_2digit_numbers()
            else:
                # Tạo thủ công nếu không có method
                all_numbers = self._extract_2digit_numbers(ket_qua)
            
            # Phân tích chạm đầu (0-9)
            for i in range(10):
                digit = str(i)
                matching_numbers = [num for num in all_numbers if num.startswith(digit)]
                setattr(cham_analysis, f'cham_dau_{i}', ','.join(matching_numbers))
            
            # Phân tích chạm đuôi (0-9)
            for i in range(10):
                digit = str(i)
                matching_numbers = [num for num in all_numbers if num.endswith(digit)]
                setattr(cham_analysis, f'cham_duoi_{i}', ','.join(matching_numbers))
            
            # Tính cầu chạm (chỉ cho chủ nhật)
            if cham_analysis.is_sunday:
                # Logic tính cầu chạm 1 và cầu chạm 2
                cham_analysis.cau_cham1_value = self._calculate_cau_cham1(ket_qua)
                cham_analysis.cau_cham2_value = self._calculate_cau_cham2(ket_qua)
            
            cham_analysis.save()
            
        except Exception as e:
            logger.error(f"Lỗi khi tạo thủ công ChamAnalysis: {str(e)}")
            raise
    
    def _extract_2digit_numbers(self, ket_qua):
        """
        Trích xuất tất cả số 2 chữ số từ kết quả xổ số
        """
        numbers = []
        
        # Lấy từ các trường giải
        fields = ['giai_db', 'giai_nhat', 'giai_nhi', 'giai_ba', 'giai_tu', 
                 'giai_nam', 'giai_sau', 'giai_bay', 'giai_tam']
        
        for field in fields:
            if hasattr(ket_qua, field):
                value = getattr(ket_qua, field)
                if value:
                    # Xử lý giải có nhiều giá trị (phân cách bằng dấu phẩy)
                    if ',' in str(value):
                        for part in str(value).split(','):
                            numbers.extend(self._get_2digit_from_string(part.strip()))
                    else:
                        numbers.extend(self._get_2digit_from_string(str(value)))
        
        # Loại bỏ trùng lặp và sắp xếp
        return sorted(list(set(numbers)))
    
    def _get_2digit_from_string(self, text):
        """
        Lấy tất cả số 2 chữ số từ một chuỗi
        """
        numbers = []
        text = ''.join(c for c in text if c.isdigit())
        
        if len(text) >= 2:
            # Lấy 2 chữ số cuối
            numbers.append(text[-2:])
            
            # Lấy tất cả cặp 2 chữ số liên tiếp
            for i in range(len(text) - 1):
                numbers.append(text[i:i+2])
        
        return list(set(numbers))
    
    def _analyze_single_day(self, analyzer, ket_qua, options):
        """
        Version debug đã sửa lỗi missing fields
        """
        try:
            self.stdout.write(f"🔍 Debug ngày {ket_qua.ngay}:")
            
            # Kiểm tra dữ liệu đầu vào
            self.stdout.write(f"  - Giải đặc biệt: '{ket_qua.giai_db}'")
            self.stdout.write(f"  - Giải nhất: '{ket_qua.giai_1}'")
            
            try:
                analysis = ChamAnalysis.objects.get(ngay=ket_qua.ngay)
                created = False
                print(f"DEBUG - Đã tìm thấy bản ghi existing cho ngày {ket_qua.ngay}")
            except ChamAnalysis.DoesNotExist:
                print(f"DEBUG - Tạo bản ghi mới cho ngày {ket_qua.ngay}")
                # Tạo instance mới và set tất cả giá trị trước khi save
                analysis = ChamAnalysis(ngay=ket_qua.ngay)
                analysis.ket_qua = ket_qua
            
            # Test từng bước
            self.stdout.write("  - Đang set thông tin cơ bản...")
            analysis.ket_qua = ket_qua
            
            # Test giải đặc biệt
            giai_db = ket_qua.giai_db or ''
            self.stdout.write(f"  - Xử lý giải ĐB: '{giai_db}' (length: {len(giai_db)})")
            
            if giai_db:
                analysis.db_full = str(giai_db)
                analysis.db_cham_dau = str(giai_db[0]) if len(giai_db) > 0 else '0'
                analysis.db_cham_duoi = str(giai_db[-1]) if len(giai_db) > 0 else '0'
                
                # THÊM: Tính toán các trường bị thiếu
                # Lấy 2 số cuối
                analysis.db_last2 = str(giai_db[-2:]) if len(giai_db) >= 2 else giai_db
                
                # Tính tổng các chữ số của giải đặc biệt
                analysis.db_total = sum(int(digit) for digit in giai_db if digit.isdigit())
                
                # Tính tổng 2 số cuối
                last2_digits = analysis.db_last2
                analysis.db_last2_total = sum(int(digit) for digit in last2_digits if digit.isdigit())
                
                # Gán từng chữ số (nếu có đủ)
                analysis.db_digit1 = giai_db[0] if len(giai_db) > 0 else ''
                analysis.db_digit2 = giai_db[1] if len(giai_db) > 1 else ''
                analysis.db_digit3 = giai_db[2] if len(giai_db) > 2 else ''
                analysis.db_digit4 = giai_db[3] if len(giai_db) > 3 else ''
                analysis.db_digit5 = giai_db[4] if len(giai_db) > 4 else ''
                analysis.db_digit6 = giai_db[5] if len(giai_db) > 5 else ''
                
                self.stdout.write(f"    + Chạm đầu: '{analysis.db_cham_dau}'")
                self.stdout.write(f"    + Chạm đuôi: '{analysis.db_cham_duoi}'")
                self.stdout.write(f"    + 2 số cuối: '{analysis.db_last2}'")
                self.stdout.write(f"    + Tổng ĐB: {analysis.db_total}")
                self.stdout.write(f"    + Tổng 2 số cuối: {analysis.db_last2_total}")
            else:
                analysis.db_full = ''
                analysis.db_cham_dau = '0'
                analysis.db_cham_duoi = '0'
                analysis.db_last2 = '00'
                analysis.db_total = 0
                analysis.db_last2_total = 0
                analysis.db_digit1 = ''
                analysis.db_digit2 = ''
                analysis.db_digit3 = ''
                analysis.db_digit4 = ''
                analysis.db_digit5 = ''
                analysis.db_digit6 = ''
            
            # THÊM: Xử lý giải nhất
            giai_nhat = ket_qua.giai_1 or ''
            if giai_nhat:
                analysis.giai_nhat_full = str(giai_nhat)
                # Lấy chữ số giữa (nếu có 5 số thì lấy số thứ 3)
                if len(giai_nhat) >= 3:
                    mid_index = len(giai_nhat) // 2
                    analysis.giai_nhat_mid_digit = str(giai_nhat[mid_index])
                else:
                    analysis.giai_nhat_mid_digit = giai_nhat[0] if giai_nhat else '0'
            else:
                analysis.giai_nhat_full = ''
                analysis.giai_nhat_mid_digit = '0'
            
            # Test các trường ngày
            self.stdout.write("  - Đang set thông tin ngày...")
            analysis.day_of_week = ket_qua.ngay.weekday()
            analysis.month = ket_qua.ngay.month
            analysis.week_number = ket_qua.ngay.isocalendar()[1]
            
            # Test Boolean fields - QUAN TRỌNG
            self.stdout.write("  - Đang reset Boolean fields...")
            
            # Kiểm tra từng trường Boolean trước khi gán
            boolean_fields = [
                'is_sunday', 'is_monday', 'is_tuesday', 'is_wednesday', 
                'is_thursday', 'is_friday', 'is_saturday'
            ]
            
            for field in boolean_fields:
                if hasattr(analysis, field):
                    old_value = getattr(analysis, field)
                    self.stdout.write(f"    + {field}: {old_value} -> False")
                    setattr(analysis, field, False)
                else:
                    self.stdout.write(f"    ! Trường {field} không tồn tại!")
            
            # Set đúng ngày
            weekday = ket_qua.ngay.weekday()
            weekday_names = ['is_monday', 'is_tuesday', 'is_wednesday', 'is_thursday', 'is_friday', 'is_saturday', 'is_sunday']
            if 0 <= weekday < len(weekday_names):
                field_name = weekday_names[weekday]
                if hasattr(analysis, field_name):
                    setattr(analysis, field_name, True)
                    self.stdout.write(f"    + Set {field_name} = True")
                else:
                    self.stdout.write(f"    ! Trường {field_name} không tồn tại!")
            
            # Test các trường chạm đầu/đuôi
            self.stdout.write("  - Đang set trường chạm...")
            for i in range(10):
                cham_dau_field = f'cham_dau_{i}'
                cham_duoi_field = f'cham_duoi_{i}'
                
                if hasattr(analysis, cham_dau_field):
                    setattr(analysis, cham_dau_field, False)
                else:
                    self.stdout.write(f"    ! Trường {cham_dau_field} không tồn tại!")
                    
                if hasattr(analysis, cham_duoi_field):
                    setattr(analysis, cham_duoi_field, False)
                else:
                    self.stdout.write(f"    ! Trường {cham_duoi_field} không tồn tại!")
            
            # Set đúng giá trị chạm
            if analysis.db_cham_dau and analysis.db_cham_dau.isdigit():
                digit = int(analysis.db_cham_dau)
                field_name = f'cham_dau_{digit}'
                if hasattr(analysis, field_name):
                    setattr(analysis, field_name, True)
                    self.stdout.write(f"    + Set {field_name} = True")
            
            if analysis.db_cham_duoi and analysis.db_cham_duoi.isdigit():
                digit = int(analysis.db_cham_duoi)
                field_name = f'cham_duoi_{digit}'
                if hasattr(analysis, field_name):
                    setattr(analysis, field_name, True)
                    self.stdout.write(f"    + Set {field_name} = True")
            
            # THÊM: Set giá trị mặc định cho các trường có thể null
            if not hasattr(analysis, 'cau_cham1_value') or analysis.cau_cham1_value is None:
                analysis.cau_cham1_value = None
            if not hasattr(analysis, 'cau_cham2_value') or analysis.cau_cham2_value is None:
                analysis.cau_cham2_value = None
            
            # Test save
            self.stdout.write("  - Đang lưu vào database...")
            
            # Kiểm tra tất cả fields trước khi save
            for field in analysis._meta.get_fields():
                if hasattr(analysis, field.name):
                    value = getattr(analysis, field.name)
                    if field.get_internal_type() == 'BooleanField':
                        if not isinstance(value, bool) and value is not None:
                            self.stdout.write(f"    ! CẢNH BÁO: {field.name} có giá trị không hợp lệ: {value} (type: {type(value)})")
                            # Fix ngay
                            setattr(analysis, field.name, bool(value) if value else False)
            
            # Debug: In ra các giá trị quan trọng trước khi save
            self.stdout.write(f"    + db_last2_total: {analysis.db_last2_total}")
            self.stdout.write(f"    + db_total: {analysis.db_total}")
            self.stdout.write(f"    + giai_nhat_full: '{analysis.giai_nhat_full}'")
            
            analysis.save()
            self.stdout.write(f"  ✅ Thành công!")
            
        except Exception as e:
            self.stdout.write(f"  ❌ LỖI: {str(e)}")
            # In thêm thông tin chi tiết
            import traceback
            self.stdout.write(f"  📋 Traceback: {traceback.format_exc()}")
            raise e

    def _create_cham_data(self, ket_qua, force_update):
        """
        Tạo dữ liệu chạm đầu và chạm đuôi
        """
        try:
            if force_update:
                ChamDau.objects.filter(ngay=ket_qua.ngay).delete()
                ChamDuoi.objects.filter(ngay=ket_qua.ngay).delete()
            
            if hasattr(ChamDau.objects, 'create_for_date'):
                ChamDau.objects.create_for_date(ket_qua.ngay, ket_qua)
            else:
                self._manual_create_cham_dau(ket_qua)
            
            if hasattr(ChamDuoi.objects, 'create_for_date'):
                ChamDuoi.objects.create_for_date(ket_qua.ngay, ket_qua)
            else:
                self._manual_create_cham_duoi(ket_qua)
                
        except Exception as e:
            logger.error(f"Lỗi khi tạo dữ liệu chạm: {str(e)}")
    
    def _manual_create_cham_dau(self, ket_qua):
        """
        Tạo thủ công dữ liệu chạm đầu
        """
        all_numbers = self._extract_2digit_numbers(ket_qua)
        
        for i in range(10):
            cham_value = str(i)
            matching_numbers = [num for num in all_numbers if num.startswith(cham_value)]
            has_hit = len(matching_numbers) > 0
            
            ChamDau.objects.get_or_create(
                ngay=ket_qua.ngay,
                cham_value=cham_value,
                defaults={
                    'ket_qua': ket_qua,
                    'has_hit': has_hit,
                    'matching_numbers': ','.join(matching_numbers),
                    'hit_count': len(matching_numbers)
                }
            )
    
    def _manual_create_cham_duoi(self, ket_qua):
        """
        Tạo thủ công dữ liệu chạm đuôi
        """
        all_numbers = self._extract_2digit_numbers(ket_qua)
        
        for i in range(10):
            cham_value = str(i)
            matching_numbers = [num for num in all_numbers if num.endswith(cham_value)]
            has_hit = len(matching_numbers) > 0
            
            ChamDuoi.objects.get_or_create(
                ngay=ket_qua.ngay,
                cham_value=cham_value,
                defaults={
                    'ket_qua': ket_qua,
                    'has_hit': has_hit,
                    'matching_numbers': ','.join(matching_numbers),
                    'hit_count': len(matching_numbers)
                }
            )
    
    def _create_qua_tram_patterns(self, ket_qua, force_update):
        """
        Tạo mẫu quả trám
        """
        try:
            if force_update:
                QuaTramPattern.objects.filter(ngay=ket_qua.ngay).delete()
            
            if hasattr(QuaTramPattern.objects, 'find_patterns'):
                QuaTramPattern.objects.find_patterns(ket_qua)
            else:
                self._manual_create_qua_tram_patterns(ket_qua)
                
        except Exception as e:
            logger.error(f"Lỗi khi tạo mẫu quả trám: {str(e)}")
    
    def _manual_create_qua_tram_patterns(self, ket_qua):
        """
        Tạo thủ công mẫu quả trám
        """
        # Logic tạo mẫu quả trám - cần điều chỉnh theo quy tắc cụ thể
        # Đây là logic mẫu đơn giản
        
        if hasattr(ket_qua, 'giai_db') and ket_qua.giai_db:
            db_str = str(ket_qua.giai_db)
            if len(db_str) >= 4:
                # Tạo mẫu từ 4 chữ số cuối của giải đặc biệt
                digits = db_str[-4:]
                
                QuaTramPattern.objects.get_or_create(
                    ngay=ket_qua.ngay,
                    defaults={
                        'ket_qua': ket_qua,
                        'digit_top': digits[0],
                        'digit_mid_left': digits[1],
                        'digit_mid_right': digits[2],
                        'digit_bottom': digits[3],
                        'predicted_number': digits[-2:],  # 2 chữ số cuối làm dự đoán
                        'has_hit': False,
                        'days_to_hit': None,
                        'hit_date': None
                    }
                )