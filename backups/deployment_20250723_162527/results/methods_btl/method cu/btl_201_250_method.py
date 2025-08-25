from typing import Dict, List, Any
from .base import BasePredictionMethod, BaseMakeResult
import logging
from .utils import get_ball_number
logger = logging.getLogger(__name__)

class Btl_201LotoMethod(BasePredictionMethod):
    """
    Phương pháp Bạch thủ lô 201
    Dự đoán từ số thứ 3 giải 3.4, số thứ 3 giải 4.1
    """
    def get_code(self) -> str:
        return "btl_201"
    
    def get_name(self) -> str:
        return "Bạch thủ lô 201"
    
    def get_description(self) -> str:
        return "Dự đoán các cặp số 2 chữ số từ số thứ 3 giải 3.4 và số thứ 3 giải 4.1"
    
    def calculate(self, data: Dict[str, Any]) -> Dict[str, List[str]]:
        giai_3_4 = data.get('giai_3_4', '')
        giai_4_1 = data.get('giai_4_1', '')
        
        if not all([giai_3_4, giai_4_1]):
            logger.warning(f"[{self.get_code()}] Thiếu dữ liệu đầu vào: giai_3_4={giai_3_4}, giai_4_1={giai_4_1}")
            return {'two_digits_loto': []}
        
        try:
            # Số thứ nhất: Số thứ 3 giải 3.4
            # Ví dụ: 11421 -> 4
            if len(giai_3_4) >= 3:
                first_digit = giai_3_4[2]
            else:
                logger.warning(f"[{self.get_code()}] Giải 3.4 không đủ dài: {giai_3_4}")
                return {'two_digits_loto': []}
                
            # Số thứ hai: Số thứ 3 giải 4.1
            # Ví dụ: 1315 -> 1
            if len(giai_4_1) >= 3:
                second_digit = giai_4_1[2]
            else:
                logger.warning(f"[{self.get_code()}] Giải 4.1 không đủ dài: {giai_4_1}")
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
            logger.error(f"[{self.get_code()}] Lỗi tính bạch thủ lô 201: {str(e)}")
            return {'two_digits_loto': []}


class Btl_202LotoMethod(BasePredictionMethod):
    """
    Phương pháp Bạch thủ lô 202
    Dự đoán từ số thứ 2 giải 3.6, số thứ 4 giải 5.4
    """
    def get_code(self) -> str:
        return "btl_202"
    
    def get_name(self) -> str:
        return "Bạch thủ lô 202"
    
    def get_description(self) -> str:
        return "Dự đoán các cặp số 2 chữ số từ số thứ 2 giải 3.6 và số thứ 4 giải 5.4"
    
    def calculate(self, data: Dict[str, Any]) -> Dict[str, List[str]]:
        giai_3_6 = data.get('giai_3_6', '')
        giai_5_4 = data.get('giai_5_4', '')
        
        if not all([giai_3_6, giai_5_4]):
            logger.warning(f"[{self.get_code()}] Thiếu dữ liệu đầu vào: giai_3_6={giai_3_6}, giai_5_4={giai_5_4}")
            return {'two_digits_loto': []}
        
        try:
            # Số thứ nhất: Số thứ 2 giải 3.6
            # Ví dụ: 11421 -> 1
            if len(giai_3_6) >= 2:
                first_digit = giai_3_6[1]
            else:
                logger.warning(f"[{self.get_code()}] Giải 3.6 không đủ dài: {giai_3_6}")
                return {'two_digits_loto': []}
                
            # Số thứ hai: Số thứ 4 giải 5.4
            # Ví dụ: 1315 -> 5
            if len(giai_5_4) >= 4:
                second_digit = giai_5_4[3]
            else:
                logger.warning(f"[{self.get_code()}] Giải 5.4 không đủ dài: {giai_5_4}")
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
            logger.error(f"[{self.get_code()}] Lỗi tính bạch thủ lô 202: {str(e)}")
            return {'two_digits_loto': []}
        

class Btl_203LotoMethod(BasePredictionMethod):
    """
    Phương pháp Bạch thủ lô 203
    Dự đoán từ số thứ 3 giải 2.1, số thứ 2 giải 5.3
    """
    def get_code(self) -> str:
        return "btl_203"
    
    def get_name(self) -> str:
        return "Bạch thủ lô 203"
    
    def get_description(self) -> str:
        return "Dự đoán các cặp số 2 chữ số từ số thứ 3 giải 2.1 và số thứ 2 giải 5.3"
    
    def calculate(self, data: Dict[str, Any]) -> Dict[str, List[str]]:
        giai_2_1 = data.get('giai_2_1', '')
        giai_5_3 = data.get('giai_5_3', '')
        
        if not all([giai_2_1, giai_5_3]):
            logger.warning(f"[{self.get_code()}] Thiếu dữ liệu đầu vào: giai_2_1={giai_2_1}, giai_5_3={giai_5_3}")
            return {'two_digits_loto': []}
        
        try:
            # Số thứ nhất: Số thứ 3 giải 2.1
            # Ví dụ: 11421 -> 4
            if len(giai_2_1) >= 3:
                first_digit = giai_2_1[2]
            else:
                logger.warning(f"[{self.get_code()}] Giải 2.1 không đủ dài: {giai_2_1}")
                return {'two_digits_loto': []}
                
            # Số thứ hai: Số thứ 2 giải 5.3
            # Ví dụ: 1315 -> 3
            if len(giai_5_3) >= 2:
                second_digit = giai_5_3[1]
            else:
                logger.warning(f"[{self.get_code()}] Giải 5.3 không đủ dài: {giai_5_3}")
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
            logger.error(f"[{self.get_code()}] Lỗi tính bạch thủ lô 203: {str(e)}")
            return {'two_digits_loto': []}

class Btl_204LotoMethod(BasePredictionMethod):
    """
    Phương pháp Bạch thủ lô 204
    Dự đoán từ số thứ 2 giải 1, số thứ 3 giải 3.1
    """
    def get_code(self) -> str:
        return "btl_204"
    
    def get_name(self) -> str:
        return "Bạch thủ lô 204"
    
    def get_description(self) -> str:
        return "Dự đoán các cặp số 2 chữ số từ số thứ 2 giải 1 và số thứ 3 giải 3.1"
    
    def calculate(self, data: Dict[str, Any]) -> Dict[str, List[str]]:
        giai_1 = data.get('giai_1', '')
        giai_3_1 = data.get('giai_3_1', '')
        
        if not all([giai_1, giai_3_1]):
            logger.warning(f"[{self.get_code()}] Thiếu dữ liệu đầu vào: giai_1={giai_1}, giai_3_1={giai_3_1}")
            return {'two_digits_loto': []}
        
        try:
            # Số thứ nhất: Số thứ 2 giải 1
            # Ví dụ: 11421 -> 1
            if len(giai_1) >= 2:
                first_digit = giai_1[1]
            else:
                logger.warning(f"[{self.get_code()}] Giải 1 không đủ dài: {giai_1}")
                return {'two_digits_loto': []}
                
            # Số thứ hai: Số thứ 3 giải 3.1
            # Ví dụ: 1315 -> 1
            if len(giai_3_1) >= 3:
                second_digit = giai_3_1[2]
            else:
                logger.warning(f"[{self.get_code()}] Giải 3.1 không đủ dài: {giai_3_1}")
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
            logger.error(f"[{self.get_code()}] Lỗi tính bạch thủ lô 204: {str(e)}")
            return {'two_digits_loto': []}
        


class Btl_205LotoMethod(BasePredictionMethod):
    """
    Phương pháp Bạch thủ lô 205
    Dự đoán từ số thứ 5 giải 3.2, số thứ 3 giải 4.4
    """
    def get_code(self) -> str:
        return "btl_205"
    
    def get_name(self) -> str:
        return "Bạch thủ lô 205"
    
    def get_description(self) -> str:
        return "Dự đoán các cặp số 2 chữ số từ số thứ 5 giải 3.2 và số thứ 3 giải 4.4"
    
    def calculate(self, data: Dict[str, Any]) -> Dict[str, List[str]]:
        giai_3_2 = data.get('giai_3_2', '')
        giai_4_4 = data.get('giai_4_4', '')
        
        if not all([giai_3_2, giai_4_4]):
            logger.warning(f"[{self.get_code()}] Thiếu dữ liệu đầu vào: giai_3_2={giai_3_2}, giai_4_4={giai_4_4}")
            return {'two_digits_loto': []}
        
        try:
            # Số thứ nhất: Số thứ 5 giải 3.2
            # Ví dụ: 11421 -> 1
            if len(giai_3_2) >= 5:
                first_digit = giai_3_2[4]
            else:
                logger.warning(f"[{self.get_code()}] Giải 3.2 không đủ dài: {giai_3_2}")
                return {'two_digits_loto': []}
                
            # Số thứ hai: Số thứ 3 giải 4.4
            # Ví dụ: 1315 -> 1
            if len(giai_4_4) >= 3:
                second_digit = giai_4_4[2]
            else:
                logger.warning(f"[{self.get_code()}] Giải 4.4 không đủ dài: {giai_4_4}")
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
            logger.error(f"[{self.get_code()}] Lỗi tính bạch thủ lô 205: {str(e)}")
            return {'two_digits_loto': []}


class Btl_206LotoMethod(BasePredictionMethod):
    """
    Phương pháp Bạch thủ lô 206
    Dự đoán từ số thứ 2 giải 5.2, số thứ 3 giải 6.2
    """
    def get_code(self) -> str:
        return "btl_206"
    
    def get_name(self) -> str:
        return "Bạch thủ lô 206"
    
    def get_description(self) -> str:
        return "Dự đoán các cặp số 2 chữ số từ số thứ 2 giải 5.2 và số thứ 3 giải 6.2"
    
    def calculate(self, data: Dict[str, Any]) -> Dict[str, List[str]]:
        giai_5_2 = data.get('giai_5_2', '')
        giai_6_2 = data.get('giai_6_2', '')
        
        if not all([giai_5_2, giai_6_2]):
            logger.warning(f"[{self.get_code()}] Thiếu dữ liệu đầu vào: giai_5_2={giai_5_2}, giai_6_2={giai_6_2}")
            return {'two_digits_loto': []}
        
        try:
            # Số thứ nhất: Số thứ 2 giải 5.2
            # Ví dụ: 1142 -> 1
            if len(giai_5_2) >= 2:
                first_digit = giai_5_2[1]
            else:
                logger.warning(f"[{self.get_code()}] Giải 5.2 không đủ dài: {giai_5_2}")
                return {'two_digits_loto': []}
                
            # Số thứ hai: Số thứ 3 giải 6.2
            # Ví dụ: 1315 -> 1
            if len(giai_6_2) >= 3:
                second_digit = giai_6_2[2]
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
            logger.error(f"[{self.get_code()}] Lỗi tính bạch thủ lô 206: {str(e)}")
            return {'two_digits_loto': []}
        


