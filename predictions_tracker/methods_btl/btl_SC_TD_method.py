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


class Btl_SC_TD_01LotoMethod(BasePredictionMethod, BaseMakeResult):
    def get_code(self):
        return "btl_sc_TD_01"

    def get_name(self):
        return "SC_TD 01"

    def get_description(self):
        return "Tổng từ giải 2.2.2 + 5.1.4 + 5.2.4 và giải 1.1.5 + 5.5.2 + 5.6.4"

    def calculate(self, data):
        return self._make_result(
            data,
            [("giai_2_2", 1), ("giai_5_1", 3), ("giai_5_2", 3)],
            [("giai_1", 4), ("giai_5_5", 1), ("giai_5_6", 3)],
            reverse=True,
        )


class Btl_SC_TD_02LotoMethod(BasePredictionMethod, BaseMakeResult):
    def get_code(self):
        return "btl_sc_TD_02"

    def get_name(self):
        return "SC_TD 02"

    def get_description(self):
        return "Tổng từ giải 3.1.2 + 3.2.5 + 6.3.3 và giải 3.5.2 + 3.6.4 + 4.2.4"

    def calculate(self, data):
        return self._make_result(
            data,
            [("giai_3_1", 1), ("giai_3_2", 4), ("giai_6_3", 2)],
            [("giai_3_5", 1), ("giai_3_6", 3), ("giai_4_2", 3)],
            reverse=True,
        )


class Btl_SC_TD_03LotoMethod(BasePredictionMethod, BaseMakeResult):
    def get_code(self):
        return "btl_sc_TD_03"

    def get_name(self):
        return "SC_TD 03"

    def get_description(self):
        return "Tổng từ giải 5.1.3 + 5.2.4 + 5.6.4 và giải 6.1.1 + 5.5.2 + 5.6.4"

    def calculate(self, data):
        return self._make_result(
            data,
            [("giai_5_1", 2), ("giai_5_2", 3), ("giai_5_6", 3)],
            [("giai_6_1", 0), ("giai_5_5", 1), ("giai_5_6", 3)],
            reverse=True,
        )


class Btl_SC_TD_04LotoMethod(BasePredictionMethod, BaseMakeResult):
    def get_code(self):
        return "btl_sc_TD_04"

    def get_name(self):
        return "SC_TD 04 (kn3)"

    def get_description(self):
        return "Tổng từ giải 3.1.3 + 3.3.2 + 6.2.3 và giải 3.4.2 + 3.4.4 + 2.2.3"

    def calculate(self, data):
        return self._make_result(
            data,
            [("giai_3_1", 2), ("giai_3_3", 1), ("giai_6_2", 2)],
            [("giai_3_4", 1), ("giai_3_4", 3), ("giai_2_2", 2)],
            reverse=True,
        )


class Btl_SC_TD_05LotoMethod(BasePredictionMethod, BaseMakeResult):
    def get_code(self):
        return "btl_sc_TD_05"

    def get_name(self):
        return "SC_TD 05"

    def get_description(self):
        return "Tổng từ giải giai_db.2 + 3.2.3 + 3.3.2 và giải 1.1.2 + 3.5.4 + 3.5.5"

    def calculate(self, data):
        return self._make_result(
            data,
            [("giai_db", 1), ("giai_3_2", 2), ("giai_3_3", 1)],
            [("giai_1", 1), ("giai_3_5", 3), ("giai_3_5", 4)],
            reverse=True,
        )


class Btl_SC_TD_06LotoMethod(BasePredictionMethod, BaseMakeResult):
    def get_code(self):
        return "btl_sc_TD_06"

    def get_name(self):
        return "SC_TD 06 đb"

    def get_description(self):
        return "Tổng từ giải 5.3.3 + 5.3.4 + 7.2.2 và giải 5.5.1 + 5.6.1 + 6.1.2"

    def calculate(self, data):
        return self._make_result(
            data,
            [("giai_5_3", 2), ("giai_5_3", 3), ("giai_7_2", 1)],
            [("giai_5_5", 0), ("giai_5_6", 0), ("giai_6_1", 1)],
            reverse=True,
        )


class Btl_SC_TD_07LotoMethod(BasePredictionMethod, BaseMakeResult):
    def get_code(self):
        return "btl_sc_TD_07"

    def get_name(self):
        return "SC_TD 07 đb"

    def get_description(self):
        return "Tổng từ giải 3.3.1 + 3.3.5 + 5.6.1 và giải 3.6.1 + 3.6.4 + 5.6.3"

    def calculate(self, data):
        return self._make_result(
            data,
            [("giai_3_3", 0), ("giai_3_3", 4), ("giai_5_6", 0)],
            [("giai_3_6", 0), ("giai_3_6", 3), ("giai_5_6", 2)],
            reverse=True,
        )


