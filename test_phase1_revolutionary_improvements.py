#!/usr/bin/env python3
"""
🧪 COMPREHENSIVE TESTING PHASE 1 - Revolutionary Improvements
Tests for Portfolio Optimization, ML Ensemble, and Regime Detection Services
"""

import unittest
import numpy as np
import sys
import os
from datetime import datetime, timedelta
from unittest.mock import Mock, patch, MagicMock

# Add project path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

# Import services to test
from predictions_tracker.services.portfolio_optimization_service import (
    PortfolioOptimizationService, 
    MethodPerformance, 
    OptimizationResult,
    MarketRegime
)
from predictions_tracker.services.ml_ensemble_service import (
    MLEnsembleService,
    ModelPrediction,
    EnsembleResult,
    MarketFeatures
)
from predictions_tracker.services.regime_detection_service import (
    RegimeDetectionService,
    RegimeMetrics,
    RegimeState,
    MarketPhase
)

class TestPortfolioOptimizationService(unittest.TestCase):
    """Test Portfolio Optimization Service"""
    
    def setUp(self):
        """Set up test environment"""
        self.service = PortfolioOptimizationService()
        
        # Sample method performances
        self.sample_performances = [
            MethodPerformance(
                method_name="frequency_analysis",
                expected_return=0.65,
                volatility=0.15,
                hit_rate=0.68,
                sharpe_ratio=2.1,
                max_drawdown=0.08,
                confidence_score=0.85
            ),
            MethodPerformance(
                method_name="pattern_analysis", 
                expected_return=0.58,
                volatility=0.22,
                hit_rate=0.62,
                sharpe_ratio=1.4,
                max_drawdown=0.12,
                confidence_score=0.72
            ),
            MethodPerformance(
                method_name="correlation_analysis",
                expected_return=0.52,
                volatility=0.18,
                hit_rate=0.55,
                sharpe_ratio=1.2,
                max_drawdown=0.10,
                confidence_score=0.68
            )
        ]
        
    def test_correlation_matrix_calculation(self):
        """Test correlation matrix calculation"""
        result = self.service.calculate_correlation_matrix_v3(self.sample_performances)
        
        # Check structure
        self.assertIsInstance(result, dict)
        self.assertIn('correlation_matrix', result)
        self.assertIn('diversification_score', result)
        
        # Check matrix properties
        matrix = result['correlation_matrix']
        self.assertEqual(len(matrix), 3)  # 3x3 matrix
        
        # Check diagonal elements are 1.0
        methods = list(matrix.keys())
        for method in methods:
            self.assertAlmostEqual(matrix[method][method], 1.0, places=2)
        
        # Check symmetry
        for i, method1 in enumerate(methods):
            for j, method2 in enumerate(methods):
                if i != j:
                    self.assertAlmostEqual(
                        matrix[method1][method2], 
                        matrix[method2][method1], 
                        places=2
                    )
        
        print(f"✅ Correlation matrix test passed: {len(matrix)}x{len(matrix)} matrix")
    
    def test_markowitz_optimization(self):
        """Test Markowitz portfolio optimization"""
        correlation_data = self.service.calculate_correlation_matrix_v3(self.sample_performances)
        
        result = self.service.markowitz_optimization_v3(
            self.sample_performances, 
            correlation_data['correlation_matrix']
        )
        
        # Check structure
        self.assertIsInstance(result, OptimizationResult)
        self.assertIsInstance(result.optimal_weights, dict)
        self.assertIsInstance(result.expected_return, float)
        self.assertIsInstance(result.portfolio_volatility, float)
        
        # Check weights sum to 1
        total_weight = sum(result.optimal_weights.values())
        self.assertAlmostEqual(total_weight, 1.0, places=2)
        
        # Check all weights are non-negative
        for weight in result.optimal_weights.values():
            self.assertGreaterEqual(weight, 0.0)
        
        # Check Sharpe ratio is positive
        self.assertGreater(result.sharpe_ratio, 0.0)
        
        print(f"✅ Markowitz optimization test passed: Sharpe={result.sharpe_ratio:.3f}")
    
    def test_kelly_criterion(self):
        """Test Kelly Criterion calculation"""
        method_performance = self.sample_performances[0]
        
        result = self.service.calculate_kelly_criterion_v3(method_performance)
        
        # Check structure
        self.assertIsInstance(result, dict)
        self.assertIn('kelly_fraction', result)
        self.assertIn('recommended_weight', result)
        self.assertIn('risk_assessment', result)
        
        # Check values are reasonable
        kelly_fraction = result['kelly_fraction']
        self.assertGreaterEqual(kelly_fraction, 0.0)
        self.assertLessEqual(kelly_fraction, 1.0)
        
        recommended_weight = result['recommended_weight']
        self.assertGreaterEqual(recommended_weight, 0.0)
        self.assertLessEqual(recommended_weight, 1.0)
        
        print(f"✅ Kelly criterion test passed: fraction={kelly_fraction:.3f}")
    
    def test_regime_aware_optimization(self):
        """Test regime-aware portfolio optimization"""
        correlation_data = self.service.calculate_correlation_matrix_v3(self.sample_performances)
        regime = MarketRegime.VOLATILE
        
        result = self.service.regime_aware_optimization_v3(
            self.sample_performances,
            correlation_data['correlation_matrix'],
            regime
        )
        
        # Check structure
        self.assertIsInstance(result, OptimizationResult)
        self.assertIn('regime_adjustments', result.additional_metrics)
        
        # Check regime-specific adjustments
        adjustments = result.additional_metrics['regime_adjustments']
        self.assertIn('risk_penalty', adjustments)
        self.assertIn('concentration_limit', adjustments)
        
        print(f"✅ Regime-aware optimization test passed for {regime.value}")

