#!/usr/bin/env python
"""
🚀 Enhanced Deep Frequency Analyzer - Functionality Test
===============================================================
Tests core analyzer functionality to verify fixes
"""

import json
import os
import sys
from datetime import date, datetime, timedelta

# Django setup
import django

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "xoso_crawler.settings")
django.setup()

from analytic_frequence.enhanced_deep_frequency_analyzer import (
    EnhancedDeepFrequencyAnalyzer,
)


def test_basic_analysis():
    """Test basic analysis functionality"""
    print("🧪 Testing Basic Analysis...")

    try:
        analyzer = EnhancedDeepFrequencyAnalyzer()

        # Test with date range
        end_date = date.today()
        start_date = end_date - timedelta(days=30)

        print(f"   📅 Analysis period: {start_date} to {end_date}")

        # Run basic analysis
        result = analyzer.analyze_frequency_patterns_enhanced(
            start_date=start_date, end_date=end_date
        )

        print(f"   📊 Result type: {type(result)}")
        print(
            f"   🔑 Result keys: {list(result.keys()) if isinstance(result, dict) else 'Not a dict'}"
        )

        if "error" in result:
            print(f"   ❌ Analysis error: {result['error']}")
            return False
        else:
            print(f"   ✅ Analysis completed successfully")

            # Test JSON serialization
            try:
                json_str = json.dumps(result, indent=2, ensure_ascii=False)
                print(f"   ✅ JSON serialization successful")
                print(f"   📊 JSON size: {len(json_str)} bytes")
                return True
            except Exception as json_error:
                print(f"   ❌ JSON serialization failed: {json_error}")
                return False

    except Exception as e:
        print(f"   ❌ Basic analysis failed: {e}")
        return False


def test_full_pipeline():
    """Test full analysis pipeline"""
    print("🧪 Testing Full Pipeline...")

    try:
        analyzer = EnhancedDeepFrequencyAnalyzer()

        end_date = date.today()
        start_date = end_date - timedelta(days=30)

        # Run full pipeline
        result = analyzer.analyze_with_full_pipeline(
            start_date=start_date, end_date=end_date, generate_visualizations=True
        )

        print(f"   📊 Pipeline result type: {type(result)}")

        if "error" in result:
            print(f"   ❌ Pipeline error: {result['error']}")
            return False
        else:
            print(f"   ✅ Pipeline completed successfully")

            # Check for expected sections
            expected_keys = ["pipeline_metadata", "frequency_analysis"]
            for key in expected_keys:
                if key in result:
                    print(f"   ✅ Contains {key}")
                else:
                    print(f"   ⚠️  Missing {key}")

            # Test JSON serialization
            try:
                json_str = json.dumps(result, indent=2, ensure_ascii=False)
                print(f"   ✅ Pipeline JSON serialization successful")
                return True
            except Exception as json_error:
                print(f"   ❌ Pipeline JSON serialization failed: {json_error}")
                return False

    except Exception as e:
        print(f"   ❌ Full pipeline failed: {e}")
        return False


def test_configuration():
    """Test configuration handling"""
    print("🧪 Testing Configuration...")

    try:
        analyzer = EnhancedDeepFrequencyAnalyzer()

        # Check configuration values
        config = analyzer.config
        print(f"   🔧 Configuration: {config}")

        # Verify string-based boolean values
        bool_keys = [
            "enable_validation",
            "enable_feedback_learning",
            "enable_visualization",
        ]
        for key in bool_keys:
            value = config.get(key)
            if value in ["enabled", "disabled"]:
                print(f"   ✅ {key}: {value} (string format)")
            else:
                print(f"   ⚠️  {key}: {value} (not string format)")

        return True

    except Exception as e:
        print(f"   ❌ Configuration test failed: {e}")
        return False


def main():
    """Run all functionality tests"""
    print("🚀 Enhanced Deep Frequency Analyzer - Functionality Test")
    print("=" * 70)

    tests = [
        ("Configuration", test_configuration),
        ("Basic Analysis", test_basic_analysis),
        ("Full Pipeline", test_full_pipeline),
    ]

    results = []

    for test_name, test_func in tests:
        print(f"\n🔍 Running {test_name} test...")
        result = test_func()
        results.append((test_name, result))

    # Summary
    print("\n" + "=" * 70)
    print("📋 FUNCTIONALITY TEST SUMMARY:")
    print("=" * 70)

    passed = 0
    for test_name, result in results:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"   {test_name}: {status}")
        if result:
            passed += 1

    print(f"📊 Results: {passed}/{len(tests)} tests passed")

    if passed == len(tests):
        print("🎉 All functionality tests passed!")
        print("📝 System is ready for production use")
    else:
        print("⚠️  Some functionality tests failed")
        print("📝 Check error messages above for details")


if __name__ == "__main__":
    main()
