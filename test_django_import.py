"""
Test Django Import 
"""
import os
import sys
import django

# Setup Django
sys.path.append('c:\\Users\\n2t\\Documents\\xoso_crawler')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'xoso_crawler.settings')
django.setup()

try:
    from predictions_tracker.views_dir.api_method_analysis_by_date_v2 import api_method_analysis_by_date_v2
    print("✅ api_method_analysis_by_date_v2 imported successfully!")
    print(f"Function name: {api_method_analysis_by_date_v2.__name__}")
    print(f"Function docstring: {api_method_analysis_by_date_v2.__doc__[:100]}...")
except ImportError as e:
    print(f"❌ Import failed: {e}")
except Exception as e:
    print(f"❌ Error: {e}")

# Test Django URLs
try:
    from django.urls import reverse
    from django.test import RequestFactory
    
    print("✅ Django URL system working")
    
    # Test URL resolve
    from django.urls import resolve
    try:
        match = resolve('/predictions_tracker/api/method-analysis-v2/')
        print(f"✅ URL resolved to: {match.func.__name__}")
    except Exception as e:
        print(f"❌ URL resolve error: {e}")
    
except Exception as e:
    print(f"❌ Django URL test error: {e}")
