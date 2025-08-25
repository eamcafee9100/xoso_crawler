import sys
print("Python version:", sys.version)
print("Testing basic imports...")

try:
    import numpy as np
    print("✅ numpy imported")
except Exception as e:
    print("❌ numpy error:", e)

try:
    import os
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "xoso_crawler.settings")
    print("✅ Django settings configured")
except Exception as e:
    print("❌ Django settings error:", e)

try:
    import django
    django.setup()
    print("✅ Django setup completed")
except Exception as e:
    print("❌ Django setup error:", e)

try:
    from analytic_frequence.ultimate_prediction_system import UltimatePredictionSystem
    print("✅ UltimatePredictionSystem imported")
    
    # Quick test
    system = UltimatePredictionSystem()
    print("✅ UltimatePredictionSystem initialized")
    
    # Test method generation
    test_numbers = [10, 15, 20, 25, 30, 35, 40]
    result = system._generate_ultimate_predictions(
        lottery_numbers=test_numbers,
        information_insights={"entropy": 0.7},
        time_crystal_insights={"crystal_strength": 0.5},
        quantum_insights={"entanglement_score": 0.6},
        neural_insights={"pattern_strength": 0.8},
        ensemble_insights={"consensus_confidence": 0.7},
        consciousness_insights={"consciousness_level": 0.5},
        prediction_horizon=5
    )
    
    print(f"✅ Generated {len(result)} predictions")
    print("First prediction:", result[0] if result else "None")
    
    # Check for fallback indicators
    for i, pred in enumerate(result[:3]):
        source = pred.get('analysis_source', 'unknown')
        print(f"Prediction {i+1} source: {source}")
        if 'fallback' in source.lower():
            print(f"  ⚠️ Fallback detected!")
        else:
            print(f"  ✅ Real prediction confirmed")
    
except Exception as e:
    print("❌ UltimatePredictionSystem error:", e)
    import traceback
    traceback.print_exc()

print("🏁 Test completed!")
