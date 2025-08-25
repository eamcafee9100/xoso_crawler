# from typing import Dict, List, Any
from typing import Any, Dict, List
import logging
logger = logging.getLogger(__name__)

# Import với try-catch để handle cả relative và absolute import
try:
    from .utils import get_ball_number
    from .base import BaseMakeResult, BasePredictionMethod
except ImportError:
    # Fallback cho khi chạy trực tiếp file này
    import sys
    import os
    sys.path.append(os.path.dirname(os.path.abspath(__file__)))
    from utils import get_ball_number
    from base import BaseMakeResult, BasePredictionMethod

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
    
class Btl_GL_01LotoMethod(BasePredictionMethod, BaseMakeResult):
    def get_code(self): return "btl_gl_01"
    def get_name(self): return "BTL GL_ 01"
    def get_description(self): return "Tổng từ giải 3.1.1 + 4.4.4 + 6.1.1 và giải giai_db.3"
    def calculate(self, data): return self._make_result(data, [('giai_3_1', 0), ('giai_4_4', 3), ('giai_6_1', 0)], [('giai_db', 2)],reverse=True)

class Btl_GL_02LotoMethod(BasePredictionMethod, BaseMakeResult):
    def get_code(self): return "btl_gl_02"
    def get_name(self): return "BTL GL_ 02"
    def get_description(self): return "Tổng từ giải 3.1.1 + 5.6.4 và giải 6.1.1 + 6.1.2"
    def calculate(self, data): return self._make_result(data, [('giai_3_1', 0), ('giai_5_6', 3)], [('giai_6_1', 0), ('giai_6_1', 1)],reverse=True)

class Btl_GL_03LotoMethod(BasePredictionMethod, BaseMakeResult):
    def get_code(self): return "btl_gl_03"
    def get_name(self): return "BTL GL_ 03"
    def get_description(self): return "Tổng từ giải giai_db.3 + 1.1.3 và giải 3.2.3 + 3.5.3"
    def calculate(self, data): return self._make_result(data, [('giai_db', 2), ('giai_1', 2)], [('giai_3_2', 2), ('giai_3_5', 2)],reverse=True)

class Btl_GL_04LotoMethod(BasePredictionMethod, BaseMakeResult):
    def get_code(self): return "btl_gl_04"
    def get_name(self): return "BTL GL_ 04"
    def get_description(self): return "Tổng từ giải 7.1.1 + 7.1.2 và giải 7.4.2"
    def calculate(self, data): return self._make_result(data, [('giai_7_1', 0), ('giai_7_1', 1)], [('giai_7_4', 1)],reverse=True)

class Btl_GL_05LotoMethod(BasePredictionMethod, BaseMakeResult):
    def get_code(self): return "btl_gl_05"
    def get_name(self): return "BTL GL_ 05"
    def get_description(self): return "Tổng từ giải 7.2.1 + 7.2.2 và giải 7.3.1 + 7.3.2"
    def calculate(self, data): return self._make_result(data, [('giai_7_2', 0), ('giai_7_2', 1)], [('giai_7_3', 0), ('giai_7_3', 1)],reverse=True)

class Btl_GL_06LotoMethod(BasePredictionMethod, BaseMakeResult):
    def get_code(self): return "btl_gl_06"
    def get_name(self): return "BTL GL_ 06"
    def get_description(self): return "Tổng từ giải 3.1.1 và giải 3.4.1"
    def calculate(self, data): return self._make_result(data, [('giai_3_1', 0)], [('giai_3_4', 0)],reverse=True)

