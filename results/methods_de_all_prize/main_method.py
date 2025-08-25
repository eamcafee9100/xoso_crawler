from typing import Dict, List, Any
from .base import BasePredictionMethod
from .utils import process_prize, get_ball_number
import logging

logger = logging.getLogger(__name__)

class MainDanDeMethod(BasePredictionMethod):
    """
    Phương pháp dàn đề chính từ giải 2 và giải 3
    """
    def get_code(self) -> str:
        return "main_dande"
    
    def get_name(self) -> str:
        return "Dàn đề chính (34)"
    
    def get_description(self) -> str:
        return "Phương pháp tạo dàn đề từ giải 3 (đầu) và giải 2 (đuôi)"
    
    def calculate(self, data: Dict[str, Any]) -> Dict[str, List[str]]:
        try:
            # Xử lý giải 2 theo cấu trúc mới
            giai_2_1 = data.get('giai_2_1', '')
            if not giai_2_1:
                logger.warning(f"[{self.get_code()}] Thiếu dữ liệu giải 2.1")
                return {'two_digits_special': []}
            
            # Xử lý giải 3 theo cấu trúc mới
            giai_3_2 = data.get('giai_3_2', '')  # Sử dụng giải 3.2 thay vì 3.1
            if not giai_3_2:
                logger.warning(f"[{self.get_code()}] Thiếu dữ liệu giải 3.2")
                return {'two_digits_special': []}
            
            # Xử lý thành bóng
            processed_prize2 = process_prize(giai_2_1)
            processed_prize3 = process_prize(giai_3_2)
            
            # Tạo bộ số dàn đề
            numbers = []
            if processed_prize3 and processed_prize2:
                for digit1 in processed_prize3:
                    for digit2 in processed_prize2:
                        numbers.append(f"{digit1}{digit2}")
            
            logger.info(f"[{self.get_code()}] Kết quả: {sorted(list(set(numbers)))}")
            return {
                'two_digits_special': sorted(list(set(numbers)))
            }
        except Exception as e:
            logger.error(f"[{self.get_code()}] Lỗi: {str(e)}")
            return {'two_digits_special': []}
        
class MainDande3DigitMethod(BasePredictionMethod):
    """
    Phương pháp dàn đề 3 số dựa trên giải 2, giải 3 và giải 5.5
    """
    def get_code(self) -> str:
        return "main_dande_3d"
    
    def get_name(self) -> str:
        return "Dàn đề chính 3 số"
    
    def get_description(self) -> str:
        return "Phương pháp tạo dàn đề 3 số từ giải 3 (đầu), giải 2 (đuôi) và giải 5.5 (càng)"
    
    def calculate(self, data: Dict[str, Any]) -> Dict[str, List[str]]:
        try:
            # Xử lý giải 2 theo cấu trúc mới
            giai_2_1 = data.get('giai_2_1', '')
            if not giai_2_1:
                logger.warning(f"[{self.get_code()}] Thiếu dữ liệu giải 2.1")
                return {'three_digits_special': []}
            
            # Xử lý giải 3 theo cấu trúc mới
            giai_3_2 = data.get('giai_3_2', '')  # Sử dụng giải 3.2 thay vì 3.1
            if not giai_3_2:
                logger.warning(f"[{self.get_code()}] Thiếu dữ liệu giải 3.2")
                return {'three_digits_special': []}
            
            # Lấy số càng từ giải 5.5
            giai_5_5 = data.get('giai_5_5', '')
            if not giai_5_5 or len(giai_5_5) < 1:
                logger.warning(f"[{self.get_code()}] Thiếu dữ liệu giải 5.5 hoặc dữ liệu không đúng: {giai_5_5}")
                return {'three_digits_special': []}
                
            # Lấy số đầu tiên của giải 5.5 và bóng của nó
            cang_digit = giai_5_5[0]
            cang_bong = str(get_ball_number(int(cang_digit)))
            cang_digits = [cang_digit, cang_bong]
            
            # Xử lý thành bóng
            processed_prize2 = process_prize(giai_2_1)
            processed_prize3 = process_prize(giai_3_2)
            
            # Tạo bộ số dàn đề 2 chữ số
            two_digits = []
            if processed_prize3 and processed_prize2:
                for digit1 in processed_prize3:
                    for digit2 in processed_prize2:
                        two_digits.append(f"{digit1}{digit2}")
            
            # Tạo bộ số dàn đề 3 chữ số bằng cách ghép số càng với 2 số đã tạo
            three_digits = []
            for cang in cang_digits:
                for two_digit in two_digits:
                    three_digits.append(f"{cang}{two_digit}")
            
            logger.info(f"[{self.get_code()}] Kết quả: {sorted(list(set(three_digits)))}")
            return {
                'three_digits_special': sorted(list(set(three_digits)))
            }
        except Exception as e:
            logger.error(f"[{self.get_code()}] Lỗi: {str(e)}")
            return {'three_digits_special': []}