#!/usr/bin/env python
"""
🔧 Complete Error Fix Test - Enhanced Deep Frequency Analyzer
============================================================
Test script to verify all fixes are working correctly
"""

import json
import os
import sys
from datetime import date, datetime, timedelta

# Add project to path for testing
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)


def test_safe_chi_square_function():
    """Test the new safe chi-square function"""
    print("🧪 Testing Safe Chi-Square Function...")

    try:
        from analytic_frequence.enhanced_deep_frequency_analyzer import (
            safe_chi_square_test,
        )

        # Test normal case
        result = safe_chi_square_test(15, 10, 0.05)
        print(f"   ✅ Normal case: {result}")

        # Test edge case with zero expected
        result = safe_chi_square_test(5, 0, 0.05)
        print(f"   ✅ Zero expected case: {result}")

        # Test equal values
        result = safe_chi_square_test(10, 10, 0.05)
        print(f"   ✅ Equal values case: {result}")

        return True

    except Exception as e:
        print(f"   ❌ Safe chi-square test failed: {e}")
        return False


def test_custom_json_encoder():
    """Test the enhanced custom JSON encoder"""
    print("🧪 Testing Enhanced Custom JSON Encoder...")

    try:
        from analytic_frequence.enhanced_deep_frequency_analyzer import (
            CustomJSONEncoder,
        )

        # Test data with all problematic types
        test_data = {
            "boolean_true": True,
            "boolean_false": False,
            "datetime_obj": datetime.now(),
            "date_obj": date.today(),
            "numpy_int": 42,  # Will be treated as regular int
            "string": "test",
            "nested": {"inner_bool": True, "inner_date": date.today()},
        }

        # Try to serialize
        json_str = json.dumps(
            test_data, cls=CustomJSONEncoder, indent=2, ensure_ascii=False
        )
        parsed = json.loads(json_str)

        # Verify boolean conversion
        if (
            parsed["boolean_true"] == "enabled"
            and parsed["boolean_false"] == "disabled"
        ):
            print("   ✅ Boolean conversion working")
        else:
            print(
                f"   ❌ Boolean conversion failed: {parsed['boolean_true']}, {parsed['boolean_false']}"
            )
            return False

        # Verify datetime conversion
        if "T" in parsed["datetime_obj"] and "-" in parsed["date_obj"]:
            print("   ✅ Datetime conversion working")
        else:
            print("   ❌ Datetime conversion failed")
            return False

        print(f"   📊 JSON serialization successful: {len(json_str)} bytes")
        return True

    except Exception as e:
        print(f"   ❌ Custom JSON encoder test failed: {e}")
        return False


def test_analyzer_instantiation():
    """Test if analyzer can be created without errors"""
    print("🧪 Testing Analyzer Instantiation...")

    try:
        from analytic_frequence.enhanced_deep_frequency_analyzer import (
            EnhancedDeepFrequencyAnalyzer,
        )

        analyzer = EnhancedDeepFrequencyAnalyzer()
        print("   ✅ Analyzer created successfully")

        # Check config values are strings
        config = analyzer.config
        bool_keys = [
            "enable_validation",
            "enable_feedback_learning",
            "enable_visualization",
        ]

        for key in bool_keys:
            value = config.get(key)
            if isinstance(value, str):
                print(f"   ✅ Config {key}: '{value}' (string)")
            else:
                print(f"   ❌ Config {key}: {value} ({type(value).__name__})")
                return False

        return True

    except Exception as e:
        print(f"   ❌ Analyzer instantiation failed: {e}")
        return False


def test_views_safe_functions():
    """Test if views safe functions work"""
    print("🧪 Testing Views Safe Functions...")

    try:
        from predictions_tracker.views_dir.enhanced_frequency_analyzer_views import (
            CustomJSONEncoder as ViewsEncoder,
        )
        from predictions_tracker.views_dir.enhanced_frequency_analyzer_views import (
            safe_json_response,
        )

        # Test data
        test_data = {
            "status": "success",
            "has_results": True,
            "is_valid": False,
            "timestamp": datetime.now(),
        }

        # Test safe_json_response
        response = safe_json_response(test_data)

        if hasattr(response, "content"):
            content = response.content.decode("utf-8")
            parsed = json.loads(content)

            if parsed["has_results"] == "enabled":
                print("   ✅ Views safe JSON response working")
                return True
            else:
                print(f"   ❌ Views JSON conversion failed: {parsed['has_results']}")
                return False
        else:
            print("   ❌ Response object invalid")
            return False

    except Exception as e:
        print(f"   ❌ Views safe functions test failed: {e}")
        return False


def test_analysis_methods():
    """Test key analysis methods for proper return types"""
    print("🧪 Testing Analysis Methods Return Types...")

    try:
        from analytic_frequence.enhanced_deep_frequency_analyzer import (
            safe_chi_square_test,
        )

        # Test various scenarios
        test_cases = [
            (10, 8, 0.05),
            (5, 15, 0.05),
            (0, 5, 0.05),
            (10, 0, 0.05),
        ]

        for observed, expected, sig_level in test_cases:
            result = safe_chi_square_test(observed, expected, sig_level)

            # Check all return values are JSON serializable
            json_str = json.dumps(result)
            parsed = json.loads(json_str)

            if "is_significant" in parsed and isinstance(parsed["is_significant"], str):
                print(
                    f"   ✅ Test case ({observed}, {expected}): {parsed['is_significant']}"
                )
            else:
                print(f"   ❌ Test case ({observed}, {expected}): invalid result")
                return False

        return True

    except Exception as e:
        print(f"   ❌ Analysis methods test failed: {e}")
        return False


def main():
    """Run all comprehensive tests"""
    print("🔧 Complete Error Fix Test - Enhanced Deep Frequency Analyzer")
    print("=" * 80)

    tests = [
        ("Safe Chi-Square Function", test_safe_chi_square_function),
        ("Enhanced Custom JSON Encoder", test_custom_json_encoder),
        ("Analyzer Instantiation", test_analyzer_instantiation),
        ("Views Safe Functions", test_views_safe_functions),
        ("Analysis Methods Return Types", test_analysis_methods),
    ]

    results = []

    for test_name, test_func in tests:
        print(f"\n🔍 Running {test_name} test...")
        result = test_func()
        results.append((test_name, result))

    # Summary
    print("\n" + "=" * 80)
    print("📋 COMPREHENSIVE TEST SUMMARY:")
    print("=" * 80)

    passed = 0
    for test_name, result in results:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"   {test_name}: {status}")
        if result:
            passed += 1

    print(f"📊 Results: {passed}/{len(tests)} tests passed")

    if passed == len(tests):
        print("\n🎉 ALL FIXES SUCCESSFUL!")
        print("✅ Chi-square errors: FIXED")
        print("✅ JSON serialization errors: FIXED")
        print("✅ Boolean value handling: FIXED")
        print("✅ Views safe response: WORKING")
        print("✅ Analyzer methods: RETURNING SAFE DATA")
        print("\n🚀 SYSTEM READY FOR DEPLOYMENT!")
        print("📝 Start server: python manage.py runserver")
        print("🌐 Access: http://localhost:8000/pre-lokhung/enhanced-analyzer/")
    else:
        print(f"\n⚠️  {len(tests) - passed} test(s) failed")
        print("📝 Review error messages above")


if __name__ == "__main__":
    main()