class Btl_207LotoMethod(BasePredictionMethod):
    """
    Phương pháp Bạch thủ lô 207
    Dự đoán từ số thứ 3 giải 3.1, số thứ 2 giải 7.1
    """
    def get_code(self) -> str:
        return "btl_207"
    
    def get_name(self) -> str:
        return "Bạch thủ lô 207"
    
    def get_description(self) -> str:
        return "Dự đoán các cặp số 2 chữ số từ số thứ 3 giải 3.1 và số thứ 2 giải 7.1"
    
    def calculate(self, data: Dict[str, Any]) -> Dict[str, List[str]]:
        giai_3_1 = data.get('giai_3_1', '')
        giai_7_1 = data.get('giai_7_1', '')
        
        if not all([giai_3_1, giai_7_1]):
            logger.warning(f"[{self.get_code()}] Thiếu dữ liệu đầu vào: giai_3_1={giai_3_1}, giai_7_1={giai_7_1}")
            return {'two_digits_loto': []}
        
        try:
            # Số thứ nhất: Số thứ 3 giải 3.1
            # Ví dụ: 1142 -> 4
            if len(giai_3_1) >= 3:
                first_digit = giai_3_1[2]
            else:
                logger.warning(f"[{self.get_code()}] Giải 3.1 không đủ dài: {giai_3_1}")
                return {'two_digits_loto': []}
                
            # Số thứ hai: Số thứ 2 giải 7.1
            # Ví dụ: 13 -> 3
            if len(giai_7_1) >= 2:
                second_digit = giai_7_1[1]
            else:
                logger.warning(f"[{self.get_code()}] Giải 7.1 không đủ dài: {giai_7_1}")
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
            logger.error(f"[{self.get_code()}] Lỗi tính bạch thủ lô 207: {str(e)}")
            return {'two_digits_loto': []}


class Btl_208LotoMethod(BasePredictionMethod):
    """
    Phương pháp Bạch thủ lô 208
    Dự đoán từ số thứ 5 giải 2.2, số thứ 4 giải 3.2
    """
    def get_code(self) -> str:
        return "btl_208"
    
    def get_name(self) -> str:
        return "Bạch thủ lô 208"
    
    def get_description(self) -> str:
        return "Dự đoán các cặp số 2 chữ số từ số thứ 5 giải 2.2 và số thứ 4 giải 3.2"
    
    def calculate(self, data: Dict[str, Any]) -> Dict[str, List[str]]:
        giai_2_2 = data.get('giai_2_2', '')
        giai_3_2 = data.get('giai_3_2', '')
        
        if not all([giai_2_2, giai_3_2]):
            logger.warning(f"[{self.get_code()}] Thiếu dữ liệu đầu vào: giai_2_2={giai_2_2}, giai_3_2={giai_3_2}")
            return {'two_digits_loto': []}
        
        try:
            # Số thứ nhất: Số thứ 5 giải 2.2
            if len(giai_2_2) >= 5:
                first_digit = giai_2_2[4]
            else:
                logger.warning(f"[{self.get_code()}] Giải 2.2 không đủ dài: {giai_2_2}")
                return {'two_digits_loto': []}
                
            # Số thứ hai: Số thứ 4 giải 3.2
            if len(giai_3_2) >= 4:
                second_digit = giai_3_2[3]
            else:
                logger.warning(f"[{self.get_code()}] Giải 3.2 không đủ dài: {giai_3_2}")
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
            logger.error(f"[{self.get_code()}] Lỗi tính bạch thủ lô 208: {str(e)}")
            return {'two_digits_loto': []}
        

class Btl_209LotoMethod(BasePredictionMethod):
    """
    Phương pháp Bạch thủ lô 209
    Dự đoán từ số thứ 3 giải 4.1, số thứ 4 giải 5.6
    """
    def get_code(self) -> str:
        return "btl_209"
    
    def get_name(self) -> str:
        return "Bạch thủ lô 209"
    
    def get_description(self) -> str:
        return "Dự đoán các cặp số 2 chữ số từ số thứ 3 giải 4.1 và số thứ 4 giải 5.6"
    
    def calculate(self, data: Dict[str, Any]) -> Dict[str, List[str]]:
        giai_4_1 = data.get('giai_4_1', '')
        giai_5_6 = data.get('giai_5_6', '')
        
        if not all([giai_4_1, giai_5_6]):
            logger.warning(f"[{self.get_code()}] Thiếu dữ liệu đầu vào: giai_4_1={giai_4_1}, giai_5_6={giai_5_6}")
            return {'two_digits_loto': []}
        
        try:
            # Số thứ nhất: Số thứ 3 giải 4.1
            if len(giai_4_1) >= 3:
                first_digit = giai_4_1[2]
            else:
                logger.warning(f"[{self.get_code()}] Giải 4.1 không đủ dài: {giai_4_1}")
                return {'two_digits_loto': []}
                
            # Số thứ hai: Số thứ 4 giải 5.6
            if len(giai_5_6) >= 4:
                second_digit = giai_5_6[3]
            else:
                logger.warning(f"[{self.get_code()}] Giải 5.6 không đủ dài: {giai_5_6}")
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
            logger.error(f"[{self.get_code()}] Lỗi tính bạch thủ lô 209: {str(e)}")
            return {'two_digits_loto': []}
        

class Btl_210LotoMethod(BasePredictionMethod):
    """
    Phương pháp Bạch thủ lô 210
    Dự đoán từ số thứ 3 giải 5.4, số thứ 2 giải 5.5
    """
    def get_code(self) -> str:
        return "btl_210"
    
    def get_name(self) -> str:
        return "Bạch thủ lô 210"
    
    def get_description(self) -> str:
        return "Dự đoán các cặp số 2 chữ số từ số thứ 3 giải 5.4 và số thứ 2 giải 5.5"
    
    def calculate(self, data: Dict[str, Any]) -> Dict[str, List[str]]:
        giai_5_4 = data.get('giai_5_4', '')
        giai_5_5 = data.get('giai_5_5', '')
        
        if not all([giai_5_4, giai_5_5]):
            logger.warning(f"[{self.get_code()}] Thiếu dữ liệu đầu vào: giai_5_4={giai_5_4}, giai_5_5={giai_5_5}")
            return {'two_digits_loto': []}
        
        try:
            # Số thứ nhất: Số thứ 3 giải 5.4
            if len(giai_5_4) >= 3:
                first_digit = giai_5_4[2]
            else:
                logger.warning(f"[{self.get_code()}] Giải 5.4 không đủ dài: {giai_5_4}")
                return {'two_digits_loto': []}
                
            # Số thứ hai: Số thứ 2 giải 5.5
            if len(giai_5_5) >= 2:
                second_digit = giai_5_5[1]
            else:
                logger.warning(f"[{self.get_code()}] Giải 5.5 không đủ dài: {giai_5_5}")
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
            logger.error(f"[{self.get_code()}] Lỗi tính bạch thủ lô 210: {str(e)}")
            return {'two_digits_loto': []}
  

class Btl_211LotoMethod(BasePredictionMethod):
    """
    Phương pháp Bạch thủ lô 211
    Dự đoán từ số thứ 2 giải 3.2, số thứ 4 giải 5.2
    """
    def get_code(self) -> str:
        return "btl_211"
    
    def get_name(self) -> str:
        return "Bạch thủ lô 211"
    
    def get_description(self) -> str:
        return "Dự đoán các cặp số 2 chữ số từ số thứ 2 giải 3.2 và số thứ 4 giải 5.2"
    
    def calculate(self, data: Dict[str, Any]) -> Dict[str, List[str]]:
        giai_3_2 = data.get('giai_3_2', '')
        giai_5_2 = data.get('giai_5_2', '')
        
        if not all([giai_3_2, giai_5_2]):
            logger.warning(f"[{self.get_code()}] Thiếu dữ liệu đầu vào: giai_3_2={giai_3_2}, giai_5_2={giai_5_2}")
            return {'two_digits_loto': []}
        
        try:
            # Số thứ nhất: Số thứ 2 giải 3.2
            if len(giai_3_2) >= 2:
                first_digit = giai_3_2[1]
            else:
                logger.warning(f"[{self.get_code()}] Giải 3.2 không đủ dài: {giai_3_2}")
                return {'two_digits_loto': []}
                
            # Số thứ hai: Số thứ 4 giải 5.2
            if len(giai_5_2) >= 4:
                second_digit = giai_5_2[3]
            else:
                logger.warning(f"[{self.get_code()}] Giải 5.2 không đủ dài: {giai_5_2}")
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
            logger.error(f"[{self.get_code()}] Lỗi tính bạch thủ lô 211: {str(e)}")
            return {'two_digits_loto': []}
        


class Btl_212LotoMethod(BasePredictionMethod):
    """
    Phương pháp Bạch thủ lô 212
    Dự đoán từ số thứ 4 giải 3.2, số thứ 2 giải 3.4
    """
    def get_code(self) -> str:
        return "btl_212"
    
    def get_name(self) -> str:
        return "Bạch thủ lô 212"
    
    def get_description(self) -> str:
        return "Dự đoán các cặp số 2 chữ số từ số thứ 4 giải 3.2 và số thứ 2 giải 3.4"
    
    def calculate(self, data: Dict[str, Any]) -> Dict[str, List[str]]:
        giai_3_2 = data.get('giai_3_2', '')
        giai_3_4 = data.get('giai_3_4', '')
        
        if not all([giai_3_2, giai_3_4]):
            logger.warning(f"[{self.get_code()}] Thiếu dữ liệu đầu vào: giai_3_2={giai_3_2}, giai_3_4={giai_3_4}")
            return {'two_digits_loto': []}
        
        try:
            # Số thứ nhất: Số thứ 4 giải 3.2
            if len(giai_3_2) >= 4:
                first_digit = giai_3_2[3]
            else:
                logger.warning(f"[{self.get_code()}] Giải 3.2 không đủ dài: {giai_3_2}")
                return {'two_digits_loto': []}
                
            # Số thứ hai: Số thứ 2 giải 3.4
            if len(giai_3_4) >= 2:
                second_digit = giai_3_4[1]
            else:
                logger.warning(f"[{self.get_code()}] Giải 3.4 không đủ dài: {giai_3_4}")
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
            logger.error(f"[{self.get_code()}] Lỗi tính bạch thủ lô 212: {str(e)}")
            return {'two_digits_loto': []}
        


class Btl_213LotoMethod(BasePredictionMethod):
    """
    Phương pháp Bạch thủ lô 213
    Dự đoán từ số thứ 4 giải 5.2, số thứ 2 giải 5.3
    """
    def get_code(self) -> str:
        return "btl_213"
    
    def get_name(self) -> str:
        return "Bạch thủ lô 213"
    
    def get_description(self) -> str:
        return "Dự đoán các cặp số 2 chữ số từ số thứ 4 giải 5.2 và số thứ 2 giải 5.3"
    
    def calculate(self, data: Dict[str, Any]) -> Dict[str, List[str]]:
        giai_5_2 = data.get('giai_5_2', '')
        giai_5_3 = data.get('giai_5_3', '')
        
        if not all([giai_5_2, giai_5_3]):
            logger.warning(f"[{self.get_code()}] Thiếu dữ liệu đầu vào: giai_5_2={giai_5_2}, giai_5_3={giai_5_3}")
            return {'two_digits_loto': []}
        
        try:
            # Số thứ nhất: Số thứ 4 giải 5.2
            if len(giai_5_2) >= 4:
                first_digit = giai_5_2[3]
            else:
                logger.warning(f"[{self.get_code()}] Giải 5.2 không đủ dài: {giai_5_2}")
                return {'two_digits_loto': []}
                
            # Số thứ hai: Số thứ 2 giải 5.3
            if len(giai_5_3) >= 2:
                second_digit = giai_5_3[1]
            else:
                logger.warning(f"[{self.get_code()}] Giải 5.3 không đủ dài: {giai_5_3}")
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
            logger.error(f"[{self.get_code()}] Lỗi tính bạch thủ lô 213: {str(e)}")
            return {'two_digits_loto': []}
        

