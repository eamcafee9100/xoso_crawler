from typing import Dict, List, Any
from .base import BasePredictionMethod
import logging
from .utils import get_ball_number
logger = logging.getLogger(__name__)
class Btl_51LotoMethod(BasePredictionMethod):
    """
    Phương pháp Bạch thủ lô 51
    Dự đoán từ giải 3.1 (số thứ 4) và giải 7.1 (số thứ 2)
    """
    def get_code(self) -> str:
        return "btl_51"
    
    def get_name(self) -> str:
        return "Bạch thủ lô 51"
    
    def get_description(self) -> str:
        return "Dự đoán 2 số từ giải 3.1 và giải 7.1"
    
    def calculate(self, data: Dict[str, Any]) -> Dict[str, List[str]]:
        giai_3_1 = data.get('giai_3_1', '')
        giai_7_1 = data.get('giai_7_1', '')
        
        if not giai_3_1 or not giai_7_1:
            logger.warning(f"[{self.get_code()}] Thiếu dữ liệu đầu vào: giai_3_1={giai_3_1}, giai_7_1={giai_7_1}")
            return {'two_digits_loto': []}
        
        try:
            # Số thứ nhất từ giải 3.1: số thứ 4
            # Ví dụ: 43234 -> số thứ 4 = 3
            if len(giai_3_1) >= 4:
                first_digit = giai_3_1[3]
            else:
                logger.warning(f"[{self.get_code()}] Giải 3.1 không đủ dài: {giai_3_1}")
                return {'two_digits_loto': []}
                
            # Số thứ hai từ giải 7.1: số thứ 2
            # Ví dụ: 31 -> số thứ 2 = 1
            if len(giai_7_1) >= 2:
                second_digit = giai_7_1[1]
            else:
                logger.warning(f"[{self.get_code()}] Giải 7.1 không đủ dài: {giai_7_1}")
                return {'two_digits_loto': []}
            
            # Tạo các cặp số 2 chữ số (bao gồm cả cặp đảo ngược)
            two_digits = set()
            # Thêm cặp số thẳng
            two_digits.add(f"{first_digit}{second_digit}")
            # Thêm cặp số đảo ngược
            two_digits.add(f"{second_digit}{first_digit}")
            
            logger.info(f"[{self.get_code()}] Kết quả: {sorted(list(two_digits))}")
            return {
                'two_digits_loto': sorted(list(two_digits))
            }
        except (ValueError, IndexError, TypeError) as e:
            logger.error(f"[{self.get_code()}] Lỗi tính bạch thủ lô 1: {str(e)}")
            return {'two_digits_loto': []}
        
class Btl_52LotoMethod(BasePredictionMethod):
    """
    Phương pháp Bạch thủ lô 52
    Dự đoán từ giải 5.4 (số thứ 2) và giải 6.2 (số thứ 3)
    """
    def get_code(self) -> str:
        return "btl_52"
    
    def get_name(self) -> str:
        return "Bạch thủ lô 52"
    
    def get_description(self) -> str:
        return "Dự đoán 2 số từ giải 5.4 và giải 6.2"
    
    def calculate(self, data: Dict[str, Any]) -> Dict[str, List[str]]:
        giai_5_4 = data.get('giai_5_4', '')
        giai_6_2 = data.get('giai_6_2', '')
        
        if not giai_5_4 or not giai_6_2:
            logger.warning(f"[{self.get_code()}] Thiếu dữ liệu đầu vào: giai_5_4={giai_5_4}, giai_6_2={giai_6_2}")
            return {'two_digits_loto': []}
        
        try:
            # Số thứ nhất từ giải 5.4: số thứ 2
            # Ví dụ: 4324 -> số thứ 2 = 3
            if len(giai_5_4) >= 2:
                first_digit = giai_5_4[1]
            else:
                logger.warning(f"[{self.get_code()}] Giải 5.4 không đủ dài: {giai_5_4}")
                return {'two_digits_loto': []}
                
            # Số thứ hai từ giải 6.2: số thứ 3
            # Ví dụ: 351 -> số thứ 3 = 1
            if len(giai_6_2) >= 3:
                second_digit = giai_6_2[2]
            else:
                logger.warning(f"[{self.get_code()}] Giải 6.2 không đủ dài: {giai_6_2}")
                return {'two_digits_loto': []}
            
            # Tạo các cặp số 2 chữ số (bao gồm cả cặp đảo ngược)
            two_digits = set()
            # Thêm cặp số thẳng
            two_digits.add(f"{first_digit}{second_digit}")
            # Thêm cặp số đảo ngược
            two_digits.add(f"{second_digit}{first_digit}")
            
            logger.info(f"[{self.get_code()}] Kết quả: {sorted(list(two_digits))}")
            return {
                'two_digits_loto': sorted(list(two_digits))
            }
        except (ValueError, IndexError, TypeError) as e:
            logger.error(f"[{self.get_code()}] Lỗi tính bạch thủ lô 2: {str(e)}")
            return {'two_digits_loto': []}
        
