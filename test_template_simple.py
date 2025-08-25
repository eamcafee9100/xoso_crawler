#!/usr/bin/env python3
"""
Simple Django test to verify the template fix
"""

import os
import sys
import django

# Setup Django
sys.path.append("C:\\Users\\n2t\\Documents\\xoso_crawler")
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "xoso_crawler.settings")
django.setup()

from django.test import Client
import json


def test_ultimate_prediction_template():
    """Test the Ultimate Prediction template rendering"""
    print("=== TESTING ULTIMATE PREDICTION TEMPLATE ===")
    
    client = Client()
    
    try:
        # Test template view
        response = client.get("/analytic-frequence/ultimate-prediction/")
        print(f"Template view status: {response.status_code}")
        
        if response.status_code == 200:
            content = response.content.decode('utf-8')
            
            # Check if JavaScript errors are present
            js_error_indicators = [
                "&#x27;",  # HTML entity that breaks JavaScript
                "np.float64",  # Python object that breaks JavaScript
                "Float64",  # Numpy type that breaks JavaScript
            ]
            
            errors_found = []
            for indicator in js_error_indicators:
                if indicator in content:
                    errors_found.append(indicator)
            
            if errors_found:
                print(f"❌ Found JavaScript error indicators: {errors_found}")
                # Find the context of the error
                for error in errors_found:
                    start = content.find(error)
                    if start != -1:
                        context = content[max(0, start-50):start+100]
                        print(f"   Context for '{error}': ...{context}...")
            else:
                print("✅ No JavaScript error indicators found")
            
            # Check if sample_prediction_json is present
            if "sample_prediction_json" in content:
                print("✅ sample_prediction_json variable found in template")
            else:
                print("❌ sample_prediction_json variable not found")
                
            # Look for the JSON structure
            if "const sampleData = " in content:
                print("✅ JavaScript sampleData assignment found")
            else:
                print("❌ JavaScript sampleData assignment not found")
                
        else:
            print(f"❌ Template view failed with status {response.status_code}")
            
    except Exception as e:
        print(f"❌ Template test error: {e}")
        

def test_ajax_prediction():
    """Test AJAX prediction endpoint"""
    print("\n=== TESTING AJAX PREDICTION ENDPOINT ===")
    
    client = Client()
    
    test_data = {
        "prediction_date": "2025-08-12",
        "prediction_horizon": 5,
        "use_real_data": True
    }
    
    try:
        response = client.post(
            "/analytic-frequence/ajax-prediction/",
            data=json.dumps(test_data),
            content_type="application/json"
        )
        
        print(f"AJAX status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ AJAX success: {result.get('success', False)}")
            
            if result.get('success') and 'data' in result:
                prediction_data = result['data'].get('prediction_data', {})
                print(f"   Data source: {prediction_data.get('data_source', 'N/A')}")
                print(f"   Confidence: {prediction_data.get('confidence_score', 'N/A')}")
            else:
                print(f"   Error: {result.get('message', 'Unknown error')}")
        else:
            print(f"❌ AJAX failed with status {response.status_code}")
            print(f"   Response: {response.content.decode('utf-8')[:200]}...")
            
    except Exception as e:
        print(f"❌ AJAX test error: {e}")


if __name__ == "__main__":
    test_ultimate_prediction_template()
    test_ajax_prediction()
    print("\n✅ All tests completed!")