class Btl_SC_TD_08LotoMethod(BasePredictionMethod, BaseMakeResult):
    def get_code(self):
        return "btl_sc_TD_08"

    def get_name(self):
        return "SC_TD 08 k3n"

    def get_description(self):
        return "Tổng từ giải 3.1.1 + 3.1.2 + 3.4.1 và giải 3.1.4 + 3.1.5 + 3.4.5"

    def calculate(self, data):
        return self._make_result(
            data,
            [("giai_3_1", 0), ("giai_3_1", 1), ("giai_3_4", 0)],
            [("giai_3_1", 3), ("giai_3_1", 4), ("giai_3_4", 4)],
            reverse=True,
        )


class Btl_SC_TD_09LotoMethod(BasePredictionMethod, BaseMakeResult):
    def get_code(self):
        return "btl_sc_TD_09"

    def get_name(self):
        return "SC_TD 09"

    def get_description(self):
        return "Tổng từ giải giai_db.3 + 3.3.1 + 3.3.4 và giải 2.1.3 + 3.4.1 + 3.6.2"

    def calculate(self, data):
        return self._make_result(
            data,
            [("giai_db", 2), ("giai_3_3", 0), ("giai_3_3", 3)],
            [("giai_2_1", 2), ("giai_3_4", 0), ("giai_3_6", 1)],
            reverse=True,
        )


class Btl_SC_TD_10LotoMethod(BasePredictionMethod, BaseMakeResult):
    def get_code(self):
        return "btl_sc_TD_10"

    def get_name(self):
        return "SC_TD 10 đb"

    def get_description(self):
        return "Tổng từ giải giai_db.1 + 3.1.3 + 3.3.5 và giải 3.1.1 + 3.4.1 + 3.6.3"

    def calculate(self, data):
        return self._make_result(
            data,
            [("giai_db", 0), ("giai_3_1", 2), ("giai_3_3", 4)],
            [("giai_3_1", 0), ("giai_3_4", 0), ("giai_3_6", 2)],
            reverse=True,
        )


class Btl_SC_TD_11LotoMethod(BasePredictionMethod, BaseMakeResult):
    def get_code(self):
        return "btl_sc_TD_11"

    def get_name(self):
        return "SC_TD 11"

    def get_description(self):
        return "Tổng từ giải 3.1.5 + 3.2.3 + 7.3.2 và giải 3.3.1 + 3.4.5 + 3.6.4"

    def calculate(self, data):
        return self._make_result(
            data,
            [("giai_3_1", 4), ("giai_3_2", 2), ("giai_7_3", 1)],
            [("giai_3_3", 0), ("giai_3_4", 4), ("giai_3_6", 3)],
            reverse=True,
        )


class Btl_SC_TD_12LotoMethod(BasePredictionMethod, BaseMakeResult):
    def get_code(self):
        return "btl_sc_TD_12"

    def get_name(self):
        return "SC_TD 12"

    def get_description(self):
        return "Tổng từ giải 4.2.2 + 5.2.2 + 5.2.4 và giải 5.1.4 + 5.5.3 + 5.5.4"

    def calculate(self, data):
        return self._make_result(
            data,
            [("giai_4_2", 1), ("giai_5_2", 1), ("giai_5_2", 3)],
            [("giai_5_1", 3), ("giai_5_5", 2), ("giai_5_5", 3)],
            reverse=True,
        )


class Btl_SC_TD_13LotoMethod(BasePredictionMethod, BaseMakeResult):
    def get_code(self):
        return "btl_sc_TD_13"

    def get_name(self):
        return "SC_TD 13"

    def get_description(self):
        return "Tổng từ giải 1.1.1 + 3.2.2 + 3.2.4 và giải giai_db.2 + 3.6.1 + 3.6.2"

    def calculate(self, data):
        return self._make_result(
            data,
            [("giai_1", 0), ("giai_3_2", 1), ("giai_3_2", 3)],
            [("giai_db", 1), ("giai_3_6", 0), ("giai_3_6", 1)],
            reverse=True,
        )


class Btl_SC_TD_14LotoMethod(BasePredictionMethod, BaseMakeResult):
    def get_code(self):
        return "btl_sc_TD_14"

    def get_name(self):
        return "SC_TD 14"

    def get_description(self):
        return "Tổng từ giải 3.2.3 + 3.3.2 + 5.3.2 và giải 3.6.2 + 3.6.3 + 4.4.4"

    def calculate(self, data):
        return self._make_result(
            data,
            [("giai_3_2", 2), ("giai_3_3", 1), ("giai_5_3", 1)],
            [("giai_3_6", 1), ("giai_3_6", 2), ("giai_4_4", 3)],
            reverse=True,
        )


