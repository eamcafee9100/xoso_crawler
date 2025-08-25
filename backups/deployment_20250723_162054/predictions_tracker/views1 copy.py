import json
import logging
from datetime import date, datetime, timedelta
from typing import Any, Dict, List

import numpy as np
from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.core.serializers.json import DjangoJSONEncoder
from django.db.models import Avg, Count, Q, Sum
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

from results.models import KetQuaXoSo

from .core.services.DataService import data_service
from .core.services.MLModelService import ml_model_service
from .core.services.TrackingService import tracking_service
from .management.commands.load_prediction_methods import get_all_method_classes
from .models import (
    CycleMethodParticipation,
    DailyTrackingSession,
    MethodPredictionResult,
    PredictionCycle,
    PredictionMethod,
    PredictionStrategy,
    TrackingEvaluation,
)

logger = logging.getLogger(__name__)

import calendar
import json
from collections import Counter, defaultdict
from datetime import date, timedelta

import numpy as np
from django.db.models import Avg, Count, Q
from django.shortcuts import render
from django.utils import timezone
from django.views.generic import TemplateView
from sklearn.ensemble import GradientBoostingClassifier, RandomForestClassifier
from sklearn.metrics import classification_report
from sklearn.model_selection import cross_val_score
from sklearn.preprocessing import StandardScaler

from .models import (
    DailyTrackingSession,
    MethodPredictionResult,
    PredictionCycle,
    PredictionMethod,
    TrackingEvaluation,
)

# ==================== DASHBOARD VIEWS ====================


@login_required
def dashboard(request):
    """
    Dashboard tổng quan hệ thống tracking
    """
    try:
        # Lấy thống kê tổng quan
        total_cycles = PredictionCycle.objects.count()
        active_cycles = PredictionCycle.objects.filter(status="active").count()
        total_sessions = DailyTrackingSession.objects.count()
        completed_sessions = DailyTrackingSession.objects.filter(
            status="completed"
        ).count()

        # Chu kỳ đang hoạt động
        active_cycles_data = PredictionCycle.objects.filter(status="active").order_by(
            "-start_date"
        )[:5]

        # Session gần đây
        recent_sessions = DailyTrackingSession.objects.select_related("cycle").order_by(
            "-created_at"
        )[:10]

        # Thống kê hiệu suất
        recent_evaluations = TrackingEvaluation.objects.select_related(
            "method_result__method", "session__cycle"
        ).order_by("-created_at")[:20]

        # Tính average hit rate
        avg_hit_rate = (
            recent_evaluations.aggregate(avg_rate=Avg("hit_rate"))["avg_rate"] or 0
        )

        # Top performing methods
        method_performance = {}
        for eval in recent_evaluations:
            method_name = eval.method_result.method.name
            if method_name not in method_performance:
                method_performance[method_name] = {
                    "name": method_name,
                    "evaluations": 0,
                    "total_hit_rate": 0,
                    "total_wilson_score": 0,
                }

            method_performance[method_name]["evaluations"] += 1
            method_performance[method_name]["total_hit_rate"] += eval.hit_rate
            method_performance[method_name]["total_wilson_score"] += eval.wilson_score

        # Tính average và sort
        top_methods = []
        for method_name, data in method_performance.items():
            if data["evaluations"] > 0:
                avg_hit_rate = data["total_hit_rate"] / data["evaluations"]
                avg_wilson = data["total_wilson_score"] / data["evaluations"]
                top_methods.append(
                    {
                        "name": method_name,
                        "avg_hit_rate": round(avg_hit_rate, 2),
                        "avg_wilson_score": round(avg_wilson, 4),
                        "evaluations": data["evaluations"],
                    }
                )

        top_methods.sort(key=lambda x: x["avg_hit_rate"], reverse=True)

        context = {
            "total_cycles": total_cycles,
            "active_cycles": active_cycles,
            "total_sessions": total_sessions,
            "completed_sessions": completed_sessions,
            "completion_rate": round(
                (
                    (completed_sessions / total_sessions * 100)
                    if total_sessions > 0
                    else 0
                ),
                1,
            ),
            "active_cycles_data": active_cycles_data,
            "recent_sessions": recent_sessions,
            "recent_evaluations": recent_evaluations[:10],
            "avg_hit_rate": round(avg_hit_rate, 2),
            "top_methods": top_methods[:5],
            "page_title": "Dashboard - Prediction Tracker",
        }

        return render(request, "predictions_tracker/dashboard.html", context)

    except Exception as e:
        logger.error(f"Error in dashboard: {e}")
        messages.error(request, f"Lỗi tải dashboard: {str(e)}")
        return render(
            request,
            "predictions_tracker/dashboard.html",
            {"page_title": "Dashboard - Error", "error": str(e)},
        )


# ==================== CYCLE MANAGEMENT ====================


@login_required
def cycles_list(request):
    """
    Danh sách tất cả các chu kỳ
    """
    try:
        cycles = PredictionCycle.objects.all().order_by("-start_date")

        # Filtering
        status_filter = request.GET.get("status")
        if status_filter:
            cycles = cycles.filter(status=status_filter)

        # Pagination
        paginator = Paginator(cycles, 10)
        page = request.GET.get("page")
        cycles_page = paginator.get_page(page)

        # Thống kê cho mỗi cycle
        cycles_with_stats = []
        for cycle in cycles_page:
            sessions_count = cycle.daily_sessions.count()
            completed_sessions = cycle.daily_sessions.filter(status="completed").count()

            # Lấy summary từ service
            cycle_summary = tracking_service.get_cycle_summary(cycle)

            cycles_with_stats.append(
                {
                    "cycle": cycle,
                    "sessions_count": sessions_count,
                    "completed_sessions": completed_sessions,
                    "completion_rate": round(
                        (
                            (completed_sessions / sessions_count * 100)
                            if sessions_count > 0
                            else 0
                        ),
                        1,
                    ),
                    "summary": cycle_summary,
                }
            )

        context = {
            "cycles_with_stats": cycles_with_stats,
            "page_obj": cycles_page,
            "status_filter": status_filter,
            "status_choices": PredictionCycle.STATUS_CHOICES,
            "page_title": "Quản lý Chu kỳ",
        }

        return render(request, "predictions_tracker/cycles/list.html", context)

    except Exception as e:
        logger.error(f"Error in cycles_list: {e}")
        messages.error(request, f"Lỗi tải danh sách chu kỳ: {str(e)}")
        return render(
            request,
            "predictions_tracker/cycles/list.html",
            {"page_title": "Chu kỳ - Error", "error": str(e)},
        )


@login_required
def cycle_detail(request, cycle_id):
    """
    Chi tiết chu kỳ với thống kê đầy đủ
    """
    try:
        cycle = get_object_or_404(PredictionCycle, id=cycle_id)

        # Lấy tất cả sessions của cycle
        sessions = cycle.daily_sessions.all().order_by("-prediction_date")

        # Pagination cho sessions
        paginator = Paginator(sessions, 15)
        page = request.GET.get("page")
        sessions_page = paginator.get_page(page)

        # Lấy summary và comparison từ service
        cycle_summary = tracking_service.get_cycle_summary(cycle)
        method_comparison = tracking_service.get_method_comparison(cycle)

        # Lấy participations
        participations = cycle.cyclemethodparticipation_set.select_related(
            "method"
        ).all()

        # Thống kê theo ngày
        daily_stats = []
        for session in sessions_page:
            evaluations = session.evaluations.all()
            avg_hit_rate = (
                evaluations.aggregate(avg_rate=Avg("hit_rate"))["avg_rate"] or 0
            )

            daily_stats.append(
                {
                    "session": session,
                    "evaluations_count": evaluations.count(),
                    "avg_hit_rate": round(avg_hit_rate, 2),
                    "status_display": session.get_status_display(),
                    "tracking_progress": (
                        (session.current_tracking_day / cycle.tracking_days * 100)
                        if cycle.tracking_days > 0
                        else 0
                    ),
                }
            )

        context = {
            "cycle": cycle,
            "cycle_summary": cycle_summary,
            "method_comparison": method_comparison,
            "participations": participations,
            "daily_stats": daily_stats,
            "page_obj": sessions_page,
            "page_title": f"Chi tiết chu kỳ: {cycle.cycle_name}",
        }

        return render(request, "predictions_tracker/cycles/detail.html", context)

    except Exception as e:
        logger.error(f"Error in cycle_detail: {e}")
        messages.error(request, f"Lỗi tải chi tiết chu kỳ: {str(e)}")
        return redirect("predictions_tracker:cycles_list")


@login_required
def cycle_create(request):
    """
    Tạo chu kỳ mới
    """
    if request.method == "POST":
        try:
            # Lấy dữ liệu từ form
            cycle_name = request.POST.get("cycle_name")
            start_date = request.POST.get("start_date")
            end_date = request.POST.get("end_date")
            tracking_days = int(request.POST.get("tracking_days", 3))
            selected_methods = request.POST.getlist("methods")

            # Validate
            if not all([cycle_name, start_date, end_date]):
                messages.error(request, "Vui lòng điền đầy đủ thông tin bắt buộc")
                return render(
                    request,
                    "predictions_tracker/cycles/create.html",
                    {
                        "available_methods": PredictionMethod.objects.filter(
                            is_active=True
                        ),
                        "page_title": "Tạo chu kỳ mới",
                    },
                )

            # Tạo cycle
            cycle = PredictionCycle.objects.create(
                cycle_name=cycle_name,
                start_date=start_date,
                end_date=end_date,
                tracking_days=tracking_days,
                status="planning",
            )

            # Thêm methods vào cycle
            for method_id in selected_methods:
                method = PredictionMethod.objects.get(id=method_id)
                CycleMethodParticipation.objects.create(
                    cycle=cycle,
                    method=method,
                    is_ensemble_enabled=request.POST.get(f"ensemble_{method_id}")
                    == "on",
                    custom_weight=float(request.POST.get(f"weight_{method_id}", 1.0)),
                )

            messages.success(request, f"Đã tạo chu kỳ '{cycle_name}' thành công!")
            return redirect("predictions_tracker:cycle_detail", cycle_id=cycle.id)

        except Exception as e:
            logger.error(f"Error creating cycle: {e}")
            messages.error(request, f"Lỗi tạo chu kỳ: {str(e)}")

    # GET request
    available_methods = PredictionMethod.objects.filter(is_active=True)

    context = {"available_methods": available_methods, "page_title": "Tạo chu kỳ mới"}

    return render(request, "predictions_tracker/cycles/create.html", context)


# ==================== SESSION MANAGEMENT ====================


@login_required
def session_detail(request, session_id):
    """
    Chi tiết session theo dõi
    """
    try:
        session = get_object_or_404(DailyTrackingSession, id=session_id)

        # Lấy method results
        method_results = session.method_results.select_related("method").all()

        # Lấy evaluations
        evaluations = session.evaluations.select_related("method_result__method").all()

        # Cập nhật trạng thái tracking
        tracking_update = tracking_service.update_tracking_status(session)

        # Chuẩn bị dữ liệu cho biểu đồ
        chart_data = {
            "methods": [],
            "hit_rates": [],
            "wilson_scores": [],
            "confidence_scores": [],
        }
        method_stats = []
        for result in method_results:
            chart_data["methods"].append(result.method.name)
            chart_data["confidence_scores"].append(result.overall_confidence)

            # Lấy hit rate từ evaluations
            method_evaluations = evaluations.filter(method_result=result)
            avg_hit_rate = (
                method_evaluations.aggregate(avg_rate=Avg("hit_rate"))["avg_rate"] or 0
            )
            avg_wilson = (
                method_evaluations.aggregate(avg_wilson=Avg("wilson_score"))[
                    "avg_wilson"
                ]
                or 0
            )

            avg_hit_rate = (
                method_evaluations.aggregate(avg_rate=Avg("hit_rate"))["avg_rate"] or 0
            )
            avg_wilson = (
                method_evaluations.aggregate(avg_wilson=Avg("wilson_score"))[
                    "avg_wilson"
                ]
                or 0
            )
            method_stats.append(
                {
                    "result": result,
                    "avg_hit_rate": round(avg_hit_rate, 2),
                    "avg_wilson": round(avg_wilson, 4),
                    # ... các trường khác nếu cần
                }
            )
            chart_data["hit_rates"].append(round(avg_hit_rate, 2))
            chart_data["wilson_scores"].append(round(avg_wilson, 4))

        # Ensemble analysis data
        ensemble_data = {
            "recommendations": session.ensemble_recommendations[:10],
            "cycle_analysis": session.cycle_analysis_data,
            "gap_analysis": session.gap_analysis_data,
            "pattern_mining": session.pattern_mining_data,
        }

        context = {
            "session": session,
            "method_results": method_results,
            "method_stats": method_stats,
            "evaluations": evaluations,
            "tracking_update": tracking_update,
            "chart_data": chart_data,
            "ensemble_data": ensemble_data,
            "actual_numbers": session.get_actual_numbers(),
            "page_title": f"Chi tiết phiên: {session.session_id}",
        }

        return render(request, "predictions_tracker/sessions/detail.html", context)

    except Exception as e:
        logger.error(f"Error in session_detail: {e}")
        messages.error(request, f"Lỗi tải chi tiết phiên: {str(e)}")
        return redirect("predictions_tracker:pre_tracker_dashboard")


@login_required
def create_session(request, cycle_id):
    """
    Tạo session mới cho chu kỳ
    """
    try:
        cycle = get_object_or_404(PredictionCycle, id=cycle_id)

        if request.method == "POST":
            prediction_date = request.POST.get("prediction_date")

            if not prediction_date:
                messages.error(request, "Vui lòng chọn ngày dự đoán")
                return render(
                    request,
                    "predictions_tracker/sessions/create.html",
                    {
                        "cycle": cycle,
                        "page_title": f"Tạo phiên mới - {cycle.cycle_name}",
                    },
                )

            # Tạo session bằng service
            session = tracking_service.create_daily_session(cycle, prediction_date)

            messages.success(request, f"Đã tạo phiên {session.session_id} thành công!")
            return redirect("predictions_tracker:session_detail", session_id=session.id)

        # GET request
        context = {"cycle": cycle, "page_title": f"Tạo phiên mới - {cycle.cycle_name}"}

        return render(request, "predictions_tracker/sessions/create.html", context)

    except Exception as e:
        logger.error(f"Error creating session: {e}")
        messages.error(request, f"Lỗi tạo phiên: {str(e)}")
        return redirect("predictions_tracker:cycle_detail", cycle_id=cycle_id)


# ==================== EVALUATION VIEWS ====================


@login_required
def evaluation_list(request):
    """
    Danh sách tất cả các đánh giá
    """
    try:
        evaluations = TrackingEvaluation.objects.select_related(
            "session__cycle", "method_result__method"
        ).order_by("-evaluation_date")

        # Filtering
        method_filter = request.GET.get("method")
        if method_filter:
            evaluations = evaluations.filter(
                method_result__method__name__icontains=method_filter
            )

        date_filter = request.GET.get("date")
        if date_filter:
            evaluations = evaluations.filter(evaluation_date=date_filter)

        # Pagination
        paginator = Paginator(evaluations, 20)
        page = request.GET.get("page")
        evaluations_page = paginator.get_page(page)

        # Thống kê
        avg_hit_rate = evaluations.aggregate(avg_rate=Avg("hit_rate"))["avg_rate"] or 0
        avg_wilson = (
            evaluations.aggregate(avg_wilson=Avg("wilson_score"))["avg_wilson"] or 0
        )

        context = {
            "evaluations": evaluations_page,
            "avg_hit_rate": round(avg_hit_rate, 2),
            "avg_wilson": round(avg_wilson, 4),
            "method_filter": method_filter,
            "date_filter": date_filter,
            "page_title": "Danh sách đánh giá",
        }

        return render(request, "predictions_tracker/evaluations/list.html", context)

    except Exception as e:
        logger.error(f"Error in evaluation_list: {e}")
        messages.error(request, f"Lỗi tải danh sách đánh giá: {str(e)}")
        return render(
            request,
            "predictions_tracker/evaluations/list.html",
            {"page_title": "Đánh giá - Error", "error": str(e)},
        )


@login_required
def run_evaluation(request, session_id):
    """
    Chạy đánh giá cho session
    """
    try:
        print(
            f"run_evaluation called with session_id={session_id}, method={request.method}"
        )
        session = get_object_or_404(DailyTrackingSession, id=session_id)

        if request.method == "POST":
            evaluation_date = request.POST.get("evaluation_date")
            print(f"POST data: evaluation_date={evaluation_date}")

            if not evaluation_date:
                messages.error(request, "Vui lòng chọn ngày đánh giá")
                return render(
                    request,
                    "predictions_tracker/evaluations/run.html",
                    {
                        "session": session,
                        "page_title": f"Chạy đánh giá - {session.session_id}",
                    },
                )
            # Chuyển evaluation_date sang kiểu date
            if isinstance(evaluation_date, str):
                evaluation_date = datetime.strptime(evaluation_date, "%Y-%m-%d").date()
            # Chạy evaluation bằng service
            evaluations = tracking_service.evaluate_session_performance(
                session, evaluation_date
            )
            print(f"Evaluations created: {evaluations}")

            if evaluations:
                messages.success(
                    request, f"Đã tạo {len(evaluations)} đánh giá thành công!"
                )
            else:
                messages.warning(request, "Không tạo được đánh giá nào")

            return redirect("predictions_tracker:session_detail", session_id=session.id)

        # GET request
        context = {
            "session": session,
            "page_title": f"Chạy đánh giá - {session.session_id}",
        }
        print(f"Rendering run evaluation page for session_id={session_id}")
        return render(request, "predictions_tracker/evaluations/run.html", context)

    except Exception as e:
        print(f"Error running evaluation: {e}")
        messages.error(request, f"Lỗi chạy đánh giá: {str(e)}")
        return redirect("predictions_tracker:session_detail", session_id=session_id)


# ==================== ANALYTICS VIEWS ====================


@login_required
def analytics_dashboard(request):
    """
    Dashboard phân tích nâng cao
    """
    try:
        # Lấy dữ liệu cho biểu đồ
        recent_evaluations = TrackingEvaluation.objects.select_related(
            "method_result__method", "session__cycle"
        ).order_by("-evaluation_date")[:100]

        # Phân tích theo method
        method_analytics = {}
        for eval in recent_evaluations:
            method_name = eval.method_result.method.name
            if method_name not in method_analytics:
                method_analytics[method_name] = {
                    "name": method_name,
                    "evaluations": [],
                    "hit_rates": [],
                    "wilson_scores": [],
                    "confidence_scores": [],
                }

            method_analytics[method_name]["evaluations"].append(eval)
            method_analytics[method_name]["hit_rates"].append(eval.hit_rate)
            method_analytics[method_name]["wilson_scores"].append(eval.wilson_score)
            method_analytics[method_name]["confidence_scores"].append(
                eval.method_result.overall_confidence
            )

        # Tính thống kê cho từng method
        method_stats = []
        for method_name, data in method_analytics.items():
            if data["evaluations"]:
                method_stats.append(
                    {
                        "name": method_name,
                        "total_evaluations": len(data["evaluations"]),
                        "avg_hit_rate": round(
                            sum(data["hit_rates"]) / len(data["hit_rates"]), 2
                        ),
                        "avg_wilson_score": round(
                            sum(data["wilson_scores"]) / len(data["wilson_scores"]), 4
                        ),
                        "avg_confidence": round(
                            sum(data["confidence_scores"])
                            / len(data["confidence_scores"]),
                            4,
                        ),
                        "hit_rate_trend": data["hit_rates"][-10:],  # 10 điểm gần nhất
                        "wilson_trend": data["wilson_scores"][-10:],
                    }
                )

        # Sắp xếp theo performance
        method_stats.sort(key=lambda x: x["avg_hit_rate"], reverse=True)

        # Phân tích theo thời gian
        time_analytics = {}
        for eval in recent_evaluations:
            date_key = eval.evaluation_date.strftime("%Y-%m-%d")
            if date_key not in time_analytics:
                time_analytics[date_key] = {
                    "date": date_key,
                    "evaluations": 0,
                    "total_hit_rate": 0,
                    "total_wilson_score": 0,
                }

            time_analytics[date_key]["evaluations"] += 1
            time_analytics[date_key]["total_hit_rate"] += eval.hit_rate
            time_analytics[date_key]["total_wilson_score"] += eval.wilson_score

        # Tính average theo ngày
        daily_stats = []
        for date_key, data in sorted(time_analytics.items()):
            if data["evaluations"] > 0:
                daily_stats.append(
                    {
                        "date": date_key,
                        "avg_hit_rate": round(
                            data["total_hit_rate"] / data["evaluations"], 2
                        ),
                        "avg_wilson_score": round(
                            data["total_wilson_score"] / data["evaluations"], 4
                        ),
                        "evaluations_count": data["evaluations"],
                    }
                )

        # Lấy 30 ngày gần nhất
        daily_stats = daily_stats[-30:]

        context = {
            "method_stats": method_stats,
            "daily_stats": daily_stats,
            "total_evaluations": len(recent_evaluations),
            "page_title": "Analytics Dashboard",
        }

        return render(request, "predictions_tracker/analytics/dashboard.html", context)

    except Exception as e:
        logger.error(f"Error in analytics_dashboard: {e}")
        messages.error(request, f"Lỗi tải analytics: {str(e)}")
        return render(
            request,
            "predictions_tracker/analytics/dashboard.html",
            {"page_title": "Analytics - Error", "error": str(e)},
        )


class DateEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, (date, datetime)):
            return o.isoformat()
        return super().default(o)


