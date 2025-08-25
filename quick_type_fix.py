"""
Quick fix for insights type conversion error
"""

import os
import sys

import django

# Django setup
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "xoso_crawler.settings")
sys.path.append(".")
django.setup()


def debug_and_fix():
    """Find and fix the insights type issue"""
    print("=== QUICK TYPE FIX ===")

    # Test problematic values
    test_values = [
        {"entropy": 0.5},
        {"entanglement_score": 0.8},
        {"pattern_strength": {"some": "dict"}},  # This could be the issue
        {"consensus_confidence": [0.1, 0.2, 0.3]},  # This too
        {"consciousness_level": {"nested": {"value": 0.5}}},
    ]

    for i, test_val in enumerate(test_values):
        print(f"\nTest {i+1}: {test_val}")

        for key, value in test_val.items():
            try:
                result = float(value)
                print(f"  {key}: {value} -> {result} ✅")
            except (TypeError, ValueError) as e:
                print(f"  {key}: {value} -> ERROR: {e} ❌")

                # Try to extract float from complex types
                if isinstance(value, dict):
                    # Try to find first numeric value in dict
                    for k, v in value.items():
                        try:
                            result = float(v)
                            print(f"    Extracted from dict[{k}]: {result} ✅")
                            break
                        except:
                            continue
                    else:
                        print(f"    Default fallback: 0.5 ⚠️")

                elif isinstance(value, (list, tuple)):
                    # Try to use first element or mean
                    try:
                        if value:
                            result = float(value[0])
                            print(f"    Extracted from list[0]: {result} ✅")
                        else:
                            print(f"    Empty list, fallback: 0.5 ⚠️")
                    except:
                        print(f"    List conversion failed, fallback: 0.5 ⚠️")


if __name__ == "__main__":
    debug_and_fix()
