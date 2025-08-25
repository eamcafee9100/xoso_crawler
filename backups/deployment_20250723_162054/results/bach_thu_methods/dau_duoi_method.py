
from .base import BaseBachThuMethod
from typing import Dict, List, Any
import logging

logger = logging.getLogger(__name__)

class DauDuoiMethod(BaseBachThuMethod):
    """
    Phương pháp Đầu Đuôi - dự đoán từ đầu và đuôi các giải
    """
    
    def get_code(self) -> str:
        return "DAU_DUOI_METHOD"
    
    def get_name(self) -> str:
        return "Phương pháp Đầu Đuôi"
    
    def get_description(self) -> str:
        return "Dự đoán bạch thủ lô từ số đầu và số đuôi của các giải thưởng"
    
    def get_default_confidence_level(self) -> int:
        return 4
    
    def get_required_fields(self) -> List[str]:
        return ["giai_nhat", "giai_nhi", "giai_ba"]
    
    def calculate(self, data: Dict[str, Any]) -> List[str]:
        """
        Tính toán bạch thủ lô bằng phương pháp đầu đuôi
        
        Logic:
        - Lấy số đầu và số đuôi của các giải
        - Ghép các tổ hợp đầu-đuôi
        """
        try:
            if not self.validate_input(data):
                return []
            
            bach_thu_numbers = []
            
            # Lấy dữ liệu các giải
            giai_nhat = str(data.get("giai_nhat", ""))
            giai_nhi = data.get("giai_nhi", [])
            giai_ba = data.get("giai_ba", [])
            
            # Tập hợp tất cả các số
            all_numbers = [giai_nhat]
            if isinstance(giai_nhi, list):
                all_numbers.extend([str(x) for x in giai_nhi])
            if isinstance(giai_ba, list):
                all_numbers.extend([str(x) for x in giai_ba])
            
            # Lấy số đầu và số đuôi
            dau_numbers = []
            duoi_numbers = []
            
            for num_str in all_numbers:
                clean_num = ''.join(filter(str.isdigit, str(num_str)))
                if len(clean_num) >= 2:
                    dau = clean_num[0]
                    duoi = clean_num[-1]
                    dau_numbers.append(dau)
                    duoi_numbers.append(duoi)
            
            # Loại bỏ trùng lặp
            dau_numbers = list(set(dau_numbers))
            duoi_numbers = list(set(duoi_numbers))
            
            # Tạo tổ hợp đầu-đuôi
            for dau in dau_numbers:
                for duoi in duoi_numbers:
                    combination = dau + duoi
                    if combination not in bach_thu_numbers:
                        bach_thu_numbers.append(combination)
            
            logger.info(f"DAU_DUOI method result: {bach_thu_numbers}")
            return bach_thu_numbers[:8]  # Giới hạn tối đa 8 số
            
        except Exception as e:
            logger.error(f"Error in DAU_DUOI method calculation: {e}")
            return []
