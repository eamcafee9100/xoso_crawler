from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional
import logging

logger = logging.getLogger(__name__)

class BasePredictionMethod(ABC):
    """
    Lớp cơ sở cho tất cả các phương pháp dự đoán
    """
    
    @abstractmethod
    def get_code(self) -> str:
        """Trả về mã định danh duy nhất của phương pháp"""
        pass
    
    @abstractmethod
    def get_name(self) -> str:
        """Trả về tên của phương pháp"""
        pass
    
    @abstractmethod
    def get_description(self) -> str:
        """Trả về mô tả của phương pháp"""
        pass
    
    @abstractmethod
    def calculate(self, data: Dict[str, Any]) -> Dict[str, List[str]]:
        """
        Tính toán các số dự đoán dựa trên dữ liệu đầu vào
        
        Args:
            data: Dictionary chứa dữ liệu các giải thưởng
            
        Returns:
            Dictionary chứa các tập hợp số dự đoán theo loại
        """
        pass
    
    def log_error(self, message: str):
        """
        Ghi log lỗi
        """
        logger.error(f"[{self.get_code()}] {message}")

class BaseMakeResult:
    def _make_result(self, data: Dict[str, Any], keys1: List[tuple], keys2: List[tuple]) -> Dict[str, List[str]]:
        try:
            # Tính tổng số thứ 1
            digit1_sum = 0
            for key, idx in keys1:
                val = data.get(key, '')
                if not val or idx >= len(str(val)):
                    logger.warning(f"[{self.get_code()}] Dữ liệu không đủ cho {key} tại index {idx}")
                    return {'two_digits_loto': []}
                digit1_sum += int(str(val)[idx])
            digit1 = str(digit1_sum % 10)

            # Tính tổng số thứ 2
            digit2_sum = 0
            for key, idx in keys2:
                val = data.get(key, '')
                if not val or idx >= len(str(val)):
                    logger.warning(f"[{self.get_code()}] Dữ liệu không đủ cho {key} tại index {idx}")
                    return {'two_digits_loto': []}
                digit2_sum += int(str(val)[idx])
            digit2 = str(digit2_sum % 10)

            # Tạo các cặp số 2 chữ số
            results = {f"{digit1}{digit2}"}

            logger.info(f"[{self.get_code()}] Kết quả: {sorted(results)}")
            return {'two_digits_loto': sorted(results)}

        except Exception as e:
            logger.error(f"[{self.get_code()}] Lỗi khi tính toán: {str(e)}")
            return {'two_digits_loto': []}