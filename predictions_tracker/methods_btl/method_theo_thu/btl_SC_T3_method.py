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


class Btl_SC_T3_01LotoMethod(BasePredictionMethod, BaseMakeResult):
    def get_code(self):
        return "btl_sc_T3_01"

    def get_name(self):
        return "SC_T3 01"

    def get_description(self):
        return "Tổng từ giải 5.6.4 và giải 6.3.1"

    def calculate(self, data):
        return self._make_result(
            data,
            [("giai_5_6", 3)],
            [("giai_6_3", 0)],
            reverse=True,
        )


class Btl_SC_T3_02LotoMethod(BasePredictionMethod, BaseMakeResult):
    def get_code(self):
        return "btl_sc_T3_02"

    def get_name(self):
        return "SC_T3 02"

    def get_description(self):
        return "Tổng từ giải 3.1.5 và giải 4.2.2"

    def calculate(self, data):
        return self._make_result(
            data,
            [("giai_3_1", 4)],
            [("giai_4_2", 1)],
            reverse=True,
        )


class Btl_SC_T3_03LotoMethod(BasePredictionMethod, BaseMakeResult):
    def get_code(self):
        return "btl_sc_T3_03"

    def get_name(self):
        return "SC_T3 03"

    def get_description(self):
        return "Tổng từ giải 4.2.2 và giải 5.5.4"

    def calculate(self, data):
        return self._make_result(
            data,
            [("giai_4_2", 1)],
            [("giai_5_5", 3)],
            reverse=True,
        )


class Btl_SC_T3_04LotoMethod(BasePredictionMethod, BaseMakeResult):
    def get_code(self):
        return "btl_sc_T3_04"

    def get_name(self):
        return "SC_T3 04 (kn3)"

    def get_description(self):
        return "Tổng từ giải 4.4.2 và giải 6.1.3"

    def calculate(self, data):
        return self._make_result(
            data,
            [("giai_4_4", 1)],
            [("giai_6_1", 2)],
            reverse=True,
        )


class Btl_SC_T3_05LotoMethod(BasePredictionMethod, BaseMakeResult):
    def get_code(self):
        return "btl_sc_T3_05"

    def get_name(self):
        return "SC_T3 05"

    def get_description(self):
        return "Tổng từ giải 2.1.3 và giải 3.3.2"

    def calculate(self, data):
        return self._make_result(
            data,
            [("giai_2_1", 2)],
            [("giai_3_3", 1)],
            reverse=True,
        )
