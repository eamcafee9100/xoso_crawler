#!/usr/bin/env python3
"""
🚀 MACHINE LEARNING ENSEMBLE SERVICE - Advanced ML Models cho Hybrid Scoring
Replaces simple weighted averages with sophisticated ML ensemble approaches
"""

import numpy as np
import logging
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from datetime import date, datetime
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.neural_network import MLPRegressor
from sklearn.linear_model import LinearRegression, Ridge
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import cross_val_score
import warnings
warnings.filterwarnings('ignore')

logger = logging.getLogger(__name__)

@dataclass(frozen=True)
class ModelPrediction:
    """Immutable data contract for model prediction"""
    model_name: str
    prediction: float
    confidence: float
    feature_importance: Dict[str, float]
    cross_val_score: float

@dataclass(frozen=True)
class EnsembleResult:
    """Immutable data contract for ensemble result"""
    final_score: float
    model_predictions: List[ModelPrediction]
    ensemble_confidence: float
    feature_analysis: Dict[str, float]
    model_weights: Dict[str, float]
    meta_learning_score: float

@dataclass(frozen=True)
class MarketFeatures:
    """Immutable data contract for market features"""
    regime: str
    volatility: float
    trend_strength: float
    correlation_level: float
    data_quality: float
    temporal_consistency: float

