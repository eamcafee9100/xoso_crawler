from typing import Dict, List, Any
from .base import BasePredictionMethod
from .utils import get_ball_number
import logging

logger = logging.getLogger(__name__)

class De135TwoDigitMethod(BasePredictionMethod):
    """
    Phương pháp 135 Đề 2 số
    Dự đoán từ giải 2.1 (số thứ 4 và bóng) và giải 6.2 (số thứ 2 và bóng)
    """
    def get_code(self) -> str:
        return "de135_2d"
    
    def get_name(self) -> str:
        return "135 Đề 2 số"
    
    def get_description(self) -> str:
        return "Dự đoán 2 số từ giải 2.1 và giải 6.2"
    
    def calculate(self, data: Dict[str, Any]) -> Dict[str, List[str]]:
        giai_2_1 = data.get('giai_2_1', '')
        giai_6_2 = data.get('giai_6_2', '')
        
        if not giai_2_1 or not giai_6_2:
            logger.warning(f"[{self.get_code()}] Thiếu dữ liệu đầu vào: giai_2_1={giai_2_1}, giai_6_2={giai_6_2}")
            return {'two_digits_special': []}
        
        try:
            # Số thứ nhất từ giải 2.1: số thứ 4 và bóng
            # Ví dụ: 25249 -> số thứ 4 = 4, bóng là 9
            if len(giai_2_1) >= 4:
                digit_fourth = giai_2_1[3]
                first_nums = [digit_fourth, str(get_ball_number(int(digit_fourth)))]
            else:
                logger.warning(f"[{self.get_code()}] Giải 2.1 không đủ dài: {giai_2_1}")
                return {'two_digits_special': []}
                
            # Số thứ hai từ giải 6.2: số thứ 2 và bóng
            # Ví dụ: 123 -> số thứ 2 = 2, bóng là 7
            if len(giai_6_2) >= 2:
                digit_second = giai_6_2[1]
                second_nums = [digit_second, str(get_ball_number(int(digit_second)))]
            else:
                logger.warning(f"[{self.get_code()}] Giải 6.2 không đủ dài: {giai_6_2}")
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
            logger.error(f"[{self.get_code()}] Lỗi tính 135 đề 2 số: {str(e)}")
            return {'two_digits_special': []}

class De135ThreeDigitMethod(BasePredictionMethod):
    """
    Phương pháp 135 Đề 3 số
    Dự đoán từ giải 2.1 (số thứ 4 và bóng), giải 6.2 (số thứ 2 và bóng), và giải 7.1 (càng đề)
    """
    def get_code(self) -> str:
        return "de135_3d"
    
    def get_name(self) -> str:
        return "135 Đề 3 số"
    
    def get_description(self) -> str:
        return "Dự đoán 3 số từ giải 2.1, 6.2 và giải 7.1 (càng đề)"
    
    def calculate(self, data: Dict[str, Any]) -> Dict[str, List[str]]:
        giai_2_1 = data.get('giai_2_1', '')
        giai_6_2 = data.get('giai_6_2', '')
        giai_7_1 = data.get('giai_7_1', '')
        
        if not giai_2_1 or not giai_6_2 or not giai_7_1:
            logger.warning(f"[{self.get_code()}] Thiếu dữ liệu đầu vào: giai_2_1={giai_2_1}, giai_6_2={giai_6_2}, giai_7_1={giai_7_1}")
            return {'three_digits_special': []}
        
        try:
            # Số thứ nhất từ giải 2.1: số thứ 4 và bóng
            # Ví dụ: 25249 -> số thứ 4 = 4, bóng là 9
            if len(giai_2_1) >= 4:
                digit_fourth = giai_2_1[3]
                first_nums = [digit_fourth, str(get_ball_number(int(digit_fourth)))]
            else:
                logger.warning(f"[{self.get_code()}] Giải 2.1 không đủ dài: {giai_2_1}")
                return {'three_digits_special': []}
                
            # Số thứ hai từ giải 6.2: số thứ 2 và bóng
            # Ví dụ: 123 -> số thứ 2 = 2, bóng là 7
            if len(giai_6_2) >= 2:
                digit_second = giai_6_2[1]
                second_nums = [digit_second, str(get_ball_number(int(digit_second)))]
            else:
                logger.warning(f"[{self.get_code()}] Giải 6.2 không đủ dài: {giai_6_2}")
                return {'three_digits_special': []}
            
            # Tạo các cặp số 2 chữ số (bao gồm cả cặp đảo ngược)
            two_digits = []
            for first in first_nums:
                for second in second_nums:
                    two_digits.append(f"{first}{second}")
                    two_digits.append(f"{second}{first}")
            
            # Càng đề từ giải 7.1: số thứ 1 và bóng
            # Ví dụ: 41 -> số thứ 1 = 4, bóng là 9
            if len(giai_7_1) >= 1:
                digit_first_cang = giai_7_1[0]
                cang_nums = [digit_first_cang, str(get_ball_number(int(digit_first_cang)))]
            else:
                logger.warning(f"[{self.get_code()}] Giải 7.1 không đủ dài: {giai_7_1}")
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
            logger.error(f"[{self.get_code()}] Lỗi tính 135 đề 3 số: {str(e)}")
            return {'three_digits_special': []}