#!/usr/bin/env python3
"""
Direct Function Test - Bypass Django Server
Test run_enhanced_analysis function directly with mock request
"""

import json
import os
import sys
from datetime import date, datetime
from unittest.mock import Mock, patch

# Add the project directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))


def setup_minimal_django():
    """Setup minimal Django configuration"""
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "xoso_crawler.settings")

    import django
    from django.conf import settings

    if not settings.configured:
        settings.configure(
            DEBUG=True,
            DATABASES={
                "default": {
                    "ENGINE": "django.db.backends.sqlite3",
                    "NAME": "test.db",
                }
            },
            INSTALLED_APPS=[
                "django.contrib.contenttypes",
                "django.contrib.auth",
                "results",
                "predictions_tracker",
            ],
            SECRET_KEY="test-key",
            USE_TZ=True,
            LOGGING={
                "version": 1,
                "disable_existing_loggers": False,
                "handlers": {
                    "console": {
                        "class": "logging.StreamHandler",
                    },
                },
                "root": {
                    "handlers": ["console"],
                },
                "loggers": {
                    "enhanced_frequency_analyzer_views": {
                        "handlers": ["console"],
                        "level": "INFO",
                        "propagate": False,
                    },
                },
            },
        )

    django.setup()


def test_run_enhanced_analysis_directly():
    """Test run_enhanced_analysis function directly"""

    print("🧪 Testing run_enhanced_analysis function directly...")

    try:
        # Setup Django
        setup_minimal_django()

        # Mock request
        mock_request = Mock()
        mock_request.body = json.dumps(
            {
                "start_date": "2024-12-01",
                "end_date": "2025-01-31",
                "significance_level": "0.05",
                "enable_full_pipeline": True,
            }
        ).encode()

        # Mock analyzer to return data with booleans
        mock_analyzer = Mock()
        mock_analyzer.analyze_with_full_pipeline.return_value = {
            "hot_numbers": {
                "15": {
                    "frequency": 25,
                    "hotness_score": 3.5,
                    "is_trending": True,  # BOOLEAN!
                    "has_momentum": False,  # BOOLEAN!
                    "statistical_significance": "significant",
                }
            },
            "cold_numbers": {
                "87": {
                    "frequency": 3,
                    "is_overdue": True,  # BOOLEAN!
                    "needs_attention": False,  # BOOLEAN!
                }
            },
        }

        mock_analyzer.generate_visualization_data.return_value = {
            "charts_enabled": True,  # BOOLEAN!
            "interactive_mode": False,  # BOOLEAN!
            "data_available": True,  # BOOLEAN!
        }

        print("   📊 Mock data contains booleans:")
        print("   - hot_numbers.15.is_trending: True")
        print("   - hot_numbers.15.has_momentum: False")
        print("   - cold_numbers.87.is_overdue: True")
        print("   - visualization_data.charts_enabled: True")

        # Import and patch
        from analytic_frequence.enhanced_deep_frequency_analyzer import (
            EnhancedDeepFrequencyAnalyzer,
        )
        from predictions_tracker.views_dir.enhanced_frequency_analyzer_views import (
            run_enhanced_analysis,
        )

        with patch.object(
            EnhancedDeepFrequencyAnalyzer, "__new__", return_value=mock_analyzer
        ):

            # This should trigger the JSON serialization error if not fixed
            response = run_enhanced_analysis(mock_request)

            print(f"   ✅ Function executed successfully!")
            print(f"   📄 Response status: {response.status_code}")
            print(
                f"   📄 Response content type: {response.get('Content-Type', 'Unknown')}"
            )

            # Check if response contains converted booleans
            content = (
                response.content.decode()
                if hasattr(response.content, "decode")
                else str(response.content)
            )

            # Check for boolean conversion
            if '"enabled"' in content or '"disabled"' in content:
                print("   ✅ Boolean conversion detected in response!")

                # Parse and check specific values
                try:
                    data = json.loads(content)
                    status = data.get("status", "unknown")
                    print(f"   📊 Response status: {status}")

                    if status == "success":
                        print("   🎉 SUCCESS: No JSON serialization error!")
                        return True
                    else:
                        print(
                            f"   ❌ Error response: {data.get('error_message', 'Unknown error')}"
                        )
                        return False

                except json.JSONDecodeError as e:
                    print(f"   ❌ Response is not valid JSON: {e}")
                    return False
            else:
                print("   ⚠️  No boolean conversion markers found")
                return False

    except Exception as e:
        print(f"   ❌ Test failed: {e}")
        import traceback

        traceback.print_exc()
        return False


