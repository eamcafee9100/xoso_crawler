import json
import logging
from datetime import datetime, timedelta
from django.core.cache import cache
from django.conf import settings

logger = logging.getLogger(__name__)

class IntelligentPredictionCache:
    """Intelligent caching system with invalidation"""
    
    def __init__(self):
        self.cache_ttl = {
            'predictions': 3600,      # 1 hour
            'models': 86400,         # 1 day
            'performance': 7200      # 2 hours
        }
    
    def get_cached_prediction(self, analysis_date, model_version):
        """Get cached prediction with version checking"""
        cache_key = f"prediction:{analysis_date}:{model_version}"
        
        try:
            cached_data = cache.get(cache_key)
            if cached_data:
                if self._is_cache_valid(cached_data, analysis_date):
                    return cached_data
                else:
                    cache.delete(cache_key)
        except Exception as e:
            logger.error(f"Cache retrieval error: {e}")
        
        return None
    
    def cache_prediction(self, analysis_date, model_version, predictions):
        """Cache prediction with metadata"""
        cache_key = f"prediction:{analysis_date}:{model_version}"
        
        cache_data = {
            'predictions': predictions,
            'cached_at': datetime.now().isoformat(),
            'model_version': model_version,
            'analysis_date': analysis_date.isoformat()
        }
        
        try:
            cache.set(cache_key, cache_data, self.cache_ttl['predictions'])
        except Exception as e:
            logger.error(f"Cache storage error: {e}")
    
    def _is_cache_valid(self, cached_data, analysis_date):
        """Check if cached data is still valid"""
        try:
            cached_at = datetime.fromisoformat(cached_data['cached_at'])
            age = (datetime.now() - cached_at).total_seconds()
            return age < self.cache_ttl['predictions']
        except Exception:
            return False