class Btl_214LotoMethod(BasePredictionMethod):
    """
    Phương pháp Bạch thủ lô 214
    Dự đoán từ số thứ 2 giải 4.2, số thứ 1 giải 6.3
    """
    def get_code(self) -> str:
        return "btl_214"
    
    def get_name(self) -> str:
        return "Bạch thủ lô 214"
    
    def get_description(self) -> str:
        return "Dự đoán các cặp số 2 chữ số từ số thứ 2 giải 4.2 và số thứ 1 giải 6.3"
    
    def calculate(self, data: Dict[str, Any]) -> Dict[str, List[str]]:
        giai_4_2 = data.get('giai_4_2', '')
        giai_6_3 = data.get('giai_6_3', '')
        
        if not all([giai_4_2, giai_6_3]):
            logger.warning(f"[{self.get_code()}] Thiếu dữ liệu đầu vào: giai_4_2={giai_4_2}, giai_6_3={giai_6_3}")
            return {'two_digits_loto': []}
        
        try:
            # Số thứ nhất: Số thứ 2 giải 4.2
            if len(giai_4_2) >= 2:
                first_digit = giai_4_2[1]
            else:
                logger.warning(f"[{self.get_code()}] Giải 4.2 không đủ dài: {giai_4_2}")
                return {'two_digits_loto': []}
                
            # Số thứ hai: Số thứ 1 giải 6.3
            if len(giai_6_3) >= 1:
                second_digit = giai_6_3[0]
            else:
                logger.warning(f"[{self.get_code()}] Giải 6.3 không đủ dài: {giai_6_3}")
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
            logger.error(f"[{self.get_code()}] Lỗi tính bạch thủ lô 214: {str(e)}")
            return {'two_digits_loto': []}
        
class Btl_215LotoMethod(BasePredictionMethod):
    """
    Phương pháp Bạch thủ lô 215
    Dự đoán từ số thứ 4 giải 5.1, số thứ 1 giải 7.4
    """
    def get_code(self) -> str:
        return "btl_215"
    
    def get_name(self) -> str:
        return "Bạch thủ lô 215"
    
    def get_description(self) -> str:
        return "Dự đoán các cặp số 2 chữ số từ số thứ 4 giải 5.1 và số thứ 1 giải 7.4"
    
    def calculate(self, data: Dict[str, Any]) -> Dict[str, List[str]]:
        giai_5_1 = data.get('giai_5_1', '')
        giai_7_4 = data.get('giai_7_4', '')
        
        if not all([giai_5_1, giai_7_4]):
            logger.warning(f"[{self.get_code()}] Thiếu dữ liệu đầu vào: giai_5_1={giai_5_1}, giai_7_4={giai_7_4}")
            return {'two_digits_loto': []}
        
        try:
            # Số thứ nhất: Số thứ 4 giải 5.1
            if len(giai_5_1) >= 4:
                first_digit = giai_5_1[3]
            else:
                logger.warning(f"[{self.get_code()}] Giải 5.1 không đủ dài: {giai_5_1}")
                return {'two_digits_loto': []}
                
            # Số thứ hai: Số thứ 1 giải 7.4
            if len(giai_7_4) >= 1:
                second_digit = giai_7_4[0]
            else:
                logger.warning(f"[{self.get_code()}] Giải 7.4 không đủ dài: {giai_7_4}")
                return {'two_digits_loto': []}
            
            # Tạo các cặp số 2 chữ số
            two_digits = set()
            # Cặp số thẳng
            two_digits.add(f"{first_digit}{second_digit}")
            # Cặp số đảo
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
            logger.error(f"[{self.get_code()}] Lỗi tính bạch thủ lô 215: {str(e)}")
            return {'two_digits_loto': []}
        

class Btl_216LotoMethod(BasePredictionMethod):
    """
    Phương pháp Bạch thủ lô 216
    Dự đoán từ số thứ 2 giải 3.2, số thứ 2 giải 4.3
    """
    def get_code(self) -> str:
        return "btl_216"
    
    def get_name(self) -> str:
        return "Bạch thủ lô 216"
    
    def get_description(self) -> str:
        return "Dự đoán các cặp số 2 chữ số từ số thứ 2 giải 3.2 và số thứ 2 giải 4.3"
    
    def calculate(self, data: Dict[str, Any]) -> Dict[str, List[str]]:
        giai_3_2 = data.get('giai_3_2', '')
        giai_4_3 = data.get('giai_4_3', '')
        
        if not all([giai_3_2, giai_4_3]):
            logger.warning(f"[{self.get_code()}] Thiếu dữ liệu đầu vào: giai_3_2={giai_3_2}, giai_4_3={giai_4_3}")
            return {'two_digits_loto': []}
        
        try:
            # Số thứ nhất: Số thứ 2 giải 3.2
            if len(giai_3_2) >= 2:
                first_digit = giai_3_2[1]
            else:
                logger.warning(f"[{self.get_code()}] Giải 3.2 không đủ dài: {giai_3_2}")
                return {'two_digits_loto': []}
                
            # Số thứ hai: Số thứ 2 giải 4.3
            if len(giai_4_3) >= 2:
                second_digit = giai_4_3[1]
            else:
                logger.warning(f"[{self.get_code()}] Giải 4.3 không đủ dài: {giai_4_3}")
                return {'two_digits_loto': []}
            
            # Tạo các cặp số 2 chữ số
            two_digits = set()
            # Cặp số thẳng
            two_digits.add(f"{first_digit}{second_digit}")
            # Cặp số đảo
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
            logger.error(f"[{self.get_code()}] Lỗi tính bạch thủ lô:216: {str(e)}")
            return {'two_digits_loto': []}
        

class Btl_217LotoMethod(BasePredictionMethod):
    """
    Phương pháp Bạch thủ lô 217
    Dự đoán từ số thứ 3 giải 4.1, số thứ 4 giải 4.1
    """
    def get_code(self) -> str:
        return "btl_217"
    
    def get_name(self) -> str:
        return "Bạch thủ lô 217"
    
    def get_description(self) -> str:
        return "Dự đoán các cặp số 2 chữ số từ số thứ 3 giải 4.1 và số thứ 4 giải 4.1"
    
    def calculate(self, data: Dict[str, Any]) -> Dict[str, List[str]]:
        giai_4_1 = data.get('giai_4_1', '')
        
        if not giai_4_1:
            logger.warning(f"[{self.get_code()}] Thiếu dữ liệu đầu vào: giai_4_1={giai_4_1}")
            return {'two_digits_loto': []}
        
        try:
            # Số thứ nhất: Số thứ 3 giải 4.1
            if len(giai_4_1) >= 3:
                first_digit = giai_4_1[2]
            else:
                logger.warning(f"[{self.get_code()}] Giải 4.1 không đủ dài: {giai_4_1}")
                return {'two_digits_loto': []}
                
            # Số thứ hai: Số thứ 4 giải 4.1
            if len(giai_4_1) >= 4:
                second_digit = giai_4_1[3]
            else:
                logger.warning(f"[{self.get_code()}] Giải 4.1 không đủ dài: {giai_4_1}")
                return {'two_digits_loto': []}
            
            # Tạo các cặp số 2 chữ số
            two_digits = set()
            # Cặp số thẳng
            two_digits.add(f"{first_digit}{second_digit}")
            # Cặp số đảo
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
            logger.error(f"[{self.get_code()}] Lỗi tính bạch thủ lô 217: {str(e)}")
            return {'two_digits_loto': []}
        
class Btl_218LotoMethod(BasePredictionMethod):
    """
    Phương pháp Bạch thủ lô 218
    Dự đoán từ số thứ 2 giải 3.4, số thứ 3 giải 5.4
    """
    def get_code(self) -> str:
        return "btl_218"
    
    def get_name(self) -> str:
        return "Bạch thủ lô 218"
    
    def get_description(self) -> str:
        return "Dự đoán các cặp số 2 chữ số từ số thứ 2 giải 3.4 và số thứ 3 giải 5.4"
    
    def calculate(self, data: Dict[str, Any]) -> Dict[str, List[str]]:
        giai_3_4 = data.get('giai_3_4', '')
        giai_5_4 = data.get('giai_5_4', '')
        
        if not giai_3_4 or not giai_5_4:
            logger.warning(f"[{self.get_code()}] Thiếu dữ liệu đầu vào: giai_3_4={giai_3_4}, giai_5_4={giai_5_4}")
            return {'two_digits_loto': []}
        
        try:
            # Số thứ nhất: Số thứ 2 giải 3.4
            if len(giai_3_4) >= 2:
                first_digit = giai_3_4[1]
            else:
                logger.warning(f"[{self.get_code()}] Giải 3.4 không đủ dài: {giai_3_4}")
                return {'two_digits_loto': []}
                
            # Số thứ hai: Số thứ 3 giải 5.4
            if len(giai_5_4) >= 3:
                second_digit = giai_5_4[2]
            else:
                logger.warning(f"[{self.get_code()}] Giải 5.4 không đủ dài: {giai_5_4}")
                return {'two_digits_loto': []}
            
            # Tạo các cặp số 2 chữ số
            two_digits = set()
            # Cặp số thẳng
            two_digits.add(f"{first_digit}{second_digit}")
            # Cặp số đảo
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
            logger.error(f"[{self.get_code()}] Lỗi tính bạch thủ lô 218: {str(e)}")
            return {'two_digits_loto': []}
        
class Btl_219LotoMethod(BasePredictionMethod):
    """
    Phương pháp Bạch thủ lô 219
    Dự đoán từ số thứ 3 giải 3.4, số thứ 3 giải 5.4
    """
    def get_code(self) -> str:
        return "btl_219"
    
    def get_name(self) -> str:
        return "Bạch thủ lô 219"
    
    def get_description(self) -> str:
        return "Dự đoán các cặp số 2 chữ số từ số thứ 3 giải 3.4 và số thứ 3 giải 5.4"
    
    def calculate(self, data: Dict[str, Any]) -> Dict[str, List[str]]:
        giai_3_4 = data.get('giai_3_4', '')
        giai_5_4 = data.get('giai_5_4', '')
        
        if not giai_3_4 or not giai_5_4:
            logger.warning(f"[{self.get_code()}] Thiếu dữ liệu đầu vào: giai_3_4={giai_3_4}, giai_5_4={giai_5_4}")
            return {'two_digits_loto': []}
        
        try:
            # Số thứ nhất: Số thứ 3 giải 3.4
            if len(giai_3_4) >= 3:
                first_digit = giai_3_4[2]
            else:
                logger.warning(f"[{self.get_code()}] Giải 3.4 không đủ dài: {giai_3_4}")
                return {'two_digits_loto': []}
                
            # Số thứ hai: Số thứ 3 giải 5.4
            if len(giai_5_4) >= 3:
                second_digit = giai_5_4[2]
            else:
                logger.warning(f"[{self.get_code()}] Giải 5.4 không đủ dài: {giai_5_4}")
                return {'two_digits_loto': []}
            
            # Tạo các cặp số 2 chữ số
            two_digits = set()
            # Cặp số thẳng
            two_digits.add(f"{first_digit}{second_digit}")
            # Cặp số đảo
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
            logger.error(f"[{self.get_code()}] Lỗi tính bạch thủ lô 219: {str(e)}")
            return {'two_digits_loto': []}
        