class Btl_53LotoMethod(BasePredictionMethod):
    """
    Phương pháp Bạch thủ lô 53
    Dự đoán từ giải 3.1 (số thứ 3) và giải 5.5 (số thứ 2)
    """
    def get_code(self) -> str:
        return "btl_53"
    
    def get_name(self) -> str:
        return "Bạch thủ lô 53"
    
    def get_description(self) -> str:
        return "Dự đoán 2 số từ giải 3.1 và giải 5.5"
    
    def calculate(self, data: Dict[str, Any]) -> Dict[str, List[str]]:
        giai_3_1 = data.get('giai_3_1', '')
        giai_5_5 = data.get('giai_5_5', '')
        
        if not giai_3_1 or not giai_5_5:
            logger.warning(f"[{self.get_code()}] Thiếu dữ liệu đầu vào: giai_3_1={giai_3_1}, giai_5_5={giai_5_5}")
            return {'two_digits_loto': []}
        
        try:
            # Số thứ nhất từ giải 3.1: số thứ 3
            # Ví dụ: 43234 -> số thứ 3 = 2
            if len(giai_3_1) >= 3:
                first_digit = giai_3_1[2]
            else:
                logger.warning(f"[{self.get_code()}] Giải 3.1 không đủ dài: {giai_3_1}")
                return {'two_digits_loto': []}
                
            # Số thứ hai từ giải 5.5: số thứ 2
            # Ví dụ: 3231 -> số thứ 2 = 1
            if len(giai_5_5) >= 2:
                second_digit = giai_5_5[1]
            else:
                logger.warning(f"[{self.get_code()}] Giải 5.5 không đủ dài: {giai_5_5}")
                return {'two_digits_loto': []}
            
            # Tạo các cặp số 2 chữ số (bao gồm cả cặp đảo ngược)
            two_digits = set()
            # Thêm cặp số thẳng
            two_digits.add(f"{first_digit}{second_digit}")
            # Thêm cặp số đảo ngược
            two_digits.add(f"{second_digit}{first_digit}")
            
            logger.info(f"[{self.get_code()}] Kết quả: {sorted(list(two_digits))}")
            return {
                'two_digits_loto': sorted(list(two_digits))
            }
        except (ValueError, IndexError, TypeError) as e:
            logger.error(f"[{self.get_code()}] Lỗi tính bạch thủ lô 3: {str(e)}")
            return {'two_digits_loto': []}
        
class Btl_54LotoMethod(BasePredictionMethod):
    """
    Phương pháp Bạch thủ lô 54
    Dự đoán từ giải 4.1 (số thứ 2) và giải 5.5 (số thứ 2)
    """
    def get_code(self) -> str:
        return "btl_54"
    
    def get_name(self) -> str:
        return "Bạch thủ lô 54"
    
    def get_description(self) -> str:
        return "Dự đoán 2 số từ giải 4.1 và giải 5.5"
    
    def calculate(self, data: Dict[str, Any]) -> Dict[str, List[str]]:
        giai_4_1 = data.get('giai_4_1', '')
        giai_5_5 = data.get('giai_5_5', '')
        
        if not giai_4_1 or not giai_5_5:
            logger.warning(f"[{self.get_code()}] Thiếu dữ liệu đầu vào: giai_4_1={giai_4_1}, giai_5_5={giai_5_5}")
            return {'two_digits_loto': []}
        
        try:
            # Số thứ nhất từ giải 4.1: số thứ 2
            # Ví dụ: 4324 -> số thứ 2 = 3
            if len(giai_4_1) >= 2:
                first_digit = giai_4_1[1]
            else:
                logger.warning(f"[{self.get_code()}] Giải 4.1 không đủ dài: {giai_4_1}")
                return {'two_digits_loto': []}
                
            # Số thứ hai từ giải 5.5: số thứ 2
            # Ví dụ: 3151 -> số thứ 2 = 1
            if len(giai_5_5) >= 2:
                second_digit = giai_5_5[1]
            else:
                logger.warning(f"[{self.get_code()}] Giải 5.5 không đủ dài: {giai_5_5}")
                return {'two_digits_loto': []}
            
            # Tạo các cặp số 2 chữ số (bao gồm cả cặp đảo ngược)
            two_digits = set()
            # Thêm cặp số thẳng
            two_digits.add(f"{first_digit}{second_digit}")
            # Thêm cặp số đảo ngược
            two_digits.add(f"{second_digit}{first_digit}")
            
            logger.info(f"[{self.get_code()}] Kết quả: {sorted(list(two_digits))}")
            return {
                'two_digits_loto': sorted(list(two_digits))
            }
        except (ValueError, IndexError, TypeError) as e:
            logger.error(f"[{self.get_code()}] Lỗi tính bạch thủ lô 51: {str(e)}")
            return {'two_digits_loto': []}
        


