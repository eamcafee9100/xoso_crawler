from django.shortcuts import render
from django.contrib import messages
from django.utils import timezone
from datetime import date, timedelta
from typing import Dict, List, Any, Optional
import json
import logging
from collections import defaultdict
from predictions_tracker.models import PredictionMethod, DailyTrackingSession, TrackingEvaluation
from results.models import KetQuaXoSo   
from django.http import HttpRequest, HttpResponse
from django.db import models
# Initialize logger
logger = logging.getLogger(__name__)

def test_ml_train(request):
    """
    View test ML training và prediction performance
    
    Returns:
        Template response với training results và performance metrics
    """
    if request.method == 'POST':
        try:
            # ✅ Parse form data
            target_date_str = request.POST.get('target_date')
            method_ids = request.POST.getlist('method_ids')
            months_back = int(request.POST.get('months_back', 3))
            
            if not target_date_str:
                messages.error(request, "Vui lòng chọn ngày dự đoán")
                return render(request, 'predictions_tracker/test_ml_train.html', _get_form_context())
            
            target_date = date.fromisoformat(target_date_str)
            
            # ✅ Validate target_date
            if target_date >= date.today():
                messages.error(request, "Ngày dự đoán phải là ngày trong quá khứ để có thể so sánh với kết quả thực tế")
                return render(request, 'predictions_tracker/test_ml_train.html', _get_form_context())
            
            # ✅ Get selected methods
            if not method_ids:
                active_methods = PredictionMethod.objects.filter(is_active=True)
                method_ids = [str(m.id) for m in active_methods]
            
            # ✅ Perform ML training and testing
            test_results = _perform_ml_training_test(
                target_date=target_date,
                method_ids=method_ids,
                months_back=months_back
            )
            
            context = {
                'form_data': {
                    'target_date': target_date_str,
                    'method_ids': method_ids,
                    'months_back': months_back,
                },
                'test_results': test_results,
                'has_results': True,
            }
            context.update(_get_form_context())
            
            return render(request, 'predictions_tracker/test_ml_train.html', context)
            
        except Exception as e:
            logger.error(f"Error in test_ml_train: {e}")
            messages.error(request, f"Lỗi khi thực hiện test: {str(e)}")
            return render(request, 'predictions_tracker/test_ml_train.html', _get_form_context())
    
    # GET request - show form
    return render(request, 'predictions_tracker/test_ml_train.html', _get_form_context())

def _get_form_context() -> Dict[str, Any]:
    """
    Lấy context cho form
    
    Returns:
        Dict với methods và default values
    """
    return {
        'methods': PredictionMethod.objects.filter(is_active=True).order_by('name'),
        'default_months_back': 3,
        'max_date': date.today() - timedelta(days=1),
        'has_results': False,
    }

def _perform_ml_training_test(target_date: date, method_ids: List[str], months_back: int) -> Dict[str, Any]:
    """
    Thực hiện training và testing ML models
    
    Args:
        target_date: Ngày dự đoán
        method_ids: Danh sách method IDs
        months_back: Số tháng training data
        
    Returns:
        Dict chứa kết quả training và testing với structure:
        {
            'target_date': date,
            'training_info': {
                'start_date': date,
                'end_date': date,
                'total_days': int,
                'data_points': List[Dict],
            },
            'method_results': List[Dict],
            'overall_metrics': Dict,
            'warnings': List[str],
        }
    """
    # ✅ Calculate training date range
    training_end_date = target_date - timedelta(days=1)  # Exclude target_date
    training_start_date = training_end_date - timedelta(days=months_back * 30)
    
    # ✅ Get training data
    training_info = _get_training_data_info(training_start_date, training_end_date)
    
    # ✅ Get actual results for target_date + 3 days
    actual_results = _get_actual_results_for_dates(target_date, target_date + timedelta(days=3))
    
    # ✅ Initialize results
    method_results = []
    warnings = []
    
    # ✅ Process each method
    for method_id in method_ids:
        try:
            method = PredictionMethod.objects.get(id=method_id)
            
            # ✅ Train ML model for this method
            ml_result = _train_and_predict_method(
                method=method,
                target_date=target_date,
                training_start_date=training_start_date,
                training_end_date=training_end_date,
                actual_results=actual_results
            )
            
            method_results.append(ml_result)
            
        except PredictionMethod.DoesNotExist:
            warnings.append(f"Method ID {method_id} không tồn tại")
        except Exception as e:
            logger.error(f"Error training method {method_id}: {e}")
            warnings.append(f"Lỗi khi training method {method_id}: {str(e)}")
    
    # ✅ Calculate overall metrics
    overall_metrics = _calculate_overall_metrics(method_results)
    
    return {
        'target_date': target_date,
        'training_info': training_info,
        'method_results': method_results,
        'overall_metrics': overall_metrics,
        'warnings': warnings,
        'actual_results': actual_results,
    }

