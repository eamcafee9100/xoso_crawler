#!/usr/bin/env python3
"""
Test AJAX endpoint with different dates
"""

import os
import sys
import django
import requests
import json

# Setup Django
sys.path.append("C:\\Users\\n2t\\Documents\\xoso_crawler")
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "xoso_crawler.settings")
django.setup()


def test_ajax_endpoint():
    """Test the AJAX endpoint with different dates"""
    base_url = "http://127.0.0.1:8000/analytic-frequence/ajax-prediction/"
    
    test_dates = [
        "2025-08-12",
        "2025-08-06", 
        "2025-07-15"
    ]
    
    for date in test_dates:
        print(f"\n📅 Testing date: {date}")
        
        data = {
            "prediction_date": date,
            "prediction_horizon": 5,
            "use_real_data": True
        }
        
        try:
            response = requests.post(
                base_url,
                json=data,
                headers={"Content-Type": "application/json"},
                timeout=30
            )
            
            print(f"Status: {response.status_code}")
            
            if response.status_code == 200:
                result = response.json()
                print(f"✅ Success: {result.get('success', False)}")
                
                if result.get('success') and 'data' in result:
                    prediction_data = result['data'].get('prediction_data', {})
                    print(f"   Data source: {prediction_data.get('data_source', 'N/A')}")
                    print(f"   Confidence: {prediction_data.get('confidence_score', 'N/A')}")
                    predictions = prediction_data.get('predictions', [])
                    print(f"   Predictions: {predictions[:5] if predictions else 'None'}...")
                else:
                    print(f"   Error: {result.get('message', 'Unknown error')}")
            else:
                print(f"❌ HTTP Error: {response.status_code}")
                print(f"   Response: {response.text[:200]}...")
                
        except Exception as e:
            print(f"❌ Exception: {e}")


if __name__ == "__main__":
    print("=== TESTING AJAX ENDPOINT WITH DIFFERENT DATES ===")
    test_ajax_endpoint()
    print("\n✅ Testing completed!")
