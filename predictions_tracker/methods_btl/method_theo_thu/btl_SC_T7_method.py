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


class Btl_SC_T7_01LotoMethod(BasePredictionMethod, BaseMakeResult):
    def get_code(self):
        return "btl_sc_T7_01"

    def get_name(self):
        return "SC_T7 01"

    def get_description(self):
        return "Tổng từ giải 3.3.3 và giải 3.4.3"

    def calculate(self, data):
        return self._make_result(
            data,
            [("giai_3_3", 2)],
            [("giai_3_4", 2)],
            reverse=True,
        )


class Btl_SC_T7_02LotoMethod(BasePredictionMethod, BaseMakeResult):
    def get_code(self):
        return "btl_sc_T7_02"

    def get_name(self):
        return "SC_T7 02"

    def get_description(self):
        return "Tổng từ giải 2.1.2 và giải 3.4.3"

    def calculate(self, data):
        return self._make_result(
            data,
            [("giai_2_1", 1)],
            [("giai_3_4", 2)],
            reverse=True,
        )


class Btl_SC_T7_03LotoMethod(BasePredictionMethod, BaseMakeResult):
    def get_code(self):
        return "btl_sc_T7_03"

    def get_name(self):
        return "SC_T7 03"

    def get_description(self):
        return "Tổng từ giải 3.4.3 và giải 5.2.3"

    def calculate(self, data):
        return self._make_result(
            data,
            [("giai_3_4", 2)],
            [("giai_5_2", 2)],
            reverse=True,
        )


class Btl_SC_T7_04LotoMethod(BasePredictionMethod, BaseMakeResult):
    def get_code(self):
        return "btl_sc_T7_04"

    def get_name(self):
        return "SC_T7 04 (kn3)"

    def get_description(self):
        return "Tổng từ giải giai_db.3 và giải 2.1.2"

    def calculate(self, data):
        return self._make_result(
            data,
            [("giai_db", 2)],
            [("giai_2_1", 1)],
            reverse=True,
        )

class Btl_SC_T7_05LotoMethod(BasePredictionMethod, BaseMakeResult):
    def get_code(self):
        return "btl_sc_T7_05"

    def get_name(self):
        return "SC_T7 05"

    def get_description(self):
        return "Tổng từ giải giai_db.4 và giải 3.2.5"

    def calculate(self, data):
        return self._make_result(
            data,
            [("giai_db", 3)],
            [("giai_3_2", 4)],
            reverse=True,
        )