from .base import BaseBachThuMethod
from typing import Dict, List, Any
import logging

logger = logging.getLogger(__name__)

class GapMethod(BaseBachThuMethod):
    """
    Phương pháp Gãy - dự đoán bạch thủ lô từ giải đặc biệt của ngày hôm trước
    """
    
    def get_code(self) -> str:
        return "GAP_METHOD"
    
    def get_name(self) -> str:
        return "Phương pháp Gãy"
    
    def get_description(self) -> str:
        return "Dự đoán bạch thủ lô bằng cách 'gãy' các số từ giải đặc biệt ngày hôm trước"
    
    def get_default_confidence_level(self) -> int:
        return 3
    
    def get_required_fields(self) -> List[str]:
        return ["giai_dac_biet_prev"]
    
    def calculate(self, data: Dict[str, Any]) -> List[str]:
        """
        Tính toán bạch thủ lô bằng phương pháp gãy
        
        Logic:
        - Lấy giải đặc biệt ngày hôm trước
        - Gãy thành các cặp số 2 chữ số
        - Tính tổng từng cặp và lấy 2 chữ số cuối
        """
        try:
            if not self.validate_input(data):
                return []
            
            gdb_prev = str(data.get("giai_dac_biet_prev", ""))
            logger.info(f"Calculating GAP method for: {gdb_prev}")
            
            # Trích xuất các số 2 chữ số
            two_digit_numbers = self.extract_two_digit_numbers(gdb_prev)
            
            bach_thu_numbers = []
            
            # Phương pháp gãy: lấy các cặp số liền kề
            clean_str = ''.join(filter(str.isdigit, gdb_prev))
            if len(clean_str) >= 4:
                for i in range(0, len(clean_str) - 1, 2):
                    if i + 1 < len(clean_str):
                        pair = clean_str[i:i+2]
                        if len(pair) == 2:
                            bach_thu_numbers.append(pair)
            
            # Thêm 2 chữ số cuối
            if len(clean_str) >= 2:
                last_two = clean_str[-2:]
                if last_two not in bach_thu_numbers:
                    bach_thu_numbers.append(last_two)
            
            # Tính tổng và gãy
            if len(clean_str) >= 2:
                sum_digits = self.calculate_sum_digits(clean_str)
                if sum_digits not in bach_thu_numbers:
                    bach_thu_numbers.append(sum_digits)
            
            logger.info(f"GAP method result: {bach_thu_numbers}")
            return bach_thu_numbers[:5]  # Giới hạn tối đa 5 số
            
        except Exception as e:
            logger.error(f"Error in GAP method calculation: {e}")
            return []
