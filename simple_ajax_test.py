#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
🔧 SIMPLE AJAX TEST: Test AJAX API directly using Django test client
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
from django.conf import settings

def test_ajax_direct():
    """Test AJAX API directly with Django client"""
    print("🧪 TESTING AJAX API WITH DJANGO CLIENT")
    print("="*60)
    
    # Add localhost to ALLOWED_HOSTS if needed
    if 'localhost' not in settings.ALLOWED_HOSTS:
        settings.ALLOWED_HOSTS.append('localhost')
    if '127.0.0.1' not in settings.ALLOWED_HOSTS:
        settings.ALLOWED_HOSTS.append('127.0.0.1')
    
    client = Client()
    
    test_dates = ['2025-08-12', '2025-08-06', '2025-07-15']
    results = {}
    
    for date in test_dates:
        print(f"\n📅 Testing date: {date}")
        print("-" * 40)
        
        test_data = {
            'prediction_date': date,
            'prediction_horizon': 3,
            'use_real_data': True
        }
        
        try:
            response = client.post(
                '/analytic-frequence/ajax-prediction/',
                data=json.dumps(test_data),
                content_type='application/json'
            )
            
            print(f"📊 Status Code: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                success = data.get('success', False)
                print(f"✅ Success: {success}")
                
                if success:
                    pred_data = data['prediction_data']
                    data_source = pred_data.get('data_source', 'unknown')
                    predictions = pred_data.get('predictions', [])
                    confidence = pred_data.get('confidence_score', 0)
                    analysis_date = pred_data.get('prediction_date', 'none')
                    
                    print(f"🔗 Data Source: {data_source}")
                    print(f"🎯 Predictions Count: {len(predictions)}")
                    print(f"🎖️ Confidence Score: {confidence}")
                    print(f"📅 Analysis Date: {analysis_date}")
                    
                    results[date] = {
                        'data_source': data_source,
                        'confidence': confidence,
                        'predictions_count': len(predictions)
                    }
                    
                    print("✅ SUCCESS!")
                else:
                    error = data.get('error', 'Unknown error')
                    print(f"❌ API Error: {error}")
            else:
                print(f"❌ HTTP Error: {response.status_code}")
                content = response.content.decode()[:300]
                print(f"📝 Response: {content}")
                
        except Exception as e:
            print(f"❌ Exception: {e}")
            import traceback
            traceback.print_exc()
    
    # Compare results
    if len(results) > 1:
        print(f"\n🔍 COMPARISON RESULTS:")
        print("="*60)
        
        data_sources = set()
        confidences = set()
        
        for date, result in results.items():
            data_sources.add(result['data_source'])
            confidences.add(result['confidence'])
            print(f"📅 {date}: {result['data_source']} (confidence: {result['confidence']})")
        
        print(f"\n📊 Summary:")
        print(f"  • Unique data sources: {len(data_sources)}")
        print(f"  • Unique confidences: {len(confidences)}")
        
        if len(data_sources) > 1:
            print("✅ SUCCESS: Different data sources for different dates!")
            print("✅ Date-specific analysis is working correctly!")
        else:
            print("⚠️ WARNING: Same data sources for all dates")
            
        print(f"\n📋 Data Sources Found:")
        for ds in data_sources:
            print(f"  • {ds}")
            
    else:
        print("⚠️ Not enough successful results to compare")
    
    print("\n🏁 Testing completed")

if __name__ == "__main__":
    test_ajax_direct()
