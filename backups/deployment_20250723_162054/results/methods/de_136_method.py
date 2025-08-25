from typing import Dict, List, Any
from .base import BasePredictionMethod
from .utils import get_ball_number
import logging

logger = logging.getLogger(__name__)

class De136TwoDigitMethod(BasePredictionMethod):
    """
    Phương pháp 136 Đề 2 số
    Dự đoán từ giải 2.2 (số thứ 1 và bóng) và giải 5.5 (số thứ 1 và bóng)
    """
    def get_code(self) -> str:
        return "de136_2d"
    
    def get_name(self) -> str:
        return "136 Đề 2 số"
    
    def get_description(self) -> str:
        return "Dự đoán 2 số từ giải 2.2 và giải 5.5"
    
    def calculate(self, data: Dict[str, Any]) -> Dict[str, List[str]]:
        giai_2_2 = data.get('giai_2_2', '')
        giai_5_5 = data.get('giai_5_5', '')
        
        if not giai_2_2 or not giai_5_5:
            logger.warning(f"[{self.get_code()}] Thiếu dữ liệu đầu vào: giai_2_2={giai_2_2}, giai_5_5={giai_5_5}")
            return {'two_digits_special': []}
        
        try:
            # Số thứ nhất từ giải 2.2: số thứ 1 và bóng
            # Ví dụ: 25249 -> số thứ 1 = 2, bóng là 7
            if len(giai_2_2) >= 1:
                digit_first = giai_2_2[0]
                first_nums = [digit_first, str(get_ball_number(int(digit_first)))]
            else:
                logger.warning(f"[{self.get_code()}] Giải 2.2 không đủ dài: {giai_2_2}")
                return {'two_digits_special': []}
                
            # Số thứ hai từ giải 5.5: số thứ 1 và bóng
            # Ví dụ: 5123 -> số thứ 1 = 5, bóng là 0
            if len(giai_5_5) >= 1:
                digit_first = giai_5_5[0]
                second_nums = [digit_first, str(get_ball_number(int(digit_first)))]
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
            logger.error(f"[{self.get_code()}] Lỗi tính 136 đề 2 số: {str(e)}")
            return {'two_digits_special': []}

class De136ThreeDigitMethod(BasePredictionMethod):
    """
    Phương pháp 136 Đề 3 số
    Dự đoán từ giải 2.2 (số thứ 1 và bóng), giải 5.5 (số thứ 1 và bóng), và giải 2.1 (càng đề từ tổng số thứ 4 và 5)
    """
    def get_code(self) -> str:
        return "de136_3d"
    
    def get_name(self) -> str:
        return "136 Đề 3 số"
    
    def get_description(self) -> str:
        return "Dự đoán 3 số từ giải 2.2, 5.5 và giải 2.1 (càng đề)"
    
    def calculate(self, data: Dict[str, Any]) -> Dict[str, List[str]]:
        giai_2_2 = data.get('giai_2_2', '')
        giai_5_5 = data.get('giai_5_5', '')
        giai_2_1 = data.get('giai_2_1', '')
        
        if not giai_2_2 or not giai_5_5 or not giai_2_1:
            logger.warning(f"[{self.get_code()}] Thiếu dữ liệu đầu vào: giai_2_2={giai_2_2}, giai_5_5={giai_5_5}, giai_2_1={giai_2_1}")
            return {'three_digits_special': []}
        
        try:
            # Số thứ nhất từ giải 2.2: số thứ 1 và bóng
            # Ví dụ: 25249 -> số thứ 1 = 2, bóng là 7
            if len(giai_2_2) >= 1:
                digit_first = giai_2_2[0]
                first_nums = [digit_first, str(get_ball_number(int(digit_first)))]
            else:
                logger.warning(f"[{self.get_code()}] Giải 2.2 không đủ dài: {giai_2_2}")
                return {'three_digits_special': []}
                
            # Số thứ hai từ giải 5.5: số thứ 1 và bóng
            # Ví dụ: 5123 -> số thứ 1 = 5, bóng là 0
            if len(giai_5_5) >= 1:
                digit_first = giai_5_5[0]
                second_nums = [digit_first, str(get_ball_number(int(digit_first)))]
            else:
                logger.warning(f"[{self.get_code()}] Giải 5.5 không đủ dài: {giai_5_5}")
                return {'three_digits_special': []}
            
            # Tạo các cặp số 2 chữ số (bao gồm cả cặp đảo ngược)
            two_digits = []
            for first in first_nums:
                for second in second_nums:
                    two_digits.append(f"{first}{second}")
                    two_digits.append(f"{second}{first}")
            
            # Càng đề từ giải 2.1: tổng số thứ 4 và số thứ 5, lấy số cuối và bóng
            # Ví dụ: 46741 -> số thứ 4 = 4, số thứ 5 = 1 -> tổng = 5, bóng là 0
            if len(giai_2_1) >= 5:
                digit_fourth_cang = int(giai_2_1[3])
                digit_fifth_cang = int(giai_2_1[4])
                sum_digits = (digit_fourth_cang + digit_fifth_cang) % 10  # Lấy số cuối của tổng
                cang_nums = [str(sum_digits), str(get_ball_number(sum_digits))]
            else:
                logger.warning(f"[{self.get_code()}] Giải 2.1 không đủ dài: {giai_2_1}")
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
            logger.error(f"[{self.get_code()}] Lỗi tính 136 đề 3 số: {str(e)}")
            return {'three_digits_special': []}