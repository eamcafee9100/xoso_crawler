from typing import Dict, List, Any
from .base import BasePredictionMethod
from .utils import get_ball_number
import logging

logger = logging.getLogger(__name__)

class De78TwoDigitMethod(BasePredictionMethod):
    """
    Phương pháp 78 Đề 2 số
    Dự đoán từ giải 7.2 (số thứ 2 và bóng) và giải 7.4 (tổng số thứ 1 và 2 và bóng)
    """
    def get_code(self) -> str:
        return "de78_2d"
    
    def get_name(self) -> str:
        return "78 Đề 2 số"
    
    def get_description(self) -> str:
        return "Dự đoán 2 số từ giải 7.2 và giải 7.4"
    
    def calculate(self, data: Dict[str, Any]) -> Dict[str, List[str]]:
        giai_7_2 = data.get('giai_7_2', '')
        giai_7_4 = data.get('giai_7_4', '')
        
        if not giai_7_2 or not giai_7_4:
            logger.warning(f"[{self.get_code()}] Thiếu dữ liệu đầu vào: giai_7_2={giai_7_2}, giai_7_4={giai_7_4}")
            return {'two_digits_special': []}
        
        try:
            # Số thứ nhất từ giải 7.2: số thứ 2 và bóng
            # Ví dụ: 96 -> số thứ 2 = 6 và bóng là 1
            if len(giai_7_2) >= 2:
                digit_second = giai_7_2[1]
                first_nums = [digit_second, str(get_ball_number(int(digit_second)))]
            else:
                logger.warning(f"[{self.get_code()}] Giải 7.2 không đủ dài: {giai_7_2}")
                return {'two_digits_special': []}
                
            # Số thứ 2 từ giải 7.4: tổng số thứ 1 và số thứ 2 và bóng
            # Ví dụ: 96 -> 9+6=15 -> 15%10=5 và bóng là 0
            if len(giai_7_4) >= 2:
                sum_first_second = (int(giai_7_4[0]) + int(giai_7_4[1])) % 10
                second_nums = [str(sum_first_second), str(get_ball_number(sum_first_second))]
            else:
                logger.warning(f"[{self.get_code()}] Giải 7.4 không đủ dài: {giai_7_4}")
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
            logger.error(f"[{self.get_code()}] Lỗi tính 78 đề 2 số: {str(e)}")
            return {'two_digits_special': []}


class De78ThreeDigitMethod(BasePredictionMethod):
    """
    Phương pháp 78 Đề 3 số
    Dự đoán từ giải 7.2, 7.4 và giải 1 (càng đề)
    """
    def get_code(self) -> str:
        return "de78_3d"
    
    def get_name(self) -> str:
        return "78 Đề 3 số"
    
    def get_description(self) -> str:
        return "Dự đoán 3 số từ giải 7.2, 7.4 và giải 1 (càng đề)"
    
    def calculate(self, data: Dict[str, Any]) -> Dict[str, List[str]]:
        giai_7_2 = data.get('giai_7_2', '')
        giai_7_4 = data.get('giai_7_4', '')
        giai_1 = data.get('giai_1', '')
        
        if not giai_7_2 or not giai_7_4 or not giai_1:
            logger.warning(f"[{self.get_code()}] Thiếu dữ liệu đầu vào: giai_7_2={giai_7_2}, giai_7_4={giai_7_4}, giai_1={giai_1}")
            return {'three_digits_special': []}
        
        try:
            # Tính các cặp số 2 chữ số từ giải 7.2 và 7.4
            if len(giai_7_2) >= 2:
                digit_second = giai_7_2[1]
                first_nums = [digit_second, str(get_ball_number(int(digit_second)))]
            else:
                logger.warning(f"[{self.get_code()}] Giải 7.2 không đủ dài: {giai_7_2}")
                return {'three_digits_special': []}
                
            if len(giai_7_4) >= 2:
                sum_first_second = (int(giai_7_4[0]) + int(giai_7_4[1])) % 10
                second_nums = [str(sum_first_second), str(get_ball_number(sum_first_second))]
            else:
                logger.warning(f"[{self.get_code()}] Giải 7.4 không đủ dài: {giai_7_4}")
                return {'three_digits_special': []}
            
            # Tạo các cặp số 2 chữ số (bao gồm cả cặp đảo ngược)
            two_digits = []
            for first in first_nums:
                for second in second_nums:
                    # Thêm cặp số thẳng
                    two_digits.append(f"{first}{second}")
                    # Thêm cặp số đảo ngược
                    two_digits.append(f"{second}{first}")
            
            # Càng đề từ giải 1: số thứ 4
            if len(giai_1) >= 4:
                cang_de = giai_1[3]  # Lấy số thứ 4, ví dụ: 16728 -> 2
                cang_de_bong = str(get_ball_number(int(cang_de)))
                cang_nums = [cang_de, cang_de_bong]
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
            logger.error(f"[{self.get_code()}] Lỗi tính 78 đề 3 số: {str(e)}")
            return {'three_digits_special': []}