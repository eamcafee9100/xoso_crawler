"""
Test import models
"""
import os
import sys
import django

# Add project root to Python path
sys.path.insert(0, 'c:/Users/n2t/Documents/xoso_crawler')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'xoso_crawler.settings')

try:
    django.setup()
    print("Django setup completed")
    
    # Test import specific models
    from results.models import NumberFrequencyStats
    print("NumberFrequencyStats imported successfully")
    
    from results.models import NumberAnalysisCache
    print("NumberAnalysisCache imported successfully")
    
    from results.models import NumberAnalysisDetail  
    print("NumberAnalysisDetail imported successfully")
    
    print("All models imported successfully!")
    
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