class Btl_GL_07LotoMethod(BasePredictionMethod):
    def get_code(self): return "btl_gl_07"
    def get_name(self): return "BTL GL_ 07"
    def get_description(self): return "Tổng từ giải 1.1.1 và giải 1.1.5"
    def calculate(self, data): return self._make_result(data, [('giai_1', 0)], [('giai_1', 4)],reverse=True)
    def _make_result(
        self, data: Dict[str, Any], keys1: List[tuple], keys2: List[tuple], reverse: bool = False
    ) -> Dict[str, List[str]]:
        """
        Tính toán kết quả từ 2 nhóm keys
        
        Args:
            data: Dict chứa dữ liệu kết quả xổ số
            keys1: List[tuple] - Nhóm keys thứ nhất, format: (key, index)
            keys2: List[tuple] - Nhóm keys thứ hai, format: (key, index)
            
        Returns:
            Dict[str, List[str]]: {
                "two_digits_loto": List[str] - Danh sách số 2 chữ số
            }
        """
        try:
            # ✅ SỬA: Tính digit1 từ keys1 - LUÔN TÍNH TỔNG
            digit1_sum = 0
            for key, idx in keys1:
                val = data.get(key, "")
                if idx >= len(val):
                    logger.warning(
                        f"[BaseMakeResult] Dữ liệu không đủ cho {key} tại index {idx}"
                    )
                    return {"two_digits_loto": []}
                  
                digit1_sum += int(val[idx])
            digit1 = digit1_sum % 10
            digit1 = get_ball_number(digit1)
            # ✅ SỬA: Tính digit2 từ keys2 - LUÔN TÍNH TỔNG  
            digit2_sum = 0
            for key, idx in keys2:
                val = data.get(key, "")
                if idx >= len(val):
                    logger.warning(
                        f"[BaseMakeResult] Dữ liệu không đủ cho {key} tại index {idx}"
                    )
                    return {"two_digits_loto": []}
                digit2_sum += int(val[idx])
            digit2 = digit2_sum % 10
            digit2 = get_ball_number(digit2)  # Chuyển số thành bóng
            # Tạo số 2 chữ số
            results = [f"{digit1}{digit2}".zfill(2)]  # Đảm bảo 2 chữ số
            if reverse:
                results.append(f"{digit2}{digit1}".zfill(2))
            logger.info(f"[BaseMakeResult] Keys1 sum: {digit1_sum} -> digit1: {digit1}")
            logger.info(f"[BaseMakeResult] Keys2 sum: {digit2_sum} -> digit2: {digit2}")
            logger.info(f"[BaseMakeResult] Kết quả: {results}")
            
            return {"two_digits_loto": results}

        except (ValueError, IndexError, TypeError) as e:
            logger.error(f"[BaseMakeResult] Lỗi khi tính toán: {str(e)}")
            return {"two_digits_loto": []}
        except Exception as e:
            logger.error(f"[BaseMakeResult] Lỗi không xác định: {str(e)}")
            return {"two_digits_loto": []}
        
class Btl_GL_08LotoMethod(BasePredictionMethod, BaseMakeResult):
    def get_code(self): return "btl_gl_08"
    def get_name(self): return "BTL GL_ 08"
    def get_description(self): return "Tổng từ giải 3.3.5 và giải giai_db.5"
    def calculate(self, data): return self._make_result(data, [('giai_3_3', 4)], [('giai_db', 4)],reverse=True)

class Btl_GL_09LotoMethod(BasePredictionMethod, BaseMakeResult):
    def get_code(self): return "btl_gl_09"
    def get_name(self): return "BTL GL_ 09"
    def get_description(self): return "Tổng từ giải 6.3.1 và giải 6.3.2"
    def calculate(self, data): return self._make_result(data, [('giai_6_3', 0)], [('giai_6_3', 1)],reverse=True)
    def _make_result(
        self, data: Dict[str, Any], keys1: List[tuple], keys2: List[tuple], reverse: bool = False
    ) -> Dict[str, List[str]]:
        """
        Tính toán kết quả từ 2 nhóm keys
        
        Args:
            data: Dict chứa dữ liệu kết quả xổ số
            keys1: List[tuple] - Nhóm keys thứ nhất, format: (key, index)
            keys2: List[tuple] - Nhóm keys thứ hai, format: (key, index)
            
        Returns:
            Dict[str, List[str]]: {
                "two_digits_loto": List[str] - Danh sách số 2 chữ số
            }
        """
        try:
            # ✅ SỬA: Tính digit1 từ keys1 - LUÔN TÍNH TỔNG
            digit1_sum = 0
            for key, idx in keys1:
                val = data.get(key, "")
                if idx >= len(val):
                    logger.warning(
                        f"[BaseMakeResult] Dữ liệu không đủ cho {key} tại index {idx}"
                    )
                    return {"two_digits_loto": []}
                  
                digit1_sum += int(val[idx])
            digit1 = digit1_sum % 10
            # ✅ SỬA: Tính digit2 từ keys2 - LUÔN TÍNH TỔNG  
            digit2_sum = 0
            for key, idx in keys2:
                val = data.get(key, "")
                if idx >= len(val):
                    logger.warning(
                        f"[BaseMakeResult] Dữ liệu không đủ cho {key} tại index {idx}"
                    )
                    return {"two_digits_loto": []}
                digit2_sum += int(val[idx])
            digit2 = digit2_sum % 10
            digit2 = get_ball_number(digit2)  # Chuyển số thành bóng
            # Tạo số 2 chữ số
            results = [f"{digit1}{digit2}".zfill(2)]  # Đảm bảo 2 chữ số
            if reverse:
                results.append(f"{digit2}{digit1}".zfill(2))
           
            return {"two_digits_loto": results}

        except (ValueError, IndexError, TypeError) as e:
            logger.error(f"[BaseMakeResult] Lỗi khi tính toán: {str(e)}")
            return {"two_digits_loto": []}
        except Exception as e:
            logger.error(f"[BaseMakeResult] Lỗi không xác định: {str(e)}")
            return {"two_digits_loto": []}
        
