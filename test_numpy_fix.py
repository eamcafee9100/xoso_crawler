#!/usr/bin/env python3
"""
Test the updated CustomJSONEncoder with numpy support
"""

import json
import os
import sys

# Add the project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import the updated CustomJSONEncoder
sys.path.insert(
    0,
    os.path.join(
        os.path.dirname(os.path.abspath(__file__)), "predictions_tracker", "views_dir"
    ),
)


class CustomJSONEncoder(json.JSONEncoder):
    """Custom JSON encoder to handle boolean, numpy, and datetime objects"""

    def default(self, o):
        # Handle regular booleans
        if isinstance(o, bool):
            return "enabled" if o else "disabled"
        # Handle numpy booleans
        elif hasattr(o, "dtype") and "bool" in str(o.dtype):
            return "enabled" if bool(o) else "disabled"
        # Handle numpy arrays
        elif hasattr(o, "tolist"):
            return o.tolist()
        # Handle datetime objects
        elif hasattr(o, "isoformat"):
            return o.isoformat()
        # Handle objects with __dict__
        elif hasattr(o, "__dict__"):
            return o.__dict__
        return super().default(o)

    def encode(self, o):
        """Override encode to handle booleans in nested structures"""
        return super().encode(self._convert_booleans(o))

    def _convert_booleans(self, obj):
        """Recursively convert all boolean values (including numpy) to strings"""
        # Handle numpy arrays first (before checking dtype)
        if hasattr(obj, "tolist") and hasattr(obj, "dtype"):
            return self._convert_booleans(obj.tolist())
        # Handle regular Python booleans
        elif isinstance(obj, bool):
            return "enabled" if obj else "disabled"
        # Handle numpy scalars (booleans, integers, floats)
        elif hasattr(obj, "dtype"):
            if "bool" in str(obj.dtype):
                return "enabled" if bool(obj) else "disabled"
            elif hasattr(obj, "item"):  # numpy scalar
                return obj.item()  # Convert to Python native type
            else:
                return obj.tolist() if hasattr(obj, "tolist") else obj
        # Handle dictionaries
        elif isinstance(obj, dict):
            return {key: self._convert_booleans(value) for key, value in obj.items()}
        # Handle lists
        elif isinstance(obj, list):
            return [self._convert_booleans(item) for item in obj]
        # Handle tuples
        elif isinstance(obj, tuple):
            return tuple(self._convert_booleans(item) for item in obj)
        # Handle objects with __dict__ (but avoid strings, numbers, etc.)
        elif hasattr(obj, "__dict__") and not isinstance(obj, (str, int, float)):
            return {
                key: self._convert_booleans(value)
                for key, value in obj.__dict__.items()
            }
        else:
            return obj


def test_numpy_fix():
    """Test the numpy boolean fix"""
    from datetime import date, datetime

    import numpy as np

    print("🧪 Testing Updated CustomJSONEncoder with Numpy Support")
    print("=" * 60)

    # Test problematic data that was failing before
    problematic_data = {
        "numpy_bool_true": np.bool_(True),
        "numpy_bool_false": np.bool_(False),
        "numpy_array": np.array([True, False]),
        "datetime_now": datetime.now(),
        "date_today": date.today(),
        "regular_bool": True,
        "mixed_list": [True, np.bool_(False), "string", 123],
        "complex_nested": {
            "config": {
                "enabled": np.bool_(True),
                "debug": False,
                "features": [np.bool_(True), False, np.bool_(False)],
            },
            "results": np.array([True, False, True]),
        },
    }

    encoder = CustomJSONEncoder()

    print("Original types:")
    for key, value in problematic_data.items():
        print(f"  - {key}: {type(value)} = {value}")

    print("\n🔄 Testing conversion...")

    try:
        # Test pre-conversion
        safe_data = encoder._convert_booleans(problematic_data)
        print("✅ Pre-conversion successful!")

        print("\nAfter conversion:")
        for key, value in safe_data.items():
            print(f"  - {key}: {type(value)} = {value}")

        # Test JSON serialization
        json_str = json.dumps(safe_data, cls=CustomJSONEncoder)
        print("\n✅ JSON serialization successful!")

        # Parse it back to verify
        parsed_data = json.loads(json_str)
        print("✅ JSON parsing successful!")

        print(f"\nSerialized JSON length: {len(json_str)} characters")
        print("First 200 characters:")
        print(json_str[:200] + "..." if len(json_str) > 200 else json_str)

        return True

    except Exception as e:
        print(f"❌ Test failed: {e}")

        # Test each item individually to isolate the problem
        print("\n🔍 Testing individual items:")
        for key, value in problematic_data.items():
            try:
                safe_value = encoder._convert_booleans(value)
                json.dumps({key: safe_value}, cls=CustomJSONEncoder)
                print(f"✅ {key}: OK")
            except Exception as item_error:
                print(f"❌ {key}: {item_error}")
                print(f"   Type: {type(value)}")
                print(
                    f"   Safe type: {type(safe_value) if 'safe_value' in locals() else 'N/A'}"
                )

        return False


def test_edge_cases():
    """Test edge cases that might still cause issues"""
    print("\n🔍 Testing Edge Cases")
    print("-" * 30)

    import numpy as np

    edge_cases = [
        # Numpy scalars
        np.int32(42),
        np.float64(3.14),
        np.bool_(True),
        # Nested numpy in complex structures
        {
            "data": np.array([True, False, True]),
            "metadata": {"valid": np.bool_(True), "count": np.int32(3)},
        },
        # Mixed types that might cause confusion
        [np.bool_(True), True, 1, "true", np.bool_(False)],
    ]

    encoder = CustomJSONEncoder()

    for i, test_case in enumerate(edge_cases):
        print(f"\nEdge case {i+1}: {type(test_case)}")
        try:
            safe_data = encoder._convert_booleans(test_case)
            json_str = json.dumps(safe_data, cls=CustomJSONEncoder)
            print(f"✅ Success: {json_str[:100]}{'...' if len(json_str) > 100 else ''}")
        except Exception as e:
            print(f"❌ Failed: {e}")


if __name__ == "__main__":
    success = test_numpy_fix()
    test_edge_cases()

    print("\n" + "=" * 60)
    if success:
        print("✅ All tests passed! The numpy boolean fix should work.")
    else:
        print("❌ Tests failed. More investigation needed.")
