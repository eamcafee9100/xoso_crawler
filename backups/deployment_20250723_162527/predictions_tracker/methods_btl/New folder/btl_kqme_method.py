# from typing import Dict, List, Any
from typing import Any, Dict, List

from .base import BaseMakeResult, BasePredictionMethod


class Btl_kqme_01LotoMethod(BasePredictionMethod, BaseMakeResult):
    def get_code(self): return "btl_kqme_01"
    def get_name(self): return "Bạch thủ lô kqme 01"
    def get_description(self): return "Tổng từ giải 3.4.3 và giải 4.1.3"
    def calculate(self, data): return self._make_result(data, [('giai_3_4', 2)], [('giai_4_1', 2)], reverse=True)

class Btl_kqme_02LotoMethod(BasePredictionMethod, BaseMakeResult):
    def get_code(self): return "btl_kqme_02"
    def get_name(self): return "Bạch thủ lô kqme 02"
    def get_description(self): return "Tổng từ giải 3.6.2 và giải 5.4.4"
    def calculate(self, data): return self._make_result(data, [('giai_3_6', 1)], [('giai_5_4', 3)], reverse=True)

class Btl_kqme_03LotoMethod(BasePredictionMethod, BaseMakeResult):
    def get_code(self): return "btl_kqme_03"
    def get_name(self): return "Bạch thủ lô kqme 03"
    def get_description(self): return "Tổng từ giải 2.1.3 và giải 5.3.2"
    def calculate(self, data): return self._make_result(data, [('giai_2_1', 2)], [('giai_5_3', 1)], reverse=True)

class Btl_kqme_04LotoMethod(BasePredictionMethod, BaseMakeResult):
    def get_code(self): return "btl_kqme_04"
    def get_name(self): return "Bạch thủ lô kqme 04"
    def get_description(self): return "Tổng từ giải 1.1.2 và giải 3.1.3"
    def calculate(self, data): return self._make_result(data, [('giai_1', 1)], [('giai_3_1', 2)], reverse=True)

class Btl_kqme_05LotoMethod(BasePredictionMethod, BaseMakeResult):
    def get_code(self): return "btl_kqme_05"
    def get_name(self): return "Bạch thủ lô kqme 05"
    def get_description(self): return "Tổng từ giải 3.2.5 và giải 4.4.3"
    def calculate(self, data): return self._make_result(data, [('giai_3_2', 4)], [('giai_4_4', 2)], reverse=True)

class Btl_kqme_06LotoMethod(BasePredictionMethod, BaseMakeResult):
    def get_code(self): return "btl_kqme_06"
    def get_name(self): return "Bạch thủ lô kqme 06"
    def get_description(self): return "Tổng từ giải 5.2.2 và giải 6.2.3"
    def calculate(self, data): return self._make_result(data, [('giai_5_2', 1)], [('giai_6_2', 2)], reverse=True)

class Btl_kqme_07LotoMethod(BasePredictionMethod, BaseMakeResult):
    def get_code(self): return "btl_kqme_07"
    def get_name(self): return "Bạch thủ lô kqme 07"
    def get_description(self): return "Tổng từ giải 3.1.3 và giải 7.1.2"
    def calculate(self, data): return self._make_result(data, [('giai_3_1', 2)], [('giai_7_1', 1)], reverse=True)

class Btl_kqme_08LotoMethod(BasePredictionMethod, BaseMakeResult):
    def get_code(self): return "btl_kqme_08"
    def get_name(self): return "Bạch thủ lô kqme 08"
    def get_description(self): return "Tổng từ giải 2.2.5 và giải 3.2.4"
    def calculate(self, data): return self._make_result(data, [('giai_2_2', 4)], [('giai_3_2', 3)], reverse=True)

class Btl_kqme_09LotoMethod(BasePredictionMethod, BaseMakeResult):
    def get_code(self): return "btl_kqme_09"
    def get_name(self): return "Bạch thủ lô kqme 09"
    def get_description(self): return "Tổng từ giải 4.1.3 và giải 5.6.4"
    def calculate(self, data): return self._make_result(data, [('giai_4_1', 2)], [('giai_5_6', 3)], reverse=True)

