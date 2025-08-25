#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
🚀 REDIS ADVANCED CACHING LAYER
Enterprise-grade caching with Redis for ultimate performance
"""

import json
import logging
import redis
import time
from typing import Any, Dict, List, Optional, Callable
from functools import wraps
from datetime import datetime, timedelta

from django.conf import settings
from django.core.cache import cache
from django.utils import timezone

logger = logging.getLogger(__name__)


class RedisAdvancedCache:
    """
    🎯 REDIS ADVANCED CACHING SYSTEM
    
    Features:
    - Multi-tier Redis caching
    - Pattern-based invalidation
    - Predictive cache warming
    - Performance analytics
    - Circuit breaker pattern
    """
    
    def __init__(self):
        """Initialize Redis connections"""
        try:
            # Primary Redis connection
            self.redis_client = redis.Redis(
                host=getattr(settings, 'REDIS_HOST', 'localhost'),
                port=getattr(settings, 'REDIS_PORT', 6379),
                db=getattr(settings, 'REDIS_DB', 0),
                decode_responses=True,
                socket_connect_timeout=5,
                socket_timeout=5,
                retry_on_timeout=True
            )
            
            # Test connection
            self.redis_client.ping()
            self.redis_available = True
            logger.info("✅ Redis connection established")
            
        except (redis.ConnectionError, redis.TimeoutError) as e:
            logger.warning(f"⚠️ Redis unavailable, falling back to Django cache: {e}")
            self.redis_available = False
            self.redis_client = None
    
    # Cache tiers with different TTL strategies
    CACHE_TIERS = {
        'hot': 60,          # 1 minute - frequently changing data
        'warm': 300,        # 5 minutes - moderately changing data
        'cold': 1800,       # 30 minutes - stable data
        'frozen': 7200,     # 2 hours - static data
        'permanent': 86400, # 24 hours - rarely changing data
    }
    
    # Cache prefixes for organized key management
    PREFIXES = {
        'prediction': 'ultimate:pred',
        'context': 'ultimate:ctx',
        'system': 'ultimate:sys',
        'user': 'ultimate:user',
        'analytics': 'ultimate:analytics',
        'ml_model': 'ultimate:ml',
    }
    
    def get_or_set(self, 
                   key: str, 
                   generator_func: Callable, 
                   tier: str = 'warm',
                   prefix: str = 'prediction',
                   version: int = 1) -> Any:
        """
        Advanced get or set with Redis backend
        
        Args:
            key: Cache key
            generator_func: Function to generate data if cache miss
            tier: Cache tier (hot/warm/cold/frozen/permanent)
            prefix: Key prefix for organization
            version: Cache version for invalidation
        """
        
        # Generate full key
        full_key = f"{self.PREFIXES[prefix]}:{key}:v{version}"
        
        # Try Redis first, fallback to Django cache
        cached_data = self._get_from_cache(full_key)
        
        if cached_data is not None:
            logger.debug(f"🎯 Cache HIT for {full_key}")
            self._record_cache_hit(prefix, key)
            return self._deserialize_data(cached_data)
        
        # Cache miss - generate data
        logger.debug(f"⚠️ Cache MISS for {full_key}")
        start_time = time.time()
        
        try:
            data = generator_func()
            generation_time = (time.time() - start_time) * 1000
            
            # Store in cache
            ttl = self.CACHE_TIERS.get(tier, self.CACHE_TIERS['warm'])
            self._set_in_cache(full_key, data, ttl)
            
            logger.debug(f"✅ Cache SET for {full_key} (generated in {generation_time:.2f}ms)")
            self._record_cache_miss(prefix, key, generation_time)
            
            return data
            
        except Exception as e:
            logger.error(f"❌ Cache generation failed for {full_key}: {e}")
            self._record_cache_error(prefix, key)
            raise
    
    def _get_from_cache(self, key: str) -> Optional[str]:
        """Get data from Redis or Django cache"""
        if self.redis_available and self.redis_client:
            try:
                return self.redis_client.get(key)
            except Exception as e:
                logger.warning(f"Redis GET failed, using Django cache: {e}")
                return cache.get(key)
        else:
            return cache.get(key)
    
    def _set_in_cache(self, key: str, data: Any, ttl: int):
        """Set data in Redis or Django cache"""
        serialized_data = self._serialize_data(data)
        
        if self.redis_available and self.redis_client:
            try:
                self.redis_client.setex(key, ttl, serialized_data)
                return
            except Exception as e:
                logger.warning(f"Redis SET failed, using Django cache: {e}")
        
        # Fallback to Django cache
        cache.set(key, serialized_data, ttl)
    
    def _serialize_data(self, data: Any) -> str:
        """Serialize data for storage"""
        try:
            return json.dumps(data, default=str, ensure_ascii=False)
        except (TypeError, ValueError) as e:
            logger.warning(f"JSON serialization failed: {e}")
            return str(data)
    
    def _deserialize_data(self, data: str) -> Any:
        """Deserialize data from storage"""
        try:
            return json.loads(data)
        except (TypeError, ValueError, json.JSONDecodeError):
            return data
    
    def invalidate_pattern(self, pattern: str, prefix: str = 'prediction'):
        """Invalidate cache keys matching pattern"""
        try:
            full_pattern = f"{self.PREFIXES[prefix]}:{pattern}*"
            
            if self.redis_available and self.redis_client:
                # Use Redis SCAN for pattern matching
                keys = []
                for key in self.redis_client.scan_iter(match=full_pattern):
                    keys.append(key)
                
                if keys:
                    self.redis_client.delete(*keys)
                    logger.info(f"🔄 Invalidated {len(keys)} Redis keys matching {full_pattern}")
            else:
                # Django cache doesn't support pattern matching easily
                # We'll need to track keys manually or use a different approach
                logger.warning("Pattern invalidation limited without Redis")
                
        except Exception as e:
            logger.error(f"❌ Cache invalidation failed for {pattern}: {e}")
    
    def _record_cache_hit(self, prefix: str, key: str):
        """Record cache hit for analytics"""
        try:
            stats_key = f"cache_stats:hits:{prefix}"
            if self.redis_available and self.redis_client:
                self.redis_client.incr(stats_key)
                self.redis_client.expire(stats_key, 3600)  # Expire in 1 hour
        except Exception:
            pass  # Non-critical operation
    
    def _record_cache_miss(self, prefix: str, key: str, generation_time: float):
        """Record cache miss for analytics"""
        try:
            stats_key = f"cache_stats:misses:{prefix}"
            time_key = f"cache_stats:gen_time:{prefix}"
            
            if self.redis_available and self.redis_client:
                self.redis_client.incr(stats_key)
                self.redis_client.expire(stats_key, 3600)
                
                # Store generation time for performance analysis
                self.redis_client.lpush(time_key, generation_time)
                self.redis_client.ltrim(time_key, 0, 99)  # Keep last 100 times
                self.redis_client.expire(time_key, 3600)
        except Exception:
            pass  # Non-critical operation
    
    def _record_cache_error(self, prefix: str, key: str):
        """Record cache error for monitoring"""
        try:
            stats_key = f"cache_stats:errors:{prefix}"
            if self.redis_available and self.redis_client:
                self.redis_client.incr(stats_key)
                self.redis_client.expire(stats_key, 3600)
        except Exception:
            pass  # Non-critical operation
    
    def get_performance_analytics(self) -> Dict[str, Any]:
        """Get comprehensive cache performance analytics"""
        try:
            analytics = {}
            
            for prefix_name, prefix_key in self.PREFIXES.items():
                hits = self._get_cache_stat(f"cache_stats:hits:{prefix_name}")
                misses = self._get_cache_stat(f"cache_stats:misses:{prefix_name}")
                errors = self._get_cache_stat(f"cache_stats:errors:{prefix_name}")
                
                total_requests = hits + misses + errors
                
                if total_requests > 0:
                    hit_rate = (hits / total_requests) * 100
                    
                    # Get average generation time
                    gen_times = self._get_generation_times(f"cache_stats:gen_time:{prefix_name}")
                    avg_gen_time = sum(gen_times) / len(gen_times) if gen_times else 0
                    
                    analytics[prefix_name] = {
                        'hit_rate': f"{hit_rate:.1f}%",
                        'total_requests': total_requests,
                        'hits': hits,
                        'misses': misses,
                        'errors': errors,
                        'avg_generation_time': f"{avg_gen_time:.2f}ms",
                        'error_rate': f"{(errors / total_requests * 100):.2f}%"
                    }
            
            # Calculate overall metrics
            total_hits = sum(a.get('hits', 0) for a in analytics.values())
            total_requests = sum(a.get('total_requests', 0) for a in analytics.values())
            overall_hit_rate = (total_hits / total_requests * 100) if total_requests > 0 else 0
            
            return {
                'redis_available': self.redis_available,
                'cache_analytics': analytics,
                'overall_hit_rate': f"{overall_hit_rate:.1f}%",
                'timestamp': timezone.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"❌ Failed to get cache analytics: {e}")
            return {'error': str(e)}
    
    def _get_cache_stat(self, key: str) -> int:
        """Get cache statistic value"""
        try:
            if self.redis_available and self.redis_client:
                value = self.redis_client.get(key)
                return int(value) if value else 0
            return 0
        except Exception:
            return 0
    
    def _get_generation_times(self, key: str) -> List[float]:
        """Get list of generation times"""
        try:
            if self.redis_available and self.redis_client:
                times = self.redis_client.lrange(key, 0, -1)
                return [float(t) for t in times]
            return []
        except Exception:
            return []
    
    def warm_cache_predictively(self, user_patterns: Dict[str, Any]):
        """Predictively warm cache based on user patterns"""
        try:
            logger.info("🔥 Starting predictive cache warming...")
            
            # Common prediction scenarios to pre-generate
            common_scenarios = [
                {'numbers': list(range(1, 21)), 'horizon': 5},
                {'numbers': [12, 25, 34, 8, 41, 17, 29, 3, 36, 22], 'horizon': 3},
                {'numbers': [1, 15, 23, 37, 44, 9, 18, 27, 33, 41], 'horizon': 7},
            ]
            
            for scenario in common_scenarios:
                # Pre-generate predictions for popular scenarios
                cache_key = f"prediction_scenario_{hash(str(scenario['numbers']))}"
                
                def generate_prediction():
                    # This would call the actual prediction system
                    return {
                        'predictions': scenario['numbers'][:scenario['horizon']],
                        'confidence': 0.75,
                        'pre_generated': True,
                        'timestamp': timezone.now().isoformat()
                    }
                
                self.get_or_set(
                    cache_key,
                    generate_prediction,
                    tier='cold',
                    prefix='prediction'
                )
            
            logger.info("✅ Predictive cache warming completed")
            
        except Exception as e:
            logger.error(f"❌ Predictive cache warming failed: {e}")


class CircuitBreakerCache:
    """
    🛡️ CIRCUIT BREAKER PATTERN FOR CACHE
    Prevent cascade failures when cache is down
    """
    
    def __init__(self):
        self.failure_count = 0
        self.failure_threshold = 5
        self.recovery_timeout = 60  # seconds
        self.last_failure_time = None
        self.state = 'CLOSED'  # CLOSED, OPEN, HALF_OPEN
        
        self.redis_cache = RedisAdvancedCache()
    
    def get_or_set(self, key: str, generator_func: Callable, **kwargs) -> Any:
        """Get or set with circuit breaker protection"""
        
        if self.state == 'OPEN':
            # Check if we should try to recover
            if (time.time() - self.last_failure_time) > self.recovery_timeout:
                self.state = 'HALF_OPEN'
                logger.info("🔄 Circuit breaker moving to HALF_OPEN state")
            else:
                # Circuit is open, bypass cache
                logger.warning("⚠️ Circuit breaker OPEN, bypassing cache")
                return generator_func()
        
        try:
            result = self.redis_cache.get_or_set(key, generator_func, **kwargs)
            
            if self.state == 'HALF_OPEN':
                # Success in half-open state, close the circuit
                self.state = 'CLOSED'
                self.failure_count = 0
                logger.info("✅ Circuit breaker CLOSED, cache recovered")
            
            return result
            
        except Exception as e:
            self.failure_count += 1
            self.last_failure_time = time.time()
            
            if self.failure_count >= self.failure_threshold:
                self.state = 'OPEN'
                logger.error(f"🚨 Circuit breaker OPEN due to {self.failure_count} failures")
            
            # Fallback to direct generation
            logger.warning(f"⚠️ Cache failed, using direct generation: {e}")
            return generator_func()


# Global instance
redis_advanced_cache = RedisAdvancedCache()
circuit_breaker_cache = CircuitBreakerCache()


def redis_cached(tier: str = 'warm', prefix: str = 'prediction', version: int = 1):
    """
    🎯 DECORATOR FOR REDIS CACHING WITH CIRCUIT BREAKER
    
    Usage:
        @redis_cached(tier='cold', prefix='system')
        def expensive_operation(self, param1, param2):
            return complex_calculation()
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Generate cache key from function name and parameters
            key_data = {
                'func': func.__name__,
                'args': args[1:] if args else [],  # Skip 'self' if present
                'kwargs': kwargs
            }
            cache_key = f"{func.__name__}_{hash(str(key_data))}"
            
            def generator():
                return func(*args, **kwargs)
            
            return circuit_breaker_cache.get_or_set(
                cache_key,
                generator,
                tier=tier,
                prefix=prefix,
                version=version
            )
        
        return wrapper
    return decorator
