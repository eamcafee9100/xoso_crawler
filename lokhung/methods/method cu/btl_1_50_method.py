from typing import Dict, List, Any
from .base import BasePredictionMethod
import logging
from .utils import get_ball_number

logger = logging.getLogger(__name__)
        
class Btl_1LotoMethod(BasePredictionMethod):
    """
    Phương pháp Bạch thủ lô 1
    Dự đoán từ giải 3.2 (số thứ 2) và giải 4.2 (số thứ 2)
    """
    def get_code(self) -> str:
        return "btl_1"
    
    def get_name(self) -> str:
        return "Bạch thủ lô 1"
    
    def get_description(self) -> str:
        return "Dự đoán 2 số từ giải 3.2 và giải 4.2"
    
    def calculate(self, data: Dict[str, Any]) -> Dict[str, List[str]]:
        giai_3_2 = data.get('giai_3_2', '')
        giai_4_2 = data.get('giai_4_2', '')
        
        if not giai_3_2 or not giai_4_2:
            logger.warning(f"[{self.get_code()}] Thiếu dữ liệu đầu vào: giai_3_2={giai_3_2}, giai_4_2={giai_4_2}")
            return {'two_digits_loto': []}
        
        try:
            # Số thứ nhất từ giải 3.2: số thứ 2
            # Ví dụ: 43234 -> số thứ 2 = 3
            if len(giai_3_2) >= 2:
                first_digit = giai_3_2[1]
            else:
                logger.warning(f"[{self.get_code()}] Giải 3.2 không đủ dài: {giai_3_2}")
                return {'two_digits_loto': []}
                
            # Số thứ hai từ giải 4.2: số thứ 2
            # Ví dụ: 3231 -> số thứ 2 = 2
            if len(giai_4_2) >= 2:
                second_digit = giai_4_2[1]
            else:
                logger.warning(f"[{self.get_code()}] Giải 4.2 không đủ dài: {giai_4_2}")
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
            logger.error(f"[{self.get_code()}] Lỗi tính bạch thủ lô 4: {str(e)}")
            return {'two_digits_loto': []}
        
class Btl_2LotoMethod(BasePredictionMethod):
    """
    Phương pháp Bạch thủ lô 2
    Dự đoán từ giải đặc biệt: số thứ nhất lấy tất cả các số, số thứ hai lấy 4 số còn lại trừ số được chọn
    """
    def get_code(self) -> str:
        return "btl_2"
    
    def get_name(self) -> str:
        return "Bạch thủ lô 2"
    
    def get_description(self) -> str:
        return "Dự đoán các cặp số 2 chữ số từ tất cả số của giải đặc biệt và 4 số còn lại trừ số được chọn"
    
    def calculate(self, data: Dict[str, Any]) -> Dict[str, List[str]]:
        giai_dac_biet = data.get('giai_db', '')
        
        if not giai_dac_biet:
            logger.warning(f"[{self.get_code()}] Thiếu dữ liệu đầu vào: giai_dac_biet={giai_dac_biet}")
            return {'two_digits_loto': []}
        
        try:
            # Kiểm tra độ dài giải đặc biệt (ít nhất 5 số)
            if len(giai_dac_biet) < 5:
                logger.warning(f"[{self.get_code()}] Giải đặc biệt không đủ dài: {giai_dac_biet}")
                return {'two_digits_loto': []}
                
            # Số thứ nhất: lấy tất cả các số của giải đặc biệt
            # Ví dụ: 70103 -> [7, 0, 1, 0, 3]
            first_digits = list(giai_dac_biet)
            
            # Tạo các cặp số 2 chữ số
            two_digits = set()
            for i, first in enumerate(first_digits):
                # Số thứ hai: lấy tất cả số trừ số được chọn (first tại vị trí i)
                # Ví dụ: nếu first = 7, thì second_digits = [0, 1, 0, 3]
                second_digits = [d for j, d in enumerate(first_digits) if j != i]
                
                # Nếu không đủ 4 số cho second_digits, bỏ qua
                if len(second_digits) < 4:
                    continue
                
                # Lấy 4 số từ second_digits
                second_digits = second_digits[:4]
                
                for second in second_digits:
                    # Thêm cặp số thẳng
                    two_digits.add(f"{first}{second}")
                    # Thêm cặp số đảo ngược
                    two_digits.add(f"{second}{first}")
            
            if not two_digits:
                logger.warning(f"[{self.get_code()}] Không tạo được cặp số nào từ dữ liệu: {giai_dac_biet}")
                return {'two_digits_loto': []}
            
            logger.info(f"[{self.get_code()}] Kết quả: {sorted(list(two_digits))}")
            return {
                'two_digits_loto': sorted(list(two_digits))
            }
        except (ValueError, IndexError, TypeError) as e:
            logger.error(f"[{self.get_code()}] Lỗi tính bạch thủ lô 5: {str(e)}")
            return {'two_digits_loto': []}
        
