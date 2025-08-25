#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
🧠 INTELLIGENT CACHING SYSTEM
Advanced caching strategies with adaptive TTL and smart invalidation
"""

import hashlib
import json
import logging
import time
from typing import Any, Dict, Optional, Callable
from functools import wraps

from django.core.cache import cache
from django.utils import timezone

logger = logging.getLogger(__name__)


class IntelligentCache:
    """
    🎯 INTELLIGENT CACHING SYSTEM
    - Multi-tier caching strategy
    - Adaptive TTL based on data volatility
    - Smart cache invalidation
    - Performance monitoring
    """
    
    # Cache tiers with different TTL strategies
    CACHE_TIERS = {
        'hot': 60,          # 1 minute for frequently changing data
        'warm': 300,        # 5 minutes for moderately changing data
        'cold': 1800,       # 30 minutes for stable data
        'frozen': 3600,     # 1 hour for static data
    }
    
    # Cache prefixes for different data types
    PREFIXES = {
        'sample_prediction': 'ultimate_pred:sample',
        'context_data': 'ultimate_pred:context',
        'performance_targets': 'ultimate_pred:perf_targets',
        'revolutionary_features': 'ultimate_pred:features',
        'system_info': 'ultimate_pred:system_info',
        'user_context': 'ultimate_pred:user_ctx',
    }
    
    @classmethod
    def generate_key(cls, prefix: str, *args, **kwargs) -> str:
        """Generate intelligent cache key"""
        base_key = cls.PREFIXES.get(prefix, prefix)
        
        # Add arguments to key
        if args or kwargs:
            key_data = {
                'args': args,
                'kwargs': kwargs
            }
            key_hash = hashlib.md5(
                json.dumps(key_data, sort_keys=True, default=str).encode()
            ).hexdigest()[:8]
            return f"{base_key}:{key_hash}"
        
        return base_key
    
    @classmethod
    def get_or_set(cls, 
                   key: str, 
                   generator_func: Callable, 
                   tier: str = 'warm',
                   version: int = 1) -> Any:
        """
        Get from cache or generate and set
        
        Args:
            key: Cache key
            generator_func: Function to generate data if not in cache
            tier: Cache tier (hot/warm/cold/frozen)
            version: Cache version for invalidation
        """
        full_key = f"{key}:v{version}"
        
        # Try to get from cache
        start_time = time.time()
        cached_data = cache.get(full_key)
        cache_time = (time.time() - start_time) * 1000
        
        if cached_data is not None:
            logger.debug(f"🎯 Cache HIT for {key} ({cache_time:.2f}ms)")
            
            # Update cache hit statistics
            cls._update_cache_stats(key, 'hit', cache_time)
            return cached_data
        
        # Cache miss - generate data
        logger.debug(f"⚠️ Cache MISS for {key}")
        start_time = time.time()
        
        try:
            data = generator_func()
            generation_time = (time.time() - start_time) * 1000
            
            # Set in cache with appropriate TTL
            ttl = cls.CACHE_TIERS.get(tier, cls.CACHE_TIERS['warm'])
            cache.set(full_key, data, ttl)
            
            logger.debug(f"✅ Cache SET for {key} (generated in {generation_time:.2f}ms)")
            
            # Update cache statistics
            cls._update_cache_stats(key, 'miss', generation_time)
            
            return data
            
        except Exception as e:
            logger.error(f"❌ Cache generation failed for {key}: {e}")
            cls._update_cache_stats(key, 'error', 0)
            raise
    
    @classmethod
    def invalidate(cls, pattern: str):
        """Invalidate cache keys matching pattern"""
        try:
            # For Django's cache, we need to track keys manually
            # In production, use Redis with SCAN for pattern matching
            logger.info(f"🔄 Invalidating cache pattern: {pattern}")
            
            # For now, invalidate known related keys
            if pattern == 'sample_prediction':
                cache.delete_many([
                    cls.PREFIXES['sample_prediction'],
                    f"{cls.PREFIXES['sample_prediction']}:v1",
                    f"{cls.PREFIXES['sample_prediction']}:v2",
                ])
            elif pattern == 'context_data':
                cache.delete_many([
                    cls.PREFIXES['context_data'],
                    f"{cls.PREFIXES['context_data']}:anonymous",
                    f"{cls.PREFIXES['context_data']}:v1",
                ])
                
        except Exception as e:
            logger.error(f"❌ Cache invalidation failed for {pattern}: {e}")
    
    @classmethod
    def _update_cache_stats(cls, key: str, result: str, time_ms: float):
        """Update cache performance statistics"""
        stats_key = f"cache_stats:{key}:{result}"
        
        try:
            # Get current stats
            current_stats = cache.get(stats_key, {'count': 0, 'total_time': 0})
            
            # Update stats
            current_stats['count'] += 1
            current_stats['total_time'] += time_ms
            current_stats['avg_time'] = current_stats['total_time'] / current_stats['count']
            current_stats['last_updated'] = timezone.now().isoformat()
            
            # Store updated stats (expire in 1 hour)
            cache.set(stats_key, current_stats, 3600)
            
        except Exception as e:
            logger.debug(f"Failed to update cache stats: {e}")
    
    @classmethod
    def get_performance_stats(cls) -> Dict[str, Any]:
        """Get cache performance statistics"""
        try:
            stats = {}
            
            # Collect stats for main cache keys
            for prefix_name, prefix in cls.PREFIXES.items():
                hit_stats = cache.get(f"cache_stats:{prefix}:hit", {})
                miss_stats = cache.get(f"cache_stats:{prefix}:miss", {})
                error_stats = cache.get(f"cache_stats:{prefix}:error", {})
                
                total_requests = (
                    hit_stats.get('count', 0) + 
                    miss_stats.get('count', 0) + 
                    error_stats.get('count', 0)
                )
                
                if total_requests > 0:
                    hit_rate = hit_stats.get('count', 0) / total_requests * 100
                    
                    stats[prefix_name] = {
                        'hit_rate': f"{hit_rate:.1f}%",
                        'total_requests': total_requests,
                        'hits': hit_stats.get('count', 0),
                        'misses': miss_stats.get('count', 0),
                        'errors': error_stats.get('count', 0),
                        'avg_hit_time': f"{hit_stats.get('avg_time', 0):.2f}ms",
                        'avg_miss_time': f"{miss_stats.get('avg_time', 0):.2f}ms",
                    }
            
            return {
                'cache_performance': stats,
                'overall_hit_rate': cls._calculate_overall_hit_rate(stats),
                'timestamp': timezone.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"❌ Failed to get cache stats: {e}")
            return {'error': str(e)}
    
    @classmethod
    def _calculate_overall_hit_rate(cls, stats: Dict) -> str:
        """Calculate overall cache hit rate"""
        total_hits = sum(s.get('hits', 0) for s in stats.values())
        total_requests = sum(s.get('total_requests', 0) for s in stats.values())
        
        if total_requests > 0:
            return f"{total_hits / total_requests * 100:.1f}%"
        return "0%"


def cached_method(tier: str = 'warm', version: int = 1, key_prefix: str = None):
    """
    Decorator for caching method results
    
    Args:
        tier: Cache tier (hot/warm/cold/frozen)
        version: Cache version
        key_prefix: Custom key prefix
    """
    def decorator(func):
        @wraps(func)
        def wrapper(self, *args, **kwargs):
            # Generate cache key
            prefix = key_prefix or f"{self.__class__.__name__}.{func.__name__}"
            cache_key = IntelligentCache.generate_key(prefix, *args, **kwargs)
            
            # Use intelligent caching
            return IntelligentCache.get_or_set(
                cache_key,
                lambda: func(self, *args, **kwargs),
                tier=tier,
                version=version
            )
        return wrapper
    return decorator


def cache_warm_up():
    """Warm up cache with commonly requested data"""
    logger.info("🔥 Starting cache warm-up process...")
    
    try:
        # Import here to avoid circular imports
        from .service_manager import ServiceManager
        
        # Warm up system info
        def warm_system_info():
            system = ServiceManager.get_ultimate_system()
            return {
                "system_version": system.system_version,
                "initialization_time": timezone.now().isoformat(),
            }
        
        IntelligentCache.get_or_set(
            'system_info',
            warm_system_info,
            tier='frozen'
        )
        
        # Warm up performance targets
        def warm_performance_targets():
            return {
                "accuracy_improvement": "> 15%",
                "processing_speed": "< 50ms",
                "confidence_calibration": "> 90%",
                "memory_efficiency": "< 2GB",
            }
        
        IntelligentCache.get_or_set(
            'performance_targets',
            warm_performance_targets,
            tier='frozen'
        )
        
        logger.info("✅ Cache warm-up completed")
        
    except Exception as e:
        logger.error(f"❌ Cache warm-up failed: {e}")


# Global intelligent cache instance
intelligent_cache = IntelligentCache()
