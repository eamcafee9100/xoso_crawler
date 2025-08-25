# lokhung/methods/base.py
from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional
import logging

logger = logging.getLogger(__name__)

class BasePredictionMethod(ABC):
    """
    Lớp cơ sở cho tất cả các phương pháp dự đoán
    """
    def __init__(self):
        from results.models import PredictionMethodBtl
        # Đảm bảo phương pháp đã được đăng ký trong database
        self.prediction_method, _ = PredictionMethodBtl.objects.get_or_create(
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
    
    def create_prediction(self, dan_btl, input_data, next_day_result=None):
        """
        Tạo kết quả dự đoán cho dàn đề và lưu vào database
        
        Args:
            dan_de: Đối tượng DanDeDacBiet 
            input_data: Dữ liệu đầu vào từ kết quả xổ số
            next_day_result: Kết quả ngày tiếp theo để kiểm tra số trúng
        """
        from results.models import PredictionResultBtl
        
        try:
            # Xóa các kết quả dự đoán cũ của phương pháp này (nếu có)
            PredictionResultBtl.objects.filter(
                dan_btl=dan_btl,
                method=self.prediction_method
            ).delete()
            
            # Tính toán các số dự đoán
            prediction_data = self.calculate(input_data)
            
            # Xử lý từng loại dự đoán
            for prediction_type, numbers in prediction_data.items():
                                
                # Tìm các số trúng
                winning_numbers = []
                if next_day_result:
                    all_2digit = next_day_result.get_all_2digit_numbers()
                    # So sánh với tất cả các số 2 chữ số
                    winning_numbers = [num for num in numbers if num in all_2digit]
                    
                
                # Lưu kết quả
                PredictionResultBtl.objects.update_or_create(
                    dan_btl=dan_btl,
                    method=self.prediction_method,
                    is_special_prize=False,
                    defaults={
                        'predicted_numbers': numbers,
                        'winning_numbers': winning_numbers,
                        'hit_count': len(winning_numbers)
                    }
                )
                
        except Exception as e:
            logger.error(f"Lỗi khi tạo dự đoán từ phương pháp {self.get_name()}: {str(e)}", exc_info=True)

class BaseMakeResult:
    def _make_result(self, data: Dict[str, Any], keys1: List[tuple], keys2: List[tuple]) -> Dict[str, List[str]]:
        try:
            # Tính tổng số thứ 1
            digit1_sum = 0
            for key, idx in keys1:
                val = data.get(key, '')
                if idx >= len(val):
                    logger.warning(f"[BaseMakeResult] Dữ liệu không đủ cho {key} tại index {idx}")
                    return {'two_digits_loto': []}
                digit1_sum += int(val[idx])
            digit1 = str(digit1_sum % 10)

            # Tính tổng số thứ 2
            digit2_sum = 0
            for key, idx in keys2:
                val = data.get(key, '')
                if idx >= len(val):
                    logger.warning(f"[BaseMakeResult] Dữ liệu không đủ cho {key} tại index {idx}")
                    return {'two_digits_loto': []}
                digit2_sum += int(val[idx])
            digit2 = str(digit2_sum % 10)

            # Tạo các cặp số 2 chữ số
            results = {f"{digit1}{digit2}"}
            # if digit1 != digit2:
            #     results.add(f"{digit2}{digit1}")

            logger.info(f"[BaseMakeResult] Kết quả: {sorted(results)}")
            return {'two_digits_loto': sorted(results)}

        except Exception as e:
            logger.error(f"[BaseMakeResult] Lỗi khi tính toán: {str(e)}")
            return {'two_digits_loto': []}

