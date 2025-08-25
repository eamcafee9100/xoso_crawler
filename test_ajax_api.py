#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
🧪 TEST SCRIPT: AJAX API Performance Test
Test the AJAX prediction API to ensure it works properly
"""

import requests
import json
import time
from datetime import datetime

def test_ajax_api():
    """Test AJAX prediction API"""
    
    print("🧪 Testing AJAX Prediction API")
    print("=" * 50)
    
    # Test URL
    url = "http://127.0.0.1:8000/analytic-frequence/ajax-prediction/"
    
    # Test data
    test_data = {
        "prediction_date": "2025-08-14",
        "prediction_horizon": 5,
        "use_real_data": True
    }
    
    print(f"📡 Sending request to: {url}")
    print(f"📊 Test data: {test_data}")
    
    try:
        start_time = time.time()
        
        # Send POST request
        response = requests.post(
            url,
            json=test_data,
            headers={'Content-Type': 'application/json'},
            timeout=30
        )
        
        response_time = (time.time() - start_time) * 1000
        
        print(f"⏱️ Response time: {response_time:.2f}ms")
        print(f"📊 Status code: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ SUCCESS: API responded successfully")
            
            data = response.json()
            
            if data.get('success'):
                predictions = data.get('prediction_data', {}).get('predictions', [])
                print(f"🎯 Got {len(predictions)} predictions")
                
                for i, pred in enumerate(predictions[:3]):  # Show first 3
                    print(f"  {i+1}. Number: {pred.get('number')}, Confidence: {pred.get('confidence')}")
                    
                if response_time < 500:
                    print("⚡ EXCELLENT: Response time < 500ms")
                elif response_time < 1000:
                    print("✅ GOOD: Response time < 1000ms")
                else:
                    print("⚠️ SLOW: Response time > 1000ms")
            else:
                print(f"⚠️ API returned success=false: {data.get('error')}")
                
        else:
            print(f"❌ ERROR: Status {response.status_code}")
            print(f"Response: {response.text[:200]}...")
            
    except requests.exceptions.RequestException as e:
        print(f"❌ NETWORK ERROR: {e}")
    except Exception as e:
        print(f"❌ UNEXPECTED ERROR: {e}")

def test_multiple_requests():
    """Test multiple requests to check caching"""
    
    print("\n🔄 Testing Multiple Requests (Cache Test)")
    print("=" * 50)
    
    url = "http://127.0.0.1:8000/analytic-frequence/ajax-prediction/"
    test_data = {
        "prediction_date": "2025-08-14",
        "prediction_horizon": 3,
        "use_real_data": True
    }
    
    times = []
    
    for i in range(3):
        try:
            start_time = time.time()
            response = requests.post(url, json=test_data, timeout=10)
            response_time = (time.time() - start_time) * 1000
            times.append(response_time)
            
            print(f"Request {i+1}: {response_time:.2f}ms - Status: {response.status_code}")
            
        except Exception as e:
            print(f"Request {i+1}: ERROR - {e}")
    
    if len(times) >= 2:
        if times[1] < times[0] * 0.5:  # Second request should be much faster (cached)
            print("✅ CACHING WORKS: Second request much faster")
        else:
            print("⚠️ CACHING MAY NOT BE WORKING: Similar response times")

def test_ultimate_prediction_page():
    """Test the ultimate prediction template page"""
    
    print("\n🎯 Testing Ultimate Prediction Page")
    print("=" * 50)
    
    url = "http://127.0.0.1:8000/analytic-frequence/ultimate-prediction/"
    
    try:
        start_time = time.time()
        response = requests.get(url, timeout=30)
        response_time = (time.time() - start_time) * 1000
        
        print(f"⏱️ Page load time: {response_time:.2f}ms")
        print(f"📊 Status code: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ SUCCESS: Page loaded successfully")
            
            if response_time < 1000:
                print("⚡ FAST: Page load < 1000ms")
            elif response_time < 3000:
                print("✅ ACCEPTABLE: Page load < 3000ms")
            else:
                print("⚠️ SLOW: Page load > 3000ms")
                
            # Check for key content
            content = response.text
            if "Ultimate Prediction" in content:
                print("✅ Page contains expected content")
            else:
                print("⚠️ Page may not have loaded correctly")
                
        else:
            print(f"❌ ERROR: Status {response.status_code}")
            
    except Exception as e:
        print(f"❌ ERROR: {e}")

if __name__ == "__main__":
    print("""
🎯 ULTIMATE REVOLUTIONARY SYSTEM - API TESTING
===============================================
Testing AJAX API performance and functionality
    """)
    
    # Run tests
    test_ajax_api()
    test_multiple_requests()
    test_ultimate_prediction_page()
    
    print("""
🏆 TESTING COMPLETED
===================
Check the results above to verify system performance.
    """)
