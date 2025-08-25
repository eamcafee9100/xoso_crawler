# from typing import Dict, List, Any
from .base import BasePredictionMethod, BaseMakeResult
import logging

logger = logging.getLogger(__name__)

class Btl_HoangBach01LotoMethod(BasePredictionMethod, BaseMakeResult):
    def get_code(self): return "btl_hoangbach_01"
    def get_name(self): return "Bạch thủ lô Hoàng Bách 01"
    def get_description(self): return "Tổng từ giải 3.1.3 + 4.4.2 + 5.6.4 và giải đặc biệt.1 + 2.2.4 + 3.3.1"
    def calculate(self, data): return self._make_result(data, [('giai_3_1', 2), ('giai_4_4', 1), ('giai_5_6', 3)], [('giai_db', 0), ('giai_2_2', 3), ('giai_3_3', 0)])

class Btl_HoangBach02LotoMethod(BasePredictionMethod, BaseMakeResult):
    def get_code(self): return "btl_hoangbach_02"
    def get_name(self): return "Bạch thủ lô Hoàng Bách 02"
    def get_description(self): return "Tổng từ giải 3.1.2 + 3.3.5 + 3.5.4 và giải 3.4.1 + 4.3.4 + 7.4.2"
    def calculate(self, data): return self._make_result(data, [('giai_3_1', 1), ('giai_3_3', 4), ('giai_3_5', 3)], [('giai_3_4', 0), ('giai_4_3', 3), ('giai_7_4', 1)])

class Btl_HoangBach03LotoMethod(BasePredictionMethod, BaseMakeResult):
    def get_code(self): return "btl_hoangbach_03"
    def get_name(self): return "Bạch thủ lô Hoàng Bách 03"
    def get_description(self): return "Tổng từ giải 1.1.1 + 5.5.1 + 6.3.3 và giải 3.3.1 + 4.3.3 + 4.3.4"
    def calculate(self, data): return self._make_result(data, [('giai_1', 0), ('giai_5_5', 0), ('giai_6_3', 2)], [('giai_3_3', 0), ('giai_4_3', 2), ('giai_4_3', 3)])

class Btl_HoangBach04LotoMethod(BasePredictionMethod, BaseMakeResult):
    def get_code(self): return "btl_hoangbach_04"
    def get_name(self): return "Bạch thủ lô Hoàng Bách 04"
    def get_description(self): return "Tổng từ giải 1.1.1 + 5.2.2 + 6.2.3 và giải đặc biệt.3 + 2.1.3 + 4.2.4"
    def calculate(self, data): return self._make_result(data, [('giai_1', 0), ('giai_5_2', 1), ('giai_6_2', 2)], [('giai_db', 2), ('giai_2_1', 2), ('giai_4_2', 3)])

class Btl_HoangBach05LotoMethod(BasePredictionMethod, BaseMakeResult):
    def get_code(self): return "btl_hoangbach_05"
    def get_name(self): return "Bạch thủ lô Hoàng Bách 05"
    def get_description(self): return "Tổng từ giải 3.1.2 + 5.1.3 + 5.4.1 và giải 4.1.3 + 4.1.4 + 4.4.2"
    def calculate(self, data): return self._make_result(data, [('giai_3_1', 1), ('giai_5_1', 2), ('giai_5_4', 0)], [('giai_4_1', 2), ('giai_4_1', 3), ('giai_4_4', 1)])

class Btl_HoangBach06LotoMethod(BasePredictionMethod, BaseMakeResult):
    def get_code(self): return "btl_hoangbach_06"
    def get_name(self): return "Bạch thủ lô Hoàng Bách 06"
    def get_description(self): return "Tổng từ giải 4.1.1 + 7.1.2 + 7.3.2 và giải 3.2.3 + 3.3.1 + 5.4.2"
    def calculate(self, data): return self._make_result(data, [('giai_4_1', 0), ('giai_7_1', 1), ('giai_7_3', 1)], [('giai_3_2', 2), ('giai_3_3', 0), ('giai_5_4', 1)])

class Btl_HoangBach07LotoMethod(BasePredictionMethod, BaseMakeResult):
    def get_code(self): return "btl_hoangbach_07"
    def get_name(self): return "Bạch thủ lô Hoàng Bách 07"
    def get_description(self): return "Tổng từ giải 1.1.1 + 2.2.1 + 3.4.4 và giải 3.2.3 + 5.4.2 + 5.5.3"
    def calculate(self, data): return self._make_result(data, [('giai_1', 0), ('giai_2_2', 0), ('giai_3_4', 3)], [('giai_3_2', 2), ('giai_5_4', 1), ('giai_5_5', 2)])

class Btl_HoangBach08LotoMethod(BasePredictionMethod, BaseMakeResult):
    def get_code(self): return "btl_hoangbach_08"
    def get_name(self): return "Bạch thủ lô Hoàng Bách 08"
    def get_description(self): return "Tổng từ giải 2.1.4 + 2.1.5 + 2.2.5 và giải 3.4.4 + 3.5.5 + 4.2.4"
    def calculate(self, data): return self._make_result(data, [('giai_2_1', 3), ('giai_2_1', 4), ('giai_2_2', 4)], [('giai_3_4', 3), ('giai_3_5', 4), ('giai_4_2', 3)])

class Btl_HoangBach09LotoMethod(BasePredictionMethod, BaseMakeResult):
    def get_code(self): return "btl_hoangbach_09"
    def get_name(self): return "Bạch thủ lô Hoàng Bách 09"
    def get_description(self): return "Tổng từ giải đặc biệt.1 + 3.5.5 + 6.1.3 và giải 2.2.1 + 2.2.2 + 7.3.2"
    def calculate(self, data): return self._make_result(data, [('giai_db', 0), ('giai_3_5', 4), ('giai_6_1', 2)], [('giai_2_2', 0), ('giai_2_2', 1), ('giai_7_3', 1)])

class Btl_HoangBach10LotoMethod(BasePredictionMethod, BaseMakeResult):
    def get_code(self): return "btl_hoangbach_10"
    def get_name(self): return "Bạch thủ lô Hoàng Bách 10"
    def get_description(self): return "Tổng từ giải 1.1.3 + 2.2.2 + 3.4.1 và giải 3.5.1 + 4.4.2 + 5.1.2"
    def calculate(self, data): return self._make_result(data, [('giai_1', 2), ('giai_2_2', 1), ('giai_3_4', 0)], [('giai_3_5', 0), ('giai_4_4', 1), ('giai_5_1', 1)])

class Btl_HoangBach11LotoMethod(BasePredictionMethod, BaseMakeResult):
    def get_code(self): return "btl_hoangbach_11"
    def get_name(self): return "Bạch thủ lô Hoàng Bách 11"
    def get_description(self): return "Tổng từ giải 1.1.3 + 3.5.3 + 5.1.4 và giải 3.4.1 + 5.5.1 + 6.1.1"
    def calculate(self, data): return self._make_result(data, [('giai_1', 2), ('giai_3_5', 2), ('giai_5_1', 3)], [('giai_3_4', 0), ('giai_5_5', 0), ('giai_6_1', 0)])

class Btl_HoangBach12LotoMethod(BasePredictionMethod, BaseMakeResult):
    def get_code(self): return "btl_hoangbach_12"
    def get_name(self): return "Bạch thủ lô Hoàng Bách 12"
    def get_description(self): return "Tổng từ giải 2.2.1 + 6.1.1 + 7.1.2 và giải 1.1.1 + 3.3.5 + 4.3.1"
    def calculate(self, data): return self._make_result(data, [('giai_2_2', 0), ('giai_6_1', 0), ('giai_7_1', 1)], [('giai_1', 0), ('giai_3_3', 4), ('giai_4_3', 0)])

class Btl_HoangBach13LotoMethod(BasePredictionMethod, BaseMakeResult):
    def get_code(self): return "btl_hoangbach_13"
    def get_name(self): return "Bạch thủ lô Hoàng Bách 13"
    def get_description(self): return "Tổng từ giải 3.1.4 + 3.4.4 + 6.2.2 và giải 1.1.4 + 3.3.3 + 3.6.3"
    def calculate(self, data): return self._make_result(data, [('giai_3_1', 3), ('giai_3_4', 3), ('giai_6_2', 1)], [('giai_1', 3), ('giai_3_3', 2), ('giai_3_6', 2)])

class Btl_HoangBach14LotoMethod(BasePredictionMethod, BaseMakeResult):
    def get_code(self): return "btl_hoangbach_14"
    def get_name(self): return "Bạch thủ lô Hoàng Bách 14"
    def get_description(self): return "Tổng từ giải đặc biệt.3 + 6.1.3 + 7.4.2 và giải 3.4.2 + 3.6.1 + 4.1.2"
    def calculate(self, data): return self._make_result(data, [('giai_db', 2), ('giai_6_1', 2), ('giai_7_4', 1)], [('giai_3_4', 1), ('giai_3_6', 0), ('giai_4_1', 1)])

class Btl_HoangBach15LotoMethod(BasePredictionMethod, BaseMakeResult):
    def get_code(self): return "btl_hoangbach_15"
    def get_name(self): return "Bạch thủ lô Hoàng Bách 15"
    def get_description(self): return "Tổng từ giải đặc biệt.2 + 2.2.2 + 3.4.5 và giải 4.3.4 + 4.2.3 + 6.1.2"
    def calculate(self, data): return self._make_result(data, [('giai_db', 1), ('giai_2_2', 1), ('giai_3_4', 4)], [('giai_4_3', 3), ('giai_4_2', 2), ('giai_6_1', 1)])

class Btl_HoangBach16LotoMethod(BasePredictionMethod, BaseMakeResult):
    def get_code(self): return "btl_hoangbach_16"
    def get_name(self): return "Bạch thủ lô Hoàng Bách 16"
    def get_description(self): return "Tổng từ giải đặc biệt.5 + 1.1.4 + 3.6.4 và giải 3.5.4 + 4.2.3 + 6.1.2"
    def calculate(self, data): return self._make_result(data, [('giai_db', 4), ('giai_1', 3), ('giai_3_6', 3)], [('giai_3_5', 3), ('giai_4_2', 2), ('giai_6_1', 1)])

class Btl_HoangBach17LotoMethod(BasePredictionMethod, BaseMakeResult):
    def get_code(self): return "btl_hoangbach_17"
    def get_name(self): return "Bạch thủ lô Hoàng Bách 17"
    def get_description(self): return "Tổng từ giải đặc biệt.1 + đặc biệt.4 + 5.3.3 và giải 1.1.2 + 5.4.2 + 5.4.4"
    def calculate(self, data): return self._make_result(data, [('giai_db', 0), ('giai_db', 3), ('giai_5_3', 2)], [('giai_1', 1), ('giai_5_4', 1), ('giai_5_4', 3)])

class Btl_HoangBach18LotoMethod(BasePredictionMethod, BaseMakeResult):
    def get_code(self): return "btl_hoangbach_18"
    def get_name(self): return "Bạch thủ lô Hoàng Bách 18"
    def get_description(self): return "Tổng từ giải đặc biệt.4 + 3.5.1 + 4.4.4 và giải 3.3.2 + 3.4.3 + 4.1.2"
    def calculate(self, data): return self._make_result(data, [('giai_db', 3), ('giai_3_5', 0), ('giai_4_4', 3)], [('giai_3_3', 1), ('giai_3_4', 2), ('giai_4_1', 1)])

class Btl_HoangBach19LotoMethod(BasePredictionMethod, BaseMakeResult):
    def get_code(self): return "btl_hoangbach_19"
    def get_name(self): return "Bạch thủ lô Hoàng Bách 19"
    def get_description(self): return "Tổng từ giải 1.1.2 + 3.2.4 + 5.4.4 và giải 2.2.2 + 4.3.3 + 5.6.1"
    def calculate(self, data): return self._make_result(data, [('giai_1', 1), ('giai_3_2', 3), ('giai_5_4', 3)], [('giai_2_2', 1), ('giai_4_3', 2), ('giai_5_6', 0)])

class Btl_HoangBach20LotoMethod(BasePredictionMethod, BaseMakeResult):
    def get_code(self): return "btl_hoangbach_20"
    def get_name(self): return "Bạch thủ lô Hoàng Bách 20"
    def get_description(self): return "Tổng từ giải 3.3.1 + 3.5.5 + 7.2.2 và giải 3.4.4 + 3.5.3 + 5.2.3"
    def calculate(self, data): return self._make_result(data, [('giai_3_3', 0), ('giai_3_5', 4), ('giai_7_2', 1)], [('giai_3_4', 3), ('giai_3_5', 2), ('giai_5_2', 2)])

class Btl_HoangBach21LotoMethod(BasePredictionMethod, BaseMakeResult):
    def get_code(self): return "btl_hoangbach_21"
    def get_name(self): return "Bạch thủ lô Hoàng Bách 21"
    def get_description(self): return "Tổng từ giải đặc biệt.2 + 5.2.3 + 5.6.1 và giải 1.1.4 + 3.5.4 + 5.4.3"
    def calculate(self, data): return self._make_result(data, [('giai_db', 1), ('giai_5_2', 2), ('giai_5_6', 0)], [('giai_1', 3), ('giai_3_5', 3), ('giai_5_4', 2)])

class Btl_HoangBach22LotoMethod(BasePredictionMethod, BaseMakeResult):
    def get_code(self): return "btl_hoangbach_22"
    def get_name(self): return "Bạch thủ lô Hoàng Bách 22"
    def get_description(self): return "Tổng từ giải đặc biệt.5 + 5.6.1 + 5.6.3 và giải đặc biệt.1 + 3.3.5 + 5.2.4"
    def calculate(self, data): return self._make_result(data, [('giai_db', 4), ('giai_5_6', 0), ('giai_5_6', 2)], [('giai_db', 0), ('giai_3_3', 4), ('giai_5_2', 3)])

class Btl_HoangBach23LotoMethod(BasePredictionMethod, BaseMakeResult):
    def get_code(self): return "btl_hoangbach_23"
    def get_name(self): return "Bạch thủ lô Hoàng Bách 23"
    def get_description(self): return "Tổng từ giải 5.2.4 + 5.3.3 + 6.3.3 và giải 3.1.4 + 3.3.4 + 3.5.5"
    def calculate(self, data): return self._make_result(data, [('giai_5_2', 3), ('giai_5_3', 2), ('giai_6_3', 2)], [('giai_3_1', 3), ('giai_3_3', 3), ('giai_3_5', 4)])

class Btl_HoangBach24LotoMethod(BasePredictionMethod, BaseMakeResult):
    def get_code(self): return "btl_hoangbach_24"
    def get_name(self): return "Bạch thủ lô Hoàng Bách 24"
    def get_description(self): return "Tổng từ giải 4.4.1 + 5.5.2 + 7.2.2 và giải 1.1.2 + 2.2.3 + 7.1.2"
    def calculate(self, data): return self._make_result(data, [('giai_4_4', 0), ('giai_5_5', 1), ('giai_7_2', 1)], [('giai_1', 1), ('giai_2_2', 2), ('giai_7_1', 1)])

class Btl_HoangBach25LotoMethod(BasePredictionMethod, BaseMakeResult):
    def get_code(self): return "btl_hoangbach_25"
    def get_name(self): return "Bạch thủ lô Hoàng Bách 25"
    def get_description(self): return "Tổng từ giải đặc biệt.4 + 1.1.4 + 5.1.4 và giải 2.1.1 + 3.3.1 + 3.3.3"
    def calculate(self, data): return self._make_result(data, [('giai_db', 3), ('giai_1', 3), ('giai_5_1', 3)], [('giai_2_1', 0), ('giai_3_3', 0), ('giai_3_3', 2)])

class Btl_HoangBach26LotoMethod(BasePredictionMethod, BaseMakeResult):
    def get_code(self): return "btl_hoangbach_26"
    def get_name(self): return "Bạch thủ lô Hoàng Bách 26"
    def get_description(self): return "Tổng từ giải đặc biệt.4 + 3.4.3 + 4.2.4 và giải 3.1.3 + 5.1.1 + 5.3.4"
    def calculate(self, data): return self._make_result(data, [('giai_db', 3), ('giai_3_4', 2), ('giai_4_2', 3)], [('giai_3_1', 2), ('giai_5_1', 0), ('giai_5_3', 3)])

class Btl_HoangBach27LotoMethod(BasePredictionMethod, BaseMakeResult):
    def get_code(self): return "btl_hoangbach_27"
    def get_name(self): return "Bạch thủ lô Hoàng Bách 27"
    def get_description(self): return "Tổng từ giải đặc biệt.4 + 2.2.2 + 6.2.3 và giải 1.1.1 + 5.1.1 + 5.6.1"
    def calculate(self, data): return self._make_result(data, [('giai_db', 3), ('giai_2_2', 1), ('giai_6_2', 2)], [('giai_1', 0), ('giai_5_1', 0), ('giai_5_6', 0)])

class Btl_HoangBach28LotoMethod(BasePredictionMethod, BaseMakeResult):
    def get_code(self): return "btl_hoangbach_28"
    def get_name(self): return "Bạch thủ lô Hoàng Bách 28"
    def get_description(self): return "Tổng từ giải đặc biệt.4 + 2.2.2 + 6.2.3 và giải đặc biệt.4 + 4.2.2 + 6.3.2"
    def calculate(self, data): return self._make_result(data, [('giai_db', 3), ('giai_2_2', 1), ('giai_6_2', 2)], [('giai_db', 3), ('giai_4_2', 1), ('giai_6_3', 1)])

