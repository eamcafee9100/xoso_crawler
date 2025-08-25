# predictions_tracker/methods_btl/base.py
import logging
from abc import ABC, abstractmethod
from typing import Any, Dict, List
from venv import logger

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
            keys1: List[tuple] - Nhóm keys thứ nhất, format: (key, index)
            keys2: List[tuple] - Nhóm keys thứ hai, format: (key, index)
            
        Returns:
            Dict[str, List[str]]: {
                "two_digits_loto": List[str] - Danh sách số 2 chữ số
            }
        """
        try:
            # Tính digit1 từ keys1
            if len(keys1) == 1:
                # Nếu chỉ có 1 phần tử, lấy trực tiếp chữ số
                key, idx = keys1[0]
                val = data.get(key, "")
                if idx >= len(val):
                    logger.warning(
                        f"[BaseMakeResult] Dữ liệu không đủ cho {key} tại index {idx}"
                    )
                    return {"two_digits_loto": []}
                digit1 = int(val[idx])
            else:
                # Nếu có nhiều phần tử, tính tổng
                digit1_sum = 0
                for key, idx in keys1:
                    val = data.get(key, "")
                    if idx >= len(val):
                        logger.warning(
                            f"[BaseMakeResult] Dữ liệu không đủ cho {key} tại index {idx}"
                        )
                        return {"two_digits_loto": []}
                    digit1_sum += int(val[idx])
                digit1 = digit1_sum % 10

            # Tính digit2 từ keys2
            if len(keys2) == 1:
                # Nếu chỉ có 1 phần tử, lấy trực tiếp chữ số
                key, idx = keys2[0]
                val = data.get(key, "")
                if idx >= len(val):
                    logger.warning(
                        f"[BaseMakeResult] Dữ liệu không đủ cho {key} tại index {idx}"
                    )
                    return {"two_digits_loto": []}
                digit2 = int(val[idx])
            else:
                # Nếu có nhiều phần tử, tính tổng
                digit2_sum = 0
                for key, idx in keys2:
                    val = data.get(key, "")
                    if idx >= len(val):
                        logger.warning(
                            f"[BaseMakeResult] Dữ liệu không đủ cho {key} tại index {idx}"
                        )
                        return {"two_digits_loto": []}
                    digit2_sum += int(val[idx])
                digit2 = digit2_sum % 10

            # Tạo số 2 chữ số
            results = [f"{digit1}{digit2}".zfill(2)]  # Đảm bảo 2 chữ số
            if reverse:
                results.append(f"{digit2}{digit1}".zfill(2))
            logger.info(f"[BaseMakeResult] Kết quả: {results}")
            
            return {"two_digits_loto": results}

        except (ValueError, IndexError, TypeError) as e:
            logger.error(f"[BaseMakeResult] Lỗi khi tính toán: {str(e)}")
            return {"two_digits_loto": []}
        except Exception as e:
            logger.error(f"[BaseMakeResult] Lỗi không xác định: {str(e)}")
            return {"two_digits_loto": []}