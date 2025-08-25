from typing import Dict, List, Any
from .base import BasePredictionMethod
from .utils import get_ball_number
import logging

logger = logging.getLogger(__name__)

class De52TwoDigitMethod(BasePredictionMethod):
    """
    Phương pháp 52 Đề 2 số
    Dự đoán từ giải 2.2 (tổng số thứ 1 và 2) và giải 6.1 (tổng số thứ 1 và 2)
    """
    def get_code(self) -> str:
        return "de52_2d"
    
    def get_name(self) -> str:
        return "52 Đề 2 số"
    
    def get_description(self) -> str:
        return "Dự đoán 2 số từ giải 2.2 và giải 6.1"
    
    def calculate(self, data: Dict[str, Any]) -> Dict[str, List[str]]:
        giai_2_2 = data.get('giai_2_2', '')
        giai_6_1 = data.get('giai_6_1', '')
        
        if not giai_2_2 or not giai_6_1:
            logger.warning(f"[{self.get_code()}] Thiếu dữ liệu đầu vào: giai_2_2={giai_2_2}, giai_6_1={giai_6_1}")
            return {'two_digits_special': []}
        
        try:
            # Số thứ nhất từ giải 2.2: tổng số thứ 1 và số thứ 2 và bóng
            # Ví dụ: 18519 -> 1+8=9 và bóng là 4
            if len(giai_2_2) >= 2:
                sum_first_two = (int(giai_2_2[0]) + int(giai_2_2[1])) % 10
                first_nums = [str(sum_first_two), str(get_ball_number(sum_first_two))]
            else:
                logger.warning(f"[{self.get_code()}] Giải 2.2 không đủ dài: {giai_2_2}")
                return {'two_digits_special': []}
                
            # Số thứ 2 từ giải 6.1: tổng số thứ 1 và số thứ 2
            # Ví dụ: 196 -> 1+9=10 -> 0 và bóng là 5
            if len(giai_6_1) >= 2:
                sum_first_two = (int(giai_6_1[0]) + int(giai_6_1[1])) % 10
                second_nums = [str(sum_first_two), str(get_ball_number(sum_first_two))]
            else:
                logger.warning(f"[{self.get_code()}] Giải 6.1 không đủ dài: {giai_6_1}")
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
            logger.error(f"[{self.get_code()}] Lỗi tính 52 đề 2 số: {str(e)}")
            return {'two_digits_special': []}


class De52ThreeDigitMethod(BasePredictionMethod):
    """
    Phương pháp 52 Đề 3 số
    Dự đoán từ giải 2.2, 6.1 và giải 3.6 (chạm đề)
    """
    def get_code(self) -> str:
        return "de52_3d"
    
    def get_name(self) -> str:
        return "52 Đề 3 số"
    
    def get_description(self) -> str:
        return "Dự đoán 3 số từ giải 2.2, 6.1 và giải 3.6 (chạm đề)"
    
    def calculate(self, data: Dict[str, Any]) -> Dict[str, List[str]]:
        giai_2_2 = data.get('giai_2_2', '')
        giai_6_1 = data.get('giai_6_1', '')
        giai_3_6 = data.get('giai_3_6', '')
        
        if not giai_2_2 or not giai_6_1 or not giai_3_6:
            logger.warning(f"[{self.get_code()}] Thiếu dữ liệu đầu vào: giai_2_2={giai_2_2}, giai_6_1={giai_6_1}, giai_3_6={giai_3_6}")
            return {'three_digits_special': []}
        
        try:
            # Tính các cặp số 2 chữ số từ giải 2.2 và 6.1
            if len(giai_2_2) >= 2:
                sum_first_two = (int(giai_2_2[0]) + int(giai_2_2[1])) % 10
                first_nums = [str(sum_first_two), str(get_ball_number(sum_first_two))]
            else:
                logger.warning(f"[{self.get_code()}] Giải 2.2 không đủ dài: {giai_2_2}")
                return {'three_digits_special': []}
                
            if len(giai_6_1) >= 2:
                sum_first_two = (int(giai_6_1[0]) + int(giai_6_1[1])) % 10
                second_nums = [str(sum_first_two), str(get_ball_number(sum_first_two))]
            else:
                logger.warning(f"[{self.get_code()}] Giải 6.1 không đủ dài: {giai_6_1}")
                return {'three_digits_special': []}
            
            # Tạo các cặp số 2 chữ số (bao gồm cả cặp đảo ngược)
            two_digits = []
            for first in first_nums:
                for second in second_nums:
                    # Thêm cặp số thẳng
                    two_digits.append(f"{first}{second}")
                    # Thêm cặp số đảo ngược
                    two_digits.append(f"{second}{first}")
            
            # Chạm đề từ giải 3.6: số thứ 1
            if len(giai_3_6) >= 1:
                cham_de = giai_3_6[0]  # Lấy số thứ 1, ví dụ: 13236 -> 1
                cham_de_bong = str(get_ball_number(int(cham_de)))
                cham_nums = [cham_de, cham_de_bong]
            else:
                logger.warning(f"[{self.get_code()}] Giải 3.6 không đủ dài: {giai_3_6}")
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
            logger.error(f"[{self.get_code()}] Lỗi tính 52 đề 3 số: {str(e)}")
            return {'three_digits_special': []}