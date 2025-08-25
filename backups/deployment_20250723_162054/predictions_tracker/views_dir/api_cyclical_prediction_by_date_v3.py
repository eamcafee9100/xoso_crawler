import logging
from collections import Counter, defaultdict
from datetime import date, datetime, timedelta

import numpy as np
from django.db.models import Avg, Count, Max, Min, Sum
from django.http import JsonResponse
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

from predictions_tracker.core.services.ABTestingService import (
    ab_testing_service,
)
from predictions_tracker.core.services.CyclicalValidationService import (
    cyclical_validation_service,
)
from predictions_tracker.core.services.ParameterOptimizationService import (
    OptimizationParameters,
    parameter_optimization_service,
)

logger = logging.getLogger(__name__)

from predictions_tracker.models import (
    CyclicalContextEngine,
    CyclicalNumberPredictor,
    MethodCycleSyncMatrix,
    MethodCyclicalPerformance,
    PredictionMethod,
)
from results.models import KetQuaXoSo, NumberFrequencyStats

logger = logging.getLogger(__name__)


@csrf_exempt
@require_http_methods(["GET"])
def api_cyclical_prediction_by_date_v3(request):
    """
    ✅ API CYCLICAL PREDICTION V3 - HYBRID CYCLICAL INTELLIGENCE
    
    Returns:
        dict: {
            "success": bool,
            "analysis_approach": "cyclical_intelligence",
            "analysis_date": str,
            "cyclical_analysis": {
                "context_analysis": dict,
                "method_sync_matrix": dict,
                "number_frequency_cycles": dict
            },
            "optimal_methods": {
                "cyclical_filtered": list[dict],
                "top_sync_methods": list[dict]
            },
            "intelligent_predictions": {
                "cyclical_numbers": list[int],
                "method_numbers": list[int],
                "fusion_numbers": list[int]
            },
            "performance_metrics": {
                "expected_accuracy": float,
                "confidence_level": str,
                "cyclical_strength": float
            },
            "metadata": dict
        }
    """
    try:
        # ✅ 1. VALIDATE & PARSE PARAMETERS
        analysis_date_str = request.GET.get("analysis_date")
        limit = int(request.GET.get("limit", 15))
        acceptable_hit_rate = float(request.GET.get("threshold", 60)) / 100.0  # 60% threshold
        
        if not analysis_date_str:
            return JsonResponse({
                "success": False,
                "error": "analysis_date parameter is required",
                "message": "Vui lòng cung cấp analysis_date (YYYY-MM-DD)"
            }, status=400)
            
        try:
            analysis_date = datetime.strptime(analysis_date_str, "%Y-%m-%d").date()
        except ValueError:
            return JsonResponse({
                "success": False,
                "error": "invalid_date_format",
                "message": "Định dạng ngày không hợp lệ. Sử dụng YYYY-MM-DD"
            }, status=400)
            
        logger.info(f"🔍 V3 Cyclical analysis: {analysis_date}, threshold: {acceptable_hit_rate:.1%}")
        
        # ✅ 2. CYCLICAL CONTEXT ANALYSIS
        context_analysis = _analyze_cyclical_context_v3(analysis_date)
        
        # ✅ 3. BUILD METHOD SYNC MATRIX
        sync_matrix_data = _build_method_sync_matrix_v3(analysis_date, context_analysis)
        
        # ✅ 4. CYCLICAL NUMBER PREDICTION
        cyclical_number_predictions = _predict_numbers_by_frequency_cycles_v3(analysis_date)
        
        # ✅ 5. FILTER METHODS BY CYCLICAL FITNESS
        optimal_methods = _filter_methods_by_cyclical_fitness_v3(
            sync_matrix_data, 
            acceptable_hit_rate,
            limit,
            analysis_date
        )
        
        # ✅ 6. INTELLIGENT NUMBER FUSION
        intelligent_predictions = _select_numbers_with_cyclical_intelligence_v3(
            optimal_methods, 
            cyclical_number_predictions,
            analysis_date
        )
        
        # ✅ 7. PERFORMANCE PREDICTION
        performance_metrics = _predict_cyclical_performance_v3(
            optimal_methods,
            intelligent_predictions,
            context_analysis
        )
        
        # ✅ 8. COMPREHENSIVE RESPONSE
        response_data = {
            "success": True,
            "analysis_approach": "cyclical_intelligence",
            "analysis_date": analysis_date_str,
            "cyclical_analysis": {
                "context_analysis": context_analysis,
                "method_sync_matrix": sync_matrix_data,
                "number_frequency_cycles": cyclical_number_predictions
            },
            "optimal_methods": optimal_methods,
            "intelligent_predictions": intelligent_predictions,
            "performance_metrics": performance_metrics,
            "metadata": {
                "total_active_methods": PredictionMethod.objects.filter(is_active=True).count(),
                "analysis_timestamp": timezone.now().isoformat(),
                "api_version": "v3_cyclical",
                "parameters": {
                    "limit": limit,
                    "threshold": acceptable_hit_rate,
                    "cyclical_approach": True
                }
            }
        }
        
        return JsonResponse(response_data, json_dumps_params={'ensure_ascii': False})
        
    except Exception as e:
        logger.error(f"❌ Cyclical prediction API error: {str(e)}", exc_info=True)
        return JsonResponse({
            "success": False,
            "error": "internal_server_error",
            "message": f"Lỗi xử lý: {str(e)}"
        }, status=500)


