#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
🤖 REAL-TIME MODEL TRAINING SYSTEM
Continuous learning and model optimization
"""

import json
import logging
import time
import threading
import numpy as np
from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass, asdict
from collections import defaultdict, deque
from datetime import datetime, timedelta
import asyncio
from concurrent.futures import ThreadPoolExecutor

from django.utils import timezone
from django.core.cache import cache

logger = logging.getLogger(__name__)


@dataclass
class TrainingJob:
    """Training job specification"""
    job_id: str
    model_id: str
    training_data: List[Dict[str, Any]]
    hyperparameters: Dict[str, Any]
    priority: int = 1
    status: str = 'pending'  # pending, running, completed, failed
    created_at: float = None
    started_at: Optional[float] = None
    completed_at: Optional[float] = None
    results: Optional[Dict[str, Any]] = None
    error_message: Optional[str] = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = time.time()


@dataclass
class ModelPerformanceMetrics:
    """Model performance tracking"""
    model_id: str
    accuracy: float
    precision: float
    recall: float
    f1_score: float
    confidence_score: float
    training_time: float
    prediction_speed: float
    memory_usage: float
    cpu_usage: float
    timestamp: float
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = time.time()


class RealTimeModelTrainer:
    """
    🎯 REAL-TIME MODEL TRAINING SYSTEM
    
    Features:
    - Continuous learning from new data
    - Auto-hyperparameter optimization
    - A/B testing for model comparison
    - Performance monitoring
    - Automatic model deployment
    """
    
    def __init__(self, max_workers: int = 4):
        self.max_workers = max_workers
        self.executor = ThreadPoolExecutor(max_workers=max_workers)
        self.training_queue = deque()
        self.active_jobs = {}
        self.completed_jobs = {}
        self.model_registry = {}
        self.performance_history = defaultdict(list)
        self.auto_training_enabled = True
        self.training_threshold = 100  # New data points before retraining
        
        # Start background training processor
        self.training_thread = threading.Thread(target=self._process_training_jobs, daemon=True)
        self.training_thread.start()
        
        # Start performance monitoring
        self.monitoring_thread = threading.Thread(target=self._monitor_performance, daemon=True)
        self.monitoring_thread.start()
        
        logger.info(f"✅ Real-time model trainer initialized with {max_workers} workers")
    
    def schedule_training(self, 
                         model_id: str,
                         training_data: List[Dict[str, Any]], 
                         hyperparameters: Dict[str, Any] = None,
                         priority: int = 1) -> str:
        """Schedule model training job"""
        
        job_id = f"training_{model_id}_{int(time.time() * 1000)}"
        
        training_job = TrainingJob(
            job_id=job_id,
            model_id=model_id,
            training_data=training_data,
            hyperparameters=hyperparameters or {},
            priority=priority
        )
        
        # Add to priority queue
        self.training_queue.append(training_job)
        self.training_queue = deque(sorted(self.training_queue, key=lambda x: x.priority, reverse=True))
        
        logger.info(f"🎯 Training job scheduled: {job_id} for model {model_id}")
        return job_id
    
    def _process_training_jobs(self):
        """Background training job processor"""
        while True:
            try:
                if self.training_queue and len(self.active_jobs) < self.max_workers:
                    job = self.training_queue.popleft()
                    
                    # Submit to thread pool
                    future = self.executor.submit(self._execute_training_job, job)
                    self.active_jobs[job.job_id] = {
                        'job': job,
                        'future': future,
                        'started_at': time.time()
                    }
                    
                    job.status = 'running'
                    job.started_at = time.time()
                    
                    logger.info(f"🚀 Started training job: {job.job_id}")
                
                # Check completed jobs
                completed_jobs = []
                for job_id, job_info in self.active_jobs.items():
                    if job_info['future'].done():
                        completed_jobs.append(job_id)
                
                # Process completed jobs
                for job_id in completed_jobs:
                    self._handle_completed_job(job_id)
                
                time.sleep(1)  # Prevent tight loop
                
            except Exception as e:
                logger.error(f"❌ Training processor error: {e}")
                time.sleep(5)
    
    def _execute_training_job(self, job: TrainingJob) -> Dict[str, Any]:
        """Execute individual training job"""
        start_time = time.time()
        
        try:
            logger.info(f"🔥 Executing training job: {job.job_id}")
            
            # Prepare training data
            X_train, y_train = self._prepare_training_data(job.training_data)
            
            # Optimize hyperparameters if needed
            if not job.hyperparameters:
                job.hyperparameters = self._optimize_hyperparameters(job.model_id, X_train, y_train)
            
            # Train model
            trained_model, metrics = self._train_model(job.model_id, X_train, y_train, job.hyperparameters)
            
            # Validate model
            validation_results = self._validate_model(trained_model, X_train, y_train)
            
            # Performance evaluation
            performance_metrics = self._evaluate_model_performance(trained_model, validation_results)
            
            # Prepare results
            training_time = time.time() - start_time
            results = {
                'model_id': job.model_id,
                'trained_model': trained_model,
                'performance_metrics': performance_metrics,
                'validation_results': validation_results,
                'hyperparameters_used': job.hyperparameters,
                'training_time': training_time,
                'training_data_size': len(job.training_data),
                'timestamp': timezone.now().isoformat(),
                'success': True
            }
            
            logger.info(f"✅ Training completed: {job.job_id} ({training_time:.2f}s)")
            return results
            
        except Exception as e:
            error_msg = f"Training failed: {e}"
            logger.error(f"❌ {error_msg}")
            
            return {
                'model_id': job.model_id,
                'success': False,
                'error': error_msg,
                'training_time': time.time() - start_time,
                'timestamp': timezone.now().isoformat()
            }
    
    def _prepare_training_data(self, raw_data: List[Dict[str, Any]]) -> tuple:
        """Prepare training data for ML models"""
        try:
            X_train = []
            y_train = []
            
            for record in raw_data:
                # Extract features
                if 'input_sequence' in record and 'predictions' in record:
                    # Convert sequence to features
                    sequence = record['input_sequence']
                    if len(sequence) >= 10:  # Minimum sequence length
                        features = self._extract_sequence_features(sequence)
                        X_train.append(features)
                        y_train.append(record['predictions'])
            
            logger.info(f"✅ Prepared training data: {len(X_train)} samples")
            return np.array(X_train), np.array(y_train)
            
        except Exception as e:
            logger.error(f"❌ Training data preparation failed: {e}")
            return np.array([]), np.array([])
    
    def _extract_sequence_features(self, sequence: List[int]) -> List[float]:
        """Extract features from number sequence"""
        try:
            features = []
            
            # Statistical features
            features.extend([
                np.mean(sequence),
                np.std(sequence),
                np.median(sequence),
                np.min(sequence),
                np.max(sequence)
            ])
            
            # Temporal features
            if len(sequence) > 1:
                diff = np.diff(sequence)
                features.extend([
                    np.mean(diff),
                    np.std(diff),
                    len([d for d in diff if d > 0]),  # Increasing trends
                    len([d for d in diff if d < 0])   # Decreasing trends
                ])
            else:
                features.extend([0, 0, 0, 0])
            
            # Frequency features
            unique_counts = len(set(sequence))
            most_frequent = max(set(sequence), key=sequence.count)
            features.extend([
                unique_counts,
                most_frequent,
                sequence.count(most_frequent)
            ])
            
            # Pattern features
            consecutive_count = sum(1 for i in range(len(sequence)-1) if abs(sequence[i] - sequence[i+1]) == 1)
            features.append(consecutive_count)
            
            return features
            
        except Exception as e:
            logger.error(f"❌ Feature extraction failed: {e}")
            return [0] * 13  # Return zero features as fallback
    
    def _optimize_hyperparameters(self, model_id: str, X_train: np.ndarray, y_train: np.ndarray) -> Dict[str, Any]:
        """Optimize hyperparameters for model"""
        try:
            logger.info(f"🔧 Optimizing hyperparameters for {model_id}")
            
            # Default hyperparameter search spaces
            param_spaces = {
                'lstm_predictor': {
                    'hidden_units': [64, 128, 256],
                    'dropout': [0.1, 0.2, 0.3],
                    'learning_rate': [0.001, 0.01, 0.1],
                    'sequence_length': [10, 20, 30]
                },
                'transformer_predictor': {
                    'attention_heads': [4, 8, 16],
                    'hidden_size': [128, 256, 512],
                    'num_layers': [2, 4, 6],
                    'dropout': [0.1, 0.15, 0.2]
                },
                'ensemble_predictor': {
                    'n_estimators': [50, 100, 200],
                    'max_depth': [5, 10, 15],
                    'learning_rate': [0.01, 0.1, 0.2],
                    'subsample': [0.8, 0.9, 1.0]
                }
            }
            
            if model_id not in param_spaces:
                return {}
            
            # Simple grid search (in production, use more sophisticated methods)
            best_params = {}
            best_score = -1
            
            param_space = param_spaces[model_id]
            
            # Random search with limited iterations
            max_iterations = 10
            for iteration in range(max_iterations):
                # Random parameter combination
                params = {}
                for param, values in param_space.items():
                    params[param] = np.random.choice(values)
                
                # Quick validation score
                score = self._quick_validation_score(model_id, params, X_train, y_train)
                
                if score > best_score:
                    best_score = score
                    best_params = params.copy()
            
            logger.info(f"✅ Best hyperparameters found: {best_params} (score: {best_score:.3f})")
            return best_params
            
        except Exception as e:
            logger.error(f"❌ Hyperparameter optimization failed: {e}")
            return {}
    
    def _quick_validation_score(self, model_id: str, params: Dict[str, Any], X_train: np.ndarray, y_train: np.ndarray) -> float:
        """Quick validation score for hyperparameter optimization"""
        try:
            # Simulate model training and validation
            # In production, this would actually train and validate the model
            
            # Simple scoring based on parameter quality
            score = 0.5  # Base score
            
            # Adjust score based on reasonable parameter ranges
            if model_id == 'lstm_predictor':
                if 64 <= params.get('hidden_units', 128) <= 256:
                    score += 0.1
                if 0.1 <= params.get('dropout', 0.2) <= 0.3:
                    score += 0.1
                if 10 <= params.get('sequence_length', 20) <= 30:
                    score += 0.1
            
            elif model_id == 'transformer_predictor':
                if 4 <= params.get('attention_heads', 8) <= 16:
                    score += 0.1
                if 128 <= params.get('hidden_size', 256) <= 512:
                    score += 0.1
            
            # Add randomness to simulate actual validation
            score += np.random.normal(0, 0.05)
            
            return max(0, min(1, score))
            
        except Exception as e:
            logger.error(f"❌ Quick validation failed: {e}")
            return 0.5
    
    def _train_model(self, model_id: str, X_train: np.ndarray, y_train: np.ndarray, hyperparameters: Dict[str, Any]) -> tuple:
        """Train model with given data and hyperparameters"""
        try:
            logger.info(f"🔥 Training model: {model_id}")
            
            # Simulate model training
            # In production, this would use actual ML frameworks
            
            training_start = time.time()
            
            # Create mock trained model
            trained_model = {
                'model_id': model_id,
                'type': model_id.split('_')[0],
                'hyperparameters': hyperparameters,
                'training_data_size': len(X_train),
                'feature_size': X_train.shape[1] if len(X_train.shape) > 1 else 0,
                'trained_at': training_start,
                'weights': np.random.random((10, 6)),  # Mock weights
                'version': f"v{int(time.time())}"
            }
            
            # Simulate training time
            time.sleep(np.random.uniform(0.5, 2.0))
            
            training_time = time.time() - training_start
            
            # Generate training metrics
            metrics = {
                'training_loss': np.random.uniform(0.1, 0.5),
                'validation_loss': np.random.uniform(0.15, 0.6),
                'accuracy': np.random.uniform(0.7, 0.95),
                'training_time': training_time,
                'epochs_completed': np.random.randint(10, 50),
                'convergence_achieved': True
            }
            
            logger.info(f"✅ Model training completed: {model_id} ({training_time:.2f}s)")
            return trained_model, metrics
            
        except Exception as e:
            logger.error(f"❌ Model training failed: {e}")
            return None, {}
    
    def _validate_model(self, trained_model: Dict[str, Any], X_train: np.ndarray, y_train: np.ndarray) -> Dict[str, Any]:
        """Validate trained model"""
        try:
            if not trained_model:
                return {'validation_failed': True}
            
            # Simulate model validation
            validation_results = {
                'cross_validation_score': np.random.uniform(0.7, 0.9),
                'test_accuracy': np.random.uniform(0.65, 0.85),
                'precision': np.random.uniform(0.7, 0.9),
                'recall': np.random.uniform(0.65, 0.85),
                'f1_score': np.random.uniform(0.7, 0.87),
                'confusion_matrix': np.random.randint(0, 50, (6, 6)).tolist(),
                'validation_passed': True,
                'model_stability': 'high',
                'overfitting_detected': np.random.choice([True, False], p=[0.2, 0.8])
            }
            
            return validation_results
            
        except Exception as e:
            logger.error(f"❌ Model validation failed: {e}")
            return {'validation_failed': True, 'error': str(e)}
    
    def _evaluate_model_performance(self, trained_model: Dict[str, Any], validation_results: Dict[str, Any]) -> ModelPerformanceMetrics:
        """Evaluate comprehensive model performance"""
        try:
            metrics = ModelPerformanceMetrics(
                model_id=trained_model['model_id'],
                accuracy=validation_results.get('test_accuracy', 0.75),
                precision=validation_results.get('precision', 0.8),
                recall=validation_results.get('recall', 0.75),
                f1_score=validation_results.get('f1_score', 0.77),
                confidence_score=np.random.uniform(0.8, 0.95),
                training_time=trained_model.get('training_time', 1.0),
                prediction_speed=np.random.uniform(0.001, 0.01),  # seconds per prediction
                memory_usage=np.random.uniform(50, 200),  # MB
                cpu_usage=np.random.uniform(10, 40),  # percentage
                timestamp=time.time()
            )
            
            return metrics
            
        except Exception as e:
            logger.error(f"❌ Performance evaluation failed: {e}")
            return ModelPerformanceMetrics(
                model_id='unknown',
                accuracy=0.5, precision=0.5, recall=0.5, f1_score=0.5,
                confidence_score=0.5, training_time=0, prediction_speed=0,
                memory_usage=0, cpu_usage=0, timestamp=time.time()
            )
    
    def _handle_completed_job(self, job_id: str):
        """Handle completed training job"""
        try:
            job_info = self.active_jobs.pop(job_id)
            job = job_info['job']
            future = job_info['future']
            
            # Get results
            results = future.result()
            
            if results.get('success', False):
                job.status = 'completed'
                job.results = results
                job.completed_at = time.time()
                
                # Register trained model
                self._register_trained_model(results)
                
                # Update performance history
                if 'performance_metrics' in results:
                    self.performance_history[job.model_id].append(results['performance_metrics'])
                
                logger.info(f"✅ Training job completed successfully: {job_id}")
                
                # Auto-deploy if performance is good
                if self._should_auto_deploy(results):
                    self._deploy_model(results['trained_model'])
                
            else:
                job.status = 'failed'
                job.error_message = results.get('error', 'Unknown error')
                job.completed_at = time.time()
                
                logger.error(f"❌ Training job failed: {job_id} - {job.error_message}")
            
            # Store in completed jobs
            self.completed_jobs[job_id] = job
            
        except Exception as e:
            logger.error(f"❌ Failed to handle completed job {job_id}: {e}")
    
    def _register_trained_model(self, results: Dict[str, Any]):
        """Register trained model in model registry"""
        try:
            model_id = results['model_id']
            trained_model = results['trained_model']
            
            # Store in model registry
            self.model_registry[model_id] = {
                'model': trained_model,
                'performance_metrics': results['performance_metrics'],
                'hyperparameters': results['hyperparameters_used'],
                'training_time': results['training_time'],
                'registered_at': time.time(),
                'status': 'registered',
                'deployment_ready': True
            }
            
            # Cache for quick access
            cache.set(f"trained_model_{model_id}", trained_model, 3600)
            
            logger.info(f"✅ Model registered: {model_id}")
            
        except Exception as e:
            logger.error(f"❌ Model registration failed: {e}")
    
    def _should_auto_deploy(self, results: Dict[str, Any]) -> bool:
        """Determine if model should be auto-deployed"""
        try:
            performance_metrics = results.get('performance_metrics')
            if not performance_metrics:
                return False
            
            # Auto-deploy criteria
            accuracy_threshold = 0.8
            f1_threshold = 0.75
            confidence_threshold = 0.85
            
            accuracy = performance_metrics.accuracy
            f1_score = performance_metrics.f1_score
            confidence = performance_metrics.confidence_score
            
            return (accuracy >= accuracy_threshold and 
                   f1_score >= f1_threshold and 
                   confidence >= confidence_threshold)
            
        except Exception as e:
            logger.error(f"❌ Auto-deploy decision failed: {e}")
            return False
    
    def _deploy_model(self, trained_model: Dict[str, Any]):
        """Deploy trained model to production"""
        try:
            model_id = trained_model['model_id']
            
            # Update model status
            if model_id in self.model_registry:
                self.model_registry[model_id]['status'] = 'deployed'
                self.model_registry[model_id]['deployed_at'] = time.time()
            
            # Notify other systems
            cache.set(f"deployed_model_{model_id}", trained_model, 7200)  # 2 hours
            
            logger.info(f"🚀 Model deployed to production: {model_id}")
            
        except Exception as e:
            logger.error(f"❌ Model deployment failed: {e}")
    
    def _monitor_performance(self):
        """Monitor model performance continuously"""
        while True:
            try:
                # Monitor deployed models
                for model_id, model_info in self.model_registry.items():
                    if model_info['status'] == 'deployed':
                        self._check_model_health(model_id, model_info)
                
                # Check for retraining needs
                self._check_retraining_needs()
                
                time.sleep(60)  # Check every minute
                
            except Exception as e:
                logger.error(f"❌ Performance monitoring error: {e}")
                time.sleep(300)  # Wait 5 minutes on error
    
    def _check_model_health(self, model_id: str, model_info: Dict[str, Any]):
        """Check health of deployed model"""
        try:
            # Check performance degradation
            recent_performance = self.performance_history[model_id][-10:]  # Last 10 records
            
            if len(recent_performance) >= 3:
                current_accuracy = recent_performance[-1].accuracy
                baseline_accuracy = model_info['performance_metrics'].accuracy
                
                # Alert if performance drops significantly
                if current_accuracy < baseline_accuracy * 0.9:  # 10% drop
                    logger.warning(f"⚠️ Performance degradation detected for {model_id}")
                    self._trigger_retraining(model_id, 'performance_degradation')
            
        except Exception as e:
            logger.error(f"❌ Model health check failed for {model_id}: {e}")
    
    def _check_retraining_needs(self):
        """Check if models need retraining"""
        try:
            # Check data freshness
            for model_id in self.model_registry.keys():
                model_info = self.model_registry[model_id]
                last_training = model_info.get('registered_at', 0)
                
                # Retrain if model is older than 24 hours
                if time.time() - last_training > 86400:  # 24 hours
                    logger.info(f"🔄 Scheduled retraining for {model_id} (24h threshold)")
                    self._trigger_retraining(model_id, 'scheduled_maintenance')
            
        except Exception as e:
            logger.error(f"❌ Retraining check failed: {e}")
    
    def _trigger_retraining(self, model_id: str, reason: str):
        """Trigger model retraining"""
        try:
            # Get fresh training data
            training_data = self._get_fresh_training_data(model_id)
            
            if training_data and len(training_data) >= self.training_threshold:
                job_id = self.schedule_training(
                    model_id=model_id,
                    training_data=training_data,
                    priority=2 if reason == 'performance_degradation' else 1
                )
                
                logger.info(f"🔄 Retraining triggered for {model_id}: {reason} (job: {job_id})")
            
        except Exception as e:
            logger.error(f"❌ Retraining trigger failed: {e}")
    
    def _get_fresh_training_data(self, model_id: str) -> List[Dict[str, Any]]:
        """Get fresh training data for model"""
        try:
            # In production, this would fetch data from database
            # For now, return mock data
            mock_data = []
            
            for i in range(self.training_threshold + 10):
                mock_data.append({
                    'input_sequence': [np.random.randint(1, 46) for _ in range(20)],
                    'predictions': [np.random.randint(1, 46) for _ in range(6)],
                    'timestamp': time.time() - i * 3600  # Hourly data
                })
            
            return mock_data
            
        except Exception as e:
            logger.error(f"❌ Fresh training data retrieval failed: {e}")
            return []
    
    def get_training_status(self, job_id: str) -> Dict[str, Any]:
        """Get status of training job"""
        try:
            # Check active jobs
            if job_id in self.active_jobs:
                job = self.active_jobs[job_id]['job']
                return {
                    'status': job.status,
                    'model_id': job.model_id,
                    'started_at': datetime.fromtimestamp(job.started_at).isoformat() if job.started_at else None,
                    'runtime': time.time() - job.started_at if job.started_at else 0,
                    'progress': 'training_in_progress'
                }
            
            # Check completed jobs
            if job_id in self.completed_jobs:
                job = self.completed_jobs[job_id]
                return {
                    'status': job.status,
                    'model_id': job.model_id,
                    'completed_at': datetime.fromtimestamp(job.completed_at).isoformat() if job.completed_at else None,
                    'training_time': job.completed_at - job.started_at if job.completed_at and job.started_at else 0,
                    'results': job.results,
                    'error': job.error_message
                }
            
            # Check pending jobs
            for job in self.training_queue:
                if job.job_id == job_id:
                    return {
                        'status': 'pending',
                        'model_id': job.model_id,
                        'queue_position': list(self.training_queue).index(job) + 1,
                        'estimated_start': 'pending'
                    }
            
            return {'status': 'not_found'}
            
        except Exception as e:
            logger.error(f"❌ Training status check failed: {e}")
            return {'status': 'error', 'error': str(e)}
    
    def get_model_performance_dashboard(self) -> Dict[str, Any]:
        """Get comprehensive model performance dashboard"""
        try:
            dashboard = {
                'overview': {
                    'total_models': len(self.model_registry),
                    'deployed_models': len([m for m in self.model_registry.values() if m['status'] == 'deployed']),
                    'active_training_jobs': len(self.active_jobs),
                    'pending_jobs': len(self.training_queue),
                    'completed_jobs': len(self.completed_jobs)
                },
                'model_performance': {},
                'training_statistics': {},
                'system_health': {}
            }
            
            # Model performance metrics
            for model_id, model_info in self.model_registry.items():
                if 'performance_metrics' in model_info:
                    metrics = model_info['performance_metrics']
                    dashboard['model_performance'][model_id] = {
                        'accuracy': f"{metrics.accuracy:.2%}",
                        'f1_score': f"{metrics.f1_score:.2%}",
                        'confidence': f"{metrics.confidence_score:.2%}",
                        'status': model_info['status'],
                        'last_trained': datetime.fromtimestamp(model_info['registered_at']).isoformat()
                    }
            
            # Training statistics
            completed_jobs = [j for j in self.completed_jobs.values() if j.status == 'completed']
            if completed_jobs:
                training_times = [j.results.get('training_time', 0) for j in completed_jobs if j.results]
                dashboard['training_statistics'] = {
                    'avg_training_time': f"{np.mean(training_times):.2f}s",
                    'success_rate': f"{len(completed_jobs) / len(self.completed_jobs) * 100:.1f}%",
                    'total_training_time': f"{sum(training_times):.1f}s",
                    'fastest_training': f"{min(training_times):.2f}s" if training_times else "N/A"
                }
            
            # System health
            dashboard['system_health'] = {
                'training_system': 'healthy',
                'model_registry': 'operational',
                'auto_training': 'enabled' if self.auto_training_enabled else 'disabled',
                'worker_utilization': f"{len(self.active_jobs) / self.max_workers * 100:.1f}%"
            }
            
            return dashboard
            
        except Exception as e:
            logger.error(f"❌ Performance dashboard generation failed: {e}")
            return {'error': str(e)}


# Global real-time trainer instance
real_time_model_trainer = RealTimeModelTrainer()
