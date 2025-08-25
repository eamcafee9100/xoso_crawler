#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
🔧 BASIC ENDPOINT TEST
Create a simple endpoint to test basic functionality
"""

import logging
from datetime import datetime

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

logger = logging.getLogger(__name__)


@csrf_exempt
@require_http_methods(["GET"])
def api_simple_test(request):
    """
    Simple test endpoint that returns immediately
    """
    try:
        analysis_date_str = request.GET.get("analysis_date", "2025-07-30")
        limit = int(request.GET.get("limit", 15))

        # Return mock V2 structure immediately
        response_data = {
            "success": True,
            "test_mode": True,
            "analysis_date": analysis_date_str,
            "limit": limit,
            "timestamp": datetime.now().isoformat(),
            # V2 Expected Structure
            "hybrid_analysis": {
                "short_term_insights": {
                    "trend_strength": 0.75,
                    "pattern_confidence": 0.8,
                    "recent_performance": 0.72,
                },
                "long_term_stability": {
                    "consistency_score": 0.68,
                    "historical_performance": 0.65,
                    "stability_trend": "stable",
                },
                "forward_validation": {
                    "confidence_score": 0.71,
                    "predictive_power": 0.69,
                    "validation_strength": "medium",
                },
            },
            "intelligent_selections": {
                "optimal_numbers": [12, 34, 56, 78, 90, 13, 45],
                "method_contributions": [
                    {
                        "method_name": "Test Method A",
                        "contribution": 0.35,
                        "confidence": 0.82,
                    },
                    {
                        "method_name": "Test Method B",
                        "contribution": 0.28,
                        "confidence": 0.76,
                    },
                ],
                "selection_strategy": {
                    "approach": "hybrid_balanced",
                    "risk_level": "medium",
                    "diversification": "high",
                },
            },
            "optimal_methods": {
                "day_1": [
                    {
                        "method_name": "Test Method A1",
                        "hybrid_score": 85.5,
                        "expected_hit_rate": 0.75,
                        "predicted_numbers": [12, 34, 56],
                        "confidence_level": "high",
                    },
                    {
                        "method_name": "Test Method A2",
                        "hybrid_score": 78.2,
                        "expected_hit_rate": 0.68,
                        "predicted_numbers": [78, 90, 13],
                        "confidence_level": "medium",
                    },
                ],
                "day_2": [
                    {
                        "method_name": "Test Method B1",
                        "hybrid_score": 82.1,
                        "expected_hit_rate": 0.72,
                        "predicted_numbers": [45, 67, 89],
                        "confidence_level": "high",
                    }
                ],
                "day_3": [],
                "summary": {
                    "total_qualified_methods": 3,
                    "avg_confidence": 0.72,
                    "risk_level": "medium",
                },
            },
            "performance_prediction": {
                "expected_hit_rate": 0.72,
                "confidence_level": "high",
                "overall_confidence_score": 0.78,
                "risk_assessment": {
                    "level": "medium",
                    "factors": ["market_volatility", "historical_variance"],
                },
                "performance_breakdown": {
                    "confidence_factors": {
                        "data_quality": 0.85,
                        "model_stability": 0.79,
                        "validation_strength": 0.71,
                    },
                    "risk_factors": ["limited_recent_data", "market_uncertainty"],
                },
            },
            "metadata": {
                "processing_time_ms": 50,
                "data_points_analyzed": 1000,
                "api_version": "v2_test",
                "analysis_approach": "simple_mock",
            },
        }

        logger.info(f"✅ Simple test API called: {analysis_date_str}")

        return JsonResponse(
            response_data, json_dumps_params={"ensure_ascii": False, "indent": 2}
        )

    except Exception as e:
        logger.error(f"❌ Simple test API error: {e}")
        return JsonResponse(
            {"success": False, "error": str(e), "error_type": "simple_test_error"},
            status=500,
        )
