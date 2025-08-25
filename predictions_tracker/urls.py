from django.urls import include, path
from django.views.generic import TemplateView

from predictions_tracker.core.services.IntelligentPredictionAPI import (
    IntelligentPredictionAPI,
)
from predictions_tracker.views_dir.api_cyclical_prediction_by_date_v3 import (
    api_cyclical_prediction_by_date_v3,
    api_cyclical_validation,
    api_optimization_history,
    api_optimize_parameters,
    api_validation_summary,
)
from predictions_tracker.views_dir.api_ensemble_ml_v2a import (
    api_bayesian_optimization,
    api_ensemble_prediction,
    api_ensemble_training,
)
from predictions_tracker.views_dir.api_method_analysis_by_date_v2 import (
    api_ketqua_available_dates,
    api_ketqua_by_date,
    api_method_analysis_by_date_v2,
)
from predictions_tracker.views_dir.api_minimal_test import (
    api_method_analysis_by_date_v2_minimal,
)
from predictions_tracker.views_dir.api_method_analysis_v3_integration import (
    api_method_analysis_by_date_v3_enhanced,
    api_method_analysis_comparison,
)

from predictions_tracker.views_dir.api_simple_test import api_simple_test
from predictions_tracker.views_dir.test_ml_train import test_ml_train

from . import views

from .views_dir import (
    api_monitoring_dashboard,
    api_optimization_testing,
    api_production_monitoring,
)

# Simple Test Views for Debugging
from .views_dir.enhanced_analyzer_simple_views import (
    analysis_reports_center_simple,
    enhanced_analyzer_dashboard_simple,
    get_adaptive_predictions_simple,
    run_enhanced_analysis_simple,
    validate_predictions_simple,
)

# Enhanced Deep Frequency Analyzer Views
from .views_dir.enhanced_frequency_analyzer_views import (
    analysis_reports_center,
    cyclical_analysis_workstation,
    enhanced_analyzer_dashboard,
    export_analysis_report,
    get_adaptive_predictions,
    get_performance_trends,
    run_enhanced_analysis,
    validate_predictions,
)

app_name = "predictions_tracker"

