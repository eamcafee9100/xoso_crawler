from typing import Dict, List, Any
from .base import BasePredictionMethod
from .utils import get_ball_number
import logging

logger = logging.getLogger(__name__)

class De119TwoDigitMethod(BasePredictionMethod):
    """
    Phương pháp 119 Đề 2 số
    Dự đoán từ giải 4.1 (số thứ 4 và bóng) và giải 7.3 (số thứ 1 và bóng)
    """
    def get_code(self) -> str:
        return "de119_2d"
    
    def get_name(self) -> str:
        return "119 Đề 2 số"
    
    def get_description(self) -> str:
        return "Dự đoán 2 số từ giải 4.1 và giải 7.3"
    
    def calculate(self, data: Dict[str, Any]) -> Dict[str, List[str]]:
        giai_4_1 = data.get('giai_4_1', '')
        giai_7_3 = data.get('giai_7_3', '')
        
        if not giai_4_1 or not giai_7_3:
            logger.warning(f"[{self.get_code()}] Thiếu dữ liệu đầu vào: giai_4_1={giai_4_1}, giai_7_3={giai_7_3}")
            return {'two_digits_special': []}
        
        try:
            # Số thứ nhất từ giải 4.1: số thứ 4 và bóng
            # Ví dụ: 2496 -> số thứ 4 = 6, bóng là 1
            if len(giai_4_1) >= 4:
                digit_fourth = giai_4_1[3]
                first_nums = [digit_fourth, str(get_ball_number(int(digit_fourth)))]
            else:
                logger.warning(f"[{self.get_code()}] Giải 4.1 không đủ dài: {giai_4_1}")
                return {'two_digits_special': []}
                
            # Số thứ hai từ giải 7.3: số thứ 1 và bóng
            # Ví dụ: 32 -> số thứ 1 = 3, bóng là 8
            if len(giai_7_3) >= 1:
                digit_first = giai_7_3[0]
                second_nums = [digit_first, str(get_ball_number(int(digit_first)))]
            else:
                logger.warning(f"[{self.get_code()}] Giải 7.3 không đủ dài: {giai_7_3}")
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
            logger.error(f"[{self.get_code()}] Lỗi tính 119 đề 2 số: {str(e)}")
            return {'two_digits_special': []}

class De119ThreeDigitMethod(BasePredictionMethod):
    """
    Phương pháp 119 Đề 3 số
    Dự đoán từ giải 4.1 (số thứ 4 và bóng), giải 7.3 (số thứ 1 và bóng), và giải 2.1 (càng đề)
    """
    def get_code(self) -> str:
        return "de119_3d"
    
    def get_name(self) -> str:
        return "119 Đề 3 số"
    
    def get_description(self) -> str:
        return "Dự đoán 3 số từ giải 4.1, 7.3 và giải 2.1 (càng đề)"
    
    def calculate(self, data: Dict[str, Any]) -> Dict[str, List[str]]:
        giai_4_1 = data.get('giai_4_1', '')
        giai_7_3 = data.get('giai_7_3', '')
        giai_2_1 = data.get('giai_2_1', '')
        
        if not giai_4_1 or not giai_7_3 or not giai_2_1:
            logger.warning(f"[{self.get_code()}] Thiếu dữ liệu đầu vào: giai_4_1={giai_4_1}, giai_7_3={giai_7_3}, giai_2_1={giai_2_1}")
            return {'three_digits_special': []}
        
        try:
            # Số thứ nhất từ giải 4.1: số thứ 4 và bóng
            # Ví dụ: 2496 -> số thứ 4 = 6, bóng là 1
            if len(giai_4_1) >= 4:
                digit_fourth = giai_4_1[3]
                first_nums = [digit_fourth, str(get_ball_number(int(digit_fourth)))]
            else:
                logger.warning(f"[{self.get_code()}] Giải 4.1 không đủ dài: {giai_4_1}")
                return {'three_digits_special': []}
                
            # Số thứ hai từ giải 7.3: số thứ 1 và bóng
            # Ví dụ: 32 -> số thứ 1 = 3, bóng là 8
            if len(giai_7_3) >= 1:
                digit_first = giai_7_3[0]
                second_nums = [digit_first, str(get_ball_number(int(digit_first)))]
            else:
                logger.warning(f"[{self.get_code()}] Giải 7.3 không đủ dài: {giai_7_3}")
                return {'three_digits_special': []}
            
            # Tạo các cặp số 2 chữ số (bao gồm cả cặp đảo ngược)
            two_digits = []
            for first in first_nums:
                for second in second_nums:
                    two_digits.append(f"{first}{second}")
                    two_digits.append(f"{second}{first}")
            
            # Càng đề từ giải 2.1: số thứ 1 và bóng
            # Ví dụ: 23496 -> số thứ 1 = 2, bóng là 7
            if len(giai_2_1) >= 1:
                digit_first_cang = giai_2_1[0]
                cang_nums = [digit_first_cang, str(get_ball_number(int(digit_first_cang)))]
            else:
                logger.warning(f"[{self.get_code()}] Giải 2.1 không đủ dài: {giai_2_1}")
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
            logger.error(f"[{self.get_code()}] Lỗi tính 119 đề 3 số: {str(e)}")
            return {'three_digits_special': []}