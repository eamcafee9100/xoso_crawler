#!/usr/bin/env python3
"""
Simple test view to test AJAX date functionality
"""

from django.http import HttpResponse
from django.urls import path
import os


def test_ajax_dates_view(request):
    """Serve the test HTML file"""
    file_path = os.path.join(os.path.dirname(__file__), "test_ajax_dates.html")
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()
    return HttpResponse(content, content_type="text/html")


# URL pattern for inclusion
test_urlpatterns = [
    path("test-ajax-dates/", test_ajax_dates_view, name="test_ajax_dates"),
]
