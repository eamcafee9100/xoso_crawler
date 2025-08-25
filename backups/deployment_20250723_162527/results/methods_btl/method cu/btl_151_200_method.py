from typing import Dict, List, Any
from .base import BasePredictionMethod
import logging
from .utils import get_ball_number
logger = logging.getLogger(__name__)

class Btl_151LotoMethod(BasePredictionMethod):
    """
    Phương pháp Bạch thủ lô 151
    Dự đoán từ tổng số thứ 1 và 2 giải 4.1, tổng số thứ 1 và 2 giải 4.2, tổng số thứ 3 và 4 giải 5.1, số thứ 1 giải 7.2
    """
    def get_code(self) -> str:
        return "btl_151"
    
    def get_name(self) -> str:
        return "Bạch thủ lô 151"
    
    def get_description(self) -> str:
        return "Dự đoán các cặp số 2 chữ số từ tổng số thứ 1 và 2 giải 4.1, tổng số thứ 1 và 2 giải 4.2, tổng số thứ 3 và 4 giải 5.1, số thứ 1 giải 7.2"
    
    def calculate(self, data: Dict[str, Any]) -> Dict[str, List[str]]:
        giai_4_1 = data.get('giai_4_1', '')
        giai_4_2 = data.get('giai_4_2', '')
        giai_5_1 = data.get('giai_5_1', '')
        giai_7_2 = data.get('giai_7_2', '')
        
        if not all([giai_4_1, giai_4_2, giai_5_1, giai_7_2]):
            logger.warning(f"[{self.get_code()}] Thiếu dữ liệu đầu vào: giai_4_1={giai_4_1}, giai_4_2={giai_4_2}, giai_5_1={giai_5_1}, giai_7_2={giai_7_2}")
            return {'two_digits_loto': []}
        
        try:
            # Số thứ nhất: Tổng số thứ 1 và số thứ 2 giải 4.1
            # Ví dụ: 4162 -> 4+1=5
            if len(giai_4_1) >= 2:
                first_digit = str((int(giai_4_1[0]) + int(giai_4_1[1])) % 10)
            else:
                logger.warning(f"[{self.get_code()}] Giải 4.1 không đủ dài: {giai_4_1}")
                return {'two_digits_loto': []}
                
            # Số thứ hai: Tổng số thứ 1 và số thứ 2 giải 4.2
            # Ví dụ: 5141 -> 5+1=6
            if len(giai_4_2) >= 2:
                second_digit = str((int(giai_4_2[0]) + int(giai_4_2[1])) % 10)
            else:
                logger.warning(f"[{self.get_code()}] Giải 4.2 không đủ dài: {giai_4_2}")
                return {'two_digits_loto': []}
                
            # Số thứ ba: Tổng số thứ 3 và số thứ 4 giải 5.1
            # Ví dụ: 4112 -> 1+2=3
            if len(giai_5_1) >= 4:
                third_digit = str((int(giai_5_1[2]) + int(giai_5_1[3])) % 10)
            else:
                logger.warning(f"[{self.get_code()}] Giải 5.1 không đủ dài: {giai_5_1}")
                return {'two_digits_loto': []}
                
            # Số thứ tư: Số thứ 1 giải 7.2
            # Ví dụ: 41 -> 4
            if len(giai_7_2) >= 1:
                fourth_digit = giai_7_2[0]
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
            logger.error(f"[{self.get_code()}] Lỗi tính bạch thủ lô 151: {str(e)}")
            return {'two_digits_loto': []}
        
from typing import Dict, List, Any
from .base import BasePredictionMethod
import logging

logger = logging.getLogger(__name__)

