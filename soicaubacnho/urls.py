# urls.py
from django.urls import path
from .views import SoiCauBacNhoView, SoiCauBacNhoHistoryView, SoiCauBacNhoAPIView, OptimizeWeightsView,RunHistoricalPredictionsView, dashboard, predict_view, prediction_results, compare_versions, version_config, run_analyzer, update_prediction_results, get_config,get_results

urlpatterns = [
    path('', SoiCauBacNhoView.as_view(), name='soi_cau_bac_nho'),
    path('history/', SoiCauBacNhoHistoryView.as_view(), name='soi_cau_bac_nho_history'),
    path('api/soi-cau-bac-nho/predictions/', SoiCauBacNhoAPIView.get_predictions, name='api_soi_cau_predictions'),
    path('api/soi-cau-bac-nho/update-results/', SoiCauBacNhoAPIView.update_results, name='api_update_results'),
    path('api/soi-cau-bac-nho/discover-patterns/', SoiCauBacNhoAPIView.discover_patterns, name='api_discover_patterns'),
    # Thêm vào urls.py
    path('run-historical/', RunHistoricalPredictionsView.as_view(), name='run_historical'),
    path('optimize-weights/', OptimizeWeightsView.as_view(), name='optimize_weights'),
    path('dashboard', dashboard, name='dashboard'),
    path('predict/', predict_view, name='predict_view'),
    path('prediction-results/<int:pk>/', prediction_results, name='prediction_results'),
    path('compare-versions/', compare_versions, name='compare_versions'),
    path('version-config/', version_config, name='version_config'),
    
    # API endpoints
    path('api/run-analyzer/', run_analyzer, name='run_analyzer'),
    path('api/get-results/', get_results, name='get_results'),
    path('api/update-results/', update_prediction_results, name='update_results'),
    path('api/get-config/<int:pk>/', get_config, name='get_config'),
]