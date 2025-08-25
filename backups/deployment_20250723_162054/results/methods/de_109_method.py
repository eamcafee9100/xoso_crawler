from typing import Dict, List, Any
from .base import BasePredictionMethod
from .utils import get_ball_number
import logging

logger = logging.getLogger(__name__)

class De109TwoDigitMethod(BasePredictionMethod):
    """
    Phương pháp 109 Đề 2 số
    Dự đoán từ giải 2.2 (tổng số thứ 4 và 5, lấy bóng) và giải 5.5 (tổng số thứ 3 và 4, lấy bóng)
    """
    def get_code(self) -> str:
        return "de109_2d"
    
    def get_name(self) -> str:
        return "109 Đề 2 số"
    
    def get_description(self) -> str:
        return "Dự đoán 2 số từ giải 2.2 và giải 5.5"
    
    def calculate(self, data: Dict[str, Any]) -> Dict[str, List[str]]:
        giai_2_2 = data.get('giai_2_2', '')
        giai_5_5 = data.get('giai_5_5', '')
        
        if not giai_2_2 or not giai_5_5:
            logger.warning(f"[{self.get_code()}] Thiếu dữ liệu đầu vào: giai_2_2={giai_2_2}, giai_5_5={giai_5_5}")
            return {'two_digits_special': []}
        
        try:
            # Số thứ nhất từ giải 2.2: tổng số thứ 4 và 5, lấy bóng
            # Ví dụ: 23496 -> 9+6=15 -> 5 và bóng là 0
            if len(giai_2_2) >= 5:
                sum_fourth_fifth = (int(giai_2_2[3]) + int(giai_2_2[4])) % 10
                first_nums = [str(sum_fourth_fifth), str(get_ball_number(sum_fourth_fifth))]
            else:
                logger.warning(f"[{self.get_code()}] Giải 2.2 không đủ dài: {giai_2_2}")
                return {'two_digits_special': []}
                
            # Số thứ hai từ giải 5.5: tổng số thứ 3 và 4, lấy bóng
            # Ví dụ: 3234 -> 3+4=7 và bóng là 2
            if len(giai_5_5) >= 4:
                sum_third_fourth = (int(giai_5_5[2]) + int(giai_5_5[3])) % 10
                second_nums = [str(sum_third_fourth), str(get_ball_number(sum_third_fourth))]
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
            logger.error(f"[{self.get_code()}] Lỗi tính 109 đề 2 số: {str(e)}")
            return {'two_digits_special': []}

class De109ThreeDigitMethod(BasePredictionMethod):
    """
    Phương pháp 109 Đề 3 số
    Dự đoán từ giải 2.2 (tổng số thứ 4 và 5, lấy bóng), giải 5.5 (tổng số thứ 3 và 4, lấy bóng), và giải 5.1 (càng đề)
    """
    def get_code(self) -> str:
        return "de109_3d"
    
    def get_name(self) -> str:
        return "109 Đề 3 số"
    
    def get_description(self) -> str:
        return "Dự đoán 3 số từ giải 2.2, 5.5 và giải 5.1 (càng đề)"
    
    def calculate(self, data: Dict[str, Any]) -> Dict[str, List[str]]:
        giai_2_2 = data.get('giai_2_2', '')
        giai_5_5 = data.get('giai_5_5', '')
        giai_5_1 = data.get('giai_5_1', '')
        
        if not giai_2_2 or not giai_5_5 or not giai_5_1:
            logger.warning(f"[{self.get_code()}] Thiếu dữ liệu đầu vào: giai_2_2={giai_2_2}, giai_5_5={giai_5_5}, giai_5_1={giai_5_1}")
            return {'three_digits_special': []}
        
        try:
            # Số thứ nhất từ giải 2.2: tổng số thứ 4 và 5, lấy bóng
            # Ví dụ: 23496 -> 9+6=15 -> 5 và bóng là 0
            if len(giai_2_2) >= 5:
                sum_fourth_fifth = (int(giai_2_2[3]) + int(giai_2_2[4])) % 10
                first_nums = [str(sum_fourth_fifth), str(get_ball_number(sum_fourth_fifth))]
            else:
                logger.warning(f"[{self.get_code()}] Giải 2.2 không đủ dài: {giai_2_2}")
                return {'three_digits_special': []}
                
            # Số thứ hai từ giải 5.5: tổng số thứ 3 và 4, lấy bóng
            # Ví dụ: 3234 -> 3+4=7 và bóng là 2
            if len(giai_5_5) >= 4:
                sum_third_fourth = (int(giai_5_5[2]) + int(giai_5_5[3])) % 10
                second_nums = [str(sum_third_fourth), str(get_ball_number(sum_third_fourth))]
            else:
                logger.warning(f"[{self.get_code()}] Giải 5.5 không đủ dài: {giai_5_5}")
                return {'three_digits_special': []}
            
            # Tạo các cặp số 2 chữ số (bao gồm cả cặp đảo ngược)
            two_digits = []
            for first in first_nums:
                for second in second_nums:
                    two_digits.append(f"{first}{second}")
                    two_digits.append(f"{second}{first}")
            
            # Càng đề từ giải 5.1: tổng số thứ 2 và 3, lấy bóng
            # Ví dụ: 2628 -> 6+2=8 và bóng là 3
            if len(giai_5_1) >= 3:
                sum_second_third = (int(giai_5_1[1]) + int(giai_5_1[2])) % 10
                cang_nums = [str(sum_second_third), str(get_ball_number(sum_second_third))]
            else:
                logger.warning(f"[{self.get_code()}] Giải 5.1 không đủ dài: {giai_5_1}")
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
            logger.error(f"[{self.get_code()}] Lỗi tính 109 đề 3 số: {str(e)}")
            return {'three_digits_special': []}