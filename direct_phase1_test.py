#!/usr/bin/env python3
"""
🧪 PHASE 1 DIRECT TESTING - Test services directly
"""

import sys
import os

# Add the path for imports
project_root = r'c:\Users\n2t\Documents\xoso_crawler'
sys.path.insert(0, project_root)
sys.path.insert(0, os.path.join(project_root, 'predictions_tracker'))

def test_imports():
    """Test if all services can be imported"""
    print("Testing service imports...")
    
    try:
        # Test portfolio optimization
        from predictions_tracker.services.portfolio_optimization_service import (
            PortfolioOptimizationService, MethodPerformance, OptimizationResult, MarketRegimeEnum
        )
        print("✅ Portfolio Optimization Service import successful")
        
        # Test ML ensemble
        from predictions_tracker.services.ml_ensemble_service import (
            MLEnsembleService, ModelPrediction, EnsembleResult, MarketFeatures
        )
        print("✅ ML Ensemble Service import successful")
        
        # Test regime detection
        from predictions_tracker.services.regime_detection_service import (
            RegimeDetectionService, RegimeMetrics, RegimeState, MarketPhase
        )
        print("✅ Regime Detection Service import successful")
        
        return True
        
    except Exception as e:
        print(f"❌ Import error: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_instantiation():
    """Test if services can be instantiated"""
    print("\nTesting service instantiation...")
    
    try:
        from predictions_tracker.services.portfolio_optimization_service import PortfolioOptimizationService
        from predictions_tracker.services.ml_ensemble_service import MLEnsembleService
        from predictions_tracker.services.regime_detection_service import RegimeDetectionService
        
        # Test instantiation
        portfolio_service = PortfolioOptimizationService()
        print("✅ Portfolio Optimization Service instantiated")
        
        ml_service = MLEnsembleService()
        print("✅ ML Ensemble Service instantiated")
        
        regime_service = RegimeDetectionService()
        print("✅ Regime Detection Service instantiated")
        
        return True
        
    except Exception as e:
        print(f"❌ Instantiation error: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_basic_functionality():
    """Test basic functionality of services"""
    print("\nTesting basic functionality...")
    
    try:
        from predictions_tracker.services.portfolio_optimization_service import (
            PortfolioOptimizationService, MethodPerformance
        )
        from predictions_tracker.services.ml_ensemble_service import MLEnsembleService, MarketFeatures
        from predictions_tracker.services.regime_detection_service import (
            RegimeDetectionService, RegimeMetrics
        )
        
        # Test Portfolio Optimization
        portfolio_service = PortfolioOptimizationService()
        
        # Create sample data
        sample_performance = MethodPerformance(
            method_name="test_method",
            expected_return=0.6,
            volatility=0.2,
            hit_rate=0.65,
            sharpe_ratio=1.5,
            max_drawdown=0.1,
            confidence_score=0.8
        )
        
        performances = [sample_performance]
        correlation_result = portfolio_service.calculate_correlation_matrix_v3(performances)
        print("✅ Portfolio correlation matrix calculation works")
        
        # Test ML Ensemble
        ml_service = MLEnsembleService()
        models = ml_service.initialize_models('normal')
        print("✅ ML models initialization works")
        
        # Test Regime Detection
        regime_service = RegimeDetectionService()
        
        sample_metrics = RegimeMetrics(
            volatility=0.3,
            trend_strength=0.7,
            correlation_level=0.5,
            momentum=0.2,
            stability=0.6,
            data_quality=0.8
        )
        
        regime_type, confidence = regime_service.classify_regime(sample_metrics)
        print(f"✅ Regime classification works: {regime_type} ({confidence:.3f})")
        
        return True
        
    except Exception as e:
        print(f"❌ Functionality error: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run all tests"""
    print("🧪 PHASE 1 REVOLUTIONARY IMPROVEMENTS - DIRECT TESTING")
    print("=" * 70)
    
    tests = [
        ("Service Imports", test_imports),
        ("Service Instantiation", test_instantiation),
        ("Basic Functionality", test_basic_functionality)
    ]
    
    results = []
    for test_name, test_func in tests:
        print(f"\n📊 {test_name}...")
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} failed with exception: {e}")
            results.append((test_name, False))
    
    print("\n" + "=" * 70)
    print("🧪 PHASE 1 TESTING SUMMARY")
    print("=" * 70)
    
    passed = 0
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{test_name}: {status}")
        if result:
            passed += 1
    
    total = len(results)
    print(f"\nResult: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 ALL PHASE 1 TESTS PASSED!")
        print("✅ Portfolio Optimization Service: Ready")
        print("✅ ML Ensemble Service: Ready")
        print("✅ Regime Detection Service: Ready")
        print("✅ Data Structures: Compatible")
        print("\n🚀 PHASE 1 IMPLEMENTATION SUCCESSFUL!")
        print("Ready for Phase 2: Advanced Optimization Integration")
    else:
        print(f"\n⚠️ {total - passed} tests failed")
        print("Fix issues before proceeding to Phase 2")
        
    return passed == total

if __name__ == '__main__':
    main()
