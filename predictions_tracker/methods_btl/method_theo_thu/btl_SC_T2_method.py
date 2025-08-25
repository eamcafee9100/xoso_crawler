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


class Btl_SC_T2_01LotoMethod(BasePredictionMethod, BaseMakeResult):
    def get_code(self):
        return "btl_sc_T2_01"

    def get_name(self):
        return "SC_T2 01"

    def get_description(self):
        return "Tổng từ giải 4.4.4 và giải 6.3.1"

    def calculate(self, data):
        return self._make_result(
            data,
            [("giai_4_4", 3)],
            [("giai_6_3", 0)],
            reverse=True,
        )


class Btl_SC_T2_02LotoMethod(BasePredictionMethod, BaseMakeResult):
    def get_code(self):
        return "btl_sc_T2_02"

    def get_name(self):
        return "SC_T2 02"

    def get_description(self):
        return "Tổng từ giải 5.5.2 và giải 5.6.3"

    def calculate(self, data):
        return self._make_result(
            data,
            [("giai_5_5", 1)],
            [("giai_5_6", 2)],
            reverse=True,
        )


class Btl_SC_T2_03LotoMethod(BasePredictionMethod, BaseMakeResult):
    def get_code(self):
        return "btl_sc_T2_03"

    def get_name(self):
        return "SC_T2 03"

    def get_description(self):
        return "Tổng từ giải 2.2.3 và giải 3.3.4"

    def calculate(self, data):
        return self._make_result(
            data,
            [("giai_2_2", 2)],
            [("giai_3_4", 3)],
            reverse=True,
        )


class Btl_SC_T2_04LotoMethod(BasePredictionMethod, BaseMakeResult):
    def get_code(self):
        return "btl_sc_T2_04"

    def get_name(self):
        return "SC_T2 04 (kn3)"

    def get_description(self):
        return "Tổng từ giải giai_db.4 và giải 5.1.4"

    def calculate(self, data):
        return self._make_result(
            data,
            [("giai_db", 3)],
            [("giai_5_1", 3)],
            reverse=True,
        )

class Btl_SC_T2_05LotoMethod(BasePredictionMethod, BaseMakeResult):
    def get_code(self):
        return "btl_sc_T2_05"

    def get_name(self):
        return "SC_T2 05"

    def get_description(self):
        return "Tổng từ giải giai_db.4 và giải 5.5.1"

    def calculate(self, data):
        return self._make_result(
            data,
            [("giai_db", 3)],
            [("giai_5_5", 0)],
            reverse=True,
        )