from django.urls import path
from django.views.generic import TemplateView

# PHASE 2A: Ensemble ML API imports
from predictions_tracker.views_dir.api_ensemble_ml_v2a import (
    api_bayesian_optimization,
    api_ensemble_prediction,
    api_ensemble_training,
)

from . import views
from .api.views import (
    ActualResultsView,
    ModelPerformanceView,
    PredictionAPIView,
    RetrainModelView,
)

urlpatterns = [
    path("api/predict/", PredictionAPIView.as_view()),
    path("api/model-performance/", ModelPerformanceView.as_view()),
    path("api/retrain/", RetrainModelView.as_view()),
    path("api/actual-results/", ActualResultsView.as_view()),
    # PHASE 2A: Ensemble ML API endpoints
    path("api/ml/ensemble-training/", api_ensemble_training, name="ensemble_training"),
    path(
        "api/ml/bayesian-optimization/",
        api_bayesian_optimization,
        name="bayesian_optimization",
    ),
    path(
        "api/ml/ensemble-prediction/",
        api_ensemble_prediction,
        name="ensemble_prediction",
    ),
    # Frontend Views
    path(
        "predictions/",
        views.index,
        name="predictions",
    ),
    path(
        "performance/",
        TemplateView.as_view(template_name="performance/index.html"),
        name="model-performance",
    ),
    path(
        "retrain/",
        TemplateView.as_view(template_name="retrain/index.html"),
        name="retrain-model",
    ),
]
