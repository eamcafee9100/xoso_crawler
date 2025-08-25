#!/usr/bin/env python3
"""
Check if V3 optimal numbers are from real V3 analysis or fallback
"""
import json

import requests


def check_v3_approach():
    """Check detailed V3 analysis approach"""

    # Test V3 API
    url = "http://127.0.0.1:8000/pre-lokhung/api/method-analysis-v3-enhanced/"
    params = {"analysis_date": "2025-08-05", "limit": 15, "confidence": 20}

    print("🔍 Checking V3 Analysis Approach...")
    response = requests.get(url, params=params)
    data = response.json()

    # Extract key information
    approach = data.get("analysis_approach", "unknown")
    v3_enhancements = data.get("v3_enhancements", {})
    optimal_numbers = data.get("intelligent_selections", {}).get("optimal_numbers", [])

    print(f"📊 Analysis Approach: {approach}")
    print(f"🎯 Optimal Numbers: {optimal_numbers}")
    print(f"📈 V3 Enhancements:")
    for key, value in v3_enhancements.items():
        print(f"   {key}: {value}")

    # Determine if fallback was used
    fallback_indicators = [
        "v2" in approach.lower(),
        "fallback" in approach.lower(),
        "proven_logic" in approach.lower(),
        v3_enhancements.get("fallback_to_proven_v2", False),
        v3_enhancements.get("attempted_v3_analysis", False)
        and "v2" in approach.lower(),
    ]

    is_fallback = any(fallback_indicators)

    print(f"\n🔍 ANALYSIS RESULT:")
    print(f"   Fallback Used: {'YES' if is_fallback else 'NO'}")
    print(f"   Real V3 Analysis: {'NO' if is_fallback else 'YES'}")

    if is_fallback:
        print(f"   ⚠️ Numbers are from V2 fallback mechanism")
        print(
            f"   📝 Reason: V3 strict criteria likely failed to select sufficient methods"
        )
    else:
        print(f"   ✅ Numbers are from real V3 Enhanced Method Analysis")
        print(f"   📝 V3 temporal validation and uncertainty quantification used")

    return is_fallback, approach, optimal_numbers


if __name__ == "__main__":
    check_v3_approach()
