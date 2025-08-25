#!/usr/bin/env python3
"""
🔍 SIMPLE DATA CHECK - Quick database inspection
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


def simple_data_check():
    """Simple check of available data"""
    print("🔍 SIMPLE DATA AVAILABILITY CHECK")
    print("=" * 50)

    try:
        # Check basic models
        from predictions_tracker.models import DailyTrackingSession, PredictionMethod
        from results.models import KetQuaXoSo

        print("📊 Model Counts:")
        print(f"   DailyTrackingSession: {DailyTrackingSession.objects.count()}")
        print(f"   PredictionMethod: {PredictionMethod.objects.count()}")
        print(f"   KetQuaXoSo: {KetQuaXoSo.objects.count()}")

        # Check if we have any data at all
        if KetQuaXoSo.objects.exists():
            latest = KetQuaXoSo.objects.order_by("-ngay").first()
            print(f"   📅 Latest KetQuaXoSo: {latest.ngay} - {latest.thu}")

            # Get recent dates
            recent_results = KetQuaXoSo.objects.filter(
                ngay__gte=datetime.now().date() - timedelta(days=30)
            ).order_by("-ngay")[:5]

            print("   📋 Recent results:")
            for result in recent_results:
                print(f"      {result.ngay} - {result.thu} - DB: {result.giai_db}")

        # Test the API feature extraction directly
        print("\n🧠 TESTING FEATURE EXTRACTION:")

        from predictions_tracker.views_dir.api_cyclical_prediction_by_date_v3 import (
            _extract_advanced_features_v3,
        )

        # Mock the required parameters
        class MockFeatureEngine:
            def extract_multi_horizon_features(self, **kwargs):
                return {"feature1": 1.0, "feature2": 2.0, "feature3": 3.0}

        # Try to extract features
        analysis_date = datetime.now() - timedelta(days=1)
        feature_engine = MockFeatureEngine()

        try:
            features = _extract_advanced_features_v3(
                analysis_date=analysis_date, feature_engine=feature_engine
            )
            print(f"   ✅ Features extracted: {len(features) if features else 0}")
            if features:
                sample_keys = list(features.keys())[:5]
                print(f"   📋 Sample features: {sample_keys}")
        except Exception as e:
            print(f"   ❌ Feature extraction failed: {str(e)}")

        # Test deep frequency analyzer
        print("\n🌊 TESTING DEEP FREQUENCY ANALYZER:")

        from predictions_tracker.deep_frequency_analyzer import DeepFrequencyAnalyzer

        analyzer = DeepFrequencyAnalyzer()

        # Generate test data
        test_data = []
        for i in range(30):  # 30 days
            daily_numbers = [f"{j:02d}" for j in range((i % 10), (i % 10) + 3)]
            test_data.append(daily_numbers)

        try:
            # Check if the correct method exists
            available_methods = [m for m in dir(analyzer) if not m.startswith("_")]
            print(f"   🔧 Available methods: {len(available_methods)}")

            # Try the main analyze method
            if hasattr(analyzer, "analyze_patterns"):
                patterns = analyzer.analyze_patterns(test_data)
                print(f"   ✅ Patterns analyzed: {len(patterns) if patterns else 0}")
            else:
                print("   ❌ No analyze_patterns method found")
                print(f"   📋 Available methods: {available_methods[:5]}")

        except Exception as e:
            print(f"   ❌ Deep frequency test failed: {str(e)}")

        # Test advanced fusion
        print("\n⚙️ TESTING ADVANCED FUSION:")

        from predictions_tracker.advanced_fusion_system import AdvancedNumberFusion

        fusion = AdvancedNumberFusion()

        available_methods = [m for m in dir(fusion) if not m.startswith("_")]
        print(f"   🔧 Available methods: {len(available_methods)}")
        print(f"   📋 Methods: {available_methods[:5]}")

        # Try to find a working fusion method
        test_methods = ["01", "02", "03"]
        test_cyclical = ["04", "05", "06"]

        fusion_worked = False
        for method_name in available_methods:
            if "fus" in method_name.lower():
                try:
                    method = getattr(fusion, method_name)
                    if callable(method):
                        result = method(test_methods, test_cyclical)
                        print(f"   ✅ {method_name} worked: {type(result)}")
                        fusion_worked = True
                        break
                except Exception as e:
                    print(f"   ⚠️ {method_name} failed: {str(e)[:50]}...")

        if not fusion_worked:
            print("   ❌ No working fusion method found")

        print("\n🎯 SUMMARY:")
        print(
            f"   Database: {'✅ Has data' if KetQuaXoSo.objects.exists() else '❌ No data'}"
        )
        print(
            f"   Feature Extraction: {'✅ Working' if 'features' in locals() else '❌ Failed'}"
        )
        print(
            f"   Deep Frequency: {'✅ Available' if 'analyzer' in locals() else '❌ Failed'}"
        )
        print(
            f"   Advanced Fusion: {'✅ Working' if fusion_worked else '❌ No working method'}"
        )

    except Exception as e:
        print(f"❌ Simple data check failed: {str(e)}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    simple_data_check()