class Btl_152LotoMethod(BasePredictionMethod):
    """
    Phương pháp Bạch thủ lô 152
    Dự đoán từ tổng số thứ 1 và 2 giải 4.2, tổng số thứ 1 và 2 giải 4.3, tổng số thứ 3 và 4 giải 5.1, số thứ 1 giải 7.2
    """
    def get_code(self) -> str:
        return "btl_152"
    
    def get_name(self) -> str:
        return "Bạch thủ lô 152"
    
    def get_description(self) -> str:
        return "Dự đoán các cặp số 2 chữ số từ tổng số thứ 1 và 2 giải 4.2, tổng số thứ 1 và 2 giải 4.3, tổng số thứ 3 và 4 giải 5.1, số thứ 1 giải 7.2"
    
    def calculate(self, data: Dict[str, Any]) -> Dict[str, List[str]]:
        giai_4_2 = data.get('giai_4_2', '')
        giai_4_3 = data.get('giai_4_3', '')
        giai_5_1 = data.get('giai_5_1', '')
        giai_7_2 = data.get('giai_7_2', '')
        
        if not all([giai_4_2, giai_4_3, giai_5_1, giai_7_2]):
            logger.warning(f"[{self.get_code()}] Thiếu dữ liệu đầu vào: giai_4_2={giai_4_2}, giai_4_3={giai_4_3}, giai_5_1={giai_5_1}, giai_7_2={giai_7_2}")
            return {'two_digits_loto': []}
        
        try:
            # Số thứ nhất: Tổng số thứ 1 và số thứ 2 giải 4.2
            # Ví dụ: 4162 -> 4+1=5
            if len(giai_4_2) >= 2:
                first_digit = str((int(giai_4_2[0]) + int(giai_4_2[1])) % 10)
            else:
                logger.warning(f"[{self.get_code()}] Giải 4.2 không đủ dài: {giai_4_2}")
                return {'two_digits_loto': []}
                
            # Số thứ hai: Tổng số thứ 1 và số thứ 2 giải 4.3
            # Ví dụ: 5141 -> 5+1=6
            if len(giai_4_3) >= 2:
                second_digit = str((int(giai_4_3[0]) + int(giai_4_3[1])) % 10)
            else:
                logger.warning(f"[{self.get_code()}] Giải 4.3 không đủ dài: {giai_4_3}")
                return {'two_digits_loto': []}
                
            # Số thứ ba: Tổng số thứ 3 và số thứ 4 giải 5.1
            # Ví dụ: 4112 -> 1+2=3
            if len(giai_5_1) >= 4:
                third_digit = str((int(giai_5_1[2]) + int(giai_5_1[3])) % 10)
            else:
                logger.warning(f"[{self.get_code()}] Giải 5.1 không đủ dài: {giai_5_1}")
                return {'two_digits_loto': []}
                
            # Số thứ tư: Số thứ 1 giải 7.2
            # Ví dụ: 41 -> 4
            if len(giai_7_2) >= 1:
                fourth_digit = giai_7_2[0]
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
            logger.error(f"[{self.get_code()}] Lỗi tính bạch thủ lô 152: {str(e)}")
            return {'two_digits_loto': []}


class Btl_153LotoMethod(BasePredictionMethod):
    """
    Phương pháp Bạch thủ lô 153
    Dự đoán từ số thứ 4 giải 5.4, số thứ 3 giải 6.1
    """
    def get_code(self) -> str:
        return "btl_153"
    
    def get_name(self) -> str:
        return "Bạch thủ lô 153"
    
    def get_description(self) -> str:
        return "Dự đoán các cặp số 2 chữ số từ số thứ 4 giải 5.4 và số thứ 3 giải 6.1"
    
    def calculate(self, data: Dict[str, Any]) -> Dict[str, List[str]]:
        giai_5_4 = data.get('giai_5_4', '')
        giai_6_1 = data.get('giai_6_1', '')
        
        if not all([giai_5_4, giai_6_1]):
            logger.warning(f"[{self.get_code()}] Thiếu dữ liệu đầu vào: giai_5_4={giai_5_4}, giai_6_1={giai_6_1}")
            return {'two_digits_loto': []}
        
        try:
            # Số thứ nhất: Số thứ 4 giải 5.4
            # Ví dụ: 1421 -> 1
            if len(giai_5_4) >= 4:
                first_digit = giai_5_4[3]
            else:
                logger.warning(f"[{self.get_code()}] Giải 5.4 không đủ dài: {giai_5_4}")
                return {'two_digits_loto': []}
                
            # Số thứ hai: Số thứ 3 giải 6.1
            # Ví dụ: 131 -> 1
            if len(giai_6_1) >= 3:
                second_digit = giai_6_1[2]
            else:
                logger.warning(f"[{self.get_code()}] Giải 6.1 không đủ dài: {giai_6_1}")
                return {'two_digits_loto': []}
            
            # Tạo các cặp số 2 chữ số
            two_digits = set()
            # Cặp số thẳng
            two_digits.add(f"{first_digit}{second_digit}")
            # Cặp số đảo ngược
            if first_digit != second_digit:  # Tránh cặp trùng nếu số giống nhau
                two_digits.add(f"{second_digit}{first_digit}")
            
            if not two_digits:
                logger.warning(f"[{self.get_code()}] Không tạo được cặp số nào từ dữ liệu")
                return {'two_digits_loto': []}
            
            logger.info(f"[{self.get_code()}] Kết quả: {sorted(list(two_digits))}")
            return {
                'two_digits_loto': sorted(list(two_digits))
            }
        except (ValueError, IndexError, TypeError) as e:
            logger.error(f"[{self.get_code()}] Lỗi tính bạch thủ lô 153: {str(e)}")
            return {'two_digits_loto': []}
        


