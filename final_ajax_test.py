#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
🧪 FINAL TEST: Test AJAX API directly using Python requests
"""

import requests
import json

def test_ajax_api():
    """Test AJAX API với multiple dates"""
    print("🧪 TESTING AJAX API - DATE ANALYSIS FIX")
    print("="*60)
    
    base_url = "http://127.0.0.1:8000/analytic-frequence/ajax-prediction/"
    
    test_cases = [
        {"date": "2025-08-12", "description": "Latest date"},
        {"date": "2025-08-06", "description": "One week ago"},
        {"date": "2025-07-15", "description": "One month ago"},
    ]
    
    results = {}
    
    for test_case in test_cases:
        date = test_case["date"]
        desc = test_case["description"]
        
        print(f"\n📅 Testing {desc}: {date}")
        print("-" * 50)
        
        payload = {
            "prediction_date": date,
            "prediction_horizon": 3,
            "use_real_data": True
        }
        
        try:
            response = requests.post(
                base_url,
                json=payload,
                headers={'Content-Type': 'application/json'},
                timeout=30
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
                    
                    # Store for comparison
                    results[date] = {
                        'data_source': data_source,
                        'predictions_count': len(predictions),
                        'confidence': confidence,
                        'first_prediction': predictions[0] if predictions else None
                    }
                    
                    if predictions:
                        print(f"🔢 First Prediction: {predictions[0]}")
                    
                    print("✅ SUCCESS!")
                else:
                    error = data.get('error', 'Unknown error')
                    print(f"❌ API Error: {error}")
            else:
                print(f"❌ HTTP Error: {response.status_code}")
                print(f"📝 Response: {response.text[:200]}")
                
        except requests.exceptions.RequestException as e:
            print(f"❌ Request failed: {e}")
        except Exception as e:
            print(f"❌ Unexpected error: {e}")
    
    # Compare results
    print("\n" + "="*60)
    print("🔍 COMPARISON RESULTS")
    print("="*60)
    
    if len(results) > 1:
        data_sources = set()
        confidences = set()
        
        for date, result in results.items():
            data_sources.add(result['data_source'])
            confidences.add(result['confidence'])
            print(f"📅 {date}:")
            print(f"  🔗 Data Source: {result['data_source']}")
            print(f"  🎖️ Confidence: {result['confidence']}")
            print(f"  🎯 Predictions: {result['predictions_count']}")
            
        print(f"\n📊 Unique Data Sources: {len(data_sources)}")
        print(f"📊 Unique Confidences: {len(confidences)}")
        
        if len(data_sources) > 1:
            print("✅ SUCCESS: Different data sources for different dates!")
            print("✅ Date-specific analysis is working correctly!")
        else:
            print("⚠️ WARNING: Same data sources for all dates")
            
        if len(confidences) > 1:
            print("✅ SUCCESS: Different confidence scores!")
        else:
            print("⚠️ INFO: Same confidence scores")
    else:
        print("⚠️ Not enough successful results to compare")
    
    print("\n🏁 Testing completed")

if __name__ == "__main__":
    test_ajax_api()
