from typing import Dict, List, Any
from .base import BasePredictionMethod
from .utils import get_ball_number
import logging

logger = logging.getLogger(__name__)

class De115TwoDigitMethod(BasePredictionMethod):
    """
    Phương pháp 115 Đề 2 số
    Dự đoán từ giải 5.6 (số thứ 3 và bóng) và giải 7.3 (số thứ 1 và bóng)
    """
    def get_code(self) -> str:
        return "de115_2d"
    
    def get_name(self) -> str:
        return "115 Đề 2 số"
    
    def get_description(self) -> str:
        return "Dự đoán 2 số từ giải 5.6 và giải 7.3"
    
    def calculate(self, data: Dict[str, Any]) -> Dict[str, List[str]]:
        giai_5_6 = data.get('giai_5_6', '')
        giai_7_3 = data.get('giai_7_3', '')
        
        if not giai_5_6 or not giai_7_3:
            logger.warning(f"[{self.get_code()}] Thiếu dữ liệu đầu vào: giai_5_6={giai_5_6}, giai_7_3={giai_7_3}")
            return {'two_digits_special': []}
        
        try:
            # Số thứ nhất từ giải 5.6: số thứ 3 và bóng
            # Ví dụ: 2349 -> số thứ 3 = 4, bóng là 9
            if len(giai_5_6) >= 3:
                digit_third = giai_5_6[2]
                first_nums = [digit_third, str(get_ball_number(int(digit_third)))]
            else:
                logger.warning(f"[{self.get_code()}] {self.get_code()} Giải quyết 5.6 không đủ dài: {giai_5_6}")
                return {'two_digits_special': []}
                
            # Số thứ hai từ giải 7.3: số thứ 1 và bóng
            # Ví dụ: 32 -> số thứ 1 = 3, bóng là 8
            if len(giai_7_3) >= 1:
                digit_first = giai_7_3[0]
                second_nums = [digit_first, str(get_ball_number(int(digit_first)))]
            else:
                logger.warning(f"[{self.get_code()}] Giải 7.3 không đủ dài: {giai_7_3}")
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
            logger.error(f"[{self.get_code()}] Lỗi tính 115 đề 2 số: {str(e)}")
            return {'two_digits_special': []}

class De115ThreeDigitMethod(BasePredictionMethod):
    """
    Phương pháp 115 Đề 3 số
    Dự đoán từ giải 5.6 (số thứ 3 và bóng), giải 7.3 (số thứ 1 và bóng), và giải 5.4 (càng đề)
    """
    def get_code(self) -> str:
        return "de115_3d"
    
    def get_name(self) -> str:
        return "115 Đề 3 số"
    
    def get_description(self) -> str:
        return "Dự đoán 3 số từ giải 5.6, 7.3 và giải 5.4 (càng đề)"
    
    def calculate(self, data: Dict[str, Any]) -> Dict[str, List[str]]:
        giai_5_6 = data.get('giai_5_6', '')
        giai_7_3 = data.get('giai_7_3', '')
        giai_5_4 = data.get('giai_5_4', '')
        
        if not giai_5_6 or not giai_7_3 or not giai_5_4:
            logger.warning(f"[{self.get_code()}] Thiếu dữ liệu đầu vào: giai_5_6={giai_5_6}, giai_7_3={giai_7_3}, giai_5_4={giai_5_4}")
            return {'three_digits_special': []}
        
        try:
            # Số thứ từ giải 5.6: số thứ 3 và bóng
            # Ví dụ: 2349 -> số thứ 3 = 4, bóng là 9
            if len(giai_5_6) >= 3:
                digit_third = giai_5_6[2]
                first_nums = [digit_third, str(get_ball_number(int(digit_third)))]
            else:
                logger.warning(f"[{self.get_code()}] Giải 5.6 không đủ dài: {giai_5_6}")
                return {'three_digits_special': []}
                
            # Số thứ hai từ giải 7.3: số thứ 1 và bóng
            # Ví dụ: 32 -> số thứ 1 = 3, bóng là 8
            if len(giai_7_3) >= 1:
                digit_first = giai_7_3[0]
                second_nums = [digit_first, str(get_ball_number(int(digit_first)))]
            else:
                logger.warning(f"[{self.get_code()}] Giải 7.3 không đủ dài: {giai_7_3}")
                return {'three_digits_special': []}
            
            # Tạo các cặp số 2 chữ số (bao gồm cả cặp đảo ngược)
            two_digits = []
            for first in first_nums:
                for second in second_nums:
                    two_digits.append(f"{first}{second}")
                    two_digits.append(f"{second}{first}")
            
            # Càng đề từ giải 5.4: tổng số thứ 3 và 4, lấy bóng
            # Ví dụ: 2628 -> 2+8=10 -> 0, bóng là 5
            if len(giai_5_4) >= 4:
                sum_third_fourth = (int(giai_5_4[2]) + int(giai_5_4[3])) % 10
                cang_nums = [str(sum_third_fourth), str(get_ball_number(sum_third_fourth))]
            else:
                logger.warning(f"[{self.get_code()}] Giải 5.4 không đủ dài: {giai_5_4}")
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
            logger.error(f"[{self.get_code()}] Lỗi tính 115 đề 3 số: {str(e)}")
            return {'three_digits_special': []}