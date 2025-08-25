from collections import defaultdict       
import math
from results.models import CycleAccuracy  # Thêm import này
import re
from datetime import datetime, timedelta, date
from django.contrib import messages 
from .forms import ImportKetQuaForm, BachThuPredictionForm
from django.shortcuts import render,redirect
from .models import KetQuaXoSo, PredictionRecord, PredictionDeAllPrizeResult,DanDeDacBietAllPrize, PredictionMethodAllPrize ,PredictionModel, Prediction, LoKhung2Ngay,BachThuLoMethod,BachThuLoAnalysis,BachThuLoResult,BachThuLoStatistics
from .models import PredictionMethodBtl, DanBtl, PredictionResultBtl, OptimalMethodEnsemble
from .crawler import crawl_xoso_thantai,crawl_thang_4
import threading
from django.http import JsonResponse, HttpResponse
from django.views import View
from django.views.generic import ListView, DetailView, FormView
import logging
from .predictor import AdvancedPredictor
from collections import defaultdict
from django.core.paginator import Paginator
from collections import Counter
import pandas as pd
from django.db.models import Count
from django.utils import timezone
from django.urls import reverse_lazy
import locale
from django.db.models import Avg
import numpy as np # Import from your models
from .predictor import AdvancedCyclePredictor, AdvancedLotteryPredictor
from django.views.decorators.cache import cache_page
from .predictor import EnhancedCyclePredictor
from django.db import transaction
from django.db.models import Avg, FloatField
from django.views.generic import TemplateView
from django.http import JsonResponse
import json
from results.core.optimizations import LotteryCalculator
from .crawlers import crawl_xsmb_ketquame
from calendar import monthrange
from django.db.models import Count, Case, When, BooleanField
from django.db.models import Prefetch
from .analytics.prediction_analyzer import PredictionAnalyzer
from .forms import BachThuPredictionForm
from .bach_thu_methods import get_all_bach_thu_methods, get_method_by_code
from django.core.cache import cache
from django.db.models import Q
from django.utils.dateparse import parse_date
from sklearn.ensemble import RandomForestRegressor
from sklearn.dummy import DummyRegressor
# --- CÁC HÀM HỖ TRỢ ---
def generate_method_selection_explanation(methods, current_date):
    """
    Tạo giải thích dễ hiểu về lý do chọn các phương pháp
    """
    explanations = []
    
    for i, method in enumerate(methods):
        explanation = {
            'method': method['name'],
            'ranking': i + 1,
            'strengths': [],
            'reasons': []
        }
        
        # Thêm điểm mạnh dựa trên các điểm số
        if method.get('hit_rate', 0) > 70:
            explanation['strengths'].append('Tỷ lệ trúng cao')
        
        if method.get('stability_score', 0) > 0.7:
            explanation['strengths'].append('Hiệu suất ổn định')
        
        if method.get('trend_score', 0) > 0.7:
            explanation['strengths'].append('Xu hướng tăng gần đây')
        
        if method.get('context_score', 0) > 0.7:
            explanation['strengths'].append('Phù hợp với ngày hiện tại')
        
        if method.get('next_day_probability', 0) > 0.6:
            explanation['strengths'].append('Xác suất thành công cao')
        
        # Thêm lý do chọn
        explanation['reasons'].append(f"Điểm xếp hạng tổng hợp: {method.get('ranking_score', 0):.2f}/1.0")
        
        if method.get('hit_count', 0) > 0 and method.get('prediction_count', 0) > 0:
            explanation['reasons'].append(
                f"Hiệu suất gần đây: {method.get('hit_count', 0)}/{method.get('prediction_count', 0)} "
                f"({method.get('hit_rate', 0):.1f}%)"
            )
        
        if method.get('next_day_probability') is not None:
            explanation['reasons'].append(
                f"Dự đoán xác suất thành công: {method.get('next_day_probability', 0)*100:.1f}%"
            )
        
        explanations.append(explanation)
    
    return explanations
def calculate_prediction_diversity(method):
    """
    Tính điểm đa dạng của các số được dự đoán bởi phương pháp
    
    Args:
        method: Dữ liệu về phương pháp dự đoán
        
    Returns:
        Điểm đa dạng từ 0-1
    """
    predicted_numbers = method.get('predicted_numbers', [])
    
    # Nếu không có dự đoán, trả về điểm trung bình
    if not predicted_numbers or len(predicted_numbers) < 2:
        return 0.5
    
    # Tính đa dạng dựa trên phân bố đầu số và đuôi số
    heads = [num[0] for num in predicted_numbers if len(num) >= 2]
    tails = [num[-1] for num in predicted_numbers if len(num) >= 1]
    
    # Đếm tần suất xuất hiện
    head_counts = Counter(heads)
    tail_counts = Counter(tails)
    
    # Tính chỉ số đa dạng (sử dụng chỉ số entropy)
    head_diversity = calculate_entropy([count / len(heads) for count in head_counts.values()]) if heads else 0
    tail_diversity = calculate_entropy([count / len(tails) for count in tail_counts.values()]) if tails else 0
    
    # Chuẩn hóa kết quả (entropy tối đa khi phân bố đều trên 10 giá trị = log2(10) ≈ 3.32)
    max_entropy = math.log2(10)  # Vì có 10 chữ số (0-9)
    normalized_head_diversity = min(head_diversity / max_entropy, 1.0)
    normalized_tail_diversity = min(tail_diversity / max_entropy, 1.0)
    
    # Tính đa dạng về các mẫu số đặc biệt
    special_patterns_diversity = calculate_special_patterns_diversity(predicted_numbers)
    
    # Kết hợp các điểm đa dạng
    diversity_score = (normalized_head_diversity + normalized_tail_diversity + special_patterns_diversity) / 3
    
    return diversity_score

def calculate_entropy(probabilities):
    """
    Tính entropy của một phân phối xác suất
    
    Args:
        probabilities: Danh sách các xác suất
        
    Returns:
        Giá trị entropy
    """
    return -sum(p * math.log2(p) for p in probabilities if p > 0)

def calculate_special_patterns_diversity(numbers):
    """
    Tính đa dạng của các mẫu số đặc biệt trong dự đoán
    
    Args:
        numbers: Danh sách các số dự đoán
        
    Returns:
        Điểm đa dạng từ 0-1
    """
    if not numbers:
        return 0.5
    
    pattern_counts = {
        'double': 0,        # Số kép (11, 22, ...)
        'mirror': 0,        # Số gương (19, 28, ...)
        'consecutive': 0,   # Số liên tiếp (12, 23, ...)
        'reversed': 0,      # Số đảo (12, 21, ...)
        'same_sum': 0       # Tổng chữ số bằng nhau
    }
    
    # Phân loại các số
    for num in numbers:
        if len(num) == 2:
            if num[0] == num[1]:  # Số kép
                pattern_counts['double'] += 1
            elif int(num[0]) + int(num[1]) == 9:  # Số gương
                pattern_counts['mirror'] += 1
            elif abs(int(num[0]) - int(num[1])) == 1:  # Số liên tiếp
                pattern_counts['consecutive'] += 1
            
            # Kiểm tra số đảo
            reversed_num = num[1] + num[0]
            if reversed_num in numbers and reversed_num != num:
                pattern_counts['reversed'] += 1
    
    # Tính tỷ lệ mỗi loại mẫu
    total = len(numbers)
    pattern_ratios = [count / total for count in pattern_counts.values()]
    
    # Tính mức độ cân bằng giữa các loại mẫu
    # Nếu các mẫu đặc biệt xuất hiện nhiều nhưng đa dạng -> điểm cao
    pattern_entropy = calculate_entropy([r for r in pattern_ratios if r > 0])
    
    # Chuẩn hóa
    max_pattern_entropy = math.log2(len(pattern_counts))
    normalized_pattern_entropy = min(pattern_entropy / max_pattern_entropy, 1.0) if max_pattern_entropy > 0 else 0.5
    
    return normalized_pattern_entropy
