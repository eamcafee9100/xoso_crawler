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


class Btl_SC_CN_01LotoMethod(BasePredictionMethod, BaseMakeResult):
    def get_code(self):
        return "btl_sc_CN_01"

    def get_name(self):
        return "SC_CN 01"

    def get_description(self):
        return "Tổng từ giải 2.2.4 và giải 3.1.5"

    def calculate(self, data):
        return self._make_result(
            data,
            [("giai_2_2", 3)],
            [("giai_3_1", 4)],
            reverse=True,
        )


class Btl_SC_CN_02LotoMethod(BasePredictionMethod, BaseMakeResult):
    def get_code(self):
        return "btl_sc_CN_02"

    def get_name(self):
        return "SC_CN 02"

    def get_description(self):
        return "Tổng từ giải 5.3.2 và giải 6.2.3"

    def calculate(self, data):
        return self._make_result(
            data,
            [("giai_5_3", 1)],
            [("giai_6_2", 2)],
            reverse=True,
        )


class Btl_SC_CN_03LotoMethod(BasePredictionMethod, BaseMakeResult):
    def get_code(self):
        return "btl_sc_CN_03"

    def get_name(self):
        return "SC_CN 03"

    def get_description(self):
        return "Tổng từ giải 1.1.2 và giải 6.2.3"

    def calculate(self, data):
        return self._make_result(
            data,
            [("giai_1_1", 1)],
            [("giai_6_2", 2)],
            reverse=True,
        )


class Btl_SC_CN_04LotoMethod(BasePredictionMethod, BaseMakeResult):
    def get_code(self):
        return "btl_sc_CN_04"

    def get_name(self):
        return "SC_CN 04 (kn3)"

    def get_description(self):
        return "Tổng từ giải 4.3.2 và giải 5.3.3"

    def calculate(self, data):
        return self._make_result(
            data,
            [("giai_4_3", 1)],
            [("giai_5_3", 2)],
            reverse=True,
        )


class Btl_SC_CN_05LotoMethod(BasePredictionMethod, BaseMakeResult):
    def get_code(self):
        return "btl_sc_CN_05"

    def get_name(self):
        return "SC_CN 05"

    def get_description(self):
        return "Tổng từ giải 5.2.1 và giải 6.1.1"

    def calculate(self, data):
        return self._make_result(
            data,
            [("giai_5_2", 0)],
            [("giai_6_1", 0)],
            reverse=True,
        )
