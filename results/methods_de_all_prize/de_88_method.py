from typing import Dict, List, Any
from .base import BasePredictionMethod
from .utils import get_ball_number
import logging

logger = logging.getLogger(__name__)

class De88TwoDigitMethod(BasePredictionMethod):
    """
    Phương pháp 88 Đề 2 số
    Dự đoán từ giải 3.3 (tổng số thứ 2 và 3 và bóng) và giải 7.3 (số thứ 1 và bóng)
    """
    def get_code(self) -> str:
        return "de88_2d"
    
    def get_name(self) -> str:
        return "88 Đề 2 số"
    
    def get_description(self) -> str:
        return "Dự đoán 2 số từ giải 3.3 và giải 7.3"
    
    def calculate(self, data: Dict[str, Any]) -> Dict[str, List[str]]:
        giai_3_3 = data.get('giai_3_3', '')
        giai_7_3 = data.get('giai_7_3', '')
        
        if not giai_3_3 or not giai_7_3:
            logger.warning(f"[{self.get_code()}] Thiếu dữ liệu đầu vào: giai_3_3={giai_3_3}, giai_7_3={giai_7_3}")
            return {'two_digits_special': []}
        
        try:
            # Số thứ nhất từ giải 3.3: tổng số thứ 2 và số thứ 3, và bóng
            # Ví dụ: 23496 -> 3+4=7 và bóng là 2
            if len(giai_3_3) >= 3:
                sum_second_third = (int(giai_3_3[1]) + int(giai_3_3[2])) % 10
                first_nums = [str(sum_second_third), str(get_ball_number(sum_second_third))]
            else:
                logger.warning(f"[{self.get_code()}] Giải 3.3 không đủ dài: {giai_3_3}")
                return {'two_digits_special': []}
                
            # Số thứ 2 từ giải 7.3: số thứ 1 và bóng
            # Ví dụ: 13 -> số thứ 1 = 1 và bóng là 6
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
                    # Thêm cặp số thẳng
                    two_digits.add(f"{first}{second}")
                    # Thêm cặp số đảo ngược
                    two_digits.add(f"{second}{first}")
            
            logger.info(f"[{self.get_code()}] Kết quả: {sorted(list(two_digits))}")
            return {
                'two_digits_special': sorted(list(two_digits))
            }
        except (ValueError, IndexError, TypeError) as e:
            logger.error(f"[{self.get_code()}] Lỗi tính 88 đề 2 số: {str(e)}")
            return {'two_digits_special': []}


class De88ThreeDigitMethod(BasePredictionMethod):
    """
    Phương pháp 88 Đề 3 số
    Dự đoán từ giải 3.3, 7.3 và giải 5.1 (càng đề)
    """
    def get_code(self) -> str:
        return "de88_3d"
    
    def get_name(self) -> str:
        return "88 Đề 3 số"
    
    def get_description(self) -> str:
        return "Dự đoán 3 số từ giải 3.3, 7.3 và giải 5.1 (càng đề)"
    
    def calculate(self, data: Dict[str, Any]) -> Dict[str, List[str]]:
        giai_3_3 = data.get('giai_3_3', '')
        giai_7_3 = data.get('giai_7_3', '')
        giai_5_1 = data.get('giai_5_1', '')
        
        if not giai_3_3 or not giai_7_3 or not giai_5_1:
            logger.warning(f"[{self.get_code()}] Thiếu dữ liệu đầu vào: giai_3_3={giai_3_3}, giai_7_3={giai_7_3}, giai_5_1={giai_5_1}")
            return {'three_digits_special': []}
        
        try:
            # Tính các cặp số 2 chữ số từ giải 3.3 và 7.3
            if len(giai_3_3) >= 3:
                sum_second_third = (int(giai_3_3[1]) + int(giai_3_3[2])) % 10
                first_nums = [str(sum_second_third), str(get_ball_number(sum_second_third))]
            else:
                logger.warning(f"[{self.get_code()}] Giải 3.3 không đủ dài: {giai_3_3}")
                return {'three_digits_special': []}
                
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
            logger.error(f"[{self.get_code()}] Lỗi tính 88 đề 3 số: {str(e)}")
            return {'three_digits_special': []}