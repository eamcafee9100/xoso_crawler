from typing import Dict, List, Any
from .base import BasePredictionMethod
from .utils import get_ball_number
import logging

logger = logging.getLogger(__name__)

class De130TwoDigitMethod(BasePredictionMethod):
    """
    Phương pháp 130 Đề 2 số
    Dự đoán từ giải 5.6 (số thứ 1 và bóng) và giải 7.1 (số thứ 2 và bóng)
    """
    def get_code(self) -> str:
        return "de130_2d"
    
    def get_name(self) -> str:
        return "130 Đề 2 số"
    
    def get_description(self) -> str:
        return "Dự đoán 2 số từ giải 5.6 và giải 7.1"
    
    def calculate(self, data: Dict[str, Any]) -> Dict[str, List[str]]:
        giai_5_6 = data.get('giai_5_6', '')
        giai_7_1 = data.get('giai_7_1', '')
        
        if not giai_5_6 or not giai_7_1:
            logger.warning(f"[{self.get_code()}] Thiếu dữ liệu đầu vào: giai_5_6={giai_5_6}, giai_7_1={giai_7_1}")
            return {'two_digits_special': []}
        
        try:
            # Số thứ nhất từ giải 5.6: số thứ 1 và bóng
            # Ví dụ: 24249 -> số thứ 1 = 2, bóng là 7
            if len(giai_5_6) >= 1:
                digit_first = giai_5_6[0]
                first_nums = [digit_first, str(get_ball_number(int(digit_first)))]
            else:
                logger.warning(f"[{self.get_code()}] Giải 5.6 không đủ dài: {giai_5_6}")
                return {'two_digits_special': []}
                
            # Số thứ hai từ giải 7.1: số thứ 2 và bóng
            # Ví dụ: 12 -> số thứ 2 = 2, bóng là 7
            if len(giai_7_1) >= 2:
                digit_second = giai_7_1[1]
                second_nums = [digit_second, str(get_ball_number(int(digit_second)))]
            else:
                logger.warning(f"[{self.get_code()}] Giải 7.1 không đủ dài: {giai_7_1}")
                return {'two_digits_special': []}
            
            # Tạo các cặp số 2 chữ số (bao gồm cả cặp đảo ngược)
            two_digits = set()
            for first in first_nums:
                for second in second_nums:
                    two_digits.add(f"{first}{second}")
                    two_digits.add(f"{second}{first}")
            
            logger.info(f"[{self.get_code()}] Kết quả: {sorted(list(two_digits))}")
            return {
                'two_digits_special': sorted(list(two_digits))
            }
        except (ValueError, IndexError, TypeError) as e:
            logger.error(f"[{self.get_code()}] Lỗi tính 130 đề 2 số: {str(e)}")
            return {'two_digits_special': []}

class De130ThreeDigitMethod(BasePredictionMethod):
    """
    Phương pháp 130 Đề 3 số
    Dự đoán từ giải 5.6 (số thứ 1 và bóng), giải 7.1 (số thứ 2 và bóng), và giải 4.2 (càng đề từ tổng số thứ 1 và 2)
    """
    def get_code(self) -> str:
        return "de130_3d"
    
    def get_name(self) -> str:
        return "130 Đề 3 số"
    
    def get_description(self) -> str:
        return "Dự đoán 3 số từ giải 5.6, 7.1 và giải 4.2 (càng đề)"
    
    def calculate(self, data: Dict[str, Any]) -> Dict[str, List[str]]:
        giai_5_6 = data.get('giai_5_6', '')
        giai_7_1 = data.get('giai_7_1', '')
        giai_4_2 = data.get('giai_4_2', '')
        
        if not giai_5_6 or not giai_7_1 or not giai_4_2:
            logger.warning(f"[{self.get_code()}] Thiếu dữ liệu đầu vào: giai_5_6={giai_5_6}, giai_7_1={giai_7_1}, giai_4_2={giai_4_2}")
            return {'three_digits_special': []}
        
        try:
            # Số thứ nhất từ giải 5.6: số thứ 1 và bóng
            # Ví dụ: 24249 -> số thứ 1 = 2, bóng là 7
            if len(giai_5_6) >= 1:
                digit_first = giai_5_6[0]
                first_nums = [digit_first, str(get_ball_number(int(digit_first)))]
            else:
                logger.warning(f"[{self.get_code()}] Giải 5.6 không đủ dài: {giai_5_6}")
                return {'three_digits_special': []}
                
            # Số thứ hai từ giải 7.1: số thứ 2 và bóng
            # Ví dụ: 12 -> số thứ 2 = 2, bóng là 7
            if len(giai_7_1) >= 2:
                digit_second = giai_7_1[1]
                second_nums = [digit_second, str(get_ball_number(int(digit_second)))]
            else:
                logger.warning(f"[{self.get_code()}] Giải 7.1 không đủ dài: {giai_7_1}")
                return {'three_digits_special': []}
            
            # Tạo các cặp số 2 chữ số (bao gồm cả cặp đảo ngược)
            two_digits = []
            for first in first_nums:
                for second in second_nums:
                    two_digits.append(f"{first}{second}")
                    two_digits.append(f"{second}{first}")
            
            # Càng đề từ giải 4.2: tổng số thứ 1 và số thứ 2, lấy số cuối và bóng
            # Ví dụ: 3123 -> số thứ 1 = 3, số thứ 2 = 1 -> tổng = 4, bóng là 9
            if len(giai_4_2) >= 2:
                digit_first_cang = int(giai_4_2[0])
                digit_second_cang = int(giai_4_2[1])
                sum_digits = (digit_first_cang + digit_second_cang) % 10  # Lấy số cuối của tổng
                cang_nums = [str(sum_digits), str(get_ball_number(sum_digits))]
            else:
                logger.warning(f"[{self.get_code()}] Giải 4.2 không đủ dài: {giai_4_2}")
                return {'three_digits_special': []}
            
            # Tạo các cặp số 3 chữ số
            three_digits = set()
            for cang in cang_nums:
                for two_digit in two_digits:
                    three_digits.add(f"{cang}{two_digit}")
            
            logger.info(f"[{self.get_code()}] Kết quả: {sorted(list(three_digits))}")
            return {
                'three_digits_special': sorted(list(three_digits))
            }
        except (ValueError, IndexError, TypeError) as e:
            logger.error(f"[{self.get_code()}] Lỗi tính 130 đề 3 số: {str(e)}")
            return {'three_digits_special': []}