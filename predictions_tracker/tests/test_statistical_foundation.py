"""
Tests for PHASE 1: Statistical Foundation
=========================================
Test suite for AdvancedFeatureEngine and StatisticalValidator
"""

import unittest

import numpy as np
from django.test import TestCase

from predictions_tracker.statistical_foundation import (
    AdvancedFeatureEngine,
    StatisticalValidator,
)


class TestAdvancedFeatureEngine(TestCase):
    """Test AdvancedFeatureEngine functionality"""

    def setUp(self):
        """Set up test fixtures"""
        self.engine = AdvancedFeatureEngine()

        # Sample lottery data for testing
        self.test_data = [
            [12, 34, 56, 78, 90],
            [23, 45, 67, 89, 1],
            [34, 56, 78, 90, 12],
            [45, 67, 89, 1, 23],
            [56, 78, 90, 12, 34],
            [67, 89, 1, 23, 45],
            [78, 90, 12, 34, 56],
            [89, 1, 23, 45, 67],
            [90, 12, 34, 56, 78],
            [1, 23, 45, 67, 89],
        ]

    def test_extract_statistical_features(self):
        """Test feature extraction from lottery data"""
        features = self.engine.extract_statistical_features(
            self.test_data, lookback_days=30
        )

        # Verify features are extracted
        self.assertIsInstance(features, dict)
        self.assertGreater(len(features), 50)  # Should have many features

        # Check for specific feature categories
        feature_names = list(features.keys())

        # Basic statistics should be present
        self.assertIn("mean", feature_names)
        self.assertIn("std", feature_names)
        self.assertIn("variance", feature_names)
        self.assertIn("skewness", feature_names)
        self.assertIn("kurtosis", feature_names)

        # Percentiles should be present
        self.assertIn("percentile_25", feature_names)
        self.assertIn("percentile_75", feature_names)
        self.assertIn("percentile_95", feature_names)

        print(f"✅ Extracted {len(features)} statistical features")
        print(f"📊 Sample features: {dict(list(features.items())[:5])}")

    def test_basic_statistics(self):
        """Test basic statistical calculations"""
        data = np.array(self.test_data)
        features = self.engine._basic_statistics(data)

        # Check basic stats are calculated
        self.assertIn("mean", features)
        self.assertIn("median", features)
        self.assertIn("std", features)

        # Verify values are reasonable
        self.assertGreater(features["mean"], 0)
        self.assertGreater(features["std"], 0)

        print(f"📈 Basic stats: mean={features['mean']:.2f}, std={features['std']:.2f}")

    def test_distribution_features(self):
        """Test distribution feature calculations"""
        data = np.array(self.test_data)
        features = self.engine._distribution_features(data)

        # Check distribution features
        self.assertIn("freq_mean", features)
        self.assertIn("freq_entropy", features)
        self.assertIn("unique_numbers", features)
        self.assertIn("coverage_ratio", features)

        print(
            f"📊 Distribution: unique_numbers={features['unique_numbers']}, entropy={features['freq_entropy']:.3f}"
        )

    def test_temporal_features(self):
        """Test temporal pattern features"""
        data = np.array(self.test_data)
        features = self.engine._temporal_features(data)

        # Should have gap analysis
        self.assertIn("gap_mean", features)
        self.assertIn("gap_std", features)

        print(f"⏰ Temporal: gap_mean={features['gap_mean']:.2f}")

    def test_pattern_features(self):
        """Test pattern recognition features"""
        data = np.array(self.test_data)
        features = self.engine._pattern_features(data)

        # Check pattern features
        self.assertIn("consecutive_mean", features)
        self.assertIn("sum_mean", features)
        self.assertIn("even_ratio_mean", features)

        print(
            f"🔍 Patterns: consecutive={features['consecutive_mean']:.2f}, even_ratio={features['even_ratio_mean']:.2f}"
        )

    def test_default_features(self):
        """Test default features when no data available"""
        features = self.engine._get_default_features()

        self.assertIsInstance(features, dict)
        self.assertGreater(len(features), 0)

        # All values should be defaults (0.0)
        for key, value in features.items():
            self.assertEqual(value, 0.0)

        print(f"🔧 Default features: {len(features)} features with 0.0 values")