class Btl_57LotoMethod(BasePredictionMethod):
    """
    Phương pháp Bạch thủ lô 57
    Dự đoán từ tổng số thứ 1 và 2 giải 3.1, tổng số thứ 4 và 5 giải 3.4, số thứ 2 giải 7.1, số thứ 2 giải 7.2
    """
    def get_code(self) -> str:
        return "btl_57"
    
    def get_name(self) -> str:
        return "Bạch thủ lô 57"
    
    def get_description(self) -> str:
        return "Dự đoán các cặp số 2 chữ số từ tổng số thứ 1 và 2 giải 3.1, tổng số thứ 4 và 5 giải 3.4, số thứ 2 giải 7.1, số thứ 2 giải 7.2"
    
    def calculate(self, data: Dict[str, Any]) -> Dict[str, List[str]]:
        giai_3_1 = data.get('giai_3_1', '')
        giai_3_4 = data.get('giai_3_4', '')
        giai_7_1 = data.get('giai_7_1', '')
        giai_7_2 = data.get('giai_7_2', '')
        
        if not all([giai_3_1, giai_3_4, giai_7_1, giai_7_2]):
            logger.warning(f"[{self.get_code()}] Thiếu dữ liệu đầu vào: giai_3_1={giai_3_1}, giai_3_4={giai_3_4}, giai_7_1={giai_7_1}, giai_7_2={giai_7_2}")
            return {'two_digits_loto': []}
        
        try:
            # Số thứ nhất: Tổng số thứ 1 và số thứ 2 giải 3.1
            # Ví dụ: 11212 -> 1+1=2
            if len(giai_3_1) >= 2:
                first_digit = str((int(giai_3_1[0]) + int(giai_3_1[1])) % 10)
            else:
                logger.warning(f"[{self.get_code()}] Giải 3.1 không đủ dài: {giai_3_1}")
                return {'two_digits_loto': []}
                
            # Số thứ hai: Tổng số thứ 4 và số thứ 5 giải 3.4
            # Ví dụ: 51411 -> 1+1=2
            if len(giai_3_4) >= 5:
                second_digit = str((int(giai_3_4[3]) + int(giai_3_4[4])) % 10)
            else:
                logger.warning(f"[{self.get_code()}] Giải 3.4 không đủ dài: {giai_3_4}")
                return {'two_digits_loto': []}
                
            # Số thứ ba: Số thứ 2 giải 7.1
            # Ví dụ: 13 -> 3
            if len(giai_7_1) >= 2:
                third_digit = giai_7_1[1]
            else:
                logger.warning(f"[{self.get_code()}] Giải 7.1 không đủ dài: {giai_7_1}")
                return {'two_digits_loto': []}
                
            # Số thứ tư: Số thứ 2 giải 7.2
            # Ví dụ: 54 -> 4
            if len(giai_7_2) >= 2:
                fourth_digit = giai_7_2[1]
            else:
                logger.warning(f"[{self.get_code()}] Giải 7.2 không đủ dài: {giai_7_2}")
                return {'two_digits_loto': []}
            
            # Tạo các cặp số 2 chữ số
            two_digits = set()
            # Cặp từ số thứ nhất và số thứ hai
            two_digits.add(f"{first_digit}{second_digit}")
            if first_digit != second_digit:  # Tránh cặp trùng nếu số giống nhau
                two_digits.add(f"{second_digit}{first_digit}")
                
            # Cặp từ số thứ ba và số thứ tư
            two_digits.add(f"{third_digit}{fourth_digit}")
            if third_digit != fourth_digit:  # Tránh cặp trùng nếu số giống nhau
                two_digits.add(f"{fourth_digit}{third_digit}")
            
            if not two_digits:
                logger.warning(f"[{self.get_code()}] Không tạo được cặp số nào từ dữ liệu")
                return {'two_digits_loto': []}
            
            logger.info(f"[{self.get_code()}] Kết quả: {sorted(list(two_digits))}")
            return {
                'two_digits_loto': sorted(list(two_digits))
            }
        except (ValueError, IndexError, TypeError) as e:
            logger.error(f"[{self.get_code()}] Lỗi tính bạch thủ lô 57: {str(e)}")
            return {'two_digits_loto': []}


