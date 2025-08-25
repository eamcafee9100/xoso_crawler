from typing import Dict, List, Any
from .base import BasePredictionMethod
from .utils import get_ball_number
import logging

logger = logging.getLogger(__name__)

class De113TwoDigitMethod(BasePredictionMethod):
    """
    Phương pháp 113 Đề 2 số
    Dự đoán từ giải 2.1 (tổng số thứ 1 và 2, lấy bóng) và giải 5.5 (tổng số thứ 3 và 4, lấy bóng)
    """
    def get_code(self) -> str:
        return "de113_2d"
    
    def get_name(self) -> str:
        return "113 Đề 2 số"
    
    def get_description(self) -> str:
        return "Dự đoán 2 số từ giải 2.1 (tổng số thứ 1 và 2) và giải 5.5 (tổng số thứ 3 và 4)"
    
    def calculate(self, data: Dict[str, Any]) -> Dict[str, List[str]]:
        giai_2_1 = data.get('giai_2_1', '')
        giai_5_5 = data.get('giai_5_5', '')
        
        if not giai_2_1 or not giai_5_5:
            logger.warning(f"[{self.get_code()}] Thiếu dữ liệu đầu vào: giai_2_1={giai_2_1}, giai_5_5={giai_5_5}")
            return {'two_digits_special': []}
        
        try:
            # Số thứ nhất từ giải 2.1: tổng số thứ 1 và số thứ 2, lấy số cuối và bóng
            # Ví dụ: 25249 -> số thứ 1 = 2, số thứ 2 = 5 -> tổng = 7, bóng là 2
            if len(giai_2_1) >= 2:
                digit_first = int(giai_2_1[0])
                digit_second = int(giai_2_1[1])
                sum_digits_2_1 = (digit_first + digit_second) % 10  # Lấy số cuối của tổng
                first_nums = [str(sum_digits_2_1), str(get_ball_number(sum_digits_2_1))]
            else:
                logger.warning(f"[{self.get_code()}] Giải 2.1 không đủ dài: {giai_2_1}")
                return {'two_digits_special': []}
                
            # Số thứ hai từ giải 5.5: tổng số thứ 3 và số thứ 4, lấy số cuối và bóng
            # Ví dụ: 5123 -> số thứ 3 = 2, số thứ 4 = 3 -> tổng = 5, bóng là 0
            if len(giai_5_5) >= 4:
                digit_third = int(giai_5_5[2])
                digit_fourth = int(giai_5_5[3])
                sum_digits_5_5 = (digit_third + digit_fourth) % 10  # Lấy số cuối của tổng
                second_nums = [str(sum_digits_5_5), str(get_ball_number(sum_digits_5_5))]
            else:
                logger.warning(f"[{self.get_code()}] Giải 5.5 không đủ dài: {giai_5_5}")
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
            logger.error(f"[{self.get_code()}] Lỗi tính 113 đề 2 số: {str(e)}")
            return {'two_digits_special': []}

class De113ThreeDigitMethod(BasePredictionMethod):
    """
    Phương pháp 113 Đề 3 số
    Dự đoán từ giải 2.1 (tổng số thứ 1 và 2, lấy bóng), giải 5.5 (tổng số thứ 3 và 4, lấy bóng), và giải 5.5 (càng đề từ số thứ 1)
    """
    def get_code(self) -> str:
        return "de113_3d"
    
    def get_name(self) -> str:
        return "113 Đề 3 số"
    
    def get_description(self) -> str:
        return "Dự đoán 3 số từ giải 2.1 (tổng số thứ 1 và 2), giải 5.5 (tổng số thứ 3 và 4, và càng đề từ số thứ 1)"
    
    def calculate(self, data: Dict[str, Any]) -> Dict[str, List[str]]:
        giai_2_1 = data.get('giai_2_1', '')
        giai_5_5 = data.get('giai_5_5', '')
        
        if not giai_2_1 or not giai_5_5:
            logger.warning(f"[{self.get_code()}] Thiếu dữ liệu đầu vào: giai_2_1={giai_2_1}, giai_5_5={giai_5_5}")
            return {'three_digits_special': []}
        
        try:
            # Số thứ nhất từ giải 2.1: tổng số thứ 1 và số thứ 2, lấy số cuối và bóng
            # Ví dụ: 25249 -> số thứ 1 = 2, số thứ 2 = 5 -> tổng = 7, bóng là 2
            if len(giai_2_1) >= 2:
                digit_first = int(giai_2_1[0])
                digit_second = int(giai_2_1[1])
                sum_digits_2_1 = (digit_first + digit_second) % 10  # Lấy số cuối của tổng
                first_nums = [str(sum_digits_2_1), str(get_ball_number(sum_digits_2_1))]
            else:
                logger.warning(f"[{self.get_code()}] Giải 2.1 không đủ dài: {giai_2_1}")
                return {'three_digits_special': []}
                
            # Số thứ hai từ giải 5.5: tổng số thứ 3 và số thứ 4, lấy số cuối và bóng
            # Ví dụ: 5123 -> số thứ 3 = 2, số thứ 4 = 3 -> tổng = 5, bóng là 0
            if len(giai_5_5) >= 4:
                digit_third = int(giai_5_5[2])
                digit_fourth = int(giai_5_5[3])
                sum_digits_5_5 = (digit_third + digit_fourth) % 10  # Lấy số cuối của tổng
                second_nums = [str(sum_digits_5_5), str(get_ball_number(sum_digits_5_5))]
            else:
                logger.warning(f"[{self.get_code()}] Giải 5.5 không đủ dài: {giai_5_5}")
                return {'three_digits_special': []}
            
            # Tạo các cặp số 2 chữ số (bao gồm cả cặp đảo ngược)
            two_digits = []
            for first in first_nums:
                for second in second_nums:
                    two_digits.append(f"{first}{second}")
                    two_digits.append(f"{second}{first}")
            
            # Càng đề từ giải 5.5: số thứ 1 và bóng
            # Ví dụ: 4674 -> số thứ 1 = 4, bóng là 9
            if len(giai_5_5) >= 1:
                digit_first_cang = giai_5_5[0]
                cang_nums = [digit_first_cang, str(get_ball_number(int(digit_first_cang)))]
            else:
                logger.warning(f"[{self.get_code()}] Giải 5.5 không đủ dài: {giai_5_5}")
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
            logger.error(f"[{self.get_code()}] Lỗi tính 113 đề 3 số: {str(e)}")
            return {'three_digits_special': []}