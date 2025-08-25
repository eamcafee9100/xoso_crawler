# from typing import Dict, List, Any
from typing import Any, Dict, List

from .base import BaseMakeResult, BasePredictionMethod


class Btl_TN_k3N_01LotoMethod(BasePredictionMethod, BaseMakeResult):
    def get_code(self):
        return "btl_tn_k3n_01"

    def get_name(self):
        return "BTL TN_k3N 01"

    def get_description(self):
        return "Tổng từ giải giai_db.2 và giải giai_db.3"

    def calculate(self, data):
        return self._make_result(data, [("giai_db", 1)], [("giai_db", 2)], reverse=True)


class Btl_TN_k3N_02LotoMethod(BasePredictionMethod, BaseMakeResult):
    def get_code(self):
        return "btl_tn_k3n_02"

    def get_name(self):
        return "BTL TN_k3N 02"

    def get_description(self):
        return "Tổng từ giải giai_db.4 và giải giai_db.5"

    def calculate(self, data):
        return self._make_result(data, [("giai_db", 3)], [("giai_db", 4)], reverse=True)


class Btl_TN_k3N_02_bLotoMethod(BasePredictionMethod, BaseMakeResult):
    def get_code(self):
        return "btl_tn_k3n_02_b"

    def get_name(self):
        return "BTL TN_k3N 02_b"

    def get_description(self):
        return "Tổng từ giải 7.1.1 + 7.1.2 và giải 7.4.2"

    def calculate(self, data):
        return self._make_result(
            data, [("giai_7_1", 0), ("giai_7_1", 1)], [("giai_7_4", 1)], reverse=True
        )


class Btl_TN_k3N_03LotoMethod(BasePredictionMethod, BaseMakeResult):
    def get_code(self):
        return "btl_tn_k3n_03"

    def get_name(self):
        return "BTL TN_k3N 03"

    def get_description(self):
        return "Tổng từ giải 7.2.1 và giải 7.3.1"

    def calculate(self, data):
        return self._make_result(
            data, [("giai_7_2", 0)], [("giai_7_3", 0)], reverse=True
        )


class Btl_TN_k3N_04LotoMethod(BasePredictionMethod, BaseMakeResult):
    def get_code(self):
        return "btl_tn_k3n_04"

    def get_name(self):
        return "BTL TN_k3N 04"

    def get_description(self):
        return "Tổng từ giải 5.2.3 + 5.2.4 và giải 5.2.1 + 5.2.2"

    def calculate(self, data):
        return self._make_result(
            data,
            [("giai_5_2", 2), ("giai_5_2", 3)],
            [("giai_5_2", 0), ("giai_5_2", 1)],
            reverse=True,
        )


class Btl_TN_k3N_05LotoMethod(BasePredictionMethod, BaseMakeResult):
    def get_code(self):
        return "btl_tn_k3n_05"

    def get_name(self):
        return "BTL TN_k3N 05"

    def get_description(self):
        return "Tổng từ giải 3.2.1 và giải 5.1.1"

    def calculate(self, data):
        return self._make_result(
            data, [("giai_3_2", 0)], [("giai_5_1", 0)], reverse=True
        )


class Btl_TN_k3N_06LotoMethod(BasePredictionMethod, BaseMakeResult):
    def get_code(self):
        return "btl_tn_k3n_06"

    def get_name(self):
        return "BTL TN_k3N 06"

    def get_description(self):
        return "Tổng từ giải 4.1.2 và giải 6.1.1"

    def calculate(self, data):
        return self._make_result(
            data, [("giai_4_1", 1)], [("giai_6_1", 0)], reverse=True
        )


class Btl_TN_k3N_07LotoMethod(BasePredictionMethod, BaseMakeResult):
    def get_code(self):
        return "btl_tn_k3n_07"

    def get_name(self):
        return "BTL TN_k3N 07"

    def get_description(self):
        return "Tổng từ giải 3.6.4 và giải 4.4.4"

    def calculate(self, data):
        return self._make_result(
            data, [("giai_3_6", 3)], [("giai_4_4", 3)], reverse=True
        )


class Btl_TN_k3N_08LotoMethod(BasePredictionMethod, BaseMakeResult):
    def get_code(self):
        return "btl_tn_k3n_08"

    def get_name(self):
        return "BTL TN_k3N 08"

    def get_description(self):
        return "Tổng từ giải 3.1.3 và giải 6.2.1"

    def calculate(self, data):
        return self._make_result(
            data, [("giai_3_1", 2)], [("giai_6_2", 0)], reverse=True
        )


