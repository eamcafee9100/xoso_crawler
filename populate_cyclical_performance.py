"""
Script to populate MethodCyclicalPerformance data
This will create sample performance data for testing the cyclical prediction API
"""

import os
import sys
import django
import random
from datetime import datetime, timedelta

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'xoso_crawler.settings')
django.setup()

from predictions_tracker.models import (
    PredictionMethod,
    MethodCyclicalPerformance
)


def populate_cyclical_performance_data():
    """Populate sample cyclical performance data for all active methods"""
    
    # Get all active prediction methods
    active_methods = PredictionMethod.objects.filter(is_active=True)
    
    if not active_methods.exists():
        print("No active prediction methods found. Please create some methods first.")
        return
    
    print(f"Found {active_methods.count()} active methods")
    
    # Generate data for the last 3 months
    current_date = datetime.now().date()
    
    for month_offset in range(3):
        # Calculate month and year
        target_date = current_date - timedelta(days=30 * month_offset)
        year = target_date.year
        month = target_date.month
        
        print(f"\nGenerating data for {month}/{year}")
        
        for method in active_methods:
            # Check if data already exists
            performance, created = MethodCyclicalPerformance.objects.get_or_create(
                method_name=method.name,
                year=year,
                month=month,
                defaults={
                    'early_month_performance': {},
                    'mid_month_performance': {},
                    'late_month_performance': {},
                    'total_hit_days': 0,
                    'total_days': 0,
                    'hit_rate': 0.0,
                    'fatigue_threshold_reached': False
                }
            )
            
            if not created:
                print(f"  - Data already exists for {method.name}")
                continue
            
            # Generate realistic performance data
            # Early month (days 1-10)
            early_hits = random.randint(3, 8)
            early_total = 10
            early_predictions = random.randint(100, 150)
            
            performance.early_month_performance = {
                'total_hits': early_hits,
                'total_predictions': early_predictions,
                'hit_rate': early_hits / early_total if early_total > 0 else 0,
                'days_active': early_total,
                'avg_predictions_per_day': early_predictions / early_total
            }
            
            # Mid month (days 11-20)
            mid_hits = random.randint(4, 9)
            mid_total = 10
            mid_predictions = random.randint(100, 150)
            
            performance.mid_month_performance = {
                'total_hits': mid_hits,
                'total_predictions': mid_predictions,
                'hit_rate': mid_hits / mid_total if mid_total > 0 else 0,
                'days_active': mid_total,
                'avg_predictions_per_day': mid_predictions / mid_total
            }
            
            # Late month (days 21-30/31)
            late_hits = random.randint(2, 7)
            late_total = 10
            late_predictions = random.randint(100, 150)
            
            performance.late_month_performance = {
                'total_hits': late_hits,
                'total_predictions': late_predictions,
                'hit_rate': late_hits / late_total if late_total > 0 else 0,
                'days_active': late_total,
                'avg_predictions_per_day': late_predictions / late_total
            }
            
            # Calculate totals
            total_hit_days = early_hits + mid_hits + late_hits
            total_days = early_total + mid_total + late_total
            
            performance.total_hit_days = total_hit_days
            performance.total_days = total_days
            performance.hit_rate = total_hit_days / total_days if total_days > 0 else 0
            
            # Simulate fatigue for some methods
            if total_hit_days >= 19 and random.random() > 0.7:
                performance.fatigue_threshold_reached = True
                performance.fatigue_reached_on = target_date.replace(day=random.randint(20, 28))
            
            performance.save()
            print(f"  ✓ Created data for {method.name}: {total_hit_days}/{total_days} days ({performance.hit_rate:.1%})")
    
    print("\n✅ Cyclical performance data population completed!")
    
    # Show summary
    total_records = MethodCyclicalPerformance.objects.count()
    fatigued_methods = MethodCyclicalPerformance.objects.filter(fatigue_threshold_reached=True).count()
    
    print(f"\nSummary:")
    print(f"- Total performance records: {total_records}")
    print(f"- Methods with fatigue: {fatigued_methods}")
    
    # Show sample data
    print("\nSample performance data:")
    sample_performances = MethodCyclicalPerformance.objects.all()[:5]
    for perf in sample_performances:
        print(f"- {perf.method_name} ({perf.month}/{perf.year}): "
              f"{perf.total_hit_days}/{perf.total_days} days, "
              f"Hit rate: {perf.hit_rate:.1%}, "
              f"Fatigued: {perf.fatigue_threshold_reached}")


def create_sample_methods_if_needed():
    """Create sample prediction methods if none exist"""
    if PredictionMethod.objects.exists():
        return
    
    print("Creating sample prediction methods...")
    
    sample_methods = [
        {"code": "BTL_HB_k3N_1_01", "name": "BTL HB_k3N_1 01", "category": "cycle"},
        {"code": "BTL_HB_k3N_1_02", "name": "BTL HB_k3N_1 02", "category": "frequency"},
        {"code": "BTL_HB_k3N_2_01", "name": "BTL HB_k3N_2 01", "category": "gap"},
        {"code": "SC_QM_01", "name": "SC_QM 01", "category": "pattern"},
        {"code": "SC_QM_02", "name": "SC_QM 02", "category": "statistical"},
    ]
    
    for method_data in sample_methods:
        PredictionMethod.objects.create(
            code=method_data["code"],
            name=method_data["name"],
            category=method_data["category"],
            description=f"Sample method for {method_data['category']} analysis",
            is_active=True,
            priority=random.randint(1, 5)
        )
    
    print(f"Created {len(sample_methods)} sample methods")


if __name__ == "__main__":
    print("Starting cyclical performance data population...")
    
    # Create sample methods if needed
    create_sample_methods_if_needed()
    
    # Populate performance data
    populate_cyclical_performance_data()
