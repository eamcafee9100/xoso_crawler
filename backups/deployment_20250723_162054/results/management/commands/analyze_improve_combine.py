from django.core.management.base import BaseCommand
from datetime import datetime, timedelta
from results.models import DailyPredictionAnalysis, AccuracyTrend
from results.services.MLModelService import MLModelService
import logging
import numpy as np
from collections import defaultdict
import warnings

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Analyze prediction performance and suggest improvements with enhanced ML model integration'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--days',
            type=int,
            default=30,
            help='Number of days to analyze'
        )
        parser.add_argument(
            '--retrain',
            action='store_true',
            help='Force retrain ML models based on analysis'
        )
        parser.add_argument(
            '--export',
            action='store_true',
            help='Export analysis results to file'
        )
        parser.add_argument(
            '--fix-models',
            action='store_true',
            help='Fix ML model compatibility issues'
        )
        parser.add_argument(
            '--validate-models',
            action='store_true',
            help='Validate ML models before analysis'
        )
    
    def handle(self, *args, **options):
        days = options['days']
        retrain = options['retrain']
        export = options['export']
        fix_models = options['fix_models']
        validate_models = options['validate_models']
        
        self.stdout.write(f"Analyzing prediction performance for last {days} days...")
        
        # 0. Khởi tạo ML Service và kiểm tra trạng thái
        ml_service = self._initialize_ml_service(fix_models, validate_models)
        
        # 1. Phân tích performance tổng thể
        overall_stats = self.analyze_overall_performance(days)
        self.display_overall_stats(overall_stats)
        
        # 2. Phân tích theo phương pháp
        method_analysis = self.analyze_method_performance(days)
        self.display_method_analysis(method_analysis)
        
        # 3. Phân tích xu hướng theo thời gian
        trend_analysis = self.analyze_accuracy_trends(days)
        self.display_trend_analysis(trend_analysis)
        
        # 4. Phân tích ML models
        ml_analysis = self.analyze_ml_performance(ml_service, days)
        self.display_ml_analysis(ml_analysis)
        
        # 5. Đề xuất cải tiến
        recommendations = self.generate_recommendations(overall_stats, method_analysis, ml_analysis)
        self.display_recommendations(recommendations)
        
        # 6. Retrain models nếu cần
        if retrain or self.should_retrain(overall_stats, ml_analysis):
            self.retrain_models(ml_service)
        
        # 7. Export kết quả nếu được yêu cầu
        if export:
            self.export_analysis_results(overall_stats, method_analysis, trend_analysis, ml_analysis, recommendations)
    
    def _initialize_ml_service(self, fix_models=False, validate_models=False):
        """Khởi tạo và kiểm tra ML Service"""
        try:
            self.stdout.write("Initializing ML Service...")
            ml_service = MLModelService()
            
            # Kiểm tra tính tương thích phiên bản
            if fix_models or ml_service.check_version_compatibility():
                self.stdout.write(self.style.WARNING("Fixing ML model compatibility issues..."))
                if ml_service.fix_version_compatibility():
                    self.stdout.write(self.style.SUCCESS("✅ ML models fixed successfully"))
                else:
                    self.stdout.write(self.style.ERROR("❌ Failed to fix ML models"))
            
            # Validate models nếu được yêu cầu
            if validate_models:
                validation_result = ml_service.validate_models()
                self.stdout.write(f"Model validation: {validation_result}")
            
            # Hiển thị thông tin models
            model_info = ml_service.get_model_info()
            self.stdout.write(f"Loaded models: {model_info['loaded_models']}")
            self.stdout.write(f"Feature count: {model_info['feature_count']}")
            
            return ml_service
            
        except Exception as e:
            logger.error(f"Error initializing ML service: {e}")
            self.stdout.write(self.style.ERROR(f"Failed to initialize ML service: {e}"))
            return None
    
    def analyze_ml_performance(self, ml_service, days):
        """Phân tích performance của ML models"""
        if not ml_service:
            return None
        
        try:
            # Lấy thông tin models
            model_info = ml_service.get_model_info()
            
            # Lấy feature importance
            feature_importance = ml_service.get_feature_importance()
            
            # Lấy độ chính xác gần đây
            recent_accuracy = ml_service.get_recent_accuracy()
            
            # Lấy ngày training cuối cùng
            last_training_date = ml_service.get_last_training_date()
            
            # Tính số ngày kể từ lần training cuối
            days_since_training = None
            if last_training_date:
                days_since_training = (datetime.now().date() - last_training_date).days
            
            return {
                'model_info': model_info,
                'feature_importance': feature_importance,
                'recent_accuracy': recent_accuracy,
                'last_training_date': last_training_date,
                'days_since_training': days_since_training,
                'models_available': len(model_info.get('loaded_models', [])) > 0
            }
            
        except Exception as e:
            logger.error(f"Error analyzing ML performance: {e}")
            return {'error': str(e)}
    
    def analyze_overall_performance(self, days):
        """Phân tích performance tổng thể với cải tiến"""
        end_date = datetime.now().date()
        start_date = end_date - timedelta(days=days)
        
        analyses = DailyPredictionAnalysis.objects.filter(
            analysis_date__range=(start_date, end_date)
        ).exclude(actual_numbers__isnull=True)
        
        if not analyses:
            return None
        
        # Tính các thống kê cơ bản
        accuracies = [a.accuracy_rate for a in analyses]
        total_accuracy = sum(accuracies)
        avg_accuracy = total_accuracy / len(analyses)
        
        # Tính xu hướng với window sliding
        window_size = min(7, len(analyses) // 2)
        if len(analyses) >= window_size * 2:
            first_window = accuracies[:window_size]
            last_window = accuracies[-window_size:]
            first_avg = sum(first_window) / len(first_window)
            last_avg = sum(last_window) / len(last_window)
        else:
            mid_point = len(analyses) // 2
            first_avg = sum(accuracies[:mid_point]) / mid_point if mid_point > 0 else 0
            last_avg = sum(accuracies[mid_point:]) / (len(accuracies) - mid_point) if len(accuracies) - mid_point > 0 else 0
        
        trend_change = last_avg - first_avg
        trend = "improving" if trend_change > 2 else \
                "declining" if trend_change < -2 else "stable"
        
        # Tính các thống kê nâng cao
        std_deviation = np.std(accuracies)
        consistency_score = max(0, 100 - std_deviation)
        
        # Phân tích quartiles
        q1 = np.percentile(accuracies, 25)
        q2 = np.percentile(accuracies, 50)  # median
        q3 = np.percentile(accuracies, 75)
        
        # Đếm số ngày có performance tốt/xấu
        good_days = sum(1 for acc in accuracies if acc > avg_accuracy + std_deviation)
        bad_days = sum(1 for acc in accuracies if acc < avg_accuracy - std_deviation)
        
        return {
            'total_days': len(analyses),
            'avg_accuracy': avg_accuracy,
            'std_deviation': std_deviation,
            'consistency_score': consistency_score,
            'best_day': max(analyses, key=lambda x: x.accuracy_rate),
            'worst_day': min(analyses, key=lambda x: x.accuracy_rate),
            'trend': trend,
            'trend_change': trend_change,
            'first_window_avg': first_avg,
            'last_window_avg': last_avg,
            'quartiles': {'q1': q1, 'q2': q2, 'q3': q3},
            'good_days': good_days,
            'bad_days': bad_days,
            'stability_ratio': (len(analyses) - good_days - bad_days) / len(analyses) * 100
        }
    
    def generate_recommendations(self, overall_stats, method_analysis, ml_analysis):
        """Tạo đề xuất cải tiến với ML analysis"""
        recommendations = []
        
        # Đề xuất dựa trên overall performance
        if overall_stats:
            if overall_stats['avg_accuracy'] < 30:
                recommendations.append({
                    'type': 'critical',
                    'message': f"Độ chính xác tổng thể thấp ({overall_stats['avg_accuracy']:.1f}%). Cần xem xét lại toàn bộ phương pháp.",
                    'action': 'retrain_all',
                    'priority': 1
                })
            
            if overall_stats['stability_ratio'] < 60:
                recommendations.append({
                    'type': 'warning',
                    'message': f"Độ ổn định thấp ({overall_stats['stability_ratio']:.1f}%). Có quá nhiều ngày có performance bất thường.",
                    'action': 'improve_stability',
                    'priority': 2
                })
            
            if overall_stats['trend'] == 'declining' and overall_stats['trend_change'] < -3:
                recommendations.append({
                    'type': 'warning',
                    'message': f"Xu hướng giảm mạnh ({overall_stats['trend_change']:.1f}%). Cần can thiệp ngay.",
                    'action': 'immediate_adjustment',
                    'priority': 1
                })
        
        # Đề xuất dựa trên ML analysis
        if ml_analysis and not ml_analysis.get('error'):
            if not ml_analysis.get('models_available'):
                recommendations.append({
                    'type': 'critical',
                    'message': "Không có ML models nào được load. Hệ thống không thể dự đoán.",
                    'action': 'train_models',
                    'priority': 1
                })
            
            if ml_analysis.get('days_since_training', 0) > 7:
                recommendations.append({
                    'type': 'warning',
                    'message': f"Models đã không được training {ml_analysis['days_since_training']} ngày. Cần cập nhật.",
                    'action': 'retrain_models',
                    'priority': 2
                })
            
            if ml_analysis.get('recent_accuracy', 0) < 0.3:
                recommendations.append({
                    'type': 'warning',
                    'message': f"Độ chính xác ML models thấp ({ml_analysis['recent_accuracy']*100:.1f}%).",
                    'action': 'improve_ml_features',
                    'priority': 2
                })
        
        # Đề xuất dựa trên method analysis
        if method_analysis:
            sorted_methods = sorted(
                method_analysis.items(),
                key=lambda x: x[1]['overall_accuracy'],
                reverse=True
            )
            
            if len(sorted_methods) > 0:
                best_method = sorted_methods[0]
                worst_method = sorted_methods[-1]
                
                recommendations.append({
                    'type': 'info',
                    'message': f"Phương pháp tốt nhất: {best_method[0]} ({best_method[1]['overall_accuracy']:.1f}%)",
                    'action': 'increase_weight',
                    'priority': 3
                })
                
                if worst_method[1]['overall_accuracy'] < 20:
                    recommendations.append({
                        'type': 'warning',
                        'message': f"Phương pháp {worst_method[0]} có độ chính xác rất thấp ({worst_method[1]['overall_accuracy']:.1f}%)",
                        'action': 'reduce_weight_or_disable',
                        'priority': 2
                    })
        
        # Sắp xếp theo độ ưu tiên
        recommendations.sort(key=lambda x: x['priority'])
        
        return recommendations
    
    def should_retrain(self, overall_stats, ml_analysis):
        """Quyết định có nên retrain models hay không"""
        # Retrain nếu overall performance thấp
        if overall_stats and overall_stats['avg_accuracy'] < 25:
            return True
        
        # Retrain nếu xu hướng giảm mạnh
        if overall_stats and overall_stats['trend'] == 'declining' and overall_stats['trend_change'] < -5:
            return True
        
        # Retrain nếu ML models không khả dụng
        if ml_analysis and not ml_analysis.get('models_available'):
            return True
        
        # Retrain nếu models quá cũ
        if ml_analysis and ml_analysis.get('days_since_training', 0) > 14:
            return True
        
        return False
    
    def retrain_models(self, ml_service):
        """Retrain ML models với error handling cải tiến"""
        if not ml_service:
            self.stdout.write(self.style.ERROR("ML Service not available for retraining"))
            return False
        
        try:
            self.stdout.write("🔄 Starting ML model retraining...")
            
            # Kiểm tra và fix compatibility trước khi retrain
            if ml_service.check_version_compatibility():
                self.stdout.write("🔧 Fixing version compatibility first...")
                ml_service.fix_version_compatibility()
            
            # Tiến hành retrain
            success = ml_service.train_models(force_retrain=True)
            
            if success:
                self.stdout.write(self.style.SUCCESS("✅ Models retrained successfully"))
                
                # Validate models sau khi retrain
                validation_result = ml_service.validate_models()
                self.stdout.write(f"Post-training validation: {validation_result}")
                
                return True
            else:
                self.stdout.write(self.style.ERROR("❌ Failed to retrain models"))
                return False
                
        except Exception as e:
            logger.error(f"Error during model retraining: {e}")
            self.stdout.write(self.style.ERROR(f"Retraining failed with error: {e}"))
            return False
    
    def display_ml_analysis(self, ml_analysis):
        """Hiển thị phân tích ML models"""
        if not ml_analysis:
            self.stdout.write(self.style.WARNING("No ML analysis data available"))
            return
        
        if ml_analysis.get('error'):
            self.stdout.write(self.style.ERROR(f"ML Analysis Error: {ml_analysis['error']}"))
            return
        
        self.stdout.write(self.style.SUCCESS("\n=== PHÂN TÍCH ML MODELS ==="))
        
        # Thông tin models
        model_info = ml_analysis.get('model_info', {})
        self.stdout.write(f"Models đã load: {model_info.get('loaded_models', [])}")
        self.stdout.write(f"Số features: {model_info.get('feature_count', 0)}")
        
        # Độ chính xác
        recent_accuracy = ml_analysis.get('recent_accuracy', 0)
        accuracy_style = self.style.SUCCESS if recent_accuracy > 0.4 else \
                        self.style.WARNING if recent_accuracy > 0.25 else \
                        self.style.ERROR
        self.stdout.write(accuracy_style(f"Độ chính xác gần đây: {recent_accuracy*100:.2f}%"))
        
        # Thông tin training
        last_training = ml_analysis.get('last_training_date')
        days_since = ml_analysis.get('days_since_training', 0)
        
        if last_training:
            training_style = self.style.SUCCESS if days_since <= 7 else \
                           self.style.WARNING if days_since <= 14 else \
                           self.style.ERROR
            self.stdout.write(training_style(f"Lần training cuối: {last_training} ({days_since} ngày trước)"))
        else:
            self.stdout.write(self.style.ERROR("Chưa có thông tin training"))
        
        # Feature importance (top 5)
        feature_importance = ml_analysis.get('feature_importance', {})
        if feature_importance:
            self.stdout.write("\nTop 5 features quan trọng:")
            for model_name, features in feature_importance.items():
                sorted_features = sorted(features.items(), key=lambda x: x[1], reverse=True)[:5]
                self.stdout.write(f"  {model_name}:")
                for feature, importance in sorted_features:
                    self.stdout.write(f"    - {feature}: {importance:.4f}")
    
    def display_overall_stats(self, stats):
        """Hiển thị thống kê tổng thể với cải tiến"""
        if not stats:
            self.stdout.write(self.style.WARNING("No data available for analysis"))
            return
        
        self.stdout.write(self.style.SUCCESS("\n=== THỐNG KÊ TỔNG THỂ ==="))
        self.stdout.write(f"Số ngày phân tích: {stats['total_days']}")
        self.stdout.write(f"Độ chính xác trung bình: {stats['avg_accuracy']:.2f}%")
        self.stdout.write(f"Độ lệch chuẩn: {stats['std_deviation']:.2f}")
        self.stdout.write(f"Độ nhất quán: {stats['consistency_score']:.2f}%")
        self.stdout.write(f"Độ ổn định: {stats['stability_ratio']:.2f}%")
        self.stdout.write(f"Xu hướng: {stats['trend']} ({stats['trend_change']:+.2f}%)")
        self.stdout.write(f"Ngày tốt nhất: {stats['best_day'].analysis_date} ({stats['best_day'].accuracy_rate:.1f}%)")
        self.stdout.write(f"Ngày tệ nhất: {stats['worst_day'].analysis_date} ({stats['worst_day'].accuracy_rate:.1f}%)")
        self.stdout.write(f"Quartiles: Q1={stats['quartiles']['q1']:.1f}%, Q2={stats['quartiles']['q2']:.1f}%, Q3={stats['quartiles']['q3']:.1f}%")
        self.stdout.write(f"Ngày performance tốt: {stats['good_days']}")
        self.stdout.write(f"Ngày performance xấu: {stats['bad_days']}")
    
    # Giữ lại các method khác từ version cũ nhưng có thể cải tiến thêm
    def analyze_method_performance(self, days):
        """Phân tích performance theo phương pháp (giữ nguyên logic cũ)"""
        end_date = datetime.now().date()
        start_date = end_date - timedelta(days=days)
        
        analyses = DailyPredictionAnalysis.objects.filter(
            analysis_date__range=(start_date, end_date)
        ).exclude(actual_numbers__isnull=True)
        
        method_stats = {}
        
        for analysis in analyses:
            if not hasattr(analysis, 'method_performance') or not analysis.method_performance:
                continue
                
            for method, stats in analysis.method_performance.items():
                if method not in method_stats:
                    method_stats[method] = {
                        'total_predictions': 0,
                        'correct_predictions': 0,
                        'days_used': 0,
                        'accuracies': [],
                        'hit_days': 0,
                        'daily_hits': []
                    }
                
                method_stats[method]['total_predictions'] += stats.get('total', 0)
                method_stats[method]['correct_predictions'] += stats.get('correct', 0)
                method_stats[method]['days_used'] += 1
                
                accuracy = stats.get('accuracy', 0)
                method_stats[method]['accuracies'].append(accuracy)
                
                if stats.get('correct', 0) > 0:
                    method_stats[method]['hit_days'] += 1
                
                method_stats[method]['daily_hits'].append(stats.get('correct', 0))
        
        # Tính thống kê cuối cùng
        for method in method_stats:
            stats = method_stats[method]
            stats['overall_accuracy'] = (stats['correct_predictions'] / stats['total_predictions'] * 100) \
                                       if stats['total_predictions'] > 0 else 0
            stats['avg_daily_accuracy'] = sum(stats['accuracies']) / len(stats['accuracies']) \
                                          if stats['accuracies'] else 0
            stats['consistency'] = max(0, 100 - (np.std(stats['accuracies']) if len(stats['accuracies']) > 1 else 0))
            stats['hit_rate'] = (stats['hit_days'] / stats['days_used'] * 100) \
                               if stats['days_used'] > 0 else 0
            stats['avg_daily_hits'] = sum(stats['daily_hits']) / len(stats['daily_hits']) \
                                     if stats['daily_hits'] else 0
        
        return method_stats
    
    def analyze_accuracy_trends(self, days):
        """Phân tích xu hướng độ chính xác theo thời gian (giữ nguyên)"""
        end_date = datetime.now().date()
        start_date = end_date - timedelta(days=days)
        
        trends = AccuracyTrend.objects.filter(
            date__range=(start_date, end_date)
        ).order_by('date')
        
        if not trends:
            return None
        
        weekly_trends = defaultdict(list)
        for trend in trends:
            week_key = trend.date.strftime('%Y-W%U')
            weekly_trends[week_key].append(trend.accuracy)
        
        weekly_averages = {}
        for week, accuracies in weekly_trends.items():
            weekly_averages[week] = sum(accuracies) / len(accuracies)
        
        if len(weekly_averages) >= 2:
            weeks = list(weekly_averages.keys())
            values = list(weekly_averages.values())
            x = list(range(len(values)))
            slope = np.polyfit(x, values, 1)[0]
        else:
            slope = 0
        
        return {
            'daily_trends': [(t.date, t.accuracy) for t in trends],
            'weekly_averages': weekly_averages,
            'slope': slope,
            'trend_direction': 'improving' if slope > 0.5 else 'declining' if slope < -0.5 else 'stable'
        }
    
    def display_method_analysis(self, method_analysis):
        """Hiển thị phân tích theo phương pháp (giữ nguyên)"""
        if not method_analysis:
            self.stdout.write(self.style.WARNING("No method analysis data available"))
            return
        
        self.stdout.write(self.style.SUCCESS("\n=== PHÂN TÍCH THEO PHƯƠNG PHÁP ==="))
        
        sorted_methods = sorted(
            method_analysis.items(),
            key=lambda x: x[1]['overall_accuracy'],
            reverse=True
        )
        
        for method, stats in sorted_methods:
            style = self.style.SUCCESS if stats['overall_accuracy'] > 40 else \
                   self.style.WARNING if stats['overall_accuracy'] > 25 else \
                   self.style.ERROR
            
            self.stdout.write(style(f"\n{method}:"))
            self.stdout.write(f"  Độ chính xác tổng thể: {stats['overall_accuracy']:.2f}%")
            self.stdout.write(f"  Độ chính xác hàng ngày: {stats['avg_daily_accuracy']:.2f}%")
            self.stdout.write(f"  Tính nhất quán: {stats['consistency']:.2f}%")
            self.stdout.write(f"  Tỷ lệ trúng: {stats['hit_rate']:.2f}%")
            self.stdout.write(f"  Số hits trung bình/ngày: {stats['avg_daily_hits']:.2f}")
            self.stdout.write(f"  Số ngày sử dụng: {stats['days_used']}")
    
    def display_trend_analysis(self, trend_analysis):
        """Hiển thị phân tích xu hướng (giữ nguyên)"""
        if not trend_analysis:
            self.stdout.write(self.style.WARNING("No trend analysis data available"))
            return
        
        self.stdout.write(self.style.SUCCESS("\n=== PHÂN TÍCH XU HƯỚNG ==="))
        self.stdout.write(f"Hướng xu hướng: {trend_analysis['trend_direction']}")
        self.stdout.write(f"Độ dốc xu hướng: {trend_analysis['slope']:.4f}")
        
        if trend_analysis['weekly_averages']:
            self.stdout.write("\nĐộ chính xác theo tuần:")
            for week, avg in trend_analysis['weekly_averages'].items():
                self.stdout.write(f"  {week}: {avg:.2f}%")
    
    def display_recommendations(self, recommendations):
        """Hiển thị đề xuất cải tiến (giữ nguyên)"""
        if not recommendations:
            self.stdout.write(self.style.WARNING("No recommendations generated"))
            return
        
        self.stdout.write(self.style.SUCCESS("\n=== ĐỀ XUẤT CẢI TIẾN ==="))
        
        for i, rec in enumerate(recommendations, 1):
            if rec['type'] == 'critical':
                style = self.style.ERROR
            elif rec['type'] == 'warning':
                style = self.style.WARNING
            else:
                style = self.style.SUCCESS
            
            self.stdout.write(style(f"{i}. {rec['message']}"))
            self.stdout.write(f"   Hành động: {rec['action']}")
            self.stdout.write(f"   Độ ưu tiên: {rec['priority']}")
    
    def export_analysis_results(self, overall_stats, method_analysis, trend_analysis, ml_analysis, recommendations):
        """Export kết quả phân tích ra file với ML analysis"""
        try:
            import json
            from django.conf import settings
            import os
            
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"prediction_analysis_{timestamp}.json"
            filepath = os.path.join(settings.BASE_DIR, 'exports', filename)
            
            os.makedirs(os.path.dirname(filepath), exist_ok=True)
            
            export_data = {
                'timestamp': timestamp,
                'analysis_date': datetime.now().isoformat(),
                'overall_stats': self._serialize_overall_stats(overall_stats),
                'method_analysis': method_analysis,
                'trend_analysis': self._serialize_trend_analysis(trend_analysis),
                'ml_analysis': self._serialize_ml_analysis(ml_analysis),
                'recommendations': recommendations
            }
            
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(export_data, f, ensure_ascii=False, indent=2, default=str)
            
            self.stdout.write(self.style.SUCCESS(f"Analysis results exported to: {filepath}"))
            
        except Exception as e:
            logger.error(f"Error exporting analysis results: {e}")
            self.stdout.write(self.style.ERROR(f"Failed to export results: {e}"))
    
    def _serialize_overall_stats(self, stats):
        """Serialize overall stats để có thể JSON"""
        if not stats:
            return None
        
        serialized = stats.copy()
        if 'best_day' in serialized:
            serialized['best_day'] = {
                'date': serialized['best_day'].analysis_date,
                'accuracy': serialized['best_day'].accuracy_rate
            }
        if 'worst_day' in serialized:
            serialized['worst_day'] = {
                'date': serialized['worst_day'].analysis_date,
                'accuracy': serialized['worst_day'].accuracy_rate
            }
        
        return serialized
    
    def _serialize_trend_analysis(self, trend_analysis):
        """Serialize trend analysis để có thể JSON"""
        if not trend_analysis:
            return None
        
        serialized = trend_analysis.copy()
        if 'daily_trends' in serialized:
            serialized['daily_trends'] = [
                {'date': date, 'accuracy': accuracy}
                for date, accuracy in serialized['daily_trends']
            ]
        
        return serialized
    
    def _serialize_ml_analysis(self, ml_analysis):
        """Serialize ML analysis để có thể JSON"""
        if not ml_analysis:
            return None
        
        serialized = ml_analysis.copy()
        # Convert date objects to strings
        if 'last_training_date' in serialized and serialized['last_training_date']:
            serialized['last_training_date'] = serialized['last_training_date'].isoformat()
        
        return serialized