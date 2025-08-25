# from typing import Dict, List, Any
from typing import Any, Dict, List

from .base import BaseMakeResult, BasePredictionMethod


class Btl_HB_k3N_2_01LotoMethod(BasePredictionMethod, BaseMakeResult):
    def get_code(self): return "btl_hb_k3n_2_01"
    def get_name(self): return "BTL HB_k3N_2 01"
    def get_description(self): return "Tổng từ giải 3.5.1 + 3.6.1 + 5.2.2 và giải 1.1.1 + 3.3.5 + 7.3.1"
    def calculate(self, data): return self._make_result(data, [('giai_3_5', 0), ('giai_3_6', 0), ('giai_5_2', 1)], [('giai_1', 0), ('giai_3_3', 4), ('giai_7_3', 0)] ,reverse=True)

class Btl_HB_k3N_2_02LotoMethod(BasePredictionMethod, BaseMakeResult):
    def get_code(self): return "btl_hb_k3n_2_02"
    def get_name(self): return "BTL HB_k3N_2 02"
    def get_description(self): return "Tổng từ giải 5.6.3 + 6.1.3 + 7.4.2 và giải 1.1.1 + 3.5.2 + 5.3.3"
    def calculate(self, data): return self._make_result(data, [('giai_5_6', 2), ('giai_6_1', 2), ('giai_7_4', 1)], [('giai_1', 0), ('giai_3_5', 1), ('giai_5_3', 2)] ,reverse=True)

class Btl_HB_k3N_2_03LotoMethod(BasePredictionMethod, BaseMakeResult):
    def get_code(self): return "btl_hb_k3n_2_03"
    def get_name(self): return "BTL HB_k3N_2 03"
    def get_description(self): return "Tổng từ giải 3.2.1 + 3.6.2 + 6.2.2 và giải 1.1.2 + 5.1.4 + 5.2.2"
    def calculate(self, data): return self._make_result(data, [('giai_3_2', 0), ('giai_3_6', 1), ('giai_6_2', 1)], [('giai_1', 1), ('giai_5_1', 3), ('giai_5_2', 1)] ,reverse=True)

class Btl_HB_k3N_2_04LotoMethod(BasePredictionMethod, BaseMakeResult):
    def get_code(self): return "btl_hb_k3n_2_04"
    def get_name(self): return "BTL HB_k3N_2 04"
    def get_description(self): return "Tổng từ giải 5.1.1 + 6.1.2 + 7.3.1 và giải 4.1.4 + 4.2.2 + 4.4.4"
    def calculate(self, data): return self._make_result(data, [('giai_5_1', 0), ('giai_6_1', 1), ('giai_7_3', 0)], [('giai_4_1', 3), ('giai_4_2', 1), ('giai_4_4', 3)] ,reverse=True)

class Btl_HB_k3N_2_05LotoMethod(BasePredictionMethod, BaseMakeResult):
    def get_code(self): return "btl_hb_k3n_2_05"
    def get_name(self): return "BTL HB_k3N_2 05"
    def get_description(self): return "Tổng từ giải 2.1.5 + 4.2.2 + 4.3.4 và giải giai_db.3 + 3.2.2 + 5.1.2"
    def calculate(self, data): return self._make_result(data, [('giai_2_1', 4), ('giai_4_2', 1), ('giai_4_3', 3)], [('giai_db', 2), ('giai_3_2', 1), ('giai_5_1', 1)] ,reverse=True)

class Btl_HB_k3N_2_06LotoMethod(BasePredictionMethod, BaseMakeResult):
    def get_code(self): return "btl_hb_k3n_2_06"
    def get_name(self): return "BTL HB_k3N_2 06"
    def get_description(self): return "Tổng từ giải 3.4.5 + 4.4.2 + 4.4.3 và giải giai_db.3 + 3.2.2 + 5.1.2"
    def calculate(self, data): return self._make_result(data, [('giai_3_4', 4), ('giai_4_4', 1), ('giai_4_4', 2)], [('giai_db', 2), ('giai_3_2', 1), ('giai_5_1', 1)] ,reverse=True)

class Btl_HB_k3N_2_07LotoMethod(BasePredictionMethod, BaseMakeResult):
    def get_code(self): return "btl_hb_k3n_2_07"
    def get_name(self): return "BTL HB_k3N_2 07"
    def get_description(self): return "Tổng từ giải giai_db.2 + 2.2.2 + 5.3.3 và giải giai_db.3 + 5.6.2 + 6.3.2"
    def calculate(self, data): return self._make_result(data, [('giai_db', 1), ('giai_2_2', 1), ('giai_5_3', 2)], [('giai_db', 2), ('giai_5_6', 1), ('giai_6_3', 1)] ,reverse=True)

class Btl_HB_k3N_2_08LotoMethod(BasePredictionMethod, BaseMakeResult):
    def get_code(self): return "btl_hb_k3n_2_08"
    def get_name(self): return "BTL HB_k3N_2 08"
    def get_description(self): return "Tổng từ giải 3.2.3 + 4.4.1 + 5.1.4 và giải giai_db.5 + 4.2.2 + 6.2.3"
    def calculate(self, data): return self._make_result(data, [('giai_3_2', 2), ('giai_4_4', 0), ('giai_5_1', 3)], [('giai_db', 4), ('giai_4_2', 1), ('giai_6_2', 2)] ,reverse=True)

class Btl_HB_k3N_2_09LotoMethod(BasePredictionMethod, BaseMakeResult):
    def get_code(self): return "btl_hb_k3n_2_09"
    def get_name(self): return "BTL HB_k3N_2 09"
    def get_description(self): return "Tổng từ giải 3.4.5 + 6.2.1 + 6.2.3 và giải 1.1.4 + 4.2.2 + 5.3.1"
    def calculate(self, data): return self._make_result(data, [('giai_3_4', 4), ('giai_6_2', 0), ('giai_6_2', 2)], [('giai_1', 3), ('giai_4_2', 1), ('giai_5_3', 0)] ,reverse=True)

class Btl_HB_k3N_2_10LotoMethod(BasePredictionMethod, BaseMakeResult):
    def get_code(self): return "btl_hb_k3n_2_10"
    def get_name(self): return "BTL HB_k3N_2 10"
    def get_description(self): return "Tổng từ giải 4.4.3 + 5.1.2 + 6.2.3 và giải 3.3.1 + 3.5.3 + 3.6.1"
    def calculate(self, data): return self._make_result(data, [('giai_4_4', 2), ('giai_5_1', 1), ('giai_6_2', 2)], [('giai_3_3', 0), ('giai_3_5', 2), ('giai_3_6', 0)] ,reverse=True)

class Btl_HB_k3N_2_11LotoMethod(BasePredictionMethod, BaseMakeResult):
    def get_code(self): return "btl_hb_k3n_2_11"
    def get_name(self): return "BTL HB_k3N_2 11"
    def get_description(self): return "Tổng từ giải 2.1.1 + 4.2.3 + 5.1.4 và giải 3.2.3 + 4.1.3 + 4.1.4"
    def calculate(self, data): return self._make_result(data, [('giai_2_1', 0), ('giai_4_2', 2), ('giai_5_1', 3)], [('giai_3_2', 2), ('giai_4_1', 2), ('giai_4_1', 3)] ,reverse=True)