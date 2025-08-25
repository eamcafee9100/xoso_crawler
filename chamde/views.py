from django.shortcuts import render

# Create your views here.
from django.views.generic import TemplateView, ListView, DetailView
from django.utils import timezone
from django.db.models import Count, Avg, F, Sum, Case, When, IntegerField, FloatField
from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from django.contrib import messages
from datetime import timedelta, datetime
import json
from django.views.decorators.http import require_POST
from .models import (
    ChamAnalysis, ChamDau, ChamDuoi, CauChamPrediction, 
    QuaTramPattern, NumberStatistics, NumberFrequencyTimeSeriesStats,
    ChamPatternAnalysis, WeeklyDigitPatternStats, LoGanStats, KetQuaXoSo
)
from .models import generate_cham_dau_numbers, generate_cham_duoi_numbers

class ChamDashboardView(TemplateView):
    """Trang Dashboard cho phân tích chạm"""
    template_name = 'chamde/dashboard.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        today = timezone.now().date()
        
        # Lấy khoảng thời gian từ query params hoặc mặc định
        days = int(self.request.GET.get('days', 30))
        start_date = today - timedelta(days=days)
        
        # Thống kê cơ bản
        total_results = KetQuaXoSo.objects.filter(ngay__gte=start_date, ngay__lte=today).count()
        
        # Tỷ lệ trúng của chạm đầu
        cham_dau_stats = self._get_cham_stats(ChamDau, start_date, today)
        
        # Tỷ lệ trúng của chạm đuôi
        cham_duoi_stats = self._get_cham_stats(ChamDuoi, start_date, today)
        
        # Thống kê số lần xuất hiện của các số
        number_stats = NumberStatistics.objects.all().order_by('-total_appearances')[:20]
        
        # Kết quả xổ số gần đây
        recent_results = KetQuaXoSo.objects.filter(ngay__lte=today).order_by('-ngay')[:7]
        
        # Top số nóng (xuất hiện nhiều nhất trong khoảng thời gian)
        hot_numbers = NumberFrequencyTimeSeriesStats.objects.filter(
            period_type='daily',
            period_start__gte=start_date,
            period_start__lte=today
        ).values('number').annotate(
            total=Sum('appearance_count')
        ).order_by('-total')[:10]
        
        # Top số lạnh (số ít xuất hiện nhưng có xác suất cao sẽ về)
        cold_numbers = LoGanStats.objects.filter(
            date=today
        ).order_by('-due_probability')[:10]
        
        # Dự đoán cho ngày mai
        tomorrow = today + timedelta(days=1)
        predictions = CauChamPrediction.objects.filter(
            ngay_du_doan=tomorrow
        ).order_by('-do_tin_cay')
        
        # Các mẫu quả trám gần đây
        recent_qua_trams = QuaTramPattern.objects.filter(
            ngay__gte=start_date
        ).order_by('-ngay')[:5]
        
        # Thêm dữ liệu vào context
        context.update({
            'today': today,
            'tomorrow': tomorrow,
            'selected_days': days,
            'start_date': start_date,
            'total_results': total_results,
            'cham_dau_stats': cham_dau_stats,
            'cham_duoi_stats': cham_duoi_stats,
            'number_stats': number_stats,
            'recent_results': recent_results,
            'hot_numbers': hot_numbers,
            'cold_numbers': cold_numbers,
            'predictions': predictions,
            'recent_qua_trams': recent_qua_trams,
        })
        
        return context
    
    def _get_cham_stats(self, model, start_date, end_date):
        """Lấy thống kê trúng của từng giá trị chạm"""
        stats = {}
        
        for i in range(10):
            value = str(i)
            total = model.objects.filter(
                ngay__gte=start_date,
                ngay__lte=end_date,
                cham_value=value
            ).count()
            
            hits = model.objects.filter(
                ngay__gte=start_date,
                ngay__lte=end_date,
                cham_value=value,
                has_hit=True
            ).count()
            
            hit_rate = (hits / total) * 100 if total > 0 else 0
            stats[value] = {
                'total': total,
                'hits': hits,
                'hit_rate': hit_rate
            }
        
        return stats
    

class ChamAnalysisView(TemplateView):
    """Trang phân tích chi tiết các dạng chạm"""
    template_name = 'chamde/analysis.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        today = timezone.now().date()
        
        # Lấy khoảng thời gian từ query params hoặc mặc định
        days = int(self.request.GET.get('days', 30))
        start_date = today - timedelta(days=days)
        
        # Lấy loại chạm từ query params hoặc mặc định
        cham_type = self.request.GET.get('type', 'dau')
        
        # Tính toán thống kê chi tiết dựa trên loại chạm
        if cham_type == 'dau':
            stats = self._get_detailed_cham_stats(ChamDau, start_date, today)
            title = "Phân tích Chạm Đầu"
            description = "Phân tích các cặp số có chữ số hàng chục giống nhau"
        elif cham_type == 'duoi':
            stats = self._get_detailed_cham_stats(ChamDuoi, start_date, today)
            title = "Phân tích Chạm Đuôi"
            description = "Phân tích các cặp số có chữ số hàng đơn vị giống nhau"
        else:
            stats = {}
            title = "Phân tích Chạm"
            description = "Vui lòng chọn loại chạm để phân tích"
        
        # Phân tích theo ngày trong tuần
        weekday_analysis = self._get_weekday_analysis(cham_type, start_date, today)
        
        # Phân tích theo tháng
        month_analysis = self._get_month_analysis(cham_type, start_date, today)
        
        # Danh sách kết quả gần đây
        recent_results = self._get_recent_results(cham_type, start_date, today)
        
        # Phân tích xu hướng
        trend_analysis = self._get_trend_analysis(cham_type, start_date, today)
        
        # Thêm dữ liệu vào context
        context.update({
            'today': today,
            'selected_days': days,
            'start_date': start_date,
            'cham_type': cham_type,
            'title': title,
            'description': description,
            'stats': stats,
            'weekday_analysis': weekday_analysis,
            'month_analysis': month_analysis,
            'recent_results': recent_results,
            'trend_analysis': trend_analysis,
        })
        
        return context
    
    def _get_detailed_cham_stats(self, model, start_date, end_date):
        """Lấy thống kê chi tiết của từng giá trị chạm"""
        stats = {}
        
        for i in range(10):
            value = str(i)
            queryset = model.objects.filter(
                ngay__gte=start_date,
                ngay__lte=end_date,
                cham_value=value
            )
            total = queryset.count()
            
            hits = queryset.filter(has_hit=True).count()
            hit_rate = (hits / total) * 100 if total > 0 else 0
            
            # Lấy ngày trúng gần đây nhất
            last_hit = queryset.filter(has_hit=True).order_by('-ngay').first()
            
            # Tính số ngày trung bình giữa các lần trúng
            hit_dates = list(queryset.filter(has_hit=True).values_list('ngay', flat=True).order_by('ngay'))
            avg_days_between_hits = 0
            if len(hit_dates) > 1:
                days_between = [(hit_dates[i] - hit_dates[i-1]).days for i in range(1, len(hit_dates))]
                avg_days_between_hits = sum(days_between) / len(days_between)
            
            # Tính chu kỳ trúng
            cycle_prediction = None
            if last_hit and avg_days_between_hits > 0:
                next_hit_date = last_hit.ngay + timedelta(days=int(avg_days_between_hits))
                cycle_prediction = {
                    'date': next_hit_date,
                    'days_remaining': (next_hit_date - end_date).days
                }
            
            # Tính các số xuất hiện nhiều nhất trong dàn chạm này
            appeared_numbers = []
            for record in queryset:
                appeared_numbers.extend(record.appeared_numbers)
            
            # Đếm số lần xuất hiện của mỗi số
            number_counts = {}
            for num in appeared_numbers:
                if num in number_counts:
                    number_counts[num] += 1
                else:
                    number_counts[num] = 1
            
            # Sắp xếp theo số lần xuất hiện
            top_numbers = sorted(number_counts.items(), key=lambda x: x[1], reverse=True)[:5]
            
            stats[value] = {
                'total': total,
                'hits': hits,
                'hit_rate': hit_rate,
                'last_hit': last_hit,
                'avg_days_between_hits': avg_days_between_hits,
                'cycle_prediction': cycle_prediction,
                'top_numbers': top_numbers
            }
        
        return stats
    
    def _get_weekday_analysis(self, cham_type, start_date, end_date):
        """Phân tích tỷ lệ trúng theo ngày trong tuần"""
        model = ChamDau if cham_type == 'dau' else ChamDuoi
        weekdays = ['Thứ Hai', 'Thứ Ba', 'Thứ Tư', 'Thứ Năm', 'Thứ Sáu', 'Thứ Bảy', 'Chủ Nhật']
        weekday_stats = []
        
        for i in range(7):
            # Tính tổng số kết quả cho ngày này
            total = KetQuaXoSo.objects.filter(
                ngay__gte=start_date,
                ngay__lte=end_date,
                ngay__week_day=(i + 2) % 7 + 1  # Django sử dụng 1-7 cho thứ 2 đến CN
            ).count()
            
            # Tính tỷ lệ trúng cho từng giá trị chạm trong ngày này
            cham_hit_rates = {}
            for j in range(10):
                value = str(j)
                cham_records = model.objects.filter(
                    ngay__gte=start_date,
                    ngay__lte=end_date,
                    cham_value=value,
                    ngay__week_day=(i + 2) % 7 + 1
                )
                
                cham_total = cham_records.count()
                cham_hits = cham_records.filter(has_hit=True).count()
                hit_rate = (cham_hits / cham_total) * 100 if cham_total > 0 else 0
                
                cham_hit_rates[value] = {
                    'total': cham_total,
                    'hits': cham_hits,
                    'hit_rate': hit_rate
                }
            
            # Tìm giá trị chạm có tỷ lệ trúng cao nhất
            best_cham = max(cham_hit_rates.items(), key=lambda x: x[1]['hit_rate']) if cham_hit_rates else None
            
            weekday_stats.append({
                'weekday': weekdays[i],
                'total': total,
                'cham_hit_rates': cham_hit_rates,
                'best_cham': best_cham
            })
        
        return weekday_stats
    
    def _get_month_analysis(self, cham_type, start_date, end_date):
        """Phân tích tỷ lệ trúng theo tháng"""
        model = ChamDau if cham_type == 'dau' else ChamDuoi
        months = ['Tháng 1', 'Tháng 2', 'Tháng 3', 'Tháng 4', 'Tháng 5', 'Tháng 6', 
                  'Tháng 7', 'Tháng 8', 'Tháng 9', 'Tháng 10', 'Tháng 11', 'Tháng 12']
        month_stats = []
        
        # Lấy dữ liệu các tháng từ start_date đến end_date
        current_date = start_date
        while current_date <= end_date:
            month = current_date.month
            year = current_date.year
            
            month_start = datetime(year, month, 1).date()
            if month == 12:
                month_end = datetime(year + 1, 1, 1).date() - timedelta(days=1)
            else:
                month_end = datetime(year, month + 1, 1).date() - timedelta(days=1)
            
            # Điều chỉnh nếu vượt quá end_date
            month_end = min(month_end, end_date)
            
            # Tính tổng số kết quả cho tháng này
            total = KetQuaXoSo.objects.filter(
                ngay__gte=month_start,
                ngay__lte=month_end
            ).count()
            
            # Tính tỷ lệ trúng cho từng giá trị chạm trong tháng này
            cham_hit_rates = {}
            for j in range(10):
                value = str(j)
                cham_records = model.objects.filter(
                    ngay__gte=month_start,
                    ngay__lte=month_end,
                    cham_value=value
                )
                
                cham_total = cham_records.count()
                cham_hits = cham_records.filter(has_hit=True).count()
                hit_rate = (cham_hits / cham_total) * 100 if cham_total > 0 else 0
                
                cham_hit_rates[value] = {
                    'total': cham_total,
                    'hits': cham_hits,
                    'hit_rate': hit_rate
                }
            
            # Tìm giá trị chạm có tỷ lệ trúng cao nhất
            best_cham = max(cham_hit_rates.items(), key=lambda x: x[1]['hit_rate']) if cham_hit_rates else None
            
            month_stats.append({
                'month': months[month - 1],
                'year': year,
                'month_start': month_start,
                'month_end': month_end,
                'total': total,
                'cham_hit_rates': cham_hit_rates,
                'best_cham': best_cham
            })
            
            # Di chuyển đến tháng tiếp theo
            if month == 12:
                current_date = datetime(year + 1, 1, 1).date()
            else:
                current_date = datetime(year, month + 1, 1).date()
        
        return month_stats
    
    def _get_recent_results(self, cham_type, start_date, end_date):
        """Lấy kết quả gần đây nhất"""
        model = ChamDau if cham_type == 'dau' else ChamDuoi
        
        # Lấy 10 kết quả gần đây nhất
        recent = model.objects.filter(
            ngay__gte=start_date,
            ngay__lte=end_date,
            has_hit=True
        ).order_by('-ngay')[:10]
        
        return recent
    
    def _get_trend_analysis(self, cham_type, start_date, end_date):
        """Phân tích xu hướng theo thời gian"""
        model = ChamDau if cham_type == 'dau' else ChamDuoi
        
        # Tạo danh sách ngày từ start_date đến end_date
        days = []
        current_date = start_date
        while current_date <= end_date:
            days.append(current_date)
            current_date += timedelta(days=1)
        
        # Tính tỷ lệ trúng cho từng ngày
        daily_hit_rates = []
        for day in days:
            records = model.objects.filter(ngay=day)
            total = records.count()
            hits = records.filter(has_hit=True).count()
            hit_rate = (hits / total) * 100 if total > 0 else 0
            
            daily_hit_rates.append({
                'date': day,
                'total': total,
                'hits': hits,
                'hit_rate': hit_rate
            })
        
        # Tính xu hướng (tăng/giảm)
        if len(daily_hit_rates) >= 7:
            recent_7_days = daily_hit_rates[-7:]
            avg_recent = sum(day['hit_rate'] for day in recent_7_days) / 7
            
            prev_7_days = daily_hit_rates[-14:-7]
            avg_prev = sum(day['hit_rate'] for day in prev_7_days) / 7 if prev_7_days else 0
            
            trend = avg_recent - avg_prev
            trend_direction = "tăng" if trend > 0 else "giảm" if trend < 0 else "ổn định"
        else:
            trend = 0
            trend_direction = "không đủ dữ liệu"
        
        return {
            'daily_hit_rates': daily_hit_rates,
            'trend': trend,
            'trend_direction': trend_direction
        }
    