# Thêm hàm analyze_method_in_period vào trước hàm rank_prediction_methods
def analyze_method_in_period(method, history_data, current_date, period_days):
    """
    Phân tích hiệu suất của một phương pháp trong một khoảng thời gian nhất định
    
    Args:
        method: Thông tin phương pháp
        history_data: Dữ liệu lịch sử
        current_date: Ngày hiện tại đang phân tích
        period_days: Số ngày trong khoảng thời gian phân tích
    
    Returns:
        Dictionary chứa các chỉ số hiệu suất của phương pháp trong khoảng thời gian
    """
    # Tính ngày bắt đầu của khoảng phân tích
    start_date = current_date - timedelta(days=period_days)
    
    # Lọc dữ liệu lịch sử trong khoảng thời gian
    period_data = []
    for d in history_data:
        # Chuyển đổi ngày từ chuỗi sang đối tượng date nếu cần
        date_obj = d['date']
        if isinstance(date_obj, str):
            try:
                # Thử chuyển đổi chuỗi sang đối tượng date
                date_obj = parse_date(date_obj)
            except (ValueError, TypeError):
                # Nếu không thể chuyển đổi, bỏ qua mục này
                continue
        
        # Kiểm tra xem ngày có nằm trong khoảng thời gian không
        if start_date <= date_obj < current_date:
            period_data.append(d)
    
    # Nếu không có dữ liệu, trả về hiệu suất mặc định
    if not period_data:
        return {
            'total_predictions': 0,
            'total_hits': 0,
            'hit_rate': 0,
            'consistency': 0,
            'confidence': 0
        }
    
    # Tính tổng số dự đoán và số trúng
    total_predictions = 0
    total_hits = 0
    hit_rates = []
    
    for day in period_data:
        # Tìm thông tin phương pháp trong ngày đó
        method_in_day = next((m for m in day.get('methods', []) if m.get('id') == method.get('id')), None)
        
        if method_in_day:
            day_predictions = method_in_day.get('prediction_count', 0)
            day_hits = method_in_day.get('hit_count', 0)
            
            total_predictions += day_predictions
            total_hits += day_hits
            
            # Tính tỷ lệ trúng cho ngày
            if day_predictions > 0:
                hit_rates.append(day_hits / day_predictions)
            else:
                hit_rates.append(0)
    
    # Tính tỷ lệ trúng tổng thể
    overall_hit_rate = (total_hits / total_predictions) if total_predictions > 0 else 0
    
    # Tính độ nhất quán (mức độ dao động của tỷ lệ trúng qua các ngày)
    consistency = 1 - np.std(hit_rates) if hit_rates else 0
    
    # Tính điểm tin cậy dựa trên Wilson score
    confidence = wilson_score(total_hits, total_predictions)
    
    return {
            'total_predictions': int(total_predictions),
            'total_hits': int(total_hits),
            'hit_rate': float(overall_hit_rate * 100),
            'consistency': float(consistency * 100),
            'confidence': float(confidence * 100)
        }

# Xử lý đúng đắn trong rank_prediction_methods để đảm bảo 'trend' là số
def rank_prediction_methods(methods, history_data, current_date, winning_numbers):
    """
    Xếp hạng các phương pháp dự đoán dựa trên nhiều tiêu chí
    """
    # Đảm bảo history_data có cấu trúc phù hợp, nếu không thì trả về methods gốc
    if not history_data or not isinstance(history_data, list):
        return methods
    
    ranked_methods = []
    
    # Thời gian phân tích
    periods = [7, 30, 90]  # Phân tích trong 7, 30, và 90 ngày gần nhất
    
    for method in methods:
        method_copy = method.copy()
        
        # Tính hiệu suất trong các khoảng thời gian khác nhau
        performance = {}
        for period in periods:
            perf = analyze_method_in_period(method, history_data, current_date, period)
            performance[f'{period}_days'] = perf
        
        # Tính điểm trung bình
        avg_hit_rate = np.mean([perf['hit_rate'] for perf in performance.values()])
        avg_consistency = np.mean([perf['consistency'] for perf in performance.values()])
        avg_confidence = np.mean([perf['confidence'] for perf in performance.values()])
        
        # Tính xu hướng hiệu suất (đang tăng hay giảm)
        if len(periods) >= 2:
            short_term = float(performance[f'{periods[0]}_days']['hit_rate'])
            long_term = float(performance[f'{periods[-1]}_days']['hit_rate'])
            trend = short_term - long_term
        else:
            trend = 0
        
        # Tính điểm xếp hạng tổng hợp
        ranking_score = (
            avg_hit_rate * 0.4 +           # 40% dựa vào tỷ lệ trúng
            avg_consistency * 0.2 +         # 20% dựa vào độ nhất quán
            avg_confidence * 0.3 +          # 30% dựa vào độ tin cậy
            (trend > 0) * 10                # +10 điểm nếu xu hướng đang tăng
        )
        
        # Thêm thông tin hiệu suất vào method
        method_copy['performance'] = performance
        method_copy['avg_hit_rate'] = float(avg_hit_rate)
        method_copy['avg_consistency'] = float(avg_consistency)
        method_copy['avg_confidence'] = float(avg_confidence)
        method_copy['trend'] = float(trend)
        method_copy['ranking_score'] = float(ranking_score)
        
        # Thêm stability_score (đồng nhất với avg_consistency để đảm bảo tương thích)
        method_copy['stability_score'] = float(avg_consistency)
        
        # Dự đoán xác suất thành công cho ngày tiếp theo
        method_copy['next_day_probability'] = predict_next_day_success(method_copy, history_data, current_date)
        
        ranked_methods.append(method_copy)
    
    # Sắp xếp phương pháp theo điểm xếp hạng giảm dần
    ranked_methods.sort(key=lambda x: x['ranking_score'], reverse=True)
    
    return ranked_methods