class Btl_GL_10LotoMethod(BasePredictionMethod, BaseMakeResult):
    def get_code(self): return "btl_gl_10"
    def get_name(self): return "BTL GL_ 10"
    def get_description(self): return "Tổng từ giải 4.2.3 và giải 4.2.4"
    def calculate(self, data): return self._make_result(data, [('giai_4_2', 2)], [('giai_4_2', 3)],reverse=True)
    def _make_result(
        self, data: Dict[str, Any], keys1: List[tuple], keys2: List[tuple], reverse: bool = False
    ) -> Dict[str, List[str]]:
        """
        Tính toán kết quả từ 2 nhóm keys
        
        Args:
            data: Dict chứa dữ liệu kết quả xổ số
            keys1: List[tuple] - Nhóm keys thứ nhất, format: (key, index)
            keys2: List[tuple] - Nhóm keys thứ hai, format: (key, index)
            
        Returns:
            Dict[str, List[str]]: {
                "two_digits_loto": List[str] - Danh sách số 2 chữ số
            }
        """
        try:
            # ✅ SỬA: Tính digit1 từ keys1 - LUÔN TÍNH TỔNG
            digit1_sum = 0
            for key, idx in keys1:
                val = data.get(key, "")
                if idx >= len(val):
                    logger.warning(
                        f"[BaseMakeResult] Dữ liệu không đủ cho {key} tại index {idx}"
                    )
                    return {"two_digits_loto": []}
                  
                digit1_sum += int(val[idx])
            digit1 = digit1_sum % 10
            digit1 = get_ball_number(digit1)
            # ✅ SỬA: Tính digit2 từ keys2 - LUÔN TÍNH TỔNG  
            digit2_sum = 0
            for key, idx in keys2:
                val = data.get(key, "")
                if idx >= len(val):
                    logger.warning(
                        f"[BaseMakeResult] Dữ liệu không đủ cho {key} tại index {idx}"
                    )
                    return {"two_digits_loto": []}
                digit2_sum += int(val[idx])
            digit2 = digit2_sum % 10
            # Tạo số 2 chữ số
            results = [f"{digit1}{digit2}".zfill(2)]  # Đảm bảo 2 chữ số
            if reverse:
                results.append(f"{digit2}{digit1}".zfill(2))
            
            
            return {"two_digits_loto": results}

        except (ValueError, IndexError, TypeError) as e:
            logger.error(f"[BaseMakeResult] Lỗi khi tính toán: {str(e)}")
            return {"two_digits_loto": []}
        except Exception as e:
            logger.error(f"[BaseMakeResult] Lỗi không xác định: {str(e)}")
            return {"two_digits_loto": []}
        
class Btl_GL_11LotoMethod(BasePredictionMethod, BaseMakeResult):
    def get_code(self): return "btl_gl_11"
    def get_name(self): return "BTL GL_ 11"
    def get_description(self): return "Tổng từ giải 4.1.4 và giải 4.2.3"
    def calculate(self, data): return self._make_result(data, [('giai_4_1', 3)], [('giai_4_2', 2)],reverse=True)

