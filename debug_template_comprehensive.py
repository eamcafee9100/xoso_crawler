#!/usr/bin/env python
"""
Debug script để kiểm tra template comprehensive analysis
"""
import os
import django
import sys

# Setup Django
sys.path.append('c:\\Users\\n2t\\Documents\\xoso_crawler')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'xoso_crawler.settings')
django.setup()

from django.test import Client
from django.contrib.auth.models import User

def test_comprehensive_template():
    """Test comprehensive analysis template"""
    print("=== Testing Comprehensive Analysis Template ===")
    
    try:
        # Create test client
        client = Client()
        
        # Test comprehensive analysis mode
        url = '/number-frequency-stats/?analysis_mode=comprehensive'
        print(f"Testing URL: {url}")
        
        response = client.get(url)
        print(f"Status code: {response.status_code}")
        
        if response.status_code == 200:
            content = response.content.decode('utf-8')
            
            # Check if comprehensive_analysis data is present
            if 'comprehensive_analysis' in content:
                print("✅ comprehensive_analysis found in template")
            else:
                print("❌ comprehensive_analysis NOT found in template")
            
            # Check for specific HTML elements
            checks = [
                ('number-analysis-btn', 'Analysis button class'),
                ('frequency-cell', 'Frequency cell class'),
                ('data-number=', 'Data number attributes'),
                ('generate-heatmap', 'Generate heatmap button'),
                ('numberAnalysisModal', 'Analysis modal'),
                ('current_gan_days', 'Gan days data'),
            ]
            
            print("\n=== HTML Element Checks ===")
            for check_str, description in checks:
                if check_str in content:
                    print(f"✅ {description}: Found")
                else:
                    print(f"❌ {description}: NOT found")
            
            # Count frequency cells
            cell_count = content.count('frequency-cell')
            print(f"\nFrequency cells found: {cell_count}")
            
            # Check for JavaScript functions
            js_checks = [
                ('showNumberAnalysis', 'Number analysis function'),
                ('generateHeatmap', 'Generate heatmap function'),
                ('addEventListener', 'Event listeners'),
            ]
            
            print("\n=== JavaScript Checks ===")
            for js_str, description in js_checks:
                if js_str in content:
                    print(f"✅ {description}: Found")
                else:
                    print(f"❌ {description}: NOT found")
            
            # Save content to file for manual inspection
            with open('debug_template_output.html', 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"\n📄 Full template saved to: debug_template_output.html")
            
        else:
            print(f"❌ HTTP Error: {response.status_code}")
            print("Response content:", response.content[:500])
        
        return response.status_code == 200
        
    except Exception as e:
        print(f"❌ Exception: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_context_data():
    """Test if context data is being passed correctly"""
    print("\n=== Testing Context Data ===")
    
    try:
        from results.views import NumberFrequencyStatsListView
        from django.test import RequestFactory
        
        # Create request
        factory = RequestFactory()
        request = factory.get('/number-frequency-stats/?analysis_mode=comprehensive')
        
        # Create view and get context
        view = NumberFrequencyStatsListView()
        view.request = request
        view.object_list = view.get_queryset()
        
        context = view.get_context_data()
        
        print(f"Analysis mode: {context.get('analysis_mode')}")
        print(f"Comprehensive analysis exists: {'comprehensive_analysis' in context}")
        
        if 'comprehensive_analysis' in context:
            comp_analysis = context['comprehensive_analysis']
            print(f"Comprehensive analysis type: {type(comp_analysis)}")
            print(f"Comprehensive analysis keys: {list(comp_analysis.keys())[:10]}...")
            
            # Check specific numbers
            test_numbers = ['00', '05', '10']
            for num in test_numbers:
                if num in comp_analysis:
                    data = comp_analysis[num]
                    print(f"Number {num} data: {data}")
                else:
                    print(f"Number {num}: NOT found in comprehensive analysis")
        
        return True
        
    except Exception as e:
        print(f"❌ Exception in context test: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    template_ok = test_comprehensive_template()
    context_ok = test_context_data()
    
    print(f"\n=== Final Results ===")
    print(f"Template rendering: {'✅' if template_ok else '❌'}")
    print(f"Context data: {'✅' if context_ok else '❌'}")
    
    if template_ok and context_ok:
        print("\n🎉 Template and context are working!")
        print("Open debug_template_output.html to inspect the full HTML.")
        print("Next step: Check browser console for JavaScript errors.")
    else:
        print("\n⚠️ Issues found. Check the errors above.")
