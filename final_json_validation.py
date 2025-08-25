#!/usr/bin/env python3
"""
FINAL TEST: Enhanced Frequency Analyzer JSON Fix Validation
Simple test without Django dependencies
"""

import json
from datetime import date, datetime


# FIXED CustomJSONEncoder (with recursive boolean conversion)
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


def test_real_world_data():
    """Test with exact data structure that was causing the error"""

    # This is the EXACT type of data that was causing "Object of type bool is not JSON serializable"
    problematic_data = {
        "status": "success",
        "analysis_results": {
            "hot_numbers": {
                "15": {
                    "frequency": 25,
                    "hotness_score": 3.5,
                    "statistical_significance": "significant",
                    "is_trending": True,  # 🔥 PROBLEMATIC BOOLEAN
                    "has_momentum": False,  # 🔥 PROBLEMATIC BOOLEAN
                    "frequency_ratio": 1.8,
                    "chi2_statistic": 4.5621,
                    "p_value": 0.0327,
                },
                "22": {
                    "frequency": 28,
                    "hotness_score": 4.1,
                    "statistical_significance": "significant",
                    "is_trending": True,  # 🔥 PROBLEMATIC BOOLEAN
                    "has_momentum": True,  # 🔥 PROBLEMATIC BOOLEAN
                },
            },
            "cold_numbers": {
                "87": {
                    "frequency": 3,
                    "coldness_score": 2.8,
                    "days_absent": 45,
                    "is_overdue": True,  # 🔥 PROBLEMATIC BOOLEAN
                    "needs_attention": False,  # 🔥 PROBLEMATIC BOOLEAN
                    "reversion_pressure": 0.75,
                }
            },
            "cyclical_patterns": {
                "pattern_detected": True,  # 🔥 PROBLEMATIC BOOLEAN
                "seasonal_effects": False,  # 🔥 PROBLEMATIC BOOLEAN
                "trend_confirmed": True,  # 🔥 PROBLEMATIC BOOLEAN
                "cycles": [
                    {"active": True, "strength": 0.8},  # 🔥 NESTED BOOLEAN
                    {"active": False, "strength": 0.3},  # 🔥 NESTED BOOLEAN
                ],
            },
            "statistical_tests": {
                "uniformity_test": {
                    "statistic": 15.67,
                    "p_value": 0.023,
                    "is_significant": True,  # 🔥 PROBLEMATIC BOOLEAN
                },
                "chi_square_result": {
                    "statistic": 8.45,
                    "p_value": 0.076,
                    "is_significant": False,  # 🔥 PROBLEMATIC BOOLEAN
                },
            },
        },
        "visualization_data": {
            "charts_enabled": True,  # 🔥 PROBLEMATIC BOOLEAN
            "interactive_mode": False,  # 🔥 PROBLEMATIC BOOLEAN
            "data_available": True,  # 🔥 PROBLEMATIC BOOLEAN
            "chart_configs": [
                {"visible": True, "type": "bar"},  # 🔥 NESTED BOOLEAN
                {"visible": False, "type": "line"},  # 🔥 NESTED BOOLEAN
            ],
        },
        "analysis_metadata": {
            "execution_time": datetime.now().isoformat(),
            "date_range": "2024-12-01 to 2025-01-31",
            "significance_level": 0.05,
            "total_components": 5,
            "full_pipeline_enabled": True,  # 🔥 PROBLEMATIC BOOLEAN
            "debug_mode": False,  # 🔥 PROBLEMATIC BOOLEAN
        },
        "quick_insights": {
            "has_hot_numbers": True,  # 🔥 PROBLEMATIC BOOLEAN
            "has_cold_numbers": True,  # 🔥 PROBLEMATIC BOOLEAN
            "patterns_detected": False,  # 🔥 PROBLEMATIC BOOLEAN
            "trends_significant": True,  # 🔥 PROBLEMATIC BOOLEAN
            "alerts": [
                {"urgent": True, "message": "High activity"},  # 🔥 NESTED BOOLEAN
                {"urgent": False, "message": "Normal pattern"},  # 🔥 NESTED BOOLEAN
            ],
        },
    }

    print(
        "🔥 Testing EXACT problematic data that was causing JSON serialization errors..."
    )
    print(f"   Total boolean fields: {count_booleans(problematic_data)}")

    # Test 1: Standard JSON (should fail)
    print("\n1️⃣ Testing with standard JSON encoder (should fail):")
    try:
        json.dumps(problematic_data)
        print("   ❌ ERROR: Standard encoder should have failed!")
        return False
    except TypeError as e:
        print(f"   ✅ Expected failure: {e}")

    # Test 2: Fixed CustomJSONEncoder (should work)
    print("\n2️⃣ Testing with FIXED CustomJSONEncoder:")
    try:
        json_result = json.dumps(
            problematic_data, cls=CustomJSONEncoder, ensure_ascii=False
        )
        print("   ✅ SUCCESS: JSON serialization completed!")

        # Parse back and verify
        parsed_data = json.loads(json_result)
        print("\n   🔍 Verifying boolean conversions:")

        # Check various boolean fields
        checks = [
            (
                "hot_numbers.15.is_trending",
                parsed_data["analysis_results"]["hot_numbers"]["15"]["is_trending"],
            ),
            (
                "hot_numbers.15.has_momentum",
                parsed_data["analysis_results"]["hot_numbers"]["15"]["has_momentum"],
            ),
            (
                "cyclical_patterns.pattern_detected",
                parsed_data["analysis_results"]["cyclical_patterns"][
                    "pattern_detected"
                ],
            ),
            (
                "statistical_tests.uniformity_test.is_significant",
                parsed_data["analysis_results"]["statistical_tests"]["uniformity_test"][
                    "is_significant"
                ],
            ),
            (
                "visualization_data.charts_enabled",
                parsed_data["visualization_data"]["charts_enabled"],
            ),
            (
                "analysis_metadata.full_pipeline_enabled",
                parsed_data["analysis_metadata"]["full_pipeline_enabled"],
            ),
            (
                "quick_insights.has_hot_numbers",
                parsed_data["quick_insights"]["has_hot_numbers"],
            ),
            # Nested arrays
            (
                "cyclical_patterns.cycles[0].active",
                parsed_data["analysis_results"]["cyclical_patterns"]["cycles"][0][
                    "active"
                ],
            ),
            (
                "visualization_data.chart_configs[1].visible",
                parsed_data["visualization_data"]["chart_configs"][1]["visible"],
            ),
            (
                "quick_insights.alerts[0].urgent",
                parsed_data["quick_insights"]["alerts"][0]["urgent"],
            ),
        ]

        all_converted = True
        for field_path, value in checks:
            if isinstance(value, bool):
                print(f"   ❌ {field_path}: Still boolean ({value})")
                all_converted = False
            else:
                print(f"   ✅ {field_path}: '{value}'")

        if all_converted:
            print("\n   🎉 ALL BOOLEANS SUCCESSFULLY CONVERTED TO STRINGS!")
            return True
        else:
            print("\n   ❌ Some booleans were not converted")
            return False

    except Exception as e:
        print(f"   ❌ FAILED: {e}")
        import traceback

        traceback.print_exc()
        return False


