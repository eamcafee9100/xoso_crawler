import ast
import copy
import json
import locale
import random
import re
import threading
import time
from calendar import monthrange
from collections import Counter, defaultdict
from datetime import date, datetime, timedelta

import numpy as np  # Import from your models
import pandas as pd
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.cache import cache
from django.core.paginator import Paginator
from django.db import models, transaction
from django.db.models import (
    Avg,
    BooleanField,
    Case,
    Count,
    FloatField,
    Prefetch,
    Q,
    When,
)
from django.http import HttpResponse, JsonResponse
from django.shortcuts import redirect, render
from django.urls import reverse_lazy
from django.utils import timezone
from django.utils.dateparse import parse_date
from django.views import View
from django.views.decorators.cache import cache_page
from django.views.generic import (
    CreateView,
    DeleteView,
    DetailView,
    FormView,
    ListView,
    TemplateView,
    UpdateView,
)
from sklearn.dummy import DummyRegressor

from results.analytics.predictors import BachThuLoPredictor
from results.models import CycleAccuracy  # Thêm import này
from results.models import (
    AccuracyTrend,
    DailyPredictionAnalysis,
    KetQuaXoSo,
    MethodWeightsHistory,
    NumberFrequencyStats,
    PredictionPerformanceMetrics,
)
from results.services.EnhancedMLModelTrainer import EnhancedMLModelTrainer
from results.services.EnhancedPredictionCacheService import (
    EnhancedPredictionCacheService,
)
from results.services.MLModelService import MLModelService
from results.services.PredictionService import PredictionService
from results.services.SHAPAnalysisService import SHAPAnalysisService

from .analytics.performance_evaluator import PerformanceEvaluator
from .analytics.prediction_analyzer import PredictionAnalyzer
from .bach_thu_methods import get_all_bach_thu_methods, get_method_by_code
from .crawler import crawl_thang_4, crawl_xoso_thantai
from .crawlers import crawl_xsmb_ketquame
from .forms import BachThuPredictionForm, ImportKetQuaForm
from .models import (
    BachThuLoAnalysis,
    BachThuLoMethod,
    BachThuLoResult,
    BachThuLoStatistics,
    BtlAnalytics,
    BtlMethodAnalytics,
    BtlTimeAggregation,
    DanBtl,
    DanDeDacBietAllPrize,
    KetQuaXoSo,
    LoKhung2Ngay,
    MethodWeightsHistory,
    NumberFrequencyStats,
    OptimalMethodEnsemble,
    Prediction,
    PredictionDeAllPrizeResult,
    PredictionMethodAllPrize,
    PredictionMethodBtl,
    PredictionModel,
    PredictionPerformanceMetrics,
    PredictionRecord,
    PredictionResultBtl,
)
from .predictor import AdvancedLotteryPredictor, EnhancedCyclePredictor

try:
    locale.setlocale(locale.LC_ALL, "en_US.UTF-8")
except:
    locale.setlocale(locale.LC_ALL, "")

# Hoặc cấu hình logging
import logging

logger = logging.getLogger(__name__)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("debug.log", encoding="utf-8"),
        logging.StreamHandler(),
    ],
    encoding="utf-8",
)
prediction_logger = logging.getLogger("predictions")  # Logger chuyên biệt


class BachThuLoReportView(View):
    template_name = "btl_analysis_report.html"

    def get(self, request):
        try:
            target_date = datetime.now().date()
            selected_date = request.GET.get("selected_date")

            # Tạo phân tích
            analyzer = PredictionAnalyzer()
            analysis_report = analyzer.analyze_predictions(
                target_date=target_date, selected_date=selected_date
            )

            context = {
                "report": analysis_report,
                "summary_table": analysis_report["summary"],
                "recommendations": analysis_report["recommendations"],
                "chart_path": analysis_report["charts"],
            }

            return render(request, "btl_analysis_report.html", context)

        except Exception as e:
            logging.error(f"View error: {str(e)}")
            return HttpResponse("Analysis failed", status=500)


class CrawlThang4View(View):
    def get(self, request):
        # Chạy trong thread riêng để không block request
        def crawl_async():
            crawl_thang_4()

        thread = threading.Thread(target=crawl_async)
        thread.start()

        return JsonResponse({"status": "Đã bắt đầu quá trình crawl tháng 4"})


def crawl_xsmb_view(request):
    """
    View xử lý crawl và xóa dữ liệu xổ số miền Bắc
    """
    results = []
    delete_results = None

    if request.method == "POST":
        # Xác định action từ form
        action = request.POST.get("action", "crawl")

        if action == "delete":
            # Xử lý xóa dữ liệu
            delete_results = _handle_delete_data(request)

        elif action == "crawl":
            # Xử lý crawl dữ liệu (code hiện tại)
            results = _handle_crawl_data(request)

    return render(
        request,
        "results/crawl_form.html",
        {
            "results": results or [],
            "delete_results": delete_results,
            "default_start": (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d"),
            "default_end": datetime.now().strftime("%Y-%m-%d"),
        },
    )


def _handle_delete_data(request):
    """
    Xử lý xóa dữ liệu theo khoảng thời gian

    Returns:
        dict: Kết quả xóa dữ liệu
    """
    try:
        # Kiểm tra rate limiting
        user_ip = get_client_ip(request)
        cache_key = f"last_delete_{user_ip}"
        last_delete_time = cache.get(cache_key)

        current_time = timezone.now()

        # Giới hạn: chỉ cho phép xóa sau mỗi 30 giây
        if last_delete_time and (current_time - last_delete_time).total_seconds() < 30:
            time_to_wait = int(30 - (current_time - last_delete_time).total_seconds())
            messages.warning(
                request, f"Vui lòng đợi {time_to_wait} giây nữa trước khi xóa dữ liệu."
            )
            return {"success": False, "message": "Rate limit exceeded"}

        # Lấy thông tin ngày từ form
        start_date = request.POST.get("delete_start_date")
        end_date = request.POST.get("delete_end_date")
        confirm_delete = request.POST.get("confirm_delete") == "on"

        if not start_date or not end_date:
            messages.error(
                request, "Vui lòng chọn ngày bắt đầu và ngày kết thúc để xóa."
            )
            return {"success": False, "message": "Missing date parameters"}

        if not confirm_delete:
            messages.warning(request, "Vui lòng xác nhận bạn muốn xóa dữ liệu.")
            return {"success": False, "message": "Confirmation required"}

        # Chuyển đổi định dạng ngày
        try:
            start_date_obj = datetime.strptime(start_date, "%Y-%m-%d").date()
            end_date_obj = datetime.strptime(end_date, "%Y-%m-%d").date()
        except ValueError:
            messages.error(
                request,
                "Định dạng ngày không hợp lệ. Vui lòng sử dụng định dạng YYYY-MM-DD.",
            )
            return {"success": False, "message": "Invalid date format"}

        # Validate ngày
        if start_date_obj > end_date_obj:
            messages.error(
                request, "Ngày bắt đầu phải nhỏ hơn hoặc bằng ngày kết thúc."
            )
            return {"success": False, "message": "Invalid date range"}

        # Kiểm tra khoảng thời gian (tối đa 90 ngày)
        days_difference = (end_date_obj - start_date_obj).days
        if days_difference > 90:
            messages.error(
                request, "Chỉ có thể xóa dữ liệu trong khoảng tối đa 90 ngày."
            )
            return {"success": False, "message": "Date range too large"}

        # Thực hiện xóa dữ liệu
        with transaction.atomic():
            # Đếm số bản ghi sẽ bị xóa
            records_to_delete = KetQuaXoSo.objects.filter(
                ngay__gte=start_date_obj, ngay__lte=end_date_obj
            )

            total_records = records_to_delete.count()

            if total_records == 0:
                messages.info(
                    request,
                    f"Không có dữ liệu nào trong khoảng từ {start_date_obj.strftime('%d/%m/%Y')} đến {end_date_obj.strftime('%d/%m/%Y')}.",
                )
                return {
                    "success": True,
                    "deleted_count": 0,
                    "date_range": f"{start_date_obj.strftime('%d/%m/%Y')} - {end_date_obj.strftime('%d/%m/%Y')}",
                    "details": [],
                }

            # Lấy chi tiết các bản ghi sẽ bị xóa
            delete_details = []
            for record in records_to_delete:
                delete_details.append(
                    {
                        "date": record.ngay,
                        "giai_db": record.giai_db,
                        "formatted_date": record.ngay.strftime("%d/%m/%Y"),
                    }
                )

            # Thực hiện xóa
            deleted_count, deleted_details = records_to_delete.delete()

            # Cập nhật cache để ngăn xóa liên tục
            cache.set(cache_key, current_time, 300)  # 5 phút

            # Thông báo thành công
            messages.success(
                request,
                f"Đã xóa thành công {deleted_count} bản ghi từ {start_date_obj.strftime('%d/%m/%Y')} đến {end_date_obj.strftime('%d/%m/%Y')}.",
            )

            # Log hoạt động xóa
            logger.info(
                f"Deleted {deleted_count} records from {start_date_obj} to {end_date_obj} by IP {user_ip}"
            )

            return {
                "success": True,
                "deleted_count": deleted_count,
                "date_range": f"{start_date_obj.strftime('%d/%m/%Y')} - {end_date_obj.strftime('%d/%m/%Y')}",
                "details": delete_details,
            }

    except Exception as e:
        logger.error(f"Error in delete operation: {str(e)}")
        messages.error(request, f"Lỗi khi xóa dữ liệu: {str(e)}")
        return {"success": False, "error": str(e)}


def _handle_crawl_data(request):
    """
    Xử lý crawl dữ liệu (code hiện tại)
    """
    # Kiểm tra giới hạn tần suất truy cập
    user_ip = get_client_ip(request)
    cache_key = f"last_crawl_{user_ip}"
    last_crawl_time = cache.get(cache_key)

    current_time = timezone.now()

    # Giới hạn: chỉ cho phép truy vấn sau mỗi 10 giây
    if last_crawl_time and (current_time - last_crawl_time).total_seconds() < 10:
        time_to_wait = int(10 - (current_time - last_crawl_time).total_seconds())
        messages.warning(
            request, f"Vui lòng đợi {time_to_wait} giây nữa trước khi tải lại dữ liệu."
        )
        return []

    start_date = request.POST.get("start_date")
    end_date = request.POST.get("end_date")

    try:
        # Chuyển đổi từ YYYY-MM-DD (HTML date input) sang DD-MM-YYYY (dùng cho crawler)
        start_date_obj = datetime.strptime(start_date, "%Y-%m-%d")
        end_date_obj = datetime.strptime(end_date, "%Y-%m-%d")
        start_date_str = start_date_obj.strftime("%d-%m-%Y")
        end_date_str = end_date_obj.strftime("%d-%m-%Y")

        if start_date_obj > end_date_obj:
            messages.error(request, "Ngày bắt đầu phải nhỏ hơn hoặc bằng ngày kết thúc")
            return []

        days_difference = (end_date_obj - start_date_obj).days

        # Kiểm tra khoảng thời gian và đặt giới hạn tải cho khoảng thời gian dài
        if days_difference > 400:  # Hơn 1 năm
            messages.warning(
                request,
                "Đối với khoảng thời gian lớn hơn 1 năm, hệ thống sẽ tải từng đợt. Vui lòng chia nhỏ khoảng thời gian.",
            )
            return []

        # Thông báo về thời gian dự kiến
        if days_difference > 90:
            estimated_time = days_difference * 0.1  # Ước tính 0.1 giây mỗi ngày
            messages.info(
                request,
                f"Bạn đang tải dữ liệu cho {days_difference} ngày. Quá trình này có thể mất khoảng {int(estimated_time)} giây.",
            )

        # Tạo cache để ngăn yêu cầu quá thường xuyên
        cache.set(
            cache_key, current_time, 300
        )  # Lưu trữ thời gian truy cập trong 5 phút

        # Tách thành các đợt nhỏ nếu khoảng thời gian lớn
        if days_difference > 30:
            # Chia thành các đợt nhỏ, mỗi đợt tối đa 30 ngày
            batch_results = []
            current_date = start_date_obj

            while current_date <= end_date_obj:
                # Tính ngày kết thúc của đợt này
                batch_end_date = min(current_date + timedelta(days=29), end_date_obj)

                # Chuyển đổi định dạng ngày
                current_date_str = current_date.strftime("%d-%m-%Y")
                batch_end_date_str = batch_end_date.strftime("%d-%m-%Y")

                # Thông báo đợt đang tải
                messages.info(
                    request,
                    f"Đang tải dữ liệu từ {current_date_str} đến {batch_end_date_str}...",
                )

                # Gọi hàm crawl cho đợt này
                batch_result = crawl_xsmb_ketquame(current_date_str, batch_end_date_str)
                batch_results.extend(batch_result)

                # Thêm độ trễ ngẫu nhiên giữa các đợt để giảm tải cho server
                delay_time = random.uniform(2.5, 5.0)  # Độ trễ từ 2.5 đến 5 giây
                time.sleep(delay_time)

                # Cập nhật ngày bắt đầu cho đợt tiếp theo
                current_date = batch_end_date + timedelta(days=1)

            results = batch_results
        else:
            # Nếu khoảng thời gian nhỏ, tải tất cả cùng lúc
            results = crawl_xsmb_ketquame(start_date_str, end_date_str)

        # Thống kê kết quả an toàn
        success_count = sum(
            1 for r in results if isinstance(r, dict) and r.get("success")
        )
        total_days = len(results) if results else 0
        if success_count > 0:
            messages.success(
                request, f"Đã tải thành công {success_count}/{total_days} ngày"
            )
        else:
            messages.warning(request, "Không tải được kết quả nào")

        return results

    except ValueError as e:
        messages.error(request, f"Định dạng ngày không hợp lệ: {str(e)}")
        return []
    except Exception as e:
        messages.error(request, f"Lỗi hệ thống: {str(e)}")
        logger.error(f"Lỗi trong crawl_xsmb_view: {str(e)}")
        return []


def get_client_ip(request):
    """Lấy địa chỉ IP của client"""
    x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
    if x_forwarded_for:
        ip = x_forwarded_for.split(",")[0]
    else:
        ip = request.META.get("REMOTE_ADDR")
    return ip


def predict_view(request):
    accuracy = 0.0
    context = {}
    model_name = "HybridPredictor"

    try:
        # 1. Khởi tạo predictor
        predictor = HybridPredictor()

        # 2. Xử lý ngày được chọn
        selected_date = date.today()
        if request.method == "POST":
            try:
                selected_date = datetime.strptime(
                    request.POST.get("selected_date", ""), "%Y-%m-%d"
                ).date()
                if selected_date > date.today():
                    selected_date = date.today()
                    messages.warning(
                        request, "Không thể dự đoán tương lai. Sử dụng ngày hôm nay."
                    )
            except (ValueError, TypeError):
                messages.warning(request, "Ngày không hợp lệ. Sử dụng ngày hôm nay.")

        # 3. Lấy dữ liệu lịch sử và chuyển thành list
        history_query = KetQuaXoSo.objects.filter(ngay__lt=selected_date).order_by(
            "-ngay"
        )[:30]
        history = list(history_query)  # Chuyển thành list để tránh lỗi reverse()

        if not history:
            messages.error(request, "Không đủ dữ liệu lịch sử để phân tích")
            return render(request, "results/predict.html", context)

        # 4. Thực hiện dự đoán với kiểm tra dữ liệu
        try:
            # Chuẩn bị dữ liệu training
            training_data = [
                x.giai_db for x in history if x.giai_db
            ]  # Ví dụ lấy giải đặc biệt
            if training_data:
                training_data = np.array(training_data).reshape(
                    -1, 1
                )  # Chuyển thành 2D array
            else:
                training_data = np.zeros((1, 1))  # Dữ liệu mặc định nếu rỗng

            result = predictor.predict(selected_date, history)
        except Exception as e:
            messages.error(request, f"Lỗi khi dự đoán: {str(e)}")
            logger.error(f"Lỗi khi train model: {str(e)}", exc_info=True)
            result = {"predicted_numbers": [], "cycle_analysis": {}, "hot_pairs": []}

        # 5. Xử lý kết quả thực tế
        actual_result = KetQuaXoSo.objects.filter(ngay=selected_date).first()
        actual_numbers = (
            set(actual_result.get_all_2digit_numbers()) if actual_result else set()
        )

        # 6. Tính độ chính xác
        predicted_numbers = [num for num, _ in result.get("predicted_numbers", [])]
        hit_count = (
            len(actual_numbers & set(predicted_numbers))
            if (actual_result and predicted_numbers)
            else 0
        )
        accuracy = (
            (hit_count / len(predicted_numbers)) * 100 if predicted_numbers else 0
        )

        # Chuẩn bị dữ liệu chu kỳ với đánh dấu số trúng
        if actual_result:
            actual_numbers = set(actual_result.get_all_2digit_numbers())
            # Xử lý từng chu kỳ
            for cycle_name, cycle_data in result.get("cycle_analysis", {}).items():
                predicted_numbers = [
                    num for num, _ in cycle_data.get("top_frequency", [])
                ]
                hit_numbers = set(predicted_numbers) & actual_numbers
                cycle_data["hit_numbers"] = hit_numbers  # Thêm thông tin số trúng

        def analyze_combined_cycles(history, cycle_days):
            from itertools import combinations

            # Thống kê số lần xuất hiện
            number_freq = defaultdict(int)
            pair_freq = defaultdict(int)

            for day in cycle_days:
                # Lấy dữ liệu trong khoảng day ngày
                cycle_data = history[:day]

                # Thống kê số đơn
                for result in cycle_data:
                    numbers = result.get_all_2digit_numbers()
                    for num in numbers:
                        number_freq[num] += 1

                # Thống kê cặp số
                for result in cycle_data:
                    numbers = result.get_all_2digit_numbers()
                    for pair in combinations(sorted(numbers), 2):
                        pair_freq[pair] += 1

            # Lấy top số và cặp số
            top_numbers = sorted(number_freq.items(), key=lambda x: x[1], reverse=True)[
                :15
            ]
            top_pairs = sorted(pair_freq.items(), key=lambda x: x[1], reverse=True)[:10]
            recommended_pairs = []
            for pair, count in pair_freq.items():
                # Tính điểm dựa trên tần suất và độ "nóng" của từng số
                score = (
                    count * 0.6 + (number_freq[pair[0]] + number_freq[pair[1]]) * 0.4
                )
                recommended_pairs.append((pair, score))

            # Sắp xếp theo điểm
            recommended_pairs.sort(key=lambda x: x[1], reverse=True)
            return {"top_numbers": top_numbers, "top_pairs": top_pairs}

        # Phân tích các chu kỳ
        combined_cycles = {
            "ngắn (1-3-7 ngày)": analyze_combined_cycles(history, [1, 3, 7]),
            "dài (14 ngày)": analyze_combined_cycles(history, [14]),
        }

        # Thêm vào context
        context["combined_cycles"] = combined_cycles
        # 7. Chuẩn bị context với xử lý lỗi đầy đủ
        context.update(
            {
                "selected_date": selected_date,
                "actual_result": actual_result,
                "actual_numbers": actual_numbers,
                "predictions": {
                    "numbers": result.get("predicted_numbers", []),
                    "hit_count": hit_count,
                    "accuracy": round(accuracy, 2),
                    "hot_pairs": result.get("hot_pairs", []),
                },
                "analysis_summary": analyze_common_numbers(result),
                "cycle_analysis": result.get("cycle_analysis", {}),
                "history_count": len(history),
                "history_start_date": (
                    history[0].ngay.strftime("%d/%m/%Y") if history else ""
                ),
                "history_end_date": (
                    history[-1].ngay.strftime("%d/%m/%Y") if history else ""
                ),
                "error": None,
            }
        )

    except Exception as e:
        messages.error(request, f"Đã xảy ra lỗi nghiêm trọng: {str(e)}")
        logger.exception("Lỗi nghiêm trọng trong predict_view")
        context["error"] = str(e)

    return render(request, "results/predict.html", context)


def analyze_common_numbers(result):
    """
    Analyze common numbers across cycles and compare with predictions
    """
    cycle_analysis = result.get("cycle_analysis", {})
    predicted_numbers = result.get("predicted_numbers", [])

    # Extract numbers and frequencies from each cycle
    cycle_numbers = {}
    for cycle_name, data in cycle_analysis.items():
        if cycle_name in ["1_ngay", "3_ngay", "7_ngay", "14_ngay", "30_ngay"]:
            cycle_numbers[cycle_name] = {
                num: freq for num, freq in data.get("top_frequency", [])
            }

    # Find common numbers across cycles
    number_analysis = {}
    for cycle_name, numbers in cycle_numbers.items():
        for num, freq in numbers.items():
            if num not in number_analysis:
                number_analysis[num] = {
                    "appearances": {},
                    "total_freq": 0,
                    "cycle_count": 0,
                    "in_prediction": num in predicted_numbers,
                }
            number_analysis[num]["appearances"][cycle_name] = freq
            number_analysis[num]["total_freq"] += freq
            number_analysis[num]["cycle_count"] += 1

    # Calculate appearance rates and scores
    for num, data in number_analysis.items():
        cycles = data["appearances"].keys()
        data["appearance_rate"] = len(cycles) / len(cycle_numbers)

        # Calculate weighted score based on cycle length
        weighted_score = 0
        for cycle, freq in data["appearances"].items():
            cycle_days = int(cycle.split("_")[0])
            weighted_score += (freq / cycle_days) * (1 / cycle_days)
        data["weighted_score"] = weighted_score

    # Sort numbers by appearance rate and weighted score
    sorted_numbers = sorted(
        number_analysis.items(),
        key=lambda x: (x[1]["cycle_count"], x[1]["weighted_score"], x[1]["total_freq"]),
        reverse=True,
    )

    return {
        "common_numbers": sorted_numbers,
        "total_cycles": len(cycle_numbers),
        "analysis_summary": _generate_analysis_summary(
            sorted_numbers, predicted_numbers
        ),
    }


def _generate_analysis_summary(sorted_numbers, predicted_numbers):
    """Generate summary of number analysis"""
    high_potential = []
    medium_potential = []
    low_potential = []

    for num, data in sorted_numbers:
        score = {
            "number": num,
            "cycle_count": data["cycle_count"],
            "total_freq": data["total_freq"],
            "appearance_rate": data["appearance_rate"] * 100,
            "weighted_score": data["weighted_score"],
            "in_prediction": data["in_prediction"],
        }

        if data["cycle_count"] >= 4 and data["weighted_score"] > 0.5:
            high_potential.append(score)
        elif data["cycle_count"] >= 3 and data["weighted_score"] > 0.3:
            medium_potential.append(score)
        else:
            low_potential.append(score)

    return {
        "high_potential": high_potential[:5],
        "medium_potential": medium_potential[:5],
        "low_potential": low_potential[:5],
    }


def evaluate_prediction_accuracy(self, predicted_numbers):
    """Đánh giá độ chính xác của các dự đoán trước đó"""
    # Lấy kết quả thực tế 3 ngày gần nhất
    actual_results = KetQuaXoSo.objects.filter(ngay__lte=date.today()).order_by(
        "-ngay"
    )[:3]

    hit_count = 0
    total_tests = 0

    for record in actual_results:
        actual_numbers = record.get_all_2digit_numbers()
        hits = set(predicted_numbers) & set(actual_numbers)
        hit_count += len(hits)
        total_tests += len(predicted_numbers)

    return hit_count / total_tests if total_tests > 0 else 0


def determine_optimal_history_range():
    """Xác định khoảng thời gian phân tích tối ưu"""
    # Phân tích cơ bản - có thể nâng cao sau
    total_records = KetQuaXoSo.objects.count()

    if total_records > 365:  # Nếu có đủ dữ liệu 1 năm
        return 180  # 6 tháng
    elif total_records > 180:
        return 90  # 3 tháng
    elif total_records > 60:
        return 30  # 1 tháng
    else:
        return min(30, total_records)  # Số ngày tối đa có thể


def get_last_two_digits(numbers):
    """
    Lấy 2 chữ số cuối từ danh sách các số.
    """
    return [str(num)[-2:] for num in numbers]


def analyze_combinations(predictions_data):
    """Phân tích các tổ hợp xiên 2 và xiên 3 từ dữ liệu dự đoán"""
    from itertools import combinations

    pair_counts = defaultdict(int)
    triple_counts = defaultdict(int)

    for day_prediction in predictions_data:
        numbers = day_prediction.get("numbers", [])

        # Thống kê xiên 2
        for pair in combinations(sorted(numbers), 2):
            pair_counts[pair] += 1

        # Thống kê xiên 3
        for triple in combinations(sorted(numbers), 3):
            triple_counts[triple] += 1

    return pair_counts, triple_counts


def organize_by_first_digit(numbers):
    """Tổ chức số theo chữ số đầu tiên"""
    organized = {}
    for num in numbers:
        # Đảm bảo num là số nguyên
        num_int = int(num) if not isinstance(num, int) else num

        # Xử lý số có 1 chữ số (thêm 0 ở đầu)
        num_str = f"{num_int:02d}"  # Định dạng thành 2 chữ số

        first_digit = num_str[0]  # Lấy chữ số đầu tiên

        if first_digit not in organized:
            organized[first_digit] = []
        organized[first_digit].append(num_int)  # Lưu số nguyên

    # Sắp xếp các số trong mỗi nhóm
    for digit in organized:
        organized[digit].sort()

    return organized


def parse_input_data(content):
    pattern = r"(Thứ [^\t]+|Chủ nhật)\t*\s*Ngày:\s*(\d{2}/\d{2}/\d{4})(.*?)(?=(Thứ [^\t]+|Chủ nhật)\t*\s*Ngày:|\Z)"
    matches = re.findall(pattern, content, re.DOTALL)

    results = []
    for match in matches:
        thu = match[0]
        ngay = datetime.strptime(match[1], "%d/%m/%Y").date()

        # Trích xuất các giải
        giai_db = re.search(r"Giải ĐB\t\t(\d+)", match[2])
        giai_1 = re.search(r"Giải nhất\t\t(\d+)", match[2])
        giai_2 = re.search(r"Giải nhì\t\t([\d -]+)", match[2])
        giai_3 = re.search(r"Giải ba\t\t([\d -]+)", match[2])
        giai_4 = re.search(r"Giải tư\t\t([\d -]+)", match[2])
        giai_5 = re.search(r"Giải năm\t\t([\d -]+)", match[2])
        giai_6 = re.search(r"Giải sáu\t\t([\d -]+)", match[2])
        giai_7 = re.search(r"Giải bảy\t\t([\d -]+)", match[2])

        results.append(
            {
                "thu": thu,
                "ngay": ngay,
                "giai_db": giai_db.group(1) if giai_db else "",
                "giai_1": giai_1.group(1) if giai_1 else "",
                "giai_2": giai_2.group(1).strip() if giai_2 else "",
                "giai_3": giai_3.group(1).strip() if giai_3 else "",
                "giai_4": giai_4.group(1).strip() if giai_4 else "",
                "giai_5": giai_5.group(1).strip() if giai_5 else "",
                "giai_6": giai_6.group(1).strip() if giai_6 else "",
                "giai_7": giai_7.group(1).strip() if giai_7 else "",
            }
        )

    return results


def import_to_db(data_list):
    success_count = 0
    for data in data_list:
        try:
            KetQuaXoSo.objects.update_or_create(
                ngay=data["ngay"],
                defaults={
                    "thu": data["thu"],
                    "giai_db": data["giai_db"],
                    "giai_1": data["giai_1"],
                    "giai_2": data["giai_2"].replace(" - ", ", "),
                    "giai_3": data["giai_3"].replace(" - ", ", "),
                    "giai_4": data["giai_4"].replace(" - ", ", "),
                    "giai_5": data["giai_5"].replace(" - ", ", "),
                    "giai_6": data["giai_6"].replace(" - ", ", "),
                    "giai_7": data["giai_7"].replace(" - ", ", "),
                },
            )
            success_count += 1
        except Exception as e:
            print(f"Lỗi khi lưu ngày {data['ngay']}: {str(e)}")
    return success_count


def nhap_ket_qua_textarea(request):
    if request.method == "POST":
        form = ImportKetQuaForm(request.POST)
        if form.is_valid():
            content = form.cleaned_data["data_input"]
            try:
                parsed_data = parse_input_data(content)
                if not parsed_data:
                    messages.error(
                        request, "Không tìm thấy dữ liệu hợp lệ trong nội dung nhập!"
                    )
                else:
                    success_count = import_to_db(parsed_data)
                    messages.success(
                        request,
                        f"Đã nhập thành công {success_count}/{len(parsed_data)} bản ghi!",
                    )
                    return redirect("nhap_ket_qua_textarea")
            except Exception as e:
                messages.error(request, f"Lỗi khi xử lý dữ liệu: {str(e)}")
    else:
        form = ImportKetQuaForm()

    return render(request, "results/nhap_ket_qua_textarea.html", {"form": form})


def get_top_numbers(number_counts):
    if isinstance(number_counts, list):
        temp_counts = defaultdict(int)
        for num in number_counts:
            temp_counts[num] += 1
        number_counts = temp_counts
    sorted_numbers = sorted(number_counts.items(), key=lambda x: (-x[1], x[0]))
    return sorted_numbers[:5]


def find_common_predictions(predictions):
    # Lấy tất cả số dự đoán từ các khoảng thời gian
    pred_7 = {num for num, _ in predictions["7_ngay"]["top_numbers"]}
    pred_10 = {num for num, _ in predictions["10_ngay"]["top_numbers"]}
    pred_20 = {num for num, _ in predictions["20_ngay"]["top_numbers"]}

    # Tìm các số trùng nhau giữa các nhóm
    common_7_10 = pred_7 & pred_10
    common_7_20 = pred_7 & pred_20
    common_10_20 = pred_10 & pred_20
    common_all = pred_7 & pred_10 & pred_20

    return {
        "7_vs_10": sorted(common_7_10),
        "7_vs_20": sorted(common_7_20),
        "10_vs_20": sorted(common_10_20),
        "all_three": sorted(common_all),
    }


def extract_loto_numbers(results):
    loto_stats = {str(i): [] for i in range(10)}  # Khởi tạo dict đầu 0-9

    # Hàm chuyển đổi số thành chuỗi và đảm bảo đủ 2 chữ số
    def normalize_number(num):
        num_str = str(num)
        return num_str.zfill(2)[-2:]  # Đảm bảo luôn có 2 chữ số, thêm số 0 nếu cần

    # Duyệt qua tất cả các giải
    for prize_data in results:
        numbers = []

        # Xử lý các định dạng dữ liệu khác nhau
        if isinstance(prize_data, dict):
            numbers = prize_data.get("numbers", [])
        elif isinstance(prize_data, (list, tuple)):
            numbers = prize_data
        else:
            numbers = [prize_data]

        # Chuyển tất cả về dạng chuỗi và xử lý
        for num in numbers:
            num_str = normalize_number(num)
            first_digit = num_str[0]  # Lấy đầu số

            # Thêm vào dict nếu chưa tồn tại
            if num_str not in loto_stats[first_digit]:
                loto_stats[first_digit].append(num_str)

    # Sắp xếp các số trong mỗi đầu
    for digit in loto_stats:
        loto_stats[digit].sort(key=lambda x: int(x))  # Sắp xếp số

    return loto_stats


def analyze_predictions(predictions):
    # Tạo dict để lưu trữ các số dự đoán theo đầu số
    prediction_stats = {str(i): [] for i in range(10)}

    # Lấy các số dự đoán từ các kỳ khác nhau
    pred_7_days = predictions.get("7_ngay", {}).get("top_numbers", [])
    pred_10_days = predictions.get("10_ngay", {}).get("top_numbers", [])
    pred_20_days = predictions.get("20_ngay", {}).get("top_numbers", [])

    # Hàm chuẩn hóa số (đảm bảo 2 chữ số)
    def normalize_num(num):
        return f"{int(num):02d}" if isinstance(num, (int, float)) else num.zfill(2)

    # Tổng hợp tất cả các số dự đoán
    all_predictions = []
    for period in [pred_7_days, pred_10_days, pred_20_days]:
        for num, _ in period:  # (num, confidence_score)
            normalized = normalize_num(num)
            if normalized not in all_predictions:
                all_predictions.append(normalized)

    # Phân loại theo đầu số
    for num in all_predictions:
        if len(num) >= 2:
            first_digit = num[0]
            if first_digit in prediction_stats:
                prediction_stats[first_digit].append(num)

    # Tìm các số trùng nhau giữa các kỳ
    common_numbers = []
    if pred_7_days and pred_10_days and pred_20_days:
        nums_7 = {normalize_num(num) for num, _ in pred_7_days}
        nums_10 = {normalize_num(num) for num, _ in pred_10_days}
        nums_20 = {normalize_num(num) for num, _ in pred_20_days}
        common_numbers = list(nums_7 & nums_10 & nums_20)  # Giao của 3 tập hợp

    # Sắp xếp các số trong mỗi đầu số
    for digit in prediction_stats:
        prediction_stats[digit].sort(key=lambda x: int(x))

    return {
        "prediction_stats": prediction_stats,
        "common_numbers": common_numbers,
        "total_predictions": len(all_predictions),
    }


def get_hot_digits(predictions, top_n=3):
    """
    Xác định các đầu số xuất hiện nhiều nhất trong các dự đoán
    Args:
        predictions: Dict chứa dữ liệu dự đoán từ các kỳ
        top_n: Số lượng đầu số nổi bật cần lấy
    Returns:
        List các đầu số nổi bật nhất (ví dụ: ['1', '5', '3'])
    """
    digit_stats = {str(i): 0 for i in range(10)}  # Thống kê tần suất đầu số

    # Duyệt qua tất cả các dự đoán từ các kỳ
    for period in ["7_ngay", "10_ngay", "20_ngay"]:
        if period in predictions and "top_numbers" in predictions[period]:
            for num, _ in predictions[period]["top_numbers"]:
                if len(str(num)) >= 1:  # Đảm bảo có ít nhất 1 chữ số
                    first_digit = str(num)[0]
                    if first_digit in digit_stats:
                        digit_stats[first_digit] += 1

    # Sắp xếp và lấy top đầu số
    sorted_digits = sorted(digit_stats.items(), key=lambda x: x[1], reverse=True)
    hot_digits = [digit for digit, count in sorted_digits[:top_n] if count > 0]

    return hot_digits


import logging
from datetime import datetime, timedelta

from django.contrib import messages
from django.core.paginator import Paginator
from django.http import JsonResponse
from django.shortcuts import render
from django.utils import timezone

logger = logging.getLogger(__name__)


def extract_two_digit_numbers(result):
    """Extract all two-digit numbers from a KetQuaXoSo result."""
    if not result:
        return []

    numbers = []
    if result.giai_7:
        numbers.extend(
            [
                num.strip()
                for num in result.giai_7.split(",")
                if num.strip().isdigit() and len(num.strip()) == 2
            ]
        )
    prize_fields = [
        result.giai_db,
        result.giai_1,
        result.giai_2,
        result.giai_3,
        result.giai_4,
        result.giai_5,
        result.giai_6,
    ]
    for giai in prize_fields:
        if giai:
            for num in giai.replace(",", " ").split():
                if num.isdigit() and len(num) >= 2:
                    numbers.append(num[-2:].zfill(2))
    return sorted(list(set(numbers)))


def history_view(request):
    """Display lottery results history with two-digit numbers."""
    # Parse date parameters
    from_date = request.GET.get("from_date")
    to_date = request.GET.get("to_date")

    logger.debug(f"Filter params - from_date: {from_date}, to_date: {to_date}")

    # Initialize queryset
    queryset = KetQuaXoSo.objects.all().order_by("-ngay")

    # Apply default 30-day filter if no dates provided
    if not from_date and not to_date:
        from_date = (timezone.now().date() - timedelta(days=30)).strftime("%Y-%m-%d")
        queryset = queryset.filter(ngay__gte=from_date)
    else:
        # Apply custom date filters
        try:
            if from_date:
                from_date = datetime.strptime(from_date, "%Y-%m-%d").date()
                queryset = queryset.filter(ngay__gte=from_date)
            if to_date:
                to_date = datetime.strptime(to_date, "%Y-%m-%d").date()
                queryset = queryset.filter(ngay__lte=to_date)
        except ValueError as e:
            logger.error(f"Date format error: {e}")
            messages.error(request, "Invalid date format. Use YYYY-MM-DD.")
            queryset = KetQuaXoSo.objects.none()

    logger.debug(f"Total results found: {queryset.count()}")

    # Prepare results
    prepared_results = []
    for result in queryset:
        try:
            if not any(
                [
                    result.giai_db,
                    result.giai_1,
                    result.giai_2,
                    result.giai_3,
                    result.giai_4,
                    result.giai_5,
                    result.giai_6,
                    result.giai_7,
                ]
            ):
                logger.warning(f"Record for date {result.ngay} lacks sufficient data")
                continue
            result.two_digit_numbers = extract_two_digit_numbers(result)
            result.giai_2_split = result.giai_2.split() if result.giai_2 else []
            result.giai_3_split = result.giai_3.split() if result.giai_3 else []
            result.giai_4_split = result.giai_4.split() if result.giai_4 else []
            result.giai_5_split = result.giai_5.split() if result.giai_5 else []
            result.giai_6_split = result.giai_6.split() if result.giai_6 else []
            result.giai_7_split = result.giai_7.split() if result.giai_7 else []
            prepared_results.append(result)
        except Exception as e:
            logger.error(f"Error processing result for date {result.ngay}: {e}")
            continue

    # Group results into pairs
    result_pairs = []
    for i in range(0, len(prepared_results), 2):
        pair = (
            prepared_results[i],
            prepared_results[i + 1] if i + 1 < len(prepared_results) else None,
        )
        result_pairs.append(pair)

    # Paginate results
    paginator = Paginator(result_pairs, 5)  # 5 pairs per page
    page_number = request.GET.get("page", 1)
    try:
        page_obj = paginator.page(page_number)
    except Exception as e:
        logger.error(f"Pagination error: {e}")
        page_obj = paginator.page(1)

    context = {
        "page_obj": page_obj,
        "result_pairs": result_pairs,
        "from_date": (
            from_date
            if isinstance(from_date, str)
            else from_date.strftime("%Y-%m-%d") if from_date else ""
        ),
        "to_date": (
            to_date
            if isinstance(to_date, str)
            else to_date.strftime("%Y-%m-%d") if to_date else ""
        ),
        "total_results": queryset.count(),
    }

    return render(request, "results/history.html", context)


from results.component.soi_cau_hai_nhay import soi_cau_hai_nhay


def soi_cau_hai_nhay_from_component(request):
    return soi_cau_hai_nhay(request)


def update_cycle_accuracy():
    """Cập nhật độ chính xác các chu kỳ hàng ngày"""
    today = timezone.now().date()
    history = KetQuaXoSo.objects.filter(ngay__lt=today).order_by("-ngay")[:30]

    if len(history) < 30:
        return  # Không đủ dữ liệu

    # Lấy kết quả hôm qua để kiểm tra
    yesterday = today - timezone.timedelta(days=1)
    yesterday_result = KetQuaXoSo.objects.filter(ngay=yesterday).first()

    if not yesterday_result:
        return

    actual_numbers = set(yesterday_result.get_all_2digit_numbers())

    for cycle in ["1_ngay", "3_ngay", "7_ngay", "14_ngay", "30_ngay"]:
        # Lấy dự đoán từ model tương ứng
        predictor = AdvancedCyclePredictor()
        predictions = predictor.predict(history, top_n=20)
        predicted_numbers = {num for num, _ in predictions}

        # Tính độ chính xác
        correct = len(actual_numbers & predicted_numbers)
        total = len(predicted_numbers)

        # Cập nhật vào database
        cycle_acc, _ = CycleAccuracy.objects.get_or_create(cycle_type=cycle)
        cycle_acc.total_predictions += total
        cycle_acc.correct_predictions += correct
        cycle_acc.update_accuracy()


# views.py
from itertools import combinations

from django.contrib import messages
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import MinMaxScaler

from .hybrid_predictor import HybridPredictor


def statistical_prediction(history):
    """Phân tích thống kê truyền thống"""

    # 1. Thống kê tần suất số xuất hiện
    number_freq = defaultdict(int)
    for result in history:
        for num in result.get_all_2digit_numbers():
            number_freq[num] += 1

    # 2. Phát hiện số gan (lâu chưa xuất hiện)
    last_appearance = {}
    for idx, result in enumerate(history):
        for num in result.get_all_2digit_numbers():
            last_appearance[num] = idx

    # 3. Tính điểm tổng hợp
    scored_numbers = []
    for num in number_freq:
        freq_score = number_freq[num] / len(history)
        recency_score = 1 - (len(history) - last_appearance.get(num, 0)) / len(history)
        total_score = freq_score * 0.7 + recency_score * 0.3
        scored_numbers.append((num, total_score))

    # Lấy top 15 số
    return [
        num
        for num, score in sorted(scored_numbers, key=lambda x: x[1], reverse=True)[:15]
    ]


def prepare_ml_data(history):
    """Chuẩn bị dữ liệu đầu vào cho ML model"""
    try:
        # Lấy dữ liệu giải đặc biệt làm đặc trưng
        data = [
            [res.giai_db] for res in history if hasattr(res, "giai_db") and res.giai_db
        ]

        if len(data) < 2:
            return np.zeros((1, 1))

        scaler = MinMaxScaler()
        return scaler.fit_transform(data)
    except Exception as e:
        logger.error(f"Lỗi chuẩn bị dữ liệu ML: {str(e)}")
        return np.zeros((1, 1))


def dan_de_dac_biet_report(request):
    # Xử lý tham số tháng
    selected_month = request.GET.get("month")
    if selected_month:
        try:
            selected_month = datetime.strptime(selected_month, "%Y-%m").date()
            start_date = selected_month.replace(day=1)
            end_date = (selected_month.replace(day=28) + timedelta(days=4)).replace(
                day=1
            ) - timedelta(days=1)
        except ValueError:
            selected_month = datetime.today().date().replace(day=1)
            start_date = selected_month
            end_date = (selected_month.replace(day=28) + timedelta(days=4)).replace(
                day=1
            ) - timedelta(days=1)
    else:
        selected_month = datetime.today().date().replace(day=1)
        start_date = selected_month
        end_date = (selected_month.replace(day=28) + timedelta(days=4)).replace(
            day=1
        ) - timedelta(days=1)

    # Lấy dữ liệu theo tháng
    records = DanDeDacBiet.objects.filter(
        analysis_date__gte=start_date, analysis_date__lte=end_date
    ).order_by("analysis_date")

    # Chuẩn bị dữ liệu cho template
    days_in_month = []
    current_date = start_date
    while current_date <= end_date:
        days_in_month.append(current_date)
        current_date += timedelta(days=1)

    monthly_data = {
        "days": [],
        "stats": {
            "total_days": len(days_in_month),
            "records_count": 0,
            "hit_days": 0,
            "hit_rate": 0,
            "total_hits": 0,
            "total_two_digits_hits": 0,
            "total_three_digits_hits": 0,
            "top_numbers": [],
            "top_two_digits": [],
            "top_three_digits": [],
        },
    }

    # Thống kê số trúng
    hit_numbers = defaultdict(int)
    hit_two_digits = defaultdict(int)
    hit_three_digits = defaultdict(int)

    for day in days_in_month:
        record = records.filter(analysis_date=day).first()
        day_data = {
            "date": day,
            "record": record,
            "hit_count": record.hit_count if record else 0,
            "two_digits_hit_count": record.two_digits_hit_count if record else 0,
            "three_digits_hit_count": record.three_digits_hit_count if record else 0,
        }
        monthly_data["days"].append(day_data)

        if record:
            monthly_data["stats"]["records_count"] += 1
            monthly_data["stats"]["total_hits"] += record.hit_count
            monthly_data["stats"][
                "total_two_digits_hits"
            ] += record.two_digits_hit_count
            monthly_data["stats"][
                "total_three_digits_hits"
            ] += record.three_digits_hit_count

            if record.hit_count > 0:
                monthly_data["stats"]["hit_days"] += 1
            if record.two_digits_hit_count > 0:
                monthly_data["stats"]["hit_days"] += 1
            if record.three_digits_hit_count > 0:
                monthly_data["stats"]["hit_days"] += 1

            for num in record.winning_numbers:
                hit_numbers[num] += 1
            for num in record.two_digits_winning:
                hit_two_digits[num] += 1
            for num in record.three_digits_winning:
                hit_three_digits[num] += 1

    # Tính tỷ lệ trúng
    if monthly_data["stats"]["records_count"] > 0:
        monthly_data["stats"]["hit_rate"] = round(
            (monthly_data["stats"]["hit_days"] / monthly_data["stats"]["records_count"])
            * 100,
            2,
        )

    # Lấy top số trúng
    monthly_data["stats"]["top_numbers"] = sorted(
        hit_numbers.items(), key=lambda x: x[1], reverse=True
    )[:5]
    monthly_data["stats"]["top_two_digits"] = sorted(
        hit_two_digits.items(), key=lambda x: x[1], reverse=True
    )[:5]
    monthly_data["stats"]["top_three_digits"] = sorted(
        hit_three_digits.items(), key=lambda x: x[1], reverse=True
    )[:5]

    # Xử lý ngày được chọn
    selected_date_str = request.GET.get("date")
    selected_date = None
    selected_record = None

    if selected_date_str:
        try:
            selected_date = datetime.strptime(selected_date_str, "%Y-%m-%d").date()
            selected_record = records.filter(analysis_date=selected_date).first()
        except ValueError:
            pass

    context = {
        "selected_month": selected_month,
        "monthly_data": monthly_data,
        "monthly_stats": monthly_data["stats"],
        "selected_date": selected_date,
        "selected_record": selected_record,
    }

    return render(request, "results/dan_de_dac_biet_report.html", context)


from hashlib import md5


def custom_cache_key(func, *args, **kwargs):
    """Tạo cache key đơn giản không chứa ký tự đặc biệt"""
    key = f"{func.__module__}:{func.__name__}:{args}:{kwargs}"
    return md5(key.encode("utf-8")).hexdigest()


def get_historical_performance(historical_data):
    """Lấy hiệu suất lịch sử 30 ngày gần nhất"""
    predictor = EnhancedCyclePredictor()
    performances = []
    for i in range(len(historical_data) - 1):
        try:
            pred = predictor.predict_for_date(
                historical_data[i : i + 30], historical_data[i + 1].ngay
            )
            actual = historical_data[i + 1].get_all_2digit_numbers()
            perf = calculate_performance_metrics(pred, actual)
            performances.append(
                {"date": historical_data[i + 1].ngay, "accuracy": perf["accuracy"]}
            )
        except:
            continue
    return performances[-7:]  # Trả về 7 ngày gần nhất


def _get_performance_history(historical_data, current_date=None):
    """
    Lấy hiệu suất 30 ngày gần nhất
    Args:
        historical_data: Danh sách kết quả xổ số, sắp xếp từ mới đến cũ
        current_date: Ngày hiện tại để giới hạn dữ liệu
    """
    predictor = EnhancedCyclePredictor()
    performances = []

    # Chuyển danh sách thành list và sắp xếp lại từ cũ đến mới
    historical_list = list(historical_data)
    historical_list.reverse()

    # Lấy 30 ngày gần nhất để đánh giá
    evaluation_days = 30

    for i in range(len(historical_list) - evaluation_days):
        try:
            # Ngày cần dự đoán
            pred_date = historical_list[i + evaluation_days - 1].ngay

            # Kiểm tra nếu vượt quá ngày hiện tại
            if current_date and pred_date > current_date:
                continue

            # Lấy 30 ngày trước đó để dự đoán
            training_data = historical_list[i : i + evaluation_days]

            # Lấy kết quả thực tế của ngày tiếp theo
            if i + evaluation_days >= len(historical_list):
                continue
            actual_result = historical_list[i + evaluation_days]

            # Thực hiện dự đoán
            predictions = predictor.predict_for_date(training_data, pred_date)

            if not predictions:
                continue

            actual_numbers = actual_result.get_all_2digit_numbers()

            # Tính toán metrics
            matched_numbers = set(predictions.keys()) & set(actual_numbers)
            total_predictions = len(predictions)
            total_actual = len(actual_numbers)

            # Tính precision và recall
            precision = (
                len(matched_numbers) / total_predictions if total_predictions > 0 else 0
            )
            recall = len(matched_numbers) / total_actual if total_actual > 0 else 0

            # Tính F1-score
            f1 = (
                2 * (precision * recall) / (precision + recall)
                if (precision + recall) > 0
                else 0
            )

            # Normalize score to percentage
            accuracy_score = f1 * 100

            # Thêm kết quả vào danh sách
            performances.append(
                {
                    "date": pred_date,
                    "accuracy": min(accuracy_score, 100),  # Giới hạn maximum 100%
                    "matched": len(matched_numbers),
                    "total_pred": total_predictions,
                    "total_actual": total_actual,
                }
            )

            logger.info(
                f"""
            Performance for {pred_date}:
            - Matched numbers: {matched_numbers}
            - Precision: {precision:.2%}
            - Recall: {recall:.2%}
            - F1: {f1:.2%}
            - Final accuracy: {accuracy_score:.2f}%
            """
            )

        except Exception as e:
            logger.error(
                f"Error calculating performance for {pred_date}: {str(e)}",
                exc_info=True,
            )
            continue

    return performances


def calculate_performance_metrics(predictions, actual_numbers):
    matched_numbers = set(predictions.keys()) & set(actual_numbers)
    total_predictions = len(predictions)
    correct_predictions = len(matched_numbers)
    total_actual = len(actual_numbers)

    precision = (
        correct_predictions / total_predictions * 100 if total_predictions > 0 else 0
    )
    recall = correct_predictions / total_actual * 100 if total_actual > 0 else 0
    f1 = (
        2 * (precision * recall) / (precision + recall)
        if (precision + recall) > 0
        else 0
    )
    accuracy = correct_predictions / total_actual * 100 if total_actual > 0 else 0

    return {
        "precision": round(precision, 2),
        "recall": round(recall, 2),
        "f1": round(f1, 2),
        "accuracy": round(accuracy, 2),
        "total": total_predictions,
        "correct": correct_predictions,
    }


def analyze_pairs(predictor, best_pairs, actual_numbers, selected_date):
    analysis = {}
    if best_pairs and actual_numbers:
        analysis = {
            "hit_rate": predictor.calculate_pair_hit_rate(best_pairs, actual_numbers),
            "last_hit": predictor.get_last_hit_date(best_pairs, selected_date),
        }
    return analysis


def save_accuracy_metrics(date, metrics, predictor):
    try:
        with transaction.atomic():
            CycleAccuracy.objects.update_or_create(
                date=date,
                defaults={
                    "precision": metrics["precision"],
                    "recall": metrics["recall"],
                    "f1_score": metrics["f1"],
                    "total_predictions": metrics["total"],
                    "correct_predictions": metrics["correct"],
                    "features_used": predictor.get_used_features(),
                },
            )
    except Exception as e:
        logger.error(f"Lỗi khi lưu metrics: {str(e)}")


def update_performance_history(combined_pred, actual_numbers):
    """
    Cập nhật dữ liệu hiệu suất dựa trên kết quả kết hợp dự đoán và số thực.

    Args:
        combined_pred (dict): Dict chứa kết quả dự đoán kết hợp, dạng { số: điểm }.
        actual_numbers (iterable): Danh sách hoặc tập các số thực tế.

    Returns:
        dict: Ví dụ dict chứa các thông số hiệu suất, như số trùng, tổng số và phần trăm chính xác.
    """
    if not actual_numbers:
        return {"matched": 0, "total": 0, "accuracy": 0}

    # Đếm số dự đoán trùng với số thực tế
    matched = sum(1 for num in combined_pred if num in actual_numbers)
    total = len(actual_numbers)
    accuracy = (matched / total * 100) if total > 0 else 0

    return {"matched": matched, "total": total, "accuracy": round(accuracy, 2)}


from django.db.models.functions import Cast


def _get_history_stats(last_30_days):
    """Thống kê hiệu suất 30 ngày gần nhất"""
    stats = CycleAccuracy.objects.filter(
        date__gte=date.today() - timedelta(days=30)
    ).aggregate(
        avg_precision=Avg(Cast("precision", output_field=FloatField())),
        avg_recall=Avg("recall"),
        avg_f1=Avg("f1_score"),
    )
    return {
        "precision": stats["avg_precision"] or 0,
        "recall": stats["avg_recall"] or 0,
        "f1": stats["avg_f1"] or 0,
    }


def _generate_trend_chart(history_data, selected_date=None):
    """
    Tạo dữ liệu biểu đồ xu hướng
    Args:
        history_data: QuerySet chứa dữ liệu lịch sử
        selected_date: Ngày được chọn (optional)
    Returns:
        Dict chứa dữ liệu biểu đồ
    """
    if not history_data:
        return {"labels": [], "data": {}}

    # Sắp xếp dữ liệu theo ngày tăng dần
    sorted_data = sorted(history_data, key=lambda x: x.ngay)

    # Chuẩn bị dữ liệu
    labels = [
        date.ngay.strftime("%d/%m") for date in sorted_data[-30:]
    ]  # 30 ngày gần nhất
    frequency = []
    accuracy = []

    # Tính toán tần suất và độ chính xác
    for i in range(1, len(sorted_data)):
        prev = sorted_data[i - 1].get_all_2digit_numbers()
        current = sorted_data[i].get_all_2digit_numbers()

        # Tính tần suất xuất hiện
        common = set(prev) & set(current)
        freq = len(common) / len(prev) * 100 if prev else 0
        frequency.append(round(freq, 2))

        # Tính độ chính xác (nếu có dữ liệu đủ)
        if i > 1:
            predicted = set(sorted_data[i - 2].get_all_2digit_numbers())
            actual = set(current)
            correct = len(predicted & actual)
            acc = correct / len(predicted) * 100 if predicted else 0
            accuracy.append(round(acc, 2))

    return {
        "labels": labels,
        "data": {
            "frequency": frequency[-30:],  # Lấy 30 điểm dữ liệu gần nhất
            "accuracy": accuracy[-30:] if accuracy else [0] * min(30, len(labels)),
        },
    }


def _calculate_accuracy_trend(history):
    """Tính toán xu hướng độ chính xác từ lịch sử dự đoán

    Args:
        history: QuerySet hoặc list các bản ghi CycleAccuracy

    Returns:
        List các giá trị độ chính xác theo thứ tự ngược (mới nhất đầu tiên)
    """
    try:
        if not history:
            return []

        # Xử lý cả QuerySet và list
        history_list = list(history) if hasattr(history, "query") else history

        # Kiểm tra và tính toán giá trị accuracy
        trend_data = []
        for record in history_list:
            try:
                # Đảm bảo accuracy là số
                accuracy = float(getattr(record, "accuracy", 0))
                trend_data.append(round(accuracy, 2))
            except (TypeError, ValueError):
                trend_data.append(0.0)

        return trend_data[::-1]  # Đảo ngược để mới nhất lên đầu

    except Exception as e:
        logger.error(f"Lỗi tính xu hướng accuracy: {str(e)}")
        return []


def _generate_trend_chart(history_data, target_date=None):
    """
    Tạo dữ liệu biểu đồ xu hướng
    Args:
        history_data: QuerySet chứa dữ liệu lịch sử
        target_date: Ngày mục tiêu (optional)
    Returns:
        Dict chứa dữ liệu biểu đồ
    """
    if not history_data:
        return {"labels": [], "data": {}}

    # Sắp xếp dữ liệu theo ngày tăng dần
    sorted_data = sorted(history_data, key=lambda x: x.ngay)

    # Chuẩn bị dữ liệu
    labels = []
    frequency_data = []
    accuracy_data = []

    window_size = 7  # Cửa sổ 7 ngày
    for i in range(window_size, len(sorted_data)):
        window = sorted_data[i - window_size : i]
        current = sorted_data[i]

        # Lấy tất cả số trong cửa sổ
        window_numbers = set()
        for record in window:
            window_numbers.update(record.get_all_2digit_numbers())

        # Lấy số ngày hiện tại
        current_numbers = set(current.get_all_2digit_numbers())

        # Tính tần suất và độ chính xác
        date_label = current.ngay.strftime("%d/%m")
        labels.append(date_label)

        # Tần suất: % số xuất hiện trong cửa sổ trước
        freq = (
            len(window_numbers & current_numbers) / len(current_numbers) * 100
            if current_numbers
            else 0
        )
        frequency_data.append(round(freq, 2))

        # Độ chính xác tích lũy (ví dụ)
        accuracy = min(100, 70 + i)  # Thay bằng logic thực tế của bạn
        accuracy_data.append(round(accuracy, 2))

    return {
        "labels": labels[-30:],  # Giới hạn 30 điểm dữ liệu
        "data": {"frequency": frequency_data[-30:], "accuracy": accuracy_data[-30:]},
    }


def _calculate_frequency_trend(history):
    """Tính toán xu hướng tần suất xuất hiện các số từ lịch sử

    Args:
        history: QuerySet hoặc list các bản ghi lịch sử xổ số

    Returns:
        List các giá trị tần suất trung bình theo thứ tự ngược (mới nhất đầu tiên)
    """
    try:
        if not history:
            return []

        # Chuyển đổi history sang list nếu là QuerySet
        history_list = list(history) if hasattr(history, "query") else history

        # Dictionary để lưu tần suất xuất hiện của các số
        frequency_dict = {}
        total_days = len(history_list)

        # Tính tần suất xuất hiện của từng số
        for record in history_list:
            try:
                # Giả sử mỗi record có thuộc tính 'numbers' là list các số
                numbers = getattr(record, "numbers", [])
                for num in numbers:
                    if num in frequency_dict:
                        frequency_dict[num] += 1
                    else:
                        frequency_dict[num] = 1
            except Exception as e:
                logger.warning(f"Lỗi khi xử lý bản ghi: {str(e)}")
                continue

        # Tính tần suất trung bình (số lần xuất hiện / tổng số ngày)
        if frequency_dict and total_days > 0:
            avg_frequency = sum(frequency_dict.values()) / (
                len(frequency_dict) * total_days
            )
            return [
                round(avg_frequency, 4)
            ] * total_days  # Giả sử cùng giá trị cho tất cả các ngày
        else:
            return [0.0] * total_days

    except Exception as e:
        logger.error(f"Lỗi nghiêm trọng khi tính tần suất: {str(e)}")
        return []


def handle_error(request, error, context=None):
    """
    Xử lý lỗi và ghi log chi tiết
    Args:
        request: HttpRequest object
        error: Exception object
        context: Dict context để trả về template
    """
    error_msg = f"Lỗi trong enhanced_predict_view: {str(error)}"
    logger.error(error_msg, exc_info=True)

    # Thêm thông báo lỗi cho người dùng
    messages.error(
        request, "Đã xảy ra lỗi trong quá trình xử lý. Vui lòng thử lại sau."
    )

    # Thiết lập context mặc định nếu chưa có
    if context is None:
        context = {"performance": {}, "predictions": [], "error": error_msg}
    else:
        context["error"] = error_msg

    return context


def combine_predictions(predictions_df):
    """Kết hợp kết quả từ nhiều phương pháp"""

    scores = defaultdict(float)
    for _, row in predictions_df.iterrows():
        for num in row["numbers"]:
            scores[num] += row["confidence"]

    # Chuẩn hóa điểm số
    max_score = max(scores.values()) if scores else 1
    return {
        num: round(score / max_score * 100, 2)
        for num, score in sorted(scores.items(), key=lambda x: x[1], reverse=True)[:20]
    }


from results.services.PredictionCacheService import PredictionCacheService

from .models import AccuracyTrend, DailyPredictionAnalysis


class CombinedAnalysisView(TemplateView):
    template_name = "results/combined_analysis.html"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.prediction_service = PredictionService()
        self.ml_service = MLModelService()
        self.shap_service = SHAPAnalysisService(self.ml_service)
        self.cache_service = PredictionCacheService()

    def get_context_data(self, **kwargs):
        start_time = time.time()
        context = super().get_context_data(**kwargs)

        try:
            # Lấy ngày được chọn
            selected_date = self._get_selected_date()
            target_date = selected_date + timedelta(days=1)

            # Kiểm tra xem có nên hiển thị dự đoán không
            if not self.cache_service.should_show_prediction_results(target_date):
                context.update(
                    {
                        "hide_predictions": True,
                        "message": f"Kết quả thực tế cho ngày {target_date} đã có. Dự đoán sẽ được ẩn.",
                        "actual_result": KetQuaXoSo.objects.filter(
                            ngay=target_date
                        ).first(),
                    }
                )
                return context

            # Thử lấy từ cache trước
            cached_data = self.cache_service.get_cached_prediction(
                selected_date, "combined"
            )
            if cached_data:
                context.update(cached_data["data"])
                context["from_cache"] = True
                return context

            # Khởi tạo tracking
            context["processing_stages"] = self._init_processing_stages()

            # 1. Huấn luyện/load models
            self._update_stage(
                context,
                "model_training",
                "in_progress",
                "Training/Loading ML models...",
            )

            if not self.ml_service.train_models():
                logger.warning("Failed to train/load ML models")

            self._update_stage(context, "model_training", "complete", "Models ready")

            # 2. Lấy dữ liệu lịch sử
            self._update_stage(
                context,
                "data_retrieval",
                "in_progress",
                "Retrieving historical data...",
            )

            historical_data = self._get_historical_data_before_date(selected_date)
            if not historical_data:
                raise ValueError("Insufficient historical data")

            self._update_stage(
                context, "data_retrieval", "complete", "Historical data loaded"
            )

            # Now check if models are available
            logger.info(
                f"ML Service models available after reload: {hasattr(self.ml_service, 'models') and bool(self.ml_service.models)}"
            )
            if hasattr(self.ml_service, "models") and self.ml_service.models:
                logger.info(
                    f"Models keys after reload: {list(self.ml_service.models.keys())}"
                )

            # 3. Phân tích ML và SHAP
            self._update_stage(
                context, "ml_analysis", "in_progress", "Performing ML analysis..."
            )

            ml_predictions = self.ml_service.predict_numbers(
                target_date, historical_data
            )

            # SHAP analysis
            if ml_predictions and self.ml_service.models:
                # Chuẩn bị sample data cho SHAP
                X_sample, _ = self.ml_service.prepare_features_for_prediction(
                    historical_data[-30:], target_date
                )

                if X_sample is not None:
                    # Lấy SHAP cho model tốt nhất
                    best_model = "random_forest"  # Hoặc chọn dựa trên performance
                    shap_analysis = self.shap_service.calculate_shap_values(
                        best_model, X_sample[-100:]  # Sample 100 records
                    )
                    context["shap_analysis"] = shap_analysis

            self._update_stage(
                context, "ml_analysis", "complete", "ML analysis complete"
            )

            # 4. Dự đoán từ BachThuLoPredictor
            self._update_stage(
                context,
                "traditional_prediction",
                "in_progress",
                "Traditional predictions...",
            )

            predictor = BachThuLoPredictor(
                target_date=target_date, history_days=90, selected_date=selected_date
            )

            traditional_predictions = predictor.predict()
            self._update_stage(
                context,
                "traditional_prediction",
                "complete",
                "Traditional predictions complete",
            )

            # 5. Kết hợp tất cả dự đoán
            self._update_stage(
                context, "combination", "in_progress", "Combining predictions..."
            )

            combined_analysis = self._combine_all_predictions(
                ml_predictions, traditional_predictions, historical_data
            )

            context.update(combined_analysis)
            self._update_stage(context, "combination", "complete", "Analysis complete")

            # 6. Lưu vào database và cache
            processing_time = time.time() - start_time
            self._save_analysis_to_database(
                selected_date, target_date, combined_analysis, processing_time
            )
            self.cache_service.cache_prediction(selected_date, "combined", context)

            context.update(
                {
                    "selected_date": selected_date,
                    "target_date": target_date,
                    "processing_time": processing_time,
                    "from_cache": False,
                }
            )

        except Exception as e:
            logger.error(f"Error in CombinedAnalysisView: {e}", exc_info=True)
            context.update(self._get_error_context(str(e)))

        return context

    def _get_selected_date(self):
        """Get selected date from request or return today's date"""
        try:
            date_str = self.request.GET.get("selected_date")
            if date_str:
                return datetime.strptime(date_str, "%Y-%m-%d").date()
            return datetime.now().date()
        except Exception as e:
            logging.error(f"Error parsing date: {str(e)}")
            return datetime.now().date()

    def _get_historical_data_before_date(self, target_date):
        """
        Get historical data up to but not including target date

        Args:
            target_date: Date to get data before

        Returns:
            QuerySet of KetQuaXoSo objects
        """
        try:
            history_days = int(self.request.GET.get("days", 90))
            end_date = target_date - timedelta(days=1)
            start_date = end_date - timedelta(days=history_days)

            return KetQuaXoSo.objects.filter(
                ngay__range=(start_date, end_date)
            ).order_by("-ngay")

        except Exception as e:
            logger.error(f"Error getting historical data: {e}")
            return []

    def _init_processing_stages(self):
        """Khởi tạo các giai đoạn xử lý"""
        return {
            "model_training": {
                "status": "pending",
                "message": "Preparing ML models...",
            },
            "data_retrieval": {
                "status": "pending",
                "message": "Loading historical data...",
            },
            "ml_analysis": {"status": "pending", "message": "ML analysis pending..."},
            "traditional_prediction": {
                "status": "pending",
                "message": "Traditional predictions pending...",
            },
            "combination": {
                "status": "pending",
                "message": "Combining results pending...",
            },
        }

    def _update_stage(self, context, stage, status, message):
        """Cập nhật trạng thái giai đoạn"""
        context["processing_stages"][stage] = {"status": status, "message": message}

    def _combine_all_predictions(
        self, ml_predictions, traditional_predictions, historical_data
    ):
        """
        Kết hợp tất cả các dự đoán với trọng số thông minh - ENHANCED
        """
        try:
            combined_numbers = {}

            # 1. Từ ML predictions - Enhanced handling
            ml_weight = 0.4
            if ml_predictions:
                for prediction_item in ml_predictions:
                    # Handle different prediction formats
                    if isinstance(prediction_item, dict):
                        number = prediction_item.get("number")
                        confidence = prediction_item.get("confidence", 0.5)
                    elif (
                        isinstance(prediction_item, (tuple, list))
                        and len(prediction_item) >= 2
                    ):
                        number, confidence = prediction_item[0], prediction_item[1]
                    else:
                        continue

                    if number and isinstance(number, str) and len(number) == 2:
                        combined_numbers[number] = combined_numbers.get(number, 0) + (
                            confidence * ml_weight
                        )

            # 2. Từ traditional predictions
            traditional_weight = 0.6
            if traditional_predictions and "predictions" in traditional_predictions:
                for method, numbers in traditional_predictions["predictions"].items():
                    method_weight = traditional_weight / len(
                        traditional_predictions["predictions"]
                    )

                    for num_info in numbers:
                        if isinstance(num_info, dict):
                            number = num_info.get("number", num_info.get("so"))
                            confidence = num_info.get(
                                "confidence", num_info.get("diem", 0.5)
                            )
                        elif isinstance(num_info, str):
                            number = num_info
                            confidence = 0.5
                        else:
                            continue

                        if number and len(str(number)) == 2:
                            number = f"{int(number):02d}"
                            combined_numbers[number] = combined_numbers.get(
                                number, 0
                            ) + (confidence * method_weight)

            # 3. Áp dụng bonus cho số nóng/lạnh
            hot_cold_analysis = self._analyze_hot_cold_numbers(historical_data)

            for num_str in combined_numbers:
                # Hot number bonus
                if num_str in [
                    h["number"] for h in hot_cold_analysis.get("hot_numbers", [])
                ]:
                    combined_numbers[num_str] *= 1.2
                # Cold number penalty
                elif num_str in [
                    c["number"] for c in hot_cold_analysis.get("cold_numbers", [])
                ]:
                    combined_numbers[num_str] *= 0.8

            # 4. Sắp xếp và format kết quả
            sorted_numbers = sorted(
                combined_numbers.items(), key=lambda x: x[1], reverse=True
            )

            # 5. Tạo enhanced predictions với metadata
            enhanced_predictions = []
            for i, (num_str, score) in enumerate(sorted_numbers[:20]):
                sources = self._get_prediction_sources(
                    num_str, ml_predictions, traditional_predictions
                )

                enhanced_predictions.append(
                    {
                        "number": num_str,
                        "confidence": min(1.0, score),
                        "rank": i + 1,
                        "sources": sources,
                        "is_hot": num_str
                        in [
                            h["number"]
                            for h in hot_cold_analysis.get("hot_numbers", [])
                        ],
                        "is_cold": num_str
                        in [
                            c["number"]
                            for c in hot_cold_analysis.get("cold_numbers", [])
                        ],
                        "raw_score": score,
                    }
                )

            return {
                "ml_predictions": ml_predictions,
                "traditional_predictions": traditional_predictions,
                "combined_predictions": enhanced_predictions,
                "hot_cold_analysis": hot_cold_analysis,
                "prediction_summary": {
                    "total_numbers": len(enhanced_predictions),
                    "ml_contribution": ml_weight,
                    "traditional_contribution": traditional_weight,
                    "top_confidence": (
                        enhanced_predictions[0]["confidence"]
                        if enhanced_predictions
                        else 0
                    ),
                    "prediction_methods": len(
                        traditional_predictions.get("predictions", {})
                    )
                    + (1 if ml_predictions else 0),
                },
            }

        except Exception as e:
            logger.error(f"Error combining predictions: {e}")
            return self._get_default_combined_predictions()

    def _get_default_combined_predictions(self):
        """Default predictions when combination fails"""
        return {
            "ml_predictions": [],
            "traditional_predictions": {},
            "combined_predictions": [],
            "hot_cold_analysis": {
                "hot_numbers": [],
                "cold_numbers": [],
                "avg_frequency": 0,
            },
            "prediction_summary": {
                "total_numbers": 0,
                "ml_contribution": 0,
                "traditional_contribution": 0,
                "top_confidence": 0,
                "prediction_methods": 0,
            },
        }

    def _analyze_hot_cold_numbers(self, historical_data):
        """Phân tích số nóng/lạnh"""
        try:
            # Phân tích 30 ngày gần nhất
            recent_data = historical_data[:30]
            number_counts = {}

            for record in recent_data:
                for num in record.get_all_2digit_numbers():
                    number_counts[num] = number_counts.get(num, 0) + 1

            # Tính trung bình
            avg_frequency = (
                sum(number_counts.values()) / len(number_counts) if number_counts else 0
            )

            hot_numbers = []
            cold_numbers = []

            for num, count in number_counts.items():
                if count > avg_frequency * 1.5:  # Nóng: > 150% trung bình
                    hot_numbers.append(num)
                elif count < avg_frequency * 0.5:  # Lạnh: < 50% trung bình
                    cold_numbers.append(num)

            return {
                "hot_numbers": hot_numbers[:10],
                "cold_numbers": cold_numbers[:10],
                "avg_frequency": avg_frequency,
            }

        except Exception as e:
            logger.error(f"Error analyzing hot/cold numbers: {e}")
            return {"hot_numbers": [], "cold_numbers": [], "avg_frequency": 0}

    def _get_prediction_sources(self, number, ml_predictions, traditional_predictions):
        """Xác định nguồn dự đoán cho một số"""
        sources = []

        # Kiểm tra ML
        ml_numbers = [num for num, _ in ml_predictions]
        if number in ml_numbers:
            sources.append("ML")

        # Kiểm tra traditional
        if traditional_predictions and "predictions" in traditional_predictions:
            for method, numbers in traditional_predictions["predictions"].items():
                if isinstance(numbers, (list, tuple)) and number in [
                    str(n).zfill(2) for n in numbers
                ]:
                    sources.append(method)

        return sources

    def _save_analysis_to_database(
        self, analysis_date, target_date, analysis_data, processing_time
    ):
        """Lưu kết quả phân tích vào database"""
        try:
            # Chuẩn bị dữ liệu dự đoán
            predictions_data = {}

            if "ml_predictions" in analysis_data:
                predictions_data["ml"] = {
                    "numbers": [num for num, _ in analysis_data["ml_predictions"]],
                    "scores": {
                        num: score for num, score in analysis_data["ml_predictions"]
                    },
                }

            if (
                "traditional_predictions" in analysis_data
                and "predictions" in analysis_data["traditional_predictions"]
            ):
                for method, numbers in analysis_data["traditional_predictions"][
                    "predictions"
                ].items():
                    if isinstance(numbers, (list, tuple)):
                        predictions_data[method] = {
                            "numbers": [str(n).zfill(2) for n in numbers],
                            "count": len(numbers),
                        }

            # Lưu vào database
            analysis_record, created = DailyPredictionAnalysis.objects.update_or_create(
                analysis_date=analysis_date,
                defaults={
                    "target_date": target_date,
                    "predictions_data": predictions_data,
                    "processing_time": processing_time,
                },
            )

            logger.info(
                f"{'Created' if created else 'Updated'} analysis record for {analysis_date}"
            )

            return analysis_record

        except Exception as e:
            logger.error(f"Error saving analysis to database: {e}")
            return None

    def _get_error_context(self, error_message):
        """Tạo context khi có lỗi"""
        return {
            "error": True,
            "error_message": error_message,
            "predictions": [],
            "processing_stages": {
                "error": {"status": "failed", "message": f"Error: {error_message}"}
            },
        }

    # Thêm method để cập nhật accuracy khi có kết quả thực tế
    @classmethod
    def update_accuracy_when_result_available(cls, result_date):
        """
        Được gọi khi có kết quả xổ số mới
        Cập nhật accuracy cho các dự đoán đã lưu
        """
        try:
            # Tìm analysis record cho ngày này
            yesterday = result_date - timedelta(days=1)
            analysis = DailyPredictionAnalysis.objects.filter(
                analysis_date=yesterday, target_date=result_date
            ).first()

            if not analysis:
                logger.warning(
                    f"No analysis record found for {yesterday} -> {result_date}"
                )
                return

            # Lấy kết quả thực tế
            actual_result = KetQuaXoSo.objects.filter(ngay=result_date).first()
            if not actual_result:
                logger.warning(f"No actual result found for {result_date}")
                return

            # Cập nhật accuracy
            analysis.actual_numbers = actual_result.get_all_2digit_numbers()
            analysis.calculate_accuracy()

            # Cập nhật xu hướng
            AccuracyTrend.update_trend(result_date)

            # Xóa cache
            cache_service = PredictionCacheService()
            cache_service.invalidate_cache_for_date(yesterday)

            logger.info(f"Updated accuracy for analysis {yesterday} -> {result_date}")

        except Exception as e:
            logger.error(f"Error updating accuracy: {e}")


import logging
import re
import time
from collections import Counter
from datetime import datetime, timedelta

from django.http import JsonResponse
from django.shortcuts import render
from django.utils import timezone
from django.views import View

from results.analytics.predictors import BachThuLoPredictor
from results.models import DailyPredictionAnalysis, KetQuaXoSo
from results.services.EnhancedPredictionCacheService import (
    EnhancedPredictionCacheService,
)

logger = logging.getLogger(__name__)

from django.core.serializers.json import DjangoJSONEncoder


# Add custom JSON encoder
class NumpyJSONEncoder(DjangoJSONEncoder):
    """Custom JSON encoder to handle numpy data types"""

    def default(self, obj):
        if isinstance(obj, np.integer):
            return int(obj)
        elif isinstance(obj, np.floating):
            return float(obj)
        elif isinstance(obj, np.ndarray):
            return obj.tolist()
        elif isinstance(obj, (date, datetime)):
            return obj.isoformat()
        return super().default(obj)


class ImprovedCombinedAnalysisView(TemplateView):
    """
    Enhanced Combined Analysis View with complete functionality
    """

    template_name = "results/improved_combined_analysis.html"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.ml_service = MLModelService()
        self.shap_service = SHAPAnalysisService(self.ml_service)
        self.cache_service = PredictionCacheService()

    def get_context_data(self, **kwargs):
        """Get context data for template rendering"""
        context = super().get_context_data(**kwargs)

        try:
            start_time = time.time()

            # Get parameters
            selected_date = self._get_selected_date(self.request)
            target_date = selected_date + timedelta(days=1)

            # Check if force refresh is requested
            force_refresh = self.request.GET.get("force_refresh", "").lower() == "true"

            # Always get actual result if available
            actual_result = self._get_actual_result(target_date)

            # Try cache first (unless force refresh)
            cached_data = None
            if not force_refresh:
                try:
                    cached_data = self.cache_service.get_cached_prediction(
                        selected_date, "improved_combined"
                    )

                    # Validate cached data structure
                    if cached_data and not self._is_cached_data_complete(cached_data):
                        logger.warning(
                            f"Cached data incomplete for {selected_date}, regenerating..."
                        )
                        cached_data = None

                except Exception as cache_error:
                    logger.warning(f"Cache retrieval failed: {cache_error}")
                    cached_data = None

            if cached_data:
                # Add actual result and accuracy calculation to cached data
                if actual_result:
                    combined_predictions = cached_data.get("combined_predictions", [])
                    prediction_accuracy = self._calculate_prediction_accuracy(
                        combined_predictions, actual_result
                    )
                    cached_data["prediction_accuracy"] = prediction_accuracy

                context.update(
                    {
                        **cached_data,
                        "from_cache": True,
                        "cache_timestamp": datetime.now().isoformat(),
                        "selected_date": selected_date,
                        "target_date": target_date,
                        "actual_result": actual_result,
                        "show_predictions": True,
                        "analysis_complete": True,
                        "error": False,
                    }
                )

                logger.info(
                    f"Using cached data for {selected_date} with {len(cached_data.get('combined_predictions', []))} predictions"
                )
                return context

            # Generate fresh analysis
            logger.info(f"Generating fresh analysis for {selected_date}")

            # Get historical data
            historical_data = self._get_historical_data_before_date(selected_date)
            if not historical_data:
                context.update(
                    {
                        "error": True,
                        "error_message": "Không đủ dữ liệu lịch sử để phân tích",
                        "selected_date": selected_date,
                        "target_date": target_date,
                        "actual_result": actual_result,
                        "show_predictions": False,
                        "analysis_complete": False,
                    }
                )
                return context

            # Ensure ML models are available
            if not self.ml_service.models:
                logger.info("No ML models loaded, attempting to train...")
                try:
                    if hasattr(self.ml_service, "train_models"):
                        success = self.ml_service.train_models()
                        if not success:
                            logger.warning(
                                "Model training failed, continuing without ML predictions"
                            )
                    else:
                        logger.warning(
                            "train_models method not available, checking for models..."
                        )
                        if hasattr(self.ml_service, "_load_models"):
                            self.ml_service._load_models()
                        elif hasattr(self.ml_service, "load_models"):
                            self.ml_service.load_models()
                except Exception as train_error:
                    logger.error(f"Error during model training/loading: {train_error}")

            # Get ML predictions (sửa vấn đề ML predictions luôn hiển thị 00-19)
            ml_predictions = []
            try:
                if (
                    hasattr(self.ml_service, "predict_numbers")
                    and self.ml_service.models
                ):
                    ml_predictions = self.ml_service.predict_numbers(
                        historical_data=list(historical_data),
                        target_date=target_date,
                        top_k=20,
                    )
                    ml_predictions = self._sanitize_predictions(ml_predictions)

                    # Validate ML predictions - check if they're too sequential
                    if self._are_predictions_too_sequential(ml_predictions):
                        logger.warning(
                            "ML predictions appear to be sequential (00-19), likely a bug. Using alternative method."
                        )
                        ml_predictions = self._get_alternative_ml_predictions(
                            historical_data, target_date
                        )

                elif hasattr(self.ml_service, "predict") and self.ml_service.models:
                    prediction_result = self.ml_service.predict(
                        ket_qua_data=list(historical_data),
                        target_field="giai_db",
                        method="ensemble",
                    )
                    if prediction_result:
                        prediction_value = prediction_result.get("prediction", 50000)
                        confidence = prediction_result.get("confidence", 0.5)
                        ml_predictions = [
                            {
                                "number": f"{int(prediction_value) % 100:02d}",
                                "confidence": float(confidence),
                            }
                        ]
                else:
                    logger.info(
                        "No ML prediction methods available or no models loaded"
                    )

            except Exception as ml_error:
                logger.warning(f"ML prediction failed: {ml_error}")

            # Get traditional predictions
            traditional_predictions = self._get_traditional_predictions(
                target_date, selected_date, historical_data
            )

            # SHAP Analysis
            shap_analysis = {}
            try:
                if self.ml_service.models:
                    shap_analysis = self.shap_service.analyze_predictions(
                        historical_data=list(historical_data),
                        model_name="random_forest",
                    )
                    shap_analysis = self._sanitize_data(shap_analysis)
                else:
                    shap_analysis = {
                        "message": "No ML models available for SHAP analysis"
                    }
            except Exception as shap_error:
                logger.warning(f"SHAP analysis failed: {shap_error}")
                shap_analysis = {"error": str(shap_error)}

            # Combine all predictions
            combined_analysis = self._combine_all_predictions_enhanced(
                ml_predictions, traditional_predictions, historical_data
            )

            # Sanitize combined analysis
            combined_analysis = self._sanitize_data(combined_analysis)

            # Add SHAP analysis
            combined_analysis["shap_analysis"] = shap_analysis

            # Calculate prediction accuracy if actual result is available
            prediction_accuracy = None
            if actual_result:
                combined_predictions = combined_analysis.get("combined_predictions", [])
                prediction_accuracy = self._calculate_prediction_accuracy(
                    combined_predictions, actual_result
                )
                combined_analysis["prediction_accuracy"] = prediction_accuracy

            # Validate models
            if hasattr(self.ml_service, "validate_models"):
                model_validation = self.ml_service.validate_models()
                model_validation = self._sanitize_data(model_validation)
            else:
                model_validation = {
                    "total_models": 0,
                    "working_models": 0,
                    "message": "Model validation not available",
                }
            combined_analysis["model_status"] = model_validation

            # Performance metrics
            processing_time = time.time() - start_time
            combined_analysis.update(
                {
                    "selected_date": selected_date.isoformat(),
                    "target_date": target_date.isoformat(),
                    "processing_time": float(processing_time),
                    "from_cache": False,
                    "timestamp": datetime.now().isoformat(),
                    "data_quality": {
                        "historical_days": int(len(historical_data)),
                        "ml_predictions_count": int(len(ml_predictions)),
                        "traditional_methods": int(
                            len(traditional_predictions.get("predictions", {}))
                        ),
                        "working_models": int(
                            model_validation.get("working_models", 0)
                        ),
                    },
                }
            )

            # Cache the result only if it's complete
            try:
                if self._is_analysis_complete(combined_analysis):
                    self.cache_service.cache_prediction(
                        selected_date, "improved_combined", combined_analysis
                    )
                    logger.info(f"Cached complete analysis for {selected_date}")
                else:
                    logger.warning(
                        f"Analysis incomplete, not caching for {selected_date}"
                    )
            except Exception as cache_error:
                logger.warning(f"Failed to cache result: {cache_error}")

            # Prepare template context
            context.update(
                {
                    "analysis_results": combined_analysis,
                    "selected_date": selected_date,
                    "target_date": target_date,
                    "processing_time": processing_time,
                    "from_cache": False,
                    "timestamp": datetime.now(),
                    # Actual Result (always include if available)
                    "actual_result": actual_result,
                    "prediction_accuracy": prediction_accuracy,
                    # ML Results
                    "ml_predictions": ml_predictions,
                    "ml_predictions_count": len(ml_predictions),
                    # Traditional Results
                    "traditional_predictions": traditional_predictions,
                    "traditional_methods_count": len(
                        traditional_predictions.get("predictions", {})
                    ),
                    # Combined Results
                    "combined_predictions": combined_analysis.get(
                        "combined_predictions", []
                    ),
                    "prediction_summary": combined_analysis.get(
                        "prediction_summary", {}
                    ),
                    # SHAP Analysis
                    "shap_analysis": shap_analysis,
                    # Model Status
                    "model_status": model_validation,
                    "working_models": model_validation.get("working_models", 0),
                    # Data Quality
                    "historical_days": len(historical_data),
                    "data_quality": combined_analysis.get("data_quality", {}),
                    # Always show predictions
                    "show_predictions": True,
                    "analysis_complete": True,
                    "error": False,
                }
            )

        except Exception as e:
            logger.error(f"Error in ImprovedCombinedAnalysisView: {e}", exc_info=True)
            context.update(
                {
                    "error": True,
                    "error_message": str(e),
                    "timestamp": datetime.now(),
                    "selected_date": self._get_selected_date(self.request),
                    "target_date": self._get_selected_date(self.request)
                    + timedelta(days=1),
                    "actual_result": self._get_actual_result(
                        self._get_selected_date(self.request) + timedelta(days=1)
                    ),
                    "show_predictions": False,
                    "analysis_complete": False,
                }
            )

        return context

    def _is_cached_data_complete(self, cached_data):
        """Check if cached data is complete and valid"""
        try:
            if not isinstance(cached_data, dict):
                return False

            # Check for essential keys
            required_keys = [
                "combined_predictions",
                "ml_predictions",
                "traditional_predictions",
            ]
            for key in required_keys:
                if key not in cached_data:
                    logger.warning(f"Missing key in cached data: {key}")
                    return False

            # Check if predictions are not empty
            combined_predictions = cached_data.get("combined_predictions", [])
            if not combined_predictions:
                logger.warning("No combined predictions in cached data")
                return False

            # Check if predictions have proper structure
            if combined_predictions:
                sample_pred = combined_predictions[0]
                if not isinstance(sample_pred, dict) or "number" not in sample_pred:
                    logger.warning("Invalid prediction structure in cached data")
                    return False

            return True

        except Exception as e:
            logger.error(f"Error checking cached data completeness: {e}")
            return False

    def _is_analysis_complete(self, analysis):
        """Check if analysis is complete before caching"""
        try:
            if not analysis.get("combined_predictions"):
                return False

            if not analysis.get("data_quality", {}).get("historical_days", 0) > 0:
                return False

            return True

        except Exception:
            return False

    def _get_actual_result(self, target_date):
        """Get actual result for target date with extracted 2-digit numbers using model method"""
        try:
            result = KetQuaXoSo.objects.filter(ngay=target_date).first()
            if result:
                # Sử dụng method có sẵn trong model để lấy tất cả số 2 chữ số
                all_2digit_numbers = result.get_all_2digit_numbers()
                print(f"All 2-digit numbers for {target_date}: {all_2digit_numbers}")
                # Lấy riêng số 2 chữ số cuối của giải đặc biệt
                giai_db_numbers = []
                if result.giai_db:
                    giai_db_str = str(result.giai_db).zfill(5)  # Đảm bảo đủ 5 chữ số
                    giai_db_numbers = [giai_db_str[-2:]]  # Lấy 2 số cuối

                return {
                    "date": target_date,
                    "giai_db": result.giai_db,
                    "giai_db_numbers": giai_db_numbers,
                    "all_2digit_numbers": all_2digit_numbers,  # Đã được sorted và loại bỏ trùng lặp
                    "total_numbers": len(all_2digit_numbers),
                }
            return None
        except Exception as e:
            logger.error(f"Error getting actual result: {e}")
            return None

    def _sanitize_predictions(self, predictions):
        """Sanitize predictions to remove numpy types"""
        try:
            sanitized = []
            for pred in predictions:
                if isinstance(pred, dict):
                    sanitized_pred = {}
                    for key, value in pred.items():
                        if isinstance(value, np.integer):
                            sanitized_pred[key] = int(value)
                        elif isinstance(value, np.floating):
                            sanitized_pred[key] = float(value)
                        elif isinstance(value, np.ndarray):
                            sanitized_pred[key] = value.tolist()
                        else:
                            sanitized_pred[key] = value
                    sanitized.append(sanitized_pred)
                else:
                    sanitized.append(pred)
            return sanitized
        except Exception as e:
            logger.error(f"Error sanitizing predictions: {e}")
            return predictions

    def _sanitize_data(self, data):
        """Recursively sanitize data to remove numpy types"""
        try:
            if isinstance(data, dict):
                return {key: self._sanitize_data(value) for key, value in data.items()}
            elif isinstance(data, list):
                return [self._sanitize_data(item) for item in data]
            elif isinstance(data, np.integer):
                return int(data)
            elif isinstance(data, np.floating):
                return float(data)
            elif isinstance(data, np.ndarray):
                return data.tolist()
            elif isinstance(data, (date, datetime)):
                return data.isoformat()
            else:
                return data
        except Exception as e:
            logger.error(f"Error sanitizing data: {e}")
            return data

    def _combine_all_predictions_enhanced(
        self, ml_predictions, traditional_predictions, historical_data
    ):
        """Enhanced prediction combination"""
        try:
            combined_numbers = {}

            # Process ML predictions
            ml_weight = 0.5
            if ml_predictions:
                for prediction in ml_predictions:
                    try:
                        # Handle different prediction formats
                        if isinstance(prediction, dict):
                            number = prediction.get("number")
                            confidence = prediction.get("confidence", 0.5)
                        elif isinstance(prediction, str):
                            # Handle string predictions
                            number = prediction
                            confidence = 0.5
                        elif isinstance(prediction, (int, float)):
                            # Handle numeric predictions
                            number = str(int(prediction)).zfill(2)
                            confidence = 0.5
                        elif (
                            isinstance(prediction, (list, tuple))
                            and len(prediction) >= 2
                        ):
                            # Handle tuple/list format (number, confidence)
                            number = prediction[0]
                            confidence = prediction[1]
                        else:
                            continue

                        # Clean and validate number
                        if number is not None:
                            clean_number = self._extract_clean_number_from_prediction(
                                prediction
                            )
                            if clean_number:
                                combined_numbers[clean_number] = combined_numbers.get(
                                    clean_number, 0
                                ) + (confidence * ml_weight)

                    except Exception as pred_error:
                        logger.warning(
                            f"Error processing ML prediction {prediction}: {pred_error}"
                        )
                        continue

            # Process traditional predictions
            traditional_weight = 0.5
            traditional_preds = traditional_predictions.get("predictions", {})
            if traditional_preds:
                method_weight = (
                    traditional_weight / len(traditional_preds)
                    if len(traditional_preds) > 0
                    else traditional_weight
                )
                for method, numbers in traditional_preds.items():
                    if isinstance(numbers, list):
                        for num_info in numbers:
                            try:
                                if isinstance(num_info, dict):
                                    number = num_info.get("number", num_info.get("so"))
                                    confidence = num_info.get(
                                        "confidence", num_info.get("diem", 0.5)
                                    )
                                elif isinstance(num_info, str):
                                    number = num_info
                                    confidence = 0.5
                                else:
                                    continue

                                if number:
                                    clean_number = (
                                        self._extract_clean_number_from_prediction(
                                            num_info
                                        )
                                    )
                                    if clean_number:
                                        combined_numbers[clean_number] = (
                                            combined_numbers.get(clean_number, 0)
                                            + (confidence * method_weight)
                                        )

                            except Exception as trad_error:
                                logger.warning(
                                    f"Error processing traditional prediction {num_info}: {trad_error}"
                                )
                                continue

            # Sort and format results
            if not combined_numbers:
                logger.warning("No valid predictions found after combination")
                return {
                    "ml_predictions": ml_predictions,
                    "traditional_predictions": traditional_predictions,
                    "combined_predictions": [],
                    "prediction_summary": {"total_numbers": 0},
                }

            sorted_numbers = sorted(
                combined_numbers.items(), key=lambda x: x[1], reverse=True
            )

            enhanced_predictions = []
            for i, (number, score) in enumerate(sorted_numbers[:20]):
                enhanced_predictions.append(
                    {
                        "number": number,
                        "confidence": min(1.0, score),
                        "rank": i + 1,
                        "raw_score": float(score),
                    }
                )

            return {
                "ml_predictions": ml_predictions,
                "traditional_predictions": traditional_predictions,
                "combined_predictions": enhanced_predictions,
                "prediction_summary": {
                    "total_numbers": len(enhanced_predictions),
                    "ml_contribution": ml_weight,
                    "traditional_contribution": traditional_weight,
                    "top_confidence": (
                        enhanced_predictions[0]["confidence"]
                        if enhanced_predictions
                        else 0
                    ),
                },
            }

        except Exception as e:
            logger.error(f"Error in enhanced combination: {e}", exc_info=True)
            return {
                "ml_predictions": ml_predictions if ml_predictions else [],
                "traditional_predictions": (
                    traditional_predictions if traditional_predictions else {}
                ),
                "combined_predictions": [],
                "prediction_summary": {"total_numbers": 0, "error": str(e)},
            }

    def _get_traditional_predictions(self, target_date, selected_date, historical_data):
        """Get predictions from traditional methods"""
        try:

            predictor = BachThuLoPredictor(
                target_date=target_date, history_days=90, selected_date=selected_date
            )

            return predictor.predict()

        except Exception as e:
            logger.warning(f"Traditional prediction failed: {e}")
            return {"predictions": {}}

    def _get_historical_data_before_date(self, target_date):
        """Get historical data before target date"""
        try:
            from .models import KetQuaXoSo

            history_days = 90
            end_date = target_date - timedelta(days=1)
            start_date = end_date - timedelta(days=history_days)

            return KetQuaXoSo.objects.filter(
                ngay__range=(start_date, end_date)
            ).order_by("-ngay")

        except Exception as e:
            logger.error(f"Error getting historical data: {e}")
            return []

    def _get_selected_date(self, request):
        """Get selected date from request"""
        try:
            date_str = request.GET.get("selected_date")
            if date_str:
                return datetime.strptime(date_str, "%Y-%m-%d").date()
            return datetime.now().date()
        except Exception:
            return datetime.now().date()

    def clean_predictions_data(self, final_predictions):
        """
        Làm sạch dữ liệu final_predictions để đảm bảo number là số đơn giản
        """
        cleaned_predictions = []

        for prediction in final_predictions:
            cleaned_prediction = prediction.copy()

            # Kiểm tra nếu number là string phức tạp
            if isinstance(prediction["number"], str) and prediction[
                "number"
            ].startswith("{"):
                try:
                    # Trích xuất số từ string phức tạp
                    # Tìm pattern như "('06', 0.0)" hoặc "('34', 0.0)"
                    match = re.search(r"\('(\d+)',", prediction["number"])
                    if match:
                        cleaned_prediction["number"] = match.group(1)
                    else:
                        # Backup: thử parse JSON-like string
                        # Chuyển single quotes thành double quotes
                        json_str = prediction["number"].replace("'", '"')
                        try:
                            parsed = ast.literal_eval(prediction["number"])
                            if "number" in parsed:
                                # Trích xuất số từ tuple
                                number_tuple = parsed["number"]
                                if isinstance(number_tuple, str):
                                    # Parse tuple string như "('06', 0.0)"
                                    tuple_match = re.search(r"\('(\d+)',", number_tuple)
                                    if tuple_match:
                                        cleaned_prediction["number"] = (
                                            tuple_match.group(1)
                                        )
                        except:
                            # Nếu không parse được, bỏ qua item này
                            continue
                except:
                    # Nếu có lỗi, bỏ qua item này
                    continue

            # Đảm bảo number là string 2 chữ số
            if isinstance(cleaned_prediction["number"], str):
                number = cleaned_prediction["number"].zfill(
                    2
                )  # Thêm số 0 phía trước nếu cần
                cleaned_prediction["number"] = number

            cleaned_predictions.append(cleaned_prediction)

        return cleaned_predictions

    def _calculate_prediction_accuracy(self, predictions, actual_result):
        """Calculate accuracy of predictions against actual results"""
        try:
            if not predictions or not actual_result:
                return None

            # Extract predicted numbers - chuẩn hóa format
            predicted_numbers = []
            for pred in predictions:
                if isinstance(pred, dict):
                    number = pred.get("number", "")
                    # Chuẩn hóa thành 2 chữ số
                    if isinstance(number, (int, float)):
                        number = f"{int(number):02d}"
                    elif isinstance(number, str):
                        # Làm sạch và chuẩn hóa
                        clean_number = "".join(c for c in number if c.isdigit())
                        if clean_number:
                            number = clean_number[-2:].zfill(
                                2
                            )  # Lấy 2 số cuối và thêm 0 nếu cần
                    predicted_numbers.append(number)
                else:
                    # Xử lý trường hợp prediction không phải dict
                    clean_number = "".join(c for c in str(pred) if c.isdigit())
                    if clean_number:
                        predicted_numbers.append(clean_number[-2:].zfill(2))

            # Loại bỏ số trống và trùng lặp
            predicted_numbers = list(
                set([num for num in predicted_numbers if num and len(num) == 2])
            )

            # Get actual 2-digit numbers từ model method
            actual_numbers = actual_result.get("all_2digit_numbers", [])

            # Find matches
            matches = [num for num in predicted_numbers if num in actual_numbers]

            # Kiểm tra giải đặc biệt
            giai_db_matches = []
            giai_db_numbers = actual_result.get("giai_db_numbers", [])
            if giai_db_numbers:
                giai_db_matches = [
                    num for num in predicted_numbers if num in giai_db_numbers
                ]

            # Calculate metrics
            total_predictions = len(predicted_numbers)
            total_actual = len(actual_numbers)
            hit_count = len(matches)
            giai_db_hit_count = len(giai_db_matches)

            accuracy = (hit_count / total_actual * 100) if total_actual > 0 else 0
            hit_rate = (
                (hit_count / total_predictions * 100) if total_predictions > 0 else 0
            )

            return {
                "matches": matches,
                "giai_db_matches": giai_db_matches,
                "total_predictions": total_predictions,
                "total_actual": total_actual,
                "hit_count": hit_count,
                "giai_db_hit_count": giai_db_hit_count,
                "accuracy": round(accuracy, 1),
                "hit_rate": round(hit_rate, 1),
                "prediction_quality": self._assess_prediction_quality(hit_rate),
                "predicted_numbers": predicted_numbers,  # Để template sử dụng
                "actual_numbers": actual_numbers,  # Để template sử dụng
            }

        except Exception as e:
            logger.error(f"Error calculating prediction accuracy: {e}")
            return None

    def _assess_prediction_quality(self, hit_rate):
        """Assess prediction quality based on hit rate"""
        if hit_rate >= 15:
            return {"level": "excellent", "description": "Xuất sắc"}
        elif hit_rate >= 10:
            return {"level": "good", "description": "Tốt"}
        elif hit_rate >= 5:
            return {"level": "fair", "description": "Khá"}
        else:
            return {"level": "poor", "description": "Cần cải thiện"}

    def _validate_cache_data(self, cached_data):
        """Validate cached data structure"""
        try:
            if not isinstance(cached_data, dict):
                return False

            # Check for required keys
            required_keys = ["combined_results"]
            for key in required_keys:
                if key not in cached_data:
                    logger.warning(f"Missing required key in cached data: {key}")
                    return False

            # Check combined_results structure
            combined_results = cached_data.get("combined_results", {})
            if not isinstance(combined_results, dict):
                return False

            # Check for final_predictions
            final_predictions = combined_results.get("final_predictions", [])
            if not isinstance(final_predictions, list):
                return False

            # If we have predictions, validate their structure
            if final_predictions:
                sample_pred = final_predictions[0]
                if not isinstance(sample_pred, dict) or "number" not in sample_pred:
                    return False

            logger.info(
                f"Cached data validation passed: {len(final_predictions)} predictions found"
            )
            return True

        except Exception as e:
            logger.error(f"Error validating cached data: {e}")
            return False

    def _prepare_context_from_cache(
        self, cached_data, selected_date, target_date, hide_predictions
    ):
        """Prepare context from cached data"""
        context = cached_data.copy()

        # Ensure we have all required keys
        context.setdefault("ml_results", {"error": "Cached ML results not available"})
        context.setdefault("traditional_results", {})
        context.setdefault("combined_results", {"final_predictions": []})
        context.setdefault("historical_data_summary", {})

        return context

    def _generate_fresh_analysis(
        self, selected_date, target_date, hide_predictions, processing_stages
    ):
        """Generate fresh analysis"""
        context = {}

        try:
            # Stage 1: Load historical data
            processing_stages["data_loading"]["status"] = "in_progress"
            processing_stages["data_loading"]["message"] = "Đang tải dữ liệu lịch sử..."

            # Load 90 days of historical data
            start_date = selected_date - timedelta(days=90)
            logger.info(f"Loading historical data from {start_date} to {selected_date}")

            historical_data = list(
                KetQuaXoSo.objects.filter(
                    ngay__gte=start_date, ngay__lte=selected_date
                ).order_by("ngay")
            )

            if not historical_data:
                raise ValueError(
                    f"No historical data found for date range {start_date} to {selected_date}"
                )

            logger.info(
                f"Successfully loaded {len(historical_data)} historical records"
            )
            processing_stages["data_loading"]["status"] = "complete"
            processing_stages["data_loading"][
                "message"
            ] = f"Đã tải {len(historical_data)} bản ghi"

            # Stage 2: Traditional predictions
            processing_stages["traditional_analysis"]["status"] = "in_progress"
            processing_stages["traditional_analysis"][
                "message"
            ] = "Đang phân tích bằng phương pháp truyền thống..."

            logger.info("Starting traditional predictions...")
            traditional_results = self._run_traditional_predictions(
                historical_data, target_date
            )

            processing_stages["traditional_analysis"]["status"] = "complete"
            processing_stages["traditional_analysis"][
                "message"
            ] = "Hoàn thành phân tích truyền thống"

            # Count predictions by method
            pred_counts = {}
            for method, data in traditional_results.items():
                pred_counts[method] = len(data.get("predictions", []))

            logger.info(
                f"Traditional predictions completed: {', '.join([f'{k}={v}' for k, v in pred_counts.items()])}"
            )

            # Stage 3: ML predictions
            processing_stages["ml_analysis"]["status"] = "in_progress"
            processing_stages["ml_analysis"][
                "message"
            ] = "Đang phân tích bằng Machine Learning..."

            ml_results = self._run_ml_predictions(historical_data, target_date)

            processing_stages["ml_analysis"]["status"] = "complete"
            processing_stages["ml_analysis"]["message"] = "Hoàn thành phân tích ML"

            # Stage 4: Combine predictions
            processing_stages["combination"]["status"] = "in_progress"
            processing_stages["combination"][
                "message"
            ] = "Đang kết hợp các kết quả dự đoán..."

            logger.info("Starting prediction combination...")
            combined_results = self._combine_all_predictions(
                traditional_results, ml_results
            )

            processing_stages["combination"]["status"] = "complete"
            processing_stages["combination"]["message"] = "Đã kết hợp tất cả dự đoán"

            logger.info(
                f"Combined {len(combined_results.get('final_predictions', []))} final predictions"
            )

            # Stage 5: Cache results
            processing_stages["caching"]["status"] = "in_progress"
            processing_stages["caching"]["message"] = "Đang lưu kết quả vào cache..."

            # Validate and cache
            if (
                self._validate_cache_data({"combined_results": combined_results})
                and self.cache_service
            ):
                cache_data = {
                    "ml_results": ml_results,
                    "traditional_results": traditional_results,
                    "combined_results": combined_results,
                    "historical_data_summary": {
                        "total_records": len(historical_data),
                        "date_range": {"start": start_date, "end": selected_date},
                    },
                }

                # Use correct method name: cache_prediction_result instead of cache_prediction
                self.cache_service.cache_prediction_result(
                    selected_date.strftime("%Y-%m-%d"), "combined", cache_data
                )
                logger.info(f"Cached analysis results for {selected_date}")

                processing_stages["caching"]["status"] = "complete"
                processing_stages["caching"]["message"] = "Đã lưu vào cache"
            else:
                processing_stages["caching"]["status"] = "error"
                processing_stages["caching"]["message"] = "Lỗi khi lưu cache"

            # Record performance metrics
            self._record_performance_metrics(
                selected_date, target_date, combined_results
            )

            return {
                "ml_results": ml_results,
                "shap_results": {},  # TODO: Implement SHAP analysis
                "traditional_results": traditional_results,
                "combined_results": combined_results,
                "historical_data_summary": {
                    "total_records": len(historical_data),
                    "date_range": {"start": start_date, "end": selected_date},
                },
                "model_performance": {},  # TODO: Add model performance metrics
            }

        except Exception as e:
            logger.error(f"Error in fresh analysis: {e}", exc_info=True)
            processing_stages["data_loading"]["status"] = "error"
            processing_stages["data_loading"]["message"] = f"Lỗi: {str(e)}"

            return {
                "error": True,
                "error_message": str(e),
                "suggested_actions": [
                    "Kiểm tra kết nối cơ sở dữ liệu",
                    "Đảm bảo có dữ liệu lịch sử đầy đủ",
                    "Thử lại với ngày khác",
                ],
            }

    def _run_traditional_predictions(self, historical_data, target_date):
        """Run traditional prediction methods"""
        try:
            # Convert Django objects to format expected by predictors
            formatted_data = []
            for record in historical_data:
                # Extract all numbers from the record
                all_numbers = []
                for field_name in [
                    "giai_db",
                    "giai_1",
                    "giai_2",
                    "giai_3",
                    "giai_4",
                    "giai_5",
                    "giai_6",
                    "giai_7",
                ]:
                    field_value = getattr(record, field_name, None)
                    if field_value:
                        numbers = self._extract_two_digits(field_value)
                        all_numbers.extend(numbers)

                formatted_data.append(
                    {
                        "date": record.ngay,
                        "numbers": list(set(all_numbers)),  # Remove duplicates
                    }
                )

            # Run different prediction methods
            results = {}

            # 1. Frequency-based predictions
            results["frequency_based"] = self._get_frequency_predictions(formatted_data)

            # 2. Pattern-based predictions
            results["pattern_based"] = self._get_pattern_predictions(formatted_data)

            # 3. Bach Thu Lo predictions
            results["bach_thu_lo"] = self._get_bach_thu_predictions(
                target_date, formatted_data
            )

            # 4. Statistical predictions
            results["statistical"] = self._get_statistical_predictions(formatted_data)

            return results

        except Exception as e:
            logger.error(f"Error in traditional predictions: {e}", exc_info=True)
            return {
                "frequency_based": {"predictions": [], "error": str(e)},
                "pattern_based": {"predictions": [], "error": str(e)},
                "bach_thu_lo": {"predictions": [], "error": str(e)},
                "statistical": {"predictions": [], "error": str(e)},
            }

    def _get_ml_predictions(self):
        """Get ML model predictions"""
        try:
            ml_service = MLModelService()

            # Get recent data for prediction
            recent_data = KetQuaXoSo.objects.order_by("-ngay")[:30]

            if not recent_data.exists():
                return {"predictions": [], "error": "No historical data available"}

            # Make predictions
            predictions = ml_service.predict_next_numbers(list(recent_data))

            # Chuẩn hóa format predictions
            formatted_predictions = []
            for pred in predictions:
                if isinstance(pred, dict):
                    # If it's already formatted
                    formatted_predictions.append(
                        {
                            "number": str(pred.get("number", pred.get("num", 0))).zfill(
                                2
                            ),
                            "confidence": float(pred.get("confidence", 0.5)),
                            "method": "ML Model",
                        }
                    )
                elif isinstance(pred, (list, tuple)):
                    # If it's (number, confidence) tuple
                    formatted_predictions.append(
                        {
                            "number": str(pred[0]).zfill(2),
                            "confidence": float(pred[1]) if len(pred) > 1 else 0.5,
                            "method": "ML Model",
                        }
                    )
                else:
                    # If it's just a number
                    formatted_predictions.append(
                        {
                            "number": str(pred).zfill(2),
                            "confidence": 0.5,
                            "method": "ML Model",
                        }
                    )

            return {
                "predictions": formatted_predictions[:10],  # Limit to 10
                "confidence": 0.75,
                "model_info": {"name": "Advanced ML Ensemble"},
            }

        except Exception as e:
            logger.error(f"ML prediction error: {e}")
            return {"predictions": [], "error": str(e)}

    def _get_frequency_predictions(self, historical_data):
        """Get frequency-based predictions"""
        try:
            all_numbers = []
            for record in historical_data:
                all_numbers.extend(record.get("numbers", []))

            # Count frequency
            freq_counter = Counter(all_numbers)
            top_numbers = freq_counter.most_common(15)

            predictions = []
            for number, frequency in top_numbers:
                predictions.append(
                    {
                        "number": str(number).zfill(2),
                        "confidence": min(0.9, frequency / len(historical_data)),
                        "frequency": frequency,
                        "method": "frequency",
                    }
                )

            return {
                "predictions": predictions,
                "method": "frequency_analysis",
                "confidence": 0.7,
            }

        except Exception as e:
            logger.error(f"Frequency prediction error: {e}")
            return {"predictions": [], "error": str(e)}

    def _get_pattern_predictions(self, historical_data):
        """Get pattern-based predictions"""
        try:
            # Analyze recent patterns (last 7 days)
            recent_data = (
                historical_data[-7:] if len(historical_data) >= 7 else historical_data
            )
            pattern_numbers = set()

            for record in recent_data:
                pattern_numbers.update(record.get("numbers", []))

            predictions = []
            for number in list(pattern_numbers)[:12]:
                predictions.append(
                    {
                        "number": str(number).zfill(2),
                        "confidence": 0.6,
                        "method": "pattern",
                        "reason": "recent_pattern",
                    }
                )

            return {
                "predictions": predictions,
                "method": "pattern_analysis",
                "confidence": 0.6,
            }

        except Exception as e:
            logger.error(f"Pattern prediction error: {e}")
            return {"predictions": [], "error": str(e)}

    def _get_bach_thu_predictions(self, target_date, historical_data):
        """Get Bach Thu Lo predictions"""
        try:
            predictor = BachThuLoPredictor(target_date=target_date, history_days=90)

            predictions = predictor.predict_for_date(target_date)

            # Convert to standard format
            formatted_predictions = []
            if isinstance(predictions, dict) and "predictions" in predictions:
                for pred in predictions["predictions"]:
                    clean_number = self._extract_clean_number_from_prediction(pred)
                    if clean_number:
                        formatted_predictions.append(
                            {
                                "number": clean_number,  # Đây sẽ là string "18", "63", etc.
                                "confidence": 0.8,
                                "method": "bach_thu_lo",
                            }
                        )
            elif isinstance(predictions, list):
                for pred in predictions:
                    clean_number = self._extract_clean_number_from_prediction(pred)
                    if clean_number:
                        formatted_predictions.append(
                            {
                                "number": clean_number,  # Đây sẽ là string "18", "63", etc.
                                "confidence": 0.8,
                                "method": "bach_thu_lo",
                            }
                        )

            return {
                "predictions": formatted_predictions[:10],  # Limit to 10
                "method": "bach_thu_analysis",
                "confidence": 0.8,
            }

        except Exception as e:
            logger.error(f"Bach Thu Lo prediction error: {e}")
            return {"predictions": [], "error": str(e)}

    def _get_statistical_predictions(self, historical_data):
        """Get statistical predictions"""
        try:
            all_numbers = []
            for record in historical_data:
                all_numbers.extend(record.get("numbers", []))

            # Calculate statistics
            number_stats = Counter(all_numbers)
            avg_freq = (
                sum(number_stats.values()) / len(number_stats) if number_stats else 0
            )

            predictions = []
            for number, frequency in number_stats.items():
                if avg_freq * 0.5 <= frequency <= avg_freq * 1.5:  # Moderate frequency
                    predictions.append(
                        {
                            "number": str(number).zfill(2),
                            "confidence": min(0.8, frequency / len(historical_data)),
                            "frequency": frequency,
                            "method": "statistical",
                        }
                    )

            # Sort by confidence and limit
            predictions.sort(key=lambda x: x["confidence"], reverse=True)

            return {
                "predictions": predictions[:10],
                "method": "statistical_analysis",
                "confidence": 0.65,
            }

        except Exception as e:
            logger.error(f"Statistical prediction error: {e}")
            return {"predictions": [], "error": str(e)}

    def _run_ml_predictions(self, historical_data, target_date):
        """Run ML predictions"""
        try:
            if not self.ml_service:
                return {"error": "ML service not available"}

            # Convert historical data to format expected by ML service
            formatted_data = []
            for record in historical_data:
                all_numbers = []
                for field_name in [
                    "giai_db",
                    "giai_1",
                    "giai_2",
                    "giai_3",
                    "giai_4",
                    "giai_5",
                    "giai_6",
                    "giai_7",
                ]:
                    field_value = getattr(record, field_name, None)
                    if field_value:
                        numbers = self._extract_two_digits(field_value)
                        all_numbers.extend(numbers)

                formatted_data.append(
                    {"date": record.ngay, "numbers": list(set(all_numbers))}
                )

            predictions = self.ml_service.predict_for_date(target_date, formatted_data)

            return {
                "predictions": predictions,
                "model_info": {"name": "Enhanced ML Model"},
                "confidence": 0.75,
            }

        except Exception as e:
            logger.error(f"ML prediction error: {e}")
            return {"error": str(e)}

    def _combine_all_predictions(self, traditional_results, ml_results):
        """Combine all predictions with intelligent weighting"""
        try:
            all_predictions = (
                {}
            )  # {number: {'sources': [], 'total_weight': 0, 'confidence': 0}}

            # Method weights
            method_weights = {
                "frequency_based": 0.25,
                "pattern_based": 0.15,
                "bach_thu_lo": 0.30,
                "statistical": 0.20,
                "ml_models": 0.35,
            }

            # Collect traditional predictions
            for method_name, method_data in traditional_results.items():
                if method_data.get("predictions") and not method_data.get("error"):
                    weight = method_weights.get(method_name, 0.1)

                    for pred in method_data["predictions"]:
                        # Sửa lỗi ở đây: Extract clean number thay vì lấy trực tiếp pred['number']
                        clean_number = self._extract_clean_number_from_prediction(pred)
                        if clean_number:
                            confidence = pred.get("confidence", 0.5)

                            if clean_number not in all_predictions:
                                all_predictions[clean_number] = {
                                    "sources": [],
                                    "total_weight": 0,
                                    "confidence": 0,
                                }

                            all_predictions[clean_number]["sources"].append(method_name)
                            all_predictions[clean_number]["total_weight"] += (
                                weight * confidence
                            )
                            all_predictions[clean_number]["confidence"] = max(
                                all_predictions[clean_number]["confidence"], confidence
                            )
            logger.info(f"Collected {len(all_predictions)} traditional predictions")
            logger.info(f"thu thap mlresults {len(ml_results)} ML predictions")
            logger.info(f" mlresults {ml_results} ML predictions")

            # Collect ML predictions if available
            if (
                ml_results
                and ml_results.get("predictions")
                and not ml_results.get("error")
            ):
                weight = method_weights.get("ml_models", 0.35)

                for pred in ml_results["predictions"]:
                    clean_number = self._extract_clean_number_from_prediction(pred)
                    if clean_number:
                        confidence = (
                            0.75
                            if not isinstance(pred, dict)
                            else pred.get("confidence", 0.75)
                        )

                        if clean_number not in all_predictions:
                            all_predictions[clean_number] = {
                                "sources": [],
                                "total_weight": 0,
                                "confidence": 0,
                            }

                        all_predictions[clean_number]["sources"].append("ml_models")
                        all_predictions[clean_number]["total_weight"] += (
                            weight * confidence
                        )
                        all_predictions[clean_number]["confidence"] = max(
                            all_predictions[clean_number]["confidence"], confidence
                        )

            # Generate final predictions
            final_predictions = []
            for number, data in all_predictions.items():
                final_predictions.append(
                    {
                        "number": number,
                        "confidence": data["confidence"],
                        "weight": data["total_weight"],
                        "sources": data["sources"],
                        "source_count": len(data["sources"]),
                    }
                )

            # Sort by weight and confidence
            final_predictions.sort(
                key=lambda x: (x["weight"], x["confidence"]), reverse=True
            )

            # Limit to top 20
            final_predictions = final_predictions[:20]

            return {
                "final_predictions": final_predictions,
                "method_weights": method_weights,
                "total_sources": len(traditional_results)
                + (1 if ml_results and not ml_results.get("error") else 0),
                "combination_strategy": "weighted_ensemble",
            }

        except Exception as e:
            logger.error(f"Prediction combination error: {e}")
            return {"final_predictions": [], "error": str(e)}

    # Thêm method mới để extract clean number:
    def _extract_clean_number_from_prediction(self, pred):
        """Extract clean number from prediction regardless of format"""
        try:
            if pred is None:
                return None

            if isinstance(pred, dict):
                # Get number from prediction dict
                number = pred.get("number")
                if number is None:
                    # Try other fields
                    number = (
                        pred.get("num") or pred.get("prediction") or pred.get("value")
                    )

                if isinstance(number, str):
                    # Handle complex strings like "{'number': \"('18', 0.0)\", 'confidence': 0.5...}"
                    if number.startswith("{") or number.startswith("('"):
                        # Extract number from tuple string
                        match = re.search(r"'(\d+)'", number)
                        if match:
                            return match.group(1).zfill(2)
                    else:
                        # Clean simple string
                        clean_num = re.sub(r"[^\d]", "", str(number))
                        if clean_num.isdigit() and len(clean_num) >= 1:
                            return clean_num[-2:].zfill(2)

                elif isinstance(number, (int, float)):
                    return str(int(number)).zfill(2)

                elif isinstance(number, tuple) and len(number) > 0:
                    return str(int(number[0])).zfill(2)

            elif isinstance(pred, (int, float)):
                return str(int(pred)).zfill(2)

            elif isinstance(pred, str):
                # Handle string predictions
                if pred.startswith("('") and "'" in pred:
                    match = re.search(r"'(\d+)'", pred)
                    if match:
                        return match.group(1).zfill(2)
                else:
                    clean_num = re.sub(r"[^\d]", "", pred)
                    if clean_num.isdigit() and len(clean_num) >= 1:
                        return clean_num[-2:].zfill(2)

            elif isinstance(pred, (list, tuple)) and len(pred) > 0:
                return self._extract_clean_number_from_prediction(pred[0])

            return None

        except Exception as e:
            logger.error(f"Error extracting clean number from {pred}: {e}")
            return None

    def _record_performance_metrics(self, selected_date, target_date, combined_results):
        """Record performance metrics"""
        try:
            analysis, created = DailyPredictionAnalysis.objects.get_or_create(
                analysis_date=selected_date,
                defaults={
                    "target_date": target_date,
                    "total_predictions": len(
                        combined_results.get("final_predictions", [])
                    ),
                    "predictions_data": combined_results,
                },
            )
            logger.info(
                f"Recorded performance metrics for {selected_date} -> {target_date}"
            )

        except Exception as e:
            logger.error(f"Failed to record performance metrics: {e}")

    def _debug_final_predictions(self, context):
        """Debug final predictions"""
        logger.info("=== DEBUG FINAL PREDICTIONS ===")

        combined_results = context.get("combined_results", {})
        if combined_results:
            final_predictions = combined_results.get("final_predictions", [])
            logger.info(f"Final predictions count: {final_predictions}")

            if final_predictions:
                for i, pred in enumerate(final_predictions[:5]):
                    logger.info(f"Prediction {i}: {pred}")
        else:
            logger.warning("No combined_results in context")

    def _get_bach_thu_lo_predictions(self):
        """Get Bach Thu Lo predictions"""
        predictions = []

        try:
            from results.bach_thu_methods import DauDuoiMethod, GanMethod, GapMethod

            methods = [
                ("Đầu Đuôi", DauDuoiMethod()),
                ("Gần", GanMethod()),
                ("Gap", GapMethod()),
            ]

            for method_name, method_instance in methods:
                try:
                    # Get predictions from method
                    raw_predictions = method_instance.predict()

                    # Convert to clean format
                    if isinstance(raw_predictions, list):
                        for pred in raw_predictions:
                            clean_number = self._extract_clean_number(pred)
                            if clean_number:
                                predictions.append(
                                    {
                                        "number": clean_number,
                                        "confidence": 0.7,  # Default confidence for Bach Thu Lo
                                        "method": f"Bach Thu Lo - {method_name}",
                                        "source": "bach_thu_lo",
                                    }
                                )

                    elif isinstance(raw_predictions, dict):
                        # Handle dictionary format
                        for key, value in raw_predictions.items():
                            clean_number = self._extract_clean_number(value)
                            if clean_number:
                                predictions.append(
                                    {
                                        "number": clean_number,
                                        "confidence": 0.7,
                                        "method": f"Bach Thu Lo - {method_name}",
                                        "source": "bach_thu_lo",
                                    }
                                )

                    else:
                        # Handle single prediction
                        clean_number = self._extract_clean_number(raw_predictions)
                        if clean_number:
                            predictions.append(
                                {
                                    "number": clean_number,
                                    "confidence": 0.7,
                                    "method": f"Bach Thu Lo - {method_name}",
                                    "source": "bach_thu_lo",
                                }
                            )

                except Exception as e:
                    logger.error(f"Error getting {method_name} predictions: {e}")
                    continue

            return predictions[:5]  # Limit to 5 predictions

        except Exception as e:
            logger.error(f"Error getting Bach Thu Lo predictions: {e}")
            return []

    def _extract_clean_number(self, prediction):
        """Extract clean 2-digit number from various formats"""
        try:
            import re

            if isinstance(prediction, dict):
                # Look for number in various fields
                for field in ["number", "num", "prediction", "value", "result"]:
                    if field in prediction:
                        return self._extract_clean_number(prediction[field])

            elif isinstance(prediction, (list, tuple)):
                # Take first element if it's a list/tuple
                if len(prediction) > 0:
                    return self._extract_clean_number(prediction[0])

            elif isinstance(prediction, str):
                # Extract digits from string
                if prediction.startswith("(") and prediction.endswith(")"):
                    # Handle tuple string like "('86', 0.0)"
                    match = re.search(r"'(\d+)'", prediction)
                    if match:
                        return match.group(1).zfill(2)
                else:
                    # Extract all digits
                    digits = re.sub(r"[^\d]", "", prediction)
                    if digits and len(digits) >= 2:
                        return digits[-2:].zfill(2)  # Take last 2 digits

            elif isinstance(prediction, (int, float)):
                # Convert number to 2-digit string
                return str(int(prediction)).zfill(2)

            return None

        except Exception as e:
            logger.error(f"Error extracting clean number from {prediction}: {e}")
            return None

    def _format_prediction_number(self, prediction):
        """Format prediction number to clean string"""
        try:
            if isinstance(prediction, dict):
                # Get number from various possible fields
                number = (
                    prediction.get("number")
                    or prediction.get("num")
                    or prediction.get("prediction")
                )

                if isinstance(number, str):
                    # Handle cases like "('86', 0.0)" or "86"
                    if number.startswith("(") and number.endswith(")"):
                        # Extract from tuple string
                        import re

                        match = re.search(r"'(\d+)'", number)
                        if match:
                            return match.group(1).zfill(2)
                    else:
                        # Clean string
                        clean_num = re.sub(r"[^\d]", "", str(number))
                        if clean_num.isdigit():
                            return clean_num.zfill(2)

                elif isinstance(number, (int, float)):
                    return str(int(number)).zfill(2)

                elif isinstance(number, tuple):
                    # Handle tuple (number, confidence)
                    if len(number) >= 1:
                        return str(int(number[0])).zfill(2)

            elif isinstance(prediction, (int, float)):
                return str(int(prediction)).zfill(2)

            elif isinstance(prediction, str):
                clean_num = re.sub(r"[^\d]", "", prediction)
                if clean_num.isdigit():
                    return clean_num.zfill(2)

            return "00"  # Default fallback

        except Exception as e:
            logger.error(f"Error formatting prediction number: {e}")
            return "00"

    def _format_predictions_for_display(self, predictions):
        """Format predictions for template display"""
        formatted_predictions = []

        for pred in predictions:
            try:
                # Handle different prediction formats
                clean_number = self._format_prediction_number(pred)

                # Extract confidence score
                confidence = 0.0
                if isinstance(pred, dict):
                    confidence = pred.get("confidence", pred.get("score", 0.0))
                    if (
                        "number" in pred
                        and isinstance(pred["number"], str)
                        and pred["number"].startswith("(")
                    ):
                        # Extract confidence from tuple string like "('18', 0.8)"
                        try:
                            import ast

                            tuple_data = ast.literal_eval(pred["number"])
                            if isinstance(tuple_data, tuple) and len(tuple_data) > 1:
                                confidence = float(tuple_data[1])
                        except:
                            pass

                # Extract method info
                method = "Unknown"
                if isinstance(pred, dict):
                    method = pred.get("method", pred.get("source", "Unknown"))

                formatted_predictions.append(
                    {
                        "number": clean_number,
                        "confidence": float(confidence),
                        "method": method,
                        "original": pred,  # Keep original for debugging if needed
                    }
                )

            except Exception as e:
                logger.error(f"Error formatting prediction: {pred}, error: {e}")
                formatted_predictions.append(
                    {
                        "number": "00",
                        "confidence": 0.0,
                        "method": "Error",
                        "original": pred,
                    }
                )

        return formatted_predictions


class PredictionPerformanceReportView(TemplateView):
    """
    View báo cáo hiệu suất dự đoán tổng quan
    """

    template_name = "results/improved_prediction_performance_report.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        try:
            # Get date range parameters
            report_type = self.request.GET.get(
                "report_type", "week"
            )  # week, month, quarter
            end_date = self._get_end_date()
            start_date = self._get_start_date(end_date, report_type)

            # Generate comprehensive report
            report_data = self._generate_performance_report(
                start_date, end_date, report_type
            )

            context.update(
                {
                    "report_data": report_data,
                    "report_type": report_type,
                    "start_date": start_date,
                    "end_date": end_date,
                    "date_range_display": self._get_date_range_display(
                        start_date, end_date, report_type
                    ),
                }
            )

        except Exception as e:
            logger.error(f"Error generating performance report: {e}")
            context.update({"error": True, "error_message": str(e)})

        return context

    def _get_end_date(self):
        """Get end date from request or use current date"""
        try:
            date_str = self.request.GET.get("end_date")
            if date_str:
                return datetime.strptime(date_str, "%Y-%m-%d").date()
            return datetime.now().date()
        except Exception:
            return datetime.now().date()

    def _get_start_date(self, end_date, report_type):
        """Calculate start date based on report type"""
        if report_type == "week":
            return end_date - timedelta(days=7)
        elif report_type == "month":
            return end_date - timedelta(days=30)
        elif report_type == "quarter":
            return end_date - timedelta(days=90)
        else:
            return end_date - timedelta(days=7)

    def _get_date_range_display(self, start_date, end_date, report_type):
        """Get display string for date range"""
        if report_type == "week":
            return f"Tuần từ {start_date.strftime('%d/%m/%Y')} đến {end_date.strftime('%d/%m/%Y')}"
        elif report_type == "month":
            return f"Tháng từ {start_date.strftime('%d/%m/%Y')} đến {end_date.strftime('%d/%m/%Y')}"
        elif report_type == "quarter":
            return f"Quý từ {start_date.strftime('%d/%m/%Y')} đến {end_date.strftime('%d/%m/%Y')}"
        else:
            return f"Từ {start_date.strftime('%d/%m/%Y')} đến {end_date.strftime('%d/%m/%Y')}"

    def _generate_performance_report(self, start_date, end_date, report_type):
        """Generate comprehensive performance report"""
        try:
            # Get all lottery results in date range
            actual_results = KetQuaXoSo.objects.filter(
                ngay__range=(start_date, end_date)
            ).order_by("ngay")

            daily_performances = []
            method_performances = {
                "ml_models": {"total_predictions": 0, "hits": 0, "daily_hits": []},
                "traditional": {"total_predictions": 0, "hits": 0, "daily_hits": []},
                "combined": {"total_predictions": 0, "hits": 0, "daily_hits": []},
                "frequency_based": {
                    "total_predictions": 0,
                    "hits": 0,
                    "daily_hits": [],
                },
                "pattern_based": {"total_predictions": 0, "hits": 0, "daily_hits": []},
                "bach_thu_lo": {"total_predictions": 0, "hits": 0, "daily_hits": []},
                "statistical": {"total_predictions": 0, "hits": 0, "daily_hits": []},
            }

            for result in actual_results:
                try:
                    analysis_date = result.ngay - timedelta(days=1)

                    # Try to get cached analysis for this date
                    cache_service = PredictionCacheService()
                    cached_data = cache_service.get_cached_prediction(
                        analysis_date, "improved_combined"
                    )

                    if cached_data:
                        daily_perf = self._analyze_daily_performance(
                            cached_data, result
                        )
                        daily_performances.append(daily_perf)

                        # Update method performances
                        self._update_method_performances(
                            method_performances, daily_perf
                        )
                    else:
                        # Generate analysis for this date if not cached
                        logger.info(
                            f"No cached data for {analysis_date}, generating fresh analysis..."
                        )
                        daily_perf = self._generate_daily_analysis(
                            analysis_date, result
                        )
                        if daily_perf:
                            daily_performances.append(daily_perf)
                            self._update_method_performances(
                                method_performances, daily_perf
                            )

                except Exception as daily_error:
                    logger.warning(f"Error analyzing day {result.ngay}: {daily_error}")
                    continue

            # Calculate summary statistics
            summary_stats = self._calculate_summary_statistics(
                daily_performances, method_performances
            )

            # Generate insights and recommendations
            insights = self._generate_insights(
                daily_performances, method_performances, summary_stats
            )

            # Prepare chart data
            chart_data = self._prepare_chart_data(
                daily_performances, method_performances
            )

            return {
                "daily_performances": daily_performances,
                "method_performances": method_performances,
                "summary_stats": summary_stats,
                "insights": insights,
                "chart_data": chart_data,
                "total_days_analyzed": len(daily_performances),
                "date_range": {
                    "start": start_date,
                    "end": end_date,
                    "days": (end_date - start_date).days,
                },
            }

        except Exception as e:
            logger.error(f"Error generating performance report: {e}")
            return {"error": str(e)}

    def _analyze_daily_performance(self, cached_data, actual_result):
        """Analyze performance for a single day"""
        try:
            analysis_date = actual_result.ngay - timedelta(days=1)
            actual_numbers = actual_result.get_all_2digit_numbers()

            # Get predictions from cached data
            combined_predictions = cached_data.get("combined_predictions", [])
            ml_predictions = cached_data.get("ml_predictions", [])
            traditional_predictions = cached_data.get(
                "traditional_predictions", {}
            ).get("predictions", {})

            # Analyze combined predictions
            combined_hits = self._count_hits(combined_predictions, actual_numbers)

            # Analyze ML predictions
            ml_hits = self._count_hits(ml_predictions, actual_numbers)

            # Analyze traditional methods
            traditional_hits = {}
            for method, predictions in traditional_predictions.items():
                traditional_hits[method] = self._count_hits(predictions, actual_numbers)

            # Check for special prize hits
            giai_db_number = (
                str(actual_result.giai_db)[-2:] if actual_result.giai_db else None
            )

            return {
                "date": analysis_date,
                "target_date": actual_result.ngay,
                "actual_numbers": actual_numbers,
                "giai_db_number": giai_db_number,
                "combined": {
                    "total_predictions": len(combined_predictions),
                    "hits": combined_hits,
                    "hit_rate": (
                        (combined_hits / len(combined_predictions) * 100)
                        if combined_predictions
                        else 0
                    ),
                    "predictions": [
                        pred.get("number") for pred in combined_predictions[:10]
                    ],
                },
                "ml": {
                    "total_predictions": len(ml_predictions),
                    "hits": ml_hits,
                    "hit_rate": (
                        (ml_hits / len(ml_predictions) * 100) if ml_predictions else 0
                    ),
                    "predictions": [pred.get("number") for pred in ml_predictions[:10]],
                },
                "traditional": traditional_hits,
                "giai_db_hit": (
                    giai_db_number
                    in [pred.get("number") for pred in combined_predictions]
                    if giai_db_number
                    else False
                ),
                "quality_score": self._calculate_quality_score(
                    combined_hits,
                    len(combined_predictions),
                    giai_db_number,
                    combined_predictions,
                ),
            }

        except Exception as e:
            logger.error(f"Error analyzing daily performance: {e}")
            return None

    def _count_hits(self, predictions, actual_numbers):
        """Count how many predictions hit"""
        hits = 0
        for pred in predictions:
            pred_number = (
                pred.get("number", "") if isinstance(pred, dict) else str(pred)
            )
            if pred_number in actual_numbers:
                hits += 1
        return hits

    def _calculate_quality_score(
        self, hits, total_predictions, giai_db_number, predictions
    ):
        """Calculate quality score for the day"""
        base_score = (hits / total_predictions * 100) if total_predictions > 0 else 0

        # Bonus for special prize hit
        giai_db_bonus = 0
        if giai_db_number:
            for pred in predictions[:5]:  # Check top 5 predictions
                if pred.get("number") == giai_db_number:
                    giai_db_bonus = 25  # 25 point bonus
                    break

        return min(100, base_score + giai_db_bonus)

    def _update_method_performances(self, method_performances, daily_perf):
        """Update overall method performance statistics"""
        try:
            # Update combined performance
            combined = daily_perf.get("combined", {})
            method_performances["combined"]["total_predictions"] += combined.get(
                "total_predictions", 0
            )
            method_performances["combined"]["hits"] += combined.get("hits", 0)
            method_performances["combined"]["daily_hits"].append(
                {
                    "date": daily_perf["date"],
                    "hits": combined.get("hits", 0),
                    "total": combined.get("total_predictions", 0),
                    "hit_rate": combined.get("hit_rate", 0),
                }
            )

            # Update ML performance
            ml = daily_perf.get("ml", {})
            method_performances["ml_models"]["total_predictions"] += ml.get(
                "total_predictions", 0
            )
            method_performances["ml_models"]["hits"] += ml.get("hits", 0)
            method_performances["ml_models"]["daily_hits"].append(
                {
                    "date": daily_perf["date"],
                    "hits": ml.get("hits", 0),
                    "total": ml.get("total_predictions", 0),
                    "hit_rate": ml.get("hit_rate", 0),
                }
            )

            # Update traditional methods
            traditional = daily_perf.get("traditional", {})
            for method, data in traditional.items():
                if method not in method_performances:
                    method_performances[method] = {
                        "total_predictions": 0,
                        "hits": 0,
                        "daily_hits": [],
                    }

                method_performances[method]["total_predictions"] += data.get(
                    "total_predictions", 0
                )
                method_performances[method]["hits"] += data.get("hits", 0)
                method_performances[method]["daily_hits"].append(
                    {
                        "date": daily_perf["date"],
                        "hits": data.get("hits", 0),
                        "total": data.get("total_predictions", 0),
                        "hit_rate": data.get("hit_rate", 0),
                    }
                )

        except Exception as e:
            logger.error(f"Error updating method performances: {e}")

    def _calculate_summary_statistics(self, daily_performances, method_performances):
        """Calculate summary statistics"""
        try:
            total_days = len(daily_performances)
            if total_days == 0:
                return {"error": "No data available"}

            # Overall statistics
            total_predictions = sum(
                day.get("combined", {}).get("total_predictions", 0)
                for day in daily_performances
            )
            total_hits = sum(
                day.get("combined", {}).get("hits", 0) for day in daily_performances
            )
            overall_hit_rate = (
                (total_hits / total_predictions * 100) if total_predictions > 0 else 0
            )

            # Best and worst days
            daily_hit_rates = [
                day.get("combined", {}).get("hit_rate", 0) for day in daily_performances
            ]
            best_day_rate = max(daily_hit_rates) if daily_hit_rates else 0
            worst_day_rate = min(daily_hit_rates) if daily_hit_rates else 0
            avg_day_rate = (
                sum(daily_hit_rates) / len(daily_hit_rates) if daily_hit_rates else 0
            )

            # Special prize hits
            giai_db_hits = sum(
                1 for day in daily_performances if day.get("giai_db_hit", False)
            )
            giai_db_hit_rate = (
                (giai_db_hits / total_days * 100) if total_days > 0 else 0
            )

            # Quality score statistics
            quality_scores = [day.get("quality_score", 0) for day in daily_performances]
            avg_quality_score = (
                sum(quality_scores) / len(quality_scores) if quality_scores else 0
            )

            # Method comparison
            method_comparison = {}
            for method, data in method_performances.items():
                if data["total_predictions"] > 0:
                    method_comparison[method] = {
                        "hit_rate": (data["hits"] / data["total_predictions"] * 100),
                        "total_predictions": data["total_predictions"],
                        "total_hits": data["hits"],
                    }

            return {
                "total_days": total_days,
                "total_predictions": total_predictions,
                "total_hits": total_hits,
                "overall_hit_rate": round(overall_hit_rate, 2),
                "best_day_rate": round(best_day_rate, 2),
                "worst_day_rate": round(worst_day_rate, 2),
                "avg_day_rate": round(avg_day_rate, 2),
                "giai_db_hits": giai_db_hits,
                "giai_db_hit_rate": round(giai_db_hit_rate, 2),
                "avg_quality_score": round(avg_quality_score, 2),
                "method_comparison": method_comparison,
            }

        except Exception as e:
            logger.error(f"Error calculating summary statistics: {e}")
            return {"error": str(e)}

    def _generate_insights(
        self, daily_performances, method_performances, summary_stats
    ):
        """Generate insights and recommendations"""
        insights = []
        recommendations = []

        try:
            # Performance insights
            overall_rate = summary_stats.get("overall_hit_rate", 0)
            if overall_rate >= 15:
                insights.append("🎯 Hiệu suất dự đoán xuất sắc! Tỷ lệ trúng trên 15%")
            elif overall_rate >= 10:
                insights.append("✅ Hiệu suất dự đoán tốt. Tỷ lệ trúng trên 10%")
            elif overall_rate >= 5:
                insights.append(
                    "⚠️ Hiệu suất dự đoán khá. Cần cải thiện để đạt trên 10%"
                )
            else:
                insights.append("❌ Hiệu suất dự đoán thấp. Cần điều chỉnh thuật toán")

            # Method comparison insights
            method_comparison = summary_stats.get("method_comparison", {})
            if method_comparison:
                best_method = max(
                    method_comparison.items(), key=lambda x: x[1]["hit_rate"]
                )
                worst_method = min(
                    method_comparison.items(), key=lambda x: x[1]["hit_rate"]
                )

                insights.append(
                    f"🏆 Phương pháp tốt nhất: {best_method[0]} ({best_method[1]['hit_rate']:.1f}%)"
                )
                insights.append(
                    f"📉 Phương pháp cần cải thiện: {worst_method[0]} ({worst_method[1]['hit_rate']:.1f}%)"
                )

            # Special prize insights
            giai_db_rate = summary_stats.get("giai_db_hit_rate", 0)
            if giai_db_rate >= 10:
                insights.append(
                    f"🎊 Tỷ lệ trúng giải đặc biệt cao: {giai_db_rate:.1f}%"
                )
            elif giai_db_rate >= 5:
                insights.append(
                    f"🎯 Tỷ lệ trúng giải đặc biệt khá: {giai_db_rate:.1f}%"
                )
            else:
                insights.append(
                    f"🎲 Tỷ lệ trúng giải đặc biệt thấp: {giai_db_rate:.1f}%"
                )

            # Generate recommendations
            if overall_rate < 10:
                recommendations.append(
                    "📈 Tăng trọng số cho phương pháp có hiệu suất cao nhất"
                )
                recommendations.append("🔄 Điều chỉnh tham số ML models")
                recommendations.append("📊 Thu thập thêm dữ liệu lịch sử")

            if giai_db_rate < 5:
                recommendations.append("🎯 Tập trung cải thiện dự đoán giải đặc biệt")
                recommendations.append("🔍 Phân tích pattern của giải đặc biệt")

            # Consistency insights
            best_rate = summary_stats.get("best_day_rate", 0)
            worst_rate = summary_stats.get("worst_day_rate", 0)
            if best_rate - worst_rate > 20:
                insights.append("📊 Hiệu suất không ổn định giữa các ngày")
                recommendations.append("⚖️ Cần cân bằng thuật toán để giảm biến động")

            return {"insights": insights, "recommendations": recommendations}

        except Exception as e:
            logger.error(f"Error generating insights: {e}")
            return {"insights": [], "recommendations": []}

    def _prepare_chart_data(self, daily_performances, method_performances):
        """Prepare data for charts"""
        try:
            # Daily performance chart
            daily_chart = {
                "dates": [day["date"].strftime("%d/%m") for day in daily_performances],
                "hit_rates": [
                    day.get("combined", {}).get("hit_rate", 0)
                    for day in daily_performances
                ],
                "quality_scores": [
                    day.get("quality_score", 0) for day in daily_performances
                ],
            }

            # Method comparison chart
            method_chart = {"methods": [], "hit_rates": []}

            for method, data in method_performances.items():
                if data["total_predictions"] > 0:
                    method_chart["methods"].append(method)
                    method_chart["hit_rates"].append(
                        data["hits"] / data["total_predictions"] * 100
                    )

            # Weekly trend (if enough data)
            weekly_chart = self._prepare_weekly_trend(daily_performances)

            return {
                "daily_performance": daily_chart,
                "method_comparison": method_chart,
                "weekly_trend": weekly_chart,
            }

        except Exception as e:
            logger.error(f"Error preparing chart data: {e}")
            return {}

    def _prepare_weekly_trend(self, daily_performances):
        """Prepare weekly trend data"""
        try:
            if len(daily_performances) < 7:
                return None

            # Group by week
            weeks = {}
            for day in daily_performances:
                week_start = day["date"] - timedelta(days=day["date"].weekday())
                week_key = week_start.strftime("%d/%m")

                if week_key not in weeks:
                    weeks[week_key] = {
                        "total_hits": 0,
                        "total_predictions": 0,
                        "days": 0,
                    }

                combined = day.get("combined", {})
                weeks[week_key]["total_hits"] += combined.get("hits", 0)
                weeks[week_key]["total_predictions"] += combined.get(
                    "total_predictions", 0
                )
                weeks[week_key]["days"] += 1

            # Calculate weekly rates
            weekly_data = {"weeks": list(weeks.keys()), "hit_rates": []}

            for week_data in weeks.values():
                if week_data["total_predictions"] > 0:
                    rate = (
                        week_data["total_hits"] / week_data["total_predictions"] * 100
                    )
                    weekly_data["hit_rates"].append(rate)
                else:
                    weekly_data["hit_rates"].append(0)

            return weekly_data

        except Exception as e:
            logger.error(f"Error preparing weekly trend: {e}")
            return None

    def _generate_daily_analysis(self, analysis_date, actual_result):
        """Generate analysis for a specific date (if not cached)"""
        try:
            # This would be a simplified version of the main analysis
            # For now, return None to skip missing data
            logger.warning(f"No analysis available for {analysis_date}")
            return None

        except Exception as e:
            logger.error(f"Error generating daily analysis for {analysis_date}: {e}")
            return None


class RefreshPredictionsView(View):
    def post(self, request):
        try:
            from django.core.management import call_command

            call_command("precompute", days=1)
            return JsonResponse(
                {"status": "success", "message": "Đã cập nhật dự đoán thành công"}
            )
        except Exception as e:
            return JsonResponse({"status": "error", "message": str(e)}, status=500)


from django.db.models import Count, QuerySet

from .analytics.predictors import BachThuLoPredictor
from .models import KetQuaXoSo, MethodPerformance, PredictionFeedback, PredictionResult


class BachThuLoView(TemplateView):
    template_name = "results/bach_thu_lo.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        try:
            # Date handling
            selected_date = self.request.GET.get("selected_date")
            current_date = timezone.now().date()
            history_days = self._get_validated_history_days()
            target_date = self._get_validated_target_date(selected_date, current_date)

            # Initialize predictor
            predictor = BachThuLoPredictor(
                target_date=target_date,
                history_days=history_days,
                selected_date=selected_date,
            )
            # Thêm danh sách các khoảng thời gian lịch sử
            history_periods = [30, 60, 90, 180]
            multi_history_predictions = {}

            for days in history_periods:
                predictor = BachThuLoPredictor(
                    target_date=target_date,
                    history_days=days,
                    selected_date=selected_date,
                )
                predictions = predictor.predict() or {}
                multi_history_predictions[days] = {
                    "predictions": self._process_predictions(predictions),
                }
            actual_numbers = self._get_actual_numbers(target_date)
            # Get predictions and historical data
            predictions = predictor.predict() or {}
            historical_analysis = self._get_historical_analysis(
                target_date, history_days
            )

            # Update context with processed data
            context.update(
                {
                    "selected_date": selected_date,
                    "actual_numbers": actual_numbers,
                    "target_date": target_date,
                    "history_days": history_days,
                    "multi_history_predictions": multi_history_predictions,
                    "history_periods": history_periods,
                    **self._process_predictions(predictions),
                    "historical_analysis": historical_analysis,
                    **self._get_statistical_analysis(
                        predictions, historical_analysis or {}
                    ),
                }
            )

        except Exception as e:
            logger.error(f"Error in get_context_data: {str(e)}", exc_info=True)
            messages.error(self.request, f"Error occurred: {str(e)}")
            context.update(self._get_default_context())

        return context

    def _format_predictions(self, predictions):
        """Format raw predictions and mark hits"""
        try:
            formatted = []
            actual_set = (
                set(self.actual_numbers) if hasattr(self, "actual_numbers") else set()
            )

            for num, conf in predictions:
                formatted.append(
                    {
                        "number": str(num).zfill(2),
                        "confidence": float(conf) * 100,
                        "is_hit": str(num).zfill(2) in actual_set,
                    }
                )

            return formatted
        except Exception as e:
            logger.error(f"Error formatting predictions: {e}")
            return []

    def _get_actual_numbers(self, selected_date):
        """Lấy kết quả thực tế cho ngày được chọn"""
        try:
            result = KetQuaXoSo.objects.filter(ngay=selected_date).first()
            return result.get_all_2digit_numbers() if result else []
        except Exception as e:
            logger.error(f"Lỗi khi lấy kết quả thực tế: {str(e)}")
            return []

    def _get_historical_analysis(self, target_date, history_days):
        """Get and analyze historical data"""
        try:
            start_date = target_date - timedelta(days=history_days)
            historical_data = KetQuaXoSo.objects.filter(
                ngay__range=(start_date, target_date)
            ).order_by("-ngay")

            if not historical_data:
                return None

            analysis = {
                "data": list(historical_data),
                "total_records": historical_data.count(),
                "date_range": {"start": start_date, "end": target_date},
                "number_stats": self._analyze_historical_numbers(historical_data),
            }

            return analysis
        except Exception as e:
            logger.error(f"Error in historical analysis: {e}")
            return None

    def _analyze_historical_numbers(self, queryset):
        """Analyze historical number patterns"""
        all_numbers = []
        number_freq = {}

        for result in queryset:
            numbers = result.get_all_2digit_numbers()
            all_numbers.extend(numbers)

            for num in numbers:
                number_freq[num] = number_freq.get(num, 0) + 1

        return {
            "frequency": number_freq,
            "total_numbers": len(all_numbers),
            "unique_numbers": len(set(all_numbers)),
            "most_common": sorted(
                number_freq.items(), key=lambda x: x[1], reverse=True
            )[:10],
        }

    def _get_default_context(self):
        """Return default context when errors occur"""
        return {
            "selected_date": timezone.now().date(),
            "target_date": timezone.now().date(),
            "history_days": 90,
            "final_predictions": [],
            "ml_predictions": [],
            "method_predictions": [],
            "feature_vector": {},
            "shap_analysis": {
                "values": [],
                "feature_names": [],
                "data": {},
                "base_value": 0,
                "plot_data": {"values": [], "names": []},
            },
            "statistics": {
                "accuracy_trend": [],
                "number_distribution": {},
                "pattern_strength": 0,
                "confidence_metrics": {},
            },
            "error": "An error occurred while processing the request",
        }

    def _get_validated_history_days(self):
        """Validate and return history days parameter"""
        try:
            history_days = int(self.request.GET.get("history_days", "90"))
            return min(max(history_days, 30), 365)
        except (ValueError, TypeError):
            return 90

    def _get_validated_target_date(self, selected_date, current_date):
        """Validate and return target date"""
        if not selected_date:
            return current_date

        try:
            target_date = datetime.strptime(selected_date, "%Y-%m-%d").date()
            return min(target_date, current_date)
        except ValueError:
            return current_date

    def _process_predictions(self, predictions):
        """Process all prediction types"""
        try:
            ml_analysis = predictions.get("ml_analysis", {})
            combined_data = predictions.get("combined_predictions", {})

            # Get actual numbers as a set for easy comparison
            actual_numbers = (
                set(self.actual_numbers) if hasattr(self, "actual_numbers") else set()
            )

            # Format final predictions
            final_predictions = [
                {
                    "number": str(num).zfill(2),
                    "confidence": float(conf) * 100,
                    "is_hit": str(num).zfill(2) in actual_numbers,
                }
                for num, conf in combined_data.get("recommended_numbers", [])
            ]

            # Format ML predictions
            ml_predictions = [
                {
                    "number": str(num).zfill(2),
                    "confidence": float(conf) * 100,
                    "is_hit": str(num).zfill(2) in actual_numbers,
                }
                for num, conf in ml_analysis.get("final_prediction", [])
            ]
            logger.debug(
                f"Prediction metrics: {self._calculate_prediction_metrics(predictions)}"
            )
            return {
                "final_predictions": final_predictions,
                "ml_predictions": ml_predictions,
                "method_predictions": self._format_method_predictions(predictions),
                "shap_analysis": self._format_shap_analysis(ml_analysis),
                "feature_vector": self._format_feature_vector(ml_analysis),
                "prediction_metrics": self._calculate_prediction_metrics(predictions),
            }
        except Exception as e:
            logger.error(f"Error processing predictions: {e}")
            return {
                "final_predictions": [],
                "ml_predictions": [],
                "method_predictions": [],
                "shap_analysis": {},
                "feature_vector": {},
                "prediction_metrics": {},
            }

    def _format_predictions(self, predictions):
        """Format raw predictions into template-ready format"""
        try:
            return (
                [
                    {
                        "number": str(num).zfill(2),
                        "confidence": float(conf) * 100,
                        "is_hit": False,
                    }
                    for num, conf in predictions
                ]
                if predictions
                else []
            )
        except Exception as e:
            logger.error(f"Error formatting predictions: {e}")
            return []

    def _format_method_predictions(self, predictions):
        """Format method-specific predictions"""
        try:
            combined_data = predictions.get("combined_predictions", {})
            method_weights = combined_data.get("method_weights", {})

            formatted = []
            for method, weight in method_weights.items():
                method_name = self._get_method_name_display(method)
                formatted.append(
                    {
                        "method": method_name,
                        "weight": weight * 100,
                        "confidence": weight * 100,  # Use weight as confidence for now
                        "numbers": self._get_method_numbers(predictions, method),
                    }
                )
            return formatted
        except Exception as e:
            logger.error(f"Error formatting method predictions: {e}")
            return []

    def _format_shap_analysis(self, ml_analysis):
        """Format SHAP analysis data for template"""
        try:
            shap_data = ml_analysis.get("shap_analysis", {})
            return {
                "values": shap_data.get("values", []),
                "feature_names": shap_data.get("feature_names", []),
                "data": shap_data.get("data", {}),
                "base_value": shap_data.get("base_value", 0),
                "plot_data": {
                    "values": self._calculate_shap_plot_values(shap_data),
                    "names": shap_data.get("feature_names", []),
                },
            }
        except Exception as e:
            logger.error(f"Error formatting SHAP analysis: {e}")
            return {}

    def _format_feature_vector(self, ml_analysis):
        """Format feature vector for template display"""
        try:
            feature_data = ml_analysis.get("shap_analysis", {}).get("data", {})
            return {
                "Thứ trong tuần": f"Thứ {feature_data.get('day_of_week', 0) + 1}",
                "Tháng": f"Tháng {feature_data.get('month', 0)}",
                "Ngày": feature_data.get("day", 0),
                "Tổng số": feature_data.get("total_numbers", 0),
                "Trung bình": f"{float(feature_data.get('mean_number', 0)):.2f}",
                "Độ lệch chuẩn": f"{float(feature_data.get('std_number', 0)):.2f}",
                "Số lẻ": feature_data.get("odd_count", 0),
                "Số chẵn": feature_data.get("even_count", 0),
            }
        except Exception as e:
            logger.error(f"Error formatting feature vector: {e}")
            return {}

    def _calculate_shap_plot_values(self, shap_data):
        """Calculate SHAP plot values"""
        try:
            values = shap_data.get("values", [])
            if not values:
                return []
            return [float(sum(x)) for x in zip(*values)]
        except Exception as e:
            logger.error(f"Error calculating SHAP plot values: {e}")
            return []

    def _get_method_name_display(self, method_key):
        """Convert method keys to display names"""
        method_names = {
            "recent": "Số gần đây",
            "frequency": "Tần suất",
            "pattern": "Mẫu số",
        }
        return method_names.get(method_key, method_key)

    def _get_method_numbers(self, predictions, method):
        """Get numbers for specific prediction method"""
        try:
            if method == "recent":
                return self._get_recent_numbers(predictions)
            elif method == "frequency":
                return self._get_frequency_numbers(predictions)
            elif method == "pattern":
                return self._get_pattern_numbers(predictions)
            return []
        except Exception as e:
            logger.error(f"Error getting method numbers: {e}")
            return []

    def _get_recent_numbers(self, predictions):
        """Extract recent numbers from predictions"""
        try:
            combined = predictions.get("combined_predictions", {})
            recommended = combined.get("recommended_numbers", [])
            return [num for num, _ in recommended[:5]]
        except Exception as e:
            logger.error(f"Error getting recent numbers: {e}")
            return []

    def _get_frequency_numbers(self, predictions):
        """Extract frequency-based numbers"""
        # Similar implementation as _get_recent_numbers
        return self._get_recent_numbers(predictions)

    def _get_pattern_numbers(self, predictions):
        """Extract pattern-based numbers"""
        # Similar implementation as _get_recent_numbers
        return self._get_recent_numbers(predictions)

    def _get_statistical_analysis(self, predictions, historical_data):
        """Generate statistical analysis of predictions and historical data"""
        return {
            "statistics": {
                "accuracy_trend": self._calculate_accuracy_trend(historical_data),
                "number_distribution": self._analyze_number_distribution(
                    historical_data
                ),
                "pattern_strength": self._calculate_pattern_strength(predictions),
                "confidence_metrics": self._calculate_confidence_metrics(predictions),
            }
        }

    def _calculate_prediction_metrics(self, predictions):
        """
        Calculate comprehensive prediction metrics including:
        - Overall confidence scores
        - Method reliability scores
        - Pattern strength indicators
        - Historical accuracy rates
        """
        try:
            # Get components from predictions
            ml_analysis = predictions.get("ml_analysis", {})
            combined_data = predictions.get("combined_predictions", {})

            # Calculate various metrics
            metrics = {
                "confidence_scores": self._calculate_confidence_scores(
                    ml_analysis, combined_data
                ),
                "method_reliability": self._calculate_method_reliability(combined_data),
                "pattern_indicators": self._calculate_pattern_indicators(predictions),
                "historical_accuracy": self._get_historical_accuracy(),
            }

            # Add overall metrics
            metrics.update(
                {
                    "overall_confidence": self._calculate_overall_confidence(metrics),
                    "prediction_stability": self._calculate_stability_score(metrics),
                    "recommendation_strength": self._calculate_recommendation_strength(
                        combined_data.get("recommended_numbers", [])
                    ),
                }
            )

            return metrics

        except Exception as e:
            logger.error(f"Error calculating prediction metrics: {e}")
            return {}

    def _calculate_confidence_scores(self, ml_analysis, combined_data):
        """Calculate confidence scores for different prediction methods"""
        try:
            scores = {
                "ml_confidence": self._get_ml_confidence(ml_analysis),
                "combined_confidence": self._get_combined_confidence(combined_data),
                "method_scores": {},
            }

            # Add method-specific scores
            if "method_weights" in combined_data:
                for method, weight in combined_data["method_weights"].items():
                    scores["method_scores"][method] = weight * 100

            return scores
        except Exception as e:
            logger.error(f"Error calculating confidence scores: {e}")
            return {}

    def _calculate_stability_score(self, metrics):
        """Calculate stability score based on prediction metrics"""
        try:
            confidence_scores = metrics.get("confidence_scores", {})
            method_reliability = metrics.get("method_reliability", {})

            if not confidence_scores and not method_reliability:
                return 0.0

            # Calculate stability based on method reliability variance
            reliability_values = (
                list(method_reliability.values()) if method_reliability else []
            )

            if len(reliability_values) > 1:
                mean_reliability = sum(reliability_values) / len(reliability_values)
                variance = sum(
                    (x - mean_reliability) ** 2 for x in reliability_values
                ) / len(reliability_values)
                # Convert variance to stability score (lower variance = higher stability)
                stability = max(0, 100 - (variance / 10))  # Normalize variance
            else:
                stability = 50.0  # Default stability for single value

            # Factor in ML confidence stability
            ml_conf = confidence_scores.get("ml_confidence", 0)
            combined_conf = confidence_scores.get("combined_confidence", 0)

            if ml_conf > 0 and combined_conf > 0:
                conf_diff = abs(ml_conf - combined_conf)
                conf_stability = max(0, 100 - conf_diff)
                stability = (stability + conf_stability) / 2

            return min(max(stability, 0), 100)

        except Exception as e:
            logger.error(f"Error calculating stability score: {e}")
            return 0.0

    def sigmoid(x):
        """Hàm sigmoid để chuẩn hóa giá trị"""
        return 1 / (1 + math.exp(-x))

    def _calculate_method_reliability(self, combined_data):
        """Calculate reliability scores for each prediction method"""
        try:
            reliability = {}
            weights = combined_data.get("method_weights", {})

            for method, weight in weights.items():
                # Calculate reliability based on weight and historical performance
                base_score = weight * 100
                historical_score = self._get_method_historical_score(method)
                reliability[method] = (base_score + historical_score) / 2

            return reliability
        except Exception as e:
            logger.error(f"Error calculating method reliability: {e}")
            return {}

    def _calculate_pattern_indicators(self, predictions):
        """Calculate pattern strength indicators"""
        try:
            return {
                "pattern_strength": self._get_pattern_strength(predictions),
                "pattern_consistency": self._get_pattern_consistency(predictions),
                "trend_indicators": self._get_trend_indicators(predictions),
            }
        except Exception as e:
            logger.error(f"Error calculating pattern indicators: {e}")
            return {}

    def _get_historical_accuracy(self):
        """Get historical accuracy rates"""
        try:
            # Get last 30 days of predictions and results
            end_date = timezone.now().date()
            start_date = end_date - timedelta(days=30)

            historical_results = KetQuaXoSo.objects.filter(
                ngay__range=(start_date, end_date)
            ).order_by("-ngay")

            accuracy_data = {
                "total_predictions": 0,
                "correct_predictions": 0,
                "accuracy_by_method": {},
                "trend": [],
            }

            return accuracy_data

        except Exception as e:
            logger.error(f"Error getting historical accuracy: {e}")
            return {}

    def calculate_trend_score(time_performance):
        """Tính điểm xu hướng dựa trên sự thay đổi hiệu suất theo thời gian"""
        # Lấy các khoảng thời gian và hiệu suất tương ứng
        periods = sorted(time_performance.keys())

        if len(periods) < 2:
            return 0.5  # Điểm trung bình nếu không đủ dữ liệu

        # Ưu tiên xu hướng gần đây hơn
        # Tính điểm cho từng cặp khoảng thời gian liên tiếp
        trend_points = []
        for i in range(len(periods) - 1):
            shorter_period = periods[i]
            longer_period = periods[i + 1]

            shorter_perf = time_performance[shorter_period]["hit_rate"]
            longer_perf = time_performance[longer_period]["hit_rate"]

            # Tính điểm xu hướng (tăng là tốt)
            diff = shorter_perf - longer_perf

            # Chuẩn hóa sự khác biệt và áp dụng hàm sigmoid để giảm ảnh hưởng của giá trị cực đoan
            normalized_diff = sigmoid(diff / 10)  # Chia cho 10 để giảm độ lớn

            # Gán trọng số cao hơn cho xu hướng gần đây
            weight = 2 ** (i + 1)
            trend_points.append((normalized_diff, weight))

        # Tính điểm xu hướng tổng hợp (weighted average)
        total_weight = sum(w for _, w in trend_points)
        trend_score = (
            sum(score * weight for score, weight in trend_points) / total_weight
            if total_weight
            else 0.5
        )

        return trend_score

    def sigmoid(x):
        """Hàm sigmoid để chuẩn hóa giá trị"""
        return 1 / (1 + math.exp(-x))

    def _calculate_overall_confidence(self, metrics):
        """Calculate overall confidence score"""
        try:
            confidence_scores = metrics.get("confidence_scores", {})
            method_reliability = metrics.get("method_reliability", {})

            if not confidence_scores or not method_reliability:
                return 0.0

            # Weight different factors
            ml_weight = 0.4
            combined_weight = 0.3
            reliability_weight = 0.3

            overall_score = (
                confidence_scores.get("ml_confidence", 0) * ml_weight
                + confidence_scores.get("combined_confidence", 0) * combined_weight
                + sum(method_reliability.values())
                / len(method_reliability)
                * reliability_weight
            )

            return min(max(overall_score, 0), 100)  # Ensure score is between 0 and 100

        except Exception as e:
            logger.error(f"Error calculating overall confidence: {e}")
            return 0.0

    def evaluate_context_fit(method, current_date, history_data):
        """Đánh giá độ phù hợp của phương pháp với ngày hiện tại"""
        # Xác định các đặc điểm của ngày hiện tại
        day_of_week = current_date.weekday()
        day_of_month = current_date.day

        # Lấy dữ liệu lịch sử cho ngày tương tự (cùng thứ trong tuần)
        similar_days = [
            entry
            for entry in history_data
            if datetime.strptime(entry["date"], "%Y-%m-%d").weekday() == day_of_week
        ]

        # Tính hiệu suất của phương pháp trong các ngày tương tự
        method_name = method["name"]
        hit_count = 0
        total_count = 0

        for day_data in similar_days:
            method_result = next(
                (
                    m
                    for m in day_data.get("methods", [])
                    if m.get("name") == method_name
                ),
                None,
            )
            if method_result:
                hit_count += method_result.get("hit_count", 0)
                total_count += method_result.get("prediction_count", 0) or 1

        # Tính điểm phù hợp với ngữ cảnh
        if total_count > 0:
            context_score = hit_count / total_count
        else:
            context_score = 0.5  # Điểm trung bình nếu không có dữ liệu

        return context_score

    def evaluate_cyclical_performance(method, history_data, current_date):
        """Đánh giá hiệu suất chu kỳ của phương pháp"""
        method_name = method["name"]
        date_perf = []

        # Thu thập dữ liệu hiệu suất theo ngày
        for entry in history_data:
            entry_date = datetime.strptime(entry["date"], "%Y-%m-%d")
            method_result = next(
                (m for m in entry.get("methods", []) if m.get("name") == method_name),
                None,
            )

            if method_result and method_result.get("prediction_count", 0) > 0:
                hit_rate = (
                    method_result.get("hit_count", 0)
                    / method_result.get("prediction_count", 1)
                    * 100
                )
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

    def rank_prediction_methods(
        methods_data, history_data, current_date, winning_numbers=None
    ):
        """
        Xếp hạng các phương pháp dự đoán dựa trên nhiều chỉ số

        Args:
            methods_data: Dữ liệu hiệu suất của các phương pháp
            history_data: Dữ liệu lịch sử
            current_date: Ngày hiện tại
            winning_numbers: Danh sách số trúng (nếu có)

        Returns:
            Danh sách phương pháp được xếp hạng
        """
        # Tạo bản sao để không làm thay đổi dữ liệu gốc
        methods = copy.deepcopy(methods_data)

        # Các khoảng thời gian phân tích
        time_periods = [7, 15, 30, 60, 90]

        for method in methods:
            # 1. Phân tích hiệu suất theo thời gian
            time_performance = {}
            for period in time_periods:
                perf = analyze_method_in_period(
                    method, history_data, current_date, period
                )
                time_performance[period] = perf

            # 2. Tính điểm ổn định (đánh giá độ nhất quán của phương pháp)
            stability_score = calculate_stability_score(time_performance)

            # 3. Tính điểm xu hướng (đánh giá xu hướng hiệu suất gần đây)
            trend_score = calculate_trend_score(time_performance)

            # 4. Đánh giá độ phù hợp với điều kiện hiện tại
            context_score = evaluate_context_fit(method, current_date, history_data)

            # 5. Tính điểm vòng quay (xem xét chu kỳ hiệu suất)
            cycle_score = evaluate_cyclical_performance(
                method, history_data, current_date
            )

            # 6. Tính điểm đa dạng (đánh giá sự đa dạng trong dự đoán)
            diversity_score = calculate_prediction_diversity(method)

            # 7. Tính điểm tổng hợp (với trọng số khác nhau cho từng thành phần)
            final_score = (
                0.25 * method["confidence_score"]  # Wilson score hiện tại
                + 0.20 * stability_score  # Độ ổn định
                + 0.20 * trend_score  # Xu hướng gần đây
                + 0.15 * context_score  # Phù hợp với ngữ cảnh
                + 0.10 * cycle_score  # Hiệu suất theo chu kỳ
                + 0.10 * diversity_score  # Đa dạng trong dự đoán
            )

            # Cập nhật điểm xếp hạng
            method["ranking_score"] = final_score
            method["stability_score"] = stability_score
            method["trend_score"] = trend_score
            method["context_score"] = context_score
            method["cycle_score"] = cycle_score
            method["diversity_score"] = diversity_score

            # Tính khả năng trúng cho ngày tiếp theo
            method["next_day_probability"] = predict_next_day_success(
                method, history_data, current_date
            )

        # Sắp xếp theo điểm xếp hạng
        return sorted(methods, key=lambda x: x["ranking_score"], reverse=True)

    def calculate_ensemble_diversity(candidate, selected_methods):
        """
        Tính độ đa dạng của một phương pháp ứng viên so với các phương pháp đã chọn
        """
        # Độ đa dạng về nhóm phương pháp
        group_diversity = (
            1.0
            if candidate["group"] not in [m["group"] for m in selected_methods]
            else 0.0
        )

        # Độ đa dạng về số dự đoán
        prediction_overlap = 0
        total_predictions = len(candidate["predicted_numbers"])

        if total_predictions > 0:
            # Tính tỷ lệ số dự đoán trùng lặp với các phương pháp đã chọn
            all_selected_predictions = []
            for method in selected_methods:
                all_selected_predictions.extend(method["predicted_numbers"])

            overlap_count = sum(
                1
                for num in candidate["predicted_numbers"]
                if num in all_selected_predictions
            )
            prediction_overlap = overlap_count / total_predictions

        # Độ đa dạng về dự đoán (1 - tỷ lệ trùng lặp)
        prediction_diversity = 1 - prediction_overlap

        # Độ đa dạng về đặc điểm hiệu suất
        performance_features = [
            candidate["hit_rate"],
            candidate["stability_score"],
            candidate["trend_score"],
        ]

        performance_diversity = 0
        if selected_methods:
            avg_distances = []
            for method in selected_methods:
                method_features = [
                    method["hit_rate"],
                    method.get("stability_score", 0.5),
                    method.get("trend_score", 0.5),
                ]

                # Tính khoảng cách Euclidean giữa các vector đặc trưng
                distance = (
                    sum(
                        (f1 - f2) ** 2
                        for f1, f2 in zip(performance_features, method_features)
                    )
                    ** 0.5
                )
                avg_distances.append(distance)

            # Chuẩn hóa khoảng cách trung bình
            performance_diversity = (
                sum(avg_distances) / len(avg_distances) / (3**0.5)
            )  # 3 là số chiều

        # Kết hợp các yếu tố đa dạng
        diversity_score = (
            0.4 * group_diversity
            + 0.4 * prediction_diversity
            + 0.2 * performance_diversity
        )

        return diversity_score

    def select_optimal_method_ensemble(ranked_methods, max_methods=5):
        """
        Chọn tập hợp phương pháp tối ưu, cân bằng giữa hiệu suất và đa dạng
        """
        if len(ranked_methods) <= max_methods:
            return ranked_methods

        # Bắt đầu với phương pháp tốt nhất
        selected_methods = [ranked_methods[0]]
        remaining_methods = ranked_methods[1:]

        # Thêm lần lượt các phương pháp, ưu tiên sự đa dạng
        while len(selected_methods) < max_methods and remaining_methods:
            # Tính điểm đa dạng cho từng phương pháp còn lại
            diversity_scores = []

            for candidate in remaining_methods:
                diversity = calculate_ensemble_diversity(candidate, selected_methods)
                # Kết hợp điểm đa dạng với điểm xếp hạng gốc
                combined_score = 0.7 * candidate["ranking_score"] + 0.3 * diversity
                diversity_scores.append((candidate, combined_score))

            # Chọn phương pháp có điểm kết hợp cao nhất
            best_candidate, _ = max(diversity_scores, key=lambda x: x[1])

            # Thêm vào danh sách đã chọn
            selected_methods.append(best_candidate)
            remaining_methods.remove(best_candidate)

        return selected_methods

    def predict_next_day_success(method, history_data, current_date, model=None):
        """
        Dự đoán khả năng thành công cho ngày tiếp theo sử dụng mô hình học máy
        """
        # Nếu không có mô hình được cung cấp, tạo mô hình mới
        if model is None:
            model = train_prediction_model(history_data)

        # Chuẩn bị đặc trưng cho dự đoán
        features = extract_prediction_features(method, history_data, current_date)

        # Dự đoán xác suất thành công
        success_prob = model.predict_proba([features])[0][
            1
        ]  # Giả sử là mô hình phân loại nhị phân

        return success_prob

    def calculate_stability_score(time_performance):
        """Tính điểm ổn định dựa trên độ dao động của hiệu suất"""
        # Lấy các hiệu suất theo thời gian
        performances = [perf["hit_rate"] for perf in time_performance.values()]

        if not performances:
            return 0

        # Tính độ lệch chuẩn (càng thấp càng ổn định)
        std_dev = np.std(performances) if len(performances) > 1 else 0

        # Chuyển đổi thành điểm ổn định (1 - độ lệch chuẩn được chuẩn hóa)
        # Chuẩn hóa để có giá trị từ 0-1
        max_std = 100  # Giả sử hit_rate từ 0-100%
        normalized_std = min(std_dev / max_std, 1)

        return 1 - normalized_std

    def _calculate_recommendation_strength(self, recommended_numbers):
        """Calculate strength of recommendations"""
        try:
            if not recommended_numbers:
                return 0.0

            # Calculate average confidence
            confidences = [conf for _, conf in recommended_numbers]
            return sum(confidences) / len(confidences) * 100

        except Exception as e:
            logger.error(f"Error calculating recommendation strength: {e}")
            return 0.0

    def _calculate_shap_plot_values(self, shap_data):
        """Calculate SHAP plot values with proper type handling"""
        try:
            values = shap_data.get("values", [])
            if not values or not isinstance(values, list):
                return []

            # Initialize sum array
            result = [0.0] * len(values[0])

            # Sum values across all features
            for feature_values in values:
                for i, value in enumerate(feature_values):
                    result[i] += float(value)

            return result
        except Exception as e:
            logger.error(f"Error calculating SHAP plot values: {e}")
            return []

    def _get_ml_confidence(self, ml_analysis):
        """Calculate ML confidence score"""
        try:
            predictions = ml_analysis.get("final_prediction", [])
            if not predictions:
                return 0.0

            # Average confidence from ML predictions
            confidences = [float(conf) for _, conf in predictions]
            return sum(confidences) / len(confidences) * 100

        except Exception as e:
            logger.error(f"Error calculating ML confidence: {e}")
            return 0.0

    def _get_combined_confidence(self, combined_data):
        """Calculate combined prediction confidence"""
        try:
            recommended = combined_data.get("recommended_numbers", [])
            if not recommended:
                return 0.0

            # Average confidence from recommended numbers
            confidences = [float(conf) for _, conf in recommended]
            return sum(confidences) / len(confidences) * 100

        except Exception as e:
            logger.error(f"Error calculating combined confidence: {e}")
            return 0.0

    def _get_method_historical_score(self, method):
        """Calculate historical accuracy score for a method"""
        try:
            # Get last 30 days of results
            end_date = timezone.now().date()
            start_date = end_date - timedelta(days=30)

            results = KetQuaXoSo.objects.filter(
                ngay__range=(start_date, end_date)
            ).order_by("-ngay")

            # Default base scores for methods
            base_scores = {"recent": 75.0, "frequency": 70.0, "pattern": 65.0}

            # Add historical performance adjustment
            adjustment = self._calculate_method_adjustment(method, results)

            return min(max(base_scores.get(method, 60.0) + adjustment, 0), 100)

        except Exception as e:
            logger.error(f"Error calculating method historical score: {e}")
            return 60.0  # Default score

    def _calculate_method_adjustment(self, method, results):
        """Calculate performance adjustment based on historical data"""
        try:
            if not results:
                return 0.0

            # Basic adjustment based on result patterns
            if method == "recent":
                return self._calculate_recent_adjustment(results)
            elif method == "frequency":
                return self._calculate_frequency_adjustment(results)
            elif method == "pattern":
                return self._calculate_pattern_adjustment(results)

            return 0.0

        except Exception as e:
            logger.error(f"Error calculating method adjustment: {e}")
            return 0.0

    def _get_pattern_strength(self, predictions):
        """Calculate pattern strength indicator"""
        try:
            ml_analysis = predictions.get("ml_analysis", {})
            combined_data = predictions.get("combined_predictions", {})

            factors = [
                self._get_ml_confidence(ml_analysis) / 100,
                self._get_combined_confidence(combined_data) / 100,
                len(combined_data.get("recommended_numbers", [])) / 5,
            ]

            return sum(factors) / len(factors) * 100

        except Exception as e:
            logger.error(f"Error calculating pattern strength: {e}")
            return 0.0

    def _get_pattern_consistency(self, predictions):
        """Calculate pattern consistency score"""
        try:
            combined_data = predictions.get("combined_predictions", {})
            recommended = combined_data.get("recommended_numbers", [])

            if not recommended:
                return 0.0

            # Calculate variance in confidence scores
            confidences = [float(conf) for _, conf in recommended]
            mean_conf = sum(confidences) / len(confidences)
            variance = sum((x - mean_conf) ** 2 for x in confidences) / len(confidences)

            # Convert variance to consistency score (lower variance = higher consistency)
            consistency = max(0, 100 - (variance * 100))

            return consistency

        except Exception as e:
            logger.error(f"Error calculating pattern consistency: {e}")
            return 0.0

    def _get_trend_indicators(self, predictions):
        """Calculate trend indicators"""
        try:
            combined_data = predictions.get("combined_predictions", {})
            recommended = combined_data.get("recommended_numbers", [])

            return {
                "trend_strength": self._calculate_trend_strength(recommended),
                "trend_direction": self._calculate_trend_direction(recommended),
                "trend_stability": self._calculate_trend_stability(recommended),
            }

        except Exception as e:
            logger.error(f"Error calculating trend indicators: {e}")
            return {}

    def _calculate_recent_adjustment(self, results):
        """Calculate adjustment for recent numbers method"""
        try:
            if len(results) < 2:
                return 0.0

            recent_hits = sum(
                1
                for i in range(len(results) - 1)
                if self._check_number_overlap(results[i], results[i + 1])
            )

            return (recent_hits / (len(results) - 1)) * 20 - 10  # -10 to +10 adjustment

        except Exception as e:
            logger.error(f"Error calculating recent adjustment: {e}")
            return 0.0

    def _calculate_frequency_adjustment(self, results):
        """Calculate adjustment for frequency method"""
        try:
            if not results:
                return 0.0

            all_numbers = []
            for result in results:
                all_numbers.extend(result.get_all_2digit_numbers())

            # Calculate frequency distribution
            number_freq = {}
            for num in all_numbers:
                number_freq[num] = number_freq.get(num, 0) + 1

            # Calculate frequency stability
            mean_freq = sum(number_freq.values()) / len(number_freq)
            variance = sum((x - mean_freq) ** 2 for x in number_freq.values()) / len(
                number_freq
            )

            # Convert to adjustment (-15 to +15)
            return max(-15, min(15, 15 - (variance / mean_freq) * 15))

        except Exception as e:
            logger.error(f"Error calculating frequency adjustment: {e}")
            return 0.0

    def _calculate_pattern_adjustment(self, results):
        """Calculate adjustment for pattern method"""
        try:
            if len(results) < 3:
                return 0.0

            pattern_strength = self._calculate_pattern_correlation(results)
            return pattern_strength * 25 - 12.5  # -12.5 to +12.5 adjustment

        except Exception as e:
            logger.error(f"Error calculating pattern adjustment: {e}")
            return 0.0

    def _check_number_overlap(self, result1, result2):
        """Check if there are overlapping numbers between two results"""
        try:
            numbers1 = set(result1.get_all_2digit_numbers())
            numbers2 = set(result2.get_all_2digit_numbers())
            return bool(numbers1 & numbers2)
        except Exception as e:
            logger.error(f"Error checking number overlap: {e}")
            return False

    def _calculate_pattern_correlation(self, results):
        """Calculate pattern correlation strength"""
        try:
            if len(results) < 3:
                return 0.0

            correlations = []
            for i in range(len(results) - 2):
                correlation = self._calculate_triple_correlation(
                    results[i], results[i + 1], results[i + 2]
                )
                correlations.append(correlation)

            return sum(correlations) / len(correlations)

        except Exception as e:
            logger.error(f"Error calculating pattern correlation: {e}")
            return 0.0

    def _calculate_triple_correlation(self, result1, result2, result3):
        """Calculate correlation between three consecutive results"""
        try:
            numbers1 = set(result1.get_all_2digit_numbers())
            numbers2 = set(result2.get_all_2digit_numbers())
            numbers3 = set(result3.get_all_2digit_numbers())

            overlap12 = len(numbers1 & numbers2)
            overlap23 = len(numbers2 & numbers3)

            return (overlap12 + overlap23) / (len(numbers1) + len(numbers2))

        except Exception as e:
            logger.error(f"Error calculating triple correlation: {e}")
            return 0.0

    def _calculate_shap_plot_values(self, shap_data):
        """Calculate SHAP plot values with proper numeric handling"""
        try:
            values = shap_data.get("values", [])
            if not values or not isinstance(values, list):
                return []

            result = []
            for feature_values in zip(*values):  # Transpose the matrix
                feature_sum = sum(
                    float(val) if isinstance(val, (int, float)) else 0.0
                    for val in feature_values
                )
                result.append(feature_sum)

            return result
        except Exception as e:
            logger.error(f"Error calculating SHAP plot values: {e}")
            return []

    def _calculate_trend_strength(self, recommended):
        """Calculate the strength of number trends"""
        try:
            if not recommended:
                return 0.0

            # Get confidence values
            confidences = [float(conf) for _, conf in recommended]

            # Calculate trend strength based on confidence distribution
            mean_conf = sum(confidences) / len(confidences)
            max_conf = max(confidences)
            min_conf = min(confidences)

            # Stronger trend = less variance in confidences
            variance = sum((x - mean_conf) ** 2 for x in confidences) / len(confidences)
            strength = (1 - (variance / (max_conf**2))) * 100

            return max(0.0, min(100.0, strength))
        except Exception as e:
            logger.error(f"Error calculating trend strength: {e}")
            return 0.0

    def _calculate_trend_direction(self, recommended):
        """Calculate the direction of number trends"""
        try:
            if not recommended:
                return "neutral"

            # Convert numbers to integers for comparison
            numbers = [int(num) for num, _ in recommended]

            # Calculate average difference between consecutive numbers
            diffs = [numbers[i + 1] - numbers[i] for i in range(len(numbers) - 1)]
            avg_diff = sum(diffs) / len(diffs) if diffs else 0

            # Determine trend direction
            if avg_diff > 1:
                return "increasing"
            elif avg_diff < -1:
                return "decreasing"
            else:
                return "stable"
        except Exception as e:
            logger.error(f"Error calculating trend direction: {e}")
            return "neutral"

    def _calculate_trend_stability(self, recommended):
        """Calculate the stability of number trends"""
        try:
            if not recommended:
                return 0.0

            # Get numbers and confidences
            numbers = [int(num) for num, _ in recommended]
            confidences = [float(conf) for _, conf in recommended]

            if len(numbers) < 2:
                return 50.0  # Neutral stability for single number

            # Calculate number gaps
            number_gaps = [
                abs(numbers[i + 1] - numbers[i]) for i in range(len(numbers) - 1)
            ]
            avg_gap = sum(number_gaps) / len(number_gaps)

            # Calculate confidence stability
            conf_stability = 1 - (max(confidences) - min(confidences))

            # Combine factors (smaller gaps and more stable confidences = higher stability)
            gap_factor = max(0, 1 - (avg_gap / 50))  # Normalize gaps
            stability = (gap_factor * 0.6 + conf_stability * 0.4) * 100

            return max(0.0, min(100.0, stability))
        except Exception as e:
            logger.error(f"Error calculating trend stability: {e}")
            return 0.0

    def _calculate_accuracy_trend(self, historical_data):
        """Calculate accuracy trend over time"""
        # Implementation for accuracy trend analysis
        pass

    def _analyze_number_distribution(self, historical_data):
        """Analyze number distribution patterns"""
        # Implementation for number distribution analysis
        pass

    def _calculate_pattern_strength(self, predictions):
        """Calculate strength of detected patterns"""
        # Implementation for pattern strength calculation
        pass

    def _calculate_confidence_metrics(self, predictions):
        """Calculate confidence metrics for predictions"""
        # Implementation for confidence metrics
        pass


from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator


def lokhung2ngay(request):
    # Lấy tất cả dữ liệu sắp xếp từ mới đến cũ (không giới hạn ngày)
    lokhung_data = LoKhung2Ngay.objects.all().order_by("-analysis_date")

    # Phân trang - 30 item mỗi trang
    paginator = Paginator(lokhung_data, 30)
    page_number = request.GET.get("page")

    try:
        page_obj = paginator.get_page(page_number)
    except PageNotAnInteger:
        # Nếu page không phải số, trả về trang đầu
        page_obj = paginator.page(1)
    except EmptyPage:
        # Nếu page vượt quá số trang, trả về trang cuối
        page_obj = paginator.page(paginator.num_pages)

    # Tính toán thống kê TRÊN TOÀN BỘ DỮ LIỆU (không chỉ 30 ngày gần nhất)
    total_count = lokhung_data.count()
    winning_count = lokhung_data.filter(trung=True).count()
    win_rate = round((winning_count / total_count * 100)) if total_count > 0 else 0

    context = {
        "page_obj": page_obj,  # Dữ liệu phân trang
        "win_rate": win_rate,  # Tỷ lệ trúng tổng
        "winning_count": winning_count,
        "total_count": total_count,
        # Bỏ start_date và end_date vì không còn giới hạn 30 ngày
    }
    return render(request, "results/lokhung2ngay.html", context)


from django.db.models import Case, Count, F, FloatField, Q, Sum, Value, When
from django.db.models.functions import TruncMonth, TruncYear
from django.shortcuts import render

from results.models import DanDeDacBiet, PredictionMethod, PredictionResult


def analyze_numbers_for_day(predicted_numbers_list):
    """Phân tích các số dự đoán trong một ngày"""
    single_number_counts = defaultdict(int)
    two_number_counts = defaultdict(int)
    three_number_counts = defaultdict(int)

    # Tổng hợp tất cả số dự đoán từ các phương pháp trong ngày
    all_numbers = []
    for numbers in predicted_numbers_list:
        if numbers:
            all_numbers.extend(numbers)

    # Đếm từng số riêng lẻ
    for num in all_numbers:
        single_number_counts[num] += 1

    # Tạo các cặp 2 số liên tiếp
    sorted_numbers = sorted(all_numbers)
    for i in range(len(sorted_numbers) - 1):
        pair = tuple(sorted_numbers[i : i + 2])
        two_number_counts[pair] += 1

    # Tạo các cụm 3 số liên tiếp
    for i in range(len(sorted_numbers) - 2):
        triplet = tuple(sorted_numbers[i : i + 3])
        three_number_counts[triplet] += 1

    # Sắp xếp kết quả theo tần suất giảm dần
    sorted_single = sorted(
        single_number_counts.items(), key=lambda x: x[1], reverse=True
    )
    sorted_pairs = sorted(two_number_counts.items(), key=lambda x: x[1], reverse=True)
    sorted_triplets = sorted(
        three_number_counts.items(), key=lambda x: x[1], reverse=True
    )

    return {
        "single_numbers": sorted_single,
        "two_number_pairs": sorted_pairs,
        "three_number_groups": sorted_triplets,
        "total_numbers": len(all_numbers),
        "unique_numbers": len(single_number_counts),
    }


import calendar


def monthly_report_view(request):
    """
    Hiển thị báo cáo dự đoán theo tháng, với phương pháp theo hàng dọc và ngày theo hàng ngang.
    Bổ sung thêm thống kê số xuất hiện nhiều và gợi ý số dựa trên lịch sử.
    """
    try:
        # Lấy tham số từ URL
        year = request.GET.get("year")
        month = request.GET.get("month")
        selected_day = request.GET.get("day")

        # Nếu không có năm/tháng, sử dụng tháng hiện tại
        today = timezone.now().date()
        year = int(year) if year and year.isdigit() else today.year
        month = int(month) if month and month.isdigit() else today.month

        # Tạo ngày đầu tiên và cuối cùng của tháng
        first_day = date(year, month, 1)
        _, num_days = calendar.monthrange(year, month)
        last_day = date(year, month, num_days)

        # Tạo danh sách các ngày trong tháng
        days_in_month = [date(year, month, day) for day in range(1, num_days + 1)]

        # Xử lý ngày được chọn (nếu có)
        if selected_day and selected_day.isdigit():
            selected_day = int(selected_day)
            if 1 <= selected_day <= num_days:
                selected_date = date(year, month, selected_day)
            else:
                selected_date = (
                    today if today.month == month and today.year == year else first_day
                )
        else:
            selected_date = (
                today if today.month == month and today.year == year else first_day
            )

        # Lấy tháng trước và tháng sau để điều hướng
        if month == 1:
            prev_month = date(year - 1, 12, 1)
        else:
            prev_month = date(year, month - 1, 1)

        if month == 12:
            next_month = date(year + 1, 1, 1)
        else:
            next_month = date(year, month + 1, 1)

        # Lấy tất cả các phương pháp dự đoán
        methods = PredictionMethod.objects.filter(is_active=True).order_by("name")

        # Lấy tất cả các dự đoán trong tháng này
        predictions = PredictionResult.objects.filter(
            dan_de__analysis_date__gte=first_day, dan_de__analysis_date__lte=last_day
        ).select_related("dan_de", "method")

        # Tạo cấu trúc dữ liệu cho báo cáo
        report_data = {}
        method_totals = {
            method.id: {"hits": 0, "total": 0, "name": method.name, "code": method.code}
            for method in methods
        }
        day_totals = {day: {"hits": 0, "total": 0} for day in days_in_month}

        # Thống kê số xuất hiện nhiều
        two_digit_numbers = {}
        three_digit_numbers = {}

        # Xử lý từng dự đoán
        for prediction in predictions:
            method_id = prediction.method_id
            prediction_date = prediction.dan_de.analysis_date
            hit_count = prediction.hit_count
            predicted_numbers = (
                prediction.predicted_numbers if prediction.predicted_numbers else []
            )
            total_predictions = len(predicted_numbers)

            # Bỏ qua nếu không có dự đoán
            if total_predictions == 0:
                continue

            # Tính tỷ lệ trúng
            hit_rate = (
                (hit_count / total_predictions * 100) if total_predictions > 0 else 0
            )

            # Khởi tạo cấu trúc dữ liệu nếu cần
            if method_id not in report_data:
                report_data[method_id] = {}

            # Lưu dữ liệu dự đoán
            report_data[method_id][prediction_date] = {
                "hit_count": hit_count,
                "total_count": total_predictions,
                "hit_rate": hit_rate,
                "is_hit": hit_count > 0,
                "predicted_numbers": predicted_numbers,
                "winning_numbers": prediction.winning_numbers,
                "next_day_date": prediction.dan_de.next_day_date,
                "special_prize_next_day": prediction.dan_de.special_prize_next_day,
            }

            # Cập nhật tổng số liệu
            method_totals[method_id]["hits"] += hit_count
            method_totals[method_id]["total"] += 1

            if prediction_date in day_totals:
                day_totals[prediction_date]["hits"] += 1 if hit_count > 0 else 0
                day_totals[prediction_date]["total"] += 1

            # Thống kê số xuất hiện nhiều
            for number in predicted_numbers:
                number = str(number).strip()
                if len(number) == 2:
                    two_digit_numbers[number] = two_digit_numbers.get(number, 0) + 1
                elif len(number) == 3:
                    three_digit_numbers[number] = three_digit_numbers.get(number, 0) + 1

        # Thống kê dự đoán đặc biệt
        special_stats = (
            PredictionResult.objects.filter(is_special_prize=True)
            .values("method__name")
            .annotate(
                total_predictions=Count("id"),
                total_hits=Sum("hit_count", default=0),
                success_rate=Case(
                    When(
                        total_predictions__gt=0,
                        then=100.0
                        * Sum("hit_count", default=0)
                        / F("total_predictions"),
                    ),
                    default=Value(0.0),
                    output_field=FloatField(),
                ),
            )
            .order_by("-success_rate")
        )

        # Tạo dict ánh xạ từ method name sang success rate
        special_rates = {
            stat["method__name"]: stat["success_rate"] for stat in special_stats
        }

        # Sắp xếp methods theo success rate giảm dần
        sorted_methods = sorted(
            methods, key=lambda m: special_rates.get(m.name, 0), reverse=True
        )

        # Sắp xếp số theo tần suất xuất hiện
        sorted_two_digits = sorted(
            two_digit_numbers.items(), key=lambda x: x[1], reverse=True
        )[:20]
        sorted_three_digits = sorted(
            three_digit_numbers.items(), key=lambda x: x[1], reverse=True
        )[:20]

        # Tính tỉ lệ trúng lịch sử cho các số top (60 ngày trước)
        historical_hit_rates = {}
        history_end_date = selected_date - timedelta(days=1)
        history_start_date = history_end_date - timedelta(days=60)
        historical_results = KetQuaXoSo.objects.filter(
            ngay__range=(history_start_date, history_end_date)
        ).order_by("-ngay")

        for number, freq in sorted_two_digits + sorted_three_digits:
            hits = 0
            for result in historical_results:
                # Thay vì sử dụng result.winning_numbers, sử dụng các trường giải thưởng
                result_numbers = []

                # Thêm các số từ tất cả các giải
                for field in [
                    "giai_db",
                    "giai_1",
                    "giai_2",
                    "giai_3",
                    "giai_4",
                    "giai_5",
                    "giai_6",
                    "giai_7",
                ]:
                    value = getattr(result, field, "")
                    if value:
                        # Tách chuỗi nếu có nhiều số trong một giải
                        numbers = value.split() if " " in value else [value]
                        for num in numbers:
                            # Lấy 2 hoặc 3 số cuối tùy vào độ dài của số đang xét
                            if len(number) == 2:  # Nếu đang kiểm tra số 2 chữ số
                                if len(num) > 2:
                                    num = num[-2:]  # Lấy 2 số cuối
                            elif len(number) == 3:  # Nếu đang kiểm tra số 3 chữ số
                                if len(num) > 3:
                                    num = num[-3:]  # Lấy 3 số cuối
                            result_numbers.append(num)

                if number in result_numbers:
                    hits += 1

            hit_rate = (
                (hits / historical_results.count() * 100)
                if historical_results.count() > 0
                else 0
            )
            historical_hit_rates[number] = {
                "hits": hits,
                "total": historical_results.count(),
                "rate": hit_rate,
            }

        # Tạo gợi ý số nên đánh
        suggested_numbers = []
        for number, freq in sorted_two_digits + sorted_three_digits:
            if number in historical_hit_rates:
                hit_info = historical_hit_rates[number]
                score = freq * hit_info["rate"] / 100
                suggested_numbers.append(
                    {
                        "number": number,
                        "frequency": freq,
                        "hit_rate": hit_info["rate"],
                        "score": score,
                    }
                )

        suggested_numbers.sort(key=lambda x: x["score"], reverse=True)
        top_suggestions = suggested_numbers[:10]

        # Lấy thông tin các dự đoán trong tháng
        dan_de_count = DanDeDacBiet.objects.filter(
            analysis_date__gte=first_day, analysis_date__lte=last_day
        ).count()

        # Lấy dự đoán cho ngày được chọn (nếu có)
        selected_day_predictions = {}
        if selected_date:
            selected_predictions = PredictionResult.objects.filter(
                dan_de__analysis_date=selected_date
            ).select_related("method")

            for prediction in selected_predictions:
                method_name = prediction.method.name
                if method_name not in selected_day_predictions:
                    selected_day_predictions[method_name] = []
                selected_day_predictions[method_name].extend(
                    prediction.predicted_numbers or []
                )

        context = {
            "year": year,
            "month": month,
            "month_name": calendar.month_name[month],
            "days_in_month": days_in_month,
            "selected_date": selected_date,
            "methods": sorted_methods,
            "report_data": report_data,
            "method_totals": method_totals,
            "day_totals": day_totals,
            "prev_month": prev_month,
            "next_month": next_month,
            "has_data": dan_de_count > 0,
            # Bổ sung từ hàm thứ 2
            "top_two_digits": sorted_two_digits,
            "top_three_digits": sorted_three_digits,
            "historical_hit_rates": historical_hit_rates,
            "top_suggestions": top_suggestions,
            "selected_day_predictions": selected_day_predictions,
        }

    except Exception as e:
        logger.error(f"Error in monthly report view: {str(e)}", exc_info=True)
        context = {"error": f"Lỗi khi tải báo cáo tháng: {str(e)}", "has_data": False}

    return render(request, "results/monthly_report.html", context)


def monthly_report_allprize_view(request):
    """
    Hiển thị báo cáo dự đoán theo tháng, với phương pháp theo hàng dọc và ngày theo hàng ngang.
    Bổ sung thêm thống kê số xuất hiện nhiều và gợi ý số dựa trên lịch sử.
    """
    try:
        # Lấy tham số từ URL
        year = request.GET.get("year")
        month = request.GET.get("month")
        selected_day = request.GET.get("day")

        # Nếu không có năm/tháng, sử dụng tháng hiện tại
        today = timezone.now().date()
        year = int(year) if year and year.isdigit() else today.year
        month = int(month) if month and month.isdigit() else today.month

        # Tạo ngày đầu tiên và cuối cùng của tháng
        first_day = date(year, month, 1)
        _, num_days = calendar.monthrange(year, month)
        last_day = date(year, month, num_days)

        # Tạo danh sách các ngày trong tháng
        days_in_month = [date(year, month, day) for day in range(1, num_days + 1)]

        # Xử lý ngày được chọn (nếu có)
        if selected_day and selected_day.isdigit():
            selected_day = int(selected_day)
            if 1 <= selected_day <= num_days:
                selected_date = date(year, month, selected_day)
            else:
                selected_date = (
                    today if today.month == month and today.year == year else first_day
                )
        else:
            selected_date = (
                today if today.month == month and today.year == year else first_day
            )

        # Lấy tháng trước và tháng sau để điều hướng
        if month == 1:
            prev_month = date(year - 1, 12, 1)
        else:
            prev_month = date(year, month - 1, 1)

        if month == 12:
            next_month = date(year + 1, 1, 1)
        else:
            next_month = date(year, month + 1, 1)

        # Lấy tất cả các phương pháp dự đoán
        methods = PredictionMethodAllPrize.objects.filter(is_active=True).order_by(
            "name"
        )

        # Lấy tất cả các dự đoán trong tháng này
        predictions = PredictionDeAllPrizeResult.objects.filter(
            dan_de__analysis_date__gte=first_day, dan_de__analysis_date__lte=last_day
        ).select_related("dan_de", "method")

        # Tạo cấu trúc dữ liệu cho báo cáo
        report_data = {}
        method_totals = {
            method.id: {"hits": 0, "total": 0, "name": method.name, "code": method.code}
            for method in methods
        }
        day_totals = {day: {"hits": 0, "total": 0} for day in days_in_month}

        # Thống kê số xuất hiện nhiều
        two_digit_numbers = {}
        three_digit_numbers = {}

        # Xử lý từng dự đoán
        for prediction in predictions:
            method_id = prediction.method_id
            prediction_date = prediction.dan_de.analysis_date
            hit_count = prediction.hit_count
            predicted_numbers = (
                prediction.predicted_numbers if prediction.predicted_numbers else []
            )
            total_predictions = len(predicted_numbers)

            # Bỏ qua nếu không có dự đoán
            if total_predictions == 0:
                continue

            # Tính tỷ lệ trúng
            hit_rate = (
                (hit_count / total_predictions * 100) if total_predictions > 0 else 0
            )

            # Khởi tạo cấu trúc dữ liệu nếu cần
            if method_id not in report_data:
                report_data[method_id] = {}

            # Lưu dữ liệu dự đoán
            report_data[method_id][prediction_date] = {
                "hit_count": hit_count,
                "total_count": total_predictions,
                "hit_rate": hit_rate,
                "is_hit": hit_count > 0,
                "predicted_numbers": predicted_numbers,
                "winning_numbers": prediction.winning_numbers,
                "next_day_date": prediction.dan_de.next_day_date,
                "special_prize_next_day": prediction.dan_de.special_prize_next_day,
            }

            # Cập nhật tổng số liệu
            method_totals[method_id]["hits"] += hit_count
            method_totals[method_id]["total"] += 1

            if prediction_date in day_totals:
                day_totals[prediction_date]["hits"] += 1 if hit_count > 0 else 0
                day_totals[prediction_date]["total"] += 1

            # Thống kê số xuất hiện nhiều
            for number in predicted_numbers:
                number = str(number).strip()
                if len(number) == 2:
                    two_digit_numbers[number] = two_digit_numbers.get(number, 0) + 1
                elif len(number) == 3:
                    three_digit_numbers[number] = three_digit_numbers.get(number, 0) + 1

        # Thống kê dự đoán đặc biệt
        special_stats = (
            PredictionDeAllPrizeResult.objects.filter(is_special_prize=True)
            .values("method__name")
            .annotate(
                total_predictions=Count("id"),
                total_hits=Sum("hit_count", default=0),
                success_rate=Case(
                    When(
                        total_predictions__gt=0,
                        then=100.0
                        * Sum("hit_count", default=0)
                        / F("total_predictions"),
                    ),
                    default=Value(0.0),
                    output_field=FloatField(),
                ),
            )
            .order_by("-success_rate")
        )

        # Tính toán thành công cho từng phương pháp
        method_counts = {}
        method_allprize_hits = {}

        for result in predictions:
            method_name = result.method.name
            if method_name not in method_counts:
                method_counts[method_name] = 0
            if method_name not in method_allprize_hits:
                method_allprize_hits[method_name] = 0

            method_counts[method_name] += 1
            method_allprize_hits[method_name] += result.hit_count

        # Tính toán tỷ lệ thành công
        all_prize_rates = {}
        for method in methods:
            total = method_counts.get(method.name, 0)
            hits = method_allprize_hits.get(method.name, 0)
            all_prize_rates[method.name] = (hits / total * 100) if total > 0 else 0

        # Sắp xếp methods theo success rate giảm dần
        sorted_methods = sorted(
            methods, key=lambda m: all_prize_rates.get(m.name, 0), reverse=True
        )

        # Sắp xếp số theo tần suất xuất hiện
        sorted_two_digits = sorted(
            two_digit_numbers.items(), key=lambda x: x[1], reverse=True
        )[:20]
        sorted_three_digits = sorted(
            three_digit_numbers.items(), key=lambda x: x[1], reverse=True
        )[:20]

        # Tính tỉ lệ trúng lịch sử cho các số top (60 ngày trước)
        historical_hit_rates = {}
        history_end_date = selected_date - timedelta(days=1)
        history_start_date = history_end_date - timedelta(days=60)
        historical_results = KetQuaXoSo.objects.filter(
            ngay__range=(history_start_date, history_end_date)
        ).order_by("-ngay")

        for number, freq in sorted_two_digits + sorted_three_digits:
            hits = 0
            for result in historical_results:
                # Thay vì sử dụng result.winning_numbers, sử dụng các trường giải thưởng
                result_numbers = []

                # Thêm các số từ tất cả các giải
                for field in [
                    "giai_db",
                    "giai_1",
                    "giai_2",
                    "giai_3",
                    "giai_4",
                    "giai_5",
                    "giai_6",
                    "giai_7",
                ]:
                    value = getattr(result, field, "")
                    if value:
                        # Tách chuỗi nếu có nhiều số trong một giải
                        numbers = value.split() if " " in value else [value]
                        for num in numbers:
                            # Lấy 2 hoặc 3 số cuối tùy vào độ dài của số đang xét
                            if len(number) == 2:  # Nếu đang kiểm tra số 2 chữ số
                                if len(num) > 2:
                                    num = num[-2:]  # Lấy 2 số cuối
                            elif len(number) == 3:  # Nếu đang kiểm tra số 3 chữ số
                                if len(num) > 3:
                                    num = num[-3:]  # Lấy 3 số cuối
                            result_numbers.append(num)

                if number in result_numbers:
                    hits += 1

            hit_rate = (
                (hits / historical_results.count() * 100)
                if historical_results.count() > 0
                else 0
            )
            historical_hit_rates[number] = {
                "hits": hits,
                "total": historical_results.count(),
                "rate": hit_rate,
            }

        # Tạo gợi ý số nên đánh
        suggested_numbers = []
        for number, freq in sorted_two_digits + sorted_three_digits:
            if number in historical_hit_rates:
                hit_info = historical_hit_rates[number]
                score = freq * hit_info["rate"] / 100
                suggested_numbers.append(
                    {
                        "number": number,
                        "frequency": freq,
                        "hit_rate": hit_info["rate"],
                        "score": score,
                    }
                )

        suggested_numbers.sort(key=lambda x: x["score"], reverse=True)
        top_suggestions = suggested_numbers[:10]

        # Lấy thông tin các dự đoán trong tháng
        dan_de_count = DanDeDacBiet.objects.filter(
            analysis_date__gte=first_day, analysis_date__lte=last_day
        ).count()

        # Lấy dự đoán cho ngày được chọn (nếu có)
        selected_day_predictions = {}
        if selected_date:
            selected_predictions = PredictionResult.objects.filter(
                dan_de__analysis_date=selected_date
            ).select_related("method")

            for prediction in selected_predictions:
                method_name = prediction.method.name
                if method_name not in selected_day_predictions:
                    selected_day_predictions[method_name] = []
                selected_day_predictions[method_name].extend(
                    prediction.predicted_numbers or []
                )

        context = {
            "year": year,
            "month": month,
            "month_name": calendar.month_name[month],
            "days_in_month": days_in_month,
            "selected_date": selected_date,
            "methods": sorted_methods,
            "report_data": report_data,
            "method_totals": method_totals,
            "day_totals": day_totals,
            "prev_month": prev_month,
            "next_month": next_month,
            "has_data": dan_de_count > 0,
            # Bổ sung từ hàm thứ 2
            "top_two_digits": sorted_two_digits,
            "top_three_digits": sorted_three_digits,
            "historical_hit_rates": historical_hit_rates,
            "top_suggestions": top_suggestions,
            "selected_day_predictions": selected_day_predictions,
        }

    except Exception as e:
        logger.error(f"Error in monthly report view: {str(e)}", exc_info=True)
        context = {"error": f"Lỗi khi tải báo cáo tháng: {str(e)}", "has_data": False}

    return render(request, "results/monthly_report_allprize.html", context)


@login_required
def daily_prediction_analysis_view(request):
    """
    View đã được refactor để sử dụng service layer
    """

    start_time = time.time()

    try:
        logger.info("Bắt đầu daily_prediction_analysis_view")
        # Lấy tham số ngày
        analysis_date_str = request.GET.get("date")
        logger.debug(f"analysis_date_str: {analysis_date_str}")
        if analysis_date_str:
            analysis_date = datetime.strptime(analysis_date_str, "%Y-%m-%d").date()
        else:
            analysis_date = date.today()
        logger.info(f"analysis_date: {analysis_date}")

        # Xử lý kết quả thực tế
        # next_day = analysis_date + timedelta(days=1)
        actual_result = KetQuaXoSo.objects.filter(ngay=analysis_date).first()
        actual_numbers = (
            set(actual_result.get_all_2digit_numbers()) if actual_result else set()
        )

        # Lấy danh sách ngày có dữ liệu (ví dụ: từ bảng BtlAnalytics)
        logger.info("Lấy available_dates từ BtlAnalytics")
        available_dates = list(
            BtlAnalytics.objects.order_by("-date").values_list("date", flat=True)
        )
        logger.debug(f"available_dates: {available_dates[:5]}...")

        # Log bắt đầu
        perf_logger.info(f"Starting daily analysis for {analysis_date}")

        # Initialize services
        logger.info("Import và khởi tạo service layer")
        from results.core.services.ensemble import (
            combine_strategies,
            get_historical_hits,
        )
        from results.core.services.strategies import AnalysisStrategiesService

        strategies_service = AnalysisStrategiesService()

        # Lấy dữ liệu lịch sử
        step_start = time.time()
        logger.info("Gọi get_historical_hits")
        history_data = get_historical_hits(analysis_date)
        logger.info(
            f"Historical data loaded in {time.time() - step_start:.2f}s, len={len(history_data) if history_data else 0}"
        )

        # Kết hợp các chiến lược
        step_start = time.time()
        logger.info("Gọi combine_strategies")
        recommendations = combine_strategies(analysis_date, history_data)
        logger.info(
            f"Strategies combined in {time.time() - step_start:.2f}s, len={len(recommendations) if recommendations else 0}"
        )

        # Phân tích chu kỳ
        step_start = time.time()
        logger.info("Gọi analyze_cycles")
        cycle_analysis = strategies_service.analyze_cycles(analysis_date, days_back=60)
        logger.info(f"Cycle analysis completed in {time.time() - step_start:.2f}s")

        # Phân tích khoảng cách
        step_start = time.time()
        logger.info("Gọi analyze_gaps")
        gap_analysis = strategies_service.analyze_gaps(analysis_date, days_back=60)
        logger.info(f"Gap analysis completed in {time.time() - step_start:.2f}s")

        # Khai thác pattern
        step_start = time.time()
        logger.info("Gọi mine_patterns")
        pattern_mining = strategies_service.mine_patterns(analysis_date, days_back=60)
        logger.info(f"Pattern mining completed in {time.time() - step_start:.2f}s")

        # Phân tích hiệu suất phương pháp
        step_start = time.time()
        logger.info("Gọi get_method_performance_analysis")
        method_performance_data = strategies_service.get_method_performance_analysis(
            analysis_date
        )
        method_performance = method_performance_data.get("methods", [])
        logger.info(
            f"Method performance analysis completed in {time.time() - step_start:.2f}s, len={len(method_performance)}"
        )

        # Lấy top 15 số khuyến nghị
        recommended_numbers = [r["number"] for r in recommendations[:15]]
        logger.debug(f"recommended_numbers: {recommended_numbers}")

        # Tính toán thống kê trúng số
        hit_statistics = {
            "total_recommended": len(recommended_numbers),
            "total_hits": 0,
            "hit_rate": 0,
            "hit_numbers": [],
            "miss_numbers": [],
        }

        if actual_numbers:
            for number in recommended_numbers:
                if number in actual_numbers:
                    hit_statistics["total_hits"] += 1
                    hit_statistics["hit_numbers"].append(number)
                else:
                    hit_statistics["miss_numbers"].append(number)

            if hit_statistics["total_recommended"] > 0:
                hit_statistics["hit_rate"] = (
                    hit_statistics["total_hits"] / hit_statistics["total_recommended"]
                ) * 100

        # Thông tin bổ sung cho template
        strategy_details = []
        for strategy_name in ["cycle", "frequency", "gap", "markov"]:
            strategy_numbers = []
            for rec in recommendations[:10]:
                if rec["strategies"].get(strategy_name, 0) > 0.1:
                    strategy_numbers.append(
                        {
                            "number": rec["number"],
                            "score": rec["strategies"][strategy_name],
                        }
                    )
            strategy_details.append(
                {"name": strategy_name.title(), "top_numbers": strategy_numbers[:5]}
            )
        logger.debug(f"strategy_details: {strategy_details}")

        # Lấy thống kê tổng quan
        logger.info("Lấy daily_analytics")
        daily_analytics = BtlAnalytics.objects.filter(date=analysis_date).first()

        # Tạo overview data
        overview = {
            "accuracy_rate": method_performance_data.get("average_accuracy", 0),
            "total_methods": method_performance_data.get("total_methods", 0),
            "best_ensemble_count": len(
                [m for m in method_performance if m.get("is_top_performer", False)]
            ),
            "last_updated": timezone.now(),
        }
        logger.debug(f"overview: {overview}")

        # Tạo ensemble strategies data
        ensemble_strategies = [
            {
                "name": "Frequency Strategy",
                "description": "Dựa trên tần suất xuất hiện của các số",
                "confidence": 75.5,
                "strategies": ["Frequency", "Historical"],
            },
            {
                "name": "Cycle Strategy",
                "description": "Phân tích chu kỳ xuất hiện",
                "confidence": 68.2,
                "strategies": ["FFT", "Autocorrelation"],
            },
            {
                "name": "Gap Strategy",
                "description": "Phân tích khoảng cách giữa các lần xuất hiện",
                "confidence": 72.8,
                "strategies": ["Gap Analysis", "Trend"],
            },
            {
                "name": "Pattern Strategy",
                "description": "Khai thác mẫu xuất hiện thường xuyên",
                "confidence": 65.4,
                "strategies": ["Pattern Mining", "Association"],
            },
        ]

        # Tính navigation dates
        prev_date = analysis_date - timedelta(days=1)
        next_date = analysis_date + timedelta(days=1)

        # Context cho template với tất cả dữ liệu cần thiết
        context = {
            "actual_numbers": actual_numbers,
            "actual_result": actual_result,  # Thêm để có thêm thông tin
            "hit_statistics": hit_statistics,
            "analysis_date": analysis_date,
            "current_date": analysis_date,
            "formatted_date": analysis_date.strftime("%d/%m/%Y"),
            "prev_date": prev_date,
            "next_date": next_date,
            "available_dates": available_dates,
            "overview": overview,
            "ensemble_strategies": ensemble_strategies,
            "cycle_analysis": cycle_analysis,
            "gap_analysis": gap_analysis,
            "pattern_mining": pattern_mining,
            "method_performance": method_performance,
            "recommended_numbers": recommended_numbers,
            "strategy_details": strategy_details,
            "daily_analytics": daily_analytics,
            "total_methods": len(history_data),
            "processing_time": time.time() - start_time,
            "has_data": bool(history_data),
        }

        logger.info("Render template daily_analysis.html")
        logger.info(f"Daily analysis completed in {time.time() - start_time:.2f}s")
        # Log số lượng phần tử và kích thước các biến lớn trong context
        logger.info(
            f"context actual_numbers: {len(actual_numbers) if actual_numbers else 0}"
        )
        logger.info(
            f"context recommended_numbers: {len(recommended_numbers) if recommended_numbers else 0}"
        )
        logger.info(
            f"context method_performance: {len(method_performance) if method_performance else 0}"
        )
        logger.info(
            f"context strategy_details: {len(strategy_details) if strategy_details else 0}"
        )
        logger.info(
            f"context available_dates: {len(available_dates) if available_dates else 0}"
        )
        logger.info(
            f"context ensemble_strategies: {len(ensemble_strategies) if ensemble_strategies else 0}"
        )
        logger.info(f"context hit_statistics: {hit_statistics}")
        logger.info(f"context overview: {overview}")
        logger.info(
            f"context cycle_analysis keys: {list(cycle_analysis.keys()) if cycle_analysis else 'None'}"
        )
        logger.info(
            f"context gap_analysis keys: {list(gap_analysis.keys()) if gap_analysis else 'None'}"
        )
        logger.info(
            f"context pattern_mining keys: {list(pattern_mining.keys()) if pattern_mining else 'None'}"
        )
        logger.info(f"context daily_analytics: {daily_analytics}")

        import json
        import sys

        # Ước lượng tổng kích thước context (không chính xác tuyệt đối)
        def get_size(obj):
            try:
                return sys.getsizeof(obj)
            except Exception:
                return 0

        total_context_size = sum(get_size(v) for v in context.values())
        logger.info(f"Total context size (bytes): {total_context_size}")

        return render(request, "results/daily_analysis.html", context)

    except Exception as e:
        logger.error(f"Error in daily_prediction_analysis_view: {e}", exc_info=True)
        # Fallback context in case of error
        return render(
            request,
            "results/daily_analysis.html",
            {
                "error": f"Lỗi khi phân tích: {str(e)}",
                "analysis_date": (
                    analysis_date if "analysis_date" in locals() else date.today()
                ),
                "current_date": (
                    analysis_date if "analysis_date" in locals() else date.today()
                ),
                "available_dates": [],
                "has_data": False,
                "cycle_analysis": {
                    "detected_cycles": [],
                    "labels": [],
                    "fft_data": [],
                    "autocorr_data": [],
                },
                "gap_analysis": {
                    "gap_statistics": [],
                    "distribution_labels": [],
                    "distribution_data": [],
                    "trend_labels": [],
                    "trend_data": [],
                },
                "pattern_mining": {"frequent_patterns": []},
                "method_performance": [],
                "overview": {
                    "accuracy_rate": 0,
                    "total_methods": 0,
                    "best_ensemble_count": 0,
                    "last_updated": timezone.now(),
                },
                "ensemble_strategies": [],
            },
        )


def monthly_report_btl_view(request):
    """
    Hiển thị báo cáo dự đoán BTL theo tháng, với phương pháp theo hàng dọc và ngày theo hàng ngang.
    """
    try:
        # Lấy tham số từ URL
        year = request.GET.get("year")
        month = request.GET.get("month")
        selected_day = request.GET.get("day")

        # Nếu không có năm/tháng, sử dụng tháng hiện tại
        today = timezone.now().date()
        year = int(year) if year and year.isdigit() else today.year
        month = int(month) if month and month.isdigit() else today.month

        # Tạo ngày đầu tiên và cuối cùng của tháng
        first_day = date(year, month, 1)
        _, num_days = calendar.monthrange(year, month)
        last_day = date(year, month, num_days)

        # Tạo danh sách các ngày trong tháng
        days_in_month = [date(year, month, day) for day in range(1, num_days + 1)]

        # Xử lý ngày được chọn (nếu có)
        if selected_day and selected_day.isdigit():
            selected_day = int(selected_day)
            if 1 <= selected_day <= num_days:
                selected_date = date(year, month, selected_day)
            else:
                selected_date = (
                    today if today.month == month and today.year == year else first_day
                )
        else:
            selected_date = (
                today if today.month == month and today.year == year else first_day
            )

        # Lấy tháng trước và tháng sau để điều hướng
        if month == 1:
            prev_month = date(year - 1, 12, 1)
        else:
            prev_month = date(year, month - 1, 1)

        if month == 12:
            next_month = date(year + 1, 1, 1)
        else:
            next_month = date(year, month + 1, 1)

        # Lấy tất cả các phương pháp dự đoán một lần
        methods = list(
            PredictionMethodBtl.objects.filter(is_active=True).order_by("name")
        )
        methods_dict = {method.id: method for method in methods}

        # 1. Tải tất cả DanBtl trong tháng
        dan_btl_entries = list(
            DanBtl.objects.filter(
                analysis_date__gte=first_day, analysis_date__lte=last_day
            ).order_by("analysis_date")
        )

        dan_btl_dict = {entry.id: entry for entry in dan_btl_entries}
        date_to_dan_btl = {entry.analysis_date: entry for entry in dan_btl_entries}

        # 2. Tải tất cả PredictionResultBtl cho các DanBtl đã lấy
        all_predictions = list(
            PredictionResultBtl.objects.filter(
                dan_btl__in=dan_btl_entries
            ).select_related("dan_btl", "method")
        )

        # Tổ chức dữ liệu để truy cập hiệu quả
        # Cấu trúc: {method_id: {date: prediction_data}}
        method_date_predictions = {}

        # Tạo cấu trúc dữ liệu cho báo cáo
        report_data = {}
        method_totals = {
            method.id: {
                "hits": 0,
                "total": 0,
                "predictions": 0,
                "name": method.name,
                "code": method.code,
            }
            for method in methods
        }
        day_totals = {day: {"hits": 0, "total": 0} for day in days_in_month}
        method_days_hit = {
            method.id: {"days_hit": set(), "total_days": len(dan_btl_entries)}
            for method in methods
        }

        # Thống kê số xuất hiện nhiều
        number_counts = Counter()

        # Thêm cấu trúc dữ liệu để lưu trữ hiệu suất
        method_performance = {
            method.id: {
                "id": method.id,
                "name": method.name,
                "total_predictions": 0,
                "total_hits": 0,
                "hit_rate": 0,
                "days_used": 0,
                "days_hit": 0,
                "days_hit_rate": 0,
            }
            for method in methods
        }

        # Tìm ngày mới nhất có dự đoán trong tháng
        latest_dan_btl = None
        latest_prediction_date = None
        if dan_btl_entries:
            latest_dan_btl = max(dan_btl_entries, key=lambda x: x.analysis_date)
            latest_prediction_date = latest_dan_btl.analysis_date

        # Lấy kết quả của ngày hôm sau (để đánh dấu số trúng)
        next_day_results = []
        next_day_all_numbers = []

        if latest_dan_btl and latest_dan_btl.next_day_date:
            # Lấy kết quả dạng chuỗi trực tiếp từ dan_btl
            prize_next_day = latest_dan_btl.prize_next_day

            # Kiểm tra xem có dự đoán nào trong ngày mới nhất có winning_numbers
            latest_day_predictions = [
                p
                for p in all_predictions
                if p.dan_btl.analysis_date == latest_prediction_date
            ]

            for pred in latest_day_predictions:
                if pred.winning_numbers:
                    next_day_results.extend(pred.winning_numbers)

            # Loại bỏ trùng lặp
            next_day_all_numbers = list(set(next_day_results))

        # Tổ chức dự đoán theo phương pháp và ngày
        method_to_predictions = {}
        latest_day_numbers = Counter()
        latest_day_predictions_by_method = {}

        for prediction in all_predictions:
            method_id = prediction.method_id
            day_date = prediction.dan_btl.analysis_date

            # Khởi tạo các cấu trúc dữ liệu nếu cần
            if method_id not in method_to_predictions:
                method_to_predictions[method_id] = []

            method_to_predictions[method_id].append(prediction)

            # Tạo cấu trúc dữ liệu báo cáo
            if method_id not in report_data:
                report_data[method_id] = {}

            # Lấy thông tin dự đoán
            hit_count = prediction.hit_count or 0
            predicted_numbers = prediction.predicted_numbers or []
            total_predictions = len(predicted_numbers)

            # Bỏ qua nếu không có dự đoán
            if total_predictions == 0:
                continue

            # Tính tỷ lệ trúng
            hit_rate = (
                (hit_count / total_predictions * 100) if total_predictions > 0 else 0
            )

            # Lưu dự đoán của ngày mới nhất cho mỗi phương pháp
            if day_date == latest_prediction_date:
                latest_day_numbers.update(predicted_numbers)

                # Lưu dự đoán của phương pháp vào dictionary
                if method_id not in latest_day_predictions_by_method:
                    latest_day_predictions_by_method[method_id] = {
                        "method_id": method_id,
                        "method_name": prediction.method.name,
                        "predictions": predicted_numbers,
                        "hit_count": hit_count,
                        "hit_rate": hit_rate,
                    }

            # Lưu dữ liệu dự đoán
            report_data[method_id][day_date] = {
                "hit_count": hit_count,
                "total_count": total_predictions,
                "hit_rate": hit_rate,
                "is_hit": hit_count > 0,
                "predicted_numbers": predicted_numbers,
                "winning_numbers": prediction.winning_numbers or [],
                "next_day_date": prediction.dan_btl.next_day_date,
                "prize_next_day": prediction.dan_btl.prize_next_day,
            }

            # Cập nhật thống kê cho phương pháp
            method_totals[method_id]["hits"] += hit_count
            method_totals[method_id]["total"] += 1
            method_totals[method_id]["predictions"] += total_predictions

            # Cập nhật tổng số cho hiệu suất phương pháp
            method_performance[method_id]["total_predictions"] += total_predictions
            method_performance[method_id]["total_hits"] += hit_count
            method_performance[method_id]["days_used"] += 1

            # Cập nhật ngày có ít nhất một số trúng
            if hit_count > 0:
                method_days_hit[method_id]["days_hit"].add(day_date)
                method_performance[method_id]["days_hit"] += 1

            # Cập nhật thống kê theo ngày
            if day_date in day_totals:
                day_totals[day_date]["hits"] += 1 if hit_count > 0 else 0
                day_totals[day_date]["total"] += 1

            # Thống kê số xuất hiện nhiều trong toàn bộ tháng
            number_counts.update(predicted_numbers)

            # Thống kê số xuất hiện nhiều trong ngày mới nhất
            if day_date == latest_prediction_date:
                latest_day_numbers.update(predicted_numbers)

        # Tính tỷ lệ trúng và ngày trúng cho từng phương pháp
        for method_id, data in method_performance.items():
            if data["total_predictions"] > 0:
                data["hit_rate"] = data["total_hits"] / data["total_predictions"] * 100

            if data["days_used"] > 0:
                data["days_hit_rate"] = data["days_hit"] / data["days_used"] * 100

        # Cập nhật thông tin số ngày trúng
        for method_id, data in method_days_hit.items():
            data["days_hit"] = len(data["days_hit"])
            data["days_hit_rate"] = (
                (data["days_hit"] / data["total_days"] * 100)
                if data["total_days"] > 0
                else 0
            )

        # Tính tổng số ngày trúng trong tháng (bất kỳ phương pháp nào trúng)
        days_with_any_hit = set()
        for prediction in all_predictions:
            if prediction.hit_count > 0:
                days_with_any_hit.add(prediction.dan_btl.analysis_date)

        monthly_stats = {
            "total_days": len(dan_btl_entries),
            "days_with_hits": len(days_with_any_hit),
            "days_hit_rate": (
                (len(days_with_any_hit) / len(dan_btl_entries) * 100)
                if dan_btl_entries
                else 0
            ),
        }

        # Sắp xếp phương pháp theo hiệu suất (tỷ lệ trúng)
        sorted_methods = sorted(
            methods,
            key=lambda m: method_performance.get(m.id, {}).get("hit_rate", 0),
            reverse=True,
        )

        # Sắp xếp số theo tần suất xuất hiện
        sorted_numbers = sorted(
            number_counts.items(), key=lambda x: x[1], reverse=True
        )[:20]

        # Lấy top 10 phương pháp
        top10_methods = sorted_methods[:10]

        # Tạo Counter cho top số từ top 10 phương pháp trong ngày mới nhất
        top10_methods_latest_day_numbers = Counter()

        # Đếm số xuất hiện trong top 10 phương pháp của ngày mới nhất
        for method in top10_methods:
            method_id = method.id
            if method_id in latest_day_predictions_by_method:
                predictions = latest_day_predictions_by_method[method_id]["predictions"]
                top10_methods_latest_day_numbers.update(predictions)

        # Sắp xếp số từ top 10 phương pháp trong ngày mới nhất và thêm is_hit
        top10_methods_latest_day_sorted = []
        for num, count in sorted(
            top10_methods_latest_day_numbers.items(), key=lambda x: x[1], reverse=True
        )[:20]:
            is_hit = num in next_day_all_numbers
            top10_methods_latest_day_sorted.append((num, count, is_hit))

        # Sắp xếp số từ ngày mới nhất và thêm is_hit
        latest_day_sorted_numbers = []
        for num, count in sorted(
            latest_day_numbers.items(), key=lambda x: x[1], reverse=True
        )[:20]:
            is_hit = num in next_day_all_numbers
            latest_day_sorted_numbers.append((num, count, is_hit))

        # Thêm is_hit vào top_numbers
        top_numbers = []
        for num, count in sorted_numbers[:20]:
            is_hit = num in next_day_all_numbers
            top_numbers.append((num, count, is_hit))

        # Lấy dự đoán cho ngày được chọn (nếu có)
        selected_day_predictions = {}
        if selected_date:
            for prediction in all_predictions:
                if prediction.dan_btl.analysis_date == selected_date:
                    method_name = prediction.method.name
                    if method_name not in selected_day_predictions:
                        selected_day_predictions[method_name] = []
                    selected_day_predictions[method_name].extend(
                        prediction.predicted_numbers or []
                    )

        context = {
            "year": year,
            "month": month,
            "month_name": calendar.month_name[month],
            "days_in_month": days_in_month,
            "selected_date": selected_date,
            "methods": methods,
            "report_data": report_data,
            "method_totals": method_totals,
            "method_days_hit": method_days_hit,
            "method_performance": method_performance,  # Thêm thông tin hiệu suất
            "monthly_stats": monthly_stats,
            "day_totals": day_totals,
            "prev_month": prev_month,
            "next_month": next_month,
            "has_data": len(dan_btl_entries) > 0,
            "top_numbers": top_numbers,
            "top10_methods_latest_day_numbers": top10_methods_latest_day_sorted,  # Top 20 số từ top 10 phương pháp của ngày mới nhất
            "latest_day_top_numbers": latest_day_sorted_numbers,  # Top 20 số của ngày mới nhất
            "latest_prediction_date": latest_prediction_date,  # Thêm ngày mới nhất vào context
            "next_day_all_numbers": next_day_all_numbers,  # Danh sách số trúng của ngày hôm sau
            "has_next_day_results": len(next_day_all_numbers)
            > 0,  # Cờ kiểm tra xem có kết quả không
            "next_day_date": (
                latest_dan_btl.next_day_date if latest_dan_btl else None
            ),  # Ngày của kết quả
            "selected_day_predictions": selected_day_predictions,
        }

        return render(request, "results/monthly_report_btl.html", context)

    except Exception as e:
        logger.error(f"Error in monthly report view: {str(e)}", exc_info=True)
        context = {"error": f"Lỗi khi tải báo cáo tháng: {str(e)}", "has_data": False}
        return render(request, "results/monthly_report_btl.html", context)


def report_btl_view(request, year=None, month=None):
    """Báo cáo tháng dựa trên dữ liệu phân tích"""
    if year is None or month is None:
        # Xử lý khi không có year hoặc month, lấy tháng hiện tại
        today = timezone.now()
        year = today.year
        month = today.month
    else:
        try:
            year = int(year)
            month = int(month)
        except (ValueError, TypeError):
            # Xử lý khi year hoặc month không hợp lệ
            year = timezone.now().year
            month = timezone.now().month

    # Lấy tổng hợp tháng từ bảng phân tích
    monthly_agg = BtlTimeAggregation.objects.filter(
        aggregation_type="monthly", year=year, period=month
    ).first()

    # Lấy phân tích chi tiết cho từng ngày trong tháng
    daily_analytics = BtlAnalytics.objects.filter(year=year, month=month).order_by(
        "date"
    )

    # Lấy thông tin chi tiết các phương pháp trong tháng
    method_analytics = BtlMethodAnalytics.objects.filter(
        date__year=year, date__month=month
    ).select_related("method")

    # Tính hiệu suất phương pháp theo ngày
    methods_by_day = {}
    for ma in method_analytics:
        date_str = ma.date.strftime("%Y-%m-%d")
        if date_str not in methods_by_day:
            methods_by_day[date_str] = []

        methods_by_day[date_str].append(
            {
                "id": ma.method.id,
                "name": ma.method.name,
                "prediction_count": ma.prediction_count,
                "hit_count": ma.hit_count,
                "hit_rate": ma.hit_rate,
                "confidence_score": ma.confidence_score,
                "profit_estimate": ma.profit_estimate,
                "roi_estimate": ma.roi_estimate,
            }
        )

    # Tính hiệu suất tổng thể của từng phương pháp trong tháng
    method_summary = {}
    for ma in method_analytics:
        method_id = ma.method.id
        if method_id not in method_summary:
            method_summary[method_id] = {
                "id": method_id,
                "name": ma.method.name,
                "total_predictions": 0,
                "total_hits": 0,
                "days_used": 0,
                "days_hit": 0,
                "total_profit": 0,
            }

        method_summary[method_id]["total_predictions"] += ma.prediction_count
        method_summary[method_id]["total_hits"] += ma.hit_count
        method_summary[method_id]["days_used"] += 1
        method_summary[method_id]["days_hit"] += 1 if ma.hit_count > 0 else 0
        method_summary[method_id]["total_profit"] += ma.profit_estimate

    # Tính tỷ lệ trúng và thông tin khác
    for method_id, data in method_summary.items():
        pred_count = data["total_predictions"]
        hit_count = data["total_hits"]
        data["hit_rate"] = (hit_count / pred_count * 100) if pred_count > 0 else 0
        data["days_hit_rate"] = (
            (data["days_hit"] / data["days_used"] * 100) if data["days_used"] > 0 else 0
        )

    # Sắp xếp phương pháp theo hiệu suất
    sorted_methods = sorted(
        method_summary.values(), key=lambda x: x["hit_rate"], reverse=True
    )

    context = {
        "year": year,
        "month": month,
        "month_name": date(year, month, 1).strftime("%B"),
        "monthly_agg": monthly_agg,
        "daily_analytics": daily_analytics,
        "methods_by_day": methods_by_day,
        "sorted_methods": sorted_methods,
        "prev_month": (date(year, month, 1) - timedelta(days=1)).strftime("%Y/%m"),
        "next_month": (date(year, month, 28) + timedelta(days=5)).strftime("%Y/%m"),
    }

    return render(request, "results/btl_report.html", context)


def method_comparison_view(request):
    """So sánh hiệu suất các phương pháp trong khoảng thời gian"""
    # Lấy tham số từ request
    days = int(request.GET.get("days", 30))
    start_date_str = request.GET.get("start_date")
    end_date_str = request.GET.get("end_date")

    today = timezone.now().date()

    # Xác định khoảng thời gian
    if start_date_str and end_date_str:
        start_date = date.fromisoformat(start_date_str)
        end_date = date.fromisoformat(end_date_str)
    else:
        end_date = today
        start_date = end_date - timedelta(days=days - 1)

    # Lấy tất cả phương pháp
    methods = PredictionMethodBtl.objects.filter(is_active=True)

    # Lấy phân tích phương pháp trong khoảng thời gian
    method_analytics = BtlMethodAnalytics.objects.filter(
        date__gte=start_date, date__lte=end_date
    ).select_related("method")

    # Tính hiệu suất tổng thể của từng phương pháp
    method_summary = {}
    for ma in method_analytics:
        method_id = ma.method.id
        if method_id not in method_summary:
            method_summary[method_id] = {
                "id": method_id,
                "name": ma.method.name,
                "total_predictions": 0,
                "total_hits": 0,
                "days_used": 0,
                "days_hit": 0,
                "total_profit": 0,
                "daily_performance": [],
            }

        method_summary[method_id]["total_predictions"] += ma.prediction_count
        method_summary[method_id]["total_hits"] += ma.hit_count
        method_summary[method_id]["days_used"] += 1
        method_summary[method_id]["days_hit"] += 1 if ma.hit_count > 0 else 0
        method_summary[method_id]["total_profit"] += ma.profit_estimate

        # Thêm thông tin hiệu suất theo ngày
        method_summary[method_id]["daily_performance"].append(
            {
                "date": ma.date,
                "prediction_count": ma.prediction_count,
                "hit_count": ma.hit_count,
                "hit_rate": ma.hit_rate,
                "profit": ma.profit_estimate,
            }
        )

    # Tính tỷ lệ trúng và thông tin khác
    for method_id, data in method_summary.items():
        pred_count = data["total_predictions"]
        hit_count = data["total_hits"]
        data["hit_rate"] = (hit_count / pred_count * 100) if pred_count > 0 else 0
        data["days_hit_rate"] = (
            (data["days_hit"] / data["days_used"] * 100) if data["days_used"] > 0 else 0
        )

        # Tính xu hướng
        daily_perf = sorted(data["daily_performance"], key=lambda x: x["date"])
        if len(daily_perf) >= 7:
            recent_7d = daily_perf[-7:]
            recent_hit_rate = sum(d["hit_rate"] for d in recent_7d) / 7
            overall_hit_rate = data["hit_rate"]

            if recent_hit_rate > overall_hit_rate * 1.1:  # Tăng hơn 10%
                data["trend"] = "up"
            elif recent_hit_rate < overall_hit_rate * 0.9:  # Giảm hơn 10%
                data["trend"] = "down"
            else:
                data["trend"] = "stable"
        else:
            data["trend"] = "stable"

    # Sắp xếp phương pháp theo hiệu suất
    sorted_methods = sorted(
        method_summary.values(), key=lambda x: x["hit_rate"], reverse=True
    )
    total_hit_rate = sum(method["hit_rate"] for method in sorted_methods)
    avg_hit_rate = total_hit_rate / len(sorted_methods) if sorted_methods else 0.0

    context = {
        "start_date": start_date,
        "end_date": end_date,
        "days": (end_date - start_date).days + 1,
        "methods": methods,
        "sorted_methods": sorted_methods,
        "avg_hit_rate": avg_hit_rate,
    }

    return render(request, "results/btl_method_comparison.html", context)


def method_correlation_view(request):
    """Phân tích tương quan giữa các phương pháp"""
    # Lấy tham số từ request
    days = int(request.GET.get("days", 30))
    start_date_str = request.GET.get("start_date")
    end_date_str = request.GET.get("end_date")
    today = timezone.now().date()

    # Xác định khoảng thời gian
    if start_date_str and end_date_str:
        start_date = date.fromisoformat(start_date_str)
        end_date = date.fromisoformat(end_date_str)
    else:
        end_date = today
        start_date = end_date - timedelta(days=days - 1)

    # Lấy tất cả phương pháp
    methods = PredictionMethodBtl.objects.filter(is_active=True)
    method_ids = list(methods.values_list("id", flat=True))

    # Lấy phân tích phương pháp trong khoảng thời gian
    method_analytics = BtlMethodAnalytics.objects.filter(
        date__gte=start_date, date__lte=end_date
    ).select_related("method")

    # Tạo ma trận ngày x phương pháp
    dates = list(set(method_analytics.values_list("date", flat=True)))
    dates.sort()

    # Tạo dictionary để lưu trữ kết quả cho mỗi ngày, mỗi phương pháp
    date_method_matrix = {}
    method_names = {}

    for ma in method_analytics:
        date_str = ma.date.strftime("%Y-%m-%d")
        method_id = ma.method.id
        method_names[method_id] = ma.method.name

        if date_str not in date_method_matrix:
            date_method_matrix[date_str] = {}

        date_method_matrix[date_str][method_id] = {
            "hit_count": ma.hit_count,
            "prediction_count": ma.prediction_count,
            "hit_rate": ma.hit_rate,
            "is_hit": ma.hit_count > 0,
        }

    # Tính tương quan giữa các phương pháp
    method_correlations = {}
    for method1 in method_ids:
        if method1 not in method_correlations:
            method_correlations[method1] = {}

        for method2 in method_ids:
            if method1 == method2:
                continue

            if method2 not in method_correlations[method1]:
                # Đếm số ngày cả hai phương pháp đều trúng
                both_hit = 0
                # Đếm số ngày cả hai phương pháp đều có dữ liệu
                total_days = 0

                for date_str, methods_data in date_method_matrix.items():
                    if method1 in methods_data and method2 in methods_data:
                        total_days += 1
                        if (
                            methods_data[method1]["is_hit"]
                            and methods_data[method2]["is_hit"]
                        ):
                            both_hit += 1

                # Tính tỷ lệ trúng đồng thời
                correlation = (both_hit / total_days * 100) if total_days > 0 else 0

                method_correlations[method1][method2] = {
                    "both_hit": both_hit,
                    "total_days": total_days,
                    "correlation": correlation,
                }

    # Tìm top cặp phương pháp có tương quan cao nhất
    top_pairs = []
    for method1, correlations in method_correlations.items():
        for method2, data in correlations.items():
            if data["total_days"] >= 10:  # Chỉ lấy những cặp có đủ dữ liệu
                top_pairs.append(
                    {
                        "method1_id": method1,
                        "method1_name": method_names.get(
                            method1, f"Phương pháp {method1}"
                        ),
                        "method2_id": method2,
                        "method2_name": method_names.get(
                            method2, f"Phương pháp {method2}"
                        ),
                        "both_hit": data["both_hit"],
                        "total_days": data["total_days"],
                        "correlation": data["correlation"],
                    }
                )

    # Sắp xếp theo tương quan giảm dần
    top_pairs.sort(key=lambda x: x["correlation"], reverse=True)
    top_pairs = top_pairs[:20]  # Lấy top 20 cặp

    # Phân tích ngày có nhiều phương pháp trúng nhất
    best_days = []
    for date_str, methods_data in date_method_matrix.items():
        hit_methods = sum(1 for m in methods_data.values() if m["is_hit"])
        total_methods = len(methods_data)
        hit_rate = hit_methods / total_methods * 100 if total_methods > 0 else 0

        date_obj = datetime.strptime(date_str, "%Y-%m-%d").date()
        day_of_week = date_obj.strftime("%A")
        day_of_month = date_obj.day

        best_days.append(
            {
                "date": date_str,
                "day_of_week": day_of_week,
                "day_of_month": day_of_month,
                "hit_methods": hit_methods,
                "total_methods": total_methods,
                "hit_rate": hit_rate,
                "methods": [
                    {
                        "id": method_id,
                        "name": method_names.get(method_id, f"Phương pháp {method_id}"),
                        "hit_rate": method_data["hit_rate"],
                    }
                    for method_id, method_data in methods_data.items()
                    if method_data["is_hit"]
                ],
            }
        )

    # Sắp xếp theo số phương pháp trúng giảm dần
    best_days.sort(key=lambda x: x["hit_methods"], reverse=True)
    best_days = best_days[:10]  # Lấy top 10 ngày

    # Phân tích xu hướng theo ngày trong tuần
    weekday_analysis = {}
    for date_str, methods_data in date_method_matrix.items():
        date_obj = datetime.strptime(date_str, "%Y-%m-%d").date()
        weekday = date_obj.weekday()  # 0 = Monday, 6 = Sunday

        if weekday not in weekday_analysis:
            weekday_analysis[weekday] = {
                "name": date_obj.strftime("%A"),
                "total_days": 0,
                "total_methods": 0,
                "hit_methods": 0,
            }

        weekday_analysis[weekday]["total_days"] += 1
        weekday_analysis[weekday]["total_methods"] += len(methods_data)
        weekday_analysis[weekday]["hit_methods"] += sum(
            1 for m in methods_data.values() if m["is_hit"]
        )

    # Tính tỷ lệ trung bình cho mỗi ngày trong tuần
    weekday_stats = []
    for weekday in range(7):  # 0-6 (Monday-Sunday)
        if weekday in weekday_analysis:
            data = weekday_analysis[weekday]
            avg_hit_rate = (
                (data["hit_methods"] / data["total_methods"] * 100)
                if data["total_methods"] > 0
                else 0
            )

            weekday_stats.append(
                {
                    "weekday": weekday,
                    "name": data["name"],
                    "avg_hit_rate": avg_hit_rate,
                    "total_days": data["total_days"],
                }
            )

    # Sắp xếp theo tỷ lệ trúng giảm dần
    weekday_stats.sort(key=lambda x: x["avg_hit_rate"], reverse=True)

    # Phân tích xu hướng theo ngày trong tháng
    day_of_month_analysis = {}
    for date_str, methods_data in date_method_matrix.items():
        date_obj = datetime.strptime(date_str, "%Y-%m-%d").date()
        day = date_obj.day

        if day not in day_of_month_analysis:
            day_of_month_analysis[day] = {"total_methods": 0, "hit_methods": 0}

        day_of_month_analysis[day]["total_methods"] += len(methods_data)
        day_of_month_analysis[day]["hit_methods"] += sum(
            1 for m in methods_data.values() if m["is_hit"]
        )

    # Tính tỷ lệ trung bình cho mỗi ngày trong tháng
    day_of_month_stats = []
    for day in range(1, 32):  # 1-31
        if day in day_of_month_analysis:
            data = day_of_month_analysis[day]
            avg_hit_rate = (
                (data["hit_methods"] / data["total_methods"] * 100)
                if data["total_methods"] > 0
                else 0
            )

            day_of_month_stats.append({"day": day, "avg_hit_rate": avg_hit_rate})

    # Sắp xếp theo tỷ lệ trúng giảm dần
    day_of_month_stats.sort(key=lambda x: x["avg_hit_rate"], reverse=True)
    day_of_month_stats = day_of_month_stats[:10]  # Lấy top 10 ngày

    context = {
        "start_date": start_date,
        "end_date": end_date,
        "days": (end_date - start_date).days + 1,
        "top_pairs": top_pairs,
        "best_days": best_days,
        "weekday_stats": weekday_stats,
        "day_of_month_stats": day_of_month_stats,
    }

    return render(request, "results/btl_method_correlation.html", context)


class BachThuLoMethodListView(ListView):
    model = BachThuLoMethod
    template_name = "results/method_list.html"
    context_object_name = "methods"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["statistics"] = BachThuLoStatistics.objects.all()
        return context


class BachThuLoMethodDetailView(DetailView):
    model = BachThuLoMethod
    template_name = "results/method_detail.html"
    context_object_name = "method"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        method = self.get_object()

        # Lấy phân tích liên quan đến phương pháp
        analyses = BachThuLoAnalysis.objects.filter(method=method)
        context["analyses"] = analyses

        # Lấy kết quả liên quan đến phương pháp
        results = BachThuLoResult.objects.filter(method=method)
        context["results"] = results

        # Tính toán một số thống kê cơ bản
        if results.exists():
            context["win_count"] = results.filter(is_win=True).count()
            context["loss_count"] = results.filter(is_win=False).count()
            context["win_rate"] = (
                (context["win_count"] / results.count()) * 100
                if results.count() > 0
                else 0
            )

            # Tổng số tiền thắng/thua
            context["total_profit"] = (
                results.aggregate(Sum("profit"))["profit__sum"] or 0
            )

        return context


class BachThuLoStatisticsView(ListView):
    model = BachThuLoStatistics
    template_name = "results/statistics_bach_thu_lo.html"
    context_object_name = "statistics"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Thêm một số thống kê tổng hợp
        methods = BachThuLoMethod.objects.all()
        context["methods_count"] = methods.count()

        results = BachThuLoResult.objects.all()
        context["total_results"] = results.count()
        context["total_wins"] = results.filter(is_win=True).count()
        context["overall_win_rate"] = (
            (context["total_wins"] / context["total_results"]) * 100
            if context["total_results"] > 0
            else 0
        )

        return context


logger = logging.getLogger(__name__)

# Giữ lại các view hiện có
# BachThuLoMethodListView, BachThuLoMethodDetailView, BachThuLoStatisticsView


class BachThuPredictionView(FormView):
    template_name = "results/prediction_btl.html"
    form_class = BachThuPredictionForm
    success_url = reverse_lazy("prediction_btl_results")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        try:
            # Lấy tất cả các phương pháp để hiển thị trong form
            methods = get_all_bach_thu_methods()
            context["available_methods"] = [
                {
                    "code": method.get_code(),
                    "name": method.get_name(),
                    "description": method.get_description(),
                }
                for method in methods
            ]
        except Exception as e:
            logger.error(f"Error loading bach thu methods: {e}")
            context["available_methods"] = []
            messages.error(
                self.request,
                "Không thể tải danh sách phương pháp. Vui lòng thử lại sau.",
            )

        return context

    def form_valid(self, form):
        prediction_date = form.cleaned_data["prediction_date"]
        history_days = form.cleaned_data["history_days"]
        method_codes = form.cleaned_data["method_codes"]
        region_code = form.cleaned_data["region_code"]

        # Lấy dữ liệu xổ số từ KetQuaXoSo
        try:
            lottery_data = self._get_lottery_data(
                prediction_date, history_days, region_code
            )

            # Lưu dữ liệu vào session để hiển thị ở trang kết quả
            self.request.session["prediction_data"] = {
                "prediction_date": prediction_date.strftime("%Y-%m-%d"),
                "history_days": history_days,
                "method_codes": method_codes,
                "region_code": region_code,
                "date": timezone.now().strftime("%Y-%m-%d"),
            }

            # Thực hiện dự đoán
            predictions = self._predict_bach_thu(lottery_data, method_codes)
            self.request.session["predictions"] = predictions

            # Lưu phân tích
            self._save_analyses(predictions, lottery_data, method_codes)

            messages.success(self.request, "Dự đoán bạch thủ lô thành công!")
        except Exception as e:
            logger.error(f"Error in prediction: {e}", exc_info=True)
            messages.error(self.request, f"Lỗi khi thực hiện dự đoán: {str(e)}")
            return redirect("prediction_btl")

        return super().form_valid(form)

    def _get_lottery_data(self, prediction_date, history_days, region_code):
        """
        Lấy dữ liệu xổ số từ model KetQuaXoSo
        """
        # Tính ngày bắt đầu để lấy dữ liệu lịch sử
        start_date = prediction_date - timedelta(days=history_days)

        # Truy vấn dữ liệu xổ số
        lottery_results = KetQuaXoSo.objects.filter(
            ngay__gte=start_date,
            ngay__lt=prediction_date,
        ).order_by("-ngay")

        if not lottery_results.exists():
            raise ValueError(
                f"Không có dữ liệu xổ số cho khu vực {region_code} từ {start_date} đến {prediction_date}"
            )

        # Chuẩn bị dữ liệu để sử dụng cho các phương pháp dự đoán
        previous_results = []

        # Thống kê đầu và đuôi
        head_stats = {str(i): 0 for i in range(10)}
        tail_stats = {str(i): 0 for i in range(10)}

        for result in lottery_results:
            # Lấy tất cả các số trúng (Giải ĐB, nhất, nhì, ba, ...)
            numbers = self._extract_numbers_from_result(result)

            # Thêm vào danh sách kết quả trước đó
            previous_results.append(
                {"date": result.ngay.strftime("%Y-%m-%d"), "numbers": numbers}
            )

            # Cập nhật thống kê đầu và đuôi
            for num in numbers:
                if len(num) >= 2:  # Đảm bảo số có ít nhất 2 chữ số
                    head = num[0]  # Lấy chữ số đầu tiên
                    tail = num[-1]  # Lấy chữ số cuối cùng

                    head_stats[head] = head_stats.get(head, 0) + 1
                    tail_stats[tail] = tail_stats.get(tail, 0) + 1

        # Tạo đối tượng dữ liệu xổ số
        lottery_data = {
            "previous_results": previous_results,
            "head_stats": head_stats,
            "tail_stats": tail_stats,
            "region_code": region_code,
            "prediction_date": prediction_date.strftime("%Y-%m-%d"),
        }

        return lottery_data

    def _extract_numbers_from_result(self, result):
        """
        Trích xuất tất cả các số trúng từ một kết quả xổ số
        """
        numbers = []

        # Lấy số từ các giải (tùy thuộc vào cấu trúc của model KetQuaXoSo)
        # Ví dụ nếu có các trường như giải đặc biệt, giải nhất, v.v.
        if hasattr(result, "giai_db") and result.giai_db:
            numbers.extend(self._normalize_numbers(result.giai_db))

        if hasattr(result, "giai_1") and result.giai_1:
            numbers.extend(self._normalize_numbers(result.giai_1))

        if hasattr(result, "giai_2") and result.giai_2:
            numbers.extend(self._normalize_numbers(result.giai_2))

        if hasattr(result, "giai_3") and result.giai_3:
            numbers.extend(self._normalize_numbers(result.giai_3))

        if hasattr(result, "giai_4") and result.giai_4:
            numbers.extend(self._normalize_numbers(result.giai_4))

        if hasattr(result, "giai_5") and result.giai_5:
            numbers.extend(self._normalize_numbers(result.giai_5))

        if hasattr(result, "giai_6") and result.giai_6:
            numbers.extend(self._normalize_numbers(result.giai_6))

        if hasattr(result, "giai_7") and result.giai_7:
            numbers.extend(self._normalize_numbers(result.giai_7))

        # Nếu có trường chứa tất cả các số
        if hasattr(result, "all_numbers") and result.all_numbers:
            try:
                all_nums = json.loads(result.all_numbers)
                numbers.extend(self._normalize_numbers(all_nums))
            except (json.JSONDecodeError, TypeError):
                pass

        return list(set(numbers))  # Loại bỏ các số trùng lặp

    def _normalize_numbers(self, numbers_str):
        """
        Chuẩn hóa chuỗi số thành danh sách các số 2 chữ số
        """
        normalized = []

        if isinstance(numbers_str, str):
            # Tách chuỗi thành các số riêng biệt
            parts = numbers_str.replace(",", " ").split()

            for part in parts:
                # Loại bỏ các ký tự không phải số
                num = "".join(c for c in part if c.isdigit())

                # Nếu là số 2 chữ số hoặc có thể chuyển thành số 2 chữ số
                if num and 1 <= len(num) <= 6:  # Cho phép từ 1 đến 6 chữ số
                    # Lấy 2 chữ số cuối để dự đoán lô
                    normalized.append(num[-2:] if len(num) >= 2 else num.zfill(2))

        elif isinstance(numbers_str, list):
            # Nếu đầu vào là danh sách
            for item in numbers_str:
                if isinstance(item, str):
                    num = "".join(c for c in item if c.isdigit())
                    if num and 1 <= len(num) <= 6:
                        normalized.append(num[-2:] if len(num) >= 2 else num.zfill(2))
                elif isinstance(item, int):
                    # Chuyển số thành chuỗi 2 chữ số
                    num = str(item)
                    normalized.append(num[-2:] if len(num) >= 2 else num.zfill(2))

        return normalized

    def _predict_bach_thu(self, lottery_data, method_codes=None):
        """
        Dự đoán bạch thủ lô sử dụng các phương pháp đã chọn
        """
        results = {}

        if method_codes:
            methods_to_use = [
                get_method_by_code(code)
                for code in method_codes
                if get_method_by_code(code)
            ]
        else:
            methods_to_use = get_all_bach_thu_methods()

        for method in methods_to_use:
            try:
                predictions = method.calculate(lottery_data)
                results[method.get_code()] = {
                    "name": method.get_name(),
                    "numbers": predictions,
                    "description": method.get_description(),
                }
            except Exception as e:
                logger.error(
                    f"Error calculating {method.get_name()}: {e}", exc_info=True
                )
                results[method.get_code()] = {
                    "name": method.get_name(),
                    "numbers": [],
                    "error": str(e),
                    "description": method.get_description(),
                }

        return results

    def _save_analyses(self, predictions, lottery_data, method_codes):
        """
        Lưu phân tích vào database
        """
        for method_code, result in predictions.items():
            try:
                method_obj = BachThuLoMethod.objects.get(code=method_code)

                # Lấy các trường hợp lệ của model
                from results.models import BachThuLoAnalysis

                valid_fields = {
                    field.name
                    for field in BachThuLoAnalysis._meta.get_fields()
                    if not field.is_relation or field.many_to_one
                }

                # Chuẩn bị dữ liệu hợp lệ để tạo đối tượng
                data = {}

                # Kiểm tra từng trường
                if "method" in valid_fields and hasattr(BachThuLoAnalysis, "method"):
                    data["method"] = method_obj

                if "method_id" in valid_fields and not "method" in valid_fields:
                    data["method_id"] = method_obj.id

                if "data_input" in valid_fields:
                    data["data_input"] = str(lottery_data)

                if "predicted_numbers" in valid_fields:
                    data["predicted_numbers"] = ", ".join(result["numbers"])

                # Thêm các trường bắt buộc khác nếu cần
                if (
                    "created_at" in valid_fields
                    and not BachThuLoAnalysis._meta.get_field("created_at").auto_now_add
                ):
                    data["created_at"] = timezone.now()

                if (
                    "updated_at" in valid_fields
                    and not BachThuLoAnalysis._meta.get_field("updated_at").auto_now
                ):
                    data["updated_at"] = timezone.now()

                # Tạo phân tích mới nếu có dữ liệu hợp lệ
                if data:
                    analysis = BachThuLoAnalysis.objects.create(**data)
                    logger.info(
                        f"Saved analysis for method {method_code}: {analysis.id}"
                    )
                else:
                    logger.warning(
                        f"No valid fields found for BachThuLoAnalysis model when saving method {method_code}"
                    )
            except BachThuLoMethod.DoesNotExist:
                logger.warning(f"Method {method_code} not found in database")
            except Exception as e:
                logger.error(
                    f"Error saving analysis for method {method_code}: {e}",
                    exc_info=True,
                )


class BachThuPredictionResultView(ListView):
    template_name = "results/prediction_btl_results.html"
    context_object_name = "prediction_methods"

    def get_queryset(self):
        predictions = self.request.session.get("predictions", {})
        return predictions

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["prediction_data"] = self.request.session.get("prediction_data", {})
        context["date"] = timezone.now().strftime("%d/%m/%Y")

        # Hiển thị ngày dự đoán theo định dạng người đọc
        prediction_date = self.request.session.get("prediction_data", {}).get(
            "prediction_date"
        )
        if prediction_date:
            try:
                date_obj = datetime.strptime(prediction_date, "%Y-%m-%d")
                context["prediction_date_display"] = date_obj.strftime("%d/%m/%Y")
            except ValueError:
                context["prediction_date_display"] = prediction_date

        # Tạo một số thống kê đơn giản
        predictions = self.request.session.get("predictions", {})
        context["total_methods"] = len(predictions)
        context["total_numbers"] = sum(
            len(method_data.get("numbers", [])) for method_data in predictions.values()
        )

        # Phân tích tần suất số xuất hiện
        frequency = {}
        for method_data in predictions.values():
            for number in method_data.get("numbers", []):
                if number in frequency:
                    frequency[number] += 1
                else:
                    frequency[number] = 1

        # Sắp xếp theo tần suất giảm dần
        context["number_frequency"] = dict(
            sorted(frequency.items(), key=lambda item: item[1], reverse=True)
        )

        # Top 5 số xuất hiện nhiều nhất
        context["top_numbers"] = list(context["number_frequency"].items())[:5]

        return context

    def post(self, request, *args, **kwargs):
        """
        Xử lý khi người dùng chọn lưu kết quả
        """
        try:
            prediction_data = request.session.get("prediction_data", {})
            predictions = request.session.get("predictions", {})

            # Lưu kết quả dự đoán
            region_code = prediction_data.get("region_code", "mb")
            prediction_date = prediction_data.get(
                "prediction_date", timezone.now().strftime("%Y-%m-%d")
            )

            for method_code, method_data in predictions.items():
                try:
                    method_obj = BachThuLoMethod.objects.get(code=method_code)

                    for number in method_data.get("numbers", []):
                        BachThuLoResult.objects.create(
                            method=method_obj,
                            region_code=region_code,
                            date=prediction_date,
                            predicted_number=number,
                            is_win=False,  # Sẽ cập nhật sau khi có kết quả thực tế
                            profit=0,  # Sẽ cập nhật sau khi có kết quả thực tế
                        )
                except BachThuLoMethod.DoesNotExist:
                    logger.warning(
                        f"Method {method_code} not found in database when saving results"
                    )
                except Exception as e:
                    logger.error(
                        f"Error saving result for method {method_code}: {e}",
                        exc_info=True,
                    )

            messages.success(request, "Lưu kết quả dự đoán thành công!")
        except Exception as e:
            logger.error(f"Error saving prediction results: {e}", exc_info=True)
            messages.error(request, f"Lỗi khi lưu kết quả dự đoán: {str(e)}")

        return redirect("btl_method")


from django.views.decorators.http import require_GET


@require_GET
def historical_predictions_api(request):
    """
    API endpoint để lấy các dự đoán lịch sử cho một phương pháp vào một ngày cụ thể

    URL: /api/predictions/historical?methodCode=<code>&date=<YYYY-MM-DD>

    Args:
        methodCode: Mã của phương pháp dự đoán
        date: Ngày dự đoán (định dạng YYYY-MM-DD)

    Returns:
        JsonResponse với các dự đoán lịch sử
    """
    try:
        # Lấy các tham số từ query string
        method_code = request.GET.get("methodCode")
        date_str = request.GET.get("date")

        # Log thông tin request
        logger.info(
            f"Historical predictions request for method code '{method_code}' on {date_str}"
        )

        # Xác thực đầu vào
        if not method_code:
            return JsonResponse({"error": "methodCode is required"}, status=400)

        if not date_str:
            return JsonResponse({"error": "date is required"}, status=400)

        # Chuyển đổi ngày
        try:
            requested_date = parse_date(date_str)
            if not requested_date:
                return JsonResponse(
                    {"error": "Invalid date format. Use YYYY-MM-DD"}, status=400
                )
        except Exception as e:
            logger.error(f"Error parsing date: {e}")
            return JsonResponse(
                {"error": "Invalid date format. Use YYYY-MM-DD"}, status=400
            )

        # Tìm phương pháp dựa trên code
        try:
            method = PredictionMethodAllPrize.objects.get(code=method_code)
        except PredictionMethodAllPrize.DoesNotExist:
            logger.warning(f"Method code '{method_code}' not found")
            return JsonResponse(
                {"error": "Method not found", "predictions": []}, status=404
            )

        # Tìm dự đoán lịch sử
        predictions = get_historical_predictions_for_method(method, requested_date)

        # Log kết quả
        logger.info(
            f"Found {len(predictions)} predictions for method {method.name} on {date_str}"
        )

        # Trả về kết quả
        return JsonResponse(
            {
                "success": True,
                "method": {"id": method.id, "name": method.name, "code": method.code},
                "date": date_str,
                "predictions": predictions,
            }
        )

    except Exception as e:
        logger.exception(f"Error in historical_predictions_api: {str(e)}")
        return JsonResponse({"error": str(e), "predictions": []}, status=500)


def get_historical_predictions_for_method(method, requested_date):
    """
    Tìm các dự đoán lịch sử cho phương pháp và ngày cụ thể

    Chiến lược:
    1. Tìm chính xác ngày và phương pháp
    2. Nếu không có, tìm các ngày tương tự trong 30 ngày gần nhất
    3. Nếu vẫn không có, tạo dự đoán dựa trên các kết quả tương tự

    Args:
        method: Đối tượng PredictionMethodAllPrize
        requested_date: Đối tượng date

    Returns:
        List các số dự đoán
    """
    # 1. Tìm chính xác ngày và phương pháp
    # Giả sử có một mối quan hệ giữa PredictionResult và PredictionMethodAllPrize
    # Nếu không, bạn cần điều chỉnh truy vấn này dựa trên cấu trúc DB của bạn
    exact_results = PredictionDeAllPrizeResult.objects.filter(
        method__code=method.code, dan_de__ngay=requested_date  # Tìm theo code
    )

    if exact_results.exists():
        # Nếu có kết quả chính xác, lấy các số dự đoán
        numbers = []
        for result in exact_results:
            if isinstance(result.predicted_numbers, list):
                numbers.extend(result.predicted_numbers)
            elif isinstance(result.predicted_numbers, str):
                try:
                    parsed = json.loads(result.predicted_numbers)
                    if isinstance(parsed, list):
                        numbers.extend(parsed)
                except:
                    # Nếu không phải JSON, xử lý như chuỗi thông thường
                    numbers.extend(
                        [
                            n.strip()
                            for n in result.predicted_numbers.split(",")
                            if n.strip()
                        ]
                    )

        # Loại bỏ trùng lặp và sắp xếp
        return sorted(list(set(numbers)))

    # 2. Nếu không có kết quả chính xác, tìm trong 30 ngày gần nhất
    thirty_days_ago = requested_date - timezone.timedelta(days=30)
    similar_results = PredictionDeAllPrizeResult.objects.filter(
        method__code=method.code,  # Tìm theo code
        dan_de__ngay__gte=thirty_days_ago,
        dan_de__ngay__lt=requested_date,
    ).order_by("-dan_de__ngay")

    if similar_results.exists():
        # Lấy kết quả từ ngày gần nhất
        latest_date = similar_results.first().dan_de.ngay
        latest_results = similar_results.filter(dan_de__ngay=latest_date)

        numbers = []
        for result in latest_results:
            if isinstance(result.predicted_numbers, list):
                numbers.extend(result.predicted_numbers)
            elif isinstance(result.predicted_numbers, str):
                try:
                    parsed = json.loads(result.predicted_numbers)
                    if isinstance(parsed, list):
                        numbers.extend(parsed)
                except:
                    numbers.extend(
                        [
                            n.strip()
                            for n in result.predicted_numbers.split(",")
                            if n.strip()
                        ]
                    )

        return sorted(list(set(numbers)))

    # 3. Nếu không có kết quả tương tự, tạo dự đoán dựa trên thống kê
    # Tạo dự đoán theo ngày trong tuần
    weekday = requested_date.weekday()
    weekday_results = PredictionDeAllPrizeResult.objects.filter(
        method__code=method.code,  # Tìm theo code
        dan_de__ngay__week_day=weekday
        + 1,  # Django's week_day là 1-7, Python's weekday là 0-6
    ).order_by("-dan_de__ngay")[
        :10
    ]  # Lấy 10 kết quả gần nhất

    if weekday_results.exists():
        # Lấy tất cả các số từ kết quả của ngày tương tự trong tuần
        all_numbers = []
        for result in weekday_results:
            if isinstance(result.predicted_numbers, list):
                all_numbers.extend(result.predicted_numbers)
            elif isinstance(result.predicted_numbers, str):
                try:
                    parsed = json.loads(result.predicted_numbers)
                    if isinstance(parsed, list):
                        all_numbers.extend(parsed)
                except:
                    all_numbers.extend(
                        [
                            n.strip()
                            for n in result.predicted_numbers.split(",")
                            if n.strip()
                        ]
                    )

        # Đếm tần suất của các số
        number_counts = {}
        for num in all_numbers:
            if num in number_counts:
                number_counts[num] += 1
            else:
                number_counts[num] = 1

        # Sắp xếp theo tần suất và lấy 5 số phổ biến nhất
        top_numbers = sorted(number_counts.items(), key=lambda x: x[1], reverse=True)[
            :5
        ]
        return [num for num, count in top_numbers]

    # 4. Nếu không có gì, tạo số dựa trên ngày tháng
    day = requested_date.day
    month = requested_date.month
    year_last_two = requested_date.year % 100

    # Tạo một số dự đoán từ ngày tháng
    date_based_numbers = [
        f"{day:02d}",  # Ngày dạng 2 chữ số
        f"{month:02d}",  # Tháng dạng 2 chữ số
        f"{(day + month) % 100:02d}",  # Tổng ngày và tháng, lấy 2 chữ số cuối
        f"{(day * month) % 100:02d}",  # Tích ngày và tháng, lấy 2 chữ số cuối
        f"{year_last_two:02d}",  # 2 chữ số cuối của năm
    ]

    return date_based_numbers


def day_predictions_api(request):
    year = request.GET.get("year")
    month = request.GET.get("month")
    day = request.GET.get("day")

    if not all([year, month, day]):
        return JsonResponse({"error": "Missing parameters"}, status=400)

    # Tạo key để tìm trong cache hoặc database
    date_key = f"{year}-{month.zfill(2)}-{day.zfill(2)}"

    # Lấy dữ liệu từ cache hoặc database
    predictions_data = get_predictions_for_date(date_key)

    if not predictions_data:
        return JsonResponse({"error": "No data found"}, status=404)

    return JsonResponse(predictions_data)


def get_predictions_for_date(date_key, use_cache=True):
    """
    Lấy dữ liệu dự đoán cho một ngày cụ thể

    Args:
        date_key (str): Ngày ở định dạng 'YYYY-MM-DD'
        use_cache (bool): Có sử dụng cache hay không

    Returns:
        dict: Dữ liệu dự đoán được định dạng theo cấu trúc cần thiết cho UI
    """
    # Khởi tạo cache key
    cache_key = f"predictions_data_{date_key}"

    # Kiểm tra cache nếu use_cache=True
    if use_cache:
        cached_data = cache.get(cache_key)
        if cached_data:
            logger.info(f"Retrieved predictions for {date_key} from cache")
            return cached_data

    try:
        # Chuyển đổi date_key thành đối tượng date
        try:
            requested_date = parse_date(date_key)
            if not requested_date:
                logger.error(f"Invalid date format: {date_key}")
                return None
        except Exception as e:
            logger.error(f"Error parsing date {date_key}: {e}")
            return None

        # Tìm đối tượng DanDeDacBiet cho ngày này
        try:
            dan_de = DanDeDacBietAllPrize.objects.get(ngay=requested_date)
        except DanDeDacBietAllPrize.DoesNotExist:
            logger.warning(f"No DanDeDacBiet found for date {date_key}")
            return None

        # Lấy kết quả ngày tiếp theo (nếu có)
        next_day = requested_date + timedelta(days=1)
        next_day_dan_de = DanDeDacBietAllPrize.objects.filter(ngay=next_day).first()

        # Lấy tất cả các kết quả dự đoán cho ngày này
        prediction_results = PredictionDeAllPrizeResult.objects.filter(dan_de=dan_de)

        if not DanDeDacBietAllPrize.exists():
            logger.warning(f"No prediction results found for date {date_key}")
            return None

        # Lấy danh sách tất cả các phương pháp
        method_ids = prediction_results.values_list("method_id", flat=True).distinct()
        methods = PredictionMethodAllPrize.objects.filter(id__in=method_ids)

        # Khởi tạo cấu trúc dữ liệu kết quả
        result = {
            "date": requested_date.strftime("%d/%m/%Y"),
            "methods": [],
            "predictions": {},
            "all_numbers": set(),  # Sử dụng set để tránh trùng lặp
            "winning_numbers": [],
            "special_prize": "",
            "next_day_date": next_day.strftime("%d/%m/%Y") if next_day_dan_de else None,
        }

        # Xử lý thông tin giải đặc biệt ngày tiếp theo nếu có
        if (
            next_day_dan_de
            and hasattr(next_day_dan_de, "ket_qua")
            and next_day_dan_de.ket_qua
        ):
            try:
                # Giả sử ket_qua là một đối tượng chứa thông tin giải đặc biệt
                special_prize = next_day_dan_de.ket_qua.giai_db
                result["special_prize"] = special_prize

                # Lấy 2 số cuối của giải đặc biệt
                if special_prize and len(special_prize) >= 2:
                    result["special_prize_last2"] = special_prize[-2:]

                # Thu thập tất cả các số trúng
                all_winning_numbers = next_day_dan_de.ket_qua.get_all_2digit_numbers()
                result["winning_numbers"] = list(all_winning_numbers)

            except Exception as e:
                logger.error(f"Error extracting winning information: {e}")

        # Thu thập dữ liệu dự đoán cho từng phương pháp
        for method in methods:
            method_results = prediction_results.filter(method=method)

            # Thêm thông tin phương pháp
            result["methods"].append(
                {"id": method.id, "name": method.name, "code": method.code}
            )

            # Thu thập tất cả số dự đoán cho phương pháp này
            predicted_numbers = []
            for pred_result in method_results:
                # Kiểm tra kiểu dữ liệu của predicted_numbers
                if hasattr(pred_result, "predicted_numbers"):
                    if isinstance(pred_result.predicted_numbers, list):
                        predicted_numbers.extend(pred_result.predicted_numbers)
                    elif isinstance(pred_result.predicted_numbers, str):
                        # Thử parse JSON nếu là chuỗi
                        try:
                            parsed = json.loads(pred_result.predicted_numbers)
                            if isinstance(parsed, list):
                                predicted_numbers.extend(parsed)
                            else:
                                # Nếu không phải list, có thể là chuỗi ngăn cách bằng dấu phẩy
                                predicted_numbers.extend(
                                    [
                                        n.strip()
                                        for n in pred_result.predicted_numbers.split(
                                            ","
                                        )
                                        if n.strip()
                                    ]
                                )
                        except json.JSONDecodeError:
                            # Nếu không phải JSON, xử lý như chuỗi thông thường
                            predicted_numbers.extend(
                                [
                                    n.strip()
                                    for n in pred_result.predicted_numbers.split(",")
                                    if n.strip()
                                ]
                            )

            # Loại bỏ trùng lặp và sắp xếp
            unique_numbers = sorted(list(set(predicted_numbers)))

            # Thêm vào kết quả
            result["predictions"][method.code] = unique_numbers
            result["all_numbers"].update(unique_numbers)

        # Chuyển set thành list để có thể serialize
        result["all_numbers"] = sorted(list(result["all_numbers"]))

        # Tính tần suất xuất hiện của các số
        frequency_map = {}
        for method_code, numbers in result["predictions"].items():
            for num in numbers:
                frequency_map[num] = frequency_map.get(num, 0) + 1

        result["frequency_map"] = frequency_map

        # Tính số lượng phương pháp dự đoán mỗi số
        result["method_counts"] = {}
        for num in result["all_numbers"]:
            method_count = 0
            for numbers in result["predictions"].values():
                if num in numbers:
                    method_count += 1
            result["method_counts"][num] = method_count

        # Thêm thông tin hiệu suất cho từng số
        result["performance"] = {}
        for num in result["all_numbers"]:
            is_winning = num in result["winning_numbers"]
            result["performance"][num] = {
                "is_winning": is_winning,
                "prediction_count": frequency_map.get(num, 0),
                "method_count": result["method_counts"][num],
            }

        # Lưu vào cache nếu use_cache=True
        if use_cache:
            # Lưu cache trong 1 giờ (3600 giây)
            cache.set(cache_key, result, timeout=3600)
            logger.info(f"Saved predictions for {date_key} to cache")

        return result

    except Exception as e:
        logger.exception(f"Error getting predictions for date {date_key}: {e}")
        return None


import math

from django.conf import settings

from .calculate_profit import calculate_profit

# Tạo logger riêng cho phân tích hiệu năng
perf_logger = logging.getLogger("performance")

# def daily_prediction_analysis_view(request):
#     """
#     View phân tích dự đoán theo ngày - phiên bản cải tiến với Wilson score và phân nhóm phương pháp
#     """
#     # Đánh dấu thời gian bắt đầu
#     start_time = time.time()
#     step_times = {}

#     # Hàm helper để ghi log thời gian thực thi của từng bước
#     def log_step(step_name):
#         current_time = time.time()
#         elapsed = current_time - start_time
#         step_times[step_name] = elapsed
#         perf_logger.info(f"PERF - {step_name}: {elapsed:.4f}s")
#         return current_time

#     # Lấy tham số ngày từ request
#     date_str = request.GET.get('date')
#     if not date_str:
#         # Nếu không có tham số ngày, lấy ngày hiện tại
#         today = timezone.now().date()
#         date_str = today.strftime('%Y-%m-%d')

#     try:
#         # Chuyển đổi chuỗi ngày thành đối tượng date
#         analysis_date = parse_date(date_str)
#         if not analysis_date:
#             raise ValueError("Invalid date format")

#         # Tính toán ngày trước và ngày sau cho điều hướng
#         prev_day = analysis_date - timedelta(days=1)
#         prev_day_str = prev_day.strftime('%Y-%m-%d')
#         next_day = analysis_date + timedelta(days=1)
#         next_day_str = next_day.strftime('%Y-%m-%d')

#         log_step("1. Khởi tạo ngày tháng")

#         # Lấy dữ liệu DanDeDacBietAllPrize cho ngày phân tích
#         try:
#             dan_de = DanDeDacBietAllPrize.objects.get(analysis_date=analysis_date)
#         except DanDeDacBietAllPrize.DoesNotExist:
#             return render(request, 'results/daily_analysis.html', {
#                 'error': f"Không tìm thấy dữ liệu DanDeDacBiet cho ngày {date_str}",
#                 'date': date_str,
#                 'prev_day': prev_day_str,
#                 'next_day': next_day_str,
#                 'formatted_date': analysis_date.strftime('%d/%m/%Y')
#             })

#         log_step("2. Lấy dữ liệu DanDeDacBietAllPrize")

#         # Lấy kết quả ngày tiếp theo nếu có
#         next_day_result = None
#         next_day_ket_qua = None
#         special_prize = None
#         special_prize_last2 = None
#         winning_numbers = []
#         try:
#             next_day_dan_de = DanDeDacBietAllPrize.objects.get(analysis_date=next_day)
#             next_day_result = next_day_dan_de
#             # Lấy kết quả xổ số
#             next_day_ket_qua = KetQuaXoSo.objects.filter(ngay=next_day).first()
#             if next_day_ket_qua:
#                 # Lấy giải đặc biệt
#                 if hasattr(next_day_ket_qua, 'giai_db') and next_day_ket_qua.giai_db:
#                     special_prize = next_day_ket_qua.giai_db
#                     # Lấy 2 số cuối của giải đặc biệt
#                     if len(special_prize) >= 2:
#                         special_prize_last2 = special_prize[-2:]
#                 # Lấy tất cả các số 2 chữ số trúng
#                 if hasattr(next_day_ket_qua, 'get_all_2digit_numbers'):
#                     winning_numbers = next_day_ket_qua.get_all_2digit_numbers()
#                 else:
#                     # Nếu không có phương thức get_all_2digit_numbers, tự trích xuất
#                     winning_numbers = extract_all_2digit_numbers(next_day_ket_qua)
#         except DanDeDacBietAllPrize.DoesNotExist:
#             pass

#         log_step("3. Lấy kết quả ngày tiếp theo")

#         # Lấy tất cả kết quả dự đoán cho ngày này
#         prediction_results = PredictionDeAllPrizeResult.objects.filter(dan_de=dan_de)
#         if not prediction_results.exists():
#             return render(request, 'results/daily_analysis.html', {
#                 'error': f"Không tìm thấy kết quả dự đoán cho ngày {date_str}",
#                 'date': date_str,
#                 'prev_day': prev_day_str,
#                 'next_day': next_day_str,
#                 'formatted_date': analysis_date.strftime('%d/%m/%Y')
#             })

#         # Tối ưu hóa: Tải tất cả kết quả vào bộ nhớ để giảm số lượng truy vấn
#         all_prediction_results = list(prediction_results)

#         log_step("4. Lấy kết quả dự đoán")

#         # Lấy danh sách phương pháp
#         method_ids = prediction_results.values_list('method_id', flat=True).distinct()
#         methods = PredictionMethodAllPrize.objects.filter(id__in=method_ids)
#         all_methods = list(methods)  # Tải tất cả vào bộ nhớ

#         log_step("5. Lấy danh sách phương pháp")

#         # Thu thập dữ liệu dự đoán cho từng phương pháp
#         methods_data = []
#         all_predictions = []
#         prediction_counts = Counter()  # Đếm số lần xuất hiện của mỗi số
#         method_counts = defaultdict(set)  # Đếm số phương pháp dự đoán mỗi số

#         # Tính toán thành công cho từng phương pháp
#         method_allprize_hits = {}
#         method_prediction_counts = {}

#         # Tối ưu hóa: Tạo dict để truy cập nhanh các kết quả theo method_id
#         method_to_results = defaultdict(list)
#         for result in all_prediction_results:
#             method_to_results[result.method_id].append(result)

#         for result in all_prediction_results:
#             method_name = result.method.name
#             if method_name not in method_allprize_hits:
#                 method_allprize_hits[method_name] = 0
#                 method_prediction_counts[method_name] = 0

#             # Xử lý predicted_numbers tùy theo kiểu dữ liệu
#             numbers = get_prediction_numbers(result)
#             method_prediction_counts[method_name] += len(numbers)

#             # Tính số trúng
#             if winning_numbers:
#                 hits = sum(1 for num in numbers if num in winning_numbers)
#                 method_allprize_hits[method_name] += hits

#         log_step("6. Thống kê cơ bản các phương pháp")

#         # Tạo danh sách dữ liệu phương pháp chi tiết
#         for method in all_methods:
#             # Lấy kết quả dự đoán cho phương pháp này
#             method_results = method_to_results[method.id]

#             # Thu thập tất cả số dự đoán
#             predicted_numbers = []
#             for result in method_results:
#                 numbers = get_prediction_numbers(result)
#                 predicted_numbers.extend(numbers)

#             # Loại bỏ trùng lặp
#             predicted_numbers = sorted(list(set(predicted_numbers)))

#             # Cập nhật số lần xuất hiện của mỗi số
#             for num in predicted_numbers:
#                 prediction_counts[num] += 1
#                 method_counts[num].add(method.name)

#             # Tìm số trúng
#             hit_numbers = []
#             if winning_numbers:
#                 hit_numbers = [num for num in predicted_numbers if num in winning_numbers]

#             # Thêm vào danh sách tất cả số dự đoán
#             all_predictions.extend(predicted_numbers)

#             # Tạo dữ liệu cho phương pháp
#             method_data = {
#                 'id': method.id,
#                 'name': method.name,
#                 'code': method.code,
#                 'predicted_numbers': predicted_numbers,
#                 'prediction_count': len(predicted_numbers),
#                 'hit_numbers': hit_numbers,
#                 'hit_count': len(hit_numbers),
#                 'hit_rate': (len(hit_numbers) / len(predicted_numbers) * 100) if predicted_numbers else 0
#             }

#             # --- CẢI TIẾN: Thêm tính toán Wilson score ---
#             method_data['confidence_score'] = wilson_score(len(hit_numbers), len(predicted_numbers))

#             # --- CẢI TIẾN: Thêm nhóm phương pháp ---
#             method_data['group'] = determine_method_group(method_data)

#             methods_data.append(method_data)

#         log_step("7. Tạo dữ liệu chi tiết phương pháp")

#         # --- CẢI TIẾN: Phân nhóm và cải thiện đánh giá phương pháp ---
#         enhanced_methods = enhance_method_performance(methods_data)

#         log_step("8. Nâng cao hiệu suất phương pháp")

#         method_groups = group_methods(enhanced_methods)

#         log_step("9. Nhóm phương pháp")

#         selected_methods = select_top_methods_from_groups(method_groups)

#         log_step("10. Chọn phương pháp hàng đầu từ mỗi nhóm")

#         # ----- THAY ĐỔI: Sử dụng kết quả tối ưu đã lưu nếu có -----
#         # Tìm kiếm kết quả tối ưu hóa đã lưu
#         try:
#             ensemble = OptimalMethodEnsemble.objects.get(analysis_date=analysis_date)
#             # Lấy dữ liệu từ cơ sở dữ liệu
#             optimal_methods = ensemble.get_optimal_methods()
#             ranked_methods = ensemble.get_ranked_methods()

#             perf_logger.info(f"PERF - Sử dụng kết quả tối ưu hóa đã lưu từ cơ sở dữ liệu")
#             log_step("11-14. Sử dụng kết quả tối ưu đã lưu")

#             # Nếu không tìm thấy ranked_methods trong cơ sở dữ liệu, thực hiện tính toán
#             if not ranked_methods:
#                 # --- CẢI TIẾN: Phân tích xu hướng hiệu suất ---
#                 history_data = get_historical_data(analysis_date, 90)
#                 analyze_performance_trends(selected_methods, history_data, winning_numbers)

#                 # --- CẢI TIẾN: Xếp hạng phương pháp dự đoán đa chiều ---
#                 ranked_methods = rank_prediction_methods(enhanced_methods, history_data, analysis_date, winning_numbers)
#         except OptimalMethodEnsemble.DoesNotExist:
#             # Nếu không có kết quả đã lưu, thực hiện tính toán như trước
#             perf_logger.info(f"PERF - Không tìm thấy kết quả tối ưu hóa đã lưu, tính toán mới")

#             # --- CẢI TIẾN: Phân tích xu hướng hiệu suất ---
#             history_data = get_historical_data(analysis_date, 90)
#             log_step("11. Lấy dữ liệu lịch sử (có thể tốn nhiều thời gian)")

#             analyze_performance_trends(selected_methods, history_data, winning_numbers)
#             log_step("12. Phân tích xu hướng hiệu suất")

#             # --- CẢI TIẾN: Xếp hạng phương pháp dự đoán đa chiều ---
#             ranked_methods = rank_prediction_methods(enhanced_methods, history_data, analysis_date, winning_numbers)
#             log_step("13. Xếp hạng phương pháp dự đoán (có thể tốn nhiều thời gian)")

#             # --- CẢI TIẾN: Chọn tập hợp phương pháp tối ưu và đa dạng ---
#             optimal_methods = select_optimal_method_ensemble(ranked_methods, max_methods=5)
#             log_step("14. Chọn tập hợp phương pháp tối ưu")

#             # Lưu kết quả vào cơ sở dữ liệu cho lần sau
#             try:
#                 ensemble = OptimalMethodEnsemble(analysis_date=analysis_date)
#                 ensemble.set_ranked_methods(clean_for_json(ranked_methods[:20] if ranked_methods else []))
#                 ensemble.set_optimal_methods(clean_for_json(optimal_methods))
#                 ensemble.calculation_time = time.time() - start_time
#                 ensemble.save()
#                 perf_logger.info(f"PERF - Đã lưu kết quả tối ưu hóa vào cơ sở dữ liệu")
#             except Exception as e:
#                 perf_logger.error(f"PERF - Lỗi khi lưu kết quả tối ưu hóa: {str(e)}")

#         # --- CẢI TIẾN: Tính toán lợi nhuận cho các phương pháp được chọn ---
#         for method in optimal_methods:
#             method['profit_analysis'] = calculate_profit(method)

#         log_step("15. Tính toán lợi nhuận cho phương pháp tối ưu")

#         # --- CẢI TIẾN: Tính toán lợi nhuận cho Top 3 phương pháp ---
#         top_methods = selected_methods[:3] if len(selected_methods) >= 3 else selected_methods
#         for method in top_methods:
#             method['profit_analysis'] = calculate_profit(method)

#         log_step("16. Tính toán lợi nhuận cho Top 3 phương pháp")

#         # --- CẢI TIẾN: Tạo dự đoán đa dạng từ phương pháp được chọn ---
#         final_predictions = generate_diverse_predictions(selected_methods, winning_numbers)

#         log_step("17. Tạo dự đoán đa dạng")

#         log_step("18. Tính toán thống kê tổng quan")

#         # Top 10 số được dự đoán nhiều nhất
#         top_numbers = sorted(prediction_counts.items(), key=lambda x: x[1], reverse=True)[:10]
#         top_numbers = [
#             {
#                 'number': num,
#                 'count': count,
#                 'is_hit': num in winning_numbers,
#                 'confidence': wilson_score(1 if num in winning_numbers else 0, 1) * count  # Điểm tin cậy
#             }
#             for num, count in top_numbers
#         ]

#         # Phân tích mức độ đồng thuận giữa các phương pháp
#         consensus_numbers = [
#             {
#                 'number': num,
#                 'method_count': method_count_dict.get(num, 0),
#                 'prediction_count': prediction_counts[num],
#                 'is_hit': num in winning_numbers,
#                 'confidence': wilson_score(1 if num in winning_numbers else 0, 1) * method_count_dict.get(num, 0)
#             }
#             for num in all_unique_predictions
#         ]
#         consensus_numbers.sort(key=lambda x: x['method_count'], reverse=True)

#         log_step("19. Phân tích số đồng thuận")

#         # Phân tích đầu số và đuôi số
#         head_counts = Counter()
#         tail_counts = Counter()
#         for num in all_unique_predictions:
#             if len(num) >= 2:
#                 head = num[0]
#                 tail = num[1]
#                 head_counts[head] += 1
#                 tail_counts[tail] += 1

#         # Top 3 đầu số phổ biến nhất
#         top_heads = head_counts.most_common(3)
#         # Top 3 đuôi số phổ biến nhất
#         top_tails = tail_counts.most_common(3)

#         log_step("20. Phân tích đầu/đuôi số")

#         # Phân tích xu hướng lịch sử
#         # Lấy dữ liệu 30 ngày trước đó
#         historical_hits, historical_hit_counts = get_historical_hits(analysis_date)

#         log_step("21. Lấy lịch sử trúng số (có thể tốn nhiều thời gian)")

#         # Top 10 số trúng nhiều nhất trong lịch sử
#         top_historical_hits = historical_hit_counts.most_common(10)
#         top_historical_hits = [
#             {
#                 'number': num,
#                 'count': count,
#                 'is_in_prediction': num in all_unique_predictions,
#                 'is_hit': num in winning_numbers
#             }
#             for num, count in top_historical_hits
#         ]

#         log_step("22. Phân tích top lịch sử")

#         # --- CẢI TIẾN: Phân tích chu kỳ nâng cao ---
#         cycle_analysis = analyze_cycles(analysis_date, all_unique_predictions, method_count_dict, winning_numbers)

#         log_step("23. Phân tích chu kỳ (có thể tốn nhiều thời gian)")

#         # Tạo giải thích cho phương pháp được chọn
#         prediction_explanation = generate_method_selection_explanation(optimal_methods, analysis_date)

#         log_step("24. Tạo giải thích dự đoán")

#         # Chuẩn bị context cho template
#         context = {
#             'date': date_str,
#             'formatted_date': analysis_date.strftime('%d/%m/%Y'),
#             'prev_day': prev_day_str,
#             'next_day': next_day_str,
#             'formatted_next_day': next_day.strftime('%d/%m/%Y'),
#             # Dữ liệu kết quả
#             'special_prize': special_prize,
#             'special_prize_last2': special_prize_last2,
#             'winning_numbers': winning_numbers,
#             # Thông tin tổng quan
#             'total_methods': total_methods,
#             'total_predictions': total_predictions,
#             'total_hits': total_hits,
#             'overall_hit_rate': overall_hit_rate,
#             # Dữ liệu phương pháp
#             'ranked_methods': ranked_methods[:10],  # Top 10 phương pháp xếp hạng cao nhất
#             'optimal_methods': optimal_methods,     # Tập hợp phương pháp tối ưu
#             'prediction_explanation': prediction_explanation,
#             'next_day_forecast': {
#                 'date': next_day.strftime('%d/%m/%Y'),
#                 'recommended_methods': [m['name'] for m in optimal_methods],
#                 'success_probability': np.mean([m.get('next_day_probability', 0) for m in optimal_methods]) * 100
#             },
#             'methods_data': enhanced_methods,  # Phiên bản cải tiến với Wilson score
#             'selected_methods': selected_methods,  # Top phương pháp từ mỗi nhóm
#             'top_methods': top_methods,
#             # Dữ liệu dự đoán
#             'all_predictions': all_unique_predictions,
#             'top_numbers': top_numbers,
#             'consensus_numbers': consensus_numbers[:10],  # Top 10 số đồng thuận cao nhất
#             # Phân tích mẫu
#             'top_heads': top_heads,
#             'top_tails': top_tails,
#             # Phân tích lịch sử
#             'top_historical_hits': top_historical_hits,
#             'cycle_analysis': cycle_analysis[:15],  # Top 15 số có chu kỳ dài nhất
#             # Đề xuất số cải tiến
#             'recommended_numbers': final_predictions[:10],  # Top 10 số được đề xuất
#             # Thông tin về kết quả tối ưu hóa đã lưu
#             'optimization_info': {
#                 'from_cache': 'ensemble' in locals(),
#                 'calculation_time': ensemble.calculation_time if 'ensemble' in locals() else None,
#                 'last_updated': ensemble.updated_at if 'ensemble' in locals() else None
#             }
#         }

#         log_step("25. Chuẩn bị context")

#         # Thêm thông tin hiệu năng vào context nếu DEBUG=True
#         if settings.DEBUG:
#             context['performance_data'] = {
#                 'total_time': time.time() - start_time,
#                 'step_times': step_times
#             }

#         # Log tổng thời gian thực thi
#         total_time = time.time() - start_time
#         perf_logger.info(f"PERF - Tổng thời gian: {total_time:.4f}s")

#         # Tính toán kích thước context
#         context_size = 0
#         for key, value in context.items():
#             try:
#                 # Thử ước tính kích thước của mỗi giá trị
#                 import sys
#                 context_size += sys.getsizeof(value)
#             except:
#                 pass

#         perf_logger.info(f"PERF - Ước lượng kích thước context: {context_size / (1024*1024):.2f} MB")

#         return render(request, 'results/daily_analysis.html', context)
#     except Exception as e:
#         import traceback
#         error_time = time.time() - start_time
#         perf_logger.error(f"PERF - Lỗi sau {error_time:.4f}s: {str(e)}")
#         traceback.print_exc()
#         return render(request, 'results/daily_analysis.html', {
#             'error': f"Lỗi khi phân tích dữ liệu: {str(e)}",
#             'date': date_str
#         })


# --- CÁC HÀM HỖ TRỢ ---
def clean_for_json(data):
    """
    Xử lý dữ liệu để đảm bảo có thể chuyển đổi thành JSON
    """
    if isinstance(data, dict):
        return {k: clean_for_json(v) for k, v in data.items()}
    elif isinstance(data, list):
        return [clean_for_json(item) for item in data]
    elif isinstance(data, (int, float, str, bool)) or data is None:
        return data
    else:
        return str(data)


def generate_method_selection_explanation(methods, current_date):
    """
    Tạo giải thích dễ hiểu về lý do chọn các phương pháp
    """
    explanations = []

    for i, method in enumerate(methods):
        explanation = {
            "method": method["name"],
            "ranking": i + 1,
            "strengths": [],
            "reasons": [],
        }

        # Thêm điểm mạnh dựa trên các điểm số
        if method.get("hit_rate", 0) > 70:
            explanation["strengths"].append("Tỷ lệ trúng cao")

        if method.get("stability_score", 0) > 0.7:
            explanation["strengths"].append("Hiệu suất ổn định")

        if method.get("trend_score", 0) > 0.7:
            explanation["strengths"].append("Xu hướng tăng gần đây")

        if method.get("context_score", 0) > 0.7:
            explanation["strengths"].append("Phù hợp với ngày hiện tại")

        if method.get("next_day_probability", 0) > 0.6:
            explanation["strengths"].append("Xác suất thành công cao")

        # Thêm lý do chọn
        explanation["reasons"].append(
            f"Điểm xếp hạng tổng hợp: {method.get('ranking_score', 0):.2f}/1.0"
        )

        if method.get("hit_count", 0) > 0 and method.get("prediction_count", 0) > 0:
            explanation["reasons"].append(
                f"Hiệu suất gần đây: {method.get('hit_count', 0)}/{method.get('prediction_count', 0)} "
                f"({method.get('hit_rate', 0):.1f}%)"
            )

        if method.get("next_day_probability") is not None:
            explanation["reasons"].append(
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
    predicted_numbers = method.get("predicted_numbers", [])

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
    head_diversity = (
        calculate_entropy([count / len(heads) for count in head_counts.values()])
        if heads
        else 0
    )
    tail_diversity = (
        calculate_entropy([count / len(tails) for count in tail_counts.values()])
        if tails
        else 0
    )

    # Chuẩn hóa kết quả (entropy tối đa khi phân bố đều trên 10 giá trị = log2(10) ≈ 3.32)
    max_entropy = math.log2(10)  # Vì có 10 chữ số (0-9)
    normalized_head_diversity = min(head_diversity / max_entropy, 1.0)
    normalized_tail_diversity = min(tail_diversity / max_entropy, 1.0)

    # Tính đa dạng về các mẫu số đặc biệt
    special_patterns_diversity = calculate_special_patterns_diversity(predicted_numbers)

    # Kết hợp các điểm đa dạng
    diversity_score = (
        normalized_head_diversity
        + normalized_tail_diversity
        + special_patterns_diversity
    ) / 3

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
        "double": 0,  # Số kép (11, 22, ...)
        "mirror": 0,  # Số gương (19, 28, ...)
        "consecutive": 0,  # Số liên tiếp (12, 23, ...)
        "reversed": 0,  # Số đảo (12, 21, ...)
        "same_sum": 0,  # Tổng chữ số bằng nhau
    }

    # Phân loại các số
    for num in numbers:
        if len(num) == 2:
            if num[0] == num[1]:  # Số kép
                pattern_counts["double"] += 1
            elif int(num[0]) + int(num[1]) == 9:  # Số gương
                pattern_counts["mirror"] += 1
            elif abs(int(num[0]) - int(num[1])) == 1:  # Số liên tiếp
                pattern_counts["consecutive"] += 1

            # Kiểm tra số đảo
            reversed_num = num[1] + num[0]
            if reversed_num in numbers and reversed_num != num:
                pattern_counts["reversed"] += 1

    # Tính tỷ lệ mỗi loại mẫu
    total = len(numbers)
    pattern_ratios = [count / total for count in pattern_counts.values()]

    # Tính mức độ cân bằng giữa các loại mẫu
    # Nếu các mẫu đặc biệt xuất hiện nhiều nhưng đa dạng -> điểm cao
    pattern_entropy = calculate_entropy([r for r in pattern_ratios if r > 0])

    # Chuẩn hóa
    max_pattern_entropy = math.log2(len(pattern_counts))
    normalized_pattern_entropy = (
        min(pattern_entropy / max_pattern_entropy, 1.0)
        if max_pattern_entropy > 0
        else 0.5
    )

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
        date_obj = d["date"]
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
            "total_predictions": 0,
            "total_hits": 0,
            "hit_rate": 0,
            "consistency": 0,
            "confidence": 0,
        }

    # Tính tổng số dự đoán và số trúng
    total_predictions = 0
    total_hits = 0
    hit_rates = []

    for day in period_data:
        # Tìm thông tin phương pháp trong ngày đó
        method_in_day = next(
            (m for m in day.get("methods", []) if m.get("id") == method.get("id")), None
        )

        if method_in_day:
            day_predictions = method_in_day.get("prediction_count", 0)
            day_hits = method_in_day.get("hit_count", 0)

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
        "total_predictions": total_predictions,
        "total_hits": total_hits,
        "hit_rate": overall_hit_rate * 100,  # Chuyển thành phần trăm
        "consistency": consistency * 100,  # Chuyển thành phần trăm
        "confidence": confidence * 100,  # Chuyển thành phần trăm
    }


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
            performance[f"{period}_days"] = perf

        # Tính điểm trung bình
        avg_hit_rate = np.mean([perf["hit_rate"] for perf in performance.values()])
        avg_consistency = np.mean(
            [perf["consistency"] for perf in performance.values()]
        )
        avg_confidence = np.mean([perf["confidence"] for perf in performance.values()])

        # Tính xu hướng hiệu suất (đang tăng hay giảm)
        if len(periods) >= 2:
            short_term = performance[f"{periods[0]}_days"]["hit_rate"]
            long_term = performance[f"{periods[-1]}_days"]["hit_rate"]
            trend = short_term - long_term
        else:
            trend = 0

        # Tính điểm xếp hạng tổng hợp
        ranking_score = (
            avg_hit_rate * 0.4  # 40% dựa vào tỷ lệ trúng
            + avg_consistency * 0.2  # 20% dựa vào độ nhất quán
            + avg_confidence * 0.3  # 30% dựa vào độ tin cậy
            + (trend > 0) * 10  # +10 điểm nếu xu hướng đang tăng
        )

        # Thêm thông tin hiệu suất vào method
        method_copy["performance"] = performance
        method_copy["avg_hit_rate"] = avg_hit_rate
        method_copy["avg_consistency"] = avg_consistency
        method_copy["avg_confidence"] = avg_confidence
        method_copy["trend"] = trend
        method_copy["ranking_score"] = ranking_score

        # Dự đoán xác suất thành công cho ngày tiếp theo
        method_copy["next_day_probability"] = predict_next_day_success(
            method, history_data, current_date
        )

        ranked_methods.append(method_copy)

    # Sắp xếp phương pháp theo điểm xếp hạng giảm dần
    ranked_methods.sort(key=lambda x: x["ranking_score"], reverse=True)

    return ranked_methods


def calculate_stability_score(time_performance):
    """Tính điểm ổn định dựa trên độ dao động của hiệu suất"""
    # Lấy các hiệu suất theo thời gian
    performances = [perf["hit_rate"] for perf in time_performance.values()]

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
    for i in range(len(periods) - 1):
        shorter_period = periods[i]
        longer_period = periods[i + 1]

        shorter_perf = time_performance[shorter_period]["hit_rate"]
        longer_perf = time_performance[longer_period]["hit_rate"]

        # Tính điểm xu hướng (tăng là tốt)
        diff = shorter_perf - longer_perf

        # Chuẩn hóa sự khác biệt và áp dụng hàm sigmoid để giảm ảnh hưởng của giá trị cực đoan
        normalized_diff = sigmoid(diff / 10)  # Chia cho 10 để giảm độ lớn

        # Gán trọng số cao hơn cho xu hướng gần đây
        weight = 2 ** (i + 1)
        trend_points.append((normalized_diff, weight))

    # Tính điểm xu hướng tổng hợp (weighted average)
    total_weight = sum(w for _, w in trend_points)
    trend_score = (
        sum(score * weight for score, weight in trend_points) / total_weight
        if total_weight
        else 0.5
    )

    return trend_score


def evaluate_context_fit(method, current_date, history_data):
    """Đánh giá độ phù hợp của phương pháp với ngày hiện tại"""
    # Xác định các đặc điểm của ngày hiện tại
    day_of_week = current_date.weekday()
    day_of_month = current_date.day

    # Lấy dữ liệu lịch sử cho ngày tương tự (cùng thứ trong tuần)
    similar_days = [
        entry
        for entry in history_data
        if datetime.strptime(entry["date"], "%Y-%m-%d").weekday() == day_of_week
    ]

    # Tính hiệu suất của phương pháp trong các ngày tương tự
    method_name = method["name"]
    hit_count = 0
    total_count = 0

    for day_data in similar_days:
        method_result = next(
            (m for m in day_data.get("methods", []) if m.get("name") == method_name),
            None,
        )
        if method_result:
            hit_count += method_result.get("hit_count", 0)
            total_count += method_result.get("prediction_count", 0) or 1

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

    if hasattr(result, "predicted_numbers"):
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
                    numbers = [
                        n.strip()
                        for n in result.predicted_numbers.split(",")
                        if n.strip()
                    ]
            except json.JSONDecodeError:
                # Nếu không phải JSON, xử lý như chuỗi thông thường
                numbers = [
                    n.strip() for n in result.predicted_numbers.split(",") if n.strip()
                ]

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
            std = (
                (sum((p - avg) ** 2 for p in perfs) / len(perfs)) ** 0.5
                if len(perfs) > 1
                else 0
            )
            weekday_stats[weekday] = {"avg": avg, "std": std, "count": len(perfs)}

    # Kiểm tra độ khác biệt giữa các ngày trong tuần
    if len(weekday_stats) < 3:  # Cần ít nhất 3 ngày có dữ liệu
        return 0.5

    # Tính phương sai giữa các ngày
    all_avgs = [stats["avg"] for stats in weekday_stats.values()]
    global_avg = sum(all_avgs) / len(all_avgs)

    between_day_variance = sum((avg - global_avg) ** 2 for avg in all_avgs) / len(
        all_avgs
    )

    # Tính phương sai trung bình trong mỗi ngày
    within_day_variance = sum(
        stats["std"] ** 2 for stats in weekday_stats.values()
    ) / len(weekday_stats)

    # Tính tỷ lệ phương sai (F-statistic)
    variance_ratio = (
        between_day_variance / within_day_variance if within_day_variance > 0 else 1.0
    )

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
            weights = [2**i for i in range(min(len(perfs), 4))]
            weighted_perfs = [
                perfs[-i - 1] * weights[i] for i in range(min(len(perfs), 4))
            ]
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
    method_name = method["name"]
    date_perf = []

    # Thu thập dữ liệu hiệu suất theo ngày
    for entry in history_data:
        entry_date = datetime.strptime(entry["date"], "%Y-%m-%d")
        method_result = next(
            (m for m in entry.get("methods", []) if m.get("name") == method_name), None
        )

        if method_result and method_result.get("prediction_count", 0) > 0:
            hit_rate = (
                method_result.get("hit_count", 0)
                / method_result.get("prediction_count", 1)
                * 100
            )
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
    valid_entries = [
        entry for entry in history_data if "methods" in entry and entry["methods"]
    ]

    for i, entry in enumerate(valid_entries[:-1]):  # Bỏ qua mục cuối cùng
        entry_date = entry["date"]
        if isinstance(entry_date, str):
            try:
                entry_date = datetime.strptime(entry_date, "%Y-%m-%d").date()
            except (ValueError, TypeError):
                continue
        elif isinstance(entry_date, datetime):
            entry_date = entry_date.date()

        next_entry = valid_entries[i + 1]

        # Xử lý cho từng phương pháp trong ngày
        for method_result in entry.get("methods", []):
            # Trích xuất đặc trưng
            features = extract_model_features(method_result, entry_date, history_data)

            # Tìm kết quả thực tế ngày tiếp theo
            next_day_result = next(
                (
                    m
                    for m in next_entry.get("methods", [])
                    if m.get("id") == method_result.get("id")
                ),
                None,
            )

            if next_day_result:
                pred_count = next_day_result.get("prediction_count", 0)
                hit_count = next_day_result.get("hit_count", 0)

                if pred_count > 0:
                    actual_hit_rate = hit_count / pred_count

                    # Thêm vào tập dữ liệu huấn luyện
                    X.append(features)
                    y.append(actual_hit_rate)

    # Nếu không đủ dữ liệu, trả về mô hình giả
    if len(X) < 10:

        return DummyRegressor(strategy="mean")

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
        method.get("hit_rate", 0) / 100,  # Tỷ lệ trúng
        method.get("confidence_score", 0),  # Wilson score
        method.get("prediction_count", 0) / 100,  # Số lượng dự đoán (chuẩn hóa)
        len(method.get("group", "other"))
        / 10,  # Độ dài của tên nhóm (đặc trưng đơn giản về nhóm)
        method.get("stability_score", 0.5),  # Độ ổn định
        method.get("trend_score", 0.5),  # Xu hướng
        method.get("diversity_score", 0.5),  # Độ đa dạng
    ]

    # Đặc trưng về thời gian
    time_features = [
        current_date.weekday() / 6,  # Ngày trong tuần (0-1)
        current_date.day / 31,  # Ngày trong tháng (0-1)
        current_date.month / 12,  # Tháng trong năm (0-1)
        int(current_date.day % 2 == 0),  # Ngày chẵn/lẻ
    ]

    # Đặc trưng về hiệu suất lịch sử cho ngày tương tự
    historical_features = extract_historical_features(
        method, history_data, current_date
    )

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
    method_name = method.get("name")

    # Đặc trưng về hiệu suất trong các khoảng thời gian khác nhau
    periods = [7, 15, 30, 60]
    period_features = []

    for days in periods:
        # Tính hiệu suất trong khoảng thời gian
        start_date = current_date - timedelta(days=days)

        # Lọc dữ liệu lịch sử trong khoảng thời gian
        period_data = [
            entry
            for entry in history_data
            if start_date
            <= datetime.strptime(entry["date"], "%Y-%m-%d").date()
            < current_date
        ]

        # Tính hiệu suất của phương pháp
        hits = 0
        predictions = 0

        for entry in period_data:
            for m in entry.get("methods", []):
                if m.get("name") == method_name:
                    hits += m.get("hit_count", 0)
                    predictions += m.get("prediction_count", 0)

        # Tính tỷ lệ trúng
        hit_rate = hits / max(predictions, 1)

        # Thêm vào đặc trưng
        period_features.append(hit_rate)

    # Đặc trưng về hiệu suất theo ngày trong tuần
    weekday = current_date.weekday()
    weekday_hits = 0
    weekday_predictions = 0

    for entry in history_data:
        entry_date = datetime.strptime(entry["date"], "%Y-%m-%d").date()
        if entry_date.weekday() == weekday:
            for m in entry.get("methods", []):
                if m.get("name") == method_name:
                    weekday_hits += m.get("hit_count", 0)
                    weekday_predictions += m.get("prediction_count", 0)

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
    method_name = method.get("name")
    current_day = current_date.day

    # Thu thập hiệu suất cho ngày tương tự trong tháng
    similar_day_hits = 0
    similar_day_predictions = 0

    for entry in history_data:
        entry_date = datetime.strptime(entry["date"], "%Y-%m-%d").date()
        if entry_date.day == current_day:
            for m in entry.get("methods", []):
                if m.get("name") == method_name:
                    similar_day_hits += m.get("hit_count", 0)
                    similar_day_predictions += m.get("prediction_count", 0)

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
        entry_date_obj = entry["date"]
        if isinstance(entry_date_obj, str):
            try:
                entry_date_obj = datetime.strptime(entry_date_obj, "%Y-%m-%d").date()
            except (ValueError, TypeError):
                continue
        elif isinstance(entry_date_obj, datetime):
            entry_date_obj = entry_date_obj.date()

        # So sánh date với date
        if entry_date_obj < entry_date:
            recent_history.append(entry)

    # Giới hạn chỉ lấy 30 ngày gần nhất
    recent_history = sorted(recent_history, key=lambda x: x["date"], reverse=True)[:30]

    # Tính các đặc trưng
    # 1. Tỷ lệ trúng trung bình trong 7 ngày gần nhất
    recent_7day = recent_history[:7]
    hit_rates_7day = []
    for day in recent_7day:
        # Tìm kết quả của phương pháp trong ngày
        method_in_day = next(
            (
                m
                for m in day.get("methods", [])
                if m.get("id") == method_result.get("id")
            ),
            None,
        )
        if method_in_day:
            pred_count = method_in_day.get("prediction_count", 0)
            hit_count = method_in_day.get("hit_count", 0)
            if pred_count > 0:
                hit_rates_7day.append(hit_count / pred_count)

    avg_hit_rate_7day = (
        sum(hit_rates_7day) / len(hit_rates_7day) if hit_rates_7day else 0
    )
    features.append(avg_hit_rate_7day)

    # 2. Tỷ lệ trúng trung bình trong 30 ngày
    hit_rates_30day = []
    for day in recent_history:
        method_in_day = next(
            (
                m
                for m in day.get("methods", [])
                if m.get("id") == method_result.get("id")
            ),
            None,
        )
        if method_in_day:
            pred_count = method_in_day.get("prediction_count", 0)
            hit_count = method_in_day.get("hit_count", 0)
            if pred_count > 0:
                hit_rates_30day.append(hit_count / pred_count)

    avg_hit_rate_30day = (
        sum(hit_rates_30day) / len(hit_rates_30day) if hit_rates_30day else 0
    )
    features.append(avg_hit_rate_30day)

    # 3. Độ lệch chuẩn của tỷ lệ trúng (độ ổn định)
    std_hit_rate = np.std(hit_rates_30day) if len(hit_rates_30day) > 1 else 0
    features.append(std_hit_rate)

    # 4. Xu hướng gần đây (tỷ lệ trúng 7 ngày so với 30 ngày)
    trend = avg_hit_rate_7day - avg_hit_rate_30day
    features.append(trend)

    # 5. Số lượng dự đoán trung bình
    avg_predictions = (
        sum(
            method_in_day.get("prediction_count", 0)
            for day in recent_history
            for method_in_day in [
                next(
                    (
                        m
                        for m in day.get("methods", [])
                        if m.get("id") == method_result.get("id")
                    ),
                    None,
                )
            ]
            if method_in_day is not None
        )
        / len(recent_history)
        if recent_history
        else 0
    )
    features.append(avg_predictions)

    # 6. Wilson score trung bình
    wilson_scores = []
    for day in recent_history:
        method_in_day = next(
            (
                m
                for m in day.get("methods", [])
                if m.get("id") == method_result.get("id")
            ),
            None,
        )
        if method_in_day:
            pred_count = method_in_day.get("prediction_count", 0)
            hit_count = method_in_day.get("hit_count", 0)
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
    except Exception as e:
        # Nếu có lỗi, sử dụng phương pháp đơn giản hơn
        avg_hit_rate = (
            method.get("avg_hit_rate", 0) / 100 if "avg_hit_rate" in method else 0
        )
        trend = method.get("trend", 0) / 100 if "trend" in method else 0

        # Tính xác suất đơn giản dựa trên tỷ lệ trúng trung bình và xu hướng
        simple_prediction = max(0, min(0.95, avg_hit_rate * (1 + trend)))

        return simple_prediction


def select_optimal_method_ensemble(ranked_methods, max_methods=5):
    """
    Chọn tập hợp phương pháp tối ưu, cân bằng giữa hiệu suất và đa dạng
    """
    if len(ranked_methods) <= max_methods:
        return ranked_methods

    # Bắt đầu với phương pháp tốt nhất
    selected_methods = [ranked_methods[0]]
    remaining_methods = ranked_methods[1:]

    # Thêm lần lượt các phương pháp, ưu tiên sự đa dạng
    while len(selected_methods) < max_methods and remaining_methods:
        # Tính điểm đa dạng cho từng phương pháp còn lại
        diversity_scores = []

        for candidate in remaining_methods:
            diversity = calculate_ensemble_diversity(candidate, selected_methods)
            # Kết hợp điểm đa dạng với điểm xếp hạng gốc
            combined_score = 0.7 * candidate["ranking_score"] + 0.3 * diversity
            diversity_scores.append((candidate, combined_score))

        # Chọn phương pháp có điểm kết hợp cao nhất
        best_candidate, _ = max(diversity_scores, key=lambda x: x[1])

        # Thêm vào danh sách đã chọn
        selected_methods.append(best_candidate)
        remaining_methods.remove(best_candidate)

    return selected_methods


def calculate_ensemble_diversity(candidate, selected_methods):
    """
    Tính độ đa dạng của một phương pháp ứng viên so với các phương pháp đã chọn
    """
    # Độ đa dạng về nhóm phương pháp
    group_diversity = (
        1.0 if candidate["group"] not in [m["group"] for m in selected_methods] else 0.0
    )

    # Độ đa dạng về số dự đoán
    prediction_overlap = 0
    total_predictions = len(candidate["predicted_numbers"])

    if total_predictions > 0:
        # Tính tỷ lệ số dự đoán trùng lặp với các phương pháp đã chọn
        all_selected_predictions = []
        for method in selected_methods:
            all_selected_predictions.extend(method["predicted_numbers"])

        overlap_count = sum(
            1
            for num in candidate["predicted_numbers"]
            if num in all_selected_predictions
        )
        prediction_overlap = overlap_count / total_predictions

    # Độ đa dạng về dự đoán (1 - tỷ lệ trùng lặp)
    prediction_diversity = 1 - prediction_overlap

    # Độ đa dạng về đặc điểm hiệu suất
    performance_features = [
        candidate["hit_rate"],
        candidate["stability_score"],
        candidate["trend_score"],
    ]

    performance_diversity = 0
    if selected_methods:
        avg_distances = []
        for method in selected_methods:
            method_features = [
                method["hit_rate"],
                method.get("stability_score", 0.5),
                method.get("trend_score", 0.5),
            ]

            # Tính khoảng cách Euclidean giữa các vector đặc trưng
            distance = (
                sum(
                    (f1 - f2) ** 2
                    for f1, f2 in zip(performance_features, method_features)
                )
                ** 0.5
            )
            avg_distances.append(distance)

        # Chuẩn hóa khoảng cách trung bình
        performance_diversity = (
            sum(avg_distances) / len(avg_distances) / (3**0.5)
        )  # 3 là số chiều

    # Kết hợp các yếu tố đa dạng
    diversity_score = (
        0.4 * group_diversity + 0.4 * prediction_diversity + 0.2 * performance_diversity
    )

    return diversity_score


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
    return (
        phat
        + z * z / (2 * total)
        - z * math.sqrt((phat * (1 - phat) + z * z / (4 * total)) / total)
    ) / (1 + z * z / total)


def determine_method_group(method):
    """
    Xác định nhóm của phương pháp dựa trên tên hoặc đặc điểm
    """
    name = method.get("name", "").lower()
    code = method.get("code", "").lower()

    if any(
        term in name or term in code
        for term in ["statistical", "thống kê", "frequency", "tần suất"]
    ):
        return "statistical"
    elif any(term in name or term in code for term in ["pattern", "mẫu"]):
        return "pattern"
    elif any(term in name or term in code for term in ["cycle", "chu kỳ"]):
        return "cycle"
    elif any(term in name or term in code for term in ["combination", "kết hợp"]):
        return "combination"
    elif any(term in name or term in code for term in ["historical", "lịch sử"]):
        return "historical"
    else:
        return "other"


def enhance_method_performance(methods_data):
    """
    Cải thiện đánh giá hiệu suất của phương pháp bằng cách sử dụng
    điểm Wilson score và đặt ngưỡng dự đoán tối thiểu
    """
    enhanced_methods = []

    for method in methods_data:
        # Bỏ qua phương pháp có quá ít dự đoán (dưới 5)
        if method["prediction_count"] < 5:
            continue

        # Tính toán Wilson score đã được tính trong vòng lặp chính
        confidence_score = method.get("confidence_score", 0)

        # Tính hiệu suất trọng số (cân nhắc cả tỷ lệ trúng và số lượng dự đoán)
        weighted_performance = confidence_score * (
            1 + math.log(method["prediction_count"] + 1, 10)
        )

        # Sao chép và bổ sung thông tin phương pháp
        enhanced_method = method.copy()
        enhanced_method.update({"weighted_performance": weighted_performance})

        enhanced_methods.append(enhanced_method)

    # Sắp xếp theo hiệu suất trọng số
    return sorted(
        enhanced_methods, key=lambda x: x["weighted_performance"], reverse=True
    )


def group_methods(methods):
    """
    Phân nhóm các phương pháp theo loại
    """
    groups = defaultdict(list)
    for method in methods:
        group = method.get("group", "other")
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
    selected_methods = sorted(
        selected_methods, key=lambda x: x["weighted_performance"], reverse=True
    )
    return selected_methods[:max_total]


def get_historical_data(analysis_date, days_back=90):
    """
    Lấy dữ liệu lịch sử từ cơ sở dữ liệu
    """
    start_date = analysis_date - timedelta(days=days_back)

    # Lấy kết quả xổ số trong khoảng thời gian
    draw_results = KetQuaXoSo.objects.filter(
        ngay__gte=start_date, ngay__lt=analysis_date
    ).order_by("ngay")

    # Lấy các dự đoán trong khoảng thời gian
    predictions = DanDeDacBietAllPrize.objects.filter(
        analysis_date__gte=start_date, analysis_date__lt=analysis_date
    ).order_by("analysis_date")

    # Tổ chức dữ liệu theo ngày
    history_data = []

    for result in draw_results:
        result_date = result.ngay

        # Lấy tất cả số 2 chữ số
        if hasattr(result, "get_all_2digit_numbers"):
            winning_numbers = result.get_all_2digit_numbers()
        else:
            winning_numbers = extract_all_2digit_numbers(result)

        # Lấy dự đoán cho ngày trước kết quả này
        pred_date = result_date - timedelta(days=1)
        daily_predictions = predictions.filter(analysis_date=pred_date)

        for dan_de in daily_predictions:
            prediction_results = PredictionDeAllPrizeResult.objects.filter(
                dan_de=dan_de
            )

            methods_results = []
            for pred in prediction_results:
                predicted_nums = get_prediction_numbers(pred)
                hit_count = sum(1 for num in predicted_nums if num in winning_numbers)

                methods_results.append(
                    {
                        "name": pred.method.name,
                        "predicted_numbers": predicted_nums,
                        "prediction_count": len(predicted_nums),
                        "hit_count": hit_count,
                        "hit_rate": (
                            (hit_count / len(predicted_nums) * 100)
                            if predicted_nums
                            else 0
                        ),
                    }
                )

            history_data.append(
                {
                    "date": result_date.strftime("%Y-%m-%d"),
                    "winning_numbers": winning_numbers,
                    "methods": methods_results,
                }
            )

    return history_data


def analyze_performance_trends(
    methods, history_data, winning_numbers, time_periods=[30, 60, 90]
):
    """
    Phân tích xu hướng hiệu suất của phương pháp theo thời gian
    """
    now = timezone.now().date()

    for method in methods:
        method["performance_trend"] = []

        for period in time_periods:
            # Tính hiệu suất trong khoảng thời gian nhất định
            start_date = now - timedelta(days=period)

            # Lọc lịch sử kết quả trong khoảng thời gian
            period_history = [
                entry
                for entry in history_data
                if start_date
                <= datetime.strptime(entry["date"], "%Y-%m-%d").date()
                <= now
            ]

            # Tính tỷ lệ trúng trong khoảng thời gian này
            hits = 0
            predictions = 0

            for entry in period_history:
                method_results = next(
                    (
                        m
                        for m in entry.get("methods", [])
                        if m.get("name") == method.get("name")
                    ),
                    None,
                )
                if method_results:
                    hits += method_results.get("hit_count", 0)
                    predictions += method_results.get("prediction_count", 0)

            # Tính tỷ lệ trúng và điểm tin cậy
            hit_rate = (hits / predictions * 100) if predictions > 0 else 0
            confidence = wilson_score(hits, predictions) if predictions > 0 else 0

            method["performance_trend"].append(
                {
                    "period": period,
                    "hit_rate": hit_rate,
                    "confidence": confidence,
                    "predictions": predictions,
                    "hits": hits,
                }
            )

        # Xác định xu hướng hiệu suất (tăng/giảm/ổn định)
        if len(method["performance_trend"]) >= 2:
            short_term = method["performance_trend"][0]["confidence"]
            long_term = method["performance_trend"][-1]["confidence"]

            if short_term > long_term * 1.1:
                method["trend"] = "increasing"
            elif short_term < long_term * 0.9:
                method["trend"] = "decreasing"
            else:
                method["trend"] = "stable"
        else:
            method["trend"] = "unknown"

        # Kiểm tra xem phương pháp có dự đoán đúng số nào trong kết quả hiện tại không
        if winning_numbers:
            hits = sum(
                1
                for num in method.get("predicted_numbers", [])
                if num in winning_numbers
            )
            method["current_hits"] = hits
            method["current_hit_rate"] = (
                (hits / method["prediction_count"] * 100)
                if method["prediction_count"] > 0
                else 0
            )


def generate_diverse_predictions(selected_methods, winning_numbers, max_predictions=30):
    """
    Tạo danh sách dự đoán đa dạng từ các phương pháp được chọn
    """
    # Thu thập tất cả dự đoán từ các phương pháp được chọn
    all_predictions = []
    for method in selected_methods:
        for num in method.get("predicted_numbers", []):
            all_predictions.append(
                {
                    "number": num,
                    "method": method.get("name"),
                    "confidence": method.get("confidence_score", 0),
                    "group": method.get("group", "other"),
                }
            )

    # Tổng hợp dự đoán trùng lặp và tính điểm tổng hợp
    number_scores = defaultdict(lambda: {"score": 0, "methods": [], "groups": set()})

    for pred in all_predictions:
        num = pred["number"]
        number_scores[num]["score"] += pred["confidence"]
        number_scores[num]["methods"].append(pred["method"])
        number_scores[num]["groups"].add(pred["group"])

    # Chuyển đổi thành danh sách và thêm thông tin đa dạng (số nhóm khác nhau)
    predictions_list = []
    for num, data in number_scores.items():
        # Bổ sung thêm điểm cho số được dự đoán bởi nhiều nhóm phương pháp khác nhau
        diversity_bonus = len(data["groups"]) / 5  # Tối đa 1.0 cho 5 nhóm

        predictions_list.append(
            {
                "number": num,
                "score": data["score"]
                * (1 + diversity_bonus)
                * 100,  # Tăng điểm cho dự đoán đa dạng
                "method_count": len(set(data["methods"])),
                "methods": list(set(data["methods"])),
                "group_count": len(data["groups"]),
                "groups": list(data["groups"]),
                "is_hit": num in winning_numbers,
                "reasons": generate_prediction_reasons(num, data),
            }
        )

    # Sắp xếp theo điểm và giới hạn số lượng
    predictions_list.sort(key=lambda x: x["score"], reverse=True)
    return predictions_list[:max_predictions]


def generate_prediction_reasons(number, data):
    """
    Tạo danh sách lý do giải thích tại sao số này được đề xuất
    """
    reasons = []

    # Lý do 1: Xuất hiện trong nhiều phương pháp
    if len(data["methods"]) > 1:
        reasons.append(f"Xuất hiện trong {len(data['methods'])} phương pháp dự đoán")

    # Lý do 2: Thuộc nhiều nhóm phương pháp
    if len(data["groups"]) > 1:
        group_names = {
            "statistical": "Thống kê",
            "pattern": "Mẫu",
            "cycle": "Chu kỳ",
            "combination": "Kết hợp",
            "historical": "Lịch sử",
            "other": "Khác",
        }
        group_list = [group_names.get(g, g) for g in data["groups"]]
        reasons.append(
            f"Xuất hiện trong {len(data['groups'])} nhóm phương pháp ({', '.join(group_list)})"
        )

    # Lý do 3: Đề xuất bởi phương pháp có hiệu suất cao
    top_methods = [
        m for m in data["methods"] if "top" in m.lower() or "cao" in m.lower()
    ]
    if top_methods:
        reasons.append(
            f"Được dự đoán bởi phương pháp hiệu suất cao: {', '.join(top_methods[:2])}"
        )

    return reasons


def get_historical_hits(analysis_date, days_back=30):
    """
    Lấy và phân tích các số trúng trong lịch sử
    """
    start_date = analysis_date - timedelta(days=days_back)

    # Lấy kết quả xổ số trong khoảng thời gian
    historical_results = KetQuaXoSo.objects.filter(
        ngay__gte=start_date, ngay__lt=analysis_date
    ).order_by("ngay")

    # Tìm các số thường trúng trong lịch sử
    historical_hits = []

    for result in historical_results:
        # Lấy tất cả số 2 chữ số
        if hasattr(result, "get_all_2digit_numbers"):
            numbers = result.get_all_2digit_numbers()
        else:
            numbers = extract_all_2digit_numbers(result)

        historical_hits.extend(numbers)

    # Đếm tần suất trúng của mỗi số
    historical_hit_counts = Counter(historical_hits)

    return historical_hits, historical_hit_counts


def analyze_cycles(
    analysis_date, all_predictions, method_counts, winning_numbers, days_back=60
):
    """
    Phân tích chu kỳ xuất hiện của các số
    """
    start_date = analysis_date - timedelta(days=days_back)

    # Lấy tất cả kết quả xổ số trong khoảng thời gian, sắp xếp theo ngày
    recent_results = KetQuaXoSo.objects.filter(
        ngay__gte=start_date, ngay__lt=analysis_date
    ).order_by("ngay")

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
        if hasattr(result, "get_all_2digit_numbers"):
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
                days_since_last = (
                    days_back  # Giả định là lâu hơn khoảng thời gian phân tích
                )

            cycle_analysis.append(
                {
                    "number": num,
                    "last_appearance": last_appearance[num],
                    "days_since_last": days_since_last,
                    "method_count": method_counts.get(num, 0),
                    "is_hit": num in winning_numbers,
                    # Thêm điểm chu kỳ - số ngày không xuất hiện nhân với số phương pháp dự đoán
                    "cycle_score": days_since_last * method_counts.get(num, 0) / 10,
                }
            )

    # Sắp xếp theo số ngày từ lần xuất hiện gần nhất và số phương pháp
    cycle_analysis.sort(
        key=lambda x: (x["days_since_last"], x["method_count"]), reverse=True
    )

    return cycle_analysis


def extract_all_2digit_numbers(ket_qua):
    """
    Trích xuất tất cả các số 2 chữ số từ kết quả xổ số
    """
    numbers = []

    # Trích xuất từ giải đặc biệt
    if hasattr(ket_qua, "giai_db") and ket_qua.giai_db:
        if len(ket_qua.giai_db) >= 2:
            numbers.append(ket_qua.giai_db[-2:])

    # Trích xuất từ các giải khác
    for i in range(1, 8):
        field_name = f"giai_{i}"
        if hasattr(ket_qua, field_name):
            giai_values = getattr(ket_qua, field_name)

            # Xử lý nếu là chuỗi ngăn cách bằng dấu phẩy
            if isinstance(giai_values, str):
                for val in giai_values.split(","):
                    val = val.strip()
                    if len(val) >= 2:
                        numbers.append(val[-2:])
            # Xử lý nếu là list
            elif isinstance(giai_values, list):
                for val in giai_values:
                    if isinstance(val, str) and len(val) >= 2:
                        numbers.append(val[-2:])

    return sorted(list(set(numbers)))  # Loại bỏ trùng lặp


import calendar

from django.contrib import messages
from django.core.paginator import Paginator

# views.py
from django.shortcuts import redirect, render

from results.models import NumberFrequencyStats


class NumberFrequencyView(View):
    template_name = "results/number_frequency.html"

    def get(self, request):
        # Lấy các tham số từ request
        view_type = request.GET.get(
            "view_type", "month"
        )  # month, day_of_month, day_of_week
        year = int(request.GET.get("year", timezone.now().year))
        month = int(request.GET.get("month", timezone.now().month))
        day_range = int(request.GET.get("day_range", 31))  # Số ngày hiển thị

        # Tạo context mặc định
        context = {
            "view_type": view_type,
            "year": year,
            "month": month,
            "day_range": day_range,
            "years": range(timezone.now().year - 5, timezone.now().year + 1),
            "months": range(1, 13),
            "day_ranges": [7, 15, 31, 60, 90],
            "days_of_month": range(1, 32),
            "days_of_week": ["CN", "T2", "T3", "T4", "T5", "T6", "T7"],
        }

        # Kiểm tra nếu cần cập nhật dữ liệu tần suất
        if "update_stats" in request.GET:
            self.update_frequency_stats()
            messages.success(request, "Đã cập nhật dữ liệu tần suất thành công!")
            return redirect("number_frequency")

        # Tạo bảng tần suất tùy theo view_type
        if view_type == "month":
            context.update(self.get_monthly_frequency_table(year, month, day_range))
        elif view_type == "day_of_month":
            context.update(self.get_day_of_month_frequency_table(year, month))
        elif view_type == "day_of_week":
            context.update(self.get_day_of_week_frequency_table(year, month))

        return render(request, self.template_name, context)

    def update_frequency_stats(self):
        """Cập nhật dữ liệu tần suất vào model NumberFrequencyStats"""
        # Xóa dữ liệu cũ để tránh trùng lặp
        # NumberFrequencyStats.objects.all().delete()  # Bỏ comment dòng này nếu muốn xóa dữ liệu cũ

        # Lấy ngày cuối cùng đã lưu trong NumberFrequencyStats
        last_date = (
            NumberFrequencyStats.objects.order_by("-date")
            .values_list("date", flat=True)
            .first()
        )

        # Nếu đã có dữ liệu, lấy kết quả từ ngày tiếp theo
        # Nếu chưa có, lấy tất cả kết quả
        if last_date:
            results = KetQuaXoSo.objects.filter(ngay__gt=last_date).order_by("ngay")
        else:
            results = KetQuaXoSo.objects.all().order_by("ngay")

        # Tạo các bản ghi NumberFrequencyStats cho mỗi kết quả
        batch_size = 100
        stats_to_create = []

        for result in results:
            # Lấy tất cả số 2 chữ số từ kết quả
            all_numbers = []
            special_prize = []
            first_prize = []
            other_prizes = []

            # Lấy giải đặc biệt
            if hasattr(result, "giai_db") and result.giai_db:
                db_numbers = self.extract_two_digit_numbers(result.giai_db)
                special_prize.extend(db_numbers)
                all_numbers.extend(db_numbers)

            # Lấy giải nhất
            if hasattr(result, "giai_1") and result.giai_1:
                g1_numbers = self.extract_two_digit_numbers(result.giai_1)
                first_prize.extend(g1_numbers)
                all_numbers.extend(g1_numbers)

            # Lấy các giải khác
            for field in ["giai_2", "giai_3", "giai_4", "giai_5", "giai_6", "giai_7"]:
                if hasattr(result, field) and getattr(result, field):
                    field_numbers = self.extract_two_digit_numbers(
                        getattr(result, field)
                    )
                    other_prizes.extend(field_numbers)
                    all_numbers.extend(field_numbers)

            # Loại bỏ các số trùng lặp
            all_numbers = list(set(all_numbers))

            # Tính week_of_month
            week_of_month = (result.ngay.day - 1) // 7 + 1

            # Tạo bản ghi cho mỗi số
            for number in all_numbers:
                stats_to_create.append(
                    NumberFrequencyStats(
                        number=number,
                        date=result.ngay,
                        appeared_in_special=(number in special_prize),
                        appeared_in_first=(number in first_prize),
                        appeared_in_other=(number in other_prizes),
                        day_of_week=result.ngay.weekday(),
                        day_of_month=result.ngay.day,
                        week_of_month=week_of_month,
                        month=result.ngay.month,
                        year=result.ngay.year,
                    )
                )

                # Lưu theo batch để tránh tiêu tốn bộ nhớ
                if len(stats_to_create) >= batch_size:
                    NumberFrequencyStats.objects.bulk_create(
                        stats_to_create, ignore_conflicts=True
                    )
                    stats_to_create = []

        # Lưu các bản ghi còn lại
        if stats_to_create:
            NumberFrequencyStats.objects.bulk_create(
                stats_to_create, ignore_conflicts=True
            )

    def extract_two_digit_numbers(self, text):
        """
        Trích xuất chính xác 2 số cuối từ mỗi giải
        Args:
            text: Chuỗi kết quả của giải
        Returns:
            List các số 2 chữ số
        """
        if not text:
            return []

        # Nếu text là số, chuyển thành chuỗi
        if isinstance(text, (int, float)):
            text = str(int(text))

        # Xử lý khi text là chuỗi
        if isinstance(text, str):
            # Loại bỏ khoảng trắng, dấu phẩy và các ký tự không phải số
            text = "".join(c for c in text if c.isdigit() or c in [" ", ",", ";"])

            # Tách các số theo khoảng trắng, dấu phẩy hoặc dấu chấm phẩy
            number_list = []
            for separator in [" ", ",", ";"]:
                if separator in text:
                    number_list = [
                        x.strip() for x in text.split(separator) if x.strip()
                    ]
                    break

            # Nếu không có dấu phân cách, xem như một số duy nhất
            if not number_list and text.strip():
                number_list = [text.strip()]

            # Lấy 2 số cuối của mỗi số
            result = []
            for num in number_list:
                if len(num) >= 2:
                    result.append(num[-2:])

            return result

        return []

    def get_monthly_frequency_table(self, year, month, day_range=31):
        """Tạo bảng tần suất theo tháng"""
        # Xác định ngày bắt đầu và kết thúc
        end_date = timezone.now().date()
        if month and year:
            # Nếu chọn tháng cụ thể, lấy ngày cuối cùng của tháng đó
            _, last_day = calendar.monthrange(year, month)
            end_date = datetime(year, month, last_day).date()

        start_date = end_date - timedelta(days=day_range - 1)

        # Tạo danh sách các ngày cần hiển thị
        date_list = []
        current_date = start_date
        while current_date <= end_date:
            date_list.append(current_date)
            current_date += timedelta(days=1)

        # Lấy dữ liệu tần suất từ model
        frequency_data = (
            NumberFrequencyStats.objects.filter(date__range=(start_date, end_date))
            .values("number", "date")
            .order_by("date")
        )

        # Tạo từ điển lưu tần suất: {number: {date: count}}
        frequency_dict = defaultdict(lambda: defaultdict(int))
        for item in frequency_data:
            frequency_dict[item["number"]][item["date"]] = 1

        # Tạo dữ liệu bảng
        table_data = []
        for number in range(100):  # 00-99
            number_str = f"{number:02d}"
            row_data = {"number": number_str}
            row_total = 0

            # Thêm dữ liệu cho mỗi ngày
            for date in date_list:
                count = frequency_dict[number_str][date]
                row_data[date.strftime("%d/%m")] = count
                row_total += count

            row_data["total"] = row_total

            # Chỉ thêm số có xuất hiện ít nhất 1 lần
            if row_total > 0:
                table_data.append(row_data)

        # Sắp xếp theo số
        table_data.sort(key=lambda x: x["number"])

        return {
            "table_data": table_data,
            "date_list": date_list,
            "start_date": start_date,
            "end_date": end_date,
        }

    def get_day_of_month_frequency_table(self, year, month):
        """Tạo bảng tần suất theo ngày trong tháng"""
        # Lọc dữ liệu theo năm và tháng
        query_filter = {}
        if year:
            query_filter["year"] = year
        if month:
            query_filter["month"] = month

        # Lấy dữ liệu tần suất
        frequency_data = NumberFrequencyStats.objects.filter(**query_filter)

        # Đếm số lần xuất hiện cho mỗi số theo ngày trong tháng
        data = (
            frequency_data.values("number", "day_of_month")
            .annotate(count=Count("id"))
            .order_by("number", "day_of_month")
        )

        # Chuyển đổi dữ liệu sang định dạng bảng
        number_day_counts = defaultdict(lambda: defaultdict(int))
        for item in data:
            number_day_counts[item["number"]][item["day_of_month"]] = item["count"]

        # Tạo dữ liệu bảng
        table_data = []
        for number in range(100):  # 00-99
            number_str = f"{number:02d}"
            row_data = {"number": number_str}
            row_total = 0

            # Thêm dữ liệu cho mỗi ngày trong tháng
            for day in range(1, 32):  # 1-31
                count = number_day_counts[number_str][day]
                row_data[day] = count
                row_total += count

            row_data["total"] = row_total

            # Chỉ thêm số có xuất hiện ít nhất 1 lần
            if row_total > 0:
                table_data.append(row_data)

        # Sắp xếp theo số
        table_data.sort(key=lambda x: x["number"])

        return {
            "table_data": table_data,
            "days": range(1, 32),
        }

    def get_day_of_week_frequency_table(self, year, month):
        """Tạo bảng tần suất theo thứ trong tuần"""
        # Lọc dữ liệu theo năm và tháng
        query_filter = {}
        if year:
            query_filter["year"] = year
        if month:
            query_filter["month"] = month

        # Lấy dữ liệu tần suất
        frequency_data = NumberFrequencyStats.objects.filter(**query_filter)

        # Đếm số lần xuất hiện cho mỗi số theo thứ trong tuần
        data = (
            frequency_data.values("number", "day_of_week")
            .annotate(count=Count("id"))
            .order_by("number", "day_of_week")
        )

        # Chuyển đổi dữ liệu sang định dạng bảng
        number_day_counts = defaultdict(lambda: defaultdict(int))
        for item in data:
            number_day_counts[item["number"]][item["day_of_week"]] = item["count"]

        # Tạo dữ liệu bảng
        table_data = []
        for number in range(100):  # 00-99
            number_str = f"{number:02d}"
            row_data = {"number": number_str}
            row_total = 0

            # Thêm dữ liệu cho mỗi thứ trong tuần (0-6: Thứ 2 đến Chủ nhật)
            for day in range(7):
                count = number_day_counts[number_str][day]
                row_data[day] = count
                row_total += count

            row_data["total"] = row_total

            # Chỉ thêm số có xuất hiện ít nhất 1 lần
            if row_total > 0:
                table_data.append(row_data)

        # Sắp xếp theo số
        table_data.sort(key=lambda x: x["number"])

        return {
            "table_data": table_data,
            "days_of_week": range(7),
        }


class NumberFrequencyApiView(View):
    """API để xuất dữ liệu tần suất dưới dạng JSON"""

    def get(self, request):
        # Lấy các tham số từ request
        view_type = request.GET.get("view_type", "month")
        year = int(request.GET.get("year", timezone.now().year))
        month = int(request.GET.get("month", timezone.now().month))
        day_range = int(request.GET.get("day_range", 31))

        # Gọi hàm phù hợp để lấy dữ liệu
        view_handler = NumberFrequencyView()
        if view_type == "month":
            data = view_handler.get_monthly_frequency_table(year, month, day_range)
        elif view_type == "day_of_month":
            data = view_handler.get_day_of_month_frequency_table(year, month)
        elif view_type == "day_of_week":
            data = view_handler.get_day_of_week_frequency_table(year, month)
        else:
            return JsonResponse({"error": "Invalid view type"}, status=400)

        # Chuyển đổi dữ liệu để phù hợp với JSON
        json_data = {
            "table_data": data.get("table_data", []),
            "metadata": {k: v for k, v in data.items() if k != "table_data"},
        }

        return JsonResponse(json_data)


class NumberFrequencyHeatmapView(View):
    """View để hiển thị heatmap của tần suất số"""

    template_name = "results/number_frequency_heatmap.html"

    def get(self, request):
        # Lấy các tham số từ request
        year = int(request.GET.get("year", timezone.now().year))
        month = int(request.GET.get("month", timezone.now().month))

        # Tạo context
        context = {
            "year": year,
            "month": month,
            "years": range(timezone.now().year - 5, timezone.now().year + 1),
            "months": range(1, 13),
        }

        # Lấy dữ liệu heatmap
        heatmap_data = self.get_heatmap_data(year, month)
        context.update(heatmap_data)

        return render(request, self.template_name, context)

    def get_heatmap_data(self, year, month):
        """Tạo dữ liệu heatmap cho tần suất số"""
        # Lọc dữ liệu theo năm và tháng
        query_filter = {}
        if year:
            query_filter["year"] = year
        if month:
            query_filter["month"] = month

        # Lấy dữ liệu tần suất
        frequency_data = NumberFrequencyStats.objects.filter(**query_filter)

        # Đếm số lần xuất hiện cho mỗi số
        data = (
            frequency_data.values("number")
            .annotate(count=Count("id"))
            .order_by("number")
        )

        # Tạo heatmap data
        heatmap_data = []
        for i in range(10):  # Rows (0-9 cho chữ số đầu tiên)
            row = []
            for j in range(10):  # Columns (0-9 cho chữ số thứ hai)
                number = f"{i}{j}"
                count = next(
                    (item["count"] for item in data if item["number"] == number), 0
                )
                row.append({"number": number, "count": count})
            heatmap_data.append(row)

        # Tính giá trị max để tạo thang màu
        max_count = max(
            [item["count"] for row in heatmap_data for item in row], default=0
        )

        return {
            "heatmap_data": heatmap_data,
            "max_count": max_count,
        }


# views.py (bổ sung thêm)

import csv

from django.contrib import messages
from django.core.paginator import Paginator
from django.db import transaction
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy

from .forms import BulkImportForm, NumberFrequencyStatsForm
from .models import KetQuaXoSo, NumberFrequencyStats


class NumberFrequencyStatsListView(ListView):
    """View để hiển thị danh sách dữ liệu tần suất số"""

    model = NumberFrequencyStats
    template_name = "results/number_frequency_stats_list.html"
    context_object_name = "stats"
    paginate_by = 50

    def get_queryset(self):
        queryset = NumberFrequencyStats.objects.all()

        # Lọc theo ngày
        start_date = self.request.GET.get("start_date")
        end_date = self.request.GET.get("end_date")
        if start_date:
            try:
                start_date = datetime.strptime(start_date, "%Y-%m-%d").date()
                queryset = queryset.filter(date__gte=start_date)
            except ValueError:
                pass
        if end_date:
            try:
                end_date = datetime.strptime(end_date, "%Y-%m-%d").date()
                queryset = queryset.filter(date__lte=end_date)
            except ValueError:
                pass

        # Lọc theo số
        number = self.request.GET.get("number")
        if number:
            queryset = queryset.filter(number=number)

        # Lọc theo loại giải
        prize_type = self.request.GET.get("prize_type")
        if prize_type == "special":
            queryset = queryset.filter(appeared_in_special=True)
        elif prize_type == "first":
            queryset = queryset.filter(appeared_in_first=True)
        elif prize_type == "other":
            queryset = queryset.filter(appeared_in_other=True)

        return queryset.order_by("-date", "number")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Thêm các tham số lọc vào context
        context["start_date"] = self.request.GET.get("start_date", "")
        context["end_date"] = self.request.GET.get("end_date", "")
        context["number"] = self.request.GET.get("number", "")
        context["prize_type"] = self.request.GET.get("prize_type", "")

        # Thêm thông tin tổng hợp
        queryset = self.get_queryset()
        context["total_records"] = queryset.count()
        context["total_dates"] = queryset.values("date").distinct().count()
        context["total_numbers"] = queryset.values("number").distinct().count()

        return context


class NumberFrequencyStatsCreateView(CreateView):
    """View để tạo mới dữ liệu tần suất số"""

    model = NumberFrequencyStats
    form_class = NumberFrequencyStatsForm
    template_name = "results/number_frequency_stats_form.html"
    success_url = reverse_lazy("number_frequency_stats_list")

    def form_valid(self, form):
        # Tự động tính toán các giá trị liên quan đến ngày
        date = form.cleaned_data.get("date")
        if date:
            form.instance.day_of_week = date.weekday()
            form.instance.day_of_month = date.day
            form.instance.week_of_month = (date.day - 1) // 7 + 1
            form.instance.month = date.month
            form.instance.year = date.year

        messages.success(self.request, "Đã tạo bản ghi tần suất số thành công!")
        return super().form_valid(form)


class NumberFrequencyStatsUpdateView(UpdateView):
    """View để cập nhật dữ liệu tần suất số"""

    model = NumberFrequencyStats
    form_class = NumberFrequencyStatsForm
    template_name = "results/number_frequency_stats_form.html"
    success_url = reverse_lazy("number_frequency_stats_list")

    def form_valid(self, form):
        # Tự động cập nhật các giá trị liên quan đến ngày
        date = form.cleaned_data.get("date")
        if date:
            form.instance.day_of_week = date.weekday()
            form.instance.day_of_month = date.day
            form.instance.week_of_month = (date.day - 1) // 7 + 1
            form.instance.month = date.month
            form.instance.year = date.year

        messages.success(self.request, "Đã cập nhật bản ghi tần suất số thành công!")
        return super().form_valid(form)


class NumberFrequencyStatsBulkDeleteView(View):
    """View để xóa toàn bộ dữ liệu tần suất số"""

    template_name = "results/number_frequency_stats_bulk_delete.html"
    model = NumberFrequencyStats

    def get(self, request):
        # Thống kê dữ liệu hiện tại
        total_records = NumberFrequencyStats.objects.count()
        date_range = NumberFrequencyStats.objects.aggregate(
            min_date=models.Min("date"), max_date=models.Max("date")
        )

        context = {
            "total_records": total_records,
            "min_date": date_range["min_date"],
            "max_date": date_range["max_date"],
        }

        return render(request, self.template_name, context)

    def post(self, request):
        """Xử lý xóa dữ liệu"""
        action = request.POST.get("action")

        if action == "delete_all":
            try:
                # Đếm số bản ghi trước khi xóa
                total_records = NumberFrequencyStats.objects.count()

                # Xóa toàn bộ dữ liệu
                with transaction.atomic():
                    NumberFrequencyStats.objects.all().delete()

                messages.success(
                    request,
                    f"Đã xóa thành công {total_records} bản ghi dữ liệu tần suất số!",
                )

            except Exception as e:
                messages.error(request, f"Lỗi khi xóa dữ liệu: {str(e)}")

        elif action == "delete_range":
            # Xóa theo khoảng thời gian
            start_date = request.POST.get("start_date")
            end_date = request.POST.get("end_date")

            if start_date and end_date:
                try:
                    start_date = datetime.strptime(start_date, "%Y-%m-%d").date()
                    end_date = datetime.strptime(end_date, "%Y-%m-%d").date()

                    # Đếm số bản ghi sẽ bị xóa
                    records_to_delete = NumberFrequencyStats.objects.filter(
                        date__range=(start_date, end_date)
                    ).count()

                    # Xóa dữ liệu trong khoảng thời gian
                    with transaction.atomic():
                        NumberFrequencyStats.objects.filter(
                            date__range=(start_date, end_date)
                        ).delete()

                    messages.success(
                        request,
                        f"Đã xóa thành công {records_to_delete} bản ghi từ {start_date} đến {end_date}!",
                    )

                except ValueError:
                    messages.error(request, "Định dạng ngày không hợp lệ!")
                except Exception as e:
                    messages.error(request, f"Lỗi khi xóa dữ liệu: {str(e)}")
            else:
                messages.error(
                    request, "Vui lòng chọn cả ngày bắt đầu và ngày kết thúc!"
                )

        return redirect("number_frequency_stats_bulk_delete")


class NumberFrequencyStatsDeleteView(DeleteView):
    """View để xóa dữ liệu tần suất số"""

    model = NumberFrequencyStats
    template_name = "results/number_frequency_stats_confirm_delete.html"
    success_url = reverse_lazy("number_frequency_stats_list")

    def delete(self, request, *args, **kwargs):
        messages.success(request, "Đã xóa bản ghi tần suất số thành công!")
        return super().delete(request, *args, **kwargs)


class NumberFrequencyStatsBulkImportView(View):
    """View để nhập dữ liệu hàng loạt"""

    template_name = "results/number_frequency_stats_bulk_import.html"

    def get(self, request):
        form = BulkImportForm()
        return render(request, self.template_name, {"form": form})

    def post(self, request):
        form = BulkImportForm(request.POST, request.FILES)
        if form.is_valid():
            # Xử lý file CSV
            if "csv_file" in request.FILES:
                try:
                    csv_file = request.FILES["csv_file"]
                    decoded_file = csv_file.read().decode("utf-8").splitlines()
                    reader = csv.DictReader(decoded_file)

                    # Tạo batch dữ liệu để nhập hàng loạt
                    batch = []
                    success_count = 0
                    error_count = 0

                    for row in reader:
                        try:
                            # Chuyển đổi dữ liệu từ CSV
                            date = datetime.strptime(row["date"], "%Y-%m-%d").date()

                            # Tạo instance của NumberFrequencyStats
                            stat = NumberFrequencyStats(
                                number=row["number"],
                                date=date,
                                appeared_in_special=row.get(
                                    "appeared_in_special", "False"
                                ).lower()
                                == "true",
                                appeared_in_first=row.get(
                                    "appeared_in_first", "False"
                                ).lower()
                                == "true",
                                appeared_in_other=row.get(
                                    "appeared_in_other", "False"
                                ).lower()
                                == "true",
                                day_of_week=date.weekday(),
                                day_of_month=date.day,
                                week_of_month=(date.day - 1) // 7 + 1,
                                month=date.month,
                                year=date.year,
                            )

                            batch.append(stat)
                            success_count += 1

                            # Thực hiện bulk create mỗi 1000 bản ghi
                            if len(batch) >= 1000:
                                NumberFrequencyStats.objects.bulk_create(
                                    batch, ignore_conflicts=True
                                )
                                batch = []

                        except Exception as e:
                            error_count += 1
                            continue

                    # Thực hiện bulk create cho các bản ghi còn lại
                    if batch:
                        NumberFrequencyStats.objects.bulk_create(
                            batch, ignore_conflicts=True
                        )

                    messages.success(
                        request,
                        f"Đã nhập thành công {success_count} bản ghi. Có {error_count} lỗi.",
                    )
                    return redirect("number_frequency_stats_list")

                except Exception as e:
                    messages.error(request, f"Lỗi khi xử lý file CSV: {str(e)}")

            # Xử lý dữ liệu từ KetQuaXoSo
            elif form.cleaned_data.get("import_from_ketquaxoso"):
                start_date = form.cleaned_data.get("start_date")
                end_date = form.cleaned_data.get("end_date")

                if not start_date:
                    start_date = KetQuaXoSo.objects.order_by("ngay").first().ngay
                if not end_date:
                    end_date = KetQuaXoSo.objects.order_by("-ngay").first().ngay

                # Gọi hàm cập nhật dữ liệu
                num_created = self.update_frequency_stats(start_date, end_date)

                messages.success(
                    request, f"Đã nhập thành công {num_created} bản ghi từ KetQuaXoSo."
                )
                return redirect("number_frequency_stats_list")

        return render(request, self.template_name, {"form": form})

    def update_frequency_stats(self, start_date, end_date):
        """Cập nhật dữ liệu tần suất từ KetQuaXoSo"""
        # Lấy kết quả xổ số trong khoảng thời gian
        results = KetQuaXoSo.objects.filter(
            ngay__range=(start_date, end_date)
        ).order_by("ngay")

        # Tạo các bản ghi NumberFrequencyStats
        batch_size = 1000
        stats_to_create = []
        num_created = 0

        with transaction.atomic():
            # Xóa dữ liệu cũ trong khoảng thời gian này
            NumberFrequencyStats.objects.filter(
                date__range=(start_date, end_date)
            ).delete()

            for result in results:
                # Khởi tạo danh sách các số cho các loại giải
                all_numbers = set()  # Sử dụng set để tránh trùng lặp
                special_prize = set()
                first_prize = set()
                other_prizes = set()

                # Lấy giải đặc biệt (chỉ lấy 2 số cuối)
                if hasattr(result, "giai_db") and result.giai_db:
                    db_number = (
                        result.giai_db.strip()[-2:]
                        if len(result.giai_db.strip()) >= 2
                        else None
                    )
                    if db_number:
                        special_prize.add(db_number)
                        all_numbers.add(db_number)

                # Lấy giải nhất (chỉ lấy 2 số cuối)
                if hasattr(result, "giai_1") and result.giai_1:
                    g1_number = (
                        result.giai_1.strip()[-2:]
                        if len(result.giai_1.strip()) >= 2
                        else None
                    )
                    if g1_number:
                        first_prize.add(g1_number)
                        all_numbers.add(g1_number)

                # Lấy chính xác 2 số cuối của các giải khác
                for field_name in [
                    "giai_2",
                    "giai_3",
                    "giai_4",
                    "giai_5",
                    "giai_6",
                    "giai_7",
                ]:
                    field_value = getattr(result, field_name, None)
                    if field_value:
                        # Tách các số trong giải
                        numbers_in_field = []

                        # Nếu là giải 3, 5 (nhiều số), tách theo khoảng trắng hoặc dấu phẩy
                        for separator in [" ", ",", ";"]:
                            if separator in field_value:
                                numbers_in_field = [
                                    x.strip()
                                    for x in field_value.split(separator)
                                    if x.strip()
                                ]
                                break

                        # Nếu không có dấu phân cách, xem như một số duy nhất
                        if not numbers_in_field and field_value.strip():
                            numbers_in_field = [field_value.strip()]

                        # Lấy 2 số cuối của mỗi số
                        for num in numbers_in_field:
                            if len(num) >= 2:
                                two_digit = num[-2:]
                                other_prizes.add(two_digit)
                                all_numbers.add(two_digit)

                # In số lượng số tìm thấy (để debug)
                print(f"Ngày {result.ngay}: Tìm thấy {len(all_numbers)} số 2 chữ số")

                # Tính week_of_month
                week_of_month = (result.ngay.day - 1) // 7 + 1

                # Tạo bản ghi cho mỗi số
                for number in all_numbers:
                    stats_to_create.append(
                        NumberFrequencyStats(
                            number=number,
                            date=result.ngay,
                            appeared_in_special=(number in special_prize),
                            appeared_in_first=(number in first_prize),
                            appeared_in_other=(number in other_prizes),
                            day_of_week=result.ngay.weekday(),
                            day_of_month=result.ngay.day,
                            week_of_month=week_of_month,
                            month=result.ngay.month,
                            year=result.ngay.year,
                        )
                    )
                    num_created += 1

                    # Lưu theo batch để tránh tiêu tốn bộ nhớ
                    if len(stats_to_create) >= batch_size:
                        NumberFrequencyStats.objects.bulk_create(
                            stats_to_create, ignore_conflicts=True
                        )
                        stats_to_create = []

            # Lưu các bản ghi còn lại
            if stats_to_create:
                NumberFrequencyStats.objects.bulk_create(
                    stats_to_create, ignore_conflicts=True
                )

        return num_created

    def extract_two_digit_numbers(self, text):
        """Trích xuất tất cả số 2 chữ số từ chuỗi"""
        if not text:
            return []

        # Nếu text là số, chuyển thành chuỗi
        if isinstance(text, (int, float)):
            text = str(int(text))

        # Xử lý khi text là chuỗi
        if isinstance(text, str):
            # Loại bỏ ký tự không phải số
            digits_only = "".join(c for c in text if c.isdigit())

            # Trích xuất tất cả cặp số 2 chữ số liên tiếp
            result = []
            for i in range(0, len(digits_only) - 1, 2):
                if i + 2 <= len(digits_only):
                    result.append(digits_only[i : i + 2])

            # Đảm bảo lấy 2 chữ số cuối cùng
            if len(digits_only) >= 2:
                result.append(digits_only[-2:])

            return list(set(result))  # Loại bỏ trùng lặp

        return []


class NumberFrequencyStatsExportView(View):
    """View để xuất dữ liệu tần suất số ra file CSV"""

    def get(self, request):
        # Lấy các tham số lọc từ request
        start_date = request.GET.get("start_date")
        end_date = request.GET.get("end_date")
        number = request.GET.get("number")
        prize_type = request.GET.get("prize_type")

        # Tạo queryset với các điều kiện lọc
        queryset = NumberFrequencyStats.objects.all()

        if start_date:
            try:
                start_date = datetime.strptime(start_date, "%Y-%m-%d").date()
                queryset = queryset.filter(date__gte=start_date)
            except ValueError:
                pass
        if end_date:
            try:
                end_date = datetime.strptime(end_date, "%Y-%m-%d").date()
                queryset = queryset.filter(date__lte=end_date)
            except ValueError:
                pass
        if number:
            queryset = queryset.filter(number=number)
        if prize_type == "special":
            queryset = queryset.filter(appeared_in_special=True)
        elif prize_type == "first":
            queryset = queryset.filter(appeared_in_first=True)
        elif prize_type == "other":
            queryset = queryset.filter(appeared_in_other=True)

        # Sắp xếp dữ liệu
        queryset = queryset.order_by("-date", "number")

        # Tạo response CSV
        response = HttpResponse(content_type="text/csv")
        response["Content-Disposition"] = (
            'attachment; filename="number_frequency_stats.csv"'
        )

        # Tạo writer CSV
        writer = csv.writer(response)
        writer.writerow(
            [
                "number",
                "date",
                "appeared_in_special",
                "appeared_in_first",
                "appeared_in_other",
                "day_of_week",
                "day_of_month",
                "week_of_month",
                "month",
                "year",
            ]
        )

        # Ghi dữ liệu
        for stat in queryset:
            writer.writerow(
                [
                    stat.number,
                    stat.date.strftime("%Y-%m-%d"),
                    stat.appeared_in_special,
                    stat.appeared_in_first,
                    stat.appeared_in_other,
                    stat.day_of_week,
                    stat.day_of_month,
                    stat.week_of_month,
                    stat.month,
                    stat.year,
                ]
            )

        return response


class NumberFrequencyStatsSyncView(View):
    """View để đồng bộ dữ liệu tần suất từ KetQuaXoSo mới nhất"""

    def get(self, request):
        # Lấy ngày cuối cùng đã lưu
        last_date = (
            NumberFrequencyStats.objects.order_by("-date")
            .values_list("date", flat=True)
            .first()
        )

        if not last_date:
            messages.warning(
                request,
                "Không tìm thấy dữ liệu tần suất. Vui lòng nhập dữ liệu ban đầu.",
            )
            return redirect("number_frequency_stats_bulk_import")

        # Lấy kết quả xổ số mới nhất
        latest_result_date = (
            KetQuaXoSo.objects.order_by("-ngay").values_list("ngay", flat=True).first()
        )

        if not latest_result_date:
            messages.warning(request, "Không tìm thấy dữ liệu kết quả xổ số.")
            return redirect("number_frequency_stats_list")

        # Nếu đã đồng bộ
        if last_date >= latest_result_date:
            messages.info(
                request, "Dữ liệu tần suất đã được cập nhật đến ngày mới nhất."
            )
            return redirect("number_frequency_stats_list")

        # Đồng bộ dữ liệu mới
        start_date = last_date + timedelta(days=1)
        end_date = latest_result_date

        importer = NumberFrequencyStatsBulkImportView()
        num_created = importer.update_frequency_stats(start_date, end_date)

        messages.success(
            request,
            f"Đã đồng bộ thành công {num_created} bản ghi từ {start_date} đến {end_date}.",
        )
        return redirect("number_frequency_stats_list")


def sigmoid(x):
    """Hàm sigmoid để chuẩn hóa giá trị"""
    return 1 / (1 + math.exp(-x))


from django.shortcuts import get_object_or_404, render

from results.models import PredictionModel, StateAnalysis, StatePrediction
from results.services.hmm_service import HMMService
from results.services.lstm_service import LSTMService


class StateAnalysisListView(ListView):
    """View hiển thị danh sách phân tích state"""

    model = StateAnalysis
    template_name = "results/state_analysis/list.html"
    context_object_name = "analyses"
    paginate_by = 50

    def get_queryset(self):
        queryset = StateAnalysis.objects.select_related("source_record")

        # Filter theo ngày nếu có
        date_from = self.request.GET.get("date_from")
        date_to = self.request.GET.get("date_to")

        if date_from:
            queryset = queryset.filter(ngay__gte=date_from)
        if date_to:
            queryset = queryset.filter(ngay__lte=date_to)

        return queryset.order_by("-ngay")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Thống kê state
        total_states = StateAnalysis.objects.count()
        unique_states = (
            StateAnalysis.objects.values_list("state", flat=True).distinct().count()
        )

        # State frequency
        from django.db.models import Count

        state_freq = (
            StateAnalysis.objects.values("state")
            .annotate(count=Count("state"))
            .order_by("-count")[:10]
        )

        context.update(
            {
                "total_states": total_states,
                "unique_states": unique_states,
                "state_frequency": state_freq,
                "date_from": self.request.GET.get("date_from", ""),
                "date_to": self.request.GET.get("date_to", ""),
            }
        )

        return context


class PredictionModelListView(ListView):
    """View hiển thị danh sách models"""

    model = PredictionModel
    template_name = "results/prediction_models/list.html"
    context_object_name = "models"
    paginate_by = 20

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Thống kê models
        from django.db.models import Avg, Count

        model_stats = PredictionModel.objects.values("model_type").annotate(
            count=Count("id"), avg_accuracy=Avg("accuracy")
        )

        context["model_stats"] = model_stats
        return context


def predict_next_state(request):
    """API endpoint để dự đoán state tiếp theo"""
    if request.method != "POST":
        return JsonResponse({"error": "Method not allowed"}, status=405)

    try:
        data = json.loads(request.body)
        model_type = data.get("model_type", "markov")
        current_state = data.get("current_state")
        sequence_length = data.get("sequence_length", 10)

        if not current_state:
            return JsonResponse({"error": "Current state is required"}, status=400)

        # Lấy model đang hoạt động
        model_instance = PredictionModel.objects.get_active_model(model_type)
        if not model_instance:
            return JsonResponse(
                {"error": f"No active {model_type} model found"}, status=404
            )

        # Khởi tạo service tương ứng
        if model_type == "markov":
            service = HMMService()
            model_data = service.load_model(model_instance.file_path)
            if model_data:
                predicted_state, confidence = service.predict_with_markov(
                    model_data["model"], current_state
                )
            else:
                return JsonResponse({"error": "Failed to load model"}, status=500)

        elif model_type == "hmm":
            service = HMMService()
            model_data = service.load_model(model_instance.file_path)
            if model_data:
                predicted_state, confidence = service.predict_with_hmm(
                    model_data["model"], current_state
                )
            else:
                return JsonResponse({"error": "Failed to load model"}, status=500)

        elif model_type == "lstm":
            service = LSTMService()
            model_data = service.load_lstm_model(model_instance.file_path)
            if model_data:
                # Cần lấy sequence gần đây cho LSTM
                recent_states = StateAnalysis.objects.order_by("-ngay")[
                    :sequence_length
                ]
                recent_states_list = [s.state for s in reversed(recent_states)]

                predicted_state, confidence = service.predict_with_lstm(
                    model_data, recent_states_list
                )
            else:
                return JsonResponse({"error": "Failed to load model"}, status=500)

        else:
            return JsonResponse({"error": "Invalid model type"}, status=400)

        # Lưu prediction
        if predicted_state:
            StatePrediction.objects.create_prediction(
                model_instance=model_instance,
                current_state=current_state,
                predicted_state=predicted_state,
                confidence=confidence,
                metadata={
                    "model_type": model_type,
                    "sequence_length": (
                        sequence_length if model_type == "lstm" else None
                    ),
                },
            )

        return JsonResponse(
            {
                "predicted_state": predicted_state,
                "confidence": confidence,
                "model_type": model_type,
                "model_accuracy": model_instance.accuracy,
            }
        )

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


def model_performance(request, model_id):
    """View hiển thị performance của model"""
    from django.shortcuts import get_object_or_404

    from results.models import PredictionModel, StatePrediction

    model_instance = get_object_or_404(PredictionModel, id=model_id)

    # Lấy predictions gần đây - KHÔNG slice trước khi filter
    all_recent_predictions = StatePrediction.objects.filter(
        model=model_instance
    ).order_by("-created_at")

    # Filter predictions có kết quả trước khi slice
    predictions_with_results = all_recent_predictions.filter(actual_state__isnull=False)

    # Sau đó mới slice để lấy 100 records gần đây nhất
    recent_predictions = all_recent_predictions[:100]

    correct_predictions = predictions_with_results.filter(is_correct=True).count()

    total_predictions = predictions_with_results.count()
    current_accuracy = (
        correct_predictions / total_predictions if total_predictions > 0 else 0
    )

    context = {
        "model": model_instance,
        "recent_predictions": recent_predictions,
        "current_accuracy": current_accuracy * 100,  # Convert to percentage
        "correct_predictions": correct_predictions,
        "total_predictions": total_predictions,
    }

    return render(request, "results/prediction_models/performance.html", context)


def state_transition_chart(request):
    """API để lấy dữ liệu biểu đồ chuyển đổi state"""
    # Lấy dữ liệu transition

    # Lấy các state liên tiếp
    states = StateAnalysis.objects.order_by("ngay")
    transitions = defaultdict(lambda: defaultdict(int))

    prev_state = None
    for state_analysis in states:
        if prev_state:
            transitions[prev_state][state_analysis.state] += 1
        prev_state = state_analysis.state

    # Chuyển đổi sang format cho biểu đồ
    nodes = []
    links = []

    all_states = set()
    for from_state, to_states in transitions.items():
        all_states.add(from_state)
        for to_state in to_states.keys():
            all_states.add(to_state)

    # Tạo nodes
    for state in sorted(all_states):
        nodes.append({"id": state, "name": f"State {state}"})

    # Tạo links
    for from_state, to_states in transitions.items():
        for to_state, count in to_states.items():
            links.append({"source": from_state, "target": to_state, "value": count})

    return JsonResponse({"nodes": nodes, "links": links})


from datetime import timedelta

from django.http import JsonResponse
from django.utils import timezone


def get_2_digit_numbers(request):
    """Extract all two-digit numbers from lottery results."""
    selected_date = request.GET.get("selected_date")
    if request.method == "POST":
        try:
            selected_date = datetime.strptime(
                request.POST.get("selected_date", ""), "%Y-%m-%d"
            ).date()
            if selected_date > date.today():
                selected_date = date.today()
                messages.warning(
                    request, "Không thể dự đoán tương lai. Sử dụng ngày hôm nay."
                )
        except (ValueError, TypeError):
            messages.warning(request, "Ngày không hợp lệ. Sử dụng ngày hôm nay.")

    result = KetQuaXoSo.objects.filter(ngay=selected_date).first()
    actual_numbers = set(result.get_all_2digit_numbers()) if result else set()

    numbers = []
    # Process giai_7 (assumed to contain two-digit numbers)
    try:
        # Process other prize fields to extract last two digits
        prize_fields = [
            result.giai_db,
            result.giai_1,
            result.giai_2,
            result.giai_3,
            result.giai_4,
            result.giai_5,
            result.giai_6,
            result.giai_7,
        ]
        for giai in prize_fields:
            if giai:  # Check if field is not empty/None
                # Split by commas or spaces, handle multiple separators
                for num in giai.replace(",", " ").split():
                    if num.isdigit() and len(num) >= 2:
                        numbers.append(
                            num[-2:].zfill(2)
                        )  # Ensure two-digit format (e.g., "1" -> "01")
        # actual_numbers = list(set(numbers))
        return render(
            request,
            "results/2-digit.html",
            {
                "selected_date": selected_date,
                "results": result,
                "actual_numbers": actual_numbers,
            },
        )
    except Exception as e:
        messages.error(request, f"Error processing results: {str(e)}")
        return render(
            request,
            "results/2-digit.html",
            {
                "selected_date": selected_date,
                "results": result,
                "actual_numbers": set(),
            },
        )
