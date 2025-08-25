#!/usr/bin/env python3
"""
🔬 VERIFY V3 vs V2 FALLBACK COMPARISON
So sánh số từ V3 với số từ V2 fallback để xác nhận chúng khác nhau
"""
import json

import requests


def compare_v3_vs_v2_fallback():
    """So sánh V3 với V2 fallback để xác minh"""

    # 1. Test V3 với confidence cao để buộc fallback
    print("🧪 Test 1: V3 với confidence cao (để trigger fallback)")
    url = "http://127.0.0.1:8000/pre-lokhung/api/method-analysis-v3-enhanced/"

    # High confidence - should trigger fallback
    params_high = {
        "analysis_date": "2025-08-05",
        "limit": 15,
        "confidence": 95,  # Very high confidence - should trigger fallback
    }

    response_high = requests.get(url, params=params_high)
    if response_high.status_code == 200:
        data_high = response_high.json()
        approach_high = data_high.get("analysis_approach", "unknown")
        numbers_high = data_high.get("intelligent_selections", {}).get(
            "optimal_numbers", []
        )
        fallback_high = (
            "v2" in approach_high.lower() or "fallback" in approach_high.lower()
        )

        print(f"   📊 Approach: {approach_high}")
        print(f"   🎯 Numbers: {numbers_high}")
        print(f"   🔍 Fallback: {'YES' if fallback_high else 'NO'}")
    else:
        print(f"   ❌ Error: {response_high.status_code}")
        return

    print("\n" + "=" * 60)

    # 2. Test V3 với confidence thấp (real V3)
    print("🧪 Test 2: V3 với confidence thấp (real V3 analysis)")

    params_low = {
        "analysis_date": "2025-08-05",
        "limit": 15,
        "confidence": 20,  # Low confidence - should use real V3
    }

    response_low = requests.get(url, params=params_low)
    if response_low.status_code == 200:
        data_low = response_low.json()
        approach_low = data_low.get("analysis_approach", "unknown")
        numbers_low = data_low.get("intelligent_selections", {}).get(
            "optimal_numbers", []
        )
        fallback_low = (
            "v2" in approach_low.lower() or "fallback" in approach_low.lower()
        )

        print(f"   📊 Approach: {approach_low}")
        print(f"   🎯 Numbers: {numbers_low}")
        print(f"   🔍 Fallback: {'YES' if fallback_low else 'NO'}")
    else:
        print(f"   ❌ Error: {response_low.status_code}")
        return

    print("\n" + "=" * 60)
    print("🔬 COMPARISON ANALYSIS:")

    # 3. Compare numbers
    if numbers_high and numbers_low:
        same_numbers = set(numbers_high) == set(numbers_low)
        shared_numbers = set(numbers_high) & set(numbers_low)

        print(f"   Numbers identical: {'YES' if same_numbers else 'NO'}")
        print(
            f"   Shared numbers: {sorted(list(shared_numbers))} ({len(shared_numbers)} numbers)"
        )
        print(
            f"   V2 fallback only: {sorted(list(set(numbers_high) - set(numbers_low)))}"
        )
        print(f"   V3 real only: {sorted(list(set(numbers_low) - set(numbers_high)))}")

        # 4. Analysis conclusion
        print(f"\n🏁 CONCLUSION:")
        if same_numbers:
            print("   ⚠️ IDENTICAL NUMBERS - V3 might be using V2 fallback logic!")
            print("   📝 This suggests V3 analysis is not generating distinct results")
        else:
            print("   ✅ DIFFERENT NUMBERS - V3 is generating distinct results!")
            print("   📝 This confirms V3 Enhanced Analysis is working independently")
            if shared_numbers:
                print(
                    f"   📊 {len(shared_numbers)} shared numbers is expected due to lottery nature"
                )
    else:
        print("   ❌ Cannot compare - missing numbers")


if __name__ == "__main__":
    compare_v3_vs_v2_fallback()