class Btl_TN_k3N_09LotoMethod(BasePredictionMethod, BaseMakeResult):
    def get_code(self):
        return "btl_tn_k3n_09"

    def get_name(self):
        return "BTL TN_k3N 09"

    def get_description(self):
        return "Tổng từ giải 5.1.1 và giải 5.4.3"

    def calculate(self, data):
        return self._make_result(
            data, [("giai_5_1", 0)], [("giai_5_4", 2)], reverse=True
        )


class Btl_TN_k3N_10LotoMethod(BasePredictionMethod, BaseMakeResult):
    def get_code(self):
        return "btl_tn_k3n_10"

    def get_name(self):
        return "BTL TN_k3N 10"

    def get_description(self):
        return "Tổng từ giải 2.1.5 và giải 4.3.4"

    def calculate(self, data):
        return self._make_result(
            data, [("giai_2_1", 4)], [("giai_4_3", 3)], reverse=True
        )


class Btl_TN_k3N_11LotoMethod(BasePredictionMethod, BaseMakeResult):
    def get_code(self):
        return "btl_tn_k3n_11"

    def get_name(self):
        return "BTL TN_k3N 11"

    def get_description(self):
        return "Tổng từ giải giai_db.2 và giải 3.6.1"

    def calculate(self, data):
        return self._make_result(
            data, [("giai_db", 1)], [("giai_3_6", 0)], reverse=True
        )


class Btl_TN_k3N_12LotoMethod(BasePredictionMethod, BaseMakeResult):
    def get_code(self):
        return "btl_tn_k3n_12"

    def get_name(self):
        return "BTL TN_k3N 12"

    def get_description(self):
        return "Tổng từ giải 4.1.2 và giải 5.3.4"

    def calculate(self, data):
        return self._make_result(
            data, [("giai_4_1", 1)], [("giai_5_3", 3)], reverse=True
        )


class Btl_TN_k3N_13LotoMethod(BasePredictionMethod, BaseMakeResult):
    def get_code(self):
        return "btl_tn_k3n_13"

    def get_name(self):
        return "BTL TN_k3N 13"

    def get_description(self):
        return "Tổng từ giải 7.1.1 và giải 4.1.3"

    def calculate(self, data):
        return self._make_result(
            data, [("giai_7_1", 0)], [("giai_4_1", 2)], reverse=True
        )


class Btl_TN_k3N_14LotoMethod(BasePredictionMethod, BaseMakeResult):
    def get_code(self):
        return "btl_tn_k3n_14"

    def get_name(self):
        return "BTL TN_k3N 14"

    def get_description(self):
        return "Tổng từ giải 3.4.5 và giải 5.2.2"

    def calculate(self, data):
        return self._make_result(
            data, [("giai_3_4", 4)], [("giai_5_2", 1)], reverse=True
        )


class Btl_TN_k3N_15LotoMethod(BasePredictionMethod, BaseMakeResult):
    def get_code(self):
        return "btl_tn_k3n_15"

    def get_name(self):
        return "BTL TN_k3N 15"

    def get_description(self):
        return "Tổng từ giải 3.4.2 và giải 5.6.2"

    def calculate(self, data):
        return self._make_result(
            data, [("giai_3_4", 1)], [("giai_5_6", 1)], reverse=True
        )


class Btl_TN_k3N_16LotoMethod(BasePredictionMethod, BaseMakeResult):
    def get_code(self):
        return "btl_tn_k3n_16"

    def get_name(self):
        return "BTL TN_k3N 16"

    def get_description(self):
        return "Tổng từ giải 3.2.1 và giải 7.2.1"

    def calculate(self, data):
        return self._make_result(
            data, [("giai_3_2", 0)], [("giai_7_2", 0)], reverse=True
        )


class Btl_TN_k3N_17LotoMethod(BasePredictionMethod, BaseMakeResult):
    def get_code(self):
        return "btl_tn_k3n_17"

    def get_name(self):
        return "BTL TN_k3N 17"

    def get_description(self):
        return "Tổng từ giải giai_db.2 và giải 4.1.1"

    def calculate(self, data):
        return self._make_result(
            data, [("giai_db", 1)], [("giai_4_1", 0)], reverse=True
        )


class Btl_TN_k3N_18LotoMethod(BasePredictionMethod, BaseMakeResult):
    def get_code(self):
        return "btl_tn_k3n_18"

    def get_name(self):
        return "BTL TN_k3N 18"

    def get_description(self):
        return "Tổng từ giải 6.1.2 và giải 7.2.1"

    def calculate(self, data):
        return self._make_result(
            data, [("giai_6_1", 1)], [("giai_7_2", 0)], reverse=True
        )