class ChamDetailView(DetailView):
    """Trang chi tiết một giá trị chạm cụ thể"""
    template_name = 'chamde/detail.html'
    context_object_name = 'cham_detail'
    
    def get_object(self):
        cham_type = self.kwargs.get('cham_type')
        cham_value = self.kwargs.get('cham_value')
        
        # Lấy khoảng thời gian từ query params hoặc mặc định
        days = int(self.request.GET.get('days', 30))
        end_date = timezone.now().date()
        start_date = end_date - timedelta(days=days)
        
        # Tạo đối tượng chi tiết
        detail = {
            'type': cham_type,
            'value': cham_value,
            'start_date': start_date,
            'end_date': end_date,
            'days': days
        }
        
        # Lấy dữ liệu dựa trên loại chạm
        if cham_type == 'dau':
            model = ChamDau
            detail['type_name'] = 'Chạm Đầu'
            detail['description'] = f'Các cặp số có chữ số đầu là {cham_value}'
            detail['numbers'] = generate_cham_dau_numbers(cham_value)
        elif cham_type == 'duoi':
            model = ChamDuoi
            detail['type_name'] = 'Chạm Đuôi'
            detail['description'] = f'Các cặp số có chữ số cuối là {cham_value}'
            detail['numbers'] = generate_cham_duoi_numbers(cham_value)
        else:
            raise Http404("Loại chạm không hợp lệ")
        
        # Lấy thống kê
        queryset = model.objects.filter(
            ngay__gte=start_date,
            ngay__lte=end_date,
            cham_value=cham_value
        ).order_by('-ngay')
        
        total = queryset.count()
        hits = queryset.filter(has_hit=True).count()
        hit_rate = (hits / total) * 100 if total > 0 else 0
        
        detail.update({
            'records': queryset,
            'total': total,
            'hits': hits,
            'hit_rate': hit_rate
        })
        
        # Lấy lịch sử xuất hiện
        hit_history = []
        current_streak = 0
        for record in queryset:
            if record.has_hit:
                current_streak += 1
            else:
                current_streak = 0
            
            hit_history.append({
                'date': record.ngay,
                'has_hit': record.has_hit,
                'streak': current_streak if record.has_hit else 0,
                'appeared': record.appeared_numbers
            })
        
        detail['hit_history'] = hit_history
        
        # Tính chu kỳ trúng
        if hits > 1:
            hit_dates = list(queryset.filter(has_hit=True).values_list('ngay', flat=True).order_by('ngay'))
            days_between = [(hit_dates[i] - hit_dates[i-1]).days for i in range(1, len(hit_dates))]
            avg_days_between_hits = sum(days_between) / len(days_between)
            
            # Dự đoán ngày trúng tiếp theo
            last_hit_date = hit_dates[-1]
            next_hit_date = last_hit_date + timedelta(days=int(avg_days_between_hits))
            
            detail.update({
                'avg_days_between_hits': avg_days_between_hits,
                'next_hit_date': next_hit_date,
                'days_until_next_hit': (next_hit_date - end_date).days
            })
        
        # Phân tích theo ngày trong tuần
        weekday_stats = [0] * 7
        weekday_hits = [0] * 7
        for record in queryset:
            weekday = record.ngay.weekday()
            weekday_stats[weekday] += 1
            if record.has_hit:
                weekday_hits[weekday] += 1
        
        weekday_hit_rates = []
        for i in range(7):
            rate = (weekday_hits[i] / weekday_stats[i]) * 100 if weekday_stats[i] > 0 else 0
            weekday_hit_rates.append({
                'weekday': ['Thứ Hai', 'Thứ Ba', 'Thứ Tư', 'Thứ Năm', 'Thứ Sáu', 'Thứ Bảy', 'Chủ Nhật'][i],
                'total': weekday_stats[i],
                'hits': weekday_hits[i],
                'hit_rate': rate
            })
        
        detail['weekday_hit_rates'] = weekday_hit_rates
        
        # Tìm các số xuất hiện nhiều nhất trong dàn chạm này
        appeared_numbers = []
        for record in queryset:
            appeared_numbers.extend(record.appeared_numbers)
        
        # Đếm số lần xuất hiện của mỗi số
        number_counts = {}
        for num in appeared_numbers:
            if num in number_counts:
                number_counts[num] += 1
            else:
                number_counts[num] = 1
        
        # Sắp xếp theo số lần xuất hiện
        top_numbers = sorted(number_counts.items(), key=lambda x: x[1], reverse=True)[:10]
        detail['top_numbers'] = top_numbers
        
        return detail
    
