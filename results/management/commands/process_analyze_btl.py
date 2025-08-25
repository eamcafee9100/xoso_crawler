from django.core.management.base import BaseCommand
from django.utils import timezone
from django.db.models import Sum, Count, F, Func
from django.db.models.functions import Cast
from datetime import date, timedelta
import logging
import math
import calendar
from collections import defaultdict
from results.models import DanBtl, BtlAnalytics, BtlTimeAggregation, PredictionResultBtl, BtlMethodAnalytics

logger = logging.getLogger(__name__)

class JsonbArrayLength(Func):
    function = 'JSONB_ARRAY_LENGTH'
    arity = 1

class Command(BaseCommand):
    help = 'Xây dựng dữ liệu phân tích cho Bạch Thủ Lô'

    def add_arguments(self, parser):
        parser.add_argument(
            '--days',
            type=int,
            default=90,
            help='Số ngày gần đây cần phân tích (mặc định: 90)'
        )
        parser.add_argument(
            '--start-date',
            type=str,
            help='Ngày bắt đầu phân tích (format: YYYY-MM-DD)'
        )
        parser.add_argument(
            '--end-date',
            type=str,
            help='Ngày kết thúc phân tích (format: YYYY-MM-DD)'
        )
        parser.add_argument(
            '--force',
            action='store_true',
            help='Buộc cập nhật lại dữ liệu đã có'
        )

    def handle(self, *args, **options):
        days = options['days']
        start_date_str = options['start_date']
        end_date_str = options['end_date']
        force = options['force']
        today = timezone.now().date()

        # Xác định khoảng thời gian
        if start_date_str and end_date_str:
            start_date = date.fromisoformat(start_date_str)
            end_date = date.fromisoformat(end_date_str)
        else:
            end_date = today
            start_date = end_date - timedelta(days=days-1)

        self.stdout.write(f"Xây dựng dữ liệu phân tích từ {start_date} đến {end_date}")

        # Lấy tất cả DanBtl trong khoảng thời gian
        dan_btl_entries = DanBtl.objects.filter(
            analysis_date__gte=start_date,
            analysis_date__lte=end_date
        ).order_by('analysis_date')

        total_count = dan_btl_entries.count()
        success_count = 0
        skip_count = 0
        error_count = 0

        self.stdout.write(f"Tìm thấy {total_count} bản ghi DanBtl cần phân tích")

        # Duyệt qua từng ngày
        for dan_btl in dan_btl_entries:
            analysis_date = dan_btl.analysis_date
            
            # Kiểm tra xem đã có phân tích chưa
            existing = BtlAnalytics.objects.filter(date=analysis_date).exists()
            if existing and not force:
                self.stdout.write(f"Đã có phân tích cho ngày {analysis_date}, bỏ qua")
                skip_count += 1
                continue
            
            self.stdout.write(f"Đang phân tích ngày {analysis_date}...")
            try:
                analytics = update_btl_analytics(analysis_date)
                if analytics:
                    success_count += 1
                    self.stdout.write(self.style.SUCCESS(f"✓ Đã phân tích thành công ngày {analysis_date}"))
                else:
                    error_count += 1
                    self.stdout.write(self.style.ERROR(f"✗ Lỗi khi phân tích ngày {analysis_date}"))
            except Exception as e:
                error_count += 1
                self.stdout.write(self.style.ERROR(f"✗ Lỗi: {str(e)}"))
                logger.error(f"Lỗi khi phân tích ngày {analysis_date}: {str(e)}", exc_info=True)

        # Cập nhật tổng hợp theo tháng
        months = set()
        for dan_btl in dan_btl_entries:
            months.add((dan_btl.analysis_date.year, dan_btl.analysis_date.month))
        
        for year, month in months:
            try:
                self.stdout.write(f"Đang cập nhật tổng hợp tháng {month}/{year}...")
                update_monthly_aggregation(year, month)
                self.stdout.write(self.style.SUCCESS(f"✓ Đã cập nhật tổng hợp tháng {month}/{year}"))
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"✗ Lỗi khi tổng hợp tháng {month}/{year}: {str(e)}"))

        # Hiển thị thống kê
        self.stdout.write("\n--- Thống kê ---")
        self.stdout.write(f"Tổng số ngày cần phân tích: {total_count}")
        self.stdout.write(f"Thành công: {success_count}")
        self.stdout.write(f"Bỏ qua: {skip_count}")
        self.stdout.write(f"Lỗi: {error_count}")
        
        if success_count > 0:
            self.stdout.write(self.style.SUCCESS("\nĐã xây dựng dữ liệu phân tích thành công!"))


