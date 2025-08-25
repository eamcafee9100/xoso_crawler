"""
URL configuration for xoso_crawler project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

# from debug_toolbar.toolbar import debug_toolbar_urls  # Disabled for testing
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from django.views.generic import RedirectView

from django.views.generic import TemplateView
from results.api import views as api_views
from results.api.views import (
    cache_refresh_api,
    daily_analysis_api,
    ensemble_analysis_api,
    method_details_api,
)
from results.views import (
    BachThuLoMethodDetailView,
    BachThuLoMethodListView,
    BachThuLoReportView,
    BachThuLoStatisticsView,
    BachThuLoView,
    BachThuPredictionResultView,
    BachThuPredictionView,
    CombinedAnalysisView,
    CrawlThang4View,
    ImprovedCombinedAnalysisView,
    NumberDetailAnalysisView,
    NumberFrequencyApiView,
    NumberFrequencyHeatmapView,
    NumberFrequencyStatsBulkDeleteView,
    NumberFrequencyStatsBulkImportView,
    NumberFrequencyStatsCreateView,
    NumberFrequencyStatsDeleteView,
    NumberFrequencyStatsExportView,
    NumberFrequencyStatsListView,
    NumberFrequencyStatsSyncView,
    NumberFrequencyStatsUpdateView,
    NumberFrequencyView,
    PredictionModelListView,
    PredictionPerformanceReportView,
    StateAnalysisListView,
    crawl_xsmb_view,
    daily_prediction_analysis_view,
    dan_de_dac_biet_report,
    day_predictions_api,
    get_2_digit_numbers,
    history_view,
    lokhung2ngay,
    method_comparison_view,
    method_correlation_view,
    model_performance,
    monthly_report_allprize_view,
    monthly_report_btl_view,
    monthly_report_view,
    nhap_ket_qua_textarea,
    predict_next_state,
    predict_view,
    report_btl_view,
    state_transition_chart,
)

api_patterns = [
    path(
        "daily-analysis/refresh/",
        api_views.refresh_daily_analysis,
        name="api_refresh_daily_analysis",
    ),
    path("cache/clear/", api_views.refresh_all_cache, name="api_refresh_all_cache"),
]

urlpatterns = [
    # Revolutionary Dashboard Home
    path("", TemplateView.as_view(template_name="revolutionary_dashboard.html"), name="home"),
    
    path("api/", include(api_patterns)),
    path("2-digit/", get_2_digit_numbers, name="get_2_digit_numbers"),
    path(
        "favicon.ico",
        RedirectView.as_view(url=settings.STATIC_URL + "favicon.ico", permanent=True),
    ),
    path("results/", include("results.urls")),
    path("soicau/", include("soicaubacnho.urls")),
    path("chamde/", include("chamde.urls")),
    path("lokhung/", include("lokhung.urls")),
    path("lottery-prediction/", include("lottery_prediction.urls")),
    path("pre-lokhung/", include("predictions_tracker.urls")),
    path(
        "analytic-frequence/", include("analytic_frequence.urls")
    ),  # Add analytic_frequence app
    path("admin/", admin.site.urls),
    path("crawl-thang-4/", CrawlThang4View.as_view(), name="crawl_thang_4"),
    path("predict/", predict_view, name="predict_xs"),
    path("nhap-ket-qua-text/", nhap_ket_qua_textarea, name="nhap_ket_qua_textarea"),
    path("history-view/", history_view, name="history-view"),
    path(
        "dan-de-dac-biet/bao-cao/",
        dan_de_dac_biet_report,
        name="dan_de_dac_biet_report",
    ),
    path(
        "combined-analysis/", CombinedAnalysisView.as_view(), name="combined_analysis"
    ),
    path(
        "improved-combined-analysis/",
        ImprovedCombinedAnalysisView.as_view(),
        name="improved_combined_analysis",
    ),
    path(
        "improved-prediction-performance-report/",
        PredictionPerformanceReportView.as_view(),
        name="improved_prediction_performance_report",
    ),
    path("calc_btl/", BachThuLoView.as_view(), name="calc_btl"),
    path("update-xsmb/", crawl_xsmb_view, name="crawl_xsmb_view"),
    path("lokhung2day/", lokhung2ngay, name="lokhung2day"),
    path("report_btl/", BachThuLoReportView.as_view(), name="report_btl"),
    path("monthly-report/", monthly_report_view, name="monthly_report"),
    path("monthly-report-btl/", monthly_report_btl_view, name="monthly_report_btl"),
    path(
        "monthly-report-allprize/",
        monthly_report_allprize_view,
        name="monthly_report_allprize",
    ),
    path("btl_method", BachThuLoMethodListView.as_view(), name="btl_method"),
    path(
        "btl_method/<int:pk>/",
        BachThuLoMethodDetailView.as_view(),
        name="btl_method_detail",
    ),
    path("btl_statistics/", BachThuLoStatisticsView.as_view(), name="btl_statistics"),
    path("prediction/", BachThuPredictionView.as_view(), name="prediction_btl"),
    path(
        "prediction/results/",
        BachThuPredictionResultView.as_view(),
        name="prediction_btl_results",
    ),
    path("api/day-predictions/", day_predictions_api, name="day_predictions_api"),
    # path('analysis/daily/', daily_prediction_analysis_view, name='daily_analysis'),
    path("btl-report/", report_btl_view, name="btl_report"),
    path("btl-report/<int:year>/<int:month>/", report_btl_view, name="btl_report"),
    path(
        "btl-method-comparison/", method_comparison_view, name="btl_method_comparison"
    ),
    path(
        "btl_method_correlation/",
        method_correlation_view,
        name="btl_method_correlation",
    ),
    path("number-frequency/", NumberFrequencyView.as_view(), name="number_frequency"),
    path(
        "number-frequency/api/",
        NumberFrequencyApiView.as_view(),
        name="number_frequency_api",
    ),
    path(
        "number-frequency/heatmap/",
        NumberFrequencyHeatmapView.as_view(),
        name="number_frequency_heatmap",
    ),
    # Daily prediction analysis
    path(
        "daily-analysis/",
        daily_prediction_analysis_view,
        name="daily_prediction_analysis",
    ),
    # API endpoints
    path(
        "api/",
        include(
            [
                path(
                    "methods/<int:method_id>/details/",
                    method_details_api,
                    name="method_details_api",
                ),
                # Add other API endpoints here
            ]
        ),
    ),
    # API endpoints
    path("api/daily-analysis/", daily_analysis_api, name="daily_analysis_api"),
    path("api/ensemble-analysis/", ensemble_analysis_api, name="ensemble_analysis_api"),
    path("api/cache-refresh/", cache_refresh_api, name="cache_refresh_api"),
    path("state-analysis", StateAnalysisListView.as_view(), name="state_analysis_list"),
    path("models/", PredictionModelListView.as_view(), name="model_list"),
    path(
        "models/<int:model_id>/performance/",
        model_performance,
        name="model_performance",
    ),
    path("api/predict/", predict_next_state, name="predict"),
    path(
        "api/transition-chart/", state_transition_chart, name="state_transition_chart"
    ),
    path(
        "frequency-stats/bulk-delete/",
        NumberFrequencyStatsBulkDeleteView.as_view(),
        name="number_frequency_stats_bulk_delete",
    ),
    path(
        "number-frequency-stats/",
        NumberFrequencyStatsListView.as_view(),
        name="number_frequency_stats_list",
    ),
    path(
        "number-frequency-stats/create/",
        NumberFrequencyStatsCreateView.as_view(),
        name="number_frequency_stats_create",
    ),
    path(
        "number-frequency-stats/<int:pk>/update/",
        NumberFrequencyStatsUpdateView.as_view(),
        name="number_frequency_stats_update",
    ),
    path(
        "number-frequency-stats/<int:pk>/delete/",
        NumberFrequencyStatsDeleteView.as_view(),
        name="number_frequency_stats_delete",
    ),
    path(
        "number-frequency-stats/import/",
        NumberFrequencyStatsBulkImportView.as_view(),
        name="number_frequency_stats_bulk_import",
    ),
    path(
        "number-frequency-stats/export/",
        NumberFrequencyStatsExportView.as_view(),
        name="number_frequency_stats_export",
    ),
    path(
        "number-frequency-stats/sync/",
        NumberFrequencyStatsSyncView.as_view(),
        name="number_frequency_stats_sync",
    ),
    # New advanced analysis URLs
    path(
        "results/number-analysis/",
        NumberDetailAnalysisView.as_view(),
        name="number_detail_analysis",
    ),
    path(
        "results/frequency-heatmap/",
        NumberFrequencyHeatmapView.as_view(),
        name="number_frequency_heatmap",
    ),
]  # + debug_toolbar_urls()  # Disabled for testing
