#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
🔍 DEEP DEBUG: DATE-SPECIFIC ANALYSIS INVESTIGATION
Kiểm tra chi tiết vấn đề filtering theo ngày
"""

import os
import sys
import django
from datetime import date, datetime, timedelta
import json

# Django setup
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "xoso_crawler.settings")
sys.path.append(".")

try:
    django.setup()
    print("✅ Django setup successful")
except Exception as e:
    print(f"❌ Django setup failed: {e}")
    sys.exit(1)

# Import after Django setup
from analytic_frequence.data_integration_service import RealDataIntegrationService
from results.models import NumberFrequencyStats

def debug_numberfrequencystats_filtering():
    """Debug NumberFrequencyStats filtering step by step"""
    print("\n" + "="*80)
    print("🔍 DEEP DEBUG: NumberFrequencyStats Filtering")
    print("="*80)
    
    # Test dates
    test_dates = [
        date(2025, 8, 12),
        date(2025, 8, 6), 
        date(2025, 7, 15),
        date(2024, 12, 1)
    ]
    
    results = {}
    
    for test_date in test_dates:
        print(f"\n📅 TESTING DATE: {test_date}")
        print("-" * 50)
        
        # Calculate date range (30 days before test_date)
        start_date = test_date - timedelta(days=30)
        end_date = test_date
        
        print(f"🗓️ Date range: {start_date} to {end_date}")
        
        # Manual query to see what data is available
        try:
            # Query NumberFrequencyStats directly
            frequency_stats = NumberFrequencyStats.objects.filter(
                date__range=[start_date, end_date]
            ).order_by("-date")
            
            count = frequency_stats.count()
            print(f"📊 Total records in range: {count}")
            
            if count > 0:
                # Get distinct dates in this range
                distinct_dates = frequency_stats.values_list('date', flat=True).distinct()
                date_counts = {}
                for distinct_date in distinct_dates:
                    date_count = frequency_stats.filter(date=distinct_date).count()
                    date_counts[distinct_date] = date_count
                
                print(f"📈 Dates with data in range:")
                for date_key, date_count in sorted(date_counts.items(), reverse=True)[:10]:
                    print(f"   - {date_key}: {date_count} records")
                
                # Extract actual numbers
                real_numbers = []
                for stat in frequency_stats[:100]:  # Limit for debugging
                    try:
                        number = int(stat.number)
                        real_numbers.append(number)
                    except (ValueError, TypeError):
                        continue
                
                print(f"🔢 Extracted {len(real_numbers)} numbers")
                print(f"📝 Sample numbers: {real_numbers[:10]}")
                print(f"📝 Unique numbers: {len(set(real_numbers))}")
                
                # Store for comparison
                results[test_date.isoformat()] = {
                    "total_records": count,
                    "extracted_numbers": len(real_numbers),
                    "sample_numbers": real_numbers[:10],
                    "unique_numbers": len(set(real_numbers)),
                    "date_range": f"{start_date} to {end_date}",
                    "distinct_dates": len(distinct_dates)
                }
            else:
                print("❌ No data found in this range")
                results[test_date.isoformat()] = {
                    "total_records": 0,
                    "error": "No data in range"
                }
                
        except Exception as e:
            print(f"❌ Error querying data: {e}")
            results[test_date.isoformat()] = {
                "error": str(e)
            }
    
    # Compare results
    print(f"\n🔍 COMPARISON RESULTS:")
    print("="*50)
    
    unique_patterns = set()
    for date_key, result in results.items():
        if "sample_numbers" in result:
            pattern = str(result["sample_numbers"])
            unique_patterns.add(pattern)
            print(f"{date_key}: {result['extracted_numbers']} numbers, "
                  f"{result['unique_numbers']} unique, "
                  f"{result['distinct_dates']} dates")
    
    print(f"\n📊 Unique number patterns: {len(unique_patterns)}")
    if len(unique_patterns) > 1:
        print("✅ GOOD: Different dates produce different number sets!")
    else:
        print("⚠️ ISSUE: All dates produce same number sets")
    
    return results

def debug_data_integration_service():
    """Debug RealDataIntegrationService step by step"""
    print("\n" + "="*80)
    print("🔍 DEEP DEBUG: RealDataIntegrationService")
    print("="*80)
    
    service = RealDataIntegrationService()
    
    test_dates = [
        date(2025, 8, 12),
        date(2025, 8, 6), 
        date(2025, 7, 15),
        None  # Default case
    ]
    
    results = {}
    
    for test_date in test_dates:
        date_str = test_date.isoformat() if test_date else "default"
        print(f"\n📅 TESTING: {date_str}")
        print("-" * 40)
        
        try:
            # Test get_real_lottery_numbers directly
            if test_date:
                start_date = test_date - timedelta(days=30)
                end_date = test_date
                real_numbers = service.get_real_lottery_numbers(start_date, end_date)
                print(f"🔢 get_real_lottery_numbers({start_date}, {end_date}): {len(real_numbers)} numbers")
            else:
                real_numbers = service.get_real_lottery_numbers()
                print(f"🔢 get_real_lottery_numbers(): {len(real_numbers)} numbers")
            
            print(f"📝 Sample: {real_numbers[:10]}")
            print(f"📝 Unique: {len(set(real_numbers))}")
            
            # Test get_enhanced_lottery_input
            enhanced_data = service.get_enhanced_lottery_input(
                include_patterns=True,
                include_recent=True,
                prediction_date=test_date
            )
            
            enhanced_numbers = enhanced_data.get("lottery_numbers", [])
            data_source = enhanced_data.get("data_source", "unknown")
            analysis_date = enhanced_data.get("analysis_date")
            
            print(f"🎯 Enhanced input: {len(enhanced_numbers)} numbers")
            print(f"🔗 Data source: {data_source}")
            print(f"📅 Analysis date: {analysis_date}")
            print(f"📝 Enhanced sample: {enhanced_numbers[:10]}")
            
            results[date_str] = {
                "real_numbers_count": len(real_numbers),
                "real_numbers_sample": real_numbers[:10],
                "enhanced_numbers_count": len(enhanced_numbers),
                "enhanced_numbers_sample": enhanced_numbers[:10],
                "data_source": data_source,
                "analysis_date": analysis_date
            }
            
        except Exception as e:
            print(f"❌ Error: {e}")
            results[date_str] = {"error": str(e)}
    
    # Compare results
    print(f"\n🔍 SERVICE COMPARISON:")
    print("="*50)
    
    unique_sources = set()
    unique_samples = set()
    
    for date_str, result in results.items():
        if "data_source" in result:
            unique_sources.add(result["data_source"])
            unique_samples.add(str(result["enhanced_numbers_sample"]))
            print(f"{date_str}: {result['enhanced_numbers_count']} numbers, "
                  f"source: {result['data_source']}")
    
    print(f"\n📊 Unique data sources: {len(unique_sources)}")
    print(f"📊 Unique number samples: {len(unique_samples)}")
    
    if len(unique_sources) > 1:
        print("✅ EXCELLENT: Data sources differ by date!")
    else:
        print("⚠️ ISSUE: All data sources are the same")
        
    if len(unique_samples) > 1:
        print("✅ EXCELLENT: Number samples differ by date!")
    else:
        print("⚠️ ISSUE: All number samples are the same")
    
    return results

def debug_ajax_api_simulation():
    """Simulate AJAX API calls with different dates"""
    print("\n" + "="*80)
    print("🔍 DEEP DEBUG: AJAX API Simulation")
    print("="*80)
    
    from django.test import Client
    import json
    
    client = Client()
    
    test_dates = [
        "2025-08-12",
        "2025-08-06",
        "2025-07-15",
        "2024-12-01"
    ]
    
    results = {}
    
    for test_date in test_dates:
        print(f"\n📅 TESTING AJAX: {test_date}")
        print("-" * 40)
        
        try:
            # Simulate AJAX request
            test_data = {
                "prediction_date": test_date,
                "prediction_horizon": 5,
                "use_real_data": True
            }
            
            response = client.post(
                '/analytic-frequence/ajax-prediction/',
                data=json.dumps(test_data),
                content_type='application/json'
            )
            
            print(f"📡 Response status: {response.status_code}")
            
            if response.status_code == 200:
                try:
                    data = json.loads(response.content)
                    
                    if data.get("success"):
                        prediction_data = data.get("prediction_data", {})
                        
                        input_count = prediction_data.get("input_count", 0)
                        data_source = prediction_data.get("data_source", "unknown")
                        predictions = prediction_data.get("predictions", [])
                        prediction_date = prediction_data.get("prediction_date")
                        
                        print(f"✅ Success: {input_count} input numbers")
                        print(f"🔗 Data source: {data_source}")
                        print(f"📅 Prediction date: {prediction_date}")
                        print(f"🎯 Predictions: {[p.get('number') for p in predictions[:5]]}")
                        
                        results[test_date] = {
                            "input_count": input_count,
                            "data_source": data_source,
                            "prediction_date": prediction_date,
                            "predictions": [p.get('number') for p in predictions[:5]],
                            "success": True
                        }
                    else:
                        error = data.get("error", "Unknown error")
                        print(f"❌ API Error: {error}")
                        results[test_date] = {"error": error, "success": False}
                        
                except json.JSONDecodeError as e:
                    print(f"❌ JSON decode error: {e}")
                    print(f"📄 Raw response: {response.content[:200]}")
                    results[test_date] = {"error": f"JSON decode: {e}", "success": False}
                    
            else:
                print(f"❌ HTTP error: {response.status_code}")
                print(f"📄 Response: {response.content[:200]}")
                results[test_date] = {"error": f"HTTP {response.status_code}", "success": False}
                
        except Exception as e:
            print(f"❌ Request error: {e}")
            results[test_date] = {"error": str(e), "success": False}
    
    # Compare AJAX results
    print(f"\n🔍 AJAX COMPARISON:")
    print("="*50)
    
    successful_results = {k: v for k, v in results.items() if v.get("success")}
    
    if successful_results:
        unique_sources = set(r["data_source"] for r in successful_results.values())
        unique_predictions = set(str(r["predictions"]) for r in successful_results.values())
        
        for test_date, result in successful_results.items():
            print(f"{test_date}: {result['input_count']} inputs, "
                  f"source: {result['data_source']}, "
                  f"predictions: {result['predictions']}")
        
        print(f"\n📊 Unique data sources: {len(unique_sources)}")
        print(f"📊 Unique prediction sets: {len(unique_predictions)}")
        
        if len(unique_sources) > 1:
            print("✅ EXCELLENT: AJAX data sources differ by date!")
        else:
            print("⚠️ ISSUE: AJAX all data sources same")
            
        if len(unique_predictions) > 1:
            print("✅ EXCELLENT: AJAX predictions differ by date!")
        else:
            print("⚠️ ISSUE: AJAX all predictions same")
    else:
        print("❌ No successful AJAX responses to compare")
    
    return results

if __name__ == "__main__":
    print("🚀 ULTIMATE DEEP DEBUG: DATE-SPECIFIC ANALYSIS")
    print("="*80)
    
    try:
        # Test 1: NumberFrequencyStats direct queries
        nfs_results = debug_numberfrequencystats_filtering()
        
        # Test 2: RealDataIntegrationService
        service_results = debug_data_integration_service()
        
        # Test 3: AJAX API simulation
        ajax_results = debug_ajax_api_simulation()
        
        print("\n" + "="*80)
        print("🏁 SUMMARY & RECOMMENDATIONS")
        print("="*80)
        
        # Analysis
        print("\n📋 ANALYSIS:")
        print("-" * 30)
        
        # Check NumberFrequencyStats
        nfs_success = len([r for r in nfs_results.values() if "sample_numbers" in r]) > 0
        nfs_variation = len(set(str(r.get("sample_numbers", [])) for r in nfs_results.values() if "sample_numbers" in r)) > 1
        
        print(f"✅ NumberFrequencyStats data available: {nfs_success}")
        print(f"{'✅' if nfs_variation else '⚠️'} NumberFrequencyStats shows variation: {nfs_variation}")
        
        # Check Service
        service_success = len([r for r in service_results.values() if "data_source" in r]) > 0
        service_variation = len(set(r.get("data_source", "") for r in service_results.values() if "data_source" in r)) > 1
        
        print(f"✅ RealDataIntegrationService working: {service_success}")
        print(f"{'✅' if service_variation else '⚠️'} Service shows data source variation: {service_variation}")
        
        # Check AJAX
        ajax_success = len([r for r in ajax_results.values() if r.get("success")]) > 0
        ajax_variation = len(set(str(r.get("predictions", [])) for r in ajax_results.values() if r.get("success"))) > 1
        
        print(f"{'✅' if ajax_success else '❌'} AJAX API working: {ajax_success}")
        print(f"{'✅' if ajax_variation else '⚠️'} AJAX shows prediction variation: {ajax_variation}")
        
        print("\n🎯 RECOMMENDATIONS:")
        print("-" * 30)
        
        if not nfs_variation:
            print("🔧 FIX NEEDED: NumberFrequencyStats filtering logic")
        if not service_variation:
            print("🔧 FIX NEEDED: RealDataIntegrationService date handling")
        if not ajax_success:
            print("🔧 FIX NEEDED: AJAX API error handling")
        if not ajax_variation:
            print("🔧 FIX NEEDED: End-to-end date-specific prediction pipeline")
            
        if nfs_variation and service_variation and ajax_variation:
            print("🎉 SUCCESS: All components working correctly!")
        
    except Exception as e:
        print(f"❌ Debug failed: {e}")
        import traceback
        traceback.print_exc()