class Btl_SC_TD_15LotoMethod(BasePredictionMethod, BaseMakeResult):
    def get_code(self):
        return "btl_sc_TD_15"

    def get_name(self):
        return "SC_TD 15"

    def get_description(self):
        return "Tổng từ giải 3.1.1 + 3.3.5 + 4.3.2 và giải giai_db.2 + 3.4.4 + 3.6.5"

    def calculate(self, data):
        return self._make_result(
            data,
            [("giai_3_1", 0), ("giai_3_3", 4), ("giai_4_3", 1)],
            [("giai_db", 1), ("giai_3_4", 3), ("giai_3_6", 4)],
            reverse=True,
        )


class Btl_SC_TD_16LotoMethod(BasePredictionMethod, BaseMakeResult):
    def get_code(self):
        return "btl_sc_TD_16"

    def get_name(self):
        return "SC_TD 16"

    def get_description(self):
        return "Tổng từ giải 3.2.2 + 3.3.5 + 6.2.1 và giải 3.6.4 + 3.6.5 + 6.2.3"

    def calculate(self, data):
        return self._make_result(
            data,
            [("giai_3_2", 1), ("giai_3_3", 4), ("giai_6_2", 0)],
            [("giai_3_6", 3), ("giai_3_6", 4), ("giai_6_2", 2)],
            reverse=True,
        )


class Btl_SC_TD_17LotoMethod(BasePredictionMethod, BaseMakeResult):
    def get_code(self):
        return "btl_sc_TD_17"

    def get_name(self):
        return "SC_TD 17 db"

    def get_description(self):
        return "Tổng từ giải 1.1.4 + 3.1.5 + 3.2.3 và giải giai_db.1 + 3.4.1 + 3.4.2"

    def calculate(self, data):
        return self._make_result(
            data,
            [("giai_1", 3), ("giai_3_1", 4), ("giai_3_2", 2)],
            [("giai_db", 0), ("giai_3_4", 0), ("giai_3_4", 1)],
            reverse=True,
        )


class Btl_SC_TD_18LotoMethod(BasePredictionMethod, BaseMakeResult):
    def get_code(self):
        return "btl_sc_TD_18"

    def get_name(self):
        return "SC_TD 18"

    def get_description(self):
        return "Tổng từ giải 5.1.4 + 5.2.1 + 6.1.3 và giải 2.2.4 + 5.4.4 + 5.5.2"

    def calculate(self, data):
        return self._make_result(
            data,
            [("giai_5_1", 3), ("giai_5_2", 0), ("giai_6_1", 2)],
            [("giai_2_2", 3), ("giai_5_4", 3), ("giai_5_5", 1)],
            reverse=True,
        )


class Btl_SC_TD_19LotoMethod(BasePredictionMethod, BaseMakeResult):
    def get_code(self):
        return "btl_sc_TD_19"

    def get_name(self):
        return "SC_TD 19"

    def get_description(self):
        return "Tổng từ giải 2.2.1 + 5.2.1 + 5.3.4 và giải 3.4.1 + 5.4.2 + 5.5.2"

    def calculate(self, data):
        return self._make_result(
            data,
            [("giai_2_2", 0), ("giai_5_2", 0), ("giai_5_3", 3)],
            [("giai_3_4", 0), ("giai_5_4", 1), ("giai_5_5", 1)],
            reverse=True,
        )


class Btl_SC_TD_20LotoMethod(BasePredictionMethod, BaseMakeResult):
    def get_code(self):
        return "btl_sc_TD_20"

    def get_name(self):
        return "SC_TD 20"

    def get_description(self):
        return "Tổng từ giải 2.1.2 + 3.1.1 + 3.3.1 và giải 3.5.1 + 3.5.2 + 7.4.1"

    def calculate(self, data):
        return self._make_result(
            data,
            [("giai_2_1", 1), ("giai_3_1", 0), ("giai_3_3", 0)],
            [("giai_3_5", 0), ("giai_3_5", 1), ("giai_7_4", 0)],
            reverse=True,
        )


