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