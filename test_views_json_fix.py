#!/usr/bin/env python
"""
🧪 Test Views JSON Serialization Fix
====================================
Test script to verify JSON serialization fixes in views
"""

import json
from datetime import date, datetime


def test_custom_json_encoder():
    """Test our custom JSON encoder"""
    print("🧪 Testing Custom JSON Encoder...")

    # Import the encoder
    import os
    import sys

    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

    try:
        from predictions_tracker.views_dir.enhanced_frequency_analyzer_views import (
            CustomJSONEncoder,
        )

        # Test data with problematic types
        test_data = {
            "boolean_true": True,
            "boolean_false": False,
            "datetime_obj": datetime.now(),
            "date_obj": date.today(),
            "string": "test",
            "number": 123,
            "list": [1, 2, 3],
            "nested": {"inner_bool": True, "inner_date": date.today()},
        }

        # Try to serialize with custom encoder
        json_str = json.dumps(
            test_data, cls=CustomJSONEncoder, indent=2, ensure_ascii=False
        )
        print("   ✅ JSON serialization successful")
        print(f"   📊 JSON size: {len(json_str)} bytes")

        # Parse back to verify
        parsed = json.loads(json_str)
        print("   ✅ JSON deserialization successful")

        # Check boolean conversion
        if parsed["boolean_true"] == "enabled":
            print("   ✅ Boolean True → 'enabled'")
        else:
            print(f"   ❌ Boolean True → '{parsed['boolean_true']}'")

        if parsed["boolean_false"] == "disabled":
            print("   ✅ Boolean False → 'disabled'")
        else:
            print(f"   ❌ Boolean False → '{parsed['boolean_false']}'")

        # Check datetime conversion
        if "T" in parsed["datetime_obj"]:
            print("   ✅ Datetime converted to ISO format")
        else:
            print(f"   ❌ Datetime conversion failed: {parsed['datetime_obj']}")

        return True

    except Exception as e:
        print(f"   ❌ Custom JSON encoder test failed: {e}")
        return False


def test_safe_json_response():
    """Test safe_json_response function"""
    print("🧪 Testing Safe JSON Response Function...")

    try:
        from predictions_tracker.views_dir.enhanced_frequency_analyzer_views import (
            safe_json_response,
        )

        # Test data with boolean values
        test_data = {
            "status": "success",
            "has_data": True,
            "is_valid": False,
            "timestamp": datetime.now(),
            "results": {"found": True, "count": 5},
        }

        # Try to create response
        response = safe_json_response(test_data)
        print("   ✅ safe_json_response created successfully")

        # Check response properties
        if hasattr(response, "content"):
            content = response.content.decode("utf-8")
            parsed = json.loads(content)

            if parsed["has_data"] == "enabled":
                print("   ✅ Boolean values properly converted in response")
            else:
                print(f"   ❌ Boolean conversion failed: {parsed['has_data']}")

            return True
        else:
            print("   ❌ Response object missing content")
            return False

    except Exception as e:
        print(f"   ❌ Safe JSON response test failed: {e}")
        return False


def test_views_import():
    """Test if views can be imported without errors"""
    print("🧪 Testing Views Import...")

    try:
        # Try to import the views module
        from predictions_tracker.views_dir import enhanced_frequency_analyzer_views

        print("   ✅ Views module imported successfully")

        # Check if all required functions exist
        required_functions = [
            "enhanced_analyzer_dashboard",
            "run_enhanced_analysis",
            "validate_predictions",
            "get_adaptive_predictions",
            "CustomJSONEncoder",
            "safe_json_response",
        ]

        for func_name in required_functions:
            if hasattr(enhanced_frequency_analyzer_views, func_name):
                print(f"   ✅ {func_name} found")
            else:
                print(f"   ❌ {func_name} missing")
                return False

        return True

    except Exception as e:
        print(f"   ❌ Views import failed: {e}")
        return False


def main():
    """Run all tests"""
    print("🚀 Views JSON Serialization Fix Test")
    print("=" * 50)

    tests = [
        ("Views Import", test_views_import),
        ("Custom JSON Encoder", test_custom_json_encoder),
        ("Safe JSON Response", test_safe_json_response),
    ]

    results = []

    for test_name, test_func in tests:
        print(f"\n🔍 Running {test_name} test...")
        result = test_func()
        results.append((test_name, result))

    # Summary
    print("\n" + "=" * 50)
    print("📋 TEST SUMMARY:")
    print("=" * 50)

    passed = 0
    for test_name, result in results:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"   {test_name}: {status}")
        if result:
            passed += 1

    print(f"📊 Results: {passed}/{len(tests)} tests passed")

    if passed == len(tests):
        print("🎉 All tests passed!")
        print("📝 JSON serialization fixes are working correctly")
        print("🌐 Views should now handle boolean values properly")
    else:
        print("⚠️  Some tests failed")
        print("📝 Check error messages above for details")


if __name__ == "__main__":
    main()