class Btl_154LotoMethod(BasePredictionMethod):
    """
    Phương pháp Bạch thủ lô 154
    Dự đoán từ số thứ 1 giải 3.1, số thứ 2 giải 3.5
    """
    def get_code(self) -> str:
        return "btl_154"
    
    def get_name(self) -> str:
        return "Bạch thủ lô 154"
    
    def get_description(self) -> str:
        return "Dự đoán các cặp số 2 chữ số từ số thứ 1 giải 3.1 và số thứ 2 giải 3.5"
    
    def calculate(self, data: Dict[str, Any]) -> Dict[str, List[str]]:
        giai_3_1 = data.get('giai_3_1', '')
        giai_3_5 = data.get('giai_3_5', '')
        
        if not all([giai_3_1, giai_3_5]):
            logger.warning(f"[{self.get_code()}] Thiếu dữ liệu đầu vào: giai_3_1={giai_3_1}, giai_3_5={giai_3_5}")
            return {'two_digits_loto': []}
        
        try:
            # Số thứ nhất: Số thứ 1 giải 3.1
            # Ví dụ: 14215 -> 1
            if len(giai_3_1) >= 1:
                first_digit = giai_3_1[0]
            else:
                logger.warning(f"[{self.get_code()}] Giải 3.1 không đủ dài: {giai_3_1}")
                return {'two_digits_loto': []}
                
            # Số thứ hai: Số thứ 2 giải 3.5
            # Ví dụ: 14215 -> 4
            if len(giai_3_5) >= 2:
                second_digit = giai_3_5[1]
            else:
                logger.warning(f"[{self.get_code()}] Giải 3.5 không đủ dài: {giai_3_5}")
                return {'two_digits_loto': []}
            
            # Tạo các cặp số 2 chữ số
            two_digits = set()
            # Cặp số thẳng
            two_digits.add(f"{first_digit}{second_digit}")
            # Cặp số đảo ngược
            if first_digit != second_digit:  # Tránh cặp trùng nếu số giống nhau
                two_digits.add(f"{second_digit}{first_digit}")
            
            if not two_digits:
                logger.warning(f"[{self.get_code()}] Không tạo được cặp số nào từ dữ liệu")
                return {'two_digits_loto': []}
            
            logger.info(f"[{self.get_code()}] Kết quả: {sorted(list(two_digits))}")
            return {
                'two_digits_loto': sorted(list(two_digits))
            }
        except (ValueError, IndexError, TypeError) as e:
            logger.error(f"[{self.get_code()}] Lỗi tính bạch thủ lô 154: {str(e)}")
            return {'two_digits_loto': []}


class Btl_155LotoMethod(BasePredictionMethod):
    """
    Phương pháp Bạch thủ lô 155
    Dự đoán từ tổng số thứ 3 và 4 giải 3.1, số thứ 5 giải 3.1 đổi bóng, tổng số thứ 2 và 3 giải 4.4, số thứ 4 giải 4.4 đổi bóng
    """
    def get_code(self) -> str:
        return "btl_155"
    
    def get_name(self) -> str:
        return "Bạch thủ lô 155"
    
    def get_description(self) -> str:
        return "Dự đoán các cặp số 2 chữ số từ tổng số thứ 3 và 4 giải 3.1, số thứ 5 giải 3.1 đổi bóng, tổng số thứ 2 và 3 giải 4.4, số thứ 4 giải 4.4 đổi bóng"
    
    def calculate(self, data: Dict[str, Any]) -> Dict[str, List[str]]:
        giai_3_1 = data.get('giai_3_1', '')
        giai_4_4 = data.get('giai_4_4', '')
        
        if not all([giai_3_1, giai_4_4]):
            logger.warning(f"[{self.get_code()}] Thiếu dữ liệu đầu vào: giai_3_1={giai_3_1}, giai_4_4={giai_4_4}")
            return {'two_digits_loto': []}
        
        try:
            # Số thứ nhất: Tổng số thứ 3 và số thứ 4 giải 3.1
            # Ví dụ: 14162 -> 1+6=7
            if len(giai_3_1) >= 4:
                first_digit = str((int(giai_3_1[2]) + int(giai_3_1[3])) % 10)
            else:
                logger.warning(f"[{self.get_code()}] Giải 3.1 không đủ dài: {giai_3_1}")
                return {'two_digits_loto': []}
                
            # Số thứ hai: Số thứ 5 giải 3.1, đổi bóng
            # Ví dụ: 51411 -> 1 -> bóng 6
            if len(giai_3_1) >= 5:
                second_digit = str(get_ball_number(giai_3_1[4]))
            else:
                logger.warning(f"[{self.get_code()}] Giải 3.1 không đủ dài: {giai_3_1}")
                return {'two_digits_loto': []}
                
            # Số thứ ba: Tổng số thứ 2 và số thứ 3 giải 4.4
            # Ví dụ: 1212 -> 2+1=3
            if len(giai_4_4) >= 3:
                third_digit = str((int(giai_4_4[1]) + int(giai_4_4[2])) % 10)
            else:
                logger.warning(f"[{self.get_code()}] Giải 4.4 không đủ dài: {giai_4_4}")
                return {'two_digits_loto': []}
                
            # Số thứ tư: Số thứ 4 giải 4.4, đổi bóng
            # Ví dụ: 1212 -> 2 -> bóng 7
            if len(giai_4_4) >= 4:
                fourth_digit = str(get_ball_number(giai_4_4[3]))
            else:
                logger.warning(f"[{self.get_code()}] Giải 4.4 không đủ dài: {giai_4_4}")
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
            logger.error(f"[{self.get_code()}] Lỗi tính bạch thủ lô 155: {str(e)}")
            return {'two_digits_loto': []}


