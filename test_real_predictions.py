#!/usr/bin/env python3
"""Test the real prediction system to ensure no fallbacks"""

import os
import django
import sys
import json
from pathlib import Path

# Setup Django
sys.path.append(os.path.dirname(__file__))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "xoso_crawler.settings")
django.setup()

from analytic_frequence.ultimate_prediction_system import UltimatePredictionSystem
from analytic_frequence.services import ServiceManager

def test_real_predictions():
    """Test that the system generates real predictions"""
    print("🔮 Testing Real Ultimate Prediction System...")
    
    try:
        # Initialize prediction system
        print("📋 Initializing Ultimate Prediction System...")
        system = UltimatePredictionSystem()
        
        # Test with sample lottery data
        sample_data = list(range(10, 90, 3))  # [10, 13, 16, 19, ...]
        print(f"📊 Using sample data: {sample_data[:10]}... (length: {len(sample_data)})")
        
        # Generate predictions
        print("🎯 Generating predictions...")
        results = system.generate_ultimate_prediction(
            lottery_numbers=sample_data,
            num_predictions=10
        )
        
        print(f"\n✅ Prediction generation completed!")
        print(f"📦 Results type: {type(results)}")
        
        if isinstance(results, dict):
            print(f"🔑 Keys in results: {list(results.keys())}")
            
            # Check for predictions
            if 'predictions' in results:
                predictions = results['predictions']
                print(f"🎯 Number of predictions: {len(predictions)}")
                
                # Check first few predictions
                for i, pred in enumerate(predictions[:5]):
                    print(f"  Prediction {i+1}: {pred}")
                    
                    # Check if it's NOT a fallback
                    if 'prediction_type' in pred and pred['prediction_type'] == 'fallback':
                        print(f"  ❌ WARNING: Found fallback prediction!")
                    elif pred.get('analysis_source') == 'fallback_prediction':
                        print(f"  ❌ WARNING: Found fallback source!")
                    else:
                        print(f"  ✅ Real prediction confirmed")
                        
            # Check insights
            insights_keys = ['quantum_insights', 'neural_insights', 'ensemble_insights']
            for key in insights_keys:
                if key in results:
                    print(f"📊 {key}: {type(results[key])} with {len(results[key])} items")
                    
        else:
            print(f"❌ Unexpected result type: {type(results)}")
            print(f"Raw result: {results}")
            
    except Exception as e:
        print(f"❌ Error during testing: {e}")
        import traceback
        traceback.print_exc()
        
    print("\n🏁 Test completed!")

if __name__ == "__main__":
    test_real_predictions()
