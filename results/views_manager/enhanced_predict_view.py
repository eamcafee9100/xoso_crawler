import logging
import time
from collections import defaultdict
from datetime import date, datetime, timedelta
from typing import Any, Dict, List, Optional, Tuple

from django.contrib import messages
from django.core.cache import cache
from django.db import transaction
from django.http import JsonResponse
from django.shortcuts import render
from django.utils import timezone
from django.views.generic import TemplateView
from results.predictor import AdvancedLotteryPredictor
from results.models import (
    CycleAccuracy,
    KetQuaXoSo,
    ModelTrainingHistory,
    PredictionPerformanceMetrics,
    PredictionRecord,
)
from results.predictor import EnhancedCyclePredictor
from results.services.enhanced_predict_view.DataQualityAssessment import (
    DataQualityAssessment,
)
from results.services.enhanced_predict_view.IntelligentPredictionCache import (
    IntelligentPredictionCache,
)
from results.services.enhanced_predict_view.ModelPerformanceTracker import (
    ModelPerformanceTracker,
)
from results.services.enhanced_predict_view.ValidationService import ValidationService

logger = logging.getLogger(__name__)


class ValidationError(Exception):
    """Custom validation error"""

    pass


class InsufficientDataError(Exception):
    """Insufficient data error"""

    pass


class ModelTrainingError(Exception):
    """Model training error"""

    pass


