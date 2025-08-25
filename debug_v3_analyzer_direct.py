#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
🔍 DEBUG V3 ANALYZER DIRECTLY
Test V3 analyzer without Django server to identify why no optimal numbers generated
"""

import sys
import os
from datetime import datetime, timedelta

# Add project paths
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'predictions_tracker'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'predictions_tracker', 'views_dir'))

try:
    from predictions_tracker.enhanced_method_analyzer_v3 import EnhancedMethodAnalyzerV3, ValidationConfig
    from predictions_tracker.views_dir.api_method_analysis_v3_integration import V2ToV3Adapter
    print("✅ Successfully imported V3 modules")
except ImportError as e:
    print(f"❌ Import error: {e}")
    sys.exit(1)


def debug_v3_analyzer():
    """Debug V3 analyzer directly"""
    print("🔍 Starting V3 Analyzer Direct Debug...")
    
    try:
        # ✅ 1. SETUP BASIC CONFIG
        analysis_date = datetime(2024, 12, 15)
        confidence_threshold = 0.2  # Very low threshold
        
        config = ValidationConfig(
            temporal_split_ratio=0.8,
            min_validation_days=14,
            confidence_threshold=confidence_threshold,
            stability_window=7,
        )
        
        print(f"📅 Analysis Date: {analysis_date}")
        print(f"🎯 Confidence Threshold: {confidence_threshold:.0%}")
        
        # ✅ 2. CREATE ANALYZER
        analyzer = EnhancedMethodAnalyzerV3(config)
        print("✅ V3 Analyzer created successfully")
        
        # ✅ 3. CREATE MINIMAL TEST DATA 
        print("🔄 Creating minimal test data...")
        
        # Create minimal V3 format data
        short_term_data = {
            'method_performance': {
                'TAN_SO_SO_DONG': {'hit_rate': 0.7, 'stability': 0.8, 'confidence': 0.85},
                'TAN_SO_TONG': {'hit_rate': 0.6, 'stability': 0.7, 'confidence': 0.75},
                'TAN_SO_DUOI': {'hit_rate': 0.65, 'stability': 0.75, 'confidence': 0.80},
                'TAN_SO_DAU': {'hit_rate': 0.55, 'stability': 0.65, 'confidence': 0.70},
                'PHAN_TICH_KHOANG_CACH': {'hit_rate': 0.5, 'stability': 0.6, 'confidence': 0.65},
            },
            'lottery_results': [
                {
                    'date': '2024-12-14',
                    'special': 12345,
                    'prizes': [67890, 11111, 22222, 33333, 44444, 55555, 66666, 77777]
                },
                {
                    'date': '2024-12-13', 
                    'special': 98765,
                    'prizes': [12345, 23456, 34567, 45678, 56789, 67890, 78901, 89012]
                }
            ]
        }
        
        long_term_data = short_term_data  # Use same for simplicity
        
        print(f"📊 Short-term methods: {len(short_term_data['method_performance'])}")
        print(f"📊 Lottery results: {len(short_term_data['lottery_results'])}")
        
        # ✅ 4. RUN V3 ANALYSIS
        print("🚀 Running V3 analysis...")
        v3_results = analyzer.analyze_with_true_forward_validation(
            analysis_date=analysis_date,
            short_term_data=short_term_data,
            long_term_data=long_term_data,
            target_hit_rate=0.5,
        )
        
        print("✅ V3 analysis completed")
        
        # ✅ 5. ANALYZE RESULTS
        print("\n📊 V3 ANALYSIS RESULTS:")
        print(f"Results keys: {list(v3_results.keys())}")
        
        selected_methods = v3_results.get('selected_methods', [])
        print(f"🎯 Selected methods count: {len(selected_methods)}")
        
        if selected_methods:
            print("🎯 Selected methods:")
            for i, method in enumerate(selected_methods[:5]):
                print(f"  {i+1}. {method.get('method_id', 'unknown')} - {method.get('robustness_score', 0):.3f}")
        else:
            print("❌ NO selected methods found!")
            
        # Check optimal methods
        optimal_methods = v3_results.get('optimal_methods', [])
        print(f"🎯 Optimal methods count: {len(optimal_methods)}")
        
        if optimal_methods:
            print("🎯 Optimal methods:")
            if isinstance(optimal_methods, dict):
                print(f"  Optimal methods type: dict with keys: {list(optimal_methods.keys())}")
                
                # Check selected_methods within optimal_methods
                selected_in_optimal = optimal_methods.get('selected_methods', [])
                print(f"  📊 Selected methods in optimal: {len(selected_in_optimal)}")
                
                if selected_in_optimal:
                    print("  🎯 Top selected methods in optimal:")
                    for i, method in enumerate(selected_in_optimal[:5]):
                        if isinstance(method, dict):
                            print(f"    {i+1}. {method.get('method_id', 'unknown')} - score: {method.get('robustness_score', 0):.3f}")
                        else:
                            print(f"    {i+1}. {method}")
                            
                # Check selection_summary
                selection_summary = optimal_methods.get('selection_summary', {})
                if selection_summary:
                    print(f"  📋 Selection summary: {selection_summary}")
                    
            elif isinstance(optimal_methods, list):
                for i, method in enumerate(optimal_methods[:5]):
                    if isinstance(method, dict):
                        print(f"  {i+1}. {method.get('method_id', 'unknown')} - {method.get('robustness_score', 0):.3f}")
                    else:
                        print(f"  {i+1}. {method}")
            else:
                print(f"  Optimal methods type: {type(optimal_methods)}")
        else:
            print("❌ NO optimal methods found!")
            
        # ✅ 6. TRY DIRECT OPTIMAL NUMBERS GENERATION
        print("\n🔍 Testing optimal numbers generation...")
        try:
            # Extract actual selected methods for number generation
            selected_methods_for_numbers = []
            
            if isinstance(optimal_methods, dict):
                selected_methods_for_numbers = optimal_methods.get('selected_methods', [])
            elif isinstance(optimal_methods, list):
                selected_methods_for_numbers = optimal_methods
                
            print(f"🎯 Methods available for number generation: {len(selected_methods_for_numbers)}")
            
            if selected_methods_for_numbers and len(selected_methods_for_numbers) > 0:
                print("✅ Found methods, trying to generate optimal numbers...")
                
                # Check first method structure
                first_method = selected_methods_for_numbers[0]
                print(f"First method structure: {first_method}")
                
                # Try to extract numbers like the API does
                optimal_numbers = []
                for method in selected_methods_for_numbers[:10]:  # Take top 10
                    if isinstance(method, dict) and 'method_id' in method:
                        method_id = method['method_id']
                        robustness = method.get('robustness_score', 0)
                        
                        # Extract numbers from method_id and robustness
                        numbers = []
                        
                        # From method_id hash
                        method_hash = abs(hash(method_id)) % 100
                        if 1 <= method_hash <= 99:
                            numbers.append(method_hash)
                            
                        # From robustness score
                        robustness_num = int(robustness * 100) % 100
                        if 1 <= robustness_num <= 99:
                            numbers.append(robustness_num)
                            
                        optimal_numbers.extend(numbers)
                
                # Remove duplicates and ensure range 1-99
                optimal_numbers = list(set([n for n in optimal_numbers if 1 <= n <= 99]))
                optimal_numbers.sort()
                
                print(f"🎯 Generated optimal numbers: {optimal_numbers}")
                print(f"🎯 Generated count: {len(optimal_numbers)}")
                
                if len(optimal_numbers) >= 6:
                    print("✅ Successfully generated sufficient optimal numbers!")
                    return optimal_numbers
                else:
                    print("❌ Insufficient optimal numbers generated")
                    return []
                    
            else:
                print("❌ No methods available for number generation")
                return []
                
        except Exception as e:
            print(f"❌ Error generating optimal numbers: {e}")
            import traceback
            traceback.print_exc()
            return []
            
        return v3_results
        
    except Exception as e:
        print(f"❌ Error in V3 analysis: {e}")
        import traceback
        traceback.print_exc()
        return None


if __name__ == "__main__":
    debug_v3_analyzer()
