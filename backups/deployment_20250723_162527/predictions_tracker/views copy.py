import json
import logging
from datetime import date, datetime, timedelta
from typing import Any, Dict, List

from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Avg, Count, Q, Sum
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

from results.models import KetQuaXoSo

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
from collections import defaultdict
from datetime import date, timedelta

from django.db.models import Avg, Count, Q
from django.shortcuts import render
from django.utils import timezone
from django.views.generic import TemplateView

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

        report_data = self._build_monthly_report(start_date, end_date)
        methods_summary = self._get_methods_summary(start_date, end_date)

        # Logger kiểm tra lượng dữ liệu
        num_days = len(report_data.get("days", []))
        num_sessions = sum(len(day.get("sessions", [])) for day in report_data.get("days", []))
        num_methods = len(methods_summary)
        # Ước tính kích thước dict (không chính xác tuyệt đối, nhưng đủ để cảnh báo)
        try:
            import json
            def convert_for_json(obj):
                if isinstance(obj, (date, datetime)):
                    return obj.isoformat()
                # Nếu là instance model Django, chỉ lấy str hoặc pk
                if hasattr(obj, "__class__") and obj.__class__.__name__ in [
                    "PredictionMethod", "PredictionCycle", "DailyTrackingSession"
                ]:
                    return str(obj)
                if isinstance(obj, dict):
                    return {k: convert_for_json(v) for k, v in obj.items()}
                if isinstance(obj, list):
                    return [convert_for_json(i) for i in obj]
                return obj

            report_data_serializable = convert_for_json(report_data)
            report_data_size = len(json.dumps(report_data_serializable, ensure_ascii=False))
            methods_summary_serializable = [
                {
                    "method": str(m["method"]),
                    "predictions_count": m.get("predictions_count"),
                    "evaluations_count": m.get("evaluations_count"),
                    "avg_hit_count": m.get("avg_hit_count"),
                    "avg_hit_rate": m.get("avg_hit_rate"),
                    "performance_level": m.get("performance_level"),
                }
                for m in methods_summary
            ]
            methods_summary_size = len(json.dumps(methods_summary_serializable, ensure_ascii=False))
        except Exception as e:
            report_data_size = -1
            methods_summary_size = -1
            logger.warning(f"Không thể tính kích thước dữ liệu: {e}")

        logger.info(
            f"[MonthlyPredictionReportView] Dữ liệu truyền qua template: "
            f"{num_days} ngày, {num_sessions} sessions, {num_methods} methods. "
            f"Kích thước report_data: {report_data_size/1024:.1f} KB, "
            f"methods_summary: {methods_summary_size/1024:.1f} KB"
        )
        # Nếu dữ liệu quá lớn (ví dụ > 2MB), cảnh báo
        if report_data_size > 2 * 1024 * 1024:
            logger.warning(f"[MonthlyPredictionReportView] report_data quá lớn: {report_data_size/1024/1024:.2f} MB")

        context.update(
            {
                "year": year,
                "month": month,
                "month_name": calendar.month_name[month],
                "start_date": start_date,
                "end_date": end_date,
                "report_data": report_data,
                "methods_summary": methods_summary,
                "navigation": self._get_navigation_data(year, month),
            }
        )

        return context

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
                    "overall_confidence": 0
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
                        tracking_results = self._get_tracking_results(session, method_result)
                        
                        # Cập nhật methods_data cho template table
                        if method_id in methods_data:
                            methods_data[method_id].update({
                                "predicted_numbers": method_result.base_prediction_numbers,
                                "tracking_results": tracking_results,
                                "has_data": True,
                                "overall_confidence": method_result.overall_confidence
                            })
                        
                        # Thêm vào session_methods_data cho JavaScript
                        session_methods_data.append({
                            "method_id": method_result.method.id,
                            "method_name": method_result.method.name,
                            "category": method_result.method.get_category_display(),
                            "confidence": method_result.overall_confidence,
                            "predicted_numbers": method_result.base_prediction_numbers,
                            "tracking_results": tracking_results,
                            "total_hits": sum(tr["hit_count"] for tr in tracking_results),
                            "avg_hit_rate": (
                                sum(tr["hit_rate"] for tr in tracking_results) / len(tracking_results)
                                if tracking_results else 0
                            )
                        })
                    
                    # Thêm session data cho JavaScript
                    sessions_data.append({
                        "session": {
                            "cycle": {
                                "cycle_name": session.cycle.cycle_name if session.cycle else "Auto Import"
                            },
                            "status": session.get_status_display()
                        },
                        "methods": session_methods_data
                    })
            
            day_data = {
                "date": current_date,
                "methods_data": methods_data,
                "sessions": sessions_data  # Thêm cho JavaScript
            }
            
            report_data["days"].append(day_data)
            current_date += timedelta(days=1)
        logger.info(f"Report built with {len(report_data['days'])} days")
        return report_data
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
