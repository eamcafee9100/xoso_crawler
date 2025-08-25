# ml/models/gradient_boosting.py

import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple

import joblib
import numpy as np
import pandas as pd
from sklearn.ensemble import GradientBoostingClassifier, HistGradientBoostingClassifier
from sklearn.metrics import accuracy_score, classification_report, log_loss
from sklearn.model_selection import GridSearchCV, RandomizedSearchCV, TimeSeriesSplit
from sklearn.preprocessing import LabelEncoder

from ..features.extractors import DataLeakageValidator, LotteryFeatureExtractor
from .baseline import BasePredictionModel

logger = logging.getLogger(__name__)


class LotteryGradientBoostingModel(BasePredictionModel):
    """Gradient Boosting Classifier for lottery prediction"""

    def __init__(self, model_type: str = "gradient_boosting", **kwargs):
        """
        Initialize Gradient Boosting Model

        Args:
            model_type: 'gradient_boosting' or 'hist_gradient_boosting'
            **kwargs: Additional parameters for the model
        """
        super().__init__(f"LotteryGBM_{model_type}")
        self.model_type = model_type
        self.model = None
        self.label_encoder = LabelEncoder()
        self.feature_names = []
        self.feature_importance = {}
        self.training_history = []
        self.hyperparameters = kwargs

        # Initialize model based on type
        self._initialize_model(**kwargs)

    def _initialize_model(self, **kwargs):
        """Initialize the appropriate model based on type"""
        if self.model_type == "gradient_boosting":
            default_params = {
                "loss": "log_loss",
                "learning_rate": 0.1,
                "n_estimators": 100,
                "max_depth": 3,
                "subsample": 0.8,
                "max_features": "sqrt",
                "random_state": 42,
                "warm_start": True,
                "validation_fraction": 0.1,
                "n_iter_no_change": 10,
                "tol": 1e-4,
            }
            default_params.update(kwargs)
            self.model = GradientBoostingClassifier(**default_params)

        elif self.model_type == "hist_gradient_boosting":
            default_params = {
                "learning_rate": 0.1,
                "max_iter": 100,
                "max_depth": 3,
                "l2_regularization": 0.1,
                "early_stopping": True,
                "validation_fraction": 0.1,
                "n_iter_no_change": 10,
                "tol": 1e-4,
                "random_state": 42,
                "warm_start": True,
            }
            default_params.update(kwargs)
            self.model = HistGradientBoostingClassifier(**default_params)
        else:
            raise ValueError(f"Unknown model_type: {self.model_type}")

    def prepare_training_data(
        self, start_date: datetime.date, end_date: datetime.date
    ) -> Tuple[pd.DataFrame, pd.Series]:
        """
        Prepare training data with proper time series validation

        Args:
            start_date: Start date for training data
            end_date: End date for training data (exclusive)

        Returns:
            Tuple of (features_df, labels_series)
        """
        logger.info(f"Preparing training data from {start_date} to {end_date}")

        current_date = datetime.now().date()

        # FIX: Exclude the end_date and any future dates to prevent data leakage
        if end_date >= current_date:
            logger.warning(
                f"End date {end_date} is today or in future. Using {current_date - timedelta(days=2)} as end date."
            )
            end_date = current_date - timedelta(days=2)

        # Get all lottery results in the date range (EXCLUDING end_date)
        from results.models import KetQuaXoSo

        lottery_results = KetQuaXoSo.objects.filter(
            ngay__gte=start_date,
            ngay__lt=end_date,  # FIX: Use __lt instead of __lte to exclude end_date
        ).order_by("ngay")

        if not lottery_results.exists():
            raise ValueError(
                f"No lottery data found between {start_date} and {end_date}"
            )

        # Prepare features and labels for each date
        all_features = []
        all_labels = []

        for result in lottery_results:
            prediction_date = result.ngay

            # FIX: Ensure prediction_date is strictly in the past
            if prediction_date >= current_date - timedelta(days=1):
                logger.warning(f"Skipping {prediction_date} - data leakage prevention")
                continue

            # Ensure we have enough historical data before this date
            historical_count = KetQuaXoSo.objects.filter(
                ngay__lt=prediction_date
            ).count()
            if historical_count < 30:  # Need at least 30 days of history
                continue

            try:
                # FIX: Extract features with training context
                feature_extractor = LotteryFeatureExtractor(
                    prediction_date, context="training"
                )
                features_df = feature_extractor.extract_features_for_date()

                # Verify we didn't get empty features
                if features_df.empty:
                    logger.warning(f"No features extracted for {prediction_date}")
                    continue

                # Get actual results for this date
                actual_numbers = result.get_all_2digit_numbers()

                # Create labels (1 if number appeared, 0 if not)
                labels = [1 if f"{i:02d}" in actual_numbers else 0 for i in range(100)]

                # Add date information for tracking
                features_df["prediction_date"] = prediction_date

                all_features.append(features_df)
                all_labels.extend(labels)

            except Exception as e:
                logger.warning(f"Error preparing data for {prediction_date}: {e}")
                continue

        if not all_features:
            raise ValueError("No valid training data could be prepared")

        # Combine all features
        combined_features = pd.concat(all_features, ignore_index=True)
        combined_labels = pd.Series(all_labels)

        # Store feature names
        self.feature_names = [
            col for col in combined_features.columns if col != "prediction_date"
        ]

        logger.info(
            f"Prepared {len(combined_features)} training samples with {len(self.feature_names)} features"
        )

        return combined_features[self.feature_names], combined_labels

    def fit(
        self,
        X: pd.DataFrame = None,
        y: pd.Series = None,
        start_date: datetime.date = None,
        end_date: datetime.date = None,
    ) -> None:
        """
        Train the model

        Args:
            X: Feature matrix (optional if start_date/end_date provided)
            y: Labels (optional if start_date/end_date provided)
            start_date: Start date for training data
            end_date: End date for training data
        """
        training_start_time = datetime.now()

        # Prepare data if not provided
        if X is None or y is None:
            if start_date is None or end_date is None:
                # Default to last year of data, but exclude recent days to prevent leakage
                end_date = datetime.now().date() - timedelta(
                    days=2
                )  # FIX: Leave buffer
                start_date = end_date - timedelta(days=365)  # 1 year of data

            X, y = self.prepare_training_data(start_date, end_date)

        # Validate data
        if len(X) == 0 or len(y) == 0:
            raise ValueError("No training data available")

        if len(X) != len(y):
            raise ValueError(
                f"Feature matrix ({len(X)}) and labels ({len(y)}) must have same length"
            )

        logger.info(f"Training {self.model_name} with {len(X)} samples...")

        # Fit the model
        self.model.fit(X, y)

        # Calculate feature importance
        if hasattr(self.model, "feature_importances_"):
            self.feature_importance = dict(
                zip(self.feature_names, self.model.feature_importances_)
            )

        # Update model state
        self.is_trained = True
        self.training_data_size = len(X)
        self.last_train_date = datetime.now()

        # Store training history
        training_time = (datetime.now() - training_start_time).total_seconds()

        training_record = {
            "date": self.last_train_date,
            "training_samples": len(X),
            "training_time_seconds": training_time,
            "model_params": self.model.get_params(),
        }

        # Add model-specific metrics
        if hasattr(self.model, "train_score_"):
            training_record["train_scores"] = self.model.train_score_.tolist()
        if hasattr(self.model, "validation_scores_"):
            training_record["validation_scores"] = (
                self.model.validation_scores_.tolist()
            )

        self.training_history.append(training_record)

        logger.info(
            f"Training completed in {training_time:.2f}s. Model ready for prediction."
        )

    def predict_proba(
        self,
        X: pd.DataFrame = None,
        target_date: datetime.date = None,
        context: str = "prediction",
    ) -> np.ndarray:
        """
        Predict probabilities with context awareness

        Args:
            X: Feature matrix (optional if target_date provided)
            target_date: Date to predict for
            context: Prediction context for validation control
        """
        if not self.is_trained:
            raise ValueError("Model must be trained before prediction")

        # Prepare features if not provided
        if X is None:
            if target_date is None:
                target_date = datetime.now().date() + timedelta(days=1)
                context = "prediction"  # Force strict validation for future dates

            # Extract features with proper context
            feature_extractor = LotteryFeatureExtractor(target_date, context=context)
            X = feature_extractor.extract_features_for_date()

            # Ensure feature order matches training
            if self.feature_names:
                missing_features = set(self.feature_names) - set(X.columns)
                if missing_features:
                    logger.warning(f"Missing features: {missing_features}")
                    for feature in missing_features:
                        X[feature] = 0
                X = X[self.feature_names]

        # Get probabilities
        try:
            probabilities = self.model.predict_proba(X)[:, 1]
            return probabilities
        except Exception as e:
            logger.error(f"Error in prediction: {e}")
            # Return uniform probabilities as fallback
            return np.ones(100) / 100

    def predict_top_k_with_confidence(
        self,
        X: pd.DataFrame = None,
        target_date: datetime.date = None,
        k: int = 10,
        context: str = "prediction",
    ) -> Dict:
        """
        Predict top k numbers with confidence metrics

        Returns:
            Dictionary with predictions and confidence metrics
        """
        probabilities = self.predict_proba(X, target_date, context=context)

        # Get all numbers with probabilities
        numbers = [f"{i:02d}" for i in range(100)]
        number_probs = list(zip(numbers, probabilities))

        # Sort by probability
        sorted_predictions = sorted(number_probs, key=lambda x: x[1], reverse=True)
        top_k_predictions = sorted_predictions[:k]

        # Calculate confidence metrics
        top_k_probs = [prob for _, prob in top_k_predictions]
        confidence_score = np.mean(top_k_probs)
        probability_spread = max(top_k_probs) - min(top_k_probs)

        return {
            "predictions": [
                {"number": num, "probability": float(prob), "rank": i + 1}
                for i, (num, prob) in enumerate(top_k_predictions)
            ],
            "confidence_score": float(confidence_score),
            "probability_spread": float(probability_spread),
            "total_probability_mass": float(sum(top_k_probs)),
            "entropy": float(-np.sum(probabilities * np.log(probabilities + 1e-10))),
        }

    def get_feature_importance(self, top_n: int = 20) -> List[Tuple[str, float]]:
        """Get top N most important features"""
        if not self.feature_importance:
            return []

        sorted_importance = sorted(
            self.feature_importance.items(), key=lambda x: x[1], reverse=True
        )

        return sorted_importance[:top_n]

    def evaluate_on_validation_set(
        self, start_date: datetime.date, end_date: datetime.date
    ) -> Dict:
        """
        Evaluate model performance on a validation set

        Args:
            start_date: Start date for validation data
            end_date: End date for validation data

        Returns:
            Dictionary with evaluation metrics
        """
        logger.info(f"Evaluating model on validation set: {start_date} to {end_date}")

        # Prepare validation data
        X_val, y_val = self.prepare_training_data(start_date, end_date)

        # Make predictions
        y_pred_proba = self.model.predict_proba(X_val)[:, 1]
        y_pred = (y_pred_proba > 0.5).astype(int)

        # Calculate metrics
        accuracy = accuracy_score(y_val, y_pred)
        logloss = log_loss(y_val, y_pred_proba)

        # Top-K accuracy (how often actual numbers are in top K predictions)
        top_k_accuracies = {}
        for k in [5, 10, 15, 20]:
            top_k_acc = self._calculate_top_k_accuracy(y_val, y_pred_proba, k)
            top_k_accuracies[f"top_{k}_accuracy"] = top_k_acc

        evaluation_results = {
            "accuracy": float(accuracy),
            "log_loss": float(logloss),
            "validation_samples": len(X_val),
            **top_k_accuracies,
            "evaluation_date": datetime.now().isoformat(),
        }

        logger.info(
            f"Validation completed. Accuracy: {accuracy:.4f}, Log Loss: {logloss:.4f}"
        )

        return evaluation_results

    def _calculate_top_k_accuracy(
        self, y_true: pd.Series, y_pred_proba: np.ndarray, k: int
    ) -> float:
        """Calculate top-K accuracy for lottery prediction"""
        # Reshape data to group by prediction date (assuming 100 numbers per date)
        n_dates = len(y_true) // 100
        y_true_reshaped = y_true.values.reshape(n_dates, 100)
        y_pred_reshaped = y_pred_proba.reshape(n_dates, 100)

        correct_predictions = 0
        total_predictions = 0

        for i in range(n_dates):
            # Get actual numbers that appeared (indices where y_true = 1)
            actual_indices = np.where(y_true_reshaped[i] == 1)[0]

            # Get top K predicted indices
            top_k_indices = np.argsort(y_pred_reshaped[i])[-k:]

            # Count how many actual numbers are in top K
            intersection = set(actual_indices) & set(top_k_indices)
            correct_predictions += len(intersection)
            total_predictions += len(actual_indices)

        return correct_predictions / total_predictions if total_predictions > 0 else 0

    def save_model(self, filepath: str) -> None:
        """Save trained model to disk"""
        if not self.is_trained:
            raise ValueError("Cannot save untrained model")

        model_data = {
            "model": self.model,
            "model_type": self.model_type,
            "feature_names": self.feature_names,
            "feature_importance": self.feature_importance,
            "training_history": self.training_history,
            "model_info": self.get_model_info(),
        }

        joblib.dump(model_data, filepath)
        logger.info(f"Model saved to {filepath}")

    @classmethod
    def load_model(cls, filepath: str) -> "LotteryGradientBoostingModel":
        """Load trained model from disk"""
        model_data = joblib.load(filepath)

        # Create instance
        instance = cls(model_type=model_data["model_type"])

        # Restore model state
        instance.model = model_data["model"]
        instance.feature_names = model_data["feature_names"]
        instance.feature_importance = model_data["feature_importance"]
        instance.training_history = model_data["training_history"]
        instance.is_trained = True

        # Restore model info
        model_info = model_data["model_info"]
        instance.training_data_size = model_info["training_data_size"]
        instance.last_train_date = model_info["last_train_date"]

        logger.info(f"Model loaded from {filepath}")
        return instance


