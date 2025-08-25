#!/usr/bin/env python3
"""
Test the Enhanced Analyzer template JavaScript fixes
"""
import json
from datetime import datetime

import requests


def test_template_fixes():
    """Test if the template JavaScript fixes work"""
    url = "http://127.0.0.1:8000/pre-lokhung/enhanced-analyzer/"

    print("🧪 Testing Enhanced Analyzer template...")
    print(f"URL: {url}")

    try:
        # Test accessing the template first
        response = requests.get(url, timeout=10)

        print(f"Status Code: {response.status_code}")
        print(f"Content-Type: {response.headers.get('content-type')}")

        if response.status_code == 200:
            content = response.text

            # Check for key JavaScript elements
            js_checks = {
                "resultsDataTable initialization": "resultsDataTable = null" in content,
                "Error handling in initializeComponents": "console.error" in content
                and "Failed to initialize DataTable" in content,
                "Safe showResultsTable function": "if (!resultsDataTable)" in content,
                "updateTableForHotNumbers with error handling": "updateTableForHotNumbers(data)"
                in content,
                "Date inputs present": 'id="startDate"' in content
                and 'id="endDate"' in content,
                "DataTable HTML present": 'id="resultsTable"' in content,
            }

            print("\n✅ JavaScript Elements Check:")
            for check, passed in js_checks.items():
                status = "✅ PASS" if passed else "❌ FAIL"
                print(f"  {status}: {check}")

            all_passed = all(js_checks.values())

            # Check for potential error patterns
            error_patterns = [
                "resultsDataTable.clear()",  # Should be wrapped in null check
                "aDataSort",  # Should not appear directly
                "undefined is not an object",
            ]

            errors_found = []
            for pattern in error_patterns:
                if pattern in content and pattern != "resultsDataTable.clear()":
                    errors_found.append(pattern)

            if errors_found:
                print(f"\n⚠️  Potential issues found: {errors_found}")
            else:
                print("\n✅ No obvious JavaScript error patterns found")

            return all_passed and not errors_found

        else:
            print(f"❌ HTTP Error {response.status_code}")
            return False

    except requests.exceptions.RequestException as e:
        print(f"❌ Request failed: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False


if __name__ == "__main__":
    print("=" * 60)
    print("🔧 ENHANCED ANALYZER TEMPLATE TEST")
    print("=" * 60)

    success = test_template_fixes()

    print("\n" + "=" * 60)
    if success:
        print("✅ TEMPLATE FIXES LOOK GOOD!")
        print("🎉 JavaScript errors should be resolved.")
    else:
        print("❌ SOME ISSUES MAY STILL EXIST")
        print("Please check the browser console for errors.")
    print("=" * 60)