class Btl_HoangBach29LotoMethod(BasePredictionMethod, BaseMakeResult):
    def get_code(self): return "btl_hoangbach_29"
    def get_name(self): return "Bạch thủ lô Hoàng Bách 29"
    def get_description(self): return "Tổng từ giải 3.1.2 + 5.6.2 + 6.2.3 và giải 3.3.2 + 3.5.3 + 7.3.2"
    def calculate(self, data): return self._make_result(data, [('giai_3_1', 1), ('giai_5_6', 1), ('giai_6_2', 2)], [('giai_3_3', 1), ('giai_3_5', 2), ('giai_7_3', 1)])

class Btl_HoangBach30LotoMethod(BasePredictionMethod, BaseMakeResult):
    def get_code(self): return "btl_hoangbach_30"
    def get_name(self): return "Bạch thủ lô Hoàng Bách 30"
    def get_description(self): return "Tổng từ giải đặc biệt.2 + 3.1.3 + 5.2.4 và giải 1.1.4 + 2.2.5 + 7.4.2"
    def calculate(self, data): return self._make_result(data, [('giai_db', 1), ('giai_3_1', 2), ('giai_5_2', 3)], [('giai_1', 3), ('giai_2_2', 4), ('giai_7_4', 1)])

class Btl_HoangBach31LotoMethod(BasePredictionMethod, BaseMakeResult):
    def get_code(self): return "btl_hoangbach_31"
    def get_name(self): return "Bạch thủ lô Hoàng Bách 31"
    def get_description(self): return "Tổng từ giải 3.6.3 + 5.2.2 + 6.3.3 và giải 4.3.4 + 5.3.1 + 5.5.4"
    def calculate(self, data): return self._make_result(data, [('giai_3_6', 2), ('giai_5_2', 1), ('giai_6_3', 2)], [('giai_4_3', 3), ('giai_5_3', 0), ('giai_5_5', 3)])

class Btl_HoangBach32LotoMethod(BasePredictionMethod, BaseMakeResult):
    def get_code(self): return "btl_hoangbach_32"
    def get_name(self): return "Bạch thủ lô Hoàng Bách 32"
    def get_description(self): return "Tổng từ giải đặc biệt.3 + 3.4.4 + 3.4.5 và giải 5.5.2 + 5.5.3 + 5.5.4"
    def calculate(self, data): return self._make_result(data, [('giai_db', 2), ('giai_3_4', 3), ('giai_3_4', 4)], [('giai_5_5', 1), ('giai_5_5', 2), ('giai_5_5', 3)])

class Btl_HoangBach33LotoMethod(BasePredictionMethod, BaseMakeResult):
    def get_code(self): return "btl_hoangbach_33"
    def get_name(self): return "Bạch thủ lô Hoàng Bách 33"
    def get_description(self): return "Tổng từ giải đặc biệt.4 + 2.1.1 + 2.1.2 và giải 5.4.2 + 5.4.3 + 5.4.4"
    def calculate(self, data): return self._make_result(data, [('giai_db', 3), ('giai_2_1', 0), ('giai_2_1', 1)], [('giai_5_4', 1), ('giai_5_4', 2), ('giai_5_4', 3)])

class Btl_HoangBach34LotoMethod(BasePredictionMethod, BaseMakeResult):
    def get_code(self): return "btl_hoangbach_34"
    def get_name(self): return "Bạch thủ lô Hoàng Bách 34"
    def get_description(self): return "Tổng từ giải đặc biệt.2 + đặc biệt.3 + 5.1.1 và giải 3.3.3 + 3.3.4 + 7.2.1"
    def calculate(self, data): return self._make_result(data, [('giai_db', 1), ('giai_db', 2), ('giai_5_1', 0)], [('giai_3_3', 2), ('giai_3_3', 3), ('giai_7_2', 0)])

class Btl_HoangBach35LotoMethod(BasePredictionMethod, BaseMakeResult):
    def get_code(self): return "btl_hoangbach_35"
    def get_name(self): return "Bạch thủ lô Hoàng Bách 35"
    def get_description(self): return "Tổng từ giải 3.4.2 + 3.5.3 + 4.4.1 và giải 2.1.4 + 4.3.2 + 6.3.1"
    def calculate(self, data): return self._make_result(data, [('giai_3_4', 1), ('giai_3_5', 2), ('giai_4_4', 0)], [('giai_2_1', 3), ('giai_4_3', 1), ('giai_6_3', 0)])

class Btl_HoangBach36LotoMethod(BasePredictionMethod, BaseMakeResult):
    def get_code(self): return "btl_hoangbach_36"
    def get_name(self): return "Bạch thủ lô Hoàng Bách 36"
    def get_description(self): return "Tổng từ giải 3.4.2 + 3.5.3 + 4.4.1 và giải 3.5.3 + 4.3.2 + 5.5.1"
    def calculate(self, data): return self._make_result(data, [('giai_3_4', 1), ('giai_3_5', 2), ('giai_4_4', 0)], [('giai_3_5', 2), ('giai_4_3', 1), ('giai_5_5', 0)])

class Btl_HoangBach37LotoMethod(BasePredictionMethod, BaseMakeResult):
    def get_code(self): return "btl_hoangbach_37"
    def get_name(self): return "Bạch thủ lô Hoàng Bách 37"
    def get_description(self): return "Tổng từ giải 2.1.5 + 3.6.2 + 5.2.4 và giải 2.2.5 + 3.5.5 + 5.2.3"
    def calculate(self, data): return self._make_result(data, [('giai_2_1', 4), ('giai_3_6', 1), ('giai_5_2', 3)], [('giai_2_2', 4), ('giai_3_5', 4), ('giai_5_2', 2)])

class Btl_HoangBach38LotoMethod(BasePredictionMethod, BaseMakeResult):
    def get_code(self): return "btl_hoangbach_38"
    def get_name(self): return "Bạch thủ lô Hoàng Bách 38"
    def get_description(self): return "Tổng từ giải 1.1.4 + 3.6.5 + 5.1.3 và giải 5.2.2 + 5.5.2 + 6.1.1"
    def calculate(self, data): return self._make_result(data, [('giai_1', 3), ('giai_3_6', 4), ('giai_5_1', 2)], [('giai_5_2', 1), ('giai_5_5', 1), ('giai_6_1', 0)])

class Btl_HoangBach39LotoMethod(BasePredictionMethod, BaseMakeResult):
    def get_code(self): return "btl_hoangbach_39"
    def get_name(self): return "Bạch thủ lô Hoàng Bách 39"
    def get_description(self): return "Tổng từ giải 1.1.1 + 5.1.2 + 6.2.1 và giải 1.1.5 + 3.5.2 + 5.5.3"
    def calculate(self, data): return self._make_result(data, [('giai_1', 0), ('giai_5_1', 1), ('giai_6_2', 0)], [('giai_1', 4), ('giai_3_5', 1), ('giai_5_5', 2)])

class Btl_HoangBach40LotoMethod(BasePredictionMethod, BaseMakeResult):
    def get_code(self): return "btl_hoangbach_40"
    def get_name(self): return "Bạch thủ lô Hoàng Bách 40"
    def get_description(self): return "Tổng từ giải đặc biệt.4 + 4.3.1 + 7.4.1 và giải đặc biệt.2 + đặc biệt.5 + 7.3.1"
    def calculate(self, data): return self._make_result(data, [('giai_db', 3), ('giai_4_3', 0), ('giai_7_4', 0)], [('giai_db', 1), ('giai_db', 4), ('giai_7_3', 0)])

class Btl_HoangBach41LotoMethod(BasePredictionMethod, BaseMakeResult):
    def get_code(self): return "btl_hoangbach_41"
    def get_name(self): return "Bạch thủ lô Hoàng Bách 41"
    def get_description(self): return "Tổng từ giải đặc biệt.3 + 4.4.2 + 6.3.3 và giải 4.1.4 + 5.4.2 + 7.1.2"
    def calculate(self, data): return self._make_result(data, [('giai_db', 2), ('giai_4_4', 1), ('giai_6_3', 2)], [('giai_4_1', 3), ('giai_5_4', 1), ('giai_7_1', 1)])

class Btl_HoangBach42LotoMethod(BasePredictionMethod, BaseMakeResult):
    def get_code(self): return "btl_hoangbach_42"
    def get_name(self): return "Bạch thủ lô Hoàng Bách 42"
    def get_description(self): return "Tổng từ giải đặc biệt.3 + 4.4.2 + 6.3.3 và giải 3.1.2 + 3.2.3 + 3.5.5"
    def calculate(self, data): return self._make_result(data, [('giai_db', 2), ('giai_4_4', 1), ('giai_6_3', 2)], [('giai_3_1', 1), ('giai_3_2', 2), ('giai_3_5', 4)])

class Btl_HoangBach43LotoMethod(BasePredictionMethod, BaseMakeResult):
    def get_code(self): return "btl_hoangbach_43"
    def get_name(self): return "Bạch thủ lô Hoàng Bách 43"
    def get_description(self): return "Tổng từ giải 1.1.3 + 4.1.3 + 4.4.2 và giải 3.2.3 + 4.2.1 + 6.2.2"
    def calculate(self, data): return self._make_result(data, [('giai_1', 2), ('giai_4_1', 2), ('giai_4_4', 1)], [('giai_3_2', 2), ('giai_4_2', 0), ('giai_6_2', 1)])

class Btl_HoangBach44LotoMethod(BasePredictionMethod, BaseMakeResult):
    def get_code(self): return "btl_hoangbach_44"
    def get_name(self): return "Bạch thủ lô Hoàng Bách 44"
    def get_description(self): return "Tổng từ giải đặc biệt.2 + 3.1.1 + 3.3.2 và giải 3.2.5 + 3.4.5 + 4.3.1"
    def calculate(self, data): return self._make_result(data, [('giai_db', 1), ('giai_3_1', 0), ('giai_3_3', 1)], [('giai_3_2', 4), ('giai_3_4', 4), ('giai_4_3', 0)])

class Btl_HoangBach45LotoMethod(BasePredictionMethod, BaseMakeResult):
    def get_code(self): return "btl_hoangbach_45"
    def get_name(self): return "Bạch thủ lô Hoàng Bách 45"
    def get_description(self): return "Tổng từ giải 5.4.1 + 5.4.2 + 7.1.1 và giải 5.6.1 + 5.6.2 + 5.6.3"
    def calculate(self, data): return self._make_result(data, [('giai_5_4', 0), ('giai_5_4', 1), ('giai_7_1', 0)], [('giai_5_6', 0), ('giai_5_6', 1), ('giai_5_6', 2)])

class Btl_HoangBach46LotoMethod(BasePredictionMethod, BaseMakeResult):
    def get_code(self): return "btl_hoangbach_46"
    def get_name(self): return "Bạch thủ lô Hoàng Bách 46"
    def get_description(self): return "Tổng từ giải đặc biệt.5 + 2.1.3 + 5.4.4 và giải 2.2.1 + 3.5.5 + 4.4.4"
    def calculate(self, data): return self._make_result(data, [('giai_db', 4), ('giai_2_1', 2), ('giai_5_4', 3)], [('giai_2_2', 0), ('giai_3_5', 4), ('giai_4_4', 3)])

class Btl_HoangBach47LotoMethod(BasePredictionMethod, BaseMakeResult):
    def get_code(self): return "btl_hoangbach_47"
    def get_name(self): return "Bạch thủ lô Hoàng Bách 47"
    def get_description(self): return "Tổng từ giải đặc biệt.1 + 3.1.2 + 6.2.3 và giải 1.1.5 + 3.3.5 + 3.6.1"
    def calculate(self, data): return self._make_result(data, [('giai_db', 0), ('giai_3_1', 1), ('giai_6_2', 2)], [('giai_1', 4), ('giai_3_3', 4), ('giai_3_6', 0)])

class Btl_HoangBach48LotoMethod(BasePredictionMethod, BaseMakeResult):
    def get_code(self): return "btl_hoangbach_48"
    def get_name(self): return "Bạch thủ lô Hoàng Bách 48"
    def get_description(self): return "Tổng từ giải 1.1.3 + 6.1.1 + 7.2.2 và giải 5.1.4 + 5.3.3 + 6.2.3"
    def calculate(self, data): return self._make_result(data, [('giai_1', 2), ('giai_6_1', 0), ('giai_7_2', 1)], [('giai_5_1', 3), ('giai_5_3', 2), ('giai_6_2', 2)])

class Btl_HoangBach49LotoMethod(BasePredictionMethod, BaseMakeResult):
    def get_code(self): return "btl_hoangbach_49"
    def get_name(self): return "Bạch thủ lô Hoàng Bách 49"
    def get_description(self): return "Tổng từ giải 2.2.3 + 4.1.2 + 4.3.1 và giải đặc biệt.1 + 2.1.1 + 5.3.4"
    def calculate(self, data): return self._make_result(data, [('giai_2_2', 2), ('giai_4_1', 1), ('giai_4_3', 0)], [('giai_db', 0), ('giai_2_1', 0), ('giai_5_3', 3)])

class Btl_HoangBach50LotoMethod(BasePredictionMethod, BaseMakeResult):
    def get_code(self): return "btl_hoangbach_50"
    def get_name(self): return "Bạch thủ lô Hoàng Bách 50"
    def get_description(self): return "Tổng từ giải đặc biệt.1 + 3.5.2 + 4.1.4 và giải 1.1.3 + 3.3.5 + 4.3.2"
    def calculate(self, data): return self._make_result(data, [('giai_db', 0), ('giai_3_5', 1), ('giai_4_1', 3)], [('giai_1', 2), ('giai_3_3', 4), ('giai_4_3', 1)])

class Btl_HoangBach51LotoMethod(BasePredictionMethod, BaseMakeResult):
    def get_code(self): return "btl_hoangbach_51"
    def get_name(self): return "Bạch thủ lô Hoàng Bách 51"
    def get_description(self): return "Tổng từ giải 2.2.2 + 4.4.3 + 5.4.1 và giải 3.1.4 + 4.1.2 + 6.2.3"
    def calculate(self, data): return self._make_result(data, [('giai_2_2', 1), ('giai_4_4', 2), ('giai_5_4', 0)], [('giai_3_1', 3), ('giai_4_1', 1), ('giai_6_2', 2)])

class Btl_HoangBach52LotoMethod(BasePredictionMethod, BaseMakeResult):
    def get_code(self): return "btl_hoangbach_52"
    def get_name(self): return "Bạch thủ lô Hoàng Bách 52"
    def get_description(self): return "Tổng từ giải 3.5.1 + 6.1.3 + 7.3.1 và giải 2.2.4 + 4.3.4 + 6.1.3"
    def calculate(self, data): return self._make_result(data, [('giai_3_5', 0), ('giai_6_1', 2), ('giai_7_3', 0)], [('giai_2_2', 3), ('giai_4_3', 3), ('giai_6_1', 2)])

class Btl_HoangBach53LotoMethod(BasePredictionMethod, BaseMakeResult):
    def get_code(self): return "btl_hoangbach_53"
    def get_name(self): return "Bạch thủ lô Hoàng Bách 53"
    def get_description(self): return "Tổng từ giải 1.1.2 + 3.5.1 + 3.6.1 và giải 1.1.1 + 3.3.2 + 4.4.1"
    def calculate(self, data): return self._make_result(data, [('giai_1', 1), ('giai_3_5', 0), ('giai_3_6', 0)], [('giai_1', 0), ('giai_3_3', 1), ('giai_4_4', 0)])

class Btl_HoangBach54LotoMethod(BasePredictionMethod, BaseMakeResult):
    def get_code(self): return "btl_hoangbach_54"
    def get_name(self): return "Bạch thủ lô Hoàng Bách 54"
    def get_description(self): return "Tổng từ giải 1.1.4 + 3.4.1 + 4.4.4 và giải 3.3.2 + 3.6.3 + 6.2.2"
    def calculate(self, data): return self._make_result(data, [('giai_1', 3), ('giai_3_4', 0), ('giai_4_4', 3)], [('giai_3_3', 1), ('giai_3_6', 2), ('giai_6_2', 1)])

class Btl_HoangBach55LotoMethod(BasePredictionMethod, BaseMakeResult):
    def get_code(self): return "btl_hoangbach_55"
    def get_name(self): return "Bạch thủ lô Hoàng Bách 55"
    def get_description(self): return "Tổng từ giải đặc biệt.1 + 6.1.1 + 6.3.3 và giải 3.5.5 + 4.1.2 + 7.3.2"
    def calculate(self, data): return self._make_result(data, [('giai_db', 0), ('giai_6_1', 0), ('giai_6_3', 2)], [('giai_3_5', 4), ('giai_4_1', 1), ('giai_7_3', 1)])

class Btl_HoangBach56LotoMethod(BasePredictionMethod, BaseMakeResult):
    def get_code(self): return "btl_hoangbach_56"
    def get_name(self): return "Bạch thủ lô Hoàng Bách 56"
    def get_description(self): return "Tổng từ giải 4.1.1 + 7.1.2 + 7.3.2 và giải 3.2.3 + 3.3.1 + 5.4.2"
    def calculate(self, data): return self._make_result(data, [('giai_4_1', 0), ('giai_7_1', 1), ('giai_7_3', 1)], [('giai_3_2', 2), ('giai_3_3', 0), ('giai_5_4', 1)])

