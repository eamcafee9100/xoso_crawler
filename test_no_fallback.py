#!/usr/bin/env python3
"""
Final Test Script - Verify No More Fallback Predictions
"""

import requests
import json
import time

def test_ultimate_prediction_api():
    print("🎯 FINAL FALLBACK DETECTION TEST")
    print("=" * 60)
    
    url = "http://127.0.0.1:8000/analytic-frequence/ajax-prediction/"
    
    # Test multiple requests to ensure consistency
    for test_run in range(3):
        print(f"\n🧪 Test Run #{test_run + 1}")
        print("-" * 30)
        
        payload = {
            "prediction_date": "2025-08-13", 
            "prediction_horizon": 8,
            "use_real_data": True
        }
        
        try:
            response = requests.post(url, json=payload, timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                
                if data.get('success'):
                    prediction_data = data['prediction_data']
                    predictions = prediction_data['predictions']
                    
                    print(f"✅ Generated {len(predictions)} predictions")
                    print(f"📊 Confidence Score: {prediction_data['confidence_score']}")
                    print(f"⚡ Processing Time: {prediction_data['processing_time_ms']}ms")
                    
                    # CRITICAL CHECK: Look for fallback indicators
                    fallback_indicators = []
                    
                    for i, pred in enumerate(predictions):
                        # Check multiple fields for fallback indicators
                        analysis_source = pred.get('analysis_source', '').lower()
                        prediction_type = pred.get('prediction_type', '').lower()
                        prediction_strategy = pred.get('prediction_strategy', '').lower()
                        
                        # Look for any fallback signs
                        is_fallback = (
                            'fallback' in analysis_source or
                            'fallback' in prediction_type or
                            'fallback' in prediction_strategy or
                            analysis_source == 'fallback_prediction'
                        )
                        
                        if is_fallback:
                            fallback_indicators.append({
                                'prediction_index': i,
                                'number': pred['number'],
                                'analysis_source': analysis_source,
                                'prediction_type': prediction_type,
                                'prediction_strategy': prediction_strategy
                            })
                    
                    # Report results
                    if fallback_indicators:
                        print(f"❌ FALLBACK DETECTED! Found {len(fallback_indicators)} fallback predictions:")
                        for fb in fallback_indicators:
                            print(f"   - Prediction {fb['prediction_index'] + 1}: Number {fb['number']}")
                            print(f"     Source: {fb['analysis_source']}")
                            print(f"     Type: {fb['prediction_type']}")
                            print(f"     Strategy: {fb['prediction_strategy']}")
                    else:
                        print("✅ SUCCESS: NO FALLBACK PREDICTIONS DETECTED!")
                        
                    # Show sample predictions
                    print(f"\n🎲 Sample Predictions:")
                    for i, pred in enumerate(predictions[:3]):
                        print(f"   {i+1}. Number: {pred['number']}, Confidence: {pred['confidence']:.3f}")
                        print(f"      Source: {pred.get('analysis_source', 'N/A')}")
                        print(f"      Strategy: {pred.get('prediction_strategy', 'N/A')}")
                        
                else:
                    print(f"❌ API Error: {data.get('error', 'Unknown error')}")
                    
            else:
                print(f"❌ HTTP Error {response.status_code}: {response.text}")
                
        except requests.exceptions.RequestException as e:
            print(f"❌ Request failed: {e}")
        except Exception as e:
            print(f"❌ Unexpected error: {e}")
            
        # Small delay between tests
        if test_run < 2:
            time.sleep(1)
    
    print(f"\n{'='*60}")
    print("🏁 FINAL TEST COMPLETED!")
    print("📋 Summary: Check above for any ❌ FALLBACK DETECTED messages")
    print("✅ If all tests show 'NO FALLBACK PREDICTIONS DETECTED', the fix is successful!")

if __name__ == "__main__":
    test_ultimate_prediction_api()