class Btl_3LotoMethod(BasePredictionMethod):
    """
    Phương pháp Bạch thủ lô 3
    Dự đoán từ giải 3.3 (tổng 2 số đầu), giải 3.6 (tổng 2 số đầu), 
    giải 5.1 (số cuối đổi bóng), giải 5.4 (số cuối đổi bóng)
    """
    def get_code(self) -> str:
        return "btl_3"
    
    def get_name(self) -> str:
        return "Bạch thủ lô 3"
    
    def get_description(self) -> str:
        return "Dự đoán các cặp số 2 chữ số từ tổng 2 số đầu giải 3.3, 3.6 và bóng số cuối giải 5.1, 5.4"
    
    def calculate(self, data: Dict[str, Any]) -> Dict[str, List[str]]:
        giai_3_3 = data.get('giai_3_3', '')
        giai_3_6 = data.get('giai_3_6', '')
        giai_5_1 = data.get('giai_5_1', '')
        giai_5_4 = data.get('giai_5_4', '')
        
        if not all([giai_3_3, giai_3_6, giai_5_1, giai_5_4]):
            logger.warning(f"[{self.get_code()}] Thiếu dữ liệu đầu vào: giai_3_3={giai_3_3}, giai_3_6={giai_3_6}, giai_5_1={giai_5_1}, giai_5_4={giai_5_4}")
            return {'two_digits_loto': []}
        
        try:
            # Số thứ nhất: Tổng 2 số đầu giải 3.3
            # Ví dụ: 42115 -> 4+1=5
            if len(giai_3_3) >= 2:
                first_digit = str((int(giai_3_3[0]) + int(giai_3_3[1])) % 10)
            else:
                logger.warning(f"[{self.get_code()}] Giải 3.3 không đủ dài: {giai_3_3}")
                return {'two_digits_loto': []}
                
            # Số thứ hai: Tổng 2 số đầu giải 3.6, lấy hàng đơn vị
            # Ví dụ: 56421 -> 5+6=11 -> 1
            if len(giai_3_6) >= 2:
                second_digit = str((int(giai_3_6[0]) + int(giai_3_6[1])) % 10)
            else:
                logger.warning(f"[{self.get_code()}] Giải 3.6 không đủ dài: {giai_3_6}")
                return {'two_digits_loto': []}
                
            # Số thứ ba: Số cuối giải 5.1, đổi bóng
            # Ví dụ: 5642 -> 2 -> bóng 7
            if len(giai_5_1) >= 1:
                third_digit = str(get_ball_number(giai_5_1[-1]))
            else:
                logger.warning(f"[{self.get_code()}] Giải 5.1 không đủ dài: {giai_5_1}")
                return {'two_digits_loto': []}
                
            # Số thứ tư: Số cuối giải 5.4, đổi bóng
            # Ví dụ: 5313 -> 3 -> bóng 8
            if len(giai_5_4) >= 1:
                fourth_digit = str(get_ball_number(giai_5_4[-1]))
            else:
                logger.warning(f"[{self.get_code()}] Giải 5.4 không đủ dài: {giai_5_4}")
                return {'two_digits_loto': []}
            
            # Tạo các cặp số 2 chữ số
            digits = [first_digit, second_digit, third_digit, fourth_digit]
            two_digits = set()
            # Thêm cặp số thẳng
            two_digits.add(f"{first_digit}{second_digit}")
            two_digits.add(f"{third_digit}{fourth_digit}")
            # Thêm cặp số đảo ngược
            two_digits.add(f"{second_digit}{first_digit}")
            two_digits.add(f"{fourth_digit}{third_digit}")
            
            if not two_digits:
                logger.warning(f"[{self.get_code()}] Không tạo được cặp số nào từ dữ liệu")
                return {'two_digits_loto': []}
            
            logger.info(f"[{self.get_code()}] Kết quả: {sorted(list(two_digits))}")
            return {
                'two_digits_loto': sorted(list(two_digits))
            }
        except (ValueError, IndexError, TypeError) as e:
            logger.error(f"[{self.get_code()}] Lỗi tính bạch thủ lô 6: {str(e)}")
            return {'two_digits_loto': []}
        
class Btl_4LotoMethod(BasePredictionMethod):
    """
    Phương pháp Bạch thủ lô 4
    Dự đoán từ giải 1 (tổng 3 số giữa), tổng số thứ 3 của giải 3.2, số thứ 3 của giải 4.2, số thứ 2 của giải 4.3
    """
    def get_code(self) -> str:
        return "btl_4"
    
    def get_name(self) -> str:
        return "Bạch thủ lô 4"
    
    def get_description(self) -> str:
        return "Dự đoán các cặp số 2 chữ số từ tổng 3 số giữa giải 1 và tổng số thứ 3 của giải 3.2, 4.2, số thứ 2 của giải 4.3"
    
    def calculate(self, data: Dict[str, Any]) -> Dict[str, List[str]]:
        giai_1 = data.get('giai_1', '')
        giai_3_2 = data.get('giai_3_2', '')
        giai_4_2 = data.get('giai_4_2', '')
        giai_4_3 = data.get('giai_4_3', '')
        
        if not all([giai_1, giai_3_2, giai_4_2, giai_4_3]):
            logger.warning(f"[{self.get_code()}] Thiếu dữ liệu đầu vào: giai_1={giai_1}, giai_3_2={giai_3_2}, giai_4_2={giai_4_2}, giai_4_3={giai_4_3}")
            return {'two_digits_loto': []}
        
        try:
            # Số thứ nhất: Tổng 3 số giữa giải 1
            # Ví dụ: 42115 -> 2+1+1=4
            if len(giai_1) >= 5:
                first_digit = str((int(giai_1[1]) + int(giai_1[2]) + int(giai_1[3])) % 10)
            else:
                logger.warning(f"[{self.get_code()}] Giải 1 không đủ dài: {giai_1}")
                return {'two_digits_loto': []}
                
            # Số thứ hai: Tổng của số thứ 3 giải 3.2, số thứ 3 giải 4.2, số thứ 2 giải 4.3
            # Ví dụ: giai_3_2: 56421 -> 6, giai_4_2: 4301 -> 0, giai_4_3: 1234 -> 2, tổng 6+0+2=8
            second_digit_sum = 0
            
            if len(giai_3_2) >= 3:
                second_digit_sum += int(giai_3_2[2])
            else:
                logger.warning(f"[{self.get_code()}] Giải 3.2 không đủ dài: {giai_3_2}")
                return {'two_digits_loto': []}
                
            if len(giai_4_2) >= 3:
                second_digit_sum += int(giai_4_2[2])
            else:
                logger.warning(f"[{self.get_code()}] Giải 4.2 không đủ dài: {giai_4_2}")
                return {'two_digits_loto': []}
                
            if len(giai_4_3) >= 2:
                second_digit_sum += int(giai_4_3[1])
            else:
                logger.warning(f"[{self.get_code()}] Giải 4.3 không đủ dài: {giai_4_3}")
                return {'two_digits_loto': []}
                
            second_digit = str(second_digit_sum % 10)
            
            # Tạo các cặp số 2 chữ số
            digits = [first_digit, second_digit]
            two_digits = set()
            # Thêm cặp số thẳng
            two_digits.add(f"{first_digit}{second_digit}")
            # Thêm cặp số đảo ngược
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
            logger.error(f"[{self.get_code()}] Lỗi tính bạch thủ lô 7: {str(e)}")
            return {'two_digits_loto': []}
        
