from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import TemplateView, ListView, DetailView
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse, HttpResponse
from django.db.models import Count, Sum, Avg, Max, Min, Q, F
from django.utils import timezone
from datetime import datetime, timedelta, date
from collections import defaultdict, OrderedDict
import json
import pandas as pd
from io import StringIO

from lokhung.models import (
    PredictionMethodBtl, DanBtl, PredictionResultBtl, 
    MethodPerformanceReport, DailyMethodStats
)
from lokhung.services.report_service import BtlReportService
from lokhung.forms import DateRangeForm, MethodComparisonForm


class BaseBtlView(LoginRequiredMixin, TemplateView):
    """Base view cho tất cả BTL views"""
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Thêm thông tin cảnh báo chưa xử lý
        context['canh_bao_chua_xu_ly'] = 0  # Tính từ model CanhBaoHieuQua
        return context


class DashboardView(BaseBtlView):
    """Dashboard tổng quan hệ thống BTL"""
    template_name = 'lokhung/btl/btl_dashboard.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Thống kê tổng quan
        today = timezone.now().date()
        last_7_days = today - timedelta(days=7)
        last_30_days = today - timedelta(days=30)
        
        # Dữ liệu tổng quan
        overview_stats = {
            'total_methods': PredictionMethodBtl.objects.filter(is_active=True).count(),
            'total_predictions_today': PredictionResultBtl.objects.filter(
                dan_btl__analysis_date=today
            ).count(),
            'total_predictions_7days': PredictionResultBtl.objects.filter(
                dan_btl__analysis_date__gte=last_7_days
            ).count(),
            'total_predictions_30days': PredictionResultBtl.objects.filter(
                dan_btl__analysis_date__gte=last_30_days
            ).count(),
        }
        
        # Top performers
        top_methods = PredictionMethodBtl.objects.get_top_performers(limit=5, period_days=30)
        
        # Thống kê hiệu suất theo ngày (7 ngày gần nhất)
        daily_performance = self._get_daily_performance_data(last_7_days, today)
        
        # Dữ liệu cho biểu đồ
        chart_data = self._prepare_chart_data(last_30_days, today)
        
        context.update({
            'overview_stats': overview_stats,
            'top_methods': top_methods,
            'daily_performance': daily_performance,
            'chart_data': chart_data,
        })
        
        return context
    
    def _get_daily_performance_data(self, start_date, end_date):
        """Lấy dữ liệu hiệu suất hàng ngày"""
        daily_stats = DanBtl.objects.filter(
            analysis_date__range=[start_date, end_date]
        ).values('analysis_date').annotate(
            total_methods=F('total_methods_used'),
            total_predictions=F('total_predictions_made'),
            total_hits=F('total_hits_achieved'),
            avg_hit_rate=F('avg_hit_rate'),
            best_hit_count=F('best_method_hit_count')
        ).order_by('analysis_date')
        
        return list(daily_stats)
    
    def _prepare_chart_data(self, start_date, end_date):
        """Chuẩn bị dữ liệu cho biểu đồ"""
        # Dữ liệu success rate theo thời gian
        success_rate_data = []
        hit_count_data = []
        
        daily_data = DanBtl.objects.filter(
            analysis_date__range=[start_date, end_date]
        ).order_by('analysis_date')
        
        for dan_btl in daily_data:
            success_rate_data.append({
                'date': dan_btl.analysis_date.strftime('%Y-%m-%d'),
                'value': round(dan_btl.avg_hit_rate, 2)
            })
            hit_count_data.append({
                'date': dan_btl.analysis_date.strftime('%Y-%m-%d'),
                'value': dan_btl.best_method_hit_count
            })
        
        return {
            'success_rate': success_rate_data,
            'hit_count': hit_count_data,
            'labels': [item['date'] for item in success_rate_data]
        }


class MethodListView(BaseBtlView):
    """Danh sách các phương pháp dự đoán"""
    template_name = 'lokhung/btl/method_list.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Lấy tham số filter
        category = self.request.GET.get('category', 'all')
        sort_by = self.request.GET.get('sort', 'success_rate')
        
        # Query methods
        queryset = PredictionMethodBtl.objects.all()
        
        if category != 'all':
            queryset = queryset.filter(category=category)
        
        # Sắp xếp
        if sort_by == 'success_rate':
            queryset = queryset.order_by('-success_rate', '-total_hits')
        elif sort_by == 'total_predictions':
            queryset = queryset.order_by('-total_predictions')
        elif sort_by == 'avg_hits':
            queryset = queryset.order_by('-avg_hit_count')
        elif sort_by == 'last_used':
            queryset = queryset.order_by('-last_used_at')
        
        methods = queryset[:50]  # Limit để tránh quá tải
        
        # Thống kê theo category
        category_stats = PredictionMethodBtl.objects.values('category').annotate(
            count=Count('id'),
            avg_success_rate=Avg('success_rate'),
            total_predictions=Sum('total_predictions')
        ).order_by('-avg_success_rate')
        
        context.update({
            'methods': methods,
            'category_stats': category_stats,
            'current_category': category,
            'current_sort': sort_by,
            'categories': PredictionMethodBtl._meta.get_field('category').choices,
        })
        
        return context


