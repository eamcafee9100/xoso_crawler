#!/usr/bin/env python3
"""
Direct Test for JSON Serialization Issues
Reproduce the exact error happening in enhanced_frequency_analyzer_views
"""

import json
import os
import sys
from datetime import date, datetime

# Add the project directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))


# Custom JSON Encoder from views (FIXED VERSION)
class CustomJSONEncoder(json.JSONEncoder):
    """Custom JSON encoder to handle boolean and datetime objects"""

    def default(self, o):
        if isinstance(o, bool):
            return "enabled" if o else "disabled"
        elif isinstance(o, datetime):
            return o.isoformat()
        elif isinstance(o, date):
            return o.isoformat()
        elif hasattr(o, "__dict__"):
            return o.__dict__
        return super().default(o)

    def encode(self, o):
        """Override encode to handle booleans in nested structures"""
        return super().encode(self._convert_booleans(o))

    def _convert_booleans(self, obj):
        """Recursively convert all boolean values to strings"""
        if isinstance(obj, bool):
            return "enabled" if obj else "disabled"
        elif isinstance(obj, dict):
            return {key: self._convert_booleans(value) for key, value in obj.items()}
        elif isinstance(obj, list):
            return [self._convert_booleans(item) for item in obj]
        elif isinstance(obj, tuple):
            return tuple(self._convert_booleans(item) for item in obj)
        else:
            return obj


def test_enhanced_analyzer_json():
    """Test specific data that might cause JSON serialization error"""

    # Test data similar to what enhanced analyzer returns
    test_data = {
        "status": "success",
        "analysis_results": {
            "hot_numbers": {
                "15": {
                    "frequency": 25,
                    "hotness_score": 3.5,
                    "statistical_significance": "significant",
                    # These might be problematic
                    "is_trending": True,
                    "has_momentum": False,
                }
            },
            "cold_numbers": {
                "87": {
                    "frequency": 3,
                    "coldness_score": 2.8,
                    "days_absent": 45,
                    # These might be problematic
                    "is_overdue": True,
                    "needs_attention": False,
                }
            },
            # Pattern analysis might have booleans
            "cyclical_patterns": {
                "pattern_detected": True,
                "seasonal_effects": False,
                "trend_confirmed": True,
            },
            # Statistical tests might have booleans
            "statistical_tests": {
                "uniformity_test": {
                    "statistic": 15.67,
                    "p_value": 0.023,
                    "is_significant": True,  # This could be the problem
                },
                "chi_square_result": {
                    "statistic": 8.45,
                    "p_value": 0.076,
                    "is_significant": False,  # This could be the problem
                },
            },
        },
        "visualization_data": {
            "charts_enabled": True,
            "interactive_mode": False,
            "data_available": True,
        },
        "analysis_metadata": {
            "execution_time": datetime.now().isoformat(),
            "date_range": "2024-12-01 to 2025-01-31",
            "significance_level": 0.05,
            "total_components": 5,
            "full_pipeline_enabled": True,  # This could be the problem
        },
        "quick_insights": {
            "has_hot_numbers": True,
            "has_cold_numbers": True,
            "patterns_detected": False,
        },
    }

    print("🧪 Testing JSON serialization with potential boolean issues...")

    try:
        # Test without custom encoder (should fail)
        print("\n1. Testing with standard JSON encoder (should fail):")
        try:
            json_standard = json.dumps(test_data, ensure_ascii=False)
            print("   ❌ Standard encoder shouldn't work!")
        except TypeError as e:
            print(f"   ✅ Expected error with standard encoder: {e}")

        # Test with custom encoder (should work)
        print("\n2. Testing with CustomJSONEncoder:")
        json_custom = json.dumps(test_data, cls=CustomJSONEncoder, ensure_ascii=False)
        print("   ✅ Custom encoder successful!")

        # Parse back to verify
        parsed_data = json.loads(json_custom)
        print("\n3. Verifying boolean conversion:")
        print(
            f"   - is_trending: {parsed_data['analysis_results']['hot_numbers']['15']['is_trending']}"
        )
        print(
            f"   - has_momentum: {parsed_data['analysis_results']['hot_numbers']['15']['has_momentum']}"
        )
        print(
            f"   - full_pipeline_enabled: {parsed_data['analysis_metadata']['full_pipeline_enabled']}"
        )
        print(
            f"   - has_hot_numbers: {parsed_data['quick_insights']['has_hot_numbers']}"
        )

        return True

    except Exception as e:
        print(f"   ❌ Custom encoder failed: {e}")
        print(f"   Error type: {type(e).__name__}")
        import traceback

        traceback.print_exc()
        return False


def test_safe_json_response():
    """Test the safe_json_response function from views"""
    from django.http import HttpResponse

    def safe_json_response(data, status=200):
        """Create a JsonResponse with custom encoder to handle boolean values"""
        json_data = json.dumps(data, cls=CustomJSONEncoder, ensure_ascii=False)
        return HttpResponse(json_data, content_type="application/json", status=status)

    test_data = {
        "boolean_field": True,
        "another_boolean": False,
        "nested": {
            "more_booleans": True,
            "significance": False,
        },
    }

    try:
        response = safe_json_response(test_data)
        print(f"✅ safe_json_response worked! Status: {response.status_code}")
        print(f"   Content: {response.content.decode()[:100]}...")
        return True
    except Exception as e:
        print(f"❌ safe_json_response failed: {e}")
        return False


def find_boolean_patterns():
    """Search for boolean patterns that might be missed"""

    # Common boolean patterns that might slip through
    problematic_patterns = [
        {"test": True, "result": False},
        {"enabled": True, "disabled": False},
        {"significant": True, "insignificant": False},
        {"detected": True, "missing": False},
        {"valid": True, "invalid": False},
    ]

    print("\n🔍 Testing various boolean patterns:")
    for i, pattern in enumerate(problematic_patterns):
        try:
            json_result = json.dumps(pattern, cls=CustomJSONEncoder)
            parsed = json.loads(json_result)
            print(f"   Pattern {i+1}: ✅ {parsed}")
        except Exception as e:
            print(f"   Pattern {i+1}: ❌ {e}")


def main():
    print("🚀 Enhanced Deep Frequency Analyzer - JSON Serialization Debug")
    print("=" * 70)

    success_count = 0

    # Test 1: Enhanced analyzer JSON
    print("\n📋 Test 1: Enhanced Analyzer JSON Structure")
    if test_enhanced_analyzer_json():
        success_count += 1

    # Test 2: Safe JSON response
    print("\n📋 Test 2: Safe JSON Response Function")
    try:
        if test_safe_json_response():
            success_count += 1
    except ImportError:
        print("   ⚠️ Django not available, skipping safe_json_response test")

    # Test 3: Boolean patterns
    print("\n📋 Test 3: Boolean Pattern Analysis")
    find_boolean_patterns()
    success_count += 1

    # Summary
    print("\n" + "=" * 70)
    print(f"🎯 Test Results: {success_count}/3 tests completed")

    if success_count >= 2:
        print("✅ JSON serialization should be working correctly!")
        print("\n🔍 If you're still getting errors, the issue might be:")
        print("   1. Boolean values in database query results")
        print("   2. Boolean values in Django model fields")
        print("   3. Boolean values from third-party libraries")
        print("   4. Caching system returning boolean values")
        print(
            "\n💡 Recommendation: Add debugging print statements in views to identify exact boolean source"
        )
    else:
        print("❌ JSON serialization has issues!")


if __name__ == "__main__":
    main()