class Btl_kqme_10LotoMethod(BasePredictionMethod, BaseMakeResult):
    def get_code(self): return "btl_kqme_10"
    def get_name(self): return "Bạch thủ lô kqme 10"
    def get_description(self): return "Tổng từ giải 5.4.3 và giải 5.5.2"
    def calculate(self, data): return self._make_result(data, [('giai_5_4', 2)], [('giai_5_5', 1)], reverse=True)

class Btl_kqme_11LotoMethod(BasePredictionMethod, BaseMakeResult):
    def get_code(self): return "btl_kqme_11"
    def get_name(self): return "Bạch thủ lô kqme 11"
    def get_description(self): return "Tổng từ giải 3.2.2 và giải 5.2.4"
    def calculate(self, data): return self._make_result(data, [('giai_3_2', 1)], [('giai_5_2', 3)], reverse=True)

class Btl_kqme_12LotoMethod(BasePredictionMethod, BaseMakeResult):
    def get_code(self): return "btl_kqme_12"
    def get_name(self): return "Bạch thủ lô kqme 12"
    def get_description(self): return "Tổng từ giải 3.2.4 và giải 3.4.2"
    def calculate(self, data): return self._make_result(data, [('giai_3_2', 3)], [('giai_3_4', 1)], reverse=True)

class Btl_kqme_13LotoMethod(BasePredictionMethod, BaseMakeResult):
    def get_code(self): return "btl_kqme_13"
    def get_name(self): return "Bạch thủ lô kqme 13"
    def get_description(self): return "Tổng từ giải 5.2.4 và giải 5.3.2"
    def calculate(self, data): return self._make_result(data, [('giai_5_2', 3)], [('giai_5_3', 1)], reverse=True)

class Btl_kqme_14LotoMethod(BasePredictionMethod, BaseMakeResult):
    def get_code(self): return "btl_kqme_14"
    def get_name(self): return "Bạch thủ lô kqme 14"
    def get_description(self): return "Tổng từ giải 4.2.2 và giải 6.3.1"
    def calculate(self, data): return self._make_result(data, [('giai_4_2', 1)], [('giai_6_3', 0)], reverse=True)

class Btl_kqme_15LotoMethod(BasePredictionMethod, BaseMakeResult):
    def get_code(self): return "btl_kqme_15"
    def get_name(self): return "Bạch thủ lô kqme 15"
    def get_description(self): return "Tổng từ giải 5.1.4 và giải 7.4.1"
    def calculate(self, data): return self._make_result(data, [('giai_5_1', 3)], [('giai_7_4', 0)], reverse=True)

class Btl_kqme_16LotoMethod(BasePredictionMethod, BaseMakeResult):
    def get_code(self): return "btl_kqme_16"
    def get_name(self): return "Bạch thủ lô kqme 16"
    def get_description(self): return "Tổng từ giải 3.2.2 và giải 4.3.2"
    def calculate(self, data): return self._make_result(data, [('giai_3_2', 1)], [('giai_4_3', 1)], reverse=True)

class Btl_kqme_17LotoMethod(BasePredictionMethod, BaseMakeResult):
    def get_code(self): return "btl_kqme_17"
    def get_name(self): return "Bạch thủ lô kqme 17"
    def get_description(self): return "Tổng từ giải 4.1.3 và giải 4.1.4"
    def calculate(self, data): return self._make_result(data, [('giai_4_1', 2)], [('giai_4_1', 3)], reverse=True)

class Btl_kqme_18LotoMethod(BasePredictionMethod, BaseMakeResult):
    def get_code(self): return "btl_kqme_18"
    def get_name(self): return "Bạch thủ lô kqme 18"
    def get_description(self): return "Tổng từ giải 3.4.2 và giải 5.4.3"
    def calculate(self, data): return self._make_result(data, [('giai_3_4', 1)], [('giai_5_4', 2)], reverse=True)

