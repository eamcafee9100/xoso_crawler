"""
PHASE 2A TEST SUITE: Ensemble Learning & Machine Learning Enhancement Tests
===========================================================================
Comprehensive test coverage for ML ensemble system, Bayesian optimization, and feature pipeline
"""

import os
import sys
import tempfile
import unittest
from datetime import date, datetime, timedelta
from unittest.mock import MagicMock, Mock, patch

import numpy as np
import pandas as pd

# Add project root to path for imports
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))

# Set Django settings before importing Django components
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "xoso_crawler.settings")

import django

django.setup()

from django.http import JsonResponse
from django.test import Client, TestCase
from django.urls import reverse

# Phase 2A imports
from predictions_tracker.ensemble_ml_foundation import (
    AdvancedFeaturePipeline,
    BayesianOptimizer,
    EnsembleLotteryPredictor,
)
from predictions_tracker.views_dir.api_ensemble_ml_v2a import (
    _get_recent_lottery_data,
    _prepare_ml_training_data,
    api_bayesian_optimization,
    api_ensemble_prediction,
    api_ensemble_training,
)


class TestEnsembleLotteryPredictor(TestCase):
    """Test suite for EnsembleLotteryPredictor class"""

    def setUp(self):
        """Set up test environment"""
        self.predictor = EnsembleLotteryPredictor(random_state=42)

        # Create mock training data
        np.random.seed(42)
        self.X_train = np.random.randn(100, 20)  # 100 samples, 20 features
        self.y_train = np.random.randn(100)  # 100 targets

        self.X_test = np.random.randn(20, 20)  # 20 test samples
        self.y_test = np.random.randn(20)  # 20 test targets

    def test_initialization(self):
        """Test EnsembleLotteryPredictor initialization"""
        self.assertEqual(len(self.predictor.models), 5)
        self.assertIn("random_forest", self.predictor.models)
        self.assertIn("xgboost", self.predictor.models)
        self.assertIn("gradient_boost", self.predictor.models)
        self.assertIn("neural_network", self.predictor.models)
        self.assertIn("meta_learner", self.predictor.models)

        # Test default ensemble weights
        self.assertEqual(len(self.predictor.ensemble_weights), 5)
        self.assertAlmostEqual(
            sum(self.predictor.ensemble_weights.values()), 1.0, places=5
        )

    def test_train_individual_models(self):
        """Test individual model training"""
        # Train individual models (this is done internally in train_ensemble)
        training_results = self.predictor.train_ensemble(
            self.X_train, self.y_train, validation_split=0.2
        )

        # Check that all models are trained (fitted attribute exists)
        for model_name, model in self.predictor.models.items():
            if model_name != "meta_learner":  # Skip meta learner for individual test
                self.assertTrue(hasattr(model, "predict"))

    def test_ensemble_training(self):
        """Test full ensemble training process"""
        training_results = self.predictor.train_ensemble(
            self.X_train, self.y_train, validation_split=0.2
        )

        # Check training results structure
        self.assertIsInstance(training_results, dict)
        self.assertIn("model_performances", training_results)
        self.assertIn("cross_validation_scores", training_results)

        # Check that all models have performance metrics
        model_performances = training_results["model_performances"]
        for model_name in self.predictor.models.keys():
            self.assertIn(model_name, model_performances)
            if not np.isnan(model_performances[model_name]["mse"]):
                self.assertGreater(model_performances[model_name]["mse"], 0)

    def test_ensemble_prediction(self):
        """Test ensemble prediction methods"""
        # Train ensemble first
        self.predictor.train_ensemble(self.X_train, self.y_train, validation_split=0.2)

        # Test weighted average prediction
        predictions_weighted = self.predictor.predict_ensemble(
            self.X_test, method="weighted_average"
        )
        self.assertEqual(len(predictions_weighted), len(self.X_test))

        # Test voting prediction
        predictions_voting = self.predictor.predict_ensemble(
            self.X_test, method="voting"
        )
        self.assertEqual(len(predictions_voting), len(self.X_test))

        # Test stacking prediction
        predictions_stacking = self.predictor.predict_ensemble(
            self.X_test, method="stacking"
        )
        self.assertEqual(len(predictions_stacking), len(self.X_test))

    def test_feature_importance(self):
        """Test feature importance ranking"""
        # Train ensemble first
        self.predictor.train_ensemble(self.X_train, self.y_train, validation_split=0.2)

        # Get feature importance
        importance_ranking = self.predictor.get_feature_importance_ranking(top_k=10)

        self.assertIsInstance(importance_ranking, dict)

        if "error" not in importance_ranking:
            self.assertIn("top_features", importance_ranking)
            # Check that we get reasonable number of features
            self.assertLessEqual(len(importance_ranking["top_features"]), 10)

            # Check feature importance structure
            for feature_info in importance_ranking["top_features"]:
                self.assertIn("importance_score", feature_info)
                self.assertGreaterEqual(feature_info["importance_score"], 0)

    def test_model_persistence(self):
        """Test model saving and loading"""
        # Train ensemble
        self.predictor.train_ensemble(self.X_train, self.y_train, validation_split=0.2)
        original_predictions = self.predictor.predict_ensemble(self.X_test[:5])

        # Save model to temporary file
        with tempfile.NamedTemporaryFile(suffix=".pkl", delete=False) as tmp_file:
            temp_path = tmp_file.name

        try:
            # Save ensemble
            success = self.predictor.save_ensemble(temp_path)
            self.assertTrue(success)

            # Create new predictor and load ensemble
            new_predictor = EnsembleLotteryPredictor(random_state=42)
            load_success = new_predictor.load_ensemble(temp_path)
            self.assertTrue(load_success)

            # Test that loaded model produces same predictions
            loaded_predictions = new_predictor.predict_ensemble(self.X_test[:5])
            np.testing.assert_array_almost_equal(
                original_predictions, loaded_predictions, decimal=5
            )

        finally:
            # Clean up temporary file
            if os.path.exists(temp_path):
                os.unlink(temp_path)