class Btl_SC_TD_21LotoMethod(BasePredictionMethod, BaseMakeResult):
    def get_code(self):
        return "btl_sc_TD_21"

    def get_name(self):
        return "SC_TD 21"

    def get_description(self):
        return "Tổng từ giải giai_db.3 + 5.1.2 + 5.3.4 và giải 2.1.4 + 5.5.4 + 5.6.4"

    def calculate(self, data):
        return self._make_result(
            data,
            [("giai_db", 2), ("giai_5_1", 1), ("giai_5_3", 3)],
            [("giai_2_1", 3), ("giai_5_5", 3), ("giai_5_6", 3)],
            reverse=True,
        )


class Btl_SC_TD_22LotoMethod(BasePredictionMethod, BaseMakeResult):
    def get_code(self):
        return "btl_sc_TD_22"

    def get_name(self):
        return "SC_TD 22"

    def get_description(self):
        return "Tổng từ giải 4.2.1 + 4.2.2 và giải 4.2.3 + 4.2.4"

    def calculate(self, data):
        return self._make_result(
            data, [("giai_4_2", 0), ("giai_4_2", 1)], [("giai_4_2", 2), ("giai_4_2", 3)]
        )


class Btl_SC_TD_23LotoMethod(BasePredictionMethod, BaseMakeResult):
    def get_code(self):
        return "btl_sc_TD_23"

    def get_name(self):
        return "SC_TD 23"

    def get_description(self):
        return "Tổng từ giải 3.1.1 + 3.1.4 + 3.4.3 và giải 3.4.1 + 3.5.5 + 5.2.1"

    def calculate(self, data):
        return self._make_result(
            data,
            [("giai_3_1", 0), ("giai_3_1", 3), ("giai_3_4", 2)],
            [("giai_3_4", 0), ("giai_3_5", 4), ("giai_5_2", 0)],
            reverse=True,
        )


class Btl_SC_TD_24LotoMethod(BasePredictionMethod, BaseMakeResult):
    def get_code(self):
        return "btl_sc_TD_24"

    def get_name(self):
        return "SC_TD 24"

    def get_description(self):
        return "Tổng từ giải 3.2.5 + 5.1.1 + 5.3.1 và giải 3.2.4 + 5.6.1 + 5.6.3"

    def calculate(self, data):
        return self._make_result(
            data,
            [("giai_3_2", 4), ("giai_5_1", 0), ("giai_5_3", 0)],
            [("giai_3_2", 3), ("giai_5_6", 0), ("giai_5_6", 2)],
            reverse=True,
        )


class Btl_SC_TD_25LotoMethod(BasePredictionMethod, BaseMakeResult):
    def get_code(self):
        return "btl_sc_TD_25"

    def get_name(self):
        return "SC_TD 25"

    def get_description(self):
        return "Tổng từ giải 3.5.3 + 5.3.1 + 5.3.2 và giải 4.1.3 + 5.4.4 + 5.5.2"

    def calculate(self, data):
        return self._make_result(
            data,
            [("giai_3_5", 2), ("giai_5_3", 0), ("giai_5_3", 1)],
            [("giai_4_1", 2), ("giai_5_4", 3), ("giai_5_5", 1)],
            reverse=True,
        )


class Btl_SC_TD_26LotoMethod(BasePredictionMethod, BaseMakeResult):
    def get_code(self):
        return "btl_sc_TD_26"

    def get_name(self):
        return "SC_TD 26"

    def get_description(self):
        return "Tổng từ giải giai_db.4 + 3.3.3 + 3.3.4 và giải 3.3.4 + 3.4.1 + 3.4.4"

    def calculate(self, data):
        return self._make_result(
            data,
            [("giai_db", 3), ("giai_3_3", 2), ("giai_3_3", 3)],
            [("giai_3_3", 3), ("giai_3_4", 0), ("giai_3_4", 3)],
            reverse=True,
        )


class Btl_SC_TD_27LotoMethod(BasePredictionMethod, BaseMakeResult):
    def get_code(self):
        return "btl_sc_TD_27"

    def get_name(self):
        return "SC_TD 27"

    def get_description(self):
        return "Tổng từ giải 3.1.1 + 3.3.2 + 4.1.4 và giải 3.5.4 + 3.6.2 + 5.5.1"

    def calculate(self, data):
        return self._make_result(
            data,
            [("giai_3_1", 0), ("giai_3_3", 1), ("giai_4_1", 3)],
            [("giai_3_5", 3), ("giai_3_6", 1), ("giai_5_5", 0)],
            reverse=True,
        )