class Btl_5LotoMethod(BasePredictionMethod):
    """
    Phương pháp Bạch thủ lô 5
    Dự đoán từ giải 4.3 (tổng 2 số giữa, số cuối), giải 5.1 (số đầu), giải 5.4 (số đầu)
    """
    def get_code(self) -> str:
        return "btl_5"
    
    def get_name(self) -> str:
        return "Bạch thủ lô 5"
    
    def get_description(self) -> str:
        return "Dự đoán các cặp số 2 chữ số từ tổng 2 số giữa và số cuối giải 4.3, số đầu giải 5.1 và 5.4"
    
    def calculate(self, data: Dict[str, Any]) -> Dict[str, List[str]]:
        giai_4_3 = data.get('giai_4_3', '')
        giai_5_1 = data.get('giai_5_1', '')
        giai_5_4 = data.get('giai_5_4', '')
        
        if not all([giai_4_3, giai_5_1, giai_5_4]):
            logger.warning(f"[{self.get_code()}] Thiếu dữ liệu đầu vào: giai_4_3={giai_4_3}, giai_5_1={giai_5_1}, giai_5_4={giai_5_4}")
            return {'two_digits_loto': []}
        
        try:
            # Số thứ nhất: Tổng 2 số giữa giải 4.3
            # Ví dụ: 4215 -> 2+1=3
            if len(giai_4_3) >= 4:
                first_digit = str((int(giai_4_3[1]) + int(giai_4_3[2])) % 10)
            else:
                logger.warning(f"[{self.get_code()}] Giải 4.3 không đủ dài: {giai_4_3}")
                return {'two_digits_loto': []}
                
            # Số thứ hai: Số cuối giải 4.3
            # Ví dụ: 4215 -> 5
            if len(giai_4_3) >= 1:
                second_digit = giai_4_3[-1]
            else:
                logger.warning(f"[{self.get_code()}] Giải 4.3 không đủ dài: {giai_4_3}")
                return {'two_digits_loto': []}
                
            # Số thứ ba: Số đầu giải 5.1
            # Ví dụ: 5234 -> 5
            if len(giai_5_1) >= 1:
                third_digit = giai_5_1[0]
            else:
                logger.warning(f"[{self.get_code()}] Giải 5.1 không đủ dài: {giai_5_1}")
                return {'two_digits_loto': []}
                
            # Số thứ tư: Số đầu giải 5.4
            # Ví dụ: 4132 -> 4
            if len(giai_5_4) >= 1:
                fourth_digit = giai_5_4[0]
            else:
                logger.warning(f"[{self.get_code()}] Giải 5.4 không đủ dài: {giai_5_4}")
                return {'two_digits_loto': []}
            
            # Tạo các cặp số 2 chữ số
            digits = [first_digit, second_digit, third_digit, fourth_digit]
            two_digits = set()
        
            # Thêm cặp số thẳng
            two_digits.add(f"{first_digit}{second_digit}")
            two_digits.add(f"{third_digit}{fourth_digit}")
            # Thêm cặp số đảo ngược
            two_digits.add(f"{second_digit}{first_digit}")
            two_digits.add(f"{fourth_digit}{third_digit}")
            
            if not two_digits:
                logger.warning(f"[{self.get_code()}] Không tạo được cặp số nào từ dữ liệu")
                return {'two_digits_loto': []}
            
            logger.info(f"[{self.get_code()}] Kết quả: {sorted(list(two_digits))}")
            return {
                'two_digits_loto': sorted(list(two_digits))
            }
        except (ValueError, IndexError, TypeError) as e:
            logger.error(f"[{self.get_code()}] Lỗi tính bạch thủ lô 8: {str(e)}")
            return {'two_digits_loto': []}

class Btl_6LotoMethod(BasePredictionMethod):
    """
    Phương pháp Bạch thủ lô 6
    Dự đoán từ tổng số thứ 3 giải 1, số thứ 1 giải 3.4, số thứ 5 giải 3.6 và tổng 3 số giữa giải 3.5
    """
    def get_code(self) -> str:
        return "btl_6"
    
    def get_name(self) -> str:
        return "Bạch thủ lô 6"
    
    def get_description(self) -> str:
        return "Dự đoán các cặp số 2 chữ số từ tổng số thứ 3 giải 1, số thứ 1 giải 3.4, số thứ 5 giải 3.6 và tổng 3 số giữa giải 3.5"
    
    def calculate(self, data: Dict[str, Any]) -> Dict[str, List[str]]:
        giai_1 = data.get('giai_1', '')
        giai_3_4 = data.get('giai_3_4', '')
        giai_3_6 = data.get('giai_3_6', '')
        giai_3_5 = data.get('giai_3_5', '')
        
        if not all([giai_1, giai_3_4, giai_3_6, giai_3_5]):
            logger.warning(f"[{self.get_code()}] Thiếu dữ liệu đầu vào: giai_1={giai_1}, giai_3_4={giai_3_4}, giai_3_6={giai_3_6}, giai_3_5={giai_3_5}")
            return {'two_digits_loto': []}
        
        try:
            # Số thứ nhất: Tổng của số thứ 3 giải 1, số thứ 1 giải 3.4, số thứ 5 giải 3.6
            # Ví dụ: giai_1: 14215 -> 2, giai_3_4: 45245 -> 4, giai_3_6: 32423 -> 3, tổng 2+4+3=9
            first_digit_sum = 0
            
            if len(giai_1) >= 3:
                first_digit_sum += int(giai_1[2])
            else:
                logger.warning(f"[{self.get_code()}] Giải 1 không đủ dài: {giai_1}")
                return {'two_digits_loto': []}
                
            if len(giai_3_4) >= 1:
                first_digit_sum += int(giai_3_4[0])
            else:
                logger.warning(f"[{self.get_code()}] Giải 3.4 không đủ dài: {giai_3_4}")
                return {'two_digits_loto': []}
                
            if len(giai_3_6) >= 5:
                first_digit_sum += int(giai_3_6[4])
            else:
                logger.warning(f"[{self.get_code()}] Giải 3.6 không đủ dài: {giai_3_6}")
                return {'two_digits_loto': []}
                
            first_digit = str(first_digit_sum % 10)
            
            # Số thứ hai: Tổng 3 số giữa giải 3.5
            # Ví dụ: 14215 -> 4+2+1=7
            if len(giai_3_5) >= 5:
                second_digit = str((int(giai_3_5[1]) + int(giai_3_5[2]) + int(giai_3_5[3])) % 10)
            else:
                logger.warning(f"[{self.get_code()}] Giải 3.5 không đủ dài: {giai_3_5}")
                return {'two_digits_loto': []}
            
            # Tạo các cặp số 2 chữ số
            digits = [first_digit, second_digit]
            two_digits = set()
            # Thêm cặp số thẳng
            two_digits.add(f"{first_digit}{second_digit}")
            # Thêm cặp số đảo ngược
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
            logger.error(f"[{self.get_code()}] Lỗi tính bạch thủ lô 9: {str(e)}")
            return {'two_digits_loto': []}


