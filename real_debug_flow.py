#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
🔧 REAL DEBUG: Test the actual flow to identify why same results
"""

import os
import sys
import django
from datetime import date, datetime

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'xoso_crawler.settings')
sys.path.append('.')
django.setup()

print("🔧 DEBUGGING REAL DATE ANALYSIS FLOW")
print("="*70)

# Test 1: Direct data service test
print("\n🔍 STEP 1: Testing RealDataIntegrationService directly")
print("-" * 60)

from analytic_frequence.data_integration_service import RealDataIntegrationService

service = RealDataIntegrationService()

test_dates = [
    date(2025, 8, 12),
    date(2025, 8, 6),
    date(2025, 7, 15)
]

service_results = {}

for test_date in test_dates:
    print(f"\n📅 Testing date: {test_date}")
    
    # Test without date
    result_default = service.get_enhanced_lottery_input()
    print(f"  Default: {len(result_default['lottery_numbers'])} numbers, source: {result_default['data_source']}")
    
    # Test with date
    result_dated = service.get_enhanced_lottery_input(prediction_date=test_date)
    print(f"  With date: {len(result_dated['lottery_numbers'])} numbers, source: {result_dated['data_source']}")
    print(f"  Analysis date: {result_dated.get('analysis_date')}")
    
    service_results[str(test_date)] = {
        'default': result_default['data_source'],
        'dated': result_dated['data_source'],
        'count': len(result_dated['lottery_numbers'])
    }

# Compare service results
print(f"\n📊 SERVICE COMPARISON:")
print("-" * 40)
dated_sources = set()
for date_str, result in service_results.items():
    dated_sources.add(result['dated'])
    print(f"  {date_str}: {result['dated']} ({result['count']} numbers)")

if len(dated_sources) > 1:
    print("✅ Service level: Different sources for different dates")
else:
    print("❌ Service level: Same sources - THIS IS THE PROBLEM!")

# Test 2: AJAX API simulation
print(f"\n🔍 STEP 2: Testing AJAX API simulation")
print("-" * 60)

from analytic_frequence.template_views import ajax_prediction_api
from django.http import HttpRequest
import json

def create_mock_request(pred_date):
    request = HttpRequest()
    request.method = 'POST'
    request.META['CONTENT_TYPE'] = 'application/json'
    
    test_data = {
        'prediction_date': pred_date,
        'prediction_horizon': 3,
        'use_real_data': True
    }
    
    request._body = json.dumps(test_data).encode('utf-8')
    return request

ajax_results = {}

for test_date in test_dates:
    date_str = test_date.strftime('%Y-%m-%d')
    print(f"\n📅 Testing AJAX with date: {date_str}")
    
    try:
        request = create_mock_request(date_str)
        response = ajax_prediction_api(request)
        
        print(f"  Status: {response.status_code}")
        
        if response.status_code == 200:
            data = json.loads(response.content.decode())
            success = data.get('success', False)
            print(f"  Success: {success}")
            
            if success:
                pred_data = data['prediction_data']
                data_source = pred_data.get('data_source', 'unknown')
                prediction_date = pred_data.get('prediction_date', 'none')
                confidence = pred_data.get('confidence_score', 0)
                
                print(f"  Data source: {data_source}")
                print(f"  Prediction date: {prediction_date}")
                print(f"  Confidence: {confidence}")
                
                ajax_results[date_str] = {
                    'data_source': data_source,
                    'prediction_date': prediction_date,
                    'confidence': confidence
                }
            else:
                error = data.get('error', 'Unknown')
                print(f"  ❌ Error: {error}")
        else:
            print(f"  ❌ HTTP Error: {response.status_code}")
            
    except Exception as e:
        print(f"  ❌ Exception: {e}")
        import traceback
        traceback.print_exc()

# Compare AJAX results
print(f"\n📊 AJAX COMPARISON:")
print("-" * 40)
ajax_sources = set()
ajax_confidences = set()

for date_str, result in ajax_results.items():
    ajax_sources.add(result['data_source'])
    ajax_confidences.add(result['confidence'])
    print(f"  {date_str}: {result['data_source']} (conf: {result['confidence']})")

print(f"\n📈 FINAL ANALYSIS:")
print("-" * 40)
print(f"  Service level sources: {len(dated_sources)} unique")
print(f"  AJAX level sources: {len(ajax_sources)} unique")
print(f"  AJAX confidences: {len(ajax_confidences)} unique")

if len(ajax_sources) > 1:
    print("✅ SUCCESS: AJAX returns different data sources!")
    print("✅ Date-specific analysis is working!")
else:
    print("❌ PROBLEM: AJAX returns same data sources")
    print("🔍 Need to investigate why...")
    
    # Additional debugging
    if len(dated_sources) > 1:
        print("📋 Service works but AJAX doesn't - check AJAX logic")
    else:
        print("📋 Service itself doesn't work - check data integration")

print(f"\n🏁 DEBUG COMPLETED")
