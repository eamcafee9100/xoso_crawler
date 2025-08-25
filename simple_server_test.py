#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
🔧 SIMPLE DJANGO SERVER TEST
Quick test to check if Django server is accessible
"""

import json

import requests


def test_basic_connection():
    print("🔧 BASIC CONNECTION TEST")
    print("=" * 50)

    # Test root URL first
    try:
        response = requests.get("http://127.0.0.1:8000/", timeout=5)
        print(f"✅ Root URL Status: {response.status_code}")

        if response.status_code == 200:
            print("✅ Django server is accessible")
        else:
            print(f"⚠️ Django returned: {response.status_code}")

    except Exception as e:
        print(f"❌ Connection failed: {e}")
        return False

    return True


def test_admin_url():
    print("\n🔧 ADMIN URL TEST")
    print("=" * 50)

    try:
        response = requests.get("http://127.0.0.1:8000/admin/", timeout=5)
        print(f"📊 Admin URL Status: {response.status_code}")

        if response.status_code in [200, 302]:
            print("✅ Admin URL accessible")

    except Exception as e:
        print(f"❌ Admin URL failed: {e}")


def test_api_endpoint():
    print("\n🔧 API ENDPOINT TEST")
    print("=" * 50)

    # Test if endpoint exists
    api_url = "http://127.0.0.1:8000/pre-lokhung/api/method-analysis-v2/?analysis_date=2025-07-30&limit=5"

    try:
        response = requests.get(api_url, timeout=5)
        print(f"📊 API Status: {response.status_code}")
        print(f"📊 API Headers: {dict(response.headers)}")

        if response.status_code == 200:
            print("✅ API endpoint accessible")
            try:
                data = response.json()
                print(f"📊 Response type: {type(data)}")
                if isinstance(data, dict):
                    print(f"📊 Response keys: {list(data.keys())}")
                print("✅ JSON parsing successful")

                # Save response
                with open("api_response_debug.json", "w", encoding="utf-8") as f:
                    json.dump(data, f, indent=2, ensure_ascii=False)
                print("💾 Response saved to api_response_debug.json")

            except json.JSONDecodeError:
                print("❌ JSON parsing failed")
                print(f"📊 Raw response: {response.text[:200]}...")

        elif response.status_code == 404:
            print("❌ API endpoint not found")

        elif response.status_code == 500:
            print("❌ Internal server error")
            print(f"📊 Error response: {response.text[:200]}...")

        else:
            print(f"❌ Unexpected status: {response.status_code}")
            print(f"📊 Response: {response.text[:200]}...")

    except requests.exceptions.Timeout:
        print("❌ Request timed out")
    except Exception as e:
        print(f"❌ Request failed: {e}")


if __name__ == "__main__":
    print("🚀 SIMPLE DJANGO SERVER TEST")
    print("=" * 50)

    if test_basic_connection():
        test_admin_url()
        test_api_endpoint()

    print("\n" + "=" * 50)
    print("✅ TEST COMPLETE")
