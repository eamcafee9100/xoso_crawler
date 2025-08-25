#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
🎯 ANALYTIC FREQUENCE URLs: URL Configuration
Defines URL patterns for the advanced frequency analysis API
"""

from django.urls import include, path

from .template_views import (
    PredictionDashboardView,
    UltimatePredictionTemplateView,
    ajax_prediction_api,
    debug_date_analysis,
)
from .test_api_view import test_api_page
from .views import (  # API Views; Function-based views
    AdvancedFrequencyAnalysisAPIView,
    EnsembleMachineLearningAPIView,
    LotteryPredictionAPIView,
    MathematicalAnalysisAPIView,
    MetaLearningAPIView,
    NeuralNetworkAnalysisAPIView,
    NeuralRecognizerAPIView,
    NeuralTrainingAPIView,
    PredictionValidationAPIView,
    QuantumAnalysisAPIView,
    QuantumOptimizerAPIView,
    QuantumProcessingAPIView,
    QuantumProcessorAPIView,
    SystemHealthAPIView,
    UltimatePredictionAPIView,
    VisualizationDataAPIView,
    clear_cache,
    system_info,
)

app_name = "analytic_frequence"

# API URL patterns
api_urlpatterns = [
    # Root path - redirect to ultimate prediction
    path("", UltimatePredictionTemplateView.as_view(), name="root"),
    
    # Template Views
    path(
        "ultimate-prediction/",
        UltimatePredictionTemplateView.as_view(),
        name="ultimate_prediction_template",
    ),
    # Dashboard template
    path("dashboard/", PredictionDashboardView.as_view(), name="prediction_dashboard"),
    # AJAX API for real-time predictions
    path("ajax-prediction/", ajax_prediction_api, name="ajax_prediction_api"),
    # Debug view for date analysis
    path("debug-date/", debug_date_analysis, name="debug_date_analysis"),
    # Quantum Data Processor API
    path(
        "quantum-processor/",
        QuantumProcessorAPIView.as_view(),
        name="quantum-processor-list",
    ),
    path(
        "quantum-processor/<str:processor_id>/",
        QuantumProcessorAPIView.as_view(),
        name="quantum-processor-detail",
    ),
    path(
        "quantum-processing/",
        QuantumProcessingAPIView.as_view(),
        name="quantum-processing",
    ),
    # Neural Pattern Recognizer API
    path(
        "neural-recognizer/",
        NeuralRecognizerAPIView.as_view(),
        name="neural-recognizer-list",
    ),
    path(
        "neural-recognizer/<str:recognizer_id>/",
        NeuralRecognizerAPIView.as_view(),
        name="neural-recognizer-detail",
    ),
    path("neural-training/", NeuralTrainingAPIView.as_view(), name="neural-training"),
    # Quantum Optimizer API
    path(
        "quantum-optimizer/",
        QuantumOptimizerAPIView.as_view(),
        name="quantum-optimizer-list",
    ),
    path(
        "quantum-optimizer/<str:optimizer_id>/",
        QuantumOptimizerAPIView.as_view(),
        name="quantum-optimizer-detail",
    ),
    # Meta Learning API
    path("meta-learning/", MetaLearningAPIView.as_view(), name="meta-learning-list"),
    path(
        "meta-learning/<str:orchestrator_id>/",
        MetaLearningAPIView.as_view(),
        name="meta-learning-detail",
    ),
    # Advanced Frequency Analysis API
    path(
        "advanced-analysis/",
        AdvancedFrequencyAnalysisAPIView.as_view(),
        name="advanced-analysis-list",
    ),
    path(
        "advanced-analysis/<str:analysis_id>/",
        AdvancedFrequencyAnalysisAPIView.as_view(),
        name="advanced-analysis-detail",
    ),
    # Mathematical Analysis API
    path(
        "mathematical-analysis/",
        MathematicalAnalysisAPIView.as_view(),
        name="mathematical-analysis",
    ),
    # Neural Network Analysis API
    path(
        "neural-analysis/",
        NeuralNetworkAnalysisAPIView.as_view(),
        name="neural-analysis",
    ),
    # Ensemble Machine Learning API
    path(
        "ensemble-ml/",
        EnsembleMachineLearningAPIView.as_view(),
        name="ensemble-ml",
    ),
    # Quantum Analysis API
    path(
        "quantum-analysis/",
        QuantumAnalysisAPIView.as_view(),
        name="quantum-analysis",
    ),
    # Ultimate Prediction API
    path(
        "ultimate-prediction/",
        UltimatePredictionAPIView.as_view(),
        name="ultimate-prediction",
    ),
    # Lottery Prediction API
    path(
        "lottery-prediction/",
        LotteryPredictionAPIView.as_view(),
        name="lottery-prediction",
    ),
    path(
        "prediction-validation/",
        PredictionValidationAPIView.as_view(),
        name="prediction-validation",
    ),
    # Visualization API
    path(
        "visualization/", VisualizationDataAPIView.as_view(), name="visualization-data"
    ),
    # System Health and Status
    path("health/", SystemHealthAPIView.as_view(), name="system-health"),
    # Utility endpoints
    path("system-info/", system_info, name="system-info"),
    path("clear-cache/", clear_cache, name="clear-cache"),
]

# Main URL patterns
urlpatterns = [
    # API v1 endpoints
    path("api/v1/", include(api_urlpatterns)),
    # Backward compatibility (legacy endpoints)
    path("", include(api_urlpatterns)),
]

# Optional: Add API documentation patterns if using DRF swagger/redoc
# Commented out to avoid dependency issues
# try:
#     from rest_framework.documentation import include_docs_urls
#     from rest_framework.schemas import get_schema_view
#
#     # API Documentation
#     docs_urlpatterns = [
#         path('docs/', include_docs_urls(title='Advanced Frequency Analysis API')),
#         path('schema/', get_schema_view(
#             title="Advanced Frequency Analysis API",
#             description="API for quantum-inspired lottery frequency analysis",
#             version="1.0.0"
#         ), name='openapi-schema'),
#     ]
#
#     urlpatterns += docs_urlpatterns
#
# except ImportError:
#     # DRF documentation not available
#     pass

# Additional patterns for development/debugging
import os

if os.environ.get("DEBUG", "False").lower() == "true":
    # Debug-only patterns
    debug_urlpatterns = [
        path(
            "debug/quantum-processor/",
            QuantumProcessorAPIView.as_view(),
            {"debug": True},
            name="debug-quantum-processor",
        ),
        path(
            "debug/neural-recognizer/",
            NeuralRecognizerAPIView.as_view(),
            {"debug": True},
            name="debug-neural-recognizer",
        ),
        path(
            "debug/quantum-optimizer/",
            QuantumOptimizerAPIView.as_view(),
            {"debug": True},
            name="debug-quantum-optimizer",
        ),
        path(
            "debug/meta-learning/",
            MetaLearningAPIView.as_view(),
            {"debug": True},
            name="debug-meta-learning",
        ),
        path(
            "debug/advanced-analysis/",
            AdvancedFrequencyAnalysisAPIView.as_view(),
            {"debug": True},
            name="debug-advanced-analysis",
        ),
        # Test API page
        path("test-api/", test_api_page, name="test-api-page"),
    ]

    urlpatterns += debug_urlpatterns
