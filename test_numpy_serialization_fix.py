#!/usr/bin/env python3
"""
Test numpy serialization fix
"""
import json

import numpy as np


# Test CustomJSONEncoder
class CustomJSONEncoder(json.JSONEncoder):
    """Custom JSON encoder to handle boolean, numpy, and datetime objects"""

    def default(self, o):
        import numpy as np

        # Handle numpy arrays first (before other checks)
        if hasattr(o, "tolist") and hasattr(o, "dtype"):
            return o.tolist()
        # Handle numpy scalars specifically
        elif isinstance(o, (np.integer, np.floating, np.complexfloating)):
            return o.item()  # Convert to Python native type
        elif isinstance(o, np.ndarray):
            return o.tolist()
        elif isinstance(o, np.bool_):
            return "enabled" if bool(o) else "disabled"
        # Handle regular booleans
        elif isinstance(o, bool):
            return "enabled" if o else "disabled"
        # Handle numpy scalars by dtype check (fallback)
        elif hasattr(o, "dtype"):
            if "bool" in str(o.dtype):
                return "enabled" if bool(o) else "disabled"
            elif "int" in str(o.dtype) or "float" in str(o.dtype):
                return o.item() if hasattr(o, "item") else float(o)
        return super().default(o)

    def encode(self, o):
        """Override encode to handle booleans in nested structures"""
        return super().encode(self._convert_booleans(o))

    def _convert_booleans(self, obj):
        """Recursively convert all boolean values (including numpy) to strings"""
        import numpy as np

        # Handle numpy arrays first (before checking dtype)
        if hasattr(obj, "tolist") and hasattr(obj, "dtype"):
            return self._convert_booleans(obj.tolist())
        # Handle numpy scalars specifically
        elif isinstance(obj, (np.integer, np.floating, np.complexfloating)):
            return obj.item()  # Convert to Python native type
        elif isinstance(obj, np.ndarray):
            return self._convert_booleans(obj.tolist())
        elif isinstance(obj, np.bool_):
            return "enabled" if bool(obj) else "disabled"
        # Handle regular Python booleans
        elif isinstance(obj, bool):
            return "enabled" if obj else "disabled"
        # Handle numpy scalars by dtype check (fallback)
        elif hasattr(obj, "dtype"):
            if "bool" in str(obj.dtype):
                return "enabled" if bool(obj) else "disabled"
            elif "int" in str(obj.dtype) or "float" in str(obj.dtype):
                return obj.item() if hasattr(obj, "item") else float(obj)
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
        else:
            return obj


def test_numpy_serialization():
    """Test numpy serialization"""
    print("🧪 Testing numpy serialization fix...")

    # Create test data with numpy types
    test_data = {
        "weight": np.float64(0.2026),
        "correlation": np.float64(-0.2026),
        "bool_value": np.bool_(True),
        "int_value": np.int64(42),
        "array": np.array([1.1, 2.2, 3.3]),
        "nested": {"inner_float": np.float64(3.14), "inner_bool": np.bool_(False)},
    }

    try:
        # Test serialization
        json_str = json.dumps(test_data, cls=CustomJSONEncoder)
        print("✅ JSON serialization successful")
        print(f"Result: {json_str}")

        # Test if it can be parsed back
        parsed = json.loads(json_str)
        print("✅ JSON parsing successful")

        # Check for numpy patterns that would cause JS errors
        if "np." in json_str or "numpy." in json_str:
            print("❌ Still contains numpy patterns!")
            return False
        else:
            print("✅ No numpy patterns found in output")
            return True

    except Exception as e:
        print(f"❌ Serialization failed: {e}")
        return False


if __name__ == "__main__":
    print("=" * 50)
    print("🔧 NUMPY SERIALIZATION FIX TEST")
    print("=" * 50)

    success = test_numpy_serialization()

    print("\n" + "=" * 50)
    if success:
        print("✅ NUMPY SERIALIZATION FIX SUCCESSFUL!")
    else:
        print("❌ NUMPY SERIALIZATION ISSUES REMAIN")
    print("=" * 50)
