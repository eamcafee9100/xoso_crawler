import logging
from datetime import date, datetime, timedelta
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.utils import timezone

from predictions_tracker.core.services.ParameterOptimizationService import (
    parameter_optimization_service,
    OptimizationParameters
)
from predictions_tracker.core.services.ABTestingService import ab_testing_service
from predictions_tracker.models import ABTestVariant, ABTestResult

logger = logging.getLogger(__name__)


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


@csrf_exempt
@require_http_methods(["POST"])
def api_create_ab_test(request):
    """
    Create A/B test
    
    POST JSON body:
        {
            "test_name": str,
            "target_method_code": str,
            "test_parameters": dict,
            "baseline_parameters": dict,
            "traffic_percentage": float (default: 50.0),
            "test_duration_days": int (default: 30),
            "success_criteria": dict (optional),
            "created_by": str (default: "api")
        }
        
    Returns:
        dict: {
            "success": bool,
            "test_variant": dict,
            "message": str
        }
    """
    try:
        import json
        
        # Parse JSON body
        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse({
                "success": False,
                "error": "invalid_json",
                "message": "Invalid JSON in request body"
            }, status=400)
        
        # Validate required fields
        required_fields = ['test_name', 'target_method_code', 'test_parameters', 'baseline_parameters']
        missing_fields = [field for field in required_fields if field not in data]
        if missing_fields:
            return JsonResponse({
                "success": False,
                "error": "missing_fields",
                "message": f"Missing required fields: {', '.join(missing_fields)}"
            }, status=400)
        
        # Extract parameters with defaults
        test_name = data['test_name']
        target_method_code = data['target_method_code']
        test_parameters = data['test_parameters']
        baseline_parameters = data['baseline_parameters']
        traffic_percentage = data.get('traffic_percentage', 50.0)
        test_duration_days = data.get('test_duration_days', 30)
        success_criteria = data.get('success_criteria', None)
        created_by = data.get('created_by', 'api')
        
        logger.info(f"🧪 Creating A/B test via API: {test_name}")
        
        # Create A/B test using service
        result = ab_testing_service.create_ab_test(
            test_name=test_name,
            target_method_code=target_method_code,
            test_parameters=test_parameters,
            baseline_parameters=baseline_parameters,
            traffic_percentage=traffic_percentage,
            test_duration_days=test_duration_days,
            success_criteria=success_criteria,
            created_by=created_by
        )
        
        # Add API metadata
        if result["success"]:
            result["metadata"] = {
                "created_via": "api",
                "api_version": "v3_ab_testing",
                "created_at": timezone.now().isoformat()
            }
        
        return JsonResponse(result, json_dumps_params={'ensure_ascii': False})
        
    except Exception as e:
        logger.error(f"❌ Create A/B test API error: {str(e)}", exc_info=True)
        return JsonResponse({
            "success": False,
            "error": "internal_server_error",
            "message": f"Failed to create A/B test: {str(e)}"
        }, status=500)


@csrf_exempt
@require_http_methods(["POST"])
def api_execute_ab_test(request):
    """
    Execute A/B test for specific date
    
    POST JSON body:
        {
            "test_date": str (YYYY-MM-DD),
            "method_code": str,
            "predicted_numbers": list,
            "actual_numbers": list
        }
        
    Returns:
        dict: {
            "success": bool,
            "variant_used": str,
            "test_result": dict,
            "message": str
        }
    """
    try:
        import json
        
        # Parse JSON body
        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse({
                "success": False,
                "error": "invalid_json",
                "message": "Invalid JSON in request body"
            }, status=400)
        
        # Validate required fields
        required_fields = ['test_date', 'method_code', 'predicted_numbers', 'actual_numbers']
        missing_fields = [field for field in required_fields if field not in data]
        if missing_fields:
            return JsonResponse({
                "success": False,
                "error": "missing_fields",
                "message": f"Missing required fields: {', '.join(missing_fields)}"
            }, status=400)
        
        # Parse test date
        try:
            test_date = datetime.strptime(data['test_date'], "%Y-%m-%d").date()
        except ValueError:
            return JsonResponse({
                "success": False,
                "error": "invalid_date_format",
                "message": "Invalid date format. Use YYYY-MM-DD"
            }, status=400)
        
        # Execute A/B test
        result = ab_testing_service.execute_ab_test(
            test_date=test_date,
            method_code=data['method_code'],
            predicted_numbers=data['predicted_numbers'],
            actual_numbers=data['actual_numbers']
        )
        
        # Add API metadata
        if result["success"]:
            result["metadata"] = {
                "executed_via": "api",
                "api_version": "v3_ab_testing",
                "executed_at": timezone.now().isoformat()
            }
        
        return JsonResponse(result, json_dumps_params={'ensure_ascii': False})
        
    except Exception as e:
        logger.error(f"❌ Execute A/B test API error: {str(e)}", exc_info=True)
        return JsonResponse({
            "success": False,
            "error": "internal_server_error",
            "message": f"Failed to execute A/B test: {str(e)}"
        }, status=500)