def _analyze_cyclical_context_v3(analysis_date):
    """Phân tích bối cảnh chu kỳ cho ngày phân tích"""
    try:
        # Get or create cyclical context
        context = CyclicalContextEngine.analyze_current_context(analysis_date)
        
        return {
            "analysis_date": analysis_date.isoformat(),
            "day_of_month_phase": context.day_of_month_phase,
            "week_phase": context.week_phase,
            "month_trend": context.month_trend,
            "cycle_strength": context.cycle_strength,
            "active_cycles": context.active_cycles,
            "fatigued_methods": context.fatigue_methods,
            "context_metadata": {
                "day_of_month": analysis_date.day,
                "day_of_week": analysis_date.weekday(),
                "month": analysis_date.month,
                "year": analysis_date.year
            }
        }
    except Exception as e:
        logger.error(f"Context analysis error: {str(e)}")
        return {
            "analysis_date": analysis_date.isoformat(),
            "error": str(e),
            "fallback_context": True
        }


def _build_method_sync_matrix_v3(analysis_date, context_analysis):
    """Xây dựng ma trận đồng bộ method-cycle"""
    try:
        # Build sync matrix
        sync_records = MethodCycleSyncMatrix.build_sync_matrix(analysis_date)
        
        # Format response
        sync_data = {
            "total_methods_analyzed": len(sync_records),
            "analysis_date": analysis_date.isoformat(),
            "sync_records": [],
            "summary_stats": {
                "avg_cyclical_fitness": 0,
                "avg_fatigue_risk": 0,
                "methods_by_trend": Counter()
            }
        }
        
        fitness_scores = []
        fatigue_risks = []
        
        for record in sync_records:
            record_data = {
                "method_id": record.method.id,
                "method_name": record.method.name,
                "method_category": record.method.category,
                "cyclical_fitness": record.cyclical_fitness,
                "phase_alignment": record.phase_alignment,
                "fatigue_risk": record.fatigue_risk,
                "phase_sync": {
                    "early_month": record.early_month_sync,
                    "mid_month": record.mid_month_sync,
                    "late_month": record.late_month_sync
                },
                "trend_analysis": {
                    "direction": record.trend_direction,
                    "strength": record.trend_strength
                }
            }
            
            sync_data["sync_records"].append(record_data)
            fitness_scores.append(record.cyclical_fitness)
            fatigue_risks.append(record.fatigue_risk)
            sync_data["summary_stats"]["methods_by_trend"][record.trend_direction] += 1
        
        # Calculate summary stats
        if fitness_scores:
            sync_data["summary_stats"]["avg_cyclical_fitness"] = round(np.mean(fitness_scores), 2)
            sync_data["summary_stats"]["avg_fatigue_risk"] = round(np.mean(fatigue_risks), 2)
        
        return sync_data
        
    except Exception as e:
        logger.error(f"Sync matrix build error: {str(e)}")
        return {"error": str(e), "fallback": True}