class Btl_HoangBach57LotoMethod(BasePredictionMethod, BaseMakeResult):
    def get_code(self): return "btl_hoangbach_57"
    def get_name(self): return "Bạch thủ lô Hoàng Bách 57"
    def get_description(self): return "Tổng từ giải 2.1.5 + 3.4.3 + 5.2.2 và giải 1.1.1 + 3.3.5 + 5.3.1"
    def calculate(self, data): return self._make_result(data, [('giai_2_1', 4), ('giai_3_4', 2), ('giai_5_2', 1)], [('giai_1', 0), ('giai_3_3', 4), ('giai_5_3', 0)])

class Btl_HoangBach58LotoMethod(BasePredictionMethod, BaseMakeResult):
    def get_code(self): return "btl_hoangbach_58"
    def get_name(self): return "Bạch thủ lô Hoàng Bách 58"
    def get_description(self): return "Tổng từ giải 1.1.3 + 3.4.1 + 5.5.2 và giải đặc biệt.5 + 3.3.2 + 6.3.2"
    def calculate(self, data): return self._make_result(data, [('giai_1', 2), ('giai_3_4', 0), ('giai_5_5', 1)], [('giai_db', 4), ('giai_3_3', 1), ('giai_6_3', 1)])

class Btl_HoangBach59LotoMethod(BasePredictionMethod, BaseMakeResult):
    def get_code(self): return "btl_hoangbach_59"
    def get_name(self): return "Bạch thủ lô Hoàng Bách 59"
    def get_description(self): return "Tổng từ giải đặc biệt.4 + 3.4.1 + 5.4.4 và giải 3.2.1 + 3.6.4 + 7.4.2"
    def calculate(self, data): return self._make_result(data, [('giai_db', 3), ('giai_3_4', 0), ('giai_5_4', 3)], [('giai_3_2', 0), ('giai_3_6', 3), ('giai_7_4', 1)])

class Btl_HoangBach60LotoMethod(BasePredictionMethod, BaseMakeResult):
    def get_code(self): return "btl_hoangbach_60"
    def get_name(self): return "Bạch thủ lô Hoàng Bách 60"
    def get_description(self): return "Tổng từ giải 3.1.3 + 4.4.2 + 5.6.4 và giải đặc biệt.1 + 2.2.4 + 3.3.1"
    def calculate(self, data): return self._make_result(data, [('giai_3_1', 2), ('giai_4_4', 1), ('giai_5_6', 3)], [('giai_db', 0), ('giai_2_2', 3), ('giai_3_3', 0)])

class Btl_HoangBach61LotoMethod(BasePredictionMethod, BaseMakeResult):
    def get_code(self): return "btl_hoangbach_61"
    def get_name(self): return "Bạch thủ lô Hoàng Bách 61"
    def get_description(self): return "Tổng từ giải đặc biệt.4 + 4.3.1 + 7.4.1 và giải đặc biệt.2 + đặc biệt.5 + 7.3.1"
    def calculate(self, data): return self._make_result(data, [('giai_db', 3), ('giai_4_3', 0), ('giai_7_4', 0)], [('giai_db', 1), ('giai_db', 4), ('giai_7_3', 0)])

class Btl_HoangBach62LotoMethod(BasePredictionMethod, BaseMakeResult):
    def get_code(self): return "btl_hoangbach_62"
    def get_name(self): return "Bạch thủ lô Hoàng Bách 62"
    def get_description(self): return "Tổng từ giải 2.1.1 + 4.4.2 + 5.3.1 và giải 3.2.5 + 3.5.5 + 5.5.4"
    def calculate(self, data): return self._make_result(data, [('giai_2_1', 0), ('giai_4_4', 1), ('giai_5_3', 0)], [('giai_3_2', 4), ('giai_3_5', 4), ('giai_5_5', 3)])

class Btl_HoangBach63LotoMethod(BasePredictionMethod, BaseMakeResult):
    def get_code(self): return "btl_hoangbach_63"
    def get_name(self): return "Bạch thủ lô Hoàng Bách 63"
    def get_description(self): return "Tổng từ giải đặc biệt.2 + 2.1.3 + 4.3.2 và giải 3.1.5 + 4.4.2 + 5.1.4"
    def calculate(self, data): return self._make_result(data, [('giai_db', 1), ('giai_2_1', 2), ('giai_4_3', 1)], [('giai_3_1', 4), ('giai_4_4', 1), ('giai_5_1', 3)])

class Btl_HoangBach64LotoMethod(BasePredictionMethod, BaseMakeResult):
    def get_code(self): return "btl_hoangbach_64"
    def get_name(self): return "Bạch thủ lô Hoàng Bách 64"
    def get_description(self): return "Tổng từ giải đặc biệt.3 + 2.2.5 + 3.5.5 và giải đặc biệt.5 + 2.1.5 + 3.2.5"
    def calculate(self, data): return self._make_result(data, [('giai_db', 2), ('giai_2_2', 4), ('giai_3_5', 4)], [('giai_db', 4), ('giai_2_1', 4), ('giai_3_2', 4)])

class Btl_HoangBach65LotoMethod(BasePredictionMethod, BaseMakeResult):
    def get_code(self): return "btl_hoangbach_65"
    def get_name(self): return "Bạch thủ lô Hoàng Bách 65"
    def get_description(self): return "Tổng từ giải 2.1.1 + 4.4.2 + 5.3.1 và giải 3.2.5 + 3.5.5 + 5.5.4"
    def calculate(self, data): return self._make_result(data, [('giai_2_1', 0), ('giai_4_4', 1), ('giai_5_3', 0)], [('giai_3_2', 4), ('giai_3_5', 4), ('giai_5_5', 3)])

class Btl_HoangBach66LotoMethod(BasePredictionMethod, BaseMakeResult):
    def get_code(self): return "btl_hoangbach_66"
    def get_name(self): return "Bạch thủ lô Hoàng Bách 66"
    def get_description(self): return "Tổng từ giải đặc biệt.2 + 2.1.1 + 3.3.1 và giải 3.5.3 + 4.1.4 + 5.2.4"
    def calculate(self, data): return self._make_result(data, [('giai_db', 1), ('giai_2_1', 0), ('giai_3_3', 0)], [('giai_3_5', 2), ('giai_4_1', 3), ('giai_5_2', 3)])

class Btl_HoangBach67LotoMethod(BasePredictionMethod, BaseMakeResult):
    def get_code(self): return "btl_hoangbach_67"
    def get_name(self): return "Bạch thủ lô Hoàng Bách 67"
    def get_description(self): return "Tổng từ giải 2.1.3 + 3.5.2 + 6.2.3 và giải 3.3.1 + 3.3.2 + 6.1.2"
    def calculate(self, data): return self._make_result(data, [('giai_2_1', 2), ('giai_3_5', 1), ('giai_6_2', 2)], [('giai_3_3', 0), ('giai_3_3', 1), ('giai_6_1', 1)])

class Btl_HoangBach68LotoMethod(BasePredictionMethod, BaseMakeResult):
    def get_code(self): return "btl_hoangbach_68"
    def get_name(self): return "Bạch thủ lô Hoàng Bách 68"
    def get_description(self): return "Tổng từ giải 5.3.1 + 5.3.2 + 5.3.3 và giải 3.6.2 + 3.6.3 + 3.6.4"
    def calculate(self, data): return self._make_result(data, [('giai_5_3', 0), ('giai_5_3', 1), ('giai_5_3', 2)], [('giai_3_6', 1), ('giai_3_6', 2), ('giai_3_6', 3)])

class Btl_HoangBach69LotoMethod(BasePredictionMethod, BaseMakeResult):
    def get_code(self): return "btl_hoangbach_69"
    def get_name(self): return "Bạch thủ lô Hoàng Bách 69"
    def get_description(self): return "Tổng từ giải 1.1.1 + 2.2.3 + 3.5.1 và giải 3.6.1 + 5.1.3 + 5.3.2"
    def calculate(self, data): return self._make_result(data, [('giai_1', 0), ('giai_2_2', 2), ('giai_3_5', 0)], [('giai_3_6', 0), ('giai_5_1', 2), ('giai_5_3', 1)])

class Btl_HoangBach69LotoMethod(BasePredictionMethod, BaseMakeResult):
    def get_code(self): return "btl_hoangbach_69"
    def get_name(self): return "Bạch thủ lô Hoàng Bách 69"
    def get_description(self): return "Tổng từ giải 1.1.1 + 2.2.3 + 3.5.1 và giải 3.6.1 + 5.1.3 + 5.3.2"
    def calculate(self, data): return self._make_result(data, [('giai_1', 0), ('giai_2_2', 2), ('giai_3_5', 0)], [('giai_3_6', 0), ('giai_5_1', 2), ('giai_5_3', 1)])

class Btl_HoangBach70LotoMethod(BasePredictionMethod, BaseMakeResult):
    def get_code(self): return "btl_hoangbach_70"
    def get_name(self): return "Bạch thủ lô Hoàng Bách 70"
    def get_description(self): return "Tổng từ giải 1.1.1 + 4.1.1 + 7.1.1 và giải giai_db.4 + 3.3.5 + 5.5.2"
    def calculate(self, data): return self._make_result(data, [('giai_1', 0), ('giai_4_1', 0), ('giai_7_1', 0)], [('giai_db', 3), ('giai_3_3', 4), ('giai_5_5', 1)])

class Btl_HoangBach71LotoMethod(BasePredictionMethod, BaseMakeResult):
    def get_code(self): return "btl_hoangbach_71"
    def get_name(self): return "Bạch thủ lô Hoàng Bách 71"
    def get_description(self): return "Tổng từ giải 1.1.5 + 2.2.1 + 4.4.3 và giải 2.1.4 + 3.1.2 + 4.3.4"
    def calculate(self, data): return self._make_result(data, [('giai_1', 4), ('giai_2_2', 0), ('giai_4_4', 2)], [('giai_2_1', 3), ('giai_3_1', 1), ('giai_4_3', 3)])

class Btl_HoangBach72LotoMethod(BasePredictionMethod, BaseMakeResult):
    def get_code(self): return "btl_hoangbach_72"
    def get_name(self): return "Bạch thủ lô Hoàng Bách 72"
    def get_description(self): return "Tổng từ giải 3.1.3 + 6.2.2 + 7.1.1 và giải 3.3.1 + 5.4.4 + 6.3.3"
    def calculate(self, data): return self._make_result(data, [('giai_3_1', 2), ('giai_6_2', 1), ('giai_7_1', 0)], [('giai_3_3', 0), ('giai_5_4', 3), ('giai_6_3', 2)])

class Btl_HoangBach73LotoMethod(BasePredictionMethod, BaseMakeResult):
    def get_code(self): return "btl_hoangbach_73"
    def get_name(self): return "Bạch thủ lô Hoàng Bách 73"
    def get_description(self): return "Tổng từ giải 1.1.2 + 5.5.1 + 5.5.2 và giải 3.3.1 + 3.6.4 + 4.2.3"
    def calculate(self, data): return self._make_result(data, [('giai_1', 1), ('giai_5_5', 0), ('giai_5_5', 1)], [('giai_3_3', 0), ('giai_3_6', 3), ('giai_4_2', 2)])

class Btl_HoangBach74LotoMethod(BasePredictionMethod, BaseMakeResult):
    def get_code(self): return "btl_hoangbach_74"
    def get_name(self): return "Bạch thủ lô Hoàng Bách 74"
    def get_description(self): return "Tổng từ giải 2.1.1 + 2.2.1 + 4.2.4 và giải 3.3.2 + 4.1.2 + 7.1.1"
    def calculate(self, data): return self._make_result(data, [('giai_2_1', 0), ('giai_2_2', 0), ('giai_4_2', 3)], [('giai_3_3', 1), ('giai_4_1', 1), ('giai_7_1', 0)])

class Btl_HoangBach75LotoMethod(BasePredictionMethod, BaseMakeResult):
    def get_code(self): return "btl_hoangbach_75"
    def get_name(self): return "Bạch thủ lô Hoàng Bách 75"
    def get_description(self): return "Tổng từ giải 2.1.4 + 5.5.4 + 7.1.1 và giải 2.2.5 + 5.3.3 + 5.6.1"
    def calculate(self, data): return self._make_result(data, [('giai_2_1', 3), ('giai_5_5', 3), ('giai_7_1', 0)], [('giai_2_2', 4), ('giai_5_3', 2), ('giai_5_6', 0)])

class Btl_HoangBach76LotoMethod(BasePredictionMethod, BaseMakeResult):
    def get_code(self): return "btl_hoangbach_76"
    def get_name(self): return "Bạch thủ lô Hoàng Bách 76"
    def get_description(self): return "Tổng từ giải 2.2.4 + 3.4.3 + 7.4.2 và giải 1.1.1 + 4.3.2 + 5.5.3"
    def calculate(self, data): return self._make_result(data, [('giai_2_2', 3), ('giai_3_4', 2), ('giai_7_4', 1)], [('giai_1', 0), ('giai_4_3', 1), ('giai_5_5', 2)])

class Btl_HoangBach77LotoMethod(BasePredictionMethod, BaseMakeResult):
    def get_code(self): return "btl_hoangbach_77"
    def get_name(self): return "Bạch thủ lô Hoàng Bách 77"
    def get_description(self): return "Tổng từ giải 3.2.4 + 3.4.5 + 4.3.1 và giải giai_db.2 + giai_db.4 + 5.6.1"
    def calculate(self, data): return self._make_result(data, [('giai_3_2', 3), ('giai_3_4', 4), ('giai_4_3', 0)], [('giai_db', 1), ('giai_db', 3), ('giai_5_6', 0)])

class Btl_HoangBach78LotoMethod(BasePredictionMethod, BaseMakeResult):
    def get_code(self): return "btl_hoangbach_78"
    def get_name(self): return "Bạch thủ lô Hoàng Bách 78"
    def get_description(self): return "Tổng từ giải 3.5.2 + 3.6.1 + 5.3.2 và giải giai_db.2 + 3.4.1 + 5.6.4"
    def calculate(self, data): return self._make_result(data, [('giai_3_5', 1), ('giai_3_6', 0), ('giai_5_3', 1)], [('giai_db', 1), ('giai_3_4', 0), ('giai_5_6', 3)])

class Btl_HoangBach79LotoMethod(BasePredictionMethod, BaseMakeResult):
    def get_code(self): return "btl_hoangbach_79"
    def get_name(self): return "Bạch thủ lô Hoàng Bách 79"
    def get_description(self): return "Tổng từ giải 3.2.4 + 3.4.5 + 4.3.1 và giải giai_db.2 + giai_db.4 + 5.6.1"
    def calculate(self, data): return self._make_result(data, [('giai_3_2', 3), ('giai_3_4', 4), ('giai_4_3', 0)], [('giai_db', 1), ('giai_db', 3), ('giai_5_6', 0)])

class Btl_HoangBach80LotoMethod(BasePredictionMethod, BaseMakeResult):
    def get_code(self): return "btl_hoangbach_80"
    def get_name(self): return "Bạch thủ lô Hoàng Bách 80"
    def get_description(self): return "Tổng từ giải 2.1.1 + 4.1.1 + 4.4.4 và giải giai_db.2 + 3.4.3 + 5.6.3"
    def calculate(self, data): return self._make_result(data, [('giai_2_1', 0), ('giai_4_1', 0), ('giai_4_4', 3)], [('giai_db', 1), ('giai_3_4', 2), ('giai_5_6', 2)])

class Btl_HoangBach81LotoMethod(BasePredictionMethod, BaseMakeResult):
    def get_code(self): return "btl_hoangbach_81"
    def get_name(self): return "Bạch thủ lô Hoàng Bách 81"
    def get_description(self): return "Tổng từ giải giai_db.3 + 1.1.3 + 3.4.5 và giải 3.3.2 + 3.6.2 + 5.5.4"
    def calculate(self, data): return self._make_result(data, [('giai_db', 2), ('giai_1', 2), ('giai_3_4', 4)], [('giai_3_3', 1), ('giai_3_6', 1), ('giai_5_5', 3)])

class Btl_HoangBach82LotoMethod(BasePredictionMethod, BaseMakeResult):
    def get_code(self): return "btl_hoangbach_82"
    def get_name(self): return "Bạch thủ lô Hoàng Bách 82"
    def get_description(self): return "Tổng từ giải 3.5.2 + 3.6.1 + 5.3.2 và giải giai_db.2 + 3.4.1 + 5.6.4"
    def calculate(self, data): return self._make_result(data, [('giai_3_5', 1), ('giai_3_6', 0), ('giai_5_3', 1)], [('giai_db', 1), ('giai_3_4', 0), ('giai_5_6', 3)])

class Btl_HoangBach83LotoMethod(BasePredictionMethod, BaseMakeResult):
    def get_code(self): return "btl_hoangbach_83"
    def get_name(self): return "Bạch thủ lô Hoàng Bách 83"
    def get_description(self): return "Tổng từ giải 3.2.3 + 5.2.4 + 5.6.1 và giải 1.1.2 + 5.1.2 + 7.4.1"
    def calculate(self, data): return self._make_result(data, [('giai_3_2', 2), ('giai_5_2', 3), ('giai_5_6', 0)], [('giai_1', 1), ('giai_5_1', 1), ('giai_7_4', 0)])

