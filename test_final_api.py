#!/usr/bin/env python3
import urllib.request
import urllib.parse
import json
import time

def test_ultimate_prediction():
    """Simple test without external dependencies"""
    print("🧪 Testing Ultimate Prediction API")
    print("=" * 50)
    
    url = "http://127.0.0.1:8000/analytic-frequence/ajax-prediction/"
    
    # Create test data
    test_data = {
        "prediction_date": "2025-08-13",
        "prediction_horizon": 5,
        "use_real_data": True
    }
    
    # Convert to JSON bytes
    json_data = json.dumps(test_data).encode('utf-8')
    
    # Create request
    req = urllib.request.Request(
        url,
        data=json_data,
        headers={
            'Content-Type': 'application/json',
            'User-Agent': 'TestScript/1.0'
        },
        method='POST'
    )
    
    try:
        print("📡 Sending request...")
        start_time = time.time()
        
        with urllib.request.urlopen(req, timeout=30) as response:
            response_time = (time.time() - start_time) * 1000
            
            print(f"⏱️  Response time: {response_time:.2f}ms")
            print(f"📊 Status: {response.getcode()}")
            
            if response.getcode() == 200:
                # Read and parse response
                response_text = response.read().decode('utf-8')
                data = json.loads(response_text)
                
                if data.get('success'):
                    pred_data = data['prediction_data']
                    predictions = pred_data['predictions']
                    
                    print(f"✅ Success: {len(predictions)} predictions")
                    print(f"🎯 Confidence: {pred_data['confidence_score']}")
                    print(f"⚡ Processing: {pred_data['processing_time_ms']}ms")
                    
                    # Check for fallback
                    fallback_count = 0
                    real_count = 0
                    
                    print(f"\n🔍 Analyzing predictions:")
                    for i, pred in enumerate(predictions):
                        source = pred.get('analysis_source', '')
                        pred_type = pred.get('prediction_type', '')
                        strategy = pred.get('prediction_strategy', '')
                        
                        print(f"  {i+1}. Number: {pred['number']}, Confidence: {pred['confidence']:.3f}")
                        print(f"      Source: {source}")
                        
                        if 'fallback' in source.lower() or 'fallback' in pred_type.lower():
                            fallback_count += 1
                            print(f"      ❌ FALLBACK DETECTED!")
                        else:
                            real_count += 1
                            print(f"      ✅ Real prediction")
                    
                    print(f"\n📊 SUMMARY:")
                    print(f"   Real predictions: {real_count}")
                    print(f"   Fallback predictions: {fallback_count}")
                    
                    if fallback_count == 0:
                        print(f"   🎉 SUCCESS: NO FALLBACK PREDICTIONS!")
                    else:
                        print(f"   ⚠️  WARNING: {fallback_count} fallback predictions found")
                        
                else:
                    print(f"❌ API Error: {data.get('error', 'Unknown')}")
            else:
                print(f"❌ HTTP Error: {response.getcode()}")
                
    except urllib.error.HTTPError as e:
        print(f"❌ HTTP Error: {e.code} - {e.reason}")
    except urllib.error.URLError as e:
        print(f"❌ URL Error: {e.reason}")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    print(f"\n{'='*50}")

if __name__ == "__main__":
    test_ultimate_prediction()
