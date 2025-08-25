from typing import Dict, List, Any
from .base import BasePredictionMethod
from .utils import get_ball_number
import logging

logger = logging.getLogger(__name__)

class De134TwoDigitMethod(BasePredictionMethod):
    """
    Phương pháp 134 Đề 2 số
    Dự đoán từ giải 2.1 (số thứ 4 và bóng) và giải 4.3 (số thứ 2 và bóng)
    """
    def get_code(self) -> str:
        return "de134_2d"
    
    def get_name(self) -> str:
        return "134 Đề 2 số"
    
    def get_description(self) -> str:
        return "Dự đoán 2 số từ giải 2.1 và giải 4.3"
    
    def calculate(self, data: Dict[str, Any]) -> Dict[str, List[str]]:
        giai_2_1 = data.get('giai_2_1', '')
        giai_4_3 = data.get('giai_4_3', '')
        
        if not giai_2_1 or not giai_4_3:
            logger.warning(f"[{self.get_code()}] Thiếu dữ liệu đầu vào: giai_2_1={giai_2_1}, giai_4_3={giai_4_3}")
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
                
            # Số thứ hai từ giải 4.3: số thứ 2 và bóng
            # Ví dụ: 1253 -> số thứ 2 = 2, bóng là 7
            if len(giai_4_3) >= 2:
                digit_second = giai_4_3[1]
                second_nums = [digit_second, str(get_ball_number(int(digit_second)))]
            else:
                logger.warning(f"[{self.get_code()}] Giải 4.3 không đủ dài: {giai_4_3}")
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
            logger.error(f"[{self.get_code()}] Lỗi tính 134 đề 2 số: {str(e)}")
            return {'two_digits_special': []}

class De134ThreeDigitMethod(BasePredictionMethod):
    """
    Phương pháp 134 Đề 3 số
    Dự đoán từ giải 2.1 (số thứ 4 và bóng), giải 4.3 (số thứ 2 và bóng), và giải 6.3 (càng đề từ tổng số thứ 2 và 3)
    """
    def get_code(self) -> str:
        return "de134_3d"
    
    def get_name(self) -> str:
        return "134 Đề 3 số"
    
    def get_description(self) -> str:
        return "Dự đoán 3 số từ giải 2.1, 4.3 và giải 6.3 (càng đề)"
    
    def calculate(self, data: Dict[str, Any]) -> Dict[str, List[str]]:
        giai_2_1 = data.get('giai_2_1', '')
        giai_4_3 = data.get('giai_4_3', '')
        giai_6_3 = data.get('giai_6_3', '')
        
        if not giai_2_1 or not giai_4_3 or not giai_6_3:
            logger.warning(f"[{self.get_code()}] Thiếu dữ liệu đầu vào: giai_2_1={giai_2_1}, giai_4_3={giai_4_3}, giai_6_3={giai_6_3}")
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
                
            # Số thứ hai từ giải 4.3: số thứ 2 và bóng
            # Ví dụ: 1253 -> số thứ 2 = 2, bóng là 7
            if len(giai_4_3) >= 2:
                digit_second = giai_4_3[1]
                second_nums = [digit_second, str(get_ball_number(int(digit_second)))]
            else:
                logger.warning(f"[{self.get_code()}] Giải 4.3 không đủ dài: {giai_4_3}")
                return {'three_digits_special': []}
            
            # Tạo các cặp số 2 chữ số (bao gồm cả cặp đảo ngược)
            two_digits = []
            for first in first_nums:
                for second in second_nums:
                    two_digits.append(f"{first}{second}")
                    two_digits.append(f"{second}{first}")
            
            # Càng đề từ giải 6.3: tổng số thứ 2 và số thứ 3, lấy số cuối và bóng
            # Ví dụ: 341 -> số thứ 2 = 4, số thứ 3 = 1 -> tổng = 5, bóng là 0
            if len(giai_6_3) >= 3:
                digit_second_cang = int(giai_6_3[1])
                digit_third_cang = int(giai_6_3[2])
                sum_digits = (digit_second_cang + digit_third_cang) % 10  # Lấy số cuối của tổng
                cang_nums = [str(sum_digits), str(get_ball_number(sum_digits))]
            else:
                logger.warning(f"[{self.get_code()}] Giải 6.3 không đủ dài: {giai_6_3}")
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
            logger.error(f"[{self.get_code()}] Lỗi tính 134 đề 3 số: {str(e)}")
            return {'three_digits_special': []}