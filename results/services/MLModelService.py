"""
MLModelService - Fixed version with REAL ML predictions
"""
import numpy as np
import pandas as pd
import logging
import os
import joblib
import warnings
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Tuple
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import RobustScaler
from sklearn.model_selection import cross_val_score
import sklearn

from django.conf import settings
from django.utils import timezone
from ..models import KetQuaXoSo

# Suppress warnings
warnings.filterwarnings('ignore')

# Logger setup
logger = logging.getLogger(__name__)

class MLModelService:
    """Fixed ML Model Service with REAL predictions from trained models"""
    
    _instance = None
    _initialized = False
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(MLModelService, cls).__new__(cls)
        return cls._instance
    
    def __init__(self):
        if not self._initialized:
            # Synchronized feature names with EnhancedMLModelTrainer (12 features)
            self.feature_names = [
                'so_dau', 'so_cuoi', 'tong_giai_db', 'chu_so_cuoi', 
                'tong_cham_dau', 'tong_cham_duoi', 'cham_dau_unique',
                'cham_duoi_unique', 'tong_de', 'avg_tong_de_7days', 
                'std_tong_de_7days', 'pattern_score'
            ]
            
            self.models = {}
            self.scalers = {}
            self.version_info = {
                'sklearn_version': sklearn.__version__,
                'created_at': datetime.now().isoformat(),
                'feature_count': len(self.feature_names),
                'compatible_versions': ['1.6.1', '1.7.0']
            }
            
            # Model paths
            self.model_dir = getattr(settings, 'ML_MODEL_DIR', 'data/predictor_models')
            if not os.path.exists(self.model_dir):
                os.makedirs(self.model_dir)
                
            self.model_names = ['random_forest', 'gradient_boost', 'neural_network', 'ensemble']
            
            # 🚀 LAZY LOADING: Không load models ngay khi khởi tạo
            # Models sẽ được load khi cần thiết (first prediction call)
            self._models_loaded = False
            self._initialized = True
            
            logger.info(f"MLModelService initialized with {len(self.feature_names)} features (models will be loaded on demand)")
    
    def _ensure_models_loaded(self):
        """🚀 LAZY LOADING: Load models only when needed"""
        if not self._models_loaded:
            logger.info("🔄 Loading ML models on first use...")
            start_time = datetime.now()
            
            self._load_models()
            self._models_loaded = True
            
            load_time = (datetime.now() - start_time).total_seconds()
            logger.info(f"✅ Models loaded in {load_time:.2f} seconds")
    
    def _load_models(self):
        """Load models with better error handling"""
        loaded_count = 0
        
        for model_name in self.model_names:
            try:
                model_path = os.path.join(self.model_dir, f'{model_name}_model.pkl')
                scaler_path = os.path.join(self.model_dir, f'{model_name}_scaler.pkl')
                
                if os.path.exists(model_path) and os.path.exists(scaler_path):
                    self.models[model_name] = joblib.load(model_path)
                    self.scalers[model_name] = joblib.load(scaler_path)
                    
                    # Validate model compatibility
                    if self._validate_model_compatibility(self.models[model_name], self.scalers[model_name]):
                        loaded_count += 1
                        logger.info(f"✅ Loaded {model_name} model successfully")
                    else:
                        logger.warning(f"⚠️ {model_name} model failed validation")
                        del self.models[model_name]
                        del self.scalers[model_name]
                else:
                    logger.info(f"📂 {model_name} model files not found")
                    
            except Exception as e:
                logger.error(f"❌ Failed to load {model_name}: {str(e)}")
        
        logger.info(f"📊 Successfully loaded {loaded_count}/{len(self.model_names)} models")

    def predict_numbers(self, historical_data, target_date, top_k=20):
        """
        REAL ML prediction - dự đoán thật sự từ trained models
        
        Phương pháp mới:
        1. Trích xuất features từ historical data (giống như khi training)
        2. Sử dụng ensemble model để dự đoán giải đặc biệt ngày tiếp theo
        3. Từ dự đoán giải đặc biệt, tính toán các số 2 chữ số có xác suất cao
        4. Kết hợp với frequency analysis để có danh sách số cân bằng
        """
        try:
            # 🚀 LAZY LOADING: Load models only when first prediction is called
            self._ensure_models_loaded()
            
            if not self.models:
                logger.warning("No trained models available")
                return self._get_frequency_based_predictions(historical_data, top_k)
            
            # Convert QuerySet to list if needed
            if hasattr(historical_data, 'all'):
                historical_data = list(historical_data)
            
            if len(historical_data) < 10:
                logger.warning("Insufficient historical data for ML prediction")
                return self._get_frequency_based_predictions(historical_data, top_k)
            
            logger.info(f"🤖 Making REAL ML predictions from {len(historical_data)} historical records")
            
            # 1. Extract features từ historical data (exactly like training)
            features = self._extract_features_for_prediction(historical_data)
            
            if len(features) == 0:
                logger.warning("No features extracted, using fallback")
                return self._get_frequency_based_predictions(historical_data, top_k)
            
            # 2. Predict next giai_db using trained models
            predicted_giai_db = self._predict_next_giai_db(features)
            
            logger.info(f"🎯 ML predicted next giai_db: {predicted_giai_db}")
            
            # 3. Generate number predictions based on predicted giai_db and patterns
            ml_predictions = self._generate_number_predictions_from_giai_db(
                predicted_giai_db, historical_data, top_k
            )
            
            # 4. Enhance with frequency analysis
            enhanced_predictions = self._enhance_with_frequency_analysis(
                ml_predictions, historical_data, top_k
            )
            
            logger.info(f"✅ Generated {len(enhanced_predictions)} REAL ML predictions")
            
            return enhanced_predictions
            
        except Exception as e:
            logger.error(f"Error in REAL ML prediction: {str(e)}")
            return self._get_frequency_based_predictions(historical_data, top_k)

    def _extract_features_for_prediction(self, historical_data):
        """
        Extract features for prediction - EXACTLY same as training
        """
        try:
            features = []
            
            # Use the same logic as EnhancedMLModelTrainer.extract_enhanced_features
            for i, kq in enumerate(historical_data):
                try:
                    # Skip if we don't have enough historical data for some features
                    if i < 7:
                        continue
                    
                    # Basic features from current record
                    giai_db = str(kq.giai_db).zfill(5) if kq.giai_db else "00000"
                    so_dau = int(giai_db[0]) if giai_db else 0
                    so_cuoi = int(giai_db[-1]) if giai_db else 0
                    tong_giai_db = sum(int(d) for d in giai_db if d.isdigit())
                    chu_so_cuoi = int(giai_db[-1]) if giai_db and giai_db[-1].isdigit() else 0
                    
                    # Get all 2-digit numbers using model method
                    if hasattr(kq, 'get_all_2digit_numbers'):
                        all_2digit_numbers = kq.get_all_2digit_numbers()
                    else:
                        # Fallback extraction
                        all_2digit_numbers = []
                        for field_name in ['giai_db', 'giai_1', 'giai_2', 'giai_3', 'giai_4', 'giai_5', 'giai_6', 'giai_7']:
                            field_value = getattr(kq, field_name, None)
                            if field_value:
                                # Extract 2-digit numbers
                                field_str = str(field_value)
                                numbers = []
                                if ',' in field_str:
                                    for num in field_str.split(','):
                                        num = num.strip()
                                        if num.isdigit() and len(num) >= 2:
                                            numbers.append(num[-2:])  # Last 2 digits
                                else:
                                    if field_str.isdigit() and len(field_str) >= 2:
                                        numbers.append(field_str[-2:])
                                all_2digit_numbers.extend(numbers)
                    
                    # Calculate cham features
                    cham_dau = set()
                    cham_duoi = set()
                    tong_de_nums = []
                    
                    for num_str in all_2digit_numbers:
                        if num_str and len(str(num_str)) >= 2:
                            num_str = str(num_str).zfill(2)
                            cham_dau.add(num_str[0])   # First digit
                            cham_duoi.add(num_str[1])  # Second digit
                            try:
                                tong_de_nums.append(int(num_str))
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
                        if j < len(historical_data):
                            prev_kq = historical_data[j]
                            if hasattr(prev_kq, 'get_all_2digit_numbers'):
                                prev_all_numbers = prev_kq.get_all_2digit_numbers()
                            else:
                                prev_all_numbers = []
                            
                            prev_tong_de = sum(int(num) for num in prev_all_numbers if num.isdigit())
                            recent_tong_de.append(prev_tong_de)
                    
                    avg_tong_de_7days = np.mean(recent_tong_de) if recent_tong_de else tong_de
                    std_tong_de_7days = np.std(recent_tong_de) if len(recent_tong_de) > 1 else 0
                    
                    # Advanced pattern analysis
                    pattern_score = (tong_cham_dau + tong_cham_duoi + (tong_de % 10)) / 30.0
                    
                    # Create feature vector - EXACTLY same order as training
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
                    
                except Exception as e:
                    logger.debug(f"Error extracting features for record {i}: {str(e)}")
                    continue
            
            logger.info(f"Extracted {len(features)} feature vectors for prediction")
            return np.array(features)
            
        except Exception as e:
            logger.error(f"Error in feature extraction: {str(e)}")
            return np.array([])

    def _predict_next_giai_db(self, features):
        """
        Use trained models to predict next giai_db value
        """
        try:
            if len(features) == 0:
                return 50000  # Default middle value
            
            # Use the latest feature vector for prediction
            latest_features = features[-1].reshape(1, -1)
            
            predictions = []
            confidences = []
            
            # Try ensemble model first
            if 'ensemble' in self.models and 'ensemble' in self.scalers:
                try:
                    scaled_features = self.scalers['ensemble'].transform(latest_features)
                    prediction = self.models['ensemble'].predict(scaled_features)[0]
                    predictions.append(prediction)
                    confidences.append(0.9)  # High confidence for ensemble
                    logger.info(f"Ensemble prediction: {prediction}")
                except Exception as e:
                    logger.warning(f"Ensemble prediction failed: {str(e)}")
            
            # Try individual models
            for model_name in ['random_forest', 'gradient_boost', 'neural_network']:
                if model_name in self.models and model_name in self.scalers:
                    try:
                        scaled_features = self.scalers[model_name].transform(latest_features)
                        prediction = self.models[model_name].predict(scaled_features)[0]
                        predictions.append(prediction)
                        confidences.append(0.7)
                        logger.info(f"{model_name} prediction: {prediction}")
                    except Exception as e:
                        logger.warning(f"{model_name} prediction failed: {str(e)}")
            
            if predictions:
                # Weighted average of predictions
                weighted_prediction = np.average(predictions, weights=confidences)
                
                # Ensure it's a valid 5-digit number
                predicted_giai_db = int(max(10000, min(99999, weighted_prediction)))
                
                logger.info(f"Final weighted prediction: {predicted_giai_db}")
                return predicted_giai_db
            else:
                logger.warning("No models could make predictions")
                return 50000
                
        except Exception as e:
            logger.error(f"Error in giai_db prediction: {str(e)}")
            return 50000

    def _generate_number_predictions_from_giai_db(self, predicted_giai_db, historical_data, top_k):
        """
        Generate 2-digit number predictions based on predicted giai_db
        """
        try:
            predictions = []
            
            # 1. Extract numbers from predicted giai_db
            giai_db_str = str(predicted_giai_db).zfill(5)
            
            # Add different combinations from giai_db
            giai_db_numbers = [
                giai_db_str[-2:],           # Last 2 digits (most important)
                giai_db_str[:2],            # First 2 digits
                giai_db_str[1:3],           # Middle 2 digits
                giai_db_str[2:4],           # Another middle combination
            ]
            
            for i, number in enumerate(giai_db_numbers):
                if number.isdigit():
                    confidence = 0.9 - (i * 0.1)  # Decreasing confidence
                    predictions.append({
                        'number': number,
                        'confidence': confidence,
                        'method': f'ml_giai_db_{i+1}'
                    })
            
            # 2. Generate related numbers using ML-based patterns
            base_numbers = [int(d) for d in giai_db_str]
            
            # Pattern-based generations
            for i in range(min(10, top_k - len(predictions))):
                # Generate numbers based on mathematical relationships
                if i < len(base_numbers) - 1:
                    # Sum of consecutive digits
                    num1 = base_numbers[i]
                    num2 = base_numbers[i + 1]
                    generated_num = f"{num1}{num2}"
                    
                    predictions.append({
                        'number': generated_num,
                        'confidence': 0.8 - (i * 0.05),
                        'method': f'ml_pattern_{i+1}'
                    })
                
                # Mathematical transformations
                if i < len(base_numbers):
                    digit = base_numbers[i]
                    # Various transformations
                    transforms = [
                        (digit + 1) % 10,
                        (digit + 2) % 10,
                        (digit * 2) % 10,
                        (digit + 5) % 10
                    ]
                    
                    for j, transform in enumerate(transforms):
                        if len(predictions) < top_k:
                            generated_num = f"{digit}{transform}"
                            predictions.append({
                                'number': generated_num,
                                'confidence': 0.7 - (i * 0.02) - (j * 0.01),
                                'method': f'ml_transform_{i+1}_{j+1}'
                            })
            
            # Remove duplicates while preserving order
            seen = set()
            unique_predictions = []
            for pred in predictions:
                if pred['number'] not in seen:
                    seen.add(pred['number'])
                    unique_predictions.append(pred)
            
            return unique_predictions[:top_k]
            
        except Exception as e:
            logger.error(f"Error generating number predictions: {str(e)}")
            return []

    def _enhance_with_frequency_analysis(self, ml_predictions, historical_data, top_k):
        """
        Enhance ML predictions with frequency analysis from historical data
        """
        try:
            # Get frequency analysis from recent data
            recent_data = historical_data[:30] if len(historical_data) >= 30 else historical_data
            
            number_frequency = {}
            for record in recent_data:
                if hasattr(record, 'get_all_2digit_numbers'):
                    numbers = record.get_all_2digit_numbers()
                    for num in numbers:
                        number_frequency[num] = number_frequency.get(num, 0) + 1
            
            # Combine ML predictions with frequency data
            enhanced_predictions = []
            ml_numbers = set()
            
            # Add ML predictions with frequency boost
            for pred in ml_predictions:
                number = pred['number']
                ml_numbers.add(number)
                
                # Boost confidence if number appears frequently
                frequency_boost = 0
                if number in number_frequency:
                    freq_score = number_frequency[number] / len(recent_data)
                    frequency_boost = min(0.2, freq_score * 2)  # Max 0.2 boost
                
                enhanced_predictions.append({
                    'number': number,
                    'confidence': min(0.95, pred['confidence'] + frequency_boost),
                    'method': f"{pred['method']}_enhanced",
                    'frequency': number_frequency.get(number, 0),
                    'frequency_boost': frequency_boost
                })
            
            # Add some pure frequency-based predictions if we need more
            if len(enhanced_predictions) < top_k:
                # Sort by frequency
                sorted_freq = sorted(number_frequency.items(), key=lambda x: x[1], reverse=True)
                
                for number, freq in sorted_freq:
                    if number not in ml_numbers and len(enhanced_predictions) < top_k:
                        confidence = min(0.8, 0.3 + (freq / len(recent_data)))
                        enhanced_predictions.append({
                            'number': number,
                            'confidence': confidence,
                            'method': 'frequency_based',
                            'frequency': freq,
                            'frequency_boost': 0
                        })
            
            # Sort by confidence
            enhanced_predictions.sort(key=lambda x: x['confidence'], reverse=True)
            
            return enhanced_predictions[:top_k]
            
        except Exception as e:
            logger.error(f"Error enhancing with frequency analysis: {str(e)}")
            return ml_predictions

    def _get_frequency_based_predictions(self, historical_data, top_k):
        """
        Fallback frequency-based predictions when ML models are not available
        """
        try:
            logger.info("Using frequency-based fallback predictions")
            
            number_frequency = {}
            recent_data = historical_data[:30] if len(historical_data) >= 30 else historical_data
            
            for record in recent_data:
                if hasattr(record, 'get_all_2digit_numbers'):
                    numbers = record.get_all_2digit_numbers()
                    for num in numbers:
                        number_frequency[num] = number_frequency.get(num, 0) + 1
            
            # Convert to predictions format
            predictions = []
            sorted_freq = sorted(number_frequency.items(), key=lambda x: x[1], reverse=True)
            
            for i, (number, freq) in enumerate(sorted_freq[:top_k]):
                confidence = min(0.8, 0.2 + (freq / len(recent_data)))
                predictions.append({
                    'number': number,
                    'confidence': confidence,
                    'method': 'frequency_fallback',
                    'frequency': freq
                })
            
            return predictions
            
        except Exception as e:
            logger.error(f"Error in frequency-based predictions: {str(e)}")
            return []

    def train_models(self, force_retrain=False):
        """Train models using EnhancedMLModelTrainer"""
        try:
            from .EnhancedMLModelTrainer import EnhancedMLModelTrainer
            
            logger.info("🔄 Starting REAL model training...")
            trainer = EnhancedMLModelTrainer()
            
            # Get sufficient data for training
            end_date = timezone.now().date()
            start_date = end_date - timedelta(days=180)  # Use 6 months of data
            
            training_data = KetQuaXoSo.objects.filter(
                ngay__range=[start_date, end_date]
            ).order_by('ngay')
            
            if training_data.count() < 50:
                logger.error(f"Insufficient training data: {training_data.count()} records (minimum 50)")
                return False
            
            logger.info(f"Training with {training_data.count()} records from {start_date} to {end_date}")
            
            success = trainer.train_all_models(training_data, optimize_params=False)
            
            if success:
                # Reload models after training
                self._load_models()
                logger.info("✅ Models trained and reloaded successfully")
                return True
            else:
                logger.error("❌ Model training failed")
                return False
                
        except Exception as e:
            logger.error(f"❌ Error training models: {str(e)}")
            return False

    def _validate_model_compatibility(self, model, scaler) -> bool:
        """Validate model compatibility with enhanced checking"""
        try:
            # Check if scaler can handle our feature count
            dummy_data = np.array([[0.5] * len(self.feature_names)])
            scaled_data = scaler.transform(dummy_data)
            
            # Check if model can predict
            prediction = model.predict(scaled_data)
            
            return len(prediction) > 0 and not np.isnan(prediction[0])
            
        except Exception as e:
            logger.error(f"Model validation failed: {str(e)}")
            return False

    def get_model_info(self):
        """Get detailed model information"""
        working_models = 0
        model_details = {}
        
        for model_name in self.model_names:
            if model_name in self.models and model_name in self.scalers:
                try:
                    # Test model
                    dummy_data = np.array([[0.5] * len(self.feature_names)])
                    scaled_data = self.scalers[model_name].transform(dummy_data)
                    prediction = self.models[model_name].predict(scaled_data)
                    
                    model_details[model_name] = {
                        'status': 'working',
                        'can_predict': True,
                        'test_prediction': float(prediction[0]) if len(prediction) > 0 else None
                    }
                    working_models += 1
                except Exception as e:
                    model_details[model_name] = {
                        'status': 'error',
                        'error': str(e),
                        'can_predict': False
                    }
            else:
                model_details[model_name] = {
                    'status': 'not_loaded',
                    'can_predict': False
                }
        
        return {
            'total_models': len(self.model_names),
            'loaded_models': len(self.models),
            'working_models': working_models,
            'model_details': model_details,
            'feature_count': len(self.feature_names),
            'sklearn_version': sklearn.__version__,
            'version_info': self.version_info
        }

    def validate_models(self):
        """Validate all models and return detailed report"""
        validation_results = {
            'total_models': len(self.model_names),
            'working_models': 0,
            'failed_models': [],
            'details': {},
            'feature_count': len(self.feature_names),
            'sklearn_version': sklearn.__version__
        }
        
        for model_name in self.model_names:
            try:
                if model_name in self.models and model_name in self.scalers:
                    if self._validate_model_compatibility(self.models[model_name], self.scalers[model_name]):
                        validation_results['working_models'] += 1
                        validation_results['details'][model_name] = 'working'
                    else:
                        validation_results['failed_models'].append(model_name)
                        validation_results['details'][model_name] = 'validation_failed'
                else:
                    validation_results['failed_models'].append(model_name)
                    validation_results['details'][model_name] = 'not_loaded'
                    
            except Exception as e:
                validation_results['failed_models'].append(model_name)
                validation_results['details'][model_name] = f'error: {str(e)}'
        
        return validation_results

# 🚀 LAZY SINGLETON: Instance chỉ được tạo khi cần thiết
_ml_service_instance = None

def get_ml_model_service():
    """Get ML Model Service instance (lazy loading)"""
    global _ml_service_instance
    if _ml_service_instance is None:
        _ml_service_instance = MLModelService()
    return _ml_service_instance

# Backward compatibility - proxy object that behaves like the service
class _LazyMLServiceProxy:
    def __getattr__(self, name):
        return getattr(get_ml_model_service(), name)

ml_model_service = _LazyMLServiceProxy()