class Btl_HoangBach84LotoMethod(BasePredictionMethod, BaseMakeResult):
    def get_code(self): return "btl_hoangbach_84"
    def get_name(self): return "Bạch thủ lô Hoàng Bách 84"
    def get_description(self): return "Tổng từ giải 2.1.3 + 3.5.2 + 4.3.4 và giải 2.2.1 + 5.6.4 + 7.4.2"
    def calculate(self, data): return self._make_result(data, [('giai_2_1', 2), ('giai_3_5', 1), ('giai_4_3', 3)], [('giai_2_2', 0), ('giai_5_6', 3), ('giai_7_4', 1)])

class Btl_HoangBach85LotoMethod(BasePredictionMethod, BaseMakeResult):
    def get_code(self): return "btl_hoangbach_85"
    def get_name(self): return "Bạch thủ lô Hoàng Bách 85"
    def get_description(self): return "Tổng từ giải giai_db.4 + 2.1.1 + 5.2.1 và giải 2.2.1 + 3.5.5 + 6.3.1"
    def calculate(self, data): return self._make_result(data, [('giai_db', 3), ('giai_2_1', 0), ('giai_5_2', 0)], [('giai_2_2', 0), ('giai_3_5', 4), ('giai_6_3', 0)])

class Btl_HoangBach86LotoMethod(BasePredictionMethod, BaseMakeResult):
    def get_code(self): return "btl_hoangbach_86"
    def get_name(self): return "Bạch thủ lô Hoàng Bách 86"
    def get_description(self): return "Tổng từ giải 1.1.2 + 3.1.2 + 5.1.3 và giải giai_db.5 + 3.3.5 + 5.2.1"
    def calculate(self, data): return self._make_result(data, [('giai_1', 1), ('giai_3_1', 1), ('giai_5_1', 2)], [('giai_db', 4), ('giai_3_3', 4), ('giai_5_2', 0)])

class Btl_HoangBach87LotoMethod(BasePredictionMethod, BaseMakeResult):
    def get_code(self): return "btl_hoangbach_87"
    def get_name(self): return "Bạch thủ lô Hoàng Bách 87"
    def get_description(self): return "Tổng từ giải giai_db.1 + 3.4.1 + 5.4.4 và giải 1.1.4 + 3.3.3 + 6.3.2"
    def calculate(self, data): return self._make_result(data, [('giai_db', 0), ('giai_3_4', 0), ('giai_5_4', 3)], [('giai_1', 3), ('giai_3_3', 2), ('giai_6_3', 1)])

class Btl_HoangBach88LotoMethod(BasePredictionMethod, BaseMakeResult):
    def get_code(self): return "btl_hoangbach_88"
    def get_name(self): return "Bạch thủ lô Hoàng Bách 88"
    def get_description(self): return "Tổng từ giải giai_db.2 + 3.4.3 + 6.3.3 và giải 3.4.3 + 3.5.1 + 5.3.3"
    def calculate(self, data): return self._make_result(data, [('giai_db', 1), ('giai_3_4', 2), ('giai_6_3', 2)], [('giai_3_4', 2), ('giai_3_5', 0), ('giai_5_3', 2)])

class Btl_HoangBach89LotoMethod(BasePredictionMethod, BaseMakeResult):
    def get_code(self): return "btl_hoangbach_89"
    def get_name(self): return "Bạch thủ lô Hoàng Bách 89"
    def get_description(self): return "Tổng từ giải 2.1.3 + 4.2.3 + 5.2.2 và giải 3.1.2 + 5.4.3 + 7.2.1"
    def calculate(self, data): return self._make_result(data, [('giai_2_1', 2), ('giai_4_2', 2), ('giai_5_2', 1)], [('giai_3_1', 1), ('giai_5_4', 2), ('giai_7_2', 0)])

class Btl_HoangBach90LotoMethod(BasePredictionMethod, BaseMakeResult):
    def get_code(self): return "btl_hoangbach_90"
    def get_name(self): return "Bạch thủ lô Hoàng Bách 90"
    def get_description(self): return "Tổng từ giải giai_db.2 + giai_db.4 + 3.1.3 và giải 3.2.1 + 3.4.5 + 4.1.1"
    def calculate(self, data): return self._make_result(data, [('giai_db', 1), ('giai_db', 3), ('giai_3_1', 2)], [('giai_3_2', 0), ('giai_3_4', 4), ('giai_4_1', 0)])

class Btl_HoangBach91LotoMethod(BasePredictionMethod, BaseMakeResult):
    def get_code(self): return "btl_hoangbach_91"
    def get_name(self): return "Bạch thủ lô Hoàng Bách 91"
    def get_description(self): return "Tổng từ giải 2.2.5 + 3.4.2 + 7.3.1 và giải 3.1.5 + 3.2.5 + 3.3.2"
    def calculate(self, data): return self._make_result(data, [('giai_2_2', 4), ('giai_3_4', 1), ('giai_7_3', 0)], [('giai_3_1', 4), ('giai_3_2', 4), ('giai_3_3', 1)])

class Btl_HoangBach92LotoMethod(BasePredictionMethod, BaseMakeResult):
    def get_code(self): return "btl_hoangbach_92"
    def get_name(self): return "Bạch thủ lô Hoàng Bách 92"
    def get_description(self): return "Tổng từ giải 3.2.1 + 4.1.2 + 5.4.1 và giải giai_db.5 + 2.2.5 + 4.4.2"
    def calculate(self, data): return self._make_result(data, [('giai_3_2', 0), ('giai_4_1', 1), ('giai_5_4', 0)], [('giai_db', 4), ('giai_2_2', 4), ('giai_4_4', 1)])

class Btl_HoangBach93LotoMethod(BasePredictionMethod, BaseMakeResult):
    def get_code(self): return "btl_hoangbach_93"
    def get_name(self): return "Bạch thủ lô Hoàng Bách 93"
    def get_description(self): return "Tổng từ giải 2.2.3 + 5.2.2 + 7.3.1 và giải 3.2.3 + 4.1.4 + 5.6.4"
    def calculate(self, data): return self._make_result(data, [('giai_2_2', 2), ('giai_5_2', 1), ('giai_7_3', 0)], [('giai_3_2', 2), ('giai_4_1', 3), ('giai_5_6', 3)])

class Btl_HoangBach94LotoMethod(BasePredictionMethod, BaseMakeResult):
    def get_code(self): return "btl_hoangbach_94"
    def get_name(self): return "Bạch thủ lô Hoàng Bách 94"
    def get_description(self): return "Tổng từ giải giai_db.2 + 2.1.1 + 5.1.4 và giải 1.1.4 + 3.3.5 + 5.3.1"
    def calculate(self, data): return self._make_result(data, [('giai_db', 1), ('giai_2_1', 0), ('giai_5_1', 3)], [('giai_1', 3), ('giai_3_3', 4), ('giai_5_3', 0)])

class Btl_HoangBach95LotoMethod(BasePredictionMethod, BaseMakeResult):
    def get_code(self): return "btl_hoangbach_95"
    def get_name(self): return "Bạch thủ lô Hoàng Bách 95"
    def get_description(self): return "Tổng từ giải 1.1.3 + 3.2.3 + 3.6.1 và giải 2.1.3 + 5.1.3 + 5.5.2"
    def calculate(self, data): return self._make_result(data, [('giai_1', 2), ('giai_3_2', 2), ('giai_3_6', 0)], [('giai_2_1', 2), ('giai_5_1', 2), ('giai_5_5', 1)])

class Btl_HoangBach96LotoMethod(BasePredictionMethod, BaseMakeResult):
    def get_code(self): return "btl_hoangbach_96"
    def get_name(self): return "Bạch thủ lô Hoàng Bách 96"
    def get_description(self): return "Tổng từ giải 2.2.3 + 5.2.2 + 7.3.1 và giải 3.2.3 + 4.1.4 + 5.6.4"
    def calculate(self, data): return self._make_result(data, [('giai_2_2', 2), ('giai_5_2', 1), ('giai_7_3', 0)], [('giai_3_2', 2), ('giai_4_1', 3), ('giai_5_6', 3)])

class Btl_HoangBach97LotoMethod(BasePredictionMethod, BaseMakeResult):
    def get_code(self): return "btl_hoangbach_97"
    def get_name(self): return "Bạch thủ lô Hoàng Bách 97"
    def get_description(self): return "Tổng từ giải 1.1.2 + 1.1.3 + 2.1.5 và giải 2.2.4 + 2.2.5 + 4.3.4"
    def calculate(self, data): return self._make_result(data, [('giai_1', 1), ('giai_1', 2), ('giai_2_1', 4)], [('giai_2_2', 3), ('giai_2_2', 4), ('giai_4_3', 3)])

class Btl_HoangBach98LotoMethod(BasePredictionMethod, BaseMakeResult):
    def get_code(self): return "btl_hoangbach_98"
    def get_name(self): return "Bạch thủ lô Hoàng Bách 98"
    def get_description(self): return "Tổng từ giải 1.1.2 + 1.1.3 + 2.1.5 và giải 3.4.4 + 5.5.2 + 5.6.3"
    def calculate(self, data): return self._make_result(data, [('giai_1', 1), ('giai_1', 2), ('giai_2_1', 4)], [('giai_3_4', 3), ('giai_5_5', 1), ('giai_5_6', 2)])

class Btl_HoangBach99LotoMethod(BasePredictionMethod, BaseMakeResult):
    def get_code(self): return "btl_hoangbach_99"
    def get_name(self): return "Bạch thủ lô Hoàng Bách 99"
    def get_description(self): return "Tổng từ giải 1.1.2 + 3.6.3 + 6.2.2 và giải 2.2.1 + 5.3.2 + 5.5.1"
    def calculate(self, data): return self._make_result(data, [('giai_1', 1), ('giai_3_6', 2), ('giai_6_2', 1)], [('giai_2_2', 0), ('giai_5_3', 1), ('giai_5_5', 0)])

class Btl_HoangBach100LotoMethod(BasePredictionMethod, BaseMakeResult):
    def get_code(self): return "btl_hoangbach_100"
    def get_name(self): return "Bạch thủ lô Hoàng Bách 100"
    def get_description(self): return "Tổng từ giải 1.1.2 + 3.6.3 + 6.2.2 và giải giai_db.1 + giai_db.3 + 5.1.2"
    def calculate(self, data): return self._make_result(data, [('giai_1', 1), ('giai_3_6', 2), ('giai_6_2', 1)], [('giai_db', 0), ('giai_db', 2), ('giai_5_1', 1)])

class Btl_HoangBach101LotoMethod(BasePredictionMethod, BaseMakeResult):
    def get_code(self): return "btl_hoangbach_101"
    def get_name(self): return "Bạch thủ lô Hoàng Bách 101"
    def get_description(self): return "Tổng từ giải 1.1.4 + 3.5.3 + 7.1.1 và giải 1.1.3 + 3.4.2 + 3.4.4"
    def calculate(self, data): return self._make_result(data, [('giai_1', 3), ('giai_3_5', 2), ('giai_7_1', 0)], [('giai_1', 2), ('giai_3_4', 1), ('giai_3_4', 3)])

class Btl_HoangBach102LotoMethod(BasePredictionMethod, BaseMakeResult):
    def get_code(self): return "btl_hoangbach_102"
    def get_name(self): return "Bạch thủ lô Hoàng Bách 102"
    def get_description(self): return "Tổng từ giải 2.1.5 + 3.1.4 + 3.3.3 và giải 3.6.2 + 5.6.3 + 7.4.2"
    def calculate(self, data): return self._make_result(data, [('giai_2_1', 4), ('giai_3_1', 3), ('giai_3_3', 2)], [('giai_3_6', 1), ('giai_5_6', 2), ('giai_7_4', 1)])

class Btl_HoangBach103LotoMethod(BasePredictionMethod, BaseMakeResult):
    def get_code(self): return "btl_hoangbach_103"
    def get_name(self): return "Bạch thủ lô Hoàng Bách 103"
    def get_description(self): return "Tổng từ giải 3.3.2 + 3.5.5 + 4.2.2 và giải 1.1.3 + 4.1.2 + 5.1.3"
    def calculate(self, data): return self._make_result(data, [('giai_3_3', 1), ('giai_3_5', 4), ('giai_4_2', 1)], [('giai_1', 2), ('giai_4_1', 1), ('giai_5_1', 2)])

class Btl_HoangBach104LotoMethod(BasePredictionMethod, BaseMakeResult):
    def get_code(self): return "btl_hoangbach_104"
    def get_name(self): return "Bạch thủ lô Hoàng Bách 104"
    def get_description(self): return "Tổng từ giải 3.2.2 + 3.6.1 + 5.1.3 và giải giai_db.5 + 1.1.1 + 5.2.4"
    def calculate(self, data): return self._make_result(data, [('giai_3_2', 1), ('giai_3_6', 0), ('giai_5_1', 2)], [('giai_db', 4), ('giai_1', 0), ('giai_5_2', 3)])

class Btl_HoangBach105LotoMethod(BasePredictionMethod, BaseMakeResult):
    def get_code(self): return "btl_hoangbach_105"
    def get_name(self): return "Bạch thủ lô Hoàng Bách 105"
    def get_description(self): return "Tổng từ giải 2.2.4 + 3.1.1 + 7.1.2 và giải giai_db.2 + 2.1.4 + 3.2.5"
    def calculate(self, data): return self._make_result(data, [('giai_2_2', 3), ('giai_3_1', 0), ('giai_7_1', 1)], [('giai_db', 1), ('giai_2_1', 3), ('giai_3_2', 4)])

class Btl_HoangBach106LotoMethod(BasePredictionMethod, BaseMakeResult):
    def get_code(self): return "btl_hoangbach_106"
    def get_name(self): return "Bạch thủ lô Hoàng Bách 106"
    def get_description(self): return "Tổng từ giải 5.2.4 + 5.4.3 + 5.5.4 và giải 3.4.2 + 3.4.3 + 4.3.3"
    def calculate(self, data): return self._make_result(data, [('giai_5_2', 3), ('giai_5_4', 2), ('giai_5_5', 3)], [('giai_3_4', 1), ('giai_3_4', 2), ('giai_4_3', 2)])

class Btl_HoangBach107LotoMethod(BasePredictionMethod, BaseMakeResult):
    def get_code(self): return "btl_hoangbach_107"
    def get_name(self): return "Bạch thủ lô Hoàng Bách 107"
    def get_description(self): return "Tổng từ giải 2.1.4 + 2.2.3 + 7.3.2 và giải 1.1.1 + 3.2.3 + 5.5.2"
    def calculate(self, data): return self._make_result(data, [('giai_2_1', 3), ('giai_2_2', 2), ('giai_7_3', 1)], [('giai_1', 0), ('giai_3_2', 2), ('giai_5_5', 1)])

class Btl_HoangBach108LotoMethod(BasePredictionMethod, BaseMakeResult):
    def get_code(self): return "btl_hoangbach_108"
    def get_name(self): return "Bạch thủ lô Hoàng Bách 108"
    def get_description(self): return "Tổng từ giải giai_db.3 + 1.1.3 + 3.4.5 và giải 3.3.2 + 3.6.2 + 5.5.4"
    def calculate(self, data): return self._make_result(data, [('giai_db', 2), ('giai_1', 2), ('giai_3_4', 4)], [('giai_3_3', 1), ('giai_3_6', 1), ('giai_5_5', 3)])

class Btl_HoangBach109LotoMethod(BasePredictionMethod, BaseMakeResult):
    def get_code(self): return "btl_hoangbach_109"
    def get_name(self): return "Bạch thủ lô Hoàng Bách 109"
    def get_description(self): return "Tổng từ giải giai_db.5 + 5.2.3 + 5.5.2 và giải 2.2.3 + 3.3.3 + 4.1.1"
    def calculate(self, data): return self._make_result(data, [('giai_db', 4), ('giai_5_2', 2), ('giai_5_5', 1)], [('giai_2_2', 2), ('giai_3_3', 2), ('giai_4_1', 0)])

class Btl_HoangBach110LotoMethod(BasePredictionMethod, BaseMakeResult):
    def get_code(self): return "btl_hoangbach_110"
    def get_name(self): return "Bạch thủ lô Hoàng Bách 110"
    def get_description(self): return "Tổng từ giải 3.5.1 + 5.4.3 + 5.6.1 và giải giai_db.1 + 1.1.1 + 5.5.1"
    def calculate(self, data): return self._make_result(data, [('giai_3_5', 0), ('giai_5_4', 2), ('giai_5_6', 0)], [('giai_db', 0), ('giai_1', 0), ('giai_5_5', 0)])

class Btl_HoangBach111LotoMethod(BasePredictionMethod, BaseMakeResult):
    def get_code(self): return "btl_hoangbach_111"
    def get_name(self): return "Bạch thủ lô Hoàng Bách 111"
    def get_description(self): return "Tổng từ giải giai_db.2 + 2.2.4 + 2.2.5 và giải 2.1.4 + 2.1.5 + 4.2.1"
    def calculate(self, data): return self._make_result(data, [('giai_db', 1), ('giai_2_2', 3), ('giai_2_2', 4)], [('giai_2_1', 3), ('giai_2_1', 4), ('giai_4_2', 0)])

class Btl_HoangBach112LotoMethod(BasePredictionMethod, BaseMakeResult):
    def get_code(self): return "btl_hoangbach_112"
    def get_name(self): return "Bạch thủ lô Hoàng Bách 112"
    def get_description(self): return "Tổng từ giải 1.1.3 + 3.4.4 + 3.6.4 và giải 1.1.3 + 4.3.1 + 5.1.3"
    def calculate(self, data): return self._make_result(data, [('giai_1', 2), ('giai_3_4', 3), ('giai_3_6', 3)], [('giai_1', 2), ('giai_4_3', 0), ('giai_5_1', 2)])

