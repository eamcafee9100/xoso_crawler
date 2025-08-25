#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
🧪 TEST AJAX FIX: Test the fixed AJAX prediction API
"""

import os
import sys
import django
import json

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'xoso_crawler.settings')
sys.path.append('.')
django.setup()

from django.test import Client

def test_ajax_fix():
    """Test the fixed AJAX prediction API"""
    print("🧪 TESTING FIXED AJAX PREDICTION API")
    print("="*60)
    
    # Test AJAX request
    client = Client()
    test_data = {
        'prediction_date': '2025-08-12',
        'prediction_horizon': 3,
        'use_real_data': True
    }

    print(f"📤 Sending request: {test_data}")
    
    try:
        response = client.post(
            '/analytic-frequence/ajax-prediction/',
            data=json.dumps(test_data),
            content_type='application/json',
            HTTP_HOST='localhost'
        )

        print(f"📥 Response status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Success: {data.get('success')}")
            
            if data.get('success'):
                pred_data = data['prediction_data']
                print(f"🎯 Predictions: {len(pred_data.get('predictions', []))}")
                print(f"🔗 Data source: {pred_data.get('data_source')}")
                print(f"📅 Analysis date: {pred_data.get('prediction_date')}")
                print(f"🎖️ Confidence: {pred_data.get('confidence_score')}")
                print("✅ AJAX API WORKING!")
                return True
            else:
                print(f"❌ API Error: {data.get('error')}")
                return False
        else:
            print("❌ HTTP Error")
            content = response.content.decode()[:500]
            print(f"📝 Content: {content}")
            return False
            
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_multiple_dates():
    """Test multiple dates to verify different results"""
    print("\n🔬 TESTING MULTIPLE DATES")
    print("="*60)
    
    client = Client()
    test_dates = ['2025-08-12', '2025-08-06', '2025-07-15']
    results = {}
    
    for test_date in test_dates:
        test_data = {
            'prediction_date': test_date,
            'prediction_horizon': 3,
            'use_real_data': True
        }
        
        try:
            response = client.post(
                '/analytic-frequence/ajax-prediction/',
                data=json.dumps(test_data),
                content_type='application/json',
                HTTP_HOST='localhost'
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get('success'):
                    pred_data = data['prediction_data']
                    results[test_date] = {
                        'data_source': pred_data.get('data_source'),
                        'predictions': pred_data.get('predictions', [])[:3],  # First 3
                        'confidence': pred_data.get('confidence_score')
                    }
                    print(f"📅 {test_date}: ✅ {pred_data.get('data_source')}")
                else:
                    print(f"📅 {test_date}: ❌ {data.get('error')}")
            else:
                print(f"📅 {test_date}: ❌ HTTP {response.status_code}")
                
        except Exception as e:
            print(f"📅 {test_date}: ❌ Exception {e}")
    
    # Compare results
    print("\n🔍 RESULTS COMPARISON:")
    print("-" * 50)
    data_sources = set()
    for date, result in results.items():
        data_sources.add(result['data_source'])
        print(f"  {date}: {result['data_source']}")
        
    if len(data_sources) > 1:
        print("✅ SUCCESS: Different data sources for different dates!")
        return True
    else:
        print("❌ ISSUE: Same data sources for all dates")
        return False

if __name__ == "__main__":
    print("🚀 AJAX FIX VERIFICATION")
    print("="*60)
    
    # Test basic functionality
    ajax_works = test_ajax_fix()
    
    if ajax_works:
        # Test date specificity
        date_specific = test_multiple_dates()
        
        if date_specific:
            print("\n🎉 ALL TESTS PASSED!")
            print("✅ AJAX API is working")
            print("✅ Date-specific analysis is working")
        else:
            print("\n⚠️ PARTIAL SUCCESS")
            print("✅ AJAX API is working")
            print("❌ Date-specific analysis needs investigation")
    else:
        print("\n❌ TESTS FAILED")
        print("❌ AJAX API still has issues")
    
    print("\n🏁 Testing completed")
