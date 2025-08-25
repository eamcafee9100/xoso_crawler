import logging
import re
from datetime import datetime, date, timedelta
from typing import Dict, List, Any, Optional, Union
from django.core.exceptions import ValidationError as DjangoValidationError

logger = logging.getLogger(__name__)

class ValidationService:
    """
    Service để validation toàn diện cho dự đoán xổ số
    
    Returns:
        Tất cả methods trả về kiểu dữ liệu rõ ràng:
        - validate_predictions_strict: bool (raise exception nếu invalid)
        - normalize_predictions_format: Dict[str, float]
        - validate_historical_data: bool (raise exception nếu invalid)
        - validate_number_format: bool
    """
    
    def __init__(self):
        self.number_pattern = re.compile(r'^\d{2}$')
        self.valid_confidence_range = (0.0, 1.0)
        self.max_predictions = 100  # Maximum predictions per request
        
    def validate_predictions_strict(self, predictions: Any, source: str = "unknown") -> bool:
        """
        Validate nghiêm ngặt format predictions
        
        Args:
            predictions: Predictions cần validate
            source: Nguồn dữ liệu để logging
            
        Returns:
            bool: True nếu valid
            
        Raises:
            ValueError: Nếu predictions không hợp lệ
        """
        try:
            # Check type
            if not isinstance(predictions, dict):
                raise ValueError(f"Predictions từ {source} phải là dict, nhận {type(predictions)}")
            
            # Check empty
            if len(predictions) == 0:
                raise ValueError(f"Predictions từ {source} rỗng")
            
            # Check size limit
            if len(predictions) > self.max_predictions:
                raise ValueError(f"Quá nhiều predictions: {len(predictions)} > {self.max_predictions}")
            
            # Validate each prediction
            for number, confidence in predictions.items():
                # Validate number format
                if not self.validate_number_format(number):
                    raise ValueError(f"Number không hợp lệ: '{number}' (phải là string 2 chữ số)")
                
                # Validate confidence
                if not isinstance(confidence, (int, float)):
                    raise ValueError(f"Confidence cho {number} phải là số, nhận {type(confidence)}")
                
                if not (self.valid_confidence_range[0] <= confidence <= self.valid_confidence_range[1]):
                    raise ValueError(f"Confidence cho {number} ngoài phạm vi {self.valid_confidence_range}: {confidence}")
            
            logger.info(f"✅ Validated {len(predictions)} predictions từ {source}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Validation failed cho {source}: {e}")
            raise ValueError(f"Validation predictions từ {source} thất bại: {e}")
    
    def normalize_predictions_format(self, predictions: Dict[Any, Any]) -> Dict[str, float]:
        """
        Normalize predictions về format chuẩn
        
        Args:
            predictions: Raw predictions
            
        Returns:
            Dict[str, float]: Normalized predictions với format:
            {
                "00": 0.85,
                "01": 0.72,
                ...
            }
        """
        try:
            normalized = {}
            
            for number, confidence in predictions.items():
                # Normalize number to 2-digit string
                normalized_number = self.normalize_number_format(number)
                if not normalized_number:
                    logger.warning(f"Skipping invalid number: {number}")
                    continue
                
                # Normalize confidence to float
                try:
                    normalized_confidence = float(confidence)
                    # Clamp to valid range
                    normalized_confidence = max(self.valid_confidence_range[0], 
                                              min(self.valid_confidence_range[1], normalized_confidence))
                    normalized[normalized_number] = normalized_confidence
                except (ValueError, TypeError):
                    logger.warning(f"Skipping invalid confidence for {number}: {confidence}")
                    continue
            
            # Sort by confidence descending
            sorted_predictions = dict(sorted(normalized.items(), 
                                           key=lambda x: x[1], 
                                           reverse=True))
            
            logger.info(f"✅ Normalized {len(sorted_predictions)} predictions")
            return sorted_predictions
            
        except Exception as e:
            logger.error(f"❌ Normalization failed: {e}")
            return {}
    
    def validate_historical_data(self, historical_data: List[Any]) -> bool:
        """
        Validate historical data integrity
        
        Args:
            historical_data: List of KetQuaXoSo objects
            
        Returns:
            bool: True nếu valid
            
        Raises:
            ValueError: Nếu data không hợp lệ
        """
        try:
            if not isinstance(historical_data, list):
                raise ValueError(f"Historical data phải là list, nhận {type(historical_data)}")
            
            if len(historical_data) == 0:
                raise ValueError("Historical data rỗng")
            
            # Check data completeness
            valid_records = 0
            date_set = set()
            
            for i, record in enumerate(historical_data):
                # Check required method exists
                if not hasattr(record, 'get_all_2digit_numbers'):
                    raise ValueError(f"Record {i} thiếu method get_all_2digit_numbers")
                
                if not hasattr(record, 'ngay'):
                    raise ValueError(f"Record {i} thiếu field ngay")
                
                # Check date uniqueness
                if record.ngay in date_set:
                    logger.warning(f"Duplicate date found: {record.ngay}")
                else:
                    date_set.add(record.ngay)
                
                # Check data completeness
                try:
                    numbers = record.get_all_2digit_numbers()
                    if len(numbers) >= 10:  # Minimum expected numbers
                        valid_records += 1
                except Exception as e:
                    logger.warning(f"Record {i} ({record.ngay}) có lỗi: {e}")
            
            # Calculate completeness ratio
            completeness_ratio = valid_records / len(historical_data)
            
            if completeness_ratio < 0.7:  # Require at least 70% valid records
                raise ValueError(f"Dữ liệu lịch sử có chất lượng thấp: {completeness_ratio:.1%} records hợp lệ")
            
            # Check date continuity
            self._validate_date_continuity(historical_data)
            
            logger.info(f"✅ Validated {len(historical_data)} historical records ({completeness_ratio:.1%} valid)")
            return True
            
        except Exception as e:
            logger.error(f"❌ Historical data validation failed: {e}")
            raise ValueError(f"Validation dữ liệu lịch sử thất bại: {e}")
    
    def validate_number_format(self, number: Any) -> bool:
        """
        Validate number format (must be 2-digit string)
        
        Args:
            number: Number to validate
            
        Returns:
            bool: True if valid format
        """
        return (isinstance(number, str) and 
                len(number) == 2 and 
                self.number_pattern.match(number) is not None)
    
    def normalize_number_format(self, number: Any) -> Optional[str]:
        """
        Normalize number to 2-digit string format
        
        Args:
            number: Number in any format
            
        Returns:
            Optional[str]: Normalized number or None if invalid
        """
        try:
            if isinstance(number, str):
                # Remove whitespace
                clean_number = number.strip()
                
                # Check if already 2-digit
                if self.validate_number_format(clean_number):
                    return clean_number
                
                # Try to convert if numeric string
                if clean_number.isdigit():
                    num_int = int(clean_number)
                    if 0 <= num_int <= 99:
                        return f"{num_int:02d}"
            
            elif isinstance(number, (int, float)):
                num_int = int(number)
                if 0 <= num_int <= 99:
                    return f"{num_int:02d}"
            
            return None
            
        except Exception:
            return None
    
    def validate_date_range(self, start_date: date, end_date: date, 
                          max_days: int = 365) -> bool:
        """
        Validate date range for analysis
        
        Args:
            start_date: Start date
            end_date: End date  
            max_days: Maximum allowed days
            
        Returns:
            bool: True if valid
            
        Raises:
            ValueError: If date range invalid
        """
        try:
            if start_date >= end_date:
                raise ValueError("Start date phải trước end date")
            
            if end_date > date.today():
                raise ValueError("End date không thể trong tương lai")
            
            days_diff = (end_date - start_date).days
            if days_diff > max_days:
                raise ValueError(f"Khoảng thời gian quá dài: {days_diff} > {max_days} ngày")
            
            return True
            
        except Exception as e:
            logger.error(f"Date range validation failed: {e}")
            raise
    
    def _validate_date_continuity(self, historical_data: List[Any]) -> bool:
        """
        Validate date continuity in historical data
        
        Args:
            historical_data: Historical records
            
        Returns:
            bool: True if acceptable continuity
        """
        try:
            if len(historical_data) < 2:
                return True
            
            dates = [record.ngay for record in historical_data if hasattr(record, 'ngay')]
            dates.sort()
            
            gaps = []
            for i in range(1, len(dates)):
                gap = (dates[i] - dates[i-1]).days
                if gap > 1:
                    gaps.append(gap)
            
            # Allow some gaps but not too many
            if len(gaps) > len(dates) * 0.2:  # More than 20% gaps
                logger.warning(f"Nhiều khoảng trống trong dữ liệu: {len(gaps)} gaps")
            
            # Check for very large gaps
            large_gaps = [g for g in gaps if g > 7]  # More than 1 week
            if large_gaps:
                logger.warning(f"Có khoảng trống lớn: {large_gaps}")
            
            return True
            
        except Exception as e:
            logger.warning(f"Date continuity check failed: {e}")
            return True  # Don't fail validation for this
    
    def validate_confidence_distribution(self, predictions: Dict[str, float]) -> dict:
        """
        Validate confidence distribution and provide insights
        
        Args:
            predictions: Predictions với confidence scores
            
        Returns:
            dict: {
                "is_valid": bool,
                "distribution_type": str,
                "confidence_stats": dict,
                "warnings": list
            }
        """
        try:
            confidences = list(predictions.values())
            
            if not confidences:
                return {
                    "is_valid": False,
                    "distribution_type": "empty",
                    "confidence_stats": {},
                    "warnings": ["No predictions provided"]
                }
            
            # Calculate statistics
            stats = {
                "mean": sum(confidences) / len(confidences),
                "min": min(confidences),
                "max": max(confidences),
                "std": self._calculate_std(confidences),
                "count": len(confidences)
            }
            
            warnings = []
            
            # Check for reasonable distribution
            if stats["max"] - stats["min"] < 0.1:
                warnings.append("Confidence scores quá đồng đều")
                distribution_type = "uniform"
            elif stats["std"] > 0.3:
                warnings.append("Confidence scores có độ biến động cao")
                distribution_type = "high_variance"
            else:
                distribution_type = "normal"
            
            # Check for extreme values
            if stats["max"] < 0.2:
                warnings.append("Tất cả confidence scores quá thấp")
            elif stats["min"] > 0.8:
                warnings.append("Tất cả confidence scores quá cao")
            
            is_valid = len(warnings) < 2  # Allow some warnings but not too many
            
            return {
                "is_valid": is_valid,
                "distribution_type": distribution_type,
                "confidence_stats": stats,
                "warnings": warnings
            }
            
        except Exception as e:
            logger.error(f"Confidence distribution validation failed: {e}")
            return {
                "is_valid": False,
                "distribution_type": "error",
                "confidence_stats": {},
                "warnings": [f"Validation error: {e}"]
            }
    
    def _calculate_std(self, values: List[float]) -> float:
        """Calculate standard deviation"""
        if len(values) < 2:
            return 0.0
        
        mean = sum(values) / len(values)
        variance = sum((x - mean) ** 2 for x in values) / (len(values) - 1)
        return variance ** 0.5