def _predict_numbers_by_frequency_cycles_v3(analysis_date):
    """Dự đoán số dựa trên chu kỳ tần suất"""
    try:
        # Get cyclical number predictor
        predictor = CyclicalNumberPredictor.predict_numbers_by_frequency_cycles(analysis_date)
        
        return {
            "analysis_date": analysis_date.isoformat(),
            "target_date": (analysis_date + timedelta(days=1)).isoformat(),
            "prediction_confidence": predictor.prediction_confidence,
            "cycle_strength": predictor.cycle_strength,
            "predicted_numbers": predictor.predicted_numbers,
            "cycle_patterns": predictor.cycle_patterns,
            "frequency_analysis": predictor.frequency_analysis,
            "phase_compatibility": predictor.phase_compatibility
        }
        
    except Exception as e:
        logger.error(f"Cyclical number prediction error: {str(e)}")
        return {"error": str(e), "fallback_predictions": []}


def _filter_methods_by_cyclical_fitness_v3(sync_matrix_data, acceptable_hit_rate, limit, analysis_date):
    """Lọc methods dựa trên cyclical fitness"""
    try:
        if "error" in sync_matrix_data:
            return {"error": "Sync matrix data unavailable"}
        
        sync_records = sync_matrix_data.get("sync_records", [])
        
        # Filter and score methods
        enhanced_methods = []
        
        for record in sync_records:
            # Skip fatigued methods
            if record["fatigue_risk"] > 0.8:
                continue
                
            # Skip methods with very low fitness
            if record["cyclical_fitness"] < 20:  # Below 20% cyclical fitness
                continue
            
            # Calculate Cyclical Compatibility Score
            cyclical_score = (
                record["cyclical_fitness"] * 0.4 +                    # Base cyclical fitness
                record["phase_alignment"] * 100 * 0.3 +              # Phase alignment bonus  
                (1 - record["fatigue_risk"]) * 100 * 0.2 +           # Anti-fatigue bonus
                record["trend_analysis"]["strength"] * 10 * 0.1      # Trend strength bonus
            )
            
            method_data = {
                "method_id": record["method_id"],
                "method_name": record["method_name"],
                "method_category": record["method_category"],
                "cyclical_score": round(cyclical_score, 2),
                "cyclical_fitness": record["cyclical_fitness"],
                "phase_alignment": record["phase_alignment"],
                "fatigue_risk": record["fatigue_risk"],
                "trend_direction": record["trend_analysis"]["direction"],
                "sync_data": record
            }
            
            enhanced_methods.append(method_data)
        
        # Sort by cyclical score
        enhanced_methods.sort(key=lambda x: x["cyclical_score"], reverse=True)
        
        # Apply limit
        cyclical_filtered = enhanced_methods[:limit]
        
        # Get top sync methods (different criteria)
        top_sync_methods = sorted(
            enhanced_methods,
            key=lambda x: (x["phase_alignment"], x["cyclical_fitness"]),
            reverse=True
        )[:min(10, len(enhanced_methods))]
        
        return {
            "total_candidates": len(enhanced_methods),
            "filtered_count": len(cyclical_filtered),
            "cyclical_filtered": cyclical_filtered,
            "top_sync_methods": top_sync_methods,
            "filtering_criteria": {
                "min_cyclical_fitness": 20,
                "max_fatigue_risk": 0.8,
                "acceptable_hit_rate": acceptable_hit_rate
            }
        }
        
    except Exception as e:
        logger.error(f"Method filtering error: {str(e)}")
        return {"error": str(e)}


def _select_numbers_with_cyclical_intelligence_v3(optimal_methods, cyclical_predictions, analysis_date):
    """Kết hợp predictions từ methods với cyclical intelligence"""
    try:
        # 1. Get method predictions (simulate method predictions for now)
        method_numbers = _get_method_predictions_v3(optimal_methods, analysis_date)
        
        # 2. Get cyclical predictions
        cyclical_numbers = _extract_cyclical_numbers(cyclical_predictions)
        
        # 3. Fusion scoring
        fusion_numbers = _perform_number_fusion_v3(method_numbers, cyclical_numbers)
        
        return {
            "cyclical_numbers": cyclical_numbers[:15],
            "method_numbers": method_numbers[:15], 
            "fusion_numbers": fusion_numbers[:15],
            "fusion_strategy": {
                "method_weight": 0.6,
                "cyclical_weight": 0.4,
                "total_candidates": len(set(method_numbers + cyclical_numbers))
            }
        }
        
    except Exception as e:
        logger.error(f"Number selection error: {str(e)}")
        return {
            "cyclical_numbers": [],
            "method_numbers": [],
            "fusion_numbers": [],
            "error": str(e)
        }


