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
        from results.models import PredictionMethod
        # Đảm bảo phương pháp đã được đăng ký trong database
        self.prediction_method, _ = PredictionMethod.objects.get_or_create(
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
        from results.models import PredictionResult
        
        try:
            # Xóa các kết quả dự đoán cũ của phương pháp này (nếu có)
            PredictionResult.objects.filter(
                dan_de=dan_de,
                method=self.prediction_method
            ).delete()
            
            # Tính toán các số dự đoán
            prediction_data = self.calculate(input_data)
            
            # Xử lý từng loại dự đoán
            for prediction_type, numbers in prediction_data.items():
                # Xác định loại dự đoán
                is_special = "special" in prediction_type
                is_three_digit = "three" in prediction_type or "3" in prediction_type
                digit_count = 3 if is_three_digit else 2
                
                # Tìm các số trúng
                winning_numbers = []
                if next_day_result:
                    if digit_count == 2:
                        last2_special = next_day_result.giai_db[-2:] if next_day_result.giai_db else ""
                        all_2digit = next_day_result.get_all_2digit_numbers()
                        
                        if is_special:
                            # Chỉ so sánh với 2 số cuối của giải đặc biệt
                            winning_numbers = [num for num in numbers if num == last2_special]
                        else:
                            # So sánh với tất cả các số 2 chữ số
                            winning_numbers = [num for num in numbers if num in all_2digit]
                    else:  # 3 chữ số
                        if is_special:
                            # Chỉ so sánh với 3 số cuối của giải đặc biệt
                            last3_special = next_day_result.giai_db[-3:] if len(next_day_result.giai_db) >= 3 else ""
                            winning_numbers = [num for num in numbers if num == last3_special]
                        else:
                            # So sánh với tất cả các số 3 chữ số
                            all_3digit = next_day_result.get_all_three_digit_numbers() or []
                            winning_numbers = [num for num in numbers if num in all_3digit]
                
                # Lưu kết quả
                PredictionResult.objects.update_or_create(
                    dan_de=dan_de,
                    method=self.prediction_method,
                    digit_count=digit_count,
                    is_special_prize=is_special,
                    defaults={
                        'predicted_numbers': numbers,
                        'winning_numbers': winning_numbers,
                        'hit_count': len(winning_numbers)
                    }
                )
                
        except Exception as e:
            logger.error(f"Lỗi khi tạo dự đoán từ phương pháp {self.get_name()}: {str(e)}", exc_info=True)