class Btl_HoangBach113LotoMethod(BasePredictionMethod, BaseMakeResult):
    def get_code(self): return "btl_hoangbach_113"
    def get_name(self): return "Bạch thủ lô Hoàng Bách 113"
    def get_description(self): return "Tổng từ giải 1.1.5 + 3.1.1 + 4.4.1 và giải giai_db.2 + 5.1.4 + 5.3.2"
    def calculate(self, data): return self._make_result(data, [('giai_1', 4), ('giai_3_1', 0), ('giai_4_4', 0)], [('giai_db', 1), ('giai_5_1', 3), ('giai_5_3', 1)])

class Btl_HoangBach114LotoMethod(BasePredictionMethod, BaseMakeResult):
    def get_code(self): return "btl_hoangbach_114"
    def get_name(self): return "Bạch thủ lô Hoàng Bách 114"
    def get_description(self): return "Tổng từ giải 1.1.3 + 3.1.1 + 6.2.3 và giải giai_db.4 + 4.2.3 + 5.6.4"
    def calculate(self, data): return self._make_result(data, [('giai_1', 2), ('giai_3_1', 0), ('giai_6_2', 2)], [('giai_db', 3), ('giai_4_2', 2), ('giai_5_6', 3)])

class Btl_HoangBach115LotoMethod(BasePredictionMethod, BaseMakeResult):
    def get_code(self): return "btl_hoangbach_115"
    def get_name(self): return "Bạch thủ lô Hoàng Bách 115"
    def get_description(self): return "Tổng từ giải 2.2.5 + 3.3.4 + 5.1.4 và giải giai_db.2 + 3.4.3 + 5.6.1"
    def calculate(self, data): return self._make_result(data, [('giai_2_2', 4), ('giai_3_3', 3), ('giai_5_1', 3)], [('giai_db', 1), ('giai_3_4', 2), ('giai_5_6', 0)])

class Btl_HoangBach116LotoMethod(BasePredictionMethod, BaseMakeResult):
    def get_code(self): return "btl_hoangbach_116"
    def get_name(self): return "Bạch thủ lô Hoàng Bách 116"
    def get_description(self): return "Tổng từ giải giai_db.2 + 3.3.1 + 3.4.4 và giải giai_db.2 + 3.5.2 + 7.4.1"
    def calculate(self, data): return self._make_result(data, [('giai_db', 1), ('giai_3_3', 0), ('giai_3_4', 3)], [('giai_db', 1), ('giai_3_5', 1), ('giai_7_4', 0)])

class Btl_HoangBach117LotoMethod(BasePredictionMethod, BaseMakeResult):
    def get_code(self): return "btl_hoangbach_117"
    def get_name(self): return "Bạch thủ lô Hoàng Bách 117"
    def get_description(self): return "Tổng từ giải giai_db.3 + 4.1.1 + 5.4.2 và giải 2.1.1 + 5.1.3 + 6.1.3"
    def calculate(self, data): return self._make_result(data, [('giai_db', 2), ('giai_4_1', 0), ('giai_5_4', 1)], [('giai_2_1', 0), ('giai_5_1', 2), ('giai_6_1', 2)])

class Btl_HoangBach118LotoMethod(BasePredictionMethod, BaseMakeResult):
    def get_code(self): return "btl_hoangbach_118"
    def get_name(self): return "Bạch thủ lô Hoàng Bách 118"
    def get_description(self): return "Tổng từ giải giai_db.2 + 5.3.2 + 5.5.4 và giải 3.2.1 + 3.6.5 + 6.1.3"
    def calculate(self, data): return self._make_result(data, [('giai_db', 1), ('giai_5_3', 1), ('giai_5_5', 3)], [('giai_3_2', 0), ('giai_3_6', 4), ('giai_6_1', 2)])

class Btl_HoangBach119LotoMethod(BasePredictionMethod, BaseMakeResult):
    def get_code(self): return "btl_hoangbach_119"
    def get_name(self): return "Bạch thủ lô Hoàng Bách 119"
    def get_description(self): return "Tổng từ giải giai_db.4 + 2.2.3 + 3.2.3 và giải giai_db.1 + 4.3.2 + 6.3.2"
    def calculate(self, data): return self._make_result(data, [('giai_db', 3), ('giai_2_2', 2), ('giai_3_2', 2)], [('giai_db', 0), ('giai_4_3', 1), ('giai_6_3', 1)])

class Btl_HoangBach120LotoMethod(BasePredictionMethod, BaseMakeResult):
    def get_code(self): return "btl_hoangbach_120"
    def get_name(self): return "Bạch thủ lô Hoàng Bách 120"
    def get_description(self): return "Tổng từ giải 2.2.3 + 5.3.4 + 7.2.2 và giải giai_db.4 + 4.2.3 + 5.6.4"
    def calculate(self, data): return self._make_result(data, [('giai_2_2', 2), ('giai_5_3', 3), ('giai_7_2', 1)], [('giai_db', 3), ('giai_4_2', 2), ('giai_5_6', 3)])

class Btl_HoangBach121LotoMethod(BasePredictionMethod, BaseMakeResult):
    def get_code(self): return "btl_hoangbach_121"
    def get_name(self): return "Bạch thủ lô Hoàng Bách 121"
    def get_description(self): return "Tổng từ giải 1.1.5 + 3.1.1 + 4.4.1 và giải giai_db.2 + 5.1.4 + 5.3.2"
    def calculate(self, data): return self._make_result(data, [('giai_1', 4), ('giai_3_1', 0), ('giai_4_4', 0)], [('giai_db', 1), ('giai_5_1', 3), ('giai_5_3', 1)])

class Btl_HoangBach122LotoMethod(BasePredictionMethod, BaseMakeResult):
    def get_code(self): return "btl_hoangbach_122"
    def get_name(self): return "Bạch thủ lô Hoàng Bách 122"
    def get_description(self): return "Tổng từ giải 1.1.3 + 3.1.4 + 4.4.4 và giải 3.1.4 + 5.4.4 + 6.3.3"
    def calculate(self, data): return self._make_result(data, [('giai_1', 2), ('giai_3_1', 3), ('giai_4_4', 3)], [('giai_3_1', 3), ('giai_5_4', 3), ('giai_6_3', 2)])

class Btl_HoangBach123LotoMethod(BasePredictionMethod, BaseMakeResult):
    def get_code(self): return "btl_hoangbach_123"
    def get_name(self): return "Bạch thủ lô Hoàng Bách 123"
    def get_description(self): return "Tổng từ giải giai_db.3 + 2.1.2 + 3.2.2 và giải 2.1.3 + 3.1.4 + 6.2.1"
    def calculate(self, data): return self._make_result(data, [('giai_db', 2), ('giai_2_1', 1), ('giai_3_2', 1)], [('giai_2_1', 2), ('giai_3_1', 3), ('giai_6_2', 0)])

class Btl_HoangBach124LotoMethod(BasePredictionMethod, BaseMakeResult):
    def get_code(self): return "btl_hoangbach_124"
    def get_name(self): return "Bạch thủ lô Hoàng Bách 124"
    def get_description(self): return "Tổng từ giải 5.6.2 + 5.6.3 + 5.6.4 và giải 3.3.3 + 3.3.4 + 3.3.5"
    def calculate(self, data): return self._make_result(data, [('giai_5_6', 1), ('giai_5_6', 2), ('giai_5_6', 3)], [('giai_3_3', 2), ('giai_3_3', 3), ('giai_3_3', 4)])

class Btl_HoangBach125LotoMethod(BasePredictionMethod, BaseMakeResult):
    def get_code(self): return "btl_hoangbach_125"
    def get_name(self): return "Bạch thủ lô Hoàng Bách 125"
    def get_description(self): return "Tổng từ giải 1.1.5 + 4.3.3 + 5.3.2 và giải giai_db.1 + 5.1.4 + 6.3.2"
    def calculate(self, data): return self._make_result(data, [('giai_1', 4), ('giai_4_3', 2), ('giai_5_3', 1)], [('giai_db', 0), ('giai_5_1', 3), ('giai_6_3', 1)])

class Btl_HoangBach126LotoMethod(BasePredictionMethod, BaseMakeResult):
    def get_code(self): return "btl_hoangbach_126"
    def get_name(self): return "Bạch thủ lô Hoàng Bách 126"
    def get_description(self): return "Tổng từ giải 2.2.1 + 2.2.2 + 2.2.3 và giải 4.4.1 + 4.4.2 + 4.4.3"
    def calculate(self, data): return self._make_result(data, [('giai_2_2', 0), ('giai_2_2', 1), ('giai_2_2', 2)], [('giai_4_4', 0), ('giai_4_4', 1), ('giai_4_4', 2)])

class Btl_HoangBach127LotoMethod(BasePredictionMethod, BaseMakeResult):
    def get_code(self): return "btl_hoangbach_127"
    def get_name(self): return "Bạch thủ lô Hoàng Bách 127"
    def get_description(self): return "Tổng từ giải 2.1.1 + 2.2.5 + 5.2.4 và giải 2.2.2 + 4.1.4 + 5.6.3"
    def calculate(self, data): return self._make_result(data, [('giai_2_1', 0), ('giai_2_2', 4), ('giai_5_2', 3)], [('giai_2_2', 1), ('giai_4_1', 3), ('giai_5_6', 2)])

class Btl_HoangBach128LotoMethod(BasePredictionMethod, BaseMakeResult):
    def get_code(self): return "btl_hoangbach_128"
    def get_name(self): return "Bạch thủ lô Hoàng Bách 128"
    def get_description(self): return "Tổng từ giải 2.1.4 + 3.4.5 + 3.6.3 và giải giai_db.5 + 5.2.2 + 6.2.3"
    def calculate(self, data): return self._make_result(data, [('giai_2_1', 3), ('giai_3_4', 4), ('giai_3_6', 2)], [('giai_db', 4), ('giai_5_2', 1), ('giai_6_2', 2)])

class Btl_HoangBach129LotoMethod(BasePredictionMethod, BaseMakeResult):
    def get_code(self): return "btl_hoangbach_129"
    def get_name(self): return "Bạch thủ lô Hoàng Bách 129"
    def get_description(self): return "Tổng từ giải 1.1.2 + 3.6.4 + 4.4.2 và giải 2.1.3 + 4.1.1 + 4.3.4"
    def calculate(self, data): return self._make_result(data, [('giai_1', 1), ('giai_3_6', 3), ('giai_4_4', 1)], [('giai_2_1', 2), ('giai_4_1', 0), ('giai_4_3', 3)])

class Btl_HoangBach130LotoMethod(BasePredictionMethod, BaseMakeResult):
    def get_code(self): return "btl_hoangbach_130"
    def get_name(self): return "Bạch thủ lô Hoàng Bách 130"
    def get_description(self): return "Tổng từ giải 2.2.5 + 3.1.3 + 7.1.2 và giải 2.1.1 + 3.2.2 + 5.2.2"
    def calculate(self, data): return self._make_result(data, [('giai_2_2', 4), ('giai_3_1', 2), ('giai_7_1', 1)], [('giai_2_1', 0), ('giai_3_2', 1), ('giai_5_2', 1)])

class Btl_HoangBach131LotoMethod(BasePredictionMethod, BaseMakeResult):
    def get_code(self): return "btl_hoangbach_131"
    def get_name(self): return "Bạch thủ lô Hoàng Bách 131"
    def get_description(self): return "Tổng từ giải 2.1.5 + 3.2.1 + 3.5.2 và giải 4.1.4 + 5.3.2 + 5.5.2"
    def calculate(self, data): return self._make_result(data, [('giai_2_1', 4), ('giai_3_2', 0), ('giai_3_5', 1)], [('giai_4_1', 3), ('giai_5_3', 1), ('giai_5_5', 1)])

class Btl_HoangBach132LotoMethod(BasePredictionMethod, BaseMakeResult):
    def get_code(self): return "btl_hoangbach_132"
    def get_name(self): return "Bạch thủ lô Hoàng Bách 132"
    def get_description(self): return "Tổng từ giải 2.2.3 + 2.2.4 + 2.2.5 và giải 3.6.2 + 3.6.3 + 3.6.4"
    def calculate(self, data): return self._make_result(data, [('giai_2_2', 2), ('giai_2_2', 3), ('giai_2_2', 4)], [('giai_3_6', 1), ('giai_3_6', 2), ('giai_3_6', 3)])

class Btl_HoangBach133LotoMethod(BasePredictionMethod, BaseMakeResult):
    def get_code(self): return "btl_hoangbach_133"
    def get_name(self): return "Bạch thủ lô Hoàng Bách 133"
    def get_description(self): return "Tổng từ giải 3.1.2 + 3.3.5 + 3.5.4 và giải 3.4.1 + 4.3.4 + 7.4.2"
    def calculate(self, data): return self._make_result(data, [('giai_3_1', 1), ('giai_3_3', 4), ('giai_3_5', 3)], [('giai_3_4', 0), ('giai_4_3', 3), ('giai_7_4', 1)])

class Btl_HoangBach134LotoMethod(BasePredictionMethod, BaseMakeResult):
    def get_code(self): return "btl_hoangbach_134"
    def get_name(self): return "Bạch thủ lô Hoàng Bách 134"
    def get_description(self): return "Tổng từ giải 3.6.1 + 4.2.2 + 7.2.2 và giải 2.1.2 + 3.1.5 + 3.5.2"
    def calculate(self, data): return self._make_result(data, [('giai_3_6', 0), ('giai_4_2', 1), ('giai_7_2', 1)], [('giai_2_1', 1), ('giai_3_1', 4), ('giai_3_5', 1)])

class Btl_HoangBach135LotoMethod(BasePredictionMethod, BaseMakeResult):
    def get_code(self): return "btl_hoangbach_135"
    def get_name(self): return "Bạch thủ lô Hoàng Bách 135"
    def get_description(self): return "Tổng từ giải 4.4.2 + 4.4.3 + 4.4.4 và giải 3.6.3 + 3.6.4 + 3.6.5"
    def calculate(self, data): return self._make_result(data, [('giai_4_4', 1), ('giai_4_4', 2), ('giai_4_4', 3)], [('giai_3_6', 2), ('giai_3_6', 3), ('giai_3_6', 4)])

class Btl_HoangBach136LotoMethod(BasePredictionMethod, BaseMakeResult):
    def get_code(self): return "btl_hoangbach_136"
    def get_name(self): return "Bạch thủ lô Hoàng Bách 136"
    def get_description(self): return "Tổng từ giải 3.2.2 + 3.5.5 + 6.2.2 và giải 2.2.2 + 2.2.3 + 6.1.3"
    def calculate(self, data): return self._make_result(data, [('giai_3_2', 1), ('giai_3_5', 4), ('giai_6_2', 1)], [('giai_2_2', 1), ('giai_2_2', 2), ('giai_6_1', 2)])

class Btl_HoangBach137LotoMethod(BasePredictionMethod, BaseMakeResult):
    def get_code(self): return "btl_hoangbach_137"
    def get_name(self): return "Bạch thủ lô Hoàng Bách 137"
    def get_description(self): return "Tổng từ giải 2.2.4 + 3.2.5 + 7.2.1 và giải 2.1.1 + 3.2.3 + 5.4.4"
    def calculate(self, data): return self._make_result(data, [('giai_2_2', 3), ('giai_3_2', 4), ('giai_7_2', 0)], [('giai_2_1', 0), ('giai_3_2', 2), ('giai_5_4', 3)])

class Btl_HoangBach138LotoMethod(BasePredictionMethod, BaseMakeResult):
    def get_code(self): return "btl_hoangbach_138"
    def get_name(self): return "Bạch thủ lô Hoàng Bách 138"
    def get_description(self): return "Tổng từ giải 3.5.5 + 5.1.3 + 5.2.4 và giải 2.2.5 + 3.6.2 + 6.2.2"
    def calculate(self, data): return self._make_result(data, [('giai_3_5', 4), ('giai_5_1', 2), ('giai_5_2', 3)], [('giai_2_2', 4), ('giai_3_6', 1), ('giai_6_2', 1)])

class Btl_HoangBach139LotoMethod(BasePredictionMethod, BaseMakeResult):
    def get_code(self): return "btl_hoangbach_139"
    def get_name(self): return "Bạch thủ lô Hoàng Bách 139"
    def get_description(self): return "Tổng từ giải 2.1.1 + 4.2.4 + 4.4.4 và giải 4.4.2 + 5.4.2 + 6.3.3"
    def calculate(self, data): return self._make_result(data, [('giai_2_1', 0), ('giai_4_2', 3), ('giai_4_4', 3)], [('giai_4_4', 1), ('giai_5_4', 1), ('giai_6_3', 2)])

class Btl_HoangBach140LotoMethod(BasePredictionMethod, BaseMakeResult):
    def get_code(self): return "btl_hoangbach_140"
    def get_name(self): return "Bạch thủ lô Hoàng Bách 140"
    def get_description(self): return "Tổng từ giải 1.1.3 + 1.1.4 + 1.1.5 và giải giai_db.2 + giai_db.3 + giai_db.4"
    def calculate(self, data): return self._make_result(data, [('giai_1', 2), ('giai_1', 3), ('giai_1', 4)], [('giai_db', 1), ('giai_db', 2), ('giai_db', 3)])

