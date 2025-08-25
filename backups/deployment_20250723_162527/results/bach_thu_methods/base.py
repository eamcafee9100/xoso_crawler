from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional, Tuple
import logging

logger = logging.getLogger(__name__)

class BaseBachThuMethod(ABC):
    """
    Lớp cơ sở cho tất cả các phương pháp dự đoán bạch thủ lô
    """
    
    def __init__(self):
        from results.models import BachThuLoMethod
        # Đảm bảo phương pháp đã được đăng ký trong database
        self.bach_thu_method, _ = BachThuLoMethod.objects.get_or_create(
            code=self.get_code(),
            defaults={
                'name': self.get_name(),
                'description': self.get_description(),
                # 'method_type': self.get_method_type(),
                'is_active': True
            }
        )
    
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
    def get_default_confidence_level(self) -> int:
        """Trả về mức độ tin cậy mặc định (1-5)"""
        pass
    
    @abstractmethod
    def calculate(self, data: Dict[str, Any]) -> List[str]:
        """
        Tính toán các số bạch thủ lô dựa trên dữ liệu đầu vào
        
        Args:
            data: Dictionary chứa dữ liệu các giải thưởng và thông tin phụ trợ
            
        Returns:
            List các số bạch thủ lô (2 chữ số)
        """
        pass
    
    def validate_input(self, data: Dict[str, Any]) -> bool:
        """
        Kiểm tra tính hợp lệ của dữ liệu đầu vào
        
        Args:
            data: Dictionary chứa dữ liệu đầu vào
            
        Returns:
            True nếu dữ liệu hợp lệ, False nếu không
        """
        try:
            required_fields = self.get_required_fields()
            for field in required_fields:
                if field not in data:
                    logger.warning(f"Missing required field: {field}")
                    return False
            return True
        except Exception as e:
            logger.error(f"Error validating input: {e}")
            return False
    
    @abstractmethod
    def get_required_fields(self) -> List[str]:
        """Trả về danh sách các trường dữ liệu bắt buộc"""
        pass
    
    def extract_two_digit_numbers(self, number_str: str) -> List[str]:
        """
        Trích xuất các số 2 chữ số từ chuỗi số
        
        Args:
            number_str: Chuỗi số cần trích xuất
            
        Returns:
            List các số 2 chữ số
        """
        if not number_str or len(number_str) < 2:
            return []
        
        # Loại bỏ ký tự không phải số
        clean_str = ''.join(filter(str.isdigit, str(number_str)))
        
        # Trích xuất các số 2 chữ số
        two_digit_numbers = []
        for i in range(len(clean_str) - 1):
            two_digit = clean_str[i:i+2]
            if len(two_digit) == 2:
                two_digit_numbers.append(two_digit)
        
        # Lấy 2 chữ số cuối
        if len(clean_str) >= 2:
            last_two = clean_str[-2:]
            if last_two not in two_digit_numbers:
                two_digit_numbers.append(last_two)
        
        return list(set(two_digit_numbers))  # Loại bỏ trùng lặp
    
    def calculate_sum_digits(self, number: str) -> str:
        """
        Tính tổng các chữ số và trả về 2 chữ số cuối
        
        Args:
            number: Số cần tính tổng
            
        Returns:
            2 chữ số cuối của tổng
        """
        try:
            clean_number = ''.join(filter(str.isdigit, str(number)))
            if not clean_number:
                return "00"
            
            digit_sum = sum(int(digit) for digit in clean_number)
            return str(digit_sum)[-2:].zfill(2)
        except Exception:
            return "00"
