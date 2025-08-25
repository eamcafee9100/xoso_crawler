#!/usr/bin/env python3
"""
🔍 COMPREHENSIVE PHASE 1 REVIEW & TESTING SUITE
Deep analysis and validation of all Phase 1 improvements
"""

import json
import os
import statistics
import sys
import time
from datetime import datetime, timedelta

import django

# Add the project root to Python path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

# Setup Django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "xoso_crawler.settings")
django.setup()

from django.http import HttpRequest

from predictions_tracker.advanced_fusion_system import AdvancedNumberFusion
from predictions_tracker.deep_frequency_analyzer import DeepFrequencyAnalyzer
from predictions_tracker.views_dir.api_cyclical_prediction_by_date_v3 import (
    api_cyclical_prediction_by_date_v3,
)


class Phase1ReviewSuite:
    """Comprehensive testing and review of Phase 1 improvements"""

    def __init__(self):
        self.results = {
            "extended_lookback": {},
            "deep_frequency": {},
            "advanced_fusion": {},
            "method_intelligence": {},
            "performance_benchmarks": {},
            "stability_tests": {},
            "warnings_analysis": {},
        }

    def run_comprehensive_review(self):
        """Run all review tests"""
        print("🔍 COMPREHENSIVE PHASE 1 REVIEW & TESTING")
        print("=" * 60)

        # 1. Extended Lookback Analysis
        print("\n📊 1. EXTENDED LOOKBACK ANALYSIS")
        self._test_extended_lookback()

        # 2. Deep Frequency Analysis Review
        print("\n🌊 2. DEEP FREQUENCY ANALYSIS REVIEW")
        self._test_deep_frequency()

        # 3. Advanced Fusion System Review
        print("\n⚙️ 3. ADVANCED FUSION SYSTEM REVIEW")
        self._test_advanced_fusion()

        # 4. Method Intelligence Review
        print("\n🧠 4. METHOD INTELLIGENCE REVIEW")
        self._test_method_intelligence()

        # 5. Performance Benchmarks
        print("\n📈 5. PERFORMANCE BENCHMARKS")
        self._benchmark_performance()

        # 6. Stability Tests
        print("\n🔧 6. STABILITY TESTS")
        self._test_stability()

        # 7. Warning Analysis
        print("\n⚠️ 7. WARNING ANALYSIS")
        self._analyze_warnings()

        # 8. Final Assessment
        print("\n🎯 8. FINAL ASSESSMENT")
        self._generate_final_assessment()

    def _test_extended_lookback(self):
        """Test extended lookback functionality"""
        try:
            # Test different date ranges
            test_dates = [
                datetime.now() - timedelta(days=1),
                datetime.now() - timedelta(days=7),
                datetime.now() - timedelta(days=30),
                datetime.now() - timedelta(days=90),
            ]

            feature_counts = []

            for test_date in test_dates:
                request = HttpRequest()
                request.method = "GET"
                request.GET = {"analysis_date": test_date.strftime("%Y-%m-%d")}

                start_time = time.time()
                response = api_cyclical_prediction_by_date_v3(request)
                execution_time = time.time() - start_time

                if response.status_code == 200:
                    data = json.loads(response.content.decode("utf-8"))
                    debug_info = data.get("debug_info", {})
                    feature_count = debug_info.get("total_features", 0)
                    feature_counts.append(feature_count)

                    print(
                        f"   📅 {test_date.strftime('%Y-%m-%d')}: {feature_count} features, {execution_time:.2f}s"
                    )
                else:
                    print(
                        f"   ❌ {test_date.strftime('%Y-%m-%d')}: API error {response.status_code}"
                    )

            if feature_counts:
                avg_features = statistics.mean(feature_counts)
                print(f"   📊 Average features: {avg_features:.0f}")
                print(
                    f"   🎯 Feature consistency: {'High' if len(set(feature_counts)) <= 2 else 'Variable'}"
                )

                self.results["extended_lookback"] = {
                    "average_features": avg_features,
                    "feature_range": f"{min(feature_counts)}-{max(feature_counts)}",
                    "consistency": len(set(feature_counts)) <= 2,
                }

        except Exception as e:
            print(f"   ❌ Extended lookback test failed: {str(e)}")

    def _test_deep_frequency(self):
        """Test deep frequency analysis"""
        try:
            analyzer = DeepFrequencyAnalyzer()

            # Generate test data
            import random

            random.seed(42)
            test_data = []
            for _ in range(365):  # 1 year of data
                daily_numbers = [random.randint(0, 99) for _ in range(3)]
                test_data.append(daily_numbers)

            # Test all analysis methods
            patterns = analyzer.analyze_comprehensive_patterns(test_data)

            pattern_types = list(patterns.keys())
            pattern_counts = {
                k: len(v) if isinstance(v, dict) else 0 for k, v in patterns.items()
            }

            print(f"   🔍 Pattern types detected: {len(pattern_types)}")
            for pattern_type, count in pattern_counts.items():
                print(f"      - {pattern_type}: {count} items")

            # Test specific components
            hot_numbers = patterns.get("hot_numbers", {})
            cold_numbers = patterns.get("cold_numbers", {})
            cyclical = patterns.get("cyclical_patterns", {})

            print(f"   🔥 Hot numbers: {len(hot_numbers)}")
            print(f"   ❄️ Cold numbers: {len(cold_numbers)}")
            print(f"   🔄 Cyclical patterns: {len(cyclical)}")

            self.results["deep_frequency"] = {
                "pattern_types": len(pattern_types),
                "total_patterns": sum(pattern_counts.values()),
                "hot_numbers": len(hot_numbers),
                "cold_numbers": len(cold_numbers),
                "cyclical_patterns": len(cyclical),
            }

        except Exception as e:
            print(f"   ❌ Deep frequency test failed: {str(e)}")

    def _test_advanced_fusion(self):
        """Test advanced fusion system"""
        try:
            fusion_system = AdvancedNumberFusion()

            # Test data
            method_numbers = ["01", "15", "23", "45", "67"]
            cyclical_numbers = ["12", "23", "34", "56", "78"]

            # Test fusion
            result = fusion_system.fuse_predictions_advanced(
                method_numbers, cyclical_numbers
            )

            fused_numbers = result.get("fused_numbers", [])
            uncertainty = result.get("uncertainty_metrics", {})
            confidence_intervals = result.get("confidence_intervals", {})

            print(f"   🎲 Numbers fused: {len(fused_numbers)}")
            print(
                f"   📊 Uncertainty level: {uncertainty.get('overall_uncertainty', 'N/A')}"
            )
            print(f"   🎯 Confidence intervals: {len(confidence_intervals)}")
            print(f"   📈 Fusion method: {result.get('fusion_method', 'N/A')}")

            # Test different fusion scenarios
            scenarios = [
                (["01", "02", "03"], ["04", "05", "06"]),  # No overlap
                (["01", "02", "03"], ["02", "03", "04"]),  # Partial overlap
                (["01", "02", "03"], ["01", "02", "03"]),  # Full overlap
            ]

            fusion_results = []
            for i, (m_nums, c_nums) in enumerate(scenarios):
                scenario_result = fusion_system.fuse_predictions_advanced(
                    m_nums, c_nums
                )
                fusion_results.append(len(scenario_result.get("fused_numbers", [])))
                print(f"   📊 Scenario {i+1}: {fusion_results[-1]} fused numbers")

            self.results["advanced_fusion"] = {
                "base_fusion_count": len(fused_numbers),
                "uncertainty_available": bool(uncertainty),
                "confidence_intervals_available": bool(confidence_intervals),
                "scenario_results": fusion_results,
            }

        except Exception as e:
            print(f"   ❌ Advanced fusion test failed: {str(e)}")

    def _test_method_intelligence(self):
        """Test method intelligence enhancements"""
        try:
            # Test with different dates to see method adaptation
            test_dates = [
                datetime.now() - timedelta(days=1),
                datetime.now() - timedelta(days=30),
                datetime.now() - timedelta(days=90),
            ]

            intelligence_metrics = []

            for test_date in test_dates:
                request = HttpRequest()
                request.method = "GET"
                request.GET = {"analysis_date": test_date.strftime("%Y-%m-%d")}

                response = api_cyclical_prediction_by_date_v3(request)

                if response.status_code == 200:
                    data = json.loads(response.content.decode("utf-8"))

                    performance = data.get("performance_prediction", {})
                    analysis = data.get("analysis", {})
                    debug_info = data.get("debug_info", {})

                    metrics = {
                        "expected_accuracy": performance.get("expected_accuracy", 0),
                        "confidence_level": performance.get(
                            "confidence_level", "Unknown"
                        ),
                        "volatility_score": performance.get("volatility_score", 0),
                        "pattern_strength": performance.get("pattern_strength", 0),
                        "ml_enhancement": debug_info.get(
                            "ml_enhancement_active", False
                        ),
                        "methods_analyzed": debug_info.get("methods_analyzed", 0),
                    }

                    intelligence_metrics.append(metrics)
                    print(f"   📅 {test_date.strftime('%Y-%m-%d')}:")
                    print(f"      🎯 Accuracy: {metrics['expected_accuracy']}%")
                    print(f"      📊 Confidence: {metrics['confidence_level']}")
                    print(f"      ⚡ ML Active: {metrics['ml_enhancement']}")

            if intelligence_metrics:
                avg_accuracy = statistics.mean(
                    [
                        m["expected_accuracy"]
                        for m in intelligence_metrics
                        if m["expected_accuracy"]
                    ]
                )
                print(f"   📊 Average expected accuracy: {avg_accuracy:.1f}%")

                self.results["method_intelligence"] = {
                    "average_accuracy": avg_accuracy,
                    "metrics_collected": len(intelligence_metrics),
                    "ml_enhancement_active": any(
                        m["ml_enhancement"] for m in intelligence_metrics
                    ),
                }

        except Exception as e:
            print(f"   ❌ Method intelligence test failed: {str(e)}")

    def _benchmark_performance(self):
        """Benchmark overall system performance"""
        try:
            test_date = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")

            # Multiple runs for performance consistency
            execution_times = []
            response_sizes = []

            for i in range(5):
                request = HttpRequest()
                request.method = "GET"
                request.GET = {"analysis_date": test_date}

                start_time = time.time()
                response = api_cyclical_prediction_by_date_v3(request)
                execution_time = time.time() - start_time

                execution_times.append(execution_time)
                response_sizes.append(len(response.content))

                print(
                    f"   🏃 Run {i+1}: {execution_time:.2f}s, {len(response.content)} bytes"
                )

            avg_time = statistics.mean(execution_times)
            avg_size = statistics.mean(response_sizes)

            print(f"   📊 Average execution time: {avg_time:.2f}s")
            print(f"   📊 Average response size: {avg_size:.0f} bytes")
            print(
                f"   🎯 Performance consistency: {statistics.stdev(execution_times):.2f}s std dev"
            )

            self.results["performance_benchmarks"] = {
                "average_execution_time": avg_time,
                "execution_time_std": statistics.stdev(execution_times),
                "average_response_size": avg_size,
                "performance_consistent": statistics.stdev(execution_times) < 1.0,
            }

        except Exception as e:
            print(f"   ❌ Performance benchmark failed: {str(e)}")

    def _test_stability(self):
        """Test system stability with edge cases"""
        try:
            # Test various edge cases
            edge_cases = [
                {"analysis_date": "2020-01-01"},  # Very old date
                {"analysis_date": "2030-01-01"},  # Future date
                {"analysis_date": "2025-02-29"},  # Invalid date
                {"analysis_date": "invalid"},  # Invalid format
                {},  # Missing parameter
            ]

            stability_results = []

            for i, params in enumerate(edge_cases):
                request = HttpRequest()
                request.method = "GET"
                request.GET = params

                try:
                    response = api_cyclical_prediction_by_date_v3(request)
                    status = (
                        "SUCCESS"
                        if response.status_code == 200
                        else f"ERROR_{response.status_code}"
                    )
                    stability_results.append(status)
                    print(f"   🧪 Edge case {i+1}: {status}")
                except Exception as e:
                    stability_results.append("EXCEPTION")
                    print(f"   🧪 Edge case {i+1}: EXCEPTION - {str(e)[:50]}...")

            success_rate = sum(1 for r in stability_results if r == "SUCCESS") / len(
                stability_results
            )
            print(f"   📊 Edge case success rate: {success_rate:.1%}")

            self.results["stability_tests"] = {
                "edge_cases_tested": len(edge_cases),
                "success_rate": success_rate,
                "results": stability_results,
            }

        except Exception as e:
            print(f"   ❌ Stability test failed: {str(e)}")

    def _analyze_warnings(self):
        """Analyze system warnings and issues"""
        try:
            # Test to capture warnings
            request = HttpRequest()
            request.method = "GET"
            request.GET = {
                "analysis_date": (datetime.now() - timedelta(days=1)).strftime(
                    "%Y-%m-%d"
                )
            }

            import io
            import logging

            # Capture log output
            log_capture = io.StringIO()
            handler = logging.StreamHandler(log_capture)
            logging.getLogger().addHandler(handler)

            response = api_cyclical_prediction_by_date_v3(request)

            log_output = log_capture.getvalue()
            warnings = [line for line in log_output.split("\n") if "WARNING" in line]
            errors = [line for line in log_output.split("\n") if "ERROR" in line]

            print(f"   ⚠️ Warnings detected: {len(warnings)}")
            print(f"   ❌ Errors detected: {len(errors)}")

            # Categorize warnings
            warning_categories = {}
            for warning in warnings[:10]:  # Show first 10
                if "slice" in warning.lower():
                    warning_categories["slicing"] = (
                        warning_categories.get("slicing", 0) + 1
                    )
                elif "failed" in warning.lower():
                    warning_categories["analysis_failures"] = (
                        warning_categories.get("analysis_failures", 0) + 1
                    )
                elif "sessions" in warning.lower():
                    warning_categories["data_access"] = (
                        warning_categories.get("data_access", 0) + 1
                    )
                else:
                    warning_categories["other"] = warning_categories.get("other", 0) + 1

                print(f"      📝 {warning[:100]}...")

            self.results["warnings_analysis"] = {
                "total_warnings": len(warnings),
                "total_errors": len(errors),
                "warning_categories": warning_categories,
                "system_functional": response.status_code == 200,
            }

        except Exception as e:
            print(f"   ❌ Warning analysis failed: {str(e)}")

    def _generate_final_assessment(self):
        """Generate comprehensive assessment"""
        print("   📋 FINAL ASSESSMENT SUMMARY")
        print("   " + "-" * 40)

        # Calculate overall scores
        scores = {
            "Extended Lookback": self._score_extended_lookback(),
            "Deep Frequency": self._score_deep_frequency(),
            "Advanced Fusion": self._score_advanced_fusion(),
            "Method Intelligence": self._score_method_intelligence(),
            "Performance": self._score_performance(),
            "Stability": self._score_stability(),
        }

        for component, score in scores.items():
            status = (
                "✅ EXCELLENT"
                if score >= 90
                else (
                    "🟡 GOOD"
                    if score >= 70
                    else "🔶 NEEDS WORK" if score >= 50 else "❌ CRITICAL"
                )
            )
            print(f"   {status} {component}: {score:.0f}%")

        overall_score = sum(scores.values()) / len(scores)
        overall_status = (
            "✅ READY"
            if overall_score >= 80
            else "🔧 NEEDS FIXES" if overall_score >= 60 else "❌ NOT READY"
        )

        print(f"\n   🎯 OVERALL PHASE 1 SCORE: {overall_score:.1f}%")
        print(f"   🚀 STATUS: {overall_status} for Phase 2")

        # Recommendations
        print(f"\n   💡 RECOMMENDATIONS:")
        if overall_score >= 90:
            print("   🎉 Phase 1 is excellent! Ready to proceed to Phase 2.")
        elif overall_score >= 80:
            print(
                "   ✅ Phase 1 is solid. Minor optimizations recommended before Phase 2."
            )
        elif overall_score >= 60:
            print("   🔧 Phase 1 needs fixes. Address critical issues before Phase 2.")
        else:
            print(
                "   ❌ Phase 1 requires significant work. Do not proceed to Phase 2 yet."
            )

    def _score_extended_lookback(self):
        """Score extended lookback implementation"""
        data = self.results.get("extended_lookback", {})
        score = 0

        if data.get("average_features", 0) > 200:
            score += 40  # Good feature extraction
        if data.get("consistency", False):
            score += 30  # Consistent results
        if data.get("average_features", 0) > 300:
            score += 30  # Excellent feature count

        return min(score, 100)

    def _score_deep_frequency(self):
        """Score deep frequency analysis"""
        data = self.results.get("deep_frequency", {})
        score = 0

        if data.get("pattern_types", 0) >= 8:
            score += 30
        if data.get("total_patterns", 0) > 50:
            score += 25
        if data.get("hot_numbers", 0) > 0 and data.get("cold_numbers", 0) > 0:
            score += 25
        if data.get("cyclical_patterns", 0) > 0:
            score += 20

        return min(score, 100)

    def _score_advanced_fusion(self):
        """Score advanced fusion system"""
        data = self.results.get("advanced_fusion", {})
        score = 0

        if data.get("base_fusion_count", 0) > 0:
            score += 30
        if data.get("uncertainty_available", False):
            score += 25
        if data.get("confidence_intervals_available", False):
            score += 25
        if len(data.get("scenario_results", [])) == 3:
            score += 20

        return min(score, 100)

    def _score_method_intelligence(self):
        """Score method intelligence"""
        data = self.results.get("method_intelligence", {})
        score = 0

        if data.get("average_accuracy", 0) > 50:
            score += 40
        if data.get("ml_enhancement_active", False):
            score += 30
        if data.get("metrics_collected", 0) > 0:
            score += 30

        return min(score, 100)

    def _score_performance(self):
        """Score performance metrics"""
        data = self.results.get("performance_benchmarks", {})
        score = 0

        if data.get("average_execution_time", 10) < 5:
            score += 40
        if data.get("performance_consistent", False):
            score += 30
        if data.get("average_response_size", 0) > 1000:
            score += 30

        return min(score, 100)

    def _score_stability(self):
        """Score system stability"""
        data = self.results.get("stability_tests", {})
        score = 0

        success_rate = data.get("success_rate", 0)
        if success_rate > 0.6:
            score += 50
        if success_rate > 0.8:
            score += 30
        if data.get("edge_cases_tested", 0) >= 5:
            score += 20

        return min(score, 100)


if __name__ == "__main__":
    reviewer = Phase1ReviewSuite()
    reviewer.run_comprehensive_review()
