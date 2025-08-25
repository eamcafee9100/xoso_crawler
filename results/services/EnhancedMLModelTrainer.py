"""
Enhanced ML Model Trainer với cải tiến hiệu suất và tương thích
Đồng bộ với MLModelService để sử dụng 12 features chuẩn
"""

import numpy as np
import pandas as pd
import pickle
import joblib
import os
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Tuple
import sklearn
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.neural_network import MLPRegressor
from sklearn.preprocessing import RobustScaler, StandardScaler
from sklearn.model_selection import train_test_split, cross_val_score, GridSearchCV
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
import warnings

from django.conf import settings
from django.utils import timezone
from ..models import KetQuaXoSo

# Suppress warnings
warnings.filterwarnings('ignore')

# Logger setup
logger = logging.getLogger(__name__)

class EnhancedMLModelTrainer:
    """Enhanced ML Model Trainer với feature engineering và model optimization"""
    
    def __init__(self):
        # Synchronized feature names with MLModelService (12 features)
        self.feature_names = [
            'so_dau', 'so_cuoi', 'tong_giai_db', 'chu_so_cuoi', 
            'tong_cham_dau', 'tong_cham_duoi', 'cham_dau_unique',
            'cham_duoi_unique', 'tong_de', 'avg_tong_de_7days', 
            'std_tong_de_7days', 'pattern_score'
        ]
        
        self.model_dir = getattr(settings, 'ML_MODEL_DIR', 'data/predictor_models')
        if not os.path.exists(self.model_dir):
            os.makedirs(self.model_dir)
        
        self.models = {}
        self.scalers = {}
        self.training_history = {}
        
        # Enhanced model configurations
        self.model_configs = {
            'random_forest': {
                'model_class': RandomForestRegressor,
                'params': {
                    'n_estimators': 200,
                    'max_depth': 15,
                    'min_samples_split': 5,
                    'min_samples_leaf': 2,
                    'random_state': 42,
                    'n_jobs': -1
                },
                'param_grid': {
                    'n_estimators': [100, 200, 300],
                    'max_depth': [10, 15, 20, None],
                    'min_samples_split': [2, 5, 10]
                }
            },
            'gradient_boost': {
                'model_class': GradientBoostingRegressor,
                'params': {
                    'n_estimators': 200,
                    'learning_rate': 0.1,
                    'max_depth': 6,
                    'min_samples_split': 5,
                    'min_samples_leaf': 2,
                    'random_state': 42
                },
                'param_grid': {
                    'n_estimators': [100, 200, 300],
                    'learning_rate': [0.05, 0.1, 0.15],
                    'max_depth': [4, 6, 8]
                }
            },
            'neural_network': {
                'model_class': MLPRegressor,
                'params': {
                    'hidden_layer_sizes': (100, 50, 25),
                    'activation': 'relu',
                    'solver': 'adam',
                    'alpha': 0.001,
                    'learning_rate': 'adaptive',
                    'max_iter': 1000,
                    'random_state': 42,
                    'early_stopping': True,
                    'validation_fraction': 0.1
                },
                'param_grid': {
                    'hidden_layer_sizes': [(50, 25), (100, 50), (100, 50, 25)],
                    'alpha': [0.0001, 0.001, 0.01],
                    'learning_rate': ['constant', 'adaptive']
                }
            }
        }
        
        logger.info(f"EnhancedMLModelTrainer initialized with {len(self.feature_names)} features")
    
    def extract_enhanced_features(self, ket_qua_list):
        """Enhanced feature extraction với improved engineering"""
        features = []
        targets = []
        
        for i, kq in enumerate(ket_qua_list):
            try:
                # Skip if we don't have enough historical data for some features
                if i < 7:
                    continue
                
                # Basic features from current record
                giai_db = str(kq.giai_db).zfill(5)
                so_dau = int(giai_db[0]) if giai_db else 0
                so_cuoi = int(giai_db[-1]) if giai_db else 0
                tong_giai_db = sum(int(d) for d in giai_db if d.isdigit())
                chu_so_cuoi = int(giai_db[-1]) if giai_db and giai_db[-1].isdigit() else 0
                
                # Collect all numbers from various prizes
                all_numbers = []
                for field_name in ['giai_db', 'giai_nhat', 'giai_nhi', 'giai_ba']:
                    if hasattr(kq, field_name):
                        value = getattr(kq, field_name)
                        if value:
                            if isinstance(value, str):
                                all_numbers.extend([value])
                            elif isinstance(value, list):
                                all_numbers.extend(value)
                
                # Calculate cham features
                cham_dau = set()
                cham_duoi = set()
                tong_de_nums = []
                
                for num_str in all_numbers:
                    if num_str and len(str(num_str)) >= 2:
                        num_str = str(num_str).zfill(2)
                        if len(num_str) >= 2:
                            cham_dau.add(num_str[-2])
                            cham_duoi.add(num_str[-1])
                            try:
                                tong_de_nums.append(int(num_str[-2:]))
                            except:
                                pass
                
                tong_cham_dau = len(cham_dau)
                tong_cham_duoi = len(cham_duoi)
                cham_dau_unique = len(cham_dau)
                cham_duoi_unique = len(cham_duoi)
                tong_de = sum(tong_de_nums) if tong_de_nums else 0
                
                # Historical features (7-day window)
                recent_tong_de = []
                for j in range(max(0, i-7), i):
                    prev_kq = ket_qua_list[j]
                    prev_all_numbers = []
                    for field_name in ['giai_db', 'giai_nhat', 'giai_nhi', 'giai_ba']:
                        if hasattr(prev_kq, field_name):
                            value = getattr(prev_kq, field_name)
                            if value:
                                if isinstance(value, str):
                                    prev_all_numbers.extend([value])
                                elif isinstance(value, list):
                                    prev_all_numbers.extend(value)
                    
                    prev_tong_de = 0
                    for num_str in prev_all_numbers:
                        if num_str and len(str(num_str)) >= 2:
                            try:
                                prev_tong_de += int(str(num_str)[-2:])
                            except:
                                pass
                    recent_tong_de.append(prev_tong_de)
                
                avg_tong_de_7days = np.mean(recent_tong_de) if recent_tong_de else tong_de
                std_tong_de_7days = np.std(recent_tong_de) if len(recent_tong_de) > 1 else 0
                
                # Advanced pattern analysis
                pattern_score = (tong_cham_dau + tong_cham_duoi + (tong_de % 10)) / 30.0
                
                # Ensure all features are numeric and valid
                feature_row = [
                    float(so_dau), float(so_cuoi), float(tong_giai_db), float(chu_so_cuoi),
                    float(tong_cham_dau), float(tong_cham_duoi), float(cham_dau_unique),
                    float(cham_duoi_unique), float(tong_de), float(avg_tong_de_7days),
                    float(std_tong_de_7days), float(pattern_score)
                ]
                
                # Validate feature count
                if len(feature_row) != len(self.feature_names):
                    logger.warning(f"Feature count mismatch: expected {len(self.feature_names)}, got {len(feature_row)}")
                    continue
                
                features.append(feature_row)
                
                # Target is the next day's giai_db (if available)
                if i + 1 < len(ket_qua_list):
                    next_kq = ket_qua_list[i + 1]
                    target = int(next_kq.giai_db) if next_kq.giai_db else 50000
                    targets.append(target)
                else:
                    # For the last record, we can't predict the next day
                    features.pop()
                    
            except Exception as e:
                logger.error(f"Error extracting features for record {i}: {str(e)}")
                continue
        
        return np.array(features), np.array(targets)
    
    def prepare_training_data(self, ket_qua_queryset, target_field='giai_db'):
        """Prepare training data với enhanced preprocessing"""
        try:
            ket_qua_list = list(ket_qua_queryset.order_by('ngay'))
            
            if len(ket_qua_list) < 30:
                raise ValueError(f"Insufficient training data: {len(ket_qua_list)} records (minimum 30 required)")
            
            logger.info(f"Preparing training data from {len(ket_qua_list)} records")
            
            # Extract features and targets
            X, y = self.extract_enhanced_features(ket_qua_list)
            
            if len(X) == 0:
                raise ValueError("No valid features extracted")
            
            logger.info(f"Extracted {len(X)} feature vectors with {len(self.feature_names)} features each")
            
            # Create DataFrame for better handling
            feature_df = pd.DataFrame(X, columns=self.feature_names)
            
            # Remove any rows with invalid values
            mask = ~(np.isnan(feature_df).any(axis=1) | np.isinf(feature_df).any(axis=1))
            feature_df = feature_df[mask]
            y = y[mask]
            
            if len(feature_df) == 0:
                raise ValueError("No valid data after cleaning")
            
            # Ensure consistent feature order
            feature_df = feature_df[self.feature_names]
            
            logger.info(f"Final training data: {len(feature_df)} samples, {len(self.feature_names)} features")
            
            return feature_df.values, y
            
        except Exception as e:
            logger.error(f"Error preparing training data: {str(e)}")
            # Return dummy data to prevent complete failure
            return [0.0] * len(self.feature_names)
    
    def train_model(self, model_name, X_train, y_train, optimize_params=False):
        """Train individual model với hyperparameter optimization"""
        try:
            if model_name not in self.model_configs:
                raise ValueError(f"Unknown model: {model_name}")
            
            config = self.model_configs[model_name]
            
            logger.info(f"Training {model_name} model...")
            
            # Initialize scaler
            scaler = RobustScaler()
            X_scaled = scaler.fit_transform(X_train)
            
            # Initialize model
            if optimize_params and 'param_grid' in config:
                logger.info(f"Optimizing hyperparameters for {model_name}...")
                
                base_model = config['model_class'](**config['params'])
                
                # Use GridSearchCV for parameter optimization
                grid_search = GridSearchCV(
                    base_model,
                    config['param_grid'],
                    cv=3,
                    scoring='neg_mean_squared_error',
                    n_jobs=-1,
                    verbose=0
                )
                
                grid_search.fit(X_scaled, y_train)
                model = grid_search.best_estimator_
                
                logger.info(f"Best parameters for {model_name}: {grid_search.best_params_}")
                
            else:
                model = config['model_class'](**config['params'])
                model.fit(X_scaled, y_train)
            
            # Evaluate model
            train_score = model.score(X_scaled, y_train)
            cv_scores = cross_val_score(model, X_scaled, y_train, cv=3, scoring='r2')
            
            # Store model and scaler
            self.models[model_name] = model
            self.scalers[model_name] = scaler
            
            # Store training history
            self.training_history[model_name] = {
                'train_score': train_score,
                'cv_scores': cv_scores.tolist(),
                'cv_mean': cv_scores.mean(),
                'cv_std': cv_scores.std(),
                'training_samples': len(X_train),
                'features_used': len(self.feature_names),
                'timestamp': datetime.now().isoformat(),
                'sklearn_version': sklearn.__version__
            }
            
            logger.info(f"✅ {model_name} trained successfully")
            logger.info(f"   Train R²: {train_score:.4f}")
            logger.info(f"   CV R²: {cv_scores.mean():.4f} ± {cv_scores.std():.4f}")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to train {model_name}: {str(e)}")
            return False
    
    def create_ensemble_model(self):
        """Create ensemble model from trained individual models"""
        try:
            if len(self.models) < 2:
                logger.warning("Not enough models for ensemble")
                return False
            
            logger.info("Creating ensemble model...")
            
            # Simple ensemble: equal weighting of all models
            class EnsembleModel:
                def __init__(self, models, scalers):
                    self.models = models
                    self.scalers = scalers
                    self.model_names = list(models.keys())
                
                def predict(self, X):
                    predictions = []
                    for name in self.model_names:
                        if name in self.models and name in self.scalers:
                            try:
                                X_scaled = self.scalers[name].transform(X)
                                pred = self.models[name].predict(X_scaled)
                                predictions.append(pred)
                            except Exception as e:
                                logger.warning(f"Model {name} failed in ensemble: {str(e)}")
                                continue
                    
                    if predictions:
                        return np.mean(predictions, axis=0)
                    else:
                        return np.zeros(X.shape[0])
            
            # Create ensemble
            ensemble = EnsembleModel(self.models, self.scalers)
            
            # For ensemble, we'll use the first scaler (they should be similar)
            first_scaler_name = list(self.scalers.keys())[0]
            ensemble_scaler = self.scalers[first_scaler_name]
            
            self.models['ensemble'] = ensemble
            self.scalers['ensemble'] = ensemble_scaler
            
            logger.info(f"✅ Ensemble model created with {len(self.models)-1} base models")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to create ensemble: {str(e)}")
            return False
    
    def save_models(self):
        """Save trained models và scalers"""
        try:
            saved_count = 0
            
            for model_name in self.models:
                try:
                    model_path = os.path.join(self.model_dir, f'{model_name}_model.pkl')
                    scaler_path = os.path.join(self.model_dir, f'{model_name}_scaler.pkl')
                    
                    # Save using joblib (preferred for sklearn models)
                    joblib.dump(self.models[model_name], model_path)
                    joblib.dump(self.scalers[model_name], scaler_path)
                    
                    saved_count += 1
                    logger.info(f"✅ Saved {model_name} model")
                    
                except Exception as e:
                    logger.error(f"❌ Failed to save {model_name}: {str(e)}")
            
            # Save training history
            history_path = os.path.join(self.model_dir, 'training_history.pkl')
            try:
                joblib.dump(self.training_history, history_path)
                logger.info("✅ Saved training history")
            except Exception as e:
                logger.warning(f"Failed to save training history: {str(e)}")
            
            logger.info(f"Saved {saved_count}/{len(self.models)} models successfully")
            
            return saved_count > 0
            
        except Exception as e:
            logger.error(f"Error saving models: {str(e)}")
            return False
    
    def train_all_models(self, ket_qua_queryset, optimize_params=False, target_field='giai_db'):
        """Train all models with comprehensive workflow"""
        try:
            logger.info("Starting comprehensive model training...")
            
            # Prepare training data
            X, y = self.prepare_training_data(ket_qua_queryset, target_field)
            
            if len(X) == 0:
                logger.error("No training data available")
                return False
            
            # Split data for validation
            X_train, X_val, y_train, y_val = train_test_split(
                X, y, test_size=0.2, random_state=42, shuffle=True
            )
            
            logger.info(f"Training set: {len(X_train)} samples")
            logger.info(f"Validation set: {len(X_val)} samples")
            
            # Train individual models
            trained_models = 0
            for model_name in ['random_forest', 'gradient_boost', 'neural_network']:
                if self.train_model(model_name, X_train, y_train, optimize_params):
                    trained_models += 1
            
            if trained_models == 0:
                logger.error("No models were trained successfully")
                return False
            
            # Create ensemble model
            if trained_models > 1:
                self.create_ensemble_model()
            
            # Validate all models
            self.validate_all_models(X_val, y_val)
            
            # Save models
            if self.save_models():
                logger.info("🎉 All models trained and saved successfully!")
                return True
            else:
                logger.error("Failed to save models")
                return False
            
        except Exception as e:
            logger.error(f"Training workflow failed: {str(e)}")
            return False
    
    def validate_all_models(self, X_val, y_val):
        """Validate all trained models"""
        try:
            logger.info("Validating trained models...")
            
            validation_results = {}
            
            for model_name, model in self.models.items():
                try:
                    if model_name in self.scalers:
                        # Scale validation data
                        X_val_scaled = self.scalers[model_name].transform(X_val)
                        
                        # Make predictions
                        y_pred = model.predict(X_val_scaled)
                        
                        # Calculate metrics
                        mse = mean_squared_error(y_val, y_pred)
                        mae = mean_absolute_error(y_val, y_pred)
                        r2 = r2_score(y_val, y_pred)
                        
                        validation_results[model_name] = {
                            'mse': mse,
                            'mae': mae,
                            'r2': r2,
                            'rmse': np.sqrt(mse)
                        }
                        
                        logger.info(f"📊 {model_name}: R²={r2:.4f}, RMSE={np.sqrt(mse):.2f}, MAE={mae:.2f}")
                        
                except Exception as e:
                    logger.error(f"Validation failed for {model_name}: {str(e)}")
                    validation_results[model_name] = {'error': str(e)}
            
            # Store validation results
            self.validation_results = validation_results
            
            return validation_results
            
        except Exception as e:
            logger.error(f"Model validation error: {str(e)}")
            return {}
    
    def get_training_summary(self):
        """Get comprehensive training summary"""
        summary = {
            'feature_count': len(self.feature_names),
            'feature_names': self.feature_names,
            'models_trained': len(self.models),
            'model_names': list(self.models.keys()),
            'training_history': self.training_history,
            'validation_results': getattr(self, 'validation_results', {}),
            'sklearn_version': sklearn.__version__,
            'timestamp': datetime.now().isoformat()
        }
        
        return summary
    
    def quick_retrain(self, days=30):
        """Quick retrain với recent data"""
        try:
            logger.info(f"Quick retraining with {days} days of recent data...")
            
            end_date = timezone.now().date()
            start_date = end_date - timedelta(days=days)
            
            recent_data = KetQuaXoSo.objects.filter(
                ngay__range=[start_date, end_date]
            ).order_by('ngay')
            
            if recent_data.count() < 20:
                logger.error(f"Insufficient recent data: {recent_data.count()} records")
                return False
            
            return self.train_all_models(recent_data, optimize_params=False)
            
        except Exception as e:
            logger.error(f"Quick retrain failed: {str(e)}")
            return False

# Factory function for creating trainer instances
def create_enhanced_trainer():
    """Factory function to create EnhancedMLModelTrainer instance"""
    return EnhancedMLModelTrainer()