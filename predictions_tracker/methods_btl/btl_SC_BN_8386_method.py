# from typing import Dict, List, Any
from typing import Any, Dict, List

from .base import BaseMakeResult, BasePredictionMethod

class Btl_SC_BN_8386_01LotoMethod(BasePredictionMethod, BaseMakeResult):
    def get_code(self): return "btl_sc_bn_8386_01"
    def get_name(self): return "SC_BN_8386_01 2 nháy"
    def get_description(self): return "Tổng từ giải 5.4.2 và giải 6.1.1"
    def calculate(self, data): return self._make_result(data, [('giai_5_4', 1)], [('giai_6_1', 0)], reverse=True)

class Btl_SC_BN_8386_02LotoMethod(BasePredictionMethod, BaseMakeResult):
    def get_code(self): return "btl_sc_bn_8386_02"
    def get_name(self): return "SC_BN_8386_02"
    def get_description(self): return "Tổng từ giải giai_db.3 + 1.1.3 và giải 3.2.3 + 3.5.3"
    def calculate(self, data): return self._make_result(data, [('giai_db', 2), ('giai_1', 2)], [('giai_3_2', 2), ('giai_3_5', 2)], reverse=True)

class Btd_SC_BN_8386_03LotoMethod(BasePredictionMethod, BaseMakeResult):
    def get_code(self): return "btd_sc_bn_8386_03"
    def get_name(self): return "SC_BN_8386_03 đb"
    def get_description(self): return "Tổng từ giải 7.3.1 + 7.3.2 và giải 5.6.2 + 5.6.3"
    def calculate(self, data): return self._make_result(data, [('giai_7_3', 0), ('giai_7_3', 1)], [('giai_5_6', 1), ('giai_5_6', 2)], reverse=True)

class Btd_SC_BN_8386_04LotoMethod(BasePredictionMethod, BaseMakeResult):
    def get_code(self): return "btd_sc_bn_8386_04"
    def get_name(self): return "SC_BN_8386_04 đb"
    def get_description(self): return "Tổng từ giải 3.1.1 + 3.1.2 và giải 3.6.4 + 3.6.5"
    def calculate(self, data): return self._make_result(data, [('giai_3_1', 0), ('giai_3_1', 1)], [('giai_3_6', 3), ('giai_3_6', 4)], reverse=True)
    
class Btd_SC_BN_8386_05LotoMethod(BasePredictionMethod, BaseMakeResult):
    def get_code(self): return "btd_sc_bn_8386_05"
    def get_name(self): return "SC_BN_8386_05 đb"
    def get_description(self): return "Tổng từ giải 7.1.1 và giải 7.2.1"
    def calculate(self, data): return self._make_result(data, [('giai_7_1', 0)], [('giai_7_2', 0)], reverse=True)

class Btd_SC_BN_8386_06LotoMethod(BasePredictionMethod, BaseMakeResult):
    def get_code(self): return "btd_sc_bn_8386_06"
    def get_name(self): return "SC_BN_8386_06 đb"
    def get_description(self): return "Tổng từ giải 5.5.2 và giải 3.5.5"
    def calculate(self, data): return self._make_result(data, [('giai_5_5', 1)], [('giai_3_5', 4)], reverse=True)

class Btd_SC_BN_8386_07LotoMethod(BasePredictionMethod, BaseMakeResult):
    def get_code(self): return "btd_sc_bn_8386_07"
    def get_name(self): return "SC_BN_8386_07 đb"
    def get_description(self): return "Tổng từ giải 7.4.2 và giải 7.2.2"
    def calculate(self, data): return self._make_result(data, [('giai_7_4', 1)], [('giai_7_2', 1)], reverse=True)