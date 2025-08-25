from typing import Dict, List, Any
from .base import BasePredictionMethod
from .utils import get_ball_number
import logging

logger = logging.getLogger(__name__)

class De93TwoDigitMethod(BasePredictionMethod):
    """
    Phương pháp 93 Đề 2 số
    Dự đoán từ giải 3.1 (tổng số thứ 4 và 5) và giải 3.5 (số thứ 3)
    """
    def get_code(self) -> str:
        return "de93_2d"
    
    def get_name(self) -> str:
        return "93 Đề 2 số"
    
    def get_description(self) -> str:
        return "Dự đoán 2 số từ giải 3.1 (tổng số thứ 4,5) và giải 3.5 (số thứ 3)"
    
    def calculate(self, data: Dict[str, Any]) -> Dict[str, List[str]]:
        giai_3_1 = data.get('giai_3_1', '')
        giai_3_5 = data.get('giai_3_5', '')
        
        if not giai_3_1 or not giai_3_5:
            logger.warning(f"[{self.get_code()}] Thiếu dữ liệu đầu vào: giai_3_1={giai_3_1}, giai_3_5={giai_3_5}")
            return {'two_digits_special': []}
        
        try:
            # Số thứ nhất từ giải 3.1: tổng số thứ 4 và số thứ 5, và bóng
            if len(giai_3_1) >= 5:
                sum_4_5 = (int(giai_3_1[3]) + int(giai_3_1[4])) % 10
                first_nums = [str(sum_4_5), str(get_ball_number(sum_4_5))]
            else:
                logger.warning(f"[{self.get_code()}] Giải 3.1 không đủ dài: {giai_3_1}")
                return {'two_digits_special': []}
                
            # Số thứ 2 từ giải 3.5: số thứ 3 và bóng
            if len(giai_3_5) >= 3:
                digit_third = giai_3_5[2]
                second_nums = [digit_third, str(get_ball_number(int(digit_third)))]
            else:
                logger.warning(f"[{self.get_code()}] Giải 3.5 không đủ dài: {giai_3_5}")
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
            logger.error(f"[{self.get_code()}] Lỗi tính 93 đề 2 số: {str(e)}")
            return {'two_digits_special': []}


class De93ThreeDigitMethod(BasePredictionMethod):
    """
    Phương pháp 93 Đề 3 số
    Dự đoán từ giải 3.1, 3.5 và giải 1 (càng đề)
    """
    def get_code(self) -> str:
        return "de93_3d"
    
    def get_name(self) -> str:
        return "93 Đề 3 số"
    
    def get_description(self) -> str:
        return "Dự đoán 3 số từ giải 3.1, 3.5 và giải 1 (càng đề)"
    
    def calculate(self, data: Dict[str, Any]) -> Dict[str, List[str]]:
        giai_3_1 = data.get('giai_3_1', '')
        giai_3_5 = data.get('giai_3_5', '')
        giai_1 = data.get('giai_1', '')
        
        if not giai_3_1 or not giai_3_5 or not giai_1:
            logger.warning(f"[{self.get_code()}] Thiếu dữ liệu đầu vào: giai_3_1={giai_3_1}, giai_3_5={giai_3_5}, giai_1={giai_1}")
            return {'three_digits_special': []}
        
        try:
            # Tính các cặp số 2 chữ số từ giải 3.1 và 3.5
            if len(giai_3_1) >= 5:
                sum_4_5 = (int(giai_3_1[3]) + int(giai_3_1[4])) % 10
                first_nums = [str(sum_4_5), str(get_ball_number(sum_4_5))]
            else:
                logger.warning(f"[{self.get_code()}] Giải 3.1 không đủ dài: {giai_3_1}")
                return {'three_digits_special': []}
                
            if len(giai_3_5) >= 3:
                digit_third = giai_3_5[2]
                second_nums = [digit_third, str(get_ball_number(int(digit_third)))]
            else:
                logger.warning(f"[{self.get_code()}] Giải 3.5 không đủ dài: {giai_3_5}")
                return {'three_digits_special': []}
            
            # Tạo các cặp số 2 chữ số (bao gồm cả cặp đảo ngược)
            two_digits = []
            for first in first_nums:
                for second in second_nums:
                    # Thêm cặp số thẳng
                    two_digits.append(f"{first}{second}")
                    # Thêm cặp số đảo ngược
                    two_digits.append(f"{second}{first}")
            
            # Càng đề từ giải 1: tổng số thứ 5 và số thứ 6 (nếu có), hoặc chỉ số thứ 5 nếu giải 1 chỉ có 5 số
            if len(giai_1) >= 5:
                # Nếu giải 1 có 6 số (ví dụ: 123456)
                if len(giai_1) >= 6:
                    sum_5_6 = (int(giai_1[4]) + int(giai_1[5])) % 10
                else:
                    sum_5_6 = int(giai_1[4])  # Chỉ lấy số thứ 5 nếu giải 1 có 5 số
                
                cang_de = str(sum_5_6 % 10)
                cang_de_bong = str(get_ball_number(int(cang_de)))
                cang_nums = [cang_de, cang_de_bong]
            else:
                logger.warning(f"[{self.get_code()}] Giải 1 không đủ dài: {giai_1}")
                return {'three_digits_special': []}
            
            # Tạo các cặp số 3 chữ số
            three_digits = set()
            for cang in cang_nums:
                for two_digit in two_digits:
                    three_digits.add(f"{cang}{two_digit}")
                    # Có thể thêm cả đảo ngược nếu muốn
                    # three_digits.add(f"{two_digit}{cang}")
            
            logger.info(f"[{self.get_code()}] Kết quả: {sorted(list(three_digits))}")
            return {
                'three_digits_special': sorted(list(three_digits))
            }
        except (ValueError, IndexError, TypeError) as e:
            logger.error(f"[{self.get_code()}] Lỗi tính 93 đề 3 số: {str(e)}")
            return {'three_digits_special': []}