class Btl_220LotoMethod(BasePredictionMethod):
    """
    Phương pháp Bạch thủ lô 220
    Dự đoán từ số thứ 1 giải 3.6, số thứ 3 giải 5.4
    """
    def get_code(self) -> str:
        return "btl_220"
    
    def get_name(self) -> str:
        return "Bạch thủ lô 220"
    
    def get_description(self) -> str:
        return "Dự đoán các cặp số 2 chữ số từ số thứ 1 giải 3.6 và số thứ 3 giải 5.4"
    
    def calculate(self, data: Dict[str, Any]) -> Dict[str, List[str]]:
        giai_3_6 = data.get('giai_3_6', '')
        giai_5_4 = data.get('giai_5_4', '')
        
        if not giai_3_6 or not giai_5_4:
            logger.warning(f"[{self.get_code()}] Thiếu dữ liệu đầu vào: giai_3_6={giai_3_6}, giai_5_4={giai_5_4}")
            return {'two_digits_loto': []}
        
        try:
            # Số thứ nhất: Số thứ 1 giải 3.6
            if len(giai_3_6) >= 1:
                first_digit = giai_3_6[0]
            else:
                logger.warning(f"[{self.get_code()}] Giải 3.6 không đủ dài: {giai_3_6}")
                return {'two_digits_loto': []}
                
            # Số thứ hai: Số thứ 3 giải 5.4
            if len(giai_5_4) >= 3:
                second_digit = giai_5_4[2]
            else:
                logger.warning(f"[{self.get_code()}] Giải 5.4 không đủ dài: {giai_5_4}")
                return {'two_digits_loto': []}
            
            # Tạo các cặp số 2 chữ số
            two_digits = set()
            # Cặp số thẳng
            two_digits.add(f"{first_digit}{second_digit}")
            # Cặp số đảo
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
            logger.error(f"[{self.get_code()}] Lỗi tính bạch thủ lô 220: {str(e)}")
            return {'two_digits_loto': []}
class Btl_221LotoMethod(BasePredictionMethod):
    """
    Phương pháp Bạch thủ lô 221
    Dự đoán từ số thứ 4 giải 5.1, số thứ 2 giải 5.4
    """
    def get_code(self) -> str:
        return "btl_221"
    
    def get_name(self) -> str:
        return "Bạch thủ lô 221"
    
    def get_description(self) -> str:
        return "Dự đoán các cặp số 2 chữ số từ số thứ 4 giải 5.1 và số thứ 2 giải 5.4"
    
    def calculate(self, data: Dict[str, Any]) -> Dict[str, List[str]]:
        giai_5_1 = data.get('giai_5_1', '')
        giai_5_4 = data.get('giai_5_4', '')
        
        if not giai_5_1 or not giai_5_4:
            logger.warning(f"[{self.get_code()}] Thiếu dữ liệu đầu vào: giai_5_1={giai_5_1}, giai_5_4={giai_5_4}")
            return {'two_digits_loto': []}
        
        try:
            # Số thứ nhất: Số thứ 4 giải 5.1
            if len(giai_5_1) >= 4:
                first_digit = giai_5_1[3]
            else:
                logger.warning(f"[{self.get_code()}] Giải 5.1 không đủ dài: {giai_5_1}")
                return {'two_digits_loto': []}
                
            # Số thứ hai: Số thứ 2 giải 5.4
            if len(giai_5_4) >= 2:
                second_digit = giai_5_4[1]
            else:
                logger.warning(f"[{self.get_code()}] Giải 5.4 không đủ dài: {giai_5_4}")
                return {'two_digits_loto': []}
            
            # Tạo các cặp số 2 chữ số
            two_digits = set()
            # Cặp số thẳng
            two_digits.add(f"{first_digit}{second_digit}")
            # Cặp số đảo
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
            logger.error(f"[{self.get_code()}] Lỗi tính bạch thủ lô 221: {str(e)}")
            return {'two_digits_loto': []}

class Btl_222LotoMethod(BasePredictionMethod):
    """
    Phương pháp Bạch thủ lô 222
    Dự đoán từ số thứ 1 giải 3.2, số thứ 1 giải 4.4
    """
    def get_code(self) -> str:
        return "btl_222"
    
    def get_name(self) -> str:
        return "Bạch thủ lô 222"
    
    def get_description(self) -> str:
        return "Dự đoán các cặp số 2 chữ số từ số thứ 1 giải 3.2 và số thứ 1 giải 4.4"
    
    def calculate(self, data: Dict[str, Any]) -> Dict[str, List[str]]:
        giai_3_2 = data.get('giai_3_2', '')
        giai_4_4 = data.get('giai_4_4', '')
        
        if not giai_3_2 or not giai_4_4:
            logger.warning(f"[{self.get_code()}] Thiếu dữ liệu đầu vào: giai_3_2={giai_3_2}, giai_4_4={giai_4_4}")
            return {'two_digits_loto': []}
        
        try:
            # Số thứ nhất: Số thứ 1 giải 3.2
            if len(giai_3_2) >= 1:
                first_digit = giai_3_2[0]
            else:
                logger.warning(f"[{self.get_code()}] Giải 3.2 không đủ dài: {giai_3_2}")
                return {'two_digits_loto': []}
                
            # Số thứ hai: Số thứ 1 giải 4.4
            if len(giai_4_4) >= 1:
                second_digit = giai_4_4[0]
            else:
                logger.warning(f"[{self.get_code()}] Giải 4.4 không đủ dài: {giai_4_4}")
                return {'two_digits_loto': []}
            
            # Tạo các cặp số 2 chữ số
            two_digits = set()
            # Cặp số thẳng
            two_digits.add(f"{first_digit}{second_digit}")
            # Cặp số đảo
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
            logger.error(f"[{self.get_code()}] Lỗi tính bạch thủ lô 222: {str(e)}")
            return {'two_digits_loto': []}
        
class Btl_223LotoMethod(BasePredictionMethod):
    """
    Phương pháp Bạch thủ lô 223
    Dự đoán từ số thứ 5 giải 3.4, số thứ 1 giải 5.4
    """
    def get_code(self) -> str:
        return "btl_223"
    
    def get_name(self) -> str:
        return "Bạch thủ lô 223"
    
    def get_description(self) -> str:
        return "Dự đoán các cặp số 2 chữ số từ số thứ 5 giải 3.4 và số thứ 1 giải 5.4"
    
    def calculate(self, data: Dict[str, Any]) -> Dict[str, List[str]]:
        giai_3_4 = data.get('giai_3_4', '')
        giai_5_4 = data.get('giai_5_4', '')
        
        if not giai_3_4 or not giai_5_4:
            logger.warning(f"[{self.get_code()}] Thiếu dữ liệu đầu vào: giai_3_4={giai_3_4}, giai_5_4={giai_5_4}")
            return {'two_digits_loto': []}
        
        try:
            # Số thứ nhất: Số thứ 5 giải 3.4
            if len(giai_3_4) >= 5:
                first_digit = giai_3_4[4]
            else:
                logger.warning(f"[{self.get_code()}] Giải 3.4 không đủ dài: {giai_3_4}")
                return {'two_digits_loto': []}
                
            # Số thứ hai: Số thứ 1 giải 5.4
            if len(giai_5_4) >= 1:
                second_digit = giai_5_4[0]
            else:
                logger.warning(f"[{self.get_code()}] Giải 5.4 không đủ dài: {giai_5_4}")
                return {'two_digits_loto': []}
            
            # Tạo các cặp số 2 chữ số
            two_digits = set()
            # Cặp số thẳng
            two_digits.add(f"{first_digit}{second_digit}")
            # Cặp số đảo
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
            logger.error(f"[{self.get_code()}] Lỗi tính bạch thủ lô 223: {str(e)}")
            return {'two_digits_loto': []}
        
class Btl_224LotoMethod(BasePredictionMethod):
    """
    Phương pháp Bạch thủ lô 224
    Dự đoán từ số thứ 5 giải 3.2, số thứ 2 giải 6.1
    """
    def get_code(self) -> str:
        return "btl_224"
    
    def get_name(self) -> str:
        return "Bạch thủ lô 224"
    
    def get_description(self) -> str:
        return "Dự đoán các cặp số 2 chữ số từ số thứ 5 giải 3.2 và số thứ 2 giải 6.1"
    
    def calculate(self, data: Dict[str, Any]) -> Dict[str, List[str]]:
        giai_3_2 = data.get('giai_3_2', '')
        giai_6_1 = data.get('giai_6_1', '')
        
        if not giai_3_2 or not giai_6_1:
            logger.warning(f"[{self.get_code()}] Thiếu dữ liệu đầu vào: giai_3_2={giai_3_2}, giai_6_1={giai_6_1}")
            return {'two_digits_loto': []}
        
        try:
            # Số thứ nhất: Số thứ 5 giải 3.2
            if len(giai_3_2) >= 5:
                first_digit = giai_3_2[4]
            else:
                logger.warning(f"[{self.get_code()}] Giải 3.2 không đủ dài: {giai_3_2}")
                return {'two_digits_loto': []}
                
            # Số thứ hai: Số thứ 2 giải 6.1
            if len(giai_6_1) >= 2:
                second_digit = giai_6_1[1]
            else:
                logger.warning(f"[{self.get_code()}] Giải 6.1 không đủ dài: {giai_6_1}")
                return {'two_digits_loto': []}
            
            # Tạo các cặp số 2 chữ số
            two_digits = set()
            # Cặp số thẳng
            two_digits.add(f"{first_digit}{second_digit}")
            # Cặp số đảo
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
            logger.error(f"[{self.get_code()}] Lỗi tính bạch thủ lô 224: {str(e)}")
            return {'two_digits_loto': []}
        
class Btl_225LotoMethod(BasePredictionMethod):
    """
    Phương pháp Bạch thủ lô 225
    Dự đoán từ số thứ 3 giải 1.1, số thứ 5 giải 3.1
    """
    def get_code(self) -> str:
        return "btl_225"
    
    def get_name(self) -> str:
        return "Bạch thủ lô 225"
    
    def get_description(self) -> str:
        return "Dự đoán các cặp số 2 chữ số từ số thứ 3 giải 1.1 và số thứ 5 giải 3.1"
    
    def calculate(self, data: Dict[str, Any]) -> Dict[str, List[str]]:
        giai_1_1 = data.get('giai_1', '')
        giai_3_1 = data.get('giai_3_1', '')
        
        if not giai_1_1 or not giai_3_1:
            logger.warning(f"[{self.get_code()}] Thiếu dữ liệu đầu vào: giai_1_1={giai_1_1}, giai_3_1={giai_3_1}")
            return {'two_digits_loto': []}
        
        try:
            # Số thứ nhất: Số thứ 3 giải 1.1
            if len(giai_1_1) >= 3:
                first_digit = giai_1_1[2]
            else:
                logger.warning(f"[{self.get_code()}] Giải 1.1 không đủ dài: {giai_1_1}")
                return {'two_digits_loto': []}
                
            # Số thứ hai: Số thứ 5 giải 3.1
            if len(giai_3_1) >= 5:
                second_digit = giai_3_1[4]
            else:
                logger.warning(f"[{self.get_code()}] Giải 3.1 không đủ dài: {giai_3_1}")
                return {'two_digits_loto': []}
            
            # Tạo các cặp số 2 chữ số
            two_digits = set()
            # Cặp số thẳng
            two_digits.add(f"{first_digit}{second_digit}")
            # Cặp số đảo
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
            logger.error(f"[{self.get_code()}] Lỗi tính bạch thủ lô 225: {str(e)}")
            return {'two_digits_loto': []}
        
