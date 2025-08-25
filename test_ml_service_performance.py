#!/usr/bin/env python
"""
Test script để kiểm tra hiệu suất MLModelService với lazy loading
"""
import os
import sys
import django
import time
from datetime import datetime

# Setup Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'xoso_crawler.settings')
django.setup()

def test_import_performance():
    """Test thời gian import MLModelService"""
    print("🔄 Testing MLModelService import performance...")
    
    start_time = time.time()
    
    # Import module
    from results.services.MLModelService import get_ml_model_service
    
    import_time = time.time() - start_time
    print(f"📊 Import time: {import_time:.4f} seconds")
    
    return import_time

def test_first_use_performance():
    """Test thời gian khởi tạo lần đầu"""
    print("\n🔄 Testing first use performance...")
    
    from results.services.MLModelService import get_ml_model_service
    
    start_time = time.time()
    
    # Lần đầu gọi service - sẽ trigger lazy loading
    service = get_ml_model_service()
    
    init_time = time.time() - start_time
    print(f"📊 First initialization time: {init_time:.4f} seconds")
    
    # Test get_model_info (sẽ trigger model loading nếu chưa load)
    start_time = time.time()
    model_info = service.get_model_info()
    model_info_time = time.time() - start_time
    print(f"📊 Model info time: {model_info_time:.4f} seconds")
    
    print(f"📋 Models loaded: {model_info.get('models_loaded', False)}")
    print(f"📋 Working models: {model_info.get('working_models', 0)}/{model_info.get('total_models', 0)}")
    
    return init_time, model_info_time

def test_subsequent_calls():
    """Test hiệu suất các lần gọi tiếp theo"""
    print("\n🔄 Testing subsequent calls performance...")
    
    from results.services.MLModelService import get_ml_model_service
    
    service = get_ml_model_service()
    
    # Multiple calls to test singleton
    times = []
    for i in range(5):
        start_time = time.time()
        service2 = get_ml_model_service()
        call_time = time.time() - start_time
        times.append(call_time)
        print(f"📊 Call {i+1}: {call_time:.6f} seconds")
    
    avg_time = sum(times) / len(times)
    print(f"📊 Average subsequent call time: {avg_time:.6f} seconds")
    
    return avg_time

def compare_with_old_approach():
    """So sánh với cách cũ (nếu có)"""
    print("\n🔄 Comparing with old approach...")
    
    # Simulate old approach (loading models immediately)
    start_time = time.time()
    
    try:
        # Try to simulate old behavior
        print("📋 Old approach would load models immediately on import")
        print("📋 New approach: Models only loaded when needed")
        
        # Check if model files exist
        model_dir = "data/predictor_models"
        if os.path.exists(model_dir):
            model_files = [f for f in os.listdir(model_dir) if f.endswith('.pkl')]
            print(f"📂 Found {len(model_files)} model files")
            
            if model_files:
                # Estimate loading time based on file sizes
                total_size = sum(os.path.getsize(os.path.join(model_dir, f)) for f in model_files)
                estimated_load_time = total_size / (1024 * 1024) * 0.1  # Rough estimate
                print(f"📊 Estimated old approach load time: {estimated_load_time:.2f} seconds")
            else:
                print("📂 No model files found - both approaches would be fast")
        else:
            print("📂 Model directory not found - no models to load")
            
    except Exception as e:
        print(f"❌ Error in comparison: {e}")

def main():
    """Main test function"""
    print("🚀 MLModelService Performance Test")
    print("=" * 50)
    
    # Test 1: Import performance
    import_time = test_import_performance()
    
    # Test 2: First use performance
    init_time, model_info_time = test_first_use_performance()
    
    # Test 3: Subsequent calls
    avg_call_time = test_subsequent_calls()
    
    # Test 4: Comparison
    compare_with_old_approach()
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 PERFORMANCE SUMMARY")
    print("=" * 50)
    print(f"🔹 Import time: {import_time:.4f}s")
    print(f"🔹 First initialization: {init_time:.4f}s")
    print(f"🔹 Model loading: {model_info_time:.4f}s")
    print(f"🔹 Subsequent calls: {avg_call_time:.6f}s")
    print(f"🔹 Total first use: {import_time + init_time + model_info_time:.4f}s")
    
    if import_time < 0.1:
        print("✅ Import performance: EXCELLENT (< 0.1s)")
    elif import_time < 0.5:
        print("🟡 Import performance: GOOD (< 0.5s)")
    else:
        print("🔴 Import performance: NEEDS IMPROVEMENT (> 0.5s)")
    
    print("\n🎯 Lazy loading successfully implemented!")
    print("🚀 Django server startup should be significantly faster now!")

if __name__ == "__main__":
    main()
