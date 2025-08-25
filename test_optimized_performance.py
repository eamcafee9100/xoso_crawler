#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
🧪 PERFORMANCE TESTING SCRIPT
Test the optimized UltimatePredictionTemplateView performance improvements
"""

import os
import sys
import time
import statistics
from typing import List, Dict

import django

# Setup Django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "xoso_crawler.settings")
django.setup()

from analytic_frequence.template_views import UltimatePredictionTemplateView
from analytic_frequence.service_manager import ServiceManager
from analytic_frequence.intelligent_cache import IntelligentCache
from django.test import RequestFactory
from django.core.cache import cache


class PerformanceTester:
    """
    🎯 PERFORMANCE TESTING SUITE
    Compare before/after optimization performance
    """
    
    def __init__(self):
        self.factory = RequestFactory()
        self.results = {}
    
    def run_comprehensive_test(self):
        """Run comprehensive performance tests"""
        print("🧪 ULTIMATE PREDICTION TEMPLATE VIEW - PERFORMANCE TESTING")
        print("=" * 70)
        
        # Test 1: Initialization Performance
        self.test_initialization_performance()
        
        # Test 2: Context Generation Performance  
        self.test_context_generation_performance()
        
        # Test 3: Cache Performance
        self.test_cache_performance()
        
        # Test 4: Load Testing
        self.test_load_performance()
        
        # Test 5: Memory Usage
        self.test_memory_usage()
        
        # Final Report
        self.generate_performance_report()
    
    def test_initialization_performance(self):
        """Test view initialization performance"""
        print("\n🔥 TEST 1: INITIALIZATION PERFORMANCE")
        print("-" * 50)
        
        # Test optimized initialization (ServiceManager singleton)
        times = []
        for i in range(10):
            start = time.time()
            view = UltimatePredictionTemplateView()
            end = time.time()
            times.append((end - start) * 1000)
        
        avg_time = statistics.mean(times)
        min_time = min(times)
        max_time = max(times)
        
        print(f"📊 Average initialization time: {avg_time:.2f}ms")
        print(f"📊 Min/Max: {min_time:.2f}ms / {max_time:.2f}ms")
        
        # Performance assessment
        if avg_time < 10:
            print("✅ EXCELLENT: Initialization time < 10ms")
        elif avg_time < 50:
            print("✅ GOOD: Initialization time < 50ms")
        elif avg_time < 100:
            print("⚠️ ACCEPTABLE: Initialization time < 100ms")
        else:
            print("❌ POOR: Initialization time > 100ms")
        
        self.results['initialization'] = {
            'avg_time_ms': avg_time,
            'min_time_ms': min_time,
            'max_time_ms': max_time,
            'grade': 'excellent' if avg_time < 10 else 'good' if avg_time < 50 else 'acceptable' if avg_time < 100 else 'poor'
        }
    
    def test_context_generation_performance(self):
        """Test context generation performance"""
        print("\n🎯 TEST 2: CONTEXT GENERATION PERFORMANCE")
        print("-" * 50)
        
        view = UltimatePredictionTemplateView()
        request = self.factory.get('/test/')
        view.request = request
        
        # Test with cold cache
        cache.clear()
        times_cold = []
        for i in range(5):
            start = time.time()
            context = view.get_context_data()
            end = time.time()
            times_cold.append((end - start) * 1000)
        
        # Test with warm cache
        times_warm = []
        for i in range(10):
            start = time.time()
            context = view.get_context_data()
            end = time.time()
            times_warm.append((end - start) * 1000)
        
        avg_cold = statistics.mean(times_cold)
        avg_warm = statistics.mean(times_warm)
        
        print(f"📊 Cold cache average: {avg_cold:.2f}ms")
        print(f"📊 Warm cache average: {avg_warm:.2f}ms")
        print(f"📊 Cache improvement: {((avg_cold - avg_warm) / avg_cold * 100):.1f}%")
        
        # Performance assessment
        if avg_warm < 50:
            print("✅ EXCELLENT: Warm cache response < 50ms")
        elif avg_warm < 100:
            print("✅ GOOD: Warm cache response < 100ms")
        elif avg_warm < 200:
            print("⚠️ ACCEPTABLE: Warm cache response < 200ms")
        else:
            print("❌ POOR: Warm cache response > 200ms")
        
        self.results['context_generation'] = {
            'cold_cache_ms': avg_cold,
            'warm_cache_ms': avg_warm,
            'cache_improvement_percent': ((avg_cold - avg_warm) / avg_cold * 100) if avg_cold > 0 else 0,
            'grade': 'excellent' if avg_warm < 50 else 'good' if avg_warm < 100 else 'acceptable' if avg_warm < 200 else 'poor'
        }
    
    def test_cache_performance(self):
        """Test intelligent cache performance"""
        print("\n🧠 TEST 3: INTELLIGENT CACHE PERFORMANCE")
        print("-" * 50)
        
        # Clear cache for clean test
        cache.clear()
        
        # Generate cache operations
        cache_ops = 0
        cache_hits = 0
        
        view = UltimatePredictionTemplateView()
        
        # Test sample prediction caching
        for i in range(20):
            start = time.time()
            
            if i < 5:  # First 5 should be cache misses
                cache.delete(IntelligentCache.generate_key('sample_prediction'))
            
            result = view._get_sample_prediction_cached()
            end = time.time()
            
            cache_ops += 1
            # Estimate cache hit based on response time
            if (end - start) * 1000 < 100:  # Fast response likely cache hit
                cache_hits += 1
        
        cache_hit_rate = (cache_hits / cache_ops * 100) if cache_ops > 0 else 0
        
        print(f"📊 Cache operations: {cache_ops}")
        print(f"📊 Estimated cache hits: {cache_hits}")
        print(f"📊 Cache hit rate: {cache_hit_rate:.1f}%")
        
        # Get actual cache statistics
        cache_stats = IntelligentCache.get_performance_stats()
        overall_hit_rate = cache_stats.get('overall_hit_rate', '0%')
        
        print(f"📊 Overall system cache hit rate: {overall_hit_rate}")
        
        # Performance assessment
        hit_rate_num = float(overall_hit_rate.replace('%', ''))
        if hit_rate_num >= 80:
            print("✅ EXCELLENT: Cache hit rate >= 80%")
        elif hit_rate_num >= 60:
            print("✅ GOOD: Cache hit rate >= 60%")
        elif hit_rate_num >= 40:
            print("⚠️ ACCEPTABLE: Cache hit rate >= 40%")
        else:
            print("❌ POOR: Cache hit rate < 40%")
        
        self.results['cache_performance'] = {
            'hit_rate_percent': hit_rate_num,
            'total_operations': cache_ops,
            'grade': 'excellent' if hit_rate_num >= 80 else 'good' if hit_rate_num >= 60 else 'acceptable' if hit_rate_num >= 40 else 'poor'
        }
    
    def test_load_performance(self):
        """Test performance under load"""
        print("\n⚡ TEST 4: LOAD PERFORMANCE")
        print("-" * 50)
        
        view = UltimatePredictionTemplateView()
        request = self.factory.get('/test/')
        view.request = request
        
        # Simulate concurrent requests
        concurrent_times = []
        
        print("📊 Simulating 50 concurrent requests...")
        start_total = time.time()
        
        for i in range(50):
            start = time.time()
            try:
                context = view.get_context_data()
                end = time.time()
                concurrent_times.append((end - start) * 1000)
            except Exception as e:
                print(f"❌ Request {i+1} failed: {e}")
                concurrent_times.append(5000)  # 5 second penalty for failure
        
        total_time = (time.time() - start_total) * 1000
        
        avg_response = statistics.mean(concurrent_times)
        p95_response = statistics.quantiles(concurrent_times, n=20)[18]  # 95th percentile
        p99_response = statistics.quantiles(concurrent_times, n=100)[98]  # 99th percentile
        
        print(f"📊 Total time for 50 requests: {total_time:.2f}ms")
        print(f"📊 Average response time: {avg_response:.2f}ms")
        print(f"📊 95th percentile: {p95_response:.2f}ms")
        print(f"📊 99th percentile: {p99_response:.2f}ms")
        print(f"📊 Requests per second: {(50 / (total_time / 1000)):.1f}")
        
        # Performance assessment
        if avg_response < 100 and p95_response < 200:
            print("✅ EXCELLENT: Great performance under load")
        elif avg_response < 200 and p95_response < 500:
            print("✅ GOOD: Good performance under load")
        elif avg_response < 500:
            print("⚠️ ACCEPTABLE: Acceptable performance under load")
        else:
            print("❌ POOR: Poor performance under load")
        
        self.results['load_performance'] = {
            'avg_response_ms': avg_response,
            'p95_response_ms': p95_response,
            'p99_response_ms': p99_response,
            'requests_per_second': (50 / (total_time / 1000)),
            'grade': 'excellent' if avg_response < 100 and p95_response < 200 else 'good' if avg_response < 200 and p95_response < 500 else 'acceptable' if avg_response < 500 else 'poor'
        }
    
    def test_memory_usage(self):
        """Test memory usage"""
        print("\n🧠 TEST 5: MEMORY USAGE")
        print("-" * 50)
        
        try:
            import psutil
            process = psutil.Process()
            
            # Baseline memory
            baseline_memory = process.memory_info().rss / 1024 / 1024  # MB
            
            # Create multiple view instances
            views = []
            for i in range(10):
                views.append(UltimatePredictionTemplateView())
            
            # Memory after creating views
            after_creation = process.memory_info().rss / 1024 / 1024  # MB
            
            # Generate contexts
            for view in views[:5]:
                request = self.factory.get('/test/')
                view.request = request
                context = view.get_context_data()
            
            after_usage = process.memory_info().rss / 1024 / 1024  # MB
            
            memory_per_view = (after_creation - baseline_memory) / 10
            memory_per_context = (after_usage - after_creation) / 5
            
            print(f"📊 Baseline memory: {baseline_memory:.2f} MB")
            print(f"📊 Memory per view instance: {memory_per_view:.2f} MB")
            print(f"📊 Memory per context generation: {memory_per_context:.2f} MB")
            print(f"📊 Total memory usage: {after_usage:.2f} MB")
            
            # Performance assessment
            if memory_per_view < 1 and memory_per_context < 5:
                print("✅ EXCELLENT: Very efficient memory usage")
            elif memory_per_view < 5 and memory_per_context < 20:
                print("✅ GOOD: Good memory efficiency")
            elif memory_per_view < 20:
                print("⚠️ ACCEPTABLE: Acceptable memory usage")
            else:
                print("❌ POOR: High memory usage")
            
            self.results['memory_usage'] = {
                'baseline_mb': baseline_memory,
                'memory_per_view_mb': memory_per_view,
                'memory_per_context_mb': memory_per_context,
                'total_memory_mb': after_usage,
                'grade': 'excellent' if memory_per_view < 1 and memory_per_context < 5 else 'good' if memory_per_view < 5 and memory_per_context < 20 else 'acceptable' if memory_per_view < 20 else 'poor'
            }
            
        except ImportError:
            print("⚠️ psutil not available, skipping memory test")
            self.results['memory_usage'] = {'grade': 'not_tested'}
    
    def generate_performance_report(self):
        """Generate comprehensive performance report"""
        print("\n🎯 COMPREHENSIVE PERFORMANCE REPORT")
        print("=" * 70)
        
        # Calculate overall grade
        grades = [result['grade'] for result in self.results.values() if 'grade' in result and result['grade'] != 'not_tested']
        grade_scores = {
            'excellent': 4,
            'good': 3,
            'acceptable': 2,
            'poor': 1
        }
        
        if grades:
            avg_score = statistics.mean([grade_scores[grade] for grade in grades])
            if avg_score >= 3.5:
                overall_grade = 'EXCELLENT'
                status_emoji = '🚀'
            elif avg_score >= 2.5:
                overall_grade = 'GOOD'
                status_emoji = '✅'
            elif avg_score >= 1.5:
                overall_grade = 'ACCEPTABLE'
                status_emoji = '⚠️'
            else:
                overall_grade = 'POOR'
                status_emoji = '❌'
        else:
            overall_grade = 'UNKNOWN'
            status_emoji = '❓'
        
        print(f"\n{status_emoji} OVERALL PERFORMANCE GRADE: {overall_grade}")
        print("\n📊 DETAILED RESULTS:")
        
        for test_name, result in self.results.items():
            grade = result.get('grade', 'unknown')
            print(f"   {test_name.replace('_', ' ').title()}: {grade.upper()}")
        
        print(f"\n🎯 OPTIMIZATION SUCCESS METRICS:")
        
        # Key improvements
        init_time = self.results.get('initialization', {}).get('avg_time_ms', 0)
        context_time = self.results.get('context_generation', {}).get('warm_cache_ms', 0)
        cache_hit_rate = self.results.get('cache_performance', {}).get('hit_rate_percent', 0)
        
        print(f"   🔥 Initialization time: {init_time:.2f}ms (Target: <50ms)")
        print(f"   ⚡ Warm cache response: {context_time:.2f}ms (Target: <100ms)")
        print(f"   🧠 Cache hit rate: {cache_hit_rate:.1f}% (Target: >60%)")
        
        # Performance targets achievement
        targets_met = 0
        total_targets = 3
        
        if init_time < 50:
            targets_met += 1
            print("   ✅ Initialization target MET")
        else:
            print("   ❌ Initialization target MISSED")
        
        if context_time < 100:
            targets_met += 1
            print("   ✅ Response time target MET")
        else:
            print("   ❌ Response time target MISSED")
        
        if cache_hit_rate > 60:
            targets_met += 1
            print("   ✅ Cache performance target MET")
        else:
            print("   ❌ Cache performance target MISSED")
        
        success_rate = (targets_met / total_targets * 100)
        print(f"\n🎯 PERFORMANCE TARGETS ACHIEVEMENT: {targets_met}/{total_targets} ({success_rate:.1f}%)")
        
        if success_rate >= 80:
            print("🚀 REVOLUTIONARY SUCCESS: Performance optimization goals achieved!")
        elif success_rate >= 60:
            print("✅ SUCCESS: Good performance improvements achieved!")
        else:
            print("⚠️ PARTIAL SUCCESS: Some optimizations needed")


def main():
    """Run performance testing suite"""
    try:
        # Warm up the system first
        print("🔥 Warming up system...")
        ServiceManager()  # Initialize singleton
        time.sleep(1)  # Give services time to initialize
        
        # Run tests
        tester = PerformanceTester()
        tester.run_comprehensive_test()
        
        return True
        
    except Exception as e:
        print(f"❌ Performance testing failed: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