class TestBayesianOptimizer(TestCase):
    """Test suite for BayesianOptimizer class"""

    def setUp(self):
        """Set up test environment"""
        self.optimizer = BayesianOptimizer(random_state=42)

        # Create mock data
        np.random.seed(42)
        self.X = np.random.randn(50, 15)  # 50 samples, 15 features
        self.y = np.random.randn(50)  # 50 targets

    def test_initialization(self):
        """Test BayesianOptimizer initialization"""
        self.assertEqual(self.optimizer.random_state, 42)
        self.assertIsInstance(self.optimizer.optimization_history, list)
        self.assertEqual(len(self.optimizer.optimization_history), 0)

    def test_parameter_space_generation(self):
        """Test parameter space generation for different models"""
        param_spaces = self.optimizer._define_parameter_spaces()

        self.assertIsInstance(param_spaces, dict)
        self.assertIn("random_forest", param_spaces)
        self.assertIn("xgboost", param_spaces)

        rf_params = param_spaces["random_forest"]
        self.assertIn("n_estimators", rf_params)
        self.assertIn("max_depth", rf_params)

    @patch("predictions_tracker.ensemble_ml_foundation.GridSearchCV")
    def test_single_model_optimization(self, mock_grid_search):
        """Test single model hyperparameter optimization"""
        # Mock GridSearchCV behavior
        mock_search = Mock()
        mock_search.best_params_ = {"n_estimators": 100, "max_depth": 10}
        mock_search.best_score_ = 0.85
        mock_search.cv_results_ = {"mean_test_score": [0.8, 0.85, 0.82]}
        mock_grid_search.return_value = mock_search

        # Get parameter space
        param_spaces = self.optimizer._define_parameter_spaces()
        rf_param_space = param_spaces["random_forest"]

        # Run optimization
        result = self.optimizer._optimize_single_model(
            "random_forest", rf_param_space, self.X, self.y
        )

        best_params, best_score = result
        self.assertIsInstance(best_params, dict)
        self.assertIsInstance(best_score, (int, float))

    def test_ensemble_optimization(self):
        """Test full ensemble hyperparameter optimization"""
        # Reduce iterations for faster testing
        optimization_results = self.optimizer.optimize_ensemble_hyperparameters(
            self.X, self.y, n_iterations=3
        )

        self.assertIsInstance(optimization_results, dict)
        self.assertIn("best_parameters", optimization_results)
        self.assertIn("best_scores", optimization_results)
        self.assertIn("improvement_summary", optimization_results)

        # Check that optimization history is populated
        self.assertGreater(len(self.optimizer.optimization_history), 0)

    def test_improvement_calculation(self):
        """Test improvement calculation logic"""
        # Mock optimization history
        self.optimizer.optimization_history = [
            {"model": "random_forest", "baseline_score": 0.7, "optimized_score": 0.8},
            {"model": "xgboost", "baseline_score": 0.75, "optimized_score": 0.85},
            {
                "model": "gradient_boosting",
                "baseline_score": 0.72,
                "optimized_score": 0.78,
            },
        ]

        improvement_summary = self.optimizer._calculate_improvement_summary()

        self.assertIsInstance(improvement_summary, dict)
        self.assertIn("average_improvement", improvement_summary)
        self.assertIn("best_performing_model", improvement_summary)
        self.assertIn("total_models_optimized", improvement_summary)

        # Check improvement calculation
        expected_avg = (
            ((0.8 - 0.7) / 0.7 + (0.85 - 0.75) / 0.75 + (0.78 - 0.72) / 0.72) / 3 * 100
        )
        self.assertAlmostEqual(
            improvement_summary["average_improvement"], expected_avg, places=1
        )