class TestMLEnsembleService(unittest.TestCase):
    """Test ML Ensemble Service"""
    
    def setUp(self):
        """Set up test environment"""
        self.service = MLEnsembleService()
        
        # Sample analysis data
        self.sample_short_analysis = {
            'score': 75.0,
            'confidence': 0.8,
            'expected_hit_rate': 0.65,
            'momentum': 0.3,
            'consistency': 0.7
        }
        
        self.sample_long_analysis = {
            'score': 68.0,
            'confidence': 0.75,
            'expected_hit_rate': 0.62,
            'stability': 0.8,
            'trend': 0.2
        }
        
        self.sample_market_features = MarketFeatures(
            regime='volatile',
            volatility=0.6,
            trend_strength=0.4,
            correlation_level=0.3,
            data_quality=0.85,
            temporal_consistency=0.7
        )
    
    def test_model_initialization(self):
        """Test ML model initialization"""
        models = self.service.initialize_models('volatile')
        
        # Check models are created
        self.assertIsInstance(models, dict)
        self.assertGreater(len(models), 0)
        
        # Check expected models exist
        expected_models = ['random_forest', 'gradient_boost', 'ridge_regression']
        for model_name in expected_models:
            if model_name in models:
                self.assertIsNotNone(models[model_name])
        
        print(f"✅ Model initialization test passed: {len(models)} models created")
    
    def test_feature_extraction(self):
        """Test comprehensive feature extraction"""
        features = self.service.extract_comprehensive_features(
            self.sample_short_analysis,
            self.sample_long_analysis,
            self.sample_market_features
        )
        
        # Check structure
        self.assertIsInstance(features, np.ndarray)
        self.assertEqual(len(features.shape), 2)  # Should be 2D array
        self.assertEqual(features.shape[0], 1)     # Single sample
        self.assertGreater(features.shape[1], 10)  # At least 10 features
        
        # Check feature names are set
        self.assertGreater(len(self.service.feature_names), 0)
        
        print(f"✅ Feature extraction test passed: {features.shape[1]} features extracted")
    
    def test_ml_ensemble_scoring(self):
        """Test ML ensemble scoring"""
        validation_results = {'validation_score': 0.8}
        
        result = self.service.ml_ensemble_scoring_v3(
            self.sample_short_analysis,
            self.sample_long_analysis,
            validation_results,
            self.sample_market_features
        )
        
        # Check structure
        self.assertIsInstance(result, EnsembleResult)
        self.assertIsInstance(result.final_score, float)
        self.assertIsInstance(result.model_predictions, list)
        self.assertIsInstance(result.ensemble_confidence, float)
        
        # Check values are reasonable
        self.assertGreaterEqual(result.final_score, 0.0)
        self.assertLessEqual(result.final_score, 100.0)
        self.assertGreaterEqual(result.ensemble_confidence, 0.0)
        self.assertLessEqual(result.ensemble_confidence, 1.0)
        
        # Check model predictions
        if result.model_predictions:
            for pred in result.model_predictions:
                self.assertIsInstance(pred, ModelPrediction)
                self.assertIsInstance(pred.model_name, str)
                self.assertIsInstance(pred.prediction, float)
                self.assertIsInstance(pred.confidence, float)
        
        print(f"✅ ML ensemble scoring test passed: score={result.final_score:.3f}")

