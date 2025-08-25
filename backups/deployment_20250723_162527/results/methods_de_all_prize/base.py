# results/methods/base.py
from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional
import logging

logger = logging.getLogger(__name__)

class BasePredictionMethod(ABC):
    """
    Lớp cơ sở cho tất cả các phương pháp dự đoán
    """
    def __init__(self):
        from results.models import PredictionMethodAllPrize
        # Đảm bảo phương pháp đã được đăng ký trong database
        self.prediction_method, _ = PredictionMethodAllPrize.objects.get_or_create(
            code=self.get_code(),
            defaults={
                'name': self.get_name(),
                'description': self.get_description(),
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
    
    def create_prediction(self, dan_de, input_data, next_day_result=None):
        """
        Tạo kết quả dự đoán cho dàn đề và lưu vào database
        
        Args:
            dan_de: Đối tượng DanDeDacBiet 
            input_data: Dữ liệu đầu vào từ kết quả xổ số
            next_day_result: Kết quả ngày tiếp theo để kiểm tra số trúng
        """
        from results.models import PredictionDeAllPrizeResult
        
        try:
            # Xóa các kết quả dự đoán cũ của phương pháp này (nếu có)
            PredictionDeAllPrizeResult.objects.filter(
                dan_de=dan_de,
                method=self.prediction_method
            ).delete()
            
            # Tính toán các số dự đoán
            prediction_data = self.calculate(input_data)
            
            # Xử lý từng loại dự đoán
            for prediction_type, numbers in prediction_data.items():
                # Xác định loại dự đoán
                
                is_three_digit = "three" in prediction_type or "3" in prediction_type
                digit_count = 3 if is_three_digit else 2
                
                # Tìm các số trúng
                winning_numbers = []
                if next_day_result:
                    if digit_count == 2:
                        # last2_special = next_day_result.giai_db[-2:] if next_day_result.giai_db else ""
                        all_2digit = next_day_result.get_all_2digit_numbers()
                        winning_numbers = [num for num in numbers if num in all_2digit]
                    else:  # 3 chữ số
                        # Lấy tất cả các số 3 chữ số từ tất cả các giải
                        all_3digit = next_day_result.get_all_three_digit_numbers() or []
                        winning_numbers = [num for num in numbers if num in all_3digit]
                
                # Lưu kết quả
                PredictionDeAllPrizeResult.objects.update_or_create(
                    dan_de=dan_de,
                    method=self.prediction_method,
                    digit_count=digit_count,
                    is_special_prize=False,
                    defaults={
                        'predicted_numbers': numbers,
                        'winning_numbers': winning_numbers,
                        'hit_count': len(winning_numbers)
                    }
                )
                
        except Exception as e:
            logger.error(f"Lỗi khi tạo dự đoán từ phương pháp {self.get_name()}: {str(e)}", exc_info=True)