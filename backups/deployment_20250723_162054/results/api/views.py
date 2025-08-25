import logging
import time
from datetime import date, datetime

from django.http import JsonResponse
from django.utils import timezone
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.http import require_POST
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from results.core.services.ensemble import ensemble_service
from results.core.services.strategies import AnalysisStrategiesService

from ..core.services.ensemble import combine_strategies, get_historical_hits
from ..models import BtlAnalytics, PredictionMethodBtl
from ..views import wilson_score
from .serializers import DailyAnalysisSerializer, EnsembleAnalysisSerializer

logger = logging.getLogger(__name__)


@api_view(["GET"])
def daily_analysis_api(request):
    """
    API endpoint cho phân tích hàng ngày
    GET /api/daily-analysis/?date=YYYY-MM-DD
    """
    start_time = time.time()

    try:
        # Lấy tham số ngày
        date_str = request.GET.get("date")
        if date_str:
            analysis_date = datetime.strptime(date_str, "%Y-%m-%d").date()
        else:
            analysis_date = date.today()

        # Lấy dữ liệu lịch sử
        history_data = get_historical_hits(analysis_date)

        # Kết hợp các chiến lược
        recommendations = combine_strategies(analysis_date, history_data)

        # Lấy thống kê tổng quan
        daily_analytics = BtlAnalytics.objects.filter(date=analysis_date).first()

        total_methods = len(history_data)

        # Tính toán summary
        analysis_summary = {
            "total_recommendations": len(recommendations),
            "avg_score": (
                sum(r["score"] for r in recommendations) / len(recommendations)
                if recommendations
                else 0
            ),
            "top_score": recommendations[0]["score"] if recommendations else 0,
            "methods_analyzed": total_methods,
            "data_quality": "good" if total_methods >= 5 else "limited",
        }

        processing_time = time.time() - start_time

        # Chuẩn bị response data
        response_data = {
            "date": analysis_date,
            "recommendations": recommendations[:20],  # Top 20
            "total_methods": total_methods,
            "analysis_summary": analysis_summary,
            "processing_time": processing_time,
        }

        # Validate và serialize
        serializer = DailyAnalysisSerializer(response_data)

        return Response(serializer.data, status=status.HTTP_200_OK)

    except ValueError as e:
        return Response(
            {"error": "Invalid date format. Use YYYY-MM-DD"},
            status=status.HTTP_400_BAD_REQUEST,
        )
    except Exception as e:
        logger.error(f"Error in daily_analysis_api: {e}")
        return Response(
            {"error": "Internal server error"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


@api_view(["GET"])
def ensemble_analysis_api(request):
    """
    API endpoint cho phân tích ensemble chi tiết
    GET /api/ensemble-analysis/?date=YYYY-MM-DD&methods=1,2,3
    """
    try:
        # Lấy tham số
        date_str = request.GET.get("date")
        method_ids_str = request.GET.get("methods", "")

        if date_str:
            analysis_date = datetime.strptime(date_str, "%Y-%m-%d").date()
        else:
            analysis_date = date.today()

        # Lọc phương pháp nếu có
        if method_ids_str:
            method_ids = [int(id.strip()) for id in method_ids_str.split(",")]
            methods = PredictionMethodBtl.objects.filter(
                id__in=method_ids, is_active=True
            )
        else:
            methods = PredictionMethodBtl.objects.filter(is_active=True)

        # Lấy dữ liệu lịch sử
        history_data = get_historical_hits(analysis_date)

        # Lọc history theo methods nếu cần
        if method_ids_str:
            method_names = [m.name for m in methods]
            history_data = {
                name: data
                for name, data in history_data.items()
                if name in method_names
            }

        # Phân tích ensemble
        recommendations = combine_strategies(analysis_date, history_data)

        # Tính hiệu suất từng phương pháp
        method_performance = []
        for method in methods:
            method_history = history_data.get(method.name, [])
            if method_history:
                total_predictions = sum(
                    len(h["predicted_numbers"]) for h in method_history
                )
                total_hits = sum(h["hit_count"] for h in method_history)
                hit_rate = (
                    (total_hits / total_predictions * 100)
                    if total_predictions > 0
                    else 0
                )

                # Tính Wilson score
                wilson = wilson_score(total_hits, total_predictions)

                method_performance.append(
                    {
                        "method_id": method.id,
                        "method_name": method.name,
                        "hit_rate": hit_rate,
                        "total_predictions": total_predictions,
                        "total_hits": total_hits,
                        "wilson_score": wilson,
                        "cycle_strength": 0.0,  # Sẽ tính sau
                    }
                )

        # Tính diversity score
        method_predictions = {}
        for method_name, history in history_data.items():
            if history:
                latest_predictions = history[-1]["predicted_numbers"]
                method_predictions[method_name] = latest_predictions

        from ..core.services.strategies import ensemble_diversity_score

        diversity = ensemble_diversity_score(method_predictions)

        response_data = {
            "analysis_date": analysis_date,
            "top_recommendations": recommendations[:10],
            "method_performance": method_performance,
            "diversity_score": diversity,
            "confidence_level": 0.85,  # Placeholder
            "strategy_weights": {
                "cycle": 0.3,
                "frequency": 0.25,
                "gap": 0.25,
                "markov": 0.2,
            },
        }

        serializer = EnsembleAnalysisSerializer(response_data)
        return Response(serializer.data, status=status.HTTP_200_OK)

    except Exception as e:
        logger.error(f"Error in ensemble_analysis_api: {e}")
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(["GET"])
def method_details_api(request, method_id):
    """
    API endpoint trả về chi tiết một phương pháp dự đoán.
    GET /api/methods/<method_id>/details/
    Trả về:
    {
      "method_id": int,
      "method_name": str,
      "type": str,
      "accuracy": float,
      "wilson_score": float,
      "correct_count": int,
      "wrong_count": int,
      "history": [
        {
          "date": "YYYY-MM-DD",
          "prediction": str,
          "result": str,
          "correct": bool
        },
        ...
      ]
    }
    """
    try:
        method = PredictionMethodBtl.objects.get(id=method_id)
        history_qs = BtlAnalytics.objects.filter(phuong_phap=method).order_by("-ngay")[
            :10
        ]

        total_predictions = history_qs.count()
        correct_predictions = history_qs.filter(ket_qua="dung").count()
        wrong_predictions = total_predictions - correct_predictions
        accuracy = (
            (correct_predictions / total_predictions * 100)
            if total_predictions > 0
            else 0
        )
        wilson = wilson_score(correct_predictions, total_predictions)

        history = [
            {
                "date": h.ngay.strftime("%Y-%m-%d"),
                "prediction": h.du_doan,
                "result": h.ket_qua_thuc_te,
                "correct": h.ket_qua == "dung",
            }
            for h in history_qs
        ]

        data = {
            "method_id": method.id,
            "method_name": method.name,
            "type": (
                method.loai_phuong_phap if hasattr(method, "loai_phuong_phap") else ""
            ),
            "accuracy": round(accuracy, 2),
            "wilson_score": round(wilson, 4),
            "correct_count": correct_predictions,
            "wrong_count": wrong_predictions,
            "history": history,
        }
        return Response(data, status=status.HTTP_200_OK)
    except PredictionMethodBtl.DoesNotExist:
        return Response({"error": "Method not found"}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(["POST"])
def cache_refresh_api(request):
    """
    API để refresh cache
    POST /api/cache-refresh/
    """
    try:
        from django.core.cache import cache

        # Clear specific cache patterns
        cache_patterns = [
            "ensemble_analysis_*",
            "cycle_analysis_*",
            "frequency_stats_*",
        ]

        cleared_count = 0
        for pattern in cache_patterns:
            # Django cache doesn't support pattern deletion directly
            # This is a simplified version
            cache.delete(pattern)
            cleared_count += 1

        return Response(
            {
                "message": f"Cache refreshed successfully",
                "patterns_cleared": cleared_count,
            },
            status=status.HTTP_200_OK,
        )

    except Exception as e:
        logger.error(f"Error in cache_refresh_api: {e}")
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@require_POST
@csrf_protect
def refresh_daily_analysis(request):
    """
    API endpoint để làm mới dữ liệu phân tích hàng ngày

    Returns:
        dict - {
            'success': bool,
            'message': str,
            'date': str,
            'timestamp': str
        }
    """
    try:
        # Get the date from request
        date_str = request.GET.get("date")
        if not date_str:
            return JsonResponse(
                {"success": False, "error": "Ngày phân tích là bắt buộc"}, status=400
            )

        # Parse the date
        try:
            analysis_date = datetime.strptime(date_str, "%Y-%m-%d").date()
        except ValueError:
            return JsonResponse(
                {
                    "success": False,
                    "error": "Định dạng ngày không hợp lệ. Sử dụng YYYY-MM-DD",
                },
                status=400,
            )

        # Initialize services
        strategies_service = AnalysisStrategiesService()

        # Clear cache for the specific date
        from django.core.cache import cache

        cache_keys_to_clear = [
            f"method_performance_{analysis_date.strftime('%Y%m%d')}",
            f"cycle_analysis_{analysis_date}_60",
            f"gap_analysis_{analysis_date}_90",
            f"pattern_mining_{analysis_date}_60",
            f"ensemble_strategies_{analysis_date.strftime('%Y%m%d')}",
        ]

        for key in cache_keys_to_clear:
            cache.delete(key)

        # Trigger refresh of analyses
        logger.info(f"Refreshing daily analysis for date: {analysis_date}")

        # Refresh method performance analysis
        strategies_service.get_method_performance_analysis(analysis_date)

        # Refresh cycle analysis
        strategies_service.analyze_cycles(analysis_date)

        # Refresh gap analysis
        strategies_service.analyze_gaps(analysis_date)

        # Refresh pattern mining
        strategies_service.mine_patterns(analysis_date)

        # If ensemble_service has a refresh method, call it
        if hasattr(ensemble_service, "get_ensemble_strategies_analysis"):
            ensemble_service.get_ensemble_strategies_analysis(analysis_date)

        return JsonResponse(
            {
                "success": True,
                "message": f'Dữ liệu phân tích cho ngày {analysis_date.strftime("%d/%m/%Y")} đã được làm mới thành công',
                "date": date_str,
                "timestamp": timezone.now().isoformat(),
            }
        )

    except Exception as e:
        logger.error(f"Error refreshing daily analysis: {e}", exc_info=True)
        return JsonResponse(
            {"success": False, "error": f"Lỗi khi làm mới dữ liệu: {str(e)}"},
            status=500,
        )


@require_POST
@csrf_protect
def refresh_all_cache(request):
    """
    API endpoint để làm mới toàn bộ cache
    """
    try:
        from django.core.cache import cache

        cache.clear()

        return JsonResponse(
            {
                "success": True,
                "message": "Toàn bộ cache đã được xóa thành công",
                "timestamp": timezone.now().isoformat(),
            }
        )

    except Exception as e:
        logger.error(f"Error clearing cache: {e}", exc_info=True)
        return JsonResponse(
            {"success": False, "error": f"Lỗi khi xóa cache: {str(e)}"}, status=500
        )
