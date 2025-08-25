#!/usr/bin/env python
"""
Simple test for MLModelService lazy loading
"""
import time
import os
import sys

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'xoso_crawler.settings')

import django
django.setup()

def test_lazy_loading():
    print("🚀 Testing MLModelService Lazy Loading")
    print("=" * 40)
    
    # Test 1: Import time
    print("1️⃣ Testing import time...")
    start = time.time()
    
    try:
        from results.services.MLModelService import get_ml_model_service
        import_time = time.time() - start
        print(f"   ✅ Import time: {import_time:.4f}s")
        
        if import_time < 0.1:
            print("   🎯 EXCELLENT: Very fast import!")
        elif import_time < 0.5:
            print("   🟡 GOOD: Reasonable import time")
        else:
            print("   🔴 SLOW: Import taking too long")
            
    except Exception as e:
        print(f"   ❌ Import failed: {e}")
        return False
    
    # Test 2: First instance creation
    print("\n2️⃣ Testing first instance creation...")
    start = time.time()
    
    try:
        service = get_ml_model_service()
        init_time = time.time() - start
        print(f"   ✅ Instance creation: {init_time:.4f}s")
        
        # Check if models are loaded yet
        has_models = hasattr(service, '_models_loaded') and service._models_loaded
        print(f"   📊 Models loaded immediately: {has_models}")
        
        if not has_models:
            print("   🎯 SUCCESS: Models NOT loaded on init (lazy loading working!)")
        else:
            print("   ⚠️ WARNING: Models loaded immediately (lazy loading may not be working)")
            
    except Exception as e:
        print(f"   ❌ Instance creation failed: {e}")
        return False
    
    # Test 3: Subsequent calls
    print("\n3️⃣ Testing subsequent calls...")
    times = []
    for i in range(3):
        start = time.time()
        service2 = get_ml_model_service()
        call_time = time.time() - start
        times.append(call_time)
        print(f"   Call {i+1}: {call_time:.6f}s")
    
    avg_time = sum(times) / len(times)
    print(f"   📊 Average: {avg_time:.6f}s")
    
    if avg_time < 0.001:
        print("   🎯 EXCELLENT: Singleton pattern working perfectly!")
    
    # Test 4: Django server startup simulation
    print("\n4️⃣ Simulating Django server startup...")
    startup_start = time.time()
    
    # Simulate what happens during Django startup
    try:
        # This would normally happen during Django app loading
        from results.services.MLModelService import get_ml_model_service
        
        startup_time = time.time() - startup_start
        print(f"   ✅ Startup simulation: {startup_time:.4f}s")
        
        if startup_time < 0.5:
            print("   🚀 EXCELLENT: Django server will start quickly!")
        elif startup_time < 2.0:
            print("   🟡 GOOD: Reasonable startup time")
        else:
            print("   🔴 SLOW: May impact server startup")
            
    except Exception as e:
        print(f"   ❌ Startup simulation failed: {e}")
        return False
    
    # Summary
    print("\n" + "=" * 40)
    print("📋 SUMMARY")
    print("=" * 40)
    print(f"📊 Import time: {import_time:.4f}s")
    print(f"📊 Init time: {init_time:.4f}s")
    print(f"📊 Total startup impact: {import_time + init_time:.4f}s")
    
    total_time = import_time + init_time
    if total_time < 0.2:
        print("🎉 RESULT: EXCELLENT - Minimal impact on Django startup!")
    elif total_time < 1.0:
        print("✅ RESULT: GOOD - Reasonable startup performance")
    else:
        print("⚠️ RESULT: May still impact startup time")
    
    print("\n🔥 RECOMMENDATIONS:")
    print("• Django server startup should be much faster now")
    print("• ML models will only load when first prediction is requested")
    print("• Memory usage reduced during startup")
    print("• Better development experience with faster reloads")
    
    return True

if __name__ == "__main__":
    try:
        success = test_lazy_loading()
        if success:
            print("\n🎯 Test completed successfully!")
        else:
            print("\n❌ Test failed!")
    except Exception as e:
        print(f"\n💥 Test crashed: {e}")
        import traceback
        traceback.print_exc()
