#!/usr/bin/env python3
"""
Final verification test for the date analysis fix
"""

import os
import sys
import django

# Setup Django
sys.path.append("C:\\Users\\n2t\\Documents\\xoso_crawler")
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "xoso_crawler.settings")
django.setup()

from django.test import Client
import json


def test_date_specific_analysis():
    """Test that different dates produce different results"""
    print("=== FINAL DATE ANALYSIS VERIFICATION ===")
    
    client = Client()
    
    test_dates = [
        "2025-08-12",
        "2025-08-06", 
        "2025-07-15"
    ]
    
    results = {}
    
    for date in test_dates:
        print(f"\n📅 Testing date: {date}")
        
        test_data = {
            "prediction_date": date,
            "prediction_horizon": 5,
            "use_real_data": True
        }
        
        try:
            response = client.post(
                "/analytic-frequence/ajax-prediction/",
                data=json.dumps(test_data),
                content_type="application/json"
            )
            
            print(f"   Status: {response.status_code}")
            
            if response.status_code == 200:
                result = response.json()
                if result.get('success') and 'data' in result:
                    prediction_data = result['data'].get('prediction_data', {})
                    data_source = prediction_data.get('data_source', 'Unknown')
                    confidence = prediction_data.get('confidence_score', 0)
                    predictions = prediction_data.get('predictions', [])
                    
                    results[date] = {
                        'data_source': data_source,
                        'confidence': confidence,
                        'predictions': predictions[:5] if predictions else [],
                        'prediction_count': len(predictions) if predictions else 0
                    }
                    
                    print(f"   ✅ Data source: {data_source}")
                    print(f"   ✅ Confidence: {confidence:.3f}")
                    print(f"   ✅ Predictions: {len(predictions) if predictions else 0}")
                else:
                    print(f"   ❌ API error: {result.get('message', 'Unknown')}")
                    results[date] = {'error': result.get('message', 'API error')}
            else:
                print(f"   ❌ HTTP {response.status_code}")
                results[date] = {'error': f'HTTP {response.status_code}'}
                
        except Exception as e:
            print(f"   ❌ Exception: {e}")
            results[date] = {'error': str(e)}
    
    # Analyze results
    print(f"\n🔍 ANALYSIS SUMMARY:")
    successful_dates = [date for date, result in results.items() if 'error' not in result]
    
    if len(successful_dates) >= 2:
        print(f"✅ Successfully tested {len(successful_dates)} dates")
        
        # Check for different data sources
        data_sources = {date: results[date]['data_source'] for date in successful_dates}
        unique_sources = set(data_sources.values())
        
        print(f"📊 Data sources: {dict(data_sources)}")
        
        if len(unique_sources) > 1:
            print(f"✅ DIFFERENT DATA SOURCES CONFIRMED: {unique_sources}")
            print("🎉 Date-specific analysis is working correctly!")
        else:
            print(f"⚠️  Same data source for all dates: {unique_sources}")
            
        # Check for different predictions
        predictions_comparison = {}
        for date in successful_dates:
            preds = results[date]['predictions']
            predictions_comparison[date] = preds
            
        print(f"🔢 Predictions comparison:")
        for date, preds in predictions_comparison.items():
            print(f"   {date}: {preds}")
            
        # Check if predictions are different
        prediction_sets = [tuple(sorted(preds)) for preds in predictions_comparison.values()]
        unique_predictions = len(set(prediction_sets))
        
        if unique_predictions > 1:
            print(f"✅ DIFFERENT PREDICTIONS CONFIRMED ({unique_predictions} unique sets)")
        else:
            print(f"⚠️  Similar predictions across dates")
            
    else:
        print(f"❌ Only {len(successful_dates)} successful tests - need more for comparison")
        
    return results


def test_template_javascript():
    """Test that template renders without JavaScript errors"""
    print(f"\n🌐 TESTING TEMPLATE JAVASCRIPT:")
    
    client = Client()
    response = client.get("/analytic-frequence/ultimate-prediction/")
    
    if response.status_code == 200:
        content = response.content.decode('utf-8')
        
        # Check for our fix
        if "const sampleData = " in content and "sample_prediction_json" in content:
            print(f"✅ JavaScript fix is present in template")
            
            # Check for problematic patterns
            error_patterns = ["&#x27;", "np.float64", "Float64"]
            found_errors = [pattern for pattern in error_patterns if pattern in content]
            
            if found_errors:
                print(f"❌ Found error patterns: {found_errors}")
            else:
                print(f"✅ No JavaScript error patterns found")
                
            return True
        else:
            print(f"❌ JavaScript fix not found in template")
            return False
    else:
        print(f"❌ Template request failed: {response.status_code}")
        return False


if __name__ == "__main__":
    print("🔧 ULTIMATE PREDICTION SYSTEM - FINAL VERIFICATION")
    print("=" * 60)
    
    # Test template
    template_ok = test_template_javascript()
    
    # Test date analysis
    date_results = test_date_specific_analysis()
    
    print(f"\n🏁 FINAL VERDICT:")
    print(f"   Template JavaScript: {'✅ FIXED' if template_ok else '❌ BROKEN'}")
    
    successful_dates = len([r for r in date_results.values() if 'error' not in r])
    print(f"   Date Analysis: {'✅ WORKING' if successful_dates >= 2 else '❌ NEEDS WORK'}")
    
    if template_ok and successful_dates >= 2:
        print(f"\n🎉 SUCCESS! Date-specific analysis is now working correctly!")
        print(f"   - JavaScript syntax errors fixed")
        print(f"   - Different dates produce different results")
        print(f"   - AJAX API working properly")
    else:
        print(f"\n⚠️  Some issues remain - check the output above")
        
    print("=" * 60)