class Btl_HoangBach141LotoMethod(BasePredictionMethod, BaseMakeResult):
    def get_code(self): return "btl_hoangbach_141"
    def get_name(self): return "Bạch thủ lô Hoàng Bách 141"
    def get_description(self): return "Tổng từ giải 4.4.2 + 5.6.3 + 6.2.3 và giải 1.1.1 + 2.1.5 + 5.6.3"
    def calculate(self, data): return self._make_result(data, [('giai_4_4', 1), ('giai_5_6', 2), ('giai_6_2', 2)], [('giai_1', 0), ('giai_2_1', 4), ('giai_5_6', 2)])

class Btl_HoangBach142LotoMethod(BasePredictionMethod, BaseMakeResult):
    def get_code(self): return "btl_hoangbach_142"
    def get_name(self): return "Bạch thủ lô Hoàng Bách 142"
    def get_description(self): return "Tổng từ giải 3.4.3 + 3.4.4 + 3.4.5 và giải 4.2.1 + 4.2.2 + 4.2.3"
    def calculate(self, data): return self._make_result(data, [('giai_3_4', 2), ('giai_3_4', 3), ('giai_3_4', 4)], [('giai_4_2', 0), ('giai_4_2', 1), ('giai_4_2', 2)])

class Btl_HoangBach143LotoMethod(BasePredictionMethod, BaseMakeResult):
    def get_code(self): return "btl_hoangbach_143"
    def get_name(self): return "Bạch thủ lô Hoàng Bách 143"
    def get_description(self): return "Tổng từ giải 2.1.5 + 5.3.4 + 7.2.1 và giải 3.6.5 + 4.1.2 + 4.3.3"
    def calculate(self, data): return self._make_result(data, [('giai_2_1', 4), ('giai_5_3', 3), ('giai_7_2', 0)], [('giai_3_6', 4), ('giai_4_1', 1), ('giai_4_3', 2)])

class Btl_HoangBach144LotoMethod(BasePredictionMethod, BaseMakeResult):
    def get_code(self): return "btl_hoangbach_144"
    def get_name(self): return "Bạch thủ lô Hoàng Bách 144"
    def get_description(self): return "Tổng từ giải 1.1.4 + 7.2.1 + 7.3.2 và giải 3.3.3 + 3.4.5 + 3.6.4"
    def calculate(self, data): return self._make_result(data, [('giai_1', 3), ('giai_7_2', 0), ('giai_7_3', 1)], [('giai_3_3', 2), ('giai_3_4', 4), ('giai_3_6', 3)])

class Btl_HoangBach145LotoMethod(BasePredictionMethod, BaseMakeResult):
    def get_code(self): return "btl_hoangbach_145"
    def get_name(self): return "Bạch thủ lô Hoàng Bách 145"
    def get_description(self): return "Tổng từ giải 2.2.4 + 3.2.5 + 5.6.3 và giải giai_db.4 + 2.2.1 + 3.2.3"
    def calculate(self, data): return self._make_result(data, [('giai_2_2', 3), ('giai_3_2', 4), ('giai_5_6', 2)], [('giai_db', 3), ('giai_2_2', 0), ('giai_3_2', 2)])

class Btl_HoangBach146LotoMethod(BasePredictionMethod, BaseMakeResult):
    def get_code(self): return "btl_hoangbach_146"
    def get_name(self): return "Bạch thủ lô Hoàng Bách 146"
    def get_description(self): return "Tổng từ giải 2.1.4 + 3.3.1 + 7.4.2 và giải 3.3.3 + 3.4.5 + 3.6.4"
    def calculate(self, data): return self._make_result(data, [('giai_2_1', 3), ('giai_3_3', 0), ('giai_7_4', 1)], [('giai_3_3', 2), ('giai_3_4', 4), ('giai_3_6', 3)])

class Btl_HoangBach147LotoMethod(BasePredictionMethod, BaseMakeResult):
    def get_code(self): return "btl_hoangbach_147"
    def get_name(self): return "Bạch thủ lô Hoàng Bách 147"
    def get_description(self): return "Tổng từ giải giai_db.1 + 3.3.5 + 4.3.3 và giải 1.1.4 + 4.1.3 + 5.6.1"
    def calculate(self, data): return self._make_result(data, [('giai_db', 0), ('giai_3_3', 4), ('giai_4_3', 2)], [('giai_1', 3), ('giai_4_1', 2), ('giai_5_6', 0)])

class Btl_HoangBach148LotoMethod(BasePredictionMethod, BaseMakeResult):
    def get_code(self): return "btl_hoangbach_148"
    def get_name(self): return "Bạch thủ lô Hoàng Bách 148"
    def get_description(self): return "Tổng từ giải 5.4.1 + 5.4.2 + 5.4.3 và giải 2.1.2 + 2.1.3 + 2.1.4"
    def calculate(self, data): return self._make_result(data, [('giai_5_4', 0), ('giai_5_4', 1), ('giai_5_4', 2)], [('giai_2_1', 1), ('giai_2_1', 2), ('giai_2_1', 3)])

class Btl_HoangBach149LotoMethod(BasePredictionMethod, BaseMakeResult):
    def get_code(self): return "btl_hoangbach_149"
    def get_name(self): return "Bạch thủ lô Hoàng Bách 149"
    def get_description(self): return "Tổng từ giải 2.1.1 + 3.6.3 + 5.6.1 và giải 2.1.5 + 4.4.4 + 5.6.3"
    def calculate(self, data): return self._make_result(data, [('giai_2_1', 0), ('giai_3_6', 2), ('giai_5_6', 0)], [('giai_2_1', 4), ('giai_4_4', 3), ('giai_5_6', 2)])

class Btl_HoangBach150LotoMethod(BasePredictionMethod, BaseMakeResult):
    def get_code(self): return "btl_hoangbach_150"
    def get_name(self): return "Bạch thủ lô Hoàng Bách 150"
    def get_description(self): return "Tổng từ giải 3.1.2 + 5.1.3 + 5.4.1 và giải 4.1.3 + 4.1.4 + 4.4.2"
    def calculate(self, data): return self._make_result(data, [('giai_3_1', 1), ('giai_5_1', 2), ('giai_5_4', 0)], [('giai_4_1', 2), ('giai_4_1', 3), ('giai_4_4', 1)])

class Btl_HoangBach151LotoMethod(BasePredictionMethod, BaseMakeResult):
    def get_code(self): return "btl_hoangbach_151"
    def get_name(self): return "Bạch thủ lô Hoàng Bách 151"
    def get_description(self): return "Tổng từ giải 1.1.1 + 5.2.2 + 6.2.3 và giải giai_db.3 + 2.1.3 + 4.2.4"
    def calculate(self, data): return self._make_result(data, [('giai_1', 0), ('giai_5_2', 1), ('giai_6_2', 2)], [('giai_db', 2), ('giai_2_1', 2), ('giai_4_2', 3)])

class Btl_HoangBach152LotoMethod(BasePredictionMethod, BaseMakeResult):
    def get_code(self): return "btl_hoangbach_152"
    def get_name(self): return "Bạch thủ lô Hoàng Bách 152"
    def get_description(self): return "Tổng từ giải 1.1.1 + 5.5.1 + 6.3.3 và giải 3.3.1 + 4.3.3 + 4.3.4"
    def calculate(self, data): return self._make_result(data, [('giai_1', 0), ('giai_5_5', 0), ('giai_6_3', 2)], [('giai_3_3', 0), ('giai_4_3', 2), ('giai_4_3', 3)])

class Btl_HoangBach153LotoMethod(BasePredictionMethod, BaseMakeResult):
    def get_code(self): return "btl_hoangbach_153"
    def get_name(self): return "Bạch thủ lô Hoàng Bách 153"
    def get_description(self): return "Tổng từ giải 1.1.2 + 3.6.4 + 4.4.2 và giải 2.1.3 + 4.1.1 + 4.3.4"
    def calculate(self, data): return self._make_result(data, [('giai_1', 1), ('giai_3_6', 3), ('giai_4_4', 1)], [('giai_2_1', 2), ('giai_4_1', 0), ('giai_4_3', 3)])

class Btl_HoangBach154LotoMethod(BasePredictionMethod, BaseMakeResult):
    def get_code(self): return "btl_hoangbach_154"
    def get_name(self): return "Bạch thủ lô Hoàng Bách 154"
    def get_description(self): return "Tổng từ giải 2.1.4 + 3.3.5 + 5.2.3 và giải giai_db.1 + 2.1.5 + 3.2.3"
    def calculate(self, data): return self._make_result(data, [('giai_2_1', 3), ('giai_3_3', 4), ('giai_5_2', 2)], [('giai_db', 0), ('giai_2_1', 4), ('giai_3_2', 2)])

class Btl_HoangBach155LotoMethod(BasePredictionMethod, BaseMakeResult):
    def get_code(self): return "btl_hoangbach_155"
    def get_name(self): return "Bạch thủ lô Hoàng Bách 155"
    def get_description(self): return "Tổng từ giải giai_db.2 + 3.1.1 + 5.3.3 và giải 3.1.4 + 5.1.1 + 5.1.2"
    def calculate(self, data): return self._make_result(data, [('giai_db', 1), ('giai_3_1', 0), ('giai_5_3', 2)], [('giai_3_1', 3), ('giai_5_1', 0), ('giai_5_1', 1)])

class Btl_HoangBach156LotoMethod(BasePredictionMethod, BaseMakeResult):
    def get_code(self): return "btl_hoangbach_156"
    def get_name(self): return "Bạch thủ lô Hoàng Bách 156"
    def get_description(self): return "Tổng từ giải 2.1.4 + 3.3.1 + 7.4.2 và giải 3.3.3 + 3.4.5 + 3.6.4"
    def calculate(self, data): return self._make_result(data, [('giai_2_1', 3), ('giai_3_3', 0), ('giai_7_4', 1)], [('giai_3_3', 2), ('giai_3_4', 4), ('giai_3_6', 3)])

class Btl_HoangBach157LotoMethod(BasePredictionMethod, BaseMakeResult):
    def get_code(self): return "btl_hoangbach_157"
    def get_name(self): return "Bạch thủ lô Hoàng Bách 157"
    def get_description(self): return "Tổng từ giải 3.1.2 + 3.3.5 + 3.5.4 và giải 3.4.1 + 4.3.4 + 7.4.2"
    def calculate(self, data): return self._make_result(data, [('giai_3_1', 1), ('giai_3_3', 4), ('giai_3_5', 3)], [('giai_3_4', 0), ('giai_4_3', 3), ('giai_7_4', 1)])

class Btl_HoangBach158LotoMethod(BasePredictionMethod, BaseMakeResult):
    def get_code(self): return "btl_hoangbach_158"
    def get_name(self): return "Bạch thủ lô Hoàng Bách 158"
    def get_description(self): return "Tổng từ giải giai_db.5 + 2.1.2 + 2.2.4 và giải 3.2.3 + 3.4.5 + 6.2.2"
    def calculate(self, data): return self._make_result(data, [('giai_db', 4), ('giai_2_1', 1), ('giai_2_2', 3)], [('giai_3_2', 2), ('giai_3_4', 4), ('giai_6_2', 1)])

class Btl_HoangBach159LotoMethod(BasePredictionMethod, BaseMakeResult):
    def get_code(self): return "btl_hoangbach_159"
    def get_name(self): return "Bạch thủ lô Hoàng Bách 159"
    def get_description(self): return "Tổng từ giải 2.1.1 + 5.4.3 + 5.4.4 và giải 2.1.1 + 3.6.1 + 4.2.2"
    def calculate(self, data): return self._make_result(data, [('giai_2_1', 0), ('giai_5_4', 2), ('giai_5_4', 3)], [('giai_2_1', 0), ('giai_3_6', 0), ('giai_4_2', 1)])

class Btl_HoangBach160LotoMethod(BasePredictionMethod, BaseMakeResult):
    def get_code(self): return "btl_hoangbach_160"
    def get_name(self): return "Bạch thủ lô Hoàng Bách 160"
    def get_description(self): return "Tổng từ giải 5.5.4 + 5.6.1 + 5.6.2 và giải 6.3.1 + 6.3.2 + 6.3.3"
    def calculate(self, data): return self._make_result(data, [('giai_5_5', 3), ('giai_5_6', 0), ('giai_5_6', 1)], [('giai_6_3', 0), ('giai_6_3', 1), ('giai_6_3', 2)])

class Btl_HoangBach161LotoMethod(BasePredictionMethod, BaseMakeResult):
    def get_code(self): return "btl_hoangbach_161"
    def get_name(self): return "Bạch thủ lô Hoàng Bách 161"
    def get_description(self): return "Tổng từ giải 3.5.4 + 5.4.4 + 6.1.2 và giải 2.1.3 + 3.5.1 + 4.1.4"
    def calculate(self, data): return self._make_result(data, [('giai_3_5', 3), ('giai_5_4', 3), ('giai_6_1', 1)], [('giai_2_1', 2), ('giai_3_5', 0), ('giai_4_1', 3)])

class Btl_HoangBach162LotoMethod(BasePredictionMethod, BaseMakeResult):
    def get_code(self): return "btl_hoangbach_162"
    def get_name(self): return "Bạch thủ lô Hoàng Bách 162"
    def get_description(self): return "Tổng từ giải 1.1.1 + 3.5.3 + 5.3.3 và giải 1.1.2 + 1.1.4 + 1.1.5"
    def calculate(self, data): return self._make_result(data, [('giai_1', 0), ('giai_3_5', 2), ('giai_5_3', 2)], [('giai_1', 1), ('giai_1', 3), ('giai_1', 4)])

class Btl_HoangBach163LotoMethod(BasePredictionMethod, BaseMakeResult):
    def get_code(self): return "btl_hoangbach_163"
    def get_name(self): return "Bạch thủ lô Hoàng Bách 163"
    def get_description(self): return "Tổng từ giải 3.1.1 + 3.1.5 + 4.3.4 và giải 2.1.4 + 4.2.1 + 5.2.1"
    def calculate(self, data): return self._make_result(data, [('giai_3_1', 0), ('giai_3_1', 4), ('giai_4_3', 3)], [('giai_2_1', 3), ('giai_4_2', 0), ('giai_5_2', 0)])

class Btl_HoangBach164LotoMethod(BasePredictionMethod, BaseMakeResult):
    def get_code(self): return "btl_hoangbach_164"
    def get_name(self): return "Bạch thủ lô Hoàng Bách 164"
    def get_description(self): return "Tổng từ giải 3.6.1 + 3.6.2 + 3.6.3 và giải 1.1.1 + 1.1.2 + 1.1.3"
    def calculate(self, data): return self._make_result(data, [('giai_3_6', 0), ('giai_3_6', 1), ('giai_3_6', 2)], [('giai_1', 0), ('giai_1', 1), ('giai_1', 2)])

class Btl_HoangBach165LotoMethod(BasePredictionMethod, BaseMakeResult):
    def get_code(self): return "btl_hoangbach_165"
    def get_name(self): return "Bạch thủ lô Hoàng Bách 165"
    def get_description(self): return "Tổng từ giải 1.1.3 + 3.4.5 + 6.2.3 và giải 2.1.1 + 3.2.4 + 4.1.3"
    def calculate(self, data): return self._make_result(data, [('giai_1', 2), ('giai_3_4', 4), ('giai_6_2', 2)], [('giai_2_1', 0), ('giai_3_2', 3), ('giai_4_1', 2)])

class Btl_HoangBach166LotoMethod(BasePredictionMethod, BaseMakeResult):
    def get_code(self): return "btl_hoangbach_166"
    def get_name(self): return "Bạch thủ lô Hoàng Bách 166"
    def get_description(self): return "Tổng từ giải 1.1.3 + 3.4.5 + 6.2.3 và giải 3.3.2 + 5.6.2 + 7.4.1"
    def calculate(self, data): return self._make_result(data, [('giai_1', 2), ('giai_3_4', 4), ('giai_6_2', 2)], [('giai_3_3', 1), ('giai_5_6', 1), ('giai_7_4', 0)])

class Btl_HoangBach167LotoMethod(BasePredictionMethod, BaseMakeResult):
    def get_code(self): return "btl_hoangbach_167"
    def get_name(self): return "Bạch thủ lô Hoàng Bách 167"
    def get_description(self): return "Tổng từ giải 3.2.2 + 3.6.4 + 5.3.3 và giải 3.2.5 + 5.2.3 + 6.2.3"
    def calculate(self, data): return self._make_result(data, [('giai_3_2', 1), ('giai_3_6', 3), ('giai_5_3', 2)], [('giai_3_2', 4), ('giai_5_2', 2), ('giai_6_2', 2)])

class Btl_HoangBach168LotoMethod(BasePredictionMethod, BaseMakeResult):
    def get_code(self): return "btl_hoangbach_168"
    def get_name(self): return "Bạch thủ lô Hoàng Bách 168"
    def get_description(self): return "Tổng từ giải 2.1.5 + 3.6.2 + 5.4.3 và giải 3.1.4 + 4.4.3 + 6.2.3"
    def calculate(self, data): return self._make_result(data, [('giai_2_1', 4), ('giai_3_6', 1), ('giai_5_4', 2)], [('giai_3_1', 3), ('giai_4_4', 2), ('giai_6_2', 2)])