class Btl_kqme_19LotoMethod(BasePredictionMethod, BaseMakeResult):
    def get_code(self): return "btl_kqme_19"
    def get_name(self): return "Bạch thủ lô kqme 19"
    def get_description(self): return "Tổng từ giải 3.4.3 và giải 5.4.3"
    def calculate(self, data): return self._make_result(data, [('giai_3_4', 2)], [('giai_5_4', 2)], reverse=True)

class Btl_kqme_20LotoMethod(BasePredictionMethod, BaseMakeResult):
    def get_code(self): return "btl_kqme_20"
    def get_name(self): return "Bạch thủ lô kqme 20"
    def get_description(self): return "Tổng từ giải 3.6.1 và giải 5.4.3"
    def calculate(self, data): return self._make_result(data, [('giai_3_6', 0)], [('giai_5_4', 2)], reverse=True)

class Btl_kqme_21LotoMethod(BasePredictionMethod, BaseMakeResult):
    def get_code(self): return "btl_kqme_21"
    def get_name(self): return "Bạch thủ lô kqme 21"
    def get_description(self): return "Tổng từ giải 5.1.4 và giải 5.4.2"
    def calculate(self, data): return self._make_result(data, [('giai_5_1', 3)], [('giai_5_4', 1)], reverse=True)

class Btl_kqme_22LotoMethod(BasePredictionMethod, BaseMakeResult):
    def get_code(self): return "btl_kqme_22"
    def get_name(self): return "Bạch thủ lô kqme 22"
    def get_description(self): return "Tổng từ giải 3.2.1 và giải 4.4.1"
    def calculate(self, data): return self._make_result(data, [('giai_3_2', 0)], [('giai_4_4', 0)], reverse=True)

class Btl_kqme_23LotoMethod(BasePredictionMethod, BaseMakeResult):
    def get_code(self): return "btl_kqme_23"
    def get_name(self): return "Bạch thủ lô kqme 23"
    def get_description(self): return "Tổng từ giải 3.4.5 và giải 5.4.4"
    def calculate(self, data): return self._make_result(data, [('giai_3_4', 4)], [('giai_5_4', 3)], reverse=True)

class Btl_kqme_24LotoMethod(BasePredictionMethod, BaseMakeResult):
    def get_code(self): return "btl_kqme_24"
    def get_name(self): return "Bạch thủ lô kqme 24"
    def get_description(self): return "Tổng từ giải 3.2.5 và giải 6.1.2"
    def calculate(self, data): return self._make_result(data, [('giai_3_2', 4)], [('giai_6_1', 1)], reverse=True)

class Btl_kqme_25LotoMethod(BasePredictionMethod, BaseMakeResult):
    def get_code(self): return "btl_kqme_25"
    def get_name(self): return "Bạch thủ lô kqme 25"
    def get_description(self): return "Tổng từ giải 1.1.3 và giải 3.1.5"
    def calculate(self, data): return self._make_result(data, [('giai_1', 2)], [('giai_3_1', 4)], reverse=True)

class Btl_kqme_26LotoMethod(BasePredictionMethod, BaseMakeResult):
    def get_code(self): return "btl_kqme_26"
    def get_name(self): return "Bạch thủ lô kqme 26"
    def get_description(self): return "Tổng từ giải 4.1.1 và giải 5.2.2"
    def calculate(self, data): return self._make_result(data, [('giai_4_1', 0)], [('giai_5_2', 1)], reverse=True)

class Btl_kqme_27LotoMethod(BasePredictionMethod, BaseMakeResult):
    def get_code(self): return "btl_kqme_27"
    def get_name(self): return "Bạch thủ lô kqme 27"
    def get_description(self): return "Tổng từ giải 5.4.3 và giải 7.1.1"
    def calculate(self, data): return self._make_result(data, [('giai_5_4', 2)], [('giai_7_1', 0)], reverse=True)

