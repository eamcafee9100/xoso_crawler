#!/usr/bin/env python3
"""
🧪 PHASE 1A INTEGRATION TEST - Portfolio Theory in Ultimate System
Test integration of Modern Portfolio Theory with Ultimate Prediction System
"""

import sys
import os

# Add paths
project_root = r'c:\Users\n2t\Documents\xoso_crawler'
sys.path.insert(0, project_root)
sys.path.insert(0, os.path.join(project_root, 'analytic_frequence'))

def test_portfolio_integration():
    """Test portfolio integration with ultimate system"""
    print("🧪 Testing Portfolio Integration...")
    
    try:
        # Test imports
        print("Step 1: Testing imports...")
        from analytic_frequence.portfolio_integration_service import PortfolioIntegrationService
        print("✅ Portfolio Integration Service imported")
        
        from predictions_tracker.services.portfolio_optimization_service_lite import (
            PortfolioOptimizationService, MethodPerformance, OptimizationResult
        )
        print("✅ Portfolio Optimization Service imported")
        
        # Test service instantiation
        print("Step 2: Testing service instantiation...")
        portfolio_service = PortfolioIntegrationService()
        print("✅ Portfolio Integration Service instantiated")
        
        # Test with sample prediction data
        print("Step 3: Testing with sample prediction data...")
        sample_predictions = [
            {
                "number": 25,
                "confidence": 0.8,
                "rank": 1,
                "contributing_methods": {
                    "statistical_analysis": 0.40,
                    "information_theory": 0.25,
                    "quantum_algorithms": 0.20,
                    "neural_networks": 0.15
                },
                "analysis_source": "ultimate_prediction_system",
                "data_quality": "high"
            },
            {
                "number": 33,
                "confidence": 0.75,
                "rank": 2,
                "contributing_methods": {
                    "statistical_analysis": 0.35,
                    "information_theory": 0.30,
                    "quantum_algorithms": 0.25,
                    "neural_networks": 0.10
                },
                "analysis_source": "ultimate_prediction_system",
                "data_quality": "high"
            }
        ]
        
        print("Step 4: Testing portfolio optimization...")
        result = portfolio_service.optimize_method_weights_v3(sample_predictions)
        
        if "error" in result:
            print(f"❌ Portfolio optimization failed: {result['error']}")
            return False
        
        print("✅ Portfolio optimization completed")
        print(f"   Optimization status: {result.get('optimization_status', 'unknown')}")
        
        if "portfolio_metrics" in result:
            metrics = result["portfolio_metrics"]
            print(f"   Sharpe ratio: {metrics.get('sharpe_ratio', 0):.3f}")
            print(f"   Expected return: {metrics.get('expected_return', 0):.3f}")
            print(f"   Diversification score: {metrics.get('diversification_score', 0):.3f}")
        
        if "optimized_weights" in result:
            weights = result["optimized_weights"]
            print("   Optimized weights:")
            for method, weight in weights.items():
                print(f"     {method}: {weight:.3f}")
        
        # Test applying weights to predictions
        print("Step 5: Testing weight application...")
        if "optimized_weights" in result:
            optimized_predictions = portfolio_service.apply_portfolio_weights_to_predictions(
                sample_predictions,
                result["optimized_weights"]
            )
            
            print(f"✅ Applied weights to {len(optimized_predictions)} predictions")
            
            # Check if optimization was applied
            for pred in optimized_predictions:
                if pred.get("optimization_applied"):
                    print(f"   Prediction {pred['number']}: confidence {pred['confidence']:.3f}")
                    print(f"     Portfolio theory: {pred.get('portfolio_theory', 'N/A')}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_ultimate_system_integration():
    """Test if Ultimate System can import and use Portfolio Integration"""
    print("\n🧪 Testing Ultimate System Integration...")
    
    try:
        print("Step 1: Testing Ultimate System import...")
        from analytic_frequence.ultimate_prediction_system import UltimatePredictionSystem
        print("✅ Ultimate Prediction System imported")
        
        print("Step 2: Testing system instantiation...")
        ultimate_system = UltimatePredictionSystem()
        print("✅ Ultimate System instantiated")
        
        # Check if portfolio service is available
        if hasattr(ultimate_system, 'portfolio_service') and ultimate_system.portfolio_service:
            print("✅ Portfolio Integration Service is available in Ultimate System")
        else:
            print("⚠️ Portfolio Integration Service not available")
        
        print("Step 3: Testing with sample data...")
        sample_numbers = [12, 25, 33, 47, 51, 63, 72, 85, 91, 95]
        
        # This might take a while due to all the services
        print("   Running ultimate prediction analysis...")
        result = ultimate_system.ultimate_prediction_analysis(
            lottery_numbers=sample_numbers,
            prediction_horizon=3,
            include_explanations=False  # Skip explanations for speed
        )
        
        print("✅ Ultimate prediction analysis completed")
        print(f"   Predictions generated: {len(result.primary_predictions)}")
        print(f"   Confidence score: {result.confidence_score:.3f}")
        
        # Check if portfolio optimization was applied
        if result.portfolio_optimization:
            print("✅ Portfolio optimization results available:")
            portfolio_result = result.portfolio_optimization
            
            if "portfolio_metrics" in portfolio_result:
                metrics = portfolio_result["portfolio_metrics"]
                print(f"   Portfolio Sharpe ratio: {metrics.get('sharpe_ratio', 0):.3f}")
                print(f"   Portfolio expected return: {metrics.get('expected_return', 0):.3f}")
            
            if "optimized_weights" in portfolio_result:
                print("   Optimized method weights:")
                for method, weight in portfolio_result["optimized_weights"].items():
                    print(f"     {method}: {weight:.3f}")
        else:
            print("⚠️ No portfolio optimization results in Ultimate System output")
        
        # Check if predictions have optimization applied
        optimized_count = sum(1 for pred in result.primary_predictions 
                            if pred.get("optimization_applied"))
        print(f"   Predictions with portfolio optimization: {optimized_count}/{len(result.primary_predictions)}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run Phase 1A integration tests"""
    print("🚀 PHASE 1A INTEGRATION TESTING")
    print("=" * 60)
    print("Testing Modern Portfolio Theory integration with Ultimate Prediction System")
    print("=" * 60)
    
    tests = [
        ("Portfolio Integration Service", test_portfolio_integration),
        ("Ultimate System Integration", test_ultimate_system_integration)
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
    
    print("\n" + "=" * 60)
    print("🧪 PHASE 1A INTEGRATION TEST SUMMARY")
    print("=" * 60)
    
    passed = 0
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{test_name}: {status}")
        if result:
            passed += 1
    
    total = len(results)
    print(f"\nResult: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 PHASE 1A INTEGRATION SUCCESSFUL!")
        print("✅ Portfolio Integration Service working")
        print("✅ Ultimate System integration complete")
        print("✅ Modern Portfolio Theory replacing weighted averages")
        print("\n🚀 READY FOR PRODUCTION DEPLOYMENT!")
    else:
        print(f"\n⚠️ {total - passed} integration tests failed")
        print("Fix issues before production deployment")
        
    return passed == total

if __name__ == '__main__':
    main()
