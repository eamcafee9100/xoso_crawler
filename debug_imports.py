#!/usr/bin/env python3
"""
🧪 DEBUG TEST - Test imports step by step
"""

import sys
import os

# Add paths
project_root = r'c:\Users\n2t\Documents\xoso_crawler'
sys.path.insert(0, project_root)
sys.path.insert(0, os.path.join(project_root, 'predictions_tracker'))

def test_portfolio_import():
    """Test portfolio service import step by step"""
    print("Testing Portfolio Service imports...")
    
    try:
        print("Step 1: Import service class...")
        from predictions_tracker.services.portfolio_optimization_service import PortfolioOptimizationService
        print("✅ PortfolioOptimizationService imported")
        
        print("Step 2: Import MethodPerformance...")
        from predictions_tracker.services.portfolio_optimization_service import MethodPerformance
        print("✅ MethodPerformance imported")
        
        print("Step 3: Import OptimizationResult...")
        from predictions_tracker.services.portfolio_optimization_service import OptimizationResult
        print("✅ OptimizationResult imported")
        
        print("Step 4: Import MarketRegimeEnum...")
        from predictions_tracker.services.portfolio_optimization_service import MarketRegimeEnum
        print("✅ MarketRegimeEnum imported")
        
        print("Step 5: Test instantiation...")
        service = PortfolioOptimizationService()
        print("✅ Service instantiated")
        
        print("Step 6: Test data structure...")
        perf = MethodPerformance(
            method_name="test",
            expected_return=0.6,
            volatility=0.2,
            hit_rate=0.65,
            sharpe_ratio=1.5,
            max_drawdown=0.1,
            confidence_score=0.8
        )
        print("✅ MethodPerformance created")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_ml_import():
    """Test ML service import step by step"""
    print("\nTesting ML Service imports...")
    
    try:
        print("Step 1: Import service class...")
        from predictions_tracker.services.ml_ensemble_service import MLEnsembleService
        print("✅ MLEnsembleService imported")
        
        print("Step 2: Import ModelPrediction...")
        from predictions_tracker.services.ml_ensemble_service import ModelPrediction
        print("✅ ModelPrediction imported")
        
        print("Step 3: Import EnsembleResult...")
        from predictions_tracker.services.ml_ensemble_service import EnsembleResult
        print("✅ EnsembleResult imported")
        
        print("Step 4: Import MarketFeatures...")
        from predictions_tracker.services.ml_ensemble_service import MarketFeatures
        print("✅ MarketFeatures imported")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_regime_import():
    """Test regime service import step by step"""
    print("\nTesting Regime Service imports...")
    
    try:
        print("Step 1: Import service class...")
        from predictions_tracker.services.regime_detection_service import RegimeDetectionService
        print("✅ RegimeDetectionService imported")
        
        print("Step 2: Import RegimeMetrics...")
        from predictions_tracker.services.regime_detection_service import RegimeMetrics
        print("✅ RegimeMetrics imported")
        
        print("Step 3: Import RegimeState...")
        from predictions_tracker.services.regime_detection_service import RegimeState
        print("✅ RegimeState imported")
        
        print("Step 4: Import MarketPhase...")
        from predictions_tracker.services.regime_detection_service import MarketPhase
        print("✅ MarketPhase imported")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    print("🔍 DEBUG TEST - STEP BY STEP IMPORT TESTING")
    print("=" * 60)
    
    tests = [
        ("Portfolio Service", test_portfolio_import),
        ("ML Service", test_ml_import),
        ("Regime Service", test_regime_import)
    ]
    
    for name, test_func in tests:
        print(f"\n🧪 {name}...")
        result = test_func()
        if result:
            print(f"✅ {name} - ALL IMPORTS SUCCESSFUL")
        else:
            print(f"❌ {name} - IMPORT FAILED")
            break
    
    print("\n" + "=" * 60)
    print("DEBUG TEST COMPLETE")

if __name__ == '__main__':
    main()
