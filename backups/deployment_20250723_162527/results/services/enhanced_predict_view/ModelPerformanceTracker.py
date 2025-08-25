import logging
from datetime import datetime, timedelta, date
from typing import Dict, List, Any, Optional
from collections import defaultdict
from django.db import transaction
from django.utils import timezone

from results.models import (
    ModelTrainingHistory, PredictionPerformanceMetrics, 
    PredictionRecord, CycleAccuracy
)

logger = logging.getLogger(__name__)

class ModelPerformanceTracker:
    """
    Service để theo dõi và cải thiện hiệu suất model
    
    Returns:
        Tất cả methods trả về Dict với cấu trúc rõ ràng:
        - calculate_performance: {"accuracy": float, "precision": float, "recall": float, "f1": float}
        - get_recent_performance: {"ml_accuracy": float, "traditional_accuracy": float, "trend": str}
        - record_performance: {"success": bool, "message": str}
    """
    
    def __init__(self):
        self.performance_cache = {}
        self.cache_duration = timedelta(hours=1)
    
    def calculate_performance(self, predictions: Dict[str, float], 
                            actual_numbers: List[str]) -> Dict:
        """
        Tính toán performance metrics chi tiết
        
        Args:
            predictions: Dict mapping số dự đoán -> confidence score
            actual_numbers: List số thực tế xuất hiện
            
        Returns:
            Dict: {
                "accuracy": float,      # Accuracy score (0-1)
                "precision": float,     # Precision score (0-1) 
                "recall": float,        # Recall score (0-1)
                "f1": float,           # F1 score (0-1)
                "hit_rate": float,     # Hit rate (0-1)
                "total_predictions": int,  # Tổng số dự đoán
                "total_hits": int,     # Số dự đoán đúng
                "hit_numbers": List[str],  # Danh sách số trúng
                "miss_numbers": List[str], # Danh sách số miss
                "confidence_stats": Dict   # Thống kê confidence
            }
        """
        try:
            if not predictions:
                return self._get_empty_performance()
            
            predicted_numbers = list(predictions.keys())
            actual_set = set(actual_numbers)
            predicted_set = set(predicted_numbers)
            
            # Tính hit và miss
            hit_numbers = list(predicted_set & actual_set)
            miss_numbers = list(predicted_set - actual_set)
            
            total_predictions = len(predicted_numbers)
            total_hits = len(hit_numbers)
            total_actual = len(actual_numbers)
            
            # Tính metrics cơ bản
            precision = total_hits / total_predictions if total_predictions > 0 else 0
            recall = total_hits / total_actual if total_actual > 0 else 0
            hit_rate = precision  # Hit rate = precision
            
            # F1 score
            if precision + recall > 0:
                f1 = 2 * (precision * recall) / (precision + recall)
            else:
                f1 = 0
            
            # Accuracy (trong context xổ số = recall)
            accuracy = recall
            
            # Confidence statistics
            confidence_stats = self._calculate_confidence_stats(predictions, hit_numbers)
            
            performance_metrics = {
                'accuracy': round(accuracy, 4),
                'precision': round(precision, 4),
                'recall': round(recall, 4),
                'f1': round(f1, 4),
                'hit_rate': round(hit_rate, 4),
                'total_predictions': total_predictions,
                'total_hits': total_hits,
                'total_actual': total_actual,
                'hit_numbers': hit_numbers,
                'miss_numbers': miss_numbers,
                'confidence_stats': confidence_stats,
                'performance_level': self._get_performance_level(f1)
            }
            
            logger.info(f"Performance calculated: Acc={accuracy:.2%}, F1={f1:.2%}, Hits={total_hits}/{total_predictions}")
            return performance_metrics
            
        except Exception as e:
            logger.error(f"Error calculating performance: {e}")
            return self._get_empty_performance()
    
    def record_performance(self, model_id: str, date: date, 
                         performance: Dict) -> Dict:
        """
        Lưu performance vào database với đầy đủ chi tiết
        
        Args:
            model_id: ID của model
            date: Ngày dự đoán
            performance: Dict performance metrics
            
        Returns:
            Dict: {"success": bool, "message": str, "record_id": Optional[int]}
        """
        try:
            with transaction.atomic():
                # 1. Tìm hoặc tạo ModelTrainingHistory
                model_training, created = ModelTrainingHistory.objects.get_or_create(
                    model_id=model_id,
                    defaults={
                        'model_type': 'enhanced_cycle',
                        'version': '2.1.0',
                        'training_date': timezone.now(),
                        'data_size': 0,
                        'status': 'completed'
                    }
                )
                
                if created:
                    logger.info(f"Created new ModelTrainingHistory for {model_id}")
                
                # 2. Tạo hoặc cập nhật PredictionPerformanceMetrics
                performance_metric, created = PredictionPerformanceMetrics.objects.update_or_create(
                    model_training=model_training,
                    prediction_date=date,
                    defaults={
                        'analysis_date': date - timedelta(days=1),
                        'accuracy': performance.get('accuracy', 0),
                        'precision': performance.get('precision', 0),
                        'recall': performance.get('recall', 0),
                        'f1_score': performance.get('f1', 0),
                        'total_hits': performance.get('total_hits', 0),
                        'total_misses': performance.get('total_predictions', 0) - performance.get('total_hits', 0),
                        'hit_rate': performance.get('hit_rate', 0),
                        'avg_confidence': performance.get('confidence_stats', {}).get('average', 0),
                        'top_prediction_confidence': performance.get('confidence_stats', {}).get('max', 0),
                        'predicted_numbers': performance.get('hit_numbers', []) + performance.get('miss_numbers', []),
                        'actual_numbers': [],  # Will be updated when actual results available
                        'hit_numbers': performance.get('hit_numbers', []),
                        'miss_numbers': performance.get('miss_numbers', []),
                        'prediction_count': performance.get('total_predictions', 0),
                        'confidence_distribution': performance.get('confidence_stats', {}).get('distribution', {}),
                        'processing_time': performance.get('processing_time', 0),
                        'data_quality_score': performance.get('data_quality_score', 0)
                    }
                )
                
                # 3. Cập nhật ModelTrainingHistory stats
                model_training.update_performance(
                    is_successful=performance.get('f1', 0) > 0.1
                )
                
                # 4. Tạo PredictionRecord cho từng số dự đoán
                self._create_prediction_records(performance_metric, performance)
                
                # 5. Cập nhật CycleAccuracy
                self._update_cycle_accuracy(date, performance)
                
                # 6. Clear cache
                self._clear_performance_cache()
                
                logger.info(f"Performance recorded successfully for {model_id} on {date}")
                return {
                    'success': True,
                    'message': 'Performance recorded successfully',
                    'record_id': performance_metric.id
                }
                
        except Exception as e:
            logger.error(f"Error recording performance: {e}")
            return {
                'success': False,
                'message': f'Error recording performance: {e}',
                'record_id': None
            }
    
    def get_recent_performance(self, days: int = 30) -> Dict:
        """
        Lấy performance gần đây để điều chỉnh weights
        
        Args:
            days: Số ngày gần đây cần lấy
            
        Returns:
            Dict: {
                "ml_accuracy": float,        # Accuracy của ML models
                "traditional_accuracy": float, # Accuracy của traditional methods  
                "trend": str,                # Xu hướng: "improving", "declining", "stable"
                "best_model": str,           # Model tốt nhất
                "performance_history": List[Dict], # Lịch sử performance
                "recommendation": str        # Khuyến nghị
            }
        """
        try:
            # Check cache first
            cache_key = f"recent_performance_{days}"
            if cache_key in self.performance_cache:
                cache_entry = self.performance_cache[cache_key]
                if datetime.now() - cache_entry['timestamp'] < self.cache_duration:
                    return cache_entry['data']
            
            cutoff_date = timezone.now().date() - timedelta(days=days)
            
            # Lấy performance metrics gần đây
            recent_metrics = PredictionPerformanceMetrics.objects.filter(
                prediction_date__gte=cutoff_date
            ).select_related('model_training').order_by('-prediction_date')
            
            if not recent_metrics.exists():
                return self._get_default_performance()
            
            # Phân tích theo model type
            ml_performances = []
            traditional_performances = []
            all_performances = []
            
            for metric in recent_metrics:
                performance_data = {
                    'date': metric.prediction_date,
                    'accuracy': metric.accuracy,
                    'f1_score': metric.f1_score,
                    'model_type': metric.model_training.model_type,
                    'model_id': metric.model_training.model_id
                }
                
                all_performances.append(performance_data)
                
                if metric.model_training.model_type in ['enhanced_cycle', 'ensemble', 'neural_network']:
                    ml_performances.append(metric.accuracy)
                else:
                    traditional_performances.append(metric.accuracy)
            
            # Tính average performance
            ml_accuracy = sum(ml_performances) / len(ml_performances) if ml_performances else 0.4
            traditional_accuracy = sum(traditional_performances) / len(traditional_performances) if traditional_performances else 0.3
            
            # Phân tích trend
            trend_analysis = self._analyze_trend(all_performances)
            
            # Tìm model tốt nhất
            best_model = self._find_best_model(recent_metrics)
            
            # Tạo khuyến nghị
            recommendation = self._generate_performance_recommendation(
                ml_accuracy, traditional_accuracy, trend_analysis
            )
            
            performance_data = {
                'ml_accuracy': round(ml_accuracy, 4),
                'traditional_accuracy': round(traditional_accuracy, 4),
                'trend': trend_analysis['trend'],
                'trend_details': trend_analysis,
                'best_model': best_model,
                'performance_history': all_performances[:10],  # Latest 10
                'recommendation': recommendation,
                'total_records': len(all_performances),
                'analysis_period_days': days
            }
            
            # Cache result
            self.performance_cache[cache_key] = {
                'data': performance_data,
                'timestamp': datetime.now()
            }
            
            logger.info(f"Recent performance analyzed: ML={ml_accuracy:.2%}, Traditional={traditional_accuracy:.2%}, Trend={trend_analysis['trend']}")
            return performance_data
            
        except Exception as e:
            logger.error(f"Error getting recent performance: {e}")
            return self._get_default_performance()
    
    def get_model_comparison(self, days: int = 30) -> Dict:
        """
        So sánh performance giữa các models
        
        Returns:
            Dict: {
                "model_rankings": List[Dict],  # Ranking các models
                "best_performer": Dict,        # Model tốt nhất
                "improvement_suggestions": List[str] # Gợi ý cải thiện
            }
        """
        try:
            cutoff_date = timezone.now().date() - timedelta(days=days)
            
            # Group performance by model
            model_performances = defaultdict(list)
            
            metrics = PredictionPerformanceMetrics.objects.filter(
                prediction_date__gte=cutoff_date
            ).select_related('model_training')
            
            for metric in metrics:
                model_key = f"{metric.model_training.model_type}_v{metric.model_training.version}"
                model_performances[model_key].append({
                    'accuracy': metric.accuracy,
                    'f1_score': metric.f1_score,
                    'precision': metric.precision,
                    'recall': metric.recall,
                    'date': metric.prediction_date
                })
            
            # Calculate averages and rankings
            model_rankings = []
            
            for model_key, performances in model_performances.items():
                if not performances:
                    continue
                
                avg_accuracy = sum(p['accuracy'] for p in performances) / len(performances)
                avg_f1 = sum(p['f1_score'] for p in performances) / len(performances)
                avg_precision = sum(p['precision'] for p in performances) / len(performances)
                avg_recall = sum(p['recall'] for p in performances) / len(performances)
                
                model_rankings.append({
                    'model': model_key,
                    'avg_accuracy': round(avg_accuracy, 4),
                    'avg_f1': round(avg_f1, 4),
                    'avg_precision': round(avg_precision, 4),
                    'avg_recall': round(avg_recall, 4),
                    'prediction_count': len(performances),
                    'latest_performance': performances[-1] if performances else None
                })
            
            # Sort by F1 score
            model_rankings.sort(key=lambda x: x['avg_f1'], reverse=True)
            
            best_performer = model_rankings[0] if model_rankings else None
            
            # Generate improvement suggestions
            suggestions = self._generate_improvement_suggestions(model_rankings)
            
            return {
                'model_rankings': model_rankings,
                'best_performer': best_performer,
                'improvement_suggestions': suggestions,
                'analysis_period': days,
                'total_models': len(model_rankings)
            }
            
        except Exception as e:
            logger.error(f"Error in model comparison: {e}")
            return {
                'model_rankings': [],
                'best_performer': None,
                'improvement_suggestions': ['Lỗi phân tích model comparison'],
                'analysis_period': days,
                'total_models': 0
            }
    
    # Helper methods
    def _calculate_confidence_stats(self, predictions: Dict[str, float], 
                                  hit_numbers: List[str]) -> Dict:
        """Tính thống kê confidence"""
        try:
            confidences = list(predictions.values())
            hit_confidences = [predictions[num] for num in hit_numbers if num in predictions]
            
            return {
                'average': round(sum(confidences) / len(confidences), 4) if confidences else 0,
                'max': round(max(confidences), 4) if confidences else 0,
                'min': round(min(confidences), 4) if confidences else 0,
                'hit_average': round(sum(hit_confidences) / len(hit_confidences), 4) if hit_confidences else 0,
                'distribution': {
                    'high': len([c for c in confidences if c >= 0.8]),
                    'medium': len([c for c in confidences if 0.6 <= c < 0.8]),
                    'low': len([c for c in confidences if 0.4 <= c < 0.6]),
                    'very_low': len([c for c in confidences if c < 0.4])
                }
            }
        except Exception:
            return {'average': 0, 'max': 0, 'min': 0, 'hit_average': 0, 'distribution': {}}
    
    def _create_prediction_records(self, performance_metric: Any, performance: Dict):
        """Tạo PredictionRecord cho từng dự đoán"""
        try:
            # Combine hit and miss numbers with their details
            hit_numbers = performance.get('hit_numbers', [])
            miss_numbers = performance.get('miss_numbers', [])
            
            # Create records for hits
            for i, number in enumerate(hit_numbers):
                PredictionRecord.objects.create(
                    model_training=performance_metric.model_training,
                    performance_metric=performance_metric,
                    prediction_type='ml',
                    prediction_date=performance_metric.prediction_date,
                    analysis_date=performance_metric.analysis_date,
                    predicted_number=number,
                    confidence_score=performance.get('confidence_stats', {}).get('hit_average', 0.5),
                    rank_position=i + 1,
                    is_hit=True,
                    actual_result_available=True
                )
            
            # Create records for misses
            for i, number in enumerate(miss_numbers):
                PredictionRecord.objects.create(
                    model_training=performance_metric.model_training,
                    performance_metric=performance_metric,
                    prediction_type='ml',
                    prediction_date=performance_metric.prediction_date,
                    analysis_date=performance_metric.analysis_date,
                    predicted_number=number,
                    confidence_score=performance.get('confidence_stats', {}).get('average', 0.5),
                    rank_position=len(hit_numbers) + i + 1,
                    is_hit=False,
                    actual_result_available=True
                )
                
        except Exception as e:
            logger.error(f"Error creating prediction records: {e}")
    
    def _update_cycle_accuracy(self, date: date, performance: Dict):
        """Cập nhật CycleAccuracy"""
        try:
            CycleAccuracy.objects.update_or_create(
                date=date,
                defaults={
                    'precision': performance.get('precision', 0),
                    'recall': performance.get('recall', 0),
                    'f1_score': performance.get('f1', 0),
                    'accuracy': performance.get('accuracy', 0),
                    'total_predictions': performance.get('total_predictions', 0),
                    'correct_predictions': performance.get('total_hits', 0),
                    'model_version': '2.1.0',
                    'confidence_stats': performance.get('confidence_stats', {}),
                    'processing_time': performance.get('processing_time', 0)
                }
            )
        except Exception as e:
            logger.error(f"Error updating cycle accuracy: {e}")
    
    def _analyze_trend(self, performances: List[Dict]) -> Dict:
        """Phân tích xu hướng performance"""
        try:
            if len(performances) < 3:
                return {'trend': 'insufficient_data', 'slope': 0, 'confidence': 0}
            
            # Sort by date
            sorted_perfs = sorted(performances, key=lambda x: x['date'])
            
            # Calculate trend using simple linear regression on F1 scores
            x_values = list(range(len(sorted_perfs)))
            y_values = [p['f1_score'] for p in sorted_perfs]
            
            n = len(x_values)
            sum_x = sum(x_values)
            sum_y = sum(y_values)
            sum_xy = sum(x * y for x, y in zip(x_values, y_values))
            sum_x2 = sum(x * x for x in x_values)
            
            # Slope calculation
            if n * sum_x2 - sum_x * sum_x != 0:
                slope = (n * sum_xy - sum_x * sum_y) / (n * sum_x2 - sum_x * sum_x)
            else:
                slope = 0
            
            # Determine trend
            if slope > 0.01:
                trend = 'improving'
            elif slope < -0.01:
                trend = 'declining'
            else:
                trend = 'stable'
            
            # Calculate confidence in trend
            recent_avg = sum(y_values[-5:]) / min(5, len(y_values))
            overall_avg = sum(y_values) / len(y_values)
            confidence = abs(recent_avg - overall_avg)
            
            return {
                'trend': trend,
                'slope': round(slope, 4),
                'confidence': round(confidence, 4),
                'recent_average': round(recent_avg, 4),
                'overall_average': round(overall_avg, 4)
            }
            
        except Exception as e:
            logger.error(f"Error analyzing trend: {e}")
            return {'trend': 'unknown', 'slope': 0, 'confidence': 0}
    
    def _find_best_model(self, metrics) -> Dict:
        """Tìm model tốt nhất"""
        try:
            best_metric = max(metrics, key=lambda x: x.f1_score)
            return {
                'model_id': best_metric.model_training.model_id,
                'model_type': best_metric.model_training.model_type,
                'version': best_metric.model_training.version,
                'f1_score': best_metric.f1_score,
                'accuracy': best_metric.accuracy,
                'date': best_metric.prediction_date.isoformat()
            }
        except Exception:
            return {'model_id': 'unknown', 'model_type': 'unknown', 'f1_score': 0}
    
    def _generate_performance_recommendation(self, ml_acc: float, trad_acc: float, trend: Dict) -> str:
        """Tạo khuyến nghị dựa trên performance"""
        try:
            if ml_acc > trad_acc * 1.2:
                base_rec = "Ưu tiên sử dụng ML models"
            elif trad_acc > ml_acc * 1.2:
                base_rec = "Ưu tiên traditional methods"
            else:
                base_rec = "Sử dụng ensemble approach"
            
            if trend['trend'] == 'declining':
                base_rec += ", cần retrain models"
            elif trend['trend'] == 'improving':
                base_rec += ", tiếp tục strategy hiện tại"
            
            return base_rec
            
        except Exception:
            return "Cần thêm dữ liệu để đưa ra khuyến nghị"
    
    def _generate_improvement_suggestions(self, model_rankings: List[Dict]) -> List[str]:
        """Tạo gợi ý cải thiện"""
        suggestions = []
        
        try:
            if not model_rankings:
                return ["Không có dữ liệu để phân tích"]
            
            best_model = model_rankings[0]
            
            if best_model['avg_f1'] < 0.2:
                suggestions.append("Tất cả models có hiệu suất thấp, cần retrain toàn bộ")
            elif best_model['avg_f1'] < 0.5:
                suggestions.append("Models cần cải thiện, thử ensemble approach")
            
            # Check for model diversity
            unique_types = len(set(m['model'].split('_')[0] for m in model_rankings))
            if unique_types < 2:
                suggestions.append("Nên thử thêm các loại model khác")
            
            # Check prediction frequency
            low_usage_models = [m for m in model_rankings if m['prediction_count'] < 5]
            if len(low_usage_models) > len(model_rankings) // 2:
                suggestions.append("Một số models ít được sử dụng, cần review strategy")
            
            if not suggestions:
                suggestions.append("Performance tốt, tiếp tục monitoring")
                
        except Exception as e:
            suggestions.append(f"Lỗi tạo suggestions: {e}")
        
        return suggestions
    
    def _get_performance_level(self, f1_score: float) -> str:
        """Get performance level description"""
        if f1_score >= 0.8:
            return 'excellent'
        elif f1_score >= 0.6:
            return 'good'
        elif f1_score >= 0.4:
            return 'fair'
        elif f1_score >= 0.2:
            return 'poor'
        else:
            return 'very_poor'
    
    def _clear_performance_cache(self):
        """Clear performance cache"""
        self.performance_cache.clear()
    
    def _get_empty_performance(self) -> Dict:
        """Get empty performance metrics"""
        return {
            'accuracy': 0.0,
            'precision': 0.0,
            'recall': 0.0,
            'f1': 0.0,
            'hit_rate': 0.0,
            'total_predictions': 0,
            'total_hits': 0,
            'total_actual': 0,
            'hit_numbers': [],
            'miss_numbers': [],
            'confidence_stats': {},
            'performance_level': 'very_poor'
        }
    
    def _get_default_performance(self) -> Dict:
        """Get default performance when no data"""
        return {
            'ml_accuracy': 0.4,
            'traditional_accuracy': 0.3,
            'trend': 'insufficient_data',
            'trend_details': {'trend': 'insufficient_data', 'slope': 0},
            'best_model': {'model_id': 'unknown', 'model_type': 'unknown', 'f1_score': 0},
            'performance_history': [],
            'recommendation': 'Cần tích lũy thêm dữ liệu performance',
            'total_records': 0,
            'analysis_period_days': 30
        }