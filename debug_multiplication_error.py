#!/usr/bin/env python3
"""
Debug script to identify the multiplication error
"""

import os
import sys
import traceback

# Add project root to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Set Django settings
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "xoso_crawler.settings")

import django
django.setup()

from analytic_frequence.ultimate_prediction_system import UltimatePredictionSystem

def test_ultimate_prediction():
    """Test the ultimate prediction system"""
    print("🔍 Testing Ultimate Prediction System...")
    
    try:
        # Create system
        system = UltimatePredictionSystem()
        print("✅ System created successfully")
        
        # Test with sample data
        lottery_numbers = [12, 34, 56, 78, 90, 123]
        print(f"📊 Testing with data: {lottery_numbers}")
        
        # Run prediction
        result = system.ultimate_prediction_analysis(lottery_numbers)
        print(f"✅ Prediction completed: {type(result)}")
        print(f"📄 Result keys: {result.keys() if isinstance(result, dict) else 'Not a dict'}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        print("🔍 Full traceback:")
        traceback.print_exc()

if __name__ == "__main__":
    test_ultimate_prediction()