class MethodDetailView(BaseBtlView, DetailView):
    """Chi tiết phương pháp dự đoán"""
    model = PredictionMethodBtl
    template_name = 'lokhung/btl/method_detail.html'
    context_object_name = 'method'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        method = self.get_object()
        
        # Lấy tham số thời gian
        days = int(self.request.GET.get('days', 30))
        end_date = timezone.now().date()
        start_date = end_date - timedelta(days=days)
        
        # Thống kê chi tiết
        detailed_stats = self._get_method_detailed_stats(method, start_date, end_date)
        
        # Dữ liệu hiệu suất theo ngày
        daily_performance = self._get_method_daily_performance(method, start_date, end_date)
        
        # So sánh với các phương pháp khác
        comparison_data = self._get_method_comparison(method)
        
        # Dự đoán gần đây
        recent_predictions = PredictionResultBtl.objects.filter(
            method=method,
            dan_btl__analysis_date__gte=start_date
        ).select_related('dan_btl').order_by('-dan_btl__analysis_date')[:20]
        
        context.update({
            'detailed_stats': detailed_stats,
            'daily_performance': daily_performance,
            'comparison_data': comparison_data,
            'recent_predictions': recent_predictions,
            'selected_days': days,
        })
        
        return context
    
    def _get_method_detailed_stats(self, method, start_date, end_date):
        """Lấy thống kê chi tiết của phương pháp"""
        results = PredictionResultBtl.objects.filter(
            method=method,
            dan_btl__analysis_date__range=[start_date, end_date]
        )
        
        stats = results.aggregate(
            total_predictions=Count('id'),
            total_hits=Sum('hit_count'),
            avg_hit_count=Avg('hit_count'),
            max_hit_count=Max('hit_count'),
            min_hit_count=Min('hit_count'),
            avg_confidence=Avg('confidence_score'),
            avg_execution_time=Avg('execution_time_ms')
        )
        
        # Tính thêm một số thống kê
        if stats['total_predictions']:
            successful_predictions = results.filter(hit_count__gt=0).count()
            stats['success_rate'] = (successful_predictions / stats['total_predictions']) * 100
            stats['hit_rate'] = (stats['total_hits'] or 0) / stats['total_predictions']
        else:
            stats['success_rate'] = 0
            stats['hit_rate'] = 0
        
        # Phân bố số trúng
        hit_distribution = results.values('hit_count').annotate(
            count=Count('id')
        ).order_by('hit_count')
        
        stats['hit_distribution'] = list(hit_distribution)
        
        return stats
    
    def _get_method_daily_performance(self, method, start_date, end_date):
        """Lấy hiệu suất hàng ngày"""
        daily_stats = PredictionResultBtl.objects.filter(
            method=method,
            dan_btl__analysis_date__range=[start_date, end_date]
        ).values('dan_btl__analysis_date').annotate(
            predictions=Count('id'),
            hits=Sum('hit_count'),
            avg_hit_count=Avg('hit_count'),
            max_hit_count=Max('hit_count'),
            avg_confidence=Avg('confidence_score')
        ).order_by('dan_btl__analysis_date')
        
        return list(daily_stats)
    
    def _get_method_comparison(self, method):
        """So sánh với các phương pháp khác cùng category"""
        same_category_methods = PredictionMethodBtl.objects.filter(
            category=method.category,
            is_active=True
        ).exclude(id=method.id).order_by('-success_rate')[:5]
        
        return same_category_methods


class ReportListView(BaseBtlView):
    """Danh sách các báo cáo"""
    template_name = 'lokhung/btl/report_list.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Các loại báo cáo có sẵn
        report_types = [
            {
                'id': 'performance_summary',
                'name': 'Tổng quan hiệu suất',
                'description': 'Báo cáo tổng quan hiệu suất các phương pháp',
                'url': 'lokhung:report_performance_summary'
            },
            {
                'id': 'method_comparison',
                'name': 'So sánh phương pháp',
                'description': 'So sánh hiệu suất giữa các phương pháp',
                'url': 'lokhung:report_method_comparison'
            },
            {
                'id': 'daily_frequency',
                'name': 'Tần suất hàng ngày',
                'description': 'Phân tích tần suất trúng hàng ngày của từng phương pháp',
                'url': 'lokhung:report_daily_frequency'
            },
            {
                'id': 'trend_analysis',
                'name': 'Phân tích xu hướng',
                'description': 'Phân tích xu hướng hiệu suất theo thời gian',
                'url': 'lokhung:report_trend_analysis'
            },
        ]
        
        # Báo cáo đã tạo gần đây
        recent_reports = MethodPerformanceReport.objects.select_related('method').order_by('-created_at')[:10]
        
        context.update({
            'report_types': report_types,
            'recent_reports': recent_reports,
        })
        
        return context