def update_btl_analytics(analysis_date):
    """
    Cập nhật dữ liệu phân tích cho một ngày cụ thể
    """
    try:
        # Lấy dữ liệu DanBtl
        dan_btl = DanBtl.objects.get(analysis_date=analysis_date)
        
        # Thông tin thời gian
        year = analysis_date.year
        month = analysis_date.month
        day = analysis_date.day
        day_of_week = analysis_date.weekday()  # 0 = Thứ 2, 6 = Chủ nhật
        week_of_year = analysis_date.isocalendar()[1]

        # Lấy thông tin kết quả xổ số ngày kế tiếp
        prize_next_day = dan_btl.prize_next_day

        # Lấy tất cả kết quả dự đoán
        prediction_results = PredictionResultBtl.objects.filter(dan_btl=dan_btl)

        # Tính toán thông tin tổng quan
        total_methods = prediction_results.values('method').distinct().count()
        
        # Tính toán tổng số dự đoán và tổng số trúng
        # Sửa: Sử dụng Sum('hit_count') cho số trúng
        # Đếm tổng số dự đoán từ predicted_numbers trong mỗi kết quả
        total_predictions = 0
        total_hits = 0
        
        for result in prediction_results:
            total_predictions += len(result.predicted_numbers)
            total_hits += result.hit_count
            
        overall_hit_rate = (total_hits / total_predictions * 100) if total_predictions > 0 else 0

        # Số phương pháp có trúng
        methods_with_hits = prediction_results.filter(hit_count__gt=0).values('method').distinct().count()
        methods_hit_rate = (methods_with_hits / total_methods * 100) if total_methods > 0 else 0

        # Thu thập các số trúng
        all_winning_numbers = set()
        for result in prediction_results:
            if result.winning_numbers:
                all_winning_numbers.update(result.winning_numbers)

        # Thu thập thông tin số dự đoán
        number_counts = defaultdict(int)
        method_counts = defaultdict(set)
        for result in prediction_results:
            for num in result.predicted_numbers:
                number_counts[num] += 1
                method_counts[num].add(result.method.id)  # Sửa: method.id thay vì method_id

        # Top 10 số được dự đoán nhiều nhất
        most_predicted = sorted(number_counts.items(), key=lambda x: x[1], reverse=True)[:10]
        most_predicted_numbers = [
            {
                'number': num,
                'count': count,
                'is_hit': num in all_winning_numbers
            }
            for num, count in most_predicted
        ]

        # Top 10 số có nhiều phương pháp dự đoán nhất
        most_consensus = sorted(method_counts.items(), key=lambda x: len(x[1]), reverse=True)[:10]
        most_consensus_numbers = [
            {
                'number': num,
                'method_count': len(methods),
                'is_hit': num in all_winning_numbers
            }
            for num, methods in most_consensus
        ]

        # Phân tích hiệu suất phương pháp
        method_performance = {}
        for result in prediction_results:
            method_id = result.method.id  # Sửa: method.id thay vì method_id
            if method_id not in method_performance:
                method_performance[method_id] = {
                    'id': method_id,
                    'name': result.method.name,
                    'prediction_count': 0,
                    'hit_count': 0,
                    'hit_rate': 0
                }
            method_performance[method_id]['prediction_count'] += len(result.predicted_numbers)
            method_performance[method_id]['hit_count'] += result.hit_count

        # Tính tỷ lệ trúng cho từng phương pháp
        for method_id, data in method_performance.items():
            pred_count = data['prediction_count']
            hit_count = data['hit_count']
            data['hit_rate'] = (hit_count / pred_count * 100) if pred_count > 0 else 0

        # Top 5 phương pháp tốt nhất
        best_methods = sorted(
            method_performance.values(),
            key=lambda x: (x['hit_rate'], x['hit_count']),
            reverse=True
        )[:5]

        # Tính toán số ngày trúng/trật liên tiếp
        sequential_hits = 0
        sequential_misses = 0
        
        # Tìm ngày trước đó
        prev_date = analysis_date - timedelta(days=1)
        prev_analytics = BtlAnalytics.objects.filter(date=prev_date).first()
        
        if prev_analytics:
            if total_hits > 0:
                # Ngày này có trúng
                sequential_hits = prev_analytics.sequential_hits + 1
                sequential_misses = 0
            else:
                # Ngày này không trúng
                sequential_hits = 0
                sequential_misses = prev_analytics.sequential_misses + 1
        else:
            # Không có dữ liệu trước đó
            sequential_hits = 1 if total_hits > 0 else 0
            sequential_misses = 0 if total_hits > 0 else 1

        # Tạo hoặc cập nhật BtlAnalytics
        analytics, created = BtlAnalytics.objects.update_or_create(
            date=analysis_date,
            dan_btl=dan_btl,
            defaults={
                'year': year,
                'month': month,
                'day': day,
                'day_of_week': day_of_week,
                'week_of_year': week_of_year,
                'total_methods': total_methods,
                'total_predictions': total_predictions,
                'total_hits': total_hits,
                'overall_hit_rate': overall_hit_rate,
                'prize_next_day': prize_next_day,
                'winning_numbers': list(all_winning_numbers),
                'methods_with_hits': methods_with_hits,
                'methods_hit_rate': methods_hit_rate,
                'most_predicted_numbers': most_predicted_numbers,
                'most_consensus_numbers': most_consensus_numbers,
                'best_methods': best_methods,
                'sequential_hits': sequential_hits,
                'sequential_misses': sequential_misses
            }
        )

        # Tạo hoặc cập nhật BtlMethodAnalytics cho từng phương pháp
        for result in prediction_results:
            method = result.method
            
            # Tính toán tỷ lệ trúng trung bình 7 và 30 ngày
            rolling_7d = calculate_rolling_hit_rate(method, analysis_date, days=7)
            rolling_30d = calculate_rolling_hit_rate(method, analysis_date, days=30)
            
            # Xác định xu hướng
            trend = 'stable'
            if rolling_7d > rolling_30d * 1.1:  # Tăng hơn 10%
                trend = 'up'
            elif rolling_7d < rolling_30d * 0.9:  # Giảm hơn 10%
                trend = 'down'
                
            # Tính toán lợi nhuận ước tính
            pred_count = len(result.predicted_numbers)
            hit_count = result.hit_count
            hit_rate = (hit_count / pred_count * 100) if pred_count > 0 else 0
            
            # Giả sử: Cược 27,000đ/số, trúng được 94,000đ/số
            bet_amount = 27000  # Số tiền cược cho mỗi số
            win_amount = 99400 # Số tiền thắng cho mỗi số trúng
            total_bet = pred_count * bet_amount
            total_win = hit_count * win_amount
            profit = total_win - total_bet
            roi = (profit / total_bet * 100) if total_bet > 0 else 0
            
            # Tính Wilson score
            confidence_score = wilson_score(hit_count, pred_count)
            
            # Tạo hoặc cập nhật BtlMethodAnalytics
            BtlMethodAnalytics.objects.update_or_create(
                btl_analytics=analytics,
                method=method,
                defaults={
                    'date': analysis_date,
                    'prediction_count': pred_count,
                    'hit_count': hit_count,
                    'hit_rate': hit_rate,
                    'confidence_score': confidence_score,
                    'profit_estimate': profit,
                    'roi_estimate': roi,
                    'predicted_numbers': result.predicted_numbers,
                    'hit_numbers': result.winning_numbers,
                    'rolling_hit_rate_7d': rolling_7d,
                    'rolling_hit_rate_30d': rolling_30d,
                    'trend_direction': trend
                }
            )
            
        # Cập nhật tổng hợp theo tháng
        update_monthly_aggregation(year, month)
        
        # Cập nhật tổng hợp theo tuần
        update_weekly_aggregation(year, week_of_year)
        
        return analytics
        
    except Exception as e:
        logger.error(f"Lỗi khi cập nhật phân tích BTL cho ngày {analysis_date}: {str(e)}", exc_info=True)
        return None


