#!/usr/bin/env python
"""
Test lazy loading MLModelService
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'xoso_crawler.settings')
django.setup()

print("🚀 Testing MLModelService Lazy Loading")
print("=" * 40)

# Test 1: Import và tạo service
print("1️⃣ Importing and creating service...")
from results.services.MLModelService import get_ml_model_service

print("2️⃣ Getting service instance...")
service = get_ml_model_service()

print("3️⃣ Checking if models are loaded yet...")
models_loaded = getattr(service, '_models_loaded', False)
print(f"   📊 Models loaded: {models_loaded}")

if not models_loaded:
    print("   🎯 SUCCESS: Models not loaded yet (lazy loading working!)")
else:
    print("   ⚠️ WARNING: Models already loaded")

print("4️⃣ Triggering model loading with get_model_info()...")
info = service.get_model_info()

print("5️⃣ Checking after model loading...")
models_loaded_after = info.get('models_loaded', False)
working_models = info.get('working_models', 0)
total_models = info.get('total_models', 0)

print(f"   📊 Models loaded: {models_loaded_after}")
print(f"   📊 Working models: {working_models}/{total_models}")

if models_loaded_after:
    print("   🎯 SUCCESS: Models loaded on demand!")
else:
    print("   ⚠️ WARNING: Models still not loaded")

print("\n" + "=" * 40)
print("📋 SUMMARY")
print("=" * 40)
print(f"• Initial state: Models loaded = {models_loaded}")
print(f"• After first use: Models loaded = {models_loaded_after}")
print(f"• Working models: {working_models}/{total_models}")

if not models_loaded and models_loaded_after:
    print("\n🎉 LAZY LOADING WORKING PERFECTLY!")
    print("• Django startup is now faster")
    print("• Models only load when needed")
    print("• Memory usage reduced during startup")
else:
    print("\n⚠️ Lazy loading may need more adjustments")

print("\n✅ Test completed!")
