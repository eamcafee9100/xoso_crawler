from django.core.cache import cache
from django.utils import timezone
from datetime import datetime, timedelta
import json
import logging
import pickle
import io
import redis
from results.models import (
    PredictionPerformanceMetrics, MethodWeightsHistory, 
    NumberFrequencyStats, KetQuaXoSo
)

logger = logging.getLogger(__name__)

class PredictionCacheService:
    """
    Service để quản lý cache dự đoán và kết quả
    """
    
    def __init__(self):
        self.cache_duration = {
            'daily_predictions': 60 * 60 * 24,  # 24 hours
            'weekly_analysis': 60 * 60 * 24 * 7,  # 7 days
            'monthly_stats': 60 * 60 * 24 * 30,  # 30 days
        }
        self.redis_client = redis.Redis()
        self.cache_ttl = {
            'predictions': 3600,      # 1 giờ
            'models': 86400,         # 1 ngày
            'performance': 7200      # 2 giờ
        }
            
    def _sanitize_data_for_cache(self, data):
        """
        Sanitize dữ liệu trước khi cache, loại bỏ objects không thể pickle
        """
        if data is None:
            return None
            
        try:
            # Nếu không phải dict, thử convert hoặc return as is
            if not isinstance(data, dict):
                # Test pickle
                pickle.dumps(data)
                return data
                
            sanitized_data = {}
            
            for key, value in data.items():
                try:
                    # Skip các object không thể pickle
                    if hasattr(value, 'read') or hasattr(value, 'write'):
                        # File-like objects
                        logger.warning(f"Skipping file-like object: {key}")
                        continue
                        
                    if isinstance(value, (io.IOBase, io.BufferedReader, io.TextIOWrapper)):
                        # IO objects
                        logger.warning(f"Skipping IO object: {key}")
                        continue
                        
                    # Test pickle cho value
                    pickle.dumps(value)
                    sanitized_data[key] = value
                    
                except (TypeError, AttributeError, pickle.PicklingError) as e:
                    logger.warning(f"Cannot pickle key '{key}': {e}")
                    
                    # Nếu là dict, thử sanitize recursively
                    if isinstance(value, dict):
                        sanitized_value = self._sanitize_data_for_cache(value)
                        if sanitized_value:
                            sanitized_data[key] = sanitized_value
                    # Nếu là list, thử sanitize từng item
                    elif isinstance(value, list):
                        sanitized_list = []
                        for item in value:
                            try:
                                pickle.dumps(item)
                                sanitized_list.append(item)
                            except:
                                # Skip item không pickle được
                                continue
                        if sanitized_list:
                            sanitized_data[key] = sanitized_list
                    # Với các kiểu khác, thử convert sang string
                    else:
                        try:
                            sanitized_data[key] = str(value)
                        except:
                            logger.warning(f"Cannot convert to string: {key}")
                            continue
                            
            return sanitized_data
            
        except Exception as e:
            logger.error(f"Error sanitizing data for cache: {e}")
            return {}
    def get_cached_prediction(self, date, analysis_type='combined'):
        """
        Lấy dự đoán đã cache
        """
        try:
            cache_key = f"prediction_{analysis_type}_{date.strftime('%Y%m%d')}"
            cached_data = cache.get(cache_key)
            
            if cached_data:
                logger.info(f"Retrieved cached prediction for {date}")
                return cached_data
                
            return None
            
        except Exception as e:
            logger.error(f"Error getting cached prediction: {e}")
            return None

    def cache_prediction(self, date, analysis_type, data):
        """
        Cache dự đoán với data sanitization
        """
        try:
            cache_key = f"prediction_{analysis_type}_{date.strftime('%Y%m%d')}"
            
            # Sanitize data trước khi cache
            sanitized_data = self._sanitize_data_for_cache(data)
            
            if not sanitized_data:
                logger.warning(f"No data left after sanitization for {date}")
                return False
            
            # Thêm metadata
            cached_data = {
                'data': sanitized_data,
                'cached_at': datetime.now().isoformat(),
                'cache_key': cache_key,
                'original_keys_count': len(data) if isinstance(data, dict) else 0,
                'sanitized_keys_count': len(sanitized_data) if isinstance(sanitized_data, dict) else 0
            }
            
            # Test pickle trước khi cache
            try:
                pickle.dumps(cached_data)
            except Exception as pickle_error:
                logger.error(f"Data still not picklable after sanitization: {pickle_error}")
                return False
            
            cache.set(
                cache_key, 
                cached_data, 
                self.cache_duration['daily_predictions']
            )
            
            logger.info(f"Successfully cached prediction for {date} (sanitized: {cached_data.get('sanitized_keys_count', 0)}/{cached_data.get('original_keys_count', 0)} keys)")
            return True
            
        except Exception as e:
            logger.error(f"Error caching prediction: {e}")
            return False
        
    def invalidate_cache_for_date(self, date):
        """
        Xóa cache cho một ngày cụ thể khi có kết quả thực tế
        """
        try:
            # Xóa tất cả các loại cache cho ngày này
            analysis_types = ['combined', 'shap', 'ml', 'statistical']
            
            for analysis_type in analysis_types:
                cache_key = f"prediction_{analysis_type}_{date.strftime('%Y%m%d')}"
                cache.delete(cache_key)
                
            logger.info(f"Invalidated cache for {date}")
            return True
            
        except Exception as e:
            logger.error(f"Error invalidating cache: {e}")
            return False
    
    def should_show_prediction_results(self, target_date):
        """
        Kiểm tra xem có nên hiển thị kết quả dự đoán hay không
        Không hiển thị nếu đã có kết quả thực tế
        """
        try:
            # Kiểm tra xem đã có kết quả xổ số cho ngày này chưa
            actual_result = KetQuaXoSo.objects.filter(ngay=target_date).first()
            
            if actual_result:
                logger.info(f"Actual results exist for {target_date}, hiding predictions")
                return False
                
            # Chỉ hiển thị dự đoán cho ngày trong tương lai hoặc hôm nay
            today = timezone.now().date()
            if target_date < today:
                return False
                
            return True
            
        except Exception as e:
            logger.error(f"Error checking if should show predictions: {e}")
            return True  # Default to showing predictions
        
    def get_cache_info(self, date, analysis_type='combined'):
        """
        Lấy thông tin về cache (debug purpose)
        """
        try:
            cache_key = f"prediction_{analysis_type}_{date.strftime('%Y%m%d')}"
            cached_data = cache.get(cache_key)
            
            if cached_data:
                return {
                    'exists': True,
                    'cached_at': cached_data.get('cached_at'),
                    'original_keys_count': cached_data.get('original_keys_count', 0),
                    'sanitized_keys_count': cached_data.get('sanitized_keys_count', 0),
                    'cache_key': cache_key
                }
            else:
                return {
                    'exists': False,
                    'cache_key': cache_key
                }
                
        except Exception as e:
            logger.error(f"Error getting cache info: {e}")
            return {'exists': False, 'error': str(e)}