class Btl_SC_TD_28LotoMethod(BasePredictionMethod, BaseMakeResult):
    def get_code(self):
        return "btl_sc_TD_28"

    def get_name(self):
        return "SC_TD 28"

    def get_description(self):
        return "Tổng từ giải 3.3.3 + 5.2.2 + 5.2.3 và giải 3.2.3 + 5.4.3 + 5.6.1"

    def calculate(self, data):
        return self._make_result(
            data,
            [("giai_3_3", 2), ("giai_5_2", 1), ("giai_5_2", 2)],
            [("giai_3_2", 2), ("giai_5_4", 2), ("giai_5_6", 0)],
            reverse=True,
        )


class Btl_SC_TD_29LotoMethod(BasePredictionMethod, BaseMakeResult):
    def get_code(self):
        return "btl_sc_TD_29"

    def get_name(self):
        return "SC_TD 29"

    def get_description(self):
        return "Tổng từ giải 3.5.1 + 3.5.5 + 4.1.1 và giải 4.4.4 + 5.2.4 + 5.3.3"

    def calculate(self, data):
        return self._make_result(
            data,
            [("giai_3_5", 0), ("giai_3_5", 4), ("giai_4_1", 0)],
            [("giai_4_4", 3), ("giai_5_2", 3), ("giai_5_3", 2)],
            reverse=True,
        )


class Btl_SC_TD_30LotoMethod(BasePredictionMethod, BaseMakeResult):
    def get_code(self):
        return "btl_sc_TD_30"

    def get_name(self):
        return "SC_TD 30"

    def get_description(self):
        return "Tổng từ giải 3.1.5 + 3.2.3 + 5.3.4 và giải 3.2.3 + 3.4.2 + 3.6.3"

    def calculate(self, data):
        return self._make_result(
            data,
            [("giai_3_1", 4), ("giai_3_2", 2), ("giai_5_3", 3)],
            [("giai_3_2", 2), ("giai_3_4", 1), ("giai_3_6", 2)],
            reverse=True,
        )


class Btl_SC_TD_31LotoMethod(BasePredictionMethod, BaseMakeResult):
    def get_code(self):
        return "btl_sc_TD_31"

    def get_name(self):
        return "SC_TD 31"

    def get_description(self):
        return "Tổng từ giải 3.1.1 + 3.1.2 + 4.2.1 và giải 2.2.4 + 3.4.1 + 3.5.5"

    def calculate(self, data):
        return self._make_result(
            data,
            [("giai_3_1", 0), ("giai_3_1", 1), ("giai_4_2", 0)],
            [("giai_2_2", 3), ("giai_3_4", 0), ("giai_3_5", 4)],
            reverse=True,
        )


class Btl_SC_TD_32LotoMethod(BasePredictionMethod, BaseMakeResult):
    def get_code(self):
        return "btl_sc_TD_32"

    def get_name(self):
        return "SC_TD 32 đề"

    def get_description(self):
        return "Tổng từ giải 2.1.2 + 3.2.4 + 3.3.5 và giải 3.2.1 + 3.4.1 + 3.4.2"

    def calculate(self, data):
        return self._make_result(
            data,
            [("giai_2_1", 1), ("giai_3_2", 3), ("giai_3_3", 4)],
            [("giai_3_2", 0), ("giai_3_4", 0), ("giai_3_4", 1)],
            reverse=True,
        )


class Btl_SC_TD_33LotoMethod(BasePredictionMethod, BaseMakeResult):
    def get_code(self):
        return "btl_sc_TD_33"

    def get_name(self):
        return "SC_TD 33"

    def get_description(self):
        return "Tổng từ giải 3.1.1 + 3.2.2 + 5.5.1 và giải 3.1.5 + 3.4.4 + 3.5.1"

    def calculate(self, data):
        return self._make_result(
            data,
            [("giai_3_1", 0), ("giai_3_2", 1), ("giai_5_5", 0)],
            [("giai_3_1", 4), ("giai_3_4", 3), ("giai_3_5", 0)],
            reverse=True,
        )


class Btl_SC_TD_34LotoMethod(BasePredictionMethod, BaseMakeResult):
    def get_code(self):
        return "btl_sc_TD_34"

    def get_name(self):
        return "SC_TD 34"

    def get_description(self):
        return "Tổng từ giải 2.2.4 + 5.1.1 + 5.3.4 và giải 5.4.1 + 5.4.4 + 7.4.1"

    def calculate(self, data):
        return self._make_result(
            data,
            [("giai_2_2", 3), ("giai_5_1", 0), ("giai_5_3", 3)],
            [("giai_5_4", 0), ("giai_5_4", 3), ("giai_7_4", 0)],
            reverse=True,
        )


