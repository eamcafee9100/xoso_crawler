import requests

def test_comprehensive_page():
    """Test comprehensive page structure"""
    try:
        url = "http://127.0.0.1:8000/number-frequency-stats/?analysis_mode=comprehensive"
        response = requests.get(url)
        
        if response.status_code == 200:
            content = response.text
            
            print("=== Page Structure Analysis ===")
            
            # Check key elements
            checks = [
                ('frequency-grid', 'Grid container'),
                ('number-analysis-btn', 'Analysis buttons'),
                ('frequency-cell', 'Grid cells'),
                ('data-number=', 'Data attributes'),
                ('generate-heatmap', 'Heatmap button'),
                ('comprehensive_analysis', 'Analysis data context'),
                ('Số phần tử phân tích:', 'Debug info'),
            ]
            
            for search_text, description in checks:
                count = content.count(search_text)
                status = "✅" if count > 0 else "❌"
                print(f"{status} {description}: {count} occurrences")
            
            # Check for comprehensive analysis section
            if 'id="comprehensive"' in content:
                print("✅ Comprehensive tab section found")
                
                # Extract the comprehensive section
                start_idx = content.find('id="comprehensive"')
                if start_idx > 0:
                    section_start = content.rfind('<div', 0, start_idx)
                    section_end = content.find('</div>', start_idx)
                    
                    # Find the end of the comprehensive section
                    depth = 1
                    i = section_end + 6
                    while i < len(content) and depth > 0:
                        if content[i:i+5] == '<div ':
                            depth += 1
                        elif content[i:i+6] == '</div>':
                            depth -= 1
                        i += 1
                    
                    comprehensive_section = content[section_start:i]
                    
                    # Count elements in comprehensive section only
                    grid_count = comprehensive_section.count('frequency-cell number-analysis-btn')
                    print(f"📊 Grid cells in comprehensive section: {grid_count}")
                    
                    if 'comprehensive_analysis' in comprehensive_section:
                        print("✅ Comprehensive analysis data variable found in section")
                    else:
                        print("❌ Comprehensive analysis data variable NOT found in section")
            else:
                print("❌ Comprehensive tab section NOT found")
            
            # Save for manual inspection
            with open('debug_comprehensive_page.html', 'w', encoding='utf-8') as f:
                f.write(content)
            print("\n📄 Full page saved to: debug_comprehensive_page.html")
            
            return True
        else:
            print(f"❌ HTTP Error: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Exception: {e}")
        return False

def test_api_directly():
    """Test API endpoints directly"""
    print("\n=== API Tests ===")
    
    # Test number analysis API
    try:
        response = requests.get("http://127.0.0.1:8000/results/number-analysis/?number=05")
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                print("✅ Number Analysis API working")
            else:
                print(f"❌ Number Analysis API error: {data.get('error')}")
        else:
            print(f"❌ Number Analysis API HTTP error: {response.status_code}")
    except Exception as e:
        print(f"❌ Number Analysis API exception: {e}")
    
    # Test heatmap API
    try:
        response = requests.get("http://127.0.0.1:8000/results/frequency-heatmap/?period=30&type=frequency")
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                print("✅ Heatmap API working")
            else:
                print(f"❌ Heatmap API error: {data.get('error')}")
        else:
            print(f"❌ Heatmap API HTTP error: {response.status_code}")
    except Exception as e:
        print(f"❌ Heatmap API exception: {e}")

if __name__ == "__main__":
    print("🔍 Testing Comprehensive Analysis Page...")
    
    page_ok = test_comprehensive_page()
    test_api_directly()
    
    print(f"\n=== Summary ===")
    print(f"Page structure: {'✅' if page_ok else '❌'}")
    print("\nNext steps:")
    print("1. Open debug_comprehensive_page.html to inspect HTML")
    print("2. Check browser console for JavaScript errors")
    print("3. Verify that grid cells have 'number-analysis-btn' class")
