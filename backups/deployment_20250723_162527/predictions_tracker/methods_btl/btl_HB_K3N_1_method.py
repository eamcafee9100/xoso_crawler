# from typing import Dict, List, Any
from typing import Any, Dict, List

from .base import BaseMakeResult, BasePredictionMethod


class Btl_HB_k3N_1_01LotoMethod(BasePredictionMethod, BaseMakeResult):
    def get_code(self):
        return "btl_hb_k3n_1_01"

    def get_name(self):
        return "BTL HB_k3N_1 01"

    def get_description(self):
        return "Tổng từ giải 1.1.5 + 6.2.2 + 7.4.1 và giải 2.2.1 + 4.3.4 + 7.3.1"

    def calculate(self, data):
        return self._make_result(
            data,
            [("giai_1", 4), ("giai_6_2", 1), ("giai_7_4", 0)],
            [("giai_2_2", 0), ("giai_4_3", 3), ("giai_7_3", 0)],
            reverse=True,
        )


class Btl_HB_k3N_1_02LotoMethod(BasePredictionMethod, BaseMakeResult):
    def get_code(self):
        return "btl_hb_k3n_1_02"

    def get_name(self):
        return "BTL HB_k3N_1 02"

    def get_description(self):
        return "Tổng từ giải 2.1.4 + 3.4.5 + 3.6.3 và giải giai_db.5 + 5.2.2 + 6.2.3"

    def calculate(self, data):
        return self._make_result(
            data,
            [("giai_2_1", 3), ("giai_3_4", 4), ("giai_3_6", 2)],
            [("giai_db", 4), ("giai_5_2", 1), ("giai_6_2", 2)],
            reverse=True,
        )


class Btl_HB_k3N_1_03LotoMethod(BasePredictionMethod, BaseMakeResult):
    def get_code(self):
        return "btl_hb_k3n_1_03"

    def get_name(self):
        return "BTL HB_k3N_1 03"

    def get_description(self):
        return "Tổng từ giải 2.2.2 + 4.4.3 + 5.4.1 và giải 3.1.4 + 4.1.2 + 6.2.3"

    def calculate(self, data):
        return self._make_result(
            data,
            [("giai_2_2", 1), ("giai_4_4", 2), ("giai_5_4", 0)],
            [("giai_3_1", 3), ("giai_4_1", 1), ("giai_6_2", 2)],
            reverse=True,
        )


class Btl_HB_k3N_1_04LotoMethod(BasePredictionMethod, BaseMakeResult):
    def get_code(self):
        return "btl_hb_k3n_1_04"

    def get_name(self):
        return "BTL HB_k3N_1 04"

    def get_description(self):
        return "Tổng từ giải 3.2.1 + 6.3.2 + 7.3.1 và giải giai_db.4 + 3.1.3 + 4.3.3"

    def calculate(self, data):
        return self._make_result(
            data,
            [("giai_3_2", 0), ("giai_6_3", 1), ("giai_7_3", 0)],
            [("giai_db", 3), ("giai_3_1", 2), ("giai_4_3", 2)],
            reverse=True,
        )


class Btl_HB_k3N_1_05LotoMethod(BasePredictionMethod, BaseMakeResult):
    def get_code(self):
        return "btl_hb_k3n_1_05"

    def get_name(self):
        return "BTL HB_k3N_1 05"

    def get_description(self):
        return (
            "Tổng từ giải 3.2.4 + 3.4.5 + 4.3.1 và giải giai_db.2 + giai_db.4 + 5.6.1"
        )

    def calculate(self, data):
        return self._make_result(
            data,
            [("giai_3_2", 3), ("giai_3_4", 4), ("giai_4_3", 0)],
            [("giai_db", 1), ("giai_db", 3), ("giai_5_6", 0)],
            reverse=True,
        )


class Btl_HB_k3N_1_06LotoMethod(BasePredictionMethod, BaseMakeResult):
    def get_code(self):
        return "btl_hb_k3n_1_06"

    def get_name(self):
        return "BTL HB_k3N_1 06"

    def get_description(self):
        return "Tổng từ giải 1.1.3 + 5.2.3 + 5.6.1 và giải 5.3.3 + 5.4.3 + 5.6.3"

    def calculate(self, data):
        return self._make_result(
            data,
            [("giai_1", 2), ("giai_5_2", 2), ("giai_5_6", 0)],
            [("giai_5_3", 2), ("giai_5_4", 2), ("giai_5_6", 2)],
            reverse=True,
        )


class Btl_HB_k3N_1_07LotoMethod(BasePredictionMethod, BaseMakeResult):
    def get_code(self):
        return "btl_hb_k3n_1_07"

    def get_name(self):
        return "BTL HB_k3N_1 07"

    def get_description(self):
        return "Tổng từ giải 3.2.4 + 6.3.2 + 7.3.1 và giải giai_db.4 + 3.1.3 + 4.3.3"

    def calculate(self, data):
        return self._make_result(
            data,
            [("giai_3_2", 3), ("giai_6_3", 1), ("giai_7_3", 0)],
            [("giai_db", 3), ("giai_3_1", 2), ("giai_4_3", 2)],
            reverse=True,
        )


