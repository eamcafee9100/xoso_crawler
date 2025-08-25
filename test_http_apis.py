import requests
import json

# Test the APIs directly via HTTP
base_url = "http://127.0.0.1:8000"

def test_number_analysis_api():
    """Test number analysis API via HTTP"""
    print("=== Testing Number Analysis API ===")
    
    try:
        url = f"{base_url}/results/number-analysis/?number=05"
        print(f"Testing: {url}")
        
        response = requests.get(url)
        print(f"Status code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"Success: {data.get('success')}")
            if data.get('success'):
                analysis = data.get('analysis', {})
                print(f"Number: {analysis.get('number')}")
                print(f"Current gan days: {analysis.get('gan_analysis', {}).get('current_gan_days')}")
                print("✅ Number Analysis API working!")
                return True
            else:
                print(f"❌ API Error: {data.get('error')}")
                return False
        else:
            print(f"❌ HTTP Error: {response.status_code}")
            print(f"Response: {response.text[:200]}")
            return False
            
    except Exception as e:
        print(f"❌ Exception: {e}")
        return False

def test_heatmap_api():
    """Test heatmap API via HTTP"""
    print("\n=== Testing Heatmap API ===")
    
    try:
        url = f"{base_url}/results/frequency-heatmap/?period=30&type=frequency"
        print(f"Testing: {url}")
        
        response = requests.get(url)
        print(f"Status code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"Success: {data.get('success')}")
            if data.get('success'):
                heatmap_data = data.get('data', [])
                print(f"Data points: {len(heatmap_data)}")
                if heatmap_data:
                    print(f"First data point: {heatmap_data[0]}")
                print("✅ Heatmap API working!")
                return True
            else:
                print(f"❌ API Error: {data.get('error')}")
                return False
        else:
            print(f"❌ HTTP Error: {response.status_code}")
            print(f"Response: {response.text[:200]}")
            return False
            
    except Exception as e:
        print(f"❌ Exception: {e}")
        return False

def test_comprehensive_page():
    """Test comprehensive analysis page"""
    print("\n=== Testing Comprehensive Analysis Page ===")
    
    try:
        url = f"{base_url}/number-frequency-stats/?analysis_mode=comprehensive"
        print(f"Testing: {url}")
        
        response = requests.get(url)
        print(f"Status code: {response.status_code}")
        
        if response.status_code == 200:
            content = response.text
            
            # Check key elements
            checks = [
                ('number-analysis-btn', 'Analysis buttons'),
                ('frequency-cell', 'Frequency cells'),
                ('data-number=', 'Data attributes'),
                ('generate-heatmap', 'Heatmap button'),
                ('showNumberAnalysis', 'JS function'),
                ('generateHeatmap', 'JS function'),
            ]
            
            print("\nHTML Element Checks:")
            for check_str, description in checks:
                found = check_str in content
                status = "✅" if found else "❌"
                print(f"{status} {description}: {'Found' if found else 'NOT found'}")
            
            # Count elements
            cell_count = content.count('frequency-cell')
            button_count = content.count('number-analysis-btn')
            print(f"\nElement counts:")
            print(f"- Frequency cells: {cell_count}")
            print(f"- Analysis buttons: {button_count}")
            
            # Save for inspection
            with open('debug_page_output.html', 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"\n📄 Page saved to: debug_page_output.html")
            
            return True
        else:
            print(f"❌ HTTP Error: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Exception: {e}")
        return False

if __name__ == "__main__":
    print("🔍 Testing Django App via HTTP requests...")
    print("Make sure Django server is running on http://127.0.0.1:8000/")
    
    api1_ok = test_number_analysis_api()
    api2_ok = test_heatmap_api()
    page_ok = test_comprehensive_page()
    
    print(f"\n=== Final Results ===")
    print(f"Number Analysis API: {'✅' if api1_ok else '❌'}")
    print(f"Heatmap API: {'✅' if api2_ok else '❌'}")
    print(f"Comprehensive Page: {'✅' if page_ok else '❌'}")
    
    if all([api1_ok, api2_ok, page_ok]):
        print("\n🎉 All APIs and page are working!")
        print("If clicking doesn't work, check browser console for JS errors.")
    else:
        print("\n⚠️ Some issues found. Check the errors above.")