def optimize_methods(self, max_methods=5):
    """
    Thực hiện quy trình tối ưu hóa phương pháp và lưu kết quả vào cơ sở dữ liệu
    """
    start_time = time.time()
    logger.info(f"Bắt đầu tối ưu hóa phương pháp cho ngày {self.analysis_date}")
    
    try:
        # Tải dữ liệu phương pháp
        methods_data = self.load_methods_data()
        if not methods_data:
            logger.error(f"Không thể tải dữ liệu phương pháp cho ngày {self.analysis_date}")
            return None
        
        # --- CẢI TIẾN: Phân nhóm và cải thiện đánh giá phương pháp ---
        enhanced_methods = enhance_method_performance(methods_data)
        
        # Kiểm tra và ghi log
        logger.info(f"Đã nâng cao hiệu suất cho {len(enhanced_methods)} phương pháp")
        
        method_groups = group_methods(enhanced_methods)
        logger.info(f"Đã phân nhóm thành {len(method_groups)} nhóm phương pháp")
        
        selected_methods = select_top_methods_from_groups(method_groups)
        logger.info(f"Đã chọn {len(selected_methods)} phương pháp hàng đầu từ các nhóm")
        
        # --- CẢI TIẾN: Phân tích xu hướng hiệu suất ---
        history_data = get_historical_data(self.analysis_date, 90)
        if not history_data:
            logger.warning(f"Không có dữ liệu lịch sử cho ngày {self.analysis_date}, sử dụng danh sách rỗng")
            history_data = []
            
        analyze_performance_trends(selected_methods, history_data, self.winning_numbers)
        logger.info(f"Đã phân tích xu hướng hiệu suất")
        
        # --- CẢI TIẾN: Xếp hạng phương pháp dự đoán đa chiều ---
        try:
            ranked_methods = rank_prediction_methods(enhanced_methods, history_data, self.analysis_date, self.winning_numbers)
            logger.info(f"Đã xếp hạng {len(ranked_methods)} phương pháp")
            
            # Đảm bảo tất cả các phương pháp đều có trường stability_score
            for method in ranked_methods:
                if 'stability_score' not in method:
                    method['stability_score'] = method.get('avg_consistency', 50.0)
        except Exception as e:
            logger.error(f"Lỗi khi xếp hạng phương pháp: {str(e)}")
            # Nếu có lỗi, sử dụng phương pháp đơn giản hơn
            ranked_methods = sorted(enhanced_methods, key=lambda x: x.get('hit_rate', 0), reverse=True)
            for method in ranked_methods:
                method['stability_score'] = method.get('avg_consistency', 50.0)
                method['ranking_score'] = method.get('hit_rate', 0)
        
        # --- CẢI TIẾN: Chọn tập hợp phương pháp tối ưu và đa dạng ---
        try:
            optimal_methods = select_optimal_method_ensemble(ranked_methods, max_methods=max_methods)
            logger.info(f"Đã chọn {len(optimal_methods)} phương pháp tối ưu")
        except Exception as e:
            logger.error(f"Lỗi khi chọn tập hợp phương pháp tối ưu: {str(e)}")
            # Nếu có lỗi, chỉ lấy top N phương pháp theo xếp hạng
            optimal_methods = ranked_methods[:max_methods]
        
        # --- CẢI TIẾN: Tính toán lợi nhuận cho các phương pháp được chọn ---
        for method in optimal_methods:
            try:
                method['profit_analysis'] = calculate_profit(method)
            except Exception as e:
                logger.error(f"Lỗi khi tính toán lợi nhuận: {str(e)}")
                method['profit_analysis'] = {
                    'expected_profit': 0,
                    'risk_level': 'Medium',
                    'roi': 0
                }
        
        # Lưu kết quả vào cơ sở dữ liệu
        calculation_time = time.time() - start_time
        ensemble, created = OptimalMethodEnsemble.objects.update_or_create(
            analysis_date=self.analysis_date,
            defaults={
                'calculation_time': calculation_time,
            }
        )
        
        # Làm sạch dữ liệu trước khi chuyển đổi thành JSON
        clean_ranked_methods = clean_for_json(ranked_methods[:20] if ranked_methods else [])
        clean_optimal_methods = clean_for_json(optimal_methods)
        
        # Chỉ lưu top 20 phương pháp đã xếp hạng để tiết kiệm dung lượng
        ensemble.set_ranked_methods(clean_ranked_methods)
        ensemble.set_optimal_methods(clean_optimal_methods)
        ensemble.save()
        
        logger.info(f"Hoàn thành tối ưu hóa phương pháp cho ngày {self.analysis_date} trong {calculation_time:.2f}s")
        return ensemble
    
    except Exception as e:
        logger.error(f"Lỗi khi tối ưu hóa phương pháp: {str(e)}", exc_info=True)
        return None
def clean_for_json(data):
    """
    Làm sạch dữ liệu để đảm bảo có thể chuyển đổi thành JSON
    """
    if isinstance(data, dict):
        return {k: clean_for_json(v) for k, v in data.items()}
    elif isinstance(data, list):
        return [clean_for_json(item) for item in data]
    elif isinstance(data, (int, float, str, bool)) or data is None:
        # Đảm bảo số float không phải là nan hoặc inf
        if isinstance(data, float) and (math.isnan(data) or math.isinf(data)):
            return 0.0
        return data
    else:
        try:
            return str(data)
        except:
            return "Không thể chuyển đổi"    
def calculate_stability_score(time_performance):
    """Tính điểm ổn định dựa trên độ dao động của hiệu suất"""
    # Lấy các hiệu suất theo thời gian
    performances = [perf['hit_rate'] for perf in time_performance.values()]
    
    if not performances:
        return 0
    
    # Tính độ lệch chuẩn (càng thấp càng ổn định)
    std_dev = np.std(performances) if len(performances) > 1 else 0
    
    # Chuyển đổi thành điểm ổn định (1 - độ lệch chuẩn được chuẩn hóa)
    # Chuẩn hóa để có giá trị từ 0-1
    max_std = 100  # Giả sử hit_rate từ 0-100%
    normalized_std = min(std_dev / max_std, 1)
    
    return 1 - normalized_std
def calculate_trend_score(time_performance):
    """Tính điểm xu hướng dựa trên sự thay đổi hiệu suất theo thời gian"""
    # Lấy các khoảng thời gian và hiệu suất tương ứng
    periods = sorted(time_performance.keys())
    
    if len(periods) < 2:
        return 0.5  # Điểm trung bình nếu không đủ dữ liệu
    
    # Ưu tiên xu hướng gần đây hơn
    # Tính điểm cho từng cặp khoảng thời gian liên tiếp
    trend_points = []
    for i in range(len(periods)-1):
        shorter_period = periods[i]
        longer_period = periods[i+1]
        
        shorter_perf = time_performance[shorter_period]['hit_rate']
        longer_perf = time_performance[longer_period]['hit_rate']
        
        # Tính điểm xu hướng (tăng là tốt)
        diff = shorter_perf - longer_perf
        
        # Chuẩn hóa sự khác biệt và áp dụng hàm sigmoid để giảm ảnh hưởng của giá trị cực đoan
        normalized_diff = sigmoid(diff / 10)  # Chia cho 10 để giảm độ lớn
        
        # Gán trọng số cao hơn cho xu hướng gần đây
        weight = 2 ** (i+1)
        trend_points.append((normalized_diff, weight))
    
    # Tính điểm xu hướng tổng hợp (weighted average)
    total_weight = sum(w for _, w in trend_points)
    trend_score = sum(score * weight for score, weight in trend_points) / total_weight if total_weight else 0.5
    
    return trend_score

def sigmoid(x):
    """Hàm sigmoid để chuẩn hóa giá trị"""
    return 1 / (1 + math.exp(-x))
def evaluate_context_fit(method, current_date, history_data):
    """Đánh giá độ phù hợp của phương pháp với ngày hiện tại"""
    # Xác định các đặc điểm của ngày hiện tại
    day_of_week = current_date.weekday()
    day_of_month = current_date.day
    
    # Lấy dữ liệu lịch sử cho ngày tương tự (cùng thứ trong tuần)
    similar_days = [entry for entry in history_data 
                   if datetime.strptime(entry['date'], '%Y-%m-%d').weekday() == day_of_week]
    
    # Tính hiệu suất của phương pháp trong các ngày tương tự
    method_name = method['name']
    hit_count = 0
    total_count = 0
    
    for day_data in similar_days:
        method_result = next((m for m in day_data.get('methods', []) if m.get('name') == method_name), None)
        if method_result:
            hit_count += method_result.get('hit_count', 0)
            total_count += method_result.get('prediction_count', 0) or 1
    
    # Tính điểm phù hợp với ngữ cảnh
    if total_count > 0:
        context_score = hit_count / total_count
    else:
        context_score = 0.5  # Điểm trung bình nếu không có dữ liệu
    
    return context_score
