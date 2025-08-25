from typing import Dict, List, Any
from .base import BasePredictionMethod
from .utils import get_ball_number
import logging

logger = logging.getLogger(__name__)

class De81TwoDigitMethod(BasePredictionMethod):
    """
    Phương pháp 81 Đề 2 số
    Dự đoán từ giải 2.1 (tổng số thứ 4 và 5 và bóng) và giải 5.4 (số thứ 1 và bóng)
    """
    def get_code(self) -> str:
        return "de81_2d"
    
    def get_name(self) -> str:
        return "81 Đề 2 số"
    
    def get_description(self) -> str:
        return "Dự đoán 2 số từ giải 2.1 và giải 5.4"
    
    def calculate(self, data: Dict[str, Any]) -> Dict[str, List[str]]:
        giai_2_1 = data.get('giai_2_1', '')
        giai_5_4 = data.get('giai_5_4', '')
        
        if not giai_2_1 or not giai_5_4:
            logger.warning(f"[{self.get_code()}] Thiếu dữ liệu đầu vào: giai_2_1={giai_2_1}, giai_5_4={giai_5_4}")
            return {'two_digits_special': []}
        
        try:
            # Số thứ nhất từ giải 2.1: tổng số thứ 4 và số thứ 5, và bóng
            # Ví dụ: 23496 -> 9+6=15 -> 15%10=5 và bóng là 0
            if len(giai_2_1) >= 5:
                sum_fourth_fifth = (int(giai_2_1[3]) + int(giai_2_1[4])) % 10
                first_nums = [str(sum_fourth_fifth), str(get_ball_number(sum_fourth_fifth))]
            else:
                logger.warning(f"[{self.get_code()}] Giải 2.1 không đủ dài: {giai_2_1}")
                return {'two_digits_special': []}
                
            # Số thứ 2 từ giải 5.4: số thứ 1 và bóng
            # Ví dụ: 1346 -> số thứ 1 = 1 và bóng là 6
            if len(giai_5_4) >= 1:
                digit_first = giai_5_4[0]
                second_nums = [digit_first, str(get_ball_number(int(digit_first)))]
            else:
                logger.warning(f"[{self.get_code()}] Giải 5.4 không đủ dài: {giai_5_4}")
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
            logger.error(f"[{self.get_code()}] Lỗi tính 81 đề 2 số: {str(e)}")
            return {'two_digits_special': []}


class De81ThreeDigitMethod(BasePredictionMethod):
    """
    Phương pháp 81 Đề 3 số
    Dự đoán từ giải 2.1, 5.4 và giải 5.3 (càng đề)
    """
    def get_code(self) -> str:
        return "de81_3d"
    
    def get_name(self) -> str:
        return "81 Đề 3 số"
    
    def get_description(self) -> str:
        return "Dự đoán 3 số từ giải 2.1, 5.4 và giải 5.3 (càng đề)"
    
    def calculate(self, data: Dict[str, Any]) -> Dict[str, List[str]]:
        giai_2_1 = data.get('giai_2_1', '')
        giai_5_4 = data.get('giai_5_4', '')
        giai_5_3 = data.get('giai_5_3', '')
        
        if not giai_2_1 or not giai_5_4 or not giai_5_3:
            logger.warning(f"[{self.get_code()}] Thiếu dữ liệu đầu vào: giai_2_1={giai_2_1}, giai_5_4={giai_5_4}, giai_5_3={giai_5_3}")
            return {'three_digits_special': []}
        
        try:
            # Tính các cặp số 2 chữ số từ giải 2.1 và 5.4
            if len(giai_2_1) >= 5:
                sum_fourth_fifth = (int(giai_2_1[3]) + int(giai_2_1[4])) % 10
                first_nums = [str(sum_fourth_fifth), str(get_ball_number(sum_fourth_fifth))]
            else:
                logger.warning(f"[{self.get_code()}] Giải 2.1 không đủ dài: {giai_2_1}")
                return {'three_digits_special': []}
                
            if len(giai_5_4) >= 1:
                digit_first = giai_5_4[0]
                second_nums = [digit_first, str(get_ball_number(int(digit_first)))]
            else:
                logger.warning(f"[{self.get_code()}] Giải 5.4 không đủ dài: {giai_5_4}")
                return {'three_digits_special': []}
            
            # Tạo các cặp số 2 chữ số (bao gồm cả cặp đảo ngược)
            two_digits = []
            for first in first_nums:
                for second in second_nums:
                    # Thêm cặp số thẳng
                    two_digits.append(f"{first}{second}")
                    # Thêm cặp số đảo ngược
                    two_digits.append(f"{second}{first}")
            
            # Càng đề từ giải 5.3: tổng số thứ 1 và số thứ 2, và bóng
            if len(giai_5_3) >= 2:
                sum_first_second = (int(giai_5_3[0]) + int(giai_5_3[1])) % 10
                cang_de = str(sum_first_second)
                cang_de_bong = str(get_ball_number(sum_first_second))
                cang_nums = [cang_de, cang_de_bong]
            else:
                logger.warning(f"[{self.get_code()}] Giải 5.3 không đủ dài: {giai_5_3}")
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
            logger.error(f"[{self.get_code()}] Lỗi tính 81 đề 3 số: {str(e)}")
            return {'three_digits_special': []}