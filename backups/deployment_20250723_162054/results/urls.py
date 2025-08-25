from django.urls import path
from . import views
from .views import (
    StateAnalysisListView,
    PredictionModelListView,
    predict_next_state,
    model_performance,
    state_transition_chart
)
from results.views_manager.enhanced_predict_view import EnhancedPredictView
app_name = 'results'

urlpatterns = [
    # State Analysis URLs
    path("enhanced-predict/", EnhancedPredictView.as_view() , name="enhanced_predict_xs"),

    path('state-analysis/', StateAnalysisListView.as_view(), name='state_analysis_list'),
    path('prediction-models/', PredictionModelListView.as_view(), name='model_list'),
    path('models/<int:model_id>/performance/', model_performance, name='model_performance'),
    path('api/predict/', predict_next_state, name='predict'),
    path('api/transition-chart/', state_transition_chart, name='transition_chart'),

]