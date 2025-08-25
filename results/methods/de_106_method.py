from typing import Dict, List, Any
from .base import BasePredictionMethod
from .utils import get_ball_number
import logging

logger = logging.getLogger(__name__)

class De106TwoDigitMethod(BasePredictionMethod):
    """
    Phương pháp 106 Đề 2 số
    Dự đoán từ giải 3.2 (tổng 2 số đầu và bóng) và giải 5.2 (số đầu và bóng)
    """
    def get_code(self) -> str:
        return "de106_2d"
    
    def get_name(self) -> str:
        return "106 Đề 2 số"
    
    def get_description(self) -> str:
        return "Dự đoán 2 số từ giải 3.2 và giải 5.2"
    
    def calculate(self, data: Dict[str, Any]) -> Dict[str, List[str]]:
        giai_3_2 = data.get('giai_3_2', '')
        giai_5_2 = data.get('giai_5_2', '')
        
        if not giai_3_2 or not giai_5_2:
            logger.warning(f"[{self.get_code()}] Thiếu dữ liệu đầu vào: giai_3_2={giai_3_2}, giai_5_2={giai_5_2}")
            return {'two_digits_special': []}
        
        try:
            # Số thứ nhất từ giải 3.2: tổng 2 số đầu và bóng của nó
            if len(giai_3_2) >= 2:
                sum_first_two = (int(giai_3_2[0]) + int(giai_3_2[1])) % 10
                first_nums = [str(sum_first_two), str(get_ball_number(sum_first_two))]
            else:
                logger.warning(f"[{self.get_code()}] Giải 3.2 không đủ dài: {giai_3_2}")
                return {'two_digits_special': []}
                
            # Số thứ 2 từ giải 5.2: số đầu và bóng của nó
            if len(giai_5_2) >= 1:
                second_digit = giai_5_2[0]
                second_nums = [second_digit, str(get_ball_number(int(second_digit)))]
            else:
                logger.warning(f"[{self.get_code()}] Giải 5.2 không đủ dài: {giai_5_2}")
                return {'two_digits_special': []}
            
            # Tạo các cặp số 2 chữ số
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
            logger.error(f"[{self.get_code()}] Lỗi tính 106 đề 2 số: {str(e)}")
            return {'two_digits_special': []}


class De106ThreeDigitMethod(BasePredictionMethod):
    """
    Phương pháp 106 Đề 3 số
    Dự đoán từ giải 3.2, 5.2 và giải 3.4 (chạm đề)
    """
    def get_code(self) -> str:
        return "de106_3d"
    
    def get_name(self) -> str:
        return "106 Đề 3 số"
    
    def get_description(self) -> str:
        return "Dự đoán 3 số từ giải 3.2, 5.2 và giải 3.4 (chạm đề)"
    
    def calculate(self, data: Dict[str, Any]) -> Dict[str, List[str]]:
        giai_3_2 = data.get('giai_3_2', '')
        giai_5_2 = data.get('giai_5_2', '')
        giai_3_4 = data.get('giai_3_4', '')
        
        if not giai_3_2 or not giai_5_2 or not giai_3_4:
            logger.warning(f"[{self.get_code()}] Thiếu dữ liệu đầu vào: giai_3_2={giai_3_2}, giai_5_2={giai_5_2}, giai_3_4={giai_3_4}")
            return {'three_digits_special': []}
        
        try:
            # Tính các cặp số 2 chữ số như phương pháp 2 số
            if len(giai_3_2) >= 2:
                sum_first_two = (int(giai_3_2[0]) + int(giai_3_2[1])) % 10
                first_nums = [str(sum_first_two), str(get_ball_number(sum_first_two))]
            else:
                logger.warning(f"[{self.get_code()}] Giải 3.2 không đủ dài: {giai_3_2}")
                return {'three_digits_special': []}
                
            if len(giai_5_2) >= 1:
                second_digit = giai_5_2[0]
                second_nums = [second_digit, str(get_ball_number(int(second_digit)))]
            else:
                logger.warning(f"[{self.get_code()}] Giải 5.2 không đủ dài: {giai_5_2}")
                return {'three_digits_special': []}
            
            # Tạo các cặp số 2 chữ số
            two_digits = []
            for first in first_nums:
                for second in second_nums:
                    two_digits.append(f"{first}{second}")
                    two_digits.append(f"{second}{first}")
            
            # Chạm đề từ giải 3.4: số thứ 3
            if len(giai_3_4) >= 3:
                cham_de = giai_3_4[2]  # Lấy số thứ 3, ví dụ: 72091 -> 0
                cham_de_bong = str(get_ball_number(int(cham_de)))
                cham_nums = [cham_de, cham_de_bong]
            else:
                logger.warning(f"[{self.get_code()}] Giải 3.4 không đủ dài: {giai_3_4}")
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
            logger.error(f"[{self.get_code()}] Lỗi tính 106 đề 3 số: {str(e)}")
            return {'three_digits_special': []}