class MonthlyPredictionReportView(TemplateView):
    template_name = "predictions_tracker/monthly_report.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        year = int(self.request.GET.get("year", timezone.now().year))
        month = int(self.request.GET.get("month", timezone.now().month))
        
        start_date = date(year, month, 1)
        last_day = calendar.monthrange(year, month)[1]
        end_date = date(year, month, last_day)

        context.update(
            {
                "year": year,
                "month": month,
                "month_name": calendar.month_name[month],
                "start_date": start_date,
                "end_date": end_date,
                "report_data": self._build_monthly_report(start_date, end_date),
                "methods_summary": self._get_methods_summary(start_date, end_date),
                "navigation": self._get_navigation_data(year, month),
                # ✅ CHỈ THÊM METHOD ANALYSIS
                "method_analysis": self._get_method_analysis_for_js_with_patterns(
                    start_date, end_date
                ),
                # ✅ THÊM METHOD STATS CHO PARTIAL
                "method_stats": _get_method_stats(year, month),
            }
        )

        return context
    def _convert_pattern_data_to_evaluations(self, pattern_data: dict, method_id: int) -> list:
        """
        ✅ CHUYỂN ĐỔI PATTERN DATA SANG EVALUATION FORMAT
        
        Args:
            pattern_data: {
                "hit_day_1": {method_id: [0,1,0,1,...]},
                "hit_day_2": {method_id: [0,1,0,1,...]},
                "hit_day_3": {method_id: [0,1,0,1,...]}
            }
            method_id: ID của method cần phân tích
        
        Returns:
            List of evaluation-like objects for _analyze_tracking_by_day
        """
        evaluations = []
        
        method_id_str = str(method_id)
        
        # Lấy dữ liệu cho method này
        day1_data = pattern_data.get("hit_day_1", {}).get(method_id_str, [])
        day2_data = pattern_data.get("hit_day_2", {}).get(method_id_str, [])
        day3_data = pattern_data.get("hit_day_3", {}).get(method_id_str, [])
        
        # Đảm bảo 3 arrays có cùng độ dài
        min_length = min(len(day1_data), len(day2_data), len(day3_data))
        if min_length == 0:
            return []
        
        # Tạo evaluation objects từ pattern data
        for i in range(min_length):
            # Tạo evaluation cho day 1
            if i < len(day1_data):
                evaluations.append({
                    "tracking_day": 1,
                    "hit_rate": day1_data[i] * 100,  # Convert 0/1 to 0%/100%
                    "hit_count": day1_data[i],
                    "evaluation_date": f"day_{i+1}",  # Placeholder
                    "index": i
                })
            
            # Tạo evaluation cho day 2
            if i < len(day2_data):
                evaluations.append({
                    "tracking_day": 2,
                    "hit_rate": day2_data[i] * 100,
                    "hit_count": day2_data[i],
                    "evaluation_date": f"day_{i+1}",
                    "index": i
                })
            
            # Tạo evaluation cho day 3
            if i < len(day3_data):
                evaluations.append({
                    "tracking_day": 3,
                    "hit_rate": day3_data[i] * 100,
                    "hit_count": day3_data[i],
                    "evaluation_date": f"day_{i+1}",
                    "index": i
                })
        
        return evaluations

    def _analyze_tracking_by_day_from_patterns(self, pattern_data: dict, method_id: int) -> dict:
        """
        ✅ PHÂN TÍCH TRACKING BY DAY TỪ PATTERN DATA
        """
        # Convert pattern data to evaluation format
        evaluations = self._convert_pattern_data_to_evaluations(pattern_data, method_id)
        
        if not evaluations:
            return {
                "day_1": {"hit_probability": 0, "avg_hit_rate": 0, "sample_size": 0, "confidence": "no_data"},
                "day_2": {"hit_probability": 0, "avg_hit_rate": 0, "sample_size": 0, "confidence": "no_data"},
                "day_3": {"hit_probability": 0, "avg_hit_rate": 0, "sample_size": 0, "confidence": "no_data"},
                "best_day": 1,
                "recommended_strategy": "Không có dữ liệu"
            }
        
        # Sử dụng hàm analyze hiện có
        return _analyze_tracking_by_day(evaluations)

    def _get_method_analysis_for_js_with_patterns(self, start_date: date, end_date: date) -> dict:
        """
        ✅ CẢI TIẾN: Sử dụng pattern data khi không có đủ evaluation data
        """
        # Thử lấy evaluation data trước
        method_analysis = self._get_method_analysis_for_js(start_date, end_date)
        
        # Nếu không có đủ dữ liệu, sử dụng pattern data
        if not method_analysis.get("day_by_day_analysis"):
            logger.info("📊 Using pattern data for day_by_day_analysis")
            
            # Lấy pattern data từ DataService
            target_date = end_date.strftime("%Y-%m-%d")
            pattern_data = data_service.get_pattern_data_for_analysis(
                target_date=target_date,
                method_ids=None,
                months_back=6,
                min_data_points=5
            )
            
            # Phân tích từng method
            for method_id in pattern_data.get("hit_day_1", {}).keys():
                try:
                    method_id_int = int(method_id)
                    
                    # Phân tích day-by-day từ pattern data
                    day_analysis = self._analyze_tracking_by_day_from_patterns(
                        pattern_data, method_id_int
                    )
                    
                    # Thêm vào method_analysis
                    if "day_by_day_analysis" not in method_analysis:
                        method_analysis["day_by_day_analysis"] = {}
                    
                    method_analysis["day_by_day_analysis"][method_id_int] = day_analysis
                    
                except (ValueError, Exception) as e:
                    logger.warning(f"Error processing method {method_id}: {e}")
                    continue
        
        return method_analysis

    def _get_method_analysis_for_js(self, start_date: date, end_date: date) -> dict:
        """
        Tạo dữ liệu phân tích method cho JavaScript - CHỈ DỮ LIỆU CẦN THIẾT
        Trả về: {
            "method_trends": {method_id: {...}},
            "method_cycles": {method_id: {...}},
            "method_recommendations": {method_id: {...}}
        }
        """
        # Lấy evaluations trong tháng
        evaluations = (
            TrackingEvaluation.objects.filter(
                evaluation_date__range=[start_date, end_date]
            )
            .select_related("method_result__method", "method_result__session")
            .order_by("evaluation_date")
        )

        method_analysis = {
            "method_trends": {},
            "method_cycles": {},
            "method_recommendations": {},
            "day_by_day_analysis": {},
        }

        # Group evaluations theo method
        methods_evals = {}
        for eval in evaluations:
            method_id = eval.method_result.method.id
            if method_id not in methods_evals:
                methods_evals[method_id] = {
                    "method_name": eval.method_result.method.name,
                    "evaluations": [],
                }

            # ✅ SỬA LỖI: Tính tracking_day từ dates
            prediction_date = eval.method_result.session.prediction_date
            evaluation_date = eval.evaluation_date

            # Tính tracking_day dựa trên khoảng cách ngày
            days_diff = (evaluation_date - prediction_date).days
            tracking_day = min(max(days_diff, 1), 3)  # Giới hạn 1-3

            methods_evals[method_id]["evaluations"].append(
                {
                    "date": eval.evaluation_date.isoformat(),
                    "hit_rate": eval.hit_rate,
                    "hit_count": eval.hit_count,
                    "wilson_score": eval.wilson_score,
                    "tracking_day": tracking_day,  # ✅ Tính từ logic thay vì field
                    "prediction_date": prediction_date.isoformat(),
                }
            )

        # Phân tích cho từng method
        for method_id, data in methods_evals.items():
            evals = data["evaluations"]
            method_name = data["method_name"]

            # 1. Trends analysis - Weekly performance
            weekly_trend = self._calculate_weekly_trend(evals)

            # 2. Cycle analysis - Pattern detection
            cycle_info = self._detect_hit_cycles(evals)

            # 3. Recommendations
            recommendation = self._calculate_method_recommendation(
                evals, weekly_trend, cycle_info
            )

            # ✅ THÊM PHÂN TÍCH THEO TỪNG NGÀY TRACKING
            day_analysis = self._analyze_tracking_by_day(evals)

            method_analysis["method_trends"][method_id] = {
                "method_name": method_name,
                "trend_direction": weekly_trend["direction"],
                "recent_performance": weekly_trend["recent_avg"],
                "stability": weekly_trend["stability"],
            }

            method_analysis["method_cycles"][method_id] = {
                "cycle_length": cycle_info["avg_cycle_length"],
                "hit_frequency": cycle_info["hit_frequency"],
                "last_hit_days_ago": cycle_info["last_hit_days_ago"],
                "next_expected_hit": cycle_info["next_expected_hit"],
            }

            method_analysis["method_recommendations"][method_id] = {
                "score": recommendation["score"],
                "confidence": recommendation["confidence"],
                "reason": recommendation["reason"],
                "risk_level": recommendation["risk_level"],
            }

            # ✅ THÊM DAY-BY-DAY ANALYSIS
            method_analysis["day_by_day_analysis"][method_id] = day_analysis
        return method_analysis

    def _analyze_tracking_by_day(self, evaluations: list) -> dict:
        """
        Phân tích hiệu suất theo từng ngày tracking (1, 2, 3)
        Trả về: {
            "day_1": {"hit_probability": float, "avg_hit_rate": float, "sample_size": int, "confidence": str},
            "day_2": {...},
            "day_3": {...},
            "best_day": int,
            "recommended_strategy": str
        }
        
        # Group theo tracking_day
        day_groups = {1: [], 2: [], 3: []}

        for eval in evaluations:
            # ✅ SỬA: Lấy tracking_day từ dict thay vì attribute
            day = (
                eval.get("tracking_day", 1)
                if isinstance(eval, dict)
                else getattr(eval, "tracking_day", 1)
            )
            if day in day_groups:
                day_groups[day].append(eval)

        day_analysis = {"day_1": {}, "day_2": {}, "day_3": {}}

        for day, day_evals in day_groups.items():
            if not day_evals:
                day_analysis[f"day_{day}"] = {
                    "hit_probability": 0,
                    "avg_hit_rate": 0,
                    "sample_size": 0,
                    "confidence": "no_data",
                    "recent_trend": "unknown",
                }
                continue

            # ✅ SỬA: Handle cả dict và object
            def get_hit_rate(eval_item):
                if isinstance(eval_item, dict):
                    return eval_item.get("hit_rate", 0)
                else:
                    return getattr(eval_item, "hit_rate", 0)

            # Tính hit probability (số lần hit_rate > 0 / tổng số lần)
            hit_occurrences = len([e for e in day_evals if e["hit_rate"] > 0])
            hit_probability = (hit_occurrences / len(day_evals)) * 100

            # Tính average hit rate
            avg_hit_rate = sum(e["hit_rate"] for e in day_evals) / len(day_evals)

            # Tính recent trend (7 lần gần nhất)
            recent_evals = day_evals[-7:] if len(day_evals) >= 7 else day_evals
            recent_hit_prob = (
                len([e for e in recent_evals if e["hit_rate"] > 0]) / len(recent_evals)
            ) * 100

            # Confidence level based on sample size
            sample_size = len(day_evals)
            if sample_size >= 20:
                confidence = "high"
            elif sample_size >= 10:
                confidence = "medium"
            elif sample_size >= 5:
                confidence = "low"
            else:
                confidence = "very_low"

            # Recent trend direction
            if len(day_evals) >= 4:
                first_half = day_evals[: len(day_evals) // 2]
                second_half = day_evals[len(day_evals) // 2 :]

                first_half_prob = (
                    len([e for e in first_half if e["hit_rate"] > 0]) / len(first_half)
                ) * 100
                second_half_prob = (
                    len([e for e in second_half if e["hit_rate"] > 0])
                    / len(second_half)
                ) * 100

                if second_half_prob > first_half_prob + 10:
                    recent_trend = "improving"
                elif second_half_prob < first_half_prob - 10:
                    recent_trend = "declining"
                else:
                    recent_trend = "stable"
            else:
                recent_trend = "insufficient_data"

            day_analysis[f"day_{day}"] = {
                "hit_probability": round(hit_probability, 1),
                "avg_hit_rate": round(avg_hit_rate, 1),
                "sample_size": sample_size,
                "confidence": confidence,
                "recent_trend": recent_trend,
                "recent_probability": round(recent_hit_prob, 1),
            }

        # Tìm best day
        best_day = 1
        best_score = 0

        for day in [1, 2, 3]:
            day_data = day_analysis[f"day_{day}"]
            if day_data["sample_size"] >= 5:  # Chỉ xem xét days có đủ data
                # Score = hit_probability * confidence_weight
                confidence_weight = {
                    "high": 1.0,
                    "medium": 0.8,
                    "low": 0.6,
                    "very_low": 0.3,
                    "no_data": 0,
                }
                score = day_data["hit_probability"] * confidence_weight.get(
                    day_data["confidence"], 0
                )

                if score > best_score:
                    best_score = score
                    best_day = day

        # Recommended strategy
        best_day_data = day_analysis[f"day_{best_day}"]
        if best_day_data["hit_probability"] >= 70:
            strategy = f"Nên đánh khung ngày {best_day} - xác suất cao"
        elif best_day_data["hit_probability"] >= 50:
            strategy = f"Khuyên đánh khung ngày {best_day} - xác suất trung bình"
        elif best_day_data["hit_probability"] >= 30:
            strategy = f"Cân nhắc đánh khung ngày {best_day} - xác suất thấp"
        else:
            strategy = "Không khuyến nghị - xác suất rất thấp"

        return {
            "day_1": day_analysis["day_1"],
            "day_2": day_analysis["day_2"],
            "day_3": day_analysis["day_3"],
            "best_day": best_day,
            "recommended_strategy": strategy,
            "analysis_summary": {
                "total_evaluations": len(evaluations),
                "best_day_probability": best_day_data["hit_probability"],
                "confidence_level": best_day_data["confidence"],
            },
        }"""
        return _analyze_tracking_by_day(evaluations)

    def _calculate_weekly_trend(self, evaluations: list) -> dict:
        """Tính xu hướng weekly đơn giản - SỬA LỖI HANDLE DICT/OBJECT"""
        if len(evaluations) < 7:
            return {"direction": "insufficient_data", "recent_avg": 0, "stability": 0}

        # ✅ Helper function để lấy hit_rate
        def get_hit_rate(eval_item):
            if isinstance(eval_item, dict):
                return eval_item.get("hit_rate", 0)
            else:
                return getattr(eval_item, "hit_rate", 0)

        # Lấy 7 ngày gần nhất
        recent_evals = evaluations[-7:]
        recent_avg = sum(get_hit_rate(e) for e in recent_evals) / len(recent_evals)

        # So sánh với 7 ngày trước đó (nếu có)
        if len(evaluations) >= 14:
            prev_evals = evaluations[-14:-7]
            prev_avg = sum(get_hit_rate(e) for e in prev_evals) / len(prev_evals)

            if recent_avg > prev_avg + 5:
                direction = "up"
            elif recent_avg < prev_avg - 5:
                direction = "down"
            else:
                direction = "stable"
        else:
            direction = "stable"

        # Tính stability (variance)
        if len(recent_evals) > 1:
            hit_rates = [get_hit_rate(e) for e in recent_evals]
            variance = sum((rate - recent_avg) ** 2 for rate in hit_rates) / len(
                hit_rates
            )
            stability = max(0, 100 - variance)
        else:
            stability = 0

        return {
            "direction": direction,
            "recent_avg": round(recent_avg, 1),
            "stability": round(stability, 1),
        }

    def _detect_hit_cycles(self, evaluations: list) -> dict:
        """Phát hiện chu kỳ trúng đơn giản - SỬA LỖI"""
        if len(evaluations) < 10:
            return {
                "avg_cycle_length": 0,
                "hit_frequency": 0,
                "last_hit_days_ago": 999,
                "next_expected_hit": "unknown",
            }

        # ✅ Helper function
        def get_hit_rate(eval_item):
            if isinstance(eval_item, dict):
                return eval_item.get("hit_rate", 0)
            else:
                return getattr(eval_item, "hit_rate", 0)

        # Tìm các ngày có hit_rate > 15%
        hit_dates = []
        for i, eval in enumerate(evaluations):
            if get_hit_rate(eval) > 15:
                hit_dates.append(i)

        if len(hit_dates) < 2:
            return {
                "avg_cycle_length": 0,
                "hit_frequency": 0,
                "last_hit_days_ago": 999,
                "next_expected_hit": "unknown",
            }

        # Tính khoảng cách giữa các lần hit
        intervals = []
        for i in range(1, len(hit_dates)):
            intervals.append(hit_dates[i] - hit_dates[i - 1])

        avg_cycle = sum(intervals) / len(intervals) if intervals else 0
        hit_frequency = len(hit_dates) / len(evaluations) * 100

        # Tính days since last hit
        last_hit_index = hit_dates[-1] if hit_dates else -999
        last_hit_days_ago = len(evaluations) - 1 - last_hit_index

        # Dự đoán next hit
        if avg_cycle > 0 and last_hit_days_ago < avg_cycle * 2:
            next_expected = max(0, avg_cycle - last_hit_days_ago)
            if next_expected <= 2:
                next_expected_hit = "soon"
            elif next_expected <= 5:
                next_expected_hit = "medium"
            else:
                next_expected_hit = "later"
        else:
            next_expected_hit = "unknown"

        return {
            "avg_cycle_length": round(avg_cycle, 1),
            "hit_frequency": round(hit_frequency, 1),
            "last_hit_days_ago": last_hit_days_ago,
            "next_expected_hit": next_expected_hit,
        }

    def _calculate_method_recommendation(
        self, evaluations: list, trend: dict, cycle: dict
    ) -> dict:
        """Tính recommendation score cho method - SỬA LỖI"""
        score = 0
        reasons = []
        confidence = 0

        # Base score từ recent performance
        recent_avg = trend["recent_avg"]
        score += min(recent_avg * 2, 50)  # Max 50 points

        # Trend bonus/penalty
        if trend["direction"] == "up":
            score += 20
            reasons.append("Xu hướng tăng")
        elif trend["direction"] == "down":
            score -= 15
            reasons.append("Xu hướng giảm")

        # Stability bonus
        if trend["stability"] > 70:
            score += 10
            reasons.append("Hiệu suất ổn định")

        # Cycle analysis
        if cycle["next_expected_hit"] == "soon":
            score += 25
            reasons.append("Sắp đến chu kỳ trúng")
        elif cycle["next_expected_hit"] == "medium":
            score += 10
            reasons.append("Gần chu kỳ trúng")

        # Hit frequency bonus
        if cycle["hit_frequency"] > 30:
            score += 15
            reasons.append("Tần suất trúng cao")

        # Confidence calculation
        data_points = len(evaluations)
        if data_points >= 20:
            confidence = min(95, 60 + data_points)
        elif data_points >= 10:
            confidence = 40 + data_points * 2
        else:
            confidence = data_points * 3

        # Risk level
        if score >= 80:
            risk_level = "low"
        elif score >= 60:
            risk_level = "medium"
        elif score >= 40:
            risk_level = "high"
        else:
            risk_level = "very_high"

        return {
            "score": min(100, max(0, score)),
            "confidence": confidence,
            "reason": "; ".join(reasons) if reasons else "Thiếu dữ liệu",
            "risk_level": risk_level,
        }

    def _build_monthly_report(self, start_date: date, end_date: date) -> dict:
        """
        Xây dựng báo cáo tháng với cấu trúc dữ liệu tối ưu cho template
        Trả về: {
            "days": [
                {
                    "date": date,
                    "methods_data": {method_id: {...}},
                    "sessions": [{...}]  # Thêm cho JavaScript
                }
            ]
        }
        """
        report_data = {"days": []}

        # Lấy tất cả sessions trong tháng
        sessions = (
            DailyTrackingSession.objects.filter(
                prediction_date__range=[start_date, end_date]
            )
            .select_related("cycle")
            .prefetch_related("method_results__method")
            .order_by("prediction_date")
        )

        # Lấy tất cả active methods
        active_methods = PredictionMethod.objects.filter(is_active=True)

        # Group sessions theo ngày
        sessions_by_date = defaultdict(list)
        for session in sessions:
            sessions_by_date[session.prediction_date].append(session)

        # Xây dựng data cho từng ngày
        current_date = start_date
        while current_date <= end_date:
            methods_data = {}
            sessions_data = []  # Thêm cho JavaScript

            # Khởi tạo tất cả methods với dữ liệu rỗng
            for method in active_methods:
                methods_data[method.id] = {
                    "method": method,
                    "predicted_numbers": [],
                    "tracking_results": [],
                    "has_data": False,
                    "overall_confidence": 0,
                }
            # Debug log
            logger.info(f"Date {current_date}: Initialized {len(methods_data)} methods")

            # Điền dữ liệu thực tế nếu có sessions
            if current_date in sessions_by_date:
                for session in sessions_by_date[current_date]:
                    # Lấy dữ liệu cho template table
                    method_results = session.method_results.all()

                    # Lấy dữ liệu cho JavaScript detail
                    session_methods_data = []

                    for method_result in method_results:
                        method_id = method_result.method.id
                        tracking_results = self._get_tracking_results(
                            session, method_result
                        )

                        # Cập nhật methods_data cho template table
                        if method_id in methods_data:
                            methods_data[method_id].update(
                                {
                                    "predicted_numbers": method_result.base_prediction_numbers,
                                    "tracking_results": tracking_results,
                                    "has_data": True,
                                    "overall_confidence": method_result.overall_confidence,
                                }
                            )

                        # Thêm vào session_methods_data cho JavaScript
                        session_methods_data.append(
                            {
                                "method_id": method_result.method.id,
                                "method_name": method_result.method.name,
                                "category": method_result.method.get_category_display(),
                                "confidence": method_result.overall_confidence,
                                "predicted_numbers": method_result.base_prediction_numbers,
                                "tracking_results": tracking_results,
                                "total_hits": sum(
                                    tr["hit_count"] for tr in tracking_results
                                ),
                                "avg_hit_rate": (
                                    sum(tr["hit_rate"] for tr in tracking_results)
                                    / len(tracking_results)
                                    if tracking_results
                                    else 0
                                ),
                            }
                        )

                    # Thêm session data cho JavaScript
                    sessions_data.append(
                        {
                            "session": {
                                "cycle": {
                                    "cycle_name": (
                                        session.cycle.cycle_name
                                        if session.cycle
                                        else "Auto Import"
                                    )
                                },
                                "status": session.get_status_display(),
                            },
                            "methods": session_methods_data,
                        }
                    )

            day_data = {
                "date": current_date,
                "methods_data": methods_data,
                "sessions": sessions_data,  # Thêm cho JavaScript
            }

            report_data["days"].append(day_data)
            current_date += timedelta(days=1)
        logger.info(f"Report built with {len(report_data['days'])} days")
        return report_data

    def _get_minimal_tracking_results(
        self, session, method_result, evaluations_cache
    ) -> list:
        """
        Lấy tracking results tối giản - chỉ thông tin cần thiết
        """
        tracking_results = []
        prediction_date = session.prediction_date

        for day in range(1, 4):
            tracking_date = prediction_date + timedelta(days=day)
            cache_key = f"{session.id}_{method_result.method.id}_{tracking_date}"

            if cache_key in evaluations_cache:
                eval = evaluations_cache[cache_key]
                tracking_results.append(
                    {
                        "day": day,
                        "hit_count": eval.hit_count,
                        "hit_rate": round(eval.hit_rate, 1),  # Làm tròn để giảm size
                        "has_result": True,
                    }
                )
            else:
                # ✅ Tính nhanh without database query
                try:
                    actual_result = KetQuaXoSo.objects.get(ngay=tracking_date)
                    actual_numbers = set(actual_result.get_all_2digit_numbers())
                    predicted_numbers = set(method_result.base_prediction_numbers)
                    hit_count = len(predicted_numbers.intersection(actual_numbers))
                    hit_rate = (
                        (hit_count / len(predicted_numbers) * 100)
                        if predicted_numbers
                        else 0
                    )

                    tracking_results.append(
                        {
                            "day": day,
                            "hit_count": hit_count,
                            "hit_rate": round(hit_rate, 1),
                            "has_result": True,
                        }
                    )
                except KetQuaXoSo.DoesNotExist:
                    tracking_results.append(
                        {"day": day, "hit_count": 0, "hit_rate": 0, "has_result": False}
                    )

        return tracking_results

    def _get_session_methods_data(self, session: DailyTrackingSession) -> list:
        """
        Lấy dữ liệu chi tiết các methods trong session
        """
        methods_data = []

        # Lấy tất cả method results trong session
        method_results = (
            MethodPredictionResult.objects.filter(session=session)
            .select_related("method")
            .order_by("method__priority")
        )

        for method_result in method_results:
            # Lấy kết quả tracking cho 3 ngày kế tiếp
            tracking_results = self._get_tracking_results(session, method_result)

            # Tính tổng thống kê
            total_hits = sum(result["hit_count"] for result in tracking_results)
            avg_hit_rate = (
                sum(result["hit_rate"] for result in tracking_results)
                / len(tracking_results)
                if tracking_results
                else 0
            )

            method_data = {
                "method": method_result.method,
                "predicted_numbers": method_result.base_prediction_numbers,
                "tracking_results": tracking_results,
                "total_hits": total_hits,
                "avg_hit_rate": avg_hit_rate,
                "overall_confidence": method_result.overall_confidence,
            }
            methods_data.append(method_data)

        return methods_data

    def _get_tracking_results(
        self, session: DailyTrackingSession, method_result: MethodPredictionResult
    ) -> list:
        """
        Lấy kết quả tracking cho 3 ngày kế tiếp
        """
        tracking_results = []
        prediction_date = session.prediction_date

        for day in range(1, 4):  # 3 ngày kế tiếp
            tracking_date = prediction_date + timedelta(days=day)

            # Tìm kết quả thực tế từ KetQuaXoSo
            try:
                actual_result = KetQuaXoSo.objects.get(ngay=tracking_date)
                actual_numbers = list(actual_result.get_all_2digit_numbers())
            except KetQuaXoSo.DoesNotExist:
                actual_numbers = []

            # Tìm evaluation nếu có
            try:
                evaluation = TrackingEvaluation.objects.get(
                    session=session,
                    method_result=method_result,
                    evaluation_date=tracking_date,
                )
                hit_numbers = evaluation.hit_numbers
                hit_count = evaluation.hit_count
                hit_rate = evaluation.hit_rate
            except TrackingEvaluation.DoesNotExist:
                # Tính toán hit numbers nếu chưa có evaluation
                predicted_numbers = set(method_result.base_prediction_numbers)
                actual_numbers_set = set(actual_numbers)
                hit_numbers = list(predicted_numbers.intersection(actual_numbers_set))
                hit_count = len(hit_numbers)
                hit_rate = (
                    (hit_count / len(predicted_numbers)) * 100
                    if predicted_numbers
                    else 0
                )

            tracking_result = {
                "day": day,
                "tracking_date": tracking_date,
                "actual_numbers": actual_numbers,
                "hit_numbers": hit_numbers,
                "hit_count": hit_count,
                "hit_rate": hit_rate,
                "has_result": bool(actual_numbers),
            }
            tracking_results.append(tracking_result)

        return tracking_results

    def _get_methods_summary(self, start_date: date, end_date: date) -> list:
        """
        Tổng hợp hiệu suất các methods trong tháng
        """
        methods = PredictionMethod.objects.filter(is_active=True)
        summary = []

        for method in methods:
            # Đếm số predictions trong tháng
            predictions_count = MethodPredictionResult.objects.filter(
                method=method, session__prediction_date__range=[start_date, end_date]
            ).count()

            # Tính thống kê từ evaluations
            evaluations = TrackingEvaluation.objects.filter(
                method_result__method=method,
                evaluation_date__range=[start_date, end_date],
            )

            if evaluations.exists():
                stats = evaluations.aggregate(
                    total_evaluations=Count("id"),
                    avg_hit_count=Avg("hit_count"),
                    avg_hit_rate=Avg("hit_rate"),
                )

                method_summary = {
                    "method": method,
                    "predictions_count": predictions_count,
                    "evaluations_count": stats["total_evaluations"],
                    "avg_hit_count": round(stats["avg_hit_count"] or 0, 2),
                    "avg_hit_rate": round(stats["avg_hit_rate"] or 0, 2),
                    "performance_level": self._get_performance_level(
                        stats["avg_hit_rate"] or 0
                    ),
                }
            else:
                method_summary = {
                    "method": method,
                    "predictions_count": predictions_count,
                    "evaluations_count": 0,
                    "avg_hit_count": 0,
                    "avg_hit_rate": 0,
                    "performance_level": "no-data",
                }

            summary.append(method_summary)

        # Sắp xếp theo hiệu suất
        summary.sort(key=lambda x: x["avg_hit_rate"], reverse=True)
        return summary

    def _get_performance_level(self, hit_rate: float) -> str:
        """Phân loại mức hiệu suất"""
        if hit_rate >= 30:
            return "excellent"
        elif hit_rate >= 20:
            return "good"
        elif hit_rate >= 10:
            return "average"
        elif hit_rate > 0:
            return "poor"
        else:
            return "no-data"

    def _get_navigation_data(self, year: int, month: int) -> dict:
        """Dữ liệu điều hướng tháng trước/sau"""
        prev_month = month - 1 if month > 1 else 12
        prev_year = year if month > 1 else year - 1

        next_month = month + 1 if month < 12 else 1
        next_year = year if month < 12 else year + 1

        return {
            "prev_month": prev_month,
            "prev_year": prev_year,
            "next_month": next_month,
            "next_year": next_year,
            "current_month": timezone.now().month,
            "current_year": timezone.now().year,
        }


# ==================== API VIEWS ====================
# THÊM VÀO EXISTING VIEWS


@csrf_exempt
@require_http_methods(["POST"])
def api_enhanced_ml_prediction(request):
    """
    ✅ API SỬ DỤNG TRAINED ML MODELS CHO DỰ ĐOÁN
    """
    try:
        data = json.loads(request.body)

        # Validate input
        method_ids = data.get("method_ids", [])
        target_date_str = data.get("target_date")

        if not method_ids:
            return JsonResponse({"success": False, "error": "method_ids required"})

        if not target_date_str:
            return JsonResponse({"success": False, "error": "target_date required"})

        try:
            target_date = datetime.strptime(target_date_str, "%Y-%m-%d").date()
        except ValueError:
            return JsonResponse(
                {
                    "success": False,
                    "error": "Invalid target_date format. Use YYYY-MM-DD",
                }
            )

        # Get enhanced ML predictions
        results = tracking_service.get_enhanced_ml_predictions(
            method_ids=method_ids, target_date=target_date, use_trained_models=True
        )

        # Add model performance info
        model_performance = ml_model_service.get_model_performance_summary()
        results["model_performance"] = model_performance

        return JsonResponse(results)

    except Exception as e:
        logger.error(f"❌ Error in api_enhanced_ml_prediction: {e}")
        return JsonResponse({"success": False, "error": str(e)})


@csrf_exempt
@require_http_methods(["POST"])
def api_retrain_models(request):
    """
    ✅ API ĐỂ RETRAIN ML MODELS
    """
    try:
        data = json.loads(request.body)
        force_retrain = data.get("force", False)

        logger.info(f"🔄 API retrain request: force={force_retrain}")

        # Start retraining
        results = ml_model_service.retrain_if_needed(
            force_retrain=force_retrain, performance_threshold=0.6
        )

        return JsonResponse({"success": True, "retrain_results": results})

    except Exception as e:
        logger.error(f"❌ Error in api_retrain_models: {e}")
        return JsonResponse({"success": False, "error": str(e)})


@csrf_exempt
@require_http_methods(["GET"])
def api_cycle_summary(request, cycle_id):
    """
    API lấy thông tin tóm tắt chu kỳ
    """
    try:
        cycle = get_object_or_404(PredictionCycle, id=cycle_id)
        summary = tracking_service.get_cycle_summary(cycle)

        return JsonResponse({"success": True, "data": summary})

    except Exception as e:
        logger.error(f"Error in api_cycle_summary: {e}")
        return JsonResponse({"success": False, "error": str(e)}, status=500)


@csrf_exempt
@require_http_methods(["GET"])
def api_method_comparison(request, cycle_id):
    """
    API so sánh hiệu suất methods
    """
    try:
        cycle = get_object_or_404(PredictionCycle, id=cycle_id)
        comparison = tracking_service.get_method_comparison(cycle)

        return JsonResponse({"success": True, "data": comparison})

    except Exception as e:
        logger.error(f"Error in api_method_comparison: {e}")
        return JsonResponse({"success": False, "error": str(e)}, status=500)


@csrf_exempt
@require_http_methods(["POST"])
def api_update_tracking_status(request):
    """
    API cập nhật trạng thái tracking
    """
    try:
        data = json.loads(request.body)
        session_id = data.get("session_id")

        if not session_id:
            return JsonResponse(
                {"success": False, "error": "Missing session_id"}, status=400
            )

        session = get_object_or_404(DailyTrackingSession, id=session_id)
        update_info = tracking_service.update_tracking_status(session)

        return JsonResponse({"success": True, "data": update_info})

    except Exception as e:
        logger.error(f"Error in api_update_tracking_status: {e}")
        return JsonResponse({"success": False, "error": str(e)}, status=500)


@csrf_exempt
@require_http_methods(["GET"])
def api_session_chart_data(request, session_id):
    """
    API lấy dữ liệu biểu đồ cho session
    """
    try:
        session = get_object_or_404(DailyTrackingSession, id=session_id)

        # Lấy method results
        method_results = session.method_results.select_related("method").all()

        # Lấy evaluations
        evaluations = session.evaluations.select_related("method_result__method").all()

        # Chuẩn bị dữ liệu
        chart_data = {
            "methods": [],
            "hit_rates": [],
            "wilson_scores": [],
            "confidence_scores": [],
            "ensemble_recommendations": session.ensemble_recommendations[:10],
        }

        for result in method_results:
            chart_data["methods"].append(result.method.name)
            chart_data["confidence_scores"].append(result.overall_confidence)

            # Lấy hit rate từ evaluations
            method_evaluations = evaluations.filter(method_result=result)
            avg_hit_rate = (
                method_evaluations.aggregate(avg_rate=Avg("hit_rate"))["avg_rate"] or 0
            )
            avg_wilson = (
                method_evaluations.aggregate(avg_wilson=Avg("wilson_score"))[
                    "avg_wilson"
                ]
                or 0
            )

            chart_data["hit_rates"].append(round(avg_hit_rate, 2))
            chart_data["wilson_scores"].append(round(avg_wilson, 4))

        return JsonResponse({"success": True, "data": chart_data})

    except Exception as e:
        logger.error(f"Error in api_session_chart_data: {e}")
        return JsonResponse({"success": False, "error": str(e)}, status=500)


