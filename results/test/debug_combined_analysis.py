
import os
import sys
import django

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'xoso_crawler.settings')
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
django.setup()

from datetime import datetime, timedelta
from results.models import KetQuaXoSo
from results.services.PredictionService import PredictionService
from results.services.MLModelService import MLModelService, SHAPAnalysisService
from results.services.PredictionCacheService import PredictionCacheService
from results.analytics.predictors import BachThuLoPredictor

def debug_combined_analysis():
    """Debug script để kiểm tra từng thành phần của CombinedAnalysisView"""
    
    print("🔍 DEBUG: Combined Analysis View")
    print("=" * 50)
    
    # 1. Kiểm tra ngày được chọn
    selected_date = datetime.now().date()
    target_date = selected_date + timedelta(days=1)
    print(f"📅 Selected date: {selected_date}")
    print(f"📅 Target date: {target_date}")
    
    # 2. Kiểm tra dữ liệu lịch sử
    print("\n🗂️ Checking historical data...")
    historical_data = KetQuaXoSo.objects.filter(
        ngay__lt=selected_date
    ).order_by('-ngay')[:90]
    
    print(f"📊 Found {historical_data.count()} historical records")
    if historical_data.exists():
        latest = historical_data.first()
        print(f"📈 Latest record: {latest.ngay} - DB: {latest.giai_db}")
    else:
        print("❌ No historical data found!")
        return
    
    # 3. Kiểm tra services
    print("\n🔧 Checking services...")
    
    try:
        prediction_service = PredictionService()
        print("✅ PredictionService initialized")
    except Exception as e:
        print(f"❌ PredictionService error: {e}")
        prediction_service = None
    
    try:
        ml_service = MLModelService()
        print("✅ MLModelService initialized")
    except Exception as e:
        print(f"❌ MLModelService error: {e}")
        ml_service = None
    
    try:
        if ml_service:
            shap_service = SHAPAnalysisService(ml_service)
            print("✅ SHAPAnalysisService initialized")
        else:
            shap_service = None
    except Exception as e:
        print(f"❌ SHAPAnalysisService error: {e}")
        shap_service = None
    
    try:
        cache_service = PredictionCacheService()
        print("✅ PredictionCacheService initialized")
    except Exception as e:
        print(f"❌ PredictionCacheService error: {e}")
        cache_service = None
    
    # 4. Kiểm tra BachThuLoPredictor
    print("\n🎯 Checking BachThuLoPredictor...")
    try:
        predictor = BachThuLoPredictor(
            target_date=target_date,
            history_days=90,
            selected_date=selected_date
        )
        print("✅ BachThuLoPredictor initialized")
        
        # Test prediction
        print("🔮 Testing predictions...")
        predictions = predictor.predict()
        
        if predictions:
            print(f"✅ Got predictions: {type(predictions)}")
            print(f"📋 Predictions keys: {list(predictions.keys()) if isinstance(predictions, dict) else 'Not a dict'}")
            
            # In ra một vài sample predictions
            if isinstance(predictions, dict):
                for key, value in list(predictions.items())[:3]:
                    print(f"  - {key}: {type(value)} - {str(value)[:100]}")
        else:
            print("❌ No predictions returned")
            
    except Exception as e:
        print(f"❌ BachThuLoPredictor error: {e}")
        import traceback
        traceback.print_exc()
    
    # 5. Kiểm tra ML predictions
    if ml_service:
        print("\n🤖 Checking ML predictions...")
        try:
            ml_predictions = ml_service.predict_numbers(target_date, historical_data)
            if ml_predictions:
                print(f"✅ ML predictions: {len(ml_predictions)} items")
                print(f"📊 Sample: {ml_predictions[:3] if isinstance(ml_predictions, list) else str(ml_predictions)[:100]}")
            else:
                print("❌ No ML predictions")
        except Exception as e:
            print(f"❌ ML prediction error: {e}")
    
    # 6. Kiểm tra cache
    if cache_service:
        print("\n💾 Checking cache...")
        try:
            should_show = cache_service.should_show_prediction_results(target_date)
            print(f"📊 Should show predictions: {should_show}")
            
            cached_data = cache_service.get_cached_prediction(selected_date, 'combined')
            if cached_data:
                print(f"✅ Found cached data: {type(cached_data)}")
            else:
                print("ℹ️ No cached data")
        except Exception as e:
            print(f"❌ Cache error: {e}")
    
    # 7. Kiểm tra template variables
    print("\n🎨 Template variables that should be available:")
    template_vars = [
        'selected_date', 'target_date', 'optimal_numbers', 'enhanced_combined_numbers',
        'enhanced_methods', 'processing_stages', 'actual_numbers', 'performance_stats',
        'pair_suggestions', 'digit_analysis', 'pattern_analysis', 'shap_analysis',
        'historical_accuracy', 'optimized_predictions', 'error'
    ]
    
    for var in template_vars:
        print(f"  - {var}")
    
    print("\n" + "=" * 50)
    print("🏁 Debug complete! Check output above for issues.")

if __name__ == "__main__":
    debug_combined_analysis()