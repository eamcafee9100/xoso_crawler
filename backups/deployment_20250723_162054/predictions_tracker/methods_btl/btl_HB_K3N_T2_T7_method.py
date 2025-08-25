# from typing import Dict, List, Any
from typing import Any, Dict, List

from .base import BaseMakeResult, BasePredictionMethod

class Btl_HB_k2N_T2_01LotoMethod(BasePredictionMethod, BaseMakeResult):
    def get_code(self): return "btl_hb_k2n_t2_01"
    def get_name(self): return "BTL HB_k2N_T2 01"
    def get_description(self): return "Tổng từ giải giai_db.2 + 2.1.4 + 3.4.2 và giải 2.2.4 + 4.2.1 + 6.1.3"
    def calculate(self, data): return self._make_result(data, [('giai_db', 1), ('giai_2_1', 3), ('giai_3_4', 1)], [('giai_2_2', 3), ('giai_4_2', 0), ('giai_6_1', 2)], reverse=True)

class Btl_HB_k2N_T7_01LotoMethod(BasePredictionMethod, BaseMakeResult):
    def get_code(self): return "btl_hb_k2n_t7_01"
    def get_name(self): return "BTL HB_k2N_T7 01"
    def get_description(self): return "Tổng từ giải 3.3.4 + 4.1.1 + 5.4.1 và giải 1.1.1 + 5.3.2 + 5.5.2"
    def calculate(self, data): return self._make_result(data, [('giai_3_3', 3), ('giai_4_1', 0), ('giai_5_4', 0)], [('giai_1', 0), ('giai_5_3', 1), ('giai_5_5', 1)],reverse=True)
    
                                 