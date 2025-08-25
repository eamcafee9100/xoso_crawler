from typing import Dict, List, Any
from .base import BasePredictionMethod
from .utils import get_ball_number
import logging

logger = logging.getLogger(__name__)

class De24TwoDigitMethod(BasePredictionMethod):
    """
    Phương pháp 1 Đề 2 số
    Dự đoán từ giải 7.2.1+7.2.2 và giải 1.1.3 + 1.1.5
    """
    def get_code(self) -> str:
        return "de1_2d"
    
    def get_name(self) -> str:
        return "1 Đề 2 số"
    
    def get_description(self) -> str:
        return "Dự đoán 2 số từ giải 7.2.1+7.2.2 và giải 1.1.3 + 1.1.5"
    
    def calculate(self, data: Dict[str, Any]) -> Dict[str, List[str]]:
        giai_7_2_1 = data.get('giai_7_2_0', '')
        giai_7_2_2 = data.get('giai_7_2_1', '')
        giai_1_1_3 = data.get('giai_1_1_2', '')
        giai_1_1_5 = data.get('giai_1_1_4', '')

           
        try:
            digit_1 = giai_7_2_1 + giai_7_2_2
            ball_1 = get_ball_number(int(digit_1))
            digit_2 = giai_1_1_3 + giai_1_1_5
            ball_2 = get_ball_number(int(digit_2))
            
            
                
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

