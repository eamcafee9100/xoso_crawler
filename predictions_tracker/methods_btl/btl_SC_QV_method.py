# from typing import Dict, List, Any
from typing import Any, Dict, List

from .base import BaseMakeResult, BasePredictionMethod

class Btl_SC_QV_01LotoMethod(BasePredictionMethod, BaseMakeResult):
    def get_code(self): return "btl_sc_qv_01"
    def get_name(self): return "SC_QV 01"
    def get_description(self): return "Tổng từ giải 5.6.2 + 5.6.3 và giải 7.3.1 + 7.3.2"
    def calculate(self, data): return self._make_result(data, [('giai_5_6', 1), ('giai_5_6', 2)], [('giai_7_3', 0), ('giai_7_3', 1)], reverse=True)

class Btl_SC_QV_02LotoMethod(BasePredictionMethod, BaseMakeResult):
    def get_code(self): return "btl_sc_qv_02"
    def get_name(self): return "SC_QV 02"
    def get_description(self): return "Tổng từ giải 2.1.1 + 2.1.2 và giải 2.2.3"
    def calculate(self, data): return self._make_result(data, [('giai_2_1', 0), ('giai_2_1', 1)], [('giai_2_2', 2)], reverse=True)

class Btd_SC_QV_03LotoMethod(BasePredictionMethod, BaseMakeResult):
    def get_code(self): return "btd_sc_qv_03"
    def get_name(self): return "SC_QV 03 đb"
    def get_description(self): return "Tổng từ giải 7.3.1 + 7.3.2 và giải 5.6.2 + 5.6.3"
    def calculate(self, data): return self._make_result(data, [('giai_7_3', 0), ('giai_7_3', 1)], [('giai_5_6', 1), ('giai_5_6', 2)], reverse=True)
    
class Btd_SC_QV_04LotoMethod(BasePredictionMethod, BaseMakeResult):
    def get_code(self): return "btd_sc_qv_04"
    def get_name(self): return "SC_QV 04 đb"
    def get_description(self): return "Tổng từ giải 3.1.1 + 3.1.2 và giải 3.6.4 + 3.6.5"
    def calculate(self, data): return self._make_result(data, [('giai_3_1', 0), ('giai_3_1', 1)], [('giai_3_6', 3), ('giai_3_6', 4)], reverse=True)
    

class Btd_SC_QV_05LotoMethod(BasePredictionMethod, BaseMakeResult):
    def get_code(self): return "btd_sc_qv_05"
    def get_name(self): return "SC_QV 05 đb"
    def get_description(self): return "Tổng từ giải 5.4.4 và giải 5.2.4"
    def calculate(self, data): return self._make_result(data, [('giai_5_4', 3)], [('giai_5_2', 3)], reverse=True)
  
class Btd_SC_QV_06LotoMethod(BasePredictionMethod, BaseMakeResult):
    def get_code(self): return "btd_sc_qv_06"
    def get_name(self): return "SC_QV 06"
    def get_description(self): return "Tổng từ giải giai_db.1 + giia_db.2 và giải 2.1.4 + 2.1.5"
    def calculate(self, data): return self._make_result(data, [('giai_db', 0), ('giai_db', 1)], [('giai_2_1', 3), ('giai_2_1', 4)], reverse=True)

class Btd_SC_QV_07LotoMethod(BasePredictionMethod, BaseMakeResult):
    def get_code(self): return "btd_sc_qv_07"
    def get_name(self): return "SC_QV 07"
    def get_description(self): return "Tổng từ giải 4.1.1 và 4.4.4"
    def calculate(self, data): return self._make_result(data, [('giai_4_1', 0)], [('giai_4_4', 3)], reverse=True)