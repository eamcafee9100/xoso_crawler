#!/usr/bin/env python3
"""
Debug Boolean JSON Serialization Issues in Real Time
Direct test của exact functions để tìm vấn đề
"""

import json
import os
import sys
from datetime import date, datetime

# Add the project directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))


def test_current_custom_json_encoder():
    """Test CustomJSONEncoder hiện tại trong views file"""

    print("🔍 Testing CURRENT CustomJSONEncoder from views file...")

    try:
        # Import CustomJSONEncoder từ file hiện tại
        sys.path.insert(
            0,
            os.path.join(os.path.dirname(__file__), "predictions_tracker", "views_dir"),
        )
        from enhanced_frequency_analyzer_views import CustomJSONEncoder

        # Test data với nhiều boolean
        test_data = {
            "simple_bool": True,
            "simple_bool2": False,
            "nested_dict": {"inner_bool": True, "more_nested": {"deep_bool": False}},
            "bool_array": [True, False, True],
            "mixed_array": [{"bool_in_array": True}, {"bool_in_array": False}],
        }

        print(f"   Original data có {count_booleans(test_data)} boolean values")

        # Test serialization
        json_result = json.dumps(test_data, cls=CustomJSONEncoder, ensure_ascii=False)
        print("   ✅ JSON serialization successful!")

        # Parse back và check
        parsed = json.loads(json_result)
        remaining_bools = count_booleans(parsed)

        print(f"   📊 Results:")
        print(
            f"   - simple_bool: {type(parsed['simple_bool'])} = '{parsed['simple_bool']}'"
        )
        print(
            f"   - nested_dict.inner_bool: {type(parsed['nested_dict']['inner_bool'])} = '{parsed['nested_dict']['inner_bool']}'"
        )
        print(
            f"   - bool_array[0]: {type(parsed['bool_array'][0])} = '{parsed['bool_array'][0]}'"
        )
        print(f"   - Remaining booleans: {remaining_bools}")

        if remaining_bools == 0:
            print("   🎉 ALL BOOLEANS CONVERTED SUCCESSFULLY!")
            return True
        else:
            print("   ❌ Some booleans still remain!")
            return False

    except Exception as e:
        print(f"   ❌ Test failed: {e}")
        import traceback

        traceback.print_exc()
        return False


def test_safe_json_response_function():
    """Test safe_json_response function"""

    print("\n🔍 Testing safe_json_response function...")

    try:
        # Mock Django HttpResponse
        class MockHttpResponse:
            def __init__(self, content, content_type="text/html", status=200):
                self.content = content
                self.content_type = content_type
                self.status_code = status

        # Import function
        sys.path.insert(
            0,
            os.path.join(os.path.dirname(__file__), "predictions_tracker", "views_dir"),
        )

        # Mock safe_json_response
        def safe_json_response_test(data, status=200):
            from enhanced_frequency_analyzer_views import CustomJSONEncoder

            json_data = json.dumps(data, cls=CustomJSONEncoder, ensure_ascii=False)
            return MockHttpResponse(
                json_data, content_type="application/json", status=status
            )

        # Test data
        test_data = {
            "status": "success",
            "has_results": True,
            "is_valid": False,
            "nested": {"is_significant": True, "pattern_detected": False},
        }

        response = safe_json_response_test(test_data)
        content = response.content

        # Parse response
        parsed = json.loads(content)

        print(f"   ✅ safe_json_response working!")
        print(f"   📊 Response data:")
        print(f"   - has_results: '{parsed['has_results']}'")
        print(f"   - nested.is_significant: '{parsed['nested']['is_significant']}'")

        # Check if any booleans remain
        remaining_bools = count_booleans(parsed)
        if remaining_bools == 0:
            print("   🎉 safe_json_response converts all booleans!")
            return True
        else:
            print(f"   ❌ {remaining_bools} booleans still remain!")
            return False

    except Exception as e:
        print(f"   ❌ Test failed: {e}")
        import traceback

        traceback.print_exc()
        return False


