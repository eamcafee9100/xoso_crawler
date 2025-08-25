
# bach_thu_methods/gan_method.py
from .base import BaseBachThuMethod
from typing import Dict, List, Any
import logging

logger = logging.getLogger(__name__)

class GanMethod(BaseBachThuMethod):
    """
    Phương pháp Gàn - dự đoán từ các số gần nhau trong kết quả
    """
    
    def get_code(self) -> str:
        return "GAN_METHOD"
    
    def get_name(self) -> str:
        return "Phương pháp Gàn"
    
    def get_description(self) -> str:
        return "Dự đoán bạch thủ lô từ các số liền kề và gần nhau trong kết quả xổ số"
    
    def get_default_confidence_level(self) -> int:
        return 3
    
    def get_required_fields(self) -> List[str]:
        return ["giai_dac_biet", "giai_nhat"]
    
    def calculate(self, data: Dict[str, Any]) -> List[str]:
        """
        Tính toán bạch thủ lô bằng phương pháp gàn
        
        Logic:
        - Lấy các số từ giải đặc biệt và giải nhất
        - Tìm các số liền kề (+1, -1)
        - Ghép các số gần nhau
        """
        try:
            if not self.validate_input(data):
                return []
            
            bach_thu_numbers = []
            
            # Lấy dữ liệu
            gdb = str(data.get("giai_dac_biet", ""))
            giai_nhat = str(data.get("giai_nhat", ""))
            
            # Trích xuất các số 2 chữ số
            base_numbers = []
            base_numbers.extend(self.extract_two_digit_numbers(gdb))
            base_numbers.extend(self.extract_two_digit_numbers(giai_nhat))
            
            # Loại bỏ trùng lặp
            base_numbers = list(set(base_numbers))
            
            # Tạo các số gàn (liền kề)
            for num_str in base_numbers:
                try:
                    num = int(num_str)
                    
                    # Số liền trước
                    if num > 0:
                        prev_num = str(num - 1).zfill(2)
                        if prev_num not in bach_thu_numbers:
                            bach_thu_numbers.append(prev_num)
                    
                    # Số liền sau
                    if num < 99:
                        next_num = str(num + 1).zfill(2)
                        if next_num not in bach_thu_numbers:
                            bach_thu_numbers.append(next_num)
                    
                    # Số gốc
                    if num_str not in bach_thu_numbers:
                        bach_thu_numbers.append(num_str)
                        
                except ValueError:
                    continue
            
            logger.info(f"GAN method result: {bach_thu_numbers}")
            return bach_thu_numbers[:6]  # Giới hạn tối đa 6 số
            
        except Exception as e:
            logger.error(f"Error in GAN method calculation: {e}")
            return []