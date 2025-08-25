# tests/test_data_quality.py
from django.test import TestCase
from django.core.exceptions import ValidationError
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
class TestDataQuality(TestCase):
    def test_lottery_result_validation(self):
        """Test lottery result data validation"""
        # Test valid data
        valid_result = KetQuaXoSo(
            thu="Thứ 2",
            ngay=date(2025, 7, 21),
            giai_db="12345",
            giai_1="54321",
            giai_2="11111,22222",
            giai_3="33333,44444,55555,66666,77777,88888",
            giai_4="1111,2222,3333,4444",
            giai_5="111,222,333,444,555,666",
            giai_6="11,22,33",
            giai_7="1,2,3,4"
        )
        
        try:
            valid_result.full_clean()
        except ValidationError:
            self.fail("Valid lottery result should pass validation")

    def test_duplicate_date_prevention(self):
        """Test system prevents duplicate dates"""
        test_date = date(2025, 7, 21)
        
        # Create first result
        KetQuaXoSo.objects.create(
            thu="Thứ 2", ngay=test_date,
            giai_db="12345", giai_1="54321", giai_2="11111,22222",
            giai_3="33333,44444,55555,66666,77777,88888",
            giai_4="1111,2222,3333,4444", giai_5="111,222,333,444,555,666",
            giai_6="11,22,33", giai_7="1,2,3,4"
        )
        
        # Try to create duplicate
        with self.assertRaises(Exception):  # Should raise IntegrityError
            KetQuaXoSo.objects.create(
                thu="Thứ 3", ngay=test_date,  # Same date, different day
                giai_db="54321", giai_1="12345", giai_2="22222,11111",
                giai_3="44444,33333,66666,55555,88888,77777",
                giai_4="2222,1111,4444,3333", giai_5="222,111,444,333,666,555",
                giai_6="22,11,44", giai_7="2,1,4,3"
            )

    def test_number_extraction_accuracy(self):
        """Test accuracy of 2-digit number extraction"""
        result = KetQuaXoSo.objects.create(
            thu="Thứ 2", ngay=date(2025, 7, 21),
            giai_db="12345",  # Should extract: 45
            giai_1="54321",   # Should extract: 21
            giai_2="11111,22222",  # Should extract: 11, 22
            giai_3="33333,44444,55555,66666,77777,88888",  # Should extract: 33, 44, 55, 66, 77, 88
            giai_4="1111,2222,3333,4444",  # Should extract: 11, 22, 33, 44
            giai_5="111,222,333,444,555,666",  # Should extract: 11, 22, 33, 44, 55, 66
            giai_6="11,22,33",  # Should extract: 11, 22, 33
            giai_7="1,2,3,4"  # Should extract: 01, 02, 03, 04
        )
        
        extracted_numbers = result.get_all_2digit_numbers()
        expected_numbers = {
            '45', '21', '11', '22', '33', '44', '55', '66', '77', '88', '01', '02', '03', '04'
        }
        
        self.assertEqual(extracted_numbers, expected_numbers)


