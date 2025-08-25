from typing import Dict, List, Any
from .base import BasePredictionMethod
from .utils import get_ball_number
import logging

logger = logging.getLogger(__name__)

class De127TwoDigitMethod(BasePredictionMethod):
    """
    Phương pháp 127 Đề 2 số
    Dự đoán từ giải 6.3 (số thứ 3 và bóng) và giải 7.2 (số thứ 2 và bóng)
    """
    def get_code(self) -> str:
        return "de127_2d"
    
    def get_name(self) -> str:
        return "127 Đề 2 số"
    
    def get_description(self) -> str:
        return "Dự đoán 2 số từ giải 6.3 và giải 7.2"
    
    def calculate(self, data: Dict[str, Any]) -> Dict[str, List[str]]:
        giai_6_3 = data.get('giai_6_3', '')
        giai_7_2 = data.get('giai_7_2', '')
        
        if not giai_6_3 or not giai_7_2:
            logger.warning(f"[{self.get_code()}] Thiếu dữ liệu đầu vào: giai_6_3={giai_6_3}, giai_7_2={giai_7_2}")
            return {'two_digits_special': []}
        
        try:
            # Số thứ nhất từ giải 6.3: số thứ 3 và bóng
            # Ví dụ: 234 -> số thứ 3 = 4, bóng là 9
            if len(giai_6_3) >= 3:
                digit_third = giai_6_3[2]
                first_nums = [digit_third, str(get_ball_number(int(digit_third)))]
            else:
                logger.warning(f"[{self.get_code()}] Giải 6.3 không đủ dài: {giai_6_3}")
                return {'two_digits_special': []}
                
            # Số thứ hai từ giải 7.2: số thứ 2 và bóng
            # Ví dụ: 14 -> số thứ 2 = 4, bóng là 9
            if len(giai_7_2) >= 2:
                digit_second = giai_7_2[1]
                second_nums = [digit_second, str(get_ball_number(int(digit_second)))]
            else:
                logger.warning(f"[{self.get_code()}] Giải 7.2 không đủ dài: {giai_7_2}")
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
            logger.error(f"[{self.get_code()}] Lỗi tính 127 đề 2 số: {str(e)}")
            return {'two_digits_special': []}

class De127ThreeDigitMethod(BasePredictionMethod):
    """
    Phương pháp 127 Đề 3 số
    Dự đoán từ giải 6.3 (số thứ 3 và bóng), giải 7.2 (số thứ 2 và bóng), và giải 4.1 (càng đề)
    """
    def get_code(self) -> str:
        return "de127_3d"
    
    def get_name(self) -> str:
        return "127 Đề 3 số"
    
    def get_description(self) -> str:
        return "Dự đoán 3 số từ giải 6.3, 7.2 và giải 4.1 (càng đề)"
    
    def calculate(self, data: Dict[str, Any]) -> Dict[str, List[str]]:
        giai_6_3 = data.get('giai_6_3', '')
        giai_7_2 = data.get('giai_7_2', '')
        giai_4_1 = data.get('giai_4_1', '')
        
        if not giai_6_3 or not giai_7_2 or not giai_4_1:
            logger.warning(f"[{self.get_code()}] Thiếu dữ liệu đầu vào: giai_6_3={giai_6_3}, giai_7_2={giai_7_2}, giai_4_1={giai_4_1}")
            return {'three_digits_special': []}
        
        try:
            # Số thứ nhất từ giải 6.3: số thứ 3 và bóng
            # Ví dụ: 234 -> số thứ 3 = 4, bóng là 9
            if len(giai_6_3) >= 3:
                digit_third = giai_6_3[2]
                first_nums = [digit_third, str(get_ball_number(int(digit_third)))]
            else:
                logger.warning(f"[{self.get_code()}] Giải 6.3 không đủ dài: {giai_6_3}")
                return {'three_digits_special': []}
                
            # Số thứ hai từ giải 7.2: số thứ 2 và bóng
            # Ví dụ: 14 -> số thứ 2 = 4, bóng là 9
            if len(giai_7_2) >= 2:
                digit_second = giai_7_2[1]
                second_nums = [digit_second, str(get_ball_number(int(digit_second)))]
            else:
                logger.warning(f"[{self.get_code()}] Giải 7.2 không đủ dài: {giai_7_2}")
                return {'three_digits_special': []}
            
            # Tạo các cặp số 2 chữ số (bao gồm cả cặp đảo ngược)
            two_digits = []
            for first in first_nums:
                for second in second_nums:
                    two_digits.append(f"{first}{second}")
                    two_digits.append(f"{second}{first}")
            
            # Càng đề từ giải 4.1: số thứ 1 và bóng
            # Ví dụ: 2628 -> số thứ 1 = 2, bóng là 7
            if len(giai_4_1) >= 1:
                digit_first_cang = giai_4_1[0]
                cang_nums = [digit_first_cang, str(get_ball_number(int(digit_first_cang)))]
            else:
                logger.warning(f"[{self.get_code()}] Giải 4.1 không đủ dài: {giai_4_1}")
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
            logger.error(f"[{self.get_code()}] Lỗi tính 127 đề 3 số: {str(e)}")
            return {'three_digits_special': []}