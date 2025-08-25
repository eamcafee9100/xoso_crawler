import os
import sys
from typing import Dict

# Add project root to Python path for imports
project_root = os.path.dirname(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
)
sys.path.insert(0, project_root)

# Set Django settings
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "xoso_crawler.settings")

import django

django.setup()

from predictions_tracker.methods_btl.base import BaseMakeResult, BasePredictionMethod
from results.models import KetQuaXoSo


class Btl_SC_T6_01LotoMethod(BasePredictionMethod, BaseMakeResult):
    def get_code(self):
        return "btl_sc_T6_01"

    def get_name(self):
        return "SC_T6 01"

    def get_description(self):
        return "Tổng từ giải 3.6.5 và giải 5.5.3"

    def calculate(self, data):
        return self._make_result(
            data,
            [("giai_3_6", 4)],
            [("giai_5_5", 2)],
            reverse=True,
        )


class Btl_SC_T6_02LotoMethod(BasePredictionMethod, BaseMakeResult):
    def get_code(self):
        return "btl_sc_T6_02"

    def get_name(self):
        return "SC_T6 02"

    def get_description(self):
        return "Tổng từ giải 3.4.2 và giải 4.3.1"

    def calculate(self, data):
        return self._make_result(
            data,
            [("giai_3_4", 1)],
            [("giai_4_3", 0)],
            reverse=True,
        )


class Btl_SC_T6_03LotoMethod(BasePredictionMethod, BaseMakeResult):
    def get_code(self):
        return "btl_sc_T6_03"

    def get_name(self):
        return "SC_T6 03"

    def get_description(self):
        return "Tổng từ giải 3.3.1 và giải 3.5.3"

    def calculate(self, data):
        return self._make_result(
            data,
            [("giai_3_3", 0)],
            [("giai_3_5", 2)],
            reverse=True,
        )


class Btl_SC_T6_04LotoMethod(BasePredictionMethod, BaseMakeResult):
    def get_code(self):
        return "btl_sc_T6_04"

    def get_name(self):
        return "SC_T6 04 (kn3)"

    def get_description(self):
        return "Tổng từ giải 2.2.4 và giải 3.1.3"

    def calculate(self, data):
        return self._make_result(
            data,
            [("giai_2_2", 3)],
            [("giai_3_1", 2)],
            reverse=True,
        )

