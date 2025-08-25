from typing import Dict, List, Any
from .base import BasePredictionMethod
from .utils import get_ball_number
import logging

logger = logging.getLogger(__name__)

class De117TwoDigitMethod(BasePredictionMethod):
    """
    Phương pháp 117 Đề 2 số
    Dự đoán từ giải 3.2 (số thứ 5 và bóng) và giải 4.1 (tổng số thứ 2 và 3, lấy bóng)
    """
    def get_code(self) -> str:
        return "de117_2d"
    
    def get_name(self) -> str:
        return "117 Đề 2 số"
    
    def get_description(self) -> str:
        return "Dự đoán 2 số từ giải 3.2 và giải 4.1"
    
    def calculate(self, data: Dict[str, Any]) -> Dict[str, List[str]]:
        giai_3_2 = data.get('giai_3_2', '')
        giai_4_1 = data.get('giai_4_1', '')
        
        if not giai_3_2 or not giai_4_1:
            logger.warning(f"[{self.get_code()}] Thiếu dữ liệu đầu vào: giai_3_2={giai_3_2}, giai_4_1={giai_4_1}")
            return {'two_digits_special': []}
        
        try:
            # Số thứ nhất từ giải 3.2: số thứ 5 và bóng
            # Ví dụ: 23496 -> số thứ 5 = 6, bóng là 1
            if len(giai_3_2) >= 5:
                digit_fifth = giai_3_2[4]
                first_nums = [digit_fifth, str(get_ball_number(int(digit_fifth)))]
            else:
                logger.warning(f"[{self.get_code()}] Giải 3.2 không đủ dài: {giai_3_2}")
                return {'two_digits_special': []}
                
            # Số thứ hai từ giải 4.1: tổng số thứ 2 và 3, lấy bóng
            # Ví dụ: 3241 -> 2+4=6, bóng là 1
            if len(giai_4_1) >= 3:
                sum_second_third = (int(giai_4_1[1]) + int(giai_4_1[2])) % 10
                second_nums = [str(sum_second_third), str(get_ball_number(sum_second_third))]
            else:
                logger.warning(f"[{self.get_code()}] Giải 4.1 không đủ dài: {giai_4_1}")
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
            logger.error(f"[{self.get_code()}] Lỗi tính 117 đề 2 số: {str(e)}")
            return {'two_digits_special': []}

class De117ThreeDigitMethod(BasePredictionMethod):
    """
    Phương pháp 117 Đề 3 số
    Dự đoán từ giải 3.2 (số thứ 5 và bóng), giải 4.1 (tổng số thứ 2 và 3, lấy bóng), và giải 1 (càng đề)
    """
    def get_code(self) -> str:
        return "de117_3d"
    
    def get_name(self) -> str:
        return "117 Đề 3 số"
    
    def get_description(self) -> str:
        return "Dự đoán 3 số từ giải 3.2, 4.1 và giải 1 (càng đề)"
    
    def calculate(self, data: Dict[str, Any]) -> Dict[str, List[str]]:
        giai_3_2 = data.get('giai_3_2', '')
        giai_4_1 = data.get('giai_4_1', '')
        giai_1 = data.get('giai_1', '')
        
        if not giai_3_2 or not giai_4_1 or not giai_1:
            logger.warning(f"[{self.get_code()}] Thiếu dữ liệu đầu vào: giai_3_2={giai_3_2}, giai_4_1={giai_4_1}, giai_1={giai_1}")
            return {'three_digits_special': []}
        
        try:
            # Số thứ nhất từ giải 3.2: số thứ 5 và bóng
            # Ví dụ: 23496 -> số thứ 5 = 6, bóng là 1
            if len(giai_3_2) >= 5:
                digit_fifth = giai_3_2[4]
                first_nums = [digit_fifth, str(get_ball_number(int(digit_fifth)))]
            else:
                logger.warning(f"[{self.get_code()}] Giải 3.2 không đủ dài: {giai_3_2}")
                return {'three_digits_special': []}
                
            # Số thứ hai từ giải 4.1: tổng số thứ 2 và 3, lấy bóng
            # Ví dụ: 3241 -> 2+4=6, bóng là 1
            if len(giai_4_1) >= 3:
                sum_second_third = (int(giai_4_1[1]) + int(giai_4_1[2])) % 10
                second_nums = [str(sum_second_third), str(get_ball_number(sum_second_third))]
            else:
                logger.warning(f"[{self.get_code()}] Giải 4.1 không đủ dài: {giai_4_1}")
                return {'three_digits_special': []}
            
            # Tạo các cặp số 2 chữ số (bao gồm cả cặp đảo ngược)
            two_digits = []
            for first in first_nums:
                for second in second_nums:
                    two_digits.append(f"{first}{second}")
                    two_digits.append(f"{second}{first}")
            
            # Càng đề từ giải 1: số thứ 1 và bóng
            # Ví dụ: 92628 -> số thứ 1 = 9, bóng là 4
            if len(giai_1) >= 1:
                digit_first_cang = giai_1[0]
                cang_nums = [digit_first_cang, str(get_ball_number(int(digit_first_cang)))]
            else:
                logger.warning(f"[{self.get_code()}] Giải 1 không đủ dài: {giai_1}")
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
            logger.error(f"[{self.get_code()}] Lỗi tính 117 đề 3 số: {str(e)}")
            return {'three_digits_special': []}