class Btl_226LotoMethod(BasePredictionMethod):
    """
    Phương pháp Bạch thủ lô 226
    Dự đoán từ số thứ 1 giải 4.1, số thứ 2 giải 5.2
    """
    def get_code(self) -> str:
        return "btl_226"
    
    def get_name(self) -> str:
        return "Bạch thủ lô 226"
    
    def get_description(self) -> str:
        return "Dự đoán các cặp số 2 chữ số từ số thứ 1 giải 4.1 và số thứ 2 giải 5.2"
    
    def calculate(self, data: Dict[str, Any]) -> Dict[str, List[str]]:
        giai_4_1 = data.get('giai_4_1', '')
        giai_5_2 = data.get('giai_5_2', '')
        
        if not giai_4_1 or not giai_5_2:
            logger.warning(f"[{self.get_code()}] Thiếu dữ liệu đầu vào: giai_4_1={giai_4_1}, giai_5_2={giai_5_2}")
            return {'two_digits_loto': []}
        
        try:
            # Số thứ nhất: Số thứ 1 giải 4.1
            if len(giai_4_1) >= 1:
                first_digit = giai_4_1[0]
            else:
                logger.warning(f"[{self.get_code()}] Giải 4.1 không đủ dài: {giai_4_1}")
                return {'two_digits_loto': []}
                
            # Số thứ hai: Số thứ 2 giải 5.2
            if len(giai_5_2) >= 2:
                second_digit = giai_5_2[1]
            else:
                logger.warning(f"[{self.get_code()}] Giải 5.2 không đủ dài: {giai_5_2}")
                return {'two_digits_loto': []}
            
            # Tạo các cặp số 2 chữ số
            two_digits = set()
            # Cặp số thẳng
            two_digits.add(f"{first_digit}{second_digit}")
            # Cặp số đảo
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
            logger.error(f"[{self.get_code()}] Lỗi tính bạch thủ lô 226: {str(e)}")
            return {'two_digits_loto': []}
class Btl_227LotoMethod(BasePredictionMethod):
    """
    Phương pháp Bạch thủ lô 227
    Dự đoán từ số thứ 3 giải 5.4, số thứ 1 giải 7.1
    """
    def get_code(self) -> str:
        return "btl_227"
    
    def get_name(self) -> str:
        return "Bạch thủ lô 227"
    
    def get_description(self) -> str:
        return "Dự đoán các cặp số 2 chữ số từ số thứ 3 giải 5.4 và số thứ 1 giải 7.1"
    
    def calculate(self, data: Dict[str, Any]) -> Dict[str, List[str]]:
        giai_5_4 = data.get('giai_5_4', '')
        giai_7_1 = data.get('giai_7_1', '')
        
        if not giai_5_4 or not giai_7_1:
            logger.warning(f"[{self.get_code()}] Thiếu dữ liệu đầu vào: giai_5_4={giai_5_4}, giai_7_1={giai_7_1}")
            return {'two_digits_loto': []}
        
        try:
            # Số thứ nhất: Số thứ 3 giải 5.4
            if len(giai_5_4) >= 3:
                first_digit = giai_5_4[2]
            else:
                logger.warning(f"[{self.get_code()}] Giải 5.4 không đủ dài: {giai_5_4}")
                return {'two_digits_loto': []}
                
            # Số thứ hai: Số thứ 1 giải 7.1
            if len(giai_7_1) >= 1:
                second_digit = giai_7_1[0]
            else:
                logger.warning(f"[{self.get_code()}] Giải 7.1 không đủ dài: {giai_7_1}")
                return {'two_digits_loto': []}
            
            # Tạo các cặp số 2 chữ số
            two_digits = set()
            # Cặp số thẳng
            two_digits.add(f"{first_digit}{second_digit}")
            # Cặp số đảo
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
            logger.error(f"[{self.get_code()}] Lỗi tính bạch thủ lô 227: {str(e)}")
            return {'two_digits_loto': []}

class Btl_228LotoMethod(BasePredictionMethod):
    """
    Phương pháp Bạch thủ lô 228
    Dự đoán từ số thứ 3 giải 3.6, số thứ 1 giải 4.1
    """
    def get_code(self) -> str:
        return "btl_228"
    
    def get_name(self) -> str:
        return "Bạch thủ lô 228"
    
    def get_description(self) -> str:
        return "Dự đoán các cặp số 2 chữ số từ số thứ 3 giải 3.6 và số thứ 1 giải 4.1"
    
    def calculate(self, data: Dict[str, Any]) -> Dict[str, List[str]]:
        giai_3_6 = data.get('giai_3_6', '')
        giai_4_1 = data.get('giai_4_1', '')
        
        if not giai_3_6 or not giai_4_1:
            logger.warning(f"[{self.get_code()}] Thiếu dữ liệu đầu vào: giai_3_6={giai_3_6}, giai_4_1={giai_4_1}")
            return {'two_digits_loto': []}
        
        try:
            # Số thứ nhất: Số thứ 3 giải 3.6
            if len(giai_3_6) >= 3:
                first_digit = giai_3_6[2]
            else:
                logger.warning(f"[{self.get_code()}] Giải 3.6 không đủ dài: {giai_3_6}")
                return {'two_digits_loto': []}
                
            # Số thứ hai: Số thứ 1 giải 4.1
            if len(giai_4_1) >= 1:
                second_digit = giai_4_1[0]
            else:
                logger.warning(f"[{self.get_code()}] Giải 4.1 không đủ dài: {giai_4_1}")
                return {'two_digits_loto': []}
            
            # Tạo các cặp số 2 chữ số
            two_digits = set()
            # Cặp số thẳng
            two_digits.add(f"{first_digit}{second_digit}")
            # Cặp số đảo
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
            logger.error(f"[{self.get_code()}] Lỗi tính bạch thủ lô 228: {str(e)}")
            return {'two_digits_loto': []}

class Btl_229LotoMethod(BasePredictionMethod):
    """
    Phương pháp Bạch thủ lô 229
    Dự đoán từ số thứ 5 giải 2.1, số thứ 1 giải 7.2
    """
    def get_code(self) -> str:
        return "btl_229"
    
    def get_name(self) -> str:
        return "Bạch thủ lô 229"
    
    def get_description(self) -> str:
        return "Dự đoán các cặp số 2 chữ số từ số thứ 5 giải 2.1 và số thứ 1 giải 7.2"
    
    def calculate(self, data: Dict[str, Any]) -> Dict[str, List[str]]:
        giai_2_1 = data.get('giai_2_1', '')
        giai_7_2 = data.get('giai_7_2', '')
        
        if not giai_2_1 or not giai_7_2:
            logger.warning(f"[{self.get_code()}] Thiếu dữ liệu đầu vào: giai_2_1={giai_2_1}, giai_7_2={giai_7_2}")
            return {'two_digits_loto': []}
        
        try:
            # Số thứ nhất: Số thứ 5 giải 2.1
            if len(giai_2_1) >= 5:
                first_digit = giai_2_1[4]
            else:
                logger.warning(f"[{self.get_code()}] Giải 2.1 không đủ dài: {giai_2_1}")
                return {'two_digits_loto': []}
                
            # Số thứ hai: Số thứ 1 giải 7.2
            if len(giai_7_2) >= 1:
                second_digit = giai_7_2[0]
            else:
                logger.warning(f"[{self.get_code()}] Giải 7.2 không đủ dài: {giai_7_2}")
                return {'two_digits_loto': []}
            
            # Tạo các cặp số 2 chữ số
            two_digits = set()
            # Cặp số thẳng
            two_digits.add(f"{first_digit}{second_digit}")
            # Cặp số đảo
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
            logger.error(f"[{self.get_code()}] Lỗi tính bạch thủ lô 229: {str(e)}")
            return {'two_digits_loto': []}

class Btl_230LotoMethod(BasePredictionMethod):
    """
    Phương pháp Bạch thủ lô 230
    Dự đoán từ số thứ 2 giải 3.2, số thứ 2 giải 4.2
    """
    def get_code(self) -> str:
        return "btl_230"
    
    def get_name(self) -> str:
        return "Bạch thủ lô 230"
    
    def get_description(self) -> str:
        return "Dự đoán các cặp số 2 chữ số từ số thứ 2 giải 3.2 và số thứ 2 giải 4.2"
    
    def calculate(self, data: Dict[str, Any]) -> Dict[str, List[str]]:
        giai_3_2 = data.get('giai_3_2', '')
        giai_4_2 = data.get('giai_4_2', '')
        
        if not giai_3_2 or not giai_4_2:
            logger.warning(f"[{self.get_code()}] Thiếu dữ liệu đầu vào: giai_3_2={giai_3_2}, giai_4_2={giai_4_2}")
            return {'two_digits_loto': []}
        
        try:
            # Số thứ nhất: Số thứ 2 giải 3.2
            if len(giai_3_2) >= 2:
                first_digit = giai_3_2[1]
            else:
                logger.warning(f"[{self.get_code()}] Giải 3.2 không đủ dài: {giai_3_2}")
                return {'two_digits_loto': []}
                
            # Số thứ hai: Số thứ 2 giải 4.2
            if len(giai_4_2) >= 2:
                second_digit = giai_4_2[1]
            else:
                logger.warning(f"[{self.get_code()}] Giải 4.2 không đủ dài: {giai_4_2}")
                return {'two_digits_loto': []}
            
            # Tạo các cặp số 2 chữ số
            two_digits = set()
            # Cặp số thẳng
            two_digits.add(f"{first_digit}{second_digit}")
            # Cặp số đảo
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
            logger.error(f"[{self.get_code()}] Lỗi tính bạch thủ lô 230: {str(e)}")
            return {'two_digits_loto': []}