class Btl_kqme_28LotoMethod(BasePredictionMethod, BaseMakeResult):
    def get_code(self): return "btl_kqme_28"
    def get_name(self): return "Bạch thủ lô kqme 28"
    def get_description(self): return "Tổng từ giải 3.6.3 và giải 4.1.1"
    def calculate(self, data): return self._make_result(data, [('giai_3_6', 2)], [('giai_4_1', 0)], reverse=True)

class Btl_kqme_29LotoMethod(BasePredictionMethod, BaseMakeResult):
    def get_code(self): return "btl_kqme_29"
    def get_name(self): return "Bạch thủ lô kqme 29"
    def get_description(self): return "Tổng từ giải 2.1.5 và giải 7.2.1"
    def calculate(self, data): return self._make_result(data, [('giai_2_1', 4)], [('giai_7_2', 0)], reverse=True)

class Btl_kqme_30LotoMethod(BasePredictionMethod, BaseMakeResult):
    def get_code(self): return "btl_kqme_30"
    def get_name(self): return "Bạch thủ lô kqme 30"
    def get_description(self): return "Tổng từ giải 3.2.2 và giải 4.2.2"
    def calculate(self, data): return self._make_result(data, [('giai_3_2', 1)], [('giai_4_2', 1)], reverse=True)

class Btl_kqme_31LotoMethod(BasePredictionMethod, BaseMakeResult):
    def get_code(self): return "btl_kqme_31"
    def get_name(self): return "Bạch thủ lô kqme 31"
    def get_description(self): return "Tổng từ giải giai_db.1 và giải 4.4.1"
    def calculate(self, data): return self._make_result(data, [('giai_db', 0)], [('giai_4_4', 0)], reverse=True)

class Btl_kqme_32LotoMethod(BasePredictionMethod, BaseMakeResult):
    def get_code(self): return "btl_kqme_32"
    def get_name(self): return "Bạch thủ lô kqme 32"
    def get_description(self): return "Tổng từ giải 3.4.3 và giải 6.3.1"
    def calculate(self, data): return self._make_result(data, [('giai_3_4', 2)], [('giai_6_3', 0)], reverse=True)

class Btl_kqme_33LotoMethod(BasePredictionMethod, BaseMakeResult):
    def get_code(self): return "btl_kqme_33"
    def get_name(self): return "Bạch thủ lô kqme 33"
    def get_description(self): return "Tổng từ giải 2.1.3 và giải 3.5.2"
    def calculate(self, data): return self._make_result(data, [('giai_2_1', 2)], [('giai_3_5', 1)], reverse=True)

class Btl_kqme_34LotoMethod(BasePredictionMethod, BaseMakeResult):
    def get_code(self): return "btl_kqme_34"
    def get_name(self): return "Bạch thủ lô kqme 34"
    def get_description(self): return "Tổng từ giải 3.5.2 và giải 4.1.3"
    def calculate(self, data): return self._make_result(data, [('giai_3_5', 1)], [('giai_4_1', 2)], reverse=True)

class Btl_kqme_35LotoMethod(BasePredictionMethod, BaseMakeResult):
    def get_code(self): return "btl_kqme_35"
    def get_name(self): return "Bạch thủ lô kqme 35"
    def get_description(self): return "Tổng từ giải giai_db.4 và giải giai_db.5"
    def calculate(self, data): return self._make_result(data, [('giai_db', 3)], [('giai_db', 4)], reverse=True)

class Btl_kqme_36LotoMethod(BasePredictionMethod, BaseMakeResult):
    def get_code(self): return "btl_kqme_36"
    def get_name(self): return "Bạch thủ lô kqme 36"
    def get_description(self): return "Tổng từ giải 4.4.1 và giải 5.3.3"
    def calculate(self, data): return self._make_result(data, [('giai_4_4', 0)], [('giai_5_3', 2)], reverse=True)