@staff_member_required
def reload_prediction_methods_view(request):
    """
    View cho phép admin quét lại các phương pháp trong methods_btl và tính toán lại.
    """
    context = {"page_title": "Reload Prediction Methods"}
    if request.method == "POST":
        try:
            method_classes = get_all_method_classes()
            methods = []
            for cls in method_classes:
                instance = cls()
                code = instance.get_code()
                name = instance.get_name()
                description = instance.get_description()
                category = getattr(instance, "get_category", lambda: "other")()
                parameters = (
                    instance.get_parameters()
                    if hasattr(instance, "get_parameters")
                    else {}
                )
                method, _ = PredictionMethod.objects.get_or_create(
                    code=code,
                    defaults={
                        "name": name,
                        "description": description,
                        "category": category,
                        "parameters": parameters,
                        "is_active": True,
                        "priority": 5,
                    },
                )
                methods.append((method, instance))
                PredictionStrategy.objects.get_or_create(
                    method=method,
                    defaults={
                        "strategy_type": category,
                        "ensemble_weight": 1.0,
                        "ensemble_config": {},
                    },
                )
            # Tính toán lại cho 30 ngày gần nhất
            end_date = date.today()
            start_date = end_date - timedelta(days=30)
            ketqua_qs = KetQuaXoSo.objects.filter(
                ngay__gte=start_date, ngay__lte=end_date
            ).order_by("ngay")
            total_calc = 0
            for ketqua in ketqua_qs:
                data = ketqua.to_dict() if hasattr(ketqua, "to_dict") else {}
                for method, instance in methods:
                    try:
                        result = instance.calculate(data)
                        numbers = (
                            result.get("two_digits_loto")
                            if isinstance(result, dict)
                            else result
                        )
                        if not numbers:
                            continue
                        session, _ = DailyTrackingSession.objects.get_or_create(
                            cycle=None,
                            prediction_date=ketqua.ngay,
                            defaults={
                                "session_id": f"auto_{ketqua.ngay}",
                                "tracking_start_date": ketqua.ngay,
                                "tracking_end_date": ketqua.ngay,
                                "status": "completed",
                            },
                        )
                        method_result, _ = MethodPredictionResult.objects.get_or_create(
                            session=session,
                            method=method,
                            defaults={
                                "base_prediction_numbers": numbers,
                                "overall_confidence": 0.5,
                            },
                        )
                        actual_numbers = list(ketqua.get_all_2digit_numbers())
                        hit_numbers = list(set(numbers) & set(actual_numbers))
                        hit_count = len(hit_numbers)
                        total_predicted = len(numbers)
                        hit_rate = (
                            (hit_count / total_predicted * 100)
                            if total_predicted
                            else 0
                        )
                        TrackingEvaluation.objects.get_or_create(
                            session=session,
                            method_result=method_result,
                            evaluation_date=ketqua.ngay,
                            defaults={
                                "days_after_prediction": 0,
                                "actual_numbers": actual_numbers,
                                "predicted_numbers": numbers,
                                "hit_numbers": hit_numbers,
                                "hit_count": hit_count,
                                "total_predicted": total_predicted,
                                "hit_rate": hit_rate,
                                "wilson_score": 0,
                            },
                        )
                        total_calc += 1
                    except Exception as e:
                        continue
            messages.success(
                request,
                f"Đã load {len(methods)} phương pháp và tính toán {total_calc} lượt thành công.",
            )
            return redirect(request.path)
        except Exception as e:
            messages.error(request, f"Lỗi: {e}")
    return render(request, "predictions_tracker/reload_methods.html", context)


@staff_member_required
def method_management_action(request):
    """
    Xử lý các thao tác quản lý method từ partial component
    Tích hợp với load_prediction_methods command
    """
    if request.method != "POST":
        messages.error(request, "Phương thức không hợp lệ")
        return redirect("predictions_tracker:pre_tracker_monthly_report")

    try:
        action = request.POST.get("action")

        if action == "reload_quick":
            return _handle_quick_reload(request)
        elif action == "scan_only":
            return _handle_scan_only(request)
        elif action == "reload_range":
            return _handle_reload_range(request)
        else:
            messages.error(request, f"Thao tác không hợp lệ: {action}")

    except Exception as e:
        logger.error(f"Error in method_management_action: {e}")
        messages.error(request, f"Lỗi xử lý: {str(e)}")

    return redirect("predictions_tracker:pre_tracker_monthly_report")


def _handle_quick_reload(request):
    """Xử lý reload nhanh 3 ngày gần nhất"""
    from io import StringIO

    from django.core.management import call_command

    try:
        # Capture command output
        output = StringIO()
        call_command("load_prediction_methods", days=3, stdout=output)

        messages.success(
            request, "✅ Đã quét và tính toán lại 3 ngày gần nhất thành công!"
        )
        return redirect("predictions_tracker:pre_tracker_monthly_report")

    except Exception as e:
        messages.error(request, f"❌ Lỗi reload nhanh: {str(e)}")
        return redirect("predictions_tracker:pre_tracker_monthly_report")


def _handle_scan_only(request):
    """Xử lý chỉ quét methods không tính toán"""
    try:
        # Sử dụng trực tiếp logic từ command
        method_classes = get_all_method_classes()
        methods_created = 0
        methods_updated = 0

        for cls in method_classes:
            try:
                instance = cls()
                method, created = PredictionMethod.objects.update_or_create(
                    code=instance.get_code(),
                    defaults={
                        "name": instance.get_name(),
                        "description": instance.get_description(),
                        "category": getattr(
                            instance, "get_category", lambda: "other"
                        )(),
                        "parameters": (
                            instance.get_parameters()
                            if hasattr(instance, "get_parameters")
                            else {}
                        ),
                        "is_active": True,
                        "priority": 5,
                    },
                )

                if created:
                    methods_created += 1
                else:
                    methods_updated += 1

                # Tạo strategy
                PredictionStrategy.objects.get_or_create(
                    method=method,
                    defaults={
                        "strategy_type": method.category,
                        "ensemble_weight": 1.0,
                        "ensemble_config": {},
                    },
                )

            except Exception as e:
                logger.warning(f"Lỗi xử lý method {cls.__name__}: {e}")
                continue

        messages.success(
            request,
            f"✅ Quét methods thành công: {methods_created} mới, {methods_updated} cập nhật",
        )

    except Exception as e:
        messages.error(request, f"❌ Lỗi quét methods: {str(e)}")

    return redirect("predictions_tracker:pre_tracker_monthly_report")


def _handle_reload_range(request):
    """Xử lý reload với tùy chọn nâng cao"""
    from io import StringIO

    from django.core.management import call_command

    try:
        # Parse parameters
        date_option = request.POST.get("date_option", "days")
        force = request.POST.get("force") == "on"
        dry_run = request.POST.get("dry_run") == "on"
        clear_all = request.POST.get("clear_all") == "on"

        # Build command arguments
        cmd_args = []
        cmd_kwargs = {
            "force": force,
            "dry_run": dry_run,
        }

        # Handle clear_all first
        if clear_all:
            if not dry_run:  # Only execute if not dry run
                output = StringIO()
                call_command("load_prediction_methods", clear_all=True, stdout=output)
                messages.warning(request, "⚠️ Đã xóa toàn bộ dữ liệu predictions!")
                return redirect("predictions_tracker:pre_tracker_monthly_report")
            else:
                messages.info(request, "🔍 DRY RUN: Sẽ xóa toàn bộ dữ liệu predictions")
                return redirect("predictions_tracker:pre_tracker_monthly_report")

        # Handle date options
        if date_option == "days":
            days = int(request.POST.get("days", 7))
            cmd_kwargs["days"] = days

        elif date_option == "current_month":
            # Get current month dates
            today = timezone.now().date()
            start_date = today.replace(day=1)
            last_day = calendar.monthrange(today.year, today.month)[1]
            end_date = today.replace(day=last_day)

            cmd_kwargs["start_date"] = start_date.strftime("%Y-%m-%d")
            cmd_kwargs["end_date"] = end_date.strftime("%Y-%m-%d")

        elif date_option == "custom_range":
            start_date = request.POST.get("start_date")
            end_date = request.POST.get("end_date")

            if not start_date or not end_date:
                messages.error(
                    request, "❌ Vui lòng chọn đầy đủ ngày bắt đầu và kết thúc"
                )
                return redirect("predictions_tracker:pre_tracker_monthly_report")

            cmd_kwargs["start_date"] = start_date
            cmd_kwargs["end_date"] = end_date

        # Execute command
        output = StringIO()
        call_command("load_prediction_methods", *cmd_args, stdout=output, **cmd_kwargs)

        if dry_run:
            messages.info(
                request, "🔍 DRY RUN hoàn thành - kiểm tra console để xem chi tiết"
            )
        else:
            messages.success(request, "✅ Reload methods thành công!")

    except Exception as e:
        messages.error(request, f"❌ Lỗi reload range: {str(e)}")

    return redirect("predictions_tracker:pre_tracker_monthly_report")


def _get_method_stats(year, month):
    """
    Lấy thống kê methods cho partial component
    Trả về: {
        "total_methods": int,
        "active_methods": int,
        "methods_with_data": int,
        "last_update": datetime
    }
    """
    start_date = date(year, month, 1)
    last_day = calendar.monthrange(year, month)[1]
    end_date = date(year, month, last_day)

    total_methods = PredictionMethod.objects.count()
    active_methods = PredictionMethod.objects.filter(is_active=True).count()

    # Methods có dữ liệu trong tháng
    methods_with_data = (
        PredictionMethod.objects.filter(
            tracking_results__session__prediction_date__range=[start_date, end_date]
        )
        .distinct()
        .count()
    )

    # Last update
    last_session = DailyTrackingSession.objects.order_by("-created_at").first()
    last_update = last_session.created_at if last_session else None

    return {
        "total_methods": total_methods,
        "active_methods": active_methods,
        "methods_with_data": methods_with_data,
        "last_update": last_update,
    }


class NumpyJSONEncoder(DjangoJSONEncoder):
    """✅ CUSTOM JSON ENCODER để handle numpy types và boolean"""

    def default(self, obj):
        if isinstance(obj, np.integer):
            return int(obj)
        elif isinstance(obj, np.floating):
            if np.isnan(obj) or np.isinf(obj):
                return 0.0
            return float(obj)
        elif isinstance(obj, np.ndarray):
            return obj.tolist()
        elif isinstance(obj, (np.bool_, bool)):
            return bool(obj)
        elif hasattr(obj, "isoformat"):  # datetime objects
            return obj.isoformat()
        return super().default(obj)


@csrf_exempt
@require_http_methods(["POST"])  
def api_pattern_analysis(request):
    """
    ✅ API phân tích pattern được cải thiện với thuật toán nâng cao - SỬA LỖI JSON
    """
    try:
        data = json.loads(request.body)
        
        target_date_str = data.get('target_date')
        method_ids = data.get('method_ids', [])
        prediction_horizon = data.get('prediction_horizon', 1)
        use_advanced_ml = data.get('use_advanced_ml', True)
        
        # ✅ VALIDATE parameters
        if not target_date_str or not method_ids:
            return JsonResponse({
                "success": False,
                "error": "target_date và method_ids là bắt buộc"
            }, status=400, encoder=NumpyJSONEncoder)
        
        target_date_obj = datetime.strptime(target_date_str, "%Y-%m-%d").date()
        
        # ✅ LẤY DỮ LIỆU PATTERN
        historical_patterns = data_service.get_pattern_data_for_analysis(
            target_date=target_date_str,
            method_ids=method_ids,
            months_back=12,
            min_data_points=30
        )
        
        # ✅ VALIDATE data quality
        data_quality = data_service.validate_pattern_data_quality(
            historical_patterns,
            min_methods=3,
            min_data_points=30
        )
        
        if not data_quality.get('is_sufficient'):
            return JsonResponse({
                "success": False,
                "error": "Dữ liệu không đủ chất lượng cho dự đoán chính xác",
                "data_quality": _clean_for_json(data_quality),
                "suggestion": "Cần ít nhất 30 data points per method và 3 methods"
            }, encoder=NumpyJSONEncoder)
        
        # ✅ SỬA: SỬ DỤNG DataService cho ML
        if use_advanced_ml:
            logger.info("🤖 Using advanced ML with DataService")
            
            try:
                # ✅ SỬA: Train advanced model với DataService
                if not hasattr(data_service, 'advanced_models') or not getattr(data_service, 'advanced_models', {}):
                    training_result = data_service.train_advanced_prediction_model(
                        hit_patterns=historical_patterns,
                        prediction_horizon=prediction_horizon
                    )
                    
                    if not training_result.get('training_completed'):
                        logger.warning("Advanced model training failed, using fallback")
                        use_advanced_ml = False
                
                if use_advanced_ml and hasattr(data_service, 'advanced_models'):
                    # ✅ SỬA: Dự đoán với DataService
                    predictions = data_service.predict_next_days(
                        hit_patterns=historical_patterns,
                        method_ids=[str(mid) for mid in method_ids],
                        prediction_horizon=prediction_horizon
                    )
                    
                    # ✅ CLEAN predictions cho JSON serialization
                    formatted_predictions = {}
                    for method_id, pred in predictions.items():
                        try:
                            # ✅ ENSURE all values are JSON serializable
                            if 'day_1' in pred and 'day_2' in pred and 'day_3' in pred:
                                formatted_predictions[str(method_id)] = {
                                    'method_name': str(pred.get('method_name', f'Method {method_id}')),
                                    'day_probabilities': {
                                        'day_1': _ensure_float(pred['day_1']['probability']),
                                        'day_2': _ensure_float(pred['day_2']['probability']), 
                                        'day_3': _ensure_float(pred['day_3']['probability'])
                                    },
                                    'day_confidences': {
                                        'day_1': _ensure_float(pred['day_1']['confidence']),
                                        'day_2': _ensure_float(pred['day_2']['confidence']),
                                        'day_3': _ensure_float(pred['day_3']['confidence']) 
                                    },
                                    'recommended_day': int(pred.get('recommended_day', 1)),
                                    'confidence': _ensure_float(pred.get('overall_confidence', 0.0)),
                                    'prediction_quality': str(pred.get('prediction_quality', 'unknown'))
                                }
                            else:
                                # ✅ FALLBACK format
                                formatted_predictions[str(method_id)] = {
                                    'method_name': f'Method {method_id}',
                                    'day_probabilities': {'day_1': 0.1, 'day_2': 0.1, 'day_3': 0.1},
                                    'day_confidences': {'day_1': 0.1, 'day_2': 0.1, 'day_3': 0.1},
                                    'recommended_day': 1,
                                    'confidence': 0.0,
                                    'prediction_quality': 'error'
                                }
                        except Exception as format_error:
                            logger.error(f"❌ Error formatting prediction for method {method_id}: {format_error}")
                            continue
                    
                    return JsonResponse({
                        "success": True,
                        "predictions": formatted_predictions,
                        "analysis_type": "advanced_ml_dataservice",
                        "data_source": "trained_advanced_models_dataservice",
                        "target_date": target_date_str,
                        "prediction_horizon": int(prediction_horizon),
                        "methods_analyzed": len(formatted_predictions),
                        "data_quality": _clean_for_json(data_quality),
                        "metadata": _clean_for_json({
                            "model_type": "ensemble_advanced_dataservice",
                            "training_samples": int(data_quality.get('total_data_points', 0)),
                            "feature_engineering": "advanced",
                            "prediction_algorithm": "sliding_window_ensemble",
                            "service": "DataService"
                        })
                    }, encoder=NumpyJSONEncoder)
                    
            except Exception as ml_error:
                logger.error(f"❌ Advanced ML error: {ml_error}")
                use_advanced_ml = False
        
        # ✅ FALLBACK: Pattern-based analysis với TrackingService
        logger.info("Using pattern-based analysis as fallback with TrackingService")
        
        try:
            pattern_predictions = tracking_service.analyze_multiple_methods_ml_with_data(
                method_ids=method_ids,
                target_date=target_date_obj,
                historical_patterns=historical_patterns,
                data_quality=data_quality
            )
            
            # ✅ CLEAN pattern_predictions cho JSON
            cleaned_predictions = _clean_for_json(pattern_predictions)
            
            return JsonResponse({
                "success": True,
                "predictions": cleaned_predictions,
                "analysis_type": "pattern_based",
                "data_source": "historical_patterns_tracking",
                "target_date": target_date_str,
                "methods_analyzed": len(cleaned_predictions),
                "data_quality": _clean_for_json(data_quality),
                "metadata": _clean_for_json({
                    "service": "TrackingService",
                    "analysis_method": "pattern_based"
                })
            }, encoder=NumpyJSONEncoder)
            
        except Exception as fallback_error:
            logger.error(f"❌ Fallback analysis error: {fallback_error}")
            raise fallback_error
        
    except Exception as e:
        logger.error(f"Error in advanced pattern analysis: {e}")
        return JsonResponse({
            "success": False,
            "error": f"Lỗi phân tích: {str(e)}"
        }, status=500, encoder=NumpyJSONEncoder)

def _ensure_float(value) -> float:
    """✅ HELPER: Đảm bảo value là float JSON-serializable"""
    try:
        if isinstance(value, (bool, np.bool_)):
            return float(value)
        elif isinstance(value, (int, np.integer)):
            return float(value)
        elif isinstance(value, (float, np.floating)):
            if np.isnan(value) or np.isinf(value):
                return 0.0
            return float(value)
        else:
            return float(value)
    except (ValueError, TypeError, OverflowError):
        return 0.0
    
def _validate_json_serializable(obj, path="root"):
    """
    ✅ VALIDATE OBJECT CÓ THỂ SERIALIZE JSON KHÔNG
    
    Args:
        obj: Object cần kiểm tra
        path: Path hiện tại để debug
        
    Returns:
        tuple: (is_valid, error_message)
    """
    try:
        if isinstance(obj, dict):
            for key, value in obj.items():
                is_valid, error_msg = _validate_json_serializable(value, f"{path}.{key}")
                if not is_valid:
                    return False, f"At {path}.{key}: {error_msg}"
        elif isinstance(obj, list):
            for i, item in enumerate(obj):
                is_valid, error_msg = _validate_json_serializable(item, f"{path}[{i}]")
                if not is_valid:
                    return False, f"At {path}[{i}]: {error_msg}"
        elif isinstance(obj, set):
            return False, f"Set object found (use list instead)"
        elif isinstance(obj, (np.integer, np.floating, np.bool_, np.ndarray)):
            # These will be handled by NumpyJSONEncoder
            pass
        elif hasattr(obj, 'isoformat'):
            # datetime objects - handled by encoder
            pass
        elif isinstance(obj, (str, int, float, bool, type(None))):
            # Native JSON types
            pass
        else:
            return False, f"Unsupported type: {type(obj)}"
            
        return True, "OK"
        
    except Exception as e:
        return False, f"Validation error: {str(e)}"


def _debug_json_response_data(data: dict) -> dict:
    """
    ✅ DEBUG FUNCTION ĐỂ TÌM LỖI JSON SERIALIZATION
    """
    logger.info("🔍 Debugging JSON response data structure...")
    
    # Validate từng phần
    for key, value in data.items():
        is_valid, error_msg = _validate_json_serializable(value, f"data.{key}")
        if not is_valid:
            logger.error(f"❌ JSON validation failed at data.{key}: {error_msg}")
        else:
            logger.info(f"✅ data.{key} is JSON serializable")
    
    # Clean data
    cleaned_data = _clean_data_for_json_response(data)
    
    # Validate cleaned data
    is_valid, error_msg = _validate_json_serializable(cleaned_data)
    if not is_valid:
        logger.error(f"❌ Cleaned data still has JSON issues: {error_msg}")
    else:
        logger.info(f"✅ Cleaned data is JSON serializable")
    
    return cleaned_data

def _clean_for_json(obj):
    """✅ HELPER: Làm sạch object cho JSON serialization"""
    if isinstance(obj, dict):
        return {key: _clean_for_json(value) for key, value in obj.items()}
    elif isinstance(obj, list):
        return [_clean_for_json(item) for item in obj]
    elif isinstance(obj, (np.bool_, bool)):
        return bool(obj)
    elif isinstance(obj, (np.integer, int)):
        return int(obj)
    elif isinstance(obj, (np.floating, float)):
        if np.isnan(obj) or np.isinf(obj):
            return 0.0
        return float(obj)
    elif isinstance(obj, np.ndarray):
        return obj.tolist()
    elif hasattr(obj, 'isoformat'):  # datetime objects
        return obj.isoformat()
    else:
        return obj
    
# ✅ THÊM API ĐỂ TRAIN ML MODELS
@csrf_exempt
@require_http_methods(["POST"])
def api_train_ml_models(request):
    """
    ✅ API để huấn luyện ML models
    """
    try:
        data = json.loads(request.body) if request.body else {}

        months_back = data.get("months_back", 12)
        min_samples = data.get("min_samples", 20)

        logger.info(
            f"🚀 Starting ML model training: months_back={months_back}, min_samples={min_samples}"
        )

        # Huấn luyện models
        training_results = ml_model_service.train_comprehensive_model(
            months_back=months_back, min_samples_per_method=min_samples
        )

        return JsonResponse(
            {
                "success": True,
                "message": "ML models trained successfully",
                "training_results": training_results,
            }
        )

    except Exception as e:
        logger.error(f"❌ Error in ML model training: {e}")
        return JsonResponse(
            {"success": False, "error": f"Error training ML models: {str(e)}"},
            status=500,
        )


# ✅ THÊM API ĐỂ KIỂM TRA TRẠNG THÁI ML MODELS
@csrf_exempt
@require_http_methods(["GET"])
def api_ml_models_status(request):
    """
    ✅ API kiểm tra trạng thái ML models
    """
    try:
        status = {
            "is_trained": ml_model_service.is_trained,
            "models_available": {
                day_key: model is not None
                for day_key, model in ml_model_service.models.items()
            },
            "feature_count": len(ml_model_service.feature_names),
            "metadata": ml_model_service._get_model_metadata(),
        }

        return JsonResponse({"success": True, "status": status})

    except Exception as e:
        logger.error(f"❌ Error getting ML models status: {e}")
        return JsonResponse(
            {"success": False, "error": f"Error getting status: {str(e)}"}, status=500
        )


def _generate_enhanced_recommendations(
    predictions: Dict, target_date: date
) -> List[Dict]:
    """
    ✅ Tạo enhanced recommendations với error handling

    Args:
        predictions: Dict - ML predictions data
        target_date: date - Target date for recommendations

    Returns:
        List[Dict] - Enhanced recommendations list
    """
    try:
        if not predictions:
            return []

        recommendations = []

        # Sắp xếp theo overall confidence
        sorted_methods = sorted(
            predictions.items(), key=lambda x: x[1].get("confidence", 0), reverse=True
        )

        for method_id, prediction in sorted_methods[:10]:  # Top 10
            try:
                best_day = prediction.get("recommended_day", 1)
                confidence = prediction.get("confidence", 0.0)

                # ✅ VALIDATE REQUIRED FIELDS
                if not all(
                    key in prediction
                    for key in [
                        "method_name",
                        "day_predicted_numbers",
                        "day_probabilities",
                        "day_confidences",
                    ]
                ):
                    logger.warning(
                        f"⚠️ Skipping recommendation for method {method_id} due to missing fields"
                    )
                    continue

                predicted_numbers = prediction["day_predicted_numbers"].get(
                    f"day_{best_day}", []
                )

                rec = {
                    "method_id": method_id,
                    "method_name": prediction["method_name"],
                    "recommended_day": best_day,
                    "confidence": confidence,
                    "predicted_numbers": predicted_numbers,
                    "all_day_predictions": {
                        "day_1": {
                            "probability": prediction["day_probabilities"].get(
                                "day_1", 0.0
                            ),
                            "confidence": prediction["day_confidences"].get(
                                "day_1", 0.0
                            ),
                            "numbers": prediction["day_predicted_numbers"].get(
                                "day_1", []
                            ),
                        },
                        "day_2": {
                            "probability": prediction["day_probabilities"].get(
                                "day_2", 0.0
                            ),
                            "confidence": prediction["day_confidences"].get(
                                "day_2", 0.0
                            ),
                            "numbers": prediction["day_predicted_numbers"].get(
                                "day_2", []
                            ),
                        },
                        "day_3": {
                            "probability": prediction["day_probabilities"].get(
                                "day_3", 0.0
                            ),
                            "confidence": prediction["day_confidences"].get(
                                "day_3", 0.0
                            ),
                            "numbers": prediction["day_predicted_numbers"].get(
                                "day_3", []
                            ),
                        },
                    },
                    "performance_info": {
                        "category": prediction.get("pattern_info", {}).get(
                            "performance_category", "average"
                        ),
                        "trend": prediction.get("pattern_info", {}).get(
                            "trend", "stable"
                        ),
                        "reliability": prediction.get("pattern_info", {}).get(
                            "reliability_score", 0.5
                        ),
                        "sample_size": prediction.get("pattern_info", {}).get(
                            "sample_size", 0
                        ),
                    },
                }

                recommendations.append(rec)

            except Exception as e:
                logger.error(
                    f"❌ Error processing recommendation for method {method_id}: {e}"
                )
                continue

        return recommendations

    except Exception as e:
        logger.error(f"❌ Error generating enhanced recommendations: {e}")
        return []


def _assess_frontend_data_quality(hit_patterns):
    """
    ✅ ĐÁNH GIÁ NHANH CHẤT LƯỢNG DỮ LIỆU TỪ FRONTEND
    """
    if not hit_patterns or not hit_patterns.get("hit_day_1"):
        return {
            "is_insufficient": True,
            "reason": "No frontend data provided",
            "total_methods": 0,
        }

    total_methods = len(hit_patterns.get("hit_day_1", {}))
    valid_methods = 0
    total_data_points = 0

    for method_id in hit_patterns.get("hit_day_1", {}).keys():
        day1_data = hit_patterns["hit_day_1"].get(method_id, [])
        day2_data = hit_patterns.get("hit_day_2", {}).get(method_id, [])
        day3_data = hit_patterns.get("hit_day_3", {}).get(method_id, [])

        if len(day1_data) >= 5:  # Yêu cầu tối thiểu
            all_data = day1_data + day2_data + day3_data
            unique_values = set(all_data)

            if len(unique_values) >= 2:  # Có diversity
                valid_methods += 1
                total_data_points += len(day1_data)

    avg_data_points = total_data_points / valid_methods if valid_methods > 0 else 0

    # Đánh giá
    is_insufficient = (
        total_methods < 3  # Ít hơn 3 methods
        or valid_methods < 2  # Ít hơn 2 methods hợp lệ
        or avg_data_points < 10  # Trung bình dưới 10 data points
    )

    return {
        "is_insufficient": is_insufficient,
        "reason": f"Frontend: {valid_methods}/{total_methods} valid methods, avg {avg_data_points:.1f} points",
        "total_methods": total_methods,
        "valid_methods": valid_methods,
        "avg_data_points": avg_data_points,
    }


def _get_comprehensive_fallback_data(
    target_date, method_ids=None, months_back=6, min_data_points=5
):
    """
    ✅ SỬA: SỬ DỤNG DATASERVICE THỐNG NHẤT
    """
    logger.info(f"🔄 Using DataService for fallback data")

    try:
        # ✅ SỬ DỤNG DATASERVICE
        patterns = data_service.get_pattern_data_for_analysis(
            target_date=target_date,
            method_ids=method_ids,
            months_back=months_back,
            min_data_points=min_data_points,
        )

        return patterns

    except Exception as e:
        logger.error(f"❌ Error using DataService for pattern data: {e}")
        return {"hit_day_1": {}, "hit_day_2": {}, "hit_day_3": {}}