class Btl_231LotoMethod(BasePredictionMethod):
    """
    Phương pháp Bạch thủ lô 231
    Dự đoán từ số thứ 1 giải đặc biệt, số thứ 1 giải 4.4
    """
    def get_code(self) -> str:
        return "btl_231"
    
    def get_name(self) -> str:
        return "Bạch thủ lô 231"
    
    def get_description(self) -> str:
        return "Dự đoán các cặp số 2 chữ số từ số thứ 1 giải đặc biệt và số thứ 1 giải 4.4"
    
    def calculate(self, data: Dict[str, Any]) -> Dict[str, List[str]]:
        giai_dac_biet = data.get('giai_db', '')
        giai_4_4 = data.get('giai_4_4', '')
        
        if not giai_dac_biet or not giai_4_4:
            logger.warning(f"[{self.get_code()}] Thiếu dữ liệu đầu vào: giai_dac_biet={giai_dac_biet}, giai_4_4={giai_4_4}")
            return {'two_digits_loto': []}
        
        try:
            # Số thứ nhất: Số thứ 1 giải đặc biệt
            if len(giai_dac_biet) >= 1:
                first_digit = giai_dac_biet[0]
            else:
                logger.warning(f"[{self.get_code()}] Giải đặc biệt không đủ dài: {giai_dac_biet}")
                return {'two_digits_loto': []}
                
            # Số thứ hai: Số thứ 1 giải 4.4
            if len(giai_4_4) >= 1:
                second_digit = giai_4_4[0]
            else:
                logger.warning(f"[{self.get_code()}] Giải 4.4 không đủ dài: {giai_4_4}")
                return {'two_digits_loto': []}
            
            # Tạo các cặp số 2 chữ số
            two_digits = set()
            # Cặp số thẳng
            two_digits.add(f"{first_digit}{second_digit}")
            # Cặp số đảo
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
            logger.error(f"[{self.get_code()}] Lỗi tính bạch thủ lô 231: {str(e)}")
            return {'two_digits_loto': []}
        
class Btl_232LotoMethod(BasePredictionMethod):
    """
    Phương pháp Bạch thủ lô 232
    Dự đoán từ số thứ 3 giải 3.4, số thứ 1 giải 6.3
    """
    def get_code(self) -> str:
        return "btl_232"
    
    def get_name(self) -> str:
        return "Bạch thủ lô 232"
    
    def get_description(self) -> str:
        return "Dự đoán các cặp số 2 chữ số từ số thứ 3 giải 3.4 và số thứ 1 giải 6.3"
    
    def calculate(self, data: Dict[str, Any]) -> Dict[str, List[str]]:
        giai_3_4 = data.get('giai_3_4', '')
        giai_6_3 = data.get('giai_6_3', '')
        
        if not giai_3_4 or not giai_6_3:
            logger.warning(f"[{self.get_code()}] Thiếu dữ liệu đầu vào: giai_3_4={giai_3_4}, giai_6_3={giai_6_3}")
            return {'two_digits_loto': []}
        
        try:
            # Số thứ nhất: Số thứ 3 giải 3.4
            if len(giai_3_4) >= 3:
                first_digit = giai_3_4[2]
            else:
                logger.warning(f"[{self.get_code()}] Giải 3.4 không đủ dài: {giai_3_4}")
                return {'two_digits_loto': []}
                
            # Số thứ hai: Số thứ 1 giải 6.3
            if len(giai_6_3) >= 1:
                second_digit = giai_6_3[0]
            else:
                logger.warning(f"[{self.get_code()}] Giải 6.3 không đủ dài: {giai_6_3}")
                return {'two_digits_loto': []}
            
            # Tạo các cặp số 2 chữ số
            two_digits = set()
            # Cặp số thẳng
            two_digits.add(f"{first_digit}{second_digit}")
            # Cặp số đảo
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
            logger.error(f"[{self.get_code()}] Lỗi tính bạch thủ lô 232: {str(e)}")
            return {'two_digits_loto': []}

class Btl_233LotoMethod(BasePredictionMethod):
    """
    Phương pháp Bạch thủ lô 233
    Dự đoán từ số thứ 3 giải 2.1, số thứ 2 giải 3.5
    """
    def get_code(self) -> str:
        return "btl_233"
    
    def get_name(self) -> str:
        return "Bạch thủ lô 233"
    
    def get_description(self) -> str:
        return "Dự đoán các cặp số 2 chữ số từ số thứ 3 giải 2.1 và số thứ 2 giải 3.5"
    
    def calculate(self, data: Dict[str, Any]) -> Dict[str, List[str]]:
        giai_2_1 = data.get('giai_2_1', '')
        giai_3_5 = data.get('giai_3_5', '')
        
        if not giai_2_1 or not giai_3_5:
            logger.warning(f"[{self.get_code()}] Thiếu dữ liệu đầu vào: giai_2_1={giai_2_1}, giai_3_5={giai_3_5}")
            return {'two_digits_loto': []}
        
        try:
            # Số thứ nhất: Số thứ 3 giải 2.1
            if len(giai_2_1) >= 3:
                first_digit = giai_2_1[2]
            else:
                logger.warning(f"[{self.get_code()}] Giải 2.1 không đủ dài: {giai_2_1}")
                return {'two_digits_loto': []}
                
            # Số thứ hai: Số thứ 2 giải 3.5
            if len(giai_3_5) >= 2:
                second_digit = giai_3_5[1]
            else:
                logger.warning(f"[{self.get_code()}] Giải 3.5 không đủ dài: {giai_3_5}")
                return {'two_digits_loto': []}
            
            # Tạo các cặp số 2 chữ số
            two_digits = set()
            # Cặp số thẳng
            two_digits.add(f"{first_digit}{second_digit}")
            # Cặp số đảo
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
            logger.error(f"[{self.get_code()}] Lỗi tính bạch thủ lô 233: {str(e)}")
            return {'two_digits_loto': []}
        
class Btl_234LotoMethod(BasePredictionMethod):
    """
    Phương pháp Bạch thủ lô 234
    Dự đoán từ số thứ 2 giải 3.5, số thứ 3 giải 4.1
    """
    def get_code(self) -> str:
        return "btl_234"
    
    def get_name(self) -> str:
        return "Bạch thủ lô 234"
    
    def get_description(self) -> str:
        return "Dự đoán các cặp số 2 chữ số từ số thứ 2 giải 3.5 và số thứ 3 giải 4.1"
    
    def calculate(self, data: Dict[str, Any]) -> Dict[str, List[str]]:
        giai_3_5 = data.get('giai_3_5', '')
        giai_4_1 = data.get('giai_4_1', '')
        
        if not giai_3_5 or not giai_4_1:
            logger.warning(f"[{self.get_code()}] Thiếu dữ liệu đầu vào: giai_3_5={giai_3_5}, giai_4_1={giai_4_1}")
            return {'two_digits_loto': []}
        
        try:
            # Số thứ nhất: Số thứ 2 giải 3.5
            if len(giai_3_5) >= 2:
                first_digit = giai_3_5[1]
            else:
                logger.warning(f"[{self.get_code()}] Giải 3.5 không đủ dài: {giai_3_5}")
                return {'two_digits_loto': []}
                
            # Số thứ hai: Số thứ 3 giải 4.1
            if len(giai_4_1) >= 3:
                second_digit = giai_4_1[2]
            else:
                logger.warning(f"[{self.get_code()}] Giải 4.1 không đủ dài: {giai_4_1}")
                return {'two_digits_loto': []}
            
            # Tạo các cặp số 2 chữ số
            two_digits = set()
            # Cặp số thẳng
            two_digits.add(f"{first_digit}{second_digit}")
            # Cặp số đảo
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
            logger.error(f"[{self.get_code()}] Lỗi tính bạch thủ lô 234: {str(e)}")
            return {'two_digits_loto': []}

class Btl_234LotoMethod(BasePredictionMethod):
    """
    Phương pháp Bạch thủ lô 234
    Dự đoán từ số thứ 2 giải 3.5, số thứ 3 giải 4.1
    """
    def get_code(self) -> str:
        return "btl_234"
    
    def get_name(self) -> str:
        return "Bạch thủ lô 234"
    
    def get_description(self) -> str:
        return "Dự đoán các cặp số 2 chữ số từ số thứ 2 giải 3.5 và số thứ 3 giải 4.1"
    
    def calculate(self, data: Dict[str, Any]) -> Dict[str, List[str]]:
        giai_3_5 = data.get('giai_3_5', '')
        giai_4_1 = data.get('giai_4_1', '')
        
        if not giai_3_5 or not giai_4_1:
            logger.warning(f"[{self.get_code()}] Thiếu dữ liệu đầu vào: giai_3_5={giai_3_5}, giai_4_1={giai_4_1}")
            return {'two_digits_loto': []}
        
        try:
            # Số thứ nhất: Số thứ 2 giải 3.5
            if len(giai_3_5) >= 2:
                first_digit = giai_3_5[1]
            else:
                logger.warning(f"[{self.get_code()}] Giải 3.5 không đủ dài: {giai_3_5}")
                return {'two_digits_loto': []}
                
            # Số thứ hai: Số thứ 3 giải 4.1
            if len(giai_4_1) >= 3:
                second_digit = giai_4_1[2]
            else:
                logger.warning(f"[{self.get_code()}] Giải 4.1 không đủ dài: {giai_4_1}")
                return {'two_digits_loto': []}
            
            # Tạo các cặp số 2 chữ số
            two_digits = set()
            # Cặp số thẳng
            two_digits.add(f"{first_digit}{second_digit}")
            # Cặp số đảo
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
            logger.error(f"[{self.get_code()}] Lỗi tính bạch thủ lô 234: {str(e)}")
            return {'two_digits_loto': []}
        
class Btl_235LotoMethod(BasePredictionMethod):
    """
    Phương pháp Bạch thủ lô 235
    Dự đoán từ số thứ 4 giải đặc biệt, số thứ 5 giải đặc biệt
    """
    def get_code(self) -> str:
        return "btl_235"
    
    def get_name(self) -> str:
        return "Bạch thủ lô 235"
    
    def get_description(self) -> str:
        return "Dự đoán các cặp số 2 chữ số từ số thứ 4 giải đặc biệt và số thứ 5 giải đặc biệt"
    
    def calculate(self, data: Dict[str, Any]) -> Dict[str, List[str]]:
        giai_dac_biet = data.get('giai_db', '')
        
        if not giai_dac_biet:
            logger.warning(f"[{self.get_code()}] Thiếu dữ liệu đầu vào: giai_dac_biet={giai_dac_biet}")
            return {'two_digits_loto': []}
        
        try:
            # Số thứ nhất: Số thứ 4 giải đặc biệt
            if len(giai_dac_biet) >= 4:
                first_digit = giai_dac_biet[3]
            else:
                logger.warning(f"[{self.get_code()}] Giải đặc biệt không đủ dài: {giai_dac_biet}")
                return {'two_digits_loto': []}
                
            # Số thứ hai: Số thứ 5 giải đặc biệt
            if len(giai_dac_biet) >= 5:
                second_digit = giai_dac_biet[4]
            else:
                logger.warning(f"[{self.get_code()}] Giải đặc biệt không đủ dài: {giai_dac_biet}")
                return {'two_digits_loto': []}
            
            # Tạo các cặp số 2 chữ số
            two_digits = set()
            # Cặp số thẳng
            two_digits.add(f"{first_digit}{second_digit}")
            # Cặp số đảo
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
            logger.error(f"[{self.get_code()}] Lỗi tính bạch thủ lô 235: {str(e)}")
            return {'two_digits_loto': []}
        