class ChamPredictionView(TemplateView):
    """Trang dự đoán dựa trên phân tích chạm"""
    template_name = 'chamde/prediction.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        today = timezone.now().date()
        tomorrow = today + timedelta(days=1)
        
        # Lấy phương pháp dự đoán từ query params hoặc mặc định
        method = self.request.GET.get('method', 'all')
        
        # Lấy ngày dự đoán từ query params hoặc mặc định
        target_date_str = self.request.GET.get('target_date', None)
        if target_date_str:
            try:
                target_date = datetime.strptime(target_date_str, '%Y-%m-%d').date()
            except ValueError:
                target_date = tomorrow
        else:
            target_date = tomorrow
        
        # Tạo dự đoán dựa trên phương pháp được chọn
        if method == 'all':
            # Sử dụng tất cả các phương pháp
            predictions = self._get_all_predictions(target_date)
            
            # Tính điểm tổng hợp cho từng số
            number_scores = self._calculate_combined_scores(predictions)
            
            # Sắp xếp theo điểm giảm dần
            sorted_numbers = sorted(number_scores.items(), key=lambda x: x[1], reverse=True)
            top_numbers = [num for num, score in sorted_numbers[:10]]
            
            context.update({
                'prediction_method': 'all',
                'method_name': 'Tất cả phương pháp',
                'predictions': predictions,
                'number_scores': sorted_numbers[:20],  # Top 20 số có điểm cao nhất
                'top_numbers': top_numbers,
            })
        else:
            # Sử dụng một phương pháp cụ thể
            prediction = self._get_prediction_by_method(method, target_date)
            context.update({
                'prediction_method': method,
                'method_name': prediction.get('method_name', 'Phương pháp không xác định'),
                'prediction': prediction,
            })
        
        # Thêm dữ liệu cơ bản vào context
        context.update({
            'today': today,
            'tomorrow': tomorrow,
            'target_date': target_date,
        })
        
        return context
    
    def _get_all_predictions(self, target_date):
        """Lấy dự đoán từ tất cả các phương pháp"""
        predictions = {}
        
        # 1. Dự đoán từ chạm đầu
        predictions['cham_dau'] = self._predict_cham_dau(target_date)
        
        # 2. Dự đoán từ chạm đuôi
        predictions['cham_duoi'] = self._predict_cham_duoi(target_date)
        
        # 3. Dự đoán từ cầu chạm kiểu 1
        predictions['cau_cham1'] = self._predict_cau_cham1(target_date)
        
        # 4. Dự đoán từ cầu chạm kiểu 2
        predictions['cau_cham2'] = self._predict_cau_cham2(target_date)
        
        # 5. Dự đoán từ mẫu quả trám
        predictions['qua_tram'] = self._predict_qua_tram(target_date)
        
        # 6. Dự đoán từ lô gan
        predictions['lo_gan'] = self._predict_lo_gan(target_date)
        
        return predictions
    
    def _calculate_combined_scores(self, predictions):
        """Tính điểm tổng hợp cho từng số dựa trên các dự đoán"""
        # Trọng số cho từng phương pháp
        weights = {
            'cham_dau': 0.2,
            'cham_duoi': 0.2,
            'cau_cham1': 0.25,
            'cau_cham2': 0.15,
            'qua_tram': 0.1,
            'lo_gan': 0.1,
        }
        
        # Tính điểm cho từng số
        number_scores = {}
        
        for method, prediction in predictions.items():
            weight = weights.get(method, 0.1)  # Trọng số mặc định
            confidence = prediction.get('confidence', 50) / 100  # Chuyển đổi từ phần trăm sang tỷ lệ
            
            for number in prediction.get('numbers', []):
                if number in number_scores:
                    number_scores[number] += weight * confidence
                else:
                    number_scores[number] = weight * confidence
        
        return number_scores
    
    def _get_prediction_by_method(self, method, target_date):
        """Lấy dự đoán từ một phương pháp cụ thể"""
        if method == 'cham_dau':
            return self._predict_cham_dau(target_date)
        elif method == 'cham_duoi':
            return self._predict_cham_duoi(target_date)
        elif method == 'cau_cham1':
            return self._predict_cau_cham1(target_date)
        elif method == 'cau_cham2':
            return self._predict_cau_cham2(target_date)
        elif method == 'qua_tram':
            return self._predict_qua_tram(target_date)
        elif method == 'lo_gan':
            return self._predict_lo_gan(target_date)
        else:
            return {
                'method': method,
                'method_name': 'Phương pháp không hỗ trợ',
                'numbers': [],
                'confidence': 0,
                'description': 'Phương pháp này không được hỗ trợ.'
            }
    
    def _predict_cham_dau(self, target_date):
        """Dự đoán dựa trên phân tích chạm đầu"""
        today = timezone.now().date()
        
        # Tính tỷ lệ trúng của từng giá trị chạm đầu trong 30 ngày qua
        start_date = today - timedelta(days=30)
        hit_rates = {}
        
        for i in range(10):
            value = str(i)
            queryset = ChamDau.objects.filter(
                ngay__gte=start_date,
                ngay__lte=today,
                cham_value=value
            )
            
            total = queryset.count()
            hits = queryset.filter(has_hit=True).count()
            hit_rate = (hits / total) * 100 if total > 0 else 0
            
            hit_rates[value] = hit_rate
        
        # Sắp xếp theo tỷ lệ trúng giảm dần
        sorted_hit_rates = sorted(hit_rates.items(), key=lambda x: x[1], reverse=True)
        
        # Lấy top 3 chạm có tỷ lệ trúng cao nhất
        top_chams = [value for value, rate in sorted_hit_rates[:3]]
        
        # Tạo danh sách số dự đoán từ các chạm này
        numbers = []
        for cham in top_chams:
            numbers.extend(generate_cham_dau_numbers(cham))
        
        # Loại bỏ trùng lặp
        numbers = list(set(numbers))
        
        # Tính độ tin cậy dựa trên tỷ lệ trúng trung bình của top 3 chạm
        avg_hit_rate = sum(hit_rates[cham] for cham in top_chams) / len(top_chams)
        
        return {
            'method': 'cham_dau',
            'method_name': 'Chạm Đầu',
            'numbers': numbers,
            'confidence': min(avg_hit_rate, 100),  # Giới hạn tối đa 100%
            'top_chams': [{'value': value, 'hit_rate': rate} for value, rate in sorted_hit_rates[:3]],
            'description': 'Dự đoán dựa trên tỷ lệ trúng của chạm đầu trong 30 ngày qua.'
        }
    
    def _predict_cham_duoi(self, target_date):
        """Dự đoán dựa trên phân tích chạm đuôi"""
        today = timezone.now().date()
        
        # Tính tỷ lệ trúng của từng giá trị chạm đuôi trong 30 ngày qua
        start_date = today - timedelta(days=30)
        hit_rates = {}
        
        for i in range(10):
            value = str(i)
            queryset = ChamDuoi.objects.filter(
                ngay__gte=start_date,
                ngay__lte=today,
                cham_value=value
            )
            
            total = queryset.count()
            hits = queryset.filter(has_hit=True).count()
            hit_rate = (hits / total) * 100 if total > 0 else 0
            
            hit_rates[value] = hit_rate
        
        # Sắp xếp theo tỷ lệ trúng giảm dần
        sorted_hit_rates = sorted(hit_rates.items(), key=lambda x: x[1], reverse=True)
        
        # Lấy top 3 chạm có tỷ lệ trúng cao nhất
        top_chams = [value for value, rate in sorted_hit_rates[:3]]
        
        # Tạo danh sách số dự đoán từ các chạm này
        numbers = []
        for cham in top_chams:
            numbers.extend(generate_cham_duoi_numbers(cham))
        
        # Loại bỏ trùng lặp
        numbers = list(set(numbers))
        
        # Tính độ tin cậy dựa trên tỷ lệ trúng trung bình của top 3 chạm
        avg_hit_rate = sum(hit_rates[cham] for cham in top_chams) / len(top_chams)
        
        return {
            'method': 'cham_duoi',
            'method_name': 'Chạm Đuôi',
            'numbers': numbers,
            'confidence': min(avg_hit_rate, 100),  # Giới hạn tối đa 100%
            'top_chams': [{'value': value, 'hit_rate': rate} for value, rate in sorted_hit_rates[:3]],
            'description': 'Dự đoán dựa trên tỷ lệ trúng của chạm đuôi trong 30 ngày qua.'
        }
    
    def _predict_cau_cham1(self, target_date):
        """Dự đoán dựa trên cầu chạm kiểu 1 (giải nhất Chủ Nhật)"""
        today = timezone.now().date()
        
        # Tìm Chủ Nhật gần nhất
        days_since_sunday = (today.weekday() + 1) % 7  # 0 là thứ hai, 6 là chủ nhật
        last_sunday = today - timedelta(days=days_since_sunday)
        
        # Lấy phân tích chạm cho Chủ Nhật
        analysis = ChamAnalysis.objects.filter(ngay=last_sunday).first()
        
        if analysis and analysis.cau_cham1_value:
            # Lấy giá trị chạm từ giải nhất
            cham_value = analysis.cau_cham1_value
            
            # Tạo danh sách số dự đoán từ chạm này
            numbers = generate_cham_dau_numbers(cham_value)
            
            # Tính tỷ lệ trúng lịch sử của phương pháp này
            start_date = today - timedelta(days=90)  # 3 tháng
            
            # Lấy tất cả các phân tích chạm của các Chủ Nhật trong khoảng thời gian
            sunday_analyses = ChamAnalysis.objects.filter(
                ngay__gte=start_date,
                ngay__lte=today,
                is_sunday=True
            ).exclude(cau_cham1_value__isnull=True)
            
            # Đếm số lần phương pháp này trúng trong tuần tiếp theo
            hits = 0
            total = sunday_analyses.count()
            
            for analysis in sunday_analyses:
                # Lấy kết quả trong tuần tiếp theo
                week_start = analysis.ngay + timedelta(days=1)
                week_end = week_start + timedelta(days=6)
                
                # Lấy tất cả kết quả xổ số trong tuần
                week_results = KetQuaXoSo.objects.filter(
                    ngay__gte=week_start,
                    ngay__lte=week_end
                )
                
                # Kiểm tra xem có kết quả nào trúng chạm không
                for result in week_results:
                    db_last2 = result.giai_db[-2:] if len(result.giai_db) >= 2 else ''
                    if db_last2 and db_last2[0] == analysis.cau_cham1_value:
                        hits += 1
                        break
            
            # Tính tỷ lệ trúng
            hit_rate = (hits / total) * 100 if total > 0 else 0
            
            return {
                'method': 'cau_cham1',
                'method_name': 'Cầu Chạm Kiểu 1',
                'numbers': numbers,
                'confidence': min(hit_rate, 100),  # Giới hạn tối đa 100%
                'cham_value': cham_value,
                'source_date': last_sunday,
                'historical_hit_rate': hit_rate,
                'description': 'Dự đoán dựa trên chữ số giữa của giải nhất ngày Chủ Nhật.'
            }
        else:
            # Không có dữ liệu hoặc không tìm thấy giá trị chạm
            return {
                'method': 'cau_cham1',
                'method_name': 'Cầu Chạm Kiểu 1',
                'numbers': [],
                'confidence': 0,
                'description': 'Không có dữ liệu hoặc không tìm thấy giá trị chạm từ giải nhất Chủ Nhật gần nhất.'
            }
    
    def _predict_cau_cham2(self, target_date):
        """Dự đoán dựa trên cầu chạm kiểu 2 (tổng đề CN + đuôi đề thứ 6)"""
        today = timezone.now().date()
        
        # Tìm Chủ Nhật gần nhất
        days_since_sunday = (today.weekday() + 1) % 7
        last_sunday = today - timedelta(days=days_since_sunday)
        
        # Lấy phân tích chạm cho Chủ Nhật
        analysis = ChamAnalysis.objects.filter(ngay=last_sunday).first()
        
        if analysis and analysis.cau_cham2_value:
            # Lấy giá trị cầu chạm kiểu 2
            cau_cham2_value = analysis.cau_cham2_value
            
            # Tính tỷ lệ trúng lịch sử của phương pháp này
            start_date = today - timedelta(days=90)  # 3 tháng
            
            # Lấy tất cả các phân tích chạm của các Chủ Nhật trong khoảng thời gian
            sunday_analyses = ChamAnalysis.objects.filter(
                ngay__gte=start_date,
                ngay__lte=today,
                is_sunday=True
            ).exclude(cau_cham2_value__isnull=True)
            
            # Đếm số lần phương pháp này trúng trong tuần tiếp theo
            hits = 0
            total = sunday_analyses.count()
            
            for analysis in sunday_analyses:
                # Lấy kết quả trong tuần tiếp theo
                week_start = analysis.ngay + timedelta(days=1)
                week_end = week_start + timedelta(days=6)
                
                # Lấy tất cả kết quả xổ số trong tuần
                week_results = KetQuaXoSo.objects.filter(
                    ngay__gte=week_start,
                    ngay__lte=week_end
                )
                
                # Kiểm tra xem có kết quả nào trúng cầu chạm kiểu 2 không
                for result in week_results:
                    db_last2 = result.giai_db[-2:] if len(result.giai_db) >= 2 else ''
                    if db_last2 == analysis.cau_cham2_value:
                        hits += 1
                        break
            
            # Tính tỷ lệ trúng
            hit_rate = (hits / total) * 100 if total > 0 else 0
            
            return {
                'method': 'cau_cham2',
                'method_name': 'Cầu Chạm Kiểu 2',
                'numbers': [cau_cham2_value],
                'confidence': min(hit_rate, 100),  # Giới hạn tối đa 100%
                'cau_cham2_value': cau_cham2_value,
                'source_date': last_sunday,
                'historical_hit_rate': hit_rate,
                'description': 'Dự đoán dựa trên tổng giải đặc biệt Chủ Nhật + đuôi giải đặc biệt thứ 6.'
            }
        else:
            # Không có dữ liệu hoặc không tìm thấy giá trị cầu chạm kiểu 2
            return {
                'method': 'cau_cham2',
                'method_name': 'Cầu Chạm Kiểu 2',
                'numbers': [],
                'confidence': 0,
                'description': 'Không có dữ liệu hoặc không tìm thấy giá trị cầu chạm kiểu 2 từ Chủ Nhật gần nhất.'
            }
    
    def _predict_qua_tram(self, target_date):
        """Dự đoán dựa trên mẫu quả trám"""
        today = timezone.now().date()
        
        # Lấy các mẫu quả trám được phát hiện trong 7 ngày qua
        start_date = today - timedelta(days=7)
        patterns = QuaTramPattern.objects.filter(
            ngay__gte=start_date,
            ngay__lte=today
        ).order_by('-ngay')
        
        if patterns:
            # Lấy số dự đoán từ các mẫu quả trám
            numbers = list(patterns.values_list('predicted_number', flat=True))
            
            # Loại bỏ trùng lặp
            numbers = list(set(numbers))
            
            # Tính tỷ lệ trúng lịch sử của phương pháp này
            historical_patterns = QuaTramPattern.objects.filter(
                ngay__lte=today - timedelta(days=6)  # Đảm bảo đã qua 5 ngày để kiểm tra
            )
            
            total = historical_patterns.count()
            hits = historical_patterns.filter(has_hit=True).count()
            hit_rate = (hits / total) * 100 if total > 0 else 0
            
            return {
                'method': 'qua_tram',
                'method_name': 'Mẫu Quả Trám',
                'numbers': numbers,
                'confidence': min(hit_rate, 100),  # Giới hạn tối đa 100%
                'patterns': list(patterns.values('ngay', 'predicted_number', 'digit_top', 'digit_mid_left', 'digit_mid_right', 'digit_bottom')),
                'historical_hit_rate': hit_rate,
                'description': 'Dự đoán dựa trên các mẫu quả trám được phát hiện trong 7 ngày qua.'
            }
        else:
            # Không có mẫu quả trám nào được phát hiện
            return {
                'method': 'qua_tram',
                'method_name': 'Mẫu Quả Trám',
                'numbers': [],
                'confidence': 0,
                'description': 'Không có mẫu quả trám nào được phát hiện trong 7 ngày qua.'
            }
    
    def _predict_lo_gan(self, target_date):
        """Dự đoán dựa trên lô gan"""
        today = timezone.now().date()
        
        # Lấy top 10 số có xác suất sắp về cao nhất
        lo_gan_stats = LoGanStats.objects.filter(
            date=today
        ).order_by('-due_probability')[:10]
        
        if lo_gan_stats:
            # Lấy số dự đoán từ lô gan
            numbers = list(lo_gan_stats.values_list('number', flat=True))
            
            # Tính độ tin cậy dựa trên xác suất trung bình
            avg_probability = lo_gan_stats.aggregate(Avg('due_probability'))['due_probability__avg']
            
            return {
                'method': 'lo_gan',
                'method_name': 'Lô Gan',
                'numbers': numbers,
                'confidence': min(avg_probability, 100),  # Giới hạn tối đa 100%
                'lo_gan_stats': list(lo_gan_stats.values('number', 'current_absent_days', 'due_probability')),
                'description': 'Dự đoán dựa trên các số lô gan có xác suất sắp về cao nhất.'
            }
        else:
            # Không có dữ liệu lô gan
            return {
                'method': 'lo_gan',
                'method_name': 'Lô Gan',
                'numbers': [],
                'confidence': 0,
                'description': 'Không có dữ liệu lô gan cho ngày hôm nay.'
            }

