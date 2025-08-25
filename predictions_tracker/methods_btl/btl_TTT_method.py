# from typing import Dict, List, Any
from typing import Any, Dict, List

from .base import BaseMakeResult, BasePredictionMethod


class Btl_TTT_k3N_01LotoMethod(BasePredictionMethod, BaseMakeResult):
    def get_code(self):
        return "btl_ttt_k3n_01"

    def get_name(self):
        return "TTT_k3N 01"

    def get_description(self):
        return "Tổng từ giải giai_db.1 và giải giai_1.1"

    def calculate(self, data):
        return self._make_result(data, [("giai_db", 0)], [("giai_1", 0)], reverse=True)


class Btl_TTT_k3N_02LotoMethod(BasePredictionMethod, BaseMakeResult):
    def get_code(self):
        return "btl_ttt_k3n_02"

    def get_name(self):
        return "TTT_k3N 02"

    def get_description(self):
        return "Tổng từ giải 2.2.2 và giải 4.1.1"

    def calculate(self, data):
        return self._make_result(data, [("giai_2_2", 1)], [("giai_4_1", 0)], reverse=True)


class Btl_TTT_k3N_03LotoMethod(BasePredictionMethod, BaseMakeResult):
    def get_code(self):
        return "btl_ttt_k3n_03"

    def get_name(self):
        return "TTT_k3N 03"

    def get_description(self):
        return "Tổng từ giải 4.1.1 và giải 4.2.3"

    def calculate(self, data):
        return self._make_result(
            data, [("giai_4_1", 0)], [("giai_4_2", 2)], reverse=True
        )

class Btl_TTT_k3N_04LotoMethod(BasePredictionMethod, BaseMakeResult):
    def get_code(self):
        return "btl_ttt_k3n_04"

    def get_name(self):
        return "TTT_k3N 04"

    def get_description(self):
        return "Tổng từ giải giai_db.2 và giải 5.2.4"

    def calculate(self, data):
        return self._make_result(
            data, [("giai_db", 1)], [("giai_5_2", 3)], reverse=True
        )


class Btl_TTT_k3N_05LotoMethod(BasePredictionMethod, BaseMakeResult):
    def get_code(self):
        return "btl_ttt_k3n_05"

    def get_name(self):
        return "TTT_k3N 05"

    def get_description(self):
        return "Tổng từ giải 4.4.1 và giải 5.1.3"

    def calculate(self, data):
        return self._make_result(
            data, [("giai_4_4", 0)], [("giai_5_1", 2)], reverse=True
        )

class Btl_TTT_k3N_06LotoMethod(BasePredictionMethod, BaseMakeResult):
    def get_code(self):
        return "btl_ttt_k3n_06"

    def get_name(self):
        return "TTT_k3N 06"

    def get_description(self):
        return "Tổng từ giải 3.4.4 và giải 4.1.3"

    def calculate(self, data):
        return self._make_result(
            data, [("giai_3_4", 3)], [("giai_4_1", 2)], reverse=True
        )