class Btl_kqme_37LotoMethod(BasePredictionMethod, BaseMakeResult):
    def get_code(self): return "btl_kqme_37"
    def get_name(self): return "Bạch thủ lô kqme 37"
    def get_description(self): return "Tổng từ giải 3.2.4 và giải 4.2.1"
    def calculate(self, data): return self._make_result(data, [('giai_3_2', 3)], [('giai_4_2', 0)], reverse=True)

class Btl_kqme_38LotoMethod(BasePredictionMethod, BaseMakeResult):
    def get_code(self): return "btl_kqme_38"
    def get_name(self): return "Bạch thủ lô kqme 38"
    def get_description(self): return "Tổng từ giải 3.3.2 và giải 5.5.2"
    def calculate(self, data): return self._make_result(data, [('giai_3_3', 1)], [('giai_5_5', 1)], reverse=True)

class Btl_kqme_39LotoMethod(BasePredictionMethod, BaseMakeResult):
    def get_code(self): return "btl_kqme_39"
    def get_name(self): return "Bạch thủ lô kqme 39"
    def get_description(self): return "Tổng từ giải 5.1.3 và giải 7.2.2"
    def calculate(self, data): return self._make_result(data, [('giai_5_1', 2)], [('giai_7_2', 1)], reverse=True)

class Btl_kqme_40LotoMethod(BasePredictionMethod, BaseMakeResult):
    def get_code(self): return "btl_kqme_40"
    def get_name(self): return "Bạch thủ lô kqme 40"
    def get_description(self): return "Tổng từ giải 5.5.2 và giải 7.1.1"
    def calculate(self, data): return self._make_result(data, [('giai_5_5', 1)], [('giai_7_1', 0)], reverse=True)

class Btl_kqme_41LotoMethod(BasePredictionMethod, BaseMakeResult):
    def get_code(self): return "btl_kqme_41"
    def get_name(self): return "Bạch thủ lô kqme 41"
    def get_description(self): return "Tổng từ giải 3.2.5 và giải 5.5.3"
    def calculate(self, data): return self._make_result(data, [('giai_3_2', 4)], [('giai_5_5', 2)], reverse=True)

class Btl_kqme_42LotoMethod(BasePredictionMethod, BaseMakeResult):
    def get_code(self): return "btl_kqme_42"
    def get_name(self): return "Bạch thủ lô kqme 42"
    def get_description(self): return "Tổng từ giải 2.2.4 và giải 6.2.2"
    def calculate(self, data): return self._make_result(data, [('giai_2_2', 3)], [('giai_6_2', 1)], reverse=True)

class Btl_kqme_43LotoMethod(BasePredictionMethod, BaseMakeResult):
    def get_code(self): return "btl_kqme_43"
    def get_name(self): return "Bạch thủ lô kqme 43"
    def get_description(self): return "Tổng từ giải 2.2.4 và giải 5.4.4"
    def calculate(self, data): return self._make_result(data, [('giai_2_2', 3)], [('giai_5_4', 3)], reverse=True)

class Btl_kqme_44LotoMethod(BasePredictionMethod, BaseMakeResult):
    def get_code(self): return "btl_kqme_44"
    def get_name(self): return "Bạch thủ lô kqme 44"
    def get_description(self): return "Tổng từ giải 2.2.4 và giải 4.2.4"
    def calculate(self, data): return self._make_result(data, [('giai_2_2', 3)], [('giai_4_2', 3)], reverse=True)

class Btl_kqme_45LotoMethod(BasePredictionMethod, BaseMakeResult):
    def get_code(self): return "btl_kqme_45"
    def get_name(self): return "Bạch thủ lô kqme 45"
    def get_description(self): return "Tổng từ giải 4.3.3 và giải 7.2.2"
    def calculate(self, data): return self._make_result(data, [('giai_4_3', 2)], [('giai_7_2', 1)], reverse=True)

class Btl_kqme_46LotoMethod(BasePredictionMethod, BaseMakeResult):
    def get_code(self): return "btl_kqme_46"
    def get_name(self): return "Bạch thủ lô kqme 46"
    def get_description(self): return "Tổng từ giải 5.2.4 và giải 6.2.3"
    def calculate(self, data): return self._make_result(data, [('giai_5_2', 3)], [('giai_6_2', 2)], reverse=True)

