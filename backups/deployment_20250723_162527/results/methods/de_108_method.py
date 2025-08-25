from typing import Dict, List, Any
from .base import BasePredictionMethod
from .utils import get_ball_number
import logging

logger = logging.getLogger(__name__)

class De108TwoDigitMethod(BasePredictionMethod):
    """
    Phương pháp 108 Đề 2 số
    Dự đoán từ giải 3.2 (số thứ 1 và bóng) và giải 3.6 (số thứ 4)
    """
    def get_code(self) -> str:
        return "de108_2d"
    
    def get_name(self) -> str:
        return "108 Đề 2 số"
    
    def get_description(self) -> str:
        return "Dự đoán 2 số từ giải 3.2 và giải 3.6"
    
    def calculate(self, data: Dict[str, Any]) -> Dict[str, List[str]]:
        giai_3_2 = data.get('giai_3_2', '')
        giai_3_6 = data.get('giai_3_6', '')
        
        if not giai_3_2 or not giai_3_6:
            logger.warning(f"[{self.get_code()}] Thiếu dữ liệu đầu vào: giai_3_2={giai_3_2}, giai_3_6={giai_3_6}")
            return {'two_digits_special': []}
        
        try:
            # Số thứ nhất từ giải 3.2: số thứ 1 và bóng
            # Ví dụ: 23496 -> số thứ 1 = 2 và bóng là 7
            if len(giai_3_2) >= 1:
                digit_first = giai_3_2[0]
                first_nums = [digit_first, str(get_ball_number(int(digit_first)))]
            else:
                logger.warning(f"[{self.get_code()}] Giải 3.2 không đủ dài: {giai_3_2}")
                return {'two_digits_special': []}
                
            # Số thứ hai từ giải 3.6: số thứ 4, không lấy bóng
            # Ví dụ: 13234 -> số thứ 4 = 3
            if len(giai_3_6) >= 4:
                digit_fourth = giai_3_6[3]
                second_nums = [digit_fourth]
            else:
                logger.warning(f"[{self.get_code()}] Giải 3.6 không đủ dài: {giai_3_6}")
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
            logger.error(f"[{self.get_code()}] Lỗi tính 108 đề 2 số: {str(e)}")
            return {'two_digits_special': []}

class De108ThreeDigitMethod(BasePredictionMethod):
    """
    Phương pháp 108 Đề 3 số
    Dự đoán từ giải 3.2 (số thứ 1 và bóng), giải 3.6 (số thứ 4), và giải 3.5 (càng đề)
    """
    def get_code(self) -> str:
        return "de108_3d"
    
    def get_name(self) -> str:
        return "108 Đề 3 số"
    
    def get_description(self) -> str:
        return "Dự đoán 3 số từ giải 3.2, 3.6 và giải 3.5 (càng đề)"
    
    def calculate(self, data: Dict[str, Any]) -> Dict[str, List[str]]:
        giai_3_2 = data.get('giai_3_2', '')
        giai_3_6 = data.get('giai_3_6', '')
        giai_3_5 = data.get('giai_3_5', '')
        
        if not giai_3_2 or not giai_3_6 or not giai_3_5:
            logger.warning(f"[{self.get_code()}] Thiếu dữ liệu đầu vào: giai_3_2={giai_3_2}, giai_3_6={giai_3_6}, giai_3_5={giai_3_5}")
            return {'three_digits_special': []}
        
        try:
            # Số thứ nhất từ giải 3.2: số thứ 1 và bóng
            # Ví dụ: 23496 -> số thứ 1 = 2 và bóng là 7
            if len(giai_3_2) >= 1:
                digit_first = giai_3_2[0]
                first_nums = [digit_first, str(get_ball_number(int(digit_first)))]
            else:
                logger.warning(f"[{self.get_code()}] Giải 3.2 không đủ dài: {giai_3_2}")
                return {'three_digits_special': []}
                
            # Số thứ hai từ giải 3.6: số thứ 4, không lấy bóng
            # Ví dụ: 13234 -> số thứ 4 = 3
            if len(giai_3_6) >= 4:
                digit_fourth = giai_3_6[3]
                second_nums = [digit_fourth]
            else:
                logger.warning(f"[{self.get_code()}] Giải 3.6 không đủ dài: {giai_3_6}")
                return {'three_digits_special': []}
            
            # Tạo các cặp số 2 chữ số (bao gồm cả cặp đảo ngược)
            two_digits = []
            for first in first_nums:
                for second in second_nums:
                    two_digits.append(f"{first}{second}")
                    two_digits.append(f"{second}{first}")
            
            # Càng đề từ giải 3.5: số thứ 1 và bóng
            # Ví dụ: 12628 -> số thứ 1 = 1 và bóng là 6
            if len(giai_3_5) >= 1:
                digit_first_cang = giai_3_5[0]
                cang_nums = [digit_first_cang, str(get_ball_number(int(digit_first_cang)))]
            else:
                logger.warning(f"[{self.get_code()}] Giải 3.5 không đủ dài: {giai_3_5}")
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
            logger.error(f"[{self.get_code()}] Lỗi tính 108 đề 3 số: {str(e)}")
            return {'three_digits_special': []}