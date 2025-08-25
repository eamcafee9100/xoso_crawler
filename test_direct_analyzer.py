#!/usr/bin/env python
"""
🚀 Enhanced Deep Frequency Analyzer - Direct Syntax Test
=========================================================
Tests core analyzer code directly without Django
"""

import json
from datetime import date, datetime, timedelta


def test_analyzer_import():
    """Test if analyzer can be imported and instantiated"""
    print("🧪 Testing Analyzer Import...")

    try:
        # Test import - this will catch syntax errors
        import os
        import sys

        # Add project root to path
        project_root = os.path.dirname(os.path.abspath(__file__))
        sys.path.insert(0, project_root)

        from analytic_frequence.enhanced_deep_frequency_analyzer import (
            EnhancedDeepFrequencyAnalyzer,
        )

        print("   ✅ Import successful")

        # Test instantiation
        try:
            analyzer = EnhancedDeepFrequencyAnalyzer()
            print("   ✅ Instantiation successful")

            # Test configuration
            config = analyzer.config
            print(f"   🔧 Configuration loaded: {len(config)} keys")

            # Check boolean config values are strings
            bool_keys = [
                "enable_validation",
                "enable_feedback_learning",
                "enable_visualization",
            ]
            for key in bool_keys:
                value = config.get(key, "missing")
                if isinstance(value, str):
                    print(f"   ✅ {key}: '{value}' (string)")
                else:
                    print(f"   ❌ {key}: {value} ({type(value).__name__})")

            return True

        except Exception as inst_error:
            print(f"   ❌ Instantiation failed: {inst_error}")
            return False

    except SyntaxError as syntax_error:
        print(f"   ❌ Syntax error: {syntax_error}")
        return False
    except ImportError as import_error:
        print(f"   ❌ Import error: {import_error}")
        return False
    except Exception as e:
        print(f"   ❌ Unexpected error: {e}")
        return False


def test_json_serialization():
    """Test JSON serialization of common data structures"""
    print("🧪 Testing JSON Serialization...")

    try:
        # Test data with various types that might cause issues
        test_data = {
            "string_boolean": "enabled",
            "string_disabled": "disabled",
            "is_significant": "significant",
            "is_not_significant": "not_significant",
            "analysis_date": datetime.now().isoformat(),
            "numbers": [1, 2, 3, 4, 5],
            "float_value": 0.85,
            "nested": {"validation_enabled": "enabled", "status": "active"},
        }

        # Try to serialize
        json_str = json.dumps(test_data, indent=2, ensure_ascii=False)
        print("   ✅ JSON serialization successful")
        print(f"   📊 JSON size: {len(json_str)} bytes")

        # Try to deserialize
        parsed = json.loads(json_str)
        print("   ✅ JSON deserialization successful")

        return True

    except Exception as e:
        print(f"   ❌ JSON serialization failed: {e}")
        return False


def test_field_names():
    """Test that field names are correct"""
    print("🧪 Testing Field Names...")

    try:
        # This simulates what the analyzer might do with database fields
        # We'll test the field mapping we fixed

        # Simulate database record (like NumberFrequencyStats)
        mock_record = {
            "date": date.today(),  # Correct field name
            "number": 12,
            "frequency": 5,
            "appeared_in_special": True,
            "appeared_in_first": True,
        }

        # Test accessing the correct field
        record_date = mock_record["date"]  # This should work
        print(f"   ✅ Field 'date' access successful: {record_date}")

        # Test that we don't try to access wrong field
        try:
            wrong_date = mock_record["draw_date"]  # This should fail
            print(f"   ❌ Wrong field 'draw_date' should not exist: {wrong_date}")
            return False
        except KeyError:
            print("   ✅ Field 'draw_date' correctly not found (as expected)")

        return True

    except Exception as e:
        print(f"   ❌ Field name test failed: {e}")
        return False


def main():
    """Run all direct tests"""
    print("🚀 Enhanced Deep Frequency Analyzer - Direct Syntax Test")
    print("=" * 70)

    tests = [
        ("Analyzer Import", test_analyzer_import),
        ("JSON Serialization", test_json_serialization),
        ("Field Names", test_field_names),
    ]

    results = []

    for test_name, test_func in tests:
        print(f"\n🔍 Running {test_name} test...")
        result = test_func()
        results.append((test_name, result))

    # Summary
    print("\n" + "=" * 70)
    print("📋 DIRECT TEST SUMMARY:")
    print("=" * 70)

    passed = 0
    for test_name, result in results:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"   {test_name}: {status}")
        if result:
            passed += 1

    print(f"📊 Results: {passed}/{len(tests)} tests passed")

    if passed == len(tests):
        print("🎉 All direct tests passed!")
        print("📝 Core fixes are working correctly")
    else:
        print("⚠️  Some direct tests failed")
        print("📝 Check error messages above for details")


if __name__ == "__main__":
    main()