class Btl_GL_12LotoMethod(BasePredictionMethod, BaseMakeResult):
    def get_code(self): return "btl_gl_12"
    def get_name(self): return "BTL GL_ 12"
    def get_description(self): return "Tổng từ giải 5.3.3 và giải 5.2.3"
    def calculate(self, data): return self._make_result(data, [('giai_5_3', 2)], [('giai_5_2', 2)],reverse=True)
class Btl_GL_13LotoMethod(BasePredictionMethod, BaseMakeResult):
    def get_code(self): return "btl_gl_13"
    def get_name(self): return "BTL GL_ 13"
    def get_description(self): return "Tổng từ giải 4.4.2 và giải 7.3.2"
    def calculate(self, data): return self._make_result(data, [('giai_4_4', 1)], [('giai_7_3', 1)],reverse=True)
class Btl_GL_14LotoMethod(BasePredictionMethod, BaseMakeResult):
    def get_code(self): return "btl_gl_14"
    def get_name(self): return "BTL GL_ 14"
    def get_description(self): return "Tổng từ giải 3.2.3 và giải 7.1.2"
    def calculate(self, data): return self._make_result(data, [('giai_4_4', 2)], [('giai_7_3', 1)],reverse=True)

class Btl_GL_15LotoMethod(BasePredictionMethod, BaseMakeResult):
    def get_code(self): return "btl_gl_15"
    def get_name(self): return "BTL GL_ 15"
    def get_description(self): return "Tổng từ giải 3.3.2 và giải 7.1.1"
    def calculate(self, data): return self._make_result(data, [('giai_3_3', 1)], [('giai_7_1', 0)],reverse=True)

class Btl_GL_16LotoMethod(BasePredictionMethod, BaseMakeResult):
    def get_code(self): return "btl_gl_16"
    def get_name(self): return "BTL GL_ 16 2 nháy"
    def get_description(self): return "Tổng từ giải 4.1.1 và giải 6.1.2"
    def calculate(self, data): return self._make_result(data, [('giai_4_1', 0)], [('giai_6_1', 1)],reverse=True)
class Btl_GL_17LotoMethod(BasePredictionMethod, BaseMakeResult):
    def get_code(self): return "btl_gl_17"
    def get_name(self): return "BTL GL_ 17 2 nháy"
    def get_description(self): return "Tổng từ giải 3.1.1 và giải 4.1.1"
    def calculate(self, data): return self._make_result(data, [('giai_3_1', 0)], [('giai_4_1', 0)],reverse=True)
class Btl_GL_18LotoMethod(BasePredictionMethod, BaseMakeResult):
    def get_code(self): return "btl_gl_18"
    def get_name(self): return "BTL GL_ 18"
    def get_description(self): return "Tổng từ giải 3.1.5 và giải 3.4.5"
    def calculate(self, data): return self._make_result(data, [('giai_3_1', 4)], [('giai_3_4', 4)],reverse=True)
class Btl_GL_19LotoMethod(BasePredictionMethod, BaseMakeResult):
    def get_code(self): return "btl_gl_19"
    def get_name(self): return "BTL GL_ 19"
    def get_description(self): return "Tổng từ giải 4.2.4 và giải 4.4.4"
    def calculate(self, data): return self._make_result(data, [('giai_4_2', 3)], [('giai_4_4', 3, "ball")],reverse=True)
class Btl_GL_20LotoMethod(BasePredictionMethod, BaseMakeResult):
    def get_code(self): return "btl_gl_20"
    def get_name(self): return "BTL GL_ 20"
    def get_description(self): return "Tổng từ giải 3.1.1 và giải 1.1.1"
    def calculate(self, data): return self._make_result(data, [('giai_3_1', 0)], [('giai_1', 0, "ball")],reverse=True)

class Btl_GL_21LotoMethod(BasePredictionMethod, BaseMakeResult):
    def get_code(self): return "btl_gl_21"
    def get_name(self): return "BTL GL_ 21"
    def get_description(self): return "Tổng từ giải 4.1.2 và giải 4.1.4"
    def calculate(self, data): return self._make_result(data, [('giai_4_1', 1)], [('giai_4_1', 3, "ball")],reverse=True)    