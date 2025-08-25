#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
🎯 ANALYTIC FREQUENCE ADMIN: Django Admin Configuration
Registers models for Django admin interface
"""

from django.contrib import admin
from django.urls import reverse
from django.utils.html import format_html
from django.utils.safestring import mark_safe

from .models import (
    AdvancedFrequencyAnalysis,
    MetaLearningOrchestrator,
    NeuralPatternRecognizer,
    QuantumDataProcessor,
    QuantumOptimizer,
)


@admin.register(QuantumDataProcessor)
class QuantumDataProcessorAdmin(admin.ModelAdmin):
    """Admin interface for QuantumDataProcessor"""
    
    list_display = ['processor_id', 'parallel_universe_count', 'processing_state', 'created_at']
    list_filter = ['processing_state', 'created_at', 'updated_at']
    search_fields = ['processor_id']
    readonly_fields = ['processor_id', 'created_at', 'updated_at', 'processing_duration']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('processor_id', 'parallel_universe_count', 'processing_state')
        }),
        ('Configuration', {
            'fields': ('quantum_state_config',)
        }),
        ('Results', {
            'fields': ('quantum_states_result', 'parallel_analysis_result', 'temporal_crystal_data'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at', 'processing_started_at', 'processing_completed_at', 'processing_duration'),
            'classes': ('collapse',)
        }),
    )


@admin.register(NeuralPatternRecognizer)
class NeuralPatternRecognizerAdmin(admin.ModelAdmin):
    """Admin interface for NeuralPatternRecognizer"""
    
    list_display = ['recognizer_id', 'recognition_status', 'accuracy_score', 'confidence_level', 'created_at']
    list_filter = ['recognition_status', 'created_at']
    search_fields = ['recognizer_id']
    readonly_fields = ['recognizer_id', 'created_at', 'updated_at', 'is_ready_for_analysis', 'performance_grade']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('recognizer_id', 'recognition_status', 'accuracy_score', 'confidence_level')
        }),
        ('Neural Network Configuration', {
            'fields': ('transformer_config', 'attention_heads', 'sequence_length')
        }),
        ('Pattern Recognition Results', {
            'fields': ('pattern_weights', 'attention_maps', 'correlation_graphs'),
            'classes': ('collapse',)
        }),
        ('Training Metadata', {
            'fields': ('training_epochs', 'training_data_size', 'last_training_date'),
            'classes': ('collapse',)
        }),
        ('Performance', {
            'fields': ('is_ready_for_analysis', 'performance_grade'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(QuantumOptimizer)
class QuantumOptimizerAdmin(admin.ModelAdmin):
    """Admin interface for QuantumOptimizer"""
    
    list_display = ['optimizer_id', 'optimization_state', 'optimization_score', 'quantum_advantage', 'created_at']
    list_filter = ['optimization_state', 'created_at']
    search_fields = ['optimizer_id']
    readonly_fields = ['optimizer_id', 'created_at', 'updated_at', 'has_quantum_advantage', 'optimization_efficiency']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('optimizer_id', 'optimization_state', 'optimization_score', 'quantum_advantage')
        }),
        ('Quantum Parameters', {
            'fields': ('annealing_temperature', 'superposition_states', 'entanglement_threshold')
        }),
        ('Configuration', {
            'fields': ('optimization_config',),
            'classes': ('collapse',)
        }),
        ('Results', {
            'fields': ('quantum_annealing_result', 'superposition_analysis', 'entanglement_correlations'),
            'classes': ('collapse',)
        }),
        ('Performance Metrics', {
            'fields': ('convergence_iterations', 'has_quantum_advantage', 'optimization_efficiency'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at', 'optimization_started_at', 'optimization_completed_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(MetaLearningOrchestrator)
class MetaLearningOrchestratorAdmin(admin.ModelAdmin):
    """Admin interface for MetaLearningOrchestrator"""
    
    list_display = ['orchestrator_id', 'learning_phase', 'creativity_score', 'innovation_index', 'created_at']
    list_filter = ['learning_phase', 'created_at']
    search_fields = ['orchestrator_id']
    readonly_fields = ['orchestrator_id', 'created_at', 'updated_at', 'learning_maturity', 'is_ready_for_creative_synthesis']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('orchestrator_id', 'learning_phase', 'creativity_score', 'innovation_index')
        }),
        ('Learning Configuration', {
            'fields': ('meta_learning_config',),
            'classes': ('collapse',)
        }),
        ('Performance Tracking', {
            'fields': ('method_weights', 'performance_history', 'adaptation_rules'),
            'classes': ('collapse',)
        }),
        ('Learning Results', {
            'fields': ('learned_patterns', 'method_recommendations', 'creative_insights'),
            'classes': ('collapse',)
        }),
        ('Metrics', {
            'fields': ('self_improvement_rate', 'learning_cycles_completed', 'total_training_time', 'learning_maturity', 'is_ready_for_creative_synthesis'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at', 'last_adaptation_date'),
            'classes': ('collapse',)
        }),
    )


@admin.register(AdvancedFrequencyAnalysis)
class AdvancedFrequencyAnalysisAdmin(admin.ModelAdmin):
    """Admin interface for AdvancedFrequencyAnalysis"""
    
    list_display = ['analysis_id', 'analysis_type', 'analysis_status', 'overall_confidence', 'get_date_range', 'created_at']
    list_filter = ['analysis_type', 'analysis_status', 'created_at']
    search_fields = ['analysis_id']
    readonly_fields = ['analysis_id', 'created_at', 'updated_at', 'analysis_duration', 'date_range_days', 'performance_grade', 'is_ready_for_production']
    
    def get_date_range(self, obj):
        """Display analysis date range"""
        if obj.start_date and obj.end_date:
            return f"{obj.start_date} - {obj.end_date}"
        return "Not set"
    get_date_range.short_description = 'Date Range'
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('analysis_id', 'analysis_type', 'analysis_status', 'overall_confidence')
        }),
        ('Analysis Period', {
            'fields': ('start_date', 'end_date', 'date_range_days')
        }),
        ('Components', {
            'fields': ('quantum_processor', 'neural_recognizer', 'optimizer', 'meta_orchestrator')
        }),
        ('Results', {
            'fields': ('frequency_results', 'pattern_analysis', 'trend_analysis', 'risk_assessment'),
            'classes': ('collapse',)
        }),
        ('Advanced Results', {
            'fields': ('quantum_patterns', 'neural_insights', 'meta_learning_adaptations'),
            'classes': ('collapse',)
        }),
        ('Performance Metrics', {
            'fields': ('prediction_accuracy', 'analysis_completeness', 'performance_grade', 'is_ready_for_production'),
            'classes': ('collapse',)
        }),
        ('Processing Metadata', {
            'fields': ('processing_time', 'data_points_analyzed', 'memory_usage_mb'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at', 'analysis_started_at', 'analysis_completed_at', 'analysis_duration'),
            'classes': ('collapse',)
        }),
    )
    
    def get_queryset(self, request):
        """Optimize queryset with related objects"""
        return super().get_queryset(request).select_related(
            'quantum_processor',
            'neural_recognizer', 
            'optimizer',
            'meta_orchestrator'
        )
