#!/usr/bin/env python3

import traceback
import sys
import os
import django

# Setup Django
sys.path.append('.')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'xoso_crawler.settings')
django.setup()

def test_api_function():
    """Test the API function directly to find error source"""
    try:
        print("🔍 Testing API function import...")
        
        # Import the problematic function
        from predictions_tracker.views_dir.api_method_analysis_by_date_v2 import api_method_analysis_by_date_v2
        print("✅ API function imported successfully")
        
        # Mock request object
        class MockRequest:
            def __init__(self):
                self.GET = {
                    'analysis_date': '2025-08-14',
                    'limit': '1',
                    'threshold': '40',
                    'hybrid': 'true'
                }
        
        print("🔍 Creating mock request...")
        mock_request = MockRequest()
        print("✅ Mock request created")
        
        print("🔍 Calling API function...")
        result = api_method_analysis_by_date_v2(mock_request)
        print(f"✅ API function returned: {type(result)}")
        
        return result
        
    except Exception as e:
        print(f"❌ Error occurred: {e}")
        print(f"🔍 Error type: {type(e)}")
        print("🔍 Full traceback:")
        traceback.print_exc()
        return None

if __name__ == "__main__":
    print("🌟 Starting API debug test...")
    result = test_api_function()
    print(f"🔍 Final result: {result}")
