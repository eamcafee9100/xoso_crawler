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


class Btl_SC_T4_01LotoMethod(BasePredictionMethod, BaseMakeResult):
    def get_code(self):
        return "btl_sc_T4_01"

    def get_name(self):
        return "SC_T4 01"

    def get_description(self):
        return "Tổng từ giải giai_db.3 và giải 7.3.2"

    def calculate(self, data):
        return self._make_result(
            data,
            [("giai_db", 2)],
            [("giai_7_3", 1)],
            reverse=True,
        )


class Btl_SC_T4_02LotoMethod(BasePredictionMethod, BaseMakeResult):
    def get_code(self):
        return "btl_sc_T4_02"

    def get_name(self):
        return "SC_T4 02"

    def get_description(self):
        return "Tổng từ giải 2.1.1 và giải 7.4.1"

    def calculate(self, data):
        return self._make_result(
            data,
            [("giai_2_1", 0)],
            [("giai_7_4", 0)],
            reverse=True,
        )


class Btl_SC_T4_03LotoMethod(BasePredictionMethod, BaseMakeResult):
    def get_code(self):
        return "btl_sc_T4_03"

    def get_name(self):
        return "SC_T4 03"

    def get_description(self):
        return "Tổng từ giải 3.2.2 và giải 7.3.2"

    def calculate(self, data):
        return self._make_result(
            data,
            [("giai_3_2", 1)],
            [("giai_7_3", 1)],
            reverse=True,
        )


class Btl_SC_T4_04LotoMethod(BasePredictionMethod, BaseMakeResult):
    def get_code(self):
        return "btl_sc_T4_04"

    def get_name(self):
        return "SC_T4 04 (kn3)"

    def get_description(self):
        return "Tổng từ giải giai_db.3 và giải 3.2.3"

    def calculate(self, data):
        return self._make_result(
            data,
            [("giai_db", 2)],
            [("giai_3_2", 2)],
            reverse=True,
        )

class Btl_SC_T4_05LotoMethod(BasePredictionMethod, BaseMakeResult):
    def get_code(self):
        return "btl_sc_T4_05"

    def get_name(self):
        return "SC_T4 05"

    def get_description(self):
        return "Tổng từ giải 7.3.1 và giải 7.3.2"

    def calculate(self, data):
        return self._make_result(
            data,
            [("giai_7_3", 0)],
            [("giai_7_3", 1)],
            reverse=True,
        )