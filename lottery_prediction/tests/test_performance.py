# tests/test_performance.py
import os
import time

# tests/test_features.py
import unittest
from datetime import date, timedelta
from unittest.mock import MagicMock, patch

import numpy as np
import pandas as pd
import psutil
from django.test import TestCase
from django.test.utils import override_settings
from django.utils import timezone

from lottery_prediction.ml.features.extractors import LotteryFeatureExtractor
from lottery_prediction.ml.features.validators import DataLeakageValidator
from results.models import KetQuaXoSo

# ===== 1. UNIT TESTS =====


class TestSystemPerformance(TestCase):
    def setUp(self):
        self.prediction_date = date(2025, 7, 25)

        # Create large dataset for performance testing
        for i in range(1000):  # 1000 days of data
            test_date = self.prediction_date - timedelta(days=i + 1)
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

    def test_feature_extraction_performance(self):
        """Test feature extraction performance"""
        from lottery_prediction.ml.features.extractors import LotteryFeatureExtractor

        extractor = LotteryFeatureExtractor()

        start_time = time.time()
        start_memory = psutil.Process(os.getpid()).memory_info().rss / 1024 / 1024  # MB

        features = extractor.extract_features_for_date(self.prediction_date)

        end_time = time.time()
        end_memory = psutil.Process(os.getpid()).memory_info().rss / 1024 / 1024  # MB

        execution_time = end_time - start_time
        memory_usage = end_memory - start_memory

        # Performance assertions
        self.assertLess(
            execution_time, 30, "Feature extraction should complete within 30 seconds"
        )
        self.assertLess(memory_usage, 500, "Memory usage should be less than 500MB")

        print(
            f"Feature extraction: {execution_time:.2f}s, Memory: {memory_usage:.2f}MB"
        )

    def test_model_training_performance(self):
        """Test model training performance"""
        from lottery_prediction.ml.models.gradient_boosting import (
            GradientBoostingPredictor,
        )

        predictor = GradientBoostingPredictor()

        start_time = time.time()
        start_memory = psutil.Process(os.getpid()).memory_info().rss / 1024 / 1024

        predictor.train(self.prediction_date - timedelta(days=1))

        end_time = time.time()
        end_memory = psutil.Process(os.getpid()).memory_info().rss / 1024 / 1024

        execution_time = end_time - start_time
        memory_usage = end_memory - start_memory

        # Performance assertions
        self.assertLess(
            execution_time, 300, "Model training should complete within 5 minutes"
        )
        self.assertLess(memory_usage, 1000, "Memory usage should be less than 1GB")

        print(f"Model training: {execution_time:.2f}s, Memory: {memory_usage:.2f}MB")

    def test_prediction_response_time(self):
        """Test prediction API response time"""
        from django.test import Client

        client = Client()

        # Pre-train model
        from lottery_prediction.ml.models.gradient_boosting import (
            GradientBoostingPredictor,
        )

        predictor = GradientBoostingPredictor()
        predictor.train(self.prediction_date - timedelta(days=1))

        # Test multiple requests
        response_times = []

        for i in range(10):
            start_time = time.time()

            response = client.get(
                reverse("lottery_prediction:predict"),
                {"prediction_date": self.prediction_date + timedelta(days=i)},
            )

            end_time = time.time()
            response_times.append(end_time - start_time)

            self.assertEqual(response.status_code, 200)

        avg_response_time = sum(response_times) / len(response_times)
        max_response_time = max(response_times)

        # Performance assertions
        self.assertLess(
            avg_response_time, 5, "Average response time should be less than 5 seconds"
        )
        self.assertLess(
            max_response_time, 10, "Max response time should be less than 10 seconds"
        )

        print(
            f"API Response - Avg: {avg_response_time:.2f}s, Max: {max_response_time:.2f}s"
        )
