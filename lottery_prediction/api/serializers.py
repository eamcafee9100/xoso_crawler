# api/serializers.py

from datetime import date, datetime, timedelta
from typing import Dict, List

from rest_framework import serializers


class PredictionRequestSerializer(serializers.Serializer):
    """Serializer for prediction request data"""

    prediction_date = serializers.DateField(
        required=False,
        help_text="Date to predict lottery numbers for (YYYY-MM-DD format). Defaults to tomorrow.",
    )

    model_type = serializers.ChoiceField(
        choices=[
            "ensemble",
            "dynamic_ensemble",
            "gradient_boosting",
            "hist_gradient_boosting",
            "frequency_based",
            "day_of_week",
            "cyclical",
        ],
        default="ensemble",
        required=False,
        help_text="Type of model to use for prediction",
    )

    top_k = serializers.IntegerField(
        min_value=1,
        max_value=50,
        default=10,
        required=False,
        help_text="Number of top predictions to return (1-50)",
    )

    prediction_context = serializers.ChoiceField(
        choices=["prediction", "evaluation", "backtesting", "validation"],
        default="prediction",
        required=False,
        help_text="Context for prediction - 'evaluation' allows historical dates for testing",
    )

    def validate_prediction_date(self, value):
        """Validate prediction date based on context"""
        from django.utils import timezone
        from lottery_prediction.ml.features.extractors import DataLeakageValidator
        
        current_date = timezone.now().date()
        
        # Get context from the request data
        context = self.initial_data.get('prediction_context', 'prediction')
        
        # Context-aware validation
        if context == 'prediction':
            # For real predictions, only allow future dates
            if value <= current_date:
                raise serializers.ValidationError(
                    "Prediction date must be in the future for real predictions"
                )
        elif context in ['evaluation', 'backtesting', 'validation']:
            # For historical testing, allow past dates but validate data availability
            try:
                DataLeakageValidator.validate_prediction_request(value, context)
            except ValueError as e:
                raise serializers.ValidationError(str(e))
        
        return value

    def validate(self, data):
        """Cross-field validation"""
        prediction_date = data.get('prediction_date')
        context = data.get('prediction_context', 'prediction')
        
        # Additional validation logic if needed
        if context == 'prediction' and prediction_date:
            from django.utils import timezone
            if prediction_date <= timezone.now().date():
                raise serializers.ValidationError({
                    'prediction_date': 'Future date required for real predictions'
                })
        
        return data

class NumberPredictionSerializer(serializers.Serializer):
    """Serializer for individual number prediction"""

    number = serializers.CharField(
        max_length=2, help_text="Two-digit lottery number (00-99)"
    )

    probability = serializers.FloatField(
        min_value=0.0, max_value=1.0, help_text="Probability of this number appearing"
    )

    rank = serializers.IntegerField(
        min_value=1, help_text="Rank of this prediction (1 = highest probability)"
    )


class ModelInfoSerializer(serializers.Serializer):
    """Serializer for model information"""

    model_name = serializers.CharField(help_text="Name of the model")
    model_type = serializers.CharField(help_text="Type of the model")
    confidence_score = serializers.FloatField(help_text="Overall confidence score")
    total_probability_mass = serializers.FloatField(
        help_text="Sum of top-K probabilities"
    )
    entropy = serializers.FloatField(
        help_text="Entropy of the probability distribution"
    )
    last_train_date = serializers.DateTimeField(
        help_text="When the model was last trained"
    )
    training_data_size = serializers.IntegerField(help_text="Size of training dataset")

    # Optional fields for ensemble models
    current_weights = serializers.DictField(
        required=False, help_text="Current weights for ensemble models"
    )
    weight_trends = serializers.DictField(
        required=False, help_text="Weight trends for dynamic ensemble models"
    )


class DataQualitySerializer(serializers.Serializer):
    """Serializer for data quality information"""

    score = serializers.FloatField(
        min_value=0.0, max_value=1.0, help_text="Overall data quality score (0-1)"
    )

    reference_data_points = serializers.IntegerField(
        help_text="Number of historical data points available"
    )

    data_freshness_days = serializers.IntegerField(
        help_text="Days between prediction date and most recent data"
    )


class MetadataSerializer(serializers.Serializer):
    """Serializer for response metadata"""

    prediction_generated_at = serializers.DateTimeField(
        help_text="Timestamp when prediction was generated"
    )

    processing_time_seconds = serializers.FloatField(
        help_text="Time taken to generate prediction"
    )

    api_version = serializers.CharField(help_text="API version used")


class PredictionResponseSerializer(serializers.Serializer):
    """Serializer for prediction response data"""

    prediction_date = serializers.DateField(help_text="Date the prediction is for")

    reference_date = serializers.DateField(
        help_text="Most recent date with available data"
    )

    top_k_predictions = NumberPredictionSerializer(
        many=True, help_text="List of top-K number predictions"
    )

    model_info = ModelInfoSerializer(help_text="Information about the model used")

    data_quality = DataQualitySerializer(help_text="Information about data quality")

    metadata = MetadataSerializer(help_text="Response metadata")


