from django.urls import path

from results.views_manager.enhanced_predict_view import EnhancedPredictView

from . import views
from .enhanced_urls import urlpatterns as enhanced_urls
from .views import (
    PredictionModelListView,
    StateAnalysisListView,
    model_performance,
    predict_next_state,
    state_transition_chart,
)

app_name = "results"

urlpatterns = [
    # State Analysis URLs
    path(
        "enhanced-predict/", EnhancedPredictView.as_view(), name="enhanced_predict_xs"
    ),
    path(
        "state-analysis/", StateAnalysisListView.as_view(), name="state_analysis_list"
    ),
    path("prediction-models/", PredictionModelListView.as_view(), name="model_list"),
    path(
        "models/<int:model_id>/performance/",
        model_performance,
        name="model_performance",
    ),
    path("api/predict/", predict_next_state, name="predict"),
    path("api/transition-chart/", state_transition_chart, name="transition_chart"),
]
# Append enhanced system URLs
urlpatterns += enhanced_urls
