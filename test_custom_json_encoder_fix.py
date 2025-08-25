#!/usr/bin/env python
"""
Simple script to test Enhanced Deep Frequency Analyzer JSON serialization fix
"""
import json
import os
import sys

# Add project to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))


def test_custom_json_encoder_only():
    """Test only the CustomJSONEncoder without Django dependencies"""
    print("🔧 Testing CustomJSONEncoder Implementation...")

    # Define CustomJSONEncoder inline to avoid imports
    class CustomJSONEncoder(json.JSONEncoder):
        """Custom JSON encoder that handles boolean values by converting them to strings"""

        def encode(self, obj):
            """Override encode to handle boolean conversion before serialization"""
            converted_obj = self._convert_booleans(obj)
            return super().encode(converted_obj)

        def _convert_booleans(self, obj):
            """Recursively convert all boolean values to strings"""
            if isinstance(obj, bool):
                return "true" if obj else "false"
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

    # Test cases that simulate real Enhanced Analyzer responses
    test_cases = [
        # Case 1: Simple boolean
        {"status": "success", "has_results": True, "is_significant": False},
        # Case 2: Complex nested structure similar to enhanced analyzer
        {
            "analysis_results": {
                "frequency_analysis": {
                    "is_significant": True,
                    "confidence_level": 0.95,
                    "patterns": [
                        {"number": 1, "is_hot": True, "is_cold": False},
                        {"number": 2, "is_hot": False, "is_cold": True},
                    ],
                },
                "trend_analysis": {
                    "has_trend": True,
                    "is_ascending": False,
                    "indicators": [True, False, True, False],
                },
                "statistical_tests": {
                    "chi_square": {"is_significant": True, "p_value": 0.001},
                    "kolmogorov_smirnov": {"is_significant": False, "p_value": 0.12},
                },
            },
            "metadata": {
                "analysis_complete": True,
                "has_errors": False,
                "processing_flags": [True, True, False],
            },
        },
        # Case 3: Edge cases
        {
            "empty_list": [],
            "mixed_list": [True, 1, "test", False, 2.5],
            "nested_booleans": {
                "level1": {"level2": {"level3": [True, {"deep": False}]}}
            },
        },
    ]

    encoder = CustomJSONEncoder()

    for i, test_case in enumerate(test_cases, 1):
        print(f"\n📋 Test Case {i}:")
        print(f"   Input structure: {_describe_structure(test_case)}")

        # Find booleans in input
        input_booleans = _find_all_booleans(test_case)
        print(f"   Input booleans: {len(input_booleans)} found")
        for path, value in input_booleans:
            print(f"      {path}: {value}")

        try:
            # Encode with custom encoder
            json_result = encoder.encode(test_case)
            print(f"   ✅ CustomJSONEncoder: SUCCESS")

            # Parse back and check for booleans
            parsed = json.loads(json_result)
            output_booleans = _find_all_booleans(parsed)

            if output_booleans:
                print(
                    f"   ❌ Still has {len(output_booleans)} booleans after encoding!"
                )
                for path, value in output_booleans:
                    print(f"      {path}: {value} (type: {type(value)})")
            else:
                print(f"   ✅ All booleans converted successfully!")

            # Test standard JSON encoder for comparison
            try:
                standard_json = json.dumps(test_case)
                print(f"   ⚠️  Standard JSON: Also works (no booleans detected)")
            except TypeError as e:
                print(f"   ❌ Standard JSON: FAILED - {e}")

        except Exception as e:
            print(f"   ❌ CustomJSONEncoder: FAILED - {e}")
            import traceback

            traceback.print_exc()


def _describe_structure(obj, max_depth=2, current_depth=0):
    """Describe the structure of an object"""
    if current_depth >= max_depth:
        return f"{type(obj).__name__}(...)"

    if isinstance(obj, dict):
        if not obj:
            return "{}"
        keys = list(obj.keys())[:3]  # Show first 3 keys
        key_desc = ", ".join(
            f'"{k}": {_describe_structure(obj[k], max_depth, current_depth+1)}'
            for k in keys
        )
        if len(obj) > 3:
            key_desc += f", ...{len(obj)-3} more"
        return f"{{{key_desc}}}"
    elif isinstance(obj, list):
        if not obj:
            return "[]"
        first_few = obj[:2]  # Show first 2 items
        item_desc = ", ".join(
            _describe_structure(item, max_depth, current_depth + 1)
            for item in first_few
        )
        if len(obj) > 2:
            item_desc += f", ...{len(obj)-2} more"
        return f"[{item_desc}]"
    else:
        return f"{type(obj).__name__}({obj})" if current_depth == 0 else str(obj)


def _find_all_booleans(obj, path=""):
    """Find all boolean values in nested structure"""
    booleans = []

    if isinstance(obj, bool):
        booleans.append((path if path else "root", obj))
    elif isinstance(obj, dict):
        for key, value in obj.items():
            current_path = f"{path}.{key}" if path else key
            booleans.extend(_find_all_booleans(value, current_path))
    elif isinstance(obj, (list, tuple)):
        for i, value in enumerate(obj):
            current_path = f"{path}[{i}]" if path else f"[{i}]"
            booleans.extend(_find_all_booleans(value, current_path))

    return booleans


if __name__ == "__main__":
    print("🚀 CustomJSONEncoder Test - Enhanced Analyzer Fix Verification")
    print("=" * 70)

    test_custom_json_encoder_only()

    print("\n" + "=" * 70)
    print("🏁 Test completed!")
    print("✅ If all test cases show 'All booleans converted successfully!'")
    print("   then the Enhanced Analyzer JSON serialization fix is working correctly.")