def _get_training_data_info(start_date: date, end_date: date) -> Dict[str, Any]:
    """
    Lấy thông tin chi tiết training data
    
    Returns:
        Dict chứa thông tin training data
    """
    # ✅ Get all sessions in training period
    sessions = DailyTrackingSession.objects.filter(
        prediction_date__range=[start_date, end_date]
    ).select_related('cycle').order_by('prediction_date')
    
    # ✅ Get evaluations for these sessions
    evaluations = TrackingEvaluation.objects.filter(
        method_result__session__in=sessions
    ).select_related('method_result__method')
    
    # ✅ Build data points summary
    data_points = []
    for session in sessions:
        session_evals = evaluations.filter(method_result__session=session)
        
        data_points.append({
            'date': session.prediction_date,
            'cycle': session.cycle.cycle_name if session.cycle else 'Auto',
            'methods_count': session_evals.values('method_result__method').distinct().count(),
            'evaluations_count': session_evals.count(),
            'avg_hit_rate': session_evals.aggregate(avg_hit_rate=models.Avg('hit_rate'))['avg_hit_rate'] or 0,
        })
    
    return {
        'start_date': start_date,
        'end_date': end_date,
        'total_days': (end_date - start_date).days + 1,
        'sessions_count': sessions.count(),
        'data_points': data_points,
        'evaluations_count': evaluations.count(),
    }

def _get_actual_results_for_dates(start_date: date, end_date: date) -> Dict[str, List[str]]:
    """
    Lấy kết quả thực tế cho range ngày
    
    Returns:
        Dict mapping date -> list of 2-digit numbers
    """
    actual_results = {}
    
    current_date = start_date
    while current_date <= end_date:
        try:
            ketqua = KetQuaXoSo.objects.get(ngay=current_date)
            actual_results[current_date.isoformat()] = list(ketqua.get_all_2digit_numbers())
        except KetQuaXoSo.DoesNotExist:
            actual_results[current_date.isoformat()] = []
        
        current_date += timedelta(days=1)
    
    return actual_results

