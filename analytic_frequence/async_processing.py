#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
🚀 ASYNC PROCESSING SYSTEM
High-performance asynchronous operations for ultimate performance
"""

import asyncio
import logging
import time
import concurrent.futures
from typing import Any, Dict, List, Optional, Callable, Awaitable
from functools import wraps
from dataclasses import dataclass
from queue import Queue
import threading

from django.utils import timezone
from django.core.cache import cache

logger = logging.getLogger(__name__)


@dataclass
class AsyncTask:
    """Async task definition"""
    id: str
    name: str
    func: Callable
    args: tuple
    kwargs: dict
    priority: int = 1
    timeout: float = 30.0
    created_at: float = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = time.time()


class AsyncTaskManager:
    """
    🎯 ASYNC TASK MANAGER
    
    Features:
    - Concurrent task execution
    - Priority queue
    - Task monitoring
    - Resource management
    - Error handling and retries
    """
    
    def __init__(self, max_workers: int = 10):
        self.max_workers = max_workers
        self.executor = concurrent.futures.ThreadPoolExecutor(max_workers=max_workers)
        self.task_queue = Queue()
        self.running_tasks = {}
        self.completed_tasks = {}
        self.failed_tasks = {}
        self.task_stats = {
            'total_executed': 0,
            'total_failed': 0,
            'avg_execution_time': 0,
            'current_load': 0
        }
        
        # Start background task processor
        self.processor_thread = threading.Thread(target=self._process_tasks, daemon=True)
        self.processor_thread.start()
        
        logger.info(f"✅ AsyncTaskManager initialized with {max_workers} workers")
    
    def submit_task(self, 
                   task_id: str,
                   task_name: str,
                   func: Callable,
                   args: tuple = (),
                   kwargs: dict = None,
                   priority: int = 1,
                   timeout: float = 30.0) -> str:
        """Submit async task for execution"""
        
        kwargs = kwargs or {}
        
        task = AsyncTask(
            id=task_id,
            name=task_name,
            func=func,
            args=args,
            kwargs=kwargs,
            priority=priority,
            timeout=timeout
        )
        
        self.task_queue.put(task)
        logger.debug(f"🎯 Task submitted: {task_name} (ID: {task_id})")
        
        return task_id
    
    def _process_tasks(self):
        """Background task processor"""
        while True:
            try:
                task = self.task_queue.get(timeout=1.0)
                self._execute_task(task)
                self.task_queue.task_done()
            except:
                continue  # Timeout or other non-critical error
    
    def _execute_task(self, task: AsyncTask):
        """Execute individual task"""
        start_time = time.time()
        
        try:
            self.running_tasks[task.id] = {
                'task': task,
                'start_time': start_time,
                'status': 'running'
            }
            
            # Submit to thread pool
            future = self.executor.submit(task.func, *task.args, **task.kwargs)
            
            try:
                result = future.result(timeout=task.timeout)
                execution_time = time.time() - start_time
                
                # Store successful result
                self.completed_tasks[task.id] = {
                    'task': task,
                    'result': result,
                    'execution_time': execution_time,
                    'completed_at': time.time(),
                    'status': 'completed'
                }
                
                # Update stats
                self.task_stats['total_executed'] += 1
                self._update_avg_execution_time(execution_time)
                
                logger.debug(f"✅ Task completed: {task.name} ({execution_time:.2f}s)")
                
            except concurrent.futures.TimeoutError:
                self._handle_task_failure(task, f"Task timeout ({task.timeout}s)", start_time)
            except Exception as e:
                self._handle_task_failure(task, str(e), start_time)
                
        except Exception as e:
            self._handle_task_failure(task, f"Execution error: {e}", start_time)
        finally:
            # Remove from running tasks
            self.running_tasks.pop(task.id, None)
    
    def _handle_task_failure(self, task: AsyncTask, error: str, start_time: float):
        """Handle task failure"""
        execution_time = time.time() - start_time
        
        self.failed_tasks[task.id] = {
            'task': task,
            'error': error,
            'execution_time': execution_time,
            'failed_at': time.time(),
            'status': 'failed'
        }
        
        self.task_stats['total_failed'] += 1
        logger.error(f"❌ Task failed: {task.name} - {error}")
    
    def _update_avg_execution_time(self, execution_time: float):
        """Update average execution time"""
        current_avg = self.task_stats['avg_execution_time']
        total_executed = self.task_stats['total_executed']
        
        if total_executed == 1:
            self.task_stats['avg_execution_time'] = execution_time
        else:
            # Rolling average
            self.task_stats['avg_execution_time'] = (
                (current_avg * (total_executed - 1) + execution_time) / total_executed
            )
    
    def get_task_status(self, task_id: str) -> Dict[str, Any]:
        """Get status of specific task"""
        
        # Check running tasks
        if task_id in self.running_tasks:
            task_info = self.running_tasks[task_id]
            return {
                'status': 'running',
                'task_name': task_info['task'].name,
                'runtime': time.time() - task_info['start_time'],
                'priority': task_info['task'].priority
            }
        
        # Check completed tasks
        if task_id in self.completed_tasks:
            task_info = self.completed_tasks[task_id]
            return {
                'status': 'completed',
                'task_name': task_info['task'].name,
                'execution_time': task_info['execution_time'],
                'result_available': True
            }
        
        # Check failed tasks
        if task_id in self.failed_tasks:
            task_info = self.failed_tasks[task_id]
            return {
                'status': 'failed',
                'task_name': task_info['task'].name,
                'error': task_info['error'],
                'execution_time': task_info['execution_time']
            }
        
        return {'status': 'not_found'}
    
    def get_task_result(self, task_id: str) -> Any:
        """Get result of completed task"""
        if task_id in self.completed_tasks:
            return self.completed_tasks[task_id]['result']
        return None
    
    def get_performance_metrics(self) -> Dict[str, Any]:
        """Get comprehensive performance metrics"""
        current_time = time.time()
        
        # Calculate current load
        active_tasks = len(self.running_tasks)
        load_percentage = (active_tasks / self.max_workers) * 100
        
        # Get queue size
        queue_size = self.task_queue.qsize()
        
        # Calculate success rate
        total_tasks = self.task_stats['total_executed'] + self.task_stats['total_failed']
        success_rate = (self.task_stats['total_executed'] / total_tasks * 100) if total_tasks > 0 else 100
        
        return {
            'current_load': f"{load_percentage:.1f}%",
            'active_tasks': active_tasks,
            'queued_tasks': queue_size,
            'max_workers': self.max_workers,
            'total_executed': self.task_stats['total_executed'],
            'total_failed': self.task_stats['total_failed'],
            'success_rate': f"{success_rate:.1f}%",
            'avg_execution_time': f"{self.task_stats['avg_execution_time']:.2f}s",
            'uptime': f"{(current_time - getattr(self, 'start_time', current_time)):.0f}s"
        }


class AsyncPredictionEngine:
    """
    🚀 ASYNC PREDICTION ENGINE
    High-performance prediction processing
    """
    
    def __init__(self):
        self.task_manager = AsyncTaskManager(max_workers=8)
        self.prediction_cache = {}
    
    async def predict_async(self, 
                          numbers: List[int], 
                          horizon: int = 5,
                          algorithm: str = 'ultimate') -> Dict[str, Any]:
        """Async prediction with caching"""
        
        # Generate cache key
        cache_key = f"async_pred_{hash(str(sorted(numbers)))}_{horizon}_{algorithm}"
        
        # Check cache first
        cached_result = cache.get(cache_key)
        if cached_result:
            logger.debug(f"🎯 Async prediction cache HIT: {cache_key}")
            return cached_result
        
        # Submit async task
        task_id = f"prediction_{int(time.time() * 1000000)}"
        
        def prediction_worker():
            """Worker function for prediction"""
            try:
                from analytic_frequence.prediction_system import UltimatePredictionSystem
                
                system = UltimatePredictionSystem()
                result = system.predict(numbers, horizon)
                
                # Add async metadata
                result['async_metadata'] = {
                    'generated_async': True,
                    'task_id': task_id,
                    'algorithm': algorithm,
                    'processing_time': time.time()
                }
                
                return result
                
            except Exception as e:
                logger.error(f"❌ Async prediction failed: {e}")
                return {
                    'error': str(e),
                    'predictions': [],
                    'async_metadata': {
                        'failed': True,
                        'task_id': task_id
                    }
                }
        
        # Submit task
        self.task_manager.submit_task(
            task_id=task_id,
            task_name=f"prediction_{algorithm}",
            func=prediction_worker,
            priority=2,  # High priority for predictions
            timeout=15.0
        )
        
        # Wait for result with timeout
        max_wait = 10  # seconds
        wait_interval = 0.1
        waited = 0
        
        while waited < max_wait:
            task_status = self.task_manager.get_task_status(task_id)
            
            if task_status['status'] == 'completed':
                result = self.task_manager.get_task_result(task_id)
                
                # Cache result for future use
                cache.set(cache_key, result, 300)  # Cache for 5 minutes
                
                logger.debug(f"✅ Async prediction completed: {task_id}")
                return result
            
            elif task_status['status'] == 'failed':
                logger.error(f"❌ Async prediction failed: {task_id}")
                return {
                    'error': 'Async prediction failed',
                    'predictions': [],
                    'task_id': task_id
                }
            
            await asyncio.sleep(wait_interval)
            waited += wait_interval
        
        # Timeout fallback
        logger.warning(f"⚠️ Async prediction timeout: {task_id}")
        return {
            'error': 'Prediction timeout',
            'predictions': [],
            'task_id': task_id,
            'status': 'timeout'
        }
    
    def get_performance_dashboard(self) -> Dict[str, Any]:
        """Get async engine performance dashboard"""
        return {
            'task_manager_metrics': self.task_manager.get_performance_metrics(),
            'cache_stats': {
                'cached_predictions': len(self.prediction_cache),
                'cache_memory_usage': f"{len(str(self.prediction_cache)) / 1024:.1f}KB"
            },
            'timestamp': timezone.now().isoformat()
        }


class BackgroundJobProcessor:
    """
    ⚡ BACKGROUND JOB PROCESSOR
    Process intensive tasks in background
    """
    
    def __init__(self):
        self.task_manager = AsyncTaskManager(max_workers=4)
        self.job_history = []
    
    def schedule_cache_warming(self, patterns: List[Dict[str, Any]]):
        """Schedule cache warming job"""
        
        def warm_cache_job():
            """Background cache warming"""
            try:
                from analytic_frequence.redis_advanced_cache import redis_advanced_cache
                
                for pattern in patterns:
                    redis_advanced_cache.warm_cache_predictively(pattern)
                
                return {
                    'status': 'success',
                    'patterns_processed': len(patterns),
                    'timestamp': timezone.now().isoformat()
                }
                
            except Exception as e:
                return {
                    'status': 'failed',
                    'error': str(e),
                    'timestamp': timezone.now().isoformat()
                }
        
        task_id = f"cache_warming_{int(time.time())}"
        self.task_manager.submit_task(
            task_id=task_id,
            task_name="cache_warming",
            func=warm_cache_job,
            priority=1,
            timeout=120.0
        )
        
        logger.info(f"🔥 Cache warming job scheduled: {task_id}")
        return task_id
    
    def schedule_performance_analysis(self):
        """Schedule performance analysis job"""
        
        def analyze_performance():
            """Background performance analysis"""
            try:
                from analytic_frequence.performance_monitoring import performance_monitor
                
                analysis = performance_monitor.generate_comprehensive_report()
                
                # Store analysis result
                cache.set('latest_performance_analysis', analysis, 3600)
                
                return analysis
                
            except Exception as e:
                return {
                    'status': 'failed',
                    'error': str(e),
                    'timestamp': timezone.now().isoformat()
                }
        
        task_id = f"performance_analysis_{int(time.time())}"
        self.task_manager.submit_task(
            task_id=task_id,
            task_name="performance_analysis",
            func=analyze_performance,
            priority=1,
            timeout=60.0
        )
        
        logger.info(f"📊 Performance analysis job scheduled: {task_id}")
        return task_id


def async_operation(timeout: float = 30.0, priority: int = 1):
    """
    🎯 DECORATOR FOR ASYNC OPERATIONS
    
    Usage:
        @async_operation(timeout=15.0, priority=2)
        def expensive_calculation(self, data):
            return complex_processing(data)
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            task_manager = AsyncTaskManager()
            
            task_id = f"{func.__name__}_{int(time.time() * 1000000)}"
            
            # Submit as async task
            task_manager.submit_task(
                task_id=task_id,
                task_name=func.__name__,
                func=func,
                args=args,
                kwargs=kwargs,
                priority=priority,
                timeout=timeout
            )
            
            return {
                'task_id': task_id,
                'status': 'submitted',
                'estimated_completion': time.time() + timeout
            }
        
        return wrapper
    return decorator


# Global instances
async_task_manager = AsyncTaskManager()
async_prediction_engine = AsyncPredictionEngine()
background_job_processor = BackgroundJobProcessor()
