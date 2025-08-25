#!/usr/bin/env python3
"""
🧪 Simple test API to verify Phase 2A structure is working
"""

import logging

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

logger = logging.getLogger(__name__)


@csrf_exempt
@require_http_methods(["POST"])
def api_simple_test(request):
    """Simple test endpoint to verify API structure"""
    try:
        logger.info("🧪 Simple test API called")

        # Just return basic info
        return JsonResponse(
            {
                "success": True,
                "message": "🎉 Phase 2A API structure is working!",
                "endpoint": "test",
                "method": "POST",
                "timestamp": "2025-07-29T12:00:00Z",
                "data_received": {
                    "POST": dict(request.POST),
                    "headers": dict(request.headers),
                },
            }
        )

    except Exception as e:
        logger.error(f"❌ Simple test API error: {e}")
        return JsonResponse(
            {"success": False, "error": str(e), "message": "Test API failed"},
            status=500,
        )