def get_prediction_numbers(result):
    """
    Trích xuất danh sách số dự đoán từ kết quả, xử lý nhiều định dạng dữ liệu
    """
    numbers = []
    
    if hasattr(result, 'predicted_numbers'):
        if isinstance(result.predicted_numbers, list):
            numbers = result.predicted_numbers
        elif isinstance(result.predicted_numbers, str):
            try:
                # Thử parse JSON
                parsed = json.loads(result.predicted_numbers)
                if isinstance(parsed, list):
                    numbers = parsed
                else:
                    # Nếu không phải list, có thể là chuỗi ngăn cách bằng dấu phẩy
                    numbers = [n.strip() for n in result.predicted_numbers.split(',') if n.strip()]
            except json.JSONDecodeError:
                # Nếu không phải JSON, xử lý như chuỗi thông thường
                numbers = [n.strip() for n in result.predicted_numbers.split(',') if n.strip()]
    
    return numbers

def check_weekly_pattern(date_perf):
    """
    Kiểm tra mẫu hiệu suất theo chu kỳ tuần
    
    Args:
        date_perf: Danh sách các cặp (ngày, hiệu suất)
        
    Returns:
        Điểm mẫu tuần từ 0-1 (càng cao càng có mẫu rõ ràng)
    """
    if len(date_perf) < 14:  # Cần ít nhất 2 tuần dữ liệu
        return 0.5
    
    # Tính hiệu suất trung bình theo ngày trong tuần
    weekday_performances = {i: [] for i in range(7)}  # 0-6: Thứ hai - Chủ nhật
    
    for date, perf in date_perf:
        weekday = date.weekday()
        weekday_performances[weekday].append(perf)
    
    # Tính trung bình và độ lệch chuẩn cho mỗi ngày
    weekday_stats = {}
    for weekday, perfs in weekday_performances.items():
        if perfs:
            avg = sum(perfs) / len(perfs)
            std = (sum((p - avg) ** 2 for p in perfs) / len(perfs)) ** 0.5 if len(perfs) > 1 else 0
            weekday_stats[weekday] = {'avg': avg, 'std': std, 'count': len(perfs)}
    
    # Kiểm tra độ khác biệt giữa các ngày trong tuần
    if len(weekday_stats) < 3:  # Cần ít nhất 3 ngày có dữ liệu
        return 0.5
    
    # Tính phương sai giữa các ngày
    all_avgs = [stats['avg'] for stats in weekday_stats.values()]
    global_avg = sum(all_avgs) / len(all_avgs)
    
    between_day_variance = sum((avg - global_avg) ** 2 for avg in all_avgs) / len(all_avgs)
    
    # Tính phương sai trung bình trong mỗi ngày
    within_day_variance = sum(stats['std'] ** 2 for stats in weekday_stats.values()) / len(weekday_stats)
    
    # Tính tỷ lệ phương sai (F-statistic)
    variance_ratio = between_day_variance / within_day_variance if within_day_variance > 0 else 1.0
    
    # Chuẩn hóa tỷ lệ thành điểm mẫu tuần (0-1)
    # Sử dụng hàm sigmoid để chuyển đổi
    pattern_score = 1 / (1 + math.exp(-variance_ratio + 2))  # +2 để điều chỉnh ngưỡng
    
    return pattern_score
def predict_cyclical_performance(date_perf, target_date):
    """
    Dự đoán hiệu suất cho một ngày cụ thể dựa trên mẫu chu kỳ
    
    Args:
        date_perf: Danh sách các cặp (ngày, hiệu suất)
        target_date: Ngày cần dự đoán
        
    Returns:
        Điểm dự đoán từ 0-1
    """
    if len(date_perf) < 7:  # Cần ít nhất 1 tuần dữ liệu
        return 0.5
    
    # Tính hiệu suất trung bình theo ngày trong tuần
    target_weekday = target_date.weekday()
    weekday_performances = {}
    
    for date, perf in date_perf:
        weekday = date.weekday()
        if weekday not in weekday_performances:
            weekday_performances[weekday] = []
        weekday_performances[weekday].append(perf)
    
    # Kiểm tra nếu có dữ liệu cho ngày mục tiêu
    if target_weekday in weekday_performances and weekday_performances[target_weekday]:
        # Tính trung bình và xu hướng
        perfs = weekday_performances[target_weekday]
        
        # Ưu tiên dữ liệu gần đây hơn
        if len(perfs) >= 4:
            # Trọng số giảm dần theo thời gian (mới nhất có trọng số cao nhất)
            weights = [2 ** i for i in range(min(len(perfs), 4))]
            weighted_perfs = [perfs[-i-1] * weights[i] for i in range(min(len(perfs), 4))]
            predicted_perf = sum(weighted_perfs) / sum(weights)
        else:
            predicted_perf = sum(perfs) / len(perfs)
        
        # Chuẩn hóa về 0-1
        normalized_perf = min(predicted_perf / 100, 1.0)
        
        return normalized_perf
    else:
        # Nếu không có dữ liệu cho ngày mục tiêu, sử dụng trung bình toàn bộ
        all_perfs = [perf for _, perf in date_perf]
        avg_perf = sum(all_perfs) / len(all_perfs) if all_perfs else 50
        
        # Chuẩn hóa về 0-1
        normalized_perf = min(avg_perf / 100, 1.0)
        
        return normalized_perf
    
def evaluate_cyclical_performance(method, history_data, current_date):
    """Đánh giá hiệu suất chu kỳ của phương pháp"""
    method_name = method['name']
    date_perf = []
    
    # Thu thập dữ liệu hiệu suất theo ngày
    for entry in history_data:
        entry_date = datetime.strptime(entry['date'], '%Y-%m-%d')
        method_result = next((m for m in entry.get('methods', []) if m.get('name') == method_name), None)
        
        if method_result and method_result.get('prediction_count', 0) > 0:
            hit_rate = method_result.get('hit_count', 0) / method_result.get('prediction_count', 1) * 100
            date_perf.append((entry_date, hit_rate))
    
    if len(date_perf) < 7:  # Cần ít nhất 1 tuần dữ liệu
        return 0.5
    
    # Sắp xếp theo ngày
    date_perf.sort(key=lambda x: x[0])
    
    # Tính toán chu kỳ (sử dụng FFT hoặc phương pháp đơn giản hơn)
    # Ví dụ đơn giản: Kiểm tra chu kỳ 7 ngày (tuần)
    weekly_pattern = check_weekly_pattern(date_perf)
    
    # Dự đoán hiệu suất cho ngày hiện tại dựa trên chu kỳ
    predicted_perf = predict_cyclical_performance(date_perf, current_date)
    
    # Điểm số càng cao nếu chu kỳ rõ ràng và dự đoán tốt
    cycle_score = (weekly_pattern + predicted_perf) / 2
    
    return cycle_score

def train_prediction_model(history_data):
    """
    Huấn luyện mô hình dự đoán hiệu suất cho ngày tiếp theo
    """
    X = []  # Đặc trưng
    y = []  # Nhãn (tỷ lệ trúng thực tế)
    
    # Lọc các mục có thông tin về methods
    valid_entries = [entry for entry in history_data if 'methods' in entry and entry['methods']]
    
    for i, entry in enumerate(valid_entries[:-1]):  # Bỏ qua mục cuối cùng
        entry_date = entry['date']
        if isinstance(entry_date, str):
            try:
                entry_date = datetime.strptime(entry_date, '%Y-%m-%d').date()
            except (ValueError, TypeError):
                continue
        elif isinstance(entry_date, datetime):
            entry_date = entry_date.date()
        
        next_entry = valid_entries[i+1]
        
        # Xử lý cho từng phương pháp trong ngày
        for method_result in entry.get('methods', []):
            # Trích xuất đặc trưng
            features = extract_model_features(method_result, entry_date, history_data)
            
            # Tìm kết quả thực tế ngày tiếp theo
            next_day_result = next((m for m in next_entry.get('methods', []) 
                                   if m.get('id') == method_result.get('id')), None)
            
            if next_day_result:
                pred_count = next_day_result.get('prediction_count', 0)
                hit_count = next_day_result.get('hit_count', 0)
                
                if pred_count > 0:
                    actual_hit_rate = hit_count / pred_count
                    
                    # Thêm vào tập dữ liệu huấn luyện
                    X.append(features)
                    y.append(actual_hit_rate)
    
    # Nếu không đủ dữ liệu, trả về mô hình giả
    if len(X) < 10:
        return DummyRegressor(strategy='mean')
    
    # Huấn luyện mô hình
    model = RandomForestRegressor(n_estimators=50, random_state=42)
    model.fit(X, y)
    
    return model



