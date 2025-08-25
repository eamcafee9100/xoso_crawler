import os, sys, django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'xoso_crawler.settings')
sys.path.append('.')
django.setup()
print('✅ Django OK')

from analytic_frequence.ultimate_prediction_system import create_ultimate_prediction_system
system = create_ultimate_prediction_system()
result = system.ultimate_prediction_analysis(lottery_numbers=[1,5,10,15,20], prediction_horizon=3)
print('📋 Result type:', type(result))

# Check each attribute
attrs = ['confidence_score', 'processing_time_ms', 'accuracy_boost', 'memory_usage_mb']
for attr in attrs:
    if hasattr(result, attr):
        value = getattr(result, attr)
        print(f'  {attr}: {type(value)} = {value}')
    else:
        print(f'  {attr}: NOT FOUND')

# Check time_crystal_patterns specifically
if hasattr(result, 'time_crystal_patterns'):
    tcp = result.time_crystal_patterns
    print(f'  time_crystal_patterns: {type(tcp)} = {tcp}')
else:
    print('  time_crystal_patterns: NOT FOUND')
