# predictions_tracker/methods_btl/base.py
import logging
from abc import ABC, abstractmethod
from typing import Any, Dict, List
from venv import logger
from .utils import get_ball_number
logger = logging.getLogger(__name__)


class BasePredictionMethod(ABC):
    @abstractmethod
    def get_code(self) -> str:
        pass

    @abstractmethod
    def get_name(self) -> str:
        pass

    @abstractmethod
    def get_description(self) -> str:
        pass

    @abstractmethod
    def calculate(self, data: Any) -> Dict[str, List[str]]:
        pass

    def get_parameters(self) -> Dict[str, Any]:
        """Override để cung cấp parameters đặc biệt"""
        return {}

    def get_category(self) -> str:
        """Override để chỉ định category cụ thể"""
        return "other"


class BaseMakeResult:
    def _make_result(
        self, data: Dict[str, Any], keys1: List[tuple], keys2: List[tuple], reverse: bool = False
    ) -> Dict[str, List[str]]:
        """
        Tính toán kết quả từ 2 nhóm keys
        
        Args:
            data: Dict chứa dữ liệu kết quả xổ số
            keys1: List[tuple] - Nhóm keys thứ nhất, format: (key, index) hoặc (key, index, 'ball')
            keys2: List[tuple] - Nhóm keys thứ hai, format: (key, index) hoặc (key, index, 'ball')
            reverse: bool - Có tạo số đảo ngược hay không
            
        Returns:
            Dict[str, List[str]]: {
                "two_digits_loto": List[str] - Danh sách số 2 chữ số
            }
        """
        try:
            # ✅ SỬA: Tính digit1 từ keys1 - LUÔN TÍNH TỔNG với hỗ trợ ball
            digit1_sum = 0
            for key_tuple in keys1:
                key, idx = key_tuple[0], key_tuple[1]
                use_ball = len(key_tuple) > 2 and key_tuple[2] == 'ball'
                
                val = data.get(key, "")
                if idx >= len(val):
                    logger.warning(
                        f"[BaseMakeResult] Dữ liệu không đủ cho {key} tại index {idx}"
                    )
                    return {"two_digits_loto": []}
                
                digit = int(val[idx])
                if use_ball:
                    digit = get_ball_number(digit)
                    
                digit1_sum += digit
                
            digit1 = digit1_sum % 10
            
            # ✅ SỬA: Tính digit2 từ keys2 - LUÔN TÍNH TỔNG với hỗ trợ ball
            digit2_sum = 0
            for key_tuple in keys2:
                key, idx = key_tuple[0], key_tuple[1]
                use_ball = len(key_tuple) > 2 and key_tuple[2] == 'ball'
                
                val = data.get(key, "")
                if idx >= len(val):
                    logger.warning(
                        f"[BaseMakeResult] Dữ liệu không đủ cho {key} tại index {idx}"
                    )
                    return {"two_digits_loto": []}
                
                digit = int(val[idx])
                if use_ball:
                    digit = get_ball_number(digit)
                    
                digit2_sum += digit
                
            digit2 = digit2_sum % 10
            
            # Tạo số 2 chữ số
            results = [f"{digit1}{digit2}".zfill(2)]  # Đảm bảo 2 chữ số
            if reverse:
                results.append(f"{digit2}{digit1}".zfill(2))
            
            logger.info(f"[BaseMakeResult] Keys1 sum: {digit1_sum} -> digit1: {digit1}")
            logger.info(f"[BaseMakeResult] Keys2 sum: {digit2_sum} -> digit2: {digit2}")
            logger.info(f"[BaseMakeResult] Kết quả: {results}")
            
            return {"two_digits_loto": results}

        except (ValueError, IndexError, TypeError) as e:
            logger.error(f"[BaseMakeResult] Lỗi khi tính toán: {str(e)}")
            return {"two_digits_loto": []}
        except Exception as e:
            logger.error(f"[BaseMakeResult] Lỗi không xác định: {str(e)}")
            return {"two_digits_loto": []}      
