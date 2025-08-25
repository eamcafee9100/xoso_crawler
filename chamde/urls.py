from django.urls import path
from . import views

app_name = 'chamde'

urlpatterns = [
    # Trang chủ phân tích chạm
    path('', views.ChamDashboardView.as_view(), name='cham_dashboard'),
    
    # Phân tích chi tiết
    path('phan-tich/', views.ChamAnalysisView.as_view(), name='cham_analysis'),
    path('phan-tich/<str:cham_type>/<str:cham_value>/', views.ChamDetailView.as_view(), name='cham_detail'),
    
    # Thống kê và theo dõi
    path('thong-ke/', views.ChamStatisticsView.as_view(), name='cham_statistics'),
    path('theo-doi/', views.ChamTrackingView.as_view(), name='cham_tracking'),
    
    # Dự đoán và gợi ý
    path('du-doan/', views.ChamPredictionView.as_view(), name='cham_prediction'),
    path('goi-y/', views.ChamSuggestionView.as_view(), name='cham_suggestion'),
    
    # Báo cáo
    path('bao-cao/', views.ChamReportView.as_view(), name='cham_report'),
    path('bao-cao/tuan/', views.WeeklyReportView.as_view(), name='weekly_report'),
    path('bao-cao/thang/', views.MonthlyReportView.as_view(), name='monthly_report'),
    
    # Các mô hình chạm
    path('dau/', views.ChamDauListView.as_view(), name='cham_dau_list'),
    path('duoi/', views.ChamDuoiListView.as_view(), name='cham_duoi_list'),
    
    # Phương pháp cầu chạm
    path('cau-cham-1/', views.CauCham1View.as_view(), name='cau_cham_1'),
    path('cau-cham-2/', views.CauCham2View.as_view(), name='cau_cham_2'),
    
    # Mẫu quả trám
    path('qua-tram/', views.QuaTramPatternView.as_view(), name='qua_tram_pattern'),
    path('qua-tram/<int:pk>/', views.QuaTramDetailView.as_view(), name='qua_tram_detail'),
    
    path('save-prediction/', views.SavePredictionView.as_view(), name='save_prediction'),
    
    # API endpoints cho AJAX requests
    path('api/cham/statistics/', views.cham_statistics_api, name='cham_statistics_api'),
    path('api/cham/prediction/', views.cham_prediction_api, name='cham_prediction_api'),
]