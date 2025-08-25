from typing import Dict, List, Any
from .base import BasePredictionMethod
from .utils import get_ball_number
import logging

logger = logging.getLogger(__name__)

class De105TwoDigitMethod(BasePredictionMethod):
    """
    Phương pháp 105 Đề 2 số
    Dự đoán từ giải 3.1, 4.1, 6.3
    """
    def get_code(self) -> str:
        return "de105_2d"
    
    def get_name(self) -> str:
        return "105 Đề 2 số"
    
    def get_description(self) -> str:
        return "Dự đoán 2 số từ giải 3.1, 4.1, 6.3"
    
    def calculate(self, data: Dict[str, Any]) -> Dict[str, List[str]]:
        # Lấy các giải chi tiết theo cấu trúc mới
        giai_3_1 = data.get('giai_3_1', '')
        giai_4_1 = data.get('giai_4_1', '')
        giai_6_3 = data.get('giai_6_3', '')
        
        if not all([giai_3_1, giai_4_1, giai_6_3]):
            logger.warning(f"[{self.get_code()}] Thiếu dữ liệu đầu vào: giai_3_1={giai_3_1}, giai_4_1={giai_4_1}, giai_6_3={giai_6_3}")
            return {'two_digits_special': []}  # Thay đổi key này từ 'two_digits' thành 'two_digits_special'
        
        try:
            # Giải 3.1: Lấy số thứ 4 (index 3)
            digit_3_1 = giai_3_1[3] if len(giai_3_1) > 3 else '0'
            
            # Giải 4.1: Lấy số cuối cùng
            digit_4_1 = giai_4_1[-1] if giai_4_1 else '0'
            
            # Tính tổng 2 số cuối
            sum_digits = (int(digit_3_1) + int(digit_4_1)) % 10
            bong_sum_digits = str(get_ball_number(int(sum_digits)))
            # Giải 6.3: Lấy số đầu tiên
            digit_6_3 = giai_6_3[0] if len(giai_6_3) > 0 else '0'
            bong_6_3 = str(get_ball_number(int(digit_6_3)))
            
            two_digits = {
                f"{sum_digits}{digit_6_3}",
                f"{digit_6_3}{sum_digits}",
                f"{sum_digits}{bong_6_3}",
                f"{bong_6_3}{sum_digits}",
                f"{bong_sum_digits}{digit_6_3}",
                f"{digit_6_3}{bong_sum_digits}",
                f"{bong_sum_digits}{bong_6_3}",
                f"{bong_6_3}{bong_sum_digits}",
            }
            
            logger.info(f"[{self.get_code()}] Kết quả: {sorted(list(two_digits))}")
            return {
                'two_digits_special': sorted(list(two_digits))  # Thay đổi key này từ 'two_digits' thành 'two_digits_special'
            }
        except (ValueError, IndexError, TypeError) as e:
            logger.error(f"[{self.get_code()}] Lỗi tính 105 đề 2 số: {str(e)}")
            return {'two_digits_special': []}  # Thay đổi key này từ 'two_digits' thành 'two_digits_special'


class De105ThreeDigitMethod(BasePredictionMethod):
    """
    Phương pháp 105 Đề 3 số
    Dự đoán từ giải 3.1, 4.1, 6.3, 3.6
    """
    def get_code(self) -> str:
        return "de105_3d"
    
    def get_name(self) -> str:
        return "105 Đề 3 số"
    
    def get_description(self) -> str:
        return "Dự đoán 3 số từ giải 3.1, 4.1, 6.3, 3.6"
    
    def calculate(self, data: Dict[str, Any]) -> Dict[str, List[str]]:
        # Lấy các giải chi tiết theo cấu trúc mới
        giai_3_1 = data.get('giai_3_1', '')
        giai_3_6 = data.get('giai_3_6', '')
        giai_4_1 = data.get('giai_4_1', '')
        giai_6_3 = data.get('giai_6_3', '')
        
        if not all([giai_3_1, giai_3_6, giai_4_1, giai_6_3]):
            logger.warning(f"[{self.get_code()}] Thiếu dữ liệu đầu vào: giai_3_1={giai_3_1}, giai_3_6={giai_3_6}, giai_4_1={giai_4_1}, giai_6_3={giai_6_3}")
            return {'three_digits_special': []}  # Thay đổi key này từ 'three_digits' thành 'three_digits_special'
        
        try:
            # Tính toán 2 số như phương pháp 2 số
            digit_3_1 = giai_3_1[3] if len(giai_3_1) > 3 else '0'
            digit_4_1 = giai_4_1[-1] if giai_4_1 else '0'
            sum_digits = (int(digit_3_1) + int(digit_4_1)) % 10
            bong_sum_digits = str(get_ball_number(int(sum_digits)))
            digit_6_3 = giai_6_3[0] if len(giai_6_3) > 0 else '0'
            bong_6_3 = str(get_ball_number(int(digit_6_3)))
            
            two_digits = {
                f"{sum_digits}{digit_6_3}",
                f"{digit_6_3}{sum_digits}",
                f"{sum_digits}{bong_6_3}",
                f"{bong_6_3}{sum_digits}",
                f"{bong_sum_digits}{digit_6_3}",
                f"{digit_6_3}{bong_sum_digits}",
                f"{bong_sum_digits}{bong_6_3}",
                f"{bong_6_3}{bong_sum_digits}",
            }
            
            # Thêm số thứ 3 từ giải 3.6 (số thứ 2)
            cang_digit = giai_3_6[1] if len(giai_3_6) > 1 else ''
            if not cang_digit:
                logger.warning(f"[{self.get_code()}] Không thể lấy số thứ 2 từ giải 3.6: {giai_3_6}")
                return {'three_digits_special': []}  # Thay đổi key này từ 'three_digits' thành 'three_digits_special'
                
            cang_bong = str(get_ball_number(int(cang_digit)))
            
            # Tạo các bộ 3 số
            three_digits = set()
            for cang in [cang_digit, cang_bong]:
                for num in two_digits:
                    three_digits.add(f"{cang}{num}")
            
            logger.info(f"[{self.get_code()}] Kết quả: {sorted(list(three_digits))}")
            return {
                'three_digits_special': sorted(list(three_digits))  # Thay đổi key này từ 'three_digits' thành 'three_digits_special'
            }
        except (ValueError, IndexError, TypeError) as e:
            logger.error(f"[{self.get_code()}] Lỗi tính 105 đề 3 số: {str(e)}")
            return {'three_digits_special': []}  # Thay đổi key này từ 'three_digits' thành 'three_digits_special'