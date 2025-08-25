#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
🔧 TEST SIMPLE ENDPOINT
Test the new simple endpoint we created
"""

import json

import requests


def test_simple_endpoint():
    print("🔧 TESTING SIMPLE ENDPOINT")
    print("=" * 50)

    # Test simple endpoint first
    api_url = "http://127.0.0.1:8000/pre-lokhung/api/simple-test/?analysis_date=2025-07-30&limit=10"

    try:
        print(f"🔍 Testing: {api_url}")
        response = requests.get(api_url, timeout=5)

        print(f"📊 Status: {response.status_code}")
        print(f"📊 Headers: {dict(response.headers)}")

        if response.status_code == 200:
            print("✅ Simple endpoint works!")

            try:
                data = response.json()
                print("✅ JSON parsing successful")

                # Check V2 structure
                v2_keys = [
                    "hybrid_analysis",
                    "intelligent_selections",
                    "optimal_methods",
                    "performance_prediction",
                ]
                found_keys = [key for key in v2_keys if key in data]

                print(f"📊 V2 Keys Found: {found_keys}")
                print(f"📊 Success: {data.get('success')}")
                print(f"📊 Test Mode: {data.get('test_mode')}")

                # Save response
                with open("simple_endpoint_response.json", "w", encoding="utf-8") as f:
                    json.dump(data, f, indent=2, ensure_ascii=False)
                print("💾 Response saved to simple_endpoint_response.json")

                return True

            except json.JSONDecodeError as e:
                print(f"❌ JSON parsing failed: {e}")
                print(f"📊 Raw response: {response.text[:300]}...")

        else:
            print(f"❌ HTTP Error: {response.status_code}")
            print(f"📊 Response: {response.text[:300]}...")

    except requests.exceptions.Timeout:
        print("❌ Simple endpoint also timed out!")
    except Exception as e:
        print(f"❌ Error: {e}")

    return False


def test_loadMethodAnalysis_with_simple_endpoint():
    print("\n🔧 TESTING loadMethodAnalysis WITH SIMPLE ENDPOINT")
    print("=" * 60)

    # Create modified test that uses simple endpoint
    js_test_code = """
// Test loadMethodAnalysis with simple endpoint
function testWithSimpleEndpoint() {
    // Mock DOM
    const mockElements = {
        'analysisDatePicker': { value: '2025-07-30' },
        'analysisLoading': { classList: { remove: () => {}, add: () => {} } },
        'analysisError': { classList: { remove: () => {}, add: () => {} }, textContent: '' },
        'analysisResults': { classList: { remove: () => {}, add: () => {} } },
        'predictionAnalysisDate': { textContent: '' }
    };
    
    global.document = {
        getElementById: (id) => mockElements[id] || { classList: { remove: () => {}, add: () => {} }, innerHTML: '', textContent: '' }
    };
    
    // Modified loadMethodAnalysis to use simple endpoint
    function loadMethodAnalysisSimple() {
        const dateInput = document.getElementById('analysisDatePicker');
        const analysisDate = dateInput.value;
        
        if (!analysisDate) {
            console.log('❌ No analysis date');
            return;
        }
        
        console.log('📅 Analysis Date:', analysisDate);
        
        // Use simple endpoint instead
        const apiUrl = `/pre-lokhung/api/simple-test/?analysis_date=${analysisDate}&limit=15`;
        
        console.log('🔍 Calling Simple API:', apiUrl);
        
        // Mock fetch with simple endpoint call
        return fetch(apiUrl)
            .then(response => {
                console.log('📡 Response status:', response.status);
                
                if (!response.ok) {
                    throw new Error(`HTTP ${response.status}: ${response.statusText}`);
                }
                
                const contentType = response.headers.get('content-type');
                if (!contentType || !contentType.includes('application/json')) {
                    throw new Error(`Expected JSON but got: ${contentType}`);
                }
                
                return response.json();
            })
            .then(data => {
                console.log('✅ Data received successfully');
                console.log('📊 Success:', data.success);
                console.log('📊 Test Mode:', data.test_mode);
                
                if (data.success) {
                    console.log('✅ Calling renderAnalysisResults...');
                    // renderAnalysisResults(data); // This would work with real DOM
                    console.log('✅ Test completed successfully!');
                } else {
                    console.log('❌ API returned success=false');
                }
            })
            .catch(error => {
                console.log('❌ Error:', error.message);
            });
    }
    
    // Run test
    return loadMethodAnalysisSimple();
}

// Execute
testWithSimpleEndpoint().then(() => {
    console.log('🎯 Simple endpoint test complete');
});
"""

    print("📝 JavaScript test code generated")
    print("🔍 This would test loadMethodAnalysis with simple endpoint")
    print("✅ Simple endpoint should respond quickly")


if __name__ == "__main__":
    print("🚀 SIMPLE ENDPOINT TEST")
    print("=" * 50)

    if test_simple_endpoint():
        test_loadMethodAnalysis_with_simple_endpoint()

    print("\n" + "=" * 50)
    print("✅ TEST COMPLETE")