class PerformanceSummaryReportView(BaseBtlView):
    """Báo cáo tổng quan hiệu suất"""
    template_name = 'lokhung//btl/report_performance_summary.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Lấy tham số từ request
        start_date_str = self.request.GET.get('start_date')
        end_date_str = self.request.GET.get('end_date')
        method_ids = self.request.GET.getlist('method_ids')
        
        # Thiết lập ngày mặc định (30 ngày gần nhất)
        if not start_date_str or not end_date_str:
            end_date = timezone.now().date()
            start_date = end_date - timedelta(days=30)
        else:
            start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
            end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()
        
        # Tạo báo cáo
        report_data = BtlReportService.generate_method_performance_report(
            start_date, end_date, method_ids
        )
        
        # Thống kê tổng hợp
        summary_stats = self._calculate_summary_stats(report_data)
        
        # Dữ liệu cho biểu đồ
        chart_data = self._prepare_performance_chart_data(report_data)
        
        context.update({
            'report_data': report_data,
            'summary_stats': summary_stats,
            'chart_data': chart_data,
            'start_date': start_date,
            'end_date': end_date,
            'selected_methods': method_ids,
            'available_methods': PredictionMethodBtl.objects.filter(is_active=True),
        })
        
        return context
    
    def _calculate_summary_stats(self, report_data):
        """Tính toán thống kê tổng hợp"""
        if not report_data:
            return {}
        
        total_predictions = sum(item['total_predictions'] for item in report_data)
        total_hits = sum(item['total_hits'] for item in report_data)
        
        return {
            'total_methods': len(report_data),
            'total_predictions': total_predictions,
            'total_hits': total_hits,
            'overall_hit_rate': (total_hits / total_predictions * 100) if total_predictions else 0,
            'avg_success_rate': sum(item['success_rate'] for item in report_data) / len(report_data),
            'best_method': max(report_data, key=lambda x: x['success_rate']) if report_data else None,
            'worst_method': min(report_data, key=lambda x: x['success_rate']) if report_data else None,
        }
    
    def _prepare_performance_chart_data(self, report_data):
        """Chuẩn bị dữ liệu cho biểu đồ hiệu suất"""
        return {
            'labels': [item['method__name'] for item in report_data],
            'success_rates': [round(item['success_rate'], 2) for item in report_data],
            'total_predictions': [item['total_predictions'] for item in report_data],
            'avg_hit_counts': [round(item['avg_hit_count'], 2) for item in report_data],
        }


class MethodComparisonReportView(BaseBtlView):
    """Báo cáo so sánh phương pháp"""
    template_name = 'lokhung/btl/report_method_comparison.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Lấy tham số
        method_ids = self.request.GET.getlist('method_ids')
        start_date_str = self.request.GET.get('start_date')
        end_date_str = self.request.GET.get('end_date')
        
        # Thiết lập mặc định
        if not start_date_str or not end_date_str:
            end_date = timezone.now().date()
            start_date = end_date - timedelta(days=30)
        else:
            start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
            end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()
        
        if not method_ids:
            # Lấy top 5 methods mặc định
            top_methods = PredictionMethodBtl.objects.get_top_performers(limit=5)
            method_ids = [str(method.id) for method in top_methods]
        
        # Tạo báo cáo so sánh
        comparison_data = BtlReportService.generate_comparison_report(
            method_ids, start_date, end_date
        )
        
        # Chuẩn bị dữ liệu cho bảng so sánh
        comparison_table = self._prepare_comparison_table(comparison_data, method_ids)
        
        # Dữ liệu cho biểu đồ radar
        radar_chart_data = self._prepare_radar_chart_data(comparison_data, method_ids)
        
        context.update({
            'comparison_data': comparison_data,
            'comparison_table': comparison_table,
            'radar_chart_data': radar_chart_data,
            'selected_methods': method_ids,
            'start_date': start_date,
            'end_date': end_date,
            'available_methods': PredictionMethodBtl.objects.filter(is_active=True),
        })
        
        return context
    
    def _prepare_comparison_table(self, comparison_data, method_ids):
        """Chuẩn bị dữ liệu cho bảng so sánh"""
        methods = PredictionMethodBtl.objects.filter(id__in=method_ids)
        method_dict = {str(method.id): method for method in methods}
        
        table_data = []
        for method_id in method_ids:
            method = method_dict.get(method_id)
            stats = comparison_data.get(int(method_id), {})
            
            table_data.append({
                'method': method,
                'stats': stats,
                'rank_success': 0,  # Sẽ tính sau
                'rank_hits': 0,     # Sẽ tính sau
            })
        
        # Tính ranking
        table_data.sort(key=lambda x: x['stats'].get('success_rate', 0), reverse=True)
        for i, item in enumerate(table_data):
            item['rank_success'] = i + 1
        
        table_data.sort(key=lambda x: x['stats'].get('avg_hit_count', 0), reverse=True)
        for i, item in enumerate(table_data):
            item['rank_hits'] = i + 1
        
        return table_data
    
    def _prepare_radar_chart_data(self, comparison_data, method_ids):
        """Chuẩn bị dữ liệu cho biểu đồ radar"""
        methods = PredictionMethodBtl.objects.filter(id__in=method_ids)
        
        datasets = []
        for method in methods:
            stats = comparison_data.get(method.id, {})
            
            # Normalize các giá trị về thang 0-100
            normalized_data = [
                stats.get('success_rate', 0),
                min(stats.get('avg_hit_count', 0) * 10, 100),  # Scale hit count
                stats.get('consistency', 0),
                min(stats.get('total_predictions', 0) / 10, 100),  # Scale predictions
            ]
            
            datasets.append({
                'label': method.name,
                'data': normalized_data,
                'borderColor': self._get_method_color(method.id),
                'backgroundColor': self._get_method_color(method.id, alpha=0.2),
            })
        
        return {
            'labels': ['Tỷ lệ thành công', 'Số trúng TB', 'Tính ổn định', 'Số dự đoán'],
            'datasets': datasets
        }
    
    def _get_method_color(self, method_id, alpha=1.0):
        """Lấy màu cho method trong biểu đồ"""
        colors = [
            f'rgba(255, 99, 132, {alpha})',
            f'rgba(54, 162, 235, {alpha})',
            f'rgba(255, 205, 86, {alpha})',
            f'rgba(75, 192, 192, {alpha})',
            f'rgba(153, 102, 255, {alpha})',
        ]
        return colors[method_id % len(colors)]


