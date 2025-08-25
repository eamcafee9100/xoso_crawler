#!/usr/bin/env python3
"""
🔍 ROOT CAUSE ANALYSIS - Phase 1 Issues
Debug why the system is showing 0 features and no data
"""

import os
import sys
from datetime import datetime, timedelta

import django

# Add the project root to Python path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

# Setup Django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "xoso_crawler.settings")
django.setup()


def debug_data_availability():
    """Check what data is actually available in the database"""
    print("🔍 ROOT CAUSE ANALYSIS - DATA AVAILABILITY")
    print("=" * 60)

    # 1. Check database models
    from predictions_tracker.models import (
        DailyTrackingSession,
        PredictionMethod,
        TrackingEvaluation,
    )
    from results.models import KetQuaXoSo

    print("📊 1. DATABASE MODEL ANALYSIS")

    # Check DailyTrackingSession
    sessions = DailyTrackingSession.objects.all()
    print(f"   📅 DailyTrackingSession records: {sessions.count()}")

    if sessions.exists():
        latest_session = sessions.order_by("-prediction_date").first()
        oldest_session = sessions.order_by("prediction_date").first()
        print(
            f"   📅 Date range: {oldest_session.prediction_date} to {latest_session.prediction_date}"
        )
        print(
            f"   📅 Latest session: {latest_session.prediction_date} - {latest_session.session_id}"
        )

    # Check PredictionMethod
    methods = PredictionMethod.objects.all()
    print(f"   🔧 PredictionMethod records: {methods.count()}")

    if methods.exists():
        for method in methods[:5]:  # Show first 5
            print(
                f"      - {method.name} (Code: {method.code}) - Category: {method.category}"
            )

    # Check KetQuaXoSo
    results = KetQuaXoSo.objects.all()
    print(f"   📈 KetQuaXoSo records: {results.count()}")

    if results.exists():
        latest_result = results.order_by("-ngay").first()
        print(f"   📈 Latest result: {latest_result.ngay}")

    print()


def debug_feature_extraction():
    """Debug the feature extraction process"""
    print("🧠 2. FEATURE EXTRACTION DEBUG")

    from datetime import datetime, timedelta

    from predictions_tracker.views_dir.api_cyclical_prediction_by_date_v3 import (
        _extract_advanced_features_v3,
    )

    # Test feature extraction directly
    analysis_date = datetime.now() - timedelta(days=1)

    try:
        # Test different lookback periods
        lookback_periods = {
            "ultra_short": 30,
            "short_term": 90,
            "medium_term": 365,
            "long_term": 730,
        }

        for period_name, days in lookback_periods.items():
            print(f"   🔍 Testing {period_name} ({days} days)")

            try:
                features = _extract_advanced_features_v3(
                    analysis_date=analysis_date,
                    lookback_days=days,
                    location="MB",  # Default location
                )

                print(
                    f"      📊 Features extracted: {len(features) if features else 0}"
                )
                if features:
                    print(f"      📋 Sample features: {list(features.keys())[:5]}")
                else:
                    print("      ❌ No features extracted")

            except Exception as e:
                print(f"      ❌ Error: {str(e)}")

    except Exception as e:
        print(f"   ❌ Feature extraction test failed: {str(e)}")

    print()


def debug_deep_frequency_methods():
    """Debug deep frequency analyzer methods"""
    print("🌊 3. DEEP FREQUENCY ANALYZER DEBUG")

    from predictions_tracker.deep_frequency_analyzer import DeepFrequencyAnalyzer

    analyzer = DeepFrequencyAnalyzer()

    # Check available methods
    methods = [method for method in dir(analyzer) if not method.startswith("_")]
    print(f"   🔧 Available methods: {len(methods)}")
    for method in methods:
        print(f"      - {method}")

    # Test with sample data
    print("   🧪 Testing with sample data:")
    sample_data = []
    for i in range(100):  # 100 days of sample data
        daily_numbers = [f"{j:02d}" for j in range(i % 10, i % 10 + 3)]
        sample_data.append(daily_numbers)

    try:
        # Test individual methods
        hot_numbers = analyzer._identify_hot_numbers(sample_data)
        print(f"      🔥 Hot numbers: {len(hot_numbers)}")

        cold_numbers = analyzer._identify_cold_numbers(sample_data)
        print(f"      ❄️ Cold numbers: {len(cold_numbers)}")

        cyclical = analyzer._detect_cyclical_patterns(sample_data)
        print(f"      🔄 Cyclical patterns: {len(cyclical)}")

    except Exception as e:
        print(f"      ❌ Method test failed: {str(e)}")

    print()