def _train_and_predict_method(
    method: PredictionMethod,
    target_date: date,
    training_start_date: date,
    training_end_date: date,
    actual_results: Dict[str, List[str]]
) -> Dict[str, Any]:
    """
    ✅ SỬA: Sử dụng DataService để lấy training data
    """
    # ✅ Import DataService
    try:
        from predictions_tracker.core.services.DataService import data_service
        use_data_service = True
    except ImportError:
        data_service = None
        use_data_service = False
        logger.warning("⚠️ DataService not available, using fallback")
    
    # ✅ Import tracking service
    from predictions_tracker.core.services.TrackingService import TrackingService
    
    tracking_service = TrackingService()
    
    # ✅ Get training data - TRY DataService first
    if use_data_service and data_service is not None:
        try:
            months_back = ((training_end_date - training_start_date).days // 30) + 1
            
            # Get comprehensive historical data
            historical_patterns = data_service.get_comprehensive_historical_data(
                target_date=training_end_date.isoformat(),
                method_ids=[method.id],
                months_back=months_back
            )
            
            method_id_str = str(method.id)
            
            if (historical_patterns and 
                historical_patterns.get('hit_day_1') and 
                method_id_str in historical_patterns['hit_day_1']):
                
                training_data_length = len(historical_patterns['hit_day_1'][method_id_str])
                logger.info(f"✅ Using DataService training data for method {method.id}: {training_data_length} points")
                
                # Convert patterns to training data format
                training_data = []
                for i in range(training_data_length):
                    training_data.append({
                        'date': training_start_date + timedelta(days=i),
                        'prediction_date': training_start_date + timedelta(days=i),
                        'predicted_numbers': [],  # Placeholder
                        'hit_numbers': [],
                        'hit_count': historical_patterns['hit_day_1'][method_id_str][i],
                        'hit_rate': historical_patterns['hit_day_1'][method_id_str][i] * 100,
                        'wilson_score': 0.5,
                    })
                
            else:
                logger.warning(f"⚠️ No DataService data for method {method.id}, using fallback")
                training_data = _get_method_training_data(method, training_start_date, training_end_date)
                
        except Exception as ds_error:
            logger.warning(f"⚠️ DataService error: {ds_error}, using fallback")
            training_data = _get_method_training_data(method, training_start_date, training_end_date)
    else:
        training_data = _get_method_training_data(method, training_start_date, training_end_date)
    
    # ✅ REST OF LOGIC REMAINS THE SAME...
    if len(training_data) < 10:
        return {
            'method': {
                'id': method.id,
                'name': method.name,
                'category': method.get_category_display(),
            },
            'training_data': training_data,
            'predictions': [],
            'comparison': [],
            'metrics': {},
            'error': f"Không đủ dữ liệu training (có {len(training_data)}, cần ít nhất 10)",
        }
    
    try:
        # ✅ Train ML model và predict
        ml_results = tracking_service.get_enhanced_ml_predictions(
            method_ids=[method.id],
            target_date=target_date,
            use_trained_models=False,  # Train fresh model
            training_months=((training_end_date - training_start_date).days // 30) + 1
        )
        
        # ✅ Get predictions cho 3 ngày
        predictions = []
        comparison = []
        
        for day in range(1, 4):
            prediction_date = target_date + timedelta(days=day)
            
            # ✅ Get ML prediction
            method_prediction = ml_results.get(str(method.id), {})
            predicted_numbers = method_prediction.get('predicted_numbers', [])
            
            # ✅ Get actual numbers
            actual_numbers = actual_results.get(prediction_date.isoformat(), [])
            
            # ✅ Calculate comparison
            if actual_numbers:
                predicted_set = set(str(n).zfill(2) for n in predicted_numbers)
                actual_set = set(str(n).zfill(2) for n in actual_numbers)
                
                hit_numbers = list(predicted_set.intersection(actual_set))
                hit_count = len(hit_numbers)
                hit_rate = (hit_count / len(predicted_set)) * 100 if predicted_set else 0
                
                comparison.append({
                    'day': day,
                    'date': prediction_date,
                    'predicted_numbers': predicted_numbers,
                    'actual_numbers': actual_numbers,
                    'hit_numbers': hit_numbers,
                    'hit_count': hit_count,
                    'hit_rate': hit_rate,
                    'has_actual': True,
                })
            else:
                comparison.append({
                    'day': day,
                    'date': prediction_date,
                    'predicted_numbers': predicted_numbers,
                    'actual_numbers': [],
                    'hit_numbers': [],
                    'hit_count': 0,
                    'hit_rate': 0,
                    'has_actual': False,
                })
            
            predictions.append({
                'day': day,
                'date': prediction_date,
                'predicted_numbers': predicted_numbers,
                'confidence': method_prediction.get('confidence', 0),
                'model_type': method_prediction.get('model_type', 'unknown'),
            })
        
        # ✅ Calculate metrics
        metrics = _calculate_method_metrics(comparison)
        
        return {
            'method': {
                'id': method.id,
                'name': method.name,
                'category': method.get_category_display(),
            },
            'training_data': training_data,
            'predictions': predictions,
            'comparison': comparison,
            'metrics': metrics,
            'error': None,
        }
        
    except Exception as e:
        logger.error(f"Error training method {method.id}: {e}")
        return {
            'method': {
                'id': method.id,
                'name': method.name,
                'category': method.get_category_display(),
            },
            'training_data': training_data,
            'predictions': [],
            'comparison': [],
            'metrics': {},
            'error': str(e),
        }

def _get_method_training_data(method: PredictionMethod, start_date: date, end_date: date) -> List[Dict[str, Any]]:
    """
    Lấy training data cho method
    
    Returns:
        List các data points cho training
    """
    evaluations = TrackingEvaluation.objects.filter(
        method_result__method=method,
        evaluation_date__range=[start_date, end_date]
    ).select_related('method_result__session').order_by('evaluation_date')
    
    training_data = []
    for eval in evaluations:
        training_data.append({
            'date': eval.evaluation_date,
            'prediction_date': eval.method_result.session.prediction_date,
            'predicted_numbers': eval.method_result.base_prediction_numbers,
            'hit_numbers': eval.hit_numbers,
            'hit_count': eval.hit_count,
            'hit_rate': eval.hit_rate,
            'wilson_score': eval.wilson_score,
        })
    
    return training_data

def _calculate_method_metrics(comparison: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Tính toán metrics cho method
    
    Returns:
        Dict chứa các metrics
    """
    if not comparison:
        return {}
    
    # ✅ Filter comparisons có actual data
    valid_comparisons = [c for c in comparison if c['has_actual']]
    
    if not valid_comparisons:
        return {
            'no_actual_data': True,
            'message': 'Không có dữ liệu thực tế để so sánh'
        }
    
    # ✅ Basic metrics
    total_predictions = sum(len(c['predicted_numbers']) for c in valid_comparisons)
    total_hits = sum(c['hit_count'] for c in valid_comparisons)
    avg_hit_rate = sum(c['hit_rate'] for c in valid_comparisons) / len(valid_comparisons)
    
    # ✅ Binary classification metrics (hit/miss per day)
    tp = sum(1 for c in valid_comparisons if c['hit_count'] > 0)  # Days with hits
    fp = sum(1 for c in valid_comparisons if c['hit_count'] == 0)  # Days with no hits
    
    accuracy = tp / len(valid_comparisons) if valid_comparisons else 0
    
    # ✅ Detailed metrics per day
    day_metrics = {}
    for day in [1, 2, 3]:
        day_comps = [c for c in valid_comparisons if c['day'] == day]
        if day_comps:
            day_metrics[f'day_{day}'] = {
                'hit_rate': sum(c['hit_rate'] for c in day_comps) / len(day_comps),
                'hit_count': sum(c['hit_count'] for c in day_comps),
                'predictions_count': sum(len(c['predicted_numbers']) for c in day_comps),
                'accuracy': sum(1 for c in day_comps if c['hit_count'] > 0) / len(day_comps),
            }
    
    return {
        'total_predictions': total_predictions,
        'total_hits': total_hits,
        'avg_hit_rate': round(avg_hit_rate, 2),
        'accuracy': round(accuracy * 100, 2),
        'days_with_hits': tp,
        'days_without_hits': fp,
        'day_metrics': day_metrics,
        'no_actual_data': False,
    }

def _calculate_overall_metrics(method_results: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Tính toán overall metrics cho tất cả methods
    
    Returns:
        Dict chứa overall metrics
    """
    if not method_results:
        return {}
    
    # ✅ Filter methods có data
    valid_methods = [m for m in method_results if not m.get('error') and m.get('metrics', {}).get('no_actual_data') is False]
    
    if not valid_methods:
        return {
            'no_valid_methods': True,
            'message': 'Không có method nào có dữ liệu hợp lệ'
        }
    
    # ✅ Calculate averages
    avg_hit_rate = sum(m['metrics']['avg_hit_rate'] for m in valid_methods) / len(valid_methods)
    avg_accuracy = sum(m['metrics']['accuracy'] for m in valid_methods) / len(valid_methods)
    
    # ✅ Best performing method
    best_method = max(valid_methods, key=lambda m: m['metrics']['avg_hit_rate'])
    
    # ✅ Methods ranking
    methods_ranking = sorted(valid_methods, key=lambda m: m['metrics']['avg_hit_rate'], reverse=True)
    
    return {
        'total_methods': len(method_results),
        'valid_methods': len(valid_methods),
        'avg_hit_rate': round(avg_hit_rate, 2),
        'avg_accuracy': round(avg_accuracy, 2),
        'best_method': {
            'name': best_method['method']['name'],
            'hit_rate': best_method['metrics']['avg_hit_rate'],
            'accuracy': best_method['metrics']['accuracy'],
        },
        'methods_ranking': [
            {
                'name': m['method']['name'],
                'hit_rate': m['metrics']['avg_hit_rate'],
                'accuracy': m['metrics']['accuracy'],
            }
            for m in methods_ranking
        ],
        'no_valid_methods': False,
    }