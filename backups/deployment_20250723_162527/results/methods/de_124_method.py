from typing import Dict, List, Any
from .base import BasePredictionMethod
from .utils import get_ball_number
import logging

logger = logging.getLogger(__name__)

class De124TwoDigitMethod(BasePredictionMethod):
    """
    Phương pháp 124 Đề 2 số
    Dự đoán từ giải 6.2 (số thứ 3) cộng giải 7.3 (số thứ 2) và giải 7.2 (số thứ 2 và bóng)
    """
    def get_code(self) -> str:
        return "de124_2d"
    
    def get_name(self) -> str:
        return "124 Đề 2 số"
    
    def get_description(self) -> str:
        return "Dự đoán 2 số từ tổng giải 6.2, 7.3 và giải 7.2"
    
    def calculate(self, data: Dict[str, Any]) -> Dict[str, List[str]]:
        giai_6_2 = data.get('giai_6_2', '')
        giai_7_3 = data.get('giai_7_3', '')
        giai_7_2 = data.get('giai_7_2', '')
        
        if not giai_6_2 or not giai_7_3 or not giai_7_2:
            logger.warning(f"[{self.get_code()}] Thiếu dữ liệu đầu vào: giai_6_2={giai_6_2}, giai_7_3={giai_7_3}, giai_7_2={giai_7_2}")
            return {'two_digits_special': []}
        
        try:
            # Số thứ nhất: tổng số thứ 3 từ giải 6.2 và số thứ 2 từ giải 7.3
            # Ví dụ: giai_6_2=249 -> số thứ 3 = 9, giai_7_3=39 -> số thứ 2 = 9, tổng 9+9=18 -> 8
            if len(giai_6_2) >= 3 and len(giai_7_3) >= 2:
                digit_third_6_2 = int(giai_6_2[2])
                digit_second_7_3 = int(giai_7_3[1])
                sum_digits = (digit_third_6_2 + digit_second_7_3) % 10
                first_nums = [str(sum_digits)]
            else:
                logger.warning(f"[{self.get_code()}] Giải 6.2 hoặc 7.3 không đủ dài: giai_6_2={giai_6_2}, giai_7_3={giai_7_3}")
                return {'two_digits_special': []}
                
            # Số thứ hai từ giải 7.2: số thứ 2 và bóng
            # Ví dụ: 12 -> số thứ 2 = 2, bóng là 7
            if len(giai_7_2) >= 2:
                digit_second = giai_7_2[1]
                second_nums = [digit_second, str(get_ball_number(int(digit_second)))]
            else:
                logger.warning(f"[{self.get_code()}] Giải 7.2 không đủ dài: {giai_7_2}")
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
            logger.error(f"[{self.get_code()}] Lỗi tính 124 đề 2 số: {str(e)}")
            return {'two_digits_special': []}

class De124ThreeDigitMethod(BasePredictionMethod):
    """
    Phương pháp 124 Đề 3 số
    Dự đoán từ giải 6.2 (số thứ 3) cộng giải 7.3 (số thứ 2), giải 7.2 (số thứ 2 và bóng), và giải 4.4 (càng đề)
    """
    def get_code(self) -> str:
        return "de124_3d"
    
    def get_name(self) -> str:
        return "124 Đề 3 số"
    
    def get_description(self) -> str:
        return "Dự đoán 3 số từ tổng giải 6.2, 7.3, giải 7.2 và giải 4.4 (càng đề)"
    
    def calculate(self, data: Dict[str, Any]) -> Dict[str, List[str]]:
        giai_6_2 = data.get('giai_6_2', '')
        giai_7_3 = data.get('giai_7_3', '')
        giai_7_2 = data.get('giai_7_2', '')
        giai_4_4 = data.get('giai_4_4', '')
        
        if not giai_6_2 or not giai_7_3 or not giai_7_2 or not giai_4_4:
            logger.warning(f"[{self.get_code()}] Thiếu dữ liệu đầu vào: giai_6_2={giai_6_2}, giai_7_3={giai_7_3}, giai_7_2={giai_7_2}, giai_4_4={giai_4_4}")
            return {'three_digits_special': []}
        
        try:
            # Số thứ nhất: tổng số thứ 3 từ giải 6.2 và số thứ 2 từ giải 7.3
            # Ví dụ: giai_6_2=249 -> số thứ 3 = 9, giai_7_3=39 -> số thứ 2 = 9, tổng 9+9=18 -> 8
            if len(giai_6_2) >= 3 and len(giai_7_3) >= 2:
                digit_third_6_2 = int(giai_6_2[2])
                digit_second_7_3 = int(giai_7_3[1])
                sum_digits = (digit_third_6_2 + digit_second_7_3) % 10
                first_nums = [str(sum_digits)]
            else:
                logger.warning(f"[{self.get_code()}] Giải 6.2 hoặc 7.3 không đủ dài: giai_6_2={giai_6_2}, giai_7_3={giai_7_3}")
                return {'three_digits_special': []}
                
            # Số thứ hai từ giải 7.2: số thứ 2 và bóng
            # Ví dụ: 12 -> số thứ 2 = 2, bóng là 7
            if len(giai_7_2) >= 2:
                digit_second = giai_7_2[1]
                second_nums = [digit_second, str(get_ball_number(int(digit_second)))]
            else:
                logger.warning(f"[{self.get_code()}] Giải 7.2 không đủ dài: {giai_7_2}")
                return {'three_digits_special': []}
            
            # Tạo các cặp số 2 chữ số (bao gồm cả cặp đảo ngược)
            two_digits = []
            for first in first_nums:
                for second in second_nums:
                    two_digits.append(f"{first}{second}")
                    two_digits.append(f"{second}{first}")
            
            # Càng đề từ giải 4.4: số thứ 2 và bóng
            # Ví dụ: 2349 -> số thứ 2 = 3, bóng là 8
            if len(giai_4_4) >= 2:
                digit_second_cang = giai_4_4[1]
                cang_nums = [digit_second_cang, str(get_ball_number(int(digit_second_cang)))]
            else:
                logger.warning(f"[{self.get_code()}] Giải 4.4 không đủ dài: {giai_4_4}")
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
            logger.error(f"[{self.get_code()}] Lỗi tính 124 đề 3 số: {str(e)}")
            return {'three_digits_special': []}