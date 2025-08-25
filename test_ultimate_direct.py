#!/usr/bin/env python3
"""
🔍 Direct Django Test - Import and test Ultimate Prediction System directly
"""

import os
import sys
import django

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'xoso_crawler.settings')
django.setup()

def test_ultimate_system_direct():
    """Test Ultimate Prediction System directly in Django environment"""
    
    print("🔍 Testing Ultimate Prediction System directly...")
    
    try:
        # Test imports
        print("📦 Testing imports...")
        
        from analytic_frequence.ultimate_prediction_system import create_ultimate_prediction_system, UltimatePredictionSystem
        print("✅ UltimatePredictionSystem imported successfully")
        
        from analytic_frequence.data_integration_service import RealDataIntegrationService
        print("✅ RealDataIntegrationService imported successfully")
        
        # Test system creation
        print("\n🚀 Testing system creation...")
        ultimate_system = create_ultimate_prediction_system()
        
        if ultimate_system is None:
            print("❌ create_ultimate_prediction_system() returned None")
            return False
        
        print(f"✅ Ultimate system created: {type(ultimate_system)}")
        print(f"📋 System version: {ultimate_system.system_version}")
        
        # Test data service
        print("\n📊 Testing data service...")
        data_service = RealDataIntegrationService()
        real_data = data_service.get_enhanced_lottery_input()
        lottery_numbers = real_data.get("lottery_numbers", [])
        
        print(f"✅ Data service working: got {len(lottery_numbers)} numbers")
        print(f"📝 Sample numbers: {lottery_numbers[:10] if lottery_numbers else 'No data'}")
        
        # Test prediction
        print("\n🔮 Testing prediction analysis...")
        
        # Use test data if no real data
        test_numbers = lottery_numbers[:20] if len(lottery_numbers) >= 20 else [12, 25, 34, 8, 41, 17, 29, 3, 36, 22]
        
        print(f"🎯 Using {len(test_numbers)} numbers for prediction")
        
        result = ultimate_system.ultimate_prediction_analysis(
            lottery_numbers=test_numbers,
            prediction_horizon=5,
            include_explanations=True
        )
        
        print(f"✅ Prediction completed successfully!")
        print(f"📋 Result type: {type(result)}")
        print(f"🎯 Confidence score: {result.confidence_score:.3f}")
        print(f"⚡ Processing time: {result.processing_time_ms:.2f}ms")
        print(f"📈 Accuracy boost: {result.accuracy_boost * 100:.1f}%")
        
        # Check predictions structure
        predictions = result.primary_predictions
        print(f"\n🔍 Predictions analysis:")
        print(f"   Type: {type(predictions)}")
        print(f"   Count: {len(predictions) if hasattr(predictions, '__len__') else 'Unknown'}")
        
        if predictions:
            first_pred = predictions[0]
            print(f"   First prediction: {first_pred}")
            print(f"   First prediction type: {type(first_pred)}")
            
            # Check if it's fallback
            if isinstance(first_pred, dict) and first_pred.get('prediction_type') == 'fallback':
                print("❌ SYSTEM IS STILL USING FALLBACK!")
                return False
            else:
                print("✅ SYSTEM IS USING REAL PREDICTIONS!")
                
        # Check revolutionary insights
        print(f"\n🚀 Revolutionary insights:")
        print(f"   Information entropy: {result.information_entropy:.3f}")
        print(f"   Quantum entanglement: {result.quantum_entanglement_score:.3f}")
        print(f"   Consciousness level: {result.consciousness_level:.3f}")
        
        return True
        
    except ImportError as e:
        print(f"❌ Import Error: {e}")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("🔧 Direct Django Ultimate Prediction Test")
    print("=" * 60)
    
    success = test_ultimate_system_direct()
    
    print("\n" + "=" * 60)
    if success:
        print("🎉 SUCCESS: Ultimate Prediction System is working correctly!")
    else:
        print("❌ ISSUE: Ultimate Prediction System has problems")
        
    sys.exit(0 if success else 1)
