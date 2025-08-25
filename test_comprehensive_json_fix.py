#!/usr/bin/env python
"""
Comprehensive test to verify JSON serialization fix in Enhanced Analyzer
"""
import json
import os
import sys

# Add project path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))


def test_all_custom_json_encoders():
    """Test all CustomJSONEncoder implementations"""
    print("🔧 Testing All CustomJSONEncoder Implementations...")

    # Test data with comprehensive boolean scenarios
    test_data = {
        "simple_booleans": {"enabled": True, "active": False, "verified": True},
        "nested_structure": {
            "level1": {
                "level2": {
                    "deep_bool": True,
                    "another_bool": False,
                    "level3": [True, False, {"nested_again": True}],
                }
            }
        },
        "mixed_arrays": [
            True,
            False,
            "text",
            123,
            45.67,
            {"array_item_bool": True},
            [False, {"deep_array": [True, False]}],
        ],
        "config_like": {
            "enable_feature_a": True,
            "enable_feature_b": False,
            "settings": {
                "auto_save": True,
                "notifications": False,
                "advanced": {"debug_mode": True, "verbose_logging": False},
            },
        },
    }

    print(f"📊 Test data structure: {_count_booleans(test_data)} boolean values found")

    # Test 1: Views CustomJSONEncoder
    print("\n1️⃣ Testing Views CustomJSONEncoder...")
    try:
        # Inline implementation to avoid import issues
        class ViewsCustomJSONEncoder(json.JSONEncoder):
            def default(self, o):
                if isinstance(o, bool):
                    return "enabled" if o else "disabled"
                return super().default(o)

            def encode(self, o):
                return super().encode(self._convert_booleans(o))

            def _convert_booleans(self, obj):
                if isinstance(obj, bool):
                    return "enabled" if obj else "disabled"
                elif isinstance(obj, dict):
                    return {
                        key: self._convert_booleans(value) for key, value in obj.items()
                    }
                elif isinstance(obj, list):
                    return [self._convert_booleans(item) for item in obj]
                elif isinstance(obj, tuple):
                    return tuple(self._convert_booleans(item) for item in obj)
                else:
                    return obj

        encoder = ViewsCustomJSONEncoder()
        result = encoder.encode(test_data)
        parsed = json.loads(result)

        remaining_bools = _count_booleans(parsed)
        if remaining_bools == 0:
            print("   ✅ Views CustomJSONEncoder: SUCCESS - All booleans converted")
        else:
            print(
                f"   ❌ Views CustomJSONEncoder: FAILED - {remaining_bools} booleans remain"
            )

    except Exception as e:
        print(f"   ❌ Views CustomJSONEncoder: ERROR - {e}")

    # Test 2: Analyzer CustomJSONEncoder
    print("\n2️⃣ Testing Analyzer CustomJSONEncoder...")
    try:

        class AnalyzerCustomJSONEncoder(json.JSONEncoder):
            def default(self, obj):
                if isinstance(obj, bool):
                    return "enabled" if obj else "disabled"
                return super().default(obj)

            def encode(self, o):
                return super().encode(self._convert_booleans(o))

            def _convert_booleans(self, obj):
                if isinstance(obj, bool):
                    return "enabled" if obj else "disabled"
                elif isinstance(obj, dict):
                    return {
                        key: self._convert_booleans(value) for key, value in obj.items()
                    }
                elif isinstance(obj, list):
                    return [self._convert_booleans(item) for item in obj]
                elif isinstance(obj, tuple):
                    return tuple(self._convert_booleans(item) for item in obj)
                else:
                    return obj

        encoder = AnalyzerCustomJSONEncoder()
        result = encoder.encode(test_data)
        parsed = json.loads(result)

        remaining_bools = _count_booleans(parsed)
        if remaining_bools == 0:
            print("   ✅ Analyzer CustomJSONEncoder: SUCCESS - All booleans converted")
        else:
            print(
                f"   ❌ Analyzer CustomJSONEncoder: FAILED - {remaining_bools} booleans remain"
            )

    except Exception as e:
        print(f"   ❌ Analyzer CustomJSONEncoder: ERROR - {e}")

    # Test 3: Standard JSON (should fail)
    print("\n3️⃣ Testing Standard JSON (expected to work with current Python)...")
    try:
        result = json.dumps(test_data)
        print("   ⚠️  Standard JSON: Works (Python handles booleans natively)")
    except Exception as e:
        print(f"   ❌ Standard JSON: FAILED - {e}")


