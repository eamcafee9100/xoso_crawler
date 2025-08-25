#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
🔍 KIỂM TRA VẤNĐỀ DATE ANALYSIS
Kiểm tra dữ liệu NumberFrequencyStats và logic phân tích theo ngày
"""

import os
import sys
from datetime import datetime, date, timedelta

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'xoso_crawler.settings')
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    import django
    django.setup()
    from results.models import NumberFrequencyStats
    from analytic_frequence.data_integration_service import RealDataIntegrationService
    from analytic_frequence.template_views import ajax_prediction_api
    from django.test import RequestFactory
    import json
    
    print("✅ Django setup successful")
except Exception as e:
    print(f"❌ Django setup failed: {e}")
    sys.exit(1)


def check_numberfrequencystats_data():
    """Kiểm tra dữ liệu NumberFrequencyStats"""
    print("\n" + "="*60)
    print("🔍 KIỂM TRA DỮ LIỆU NUMBERFREQUENCYSTATS")
    print("="*60)
    
    try:
        # 1. Kiểm tra tổng số records
        total_count = NumberFrequencyStats.objects.count()
        print(f"📊 Total records: {total_count}")
        
        if total_count == 0:
            print("❌ Không có dữ liệu trong NumberFrequencyStats!")
            print("💡 Cần chạy script populate dữ liệu")
            return False
            
        # 2. Kiểm tra phạm vi ngày
        earliest = NumberFrequencyStats.objects.order_by('date').first()
        latest = NumberFrequencyStats.objects.order_by('-date').first()
        
        if earliest and latest:
            print(f"📅 Date range: {earliest.date} to {latest.date}")
            
        # 3. Kiểm tra dữ liệu theo từng ngày gần đây
        recent_dates = NumberFrequencyStats.objects.values('date').distinct().order_by('-date')[:10]
        
        print(f"\n📈 Recent dates with data:")
        for date_record in recent_dates:
            date_obj = date_record['date']
            count = NumberFrequencyStats.objects.filter(date=date_obj).count()
            print(f"  - {date_obj}: {count} records")
            
        # 4. Kiểm tra một số mẫu cụ thể
        print(f"\n🔍 Sample records from latest date ({latest.date}):")
        samples = NumberFrequencyStats.objects.filter(date=latest.date)[:5]
        for sample in samples:
            print(f"  - Number {sample.number}: special={sample.appeared_in_special}, first={sample.appeared_in_first}, other={sample.appeared_in_other}")
            
        return True
        
    except Exception as e:
        print(f"❌ Error checking NumberFrequencyStats: {e}")
        return False


def test_data_integration_service():
    """Kiểm tra RealDataIntegrationService"""
    print("\n" + "="*60)
    print("🔍 KIỂM TRA REAL DATA INTEGRATION SERVICE")
    print("="*60)
    
    try:
        service = RealDataIntegrationService()
        
        # Test get_enhanced_lottery_input
        print("📊 Testing get_enhanced_lottery_input()...")
        result = service.get_enhanced_lottery_input()
        
        print(f"✅ Result type: {type(result)}")
        print(f"✅ Keys: {list(result.keys()) if isinstance(result, dict) else 'Not a dict'}")
        
        if isinstance(result, dict):
            lottery_numbers = result.get('lottery_numbers', [])
            data_source = result.get('data_source', 'unknown')
            
            print(f"📈 Lottery numbers count: {len(lottery_numbers)}")
            print(f"📈 Data source: {data_source}")
            
            if lottery_numbers:
                print(f"📈 Sample numbers: {lottery_numbers[:10]}")
            else:
                print("❌ No lottery numbers found!")
                
        return result
        
    except Exception as e:
        print(f"❌ Error testing RealDataIntegrationService: {e}")
        return None


def test_ajax_prediction_with_different_dates():
    """Test AJAX prediction với các ngày khác nhau"""
    print("\n" + "="*60)
    print("🔍 KIỂM TRA AJAX PREDICTION VỚI CÁC NGÀY KHÁC NHAU")
    print("="*60)
    
    # Chuẩn bị các ngày test
    today = date.today()
    test_dates = [
        today.strftime("%Y-%m-%d"),
        (today - timedelta(days=1)).strftime("%Y-%m-%d"),
        (today - timedelta(days=7)).strftime("%Y-%m-%d"),
        (today - timedelta(days=30)).strftime("%Y-%m-%d"),
    ]
    
    factory = RequestFactory()
    results = {}
    
    for test_date in test_dates:
        print(f"\n📅 Testing date: {test_date}")
        
        try:
            # Tạo request với ngày cụ thể
            request_data = {
                "prediction_date": test_date,
                "prediction_horizon": 5,
                "use_real_data": True
            }
            
            request = factory.post(
                "/ajax/prediction/",
                data=json.dumps(request_data),
                content_type="application/json",
            )
            
            # Gọi API
            response = ajax_prediction_api(request)
            
            if response.status_code == 200:
                content = json.loads(response.content.decode('utf-8'))
                
                if content.get('success'):
                    prediction_data = content.get('prediction_data', {})
                    predictions = prediction_data.get('predictions', [])
                    confidence = prediction_data.get('confidence_score', 0)
                    data_source = prediction_data.get('data_source', 'unknown')
                    
                    # Lưu kết quả để so sánh
                    results[test_date] = {
                        'predictions': [p.get('number', 0) if isinstance(p, dict) else p for p in predictions[:3]],  # Lấy 3 số đầu
                        'confidence': confidence,
                        'data_source': data_source
                    }
                    
                    print(f"  ✅ Success: {len(predictions)} predictions")
                    print(f"  📊 Top 3 numbers: {results[test_date]['predictions']}")
                    print(f"  🎯 Confidence: {confidence}")
                    print(f"  📈 Data source: {data_source}")
                else:
                    print(f"  ❌ API failed: {content.get('error', 'Unknown error')}")
                    
            else:
                print(f"  ❌ HTTP error: {response.status_code}")
                
        except Exception as e:
            print(f"  ❌ Exception: {e}")
    
    # So sánh kết quả
    print(f"\n🔍 SO SÁNH KẾT QUẢ:")
    print("-" * 60)
    
    unique_results = set()
    for date_str, result in results.items():
        result_signature = tuple(result['predictions'])
        unique_results.add(result_signature)
        print(f"{date_str}: {result['predictions']} (confidence: {result['confidence']:.3f}, source: {result['data_source']})")
    
    print(f"\n📊 Unique result patterns: {len(unique_results)}")
    
    if len(unique_results) == 1:
        print("❌ VẤNĐỀ XÁC NHẬN: Tất cả ngày trả về cùng kết quả!")
        print("💡 Nguyên nhân có thể:")
        print("   1. Logic phân tích không sử dụng prediction_date")
        print("   2. Dữ liệu NumberFrequencyStats không đủ hoặc không chính xác")
        print("   3. RealDataIntegrationService không lọc theo ngày")
    elif len(unique_results) == len(test_dates):
        print("✅ Tốt: Mỗi ngày có kết quả khác nhau")
    else:
        print("⚠️ Một số ngày có kết quả giống nhau")
    
    return results


def check_data_integration_logic():
    """Kiểm tra logic trong RealDataIntegrationService"""
    print("\n" + "="*60)
    print("🔍 KIỂM TRA LOGIC DATA INTEGRATION")
    print("="*60)
    
    try:
        # Đọc source code của RealDataIntegrationService
        from analytic_frequence import data_integration_service
        import inspect
        
        # Lấy source code của get_enhanced_lottery_input
        source = inspect.getsource(data_integration_service.RealDataIntegrationService.get_enhanced_lottery_input)
        
        print("📝 Source code analysis:")
        
        # Kiểm tra xem có sử dụng date filter không
        if "date" in source.lower() and "filter" in source.lower():
            print("✅ Logic có chứa date filtering")
        else:
            print("❌ Logic KHÔNG chứa date filtering - đây có thể là vấn đề!")
            
        # Kiểm tra NumberFrequencyStats usage
        if "NumberFrequencyStats" in source:
            print("✅ Logic sử dụng NumberFrequencyStats")
        else:
            print("❌ Logic KHÔNG sử dụng NumberFrequencyStats")
            
        # In ra một phần source code quan trọng
        print(f"\n📋 Relevant source code snippet:")
        lines = source.split('\n')
        for i, line in enumerate(lines[:20]):  # In 20 dòng đầu
            print(f"  {i+1:2d}: {line}")
            
    except Exception as e:
        print(f"❌ Error analyzing source code: {e}")


def main():
    """Main function"""
    print("🚀 KIỂM TRA VẤNĐỀ DATE ANALYSIS - ULTIMATE PREDICTION SYSTEM")
    print("=" * 80)
    
    # 1. Kiểm tra dữ liệu NumberFrequencyStats
    has_data = check_numberfrequencystats_data()
    
    # 2. Kiểm tra RealDataIntegrationService
    integration_result = test_data_integration_service()
    
    # 3. Kiểm tra logic trong data integration
    check_data_integration_logic()
    
    # 4. Test với các ngày khác nhau
    if has_data:
        test_results = test_ajax_prediction_with_different_dates()
    else:
        print("\n⚠️ Skipping AJAX test due to lack of data")
    
    print("\n" + "="*80)
    print("🏁 KIỂM TRA HOÀN TẤT")
    print("="*80)


if __name__ == "__main__":
    main()