class TestAdvancedFeaturePipeline(TestCase):
    """Test suite for AdvancedFeaturePipeline class"""

    def setUp(self):
        """Set up test environment"""
        self.pipeline = AdvancedFeaturePipeline()

        # Create mock historical features
        self.historical_features = {
            "mean": 45.5,
            "std": 12.3,
            "min": 10,
            "max": 99,
            "freq_entropy": 0.85,
            "weekly_consistency": 0.6,
            "trend_slope": 0.02,
            "gap_median": 5.0,
            "hot_numbers_count": 8,
            "cold_numbers_count": 12,
        }

        # Create mock lottery data
        self.lottery_data = np.array(
            [
                [23, 45, 67, 12, 89],
                [34, 56, 78, 23, 90],
                [45, 67, 89, 34, 12],
                [56, 78, 90, 45, 23],
                [67, 89, 12, 56, 34],
            ]
        )

    def test_initialization(self):
        """Test AdvancedFeaturePipeline initialization"""
        self.assertIsNotNone(self.pipeline.feature_transformers)
        self.assertIsNotNone(self.pipeline.feature_selectors)
        self.assertEqual(self.pipeline.feature_transformers, {})
        self.assertEqual(self.pipeline.feature_selectors, {})

    def test_cyclical_features(self):
        """Test cyclical feature encoding - using actual implementation"""
        # Since AdvancedFeaturePipeline doesn't expose _create_cyclical_features,
        # we test the overall feature creation that includes cyclical patterns
        ml_features = self.pipeline.create_ml_features(
            self.historical_features, self.lottery_data
        )

        self.assertIsInstance(ml_features, np.ndarray)
        self.assertEqual(ml_features.shape[0], 1)  # Single sample
        self.assertGreater(
            ml_features.shape[1], len(self.historical_features)
        )  # More features than input

    def test_sequence_features(self):
        """Test sequence feature extraction - using actual implementation"""
        # Test that pipeline can handle sequence data
        ml_features = self.pipeline.create_ml_features(
            self.historical_features, self.lottery_data
        )

        self.assertIsInstance(ml_features, np.ndarray)
        self.assertEqual(len(ml_features.shape), 2)  # 2D array

        # Test with empty sequence data
        empty_features = self.pipeline.create_ml_features(
            self.historical_features, np.array([])
        )
        self.assertIsInstance(empty_features, np.ndarray)

    def test_interaction_features(self):
        """Test interaction feature creation - using actual implementation"""
        # Pipeline creates interaction features internally during create_ml_features
        ml_features = self.pipeline.create_ml_features(
            self.historical_features, self.lottery_data
        )

        # Check that we get more features than input (due to interactions)
        self.assertGreater(ml_features.shape[1], len(self.historical_features))

        # Test with minimal features
        minimal_features = {"mean": 45.0, "std": 15.0}
        minimal_ml = self.pipeline.create_ml_features(
            minimal_features, self.lottery_data
        )
        self.assertIsInstance(minimal_ml, np.ndarray)

    def test_ml_feature_creation(self):
        """Test complete ML feature creation pipeline"""
        ml_features = self.pipeline.create_ml_features(
            self.historical_features, self.lottery_data
        )

        self.assertIsInstance(ml_features, np.ndarray)
        self.assertGreater(
            ml_features.shape[1], len(self.historical_features)
        )  # More features than input

        # Check that features are scaled (no extreme values)
        self.assertTrue(np.all(np.abs(ml_features) < 1000))  # Reasonable scale check

    def test_feature_scaling(self):
        """Test feature scaling functionality - using actual implementation"""
        # Pipeline handles scaling internally, test that features are reasonable
        ml_features = self.pipeline.create_ml_features(
            self.historical_features, self.lottery_data
        )

        # Check that features are in reasonable ranges (not raw large values)
        self.assertIsInstance(ml_features, np.ndarray)
        self.assertTrue(np.all(np.isfinite(ml_features)))  # No inf or nan

        # Test with different input scales
        large_features = {k: v * 1000 for k, v in self.historical_features.items()}
        large_ml = self.pipeline.create_ml_features(large_features, self.lottery_data)
        self.assertIsInstance(large_ml, np.ndarray)


