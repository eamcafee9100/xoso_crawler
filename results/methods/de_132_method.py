from typing import Dict, List, Any
from .base import BasePredictionMethod
from .utils import get_ball_number
import logging

logger = logging.getLogger(__name__)

class De132TwoDigitMethod(BasePredictionMethod):
    """
    Phương pháp 132 Đề 2 số
    Dự đoán từ giải đặc biệt (số thứ 2 và bóng) và giải 4.1 (số thứ 4 và bóng)
    """
    def get_code(self) -> str:
        return "de132_2d"
    
    def get_name(self) -> str:
        return "132 Đề 2 số"
    
    def get_description(self) -> str:
        return "Dự đoán 2 số từ giải đặc biệt và giải 4.1"
    
    def calculate(self, data: Dict[str, Any]) -> Dict[str, List[str]]:
        giai_dac_biet = data.get('giai_dac_biet', '')
        giai_4_1 = data.get('giai_4_1', '')
        
        if not giai_dac_biet or not giai_4_1:
            logger.warning(f"[{self.get_code()}] Thiếu dữ liệu đầu vào: giai_dac_biet={giai_dac_biet}, giai_4_1={giai_4_1}")
            return {'two_digits_special': []}
        
        try:
            # Số thứ nhất từ giải đặc biệt: số thứ 2 và bóng
            # Ví dụ: 24249 -> số thứ 2 = 4, bóng là 9
            if len(giai_dac_biet) >= 2:
                digit_second = giai_dac_biet[1]
                first_nums = [digit_second, str(get_ball_number(int(digit_second)))]
            else:
                logger.warning(f"[{self.get_code()}] Giải đặc biệt không đủ dài: {giai_dac_biet}")
                return {'two_digits_special': []}
                
            # Số thứ hai từ giải 4.1: số thứ 4 và bóng
            # Ví dụ: 1253 -> số thứ 4 = 3, bóng là 8
            if len(giai_4_1) >= 4:
                digit_fourth = giai_4_1[3]
                second_nums = [digit_fourth, str(get_ball_number(int(digit_fourth)))]
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
            logger.error(f"[{self.get_code()}] Lỗi tính 132 đề 2 số: {str(e)}")
            return {'two_digits_special': []}

class De132ThreeDigitMethod(BasePredictionMethod):
    """
    Phương pháp 132 Đề 3 số
    Dự đoán từ giải đặc biệt (số thứ 2 và bóng), giải 4.1 (số thứ 4 và bóng), và giải 7.1 (càng đề từ tổng số thứ 1 và 2)
    """
    def get_code(self) -> str:
        return "de132_3d"
    
    def get_name(self) -> str:
        return "132 Đề 3 số"
    
    def get_description(self) -> str:
        return "Dự đoán 3 số từ giải đặc biệt, 4.1 và giải 7.1 (càng đề)"
    
    def calculate(self, data: Dict[str, Any]) -> Dict[str, List[str]]:
        giai_dac_biet = data.get('giai_dac_biet', '')
        giai_4_1 = data.get('giai_4_1', '')
        giai_7_1 = data.get('giai_7_1', '')
        
        if not giai_dac_biet or not giai_4_1 or not giai_7_1:
            logger.warning(f"[{self.get_code()}] Thiếu dữ liệu đầu vào: giai_dac_biet={giai_dac_biet}, giai_4_1={giai_4_1}, giai_7_1={giai_7_1}")
            return {'three_digits_special': []}
        
        try:
            # Số thứ nhất từ giải đặc biệt: số thứ 2 và bóng
            # Ví dụ: 24249 -> số thứ 2 = 4, bóng là 9
            if len(giai_dac_biet) >= 2:
                digit_second = giai_dac_biet[1]
                first_nums = [digit_second, str(get_ball_number(int(digit_second)))]
            else:
                logger.warning(f"[{self.get_code()}] Giải đặc biệt không đủ dài: {giai_dac_biet}")
                return {'three_digits_special': []}
                
            # Số thứ hai từ giải 4.1: số thứ 4 và bóng
            # Ví dụ: 1253 -> số thứ 4 = 3, bóng là 8
            if len(giai_4_1) >= 4:
                digit_fourth = giai_4_1[3]
                second_nums = [digit_fourth, str(get_ball_number(int(digit_fourth)))]
            else:
                logger.warning(f"[{self.get_code()}] Giải 4.1 không đủ dài: {giai_4_1}")
                return {'three_digits_special': []}
            
            # Tạo các cặp số 2 chữ số (bao gồm cả cặp đảo ngược)
            two_digits = []
            for first in first_nums:
                for second in second_nums:
                    two_digits.append(f"{first}{second}")
                    two_digits.append(f"{second}{first}")
            
            # Càng đề từ giải 7.1: tổng số thứ 1 và số thứ 2, lấy số cuối và bóng
            # Ví dụ: 31 -> số thứ 1 = 3, số thứ 2 = 1 -> tổng = 4, bóng là 9
            if len(giai_7_1) >= 2:
                digit_first_cang = int(giai_7_1[0])
                digit_second_cang = int(giai_7_1[1])
                sum_digits = (digit_first_cang + digit_second_cang) % 10  # Lấy số cuối của tổng
                cang_nums = [str(sum_digits), str(get_ball_number(sum_digits))]
            else:
                logger.warning(f"[{self.get_code()}] Giải 7.1 không đủ dài: {giai_7_1}")
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
            logger.error(f"[{self.get_code()}] Lỗi tính 132 đề 3 số: {str(e)}")
            return {'three_digits_special': []}