class Btl_TN_k3N_19LotoMethod(BasePredictionMethod, BaseMakeResult):
    def get_code(self):
        return "btl_tn_k3n_19"

    def get_name(self):
        return "BTL TN_k3N 19"

    def get_description(self):
        return "Tổng từ giải 7.2.1 + giải 7.2.2 và giải 3.1.3"

    def calculate(self, data):
        return self._make_result(
            data, [("giai_7_2", 0), ("giai_7_2", 1)], [("giai_3_1", 2)], reverse=True
        )


class Btl_TN_k3N_20LotoMethod(BasePredictionMethod, BaseMakeResult):
    def get_code(self):
        return "btl_tn_k3n_20"

    def get_name(self):
        return "BTL TN_k3N 20"

    def get_description(self):
        return "Tổng từ giải 6.1.2 và giải 6.3.1"

    def calculate(self, data):
        return self._make_result(
            data, [("giai_6_1", 1)], [("giai_6_3", 0)], reverse=True
        )


class Btl_TN_k3N_21LotoMethod(BasePredictionMethod, BaseMakeResult):
    def get_code(self):
        return "btl_tn_k3n_21"

    def get_name(self):
        return "BTL TN_k3N 21"

    def get_description(self):
        return "Tổng từ giải 3.2.1 + 3.2.2 và giải 3.2.3"

    def calculate(self, data):
        return self._make_result(
            data, [("giai_3_2", 0), ("giai_3_2", 1)], [("giai_3_2", 2)], reverse=True
        )


class Btl_TN_k3N_22LotoMethod(BasePredictionMethod, BaseMakeResult):
    def get_code(self):
        return "btl_tn_k3n_22"

    def get_name(self):
        return "STL TN_k3N 22"

    def get_description(self):
        return "Tổng từ giải 3.1.1 và giải 5.1.2 + 5.1.3"

    def calculate(self, data):
        return self._make_result(
            data, [("giai_3_1", 0)], [("giai_5_1", 1), ("giai_5_1", 2)], reverse=True
        )


class Btl_TN_k3N_23LotoMethod(BasePredictionMethod, BaseMakeResult):
    def get_code(self):
        return "btl_tn_k3n_23"

    def get_name(self):
        return "STL TN_k3N 23"

    def get_description(self):
        return "Tổng từ giải đặc biệt giai_db.1 và giai_db.5"

    def calculate(self, data):
        return self._make_result(data, [("giai_db", 0)], [("giai_db", 4)], reverse=True)


class Btl_TN_k3N_24LotoMethod(BasePredictionMethod, BaseMakeResult):
    def get_code(self):
        return "btl_tn_k3n_24"

    def get_name(self):
        return "STL TN_k3N 24"

    def get_description(self):
        return "Tổng từ giải 5.6.4 và 6.1.1"

    def calculate(self, data):
        return self._make_result(
            data, [("giai_5_6", 3)], [("giai_6_1", 0)], reverse=True
        )


class Btl_TN_k3N_25LotoMethod(BasePredictionMethod, BaseMakeResult):
    def get_code(self):
        return "btl_tn_k3n_25"

    def get_name(self):
        return "STL TN_k3N 25"

    def get_description(self):
        return "Tổng từ giải 1.1.4 và 3.5.1"

    def calculate(self, data):
        return self._make_result(data, [("giai_1", 3)], [("giai_3_5", 0)], reverse=True)


class Btl_TN_k3N_26LotoMethod(BasePredictionMethod, BaseMakeResult):
    def get_code(self):
        return "btl_tn_k3n_26"

    def get_name(self):
        return "STL TN_k3N 26"

    def get_description(self):
        return "Tổng từ giải đặc biệt giai_db.5 và giai_2.1.1"

    def calculate(self, data):
        return self._make_result(
            data, [("giai_db", 4)], [("giai_2_1", 0)], reverse=True
        )


class Btl_TN_k3N_27LotoMethod(BasePredictionMethod, BaseMakeResult):
    def get_code(self):
        return "btl_tn_k3n_27"

    def get_name(self):
        return "STL TN_k3N 27"

    def get_description(self):
        return "Tổng từ giải 2.1.2 + 3.3.2 + 3.3.5 và 2.2.3 + 3.5.4 + 3.6.4"

    def calculate(self, data):
        return self._make_result(
            data,
            [("giai_2_1", 1), ("giai_3_3", 1), ("giai_3_3", 4)],
            [("giai_2_2", 2), ("giai_3_5", 3), ("giai_3_6", 3)],
            reverse=True,
        )


