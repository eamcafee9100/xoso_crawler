# conftest.py
import os
from datetime import date, timedelta

import django
import pytest
from django.conf import settings
from django.test.utils import get_runner

# Configure Django before importing models
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "xoso_crawler.settings")
django.setup()

# Now import models
from results.models import KetQuaXoSo


def pytest_configure(config):
    """Configure Django settings for pytest"""
    pass  # Already configured above


@pytest.fixture
def create_historical_data():
    """Create realistic historical lottery data for testing"""

    def _create_data(days=100, end_date=None):
        if end_date is None:
            end_date = date.today() - timedelta(days=1)

        created_objects = []
        for i in range(days):
            test_date = end_date - timedelta(days=i)

            # Generate realistic lottery numbers with variation
            base_num = (i * 13) % 100
            numbers = []
            for j in range(27):  # Total numbers needed
                num = (base_num + j * 7 + i * 3) % 100
                numbers.append(f"{num:02d}")

            obj = KetQuaXoSo.objects.create(
                thu=f"Thứ {((i % 7) + 2) if (i % 7) + 2 <= 8 else 2}",
                ngay=test_date,
                giai_db=f"{numbers[0]}{numbers[1]}{numbers[2]}{numbers[3]}{numbers[4]}",
                giai_1=f"{numbers[5]}{numbers[6]}{numbers[7]}{numbers[8]}{numbers[9]}",
                giai_2=f"{numbers[10]}{numbers[11]}{numbers[12]}{numbers[13]}{numbers[14]},{numbers[15]}{numbers[16]}{numbers[17]}{numbers[18]}{numbers[19]}",
                giai_3=f"{numbers[20]}{numbers[21]}{numbers[22]}{numbers[23]}{numbers[24]},{numbers[25]}{numbers[26]}{numbers[0]}{numbers[1]}{numbers[2]},{numbers[3]}{numbers[4]}{numbers[5]}{numbers[6]}{numbers[7]},{numbers[8]}{numbers[9]}{numbers[10]}{numbers[11]}{numbers[12]},{numbers[13]}{numbers[14]}{numbers[15]}{numbers[16]}{numbers[17]},{numbers[18]}{numbers[19]}{numbers[20]}{numbers[21]}{numbers[22]}",
                giai_4=f"{numbers[23]}{numbers[24]}{numbers[25]}{numbers[26]},{numbers[0]}{numbers[1]}{numbers[2]}{numbers[3]},{numbers[4]}{numbers[5]}{numbers[6]}{numbers[7]},{numbers[8]}{numbers[9]}{numbers[10]}{numbers[11]}",
                giai_5=f"{numbers[12]}{numbers[13]}{numbers[14]},{numbers[15]}{numbers[16]}{numbers[17]},{numbers[18]}{numbers[19]}{numbers[20]},{numbers[21]}{numbers[22]}{numbers[23]},{numbers[24]}{numbers[25]}{numbers[26]},{numbers[0]}{numbers[1]}{numbers[2]}",
                giai_6=f"{numbers[3]}{numbers[4]},{numbers[5]}{numbers[6]},{numbers[7]}{numbers[8]}",
                giai_7=f"{numbers[9]},{numbers[10]},{numbers[11]},{numbers[12]}",
            )
            created_objects.append(obj)

        return created_objects

    return _create_data


@pytest.fixture
def cleanup_test_data():
    """Clean up test data after tests"""
    yield
    # Clean up after test
    KetQuaXoSo.objects.all().delete()
