from typing import Dict, List, Any
from .base import BasePredictionMethod
from .utils import get_ball_number
import logging

logger = logging.getLogger(__name__)

class De110TwoDigitMethod(BasePredictionMethod):
    """
    Phương pháp 110 Đề 2 số
    Dự đoán từ giải 2.2 (tổng số thứ 4 và 5, lấy bóng) và giải 3.4 (tổng số thứ 1, 2 và 3, lấy bóng)
    """
    def get_code(self) -> str:
        return "de110_2d"
    
    def get_name(self) -> str:
        return "110 Đề 2 số"
    
    def get_description(self) -> str:
        return "Dự đoán 2 số từ giải 2.2 và giải 3.4"
    
    def calculate(self, data: Dict[str, Any]) -> Dict[str, List[str]]:
        giai_2_2 = data.get('giai_2_2', '')
        giai_3_4 = data.get('giai_3_4', '')
        
        if not giai_2_2 or not giai_3_4:
            logger.warning(f"[{self.get_code()}] Thiếu dữ liệu đầu vào: giai_2_2={giai_2_2}, giai_3_4={giai_3_4}")
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
                
            # Số thứ hai từ giải 3.4: tổng số thứ 1, 2 và 3, lấy bóng
            # Ví dụ: 32347 -> 3+2+3=8 và bóng là 3
            if len(giai_3_4) >= 3:
                sum_first_second_third = (int(giai_3_4[0]) + int(giai_3_4[1]) + int(giai_3_4[2])) % 10
                second_nums = [str(sum_first_second_third), str(get_ball_number(sum_first_second_third))]
            else:
                logger.warning(f"[{self.get_code()}] Giải 3.4 không đủ dài: {giai_3_4}")
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
            logger.error(f"[{self.get_code()}] Lỗi tính 110 đề 2 số: {str(e)}")
            return {'two_digits_special': []}

class De110ThreeDigitMethod(BasePredictionMethod):
    """
    Phương pháp 110 Đề 3 số
    Dự đoán từ giải 2.2 (tổng số thứ 4 và 5, lấy bóng), giải 3.4 (tổng số thứ 1, 2 và 3, lấy bóng), và giải 3.5 (càng đề)
    """
    def get_code(self) -> str:
        return "de110_3d"
    
    def get_name(self) -> str:
        return "110 Đề 3 số"
    
    def get_description(self) -> str:
        return "Dự đoán 3 số từ giải 2.2, 3.4 và giải 3.5 (càng đề)"
    
    def calculate(self, data: Dict[str, Any]) -> Dict[str, List[str]]:
        giai_2_2 = data.get('giai_2_2', '')
        giai_3_4 = data.get('giai_3_4', '')
        giai_3_5 = data.get('giai_3_5', '')
        
        if not giai_2_2 or not giai_3_4 or not giai_3_5:
            logger.warning(f"[{self.get_code()}] Thiếu dữ liệu đầu vào: giai_2_2={giai_2_2}, giai_3_4={giai_3_4}, giai_3_5={giai_3_5}")
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
                
            # Số thứ hai từ giải 3.4: tổng số thứ 1, 2 và 3, lấy bóng
            # Ví dụ: 32347 -> 3+2+3=8 và bóng là 3
            if len(giai_3_4) >= 3:
                sum_first_second_third = (int(giai_3_4[0]) + int(giai_3_4[1]) + int(giai_3_4[2])) % 10
                second_nums = [str(sum_first_second_third), str(get_ball_number(sum_first_second_third))]
            else:
                logger.warning(f"[{self.get_code()}] Giải 3.4 không đủ dài: {giai_3_4}")
                return {'three_digits_special': []}
            
            # Tạo các cặp số 2 chữ số (bao gồm cả cặp đảo ngược)
            two_digits = []
            for first in first_nums:
                for second in second_nums:
                    two_digits.append(f"{first}{second}")
                    two_digits.append(f"{second}{first}")
            
            # Càng đề từ giải 3.5: số thứ 1 và bóng
            # Ví dụ: 92628 -> số thứ 1 = 9 và bóng là 4
            if len(giai_3_5) >= 1:
                digit_first_cang = giai_3_5[0]
                cang_nums = [digit_first_cang, str(get_ball_number(int(digit_first_cang)))]
            else:
                logger.warning(f"[{self.get_code()}] Giải 3.5 không đủ dài: {giai_3_5}")
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
            logger.error(f"[{self.get_code()}] Lỗi tính 110 đề 3 số: {str(e)}")
            return {'three_digits_special': []}