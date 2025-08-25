#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
🔧 SIMPLE DEBUG: Find the float conversion error
"""

import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'xoso_crawler.settings')
sys.path.append('.')

django.setup()
print("✅ Django setup successful")

# Test 1: Ultimate Prediction System Result Structure
print("\n🔍 Testing Ultimate Prediction System...")
try:
    from analytic_frequence.ultimate_prediction_system import create_ultimate_prediction_system
    
    ultimate_system = create_ultimate_prediction_system()
    test_numbers = [1, 5, 10, 15, 20]  # Simple test data
    
    result = ultimate_system.ultimate_prediction_analysis(
        lottery_numbers=test_numbers,
        prediction_horizon=3,
        include_explanations=True,
    )
    
    print(f"✅ Result type: {type(result)}")
    print(f"📋 Result attributes: {[attr for attr in dir(result) if not attr.startswith('_')]}")
    
    # Check specific problematic attributes
    problematic_attrs = ['confidence_score', 'accuracy_boost', 'processing_time_ms']
    for attr in problematic_attrs:
        if hasattr(result, attr):
            value = getattr(result, attr)
            print(f"  {attr}: {type(value)} = {value}")
            
    # Check time_crystal_patterns
    if hasattr(result, 'time_crystal_patterns'):
        tcp = result.time_crystal_patterns
        print(f"  time_crystal_patterns: {type(tcp)}")
        if isinstance(tcp, dict):
            print(f"    Keys: {list(tcp.keys())}")
            
except Exception as e:
    print(f"❌ Ultimate system error: {e}")
    import traceback
    traceback.print_exc()

# Test 2: Check template_views safe_float function
print("\n🧪 Testing safe_float function...")
def safe_float(value, default=0.0):
    """Safely convert value to float"""
    try:
        if isinstance(value, (dict, list)):
            print(f"  🚨 Dict/List detected: {type(value)} = {value}")
            return default
        return float(value) if value is not None else default
    except (ValueError, TypeError) as e:
        print(f"  ⚠️ Conversion error: {e}")
        return default

# Test problematic values
test_values = [
    ("Good float", 3.14),
    ("Dict (bad)", {"key": "value"}),
    ("List (bad)", [1, 2, 3]),
]

for desc, val in test_values:
    result = safe_float(val)
    print(f"  {desc}: {type(val)} -> {result}")

print("\n🏁 Simple debug completed")
