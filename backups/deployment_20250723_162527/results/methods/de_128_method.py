from typing import Dict, List, Any
from .base import BasePredictionMethod
from .utils import get_ball_number
import logging

logger = logging.getLogger(__name__)

class De128TwoDigitMethod(BasePredictionMethod):
    """
    Phương pháp 128 Đề 2 số
    Dự đoán từ giải 7.1 (số thứ 2 và bóng), giải 6.1 (số thứ 2 và bóng), giải 6.3 (số thứ 2 và bóng)
    """
    def get_code(self) -> str:
        return "de128_2d"
    
    def get_name(self) -> str:
        return "128 Đề 2 số"
    
    def get_description(self) -> str:
        return "Dự đoán 2 số từ giải 7.1 (số thứ 2), giải 6.1 (số thứ 2), giải 6.3 (số thứ 2)"
    
    def calculate(self, data: Dict[str, Any]) -> Dict[str, List[str]]:
        giai_7_1 = data.get('giai_7_1', '')
        giai_6_1 = data.get('giai_6_1', '')
        giai_6_3 = data.get('giai_6_3', '')
        
        if not giai_7_1 or not giai_6_1 or not giai_6_3:
            logger.warning(f"[{self.get_code()}] Thiếu dữ liệu đầu vào: giai_7_1={giai_7_1}, giai_6_1={giai_6_1}, giai_6_3={giai_6_3}")
            return {'two_digits_special': []}
        
        try:
            # Số thứ nhất từ giải 7.1: số thứ 2 và bóng
            # Ví dụ: 23 -> số thứ 2 = 3, bóng là 8
            if len(giai_7_1) >= 2:
                digit_second = giai_7_1[1]
                first_nums = [digit_second, str(get_ball_number(int(digit_second)))]
            else:
                logger.warning(f"[{self.get_code()}] Giải 7.1 không đủ dài: {giai_7_1}")
                return {'two_digits_special': []}
                
            # Số thứ hai từ giải 6.1: số thứ 2 và bóng
            # Ví dụ: 325 -> số thứ 2 = 2, bóng là 7
            if len(giai_6_1) >= 2:
                digit_second = giai_6_1[1]
                second_nums = [digit_second, str(get_ball_number(int(digit_second)))]
            else:
                logger.warning(f"[{self.get_code()}] Giải 6.1 không đủ dài: {giai_6_1}")
                return {'two_digits_special': []}
                
            # Số thứ ba từ giải 6.3: số thứ 2 và bóng
            # Ví dụ: 365 -> số thứ 2 = 6, bóng là 1
            if len(giai_6_3) >= 2:
                digit_second = giai_6_3[1]
                third_nums = [digit_second, str(get_ball_number(int(digit_second)))]
            else:
                logger.warning(f"[{self.get_code()}] Giải 6.3 không đủ dài: {giai_6_3}")
                return {'two_digits_special': []}
            
            # Tạo các cặp số 2 chữ số (ghép lần lượt: số 1 với số 2, số 1 với số 3, số 2 với số 3, và ngược lại)
            two_digits = set()
            # Ghép số thứ nhất với số thứ hai
            for first in first_nums:
                for second in second_nums:
                    two_digits.add(f"{first}{second}")
                    two_digits.add(f"{second}{first}")
            # Ghép số thứ nhất với số thứ ba
            for first in first_nums:
                for third in third_nums:
                    two_digits.add(f"{first}{third}")
                    two_digits.add(f"{third}{first}")
            # Ghép số thứ hai với số thứ ba
            for second in second_nums:
                for third in third_nums:
                    two_digits.add(f"{second}{third}")
                    two_digits.add(f"{third}{second}")
            
            logger.info(f"[{self.get_code()}] Kết quả: {sorted(list(two_digits))}")
            return {
                'two_digits_special': sorted(list(two_digits))
            }
        except (ValueError, IndexError, TypeError) as e:
            logger.error(f"[{self.get_code()}] Lỗi tính 128 đề 2 số: {str(e)}")
            return {'two_digits_special': []}