class DailyFrequencyReportView(BaseBtlView):
    """Báo cáo tần suất trúng hàng ngày"""
    template_name = 'lokhung/btl/report_daily_frequency.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Lấy tham số
        method_id = self.request.GET.get('method_id')
        start_date_str = self.request.GET.get('start_date')
        end_date_str = self.request.GET.get('end_date')
        
        # Thiết lập mặc định
        if not start_date_str or not end_date_str:
            end_date = timezone.now().date()
            start_date = end_date - timedelta(days=30)
        else:
            start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
            end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()
        
        if not method_id:
            # Lấy method có hiệu suất tốt nhất làm mặc định
            top_method = PredictionMethodBtl.objects.get_top_performers(limit=1).first()
            method_id = top_method.id if top_method else None
        
        if method_id:
            method = get_object_or_404(PredictionMethodBtl, id=method_id)
            
            # Tạo báo cáo tần suất hàng ngày
            daily_data = BtlReportService.generate_daily_frequency_report(
                start_date, end_date, method_id
            )
            
            # Phân tích tần suất
            frequency_analysis = self._analyze_frequency_patterns(daily_data)
            
            # Dữ liệu cho biểu đồ
            chart_data = self._prepare_frequency_chart_data(daily_data)
            
            context.update({
                'method': method,
                'daily_data': daily_data,
                'frequency_analysis': frequency_analysis,
                'chart_data': chart_data,
            })
        
        context.update({
            'selected_method_id': method_id,
            'start_date': start_date,
            'end_date': end_date,
            'available_methods': PredictionMethodBtl.objects.filter(is_active=True),
        })
        
        return context
    
    def _analyze_frequency_patterns(self, daily_data):
        """Phân tích các pattern tần suất"""
        if not daily_data:
            return {}
        
        hit_counts = [item['hit_count'] for item in daily_data]
        hit_rates = [item['hit_rate'] for item in daily_data if item['hit_rate'] is not None]
        
        analysis = {
            'total_days': len(daily_data),
            'days_with_hits': len([x for x in hit_counts if x > 0]),
            'avg_hit_count': sum(hit_counts) / len(hit_counts) if hit_counts else 0,
            'max_hit_count': max(hit_counts) if hit_counts else 0,
            'min_hit_count': min(hit_counts) if hit_counts else 0,
            'avg_hit_rate': sum(hit_rates) / len(hit_rates) if hit_rates else 0,
        }
        
        # Tính consistency
        if len(hit_counts) > 1:
            import statistics
            analysis['hit_count_std'] = statistics.stdev(hit_counts)
            analysis['consistency_score'] = max(0, 100 - analysis['hit_count_std'] * 10)
        else:
            analysis['consistency_score'] = 0
        
        # Phân tích streaks
        current_streak = 0
        max_streak = 0
        for hit_count in hit_counts:
            if hit_count > 0:
                current_streak += 1
                max_streak = max(max_streak, current_streak)
            else:
                current_streak = 0
        
        analysis['max_streak'] = max_streak
        
        return analysis
    
    def _prepare_frequency_chart_data(self, daily_data):
        """Chuẩn bị dữ liệu cho biểu đồ tần suất"""
        return {
            'labels': [item['date'].strftime('%m-%d') for item in daily_data],
            'hit_counts': [item['hit_count'] for item in daily_data],
            'hit_rates': [round(item['hit_rate'], 2) for item in daily_data],
            'confidences': [round(item['confidence'], 2) for item in daily_data],
        }


