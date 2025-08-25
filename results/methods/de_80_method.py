from typing import Dict, List, Any
from .base import BasePredictionMethod
from .utils import get_ball_number
import logging

logger = logging.getLogger(__name__)

class De80TwoDigitMethod(BasePredictionMethod):
    """
    Phương pháp 80 Đề 2 số
    Dự đoán từ giải 1 (tổng số thứ 2 và 3, không lấy bóng) và giải 3.3 (số thứ 2 và bóng)
    """
    def get_code(self) -> str:
        return "de80_2d"
    
    def get_name(self) -> str:
        return "80 Đề 2 số"
    
    def get_description(self) -> str:
        return "Dự đoán 2 số từ giải 1 và giải 3.3"
    
    def calculate(self, data: Dict[str, Any]) -> Dict[str, List[str]]:
        giai_1 = data.get('giai_1', '')
        giai_3_3 = data.get('giai_3_3', '')
        
        if not giai_1 or not giai_3_3:
            logger.warning(f"[{self.get_code()}] Thiếu dữ liệu đầu vào: giai_1={giai_1}, giai_3_3={giai_3_3}")
            return {'two_digits_special': []}
        
        try:
            # Số thứ nhất từ giải 1: tổng số thứ 2 và số thứ 3, không lấy bóng
            # Ví dụ: 23496 -> 3+4=7
            if len(giai_1) >= 3:
                sum_second_third = (int(giai_1[1]) + int(giai_1[2])) % 10
                first_nums = [str(sum_second_third)]  # Không lấy bóng
            else:
                logger.warning(f"[{self.get_code()}] Giải 1 không đủ dài: {giai_1}")
                return {'two_digits_special': []}
                
            # Số thứ 2 từ giải 3.3: số thứ 2 và bóng
            # Ví dụ: 91346 -> số thứ 2 = 1 và bóng là 6
            if len(giai_3_3) >= 2:
                digit_second = giai_3_3[1]
                second_nums = [digit_second, str(get_ball_number(int(digit_second)))]
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
            logger.error(f"[{self.get_code()}] Lỗi tính 80 đề 2 số: {str(e)}")
            return {'two_digits_special': []}


class De80ThreeDigitMethod(BasePredictionMethod):
    """
    Phương pháp 80 Đề 3 số
    Dự đoán từ giải 1, 3.3 và giải 5.4 (càng đề)
    """
    def get_code(self) -> str:
        return "de80_3d"
    
    def get_name(self) -> str:
        return "80 Đề 3 số"
    
    def get_description(self) -> str:
        return "Dự đoán 3 số từ giải 1, 3.3 và giải 5.4 (càng đề)"
    
    def calculate(self, data: Dict[str, Any]) -> Dict[str, List[str]]:
        giai_1 = data.get('giai_1', '')
        giai_3_3 = data.get('giai_3_3', '')
        giai_5_4 = data.get('giai_5_4', '')
        
        if not giai_1 or not giai_3_3 or not giai_5_4:
            logger.warning(f"[{self.get_code()}] Thiếu dữ liệu đầu vào: giai_1={giai_1}, giai_3_3={giai_3_3}, giai_5_4={giai_5_4}")
            return {'three_digits_special': []}
        
        try:
            # Tính các cặp số 2 chữ số từ giải 1 và 3.3
            if len(giai_1) >= 3:
                sum_second_third = (int(giai_1[1]) + int(giai_1[2])) % 10
                first_nums = [str(sum_second_third)]  # Không lấy bóng
            else:
                logger.warning(f"[{self.get_code()}] Giải 1 không đủ dài: {giai_1}")
                return {'three_digits_special': []}
                
            if len(giai_3_3) >= 2:
                digit_second = giai_3_3[1]
                second_nums = [digit_second, str(get_ball_number(int(digit_second)))]
            else:
                logger.warning(f"[{self.get_code()}] Giải 3.3 không đủ dài: {giai_3_3}")
                return {'three_digits_special': []}
            
            # Tạo các cặp số 2 chữ số (bao gồm cả cặp đảo ngược)
            two_digits = []
            for first in first_nums:
                for second in second_nums:
                    # Thêm cặp số thẳng
                    two_digits.append(f"{first}{second}")
                    # Thêm cặp số đảo ngược
                    two_digits.append(f"{second}{first}")
            
            # Càng đề từ giải 5.4: số thứ 3 và bóng
            if len(giai_5_4) >= 3:
                cang_de = giai_5_4[2]  # Lấy số thứ 3, ví dụ: 1628 -> 2
                cang_de_bong = str(get_ball_number(int(cang_de)))
                cang_nums = [cang_de, cang_de_bong]
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
            logger.error(f"[{self.get_code()}] Lỗi tính 80 đề 3 số: {str(e)}")
            return {'three_digits_special': []}