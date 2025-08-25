#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
🚀 DATABASE OPTIMIZATION LAYER
Advanced database connection pooling and query optimization
"""

import logging
import time
from typing import Dict, List, Any, Optional
from contextlib import contextmanager
from functools import wraps
from collections import defaultdict

from django.db import connections, transaction
from django.db.models import QuerySet, Q, Prefetch
from django.core.cache import cache
from django.utils import timezone

logger = logging.getLogger(__name__)


class DatabaseOptimizer:
    """
    🎯 DATABASE PERFORMANCE OPTIMIZER
    
    Features:
    - Connection pooling optimization
    - Query analysis and optimization
    - Bulk operations
    - Read replica routing
    - Query result caching
    """
    
    def __init__(self):
        self.query_stats = defaultdict(list)
        self.slow_query_threshold = 100  # milliseconds
    
    def optimize_connections(self):
        """Optimize database connections"""
        try:
            for alias in connections:
                connection = connections[alias]
                
                # Optimize connection settings
                if hasattr(connection, 'settings_dict'):
                    settings = connection.settings_dict.get('OPTIONS', {})
                    
                    # Apply optimizations
                    optimizations = {
                        'MAX_CONNS': 20,
                        'MIN_CONNS': 5,
                        'conn_max_age': 600,  # 10 minutes
                        'CONN_HEALTH_CHECKS': True,
                        'autocommit': True,
                    }
                    
                    for key, value in optimizations.items():
                        if key not in settings:
                            settings[key] = value
                            logger.info(f"✅ Applied DB optimization: {key}={value}")
            
        except Exception as e:
            logger.error(f"❌ Database optimization failed: {e}")
    
    @contextmanager
    def optimized_query_context(self, description: str = "query"):
        """Context manager for query optimization and monitoring"""
        start_time = time.time()
        
        try:
            # Enable query debugging if needed
            from django.conf import settings
            original_debug = getattr(settings, 'DEBUG', False)
            
            yield
            
        finally:
            duration = (time.time() - start_time) * 1000
            
            # Record query performance
            self.query_stats[description].append({
                'duration_ms': duration,
                'timestamp': timezone.now(),
                'slow': duration > self.slow_query_threshold
            })
            
            if duration > self.slow_query_threshold:
                logger.warning(f"⚠️ Slow query detected ({description}): {duration:.2f}ms")
            else:
                logger.debug(f"✅ Query completed ({description}): {duration:.2f}ms")
    
    def bulk_fetch_with_prefetch(self, 
                                queryset: QuerySet, 
                                prefetch_fields: List[str],
                                batch_size: int = 1000) -> List[Any]:
        """Optimized bulk fetching with prefetch"""
        try:
            with self.optimized_query_context("bulk_fetch_with_prefetch"):
                
                # Apply prefetch optimizations
                prefetch_related = []
                for field in prefetch_fields:
                    if '.' in field:
                        # Nested prefetch
                        prefetch_related.append(
                            Prefetch(field.split('.')[0], 
                                   queryset=queryset.model._meta.get_field(field.split('.')[0])
                                   .related_model.objects.select_related())
                        )
                    else:
                        prefetch_related.append(field)
                
                # Execute optimized query
                optimized_queryset = queryset.prefetch_related(*prefetch_related)
                
                # Use iterator for large datasets
                if queryset.count() > batch_size:
                    return list(optimized_queryset.iterator(chunk_size=batch_size))
                else:
                    return list(optimized_queryset)
                    
        except Exception as e:
            logger.error(f"❌ Bulk fetch failed: {e}")
            return list(queryset)
    
    def optimize_number_frequency_queries(self):
        """Specific optimizations for NumberFrequencyStats queries"""
        from analytic_frequence.models import NumberFrequencyStats
        
        try:
            with self.optimized_query_context("number_frequency_optimization"):
                
                # Create optimized queries for common patterns
                optimized_queries = {
                    'recent_high_frequency': NumberFrequencyStats.objects.filter(
                        frequency__gte=10
                    ).select_related().order_by('-frequency')[:100],
                    
                    'recent_trends': NumberFrequencyStats.objects.filter(
                        last_seen__gte=timezone.now() - timezone.timedelta(days=30)
                    ).select_related().order_by('-last_seen')[:200],
                    
                    'hot_numbers': NumberFrequencyStats.objects.filter(
                        frequency__gte=15,
                        last_seen__gte=timezone.now() - timezone.timedelta(days=7)
                    ).select_related()
                }
                
                # Pre-execute and cache common queries
                cached_results = {}
                for query_name, queryset in optimized_queries.items():
                    cache_key = f"optimized_query:{query_name}"
                    
                    # Try cache first
                    cached_data = cache.get(cache_key)
                    if cached_data is None:
                        # Execute and cache for 5 minutes
                        cached_data = list(queryset)
                        cache.set(cache_key, cached_data, 300)
                        logger.info(f"✅ Cached query result: {query_name} ({len(cached_data)} items)")
                    
                    cached_results[query_name] = cached_data
                
                return cached_results
                
        except Exception as e:
            logger.error(f"❌ Number frequency query optimization failed: {e}")
            return {}
    
    def get_query_performance_report(self) -> Dict[str, Any]:
        """Generate comprehensive query performance report"""
        try:
            report = {
                'total_queries': 0,
                'slow_queries': 0,
                'avg_query_time': 0,
                'query_breakdown': {},
                'recommendations': []
            }
            
            all_durations = []
            
            for query_type, stats in self.query_stats.items():
                if not stats:
                    continue
                
                durations = [s['duration_ms'] for s in stats]
                slow_count = sum(1 for s in stats if s['slow'])
                
                all_durations.extend(durations)
                
                query_report = {
                    'count': len(stats),
                    'avg_duration': sum(durations) / len(durations),
                    'max_duration': max(durations),
                    'min_duration': min(durations),
                    'slow_queries': slow_count,
                    'slow_percentage': (slow_count / len(stats)) * 100
                }
                
                report['query_breakdown'][query_type] = query_report
                
                # Generate recommendations
                if query_report['slow_percentage'] > 20:
                    report['recommendations'].append(
                        f"❌ {query_type}: {query_report['slow_percentage']:.1f}% slow queries - needs optimization"
                    )
                elif query_report['avg_duration'] > 50:
                    report['recommendations'].append(
                        f"⚠️ {query_type}: avg {query_report['avg_duration']:.1f}ms - consider indexing"
                    )
                else:
                    report['recommendations'].append(
                        f"✅ {query_type}: performing well ({query_report['avg_duration']:.1f}ms avg)"
                    )
            
            if all_durations:
                report['total_queries'] = len(all_durations)
                report['slow_queries'] = sum(1 for d in all_durations if d > self.slow_query_threshold)
                report['avg_query_time'] = sum(all_durations) / len(all_durations)
                report['slow_query_percentage'] = (report['slow_queries'] / report['total_queries']) * 100
            
            return report
            
        except Exception as e:
            logger.error(f"❌ Failed to generate query performance report: {e}")
            return {'error': str(e)}


class ReadWriteSplitter:
    """
    📊 READ/WRITE SPLITTING FOR PERFORMANCE
    Route read operations to read replicas
    """
    
    def __init__(self):
        self.read_db = 'default'  # Could be configured for read replica
        self.write_db = 'default'
        self.read_operations = {'select', 'count', 'exists', 'aggregate'}
    
    @contextmanager
    def read_context(self):
        """Context for read operations"""
        try:
            from django.db import connections
            connection = connections[self.read_db]
            
            with connection.cursor() as cursor:
                yield cursor
                
        except Exception as e:
            logger.error(f"❌ Read context failed: {e}")
            raise
    
    @contextmanager
    def write_context(self):
        """Context for write operations"""
        try:
            from django.db import connections
            connection = connections[self.write_db]
            
            with transaction.atomic(using=self.write_db):
                with connection.cursor() as cursor:
                    yield cursor
                    
        except Exception as e:
            logger.error(f"❌ Write context failed: {e}")
            raise


class QueryBatchProcessor:
    """
    ⚡ BATCH QUERY PROCESSOR
    Optimize multiple database operations
    """
    
    def __init__(self):
        self.batch_size = 1000
        self.pending_operations = []
    
    def add_operation(self, operation_type: str, model_class, data: Dict[str, Any]):
        """Add operation to batch"""
        self.pending_operations.append({
            'type': operation_type,
            'model': model_class,
            'data': data,
            'timestamp': timezone.now()
        })
    
    def execute_batch(self):
        """Execute all pending operations in optimized batches"""
        if not self.pending_operations:
            return
        
        try:
            with transaction.atomic():
                # Group operations by type and model
                grouped_ops = defaultdict(list)
                
                for op in self.pending_operations:
                    key = f"{op['type']}_{op['model'].__name__}"
                    grouped_ops[key].append(op)
                
                # Execute grouped operations
                for group_key, operations in grouped_ops.items():
                    if 'bulk_create' in group_key:
                        self._execute_bulk_create(operations)
                    elif 'bulk_update' in group_key:
                        self._execute_bulk_update(operations)
                    elif 'bulk_delete' in group_key:
                        self._execute_bulk_delete(operations)
                
                logger.info(f"✅ Executed {len(self.pending_operations)} batch operations")
                self.pending_operations.clear()
                
        except Exception as e:
            logger.error(f"❌ Batch execution failed: {e}")
            raise
    
    def _execute_bulk_create(self, operations: List[Dict]):
        """Execute bulk create operations"""
        if not operations:
            return
        
        model_class = operations[0]['model']
        objects_to_create = [
            model_class(**op['data']) 
            for op in operations
        ]
        
        # Bulk create in batches
        for i in range(0, len(objects_to_create), self.batch_size):
            batch = objects_to_create[i:i + self.batch_size]
            model_class.objects.bulk_create(batch, batch_size=self.batch_size)
    
    def _execute_bulk_update(self, operations: List[Dict]):
        """Execute bulk update operations"""
        if not operations:
            return
        
        model_class = operations[0]['model']
        
        # Group by fields to update
        for op in operations:
            model_class.objects.filter(
                id=op['data'].get('id')
            ).update(**{
                k: v for k, v in op['data'].items() 
                if k != 'id'
            })
    
    def _execute_bulk_delete(self, operations: List[Dict]):
        """Execute bulk delete operations"""
        if not operations:
            return
        
        model_class = operations[0]['model']
        ids_to_delete = [op['data']['id'] for op in operations if 'id' in op['data']]
        
        if ids_to_delete:
            model_class.objects.filter(id__in=ids_to_delete).delete()


# Decorator for database operation optimization
def optimized_db_operation(operation_type: str = 'read'):
    """
    🎯 DECORATOR FOR DATABASE OPTIMIZATION
    
    Usage:
        @optimized_db_operation('read')
        def get_frequency_data(self):
            return NumberFrequencyStats.objects.all()
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            optimizer = DatabaseOptimizer()
            
            with optimizer.optimized_query_context(f"{func.__name__}_{operation_type}"):
                return func(*args, **kwargs)
        
        return wrapper
    return decorator


# Global instances
db_optimizer = DatabaseOptimizer()
read_write_splitter = ReadWriteSplitter()
query_batch_processor = QueryBatchProcessor()
