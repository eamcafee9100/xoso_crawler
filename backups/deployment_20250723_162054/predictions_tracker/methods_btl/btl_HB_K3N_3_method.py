# from typing import Dict, List, Any
from typing import Any, Dict, List

from .base import BaseMakeResult, BasePredictionMethod


class Btl_HB_k3N_3_01LotoMethod(BasePredictionMethod, BaseMakeResult):
    def get_code(self):
        return "btl_hb_k3n_3_01"

    def get_name(self):
        return "BTL HB_k3N_3 01"

    def get_description(self):
        return "Tổng từ giải 3.6.5 + 5.2.1 + 5.5.1 và giải 2.1.5 + 3.1.1 + 7.3.1"

    def calculate(self, data):
        return self._make_result(
            data,
            [("giai_3_6", 4), ("giai_5_2", 0), ("giai_5_5", 0)],
            [("giai_2_1", 4), ("giai_3_1", 0), ("giai_7_3", 0)],
            reverse=True,
        )


class Btl_HB_k3N_3_02LotoMethod(BasePredictionMethod, BaseMakeResult):
    def get_code(self):
        return "btl_hb_k3n_3_02"

    def get_name(self):
        return "BTL HB_k3N_3 02"

    def get_description(self):
        return "Tổng từ giải giai_db.3 + 2.2.5 + 4.3.2 và giải 1.1.1 + 3.2.2 + 7.1.1"

    def calculate(self, data):
        return self._make_result(
            data,
            [("giai_db", 2), ("giai_2_2", 4), ("giai_4_3", 1)],
            [("giai_1", 0), ("giai_3_2", 1), ("giai_7_1", 0)],
            reverse=True,
        )


class Btl_HB_k3N_3_03LotoMethod(BasePredictionMethod, BaseMakeResult):
    def get_code(self):
        return "btl_hb_k3n_3_03"

    def get_name(self):
        return "BTL HB_k3N_3 03"

    def get_description(self):
        return "Tổng từ giải 1.1.3 + 3.5.2 + 6.3.2 và giải 3.1.4 + 5.5.3 + 5.6.3"

    def calculate(self, data):
        return self._make_result(
            data,
            [("giai_1", 2), ("giai_3_5", 1), ("giai_6_3", 1)],
            [("giai_3_1", 3), ("giai_5_5", 2), ("giai_5_6", 2)],
            reverse=True,
        )


class Btl_HB_k3N_3_04LotoMethod(BasePredictionMethod, BaseMakeResult):
    def get_code(self):
        return "btl_hb_k3n_3_04"

    def get_name(self):
        return "BTL HB_k3N_3 04"

    def get_description(self):
        return "Tổng từ giải 2.1.2 + 3.5.1 + 3.6.1 và giải 1.1.1 + 3.3.2 + 4.4.1"

    def calculate(self, data):
        return self._make_result(
            data,
            [("giai_2_1", 1), ("giai_3_5", 0), ("giai_3_6", 0)],
            [("giai_1", 0), ("giai_3_3", 1), ("giai_4_4", 0)],
            reverse=True,
        )


class Btl_HB_k3N_3_05LotoMethod(BasePredictionMethod, BaseMakeResult):
    def get_code(self):
        return "btl_hb_k3n_3_05"

    def get_name(self):
        return "BTL HB_k3N_3 05"

    def get_description(self):
        return "Tổng từ giải 2.1.1 + 2.1.5 + 7.3.2 và giải giai_db.1 + 3.5.5 + 6.2.3"

    def calculate(self, data):
        return self._make_result(
            data,
            [("giai_2_1", 0), ("giai_2_1", 4), ("giai_7_3", 1)],
            [("giai_db", 0), ("giai_3_5", 4), ("giai_6_2", 2)],
            reverse=True,
        )


class Btl_HB_k3N_3_06LotoMethod(BasePredictionMethod, BaseMakeResult):
    def get_code(self):
        return "btl_hb_k3n_3_06"

    def get_name(self):
        return "BTL HB_k3N_3 06"

    def get_description(self):
        return "Tổng từ giải 2.1.5 + 3.6.3 + 6.3.2 và giải 2.1.2 + 7.1.2 + 7.4.2"

    def calculate(self, data):
        return self._make_result(
            data,
            [("giai_2_1", 4), ("giai_3_6", 2), ("giai_6_3", 1)],
            [("giai_2_1", 1), ("giai_7_1", 1), ("giai_7_4", 1)],
            reverse=True,
        )