class Btl_7LotoMethod(BasePredictionMethod):
    """
    Phương pháp Bạch thủ lô 7
    Dự đoán từ giải 1 (tổng số thứ 3 và 4, số thứ 5 đổi bóng), giải 3.2 (số thứ 1), giải 3.5 (số thứ 1)
    """
    def get_code(self) -> str:
        return "btl_7"
    
    def get_name(self) -> str:
        return "Bạch thủ lô 7"
    
    def get_description(self) -> str:
        return "Dự đoán các cặp số 2 chữ số từ tổng số thứ 3 và 4 giải 1, số thứ 5 giải 1 đổi bóng, số thứ 1 giải 3.2 và 3.5"
    
    def calculate(self, data: Dict[str, Any]) -> Dict[str, List[str]]:
        giai_1 = data.get('giai_1', '')
        giai_3_2 = data.get('giai_3_2', '')
        giai_3_5 = data.get('giai_3_5', '')
        
        if not all([giai_1, giai_3_2, giai_3_5]):
            logger.warning(f"[{self.get_code()}] Thiếu dữ liệu đầu vào: giai_1={giai_1}, giai_3_2={giai_3_2}, giai_3_5={giai_3_5}")
            return {'two_digits_loto': []}
        
        try:
            # Số thứ nhất: Tổng số thứ 3 và thứ 4 giải 1
            # Ví dụ: 14215 -> 2+1=3
            if len(giai_1) >= 4:
                first_digit = str((int(giai_1[2]) + int(giai_1[3])) % 10)
            else:
                logger.warning(f"[{self.get_code()}] Giải 1 không đủ dài: {giai_1}")
                return {'two_digits_loto': []}
                
            # Số thứ hai: Số thứ 5 giải 1, đổi bóng
            # Ví dụ: 14215 -> 5 -> bóng 0
            if len(giai_1) >= 5:
                second_digit = str(get_ball_number(giai_1[4]))
            else:
                logger.warning(f"[{self.get_code()}] Giải 1 không đủ dài: {giai_1}")
                return {'two_digits_loto': []}
                
            # Số thứ ba: Số thứ 1 giải 3.2
            # Ví dụ: 51234 -> 5
            if len(giai_3_2) >= 1:
                third_digit = giai_3_2[0]
            else:
                logger.warning(f"[{self.get_code()}] Giải 3.2 không đủ dài: {giai_3_2}")
                return {'two_digits_loto': []}
                
            # Số thứ tư: Số thứ 1 giải 3.5
            # Ví dụ: 64132 -> 6
            if len(giai_3_5) >= 1:
                fourth_digit = giai_3_5[0]
            else:
                logger.warning(f"[{self.get_code()}] Giải 3.5 không đủ dài: {giai_3_5}")
                return {'two_digits_loto': []}
            
            # Tạo các cặp số 2 chữ số
            digits = [first_digit, second_digit, third_digit, fourth_digit]
            two_digits = set()
            # Thêm cặp số thẳng
            two_digits.add(f"{first_digit}{second_digit}")
            # Thêm cặp số đảo ngược
            two_digits.add(f"{second_digit}{first_digit}")
            # Thêm cặp số thẳng
            two_digits.add(f"{fourth_digit}{third_digit}")
            # Thêm cặp số đảo ngược
            two_digits.add(f"{third_digit}{fourth_digit}")
            
            if not two_digits:
                logger.warning(f"[{self.get_code()}] Không tạo được cặp số nào từ dữ liệu")
                return {'two_digits_loto': []}
            
            logger.info(f"[{self.get_code()}] Kết quả: {sorted(list(two_digits))}")
            return {
                'two_digits_loto': sorted(list(two_digits))
            }
        except (ValueError, IndexError, TypeError) as e:
            logger.error(f"[{self.get_code()}] Lỗi tính bạch thủ lô 10: {str(e)}")
            return {'two_digits_loto': []}


