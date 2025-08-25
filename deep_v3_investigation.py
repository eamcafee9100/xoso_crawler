#!/usr/bin/env python3
"""
🔍 DEEP INVESTIGATION OF V3 NUMBER GENERATION
Điều tra sâu cách V3 tạo ra những con số này
"""
import requests


def investigate_v3_generation():
    """Điều tra chi tiết quá trình sinh số của V3"""

    # Test with different dates and parameters
    test_cases = [
        {"analysis_date": "2025-08-05", "confidence": 20, "name": "Original"},
        {"analysis_date": "2025-08-04", "confidence": 20, "name": "Different Date"},
        {"analysis_date": "2025-08-05", "confidence": 50, "name": "Medium Confidence"},
        {
            "analysis_date": "2025-08-03",
            "confidence": 80,
            "name": "High Confidence + Old Date",
        },
    ]

    url = "http://127.0.0.1:8000/pre-lokhung/api/method-analysis-v3-enhanced/"

    print("🔍 DEEP V3 INVESTIGATION - Testing Different Scenarios")
    print("=" * 70)

    results = []

    for i, case in enumerate(test_cases, 1):
        print(f"\n🧪 Test {i}: {case['name']}")
        print(f"   📅 Date: {case['analysis_date']}")
        print(f"   🎯 Confidence: {case['confidence']}%")

        params = {
            "analysis_date": case["analysis_date"],
            "limit": 15,
            "confidence": case["confidence"],
        }

        response = requests.get(url, params=params, timeout=30)

        if response.status_code == 200:
            data = response.json()
            approach = data.get("analysis_approach", "unknown")
            numbers = data.get("intelligent_selections", {}).get("optimal_numbers", [])
            v3_enhancements = data.get("v3_enhancements", {})

            print(f"   📊 Approach: {approach}")
            print(f"   🎯 Numbers: {numbers}")
            print(f"   🔍 V3 Enhancements: {bool(v3_enhancements)}")

            results.append(
                {
                    "case": case["name"],
                    "approach": approach,
                    "numbers": numbers,
                    "v3_active": bool(v3_enhancements),
                }
            )
        else:
            print(f"   ❌ Error: {response.status_code}")
            if response.status_code == 422:
                error_data = response.json()
                print(f"   📝 Error: {error_data.get('error', 'Unknown')}")

    print("\n" + "=" * 70)
    print("📊 ANALYSIS SUMMARY:")

    # Check if all results are identical
    if results:
        first_numbers = results[0]["numbers"]
        all_identical = all(r["numbers"] == first_numbers for r in results)

        print(f"\n🔍 All results identical: {'YES' if all_identical else 'NO'}")

        if all_identical:
            print("⚠️ PROBLEM DETECTED:")
            print("   • V3 returns same numbers regardless of date/confidence")
            print("   • This suggests:")
            print("     1. V3 analysis is using cached/static data")
            print("     2. The algorithm is deterministic with same input")
            print("     3. Method selection criteria are too restrictive")
            print("     4. All scenarios select same top methods")

            # Check approach consistency
            all_approaches = [r["approach"] for r in results]
            unique_approaches = set(all_approaches)
            print(f"\n📊 Approaches used: {unique_approaches}")

            if len(unique_approaches) == 1:
                approach = list(unique_approaches)[0]
                if "v3" in approach.lower() and "fallback" not in approach.lower():
                    print("✅ Consistent V3 approach - Numbers are from V3 analysis")
                    print(
                        "📝 The identical numbers suggest V3 is selecting same optimal methods"
                    )
                    print(
                        "   This could be correct if these are truly the best methods"
                    )
                else:
                    print("⚠️ All scenarios used same approach - need investigation")
        else:
            print("✅ V3 generates different numbers for different scenarios")
            print("📝 This is expected behavior")

            # Show differences
            for r in results:
                print(f"   {r['case']}: {r['numbers']}")

    print("\n🏁 VERDICT:")
    if results and all(
        r["approach"] == "enhanced_v3_temporal_validation" for r in results
    ):
        if all(r["numbers"] == results[0]["numbers"] for r in results):
            print("🤔 V3 IS WORKING but returns consistent results")
            print("   This might be CORRECT if the same methods are always optimal")
            print(
                "   The numbers [37, 39, 40, 41, 48, 50, 51, 52] might be the true optimal set"
            )
        else:
            print("✅ V3 IS WORKING and returns varied results")
    else:
        print("⚠️ V3 behavior is inconsistent - needs investigation")


if __name__ == "__main__":
    investigate_v3_generation()
