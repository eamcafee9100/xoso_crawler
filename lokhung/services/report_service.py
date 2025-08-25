from django.db.models import Count, Avg, Sum, Max, Min, Q, F
from datetime import datetime, timedelta
from collections import defaultdict
import pandas as pd
import numpy as np

class BtlReportService:
    """Service xử lý các báo cáo cho BTL - Được mở rộng"""
    
    @staticmethod
    def generate_method_performance_report(start_date, end_date, method_ids=None):
        """Tạo báo cáo hiệu suất phương pháp với thống kê nâng cao"""
        from lokhung.models import PredictionResultBtl
        
        queryset = PredictionResultBtl.objects.filter(
            dan_btl__analysis_date__range=[start_date, end_date]
        )
        
        if method_ids:
            queryset = queryset.filter(method_id__in=method_ids)
            
        # Báo cáo chi tiết
        report_data = queryset.values(
            'method__id',
            'method__name',
            'method__category',
            'method__priority'
        ).annotate(
            total_predictions=Count('id'),
            total_hits=Sum('hit_count'),
            avg_hit_count=Avg('hit_count'),
            max_hit_count=Max('hit_count'),
            min_hit_count=Min('hit_count'),
            success_rate=Avg('hit_rate'),
            avg_confidence=Avg('confidence_score'),
            avg_execution_time=Avg('execution_time_ms'),
            
            # Thống kê nâng cao
            successful_predictions=Count('id', filter=Q(hit_count__gt=0)),
            zero_hit_predictions=Count('id', filter=Q(hit_count=0)),
            high_confidence_predictions=Count('id', filter=Q(confidence_score__gte=80)),
            
        ).annotate(
            # Tính toán tỷ lệ
            actual_success_rate=F('successful_predictions') * 100.0 / F('total_predictions'),
            zero_hit_rate=F('zero_hit_predictions') * 100.0 / F('total_predictions'),
            high_confidence_rate=F('high_confidence_predictions') * 100.0 / F('total_predictions'),
            
        ).order_by('-success_rate')
        
        return list(report_data)
    
    @staticmethod
    def generate_trend_analysis_report(method_id, start_date, end_date):
        """Phân tích xu hướng hiệu suất của phương pháp"""
        from lokhung.models import PredictionResultBtl
        
        # Dữ liệu theo ngày
        daily_data = PredictionResultBtl.objects.filter(
            method_id=method_id,
            dan_btl__analysis_date__range=[start_date, end_date]
        ).values('dan_btl__analysis_date').annotate(
            predictions=Count('id'),
            hits=Sum('hit_count'),
            avg_hit_count=Avg('hit_count'),
            max_hit_count=Max('hit_count'),
            avg_confidence=Avg('confidence_score'),
            success_rate=Avg('hit_rate')
        ).order_by('dan_btl__analysis_date')
        
        daily_list = list(daily_data)
        
        if len(daily_list) < 2:
            return {'trend': 'insufficient_data', 'analysis': {}}
        
        # Phân tích xu hướng
        success_rates = [item['success_rate'] for item in daily_list if item['success_rate'] is not None]
        hit_counts = [item['avg_hit_count'] for item in daily_list if item['avg_hit_count'] is not None]
        
        trend_analysis = {
            'period_days': len(daily_list),
            'avg_success_rate': np.mean(success_rates) if success_rates else 0,
            'success_rate_trend': BtlReportService._calculate_trend(success_rates),
            'avg_hit_count': np.mean(hit_counts) if hit_counts else 0,
            'hit_count_trend': BtlReportService._calculate_trend(hit_counts),
            'consistency_score': BtlReportService._calculate_consistency(success_rates),
            'daily_data': daily_list
        }
        
        # Dự đoán xu hướng
        if len(success_rates) >= 7:
            trend_analysis['predicted_trend'] = BtlReportService._predict_trend(success_rates)
        
        return trend_analysis
    
    @staticmethod
    def _calculate_trend(values):
        """Tính toán xu hướng từ danh sách giá trị"""
        if len(values) < 2:
            return 'stable'
        
        # Sử dụng linear regression đơn giản
        x = np.arange(len(values))
        y = np.array(values)
        
        # Tính slope
        slope = np.polyfit(x, y, 1)[0]
        
        if slope > 0.5:
            return 'increasing'
        elif slope < -0.5:
            return 'decreasing'
        else:
            return 'stable'
    
    @staticmethod
    def _calculate_consistency(values):
        """Tính toán điểm ổn định"""
        if len(values) < 2:
            return 0
        
        std_dev = np.std(values)
        mean_val = np.mean(values)
        
        if mean_val == 0:
            return 0
        
        # Coefficient of variation (CV)
        cv = std_dev / mean_val
        
        # Chuyển đổi thành điểm (0-100)
        consistency_score = max(0, 100 - (cv * 100))
        
        return round(consistency_score, 2)
    
    @staticmethod
    def _predict_trend(values):
        """Dự đoán xu hướng cho 7 ngày tiếp theo"""
        if len(values) < 7:
            return None
        
        # Sử dụng simple moving average
        recent_values = values[-7:]
        predicted_value = np.mean(recent_values)
        
        # Tính xu hướng gần đây
        recent_trend = BtlReportService._calculate_trend(recent_values)
        
        return {
            'predicted_value': round(predicted_value, 2),
            'trend_direction': recent_trend,
            'confidence': 'medium'  # Có thể cải thiện bằng ML models
        }
    
    @staticmethod
    def generate_comprehensive_dashboard_data():
        """Tạo dữ liệu tổng hợp cho dashboard"""
        from lokhung.models import PredictionMethodBtl, DanBtl, PredictionResultBtl
        from django.utils import timezone
        
        today = timezone.now().date()
        last_7_days = today - timedelta(days=7)
        last_30_days = today - timedelta(days=30)
        
        # Thống kê tổng quan
        overview = {
            'active_methods': PredictionMethodBtl.objects.filter(is_active=True).count(),
            'total_predictions_today': PredictionResultBtl.objects.filter(
                dan_btl__analysis_date=today
            ).count(),
            'total_predictions_week': PredictionResultBtl.objects.filter(
                dan_btl__analysis_date__gte=last_7_days
            ).count(),
            'total_predictions_month': PredictionResultBtl.objects.filter(
                dan_btl__analysis_date__gte=last_30_days
            ).count(),
        }
        
        # Top performers
        top_methods = PredictionMethodBtl.objects.annotate(
            recent_success_rate=Avg(
                'results_btl__hit_rate',
                filter=Q(results_btl__dan_btl__analysis_date__gte=last_30_days)
            ),
            recent_predictions=Count(
                'results_btl',
                filter=Q(results_btl__dan_btl__analysis_date__gte=last_30_days)
            )
        ).filter(
            recent_predictions__gte=5,
            is_active=True
        ).order_by('-recent_success_rate')[:5]
        
        # Thống kê theo category
        category_stats = PredictionMethodBtl.objects.values('category').annotate(
            count=Count('id'),
            avg_success_rate=Avg('success_rate'),
            total_predictions=Sum('total_predictions')
        ).filter(is_active=True)
        
        # Performance trends (7 ngày gần nhất)
        daily_trends = DanBtl.objects.filter(
            analysis_date__gte=last_7_days
        ).values('analysis_date').annotate(
            total_methods=F('total_methods_used'),
            total_predictions=F('total_predictions_made'),
            total_hits=F('total_hits_achieved'),
            avg_hit_rate=F('avg_hit_rate')
        ).order_by('analysis_date')
        
        return {
            'overview': overview,
            'top_methods': list(top_methods.values()),
            'category_stats': list(category_stats),
            'daily_trends': list(daily_trends),
        }
    