class DummyPredictor:
    """Mô hình dự đoán đơn giản khi không có scikit-learn"""
    
    def predict_proba(self, X):
        """Trả về xác suất ngẫu nhiên"""
        return [[0.5, 0.5] for _ in X]
    
def extract_prediction_features(method, history_data, current_date):
    """
    Trích xuất đặc trưng cho dự đoán hiệu suất phương pháp
    
    Args:
        method: Dữ liệu phương pháp
        history_data: Dữ liệu lịch sử
        current_date: Ngày hiện tại
        
    Returns:
        Vector đặc trưng
    """
    # Đặc trưng cơ bản từ phương pháp hiện tại
    basic_features = [
        method.get('hit_rate', 0) / 100,  # Tỷ lệ trúng
        method.get('confidence_score', 0),  # Wilson score
        method.get('prediction_count', 0) / 100,  # Số lượng dự đoán (chuẩn hóa)
        len(method.get('group', 'other')) / 10,  # Độ dài của tên nhóm (đặc trưng đơn giản về nhóm)
        method.get('stability_score', 0.5),  # Độ ổn định
        method.get('trend_score', 0.5),  # Xu hướng
        method.get('diversity_score', 0.5),  # Độ đa dạng
    ]
    
    # Đặc trưng về thời gian
    time_features = [
        current_date.weekday() / 6,  # Ngày trong tuần (0-1)
        current_date.day / 31,  # Ngày trong tháng (0-1)
        current_date.month / 12,  # Tháng trong năm (0-1)
        int(current_date.day % 2 == 0),  # Ngày chẵn/lẻ
    ]
    
    # Đặc trưng về hiệu suất lịch sử cho ngày tương tự
    historical_features = extract_historical_features(method, history_data, current_date)
    
    # Kết hợp tất cả đặc trưng
    all_features = basic_features + time_features + historical_features
    
    return all_features

def extract_historical_features(method, history_data, current_date):
    """
    Trích xuất đặc trưng về hiệu suất lịch sử
    
    Args:
        method: Dữ liệu phương pháp
        history_data: Dữ liệu lịch sử
        current_date: Ngày hiện tại
        
    Returns:
        Vector đặc trưng lịch sử
    """
    method_name = method.get('name')
    
    # Đặc trưng về hiệu suất trong các khoảng thời gian khác nhau
    periods = [7, 15, 30, 60]
    period_features = []
    
    for days in periods:
        # Tính hiệu suất trong khoảng thời gian
        start_date = current_date - timedelta(days=days)
        
        # Lọc dữ liệu lịch sử trong khoảng thời gian
        period_data = [
            entry for entry in history_data 
            if start_date <= datetime.strptime(entry['date'], '%Y-%m-%d').date() < current_date
        ]
        
        # Tính hiệu suất của phương pháp
        hits = 0
        predictions = 0
        
        for entry in period_data:
            for m in entry.get('methods', []):
                if m.get('name') == method_name:
                    hits += m.get('hit_count', 0)
                    predictions += m.get('prediction_count', 0)
        
        # Tính tỷ lệ trúng
        hit_rate = hits / max(predictions, 1)
        
        # Thêm vào đặc trưng
        period_features.append(hit_rate)
    
    # Đặc trưng về hiệu suất theo ngày trong tuần
    weekday = current_date.weekday()
    weekday_hits = 0
    weekday_predictions = 0
    
    for entry in history_data:
        entry_date = datetime.strptime(entry['date'], '%Y-%m-%d').date()
        if entry_date.weekday() == weekday:
            for m in entry.get('methods', []):
                if m.get('name') == method_name:
                    weekday_hits += m.get('hit_count', 0)
                    weekday_predictions += m.get('prediction_count', 0)
    
    weekday_hit_rate = weekday_hits / max(weekday_predictions, 1)
    
    # Thêm đặc trưng đặc biệt
    special_features = [
        weekday_hit_rate,  # Tỷ lệ trúng theo ngày trong tuần
        check_monthly_pattern(method, history_data, current_date),  # Mẫu theo tháng
    ]
    
    return period_features + special_features

def check_monthly_pattern(method, history_data, current_date):
    """
    Kiểm tra mẫu theo ngày trong tháng
    
    Args:
        method: Dữ liệu phương pháp
        history_data: Dữ liệu lịch sử
        current_date: Ngày hiện tại
        
    Returns:
        Điểm mẫu tháng từ 0-1
    """
    method_name = method.get('name')
    current_day = current_date.day
    
    # Thu thập hiệu suất cho ngày tương tự trong tháng
    similar_day_hits = 0
    similar_day_predictions = 0
    
    for entry in history_data:
        entry_date = datetime.strptime(entry['date'], '%Y-%m-%d').date()
        if entry_date.day == current_day:
            for m in entry.get('methods', []):
                if m.get('name') == method_name:
                    similar_day_hits += m.get('hit_count', 0)
                    similar_day_predictions += m.get('prediction_count', 0)
    
    similar_day_hit_rate = similar_day_hits / max(similar_day_predictions, 1)
    
    return similar_day_hit_rate

def extract_model_features(method_result, entry_date, history_data):
    """
    Trích xuất các đặc trưng cho mô hình dự đoán
    """
    features = []
    
    # Đảm bảo entry_date là đối tượng date
    if isinstance(entry_date, datetime):
        entry_date = entry_date.date()
    
    # Lấy lịch sử gần đây (30 ngày)
    recent_history = []
    for entry in history_data:
        # Đảm bảo entry['date'] được chuyển đổi thành date
        entry_date_obj = entry['date']
        if isinstance(entry_date_obj, str):
            try:
                entry_date_obj = datetime.strptime(entry_date_obj, '%Y-%m-%d').date()
            except (ValueError, TypeError):
                continue
        elif isinstance(entry_date_obj, datetime):
            entry_date_obj = entry_date_obj.date()
        
        # So sánh date với date
        if entry_date_obj < entry_date:
            recent_history.append(entry)
    
    # Giới hạn chỉ lấy 30 ngày gần nhất
    recent_history = sorted(recent_history, key=lambda x: x['date'], reverse=True)[:30]
    
    # Tính các đặc trưng
    # 1. Tỷ lệ trúng trung bình trong 7 ngày gần nhất
    recent_7day = recent_history[:7]
    hit_rates_7day = []
    for day in recent_7day:
        # Tìm kết quả của phương pháp trong ngày
        method_in_day = next((m for m in day.get('methods', []) if m.get('id') == method_result.get('id')), None)
        if method_in_day:
            pred_count = method_in_day.get('prediction_count', 0)
            hit_count = method_in_day.get('hit_count', 0)
            if pred_count > 0:
                hit_rates_7day.append(hit_count / pred_count)
    
    avg_hit_rate_7day = sum(hit_rates_7day) / len(hit_rates_7day) if hit_rates_7day else 0
    features.append(avg_hit_rate_7day)
    
    # 2. Tỷ lệ trúng trung bình trong 30 ngày
    hit_rates_30day = []
    for day in recent_history:
        method_in_day = next((m for m in day.get('methods', []) if m.get('id') == method_result.get('id')), None)
        if method_in_day:
            pred_count = method_in_day.get('prediction_count', 0)
            hit_count = method_in_day.get('hit_count', 0)
            if pred_count > 0:
                hit_rates_30day.append(hit_count / pred_count)
    
    avg_hit_rate_30day = sum(hit_rates_30day) / len(hit_rates_30day) if hit_rates_30day else 0
    features.append(avg_hit_rate_30day)
    
    # 3. Độ lệch chuẩn của tỷ lệ trúng (độ ổn định)
    std_hit_rate = np.std(hit_rates_30day) if len(hit_rates_30day) > 1 else 0
    features.append(std_hit_rate)
    
    # 4. Xu hướng gần đây (tỷ lệ trúng 7 ngày so với 30 ngày)
    trend = avg_hit_rate_7day - avg_hit_rate_30day
    features.append(trend)
    
    # 5. Số lượng dự đoán trung bình
    avg_predictions = sum(method_in_day.get('prediction_count', 0) 
                         for day in recent_history 
                         for method_in_day in [next((m for m in day.get('methods', []) 
                                                  if m.get('id') == method_result.get('id')), None)]
                         if method_in_day is not None) / len(recent_history) if recent_history else 0
    features.append(avg_predictions)
    
    # 6. Wilson score trung bình
    wilson_scores = []
    for day in recent_history:
        method_in_day = next((m for m in day.get('methods', []) if m.get('id') == method_result.get('id')), None)
        if method_in_day:
            pred_count = method_in_day.get('prediction_count', 0)
            hit_count = method_in_day.get('hit_count', 0)
            if pred_count > 0:
                wilson_scores.append(wilson_score(hit_count, pred_count))
    
    avg_wilson = sum(wilson_scores) / len(wilson_scores) if wilson_scores else 0
    features.append(avg_wilson)
    
    return features
