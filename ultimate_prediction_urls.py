"""
URL Configuration for Ultimate Lottery Prediction V4 FUSION
==========================================================

Routing configuration for the ultimate prediction system integrating all phases.
Designed with top 0.1% strategic thinking for optimal user experience.

Author: Top 0.1% Strategic AI System
Version: 4.0 FUSION
"""

from django.urls import include, path
from django.views.generic import TemplateView

from . import api_ultimate_lottery_prediction_v4_fusion

app_name = "ultimate_prediction"

urlpatterns = [
    # Ultimate Prediction V4 FUSION - Main API
    path(
        "api/ultimate-prediction-v4-fusion/",
        api_ultimate_lottery_prediction_v4_fusion.api_ultimate_prediction_v4_fusion,
        name="api_ultimate_prediction_v4_fusion",
    ),
    # Enhanced V3 API with Phase 4 integration for backward compatibility
    path(
        "api/cyclical-prediction-v3-enhanced/",
        api_ultimate_lottery_prediction_v4_fusion.api_cyclical_prediction_by_date_v3_enhanced,
        name="api_cyclical_prediction_v3_enhanced",
    ),
    # Web Interface for Ultimate Prediction
    path(
        "ultimate-prediction/",
        TemplateView.as_view(template_name="ultimate_lottery_prediction_v4.html"),
        name="ultimate_prediction_interface",
    ),
    # Admin Interface for System Monitoring
    path(
        "ultimate-prediction/admin/",
        TemplateView.as_view(template_name="ultimate_prediction_admin.html"),
        name="ultimate_prediction_admin",
    ),
    # API Documentation
    path(
        "ultimate-prediction/docs/",
        TemplateView.as_view(template_name="ultimate_prediction_docs.html"),
        name="ultimate_prediction_docs",
    ),
    # Performance Analytics Dashboard
    path(
        "ultimate-prediction/analytics/",
        TemplateView.as_view(template_name="ultimate_prediction_analytics.html"),
        name="ultimate_prediction_analytics",
    ),
    # Backtesting Interface
    path(
        "ultimate-prediction/backtest/",
        TemplateView.as_view(template_name="ultimate_prediction_backtest.html"),
        name="ultimate_prediction_backtest",
    ),
]

# Additional API endpoints for advanced features
advanced_api_patterns = [
    # Batch prediction for multiple dates
    path(
        "api/ultimate-prediction/batch/",
        api_ultimate_lottery_prediction_v4_fusion.api_batch_prediction,
        name="api_batch_prediction",
    ),
    # Real-time prediction streaming
    path(
        "api/ultimate-prediction/stream/",
        api_ultimate_lottery_prediction_v4_fusion.api_prediction_stream,
        name="api_prediction_stream",
    ),
    # Performance evaluation
    path(
        "api/ultimate-prediction/evaluate/",
        api_ultimate_lottery_prediction_v4_fusion.api_evaluate_performance,
        name="api_evaluate_performance",
    ),
    # Model configuration
    path(
        "api/ultimate-prediction/config/",
        api_ultimate_lottery_prediction_v4_fusion.api_model_configuration,
        name="api_model_configuration",
    ),
    # System health check
    path(
        "api/ultimate-prediction/health/",
        api_ultimate_lottery_prediction_v4_fusion.api_health_check,
        name="api_health_check",
    ),
]

# Combine all URL patterns
urlpatterns += advanced_api_patterns

# URL patterns for testing and development
if True:  # Enable in development/testing
    test_patterns = [
        # Test interface
        path(
            "ultimate-prediction/test/",
            TemplateView.as_view(template_name="ultimate_prediction_test.html"),
            name="ultimate_prediction_test",
        ),
        # Debug information
        path(
            "api/ultimate-prediction/debug/",
            api_ultimate_lottery_prediction_v4_fusion.api_debug_info,
            name="api_debug_info",
        ),
        # Performance benchmarking
        path(
            "api/ultimate-prediction/benchmark/",
            api_ultimate_lottery_prediction_v4_fusion.api_benchmark,
            name="api_benchmark",
        ),
    ]

    urlpatterns += test_patterns

# Meta information for URL routing
URL_META = {
    "version": "4.0_FUSION",
    "api_count": len([p for p in urlpatterns if "api" in str(p.pattern)]),
    "interface_count": len([p for p in urlpatterns if "api" not in str(p.pattern)]),
    "total_endpoints": len(urlpatterns),
    "main_api": "api/ultimate-prediction-v4-fusion/",
    "main_interface": "ultimate-prediction/",
    "documentation": "ultimate-prediction/docs/",
    "features": [
        "Multi-phase prediction fusion",
        "Risk-adjusted optimization",
        "Real-time streaming",
        "Batch processing",
        "Performance analytics",
        "Backtesting framework",
        "Admin monitoring",
        "API documentation",
    ],
}

print(f"🚀 Ultimate Prediction V4 FUSION URLs loaded:")
print(f"📊 Total endpoints: {URL_META['total_endpoints']}")
print(f"🔌 API endpoints: {URL_META['api_count']}")
print(f"🖥️ Interface endpoints: {URL_META['interface_count']}")
print(f"🎯 Main API: {URL_META['main_api']}")
print(f"📱 Main Interface: {URL_META['main_interface']}")