class Btl_SC_TD_35LotoMethod(BasePredictionMethod, BaseMakeResult):
    def get_code(self):
        return "btl_sc_TD_35"

    def get_name(self):
        return "SC_TD 35"

    def get_description(self):
        return "Tổng từ giải 3.1.2 + 3.1.3 + 5.4.4 và giải 5.4.1 + 5.4.2 + 5.4.4"

    def calculate(self, data):
        return self._make_result(
            data,
            [("giai_3_1", 1), ("giai_3_1", 2), ("giai_5_4", 3)],
            [("giai_5_4", 0), ("giai_5_4", 1), ("giai_5_4", 3)],
            reverse=True,
        )


class Btl_SC_TD_36LotoMethod(BasePredictionMethod, BaseMakeResult):
    def get_code(self):
        return "btl_sc_TD_36"

    def get_name(self):
        return "SC_TD 36 đề"

    def get_description(self):
        return "Tổng từ giải 2.2.1 + 3.1.4 + 3.2.3 và giải 3.4.1 + 3.6.3 + 4.3.3"

    def calculate(self, data):
        return self._make_result(
            data,
            [("giai_2_2", 0), ("giai_3_1", 3), ("giai_3_2", 2)],
            [("giai_3_4", 0), ("giai_3_6", 2), ("giai_4_3", 2)],
            reverse=True,
        )


class Btl_SC_TD_37LotoMethod(BasePredictionMethod, BaseMakeResult):
    def get_code(self):
        return "btl_sc_TD_37"

    def get_name(self):
        return "SC_TD 37 đề"

    def get_description(self):
        return "Tổng từ giải 3.1.2 + 3.1.3 + 5.4.4 và giải 2.2.4 + 3.4.1 + 3.5.5"

    def calculate(self, data):
        return self._make_result(
            data,
            [("giai_3_1", 1), ("giai_3_1", 2), ("giai_5_4", 3)],
            [("giai_2_2", 3), ("giai_3_4", 0), ("giai_3_5", 4)],
            reverse=True,
        )


class Btl_SC_TD_38LotoMethod(BasePredictionMethod, BaseMakeResult):
    def get_code(self):
        return "btl_sc_TD_38"

    def get_name(self):
        return "SC_TD 38 LK"

    def get_description(self):
        return "Tổng từ giải 4.1.1 + 4.1.2 và giải 4.1.2 + 4.1.4"

    def calculate(self, data):
        return self._make_result(
            data,
            [("giai_4_1", 0), ("giai_4_1", 1)],
            [("giai_4_1", 1), ("giai_4_1", 3)],
            reverse=True,
        )


class Btl_SC_TD_39LotoMethod(BasePredictionMethod, BaseMakeResult):
    def get_code(self):
        return "btl_sc_TD_39"

    def get_name(self):
        return "SC_TD 39"

    def get_description(self):
        return "Tổng từ giải giai_db.1 + 3.1.5 3.2.3 và 2.2.4 + 3.4.1 + 3.5.5"

    def calculate(self, data):
        return self._make_result(
            data,
            [("giai_db", 0), ("giai_3_1", 4), ("giai_3_2", 2)],
            [("giai_2_2", 3), ("giai_3_4", 0), ("giai_3_5", 4)],
            reverse=True,
        )


class Btl_SC_TD_40LotoMethod(BasePredictionMethod, BaseMakeResult):
    def get_code(self):
        return "btl_sc_TD_40"

    def get_name(self):
        return "SC_TD 40"

    def get_description(self):
        return "Tổng từ giải 2.1.1 + 3.1.2 + 3.3.3 và 3.1.3 + 3.4.5 + 3.5.2"

    def calculate(self, data):
        return self._make_result(
            data,
            [("giai_2_1", 0), ("giai_3_1", 1), ("giai_3_3", 2)],
            [("giai_3_1", 2), ("giai_3_4", 4), ("giai_3_5", 1)],
            reverse=True,
        )


class Btl_SC_TD_41LotoMethod(BasePredictionMethod, BaseMakeResult):
    def get_code(self):
        return "btl_sc_TD_41"

    def get_name(self):
        return "SC_TD 41"

    def get_description(self):
        return "Tổng từ giải 2.2.3 + 5.1.4 + 5.3.3 và 3.5.2 + 5.4.1 + 5.4.2"

    def calculate(self, data):
        return self._make_result(
            data,
            [("giai_2_2", 2), ("giai_5_1", 3), ("giai_5_3", 1)],
            [("giai_3_5", 1), ("giai_5_4", 0), ("giai_5_4", 1)],
            reverse=True,
        )


