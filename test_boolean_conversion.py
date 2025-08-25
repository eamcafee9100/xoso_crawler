#!/usr/bin/env python3
"""
Simple test to reproduce JSON serialization error without Django setup
"""

import json
import os
import sys

# Add the project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


class CustomJSONEncoder(json.JSONEncoder):
    """Custom JSON encoder to handle boolean and datetime objects"""

    def default(self, o):
        if isinstance(o, bool):
            return "enabled" if o else "disabled"
        elif hasattr(o, "isoformat"):  # datetime/date
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
        elif hasattr(obj, "__dict__") and not isinstance(obj, (str, int, float)):
            # Handle objects with __dict__
            return {
                key: self._convert_booleans(value)
                for key, value in obj.__dict__.items()
            }
        else:
            return obj


def find_booleans(obj, path=""):
    """Recursively find all boolean values in the data structure"""
    booleans_found = []

    if isinstance(obj, bool):
        booleans_found.append((path, obj))
    elif isinstance(obj, dict):
        for key, value in obj.items():
            new_path = f"{path}.{key}" if path else key
            booleans_found.extend(find_booleans(value, new_path))
    elif isinstance(obj, (list, tuple)):
        for i, value in enumerate(obj):
            new_path = f"{path}[{i}]" if path else f"[{i}]"
            booleans_found.extend(find_booleans(value, new_path))
    elif hasattr(obj, "__dict__") and not isinstance(obj, (str, int, float)):
        for key, value in obj.__dict__.items():
            new_path = f"{path}.{key}" if path else key
            booleans_found.extend(find_booleans(value, new_path))

    return booleans_found


def test_boolean_conversion():
    """Test various boolean data structures"""

    test_cases = [
        # Simple boolean
        True,
        False,
        # Boolean in dict
        {"enabled": True, "disabled": False},
        # Boolean in list
        [True, False, "string", 123],
        # Nested structures
        {
            "config": {
                "feature_a": True,
                "feature_b": False,
                "settings": [True, False, {"nested": True}],
            },
            "results": [{"success": True, "count": 5}, {"success": False, "count": 0}],
        },
        # Complex structure like what might come from analyzer
        {
            "status": "success",
            "analysis_results": [
                {
                    "component": "frequency_analysis",
                    "active": True,
                    "significant": False,
                    "patterns": [
                        {"pattern_id": 1, "valid": True, "confidence": 0.85},
                        {"pattern_id": 2, "valid": False, "confidence": 0.23},
                    ],
                }
            ],
            "metadata": {
                "full_pipeline": True,
                "cache_enabled": False,
                "debug_mode": True,
            },
        },
    ]

    encoder = CustomJSONEncoder()

    for i, test_data in enumerate(test_cases):
        print(f"\n🧪 Test Case {i+1}:")
        print(f"Original data type: {type(test_data)}")

        # Find all booleans
        booleans = find_booleans(test_data, f"test_{i+1}")
        if booleans:
            print(f"Found {len(booleans)} boolean values:")
            for path, value in booleans:
                print(f"  - {path}: {value}")
        else:
            print("No boolean values found")

        # Test 1: Standard json.dumps (should fail if booleans present)
        try:
            json_str = json.dumps(test_data)
            print("✅ Standard json.dumps: SUCCESS")
        except Exception as e:
            print(f"❌ Standard json.dumps: {e}")

        # Test 2: CustomJSONEncoder direct usage
        try:
            json_str = json.dumps(test_data, cls=CustomJSONEncoder)
            print("✅ CustomJSONEncoder: SUCCESS")
        except Exception as e:
            print(f"❌ CustomJSONEncoder: {e}")

        # Test 3: Pre-conversion + standard json.dumps
        try:
            safe_data = encoder._convert_booleans(test_data)
            json_str = json.dumps(safe_data)
            print("✅ Pre-conversion + json.dumps: SUCCESS")

            # Verify no booleans remain
            remaining_booleans = find_booleans(safe_data, f"safe_test_{i+1}")
            if remaining_booleans:
                print(
                    f"⚠️  {len(remaining_booleans)} booleans still remain after conversion!"
                )
                for path, value in remaining_booleans[:5]:
                    print(f"  - {path}: {value} ({type(value)})")
            else:
                print("✅ All booleans converted successfully")

        except Exception as e:
            print(f"❌ Pre-conversion + json.dumps: {e}")


def test_problematic_types():
    """Test types that might cause issues"""
    print("\n🔍 Testing potentially problematic data types:")

    from datetime import date, datetime

    import numpy as np

    # Test numpy booleans (common source of JSON issues)
    problematic_data = {
        "numpy_bool_true": np.bool_(True),
        "numpy_bool_false": np.bool_(False),
        "numpy_array": np.array([True, False]),
        "datetime_now": datetime.now(),
        "date_today": date.today(),
        "regular_bool": True,
        "mixed_list": [True, np.bool_(False), "string", 123],
    }

    encoder = CustomJSONEncoder()

    print("Original types:")
    for key, value in problematic_data.items():
        print(f"  - {key}: {type(value)} = {value}")

    # Test conversion
    try:
        safe_data = encoder._convert_booleans(problematic_data)
        print("\nAfter conversion:")
        for key, value in safe_data.items():
            print(f"  - {key}: {type(value)} = {value}")

        # Test JSON serialization
        json_str = json.dumps(safe_data, cls=CustomJSONEncoder)
        print("✅ JSON serialization successful!")

    except Exception as e:
        print(f"❌ Conversion/serialization failed: {e}")

        # Test each item individually
        for key, value in problematic_data.items():
            try:
                safe_value = encoder._convert_booleans(value)
                json.dumps({key: safe_value}, cls=CustomJSONEncoder)
                print(f"✅ {key}: OK")
            except Exception as item_error:
                print(f"❌ {key}: {item_error}")


if __name__ == "__main__":
    print("🧪 Testing JSON Boolean Serialization")
    print("=" * 50)

    test_boolean_conversion()

    try:
        test_problematic_types()
    except ImportError as e:
        print(f"Skipping numpy tests: {e}")

    print("\n" + "=" * 50)
    print("✅ Boolean conversion test completed")
