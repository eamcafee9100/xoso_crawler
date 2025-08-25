#!/usr/bin/env python
"""
Test script để kiểm tra views API hoạt động đúng không
"""
import os
import django
import sys

# Setup Django
sys.path.append('c:\\Users\\n2t\\Documents\\xoso_crawler')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'xoso_crawler.settings')
django.setup()

from django.test import RequestFactory
from results.views import NumberDetailAnalysisView, NumberFrequencyHeatmapView
from django.http import HttpRequest

def test_number_detail_analysis():
    """Test NumberDetailAnalysisView"""
    print("Testing NumberDetailAnalysisView...")
    
    try:
        # Create request factory
        factory = RequestFactory()
        
        # Create GET request with number parameter
        request = factory.get('/results/number-analysis/?number=05')
        
        # Create view instance and call get method
        view = NumberDetailAnalysisView()
        response = view.get(request)
        
        print(f"Status code: {response.status_code}")
        print(f"Content type: {response.get('content-type', 'unknown')}")
        
        # Parse JSON response
        import json
        if hasattr(response, 'content'):
            try:
                content = json.loads(response.content.decode('utf-8'))
                print("Response JSON:")
                if content.get('success'):
                    print("✅ Success!")
                    analysis = content.get('analysis', {})
                    print(f"Number: {analysis.get('number')}")
                    print(f"Analysis date: {analysis.get('analysis_date')}")
                    print(f"Current gan days: {analysis.get('gan_analysis', {}).get('current_gan_days')}")
                else:
                    print(f"❌ Error: {content.get('error')}")
            except json.JSONDecodeError as e:
                print(f"❌ JSON decode error: {e}")
                print(f"Raw content: {response.content[:200]}")
        
        return response.status_code == 200
        
    except Exception as e:
        print(f"❌ Exception in NumberDetailAnalysisView: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_heatmap_view():
    """Test NumberFrequencyHeatmapView"""
    print("\nTesting NumberFrequencyHeatmapView...")
    
    try:
        # Create request factory
        factory = RequestFactory()
        
        # Create GET request with parameters
        request = factory.get('/results/frequency-heatmap/?period=30&type=frequency')
        
        # Create view instance and call get method
        view = NumberFrequencyHeatmapView()
        response = view.get(request)
        
        print(f"Status code: {response.status_code}")
        print(f"Content type: {response.get('content-type', 'unknown')}")
        
        # Parse JSON response
        import json
        if hasattr(response, 'content'):
            try:
                content = json.loads(response.content.decode('utf-8'))
                print("Response JSON keys:", list(content.keys()))
                if content.get('success'):
                    print("✅ Success!")
                    data = content.get('data', [])
                    print(f"Data points: {len(data)}")
                    if data:
                        print(f"First data point: {data[0]}")
                        print(f"Value range: {content.get('value_range')}")
                else:
                    print(f"❌ Error: {content.get('error')}")
            except json.JSONDecodeError as e:
                print(f"❌ JSON decode error: {e}")
                print(f"Raw content: {response.content[:200]}")
        
        return response.status_code == 200
        
    except Exception as e:
        print(f"❌ Exception in NumberFrequencyHeatmapView: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_frequency_service():
    """Test frequency analysis service directly"""
    print("\nTesting FrequencyAnalysisService directly...")
    
    try:
        from results.services.frequency_analysis_service import get_frequency_analysis_service
        
        service = get_frequency_analysis_service()
        print("✅ Service instantiated successfully")
        
        # Test single number analysis
        analysis = service.get_comprehensive_analysis('05')
        print("✅ Single analysis successful")
        print(f"Analysis keys: {list(analysis.keys())}")
        
        # Test batch analysis summary
        all_numbers = [f"{i:02d}" for i in range(10)]  # Test with first 10 numbers
        batch_analysis = service.get_batch_analysis_summary(all_numbers)
        print("✅ Batch analysis successful")
        print(f"Batch analysis keys: {list(batch_analysis.keys())}")
        print(f"Sample data for '05': {batch_analysis.get('05', {}).keys()}")
        
        return True
        
    except Exception as e:
        print(f"❌ Exception in FrequencyAnalysisService: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("=== API Views Testing ===")
    
    # Test service first
    service_ok = test_frequency_service()
    
    if service_ok:
        # Test API views
        analysis_ok = test_number_detail_analysis()
        heatmap_ok = test_heatmap_view()
        
        print(f"\n=== Results ===")
        print(f"Frequency Service: {'✅' if service_ok else '❌'}")
        print(f"Number Analysis API: {'✅' if analysis_ok else '❌'}")
        print(f"Heatmap API: {'✅' if heatmap_ok else '❌'}")
        
        if all([service_ok, analysis_ok, heatmap_ok]):
            print("\n🎉 All tests passed! APIs should work in browser.")
        else:
            print("\n⚠️  Some tests failed. Check the errors above.")
    else:
        print("\n❌ Service failed, skipping API tests.")