class Btl_SC_TD_42LotoMethod(BasePredictionMethod, BaseMakeResult):
    def get_code(self):
        return "btl_sc_TD_42"

    def get_name(self):
        return "SC_TD 42"

    def get_description(self):
        return "Tổng từ giải 3.1.4 + 3.2.5 + 6.3.2 và 3.5.5 + 3.6.3 + 4.4.4"

    def calculate(self, data):
        return self._make_result(
            data,
            [("giai_3_1", 3), ("giai_3_2", 4), ("giai_6_3", 1)],
            [("giai_3_5", 4), ("giai_3_6", 2), ("giai_4_4", 3)],
            reverse=True,
        )


class Btl_SC_TD_43LotoMethod(BasePredictionMethod, BaseMakeResult):
    def get_code(self):
        return "btl_sc_TD_43"

    def get_name(self):
        return "SC_TD 43"

    def get_description(self):
        return "Tổng từ giải 2.1.3 + 5.1.1 + 5.1.2 và giai_db.2 + 5.5.4 + 5.6.3"

    def calculate(self, data):
        return self._make_result(
            data,
            [("giai_2_1", 2), ("giai_5_1", 0), ("giai_5_1", 1)],
            [("giai_db", 1), ("giai_5_5", 3), ("giai_5_6", 2)],
            reverse=True,
        )


class Btl_SC_TD_44LotoMethod(BasePredictionMethod, BaseMakeResult):
    def get_code(self):
        return "btl_sc_TD_44"

    def get_name(self):
        return "SC_TD 44"

    def get_description(self):
        return "Tổng từ giải 2.1.5 + 4.4.2 + 4.4.4 và 3.5.1 + 5.4.1 + 5.5.2"

    def calculate(self, data):
        return self._make_result(
            data,
            [("giai_2_1", 4), ("giai_4_4", 1), ("giai_4_4", 3)],
            [("giai_3_5", 0), ("giai_5_4", 0), ("giai_5_5", 1)],
            reverse=True,
        )


class Btl_SC_TD_45LotoMethod(BasePredictionMethod, BaseMakeResult):
    def get_code(self):
        return "btl_sc_TD_45"

    def get_name(self):
        return "SC_TD 45"

    def get_description(self):
        return "Tổng từ giải 1.1.2 + 3.2.1 + 3.2.3 và giai_db.2 + 3.4.1 + 3.4.3"

    def calculate(self, data):
        return self._make_result(
            data,
            [("giai_1", 1), ("giai_3_2", 0), ("giai_3_2", 2)],
            [("giai_db", 1), ("giai_3_4", 0), ("giai_3_4", 2)],
            reverse=True,
        )


class Btl_SC_TD_46LotoMethod(BasePredictionMethod, BaseMakeResult):
    def get_code(self):
        return "btl_sc_TD_46"

    def get_name(self):
        return "SC_TD 46"

    def get_description(self):
        return "Tổng từ giải 3.4.3 + 5.1.2 + 5.1.3 và 5.5.3 + 5.5.4 + 7.3.1"

    def calculate(self, data):
        return self._make_result(
            data,
            [("giai_3_4", 2), ("giai_5_1", 1), ("giai_5_1", 2)],
            [("giai_5_5", 2), ("giai_5_5", 3), ("giai_7_3", 0)],
            reverse=True,
        )


class Btl_SC_TD_47LotoMethod(BasePredictionMethod, BaseMakeResult):
    def get_code(self):
        return "btl_sc_TD_47"

    def get_name(self):
        return "SC_TD 47"

    def get_description(self):
        return "Tổng từ giải 2.2.5 + 3.1.3 + 3.3.4 và 2.1.1 + 3.4.2 + 3.6.3"

    def calculate(self, data):
        return self._make_result(
            data,
            [("giai_2_2", 4), ("giai_3_1", 2), ("giai_3_3", 3)],
            [("giai_2_1", 0), ("giai_3_4", 1), ("giai_3_6", 2)],
            reverse=True,
        )

class Btl_SC_TD_48LotoMethod(BasePredictionMethod, BaseMakeResult):
    def get_code(self):
        return "btl_sc_TD_48"

    def get_name(self):
        return "SC_TD 48"

    def get_description(self):
        return "Tổng từ giải 2.1.5 + 5.1.4 + 5.2.3 và giai_db.4 + 5.4.4 + 5.6.4"

    def calculate(self, data):
        return self._make_result(
            data,
            [("giai_2_1", 4), ("giai_5_1", 3), ("giai_5_2", 2)],
            [("giai_db", 3), ("giai_5_4", 3), ("giai_5_6", 3)],
            reverse=True,
        )

