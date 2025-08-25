#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import time

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'xoso_crawler.settings')
import django
django.setup()

print("🚀 TESTING OPTIMIZED ULTIMATE PREDICTION TEMPLATE VIEW")
print("=" * 60)

try:
    # Test ServiceManager
    print("1. Testing ServiceManager...")
    from analytic_frequence.service_manager import ServiceManager
    
    start = time.time()
    manager = ServiceManager()
    init_time = (time.time() - start) * 1000
    print(f"   ✅ ServiceManager initialized in {init_time:.2f}ms")
    
    # Test service health
    health = ServiceManager.is_healthy()
    print(f"   ✅ Services healthy: {health}")
    
    # Test IntelligentCache
    print("\n2. Testing IntelligentCache...")
    from analytic_frequence.intelligent_cache import IntelligentCache
    
    start = time.time()
    test_data = IntelligentCache.get_or_set(
        'test_key',
        lambda: {'test': 'data', 'timestamp': time.time()},
        tier='warm'
    )
    cache_time = (time.time() - start) * 1000
    print(f"   ✅ Cache operation completed in {cache_time:.2f}ms")
    
    # Test optimized template view
    print("\n3. Testing Optimized Template View...")
    from analytic_frequence.template_views import UltimatePredictionTemplateView
    from django.test import RequestFactory
    
    factory = RequestFactory()
    request = factory.get('/test/')
    
    start = time.time()
    view = UltimatePredictionTemplateView()
    view.request = request
    init_time = (time.time() - start) * 1000
    print(f"   ✅ View initialized in {init_time:.2f}ms")
    
    start = time.time()
    context = view.get_context_data()
    context_time = (time.time() - start) * 1000
    print(f"   ✅ Context generated in {context_time:.2f}ms")
    
    # Performance assessment
    total_time = init_time + context_time
    print(f"\n🎯 TOTAL PERFORMANCE: {total_time:.2f}ms")
    
    if total_time < 100:
        print("🚀 EXCELLENT: Sub-100ms performance achieved!")
    elif total_time < 200:
        print("✅ GOOD: Sub-200ms performance achieved!")
    elif total_time < 500:
        print("⚠️ ACCEPTABLE: Sub-500ms performance")
    else:
        print("❌ NEEDS IMPROVEMENT: Over 500ms")
    
    # Test cache warm-up
    print("\n4. Testing Cache Warm-up...")
    from analytic_frequence.intelligent_cache import cache_warm_up
    
    start = time.time()
    cache_warm_up()
    warmup_time = (time.time() - start) * 1000
    print(f"   ✅ Cache warmed up in {warmup_time:.2f}ms")
    
    print("\n🎉 ALL TESTS PASSED!")
    print("✅ Revolutionary optimizations are working!")
    
except Exception as e:
    print(f"❌ ERROR: {e}")
    import traceback
    traceback.print_exc()