def predict_next_day_success(method, history_data, current_date):
    """
    Dự đoán xác suất thành công cho ngày tiếp theo dựa trên mô hình ML
    """
    try:
        # Huấn luyện mô hình với dữ liệu lịch sử
        model = train_prediction_model(history_data)
        
        # Trích xuất đặc trưng cho phương pháp hiện tại
        features = extract_model_features(method, current_date, history_data)
        
        # Dự đoán xác suất thành công
        prediction = model.predict([features])[0]
        
        # Giới hạn dự đoán trong khoảng [0, 0.95]
        prediction = max(0, min(0.95, prediction))
        
        return prediction
    except Exception:
        # Nếu có lỗi, sử dụng phương pháp đơn giản hơn
        try:
            # Đảm bảo avg_hit_rate là số
            if 'avg_hit_rate' in method:
                avg_hit_rate = float(method.get('avg_hit_rate', 0)) / 100
            else:
                avg_hit_rate = 0
                
            # Đảm bảo trend là số
            if 'trend' in method:
                try:
                    trend = float(method.get('trend', 0)) / 100
                except (ValueError, TypeError):
                    trend = 0
            else:
                trend = 0
            
            # Tính xác suất đơn giản dựa trên tỷ lệ trúng trung bình và xu hướng
            simple_prediction = max(0, min(0.95, avg_hit_rate * (1 + trend)))
            
            return simple_prediction
        except Exception as inner_e:
            # Nếu vẫn lỗi, trả về giá trị mặc định an toàn
            return 0.5

def select_optimal_method_ensemble(ranked_methods, max_methods=5, min_methods=3):
    """
    Chọn tập hợp phương pháp tối ưu dựa trên xếp hạng và đa dạng
    
    Args:
        ranked_methods: Danh sách phương pháp đã được xếp hạng
        max_methods: Số lượng phương pháp tối đa trong tập hợp
        min_methods: Số lượng phương pháp tối thiểu cần chọn
        
    Returns:
        Danh sách các phương pháp tối ưu đã được chọn
    """
    if not ranked_methods:
        return []
        
    if len(ranked_methods) <= min_methods:
        return ranked_methods
    
    # Chọn phương pháp tốt nhất làm điểm khởi đầu
    selected_methods = [ranked_methods[0]]
    candidates = ranked_methods[1:]
    
    while len(selected_methods) < max_methods and candidates:
        best_candidate = None
        best_score = -1
        
        for candidate in candidates:
            # Tính điểm tổng hợp = 70% điểm xếp hạng + 30% điểm đa dạng
            ranking_score = candidate.get('ranking_score', 0)
            
            try:
                diversity = calculate_ensemble_diversity(candidate, selected_methods)
            except Exception as e:
                # Xử lý lỗi, gán giá trị mặc định cho diversity
                diversity = 50
            
            combined_score = ranking_score * 0.7 + diversity * 0.3
            
            if combined_score > best_score:
                best_score = combined_score
                best_candidate = candidate
        
        if best_candidate:
            selected_methods.append(best_candidate)
            candidates.remove(best_candidate)
        else:
            break
    
    return selected_methods
def calculate_ensemble_diversity(candidate, selected_methods):
    """
    Tính độ đa dạng của một phương pháp ứng viên so với các phương pháp đã chọn
    
    Args:
        candidate: Phương pháp ứng viên cần đánh giá
        selected_methods: Danh sách các phương pháp đã được chọn
        
    Returns:
        Điểm đa dạng từ 0-100, cao hơn = đa dạng hơn
    """
    if not selected_methods:
        return 100  # Phương pháp đầu tiên luôn được đánh giá là đa dạng nhất
    
    # Lấy các đặc trưng từ candidate
    cand_group = candidate.get('group', 'unknown')
    cand_hit_rate = candidate.get('avg_hit_rate', 0)
    cand_confidence = candidate.get('avg_confidence', 0)
    
    # Sử dụng stability_score nếu có, nếu không thì sử dụng avg_consistency
    cand_stability = candidate.get('stability_score', candidate.get('avg_consistency', 0))
    
    # Danh sách số được dự đoán
    cand_numbers = set(candidate.get('predicted_numbers', []))
    
    # Tính toán độ đa dạng dựa trên các tiêu chí
    group_diversity = 100  # Điểm mặc định cao
    hit_rate_diversity = 100
    stability_diversity = 100
    number_overlap_diversity = 100
    
    # Tính điểm đa dạng cho từng tiêu chí
    for method in selected_methods:
        # Nếu cùng nhóm, giảm điểm đa dạng nhóm
        if method.get('group', 'unknown') == cand_group:
            group_diversity -= 25  # Giảm 25 điểm nếu cùng nhóm
        
        # Nếu tỷ lệ trúng tương tự, giảm điểm đa dạng tỷ lệ trúng
        hit_rate_diff = abs(cand_hit_rate - method.get('avg_hit_rate', 0))
        if hit_rate_diff < 10:  # Nếu chênh lệch < 10%
            hit_rate_diversity -= (10 - hit_rate_diff) * 2.5  # Giảm tối đa 25 điểm
        
        # Nếu độ ổn định tương tự, giảm điểm đa dạng độ ổn định
        method_stability = method.get('stability_score', method.get('avg_consistency', 0))
        stability_diff = abs(cand_stability - method_stability)
        if stability_diff < 10:  # Nếu chênh lệch < 10%
            stability_diversity -= (10 - stability_diff) * 2.5  # Giảm tối đa 25 điểm
        
        # Nếu có nhiều số trùng lặp, giảm điểm đa dạng số
        method_numbers = set(method.get('predicted_numbers', []))
        if cand_numbers and method_numbers:
            overlap_ratio = len(cand_numbers.intersection(method_numbers)) / max(len(cand_numbers), 1)
            number_overlap_diversity -= overlap_ratio * 60  # Giảm tối đa 60 điểm nếu trùng 100%
    
    # Tính trung bình cộng các điểm đa dạng, với trọng số khác nhau
    overall_diversity = (
        group_diversity * 0.3 +
        hit_rate_diversity * 0.2 +
        stability_diversity * 0.2 +
        number_overlap_diversity * 0.3
    )
    
    # Đảm bảo điểm đa dạng nằm trong khoảng 0-100
    return max(0, min(100, overall_diversity))

