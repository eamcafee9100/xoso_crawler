# from typing import Dict, List, Any
from typing import Any, Dict, List
from .utils import get_ball_number
from .base import BaseMakeResult, BasePredictionMethod
import logging
logger = logging.getLogger(__name__)

class Btl_SC_BB_01LotoMethod(BasePredictionMethod, BaseMakeResult):
    def get_code(self): return "btl_sc_bb_01"
    def get_name(self): return "SC_BB 01"
    def get_description(self): return "Tổng từ giải 3.2.3 + 3.4.1 + 3.6.5 và giải 1.1.3 + 3.4.5 + 3.6.1"
    def calculate(self, data): return self._make_result(data, [('giai_3_2', 2), ('giai_3_4', 0), ('giai_3_6', 4)], [('giai_1', 2), ('giai_3_4', 4), ('giai_3_6', 0)], reverse=True)


class Btl_SC_BB_02LotoMethod(BasePredictionMethod, BaseMakeResult):
    def get_code(self): return "btl_sc_bb_02"
    def get_name(self): return "SC_BB 02"
    def get_description(self): return "Tổng từ giải 3.2.3 + 3.4.1 + 3.6.5 và giải 1.1.3 + 3.4.5 + 3.6.1"
    def calculate(self, data): return self._make_result(data, [('giai_3_2', 2), ('giai_3_4', 0), ('giai_3_6', 4)], [('giai_1', 2), ('giai_3_4', 4), ('giai_3_6', 0)], reverse=True)

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
        
