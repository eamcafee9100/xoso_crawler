from datetime import timedelta
import math
from django.utils import timezone
from chamde.models import ChamAnalysis, ChamDau, ChamDuoi, QuaTramPattern, NumberStatistics, NumberFrequencyTimeSeriesStats
from results.models import KetQuaXoSo


class ChamAnalyzer:
    """
    Công cụ phân tích dữ liệu chạm từ kết quả xổ số
    """
    def __init__(self, start_date=None, end_date=None):
        """
        Khởi tạo công cụ phân tích với khoảng thời gian
        """
        self.start_date = start_date
        self.end_date = end_date or timezone.now().date()
        if not self.start_date:
            # Mặc định phân tích 90 ngày gần nhất
            self.start_date = self.end_date - timedelta(days=90)
    
    def analyze_all(self):
        """
        Phân tích tất cả các khía cạnh của dữ liệu chạm
        """
        # Lấy tất cả kết quả xổ số trong khoảng thời gian
        ket_qua_list = KetQuaXoSo.objects.filter(
            ngay__gte=self.start_date,
            ngay__lte=self.end_date
        ).order_by('ngay')
        
        # Phân tích dữ liệu
        for ket_qua in ket_qua_list:
            self.analyze_single_day(ket_qua)
        
        # Tạo báo cáo thống kê
        return self.generate_statistics()
    
    def analyze_single_day(self, ket_qua):
        """
        Phân tích dữ liệu chạm cho một ngày
        """
        # Tạo phân tích chạm
        cham_analysis, created = ChamAnalysis.objects.get_or_create(
            ngay=ket_qua.ngay,
            defaults={'ket_qua': ket_qua}
        )
        
        if created:
            # Cập nhật dữ liệu nếu mới tạo
            ChamAnalysis.objects.create_from_ketqua(ket_qua)
        
        # Tạo dữ liệu chạm đầu và chạm đuôi
        ChamDau.objects.create_for_date(ket_qua.ngay, ket_qua)
        ChamDuoi.objects.create_for_date(ket_qua.ngay, ket_qua)
        
        # Tìm mẫu quả trám
        QuaTramPattern.objects.find_patterns(ket_qua)
        
        # Cập nhật thống kê số
        self.update_number_statistics(ket_qua)
    
    def update_number_statistics(self, ket_qua):
        """
        Cập nhật thống kê cho tất cả các số xuất hiện trong kết quả
        """
        all_numbers = ket_qua.get_all_2digit_numbers()
        db_last2 = ket_qua.giai_db[-2:] if len(ket_qua.giai_db) >= 2 else ''
        
        # Cập nhật thống kê cho mỗi số
        for number in all_numbers:
            # Tìm hoặc tạo bản ghi thống kê
            number_stat, created = NumberStatistics.objects.get_or_create(
                number=number,
                defaults={
                    'cham_dau': number[0],
                    'cham_duoi': number[1],
                    'last_appearance_date': ket_qua.ngay,
                    'is_double': number[0] == number[1],
                    'is_mirror': (int(number[0]) + int(number[1])) == 9,
                    'is_consecutive': abs(int(number[0]) - int(number[1])) == 1
                }
            )
            
            # Cập nhật thống kê
            number_stat.total_appearances += 1
            if number == db_last2:
                number_stat.db_appearances += 1
            
            # Cập nhật thống kê theo ngày trong tuần
            day_of_week = ket_qua.ngay.weekday()
            if day_of_week == 0:
                number_stat.monday_hits += 1
            elif day_of_week == 1:
                number_stat.tuesday_hits += 1
            elif day_of_week == 2:
                number_stat.wednesday_hits += 1
            elif day_of_week == 3:
                number_stat.thursday_hits += 1
            elif day_of_week == 4:
                number_stat.friday_hits += 1
            elif day_of_week == 5:
                number_stat.saturday_hits += 1
            elif day_of_week == 6:
                number_stat.sunday_hits += 1
            
            # Tính toán số ngày trung bình giữa các lần về
            if number_stat.last_appearance_date and number_stat.last_appearance_date != ket_qua.ngay:
                days_between = (ket_qua.ngay - number_stat.last_appearance_date).days
                if not number_stat.avg_days_between_hits:
                    number_stat.avg_days_between_hits = days_between
                    number_stat.std_days_between_hits = 0
                else:
                    # Cập nhật giá trị trung bình động
                    old_avg = number_stat.avg_days_between_hits
                    new_avg = old_avg + (days_between - old_avg) / number_stat.total_appearances
                    
                    # Cập nhật độ lệch chuẩn động
                    old_std = number_stat.std_days_between_hits or 0
                    new_std = math.sqrt(old_std**2 + (days_between - old_avg) * (days_between - new_avg))
                    
                    number_stat.avg_days_between_hits = new_avg
                    number_stat.std_days_between_hits = new_std
            
            # Cập nhật ngày xuất hiện gần nhất
            number_stat.last_appearance_date = ket_qua.ngay
            number_stat.save()
            
            # Cập nhật thống kê tần suất theo thời gian
            self.update_frequency_time_series(number, ket_qua)
    
    def update_frequency_time_series(self, number, ket_qua):
        """
        Cập nhật thống kê chuỗi thời gian cho số
        """
        date = ket_qua.ngay
        db_last2 = ket_qua.giai_db[-2:] if len(ket_qua.giai_db) >= 2 else ''
        is_db = (number == db_last2)
        
        # Cập nhật thống kê hàng ngày
        daily_stat, created = NumberFrequencyTimeSeriesStats.objects.get_or_create(
            number=number,
            period_type='daily',
            period_start=date,
            defaults={
                'period_end': date,
                'cham_dau': number[0],
                'cham_duoi': number[1],
                'appearance_count': 1,
                'db_appearance_count': 1 if is_db else 0,
                'appearance_days': [date.isoformat()]
            }
        )
        
        if not created:
            daily_stat.appearance_count += 1
            if is_db:
                daily_stat.db_appearance_count += 1
            days = daily_stat.appearance_days or []
            days.append(date.isoformat())
            daily_stat.appearance_days = days
            daily_stat.save()
        
        # Cập nhật thống kê hàng tuần
        week_start = date - timedelta(days=date.weekday())
        week_end = week_start + timedelta(days=6)
        
        weekly_stat, created = NumberFrequencyTimeSeriesStats.objects.get_or_create(
            number=number,
            period_type='weekly',
            period_start=week_start,
            defaults={
                'period_end': week_end,
                'cham_dau': number[0],
                'cham_duoi': number[1],
                'appearance_count': 1,
                'db_appearance_count': 1 if is_db else 0,
                'appearance_days': [date.isoformat()]
            }
        )
        
        if not created:
            weekly_stat.appearance_count += 1
            if is_db:
                weekly_stat.db_appearance_count += 1
            days = weekly_stat.appearance_days or []
            days.append(date.isoformat())
            weekly_stat.appearance_days = days
            weekly_stat.save()
        
        # Cập nhật thống kê hàng tháng
        month_start = date.replace(day=1)
        if date.month == 12:
            month_end = date.replace(year=date.year+1, month=1, day=1) - timedelta(days=1)
        else:
            month_end = date.replace(month=date.month+1, day=1) - timedelta(days=1)
        
        monthly_stat, created = NumberFrequencyTimeSeriesStats.objects.get_or_create(
            number=number,
            period_type='monthly',
            period_start=month_start,
            defaults={
                'period_end': month_end,
                'cham_dau': number[0],
                'cham_duoi': number[1],
                'appearance_count': 1,
                'db_appearance_count': 1 if is_db else 0,
                'appearance_days': [date.isoformat()]
            }
        )
        
        if not created:
            monthly_stat.appearance_count += 1
            if is_db:
                monthly_stat.db_appearance_count += 1
            days = monthly_stat.appearance_days or []
            days.append(date.isoformat())
            monthly_stat.appearance_days = days
            monthly_stat.save()
    
    def generate_statistics(self):
        """
        Tạo báo cáo thống kê tổng hợp
        """
        # Thống kê tổng quan
        total_days = (self.end_date - self.start_date).days + 1
        total_results = KetQuaXoSo.objects.filter(
            ngay__gte=self.start_date,
            ngay__lte=self.end_date
        ).count()
        
        # Thống kê chạm đầu
        cham_dau_stats = {}
        for i in range(10):
            cham_value = str(i)
            hits = ChamDau.objects.filter(
                ngay__gte=self.start_date,
                ngay__lte=self.end_date,
                cham_value=cham_value,
                has_hit=True
            ).count()
            
            cham_dau_stats[cham_value] = {
                'hits': hits,
                'hit_rate': (hits / total_results) * 100 if total_results > 0 else 0
            }
        
        # Thống kê chạm đuôi
        cham_duoi_stats = {}
        for i in range(10):
            cham_value = str(i)
            hits = ChamDuoi.objects.filter(
                ngay__gte=self.start_date,
                ngay__lte=self.end_date,
                cham_value=cham_value,
                has_hit=True
            ).count()
            
            cham_duoi_stats[cham_value] = {
                'hits': hits,
                'hit_rate': (hits / total_results) * 100 if total_results > 0 else 0
            }
        
        # Thống kê cầu chạm 1
        cau_cham1_stats = {}
        for analysis in ChamAnalysis.objects.filter(
            ngay__gte=self.start_date,
            ngay__lte=self.end_date,
            is_sunday=True
        ):
            if analysis.cau_cham1_value:
                # Lấy kết quả các ngày trong tuần tiếp theo
                start_date = analysis.ngay + timedelta(days=1)
                end_date = start_date + timedelta(days=6)
                
                # Lấy giải đặc biệt trong tuần tiếp theo
                results = KetQuaXoSo.objects.filter(
                    ngay__gte=start_date,
                    ngay__lte=end_date
                )
                
                # Kiểm tra xem cầu chạm 1 có trúng không
                hits = []
                for result in results:
                    db_last2 = result.giai_db[-2:] if len(result.giai_db) >= 2 else ''
                    if db_last2 and db_last2[0] == analysis.cau_cham1_value:
                        hits.append({
                            'date': result.ngay,
                            'db': db_last2
                        })
                
                if analysis.cau_cham1_value not in cau_cham1_stats:
                    cau_cham1_stats[analysis.cau_cham1_value] = []
                
                cau_cham1_stats[analysis.cau_cham1_value].append({
                    'sunday_date': analysis.ngay,
                    'hits': hits,
                    'hit_count': len(hits)
                })
        
        # Thống kê cầu chạm 2
        cau_cham2_stats = {}
        for analysis in ChamAnalysis.objects.filter(
            ngay__gte=self.start_date,
            ngay__lte=self.end_date,
            is_sunday=True
        ):
            if analysis.cau_cham2_value:
                # Lấy kết quả các ngày trong tuần tiếp theo
                start_date = analysis.ngay + timedelta(days=1)
                end_date = start_date + timedelta(days=6)
                
                # Lấy giải đặc biệt trong tuần tiếp theo
                results = KetQuaXoSo.objects.filter(
                    ngay__gte=start_date,
                    ngay__lte=end_date
                )
                
                # Kiểm tra xem cầu chạm 2 có trúng không
                hits = []
                for result in results:
                    db_last2 = result.giai_db[-2:] if len(result.giai_db) >= 2 else ''
                    if db_last2 == analysis.cau_cham2_value:
                        hits.append({
                            'date': result.ngay,
                            'db': db_last2
                        })
                
                if analysis.cau_cham2_value not in cau_cham2_stats:
                    cau_cham2_stats[analysis.cau_cham2_value] = []
                
                cau_cham2_stats[analysis.cau_cham2_value].append({
                    'sunday_date': analysis.ngay,
                    'hits': hits,
                    'hit_count': len(hits)
                })
        
        # Thống kê mẫu quả trám
        qua_tram_stats = {}
        for pattern in QuaTramPattern.objects.filter(
            ngay__gte=self.start_date,
            ngay__lte=self.end_date
        ):
            # Kiểm tra xem số dự đoán có trúng trong 5 ngày tiếp theo
            start_date = pattern.ngay + timedelta(days=1)
            end_date = start_date + timedelta(days=5)
            
            # Lấy giải đặc biệt trong 5 ngày tiếp theo
            results = KetQuaXoSo.objects.filter(
                ngay__gte=start_date,
                ngay__lte=end_date
            )
            
            # Kiểm tra xem số dự đoán có trúng không
            for result in results:
                db_last2 = result.giai_db[-2:] if len(result.giai_db) >= 2 else ''
                if db_last2 == pattern.predicted_number:
                    days_to_hit = (result.ngay - pattern.ngay).days
                    pattern.hit_date = result.ngay
                    pattern.days_to_hit = days_to_hit
                    pattern.has_hit = True
                    pattern.save()
                    break
            
            # Thêm vào thống kê
            if pattern.predicted_number not in qua_tram_stats:
                qua_tram_stats[pattern.predicted_number] = []
            
            qua_tram_stats[pattern.predicted_number].append({
                'date': pattern.ngay,
                'pattern': f"{pattern.digit_top}-{pattern.digit_mid_left}{pattern.digit_mid_right}-{pattern.digit_bottom}",
                'has_hit': pattern.has_hit,
                'days_to_hit': pattern.days_to_hit,
                'hit_date': pattern.hit_date
            })
        
        # Tính hiệu suất trúng của các phương pháp
        qua_tram_hit_rate = 0
        total_qua_tram = 0
        for number, patterns in qua_tram_stats.items():
            hits = sum(1 for p in patterns if p['has_hit'])
            total_qua_tram += len(patterns)
            if len(patterns) > 0:
                qua_tram_stats[number] = {
                    'patterns': patterns,
                    'hit_rate': (hits / len(patterns)) * 100
                }
        
        if total_qua_tram > 0:
            qua_tram_hit_rate = sum(stats['hit_rate'] for stats in qua_tram_stats.values()) / len(qua_tram_stats)
        
        # Tạo báo cáo tổng hợp
        return {
            'period': {
                'start_date': self.start_date,
                'end_date': self.end_date,
                'total_days': total_days,
                'total_results': total_results
            },
            'cham_dau_stats': cham_dau_stats,
            'cham_duoi_stats': cham_duoi_stats,
            'cau_cham1_stats': cau_cham1_stats,
            'cau_cham2_stats': cau_cham2_stats,
            'qua_tram_stats': qua_tram_stats,
            'qua_tram_hit_rate': qua_tram_hit_rate
        }