def _assess_fallback_quality(patterns_data, min_data_points=10):
    """
    ✅ ĐÁNH GIÁ NHANH CHẤT LƯỢNG FALLBACK DATA
    """
    total_methods = len(patterns_data.get("hit_day_1", {}))
    valid_methods = 0

    for method_id in patterns_data.get("hit_day_1", {}).keys():
        day1_data = patterns_data["hit_day_1"][method_id]
        day2_data = patterns_data.get("hit_day_2", {}).get(method_id, [])
        day3_data = patterns_data.get("hit_day_3", {}).get(method_id, [])

        if len(day1_data) >= min_data_points:
            all_data = day1_data + day2_data + day3_data
            unique_values = set(all_data)

            if len(unique_values) >= 2:
                valid_methods += 1

    return {
        "total_methods": total_methods,
        "valid_methods": valid_methods,
        "is_sufficient": valid_methods >= 5,
    }


def _predict_hit_patterns_ml(patterns_data, target_date=None):
    """
    ✅ BASIC ML PREDICTION - SỬ DỤNG KHI DỮ LIỆU CHẤT LƯỢNG TRUNG BÌNH
    Đây là version đơn giản hơn của enhanced version
    """
    predictions = {}

    logger.info(
        f"🤖 Starting BASIC ML prediction for {len(patterns_data.get('hit_day_1', {}))} methods"
    )

    total_methods = len(patterns_data.get("hit_day_1", {}))
    successful_predictions = 0

    for method_id in patterns_data["hit_day_1"].keys():
        try:
            # Lấy dữ liệu cho method này
            day1_data = patterns_data["hit_day_1"][method_id]
            day2_data = patterns_data["hit_day_2"][method_id]
            day3_data = patterns_data["hit_day_3"][method_id]

            # Yêu cầu thấp hơn cho basic version
            if len(day1_data) < 5:
                logger.debug(
                    f"Method {method_id}: Insufficient data ({len(day1_data)} points)"
                )
                continue

            # ✅ BASIC FEATURE EXTRACTION (không có advanced features)
            features = _extract_basic_features(day1_data, day2_data, day3_data)

            if not features:
                logger.warning(f"Method {method_id}: No basic features extracted")
                continue

            # ✅ BASIC PREDICTION cho từng ngày
            day_predictions = {}
            method_has_valid_prediction = False

            for day_idx, day_data in enumerate([day1_data, day2_data, day3_data], 1):
                try:
                    prediction = _predict_single_day_basic(features, day_data, day_idx)
                    day_predictions[f"day_{day_idx}"] = prediction

                    if prediction.get("probability", 0) > 0:
                        method_has_valid_prediction = True

                except Exception as e:
                    logger.error(
                        f"Method {method_id} Day {day_idx} basic prediction error: {e}"
                    )
                    # Simple fallback
                    day_predictions[f"day_{day_idx}"] = {
                        "probability": (
                            sum(day_data) / len(day_data) if day_data else 0.1
                        ),
                        "confidence": 0.3,
                        "stability": 0.5,
                    }

            if not method_has_valid_prediction:
                continue

            # Tìm ngày tốt nhất
            best_day = max(
                day_predictions.keys(), key=lambda k: day_predictions[k]["probability"]
            )
            best_day_num = int(best_day.split("_")[1])

            # Lấy tên method
            try:
                method = PredictionMethod.objects.get(id=method_id)
                method_name = method.name
            except PredictionMethod.DoesNotExist:
                method_name = f"Method {method_id}"

            predictions[method_id] = {
                "method_name": method_name,
                "recommended_day": best_day_num,
                "confidence": day_predictions[best_day]["confidence"],
                "day_probabilities": {
                    "day_1": day_predictions["day_1"]["probability"],
                    "day_2": day_predictions["day_2"]["probability"],
                    "day_3": day_predictions["day_3"]["probability"],
                },
                "pattern_info": {
                    "trend": _calculate_simple_trend(day1_data, day2_data, day3_data),
                    "stability": day_predictions[best_day]["stability"],
                    "prediction_type": "basic_ml",
                },
            }

            successful_predictions += 1

        except Exception as e:
            logger.error(f"❌ Basic ML error for method {method_id}: {e}")
            continue

    logger.info(
        f"🎯 Basic ML prediction completed: {successful_predictions}/{total_methods} methods"
    )
    return predictions


def _calculate_simple_trend(day1_data, day2_data, day3_data):
    """
    ✅ TÍNH XU HƯỚNG ĐỊN GIẢN
    """
    rates = []
    for data in [day1_data, day2_data, day3_data]:
        if data:
            rates.append(sum(data) / len(data))
        else:
            rates.append(0)

    if len(rates) >= 2:
        if rates[-1] > rates[0] + 0.05:
            return "improving"
        elif rates[-1] < rates[0] - 0.05:
            return "declining"

    return "stable"


def _enhance_patterns_with_historical_data(current_patterns, target_date, method_ids):
    """
    ✅ BỔ SUNG DỮ LIỆU LỊCH SỬ TỪ DATABASE
    """
    # Lấy dữ liệu lịch sử 6 tháng
    historical_data = _get_comprehensive_historical_data(
        target_date=target_date, method_ids=method_ids, months_back=6
    )

    enhanced_patterns = {"hit_day_1": {}, "hit_day_2": {}, "hit_day_3": {}}

    for method_id in set(
        list(current_patterns.get("hit_day_1", {}).keys())
        + list(historical_data.get("hit_day_1", {}).keys())
    ):

        for day_key in ["hit_day_1", "hit_day_2", "hit_day_3"]:
            # Kết hợp: Historical + Current với weighted priority
            historical_part = historical_data.get(day_key, {}).get(str(method_id), [])
            current_part = current_patterns.get(day_key, {}).get(str(method_id), [])

            # ✅ WEIGHTED COMBINATION: 70% historical + 30% current (nếu có current data)
            if current_part:
                # Giới hạn historical data để tránh overwhelm
                historical_trimmed = (
                    historical_part[-60:]
                    if len(historical_part) > 60
                    else historical_part
                )
                combined_data = historical_trimmed + current_part
            else:
                # Chỉ có historical data
                combined_data = (
                    historical_part[-90:]
                    if len(historical_part) > 90
                    else historical_part
                )

            enhanced_patterns[day_key][str(method_id)] = combined_data

    logger.info(
        f"Enhanced patterns: {len(enhanced_patterns['hit_day_1'])} methods with "
        f"avg {np.mean([len(v) for v in enhanced_patterns['hit_day_1'].values()]):.1f} data points"
    )

    return enhanced_patterns


def _get_comprehensive_historical_data(target_date, method_ids=None, months_back=6):
    """
    ✅ CẬP NHẬT: Sync với version mẫu - có cache và optimization
    """
    try:
        end_date = datetime.strptime(target_date, "%Y-%m-%d").date()
    except:
        end_date = date.today()

    start_date = end_date - timedelta(days=months_back * 30)

    logger.info(f"🔄 Querying historical data from {start_date} to {end_date}")

    # ✅ CẬP NHẬT: Query từ sessions như file mẫu
    query = (
        DailyTrackingSession.objects.filter(
            prediction_date__range=[start_date, end_date]
        )
        .select_related("cycle")
        .prefetch_related("method_results__method", "method_results__evaluations")
        .order_by("prediction_date")
    )  # ✅ Sắp xếp từ cũ đến mới

    if method_ids:
        query = query.filter(method_results__method_id__in=method_ids)

    sessions = query.distinct()

    logger.info(f"📊 Found {sessions.count()} sessions")

    if sessions.count() == 0:
        logger.warning("❌ No sessions found in historical data query")
        return {"hit_day_1": {}, "hit_day_2": {}, "hit_day_3": {}}

    historical_patterns = {
        "hit_day_1": defaultdict(list),
        "hit_day_2": defaultdict(list),
        "hit_day_3": defaultdict(list),
    }

    # ✅ THÊM CACHE actual_results như file mẫu
    actual_results_cache = {}

    for session in sessions:
        prediction_date = session.prediction_date

        # ✅ CACHE actual results cho 3 ngày kế tiếp
        actual_results = {}
        for day in range(1, 4):
            tracking_date = prediction_date + timedelta(days=day)
            cache_key = tracking_date.strftime("%Y-%m-%d")

            if cache_key not in actual_results_cache:
                try:
                    result = KetQuaXoSo.objects.get(ngay=tracking_date)
                    actual_results_cache[cache_key] = set(
                        result.get_all_2digit_numbers()
                    )
                except KetQuaXoSo.DoesNotExist:
                    actual_results_cache[cache_key] = set()

            actual_results[day] = actual_results_cache[cache_key]

        # ✅ XỬ LÝ từng method result
        for method_result in session.method_results.all():
            method_id = method_result.method.id
            predicted_numbers = set(method_result.base_prediction_numbers)

            day_hits = [0, 0, 0]  # [day1, day2, day3]

            for day in range(1, 4):
                if actual_results[day]:
                    hit_count = len(predicted_numbers.intersection(actual_results[day]))
                    if hit_count > 0:
                        day_hits[day - 1] = 1

            # ✅ THÊM VÀO PATTERN theo đúng thứ tự
            method_id_str = str(method_id)
            historical_patterns["hit_day_1"][method_id_str].append(day_hits[0])
            historical_patterns["hit_day_2"][method_id_str].append(day_hits[1])
            historical_patterns["hit_day_3"][method_id_str].append(day_hits[2])

    # Convert to regular dict
    result = {}
    for day_key in ["hit_day_1", "hit_day_2", "hit_day_3"]:
        result[day_key] = dict(historical_patterns[day_key])

    # ✅ VALIDATION: Log để kiểm tra thứ tự như file mẫu
    if result["hit_day_1"]:
        sample_method = list(result["hit_day_1"].keys())[0]
        sample_data = result["hit_day_1"][sample_method]
        logger.info(
            f"✅ Data order validation: Method {sample_method} - "
            f"First 3: {sample_data[:3]} (oldest), Last 3: {sample_data[-3:]} (newest)"
        )
    else:
        logger.warning("❌ No methods found in historical data")

    logger.info(
        f"Historical data loaded: {len(result['hit_day_1'])} methods from {start_date} to {end_date}"
    )
    return result


def _assess_final_data_quality(patterns_data):
    """
    ✅ ĐÁNH GIÁ CHẤT LƯỢNG DỮ LIỆU CUỐI CÙNG
    """
    quality_metrics = {
        "total_methods": len(patterns_data.get("hit_day_1", {})),
        "valid_methods": 0,
        "avg_data_points": 0,
        "diversity_scores": [],
        "insufficient_methods": [],
        "single_class_methods": [],
        "is_insufficient": False,
        "historical_boost": False,
    }

    total_data_points = 0

    for method_id in patterns_data.get("hit_day_1", {}).keys():
        day1_data = patterns_data["hit_day_1"][method_id]
        day2_data = patterns_data["hit_day_2"][method_id]
        day3_data = patterns_data["hit_day_3"][method_id]

        all_data = day1_data + day2_data + day3_data
        data_points = len(day1_data)

        # Kiểm tra đủ dữ liệu
        if data_points < 10:
            quality_metrics["insufficient_methods"].append(method_id)
            continue

        # Kiểm tra diversity
        unique_values = set(all_data)
        if len(unique_values) < 2:
            quality_metrics["single_class_methods"].append(method_id)
            continue

        # Tính diversity score
        hit_rate = sum(all_data) / len(all_data)
        diversity = min(hit_rate, 1 - hit_rate) * 2
        quality_metrics["diversity_scores"].append(diversity)

        quality_metrics["valid_methods"] += 1
        total_data_points += data_points

    if quality_metrics["valid_methods"] > 0:
        quality_metrics["avg_data_points"] = (
            total_data_points / quality_metrics["valid_methods"]
        )
        quality_metrics["avg_diversity"] = np.mean(quality_metrics["diversity_scores"])
    else:
        quality_metrics["avg_diversity"] = 0

    # Đánh giá tổng thể
    if quality_metrics["valid_methods"] < 5 or quality_metrics["avg_diversity"] < 0.1:
        quality_metrics["is_insufficient"] = True

    # Kiểm tra có boost từ historical data không
    if quality_metrics["avg_data_points"] > 50:
        quality_metrics["historical_boost"] = True

    return quality_metrics


def _get_historical_hit_patterns(days_back=90, target_date=None):
    """
    ✅ CẢI TIẾN: Lấy dữ liệu pattern trúng từ lịch sử với target_date
    """
    if target_date:
        try:
            end_date = datetime.strptime(target_date, "%Y-%m-%d").date()
        except:
            end_date = date.today()
    else:
        end_date = date.today()

    start_date = end_date - timedelta(days=days_back)

    # Lấy tất cả sessions trong khoảng thời gian
    sessions = (
        DailyTrackingSession.objects.filter(
            prediction_date__range=[start_date, end_date]
        )
        .select_related("cycle")
        .prefetch_related("method_results__method", "method_results__evaluations")
    )

    historical_patterns = {
        "hit_day_1": defaultdict(list),
        "hit_day_2": defaultdict(list),
        "hit_day_3": defaultdict(list),
    }

    # Xử lý sessions theo prediction_date
    for session in sessions:
        prediction_date = session.prediction_date

        for method_result in session.method_results.all():
            method_id = method_result.method.id
            day_hits = [0, 0, 0]  # [day1, day2, day3]

            # Kiểm tra evaluations cho từng ngày
            for evaluation in method_result.evaluations.all():
                if hasattr(evaluation, "days_after_prediction"):
                    tracking_day = evaluation.days_after_prediction + 1
                    if 1 <= tracking_day <= 3 and evaluation.hit_count > 0:
                        day_hits[tracking_day - 1] = 1

            # Thêm vào historical patterns
            historical_patterns["hit_day_1"][method_id].append(day_hits[0])
            historical_patterns["hit_day_2"][method_id].append(day_hits[1])
            historical_patterns["hit_day_3"][method_id].append(day_hits[2])

    # Convert defaultdict to dict
    result = {}
    for day_key in ["hit_day_1", "hit_day_2", "hit_day_3"]:
        result[day_key] = dict(historical_patterns[day_key])

    logger.info(
        f"📊 Historical patterns loaded for target_date {target_date}: "
        f"{len(result['hit_day_1'])} methods, "
        f"{len(list(result['hit_day_1'].values())[0]) if result['hit_day_1'] else 0} days"
    )

    return result


def _compare_with_actual_results(recommendations, target_date):
    """
    ✅ SO SÁNH RECOMMENDATIONS VỚI KẾT QUẢ THỰC TẾ - SỬA LỖI BIẾN day_key

    Args:
        recommendations (dict): Top recommendations theo từng ngày
        target_date (str): Target date string "YYYY-MM-DD"

    Returns:
        dict: {
            "day_1": {"hit_numbers": list, "hit_rate": float, "total_numbers": int, "actual_numbers": list},
            "day_2": {...},
            "day_3": {...},
            "overall_stats": {"total_hits": int, "total_predictions": int, "hit_rate": float}
        }
    """
    comparison_results = {
        "day_1": {
            "hit_numbers": [],
            "hit_rate": 0.0,
            "total_numbers": 0,
            "actual_numbers": [],
        },
        "day_2": {
            "hit_numbers": [],
            "hit_rate": 0.0,
            "total_numbers": 0,
            "actual_numbers": [],
        },
        "day_3": {
            "hit_numbers": [],
            "hit_rate": 0.0,
            "total_numbers": 0,
            "actual_numbers": [],
        },
        "overall_stats": {"total_hits": 0, "total_predictions": 0, "hit_rate": 0.0},
    }

    try:
        target_dt = datetime.strptime(target_date, "%Y-%m-%d").date()

        # ✅ SỬA: Dùng enumerate để đảm bảo day_key luôn được định nghĩa
        for day in range(1, 4):
            day_key = f"day_{day}"  # ✅ ĐỊNH NGHĨA RÕ RÀNG day_key
            tracking_date = target_dt + timedelta(days=day)

            try:
                # Lấy kết quả thực tế
                actual_result = KetQuaXoSo.objects.get(ngay=tracking_date)
                actual_numbers = set(actual_result.get_all_2digit_numbers())

                # Lấy recommendations cho ngày này
                day_recommendations = recommendations.get(day_key, [])

                all_predicted_numbers = []
                hit_numbers = []

                # Xử lý từng method recommendation
                for method_rec in day_recommendations:
                    if isinstance(method_rec, dict) and "numbers" in method_rec:
                        predicted_nums = set(method_rec["numbers"])
                        all_predicted_numbers.extend(predicted_nums)

                        # Tìm số trúng
                        hits = predicted_nums.intersection(actual_numbers)
                        hit_numbers.extend(hits)

                # ✅ TÍNH TOÁN RESULTS CHO NGÀY
                unique_predicted = set(all_predicted_numbers)
                unique_hits = set(hit_numbers)

                comparison_results[day_key] = {
                    "hit_numbers": sorted(list(unique_hits)),
                    "total_numbers": len(unique_predicted),
                    "hit_rate": (
                        len(unique_hits) / len(unique_predicted)
                        if unique_predicted
                        else 0.0
                    ),
                    "actual_numbers": sorted(list(actual_numbers)),
                    "prediction_count": len(day_recommendations),
                    "tracking_date": tracking_date.strftime("%Y-%m-%d"),
                }

                logger.debug(
                    f"Comparison for {day_key}: {len(unique_hits)}/{len(unique_predicted)} hits"
                )

            except KetQuaXoSo.DoesNotExist:
                # ✅ HANDLE TRƯỜNG HỢP CHƯA CÓ KẾT QUẢ
                day_recommendations = recommendations.get(day_key, [])
                total_predicted = sum(
                    len(method_rec.get("numbers", []))
                    for method_rec in day_recommendations
                    if isinstance(method_rec, dict)
                )

                comparison_results[day_key] = {
                    "hit_numbers": [],
                    "total_numbers": total_predicted,
                    "hit_rate": 0.0,
                    "actual_numbers": [],
                    "note": f"Chưa có kết quả cho {tracking_date.strftime('%d/%m/%Y')}",
                    "prediction_count": len(day_recommendations),
                    "tracking_date": tracking_date.strftime("%Y-%m-%d"),
                }

                logger.info(f"No result available for {tracking_date}")

            except Exception as day_error:
                # ✅ HANDLE LỖI CHO TỪNG NGÀY
                logger.error(f"Error processing day {day}: {day_error}")
                comparison_results[day_key] = {
                    "hit_numbers": [],
                    "total_numbers": 0,
                    "hit_rate": 0.0,
                    "actual_numbers": [],
                    "error": str(day_error),
                    "prediction_count": 0,
                    "tracking_date": tracking_date.strftime("%Y-%m-%d"),
                }

    except ValueError as date_error:
        # ✅ HANDLE LỖI PARSE DATE
        logger.error(f"Invalid target_date format '{target_date}': {date_error}")
        for day in range(1, 4):
            day_key = f"day_{day}"
            comparison_results[day_key]["error"] = f"Invalid date format: {target_date}"

    except Exception as e:
        # ✅ HANDLE LỖI CHUNG
        logger.error(f"General error in comparison: {e}")
        for day in range(1, 4):
            day_key = f"day_{day}"
            comparison_results[day_key]["error"] = f"Comparison error: {str(e)}"

    # ✅ TÍNH OVERALL STATS - SỬA ĐỂ TRÁNH LỖI
    try:
        total_hits = 0
        total_predictions = 0

        for day in range(1, 4):
            day_key = f"day_{day}"
            day_data = comparison_results[day_key]

            if isinstance(day_data, dict):
                # Kiểm tra có error không
                if "error" not in day_data:
                    total_hits += len(day_data.get("hit_numbers", []))
                    total_predictions += day_data.get("total_numbers", 0)

        comparison_results["overall_stats"] = {
            "total_hits": total_hits,
            "total_predictions": total_predictions,
            "hit_rate": (
                total_hits / total_predictions if total_predictions > 0 else 0.0
            ),
            "target_date": target_date,
            "comparison_timestamp": timezone.now().isoformat(),
        }

        logger.info(
            f"Overall comparison stats: {total_hits}/{total_predictions} = {(total_hits/total_predictions*100 if total_predictions > 0 else 0):.1f}%"
        )

    except Exception as stats_error:
        logger.error(f"Error calculating overall stats: {stats_error}")
        comparison_results["overall_stats"] = {
            "total_hits": 0,
            "total_predictions": 0,
            "hit_rate": 0.0,
            "error": str(stats_error),
            "target_date": target_date,
        }

    return comparison_results


def _get_method_predicted_numbers(method_id, target_date):
    """
    ✅ LẤY SỐ DỰ ĐOÁN CỦA METHOD CHO NGÀY CỤ THỂ - CẢI TIẾN ERROR HANDLING

    Args:
        method_id (str/int): Method ID
        target_date (str): Target date "YYYY-MM-DD"

    Returns:
        list: Predicted numbers hoặc empty list nếu không tìm thấy
    """
    try:
        target_dt = datetime.strptime(target_date, "%Y-%m-%d").date()

        # ✅ STRATEGY 1: Tìm session chính xác cho ngày target
        session = (
            DailyTrackingSession.objects.filter(prediction_date=target_dt)
            .order_by("-created_at")
            .first()
        )

        if session:
            method_result = session.method_results.filter(method_id=method_id).first()

            if method_result and method_result.base_prediction_numbers:
                logger.debug(
                    f"Found exact match for method {method_id} on {target_date}"
                )
                return method_result.base_prediction_numbers

        # ✅ STRATEGY 2: Tìm session gần nhất trước target_date
        session = (
            DailyTrackingSession.objects.filter(prediction_date__lt=target_dt)
            .order_by("-prediction_date")
            .first()
        )

        if session:
            method_result = session.method_results.filter(method_id=method_id).first()

            if method_result and method_result.base_prediction_numbers:
                logger.debug(
                    f"Found nearby session for method {method_id}: {session.prediction_date}"
                )
                return method_result.base_prediction_numbers

        # ✅ STRATEGY 3: Tìm session gần nhất sau target_date (trong vòng 3 ngày)
        max_future_date = target_dt + timedelta(days=3)
        session = (
            DailyTrackingSession.objects.filter(
                prediction_date__gt=target_dt, prediction_date__lte=max_future_date
            )
            .order_by("prediction_date")
            .first()
        )

        if session:
            method_result = session.method_results.filter(method_id=method_id).first()

            if method_result and method_result.base_prediction_numbers:
                logger.debug(
                    f"Found future session for method {method_id}: {session.prediction_date}"
                )
                return method_result.base_prediction_numbers

        logger.info(
            f"No predicted numbers found for method {method_id} around {target_date}"
        )

    except ValueError as ve:
        logger.error(f"Invalid target_date format '{target_date}': {ve}")
    except Exception as e:
        logger.error(f"Error getting predicted numbers for method {method_id}: {e}")

    return []


def _predict_hit_patterns_ml_enhanced(
    patterns_data, target_date=None, data_quality=None
):
    """
    ✅ ML DỰ ĐOÁN VỚI ADAPTIVE WEIGHTS VÀ QUALITY-AWARE LEARNING
    """
    predictions = {}

    # ✅ ADAPTIVE WEIGHTS dựa trên data quality
    time_weights = _calculate_adaptive_weights(data_quality)

    for method_id in patterns_data["hit_day_1"].keys():
        try:
            day1_data = patterns_data["hit_day_1"][method_id]
            day2_data = patterns_data["hit_day_2"][method_id]
            day3_data = patterns_data["hit_day_3"][method_id]

            if len(day1_data) < 10:
                continue

            # ✅ APPLY ADAPTIVE WEIGHTS
            weighted_day1 = _apply_time_weights(day1_data, time_weights)
            weighted_day2 = _apply_time_weights(day2_data, time_weights)
            weighted_day3 = _apply_time_weights(day3_data, time_weights)

            # Date context
            date_context = {}
            if target_date:
                try:
                    target_dt = datetime.strptime(target_date, "%Y-%m-%d")
                    date_context = {
                        "day_of_week": target_dt.weekday(),
                        "day_of_month": target_dt.day,
                        "month": target_dt.month,
                        "is_weekend": target_dt.weekday() >= 5,
                    }
                except:
                    pass

            # Enhanced features với weights
            features = _extract_enhanced_features(
                weighted_day1, weighted_day2, weighted_day3, date_context, time_weights
            )

            # Dự đoán với enhanced models
            day_predictions = {}
            for day_idx, (day_data, weighted_data) in enumerate(
                [
                    (day1_data, weighted_day1),
                    (day2_data, weighted_day2),
                    (day3_data, weighted_day3),
                ],
                1,
            ):
                prediction = _predict_single_day_enhanced(
                    features,
                    day_data,
                    weighted_data,
                    day_idx,
                    date_context,
                    time_weights,
                )
                day_predictions[f"day_{day_idx}"] = prediction

            # Tìm ngày tốt nhất
            best_day = max(
                day_predictions.keys(), key=lambda k: day_predictions[k]["probability"]
            )
            best_day_num = int(best_day.split("_")[1])

            # Method name
            try:
                method = PredictionMethod.objects.get(id=method_id)
                method_name = method.name
            except PredictionMethod.DoesNotExist:
                method_name = f"Method {method_id}"

            predictions[method_id] = {
                "method_name": method_name,
                "recommended_day": best_day_num,
                "confidence": day_predictions[best_day]["confidence"],
                "day_probabilities": {
                    "day_1": day_predictions["day_1"]["probability"],
                    "day_2": day_predictions["day_2"]["probability"],
                    "day_3": day_predictions["day_3"]["probability"],
                },
                "pattern_info": {
                    "cycle_length": _calculate_cycle_length(
                        day1_data + day2_data + day3_data
                    ),
                    "trend": _calculate_trend(day1_data, day2_data, day3_data),
                    "stability": day_predictions[best_day]["stability"],
                    "adaptive_boost": time_weights["recent_boost"],
                    "data_quality_score": _calculate_method_quality_score(
                        day1_data, day2_data, day3_data
                    ),
                },
            }

        except Exception as e:
            logger.error(f"Enhanced ML error for method {method_id}: {e}")
            continue

    return predictions


def _calculate_adaptive_weights(data_quality):
    """
    ✅ TÍNH ADAPTIVE WEIGHTS DỰA TRÊN CHẤT LƯỢNG DỮ LIỆU
    """
    if not data_quality:
        return {"weights": [1.0], "recent_boost": 1.0}

    avg_data_points = data_quality.get("avg_data_points", 30)
    avg_diversity = data_quality.get("avg_diversity", 0.5)

    # Tạo time weights: dữ liệu gần đây có trọng số cao hơn
    weights = []
    for i in range(int(avg_data_points)):
        # Exponential decay với boost cho recent data
        recent_boost = 1.5 if i >= avg_data_points * 0.8 else 1.0
        weight = np.exp(-0.05 * (avg_data_points - i - 1)) * recent_boost
        weights.append(weight)

    # Normalize weights
    total_weight = sum(weights)
    if total_weight > 0:
        weights = [w / total_weight * len(weights) for w in weights]

    return {
        "weights": weights,
        "recent_boost": 1.5 if avg_diversity > 0.3 else 1.2,
        "quality_multiplier": min(2.0, max(0.5, avg_diversity * 2)),
    }


def _apply_time_weights(data, time_weights):
    """
    ✅ ÁP DỤNG TIME WEIGHTS CHO DỮ LIỆU
    """
    if not time_weights or len(data) != len(time_weights["weights"]):
        return data

    weighted_data = []
    for i, (value, weight) in enumerate(zip(data, time_weights["weights"])):
        # Apply weight bằng cách duplicate data points theo trọng số
        repeat_count = max(1, int(weight * time_weights["quality_multiplier"]))
        weighted_data.extend([value] * repeat_count)

    return weighted_data


