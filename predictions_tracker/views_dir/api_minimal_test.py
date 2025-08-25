"""
Minimal API Version để debug lỗi "'str' object has no attribute 'get'"
"""
import logging
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

logger = logging.getLogger(__name__)

@csrf_exempt
@require_http_methods(["GET"])
def api_method_analysis_by_date_v2_minimal(request):
    """Minimal version để debug error"""
    try:
        logger.info("🔍 MINIMAL API: Starting request...")
        
        # Basic parameter extraction 
        analysis_date_str = request.GET.get("analysis_date", "2025-08-14")
        limit = int(request.GET.get("limit", 1))
        
        logger.info(f"🔍 MINIMAL API: Parameters extracted: date={analysis_date_str}, limit={limit}")
        
        # Return minimal successful response
        return JsonResponse({
            "success": True,
            "message": "Minimal API working",
            "analysis_date": analysis_date_str,
            "limit": limit,
            "test": "This is a string, not a dict"
        })
        
    except Exception as e:
        logger.error(f"❌ MINIMAL API Error: {e}")
        import traceback
        logger.error(f"❌ MINIMAL API Traceback: {traceback.format_exc()}")
        return JsonResponse({
            "success": False,
            "error": str(e)
        }, status=500)