class Btl_HB_k3N_1_08LotoMethod(BasePredictionMethod, BaseMakeResult):
    def get_code(self):
        return "btl_hb_k3n_1_08"

    def get_name(self):
        return "BTL HB_k3N_1 08"

    def get_description(self):
        return "Tổng từ giải 3.1.1 + 4.3.3 + 5.5.1 và giải giai_db.2 + 3.3.4 + 5.3.1"

    def calculate(self, data):
        return self._make_result(
            data,
            [("giai_3_1", 0), ("giai_4_3", 2), ("giai_5_5", 0)],
            [("giai_db", 1), ("giai_3_3", 3), ("giai_5_3", 0)],
            reverse=True,
        )


class Btl_HB_k3N_1_09LotoMethod(BasePredictionMethod, BaseMakeResult):
    def get_code(self):
        return "btl_hb_k3n_1_09"

    def get_name(self):
        return "BTL HB_k3N_1 09"

    def get_description(self):
        return "Tổng từ giải 3.3.1 + 3.6.2 + 4.4.3 và giải 3.1.4 + 5.1.2 + 5.2.3"

    def calculate(self, data):
        return self._make_result(
            data,
            [("giai_3_3", 0), ("giai_3_6", 1), ("giai_4_4", 2)],
            [("giai_3_1", 3), ("giai_5_1", 1), ("giai_5_2", 2)],
            reverse=True,
        )


class Btl_HB_k3N_1_10LotoMethod(BasePredictionMethod, BaseMakeResult):
    def get_code(self):
        return "btl_hb_k3n_1_10"

    def get_name(self):
        return "BTL HB_k3N_1 10"

    def get_description(self):
        return "Tổng từ giải giai_db.1 + 3.1.3 + 4.2.1 và giải 3.3.5 + 4.3.4 + 5.4.4"

    def calculate(self, data):
        return self._make_result(
            data,
            [("giai_db", 0), ("giai_3_1", 2), ("giai_4_2", 0)],
            [("giai_3_3", 4), ("giai_4_3", 3), ("giai_5_4", 3)],
            reverse=True,
        )


class Btl_HB_k3N_1_11LotoMethod(BasePredictionMethod, BaseMakeResult):
    def get_code(self):
        return "btl_hb_k3n_1_11"

    def get_name(self):
        return "BTL HB_k3N_1 11"

    def get_description(self):
        return "Tổng từ giải giai_db.2 + 4.2.4 + 7.3.1 và giải 2.1.2 + 7.2.2 + 7.4.2"

    def calculate(self, data):
        return self._make_result(
            data,
            [("giai_db", 1), ("giai_4_2", 3), ("giai_7_3", 0)],
            [("giai_2_1", 1), ("giai_7_2", 1), ("giai_7_4", 1)],
            reverse=True,
        )


class Btl_HB_k3N_1_12LotoMethod(BasePredictionMethod, BaseMakeResult):
    def get_code(self):
        return "btl_hb_k3n_1_12"

    def get_name(self):
        return "BTL HB_k3N_1 12"

    def get_description(self):
        return "Tổng từ giải giai_db.3 + 5.5.2 + 5.5.3 và giải 3.1.2 + 3.1.5 + 4.1.3"

    def calculate(self, data):
        return self._make_result(
            data,
            [("giai_db", 2), ("giai_5_5", 1), ("giai_5_5", 2)],
            [("giai_3_1", 1), ("giai_3_1", 4), ("giai_4_1", 2)],
            reverse=True,
        )


class Btl_HB_k3N_1_13LotoMethod(BasePredictionMethod, BaseMakeResult):
    def get_code(self):
        return "btl_hb_k3n_1_13"

    def get_name(self):
        return "BTL HB_k3N_1 13"

    def get_description(self):
        return "Tổng từ giải 2.1.1 + 2.2.5 + 5.2.4 và giải 2.2.2 + 4.1.4 + 5.6.3"

    def calculate(self, data):
        return self._make_result(
            data,
            [("giai_2_1", 0), ("giai_2_2", 4), ("giai_5_2", 3)],
            [("giai_2_2", 1), ("giai_4_1", 3), ("giai_5_6", 2)],
            reverse=True,
        )


class Btl_HB_k3N_1_14LotoMethod(BasePredictionMethod, BaseMakeResult):
    def get_code(self):
        return "btl_hb_k3n_1_14"

    def get_name(self):
        return "BTL HB_k3N_1 14"

    def get_description(self):
        return "Tổng từ giải 5.1.1 + 5.4.2 + 7.1.2 và giải 5.1.1 + 5.2.3 + 5.4.3"

    def calculate(self, data):
        return self._make_result(
            data,
            [("giai_5_1", 0), ("giai_5_4", 1), ("giai_7_1", 1)],
            [("giai_5_1", 0), ("giai_5_2", 2), ("giai_5_4", 2)],
            reverse=True,
        )


class Btl_HB_k3N_1_15LotoMethod(BasePredictionMethod, BaseMakeResult):
    def get_code(self):
        return "btl_hb_k3n_1_15"

    def get_name(self):
        return "BTL HB_k3N_1 15"

    def get_description(self):
        return "Tổng từ giải 3.1.3 + 5.6.4 + 7.3.2 và giải 3.4.1 + 4.1.3 + 5.4.4"

    def calculate(self, data):
        return self._make_result(
            data,
            [("giai_3_1", 2), ("giai_5_6", 3), ("giai_7_3", 1)],
            [("giai_3_4", 0), ("giai_4_1", 2), ("giai_5_4", 3)],
            reverse=True,
        )
