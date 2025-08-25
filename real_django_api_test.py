#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
🔧 REAL API TEST SCRIPT
Test the actual Django API endpoint for loadMethodAnalysis
"""

import json
import sys
from datetime import datetime, timedelta

import requests

# Django server configuration
DJANGO_HOST = "http://127.0.0.1:8000"
API_ENDPOINT = "/pre-lokhung/api/method-analysis-v2/"


def test_api_endpoint():
    print("🔧 TESTING ACTUAL DJANGO API")
    print("=" * 60)

    # Test data
    test_date = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")

    # Construct URL
    api_url = f"{DJANGO_HOST}{API_ENDPOINT}?analysis_date={test_date}&limit=15"

    print(f"📅 Test Date: {test_date}")
    print(f"🔍 API URL: {api_url}")
    print("-" * 60)

    try:
        # Make request
        print("📡 Making request...")
        response = requests.get(api_url, timeout=30)

        print(f"📊 Response Status: {response.status_code}")
        print(f"📊 Response Headers: {dict(response.headers)}")

        # Check status code
        if response.status_code == 200:
            print("✅ Status: OK")

            # Check content type
            content_type = response.headers.get("content-type", "")
            if "application/json" in content_type:
                print("✅ Content-Type: JSON")

                try:
                    # Parse JSON
                    data = response.json()
                    print("✅ JSON Parse: Success")

                    # Analyze structure
                    print("\n📋 RESPONSE STRUCTURE ANALYSIS:")
                    print("-" * 40)

                    if isinstance(data, dict):
                        print("✅ Root Type: Dictionary")
                        print(f"📊 Keys: {list(data.keys())}")

                        # Check V2 expected structure
                        v2_keys = [
                            "hybrid_analysis",
                            "intelligent_selections",
                            "optimal_methods",
                            "performance_prediction",
                        ]
                        found_v2_keys = [key for key in v2_keys if key in data]

                        print(f"🔍 V2 Structure Keys Found: {found_v2_keys}")
                        print(
                            f"🔍 V2 Structure Keys Missing: {[key for key in v2_keys if key not in data]}"
                        )

                        # Check success field
                        if "success" in data:
                            print(f"✅ Success Field: {data['success']}")

                            if data["success"]:
                                print("\n🎯 DETAILED DATA ANALYSIS:")
                                print("-" * 40)

                                # Analyze each section
                                for key in data.keys():
                                    value = data[key]
                                    if isinstance(value, dict):
                                        print(
                                            f"📊 {key}: Dict with {len(value)} keys - {list(value.keys())}"
                                        )
                                    elif isinstance(value, list):
                                        print(f"📊 {key}: List with {len(value)} items")
                                    else:
                                        print(
                                            f"📊 {key}: {type(value).__name__} - {value}"
                                        )

                                # Save sample response
                                with open(
                                    "api_v2_response_sample.json", "w", encoding="utf-8"
                                ) as f:
                                    json.dump(data, f, indent=2, ensure_ascii=False)
                                print(
                                    f"\n💾 Sample response saved to: api_v2_response_sample.json"
                                )

                            else:
                                print(
                                    f"❌ API returned success=false: {data.get('error', 'Unknown error')}"
                                )
                        else:
                            print(
                                "⚠️ No 'success' field found - this might be an old API format"
                            )

                    else:
                        print(f"❌ Root Type: {type(data).__name__} (expected dict)")

                except json.JSONDecodeError as e:
                    print(f"❌ JSON Parse Error: {e}")
                    print(f"📝 Raw Response: {response.text[:500]}...")

            else:
                print(f"❌ Content-Type: {content_type} (expected application/json)")
                print(f"📝 Raw Response: {response.text[:500]}...")

        elif response.status_code == 404:
            print("❌ Status: 404 Not Found")
            print("🔍 Possible Issues:")
            print("   1. URL pattern not defined in urls.py")
            print("   2. View function doesn't exist")
            print("   3. App not included in main urls.py")

        elif response.status_code == 500:
            print("❌ Status: 500 Internal Server Error")
            print("🔍 Possible Issues:")
            print("   1. Code error in view function")
            print("   2. Database connection issue")
            print("   3. Missing dependencies")
            print(f"📝 Error Response: {response.text[:500]}...")

        else:
            print(f"❌ Status: {response.status_code}")
            print(f"📝 Response: {response.text[:500]}...")

    except requests.exceptions.ConnectionError:
        print("❌ Connection Error: Django server not running")
        print("🔍 Solutions:")
        print("   1. Start Django server: python manage.py runserver")
        print("   2. Check if server is running on port 8000")

    except requests.exceptions.Timeout:
        print("❌ Timeout Error: Request took too long")

    except Exception as e:
        print(f"❌ Unexpected Error: {e}")


def test_multiple_dates():
    print("\n🔄 TESTING MULTIPLE DATES")
    print("=" * 60)

    # Test last 5 days
    for i in range(5):
        test_date = (datetime.now() - timedelta(days=i + 1)).strftime("%Y-%m-%d")
        api_url = f"{DJANGO_HOST}{API_ENDPOINT}?analysis_date={test_date}&limit=5"

        print(f"\n📅 Testing Date: {test_date}")

        try:
            response = requests.get(api_url, timeout=10)
            print(f"   📊 Status: {response.status_code}")

            if response.status_code == 200:
                data = response.json()
                if data.get("success"):
                    print(f"   ✅ Success: Data available")

                    # Quick structure check
                    v2_keys = [
                        "hybrid_analysis",
                        "intelligent_selections",
                        "optimal_methods",
                        "performance_prediction",
                    ]
                    found_keys = sum(1 for key in v2_keys if key in data)
                    print(f"   📊 V2 Keys: {found_keys}/4 found")
                else:
                    print(
                        f"   ❌ Success: False - {data.get('error', 'Unknown error')}"
                    )
            else:
                print(f"   ❌ HTTP Error: {response.status_code}")

        except Exception as e:
            print(f"   ❌ Error: {e}")


if __name__ == "__main__":
    print("🚀 DJANGO API V2 REAL TEST")
    print("=" * 60)
    print(f"📅 Test Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"🌐 Django Host: {DJANGO_HOST}")
    print(f"🔗 API Endpoint: {API_ENDPOINT}")
    print("=" * 60)

    # Test main endpoint
    test_api_endpoint()

    # Test multiple dates
    test_multiple_dates()

    print("\n" + "=" * 60)
    print("✅ REAL API TEST COMPLETE")
    print("📋 Check the results above to identify any issues")
    print("💡 If errors found, check Django server console for details")