class HyperparameterOptimizer:
    """Optimize hyperparameters for lottery prediction models"""

    def __init__(self, model_type: str = "gradient_boosting"):
        self.model_type = model_type
        self.best_params = None
        self.best_score = None
        self.optimization_history = []

    def get_parameter_grid(self, search_type: str = "grid") -> Dict:
        """Get parameter grid for optimization"""
        if self.model_type == "gradient_boosting":
            if search_type == "grid":
                return {
                    "learning_rate": [0.01, 0.05, 0.1, 0.2],
                    "n_estimators": [100, 200, 300],
                    "max_depth": [3, 5, 7],
                    "subsample": [0.8, 0.9, 1.0],
                    "max_features": ["sqrt", "log2", None],
                }
            else:  # random search
                return {
                    "learning_rate": [0.01, 0.02, 0.05, 0.1, 0.15, 0.2],
                    "n_estimators": [50, 100, 150, 200, 250, 300, 400],
                    "max_depth": [2, 3, 4, 5, 6, 7, 8],
                    "subsample": [0.6, 0.7, 0.8, 0.9, 1.0],
                    "max_features": ["sqrt", "log2", None, 0.5, 0.7, 0.9],
                }

        elif self.model_type == "hist_gradient_boosting":
            if search_type == "grid":
                return {
                    "learning_rate": [0.01, 0.05, 0.1, 0.2],
                    "max_iter": [100, 200, 300],
                    "max_depth": [3, 5, 7, None],
                    "l2_regularization": [0, 0.1, 0.5, 1.0],
                }
            else:  # random search
                return {
                    "learning_rate": [0.01, 0.02, 0.05, 0.1, 0.15, 0.2, 0.3],
                    "max_iter": [50, 100, 150, 200, 250, 300, 400, 500],
                    "max_depth": [2, 3, 4, 5, 6, 7, 8, None],
                    "l2_regularization": [0, 0.01, 0.1, 0.2, 0.5, 1.0],
                }

    def optimize(
        self,
        X: pd.DataFrame,
        y: pd.Series,
        search_type: str = "random",
        n_iter: int = 50,
        cv_folds: int = 3,
    ) -> Dict:
        """
        Optimize hyperparameters using cross-validation

        Args:
            X: Feature matrix
            y: Labels
            search_type: 'grid' or 'random'
            n_iter: Number of iterations for random search
            cv_folds: Number of CV folds

        Returns:
            Dictionary with optimization results
        """
        logger.info(f"Starting {search_type} search hyperparameter optimization...")

        # Create base model
        base_model = LotteryGradientBoostingModel(model_type=self.model_type)

        # Get parameter grid
        param_grid = self.get_parameter_grid(search_type)

        # Use TimeSeriesSplit for cross-validation (important for time series data)
        cv = TimeSeriesSplit(n_splits=cv_folds)

        # Choose search method
        if search_type == "grid":
            search = GridSearchCV(
                base_model.model,
                param_grid,
                cv=cv,
                scoring="neg_log_loss",
                n_jobs=-1,
                verbose=1,
            )
        else:  # random search
            search = RandomizedSearchCV(
                base_model.model,
                param_grid,
                n_iter=n_iter,
                cv=cv,
                scoring="neg_log_loss",
                n_jobs=-1,
                verbose=1,
                random_state=42,
            )

        # Perform search
        search.fit(X, y)

        # Store results
        self.best_params = search.best_params_
        self.best_score = search.best_score_

        optimization_result = {
            "best_params": self.best_params,
            "best_score": float(self.best_score),
            "cv_results": search.cv_results_,
            "search_type": search_type,
            "optimization_date": datetime.now().isoformat(),
        }

        self.optimization_history.append(optimization_result)

        logger.info(f"Optimization completed. Best score: {self.best_score:.4f}")
        logger.info(f"Best parameters: {self.best_params}")

        return optimization_result

    def create_optimized_model(self) -> LotteryGradientBoostingModel:
        """Create model with optimized parameters"""
        if not self.best_params:
            raise ValueError("Must run optimization before creating optimized model")

        return LotteryGradientBoostingModel(
            model_type=self.model_type, **self.best_params
        )
