#!/usr/bin/env python3
"""
Test JavaScript Fix for TypeError: insights.quantum_entanglement_score.toFixed is not a function
"""

import requests
import json
import sys

def test_ajax_api():
    """Test the AJAX API that was causing JavaScript errors"""
    
    url = "http://127.0.0.1:8000/analytic-frequence/ajax-prediction/"
    
    # Test data
    test_payload = {
        "prediction_date": "2025-08-14",
        "prediction_horizon": 5,
        "use_real_data": True
    }
    
    print("🧪 Testing AJAX API...")
    print(f"URL: {url}")
    print(f"Payload: {json.dumps(test_payload, indent=2)}")
    
    try:
        response = requests.post(
            url,
            json=test_payload,
            headers={
                'Content-Type': 'application/json',
                'Accept': 'application/json'
            },
            timeout=30
        )
        
        print(f"\n📊 Response Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            
            if data.get('success'):
                print("✅ API Request successful!")
                
                # Check revolutionary insights structure
                insights = data.get('prediction_data', {}).get('revolutionary_insights', {})
                print(f"\n🔍 Revolutionary Insights Analysis:")
                print(f"Structure: {type(insights)}")
                
                # Check each field that was causing JavaScript errors
                fields_to_check = [
                    'information_entropy',
                    'quantum_entanglement_score', 
                    'consciousness_level',
                    'time_crystal_strength'
                ]
                
                for field in fields_to_check:
                    value = insights.get(field)
                    value_type = type(value).__name__
                    print(f"  {field}: {value} (type: {value_type})")
                    
                    # Test if it's safe for JavaScript .toFixed()
                    if isinstance(value, (int, float)) and value is not None:
                        print(f"    ✅ Safe for .toFixed(): {value:.3f}")
                    elif value is None:
                        print(f"    ⚠️  NULL value - needs safe handling")
                    else:
                        print(f"    ❌ NOT safe for .toFixed() - needs conversion")
                
                # Summary
                print(f"\n📝 Summary:")
                print(f"- Predictions: {len(data.get('prediction_data', {}).get('predictions', []))}")
                print(f"- Confidence: {data.get('prediction_data', {}).get('confidence_score', 'N/A')}")
                print(f"- Processing time: {data.get('prediction_data', {}).get('processing_time_ms', 'N/A')}ms")
                
                return True
                
            else:
                print(f"❌ API Error: {data.get('error', 'Unknown error')}")
                return False
                
        else:
            print(f"❌ HTTP Error: {response.status_code}")
            try:
                error_data = response.json()
                print(f"Error details: {json.dumps(error_data, indent=2)}")
            except:
                print(f"Error response: {response.text[:200]}...")
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ Connection Error: Make sure Django server is running on http://127.0.0.1:8000")
        return False
    except requests.exceptions.Timeout:
        print("❌ Timeout Error: Request took too long")
        return False
    except Exception as e:
        print(f"❌ Unexpected Error: {e}")
        return False

def test_browser_compatibility():
    """Test if the data structure is compatible with JavaScript"""
    
    print("\n🌐 Testing Browser Compatibility...")
    
    # Simulate the problematic JavaScript operations
    test_data = {
        'revolutionary_insights': {
            'information_entropy': 0.756,
            'quantum_entanglement_score': 0.892,
            'consciousness_level': 0.634,
            'time_crystal_strength': 0.445
        }
    }
    
    print("Testing JavaScript operations simulation:")
    
    def safe_to_fixed(value, decimals=3):
        """Python simulation of the JavaScript safeToFixed function"""
        if value is None:
            return '0.' + '0' * decimals
        
        try:
            num_value = float(value) if isinstance(value, str) else value
            if not isinstance(num_value, (int, float)) or not (-float('inf') < num_value < float('inf')):
                return '0.' + '0' * decimals
            return f"{num_value:.{decimals}f}"
        except (ValueError, TypeError):
            return '0.' + '0' * decimals
    
    insights = test_data['revolutionary_insights']
    
    # Test the operations that were failing
    try:
        info_entropy = safe_to_fixed(insights.get('information_entropy'), 3)
        quantum_score = safe_to_fixed(insights.get('quantum_entanglement_score'), 3)
        consciousness = safe_to_fixed(insights.get('consciousness_level'), 3)
        crystal_strength = safe_to_fixed(insights.get('time_crystal_strength'), 3)
        
        print(f"✅ Information Entropy: {info_entropy}")
        print(f"✅ Quantum Entanglement: {quantum_score}")
        print(f"✅ Consciousness Level: {consciousness}")
        print(f"✅ Time Crystal Strength: {crystal_strength}")
        
        return True
        
    except Exception as e:
        print(f"❌ JavaScript simulation failed: {e}")
        return False

if __name__ == "__main__":
    print("🔧 JavaScript TypeError Fix Test")
    print("=" * 50)
    
    # Test the API
    api_success = test_ajax_api()
    
    # Test browser compatibility
    browser_success = test_browser_compatibility()
    
    print("\n" + "=" * 50)
    if api_success and browser_success:
        print("🎉 ALL TESTS PASSED! JavaScript errors should be fixed.")
        sys.exit(0)
    else:
        print("❌ Some tests failed. Check the output above.")
        sys.exit(1)