class Btl_156LotoMethod(BasePredictionMethod):
    """
    Phương pháp Bạch thủ lô 156
    Dự đoán từ số thứ 1 giải 2.1, số thứ 5 giải 3.6, số thứ 3 giải 4.2
    """
    def get_code(self) -> str:
        return "btl_156"
    
    def get_name(self) -> str:
        return "Bạch thủ lô 156"
    
    def get_description(self) -> str:
        return "Dự đoán các cặp số 2 chữ số từ số thứ 1 giải 2.1 và số thứ 5 giải 3.6, số thứ 1 giải 2.1 và số thứ 3 giải 4.2"
    
    def calculate(self, data: Dict[str, Any]) -> Dict[str, List[str]]:
        giai_2_1 = data.get('giai_2_1', '')
        giai_3_6 = data.get('giai_3_6', '')
        giai_4_2 = data.get('giai_4_2', '')
        
        if not all([giai_2_1, giai_3_6, giai_4_2]):
            logger.warning(f"[{self.get_code()}] Thiếu dữ liệu đầu vào: giai_2_1={giai_2_1}, giai_3_6={giai_3_6}, giai_4_2={giai_4_2}")
            return {'two_digits_loto': []}
        
        try:
            # Số thứ nhất: Số thứ 1 giải 2.1
            # Ví dụ: 14215 -> 1
            if len(giai_2_1) >= 1:
                first_digit = giai_2_1[0]
            else:
                logger.warning(f"[{self.get_code()}] Giải 2.1 không đủ dài: {giai_2_1}")
                return {'two_digits_loto': []}
                
            # Số thứ hai: Số thứ 5 giải 3.6
            # Ví dụ: 14215 -> 5
            if len(giai_3_6) >= 5:
                second_digit = giai_3_6[4]
            else:
                logger.warning(f"[{self.get_code()}] Giải 3.6 không đủ dài: {giai_3_6}")
                return {'two_digits_loto': []}
                
            # Số thứ ba: Số thứ 3 giải 4.2
            # Ví dụ: 1215 -> 1
            if len(giai_4_2) >= 3:
                third_digit = giai_4_2[2]
            else:
                logger.warning(f"[{self.get_code()}] Giải 4.2 không đủ dài: {giai_4_2}")
                return {'two_digits_loto': []}
            
            # Tạo các cặp số 2 chữ số
            two_digits = set()
            # Cặp từ số thứ nhất và số thứ hai
            two_digits.add(f"{first_digit}{second_digit}")
            if first_digit != second_digit:  # Tránh cặp trùng nếu số giống nhau
                two_digits.add(f"{second_digit}{first_digit}")
                
            # Cặp từ số thứ nhất và số thứ ba
            two_digits.add(f"{first_digit}{third_digit}")
            if first_digit != third_digit:  # Tránh cặp trùng nếu số giống nhau
                two_digits.add(f"{third_digit}{first_digit}")
            
            if not two_digits:
                logger.warning(f"[{self.get_code()}] Không tạo được cặp số nào từ dữ liệu")
                return {'two_digits_loto': []}
            
            logger.info(f"[{self.get_code()}] Kết quả: {sorted(list(two_digits))}")
            return {
                'two_digits_loto': sorted(list(two_digits))
            }
        except (ValueError, IndexError, TypeError) as e:
            logger.error(f"[{self.get_code()}] Lỗi tính bạch thủ lô 156: {str(e)}")
            return {'two_digits_loto': []}