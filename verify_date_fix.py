#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
🧪 SIMPLE DATE FIX TEST
Quick verification of date-specific fixes
"""

import os
import sys
import django
from datetime import date

# Django setup
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "xoso_crawler.settings")
sys.path.append(".")

try:
    django.setup()
    print("✅ Django setup successful")
    
    # Test date-specific data integration
    from analytic_frequence.data_integration_service import RealDataIntegrationService
    
    service = RealDataIntegrationService()
    
    print("\n🔍 Testing date-specific data integration...")
    
    # Test without date
    data1 = service.get_enhanced_lottery_input()
    print(f"📊 Default data: {len(data1['lottery_numbers'])} numbers")
    print(f"🔗 Data source: {data1['data_source']}")
    
    # Test with specific date
    test_date = date(2025, 8, 12)
    data2 = service.get_enhanced_lottery_input(prediction_date=test_date)
    print(f"📅 Date-specific data: {len(data2['lottery_numbers'])} numbers")
    print(f"🔗 Data source: {data2['data_source']}")
    print(f"📈 Analysis date: {data2.get('analysis_date')}")
    
    # Compare
    if data1["data_source"] != data2["data_source"]:
        print("✅ SUCCESS: Different data sources for different dates!")
    else:
        print("⚠️ ISSUE: Same data source")
        
    # Test sample numbers
    sample1 = data1["lottery_numbers"][:5]
    sample2 = data2["lottery_numbers"][:5]
    print(f"🔢 Default sample: {sample1}")
    print(f"🔢 Date-specific sample: {sample2}")
    
    if sample1 != sample2:
        print("✅ SUCCESS: Different number samples!")
    else:
        print("⚠️ ISSUE: Same number samples")
        
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