@csrf_exempt
@require_http_methods(["GET"])
def api_get_ab_test_results(request):
    """
    Get A/B test results
    
    GET params:
        - test_name: str (optional)
        - method_code: str (optional)  
        - start_date: str YYYY-MM-DD (optional)
        - end_date: str YYYY-MM-DD (optional)
        
    Returns:
        dict: {
            "success": bool,
            "test_results": list,
            "summary": dict,
            "message": str
        }
    """
    try:
        # Get query parameters
        test_name = request.GET.get('test_name')
        method_code = request.GET.get('method_code')
        start_date_str = request.GET.get('start_date')
        end_date_str = request.GET.get('end_date')
        
        # Parse dates if provided
        start_date = None
        end_date = None
        
        if start_date_str:
            try:
                start_date = datetime.strptime(start_date_str, "%Y-%m-%d").date()
            except ValueError:
                return JsonResponse({
                    "success": False,
                    "error": "invalid_start_date_format",
                    "message": "Invalid start_date format. Use YYYY-MM-DD"
                }, status=400)
        
        if end_date_str:
            try:
                end_date = datetime.strptime(end_date_str, "%Y-%m-%d").date()
            except ValueError:
                return JsonResponse({
                    "success": False,
                    "error": "invalid_end_date_format",
                    "message": "Invalid end_date format. Use YYYY-MM-DD"
                }, status=400)
        
        # Get results from service
        result = ab_testing_service.get_ab_test_results(
            test_name=test_name,
            method_code=method_code,
            start_date=start_date,
            end_date=end_date
        )
        
        # Add API metadata
        if result["success"]:
            result["metadata"] = {
                "retrieved_via": "api",
                "api_version": "v3_ab_testing",
                "retrieved_at": timezone.now().isoformat(),
                "filters_applied": {
                    "test_name": test_name,
                    "method_code": method_code,
                    "start_date": start_date_str,
                    "end_date": end_date_str
                }
            }
        
        return JsonResponse(result, json_dumps_params={'ensure_ascii': False})
        
    except Exception as e:
        logger.error(f"❌ Get A/B test results API error: {str(e)}", exc_info=True)
        return JsonResponse({
            "success": False,
            "error": "internal_server_error",
            "message": f"Failed to get A/B test results: {str(e)}"
        }, status=500)


@csrf_exempt
@require_http_methods(["POST"])
def api_compare_ab_test_variants(request):
    """
    Compare A/B test variants
    
    POST JSON body:
        {
            "test_name": str,
            "baseline_variant": str (default: "baseline"),
            "test_variant": str (default: "test_variant")
        }
        
    Returns:
        dict: {
            "success": bool,
            "comparison": dict,
            "statistical_significance": dict,
            "recommendation": str,
            "message": str
        }
    """
    try:
        import json
        
        # Parse JSON body
        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse({
                "success": False,
                "error": "invalid_json",
                "message": "Invalid JSON in request body"
            }, status=400)
        
        # Validate required fields
        if 'test_name' not in data:
            return JsonResponse({
                "success": False,
                "error": "missing_test_name",
                "message": "test_name is required"
            }, status=400)
        
        # Get parameters with defaults
        test_name = data['test_name']
        baseline_variant = data.get('baseline_variant', 'baseline')
        test_variant = data.get('test_variant', 'test_variant')
        
        # Compare variants using service
        result = ab_testing_service.compare_variants(
            test_name=test_name,
            baseline_variant=baseline_variant,
            test_variant=test_variant
        )
        
        # Add API metadata
        if result["success"]:
            result["metadata"] = {
                "compared_via": "api",
                "api_version": "v3_ab_testing",
                "compared_at": timezone.now().isoformat(),
                "comparison_params": {
                    "test_name": test_name,
                    "baseline_variant": baseline_variant,
                    "test_variant": test_variant
                }
            }
        
        return JsonResponse(result, json_dumps_params={'ensure_ascii': False})
        
    except Exception as e:
        logger.error(f"❌ Compare A/B test variants API error: {str(e)}", exc_info=True)
        return JsonResponse({
            "success": False,
            "error": "internal_server_error",
            "message": f"Failed to compare variants: {str(e)}"
        }, status=500)


@csrf_exempt
@require_http_methods(["POST"])
def api_conclude_ab_test(request):
    """
    Conclude A/B test
    
    POST JSON body:
        {
            "test_name": str,
            "conclusion": str ("auto", "deploy_test", "keep_baseline", "continue")
        }
        
    Returns:
        dict: {
            "success": bool,
            "conclusion": str,
            "final_results": dict,
            "message": str
        }
    """
    try:
        import json
        
        # Parse JSON body
        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse({
                "success": False,
                "error": "invalid_json", 
                "message": "Invalid JSON in request body"
            }, status=400)
        
        # Validate required fields
        if 'test_name' not in data:
            return JsonResponse({
                "success": False,
                "error": "missing_test_name",
                "message": "test_name is required"
            }, status=400)
        
        # Get parameters
        test_name = data['test_name']
        conclusion = data.get('conclusion', 'auto')
        
        # Validate conclusion parameter
        valid_conclusions = ['auto', 'deploy_test', 'keep_baseline', 'continue']
        if conclusion not in valid_conclusions:
            return JsonResponse({
                "success": False,
                "error": "invalid_conclusion",
                "message": f"conclusion must be one of: {', '.join(valid_conclusions)}"
            }, status=400)
        
        # Conclude A/B test using service
        result = ab_testing_service.conclude_ab_test(
            test_name=test_name,
            conclusion=conclusion
        )
        
        # Add API metadata
        if result["success"]:
            result["metadata"] = {
                "concluded_via": "api",
                "api_version": "v3_ab_testing",
                "concluded_at": timezone.now().isoformat(),
                "conclusion_params": {
                    "test_name": test_name,
                    "conclusion_method": conclusion
                }
            }
        
        return JsonResponse(result, json_dumps_params={'ensure_ascii': False})
        
    except Exception as e:
        logger.error(f"❌ Conclude A/B test API error: {str(e)}", exc_info=True)
        return JsonResponse({
            "success": False,
            "error": "internal_server_error",
            "message": f"Failed to conclude A/B test: {str(e)}"
        }, status=500)
        
        