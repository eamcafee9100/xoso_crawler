# ml/models/ensemble.py

import logging
import math
from datetime import date, datetime, timedelta
from typing import Dict, List, Optional, Tuple, Union

import numpy as np
import pandas as pd
from sklearn.ensemble import VotingClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, log_loss

from .baseline import (
    BasePredictionModel,
    CyclicalPredictor,
    DayOfWeekPredictor,
    FrequencyBasedPredictor,
)
from .gradient_boosting import LotteryGradientBoostingModel

logger = logging.getLogger(__name__)


class WeightedEnsemble(BasePredictionModel):
    """Weighted ensemble of multiple models"""

    def __init__(self, models: List[BasePredictionModel], weights: List[float] = None):
        """
        Initialize weighted ensemble

        Args:
            models: List of prediction models
            weights: Weights for each model (None for equal weights)
        """
        super().__init__("WeightedEnsemble")
        self.models = models
        self.weights = weights or [1.0] * len(models)

        if len(self.weights) != len(self.models):
            raise ValueError("Number of weights must match number of models")

        # Normalize weights
        total_weight = sum(self.weights)
        self.weights = [w / total_weight for w in self.weights]

        self.model_performance_history = {}

    def fit(
        self,
        X: pd.DataFrame = None,
        y: pd.Series = None,
        start_date: datetime.date = None,
        end_date: datetime.date = None,
    ) -> None:
        """Train all constituent models"""
        logger.info(f"Training ensemble of {len(self.models)} models...")

        training_start = datetime.now()
        total_training_size = 0

        for i, model in enumerate(self.models):
            logger.info(f"Training model {i+1}/{len(self.models)}: {model.model_name}")

            try:
                if hasattr(model, "fit"):
                    model.fit(X=X, y=y, start_date=start_date, end_date=end_date)

                    total_training_size += getattr(model, "training_data_size", 0)

            except Exception as e:
                logger.error(f"Error training {model.model_name}: {e}")
                # Set weight to 0 for failed models
                self.weights[i] = 0

        # Renormalize weights after removing failed models
        total_weight = sum(self.weights)
        if total_weight > 0:
            self.weights = [w / total_weight for w in self.weights]
        else:
            raise ValueError("All models failed to train")

        self.is_trained = True
        self.training_data_size = total_training_size
        self.last_train_date = datetime.now()

        training_time = (datetime.now() - training_start).total_seconds()
        logger.info(f"Ensemble training completed in {training_time:.2f}s")

    def predict_top_k(
        self,
        X: pd.DataFrame = None,
        k: int = 10,
        target_date: datetime.date = None,
        context: str = "prediction",
    ) -> List[Tuple[str, float]]:
        """Predict top k numbers with context support"""
        probabilities = self.predict_proba(X, target_date=target_date, context=context)

        numbers = [f"{i:02d}" for i in range(100)]
        number_probs = list(zip(numbers, probabilities))
        sorted_predictions = sorted(number_probs, key=lambda x: x[1], reverse=True)

        return sorted_predictions[:k]

    def predict_top_k_with_confidence(self, target_date: date, k: int) -> Dict:
        """
        Generate top K predictions with confidence metrics

        Args:
            target_date: Date to predict for
            k: Number of predictions to return

        Returns:
            Dictionary with predictions and confidence metrics
        """
        # 1. Get probabilities for all numbers
        all_probs = self.predict_proba(
            target_date=target_date
        )  # Pass as keyword argument

        # 2. Handle numpy array format
        if isinstance(all_probs, np.ndarray):
            # Convert numpy array to dict with numbers as keys
            prob_dict = {f"{i:02d}": float(prob) for i, prob in enumerate(all_probs)}
        else:
            prob_dict = all_probs

        # 3. Sort and get top K
        sorted_numbers = sorted(prob_dict.items(), key=lambda x: x[1], reverse=True)
        top_k = sorted_numbers[:k]

        # 4. Calculate metrics
        top_k_mass = sum(p for _, p in top_k)
        entropy = -sum(p * math.log(p + 1e-10) for p in prob_dict.values() if p > 0)

        return {
            "predictions": [
                {"number": num, "probability": prob, "rank": i + 1}
                for i, (num, prob) in enumerate(top_k)
            ],
            "confidence_score": min(
                max(top_k_mass * (1 - entropy / math.log(100)), 0.0), 1.0
            ),
            "total_probability_mass": top_k_mass,
            "entropy": entropy,
        }

    def predict_proba(
        self,
        X: pd.DataFrame = None,
        target_date: datetime.date = None,
        context: str = "prediction",
    ) -> np.ndarray:
        """Ensemble prediction with context-aware error handling"""
        if not self.is_trained:
            raise ValueError("Ensemble must be trained before prediction")

        ensemble_probs = np.zeros(100)
        total_weight = 0
        successful_predictions = 0

        for model, weight in zip(self.models, self.weights):
            if weight == 0:
                continue

            try:
                # Context-aware model prediction
                if hasattr(model, "predict_proba"):
                    # Check method signature for supported parameters
                    import inspect

                    sig = inspect.signature(model.predict_proba)

                    if isinstance(
                        model,
                        (
                            FrequencyBasedPredictor,
                            DayOfWeekPredictor,
                            CyclicalPredictor,
                        ),
                    ):
                        if "target_date" in sig.parameters:
                            model_probs = model.predict_proba(
                                X, target_date=target_date
                            )
                        else:
                            model_probs = model.predict_proba(
                                X,
                                **({"target_date": target_date} if target_date else {}),
                            )
                    elif (
                        hasattr(model, "__class__")
                        and "LotteryGBM" in model.__class__.__name__
                    ):
                        if "context" in sig.parameters:
                            model_probs = model.predict_proba(
                                X, target_date=target_date, context=context
                            )
                        elif "target_date" in sig.parameters:
                            model_probs = model.predict_proba(
                                X, target_date=target_date
                            )
                        else:
                            model_probs = model.predict_proba(X)
                    else:
                        model_probs = model.predict_proba(X)

                    if len(model_probs) == 100:
                        ensemble_probs += weight * model_probs
                        total_weight += weight
                        successful_predictions += 1

            except Exception as e:
                # Context-aware error logging
                if context == "evaluation":
                    logger.debug(f"Model {model.model_name} failed in evaluation: {e}")
                else:
                    logger.warning(
                        f"Error getting predictions from {model.model_name}: {e}"
                    )
                continue

        if total_weight == 0:
            logger.warning("No models provided predictions, using uniform distribution")
            return np.ones(100) / 100

        # Normalize probabilities
        ensemble_probs = ensemble_probs / total_weight
        ensemble_probs = ensemble_probs / ensemble_probs.sum()

        return ensemble_probs

    def adaptive_weight_update(
        self, validation_start: datetime.date, validation_end: datetime.date
    ) -> None:
        """Update model weights based on recent performance"""
        logger.info("Updating ensemble weights based on validation performance...")

        model_scores = []

        for model in self.models:
            try:
                if hasattr(model, "evaluate_on_validation_set"):
                    eval_results = model.evaluate_on_validation_set(
                        validation_start, validation_end
                    )
                    score = eval_results.get(
                        "top_10_accuracy", 0
                    )  # Use top-10 accuracy as primary metric
                else:
                    # Fallback: manual evaluation
                    score = self._evaluate_model_performance(
                        model, validation_start, validation_end
                    )

                model_scores.append(score)

                # Store performance history
                if model.model_name not in self.model_performance_history:
                    self.model_performance_history[model.model_name] = []

                self.model_performance_history[model.model_name].append(
                    {
                        "date": datetime.now().isoformat(),
                        "score": score,
                        "validation_period": f"{validation_start} to {validation_end}",
                    }
                )

            except Exception as e:
                logger.warning(f"Error evaluating {model.model_name}: {e}")
                model_scores.append(0)

        # Update weights based on performance (softmax transformation)
        if max(model_scores) > 0:
            # Use softmax to convert scores to weights
            scores_array = np.array(model_scores)
            # Add small epsilon to avoid numerical issues
            scores_array = scores_array + 1e-8
            exp_scores = np.exp(
                scores_array * 10
            )  # Temperature = 10 for more pronounced differences
            new_weights = exp_scores / exp_scores.sum()

            self.weights = new_weights.tolist()

            logger.info("Updated ensemble weights:")
            for model, weight, score in zip(self.models, self.weights, model_scores):
                logger.info(f"  {model.model_name}: {weight:.4f} (score: {score:.4f})")

    def _evaluate_model_performance(
        self,
        model: BasePredictionModel,
        start_date: datetime.date,
        end_date: datetime.date,
    ) -> float:
        """Evaluate individual model performance"""
        from results.models import KetQuaXoSo

        # Get lottery results for validation period
        results = KetQuaXoSo.objects.filter(
            ngay__gte=start_date, ngay__lt=end_date
        ).order_by("ngay")

        if not results.exists():
            return 0

        correct_predictions = 0
        total_days = 0

        for result in results:
            try:
                # Get model predictions
                predictions = model.predict_top_k(None, k=10, target_date=result.ngay)
                predicted_numbers = [pred[0] for pred in predictions]

                # Get actual numbers
                actual_numbers = result.get_all_2digit_numbers()

                # Count correct predictions
                correct = len(set(predicted_numbers) & set(actual_numbers))
                correct_predictions += correct
                total_days += 1

            except Exception as e:
                logger.warning(f"Error evaluating model on {result.ngay}: {e}")
                continue

        # Return average correct predictions per day
        return correct_predictions / (total_days * 10) if total_days > 0 else 0

    def get_model_info(self) -> Dict:
        """Get ensemble model information"""
        base_info = super().get_model_info()
        base_info["constituent_models"] = [
            {
                "name": model.model_name,
                "weight": weight,
                "info": (
                    model.get_model_info() if hasattr(model, "get_model_info") else {}
                ),
            }
            for model, weight in zip(self.models, self.weights)
        ]
        base_info["performance_history"] = self.model_performance_history
        return base_info