def debug_advanced_fusion_methods():
    """Debug advanced fusion system methods"""
    print("⚙️ 4. ADVANCED FUSION SYSTEM DEBUG")

    from predictions_tracker.advanced_fusion_system import AdvancedNumberFusion

    fusion_system = AdvancedNumberFusion()

    # Check available methods
    methods = [method for method in dir(fusion_system) if not method.startswith("_")]
    print(f"   🔧 Available methods: {len(methods)}")
    for method in methods:
        print(f"      - {method}")

    # Test with sample data
    print("   🧪 Testing with sample data:")
    method_numbers = ["01", "15", "23", "45", "67"]
    cyclical_numbers = ["12", "23", "34", "56", "78"]

    try:
        # Find the correct method name
        if hasattr(fusion_system, "fuse_predictions_advanced"):
            result = fusion_system.fuse_predictions_advanced(
                method_numbers, cyclical_numbers
            )
        elif hasattr(fusion_system, "fusion_with_uncertainty"):
            result = fusion_system.fusion_with_uncertainty(
                method_numbers, cyclical_numbers
            )
        elif hasattr(fusion_system, "advanced_fusion"):
            result = fusion_system.advanced_fusion(method_numbers, cyclical_numbers)
        else:
            print("      ❌ No suitable fusion method found")
            return

        print(
            f"      ✅ Fusion successful: {len(result.get('fused_numbers', []))} numbers"
        )

    except Exception as e:
        print(f"      ❌ Fusion test failed: {str(e)}")

    print()


def debug_api_parameters():
    """Debug API parameter handling"""
    print("🔧 5. API PARAMETER DEBUG")

    from django.http import HttpRequest

    from predictions_tracker.views_dir.api_cyclical_prediction_by_date_v3 import (
        api_cyclical_prediction_by_date_v3,
    )

    # Test different parameter scenarios
    test_scenarios = [
        {"analysis_date": "2025-07-28"},
        {"analysis_date": "2025-07-01"},
        {"analysis_date": "2025-01-01"},
        {"analysis_date": "2024-12-01"},
        {"analysis_date": "2024-01-01"},
    ]

    for i, params in enumerate(test_scenarios):
        print(f"   🧪 Scenario {i+1}: {params}")

        request = HttpRequest()
        request.method = "GET"
        request.GET = params

        try:
            import time

            start_time = time.time()
            response = api_cyclical_prediction_by_date_v3(request)
            execution_time = time.time() - start_time

            print(f"      ⏱️ Time: {execution_time:.2f}s")
            print(f"      📊 Status: {response.status_code}")
            print(f"      📄 Size: {len(response.content)} bytes")

            if response.status_code == 200:
                import json

                data = json.loads(response.content.decode("utf-8"))
                debug_info = data.get("debug_info", {})
                print(f"      🧠 Features: {debug_info.get('total_features', 'N/A')}")
                print(f"      🎲 Predictions: {len(data.get('predicted_numbers', []))}")

        except Exception as e:
            print(f"      ❌ Error: {str(e)}")

        print()


def main():
    """Run all debug checks"""
    debug_data_availability()
    debug_feature_extraction()
    debug_deep_frequency_methods()
    debug_advanced_fusion_methods()
    debug_api_parameters()

    print("🎯 ROOT CAUSE ANALYSIS COMPLETE")
    print("=" * 60)
    print("💡 Check the output above to identify:")
    print("   1. Database data availability issues")
    print("   2. Feature extraction problems")
    print("   3. Method naming mismatches")
    print("   4. API parameter handling issues")


if __name__ == "__main__":
    main()