class Btl_8LotoMethod(BasePredictionMethod):
    """
    Phương pháp Bạch thủ lô 8
    Dự đoán từ tổng số thứ 1 giải 2.2, số thứ 4 giải 4.2, số thứ 4 giải 4.3 và tổng số thứ 5 giải 3.5, số thứ 2 giải 4.4, số thứ 4 giải 5.5
    """
    def get_code(self) -> str:
        return "btl_8"
    
    def get_name(self) -> str:
        return "Bạch thủ lô 8"
    
    def get_description(self) -> str:
        return "Dự đoán các cặp số 2 chữ số từ tổng số thứ 1 giải 2.2, số thứ 4 giải 4.2, số thứ 4, và tổng số thứ 5 giải 3.5, số thứ 2 giải 4.4, số thứ 4 5.5"
    
    def calculate(self, data: Dict[str, Any]) -> Dict[str, List[str]]:
        giai_2_2 = data.get('giai_2_2', '')
        giai_4_2 = data.get('giai_4_2', '')
        giai_4_3 = data.get('giai_4_3', '')
        giai_3_5 = data.get('giai_3_5', '')
        giai_4_4 = data.get('giai_4_4', '')
        giai_5_5 = data.get('giai_5_5', '')
        
        if not all([giai_2_2, giai_4_2, giai_4_3, giai_3_5, giai_4_4, giai_5_5]):
            logger.warning(f"[{self.get_code()}] Thiếu dữ liệu đầu vào: giai_2_2={giai_2_2}, giai_4_2={giai_4_2}, giai_4_3={giai_4_3}, giai_3_5={giai_3_5}, giai_4_4={giai_4_4}, giai_5_5={giai_5_5}")
            return {'two_digits_loto': []}
        
        try:
            # Số thứ nhất: Tổng của số thứ 1 giải 2, số thứ 4 giải 4.2, số thứ 4 giải 4.3
            # Ví dụ: giai_2_2: 14215 -> 1, giai_4_2: 4524 -> 4, giai_4_3: 3243 -> 3, tổng=4+1=8
            first_digit_sum = 0
            
            if len(giai_2_2) >= 1:
                first_digit_sum += int(giai_2_2[0])
            else:
                logger.warning(f"[{self.get_code()}] Giải 2.2 không đủ dài: {giai_2_2}")
                return {'two_digits_loto': []}
                
            if len(giai_4_2) >= 4:
                first_digit_sum += int(giai_4_2[3])
            else:
                logger.warning(f"[{self.get_code()}] Giải 4.2 không đủ dài: {giai_4_2}")
                return {'two_digits_loto': []}
                
            if len(giai_4_3) >= 4:
                first_digit_sum += int(giai_4_3[3])
            else:
                logger.warning(f"[{self.get_code()}] Giải 4.3 không đủ dài: {giai_4_3}")
                return {'two_digits_loto': []}
                
            first_digit = str(first_digit_sum % 10)
            
            # Số thứ hai: Tổng của số thứ 5 giải 3.5, số thứ 2 giải 4, số thứ 4 giải 5, thứ 5
            # Ví dụ: giai_3_5: 14215 -> 5, giai_4_4: 4524 -> 5, giai_5_5: 3243 -> 3, tổng 5+4+3=12 -> 3
            second_digit_sum = 0
            
            if len(giai_3_5) >= 5:
                second_digit_sum += int(giai_3_5[4])
            else:
                logger.warning(f"[{self.get_code()}] Giải 3.5 không đủ dài: {giai_3_5}")
                return {'two_digits_loto': []}
                
            if len(giai_4_4) >= 2:
                second_digit_sum += int(giai_4_4[1])
            else:
                logger.warning(f"[{self.get_code()}] Giải 4.4 không đủ dài: {giai_4_4}")
                return {'two_digits_loto': []}
                
            if len(giai_5_5) >= 4:
                second_digit_sum += int(giai_5_5[3])
            else:
                logger.warning(f"[{self.get_code()}] Giải 5.5 không đủ dài: {giai_5_5}")
                return {'two_digits_loto': []}
                
            second_digit = str(second_digit_sum % 10)
            
            # Tạo các cặp số 2 chữ số
            digits = [first_digit, second_digit]
            two_digits = set()
            # Thêm cặp số thẳng
            two_digits.add(f"{first_digit}{second_digit}")
            # Thêm cặp số đảo ngược
            if first_digit != second_digit:  # Tránh cặp trùng nếu số giống nhau
                two_digits.add(f"{second_digit}{second_digit}")
            
            if not two_digits:
                logger.warning(f"[{self.get_code()}] Không tạo được cặp số nào từ dữ liệu")
                return {'two_digits_loto': []}
            
            logger.info(f"[{self.get_code()}] Kết quả: {sorted(list(two_digits))}")
            return {
                'two_digits_loto': sorted(list(two_digits))
            }
        except (ValueError, TypeError, IndexError) as e:
            logger.error(f"[{self.get_code()}] Lỗi tính bạch thủ lô 8: {str(e)}")
            return {'two_digits_loto': []}


class Btl_9LotoMethod(BasePredictionMethod):
    """
    Phương pháp Bạch thủ lô 9
    Dự đoán từ tổng số thứ 3 giải 1, số thứ 2 giải 4.2, số thứ 3 giải 4.3 và tổng số thứ 3 giải 2.1, số thứ 3 giải 2.2, số thứ 3 giải 3.5
    """
    def get_code(self) -> str:
        return "btl_9"
    
    def get_name(self) -> str:
        return "Bạch thủ lô 9"
    
    def get_description(self) -> str:
        return "Dự đoán các cặp số 2 chữ số từ tổng số thứ 3 giải 1, số thứ 2 giải 4.2, số thứ 3 giải 4.3 và tổng số thứ 3 giải 2.1, số thứ 3 giải 2.2, số thứ 3 giải 3.5"
    
    def calculate(self, data: Dict[str, Any]) -> Dict[str, List[str]]:
        giai_1 = data.get('giai_1', '')
        giai_4_2 = data.get('giai_4_2', '')
        giai_4_3 = data.get('giai_4_3', '')
        giai_2_1 = data.get('giai_2_1', '')
        giai_2_2 = data.get('giai_2_2', '')
        giai_3_5 = data.get('giai_3_5', '')
        
        if not all([giai_1, giai_4_2, giai_4_3, giai_2_1, giai_2_2, giai_3_5]):
            logger.warning(f"[{self.get_code()}] Thiếu dữ liệu đầu vào: giai_1={giai_1}, giai_4_2={giai_4_2}, giai_4_3={giai_4_3}, giai_2_1={giai_2_1}, giai_2_2={giai_2_2}, giai_3_5={giai_3_5}")
            return {'two_digits_loto': []}
        
        try:
            # Số thứ nhất: Tổng của số thứ 3 giải 1, số thứ 2 giải 4.2, số thứ 3 giải 4.3
            # Ví dụ: giai_1: 14215 -> 2, giai_4_2: 4524 -> 5, giai_4_3: 3243 -> 4, tổng 2+5+4=11 -> 1
            first_digit_sum = 0
            
            if len(giai_1) >= 3:
                first_digit_sum += int(giai_1[2])
            else:
                logger.warning(f"[{self.get_code()}] Giải 1 không đủ dài: {giai_1}")
                return {'two_digits_loto': []}
                
            if len(giai_4_2) >= 2:
                first_digit_sum += int(giai_4_2[1])
            else:
                logger.warning(f"[{self.get_code()}] Giải 4.2 không đủ dài: {giai_4_2}")
                return {'two_digits_loto': []}
                
            if len(giai_4_3) >= 3:
                first_digit_sum += int(giai_4_3[2])
            else:
                logger.warning(f"[{self.get_code()}] Giải 4.3 không đủ dài: {giai_4_3}")
                return {'two_digits_loto': []}
                
            first_digit = str(first_digit_sum % 10)
            
            # Số thứ hai: Tổng của số thứ 3 giải 2.1, số thứ 3 giải 2.2, số thứ 3 giải 3.5
            # Ví dụ: giai_2_1: 14215 -> 2, giai_2_2: 14524 -> 5, giai_3_5: 13243 -> 2, tổng 2+5+2=9
            second_digit_sum = 0
            
            if len(giai_2_1) >= 3:
                second_digit_sum += int(giai_2_1[2])
            else:
                logger.warning(f"[{self.get_code()}] Giải 2.1 không đủ dài: {giai_2_1}")
                return {'two_digits_loto': []}
                
            if len(giai_2_2) >= 3:
                second_digit_sum += int(giai_2_2[2])
            else:
                logger.warning(f"[{self.get_code()}] Giải 2.2 không đủ dài: {giai_2_2}")
                return {'two_digits_loto': []}
                
            if len(giai_3_5) >= 3:
                second_digit_sum += int(giai_3_5[2])
            else:
                logger.warning(f"[{self.get_code()}] Giải 3.5 không đủ dài: {giai_3_5}")
                return {'two_digits_loto': []}
                
            second_digit = str(second_digit_sum % 10)
            
            # Tạo các cặp số 2 chữ số
            digits = [first_digit, second_digit]
            two_digits = set()
            # Thêm cặp số thẳng
            two_digits.add(f"{first_digit}{second_digit}")
            # Thêm cặp số đảo ngược
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
            logger.error(f"[{self.get_code()}] Lỗi tính bạch thủ lô 9: {str(e)}")
            return {'two_digits_loto': []}
        

