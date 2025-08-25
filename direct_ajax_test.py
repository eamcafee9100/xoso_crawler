#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
🔧 DIRECT TEST: Test AJAX functionality directly
"""

import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'xoso_crawler.settings')
sys.path.append('.')
django.setup()
print("✅ Django initialized")

# Import after Django setup
from analytic_frequence.template_views import ajax_prediction_api
from django.http import HttpRequest
import json

def create_test_request(prediction_date="2025-08-12"):
    """Create a test HTTP request"""
    request = HttpRequest()
    request.method = 'POST'
    request.META['CONTENT_TYPE'] = 'application/json'
    
    test_data = {
        'prediction_date': prediction_date,
        'prediction_horizon': 3,
        'use_real_data': True
    }
    
    request._body = json.dumps(test_data).encode('utf-8')
    return request

def test_ajax_direct():
    """Test AJAX function directly"""
    print("\n🧪 TESTING AJAX FUNCTION DIRECTLY")
    print("="*60)
    
    try:
        # Test with date
        print("📅 Testing with date: 2025-08-12")
        request = create_test_request("2025-08-12")
        response = ajax_prediction_api(request)
        
        print(f"📊 Response status: {response.status_code}")
        
        if response.status_code == 200:
            data = json.loads(response.content.decode())
            print(f"✅ Success: {data.get('success')}")
            
            if data.get('success'):
                pred_data = data['prediction_data']
                print(f"🎯 Predictions: {len(pred_data.get('predictions', []))}")
                print(f"🔗 Data source: {pred_data.get('data_source')}")
                print(f"📅 Analysis date: {pred_data.get('prediction_date')}")
                
                # Test another date
                print("\n📅 Testing with date: 2025-08-06")
                request2 = create_test_request("2025-08-06")
                response2 = ajax_prediction_api(request2)
                
                if response2.status_code == 200:
                    data2 = json.loads(response2.content.decode())
                    if data2.get('success'):
                        pred_data2 = data2['prediction_data']
                        print(f"🔗 Data source: {pred_data2.get('data_source')}")
                        
                        # Compare
                        if pred_data['data_source'] != pred_data2['data_source']:
                            print("✅ SUCCESS: Different data sources!")
                        else:
                            print("⚠️ Same data sources")
                
                return True
            else:
                print(f"❌ Error: {data.get('error')}")
                return False
        else:
            print(f"❌ HTTP Error: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_ajax_direct()
