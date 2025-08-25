#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
🧪 DIRECT TEST: V3 Optimal Numbers Generation
Test updated generate_v3_optimal_numbers function directly
"""

import sys
import os
from datetime import datetime

# Add project paths
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'predictions_tracker', 'views_dir'))

# Mock V3 raw results for testing
mock_v3_results = {
    'ensemble_results': {
        'TAN_SO_SO_DONG': {
            'ensemble_score': {'expected_hit_rate': 0.45},
            'reliability_score': 0.35
        },
        'TAN_SO_TONG': {
            'ensemble_score': {'expected_hit_rate': 0.38},
            'reliability_score': 0.42
        },
        'TAN_SO_DUOI': {
            'ensemble_score': {'expected_hit_rate': 0.52},
            'reliability_score': 0.28
        },
        'TAN_SO_DAU': {
            'ensemble_score': {'expected_hit_rate': 0.31},
            'reliability_score': 0.47
        },
        'PHAN_TICH_KHOANG_CACH': {
            'ensemble_score': {'expected_hit_rate': 0.29},
            'reliability_score': 0.33
        }
    },
    'uncertainty_analysis': {
        'method_uncertainties': {
            'TAN_SO_SO_DONG': {'confidence_level': 'medium'},
            'TAN_SO_TONG': {'confidence_level': 'medium'},
            'TAN_SO_DUOI': {'confidence_level': 'low'},
            'TAN_SO_DAU': {'confidence_level': 'medium'},
            'PHAN_TICH_KHOANG_CACH': {'confidence_level': 'low'}
        }
    }
}

def test_direct_generation():
    """Test optimal numbers generation directly"""
    print("🧪 Testing Direct V3 Optimal Numbers Generation...")
    
    try:
        # Import the updated function
        from api_method_analysis_v3_integration import generate_v3_optimal_numbers, _generate_from_v3_insights
        
        # Test 1: Empty selected methods (should trigger insights approach)
        print("\n🔍 Test 1: Empty selected methods -> Should use V3 insights")
        selected_methods = []
        optimal_methods = {}
        
        result = generate_v3_optimal_numbers(selected_methods, optimal_methods, mock_v3_results)
        print(f"📊 Generated numbers: {result}")
        print(f"📊 Count: {len(result)}")
        
        if len(result) >= 6:
            print("✅ SUCCESS: Generated sufficient optimal numbers from V3 insights!")
            return True
        else:
            print("❌ FAILED: Insufficient numbers generated")
            
        # Test 2: Direct insights function
        print("\n🔍 Test 2: Direct insights generation")
        direct_result = _generate_from_v3_insights(mock_v3_results)
        print(f"📊 Direct insights numbers: {direct_result}")
        print(f"📊 Count: {len(direct_result)}")
        
        if len(direct_result) >= 6:
            print("✅ SUCCESS: Direct insights generation works!")
            return True
        else:
            print("❌ FAILED: Direct insights insufficient")
            
        return False
        
    except Exception as e:
        print(f"❌ Error in direct test: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_direct_generation()
