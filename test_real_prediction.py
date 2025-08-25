#!/usr/bin/env python3
"""
🔍 Test Ultimate Prediction System - Check if it's using real predictions or fallback
"""

import requests
import json
import sys

def test_ajax_prediction():
    """Test if AJAX API is using real prediction system or fallback"""
    
    url = "http://127.0.0.1:8000/analytic-frequence/ajax-prediction/"
    
    test_payload = {
        "prediction_date": "2025-08-14",
        "prediction_horizon": 5,
        "use_real_data": True
    }
    
    print("🧪 Testing AJAX Prediction API...")
    print(f"URL: {url}")
    print(f"Payload: {json.dumps(test_payload, indent=2)}")
    
    try:
        response = requests.post(
            url,
            json=test_payload,
            headers={
                'Content-Type': 'application/json',
                'Accept': 'application/json'
            },
            timeout=30
        )
        
        print(f"\n📊 Response Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            
            if data.get('success'):
                print("✅ API Request successful!")
                
                pred_data = data.get('prediction_data', {})
                
                # Check if using fallback or real system
                predictions = pred_data.get('predictions', [])
                data_source = pred_data.get('data_source', 'unknown')
                system_version = pred_data.get('system_version', 'unknown')
                
                print(f"\n🔍 System Analysis:")
                print(f"  Data Source: {data_source}")
                print(f"  System Version: {system_version}")
                print(f"  Number of predictions: {len(predictions)}")
                
                # Check prediction structure to identify fallback vs real
                if predictions:
                    first_pred = predictions[0]
                    print(f"  Sample prediction: {first_pred}")
                    
                    # Fallback predictions have "prediction_type": "fallback"
                    if isinstance(first_pred, dict) and first_pred.get('prediction_type') == 'fallback':
                        print("❌ SYSTEM IS USING FALLBACK PREDICTION!")
                        print("   This means UltimatePredictionSystem is not working properly")
                        return False
                    else:
                        print("✅ SYSTEM IS USING REAL PREDICTION SYSTEM!")
                        print("   UltimatePredictionSystem is working correctly")
                        
                        # Check revolutionary insights
                        insights = pred_data.get('revolutionary_insights', {})
                        print(f"\n🚀 Revolutionary Insights:")
                        for key, value in insights.items():
                            print(f"    {key}: {value}")
                        
                        return True
                else:
                    print("⚠️ No predictions returned")
                    return False
                
            else:
                print(f"❌ API Error: {data.get('error', 'Unknown error')}")
                return False
                
        else:
            print(f"❌ HTTP Error: {response.status_code}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ Connection Error: Make sure Django server is running")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    print("🔧 Ultimate Prediction System Test")
    print("=" * 50)
    
    success = test_ajax_prediction()
    
    print("\n" + "=" * 50)
    if success:
        print("🎉 SUCCESS: Real prediction system is working!")
        sys.exit(0)
    else:
        print("❌ ISSUE: System is still using fallback predictions")
        sys.exit(1)