def _get_method_predictions_v3(optimal_methods, analysis_date):
    """Lấy predictions từ methods (simplified for now)"""
    method_predictions = defaultdict(float)
    
    filtered_methods = optimal_methods.get("cyclical_filtered", [])
    
    for method_data in filtered_methods:
        cyclical_score = method_data.get("cyclical_score", 0)
        method_id = method_data.get("method_id")
        
        # Simulate method predictions based on cyclical score
        # In real implementation, this would call actual method prediction logic
        predicted_numbers = _simulate_method_predictions(method_id, cyclical_score)
        
        for number in predicted_numbers:
            method_predictions[number] += cyclical_score
    
    # Sort by aggregated score
    sorted_predictions = sorted(
        method_predictions.items(),
        key=lambda x: x[1],
        reverse=True
    )
    
    return [str(num).zfill(2) for num, score in sorted_predictions]


def _simulate_method_predictions(method_id, cyclical_score):
    """Simulate method predictions (replace with actual method calls)"""
    # This is a placeholder - replace with actual method prediction logic
    import random
    random.seed(method_id + int(cyclical_score))
    
    # Generate some numbers based on cyclical score
    num_predictions = max(5, int(cyclical_score / 10))
    predictions = []
    
    for _ in range(num_predictions):
        predictions.append(random.randint(0, 99))
    
    return [str(num).zfill(2) for num in predictions]


def _extract_cyclical_numbers(cyclical_predictions):
    """Trích xuất numbers từ cyclical predictions"""
    if "error" in cyclical_predictions:
        return []
    
    predicted_numbers = cyclical_predictions.get("predicted_numbers", [])
    
    return [
        item["number"] 
        for item in predicted_numbers
        if isinstance(item, dict) and "number" in item
    ]


def _perform_number_fusion_v3(method_numbers, cyclical_numbers):
    """Fusion hai sets predictions"""
    final_scores = defaultdict(float)
    
    # Method predictions với weight 0.6
    for i, number in enumerate(method_numbers[:20]):
        score = (20 - i) * 0.6  # Decreasing score by position
        final_scores[number] += score
    
    # Cyclical predictions với weight 0.4
    for i, number in enumerate(cyclical_numbers[:20]):
        score = (20 - i) * 0.4
        final_scores[number] += score
    
    # Sort by final score
    fusion_results = sorted(
        final_scores.items(),
        key=lambda x: x[1],
        reverse=True
    )
    
    return [num for num, score in fusion_results]


def _predict_cyclical_performance_v3(optimal_methods, intelligent_predictions, context_analysis):
    """Dự đoán performance dựa trên cyclical analysis"""
    try:
        # Base accuracy từ cyclical strength
        cycle_strength = context_analysis.get("cycle_strength", 0.5)
        base_accuracy = min(0.6, cycle_strength * 0.8)  # Max 60% base accuracy
        
        # Method quality bonus
        filtered_methods = optimal_methods.get("cyclical_filtered", [])
        if filtered_methods:
            avg_cyclical_score = np.mean([m["cyclical_score"] for m in filtered_methods])
            method_bonus = min(0.2, avg_cyclical_score / 500)  # Max 20% bonus
        else:
            method_bonus = 0
        
        # Fusion bonus
        fusion_numbers = intelligent_predictions.get("fusion_numbers", [])
        fusion_bonus = min(0.1, len(fusion_numbers) / 150)  # Max 10% bonus
        
        expected_accuracy = base_accuracy + method_bonus + fusion_bonus
        expected_accuracy = min(0.65, expected_accuracy)  # Cap at 65%
        
        # Determine confidence level
        if expected_accuracy >= 0.55:
            confidence_level = "High"
        elif expected_accuracy >= 0.4:
            confidence_level = "Medium"
        else:
            confidence_level = "Low"
        
        return {
            "expected_accuracy": round(expected_accuracy * 100, 1),  # Convert to percentage
            "confidence_level": confidence_level,
            "cyclical_strength": cycle_strength,
            "performance_breakdown": {
                "base_accuracy": round(base_accuracy * 100, 1),
                "method_bonus": round(method_bonus * 100, 1),
                "fusion_bonus": round(fusion_bonus * 100, 1)
            },
            "risk_assessment": {
                "fatigue_risk": _calculate_overall_fatigue_risk(optimal_methods),
                "data_quality": "Good" if cycle_strength > 0.6 else "Fair",
                "prediction_stability": confidence_level
            }
        }
        
    except Exception as e:
        logger.error(f"Performance prediction error: {str(e)}")
        return {
            "expected_accuracy": 30.0,
            "confidence_level": "Low",
            "cyclical_strength": 0.0,
            "error": str(e)
        }


