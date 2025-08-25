from typing import Dict, List, Any
from .base import BasePredictionMethod
from .utils import get_ball_number
import logging

logger = logging.getLogger(__name__)

class De59TwoDigitMethod(BasePredictionMethod):
    """
    Phương pháp 59 Đề 2 số
    Dự đoán từ giải 3.3 (số thứ 1) và giải 4.2 (số thứ 4 - chạm đề)
    Tạo các cặp số có tổng bằng số thứ 1 của giải 3.3 với chạm đề
    """
    def get_code(self) -> str:
        return "de59_2d"
    
    def get_name(self) -> str:
        return "59 Đề 2 số"
    
    def get_description(self) -> str:
        return "Dự đoán 2 số từ giải 3.3 (số thứ 1) và giải 4.2 (số thứ 4 - chạm đề)"
    
    def calculate(self, data: Dict[str, Any]) -> Dict[str, List[str]]:
        giai_3_3 = data.get('giai_3_3', '')
        giai_4_2 = data.get('giai_4_2', '')
        
        if not giai_3_3 or not giai_4_2:
            logger.warning(f"[{self.get_code()}] Thiếu dữ liệu đầu vào: giai_3_3={giai_3_3}, giai_4_2={giai_4_2}")
            return {'two_digits_special': []}
        
        try:
            # Số tổng từ giải 3.3: số thứ 1 và bóng
            if len(giai_3_3) >= 1:
                first_digit = int(giai_3_3[0])
                sum_targets = [first_digit, get_ball_number(first_digit)]
            else:
                logger.warning(f"[{self.get_code()}] Giải 3.3 không đủ dài: {giai_3_3}")
                return {'two_digits_special': []}
                
            # Chạm đề từ giải 4.2: số thứ 4 và bóng
            if len(giai_4_2) >= 4:
                cham_de = int(giai_4_2[3])
                cham_de_targets = [cham_de, get_ball_number(cham_de)]
            else:
                logger.warning(f"[{self.get_code()}] Giải 4.2 không đủ dài: {giai_4_2}")
                return {'two_digits_special': []}
            
            # Tạo các cặp số 2 chữ số có tổng bằng số tổng đích
            two_digits = set()
            for sum_target in sum_targets:
                for cham in cham_de_targets:
                    # Tìm các số từ 0-9 mà khi cộng với chạm đề thì bằng sum_target (mod 10)
                    for i in range(10):
                        if (i + cham) % 10 == sum_target:
                            # Thêm cặp số thẳng và đảo ngược
                            two_digits.add(f"{i}{cham}")
                            two_digits.add(f"{cham}{i}")
            
            logger.info(f"[{self.get_code()}] Kết quả: {sorted(list(two_digits))}")
            return {
                'two_digits_special': sorted(list(two_digits))
            }
        except (ValueError, IndexError, TypeError) as e:
            logger.error(f"[{self.get_code()}] Lỗi tính 59 đề 2 số: {str(e)}")
            return {'two_digits_special': []}


class De59ThreeDigitMethod(BasePredictionMethod):
    """
    Phương pháp 59 Đề 3 số
    Dự đoán từ giải 3.3, 4.2 và giải 6.1 (càng đề)
    """
    def get_code(self) -> str:
        return "de59_3d"
    
    def get_name(self) -> str:
        return "59 Đề 3 số"
    
    def get_description(self) -> str:
        return "Dự đoán 3 số từ giải 3.3, 4.2 và giải 6.1 (càng đề)"
    
    def calculate(self, data: Dict[str, Any]) -> Dict[str, List[str]]:
        giai_3_3 = data.get('giai_3_3', '')
        giai_4_2 = data.get('giai_4_2', '')
        giai_6_1 = data.get('giai_6_1', '')
        
        if not giai_3_3 or not giai_4_2 or not giai_6_1:
            logger.warning(f"[{self.get_code()}] Thiếu dữ liệu đầu vào: giai_3_3={giai_3_3}, giai_4_2={giai_4_2}, giai_6_1={giai_6_1}")
            return {'three_digits_special': []}
        
        try:
            # Tính các cặp số 2 chữ số từ giải 3.3 và 4.2
            if len(giai_3_3) >= 1:
                first_digit = int(giai_3_3[0])
                sum_targets = [first_digit, get_ball_number(first_digit)]
            else:
                logger.warning(f"[{self.get_code()}] Giải 3.3 không đủ dài: {giai_3_3}")
                return {'three_digits_special': []}
                
            if len(giai_4_2) >= 4:
                cham_de = int(giai_4_2[3])
                cham_de_targets = [cham_de, get_ball_number(cham_de)]
            else:
                logger.warning(f"[{self.get_code()}] Giải 4.2 không đủ dài: {giai_4_2}")
                return {'three_digits_special': []}
            
            # Tạo các cặp số 2 chữ số có tổng bằng số tổng đích
            two_digits = []
            for sum_target in sum_targets:
                for cham in cham_de_targets:
                    for i in range(10):
                        if (i + cham) % 10 == sum_target:
                            two_digits.append(f"{i}{cham}")
                            two_digits.append(f"{cham}{i}")
            
            # Càng đề từ giải 6.1: tổng số thứ 1 và số thứ 2, và bóng
            if len(giai_6_1) >= 2:
                sum_1_2 = (int(giai_6_1[0]) + int(giai_6_1[1])) % 10
                cang_de = str(sum_1_2)
                cang_de_bong = str(get_ball_number(sum_1_2))
                cang_nums = [cang_de, cang_de_bong]
            else:
                logger.warning(f"[{self.get_code()}] Giải 6.1 không đủ dài: {giai_6_1}")
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
            logger.error(f"[{self.get_code()}] Lỗi tính 59 đề 3 số: {str(e)}")
            return {'three_digits_special': []}