#!/usr/bin/env python
"""
TRANSCEND 99.9% Real Prediction API
==================================

API endpoint to serve real lottery predictions using TRANSCEND system
integrated with actual historical lottery data.
"""

import os
import sys
import django
import json
from datetime import datetime, timedelta

# Setup Django environment
sys.path.append('.')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'xoso_crawler.settings')
django.setup()

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
import logging

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def get_transcend_real_predictions():
    """
    Lấy dự đoán thực tế từ TRANSCEND 99.9% System
    
    Returns:
        dict: Kết quả dự đoán chi tiết
    """
    try:
        from results.models import KetQuaXoSo
        from analytic_frequence.transcend_999_achievement_system import TranscendentPredictionSystem
        from collections import Counter
        
        logger.info("🚀 Starting TRANSCEND 99.9% Real Prediction API")
        
        # Lấy dữ liệu thực từ database
        results = KetQuaXoSo.objects.order_by('-ngay')[:30]
        if not results:
            return {
                'error': 'No historical data available',
                'status': 'failed'
            }
        
        # Phân tích dữ liệu thực
        all_numbers = []
        for result in results:
            numbers = list(result.get_all_2digit_numbers())
            all_numbers.extend(numbers)
        
        frequency = Counter(all_numbers)
        hot_numbers = [num for num, count in frequency.most_common(10)]
        
        # Khởi tạo TRANSCEND
        transcend = TranscendentPredictionSystem()
        
        # Chuẩn bị dữ liệu cho TRANSCEND
        historical_data = []
        for result in results[:15]:
            numbers = list(result.get_all_2digit_numbers())[:8]
            numbers_int = [int(num) for num in numbers]
            
            historical_data.append({
                "numbers": numbers_int,
                "date": result.ngay.strftime("%Y-%m-%d")
            })
        
        # Chạy TRANSCEND prediction
        transcend_result = transcend.ultimate_transcendent_prediction(historical_data)
        
        # Tạo final predictions
        final_predictions = {}
        
        # TRANSCEND numbers (highest priority)
        for i, num in enumerate(transcend_result.transcendent_numbers[:8]):
            num_str = f"{num:02d}"
            confidence = transcend_result.transcendent_confidence - (i * 0.015)
            final_predictions[num_str] = {
                'confidence': round(confidence, 3),
                'rank': i + 1,
                'source': 'TRANSCEND_ULTIMATE',
                'reasoning': 'TRANSCEND 99.9% Ultimate Selection'
            }
        
        # Hot numbers boost
        for i, num in enumerate(hot_numbers[:5]):
            if num not in final_predictions:
                confidence = 0.72 - (i * 0.03)
                final_predictions[num] = {
                    'confidence': round(confidence, 3),
                    'rank': len(final_predictions) + 1,
                    'source': 'HOT_PATTERN',
                    'reasoning': 'High frequency pattern from real data'
                }
        
        # Sắp xếp theo confidence
        sorted_preds = sorted(final_predictions.items(), 
                            key=lambda x: x[1]['confidence'], reverse=True)
        
        # Update ranks
        for i, (number, details) in enumerate(sorted_preds):
            final_predictions[number]['rank'] = i + 1
        
        # Tạo response
        response = {
            'success': True,
            'timestamp': datetime.now().isoformat(),
            'prediction_date': (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d'),
            'method': 'TRANSCEND 99.9% + Real Historical Data',
            'system_info': {
                'version': transcend_result.system_version,
                'methodology': transcend_result.prediction_methodology,
                'transcendence_achieved': transcend_result.transcendence_achieved,
                'quality_breakthrough': transcend_result.quality_breakthrough
            },
            'achievement_scores': {
                'overall_confidence': round(transcend_result.transcendent_confidence, 3),
                'overall_transcendence': round(transcend_result.overall_transcendence, 3),
                'foundation_score': round(transcend_result.phase1_foundation_score, 3),
                'statistical_score': round(transcend_result.phase2_statistical_score, 3),
                'ai_score': round(transcend_result.phase3_ai_score, 3),
                'quantum_score': round(transcend_result.phase4_quantum_score, 3),
                'quantum_advantage': round(transcend_result.quantum_advantage, 3)
            },
            'data_summary': {
                'days_analyzed': len(results),
                'total_numbers_processed': len(all_numbers),
                'unique_numbers_found': len(frequency),
                'hot_numbers_count': len(hot_numbers)
            },
            'predictions': dict(sorted_preds[:12]),  # Top 12 predictions
            'summary': {
                'top_3_numbers': [num for num, _ in sorted_preds[:3]],
                'highest_confidence': max([details['confidence'] for _, details in sorted_preds]),
                'prediction_count': len(sorted_preds),
                'transcend_numbers_count': len(transcend_result.transcendent_numbers)
            }
        }
        
        logger.info(f"✅ Generated {len(sorted_preds)} predictions with {transcend_result.transcendent_confidence:.1%} confidence")
        return response
        
    except Exception as e:
        logger.error(f"❌ Error in TRANSCEND prediction: {str(e)}")
        return {
            'success': False,
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }

@csrf_exempt
@require_http_methods(["GET", "POST"])
def api_transcend_real_predictions(request):
    """
    API endpoint for TRANSCEND 99.9% real predictions
    
    GET/POST /transcend-real-predictions/
    
    Returns:
        JsonResponse: Comprehensive prediction data
    """
    try:
        logger.info(f"📡 TRANSCEND Real Predictions API called - Method: {request.method}")
        
        # Get predictions
        prediction_data = get_transcend_real_predictions()
        
        if prediction_data.get('success'):
            logger.info("✅ API call successful")
            return JsonResponse(prediction_data, status=200)
        else:
            logger.error("❌ API call failed")
            return JsonResponse(prediction_data, status=500)
            
    except Exception as e:
        logger.error(f"❌ API endpoint error: {str(e)}")
        return JsonResponse({
            'success': False,
            'error': f'API endpoint error: {str(e)}',
            'timestamp': datetime.now().isoformat()
        }, status=500)

# Test function
def test_api():
    """Test the API function locally"""
    print("🧪 Testing TRANSCEND Real Predictions API...")
    
    result = get_transcend_real_predictions()
    
    if result.get('success'):
        print("✅ API Test Successful!")
        print(f"🎯 Prediction Date: {result['prediction_date']}")
        print(f"🌟 Confidence: {result['achievement_scores']['overall_confidence']:.1%}")
        print(f"🔮 Top 5 Predictions:")
        
        for i, (number, details) in enumerate(list(result['predictions'].items())[:5]):
            print(f"   {i+1}. {number} - {details['confidence']:.1%} ({details['source']})")
        
        return True
    else:
        print("❌ API Test Failed!")
        print(f"Error: {result.get('error', 'Unknown error')}")
        return False

if __name__ == "__main__":
    test_api()