class TestRegimeDetectionService(unittest.TestCase):
    """Test Regime Detection Service"""
    
    def setUp(self):
        """Set up test environment"""
        self.service = RegimeDetectionService()
        
        # Sample historical data
        self.sample_historical_data = []
        for i in range(30):
            date_obj = datetime.now() - timedelta(days=30-i)
            data = {
                'date': date_obj.strftime('%Y-%m-%d'),
                'analysis_results': {
                    'composite_score': 50 + np.random.normal(0, 10),
                    'hit_rate': 0.5 + np.random.normal(0, 0.1),
                },
                'predictions': [1, 2, 3, 4, 5],
                'actual_results': [1, 2, 3, 6, 7] if i % 3 == 0 else [1, 2, 8, 9, 10]
            }
            self.sample_historical_data.append(data)
        
        self.sample_predictions = [
            {'accuracy': 0.6, 'confidence': 0.8},
            {'accuracy': 0.7, 'confidence': 0.75},
            {'accuracy': 0.65, 'confidence': 0.82}
        ]
    
    def test_regime_metrics_calculation(self):
        """Test regime metrics calculation"""
        metrics = self.service.calculate_regime_metrics(
            self.sample_historical_data,
            self.sample_predictions
        )
        
        # Check structure
        self.assertIsInstance(metrics, RegimeMetrics)
        
        # Check all metrics are in valid ranges
        self.assertGreaterEqual(metrics.volatility, 0.0)
        self.assertLessEqual(metrics.volatility, 1.0)
        
        self.assertGreaterEqual(metrics.trend_strength, 0.0)
        self.assertLessEqual(metrics.trend_strength, 1.0)
        
        self.assertGreaterEqual(metrics.correlation_level, 0.0)
        self.assertLessEqual(metrics.correlation_level, 1.0)
        
        self.assertGreaterEqual(metrics.momentum, -1.0)
        self.assertLessEqual(metrics.momentum, 1.0)
        
        self.assertGreaterEqual(metrics.stability, 0.0)
        self.assertLessEqual(metrics.stability, 1.0)
        
        self.assertGreaterEqual(metrics.data_quality, 0.0)
        self.assertLessEqual(metrics.data_quality, 1.0)
        
        print(f"✅ Regime metrics test passed: volatility={metrics.volatility:.3f}")
    
    def test_regime_classification(self):
        """Test regime classification"""
        sample_metrics = RegimeMetrics(
            volatility=0.3,
            trend_strength=0.7,
            correlation_level=0.6,
            momentum=0.4,
            stability=0.6,
            data_quality=0.8
        )
        
        regime_type, confidence = self.service.classify_regime(sample_metrics)
        
        # Check structure
        self.assertIsInstance(regime_type, str)
        self.assertIn(regime_type, ['bull', 'bear', 'volatile', 'sideways'])
        
        self.assertIsInstance(confidence, float)
        self.assertGreaterEqual(confidence, 0.0)
        self.assertLessEqual(confidence, 1.0)
        
        print(f"✅ Regime classification test passed: {regime_type} ({confidence:.3f})")
    
    def test_regime_forecasting(self):
        """Test regime forecasting"""
        current_regime = 'bull'
        forecast = self.service.forecast_regime(current_regime, horizon=3)
        
        # Check structure
        self.assertIsInstance(forecast, dict)
        self.assertEqual(len(forecast), 4)  # 4 possible regimes
        
        # Check probabilities sum to approximately 1
        total_prob = sum(forecast.values())
        self.assertAlmostEqual(total_prob, 1.0, places=1)
        
        # Check all probabilities are valid
        for regime, prob in forecast.items():
            self.assertGreaterEqual(prob, 0.0)
            self.assertLessEqual(prob, 1.0)
        
        print(f"✅ Regime forecasting test passed: {forecast}")
    
    def test_adaptive_weights_calculation(self):
        """Test adaptive weights calculation"""
        sample_metrics = RegimeMetrics(0.4, 0.6, 0.5, 0.2, 0.7, 0.8)
        sample_regime = RegimeState(
            regime_type='bull',
            confidence=0.8,
            duration=5,
            transition_probability={'bull': 0.7, 'bear': 0.1, 'volatile': 0.15, 'sideways': 0.05},
            regime_metrics=sample_metrics,
            timestamp=datetime.now()
        )
        
        weights = self.service.calculate_adaptive_weights(sample_regime)
        
        # Check structure
        self.assertIsInstance(weights, dict)
        expected_keys = ['short_term_weight', 'long_term_weight', 'pattern_weight', 
                        'frequency_weight', 'correlation_weight', 'ml_weight']
        
        for key in expected_keys:
            self.assertIn(key, weights)
            self.assertIsInstance(weights[key], float)
            self.assertGreaterEqual(weights[key], 0.0)
            self.assertLessEqual(weights[key], 1.0)
        
        print(f"✅ Adaptive weights test passed: {len(weights)} weights calculated")
    
    def test_full_regime_detection(self):
        """Test complete regime detection process"""
        market_phase = self.service.detect_regime_v3(
            self.sample_historical_data,
            self.sample_predictions
        )
        
        # Check structure
        self.assertIsInstance(market_phase, MarketPhase)
        self.assertIsInstance(market_phase.current_regime, RegimeState)
        self.assertIsInstance(market_phase.regime_history, list)
        self.assertIsInstance(market_phase.transition_matrix, dict)
        self.assertIsInstance(market_phase.regime_forecast, dict)
        self.assertIsInstance(market_phase.adaptive_weights, dict)
        
        # Check current regime
        current = market_phase.current_regime
        self.assertIn(current.regime_type, ['bull', 'bear', 'volatile', 'sideways'])
        self.assertGreaterEqual(current.confidence, 0.0)
        self.assertLessEqual(current.confidence, 1.0)
        self.assertGreaterEqual(current.duration, 1)
        
        print(f"✅ Full regime detection test passed: {current.regime_type}")

