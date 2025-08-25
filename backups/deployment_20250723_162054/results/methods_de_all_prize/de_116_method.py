from typing import Dict, List, Any
from .base import BasePredictionMethod
from .utils import get_ball_number
import logging

logger = logging.getLogger(__name__)

class De116TwoDigitMethod(BasePredictionMethod):
    """
    Phương pháp 116 Đề 2 số
    Dự đoán từ giải 5.6 (tổng số thứ 1 và 2), giải 7.2 (số thứ 2), giải 7.3 (số thứ 1)
    """
    def get_code(self) -> str:
        return "de116_2d"
    
    def get_name(self) -> str:
        return "116 Đề 2 số"
    
    def get_description(self) -> str:
        return "Dự đoán 2 số từ tổng giải 5.6 và chạm đề từ giải 7.2, 7.3"
    
    def calculate(self, data: Dict[str, Any]) -> Dict[str, List[str]]:
        giai_5_6 = data.get('giai_5_6', '')
        giai_7_2 = data.get('giai_7_2', '')
        giai_7_3 = data.get('giai_7_3', '')
        
        if not giai_5_6 or not giai_7_2 or not giai_7_3:
            logger.warning(f"[{self.get_code()}] Thiếu dữ liệu đầu vào: giai_5_6={giai_5_6}, giai_7_2={giai_7_2}, giai_7_3={giai_7_3}")
            return {'two_digits_special': []}
        
        try:
            # Tổng từ giải 5.6: tổng số thứ 1 và 2
            # Ví dụ: 5361 -> 5+3=8
            if len(giai_5_6) >= 2:
                total = (int(giai_5_6[0]) + int(giai_5_6[1])) % 10
            else:
                logger.warning(f"[{self.get_code()}] Giải 5.6 không đủ dài: {giai_5_6}")
                return {'two_digits_special': []}
                
            # Chạm đề 1 từ giải 7.2: số thứ 2
            # Ví dụ: 71 -> số thứ 2 = 1
            if len(giai_7_2) >= 2:
                cham_de_1 = int(giai_7_2[1])
            else:
                logger.warning(f"[{self.get_code()}] Giải 7.2 không đủ dài: {giai_7_2}")
                return {'two_digits_special': []}
                
            # Chạm đề 2 từ giải 7.3: số thứ 1
            # Ví dụ: 32 -> số thứ 1 = 3
            if len(giai_7_3) >= 1:
                cham_de_2 = int(giai_7_3[0])
            else:
                logger.warning(f"[{self.get_code()}] Giải 7.3 không đủ dài: {giai_7_3}")
                return {'two_digits_special': []}
            
            # Tạo các cặp số 2 chữ số: tìm số sao cho tổng với chạm đề bằng total
            # Ví dụ: total=8, cham_de_1=1 -> 1+x=8 -> x=7 -> 17, 71
            #        total=8, cham_de_2=3 -> 3+x=8 -> x=5 -> 35, 53
            two_digits = set()
            for cham in [cham_de_1, cham_de_2]:
                complement = (total - cham) % 10
                two_digits.add(f"{cham}{complement}")
                two_digits.add(f"{complement}{cham}")
            
            logger.info(f"[{self.get_code()}] Kết quả: {sorted(list(two_digits))}")
            return {
                'two_digits_special': sorted(list(two_digits))
            }
        except (ValueError, IndexError, TypeError) as e:
            logger.error(f"[{self.get_code()}] Lỗi tính 116 đề 2 số: {str(e)}")
            return {'two_digits_special': []}

class De116ThreeDigitMethod(BasePredictionMethod):
    """
    Phương pháp 116 Đề 3 số
    Dự đoán từ giải 5.6 (tổng số thứ 1 và 2), giải 7.2 (số thứ 2), giải 7.3 (số thứ 1), và giải 3.6 (càng đề)
    """
    def get_code(self) -> str:
        return "de116_3d"
    
    def get_name(self) -> str:
        return "116 Đề 3 số"
    
    def get_description(self) -> str:
        return "Dự đoán 3 số từ giải 5.6, 7.2, 7.3 và giải 3.6 (càng đề)"
    
    def calculate(self, data: Dict[str, Any]) -> Dict[str, List[str]]:
        giai_5_6 = data.get('giai_5_6', '')
        giai_7_2 = data.get('giai_7_2', '')
        giai_7_3 = data.get('giai_7_3', '')
        giai_3_6 = data.get('giai_3_6', '')
        
        if not giai_5_6 or not giai_7_2 or not giai_7_3 or not giai_3_6:
            logger.warning(f"[{self.get_code()}] Thiếu dữ liệu đầu vào: giai_5_6={giai_5_6}, giai_7_2={giai_7_2}, giai_7_3={giai_7_3}, giai_3_6={giai_3_6}")
            return {'three_digits_special': []}
        
        try:
            # Tổng từ giải 5.6: tổng số thứ 1 và 2
            # Ví dụ: 5361 -> 5+3=8
            if len(giai_5_6) >= 2:
                total = (int(giai_5_6[0]) + int(giai_5_6[1])) % 10
            else:
                logger.warning(f"[{self.get_code()}] Giải 5.6 không đủ dài: {giai_5_6}")
                return {'three_digits_special': []}
                
            # Chạm đề 1 từ giải 7.2: số thứ 2
            # Ví dụ: 71 -> số thứ 2 = 1
            if len(giai_7_2) >= 2:
                cham_de_1 = int(giai_7_2[1])
            else:
                logger.warning(f"[{self.get_code()}] Giải 7.2 không đủ dài: {giai_7_2}")
                return {'three_digits_special': []}
                
            # Chạm đề 2 từ giải 7.3: số thứ 1
            # Ví dụ: 32 -> số thứ 1 = 3
            if len(giai_7_3) >= 1:
                cham_de_2 = int(giai_7_3[0])
            else:
                logger.warning(f"[{self.get_code()}] Giải 7.3 không đủ dài: {giai_7_3}")
                return {'three_digits_special': []}
            
            # Tạo các cặp số 2 chữ số: tìm số sao cho tổng với chạm đề bằng total
            # Ví dụ: total=8, cham_de_1=1 -> 1+x=8 -> x=7 -> 17, 71
            #        total=8, cham_de_2=3 -> 3+x=8 -> x=5 -> 35, 53
            two_digits = []
            for cham in [cham_de_1, cham_de_2]:
                complement = (total - cham) % 10
                two_digits.append(f"{cham}{complement}")
                two_digits.append(f"{complement}{cham}")
            
            # Càng đề từ giải 3.6: số thứ 1 và bóng
            # Ví dụ: 34185 -> số thứ 1 = 3, bóng là 8
            if len(giai_3_6) >= 1:
                digit_first_cang = giai_3_6[0]
                cang_nums = [digit_first_cang, str(get_ball_number(int(digit_first_cang)))]
            else:
                logger.warning(f"[{self.get_code()}] Giải 3.6 không đủ dài: {giai_3_6}")
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
            logger.error(f"[{self.get_code()}] Lỗi tính 116 đề 3 số: {str(e)}")
            return {'three_digits_special': []}