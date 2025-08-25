#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
🔄 ANALYTIC FREQUENCE SERIALIZERS: API Serialization Layer
Implements consistent API response formatting following Django best practices
"""

import json
from datetime import date, datetime, timedelta
from typing import Any, Dict, List

from django.utils import timezone
from rest_framework import serializers

from .models import (
    AdvancedFrequencyAnalysis,
    MetaLearningOrchestrator,
    NeuralPatternRecognizer,
    QuantumDataProcessor,
    QuantumOptimizer,
)


class BaseAnalyticSerializer(serializers.Serializer):
    """Base serializer with common fields and validation"""

    created_at = serializers.DateTimeField(read_only=True)
    updated_at = serializers.DateTimeField(read_only=True)

    def validate_date_range(self, start_date, end_date):
        """Validate date range constraints"""
        if start_date and end_date:
            if start_date > end_date:
                raise serializers.ValidationError("Start date cannot be after end date")

            # Check if end date is not in future
            if end_date > date.today():
                raise serializers.ValidationError("End date cannot be in the future")

            # Check minimum date range
            if (end_date - start_date).days < 7:
                raise serializers.ValidationError("Date range must be at least 7 days")

        return True


class QuantumDataProcessorSerializer(BaseAnalyticSerializer):
    """Serializer for Quantum Data Processor"""

    processor_id = serializers.CharField(read_only=True)
    quantum_state_config = serializers.JSONField()
    parallel_universe_count = serializers.IntegerField(min_value=1, max_value=10)
    processing_state = serializers.CharField(read_only=True)

    # Results fields
    quantum_states_result = serializers.JSONField(read_only=True)
    parallel_analysis_result = serializers.JSONField(read_only=True)
    temporal_crystal_data = serializers.JSONField(read_only=True)

    # Metadata
    processing_duration = serializers.SerializerMethodField()
    quantum_advantage = serializers.SerializerMethodField()
    is_active = serializers.BooleanField(read_only=True)

    class Meta:
        model = QuantumDataProcessor
        fields = [
            "processor_id",
            "quantum_state_config",
            "parallel_universe_count",
            "processing_state",
            "quantum_states_result",
            "parallel_analysis_result",
            "temporal_crystal_data",
            "processing_duration",
            "quantum_advantage",
            "is_active",
            "created_at",
            "updated_at",
        ]

    def get_processing_duration(self, obj):
        """Get processing duration in seconds"""
        if obj.processing_duration:
            return obj.processing_duration.total_seconds()
        return None

    def get_quantum_advantage(self, obj):
        """Calculate quantum advantage score"""
        if obj.quantum_states_result and obj.temporal_crystal_data:
            coherence = obj.quantum_states_result.get("quantum_coherence", 0)
            crystal_coherence = obj.temporal_crystal_data.get("temporal_coherence", 0)
            return round((coherence + crystal_coherence) / 2, 3)
        return 0.0

    def validate_quantum_state_config(self, value):
        """Validate quantum state configuration"""
        required_fields = ["coherence_time", "entanglement_strength"]
        for field in required_fields:
            if field not in value:
                raise serializers.ValidationError(f"Missing required field: {field}")

        if (
            not isinstance(value.get("coherence_time"), (int, float))
            or value["coherence_time"] <= 0
        ):
            raise serializers.ValidationError("Coherence time must be positive number")

        if not (0 <= value.get("entanglement_strength", 0) <= 1):
            raise serializers.ValidationError(
                "Entanglement strength must be between 0 and 1"
            )

        return value


class NeuralPatternRecognizerSerializer(BaseAnalyticSerializer):
    """Serializer for Neural Pattern Recognizer"""

    recognizer_id = serializers.CharField(read_only=True)
    transformer_config = serializers.JSONField()
    attention_heads = serializers.IntegerField(min_value=1, max_value=16)
    sequence_length = serializers.IntegerField(min_value=10, max_value=1000)
    recognition_status = serializers.CharField(read_only=True)

    # Performance metrics
    accuracy_score = serializers.FloatField(read_only=True)
    confidence_level = serializers.FloatField(read_only=True)
    performance_grade = serializers.CharField(read_only=True)

    # Results
    pattern_weights = serializers.JSONField(read_only=True)
    attention_maps = serializers.JSONField(read_only=True)
    correlation_graphs = serializers.JSONField(read_only=True)

    # Training metadata
    training_epochs = serializers.IntegerField(read_only=True)
    training_data_size = serializers.IntegerField(read_only=True)
    last_training_date = serializers.DateTimeField(read_only=True)
    is_ready_for_analysis = serializers.BooleanField(read_only=True)

    class Meta:
        model = NeuralPatternRecognizer
        fields = [
            "recognizer_id",
            "transformer_config",
            "attention_heads",
            "sequence_length",
            "recognition_status",
            "accuracy_score",
            "confidence_level",
            "performance_grade",
            "pattern_weights",
            "attention_maps",
            "correlation_graphs",
            "training_epochs",
            "training_data_size",
            "last_training_date",
            "is_ready_for_analysis",
            "created_at",
            "updated_at",
        ]

    def validate_transformer_config(self, value):
        """Validate transformer configuration"""
        required_fields = ["model_dim", "num_heads", "num_layers"]
        for field in required_fields:
            if field not in value:
                raise serializers.ValidationError(f"Missing required field: {field}")

        if value.get("model_dim", 0) not in [256, 512, 768, 1024]:
            raise serializers.ValidationError(
                "Model dimension must be one of: 256, 512, 768, 1024"
            )

        if not (1 <= value.get("num_heads", 0) <= 16):
            raise serializers.ValidationError(
                "Number of heads must be between 1 and 16"
            )

        if not (1 <= value.get("num_layers", 0) <= 24):
            raise serializers.ValidationError(
                "Number of layers must be between 1 and 24"
            )

        return value


class QuantumOptimizerSerializer(BaseAnalyticSerializer):
    """Serializer for Quantum Optimizer"""

    optimizer_id = serializers.CharField(read_only=True)
    optimization_config = serializers.JSONField()
    annealing_temperature = serializers.FloatField(min_value=0.1, max_value=10.0)
    superposition_states = serializers.IntegerField(min_value=2, max_value=64)
    entanglement_threshold = serializers.FloatField(min_value=0.0, max_value=1.0)
    optimization_state = serializers.CharField(read_only=True)

    # Results
    quantum_annealing_result = serializers.JSONField(read_only=True)
    superposition_analysis = serializers.JSONField(read_only=True)
    entanglement_correlations = serializers.JSONField(read_only=True)

    # Performance metrics
    optimization_score = serializers.FloatField(read_only=True)
    convergence_iterations = serializers.IntegerField(read_only=True)
    quantum_advantage = serializers.FloatField(read_only=True)
    has_quantum_advantage = serializers.BooleanField(read_only=True)
    optimization_efficiency = serializers.FloatField(read_only=True)

    class Meta:
        model = QuantumOptimizer
        fields = [
            "optimizer_id",
            "optimization_config",
            "annealing_temperature",
            "superposition_states",
            "entanglement_threshold",
            "optimization_state",
            "quantum_annealing_result",
            "superposition_analysis",
            "entanglement_correlations",
            "optimization_score",
            "convergence_iterations",
            "quantum_advantage",
            "has_quantum_advantage",
            "optimization_efficiency",
            "created_at",
            "updated_at",
        ]

    def validate_optimization_config(self, value):
        """Validate optimization configuration"""
        if "annealing_schedule" not in value:
            raise serializers.ValidationError(
                "Missing required field: annealing_schedule"
            )

        valid_schedules = ["linear", "exponential", "cosine", "adaptive"]
        if value["annealing_schedule"] not in valid_schedules:
            raise serializers.ValidationError(
                f"Invalid annealing schedule. Must be one of: {valid_schedules}"
            )

        return value


class MetaLearningOrchestratorSerializer(BaseAnalyticSerializer):
    """Serializer for Meta-Learning Orchestrator"""

    orchestrator_id = serializers.CharField(read_only=True)
    learning_phase = serializers.CharField(read_only=True)
    meta_learning_config = serializers.JSONField()

    # Performance metrics
    creativity_score = serializers.FloatField(read_only=True)
    innovation_index = serializers.FloatField(read_only=True)
    self_improvement_rate = serializers.FloatField(read_only=True)
    learning_maturity = serializers.CharField(read_only=True)

    # Results
    method_weights = serializers.JSONField(read_only=True)
    learned_patterns = serializers.JSONField(read_only=True)
    creative_insights = serializers.JSONField(read_only=True)
    adaptation_rules = serializers.JSONField(read_only=True)

    # Learning metadata
    learning_cycles_completed = serializers.IntegerField(read_only=True)
    total_training_time = serializers.SerializerMethodField()
    last_adaptation_date = serializers.DateTimeField(read_only=True)
    is_ready_for_creative_synthesis = serializers.BooleanField(read_only=True)

    class Meta:
        model = MetaLearningOrchestrator
        fields = [
            "orchestrator_id",
            "learning_phase",
            "meta_learning_config",
            "creativity_score",
            "innovation_index",
            "self_improvement_rate",
            "learning_maturity",
            "method_weights",
            "learned_patterns",
            "creative_insights",
            "adaptation_rules",
            "learning_cycles_completed",
            "total_training_time",
            "last_adaptation_date",
            "is_ready_for_creative_synthesis",
            "created_at",
            "updated_at",
        ]

    def get_total_training_time(self, obj):
        """Get total training time in seconds"""
        if obj.total_training_time:
            return obj.total_training_time.total_seconds()
        return 0

    def validate_meta_learning_config(self, value):
        """Validate meta-learning configuration"""
        required_fields = ["adaptation_rate", "exploration_factor"]
        for field in required_fields:
            if field not in value:
                raise serializers.ValidationError(f"Missing required field: {field}")

        if not (0.01 <= value.get("adaptation_rate", 0) <= 1.0):
            raise serializers.ValidationError(
                "Adaptation rate must be between 0.01 and 1.0"
            )

        if not (0.0 <= value.get("exploration_factor", 0) <= 1.0):
            raise serializers.ValidationError(
                "Exploration factor must be between 0.0 and 1.0"
            )

        return value


class AdvancedFrequencyAnalysisSerializer(BaseAnalyticSerializer):
    """Serializer for Advanced Frequency Analysis"""

    analysis_id = serializers.CharField(read_only=True)
    analysis_type = serializers.ChoiceField(
        choices=AdvancedFrequencyAnalysis.AnalysisType.choices,
        default=AdvancedFrequencyAnalysis.AnalysisType.ENHANCED,
    )
    analysis_status = serializers.CharField(read_only=True)

    # Date range
    start_date = serializers.DateField()
    end_date = serializers.DateField()
    significance_level = serializers.FloatField(
        min_value=0.001, max_value=0.1, default=0.05
    )

    # Component references
    quantum_processor = QuantumDataProcessorSerializer(read_only=True)
    neural_recognizer = NeuralPatternRecognizerSerializer(read_only=True)
    quantum_optimizer = QuantumOptimizerSerializer(read_only=True)
    meta_orchestrator = MetaLearningOrchestratorSerializer(read_only=True)

    # Analysis results
    hot_numbers_analysis = serializers.JSONField(read_only=True)
    cold_numbers_analysis = serializers.JSONField(read_only=True)
    cyclical_patterns = serializers.JSONField(read_only=True)
    seasonal_effects = serializers.JSONField(read_only=True)
    correlation_matrix = serializers.JSONField(read_only=True)
    trend_analysis = serializers.JSONField(read_only=True)
    risk_assessment = serializers.JSONField(read_only=True)

    # Advanced results
    quantum_patterns = serializers.JSONField(read_only=True)
    neural_insights = serializers.JSONField(read_only=True)
    meta_learning_adaptations = serializers.JSONField(read_only=True)

    # Performance metrics
    overall_confidence = serializers.FloatField(read_only=True)
    prediction_accuracy = serializers.FloatField(read_only=True)
    analysis_completeness = serializers.FloatField(read_only=True)
    performance_grade = serializers.CharField(read_only=True)
    is_ready_for_production = serializers.BooleanField(read_only=True)

    # Processing metadata
    processing_time = serializers.SerializerMethodField()
    data_points_analyzed = serializers.IntegerField(read_only=True)
    memory_usage_mb = serializers.FloatField(read_only=True)
    date_range_days = serializers.IntegerField(read_only=True)
    analysis_duration = serializers.SerializerMethodField()

    class Meta:
        model = AdvancedFrequencyAnalysis
        fields = [
            "analysis_id",
            "analysis_type",
            "analysis_status",
            "start_date",
            "end_date",
            "significance_level",
            "quantum_processor",
            "neural_recognizer",
            "quantum_optimizer",
            "meta_orchestrator",
            "hot_numbers_analysis",
            "cold_numbers_analysis",
            "cyclical_patterns",
            "seasonal_effects",
            "correlation_matrix",
            "trend_analysis",
            "risk_assessment",
            "quantum_patterns",
            "neural_insights",
            "meta_learning_adaptations",
            "overall_confidence",
            "prediction_accuracy",
            "analysis_completeness",
            "performance_grade",
            "is_ready_for_production",
            "processing_time",
            "data_points_analyzed",
            "memory_usage_mb",
            "date_range_days",
            "analysis_duration",
            "created_at",
            "updated_at",
        ]

    def validate(self, data):
        """Validate the complete analysis data"""
        start_date = data.get("start_date")
        end_date = data.get("end_date")

        if start_date and end_date:
            self.validate_date_range(start_date, end_date)

        return data

    def get_processing_time(self, obj):
        """Get processing time in seconds"""
        if obj.processing_time:
            return obj.processing_time.total_seconds()
        return 0

    def get_analysis_duration(self, obj):
        """Get analysis duration in seconds"""
        if obj.analysis_duration:
            return obj.analysis_duration.total_seconds()
        return None


# =====================================
# 🔄 REQUEST/RESPONSE SERIALIZERS
# =====================================


class AnalysisRequestSerializer(serializers.Serializer):
    """Serializer for analysis request data"""

    analysis_type = serializers.ChoiceField(
        choices=["basic", "enhanced", "quantum", "meta_learning", "hybrid"],
        default="enhanced",
    )
    start_date = serializers.DateField()
    end_date = serializers.DateField(default=date.today)
    significance_level = serializers.FloatField(
        min_value=0.001, max_value=0.1, default=0.05
    )

    # Optional advanced parameters
    enable_quantum_processing = serializers.BooleanField(default=False)
    enable_neural_patterns = serializers.BooleanField(default=True)
    enable_meta_learning = serializers.BooleanField(default=False)
    parallel_universe_count = serializers.IntegerField(
        min_value=1, max_value=10, default=5
    )
    attention_heads = serializers.IntegerField(min_value=1, max_value=16, default=8)

    def validate(self, data):
        """Validate analysis request"""
        start_date = data.get("start_date")
        end_date = data.get("end_date", date.today())

        if start_date and end_date:
            if start_date > end_date:
                raise serializers.ValidationError("Start date cannot be after end date")

            if end_date > date.today():
                raise serializers.ValidationError("End date cannot be in the future")

            if (end_date - start_date).days < 7:
                raise serializers.ValidationError("Date range must be at least 7 days")

        return data


class AnalysisResponseSerializer(serializers.Serializer):
    """Serializer for consistent analysis response format"""

    success = serializers.BooleanField()
    data = serializers.JSONField(allow_null=True)
    error = serializers.CharField(allow_null=True)
    meta = serializers.JSONField()

    def __init__(self, *args, **kwargs):
        """Initialize with default meta information"""
        super().__init__(*args, **kwargs)
        if "initial_data" not in kwargs:
            self.initial_data = {
                "meta": {
                    "timestamp": timezone.now().isoformat(),
                    "version": "v1",
                    "analysis_engine": "advanced_frequency_analyzer",
                }
            }


class ValidationResultSerializer(serializers.Serializer):
    """Serializer for prediction validation results"""

    prediction_date = serializers.DateField()
    method_name = serializers.CharField()
    actual_results = serializers.ListField(child=serializers.CharField())

    # Validation metrics
    overall_performance = serializers.JSONField()
    category_performance = serializers.JSONField()
    roi_analysis = serializers.JSONField()

    # Additional metadata
    validation_timestamp = serializers.DateTimeField(default=timezone.now)
    validation_id = serializers.CharField(read_only=True)


class VisualizationDataSerializer(serializers.Serializer):
    """Serializer for visualization data"""

    chart_type = serializers.ChoiceField(
        choices=[
            "heatmap",
            "line_chart",
            "network",
            "dashboard",
            "radar_chart",
            "bar_chart",
        ]
    )
    title = serializers.CharField()
    data = serializers.JSONField()
    config = serializers.JSONField(default=dict)
    generated_at = serializers.DateTimeField(default=timezone.now)


class PredictionSetSerializer(serializers.Serializer):
    """Serializer for prediction sets"""

    prediction_id = serializers.CharField(read_only=True)
    prediction_type = serializers.ChoiceField(
        choices=[
            "hot_numbers",
            "cold_numbers",
            "adaptive",
            "quantum_enhanced",
            "neural_patterns",
        ]
    )
    numbers = serializers.ListField(child=serializers.CharField())
    confidence_scores = serializers.JSONField()
    method_weights = serializers.JSONField()

    generated_at = serializers.DateTimeField(default=timezone.now)
    valid_until = serializers.DateTimeField()
    prediction_metadata = serializers.JSONField(default=dict)

    def validate_numbers(self, value):
        """Validate number format"""
        for number in value:
            if not (isinstance(number, str) and len(number) == 2 and number.isdigit()):
                raise serializers.ValidationError(
                    f"Invalid number format: {number}. Must be 2-digit string."
                )

            if not (0 <= int(number) <= 99):
                raise serializers.ValidationError(
                    f"Number {number} out of range. Must be 00-99."
                )

        return value


# =====================================
# 🎯 SPECIALIZED SERIALIZERS
# =====================================


class QuantumStateSerializer(serializers.Serializer):
    """Serializer for quantum state data"""

    state_id = serializers.CharField()
    amplitude = serializers.FloatField()
    phase = serializers.FloatField()
    probability = serializers.FloatField(min_value=0.0, max_value=1.0)
    coherence_time = serializers.FloatField(min_value=0.0)
    entanglement_strength = serializers.FloatField(min_value=0.0, max_value=1.0)


class NeuralAttentionMapSerializer(serializers.Serializer):
    """Serializer for neural attention maps"""

    head_id = serializers.CharField()
    attention_weights = serializers.ListField(
        child=serializers.ListField(child=serializers.FloatField())
    )
    key_patterns = serializers.ListField(child=serializers.CharField())
    value_transformations = serializers.ListField(child=serializers.FloatField())
    attention_flow = serializers.CharField()


class MetaInsightSerializer(serializers.Serializer):
    """Serializer for meta-learning insights"""

    insight_id = serializers.CharField(read_only=True)
    insight_type = serializers.ChoiceField(
        choices=[
            "method_fusion",
            "temporal_discovery",
            "adaptive_optimization",
            "pattern_synthesis",
        ]
    )
    description = serializers.CharField()
    confidence = serializers.FloatField(min_value=0.0, max_value=1.0)
    novelty_score = serializers.FloatField(min_value=0.0, max_value=1.0)
    implementation_complexity = serializers.ChoiceField(
        choices=["low", "medium", "high"]
    )

    generated_at = serializers.DateTimeField(default=timezone.now)
    validation_status = serializers.CharField(default="pending")


class PerformanceMetricsSerializer(serializers.Serializer):
    """Serializer for performance metrics"""

    accuracy = serializers.FloatField(min_value=0.0, max_value=1.0)
    precision = serializers.FloatField(min_value=0.0, max_value=1.0)
    recall = serializers.FloatField(min_value=0.0, max_value=1.0)
    f1_score = serializers.FloatField(min_value=0.0, max_value=1.0)
    confidence = serializers.FloatField(min_value=0.0, max_value=1.0)

    # ROI metrics
    roi_percentage = serializers.FloatField()
    profit_loss = serializers.FloatField()
    hit_ratio = serializers.CharField()

    # Temporal metrics
    consistency_score = serializers.FloatField(min_value=0.0, max_value=1.0)
    trend_direction = serializers.ChoiceField(
        choices=["improving", "stable", "declining"]
    )
    volatility = serializers.FloatField(min_value=0.0)


# =====================================
# 🔧 UTILITY SERIALIZERS
# =====================================


class ErrorDetailSerializer(serializers.Serializer):
    """Serializer for detailed error information"""

    error_code = serializers.CharField()
    error_message = serializers.CharField()
    error_details = serializers.JSONField(default=dict)
    timestamp = serializers.DateTimeField(default=timezone.now)
    component = serializers.CharField()
    severity = serializers.ChoiceField(choices=["low", "medium", "high", "critical"])


class ConfigurationSerializer(serializers.Serializer):
    """Serializer for system configuration"""

    quantum_processing_enabled = serializers.BooleanField(default=True)
    neural_processing_enabled = serializers.BooleanField(default=True)
    meta_learning_enabled = serializers.BooleanField(default=True)
    visualization_enabled = serializers.BooleanField(default=True)

    cache_timeout = serializers.IntegerField(
        min_value=300, max_value=86400, default=3600
    )
    max_parallel_universes = serializers.IntegerField(
        min_value=1, max_value=20, default=10
    )
    min_confidence_threshold = serializers.FloatField(
        min_value=0.5, max_value=0.95, default=0.7
    )

    optimization_parameters = serializers.JSONField(default=dict)
    neural_architecture_config = serializers.JSONField(default=dict)
    quantum_coherence_settings = serializers.JSONField(default=dict)


class HealthCheckSerializer(serializers.Serializer):
    """Serializer for system health check"""

    system_status = serializers.ChoiceField(
        choices=["healthy", "warning", "critical", "down"]
    )
    component_status = serializers.JSONField()
    performance_metrics = serializers.JSONField()
    last_check = serializers.DateTimeField(default=timezone.now)
    uptime_seconds = serializers.IntegerField()

    # Resource usage
    memory_usage_mb = serializers.FloatField()
    cpu_usage_percent = serializers.FloatField()
    active_analyses = serializers.IntegerField()

    # Recent performance
    recent_success_rate = serializers.FloatField(min_value=0.0, max_value=1.0)
    average_response_time_ms = serializers.FloatField()
    error_rate = serializers.FloatField(min_value=0.0, max_value=1.0)