class PerformanceDataSerializer(serializers.Serializer):
    """Serializer for model performance data"""

    model_name = serializers.CharField(help_text="Name of the model")
    year = serializers.IntegerField(help_text="Year of performance data")
    month = serializers.IntegerField(help_text="Month of performance data")
    hit_rate = serializers.FloatField(
        help_text="Hit rate (successful predictions / total predictions)"
    )
    total_hit_days = serializers.IntegerField(
        help_text="Number of days with successful predictions"
    )
    total_days = serializers.IntegerField(help_text="Total number of prediction days")
    fatigue_threshold_reached = serializers.BooleanField(
        help_text="Whether fatigue threshold was reached"
    )
    fatigue_reached_on = serializers.DateField(
        allow_null=True, help_text="Date when fatigue threshold was reached"
    )

    # Optional detailed performance data
    early_month_performance = serializers.DictField(
        required=False, help_text="Performance in early month (days 1-10)"
    )
    mid_month_performance = serializers.DictField(
        required=False, help_text="Performance in mid month (days 11-20)"
    )
    late_month_performance = serializers.DictField(
        required=False, help_text="Performance in late month (days 21-31)"
    )


class PerformanceSummarySerializer(serializers.Serializer):
    """Serializer for performance summary data"""

    period = serializers.CharField(help_text="Time period for the summary")
    total_models = serializers.IntegerField(help_text="Number of models in summary")
    avg_hit_rate = serializers.FloatField(
        help_text="Average hit rate across all models"
    )
    overall_hit_rate = serializers.FloatField(
        help_text="Overall hit rate for the period"
    )
    total_successful_days = serializers.IntegerField(
        help_text="Total successful prediction days"
    )
    total_prediction_days = serializers.IntegerField(help_text="Total prediction days")


class ModelPerformanceResponseSerializer(serializers.Serializer):
    """Serializer for model performance response"""

    performance_data = PerformanceDataSerializer(
        many=True, help_text="Performance data for each model/period"
    )

    summary = PerformanceSummarySerializer(help_text="Summary statistics")

    metadata = serializers.DictField(help_text="Response metadata")


class RetrainRequestSerializer(serializers.Serializer):
    """Serializer for model retraining request"""

    model_type = serializers.ChoiceField(
        choices=[
            "ensemble",
            "dynamic_ensemble",
            "gradient_boosting",
            "hist_gradient_boosting",
        ],
        default="ensemble",
        help_text="Type of model to retrain",
    )

    force_retrain = serializers.BooleanField(
        default=False,
        help_text="Force retraining even if not needed based on performance",
    )

    training_days = serializers.IntegerField(
        min_value=30,
        max_value=1095,  # 3 years
        default=365,
        help_text="Number of days of historical data to use for training",
    )

    def validate_training_days(self, value):
        """Validate training days"""
        # Check if we have enough historical data
        from datetime import date, timedelta

        from results.models import KetQuaXoSo

        end_date = date.today()
        start_date = end_date - timedelta(days=value)

        available_data = KetQuaXoSo.objects.filter(
            ngay__gte=start_date, ngay__lte=end_date
        ).count()

        if available_data < 30:
            raise serializers.ValidationError(
                f"Insufficient training data. Requested {value} days, but only {available_data} records available."
            )

        if (
            available_data < value * 0.7
        ):  # At least 70% of requested days should have data
            raise serializers.ValidationError(
                f"Sparse training data. Only {available_data} records available for {value} requested days."
            )

        return value


class RetrainResponseSerializer(serializers.Serializer):
    """Serializer for model retraining response"""

    message = serializers.CharField(help_text="Status message")
    model_type = serializers.CharField(help_text="Type of model that was retrained")
    training_period = serializers.CharField(help_text="Date range used for training")
    training_data_size = serializers.IntegerField(
        help_text="Number of training samples"
    )
    retraining_time_seconds = serializers.FloatField(
        help_text="Time taken for retraining"
    )
    model_saved_to = serializers.CharField(help_text="Path where model was saved")
    retrained_at = serializers.DateTimeField(
        help_text="Timestamp of retraining completion"
    )


class ValidationErrorSerializer(serializers.Serializer):
    """Serializer for validation error responses"""

    error = serializers.CharField(help_text="Error type")
    details = serializers.DictField(help_text="Detailed error information")


class InternalErrorSerializer(serializers.Serializer):
    """Serializer for internal error responses"""

    error = serializers.CharField(help_text="Error type")
    details = serializers.CharField(help_text="Error details")


# Custom field for better number validation
class LotteryNumberField(serializers.CharField):
    """Custom field for lottery number validation"""

    def __init__(self, **kwargs):
        kwargs["max_length"] = 2
        kwargs["min_length"] = 2
        super().__init__(**kwargs)

    def to_internal_value(self, data):
        value = super().to_internal_value(data)

        # Validate format
        if not value.isdigit():
            raise serializers.ValidationError("Number must contain only digits")

        # Validate range
        num = int(value)
        if num < 0 or num > 99:
            raise serializers.ValidationError("Number must be between 00 and 99")

        # Ensure two-digit format
        return f"{num:02d}"