def _calculate_overall_fatigue_risk(optimal_methods):
    """Tính rủi ro mệt mỏi tổng thể"""
    filtered_methods = optimal_methods.get("cyclical_filtered", [])
    
    if not filtered_methods:
        return "Unknown"
    
    avg_fatigue = np.mean([m["fatigue_risk"] for m in filtered_methods])
    
    if avg_fatigue < 0.3:
        return "Low"
    elif avg_fatigue < 0.6:
        return "Medium"
    else:
        return "High"


@csrf_exempt
@require_http_methods(["GET", "POST"])
def api_cyclical_validation(request):
    """
    API for cyclical approach validation and backtesting
    
    GET params:
        - start_date: YYYY-MM-DD (required)
        - end_date: YYYY-MM-DD (required)  
        - validation_type: full|quick (default: quick)
        
    Returns:
        dict: {
            "success": bool,
            "validation_type": str,
            "validation_period": dict,
            "overall_metrics": dict,
            "performance_analysis": dict,
            "comparison_baseline": dict,
            "daily_results": list (if validation_type=full),
            "metadata": dict
        }
    """
    try:
        # 1. Parse parameters
        start_date_str = request.GET.get("start_date")
        end_date_str = request.GET.get("end_date") 
        validation_type = request.GET.get("validation_type", "quick")
        
        if not start_date_str or not end_date_str:
            return JsonResponse({
                "success": False,
                "error": "missing_parameters",
                "message": "start_date và end_date parameters are required"
            }, status=400)
        
        try:
            start_date = datetime.strptime(start_date_str, "%Y-%m-%d").date()
            end_date = datetime.strptime(end_date_str, "%Y-%m-%d").date()
        except ValueError:
            return JsonResponse({
                "success": False,
                "error": "invalid_date_format", 
                "message": "Định dạng ngày không hợp lệ. Sử dụng YYYY-MM-DD"
            }, status=400)
        
        # Validate date range
        if start_date >= end_date:
            return JsonResponse({
                "success": False,
                "error": "invalid_date_range",
                "message": "start_date phải nhỏ hơn end_date"
            }, status=400)
        
        if (end_date - start_date).days > 90:
            return JsonResponse({
                "success": False,
                "error": "date_range_too_large",
                "message": "Khoảng thời gian validation không được vượt quá 90 ngày"
            }, status=400)
        
        logger.info(f"🔍 Starting cyclical validation: {start_date} to {end_date} (type: {validation_type})")
        
        # 2. Run validation
        validation_result = cyclical_validation_service.validate_cyclical_approach(
            start_date, end_date
        )
        
        if "error" in validation_result:
            return JsonResponse({
                "success": False,
                "error": "validation_failed",
                "message": f"Validation thất bại: {validation_result['error']}"
            }, status=500)
        
        # 3. Format response based on validation_type
        response_data = {
            "success": True,
            "validation_type": validation_type,
            "validation_period": validation_result["validation_period"],
            "overall_metrics": validation_result["overall_metrics"],
            "performance_analysis": validation_result["performance_analysis"],
            "comparison_baseline": validation_result["comparison_baseline"],
            "metadata": {
                "validation_timestamp": validation_result["validation_timestamp"],
                "api_version": "v3_cyclical_validation",
                "parameters": {
                    "start_date": start_date_str,
                    "end_date": end_date_str,
                    "validation_type": validation_type
                }
            }
        }
        
        # Include daily results only for full validation
        if validation_type == "full":
            response_data["daily_results"] = validation_result["daily_results"]
        else:
            response_data["daily_results_summary"] = {
                "total_days": len(validation_result["daily_results"]),
                "sample_size": min(5, len(validation_result["daily_results"])),
                "sample_results": validation_result["daily_results"][:5]
            }
        
        logger.info(f"✅ Validation completed. Accuracy: {validation_result['overall_metrics'].get('accuracy', 0):.1%}")
        
        return JsonResponse(response_data, json_dumps_params={'ensure_ascii': False})
        
    except Exception as e:
        logger.error(f"❌ Cyclical validation API error: {str(e)}", exc_info=True)
        return JsonResponse({
            "success": False,
            "error": "internal_server_error",
            "message": f"Lỗi xử lý: {str(e)}"
        }, status=500)


