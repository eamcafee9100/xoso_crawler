#!/usr/bin/env python
"""
Real Data Integration Test for TRANSCEND 99.9% System
=====================================================

Test script để tích hợp TRANSCEND với dữ liệu thực từ database Django
và tạo ra những dự đoán xổ số thực tế thay vì simulation data.
"""

import os
import sys
import django
from datetime import datetime, timedelta
import json

# Setup Django environment
sys.path.append('.')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'xoso_crawler.settings')
django.setup()

# Import models and TRANSCEND system
from results.models import KetQuaXoSo
from transcend_999_achievement_system import TRANSCEND999AchievementSystem
import numpy as np

def get_real_lottery_data(days_back=100):
    """
    Lấy dữ liệu xổ số thực từ database
    
    Returns:
        list: Danh sách dictionary chứa dữ liệu xổ số thực
    """
    print(f"🔍 Đang lấy dữ liệu xổ số {days_back} ngày gần nhất...")
    
    try:
        # Lấy dữ liệu từ database
        end_date = datetime.now().date()
        start_date = end_date - timedelta(days=days_back)
        
        results = KetQuaXoSo.objects.filter(
            ngay__gte=start_date,
            ngay__lte=end_date
        ).order_by('-ngay')
        
        real_data = []
        for result in results:
            # Lấy tất cả số 2 chữ số từ kết quả
            all_2d_numbers = result.get_all_2digit_numbers()
            
            # Chuyển đổi set thành list và sắp xếp
            numbers_list = sorted(list(all_2d_numbers))
            
            real_data.append({
                'date': result.ngay.strftime('%Y-%m-%d'),
                'numbers': numbers_list,
                'special_prize': result.giai_db[-2:] if result.giai_db and len(result.giai_db) >= 2 else '00',
                'first_prize': result.giai_1[-2:] if result.giai_1 and len(result.giai_1) >= 2 else '00',
                'raw_data': {
                    'giai_db': result.giai_db,
                    'giai_1': result.giai_1,
                    'giai_2': result.giai_2,
                    'giai_3': result.giai_3,
                    'giai_4': result.giai_4,
                    'giai_5': result.giai_5,
                    'giai_6': result.giai_6,
                    'giai_7': result.giai_7,
                }
            })
        
        print(f"✅ Đã lấy được {len(real_data)} bản ghi dữ liệu thực")
        return real_data
        
    except Exception as e:
        print(f"❌ Lỗi khi lấy dữ liệu: {str(e)}")
        return []

def analyze_real_data_patterns(real_data):
    """
    Phân tích pattern thực từ dữ liệu lịch sử
    
    Args:
        real_data (list): Dữ liệu xổ số thực
        
    Returns:
        dict: Thống kê và pattern phân tích
    """
    print("📊 Đang phân tích pattern từ dữ liệu thực...")
    
    # Phân tích tần suất số
    frequency_map = {}
    all_numbers = []
    
    for record in real_data:
        for number in record['numbers']:
            all_numbers.append(number)
            frequency_map[number] = frequency_map.get(number, 0) + 1
    
    # Tính toán thống kê
    total_numbers = len(all_numbers)
    avg_frequency = total_numbers / 100 if total_numbers > 0 else 0  # Chia cho 100 số có thể (00-99)
    
    # Phân loại số theo tần suất
    hot_numbers = []    # Số nóng (xuất hiện nhiều)
    cold_numbers = []   # Số lạnh (xuất hiện ít)
    
    for number in range(100):
        num_str = f"{number:02d}"
        freq = frequency_map.get(num_str, 0)
        
        if freq > avg_frequency * 1.2:
            hot_numbers.append(num_str)
        elif freq < avg_frequency * 0.8:
            cold_numbers.append(num_str)
    
    # Phân tích chu kỳ và gap
    gap_analysis = analyze_number_gaps(real_data)
    
    analysis_result = {
        'total_records': len(real_data),
        'total_unique_numbers': len(frequency_map),
        'avg_frequency': round(avg_frequency, 2),
        'hot_numbers': hot_numbers[:10],  # Top 10 số nóng
        'cold_numbers': cold_numbers[:10],  # Top 10 số lạnh
        'frequency_distribution': dict(sorted(frequency_map.items(), key=lambda x: x[1], reverse=True)[:20]),
        'gap_analysis': gap_analysis
    }
    
    print(f"✅ Phân tích hoàn thành:")
    print(f"   - Tổng số bản ghi: {analysis_result['total_records']}")
    print(f"   - Số duy nhất: {analysis_result['total_unique_numbers']}")
    print(f"   - Tần suất trung bình: {analysis_result['avg_frequency']}")
    print(f"   - Số nóng: {len(analysis_result['hot_numbers'])}")
    print(f"   - Số lạnh: {len(analysis_result['cold_numbers'])}")
    
    return analysis_result