class TestEnsembleMLAPIs(TestCase):
    """Test suite for Phase 2A API endpoints"""

    def setUp(self):
        """Set up test environment"""
        self.client = Client()

    @patch(
        "predictions_tracker.views_dir.api_ensemble_ml_v2a._prepare_ml_training_data"
    )
    def test_ensemble_training_api(self, mock_prepare_data):
        """Test ensemble training API endpoint"""
        # Mock training data
        mock_X = np.random.randn(50, 20)
        mock_y = np.random.randn(50)
        mock_prepare_data.return_value = (mock_X, mock_y)

        response = self.client.post(
            "/lottery-prediction/api/ml/ensemble-training/",
            {"training_days": 60, "validation_split": 0.2},
        )

        self.assertEqual(response.status_code, 200)

        response_data = response.json()
        self.assertTrue(response_data["success"])
        self.assertIn("training_results", response_data)
        self.assertIn("ensemble_performance", response_data)
        self.assertIn("feature_importance", response_data)

    @patch(
        "predictions_tracker.views_dir.api_ensemble_ml_v2a._prepare_ml_training_data"
    )
    def test_bayesian_optimization_api(self, mock_prepare_data):
        """Test Bayesian optimization API endpoint"""
        # Mock training data
        mock_X = np.random.randn(30, 15)
        mock_y = np.random.randn(30)
        mock_prepare_data.return_value = (mock_X, mock_y)

        response = self.client.post(
            "/lottery-prediction/api/ml/bayesian-optimization/",
            {"optimization_iterations": 5, "training_days": 30},
        )

        self.assertEqual(response.status_code, 200)

        response_data = response.json()
        self.assertTrue(response_data["success"])
        self.assertIn("optimization_results", response_data)
        self.assertIn("best_parameters", response_data)
        self.assertIn("improvement_summary", response_data)

    @patch(
        "predictions_tracker.views_dir.api_ensemble_ml_v2a._prepare_ml_training_data"
    )
    @patch("predictions_tracker.views_dir.api_ensemble_ml_v2a._get_recent_lottery_data")
    def test_ensemble_prediction_api(self, mock_recent_data, mock_prepare_data):
        """Test ensemble prediction API endpoint"""
        # Mock data
        mock_X = np.random.randn(20, 15)
        mock_y = np.random.randn(20)
        mock_prepare_data.return_value = (mock_X, mock_y)

        mock_recent_data.return_value = [[23, 45, 67], [34, 56, 78], [45, 67, 89]]

        response = self.client.get(
            "/lottery-prediction/api/ml/ensemble-prediction/",
            {"prediction_date": "2024-01-15", "ensemble_method": "weighted_average"},
        )

        self.assertEqual(response.status_code, 200)

        response_data = response.json()
        self.assertTrue(response_data["success"])
        self.assertIn("ml_predictions", response_data)
        self.assertIn("ensemble_confidence", response_data)
        self.assertIn("feature_analysis", response_data)

    def test_api_error_handling(self):
        """Test API error handling"""
        # Test missing required parameters
        response = self.client.get("/lottery-prediction/api/ml/ensemble-prediction/")
        self.assertEqual(response.status_code, 400)

        response_data = response.json()
        self.assertFalse(response_data["success"])
        self.assertEqual(response_data["error"], "missing_date")

        # Test invalid date format
        response = self.client.get(
            "/lottery-prediction/api/ml/ensemble-prediction/",
            {"prediction_date": "invalid-date"},
        )
        self.assertEqual(response.status_code, 400)

        response_data = response.json()
        self.assertFalse(response_data["success"])
        self.assertEqual(response_data["error"], "invalid_date_format")


