#!/usr/bin/env python
"""
Test script to directly check Enhanced Analyzer endpoint for JSON serialization errors
"""
import json
import os
import sys
from datetime import datetime, timedelta

import django

# Add the project directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Set up Django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "xoso_crawler.settings")
django.setup()

from django.contrib.auth.models import User
from django.test import Client, RequestFactory
from django.urls import reverse

# from results.models import Result  # Comment out for now


def test_enhanced_analyzer_direct():
    """Test Enhanced Analyzer endpoint directly"""
    print("🔍 Testing Enhanced Analyzer Endpoint Direct Call...")

    # Create test client
    client = Client()

    # Create test data if needed
    try:
        # Get or create some recent results for testing
        from datetime import date

        today = date.today()

        # Test data
        test_data = {
            "analysis_type": "comprehensive",
            "period_days": 30,
            "numbers_to_analyze": [1, 2, 3, 4, 5],
            "confidence_threshold": 0.7,
        }

        print(f"📊 Test data: {test_data}")

        # Make POST request to enhanced analyzer
        url = "/pre-lokhung/enhanced-analyzer/run-analysis/"
        print(f"🌐 Calling endpoint: {url}")

        response = client.post(
            url,
            data=json.dumps(test_data),
            content_type="application/json",
            HTTP_X_REQUESTED_WITH="XMLHttpRequest",  # Make it AJAX
        )

        print(f"📱 Response status: {response.status_code}")
        print(f"📝 Response headers: {dict(response.items())}")

        if response.status_code == 200:
            try:
                response_data = response.json()
                print("✅ JSON Response parsed successfully!")
                print(f"📋 Response keys: {list(response_data.keys())}")

                # Check for boolean values in response
                def find_booleans(obj, path=""):
                    """Recursively find boolean values in response"""
                    booleans = []
                    if isinstance(obj, dict):
                        for key, value in obj.items():
                            current_path = f"{path}.{key}" if path else key
                            if isinstance(value, bool):
                                booleans.append((current_path, value))
                            elif isinstance(value, (dict, list)):
                                booleans.extend(find_booleans(value, current_path))
                    elif isinstance(obj, list):
                        for i, value in enumerate(obj):
                            current_path = f"{path}[{i}]"
                            if isinstance(value, bool):
                                booleans.append((current_path, value))
                            elif isinstance(value, (dict, list)):
                                booleans.extend(find_booleans(value, current_path))
                    return booleans

                booleans_found = find_booleans(response_data)
                if booleans_found:
                    print("⚠️  Boolean values found in response:")
                    for path, value in booleans_found:
                        print(f"   {path}: {value} (type: {type(value)})")
                else:
                    print("✅ No boolean values found in response!")

            except json.JSONDecodeError as e:
                print(f"❌ JSON parsing failed: {e}")
                print(f"📄 Raw response: {response.content.decode()[:500]}...")

        else:
            print(f"❌ Request failed with status {response.status_code}")
            print(f"📄 Response content: {response.content.decode()[:500]}...")

    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        import traceback

        traceback.print_exc()


def test_custom_json_encoder():
    """Test our CustomJSONEncoder directly"""
    print("\n🔧 Testing CustomJSONEncoder directly...")

    try:
        from lokhung.enhanced_frequency_analyzer_views import CustomJSONEncoder

        # Test data with various boolean scenarios
        test_cases = [
            # Simple boolean
            {"result": True},
            # Nested boolean in dict
            {"analysis": {"is_significant": True, "is_trending": False}},
            # Boolean in list
            {"flags": [True, False, True]},
            # Complex nested structure
            {
                "data": {
                    "patterns": [
                        {"active": True, "confidence": 0.85},
                        {"active": False, "confidence": 0.23},
                    ],
                    "summary": {
                        "has_results": True,
                        "is_complete": False,
                        "metrics": [True, False, True],
                    },
                }
            },
        ]

        encoder = CustomJSONEncoder()

        for i, test_case in enumerate(test_cases, 1):
            print(f"\n📋 Test case {i}: {test_case}")
            try:
                json_result = encoder.encode(test_case)
                print(f"✅ Encoded successfully: {json_result}")

                # Parse back to verify no booleans remain
                parsed = json.loads(json_result)

                def check_no_booleans(obj, path=""):
                    """Verify no boolean values remain"""
                    if isinstance(obj, dict):
                        for key, value in obj.items():
                            current_path = f"{path}.{key}" if path else key
                            if isinstance(value, bool):
                                print(f"❌ Boolean found at {current_path}: {value}")
                                return False
                            elif isinstance(value, (dict, list)):
                                if not check_no_booleans(value, current_path):
                                    return False
                    elif isinstance(obj, list):
                        for i, value in enumerate(obj):
                            current_path = f"{path}[{i}]"
                            if isinstance(value, bool):
                                print(f"❌ Boolean found at {current_path}: {value}")
                                return False
                            elif isinstance(value, (dict, list)):
                                if not check_no_booleans(value, current_path):
                                    return False
                    return True

                if check_no_booleans(parsed):
                    print("✅ No booleans found in parsed result!")

            except Exception as e:
                print(f"❌ Encoding failed: {e}")

    except ImportError as e:
        print(f"❌ Cannot import CustomJSONEncoder: {e}")


if __name__ == "__main__":
    print("🚀 Starting Enhanced Analyzer JSON Serialization Test")
    print("=" * 60)

    # Test custom encoder first
    test_custom_json_encoder()

    # Test actual endpoint
    test_enhanced_analyzer_direct()

    print("\n" + "=" * 60)
    print("🏁 Test completed!")
