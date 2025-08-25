from django.urls import path
from .views_dir import api_monitoring_dashboard
from .views_dir import api_production_monitoring
from .views_dir import api_optimization_testing
from predictions_tracker.core.services.IntelligentPredictionAPI import (
    IntelligentPredictionAPI,
)
from predictions_tracker.views_dir.api_method_analysis_by_date_v2 import (
    api_ketqua_available_dates,
    api_ketqua_by_date,
    api_method_analysis_by_date_v2,
)
from predictions_tracker.views_dir.api_cyclical_prediction_by_date_v3 import (
    api_cyclical_prediction_by_date_v3, api_cyclical_validation, api_validation_summary, api_optimize_parameters, api_optimization_history,
    
)
from predictions_tracker.views_dir.test_ml_train import test_ml_train

from . import views
from django.views.generic import TemplateView

app_name = "predictions_tracker"

urlpatterns = [
    # Production Monitoring APIs
    path('api/production-dashboard/', 
         api_production_monitoring.api_production_dashboard, 
         name='api_production_dashboard'),
         
    path('api/system-health-check/', 
         api_production_monitoring.api_system_health_check, 
         name='api_system_health_check'),
         
    path('api/resolve-production-alert/', 
         api_production_monitoring.api_resolve_production_alert, 
         name='api_resolve_production_alert'),
         
    path('api/production-performance-metrics/', 
         api_production_monitoring.api_performance_metrics, 
         name='api_production_performance_metrics'),
         
    # Production Dashboard View
    path('production-monitoring/', 
         TemplateView.as_view(template_name='predictions_tracker/production_monitoring.html'),
         name='production_monitoring_dashboard'),
    # Monitoring & Dashboard APIs
    path('api/monitoring-dashboard/', 
         api_monitoring_dashboard.api_monitoring_dashboard, 
         name='api_monitoring_dashboard'),
         
    path('api/system-health/', 
         api_monitoring_dashboard.api_system_health, 
         name='api_system_health'),
         
    path('api/resolve-alert/', 
         api_monitoring_dashboard.api_resolve_alert, 
         name='api_resolve_alert'),
         
    path('api/performance-metrics/', 
         api_monitoring_dashboard.api_performance_metrics, 
         name='api_performance_metrics'),
         
    # Dashboard Views
    path('monitoring/', 
         TemplateView.as_view(template_name='predictions_tracker/monitoring_dashboard.html'),
         name='monitoring_dashboard'),
    # Dashboard
    path("", views.dashboard, name="pre_tracker_dashboard"),
    path("test-ml-train/", test_ml_train, name="test_ml_train"),
    path(
        "monthly-report/",
        views.MonthlyPredictionReportView.as_view(),
        name="pre_tracker_monthly_report",
    ),
    path(
        "reload-methods/",
        views.reload_prediction_methods_view,
        name="reload_prediction_methods",
    ),
    path(
        "method-management/action/",
        views.method_management_action,
        name="method_management_action",
    ),  # Cycle Management
    # ✅ THÊM API CHO PATTERN ANALYSIS
    path("api/pattern-analysis/", views.api_pattern_analysis, name="api_pattern_analysis"), 
    path("api/method-analysis-by-date/", views.api_method_analysis_by_date, name="api_method_analysis_by_date"),
    path(
        "api/test-method-analysis/",
        views.api_test_method_analysis,
        name="api_test_method_analysis",
    ),
    path('api/cyclical-prediction/', 
         api_cyclical_prediction_by_date_v3, 
         name='api_cyclical_prediction_v3'),
     # Cyclical Intelligence API
    path('api/cyclical-prediction/', 
         api_cyclical_prediction_by_date_v3, 
         name='api_cyclical_prediction_v3'),
         
    # Validation APIs  
    path('api/cyclical-validation/', 
         api_cyclical_validation, 
         name='api_cyclical_validation'),
         
    path('api/validation-summary/', 
         api_validation_summary, 
         name='api_validation_summary'),
    path('api/optimize-parameters/', 
         api_optimize_parameters, 
         name='api_optimize_parameters'),
         
    path('api/optimization-history/', 
         api_optimization_history, 
         name='api_optimization_history'),
         
    # A/B Testing APIs
    path('api/ab-test/create/', 
         api_optimization_testing.api_create_ab_test, 
         name='api_create_ab_test'),
         
    path('api/ab-test/execute/', 
         api_optimization_testing.api_execute_ab_test, 
         name='api_execute_ab_test'),
         
    path('api/ab-test/results/', 
         api_optimization_testing.api_get_ab_test_results, 
         name='api_get_ab_test_results'),
         
    path('api/ab-test/compare/', 
         api_optimization_testing.api_compare_ab_test_variants, 
         name='api_compare_ab_test_variants'),
         
    path('api/ab-test/conclude/', 
         api_optimization_testing.api_conclude_ab_test, 
         name='api_conclude_ab_test'),
    
    path(
        "api/method-analysis-v2/",
        api_method_analysis_by_date_v2,
        name="api_method_analysis_v2",
    ),
    # ✅ API để lấy kết quả xổ số theo ngày
    path("api/ketqua/<str:date_str>/", api_ketqua_by_date, name="api_ketqua_by_date"),
    # ✅ API để lấy danh sách ngày có kết quả
    path(
        "api/ketqua/available-dates/",
        api_ketqua_available_dates,
        name="api_ketqua_available_dates",
    ),
    path(
        "api/intelligent-predictions/",
        IntelligentPredictionAPI.as_view(),
        name="intelligent-predictions",
    ),
    path("cycles/", views.cycles_list, name="cycles_list"),
    path("cycles/create/", views.cycle_create, name="cycle_create"),
    path("cycles/<int:cycle_id>/", views.cycle_detail, name="cycle_detail"),
    # Session Management
    path("sessions/<int:session_id>/", views.session_detail, name="session_detail"),
    path(
        "cycles/<int:cycle_id>/create-session/",
        views.create_session,
        name="create_session",
    ),
    # Evaluation
    path("evaluations/", views.evaluation_list, name="evaluation_list"),
    path(
        "sessions/<int:session_id>/run-evaluation/",
        views.run_evaluation,
        name="run_evaluation",
    ),
    # Analytics
    path("analytics/", views.analytics_dashboard, name="analytics_dashboard"),
    # API Endpoints
    path(
        "api/cycles/<int:cycle_id>/summary/",
        views.api_cycle_summary,
        name="api_cycle_summary",
    ),
    path(
        "api/cycles/<int:cycle_id>/comparison/",
        views.api_method_comparison,
        name="api_method_comparison",
    ),
    path(
        "api/sessions/<int:session_id>/chart-data/",
        views.api_session_chart_data,
        name="api_session_chart_data",
    ),
    path(
        "api/tracking/update-status/",
        views.api_update_tracking_status,
        name="api_update_tracking_status",
    ),
    # ✅ THÊM URL MỚI CHO DAY DETAIL API
    path(
        "api/day-detail/<int:year>/<int:month>/<int:day>/",
        views.api_day_detail,
        name="api_day_detail",
    ),
    # Enhanced ML APIs
    path(
        "api/enhanced-ml-prediction/",
        views.api_enhanced_ml_prediction,
        name="api_enhanced_ml_prediction",
    ),
    path("api/retrain-models/", views.api_retrain_models, name="api_retrain_models"),
    # ✅ THÊM ML MODELS APIs
    path("api/train-ml-models/", views.api_train_ml_models, name="api_train_ml_models"),
    path(
        "api/ml-models-status/", views.api_ml_models_status, name="api_ml_models_status"
    ),
    # ✅ COMPREHENSIVE HISTORICAL DATA API
    path(
        "api/comprehensive-historical-data/",
        views.api_comprehensive_historical_data,
        name="api_comprehensive_historical_data",
    ),
    # ✅ METHOD-SPECIFIC HISTORICAL API
    path(
        "api/method/<int:method_id>/historical-summary/",
        views.api_method_historical_summary,
        name="api_method_historical_summary",
    ),
]
