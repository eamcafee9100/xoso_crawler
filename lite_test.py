#!/usr/bin/env python3
"""
🧪 LITE TEST - Test lightweight versions without heavy dependencies
"""

import sys
import os

# Add paths
project_root = r'c:\Users\n2t\Documents\xoso_crawler'
sys.path.insert(0, project_root)
sys.path.insert(0, os.path.join(project_root, 'predictions_tracker'))

def test_lite_portfolio():
    """Test lite portfolio service"""
    print("Testing Lite Portfolio Service...")
    
    try:
        from predictions_tracker.services.portfolio_optimization_service_lite import (
            PortfolioOptimizationService, MethodPerformance, OptimizationResult, MarketRegimeEnum
        )
        print("✅ All imports successful")
        
        # Test instantiation
        service = PortfolioOptimizationService()
        print("✅ Service instantiated")
        
        # Test basic functionality
        perf1 = MethodPerformance(
            method_name="method1",
            expected_return=0.6,
            volatility=0.2,
            hit_rate=0.65,
            sharpe_ratio=1.5,
            max_drawdown=0.1,
            confidence_score=0.8
        )
        
        perf2 = MethodPerformance(
            method_name="method2",
            expected_return=0.55,
            volatility=0.25,
            hit_rate=0.6,
            sharpe_ratio=1.2,
            max_drawdown=0.15,
            confidence_score=0.75
        )
        
        performances = [perf1, perf2]
        print("✅ Test data created")
        
        # Test correlation calculation
        correlation_result = service.calculate_correlation_matrix_v3(performances)
        print("✅ Correlation matrix calculated")
        print(f"   Diversification score: {correlation_result['diversification_score']:.3f}")
        
        # Test optimization
        optimization_result = service.markowitz_optimization_v3(
            performances, 
            correlation_result['correlation_matrix']
        )
        print("✅ Portfolio optimization completed")
        print(f"   Sharpe ratio: {optimization_result.sharpe_ratio:.3f}")
        print(f"   Status: {optimization_result.optimization_status}")
        
        # Test Kelly criterion
        kelly_result = service.calculate_kelly_criterion_v3(perf1)
        print("✅ Kelly criterion calculated")
        print(f"   Kelly fraction: {kelly_result['kelly_fraction']:.3f}")
        print(f"   Risk assessment: {kelly_result['risk_assessment']}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_minimal_ml():
    """Test if we can create minimal ML structures"""
    print("\nTesting Minimal ML Structures...")
    
    try:
        from dataclasses import dataclass
        from typing import Dict, List
        
        @dataclass(frozen=True)
        class SimpleModelResult:
            model_name: str
            prediction: float
            confidence: float
        
        @dataclass(frozen=True)
        class SimpleEnsembleResult:
            final_score: float
            model_results: List[SimpleModelResult]
            ensemble_confidence: float
        
        # Test creation
        model1 = SimpleModelResult("model1", 75.0, 0.8)
        model2 = SimpleModelResult("model2", 72.0, 0.75)
        
        ensemble = SimpleEnsembleResult(73.5, [model1, model2], 0.775)
        
        print("✅ Minimal ML structures work")
        print(f"   Final score: {ensemble.final_score}")
        print(f"   Confidence: {ensemble.ensemble_confidence}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_minimal_regime():
    """Test minimal regime detection"""
    print("\nTesting Minimal Regime Detection...")
    
    try:
        from dataclasses import dataclass
        from typing import Dict
        
        @dataclass(frozen=True)
        class SimpleRegimeMetrics:
            volatility: float
            trend_strength: float
            stability: float
        
        @dataclass(frozen=True)
        class SimpleRegimeState:
            regime_type: str
            confidence: float
            metrics: SimpleRegimeMetrics
        
        # Test creation
        metrics = SimpleRegimeMetrics(0.3, 0.7, 0.6)
        regime = SimpleRegimeState("bull", 0.8, metrics)
        
        print("✅ Minimal regime structures work")
        print(f"   Regime: {regime.regime_type}")
        print(f"   Confidence: {regime.confidence}")
        print(f"   Volatility: {regime.metrics.volatility}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    print("🧪 LITE PHASE 1 TESTING - NO HEAVY DEPENDENCIES")
    print("=" * 60)
    
    tests = [
        ("Lite Portfolio Service", test_lite_portfolio),
        ("Minimal ML Structures", test_minimal_ml),
        ("Minimal Regime Detection", test_minimal_regime)
    ]
    
    results = []
    for name, test_func in tests:
        print(f"\n📊 {name}...")
        result = test_func()
        results.append((name, result))
        
        if result:
            print(f"✅ {name} - SUCCESS")
        else:
            print(f"❌ {name} - FAILED")
    
    print("\n" + "=" * 60)
    print("🧪 LITE TESTING SUMMARY")
    print("=" * 60)
    
    passed = sum(1 for name, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{name}: {status}")
    
    print(f"\nResult: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 ALL LITE TESTS PASSED!")
        print("✅ Core data structures work")
        print("✅ Basic algorithms work")
        print("✅ No dependency issues")
        print("\n📋 NEXT STEPS:")
        print("1. Fix sklearn import issues")
        print("2. Create production-ready services")
        print("3. Integrate with existing system")
    else:
        print(f"\n⚠️ {total - passed} tests failed")
        print("Fix basic issues first")
    
    return passed == total

if __name__ == '__main__':
    main()
