# ===== PHASE 2: TESTING & INTEGRATION SYSTEM =====

"""
Phase 2: Testing & Quality Assurance
Timeline: 7-10 ngày
- Unit Testing cho tất cả components
- Integration Testing cho end-to-end workflow  
- Performance Testing & Load Testing
- Data Quality & Model Drift Detection
"""

# ===== 1. UNIT TESTS =====

# tests/test_features.py
import unittest
from datetime import date, timedelta
from django.test import TestCase
from django.utils import timezone
from unittest.mock import patch, MagicMock
import numpy as np
import pandas as pd

from lottery_prediction.ml.features.extractors import LotteryFeatureExtractor
from lottery_prediction.ml.features.validators import DataLeakageValidator
from results.models import KetQuaXoSo

class TestLotteryFeatureExtractor(TestCase):
    def setUp(self):
        self.extractor = LotteryFea`tureExtractor()
        self.target_date = date(2025, 7, 25)
        
        # Create test data
        test_dates = [
            self.target_date - timedelta(days=i) 
            for i in range(1, 31)  # 30 days before target
        ]
        
        for i, test_date in enumerate(test_dates):
            KetQuaXoSo.objects.create(
                thu=f"Thứ {(i % 7) + 2}",
                ngay=test_date,
                giai_db="12345",
                giai_1="54321",
                giai_2="11111,22222",
                giai_3="33333,44444,55555,66666,77777,88888",
                giai_4="1111,2222,3333,4444",
                giai_5="111,222,333,444,555,666",
                giai_6="11,22,33",
                giai_7="1,2,3,4"
            )

    def test_frequency_features_extraction(self):
        """Test frequency features calculation"""
        features = self.extractor.extract_frequency_features(self.target_date)
        
        # Check structure
        self.assertIn('number_frequency_7d', features.columns)
        self.assertIn('number_frequency_30d', features.columns)
        self.assertEqual(len(features), 100)  # 00-99 numbers
        
        # Check data types
        self.assertTrue(features['number_frequency_7d'].dtype in [np.int64, np.float64])
        
        # Check no negative frequencies
        self.assertTrue((features['number_frequency_7d'] >= 0).all())

    def test_temporal_features_extraction(self):
        """Test temporal features calculation"""
        features = self.extractor.extract_temporal_features(self.target_date)
        
        # Check day of week features
        self.assertIn('is_monday', features)
        self.assertIn('is_friday', features)
        
        # Check values are binary
        day_features = [col for col in features.columns if col.startswith('is_')]
        for col in day_features:
            self.assertTrue(features[col].isin([0, 1]).all())

    def test_sequential_features_extraction(self):
        """Test sequential pattern features"""
        features = self.extractor.extract_sequential_features(self.target_date)
        
        self.assertIn('days_since_last_appearance', features.columns)
        self.assertIn('consecutive_miss_count', features.columns)
        
        # Check no infinite values
        self.assertFalse(np.isinf(features).any().any())

    def test_full_feature_extraction(self):
        """Test complete feature extraction pipeline"""
        features = self.extractor.extract_features_for_date(self.target_date)
        
        # Check output structure
        self.assertEqual(len(features), 100)  # 100 numbers (00-99)
        self.assertGreater(len(features.columns), 20)  # Many features
        
        # Check for NaN values
        nan_count = features.isnull().sum().sum()
        self.assertEqual(nan_count, 0, "Features should not contain NaN values")

    def test_feature_consistency(self):
        """Test feature consistency across multiple runs"""
        features1 = self.extractor.extract_features_for_date(self.target_date)
        features2 = self.extractor.extract_features_for_date(self.target_date)
        
        # Should be identical
        pd.testing.assert_frame_equal(features1, features2)

class TestDataLeakageValidator(TestCase):
    def setUp(self):
        self.validator = DataLeakageValidator()
        self.prediction_date = date(2025, 7, 25)

    def test_valid_date_range(self):
        """Test validation accepts valid date ranges"""
        valid_start = self.prediction_date - timedelta(days=30)
        valid_end = self.prediction_date - timedelta(days=1)
        
        result = self.validator.validate_date_range(
            valid_start, valid_end, self.prediction_date
        )
        self.assertTrue(result)

    def test_invalid_future_date(self):
        """Test validation rejects future dates"""
        invalid_start = self.prediction_date - timedelta(days=30)
        invalid_end = self.prediction_date + timedelta(days=1)  # Future date
        
        with self.assertRaises(ValueError):
            self.validator.validate_date_range(
                invalid_start, invalid_end, self.prediction_date
            )

    def test_queryset_validation(self):
        """Test queryset doesn't contain future data"""
        # Create test data including future date
        KetQuaXoSo.objects.create(
            thu="Thứ 2",
            ngay=self.prediction_date + timedelta(days=1),  # Future
            giai_db="12345", giai_1="54321", giai_2="11111,22222",
            giai_3="33333,44444,55555,66666,77777,88888",
            giai_4="1111,2222,3333,4444", giai_5="111,222,333,444,555,666",
            giai_6="11,22,33", giai_7="1,2,3,4"
        )
        
        queryset = KetQuaXoSo.objects.all()
        
        with self.assertRaises(ValueError):
            self.validator.validate_queryset(queryset, self.prediction_date)