class StackingEnsemble(BasePredictionModel):
    """Stacking ensemble with meta-learner"""

    def __init__(
        self,
        base_models: List[BasePredictionModel],
        meta_learner: Optional[BasePredictionModel] = None,
    ):
        """
        Initialize stacking ensemble

        Args:
            base_models: List of base prediction models
            meta_learner: Meta-learner model (LogisticRegression by default)
        """
        super().__init__("StackingEnsemble")
        self.base_models = base_models
        self.meta_learner = meta_learner or LogisticRegression(
            random_state=42, max_iter=1000
        )
        self.meta_features_names = []

    def fit(
        self,
        X: pd.DataFrame = None,
        y: pd.Series = None,
        start_date: datetime.date = None,
        end_date: datetime.date = None,
    ) -> None:
        """Train base models and meta-learner"""
        logger.info(
            f"Training stacking ensemble with {len(self.base_models)} base models..."
        )

        # Step 1: Train base models
        logger.info("Training base models...")
        for i, model in enumerate(self.base_models):
            logger.info(
                f"Training base model {i+1}/{len(self.base_models)}: {model.model_name}"
            )

            model.fit(X=X, y=y, start_date=start_date, end_date=end_date)

        # Step 2: Generate meta-features using cross-validation
        logger.info("Generating meta-features...")

        if X is None or y is None:
            if start_date is None or end_date is None:
                end_date = datetime.now().date()
                start_date = end_date - timedelta(days=365)

            # Prepare training data for meta-learner
            X, y = self._prepare_stacking_data(start_date, end_date)

        meta_X = self._generate_meta_features(X, y, start_date, end_date)

        # Step 3: Train meta-learner with robust preprocessing
        logger.info("Training meta-learner...")

        # Ensure no NaN values in meta-features
        meta_X = meta_X.fillna(0.5)  # Fill NaN with neutral probability

        # Validate meta-features
        if meta_X.isnull().any().any():
            logger.warning(
                "NaN values detected in meta-features, applying additional cleaning"
            )
            meta_X = meta_X.fillna(method="bfill").fillna(method="ffill").fillna(0)

        # Use robust meta-learner that handles edge cases
        from sklearn.ensemble import HistGradientBoostingClassifier

        self.meta_learner = HistGradientBoostingClassifier(
            random_state=42, max_iter=100, early_stopping=True, validation_fraction=0.1
        )

        self.meta_learner.fit(meta_X, y)

        self.is_trained = True
        self.training_data_size = len(X) if X is not None else 0
        self.last_train_date = datetime.now()

        logger.info("Stacking ensemble training completed")

    def _prepare_stacking_data(
        self, start_date: datetime.date, end_date: datetime.date
    ) -> Tuple[pd.DataFrame, pd.Series]:
        """Prepare data for stacking ensemble training"""
        # Use the same data preparation as gradient boosting models
        from .gradient_boosting import LotteryGradientBoostingModel

        temp_model = LotteryGradientBoostingModel()
        return temp_model.prepare_training_data(start_date, end_date)

    def _generate_meta_features(
        self,
        X: pd.DataFrame,
        y: pd.Series,
        start_date: datetime.date,
        end_date: datetime.date,
    ) -> pd.DataFrame:
        """Generate meta-features with validation context"""
        from sklearn.model_selection import TimeSeriesSplit

        # Use time series split for proper temporal validation
        cv = TimeSeriesSplit(n_splits=3)

        # Initialize meta-features matrix
        meta_X = np.zeros((len(X), len(self.base_models)))

        # Date mapping for context-aware feature extraction
        date_range = pd.date_range(start=start_date, end=end_date, freq="D")
        available_dates = [d.date() for d in date_range if d.date() <= end_date]

        for fold, (train_idx, val_idx) in enumerate(cv.split(X)):
            logger.info(f"Generating meta-features for fold {fold+1}/3")

            X_train_fold = X.iloc[train_idx]
            y_train_fold = y.iloc[train_idx]

            # Get validation dates
            val_dates = [
                available_dates[i] for i in val_idx if i < len(available_dates)
            ]

            for i, model in enumerate(self.base_models):
                try:
                    # Train model for this fold with proper context
                    if isinstance(
                        model,
                        (
                            FrequencyBasedPredictor,
                            DayOfWeekPredictor,
                            CyclicalPredictor,
                        ),
                    ):
                        # Train baseline models with safe date range
                        safe_end_date = min(
                            end_date, datetime.now().date() - timedelta(days=1)
                        )
                        model.fit(start_date=start_date, end_date=safe_end_date)
                    else:
                        # Train ML models with training context
                        model.fit(X=X_train_fold, y=y_train_fold)

                    # Generate predictions for validation fold
                    for j, val_idx_single in enumerate(val_idx):
                        try:
                            if val_idx_single < len(available_dates):
                                val_date = available_dates[val_idx_single]
                                # Use validation context to suppress warnings
                                if hasattr(model, "predict_proba"):
                                    import inspect

                                    sig = inspect.signature(model.predict_proba)
                                    if "context" in sig.parameters:
                                        pred_proba = model.predict_proba(
                                            None,
                                            target_date=val_date,
                                            context="validation",
                                        )
                                    elif "target_date" in sig.parameters:
                                        pred_proba = model.predict_proba(
                                            None, target_date=val_date
                                        )
                                    else:
                                        pred_proba = model.predict_proba(None)

                                    # Use average probability as meta-feature
                                    meta_X[val_idx_single, i] = np.mean(pred_proba)
                                else:
                                    meta_X[val_idx_single, i] = 0.5
                        except Exception as inner_e:
                            logger.debug(
                                f"Error generating meta-feature for {model.model_name} on validation sample: {inner_e}"
                            )
                            meta_X[val_idx_single, i] = 0.5

                except Exception as e:
                    logger.warning(
                        f"Error generating meta-features for {model.model_name}: {e}"
                    )
                    # Fill with neutral predictions
                    meta_X[val_idx, i] = 0.5

        # Convert to DataFrame with proper column names
        meta_feature_names = [
            f"model_{i}_{model.model_name}" for i, model in enumerate(self.base_models)
        ]
        meta_df = pd.DataFrame(meta_X, columns=meta_feature_names)

        # Handle any remaining NaN values
        meta_df = meta_df.fillna(0.5)

        return meta_df

    def predict_proba(
        self, X: pd.DataFrame = None, target_date: datetime.date = None
    ) -> np.ndarray:
        """Predict using stacking ensemble"""
        if not self.is_trained:
            raise ValueError("Stacking ensemble must be trained before prediction")

        # Get base model predictions
        base_predictions = []

        for model in self.base_models:
            try:
                if hasattr(model, "predict_proba"):
                    if "target_date" in model.predict_proba.__code__.co_varnames:
                        probs = model.predict_proba(X, target_date=target_date)
                    else:
                        probs = model.predict_proba(X)

                    # For multi-class classification, we need probabilities for each number
                    # Since we're predicting 100 numbers, we need to reshape appropriately
                    if len(probs) == 100:
                        # Average probability across all numbers for meta-learning
                        base_predictions.append(np.mean(probs))
                    else:
                        base_predictions.append(probs[0] if len(probs) > 0 else 0.5)

            except Exception as e:
                logger.warning(
                    f"Error getting predictions from {model.model_name}: {e}"
                )
                base_predictions.append(0.5)  # Neutral prediction

        # Create meta-features
        meta_X = pd.DataFrame([base_predictions], columns=self.meta_features_names)

        # Get meta-learner prediction
        if hasattr(self.meta_learner, "predict_proba"):
            meta_prob = self.meta_learner.predict_proba(meta_X)[
                0, 1
            ]  # Probability of class 1
        else:
            meta_prob = self.meta_learner.predict(meta_X)[0]

        # For now, return uniform probabilities scaled by meta-learner confidence
        # This is a simplified approach - could be enhanced with more sophisticated combination
        base_ensemble_probs = np.array(base_predictions)
        if len(base_ensemble_probs) == len(self.base_models):
            # Weight base model predictions and return as number probabilities
            weighted_probs = np.zeros(100)
            for i, model in enumerate(self.base_models):
                try:
                    if hasattr(model, "predict_proba"):
                        model_probs = (
                            model.predict_proba(X, target_date=target_date)
                            if hasattr(model, "predict_proba")
                            else np.random.random(100)
                        )
                        if len(model_probs) == 100:
                            weighted_probs += base_ensemble_probs[i] * model_probs
                except:
                    continue

            # Normalize
            weighted_probs = (
                weighted_probs / weighted_probs.sum()
                if weighted_probs.sum() > 0
                else np.ones(100) / 100
            )
            return weighted_probs * meta_prob + (1 - meta_prob) * (np.ones(100) / 100)

        # Fallback: uniform distribution
        return np.ones(100) / 100


