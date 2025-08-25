#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
🔧 TEST REAL AJAX: Test the actual AJAX endpoint with date
"""

import requests
import json

def test_real_ajax():
    """Test the actual AJAX endpoint that frontend uses"""
    print("🧪 TESTING REAL AJAX ENDPOINT")
    print("="*60)
    
    url = "http://127.0.0.1:8000/analytic-frequence/ajax-prediction/"
    
    test_cases = [
        {"date": "2025-08-12", "desc": "Latest date"},
        {"date": "2025-08-06", "desc": "One week ago"},
        {"date": "2025-07-15", "desc": "One month ago"},
    ]
    
    results = {}
    
    for case in test_cases:
        date = case["date"]
        desc = case["desc"]
        
        print(f"\n📅 Testing {desc}: {date}")
        print("-" * 40)
        
        payload = {
            "prediction_date": date,
            "prediction_horizon": 3,
            "use_real_data": True
        }
        
        try:
            response = requests.post(
                url,
                json=payload,
                headers={'Content-Type': 'application/json'},
                timeout=30
            )
            
            print(f"📊 Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                success = data.get('success', False)
                print(f"✅ Success: {success}")
                
                if success:
                    pred_data = data['prediction_data']
                    data_source = pred_data.get('data_source', 'unknown')
                    prediction_date = pred_data.get('prediction_date', 'none')
                    confidence = pred_data.get('confidence_score', 0)
                    predictions = pred_data.get('predictions', [])
                    
                    print(f"🔗 Data Source: {data_source}")
                    print(f"📅 Prediction Date: {prediction_date}")
                    print(f"🎖️ Confidence: {confidence}")
                    print(f"🎯 Predictions: {len(predictions)}")
                    
                    if predictions:
                        print(f"🔢 First Prediction: {predictions[0]}")
                    
                    results[date] = {
                        'data_source': data_source,
                        'prediction_date': prediction_date,
                        'confidence': confidence,
                        'predictions_count': len(predictions)
                    }
                    
                else:
                    error = data.get('error', 'Unknown error')
                    print(f"❌ API Error: {error}")
            else:
                print(f"❌ HTTP Error: {response.status_code}")
                print(f"📝 Response: {response.text[:300]}")
                
        except requests.exceptions.RequestException as e:
            print(f"❌ Request failed: {e}")
        except Exception as e:
            print(f"❌ Unexpected error: {e}")
    
    # Compare results
    print(f"\n🔍 COMPARISON RESULTS")
    print("="*60)
    
    if len(results) >= 2:
        data_sources = set()
        confidences = set()
        prediction_dates = set()
        
        for date, result in results.items():
            data_sources.add(result['data_source'])
            confidences.add(result['confidence'])
            prediction_dates.add(result['prediction_date'])
            print(f"📅 {date}:")
            print(f"  🔗 Data Source: {result['data_source']}")
            print(f"  📅 Prediction Date: {result['prediction_date']}")
            print(f"  🎖️ Confidence: {result['confidence']}")
        
        print(f"\n📊 Summary:")
        print(f"  • Unique data sources: {len(data_sources)}")
        print(f"  • Unique confidences: {len(confidences)}")
        print(f"  • Unique prediction dates: {len(prediction_dates)}")
        
        if len(data_sources) > 1:
            print("✅ SUCCESS: AJAX endpoint returns different data sources!")
            print("✅ Date-specific analysis working in AJAX!")
            print("\n🔍 Frontend issue likely:")
            print("  • Check browser cache")
            print("  • Check JavaScript console for errors")
            print("  • Verify date input is being sent correctly")
        else:
            print("❌ PROBLEM: AJAX endpoint returns same data sources")
            print("🔍 Backend issue despite debug success")
            
    else:
        print("⚠️ Not enough successful results to compare")
    
    print(f"\n🏁 AJAX Testing completed")

if __name__ == "__main__":
    test_real_ajax()