class ChamSuggestionView(TemplateView):
    """Trang gợi ý cá nhân dựa trên lịch sử và sở thích"""
    template_name = 'chamde/suggestion.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        today = timezone.now().date()
        tomorrow = today + timedelta(days=1)
        
        # Lấy các phương pháp dự đoán
        prediction_view = ChamPredictionView()
        all_predictions = prediction_view._get_all_predictions(tomorrow)
        
        # Lấy thông tin về lịch sử hiệu suất của từng phương pháp
        method_performance = self._get_method_performance()
        
        # Áp dụng trọng số dựa trên hiệu suất
        weighted_scores = self._calculate_weighted_scores(all_predictions, method_performance)
        
        # Sắp xếp các số theo điểm
        sorted_numbers = sorted(weighted_scores.items(), key=lambda x: x[1], reverse=True)
        
        # Phân loại các số
        top_10_percent = int(len(sorted_numbers) * 0.1) or 1
        top_numbers = sorted_numbers[:top_10_percent]
        good_numbers = sorted_numbers[top_10_percent:int(len(sorted_numbers) * 0.3)]
        average_numbers = sorted_numbers[int(len(sorted_numbers) * 0.3):int(len(sorted_numbers) * 0.7)]
        
        # Tạo gợi ý cá nhân
        personal_suggestions = self._create_personal_suggestions(sorted_numbers, method_performance)
        
        # Thêm dữ liệu vào context
        context.update({
            'today': today,
            'tomorrow': tomorrow,
            'all_predictions': all_predictions,
            'method_performance': method_performance,
            'top_numbers': top_numbers,
            'good_numbers': good_numbers,
            'average_numbers': average_numbers,
            'personal_suggestions': personal_suggestions,
        })
        
        return context
    
    def _get_method_performance(self):
        """Lấy thông tin về hiệu suất của từng phương pháp trong 30 ngày qua"""
        today = timezone.now().date()
        start_date = today - timedelta(days=30)
        
        method_performance = {
            'cham_dau': {'name': 'Chạm Đầu', 'hits': 0, 'total': 0, 'hit_rate': 0},
            'cham_duoi': {'name': 'Chạm Đuôi', 'hits': 0, 'total': 0, 'hit_rate': 0},
            'cau_cham1': {'name': 'Cầu Chạm Kiểu 1', 'hits': 0, 'total': 0, 'hit_rate': 0},
            'cau_cham2': {'name': 'Cầu Chạm Kiểu 2', 'hits': 0, 'total': 0, 'hit_rate': 0},
            'qua_tram': {'name': 'Mẫu Quả Trám', 'hits': 0, 'total': 0, 'hit_rate': 0},
            'lo_gan': {'name': 'Lô Gan', 'hits': 0, 'total': 0, 'hit_rate': 0},
        }
        
        # Lấy kết quả dự đoán trong 30 ngày qua
        predictions = CauChamPrediction.objects.filter(
            ngay_du_doan__gte=start_date,
            ngay_du_doan__lte=today,
            ket_qua_thuc_te__isnull=False  # Đã có kết quả
        )
        
        # Tính hiệu suất cho từng phương pháp
        for prediction in predictions:
            method = prediction.phuong_phap
            if method in method_performance:
                method_performance[method]['total'] += 1
                if prediction.ket_qua_trung:
                    method_performance[method]['hits'] += 1
        
        # Tính tỷ lệ trúng
        for method, stats in method_performance.items():
            if stats['total'] > 0:
                stats['hit_rate'] = (stats['hits'] / stats['total']) * 100
        
        return method_performance
    
    def _calculate_weighted_scores(self, predictions, method_performance):
        """Tính điểm có trọng số cho từng số dựa trên hiệu suất của phương pháp"""
        number_scores = {}
        
        # Tính tổng điểm cho từng số
        for method, prediction in predictions.items():
            # Lấy hiệu suất của phương pháp
            performance = method_performance.get(method, {'hit_rate': 0})
            hit_rate = performance.get('hit_rate', 0)
            
            # Trọng số là tỷ lệ trúng của phương pháp
            weight = hit_rate / 100  # Chuyển đổi từ phần trăm sang tỷ lệ
            
            # Độ tin cậy của dự đoán
            confidence = prediction.get('confidence', 50) / 100
            
            # Tính điểm cho từng số
            for number in prediction.get('numbers', []):
                if number in number_scores:
                    number_scores[number] += weight * confidence
                else:
                    number_scores[number] = weight * confidence
        
        return number_scores
    
    def _create_personal_suggestions(self, sorted_numbers, method_performance):
        """Tạo gợi ý cá nhân dựa trên điểm và hiệu suất"""
        today = timezone.now().date()
        
        suggestions = []
        
        # 1. Dàn đề từ top 3 số
        if len(sorted_numbers) >= 3:
            top_3 = [num for num, _ in sorted_numbers[:3]]
            suggestions.append({
                'name': 'Dàn đề top 3',
                'numbers': top_3,
                'description': 'Đánh dàn đề với top 3 số có điểm cao nhất',
                'confidence': 'Cao'
            })
        
        # 2. Gợi ý dựa trên phương pháp có hiệu suất cao nhất
        best_method = max(method_performance.items(), key=lambda x: x[1]['hit_rate'])
        if best_method[1]['hit_rate'] > 0:
            method_name = best_method[0]
            prediction_view = ChamPredictionView()
            method_prediction = prediction_view._get_prediction_by_method(method_name, today + timedelta(days=1))
            
            if method_prediction and method_prediction.get('numbers'):
                suggestions.append({
                    'name': f'Theo phương pháp {best_method[1]["name"]}',
                    'numbers': method_prediction.get('numbers')[:5],  # Top 5 số
                    'description': f'Đánh theo phương pháp {best_method[1]["name"]} - hiệu suất cao nhất ({best_method[1]["hit_rate"]:.1f}%)',
                    'confidence': 'Cao' if best_method[1]["hit_rate"] > 70 else 'Trung bình'
                })
        
        # 3. Gợi ý dựa trên ngày trong tuần
        weekday = (today.weekday() + 1) % 7  # Ngày mai
        weekday_name = ['Thứ Hai', 'Thứ Ba', 'Thứ Tư', 'Thứ Năm', 'Thứ Sáu', 'Thứ Bảy', 'Chủ Nhật'][weekday]
        
        # Tìm chạm đầu và chạm đuôi có hiệu suất cao nhất cho ngày này
        best_cham_dau = self._get_best_cham_for_weekday('dau', weekday)
        best_cham_duoi = self._get_best_cham_for_weekday('duoi', weekday)
        
        if best_cham_dau:
            suggestions.append({
                'name': f'Chạm đầu cho {weekday_name}',
                'numbers': generate_cham_dau_numbers(best_cham_dau['value']),
                'description': f'Chạm đầu {best_cham_dau["value"]} có hiệu suất cao nhất cho {weekday_name} ({best_cham_dau["hit_rate"]:.1f}%)',
                'confidence': 'Trung bình'
            })
        
        if best_cham_duoi:
            suggestions.append({
                'name': f'Chạm đuôi cho {weekday_name}',
                'numbers': generate_cham_duoi_numbers(best_cham_duoi['value']),
                'description': f'Chạm đuôi {best_cham_duoi["value"]} có hiệu suất cao nhất cho {weekday_name} ({best_cham_duoi["hit_rate"]:.1f}%)',
                'confidence': 'Trung bình'
            })
        
        # 4. Kết hợp chạm đầu và chạm đuôi
        if best_cham_dau and best_cham_duoi:
            combined_number = best_cham_dau['value'] + best_cham_duoi['value']
            suggestions.append({
                'name': 'Kết hợp chạm đầu và chạm đuôi',
                'numbers': [combined_number],
                'description': f'Kết hợp chạm đầu {best_cham_dau["value"]} và chạm đuôi {best_cham_duoi["value"]}',
                'confidence': 'Cao' if combined_number in dict(sorted_numbers[:10]) else 'Trung bình'
            })
        
        return suggestions
    
    def _get_best_cham_for_weekday(self, cham_type, weekday):
        """Tìm giá trị chạm có hiệu suất cao nhất cho một ngày trong tuần"""
        today = timezone.now().date()
        start_date = today - timedelta(days=90)  # 3 tháng
        
        model = ChamDau if cham_type == 'dau' else ChamDuoi
        
        best_cham = None
        best_hit_rate = 0
        
        for i in range(10):
            value = str(i)
            queryset = model.objects.filter(
                ngay__gte=start_date,
                ngay__lte=today,
                cham_value=value,
                ngay__week_day=(weekday + 2) % 7 + 1  # Django sử dụng 1-7 cho thứ 2 đến CN
            )
            
            total = queryset.count()
            hits = queryset.filter(has_hit=True).count()
            hit_rate = (hits / total) * 100 if total > 0 else 0
            
            if hit_rate > best_hit_rate:
                best_hit_rate = hit_rate
                best_cham = {
                    'value': value,
                    'hit_rate': hit_rate,
                    'total': total,
                    'hits': hits
                }
        
        return best_cham
    
