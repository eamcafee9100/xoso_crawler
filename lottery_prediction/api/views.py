# api/views.py

import json
import logging
import math
import os
from datetime import date, datetime, timedelta
from typing import Dict, List, Optional

import joblib
from django.conf import settings
from django.utils import timezone
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from lottery_prediction.ml.features.extractors import DataLeakageValidator
from lottery_prediction.ml.models.ensemble import ModelFactory
from results.models import KetQuaXoSo, MethodCyclicalPerformance

from .serializers import PredictionRequestSerializer, PredictionResponseSerializer

logger = logging.getLogger(__name__)


class PredictionAPIView(APIView):
    """
    Main API endpoint for lottery number predictions
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.model_cache = {}
        self.model_load_time = {}

    def post(self, request):
        """
        Generate lottery predictions for a specific date

        Request body:
        {
            "prediction_date": "2025-07-26",
            "model_type": "ensemble",
            "top_k": 10,
            "context": "prediction"  // or "evaluation" for historical testing
        }
        """
        try:
            # Validate request data
            serializer = PredictionRequestSerializer(data=request.data)
            logger.info(f"Received prediction request: {request.data}")
            if not serializer.is_valid():
                return Response(
                    {"error": "Invalid request data", "details": serializer.errors},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            validated_data = serializer.validated_data
            prediction_date = validated_data.get(
                "prediction_date", self._get_default_prediction_date()
            )
            model_type = validated_data.get("model_type", "gradient_boosting")
            top_k = validated_data.get("top_k", 10)
            context = validated_data.get(
                "prediction_context", "prediction"
            )  # Fix field name

            # Validate prediction date with context
            try:
                DataLeakageValidator.validate_prediction_request(
                    prediction_date, context
                )
            except ValueError as e:
                return Response(
                    {"error": "Invalid prediction date", "details": str(e)},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            # Generate predictions
            prediction_result = self._generate_predictions(
                prediction_date, model_type, top_k, context
            )

            # Log prediction request
            logger.info(
                f"Prediction generated for {prediction_date} using {model_type} model"
            )

            return Response(prediction_result, status=status.HTTP_200_OK)

        except Exception as e:
            logger.error(f"Error generating predictions: {e}", exc_info=True)
            return Response(
                {"error": "Internal server error", "details": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    def _get_default_prediction_date(self) -> date:
        """Get default prediction date (tomorrow)"""
        return timezone.now().date() + timedelta(days=1)

    def _generate_predictions(
        self,
        prediction_date: date,
        model_type: str,
        top_k: int,
        context: str = "prediction",
    ) -> Dict:
        """Generate predictions using specified model"""
        start_time = timezone.now()

        # Load model
        model = self._load_model(model_type)

        # Generate predictions
        if hasattr(model, "predict_top_k_with_confidence"):
            # Use confidence method if available (gradient boosting, ensemble)
            try:
                # Try with context parameter first
                prediction_results = model.predict_top_k_with_confidence(
                    target_date=prediction_date, k=top_k, context=context
                )
            except TypeError:
                # Fallback for models that don't support context parameter
                prediction_results = model.predict_top_k_with_confidence(
                    target_date=prediction_date, k=top_k
                )
        else:
            # Fallback for baseline models
            # Create dummy DataFrame for baseline models that expect X parameter
            import pandas as pd

            dummy_x = pd.DataFrame()
            top_predictions = model.predict_top_k(
                X=dummy_x, k=top_k, target_date=prediction_date
            )

            # Convert to expected format
            predictions = [
                {"number": num, "probability": float(prob), "rank": i + 1}
                for i, (num, prob) in enumerate(top_predictions)
            ]

            # Calculate basic confidence metrics
            probabilities = [prob for _, prob in top_predictions]
            confidence_score = (
                sum(probabilities) / len(probabilities) if probabilities else 0
            )
            total_prob_mass = sum(probabilities)

            prediction_results = {
                "predictions": predictions,
                "confidence_score": confidence_score,
                "total_probability_mass": total_prob_mass,
                "entropy": -sum(p * math.log(p + 1e-10) for p in probabilities),
            }

        # Get reference date (last available data)
        reference_date = DataLeakageValidator.get_safe_reference_date(prediction_date)

        # Calculate data quality score
        data_quality_score = self._calculate_data_quality_score(reference_date)

        # Get model information
        model_info = model.get_model_info()

        # Prepare response
        response_data = {
            "prediction_date": prediction_date.isoformat(),
            "reference_date": reference_date.isoformat(),
            "top_k_predictions": prediction_results["predictions"],
            "model_info": {
                "model_name": model_info.get("model_name", model_type),
                "model_type": model_type,
                "confidence_score": prediction_results["confidence_score"],
                "total_probability_mass": prediction_results["total_probability_mass"],
                "entropy": prediction_results["entropy"],
                "last_train_date": model_info.get("last_train_date"),
                "training_data_size": model_info.get("training_data_size", 0),
            },
            "data_quality": {
                "score": data_quality_score,
                "reference_data_points": self._count_reference_data_points(
                    reference_date
                ),
                "data_freshness_days": (prediction_date - reference_date).days,
            },
            "metadata": {
                "prediction_generated_at": start_time.isoformat(),
                "processing_time_seconds": (
                    timezone.now() - start_time
                ).total_seconds(),
                "api_version": "1.0",
            },
        }

        # Add ensemble-specific information if applicable
        if hasattr(model, "get_weight_trend"):
            response_data["model_info"]["weight_trends"] = model.get_weight_trend()

        if hasattr(model, "current_weights") and hasattr(model, "models"):
            response_data["model_info"]["current_weights"] = dict(
                zip([m.model_name for m in model.models], model.current_weights)
            )

        return response_data

    def _load_model(self, model_type: str):
        """Load and cache model"""
        model_cache_key = f"{model_type}_model"

        # Check if model is already cached and not too old
        if (
            model_cache_key in self.model_cache
            and model_cache_key in self.model_load_time
        ):

            # Reload model if it's older than 1 hour
            time_since_load = (
                timezone.now() - self.model_load_time[model_cache_key]
            ).total_seconds()
            if time_since_load < 3600:  # 1 hour
                return self.model_cache[model_cache_key]

        # Load model from disk or create new one
        model_path = os.path.join(
            settings.BASE_DIR, "models", f"{model_type}_model.pkl"
        )

        if os.path.exists(model_path):
            logger.info(f"Loading {model_type} model from {model_path}")
            try:
                if model_type in ["gradient_boosting", "hist_gradient_boosting"]:
                    from lottery_prediction.ml.models.gradient_boosting import (
                        LotteryGradientBoostingModel,
                    )

                    model = LotteryGradientBoostingModel.load_model(model_path)
                else:
                    model = joblib.load(model_path)

                # Cache model
                self.model_cache[model_cache_key] = model
                self.model_load_time[model_cache_key] = timezone.now()

                return model

            except Exception as e:
                logger.warning(f"Error loading model from {model_path}: {e}")
                # Fallback to creating new model

        # Create new model if loading failed or file doesn't exist
        logger.info(f"Creating new {model_type} model")
        model = self._create_new_model(model_type)

        # Cache model
        self.model_cache[model_cache_key] = model
        self.model_load_time[model_cache_key] = timezone.now()

        return model

    def predict_top_k_with_confidence(self, target_date: date, k: int) -> Dict:
        """
        Generate top K predictions with confidence metrics for a target date

        Args:
            target_date: Date to predict for
            k: Number of top predictions to return

        Returns:
            Dictionary containing:
            - predictions: List of predicted numbers with probabilities
            - confidence_score: Overall confidence score
            - total_probability_mass: Sum of probabilities for top K
            - entropy: Measure of prediction uncertainty
        """
        # 1. Generate probabilities for all numbers (00-99)
        all_probs = self._calculate_number_probabilities(target_date)

        # 2. Sort numbers by probability (descending)
        sorted_numbers = sorted(all_probs.items(), key=lambda x: x[1], reverse=True)

        # 3. Take top K predictions
        top_k_predictions = sorted_numbers[:k]

        # 4. Calculate confidence metrics
        confidence_metrics = self._calculate_confidence_metrics(
            top_k_predictions, all_probs
        )

        # 5. Format the response
        predictions = [
            {"number": num, "probability": prob, "rank": i + 1}
            for i, (num, prob) in enumerate(top_k_predictions)
        ]

        return {
            "predictions": predictions,
            "confidence_score": confidence_metrics["confidence_score"],
            "total_probability_mass": confidence_metrics["total_probability_mass"],
            "entropy": confidence_metrics["entropy"],
        }

    def _calculate_number_probabilities(self, target_date: date) -> Dict[str, float]:
        """
        Calculate probabilities for all numbers (00-99) for a given date

        Args:
            target_date: Date to predict for

        Returns:
            Dictionary mapping numbers (as strings) to probabilities
        """
        # This will vary based on your model implementation
        # Here's a simplified version:

        # 1. Get base probabilities (could be from frequency analysis)
        base_probs = self._get_base_probabilities()

        # 2. Apply date-specific adjustments
        date_adjusted_probs = self._apply_date_adjustments(base_probs, target_date)

        # 3. Normalize to ensure sum to 1
        total = sum(date_adjusted_probs.values())
        return {num: prob / total for num, prob in date_adjusted_probs.items()}

    def _calculate_confidence_metrics(
        self, top_k_predictions: List, all_probs: Dict
    ) -> Dict:
        """
        Calculate various confidence metrics for predictions

        Args:
            top_k_predictions: List of (number, probability) tuples
            all_probs: Dictionary of all number probabilities

        Returns:
            Dictionary of confidence metrics
        """
        # 1. Total probability mass in top K
        top_k_mass = sum(prob for _, prob in top_k_predictions)

        # 2. Entropy calculation (measure of uncertainty)
        entropy = -sum(p * math.log(p) for p in all_probs.values() if p > 0)

        # 3. Confidence score (custom metric, could be based on top_k_mass and entropy)
        confidence_score = top_k_mass * (
            1 - entropy / math.log(100)
        )  # log(100) is max entropy

        return {
            "confidence_score": min(max(confidence_score, 0), 1),  # Clamp to 0-1
            "total_probability_mass": top_k_mass,
            "entropy": entropy,
        }

    def _get_base_probabilities(self) -> Dict[str, float]:
        """
        Get base probabilities for numbers based on historical frequency
        """
        # Implement your frequency analysis here
        # This is a simplified example with uniform distribution
        return {f"{i:02d}": 1.0 for i in range(100)}

    def _apply_date_adjustments(
        self, base_probs: Dict[str, float], target_date: date
    ) -> Dict[str, float]:
        """
        Adjust probabilities based on date-specific factors
        """
        # Implement your date-based adjustments here
        # Example: day of week effects, seasonal patterns, etc.
        adjusted_probs = base_probs.copy()

        # Example adjustment - boost numbers that frequently appear on this weekday
        weekday = target_date.weekday()
        weekday_boost_numbers = self._get_weekday_boost_numbers(weekday)

        for num in weekday_boost_numbers:
            adjusted_probs[num] *= 1.5  # Boost by 50%

        return adjusted_probs

    def _get_weekday_boost_numbers(self, weekday: int) -> List[str]:
        """
        Get numbers that should be boosted for a specific weekday
        """
        # Implement your weekday-specific logic here
        # This is just an example
        weekday_patterns = {
            0: ["12", "34", "56"],  # Monday
            1: ["23", "45", "67"],  # Tuesday
            # ... etc for other weekdays
        }
        return weekday_patterns.get(weekday, [])

    def _create_new_model(self, model_type: str):
        """Create and train a new model"""
        if model_type == "ensemble":
            model = ModelFactory.create_default_ensemble()
        elif model_type == "dynamic_ensemble":
            model = ModelFactory.create_dynamic_ensemble()
        elif model_type == "gradient_boosting":
            from lottery_prediction.ml.models.gradient_boosting import (
                LotteryGradientBoostingModel,
            )
            model = LotteryGradientBoostingModel(model_type="gradient_boosting")
        elif model_type == "hist_gradient_boosting":
            from lottery_prediction.ml.models.gradient_boosting import (
                LotteryGradientBoostingModel,
            )
            model = LotteryGradientBoostingModel(model_type="hist_gradient_boosting")
        elif model_type == "frequency_based":
            from lottery_prediction.ml.models.baseline import FrequencyBasedPredictor
            model = FrequencyBasedPredictor()
        elif model_type == "day_of_week":
            from lottery_prediction.ml.models.baseline import DayOfWeekPredictor
            model = DayOfWeekPredictor()
        elif model_type == "cyclical":
            from lottery_prediction.ml.models.baseline import CyclicalPredictor
            model = CyclicalPredictor()
        else:
            raise ValueError(f"Unknown model type: {model_type}")

        # Quick training with recent data
        end_date = timezone.now().date()
        start_date = end_date - timedelta(days=180)  # 6 months of data

        logger.info(
            f"Quick training {model_type} model with data from {start_date} to {end_date}"
        )
        
        # Baseline models use different fit signature
        if model_type in ["frequency_based", "day_of_week", "cyclical"]:
            model.fit(start_date=start_date, end_date=end_date)
        else:
            model.fit(start_date=start_date, end_date=end_date)

        return model

    def _calculate_data_quality_score(self, reference_date: date) -> float:
        """Calculate data quality score based on recent data availability"""
        # Check data availability in the last 30 days
        start_date = reference_date - timedelta(days=30)

        available_days = KetQuaXoSo.objects.filter(
            ngay__gte=start_date, ngay__lte=reference_date
        ).count()

        # Expected days (excluding weekends if lottery doesn't run on weekends)
        expected_days = 30  # Simplified - could be more sophisticated

        # Check for data completeness
        incomplete_records = 0
        for result in KetQuaXoSo.objects.filter(
            ngay__gte=start_date, ngay__lte=reference_date
        ):
            numbers = result.get_all_2digit_numbers()
            if len(numbers) < 5:  # Assuming normal result has at least 5 numbers
                incomplete_records += 1

        # Calculate score
        availability_score = min(available_days / expected_days, 1.0)
        completeness_score = max(0, 1.0 - (incomplete_records / max(available_days, 1)))

        overall_score = availability_score * 0.7 + completeness_score * 0.3

        return round(overall_score, 3)

    def _count_reference_data_points(self, reference_date: date) -> int:
        """Count available data points up to reference date"""
        return KetQuaXoSo.objects.filter(ngay__lte=reference_date).count()


class ModelPerformanceView(APIView):
    """
    API endpoint for retrieving model performance metrics
    """

    def get(self, request):
        """
        Get model performance metrics

        Query parameters:
        - model_name: Name of the model (optional)
        - days: Number of days to look back (default: 30)
        - metric_type: Type of metrics to return (default: all)
        """
        try:
            model_name = request.query_params.get("model_name")
            days = int(request.query_params.get("days", 30))
            metric_type = request.query_params.get("metric_type", "all")

            end_date = timezone.now().date()
            start_date = end_date - timedelta(days=days)

            # Get performance data
            performance_query = MethodCyclicalPerformance.objects.filter(
                year__gte=start_date.year, month__gte=start_date.month
            )

            if model_name:
                performance_query = performance_query.filter(method_name=model_name)

            performance_data = performance_query.order_by("-year", "-month")

            # Process performance data
            results = []
            for perf in performance_data:
                perf_data = {
                    "model_name": perf.method_name,
                    "year": perf.year,
                    "month": perf.month,
                    "hit_rate": perf.hit_rate,
                    "total_hit_days": perf.total_hit_days,
                    "total_days": perf.total_days,
                    "fatigue_threshold_reached": perf.fatigue_threshold_reached,
                    "fatigue_reached_on": perf.fatigue_reached_on,
                }

                if metric_type in ["all", "detailed"]:
                    perf_data.update(
                        {
                            "early_month_performance": perf.early_month_performance,
                            "mid_month_performance": perf.mid_month_performance,
                            "late_month_performance": perf.late_month_performance,
                        }
                    )

                results.append(perf_data)

            # Calculate summary statistics
            if results:
                avg_hit_rate = sum(r["hit_rate"] for r in results) / len(results)
                total_successful_days = sum(r["total_hit_days"] for r in results)
                total_prediction_days = sum(r["total_days"] for r in results)
                overall_hit_rate = (
                    total_successful_days / total_prediction_days
                    if total_prediction_days > 0
                    else 0
                )
            else:
                avg_hit_rate = 0
                overall_hit_rate = 0
                total_successful_days = 0
                total_prediction_days = 0

            response_data = {
                "performance_data": results,
                "summary": {
                    "period": f"{start_date} to {end_date}",
                    "total_models": len(set(r["model_name"] for r in results)),
                    "avg_hit_rate": round(avg_hit_rate, 4),
                    "overall_hit_rate": round(overall_hit_rate, 4),
                    "total_successful_days": total_successful_days,
                    "total_prediction_days": total_prediction_days,
                },
                "metadata": {
                    "generated_at": timezone.now().isoformat(),
                    "query_parameters": {
                        "model_name": model_name,
                        "days": days,
                        "metric_type": metric_type,
                    },
                },
            }

            return Response(response_data, status=status.HTTP_200_OK)

        except Exception as e:
            logger.error(f"Error retrieving performance metrics: {e}", exc_info=True)
            return Response(
                {"error": "Internal server error", "details": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class RetrainModelView(APIView):
    """
    API endpoint for triggering model retraining
    """

    def post(self, request):
        """
        Trigger model retraining

        Request body:
        {
            "model_type": "ensemble",     # Type of model to retrain
            "force_retrain": false,       # Force retrain even if not needed
            "training_days": 365          # Days of training data to use
        }
        """
        try:
            model_type = request.data.get("model_type", "ensemble")
            force_retrain = request.data.get("force_retrain", False)
            training_days = request.data.get("training_days", 365)

            # Check if retraining is needed
            if not force_retrain and not self._should_retrain(model_type):
                return Response(
                    {
                        "message": "Model retraining not needed at this time",
                        "model_type": model_type,
                        "last_performance_check": timezone.now().isoformat(),
                    },
                    status=status.HTTP_200_OK,
                )

            # Start retraining process
            retrain_result = self._retrain_model(model_type, training_days)

            return Response(retrain_result, status=status.HTTP_200_OK)

        except Exception as e:
            logger.error(f"Error during model retraining: {e}", exc_info=True)
            return Response(
                {"error": "Retraining failed", "details": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    def _should_retrain(self, model_type: str) -> bool:
        """Determine if model should be retrained based on performance"""
        # Get recent performance
        end_date = timezone.now().date()
        start_date = end_date - timedelta(days=14)  # Last 2 weeks

        recent_performance = (
            MethodCyclicalPerformance.objects.filter(
                method_name__icontains=model_type,
                year__gte=start_date.year,
                month__gte=start_date.month,
            )
            .order_by("-year", "-month")
            .first()
        )

        if not recent_performance:
            return True  # No recent performance data, should retrain

        # Check performance thresholds
        if recent_performance.hit_rate < 0.3:  # Less than 30% hit rate
            logger.info(
                f"Model {model_type} performance below threshold: {recent_performance.hit_rate}"
            )
            return True

        if recent_performance.fatigue_threshold_reached:
            logger.info(f"Model {model_type} has reached fatigue threshold")
            return True

        # Check data freshness (if last training was more than 30 days ago)
        if recent_performance.fatigue_reached_on:
            days_since_fatigue = (end_date - recent_performance.fatigue_reached_on).days
            if days_since_fatigue > 30:
                return True

        return False

    def _retrain_model(self, model_type: str, training_days: int) -> Dict:
        """Perform model retraining"""
        retrain_start_time = timezone.now()

        logger.info(
            f"Starting retraining for {model_type} with {training_days} days of data"
        )

        # Prepare training dates
        end_date = timezone.now().date()
        start_date = end_date - timedelta(days=training_days)

        # Create and train new model
        if model_type == "ensemble":
            model = ModelFactory.create_dynamic_ensemble()
        elif model_type == "gradient_boosting":
            from lottery_prediction.ml.models.gradient_boosting import (
                LotteryGradientBoostingModel,
            )

            model = LotteryGradientBoostingModel(model_type="gradient_boosting")
        elif model_type == "hist_gradient_boosting":
            from lottery_prediction.ml.models.gradient_boosting import (
                LotteryGradientBoostingModel,
            )

            model = LotteryGradientBoostingModel(model_type="hist_gradient_boosting")
        else:
            raise ValueError(f"Unknown model type: {model_type}")

        # Train model
        model.fit(start_date=start_date, end_date=end_date)

        # Save retrained model
        model_dir = os.path.join(settings.BASE_DIR, "models")
        os.makedirs(model_dir, exist_ok=True)
        model_path = os.path.join(model_dir, f"{model_type}_model.pkl")

        if hasattr(model, "save_model"):
            model.save_model(model_path)
        else:
            joblib.dump(model, model_path)

        # Calculate retraining time
        retrain_time = (timezone.now() - retrain_start_time).total_seconds()

        # Prepare response
        result = {
            "message": "Model retrained successfully",
            "model_type": model_type,
            "training_period": f"{start_date} to {end_date}",
            "training_data_size": getattr(model, "training_data_size", 0),
            "retraining_time_seconds": retrain_time,
            "model_saved_to": model_path,
            "retrained_at": timezone.now().isoformat(),
        }

        logger.info(f"Model {model_type} retrained successfully in {retrain_time:.2f}s")

        return result


class ActualResultsView(APIView):
    """
    API endpoint for retrieving actual lottery results for comparison
    """

    def get(self, request):
        """Get actual lottery results for a specific date"""
        try:
            date_str = request.query_params.get("date")
            if not date_str:
                return Response(
                    {"error": "Date parameter is required"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            try:
                target_date = datetime.strptime(date_str, "%Y-%m-%d").date()
            except ValueError:
                return Response(
                    {"error": "Invalid date format. Use YYYY-MM-DD"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            # Get actual results from database
            try:
                result = KetQuaXoSo.objects.get(ngay=target_date)

                # Extract all winning numbers from different prize categories
                winning_numbers = []

                # Special prize
                if result.giai_db:
                    winning_numbers.extend(
                        self._extract_numbers_from_prize(result.giai_db)
                    )

                # First prize
                if result.giai_1:
                    winning_numbers.extend(
                        self._extract_numbers_from_prize(result.giai_1)
                    )

                # Other prizes - extract last 2 digits
                for field in [
                    "giai_2",
                    "giai_3",
                    "giai_4",
                    "giai_5",
                    "giai_6",
                    "giai_7",
                ]:
                    prize_value = getattr(result, field, "")
                    if prize_value:
                        winning_numbers.extend(
                            self._extract_numbers_from_prize(prize_value, last_digits=2)
                        )

                # Remove duplicates and sort
                unique_numbers = sorted(list(set(winning_numbers)))

                return Response(
                    {
                        "date": target_date.isoformat(),
                        "results": {
                            "date": target_date.isoformat(),
                            "winning_numbers": unique_numbers,
                            "special_prize": result.giai_db,
                            "first_prize": result.giai_1,
                            "total_unique_numbers": len(unique_numbers),
                        },
                    },
                    status=status.HTTP_200_OK,
                )

            except KetQuaXoSo.DoesNotExist:
                return Response(
                    {"error": f"No results found for date {target_date}"},
                    status=status.HTTP_404_NOT_FOUND,
                )

        except Exception as e:
            logger.error(f"Error fetching actual results: {e}")
            return Response(
                {"error": "Internal server error", "details": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    def _extract_numbers_from_prize(
        self, prize_str: str, last_digits: Optional[int] = None
    ) -> List[str]:
        """Extract numbers from prize string"""
        numbers = []
        if not prize_str:
            return numbers

        # Split by comma and clean up
        parts = [part.strip() for part in prize_str.split(",")]

        for part in parts:
            if part:
                if last_digits:
                    # Extract last N digits
                    if len(part) >= last_digits:
                        numbers.append(part[-last_digits:].zfill(2))
                else:
                    # Extract last 2 digits for lottery number prediction
                    if len(part) >= 2:
                        numbers.append(part[-2:].zfill(2))

        return numbers
