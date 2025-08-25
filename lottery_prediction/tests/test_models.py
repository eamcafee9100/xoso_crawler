# tests/test_models.py
# tests/test_features.py
import unittest
from datetime import date, timedelta
from unittest.mock import MagicMock, patch

import numpy as np
import pandas as pd
from django.test import TestCase
from django.utils import timezone

from lottery_prediction.ml.features.extractors import LotteryFeatureExtractor
from lottery_prediction.ml.features.validators import DataLeakageValidator
from lottery_prediction.ml.models.baseline import FrequencyBasedPredictor
from lottery_prediction.ml.models.ensemble import WeightedEnsemble
from lottery_prediction.ml.models.gradient_boosting import GradientBoostingPredictor
from results.models import KetQuaXoSo

# ===== 1. UNIT TESTS =====


class TestGradientBoostingPredictor(TestCase):
    def setUp(self):
        self.predictor = GradientBoostingPredictor()
        self.training_date = date(2025, 7, 20)

        # Create substantial test data
        for i in range(100):  # 100 days of data
            test_date = self.training_date - timedelta(days=i)
            KetQuaXoSo.objects.create(
                thu=f"Thứ {(i % 7) + 2}",
                ngay=test_date,
                giai_db=f"{i:05d}",
                giai_1=f"{(i+1):05d}",
                giai_2=f"{(i+2):05d},{(i+3):05d}",
                giai_3=f"{(i+4):05d},{(i+5):05d},{(i+6):05d},{(i+7):05d},{(i+8):05d},{(i+9):05d}",
                giai_4=f"{(i+10):04d},{(i+11):04d},{(i+12):04d},{(i+13):04d}",
                giai_5=f"{(i+14):03d},{(i+15):03d},{(i+16):03d},{(i+17):03d},{(i+18):03d},{(i+19):03d}",
                giai_6=f"{(i+20):02d},{(i+21):02d},{(i+22):02d}",
                giai_7=f"{(i+23):01d},{(i+24):01d},{(i+25):01d},{(i+26):01d}",
            )

    def test_model_training(self):
        """Test model can be trained without errors"""
        try:
            self.predictor.train(self.training_date)
            self.assertTrue(self.predictor.is_trained)
        except Exception as e:
            self.fail(f"Model training failed: {str(e)}")

    def test_prediction_format(self):
        """Test prediction output format"""
        self.predictor.train(self.training_date)
        predictions = self.predictor.predict(self.training_date + timedelta(days=1))

        # Check structure
        self.assertIsInstance(predictions, dict)
        self.assertIn("top_10_predictions", predictions)
        self.assertEqual(len(predictions["top_10_predictions"]), 10)

        # Check prediction format
        first_pred = predictions["top_10_predictions"][0]
        self.assertIn("number", first_pred)
        self.assertIn("probability", first_pred)
        self.assertIn("rank", first_pred)

    def test_probability_sum(self):
        """Test probabilities are valid"""
        self.predictor.train(self.training_date)
        predictions = self.predictor.predict(self.training_date + timedelta(days=1))

        probs = [p["probability"] for p in predictions["top_10_predictions"]]

        # All probabilities should be positive
        self.assertTrue(all(p > 0 for p in probs))

        # Should be sorted in descending order
        self.assertEqual(probs, sorted(probs, reverse=True))


class TestWeightedEnsemble(TestCase):
    def setUp(self):
        self.ensemble = WeightedEnsemble()
        self.training_date = date(2025, 7, 20)

        # Create test data (same as above)
        for i in range(50):
            test_date = self.training_date - timedelta(days=i)
            KetQuaXoSo.objects.create(
                thu=f"Thứ {(i % 7) + 2}",
                ngay=test_date,
                giai_db=f"{i:05d}",
                giai_1=f"{(i+1):05d}",
                giai_2=f"{(i+2):05d},{(i+3):05d}",
                giai_3=f"{(i+4):05d},{(i+5):05d},{(i+6):05d},{(i+7):05d},{(i+8):05d},{(i+9):05d}",
                giai_4=f"{(i+10):04d},{(i+11):04d},{(i+12):04d},{(i+13):04d}",
                giai_5=f"{(i+14):03d},{(i+15):03d},{(i+16):03d},{(i+17):03d},{(i+18):03d},{(i+19):03d}",
                giai_6=f"{(i+20):02d},{(i+21):02d},{(i+22):02d}",
                giai_7=f"{(i+23):01d},{(i+24):01d},{(i+25):01d},{(i+26):01d}",
            )

    def test_ensemble_training(self):
        """Test ensemble can train multiple models"""
        try:
            self.ensemble.train(self.training_date)
            self.assertTrue(len(self.ensemble.models) > 1)
        except Exception as e:
            self.fail(f"Ensemble training failed: {str(e)}")

    def test_ensemble_prediction_aggregation(self):
        """Test ensemble properly aggregates predictions"""
        self.ensemble.train(self.training_date)
        predictions = self.ensemble.predict(self.training_date + timedelta(days=1))

        # Should have model_info showing ensemble details
        self.assertIn("model_info", predictions)
        self.assertIn("ensemble_weights", predictions["model_info"])