class Btl_236LotoMethod(BasePredictionMethod):
    """
    Phương pháp Bạch thủ lô 236
    Dự đoán từ số thứ 1 giải 4.4, số thứ 3 giải 5.3
    """
    def get_code(self) -> str:
        return "btl_236"
    
    def get_name(self) -> str:
        return "Bạch thủ lô 236"
    
    def get_description(self) -> str:
        return "Dự đoán các cặp số 2 chữ số từ số thứ 1 giải 4.4 và số thứ 3 giải 5.3"
    
    def calculate(self, data: Dict[str, Any]) -> Dict[str, List[str]]:
        giai_4_4 = data.get('giai_4_4', '')
        giai_5_3 = data.get('giai_5_3', '')
        
        if not giai_4_4 or not giai_5_3:
            logger.warning(f"[{self.get_code()}] Thiếu dữ liệu đầu vào: giai_4_4={giai_4_4}, giai_5_3={giai_5_3}")
            return {'two_digits_loto': []}
        
        try:
            # Số thứ nhất: Số thứ 1 giải 4.4
            if len(giai_4_4) >= 1:
                first_digit = giai_4_4[0]
            else:
                logger.warning(f"[{self.get_code()}] Giải 4.4 không đủ dài: {giai_4_4}")
                return {'two_digits_loto': []}
                
            # Số thứ hai: Số thứ 3 giải 5.3
            if len(giai_5_3) >= 3:
                second_digit = giai_5_3[2]
            else:
                logger.warning(f"[{self.get_code()}] Giải 5.3 không đủ dài: {giai_5_3}")
                return {'two_digits_loto': []}
            
            # Tạo các cặp số 2 chữ số
            two_digits = set()
            # Cặp số thẳng
            two_digits.add(f"{first_digit}{second_digit}")
            # Cặp số đảo
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
            logger.error(f"[{self.get_code()}] Lỗi tính bạch thủ lô 236: {str(e)}")
            return {'two_digits_loto': []}
        
class Btl_237LotoMethod(BasePredictionMethod):
    """
    Phương pháp Bạch thủ lô 237
    Dự đoán từ giải 3.2.4 và giải 4.2.1
    """

    def get_code(self) -> str:
        return "btl_237"
    
    def get_name(self) -> str:
        return "Bạch thủ lô 237"
    
    def get_description(self) -> str:
        return "Dự đoán các cặp số 2 chữ số từ giải 3.2.4 và giải 4.2.1"

    def calculate(self, data: Dict[str, Any]) -> Dict[str, List[str]]:
        giai_3_2 = data.get('giai_3_2', '')
        giai_4_2 = data.get('giai_4_2', '')

        if not giai_3_2 or not giai_4_2:
            logger.warning(f"[{self.get_code()}] Thiếu dữ liệu đầu vào: giai_3_2={giai_3_2}, giai_4_2={giai_4_2}")
            return {'two_digits_loto': []}

        try:
            # Lấy số thứ 4 từ giải 3.2 (giải 3 có 5 chữ số)
            if len(giai_3_2) >= 4:
                digit1 = giai_3_2[3]
            else:
                logger.warning(f"[{self.get_code()}] Giải 3.2 không đủ dài: {giai_3_2}")
                return {'two_digits_loto': []}

            # Lấy số thứ 1 từ giải 4.2 (giải 4 có 4 chữ số)
            if len(giai_4_2) >= 1:
                digit2 = giai_4_2[0]
            else:
                logger.warning(f"[{self.get_code()}] Giải 4.2 không đủ dài: {giai_4_2}")
                return {'two_digits_loto': []}

            # Tạo các cặp số 2 chữ số
            two_digits = set()
            two_digits.add(f"{digit1}{digit2}")
            if digit1 != digit2:
                two_digits.add(f"{digit2}{digit1}")

            logger.info(f"[{self.get_code()}] Kết quả: {sorted(list(two_digits))}")
            return {'two_digits_loto': sorted(list(two_digits))}
        
        except (ValueError, IndexError, TypeError) as e:
            logger.error(f"[{self.get_code()}] Lỗi tính BTL 237: {str(e)}")
            return {'two_digits_loto': []}


class Btl_238LotoMethod(BasePredictionMethod):
    """
    Phương pháp Bạch thủ lô 238
    Dự đoán từ giải 3.3.2 và giải 5.5.2
    """

    def get_code(self) -> str:
        return "btl_238"
    
    def get_name(self) -> str:
        return "Bạch thủ lô 238"
    
    def get_description(self) -> str:
        return "Dự đoán các cặp số 2 chữ số từ giải 3.3.2 và giải 5.5.2"

    def calculate(self, data: Dict[str, Any]) -> Dict[str, List[str]]:
        giai_3_3 = data.get('giai_3_3', '')
        giai_5_5 = data.get('giai_5_5', '')

        if not giai_3_3 or not giai_5_5:
            logger.warning(f"[{self.get_code()}] Thiếu dữ liệu đầu vào: giai_3_3={giai_3_3}, giai_5_5={giai_5_5}")
            return {'two_digits_loto': []}

        try:
            # Lấy số thứ 2 từ giải 3.3 (giải 3 có 5 chữ số)
            if len(giai_3_3) >= 2:
                digit1 = giai_3_3[1]
            else:
                logger.warning(f"[{self.get_code()}] Giải 3.3 không đủ dài: {giai_3_3}")
                return {'two_digits_loto': []}

            # Lấy số thứ 2 từ giải 5.5 (giải 5 có 4 chữ số)
            if len(giai_5_5) >= 2:
                digit2 = giai_5_5[1]
            else:
                logger.warning(f"[{self.get_code()}] Giải 5.5 không đủ dài: {giai_5_5}")
                return {'two_digits_loto': []}

            # Tạo các cặp số 2 chữ số
            two_digits = set()
            two_digits.add(f"{digit1}{digit2}")
            if digit1 != digit2:
                two_digits.add(f"{digit2}{digit1}")

            logger.info(f"[{self.get_code()}] Kết quả: {sorted(list(two_digits))}")
            return {'two_digits_loto': sorted(list(two_digits))}

        except (ValueError, IndexError, TypeError) as e:
            logger.error(f"[{self.get_code()}] Lỗi tính BTL 238: {str(e)}")
            return {'two_digits_loto': []}

class Btl_239LotoMethod(BasePredictionMethod):
    """
    Phương pháp Bạch thủ lô 239
    Dự đoán từ giải 5.1.3 và giải 7.2.2
    """

    def get_code(self) -> str:
        return "btl_239"
    
    def get_name(self) -> str:
        return "Bạch thủ lô 239"
    
    def get_description(self) -> str:
        return "Dự đoán các cặp số 2 chữ số từ giải 5.1.3 và giải 7.2.2"

    def calculate(self, data: Dict[str, Any]) -> Dict[str, List[str]]:
        giai_5_1 = data.get('giai_5_1', '')
        giai_7_2 = data.get('giai_7_2', '')

        if not giai_5_1 or not giai_7_2:
            logger.warning(f"[{self.get_code()}] Thiếu dữ liệu đầu vào: giai_5_1={giai_5_1}, giai_7_2={giai_7_2}")
            return {'two_digits_loto': []}

        try:
            # Lấy số thứ 3 từ giải 5.1 (giải 5 có 4 chữ số)
            if len(giai_5_1) >= 3:
                digit1 = giai_5_1[2]
            else:
                logger.warning(f"[{self.get_code()}] Giải 5.1 không đủ dài: {giai_5_1}")
                return {'two_digits_loto': []}

            # Lấy số thứ 2 từ giải 7.2 (giải 7 có 2 chữ số)
            if len(giai_7_2) >= 2:
                digit2 = giai_7_2[1]
            else:
                logger.warning(f"[{self.get_code()}] Giải 7.2 không đủ dài: {giai_7_2}")
                return {'two_digits_loto': []}

            # Tạo các cặp số 2 chữ số
            two_digits = set()
            two_digits.add(f"{digit1}{digit2}")
            if digit1 != digit2:
                two_digits.add(f"{digit2}{digit1}")

            logger.info(f"[{self.get_code()}] Kết quả: {sorted(list(two_digits))}")
            return {'two_digits_loto': sorted(list(two_digits))}

        except (ValueError, IndexError, TypeError) as e:
            logger.error(f"[{self.get_code()}] Lỗi tính BTL 239: {str(e)}")
            return {'two_digits_loto': []}

class Btl_240LotoMethod(BasePredictionMethod):
    """
    Phương pháp Bạch thủ lô 240
    Dự đoán từ giải 5.5.2 và giải 7.1.1
    """

    def get_code(self) -> str:
        return "btl_240"
    
    def get_name(self) -> str:
        return "Bạch thủ lô 240"
    
    def get_description(self) -> str:
        return "Dự đoán các cặp số 2 chữ số từ giải 5.5.2 và giải 7.1.1"

    def calculate(self, data: Dict[str, Any]) -> Dict[str, List[str]]:
        giai_5_5 = data.get('giai_5_5', '')
        giai_7_1 = data.get('giai_7_1', '')

        if not giai_5_5 or not giai_7_1:
            logger.warning(f"[{self.get_code()}] Thiếu dữ liệu đầu vào: giai_5_5={giai_5_5}, giai_7_1={giai_7_1}")
            return {'two_digits_loto': []}

        try:
            # Lấy số thứ 2 từ giải 5.5 (4 chữ số)
            if len(giai_5_5) >= 2:
                digit1 = giai_5_5[1]
            else:
                logger.warning(f"[{self.get_code()}] Giải 5.5 không đủ dài: {giai_5_5}")
                return {'two_digits_loto': []}

            # Lấy số thứ 1 từ giải 7.1 (2 chữ số)
            if len(giai_7_1) >= 1:
                digit2 = giai_7_1[0]
            else:
                logger.warning(f"[{self.get_code()}] Giải 7.1 không đủ dài: {giai_7_1}")
                return {'two_digits_loto': []}

            # Tạo các cặp số 2 chữ số
            two_digits = set()
            two_digits.add(f"{digit1}{digit2}")
            if digit1 != digit2:
                two_digits.add(f"{digit2}{digit1}")

            logger.info(f"[{self.get_code()}] Kết quả: {sorted(list(two_digits))}")
            return {'two_digits_loto': sorted(list(two_digits))}

        except (ValueError, IndexError, TypeError) as e:
            logger.error(f"[{self.get_code()}] Lỗi tính BTL 240: {str(e)}")
            return {'two_digits_loto': []}

class Btl_241LotoMethod(BasePredictionMethod):
    """
    Phương pháp Bạch thủ lô 241
    Dự đoán từ giải 3.2.5 và giải 5.5.3
    """

    def get_code(self) -> str:
        return "btl_241"
    
    def get_name(self) -> str:
        return "Bạch thủ lô 241"
    
    def get_description(self) -> str:
        return "Dự đoán các cặp số 2 chữ số từ giải 3.2.5 và giải 5.5.3"

    def calculate(self, data: Dict[str, Any]) -> Dict[str, List[str]]:
        giai_3_2 = data.get('giai_3_2', '')
        giai_5_5 = data.get('giai_5_5', '')

        if not giai_3_2 or not giai_5_5:
            logger.warning(f"[{self.get_code()}] Thiếu dữ liệu đầu vào: giai_3_2={giai_3_2}, giai_5_5={giai_5_5}")
            return {'two_digits_loto': []}

        try:
            # Lấy số thứ 5 từ giải 3.2 (giải 3 có 5 chữ số)
            if len(giai_3_2) >= 5:
                digit1 = giai_3_2[4]
            else:
                logger.warning(f"[{self.get_code()}] Giải 3.2 không đủ dài: {giai_3_2}")
                return {'two_digits_loto': []}

            # Lấy số thứ 3 từ giải 5.5 (giải 5 có 4 chữ số)
            if len(giai_5_5) >= 3:
                digit2 = giai_5_5[2]
            else:
                logger.warning(f"[{self.get_code()}] Giải 5.5 không đủ dài: {giai_5_5}")
                return {'two_digits_loto': []}

            # Tạo các cặp số 2 chữ số
            two_digits = set()
            two_digits.add(f"{digit1}{digit2}")
            if digit1 != digit2:
                two_digits.add(f"{digit2}{digit1}")

            logger.info(f"[{self.get_code()}] Kết quả: {sorted(list(two_digits))}")
            return {'two_digits_loto': sorted(list(two_digits))}

        except (ValueError, IndexError, TypeError) as e:
            logger.error(f"[{self.get_code()}] Lỗi tính BTL 241: {str(e)}")
            return {'two_digits_loto': []}