def calculate_rolling_hit_rate(method, end_date, days=7):
    """Tính tỷ lệ trúng trung bình trong khoảng thời gian"""
    start_date = end_date - timedelta(days=days)
    
    # Lấy kết quả trong khoảng thời gian
    results = PredictionResultBtl.objects.filter(
        method=method,
        dan_btl__analysis_date__gte=start_date,
        dan_btl__analysis_date__lt=end_date
    )
    
    # Sửa: Sử dụng tổng số dự đoán và tổng số trúng theo cách thủ công
    total_pred = 0
    total_hits = 0
    
    for result in results:
        total_pred += len(result.predicted_numbers)
        total_hits += result.hit_count
    
    return (total_hits / total_pred * 100) if total_pred > 0 else 0


def wilson_score(hits, trials, z=1.96):
    """Tính điểm Wilson score với khoảng tin cậy 95%"""
    if trials == 0:
        return 0
    
    p = hits / trials
    
    # Tính Wilson score
    numerator = p + z*z/(2*trials) - z * math.sqrt((p*(1-p) + z*z/(4*trials))/trials)
    denominator = 1 + z*z/trials
    
    return numerator / denominator


def update_monthly_aggregation(year, month):
    """Cập nhật tổng hợp theo tháng"""
    # Tính ngày đầu và cuối tháng
    first_day = date(year, month, 1)
    _, last_day_num = calendar.monthrange(year, month)
    last_day = date(year, month, last_day_num)
    
    # Lấy tất cả dữ liệu phân tích trong tháng
    analytics = BtlAnalytics.objects.filter(
        date__gte=first_day,
        date__lte=last_day
    )
    
    # Tính toán các số liệu tổng hợp
    total_days = analytics.count()
    days_with_hits = analytics.filter(total_hits__gt=0).count()
    days_hit_rate = (days_with_hits / total_days * 100) if total_days > 0 else 0
    
    total_predictions = analytics.aggregate(Sum('total_predictions')).get('total_predictions__sum', 0) or 0
    total_hits = analytics.aggregate(Sum('total_hits')).get('total_hits__sum', 0) or 0
    overall_hit_rate = (total_hits / total_predictions * 100) if total_predictions > 0 else 0
    
    # ... Tính toán thêm các thông tin khác ...
    
    # Tạo hoặc cập nhật BtlTimeAggregation
    BtlTimeAggregation.objects.update_or_create(
        aggregation_type='monthly',
        year=year,
        period=month,
        defaults={
            'start_date': first_day,
            'end_date': last_day,
            'total_days': total_days,
            'days_with_hits': days_with_hits,
            'days_hit_rate': days_hit_rate,
            'total_predictions': total_predictions,
            'total_hits': total_hits,
            'overall_hit_rate': overall_hit_rate,
            # ... Các thông tin khác ...
        }
    )


