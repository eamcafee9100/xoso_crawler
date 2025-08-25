from django.http import HttpResponse, FileResponse
from django.views.decorators.csrf import csrf_exempt
import os

@csrf_exempt
def test_api_page(request):
    """Serve the test API HTML page"""
    html_path = os.path.join(os.path.dirname(__file__), '..', '..', 'test_api.html')
    
    try:
        with open(html_path, 'r', encoding='utf-8') as f:
            html_content = f.read()
        return HttpResponse(html_content, content_type='text/html')
    except FileNotFoundError:
        return HttpResponse("Test API page not found", status=404)