class Btl_74LotoMethod(BasePredictionMethod):
    """
    Phương pháp Bạch thủ lô 74
    Dự đoán từ số thứ 5 giải 3.2, số thứ 5 giải 3.5, tổng số thứ 1 và 2 giải 5.6, số thứ 3 giải 5.6 đổi bóng
    """
    def get_code(self) -> str:
        return "btl_74"
    
    def get_name(self) -> str:
        return "Bạch thủ lô 74"
    
    def get_description(self) -> str:
        return "Dự đoán các cặp số 2 chữ số từ số thứ 5 giải 3.2, số thứ 5 giải 3.5, tổng số thứ 1 và 2 giải 5.6, số thứ 3 giải 5.6 đổi bóng"
    
    def calculate(self, data: Dict[str, Any]) -> Dict[str, List[str]]:
        giai_3_2 = data.get('giai_3_2', '')
        giai_3_5 = data.get('giai_3_5', '')
        giai_5_6 = data.get('giai_5_6', '')
        
        if not all([giai_3_2, giai_3_5, giai_5_6]):
            logger.warning(f"[{self.get_code()}] Thiếu dữ liệu đầu vào: giai_3_2={giai_3_2}, giai_3_5={giai_3_5}, giai_5_6={giai_5_6}")
            return {'two_digits_loto': []}
        
        try:
            # Số thứ nhất: Số thứ 5 giải 3.2
            # Ví dụ: 11212 -> 2
            if len(giai_3_2) >= 5:
                first_digit = giai_3_2[4]
            else:
                logger.warning(f"[{self.get_code()}] Giải 3.2 không đủ dài: {giai_3_2}")
                return {'two_digits_loto': []}
                
            # Số thứ hai: Số thứ 5 giải 3.5
            # Ví dụ: 51411 -> 1
            if len(giai_3_5) >= 5:
                second_digit = giai_3_5[4]
            else:
                logger.warning(f"[{self.get_code()}] Giải 3.5 không đủ dài: {giai_3_5}")
                return {'two_digits_loto': []}
                
            # Số thứ ba: Tổng số thứ 1 và số thứ 2 giải 5.6
            # Ví dụ: 1343 -> 1+3=4
            if len(giai_5_6) >= 2:
                third_digit = str((int(giai_5_6[0]) + int(giai_5_6[1])) % 10)
            else:
                logger.warning(f"[{self.get_code()}] Giải 5.6 không đủ dài: {giai_5_6}")
                return {'two_digits_loto': []}
                
            # Số thứ tư: Số thứ 3 giải 5.6, đổi bóng
            # Ví dụ: 1343 -> 4 -> bóng 9
            if len(giai_5_6) >= 3:
                fourth_digit = str(get_ball_number(giai_5_6[2]))
            else:
                logger.warning(f"[{self.get_code()}] Giải 5.6 không đủ dài: {giai_5_6}")
                return {'two_digits_loto': []}
            
            # Tạo các cặp số 2 chữ số
            two_digits = set()
            # Cặp từ số thứ nhất và số thứ hai
            two_digits.add(f"{first_digit}{second_digit}")
            if first_digit != second_digit:  # Tránh cặp trùng nếu số giống nhau
                two_digits.add(f"{second_digit}{first_digit}")
                
            # Cặp từ số thứ ba và số thứ tư
            two_digits.add(f"{third_digit}{fourth_digit}")
            if third_digit != fourth_digit:  # Tránh cặp trùng nếu số giống nhau
                two_digits.add(f"{fourth_digit}{third_digit}")
            
            if not two_digits:
                logger.warning(f"[{self.get_code()}] Không tạo được cặp số nào từ dữ liệu")
                return {'two_digits_loto': []}
            
            logger.info(f"[{self.get_code()}] Kết quả: {sorted(list(two_digits))}")
            return {
                'two_digits_loto': sorted(list(two_digits))
            }
        except (ValueError, IndexError, TypeError) as e:
            logger.error(f"[{self.get_code()}] Lỗi tính bạch thủ lô 74: {str(e)}")
            return {'two_digits_loto': []}
