#!/usr/bin/env python3
"""
🧪 SIMPLE PHASE 1 TESTING - Test core functionality
"""

import sys
import os
from datetime import datetime

def test_portfolio_optimization():
    """Test portfolio optimization service basic functionality"""
    try:
        sys.path.append(os.path.join(os.path.dirname(__file__), 'predictions_tracker', 'services'))
        
        print("Testing Portfolio Optimization Service...")
        
        # Test basic imports
        try:
            from portfolio_optimization_service import PortfolioOptimizationService
            print("✅ PortfolioOptimizationService import successful")
        except Exception as e:
            print(f"❌ Import error: {e}")
            return False
        
        # Test service instantiation
        try:
            service = PortfolioOptimizationService()
            print("✅ Service instantiation successful")
        except Exception as e:
            print(f"❌ Instantiation error: {e}")
            return False
        
        # Test method availability
        methods = ['calculate_correlation_matrix_v3', 'markowitz_optimization_v3', 'calculate_kelly_criterion_v3']
        for method in methods:
            if hasattr(service, method):
                print(f"✅ Method {method} available")
            else:
                print(f"❌ Method {method} missing")
                return False
        
        return True
        
    except Exception as e:
        print(f"❌ Portfolio optimization test failed: {e}")
        return False

def test_ml_ensemble():
    """Test ML ensemble service basic functionality"""
    try:
        sys.path.append(os.path.join(os.path.dirname(__file__), 'predictions_tracker', 'services'))
        
        print("\nTesting ML Ensemble Service...")
        
        # Test basic imports
        try:
            from ml_ensemble_service import MLEnsembleService
            print("✅ MLEnsembleService import successful")
        except Exception as e:
            print(f"❌ Import error: {e}")
            return False
        
        # Test service instantiation
        try:
            service = MLEnsembleService()
            print("✅ Service instantiation successful")
        except Exception as e:
            print(f"❌ Instantiation error: {e}")
            return False
        
        # Test method availability
        methods = ['initialize_models', 'extract_comprehensive_features', 'ml_ensemble_scoring_v3']
        for method in methods:
            if hasattr(service, method):
                print(f"✅ Method {method} available")
            else:
                print(f"❌ Method {method} missing")
                return False
        
        return True
        
    except Exception as e:
        print(f"❌ ML ensemble test failed: {e}")
        return False

def test_regime_detection():
    """Test regime detection service basic functionality"""
    try:
        sys.path.append(os.path.join(os.path.dirname(__file__), 'predictions_tracker', 'services'))
        
        print("\nTesting Regime Detection Service...")
        
        # Test basic imports
        try:
            from regime_detection_service import RegimeDetectionService
            print("✅ RegimeDetectionService import successful")
        except Exception as e:
            print(f"❌ Import error: {e}")
            return False
        
        # Test service instantiation
        try:
            service = RegimeDetectionService()
            print("✅ Service instantiation successful")
        except Exception as e:
            print(f"❌ Instantiation error: {e}")
            return False
        
        # Test method availability
        methods = ['calculate_regime_metrics', 'classify_regime', 'detect_regime_v3']
        for method in methods:
            if hasattr(service, method):
                print(f"✅ Method {method} available")
            else:
                print(f"❌ Method {method} missing")
                return False
        
        return True
        
    except Exception as e:
        print(f"❌ Regime detection test failed: {e}")
        return False

def test_data_structures():
    """Test data structure compatibility"""
    try:
        sys.path.append(os.path.join(os.path.dirname(__file__), 'predictions_tracker', 'services'))
        
        print("\nTesting Data Structure Compatibility...")
        
        # Test dataclass imports
        try:
            from portfolio_optimization_service import MethodPerformance, OptimizationResult
            from ml_ensemble_service import ModelPrediction, EnsembleResult, MarketFeatures
            from regime_detection_service import RegimeMetrics, RegimeState, MarketPhase
            print("✅ All dataclass imports successful")
        except Exception as e:
            print(f"❌ Dataclass import error: {e}")
            return False
        
        # Test dataclass instantiation
        try:
            # Test MethodPerformance
            perf = MethodPerformance(
                method_name="test",
                expected_return=0.6,
                volatility=0.2,
                hit_rate=0.65,
                sharpe_ratio=1.5,
                max_drawdown=0.1,
                confidence_score=0.8
            )
            print("✅ MethodPerformance creation successful")
            
            # Test MarketFeatures
            features = MarketFeatures(
                regime='bull',
                volatility=0.3,
                trend_strength=0.7,
                correlation_level=0.5,
                data_quality=0.8,
                temporal_consistency=0.7
            )
            print("✅ MarketFeatures creation successful")
            
            # Test RegimeMetrics
            metrics = RegimeMetrics(
                volatility=0.3,
                trend_strength=0.7,
                correlation_level=0.5,
                momentum=0.2,
                stability=0.6,
                data_quality=0.8
            )
            print("✅ RegimeMetrics creation successful")
            
        except Exception as e:
            print(f"❌ Dataclass instantiation error: {e}")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Data structure test failed: {e}")
        return False

def main():
    """Run all basic tests"""
    print("🧪 STARTING PHASE 1 BASIC FUNCTIONALITY TESTING")
    print("=" * 60)
    
    tests = [
        ("Portfolio Optimization", test_portfolio_optimization),
        ("ML Ensemble", test_ml_ensemble), 
        ("Regime Detection", test_regime_detection),
        ("Data Structures", test_data_structures)
    ]
    
    results = []
    for test_name, test_func in tests:
        print(f"\n📊 Running {test_name} Test...")
        try:
            result = test_func()
            results.append((test_name, result))
            if result:
                print(f"✅ {test_name} test PASSED")
            else:
                print(f"❌ {test_name} test FAILED")
        except Exception as e:
            print(f"❌ {test_name} test ERROR: {e}")
            results.append((test_name, False))
    
    print("\n" + "=" * 60)
    print("🧪 PHASE 1 BASIC TESTING SUMMARY")
    print("=" * 60)
    
    passed = sum(1 for name, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{test_name}: {status}")
    
    print(f"\nTotal: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 ALL PHASE 1 BASIC TESTS PASSED!")
        print("✅ Services are ready for integration")
        print("✅ Data structures are compatible")
        print("✅ Ready to proceed with Phase 2")
    else:
        print(f"\n⚠️ {total - passed} tests failed")
        print("❌ Fix issues before proceeding")
    
    return passed == total

if __name__ == '__main__':
    success = main()