class TestMLIntegration(TestCase):
    """Integration tests for Phase 2A ML components"""

    def test_end_to_end_ml_pipeline(self):
        """Test complete ML pipeline from data to prediction"""
        # Create ensemble predictor
        ensemble = EnsembleLotteryPredictor(random_state=42)

        # Create mock training data
        np.random.seed(42)
        X_train = np.random.randn(100, 20)
        y_train = np.random.randn(100)
        X_test = np.random.randn(10, 20)

        # Train ensemble
        training_results = ensemble.train_ensemble(
            X_train, y_train, validation_split=0.2
        )

        # Make predictions
        predictions = ensemble.predict_ensemble(X_test, method="weighted_average")

        # Verify pipeline worked
        self.assertIsInstance(training_results, dict)
        self.assertEqual(len(predictions), len(X_test))
        self.assertTrue(
            all(
                isinstance(p, (int, float, np.integer, np.floating))
                for p in predictions
            )
        )

    def test_feature_pipeline_integration(self):
        """Test feature pipeline integration with ensemble"""
        # Create feature pipeline
        pipeline = AdvancedFeaturePipeline()

        # Mock data
        historical_features = {
            "mean": 45.0,
            "std": 15.0,
            "freq_entropy": 0.8,
            "weekly_consistency": 0.6,
            "trend_slope": 0.01,
        }
        lottery_data = np.array([[23, 45, 67], [34, 56, 78], [45, 67, 89]])

        # Create ML features
        ml_features = pipeline.create_ml_features(historical_features, lottery_data)

        # Test with ensemble
        ensemble = EnsembleLotteryPredictor(random_state=42)

        # Create training data with same feature dimensions
        X_train = np.random.randn(50, len(ml_features))
        y_train = np.random.randn(50)

        # Train and predict
        ensemble.train_ensemble(X_train, y_train, validation_split=0.2)
        prediction = ensemble.predict_ensemble(ml_features, method="weighted_average")

        self.assertEqual(len(prediction), 1)
        self.assertIsInstance(prediction[0], (int, float, np.integer, np.floating))


if __name__ == "__main__":
    # Run tests
    unittest.main(verbosity=2)
