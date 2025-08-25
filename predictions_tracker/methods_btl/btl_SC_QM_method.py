# from typing import Dict, List, Any
from typing import Any, Dict, List

from .base import BaseMakeResult, BasePredictionMethod


class Btl_SC_QM_01LotoMethod(BasePredictionMethod, BaseMakeResult):
    def get_code(self): return "btl_sc_QM_01"
    def get_name(self): return "SC_QM 01"
    def get_description(self): return "Tổng từ giải 1.1.4 + 3.3.4 + 5.2.2 và giải 2.2.1 + 3.2.2 + 3.6.3"
    def calculate(self, data): return self._make_result(data, [('giai_1', 3), ('giai_3_3', 3), ('giai_5_2', 1)], [('giai_2_2', 0), ('giai_3_2', 1), ('giai_3_6', 2)],reverse=True)

class Btl_SC_QM_02LotoMethod(BasePredictionMethod, BaseMakeResult):
    def get_code(self): return "btl_sc_QM_02"
    def get_name(self): return "SC_QM 02"
    def get_description(self): return "Tổng từ giải 1.1.5 + 5.6.1 + 7.3.2 và giải 5.4.3 + 6.2.1 + 6.2.3"
    def calculate(self, data): return self._make_result(data, [('giai_1', 4), ('giai_5_6', 0), ('giai_7_3', 1)], [('giai_5_4', 2), ('giai_6_2', 0), ('giai_6_2', 2)],reverse=True)

class Btd_SC_QM_03LotoMethod(BasePredictionMethod, BaseMakeResult):
    def get_code(self): return "btd_sc_QM_03"
    def get_name(self): return "SC_QM 03 ĐB"
    def get_description(self): return "Tổng từ giải 4.4.1 + 5.4.1 + 6.2.2 và giải 3.2.4 + 3.6.3 + 7.2.2"
    def calculate(self, data): return self._make_result(data, [('giai_4_4', 0), ('giai_5_4', 0), ('giai_6_2', 1)], [('giai_3_2', 3), ('giai_3_6', 2), ('giai_7_2', 1)],reverse=True)

class Btd_SC_QM_04LotoMethod(BasePredictionMethod, BaseMakeResult):
    def get_code(self): return "btd_sc_QM_04"
    def get_name(self): return "SC_QM 04"
    def get_description(self): return "Tổng từ giải 2.1.1 + 5.1.1 + 5.3.3 và giải 3.2.2 + 3.4.4 + 7.1.2"
    def calculate(self, data): return self._make_result(data, [('giai_2_1', 0), ('giai_5_1', 0), ('giai_5_3', 2)], [('giai_3_2', 1), ('giai_3_4', 3), ('giai_7_1', 1)],reverse=True)

class Btd_SC_QM_05LotoMethod(BasePredictionMethod, BaseMakeResult):
    def get_code(self): return "btd_sc_QM_05"
    def get_name(self): return "SC_QM 05"
    def get_description(self): return "Tổng từ giải 3.4.3 + 4.1.2 + 5.1.3 và giải 3.4.5 + 5.2.1 + 7.2.2"
    def calculate(self, data): return self._make_result(data, [('giai_3_4', 2), ('giai_5_1', 1), ('giai_5_1', 2)], [('giai_3_4', 4), ('giai_5_2', 0), ('giai_7_2', 1)],reverse=True)

class Btd_SC_QM_06LotoMethod(BasePredictionMethod, BaseMakeResult):
    def get_code(self): return "btd_sc_QM_06"
    def get_name(self): return "SC_QM 06 xiên 3"
    def get_description(self): return "Tổng từ giải 3.4.2 + 4.2.4 + 5.2.2 và giải 5.5.2 + 5.5.4 + 5.6.1"
    def calculate(self, data): return self._make_result(data, [('giai_3_4', 1), ('giai_4_2', 3), ('giai_5_2', 1)], [('giai_5_5', 1), ('giai_5_5', 3), ('giai_5_6', 0)],reverse=True)
    