class Btl_HB_k3N_3_07LotoMethod(BasePredictionMethod, BaseMakeResult):
    def get_code(self):
        return "btl_hb_k3n_3_07"

    def get_name(self):
        return "BTL HB_k3N_3 07"

    def get_description(self):
        return "Tổng từ giải 1.1.5 + 4.3.1 + 5.4.2 và giải 1.1.5 + 3.5.1 + 7.3.1"

    def calculate(self, data):
        return self._make_result(
            data,
            [("giai_1", 4), ("giai_4_3", 0), ("giai_5_4", 1)],
            [("giai_1", 4), ("giai_3_5", 0), ("giai_7_3", 0)],
            reverse=True,
        )


class Btl_HB_k3N_3_08LotoMethod(BasePredictionMethod, BaseMakeResult):
    def get_code(self):
        return "btl_hb_k3n_3_08"

    def get_name(self):
        return "BTL HB_k3N_3 08"

    def get_description(self):
        return "Tổng từ giải giai_db.3 + 2.2.5 + 3.2.4 và giải 2.1.1 + 2.2.5 + 3.2.4"

    def calculate(self, data):
        return self._make_result(
            data,
            [("giai_db", 2), ("giai_2_2", 4), ("giai_3_2", 3)],
            [("giai_2_1", 0), ("giai_2_2", 4), ("giai_3_2", 3)],
            reverse=True,
        )


class Btl_HB_k3N_3_09LotoMethod(BasePredictionMethod, BaseMakeResult):
    def get_code(self):
        return "btl_hb_k3n_3_09"

    def get_name(self):
        return "BTL HB_k3N_3 09"

    def get_description(self):
        return "Tổng từ giải 3.1.5 + 3.2.4 + 3.4.5 và giải 4.2.3 + 5.1.2 + 5.4.2"

    def calculate(self, data):
        return self._make_result(
            data,
            [("giai_3_1", 4), ("giai_3_2", 3), ("giai_3_4", 4)],
            [("giai_4_2", 2), ("giai_5_1", 1), ("giai_5_4", 1)],
            reverse=True,
        )


class Btl_HB_k3N_3_10LotoMethod(BasePredictionMethod, BaseMakeResult):
    def get_code(self):
        return "btl_hb_k3n_3_10"

    def get_name(self):
        return "BTL HB_k3N_3 10"

    def get_description(self):
        return "Tổng từ giải 3.1.5 + 3.2.4 + 3.4.5 và giải 2.1.1 + 2.2.5 + 3.2.4"

    def calculate(self, data):
        return self._make_result(
            data,
            [("giai_3_1", 4), ("giai_3_2", 3), ("giai_3_4", 4)],
            [("giai_2_1", 0), ("giai_2_2", 4), ("giai_3_2", 3)],
            reverse=True,
        )


class Btl_HB_k3N_3_11LotoMethod(BasePredictionMethod, BaseMakeResult):
    def get_code(self):
        return "btl_hb_k3n_3_11"

    def get_name(self):
        return "BTL HB_k3N_3 11"

    def get_description(self):
        return "Tổng từ giải 5.2.2 + 5.4.2 + 6.3.1 và giải 5.2.2 + 5.6.1 + 5.6.4"

    def calculate(self, data):
        return self._make_result(
            data,
            [("giai_5_2", 1), ("giai_5_4", 1), ("giai_6_3", 0)],
            [("giai_5_2", 1), ("giai_5_6", 0), ("giai_5_6", 3)],
            reverse=True,
        )


class Btl_HB_k3N_3_12LotoMethod(BasePredictionMethod, BaseMakeResult):
    def get_code(self):
        return "btl_hb_k3n_3_12"

    def get_name(self):
        return "BTL HB_k3N_3 12"

    def get_description(self):
        return "Tổng từ giải 3.4.2 + 5.4.2 + 6.1.3 và giải 3.2.4 + 5.3.3 + 7.1.2"

    def calculate(self, data):
        return self._make_result(
            data,
            [("giai_3_4", 1), ("giai_5_4", 1), ("giai_6_1", 2)],
            [("giai_3_2", 3), ("giai_5_3", 2), ("giai_7_1", 1)],
            reverse=True,
        )


class Btl_HB_k3N_3_13LotoMethod(BasePredictionMethod, BaseMakeResult):
    def get_code(self):
        return "btl_hb_k3n_3_13"

    def get_name(self):
        return "BTL HB_k3N_3 13"

    def get_description(self):
        return "Tổng từ giải 3.6.1 + 4.1.2 + 5.2.4 và giải 3.5.2 + 6.1.2 + 7.4.1"

    def calculate(self, data):
        return self._make_result(
            data,
            [("giai_3_6", 0), ("giai_4_1", 1), ("giai_5_2", 3)],
            [("giai_3_5", 1), ("giai_6_1", 1), ("giai_7_4", 0)],
            reverse=True,
        )
