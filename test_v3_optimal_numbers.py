#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
🧪 TEST V3 OPTIMAL NUMBERS GENERATION
"""

import json

import requests


def test_v3_optimal_numbers():
    """Test V3 API để kiểm tra optimal numbers"""
    try:
        url = "http://127.0.0.1:8000/pre-lokhung/api/method-analysis-v3-enhanced/"
        params = {
            "analysis_date": "2025-08-05",  # Use recent date with actual data
            "limit": 15,
            "confidence": 20,  # Much lower confidence threshold
        }

        print("🧪 Testing V3 Optimal Numbers Generation...")
        print(f"📡 URL: {url}")
        print(f"📋 Params: {params}")

        response = requests.get(url, params=params)

        print(f"📊 Status Code: {response.status_code}")
        print(f"📄 Content Type: {response.headers.get('content-type')}")

        if response.status_code == 200:
            data = response.json()

            # Check basic response
            print(f"✅ Success: {data.get('success')}")
            print(f"📅 Analysis Date: {data.get('analysis_date')}")

            # Check intelligent selections
            intelligent_selections = data.get("intelligent_selections", {})
            optimal_numbers = intelligent_selections.get("optimal_numbers", [])

            print(f"🎯 Optimal Numbers Count: {len(optimal_numbers)}")
            print(f"🎯 Optimal Numbers: {optimal_numbers}")

            # ✅ CHECK ANALYSIS APPROACH
            approach = data.get("analysis_approach", "unknown")
            v3_enhancements = data.get("v3_enhancements", {})

            print(f"📊 Analysis Approach: {approach}")

            # Check if fallback was used
            fallback_indicators = [
                "v2" in approach.lower(),
                "fallback" in approach.lower(),
                "proven_logic" in approach.lower(),
                v3_enhancements.get("fallback_to_proven_v2", False),
            ]

            is_fallback = any(fallback_indicators)

            print(f"🔍 Fallback Used: {'YES' if is_fallback else 'NO'}")
            print(f"🔍 Real V3 Analysis: {'NO' if is_fallback else 'YES'}")

            if is_fallback:
                print("⚠️ NUMBERS ARE FROM V2 FALLBACK MECHANISM!")
                print("📝 V3 strict criteria failed, used proven V2 logic")
            else:
                print("✅ NUMBERS ARE FROM REAL V3 ENHANCED ANALYSIS!")
                print("📝 V3 temporal validation and uncertainty quantification used")

            if len(optimal_numbers) > 0:
                print("✅ V3 Optimal Numbers generation: SUCCESS")
                return True
            else:
                print("❌ V3 Optimal Numbers generation: FAILED - Empty list")
                return False
        else:
            print(f"❌ API Error: {response.status_code}")
            print(f"📄 Response: {response.text[:500]}")
            return False

    except Exception as e:
        print(f"❌ Test Error: {e}")
        return False


if __name__ == "__main__":
    success = test_v3_optimal_numbers()
    if success:
        print("\n🎉 V3 Optimal Numbers test PASSED!")
    else:
        print("\n💥 V3 Optimal Numbers test FAILED!")