class ChamReportView(TemplateView):
    """Trang báo cáo tổng hợp về hiệu suất các phương pháp chạm"""
    template_name = 'chamde/report.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        today = timezone.now().date()
        
        # Lấy khoảng thời gian từ query params hoặc mặc định
        days = int(self.request.GET.get('days', 30))
        start_date = today - timedelta(days=days)
        
        # 1. Thống kê hiệu suất tổng hợp
        overall_stats = self._get_overall_stats(start_date, today)
        
        # 2. Thống kê hiệu suất theo phương pháp
        method_stats = self._get_method_stats(start_date, today)
        
        # 3. Thống kê hiệu suất theo ngày trong tuần
        weekday_stats = self._get_weekday_stats(start_date, today)
        
        # 4. Thống kê hiệu suất theo tháng
        month_stats = self._get_month_stats(start_date, today)
        
        # 5. Thống kê hiệu suất theo giá trị chạm
        cham_stats = self._get_cham_stats(start_date, today)
        
        # 6. Thống kê số xuất hiện nhiều nhất
        number_stats = self._get_number_stats(start_date, today)
        
        # Thêm dữ liệu vào context
        context.update({
            'today': today,
            'selected_days': days,
            'start_date': start_date,
            'overall_stats': overall_stats,
            'method_stats': method_stats,
            'weekday_stats': weekday_stats,
            'month_stats': month_stats,
            'cham_stats': cham_stats,
            'number_stats': number_stats,
        })
        
        return context
    
    def _get_overall_stats(self, start_date, end_date):
        """Lấy thống kê hiệu suất tổng hợp"""
        # Tổng số kết quả xổ số
        total_results = KetQuaXoSo.objects.filter(
            ngay__gte=start_date,
            ngay__lte=end_date
        ).count()
        
        # Tổng số dự đoán
        total_predictions = CauChamPrediction.objects.filter(
            ngay_du_doan__gte=start_date,
            ngay_du_doan__lte=end_date,
            ket_qua_thuc_te__isnull=False  # Đã có kết quả
        ).count()
        
        # Tổng số dự đoán trúng
        total_hits = CauChamPrediction.objects.filter(
            ngay_du_doan__gte=start_date,
            ngay_du_doan__lte=end_date,
            ket_qua_thuc_te__isnull=False,
            ket_qua_trung=True
        ).count()
        
        # Tỷ lệ trúng tổng thể
        overall_hit_rate = (total_hits / total_predictions) * 100 if total_predictions > 0 else 0
        
        # Tổng số mẫu quả trám
        total_qua_tram = QuaTramPattern.objects.filter(
            ngay__gte=start_date,
            ngay__lte=end_date
        ).count()
        
        # Tổng số mẫu quả trám trúng
        qua_tram_hits = QuaTramPattern.objects.filter(
            ngay__gte=start_date,
            ngay__lte=end_date,
            has_hit=True
        ).count()
        
        # Tỷ lệ trúng của mẫu quả trám
        qua_tram_hit_rate = (qua_tram_hits / total_qua_tram) * 100 if total_qua_tram > 0 else 0
        
        return {
            'total_results': total_results,
            'total_predictions': total_predictions,
            'total_hits': total_hits,
            'overall_hit_rate': overall_hit_rate,
            'total_qua_tram': total_qua_tram,
            'qua_tram_hits': qua_tram_hits,
            'qua_tram_hit_rate': qua_tram_hit_rate
        }
    
    def _get_method_stats(self, start_date, end_date):
        """Lấy thống kê hiệu suất theo phương pháp"""
        method_stats = {}
        
        # Các phương pháp dự đoán
        methods = {
            'cham_dau': 'Chạm Đầu',
            'cham_duoi': 'Chạm Đuôi',
            'cau_cham1': 'Cầu Chạm Kiểu 1',
            'cau_cham2': 'Cầu Chạm Kiểu 2',
            'qua_tram': 'Mẫu Quả Trám',
            'lo_gan': 'Lô Gan'
        }
        
        # Tính hiệu suất cho từng phương pháp
        for method_code, method_name in methods.items():
            # Tổng số dự đoán
            total = CauChamPrediction.objects.filter(
                ngay_du_doan__gte=start_date,
                ngay_du_doan__lte=end_date,
                phuong_phap=method_code,
                ket_qua_thuc_te__isnull=False
            ).count()
            
            # Tổng số dự đoán trúng
            hits = CauChamPrediction.objects.filter(
                ngay_du_doan__gte=start_date,
                ngay_du_doan__lte=end_date,
                phuong_phap=method_code,
                ket_qua_thuc_te__isnull=False,
                ket_qua_trung=True
            ).count()
            
            # Tỷ lệ trúng
            hit_rate = (hits / total) * 100 if total > 0 else 0
            
            method_stats[method_code] = {
                'name': method_name,
                'total': total,
                'hits': hits,
                'hit_rate': hit_rate
            }
        
        return method_stats
    
    def _get_weekday_stats(self, start_date, end_date):
        """Lấy thống kê hiệu suất theo ngày trong tuần"""
        weekdays = ['Thứ Hai', 'Thứ Ba', 'Thứ Tư', 'Thứ Năm', 'Thứ Sáu', 'Thứ Bảy', 'Chủ Nhật']
        weekday_stats = []
        
        for i in range(7):
            # Lấy tất cả dự đoán cho ngày này trong tuần
            predictions = CauChamPrediction.objects.filter(
                ngay_du_doan__gte=start_date,
                ngay_du_doan__lte=end_date,
                ngay_du_doan__week_day=(i + 2) % 7 + 1,  # Django sử dụng 1-7 cho thứ 2 đến CN
                ket_qua_thuc_te__isnull=False
            )
            
            total = predictions.count()
            hits = predictions.filter(ket_qua_trung=True).count()
            hit_rate = (hits / total) * 100 if total > 0 else 0
            
            # Tính hiệu suất cho từng phương pháp trong ngày này
            method_hit_rates = {}
            for method in ['cham_dau', 'cham_duoi', 'cau_cham1', 'cau_cham2', 'qua_tram', 'lo_gan']:
                method_preds = predictions.filter(phuong_phap=method)
                method_total = method_preds.count()
                method_hits = method_preds.filter(ket_qua_trung=True).count()
                method_hit_rate = (method_hits / method_total) * 100 if method_total > 0 else 0
                
                method_hit_rates[method] = {
                    'total': method_total,
                    'hits': method_hits,
                    'hit_rate': method_hit_rate
                }
            
            # Tìm phương pháp có hiệu suất cao nhất
            best_method = max(method_hit_rates.items(), key=lambda x: x[1]['hit_rate']) if method_hit_rates else None
            
            weekday_stats.append({
                'weekday': weekdays[i],
                'total': total,
                'hits': hits,
                'hit_rate': hit_rate,
                'method_hit_rates': method_hit_rates,
                'best_method': best_method
            })
        
        return weekday_stats
    
    def _get_month_stats(self, start_date, end_date):
        """Lấy thống kê hiệu suất theo tháng"""
        months = ['Tháng 1', 'Tháng 2', 'Tháng 3', 'Tháng 4', 'Tháng 5', 'Tháng 6', 
                 'Tháng 7', 'Tháng 8', 'Tháng 9', 'Tháng 10', 'Tháng 11', 'Tháng 12']
        month_stats = []
        
        # Lấy dữ liệu các tháng từ start_date đến end_date
        current_date = start_date
        while current_date <= end_date:
            month = current_date.month
            year = current_date.year
            
            month_start = datetime(year, month, 1).date()
            if month == 12:
                month_end = datetime(year + 1, 1, 1).date() - timedelta(days=1)
            else:
                month_end = datetime(year, month + 1, 1).date() - timedelta(days=1)
            
            # Điều chỉnh nếu vượt quá end_date
            month_end = min(month_end, end_date)
            
            # Lấy tất cả dự đoán cho tháng này
            predictions = CauChamPrediction.objects.filter(
                ngay_du_doan__gte=month_start,
                ngay_du_doan__lte=month_end,
                ket_qua_thuc_te__isnull=False
            )
            
            total = predictions.count()
            hits = predictions.filter(ket_qua_trung=True).count()
            hit_rate = (hits / total) * 100 if total > 0 else 0
            
            # Tính hiệu suất cho từng phương pháp trong tháng này
            method_hit_rates = {}
            for method in ['cham_dau', 'cham_duoi', 'cau_cham1', 'cau_cham2', 'qua_tram', 'lo_gan']:
                method_preds = predictions.filter(phuong_phap=method)
                method_total = method_preds.count()
                method_hits = method_preds.filter(ket_qua_trung=True).count()
                method_hit_rate = (method_hits / method_total) * 100 if method_total > 0 else 0
                
                method_hit_rates[method] = {
                    'total': method_total,
                    'hits': method_hits,
                    'hit_rate': method_hit_rate
                }
            
            # Tìm phương pháp có hiệu suất cao nhất
            best_method = max(method_hit_rates.items(), key=lambda x: x[1]['hit_rate']) if method_hit_rates else None
            
            month_stats.append({
                'month': months[month - 1],
                'year': year,
                'month_start': month_start,
                'month_end': month_end,
                'total': total,
                'hits': hits,
                'hit_rate': hit_rate,
                'method_hit_rates': method_hit_rates,
                'best_method': best_method
            })
            
            # Di chuyển đến tháng tiếp theo
            if month == 12:
                current_date = datetime(year + 1, 1, 1).date()
            else:
                current_date = datetime(year, month + 1, 1).date()
        
        return month_stats
    
    def _get_cham_stats(self, start_date, end_date):
        """Lấy thống kê hiệu suất theo giá trị chạm"""
        cham_stats = {
            'dau': {},
            'duoi': {}
        }
        
        # Thống kê cho chạm đầu
        for i in range(10):
            value = str(i)
            queryset = ChamDau.objects.filter(
                ngay__gte=start_date,
                ngay__lte=end_date,
                cham_value=value
            )
            
            total = queryset.count()
            hits = queryset.filter(has_hit=True).count()
            hit_rate = (hits / total) * 100 if total > 0 else 0
            
            cham_stats['dau'][value] = {
                'total': total,
                'hits': hits,
                'hit_rate': hit_rate
            }
        
        # Thống kê cho chạm đuôi
        for i in range(10):
            value = str(i)
            queryset = ChamDuoi.objects.filter(
                ngay__gte=start_date,
                ngay__lte=end_date,
                cham_value=value
            )
            
            total = queryset.count()
            hits = queryset.filter(has_hit=True).count()
            hit_rate = (hits / total) * 100 if total > 0 else 0
            
            cham_stats['duoi'][value] = {
                'total': total,
                'hits': hits,
                'hit_rate': hit_rate
            }
        
        # Tìm giá trị chạm có hiệu suất cao nhất
        best_cham_dau = max(cham_stats['dau'].items(), key=lambda x: x[1]['hit_rate'])
        best_cham_duoi = max(cham_stats['duoi'].items(), key=lambda x: x[1]['hit_rate'])
        
        cham_stats['best_cham_dau'] = {'value': best_cham_dau[0], 'stats': best_cham_dau[1]}
        cham_stats['best_cham_duoi'] = {'value': best_cham_duoi[0], 'stats': best_cham_duoi[1]}
        
        return cham_stats
    
    def _get_number_stats(self, start_date, end_date):
        """Lấy thống kê số xuất hiện nhiều nhất"""
        # Lấy tất cả số 2 chữ số xuất hiện trong khoảng thời gian
        results = KetQuaXoSo.objects.filter(
            ngay__gte=start_date,
            ngay__lte=end_date
        )
        
        # Đếm số lần xuất hiện của mỗi số
        number_counts = {}
        for result in results:
            numbers = result.get_all_2digit_numbers()
            for num in numbers:
                if num in number_counts:
                    number_counts[num] += 1
                else:
                    number_counts[num] = 1
        
        # Sắp xếp theo số lần xuất hiện
        sorted_numbers = sorted(number_counts.items(), key=lambda x: x[1], reverse=True)
        
        # Lấy top 20 số xuất hiện nhiều nhất
        top_numbers = sorted_numbers[:20]
        
        # Tính tỷ lệ xuất hiện
        total_results = results.count()
        for i, (num, count) in enumerate(top_numbers):
            appearance_rate = (count / total_results) * 100
            top_numbers[i] = (num, count, appearance_rate)
        
        return {
            'top_numbers': top_numbers,
            'total_results': total_results
        }