class Btd_SC_QM_07LotoMethod(BasePredictionMethod, BaseMakeResult):
    def get_code(self): return "btd_sc_QM_07"
    def get_name(self): return "SC_QM 07 đề"
    def get_description(self): return "Tổng từ giải 3.4.1 + 4.4.3 + 7.2.1 và giải 4.3.4 + 5.4.2 + 6.1.3"
    def calculate(self, data): return self._make_result(data, [('giai_3_4', 0), ('giai_4_4', 2), ('giai_7_2', 0)], [('giai_4_3', 3), ('giai_5_4', 1), ('giai_6_1', 2)],reverse=True)
    
class Btd_SC_QM_08LotoMethod(BasePredictionMethod, BaseMakeResult):
    def get_code(self): return "btd_sc_QM_08"
    def get_name(self): return "SC_QM 08"
    def get_description(self): return "Tổng từ giải 1.1.3 + 1.1.4 + 7.3.1 và giải 2.2.1 + 3.4.4 + 4.2.1"
    def calculate(self, data): return self._make_result(data, [('giai_1', 2), ('giai_1', 3), ('giai_7_3', 0)], [('giai_2_2', 0), ('giai_3_4', 3), ('giai_4_2', 0)],reverse=True)

class Btd_SC_QM_09LotoMethod(BasePredictionMethod, BaseMakeResult):
    def get_code(self): return "btd_sc_QM_09"
    def get_name(self): return "SC_QM 09"
    def get_description(self): return "Tổng từ giải 3.6.1 + 4.4.1 + 7.4.2 và giải 2.1.3 + 3.3.3 + 5.1.3"
    def calculate(self, data): return self._make_result(data, [('giai_3_6', 0), ('giai_4_4', 0), ('giai_7_4', 1)], [('giai_2_1', 2), ('giai_3_3', 2), ('giai_5_1', 2)],reverse=True)

class Btd_SC_QM_10LotoMethod(BasePredictionMethod, BaseMakeResult):
    def get_code(self): return "btd_sc_QM_10"
    def get_name(self): return "SC_QM 10 2 nháy"
    def get_description(self): return "Tổng từ giải 3.4.4 + 4.2.2 + 5.5.3 và giải 3.2.3 + 6.1.2 + 6.2.1"
    def calculate(self, data): return self._make_result(data, [('giai_3_4', 3), ('giai_4_2', 1), ('giai_5_5', 2)], [('giai_3_2', 2), ('giai_6_1', 1), ('giai_6_2', 0)],reverse=True)

class Btd_SC_QM_12LotoMethod(BasePredictionMethod, BaseMakeResult):
    def get_code(self): return "btd_sc_QM_12"
    def get_name(self): return "SC_QM 12 2 nháy"
    def get_description(self): return "Tổng từ giải 3.4.1 + 5.3.2 + 5.4.2 và giải 3.2.4 + 5.1.3 + 5.6.3"

    def calculate(self, data): return self._make_result(data, [('giai_3_4', 0), ('giai_5_4', 1), ('giai_5_3', 1)], [('giai_3_2', 3), ('giai_5_1', 3), ('giai_5_6', 2)],reverse=True)    

class Btd_SC_QM_11LotoMethod(BasePredictionMethod, BaseMakeResult):
    def get_code(self): return "btd_sc_QM_11"
    def get_name(self): return "SC_QM 11 2 nháy"
    def get_description(self): return "Tổng từ giải 3.5.3 + 4.3.1 + 4.4.3 và giải 3.3.5 + 4.4.4 + 5.2.1"
    def calculate(self, data): return self._make_result(data, [('giai_3_5', 2), ('giai_4_3', 0), ('giai_4_4', 0)], [('giai_3_3', 4), ('giai_4_4', 3), ('giai_5_2', 0)],reverse=True)

class Btd_SC_QM_13LotoMethod(BasePredictionMethod, BaseMakeResult):
    def get_code(self): return "btd_sc_QM_13"
    def get_name(self): return "SC_QM 13"
    def get_description(self): return "Tổng từ giải 3.2.2 + 4.2.3 + 4.3.1 và giải 5.1.3 + 5.4.2 + 6.1.2"
    def calculate(self, data): return self._make_result(data, [('giai_3_2', 1), ('giai_4_2', 2), ('giai_4_3', 0)], [('giai_5_1', 2), ('giai_5_4', 1), ('giai_6_1', 1)],reverse=True)