def wilson_score(hits, total, confidence=0.95):
    """
    Tính điểm Wilson score - thước đo thống kê đáng tin cậy hơn cho tỷ lệ thành công
    khi có mẫu kích thước nhỏ
    """
    if total == 0:
        return 0
    # z-score cho mức độ tin cậy 95%
    z = 1.96
    phat = float(hits) / total
    return (phat + z*z/(2*total) - z * math.sqrt((phat*(1-phat)+z*z/(4*total))/total))/(1+z*z/total)

def determine_method_group(method):
    """
    Xác định nhóm của phương pháp dựa trên tên hoặc đặc điểm
    """
    name = method.get('name', '').lower()
    code = method.get('code', '').lower()
    
    if any(term in name or term in code for term in ['statistical', 'thống kê', 'frequency', 'tần suất']):
        return 'statistical'
    elif any(term in name or term in code for term in ['pattern', 'mẫu']):
        return 'pattern'
    elif any(term in name or term in code for term in ['cycle', 'chu kỳ']):
        return 'cycle'
    elif any(term in name or term in code for term in ['combination', 'kết hợp']):
        return 'combination'
    elif any(term in name or term in code for term in ['historical', 'lịch sử']):
        return 'historical'
    else:
        return 'other'

def enhance_method_performance(methods_data):
    """
    Cải thiện đánh giá hiệu suất của phương pháp bằng cách sử dụng 
    điểm Wilson score và đặt ngưỡng dự đoán tối thiểu
    """
    enhanced_methods = []
    
    for method in methods_data:
        # Bỏ qua phương pháp có quá ít dự đoán (dưới 5)
        if method['prediction_count'] < 5:
            continue
            
        # Tính toán Wilson score đã được tính trong vòng lặp chính
        confidence_score = method.get('confidence_score', 0)
        
        # Tính hiệu suất trọng số (cân nhắc cả tỷ lệ trúng và số lượng dự đoán)
        weighted_performance = confidence_score * (1 + math.log(method['prediction_count'] + 1, 10))
        
        # Sao chép và bổ sung thông tin phương pháp
        enhanced_method = method.copy()
        enhanced_method.update({
            'weighted_performance': weighted_performance
        })
        
        enhanced_methods.append(enhanced_method)
    
    # Sắp xếp theo hiệu suất trọng số
    return sorted(enhanced_methods, key=lambda x: x['weighted_performance'], reverse=True)

def group_methods(methods):
    """
    Phân nhóm các phương pháp theo loại
    """
    groups = defaultdict(list)
    for method in methods:
        group = method.get('group', 'other')
        groups[group].append(method)
    return groups

def select_top_methods_from_groups(method_groups, max_per_group=3, max_total=20):
    """
    Chọn các phương pháp tốt nhất từ mỗi nhóm để đảm bảo tính đa dạng
    """
    selected_methods = []
    
    # Lấy top N phương pháp từ mỗi nhóm
    for group, methods in method_groups.items():
        selected_methods.extend(methods[:max_per_group])
    
    # Sắp xếp lại theo hiệu suất và giới hạn tổng số
    selected_methods = sorted(selected_methods, key=lambda x: x['weighted_performance'], reverse=True)
    return selected_methods[:max_total]

def get_historical_data(analysis_date, days_back=90):
    """
    Lấy dữ liệu lịch sử từ cơ sở dữ liệu
    """
    start_date = analysis_date - timedelta(days=days_back)
    
    # Lấy kết quả xổ số trong khoảng thời gian
    draw_results = KetQuaXoSo.objects.filter(
        ngay__gte=start_date,
        ngay__lt=analysis_date
    ).order_by('ngay')
    
    # Lấy các dự đoán trong khoảng thời gian
    predictions = DanDeDacBietAllPrize.objects.filter(
        analysis_date__gte=start_date,
        analysis_date__lt=analysis_date
    ).order_by('analysis_date')
    
    # Tổ chức dữ liệu theo ngày
    history_data = []
    
    for result in draw_results:
        result_date = result.ngay
        
        # Lấy tất cả số 2 chữ số
        if hasattr(result, 'get_all_2digit_numbers'):
            winning_numbers = result.get_all_2digit_numbers()
        else:
            winning_numbers = extract_all_2digit_numbers(result)
        
        # Lấy dự đoán cho ngày trước kết quả này
        pred_date = result_date - timedelta(days=1)
        daily_predictions = predictions.filter(analysis_date=pred_date)
        
        for dan_de in daily_predictions:
            prediction_results = PredictionDeAllPrizeResult.objects.filter(dan_de=dan_de)
            
            methods_results = []
            for pred in prediction_results:
                predicted_nums = get_prediction_numbers(pred)
                hit_count = sum(1 for num in predicted_nums if num in winning_numbers)
                
                methods_results.append({
                    'name': pred.method.name,
                    'predicted_numbers': predicted_nums,
                    'prediction_count': len(predicted_nums),
                    'hit_count': hit_count,
                    'hit_rate': (hit_count / len(predicted_nums) * 100) if predicted_nums else 0
                })
            
            history_data.append({
                'date': result_date.strftime('%Y-%m-%d'),
                'winning_numbers': winning_numbers,
                'methods': methods_results
            })
    
    return history_data

def analyze_performance_trends(methods, history_data, winning_numbers, time_periods=[30, 60, 90]):
    """
    Phân tích xu hướng hiệu suất của phương pháp theo thời gian
    """
    now = timezone.now().date()
    
    for method in methods:
        method['performance_trend'] = []
        
        for period in time_periods:
            # Tính hiệu suất trong khoảng thời gian nhất định
            start_date = now - timedelta(days=period)
            
            # Lọc lịch sử kết quả trong khoảng thời gian
            period_history = [entry for entry in history_data 
                             if start_date <= datetime.strptime(entry['date'], '%Y-%m-%d').date() <= now]
            
            # Tính tỷ lệ trúng trong khoảng thời gian này
            hits = 0
            predictions = 0
            
            for entry in period_history:
                method_results = next((m for m in entry.get('methods', []) 
                                    if m.get('name') == method.get('name')), None)
                if method_results:
                    hits += method_results.get('hit_count', 0)
                    predictions += method_results.get('prediction_count', 0)
            
            # Tính tỷ lệ trúng và điểm tin cậy
            hit_rate = (hits / predictions * 100) if predictions > 0 else 0
            confidence = wilson_score(hits, predictions) if predictions > 0 else 0
            
            method['performance_trend'].append({
                'period': period,
                'hit_rate': hit_rate,
                'confidence': confidence,
                'predictions': predictions,
                'hits': hits
            })
        
        # Xác định xu hướng hiệu suất (tăng/giảm/ổn định)
        if len(method['performance_trend']) >= 2:
            short_term = method['performance_trend'][0]['confidence']
            long_term = method['performance_trend'][-1]['confidence']
            
            if short_term > long_term * 1.1:
                method['trend'] = 'increasing'
            elif short_term < long_term * 0.9:
                method['trend'] = 'decreasing'
            else:
                method['trend'] = 'stable'
        else:
            method['trend'] = 'unknown'
        
        # Kiểm tra xem phương pháp có dự đoán đúng số nào trong kết quả hiện tại không
        if winning_numbers:
            hits = sum(1 for num in method.get('predicted_numbers', []) if num in winning_numbers)
            method['current_hits'] = hits
            method['current_hit_rate'] = (hits / method['prediction_count'] * 100) if method['prediction_count'] > 0 else 0