class Btl_HoangBach169LotoMethod(BasePredictionMethod, BaseMakeResult):
    def get_code(self): return "btl_hoangbach_169"
    def get_name(self): return "Bạch thủ lô Hoàng Bách 169"
    def get_description(self): return "Tổng từ giải 2.1.5 + 3.6.2 + 5.4.3 và giải 3.1.4 + 4.4.3 + 6.2.3"
    def calculate(self, data): return self._make_result(data, [('giai_2_1', 4), ('giai_3_6', 1), ('giai_5_4', 2)], [('giai_3_1', 3), ('giai_4_4', 2), ('giai_6_2', 2)])

class Btl_HoangBach170LotoMethod(BasePredictionMethod, BaseMakeResult):
    def get_code(self): return "btl_hoangbach_170"
    def get_name(self): return "Bạch thủ lô Hoàng Bách 170"
    def get_description(self): return "Tổng từ giải giai_db.3 + 2.1.5 + 3.5.4 và giải 3.4.5 + 5.1.4 + 5.2.1"
    def calculate(self, data): return self._make_result(data, [('giai_db', 2), ('giai_2_1', 4), ('giai_3_5', 3)], [('giai_3_4', 4), ('giai_5_1', 3), ('giai_5_2', 0)])

class Btl_HoangBach171LotoMethod(BasePredictionMethod, BaseMakeResult):
    def get_code(self): return "btl_hoangbach_171"
    def get_name(self): return "Bạch thủ lô Hoàng Bách 171"
    def get_description(self): return "Tổng từ giải 2.1.5 + 3.6.2 + 5.4.3 và giải giai_db.2 + 2.1.3 + 6.1.2"
    def calculate(self, data): return self._make_result(data, [('giai_2_1', 4), ('giai_3_6', 1), ('giai_5_4', 2)], [('giai_db', 1), ('giai_2_1', 2), ('giai_6_1', 1)])

class Btl_HoangBach172LotoMethod(BasePredictionMethod, BaseMakeResult):
    def get_code(self): return "btl_hoangbach_172"
    def get_name(self): return "Bạch thủ lô Hoàng Bách 172"
    def get_description(self): return "Tổng từ giải 5.2.2 + 5.2.3 + 5.2.4 và giải 6.2.1 + 6.2.2 + 6.2.3"
    def calculate(self, data): return self._make_result(data, [('giai_5_2', 1), ('giai_5_2', 2), ('giai_5_2', 3)], [('giai_6_2', 0), ('giai_6_2', 1), ('giai_6_2', 2)])

class Btl_HoangBach173LotoMethod(BasePredictionMethod, BaseMakeResult):
    def get_code(self): return "btl_hoangbach_173"
    def get_name(self): return "Bạch thủ lô Hoàng Bách 173"
    def get_description(self): return "Tổng từ giải 5.1.1 + 5.4.2 + 7.1.2 và giải 5.1.1 + 5.2.3 + 5.4.3"
    def calculate(self, data): return self._make_result(data, [('giai_5_1', 0), ('giai_5_4', 1), ('giai_7_1', 1)], [('giai_5_1', 0), ('giai_5_2', 2), ('giai_5_4', 2)])

class Btl_HoangBach174LotoMethod(BasePredictionMethod, BaseMakeResult):
    def get_code(self): return "btl_hoangbach_174"
    def get_name(self): return "Bạch thủ lô Hoàng Bách 174"
    def get_description(self): return "Tổng từ giải 2.2.4 + 4.1.4 + 5.1.4 và giải 1.1.2 + 5.1.3 + 5.5.3"
    def calculate(self, data): return self._make_result(data, [('giai_2_2', 3), ('giai_4_1', 3), ('giai_5_1', 3)], [('giai_1', 1), ('giai_5_1', 2), ('giai_5_5', 2)])

class Btl_HoangBach175LotoMethod(BasePredictionMethod, BaseMakeResult):
    def get_code(self): return "btl_hoangbach_175"
    def get_name(self): return "Bạch thủ lô Hoàng Bách 175"
    def get_description(self): return "Tổng từ giải 3.4.1 + 4.2.4 + 4.4.2 và giải giai_db.2 + 2.2.2 + 5.2.2"
    def calculate(self, data): return self._make_result(data, [('giai_3_4', 0), ('giai_4_2', 3), ('giai_4_4', 1)], [('giai_db', 1), ('giai_2_2', 1), ('giai_5_2', 1)])

class Btl_HoangBach176LotoMethod(BasePredictionMethod, BaseMakeResult):
    def get_code(self): return "btl_hoangbach_176"
    def get_name(self): return "Bạch thủ lô Hoàng Bách 176"
    def get_description(self): return "Tổng từ giải 1.1.3 + 3.1.4 + 3.3.2 và giải 3.2.3 + 3.5.3 + 5.1.2"
    def calculate(self, data): return self._make_result(data, [('giai_1', 2), ('giai_3_1', 3), ('giai_3_3', 1)], [('giai_3_2', 2), ('giai_3_5', 2), ('giai_5_1', 1)])

class Btl_HoangBach177LotoMethod(BasePredictionMethod, BaseMakeResult):
    def get_code(self): return "btl_hoangbach_177"
    def get_name(self): return "Bạch thủ lô Hoàng Bách 177"
    def get_description(self): return "Tổng từ giải 1.1.3 + 3.1.3 + 3.4.3 và giải 3.2.3 + 3.5.3 + 5.1.1"
    def calculate(self, data): return self._make_result(data, [('giai_1', 2), ('giai_3_1', 2), ('giai_3_4', 2)], [('giai_3_2', 2), ('giai_3_5', 2), ('giai_5_1', 0)])

class Btl_HoangBach178LotoMethod(BasePredictionMethod, BaseMakeResult):
    def get_code(self): return "btl_hoangbach_178"
    def get_name(self): return "Bạch thủ lô Hoàng Bách 178"
    def get_description(self): return "Tổng từ giải 1.1.5 + 3.1.3 + 3.6.1 và giải 1.1.2 + 3.6.1 + 6.1.3"
    def calculate(self, data): return self._make_result(data, [('giai_1', 4), ('giai_3_1', 2), ('giai_3_6', 0)], [('giai_1', 1), ('giai_3_6', 0), ('giai_6_1', 2)])

class Btl_HoangBach179LotoMethod(BasePredictionMethod, BaseMakeResult):
    def get_code(self): return "btl_hoangbach_179"
    def get_name(self): return "Bạch thủ lô Hoàng Bách 179"
    def get_description(self): return "Tổng từ giải giai_db.1 + 3.4.3 + 5.3.2 và giải 4.1.4 + 5.1.1 + 6.3.3"
    def calculate(self, data): return self._make_result(data, [('giai_db', 0), ('giai_3_4', 2), ('giai_5_3', 1)], [('giai_4_1', 3), ('giai_5_1', 0), ('giai_6_3', 2)])

class Btl_HoangBach180LotoMethod(BasePredictionMethod, BaseMakeResult):
    def get_code(self): return "btl_hoangbach_180"
    def get_name(self): return "Bạch thủ lô Hoàng Bách 180"
    def get_description(self): return "Tổng từ giải 3.1.4 + 3.3.3 + 3.5.1 và giải 3.4.1 + 7.1.1 + 7.3.1"
    def calculate(self, data): return self._make_result(data, [('giai_3_1', 3), ('giai_3_3', 2), ('giai_3_5', 0)], [('giai_3_4', 0), ('giai_7_1', 0), ('giai_7_3', 0)])

class Btl_HoangBach181LotoMethod(BasePredictionMethod, BaseMakeResult):
    def get_code(self): return "btl_hoangbach_181"
    def get_name(self): return "Bạch thủ lô Hoàng Bách 181"
    def get_description(self): return "Tổng từ giải 3.6.3 + 3.6.4 + 3.6.5 và giải 6.2.1 + 6.2.2 + 6.2.3"
    def calculate(self, data): return self._make_result(data, [('giai_3_6', 2), ('giai_3_6', 3), ('giai_3_6', 4)], [('giai_6_2', 0), ('giai_6_2', 1), ('giai_6_2', 2)])

class Btl_HoangBach182LotoMethod(BasePredictionMethod, BaseMakeResult):
    def get_code(self): return "btl_hoangbach_182"
    def get_name(self): return "Bạch thủ lô Hoàng Bách 182"
    def get_description(self): return "Tổng từ giải giai_db.4 + 2.1.5 + 3.2.3 và giải 1.1.1 + 5.4.2 + 7.3.2"
    def calculate(self, data): return self._make_result(data, [('giai_db', 3), ('giai_2_1', 4), ('giai_3_2', 2)], [('giai_1', 0), ('giai_5_4', 1), ('giai_7_3', 1)])

class Btl_HoangBach183LotoMethod(BasePredictionMethod, BaseMakeResult):
    def get_code(self): return "btl_hoangbach_183"
    def get_name(self): return "Bạch thủ lô Hoàng Bách 183"
    def get_description(self): return "Tổng từ giải 2.1.1 + giai_db.4 + 5.5.4 và giải giai_db.2 + 7.1.2 + 7.4.2"
    def calculate(self, data): return self._make_result(data, [('giai_2_1', 0), ('giai_db', 3), ('giai_5_5', 3)], [('giai_db', 1), ('giai_7_1', 1), ('giai_7_4', 1)])

class Btl_HoangBach184LotoMethod(BasePredictionMethod, BaseMakeResult):
    def get_code(self): return "btl_hoangbach_184"
    def get_name(self): return "Bạch thủ lô Hoàng Bách 184"
    def get_description(self): return "Tổng từ giải 2.1.1 + 3.3.2 + 5.3.1 và giải 3.4.2 + 3.6.5 + 4.2.2"
    def calculate(self, data): return self._make_result(data, [('giai_2_1', 0), ('giai_3_3', 1), ('giai_5_3', 0)], [('giai_3_4', 1), ('giai_3_6', 4), ('giai_4_2', 1)])

class Btl_HoangBach185LotoMethod(BasePredictionMethod, BaseMakeResult):
    def get_code(self): return "btl_hoangbach_185"
    def get_name(self): return "Bạch thủ lô Hoàng Bách 185"
    def get_description(self): return "Tổng từ giải 3.5.2 + 3.6.4 + 5.3.3 và giải 3.5.3 + 4.3.3 + 5.1.2"
    def calculate(self, data): return self._make_result(data, [('giai_3_5', 1), ('giai_3_6', 3), ('giai_5_3', 2)], [('giai_3_5', 2), ('giai_4_3', 2), ('giai_5_1', 1)])

class Btl_HoangBach186LotoMethod(BasePredictionMethod, BaseMakeResult):
    def get_code(self): return "btl_hoangbach_186"
    def get_name(self): return "Bạch thủ lô Hoàng Bách 186"
    def get_description(self): return "Tổng từ giải 4.3.3 + 5.5.1 + 5.6.2 và giải 1.1.5 + 2.2.1 + 5.4.4"
    def calculate(self, data): return self._make_result(data, [('giai_4_3', 2), ('giai_5_5', 0), ('giai_5_6', 1)], [('giai_1', 4), ('giai_2_2', 0), ('giai_5_4', 3)])

class Btl_HoangBach187LotoMethod(BasePredictionMethod, BaseMakeResult):
    def get_code(self): return "btl_hoangbach_187"
    def get_name(self): return "Bạch thủ lô Hoàng Bách 187"
    def get_description(self): return "Tổng từ giải 5.2.1 + 6.1.1 + 6.2.3 và giải 2.1.3 + 6.1.1 + 7.3.1"
    def calculate(self, data): return self._make_result(data, [('giai_5_2', 0), ('giai_6_1', 0), ('giai_6_2', 2)], [('giai_2_1', 2), ('giai_6_1', 0), ('giai_7_3', 0)])

class Btl_HoangBach188LotoMethod(BasePredictionMethod, BaseMakeResult):
    def get_code(self): return "btl_hoangbach_188"
    def get_name(self): return "Bạch thủ lô Hoàng Bách 188"
    def get_description(self): return "Tổng từ giải 2.1.5 + 6.3.2 + 6.3.3 và giải 1.1.1 + 2.2.1 + 6.2.2"
    def calculate(self, data): return self._make_result(data, [('giai_2_1', 4), ('giai_6_3', 1), ('giai_6_3', 2)], [('giai_1', 0), ('giai_2_2', 0), ('giai_6_2', 1)])

class Btl_HoangBach189LotoMethod(BasePredictionMethod, BaseMakeResult):
    def get_code(self): return "btl_hoangbach_189"
    def get_name(self): return "Bạch thủ lô Hoàng Bách 189"
    def get_description(self): return "Tổng từ giải giai_db.5 + 2.2.2 + 2.2.5 và giải giai_db.5 + 1.1.1 + 3.3.3"
    def calculate(self, data): return self._make_result(data, [('giai_db', 4), ('giai_2_2', 1), ('giai_2_2', 4)], [('giai_db', 4), ('giai_1', 0), ('giai_3_3', 2)])

class Btl_HoangBach190LotoMethod(BasePredictionMethod, BaseMakeResult):
    def get_code(self): return "btl_hoangbach_190"
    def get_name(self): return "Bạch thủ lô Hoàng Bách 190"
    def get_description(self): return "Tổng từ giải giai_db.5 + 2.1.1 + 4.2.4 và giải 2.2.1 + 3.3.4 + 4.3.4"
    def calculate(self, data): return self._make_result(data, [('giai_db', 4), ('giai_2_1', 0), ('giai_4_2', 3)], [('giai_2_2', 0), ('giai_3_3', 3), ('giai_4_3', 3)])

class Btl_HoangBach191LotoMethod(BasePredictionMethod, BaseMakeResult):
    def get_code(self): return "btl_hoangbach_191"
    def get_name(self): return "Bạch thủ lô Hoàng Bách 191"
    def get_description(self): return "Tổng từ giải 2.1.4 + 4.3.4 + 5.1.4 và giải 1.1.5 + 3.3.5 + 6.3.3"
    def calculate(self, data): return self._make_result(data, [('giai_2_1', 3), ('giai_4_3', 3), ('giai_5_1', 3)], [('giai_1', 4), ('giai_3_3', 4), ('giai_6_3', 2)])

class Btl_HoangBach192LotoMethod(BasePredictionMethod, BaseMakeResult):
    def get_code(self): return "btl_hoangbach_192"
    def get_name(self): return "Bạch thủ lô Hoàng Bách 192"
    def get_description(self): return "Tổng từ giải 3.1.1 + 3.2.1 + 4.3.1 và giải 1.1.4 + 2.2.5 + 4.4.4"
    def calculate(self, data): return self._make_result(data, [('giai_3_1', 0), ('giai_3_2', 0), ('giai_4_3', 0)], [('giai_1', 3), ('giai_2_2', 4), ('giai_4_4', 3)])

class Btl_HoangBach193LotoMethod(BasePredictionMethod, BaseMakeResult):
    def get_code(self): return "btl_hoangbach_193"
    def get_name(self): return "Bạch thủ lô Hoàng Bách 193"
    def get_description(self): return "Tổng từ giải 3.5.2 + 6.1.2 + 7.2.1 và giải 3.2.1 + 5.1.4 + 6.3.2"
    def calculate(self, data): return self._make_result(data, [('giai_3_5', 1), ('giai_6_1', 1), ('giai_7_2', 0)], [('giai_3_2', 0), ('giai_5_1', 3), ('giai_6_3', 1)])

class Btl_HoangBach194LotoMethod(BasePredictionMethod, BaseMakeResult):
    def get_code(self): return "btl_hoangbach_194"
    def get_name(self): return "Bạch thủ lô Hoàng Bách 194"
    def get_description(self): return "Tổng từ giải 2.1.1 + 3.3.2 + 5.3.1 và giải 3.1.2 + 5.2.1 + 5.6.1"
    def calculate(self, data): return self._make_result(data, [('giai_2_1', 0), ('giai_3_3', 1), ('giai_5_3', 0)], [('giai_3_1', 1), ('giai_5_2', 0), ('giai_5_6', 0)])

class Btl_HoangBach195LotoMethod(BasePredictionMethod, BaseMakeResult):
    def get_code(self): return "btl_hoangbach_195"
    def get_name(self): return "Bạch thủ lô Hoàng Bách 195"
    def get_description(self): return "Tổng từ giải giai_db.3 + 1.1.3 + 2.2.4 và giải 2.1.2 + 3.1.4 + 5.2.2"
    def calculate(self, data): return self._make_result(data, [('giai_db', 2), ('giai_1', 2), ('giai_2_2', 3)], [('giai_2_1', 1), ('giai_3_1', 3), ('giai_5_2', 1)])

class Btl_HoangBach196LotoMethod(BasePredictionMethod, BaseMakeResult):
    def get_code(self): return "btl_hoangbach_196"
    def get_name(self): return "Bạch thủ lô Hoàng Bách 196"
    def get_description(self): return "Tổng từ giải 4.3.1 + 5.4.2 + 7.3.2 và giải 2.2.1 + 3.1.1 + 3.5.2"
    def calculate(self, data): return self._make_result(data, [('giai_4_3', 0), ('giai_5_4', 1), ('giai_7_3', 1)], [('giai_2_2', 0), ('giai_3_1', 0), ('giai_3_5', 1)])

class Btl_HoangBach197LotoMethod(BasePredictionMethod, BaseMakeResult):
    def get_code(self): return "btl_hoangbach_197"
    def get_name(self): return "Bạch thủ lô Hoàng Bách 197"
    def get_description(self): return "Tổng từ giải 5.1.2 + 5.1.3 + 5.1.4 và giải 4.1.2 + 4.1.3 + 4.1.4"
    def calculate(self, data): return self._make_result(data, [('giai_5_1', 1), ('giai_5_1', 2), ('giai_5_1', 3)], [('giai_4_1', 1), ('giai_4_1', 2), ('giai_4_1', 3)])

