"""
Script to populate NumberFrequencyStats data for cyclical predictions
"""

import os
import sys
import django
import random
from datetime import datetime, timedelta

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'xoso_crawler.settings')
django.setup()

from results.models import NumberFrequencyStats, KetQuaXoSo


def populate_frequency_stats():
    """Populate sample frequency stats for testing"""
    
    print("Starting to populate NumberFrequencyStats...")
    
    # Generate data for the last 180 days
    end_date = datetime.now().date()
    start_date = end_date - timedelta(days=180)
    
    current_date = start_date
    created_count = 0
    
    while current_date <= end_date:
        # Generate 20-30 numbers per day
        num_count = random.randint(20, 30)
        
        for _ in range(num_count):
            number = str(random.randint(0, 99)).zfill(2)
            
            # Check if already exists
            exists = NumberFrequencyStats.objects.filter(
                date=current_date,
                number=number
            ).exists()
            
            if not exists:
                # Create with only the fields that exist in the model
                NumberFrequencyStats.objects.create(
                    date=current_date,
                    number=number,
                    appeared_in_special=random.choice([True, False]),
                    day_of_week=current_date.weekday(),
                    day_of_month=current_date.day,
                    month=current_date.month,
                    year=current_date.year
                )
                created_count += 1
        
        current_date += timedelta(days=1)
        
        if created_count % 100 == 0:
            print(f"Created {created_count} records...")
    
    print(f"\n✅ Created {created_count} NumberFrequencyStats records")
    
    # Show summary
    total_records = NumberFrequencyStats.objects.count()
    recent_records = NumberFrequencyStats.objects.filter(
        date__gte=end_date - timedelta(days=30)
    ).count()
    
    print(f"\nSummary:")
    print(f"- Total records: {total_records}")
    print(f"- Recent 30 days: {recent_records}")


if __name__ == "__main__":
    populate_frequency_stats()