@csrf_exempt
@require_http_methods(["GET"])
def api_validation_summary(request):
    """
    Get quick validation summary for recent periods
    
    Returns:
        dict: {
            "success": bool,
            "recent_validations": list,
            "performance_summary": dict
        }
    """
    try:
        # Quick validation for last 30 days
        end_date = date.today() - timedelta(days=1)
        start_date = end_date - timedelta(days=30)
        
        validation_result = cyclical_validation_service.validate_cyclical_approach(
            start_date, end_date
        )
        
        if "error" in validation_result:
            return JsonResponse({
                "success": False,
                "error": "validation_failed",
                "message": f"Summary validation failed: {validation_result['error']}"
            }, status=500)
        
        return JsonResponse({
            "success": True,
            "recent_validations": [validation_result["validation_period"]],
            "performance_summary": {
                "accuracy": validation_result["overall_metrics"]["accuracy"],
                "avg_hits_per_day": validation_result["overall_metrics"]["avg_hits_per_day"],
                "successful_days": validation_result["overall_metrics"]["successful_days"],
                "total_days": validation_result["overall_metrics"]["total_days"]
            },
            "metadata": {
                "period": f"{start_date} to {end_date}",
                "generated_at": timezone.now().isoformat()
            }
        }, json_dumps_params={'ensure_ascii': False})
        
    except Exception as e:
        logger.error(f"❌ Validation summary API error: {str(e)}", exc_info=True)
        return JsonResponse({
            "success": False,
            "error": "internal_server_error",
            "message": f"Lỗi xử lý: {str(e)}"
        }, status=500)
        

@csrf_exempt
@require_http_methods(["POST"])
def api_optimize_parameters(request):
    """
    API for parameter optimization
    
    POST params:
        - optimization_period_days: int (default: 60)
        - optimization_method: str (default: L-BFGS-B)
        
    Returns:
        dict: {
            "success": bool,
            "optimization_result": dict,
            "optimal_parameters": dict,
            "performance_improvement": float,
            "metadata": dict
        }
    """
    try:
        # Parse parameters
        optimization_period_days = int(request.POST.get('optimization_period_days', 60))
        optimization_method = request.POST.get('optimization_method', 'L-BFGS-B')
        
        # Validate parameters
        if optimization_period_days < 30 or optimization_period_days > 180:
            return JsonResponse({
                "success": False,
                "error": "invalid_period",
                "message": "Optimization period must be between 30-180 days"
            }, status=400)
        
        logger.info(f"🔍 Starting parameter optimization: {optimization_period_days} days")
        
        # Run optimization
        optimization_result = parameter_optimization_service.optimize_cyclical_parameters(
            optimization_period_days=optimization_period_days,
            optimization_method=optimization_method
        )
        
        if optimization_result.success:
            response_data = {
                "success": True,
                "optimization_result": {
                    "success": optimization_result.success,
                    "improvement_rate": optimization_result.improvement_rate,
                    "optimization_details": optimization_result.optimization_details
                },
                "optimal_parameters": {
                    "frequency_weight": optimization_result.optimal_parameters.frequency_weight,
                    "weekly_weight": optimization_result.optimal_parameters.weekly_weight,
                    "monthly_weight": optimization_result.optimal_parameters.monthly_weight,
                    "phase_weight": optimization_result.optimal_parameters.phase_weight,
                    "min_cyclical_fitness": optimization_result.optimal_parameters.min_cyclical_fitness,
                    "max_fatigue_risk": optimization_result.optimal_parameters.max_fatigue_risk,
                    "prediction_limit": optimization_result.optimal_parameters.prediction_limit
                },
                "performance_metrics": optimization_result.performance_metrics,
                "performance_improvement": round(optimization_result.improvement_rate * 100, 2),
                "metadata": {
                    "optimization_timestamp": timezone.now().isoformat(),
                    "optimization_period_days": optimization_period_days,
                    "optimization_method": optimization_method,
                    "api_version": "v3_optimization"
                }
            }
        else:
            response_data = {
                "success": False,
                "error": "optimization_failed",
                "message": "Parameter optimization failed",
                "optimization_result": {
                    "success": optimization_result.success,
                    "optimization_details": optimization_result.optimization_details
                }
            }
        
        return JsonResponse(response_data, json_dumps_params={'ensure_ascii': False})
        
    except ValueError as e:
        return JsonResponse({
            "success": False,
            "error": "invalid_parameters",
            "message": f"Invalid parameters: {str(e)}"
        }, status=400)
    except Exception as e:
        logger.error(f"❌ Parameter optimization API error: {str(e)}", exc_info=True)
        return JsonResponse({
            "success": False,
            "error": "internal_server_error",
            "message": f"Optimization failed: {str(e)}"
        }, status=500)


