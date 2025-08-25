from typing import Dict, List, Any
from .base import BasePredictionMethod
from .utils import get_ball_number
import logging

logger = logging.getLogger(__name__)

class De133TwoDigitMethod(BasePredictionMethod):
    """
    Phương pháp 133 Đề 2 số
    Dự đoán từ giải 7.3 (số thứ 2 và bóng), giải 7.1 (tổng số thứ 1 và 2, lấy bóng)
    """
    def get_code(self) -> str:
        return "de133_2d"
    
    def get_name(self) -> str:
        return "133 Đề 2 số"
    
    def get_description(self) -> str:
        return "Dự đoán 2 số từ giải 7.3 (số thứ 2) và giải 7.1 (tổng số thứ 1 và 2)"
    
    def calculate(self, data: Dict[str, Any]) -> Dict[str, List[str]]:
        giai_7_3 = data.get('giai_7_3', '')
        giai_7_1 = data.get('giai_7_1', '')
        
        if not giai_7_3 or not giai_7_1:
            logger.warning(f"[{self.get_code()}] Thiếu dữ liệu đầu vào: giai_7_3={giai_7_3}, giai_7_1={giai_7_1}")
            return {'two_digits_special': []}
        
        try:
            # Số thứ nhất từ giải 7.3: số thứ 2 và bóng
            # Ví dụ: 51 -> số thứ 2 = 1, bóng là 6
            if len(giai_7_3) >= 2:
                digit_second = giai_7_3[1]
                first_nums = [digit_second, str(get_ball_number(int(digit_second)))]
            else:
                logger.warning(f"[{self.get_code()}] Giải 7.3 không đủ dài: {giai_7_3}")
                return {'two_digits_special': []}
                
            # Số thứ hai từ giải 7.1: tổng số thứ 1 và số thứ 2, lấy số cuối và bóng
            # Ví dụ: 51 -> số thứ 1 = 5, số thứ 2 = 1 -> tổng = 6, bóng là 1
            if len(giai_7_1) >= 2:
                digit_first = int(giai_7_1[0])
                digit_second = int(giai_7_1[1])
                sum_digits_7_1 = (digit_first + digit_second) % 10  # Lấy số cuối của tổng
                second_nums = [str(sum_digits_7_1), str(get_ball_number(sum_digits_7_1))]
            else:
                logger.warning(f"[{self.get_code()}] Giải 7.1 không đủ dài: {giai_7_1}")
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
            logger.error(f"[{self.get_code()}] Lỗi tính 133 đề 2 số: {str(e)}")
            return {'two_digits_special': []}

class De133ThreeDigitMethod(BasePredictionMethod):
    """
    Phương pháp 133 Đề 3 số
    Dự đoán từ giải 7.3 (số thứ 2 và bóng), giải 7.1 (tổng số thứ 1 và 2, lấy bóng), và giải 3.2 (càng đề từ tổng số thứ 2, 3, 4)
    """
    def get_code(self) -> str:
        return "de133_3d"
    
    def get_name(self) -> str:
        return "133 Đề 3 số"
    
    def get_description(self) -> str:
        return "Dự đoán 3 số từ giải 7.3 (số thứ 2), giải 7.1 (tổng số thứ 1 và 2), và giải 3.2 (càng đề từ tổng số thứ 2, 3, 4)"
    
    def calculate(self, data: Dict[str, Any]) -> Dict[str, List[str]]:
        giai_7_3 = data.get('giai_7_3', '')
        giai_7_1 = data.get('giai_7_1', '')
        giai_3_2 = data.get('giai_3_2', '')
        
        if not giai_7_3 or not giai_7_1 or not giai_3_2:
            logger.warning(f"[{self.get_code()}] Thiếu dữ liệu đầu vào: giai_7_3={giai_7_3}, giai_7_1={giai_7_1}, giai_3_2={giai_3_2}")
            return {'three_digits_special': []}
        
        try:
            # Số thứ nhất từ giải 7.3: số thứ 2 và bóng
            # Ví dụ: 51 -> số thứ 2 = 1, bóng là 6
            if len(giai_7_3) >= 2:
                digit_second = giai_7_3[1]
                first_nums = [digit_second, str(get_ball_number(int(digit_second)))]
            else:
                logger.warning(f"[{self.get_code()}] Giải 7.3 không đủ dài: {giai_7_3}")
                return {'three_digits_special': []}
                
            # Số thứ hai từ giải 7.1: tổng số thứ 1 và số thứ 2, lấy số cuối và bóng
            # Ví dụ: 51 -> số thứ 1 = 5, số thứ 2 = 1 -> tổng = 6, bóng là 1
            if len(giai_7_1) >= 2:
                digit_first = int(giai_7_1[0])
                digit_second = int(giai_7_1[1])
                sum_digits_7_1 = (digit_first + digit_second) % 10  # Lấy số cuối của tổng
                second_nums = [str(sum_digits_7_1), str(get_ball_number(sum_digits_7_1))]
            else:
                logger.warning(f"[{self.get_code()}] Giải 7.1 không đủ dài: {giai_7_1}")
                return {'three_digits_special': []}
            
            # Tạo các cặp số 2 chữ số (bao gồm cả cặp đảo ngược)
            two_digits = []
            for first in first_nums:
                for second in second_nums:
                    two_digits.append(f"{first}{second}")
                    two_digits.append(f"{second}{first}")
            
            # Càng đề từ giải 3.2: tổng số thứ 2, số thứ 3, số thứ 4, lấy số cuối và bóng
            # Ví dụ: 25249 -> số thứ 2 = 5, số thứ 3 = 2, số thứ 4 = 4 -> tổng = 11 -> 1, bóng là 6
            if len(giai_3_2) >= 4:
                digit_second = int(giai_3_2[1])
                digit_third = int(giai_3_2[2])
                digit_fourth = int(giai_3_2[3])
                sum_digits_3_2 = (digit_second + digit_third + digit_fourth) % 10  # Lấy số cuối của tổng
                cang_nums = [str(sum_digits_3_2), str(get_ball_number(sum_digits_3_2))]
            else:
                logger.warning(f"[{self.get_code()}] Giải 3.2 không đủ dài: {giai_3_2}")
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
            logger.error(f"[{self.get_code()}] Lỗi tính 133 đề 3 số: {str(e)}")
            return {'three_digits_special': []}