class Btl_242LotoMethod(BasePredictionMethod):
    """
    Phương pháp Bạch thủ lô 242
    Dự đoán từ giải 2.2.4 và giải 6.2.2
    """

    def get_code(self) -> str:
        return "btl_242"
    
    def get_name(self) -> str:
        return "Bạch thủ lô 242"
    
    def get_description(self) -> str:
        return "Dự đoán các cặp số 2 chữ số từ giải 2.2.4 và giải 6.2.2"

    def calculate(self, data: Dict[str, Any]) -> Dict[str, List[str]]:
        giai_2_2 = data.get('giai_2_2', '')
        giai_6_2 = data.get('giai_6_2', '')

        if not giai_2_2 or not giai_6_2:
            logger.warning(f"[{self.get_code()}] Thiếu dữ liệu đầu vào: giai_2_2={giai_2_2}, giai_6_2={giai_6_2}")
            return {'two_digits_loto': []}

        try:
            # Lấy số thứ 4 từ giải 2.2 (5 chữ số)
            if len(giai_2_2) >= 4:
                digit1 = giai_2_2[3]
            else:
                logger.warning(f"[{self.get_code()}] Giải 2.2 không đủ dài: {giai_2_2}")
                return {'two_digits_loto': []}

            # Lấy số thứ 2 từ giải 6.2 (3 chữ số)
            if len(giai_6_2) >= 2:
                digit2 = giai_6_2[1]
            else:
                logger.warning(f"[{self.get_code()}] Giải 6.2 không đủ dài: {giai_6_2}")
                return {'two_digits_loto': []}

            # Tạo các cặp số 2 chữ số
            two_digits = set()
            two_digits.add(f"{digit1}{digit2}")
            if digit1 != digit2:
                two_digits.add(f"{digit2}{digit1}")

            logger.info(f"[{self.get_code()}] Kết quả: {sorted(list(two_digits))}")
            return {'two_digits_loto': sorted(list(two_digits))}

        except (ValueError, IndexError, TypeError) as e:
            logger.error(f"[{self.get_code()}] Lỗi tính BTL 242: {str(e)}")
            return {'two_digits_loto': []}

class Btl_244LotoMethod(BasePredictionMethod):
    """
    Phương pháp Bạch thủ lô 244
    Dự đoán từ giải 2.2.4 và giải 4.2.4
    """

    def get_code(self) -> str:
        return "btl_244"
    
    def get_name(self) -> str:
        return "Bạch thủ lô 244"
    
    def get_description(self) -> str:
        return "Dự đoán các cặp số 2 chữ số từ giải 2.2.4 và giải 4.2.4"

    def calculate(self, data: Dict[str, Any]) -> Dict[str, List[str]]:
        giai_2_2 = data.get('giai_2_2', '')
        giai_4_2 = data.get('giai_4_2', '')

        if not giai_2_2 or not giai_4_2:
            logger.warning(f"[{self.get_code()}] Thiếu dữ liệu đầu vào: giai_2_2={giai_2_2}, giai_4_2={giai_4_2}")
            return {'two_digits_loto': []}

        try:
            # Lấy số thứ 4 từ giải 2.2 (5 chữ số)
            if len(giai_2_2) >= 4:
                digit1 = giai_2_2[3]
            else:
                logger.warning(f"[{self.get_code()}] Giải 2.2 không đủ dài: {giai_2_2}")
                return {'two_digits_loto': []}

            # Lấy số thứ 4 từ giải 4.2 (4 chữ số)
            if len(giai_4_2) >= 4:
                digit2 = giai_4_2[3]
            else:
                logger.warning(f"[{self.get_code()}] Giải 4.2 không đủ dài: {giai_4_2}")
                return {'two_digits_loto': []}

            # Tạo các cặp số 2 chữ số
            two_digits = set()
            two_digits.add(f"{digit1}{digit2}")
            if digit1 != digit2:
                two_digits.add(f"{digit2}{digit1}")

            logger.info(f"[{self.get_code()}] Kết quả: {sorted(list(two_digits))}")
            return {'two_digits_loto': sorted(list(two_digits))}

        except (ValueError, IndexError, TypeError) as e:
            logger.error(f"[{self.get_code()}] Lỗi tính BTL 244: {str(e)}")
            return {'two_digits_loto': []}

class Btl_245LotoMethod(BasePredictionMethod):
    """
    Phương pháp Bạch thủ lô 245
    Dự đoán từ giải 4.3.3 và giải 7.2.2
    """

    def get_code(self) -> str:
        return "btl_245"
    
    def get_name(self) -> str:
        return "Bạch thủ lô 245"
    
    def get_description(self) -> str:
        return "Dự đoán các cặp số 2 chữ số từ giải 4.3.3 và giải 7.2.2"

    def calculate(self, data: Dict[str, Any]) -> Dict[str, List[str]]:
        giai_4_3 = data.get('giai_4_3', '')
        giai_7_2 = data.get('giai_7_2', '')

        if not giai_4_3 or not giai_7_2:
            logger.warning(f"[{self.get_code()}] Thiếu dữ liệu đầu vào: giai_4_3={giai_4_3}, giai_7_2={giai_7_2}")
            return {'two_digits_loto': []}

        try:
            # Lấy số thứ 3 từ giải 4.3 (4 chữ số)
            if len(giai_4_3) >= 3:
                digit1 = giai_4_3[2]
            else:
                logger.warning(f"[{self.get_code()}] Giải 4.3 không đủ dài: {giai_4_3}")
                return {'two_digits_loto': []}

            # Lấy số thứ 2 từ giải 7.2 (2 chữ số)
            if len(giai_7_2) >= 2:
                digit2 = giai_7_2[1]
            else:
                logger.warning(f"[{self.get_code()}] Giải 7.2 không đủ dài: {giai_7_2}")
                return {'two_digits_loto': []}

            # Tạo các cặp số 2 chữ số
            two_digits = set()
            two_digits.add(f"{digit1}{digit2}")
            if digit1 != digit2:
                two_digits.add(f"{digit2}{digit1}")

            logger.info(f"[{self.get_code()}] Kết quả: {sorted(list(two_digits))}")
            return {'two_digits_loto': sorted(list(two_digits))}

        except (ValueError, IndexError, TypeError) as e:
            logger.error(f"[{self.get_code()}] Lỗi tính BTL 245: {str(e)}")
            return {'two_digits_loto': []}
class Btl_246LotoMethod(BasePredictionMethod ,BaseMakeResult):
    def get_code(self): return "btl_246"
    def get_name(self): return "Bạch thủ lô 246"
    def get_description(self): return "Từ giải 5.2.4 và giải 6.2.3"
    def calculate(self, data): return self._make_result(data, 'giai_5_2', 3, 'giai_6_2', 2)

class Btl_247LotoMethod(BasePredictionMethod,BaseMakeResult):
    def get_code(self): return "btl_247"
    def get_name(self): return "Bạch thủ lô 247"
    def get_description(self): return "Từ giải 6.2.3 và giải 6.3.3"
    def calculate(self, data): return self._make_result(data, 'giai_6_2', 2, 'giai_6_3', 2)

class Btl_248LotoMethod(BasePredictionMethod,BaseMakeResult):
    def get_code(self): return "btl_248"
    def get_name(self): return "Bạch thủ lô 248"
    def get_description(self): return "Từ giải 5.5.2 và giải 6.3.1"
    def calculate(self, data): return self._make_result(data, 'giai_5_5', 1, 'giai_6_3', 0)

class Btl_249LotoMethod(BasePredictionMethod,BaseMakeResult):
    def get_code(self): return "btl_249"
    def get_name(self): return "Bạch thủ lô 249"
    def get_description(self): return "Từ giải 1.1.4 và giải 2.2.4"
    def calculate(self, data): return self._make_result(data, 'giai_1', 3, 'giai_2_2', 3)

class Btl_250LotoMethod(BasePredictionMethod,BaseMakeResult):
    def get_code(self): return "btl_250"
    def get_name(self): return "Bạch thủ lô 250"
    def get_description(self): return "Từ giải 3.5.4 và giải 7.1.2"
    def calculate(self, data): return self._make_result(data, 'giai_3_5', 3, 'giai_7_1', 1)

class Btl_251LotoMethod(BasePredictionMethod,BaseMakeResult):
    def get_code(self): return "btl_251"
    def get_name(self): return "Bạch thủ lô 251"
    def get_description(self): return "Từ giải 6.1.2 và giải 7.4.2"
    def calculate(self, data): return self._make_result(data, 'giai_6_1', 1, 'giai_7_4', 1)

class Btl_252LotoMethod(BasePredictionMethod,BaseMakeResult):
    def get_code(self): return "btl_252"
    def get_name(self): return "Bạch thủ lô 252"
    def get_description(self): return "Từ giải 5.2.3 và giải 5.5.1"
    def calculate(self, data): return self._make_result(data, 'giai_5_2', 2, 'giai_5_5', 0)

class Btl_253LotoMethod(BasePredictionMethod,BaseMakeResult):
    def get_code(self): return "btl_253"
    def get_name(self): return "Bạch thủ lô 253"
    def get_description(self): return "Từ giải 6.2.3 và giải 6.3.2"
    def calculate(self, data): return self._make_result(data, 'giai_6_2', 2, 'giai_6_3', 1)

class Btl_254LotoMethod(BasePredictionMethod,BaseMakeResult):
    def get_code(self): return "btl_254"
    def get_name(self): return "Bạch thủ lô 254"
    def get_description(self): return "Từ giải 7.1.1 và giải 5.6.2"
    def calculate(self, data): return self._make_result(data, 'giai_7_1', 0, 'giai_5_6', 1)

class Btl_255LotoMethod(BasePredictionMethod, BaseMakeResult):
    def get_code(self): return "btl_255"
    def get_name(self): return "Bạch thủ lô 255"
    def get_description(self): return "Từ giải 7.1.1 và giải 7.2.2"
    def calculate(self, data): return self._make_result(data, 'giai_7_1', 0, 'giai_7_2', 1)


class Btl_Soicau_01LotoMethod(BasePredictionMethod,BaseMakeResult):
    def get_code(self): return "Btl_Soicau_01"
    def get_name(self): return "Bạch thủ lô Soi cầu 01"
    def get_description(self): return "Từ giải 3.1.4 và giải 3.6.5"
    def calculate(self, data): return self._make_result(data, 'giai_3_1', 3, 'giai_3_6', 4)
   