def debug_analyzer_data_structure():
    """Debug analyzer data structure to find boolean sources"""

    print("\n🔍 Debugging Enhanced Analyzer Data Structure...")

    # Simulate typical analyzer output
    mock_analyzer_output = {
        # Common places where booleans might appear
        "hot_numbers": {
            "15": {
                "frequency": 25,
                "hotness_score": 3.5,
                "is_trending": True,  # Boolean from logic
                "has_momentum": False,  # Boolean from logic
                "is_significant": "significant",  # Already string
            }
        },
        "cold_numbers": {
            "87": {
                "is_overdue": True,  # Boolean from logic
                "needs_attention": False,  # Boolean from logic
            }
        },
        "metadata": {
            "full_pipeline_enabled": True,  # Boolean from request
            "debug_mode": False,  # Boolean from config
            "success": True,  # Boolean from status
        },
        # Database query results might contain booleans
        "query_results": [
            {"is_active": True, "number": 15},  # From database
            {"is_active": False, "number": 87},  # From database
        ],
    }

    print(f"   Total booleans in mock data: {count_booleans(mock_analyzer_output)}")

    # Test conversion
    try:
        from predictions_tracker.views_dir.enhanced_frequency_analyzer_views import (
            CustomJSONEncoder,
        )

        json_result = json.dumps(
            mock_analyzer_output, cls=CustomJSONEncoder, ensure_ascii=False
        )
        parsed = json.loads(json_result)

        remaining_bools = count_booleans(parsed)
        print(f"   After conversion: {remaining_bools} booleans remain")

        if remaining_bools > 0:
            print("   ❌ Some booleans not converted:")
            find_remaining_booleans(parsed)
        else:
            print("   ✅ All booleans converted successfully!")

        return remaining_bools == 0

    except Exception as e:
        print(f"   ❌ Conversion failed: {e}")
        return False


def count_booleans(obj, path=""):
    """Count boolean values in nested structure"""
    count = 0
    if isinstance(obj, bool):
        count += 1
    elif isinstance(obj, dict):
        for key, value in obj.items():
            count += count_booleans(value, f"{path}.{key}" if path else key)
    elif isinstance(obj, list):
        for i, item in enumerate(obj):
            count += count_booleans(item, f"{path}[{i}]")
    return count


def find_remaining_booleans(obj, path=""):
    """Find remaining boolean values"""
    if isinstance(obj, bool):
        print(f"      Boolean at {path}: {obj}")
    elif isinstance(obj, dict):
        for key, value in obj.items():
            find_remaining_booleans(value, f"{path}.{key}" if path else key)
    elif isinstance(obj, list):
        for i, item in enumerate(obj):
            find_remaining_booleans(item, f"{path}[{i}]")


def main():
    print("🚀 Enhanced Deep Frequency Analyzer - Boolean Debug Session")
    print("=" * 70)
    print(
        "📋 Debugging the persistent 'Object of type bool is not JSON serializable' error"
    )
    print("=" * 70)

    success_count = 0
    total_tests = 3

    # Test 1: Current CustomJSONEncoder
    if test_current_custom_json_encoder():
        success_count += 1

    # Test 2: safe_json_response function
    if test_safe_json_response_function():
        success_count += 1

    # Test 3: Analyzer data structure
    if debug_analyzer_data_structure():
        success_count += 1

    print("\n" + "=" * 70)
    print(f"🎯 Debug Results: {success_count}/{total_tests} tests passed")

    if success_count == total_tests:
        print("🎉 ALL TESTS PASSED!")
        print("✅ CustomJSONEncoder is working correctly")
        print("✅ Boolean conversion is functioning")
        print("✅ The error must be coming from a different source")
        print("\n💡 Possible remaining issues:")
        print("   1. Django caching old code versions")
        print("   2. Boolean values from database queries")
        print("   3. Boolean values from external libraries")
        print("   4. Code not using safe_json_response in some path")
    else:
        print("❌ SOME TESTS FAILED!")
        print("🔧 The CustomJSONEncoder or safe_json_response needs further fixes")

    print("=" * 70)


if __name__ == "__main__":
    main()
