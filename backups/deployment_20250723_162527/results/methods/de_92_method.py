from typing import Dict, List, Any
from .base import BasePredictionMethod
from .utils import get_ball_number
import logging

logger = logging.getLogger(__name__)

class De92TwoDigitMethod(BasePredictionMethod):
    """
    Phương pháp 92 Đề 2 số
    Dự đoán từ giải 3.5 (số thứ 3 và bóng) và giải 5.6 (số thứ 4 và bóng)
    """
    def get_code(self) -> str:
        return "de92_2d"
    
    def get_name(self) -> str:
        return "92 Đề 2 số"
    
    def get_description(self) -> str:
        return "Dự đoán 2 số từ giải 3.5 và giải 5.6"
    
    def calculate(self, data: Dict[str, Any]) -> Dict[str, List[str]]:
        giai_3_5 = data.get('giai_3_5', '')
        giai_5_6 = data.get('giai_5_6', '')
        
        if not giai_3_5 or not giai_5_6:
            logger.warning(f"[{self.get_code()}] Thiếu dữ liệu đầu vào: giai_3_5={giai_3_5}, giai_5_6={giai_5_6}")
            return {'two_digits_special': []}
        
        try:
            # Số thứ nhất từ giải 3.5: số thứ 3 và bóng
            # Ví dụ: 23496 -> số thứ 3 = 4 và bóng là 9
            if len(giai_3_5) >= 3:
                digit_third = giai_3_5[2]
                first_nums = [digit_third, str(get_ball_number(int(digit_third)))]
            else:
                logger.warning(f"[{self.get_code()}] Giải 3.5 không đủ dài: {giai_3_5}")
                return {'two_digits_special': []}
                
            # Số thứ 2 từ giải 5.6: số thứ 4 và bóng
            # Ví dụ: 1334 -> số thứ 4 = 4 và bóng là 9
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
                    # Thêm cặp số thẳng
                    two_digits.add(f"{first}{second}")
                    # Thêm cặp số đảo ngược
                    two_digits.add(f"{second}{first}")
            
            logger.info(f"[{self.get_code()}] Kết quả: {sorted(list(two_digits))}")
            return {
                'two_digits_special': sorted(list(two_digits))
            }
        except (ValueError, IndexError, TypeError) as e:
            logger.error(f"[{self.get_code()}] Lỗi tính 92 đề 2 số: {str(e)}")
            return {'two_digits_special': []}


class De92ThreeDigitMethod(BasePredictionMethod):
    """
    Phương pháp 92 Đề 3 số
    Dự đoán từ giải 3.5, 5.6 và giải 5.1 (càng đề)
    """
    def get_code(self) -> str:
        return "de92_3d"
    
    def get_name(self) -> str:
        return "92 Đề 3 số"
    
    def get_description(self) -> str:
        return "Dự đoán 3 số từ giải 3.5, 5.6 và giải 5.1 (càng đề)"
    
    def calculate(self, data: Dict[str, Any]) -> Dict[str, List[str]]:
        giai_3_5 = data.get('giai_3_5', '')
        giai_5_6 = data.get('giai_5_6', '')
        giai_5_1 = data.get('giai_5_1', '')
        
        if not giai_3_5 or not giai_5_6 or not giai_5_1:
            logger.warning(f"[{self.get_code()}] Thiếu dữ liệu đầu vào: giai_3_5={giai_3_5}, giai_5_6={giai_5_6}, giai_5_1={giai_5_1}")
            return {'three_digits_special': []}
        
        try:
            # Tính các cặp số 2 chữ số từ giải 3.5 và 5.6
            if len(giai_3_5) >= 3:
                digit_third = giai_3_5[2]
                first_nums = [digit_third, str(get_ball_number(int(digit_third)))]
            else:
                logger.warning(f"[{self.get_code()}] Giải 3.5 không đủ dài: {giai_3_5}")
                return {'three_digits_special': []}
                
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
                    # Thêm cặp số thẳng
                    two_digits.append(f"{first}{second}")
                    # Thêm cặp số đảo ngược
                    two_digits.append(f"{second}{first}")
            
            # Càng đề từ giải 5.1: tổng số thứ 3 và số thứ 4, và bóng
            if len(giai_5_1) >= 4:
                sum_third_fourth = (int(giai_5_1[2]) + int(giai_5_1[3])) % 10
                cang_de = str(sum_third_fourth)
                cang_de_bong = str(get_ball_number(sum_third_fourth))
                cang_nums = [cang_de, cang_de_bong]
            else:
                logger.warning(f"[{self.get_code()}] Giải 5.1 không đủ dài: {giai_5_1}")
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
            logger.error(f"[{self.get_code()}] Lỗi tính 92 đề 3 số: {str(e)}")
            return {'three_digits_special': []}