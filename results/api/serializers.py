from rest_framework import serializers
from datetime import date

class StrategyDetailSerializer(serializers.Serializer):
    """Serializer cho chi tiết chiến lược"""
    cycle = serializers.FloatField()
    frequency = serializers.FloatField()
    gap = serializers.FloatField()
    markov = serializers.FloatField()

class RecommendationSerializer(serializers.Serializer):
    """Serializer cho gợi ý số"""
    number = serializers.CharField(max_length=10)
    score = serializers.FloatField()
    strategies = StrategyDetailSerializer()

class DailyAnalysisSerializer(serializers.Serializer):
    """Serializer cho phân tích hàng ngày"""
    date = serializers.DateField()
    recommendations = RecommendationSerializer(many=True)
    total_methods = serializers.IntegerField()
    analysis_summary = serializers.DictField()
    processing_time = serializers.FloatField()

class MethodPerformanceSerializer(serializers.Serializer):
    """Serializer cho hiệu suất phương pháp"""
    method_id = serializers.IntegerField()
    method_name = serializers.CharField()
    hit_rate = serializers.FloatField()
    total_predictions = serializers.IntegerField()
    total_hits = serializers.IntegerField()
    wilson_score = serializers.FloatField()
    cycle_strength = serializers.FloatField()

class EnsembleAnalysisSerializer(serializers.Serializer):
    """Serializer cho phân tích ensemble"""
    analysis_date = serializers.DateField()
    top_recommendations = RecommendationSerializer(many=True)
    method_performance = MethodPerformanceSerializer(many=True)
    diversity_score = serializers.FloatField()
    confidence_level = serializers.FloatField()
    strategy_weights = serializers.DictField()