# API Views cho AJAX calls
class MethodStatsAPIView(BaseBtlView):
    """API endpoint để lấy thống kê method qua AJAX"""
    
    def get(self, request, *args, **kwargs):
        method_id = request.GET.get('method_id')
        days = int(request.GET.get('days', 30))
        
        if not method_id:
            return JsonResponse({'error': 'Method ID required'}, status=400)
        
        try:
            method = PredictionMethodBtl.objects.get(id=method_id)
            end_date = timezone.now().date()
            start_date = end_date - timedelta(days=days)
            
            stats = method.objects.get_performance_summary(method_id, days)
            
            return JsonResponse({
                'success': True,
                'stats': {
                    'total_predictions': stats.period_predictions or 0,
                    'avg_hits': round(stats.period_avg_hits or 0, 2),
                    'max_hits': stats.period_max_hits or 0,
                    'success_rate': round(stats.period_success_rate or 0, 2),
                }
            })
            
        except PredictionMethodBtl.DoesNotExist:
            return JsonResponse({'error': 'Method not found'}, status=404)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

class ReportTrendAnalysisView(BaseBtlView):
    """Báo cáo phân tích xu hướng"""
    template_name = 'lokhung/btl/report_trend_analysis.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Lấy tham số từ request
        method_id = self.request.GET.get('method_id')
        period = self.request.GET.get('period', '30')  # 30, 60, 90 days
        analysis_type = self.request.GET.get('analysis_type', 'success_rate')
        
        # Thiết lập khoảng thời gian
        end_date = timezone.now().date()
        days = int(period)
        start_date = end_date - timedelta(days=days)
        
        # Lấy danh sách methods để phân tích
        if method_id:
            methods = [get_object_or_404(PredictionMethodBtl, id=method_id)]
        else:
            # Lấy top 5 methods có hiệu suất tốt nhất
            methods = list(PredictionMethodBtl.objects.get_top_performers(limit=5))
        
        # Tạo dữ liệu xu hướng
        trend_data = self._generate_trend_data(methods, start_date, end_date, analysis_type)
        
        # Phân tích xu hướng
        trend_analysis = self._analyze_trends(trend_data)
        
        # Dự báo xu hướng
        trend_forecasts = self._forecast_trends(trend_data)
        
        # Dữ liệu cho biểu đồ
        chart_data = self._prepare_trend_chart_data(trend_data, analysis_type)
        
        context.update({
            'methods': methods,
            'trend_data': trend_data,
            'trend_analysis': trend_analysis,
            'trend_forecasts': trend_forecasts,
            'chart_data': chart_data,
            'selected_method_id': method_id,
            'selected_period': period,
            'selected_analysis_type': analysis_type,
            'period_options': [
                ('7', '7 ngày'),
                ('30', '30 ngày'), 
                ('60', '60 ngày'),
                ('90', '90 ngày'),
            ],
            'analysis_type_options': [
                ('success_rate', 'Tỷ lệ thành công'),
                ('hit_count', 'Số lần trúng'),
                ('consistency', 'Tính ổn định'),
                ('confidence', 'Độ tin cậy'),
            ],
            'available_methods': PredictionMethodBtl.objects.filter(is_active=True),
        })
        
        return context
    
    def _generate_trend_data(self, methods, start_date, end_date, analysis_type):
        """
        Tạo dữ liệu xu hướng cho các phương pháp
        Trả về: dict với structure {
            method_id: {
                'method': PredictionMethodBtl,
                'daily_data': [{'date': date, 'value': float, 'volume': int}],
                'weekly_data': [{'week': str, 'value': float, 'volume': int}],
                'summary': {'trend': str, 'change_rate': float, 'volatility': float}
            }
        }
        """
        trend_data = {}
        
        for method in methods:
            # Lấy dữ liệu hàng ngày
            daily_results = PredictionResultBtl.objects.filter(
                method=method,
                dan_btl__analysis_date__range=[start_date, end_date]
            ).values('dan_btl__analysis_date').annotate(
                predictions_count=Count('id'),
                total_hits=Sum('hit_count'),
                avg_hits=Avg('hit_count'),
                avg_confidence=Avg('confidence_score'),
                success_predictions=Count('id', filter=Q(hit_count__gt=0))
            ).order_by('dan_btl__analysis_date')
            
            daily_data = []
            for result in daily_results:
                date = result['dan_btl__analysis_date']
                predictions = result['predictions_count']
                
                if analysis_type == 'success_rate':
                    value = (result['success_predictions'] / predictions * 100) if predictions else 0
                elif analysis_type == 'hit_count':
                    value = result['avg_hits'] or 0
                elif analysis_type == 'consistency':
                    # Tính consistency dựa trên độ lệch chuẩn
                    value = self._calculate_daily_consistency(method, date)
                elif analysis_type == 'confidence':
                    value = result['avg_confidence'] or 0
                else:
                    value = 0
                
                daily_data.append({
                    'date': date,
                    'value': round(value, 2),
                    'volume': predictions,
                    'hits': result['total_hits'] or 0
                })
            
            # Nhóm dữ liệu theo tuần
            weekly_data = self._group_by_week(daily_data)
            
            # Phân tích summary
            summary = self._calculate_trend_summary(daily_data)
            
            trend_data[method.id] = {
                'method': method,
                'daily_data': daily_data,
                'weekly_data': weekly_data,
                'summary': summary
            }
        
        return trend_data
    
    def _calculate_daily_consistency(self, method, date):
        """
        Tính consistency cho một ngày cụ thể
        Trả về: float (0-100)
        """
        # Lấy dữ liệu 7 ngày gần nhất từ ngày đó
        week_start = date - timedelta(days=6)
        week_results = PredictionResultBtl.objects.filter(
            method=method,
            dan_btl__analysis_date__range=[week_start, date]
        ).values_list('hit_count', flat=True)
        
        if len(week_results) < 2:
            return 50  # Giá trị mặc định
        
        # Tính độ lệch chuẩn
        import statistics
        mean_hits = statistics.mean(week_results)
        std_dev = statistics.stdev(week_results)
        
        # Chuyển đổi thành điểm consistency (0-100)
        consistency = max(0, 100 - (std_dev / (mean_hits + 1)) * 50)
        return round(consistency, 2)
    
    def _group_by_week(self, daily_data):
        """
        Nhóm dữ liệu hàng ngày thành dữ liệu hàng tuần
        Trả về: list[dict] với structure [{'week': str, 'value': float, 'volume': int}]
        """
        weekly_data = []
        current_week = []
        
        for item in daily_data:
            current_week.append(item)
            
            # Nếu là chủ nhật hoặc là item cuối cùng
            if item['date'].weekday() == 6 or item == daily_data[-1]:
                if current_week:
                    week_start = current_week[0]['date']
                    week_end = current_week[-1]['date']
                    
                    # Tính giá trị trung bình của tuần
                    avg_value = sum(d['value'] for d in current_week) / len(current_week)
                    total_volume = sum(d['volume'] for d in current_week)
                    total_hits = sum(d['hits'] for d in current_week)
                    
                    weekly_data.append({
                        'week': f"{week_start.strftime('%m/%d')} - {week_end.strftime('%m/%d')}",
                        'value': round(avg_value, 2),
                        'volume': total_volume,
                        'hits': total_hits
                    })
                    
                    current_week = []
        
        return weekly_data
    
    def _calculate_trend_summary(self, daily_data):
        """
        Tính toán tóm tắt xu hướng
        Trả về: dict với structure {
            'trend': str,  # 'increasing', 'decreasing', 'stable'
            'change_rate': float,  # % thay đổi
            'volatility': float,   # độ biến động
            'avg_value': float,
            'max_value': float,
            'min_value': float
        }
        """
        if len(daily_data) < 2:
            return {
                'trend': 'stable',
                'change_rate': 0,
                'volatility': 0,
                'avg_value': 0,
                'max_value': 0,
                'min_value': 0
            }
        
        values = [item['value'] for item in daily_data]
        
        # Tính xu hướng dựa trên linear regression đơn giản
        n = len(values)
        x_values = list(range(n))
        
        # Tính slope
        x_mean = sum(x_values) / n
        y_mean = sum(values) / n
        
        numerator = sum((x_values[i] - x_mean) * (values[i] - y_mean) for i in range(n))
        denominator = sum((x_values[i] - x_mean) ** 2 for i in range(n))
        
        slope = numerator / denominator if denominator != 0 else 0
        
        # Xác định xu hướng
        if slope > 0.1:
            trend = 'increasing'
        elif slope < -0.1:
            trend = 'decreasing'
        else:
            trend = 'stable'
        
        # Tính % thay đổi
        first_value = values[0] if values[0] != 0 else 0.01
        last_value = values[-1]
        change_rate = ((last_value - first_value) / first_value) * 100 if first_value != 0 else 0
        
        # Tính volatility (coefficient of variation)
        import statistics
        std_dev = statistics.stdev(values) if len(values) > 1 else 0
        avg_value = statistics.mean(values)
        volatility = (std_dev / avg_value * 100) if avg_value != 0 else 0
        
        return {
            'trend': trend,
            'change_rate': round(change_rate, 2),
            'volatility': round(volatility, 2),
            'avg_value': round(avg_value, 2),
            'max_value': round(max(values), 2),
            'min_value': round(min(values), 2)
        }
    
    def _analyze_trends(self, trend_data):
        """
        Phân tích tổng quan về xu hướng
        Trả về: dict với analysis tổng hợp
        """
        if not trend_data:
            return {}
        
        # Thống kê xu hướng
        trend_counts = {'increasing': 0, 'decreasing': 0, 'stable': 0}
        all_change_rates = []
        all_volatilities = []
        
        for method_id, data in trend_data.items():
            summary = data['summary']
            trend_counts[summary['trend']] += 1
            all_change_rates.append(summary['change_rate'])
            all_volatilities.append(summary['volatility'])
        
        # Tìm method có xu hướng tốt nhất và tệ nhất
        best_method = max(trend_data.items(), key=lambda x: x[1]['summary']['change_rate'])
        worst_method = min(trend_data.items(), key=lambda x: x[1]['summary']['change_rate'])
        
        # Method ổn định nhất (volatility thấp nhất)
        most_stable = min(trend_data.items(), key=lambda x: x[1]['summary']['volatility'])
        
        return {
            'total_methods': len(trend_data),
            'trend_distribution': trend_counts,
            'avg_change_rate': round(sum(all_change_rates) / len(all_change_rates), 2),
            'avg_volatility': round(sum(all_volatilities) / len(all_volatilities), 2),
            'best_performer': {
                'method': best_method[1]['method'],
                'change_rate': best_method[1]['summary']['change_rate']
            },
            'worst_performer': {
                'method': worst_method[1]['method'],
                'change_rate': worst_method[1]['summary']['change_rate']
            },
            'most_stable': {
                'method': most_stable[1]['method'],
                'volatility': most_stable[1]['summary']['volatility']
            }
        }
    
    def _forecast_trends(self, trend_data):
        """
        Dự báo xu hướng đơn giản cho 7 ngày tới
        Trả về: dict với forecast data
        """
        forecasts = {}
        
        for method_id, data in trend_data.items():
            daily_data = data['daily_data']
            if len(daily_data) < 3:
                continue
            
            # Lấy 7 ngày gần nhất để dự báo
            recent_data = daily_data[-7:] if len(daily_data) >= 7 else daily_data
            values = [item['value'] for item in recent_data]
            
            # Tính moving average
            window_size = min(3, len(values))
            moving_avg = sum(values[-window_size:]) / window_size
            
            # Dự báo đơn giản dựa trên xu hướng gần đây
            trend = data['summary']['trend']
            if trend == 'increasing':
                forecast_change = 0.05  # Tăng 5%
            elif trend == 'decreasing':
                forecast_change = -0.05  # Giảm 5%
            else:
                forecast_change = 0  # Không đổi
            
            forecasted_value = moving_avg * (1 + forecast_change)
            
            forecasts[method_id] = {
                'method': data['method'],
                'current_value': values[-1] if values else 0,
                'forecasted_value': round(forecasted_value, 2),
                'confidence': self._calculate_forecast_confidence(data),
                'recommendation': self._generate_recommendation(data)
            }
        
        return forecasts
    
    def _calculate_forecast_confidence(self, data):
        """
        Tính độ tin cậy của dự báo dựa trên volatility và data points
        Trả về: float (0-100)
        """
        volatility = data['summary']['volatility']
        data_points = len(data['daily_data'])
        
        # Confidence giảm khi volatility cao và data points ít
        base_confidence = 100
        volatility_penalty = min(volatility * 0.5, 50)  # Max penalty 50%
        data_penalty = max(0, (30 - data_points) * 2)  # Penalty if < 30 data points
        
        confidence = max(10, base_confidence - volatility_penalty - data_penalty)
        return round(confidence, 1)
    
    def _generate_recommendation(self, data):
        """
        Tạo khuyến nghị dựa trên phân tích xu hướng
        Trả về: str
        """
        summary = data['summary']
        trend = summary['trend']
        change_rate = summary['change_rate']
        volatility = summary['volatility']
        
        if trend == 'increasing' and change_rate > 10:
            if volatility < 20:
                return "Khuyến nghị SỬ DỤNG: Xu hướng tăng mạnh và ổn định"
            else:
                return "Khuyến nghị THẬN TRỌNG: Xu hướng tăng nhưng biến động cao"
        elif trend == 'decreasing' and change_rate < -10:
            return "Khuyến nghị TRÁNH: Xu hướng giảm mạnh"
        elif volatility > 50:
            return "Khuyến nghị TRÁNH: Biến động quá cao, không ổn định"
        elif trend == 'stable' and volatility < 20:
            return "Khuyến nghị SỬ DỤNG: Hiệu suất ổn định"
        else:
            return "Khuyến nghị THEO DÕI: Cần thêm dữ liệu để đánh giá"
    
    def _prepare_trend_chart_data(self, trend_data, analysis_type):
        """
        Chuẩn bị dữ liệu cho biểu đồ xu hướng
        Trả về: dict với chart data structure
        """
        if not trend_data:
            return {}
        
        # Lấy tất cả dates từ tất cả methods
        all_dates = set()
        for data in trend_data.values():
            for item in data['daily_data']:
                all_dates.add(item['date'])
        
        sorted_dates = sorted(all_dates)
        labels = [date.strftime('%m-%d') for date in sorted_dates]
        
        # Tạo datasets cho từng method
        datasets = []
        colors = [
            'rgba(255, 99, 132, 1)',
            'rgba(54, 162, 235, 1)', 
            'rgba(255, 205, 86, 1)',
            'rgba(75, 192, 192, 1)',
            'rgba(153, 102, 255, 1)',
        ]
        
        for i, (method_id, data) in enumerate(trend_data.items()):
            # Tạo data array với null cho missing dates
            method_data = []
            daily_dict = {item['date']: item['value'] for item in data['daily_data']}
            
            for date in sorted_dates:
                method_data.append(daily_dict.get(date, None))
            
            datasets.append({
                'label': data['method'].name,
                'data': method_data,
                'borderColor': colors[i % len(colors)],
                'backgroundColor': colors[i % len(colors)].replace('1)', '0.1)'),
                'fill': False,
                'tension': 0.1
            })
        
        return {
            'labels': labels,
            'datasets': datasets,
            'analysis_type': analysis_type
        }

    
    