class Btd_SC_QM_14LotoMethod(BasePredictionMethod, BaseMakeResult):
    def get_code(self): return "btd_sc_QM_14"
    def get_name(self): return "SC_QM 14"
    def get_description(self): return "Tổng từ giải 3.5.2 + 5.4.1 + 5.5.3 và giải 6.3.1 + 7.1.1 + 7.4.1"
    def calculate(self, data): return self._make_result(data, [('giai_3_5', 1), ('giai_5_4', 0), ('giai_5_5', 2)], [('giai_6_3', 0), ('giai_7_1', 0), ('giai_7_4', 0)],reverse=True)    

class Btd_SC_QM_15LotoMethod(BasePredictionMethod, BaseMakeResult):
    def get_code(self): return "btd_sc_QM_15"
    def get_name(self): return "SC_QM 15"
    def get_description(self): return "Tổng từ giải 3.4.1 + 4.2.3 + 5.5.1 và giải 2.1.5 + 2.2.4 + 3.6.3"
    def calculate(self, data): return self._make_result(data, [('giai_3_4', 0), ('giai_5_5', 0), ('giai_4_2', 2)], [('giai_2_1', 4), ('giai_2_2', 3), ('giai_3_6', 2)],reverse=True)

class Btd_SC_QM_16LotoMethod(BasePredictionMethod, BaseMakeResult):
    def get_code(self): return "btd_sc_QM_16"
    def get_name(self): return "SC_QM 16"
    def get_description(self): return "Tổng từ giải 3.1.4 + 5.3.4 + 7.3.2 và giải 1.1.3 + 4.1.2 + 5.2.3"
    def calculate(self, data): return self._make_result(data, [('giai_3_1', 3), ('giai_5_3', 3), ('giai_7_3', 1)], [('giai_1', 2), ('giai_4_1', 1), ('giai_5_2', 2)],reverse=True)

class Btd_SC_QM_17LotoMethod(BasePredictionMethod, BaseMakeResult):
    def get_code(self): return "btd_sc_QM_17"
    def get_name(self): return "SC_QM 17"
    def get_description(self): return "Tổng từ giải 2.2.2 + 5.4.3 + 7.4.2 và giải 3.4.2 + 4.1.4 + 6.3.2"
    def calculate(self, data): return self._make_result(data, [('giai_2_2', 1), ('giai_5_4', 2), ('giai_7_4', 1)], [('giai_3_4', 1), ('giai_4_1', 3), ('giai_6_3', 1)],reverse=True)

class Btd_SC_QM_18LotoMethod(BasePredictionMethod, BaseMakeResult):
    def get_code(self): return "btd_sc_QM_18"
    def get_name(self): return "SC_QM 18"
    def get_description(self): return "Tổng từ giải 1.1.2 + 4.4.3 + 6.3.2 và giải 5.1.1 + 7.1.1 + 7.3.1"
    def calculate(self, data): return self._make_result(data, [('giai_1', 1), ('giai_4_4', 2), ('giai_6_3', 1)], [('giai_5_1', 0), ('giai_7_1', 0), ('giai_7_3', 0)],reverse=True)

class Btd_SC_QM_19LotoMethod(BasePredictionMethod, BaseMakeResult):
    def get_code(self): return "btd_sc_QM_19"
    def get_name(self): return "SC_QM 19 CK"
    def get_description(self): return "Tổng từ giải 2.2.3 + 3.1.4 + 3.5.2 và giải 3.1.1 + 5.2.2 + 5.2.4"
    def calculate(self, data): return self._make_result(data, [('giai_2_2', 2), ('giai_3_1', 3), ('giai_3_5', 1)], [('giai_3_1', 0), ('giai_5_2', 1), ('giai_5_2', 3)],reverse=True)

class Btd_SC_QM_20LotoMethod(BasePredictionMethod, BaseMakeResult):
    def get_code(self): return "btd_sc_QM_20"
    def get_name(self): return "SC_QM 20"
    def get_description(self): return "Tổng từ giải 3.3.1 + 3.6.1 + 7.2.1 và giải 2.1.5 + 3.3.3 + 4.3.3"
    def calculate(self, data): return self._make_result(data, [('giai_3_3', 0), ('giai_3_6', 0), ('giai_7_2', 0)], [('giai_2_1', 4), ('giai_3_3', 2), ('giai_4_3', 2)],reverse=True)



