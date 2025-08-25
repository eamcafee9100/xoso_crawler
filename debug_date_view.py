#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
🔧 DEBUG VIEW: Create a debug view to test date analysis
"""

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from datetime import date, datetime
import json

from analytic_frequence.data_integration_service import RealDataIntegrationService


@csrf_exempt
def debug_date_analysis(request):
    """Debug view to test date analysis functionality"""
    
    if request.method != 'GET':
        return JsonResponse({'error': 'GET method required'}, status=405)
    
    try:
        service = RealDataIntegrationService()
        
        test_dates = [
            date(2025, 8, 12),
            date(2025, 8, 6), 
            date(2025, 7, 15)
        ]
        
        results = {}
        
        # Test each date
        for test_date in test_dates:
            date_str = test_date.strftime('%Y-%m-%d')
            
            # Test with date
            result = service.get_enhanced_lottery_input(prediction_date=test_date)
            
            results[date_str] = {
                'data_source': result.get('data_source', 'unknown'),
                'analysis_date': str(result.get('analysis_date', 'none')),
                'numbers_count': len(result.get('lottery_numbers', [])),
                'sample_numbers': result.get('lottery_numbers', [])[:10]
            }
        
        # Test default (no date)
        default_result = service.get_enhanced_lottery_input()
        results['default'] = {
            'data_source': default_result.get('data_source', 'unknown'),
            'analysis_date': str(default_result.get('analysis_date', 'none')),
            'numbers_count': len(default_result.get('lottery_numbers', [])),
            'sample_numbers': default_result.get('lottery_numbers', [])[:10]
        }
        
        # Analysis
        data_sources = set()
        for key, result in results.items():
            if key != 'default':
                data_sources.add(result['data_source'])
        
        analysis = {
            'unique_data_sources': len(data_sources),
            'all_data_sources': list(data_sources),
            'working_correctly': len(data_sources) > 1
        }
        
        return JsonResponse({
            'success': True,
            'test_results': results,
            'analysis': analysis,
            'message': 'Different data sources found!' if analysis['working_correctly'] else 'Same data sources - need investigation'
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e),
            'message': 'Debug test failed'
        }, status=500)
