# ===== 1. UNIT TESTS =====

# tests/test_features.py
import json
import unittest
from datetime import date, timedelta
from unittest.mock import MagicMock, patch

import numpy as np
import pandas as pd

# tests/test_integration.py
from django.test import Client, TestCase
from django.urls import reverse
from django.utils import timezone

from lottery_prediction.ml.features.extractors import LotteryFeatureExtractor
from lottery_prediction.ml.features.validators import DataLeakageValidator
from results.models import KetQuaXoSo


class TestLotteryPredictionIntegration(TestCase):
    def setUp(self):
        self.client = Client()
        self.prediction_date = date(2025, 7, 25)

        # Create comprehensive test dataset
        self.create_test_dataset()

    def create_test_dataset(self):
        """Create realistic test dataset"""
        # Create 200 days of historical data
        for i in range(200):
            test_date = self.prediction_date - timedelta(days=i + 1)

            # Generate more realistic lottery numbers
            numbers = []
            for j in range(27):  # Total numbers in all prizes
                num = (i * 7 + j * 3) % 100
                numbers.append(f"{num:02d}")

            KetQuaXoSo.objects.create(
                thu=f"Thứ {(i % 7) + 2}",
                ngay=test_date,
                giai_db=f"{numbers[0]:0>5}",
                giai_1=f"{numbers[1]:0>5}",
                giai_2=f"{numbers[2]:0>5},{numbers[3]:0>5}",
                giai_3=f"{numbers[4]:0>5},{numbers[5]:0>5},{numbers[6]:0>5},{numbers[7]:0>5},{numbers[8]:0>5},{numbers[9]:0>5}",
                giai_4=f"{numbers[10]:0>4},{numbers[11]:0>4},{numbers[12]:0>4},{numbers[13]:0>4}",
                giai_5=f"{numbers[14]:0>3},{numbers[15]:0>3},{numbers[16]:0>3},{numbers[17]:0>3},{numbers[18]:0>3},{numbers[19]:0>3}",
                giai_6=f"{numbers[20]:0>2},{numbers[21]:0>2},{numbers[22]:0>2}",
                giai_7=f"{numbers[23]:0>1},{numbers[24]:0>1},{numbers[25]:0>1},{numbers[26]:0>1}",
            )

    def test_end_to_end_prediction_workflow(self):
        """Test complete prediction workflow"""
        # 1. Train models first
        train_url = reverse("lottery_prediction:retrain")
        train_response = self.client.post(
            train_url, {"training_date": self.prediction_date - timedelta(days=1)}
        )

        self.assertEqual(train_response.status_code, 200)
        train_data = json.loads(train_response.content)
        self.assertEqual(train_data["status"], "success")

        # 2. Make prediction
        predict_url = reverse("lottery_prediction:predict")
        predict_response = self.client.get(
            predict_url, {"prediction_date": self.prediction_date}
        )

        self.assertEqual(predict_response.status_code, 200)
        predict_data = json.loads(predict_response.content)

        # 3. Validate prediction structure
        self.assertIn("top_10_predictions", predict_data)
        self.assertEqual(len(predict_data["top_10_predictions"]), 10)

        # 4. Check each prediction has required fields
        for pred in predict_data["top_10_predictions"]:
            self.assertIn("number", pred)
            self.assertIn("probability", pred)
            self.assertIn("rank", pred)
            self.assertRegex(pred["number"], r"^\d{2}$")  # 2-digit format

    def test_data_leakage_prevention(self):
        """Test system prevents data leakage"""
        # Try to predict for a date that has data
        existing_date = self.prediction_date - timedelta(days=1)

        predict_url = reverse("lottery_prediction:predict")
        response = self.client.get(predict_url, {"prediction_date": existing_date})

        # Should still work but use only data before existing_date
        self.assertEqual(response.status_code, 200)

        # Try to predict for future date (should work)
        future_date = date.today() + timedelta(days=1)
        response = self.client.get(predict_url, {"prediction_date": future_date})

        self.assertEqual(response.status_code, 200)

    def test_model_performance_tracking(self):
        """Test performance tracking integration"""
        # First make a prediction
        predict_url = reverse("lottery_prediction:predict")
        self.client.get(predict_url, {"prediction_date": self.prediction_date})

        # Check performance endpoint
        performance_url = reverse("lottery_prediction:model-performance")
        response = self.client.get(performance_url)

        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)

        self.assertIn("models", data)
        self.assertIn("overall_stats", data)

    def test_concurrent_requests(self):
        """Test system handles concurrent requests"""
        import queue
        import threading

        results = queue.Queue()

        def make_request():
            try:
                predict_url = reverse("lottery_prediction:predict")
                response = self.client.get(
                    predict_url, {"prediction_date": self.prediction_date}
                )
                results.put(response.status_code)
            except Exception as e:
                results.put(str(e))

        # Create 5 concurrent threads
        threads = []
        for i in range(5):
            thread = threading.Thread(target=make_request)
            threads.append(thread)
            thread.start()

        # Wait for all threads
        for thread in threads:
            thread.join()

        # Check all requests succeeded
        while not results.empty():
            result = results.get()
            self.assertEqual(result, 200)