class EnhancedPredictView(TemplateView):
    """
    Enhanced Prediction View với tất cả cải tiến
    """

    template_name = "results/enhanced_predict.html"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.prediction_cache = IntelligentPredictionCache()
        self.performance_tracker = ModelPerformanceTracker()
        self.data_quality = DataQualityAssessment()
        self.validator = ValidationService()
        self.predictor = None

    def get_context_data(self, **kwargs):
        """Main entry point with comprehensive error handling"""
        context = super().get_context_data(**kwargs)
        start_time = time.time()
        logger.info("[EnhancedPredictView] Bắt đầu get_context_data với kwargs=%s", kwargs)

        # Initialize default context
        context.update(self._get_default_context())
        logger.debug("[EnhancedPredictView] Đã khởi tạo default context.")

        try:
            # 1. Parse and validate dates
            analysis_date, prediction_date = self._parse_and_validate_dates()
            logger.info("[EnhancedPredictView] Đã parse ngày: analysis_date=%s, prediction_date=%s", analysis_date, prediction_date)
            context.update({
                'analysis_date': analysis_date,
                'prediction_date': prediction_date,
                'is_future_prediction': prediction_date > timezone.now().date()
            })

            # 2. Check cache first
            cache_key = f"{analysis_date}_{prediction_date}"
            cached_result = self.prediction_cache.get_cached_prediction(
                analysis_date, 
                self._get_current_model_version()
            )
            logger.debug("[EnhancedPredictView] Cache key: %s, force_refresh=%s", cache_key, self.request.GET.get('force_refresh'))

            if cached_result and not self.request.GET.get('force_refresh'):
                logger.info("[EnhancedPredictView] Cache HIT cho ngày %s", analysis_date)
                formatted_cache = self._format_cached_data(cached_result)
                context.update(formatted_cache)
                context['from_cache'] = True
                context['processing_time'] = time.time() - start_time
                logger.info("[EnhancedPredictView] Trả về kết quả từ cache, thời gian xử lý: %.3fs", context['processing_time'])
                return context
            logger.info("[EnhancedPredictView] Cache MISS hoặc force_refresh, tiếp tục xử lý...")

            # 3. Get and validate historical data
            historical_data, data_quality_metrics = self._get_intelligent_historical_data(analysis_date)
            logger.info("[EnhancedPredictView] Lấy dữ liệu lịch sử: %d records, quality: %.2f", len(historical_data), data_quality_metrics.get("quality_score", 0))

            # 4. Initialize predictor with validated data
            self.predictor = self._get_or_create_predictor(analysis_date, historical_data)
            logger.info("[EnhancedPredictView] Predictor đã được khởi tạo: %s", type(self.predictor).__name__)

            # 5. Generate predictions with validation
            predictions = self._generate_validated_predictions(historical_data, prediction_date)
            logger.info("[EnhancedPredictView] Đã sinh %d predictions", len(predictions))

            # 6. Get traditional predictions for comparison
            traditional_predictions = self._get_traditional_predictions(historical_data, prediction_date)
            logger.info("[EnhancedPredictView] Đã lấy traditional predictions: %d methods", traditional_predictions.get("method_count", 0))

            # 7. Combine predictions intelligently
            combined_predictions = self._intelligent_prediction_combination(
                ml_predictions=predictions,
                traditional_predictions=traditional_predictions,
                historical_performance=self.performance_tracker.get_recent_performance()
            )
            logger.info("[EnhancedPredictView] Đã kết hợp predictions, tổng số: %d", len(combined_predictions))

            # 8. Process actual results if available
            actual_result = self._get_actual_result_safe(prediction_date)
            performance_metrics = None

            if actual_result:
                logger.info("[EnhancedPredictView] Có kết quả thực tế cho ngày %s: ĐB=%s", 
                        prediction_date, actual_result.get('giai_db'))
                performance_metrics = self._evaluate_and_improve_model(
                    combined_predictions, actual_result, analysis_date
                )
                logger.info("[EnhancedPredictView] Đánh giá performance: %s", performance_metrics)
            else:
                logger.info("[EnhancedPredictView] Chưa có kết quả thực tế cho ngày %s", prediction_date)

            # 9. Format ALL data for template consumption - ✅ Pass actual_result to formatter
            formatted_predictions = self._format_predictions_for_display(combined_predictions, actual_result)
            formatted_traditional = self._format_traditional_predictions(traditional_predictions, actual_result)
            formatted_data_quality = self._format_data_quality(data_quality_metrics)
            formatted_model_metadata = self._format_model_metadata()
            formatted_prediction_confidence = self._format_prediction_confidence(combined_predictions)
            logger.debug("[EnhancedPredictView] Đã format dữ liệu cho template.")

            # 10. Prepare comprehensive context
            context.update({
                'predictions': formatted_predictions,
                'traditional_predictions': formatted_traditional,
                'data_quality': formatted_data_quality,
                'model_metadata': formatted_model_metadata,
                'prediction_confidence': formatted_prediction_confidence,
                'actual_result': actual_result,  # ✅ Dict format, not object
                'performance_metrics': performance_metrics,
                'processing_time': time.time() - start_time,
                # ✅ Add hit summary for template
                'hit_summary': self._calculate_hit_summary(formatted_predictions, actual_result) if actual_result else None,
                'cache_info': {
                    'from_cache': False,
                    'cache_key': cache_key,
                    'cached_at': datetime.now().isoformat()
                }
            })
            logger.info("[EnhancedPredictView] Đã chuẩn bị context đầy đủ cho template.")

            # 11. Cache the result with proper formatting
            self._cache_result_safely(analysis_date, context)
            logger.debug("[EnhancedPredictView] Đã cache kết quả mới.")

        except ValidationError as e:
            logger.error("[EnhancedPredictView] ValidationError: %s", e)
            context.update(self._handle_validation_error(e))
        except InsufficientDataError as e:
            logger.error("[EnhancedPredictView] InsufficientDataError: %s", e)
            context.update(self._handle_data_error(e))
        except ModelTrainingError as e:
            logger.error("[EnhancedPredictView] ModelTrainingError: %s", e)
            context.update(self._handle_model_error(e))
        except Exception as e:
            logger.exception("[EnhancedPredictView] Lỗi không xác định: %s", e)

            context.update(self._handle_unexpected_error(e))

        context['processing_time'] = time.time() - start_time
        logger.info("[EnhancedPredictView] Kết thúc get_context_data, tổng thời gian: %.3fs", context['processing_time'])
        return context

    def _format_cached_data(self, cached_data: Dict) -> Dict:
        """
        Format cached data to ensure template compatibility
        
        Returns:
            Dict: Properly formatted data for template
        """
        try:
            formatted = {}
            
            # Ensure predictions is a list of dicts
            if 'predictions' in cached_data:
                if isinstance(cached_data['predictions'], dict):
                    formatted['predictions'] = self._format_predictions_for_display(cached_data['predictions'])
                elif isinstance(cached_data['predictions'], list):
                    formatted['predictions'] = cached_data['predictions']
                else:
                    formatted['predictions'] = []
            else:
                formatted['predictions'] = []
            
            # Ensure other fields are properly formatted
            formatted['data_quality'] = cached_data.get('data_quality', {
                'quality_score': 0.0,
                'total_records': 0,
                'valid_records': 0,
                'issues': []
            })
            
            formatted['model_metadata'] = cached_data.get('model_metadata', {
                'version': 'N/A',
                'last_trained': None,
                'features': []
            })
            
            formatted['prediction_confidence'] = cached_data.get('prediction_confidence', {
                'overall': 0,
                'top_prediction': 0,
                'distribution': 'poor'
            })
            
            formatted['traditional_predictions'] = cached_data.get('traditional_predictions', {
                'method_predictions': [],
                'method_count': 0,
                'confidence': 0
            })
            
            return formatted
            
        except Exception as e:
            logger.error(f"Error formatting cached data: {e}")
            return self._get_default_context()

    def _format_traditional_predictions(self, traditional_predictions: Dict, actual_result: Optional[Dict] = None) -> Dict:
        """
        Format traditional predictions for template with hit detection
        """
        try:
            if not traditional_predictions:
                return {
                    'method_predictions': [],
                    'method_count': 0,
                    'confidence': 0.0
                }
            
            # Get winning numbers for comparison
            winning_numbers = []
            if actual_result and actual_result.get('all_numbers'):
                winning_numbers = actual_result['all_numbers']
            
            method_predictions = traditional_predictions.get('method_predictions', [])
            
            if hasattr(method_predictions, 'to_dict'):
                method_predictions = method_predictions.to_dict('records')
            elif not isinstance(method_predictions, list):
                method_predictions = []
            
            # Format each method prediction with hit detection
            formatted_methods = []
            for method in method_predictions:
                if isinstance(method, dict):
                    numbers = list(method.get('numbers', []))
                    
                    # Calculate hits for this method
                    hit_numbers = [num for num in numbers if num in winning_numbers]
                    hit_rate = (len(hit_numbers) / len(numbers)) * 100 if numbers else 0
                    
                    formatted_method = {
                        'method': str(method.get('method', 'unknown')),
                        'numbers': numbers,
                        'confidence': float(method.get('confidence', 0.0)) * 100,
                        'hit_numbers': hit_numbers,  # ✅ Số trúng
                        'hit_rate': round(hit_rate, 1),  # ✅ Tỷ lệ trúng
                        'total_hits': len(hit_numbers)  # ✅ Tổng số trúng
                    }
                    formatted_methods.append(formatted_method)
            
            return {
                'method_predictions': formatted_methods,
                'method_count': len(formatted_methods),
                'confidence': traditional_predictions.get('confidence', 0.0)
            }
            
        except Exception as e:
            logger.error(f"Error formatting traditional predictions: {e}")
            return {
                'method_predictions': [],
                'method_count': 0,
                'confidence': 0.0
            }

    def _calculate_hit_summary(self, predictions: List[Dict], actual_result: Dict) -> Dict:
        """
        Calculate hit summary statistics for template display
        
        Returns:
            Dict: {
                "total_predictions": int,
                "total_hits": int,
                "special_hits": int,
                "hit_rate": float,
                "top_hit_rank": int or None
            }
        """
        try:
            total_predictions = len(predictions)
            total_hits = sum(1 for p in predictions if p.get('is_hit'))
            special_hits = sum(1 for p in predictions if p.get('is_special_hit'))
            hit_rate = (total_hits / total_predictions) * 100 if total_predictions > 0 else 0
            
            # Find best hit rank
            hit_ranks = [p['rank'] for p in predictions if p.get('is_hit')]
            top_hit_rank = min(hit_ranks) if hit_ranks else None
            
            return {
                'total_predictions': total_predictions,
                'total_hits': total_hits,
                'special_hits': special_hits,
                'hit_rate': round(hit_rate, 1),
                'top_hit_rank': top_hit_rank
            }
            
        except Exception as e:
            logger.error(f"Error calculating hit summary: {e}")
            return {
                'total_predictions': 0,
                'total_hits': 0,
                'special_hits': 0,
                'hit_rate': 0.0,
                'top_hit_rank': None
            }
    
    def _format_data_quality(self, data_quality_metrics: Dict) -> Dict:
        """
        Format data quality metrics for template
        
        Returns:
            Dict: {
                "quality_score": float,
                "total_records": int,
                "valid_records": int,
                "issues": List[str],
                "completeness": float,
                "consistency": float,
                "accuracy": float,
                "freshness": float,
                "coverage": float
            }
        """
        try:
            if not data_quality_metrics:
                return {
                    'quality_score': 0.0,
                    'total_records': 0,
                    'valid_records': 0,
                    'issues': [],
                    'completeness': 0.0,
                    'consistency': 0.0,
                    'accuracy': 0.0,
                    'freshness': 0.0,
                    'coverage': 0.0
                }
            
            # Ensure all numeric values are properly formatted
            formatted = {}
            
            numeric_fields = ['quality_score', 'completeness', 'consistency', 'accuracy', 'freshness', 'coverage']
            for field in numeric_fields:
                value = data_quality_metrics.get(field, 0.0)
                formatted[field] = float(value) if isinstance(value, (int, float)) else 0.0
            
            integer_fields = ['total_records', 'valid_records']
            for field in integer_fields:
                value = data_quality_metrics.get(field, 0)
                formatted[field] = int(value) if isinstance(value, (int, float)) else 0
            
            # Ensure issues is a list of strings
            issues = data_quality_metrics.get('issues', [])
            if isinstance(issues, list):
                formatted['issues'] = [str(issue) for issue in issues]
            else:
                formatted['issues'] = []
            
            return formatted
            
        except Exception as e:
            logger.error(f"Error formatting data quality: {e}")
            return {
                'quality_score': 0.0,
                'total_records': 0,
                'valid_records': 0,
                'issues': [],
                'completeness': 0.0,
                'consistency': 0.0,
                'accuracy': 0.0,
                'freshness': 0.0,
                'coverage': 0.0
            }

    def _format_model_metadata(self) -> Dict:
        """
        Format model metadata for template
        
        Returns:
            Dict: {
                "version": str,
                "last_trained": str or None,
                "features": List[str],
                "is_trained": bool
            }
        """
        try:
            if not self.predictor:
                return {
                    'version': 'N/A',
                    'last_trained': None,
                    'features': [],
                    'is_trained': False
                }
            
            metadata = self.predictor.get_metadata()
            
            # Format last_trained as string if it's a datetime
            last_trained = metadata.get('last_trained')
            if last_trained and hasattr(last_trained, 'isoformat'):
                last_trained = last_trained.isoformat()
            elif last_trained:
                last_trained = str(last_trained)
            else:
                last_trained = None
            
            return {
                'version': str(metadata.get('version', 'N/A')),
                'last_trained': last_trained,
                'features': list(metadata.get('features', [])),
                'is_trained': bool(metadata.get('is_trained', False))
            }
            
        except Exception as e:
            logger.error(f"Error formatting model metadata: {e}")
            return {
                'version': 'N/A',
                'last_trained': None,
                'features': [],
                'is_trained': False
            }

    def _format_prediction_confidence(self, predictions: Dict[str, float]) -> Dict:
        """
        Format prediction confidence for template
        
        Returns:
            Dict: {
                "overall": float,
                "top_prediction": float,
                "distribution": str
            }
        """
        try:
            if not predictions:
                return {
                    'overall': 0.0,
                    'top_prediction': 0.0,
                    'distribution': 'poor'
                }
            
            confidences = list(predictions.values())
            overall = sum(confidences) / len(confidences) if confidences else 0.0
            top_prediction = max(confidences) if confidences else 0.0
            
            # Determine distribution quality
            if overall >= 0.6:
                distribution = 'good'
            elif overall >= 0.4:
                distribution = 'fair'
            else:
                distribution = 'poor'
            
            return {
                'overall': round(overall * 100, 1),  # Convert to percentage
                'top_prediction': round(top_prediction * 100, 1),
                'distribution': distribution
            }
            
        except Exception as e:
            logger.error(f"Error calculating prediction confidence: {e}")
            return {
                'overall': 0.0,
                'top_prediction': 0.0,
                'distribution': 'poor'
            }

    def _get_default_context(self) -> Dict:
        """Get default context with safe values"""
        return {
            'performance': {'precision': 0, 'recall': 0, 'f1': 0, 'accuracy': 0},
            'predictions': [],  # ✅ Always a list
            'traditional_predictions': {  # ✅ Always a dict
                'method_predictions': [],
                'method_count': 0,
                'confidence': 0.0
            },
            'selected_date': timezone.now().date(),
            'error': None,
            'data_quality': {  # ✅ Always a dict
                'quality_score': 0.0,
                'total_records': 0,
                'valid_records': 0,
                'issues': [],
                'completeness': 0.0,
                'consistency': 0.0,
                'accuracy': 0.0,
                'freshness': 0.0,
                'coverage': 0.0
            },
            'model_metadata': {  # ✅ Always a dict
                'version': 'N/A',
                'last_trained': None,
                'features': [],
                'is_trained': False
            },
            'prediction_confidence': {  # ✅ Always a dict
                'overall': 0.0,
                'top_prediction': 0.0,
                'distribution': 'poor'
            },
            'processing_time': 0,
            'from_cache': False
        }

    def _parse_and_validate_dates(self) -> Tuple[date, date]:
        """Parse and validate dates with strict logic"""
        try:
            # Get analysis date from request
            if "selected_date" in self.request.GET:
                date_str = self.request.GET["selected_date"]
                analysis_date = datetime.strptime(date_str, "%Y-%m-%d").date()
            else:
                analysis_date = timezone.now().date()

            # Validate analysis date
            if analysis_date > timezone.now().date():
                raise ValidationError("Không thể phân tích cho ngày trong tương lai")

            # ✅ LOGIC ĐÚNG: Dự đoán cho ngày tiếp theo
            prediction_date = analysis_date + timedelta(days=1)

            logger.info(
                f"Analysis date: {analysis_date}, Prediction date: {prediction_date}"
            )
            return analysis_date, prediction_date

        except ValueError as e:
            raise ValidationError(f"Định dạng ngày không hợp lệ: {e}")

    def _get_intelligent_historical_data(
        self, analysis_date: date, min_days: int = 30, max_days: int = 180
    ) -> Tuple[List, Dict]:
        """Get historical data with intelligent sizing and quality assessment"""
        try:
            # 1. Check available data
            available_data = KetQuaXoSo.objects.filter(ngay__lt=analysis_date).order_by(
                "-ngay"
            )

            total_available = available_data.count()
            if total_available < min_days:
                raise InsufficientDataError(
                    f"Cần ít nhất {min_days} ngày dữ liệu, chỉ có {total_available}"
                )

            # 2. Calculate optimal size
            optimal_size = min(max_days, max(min_days, total_available // 3))

            # 3. Get data and assess quality
            historical_data = list(available_data[:optimal_size])
            data_quality = self.data_quality.assess_data_quality(historical_data)

            if data_quality["completeness"] < 0.8:
                logger.warning(f"Low data quality: {data_quality}")

            # 4. Validate data integrity
            self.validator.validate_historical_data(historical_data)

            return historical_data, data_quality

        except Exception as e:
            logger.error(f"Error getting historical data: {e}")
            raise InsufficientDataError(f"Lỗi lấy dữ liệu lịch sử: {e}")

    def _get_or_create_predictor(
        self, analysis_date: date, historical_data: List
    ) -> EnhancedCyclePredictor:
        """Get or create predictor with intelligent model management"""
        try:
            # Check if we have a cached model
            model_version = self._get_current_model_version()
            cached_predictor = self.prediction_cache.get_cached_prediction(
                analysis_date, model_version
            )

            if cached_predictor and self._is_model_fresh(
                cached_predictor, analysis_date
            ):
                logger.info("Using cached predictor")
                return cached_predictor

            # Create new predictor
            predictor = EnhancedCyclePredictor()

            # Check if retrain is needed
            if self._should_retrain_model(predictor, analysis_date):
                logger.info("Retraining model...")
                success = predictor.retrain_with_data(historical_data)
                if not success:
                    raise ModelTrainingError("Failed to retrain model")

            # Cache the predictor
            self.prediction_cache.cache_prediction(analysis_date, model_version, predictor)

            return predictor

        except Exception as e:
            logger.error(f"Error creating predictor: {e}")
            raise ModelTrainingError(f"Lỗi tạo model dự đoán: {e}")

    def _generate_validated_predictions(
        self, historical_data: List, prediction_date: date
    ) -> Dict:
        """Generate predictions with strict validation"""
        try:
            # Ensure predictor is initialized
            if self.predictor is None:
                raise ModelTrainingError("Predictor is not initialized.")
            # Generate predictions
            raw_predictions = self.predictor.predict_for_date(
                historical_data, prediction_date
            )

            # Validate predictions format
            self.validator.validate_predictions_strict(
                raw_predictions, "EnhancedCyclePredictor"
            )

            # Normalize format
            normalized_predictions = self.validator.normalize_predictions_format(
                raw_predictions
            )

            logger.info(
                f"Generated {len(normalized_predictions)} validated predictions"
            )
            return normalized_predictions

        except Exception as e:
            logger.error(f"Error generating predictions: {e}")
            # Return fallback predictions
            return self._get_fallback_predictions()

    def _get_traditional_predictions(
        self, historical_data: List, prediction_date: date
    ) -> Dict:
        """Get traditional predictions for comparison"""
        try:
            

            traditional_predictor = AdvancedLotteryPredictor()
            predictions = traditional_predictor.predict_next_day(historical_data)

            return {
                "method_predictions": (
                    predictions.to_dict("records")
                    if hasattr(predictions, "to_dict")
                    else []
                ),
                "confidence": 0.6,
                "method_count": len(predictions) if predictions is not None else 0,
            }

        except Exception as e:
            logger.warning(f"Traditional predictions failed: {e}")
            return {"method_predictions": [], "confidence": 0, "method_count": 0}

    def _intelligent_prediction_combination(
        self,
        ml_predictions: Dict,
        traditional_predictions: Dict,
        historical_performance: Dict,
    ) -> Dict:
        """Intelligently combine predictions with dynamic weighting"""
        try:
            combined_scores = defaultdict(float)

            # Dynamic weights based on historical performance
            ml_weight = historical_performance.get("ml_accuracy", 0.4)
            traditional_weight = 1 - ml_weight

            # Process ML predictions
            for number, confidence in ml_predictions.items():
                self.validator.validate_number_format(number)
                combined_scores[number] += confidence * ml_weight

            # Process traditional predictions
            for method_pred in traditional_predictions.get("method_predictions", []):
                numbers = method_pred.get("numbers", [])
                method_confidence = method_pred.get("confidence", 0.5)

                for number in numbers:
                    validated_number = self.validator.normalize_number_format(number)
                    if validated_number:
                        combined_scores[validated_number] += (
                            method_confidence * traditional_weight
                        )

            # Sort and format results
            sorted_predictions = sorted(
                combined_scores.items(), key=lambda x: x[1], reverse=True
            )[:20]

            return dict(sorted_predictions)

        except Exception as e:
            logger.error(f"Error combining predictions: {e}")
            return ml_predictions  # Fallback to ML only

    def _evaluate_and_improve_model(
        self, predictions: Dict, actual_result: Any, analysis_date: date
    ) -> Dict:
        """Evaluate predictions and improve model"""
        try:
            # Extract actual numbers
            actual_numbers = actual_result.get_all_2digit_numbers()

            # Calculate performance metrics
            performance = self.performance_tracker.calculate_performance(
                predictions, actual_numbers
            )

            # Record performance
            model_id = self.predictor.get_model_id() if self.predictor else "default_model"
            self.performance_tracker.record_performance(
                model_id=model_id,
                date=analysis_date,
                performance=performance,
            )

            # Check if retrain is needed
            if performance["accuracy"] < 0.15:
                logger.warning(f"Low performance: {performance['accuracy']:.2%}")
                self._schedule_retrain(analysis_date)

            # Update model weights based on feedback
            if self.predictor and hasattr(self.predictor, 'update_weights_from_feedback'):
                self.predictor.update_weights_from_feedback(predictions, actual_numbers)

            return performance

        except Exception as e:
            logger.error(f"Error evaluating model: {e}")
            return {"accuracy": 0, "precision": 0, "recall": 0, "f1": 0}


    def _handle_validation_error(self, error: ValidationError) -> Dict:
        """Handle validation errors"""
        logger.error(f"Validation error: {error}")
        messages.error(self.request, f"Lỗi validation: {error}")
        return {
            "error": True,
            "error_type": "validation",
            "error_message": str(error),
            "suggestions": [
                "Kiểm tra định dạng ngày (YYYY-MM-DD)",
                "Đảm bảo ngày phân tích không vượt quá hiện tại",
            ],
        }

    def _handle_data_error(self, error: InsufficientDataError) -> Dict:
        """Handle data errors"""
        logger.error(f"Data error: {error}")
        messages.error(self.request, f"Lỗi dữ liệu: {error}")
        return {
            "error": True,
            "error_type": "data",
            "error_message": str(error),
            "suggestions": [
                "Chọn ngày gần đây hơn có nhiều dữ liệu lịch sử",
                "Kiểm tra kết nối cơ sở dữ liệu",
                "Đảm bảo dữ liệu đã được crawler đầy đủ",
            ],
        }

    def _handle_model_error(self, error: ModelTrainingError) -> Dict:
        """Handle model training errors"""
        logger.error(f"Model error: {error}")
        messages.error(self.request, f"Lỗi model: {error}")
        return {
            "error": True,
            "error_type": "model",
            "error_message": str(error),
            "suggestions": [
                "Thử lại sau vài phút",
                "Kiểm tra tài nguyên hệ thống",
                "Liên hệ quản trị viên nếu vấn đề tiếp tục",
            ],
        }

    def _handle_unexpected_error(self, error: Exception) -> Dict:
        """Handle unexpected errors"""
        logger.error(f"Unexpected error: {error}", exc_info=True)
        messages.error(self.request, "Đã xảy ra lỗi hệ thống không mong muốn")
        return {
            "error": True,
            "error_type": "system",
            "error_message": "Lỗi hệ thống không mong muốn",
            "suggestions": [
                "Thử lại sau",
                "Liên hệ hỗ trợ kỹ thuật",
                "Kiểm tra kết nối mạng",
            ],
        }

    # Helper methods
    def _get_current_model_version(self) -> str:
        """Get current model version"""
        return "v2.1.0"

    def _is_model_fresh(self, model: Any, analysis_date: date) -> bool:
        """Check if model is fresh enough to use"""
        if not hasattr(model, "last_trained"):
            return False

        days_old = (analysis_date - model.last_trained).days
        return days_old < 7  # Model valid for 7 days

    def _should_retrain_model(
        self, predictor: Any, analysis_date: date
    ) -> bool:
        """Check if model should be retrained"""
        recent_performance = self.performance_tracker.get_recent_performance()
        return recent_performance.get("accuracy", 1.0) < 0.15

    def _schedule_retrain(self, analysis_date: date):
        """Schedule model retraining"""
        # This could trigger a background task
        logger.info(f"Scheduled retrain for {analysis_date}")

    def _get_fallback_predictions(self) -> Dict:
        """Get fallback predictions when primary method fails"""
        # Simple frequency-based fallback
        return {f"{i:02d}": 0.5 for i in range(10)}

    def _format_predictions_for_display(self, predictions: Dict, actual_result: Optional[Dict] = None) -> List[Dict]:
        """
        Format predictions for template display with hit detection
        
        Args:
            predictions: Dict of {number: confidence}
            actual_result: Dict with actual winning numbers
            
        Returns:
            List[Dict]: Formatted predictions with hit status
        """
        formatted = []
        
        # Get actual winning numbers for comparison
        winning_numbers = []
        if actual_result and actual_result.get('all_numbers'):
            winning_numbers = actual_result['all_numbers']
        
        for i, (number, confidence) in enumerate(predictions.items()):
            # Check if this prediction hit any winning number
            is_hit = number in winning_numbers
            is_special_hit = actual_result and number == actual_result.get('giai_db')
            
            formatted.append({
                "rank": i + 1,
                "number": number,
                "confidence": round(confidence * 100, 1),
                "confidence_level": self._get_confidence_level(confidence),
                "is_hit": is_hit,  # ✅ Trúng bất kỳ giải nào
                "is_special_hit": is_special_hit,  # ✅ Trúng giải đặc biệt
                "hit_type": "special" if is_special_hit else ("normal" if is_hit else "miss")
            })
        
        logger.debug(f"Formatted {len(formatted)} predictions, {sum(1 for p in formatted if p['is_hit'])} hits")
        return formatted


    def _get_confidence_level(self, confidence: float) -> str:
        """Get confidence level description"""
        if confidence >= 0.8:
            return "high"
        elif confidence >= 0.6:
            return "medium"
        elif confidence >= 0.4:
            return "low"
        else:
            return "very_low"

    def _calculate_prediction_confidence(self, predictions: Dict) -> Dict:
        """Calculate overall prediction confidence"""
        if not predictions:
            return {"overall": 0, "distribution": "poor"}

        confidences = list(predictions.values())
        overall = sum(confidences) / len(confidences)

        return {
            "overall": round(overall * 100, 1),
            "top_prediction": round(max(confidences) * 100, 1),
            "distribution": (
                "good" if overall > 0.6 else "fair" if overall > 0.4 else "poor"
            ),
        }

    def _get_actual_result_safe(self, prediction_date: date) -> Optional[Dict]:
        """
        Safely get actual result with proper format for template
        
        Returns:
            Dict: {
                "giai_db": str,
                "all_numbers": List[str],  # Tất cả số 2 chữ số để so sánh
                "raw_result": KetQuaXoSo object or None
            }
        """
        try:
            result_obj = KetQuaXoSo.objects.filter(ngay=prediction_date).first()
            
            if not result_obj:
                logger.warning(f"No actual result found for {prediction_date}")
                return None
            
            # Extract all 2-digit numbers for comparison
            all_2digit_numbers = result_obj.get_all_2digit_numbers()
            
            formatted_result = {
                'giai_db': result_obj.giai_db,  # Giải đặc biệt
                'all_numbers': all_2digit_numbers,  # Tất cả số 2 chữ số
                'raw_result': result_obj,  # Object gốc nếu cần
                'ngay': prediction_date.isoformat()
            }
            
            logger.info(f"Found actual result for {prediction_date}: ĐB={result_obj.giai_db}, total_numbers={len(all_2digit_numbers)}")
            return formatted_result
            
        except Exception as e:
            logger.warning(f"Error getting actual result: {e}")
            return None


    def _cache_result_safely(self, analysis_date: date, context: Dict):
        """Safely cache result"""
        try:
            if not context.get("error"):
                self.prediction_cache.cache_prediction(
                    analysis_date, self._get_current_model_version(), context
                )
        except Exception as e:
            logger.warning(f"Failed to cache result: {e}")


# API endpoint for AJAX requests
class EnhancedPredictAPIView(EnhancedPredictView):
    """API version that returns JSON"""

    def get(self, request, *args, **kwargs):
        """Return JSON response"""
        context = self.get_context_data(**kwargs)

        # Serialize context for JSON
        json_context = self._serialize_context(context)

        return JsonResponse(
            {
                "success": not context.get("error", False),
                "data": json_context,
                "timestamp": datetime.now().isoformat(),
            }
        )

    def _serialize_context(self, context: Dict) -> Dict:
        """Serialize context for JSON response"""
        serialized = {}

        for key, value in context.items():
            if key in [
                "predictions",
                "performance",
                "data_quality",
                "prediction_confidence",
            ]:
                serialized[key] = value
            elif isinstance(value, date):
                serialized[key] = value.isoformat()
            elif isinstance(value, (int, float, str, bool, list, dict)):
                serialized[key] = value

        return serialized
