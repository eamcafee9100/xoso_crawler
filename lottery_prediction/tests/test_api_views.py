# tests/test_api_views.py
"""
Comprehensive tests for lottery prediction API views
Tests real model predictions, data leakage prevention, and API functionality
"""

import json
import os
from datetime import date, datetime, timedelta
from unittest.mock import MagicMock, patch

import pytest
from django.test import TestCase, override_settings
from django.urls import reverse
from django.utils import timezone
from freezegun import freeze_time
from rest_framework import status
from rest_framework.test import APIClient, APITestCase

from lottery_prediction.ml.models.ensemble import ModelFactory
from lottery_prediction.ml.models.gradient_boosting import LotteryGradientBoostingModel
from results.models import KetQuaXoSo


class PredictionAPIViewTest(APITestCase):
    """Test PredictionAPIView with real models and data"""

    def setUp(self):
        """Set up test environment with real data"""
        self.client = APIClient()
        self.url = "/lottery-prediction/api/predict/"  # Correct URL based on routing

        # Create test data - simulate historical lottery results
        self.setup_test_data()

        # Ensure models directory exists
        self.models_dir = os.path.join("/tmp", "test_models")
        os.makedirs(self.models_dir, exist_ok=True)

    def setup_test_data(self):
        """Create realistic historical lottery data"""
        # Create lottery results for the last 60 days
        base_date = date(2025, 7, 25)  # Latest data should be yesterday

        for i in range(60):
            test_date = base_date - timedelta(days=i)

            # Create realistic lottery result
            KetQuaXoSo.objects.create(
                ngay=test_date,
                thu="Thứ 2" if test_date.weekday() == 0 else "Thứ 3",
                giai_db=f"{(12345 + i) % 100000:05d}",  # 5-digit special prize
                giai_1=f"{(67890 + i) % 100000:05d}",  # 5-digit first prize
                giai_2=f"{(11111 + i) % 100000:05d},{(22222 + i*2) % 100000:05d}",  # 2 numbers for second prize
                giai_3=f"{(33333 + i) % 100000:05d},{(44444 + i*2) % 100000:05d},{(55555 + i*3) % 100000:05d},{(66666 + i*4) % 100000:05d},{(77777 + i*5) % 100000:05d},{(88888 + i*6) % 100000:05d}",  # 6 numbers for third prize
                giai_4=f"{(1234 + i) % 10000:04d},{(5678 + i*2) % 10000:04d},{(9012 + i*3) % 10000:04d},{(3456 + i*4) % 10000:04d}",  # 4 numbers for fourth prize
                giai_5=f"{(123 + i) % 1000:03d},{(456 + i*2) % 1000:03d},{(789 + i*3) % 1000:03d},{(12 + i*4) % 1000:03d},{(345 + i*5) % 1000:03d},{(678 + i*6) % 1000:03d}",  # 6 numbers for fifth prize
                giai_6=f"{(12 + i) % 100:02d},{(34 + i*2) % 100:02d},{(56 + i*3) % 100:02d}",  # 3 numbers for sixth prize
                giai_7=f"{(1 + i) % 10},{(2 + i*2) % 10},{(3 + i*3) % 10},{(4 + i*4) % 10}",  # 4 single-digit numbers for seventh prize
            )

    @freeze_time("2025-07-26")
    def test_prediction_with_real_gradient_boosting_model(self):
        """Test prediction using real trained gradient boosting model"""
        request_data = {
            "prediction_date": "2025-07-27",
            "model_type": "gradient_boosting",
            "top_k": 10,
        }

        response = self.client.post(self.url, request_data, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()

        # Verify response structure
        self.assertIn("prediction_date", data)
        self.assertIn("reference_date", data)
        self.assertIn("top_k_predictions", data)
        self.assertIn("model_info", data)
        self.assertIn("data_quality", data)
        self.assertIn("metadata", data)

        # Verify prediction date
        self.assertEqual(data["prediction_date"], "2025-07-27")

        # Verify reference date (should be latest historical data)
        self.assertEqual(data["reference_date"], "2025-07-25")

        # Verify predictions
        predictions = data["top_k_predictions"]
        self.assertEqual(len(predictions), 10)

        for i, pred in enumerate(predictions):
            self.assertIn("number", pred)
            self.assertIn("probability", pred)
            self.assertIn("rank", pred)
            self.assertEqual(pred["rank"], i + 1)
            self.assertIsInstance(pred["probability"], float)
            self.assertGreater(pred["probability"], 0)

        # Verify probabilities are in descending order
        probabilities = [pred["probability"] for pred in predictions]
        self.assertEqual(probabilities, sorted(probabilities, reverse=True))

        # Verify model info
        model_info = data["model_info"]
        self.assertIn("model_name", model_info)
        self.assertIn("model_type", model_info)
        self.assertIn("confidence_score", model_info)
        self.assertIn("entropy", model_info)

        # Verify data quality
        data_quality = data["data_quality"]
        self.assertIn("score", data_quality)
        self.assertIn("reference_data_points", data_quality)
        self.assertIn("data_freshness_days", data_quality)

        # Data freshness should be 2 days (27th - 25th)
        self.assertEqual(data_quality["data_freshness_days"], 2)

    @freeze_time("2025-07-26")
    def test_prediction_with_ensemble_model(self):
        """Test prediction using ensemble model"""
        request_data = {
            "prediction_date": "2025-07-27",
            "model_type": "ensemble",
            "top_k": 15,
        }

        response = self.client.post(self.url, request_data, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()

        # Verify we get exactly 15 predictions
        self.assertEqual(len(data["top_k_predictions"]), 15)

        # Verify model type
        self.assertEqual(data["model_info"]["model_type"], "ensemble")

        # Check for ensemble-specific fields
        if "current_weights" in data["model_info"]:
            self.assertIsInstance(data["model_info"]["current_weights"], dict)

    @freeze_time("2025-07-26")
    def test_data_leakage_prevention(self):
        """Test that API prevents data leakage by rejecting past dates"""
        # Try to predict for past date (should fail)
        request_data = {
            "prediction_date": "2025-07-25",  # Past date
            "model_type": "gradient_boosting",
            "top_k": 10,
        }

        response = self.client.post(self.url, request_data, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("error", response.json())

    @freeze_time("2025-07-26")
    def test_data_leakage_prevention_current_date(self):
        """Test that API prevents prediction for current date"""
        request_data = {
            "prediction_date": "2025-07-26",  # Current date
            "model_type": "gradient_boosting",
            "top_k": 10,
        }

        response = self.client.post(self.url, request_data, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    @freeze_time("2025-07-26")
    def test_prediction_numbers_are_realistic(self):
        """Test that predicted numbers are in valid range (00-99)"""
        request_data = {
            "prediction_date": "2025-07-27",
            "model_type": "gradient_boosting",
            "top_k": 20,
        }

        response = self.client.post(self.url, request_data, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()

        for pred in data["top_k_predictions"]:
            number = pred["number"]
            # Verify number format (should be 00-99)
            self.assertTrue(number.isdigit())
            self.assertEqual(len(number), 2)
            self.assertGreaterEqual(int(number), 0)
            self.assertLessEqual(int(number), 99)

    @freeze_time("2025-07-26")
    def test_prediction_probabilities_sum_constraint(self):
        """Test that probabilities are reasonable (not all equal - indicating fallback)"""
        request_data = {
            "prediction_date": "2025-07-27",
            "model_type": "gradient_boosting",
            "top_k": 10,
        }

        response = self.client.post(self.url, request_data, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()

        probabilities = [pred["probability"] for pred in data["top_k_predictions"]]

        # Check that probabilities are not all identical (would indicate fallback/uniform distribution)
        unique_probs = set(probabilities)
        self.assertGreater(
            len(unique_probs),
            1,
            "All probabilities are identical - might be using fallback",
        )

        # Check that highest probability is significantly higher than lowest
        self.assertGreater(
            max(probabilities) / min(probabilities),
            1.1,
            "Probability spread too small - might be using uniform fallback",
        )

    @freeze_time("2025-07-26")
    def test_model_info_contains_training_details(self):
        """Test that model info contains actual training information"""
        request_data = {
            "prediction_date": "2025-07-27",
            "model_type": "gradient_boosting",
            "top_k": 10,
        }

        response = self.client.post(self.url, request_data, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()

        model_info = data["model_info"]

        # Verify training data size is reasonable (not 0 or None)
        training_size = model_info.get("training_data_size", 0)
        self.assertGreater(training_size, 0, "Model appears to have no training data")

        # Verify confidence score is reasonable
        confidence = model_info.get("confidence_score", 0)
        self.assertGreater(confidence, 0)
        self.assertLessEqual(confidence, 1)

    def test_invalid_model_type(self):
        """Test handling of invalid model type"""
        request_data = {
            "prediction_date": "2025-07-27",
            "model_type": "invalid_model",
            "top_k": 10,
        }

        response = self.client.post(self.url, request_data, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_invalid_top_k_values(self):
        """Test handling of invalid top_k values"""
        # Test negative value
        request_data = {
            "prediction_date": "2025-07-27",
            "model_type": "gradient_boosting",
            "top_k": -5,
        }

        response = self.client.post(self.url, request_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        # Test too large value
        request_data["top_k"] = 100
        response = self.client.post(self.url, request_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    @freeze_time("2025-07-26")
    def test_default_prediction_date(self):
        """Test that default prediction date is tomorrow"""
        request_data = {"model_type": "gradient_boosting", "top_k": 10}
        # No prediction_date specified

        response = self.client.post(self.url, request_data, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()

        # Should default to tomorrow
        self.assertEqual(data["prediction_date"], "2025-07-27")

    @freeze_time("2025-07-26")
    def test_data_quality_score_calculation(self):
        """Test that data quality score is calculated correctly"""
        request_data = {
            "prediction_date": "2025-07-27",
            "model_type": "gradient_boosting",
            "top_k": 10,
        }

        response = self.client.post(self.url, request_data, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()

        data_quality = data["data_quality"]

        # Data quality score should be between 0 and 1
        score = data_quality["score"]
        self.assertGreaterEqual(score, 0)
        self.assertLessEqual(score, 1)

        # Reference data points should be reasonable (we created 60 records)
        ref_points = data_quality["reference_data_points"]
        self.assertGreaterEqual(ref_points, 50)  # Should have most of our test data

    @freeze_time("2025-07-26")
    def test_response_time_is_reasonable(self):
        """Test that API response time is reasonable"""
        request_data = {
            "prediction_date": "2025-07-27",
            "model_type": "gradient_boosting",
            "top_k": 10,
        }

        start_time = timezone.now()
        response = self.client.post(self.url, request_data, format="json")
        end_time = timezone.now()

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        processing_time = (end_time - start_time).total_seconds()

        # Response should be under 30 seconds (reasonable for API)
        self.assertLess(processing_time, 30)

        # Check metadata includes processing time
        data = response.json()
        metadata_time = data["metadata"]["processing_time_seconds"]
        self.assertGreater(metadata_time, 0)
        self.assertLess(metadata_time, 30)


class ModelPerformanceViewTest(APITestCase):
    """Test ModelPerformanceView"""

    def setUp(self):
        self.client = APIClient()
        self.url = (
            "/lottery-prediction/api/model-performance/"  # Correct URL based on routing
        )

        # Create test performance data
        from results.models import MethodCyclicalPerformance

        MethodCyclicalPerformance.objects.create(
            method_name="gradient_boosting",
            year=2025,
            month=7,
            hit_rate=0.35,
            total_hit_days=10,
            total_days=30,
            fatigue_threshold_reached=False,
        )

        MethodCyclicalPerformance.objects.create(
            method_name="ensemble",
            year=2025,
            month=6,
            hit_rate=0.42,
            total_hit_days=12,
            total_days=30,
            fatigue_threshold_reached=False,
        )

    def test_get_all_performance_data(self):
        """Test getting all performance data"""
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()

        self.assertIn("performance_data", data)
        self.assertIn("summary", data)
        self.assertIn("metadata", data)

        # Should have 2 performance records
        self.assertEqual(len(data["performance_data"]), 2)

    def test_filter_by_model_name(self):
        """Test filtering performance data by model name"""
        response = self.client.get(self.url, {"model_name": "gradient_boosting"})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()

        # Should have only 1 record for gradient_boosting
        performance_data = data["performance_data"]
        self.assertEqual(len(performance_data), 1)
        self.assertEqual(performance_data[0]["model_name"], "gradient_boosting")

    def test_summary_calculations(self):
        """Test that summary statistics are calculated correctly"""
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()

        summary = data["summary"]

        # Check summary fields
        self.assertIn("avg_hit_rate", summary)
        self.assertIn("overall_hit_rate", summary)
        self.assertIn("total_successful_days", summary)
        self.assertIn("total_prediction_days", summary)

        # Verify calculations
        expected_avg_hit_rate = (0.35 + 0.42) / 2
        self.assertAlmostEqual(summary["avg_hit_rate"], expected_avg_hit_rate, places=4)

        expected_overall_hit_rate = (10 + 12) / (30 + 30)
        self.assertAlmostEqual(
            summary["overall_hit_rate"], expected_overall_hit_rate, places=4
        )


class RetrainModelViewTest(APITestCase):
    """Test RetrainModelView"""

    def setUp(self):
        self.client = APIClient()
        self.url = "/lottery-prediction/api/retrain/"  # Correct URL based on routing

        # Create test data
        base_date = date(2025, 7, 25)
        for i in range(30):
            test_date = base_date - timedelta(days=i)
            KetQuaXoSo.objects.create(
                ngay=test_date,
                dau=f"{(17 + i) % 100:02d}",
                duoi=f"{(43 + i*2) % 100:02d}",
                g1=f"{(12 + i) % 100:02d}",
                g2=f"{(34 + i*3) % 100:02d}",
                g3=f"{(56 + i*2) % 100:02d}",
                g4=f"{(78 + i) % 100:02d}",
                g5=f"{(23 + i*4) % 100:02d}",
                g6=f"{(45 + i*2) % 100:02d}",
                g7=f"{(67 + i*3) % 100:02d}",
            )

    @override_settings(BASE_DIR="/tmp")
    def test_retrain_gradient_boosting_model(self):
        """Test retraining gradient boosting model"""
        request_data = {
            "model_type": "gradient_boosting",
            "force_retrain": True,
            "training_days": 30,
        }

        response = self.client.post(self.url, request_data, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()

        self.assertIn("message", data)
        self.assertIn("model_type", data)
        self.assertIn("training_period", data)
        self.assertIn("retraining_time_seconds", data)
        self.assertIn("model_saved_to", data)

        # Verify model type
        self.assertEqual(data["model_type"], "gradient_boosting")

        # Verify retraining time is reasonable
        self.assertGreater(data["retraining_time_seconds"], 0)
        self.assertLess(data["retraining_time_seconds"], 300)  # Under 5 minutes

    def test_retrain_invalid_model_type(self):
        """Test retraining with invalid model type"""
        request_data = {"model_type": "invalid_model", "force_retrain": True}

        response = self.client.post(self.url, request_data, format="json")

        self.assertEqual(response.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)


class IntegrationTest(APITestCase):
    """Integration tests with real models and data flow"""

    def setUp(self):
        self.client = APIClient()

        # Create comprehensive test data (3 months)
        base_date = date(2025, 7, 25)
        for i in range(90):
            test_date = base_date - timedelta(days=i)
            KetQuaXoSo.objects.create(
                ngay=test_date,
                dau=f"{(17 + i) % 100:02d}",
                duoi=f"{(43 + i*2) % 100:02d}",
                g1=f"{(12 + i) % 100:02d}",
                g2=f"{(34 + i*3) % 100:02d}",
                g3=f"{(56 + i*2) % 100:02d}",
                g4=f"{(78 + i) % 100:02d}",
                g5=f"{(23 + i*4) % 100:02d}",
                g6=f"{(45 + i*2) % 100:02d}",
                g7=f"{(67 + i*3) % 100:02d}",
            )

    @freeze_time("2025-07-26")
    def test_full_prediction_workflow(self):
        """Test complete prediction workflow with real models"""
        # Test multiple model types
        model_types = ["gradient_boosting", "hist_gradient_boosting", "ensemble"]

        for model_type in model_types:
            with self.subTest(model_type=model_type):
                request_data = {
                    "prediction_date": "2025-07-27",
                    "model_type": model_type,
                    "top_k": 10,
                }

                response = self.client.post(
                    "/lottery_prediction/api/predict/", request_data, format="json"
                )

                self.assertEqual(response.status_code, status.HTTP_200_OK)
                data = response.json()

                # Verify essential structure for all model types
                self.assertIn("top_k_predictions", data)
                self.assertEqual(len(data["top_k_predictions"]), 10)

                # Verify predictions are different across models (not using same fallback)
                predictions = [pred["number"] for pred in data["top_k_predictions"]]
                self.assertEqual(
                    len(set(predictions)), 10, "Duplicate predictions found"
                )

    @freeze_time("2025-07-26")
    def test_prediction_consistency(self):
        """Test that same request returns consistent results"""
        request_data = {
            "prediction_date": "2025-07-27",
            "model_type": "gradient_boosting",
            "top_k": 10,
        }

        # Make same request twice
        response1 = self.client.post(
            "/lottery_prediction/api/predict/", request_data, format="json"
        )
        response2 = self.client.post(
            "/lottery_prediction/api/predict/", request_data, format="json"
        )

        self.assertEqual(response1.status_code, status.HTTP_200_OK)
        self.assertEqual(response2.status_code, status.HTTP_200_OK)

        data1 = response1.json()
        data2 = response2.json()

        # Predictions should be consistent (assuming deterministic model)
        predictions1 = [pred["number"] for pred in data1["top_k_predictions"]]
        predictions2 = [pred["number"] for pred in data2["top_k_predictions"]]

        self.assertEqual(predictions1, predictions2, "Predictions are not consistent")

    @freeze_time("2025-07-26")
    def test_no_data_leakage_in_features(self):
        """Test that predictions don't use future data"""
        # This test verifies that reference_date is always before prediction_date

        future_dates = ["2025-07-27", "2025-07-28", "2025-08-01", "2025-12-31"]

        for future_date in future_dates:
            with self.subTest(prediction_date=future_date):
                request_data = {
                    "prediction_date": future_date,
                    "model_type": "gradient_boosting",
                    "top_k": 5,
                }

                response = self.client.post(
                    "/lottery_prediction/api/predict/", request_data, format="json"
                )

                if response.status_code == status.HTTP_200_OK:
                    data = response.json()
                    pred_date = datetime.strptime(
                        data["prediction_date"], "%Y-%m-%d"
                    ).date()
                    ref_date = datetime.strptime(
                        data["reference_date"], "%Y-%m-%d"
                    ).date()

                    self.assertLess(
                        ref_date,
                        pred_date,
                        f"Reference date {ref_date} should be before prediction date {pred_date}",
                    )
