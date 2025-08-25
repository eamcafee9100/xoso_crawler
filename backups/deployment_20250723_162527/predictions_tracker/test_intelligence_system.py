"""
🧪 TEST SCRIPT - Kiểm tra Ensemble Intelligence System
"""

import json
import os
import sys
from datetime import datetime, timedelta

import django

# Setup Django
sys.path.append(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
)
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "xoso_crawler.settings")
django.setup()


def test_intelligence_system():
    """Test the complete intelligence system"""
    print("🚀 Testing Ensemble Intelligence System")
    print("=" * 60)

    try:
        # Import required modules
        from predictions_tracker.core.services.data_service import DataService
        from predictions_tracker.core.services.IntelligenceIntegration import (
            DataServiceEnhancer,
        )

        # Initialize DataService
        print("1. Initializing DataService...")
        data_service = DataService()

        # Enhance with intelligence
        print("2. Enhancing with intelligence...")
        DataServiceEnhancer.add_intelligence_methods(data_service)

        # Enhance predict_next_days method
        original_predict = data_service.predict_next_days
        data_service.predict_next_days = DataServiceEnhancer.enhance_predict_next_days(
            data_service, original_predict
        )

        print("✅ DataService enhanced successfully!")

        # Test 1: Basic predictions
        print("\n3. Testing basic predictions...")
        tomorrow = datetime.now() + timedelta(days=1)
        predictions = data_service.predict_next_days(tomorrow)

        print(f"📊 Predictions for {tomorrow.strftime('%Y-%m-%d')}:")
        print(f"   Numbers: {predictions.get('predictions', [])}")
        print(f"   Strategy: {predictions.get('strategy', 'N/A')}")
        print(f"   Enhanced: {predictions.get('enhanced', False)}")
        print(f"   Anomaly Score: {predictions.get('anomaly_score', 0):.2f}")

        # Test 2: Performance analysis
        print("\n4. Testing performance analysis...")
        try:
            analysis = data_service.get_performance_analysis()
            if "error" in analysis:
                print(f"⚠️  Performance analysis error: {analysis['error']}")
            else:
                print("📈 Performance Analysis:")
                print(f"   Baseline: {analysis.get('baseline_performance', 0):.2%}")
                print(
                    f"   Methods analyzed: {len(analysis.get('method_performances', {}))}"
                )

                # Show top 3 methods
                methods = analysis.get("method_performances", {})
                if methods:
                    sorted_methods = sorted(
                        methods.items(),
                        key=lambda x: x[1].get("hit_rate", 0),
                        reverse=True,
                    )[:3]
                    print("   Top 3 Methods:")
                    for method, perf in sorted_methods:
                        print(f"     {method}: {perf.get('hit_rate', 0):.2%}")

        except Exception as e:
            print(f"❌ Performance analysis failed: {e}")

        # Test 3: Method correlations
        print("\n5. Testing method correlations...")
        try:
            correlations = data_service.get_method_correlations()
            if "error" in correlations:
                print(f"⚠️  Correlation analysis error: {correlations['error']}")
            else:
                high_corr = correlations.get("high_correlation_pairs", [])
                print(f"🔗 High correlation pairs found: {len(high_corr)}")

                if high_corr:
                    for pair in high_corr[:3]:  # Show first 3
                        print(
                            f"   {pair['method1']} ↔ {pair['method2']}: {pair['correlation']:.3f}"
                        )

        except Exception as e:
            print(f"❌ Correlation analysis failed: {e}")

        # Test 4: Baseline comparison
        print("\n6. Testing baseline comparison...")
        try:
            baseline = data_service.get_baseline_comparison()
            if "error" in baseline:
                print(f"⚠️  Baseline comparison error: {baseline['error']}")
            else:
                print(
                    f"🎯 Baseline Performance: {baseline.get('baseline_performance', 0):.2%}"
                )

                significantly_better = baseline.get("significantly_better_methods", [])
                print(f"⭐ Significantly better methods: {len(significantly_better)}")

                if significantly_better:
                    for method in significantly_better[:5]:  # Show first 5
                        comp = baseline.get("method_comparisons", {}).get(method, {})
                        print(f"   {method}: {comp.get('improvement', 0):.1f}x better")

        except Exception as e:
            print(f"❌ Baseline comparison failed: {e}")

        print("\n✅ All tests completed!")

    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback

        traceback.print_exc()


def test_method_analysis():
    """Test specific method analysis"""
    print("\n🔍 Testing Method Analysis")
    print("=" * 40)

    try:
        from predictions_tracker.core.services.data_service import DataService

        data_service = DataService()

        # Get available methods
        methods = data_service.get_available_methods()
        print(f"📊 Available methods: {len(methods)}")

        # Analyze first few methods
        for i, method in enumerate(methods[:5]):
            print(f"\n{i+1}. {method.get_name()}")
            print(f"   Code: {method.get_code()}")
            print(f"   Description: {method.get_description()}")

            # Test calculation
            try:
                # Get some test data
                test_data = data_service.get_pattern_data_for_analysis(1)
                if test_data:
                    result = method.calculate(test_data[0])
                    print(f"   Sample prediction: {result}")
                else:
                    print(f"   No test data available")
            except Exception as e:
                print(f"   ❌ Calculation error: {e}")

    except Exception as e:
        print(f"❌ Method analysis failed: {e}")


def test_data_service_methods():
    """Test DataService methods"""
    print("\n🔧 Testing DataService Methods")
    print("=" * 40)

    try:
        from predictions_tracker.core.services.data_service import DataService

        data_service = DataService()

        # Test get_pattern_data_for_analysis
        print("1. Testing get_pattern_data_for_analysis...")
        pattern_data = data_service.get_pattern_data_for_analysis(5)
        print(f"   Retrieved {len(pattern_data)} data points")

        if pattern_data:
            sample = pattern_data[0]
            print(
                f"   Sample data keys: {list(sample.keys()) if isinstance(sample, dict) else 'Not dict'}"
            )

        # Test get_available_methods
        print("\n2. Testing get_available_methods...")
        methods = data_service.get_available_methods()
        print(f"   Available methods: {len(methods)}")

        # Test predict_next_days
        print("\n3. Testing predict_next_days...")
        tomorrow = datetime.now() + timedelta(days=1)
        predictions = data_service.predict_next_days(tomorrow, 1)
        print(f"   Predictions type: {type(predictions)}")
        print(f"   Predictions: {predictions}")

    except Exception as e:
        print(f"❌ DataService methods test failed: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    # Run all tests
    test_data_service_methods()
    test_method_analysis()
    test_intelligence_system()

    print("\n" + "=" * 60)
    print("🎯 Test Summary:")
    print("- DataService methods: Basic functionality")
    print("- Method analysis: Method details and calculations")
    print("- Intelligence system: Enhanced predictions and analysis")
    print("=" * 60)