class DynamicEnsemble(BasePredictionModel):
    """Dynamic ensemble that adapts weights based on recent performance"""

    def __init__(self, models: List[BasePredictionModel], adaptation_window: int = 30):
        """
        Initialize dynamic ensemble

        Args:
            models: List of prediction models
            adaptation_window: Number of days to look back for performance evaluation
        """
        super().__init__("DynamicEnsemble")
        self.models = models
        self.adaptation_window = adaptation_window
        self.current_weights = [1.0 / len(models)] * len(
            models
        )  # Start with equal weights
        self.performance_history = []
        self.weight_history = []

    def fit(
        self,
        X: pd.DataFrame = None,
        y: pd.Series = None,
        start_date: datetime.date = None,
        end_date: datetime.date = None,
    ) -> None:
        """Train all models and initialize dynamic weighting"""
        logger.info(f"Training dynamic ensemble with {len(self.models)} models...")

        # Train all base models
        for i, model in enumerate(self.models):
            logger.info(f"Training model {i+1}/{len(self.models)}: {model.model_name}")

            try:
                model.fit(X=X, y=y, start_date=start_date, end_date=end_date)
            except Exception as e:
                logger.error(f"Error training {model.model_name}: {e}")
                # Keep equal weight for failed models initially

        # Initialize performance tracking
        self._initialize_performance_tracking()

        self.is_trained = True
        self.training_data_size = sum(
            getattr(model, "training_data_size", 0) for model in self.models
        )
        self.last_train_date = datetime.now()

        logger.info("Dynamic ensemble training completed")

    def _initialize_performance_tracking(self):
        """Initialize performance tracking for dynamic weighting"""
        end_date = datetime.now().date()
        start_date = end_date - timedelta(days=self.adaptation_window)

        # Get initial performance for each model
        self._update_performance_scores(start_date, end_date)

    def predict_proba(
        self,
        X: pd.DataFrame = None,
        target_date: datetime.date = None,
        context: str = "prediction",
    ) -> np.ndarray:
        """Predict using dynamic ensemble with adaptive weights"""
        if not self.is_trained:
            raise ValueError("Dynamic ensemble must be trained before prediction")

        # Update weights before prediction
        self._update_weights_if_needed(target_date)

        # Get weighted ensemble prediction
        ensemble_probs = np.zeros(100)
        total_weight = 0

        for model, weight in zip(self.models, self.current_weights):
            if weight == 0:
                continue

            try:
                if hasattr(model, "predict_proba"):
                    # Check if model supports context parameter
                    import inspect

                    sig = inspect.signature(model.predict_proba)

                    if "context" in sig.parameters:
                        model_probs = model.predict_proba(
                            X, target_date=target_date, context=context
                        )
                    elif "target_date" in sig.parameters:
                        model_probs = model.predict_proba(X, target_date=target_date)
                    else:
                        model_probs = model.predict_proba(X)

                    if len(model_probs) == 100:
                        ensemble_probs += weight * model_probs
                        total_weight += weight

            except Exception as e:
                if context != "evaluation":
                    logger.warning(
                        f"Error getting predictions from {model.model_name}: {e}"
                    )
                continue

        if total_weight == 0:
            return np.ones(100) / 100  # Uniform fallback

        # Normalize
        ensemble_probs = ensemble_probs / total_weight
        ensemble_probs = ensemble_probs / ensemble_probs.sum()

        return ensemble_probs

    def _update_weights_if_needed(self, target_date: datetime.date = None):
        """Update weights if performance has changed significantly"""
        if target_date is None:
            target_date = datetime.now().date()

        # Check if we need to update (daily updates)
        if (
            not self.weight_history
            or (
                target_date
                - datetime.fromisoformat(self.weight_history[-1]["date"]).date()
            ).days
            >= 1
        ):

            end_date = target_date - timedelta(days=1)  # Don't include target date
            start_date = end_date - timedelta(days=self.adaptation_window)

            self._update_performance_scores(start_date, end_date)
            self._compute_dynamic_weights()

    def _update_performance_scores(
        self, start_date: datetime.date, end_date: datetime.date
    ):
        """Update performance scores for all models"""
        from results.models import KetQuaXoSo

        # Get lottery results for evaluation period
        results = KetQuaXoSo.objects.filter(
            ngay__gte=start_date, ngay__lt=end_date
        ).order_by("ngay")

        if not results.exists():
            logger.warning(
                f"No lottery data available for performance evaluation: {start_date} to {end_date}"
            )
            return

        model_scores = []

        for model in self.models:
            total_correct = 0
            total_predictions = 0

            for result in results:
                try:
                    # Get top 10 predictions with evaluation context
                    predictions = model.predict_top_k(
                        None, k=10, target_date=result.ngay, context="evaluation"
                    )
                    predicted_numbers = [pred[0] for pred in predictions]

                    # Get actual numbers
                    actual_numbers = result.get_all_2digit_numbers()

                    # Count correct predictions
                    correct = len(set(predicted_numbers) & set(actual_numbers))
                    total_correct += correct
                    total_predictions += 10  # Always predict 10 numbers

                except Exception as e:
                    logger.warning(
                        f"Error evaluating {model.model_name} on {result.ngay}: {e}"
                    )
                    continue

            # Calculate accuracy rate
            accuracy = total_correct / total_predictions if total_predictions > 0 else 0
            model_scores.append(accuracy)

        # Store performance history
        performance_record = {
            "date": end_date.isoformat(),
            "evaluation_period": f"{start_date} to {end_date}",
            "model_scores": {
                model.model_name: score
                for model, score in zip(self.models, model_scores)
            },
        }

        self.performance_history.append(performance_record)

        # Keep only recent history
        if len(self.performance_history) > 30:
            self.performance_history = self.performance_history[-30:]

    def _compute_dynamic_weights(self):
        """Compute new weights based on recent performance"""
        if not self.performance_history:
            return

        # Get recent performance scores
        recent_scores = self.performance_history[-1]["model_scores"]
        model_scores = [recent_scores.get(model.model_name, 0) for model in self.models]

        # Apply exponential smoothing if we have weight history
        if self.weight_history:
            prev_weights = self.weight_history[-1]["weights"]
            alpha = 0.3  # Smoothing factor

            # Compute new weights with smoothing
            new_raw_weights = []
            for i, (prev_weight, current_score) in enumerate(
                zip(prev_weights, model_scores)
            ):
                # Convert score to weight (add small epsilon to avoid zeros)
                score_weight = current_score + 1e-6
                smoothed_weight = alpha * score_weight + (1 - alpha) * prev_weight
                new_raw_weights.append(smoothed_weight)
        else:
            # First time: use scores directly
            new_raw_weights = [score + 1e-6 for score in model_scores]

        # Normalize weights
        total_weight = sum(new_raw_weights)
        if total_weight > 0:
            self.current_weights = [w / total_weight for w in new_raw_weights]
        else:
            self.current_weights = [1.0 / len(self.models)] * len(self.models)

        # Store weight history
        weight_record = {
            "date": datetime.now().date().isoformat(),
            "weights": self.current_weights.copy(),
            "model_scores": model_scores,
        }

        self.weight_history.append(weight_record)

        # Keep only recent weight history
        if len(self.weight_history) > 30:
            self.weight_history = self.weight_history[-30:]

        logger.info("Updated dynamic ensemble weights:")
        for model, weight, score in zip(
            self.models, self.current_weights, model_scores
        ):
            logger.info(
                f"  {model.model_name}: {weight:.4f} (recent score: {score:.4f})"
            )

    def get_weight_trend(self, days: int = 14) -> Dict:
        """Get weight trends over recent days"""
        if len(self.weight_history) < 2:
            return {}

        recent_history = (
            self.weight_history[-days:]
            if len(self.weight_history) >= days
            else self.weight_history
        )

        trends = {}
        for i, model in enumerate(self.models):
            weights_over_time = [record["weights"][i] for record in recent_history]

            if len(weights_over_time) >= 2:
                # Simple trend calculation (slope)
                x = list(range(len(weights_over_time)))
                y = weights_over_time

                # Linear regression slope
                n = len(x)
                slope = (n * sum(x[i] * y[i] for i in range(n)) - sum(x) * sum(y)) / (
                    n * sum(x[i] ** 2 for i in range(n)) - sum(x) ** 2
                )

                trends[model.model_name] = {
                    "current_weight": self.current_weights[i],
                    "trend_slope": slope,
                    "trend_direction": (
                        "increasing"
                        if slope > 0.001
                        else "decreasing" if slope < -0.001 else "stable"
                    ),
                }

        return trends

    def get_model_info(self) -> Dict:
        """Get dynamic ensemble information"""
        base_info = super().get_model_info()
        base_info.update(
            {
                "adaptation_window_days": self.adaptation_window,
                "current_weights": dict(
                    zip(
                        [model.model_name for model in self.models],
                        self.current_weights,
                    )
                ),
                "weight_trends": self.get_weight_trend(),
                "performance_history_length": len(self.performance_history),
                "constituent_models": [
                    {
                        "name": model.model_name,
                        "current_weight": weight,
                        "info": (
                            model.get_model_info()
                            if hasattr(model, "get_model_info")
                            else {}
                        ),
                    }
                    for model, weight in zip(self.models, self.current_weights)
                ],
            }
        )
        return base_info