class ExportReportView(BaseBtlView):
    """Export báo cáo ra CSV/Excel"""
    
    def get(self, request, *args, **kwargs):
        report_type = request.GET.get('type')
        format_type = request.GET.get('format', 'csv')
        
        if report_type == 'performance_summary':
            data = self._get_performance_summary_data()
        elif report_type == 'method_comparison':
            data = self._get_method_comparison_data()
        else:
            return JsonResponse({'error': 'Invalid report type'}, status=400)
        
        if format_type == 'csv':
            return self._export_csv(data, f'{report_type}_report.csv')
        elif format_type == 'excel':
            return self._export_excel(data, f'{report_type}_report.xlsx')
        else:
            return JsonResponse({'error': 'Invalid format'}, status=400)
    
    def _export_csv(self, data, filename):
        """Export dữ liệu ra CSV"""
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        
        if data:
            df = pd.DataFrame(data)
            df.to_csv(response, index=False, encoding='utf-8-sig')
        
        return response
    
    def _export_excel(self, data, filename):
        """Export dữ liệu ra Excel"""
        response = HttpResponse(
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        
        if data:
            df = pd.DataFrame(data)
            df.to_excel(response, index=False, engine='openpyxl')
        
        return response
    
# // cần triển khai kỹ lại

class PredictionListView(BaseBtlView):
    """Danh sách dự đoán BTL"""
    template_name = 'lokhung/btl/prediction_list.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Lấy dữ liệu dự đoán gần đây
        recent_predictions = PredictionResultBtl.objects.select_related(
            'method', 'dan_btl'
        ).order_by('-dan_btl__analysis_date')[:20]
        
        # Thống kê tổng quan
        stats = {
            'total_predictions': PredictionResultBtl.objects.count(),
            'active_methods': PredictionMethodBtl.objects.filter(is_active=True).count(),
            'today_predictions': PredictionResultBtl.objects.filter(
                dan_btl__analysis_date=timezone.now().date()
            ).count(),
        }
        
        context.update({
            'recent_predictions': recent_predictions,
            'stats': stats,
        })
        
        return context


class FrameListView(BaseBtlView):
    """Danh sách lô khung BTL"""
    template_name = 'lokhung/btl/frame_list.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Dữ liệu lô khung (có thể tạo model LoKhungBtl nếu cần)
        # Tạm thời dùng dữ liệu mẫu
        frames = []
        
        # Thống kê lô khung
        stats = {
            'total_frames': 0,
            'active_frames': 0,
            'today_frames': 0,
        }
        
        context.update({
            'frames': frames,
            'stats': stats,
        })
        
        return context


class AnalysisListView(BaseBtlView):
    """Danh sách phân tích BTL"""
    template_name = 'lokhung/btl/analysis_list.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Lấy dữ liệu phân tích từ DanBtl
        recent_analysis = DanBtl.objects.order_by('-analysis_date')[:15]
        
        # Thống kê phân tích
        stats = {
            'total_analysis': DanBtl.objects.count(),
            'this_month_analysis': DanBtl.objects.filter(
                analysis_date__month=timezone.now().month,
                analysis_date__year=timezone.now().year
            ).count(),
            'avg_methods_per_day': DanBtl.objects.aggregate(
                avg=Avg('total_methods_used')
            )['avg'] or 0,
        }
        
        context.update({
            'recent_analysis': recent_analysis,
            'stats': stats,
        })
        
        return context


class AlertListView(BaseBtlView):
    """Danh sách cảnh báo BTL"""
    template_name = 'lokhung/btl/alert_list.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Tạo dữ liệu cảnh báo mẫu (có thể tạo model CanhBaoBtl nếu cần)
        alerts = []
        
        # Phát hiện các phương pháp có hiệu suất thấp
        poor_methods = PredictionMethodBtl.objects.filter(
            success_rate__lt=30,
            is_active=True
        )
        
        for method in poor_methods:
            alerts.append({
                'type': 'warning',
                'title': f'Hiệu suất thấp: {method.name}',
                'message': f'Tỷ lệ thành công chỉ {method.success_rate}%',
                'created_at': timezone.now(),
                'method': method,
                'severity': 'medium'
            })
        
        # Phát hiện phương pháp lâu không sử dụng
        inactive_methods = PredictionMethodBtl.objects.filter(
            last_used_at__lt=timezone.now() - timedelta(days=7),
            is_active=True
        )
        
        for method in inactive_methods:
            alerts.append({
                'type': 'info',
                'title': f'Lâu không sử dụng: {method.name}',
                'message': f'Không sử dụng từ {method.last_used_at.strftime("%d/%m/%Y") if method.last_used_at else "N/A"}',
                'created_at': timezone.now(),
                'method': method,
                'severity': 'low'
            })
        
        # Thống kê cảnh báo
        stats = {
            'total_alerts': len(alerts),
            'high_priority': len([a for a in alerts if a['severity'] == 'high']),
            'medium_priority': len([a for a in alerts if a['severity'] == 'medium']),
            'low_priority': len([a for a in alerts if a['severity'] == 'low']),
        }
        
        context.update({
            'alerts': sorted(alerts, key=lambda x: x['created_at'], reverse=True),
            'stats': stats,
        })
        
        return context
