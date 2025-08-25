from typing import Dict, List, Any
from .base import BasePredictionMethod
from .utils import get_ball_number
import logging

logger = logging.getLogger(__name__)

class De101TwoDigitMethod(BasePredictionMethod):
    """
    Phương pháp 101 Đề 2 số
    Dự đoán từ giải 3.1 + 3.4 (số thứ 1) và giải 3.3 (số thứ 5)
    """
    def get_code(self) -> str:
        return "de101_2d"
    
    def get_name(self) -> str:
        return "101 Đề 2 số"
    
    def get_description(self) -> str:
        return "Dự đoán 2 số từ tổng giải 3.1+3.4 và giải 3.3 (số thứ 5)"
    
    def calculate(self, data: Dict[str, Any]) -> Dict[str, List[str]]:
        giai_3_1 = data.get('giai_3_1', '')
        giai_3_3 = data.get('giai_3_3', '')
        giai_3_4 = data.get('giai_3_4', '')
        
        if not giai_3_1 or not giai_3_3 or not giai_3_4:
            logger.warning(f"[{self.get_code()}] Thiếu dữ liệu đầu vào: giai_3_1={giai_3_1}, giai_3_3={giai_3_3}, giai_3_4={giai_3_4}")
            return {'two_digits_special': []}
        
        try:
            # Số thứ nhất: tổng số thứ 1 của giải 3.1 và 3.4, và bóng
            if len(giai_3_1) >= 1 and len(giai_3_4) >= 1:
                sum_first = (int(giai_3_1[0]) + int(giai_3_4[0])) % 10
                first_nums = [str(sum_first), str(get_ball_number(sum_first))]
            else:
                logger.warning(f"[{self.get_code()}] Giải 3.1 hoặc 3.4 không đủ dài: 3.1={giai_3_1}, 3.4={giai_3_4}")
                return {'two_digits_special': []}
                
            # Số thứ 2 từ giải 3.3: số thứ 5 và bóng
            if len(giai_3_3) >= 5:
                digit_fifth = giai_3_3[4]
                second_nums = [digit_fifth, str(get_ball_number(int(digit_fifth)))]
            else:
                logger.warning(f"[{self.get_code()}] Giải 3.3 không đủ dài: {giai_3_3}")
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
            logger.error(f"[{self.get_code()}] Lỗi tính 101 đề 2 số: {str(e)}")
            return {'two_digits_special': []}


class De101ThreeDigitMethod(BasePredictionMethod):
    """
    Phương pháp 101 Đề 3 số
    Dự đoán từ giải 3.1+3.4, 3.3 và giải 6.3 (càng đề)
    """
    def get_code(self) -> str:
        return "de101_3d"
    
    def get_name(self) -> str:
        return "101 Đề 3 số"
    
    def get_description(self) -> str:
        return "Dự đoán 3 số từ tổng giải 3.1+3.4, 3.3 và giải 6.3 (càng đề)"
    
    def calculate(self, data: Dict[str, Any]) -> Dict[str, List[str]]:
        giai_3_1 = data.get('giai_3_1', '')
        giai_3_3 = data.get('giai_3_3', '')
        giai_3_4 = data.get('giai_3_4', '')
        giai_6_3 = data.get('giai_6_3', '')
        
        if not giai_3_1 or not giai_3_3 or not giai_3_4 or not giai_6_3:
            logger.warning(f"[{self.get_code()}] Thiếu dữ liệu đầu vào: giai_3_1={giai_3_1}, giai_3_3={giai_3_3}, giai_3_4={giai_3_4}, giai_6_3={giai_6_3}")
            return {'three_digits_special': []}
        
        try:
            # Tính các cặp số 2 chữ số từ giải 3.1+3.4 và 3.3
            if len(giai_3_1) >= 1 and len(giai_3_4) >= 1:
                sum_first = (int(giai_3_1[0]) + int(giai_3_4[0])) % 10
                first_nums = [str(sum_first), str(get_ball_number(sum_first))]
            else:
                logger.warning(f"[{self.get_code()}] Giải 3.1 hoặc 3.4 không đủ dài: 3.1={giai_3_1}, 3.4={giai_3_4}")
                return {'three_digits_special': []}
                
            if len(giai_3_3) >= 5:
                digit_fifth = giai_3_3[4]
                second_nums = [digit_fifth, str(get_ball_number(int(digit_fifth)))]
            else:
                logger.warning(f"[{self.get_code()}] Giải 3.3 không đủ dài: {giai_3_3}")
                return {'three_digits_special': []}
            
            # Tạo các cặp số 2 chữ số (bao gồm cả cặp đảo ngược)
            two_digits = []
            for first in first_nums:
                for second in second_nums:
                    two_digits.append(f"{first}{second}")
                    two_digits.append(f"{second}{first}")
            
            # Càng đề từ giải 6.3: tổng số thứ 1 và số thứ 2, và bóng
            if len(giai_6_3) >= 2:
                sum_1_2 = (int(giai_6_3[0]) + int(giai_6_3[1])) % 10
                cang_de = str(sum_1_2)
                cang_de_bong = str(get_ball_number(sum_1_2))
                cang_nums = [cang_de, cang_de_bong]
            else:
                logger.warning(f"[{self.get_code()}] Giải 6.3 không đủ dài: {giai_6_3}")
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
            logger.error(f"[{self.get_code()}] Lỗi tính 101 đề 3 số: {str(e)}")
            return {'three_digits_special': []}