@require_POST
def cham_statistics_api(request):
    """API endpoint để lấy thống kê chạm"""
    try:
        data = json.loads(request.body)
        
        # Lấy thông tin từ request
        start_date_str = data.get('start_date')
        end_date_str = data.get('end_date')
        cham_type = data.get('cham_type', 'dau')
        
        # Chuyển đổi ngày
        try:
            start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
            end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()
        except (ValueError, TypeError):
            return JsonResponse({
                'success': False,
                'message': 'Định dạng ngày không hợp lệ'
            })
        
        # Lấy model dựa trên loại chạm
        model = ChamDau if cham_type == 'dau' else ChamDuoi
        
        # Tính thống kê cho từng giá trị chạm
        stats = {}
        for i in range(10):
            value = str(i)
            queryset = model.objects.filter(
                ngay__gte=start_date,
                ngay__lte=end_date,
                cham_value=value
            )
            
            total = queryset.count()
            hits = queryset.filter(has_hit=True).count()
            hit_rate = (hits / total) * 100 if total > 0 else 0
            
            stats[value] = {
                'total': total,
                'hits': hits,
                'hit_rate': hit_rate
            }
        
        # Tính thống kê theo ngày trong tuần
        weekday_stats = []
        for i in range(7):
            weekday_queryset = model.objects.filter(
                ngay__gte=start_date,
                ngay__lte=end_date,
                ngay__week_day=(i + 2) % 7 + 1
            )
            
            weekday_total = weekday_queryset.count()
            weekday_hits = weekday_queryset.filter(has_hit=True).count()
            weekday_hit_rate = (weekday_hits / weekday_total) * 100 if weekday_total > 0 else 0
            
            weekday_stats.append({
                'weekday': i,
                'weekday_name': ['Thứ Hai', 'Thứ Ba', 'Thứ Tư', 'Thứ Năm', 'Thứ Sáu', 'Thứ Bảy', 'Chủ Nhật'][i],
                'total': weekday_total,
                'hits': weekday_hits,
                'hit_rate': weekday_hit_rate
            })
        
        # Tính thống kê tổng hợp
        total = model.objects.filter(
            ngay__gte=start_date,
            ngay__lte=end_date
        ).count()
        
        hits = model.objects.filter(
            ngay__gte=start_date,
            ngay__lte=end_date,
            has_hit=True
        ).count()
        
        overall_hit_rate = (hits / total) * 100 if total > 0 else 0
        
        return JsonResponse({
            'success': True,
            'cham_type': cham_type,
            'start_date': start_date_str,
            'end_date': end_date_str,
            'stats': stats,
            'weekday_stats': weekday_stats,
            'overall': {
                'total': total,
                'hits': hits,
                'hit_rate': overall_hit_rate
            }
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Lỗi: {str(e)}'
        })

@require_POST
def cham_prediction_api(request):
    """API endpoint để lấy dự đoán chạm"""
    try:
        data = json.loads(request.body)
        
        # Lấy thông tin từ request
        target_date_str = data.get('target_date')
        method = data.get('method', 'all')
        
        # Chuyển đổi ngày
        try:
            target_date = datetime.strptime(target_date_str, '%Y-%m-%d').date()
        except (ValueError, TypeError):
            return JsonResponse({
                'success': False,
                'message': 'Định dạng ngày không hợp lệ'
            })
        
        # Tạo dự đoán
        prediction_view = ChamPredictionView()
        
        if method == 'all':
            predictions = prediction_view._get_all_predictions(target_date)
            
            # Tính điểm tổng hợp
            number_scores = prediction_view._calculate_combined_scores(predictions)
            
            # Sắp xếp theo điểm
            sorted_numbers = sorted(number_scores.items(), key=lambda x: x[1], reverse=True)
            top_numbers = [num for num, score in sorted_numbers[:10]]
            
            return JsonResponse({
                'success': True,
                'target_date': target_date_str,
                'method': 'all',
                'predictions': predictions,
                'number_scores': dict(sorted_numbers[:20]),
                'top_numbers': top_numbers
            })
        else:
            prediction = prediction_view._get_prediction_by_method(method, target_date)
            
            return JsonResponse({
                'success': True,
                'target_date': target_date_str,
                'method': method,
                'prediction': prediction
            })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Lỗi: {str(e)}'
        })
    
class ChamDauListView(ListView):
    """Danh sách chạm đầu"""
    model = ChamDau
    template_name = 'chamde/cham_dau_list.html'
    context_object_name = 'cham_dau_list'
    paginate_by = 20
    
    def get_queryset(self):
        # Lấy khoảng thời gian từ query params hoặc mặc định
        days = int(self.request.GET.get('days', 30))
        end_date = timezone.now().date()
        start_date = end_date - timedelta(days=days)
        
        # Lọc theo chạm value nếu có
        cham_value = self.request.GET.get('cham', None)
        if cham_value:
            return ChamDau.objects.filter(
                ngay__gte=start_date,
                ngay__lte=end_date,
                cham_value=cham_value
            ).order_by('-ngay')
        
        return ChamDau.objects.filter(
            ngay__gte=start_date,
            ngay__lte=end_date
        ).order_by('-ngay')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Lấy khoảng thời gian từ query params hoặc mặc định
        days = int(self.request.GET.get('days', 30))
        context['selected_days'] = days
        
        # Lấy thống kê chạm đầu
        cham_value = self.request.GET.get('cham', None)
        context['selected_cham'] = cham_value
        
        # Tính thống kê tỷ lệ trúng
        end_date = timezone.now().date()
        start_date = end_date - timedelta(days=days)
        
        hit_stats = {}
        for i in range(10):
            value = str(i)
            total = ChamDau.objects.filter(
                ngay__gte=start_date,
                ngay__lte=end_date,
                cham_value=value
            ).count()
            
            hits = ChamDau.objects.filter(
                ngay__gte=start_date,
                ngay__lte=end_date,
                cham_value=value,
                has_hit=True
            ).count()
            
            hit_rate = (hits / total) * 100 if total > 0 else 0
            hit_stats[value] = {
                'total': total,
                'hits': hits,
                'hit_rate': hit_rate
            }
        
        context['hit_stats'] = hit_stats
        
        return context

class ChamDuoiListView(ListView):
    """Danh sách chạm đuôi"""
    model = ChamDuoi
    template_name = 'chamde/cham_duoi_list.html'
    context_object_name = 'cham_duoi_list'
    paginate_by = 20
    
    def get_queryset(self):
        # Lấy khoảng thời gian từ query params hoặc mặc định
        days = int(self.request.GET.get('days', 30))
        end_date = timezone.now().date()
        start_date = end_date - timedelta(days=days)
        
        # Lọc theo chạm value nếu có
        cham_value = self.request.GET.get('cham', None)
        if cham_value:
            return ChamDuoi.objects.filter(
                ngay__gte=start_date,
                ngay__lte=end_date,
                cham_value=cham_value
            ).order_by('-ngay')
        
        return ChamDuoi.objects.filter(
            ngay__gte=start_date,
            ngay__lte=end_date
        ).order_by('-ngay')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Lấy khoảng thời gian từ query params hoặc mặc định
        days = int(self.request.GET.get('days', 30))
        context['selected_days'] = days
        
        # Lấy thống kê chạm đuôi
        cham_value = self.request.GET.get('cham', None)
        context['selected_cham'] = cham_value
        
        # Tính thống kê tỷ lệ trúng
        end_date = timezone.now().date()
        start_date = end_date - timedelta(days=days)
        
        hit_stats = {}
        for i in range(10):
            value = str(i)
            total = ChamDuoi.objects.filter(
                ngay__gte=start_date,
                ngay__lte=end_date,
                cham_value=value
            ).count()
            
            hits = ChamDuoi.objects.filter(
                ngay__gte=start_date,
                ngay__lte=end_date,
                cham_value=value,
                has_hit=True
            ).count()
            
            hit_rate = (hits / total) * 100 if total > 0 else 0
            hit_stats[value] = {
                'total': total,
                'hits': hits,
                'hit_rate': hit_rate
            }
        
        context['hit_stats'] = hit_stats
        
        return context

class CauChamPredictionView(TemplateView):
    """Trang dự đoán và phân tích cầu chạm"""
    template_name = 'chamde/cau_cham_prediction.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Lấy phương pháp cầu chạm từ query params hoặc mặc định
        method = self.request.GET.get('method', 'cau_cham1')
        context['selected_method'] = method
        
        # Lấy ngày dự đoán từ query params hoặc mặc định
        target_date_str = self.request.GET.get('target_date', None)
        if target_date_str:
            target_date = datetime.strptime(target_date_str, '%Y-%m-%d').date()
        else:
            # Mặc định là ngày mai
            target_date = timezone.now().date() + timedelta(days=1)
        
        context['target_date'] = target_date
        
        # Tạo dự đoán dựa trên phương pháp được chọn
        predictions = self.generate_predictions(method, target_date)
        context['predictions'] = predictions
        
        return context
    
    def generate_predictions(self, method, target_date):
        """Tạo dự đoán dựa trên phương pháp cầu chạm được chọn"""
        predictions = []
        
        if method == 'cau_cham1':
            # Cầu chạm kiểu 1: Lấy từ giải nhất Chủ Nhật
            # Tìm Chủ Nhật gần nhất
            today = timezone.now().date()
            days_since_sunday = (today.weekday() + 1) % 7  # 0 là thứ hai, 6 là chủ nhật
            last_sunday = today - timedelta(days=days_since_sunday)
            
            # Lấy phân tích chạm cho Chủ Nhật
            analysis = ChamAnalysis.objects.filter(ngay=last_sunday).first()
            if analysis and analysis.cau_cham1_value:
                # Tạo dự đoán từ chạm đầu
                cham_dau_numbers = generate_cham_dau_numbers(analysis.cau_cham1_value)
                predictions.append({
                    'type': 'cau_cham1',
                    'value': analysis.cau_cham1_value,
                    'source_date': last_sunday,
                    'numbers': cham_dau_numbers,
                    'confidence': 0.7  # Giá trị mặc định
                })
        
        elif method == 'cau_cham2':
            # Cầu chạm kiểu 2: Tổng đề CN + đuôi đề thứ 6
            # Tìm Chủ Nhật gần nhất
            today = timezone.now().date()
            days_since_sunday = (today.weekday() + 1) % 7
            last_sunday = today - timedelta(days=days_since_sunday)
            
            # Lấy phân tích chạm cho Chủ Nhật
            analysis = ChamAnalysis.objects.filter(ngay=last_sunday).first()
            if analysis and analysis.cau_cham2_value:
                predictions.append({
                    'type': 'cau_cham2',
                    'value': analysis.cau_cham2_value,
                    'source_date': last_sunday,
                    'numbers': [analysis.cau_cham2_value],
                    'confidence': 0.65  # Giá trị mặc định
                })
        
        return predictions    