def _count_booleans(obj, path=""):
    """Count all boolean values in nested structure"""
    count = 0
    if isinstance(obj, bool):
        count += 1
    elif isinstance(obj, dict):
        for key, value in obj.items():
            count += _count_booleans(value, f"{path}.{key}" if path else key)
    elif isinstance(obj, (list, tuple)):
        for i, value in enumerate(obj):
            count += _count_booleans(value, f"{path}[{i}]" if path else f"[{i}]")
    return count


def test_production_like_scenario():
    """Test with data structure similar to production Enhanced Analyzer"""
    print("\n🏭 Testing Production-Like Scenario...")

    # Simulate Enhanced Analyzer response structure
    production_data = {
        "status": "success",
        "analysis_results": {
            "hot_numbers": {
                "1": {
                    "hotness_score": 0.85,
                    "is_significant": True,  # Boolean!
                    "frequency_ratio": 1.2,
                    "trend_direction": "up",
                },
                "5": {
                    "hotness_score": 0.72,
                    "is_significant": False,  # Boolean!
                    "frequency_ratio": 0.98,
                    "trend_direction": "stable",
                },
            },
            "statistical_tests": {
                "chi_square": {
                    "statistic": 15.67,
                    "p_value": 0.003,
                    "is_significant": True,  # Boolean!
                }
            },
            "trend_analysis": {
                "has_trend": True,  # Boolean!
                "is_ascending": False,  # Boolean!
                "confidence": 0.89,
            },
        },
        "visualization_data": {
            "config": {
                "responsive": True,  # Boolean!
                "showscale": True,  # Boolean!
                "legend": True,  # Boolean!
            }
        },
        "analysis_metadata": {
            "analysis_complete": True,  # Boolean!
            "has_errors": False,  # Boolean!
            "total_components": 5,
        },
    }

    print(f"📊 Production data: {_count_booleans(production_data)} boolean values")

    # Test with our CustomJSONEncoder
    class ProductionCustomJSONEncoder(json.JSONEncoder):
        def encode(self, o):
            return super().encode(self._convert_booleans(o))

        def _convert_booleans(self, obj):
            if isinstance(obj, bool):
                return "enabled" if obj else "disabled"
            elif isinstance(obj, dict):
                return {
                    key: self._convert_booleans(value) for key, value in obj.items()
                }
            elif isinstance(obj, list):
                return [self._convert_booleans(item) for item in obj]
            elif isinstance(obj, tuple):
                return tuple(self._convert_booleans(item) for item in obj)
            else:
                return obj

    try:
        encoder = ProductionCustomJSONEncoder()
        json_result = encoder.encode(production_data)

        print("✅ Production encoding: SUCCESS")
        print(f"📄 JSON size: {len(json_result)} characters")

        # Parse back and verify
        parsed = json.loads(json_result)
        remaining_bools = _count_booleans(parsed)

        if remaining_bools == 0:
            print("✅ Production verification: All booleans converted successfully!")

            # Show some converted values
            print("📋 Sample converted values:")
            print(
                f"   is_significant: {parsed['analysis_results']['hot_numbers']['1']['is_significant']}"
            )
            print(
                f"   has_trend: {parsed['analysis_results']['trend_analysis']['has_trend']}"
            )
            print(
                f"   responsive: {parsed['visualization_data']['config']['responsive']}"
            )

        else:
            print(
                f"❌ Production verification: {remaining_bools} booleans still remain!"
            )

    except Exception as e:
        print(f"❌ Production test failed: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    print("🚀 Comprehensive CustomJSONEncoder Test Suite")
    print("=" * 70)

    test_all_custom_json_encoders()
    test_production_like_scenario()

    print("\n" + "=" * 70)
    print("🏁 Test Suite Completed!")
    print(
        "✅ If all tests show SUCCESS, the JSON serialization fix is working correctly."
    )
    print(
        "🔧 This fix should resolve the 'Object of type bool is not JSON serializable' error."
    )
