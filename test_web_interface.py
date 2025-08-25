#!/usr/bin/env python3
"""
Simple test script để test web interface
"""

import requests
import json
import time

def test_web_interface():
    """Test the web interface"""
    base_url = "http://127.0.0.1:8000"
    
    print("🔍 Testing Ultimate Prediction Web Interface...")
    
    try:
        # 1. Test GET request to main page
        print("📄 Testing main page...")
        response = requests.get(f"{base_url}/analytic-frequence/ultimate-prediction-ui/")
        if response.status_code == 200:
            print("✅ Main page loads successfully!")
            print(f"📊 Page size: {len(response.content)} bytes")
        else:
            print(f"❌ Main page failed: {response.status_code}")
            return
        
        # 2. Extract CSRF token from page
        csrf_token = None
        if 'csrfmiddlewaretoken' in response.text:
            # Simple extraction - in production use proper parsing
            import re
            match = re.search(r'name="csrfmiddlewaretoken" value="([^"]+)"', response.text)
            if match:
                csrf_token = match.group(1)
                print(f"🔑 Found CSRF token: {csrf_token[:10]}...")
        
        # 3. Test AJAX prediction with CSRF token
        if csrf_token:
            print("🎯 Testing AJAX prediction...")
            cookies = response.cookies
            
            headers = {
                'Content-Type': 'application/x-www-form-urlencoded',
                'X-CSRFToken': csrf_token,
                'Referer': f"{base_url}/analytic-frequence/ultimate-prediction-ui/"
            }
            
            data = {
                'csrfmiddlewaretoken': csrf_token,
                'selected_game': 'xsmb',
                'analysis_depth': 'deep',
                'prediction_strategy': 'ultimate_fusion'
            }
            
            ajax_response = requests.post(
                f"{base_url}/analytic-frequence/ajax-prediction/",
                data=data,
                headers=headers,
                cookies=cookies
            )
            
            if ajax_response.status_code == 200:
                print("✅ AJAX prediction successful!")
                try:
                    result = ajax_response.json()
                    print(f"📊 Prediction result keys: {list(result.keys())}")
                    if 'predictions' in result:
                        print(f"🎲 Number of predictions: {len(result['predictions'])}")
                    if 'confidence' in result:
                        print(f"📈 Confidence: {result['confidence']}")
                except json.JSONDecodeError:
                    print("⚠️ Response is not JSON")
                    print(f"📄 Response: {ajax_response.text[:200]}...")
            else:
                print(f"❌ AJAX prediction failed: {ajax_response.status_code}")
                print(f"📄 Response: {ajax_response.text[:200]}...")
        else:
            print("⚠️ CSRF token not found, skipping AJAX test")
            
        print("\n🎉 Web interface test completed!")
        
    except Exception as e:
        print(f"❌ Test failed with error: {e}")

if __name__ == "__main__":
    test_web_interface()
