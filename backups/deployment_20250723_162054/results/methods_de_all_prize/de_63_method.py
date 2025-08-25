from typing import Dict, List, Any
from .base import BasePredictionMethod
from .utils import get_ball_number
import logging

logger = logging.getLogger(__name__)

class De63TwoDigitMethod(BasePredictionMethod):
    """
    Phương pháp 63 Đề 2 số
    Dự đoán từ giải 3.5 (3 số cuối, số trùng đổi bóng) và giải 4.2 + 7.2 (số 3,4 của 4.2 và số 1,2 của 7.2)
    """
    def get_code(self) -> str:
        return "de63_2d"
    
    def get_name(self) -> str:
        return "63 Đề 2 số"
    
    def get_description(self) -> str:
        return "Dự đoán 2 số từ giải 3.5 và giải 4.2 + 7.2"
    
    def process_last_three_digits(self, number: str) -> List[str]:
        """Xử lý 3 số cuối, đổi số trùng thành bóng"""
        if len(number) < 3:
            return []
        
        # Lấy 3 số cuối
        last_three = number[-3:]
        result = []
        
        # Kiểm tra và xử lý số trùng
        seen = set()
        duplicates = set()
        
        # Tìm các số trùng
        for digit in last_three:
            if digit in seen:
                duplicates.add(digit)
            seen.add(digit)
        
        # Xử lý kết quả, đổi số trùng thành bóng
        for digit in last_three:
            if digit in duplicates:
                result.append(str(get_ball_number(int(digit))))
            else:
                result.append(digit)
        
        return result
    
    def process_combination(self, giai_4_2: str, giai_7_2: str) -> List[str]:
        """Xử lý số thứ 3, 4 của giải 4.2 và số thứ 1, 2 của giải 7.2"""
        result = []
        
        if len(giai_4_2) >= 4:
            if len(giai_4_2) >= 3:
                result.append(giai_4_2[2])  # Số thứ 3
            if len(giai_4_2) >= 4:
                result.append(giai_4_2[3])  # Số thứ 4
        
        if len(giai_7_2) >= 2:
            if len(giai_7_2) >= 1:
                result.append(giai_7_2[0])  # Số thứ 1
            if len(giai_7_2) >= 2:
                result.append(giai_7_2[1])  # Số thứ 2
        
        # Kiểm tra và xử lý số trùng
        seen = set()
        duplicates = set()
        
        # Tìm các số trùng
        for i, digit in enumerate(result):
            if digit in seen:
                duplicates.add(digit)
            seen.add(digit)
        
        # Xử lý kết quả, đổi số trùng thành bóng
        for i, digit in enumerate(result[:]):  # Tạo bản sao để tránh thay đổi trong quá trình lặp
            if digit in duplicates:
                result[i] = str(get_ball_number(int(digit)))
        
        return result
    
    def calculate(self, data: Dict[str, Any]) -> Dict[str, List[str]]:
        giai_3_5 = data.get('giai_3_5', '')
        giai_4_2 = data.get('giai_4_2', '')
        giai_7_2 = data.get('giai_7_2', '')
        
        if not giai_3_5 or not giai_4_2 or not giai_7_2:
            logger.warning(f"[{self.get_code()}] Thiếu dữ liệu đầu vào: giai_3_5={giai_3_5}, giai_4_2={giai_4_2}, giai_7_2={giai_7_2}")
            return {'two_digits_special': []}
        
        try:
            # Xử lý giải 3.5: 3 số cuối, số trùng đổi bóng
            # Ví dụ: 58377 -> 3,7,7 -> 3,7,2 (7 trùng nên đổi thành bóng 2)
            first_nums = self.process_last_three_digits(giai_3_5)
            if not first_nums:
                logger.warning(f"[{self.get_code()}] Giải 3.5 không đủ dài: {giai_3_5}")
                return {'two_digits_special': []}
            
            # Xử lý giải 4.2 và 7.2: lấy số thứ 3,4 của 4.2 và số thứ 1,2 của 7.2
            # Ví dụ: 4.2: 7128 -> 2,8; 7.2: 52 -> 5,2 => 2,8,5,2 -> 2,8,5,7 (2 trùng nên đổi thành bóng 7)
            second_nums = self.process_combination(giai_4_2, giai_7_2)
            if not second_nums:
                logger.warning(f"[{self.get_code()}] Giải 4.2 hoặc 7.2 không đủ dài: giai_4_2={giai_4_2}, giai_7_2={giai_7_2}")
                return {'two_digits_special': []}
            
            # Tạo các cặp số 2 chữ số 
            two_digits = set()
            for first in first_nums:
                for second in second_nums:
                    # Thêm cặp số thẳng
                    two_digits.add(f"{first}{second}")
            
            logger.info(f"[{self.get_code()}] Kết quả: {sorted(list(two_digits))}")
            return {
                'two_digits_special': sorted(list(two_digits))
            }
        except (ValueError, IndexError, TypeError) as e:
            logger.error(f"[{self.get_code()}] Lỗi tính 63 đề 2 số: {str(e)}")
            return {'two_digits_special': []}