class Btl_kqme_47LotoMethod(BasePredictionMethod, BaseMakeResult):
    def get_code(self): return "btl_kqme_47"
    def get_name(self): return "Bạch thủ lô kqme 47"
    def get_description(self): return "Tổng từ giải 6.2.3 và giải 6.3.3"
    def calculate(self, data): return self._make_result(data, [('giai_6_2', 2)], [('giai_6_3', 2)], reverse=True)

class Btl_kqme_48LotoMethod(BasePredictionMethod, BaseMakeResult):
    def get_code(self): return "btl_kqme_48"
    def get_name(self): return "Bạch thủ lô kqme 48"
    def get_description(self): return "Tổng từ giải 5.5.2 và giải 6.3.1"
    def calculate(self, data): return self._make_result(data, [('giai_5_5', 1)], [('giai_6_3', 0)], reverse=True)

class Btl_kqme_49LotoMethod(BasePredictionMethod, BaseMakeResult):
    def get_code(self): return "btl_kqme_49"
    def get_name(self): return "Bạch thủ lô kqme 49"
    def get_description(self): return "Tổng từ giải 1.1.4 và giải 2.2.4"
    def calculate(self, data): return self._make_result(data, [('giai_1', 3)], [('giai_2_2', 3)], reverse=True)

class Btl_kqme_50LotoMethod(BasePredictionMethod, BaseMakeResult):
    def get_code(self): return "btl_kqme_50"
    def get_name(self): return "Bạch thủ lô kqme 50"
    def get_description(self): return "Tổng từ giải 3.5.4 và giải 7.1.2"
    def calculate(self, data): return self._make_result(data, [('giai_3_5', 3)], [('giai_7_1', 1)], reverse=True)

class Btl_kqme_51LotoMethod(BasePredictionMethod, BaseMakeResult):
    def get_code(self): return "btl_kqme_51"
    def get_name(self): return "Bạch thủ lô kqme 51"
    def get_description(self): return "Tổng từ giải 6.1.2 và giải 7.4.2"
    def calculate(self, data): return self._make_result(data, [('giai_6_1', 1)], [('giai_7_4', 1)], reverse=True)

class Btl_kqme_52LotoMethod(BasePredictionMethod, BaseMakeResult):
    def get_code(self): return "btl_kqme_52"
    def get_name(self): return "Bạch thủ lô kqme 52"
    def get_description(self): return "Tổng từ giải 5.2.3 và giải 5.5.1"
    def calculate(self, data): return self._make_result(data, [('giai_5_2', 2)], [('giai_5_5', 0)], reverse=True)

class Btl_kqme_53LotoMethod(BasePredictionMethod, BaseMakeResult):
    def get_code(self): return "btl_kqme_53"
    def get_name(self): return "Bạch thủ lô kqme 53"
    def get_description(self): return "Tổng từ giải 6.2.3 và giải 6.3.2"
    def calculate(self, data): return self._make_result(data, [('giai_6_2', 2)], [('giai_6_3', 1)], reverse=True)

class Btl_kqme_54LotoMethod(BasePredictionMethod, BaseMakeResult):
    def get_code(self): return "btl_kqme_54"
    def get_name(self): return "Bạch thủ lô kqme 54"
    def get_description(self): return "Tổng từ giải 7.1.1 và giải 5.6.2"
    def calculate(self, data): return self._make_result(data, [('giai_7_1', 0)], [('giai_5_6', 1)], reverse=True)

class Btl_kqme_55LotoMethod(BasePredictionMethod, BaseMakeResult):
    def get_code(self): return "btl_kqme_55"
    def get_name(self): return "Bạch thủ lô kqme 55"
    def get_description(self): return "Tổng từ giải 7.1.1 và giải 7.2.2"
    def calculate(self, data): return self._make_result(data, [('giai_7_1', 0)], [('giai_7_2', 1)], reverse=True)