class QuaTramPatternView(ListView):
    """Trang hiển thị và phân tích mẫu quả trám"""
    model = QuaTramPattern
    template_name = 'chamde/qua_tram_pattern.html'
    context_object_name = 'patterns'
    paginate_by = 20
    
    def get_queryset(self):
        # Lấy khoảng thời gian từ query params hoặc mặc định
        days = int(self.request.GET.get('days', 30))
        end_date = timezone.now().date()
        start_date = end_date - timedelta(days=days)
        
        # Lọc theo trạng thái hit nếu có
        hit_filter = self.request.GET.get('hit', None)
        queryset = QuaTramPattern.objects.filter(
            ngay__gte=start_date,
            ngay__lte=end_date
        )
        
        if hit_filter == 'yes':
            queryset = queryset.filter(has_hit=True)
        elif hit_filter == 'no':
            queryset = queryset.filter(has_hit=False)
        
        return queryset.order_by('-ngay')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Lấy khoảng thời gian từ query params hoặc mặc định
        days = int(self.request.GET.get('days', 30))
        context['selected_days'] = days
        
        # Lấy filter hit
        hit_filter = self.request.GET.get('hit', None)
        context['hit_filter'] = hit_filter
        
        # Tính thống kê hiệu suất
        end_date = timezone.now().date()
        start_date = end_date - timedelta(days=days)
        
        total_patterns = QuaTramPattern.objects.filter(
            ngay__gte=start_date,
            ngay__lte=end_date
        ).count()
        
        hit_patterns = QuaTramPattern.objects.filter(
            ngay__gte=start_date,
            ngay__lte=end_date,
            has_hit=True
        ).count()
        
        hit_rate = (hit_patterns / total_patterns) * 100 if total_patterns > 0 else 0
        
        context['stats'] = {
            'total_patterns': total_patterns,
            'hit_patterns': hit_patterns,
            'hit_rate': hit_rate
        }
        
        return context

from django.views.generic import ListView, DetailView, TemplateView
from django.utils import timezone
from django.db.models import Count, Q, Avg, Sum
from datetime import timedelta, datetime
import json
from collections import defaultdict
from .models import (
    ChamAnalysis, ChamDau, ChamDuoi, CauChamPrediction, 
    QuaTramPattern, NumberStatistics, ChamPatternAnalysis,
    WeeklyDigitPatternStats, LoGanStats
)
from results.models import KetQuaXoSo

class   ChamStatisticsView(TemplateView):
    """Trang thống kê tổng quan về chạm"""
    template_name = 'chamde/cham_statistics.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Lấy khoảng thời gian từ query params hoặc mặc định
        days = int(self.request.GET.get('days', 30))
        end_date = timezone.now().date()
        start_date = end_date - timedelta(days=days)
        
        # Thống kê chạm đầu
        cham_dau_stats = self._get_cham_dau_statistics(start_date, end_date)
        
        # Thống kê chạm đuôi
        cham_duoi_stats = self._get_cham_duoi_statistics(start_date, end_date)
        
        # Thống kê theo ngày trong tuần
        weekday_stats = self._get_weekday_statistics(start_date, end_date)
        
        # Top số về nhiều nhất
        top_numbers = self._get_top_numbers(start_date, end_date)
        
        context.update({
            'selected_days': days,
            'start_date': start_date,
            'end_date': end_date,
            'cham_dau_stats': cham_dau_stats,
            'cham_duoi_stats': cham_duoi_stats,
            'weekday_stats': weekday_stats,
            'top_numbers': top_numbers,
        })
        
        return context
    
    def _get_cham_dau_statistics(self, start_date, end_date):
        """Thống kê chạm đầu"""
        stats = []
        for value in range(10):
            cham_records = ChamDau.objects.filter(
                ngay__gte=start_date,
                ngay__lte=end_date,
                cham_value=str(value)
            )
            
            total_count = cham_records.count()
            hit_count = cham_records.filter(has_hit=True).count()
            hit_rate = (hit_count / total_count) * 100 if total_count > 0 else 0
            
            stats.append({
                'value': value,
                'total_count': total_count,
                'hit_count': hit_count,
                'hit_rate': round(hit_rate, 2)
            })
        
        return sorted(stats, key=lambda x: x['hit_rate'], reverse=True)
    
    def _get_cham_duoi_statistics(self, start_date, end_date):
        """Thống kê chạm đuôi"""
        stats = []
        for value in range(10):
            cham_records = ChamDuoi.objects.filter(
                ngay__gte=start_date,
                ngay__lte=end_date,
                cham_value=str(value)
            )
            
            total_count = cham_records.count()
            hit_count = cham_records.filter(has_hit=True).count()
            hit_rate = (hit_count / total_count) * 100 if total_count > 0 else 0
            
            stats.append({
                'value': value,
                'total_count': total_count,
                'hit_count': hit_count,
                'hit_rate': round(hit_rate, 2)
            })
        
        return sorted(stats, key=lambda x: x['hit_rate'], reverse=True)
    
    def _get_weekday_statistics(self, start_date, end_date):
        """Thống kê theo ngày trong tuần"""
        weekdays = ['Thứ 2', 'Thứ 3', 'Thứ 4', 'Thứ 5', 'Thứ 6', 'Thứ 7', 'Chủ nhật']
        stats = []
        
        for i, weekday in enumerate(weekdays):
            analyses = ChamAnalysis.objects.filter(
                ngay__gte=start_date,
                ngay__lte=end_date,
                day_of_week=i
            )
            
            total_count = analyses.count()
            
            # Tính trung bình tổng giải đặc biệt theo ngày
            avg_total = analyses.aggregate(avg_total=Avg('db_total'))['avg_total'] or 0
            
            stats.append({
                'weekday': weekday,
                'total_count': total_count,
                'avg_total': round(avg_total, 2)
            })
        
        return stats
    
    def _get_top_numbers(self, start_date, end_date, limit=10):
        """Top số về nhiều nhất"""
        number_stats = NumberStatistics.objects.filter(
            last_appearance_date__gte=start_date,
            last_appearance_date__lte=end_date
        ).order_by('-total_appearances')[:limit]
        
        return number_stats


class ChamTrackingView(ListView):
    """Trang theo dõi chạm theo thời gian"""
    model = ChamAnalysis
    template_name = 'chamde/cham_tracking.html'
    context_object_name = 'analyses'
    paginate_by = 30

    def get_queryset(self):
        # Lấy khoảng thời gian từ query params
        days = int(self.request.GET.get('days', 30))
        end_date = timezone.now().date()
        start_date = end_date - timedelta(days=days)
        
        # Lọc theo chạm đầu hoặc chạm đuôi nếu có
        cham_dau_filter = self.request.GET.get('cham_dau', '')
        cham_duoi_filter = self.request.GET.get('cham_duoi', '')
        
        queryset = ChamAnalysis.objects.filter(
            ngay__gte=start_date,
            ngay__lte=end_date
        )
        
        if cham_dau_filter:
            queryset = queryset.filter(db_cham_dau=cham_dau_filter)
        
        if cham_duoi_filter:
            queryset = queryset.filter(db_cham_duoi=cham_duoi_filter)
        
        return queryset.order_by('-ngay')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        days = int(self.request.GET.get('days', 30))
        cham_dau_filter = self.request.GET.get('cham_dau', '')
        cham_duoi_filter = self.request.GET.get('cham_duoi', '')
        
        context.update({
            'selected_days': days,
            'cham_dau_filter': cham_dau_filter,
            'cham_duoi_filter': cham_duoi_filter,
            'cham_values': list(range(10)),
        })
        
        # Tạo dữ liệu cho biểu đồ timeline
        timeline_data = self._create_timeline_data(context['analyses'])
        context['timeline_data'] = json.dumps(timeline_data)
        
        return context
    
    def _create_timeline_data(self, analyses):
        """Tạo dữ liệu cho biểu đồ timeline"""
        data = []
        for analysis in analyses:
            data.append({
                'date': analysis.ngay.strftime('%Y-%m-%d'),
                'cham_dau': analysis.db_cham_dau,
                'cham_duoi': analysis.db_cham_duoi,
                'db_total': analysis.db_total,
                'db_last2': analysis.db_last2,
                'weekday': analysis.ket_qua.thu
            })
        return data


class WeeklyReportView(TemplateView):
    """Báo cáo theo tuần"""
    template_name = 'chamde/weekly_report.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Lấy tuần hiện tại hoặc từ query params
        year = int(self.request.GET.get('year', timezone.now().year))
        week = int(self.request.GET.get('week', timezone.now().isocalendar()[1]))
        
        # Lấy thống kê tuần
        weekly_stats = WeeklyDigitPatternStats.objects.filter(
            year=year, 
            week_number=week
        ).first()
        
        # Lấy dữ liệu phân tích chạm trong tuần
        week_analyses = self._get_week_analyses(year, week)
        
        # Lấy các mẫu quả trám trong tuần
        week_patterns = self._get_week_patterns(year, week)
        
        # Thống kê tổng quan tuần
        week_summary = self._get_week_summary(year, week)
        
        context.update({
            'year': year,
            'week': week,
            'weekly_stats': weekly_stats,
            'week_analyses': week_analyses,
            'week_patterns': week_patterns,
            'week_summary': week_summary,
        })
        
        return context
    
    def _get_week_analyses(self, year, week):
        """Lấy phân tích chạm trong tuần"""
        return ChamAnalysis.objects.filter(
            week_number=week,
            ngay__year=year
        ).order_by('ngay')
    
    def _get_week_patterns(self, year, week):
        """Lấy mẫu quả trám trong tuần"""
        # Tính ngày bắt đầu và kết thúc tuần
        from datetime import datetime
        import calendar
        
        # Lấy ngày đầu tiên của năm
        jan_1 = datetime(year, 1, 1).date()
        # Tính ngày bắt đầu tuần
        week_start = jan_1 + timedelta(weeks=week-1)
        week_end = week_start + timedelta(days=6)
        
        return QuaTramPattern.objects.filter(
            ngay__gte=week_start,
            ngay__lte=week_end
        ).order_by('ngay')
    
    def _get_week_summary(self, year, week):
        """Tạo tóm tắt tuần"""
        week_analyses = self._get_week_analyses(year, week)
        
        if not week_analyses:
            return None
        
        # Thống kê chạm đầu, đuôi trong tuần
        cham_dau_count = defaultdict(int)
        cham_duoi_count = defaultdict(int)
        
        for analysis in week_analyses:
            cham_dau_count[analysis.db_cham_dau] += 1
            cham_duoi_count[analysis.db_cham_duoi] += 1
        
        return {
            'total_days': len(week_analyses),
            'most_common_cham_dau': max(cham_dau_count.items(), key=lambda x: x[1]) if cham_dau_count else None,
            'most_common_cham_duoi': max(cham_duoi_count.items(), key=lambda x: x[1]) if cham_duoi_count else None,
            'avg_db_total': sum(a.db_total for a in week_analyses) / len(week_analyses),
        }


