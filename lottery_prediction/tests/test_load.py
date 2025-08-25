# tests/test_load.py
import concurrent.futures

# tests/test_features.py
import unittest
from datetime import date, timedelta
from unittest.mock import MagicMock, patch

import numpy as np
import pandas as pd
import requests
from django.test import LiveServerTestCase, TestCase
from django.utils import timezone

from lottery_prediction.ml.features.extractors import LotteryFeatureExtractor
from lottery_prediction.ml.features.validators import DataLeakageValidator
from results.models import KetQuaXoSo

# ===== 1. UNIT TESTS =====


class TestLoadPerformance(LiveServerTestCase):
    def test_concurrent_prediction_requests(self):
        """Test system handles concurrent requests"""

        def make_request(i):
            try:
                response = requests.get(
                    f"{self.live_server_url}/api/predict/",
                    params={"prediction_date": date.today() + timedelta(days=i)},
                    timeout=30,
                )
                return response.status_code
            except Exception as e:
                return str(e)

        # Test with 20 concurrent requests
        with concurrent.futures.ThreadPoolExecutor(max_workers=20) as executor:
            futures = [executor.submit(make_request, i) for i in range(20)]
            results = [
                future.result() for future in concurrent.futures.as_completed(futures)
            ]

        # All requests should succeed
        success_count = sum(1 for result in results if result == 200)
        self.assertGreater
