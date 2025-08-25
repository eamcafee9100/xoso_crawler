import json
import time

# Simple test using built-in urllib
try:
    import urllib.request
    import urllib.parse
    
    print("🧪 Testing Ultimate Prediction API")
    print("=" * 50)
    
    url = "http://127.0.0.1:8000/analytic-frequence/ajax-prediction/"
    
    test_data = {
        "prediction_date": "2025-08-13",
        "prediction_horizon": 5,
        "use_real_data": True
    }
    
    # Convert to JSON
    data = json.dumps(test_data).encode('utf-8')
    
    # Create request
    req = urllib.request.Request(
        url, 
        data=data, 
        headers={
            'Content-Type': 'application/json',
            'X-CSRFToken': 'test'  # Django might need this
        },
        method='POST'
    )
    
    print("📋 Sending test request...")
    start_time = time.time()
    
    # Send request
    with urllib.request.urlopen(req, timeout=30) as response:
        response_time = (time.time() - start_time) * 1000
        
        print(f"⏱️  Response time: {response_time:.2f}ms")
        print(f"📊 Status code: {response.getcode()}")
        
        if response.getcode() == 200:
            response_data = json.loads(response.read().decode('utf-8'))
            
            if response_data.get('success'):
                prediction_data = response_data['prediction_data']
                
                print(f"✅ Success: {len(prediction_data['predictions'])} predictions generated")
                print(f"🎯 Confidence score: {prediction_data['confidence_score']}")
                print(f"📈 Accuracy boost: {prediction_data['accuracy_boost']}%")
                print(f"⚡ Processing time: {prediction_data['processing_time_ms']}ms")
                print(f"📊 Data source: {prediction_data['data_source']}")
                
                print(f"\n🎲 Top 3 Predictions:")
                for j, pred in enumerate(prediction_data['predictions'][:3]):
                    source = pred.get('analysis_source', 'unknown')
                    pred_type = pred.get('prediction_type', 'unknown')
                    strategy = pred.get('prediction_strategy', 'unknown')
                    
                    print(f"  {j+1}. Number: {pred['number']}, Confidence: {pred['confidence']:.3f}")
                    print(f"      Source: {source}, Type: {pred_type}, Strategy: {strategy}")
                    
                    # Check for fallback
                    if 'fallback' in source.lower() or 'fallback' in pred_type.lower():
                        print(f"      ❌ FALLBACK DETECTED!")
                    else:
                        print(f"      ✅ Real prediction confirmed")
                        
                print(f"\n🔬 Revolutionary Insights:")
                insights = prediction_data['revolutionary_insights']
                print(f"  - Information Entropy: {insights['information_entropy']}")
                print(f"  - Quantum Entanglement: {insights['quantum_entanglement_score']}")
                print(f"  - Consciousness Level: {insights['consciousness_level']}")
                
                # Final verdict
                has_fallback = any(
                    'fallback' in pred.get('analysis_source', '').lower() or 
                    'fallback' in pred.get('prediction_type', '').lower()
                    for pred in prediction_data['predictions']
                )
                
                if has_fallback:
                    print(f"\n❌ SYSTEM STILL USING FALLBACK PREDICTIONS!")
                else:
                    print(f"\n✅ SUCCESS: ALL PREDICTIONS ARE REAL!")
                
            else:
                print(f"❌ API Error: {response_data.get('error', 'Unknown error')}")
        else:
            print(f"❌ HTTP Error: {response.getcode()}")
            
except Exception as e:
    print(f"❌ Test failed: {e}")
    import traceback
    traceback.print_exc()

print(f"\n{'='*50}")
print("🧪 Test completed!")