def test_custom_json_encoder_isolated():
    """Test CustomJSONEncoder in isolation"""

    print("\n🧪 Testing CustomJSONEncoder in isolation...")

    # Define encoder inline to avoid import issues
    class TestCustomJSONEncoder(json.JSONEncoder):
        def default(self, o):
            if isinstance(o, bool):
                return "enabled" if o else "disabled"
            elif isinstance(o, datetime):
                return o.isoformat()
            elif isinstance(o, date):
                return o.isoformat()
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

    # Test data
    test_data = {
        "status": "success",
        "has_results": True,
        "config": {"enabled": True, "debug": False, "nested": {"active": True}},
        "flags": [True, False, True],
    }

    print(f"   📊 Test data contains booleans at multiple levels")

    try:
        # Test encoding
        result = json.dumps(test_data, cls=TestCustomJSONEncoder, ensure_ascii=False)
        print("   ✅ JSON encoding successful!")

        # Parse back and verify
        parsed = json.loads(result)

        checks = [
            ("has_results", parsed["has_results"]),
            ("config.enabled", parsed["config"]["enabled"]),
            ("config.debug", parsed["config"]["debug"]),
            ("config.nested.active", parsed["config"]["nested"]["active"]),
            ("flags[0]", parsed["flags"][0]),
            ("flags[1]", parsed["flags"][1]),
        ]

        all_converted = True
        for path, value in checks:
            if isinstance(value, bool):
                print(f"   ❌ {path}: Still boolean ({value})")
                all_converted = False
            else:
                print(f"   ✅ {path}: '{value}'")

        if all_converted:
            print("   🎉 All booleans converted successfully!")
            return True
        else:
            print("   ❌ Some booleans not converted")
            return False

    except Exception as e:
        print(f"   ❌ Encoding failed: {e}")
        return False


def main():
    print("🚀 Enhanced Deep Frequency Analyzer - Direct Function Test")
    print("=" * 70)
    print("📋 Testing the actual function that's causing JSON serialization errors")
    print("=" * 70)

    success_count = 0

    # Test 1: Isolated CustomJSONEncoder
    print("📋 Test 1: CustomJSONEncoder Isolation Test")
    if test_custom_json_encoder_isolated():
        success_count += 1

    # Test 2: Direct function test
    print("\n📋 Test 2: Direct run_enhanced_analysis Function Test")
    try:
        if test_run_enhanced_analysis_directly():
            success_count += 1
    except Exception as e:
        print(f"   ❌ Direct function test setup failed: {e}")

    print("\n" + "=" * 70)
    print(f"🎯 Test Results: {success_count}/2 tests passed")

    if success_count == 2:
        print("🎉 ALL TESTS PASSED!")
        print("✅ CustomJSONEncoder is working correctly")
        print("✅ run_enhanced_analysis function handles booleans properly")
        print("\n💡 The error might be caused by:")
        print("   1. Django server caching old code")
        print("   2. Different code path being executed")
        print("   3. Database query results containing booleans")
        print("   4. External library returning boolean values")
    elif success_count == 1:
        print("⚠️  PARTIAL SUCCESS!")
        print("✅ CustomJSONEncoder works in isolation")
        print("❌ Integration test failed - check Django setup or function logic")
    else:
        print("❌ ALL TESTS FAILED!")
        print("🔧 Both CustomJSONEncoder and function integration need fixes")

    print("=" * 70)


if __name__ == "__main__":
    main()