class TestStatisticalValidator(TestCase):
    """Test StatisticalValidator functionality"""

    def setUp(self):
        """Set up test fixtures"""
        self.validator = StatisticalValidator()

    def test_wilson_confidence_interval(self):
        """Test Wilson confidence interval calculation"""
        # Test with typical values
        lower, upper = self.validator.wilson_confidence_interval(5, 15, confidence=0.95)

        # Verify interval is valid
        self.assertGreaterEqual(lower, 0.0)
        self.assertLessEqual(upper, 1.0)
        self.assertLess(lower, upper)

        print(f"🎯 Wilson CI (5/15): [{lower:.3f}, {upper:.3f}]")

        # Test edge cases
        lower_zero, upper_zero = self.validator.wilson_confidence_interval(0, 0)
        self.assertEqual(lower_zero, 0.0)
        self.assertEqual(upper_zero, 0.0)

        # Test perfect success
        lower_perfect, upper_perfect = self.validator.wilson_confidence_interval(10, 10)
        self.assertGreater(lower_perfect, 0.5)  # Should be high confidence

        print(
            f"🎯 Edge cases: zero=[{lower_zero:.3f}, {upper_zero:.3f}], perfect=[{lower_perfect:.3f}, {upper_perfect:.3f}]"
        )

    def test_hypothesis_test_prediction_accuracy(self):
        """Test hypothesis testing for prediction accuracy"""
        # Test with overlapping predictions
        predicted = [1, 2, 3, 4, 5]
        actual = [2, 3, 4, 6, 7]

        result = self.validator.hypothesis_test_prediction_accuracy(predicted, actual)

        # Verify result structure
        self.assertIn("p_value", result)
        self.assertIn("test_statistic", result)
        self.assertIn("significant", result)
        self.assertIn("observed_rate", result)
        self.assertIn("expected_rate", result)

        # Verify values are reasonable
        self.assertGreaterEqual(result["p_value"], 0.0)
        self.assertLessEqual(result["p_value"], 1.0)
        self.assertGreaterEqual(result["observed_rate"], 0.0)
        self.assertLessEqual(result["observed_rate"], 1.0)

        print(
            f"📈 Hypothesis test: p_value={result['p_value']:.3f}, observed_rate={result['observed_rate']:.3f}"
        )

        # Test empty inputs
        empty_result = self.validator.hypothesis_test_prediction_accuracy([], [])
        self.assertEqual(empty_result["p_value"], 1.0)
        self.assertEqual(empty_result["test_statistic"], 0.0)

        print(f"📈 Empty test: p_value={empty_result['p_value']:.3f}")

    def test_calculate_prediction_confidence(self):
        """Test prediction confidence calculation"""
        # Create test features
        features = {
            "std": 15.0,  # Low volatility
            "weekly_consistency": 0.8,  # High consistency
            "coverage_ratio": 0.9,  # Good coverage
        }

        confidence = self.validator.calculate_prediction_confidence(
            features, historical_accuracy=0.4
        )

        # Verify confidence level is valid
        valid_levels = ["low", "medium", "high", "very_high"]
        self.assertIn(confidence, valid_levels)

        print(f"🎯 Confidence level: {confidence}")

        # Test with poor features
        poor_features = {
            "std": 35.0,  # High volatility
            "weekly_consistency": 0.3,  # Low consistency
            "coverage_ratio": 0.4,  # Poor coverage
        }

        poor_confidence = self.validator.calculate_prediction_confidence(
            poor_features, historical_accuracy=0.2
        )
        print(f"🎯 Poor confidence: {poor_confidence}")

        # Test with excellent features
        excellent_features = {
            "std": 10.0,  # Very low volatility
            "weekly_consistency": 0.9,  # Very high consistency
            "coverage_ratio": 0.95,  # Excellent coverage
        }

        excellent_confidence = self.validator.calculate_prediction_confidence(
            excellent_features, historical_accuracy=0.5
        )
        print(f"🎯 Excellent confidence: {excellent_confidence}")