class Btl_10LotoMethod(BasePredictionMethod):
    """
    Phương pháp Bạch thủ lô 10
    Dự đoán từ tổng số thứ 1 giải 3.2, số thứ 1 giải 3.5 và tổng số thứ 1 giải 5.2, số thứ 1 giải 5.5
    """
    def get_code(self) -> str:
        return "btl_10"
    
    def get_name(self) -> str:
        return "Bạch thủ lô 10"
    
    def get_description(self) -> str:
        return "Dự đoán các cặp số 2 chữ số từ tổng số thứ 1 giải 3.2, số thứ 1 giải 3.5 và tổng số thứ 1 giải 5.2, số thứ 1 giải 5.5"
    
    def calculate(self, data: Dict[str, Any]) -> Dict[str, List[str]]:
        giai_3_2 = data.get('giai_3_2', '')
        giai_3_5 = data.get('giai_3_5', '')
        giai_5_2 = data.get('giai_5_2', '')
        giai_5_5 = data.get('giai_5_5', '')
        
        if not all([giai_3_2, giai_3_5, giai_5_2, giai_5_5]):
            logger.warning(f"[{self.get_code()}] Thiếu dữ liệu đầu vào: giai_3_2={giai_3_2}, giai_3_5={giai_3_5}, giai_5_2={giai_5_2}, giai_5_5={giai_5_5}")
            return {'two_digits_loto': []}
        
        try:
            # Số thứ nhất: Tổng của số thứ 1 giải 3.2, số thứ 1 giải 3.5
            # Ví dụ: giai_3_2: 14215 -> 1, giai_3_5: 42331 -> 4, tổng 1+4=5
            first_digit_sum = 0
            
            if len(giai_3_2) >= 1:
                first_digit_sum += int(giai_3_2[0])
            else:
                logger.warning(f"[{self.get_code()}] Giải 3.2 không đủ dài: {giai_3_2}")
                return {'two_digits_loto': []}
                
            if len(giai_3_5) >= 1:
                first_digit_sum += int(giai_3_5[0])
            else:
                logger.warning(f"[{self.get_code()}] Giải 3.5 không đủ dài: {giai_3_5}")
                return {'two_digits_loto': []}
                
            first_digit = str(first_digit_sum % 10)
            
            # Số thứ hai: Tổng của số thứ 1 giải 5.2, số thứ 1 giải 5.5
            # Ví dụ: giai_5_2: 4215 -> 4, giai_5_5: 2331 -> 2, tổng 4+2=6
            second_digit_sum = 0
            
            if len(giai_5_2) >= 1:
                second_digit_sum += int(giai_5_2[0])
            else:
                logger.warning(f"[{self.get_code()}] Giải 5.2 không đủ dài: {giai_5_2}")
                return {'two_digits_loto': []}
                
            if len(giai_5_5) >= 1:
                second_digit_sum += int(giai_5_5[0])
            else:
                logger.warning(f"[{self.get_code()}] Giải 5.5 không đủ dài: {giai_5_5}")
                return {'two_digits_loto': []}
                
            second_digit = str(second_digit_sum % 10)
            
            # Tạo các cặp số 2 chữ số
            digits = [first_digit, second_digit]
            two_digits = set()
            # Thêm cặp số thẳng
            two_digits.add(f"{first_digit}{second_digit}")
            # Thêm cặp số đảo ngược
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
            logger.error(f"[{self.get_code()}] Lỗi tính bạch thủ lô 10: {str(e)}")
            return {'two_digits_loto': []}