class TestServiceIntegration(unittest.TestCase):
    """Test integration between services"""
    
    def setUp(self):
        """Set up test environment"""
        self.portfolio_service = PortfolioOptimizationService()
        self.ml_service = MLEnsembleService()
        self.regime_service = RegimeDetectionService()
    
    def test_data_structure_compatibility(self):
        """Test data structure compatibility between services"""
        
        # Test that regime detection output can be used by other services
        sample_historical_data = [
            {
                'date': '2025-01-01',
                'analysis_results': {'composite_score': 65, 'hit_rate': 0.6},
                'predictions': [1, 2, 3],
                'actual_results': [1, 2, 4]
            }
        ]
        
        sample_predictions = [{'accuracy': 0.7, 'confidence': 0.8}]
        
        # Get regime detection result
        market_phase = self.regime_service.detect_regime_v3(
            sample_historical_data, 
            sample_predictions
        )
        
        # Check that regime data can be used for ML ensemble
        market_features = MarketFeatures(
            regime=market_phase.current_regime.regime_type,
            volatility=market_phase.current_regime.regime_metrics.volatility,
            trend_strength=market_phase.current_regime.regime_metrics.trend_strength,
            correlation_level=market_phase.current_regime.regime_metrics.correlation_level,
            data_quality=market_phase.current_regime.regime_metrics.data_quality,
            temporal_consistency=0.7
        )
        
        # Test ML ensemble can use this data
        short_analysis = {'score': 70, 'confidence': 0.8, 'expected_hit_rate': 0.65, 'momentum': 0.3, 'consistency': 0.7}
        long_analysis = {'score': 65, 'confidence': 0.75, 'expected_hit_rate': 0.62, 'stability': 0.8, 'trend': 0.2}
        validation_results = {'validation_score': 0.8}
        
        ensemble_result = self.ml_service.ml_ensemble_scoring_v3(
            short_analysis,
            long_analysis,
            validation_results,
            market_features
        )
        
        # Check compatibility
        self.assertIsNotNone(ensemble_result)
        self.assertIsInstance(ensemble_result.final_score, float)
        
        print("✅ Service integration test passed: Data structures are compatible")
    
    def test_performance_data_flow(self):
        """Test that performance data flows correctly between services"""
        
        # Create sample method performances
        performances = [
            MethodPerformance(
                method_name="test_method_1",
                expected_return=0.6,
                volatility=0.2,
                hit_rate=0.65,
                sharpe_ratio=1.5,
                max_drawdown=0.1,
                confidence_score=0.8
            ),
            MethodPerformance(
                method_name="test_method_2",
                expected_return=0.55,
                volatility=0.25,
                hit_rate=0.6,
                sharpe_ratio=1.2,
                max_drawdown=0.15,
                confidence_score=0.75
            )
        ]
        
        # Test portfolio optimization
        correlation_data = self.portfolio_service.calculate_correlation_matrix_v3(performances)
        optimization_result = self.portfolio_service.markowitz_optimization_v3(
            performances,
            correlation_data['correlation_matrix']
        )
        
        # Check that optimization results have correct structure
        self.assertIsInstance(optimization_result.optimal_weights, dict)
        self.assertEqual(len(optimization_result.optimal_weights), 2)
        
        for method_name in ['test_method_1', 'test_method_2']:
            self.assertIn(method_name, optimization_result.optimal_weights)
            weight = optimization_result.optimal_weights[method_name]
            self.assertGreaterEqual(weight, 0.0)
            self.assertLessEqual(weight, 1.0)
        
        print("✅ Performance data flow test passed")

