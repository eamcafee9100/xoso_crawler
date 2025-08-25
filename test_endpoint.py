#!/usr/bin/env python3
"""
Test the Enhanced Analyzer endpoint to verify JSON serialization fix
"""
import json
from datetime import datetime

import requests


def test_enhanced_analyzer_endpoint():
    """Test the actual Enhanced Analyzer endpoint"""
    url = "http://127.0.0.1:8000/pre-lokhung/enhanced-analyzer/run-analysis/"

    print("🧪 Testing Enhanced Analyzer endpoint...")
    print(f"URL: {url}")

    try:
        # Make request to Enhanced Analyzer with proper parameters
        data = {
            "start_date": "2025-01-01",
            "end_date": "2025-01-15",
            "analysis_type": "full",
        }
        response = requests.post(url, json=data, timeout=30)

        print(f"Status Code: {response.status_code}")
        print(f"Content-Type: {response.headers.get('content-type')}")

        if response.status_code == 200:
            try:
                # Try to parse JSON
                data = response.json()
                print("✅ JSON parsing successful!")
                print(f"Response keys: {list(data.keys())}")

                # Check for common numpy boolean patterns
                json_str = response.text
                has_numpy_bools = any(
                    pattern in json_str
                    for pattern in ["numpy.bool_", "bool_", "numpy.array"]
                )

                if has_numpy_bools:
                    print("⚠️  Warning: Response contains numpy type strings")
                else:
                    print("✅ No numpy type issues detected")

                print(f"Response size: {len(json_str)} characters")
                return True

            except json.JSONDecodeError as e:
                print(f"❌ JSON parsing failed: {e}")
                print(f"Raw response (first 500 chars): {response.text[:500]}")
                return False

        else:
            print(f"❌ HTTP Error {response.status_code}")
            print(f"Response: {response.text[:500]}")
            return False

    except requests.exceptions.RequestException as e:
        print(f"❌ Request failed: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False


if __name__ == "__main__":
    print("=" * 60)
    print("🔧 ENHANCED ANALYZER ENDPOINT TEST")
    print("=" * 60)

    success = test_enhanced_analyzer_endpoint()

    print("\n" + "=" * 60)
    if success:
        print("✅ TEST PASSED: JSON serialization fix is working!")
        print("🎉 The original error has been resolved.")
    else:
        print("❌ TEST FAILED: There may still be issues.")
    print("=" * 60)