@csrf_exempt
@require_http_methods(["GET"])
def api_optimization_history(request):
    """
    Get parameter optimization history
    
    Returns:
        dict: {
            "success": bool,
            "optimization_history": list,
            "current_optimal_parameters": dict,
            "metadata": dict
        }
    """
    try:
        # Get optimization history
        history = parameter_optimization_service.get_optimization_history()
        
        # Get current optimal parameters
        current_optimal = parameter_optimization_service.get_current_optimal_parameters()
        
        response_data = {
            "success": True,
            "optimization_history": [
                {
                    "timestamp": entry["timestamp"],
                    "period": entry["period"],
                    "success": entry["result"].success,
                    "improvement_rate": entry["result"].improvement_rate,
                    "performance_metrics": entry["result"].performance_metrics,
                    "optimization_details": {
                        "iterations": entry["result"].optimization_details.get("iterations", 0),
                        "final_score": entry["result"].optimization_details.get("final_score", 0.0)
                    }
                }
                for entry in history
            ],
            "current_optimal_parameters": {
                "frequency_weight": current_optimal.frequency_weight,
                "weekly_weight": current_optimal.weekly_weight,
                "monthly_weight": current_optimal.monthly_weight,
                "phase_weight": current_optimal.phase_weight,
                "min_cyclical_fitness": current_optimal.min_cyclical_fitness,
                "max_fatigue_risk": current_optimal.max_fatigue_risk,
                "prediction_limit": current_optimal.prediction_limit
            } if current_optimal else None,
            "metadata": {
                "total_optimizations": len(history),
                "successful_optimizations": sum(1 for entry in history if entry["result"].success),
                "latest_optimization": history[-1]["timestamp"] if history else None,
                "retrieved_at": timezone.now().isoformat()
            }
        }
        
        return JsonResponse(response_data, json_dumps_params={'ensure_ascii': False})
        
    except Exception as e:
        logger.error(f"❌ Optimization history API error: {str(e)}", exc_info=True)
        return JsonResponse({
            "success": False,
            "error": "internal_server_error",
            "message": f"Failed to retrieve history: {str(e)}"
        }, status=500)


    """
    Analyze A/B test results
    
    GET params:
        - test_name: str
        
    Returns:
        dict: {
            "success": bool,
            "analysis": dict,
            "metadata": dict
        }
    """
    try:
        test_name = request.GET.get('test_name')
        
        if not test_name:
            return JsonResponse({
                "success": False,
                "error": "missing_test_name",
                "message": "test_name parameter is required"
            }, status=400)
        
        # Analyze A/B test
        analysis = ab_testing_service.analyze_ab_test(test_name)
        
        response_data = {
            "success": True,
            "analysis": {
                "test_name": analysis.test_name,
                "analysis_date": analysis.analysis_date,
                "total_days": analysis.total_days,
                "variants_performance": analysis.variants_performance,
                "statistical_significance": analysis.statistical_significance,
                "winner": analysis.winner,
                "confidence_level": analysis.confidence_level,
                "recommendations": analysis.recommendations
            },
            "metadata": {
                "analyzed_at": timezone.now().isoformat(),
                "api_version": "v3_ab_testing"
            }
        }
        
        return JsonResponse(response_data, json_dumps_params={'ensure_ascii': False})
        
    except Exception as e:
        logger.error(f"❌ A/B test analysis API error: {str(e)}", exc_info=True)
        return JsonResponse({
            "success": False,
            "error": "internal_server_error",
            "message": f"Failed to analyze A/B test: {str(e)}"
        }, status=500)