def run_comprehensive_tests():
    """Run all comprehensive tests"""
    print("🧪 STARTING COMPREHENSIVE PHASE 1 TESTING")
    print("=" * 60)
    
    # Create test suite
    test_suite = unittest.TestSuite()
    
    # Add all test classes
    test_classes = [
        TestPortfolioOptimizationService,
        TestMLEnsembleService, 
        TestRegimeDetectionService,
        TestServiceIntegration
    ]
    
    for test_class in test_classes:
        tests = unittest.TestLoader().loadTestsFromTestCase(test_class)
        test_suite.addTests(tests)
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2, stream=sys.stdout)
    result = runner.run(test_suite)
    
    print("\n" + "=" * 60)
    print("🧪 PHASE 1 TESTING SUMMARY")
    print(f"Tests run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    
    if result.failures:
        print("\n❌ FAILURES:")
        for test, traceback in result.failures:
            print(f"- {test}: {traceback}")
    
    if result.errors:
        print("\n❌ ERRORS:")
        for test, traceback in result.errors:
            print(f"- {test}: {traceback}")
    
    if result.wasSuccessful():
        print("\n✅ ALL PHASE 1 TESTS PASSED!")
        print("Ready for Phase 2 implementation")
    else:
        print("\n❌ SOME TESTS FAILED!")
        print("Fix issues before proceeding to Phase 2")
    
    return result.wasSuccessful()

if __name__ == '__main__':
    run_comprehensive_tests()
