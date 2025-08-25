from typing import Dict, List, Any
from .base import BasePredictionMethod
from .utils import get_ball_number
import logging

logger = logging.getLogger(__name__)

class TuThuDeMethod(BasePredictionMethod):
    """
    Phương pháp Tứ Thủ Đề
    """
    def get_code(self) -> str:
        return "tu_thu_de"
    
    def get_name(self) -> str:
        return "Tứ Thủ Đề"
    
    def get_description(self) -> str:
        return "Phương pháp tứ thủ đề từ giải 4 và giải 5"
    
    def calculate(self, data: Dict[str, Any]) -> Dict[str, List[str]]:
        try:
            # Lấy các giải chi tiết theo cấu trúc mới
            giai_4_1 = data.get('giai_4_1', '')
            giai_4_4 = data.get('giai_4_4', '')  # Giải 4 cuối cùng
            giai_5_5 = data.get('giai_5_5', '')  # Giải 5 thứ 5
            
            if not giai_4_1 or not giai_4_4 or not giai_5_5:
                logger.warning(f"[{self.get_code()}] Thiếu dữ liệu đầu vào: giai_4_1={giai_4_1}, giai_4_4={giai_4_4}, giai_5_5={giai_5_5}")
                return {'two_digits_special': []}
            
            if len(giai_4_1) < 2 or len(giai_4_4) < 2 or len(giai_5_5) < 2:
                logger.warning(f"[{self.get_code()}] Các giải không đủ dài: giai_4_1={giai_4_1}, giai_4_4={giai_4_4}, giai_5_5={giai_5_5}")
                return {'two_digits_special': []}
            
            # Lấy các chữ số thứ 2 từ mỗi giải
            a_digit = giai_4_1[1]
            a_bong = str(get_ball_number(int(a_digit)))
            
            b_digit = giai_4_4[1]
            b_bong = str(get_ball_number(int(b_digit)))
            
            c_digit = giai_5_5[1]
            c_bong = str(get_ball_number(int(c_digit)))
            
            two_digits_combinations = [
                f"{a_digit}{c_digit}",
                f"{c_digit}{a_digit}",
                f"{a_bong}{c_digit}",
                f"{c_digit}{a_bong}",
            ]
            
            logger.info(f"[{self.get_code()}] Kết quả: {sorted(list(set(two_digits_combinations)))}")
            return {
                'two_digits_special': sorted(list(set(two_digits_combinations)))
            }
        except (ValueError, IndexError, TypeError) as e:
            logger.error(f"[{self.get_code()}] Lỗi: {str(e)}")
            return {'two_digits_special': []}