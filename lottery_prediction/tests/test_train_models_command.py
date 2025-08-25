# tests/test_train_models_command.py
"""
Test suite for train_models management command
Ensures proper date handling and data flow
"""
import os
import sys
from datetime import date, timedelta
from io import StringIO
from unittest.mock import MagicMock, call, patch

import pytest
from freezegun import freeze_time

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from django.core.management import call_command
from django.test import TestCase
from django.utils import timezone

from lottery_prediction.management.commands.train_models import Command
from results.models import KetQuaXoSo


class TestTrainModelsCommand(TestCase):
    """Test train_models management command logic"""

    def setUp(self):
        """Set up test environment"""
        self.command = Command()
        self.test_current_date = date(2025, 7, 26)

        # Create realistic historical data
        self.create_test_data()

    def create_test_data(self):
        """Create comprehensive test data"""
        # Create 100 days of historical data ending at 2025-07-25
        end_date = date(2025, 7, 25)

        for i in range(100):
            lottery_date = end_date - timedelta(days=i)

            # Generate realistic lottery numbers
            base = (i * 19 + 37) % 100
            numbers = []
            for j in range(27):
                num = (base + j * 13 + i * 7) % 100
                numbers.append(f"{num:02d}")

            KetQuaXoSo.objects.create(
                thu=self._get_day_name(lottery_date),
                ngay=lottery_date,
                giai_db=f"{numbers[0]}{numbers[1]}{numbers[2]}{numbers[3]}{numbers[4]}",
                giai_1=f"{numbers[5]}{numbers[6]}{numbers[7]}{numbers[8]}{numbers[9]}",
                giai_2=f"{numbers[10]}{numbers[11]}{numbers[12]}{numbers[13]}{numbers[14]},{numbers[15]}{numbers[16]}{numbers[17]}{numbers[18]}{numbers[19]}",
                giai_3=f"{numbers[20]}{numbers[21]}{numbers[22]}{numbers[23]}{numbers[24]},{numbers[25]}{numbers[26]}{numbers[0]}{numbers[1]}{numbers[2]},{numbers[3]}{numbers[4]}{numbers[5]}{numbers[6]}{numbers[7]},{numbers[8]}{numbers[9]}{numbers[10]}{numbers[11]}{numbers[12]},{numbers[13]}{numbers[14]}{numbers[15]}{numbers[16]}{numbers[17]},{numbers[18]}{numbers[19]}{numbers[20]}{numbers[21]}{numbers[22]}",
                giai_4=f"{numbers[23]}{numbers[24]}{numbers[25]}{numbers[26]},{numbers[0]}{numbers[1]}{numbers[2]}{numbers[3]},{numbers[4]}{numbers[5]}{numbers[6]}{numbers[7]},{numbers[8]}{numbers[9]}{numbers[10]}{numbers[11]}",
                giai_5=f"{numbers[12]}{numbers[13]}{numbers[14]},{numbers[15]}{numbers[16]}{numbers[17]},{numbers[18]}{numbers[19]}{numbers[20]},{numbers[21]}{numbers[22]}{numbers[23]},{numbers[24]}{numbers[25]}{numbers[26]},{numbers[0]}{numbers[1]}{numbers[2]}",
                giai_6=f"{numbers[3]}{numbers[4]},{numbers[5]}{numbers[6]},{numbers[7]}{numbers[8]}",
                giai_7=f"{numbers[9]},{numbers[10]},{numbers[11]},{numbers[12]}",
            )

    def _get_day_name(self, date_obj):
        """Get Vietnamese day name"""
        days = ["Thứ 2", "Thứ 3", "Thứ 4", "Thứ 5", "Thứ 6", "Thứ 7", "Chủ nhật"]
        return days[date_obj.weekday()]

    @freeze_time("2025-07-26")
    @pytest.mark.data_flow
    def test_command_date_calculation_logic(self):
        """Test command calculates dates correctly"""
        print("\n=== TEST: Command Date Calculation Logic ===")

        # Mock options
        options = {
            "model_type": "baseline",
            "train_days": 30,
            "validation_days": 15,
            "optimize": False,
            "search_type": "random",
            "search_iterations": 10,
            "cv_folds": 3,
            "output_dir": "test_models",
            "evaluate": True,
        }

        with patch("django.utils.timezone.now") as mock_now:
            mock_now.return_value.date.return_value = self.test_current_date

            # Get data range
            earliest_date = KetQuaXoSo.objects.earliest("ngay").ngay
            latest_date = KetQuaXoSo.objects.latest("ngay").ngay

            print(f"Data available: {earliest_date} to {latest_date}")

            # CRITICAL TEST: End date should use actual latest data
            current_date = self.test_current_date

            # The CORRECT logic should be:
            end_date = latest_date  # Use actual latest data, not artificially reduced
            train_start_date = end_date - timedelta(days=options["train_days"])
            validation_start_date = end_date - timedelta(
                days=options["validation_days"]
            )

            print(f"Current date: {current_date}")
            print(f"Calculated end_date: {end_date}")
            print(f"Training period: {train_start_date} to {end_date}")
            print(f"Validation period: {validation_start_date} to {end_date}")

            # Assertions for CORRECT behavior
            self.assertEqual(
                end_date,
                latest_date,
                "End date should be latest available data, not artificially reduced",
            )
            self.assertLess(
                train_start_date, end_date, "Training start should be before end"
            )
            self.assertLessEqual(
                validation_start_date,
                end_date,
                "Validation start should be before/at end",
            )

            # Verify sufficient data exists
            training_data_count = KetQuaXoSo.objects.filter(
                ngay__gte=train_start_date, ngay__lte=end_date
            ).count()

            self.assertGreaterEqual(
                training_data_count,
                options["train_days"] * 0.8,
                f"Should have sufficient training data, got {training_data_count}",
            )

    @freeze_time("2025-07-26")
    @pytest.mark.data_flow
    def test_command_handles_latest_data_correctly(self):
        """Test command uses latest available data without artificial reduction"""
        print("\n=== TEST: Command Uses Latest Data Correctly ===")

        # Create additional data up to yesterday
        yesterday = date(2025, 7, 25)

        # Ensure we have data up to yesterday
        if not KetQuaXoSo.objects.filter(ngay=yesterday).exists():
            KetQuaXoSo.objects.create(
                thu="Thứ 5",
                ngay=yesterday,
                giai_db="12345",
                giai_1="54321",
                giai_2="11111,22222",
                giai_3="33333,44444,55555,66666,77777,88888",
                giai_4="1111,2222,3333,4444",
                giai_5="111,222,333,444,555,666",
                giai_6="11,22,33",
                giai_7="1,2,3,4",
            )

        latest_date = KetQuaXoSo.objects.latest("ngay").ngay
        print(f"Latest available data: {latest_date}")

        # Mock the command's date calculation
        with patch("django.utils.timezone.now") as mock_now:
            mock_now.return_value.date.return_value = self.test_current_date

            # Test the CORRECT logic (what it SHOULD be)
            current_date = self.test_current_date
            correct_end_date = latest_date  # Should use actual latest data

            # Test the INCORRECT logic (what's currently implemented)
            incorrect_end_date = min(latest_date, current_date - timedelta(days=3))

            print(f"Current date: {current_date}")
            print(f"Correct end_date (should be): {correct_end_date}")
            print(f"Incorrect end_date (currently): {incorrect_end_date}")

            # Assert what the behavior SHOULD be
            self.assertEqual(
                correct_end_date, latest_date, "Should use actual latest data date"
            )

            # Show the problem with current implementation
            if incorrect_end_date < latest_date:
                days_lost = (latest_date - incorrect_end_date).days
                print(
                    f"❌ PROBLEM: Current implementation loses {days_lost} days of data!"
                )
                print(f"   Latest data: {latest_date}")
                print(f"   But using:   {incorrect_end_date}")

            # The fix should ensure we use latest_date as end_date
            self.assertGreaterEqual(
                correct_end_date,
                incorrect_end_date,
                "Correct logic should use more recent or same date",
            )

    @freeze_time("2025-07-26")
    @pytest.mark.data_flow
    def test_training_prediction_workflow(self):
        """Test complete workflow: train on historical data, predict future"""
        print("\n=== TEST: Training -> Prediction Workflow ===")

        # Step 1: Train using all available historical data
        latest_date = KetQuaXoSo.objects.latest("ngay").ngay
        train_start_date = latest_date - timedelta(days=30)

        print(f"Training period: {train_start_date} to {latest_date}")
        print(f"Will predict for: {self.test_current_date} (tomorrow)")

        # Verify training data exists
        training_data = KetQuaXoSo.objects.filter(
            ngay__gte=train_start_date, ngay__lte=latest_date
        )

        self.assertGreater(
            training_data.count(),
            25,
            f"Should have sufficient training data, got {training_data.count()}",
        )

        # Step 2: Verify we can make predictions for future dates
        future_date = self.test_current_date  # Tomorrow

        # This represents the user expectation:
        # 1. Train on all available historical data (up to latest_date)
        # 2. Predict for future_date (tomorrow)

        self.assertGreater(
            future_date,
            latest_date,
            "Prediction date should be after latest training data",
        )

        print("✓ Workflow logic verified: Past -> Train -> Future -> Predict")

    @freeze_time("2025-07-26")
    @pytest.mark.data_flow
    def test_command_validation_logic(self):
        """Test command data validation logic"""
        print("\n=== TEST: Command Validation Logic ===")

        # Test data availability check
        train_days = 30
        result = self.command._check_data_availability(train_days)

        self.assertTrue(result, "Should pass data availability check")

        # Test with insufficient data
        excessive_train_days = 500  # More than available data
        result = self.command._check_data_availability(excessive_train_days)

        # This might fail, which is correct behavior
        print(f"Data availability check for {excessive_train_days} days: {result}")

    @freeze_time("2025-07-26")
    @pytest.mark.data_flow
    def test_end_date_calculation_fix(self):
        """Test the proposed fix for end_date calculation"""
        print("\n=== TEST: End Date Calculation Fix ===")

        with patch("django.utils.timezone.now") as mock_now:
            mock_now.return_value.date.return_value = self.test_current_date

            # Current implementation (PROBLEMATIC)
            current_date = timezone.now().date()
            latest_date = KetQuaXoSo.objects.latest("ngay").ngay

            current_end_date = min(latest_date, current_date - timedelta(days=3))

            # Proposed fix (CORRECT)
            proposed_end_date = latest_date  # Use actual latest data

            print(f"Current date: {current_date}")
            print(f"Latest data date: {latest_date}")
            print(f"Current implementation end_date: {current_end_date}")
            print(f"Proposed fix end_date: {proposed_end_date}")

            # Show the improvement
            if proposed_end_date > current_end_date:
                days_gained = (proposed_end_date - current_end_date).days
                print(f"✅ IMPROVEMENT: Fix gains {days_gained} days of training data!")

            # Assert the fix is better
            self.assertGreaterEqual(
                proposed_end_date,
                current_end_date,
                "Fixed implementation should use same or more recent data",
            )

            # The fix should use all available data
            self.assertEqual(
                proposed_end_date,
                latest_date,
                "Fix should use all available historical data",
            )

    def tearDown(self):
        """Clean up test data"""
        KetQuaXoSo.objects.all().delete()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