class Btl_22LotoMethod(BasePredictionMethod):
    """
    Phương pháp Bạch thủ lô 22
    Dự đoán từ tổng số thứ 4 và 5 giải 2.1, tổng số thứ 1 và 2 giải 2.2, tổng số thứ 1 và 2 giải 7.1, số thứ 1 giải 7.3
    """
    def get_code(self) -> str:
        return "btl_22"
    
    def get_name(self) -> str:
        return "Bạch thủ lô 22"
    
    def get_description(self) -> str:
        return "Dự đoán các cặp số 2 chữ số từ tổng số thứ 4 và 5 giải 2.1, tổng số thứ 1 và 2 giải 2.2, tổng số thứ 1 và 2 giải 7.1, số thứ 1 giải 7.3"
    
    def calculate(self, data: Dict[str, Any]) -> Dict[str, List[str]]:
        giai_2_1 = data.get('giai_2_1', '')
        giai_2_2 = data.get('giai_2_2', '')
        giai_7_1 = data.get('giai_7_1', '')
        giai_7_3 = data.get('giai_7_3', '')
        
        if not all([giai_2_1, giai_2_2, giai_7_1, giai_7_3]):
            logger.warning(f"[{self.get_code()}] Thiếu dữ liệu đầu vào: giai_2_1={giai_2_1}, giai_2_2={giai_2_2}, giai_7_1={giai_7_1}, giai_7_3={giai_7_3}")
            return {'two_digits_loto': []}
        
        try:
            # Số thứ nhất: Tổng số thứ 4 và số thứ 5 giải 2.1
            # Ví dụ: 14162 -> 6+2=8
            if len(giai_2_1) >= 5:
                first_digit = str((int(giai_2_1[3]) + int(giai_2_1[4])) % 10)
            else:
                logger.warning(f"[{self.get_code()}] Giải 2.1 không đủ dài: {giai_2_1}")
                return {'two_digits_loto': []}
                
            # Số thứ hai: Tổng số thứ 1 và số thứ 2 giải 2.2
            # Ví dụ: 51411 -> 5+1=6
            if len(giai_2_2) >= 2:
                second_digit = str((int(giai_2_2[0]) + int(giai_2_2[1])) % 10)
            else:
                logger.warning(f"[{self.get_code()}] Giải 2.2 không đủ dài: {giai_2_2}")
                return {'two_digits_loto': []}
                
            # Số thứ ba: Tổng số thứ 1 và số thứ 2 giải 7.1
            # Ví dụ: 12 -> 1+2=3
            if len(giai_7_1) >= 2:
                third_digit = str((int(giai_7_1[0]) + int(giai_7_1[1])) % 10)
            else:
                logger.warning(f"[{self.get_code()}] Giải 7.1 không đủ dài: {giai_7_1}")
                return {'two_digits_loto': []}
                
            # Số thứ tư: Số thứ 1 giải 7.3
            # Ví dụ: 41 -> 4
            if len(giai_7_3) >= 1:
                fourth_digit = giai_7_3[0]
            else:
                logger.warning(f"[{self.get_code()}] Giải 7.3 không đủ dài: {giai_7_3}")
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
            logger.error(f"[{self.get_code()}] Lỗi tính bạch thủ lô 22: {str(e)}")
            return {'two_digits_loto': []}
        

class Btl_27LotoMethod(BasePredictionMethod):
    """
    Phương pháp Bạch thủ lô 27
    Dự đoán từ tổng số thứ 1 giải 3.1 và 3.4, tổng số thứ 5 giải 3.3 và 3.6, số thứ 1 giải 5.4, số thứ 4 giải 5.6
    """
    def get_code(self) -> str:
        return "btl_27"
    
    def get_name(self) -> str:
        return "Bạch thủ lô 27"
    
    def get_description(self) -> str:
        return "Dự đoán các cặp số 2 chữ số từ tổng số thứ 1 giải 3.1 và 3.4, tổng số thứ 5 giải 3.3 và 3.6, số thứ 1 giải 5.4, số thứ 4 giải 5.6"
    
    def calculate(self, data: Dict[str, Any]) -> Dict[str, List[str]]:
        giai_3_1 = data.get('giai_3_1', '')
        giai_3_4 = data.get('giai_3_4', '')
        giai_3_3 = data.get('giai_3_3', '')
        giai_3_6 = data.get('giai_3_6', '')
        giai_5_4 = data.get('giai_5_4', '')
        giai_5_6 = data.get('giai_5_6', '')
        
        if not all([giai_3_1, giai_3_4, giai_3_3, giai_3_6, giai_5_4, giai_5_6]):
            logger.warning(f"[{self.get_code()}] Thiếu dữ liệu đầu vào: giai_3_1={giai_3_1}, giai_3_4={giai_3_4}, giai_3_3={giai_3_3}, giai_3_6={giai_3_6}, giai_5_4={giai_5_4}, giai_5_6={giai_5_6}")
            return {'two_digits_loto': []}
        
        try:
            # Số thứ nhất: Tổng số thứ 1 giải 3.1 và giải 3.4
            # Ví dụ: giai_3_1: 14215 -> 1, giai_3_4: 54524 -> 5, tổng 1+5=6
            first_digit_sum = 0
            
            if len(giai_3_1) >= 1:
                first_digit_sum += int(giai_3_1[0])
            else:
                logger.warning(f"[{self.get_code()}] Giải 3.1 không đủ dài: {giai_3_1}")
                return {'two_digits_loto': []}
                
            if len(giai_3_4) >= 1:
                first_digit_sum += int(giai_3_4[0])
            else:
                logger.warning(f"[{self.get_code()}] Giải 3.4 không đủ dài: {giai_3_4}")
                return {'two_digits_loto': []}
                
            first_digit = str(first_digit_sum % 10)
            
            # Số thứ hai: Tổng số thứ 5 giải 3.3 và giải 3.6
            # Ví dụ: giai_3_3: 14215 -> 5, giai_3_6: 14524 -> 4, tổng 5+4=9
            second_digit_sum = 0
            
            if len(giai_3_3) >= 5:
                second_digit_sum += int(giai_3_3[4])
            else:
                logger.warning(f"[{self.get_code()}] Giải 3.3 không đủ dài: {giai_3_3}")
                return {'two_digits_loto': []}
                
            if len(giai_3_6) >= 5:
                second_digit_sum += int(giai_3_6[4])
            else:
                logger.warning(f"[{self.get_code()}] Giải 3.6 không đủ dài: {giai_3_6}")
                return {'two_digits_loto': []}
                
            second_digit = str(second_digit_sum % 10)
            
            # Số thứ ba: Số thứ 1 giải 5.4
            # Ví dụ: 1415 -> 1
            if len(giai_5_4) >= 1:
                third_digit = giai_5_4[0]
            else:
                logger.warning(f"[{self.get_code()}] Giải 5.4 không đủ dài: {giai_5_4}")
                return {'two_digits_loto': []}
                
            # Số thứ tư: Số thứ 4 giải 5.6
            # Ví dụ: 4215 -> 5
            if len(giai_5_6) >= 4:
                fourth_digit = giai_5_6[3]
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
            logger.error(f"[{self.get_code()}] Lỗi tính bạch thủ lô 27: {str(e)}")
            return {'two_digits_loto': []}