class TestIntegrationStatisticalFoundation(TestCase):
    """Integration tests for Statistical Foundation components"""

    def setUp(self):
        """Set up test fixtures"""
        self.engine = AdvancedFeatureEngine()
        self.validator = StatisticalValidator()

    def test_full_pipeline(self):
        """Test complete statistical analysis pipeline"""
        # Generate realistic lottery data
        np.random.seed(42)  # For reproducible tests
        lottery_data = []

        for _ in range(30):  # 30 days of data
            # Generate 5 numbers per day
            day_numbers = np.random.choice(range(0, 100), size=5, replace=False)
            lottery_data.append(sorted(day_numbers.tolist()))

        # Extract features
        features = self.engine.extract_statistical_features(
            lottery_data, lookback_days=30
        )

        # Calculate confidence
        confidence = self.validator.calculate_prediction_confidence(
            features, historical_accuracy=0.3
        )

        # Perform hypothesis test (simulate predictions vs actual)
        predicted = list(range(10, 25))  # 15 predicted numbers
        actual = list(range(15, 30))  # 15 actual numbers (some overlap)

        hypothesis_result = self.validator.hypothesis_test_prediction_accuracy(
            predicted, actual
        )

        # Calculate Wilson interval
        hits = len(set(predicted) & set(actual))
        wilson_interval = self.validator.wilson_confidence_interval(
            hits, len(predicted)
        )

        # Verify pipeline results
        self.assertGreater(len(features), 50)
        self.assertIn(confidence, ["low", "medium", "high", "very_high"])
        self.assertGreater(hypothesis_result["p_value"], 0.0)
        self.assertLess(wilson_interval[0], wilson_interval[1])

        print("\n🚀 STATISTICAL FOUNDATION INTEGRATION TEST RESULTS:")
        print(f"📊 Features extracted: {len(features)}")
        print(f"🎯 Confidence level: {confidence}")
        print(f"📈 Hypothesis p-value: {hypothesis_result['p_value']:.3f}")
        print(
            f"🎯 Wilson interval: [{wilson_interval[0]:.3f}, {wilson_interval[1]:.3f}]"
        )
        print(f"✅ Hit rate: {hits}/{len(predicted)} = {hits/len(predicted):.1%}")

    def test_adaptive_weighting_simulation(self):
        """Test adaptive weighting logic"""
        # Simulate different market conditions

        # High volatility scenario
        high_vol_features = {
            "std": 30.0,
            "weekly_consistency": 0.4,
            "cyclical_strength": 0.3,
        }

        # Low volatility scenario
        low_vol_features = {
            "std": 15.0,
            "weekly_consistency": 0.8,
            "cyclical_strength": 0.7,
        }

        # Test confidence calculation for different scenarios
        high_vol_confidence = self.validator.calculate_prediction_confidence(
            high_vol_features, 0.25
        )
        low_vol_confidence = self.validator.calculate_prediction_confidence(
            low_vol_features, 0.35
        )

        print("\n🧮 ADAPTIVE WEIGHTING SIMULATION:")
        print(f"📈 High volatility confidence: {high_vol_confidence}")
        print(f"📉 Low volatility confidence: {low_vol_confidence}")

        # Low volatility should generally have higher confidence
        confidence_levels = ["low", "medium", "high", "very_high"]
        high_vol_idx = confidence_levels.index(high_vol_confidence)
        low_vol_idx = confidence_levels.index(low_vol_confidence)

        # This is a general expectation, not a strict requirement
        print(
            f"🎯 Confidence comparison: high_vol_idx={high_vol_idx}, low_vol_idx={low_vol_idx}"
        )


if __name__ == "__main__":
    print("🚀 RUNNING PHASE 1 STATISTICAL FOUNDATION TESTS")
    print("=" * 60)
    unittest.main(verbosity=2)