class Btl_TN_k3N_28LotoMethod(BasePredictionMethod, BaseMakeResult):
    def get_code(self):
        return "btl_tn_k3n_28"

    def get_name(self):
        return "STL TN_k3N 28 2 nháy"

    def get_description(self):
        return "Tổng từ giải 4.1.1 và 4.3.4"

    def calculate(self, data):
        return self._make_result(
            data, [("giai_4_1", 0)], [("giai_4_3", 3)], reverse=True
        )


class Btl_TN_k3N_29LotoMethod(BasePredictionMethod, BaseMakeResult):
    def get_code(self):
        return "btl_tn_k3n_29"

    def get_name(self):
        return "STL TN_k3N 29 2 nháy"

    def get_description(self):
        return "Tổng từ giải 5.3.2 và 5.6.2"

    def calculate(self, data):
        return self._make_result(
            data, [("giai_5_3", 1)], [("giai_5_6", 1)], reverse=True
        )


class Btl_TN_k3N_30LotoMethod(BasePredictionMethod, BaseMakeResult):
    def get_code(self):
        return "btl_tn_k3n_30"

    def get_name(self):
        return "STL TN_k3N 30 2 nháy"

    def get_description(self):
        return "Tổng từ giải đặc biệt giai_db.5 và giai_2.1.1"

    def calculate(self, data):
        return self._make_result(
            data, [("giai_db", 4)], [("giai_2_1", 0)], reverse=True
        )


class Btl_TN_k3N_31LotoMethod(BasePredictionMethod, BaseMakeResult):
    def get_code(self):
        return "btl_tn_k3n_31"

    def get_name(self):
        return "STL TN_k3N 31 2 nháy"

    def get_description(self):
        return "Tổng từ giải 2.2.5 và 6.1.1"

    def calculate(self, data):
        return self._make_result(
            data, [("giai_2_2", 4)], [("giai_6_1", 0)], reverse=True
        )


class Btl_TN_k3N_32LotoMethod(BasePredictionMethod, BaseMakeResult):
    def get_code(self):
        return "btl_tn_k3n_32"

    def get_name(self):
        return "STL TN_k3N 32 2 nháy"

    def get_description(self):
        return "Tổng từ giải 4.4.1 và 5.3.1"

    def calculate(self, data):
        return self._make_result(
            data, [("giai_4_4", 0)], [("giai_5_3", 0)], reverse=True
        )


class Btl_TN_k3N_33LotoMethod(BasePredictionMethod, BaseMakeResult):
    def get_code(self):
        return "btl_tn_k3n_33"

    def get_name(self):
        return "STL TN_k3N 33 2 nháy"

    def get_description(self):
        return "Tổng từ giải 3.2.2 và 5.3.2"

    def calculate(self, data):
        return self._make_result(
            data, [("giai_3_2", 1)], [("giai_5_3", 1)], reverse=True
        )


class Btl_TN_k3N_34LotoMethod(BasePredictionMethod, BaseMakeResult):
    def get_code(self):
        return "btl_tn_k3n_34"

    def get_name(self):
        return "STL TN_k3N 34 "

    def get_description(self):
        return "Tổng từ giải 3.6.3 và 4.2.2"

    def calculate(self, data):
        return self._make_result(
            data, [("giai_3_6", 2)], [("giai_4_2", 1)], reverse=True
        )


class Btl_TN_k3N_35LotoMethod(BasePredictionMethod, BaseMakeResult):
    def get_code(self):
        return "btl_tn_k3n_35"

    def get_name(self):
        return "STL TN_k3N 35 "

    def get_description(self):
        return "Tổng từ giải 3.3.4 và 4.2.2"

    def calculate(self, data):
        return self._make_result(
            data, [("giai_3_3", 3)], [("giai_4_2", 1)], reverse=True
        )


class Btl_TN_k3N_36LotoMethod(BasePredictionMethod, BaseMakeResult):
    def get_code(self):
        return "btl_tn_k3n_36"

    def get_name(self):
        return "STL TN_k3N 36 2 nháy"

    def get_description(self):
        return "Tổng từ giải 4.1.1 và 4.3.1"

    def calculate(self, data):
        return self._make_result(
            data, [("giai_4_1", 0)], [("giai_4_3", 0)], reverse=True
        )

