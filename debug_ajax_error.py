#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
🔧 DEBUG AJAX ERROR: Investigate the 'dict' float conversion error
"""

import os
import sys
import django
import json
import logging
from datetime import datetime, date

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'xoso_crawler.settings')
sys.path.append('.')

try:
    django.setup()
    print("✅ Django setup successful")
except Exception as e:
    print(f"❌ Django setup failed: {e}")
    exit(1)

# Configure logging to see details
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def debug_ultimate_system_result():
    """Test the Ultimate Prediction System directly to see result structure"""
    print("\n" + "="*70)
    print("🔍 DEBUGGING ULTIMATE PREDICTION SYSTEM RESULT STRUCTURE")
    print("="*70)
    
    try:
        from analytic_frequence.ultimate_prediction_system import create_ultimate_prediction_system
        from analytic_frequence.data_integration_service import RealDataIntegrationService
        
        # Initialize system
        ultimate_system = create_ultimate_prediction_system()
        data_service = RealDataIntegrationService()
        
        # Get test data
        test_date = date(2025, 8, 12)
        real_data = data_service.get_enhanced_lottery_input(prediction_date=test_date)
        lottery_numbers = real_data.get("lottery_numbers", [])[:20]  # Small sample
        
        print(f"📊 Testing with {len(lottery_numbers)} numbers")
        print(f"📝 Sample numbers: {lottery_numbers[:10]}")
        
        # Perform prediction
        print("\n🔮 Running prediction analysis...")
        result = ultimate_system.ultimate_prediction_analysis(
            lottery_numbers=lottery_numbers,
            prediction_horizon=5,
            include_explanations=True,
        )
        
        print(f"✅ Prediction completed")
        print(f"📋 Result type: {type(result)}")
        print(f"📋 Result attributes: {dir(result)}")
        
        # Check each attribute type
        attributes_to_check = [
            'confidence_score', 'accuracy_boost', 'processing_time_ms', 
            'memory_usage_mb', 'information_entropy', 'quantum_entanglement_score',
            'consciousness_level', 'data_quality_score', 'robustness_score'
        ]
        
        print("\n📊 ATTRIBUTE TYPE ANALYSIS:")
        print("-" * 50)
        for attr in attributes_to_check:
            if hasattr(result, attr):
                value = getattr(result, attr)
                print(f"  {attr}: {type(value)} = {value}")
            else:
                print(f"  {attr}: NOT FOUND")
        
        # Check time_crystal_patterns specifically
        print("\n🔮 TIME CRYSTAL PATTERNS ANALYSIS:")
        print("-" * 50)
        if hasattr(result, 'time_crystal_patterns'):
            tcp = result.time_crystal_patterns
            print(f"  time_crystal_patterns: {type(tcp)} = {tcp}")
            if isinstance(tcp, dict):
                for key, value in tcp.items():
                    print(f"    {key}: {type(value)} = {value}")
        else:
            print("  time_crystal_patterns: NOT FOUND")
            
        # Check contributing_factors
        print("\n🔍 CONTRIBUTING FACTORS ANALYSIS:")
        print("-" * 50)
        if hasattr(result, 'contributing_factors'):
            cf = result.contributing_factors
            print(f"  contributing_factors: {type(cf)} = {cf}")
            if isinstance(cf, dict):
                for key, value in cf.items():
                    print(f"    {key}: {type(value)} = {repr(value)[:100]}")
        else:
            print("  contributing_factors: NOT FOUND")
            
        # Check primary_predictions
        print("\n🎯 PRIMARY PREDICTIONS ANALYSIS:")
        print("-" * 50)
        if hasattr(result, 'primary_predictions'):
            pp = result.primary_predictions
            print(f"  primary_predictions: {type(pp)} = {len(pp) if isinstance(pp, list) else pp}")
            if isinstance(pp, list) and len(pp) > 0:
                for i, pred in enumerate(pp[:3]):
                    print(f"    Prediction {i+1}: {type(pred)} = {pred}")
        else:
            print("  primary_predictions: NOT FOUND")
            
        return result
        
    except Exception as e:
        print(f"❌ Error in ultimate system debug: {e}")
        import traceback
        traceback.print_exc()
        return None

def test_safe_float_function():
    """Test the safe_float function with various inputs"""
    print("\n" + "="*70)
    print("🧪 TESTING SAFE_FLOAT FUNCTION")
    print("="*70)
    
    def safe_float(value, default=0.0):
        """Safely convert value to float"""
        try:
            if isinstance(value, (dict, list)):
                return default
            return float(value) if value is not None else default
        except (ValueError, TypeError):
            return default
    
    test_cases = [
        ("Valid float", 3.14),
        ("Valid int", 42),
        ("Valid string", "3.14"),
        ("Dict (should trigger error)", {"key": "value"}),
        ("List (should trigger error)", [1, 2, 3]),
        ("None", None),
        ("Invalid string", "not_a_number"),
        ("Empty string", ""),
    ]
    
    for description, test_value in test_cases:
        result = safe_float(test_value)
        print(f"  {description}: {type(test_value)} {test_value} -> {result}")

def simulate_ajax_call():
    """Simulate the AJAX call to reproduce the error"""
    print("\n" + "="*70) 
    print("🌐 SIMULATING AJAX CALL")
    print("="*70)
    
    try:
        from django.test import Client
        from django.conf import settings
        
        # Add testserver to ALLOWED_HOSTS temporarily
        original_hosts = settings.ALLOWED_HOSTS
        if 'testserver' not in settings.ALLOWED_HOSTS:
            settings.ALLOWED_HOSTS = settings.ALLOWED_HOSTS + ['testserver']
        
        client = Client()
        
        # Prepare test data
        test_data = {
            "prediction_date": "2025-08-12",
            "prediction_horizon": 5,
            "use_real_data": True
        }
        
        print(f"📤 Sending test data: {test_data}")
        
        # Make the request
        response = client.post(
            '/analytic-frequence/ajax-prediction/',
            data=json.dumps(test_data),
            content_type='application/json'
        )
        
        print(f"📥 Response status: {response.status_code}")
        
        if response.status_code == 200:
            response_data = response.json()
            print(f"✅ Success: {response_data.get('success')}")
            if response_data.get('success'):
                pred_data = response_data.get('prediction_data', {})
                print(f"📊 Predictions: {len(pred_data.get('predictions', []))}")
                print(f"🎯 Confidence: {pred_data.get('confidence_score')}")
                print(f"🔗 Data source: {pred_data.get('data_source')}")
            else:
                print(f"❌ Error: {response_data.get('error')}")
        else:
            print(f"❌ HTTP Error: {response.status_code}")
            print(f"📝 Response content: {response.content.decode()[:500]}")
            
        # Restore original ALLOWED_HOSTS
        settings.ALLOWED_HOSTS = original_hosts
        
    except Exception as e:
        print(f"❌ AJAX simulation failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    print("🚀 DEBUGGING AJAX FLOAT CONVERSION ERROR")
    print("="*70)
    
    # Run all debug functions
    debug_ultimate_system_result()
    test_safe_float_function()
    simulate_ajax_call()
    
    print("\n🏁 DEBUG COMPLETED")
