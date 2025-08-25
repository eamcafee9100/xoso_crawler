from typing import Dict, List, Any
from .base import BasePredictionMethod
from .utils import get_ball_number
import logging

logger = logging.getLogger(__name__)

class De126TwoDigitMethod(BasePredictionMethod):
    """
    Phương pháp 126 Đề 2 số
    Dự đoán từ giải 1 (số thứ 5 và bóng) và giải 5.6 (số thứ 4 và bóng)
    """
    def get_code(self) -> str:
        return "de126_2d"
    
    def get_name(self) -> str:
        return "126 Đề 2 số"
    
    def get_description(self) -> str:
        return "Dự đoán 2 số từ giải 1 và giải 5.6"
    
    def calculate(self, data: Dict[str, Any]) -> Dict[str, List[str]]:
        giai_1 = data.get('giai_1', '')
        giai_5_6 = data.get('giai_5_6', '')
        
        if not giai_1 or not giai_5_6:
            logger.warning(f"[{self.get_code()}] Thiếu dữ liệu đầu vào: giai_1={giai_1}, giai_5_6={giai_5_6}")
            return {'two_digits_special': []}
        
        try:
            # Số thứ nhất từ giải 1: số thứ 5 và bóng
            # Ví dụ: 23491 -> số thứ 5 = 1, bóng là 6
            if len(giai_1) >= 5:
                digit_fifth = giai_1[4]
                first_nums = [digit_fifth, str(get_ball_number(int(digit_fifth)))]
            else:
                logger.warning(f"[{self.get_code()}] Giải 1 không đủ dài: {giai_1}")
                return {'two_digits_special': []}
                
            # Số thứ hai từ giải 5.6: số thứ 4 và bóng
            # Ví dụ: 1432 -> số thứ 4 = 2, bóng là 7
            if len(giai_5_6) >= 4:
                digit_fourth = giai_5_6[3]
                second_nums = [digit_fourth, str(get_ball_number(int(digit_fourth)))]
            else:
                logger.warning(f"[{self.get_code()}] Giải 5.6 không đủ dài: {giai_5_6}")
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
            logger.error(f"[{self.get_code()}] Lỗi tính 126 đề 2 số: {str(e)}")
            return {'two_digits_special': []}

class De126ThreeDigitMethod(BasePredictionMethod):
    """
    Phương pháp 126 Đề 3 số
    Dự đoán từ giải 1 (số thứ 5 và bóng), giải 5.6 (số thứ 4 và bóng), và giải 4.1 (càng đề)
    """
    def get_code(self) -> str:
        return "de126_3d"
    
    def get_name(self) -> str:
        return "126 Đề 3 số"
    
    def get_description(self) -> str:
        return "Dự đoán 3 số từ giải 1, 5.6 và giải 4.1 (càng đề)"
    
    def calculate(self, data: Dict[str, Any]) -> Dict[str, List[str]]:
        giai_1 = data.get('giai_1', '')
        giai_5_6 = data.get('giai_5_6', '')
        giai_4_1 = data.get('giai_4_1', '')
        
        if not giai_1 or not giai_5_6 or not giai_4_1:
            logger.warning(f"[{self.get_code()}] Thiếu dữ liệu đầu vào: giai_1={giai_1}, giai_5_6={giai_5_6}, giai_4_1={giai_4_1}")
            return {'three_digits_special': []}
        
        try:
            # Số thứ nhất từ giải 1: số thứ 5 và bóng
            # Ví dụ: 23491 -> số thứ 5 = 1, bóng là 6
            if len(giai_1) >= 5:
                digit_fifth = giai_1[4]
                first_nums = [digit_fifth, str(get_ball_number(int(digit_fifth)))]
            else:
                logger.warning(f"[{self.get_code()}] Giải 1 không đủ dài: {giai_1}")
                return {'three_digits_special': []}
                
            # Số thứ hai từ giải 5.6: số thứ 4 và bóng
            # Ví dụ: 1432 -> số thứ 4 = 2, bóng là 7
            if len(giai_5_6) >= 4:
                digit_fourth = giai_5_6[3]
                second_nums = [digit_fourth, str(get_ball_number(int(digit_fourth)))]
            else:
                logger.warning(f"[{self.get_code()}] Giải 5.6 không đủ dài: {giai_5_6}")
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
            logger.error(f"[{self.get_code()}] Lỗi tính 126 đề 3 số: {str(e)}")
            return {'three_digits_special': []}