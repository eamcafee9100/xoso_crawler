from django.core.management.base import BaseCommand
from datetime import datetime, timedelta
from results.models import DailyPredictionAnalysis, AccuracyTrend
from results.services.MLModelService import MLModelService
import logging
import numpy as np

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Simple prediction performance analysis with ML model focus'
    
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
            '--quick',
            action='store_true',
            help='Quick analysis mode (basic stats only)'
        )
    
    def handle(self, *args, **options):
        days = options['days']
        retrain = options['retrain']
        quick = options['quick']
        
        self.stdout.write(f"Analyzing prediction performance for last {days} days...")
        
        # 1. Khởi tạo ML Service
        ml_service = self._setup_ml_service()
        
        # 2. Phân tích cơ bản
        if quick:
            self._quick_analysis(days, ml_service)
        else:
            self._full_analysis(days, ml_service)
        
        # 3. Retrain nếu cần
        if retrain:
            self._handle_retrain(ml_service)
    
    def _setup_ml_service(self):
        """Thiết lập ML Service với error handling"""
        try:
            ml_service = MLModelService()
            
            # Kiểm tra trạng thái models
            model_info = ml_service.get_model_info()
            loaded_models = len(model_info.get('loaded_models', []))
            
            if loaded_models == 0:
                self.stdout.write(self.style.WARNING("⚠️  No ML models loaded"))
                
                # Thử fix compatibility
                if ml_service.check_version_compatibility():
                    self.stdout.write("🔧 Fixing model compatibility...")
                    ml_service.fix_version_compatibility()
            else:
                self.stdout.write(self.style.SUCCESS(f"✅ {loaded_models} ML models loaded"))
            
            return ml_service
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"❌ Failed to setup ML service: {e}"))
            return None
    
    def _quick_analysis(self, days, ml_service):
        """Phân tích nhanh"""
        self.stdout.write(self.style.SUCCESS("\n=== QUICK ANALYSIS ==="))
        
        # Lấy dữ liệu cơ bản
        end_date = datetime.now().date()
        start_date = end_date - timedelta(days=days)
        
        analyses = DailyPredictionAnalysis.objects.filter(
            analysis_date__range=(start_date, end_date)
        ).exclude(actual_numbers__isnull=True)
        
        if not analyses:
            self.stdout.write(self.style.WARNING("No analysis data available"))
            return
        
        # Thống kê cơ bản
        total_days = len(analyses)
        accuracies = [a.accuracy_rate for a in analyses]
        avg_accuracy = sum(accuracies) / len(accuracies)
        
        self.stdout.write(f"📊 Analyzed {total_days} days")
        self.stdout.write(f"🎯 Average accuracy: {avg_accuracy:.2f}%")
        
        # Best/worst days
        best_day = max(analyses, key=lambda x: x.accuracy_rate)
        worst_day = min(analyses, key=lambda x: x.accuracy_rate)
        
        self.stdout.write(f"⬆️  Best day: {best_day.analysis_date} ({best_day.accuracy_rate:.1f}%)")
        self.stdout.write(f"⬇️  Worst day: {worst_day.analysis_date} ({worst_day.accuracy_rate:.1f}%)")
        
        # ML status
        if ml_service:
            recent_accuracy = ml_service.get_recent_accuracy()
            last_training = ml_service.get_last_training_date()
            
            self.stdout.write(f"🤖 ML accuracy: {recent_accuracy*100:.1f}%")
            if last_training:
                days_since = (datetime.now().date() - last_training).days
                self.stdout.write(f"🔄 Last training: {days_since} days ago")
            
            # Đề xuất nhanh
            if avg_accuracy < 30:
                self.stdout.write(self.style.ERROR("🔥 CRITICAL: Very low accuracy - need immediate action"))
            elif recent_accuracy < 0.3:
                self.stdout.write(self.style.WARNING("⚠️  ML models need retraining"))
            elif days_since > 7:
                self.stdout.write(self.style.WARNING("⚠️  Models are getting old - consider retraining"))
            else:
                self.stdout.write(self.style.SUCCESS("✅ System performance looks good"))
    
    def _full_analysis(self, days, ml_service):
        """Phân tích đầy đủ"""
        self.stdout.write(self.style.SUCCESS("\n=== FULL ANALYSIS ==="))
        
        # Lấy dữ liệu
        end_date = datetime.now().date()
        start_date = end_date - timedelta(days=days)
        
        analyses = DailyPredictionAnalysis.objects.filter(
            analysis_date__range=(start_date, end_date)
        ).exclude(actual_numbers__isnull=True)
        
        if not analyses:
            self.stdout.write(self.style.WARNING("No analysis data available"))
            return
        
        # Tính toán thống kê
        accuracies = [a.accuracy_rate for a in analyses]
        total_days = len(analyses)
        avg_accuracy = sum(accuracies) / len(accuracies)
        std_dev = np.std(accuracies)
        consistency = max(0, 100 - std_dev)
        
        # Xu hướng
        mid_point = len(accuracies) // 2
        first_half = accuracies[:mid_point]
        second_half = accuracies[mid_point:]
        
        first_avg = sum(first_half) / len(first_half) if first_half else 0
        second_avg = sum(second_half) / len(second_half) if second_half else 0
        trend_change = second_avg - first_avg
        
        trend = "improving" if trend_change > 2 else \
                "declining" if trend_change < -2 else "stable"
        
        # Hiển thị kết quả
        self.stdout.write(f"📊 Days analyzed: {total_days}")
        self.stdout.write(f"🎯 Average accuracy: {avg_accuracy:.2f}%")
        self.stdout.write(f"📈 Consistency: {consistency:.2f}%")
        self.stdout.write(f"📉 Trend: {trend} ({trend_change:+.2f}%)")
        
        # Best/worst
        best_day = max(analyses, key=lambda x: x.accuracy_rate)
        worst_day = min(analyses, key=lambda x: x.accuracy_rate)
        self.stdout.write(f"⬆️  Best: {best_day.analysis_date} ({best_day.accuracy_rate:.1f}%)")
        self.stdout.write(f"⬇️  Worst: {worst_day.analysis_date} ({worst_day.accuracy_rate:.1f}%)")
        
        # ML Model Analysis
        if ml_service:
            self._analyze_ml_models(ml_service)
        
        # Recommendations
        self._generate_simple_recommendations(avg_accuracy, trend_change, consistency, ml_service)
    
    def _analyze_ml_models(self, ml_service):
        """Phân tích ML models"""
        self.stdout.write(self.style.SUCCESS("\n--- ML MODELS ---"))
        
        try:
            # Model info
            model_info = ml_service.get_model_info()
            loaded_models = model_info.get('loaded_models', [])
            
            self.stdout.write(f"🤖 Loaded models: {', '.join(loaded_models)}")
            self.stdout.write(f"🔧 Features: {model_info.get('feature_count', 0)}")
            
            # Performance
            recent_accuracy = ml_service.get_recent_accuracy()
            accuracy_style = self.style.SUCCESS if recent_accuracy > 0.4 else \
                           self.style.WARNING if recent_accuracy > 0.25 else \
                           self.style.ERROR
            self.stdout.write(accuracy_style(f"🎯 ML Accuracy: {recent_accuracy*100:.2f}%"))
            
            # Training info
            last_training = ml_service.get_last_training_date()
            if last_training:
                days_since = (datetime.now().date() - last_training).days
                training_style = self.style.SUCCESS if days_since <= 7 else \
                               self.style.WARNING if days_since <= 14 else \
                               self.style.ERROR
                self.stdout.write(training_style(f"🔄 Last training: {days_since} days ago"))
            else:
                self.stdout.write(self.style.ERROR("🔄 No training info available"))
            
            # Feature importance (simplified)
            try:
                feature_importance = ml_service.get_feature_importance()
                if feature_importance:
                    self.stdout.write("🔍 Top features:")
                    for model_name in list(feature_importance.keys())[:2]:  # Show first 2 models
                        features = feature_importance[model_name]
                        top_feature = max(features.items(), key=lambda x: x[1])
                        self.stdout.write(f"   {model_name}: {top_feature[0]} ({top_feature[1]:.3f})")
            except Exception as e:
                self.stdout.write(f"   Feature analysis failed: {e}")
                
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"ML analysis failed: {e}"))
    
    def _generate_simple_recommendations(self, avg_accuracy, trend_change, consistency, ml_service):
        """Tạo đề xuất đơn giản"""
        self.stdout.write(self.style.SUCCESS("\n--- RECOMMENDATIONS ---"))
        
        recommendations = []
        
        # Accuracy-based recommendations
        if avg_accuracy < 20:
            recommendations.append("🚨 CRITICAL: Extremely low accuracy - immediate system review needed")
        elif avg_accuracy < 30:
            recommendations.append("⚠️  LOW: Below acceptable threshold - retrain all models")
        elif avg_accuracy < 40:
            recommendations.append("💡 MODERATE: Room for improvement - tune parameters")
        
        # Trend-based recommendations
        if trend_change < -5:
            recommendations.append("📉 DECLINING: Strong negative trend - investigate cause")
        elif trend_change < -2:
            recommendations.append("⬇️  WEAK: Slight decline - monitor closely")
        elif trend_change > 5:
            recommendations.append("📈 IMPROVING: Strong positive trend - good job!")
        
        # Consistency recommendations
        if consistency < 60:
            recommendations.append("🎲 UNSTABLE: High variance - stabilize methods")
        elif consistency > 85:
            recommendations.append("⚖️  STABLE: Good consistency - maintain current approach")
        
        # ML-specific recommendations
        if ml_service:
            try:
                recent_accuracy = ml_service.get_recent_accuracy()
                last_training = ml_service.get_last_training_date()
                days_since = (datetime.now().date() - last_training).days if last_training else 999
                
                if recent_accuracy < 0.2:
                    recommendations.append("🤖 ML: Models performing poorly - retrain immediately")
                elif days_since > 14:
                    recommendations.append("🤖 ML: Models are old - schedule retraining")
                elif days_since > 7:
                    recommendations.append("🤖 ML: Consider retraining soon")
                
            except Exception:
                recommendations.append("🤖 ML: Unable to assess model status")
        
        # Display recommendations
        if recommendations:
            for i, rec in enumerate(recommendations, 1):
                if "CRITICAL" in rec or "🚨" in rec:
                    style = self.style.ERROR
                elif "⚠️" in rec or "LOW" in rec:
                    style = self.style.WARNING
                else:
                    style = self.style.SUCCESS
                
                self.stdout.write(style(f"{i}. {rec}"))
        else:
            self.stdout.write(self.style.SUCCESS("✅ No specific recommendations - system looks good!"))
    
    def _handle_retrain(self, ml_service):
        """Xử lý retrain models"""
        if not ml_service:
            self.stdout.write(self.style.ERROR("❌ Cannot retrain - ML service not available"))
            return
        
        self.stdout.write("\n🔄 Starting model retraining...")
        
        try:
            # Check compatibility first
            if ml_service.check_version_compatibility():
                self.stdout.write("🔧 Fixing compatibility issues...")
                ml_service.fix_version_compatibility()
            
            # Retrain
            success = ml_service.train_models(force_retrain=True)
            
            if success:
                self.stdout.write(self.style.SUCCESS("✅ Retraining completed successfully"))
                
                # Quick validation
                validation = ml_service.validate_models()
                self.stdout.write(f"🔍 Validation: {validation}")
            else:
                self.stdout.write(self.style.ERROR("❌ Retraining failed"))
                
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"❌ Retraining error: {e}"))