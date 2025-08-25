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


class Btl_SC_T5_01LotoMethod(BasePredictionMethod, BaseMakeResult):
    def get_code(self):
        return "btl_sc_T5_01"

    def get_name(self):
        return "SC_T5 01"

    def get_description(self):
        return "Tổng từ giải 3.5.2 và giải 4.1.1"

    def calculate(self, data):
        return self._make_result(
            data,
            [("giai_3_5", 1)],
            [("giai_4_1", 0)],
            reverse=True,
        )


class Btl_SC_T5_02LotoMethod(BasePredictionMethod, BaseMakeResult):
    def get_code(self):
        return "btl_sc_T5_02"

    def get_name(self):
        return "SC_T5 02"

    def get_description(self):
        return "Tổng từ giải 2.1.4 và giải 3.6.4"

    def calculate(self, data):
        return self._make_result(
            data,
            [("giai_2_1", 3)],
            [("giai_3_6", 3)],
            reverse=True,
        )


class Btl_SC_T5_03LotoMethod(BasePredictionMethod, BaseMakeResult):
    def get_code(self):
        return "btl_sc_T5_03"

    def get_name(self):
        return "SC_T5 03"

    def get_description(self):
        return "Tổng từ giải 1.1.1 và giải 3.2.4"

    def calculate(self, data):
        return self._make_result(
            data,
            [("giai_1_1", 0)],
            [("giai_3_2", 3)],
            reverse=True,
        )


class Btl_SC_T5_04LotoMethod(BasePredictionMethod, BaseMakeResult):
    def get_code(self):
        return "btl_sc_T5_04"

    def get_name(self):
        return "SC_T5 04 (kn3)"

    def get_description(self):
        return "Tổng từ giải 5.1.1 và giải 5.1.2"

    def calculate(self, data):
        return self._make_result(
            data,
            [("giai_5_1", 0)],
            [("giai_5_1", 1)],
            reverse=True,
        )


class Btl_SC_T5_05LotoMethod(BasePredictionMethod, BaseMakeResult):
    def get_code(self):
        return "btl_sc_T5_05"

    def get_name(self):
        return "SC_T5 05"

    def get_description(self):
        return "Tổng từ giải 3.3.5 và giải 4.4.1"

    def calculate(self, data):
        return self._make_result(
            data,
            [("giai_3_3", 4)],
            [("giai_4_4", 0)],
            reverse=True,
        )
