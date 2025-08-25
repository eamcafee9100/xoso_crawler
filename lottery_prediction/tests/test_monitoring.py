# tests/test_monitoring.py
# ===== 1. UNIT TESTS =====

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
from results.models import KetQuaXoSo


class TestSystemMonitoring(TestCase):
    def test_model_performance_tracking(self):
        """Test model performance is properly tracked"""
        from lottery_prediction.services.performance_tracker import PerformanceTracker

        tracker = PerformanceTracker()

        # Simulate predictions and actual results
        predictions = ["12", "34", "56", "78", "90", "11", "33", "55", "77", "99"]
        actual_results = ["12", "34", "98", "76", "54", "32", "10", "88", "66", "44"]

        performance = tracker.calculate_performance(predictions, actual_results)

        # Should have 2 hits out of 10 = 20%
        self.assertEqual(performance["hit_count"], 2)
        self.assertEqual(performance["hit_rate"], 0.2)

    def test_alert_system(self):
        """Test alert system triggers correctly"""
        from lottery_prediction.services.alert_service import AlertService

        alert_service = AlertService()

        # Simulate performance degradation
        poor_performance = {
            "hit_rate": 0.1,  # 10% - below threshold
            "model_name": "TestModel",
            "date": date.today(),
        }

        alerts = alert_service.check_performance_alerts([poor_performance])

        self.assertGreater(len(alerts), 0)
        self.assertIn("performance_degradation", alerts[0]["type"])