def _extract_pattern_features(day1_data, day2_data, day3_data, date_context=None):
    """
    ✅ CẢI TIẾN: Trích xuất features với date context và validation

    Args:
        day1_data, day2_data, day3_data (list): Hit pattern data cho 3 ngày
        date_context (dict, optional): Context về ngày dự đoán

    Returns:
        dict: Features dictionary với kiểu dữ liệu rõ ràng
    """
    features = {}

    # ✅ VALIDATE INPUT DATA
    if not all(isinstance(data, list) for data in [day1_data, day2_data, day3_data]):
        logger.warning("Invalid input data types for pattern features extraction")
        return features

    # Features tổng quan
    all_data = day1_data + day2_data + day3_data
    features["total_hits"] = sum(all_data)
    features["hit_rate"] = sum(all_data) / len(all_data) if all_data else 0.0
    features["data_length"] = len(day1_data)

    # ✅ THÊM DATE CONTEXT FEATURES với validation
    if date_context and isinstance(date_context, dict):
        features["day_of_week"] = int(date_context.get("day_of_week", 0))
        features["day_of_month"] = int(date_context.get("day_of_month", 1))
        features["month"] = int(date_context.get("month", 1))
        features["is_weekend"] = int(bool(date_context.get("is_weekend", False)))

        # Seasonal patterns
        features["is_month_start"] = int(date_context.get("day_of_month", 1) <= 7)
        features["is_month_end"] = int(date_context.get("day_of_month", 1) >= 25)
        features["is_weekday"] = 1 - features["is_weekend"]

        # Cyclic encoding cho day_of_week (0-6)
        dow = features["day_of_week"]
        features["dow_sin"] = float(np.sin(2 * np.pi * dow / 7))
        features["dow_cos"] = float(np.cos(2 * np.pi * dow / 7))

        # Cyclic encoding cho day_of_month (1-31)
        dom = features["day_of_month"]
        features["dom_sin"] = float(np.sin(2 * np.pi * dom / 31))
        features["dom_cos"] = float(np.cos(2 * np.pi * dom / 31))

    else:
        # Default values khi không có date_context
        default_date_features = {
            "day_of_week": 0,
            "day_of_month": 1,
            "month": 1,
            "is_weekend": 0,
            "is_month_start": 0,
            "is_month_end": 0,
            "is_weekday": 1,
            "dow_sin": 0.0,
            "dow_cos": 1.0,
            "dom_sin": 0.0,
            "dom_cos": 1.0,
        }
        features.update(default_date_features)

    # Features theo từng ngày
    for day_idx, day_data in enumerate([day1_data, day2_data, day3_data], 1):
        if not day_data:  # Skip empty data
            continue

        prefix = f"day{day_idx}_"
        features[f"{prefix}hit_rate"] = sum(day_data) / len(day_data)
        features[f"{prefix}total_hits"] = sum(day_data)

        # Recent trend (5 ngày gần nhất)
        recent = day_data[-5:] if len(day_data) >= 5 else day_data
        features[f"{prefix}recent_hit_rate"] = (
            sum(recent) / len(recent) if recent else 0.0
        )

        # Streak analysis
        features[f"{prefix}current_streak"] = _get_current_streak(day_data)
        features[f"{prefix}max_streak"] = _get_max_streak(day_data)

        # Gap analysis
        features[f"{prefix}avg_gap"] = _get_average_gap(day_data)
        features[f"{prefix}last_hit_days_ago"] = _get_days_since_last_hit(day_data)

        # ✅ THÊM MOMENTUM FEATURES
        if len(day_data) >= 3:
            features[f"{prefix}momentum"] = (
                sum(day_data[-3:]) - sum(day_data[-6:-3]) if len(day_data) >= 6 else 0
            )
        else:
            features[f"{prefix}momentum"] = 0

    # Cross-day correlation
    features["day1_day2_correlation"] = _calculate_correlation(day1_data, day2_data)
    features["day2_day3_correlation"] = _calculate_correlation(day2_data, day3_data)
    features["day1_day3_correlation"] = _calculate_correlation(day1_data, day3_data)

    # ✅ VALIDATE OUTPUT - ĐẢM BẢO TẤT CẢ FEATURES LÀ NUMBERS
    validated_features = {}
    for key, value in features.items():
        try:
            validated_features[key] = (
                float(value) if not np.isnan(float(value)) else 0.0
            )
        except (ValueError, TypeError):
            validated_features[key] = 0.0
            logger.warning(f"Invalid feature value for {key}: {value}")

    return validated_features


def _analyze_overall_patterns(patterns_data, predictions, target_date=None):
    """
    ✅ CẢI TIẾN: Phân tích pattern với target date context
    """
    if not predictions:
        return {
            "total_methods": 0,
            "best_overall_day": 1,
            "avg_confidence": 0.0,
            "top_recommendations": [],
            "target_date": target_date,
        }

    # Thống kê ngày tốt nhất
    day_votes = Counter()
    total_confidence = 0

    for pred in predictions.values():
        day_votes[pred["recommended_day"]] += 1
        total_confidence += pred["confidence"]

    best_overall_day = day_votes.most_common(1)[0][0] if day_votes else 1
    avg_confidence = total_confidence / len(predictions)

    # Top recommendations - sắp xếp theo confidence
    top_recommendations = sorted(
        predictions.values(), key=lambda x: x["confidence"], reverse=True
    )[:10]

    return {
        "total_methods": len(predictions),
        "best_overall_day": best_overall_day,
        "avg_confidence": avg_confidence,
        "top_recommendations": top_recommendations,
        "day_distribution": dict(day_votes),
        "target_date": target_date,
        "date_context_available": bool(target_date),
    }


def _combine_pattern_data(current_patterns, historical_patterns):
    """
    Kết hợp dữ liệu hiện tại với lịch sử
    """
    combined = {"hit_day_1": {}, "hit_day_2": {}, "hit_day_3": {}}

    # Lấy tất cả method_ids
    all_method_ids = set()
    for patterns in [current_patterns, historical_patterns]:
        for day_key in ["hit_day_1", "hit_day_2", "hit_day_3"]:
            all_method_ids.update(patterns.get(day_key, {}).keys())

    # Kết hợp dữ liệu cho từng method
    for method_id in all_method_ids:
        for day_key in ["hit_day_1", "hit_day_2", "hit_day_3"]:
            historical_data = historical_patterns.get(day_key, {}).get(
                str(method_id), []
            )
            current_data = current_patterns.get(day_key, {}).get(str(method_id), [])

            # Kết hợp: lịch sử + hiện tại
            combined[day_key][str(method_id)] = historical_data + current_data

    return combined


