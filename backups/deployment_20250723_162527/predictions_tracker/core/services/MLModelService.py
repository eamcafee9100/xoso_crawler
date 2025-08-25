import numpy as np
import pandas as pd
import joblib
import os
from datetime import date, timedelta, datetime
from typing import Dict, List, Optional, Any, Tuple
from sklearn.ensemble import GradientBoostingClassifier, RandomForestClassifier
from sklearn.model_selection import train_test_split, cross_val_score, TimeSeriesSplit
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import classification_report, roc_auc_score, precision_recall_curve
from collections import defaultdict
import logging
from pathlib import Path

# ✅ SAFE IMPORTS với fallback
try:
    from .DataService import data_service
except ImportError:
    data_service = None
    
try:
    from .FeatureEngineering import feature_engineering_service
except ImportError:
    feature_engineering_service = None

from predictions_tracker.models import (
    PredictionMethod, 
    DailyTrackingSession, 
    MethodPredictionResult,
    TrackingEvaluation
)

logger = logging.getLogger(__name__)

class MLModelService:
    """
    ✅ ENHANCED ML MODEL SERVICE - TRUE MACHINE LEARNING
    Huấn luyện và sử dụng mô hình ML thực thụ để dự đoán xác suất hit
    
    Returns format tuân thủ quy tắc:
    - Dict với schema rõ ràng
    - Kiểu dữ liệu được định nghĩa trong docstring
    """
    
    def __init__(self):
        self.model_dir = Path("ml_models")
        self.model_dir.mkdir(exist_ok=True)
        
        # Models cho từng tracking day
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
        self.model_metadata = {}
        self.is_trained = False  # ✅ KẾT HỢP từ v1
        
        # Load existing models if available
        loaded = self._load_existing_models()
        if loaded:
            self.is_trained = True  # ✅ SET TRUE nếu load thành công
        
        logger.info(f"✅ MLModelService initialized - is_trained: {self.is_trained}")
    
    def train_comprehensive_model(
        self, 
        months_back: int = 12,
        min_samples_per_method: int = 20,
        test_size: float = 0.2,
        cv_folds: int = 5
    ) -> Dict[str, Any]:
        """
        ✅ HUẤN LUYỆN MÔ HÌNH ML TOÀN DIỆN CHO TẤT CẢ TRACKING DAYS
        
        Returns:
            Dict[str, Any] - Training result với format:
            {
                'training_completed': bool,
                'training_date': str,
                'total_samples': int,
                'models_trained': List[str],
                'successful_models': int,
                'average_accuracy': float,
                'training_summary': Dict[str, Dict]
            }
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
                logger.error("❌ No training data available")
                self.is_trained = False
                return self._create_training_fallback()
            
            logger.info(f"📈 Prepared {len(training_data)} training samples")
            
            # 2. Huấn luyện model cho từng tracking day
            training_results = {}
            
            for tracking_day in [1, 2, 3]:
                logger.info(f"🔬 Training model for tracking day {tracking_day}")
                
                try:
                    day_results = self._train_day_specific_model(
                        training_data=training_data,
                        tracking_day=tracking_day,
                        test_size=test_size,
                        cv_folds=cv_folds
                    )
                    
                    training_results[f'day_{tracking_day}'] = day_results
                    logger.info(f"✅ Day {tracking_day} model trained - accuracy: {day_results['accuracy']:.3f}")
                    
                except Exception as day_error:
                    logger.error(f"❌ Error training day {tracking_day} model: {day_error}")
                    # ✅ KẾT HỢP: Continue với các ngày khác
                    training_results[f'day_{tracking_day}'] = {
                        'error': str(day_error),
                        'accuracy': 0.0,
                        'trained': False
                    }
            
            # ✅ KẾT HỢP: Kiểm tra có ít nhất 1 model được train thành công
            successful_models = sum(1 for result in training_results.values() if result.get('trained', True))
            
            if successful_models == 0:
                logger.error("❌ No models were trained successfully")
                self.is_trained = False
                return self._create_training_fallback()
            
            # 3. Lưu models và metadata
            try:
                self._save_trained_models(training_results)
            except Exception as save_error:
                logger.error(f"❌ Error saving models: {save_error}")
            
            # 4. Tổng hợp kết quả
            overall_results = {
                'training_completed': True,
                'training_date': datetime.now().isoformat(),
                'total_samples': len(training_data),
                'models_trained': list(training_results.keys()),
                'successful_models': successful_models,
                'average_accuracy': np.mean([r.get('accuracy', 0) for r in training_results.values()]),
                'training_summary': training_results,
                'feature_count': len(self.feature_names),
                'parameters': {
                    'months_back': months_back,
                    'min_samples_per_method': min_samples_per_method,
                    'test_size': test_size,
                    'cv_folds': cv_folds
                }
            }
            
            # ✅ SET is_trained = True
            self.is_trained = True
            logger.info(f"🎉 Model training completed! Average accuracy: {overall_results['average_accuracy']:.3f}")
            
            return overall_results
            
        except Exception as e:
            logger.error(f"❌ Error in comprehensive model training: {e}")
            self.is_trained = False
            return self._create_training_fallback()

    def _create_training_fallback(self) -> Dict[str, Any]:
        """
        ✅ KẾT HỢP từ v1: Tạo fallback result khi training thất bại
        
        Returns:
            Dict[str, Any] - Fallback result với schema nhất quán
        """
        return {
            'training_completed': False,
            'training_date': datetime.now().isoformat(),
            'total_samples': 0,
            'models_trained': [],
            'successful_models': 0,
            'average_accuracy': 0.0,
            'error': 'Training failed - insufficient data or system error'
        }

    def _prepare_comprehensive_training_data(
        self, 
        months_back: int = 12,
        min_samples_per_method: int = 20
    ) -> List[Dict[str, Any]]:
        """
        ✅ CHUẨN BỊ DỮ LIỆU TRAINING với FALLBACK logic từ v1
        
        Returns:
            List[Dict[str, Any]] - Training samples với format nhất quán
        """
        try:
            # ✅ KẾT HỢP: Try DataService first, fallback to direct query
            if data_service:
                logger.info("🔄 Using DataService for training data")
                training_data = data_service.get_training_data_for_ml(
                    months_back=months_back,
                    min_samples_per_method=min_samples_per_method
                )
                
                if training_data:
                    # Extract feature names
                    if training_data:
                        self.feature_names = list(training_data[0]['features'].keys())
                        logger.info(f"🎯 Extracted {len(self.feature_names)} features from DataService")
                    return training_data
            
            # ✅ FALLBACK: Direct query như bản gốc
            logger.info("🔄 DataService unavailable, using direct query")
            
            end_date = date.today()
            start_date = end_date - timedelta(days=months_back * 30)
            
            logger.info(f"📅 Collecting training data from {start_date} to {end_date}")
            
            evaluations = TrackingEvaluation.objects.filter(
                evaluation_date__range=[start_date, end_date]
            ).select_related(
                'method_result__method',
                'method_result__session'
            ).order_by('evaluation_date')
            
            logger.info(f"📊 Found {evaluations.count()} evaluations")
            
            if evaluations.count() == 0:
                logger.warning("❌ No evaluations found in the date range")
                return []
            
            training_samples = []
            
            for evaluation in evaluations:
                try:
                    method = evaluation.method_result.method
                    session = evaluation.method_result.session
                    
                    prediction_date = session.prediction_date
                    evaluation_date = evaluation.evaluation_date
                    tracking_day = (evaluation_date - prediction_date).days
                    
                    if not (1 <= tracking_day <= 3):
                        continue
                    
                    predicted_numbers = evaluation.method_result.base_prediction_numbers or []
                    if not predicted_numbers:
                        continue
                    
                    features = self._extract_ml_features_from_evaluation(
                        evaluation=evaluation,
                        method=method,
                        session=session,
                        tracking_day=tracking_day
                    )
                    
                    if not features:
                        continue
                    
                    target = 1 if evaluation.hit_count > 0 else 0
                    
                    training_sample = {
                        'method_id': method.id,
                        'prediction_date': prediction_date,
                        'evaluation_date': evaluation_date,
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
            else:
                logger.error("❌ No training samples generated")
                return []
            
            # ✅ KẾT HỢP: Group và filter theo method
            method_samples = defaultdict(list)
            for sample in training_samples:
                method_samples[sample['method_id']].append(sample)
            
            # ✅ KẾT HỢP: Flexible threshold từ v1
            valid_samples = []
            valid_methods = 0
            
            # Try with original threshold first
            for method_id, samples in method_samples.items():
                if len(samples) >= min_samples_per_method:
                    valid_samples.extend(samples)
                    valid_methods += 1
                    logger.info(f"Method {method_id}: {len(samples)} samples (valid)")
            
            # ✅ FALLBACK: Lower threshold if not enough data
            if len(valid_samples) < 50:  # Need at least 50 total samples
                logger.warning(f"⚠️ Low valid samples ({len(valid_samples)}), lowering threshold")
                valid_samples = []
                lower_threshold = max(5, min_samples_per_method // 4)  # Much lower
                
                for method_id, samples in method_samples.items():
                    if len(samples) >= lower_threshold:
                        valid_samples.extend(samples)
                        valid_methods += 1
                        logger.info(f"Method {method_id}: {len(samples)} samples (valid with lower threshold)")
            
            logger.info(f"✅ Final dataset: {len(valid_samples)} samples from {valid_methods} methods")
            return valid_samples
            
        except Exception as e:
            logger.error(f"❌ Error preparing training data: {e}")
            return []

    def _extract_ml_features_from_evaluation(
        self,
        evaluation: 'TrackingEvaluation',
        method: 'PredictionMethod', 
        session: 'DailyTrackingSession',
        tracking_day: int
    ) -> Dict[str, float]:
        """
        ✅ TRÍCH XUẤT FEATURES với validation từ v1
        
        Returns:
            Dict[str, float] - Features với kiểu dữ liệu nhất quán
        """
        try:
            features = {}
            
            # Basic evaluation features
            features['hit_count'] = float(evaluation.hit_count)
            features['hit_rate'] = float(evaluation.hit_rate)
            features['total_predicted'] = float(len(evaluation.method_result.base_prediction_numbers))
            features['tracking_day'] = float(tracking_day)
            
            # Method features
            features['method_category'] = float(hash(method.category) % 100)
            features['method_priority'] = float(method.priority)
            
            # Session features
            features['session_confidence'] = float(evaluation.method_result.overall_confidence)
            
            # Date features
            pred_date = session.prediction_date
            features['day_of_week'] = float(pred_date.weekday())
            features['day_of_month'] = float(pred_date.day)
            features['month'] = float(pred_date.month)
            features['is_weekend'] = float(pred_date.weekday() >= 5)
            
            # ✅ THÊM: Cyclic encoding cho better performance
            import math
            features['dow_sin'] = float(math.sin(2 * math.pi * pred_date.weekday() / 7))
            features['dow_cos'] = float(math.cos(2 * math.pi * pred_date.weekday() / 7))
            features['dom_sin'] = float(math.sin(2 * math.pi * pred_date.day / 31))
            features['dom_cos'] = float(math.cos(2 * math.pi * pred_date.day / 31))
            
            # Historical performance features (nếu có thể tính)
            try:
                recent_evals = TrackingEvaluation.objects.filter(
                    method_result__method=method,
                    evaluation_date__lt=evaluation.evaluation_date
                ).order_by('-evaluation_date')[:10]
                
                if recent_evals:
                    recent_hit_rates = [e.hit_rate for e in recent_evals]
                    features['recent_avg_hit_rate'] = float(np.mean(recent_hit_rates))
                    features['recent_hit_rate_std'] = float(np.std(recent_hit_rates))
                    features['recent_performance_trend'] = float(
                        1.0 if len(recent_hit_rates) >= 2 and recent_hit_rates[0] > recent_hit_rates[-1] else 0.0
                    )
                else:
                    features['recent_avg_hit_rate'] = 0.0
                    features['recent_hit_rate_std'] = 0.0
                    features['recent_performance_trend'] = 0.0
                    
            except Exception as hist_error:
                logger.debug(f"Could not compute historical features: {hist_error}")
                features['recent_avg_hit_rate'] = 0.0
                features['recent_hit_rate_std'] = 0.0
                features['recent_performance_trend'] = 0.0
            
            # ✅ KẾT HỢP từ v1: Validate all features are numbers
            validated_features = {}
            for key, value in features.items():
                try:
                    validated_features[key] = float(value)
                except (ValueError, TypeError):
                    validated_features[key] = 0.0
                    logger.debug(f"Invalid feature value for {key}: {value}")
            
            return validated_features
            
        except Exception as e:
            logger.error(f"❌ Error extracting ML features: {e}")
            return {}

    def _train_day_specific_model(
        self,
        training_data: List[Dict[str, Any]],
        tracking_day: int,
        test_size: float = 0.2,
        cv_folds: int = 5
    ) -> Dict[str, Any]:
        """
        ✅ HUẤN LUYỆN với GradientBoostingClassifier + fallback logic từ v1
        
        Returns:
            Dict[str, Any] - Training result với schema rõ ràng
        """
        try:
            # Filter data cho tracking day cụ thể
            day_data = [
                sample for sample in training_data 
                if sample['tracking_day'] == tracking_day
            ]
            
            # ✅ KẾT HỢP: Flexible threshold từ v1
            if len(day_data) < 10:
                logger.warning(f"⚠️ Low data for day {tracking_day}: {len(day_data)} samples")
                
                if len(day_data) < 5:
                    raise ValueError(f"❌ Insufficient data for day {tracking_day}: {len(day_data)} samples")
            
            logger.info(f"📊 Day {tracking_day} training data: {len(day_data)} samples")
            
            # Chuẩn bị features và targets
            X = []
            y = []
            
            for sample in day_data:
                try:
                    feature_vector = [sample['features'].get(fname, 0.0) for fname in self.feature_names]
                    X.append(feature_vector)
                    y.append(sample['target'])
                except Exception as sample_error:
                    logger.warning(f"⚠️ Error processing sample: {sample_error}")
                    continue
            
            if len(X) < 5:
                raise ValueError(f"❌ Not enough valid samples after processing: {len(X)}")
            
            X = np.array(X)
            y = np.array(y)
            
            logger.info(f"📈 Feature matrix shape: {X.shape}, Target distribution: {np.bincount(y)}")
            
            # ✅ KẾT HỢP từ v1: Validate features
            if np.any(np.isnan(X)) or np.any(np.isinf(X)):
                logger.warning("⚠️ NaN/Inf values in features, replacing with 0")
                X = np.nan_to_num(X, nan=0.0, posinf=0.0, neginf=0.0)
            
            # Scale features
            scaler = self.feature_scalers[f'day_{tracking_day}']
            X_scaled = scaler.fit_transform(X)
            
            # ✅ KẾT HỢP: Time-aware split từ bản mới + simple split fallback từ v1
            try:
                # Time-aware split (preferred)
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
                
                logger.info("📊 Using time-aware split")
                
            except Exception as split_error:
                logger.warning(f"⚠️ Time-aware split failed: {split_error}, using simple split")
                # ✅ FALLBACK: Simple split từ v1
                X_train, X_test, y_train, y_test = train_test_split(
                    X_scaled, y, test_size=test_size, random_state=42,
                    stratify=y if len(np.unique(y)) > 1 else None
                )
            
            logger.info(f"📊 Train/Test split: {len(X_train)}/{len(X_test)}")
            
            # ✅ YÊU CẦU: Sử dụng GradientBoostingClassifier (không phải RandomForest)
            model = GradientBoostingClassifier(
                n_estimators=100,  # Giảm từ 200 để tránh overfitting với ít data
                learning_rate=0.1,
                max_depth=4,       # Giảm từ 6
                min_samples_split=10,
                min_samples_leaf=5,
                subsample=0.8,
                random_state=42,
                validation_fraction=0.1,
                n_iter_no_change=10,
                tol=1e-4
            )
            
            logger.info("🔬 Training Gradient Boosting model...")
            model.fit(X_train, y_train)
            
            # Evaluate model
            train_score = model.score(X_train, y_train)
            test_score = model.score(X_test, y_test)
            
            # ✅ KẾT HỢP: Cross-validation với error handling từ v1
            try:
                # TimeSeriesSplit if enough data
                if len(X_scaled) >= 50:
                    tscv = TimeSeriesSplit(n_splits=min(cv_folds, len(X_train) // 50))
                    cv_scores = cross_val_score(model, X_scaled, y, cv=tscv, scoring='accuracy')
                else:
                    # Regular CV for small datasets
                    cv_scores = cross_val_score(model, X_scaled, y, cv=min(cv_folds, 3), scoring='accuracy')
                
                cv_mean = float(cv_scores.mean())
                cv_std = float(cv_scores.std())
                
            except Exception as cv_error:
                logger.warning(f"⚠️ CV error: {cv_error}")
                cv_scores = [test_score]
                cv_mean = test_score
                cv_std = 0.0
            
            # ROC AUC
            try:
                if len(np.unique(y_test)) > 1:
                    y_pred_proba = model.predict_proba(X_test)
                    if y_pred_proba.shape[1] > 1:
                        roc_auc = roc_auc_score(y_test, y_pred_proba[:, 1])
                    else:
                        roc_auc = 0.5
                else:
                    roc_auc = 0.5
            except Exception as roc_error:
                logger.warning(f"⚠️ ROC AUC error: {roc_error}")
                roc_auc = 0.5
            
            # Feature importance
            try:
                feature_importance = dict(zip(self.feature_names, model.feature_importances_))
                top_features = sorted(feature_importance.items(), key=lambda x: x[1], reverse=True)[:10]
            except Exception as fi_error:
                logger.warning(f"⚠️ Feature importance error: {fi_error}")
                feature_importance = {}
                top_features = []
            
            # Store trained model
            self.models[f'day_{tracking_day}'] = model
            
            # ✅ Cache performance cho confidence calculation
            model._cached_performance = {
                'test_accuracy': test_score,
                'cv_mean': cv_mean,
                'roc_auc': roc_auc
            }
            
            results = {
                'tracking_day': tracking_day,
                'model': model,
                'scaler': scaler,
                'training_samples': len(X_train),
                'test_samples': len(X_test),
                'train_accuracy': float(train_score),
                'test_accuracy': float(test_score),
                'accuracy': float(test_score),  # Main metric
                'cv_scores': [float(s) for s in cv_scores],
                'cv_mean': cv_mean,
                'cv_std': cv_std,
                'roc_auc': float(roc_auc),
                'feature_importance': feature_importance,
                'top_features': top_features,
                'model_params': model.get_params(),
                'trained': True
            }
            
            logger.info(f"✅ Day {tracking_day} model training completed:")
            logger.info(f"   📈 Accuracy: {test_score:.3f}")
            logger.info(f"   🔄 CV Score: {cv_mean:.3f} ± {cv_std:.3f}")
            logger.info(f"   📊 ROC AUC: {roc_auc:.3f}")
            
            return results
            
        except Exception as e:
            logger.error(f"❌ Error training day {tracking_day} model: {e}")
            return {
                'tracking_day': tracking_day,
                'error': str(e),
                'accuracy': 0.0,
                'trained': False
            }

    def predict_hit_probability(
    self,
    method: PredictionMethod,
    target_date: date,
    predicted_numbers: List[str],
    historical_data: List[Dict] = None,
    training_months: int = 3  # ✅ THÊM THAM SỐ MỚI VỚI GIÁ TRỊ MẶC ĐỊNH
) -> Dict[str, Any]:
        """
        ✅ DỰ ĐOÁN XÁC SUẤT HIT với enhanced features và fallback
        
        Args:
            method: PredictionMethod - Method cần dự đoán
            target_date: date - Ngày dự đoán
            predicted_numbers: List[str] - Danh sách các số dự đoán
            historical_data: List[Dict] - Dữ liệu lịch sử (nếu có)
            training_months: int - Số tháng dữ liệu để lấy context (mặc định: 3 tháng)
        
        Returns:
            Dict[str, Any] - Prediction result với format:
            {
                'method_id': int,
                'method_name': str,
                'target_date': str,
                'day_predictions': Dict[str, Dict],
                'recommended_day': int,
                'overall_confidence': float,
                'prediction_source': str
            }
        """
        try:
            if not self.is_trained or not any(self.models.values()):
                logger.warning("⚠️ Models not trained, using statistical fallback")
                return self._statistical_fallback_prediction(method, historical_data, training_months=training_months)

            logger.info(f"🤖 ML prediction for method {method.name}")

            # ✅ KẾT HỢP: Try enhanced features first, fallback to simple
            if feature_engineering_service and historical_data is None:
                try:
                    # ✅ SỬ DỤNG training_months để lấy context data
                    historical_data = self._get_method_context_data(
                        method=method, 
                        target_date=target_date,
                        days_back=training_months * 30  # Chuyển đổi tháng thành ngày
                    )
                    features = feature_engineering_service.extract_comprehensive_features(
                        method=method,
                        target_date=target_date,
                        predicted_numbers=predicted_numbers,
                        historical_data=historical_data
                    )
                except Exception as fe_error:
                    logger.warning(f"⚠️ Enhanced feature extraction failed: {fe_error}")
                    features = self._extract_simple_prediction_features(method, target_date, predicted_numbers)
            else:
                features = self._extract_simple_prediction_features(method, target_date, predicted_numbers)

            if not features:
                logger.warning("⚠️ Could not extract features, using fallback")
                return self._statistical_fallback_prediction(method, historical_data, training_months=training_months)

            # Prepare feature vector
            feature_vector = np.array([
                features.get(fname, 0.0) for fname in self.feature_names
            ]).reshape(1, -1)

            # Validate features
            feature_vector = np.nan_to_num(feature_vector, nan=0.0, posinf=0.0, neginf=0.0)

            # Predict for each day
            predictions = {}
            overall_confidence = 0.0
            valid_predictions = 0

            for tracking_day in [1, 2, 3]:
                model = self.models[f'day_{tracking_day}']
                scaler = self.feature_scalers[f'day_{tracking_day}']

                if model is None:
                    predictions[f'day_{tracking_day}'] = {
                        'probability': 0.2,
                        'confidence': 0.1,
                        'source': 'fallback_missing_model'
                    }
                    continue

                try:
                    # Scale features
                    feature_vector_scaled = scaler.transform(feature_vector)

                    # Predict probability
                    prob_prediction = model.predict_proba(feature_vector_scaled)
                    if prob_prediction.shape[1] > 1:
                        probability = float(prob_prediction[0, 1])
                    else:
                        probability = float(prob_prediction[0, 0])

                    # Calculate confidence
                    confidence = self._calculate_prediction_confidence(
                        model, feature_vector_scaled, tracking_day
                    )

                    predictions[f'day_{tracking_day}'] = {
                        'probability': probability,
                        'confidence': confidence,
                        'source': 'ml_model'
                    }

                    overall_confidence += confidence
                    valid_predictions += 1

                except Exception as day_error:
                    logger.warning(f"⚠️ Error predicting day {tracking_day}: {day_error}")
                    predictions[f'day_{tracking_day}'] = {
                        'probability': 0.2,
                        'confidence': 0.1,
                        'source': 'fallback_prediction_error'
                    }

            # Find recommended day
            if predictions:
                recommended_day = max(
                    predictions.keys(), 
                    key=lambda k: predictions[k]['probability']
                )
                recommended_day = int(recommended_day.split('_')[1])
            else:
                recommended_day = 1

            overall_confidence = overall_confidence / max(valid_predictions, 1)

            result = {
                'method_id': method.id,
                'method_name': method.name,
                'target_date': target_date.isoformat(),
                'day_predictions': predictions,
                'recommended_day': recommended_day,
                'overall_confidence': float(overall_confidence),
                'prediction_source': 'enhanced_ml',
                'feature_count': len(self.feature_names),
                'valid_predictions': valid_predictions,
                'model_metadata': self._get_model_metadata(),
                'training_months': training_months  # ✅ THÊM THAM SỐ ĐÃ SỬ DỤNG VÀO KẾT QUẢ
            }

            logger.info(f"✅ ML prediction completed: best_day={recommended_day}, confidence={overall_confidence:.3f}")
            return result

        except Exception as e:
            logger.error(f"❌ Error in ML prediction for method {method.id}: {e}")
            return self._statistical_fallback_prediction(method, historical_data, training_months=training_months)
    def _extract_simple_prediction_features(
        self,
        method: PredictionMethod,
        target_date: date,
        predicted_numbers: List[str]
    ) -> Dict[str, float]:
        """Extract simple features cho prediction khi enhanced features không available"""
        try:
            features = {}

            # Basic features
            features['total_predicted'] = float(len(predicted_numbers))
            features['method_category'] = float(hash(method.category) % 100)
            features['method_priority'] = float(method.priority)

            # Date features
            features['day_of_week'] = float(target_date.weekday())
            features['day_of_month'] = float(target_date.day)
            features['month'] = float(target_date.month)
            features['is_weekend'] = float(target_date.weekday() >= 5)

            # Cyclic encoding
            import math
            features['dow_sin'] = float(math.sin(2 * math.pi * target_date.weekday() / 7))
            features['dow_cos'] = float(math.cos(2 * math.pi * target_date.weekday() / 7))
            features['dom_sin'] = float(math.sin(2 * math.pi * target_date.day / 31))
            features['dom_cos'] = float(math.cos(2 * math.pi * target_date.day / 31))

            # ✅ FILL missing features với 0
            for feature_name in self.feature_names:
                if feature_name not in features:
                    features[feature_name] = 0.0

            return features

        except Exception as e:
            logger.error(f"❌ Error extracting simple prediction features: {e}")
            return {}

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
                base_confidence = model._cached_performance.get('test_accuracy', 0.5)
            else:
                base_confidence = 0.6

            # Prediction probability margin
            try:
                prob_prediction = model.predict_proba(feature_vector_scaled)
                if prob_prediction.shape[1] > 1:
                    max_prob = np.max(prob_prediction[0])
                    margin = abs(max_prob - 0.5) * 2
                else:
                    margin = 0.5
            except:
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
                context_data.append({
                    'evaluation_date': evaluation.evaluation_date,
                    'prediction_date': evaluation.method_result.session.prediction_date,
                    'tracking_day': evaluation.days_after_prediction,
                    'hit_rate': evaluation.hit_rate,
                    'hit_count': evaluation.hit_count,
                    'wilson_score': evaluation.wilson_score
                })
            
            return context_data
            
        except Exception as e:
            logger.error(f"❌ Error getting method context data: {e}")
            return []

    def _statistical_fallback_prediction(
    self, 
    method: PredictionMethod, 
    historical_data: List[Dict] = None,
    training_months: int = 3  # ✅ THÊM THAM SỐ MỚI
) -> Dict[str, Any]:
        """
        ✅ KẾT HỢP từ v1: Statistical fallback khi không có ML model
        
        Args:
            method: PredictionMethod - Method cần dự đoán
            historical_data: List[Dict] - Dữ liệu lịch sử (nếu có)
            training_months: int - Số tháng dữ liệu để phân tích (mặc định: 3 tháng)
            
        Returns:
            Dict[str, Any] - Fallback prediction với schema nhất quán
        """
        logger.info(f"📊 Using statistical fallback for method {method.id}")

        # Default fallback values
        default_predictions = {
            'day_1': {'probability': 0.2, 'confidence': 0.1, 'source': 'fallback'},
            'day_2': {'probability': 0.15, 'confidence': 0.1, 'source': 'fallback'},
            'day_3': {'probability': 0.1, 'confidence': 0.1, 'source': 'fallback'}
        }

        if not historical_data:
            # ✅ TRY LẤY DỮ LIỆU NẾU KHÔNG CÓ
            try:
                days_back = training_months * 30  # Convert months to days
                today = date.today()
                start_date = today - timedelta(days=days_back)
                
                historical_data = self._get_method_context_data(
                    method=method,
                    target_date=today,
                    days_back=days_back
                )
                
                if not historical_data:
                    logger.warning(f"⚠️ No historical data available for method {method.id}")
            except Exception as hd_error:
                logger.warning(f"⚠️ Error getting historical data: {hd_error}")
        
        if not historical_data:
            return {
                'method_id': method.id,
                'method_name': method.name,
                'day_predictions': default_predictions,
                'recommended_day': 1,
                'overall_confidence': 0.1,
                'prediction_source': 'statistical_fallback_no_data',
                'training_months': training_months  # ✅ THÊM VÀO KẾT QUẢ
            }

        # Process historical data if available
        try:
            day_performance = {1: [], 2: [], 3: []}

            for data in historical_data:
                tracking_day = data.get('tracking_day')
                hit_rate = data.get('hit_rate', 0)

                if tracking_day in day_performance:
                    day_performance[tracking_day].append(hit_rate)

            predictions = {}
            for day in [1, 2, 3]:
                if day_performance[day]:
                    avg_rate = np.mean(day_performance[day]) / 100.0
                    confidence = min(0.7, len(day_performance[day]) / 20.0)
                else:
                    avg_rate = default_predictions[f'day_{day}']['probability']
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
                'prediction_source': 'statistical_fallback',
                'training_months': training_months,  # ✅ THÊM VÀO KẾT QUẢ
                'historical_data_points': len(historical_data)  # ✅ THÊM THÔNG TIN BỔ SUNG
            }

        except Exception as fallback_error:
            logger.error(f"❌ Error in statistical fallback: {fallback_error}")

            return {
                'method_id': method.id,
                'method_name': method.name,
                'day_predictions': default_predictions,
                'recommended_day': 1,
                'overall_confidence': 0.1,
                'prediction_source': 'statistical_fallback_error',
                'training_months': training_months  # ✅ THÊM VÀO KẾT QUẢ
            }
            
    def _save_trained_models(self, training_results: Dict[str, Any]) -> None:
        """✅ LƯU TRAINED MODELS sử dụng joblib"""
        try:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')

            for day_key, results in training_results.items():
                if not results.get('trained', False):
                    continue

                model = results.get('model')
                scaler = results.get('scaler')

                if model is None or scaler is None:
                    continue

                # ✅ Sử dụng joblib thay vì pickle
                model_path = self.model_dir / f"{day_key}_model_{timestamp}.joblib"
                joblib.dump(model, model_path)

                scaler_path = self.model_dir / f"{day_key}_scaler_{timestamp}.joblib"
                joblib.dump(scaler, scaler_path)

                logger.info(f"💾 Saved {day_key} model to {model_path}")

            # Save feature names và metadata
            features_path = self.model_dir / f"feature_names_{timestamp}.joblib"
            joblib.dump(self.feature_names, features_path)

            metadata = {
                'timestamp': timestamp,
                'feature_count': len(self.feature_names),
                'training_results': {k: {
                    'accuracy': v.get('accuracy', 0),
                    'cv_mean': v.get('cv_mean', 0),
                    'roc_auc': v.get('roc_auc', 0),
                    'training_samples': v.get('training_samples', 0)
                } for k, v in training_results.items() if v.get('trained', False)}
            }

            metadata_path = self.model_dir / f"metadata_{timestamp}.joblib"
            joblib.dump(metadata, metadata_path)

            self.model_metadata = metadata
            logger.info(f"✅ All models and metadata saved successfully")

        except Exception as e:
            logger.error(f"❌ Error saving trained models: {e}")

    def _load_existing_models(self) -> bool:
        """✅ LOAD EXISTING MODELS sử dụng joblib"""
        try:
            # Tìm model files mới nhất
            model_files = list(self.model_dir.glob("*_model_*.joblib"))
            if not model_files:
                logger.info("🔍 No existing model files found")
                return False

            # Get latest timestamp
            latest_timestamp = max([
                f.stem.split('_')[-1] for f in model_files 
                if len(f.stem.split('_')) >= 3
            ])

            logger.info(f"📥 Loading models from timestamp: {latest_timestamp}")

            # Load models và scalers
            models_loaded = 0
            for day_key in ['day_1', 'day_2', 'day_3']:
                try:
                    model_path = self.model_dir / f"{day_key}_model_{latest_timestamp}.joblib"
                    scaler_path = self.model_dir / f"{day_key}_scaler_{latest_timestamp}.joblib"

                    if model_path.exists() and scaler_path.exists():
                        self.models[day_key] = joblib.load(model_path)
                        self.feature_scalers[day_key] = joblib.load(scaler_path)
                        models_loaded += 1
                        logger.info(f"✅ Loaded {day_key} model and scaler")

                except Exception as e:
                    logger.warning(f"⚠️ Error loading {day_key} model: {e}")
                    continue

            # Load feature names
            try:
                features_path = self.model_dir / f"feature_names_{latest_timestamp}.joblib"
                if features_path.exists():
                    self.feature_names = joblib.load(features_path)
                    logger.info(f"✅ Loaded {len(self.feature_names)} feature names")
            except Exception as e:
                logger.warning(f"⚠️ Error loading feature names: {e}")

            # Load metadata
            try:
                metadata_path = self.model_dir / f"metadata_{latest_timestamp}.joblib"
                if metadata_path.exists():
                    self.model_metadata = joblib.load(metadata_path)
                    logger.info("✅ Loaded model metadata")
            except Exception as e:
                logger.warning(f"⚠️ Error loading metadata: {e}")

            if models_loaded >= 1:  # ✅ Chỉ cần ít nhất 1 model
                logger.info(f"🎉 Successfully loaded {models_loaded}/3 models from {latest_timestamp}")
                return True
            else:
                logger.warning(f"⚠️ No models loaded successfully")
                return False

        except Exception as e:
            logger.error(f"❌ Error loading existing models: {e}")
            return False

    def _get_model_metadata(self) -> Dict[str, Any]:
        """Get model metadata for responses"""
        if self.model_metadata:
            return self.model_metadata

        return {
            'models_available': all(self.models.values()),
            'feature_count': len(self.feature_names),
            'last_training': 'unknown'
        }

    def get_model_performance_summary(self) -> Dict[str, Any]:
        """
        ✅ LẤY TỔNG KẾT HIỆU SUẤT MODELS
        
        Returns:
            Dict[str, Any] - Performance summary với schema rõ ràng
        """
        try:
            if not self.model_metadata:
                return {'error': 'No model metadata available'}

            summary = {
                'models_trained': len([m for m in self.models.values() if m is not None]),
                'total_models': 3,
                'feature_count': len(self.feature_names),
                'training_timestamp': self.model_metadata.get('timestamp', 'unknown'),
                'performance_by_day': {}
            }

            # Performance cho từng day
            training_results = self.model_metadata.get('training_results', {})
            for day_key, metrics in training_results.items():
                summary['performance_by_day'][day_key] = {
                    'accuracy': metrics['accuracy'],
                    'cv_score': metrics['cv_mean'],
                    'roc_auc': metrics['roc_auc'],
                    'training_samples': metrics['training_samples']
                }

            # Overall performance
            if training_results:
                accuracies = [m['accuracy'] for m in training_results.values()]
                summary['overall_performance'] = {
                    'avg_accuracy': float(np.mean(accuracies)),
                    'best_accuracy': float(np.max(accuracies)),
                    'consistency': float(1.0 - np.std(accuracies))
                }

            return summary

        except Exception as e:
            logger.error(f"❌ Error getting model performance summary: {e}")
            return {'error': str(e)}

    def retrain_if_needed(
        self, 
        force_retrain: bool = False,
        performance_threshold: float = 0.6
    ) -> Dict[str, Any]:
        """
        ✅ TỰ ĐỘNG RETRAIN NẾU CẦN THIẾT
        
        Returns:
            Dict[str, Any] - Retrain result với schema nhất quán
        """
        try:
            should_retrain = force_retrain
            performance = None

            if not force_retrain:
                # Kiểm tra performance hiện tại
                performance = self.get_model_performance_summary()

                if 'overall_performance' in performance:
                    avg_accuracy = performance['overall_performance']['avg_accuracy']
                    if avg_accuracy < performance_threshold:
                        should_retrain = True
                        logger.info(f"🔄 Auto-retrain triggered: accuracy {avg_accuracy:.3f} < threshold {performance_threshold}")
                else:
                    should_retrain = True
                    logger.info("🔄 Auto-retrain triggered: no performance data")

            if should_retrain:
                logger.info("🚀 Starting automatic model retraining...")
                results = self.train_comprehensive_model()

                return {
                    'retrain_completed': True,
                    'reason': 'forced' if force_retrain else 'performance_threshold',
                    'new_performance': results.get('training_summary', {})
                }
            else:
                return {
                    'retrain_completed': False,
                    'reason': 'performance_sufficient',
                    'current_performance': performance
                }

        except Exception as e:
            logger.error(f"❌ Error in retrain_if_needed: {e}")
            return {'retrain_completed': False, 'error': str(e)}

# ✅ Singleton instance
ml_model_service = MLModelService()