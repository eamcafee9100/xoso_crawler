import logging
import os
import pickle
from datetime import date, datetime, timedelta
from typing import Any, Dict, List, Optional, Tuple

import numpy as np
import pandas as pd
from sklearn.ensemble import GradientBoostingClassifier, RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report, roc_auc_score
from sklearn.model_selection import cross_val_score, train_test_split
from sklearn.preprocessing import StandardScaler

logger = logging.getLogger(__name__)


class MLModelService:
    """
    ✅ ENHANCED ML MODEL SERVICE - TRUE MACHINE LEARNING
    """

    def __init__(self):
        self.models = {"day_1": None, "day_2": None, "day_3": None}
        self.feature_scalers = {
            "day_1": StandardScaler(),
            "day_2": StandardScaler(),
            "day_3": StandardScaler(),
        }
        self.feature_names = []
        self.models_dir = "ml_models"
        self.is_trained = False  # ✅ THÊM ATTRIBUTE NÀY

        # Create models directory if not exists
        os.makedirs(self.models_dir, exist_ok=True)

        # Try to load existing models
        loaded = self._load_existing_models()
        if loaded:
            self.is_trained = True  # ✅ SET TRUE NếU load thành công

        logger.info(f"✅ MLModelService initialized - is_trained: {self.is_trained}")

    def train_comprehensive_model(
        self,
        months_back: int = 12,
        min_samples_per_method: int = 20,
        test_size: float = 0.2,
        cv_folds: int = 5,
    ) -> Dict[str, Any]:
        """
        ✅ HUẤN LUYỆN MÔ HÌNH ML TOÀN DIỆN CHO TẤT CẢ TRACKING DAYS
        """
        try:
            logger.info(f"🚀 Starting comprehensive ML model training...")
            logger.info(
                f"📊 Parameters: months_back={months_back}, min_samples={min_samples_per_method}"
            )

            # ✅ IMPORT DataService ở đây để tránh circular import
            try:
                from .DataService import data_service
            except ImportError:
                logger.error("❌ Cannot import DataService - creating fallback")
                return self._create_training_fallback()

            # 1. Thu thập và chuẩn bị dữ liệu training
            training_data = data_service.get_training_data_for_ml(
                months_back=months_back, min_samples_per_method=min_samples_per_method
            )

            if not training_data:
                logger.error("❌ No training data available from DataService")
                return self._create_training_fallback()

            logger.info(f"📈 Prepared {len(training_data)} training samples")

            # Extract feature names
            if training_data:
                self.feature_names = list(training_data[0]["features"].keys())
                logger.info(f"🎯 Feature names: {self.feature_names}")

            # 2. Huấn luyện model cho từng tracking day
            training_results = {}

            for tracking_day in [1, 2, 3]:
                logger.info(f"🔬 Training model for tracking day {tracking_day}")

                try:
                    day_results = self._train_day_specific_model(
                        training_data=training_data,
                        tracking_day=tracking_day,
                        test_size=test_size,
                        cv_folds=cv_folds,
                    )

                    training_results[f"day_{tracking_day}"] = day_results
                    logger.info(
                        f"✅ Day {tracking_day} model trained - accuracy: {day_results['accuracy']:.3f}"
                    )

                except Exception as day_error:
                    logger.error(
                        f"❌ Error training day {tracking_day} model: {day_error}"
                    )
                    # Continue với các ngày khác
                    training_results[f"day_{tracking_day}"] = {
                        "error": str(day_error),
                        "accuracy": 0.0,
                        "trained": False,
                    }

            # 3. Kiểm tra có ít nhất 1 model được train thành công
            successful_models = sum(
                1 for result in training_results.values() if result.get("trained", True)
            )

            if successful_models == 0:
                logger.error("❌ No models were trained successfully")
                self.is_trained = False
                return self._create_training_fallback()

            # 4. Lưu models và metadata
            try:
                self._save_trained_models(training_results)
            except Exception as save_error:
                logger.error(f"❌ Error saving models: {save_error}")

            # 5. Tổng hợp kết quả
            overall_results = {
                "training_completed": True,
                "training_date": datetime.now().isoformat(),
                "total_samples": len(training_data),
                "models_trained": list(training_results.keys()),
                "successful_models": successful_models,
                "average_accuracy": np.mean(
                    [r.get("accuracy", 0) for r in training_results.values()]
                ),
                "training_summary": training_results,
            }

            # ✅ SET is_trained = True
            self.is_trained = True
            logger.info(
                f"🎉 Model training completed! Average accuracy: {overall_results['average_accuracy']:.3f}"
            )

            return overall_results

        except Exception as e:
            logger.error(f"❌ Error in comprehensive model training: {e}")
            self.is_trained = False
            return self._create_training_fallback()

    def _create_training_fallback(self) -> Dict[str, Any]:
        """Tạo fallback result khi training thất bại"""
        return {
            "training_completed": False,
            "training_date": datetime.now().isoformat(),
            "total_samples": 0,
            "models_trained": [],
            "successful_models": 0,
            "average_accuracy": 0.0,
            "error": "Training failed - insufficient data or system error",
        }

    def _train_day_specific_model(
        self,
        training_data: List[Dict[str, Any]],
        tracking_day: int,
        test_size: float = 0.2,
        cv_folds: int = 5,
    ) -> Dict[str, Any]:
        """
        ✅ HUẤN LUYỆN MÔ HÌNH CHO MỘT TRACKING DAY CỤ THỂ
        """
        try:
            # Filter data cho tracking day cụ thể
            day_data = [
                sample
                for sample in training_data
                if sample["tracking_day"] == tracking_day
            ]

            if len(day_data) < 10:  # ✅ GIẢM threshold để có thể train
                logger.warning(
                    f"⚠️ Low data for day {tracking_day}: {len(day_data)} samples"
                )

                # ✅ Thử với threshold thấp hơn
                if len(day_data) < 5:
                    raise ValueError(
                        f"❌ Insufficient data for day {tracking_day}: {len(day_data)} samples"
                    )

            logger.info(f"📊 Day {tracking_day} training data: {len(day_data)} samples")

            # Chuẩn bị features và targets
            X = []
            y = []

            for sample in day_data:
                try:
                    feature_vector = [
                        sample["features"].get(fname, 0.0)
                        for fname in self.feature_names
                    ]
                    X.append(feature_vector)
                    y.append(sample["target"])
                except Exception as sample_error:
                    logger.warning(f"⚠️ Error processing sample: {sample_error}")
                    continue

            if len(X) < 5:
                raise ValueError(
                    f"❌ Not enough valid samples after processing: {len(X)}"
                )

            X = np.array(X)
            y = np.array(y)

            logger.info(
                f"📈 Feature matrix shape: {X.shape}, Target distribution: {np.bincount(y)}"
            )

            # Validate features
            if np.any(np.isnan(X)) or np.any(np.isinf(X)):
                logger.warning("⚠️ NaN/Inf values in features, replacing with 0")
                X = np.nan_to_num(X, nan=0.0, posinf=0.0, neginf=0.0)

            # Scale features
            scaler = self.feature_scalers[f"day_{tracking_day}"]
            X_scaled = scaler.fit_transform(X)

            # ✅ Simple train/test split - không time-aware để đơn giản
            X_train, X_test, y_train, y_test = train_test_split(
                X_scaled,
                y,
                test_size=test_size,
                random_state=42,
                stratify=y if len(np.unique(y)) > 1 else None,
            )

            logger.info(f"📊 Train: {len(X_train)}, Test: {len(X_test)}")

            # ✅ Sử dụng RandomForest thay vì GradientBoosting (ít bị overfitting)
            model = RandomForestClassifier(
                n_estimators=50,  # Giảm số trees
                max_depth=3,  # Giảm depth
                random_state=42,
                min_samples_split=5,
                min_samples_leaf=2,
            )

            model.fit(X_train, y_train)

            # Evaluate
            y_pred = model.predict(X_test)
            test_accuracy = accuracy_score(y_test, y_pred)

            # ✅ Cross validation với error handling
            try:
                if len(X_scaled) >= cv_folds:
                    cv_scores = cross_val_score(model, X_scaled, y, cv=min(cv_folds, 3))
                    cv_mean = float(cv_scores.mean())
                    cv_std = float(cv_scores.std())
                else:
                    cv_scores = [test_accuracy]
                    cv_mean = test_accuracy
                    cv_std = 0.0
            except Exception as cv_error:
                logger.warning(f"⚠️ CV error: {cv_error}")
                cv_scores = [test_accuracy]
                cv_mean = test_accuracy
                cv_std = 0.0

            # ROC AUC if possible
            try:
                if len(np.unique(y_test)) > 1:
                    y_pred_proba = model.predict_proba(X_test)[:, 1]
                    roc_auc = roc_auc_score(y_test, y_pred_proba)
                else:
                    roc_auc = 0.5
            except Exception as roc_error:
                logger.warning(f"⚠️ ROC AUC error: {roc_error}")
                roc_auc = 0.5

            # Feature importance
            try:
                feature_importance = dict(
                    zip(self.feature_names, model.feature_importances_)
                )
                top_features = sorted(
                    feature_importance.items(), key=lambda x: x[1], reverse=True
                )[:5]
            except Exception as fi_error:
                logger.warning(f"⚠️ Feature importance error: {fi_error}")
                feature_importance = {}
                top_features = []

            # Store model
            self.models[f"day_{tracking_day}"] = model

            results = {
                "tracking_day": tracking_day,
                "model": model,
                "scaler": scaler,
                "train_samples": len(X_train),
                "test_samples": len(X_test),
                "test_accuracy": float(test_accuracy),
                "accuracy": float(test_accuracy),  # Main metric
                "cv_scores": [float(s) for s in cv_scores],
                "cv_mean": cv_mean,
                "cv_std": cv_std,
                "roc_auc": float(roc_auc),
                "feature_importance": feature_importance,
                "top_features": top_features,
                "model_params": model.get_params(),
                "trained": True,
            }

            logger.info(f"✅ Day {tracking_day} model training completed:")
            logger.info(f"   📈 Accuracy: {test_accuracy:.3f}")
            logger.info(f"   🔄 CV Score: {cv_mean:.3f} ± {cv_std:.3f}")
            logger.info(f"   📊 ROC AUC: {roc_auc:.3f}")

            return results

        except Exception as e:
            logger.error(f"❌ Error training day {tracking_day} model: {e}")
            return {
                "tracking_day": tracking_day,
                "error": str(e),
                "accuracy": 0.0,
                "trained": False,
            }

    def predict_hit_probability(
        self,
        method: "PredictionMethod",
        target_date: date,
        predicted_numbers: List[str],
        historical_data: List[Dict] = None,
    ) -> Dict[str, Any]:
        """
        ✅ DỰ ĐOÁN XÁC SUẤT HIT BẰNG TRAINED ML MODELS

        Returns:
            Dict[str, Any] - Prediction result với format:
            {
                'method_id': int,
                'method_name': str,
                'day_predictions': Dict,
                'recommended_day': int,
                'overall_confidence': float,
                'prediction_source': str
            }
        """
        try:
            if not self.is_trained or not any(self.models.values()):
                logger.warning("⚠️ Models not trained, using statistical fallback")
                return self._statistical_fallback_prediction(method, historical_data)

            logger.info(f"🤖 ML prediction for method {method.name}")

            # ✅ Extract features for prediction (simplified)
            features = self._extract_prediction_features(
                method=method,
                target_date=target_date,
                predicted_numbers=predicted_numbers,
            )

            if not features:
                logger.warning("⚠️ Could not extract features, using fallback")
                return self._statistical_fallback_prediction(method, historical_data)

            # Prepare feature vector
            feature_vector = np.array(
                [features.get(fname, 0.0) for fname in self.feature_names]
            ).reshape(1, -1)

            # Validate features
            feature_vector = np.nan_to_num(
                feature_vector, nan=0.0, posinf=0.0, neginf=0.0
            )

            # Predict for each day
            predictions = {}
            overall_confidence = 0.0
            valid_predictions = 0

            for tracking_day in [1, 2, 3]:
                model = self.models[f"day_{tracking_day}"]
                scaler = self.feature_scalers[f"day_{tracking_day}"]

                if model is None:
                    # Fallback for missing model
                    predictions[f"day_{tracking_day}"] = {
                        "probability": 0.2,
                        "confidence": 0.1,
                        "source": "fallback_missing_model",
                    }
                    continue

                try:
                    # Scale features
                    feature_vector_scaled = scaler.transform(feature_vector)

                    # Predict probability
                    probability = model.predict_proba(feature_vector_scaled)[0, 1]

                    # Calculate confidence
                    confidence = self._calculate_prediction_confidence(
                        model, feature_vector_scaled, tracking_day
                    )

                    predictions[f"day_{tracking_day}"] = {
                        "probability": float(probability),
                        "confidence": float(confidence),
                        "source": "ml_model",
                    }

                    overall_confidence += confidence
                    valid_predictions += 1

                except Exception as day_error:
                    logger.warning(
                        f"⚠️ Error predicting day {tracking_day}: {day_error}"
                    )
                    predictions[f"day_{tracking_day}"] = {
                        "probability": 0.2,
                        "confidence": 0.1,
                        "source": "fallback_prediction_error",
                    }

            # Find recommended day
            if predictions:
                recommended_day = max(
                    predictions.keys(), key=lambda k: predictions[k]["probability"]
                )
                recommended_day = int(recommended_day.split("_")[1])
            else:
                recommended_day = 1

            overall_confidence = overall_confidence / max(valid_predictions, 1)

            result = {
                "method_id": method.id,
                "method_name": method.name,
                "target_date": target_date.isoformat(),
                "day_predictions": predictions,
                "recommended_day": recommended_day,
                "overall_confidence": float(overall_confidence),
                "prediction_source": "enhanced_ml",
                "feature_count": len(self.feature_names),
                "valid_predictions": valid_predictions,
            }

            logger.info(
                f"✅ ML prediction completed: best_day={recommended_day}, confidence={overall_confidence:.3f}"
            )
            return result

        except Exception as e:
            logger.error(f"❌ Error in ML prediction for method {method.id}: {e}")
            return self._statistical_fallback_prediction(method, historical_data)

    def _extract_prediction_features(
        self,
        method: "PredictionMethod",
        target_date: date,
        predicted_numbers: List[str],
    ) -> Dict[str, float]:
        """Extract features cho prediction"""
        try:
            features = {}

            # Basic features
            features["total_predicted"] = float(len(predicted_numbers))
            features["method_id_hash"] = float(hash(str(method.id)) % 1000)
            features["method_priority"] = float(method.priority)

            # Date features
            features["day_of_week"] = float(target_date.weekday())
            features["day_of_month"] = float(target_date.day)
            features["month"] = float(target_date.month)
            features["is_weekend"] = float(target_date.weekday() >= 5)

            # ✅ FILL missing features với 0
            for feature_name in self.feature_names:
                if feature_name not in features:
                    features[feature_name] = 0.0

            return features

        except Exception as e:
            logger.error(f"❌ Error extracting prediction features: {e}")
            return {}

    def _calculate_prediction_confidence(
        self, model, feature_vector_scaled: np.ndarray, tracking_day: int
    ) -> float:
        """Tính confidence của prediction"""
        try:
            # Base confidence từ model performance (nếu có cache)
            base_confidence = 0.5

            # Prediction probability margin
            try:
                prob_prediction = model.predict_proba(feature_vector_scaled)
                if prob_prediction.shape[1] > 1:
                    margin = abs(prob_prediction[0, 1] - prob_prediction[0, 0])
                else:
                    margin = 0.5
            except:
                margin = 0.5

            # Combine factors
            confidence = base_confidence * 0.7 + margin * 0.3

            return min(0.95, max(0.1, float(confidence)))

        except Exception as e:
            logger.error(f"❌ Error calculating prediction confidence: {e}")
            return 0.5

    def _statistical_fallback_prediction(
        self, method: "PredictionMethod", historical_data: List[Dict]
    ) -> Dict[str, Any]:
        """
        Statistical fallback khi không có ML model

        Returns:
            Dict[str, Any] - Fallback prediction result
        """
        logger.info(f"📊 Using statistical fallback for method {method.id}")

        # Default fallback values
        default_predictions = {
            "day_1": {"probability": 0.2, "confidence": 0.1, "source": "fallback"},
            "day_2": {"probability": 0.15, "confidence": 0.1, "source": "fallback"},
            "day_3": {"probability": 0.1, "confidence": 0.1, "source": "fallback"},
        }

        if not historical_data:
            return {
                "method_id": method.id,
                "method_name": method.name,
                "day_predictions": default_predictions,
                "recommended_day": 1,
                "overall_confidence": 0.1,
                "prediction_source": "statistical_fallback_no_data",
            }

        # ✅ Process historical data if available
        try:
            day_performance = {1: [], 2: [], 3: []}

            for data in historical_data:
                tracking_day = data.get("tracking_day")
                hit_rate = data.get("hit_rate", 0)

                if tracking_day in day_performance:
                    day_performance[tracking_day].append(hit_rate)

            predictions = {}
            for day in [1, 2, 3]:
                if day_performance[day]:
                    avg_rate = (
                        np.mean(day_performance[day]) / 100.0
                    )  # Convert to probability
                    confidence = min(
                        0.7, len(day_performance[day]) / 20.0
                    )  # Based on sample size
                else:
                    avg_rate = default_predictions[f"day_{day}"]["probability"]
                    confidence = 0.1

                predictions[f"day_{day}"] = {
                    "probability": float(avg_rate),
                    "confidence": float(confidence),
                    "source": "statistical",
                }

            # Find best day
            best_day = max(
                predictions.keys(), key=lambda k: predictions[k]["probability"]
            )
            best_day_num = int(best_day.split("_")[1])

            # Overall confidence
            overall_confidence = np.mean(
                [pred["confidence"] for pred in predictions.values()]
            )

            return {
                "method_id": method.id,
                "method_name": method.name,
                "day_predictions": predictions,
                "recommended_day": best_day_num,
                "overall_confidence": float(overall_confidence),
                "prediction_source": "statistical_fallback",
            }

        except Exception as fallback_error:
            logger.error(f"❌ Error in statistical fallback: {fallback_error}")

            return {
                "method_id": method.id,
                "method_name": method.name,
                "day_predictions": default_predictions,
                "recommended_day": 1,
                "overall_confidence": 0.1,
                "prediction_source": "statistical_fallback_error",
            }

    def _save_trained_models(self, training_results: Dict[str, Any]) -> None:
        """✅ LƯU TRAINED MODELS VÀ METADATA"""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

            for day_key, results in training_results.items():
                if not results.get("trained", False):
                    continue

                model = results.get("model")
                scaler = results.get("scaler")

                if model is None or scaler is None:
                    continue

                # Save model
                model_path = os.path.join(
                    self.models_dir, f"model_{day_key}_{timestamp}.pkl"
                )
                with open(model_path, "wb") as f:
                    pickle.dump(model, f)

                # Save scaler
                scaler_path = os.path.join(
                    self.models_dir, f"scaler_{day_key}_{timestamp}.pkl"
                )
                with open(scaler_path, "wb") as f:
                    pickle.dump(scaler, f)

                logger.info(f"💾 Saved {day_key} model and scaler")

            # Save metadata
            metadata = {
                "training_date": timestamp,
                "feature_names": self.feature_names,
                "models_trained": [
                    k for k, v in training_results.items() if v.get("trained", False)
                ],
                "summary": {
                    k: {
                        "accuracy": v.get("accuracy", 0),
                        "cv_mean": v.get("cv_mean", 0),
                        "train_samples": v.get("train_samples", 0),
                    }
                    for k, v in training_results.items()
                    if v.get("trained", False)
                },
            }

            metadata_path = os.path.join(self.models_dir, f"metadata_{timestamp}.pkl")
            with open(metadata_path, "wb") as f:
                pickle.dump(metadata, f)

            logger.info(f"✅ Models and metadata saved with timestamp {timestamp}")

        except Exception as e:
            logger.error(f"❌ Error saving models: {e}")

    def _load_existing_models(self) -> bool:
        """✅ TẢI MODELS ĐÃ TRAIN TỪ TRƯỚC"""
        try:
            if not os.path.exists(self.models_dir):
                logger.info("📁 Models directory doesn't exist")
                return False

            # Find latest model files
            model_files = [
                f for f in os.listdir(self.models_dir) if f.startswith("model_")
            ]
            if not model_files:
                logger.info("📂 No model files found")
                return False

            # Get latest timestamp
            timestamps = set()
            for f in model_files:
                parts = f.split("_")
                if len(parts) >= 4:
                    timestamps.add(parts[-1].replace(".pkl", ""))

            if not timestamps:
                logger.info("⚠️ No valid model timestamps found")
                return False

            latest_timestamp = max(timestamps)
            logger.info(f"🔄 Loading models from timestamp: {latest_timestamp}")

            # Load models and scalers
            models_loaded = 0
            for day in [1, 2, 3]:
                day_key = f"day_{day}"

                model_path = os.path.join(
                    self.models_dir, f"model_{day_key}_{latest_timestamp}.pkl"
                )
                scaler_path = os.path.join(
                    self.models_dir, f"scaler_{day_key}_{latest_timestamp}.pkl"
                )

                if os.path.exists(model_path) and os.path.exists(scaler_path):
                    try:
                        with open(model_path, "rb") as f:
                            self.models[day_key] = pickle.load(f)

                        with open(scaler_path, "rb") as f:
                            self.feature_scalers[day_key] = pickle.load(f)

                        models_loaded += 1
                        logger.info(f"✅ Loaded {day_key} model and scaler")

                    except Exception as e:
                        logger.warning(f"⚠️ Error loading {day_key}: {e}")

            # Load metadata
            metadata_path = os.path.join(
                self.models_dir, f"metadata_{latest_timestamp}.pkl"
            )
            if os.path.exists(metadata_path):
                try:
                    with open(metadata_path, "rb") as f:
                        metadata = pickle.load(f)
                    self.feature_names = metadata.get("feature_names", [])
                    logger.info(
                        f"📋 Loaded metadata with {len(self.feature_names)} features"
                    )
                except Exception as e:
                    logger.warning(f"⚠️ Error loading metadata: {e}")

            if models_loaded >= 1:  # ✅ Chỉ cần ít nhất 1 model
                logger.info(
                    f"🎉 Successfully loaded {models_loaded}/3 models from {latest_timestamp}"
                )
                return True
            else:
                logger.warning(f"⚠️ No models loaded successfully")
                return False

        except Exception as e:
            logger.error(f"❌ Error loading existing models: {e}")
            return False


# ✅ SINGLETON INSTANCE
ml_model_service = MLModelService()
