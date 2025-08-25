#!/usr/bin/env python3
"""
Test DataTable reinitialize fix by checking the JavaScript content
"""
import re

import requests


def test_datatable_reinitialize_fix():
    """Test if DataTable reinitialize issue is fixed"""
    url = "http://127.0.0.1:8000/pre-lokhung/enhanced-analyzer/"

    print("🧪 Testing DataTable reinitialize fix...")
    print(f"URL: {url}")

    try:
        response = requests.get(url, timeout=10)

        if response.status_code == 200:
            content = response.text

            # Check for DataTable reinitialize protection
            checks = {
                "isDataTable check": "isDataTable('#resultsTable')" in content,
                "destroy() method": ".DataTable().destroy()" in content,
                "destroy option": "destroy: true" in content,
                "console.log for destroy": "destroying it first" in content,
                "null assignment after destroy": "resultsDataTable = null" in content,
                "proper initialization guard": "if (!resultsDataTable ||" in content,
            }

            print("\n✅ DataTable Reinitialize Protection Check:")
            all_passed = True
            for check, passed in checks.items():
                status = "✅ PASS" if passed else "❌ FAIL"
                print(f"  {status}: {check}")
                if not passed:
                    all_passed = False

            # Check for potential problematic patterns
            problems = []

            # Look for multiple DataTable initializations without checks
            dt_init_count = len(re.findall(r"\.DataTable\(\{", content))
            if dt_init_count > 1:
                problems.append(
                    f"Multiple DataTable initializations found: {dt_init_count}"
                )

            # Look for clear() calls without null checks
            clear_calls = re.findall(r"resultsDataTable\.clear\(\)", content)
            proper_clear_calls = re.findall(
                r"if.*resultsDataTable.*resultsDataTable\.clear\(\)", content, re.DOTALL
            )

            if len(clear_calls) > len(proper_clear_calls):
                problems.append("Found unprotected clear() calls")

            if problems:
                print(f"\n⚠️  Potential issues found:")
                for problem in problems:
                    print(f"    - {problem}")
                return False
            else:
                print("\n✅ No DataTable reinitialize issues found")
                return all_passed

        else:
            print(f"❌ HTTP Error {response.status_code}")
            return False

    except Exception as e:
        print(f"❌ Error: {e}")
        return False


if __name__ == "__main__":
    print("=" * 60)
    print("🔧 DATATABLE REINITIALIZE FIX TEST")
    print("=" * 60)

    success = test_datatable_reinitialize_fix()

    print("\n" + "=" * 60)
    if success:
        print("✅ DATATABLE REINITIALIZE FIX SUCCESSFUL!")
        print("🎉 DataTables warning should be resolved.")
    else:
        print("❌ SOME DATATABLE ISSUES MAY STILL EXIST")
    print("=" * 60)
