from typing import Dict, List, Any
from .base import BasePredictionMethod
from .utils import get_ball_number
import logging

logger = logging.getLogger(__name__)

class De118TwoDigitMethod(BasePredictionMethod):
    """
    Phương pháp 118 Đề 2 số
    Dự đoán từ tổng giải 5.6 (số thứ 1 và 2), chạm đề 1 từ giải 3.2 (số thứ 5), chạm đề 2 từ giải 4.1 (số thứ 4)
    """
    def get_code(self) -> str:
        return "de118_2d"
    
    def get_name(self) -> str:
        return "118 Đề 2 số"
    
    def get_description(self) -> str:
        return "Dự đoán 2 số từ tổng giải 5.6 (số thứ 1 và 2), chạm đề 1 từ giải 3.2 (số thứ 5), chạm đề 2 từ giải 4.1 (số thứ 4)"
    
    def calculate(self, data: Dict[str, Any]) -> Dict[str, List[str]]:
        giai_5_6 = data.get('giai_5_6', '')
        giai_3_2 = data.get('giai_3_2', '')
        giai_4_1 = data.get('giai_4_1', '')
        
        if not giai_5_6 or not giai_3_2 or not giai_4_1:
            logger.warning(f"[{self.get_code()}] Thiếu dữ liệu đầu vào: giai_5_6={giai_5_6}, giai_3_2={giai_3_2}, giai_4_1={giai_4_1}")
            return {'two_digits_special': []}
        
        try:
            # Tổng từ giải 5.6: tổng số thứ 1 và số thứ 2, lấy số cuối
            # Ví dụ: 5361 -> số thứ 1 = 5, số thứ 2 = 3 -> tổng = 8
            if len(giai_5_6) >= 2:
                digit_first = int(giai_5_6[0])
                digit_second = int(giai_5_6[1])
                target_sum = (digit_first + digit_second) % 10  # Lấy số cuối của tổng
            else:
                logger.warning(f"[{self.get_code()}] Giải 5.6 không đủ dài: {giai_5_6}")
                return {'two_digits_special': []}
                
            # Chạm đề 1 từ giải 3.2: số thứ 5
            # Ví dụ: 12371 -> số thứ 5 = 1
            if len(giai_3_2) >= 5:
                cham_de_1 = int(giai_3_2[4])
            else:
                logger.warning(f"[{self.get_code()}] Giải 3.2 không đủ dài: {giai_3_2}")
                return {'two_digits_special': []}
                
            # Chạm đề 2 từ giải 4.1: số thứ 4
            # Ví dụ: 1232 -> số thứ 4 = 2
            if len(giai_4_1) >= 4:
                cham_de_2 = int(giai_4_1[3])
            else:
                logger.warning(f"[{self.get_code()}] Giải 4.1 không đủ dài: {giai_4_1}")
                return {'two_digits_special': []}
            
            # Tạo các cặp số 2 chữ số có tổng bằng target_sum, sử dụng chạm đề 1 và 2
            two_digits = set()
            for cham in [cham_de_1, cham_de_2]:
                # Tìm số còn lại để tổng bằng target_sum
                complement = (target_sum - cham) % 10
                # Tạo cặp số và cặp đảo ngược
                two_digits.add(f"{cham}{complement}")
                two_digits.add(f"{complement}{cham}")
            
            logger.info(f"[{self.get_code()}] Kết quả: {sorted(list(two_digits))}")
            return {
                'two_digits_special': sorted(list(two_digits))
            }
        except (ValueError, IndexError, TypeError) as e:
            logger.error(f"[{self.get_code()}] Lỗi tính 118 đề 2 số: {str(e)}")
            return {'two_digits_special': []}

class De118ThreeDigitMethod(BasePredictionMethod):
    """
    Phương pháp 118 Đề 3 số
    Dự đoán từ tổng giải 5.6 (số thứ 1 và 2), chạm đề 1 từ giải 3.2 (số thứ 5), chạm đề 2 từ giải 4.1 (số thứ 4), và giải 1 (càng đề từ số thứ 1)
    """
    def get_code(self) -> str:
        return "de118_3d"
    
    def get_name(self) -> str:
        return "118 Đề 3 số"
    
    def get_description(self) -> str:
        return "Dự đoán 3 số từ tổng giải 5.6 (số thứ 1 và 2), chạm đề 1 từ giải 3.2 (số thứ 5), chạm đề 2 từ giải 4.1 (số thứ 4), và giải 1 (càng đề)"
    
    def calculate(self, data: Dict[str, Any]) -> Dict[str, List[str]]:
        giai_5_6 = data.get('giai_5_6', '')
        giai_3_2 = data.get('giai_3_2', '')
        giai_4_1 = data.get('giai_4_1', '')
        giai_1 = data.get('giai_1', '')
        
        if not giai_5_6 or not giai_3_2 or not giai_4_1 or not giai_1:
            logger.warning(f"[{self.get_code()}] Thiếu dữ liệu đầu vào: giai_5_6={giai_5_6}, giai_3_2={giai_3_2}, giai_4_1={giai_4_1}, giai_1={giai_1}")
            return {'three_digits_special': []}
        
        try:
            # Tổng từ giải 5.6: tổng số thứ 1 và số thứ 2, lấy số cuối
            # Ví dụ: 5361 -> số thứ 1 = 5, số thứ 2 = 3 -> tổng = 8
            if len(giai_5_6) >= 2:
                digit_first = int(giai_5_6[0])
                digit_second = int(giai_5_6[1])
                target_sum = (digit_first + digit_second) % 10  # Lấy số cuối của tổng
            else:
                logger.warning(f"[{self.get_code()}] Giải 5.6 không đủ dài: {giai_5_6}")
                return {'three_digits_special': []}
                
            # Chạm đề 1 từ giải 3.2: số thứ 5
            # Ví dụ: 12371 -> số thứ 5 = 1
            if len(giai_3_2) >= 5:
                cham_de_1 = int(giai_3_2[4])
            else:
                logger.warning(f"[{self.get_code()}] Giải 3.2 không đủ dài: {giai_3_2}")
                return {'three_digits_special': []}
                
            # Chạm đề 2 từ giải 4.1: số thứ 4
            # Ví dụ: 1232 -> số thứ 4 = 2
            if len(giai_4_1) >= 4:
                cham_de_2 = int(giai_4_1[3])
            else:
                logger.warning(f"[{self.get_code()}] Giải 4.1 không đủ dài: {giai_4_1}")
                return {'three_digits_special': []}
            
            # Tạo các cặp số 2 chữ số có tổng bằng target_sum, sử dụng chạm đề 1 và 2
            two_digits = []
            for cham in [cham_de_1, cham_de_2]:
                complement = (target_sum - cham) % 10
                two_digits.append(f"{cham}{complement}")
                two_digits.append(f"{complement}{cham}")
            
            # Càng đề từ giải 1: số thứ 1 và bóng
            # Ví dụ: 34185 -> số thứ 1 = 3, bóng là 8
            if len(giai_1) >= 1:
                digit_first_cang = giai_1[0]
                cang_nums = [digit_first_cang, str(get_ball_number(int(digit_first_cang)))]
            else:
                logger.warning(f"[{self.get_code()}] Giải 1 không đủ dài: {giai_1}")
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
            logger.error(f"[{self.get_code()}] Lỗi tính 118 đề 3 số: {str(e)}")
            return {'three_digits_special': []}