class Btl_SC_TD_49LotoMethod(BasePredictionMethod, BaseMakeResult):
    def get_code(self):
        return "btl_sc_TD_49"

    def get_name(self):
        return "SC_TD 49"

    def get_description(self):
        return "Tổng từ giải 3.4.3 + 5.1.2 + 5.1.3 và 2.1.3 + 5.4.1 + 5.5.4"

    def calculate(self, data):
        return self._make_result(
            data,
            [("giai_3_4", 2), ("giai_5_1", 1), ("giai_5_1", 2)],
            [("giai_2_1", 2), ("giai_5_4", 0), ("giai_5_5", 3)],
            reverse=True,
        )

class Btl_SC_TD_50LotoMethod(BasePredictionMethod, BaseMakeResult):
    def get_code(self):
        return "btl_sc_TD_50"

    def get_name(self):
        return "SC_TD 50"

    def get_description(self):
        return "Tổng từ giải 3.1.1 + 3.3.5 + 7.2.2 và 2.2.3 + 3.6.1 + 3.6.5"

    def calculate(self, data):
        return self._make_result(
            data,
            [("giai_3_1", 0), ("giai_3_3", 4), ("giai_7_2", 1)],
            [("giai_2_2", 2), ("giai_3_6", 0), ("giai_3_6", 4)],
            reverse=True,
        )
    
class Btl_SC_TD_51LotoMethod(BasePredictionMethod, BaseMakeResult):
    def get_code(self):
        return "btl_sc_TD_51"

    def get_name(self):
        return "SC_TD 51"

    def get_description(self):
        return "Tổng từ giải 2.1.1 + 3.1.2 + 3.3.5 và 1.1.2 + 3.6.2 + 3.6.5"

    def calculate(self, data):
        return self._make_result(
            data,
            [("giai_2_1", 0), ("giai_3_1", 1), ("giai_3_3", 4)],
            [("giai_1", 1), ("giai_3_6", 1), ("giai_3_6", 4)],
            reverse=True,
        )
    
class Btl_SC_TD_52LotoMethod(BasePredictionMethod, BaseMakeResult):
    def get_code(self):
        return "btl_sc_TD_52"

    def get_name(self):
        return "SC_TD 52"

    def get_description(self):
        return "Tổng từ giải 3.5.4 + 5.2.1 + 5.3.1 và 3.6.1 + 5.4.3 + 5.5.3"

    def calculate(self, data):
        return self._make_result(
            data,
            [("giai_3_5", 3), ("giai_5_2", 0), ("giai_5_3", 1)],
            [("giai_3_6", 0), ("giai_5_4", 2), ("giai_5_5", 2)],
            reverse=True,
        )
    
class Btl_SC_TD_53LotoMethod(BasePredictionMethod, BaseMakeResult):
    def get_code(self):
        return "btl_sc_TD_53"

    def get_name(self):
        return "SC_TD 53"

    def get_description(self):
        return "Tổng từ giải 3.5.2 + 5.2.1 + 5.3.1 và 2.2.1 + 5.4.1 + 5.6.1"

    def calculate(self, data):
        return self._make_result(
            data,
            [("giai_3_5", 1), ("giai_5_2", 0), ("giai_5_3", 0)],
            [("giai_2_2", 0), ("giai_5_4", 0), ("giai_5_6", 0)],
            reverse=True,
        )

class Btl_SC_TD_54LotoMethod(BasePredictionMethod, BaseMakeResult):
    def get_code(self):
        return "btl_sc_TD_54"

    def get_name(self):
        return "SC_TD 54"

    def get_description(self):
        return "Tổng từ giải 4.1.2 + 5.1.1 + 5.1.3 và giai_db.2 + 5.4.3 + 5.5.2"

    def calculate(self, data):
        return self._make_result(
            data,
            [("giai_4_1", 1), ("giai_5_1", 0), ("giai_5_1", 2)],
            [("giai_db", 1), ("giai_5_4", 2), ("giai_5_5", 1)],
            reverse=True,
        )
    
class Btl_SC_TD_55LotoMethod(BasePredictionMethod, BaseMakeResult):
    def get_code(self):
        return "btl_sc_TD_55"

    def get_name(self):
        return "SC_TD 55"

    def get_description(self):
        return "Tổng từ giải 5.2.1 + 5.2.2 + 5.3.2 và 5.4.2 + 5.4.4 + 6.3.3"

    def calculate(self, data):
        return self._make_result(
            data,
            [("giai_5_2", 0), ("giai_5_2", 1), ("giai_5_3", 1)],
            [("giai_5_4", 1), ("giai_5_4", 3), ("giai_6_3", 2)],
            reverse=True,
        )