def analyze_number_gaps(real_data):
    """
    Phân tích khoảng cách (gap) giữa các lần xuất hiện của số
    """
    number_last_seen = {}
    gap_stats = {}
    
    for i, record in enumerate(real_data):
        current_date = record['date']
        
        # Cập nhật gap cho các số xuất hiện
        for number in record['numbers']:
            if number in number_last_seen:
                gap = i - number_last_seen[number]
                if number not in gap_stats:
                    gap_stats[number] = []
                gap_stats[number].append(gap)
            number_last_seen[number] = i
    
    # Tính toán gap trung bình cho mỗi số
    avg_gaps = {}
    for number, gaps in gap_stats.items():
        if gaps:
            avg_gaps[number] = round(sum(gaps) / len(gaps), 2)
    
    return {
        'average_gaps': avg_gaps,
        'numbers_ready_to_appear': [num for num, gap in avg_gaps.items() if gap < 5]  # Số có thể sắp ra
    }

def create_real_predictions_with_transcend(real_data, pattern_analysis):
    """
    Tạo dự đoán thực tế sử dụng TRANSCEND 99.9% và dữ liệu thực
    
    Args:
        real_data (list): Dữ liệu xổ số thực
        pattern_analysis (dict): Kết quả phân tích pattern
        
    Returns:
        dict: Dự đoán chi tiết với confidence scores
    """
    print("🚀 Đang tạo dự đoán thực tế với TRANSCEND 99.9% System...")
    
    # Khởi tạo TRANSCEND system
    transcend = TRANSCEND999AchievementSystem()
    
    # Chuẩn bị dữ liệu đầu vào cho TRANSCEND dựa trên phân tích thực
    real_historical_data = []
    for record in real_data[:30]:  # Sử dụng 30 ngày gần nhất
        # Chuyển đổi số thành format TRANSCEND
        historical_numbers = [int(num) for num in record['numbers'][:10]]  # Lấy tối đa 10 số
        real_historical_data.append(historical_numbers)
    
    # Phase 1: Foundation Analysis với dữ liệu thực
    foundation_result = transcend.foundation_analysis(
        historical_data=real_historical_data,
        current_patterns=pattern_analysis['frequency_distribution']
    )
    
    # Phase 2: Statistical Enhancement với pattern thực
    statistical_result = transcend.statistical_enhancement(
        foundation_base=foundation_result,
        market_data={
            'hot_numbers': [int(num) for num in pattern_analysis['hot_numbers']],
            'cold_numbers': [int(num) for num in pattern_analysis['cold_numbers']],
            'frequency_map': {int(k): v for k, v in pattern_analysis['frequency_distribution'].items()}
        }
    )
    
    # Phase 3: AI Predictive với real data
    ai_result = transcend.ai_predictive_modeling(
        enhanced_base=statistical_result,
        prediction_horizon=1,  # Dự đoán cho ngày mai
        confidence_threshold=0.75
    )
    
    # Phase 4: Quantum Breakthrough với real patterns
    final_result = transcend.quantum_breakthrough_analysis(
        ai_enhanced=ai_result,
        breakthrough_probability=0.95,
        real_data_context={
            'recent_trends': real_data[:7],  # 7 ngày gần nhất
            'gap_analysis': pattern_analysis['gap_analysis']
        }
    )
    
    # Tạo top predictions với confidence scores
    real_predictions = generate_final_lottery_predictions(final_result, pattern_analysis)
    
    print("✅ Dự đoán thực tế hoàn thành!")
    return real_predictions

