from django.urls import path

from lokhung.views_folder.btl_views import (
    AlertListView,
    AnalysisListView,
    DailyFrequencyReportView,
    DashboardView,
    ExportReportView,
    FrameListView,
    MethodComparisonReportView,
    MethodDetailView,
    MethodListView,
    MethodStatsAPIView,
    PerformanceSummaryReportView,
    PredictionListView,
    ReportListView,
    ReportTrendAnalysisView,
)

from . import views

app_name = "lokhung"

urlpatterns = [
    # Dashboard
    path("", views.dashboard, name="dashboard"),
    # Phương pháp tính toán
    path("phuong-phap/", views.phuong_phap_list, name="phuong_phap_list"),
    path("phuong-phap/<int:pk>/", views.phuong_phap_detail, name="phuong_phap_detail"),
    path("phuong-phap/tao/", views.phuong_phap_create, name="phuong_phap_create"),
    path("phuong-phap/<int:pk>/sua/", views.phuong_phap_edit, name="phuong_phap_edit"),
    path(
        "phuong-phap/<int:pk>/xoa/", views.phuong_phap_delete, name="phuong_phap_delete"
    ),
    # Dự đoán
    path("du-doan/", views.du_doan_list, name="du_doan_list"),
    path("du-doan/<int:pk>/", views.du_doan_detail, name="du_doan_detail"),
    path("du-doan/tao/", views.du_doan_create, name="du_doan_create"),
    path("du-doan/<int:pk>/sua/", views.du_doan_edit, name="du_doan_edit"),
    path(
        "du-doan/<int:pk>/kiem-tra/",
        views.du_doan_check_result,
        name="du_doan_check_result",
    ),
    # Lô khung
    path("lo-khung/", views.lo_khung_list, name="lo_khung_list"),
    path("lo-khung/<int:pk>/", views.lo_khung_detail, name="lo_khung_detail"),
    path("lo-khung/tao/", views.lo_khung_create, name="lo_khung_create"),
    path("lo-khung/<int:pk>/sua/", views.lo_khung_edit, name="lo_khung_edit"),
    # Báo cáo hiệu quả
    path("bao-cao/", views.bao_cao_list, name="bao_cao_list"),
    path("bao-cao/<int:pk>/", views.bao_cao_detail, name="bao_cao_detail"),
    path("bao-cao/tao/", views.bao_cao_create, name="bao_cao_create"),
    path("bao-cao/thang/", views.monthly_performance_report, name="monthly_performance_report"),
    # Phân tích số liệu
    path("phan-tich/", views.phan_tich_list, name="phan_tich_list"),
    path("phan-tich/<int:pk>/", views.phan_tich_detail, name="phan_tich_detail"),
    path(
        "phan-tich/tao-tu-dong/",
        views.phan_tich_create_auto,
        name="phan_tich_create_auto",
    ),
    # Cảnh báo hiệu quả
    path("canh-bao/", views.canh_bao_list, name="canh_bao_list"),
    path("canh-bao/<int:pk>/", views.canh_bao_detail, name="canh_bao_detail"),
    path(
        "canh-bao/<int:pk>/xu-ly/",
        views.canh_bao_mark_resolved,
        name="canh_bao_mark_resolved",
    ),
    # API endpoints
    path(
        "api/phuong-phap/<int:pk>/thong-ke/",
        views.api_phuong_phap_stats,
        name="api_phuong_phap_stats",
    ),
    path(
        "api/kiem-tra-tat-ca-du-doan/",
        views.api_check_all_predictions,
        name="api_check_all_predictions",
    ),
    # Export
    path("export/du-doan/", views.export_du_doan_excel, name="export_du_doan_excel"),
    path("btl/", DashboardView.as_view(), name="btl_dashboard"),
    # Methods
    path("methods/", MethodListView.as_view(), name="method_list"),
    path("methods/<int:pk>/", MethodDetailView.as_view(), name="method_detail"),
    # Reports
    path("reports/", ReportListView.as_view(), name="report_list"),
    path(
        "reports/performance-summary/",
        PerformanceSummaryReportView.as_view(),
        name="report_performance_summary",
    ),
    path(
        "reports/method-comparison/",
        MethodComparisonReportView.as_view(),
        name="report_method_comparison",
    ),
    path(
        "reports/daily-frequency/",
        DailyFrequencyReportView.as_view(),
        name="report_daily_frequency",
    ),
    path(
        "reports/trend-analysis/",
        ReportTrendAnalysisView.as_view(),
        name="report_trend_analysis",
    ),
    # API endpoints
    path("api/method-stats/", MethodStatsAPIView.as_view(), name="api_method_stats"),
    path("api/export-report/", ExportReportView.as_view(), name="api_export_report"),
    # BTL Feature URLs (thay thế placeholder URLs)
    path("predictions/", PredictionListView.as_view(), name="btl_prediction_list"),
    path("frames/", FrameListView.as_view(), name="btl_frame_list"),
    path("analysis/", AnalysisListView.as_view(), name="btl_analysis_list"),
    path("alerts/", AlertListView.as_view(), name="btl_alert_list"),
]
