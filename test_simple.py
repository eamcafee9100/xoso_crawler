#!/usr/bin/env python3
"""
🔍 Simple Test - Check what's happening with Ultimate Prediction System
"""

import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'xoso_crawler.settings')
django.setup()

def test_ultimate_system():
    """Test Ultimate Prediction System step by step"""
    
    print("🔍 Testing Ultimate Prediction System Step by Step...")
    
    # Step 1: Test import
    print("\n📦 Step 1: Testing imports...")
    try:
        from analytic_frequence.ultimate_prediction_system import create_ultimate_prediction_system
        print("✅ create_ultimate_prediction_system imported successfully")
    except Exception as e:
        print(f"❌ Import failed: {e}")
        return False
    
    # Step 2: Test system creation
    print("\n🚀 Step 2: Testing system creation...")
    try:
        system = create_ultimate_prediction_system()
        print(f"✅ System created: {type(system)}")
        
        if system is None:
            print("❌ System is None")
            return False
            
        print(f"📋 System version: {getattr(system, 'system_version', 'unknown')}")
        print(f"🔧 System has ultimate_prediction_analysis: {hasattr(system, 'ultimate_prediction_analysis')}")
        
    except Exception as e:
        print(f"❌ System creation failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    # Step 3: Test data service  
    print("\n📊 Step 3: Testing data service...")
    try:
        from analytic_frequence.data_integration_service import RealDataIntegrationService
        
        data_service = RealDataIntegrationService()
        real_data = data_service.get_enhanced_lottery_input()
        lottery_numbers = real_data.get("lottery_numbers", [])
        
        print(f"✅ Data service working: got {len(lottery_numbers)} numbers")
        
        if len(lottery_numbers) < 5:
            print("⚠️ Using test data instead")
            lottery_numbers = [12, 25, 34, 8, 41, 17, 29, 3, 36, 22]
            
    except Exception as e:
        print(f"❌ Data service failed: {e}")
        lottery_numbers = [12, 25, 34, 8, 41, 17, 29, 3, 36, 22]
        print("🔄 Using fallback test data")
    
    # Step 4: Test prediction
    print(f"\n🔮 Step 4: Testing prediction with {len(lottery_numbers[:20])} numbers...")
    try:
        test_numbers = lottery_numbers[:20]
        print(f"📝 Test numbers: {test_numbers}")
        
        result = system.ultimate_prediction_analysis(
            lottery_numbers=test_numbers,
            prediction_horizon=5,
            include_explanations=True
        )
        
        print(f"✅ Prediction successful!")
        print(f"📋 Result type: {type(result)}")
        print(f"🎯 Confidence: {result.confidence_score:.3f}")
        print(f"⚡ Processing time: {result.processing_time_ms:.2f}ms")
        
        # Check predictions
        predictions = result.primary_predictions
        print(f"📊 Predictions: {type(predictions)}, count: {len(predictions) if hasattr(predictions, '__len__') else 'unknown'}")
        
        if predictions:
            first_pred = predictions[0]
            print(f"🔍 First prediction: {first_pred}")
            
            # Check if fallback
            if isinstance(first_pred, dict) and first_pred.get('prediction_type') == 'fallback':
                print("❌ STILL USING FALLBACK PREDICTIONS!")
                return False
            else:
                print("✅ USING REAL PREDICTIONS!")
                return True
        
    except Exception as e:
        print(f"❌ Prediction failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("🔧 Simple Ultimate Prediction Test")
    print("=" * 60)
    
    success = test_ultimate_system()
    
    print("\n" + "=" * 60)
    if success:
        print("🎉 SUCCESS: Real prediction system working!")
    else:
        print("❌ PROBLEM: Still issues with prediction system")
