#!/usr/bin/env python
"""
Direct test of run_enhanced_analysis function to identify JSON serialization issues
"""
import json
import os
import sys
from datetime import date, datetime

# Setup Django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "xoso_crawler.settings")
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import django

django.setup()

from django.conf import settings
from django.http import HttpRequest
from django.test import RequestFactory

# Ensure testserver is in ALLOWED_HOSTS for testing
if "testserver" not in settings.ALLOWED_HOSTS:
    settings.ALLOWED_HOSTS.append("testserver")


def test_run_enhanced_analysis_direct():
    """Test run_enhanced_analysis function directly"""
    print("🔍 Testing run_enhanced_analysis function directly...")

    try:
        # Import the function
        from predictions_tracker.views_dir.enhanced_frequency_analyzer_views import (
            run_enhanced_analysis,
        )

        print("✅ Successfully imported run_enhanced_analysis")

        # Create a mock request
        factory = RequestFactory()

        test_data = {
            "start_date": "2025-07-01",
            "end_date": "2025-08-01",
            "significance_level": "0.05",
            "enable_full_pipeline": True,
        }

        request = factory.post(
            "/enhanced-analyzer/run-analysis/",
            data=json.dumps(test_data),
            content_type="application/json",
        )

        print(f"📊 Test request data: {test_data}")
        print("🚀 Calling run_enhanced_analysis...")

        # Call the function
        response = run_enhanced_analysis(request)

        print(f"📱 Response status: {response.status_code}")
        print(f"📝 Response content type: {response.get('Content-Type', 'Unknown')}")

        if response.status_code == 200:
            try:
                # Try to parse response content
                response_content = response.content.decode("utf-8")
                print(f"✅ Response content length: {len(response_content)} characters")

                # Try to parse as JSON
                response_data = json.loads(response_content)
                print("✅ Response is valid JSON!")
                print(f"📋 Response keys: {list(response_data.keys())}")

                # Check for boolean values in response
                def find_booleans_in_response(
                    obj, path="", max_depth=10, current_depth=0
                ):
                    """Find boolean values in response with depth limit"""
                    if current_depth >= max_depth:
                        return []

                    booleans = []
                    if isinstance(obj, bool):
                        booleans.append((path if path else "root", obj, type(obj)))
                    elif isinstance(obj, dict):
                        for key, value in obj.items():
                            if (
                                current_depth < 3
                            ):  # Only print structure for first few levels
                                print(
                                    f"  {'  ' * current_depth}📁 {path}.{key if path else key}: {type(value).__name__}"
                                )
                            current_path = f"{path}.{key}" if path else key
                            booleans.extend(
                                find_booleans_in_response(
                                    value, current_path, max_depth, current_depth + 1
                                )
                            )
                    elif isinstance(obj, list):
                        if current_depth < 3:
                            print(
                                f"  {'  ' * current_depth}📋 {path}: list with {len(obj)} items"
                            )
                        for i, value in enumerate(obj):
                            current_path = f"{path}[{i}]" if path else f"[{i}]"
                            booleans.extend(
                                find_booleans_in_response(
                                    value, current_path, max_depth, current_depth + 1
                                )
                            )

                    return booleans

                print("\n🔍 Analyzing response structure...")
                booleans_found = find_booleans_in_response(response_data, "response")

                if booleans_found:
                    print(
                        f"\n⚠️  Found {len(booleans_found)} boolean values in response:"
                    )
                    for path, value, value_type in booleans_found[:10]:  # Show first 10
                        print(f"   {path}: {value} (type: {value_type})")
                    if len(booleans_found) > 10:
                        print(f"   ... and {len(booleans_found) - 10} more")
                    print("❌ These booleans should have been converted to strings!")
                else:
                    print("✅ No boolean values found in response!")
                    print("✅ CustomJSONEncoder working correctly!")

            except json.JSONDecodeError as e:
                print(f"❌ Response is not valid JSON: {e}")
                print(
                    f"📄 Raw response (first 500 chars): {response.content.decode('utf-8')[:500]}..."
                )

        else:
            print(f"❌ Request failed with status {response.status_code}")
            error_content = response.content.decode("utf-8")
            print(f"📄 Error response: {error_content[:500]}...")

    except ImportError as e:
        print(f"❌ Cannot import run_enhanced_analysis: {e}")

        # Check if the file exists
        views_path = os.path.join(
            os.path.dirname(__file__),
            "predictions_tracker",
            "views_dir",
            "enhanced_frequency_analyzer_views.py",
        )
        if os.path.exists(views_path):
            print(f"✅ Views file exists at: {views_path}")
        else:
            print(f"❌ Views file not found at: {views_path}")

    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        import traceback

        traceback.print_exc()


def test_custom_json_encoder_in_views():
    """Test the CustomJSONEncoder from views directly"""
    print("\n🔧 Testing CustomJSONEncoder from views...")

    try:
        from predictions_tracker.views_dir.enhanced_frequency_analyzer_views import (
            CustomJSONEncoder,
            safe_json_response,
        )

        print("✅ Successfully imported CustomJSONEncoder and safe_json_response")

        # Test data with booleans
        test_data = {
            "status": "success",
            "has_results": True,
            "analysis_complete": False,
            "nested": {
                "flag1": True,
                "flag2": False,
                "items": [True, False, "text", 123],
            },
        }

        print(f"📊 Test data: {test_data}")

        # Test CustomJSONEncoder directly
        encoder = CustomJSONEncoder()
        json_result = encoder.encode(test_data)

        print("✅ CustomJSONEncoder.encode() successful")
        print(f"📄 JSON result: {json_result}")

        # Parse back to check
        parsed = json.loads(json_result)

        def check_no_booleans(obj, path=""):
            """Check that no boolean values remain"""
            booleans = []
            if isinstance(obj, bool):
                booleans.append((path, obj))
            elif isinstance(obj, dict):
                for key, value in obj.items():
                    current_path = f"{path}.{key}" if path else key
                    booleans.extend(check_no_booleans(value, current_path))
            elif isinstance(obj, list):
                for i, value in enumerate(obj):
                    current_path = f"{path}[{i}]" if path else f"[{i}]"
                    booleans.extend(check_no_booleans(value, current_path))
            return booleans

        remaining_booleans = check_no_booleans(parsed)
        if remaining_booleans:
            print(f"❌ Still found booleans after encoding: {remaining_booleans}")
        else:
            print("✅ All booleans successfully converted!")

        # Test safe_json_response
        print("\n🔧 Testing safe_json_response...")
        response = safe_json_response(test_data)
        print(f"✅ safe_json_response successful, status: {response.status_code}")

        response_content = response.content.decode("utf-8")
        parsed_response = json.loads(response_content)
        response_booleans = check_no_booleans(parsed_response)

        if response_booleans:
            print(f"❌ safe_json_response still has booleans: {response_booleans}")
        else:
            print("✅ safe_json_response correctly converted all booleans!")

    except Exception as e:
        print(f"❌ CustomJSONEncoder test failed: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    print("🚀 Direct Analysis Function Test")
    print("=" * 60)

    # Test CustomJSONEncoder first
    test_custom_json_encoder_in_views()

    # Test the actual analysis function
    test_run_enhanced_analysis_direct()

    print("\n" + "=" * 60)
    print("🏁 Test completed!")
