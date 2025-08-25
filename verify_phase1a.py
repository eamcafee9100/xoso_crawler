#!/usr/bin/env python3
"""
🎯 PHASE 1A DEPLOYMENT VERIFICATION - Quick Status Check
"""

def verify_deployment():
    """Quick verification that Phase 1A is ready"""
    print("🔍 PHASE 1A DEPLOYMENT VERIFICATION")
    print("=" * 50)
    
    checks = []
    
    # Check 1: Core files exist
    import os
    files_to_check = [
        'analytic_frequence/portfolio_integration_service.py',
        'predictions_tracker/services/portfolio_optimization_service_lite.py',
        'PHASE1A_DEPLOYMENT_REPORT.md'
    ]
    
    for file_path in files_to_check:
        if os.path.exists(file_path):
            print(f"✅ {file_path}")
            checks.append(True)
        else:
            print(f"❌ {file_path} - MISSING")
            checks.append(False)
    
    # Check 2: Basic imports work
    try:
        print("\n📦 Testing Basic Imports...")
        
        import sys
        sys.path.insert(0, '.')
        sys.path.insert(0, 'predictions_tracker')
        
        from predictions_tracker.services.portfolio_optimization_service_lite import PortfolioOptimizationService
        print("✅ Lite Portfolio Service import")
        checks.append(True)
        
        # Test instantiation
        service = PortfolioOptimizationService()
        print("✅ Service instantiation")
        checks.append(True)
        
    except Exception as e:
        print(f"❌ Import test failed: {e}")
        checks.append(False)
    
    # Check 3: Basic functionality
    try:
        print("\n⚙️ Testing Basic Functionality...")
        
        from predictions_tracker.services.portfolio_optimization_service_lite import MethodPerformance
        
        # Create test performance
        perf = MethodPerformance(
            method_name="test_method",
            expected_return=0.6,
            volatility=0.2,
            hit_rate=0.65,
            sharpe_ratio=1.5,
            max_drawdown=0.1,
            confidence_score=0.8
        )
        print("✅ MethodPerformance creation")
        checks.append(True)
        
        # Test portfolio optimization
        service = PortfolioOptimizationService()
        correlation_result = service.calculate_correlation_matrix_v3([perf])
        print("✅ Correlation calculation")
        checks.append(True)
        
        optimization_result = service.markowitz_optimization_v3([perf], correlation_result['correlation_matrix'])
        print(f"✅ Portfolio optimization (Sharpe: {optimization_result.sharpe_ratio:.3f})")
        checks.append(True)
        
    except Exception as e:
        print(f"❌ Functionality test failed: {e}")
        checks.append(False)
    
    # Summary
    passed = sum(checks)
    total = len(checks)
    
    print(f"\n📊 VERIFICATION RESULTS: {passed}/{total} checks passed")
    
    if passed == total:
        print("\n🎉 PHASE 1A DEPLOYMENT VERIFIED!")
        print("✅ All core components operational")
        print("✅ Modern Portfolio Theory ready")
        print("✅ Ready for production integration")
        return True
    else:
        print(f"\n⚠️ {total - passed} checks failed")
        print("Fix issues before production use")
        return False

if __name__ == '__main__':
    verify_deployment()
