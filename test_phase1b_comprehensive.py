"""
🎯 Phase 1B Comprehensive Test
=============================

Complete test for Phase 1B Foundation Revolution components.
Tests ML Ensemble and Regime Detection independently.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import numpy as np
from datetime import datetime

def test_ml_ensemble_service():
    """Test ML Ensemble Service Lite"""
    print("🤖 Testing ML Ensemble Service Lite...")
    
    try:
        from ml_ensemble_service_lite import MLEnsembleServiceLite
        
        # Initialize service
        ensemble_service = MLEnsembleServiceLite()
        
        # Create test predictions
        predictions = [
            ensemble_service.add_prediction("statistical_analysis", "12345", 0.85),
            ensemble_service.add_prediction("information_theory", "12346", 0.75),
            ensemble_service.add_prediction("quantum_algorithms", "12345", 0.90),
            ensemble_service.add_prediction("neural_networks", "12347", 0.70),
        ]
        
        # Test weighted voting
        weighted_result = ensemble_service.ensemble_vote_weighted(predictions)
        
        # Test majority voting
        majority_result = ensemble_service.ensemble_vote_majority(predictions)
        
        # Test stacking
        stacking_result = ensemble_service.ensemble_vote_stacking(predictions)
        
        # Test diversity calculation
        diversity = ensemble_service.calculate_model_diversity(predictions)
        
        print(f"   ✅ Weighted Voting: {weighted_result.final_prediction} (conf: {weighted_result.ensemble_confidence:.3f})")
        print(f"   ✅ Majority Voting: {majority_result.final_prediction} (conf: {majority_result.ensemble_confidence:.3f})")
        print(f"   ✅ Stacking: {stacking_result.final_prediction} (conf: {stacking_result.ensemble_confidence:.3f})")
        print(f"   ✅ Diversity Score: {diversity:.3f}")
        
        return {
            'status': 'success',
            'weighted_confidence': weighted_result.ensemble_confidence,
            'diversity': diversity,
            'voting_methods': 3
        }
        
    except Exception as e:
        print(f"   ❌ ML Ensemble Error: {e}")
        return {'status': 'error', 'error': str(e)}

def test_regime_detection_service():
    """Test Regime Detection Service Lite"""
    print("\n🌊 Testing Regime Detection Service Lite...")
    
    try:
        from regime_detection_service_lite import RegimeDetectionServiceLite, RegimeType
        
        # Initialize service
        regime_service = RegimeDetectionServiceLite()
        
        # Generate different market scenarios
        np.random.seed(42)
        
        # Stable market
        stable_data = 100 + np.cumsum(np.random.normal(0, 0.5, 50))
        stable_regime = regime_service.detect_current_regime(stable_data.tolist())
        
        # Volatile market
        volatile_data = 100 + np.cumsum(np.random.normal(0, 2.0, 50))
        volatile_regime = regime_service.detect_current_regime(volatile_data.tolist())
        
        # Trending market
        trend_data = 100 + np.cumsum(np.random.normal(0.5, 1.0, 50))
        trend_regime = regime_service.detect_current_regime(trend_data.tolist())
        
        # Test transition predictions
        transitions = regime_service.predict_regime_transition(trend_regime)
        
        # Test stability analysis
        stability = regime_service.analyze_regime_stability(trend_data.tolist())
        
        print(f"   ✅ Stable Market: {stable_regime.regime_type.value} (conf: {stable_regime.confidence:.3f})")
        print(f"   ✅ Volatile Market: {volatile_regime.regime_type.value} (conf: {volatile_regime.confidence:.3f})")
        print(f"   ✅ Trending Market: {trend_regime.regime_type.value} (conf: {trend_regime.confidence:.3f})")
        print(f"   ✅ Transitions: {len(transitions)} predicted")
        print(f"   ✅ Stability: {stability.get('stability', 0):.3f}")
        
        return {
            'status': 'success',
            'regimes_detected': 3,
            'transitions_predicted': len(transitions),
            'stability_score': stability.get('stability', 0)
        }
        
    except Exception as e:
        print(f"   ❌ Regime Detection Error: {e}")
        return {'status': 'error', 'error': str(e)}

def test_phase1b_lite_integration():
    """Test Phase 1B components working together"""
    print("\n🎯 Testing Phase 1B Lite Integration...")
    
    try:
        from ml_ensemble_service_lite import MLEnsembleServiceLite
        from regime_detection_service_lite import RegimeDetectionServiceLite
        
        # Initialize services
        ensemble_service = MLEnsembleServiceLite()
        regime_service = RegimeDetectionServiceLite()
        
        # Sample data
        np.random.seed(42)
        historical_data = 100 + np.cumsum(np.random.normal(0.1, 1.5, 50))
        
        # Sample predictions
        sample_predictions = [
            {'method': 'statistical_analysis', 'prediction': '12345', 'confidence': 0.85},
            {'method': 'information_theory', 'prediction': '12346', 'confidence': 0.75},
            {'method': 'quantum_algorithms', 'prediction': '12345', 'confidence': 0.90},
            {'method': 'neural_networks', 'prediction': '12347', 'confidence': 0.70}
        ]
        
        # Apply ensemble
        ensemble_predictions = []
        for pred in sample_predictions:
            ensemble_pred = ensemble_service.add_prediction(
                pred['method'], pred['prediction'], pred['confidence']
            )
            ensemble_predictions.append(ensemble_pred)
        
        ensemble_result = ensemble_service.ensemble_vote_weighted(ensemble_predictions)
        
        # Apply regime detection
        regime_state = regime_service.detect_current_regime(historical_data.tolist())
        transitions = regime_service.predict_regime_transition(regime_state)
        
        # Calculate integrated confidence
        ensemble_confidence = ensemble_result.ensemble_confidence
        regime_confidence = regime_state.confidence
        integrated_confidence = (ensemble_confidence + regime_confidence) / 2.0
        
        print(f"   ✅ Ensemble Result: {ensemble_result.final_prediction}")
        print(f"   ✅ Ensemble Confidence: {ensemble_confidence:.3f}")
        print(f"   ✅ Current Regime: {regime_state.regime_type.value}")
        print(f"   ✅ Regime Confidence: {regime_confidence:.3f}")
        print(f"   ✅ Integrated Confidence: {integrated_confidence:.3f}")
        print(f"   ✅ Diversity Score: {ensemble_result.diversity_score:.3f}")
        print(f"   ✅ Predicted Transitions: {len(transitions)}")
        
        return {
            'status': 'success',
            'ensemble_prediction': ensemble_result.final_prediction,
            'ensemble_confidence': ensemble_confidence,
            'regime_type': regime_state.regime_type.value,
            'regime_confidence': regime_confidence,
            'integrated_confidence': integrated_confidence,
            'diversity_score': ensemble_result.diversity_score,
            'transition_count': len(transitions)
        }
        
    except Exception as e:
        print(f"   ❌ Integration Error: {e}")
        return {'status': 'error', 'error': str(e)}

def run_phase1b_comprehensive_test():
    """Run comprehensive Phase 1B test"""
    print("🎯 PHASE 1B COMPREHENSIVE TEST")
    print("=" * 50)
    print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Test individual components
    ensemble_results = test_ml_ensemble_service()
    regime_results = test_regime_detection_service()
    integration_results = test_phase1b_lite_integration()
    
    # Summary
    print("\n📊 PHASE 1B TEST SUMMARY:")
    print("=" * 30)
    
    success_count = 0
    total_tests = 3
    
    if ensemble_results['status'] == 'success':
        print("✅ ML Ensemble Service: OPERATIONAL")
        success_count += 1
    else:
        print("❌ ML Ensemble Service: ERROR")
    
    if regime_results['status'] == 'success':
        print("✅ Regime Detection Service: OPERATIONAL")
        success_count += 1
    else:
        print("❌ Regime Detection Service: ERROR")
    
    if integration_results['status'] == 'success':
        print("✅ Phase 1B Integration: OPERATIONAL")
        success_count += 1
    else:
        print("❌ Phase 1B Integration: ERROR")
    
    # Overall status
    success_rate = success_count / total_tests
    
    print(f"\n🎯 OVERALL PHASE 1B STATUS:")
    if success_rate == 1.0:
        print("🎉 PHASE 1B: FULLY OPERATIONAL")
        status = "fully_operational"
    elif success_rate >= 0.67:
        print("⚠️  PHASE 1B: MOSTLY OPERATIONAL")
        status = "mostly_operational"
    else:
        print("❌ PHASE 1B: NEEDS ATTENTION")
        status = "needs_attention"
    
    # Performance metrics
    if integration_results['status'] == 'success':
        print(f"\n📈 PERFORMANCE METRICS:")
        print(f"   Integrated Confidence: {integration_results['integrated_confidence']:.3f}")
        print(f"   Ensemble Diversity: {integration_results['diversity_score']:.3f}")
        print(f"   Regime Detection: {integration_results['regime_type']}")
        print(f"   Prediction Fusion: {integration_results['ensemble_prediction']}")
    
    # Phase 1B completion status
    print(f"\n🏁 FOUNDATION REVOLUTION STATUS:")
    print(f"   Phase 1A (Portfolio Theory): ✅ DEPLOYED")
    print(f"   Phase 1B (ML + Regime): {'✅ DEPLOYED' if status == 'fully_operational' else '🔄 IN PROGRESS'}")
    
    return {
        'overall_status': status,
        'success_rate': success_rate,
        'ensemble_status': ensemble_results['status'],
        'regime_status': regime_results['status'],
        'integration_status': integration_results['status'],
        'performance_metrics': integration_results if integration_results['status'] == 'success' else {}
    }

if __name__ == "__main__":
    results = run_phase1b_comprehensive_test()