class Btl_30LotoMethod(BasePredictionMethod):
    """
    Phương pháp Bạch thủ lô 30
    Dự đoán từ số thứ 4 giải đặc biệt, số thứ 1 giải 6.2
    """
    def get_code(self) -> str:
        return "btl_30"
    
    def get_name(self) -> str:
        return "Bạch thủ lô 30"
    
    def get_description(self) -> str:
        return "Dự đoán các cặp số 2 chữ số từ số thứ 4 giải đặc biệt và số thứ 1 giải 6.2"
    
    def calculate(self, data: Dict[str, Any]) -> Dict[str, List[str]]:
        giai_dac_biet = data.get('giai_db', '')
        giai_dac_biet = data.get('giai_db', '')
        giai_6_2 = data.get('giai_6_2', '')
        
        if not all([giai_dac_biet, giai_6_2]):
            logger.warning(f"[{self.get_code()}] Thiếu dữ liệu đầu vào: giai_dac_biet={giai_dac_biet}, giai_6_2={giai_6_2}")
            return {'two_digits_loto': []}
        
        try:
            # Số thứ nhất: Số thứ 4 giải đặc biệt
            # Ví dụ: 11421 -> 2
            if len(giai_dac_biet) >= 4:
                first_digit = giai_dac_biet[3]
            else:
                logger.warning(f"[{self.get_code()}] Giải đặc biệt không đủ dài: {giai_dac_biet}")
                return {'two_digits_loto': []}
                
            # Số thứ hai: Số thứ 1 giải 6.2
            # Ví dụ: 131 -> 1
            if len(giai_6_2) >= 1:
                second_digit = giai_6_2[0]
            else:
                logger.warning(f"[{self.get_code()}] Giải 6.2 không đủ dài: {giai_6_2}")
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



class Btl_18LotoMethod(BasePredictionMethod):
    """
    Phương pháp Bạch thủ lô 18
    Dự đoán từ số thứ 2 giải 3.1, số thứ 3 giải 3.3
    """
    def get_code(self) -> str:
        return "btl_18"
    
    def get_name(self) -> str:
        return "Bạch thủ lô 18"
    
    def get_description(self) -> str:
        return "Dự đoán các cặp số 2 chữ số từ số thứ 2 giải 3.1 và số thứ 3 giải 3.3"
    
    def calculate(self, data: Dict[str, Any]) -> Dict[str, List[str]]:
        giai_3_1 = data.get('giai_3_1', '')
        giai_3_3 = data.get('giai_3_3', '')
        
        if not all([giai_3_1, giai_3_3]):
            logger.warning(f"[{self.get_code()}] Thiếu dữ liệu đầu vào: giai_3_1={giai_3_1}, giai_3_3={giai_3_3}")
            return {'two_digits_loto': []}
        
        try:
            # Số thứ nhất: Số thứ 2 giải 3.1
            # Ví dụ: 14215 -> 4
            if len(giai_3_1) >= 2:
                first_digit = giai_3_1[1]
            else:
                logger.warning(f"[{self.get_code()}] Giải 3.1 không đủ dài: {giai_3_1}")
                return {'two_digits_loto': []}
                
            # Số thứ hai: Số thứ 3 giải 3.3
            # Ví dụ: 14215 -> 3
            if len(giai_3_3) >= 3:
                second_digit = giai_3_3[2]
            else:
                logger.warning(f"[{self.get_code()}] Giải 3.3 không đủ dài: {giai_3_3}")
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
            logger.error(f"[{self.get_code()}] Lỗi tính bạch thủ lô 18: {str(e)}")
            return {'two_digits_loto': []}


class Btl_26LotoMethod(BasePredictionMethod):
    """
    Phương pháp Bạch thủ lô 26
    Dự đoán từ số thứ 1 và 2 giải đặc biệt, tổng số thứ 1 và 2 giải 4.2, tổng số thứ 3 và 4 giải 4.3
    """
    def get_code(self) -> str:
        return "btl_26"
    
    def get_name(self) -> str:
        return "Bạch thủ lô 26"
    
    def get_description(self) -> str:
        return "Dự đoán các cặp số 2 chữ số từ số thứ 1 và 2 giải đặc biệt, tổng số thứ 1 và 2 giải 4.2, tổng số thứ 3 và 4 giải 4.3"
    
    def calculate(self, data: Dict[str, Any]) -> Dict[str, List[str]]:
        giai_dac_biet = data.get('giai_db', '')
        giai_4_2 = data.get('giai_4_2', '')
        giai_4_3 = data.get('giai_4_3', '')
        
        if not all([giai_dac_biet, giai_4_2, giai_4_3]):
            logger.warning(f"[{self.get_code()}] Thiếu dữ liệu đầu vào: giai_dac_biet={giai_dac_biet}, giai_4_2={giai_4_2}, giai_4_3={giai_4_3}")
            return {'two_digits_loto': []}
        
        try:
            # Số thứ nhất: Số thứ 1 giải đặc biệt
            # Ví dụ: 41612 -> 4
            if len(giai_dac_biet) >= 1:
                first_digit = giai_dac_biet[0]
            else:
                logger.warning(f"[{self.get_code()}] Giải đặc biệt không đủ dài: {giai_dac_biet}")
                return {'two_digits_loto': []}
                
            # Số thứ hai: Số thứ 2 giải đặc biệt
            # Ví dụ: 41612 -> 1
            if len(giai_dac_biet) >= 2:
                second_digit = giai_dac_biet[1]
            else:
                logger.warning(f"[{self.get_code()}] Giải đặc biệt không đủ dài: {giai_dac_biet}")
                return {'two_digits_loto': []}
                
            # Số thứ ba: Tổng số thứ 1 và số thứ 2 giải 4.2
            # Ví dụ: 1212 -> 1+2=3
            if len(giai_4_2) >= 2:
                third_digit = str((int(giai_4_2[0]) + int(giai_4_2[1])) % 10)
            else:
                logger.warning(f"[{self.get_code()}] Giải 4.2 không đủ dài: {giai_4_2}")
                return {'two_digits_loto': []}
                
            # Số thứ tư: Tổng số thứ 3 và số thứ 4 giải 4.3
            # Ví dụ: 4251 -> 5+1=6
            if len(giai_4_3) >= 4:
                fourth_digit = str((int(giai_4_3[2]) + int(giai_4_3[3])) % 10)
            else:
                logger.warning(f"[{self.get_code()}] Giải 4.3 không đủ dài: {giai_4_3}")
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
            logger.error(f"[{self.get_code()}] Lỗi tính bạch thủ lô 26: {str(e)}")
            return {'two_digits_loto': []}