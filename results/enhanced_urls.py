"""
URL patterns for Enhanced Prediction System
Production-ready URL configuration
"""

from django.urls import path

from .enhanced_views import (
    EnhancedPredictionAPIView,
    EnhancedPredictionView,
    MonitoringDashboardView,
    SystemHealthView,
)

urlpatterns = [
    # Main prediction interface
    path(
        "enhanced-prediction/",
        EnhancedPredictionView.as_view(),
        name="enhanced_prediction",
    ),
    # API endpoints
    path(
        "api/enhanced-prediction/",
        EnhancedPredictionAPIView.as_view(),
        name="enhanced_prediction_api",
    ),
    # Monitoring and management
    path(
        "monitoring-dashboard/",
        MonitoringDashboardView.as_view(),
        name="monitoring_dashboard",
    ),
    path("system-health/", SystemHealthView.as_view(), name="system_health"),
    # API endpoints with specific actions
    path(
        "api/enhanced-prediction/update/",
        EnhancedPredictionAPIView.as_view(),
        name="update_prediction_result",
    ),
]
