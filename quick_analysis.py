import os
import sys
import time

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'xoso_crawler.settings')
import django
django.setup()

from analytic_frequence.template_views import UltimatePredictionTemplateView

print("🎯 ULTIMATE PREDICTION TEMPLATE VIEW - ANALYSIS")
print("=" * 60)

try:
    # Test initialization time
    start = time.time()
    view = UltimatePredictionTemplateView()
    init_time = (time.time() - start) * 1000
    print(f"⏱️ Initialization: {init_time:.2f}ms")

    # Test context preparation
    start = time.time()
    context = view.get_context_data()
    context_time = (time.time() - start) * 1000
    print(f"⏱️ Context prep: {context_time:.2f}ms")

    # Analyze context
    print(f"📊 Context keys: {len(context)} items")
    print(f"📊 Has sample: {'sample_prediction' in context}")
    
    total = init_time + context_time
    print(f"🎯 Total time: {total:.2f}ms")
    
    if total > 500:
        print("🚨 CRITICAL: Over 500ms")
    elif total > 200:
        print("⚠️ WARNING: Over 200ms")
    else:
        print("✅ Acceptable performance")

except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