def _predict_single_day(features, day_data, day_number, date_context=None):
    """
    Dự đoán cho một ngày cụ thể bằng ensemble methods
    ✅ CẢI TIẾN: Enhanced error handling cho single-class data

    Args:
        features (dict): Pattern features đã trích xuất
        day_data (list): Dữ liệu hit pattern cho ngày cụ thể
        day_number (int): Số thứ tự ngày (1, 2, 3)
        date_context (dict, optional): Context về ngày cần dự đoán

    Returns:
        dict: {
            "probability": float,
            "confidence": float,
            "stability": float
        }
    """
    if len(day_data) < 5:
        return {
            "probability": 0.1,
            "confidence": 0.0,
            "stability": 0.0,
            "fallback_reason": "insufficient_data",
        }

    # ✅ KIỂM TRA DATA DIVERSITY TRƯỚC KHI TRAIN MODEL
    unique_values = set(day_data)
    if len(unique_values) < 2:
        # Chỉ có 1 class - không thể train classifier
        single_value = list(unique_values)[0]
        probability = float(single_value)  # 0.0 hoặc 1.0

        # Điều chỉnh probability dựa trên context
        if single_value == 0:
            # Toàn bộ miss - xác suất thấp nhưng không phải 0
            probability = 0.05
        else:
            # Toàn bộ hit - xác suất cao nhưng không phải 1
            probability = 0.95

        # Confidence thấp vì không có diversity
        confidence = 0.3
        stability = 1.0  # Rất stable vì consistent

        logger.info(
            f"Day {day_number}: Single class data detected ({single_value}), "
            f"using statistical fallback: prob={probability}, conf={confidence}"
        )

        return {
            "probability": probability,
            "confidence": confidence,
            "stability": stability,
            "fallback_reason": f"single_class_{single_value}",
        }

    # Chuẩn bị training data từ sliding window
    X, y = _create_training_data(day_data, window_size=5)

    if len(X) < 3:
        # Fallback to simple statistics
        recent_rate = sum(day_data[-5:]) / min(5, len(day_data))
        return {
            "probability": recent_rate,
            "confidence": min(0.6, len(day_data) / 20.0),
            "stability": 1.0 - abs(0.5 - recent_rate),
            "fallback_reason": "insufficient_training_samples",
        }

    # ✅ KIỂM TRA TRAINING DATA DIVERSITY
    unique_y = set(y)
    if len(unique_y) < 2:
        # Training data chỉ có 1 class
        single_y = list(unique_y)[0]

        # Sử dụng overall data statistics
        overall_rate = sum(day_data) / len(day_data)

        # Adjust based on recent trend
        recent_data = day_data[-10:] if len(day_data) >= 10 else day_data
        recent_rate = sum(recent_data) / len(recent_data)

        # Weighted average: 70% recent, 30% overall
        probability = 0.7 * recent_rate + 0.3 * overall_rate

        # Confidence based on data consistency
        variance = np.var(day_data)
        confidence = max(0.4, 1.0 - variance)  # Higher confidence for consistent data
        stability = 1.0 - variance

        logger.info(
            f"Day {day_number}: Training data single class ({single_y}), "
            f"using weighted statistics: prob={probability:.3f}, conf={confidence:.3f}"
        )

        return {
            "probability": float(probability),
            "confidence": float(confidence),
            "stability": float(stability),
            "fallback_reason": f"training_single_class_{single_y}",
        }

    # ✅ THÊM DATE CONTEXT VÀO FEATURES (nếu có)
    enhanced_features = features.copy()
    if date_context:
        enhanced_features.update(
            {
                f"day{day_number}_weekday": date_context.get("day_of_week", 0),
                f"day{day_number}_month_day": date_context.get("day_of_month", 1),
                f"day{day_number}_is_weekend": int(
                    date_context.get("is_weekend", False)
                ),
            }
        )

    # Ensemble của multiple models với better error handling
    models = [
        RandomForestClassifier(
            n_estimators=50, random_state=42, min_samples_split=2, min_samples_leaf=1
        ),
        GradientBoostingClassifier(
            n_estimators=30, random_state=42, min_samples_split=2, min_samples_leaf=1
        ),
    ]

    predictions = []
    confidences = []
    successful_models = 0

    for model_idx, model in enumerate(models):
        try:
            # Train model
            model.fit(X, y)

            # Predict next value
            last_window = np.array(day_data[-5:]).reshape(1, -1)
            prob = model.predict_proba(last_window)[0]

            # Lấy xác suất của class 1 (hit)
            if len(prob) > 1:
                hit_prob = prob[1]
            else:
                # Chỉ có 1 class trong prediction
                hit_prob = prob[0] if y[-1] == 1 else 1 - prob[0]

            predictions.append(hit_prob)

            # Tính confidence từ cross-validation
            if len(X) >= 5:
                try:
                    cv_scores = cross_val_score(model, X, y, cv=min(3, len(X) // 2))
                    confidence = np.mean(cv_scores)
                except Exception as cv_error:
                    logger.warning(
                        f"Cross-validation error for model {model_idx}: {cv_error}"
                    )
                    confidence = 0.5
            else:
                confidence = 0.5

            confidences.append(confidence)
            successful_models += 1

            logger.debug(
                f"Day {day_number} Model {model_idx}: prob={hit_prob:.3f}, conf={confidence:.3f}"
            )

        except Exception as model_error:
            logger.warning(f"Day {day_number} Model {model_idx} error: {model_error}")

            # Fallback prediction based on data statistics
            recent_rate = (
                sum(day_data[-3:]) / 3
                if len(day_data) >= 3
                else sum(day_data) / len(day_data)
            )
            predictions.append(recent_rate)
            confidences.append(0.3)

    # ✅ KIỂM TRA CÓ MODEL NÀO THÀNH CÔNG KHÔNG
    if successful_models == 0:
        # Tất cả models thất bại - sử dụng statistical fallback
        overall_rate = sum(day_data) / len(day_data)
        recent_rate = sum(day_data[-5:]) / min(5, len(day_data))

        # Weighted average với bias về recent data
        probability = 0.6 * recent_rate + 0.4 * overall_rate

        # Confidence thấp do model failure
        confidence = 0.25

        # Stability dựa trên variance
        stability = max(0.0, 1.0 - np.var(day_data))

        logger.warning(
            f"Day {day_number}: All models failed, using statistical fallback"
        )

        return {
            "probability": float(probability),
            "confidence": float(confidence),
            "stability": float(stability),
            "fallback_reason": "all_models_failed",
        }

    # Ensemble prediction (weighted average)
    weights = np.array(confidences)
    weights = (
        weights / np.sum(weights)
        if np.sum(weights) > 0
        else np.ones_like(weights) / len(weights)
    )

    final_probability = np.average(predictions, weights=weights)
    final_confidence = np.mean(confidences)

    # ✅ ĐIỀU CHỈNH PROBABILITY DựA trên DATE CONTEXT
    if date_context:
        # Weekend có thể có pattern khác
        if date_context.get("is_weekend", False):
            final_probability *= 0.95  # Giảm nhẹ 5% cho weekend

        # Đầu tháng/cuối tháng có thể có pattern khác
        day_of_month = date_context.get("day_of_month", 15)
        if day_of_month <= 5:  # Đầu tháng
            final_probability *= 1.02  # Tăng nhẹ 2%
        elif day_of_month >= 25:  # Cuối tháng
            final_probability *= 0.98  # Giảm nhẹ 2%

    # Tính stability
    recent_variance = (
        np.var(day_data[-10:]) if len(day_data) >= 10 else np.var(day_data)
    )
    stability = max(0.0, float(1.0 - recent_variance))

    # ✅ ĐẢM BẢO PROBABILITY TRONG KHOẢNG [0, 1]
    final_probability = max(0.0, min(1.0, float(final_probability)))

    logger.debug(
        f"Day {day_number}: Final prediction - prob={final_probability:.3f}, "
        f"conf={final_confidence:.3f}, stability={stability:.3f}, models={successful_models}"
    )

    return {
        "probability": float(final_probability),
        "confidence": float(final_confidence),
        "stability": float(stability),
        "successful_models": successful_models,
        "total_models": len(models),
    }


def _create_training_data(sequence, window_size=5):
    """
    ✅ CẢI TIẾN: Tạo training data với validation
    """
    if len(sequence) < window_size + 1:
        return np.array([]), np.array([])

    X, y = [], []

    for i in range(window_size, len(sequence)):
        X.append(sequence[i - window_size : i])
        y.append(sequence[i])

    X = np.array(X)
    y = np.array(y)

    # ✅ VALIDATION: Kiểm tra diversity
    unique_y = set(y)
    if len(unique_y) < 2:
        logger.debug(
            f"Training data has only {len(unique_y)} unique class(es): {unique_y}"
        )

    return X, y


# ✅ HELPER FUNCTIONS
def _get_current_streak(data):
    """Tính streak hiện tại (liên tiếp từ cuối)"""
    if not data:
        return 0

    current_value = data[-1]
    streak = 0

    for value in reversed(data):
        if value == current_value:
            streak += 1
        else:
            break

    return streak


def _get_max_streak(data):
    """Tính streak dài nhất"""
    if not data:
        return 0

    max_streak = 1
    current_streak = 1

    for i in range(1, len(data)):
        if data[i] == data[i - 1]:
            current_streak += 1
            max_streak = max(max_streak, current_streak)
        else:
            current_streak = 1

    return max_streak


def _get_average_gap(data):
    """Tính khoảng cách trung bình giữa các lần hit"""
    hit_indices = [i for i, val in enumerate(data) if val == 1]

    if len(hit_indices) < 2:
        return len(data)

    gaps = [hit_indices[i] - hit_indices[i - 1] for i in range(1, len(hit_indices))]
    return sum(gaps) / len(gaps)


def _get_days_since_last_hit(data):
    """Tính số ngày kể từ lần hit cuối"""
    for i in range(len(data) - 1, -1, -1):
        if data[i] == 1:
            return len(data) - 1 - i
    return len(data)


def _calculate_correlation(data1, data2):
    """Tính correlation giữa 2 sequences"""
    if len(data1) != len(data2) or len(data1) < 2:
        return 0.0

    try:
        correlation = np.corrcoef(data1, data2)[0, 1]
        return correlation if not np.isnan(correlation) else 0.0
    except:
        return 0.0


def _calculate_cycle_length(data):
    """Tính độ dài chu kỳ trung bình"""
    hit_indices = [i for i, val in enumerate(data) if val == 1]

    if len(hit_indices) < 3:
        return 0

    gaps = [hit_indices[i] - hit_indices[i - 1] for i in range(1, len(hit_indices))]
    return round(sum(gaps) / len(gaps), 1) if gaps else 0


def _calculate_trend(day1_data, day2_data, day3_data):
    """Tính xu hướng giữa các ngày"""
    rates = [
        sum(day1_data) / len(day1_data) if day1_data else 0,
        sum(day2_data) / len(day2_data) if day2_data else 0,
        sum(day3_data) / len(day3_data) if day3_data else 0,
    ]

    if rates[2] > rates[0]:
        return "increasing"
    elif rates[2] < rates[0]:
        return "decreasing"
    else:
        return "stable"


def _extract_enhanced_features(
    weighted_day1, weighted_day2, weighted_day3, date_context, time_weights
):
    """
    ✅ TRÍCH XUẤT ENHANCED FEATURES CHO ML VỚI ADAPTIVE WEIGHTS

    Args:
        weighted_day1, weighted_day2, weighted_day3 (list): Weighted hit pattern data
        date_context (dict): Context về ngày dự đoán
        time_weights (dict): Adaptive weights configuration

    Returns:
        dict: Enhanced features với kiểu dữ liệu rõ ràng
    """
    features = {}

    # ✅ VALIDATE INPUT DATA
    if not all(
        isinstance(data, list) for data in [weighted_day1, weighted_day2, weighted_day3]
    ):
        logger.warning("Invalid input data types for enhanced features extraction")
        return features

    # Basic features tổng quan
    all_weighted_data = weighted_day1 + weighted_day2 + weighted_day3
    features["total_hits"] = sum(all_weighted_data)
    features["hit_rate"] = (
        sum(all_weighted_data) / len(all_weighted_data) if all_weighted_data else 0.0
    )
    features["data_length"] = len(weighted_day1)

    # ✅ ADAPTIVE WEIGHTS FEATURES
    if time_weights:
        features["recent_boost"] = float(time_weights.get("recent_boost", 1.0))
        features["quality_multiplier"] = float(
            time_weights.get("quality_multiplier", 1.0)
        )
        features["weights_length"] = len(time_weights.get("weights", []))
    else:
        features["recent_boost"] = 1.0
        features["quality_multiplier"] = 1.0
        features["weights_length"] = 0

    # ✅ DATE CONTEXT FEATURES với validation
    if date_context and isinstance(date_context, dict):
        features["day_of_week"] = int(date_context.get("day_of_week", 0))
        features["day_of_month"] = int(date_context.get("day_of_month", 1))
        features["month"] = int(date_context.get("month", 1))
        features["is_weekend"] = int(bool(date_context.get("is_weekend", False)))

        # Enhanced seasonal patterns
        features["is_month_start"] = int(date_context.get("day_of_month", 1) <= 7)
        features["is_month_middle"] = int(
            8 <= date_context.get("day_of_month", 1) <= 23
        )
        features["is_month_end"] = int(date_context.get("day_of_month", 1) >= 24)
        features["is_weekday"] = 1 - features["is_weekend"]

        # ✅ ADVANCED CYCLIC ENCODING
        dow = features["day_of_week"]
        features["dow_sin"] = float(np.sin(2 * np.pi * dow / 7))
        features["dow_cos"] = float(np.cos(2 * np.pi * dow / 7))

        dom = features["day_of_month"]
        features["dom_sin"] = float(np.sin(2 * np.pi * dom / 31))
        features["dom_cos"] = float(np.cos(2 * np.pi * dom / 31))

        month = features["month"]
        features["month_sin"] = float(np.sin(2 * np.pi * month / 12))
        features["month_cos"] = float(np.cos(2 * np.pi * month / 12))

    else:
        # Default values
        default_date_features = {
            "day_of_week": 0,
            "day_of_month": 1,
            "month": 1,
            "is_weekend": 0,
            "is_month_start": 0,
            "is_month_middle": 0,
            "is_month_end": 0,
            "is_weekday": 1,
            "dow_sin": 0.0,
            "dow_cos": 1.0,
            "dom_sin": 0.0,
            "dom_cos": 1.0,
            "month_sin": 0.0,
            "month_cos": 1.0,
        }
        features.update(default_date_features)

    # ✅ ENHANCED FEATURES THEO TỪNG NGÀY
    for day_idx, (weighted_data, original_data) in enumerate(
        [
            (weighted_day1, weighted_day1),
            (weighted_day2, weighted_day2),
            (weighted_day3, weighted_day3),
        ],
        1,
    ):

        if not weighted_data:
            continue

        prefix = f"day{day_idx}_"

        # Basic weighted features
        features[f"{prefix}hit_rate"] = sum(weighted_data) / len(weighted_data)
        features[f"{prefix}total_hits"] = sum(weighted_data)
        features[f"{prefix}data_points"] = len(weighted_data)

        # ✅ ADVANCED TREND ANALYSIS
        if len(weighted_data) >= 5:
            recent = weighted_data[-5:]
            features[f"{prefix}recent_hit_rate"] = sum(recent) / len(recent)

            # Linear trend coefficient
            x = np.arange(len(recent))
            y = np.array(recent)
            if len(x) > 1 and np.var(x) > 0:
                features[f"{prefix}trend_slope"] = float(np.polyfit(x, y, 1)[0])
            else:
                features[f"{prefix}trend_slope"] = 0.0
        else:
            features[f"{prefix}recent_hit_rate"] = features[f"{prefix}hit_rate"]
            features[f"{prefix}trend_slope"] = 0.0

        # ✅ STATISTICAL FEATURES
        features[f"{prefix}variance"] = float(np.var(weighted_data))
        features[f"{prefix}std"] = float(np.std(weighted_data))
        features[f"{prefix}skewness"] = _calculate_skewness(weighted_data)
        features[f"{prefix}kurtosis"] = _calculate_kurtosis(weighted_data)

        # ✅ STREAK & PATTERN FEATURES
        features[f"{prefix}current_streak"] = _get_current_streak(weighted_data)
        features[f"{prefix}max_streak"] = _get_max_streak(weighted_data)
        features[f"{prefix}streak_variance"] = _get_streak_variance(weighted_data)

        # ✅ GAP ANALYSIS
        features[f"{prefix}avg_gap"] = _get_average_gap(weighted_data)
        features[f"{prefix}gap_variance"] = _get_gap_variance(weighted_data)
        features[f"{prefix}last_hit_days_ago"] = _get_days_since_last_hit(weighted_data)

        # ✅ MOMENTUM & ACCELERATION
        if len(weighted_data) >= 6:
            recent_3 = sum(weighted_data[-3:])
            prev_3 = sum(weighted_data[-6:-3])
            features[f"{prefix}momentum"] = recent_3 - prev_3

            # Second derivative (acceleration)
            if len(weighted_data) >= 9:
                old_3 = sum(weighted_data[-9:-6])
                acceleration = (recent_3 - prev_3) - (prev_3 - old_3)
                features[f"{prefix}acceleration"] = acceleration
            else:
                features[f"{prefix}acceleration"] = 0
        else:
            features[f"{prefix}momentum"] = 0
            features[f"{prefix}acceleration"] = 0

        # ✅ FREQUENCY DOMAIN FEATURES (if enough data)
        if len(weighted_data) >= 10:
            # Simple frequency analysis
            features[f"{prefix}dominant_period"] = _find_dominant_period(weighted_data)
            features[f"{prefix}periodicity_strength"] = _calculate_periodicity_strength(
                weighted_data
            )
        else:
            features[f"{prefix}dominant_period"] = 0
            features[f"{prefix}periodicity_strength"] = 0.0

    # ✅ CROSS-DAY CORRELATION & INTERACTION FEATURES
    features["day1_day2_correlation"] = _calculate_correlation(
        weighted_day1, weighted_day2
    )
    features["day2_day3_correlation"] = _calculate_correlation(
        weighted_day2, weighted_day3
    )
    features["day1_day3_correlation"] = _calculate_correlation(
        weighted_day1, weighted_day3
    )

    # Cross-day momentum
    day_rates = [
        sum(weighted_day1) / len(weighted_day1) if weighted_day1 else 0,
        sum(weighted_day2) / len(weighted_day2) if weighted_day2 else 0,
        sum(weighted_day3) / len(weighted_day3) if weighted_day3 else 0,
    ]
    features["cross_day_trend"] = (
        (day_rates[2] - day_rates[0]) / 2 if len(day_rates) == 3 else 0
    )
    features["day2_relative_strength"] = (
        day_rates[1] - np.mean([day_rates[0], day_rates[2]])
        if len(day_rates) == 3
        else 0
    )

    # ✅ ADAPTIVE QUALITY INDICATORS
    features["data_quality_score"] = _calculate_adaptive_quality_score(
        weighted_day1, weighted_day2, weighted_day3, time_weights
    )
    features["prediction_confidence"] = _calculate_prediction_confidence(
        features, time_weights
    )

    # ✅ VALIDATE OUTPUT - ĐẢM BẢO TẤT CẢ FEATURES LÀ NUMBERS
    validated_features = {}
    for key, value in features.items():
        try:
            if isinstance(value, (int, float)) and not np.isnan(float(value)):
                validated_features[key] = float(value)
            else:
                validated_features[key] = 0.0
                logger.debug(f"Invalid feature value for {key}: {value}")
        except (ValueError, TypeError):
            validated_features[key] = 0.0
            logger.warning(f"Failed to convert feature {key}: {value}")

    return validated_features


def _predict_single_day_enhanced(
    features, day_data, weighted_data, day_number, date_context, time_weights
):
    """
    ✅ DỰ ĐOÁN ENHANCED CHO MỘT NGÀY VỚI ADAPTIVE WEIGHTS

    Args:
        features (dict): Enhanced features
        day_data (list): Original day data
        weighted_data (list): Weighted day data
        day_number (int): Day number (1, 2, 3)
        date_context (dict): Date context
        time_weights (dict): Adaptive weights

    Returns:
        dict: Enhanced prediction với confidence, probability, stability
    """
    if len(day_data) < 10:
        return {
            "probability": 0.1,
            "confidence": 0.0,
            "stability": 0.0,
            "fallback_reason": "insufficient_data_enhanced",
        }

    # ✅ KIỂM TRA DATA DIVERSITY
    unique_values = set(day_data)
    if len(unique_values) < 2:
        # Enhanced fallback với time weights
        fallback_prob = _calculate_weighted_fallback_probability(day_data, time_weights)
        return {
            "probability": fallback_prob,
            "confidence": 0.4,  # Higher confidence than basic
            "stability": 1.0,
            "fallback_reason": f"single_class_enhanced_{list(unique_values)[0]}",
        }

    # ✅ ENHANCED TRAINING DATA với weighted samples
    X, y = _create_enhanced_training_data(weighted_data, window_size=5)

    if len(X) < 5:
        # Enhanced statistical fallback
        probability = _calculate_enhanced_statistical_prediction(
            day_data, features, time_weights
        )
        return {
            "probability": probability,
            "confidence": 0.6,
            "stability": 1.0 - np.var(day_data),
            "fallback_reason": "insufficient_training_enhanced",
        }

    # ✅ ENHANCED ENSEMBLE MODELS với feature engineering
    models = [
        RandomForestClassifier(
            n_estimators=100,
            random_state=42,
            min_samples_split=max(2, len(X) // 10),
            min_samples_leaf=1,
            max_features="sqrt",
        ),
        GradientBoostingClassifier(
            n_estimators=50,
            random_state=42,
            min_samples_split=max(2, len(X) // 10),
            min_samples_leaf=1,
            learning_rate=0.1,
        ),
    ]

    predictions = []
    confidences = []
    feature_importances = []
    successful_models = 0

    # ✅ FEATURE ENGINEERING cho enhanced prediction
    enhanced_X = _add_feature_engineering(X, features, day_number)

    for model_idx, model in enumerate(models):
        try:
            # Train với enhanced features
            model.fit(enhanced_X, y)

            # Predict với last window + features
            last_window_enhanced = _prepare_last_window_features(
                weighted_data, features, day_number
            )

            prob = model.predict_proba(last_window_enhanced.reshape(1, -1))[0]

            # Lấy probability cho class 1
            if len(prob) > 1:
                hit_prob = prob[1]
            else:
                hit_prob = prob[0] if y[-1] == 1 else 1 - prob[0]

            # ✅ ADAPTIVE ADJUSTMENT dựa trên time weights
            hit_prob = _apply_adaptive_adjustment(
                hit_prob, time_weights, date_context, day_number
            )

            predictions.append(hit_prob)

            # Enhanced confidence calculation
            if len(enhanced_X) >= 5:
                try:
                    cv_scores = cross_val_score(
                        model, enhanced_X, y, cv=min(3, len(enhanced_X) // 3)
                    )
                    confidence = np.mean(cv_scores) * time_weights.get(
                        "quality_multiplier", 1.0
                    )
                except Exception:
                    confidence = 0.6
            else:
                confidence = 0.6

            confidences.append(min(0.95, confidence))

            # Feature importance (if available)
            if hasattr(model, "feature_importances_"):
                feature_importances.append(model.feature_importances_)

            successful_models += 1

        except Exception as model_error:
            logger.warning(f"Enhanced model {model_idx} error: {model_error}")
            # Enhanced fallback
            fallback_prob = _calculate_enhanced_statistical_prediction(
                day_data, features, time_weights
            )
            predictions.append(fallback_prob)
            confidences.append(0.4)

    # ✅ ENHANCED ENSEMBLE COMBINATION
    if successful_models == 0:
        return {
            "probability": _calculate_enhanced_statistical_prediction(
                day_data, features, time_weights
            ),
            "confidence": 0.3,
            "stability": max(0.0, 1.0 - np.var(day_data)),
            "fallback_reason": "all_enhanced_models_failed",
        }

    # Weighted ensemble với quality-aware weighting
    weights = np.array(confidences)
    weights = weights * time_weights.get("quality_multiplier", 1.0)
    weights = (
        weights / np.sum(weights)
        if np.sum(weights) > 0
        else np.ones_like(weights) / len(weights)
    )

    final_probability = np.average(predictions, weights=weights)
    final_confidence = np.mean(confidences) * time_weights.get("recent_boost", 1.0)

    # ✅ ENHANCED STABILITY CALCULATION
    stability = _calculate_enhanced_stability(
        day_data, weighted_data, features, time_weights
    )

    # ✅ FINAL ADJUSTMENTS
    final_probability = max(0.0, min(1.0, float(final_probability)))
    final_confidence = max(0.0, min(1.0, float(final_confidence)))

    return {
        "probability": final_probability,
        "confidence": final_confidence,
        "stability": float(stability),
        "successful_models": successful_models,
        "total_models": len(models),
        "feature_importance_available": len(feature_importances) > 0,
    }


# ✅ HELPER FUNCTIONS CHO ENHANCED FEATURES


def _calculate_skewness(data):
    """Tính skewness (độ lệch) của dữ liệu"""
    if len(data) < 3:
        return 0.0

    mean_val = np.mean(data)
    std_val = np.std(data)

    if std_val == 0:
        return 0.0

    skew = np.mean([(x - mean_val) ** 3 for x in data]) / (std_val**3)
    return float(skew)


def _calculate_kurtosis(data):
    """Tính kurtosis (độ nhọn) của dữ liệu"""
    if len(data) < 4:
        return 0.0

    mean_val = np.mean(data)
    std_val = np.std(data)

    if std_val == 0:
        return 0.0

    kurt = np.mean([(x - mean_val) ** 4 for x in data]) / (std_val**4) - 3
    return float(kurt)


def _get_streak_variance(data):
    """Tính variance của các streak lengths"""
    if len(data) < 2:
        return 0.0

    streaks = []
    current_streak = 1
    current_value = data[0]

    for i in range(1, len(data)):
        if data[i] == current_value:
            current_streak += 1
        else:
            streaks.append(current_streak)
            current_streak = 1
            current_value = data[i]

    streaks.append(current_streak)

    return float(np.var(streaks)) if len(streaks) > 1 else 0.0


def _get_gap_variance(data):
    """Tính variance của gaps giữa các hits"""
    hit_indices = [i for i, val in enumerate(data) if val == 1]

    if len(hit_indices) < 3:
        return float(len(data))

    gaps = [hit_indices[i] - hit_indices[i - 1] for i in range(1, len(hit_indices))]
    return float(np.var(gaps))


def _find_dominant_period(data):
    """Tìm dominant period trong data"""
    if len(data) < 10:
        return 0

    # Simple autocorrelation approach
    best_period = 0
    max_correlation = 0

    for period in range(2, min(len(data) // 2, 10)):
        correlation = 0
        count = 0

        for i in range(len(data) - period):
            correlation += data[i] * data[i + period]
            count += 1

        if count > 0:
            avg_correlation = correlation / count
            if avg_correlation > max_correlation:
                max_correlation = avg_correlation
                best_period = period

    return best_period


def _calculate_periodicity_strength(data):
    """Tính strength của periodicity"""
    if len(data) < 6:
        return 0.0

    # Simple measure based on autocorrelation at dominant period
    period = _find_dominant_period(data)
    if period == 0:
        return 0.0

    # Calculate autocorrelation at dominant period
    correlation = 0
    count = 0

    for i in range(len(data) - period):
        correlation += data[i] * data[i + period]
        count += 1

    if count > 0:
        strength = correlation / count
        return max(0.0, min(1.0, float(strength)))

    return 0.0


def _calculate_adaptive_quality_score(day1_data, day2_data, day3_data, time_weights):
    """Tính adaptive quality score"""
    all_data = day1_data + day2_data + day3_data

    if len(all_data) == 0:
        return 0.0

    # Base quality metrics
    hit_rate = sum(all_data) / len(all_data)
    diversity = min(hit_rate, 1 - hit_rate) * 2
    length_score = min(1.0, len(all_data) / 50.0)

    # Time weights adjustment
    recent_boost = time_weights.get("recent_boost", 1.0) if time_weights else 1.0
    quality_multiplier = (
        time_weights.get("quality_multiplier", 1.0) if time_weights else 1.0
    )

    # Combined score
    base_score = diversity * 0.4 + length_score * 0.6
    adaptive_score = base_score * recent_boost * quality_multiplier

    return float(min(1.0, adaptive_score))


def _calculate_prediction_confidence(features, time_weights):
    """Tính prediction confidence dựa trên features"""
    # Base confidence từ data quality
    base_confidence = features.get("data_quality_score", 0.5)

    # Adjustments từ various factors
    data_length_factor = min(1.0, features.get("data_length", 0) / 30.0)
    variance_penalty = max(0.0, 1.0 - features.get("day1_variance", 0.5))
    correlation_bonus = abs(features.get("day1_day2_correlation", 0)) * 0.2

    # Time weights boost
    time_boost = time_weights.get("recent_boost", 1.0) if time_weights else 1.0

    confidence = (
        base_confidence * 0.5
        + data_length_factor * 0.3
        + variance_penalty * 0.1
        + correlation_bonus * 0.1
    ) * time_boost

    return float(min(0.95, max(0.1, confidence)))


def _calculate_weighted_fallback_probability(day_data, time_weights):
    """Tính fallback probability với time weights"""
    if not day_data:
        return 0.1

    overall_rate = sum(day_data) / len(day_data)

    # Recent data emphasis
    recent_data = day_data[-5:] if len(day_data) >= 5 else day_data
    recent_rate = sum(recent_data) / len(recent_data) if recent_data else overall_rate

    # Time weights adjustment
    recent_boost = time_weights.get("recent_boost", 1.0) if time_weights else 1.0

    # Weighted combination
    probability = (0.3 * overall_rate + 0.7 * recent_rate) * recent_boost

    return float(max(0.05, min(0.95, probability)))


def _create_enhanced_training_data(weighted_data, window_size=5):
    """Tạo enhanced training data với weighted samples"""
    if len(weighted_data) < window_size + 1:
        return np.array([]), np.array([])

    X, y = [], []

    for i in range(window_size, len(weighted_data)):
        X.append(weighted_data[i - window_size : i])
        y.append(weighted_data[i])

    return np.array(X), np.array(y)


def _add_feature_engineering(X, features, day_number):
    """Add feature engineering cho enhanced model"""
    if len(X) == 0:
        return X

    # Add statistical features từ global features
    additional_features = []
    for i in range(len(X)):
        row_features = [
            features.get(f"day{day_number}_trend_slope", 0),
            features.get(f"day{day_number}_variance", 0),
            features.get(f"day{day_number}_momentum", 0),
            features.get("recent_boost", 1.0),
            features.get("day_of_week", 0) / 7.0,  # Normalized
            features.get("is_weekend", 0),
        ]
        additional_features.append(row_features)

    # Combine original features với additional features
    additional_features = np.array(additional_features)
    enhanced_X = np.hstack([X, additional_features])

    return enhanced_X


def _prepare_last_window_features(weighted_data, features, day_number):
    """Prepare features cho last window prediction"""
    # Last window từ weighted data
    last_window = (
        np.array(weighted_data[-5:])
        if len(weighted_data) >= 5
        else np.array(weighted_data)
    )

    # Pad nếu thiếu
    if len(last_window) < 5:
        padding = np.zeros(5 - len(last_window))
        last_window = np.concatenate([padding, last_window])

    # Additional features
    additional_features = np.array(
        [
            features.get(f"day{day_number}_trend_slope", 0),
            features.get(f"day{day_number}_variance", 0),
            features.get(f"day{day_number}_momentum", 0),
            features.get("recent_boost", 1.0),
            features.get("day_of_week", 0) / 7.0,
            features.get("is_weekend", 0),
        ]
    )

    # Combine
    enhanced_window = np.concatenate([last_window, additional_features])

    return enhanced_window


def _apply_adaptive_adjustment(probability, time_weights, date_context, day_number):
    """Apply adaptive adjustments dựa trên context"""
    adjusted_prob = probability

    # Time weights adjustment
    if time_weights:
        recent_boost = time_weights.get("recent_boost", 1.0)
        adjusted_prob *= recent_boost

    # Date context adjustments
    if date_context:
        # Weekend adjustment
        if date_context.get("is_weekend", False):
            adjusted_prob *= 0.95  # Slight decrease for weekends

        # Month position adjustment
        day_of_month = date_context.get("day_of_month", 15)
        if day_of_month <= 7:  # Beginning of month
            adjusted_prob *= 1.02
        elif day_of_month >= 25:  # End of month
            adjusted_prob *= 0.98

    # Day-specific adjustments
    day_multipliers = {1: 1.0, 2: 0.98, 3: 0.95}  # Day 1 slightly preferred
    adjusted_prob *= day_multipliers.get(day_number, 1.0)

    return max(0.0, min(1.0, float(adjusted_prob)))


def _predict_single_day_basic(features, day_data, day_number):
    """
    ✅ SỬA LỖI: Dữ liệu recent phải lấy từ cuối array
    """
    if len(day_data) < 3:
        return {"probability": 0.1, "confidence": 0.0, "stability": 0.0}

    # ✅ SỬA: Dữ liệu đã được sắp xếp cũ -> mới
    overall_rate = sum(day_data) / len(day_data)
    recent_rate = (
        sum(day_data[-3:]) / 3 if len(day_data) >= 3 else overall_rate
    )  # ✅ ĐÚNG: Lấy 3 ngày gần nhất

    # Weighted average: 60% recent, 40% overall
    probability = 0.6 * recent_rate + 0.4 * overall_rate

    # Confidence dựa trên data length
    confidence = min(0.8, len(day_data) / 20.0)

    # Stability dựa trên variance của recent data
    recent_variance = (
        np.var(day_data[-10:]) if len(day_data) >= 10 else np.var(day_data)
    )  # ✅ ĐÚNG
    stability = max(0.0, 1.0 - recent_variance)

    return {
        "probability": float(probability),
        "confidence": float(confidence),
        "stability": float(stability),
    }


def _extract_basic_features(day1_data, day2_data, day3_data):
    """
    ✅ SỬA LỖI: Recent trend phải lấy từ cuối array
    """
    features = {}

    # Features tổng quan
    all_data = day1_data + day2_data + day3_data
    features["total_hits"] = sum(all_data)
    features["hit_rate"] = sum(all_data) / len(all_data) if all_data else 0.0
    features["data_length"] = len(day1_data)

    # Features cho từng ngày
    for day_idx, day_data in enumerate([day1_data, day2_data, day3_data], 1):
        if not day_data:
            continue

        prefix = f"day{day_idx}_"
        features[f"{prefix}hit_rate"] = sum(day_data) / len(day_data)
        features[f"{prefix}total_hits"] = sum(day_data)

        # ✅ SỬA: Recent trend lấy từ cuối array (ngày gần nhất)
        recent = day_data[-3:] if len(day_data) >= 3 else day_data  # ✅ ĐÚNG
        features[f"{prefix}recent_hit_rate"] = (
            sum(recent) / len(recent) if recent else 0.0
        )

        # ✅ SỬA: Current streak tính từ cuối array về đầu
        features[f"{prefix}current_streak"] = _get_current_streak_fixed(day_data)
        features[f"{prefix}last_hit_days_ago"] = _get_days_since_last_hit_fixed(
            day_data
        )

    return features


def _get_current_streak_fixed(data):
    """
    ✅ SỬA LỖI: Tính streak hiện tại từ ngày gần nhất (cuối array)
    """
    if not data:
        return 0

    current_value = data[-1]  # ✅ ĐÚNG: Ngày gần nhất ở cuối
    streak = 0

    # Đếm ngược từ cuối array về đầu
    for value in reversed(data):
        if value == current_value:
            streak += 1
        else:
            break

    return streak


def _get_days_since_last_hit_fixed(data):
    """
    ✅ SỬA LỖI: Tính ngày kể từ lần hit cuối (từ cuối array)
    """
    if not data:
        return len(data)

    # Tìm hit gần nhất từ cuối array về đầu
    for i in range(len(data) - 1, -1, -1):
        if data[i] == 1:
            return len(data) - 1 - i  # Số ngày kể từ hit đó

    return len(data)  # Không có hit nào


def _calculate_enhanced_statistical_prediction(day_data, features, time_weights):
    """
    ✅ SỬA LỖI: Enhanced statistical prediction với thứ tự đúng
    """
    if not day_data:
        return 0.1

    # ✅ SỬA: Recent data lấy từ cuối array
    overall_rate = sum(day_data) / len(day_data)
    recent_rate = sum(day_data[-5:]) / min(5, len(day_data))  # ✅ ĐÚNG: 5 ngày gần nhất
    median_rate = np.median(day_data)

    # Trend analysis với data đúng thứ tự
    if len(day_data) >= 10:
        # So sánh 5 ngày gần nhất vs 5 ngày trước đó
        recent_5 = day_data[-5:]  # ✅ ĐÚNG: 5 ngày gần nhất
        previous_5 = day_data[-10:-5] if len(day_data) >= 10 else day_data[:-5]

        recent_avg = sum(recent_5) / len(recent_5)
        previous_avg = sum(previous_5) / len(previous_5) if previous_5 else recent_avg

        trend_adjustment = (recent_avg - previous_avg) * 0.1  # Small adjustment
    else:
        trend_adjustment = 0

    # Weighted combination
    weights = [0.3, 0.5, 0.2]  # overall, recent, median
    base_prediction = (
        weights[0] * overall_rate + weights[1] * recent_rate + weights[2] * median_rate
    )

    # Add trend adjustment
    adjusted_prediction = base_prediction + trend_adjustment

    # Time weights boost
    if time_weights:
        adjusted_prediction *= time_weights.get("recent_boost", 1.0)

    return float(max(0.05, min(0.95, adjusted_prediction)))


def _calculate_enhanced_stability(day_data, weighted_data, features, time_weights):
    """Calculate enhanced stability metric"""
    if not day_data:
        return 0.0

    # Multiple stability measures
    variance_stability = max(0.0, 1.0 - float(np.var(day_data)))
    trend_stability = max(0.0, 1.0 - abs(features.get("day1_trend_slope", 0)))

    # Weighted data consistency
    if len(weighted_data) > 1:
        weighted_variance = float(np.var(weighted_data))
        weighted_stability = max(0.0, 1.0 - weighted_variance)
    else:
        weighted_stability = variance_stability

    # Recent stability (last 10 points)
    recent_data = day_data[-10:] if len(day_data) >= 10 else day_data
    recent_stability = (
        max(0.0, float(1.0 - np.var(recent_data))) if len(recent_data) > 1 else 1.0
    )

    # Combined stability
    weights = [0.3, 0.2, 0.3, 0.2]  # variance, trend, weighted, recent
    combined_stability = (
        weights[0] * variance_stability
        + weights[1] * trend_stability
        + weights[2] * weighted_stability
        + weights[3] * recent_stability
    )

    # Time weights adjustment
    if time_weights:
        quality_multiplier = time_weights.get("quality_multiplier", 1.0)
        combined_stability *= quality_multiplier

    return float(max(0.0, min(1.0, combined_stability)))


def _calculate_method_quality_score(day1_data, day2_data, day3_data):
    """
    ✅ TÍNH ĐIỂM CHẤT LƯỢNG CHO METHOD
    """
    all_data = day1_data + day2_data + day3_data

    if len(all_data) == 0:
        return 0.0

    # Data length score
    length_score = min(1.0, len(all_data) / 50.0)

    # Diversity score
    hit_rate = sum(all_data) / len(all_data)
    diversity_score = min(hit_rate, 1 - hit_rate) * 2

    # Consistency across days
    day_rates = []
    for data in [day1_data, day2_data, day3_data]:
        if data:
            day_rates.append(sum(data) / len(data))

    consistency_score = 1.0 - np.var(day_rates) if len(day_rates) > 1 else 1.0

    # Combined score
    quality_score = length_score * 0.4 + diversity_score * 0.4 + consistency_score * 0.2

    return float(max(0.0, min(1.0, float(quality_score))))


@csrf_exempt
@require_http_methods(["GET", "POST"])
def api_comprehensive_historical_data(request):
    """
    API trả về dữ liệu lịch sử comprehensive từ _get_comprehensive_historical_data

    Methods:
        GET: Lấy dữ liệu với query parameters
        POST: Lấy dữ liệu với JSON body

    Query Parameters (GET):
        - target_date: str (YYYY-MM-DD, default: today)
        - method_ids: str (comma-separated method IDs, optional)
        - months_back: int (default: 6)
        - format: str ('detailed'|'summary', default: 'detailed')

    POST Body:
        {
            "target_date": "2024-12-01",
            "method_ids": [1, 2, 3],
            "months_back": 6,
            "format": "detailed"
        }

    Returns:
        {
            "success": bool,
            "data": {
                "hit_day_1": {method_id: [0,1,0,1,...]},
                "hit_day_2": {method_id: [0,1,0,1,...]},
                "hit_day_3": {method_id: [0,1,0,1,...]}
            },
            "metadata": {
                "target_date": str,
                "date_range": {"start": str, "end": str},
                "total_methods": int,
                "avg_data_points": float,
                "data_quality": dict,
                "query_time": float
            }
        }
    """
    try:
        import time

        start_time = time.time()

        # ✅ PARSE PARAMETERS từ GET hoặc POST
        if request.method == "GET":
            target_date = request.GET.get(
                "target_date", date.today().strftime("%Y-%m-%d")
            )
            method_ids_param = request.GET.get("method_ids")
            months_back = int(request.GET.get("months_back", 6))
            format_type = request.GET.get("format", "detailed")

            # Parse method_ids nếu có
            method_ids = None
            if method_ids_param:
                try:
                    method_ids = [
                        int(id.strip())
                        for id in method_ids_param.split(",")
                        if id.strip()
                    ]
                except ValueError:
                    return JsonResponse(
                        {
                            "success": False,
                            "error": "Invalid method_ids format. Use comma-separated integers.",
                        },
                        status=400,
                    )

        elif request.method == "POST":
            try:
                data = json.loads(request.body)
                target_date = data.get("target_date", date.today().strftime("%Y-%m-%d"))
                method_ids = data.get("method_ids")
                months_back = int(data.get("months_back", 6))
                format_type = data.get("format", "detailed")
            except json.JSONDecodeError:
                return JsonResponse(
                    {"success": False, "error": "Invalid JSON format in request body"},
                    status=400,
                )

        # ✅ VALIDATE PARAMETERS
        try:
            target_dt = datetime.strptime(target_date, "%Y-%m-%d").date()
        except ValueError:
            return JsonResponse(
                {
                    "success": False,
                    "error": f"Invalid target_date format. Expected YYYY-MM-DD, got: {target_date}",
                },
                status=400,
            )

        if months_back < 1 or months_back > 24:
            return JsonResponse(
                {"success": False, "error": "months_back must be between 1 and 24"},
                status=400,
            )

        if format_type not in ["detailed", "summary"]:
            return JsonResponse(
                {"success": False, "error": "format must be 'detailed' or 'summary'"},
                status=400,
            )

        # ✅ VALIDATE METHOD_IDS nếu có
        if method_ids:
            if not isinstance(method_ids, list) or not all(
                isinstance(id, int) for id in method_ids
            ):
                return JsonResponse(
                    {
                        "success": False,
                        "error": "method_ids must be a list of integers",
                    },
                    status=400,
                )

            # Kiểm tra methods có tồn tại không
            existing_methods = PredictionMethod.objects.filter(
                id__in=method_ids
            ).values_list("id", flat=True)
            invalid_methods = set(method_ids) - set(existing_methods)
            if invalid_methods:
                return JsonResponse(
                    {
                        "success": False,
                        "error": f"Invalid method IDs: {list(invalid_methods)}",
                    },
                    status=400,
                )

        logger.info(
            f"📊 API comprehensive historical data request: target_date={target_date}, "
            f"methods={len(method_ids) if method_ids else 'all'}, months_back={months_back}"
        )

        # ✅ GỌI HÀM _get_comprehensive_historical_data
        historical_data = _get_comprehensive_historical_data(
            target_date=target_date, method_ids=method_ids, months_back=months_back
        )

        # ✅ TÍNH METADATA
        query_time = time.time() - start_time
        start_date = target_dt - timedelta(days=months_back * 30)

        # Tính thống kê
        total_methods = len(historical_data.get("hit_day_1", {}))
        data_points_per_method = []

        for method_id in historical_data.get("hit_day_1", {}).keys():
            day1_data = historical_data["hit_day_1"][method_id]
            data_points_per_method.append(len(day1_data))

        avg_data_points = (
            np.mean(data_points_per_method) if data_points_per_method else 0
        )

        # ✅ ĐÁNH GIÁ DATA QUALITY
        data_quality = _assess_api_data_quality(historical_data)

        # ✅ FORMAT DỮ LIỆU THEO YÊU CẦU
        if format_type == "summary":
            formatted_data = _format_summary_data(historical_data)
        else:
            formatted_data = historical_data

        # ✅ METADATA RESPONSE
        metadata = {
            "target_date": target_date,
            "date_range": {
                "start": start_date.strftime("%Y-%m-%d"),
                "end": target_date,
            },
            "total_methods": total_methods,
            "avg_data_points": round(avg_data_points, 1),
            "data_quality": data_quality,
            "query_time": round(query_time, 3),
            "months_back": months_back,
            "format": format_type,
            "api_version": "1.0",
            "timestamp": timezone.now().isoformat(),
        }

        # ✅ RESPONSE THEO QUY TẮC GIAO TIẾP DỮ LIỆU
        response_data = {"success": True, "data": formatted_data, "metadata": metadata}

        logger.info(
            f"✅ API response: {total_methods} methods, {avg_data_points:.1f} avg points, {query_time:.3f}s"
        )

        return JsonResponse(response_data, json_dumps_params={"ensure_ascii": False})

    except Exception as e:
        logger.error(f"❌ Error in api_comprehensive_historical_data: {e}")
        return JsonResponse(
            {"success": False, "error": str(e), "error_type": "server_error"},
            status=500,
        )


@csrf_exempt
@require_http_methods(["GET"])
def api_day_detail(request, year, month, day):
    """
    API lấy chi tiết một ngày cụ thể
    """
    try:
        target_date = date(year, month, day)

        sessions = DailyTrackingSession.objects.filter(
            prediction_date=target_date
        ).prefetch_related("method_results__method", "evaluations")

        day_data = []
        for session in sessions:
            session_data = {
                "session_id": session.session_id,
                "cycle_name": (
                    session.cycle.cycle_name if session.cycle else "Auto Import"
                ),
                "methods": [],
            }

            for method_result in session.method_results.all():
                method_data = {
                    "method_name": method_result.method.name,
                    "predicted_numbers": method_result.base_prediction_numbers,
                    "confidence": method_result.overall_confidence,
                    "tracking_results": [],
                }

                # Chi tiết tracking results chỉ khi cần
                for eval in session.evaluations.filter(method_result=method_result):
                    method_data["tracking_results"].append(
                        {
                            "day": eval.days_after_prediction,
                            "hit_count": eval.hit_count,
                            "hit_rate": eval.hit_rate,
                            "hit_numbers": eval.hit_numbers,
                            "actual_numbers": eval.actual_numbers,
                        }
                    )

                session_data["methods"].append(method_data)
            day_data.append(session_data)

        return JsonResponse({"success": True, "data": day_data})

    except Exception as e:
        return JsonResponse({"success": False, "error": str(e)}, status=500)


def _assess_api_data_quality(historical_data):
    """
    ✅ ĐÁNH GIÁ CHẤT LƯỢNG DỮ LIỆU CHO API RESPONSE

    Args:
        historical_data (dict): Data từ _get_comprehensive_historical_data

    Returns:
        dict: {
            "overall_quality": str,
            "total_methods": int,
            "valid_methods": int,
            "insufficient_data_methods": int,
            "single_class_methods": int,
            "avg_data_points": float,
            "data_diversity_score": float,
            "recommendations": list[str]
        }
    """
    quality_metrics = {
        "total_methods": len(historical_data.get("hit_day_1", {})),
        "valid_methods": 0,
        "insufficient_data_methods": 0,
        "single_class_methods": 0,
        "data_points_list": [],
        "diversity_scores": [],
        "recommendations": [],
    }

    for method_id in historical_data.get("hit_day_1", {}).keys():
        day1_data = historical_data["hit_day_1"][method_id]
        day2_data = historical_data.get("hit_day_2", {}).get(method_id, [])
        day3_data = historical_data.get("hit_day_3", {}).get(method_id, [])

        all_data = day1_data + day2_data + day3_data
        data_points = len(day1_data)
        quality_metrics["data_points_list"].append(data_points)

        # Kiểm tra đủ dữ liệu
        if data_points < 10:
            quality_metrics["insufficient_data_methods"] += 1
            continue

        # Kiểm tra diversity
        unique_values = set(all_data)
        if len(unique_values) < 2:
            quality_metrics["single_class_methods"] += 1
            continue

        # Tính diversity score
        hit_rate = sum(all_data) / len(all_data) if all_data else 0
        diversity = min(hit_rate, 1 - hit_rate) * 2
        quality_metrics["diversity_scores"].append(diversity)

        quality_metrics["valid_methods"] += 1

    # Tính metrics tổng hợp
    avg_data_points = (
        np.mean(quality_metrics["data_points_list"])
        if quality_metrics["data_points_list"]
        else 0
    )
    avg_diversity = (
        np.mean(quality_metrics["diversity_scores"])
        if quality_metrics["diversity_scores"]
        else 0
    )

    # Đánh giá overall quality
    valid_ratio = (
        quality_metrics["valid_methods"] / quality_metrics["total_methods"]
        if quality_metrics["total_methods"] > 0
        else 0
    )

    if valid_ratio >= 0.8 and avg_data_points >= 30 and avg_diversity >= 0.3:
        overall_quality = "excellent"
    elif valid_ratio >= 0.6 and avg_data_points >= 20 and avg_diversity >= 0.2:
        overall_quality = "good"
    elif valid_ratio >= 0.4 and avg_data_points >= 10:
        overall_quality = "fair"
    else:
        overall_quality = "poor"

    # Tạo recommendations
    recommendations = []
    if (
        quality_metrics["insufficient_data_methods"]
        > quality_metrics["total_methods"] * 0.3
    ):
        recommendations.append("Cần tăng thời gian thu thập dữ liệu (months_back)")

    if quality_metrics["single_class_methods"] > quality_metrics["total_methods"] * 0.2:
        recommendations.append(
            "Một số methods có dữ liệu không đa dạng, cần kiểm tra logic"
        )

    if avg_data_points < 15:
        recommendations.append("Dữ liệu chưa đủ nhiều để phân tích ML hiệu quả")

    if avg_diversity < 0.2:
        recommendations.append("Dữ liệu thiếu tính đa dạng, cần review methods")

    if not recommendations:
        recommendations.append("Chất lượng dữ liệu tốt, phù hợp cho phân tích ML")

    return {
        "overall_quality": overall_quality,
        "total_methods": quality_metrics["total_methods"],
        "valid_methods": quality_metrics["valid_methods"],
        "insufficient_data_methods": quality_metrics["insufficient_data_methods"],
        "single_class_methods": quality_metrics["single_class_methods"],
        "avg_data_points": round(avg_data_points, 1),
        "data_diversity_score": round(avg_diversity, 3),
        "valid_methods_ratio": round(valid_ratio, 3),
        "recommendations": recommendations,
    }


def _format_summary_data(historical_data):
    """
    ✅ FORMAT DỮ LIỆU DẠNG SUMMARY CHO API

    Args:
        historical_data (dict): Raw data từ _get_comprehensive_historical_data

    Returns:
        dict: {
            "methods_summary": {
                method_id: {
                    "method_name": str,
                    "total_predictions": int,
                    "hit_rates": {"day_1": float, "day_2": float, "day_3": float},
                    "best_day": int,
                    "consistency_score": float
                }
            },
            "overall_statistics": {
                "total_methods": int,
                "avg_hit_rates": {"day_1": float, "day_2": float, "day_3": float},
                "best_overall_day": int
            }
        }
    """
    summary_data = {
        "methods_summary": {},
        "overall_statistics": {
            "total_methods": 0,
            "avg_hit_rates": {"day_1": 0.0, "day_2": 0.0, "day_3": 0.0},
            "best_overall_day": 1,
        },
    }

    day_hit_rates = {"day_1": [], "day_2": [], "day_3": []}

    for method_id in historical_data.get("hit_day_1", {}).keys():
        try:
            # Lấy method name
            method = PredictionMethod.objects.get(id=method_id)
            method_name = method.name
        except PredictionMethod.DoesNotExist:
            method_name = f"Method {method_id}"

        # Tính hit rates cho từng ngày
        method_hit_rates = {}
        method_data_points = {}

        for day_key, day_num in [
            ("hit_day_1", "day_1"),
            ("hit_day_2", "day_2"),
            ("hit_day_3", "day_3"),
        ]:
            day_data = historical_data.get(day_key, {}).get(method_id, [])

            if day_data:
                hit_rate = sum(day_data) / len(day_data)
                method_hit_rates[day_num] = round(hit_rate, 3)
                method_data_points[day_num] = len(day_data)
                day_hit_rates[day_num].append(hit_rate)
            else:
                method_hit_rates[day_num] = 0.0
                method_data_points[day_num] = 0

        # Tìm best day cho method này
        best_day = max(method_hit_rates.keys(), key=lambda k: method_hit_rates[k])
        best_day_num = int(best_day.split("_")[1])

        # Tính consistency score (1 - variance của hit rates)
        hit_rates_values = list(method_hit_rates.values())
        consistency_score = (
            1.0 - np.var(hit_rates_values) if len(hit_rates_values) > 1 else 1.0
        )

        summary_data["methods_summary"][method_id] = {
            "method_name": method_name,
            "total_predictions": method_data_points.get("day_1", 0),
            "hit_rates": method_hit_rates,
            "best_day": best_day_num,
            "consistency_score": round(max(0.0, consistency_score), 3),
            "data_points_per_day": method_data_points,
        }

    # Tính overall statistics
    summary_data["overall_statistics"]["total_methods"] = len(
        summary_data["methods_summary"]
    )

    for day_key in ["day_1", "day_2", "day_3"]:
        if day_hit_rates[day_key]:
            avg_hit_rate = np.mean(day_hit_rates[day_key])
            summary_data["overall_statistics"]["avg_hit_rates"][day_key] = round(
                avg_hit_rate, 3
            )

    # Tìm best overall day
    avg_rates = summary_data["overall_statistics"]["avg_hit_rates"]
    best_overall_day = max(avg_rates.keys(), key=lambda k: avg_rates[k])
    summary_data["overall_statistics"]["best_overall_day"] = int(
        best_overall_day.split("_")[1]
    )

    return summary_data


@csrf_exempt
@require_http_methods(["GET"])
def api_method_historical_summary(request, method_id):
    """
    API lấy summary lịch sử cho một method cụ thể

    Args:
        method_id (int): ID của method

    Query Parameters:
        - months_back: int (default: 6)
        - target_date: str (YYYY-MM-DD, default: today)

    Returns:
        {
            "success": bool,
            "data": {
                "method_info": {"id": int, "name": str, "category": str},
                "historical_performance": {
                    "day_1": {"hit_rate": float, "total_predictions": int, "recent_trend": str},
                    "day_2": {...},
                    "day_3": {...}
                },
                "recommendations": {
                    "best_day": int,
                    "confidence": float,
                    "strategy": str
                }
            }
        }
    """
    try:
        # Validate method existence
        try:
            method = PredictionMethod.objects.get(id=method_id)
        except PredictionMethod.DoesNotExist:
            return JsonResponse(
                {"success": False, "error": f"Method with ID {method_id} not found"},
                status=404,
            )

        # Parse parameters
        months_back = int(request.GET.get("months_back", 6))
        target_date = request.GET.get("target_date", date.today().strftime("%Y-%m-%d"))

        # Get historical data for this method
        historical_data = _get_comprehensive_historical_data(
            target_date=target_date, method_ids=[method_id], months_back=months_back
        )

        # Analyze performance
        method_performance = _analyze_single_method_performance(
            historical_data, method_id, method
        )

        response_data = {
            "success": True,
            "data": {
                "method_info": {
                    "id": method.id,
                    "name": method.name,
                    "category": method.category,
                    "is_active": method.is_active,
                },
                "historical_performance": method_performance["performance"],
                "recommendations": method_performance["recommendations"],
                "data_period": {
                    "target_date": target_date,
                    "months_back": months_back,
                    "total_data_points": method_performance["total_data_points"],
                },
            },
        }

        return JsonResponse(response_data, json_dumps_params={"ensure_ascii": False})

    except Exception as e:
        logger.error(f"❌ Error in api_method_historical_summary: {e}")
        return JsonResponse({"success": False, "error": str(e)}, status=500)


def _analyze_single_method_performance(historical_data, method_id, method):
    """
    ✅ PHÂN TÍCH PERFORMANCE CHO MỘT METHOD CỤ THỂ

    Returns:
        dict: {
            "performance": {"day_1": {...}, "day_2": {...}, "day_3": {...}},
            "recommendations": {...},
            "total_data_points": int
        }
    """
    performance = {}
    total_data_points = 0

    for day_key, day_name in [
        ("hit_day_1", "day_1"),
        ("hit_day_2", "day_2"),
        ("hit_day_3", "day_3"),
    ]:
        day_data = historical_data.get(day_key, {}).get(method_id, [])

        if day_data:
            hit_rate = sum(day_data) / len(day_data)
            total_hits = sum(day_data)
            total_predictions = len(day_data)

            # Recent trend (last 10 predictions)
            recent_data = day_data[-10:] if len(day_data) >= 10 else day_data
            recent_hit_rate = sum(recent_data) / len(recent_data) if recent_data else 0

            if recent_hit_rate > hit_rate + 0.05:
                trend = "improving"
            elif recent_hit_rate < hit_rate - 0.05:
                trend = "declining"
            else:
                trend = "stable"

            performance[day_name] = {
                "hit_rate": round(hit_rate, 3),
                "total_hits": total_hits,
                "total_predictions": total_predictions,
                "recent_hit_rate": round(recent_hit_rate, 3),
                "recent_trend": trend,
                "consistency": (
                    round(1.0 - np.var(day_data), 3) if len(day_data) > 1 else 1.0
                ),
            }

            if day_name == "day_1":
                total_data_points = total_predictions
        else:
            performance[day_name] = {
                "hit_rate": 0.0,
                "total_hits": 0,
                "total_predictions": 0,
                "recent_hit_rate": 0.0,
                "recent_trend": "no_data",
                "consistency": 0.0,
            }

    # Generate recommendations
    recommendations = _generate_method_recommendations(performance, method)

    return {
        "performance": performance,
        "recommendations": recommendations,
        "total_data_points": total_data_points,
    }


def _generate_method_recommendations(performance, method):
    """
    ✅ TẠO RECOMMENDATIONS CHO METHOD
    """
    # Find best day
    best_day = 1
    best_hit_rate = 0

    for day_name, data in performance.items():
        if data["hit_rate"] > best_hit_rate:
            best_hit_rate = data["hit_rate"]
            best_day = int(day_name.split("_")[1])

    # Calculate overall confidence
    hit_rates = [data["hit_rate"] for data in performance.values()]
    avg_hit_rate = np.mean(hit_rates)
    consistency = np.mean([data["consistency"] for data in performance.values()])

    confidence = avg_hit_rate * 0.7 + consistency * 0.3

    # Generate strategy
    if best_hit_rate >= 0.3:
        strategy = f"Khuyến nghị đánh khung ngày {best_day} - tỷ lệ trúng cao"
    elif best_hit_rate >= 0.2:
        strategy = f"Cân nhắc đánh khung ngày {best_day} - tỷ lệ trúng trung bình"
    elif best_hit_rate >= 0.1:
        strategy = f"Thận trọng với ngày {best_day} - tỷ lệ trúng thấp"
    else:
        strategy = "Không khuyến nghị - hiệu suất kém"

    return {
        "best_day": best_day,
        "best_day_hit_rate": round(best_hit_rate, 3),
        "confidence": round(confidence, 3),
        "strategy": strategy,
        "overall_assessment": _assess_method_quality(avg_hit_rate, consistency),
    }


def _validate_data_order_for_ml(patterns_data):
    """
    Validation để đảm bảo dữ liệu được sắp xếp đúng thứ tự cho ML
    """
    if not patterns_data or not patterns_data.get("hit_day_1"):
        logger.warning("⚠️ No data to validate")
        return False

    sample_method = list(patterns_data["hit_day_1"].keys())[0]
    sample_data = patterns_data["hit_day_1"][sample_method]

    if len(sample_data) < 5:
        logger.warning(
            f"⚠️ Insufficient data for method {sample_method}: {len(sample_data)} points"
        )
        return False

    logger.info(
        f"✅ Data validation passed: {len(sample_data)} points for method {sample_method}"
    )
    return True


def _assess_method_quality(avg_hit_rate, consistency):
    """
    ✅ ĐÁNH GIÁ CHẤT LƯỢNG METHOD
    """
    if avg_hit_rate >= 0.25 and consistency >= 0.7:
        return "excellent"
    elif avg_hit_rate >= 0.15 and consistency >= 0.5:
        return "good"
    elif avg_hit_rate >= 0.1:
        return "average"
    else:
        return "poor"

@csrf_exempt
@require_http_methods(["POST"])
def api_method_analysis_by_date(request):
    """
    API phân tích method theo ngày được chọn - CẢI TIẾN LOGIC
    
    ✅ LOGIC MỚI:
    1. Ưu tiên sử dụng data có sẵn trong DB
    2. Chỉ tạo session mới khi thực sự cần thiết
    3. Fallback sang pattern data nếu không có session
    """
    try:
        # Parse request
        data = json.loads(request.body)
        selected_date_str = data.get('selected_date')
        method_ids = data.get('method_ids', [])
        
        if not selected_date_str:
            return JsonResponse({
                "success": False,
                "error": "selected_date is required"
            }, status=400)
        
        # Parse date
        try:
            selected_date = datetime.strptime(selected_date_str, "%Y-%m-%d").date()
        except ValueError:
            return JsonResponse({
                "success": False,
                "error": "Invalid date format. Use YYYY-MM-DD"
            }, status=400)
        
        logger.info(f"📊 API method analysis for date: {selected_date}")
        
        # ✅ STRATEGY 1: SỬ DỤNG DATA CÓ SẴN TRƯỚC
        existing_data = _get_existing_analysis_data(selected_date, method_ids)
        
        if existing_data["has_sufficient_data"]:
            logger.info(f"✅ Using existing data for {selected_date}")
            
            # ✅ SỬA LỖI: Clean data trước khi return JSON
            cleaned_data = _clean_data_for_json_response(existing_data)
            
            return JsonResponse({
                "success": True,
                "data": {
                    "analysis_date": selected_date_str,
                    "method_analysis": cleaned_data["method_analysis"],
                    "prediction_numbers": cleaned_data["prediction_numbers"],
                    "has_data": True,
                    "data_source": cleaned_data["data_source"],
                    "session_info": cleaned_data.get("session_info", {})
                }
            }, encoder=NumpyJSONEncoder)
        
        # ✅ STRATEGY 2: FALLBACK SANG PATTERN DATA
        logger.info(f"📊 Using pattern data fallback for {selected_date}")
        pattern_analysis = _get_pattern_based_analysis(selected_date, method_ids)
        
        # ✅ SỬA LỖI: Clean pattern analysis data
        cleaned_pattern_analysis = _clean_data_for_json_response(pattern_analysis)
        
        return JsonResponse({
            "success": True,
            "data": {
                "analysis_date": selected_date_str,
                "method_analysis": cleaned_pattern_analysis["method_analysis"],
                "prediction_numbers": cleaned_pattern_analysis["prediction_numbers"],
                "has_data": True,
                "data_source": "pattern_data",
                "session_info": {"note": "Generated from pattern data"}
            }
        }, encoder=NumpyJSONEncoder)
        
    except Exception as e:
        logger.error(f"❌ Error in api_method_analysis_by_date: {e}")
        return JsonResponse({
            "success": False,
            "error": str(e)
        }, status=500)


def _clean_data_for_json_response(data: dict) -> dict:
    """
    ✅ CLEAN DATA CHO JSON RESPONSE - SỬA LỖI SET SERIALIZATION
    
    Args:
        data (dict): Raw data có thể chứa set, numpy types, etc.
        
    Returns:
        dict: Cleaned data safe for JSON serialization
    """
    if isinstance(data, dict):
        cleaned = {}
        for key, value in data.items():
            cleaned[key] = _clean_data_for_json_response(value)
        return cleaned
    elif isinstance(data, list):
        return [_clean_data_for_json_response(item) for item in data]
    elif isinstance(data, set):
        # ✅ CONVERT SET TO SORTED LIST
        return sorted(list(data))
    elif isinstance(data, (np.integer, int)):
        return int(data)
    elif isinstance(data, (np.floating, float)):
        if np.isnan(data) or np.isinf(data):
            return 0.0
        return float(data)
    elif isinstance(data, np.ndarray):
        return data.tolist()
    elif isinstance(data, (np.bool_, bool)):
        return bool(data)
    elif hasattr(data, 'isoformat'):  # datetime objects
        return data.isoformat()
    else:
        return data
    
def _get_existing_analysis_data(selected_date: date, method_ids: list = None) -> dict:
    """
    ✅ LẤY DỮ LIỆU PHÂN TÍCH CÓ SẴN - KHÔNG TẠO MỚI
    
    Returns:
        dict: {
            "has_sufficient_data": bool,
            "method_analysis": dict,
            "prediction_numbers": dict,
            "data_source": str,
            "session_info": dict
        }
    """
    result = {
        "has_sufficient_data": False,
        "method_analysis": {},
        "prediction_numbers": {},
        "data_source": "none",
        "session_info": {}
    }
    
    # ✅ 1. KIỂM TRA SESSION CÓ SẴN
    existing_session = DailyTrackingSession.objects.filter(
        prediction_date=selected_date
    ).prefetch_related("method_results__method").first()
    
    if existing_session and existing_session.method_results.exists():
        logger.info(f"📊 Found existing session: {existing_session.session_id}")
        
        # Lấy method analysis từ session có sẵn
        method_analysis = _get_method_analysis_from_existing_session(
            existing_session, method_ids
        )
        
        # Lấy prediction numbers từ session có sẵn
        prediction_numbers = _get_prediction_numbers_from_existing_session(
            existing_session, method_analysis
        )
        
        result.update({
            "has_sufficient_data": True,
            "method_analysis": method_analysis,
            "prediction_numbers": prediction_numbers,
            "data_source": "existing_session",
            "session_info": {
                "session_id": existing_session.session_id,
                "created": existing_session.created_at.isoformat(),
                "method_count": existing_session.method_results.count()
            }
        })
        
        return result
    
    # ✅ 2. KIỂM TRA EVALUATION DATA CÓ SẴN
    evaluations = TrackingEvaluation.objects.filter(
        method_result__session__prediction_date=selected_date
    ).select_related("method_result__method", "method_result__session")
    
    if evaluations.exists():
        logger.info(f"📊 Found existing evaluations: {evaluations.count()}")
        
        method_analysis = _get_method_analysis_from_evaluations(
            evaluations, selected_date, method_ids
        )
        
        prediction_numbers = _get_prediction_numbers_from_evaluations(
            evaluations, method_analysis, selected_date
        )
        
        result.update({
            "has_sufficient_data": True,
            "method_analysis": method_analysis,
            "prediction_numbers": prediction_numbers,
            "data_source": "existing_evaluations",
            "session_info": {"evaluations_count": evaluations.count()}
        })
        
        return result
    
    logger.info(f"📊 No sufficient existing data for {selected_date}")
    return result


def _get_method_analysis_from_existing_session(session: DailyTrackingSession, method_ids: list = None) -> dict:
    """
    ✅ LẤY METHOD ANALYSIS TỪ SESSION CÓ SẴN
    """
    method_analysis = {
        "method_trends": {},
        "method_cycles": {},
        "method_recommendations": {},
        "day_by_day_analysis": {},
    }
    
    method_results = session.method_results.select_related("method").all()
    
    if method_ids:
        method_results = method_results.filter(method_id__in=method_ids)
    
    for method_result in method_results:
        method_id = method_result.method.id
        
        # Basic trends từ confidence
        confidence = method_result.overall_confidence
        
        method_analysis["method_trends"][method_id] = {
            "method_name": method_result.method.name,
            "trend_direction": "stable",
            "recent_performance": confidence,
            "stability": min(confidence * 1.2, 100),
        }
        
        method_analysis["method_cycles"][method_id] = {
            "cycle_length": 7,
            "hit_frequency": confidence * 0.8,
            "last_hit_days_ago": 3,
            "next_expected_hit": "medium",
        }
        
        # Risk level dựa trên confidence
        if confidence >= 70:
            risk_level = "low"
        elif confidence >= 50:
            risk_level = "medium"
        elif confidence >= 30:
            risk_level = "high"
        else:
            risk_level = "very_high"
        
        method_analysis["method_recommendations"][method_id] = {
            "score": confidence,
            "confidence": confidence,
            "reason": f"Dựa trên độ tin cậy: {confidence}%",
            "risk_level": risk_level,
        }
        
        # Day-by-day analysis từ method results
        method_analysis["day_by_day_analysis"][method_id] = {
            "day_1": {"hit_probability": confidence * 0.8, "avg_hit_rate": confidence * 0.6, "sample_size": 10, "confidence": "medium"},
            "day_2": {"hit_probability": confidence * 0.7, "avg_hit_rate": confidence * 0.5, "sample_size": 10, "confidence": "medium"},
            "day_3": {"hit_probability": confidence * 0.6, "avg_hit_rate": confidence * 0.4, "sample_size": 10, "confidence": "medium"},
            "best_day": 1,
            "recommended_strategy": f"Khuyến nghị đánh ngày 1 - độ tin cậy {confidence}%"
        }
    
    return method_analysis


def _get_prediction_numbers_from_existing_session(session: DailyTrackingSession, method_analysis: dict) -> dict:
    """
    ✅ LẤY PREDICTION NUMBERS TỪ SESSION CÓ SẴN - SỬA LỖI SET
    """
    prediction_numbers = {}
    
    # Lấy low risk methods
    low_risk_methods = []
    method_recommendations = method_analysis.get("method_recommendations", {})
    
    for method_id, recommendation in method_recommendations.items():
        if recommendation.get("risk_level") in ["low", "medium"]:
            low_risk_methods.append(int(method_id))
    
    # Nếu không có low risk methods, lấy tất cả
    if not low_risk_methods:
        low_risk_methods = list(session.method_results.values_list('method_id', flat=True))
    
    # Tạo prediction numbers cho 3 ngày
    for day in range(1, 4):
        tracking_date = session.prediction_date + timedelta(days=day-1)
        
        # Collect numbers từ low risk methods
        day_numbers = []
        for method_result in session.method_results.filter(method_id__in=low_risk_methods):
            if method_result.base_prediction_numbers:
                day_numbers.extend(method_result.base_prediction_numbers)
        
        # ✅ SỬA LỖI: Remove duplicates và convert set to list
        unique_numbers = sorted(list(set(day_numbers)))
        
        # Kiểm tra actual results
        try:
            actual_result = KetQuaXoSo.objects.get(ngay=tracking_date)
            actual_numbers = list(actual_result.get_all_2digit_numbers())  # ✅ Convert to list
            hit_numbers = [num for num in unique_numbers if num in actual_numbers]
            hit_rate = (len(hit_numbers) / len(unique_numbers) * 100) if unique_numbers else 0
            
            prediction_numbers[f"day_{day}"] = {
                "date": tracking_date.strftime("%Y-%m-%d"),
                "low_risk_numbers": unique_numbers,  # Already list
                "hit_numbers": hit_numbers,          # Already list
                "actual_numbers": actual_numbers,    # ✅ Now list instead of set
                "hit_rate": round(hit_rate, 1),
                "total_predictions": len(unique_numbers),
                "no_data": False
            }
        except KetQuaXoSo.DoesNotExist:
            prediction_numbers[f"day_{day}"] = {
                "date": tracking_date.strftime("%Y-%m-%d"),
                "low_risk_numbers": unique_numbers,
                "hit_numbers": [],
                "actual_numbers": [],
                "hit_rate": 0,
                "total_predictions": len(unique_numbers),
                "no_data": False
            }
    
    return prediction_numbers


def _get_pattern_based_analysis(selected_date: date, method_ids: list = None) -> dict:
    """
    ✅ LẤY PHÂN TÍCH DỰA TRÊN PATTERN DATA
    """
    # Sử dụng DataService để lấy pattern data
    from predictions_tracker.core.services.DataService import data_service
    
    target_date = selected_date.strftime("%Y-%m-%d")
    pattern_data = data_service.get_pattern_data_for_analysis(
        target_date=target_date,
        method_ids=method_ids,
        months_back=3,
        min_data_points=5
    )
    
    # Generate method analysis từ pattern data
    method_analysis = {
        "method_trends": {},
        "method_cycles": {},
        "method_recommendations": {},
        "day_by_day_analysis": {},
    }
    
    prediction_numbers = {}
    
    # Process pattern data
    for method_id in pattern_data.get("hit_day_1", {}).keys():
        try:
            method_id_int = int(method_id)
            
            # Get method info
            try:
                method = PredictionMethod.objects.get(id=method_id_int)
                method_name = method.name
            except PredictionMethod.DoesNotExist:
                method_name = f"Method {method_id}"
            
            # Calculate basic stats từ pattern data
            day1_data = pattern_data.get("hit_day_1", {}).get(method_id, [])
            day2_data = pattern_data.get("hit_day_2", {}).get(method_id, [])
            day3_data = pattern_data.get("hit_day_3", {}).get(method_id, [])
            
            if day1_data:
                avg_hit_rate = sum(day1_data) / len(day1_data) * 100
                stability = max(0, 100 - (np.var(day1_data) * 100))
                
                method_analysis["method_trends"][method_id_int] = {
                    "method_name": method_name,
                    "trend_direction": "stable",
                    "recent_performance": avg_hit_rate,
                    "stability": stability,
                }
                
                method_analysis["method_cycles"][method_id_int] = {
                    "cycle_length": 7,
                    "hit_frequency": avg_hit_rate,
                    "last_hit_days_ago": 2,
                    "next_expected_hit": "medium",
                }
                
                # Risk level
                if avg_hit_rate >= 25:
                    risk_level = "low"
                elif avg_hit_rate >= 15:
                    risk_level = "medium"
                elif avg_hit_rate >= 10:
                    risk_level = "high"
                else:
                    risk_level = "very_high"
                
                method_analysis["method_recommendations"][method_id_int] = {
                    "score": min(avg_hit_rate * 3, 100),
                    "confidence": min(avg_hit_rate * 2, 100),
                    "reason": f"Dựa trên pattern data: {avg_hit_rate:.1f}%",
                    "risk_level": risk_level,
                }
                
                # Day-by-day analysis
                day_analysis = {}
                for day_num, day_data in enumerate([day1_data, day2_data, day3_data], 1):
                    if day_data:
                        day_hit_rate = sum(day_data) / len(day_data) * 100
                        day_analysis[f"day_{day_num}"] = {
                            "hit_probability": day_hit_rate,
                            "avg_hit_rate": day_hit_rate,
                            "sample_size": len(day_data),
                            "confidence": "medium" if len(day_data) >= 10 else "low"
                        }
                    else:
                        day_analysis[f"day_{day_num}"] = {
                            "hit_probability": 0,
                            "avg_hit_rate": 0,
                            "sample_size": 0,
                            "confidence": "no_data"
                        }
                
                day_analysis.update({
                    "best_day": 1,
                    "recommended_strategy": f"Pattern-based strategy cho {method_name}"
                })
                
                method_analysis["day_by_day_analysis"][method_id_int] = day_analysis
                
        except (ValueError, Exception) as e:
            logger.warning(f"Error processing pattern data for method {method_id}: {e}")
            continue
    
    # Generate prediction numbers từ pattern analysis
    for day in range(1, 4):
        tracking_date = selected_date + timedelta(days=day-1)
        
        prediction_numbers[f"day_{day}"] = {
            "date": tracking_date.strftime("%Y-%m-%d"),
            "low_risk_numbers": [],
            "hit_numbers": [],
            "actual_numbers": [],
            "hit_rate": 0,
            "total_predictions": 0,
            "no_data": True,
            "note": "Generated from pattern data"
        }
    
    return {
        "method_analysis": method_analysis,
        "prediction_numbers": prediction_numbers
    }


def _get_method_analysis_from_evaluations(evaluations, selected_date: date, method_ids: list = None) -> dict:
    """
    ✅ LẤY METHOD ANALYSIS TỪ EVALUATIONS CÓ SẴN
    """
    method_analysis = {
        "method_trends": {},
        "method_cycles": {},
        "method_recommendations": {},
        "day_by_day_analysis": {},
    }
    
    # Group evaluations theo method
    methods_evals = {}
    for eval in evaluations:
        method_id = eval.method_result.method.id
        if method_ids and method_id not in method_ids:
            continue
            
        if method_id not in methods_evals:
            methods_evals[method_id] = {
                "method_name": eval.method_result.method.name,
                "evaluations": [],
            }
        
        # Calculate tracking_day
        prediction_date = eval.method_result.session.prediction_date
        evaluation_date = eval.evaluation_date
        days_diff = (evaluation_date - prediction_date).days
        tracking_day = min(max(days_diff, 1), 3)
        
        methods_evals[method_id]["evaluations"].append({
            "date": eval.evaluation_date.isoformat(),
            "hit_rate": eval.hit_rate,
            "hit_count": eval.hit_count,
            "wilson_score": eval.wilson_score,
            "tracking_day": tracking_day,
            "prediction_date": prediction_date.isoformat(),
        })
    
    # Analyze each method
    for method_id, data in methods_evals.items():
        evals = data["evaluations"]
        method_name = data["method_name"]
        
        if not evals:
            continue
            
        # Calculate basic stats
        avg_hit_rate = sum(e["hit_rate"] for e in evals) / len(evals)
        avg_wilson = sum(e["wilson_score"] for e in evals) / len(evals)
        
        method_analysis["method_trends"][method_id] = {
            "method_name": method_name,
            "trend_direction": "stable",
            "recent_performance": avg_hit_rate,
            "stability": avg_wilson * 100,
        }
        
        method_analysis["method_cycles"][method_id] = {
            "cycle_length": 7,
            "hit_frequency": avg_hit_rate,
            "last_hit_days_ago": 1,
            "next_expected_hit": "soon",
        }
        
        # Risk level
        if avg_hit_rate >= 25:
            risk_level = "low"
        elif avg_hit_rate >= 15:
            risk_level = "medium"
        elif avg_hit_rate >= 10:
            risk_level = "high"
        else:
            risk_level = "very_high"
        
        method_analysis["method_recommendations"][method_id] = {
            "score": min(avg_hit_rate * 3, 100),
            "confidence": min(avg_hit_rate * 2.5, 100),
            "reason": f"Dựa trên {len(evals)} evaluations",
            "risk_level": risk_level,
        }
        
        # Day-by-day analysis từ evaluations
        day_analysis = _analyze_tracking_by_day(evals)
        method_analysis["day_by_day_analysis"][method_id] = day_analysis
    
    return method_analysis


def _get_prediction_numbers_from_evaluations(evaluations, method_analysis: dict, selected_date: date) -> dict:
    """
    ✅ LẤY PREDICTION NUMBERS TỪ EVALUATIONS
    """
    prediction_numbers = {}
    
    # Get session từ evaluations
    sessions = set()
    for eval in evaluations:
        sessions.add(eval.method_result.session)
    
    if not sessions:
        return {}
    
    # Sử dụng session đầu tiên
    session = list(sessions)[0]
    
    # Get low risk methods
    low_risk_methods = []
    method_recommendations = method_analysis.get("method_recommendations", {})
    
    for method_id, recommendation in method_recommendations.items():
        if recommendation.get("risk_level") in ["low", "medium"]:
            low_risk_methods.append(int(method_id))
    
    if not low_risk_methods:
        low_risk_methods = list(session.method_results.values_list('method_id', flat=True))
    
    # Generate prediction numbers
    for day in range(1, 4):
        tracking_date = selected_date + timedelta(days=day-1)
        
        # Collect numbers
        day_numbers = []
        for method_result in session.method_results.filter(method_id__in=low_risk_methods):
            if method_result.base_prediction_numbers:
                day_numbers.extend(method_result.base_prediction_numbers)
        
        unique_numbers = sorted(list(set(day_numbers)))
        
        # Check actual results
        try:
            actual_result = KetQuaXoSo.objects.get(ngay=tracking_date)
            actual_numbers = actual_result.get_all_2digit_numbers()
            hit_numbers = [num for num in unique_numbers if num in actual_numbers]
            hit_rate = (len(hit_numbers) / len(unique_numbers) * 100) if unique_numbers else 0
            
            prediction_numbers[f"day_{day}"] = {
                "date": tracking_date.strftime("%Y-%m-%d"),
                "low_risk_numbers": unique_numbers,
                "hit_numbers": hit_numbers,
                "actual_numbers": actual_numbers,
                "hit_rate": round(hit_rate, 1),
                "total_predictions": len(unique_numbers),
                "no_data": False
            }
        except KetQuaXoSo.DoesNotExist:
            prediction_numbers[f"day_{day}"] = {
                "date": tracking_date.strftime("%Y-%m-%d"),
                "low_risk_numbers": unique_numbers,
                "hit_numbers": [],
                "actual_numbers": [],
                "hit_rate": 0,
                "total_predictions": len(unique_numbers),
                "no_data": False
            }
    
    return prediction_numbers



def _check_data_availability_for_date(selected_date: date) -> dict:
    """
    ✅ KIỂM TRA DỮ LIỆU CÓ SẴN CHO NGÀY ĐƯỢC CHỌN
    
    Returns:
        dict: {
            "has_session_data": bool,
            "has_pattern_data": bool,
            "data_source": str,
            "quality_info": dict
        }
    """
    # Kiểm tra session data
    session_exists = DailyTrackingSession.objects.filter(
        prediction_date=selected_date
    ).exists()
    
    # Kiểm tra pattern data từ DataService
    pattern_data = data_service.get_pattern_data_for_analysis(
        target_date=selected_date.strftime("%Y-%m-%d"),
        method_ids=None,
        months_back=1,  # Chỉ kiểm tra 1 tháng gần nhất
        min_data_points=1
    )
    
    has_pattern_data = bool(pattern_data.get("hit_day_1"))
    
    # Xác định data source
    if session_exists and has_pattern_data:
        data_source = "mixed"
    elif session_exists:
        data_source = "evaluation"
    elif has_pattern_data:
        data_source = "pattern"
    else:
        data_source = "none"
    
    return {
        "has_session_data": session_exists,
        "has_pattern_data": has_pattern_data,
        "data_source": data_source,
        "quality_info": {
            "sessions_count": DailyTrackingSession.objects.filter(
                prediction_date=selected_date
            ).count(),
            "pattern_methods_count": len(pattern_data.get("hit_day_1", {}))
        }
    }

# ✅ CẬP NHẬT HÀM _get_prediction_numbers_for_3_days
def _get_prediction_numbers_for_3_days(selected_date: date, method_analysis: dict) -> dict:
    """
    ✅ SỬA LỖI: LẤY SỐ DỰ ĐOÁN CHO 3 NGÀY TỪNG NGÀY ĐƯỢC CHỌN
    
    Logic đúng:
    - selected_date = 2025-07-02 (ngày đã chọn để phân tích)
    - Lấy session có prediction_date = 2025-07-02
    - Day 1: So sánh predictions với kết quả thực tế ngày 2025-07-02
    - Day 2: So sánh predictions với kết quả thực tế ngày 2025-07-03
    - Day 3: So sánh predictions với kết quả thực tế ngày 2025-07-04
    
    Args:
        selected_date (date): Ngày được chọn để phân tích (VD: 2025-07-02)
        method_analysis (dict): Phân tích methods
        
    Returns:
        dict: Predictions cho 3 ngày kế tiếp
    """
    prediction_numbers = {}
    today = timezone.now().date()
    
    logger.info(f"📊 Getting prediction numbers for 3 days starting from {selected_date}")
    
    # ✅ VALIDATE INPUT
    if not method_analysis:
        logger.warning("❌ No method_analysis provided")
        return _create_empty_prediction_structure(selected_date)
    
    # ✅ LẤY SESSION CHO NGÀY ĐƯỢC CHỌN
    session = DailyTrackingSession.objects.filter(
        prediction_date=selected_date  # ✅ ĐÚNG: Session dự đoán CHO ngày này
    ).first()
    
    if not session:
        logger.error(f"❌ No session found for prediction_date = {selected_date}")
        return _get_prediction_numbers_from_pattern_data(selected_date, method_analysis)
    
    logger.info(f"📊 Found session {session.session_id} FOR {selected_date} with {session.method_results.count()} methods")
    
    # ✅ LẤY LOW RISK METHODS
    low_risk_methods = _get_low_risk_methods(method_analysis, session)
    
    logger.info(f"📊 Using {len(low_risk_methods)} low risk methods for predictions")
    
    # ✅ TẠO PREDICTION NUMBERS CHO 3 NGÀY
    for day in range(1, 4):
        # ✅ ĐÚNG: Ngày tracking bắt đầu từ selected_date
        tracking_date = selected_date + timedelta(days=day-1)
        
        logger.info(f"📊 Processing day {day}: comparing predictions with actual results for {tracking_date}")
        
        # ✅ LẤY PREDICTED NUMBERS TỪ SESSION
        predicted_numbers = _get_predicted_numbers_from_session(session, low_risk_methods)
        
        # ✅ LẤY KẾT QUẢ THỰC TẾ CHO TRACKING_DATE
        actual_numbers = _get_actual_numbers_for_date(tracking_date, today)
        
        # ✅ TÍNH HIT NUMBERS VÀ HIT RATE
        hit_numbers = sorted(list(set(predicted_numbers) & set(actual_numbers)))
        hit_rate = (len(hit_numbers) / len(predicted_numbers) * 100) if predicted_numbers else 0
        
        # ✅ TẠO RESPONSE CHO NGÀY NÀY
        prediction_numbers[f"day_{day}"] = {
            "date": tracking_date.strftime("%Y-%m-%d"),
            "display_date": tracking_date.strftime("%d/%m/%Y"),
            "low_risk_numbers": predicted_numbers[:15],  # Giới hạn UI
            "hit_numbers": hit_numbers,
            "actual_numbers": actual_numbers,
            "hit_rate": round(hit_rate, 1),
            "total_predictions": len(predicted_numbers),
            "no_data": False,
            "source": "real_time_session",  # ✅ ĐÚNG: Nguồn từ session thực
            "tracking_date_info": f"Day {day}: Predictions for {selected_date} vs actual results for {tracking_date}",
            "prediction_date": selected_date.strftime("%Y-%m-%d"),  # ✅ THÊM: Ngày tạo predictions
            "tracking_date": tracking_date.strftime("%Y-%m-%d")     # ✅ THÊM: Ngày so sánh
        }
        
        logger.info(f"✅ Day {day}: {len(predicted_numbers)} predictions vs {len(actual_numbers)} actual → {len(hit_numbers)} hits ({hit_rate:.1f}%)")
    
    return prediction_numbers

def _create_empty_prediction_structure(selected_date: date) -> dict:
    """
    ✅ TẠO STRUCTURE RỖNG CHO PREDICTIONS
    """
    prediction_numbers = {}
    
    for day in range(1, 4):
        tracking_date = selected_date + timedelta(days=day-1)
        prediction_numbers[f"day_{day}"] = {
            "date": tracking_date.strftime("%Y-%m-%d"),
            "display_date": tracking_date.strftime("%d/%m/%Y"),
            "low_risk_numbers": [],
            "hit_numbers": [],
            "actual_numbers": [],
            "hit_rate": 0.0,
            "total_predictions": 0,
            "no_data": True,
            "reason": "No method analysis available",
            "source": "empty_fallback",
            "prediction_date": selected_date.strftime("%Y-%m-%d"),
            "tracking_date": tracking_date.strftime("%Y-%m-%d")
        }
    
    return prediction_numbers


def _get_low_risk_methods(method_analysis: dict, session: DailyTrackingSession) -> list:
    """
    ✅ LẤY DANH SÁCH LOW RISK METHODS
    """
    low_risk_methods = []
    method_recommendations = method_analysis.get("method_recommendations", {})
    
    # Strategy 1: Lấy methods có risk_level = "low"
    for method_id, recommendation in method_recommendations.items():
        if recommendation.get("risk_level") == "low":
            low_risk_methods.append(int(method_id))
    
    # Strategy 2: Nếu không có low risk methods, lấy top methods theo score
    if not low_risk_methods:
        sorted_methods = sorted(
            method_recommendations.items(),
            key=lambda x: x[1].get("score", 0),
            reverse=True
        )
        low_risk_methods = [int(method_id) for method_id, _ in sorted_methods[:5]]
    
    # Strategy 3: Fallback - lấy tất cả methods trong session
    if not low_risk_methods:
        low_risk_methods = list(session.method_results.values_list('method_id', flat=True))
    
    return low_risk_methods


def _get_predicted_numbers_from_session(session: DailyTrackingSession, method_ids: list) -> list:
    """
    ✅ LẤY PREDICTED NUMBERS TỪ SESSION
    """
    all_predicted_numbers = set()
    
    for method_id in method_ids:
        try:
            method_result = session.method_results.filter(method_id=method_id).first()
            if method_result and method_result.base_prediction_numbers:
                all_predicted_numbers.update(method_result.base_prediction_numbers)
        except Exception as e:
            logger.warning(f"❌ Error getting numbers for method {method_id}: {e}")
            continue
    
    return sorted(list(all_predicted_numbers))


def _get_actual_numbers_for_date(target_date: date, today: date) -> list:
    """
    ✅ LẤY KẾT QUẢ THỰC TẾ CHO NGÀY CỤ THỂ
    """
    if target_date > today:
        logger.info(f"📊 {target_date} is future date, no actual results available")
        return []
    
    try:
        actual_result = KetQuaXoSo.objects.get(ngay=target_date)
        actual_numbers = sorted(list(actual_result.get_all_2digit_numbers()))
        logger.info(f"📊 Found {len(actual_numbers)} actual numbers for {target_date}")
        return actual_numbers
    except KetQuaXoSo.DoesNotExist:
        logger.info(f"📊 No actual results found for {target_date}")
        return []
    
def _get_prediction_numbers_from_pattern_data(selected_date: date, method_analysis: dict) -> dict:
    """
    ✅ SỬA LOGIC: FALLBACK với tracking date đúng
    """
    prediction_numbers = {}
    
    logger.info(f"📊 Getting prediction numbers from pattern data for {selected_date}")
    
    # ✅ SỬ DỤNG PATTERN DATA SERVICE
    try:
        pattern_data = data_service.get_pattern_data_for_analysis(
            target_date=selected_date.strftime("%Y-%m-%d"),
            method_ids=None,
            months_back=3,
            min_data_points=5
        )
        
        # ✅ LẤY TOP METHODS TỪ PATTERN DATA
        top_methods = list(pattern_data.get("hit_day_1", {}).keys())[:5]
        
        for day in range(1, 4):
            # ✅ SỬA LOGIC: tracking_date bây giờ là selected_date + (day-1)
            tracking_date = selected_date + timedelta(days=day-1)
            
            # ✅ GENERATE SAMPLE NUMBERS (vì pattern data không có specific numbers)
            sample_numbers = []
            for method_id in top_methods:
                # Generate some sample numbers based on method_id
                base_numbers = [(int(method_id) * 10 + i) % 100 for i in range(5)]
                sample_numbers.extend(base_numbers)
            
            # Remove duplicates and sort
            sample_numbers = sorted(list(set(sample_numbers)))[:15]
            
            # ✅ LẤY KẾT QUẢ THỰC TẾ CHO ĐÚNG NGÀY
            actual_numbers = []
            try:
                actual_result = KetQuaXoSo.objects.get(ngay=tracking_date)
                actual_numbers = sorted(list(actual_result.get_all_2digit_numbers()))
            except KetQuaXoSo.DoesNotExist:
                actual_numbers = []
            
            # ✅ TÍNH HIT NUMBERS
            hit_numbers = sorted(list(set(sample_numbers) & set(actual_numbers)))
            hit_rate = (len(hit_numbers) / len(sample_numbers) * 100) if sample_numbers else 0
            
            prediction_numbers[f"day_{day}"] = {
                "date": tracking_date.strftime("%Y-%m-%d"),
                "display_date": tracking_date.strftime("%d/%m/%Y"),
                "low_risk_numbers": sample_numbers,
                "hit_numbers": hit_numbers,
                "actual_numbers": actual_numbers,
                "hit_rate": round(hit_rate, 1),
                "total_predictions": len(sample_numbers),
                "no_data": False,
                "source": "pattern_data_fallback",
                "tracking_date_info": f"Day {day} tracking for {tracking_date.strftime('%d/%m/%Y')}"
            }
        
        logger.info(f"📊 Pattern data fallback completed for {len(top_methods)} methods")
        
    except Exception as e:
        logger.error(f"❌ Error getting pattern data: {e}")
        # ✅ FINAL FALLBACK với tracking date đúng
        for day in range(1, 4):
            tracking_date = selected_date + timedelta(days=day-1)
            prediction_numbers[f"day_{day}"] = {
                "date": tracking_date.strftime("%Y-%m-%d"),
                "display_date": tracking_date.strftime("%d/%m/%Y"),
                "low_risk_numbers": [],
                "hit_numbers": [],
                "actual_numbers": [],
                "hit_rate": 0.0,
                "total_predictions": 0,
                "no_data": True,
                "reason": "No data available",
                "tracking_date_info": f"Day {day} tracking for {tracking_date.strftime('%d/%m/%Y')}"
            }
    
    return prediction_numbers


def _analyze_tracking_by_day_from_patterns(pattern_data: dict, method_id: int) -> dict:
    """
    ✅ PHÂN TÍCH TRACKING BY DAY TỪ PATTERN DATA (đã có sẵn)
    """
    # Convert pattern data to evaluation format
    evaluations = _convert_pattern_data_to_evaluations(pattern_data, method_id)
    
    if not evaluations:
        return {
            "day_1": {"hit_probability": 0, "avg_hit_rate": 0, "sample_size": 0, "confidence": "no_data"},
            "day_2": {"hit_probability": 0, "avg_hit_rate": 0, "sample_size": 0, "confidence": "no_data"},
            "day_3": {"hit_probability": 0, "avg_hit_rate": 0, "sample_size": 0, "confidence": "no_data"},
            "best_day": 1,
            "recommended_strategy": "Không có dữ liệu"
        }
    
    # Sử dụng hàm analyze hiện có
    return _analyze_tracking_by_day(evaluations)

def _analyze_tracking_by_day(evaluations: list) -> dict:
    """
    ✅ HÀM CẤP ĐỘ MODULE: Phân tích hiệu suất theo từng ngày tracking (1, 2, 3)
    
    Args:
        evaluations (list): Danh sách evaluations (có thể là dict hoặc object)
        
    Returns:
        dict: {
            "day_1": {"hit_probability": float, "avg_hit_rate": float, "sample_size": int, "confidence": str},
            "day_2": {...},
            "day_3": {...},
            "best_day": int,
            "recommended_strategy": str,
            "analysis_summary": {...}
        }
    """
    # Group theo tracking_day
    day_groups = {1: [], 2: [], 3: []}

    for eval in evaluations:
        # ✅ HANDLE CẢ DICT VÀ OBJECT
        if isinstance(eval, dict):
            day = eval.get("tracking_day", 1)
        else:
            day = getattr(eval, "tracking_day", 1)
        
        if day in day_groups:
            day_groups[day].append(eval)

    day_analysis = {"day_1": {}, "day_2": {}, "day_3": {}}

    # Helper function để lấy hit_rate từ dict hoặc object
    def get_hit_rate(eval_item):
        if isinstance(eval_item, dict):
            return eval_item.get("hit_rate", 0)
        else:
            return getattr(eval_item, "hit_rate", 0)

    for day, day_evals in day_groups.items():
        if not day_evals:
            day_analysis[f"day_{day}"] = {
                "hit_probability": 0,
                "avg_hit_rate": 0,
                "sample_size": 0,
                "confidence": "no_data",
                "recent_trend": "unknown",
            }
            continue

        # Tính hit probability (số lần hit_rate > 0 / tổng số lần)
        hit_occurrences = len([e for e in day_evals if get_hit_rate(e) > 0])
        hit_probability = (hit_occurrences / len(day_evals)) * 100

        # Tính average hit rate
        avg_hit_rate = sum(get_hit_rate(e) for e in day_evals) / len(day_evals)

        # Tính recent trend (7 lần gần nhất)
        recent_evals = day_evals[-7:] if len(day_evals) >= 7 else day_evals
        recent_hit_prob = (
            len([e for e in recent_evals if get_hit_rate(e) > 0]) / len(recent_evals)
        ) * 100

        # Confidence level based on sample size
        sample_size = len(day_evals)
        if sample_size >= 20:
            confidence = "high"
        elif sample_size >= 10:
            confidence = "medium"
        elif sample_size >= 5:
            confidence = "low"
        else:
            confidence = "very_low"

        # Recent trend direction
        if len(day_evals) >= 4:
            first_half = day_evals[: len(day_evals) // 2]
            second_half = day_evals[len(day_evals) // 2 :]

            first_half_prob = (
                len([e for e in first_half if get_hit_rate(e) > 0]) / len(first_half)
            ) * 100
            second_half_prob = (
                len([e for e in second_half if get_hit_rate(e) > 0])
                / len(second_half)
            ) * 100

            if second_half_prob > first_half_prob + 10:
                recent_trend = "improving"
            elif second_half_prob < first_half_prob - 10:
                recent_trend = "declining"
            else:
                recent_trend = "stable"
        else:
            recent_trend = "insufficient_data"

        day_analysis[f"day_{day}"] = {
            "hit_probability": round(hit_probability, 1),
            "avg_hit_rate": round(avg_hit_rate, 1),
            "sample_size": sample_size,
            "confidence": confidence,
            "recent_trend": recent_trend,
            "recent_probability": round(recent_hit_prob, 1),
        }

    # Tìm best day
    best_day = 1
    best_score = 0

    for day in [1, 2, 3]:
        day_data = day_analysis[f"day_{day}"]
        if day_data["sample_size"] >= 5:  # Chỉ xem xét days có đủ data
            # Score = hit_probability * confidence_weight
            confidence_weight = {
                "high": 1.0,
                "medium": 0.8,
                "low": 0.6,
                "very_low": 0.3,
                "no_data": 0,
            }
            score = day_data["hit_probability"] * confidence_weight.get(
                day_data["confidence"], 0
            )

            if score > best_score:
                best_score = score
                best_day = day

    # Recommended strategy
    best_day_data = day_analysis[f"day_{best_day}"]
    if best_day_data["hit_probability"] >= 70:
        strategy = f"Nên đánh khung ngày {best_day} - xác suất cao"
    elif best_day_data["hit_probability"] >= 50:
        strategy = f"Khuyên đánh khung ngày {best_day} - xác suất trung bình"
    elif best_day_data["hit_probability"] >= 30:
        strategy = f"Cân nhắc đánh khung ngày {best_day} - xác suất thấp"
    else:
        strategy = "Không khuyến nghị - xác suất rất thấp"

    return {
        "day_1": day_analysis["day_1"],
        "day_2": day_analysis["day_2"],
        "day_3": day_analysis["day_3"],
        "best_day": best_day,
        "recommended_strategy": strategy,
        "analysis_summary": {
            "total_evaluations": len(evaluations),
            "best_day_probability": best_day_data["hit_probability"],
            "confidence_level": best_day_data["confidence"],
        },
    }


# ✅ THÊM CÁC HELPER FUNCTIONS CHO _analyze_tracking_by_day
def _predict_single_day_basic(features, day_data, day_number):
    """
    ✅ DỰ ĐOÁN ĐƠN GIẢN CHO MỘT NGÀY
    """
    if len(day_data) < 3:
        return {"probability": 0.1, "confidence": 0.0, "stability": 0.0}

    # Dữ liệu đã được sắp xếp cũ -> mới
    overall_rate = sum(day_data) / len(day_data)
    recent_rate = (
        sum(day_data[-3:]) / 3 if len(day_data) >= 3 else overall_rate
    )  # Lấy 3 ngày gần nhất

    # Weighted average: 60% recent, 40% overall
    probability = 0.6 * recent_rate + 0.4 * overall_rate

    # Confidence dựa trên data length
    confidence = min(0.8, len(day_data) / 20.0)

    # Stability dựa trên variance của recent data
    recent_variance = (
        np.var(day_data[-10:]) if len(day_data) >= 10 else np.var(day_data)
    )
    stability = max(0.0, 1.0 - recent_variance)

    return {
        "probability": float(probability),
        "confidence": float(confidence),
        "stability": float(stability),
    }


def _extract_basic_features(day1_data, day2_data, day3_data):
    """
    ✅ TRÍCH XUẤT FEATURES CƠ BẢN
    """
    features = {}

    # Features tổng quan
    all_data = day1_data + day2_data + day3_data
    features["total_hits"] = sum(all_data)
    features["hit_rate"] = sum(all_data) / len(all_data) if all_data else 0.0
    features["data_length"] = len(day1_data)

    # Features cho từng ngày
    for day_idx, day_data in enumerate([day1_data, day2_data, day3_data], 1):
        if not day_data:
            continue

        prefix = f"day{day_idx}_"
        features[f"{prefix}hit_rate"] = sum(day_data) / len(day_data)
        features[f"{prefix}total_hits"] = sum(day_data)

        # Recent trend lấy từ cuối array (ngày gần nhất)
        recent = day_data[-3:] if len(day_data) >= 3 else day_data
        features[f"{prefix}recent_hit_rate"] = (
            sum(recent) / len(recent) if recent else 0.0
        )

        # Current streak tính từ cuối array về đầu
        features[f"{prefix}current_streak"] = _get_current_streak_fixed(day_data)
        features[f"{prefix}last_hit_days_ago"] = _get_days_since_last_hit_fixed(day_data)

    return features


def _get_current_streak_fixed(data):
    """
    ✅ TÍNH STREAK HIỆN TẠI TỪ NGÀY GẦN NHẤT (cuối array)
    """
    if not data:
        return 0

    current_value = data[-1]  # Ngày gần nhất ở cuối
    streak = 0

    # Đếm ngược từ cuối array về đầu
    for value in reversed(data):
        if value == current_value:
            streak += 1
        else:
            break

    return streak


def _get_days_since_last_hit_fixed(data):
    """
    ✅ TÍNH NGÀY KỂ TỪ LẦN HIT CUỐI (từ cuối array)
    """
    if not data:
        return len(data)

    # Tìm hit gần nhất từ cuối array về đầu
    for i in range(len(data) - 1, -1, -1):
        if data[i] == 1:
            return len(data) - 1 - i  # Số ngày kể từ hit đó

    return len(data)  # Không có hit nào


def _calculate_method_quality_score(day1_data, day2_data, day3_data):
    """
    ✅ TÍNH ĐIỂM CHẤT LƯỢNG CHO METHOD
    """
    all_data = day1_data + day2_data + day3_data

    if len(all_data) == 0:
        return 0.0

    # Data length score
    length_score = min(1.0, len(all_data) / 50.0)

    # Diversity score
    hit_rate = sum(all_data) / len(all_data)
    diversity_score = min(hit_rate, 1 - hit_rate) * 2

    # Consistency across days
    day_rates = []
    for data in [day1_data, day2_data, day3_data]:
        if data:
            day_rates.append(sum(data) / len(data))

    consistency_score = 1.0 - np.var(day_rates) if len(day_rates) > 1 else 1.0

    # Combined score
    quality_score = length_score * 0.4 + diversity_score * 0.4 + consistency_score * 0.2

    return float(max(0.0, min(1.0, quality_score)))

def _convert_pattern_data_to_evaluations(pattern_data: dict, method_id: int) -> list:
    """
    ✅ CHUYỂN ĐỔI PATTERN DATA SANG EVALUATION FORMAT (đã có sẵn)
    """
    evaluations = []
    
    method_id_str = str(method_id)
    
    # Lấy dữ liệu cho method này
    day1_data = pattern_data.get("hit_day_1", {}).get(method_id_str, [])
    day2_data = pattern_data.get("hit_day_2", {}).get(method_id_str, [])
    day3_data = pattern_data.get("hit_day_3", {}).get(method_id_str, [])
    
    # Đảm bảo 3 arrays có cùng độ dài
    min_length = min(len(day1_data), len(day2_data), len(day3_data))
    if min_length == 0:
        return []
    
    # Tạo evaluation objects từ pattern data
    for i in range(min_length):
        # Tạo evaluation cho day 1
        if i < len(day1_data):
            evaluations.append({
                "tracking_day": 1,
                "hit_rate": day1_data[i] * 100,  # Convert 0/1 to 0%/100%
                "hit_count": day1_data[i],
                "evaluation_date": f"day_{i+1}",  # Placeholder
                "index": i
            })
        
        # Tạo evaluation cho day 2
        if i < len(day2_data):
            evaluations.append({
                "tracking_day": 2,
                "hit_rate": day2_data[i] * 100,
                "hit_count": day2_data[i],
                "evaluation_date": f"day_{i+1}",
                "index": i
            })
        
        # Tạo evaluation cho day 3
        if i < len(day3_data):
            evaluations.append({
                "tracking_day": 3,
                "hit_rate": day3_data[i] * 100,
                "hit_count": day3_data[i],
                "evaluation_date": f"day_{i+1}",
                "index": i
            })
    
    return evaluations


def _get_method_name(method_id: int) -> str:
    """
    ✅ LẤY TÊN METHOD
    """
    try:
        method = PredictionMethod.objects.get(id=method_id)
        return method.name
    except PredictionMethod.DoesNotExist:
        return f"Method {method_id}"