def generate_final_lottery_predictions(transcend_result, pattern_analysis):
    """
    Tạo dự đoán cuối cùng dựa trên kết quả TRANSCEND và pattern thực
    """
    predictions = {
        'prediction_date': (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d'),
        'transcend_achievement_score': transcend_result.get('final_score', 0),
        'methodology': 'TRANSCEND 99.9% + Real Historical Data Analysis',
        'top_predictions': {},
        'analysis_summary': {
            'foundation_score': transcend_result.get('foundation_score', 0),
            'statistical_score': transcend_result.get('statistical_score', 0),
            'ai_score': transcend_result.get('ai_score', 0),
            'quantum_score': transcend_result.get('quantum_score', 0)
        }
    }
    
    # Combine TRANSCEND results với real data insights
    transcend_numbers = transcend_result.get('final_predictions', [])
    hot_numbers = pattern_analysis['hot_numbers']
    ready_numbers = pattern_analysis['gap_analysis']['numbers_ready_to_appear']
    
    # Tạo weighted predictions
    confidence_map = {}
    
    # TRANSCEND predictions có weight cao
    for i, num in enumerate(transcend_numbers[:10]):
        num_str = f"{num:02d}"
        base_confidence = max(0.6, 0.9 - (i * 0.05))  # Confidence giảm dần
        confidence_map[num_str] = base_confidence
    
    # Boost confidence cho hot numbers
    for num in hot_numbers[:5]:
        if num in confidence_map:
            confidence_map[num] = min(0.95, confidence_map[num] + 0.1)
        else:
            confidence_map[num] = 0.65
    
    # Boost confidence cho numbers ready to appear
    for num in ready_numbers[:5]:
        if num in confidence_map:
            confidence_map[num] = min(0.95, confidence_map[num] + 0.08)
        else:
            confidence_map[num] = 0.60
    
    # Sắp xếp theo confidence và lấy top predictions
    sorted_predictions = sorted(confidence_map.items(), key=lambda x: x[1], reverse=True)
    
    for i, (number, confidence) in enumerate(sorted_predictions[:15]):
        predictions['top_predictions'][number] = {
            'confidence': round(confidence, 3),
            'rank': i + 1,
            'reasoning': get_prediction_reasoning(number, pattern_analysis, transcend_result)
        }
    
    return predictions

def get_prediction_reasoning(number, pattern_analysis, transcend_result):
    """
    Tạo lý do cho dự đoán
    """
    reasons = []
    
    if number in pattern_analysis['hot_numbers']:
        reasons.append("Hot number (xuất hiện thường xuyên)")
    
    if number in pattern_analysis['gap_analysis']['numbers_ready_to_appear']:
        reasons.append("Gap analysis indicates ready to appear")
    
    if int(number) in transcend_result.get('final_predictions', []):
        reasons.append("TRANSCEND 99.9% high-confidence prediction")
    
    if not reasons:
        reasons.append("Statistical probability based on historical patterns")
    
    return " | ".join(reasons)

def main():
    """
    Main function để chạy toàn bộ quy trình tích hợp dữ liệu thực
    """
    print("=" * 60)
    print("🎯 TRANSCEND 99.9% REAL DATA INTEGRATION")
    print("   Tích hợp dữ liệu thực cho dự đoán xổ số")
    print("=" * 60)
    
    try:
        # Step 1: Lấy dữ liệu thực từ database
        real_data = get_real_lottery_data(days_back=100)
        
        if not real_data:
            print("❌ Không có dữ liệu thực để phân tích!")
            return
        
        # Step 2: Phân tích patterns từ dữ liệu thực
        pattern_analysis = analyze_real_data_patterns(real_data)
        
        # Step 3: Tạo dự đoán thực tế với TRANSCEND
        predictions = create_real_predictions_with_transcend(real_data, pattern_analysis)
        
        # Step 4: Hiển thị kết quả
        print("\n" + "=" * 60)
        print("🎯 REAL LOTTERY PREDICTIONS")
        print("=" * 60)
        print(f"Prediction Date: {predictions['prediction_date']}")
        print(f"TRANSCEND Achievement Score: {predictions['transcend_achievement_score']:.2%}")
        print(f"Methodology: {predictions['methodology']}")
        
        print("\n📊 TRANSCEND Phase Scores:")
        for phase, score in predictions['analysis_summary'].items():
            print(f"   {phase.title()}: {score:.2%}")
        
        print(f"\n🔮 TOP {len(predictions['top_predictions'])} PREDICTIONS:")
        print("   Rank | Number | Confidence | Reasoning")
        print("   " + "-" * 55)
        
        for number, details in predictions['top_predictions'].items():
            rank = details['rank']
            confidence = details['confidence']
            reasoning = details['reasoning'][:40] + "..." if len(details['reasoning']) > 40 else details['reasoning']
            print(f"   {rank:2d}   | {number}     | {confidence:.1%}       | {reasoning}")
        
        # Step 5: Lưu kết quả
        output_file = f"real_predictions_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump({
                'predictions': predictions,
                'pattern_analysis': pattern_analysis,
                'data_summary': {
                    'total_records_analyzed': len(real_data),
                    'analysis_period': f"{real_data[-1]['date']} to {real_data[0]['date']}"
                }
            }, f, indent=2, ensure_ascii=False)
        
        print(f"\n💾 Kết quả đã được lưu vào: {output_file}")
        print("\n✅ REAL DATA INTEGRATION COMPLETED SUCCESSFULLY!")
        
        return predictions
        
    except Exception as e:
        print(f"❌ Lỗi trong quá trình tích hợp: {str(e)}")
        import traceback
        traceback.print_exc()
        return None

if __name__ == "__main__":
    main()
