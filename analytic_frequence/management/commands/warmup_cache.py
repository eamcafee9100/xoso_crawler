#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
🔥 CACHE WARM-UP MANAGEMENT COMMAND
Initialize and warm up caches for optimal performance
"""

from django.core.management.base import BaseCommand
from django.core.cache import cache
import time
import logging

from analytic_frequence.service_manager import ServiceManager
from analytic_frequence.intelligent_cache import IntelligentCache, cache_warm_up

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    """
    🚀 CACHE WARM-UP COMMAND
    
    Usage:
        python manage.py warmup_cache
        python manage.py warmup_cache --force-reinit
        python manage.py warmup_cache --verbose
    """
    
    help = 'Warm up caches and initialize services for optimal performance'

    def add_arguments(self, parser):
        parser.add_argument(
            '--force-reinit',
            action='store_true',
            help='Force re-initialization of services',
        )
        parser.add_argument(
            '--clear-cache',
            action='store_true',
            help='Clear all caches before warming up',
        )

    def handle(self, *args, **options):
        """Handle cache warm-up process"""
        start_time = time.time()
        
        self.stdout.write(
            self.style.SUCCESS('🔥 Starting Ultimate Prediction System cache warm-up...')
        )
        
        try:
            # Clear cache if requested
            if options['clear_cache']:
                self.stdout.write('🧹 Clearing existing caches...')
                cache.clear()
                self.stdout.write(self.style.SUCCESS('✅ Cache cleared'))
            
            # Force re-initialization if requested
            if options['force_reinit']:
                self.stdout.write('🔄 Force re-initializing services...')
                ServiceManager.reinitialize()
                self.stdout.write(self.style.SUCCESS('✅ Services re-initialized'))
            
            # Initialize ServiceManager (singleton)
            self.stdout.write('🚀 Initializing ServiceManager...')
            service_start = time.time()
            service_manager = ServiceManager()
            service_time = (time.time() - service_start) * 1000
            
            if ServiceManager.is_healthy():
                self.stdout.write(
                    self.style.SUCCESS(f'✅ ServiceManager initialized in {service_time:.2f}ms')
                )
            else:
                self.stdout.write(
                    self.style.ERROR('❌ ServiceManager initialization failed')
                )
                return
            
            # Warm up intelligent cache
            self.stdout.write('🧠 Warming up intelligent cache...')
            cache_start = time.time()
            cache_warm_up()
            cache_time = (time.time() - cache_start) * 1000
            self.stdout.write(
                self.style.SUCCESS(f'✅ Cache warmed up in {cache_time:.2f}ms')
            )
            
            # Generate sample predictions for cache
            self.stdout.write('🎯 Pre-generating sample predictions...')
            self._warm_sample_predictions()
            
            # Generate context data for cache
            self.stdout.write('📄 Pre-generating context data...')
            self._warm_context_data()
            
            # Display final statistics
            total_time = (time.time() - start_time) * 1000
            self.stdout.write(
                self.style.SUCCESS(
                    f'\n🎉 Cache warm-up completed in {total_time:.2f}ms!'
                )
            )
            
            # Show performance statistics
            self._show_performance_stats()
            
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'❌ Cache warm-up failed: {e}')
            )
            logger.error(f"Cache warm-up failed: {e}")

    def _warm_sample_predictions(self):
        """Pre-generate sample predictions"""
        try:
            from analytic_frequence.template_views import UltimatePredictionTemplateView
            
            # Create view instance to trigger cache generation
            view = UltimatePredictionTemplateView()
            
            # Generate sample prediction (will be cached)
            sample_prediction = view._get_sample_prediction_cached()
            
            if sample_prediction:
                self.stdout.write(self.style.SUCCESS('✅ Sample prediction cached'))
            else:
                self.stdout.write(self.style.WARNING('⚠️ Sample prediction returned None'))
                
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'❌ Sample prediction warm-up failed: {e}'))

    def _warm_context_data(self):
        """Pre-generate context data"""
        try:
            from analytic_frequence.template_views import UltimatePredictionTemplateView
            
            # Create view and generate context (will be cached)
            view = UltimatePredictionTemplateView()
            context_data = view._generate_context_data()
            
            if context_data:
                self.stdout.write(self.style.SUCCESS('✅ Context data cached'))
            else:
                self.stdout.write(self.style.WARNING('⚠️ Context data generation failed'))
                
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'❌ Context data warm-up failed: {e}'))

    def _show_performance_stats(self):
        """Show current performance statistics"""
        try:
            # Service status
            service_status = ServiceManager.get_status()
            self.stdout.write('\n📊 SERVICE STATUS:')
            self.stdout.write(f'   Healthy: {service_status.get("healthy", False)}')
            self.stdout.write(f'   Initialization time: {service_status.get("initialization_time", "N/A")}s')
            
            # Cache statistics
            cache_stats = IntelligentCache.get_performance_stats()
            self.stdout.write('\n🧠 CACHE STATISTICS:')
            
            if 'cache_performance' in cache_stats:
                for cache_type, stats in cache_stats['cache_performance'].items():
                    self.stdout.write(f'   {cache_type}:')
                    self.stdout.write(f'     Hit rate: {stats.get("hit_rate", "N/A")}')
                    self.stdout.write(f'     Total requests: {stats.get("total_requests", 0)}')
            
            overall_hit_rate = cache_stats.get('overall_hit_rate', 'N/A')
            self.stdout.write(f'   Overall hit rate: {overall_hit_rate}')
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'❌ Failed to show stats: {e}'))
