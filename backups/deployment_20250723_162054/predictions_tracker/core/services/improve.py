import os
import logging
import pickle
import numpy as np
import pandas as pd
from datetime import date, datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from sklearn.ensemble import GradientBoostingClassifier, RandomForestClassifier
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import accuracy_score, roc_auc_score, classification_report
from predictions_tracker.models import (
    PredictionMethod, 
    DailyTrackingSession, 
    MethodPredictionResult,
    TrackingEvaluation
)
from .FeatureEngineering import feature_engineering_service

logger = logging.getLogger(__name__)

class MLModelService:
    """
    ✅ ENHANCED ML MODEL SERVICE - TRUE MACHINE LEARNING
    Huấn luyện và sử dụng mô hình ML thực thụ để dự đoán xác suất hit
    """
    
    def __init__(self):
        self.models = {
            'day_1': None,
            'day_2': None, 
            'day_3': None
        }
        self.feature_scalers = {
            'day_1': StandardScaler(),
            'day_2': StandardScaler(),
            'day_3': StandardScaler()
        }
        self.feature_names = []
        self.models_dir = 'ml_models'
        self.is_trained = False
        
        # Create models directory if not exists
        os.makedirs(self.models_dir, exist_ok=True)
        
        # Try to load existing models
        self._load_existing_models()
        
        logger.info("✅ MLModelService initialized")

    def train_comprehensive_model(
        self, 
        months_back: int = 12,
        min_samples_per_method: int = 20,
        test_size: float = 0.2,
        cv_folds: int = 5
    ) -> Dict[str, Any]:
        """
        ✅ HUẤN LUYỆN MÔ HÌNH ML TOÀN DIỆN CHO TẤT CẢ TRACKING DAYS
        """
        try:
            logger.info(f"🚀 Starting comprehensive ML model training...")
            logger.info(f"📊 Parameters: months_back={months_back}, min_samples={min_samples_per_method}")
            
            # 1. Thu thập và chuẩn bị dữ liệu training
            training_data = self._prepare_comprehensive_training_data(
                months_back=months_back,
                min_samples_per_method=min_samples_per_method
            )
            
            if not training_data:
                raise ValueError("❌ No training data available")
            
            logger.info(f"📈 Prepared {len(training_data)} training samples")
            
            # 2. Huấn luyện model cho từng tracking day
            training_results = {}
            
            for tracking_day in [1, 2, 3]:
                logger.info(f"🔬 Training model for tracking day {tracking_day}")
                
                day_results = self._train_day_specific_model(
                    training_data=training_data,
                    tracking_day=tracking_day,
                    test_size=test_size,
                    cv_folds=cv_folds
                )
                
                training_results[f'day_{tracking_day}'] = day_results
                logger.info(f"✅ Day {tracking_day} model trained - accuracy: {day_results['accuracy']:.3f}")
            
            # 3. Lưu models và metadata
            self._save_trained_models(training_results)
            
            # 4. Tổng hợp kết quả
            overall_results = {
                'training_completed': True,
                'training_date': datetime.now().isoformat(),
                'total_samples': len(training_data),
                'models_trained': list(training_results.keys()),
                'average_accuracy': np.mean([r['accuracy'] for r in training_results.values()]),
                'training_summary': training_results
            }
            
            self.is_trained = True
            logger.info(f"🎉 Model training completed! Average accuracy: {overall_results['average_accuracy']:.3f}")
            
            return overall_results
            
        except Exception as e:
            logger.error(f"❌ Error in comprehensive model training: {e}")
            raise

    def _prepare_comprehensive_training_data(
        self, 
        months_back: int = 12,
        min_samples_per_method: int = 20
    ) -> List[Dict[str, Any]]:
        """
        ✅ CHUẨN BỊ DỮ LIỆU TRAINING TOÀN DIỆN
        """
        try:
            end_date = date.today()
            start_date = end_date - timedelta(days=months_back * 30)
            
            logger.info(f"📅 Collecting training data from {start_date} to {end_date}")
            
            # Get all tracking evaluations
            evaluations = TrackingEvaluation.objects.filter(
                evaluation_date__range=[start_date, end_date]
            ).select_related(
                'method_result__method',
                'method_result__session'
            ).order_by('evaluation_date')  # ✅ SẮP XẾP THEO THỜI GIAN TĂNG DẦN
            
            logger.info(f"📊 Found {evaluations.count()} evaluations")
            
            training_samples = []
            
            for evaluation in evaluations:
                try:
                    method = evaluation.method_result.method
                    session = evaluation.method_result.session
                    
                    # Calculate tracking day correctly
                    tracking_day = (evaluation.evaluation_date - session.prediction_date).days
                    
                    if not (1 <= tracking_day <= 3):
                        continue
                    
                    # Get predicted numbers
                    predicted_numbers = evaluation.method_result.base_prediction_numbers or []
                    
                    # Extract comprehensive features using FeatureEngineering
                    features = feature_engineering_service.extract_comprehensive_features(
                        method=method,
                        target_date=session.prediction_date,  # ✅ NGÀY DỰ ĐOÁN
                        predicted_numbers=predicted_numbers,
                        historical_data=[],  # Will be populated by the service
                        context={
                            'tracking_day': tracking_day,
                            'evaluation_date': evaluation.evaluation_date
                        }
                    )
                    
                    # Target: hit or miss (1 or 0)
                    target = 1 if evaluation.hit_count > 0 else 0
                    
                    training_sample = {
                        'method_id': method.id,
                        'prediction_date': session.prediction_date,
                        'evaluation_date': evaluation.evaluation_date,
                        'tracking_day': tracking_day,
                        'features': features,
                        'target': target,
                        'hit_count': evaluation.hit_count,
                        'hit_rate': evaluation.hit_rate
                    }
                    
                    training_samples.append(training_sample)
                    
                except Exception as e:
                    logger.warning(f"⚠️ Error processing evaluation {evaluation.id}: {e}")
                    continue
            
            # Extract feature names
            if training_samples:
                self.feature_names = list(training_samples[0]['features'].keys())
                logger.info(f"🎯 Extracted {len(self.feature_names)} features")
            
            logger.info(f"✅ Prepared {len(training_samples)} training samples")
            return training_samples
            
        except Exception as e:
            logger.error(f"❌ Error preparing training data: {e}")
            return []

    def _train_day_specific_model(
        self,
        training_data: List[Dict[str, Any]],
        tracking_day: int,
        test_size: float = 0.2,
        cv_folds: int = 5
    ) -> Dict[str, Any]:
        """
        ✅ HUẤN LUYỆN MÔ HÌNH CHO MỘT TRACKING DAY CỤ THỂ
        """
        try:
            # Filter data cho tracking day cụ thể
            day_data = [
                sample for sample in training_data 
                if sample['tracking_day'] == tracking_day
            ]
            
            if len(day_data) < 50:  # Minimum samples required
                raise ValueError(f"❌ Insufficient data for day {tracking_day}: {len(day_data)} samples")
            
            logger.info(f"📊 Day {tracking_day} training data: {len(day_data)} samples")
            
            # Chuẩn bị features và targets
            X = []
            y = []
            
            for sample in day_data:
                feature_vector = [sample['features'].get(fname, 0.0) for fname in self.feature_names]
                X.append(feature_vector)
                y.append(sample['target'])
            
            X = np.array(X)
            y = np.array(y)
            
            logger.info(f"📈 Feature matrix shape: {X.shape}, Target distribution: {np.bincount(y)}")
            
            # Scale features
            scaler = self.feature_scalers[f'day_{tracking_day}']
            X_scaled = scaler.fit_transform(X)
            
            # Split data (time-aware split)
            # Sắp xếp theo thời gian để đảm bảo tính thời gian
            sorted_indices = sorted(
                range(len(day_data)), 
                key=lambda i: day_data[i]['evaluation_date']
            )
            
            split_point = int(len(sorted_indices) * (1 - test_size))
            train_indices = sorted_indices[:split_point]
            test_indices = sorted_indices[split_point:]
            
            X_train = X_scaled[train_indices]
            X_test = X_scaled[test_indices]
            y_train = y[train_indices]
            y_test = y[test_indices]
            
            logger.info(f"📊 Train: {len(X_train)}, Test: {len(X_test)}")
            
            # Train model
            model = GradientBoostingClassifier(
                n_estimators=100,
                max_depth=6,
                learning_rate=0.1,
                random_state=42
            )
            
            model.fit(X_train, y_train)
            
            # Evaluate
            y_pred = model.predict(X_test)
            test_score = accuracy_score(y_test, y_pred)
            
            # Cross validation
            cv_scores = cross_val_score(model, X_scaled, y, cv=cv_folds)
            
            # ROC AUC if possible
            try:
                y_pred_proba = model.predict_proba(X_test)[:, 1]
                roc_auc = roc_auc_score(y_test, y_pred_proba)
            except:
                roc_auc = 0.0
            
            # Feature importance
            feature_importance = dict(zip(self.feature_names, model.feature_importances_))
            top_features = sorted(feature_importance.items(), key=lambda x: x[1], reverse=True)[:10]
            
            # Store model
            self.models[f'day_{tracking_day}'] = model
            
            results = {
                'tracking_day': tracking_day,
                'model': model,
                'scaler': scaler,
                'train_samples': len(X_train),
                'test_samples': len(X_test),
                'test_accuracy': float(test_score),
                'accuracy': float(test_score),  # Main metric
                'cv_scores': cv_scores.tolist(),
                'cv_mean': float(cv_scores.mean()),
                'cv_std': float(cv_scores.std()),
                'roc_auc': float(roc_auc),
                'feature_importance': feature_importance,
                'top_features': top_features,
                'model_params': model.get_params()
            }
            
            logger.info(f"✅ Day {tracking_day} model training completed:")
            logger.info(f"   📈 Accuracy: {test_score:.3f}")
            logger.info(f"   🔄 CV Score: {cv_scores.mean():.3f} ± {cv_scores.std():.3f}")
            logger.info(f"   📊 ROC AUC: {roc_auc:.3f}")
            
            return results
            
        except Exception as e:
            logger.error(f"❌ Error training day {tracking_day} model: {e}")
            raise

    def predict_hit_probability(
        self,
        method: PredictionMethod,
        target_date: date,
        predicted_numbers: List[str],
        historical_data: List[Dict] = None
    ) -> Dict[str, Any]:
        """
        ✅ DỰ ĐOÁN XÁC SUẤT HIT BẰNG TRAINED ML MODELS
        """
        try:
            if not self.is_trained or not all(self.models.values()):
                logger.warning("⚠️ Models not trained, using statistical fallback")
                return self._statistical_fallback_prediction(method, historical_data)
            
            logger.info(f"🤖 ML prediction for method {method.name}")
            
            # Extract features for prediction
            features = feature_engineering_service.extract_comprehensive_features(
                method=method,
                target_date=target_date,
                predicted_numbers=predicted_numbers,
                historical_data=historical_data or []
            )
            
            # Prepare feature vector
            feature_vector = np.array([
                features.get(fname, 0.0) for fname in self.feature_names
            ]).reshape(1, -1)
            
            # Predict for each day
            predictions = {}
            overall_confidence = 0.0
            
            for tracking_day in [1, 2, 3]:
                model = self.models[f'day_{tracking_day}']
                scaler = self.feature_scalers[f'day_{tracking_day}']
                
                # Scale features
                feature_vector_scaled = scaler.transform(feature_vector)
                
                # Predict probability
                probability = model.predict_proba(feature_vector_scaled)[0, 1]
                
                # Calculate confidence
                confidence = self._calculate_prediction_confidence(
                    model, feature_vector_scaled, tracking_day
                )
                
                predictions[f'day_{tracking_day}'] = {
                    'probability': float(probability),
                    'confidence': float(confidence),
                    'source': 'ml_model'
                }
                
                overall_confidence += confidence
            
            # Find recommended day
            recommended_day = max(
                predictions.keys(), 
                key=lambda k: predictions[k]['probability']
            )
            recommended_day = int(recommended_day.split('_')[1])
            
            overall_confidence = overall_confidence / 3.0
            
            result = {
                'method_id': method.id,
                'method_name': method.name,
                'target_date': target_date.isoformat(),
                'day_predictions': {
                    'day_1': predictions['day_1'],
                    'day_2': predictions['day_2'],
                    'day_3': predictions['day_3']
                },
                'recommended_day': recommended_day,
                'overall_confidence': float(overall_confidence),
                'prediction_source': 'enhanced_ml',
                'feature_count': len(self.feature_names),
                'model_metadata': self._get_model_metadata()
            }
            
            logger.info(f"✅ ML prediction completed: best_day={recommended_day}, confidence={overall_confidence:.3f}")
            return result
            
        except Exception as e:
            logger.error(f"❌ Error in ML prediction for method {method.id}: {e}")
            return self._statistical_fallback_prediction(method, historical_data)

    def _calculate_prediction_confidence(
        self,
        model,
        feature_vector_scaled: np.ndarray,
        tracking_day: int
    ) -> float:
        """Tính confidence của prediction"""
        try:
            # Base confidence từ model performance
            if hasattr(model, '_cached_performance'):
                base_confidence = model._cached_performance.get('cv_mean', 0.5)
            else:
                base_confidence = 0.5
            
            # Prediction probability margin
            prob_prediction = model.predict_proba(feature_vector_scaled)
            if prob_prediction.shape[1] > 1:
                margin = abs(prob_prediction[0, 1] - prob_prediction[0, 0])
            else:
                margin = 0.5
            
            # Combine factors
            confidence = (base_confidence * 0.7 + margin * 0.3)
            
            return min(0.95, max(0.1, float(confidence)))
            
        except Exception as e:
            logger.error(f"❌ Error calculating prediction confidence: {e}")
            return 0.5

    def _get_method_context_data(
        self, 
        method: PredictionMethod, 
        target_date: date,
        days_back: int = 90
    ) -> List[Dict]:
        """Lấy dữ liệu context cho method"""
        try:
            start_date = target_date - timedelta(days=days_back)
            
            evaluations = TrackingEvaluation.objects.filter(
                method_result__method=method,
                evaluation_date__range=[start_date, target_date]
            ).select_related('method_result__session').order_by('evaluation_date')
            
            context_data = []
            for evaluation in evaluations:
                tracking_day = (evaluation.evaluation_date - evaluation.method_result.session.prediction_date).days
                if 1 <= tracking_day <= 3:
                    context_data.append({
                        'evaluation_date': evaluation.evaluation_date,
                        'tracking_day': tracking_day,
                        'hit_count': evaluation.hit_count,
                        'hit_rate': evaluation.hit_rate
                    })
            
            return context_data
            
        except Exception as e:
            logger.error(f"❌ Error getting method context data: {e}")
            return []

    def _statistical_fallback_prediction(
        self, 
        method: PredictionMethod, 
        historical_data: List[Dict]
    ) -> Dict[str, Any]:
        """Statistical fallback khi không có ML model"""
        logger.info(f"📊 Using statistical fallback for method {method.id}")
        
        if not historical_data:
            return {
                'method_id': method.id,
                'method_name': method.name,
                'day_predictions': {
                    'day_1': {'probability': 0.2, 'confidence': 0.1, 'source': 'fallback'},
                    'day_2': {'probability': 0.15, 'confidence': 0.1, 'source': 'fallback'},
                    'day_3': {'probability': 0.1, 'confidence': 0.1, 'source': 'fallback'}
                },
                'recommended_day': 1,
                'overall_confidence': 0.1,
                'prediction_source': 'statistical_fallback'
            }
        
        # Calculate basic statistics từ historical data
        day_performance = {1: [], 2: [], 3: []}
        
        for data in historical_data:
            tracking_day = data.get('tracking_day')
            hit_rate = data.get('hit_rate', 0)
            
            if tracking_day in day_performance:
                day_performance[tracking_day].append(hit_rate)
        
        predictions = {}
        for day in [1, 2, 3]:
            if day_performance[day]:
                avg_rate = np.mean(day_performance[day]) / 100.0  # Convert to probability
                confidence = min(0.7, len(day_performance[day]) / 20.0)  # Based on sample size
            else:
                avg_rate = 0.15
                confidence = 0.1
            
            predictions[f'day_{day}'] = {
                'probability': float(avg_rate),
                'confidence': float(confidence),
                'source': 'statistical'
            }
        
        # Find best day
        best_day = max(predictions.keys(), key=lambda k: predictions[k]['probability'])
        best_day_num = int(best_day.split('_')[1])
        
        # Overall confidence
        overall_confidence = np.mean([pred['confidence'] for pred in predictions.values()])
        
        return {
            'method_id': method.id,
            'method_name': method.name,
            'day_predictions': predictions,
            'recommended_day': best_day_num,
            'overall_confidence': float(overall_confidence),
            'prediction_source': 'statistical_fallback'
        }

    def _save_trained_models(self, training_results: Dict[str, Any]) -> None:
        """✅ LƯU TRAINED MODELS VÀ METADATA"""
        try:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            
            for day_key, results in training_results.items():
                model = results['model']
                scaler = results['scaler']
                
                # Save model
                model_path = os.path.join(self.models_dir, f'model_{day_key}_{timestamp}.pkl')
                with open(model_path, 'wb') as f:
                    pickle.dump(model, f)
                
                # Save scaler
                scaler_path = os.path.join(self.models_dir, f'scaler_{day_key}_{timestamp}.pkl')
                with open(scaler_path, 'wb') as f:
                    pickle.dump(scaler, f)
                
                # Cache performance data in model
                model._cached_performance = {
                    'cv_mean': results['cv_mean'],
                    'cv_std': results['cv_std'],
                    'accuracy': results['accuracy']
                }
                
                logger.info(f"💾 Saved {day_key} model and scaler")
            
            # Save metadata
            metadata = {
                'training_date': timestamp,
                'feature_names': self.feature_names,
                'models_trained': list(training_results.keys()),
                'summary': {k: {
                    'accuracy': v['accuracy'],
                    'cv_mean': v['cv_mean'],
                    'train_samples': v['train_samples']
                } for k, v in training_results.items()}
            }
            
            metadata_path = os.path.join(self.models_dir, f'metadata_{timestamp}.pkl')
            with open(metadata_path, 'wb') as f:
                pickle.dump(metadata, f)
            
            logger.info(f"✅ All models and metadata saved with timestamp {timestamp}")
            
        except Exception as e:
            logger.error(f"❌ Error saving models: {e}")

    def _load_existing_models(self) -> bool:
        """✅ TẢI MODELS ĐÃ TRAIN TỪ TRƯỚC"""
        try:
            if not os.path.exists(self.models_dir):
                logger.info("📁 Models directory doesn't exist")
                return False
            
            # Find latest model files
            model_files = [f for f in os.listdir(self.models_dir) if f.startswith('model_')]
            if not model_files:
                logger.info("📂 No model files found")
                return False
            
            # Get latest timestamp
            timestamps = set()
            for f in model_files:
                parts = f.split('_')
                if len(parts) >= 4:
                    timestamps.add(parts[-1].replace('.pkl', ''))
            
            if not timestamps:
                logger.info("⚠️ No valid model timestamps found")
                return False
            
            latest_timestamp = max(timestamps)
            logger.info(f"🔄 Loading models from timestamp: {latest_timestamp}")
            
            # Load models and scalers
            models_loaded = 0
            for day in [1, 2, 3]:
                day_key = f'day_{day}'
                
                model_path = os.path.join(self.models_dir, f'model_{day_key}_{latest_timestamp}.pkl')
                scaler_path = os.path.join(self.models_dir, f'scaler_{day_key}_{latest_timestamp}.pkl')
                
                if os.path.exists(model_path) and os.path.exists(scaler_path):
                    try:
                        with open(model_path, 'rb') as f:
                            self.models[day_key] = pickle.load(f)
                        
                        with open(scaler_path, 'rb') as f:
                            self.feature_scalers[day_key] = pickle.load(f)
                        
                        models_loaded += 1
                        logger.info(f"✅ Loaded {day_key} model and scaler")
                        
                    except Exception as e:
                        logger.warning(f"⚠️ Error loading {day_key}: {e}")
            
            # Load metadata
            metadata_path = os.path.join(self.models_dir, f'metadata_{latest_timestamp}.pkl')
            if os.path.exists(metadata_path):
                try:
                    with open(metadata_path, 'rb') as f:
                        metadata = pickle.load(f)
                    self.feature_names = metadata.get('feature_names', [])
                    logger.info(f"📋 Loaded metadata with {len(self.feature_names)} features")
                except Exception as e:
                    logger.warning(f"⚠️ Error loading metadata: {e}")
            
            if models_loaded == 3:
                self.is_trained = True
                logger.info(f"🎉 Successfully loaded all 3 models from {latest_timestamp}")
                return True
            else:
                logger.warning(f"⚠️ Only loaded {models_loaded}/3 models")
                return False
                
        except Exception as e:
            logger.error(f"❌ Error loading existing models: {e}")
            return False

    def _get_model_metadata(self) -> Dict[str, Any]:
        """Lấy metadata của models"""
        metadata = {}
        for day_key, model in self.models.items():
            if model:
                metadata[day_key] = {
                    'model_type': type(model).__name__,
                    'is_trained': hasattr(model, 'feature_importances_'),
                    'n_features': len(self.feature_names) if self.feature_names else 0
                }
                
                if hasattr(model, '_cached_performance'):
                    metadata[day_key].update(model._cached_performance)
        
        return metadata

# ✅ SINGLETON INSTANCE
ml_model_service = MLModelService()