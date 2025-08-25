from typing import Dict, List, Any
from .base import BasePredictionMethod
from .utils import get_ball_number
import logging

logger = logging.getLogger(__name__)

class De107TwoDigitMethod(BasePredictionMethod):
    """
    Phương pháp 107 Đề 2 số
    Dự đoán từ giải 4.3 (tổng 2 số thứ 2 và 3 và bóng) và giải 5.4 (tổng 2 số đầu và bóng)
    """
    def get_code(self) -> str:
        return "de107_2d"
    
    def get_name(self) -> str:
        return "107 Đề 2 số"
    
    def get_description(self) -> str:
        return "Dự đoán 2 số từ giải 4.3 và giải 5.4"
    
    def calculate(self, data: Dict[str, Any]) -> Dict[str, List[str]]:
        giai_4_3 = data.get('giai_4_3', '')
        giai_5_4 = data.get('giai_5_4', '')
        
        if not giai_4_3 or not giai_5_4:
            logger.warning(f"[{self.get_code()}] Thiếu dữ liệu đầu vào: giai_4_3={giai_4_3}, giai_5_4={giai_5_4}")
            return {'two_digits_special': []}
        
        try:
            # Số thứ nhất từ giải 4.3: tổng 2 số thứ 2 và thứ 3 và bóng của nó
            # Ví dụ: 1859 -> 8+5=13 -> 3 và bóng là 8
            if len(giai_4_3) >= 4:
                sum_second_third = (int(giai_4_3[1]) + int(giai_4_3[2])) % 10
                first_nums = [str(sum_second_third), str(get_ball_number(sum_second_third))]
            else:
                logger.warning(f"[{self.get_code()}] Giải 4.3 không đủ dài: {giai_4_3}")
                return {'two_digits_special': []}
                
            # Số thứ 2 từ giải 5.4: tổng 2 số đầu và bóng của nó
            # Ví dụ: 3226 -> 3+2=5 và bóng là 0
            if len(giai_5_4) >= 2:
                sum_first_two = (int(giai_5_4[0]) + int(giai_5_4[1])) % 10
                second_nums = [str(sum_first_two), str(get_ball_number(sum_first_two))]
            else:
                logger.warning(f"[{self.get_code()}] Giải 5.4 không đủ dài: {giai_5_4}")
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
            logger.error(f"[{self.get_code()}] Lỗi tính 107 đề 2 số: {str(e)}")
            return {'two_digits_special': []}


class De107ThreeDigitMethod(BasePredictionMethod):
    """
    Phương pháp 107 Đề 3 số
    Dự đoán từ giải 4.3, 5.4 và giải 3.4 (chạm đề)
    """
    def get_code(self) -> str:
        return "de107_3d"
    
    def get_name(self) -> str:
        return "107 Đề 3 số"
    
    def get_description(self) -> str:
        return "Dự đoán 3 số từ giải 4.3, 5.4 và giải 3.4 (chạm đề)"
    
    def calculate(self, data: Dict[str, Any]) -> Dict[str, List[str]]:
        giai_4_3 = data.get('giai_4_3', '')
        giai_5_4 = data.get('giai_5_4', '')
        giai_3_4 = data.get('giai_3_4', '')
        
        if not giai_4_3 or not giai_5_4 or not giai_3_4:
            logger.warning(f"[{self.get_code()}] Thiếu dữ liệu đầu vào: giai_4_3={giai_4_3}, giai_5_4={giai_5_4}, giai_3_4={giai_3_4}")
            return {'three_digits_special': []}
        
        try:
            # Tính các cặp số 2 chữ số từ giải 4.3 và 5.4
            if len(giai_4_3) >= 4:
                sum_second_third = (int(giai_4_3[1]) + int(giai_4_3[2])) % 10
                first_nums = [str(sum_second_third), str(get_ball_number(sum_second_third))]
            else:
                logger.warning(f"[{self.get_code()}] Giải 4.3 không đủ dài: {giai_4_3}")
                return {'three_digits_special': []}
                
            if len(giai_5_4) >= 2:
                sum_first_two = (int(giai_5_4[0]) + int(giai_5_4[1])) % 10
                second_nums = [str(sum_first_two), str(get_ball_number(sum_first_two))]
            else:
                logger.warning(f"[{self.get_code()}] Giải 5.4 không đủ dài: {giai_5_4}")
                return {'three_digits_special': []}
            
            # Tạo các cặp số 2 chữ số (bao gồm cả cặp đảo ngược)
            two_digits = []
            for first in first_nums:
                for second in second_nums:
                    # Thêm cặp số thẳng
                    two_digits.append(f"{first}{second}")
                    # Thêm cặp số đảo ngược
                    two_digits.append(f"{second}{first}")
            
            # Chạm đề từ giải 3.4: số thứ 3
            if len(giai_3_4) >= 3:
                cham_de = giai_3_4[2]  # Lấy số thứ 3, ví dụ: 72091 -> 0
                cham_de_bong = str(get_ball_number(int(cham_de)))
                cham_nums = [cham_de, cham_de_bong]
            else:
                logger.warning(f"[{self.get_code()}] Giải 3.4 không đủ dài: {giai_3_4}")
                return {'three_digits_special': []}
            
            # Tạo các cặp số 3 chữ số
            three_digits = set()
            for cham in cham_nums:
                for two_digit in two_digits:
                    three_digits.add(f"{cham}{two_digit}")
            
            logger.info(f"[{self.get_code()}] Kết quả: {sorted(list(three_digits))}")
            return {
                'three_digits_special': sorted(list(three_digits))
            }
        except (ValueError, IndexError, TypeError) as e:
            logger.error(f"[{self.get_code()}] Lỗi tính 107 đề 3 số: {str(e)}")
            return {'three_digits_special': []}