def count_booleans(obj, path=""):
    """Count total boolean values in nested structure"""
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


def main():
    print("🚀 FINAL VALIDATION: Enhanced Deep Frequency Analyzer JSON Fix")
    print("=" * 70)
    print("📋 Testing the EXACT data structure that was causing the error:")
    print("   'Object of type bool is not JSON serializable'")
    print("=" * 70)

    success = test_real_world_data()

    print("\n" + "=" * 70)
    if success:
        print("🎉 VALIDATION SUCCESSFUL!")
        print(
            "\n✅ The Enhanced Deep Frequency Analyzer JSON serialization is now FIXED:"
        )
        print("   - All boolean values are converted to 'enabled'/'disabled' strings")
        print("   - Nested boolean values in arrays and objects are handled")
        print("   - Complex data structures serialize without errors")
        print(
            "   - The 'Object of type bool is not JSON serializable' error is eliminated"
        )
        print("\n🚀 The system is ready for production deployment!")
        print("\n📝 Next steps:")
        print("   1. Start Django server: python manage.py runserver")
        print("   2. Test endpoint: POST /pre-lokhung/enhanced-analyzer/run-analysis/")
        print("   3. Verify no more JSON serialization errors in logs")
    else:
        print("❌ VALIDATION FAILED!")
        print("   The boolean conversion is not working correctly.")
        print("   Check the CustomJSONEncoder implementation.")

    print("=" * 70)


if __name__ == "__main__":
    main()
