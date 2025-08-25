#!/usr/bin/env python3
"""
Test script to verify the template fix works correctly
"""

import os
import sys
import django

# Setup Django
sys.path.append("C:\\Users\\n2t\\Documents\\xoso_crawler")
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "xoso_crawler.settings")
django.setup()

from django.test import RequestFactory
from analytic_frequence.template_views import UltimatePredictionTemplateView


def test_template_rendering():
    print("=== TESTING TEMPLATE RENDERING ===")

    # Create request
    factory = RequestFactory()
    request = factory.get("/ultimate-prediction/")

    # Create view
    view = UltimatePredictionTemplateView()
    view.setup(request)

    # Get context
    context = view.get_context_data()

    print(f"Sample prediction available: {context.get('sample_prediction') is not None}")
    print(f"Sample prediction JSON available: {'sample_prediction_json' in context}")

    sample_json = context.get("sample_prediction_json", "null")
    print(f"JSON length: {len(sample_json)}")
    print(f"JSON starts with: {sample_json[:100]}...")

    # Test if JSON is valid
    import json
    try:
        if sample_json != "null":
            parsed = json.loads(sample_json)
            print(f"✅ JSON is valid!")
            print(f"Has predictions: {'predictions' in parsed}")
            if "predictions" in parsed:
                print(f"Predictions type: {type(parsed['predictions'])}")
                if isinstance(parsed["predictions"], list):
                    print(f"Number of predictions: {len(parsed['predictions'])}")
                    if parsed["predictions"]:
                        print(f"First prediction: {parsed['predictions'][0]} (type: {type(parsed['predictions'][0])})")
        else:
            print("✅ No sample prediction - that's OK")
    except json.JSONDecodeError as e:
        print(f"❌ JSON parsing error: {e}")
        print(f"Invalid JSON: {sample_json[:500]}...")

    return context


def test_date_specific_predictions():
    print("\n=== TESTING DATE SPECIFIC PREDICTIONS ===")
    
    from analytic_frequence.data_integration_service import RealDataIntegrationService
    from datetime import datetime, timedelta
    
    service = RealDataIntegrationService()
    
    # Test with different dates
    test_dates = [
        datetime.now().date(),
        datetime.now().date() - timedelta(days=5),
        datetime.now().date() - timedelta(days=10)
    ]
    
    for test_date in test_dates:
        print(f"\n📅 Testing date: {test_date}")
        data = service.get_enhanced_lottery_input(prediction_date=test_date)
        print(f"   Data source: {data.get('data_source', 'N/A')}")
        print(f"   Numbers count: {len(data.get('lottery_numbers', []))}")
        print(f"   First 5 numbers: {data.get('lottery_numbers', [])[:5]}")


if __name__ == "__main__":
    context = test_template_rendering()
    test_date_specific_predictions()
    print("\n✅ Testing completed!")
