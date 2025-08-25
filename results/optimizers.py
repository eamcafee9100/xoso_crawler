import time
import logging
import numpy as np
import math
from .models import OptimalMethodEnsemble, DanDeDacBietAllPrize, PredictionDeAllPrizeResult, PredictionMethodAllPrize, KetQuaXoSo
from collections import defaultdict
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
import copy
logger = logging.getLogger(__name__)

class MethodOptimizerService:
    """
    Lớp dịch vụ xử lý tối ưu hóa phương pháp dự đoán
    """
    def __init__(self, analysis_date):
        self.analysis_date = analysis_date
        self.start_time = time.time()
        self.next_day = analysis_date + timedelta(days=1)
        self.winning_numbers = []
        self._load_winning_numbers()
    
    def _load_winning_numbers(self):
        """Tải danh sách số trúng của ngày tiếp theo"""
        try:
            next_day_ket_qua = KetQuaXoSo.objects.filter(ngay=self.next_day).first()
            if next_day_ket_qua:
                if hasattr(next_day_ket_qua, 'get_all_2digit_numbers'):
                    self.winning_numbers = next_day_ket_qua.get_all_2digit_numbers()
                else:
                    from .utils import extract_all_2digit_numbers
                    self.winning_numbers = extract_all_2digit_numbers(next_day_ket_qua)
        except Exception as e:
            logger.error(f"Lỗi khi tải số trúng: {str(e)}")
    
    def load_methods_data(self):
        """Tải dữ liệu phương pháp từ cơ sở dữ liệu"""
        try:
            # Lấy DanDeDacBietAllPrize cho ngày phân tích
            dan_de = DanDeDacBietAllPrize.objects.get(analysis_date=self.analysis_date)
            
            # Lấy tất cả kết quả dự đoán
            prediction_results = PredictionDeAllPrizeResult.objects.filter(dan_de=dan_de)
            if not prediction_results.exists():
                logger.error(f"Không có kết quả dự đoán cho ngày {self.analysis_date}")
                return []
            
            # Lấy danh sách phương pháp
            method_ids = prediction_results.values_list('method_id', flat=True).distinct()
            methods = PredictionMethodAllPrize.objects.filter(id__in=method_ids)
            
            # Tạo từ điển để truy cập nhanh các kết quả theo method_id
            method_to_results = {}
            for method in methods:
                method_results = prediction_results.filter(method=method)
                method_to_results[method.id] = list(method_results)
            
            # Tạo dữ liệu phương pháp
            methods_data = []
            for method in methods:
                # Thu thập tất cả số dự đoán
                predicted_numbers = []
                for result in method_to_results[method.id]:
                    from .utils import get_prediction_numbers
                    numbers = get_prediction_numbers(result)
                    predicted_numbers.extend(numbers)
                
                # Loại bỏ trùng lặp
                predicted_numbers = sorted(list(set(predicted_numbers)))
                
                # Tìm số trúng
                hit_numbers = []
                if self.winning_numbers:
                    hit_numbers = [num for num in predicted_numbers if num in self.winning_numbers]
                
                # Tạo dữ liệu cho phương pháp
                method_data = {
                    'id': method.id,
                    'name': method.name,
                    'code': method.code,
                    'predicted_numbers': predicted_numbers,
                    'prediction_count': len(predicted_numbers),
                    'hit_numbers': hit_numbers,
                    'hit_count': len(hit_numbers),
                    'hit_rate': (len(hit_numbers) / len(predicted_numbers) * 100) if predicted_numbers else 0
                }
                
                # Thêm tính toán Wilson score
                from .utils import wilson_score
                method_data['confidence_score'] = wilson_score(len(hit_numbers), len(predicted_numbers))
                
                # Thêm nhóm phương pháp
                from .utils import determine_method_group
                method_data['group'] = determine_method_group(method_data)
                
                methods_data.append(method_data)
            
            return methods_data
        except Exception as e:
            logger.error(f"Lỗi khi tải dữ liệu phương pháp: {str(e)}")
            return []
    
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
            from .utils import enhance_method_performance, group_methods, select_top_methods_from_groups
            enhanced_methods = enhance_method_performance(methods_data)
            method_groups = group_methods(enhanced_methods)
            selected_methods = select_top_methods_from_groups(method_groups)
            
            # --- CẢI TIẾN: Phân tích xu hướng hiệu suất ---
            from .utils import get_historical_data, analyze_performance_trends
            history_data = get_historical_data(self.analysis_date, 90)
            analyze_performance_trends(selected_methods, history_data, self.winning_numbers)
            
            # --- CẢI TIẾN: Xếp hạng phương pháp dự đoán đa chiều ---
            from .utils import rank_prediction_methods
            ranked_methods = rank_prediction_methods(enhanced_methods, history_data, self.analysis_date, self.winning_numbers)
            
            # --- CẢI TIẾN: Chọn tập hợp phương pháp tối ưu và đa dạng ---
            from .utils import select_optimal_method_ensemble
            optimal_methods = select_optimal_method_ensemble(ranked_methods, max_methods=max_methods)
            
            # --- CẢI TIẾN: Tính toán lợi nhuận cho các phương pháp được chọn ---
            from .calculate_profit import calculate_profit
            for method in optimal_methods:
                method['profit_analysis'] = calculate_profit(method)
            
            # Lưu kết quả vào cơ sở dữ liệu
            calculation_time = time.time() - start_time
            ensemble, created = OptimalMethodEnsemble.objects.update_or_create(
                analysis_date=self.analysis_date,
                defaults={
                    'calculation_time': calculation_time,
                }
            )
            
            # Chỉ lưu top 20 phương pháp đã xếp hạng để tiết kiệm dung lượng
            ensemble.set_ranked_methods(ranked_methods[:20] if ranked_methods else [])
            ensemble.set_optimal_methods(optimal_methods)
            ensemble.save()
            
            logger.info(f"Hoàn thành tối ưu hóa phương pháp cho ngày {self.analysis_date} trong {calculation_time:.2f}s")
            return ensemble
        
        except Exception as e:
            logger.error(f"Lỗi khi tối ưu hóa phương pháp: {str(e)}", exc_info=True)
            return None