class De128ThreeDigitMethod(BasePredictionMethod):
    """
    Phương pháp 128 Đề 3 số
    Dự đoán từ giải 7.1 (số thứ 2 và bóng), giải 6.1 (số thứ 2 và bóng), giải 6.3 (số thứ 2 và bóng), và giải 4.2 (càng đề từ số thứ 2)
    """
    def get_code(self) -> str:
        return "de128_3d"
    
    def get_name(self) -> str:
        return "128 Đề 3 số"
    
    def get_description(self) -> str:
        return "Dự đoán 3 số từ giải 7.1 (số thứ 2), giải 6.1 (số thứ 2), giải 6.3 (số thứ 2), và giải 4.2 (càng đề)"
    
    def calculate(self, data: Dict[str, Any]) -> Dict[str, List[str]]:
        giai_7_1 = data.get('giai_7_1', '')
        giai_6_1 = data.get('giai_6_1', '')
        giai_6_3 = data.get('giai_6_3', '')
        giai_4_2 = data.get('giai_4_2', '')
        
        if not giai_7_1 or not giai_6_1 or not giai_6_3 or not giai_4_2:
            logger.warning(f"[{self.get_code()}] Thiếu dữ liệu đầu vào: giai_7_1={giai_7_1}, giai_6_1={giai_6_1}, giai_6_3={giai_6_3}, giai_4_2={giai_4_2}")
            return {'three_digits_special': []}
        
        try:
            # Số thứ nhất từ giải 7.1: số thứ 2 và bóng
            # Ví dụ: 23 -> số thứ 2 = 3, bóng là 8
            if len(giai_7_1) >= 2:
                digit_second = giai_7_1[1]
                first_nums = [digit_second, str(get_ball_number(int(digit_second)))]
            else:
                logger.warning(f"[{self.get_code()}] Giải 7.1 không đủ dài: {giai_7_1}")
                return {'three_digits_special': []}
                
            # Số thứ hai từ giải 6.1: số thứ 2 và bóng
            # Ví dụ: 325 -> số thứ 2 = 2, bóng là 7
            if len(giai_6_1) >= 2:
                digit_second = giai_6_1[1]
                second_nums = [digit_second, str(get_ball_number(int(digit_second)))]
            else:
                logger.warning(f"[{self.get_code()}] Giải 6.1 không đủ dài: {giai_6_1}")
                return {'three_digits_special': []}
                
            # Số thứ ba từ giải 6.3: số thứ 2 và bóng
            # Ví dụ: 365 -> số thứ 2 = 6, bóng là 1
            if len(giai_6_3) >= 2:
                digit_second = giai_6_3[1]
                third_nums = [digit_second, str(get_ball_number(int(digit_second)))]
            else:
                logger.warning(f"[{self.get_code()}] Giải 6.3 không đủ dài: {giai_6_3}")
                return {'three_digits_special': []}
            
            # Tạo các cặp số 2 chữ số (ghép lần lượt: số 1 với số 2, số 1 với số 3, số 2 với số 3, và ngược lại)
            two_digits = []
            # Ghép số thứ nhất với số thứ hai
            for first in first_nums:
                for second in second_nums:
                    two_digits.append(f"{first}{second}")
                    two_digits.append(f"{second}{first}")
            # Ghép số thứ nhất với số thứ ba
            for first in first_nums:
                for third in third_nums:
                    two_digits.append(f"{first}{third}")
                    two_digits.append(f"{third}{first}")
            # Ghép số thứ hai với số thứ ba
            for second in second_nums:
                for third in third_nums:
                    two_digits.append(f"{second}{third}")
                    two_digits.append(f"{third}{second}")
            
            # Càng đề từ giải 4.2: số thứ 2 và bóng
            # Ví dụ: 2628 -> số thứ 2 = 6, bóng là 1
            if len(giai_4_2) >= 2:
                digit_second_cang = giai_4_2[1]
                cang_nums = [digit_second_cang, str(get_ball_number(int(digit_second_cang)))]
            else:
                logger.warning(f"[{self.get_code()}] Giải 4.2 không đủ dài: {giai_4_2}")
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
            logger.error(f"[{self.get_code()}] Lỗi tính 128 đề 3 số: {str(e)}")
            return {'three_digits_special': []}