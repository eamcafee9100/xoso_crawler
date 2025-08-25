from typing import Dict, List, Any
from .base import BasePredictionMethod
from .utils import get_ball_number
import logging

logger = logging.getLogger(__name__)

class De24TwoDigitMethod(BasePredictionMethod):
    """
    Phương pháp 24 Đề 2 số
    Dự đoán từ giải 4.1 (số thứ 2 và bóng) và giải 5.5 (số thứ 2 và bóng)
    """
    def get_code(self) -> str:
        return "de24_2d"
    
    def get_name(self) -> str:
        return "24 Đề 2 số"
    
    def get_description(self) -> str:
        return "Dự đoán 2 số từ giải 4.1 và giải 5.5"
    
    def calculate(self, data: Dict[str, Any]) -> Dict[str, List[str]]:
        giai_4_1 = data.get('giai_4_1', '')
        giai_5_5 = data.get('giai_5_5', '')
        
        if not giai_4_1 or not giai_5_5:
            logger.warning(f"[{self.get_code()}] Thiếu dữ liệu đầu vào: giai_4_1={giai_4_1}, giai_5_5={giai_5_5}")
            return {'two_digits_special': []}
        
        try:
            # Số thứ nhất từ giải 4.1: số thứ 2 và bóng
            # Ví dụ: 1859 -> số thứ 2 = 8 và bóng là 3
            if len(giai_4_1) >= 2:
                digit_second = giai_4_1[1]
                first_nums = [digit_second, str(get_ball_number(int(digit_second)))]
            else:
                logger.warning(f"[{self.get_code()}] Giải 4.1 không đủ dài: {giai_4_1}")
                return {'two_digits_special': []}
                
            # Số thứ 2 từ giải 5.5: số thứ 2 và bóng
            # Ví dụ: 4196 -> số thứ 2 = 1 và bóng là 6
            if len(giai_5_5) >= 2:
                digit_second = giai_5_5[1]
                second_nums = [digit_second, str(get_ball_number(int(digit_second)))]
            else:
                logger.warning(f"[{self.get_code()}] Giải 5.5 không đủ dài: {giai_5_5}")
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
            logger.error(f"[{self.get_code()}] Lỗi tính 24 đề 2 số: {str(e)}")
            return {'two_digits_special': []}


class De24ThreeDigitMethod(BasePredictionMethod):
    """
    Phương pháp 24 Đề 3 số
    Dự đoán từ giải 4.1, 5.5 và giải 4.4 (chạm đề)
    """
    def get_code(self) -> str:
        return "de24_3d"
    
    def get_name(self) -> str:
        return "24 Đề 3 số"
    
    def get_description(self) -> str:
        return "Dự đoán 3 số từ giải 4.1, 5.5 và giải 4.4 (chạm đề)"
    
    def calculate(self, data: Dict[str, Any]) -> Dict[str, List[str]]:
        giai_4_1 = data.get('giai_4_1', '')
        giai_5_5 = data.get('giai_5_5', '')
        giai_4_4 = data.get('giai_4_4', '')
        
        if not giai_4_1 or not giai_5_5 or not giai_4_4:
            logger.warning(f"[{self.get_code()}] Thiếu dữ liệu đầu vào: giai_4_1={giai_4_1}, giai_5_5={giai_5_5}, giai_4_4={giai_4_4}")
            return {'three_digits_special': []}
        
        try:
            # Tính các cặp số 2 chữ số từ giải 4.1 và 5.5
            if len(giai_4_1) >= 2:
                digit_second = giai_4_1[1]
                first_nums = [digit_second, str(get_ball_number(int(digit_second)))]
            else:
                logger.warning(f"[{self.get_code()}] Giải 4.1 không đủ dài: {giai_4_1}")
                return {'three_digits_special': []}
                
            if len(giai_5_5) >= 2:
                digit_second = giai_5_5[1]
                second_nums = [digit_second, str(get_ball_number(int(digit_second)))]
            else:
                logger.warning(f"[{self.get_code()}] Giải 5.5 không đủ dài: {giai_5_5}")
                return {'three_digits_special': []}
            
            # Tạo các cặp số 2 chữ số (bao gồm cả cặp đảo ngược)
            two_digits = []
            for first in first_nums:
                for second in second_nums:
                    # Thêm cặp số thẳng
                    two_digits.append(f"{first}{second}")
                    # Thêm cặp số đảo ngược
                    two_digits.append(f"{second}{first}")
            
            # Chạm đề từ giải 4.4: số thứ 2
            if len(giai_4_4) >= 2:
                cham_de = giai_4_4[1]  # Lấy số thứ 2, ví dụ: 3236 -> 2
                cham_de_bong = str(get_ball_number(int(cham_de)))
                cham_nums = [cham_de, cham_de_bong]
            else:
                logger.warning(f"[{self.get_code()}] Giải 4.4 không đủ dài: {giai_4_4}")
                return {'three_digits_special': []}
            
            # Tạo các cặp số 3 chữ số
            three_digits = set()
            for cham in cham_nums:
                for two_digit in two_digits:
                    three_digits.add(f"{cham}{two_digit}")
            
            logger.info(f"[{self.get_code()}] Kết quả: {sorted(list(three_digits))}")
            return {
                'three_digits_special': sorted(list(three_digits))
            }
        except (ValueError, IndexError, TypeError) as e:
            logger.error(f"[{self.get_code()}] Lỗi tính 24 đề 3 số: {str(e)}")
            return {'three_digits_special': []}