def update_weekly_aggregation(year, week):
    """Cập nhật tổng hợp theo tuần"""
    # Xác định ngày đầu tuần (thứ 2) và cuối tuần (chủ nhật) của tuần được chỉ định
    first_day_of_year = date(year, 1, 1)
    
    # Tìm ngày thứ hai đầu tiên của năm
    first_monday = first_day_of_year
    while first_monday.weekday() != 0:  # 0 là thứ hai
        first_monday += timedelta(days=1)
    
    # Tính ngày đầu tuần và cuối tuần dựa trên số tuần
    start_date = first_monday + timedelta(weeks=week-1)
    end_date = start_date + timedelta(days=6)
    
    # Lấy tất cả dữ liệu phân tích trong tuần
    analytics = BtlAnalytics.objects.filter(
        date__gte=start_date,
        date__lte=end_date
    )
    
    # Tính toán các số liệu tổng hợp
    total_days = analytics.count()
    days_with_hits = analytics.filter(total_hits__gt=0).count()
    days_hit_rate = (days_with_hits / total_days * 100) if total_days > 0 else 0
    
    total_predictions = analytics.aggregate(Sum('total_predictions')).get('total_predictions__sum', 0) or 0
    total_hits = analytics.aggregate(Sum('total_hits')).get('total_hits__sum', 0) or 0
    overall_hit_rate = (total_hits / total_predictions * 100) if total_predictions > 0 else 0
    
    # Tạo hoặc cập nhật BtlTimeAggregation
    BtlTimeAggregation.objects.update_or_create(
        aggregation_type='weekly',
        year=year,
        period=week,
        defaults={
            'start_date': start_date,
            'end_date': end_date,
            'total_days': total_days,
            'days_with_hits': days_with_hits,
            'days_hit_rate': days_hit_rate,
            'total_predictions': total_predictions,
            'total_hits': total_hits,
            'overall_hit_rate': overall_hit_rate,
            # ... Các thông tin khác ...
        }
    )