class MLEnsembleService:
    """
    🚀 REVOLUTIONARY: Machine Learning Ensemble Service
    Advanced ML models for scoring instead of simple weighted averages
    """
    
    def __init__(self):
        self.models = {}
        self.scaler = StandardScaler()
        self.is_fitted = False
        self.feature_names = []
        
    def initialize_models(self, regime: str = 'normal') -> Dict[str, Any]:
        """
        Initialize ML models based on market regime
        
        Args:
            regime: Market regime ('bull', 'bear', 'volatile', 'sideways')
            
        Returns:
            Dict[str, Any]: Initialized models
        """
        try:
            # Regime-specific model configurations
            if regime == 'volatile':
                # More conservative, stable models for volatile markets
                models = {
                    'random_forest': RandomForestRegressor(
                        n_estimators=150, max_depth=6, min_samples_split=10,
                        random_state=42, n_jobs=-1
                    ),
                    'gradient_boost': GradientBoostingRegressor(
                        n_estimators=100, learning_rate=0.05, max_depth=4,
                        random_state=42
                    ),
                    'ridge_regression': Ridge(alpha=1.0, random_state=42),
                    'neural_net': MLPRegressor(
                        hidden_layer_sizes=(50, 25), max_iter=500,
                        random_state=42, early_stopping=True
                    )
                }
            elif regime == 'bull':
                # More aggressive models for bull markets
                models = {
                    'random_forest': RandomForestRegressor(
                        n_estimators=200, max_depth=8, min_samples_split=5,
                        random_state=42, n_jobs=-1
                    ),
                    'gradient_boost': GradientBoostingRegressor(
                        n_estimators=150, learning_rate=0.1, max_depth=6,
                        random_state=42
                    ),
                    'neural_net': MLPRegressor(
                        hidden_layer_sizes=(100, 50, 25), max_iter=1000,
                        random_state=42, early_stopping=True
                    ),
                    'linear_regression': LinearRegression()
                }
            else:
                # Balanced models for normal/bear/sideways markets
                models = {
                    'random_forest': RandomForestRegressor(
                        n_estimators=100, max_depth=7, min_samples_split=8,
                        random_state=42, n_jobs=-1
                    ),
                    'gradient_boost': GradientBoostingRegressor(
                        n_estimators=120, learning_rate=0.08, max_depth=5,
                        random_state=42
                    ),
                    'neural_net': MLPRegressor(
                        hidden_layer_sizes=(75, 35), max_iter=800,
                        random_state=42, early_stopping=True
                    ),
                    'ridge_regression': Ridge(alpha=0.5, random_state=42)
                }
            
            self.models = models
            logger.info(f"✅ Initialized {len(models)} ML models for regime: {regime}")
            return models
            
        except Exception as e:
            logger.error(f"❌ Error initializing models: {e}")
            return {}
    
    def extract_comprehensive_features(self, short_analysis: Dict[str, Any], 
                                     long_analysis: Dict[str, Any],
                                     market_features: MarketFeatures) -> np.ndarray:
        """
        Extract comprehensive features for ML models
        
        Args:
            short_analysis: Short-term analysis results
            long_analysis: Long-term analysis results  
            market_features: Market feature data
            
        Returns:
            np.ndarray: Feature matrix
        """
        try:
            features = []
            feature_names = []
            
            # Short-term features
            short_score = short_analysis.get('score', 0.0)
            short_confidence = short_analysis.get('confidence', 0.0)
            short_hit_rate = short_analysis.get('expected_hit_rate', 0.0)
            short_momentum = short_analysis.get('momentum', 0.0)
            short_consistency = short_analysis.get('consistency', 0.0)
            
            features.extend([short_score, short_confidence, short_hit_rate, short_momentum, short_consistency])
            feature_names.extend(['short_score', 'short_confidence', 'short_hit_rate', 'short_momentum', 'short_consistency'])
            
            # Long-term features
            long_score = long_analysis.get('score', 0.0)
            long_confidence = long_analysis.get('confidence', 0.0)
            long_hit_rate = long_analysis.get('expected_hit_rate', 0.0)
            long_stability = long_analysis.get('stability', 0.0)
            long_trend = long_analysis.get('trend', 0.0)
            
            features.extend([long_score, long_confidence, long_hit_rate, long_stability, long_trend])
            feature_names.extend(['long_score', 'long_confidence', 'long_hit_rate', 'long_stability', 'long_trend'])
            
            # Market features
            features.extend([
                market_features.volatility,
                market_features.trend_strength,
                market_features.correlation_level,
                market_features.data_quality,
                market_features.temporal_consistency
            ])
            feature_names.extend(['volatility', 'trend_strength', 'correlation_level', 'data_quality', 'temporal_consistency'])
            
            # Interaction features (non-linear combinations)
            score_ratio = short_score / max(long_score, 0.001)  # Avoid division by zero
            confidence_diff = abs(short_confidence - long_confidence)
            hit_rate_momentum = short_hit_rate * short_momentum
            stability_quality = long_stability * market_features.data_quality
            
            features.extend([score_ratio, confidence_diff, hit_rate_momentum, stability_quality])
            feature_names.extend(['score_ratio', 'confidence_diff', 'hit_rate_momentum', 'stability_quality'])
            
            # Regime encoding (one-hot)
            regime_mapping = {'bull': [1, 0, 0, 0], 'bear': [0, 1, 0, 0], 'volatile': [0, 0, 1, 0], 'sideways': [0, 0, 0, 1]}
            regime_encoded = regime_mapping.get(market_features.regime, [0, 0, 0, 1])
            features.extend(regime_encoded)
            feature_names.extend(['regime_bull', 'regime_bear', 'regime_volatile', 'regime_sideways'])
            
            self.feature_names = feature_names
            
            return np.array(features).reshape(1, -1)  # Single sample
            
        except Exception as e:
            logger.error(f"❌ Error extracting features: {e}")
            # Return zero features as fallback
            fallback_features = np.zeros((1, 20))  # Minimum feature count
            self.feature_names = [f'feature_{i}' for i in range(20)]
            return fallback_features
    
    def train_meta_learner(self, training_data: List[Tuple[np.ndarray, float]], 
                          validation_data: List[Tuple[np.ndarray, float]]) -> Any:
        """
        Train meta-learner for model combination
        
        Args:
            training_data: List of (features, target) tuples
            validation_data: List of (features, target) tuples
            
        Returns:
            Trained meta-learner model
        """
        try:
            if len(training_data) < 10:  # Minimum training samples
                logger.warning("⚠️ Insufficient training data for meta-learner")
                return None
            
            # Prepare training data
            X_train = np.vstack([x[0] for x in training_data])
            y_train = np.array([x[1] for x in training_data])
            
            # Train meta-learner (simple Ridge regression)
            meta_learner = Ridge(alpha=0.1, random_state=42)
            meta_learner.fit(X_train, y_train)
            
            # Validate if validation data available
            if validation_data and len(validation_data) >= 3:
                X_val = np.vstack([x[0] for x in validation_data])
                y_val = np.array([x[1] for x in validation_data])
                
                val_score = meta_learner.score(X_val, y_val)
                logger.info(f"✅ Meta-learner validation score: {val_score:.3f}")
            
            return meta_learner
            
        except Exception as e:
            logger.error(f"❌ Error training meta-learner: {e}")
            return None
    
    def ml_ensemble_scoring_v3(self, short_analysis: Dict[str, Any],
                              long_analysis: Dict[str, Any],
                              validation_results: Dict[str, Any],
                              market_features: MarketFeatures) -> EnsembleResult:
        """
        🚀 REVOLUTIONARY: ML ensemble scoring to replace simple weighted average
        
        Args:
            short_analysis: Short-term analysis
            long_analysis: Long-term analysis
            validation_results: Validation results
            market_features: Market features
            
        Returns:
            EnsembleResult: ML ensemble prediction result
        """
        try:
            # Initialize models for current regime
            self.initialize_models(market_features.regime)
            
            # Extract features
            features = self.extract_comprehensive_features(short_analysis, long_analysis, market_features)
            
            # Get individual model predictions
            model_predictions = []
            
            # Synthetic training data for model fitting (in production, use real historical data)
            X_synthetic = self._generate_synthetic_training_data(features)
            y_synthetic = self._generate_synthetic_targets(X_synthetic, short_analysis, long_analysis)
            
            # Scale features
            X_scaled = self.scaler.fit_transform(X_synthetic)
            features_scaled = self.scaler.transform(features)
            
            for model_name, model in self.models.items():
                try:
                    # Train model on synthetic data
                    model.fit(X_scaled, y_synthetic)
                    
                    # Make prediction
                    prediction = model.predict(features_scaled)[0]
                    
                    # Calculate cross-validation score
                    cv_scores = cross_val_score(model, X_scaled, y_synthetic, cv=3, scoring='r2')
                    cv_score = np.mean(cv_scores)
                    
                    # Calculate confidence based on cross-validation
                    confidence = max(0.1, min(0.95, cv_score)) if cv_score > 0 else 0.1
                    
                    # Feature importance (if available)
                    feature_importance = {}
                    if hasattr(model, 'feature_importances_'):
                        for i, importance in enumerate(model.feature_importances_):
                            if i < len(self.feature_names):
                                feature_importance[self.feature_names[i]] = importance
                    elif hasattr(model, 'coef_'):
                        for i, coef in enumerate(model.coef_):
                            if i < len(self.feature_names):
                                feature_importance[self.feature_names[i]] = abs(coef)
                    
                    model_predictions.append(ModelPrediction(
                        model_name=model_name,
                        prediction=prediction,
                        confidence=confidence,
                        feature_importance=feature_importance,
                        cross_val_score=cv_score
                    ))
                    
                except Exception as model_error:
                    logger.warning(f"⚠️ Model {model_name} failed: {model_error}")
                    continue
            
            if not model_predictions:
                raise ValueError("All models failed to make predictions")
            
            # Calculate ensemble prediction using weighted average by confidence
            total_weight = sum(pred.confidence for pred in model_predictions)
            if total_weight > 0:
                final_score = sum(pred.prediction * pred.confidence for pred in model_predictions) / total_weight
            else:
                final_score = np.mean([pred.prediction for pred in model_predictions])
            
            # Calculate ensemble confidence
            ensemble_confidence = np.mean([pred.confidence for pred in model_predictions])
            
            # Calculate model weights
            model_weights = {}
            if total_weight > 0:
                for pred in model_predictions:
                    model_weights[pred.model_name] = pred.confidence / total_weight
            else:
                equal_weight = 1.0 / len(model_predictions)
                for pred in model_predictions:
                    model_weights[pred.model_name] = equal_weight
            
            # Aggregate feature importance
            feature_analysis = {}
            for pred in model_predictions:
                for feature, importance in pred.feature_importance.items():
                    if feature not in feature_analysis:
                        feature_analysis[feature] = 0.0
                    feature_analysis[feature] += importance * model_weights[pred.model_name]
            
            # Meta-learning score (placeholder - would use real meta-learner in production)
            meta_learning_score = final_score * 0.9 + ensemble_confidence * 0.1
            
            logger.info(f"✅ ML ensemble scoring completed: {len(model_predictions)} models, final score: {final_score:.3f}")
            
            return EnsembleResult(
                final_score=final_score,
                model_predictions=model_predictions,
                ensemble_confidence=ensemble_confidence,
                feature_analysis=feature_analysis,
                model_weights=model_weights,
                meta_learning_score=meta_learning_score
            )
            
        except Exception as e:
            logger.error(f"❌ ML ensemble scoring failed: {e}")
            
            # Fallback to simple average
            fallback_score = (short_analysis.get('score', 0.0) + long_analysis.get('score', 0.0)) / 2
            fallback_confidence = (short_analysis.get('confidence', 0.0) + long_analysis.get('confidence', 0.0)) / 2
            
            return EnsembleResult(
                final_score=fallback_score,
                model_predictions=[],
                ensemble_confidence=fallback_confidence,
                feature_analysis={},
                model_weights={},
                meta_learning_score=fallback_score
            )
    
    def _generate_synthetic_training_data(self, features: np.ndarray, n_samples: int = 100) -> np.ndarray:
        """
        Generate synthetic training data for model fitting
        (In production, this would be replaced with real historical data)
        """
        try:
            # Create variations around the input features
            base_features = features[0]
            n_features = len(base_features)
            
            synthetic_data = []
            for _ in range(n_samples):
                # Add noise to create variations
                noise = np.random.normal(0, 0.1, n_features)
                synthetic_sample = base_features + noise
                
                # Ensure features stay in reasonable bounds
                synthetic_sample = np.clip(synthetic_sample, 0, 1)
                
                synthetic_data.append(synthetic_sample)
            
            return np.array(synthetic_data)
            
        except Exception as e:
            logger.error(f"❌ Error generating synthetic data: {e}")
            return np.random.random((n_samples, features.shape[1]))
    
    def _generate_synthetic_targets(self, X: np.ndarray, 
                                  short_analysis: Dict[str, Any],
                                  long_analysis: Dict[str, Any]) -> np.ndarray:
        """
        Generate synthetic targets based on analysis results
        """
        try:
            # Create targets based on feature combinations
            targets = []
            
            short_score = short_analysis.get('score', 50.0)
            long_score = long_analysis.get('score', 50.0)
            base_target = (short_score + long_score) / 2
            
            for features in X:
                # Simple formula combining multiple features
                target = base_target
                
                # Add variations based on features
                if len(features) >= 5:
                    target += features[0] * 10  # short_score influence
                    target += features[5] * 8   # long_score influence
                    target -= features[10] * 5  # volatility penalty
                
                # Add some noise
                target += np.random.normal(0, 2)
                
                # Keep in reasonable bounds
                target = max(0, min(100, target))
                
                targets.append(target)
            
            return np.array(targets)
            
        except Exception as e:
            logger.error(f"❌ Error generating synthetic targets: {e}")
            return np.random.uniform(30, 70, len(X))
    
    def select_models_by_regime(self, models: Dict[str, Any], regime: str) -> Dict[str, Any]:
        """
        Select appropriate models based on market regime
        
        Args:
            models: Available models
            regime: Market regime
            
        Returns:
            Dict[str, Any]: Selected models for the regime
        """
        regime_preferences = {
            'bull': ['random_forest', 'gradient_boost', 'neural_net'],
            'bear': ['ridge_regression', 'random_forest'],
            'volatile': ['ridge_regression', 'gradient_boost'],
            'sideways': ['random_forest', 'neural_net', 'ridge_regression']
        }
        
        preferred_models = regime_preferences.get(regime, list(models.keys()))
        
        return {name: model for name, model in models.items() if name in preferred_models}