def generate_diverse_predictions(selected_methods, winning_numbers, max_predictions=30):
    """
    Tạo danh sách dự đoán đa dạng từ các phương pháp được chọn
    """
    # Thu thập tất cả dự đoán từ các phương pháp được chọn
    all_predictions = []
    for method in selected_methods:
        for num in method.get('predicted_numbers', []):
            all_predictions.append({
                'number': num,
                'method': method.get('name'),
                'confidence': method.get('confidence_score', 0),
                'group': method.get('group', 'other')
            })
    
    # Tổng hợp dự đoán trùng lặp và tính điểm tổng hợp
    number_scores = defaultdict(lambda: {'score': 0, 'methods': [], 'groups': set()})
    
    for pred in all_predictions:
        num = pred['number']
        number_scores[num]['score'] += pred['confidence']
        number_scores[num]['methods'].append(pred['method'])
        number_scores[num]['groups'].add(pred['group'])
    
    # Chuyển đổi thành danh sách và thêm thông tin đa dạng (số nhóm khác nhau)
    predictions_list = []
    for num, data in number_scores.items():
        # Bổ sung thêm điểm cho số được dự đoán bởi nhiều nhóm phương pháp khác nhau
        diversity_bonus = len(data['groups']) / 5  # Tối đa 1.0 cho 5 nhóm
        
        predictions_list.append({
            'number': num,
            'score': data['score'] * (1 + diversity_bonus) * 100,  # Tăng điểm cho dự đoán đa dạng
            'method_count': len(set(data['methods'])),
            'methods': list(set(data['methods'])),
            'group_count': len(data['groups']),
            'groups': list(data['groups']),
            'is_hit': num in winning_numbers,
            'reasons': generate_prediction_reasons(num, data)
        })
    
    # Sắp xếp theo điểm và giới hạn số lượng
    predictions_list.sort(key=lambda x: x['score'], reverse=True)
    return predictions_list[:max_predictions]

def generate_prediction_reasons(number, data):
    """
    Tạo danh sách lý do giải thích tại sao số này được đề xuất
    """
    reasons = []
    
    # Lý do 1: Xuất hiện trong nhiều phương pháp
    if len(data['methods']) > 1:
        reasons.append(f"Xuất hiện trong {len(data['methods'])} phương pháp dự đoán")
    
    # Lý do 2: Thuộc nhiều nhóm phương pháp
    if len(data['groups']) > 1:
        group_names = {
            'statistical': 'Thống kê',
            'pattern': 'Mẫu',
            'cycle': 'Chu kỳ',
            'combination': 'Kết hợp',
            'historical': 'Lịch sử',
            'other': 'Khác'
        }
        group_list = [group_names.get(g, g) for g in data['groups']]
        reasons.append(f"Xuất hiện trong {len(data['groups'])} nhóm phương pháp ({', '.join(group_list)})")
    
    # Lý do 3: Đề xuất bởi phương pháp có hiệu suất cao
    top_methods = [m for m in data['methods'] if 'top' in m.lower() or 'cao' in m.lower()]
    if top_methods:
        reasons.append(f"Được dự đoán bởi phương pháp hiệu suất cao: {', '.join(top_methods[:2])}")
    
    return reasons

def get_historical_hits(analysis_date, days_back=30):
    """
    Lấy và phân tích các số trúng trong lịch sử
    """
    start_date = analysis_date - timedelta(days=days_back)
    
    # Lấy kết quả xổ số trong khoảng thời gian
    historical_results = KetQuaXoSo.objects.filter(
        ngay__gte=start_date,
        ngay__lt=analysis_date
    ).order_by('ngay')
    
    # Tìm các số thường trúng trong lịch sử
    historical_hits = []
    
    for result in historical_results:
        # Lấy tất cả số 2 chữ số
        if hasattr(result, 'get_all_2digit_numbers'):
            numbers = result.get_all_2digit_numbers()
        else:
            numbers = extract_all_2digit_numbers(result)
            
        historical_hits.extend(numbers)
    
    # Đếm tần suất trúng của mỗi số
    historical_hit_counts = Counter(historical_hits)
    
    return historical_hits, historical_hit_counts

def analyze_cycles(analysis_date, all_predictions, method_counts, winning_numbers, days_back=60):
    """
    Phân tích chu kỳ xuất hiện của các số
    """
    start_date = analysis_date - timedelta(days=days_back)
    
    # Lấy tất cả kết quả xổ số trong khoảng thời gian, sắp xếp theo ngày
    recent_results = KetQuaXoSo.objects.filter(
        ngay__gte=start_date,
        ngay__lt=analysis_date
    ).order_by('ngay')
    
    # Tạo dictionary để lưu lần xuất hiện gần nhất của mỗi số
    last_appearance = {}
    # Tạo set tất cả các số có thể từ 00-99
    all_possible_numbers = {f"{i:02d}" for i in range(100)}
    
    # Khởi tạo với giá trị None
    for num in all_possible_numbers:
        last_appearance[num] = None
    
    # Duyệt qua từng ngày để xác định chu kỳ xuất hiện của các số
    for result in recent_results:
        result_date = result.ngay
        
        # Lấy tất cả số 2 chữ số
        if hasattr(result, 'get_all_2digit_numbers'):
            numbers = result.get_all_2digit_numbers()
        else:
            numbers = extract_all_2digit_numbers(result)
        
        # Cập nhật lần xuất hiện gần nhất
        for num in numbers:
            last_appearance[num] = result_date
    
    # Tính số ngày kể từ lần xuất hiện gần nhất cho mỗi số
    cycle_analysis = []
    
    for num in all_possible_numbers:
        if num in all_predictions:
            if last_appearance[num]:
                days_since_last = (analysis_date - last_appearance[num]).days
            else:
                days_since_last = days_back  # Giả định là lâu hơn khoảng thời gian phân tích
            
            cycle_analysis.append({
                'number': num,
                'last_appearance': last_appearance[num],
                'days_since_last': days_since_last,
                'method_count': method_counts.get(num, 0),
                'is_hit': num in winning_numbers,
                # Thêm điểm chu kỳ - số ngày không xuất hiện nhân với số phương pháp dự đoán
                'cycle_score': days_since_last * method_counts.get(num, 0) / 10
            })
    
    # Sắp xếp theo số ngày từ lần xuất hiện gần nhất và số phương pháp
    cycle_analysis.sort(key=lambda x: (x['days_since_last'], x['method_count']), reverse=True)
    
    return cycle_analysis

def extract_all_2digit_numbers(ket_qua):
    """
    Trích xuất tất cả các số 2 chữ số từ kết quả xổ số
    """
    numbers = []
    
    # Trích xuất từ giải đặc biệt
    if hasattr(ket_qua, 'giai_db') and ket_qua.giai_db:
        if len(ket_qua.giai_db) >= 2:
            numbers.append(ket_qua.giai_db[-2:])
    
    # Trích xuất từ các giải khác
    for i in range(1, 8):
        field_name = f'giai_{i}'
        if hasattr(ket_qua, field_name):
            giai_values = getattr(ket_qua, field_name)
            
            # Xử lý nếu là chuỗi ngăn cách bằng dấu phẩy
            if isinstance(giai_values, str):
                for val in giai_values.split(','):
                    val = val.strip()
                    if len(val) >= 2:
                        numbers.append(val[-2:])
            # Xử lý nếu là list
            elif isinstance(giai_values, list):
                for val in giai_values:
                    if isinstance(val, str) and len(val) >= 2:
                        numbers.append(val[-2:])
    
    return sorted(list(set(numbers)))  # Loại bỏ trùng lặp