class Btl_HoangBach198LotoMethod(BasePredictionMethod, BaseMakeResult):
    def get_code(self): return "btl_hoangbach_198"
    def get_name(self): return "Bạch thủ lô Hoàng Bách 198"
    def get_description(self): return "Tổng từ giải 2.2.4 + 4.2.1 + 4.3.1 và giải 3.2.1 + 3.3.1 + 3.6.2"
    def calculate(self, data): return self._make_result(data, [('giai_2_2', 3), ('giai_4_2', 0), ('giai_4_3', 0)], [('giai_3_2', 0), ('giai_3_3', 0), ('giai_3_6', 1)])

class Btl_HoangBach199LotoMethod(BasePredictionMethod, BaseMakeResult):
    def get_code(self): return "btl_hoangbach_199"
    def get_name(self): return "Bạch thủ lô Hoàng Bách 199"
    def get_description(self): return "Tổng từ giải giai_db.3 + 2.1.5 + 2.2.3 và giải 4.4.3 + 5.4.2 + 7.2.2"
    def calculate(self, data): return self._make_result(data, [('giai_db', 2), ('giai_2_1', 4), ('giai_2_2', 2)], [('giai_4_4', 2), ('giai_5_4', 1), ('giai_7_2', 1)])

class Btl_HoangBach200LotoMethod(BasePredictionMethod, BaseMakeResult):
    def get_code(self): return "btl_hoangbach_200"
    def get_name(self): return "Bạch thủ lô Hoàng Bách 200"
    def get_description(self): return "Tổng từ giải 4.2.1 + 4.2.2 + 4.2.3 và giải 4.4.3 + 5.4.2 + 7.2.2"
    def calculate(self, data): return self._make_result(data, [('giai_4_2', 0), ('giai_4_2', 1), ('giai_4_2', 2)], [('giai_4_4', 2), ('giai_5_4', 1), ('giai_7_2', 1)])

class Btl_HoangBach201LotoMethod(BasePredictionMethod, BaseMakeResult):
    def get_code(self): return "btl_hoangbach_201"
    def get_name(self): return "Bạch thủ lô Hoàng Bách 201"
    def get_description(self): return "Tổng từ giải 3.1.3 + 3.2.1 + 3.4.3 và giải 5.1.3 + 5.2.3 + 5.4.3"
    def calculate(self, data): return self._make_result(data, [('giai_3_1', 2), ('giai_3_2', 0), ('giai_3_4', 2)], [('giai_5_1', 2), ('giai_5_2', 2), ('giai_5_4', 2)])

class Btl_HoangBach202LotoMethod(BasePredictionMethod, BaseMakeResult):
    def get_code(self): return "btl_hoangbach_202"
    def get_name(self): return "Bạch thủ lô Hoàng Bách 202"
    def get_description(self): return "Tổng từ giải 3.5.4 + 3.5.5 + 3.6.1 và giải 5.6.2 + 5.6.3 + 6.3.2"
    def calculate(self, data): return self._make_result(data, [('giai_3_5', 3), ('giai_3_5', 4), ('giai_3_6', 0)], [('giai_5_6', 1), ('giai_5_6', 2), ('giai_6_3', 1)])

class Btl_HoangBach203LotoMethod(BasePredictionMethod, BaseMakeResult):
    def get_code(self): return "btl_hoangbach_203"
    def get_name(self): return "Bạch thủ lô Hoàng Bách 203"
    def get_description(self): return "Tổng từ giải giai_db.5 + 3.2.2 + 4.2.2 và giải 3.1.3 + 3.4.2 + 5.2.3"
    def calculate(self, data): return self._make_result(data, [('giai_db', 4), ('giai_3_2', 1), ('giai_4_2', 1)], [('giai_3_1', 2), ('giai_3_4', 1), ('giai_5_2', 2)])

class Btl_HoangBach204LotoMethod(BasePredictionMethod, BaseMakeResult):
    def get_code(self): return "btl_hoangbach_204"
    def get_name(self): return "Bạch thủ lô Hoàng Bách 204"
    def get_description(self): return "Tổng từ giải 2.2.1 + 3.1.5 + 4.4.1 và giải 3.1.2 + 4.4.2 + 5.3.2"
    def calculate(self, data): return self._make_result(data, [('giai_2_2', 0), ('giai_3_1', 4), ('giai_4_4', 0)], [('giai_3_1', 1), ('giai_4_4', 1), ('giai_5_3', 1)])

class Btl_HoangBach205LotoMethod(BasePredictionMethod, BaseMakeResult):
    def get_code(self): return "btl_hoangbach_205"
    def get_name(self): return "Bạch thủ lô Hoàng Bách 205"
    def get_description(self): return "Tổng từ giải 2.2.3 + 3.6.1 + 7.1.1 và giải 1.1.5 + 2.2.2 + 4.4.2"
    def calculate(self, data): return self._make_result(data, [('giai_2_2', 2), ('giai_3_6', 0), ('giai_7_1', 0)], [('giai_1', 4), ('giai_2_2', 1), ('giai_4_4', 1)])

class Btl_HoangBach206LotoMethod(BasePredictionMethod, BaseMakeResult):
    def get_code(self): return "btl_hoangbach_206"
    def get_name(self): return "Bạch thủ lô Hoàng Bách 206"
    def get_description(self): return "Tổng từ giải 1.1.4 + 4.2.1 + 5.5.3 và giải 1.1.4 + 3.3.2 + 3.6.4"
    def calculate(self, data): return self._make_result(data, [('giai_1', 3), ('giai_4_2', 0), ('giai_5_5', 2)], [('giai_1', 3), ('giai_3_3', 1), ('giai_3_6', 3)])

class Btl_HoangBach207LotoMethod(BasePredictionMethod, BaseMakeResult):
    def get_code(self): return "btl_hoangbach_207"
    def get_name(self): return "Bạch thủ lô Hoàng Bách 207"
    def get_description(self): return "Tổng từ giải 4.4.4 + 5.3.1 + 5.3.3 và giải 1.1.4 + 2.2.4 + 3.1.5"
    def calculate(self, data): return self._make_result(data, [('giai_4_4', 3), ('giai_5_3', 0), ('giai_5_3', 2)], [('giai_1', 3), ('giai_2_2', 3), ('giai_3_1', 4)])

class Btl_HoangBach208LotoMethod(BasePredictionMethod, BaseMakeResult):
    def get_code(self): return "btl_hoangbach_208"
    def get_name(self): return "Bạch thủ lô Hoàng Bách 208"
    def get_description(self): return "Tổng từ giải giai_db.2 + 3.1.3 + 5.1.2 và giải 1.1.4 + 3.3.1 + 5.6.1"
    def calculate(self, data): return self._make_result(data, [('giai_db', 1), ('giai_3_1', 2), ('giai_5_1', 1)], [('giai_1', 3), ('giai_3_3', 0), ('giai_5_6', 0)])

class Btl_HoangBach209LotoMethod(BasePredictionMethod, BaseMakeResult):
    def get_code(self): return "btl_hoangbach_209"
    def get_name(self): return "Bạch thủ lô Hoàng Bách 209"
    def get_description(self): return "Tổng từ giải 2.2.2 + 3.6.4 + 5.2.1 và giải 3.3.1 + 3.6.1 + 4.3.2"
    def calculate(self, data): return self._make_result(data, [('giai_2_2', 1), ('giai_3_6', 3), ('giai_5_2', 0)], [('giai_3_3', 0), ('giai_3_6', 0), ('giai_4_3', 1)])

class Btl_HoangBach210LotoMethod(BasePredictionMethod, BaseMakeResult):
    def get_code(self): return "btl_hoangbach_210"
    def get_name(self): return "Bạch thủ lô Hoàng Bách 210"
    def get_description(self): return "Tổng từ giải 1.1.1 + 3.1.2 + 5.1.4 và giải giai_db.5 + 2.2.5 + 5.6.4"
    def calculate(self, data): return self._make_result(data, [('giai_1', 0), ('giai_3_1', 1), ('giai_5_1', 3)], [('giai_db', 4), ('giai_2_2', 4), ('giai_5_6', 3)])

class Btl_HoangBach211LotoMethod(BasePredictionMethod, BaseMakeResult):
    def get_code(self): return "btl_hoangbach_211"
    def get_name(self): return "Bạch thủ lô Hoàng Bách 211"
    def get_description(self): return "Tổng từ giải 2.2.3 + 4.1.2 + 4.4.2 và giải giai_db.2 + 3.6.1 + 7.3.2"
    def calculate(self, data): return self._make_result(data, [('giai_2_2', 2), ('giai_4_1', 1), ('giai_4_4', 1)], [('giai_db', 1), ('giai_3_6', 0), ('giai_7_3', 1)])

class Btl_HoangBach212LotoMethod(BasePredictionMethod, BaseMakeResult):
    def get_code(self): return "btl_hoangbach_212"
    def get_name(self): return "Bạch thủ lô Hoàng Bách 212"
    def get_description(self): return "Tổng từ giải 2.1.1 + 2.1.4 + 5.4.2 và giải 3.2.4 + 3.4.2 + 5.5.2"
    def calculate(self, data): return self._make_result(data, [('giai_2_1', 0), ('giai_2_1', 3), ('giai_5_4', 1)], [('giai_3_2', 3), ('giai_3_4', 1), ('giai_5_5', 1)])

class Btl_HoangBach213LotoMethod(BasePredictionMethod, BaseMakeResult):
    def get_code(self): return "btl_hoangbach_213"
    def get_name(self): return "Bạch thủ lô Hoàng Bách 213"
    def get_description(self): return "Tổng từ giải giai_db.2 + 5.2.2 + 7.1.2 và giải 1.1.1 + 5.6.4 + 7.2.1"
    def calculate(self, data): return self._make_result(data, [('giai_db', 1), ('giai_5_2', 1), ('giai_7_1', 1)], [('giai_1', 0), ('giai_5_6', 3), ('giai_7_2', 0)])

class Btl_HoangBach214LotoMethod(BasePredictionMethod, BaseMakeResult):
    def get_code(self): return "btl_hoangbach_214"
    def get_name(self): return "Bạch thủ lô Hoàng Bách 214"
    def get_description(self): return "Tổng từ giải 1.1.1 + 3.1.5 + 5.2.4 và giải giai_db.3 + 1.1.5 + 3.6.5"
    def calculate(self, data): return self._make_result(data, [('giai_1', 0), ('giai_3_1', 4), ('giai_5_2', 3)], [('giai_db', 2), ('giai_1', 4), ('giai_3_6', 4)])

class Btl_HoangBach215LotoMethod(BasePredictionMethod, BaseMakeResult):
    def get_code(self): return "btl_hoangbach_215"
    def get_name(self): return "Bạch thủ lô Hoàng Bách 215"
    def get_description(self): return "Tổng từ giải 5.1.1 + 5.1.2 + 5.1.3 và giải 6.2.1 + 6.2.2 + 6.2.3"
    def calculate(self, data): return self._make_result(data, [('giai_5_1', 0), ('giai_5_1', 1), ('giai_5_1', 2)], [('giai_6_2', 0), ('giai_6_2', 1), ('giai_6_2', 2)])

class Btl_HoangBach216LotoMethod(BasePredictionMethod, BaseMakeResult):
    def get_code(self): return "btl_hoangbach_216"
    def get_name(self): return "Bạch thủ lô Hoàng Bách 216"
    def get_description(self): return "Tổng từ giải 1.1.4 + 3.4.2 + 5.5.4 và giải 2.2.1 + 4.3.4 + 6.3.2"
    def calculate(self, data): return self._make_result(data, [('giai_1', 3), ('giai_3_4', 1), ('giai_5_5', 3)], [('giai_2_2', 0), ('giai_4_3', 3), ('giai_6_3', 1)])

class Btl_HoangBach217LotoMethod(BasePredictionMethod, BaseMakeResult):
    def get_code(self): return "btl_hoangbach_217"
    def get_name(self): return "Bạch thủ lô Hoàng Bách 217"
    def get_description(self): return "Tổng từ giải 2.1.1 + 3.2.3 + 5.1.4 và giải giai_db.5 + 4.3.4 + 4.4.3"
    def calculate(self, data): return self._make_result(data, [('giai_2_1', 0), ('giai_3_2', 2), ('giai_5_1', 3)], [('giai_db', 4), ('giai_4_3', 3), ('giai_4_4', 2)])

class Btl_HoangBach218LotoMethod(BasePredictionMethod, BaseMakeResult):
    def get_code(self): return "btl_hoangbach_218"
    def get_name(self): return "Bạch thủ lô Hoàng Bách 218"
    def get_description(self): return "Tổng từ giải 1.1.4 + 2.1.4 + 7.3.1 và giải giai_db.3 + 3.6.3 + 4.1.4"
    def calculate(self, data): return self._make_result(data, [('giai_1', 3), ('giai_2_1', 3), ('giai_7_3', 0)], [('giai_db', 2), ('giai_3_6', 2), ('giai_4_1', 3)])

class Btl_HoangBach219LotoMethod(BasePredictionMethod, BaseMakeResult):
    def get_code(self): return "btl_hoangbach_219"
    def get_name(self): return "Bạch thủ lô Hoàng Bách 219"
    def get_description(self): return "Tổng từ giải 2.1.1 + 3.6.5 + 4.4.3 và giải 3.3.5 + 4.1.1 + 6.3.2"
    def calculate(self, data): return self._make_result(data, [('giai_2_1', 0), ('giai_3_6', 4), ('giai_4_4', 2)], [('giai_3_3', 4), ('giai_4_1', 0), ('giai_6_3', 1)])

class Btl_HoangBach220LotoMethod(BasePredictionMethod, BaseMakeResult):
    def get_code(self): return "btl_hoangbach_220"
    def get_name(self): return "Bạch thủ lô Hoàng Bách 220"
    def get_description(self): return "Tổng từ giải 3.3.3 + 5.6.3 + 6.2.3 và giải 3.2.3 + 3.4.5 + 3.5.3"
    def calculate(self, data): return self._make_result(data, [('giai_3_3', 2), ('giai_5_6', 2), ('giai_6_2', 2)], [('giai_3_2', 2), ('giai_3_4', 4), ('giai_3_5', 2)])

class Btl_HoangBach221LotoMethod(BasePredictionMethod, BaseMakeResult):
    def get_code(self): return "btl_hoangbach_221"
    def get_name(self): return "Bạch thủ lô Hoàng Bách 221"
    def get_description(self): return "Tổng từ giải 3.1.1 + 3.6.5 + 4.3.3 và giải 3.3.5 + 4.1.1 + 6.3.2"
    def calculate(self, data): return self._make_result(data, [('giai_3_1', 0), ('giai_3_6', 4), ('giai_4_3', 2)], [('giai_3_3', 4), ('giai_4_1', 0), ('giai_6_3', 1)])

class Btl_HoangBach222LotoMethod(BasePredictionMethod, BaseMakeResult):
    def get_code(self): return "btl_hoangbach_222"
    def get_name(self): return "Bạch thủ lô Hoàng Bách 222"
    def get_description(self): return "Tổng từ giải 2.2.3 + 3.1.4 + 3.4.4 và giải 4.2.2 + 5.1.3 + 5.4.3"
    def calculate(self, data): return self._make_result(data, [('giai_2_2', 2), ('giai_3_1', 3), ('giai_3_4', 3)], [('giai_4_2', 1), ('giai_5_1', 2), ('giai_5_4', 2)])

class Btl_HoangBach223LotoMethod(BasePredictionMethod, BaseMakeResult):
    def get_code(self): return "btl_hoangbach_223"
    def get_name(self): return "Bạch thủ lô Hoàng Bách 223"
    def get_description(self): return "Tổng từ giải 3.6.3 + 4.3.1 + 5.2.3 và giải 5.3.2 + 5.3.3 + 5.6.2"
    def calculate(self, data): return self._make_result(data, [('giai_3_6', 2), ('giai_4_3', 0), ('giai_5_2', 2)], [('giai_5_3', 1), ('giai_5_3', 2), ('giai_5_6', 1)])

class Btl_HoangBach224LotoMethod(BasePredictionMethod, BaseMakeResult):
    def get_code(self): return "btl_hoangbach_224"
    def get_name(self): return "Bạch thủ lô Hoàng Bách 224"
    def get_description(self): return "Tổng từ giải 2.2.3 + 4.4.3 + 5.5.1 và giải giai_db.1 + 5.4.2 + 7.4.1"
    def calculate(self, data): return self._make_result(data, [('giai_2_2', 2), ('giai_4_4', 2), ('giai_5_5', 0)], [('giai_db', 0), ('giai_5_4', 1), ('giai_7_4', 0)])

class Btl_HoangBach225LotoMethod(BasePredictionMethod, BaseMakeResult):
    def get_code(self): return "btl_hoangbach_225"
    def get_name(self): return "Bạch thủ lô Hoàng Bách 225"
    def get_description(self): return "Tổng từ giải 2.2.3 + 4.4.3 + 5.5.1 và giải 1.1.3 + 4.4.1 + 6.3.3"
    def calculate(self, data): return self._make_result(data, [('giai_2_2', 2), ('giai_4_4', 2), ('giai_5_5', 0)], [('giai_1', 2), ('giai_4_4', 0), ('giai_6_3', 2)])    