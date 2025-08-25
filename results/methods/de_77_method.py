from typing import Dict, List, Any
from .base import BasePredictionMethod
from .utils import get_ball_number
import logging

logger = logging.getLogger(__name__)

class De77TwoDigitMethod(BasePredictionMethod):
    """
    Phương pháp 77 Đề 2 số
    Dự đoán từ giải 1 (số thứ 3 và bóng) và giải 7.2 (số thứ 2 và bóng)
    """
    def get_code(self) -> str:
        return "de77_2d"
    
    def get_name(self) -> str:
        return "77 Đề 2 số"
    
    def get_description(self) -> str:
        return "Dự đoán 2 số từ giải 1 và giải 7.2"
    
    def calculate(self, data: Dict[str, Any]) -> Dict[str, List[str]]:
        giai_1 = data.get('giai_1', '')
        giai_7_2 = data.get('giai_7_2', '')
        
        if not giai_1 or not giai_7_2:
            logger.warning(f"[{self.get_code()}] Thiếu dữ liệu đầu vào: giai_1={giai_1}, giai_7_2={giai_7_2}")
            return {'two_digits_special': []}
        
        try:
            # Số thứ nhất từ giải 1: số thứ 3 và bóng
            # Ví dụ: 18519 -> số thứ 3 = 5 và bóng là 0
            if len(giai_1) >= 3:
                digit_third = giai_1[2]
                first_nums = [digit_third, str(get_ball_number(int(digit_third)))]
            else:
                logger.warning(f"[{self.get_code()}] Giải 1 không đủ dài: {giai_1}")
                return {'two_digits_special': []}
                
            # Số thứ 2 từ giải 7.2: số thứ 2 và bóng
            # Ví dụ: 96 -> số thứ 2 = 6 và bóng là 1
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
                    # Thêm cặp số thẳng
                    two_digits.add(f"{first}{second}")
                    # Thêm cặp số đảo ngược
                    two_digits.add(f"{second}{first}")
            
            logger.info(f"[{self.get_code()}] Kết quả: {sorted(list(two_digits))}")
            return {
                'two_digits_special': sorted(list(two_digits))
            }
        except (ValueError, IndexError, TypeError) as e:
            logger.error(f"[{self.get_code()}] Lỗi tính 77 đề 2 số: {str(e)}")
            return {'two_digits_special': []}


class De77ThreeDigitMethod(BasePredictionMethod):
    """
    Phương pháp 77 Đề 3 số
    Dự đoán từ giải 1, 7.2 và giải 7.4 (càng đề)
    """
    def get_code(self) -> str:
        return "de77_3d"
    
    def get_name(self) -> str:
        return "77 Đề 3 số"
    
    def get_description(self) -> str:
        return "Dự đoán 3 số từ giải 1, 7.2 và giải 7.4 (càng đề)"
    
    def calculate(self, data: Dict[str, Any]) -> Dict[str, List[str]]:
        giai_1 = data.get('giai_1', '')
        giai_7_2 = data.get('giai_7_2', '')
        giai_7_4 = data.get('giai_7_4', '')
        
        if not giai_1 or not giai_7_2 or not giai_7_4:
            logger.warning(f"[{self.get_code()}] Thiếu dữ liệu đầu vào: giai_1={giai_1}, giai_7_2={giai_7_2}, giai_7_4={giai_7_4}")
            return {'three_digits_special': []}
        
        try:
            # Tính các cặp số 2 chữ số từ giải 1 và 7.2
            if len(giai_1) >= 3:
                digit_third = giai_1[2]
                first_nums = [digit_third, str(get_ball_number(int(digit_third)))]
            else:
                logger.warning(f"[{self.get_code()}] Giải 1 không đủ dài: {giai_1}")
                return {'three_digits_special': []}
                
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
                    # Thêm cặp số thẳng
                    two_digits.append(f"{first}{second}")
                    # Thêm cặp số đảo ngược
                    two_digits.append(f"{second}{first}")
            
            # Càng đề từ giải 7.4: số thứ 1
            if len(giai_7_4) >= 1:
                cang_de = giai_7_4[0]  # Lấy số thứ 1, ví dụ: 18 -> 1
                cang_de_bong = str(get_ball_number(int(cang_de)))
                cang_nums = [cang_de, cang_de_bong]
            else:
                logger.warning(f"[{self.get_code()}] Giải 7.4 không đủ dài: {giai_7_4}")
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
            logger.error(f"[{self.get_code()}] Lỗi tính 77 đề 3 số: {str(e)}")
            return {'three_digits_special': []}