class MonthlyReportView(TemplateView):
    """Báo cáo theo tháng"""
    template_name = 'chamde/monthly_report.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Lấy tháng hiện tại hoặc từ query params
        year = int(self.request.GET.get('year', timezone.now().year))
        month = int(self.request.GET.get('month', timezone.now().month))
        
        # Lấy dữ liệu phân tích chạm trong tháng
        month_analyses = self._get_month_analyses(year, month)
        
        # Thống kê theo tuần trong tháng
        weekly_breakdown = self._get_weekly_breakdown(year, month)
        
        # Top số về nhiều trong tháng
        top_numbers_month = self._get_top_numbers_month(year, month)
        
        # Thống kê chạm theo tháng
        monthly_cham_stats = self._get_monthly_cham_stats(year, month)
        
        # Thống kê lô gan trong tháng
        gan_stats = self._get_monthly_gan_stats(year, month)
        
        context.update({
            'year': year,
            'month': month,
            'month_analyses': month_analyses,
            'weekly_breakdown': weekly_breakdown,
            'top_numbers_month': top_numbers_month,
            'monthly_cham_stats': monthly_cham_stats,
            'gan_stats': gan_stats,
        })
        
        return context
    
    def _get_month_analyses(self, year, month):
        """Lấy phân tích chạm trong tháng"""
        return ChamAnalysis.objects.filter(
            ngay__year=year,
            ngay__month=month
        ).order_by('ngay')
    
    def _get_weekly_breakdown(self, year, month):
        """Phân tích theo tuần trong tháng"""
        month_analyses = self._get_month_analyses(year, month)
        weekly_data = defaultdict(list)
        
        for analysis in month_analyses:
            week_num = analysis.week_number
            weekly_data[week_num].append(analysis)
        
        return dict(weekly_data)
    
    def _get_top_numbers_month(self, year, month, limit=20):
        """Top số về nhiều trong tháng"""
        from datetime import datetime
        start_date = datetime(year, month, 1).date()
        if month == 12:
            end_date = datetime(year + 1, 1, 1).date() - timedelta(days=1)
        else:
            end_date = datetime(year, month + 1, 1).date() - timedelta(days=1)
        
        return NumberStatistics.objects.filter(
            last_appearance_date__gte=start_date,
            last_appearance_date__lte=end_date
        ).order_by('-total_appearances')[:limit]
    
    def _get_monthly_cham_stats(self, year, month):
        """Thống kê chạm theo tháng"""
        month_analyses = self._get_month_analyses(year, month)
        
        cham_dau_stats = defaultdict(int)
        cham_duoi_stats = defaultdict(int)
        
        for analysis in month_analyses:
            cham_dau_stats[analysis.db_cham_dau] += 1
            cham_duoi_stats[analysis.db_cham_duoi] += 1
        
        return {
            'cham_dau': dict(cham_dau_stats),
            'cham_duoi': dict(cham_duoi_stats)
        }
    
    def _get_monthly_gan_stats(self, year, month):
        """Thống kê lô gan trong tháng"""
        from datetime import datetime
        start_date = datetime(year, month, 1).date()
        if month == 12:
            end_date = datetime(year + 1, 1, 1).date() - timedelta(days=1)
        else:
            end_date = datetime(year, month + 1, 1).date() - timedelta(days=1)
        
        # Lấy top lô gan nhiều ngày nhất
        top_gan = LoGanStats.objects.filter(
            date__gte=start_date,
            date__lte=end_date
        ).order_by('-current_absent_days')[:10]
        
        return top_gan


class CauCham1View(ListView):
    """Cầu chạm kiểu 1 - Dựa vào giải nhất Chủ nhật"""
    model = CauChamPrediction
    template_name = 'chamde/cau_cham1.html'
    context_object_name = 'predictions'
    paginate_by = 20

    def get_queryset(self):
        days = int(self.request.GET.get('days', 30))
        end_date = timezone.now().date()
        start_date = end_date - timedelta(days=days)
        
        return CauChamPrediction.objects.filter(
            phuong_phap='cau_cham1',
            ngay_du_doan__gte=start_date,
            ngay_du_doan__lte=end_date
        ).order_by('-ngay_du_doan')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        days = int(self.request.GET.get('days', 30))
        context['selected_days'] = days
        
        # Thống kê hiệu suất cầu chạm 1
        end_date = timezone.now().date()
        start_date = end_date - timedelta(days=days)
        
        total_predictions = CauChamPrediction.objects.filter(
            phuong_phap='cau_cham1',
            ngay_du_doan__gte=start_date,
            ngay_du_doan__lte=end_date,
            ket_qua_trung__isnull=False
        ).count()
        
        successful_predictions = CauChamPrediction.objects.filter(
            phuong_phap='cau_cham1',
            ngay_du_doan__gte=start_date,
            ngay_du_doan__lte=end_date,
            ket_qua_trung=True
        ).count()
        
        success_rate = (successful_predictions / total_predictions) * 100 if total_predictions > 0 else 0
        
        # Lấy dữ liệu chủ nhật gần nhất để dự đoán
        latest_sunday = self._get_latest_sunday_analysis()
        next_prediction = self._create_next_prediction(latest_sunday) if latest_sunday else None
        
        context.update({
            'stats': {
                'total_predictions': total_predictions,
                'successful_predictions': successful_predictions,
                'success_rate': round(success_rate, 2)
            },
            'latest_sunday': latest_sunday,
            'next_prediction': next_prediction,
        })
        
        return context
    
    def _get_latest_sunday_analysis(self):
        """Lấy phân tích chủ nhật gần nhất"""
        return ChamAnalysis.objects.filter(is_sunday=True).order_by('-ngay').first()
    
    def _create_next_prediction(self, sunday_analysis):
        """Tạo dự đoán cho ngày tiếp theo dựa vào chủ nhật"""
        if not sunday_analysis or not sunday_analysis.cau_cham1_value:
            return None
        
        # Tạo danh sách số dự đoán dựa vào chữ số giữa giải nhất
        cham_value = sunday_analysis.cau_cham1_value
        predicted_numbers = [f"{cham_value}{i}" for i in range(10)]
        
        return {
            'cham_value': cham_value,
            'predicted_numbers': predicted_numbers,
            'source_date': sunday_analysis.ngay,
            'confidence': 75  # Độ tin cậy mặc định
        }


class CauCham2View(ListView):
    """Cầu chạm kiểu 2 - Tổng đề CN + đuôi đề thứ 6"""
    model = CauChamPrediction
    template_name = 'chamde/cau_cham2.html'
    context_object_name = 'predictions'
    paginate_by = 20

    def get_queryset(self):
        days = int(self.request.GET.get('days', 30))
        end_date = timezone.now().date()
        start_date = end_date - timedelta(days=days)
        
        return CauChamPrediction.objects.filter(
            phuong_phap='cau_cham2',
            ngay_du_doan__gte=start_date,
            ngay_du_doan__lte=end_date
        ).order_by('-ngay_du_doan')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        days = int(self.request.GET.get('days', 30))
        context['selected_days'] = days
        
        # Thống kê hiệu suất cầu chạm 2
        end_date = timezone.now().date()
        start_date = end_date - timedelta(days=days)
        
        total_predictions = CauChamPrediction.objects.filter(
            phuong_phap='cau_cham2',
            ngay_du_doan__gte=start_date,
            ngay_du_doan__lte=end_date,
            ket_qua_trung__isnull=False
        ).count()
        
        successful_predictions = CauChamPrediction.objects.filter(
            phuong_phap='cau_cham2',
            ngay_du_doan__gte=start_date,
            ngay_du_doan__lte=end_date,
            ket_qua_trung=True
        ).count()
        
        success_rate = (successful_predictions / total_predictions) * 100 if total_predictions > 0 else 0
        
        # Lấy dữ liệu để tạo dự đoán mới
        prediction_data = self._get_prediction_data()
        
        context.update({
            'stats': {
                'total_predictions': total_predictions,
                'successful_predictions': successful_predictions,
                'success_rate': round(success_rate, 2)
            },
            'prediction_data': prediction_data,
        })
        
        return context
    
    def _get_prediction_data(self):
        """Lấy dữ liệu để tạo dự đoán cầu chạm 2"""
        # Lấy chủ nhật gần nhất
        latest_sunday = ChamAnalysis.objects.filter(is_sunday=True).order_by('-ngay').first()
        
        if not latest_sunday or not latest_sunday.cau_cham2_value:
            return None
        
        cham_value = latest_sunday.cau_cham2_value
        
        # Tạo danh sách số dự đoán
        if len(cham_value) == 2:
            predicted_numbers = [f"{cham_value[0]}{i}" for i in range(10)] + \
                              [f"{i}{cham_value[1]}" for i in range(10)]
            # Loại bỏ trùng lặp
            predicted_numbers = list(set(predicted_numbers))
        else:
            predicted_numbers = []
        
        return {
            'cham_value': cham_value,
            'predicted_numbers': sorted(predicted_numbers),
            'source_date': latest_sunday.ngay,
            'confidence': 70  # Độ tin cậy mặc định
        }


class QuaTramDetailView(DetailView):
    """Chi tiết mẫu quả trám"""
    model = QuaTramPattern
    template_name = 'chamde/qua_tram_detail.html'
    context_object_name = 'pattern'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        pattern = self.get_object()
        
        # Lấy lịch sử các mẫu tương tự
        similar_patterns = self._get_similar_patterns(pattern)
        
        # Thống kê hiệu suất của mẫu này
        pattern_stats = self._get_pattern_statistics(pattern)
        
        # Theo dõi kết quả nếu chưa về
        tracking_info = self._get_tracking_info(pattern)
        
        context.update({
            'similar_patterns': similar_patterns,
            'pattern_stats': pattern_stats,
            'tracking_info': tracking_info,
        })
        
        return context
    
    def _get_similar_patterns(self, pattern, limit=10):
        """Lấy các mẫu tương tự"""
        return QuaTramPattern.objects.filter(
            digit_top=pattern.digit_top,
            digit_bottom=pattern.digit_bottom
        ).exclude(id=pattern.id).order_by('-ngay')[:limit]
    
    def _get_pattern_statistics(self, pattern):
        """Thống kê hiệu suất mẫu"""
        # Lấy tất cả mẫu có cùng cấu trúc
        similar_patterns = QuaTramPattern.objects.filter(
            digit_top=pattern.digit_top,
            digit_mid_left=pattern.digit_mid_left,
            digit_mid_right=pattern.digit_mid_right,
            digit_bottom=pattern.digit_bottom
        )
        
        total_patterns = similar_patterns.count()
        hit_patterns = similar_patterns.filter(has_hit=True).count()
        hit_rate = (hit_patterns / total_patterns) * 100 if total_patterns > 0 else 0
        
        # Tính thời gian trung bình để về
        hit_patterns_with_days = similar_patterns.filter(
            has_hit=True,
            days_to_hit__isnull=False
        )
        
        avg_days_to_hit = hit_patterns_with_days.aggregate(
            avg_days=Avg('days_to_hit')
        )['avg_days']
        
        return {
            'total_patterns': total_patterns,
            'hit_patterns': hit_patterns,
            'hit_rate': round(hit_rate, 2),
            'avg_days_to_hit': round(avg_days_to_hit, 1) if avg_days_to_hit else None
        }
    
    def _get_tracking_info(self, pattern):
        """Thông tin theo dõi kết quả"""
        if pattern.has_hit:
            return {
                'status': 'completed',
                'hit_date': pattern.hit_date,
                'days_to_hit': pattern.days_to_hit
            }
        else:
            # Tính số ngày đã trôi qua kể từ khi dự đoán
            days_passed = (timezone.now().date() - pattern.ngay).days
            
            return {
                'status': 'waiting',
                'days_passed': days_passed,
                'predicted_number': pattern.predicted_number
            }
        
from .models import Prediction  # Adjust to your actual model

class SavePredictionView(TemplateView):
    """View to handle saving predictions from the form"""
    
    def post(self, request):
        # Get form data
        selected_numbers = request.POST.getlist('selected_numbers')  # Handle multiple select
        confidence = request.POST.get('confidence')
        notes = request.POST.get('notes')
        target_date = request.POST.get('target_date')
        method = request.POST.get('method')

        # Validate data
        if not selected_numbers or not confidence or not target_date:
            messages.error(request, "Vui lòng điền đầy đủ thông tin.")
            return redirect('chamde:cham_prediction')  # Redirect back to prediction page

        try:
            # Convert target_date to date object
            target_date = datetime.strptime(target_date, '%Y-%m-%d').date()
        except ValueError:
            messages.error(request, "Ngày dự đoán không hợp lệ.")
            return redirect('chamde:cham_prediction')

        # Save to database (assuming a Prediction model exists)
        Prediction.objects.create(
            user=request.user if request.user.is_authenticated else None,  # Handle authenticated user
            numbers=','.join(selected_numbers),  # Store as comma-separated string
            confidence=confidence,
            notes=notes,
            target_date=target_date,
            method=method,
        )

        messages.success(request, "Dự đoán đã được lưu thành công!")
        return redirect('chamde:cham_prediction')