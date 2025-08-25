from django.core.cache import cache
from django.utils import timezone
from datetime import datetime, timedelta
import json
import pickle
import os
import logging
from results.models import (
    PredictionPerformanceMetrics, MethodWeightsHistory, 
    NumberFrequencyStats, KetQuaXoSo, DailyPredictionAnalysis
)

logger = logging.getLogger(__name__)

class EnhancedPredictionCacheService:
    """
    Enhanced Cache Service với multi-level caching và intelligent invalidation
    """
    
    def __init__(self):
        self.cache_prefix = 'prediction_cache'
        self.default_timeout = 3600  # 1 hour
        self.cache_duration = {
            'daily_predictions': 60 * 60 * 24,  # 24 hours
            'weekly_analysis': 60 * 60 * 24 * 7,  # 7 days
            'monthly_stats': 60 * 60 * 24 * 30,  # 30 days
            'model_results': 60 * 60 * 6,  # 6 hours for ML results
            'historical_analysis': 60 * 60 * 12,  # 12 hours
        }
        
        # File-based cache cho large objects
        self.file_cache_dir = 'cache/predictions'
        self._ensure_cache_dir()
        
        # Thống kê cache
        self.cache_stats = {
            'hits': 0,
            'misses': 0,
            'invalidations': 0
        }
    
    def _ensure_cache_dir(self):
        """Tạo thư mục cache nếu chưa có"""
        os.makedirs(self.file_cache_dir, exist_ok=True)
    
    def cache_prediction_result(self, date, prediction_type, data, cache_duration=None):
        """
        Lưu kết quả dự đoán vào cache
        """
        try:
            cache_key = self._generate_cache_key(date, prediction_type)
            timeout = cache_duration or self.default_timeout
            
            # Add cache metadata
            data['cached_at'] = timezone.now().isoformat()
            data['cache_key'] = cache_key
            
            cache.set(cache_key, data, timeout)
            logger.info(f"Cached prediction result for {date} with key {cache_key}")
            
        except Exception as e:
            logger.error(f"Error caching prediction result: {e}")


    def get_cached_prediction(self, date, analysis_type='combined', include_metadata=True):
        """
        Lấy dự đoán đã cache với nhiều levels
        """
        if isinstance(date, str):
                    date = datetime.strptime(date, '%Y-%m-%d')
        try:
            # Level 1: Memory cache (Redis/Django cache)
            memory_cache_key = f"pred_mem_{analysis_type}_{date.strftime('%Y%m%d')}"
            cached_data = cache.get(memory_cache_key)
            
            if cached_data:
                self.cache_stats['hits'] += 1
                logger.info(f"Retrieved prediction from memory cache for {date}")
                
                if include_metadata:
                    cached_data['cache_info'] = {
                        'source': 'memory',
                        'retrieved_at': datetime.now().isoformat()
                    }
                
                return cached_data
            
            # Level 2: File cache
            file_cache_path = self._get_file_cache_path(date, analysis_type)
            
            if os.path.exists(file_cache_path):
                try:
                    with open(file_cache_path, 'rb') as f:
                        cached_data = pickle.load(f)
                    
                    # Kiểm tra freshness
                    if self._is_cache_fresh(file_cache_path, analysis_type):
                        self.cache_stats['hits'] += 1
                        logger.info(f"Retrieved prediction from file cache for {date}")
                        
                        # Promote to memory cache
                        cache.set(memory_cache_key, cached_data, self.cache_duration[self._get_cache_type(analysis_type)])
                        
                        if include_metadata:
                            cached_data['cache_info'] = {
                                'source': 'file',
                                'retrieved_at': datetime.now().isoformat(),
                                'promoted_to_memory': True
                            }
                        
                        return cached_data
                    else:
                        # Cache cũ, xóa
                        os.remove(file_cache_path)
                        logger.info(f"Removed stale file cache for {date}")
                        
                except Exception as e:
                    logger.error(f"Error reading file cache: {e}")
            
            # Level 3: Database cache (for completed analyses)
            db_cached = self._get_database_cached_prediction(date, analysis_type)
            if db_cached:
                self.cache_stats['hits'] += 1
                logger.info(f"Retrieved prediction from database for {date}")
                
                # Promote to both memory and file cache
                cache.set(memory_cache_key, db_cached, self.cache_duration[self._get_cache_type(analysis_type)])
                self._save_to_file_cache(date, analysis_type, db_cached)
                
                if include_metadata:
                    db_cached['cache_info'] = {
                        'source': 'database',
                        'retrieved_at': datetime.now().isoformat(),
                        'promoted': True
                    }
                
                return db_cached
            
            # Cache miss
            self.cache_stats['misses'] += 1
            return None
            
        except Exception as e:
            logger.error(f"Error getting cached prediction: {e}")
            self.cache_stats['misses'] += 1
            return None
    
    def cache_prediction(self, date, analysis_type, data, force_all_levels=False):
        """
        Cache dự đoán ở nhiều levels
        """
        if isinstance(date, str):
                    date = datetime.strptime(date, '%Y-%m-%d')
        try:
            # Thêm metadata
            enhanced_data = data.copy() if isinstance(data, dict) else data
            
            if isinstance(enhanced_data, dict):
                enhanced_data.update({
                    'cached_at': datetime.now().isoformat(),
                    'cache_date': date.isoformat() if hasattr(date, 'isoformat') else str(date),
                    'analysis_type': analysis_type,
                    'cache_version': '2.0'
                })
            
            cache_type = self._get_cache_type(analysis_type)
            
            # Level 1: Memory cache
            memory_cache_key = f"pred_mem_{analysis_type}_{date.strftime('%Y%m%d')}"
            cache.set(memory_cache_key, enhanced_data, self.cache_duration[cache_type])
            
            # Level 2: File cache (cho large objects hoặc important data)
            if force_all_levels or self._should_file_cache(analysis_type, data):
                self._save_to_file_cache(date, analysis_type, enhanced_data)
            
            logger.info(f"Cached prediction for {date} ({analysis_type})")
            return True
            
        except Exception as e:
            logger.error(f"Error caching prediction: {e}")
            return False
    
    def _save_to_file_cache(self, date, analysis_type, data):
        """Lưu vào file cache"""
        try:
            file_path = self._get_file_cache_path(date, analysis_type)
            
            with open(file_path, 'wb') as f:
                pickle.dump(data, f, protocol=pickle.HIGHEST_PROTOCOL)
            
            logger.debug(f"Saved to file cache: {file_path}")
            
        except Exception as e:
            logger.error(f"Error saving to file cache: {e}")
    
    def _get_file_cache_path(self, date, analysis_type):
        """Tạo đường dẫn file cache"""
        if isinstance(date, str):
                    date = datetime.strptime(date, '%Y-%m-%d')
        filename = f"{analysis_type}_{date.strftime('%Y%m%d')}.pkl"
        return os.path.join(self.file_cache_dir, filename)
    
    def _is_cache_fresh(self, file_path, analysis_type):
        """Kiểm tra cache còn fresh không"""
        try:
            file_age = datetime.now() - datetime.fromtimestamp(os.path.getmtime(file_path))
            cache_type = self._get_cache_type(analysis_type)
            max_age = timedelta(seconds=self.cache_duration[cache_type])
            
            return file_age < max_age
            
        except Exception as e:
            logger.error(f"Error checking cache freshness: {e}")
            return False
    
    def _get_cache_type(self, analysis_type):
        """Map analysis type to cache duration type"""
        mapping = {
            'combined': 'daily_predictions',
            'ml': 'model_results',
            'shap': 'model_results',
            'statistical': 'daily_predictions',
            'historical': 'historical_analysis'
        }
        return mapping.get(analysis_type, 'daily_predictions')
    
    def _should_file_cache(self, analysis_type, data):
        """Quyết định có nên lưu file cache không"""
        # Cache vào file cho:
        # 1. Analysis quan trọng (combined, ml)
        # 2. Data lớn
        # 3. Data có thời gian xử lý lâu
        
        if analysis_type in ['combined', 'ml', 'shap']:
            return True
        
        # Kiểm tra size (ước tính)
        try:
            if isinstance(data, dict):
                # Ước tính size dựa trên số key và complexity
                if len(data) > 10 or any(isinstance(v, (list, dict)) for v in data.values()):
                    return True
                    
                # Kiểm tra processing time
                if 'processing_time' in data and data['processing_time'] > 5:  # > 5 seconds
                    return True
                    
        except Exception:
            pass
        
        return False
    
    def _get_database_cached_prediction(self, date, analysis_type):
        """Lấy từ database cache (DailyPredictionAnalysis)"""
        try:
            # Tìm analysis record
            analysis = DailyPredictionAnalysis.objects.filter(
                analysis_date=date
            ).first()
            
            if not analysis or not analysis.predictions_data:
                return None
            
            # Convert database data to cache format
            cache_data = {
                'data': analysis.predictions_data,
                'accuracy_rate': analysis.accuracy_rate,
                'analysis_date': analysis.analysis_date,
                'target_date': analysis.target_date,
                'processing_time': analysis.processing_time,
                'method_performance': analysis.method_performance,
                'from_database': True
            }
            
            return cache_data
            
        except Exception as e:
            logger.error(f"Error getting database cached prediction: {e}")
            return None
    def invalidate_cache(self, date, prediction_type=None):
        """
        Xóa cache cho một ngày cụ thể
        """
        try:
            if prediction_type:
                cache_key = self._generate_cache_key(date, prediction_type)
                cache.delete(cache_key)
            else:
                # Xóa tất cả cache cho ngày này
                for ptype in ['combined', 'ml', 'traditional']:
                    cache_key = self._generate_cache_key(date, ptype)
                    cache.delete(cache_key)
                    
            logger.info(f"Invalidated cache for {date}")
            
        except Exception as e:
            logger.error(f"Error invalidating cache: {e}")

    def _generate_cache_key(self, date, prediction_type):
        """
        Tạo cache key duy nhất
        """
        key_string = f"{self.cache_prefix}:{date}:{prediction_type}"
        return hashlib.md5(key_string.encode()).hexdigest()
    
    def get_cache_stats(self):
        """
        Lấy thống kê về cache
        """
        # Django cache không có built-in stats, implement basic version
        return {
            'cache_hits': 0,  # Would need custom tracking
            'cache_misses': 0,
            'total_keys': 0
        }

    def invalidate_cache_for_date(self, date, analysis_types=None):
        """
        Intelligent cache invalidation

        """
        if isinstance(date, str):
                    date = datetime.strptime(date, '%Y-%m-%d')
        try:
            if analysis_types is None:
                analysis_types = ['combined', 'ml', 'shap', 'statistical', 'historical']
            
            for analysis_type in analysis_types:
                # Level 1: Memory cache
                memory_cache_key = f"pred_mem_{analysis_type}_{date.strftime('%Y%m%d')}"
                cache.delete(memory_cache_key)
                
                # Level 2: File cache
                file_path = self._get_file_cache_path(date, analysis_type)
                if os.path.exists(file_path):
                    os.remove(file_path)
                    logger.debug(f"Removed file cache: {file_path}")
            
            self.cache_stats['invalidations'] += 1
            logger.info(f"Invalidated cache for {date}")
            return True
            
        except Exception as e:
            logger.error(f"Error invalidating cache: {e}")
            return False
    
    def should_show_prediction_results(self, target_date):
        """
        Kiểm tra có nên hiển thị dự đoán hay không với logic nâng cao
        """
        try:
            # Kiểm tra kết quả thực tế
            actual_result = KetQuaXoSo.objects.filter(ngay=target_date).first()
            
            if actual_result:
                logger.info(f"Actual results exist for {target_date}, hiding predictions")
                
                # Tự động invalidate cache khi có kết quả thực tế
                yesterday = target_date - timedelta(days=1)
                self.invalidate_cache_for_date(yesterday)
                
                # Update accuracy nếu có analysis
                self._update_accuracy_for_date(yesterday, target_date, actual_result)
                
                return False
            
            # Kiểm tra thời gian - không hiển thị dự đoán cho ngày quá xa
            today = timezone.now().date()
            if target_date > today + timedelta(days=3):
                logger.info(f"Target date {target_date} too far in future")
                return False
            
            # Kiểm tra có đang trong thời gian bảo trì không
            if self._is_maintenance_time():
                logger.info("System in maintenance mode")
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"Error checking prediction display condition: {e}")
            return True  # Default: hiển thị
    
    def _update_accuracy_for_date(self, analysis_date, target_date, actual_result):
        """Update accuracy khi có kết quả thực tế"""
        try:
            analysis = DailyPredictionAnalysis.objects.filter(
                analysis_date=analysis_date,
                target_date=target_date
            ).first()
            
            if analysis:
                analysis.actual_numbers = actual_result.get_all_2digit_numbers()
                analysis.calculate_accuracy()
                logger.info(f"Updated accuracy for {analysis_date}")
                
        except Exception as e:
            logger.error(f"Error updating accuracy: {e}")
    def cache_prediction_result(self, date, analysis_type, result_data, metadata=None):
        """
        Cache prediction result with multiple levels
        """
        try:
            # Prepare cache data
            cache_data = {
                'result': result_data,
                'metadata': metadata or {},
                'timestamp': timezone.now().isoformat(),
                'analysis_type': analysis_type
            }
            if isinstance(date, str):
                    date = datetime.strptime(date, '%Y-%m-%d')
            # Level 1: Memory cache (for quick access)
            memory_cache_key = f"pred_mem_{analysis_type}_{date.strftime('%Y%m%d')}"
            cache.set(
                memory_cache_key, 
                cache_data, 
                timeout=self.cache_duration.get('daily_predictions', 86400)
            )
            
            # Level 2: File cache (for persistence)
            file_cache_key = f"{analysis_type}_prediction_{date.strftime('%Y%m%d')}.pkl"
            file_path = os.path.join(self.file_cache_dir, file_cache_key)
            
            with open(file_path, 'wb') as f:
                pickle.dump(cache_data, f)
            
            # Level 3: Database cache (for long-term storage)
            self._save_to_database_cache(date, analysis_type, cache_data)
            
            logger.info(f"Cached prediction result for {date} - {analysis_type}")
            return True
            
        except Exception as e:
            logger.error(f"Error caching prediction result: {e}")
            return False
    
    def _save_to_database_cache(self, date, analysis_type, cache_data):
        """Save cache data to database"""
        try:
            from results.models import PredictionCache
            
            # Create or update cache record
            cache_record, created = PredictionCache.objects.get_or_create(
                date=date,
                analysis_type=analysis_type,
                defaults={
                    'data': json.dumps(cache_data, default=str),
                    'created_at': timezone.now(),
                    'expires_at': timezone.now() + timedelta(
                        seconds=self.cache_duration.get('daily_predictions', 86400)
                    )
                }
            )
            
            if not created:
                cache_record.data = json.dumps(cache_data, default=str)
                cache_record.updated_at = timezone.now()
                cache_record.save()
                
        except Exception as e:
            logger.warning(f"Could not save to database cache: {e}")
    def _is_maintenance_time(self):
        """Kiểm tra có đang trong thời gian bảo trì không"""
        # Ví dụ: bảo trì từ 2-4h sáng
        current_hour = datetime.now().hour
        return 2 <= current_hour <= 4
    
    def get_cache_statistics(self):
        """Lấy thống kê cache"""
        try:
            # File cache statistics
            file_cache_size = 0
            file_count = 0
            
            if os.path.exists(self.file_cache_dir):
                for filename in os.listdir(self.file_cache_dir):
                    filepath = os.path.join(self.file_cache_dir, filename)
                    if os.path.isfile(filepath):
                        file_cache_size += os.path.getsize(filepath)
                        file_count += 1
            
            # Calculate hit rate
            total_requests = self.cache_stats['hits'] + self.cache_stats['misses']
            hit_rate = (self.cache_stats['hits'] / total_requests * 100) if total_requests > 0 else 0
            
            return {
                'memory_stats': self.cache_stats.copy(),
                'hit_rate': round(hit_rate, 2),
                'file_cache': {
                    'size_mb': round(file_cache_size / (1024 * 1024), 2),
                    'file_count': file_count
                },
                'total_requests': total_requests
            }
            
        except Exception as e:
            logger.error(f"Error getting cache statistics: {e}")
            return {}
    
    def cleanup_old_cache(self, days_old=7):
        """
        Dọn dẹp cache cũ
        """
        try:
            cutoff_date = datetime.now() - timedelta(days=days_old)
            removed_count = 0
            
            # Cleanup file cache
            if os.path.exists(self.file_cache_dir):
                for filename in os.listdir(self.file_cache_dir):
                    filepath = os.path.join(self.file_cache_dir, filename)
                    
                    if os.path.isfile(filepath):
                        file_date = datetime.fromtimestamp(os.path.getmtime(filepath))
                        
                        if file_date < cutoff_date:
                            os.remove(filepath)
                            removed_count += 1
            
            logger.info(f"Cleaned up {removed_count} old cache files")
            return removed_count
            
        except Exception as e:
            logger.error(f"Error cleaning up cache: {e}")
            return 0
    
    def preload_cache_for_date(self, date, analysis_types=None):
        """
        Preload cache cho một ngày cụ thể (chạy background)
        """
        try:
            if analysis_types is None:
                analysis_types = ['historical', 'statistical']
            
            preloaded = []
            
            for analysis_type in analysis_types:
                # Kiểm tra xem đã có cache chưa
                if not self.get_cached_prediction(date, analysis_type, include_metadata=False):
                    # Trigger generation (này sẽ cần integrate với view logic)
                    logger.info(f"Triggering preload for {date} - {analysis_type}")
                    preloaded.append(analysis_type)
            
            return preloaded
            
        except Exception as e:
            logger.error(f"Error preloading cache: {e}")
            return []