urlpatterns = [
    # 🧠 ENHANCED DEEP FREQUENCY ANALYZER
    path(
        "enhanced-analyzer/",
        enhanced_analyzer_dashboard,
        name="enhanced_analyzer_dashboard",
    ),
    path(
        "enhanced-analyzer-cyclical/",
        cyclical_analysis_workstation,
        name="cyclical_analysis_workstation",
    ),
    path(
        "enhanced-analyzer/run-analysis/",
        run_enhanced_analysis,
        name="run_enhanced_analysis",
    ),
    path(
        "enhanced-analyzer/validate-predictions/",
        validate_predictions,
        name="validate_predictions",
    ),
    path(
        "enhanced-analyzer/adaptive-predictions/",
        get_adaptive_predictions,
        name="get_adaptive_predictions",
    ),
    path(
        "enhanced-analyzer/reports/",
        analysis_reports_center,
        name="analysis_reports_center",
    ),
    path(
        "enhanced-analyzer/export-report/",
        export_analysis_report,
        name="export_analysis_report",
    ),
    path(
        "enhanced-analyzer/performance-trends/",
        get_performance_trends,
        name="get_performance_trends",
    ),
    # 🧪 TEST VERSIONS (Simple Mock Data)
    path(
        "enhanced-analyzer-test/",
        enhanced_analyzer_dashboard_simple,
        name="enhanced_analyzer_dashboard_test",
    ),
    path(
        "enhanced-analyzer-test/run-analysis/",
        run_enhanced_analysis_simple,
        name="run_enhanced_analysis_test",
    ),
    path(
        "enhanced-analyzer-test/validate-predictions/",
        validate_predictions_simple,
        name="validate_predictions_test",
    ),
    path(
        "enhanced-analyzer-test/adaptive-predictions/",
        get_adaptive_predictions_simple,
        name="get_adaptive_predictions_test",
    ),
    path(
        "enhanced-analyzer-test/reports/",
        analysis_reports_center_simple,
        name="analysis_reports_center_test",
    ),
    # 🚀 PHASE 2A: ML ENSEMBLE & OPTIMIZATION APIs
    path(
        "api/ensemble-ml-v2a/test/",
        api_simple_test,
        name="api_simple_test",
    ),
    path(
        "api/ensemble-ml-v2a/train/",
        api_ensemble_training,
        name="api_ensemble_training",
    ),
    path(
        "api/ensemble-ml-v2a/optimize/",
        api_bayesian_optimization,
        name="api_bayesian_optimization",
    ),
    path(
        "api/ensemble-ml-v2a/predict/",
        api_ensemble_prediction,
        name="api_ensemble_prediction",
    ),
    # Production Monitoring APIs
    path(
        "api/production-dashboard/",
        api_production_monitoring.api_production_dashboard,
        name="api_production_dashboard",
    ),
    path(
        "api/system-health-check/",
        api_production_monitoring.api_system_health_check,
        name="api_system_health_check",
    ),
    path(
        "api/resolve-production-alert/",
        api_production_monitoring.api_resolve_production_alert,
        name="api_resolve_production_alert",
    ),
    path(
        "api/production-performance-metrics/",
        api_production_monitoring.api_performance_metrics,
        name="api_production_performance_metrics",
    ),
    # Production Dashboard View
    path(
        "production-monitoring/",
        TemplateView.as_view(
            template_name="predictions_tracker/production_monitoring.html"
        ),
        name="production_monitoring_dashboard",
    ),
    # Monitoring & Dashboard APIs
    path(
        "api/monitoring-dashboard/",
        api_monitoring_dashboard.api_monitoring_dashboard,
        name="api_monitoring_dashboard",
    ),
    path(
        "api/system-health/",
        api_monitoring_dashboard.api_system_health,
        name="api_system_health",
    ),
    path(
        "api/resolve-alert/",
        api_monitoring_dashboard.api_resolve_alert,
        name="api_resolve_alert",
    ),
    path(
        "api/performance-metrics/",
        api_monitoring_dashboard.api_performance_metrics,
        name="api_performance_metrics",
    ),
    # Dashboard Views
    path(
        "monitoring/",
        TemplateView.as_view(
            template_name="predictions_tracker/monitoring_dashboard.html"
        ),
        name="monitoring_dashboard",
    ),
    # Dashboard
    path("", views.dashboard, name="pre_tracker_dashboard"),
    path(
        "test/",
        TemplateView.as_view(template_name="predictions_tracker/test_template.html"),
        name="test_template",
    ),
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
    path(
        "api/pattern-analysis/", views.api_pattern_analysis, name="api_pattern_analysis"
    ),
    path(
        "api/method-analysis-by-date/",
        views.api_method_analysis_by_date,
        name="api_method_analysis_by_date",
    ),
    path(
        "api/test-method-analysis/",
        views.api_test_method_analysis,
        name="api_test_method_analysis",
    ),
    path(
        "api/cyclical-prediction-v3/",
        api_cyclical_prediction_by_date_v3,
        name="api_cyclical_prediction_v3",
    ),
    # Validation APIs
    path(
        "api/cyclical-validation/",
        api_cyclical_validation,
        name="api_cyclical_validation",
    ),
    path(
        "api/validation-summary/", api_validation_summary, name="api_validation_summary"
    ),
    path(
        "api/optimize-parameters/",
        api_optimize_parameters,
        name="api_optimize_parameters",
    ),
    path(
        "api/optimization-history/",
        api_optimization_history,
        name="api_optimization_history",
    ),
    # A/B Testing APIs
    path(
        "api/ab-test/create/",
        api_optimization_testing.api_create_ab_test,
        name="api_create_ab_test",
    ),
    path(
        "api/ab-test/execute/",
        api_optimization_testing.api_execute_ab_test,
        name="api_execute_ab_test",
    ),
    path(
        "api/ab-test/results/",
        api_optimization_testing.api_get_ab_test_results,
        name="api_get_ab_test_results",
    ),
    path(
        "api/ab-test/compare/",
        api_optimization_testing.api_compare_ab_test_variants,
        name="api_compare_ab_test_variants",
    ),
    path(
        "api/ab-test/conclude/",
        api_optimization_testing.api_conclude_ab_test,
        name="api_conclude_ab_test",
    ),
    path(
        "api/method-analysis-v2/",
        api_method_analysis_by_date_v2,
        name="api_method_analysis_v2",
    ),
    path(
        "api/method-analysis-minimal/",
        api_method_analysis_by_date_v2_minimal,
        name="api_method_analysis_minimal",
    ),
    # 🚀 V3 Enhanced Method Analysis APIs
    path(
        "api/method-analysis-v3-enhanced/",
        api_method_analysis_by_date_v3_enhanced,
        name="api_method_analysis_v3_enhanced",
    ),
    path(
        "api/method-analysis-comparison/",
        api_method_analysis_comparison,
        name="api_method_analysis_comparison",
    ),
    # ✅ API TEST đơn giản để kiểm tra function
    path(
        "api/simple-test/",
        api_simple_test,
        name="api_simple_test",
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
    # ✅ MINIMAL TEST FOR DEBUGGING
    path(
        "minimal-test/",
        TemplateView.as_view(template_name="predictions_tracker/minimal_test.html"),
        name="minimal_test",
    ),
    # ✅ DEBUG TEST FOR TEMPLATE
    path(
        "debug-test/",
        TemplateView.as_view(template_name="predictions_tracker/debug_test.html"),
        name="debug_test",
    ),
    
    
    
]