class ModelFactory:
    """Factory class for creating different types of ensemble models"""

    @staticmethod
    def create_default_ensemble() -> WeightedEnsemble:
        """Create a default ensemble with baseline and ML models"""
        from .gradient_boosting import LotteryGradientBoostingModel

        models = [
            # Baseline models
            FrequencyBasedPredictor(lookback_days=90),
            DayOfWeekPredictor(lookback_days=180),
            CyclicalPredictor(lookback_days=365),
            # ML models
            LotteryGradientBoostingModel(model_type="gradient_boosting"),
            LotteryGradientBoostingModel(model_type="hist_gradient_boosting"),
        ]

        # Weights: higher for ML models
        weights = [0.1, 0.1, 0.1, 0.35, 0.35]

        return WeightedEnsemble(models, weights)

    @staticmethod
    def create_dynamic_ensemble() -> DynamicEnsemble:
        """Create a dynamic ensemble that adapts weights"""
        from .gradient_boosting import LotteryGradientBoostingModel

        models = [
            FrequencyBasedPredictor(lookback_days=60),
            FrequencyBasedPredictor(lookback_days=180),
            DayOfWeekPredictor(lookback_days=180),
            CyclicalPredictor(lookback_days=365),
            LotteryGradientBoostingModel(
                model_type="gradient_boosting", learning_rate=0.05
            ),
            LotteryGradientBoostingModel(
                model_type="gradient_boosting", learning_rate=0.1
            ),
            LotteryGradientBoostingModel(model_type="hist_gradient_boosting"),
        ]

        return DynamicEnsemble(models, adaptation_window=21)

    @staticmethod
    def create_stacking_ensemble() -> StackingEnsemble:
        """Create a stacking ensemble with meta-learner"""
        from .gradient_boosting import LotteryGradientBoostingModel

        base_models = [
            FrequencyBasedPredictor(lookback_days=90),
            DayOfWeekPredictor(lookback_days=180),
            CyclicalPredictor(lookback_days=365),
            LotteryGradientBoostingModel(model_type="gradient_boosting"),
            LotteryGradientBoostingModel(model_type="hist_gradient_boosting"),
        ]

        return StackingEnsemble(base_models)