class De63ThreeDigitMethod(BasePredictionMethod):
    """
    Phương pháp 63 Đề 3 số
    Dự đoán từ giải 3.5, 4.2, 7.2 và chạm đề từ giải 2.1 (số thứ 4) và 7.2 (số thứ 1)
    """
    def get_code(self) -> str:
        return "de63_3d"
    
    def get_name(self) -> str:
        return "63 Đề 3 số"
    
    def get_description(self) -> str:
        return "Dự đoán 3 số từ giải 3.5, 4.2, 7.2 và chạm đề từ giải 2.1 và 7.2"
    
    def process_last_three_digits(self, number: str) -> List[str]:
        """Xử lý 3 số cuối, đổi số trùng thành bóng"""
        if len(number) < 3:
            return []
        
        # Lấy 3 số cuối
        last_three = number[-3:]
        result = []
        
        # Kiểm tra và xử lý số trùng
        seen = set()
        duplicates = set()
        
        # Tìm các số trùng
        for digit in last_three:
            if digit in seen:
                duplicates.add(digit)
            seen.add(digit)
        
        # Xử lý kết quả, đổi số trùng thành bóng
        for digit in last_three:
            if digit in duplicates:
                result.append(str(get_ball_number(int(digit))))
            else:
                result.append(digit)
        
        return result
    
    def process_combination(self, giai_4_2: str, giai_7_2: str) -> List[str]:
        """Xử lý số thứ 3, 4 của giải 4.2 và số thứ 1, 2 của giải 7.2"""
        result = []
        
        if len(giai_4_2) >= 4:
            if len(giai_4_2) >= 3:
                result.append(giai_4_2[2])  # Số thứ 3
            if len(giai_4_2) >= 4:
                result.append(giai_4_2[3])  # Số thứ 4
        
        if len(giai_7_2) >= 2:
            if len(giai_7_2) >= 1:
                result.append(giai_7_2[0])  # Số thứ 1
            if len(giai_7_2) >= 2:
                result.append(giai_7_2[1])  # Số thứ 2
        
        # Kiểm tra và xử lý số trùng
        seen = set()
        duplicates = set()
        
        # Tìm các số trùng
        for i, digit in enumerate(result):
            if digit in seen:
                duplicates.add(digit)
            seen.add(digit)
        
        # Xử lý kết quả, đổi số trùng thành bóng
        for i, digit in enumerate(result[:]):  # Tạo bản sao để tránh thay đổi trong quá trình lặp
            if digit in duplicates:
                result[i] = str(get_ball_number(int(digit)))
        
        return result
    
    def calculate(self, data: Dict[str, Any]) -> Dict[str, List[str]]:
        giai_3_5 = data.get('giai_3_5', '')
        giai_4_2 = data.get('giai_4_2', '')
        giai_7_2 = data.get('giai_7_2', '')
        giai_2_1 = data.get('giai_2_1', '')
        
        if not giai_3_5 or not giai_4_2 or not giai_7_2 or not giai_2_1:
            logger.warning(f"[{self.get_code()}] Thiếu dữ liệu đầu vào: giai_3_5={giai_3_5}, giai_4_2={giai_4_2}, giai_7_2={giai_7_2}, giai_2_1={giai_2_1}")
            return {'three_digits_special': []}
        
        try:
            # Xử lý giải 3.5: 3 số cuối, số trùng đổi bóng
            first_nums = self.process_last_three_digits(giai_3_5)
            if not first_nums:
                logger.warning(f"[{self.get_code()}] Giải 3.5 không đủ dài: {giai_3_5}")
                return {'three_digits_special': []}
            
            # Xử lý giải 4.2 và 7.2: lấy số thứ 3,4 của 4.2 và số thứ 1,2 của 7.2
            second_nums = self.process_combination(giai_4_2, giai_7_2)
            if not second_nums:
                logger.warning(f"[{self.get_code()}] Giải 4.2 hoặc 7.2 không đủ dài: giai_4_2={giai_4_2}, giai_7_2={giai_7_2}")
                return {'three_digits_special': []}
            
            # Tạo các cặp số 2 chữ số (bao gồm cả cặp đảo ngược)
            two_digits = []
            for first in first_nums:
                for second in second_nums:
                    # Thêm cặp số thẳng
                    two_digits.append(f"{first}{second}")
            
            # Xử lý chạm đề từ giải 2.1 (số thứ 4) và 7.2 (số thứ 1)
            cang_digits = []
            
            # Chạm đề từ giải 2.1: số thứ 4
            if len(giai_2_1) >= 4:
                cham_de_1 = giai_2_1[3]  # Lấy số thứ 4, ví dụ: 18519 -> 1
                cang_digits.append(cham_de_1)
                cang_digits.append(str(get_ball_number(int(cham_de_1))))
            else:
                logger.warning(f"[{self.get_code()}] Giải 2.1 không đủ dài: {giai_2_1}")
                return {'three_digits_special': []}
            
            # Chạm đề từ giải 7.2: số thứ 1
            if len(giai_7_2) >= 1:
                cham_de_2 = giai_7_2[0]  # Lấy số thứ 1, ví dụ: 52 -> 5
                cang_digits.append(cham_de_2)
                cang_digits.append(str(get_ball_number(int(cham_de_2))))
            else:
                logger.warning(f"[{self.get_code()}] Giải 7.2 không đủ dài: {giai_7_2}")
                return {'three_digits_special': []}
            
            # Tạo các cặp số 3 chữ số
            three_digits = set()
            for cang in cang_digits:
                for two_digit in two_digits:
                    three_digits.add(f"{cang}{two_digit}")
            
            logger.info(f"[{self.get_code()}] Kết quả: {sorted(list(three_digits))}")
            return {
                'three_digits_special': sorted(list(three_digits))
            }
        except (ValueError, IndexError, TypeError) as e:
            logger.error(f"[{self.get_code()}] Lỗi tính 63 đề 3 số: {str(e)}")
            return {'three_digits_special': []}
        

