#!/usr/bin/env python
"""
Simple demo without caching to test basic functionality
"""
import os
import sys
import django
from datetime import datetime, timedelta

# Setup Django
sys.path.insert(0, os.path.abspath('.'))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'xoso_crawler.settings')
django.setup()

from results.models import NumberFrequencyStats
from django.utils import timezone

def create_sample_data():
    """Create some sample frequency data for testing"""
    print("Creating sample frequency data...")
    
    # Create sample data for number "23" over the past 60 days
    end_date = timezone.now().date()
    sample_dates = []
    
    # Number "23" appeared on these dates (sample pattern)
    for i in [5, 12, 18, 25, 35, 42, 55]:  # days ago
        date = end_date - timedelta(days=i)
        sample_dates.append(date)
    
    for date in sample_dates:
        NumberFrequencyStats.objects.get_or_create(
            number="23",
            date=date,
            defaults={
                'day_of_week': date.weekday(),
                'day_of_month': date.day,
                'week_of_month': (date.day - 1) // 7 + 1,
                'month': date.month,
                'year': date.year,
                'appeared_in_special': False,
                'appeared_in_first': True,
                'appeared_in_other': False
            }
        )
    
    print(f"Created sample data for {len(sample_dates)} dates")
    return sample_dates

def test_basic_analysis():
    """Test basic analysis without caching"""
    print("\n" + "="*50)
    print("TESTING BASIC FREQUENCY ANALYSIS")
    print("="*50)
    
    # Get all data for number "23"
    frequency_data = NumberFrequencyStats.objects.filter(
        number="23"
    ).order_by('-date')
    
    print(f"\nFound {frequency_data.count()} records for number '23'")
    
    if frequency_data.exists():
        print("\nRecent appearances:")
        for i, record in enumerate(frequency_data[:5]):
            print(f"   {i+1}. {record.date} (Thứ {record.day_of_week + 2})")
        
        # Calculate basic statistics
        dates = [record.date for record in frequency_data]
        dates.sort()
        
        # Calculate gaps between appearances
        gaps = []
        if len(dates) > 1:
            for i in range(len(dates) - 1):
                gap = (dates[i + 1] - dates[i]).days
                gaps.append(gap)
        
        print(f"\nBasic Statistics:")
        print(f"   • Total appearances: {len(dates)}")
        print(f"   • Last appearance: {dates[-1] if dates else 'None'}")
        print(f"   • First appearance: {dates[0] if dates else 'None'}")
        
        if gaps:
            avg_gap = sum(gaps) / len(gaps)
            print(f"   • Average gap: {avg_gap:.1f} days")
            print(f"   • Min gap: {min(gaps)} days")
            print(f"   • Max gap: {max(gaps)} days")
        
        # Current gap
        if dates:
            current_gap = (timezone.now().date() - dates[-1]).days
            print(f"   • Current gap: {current_gap} days")
        
        # Weekday analysis
        weekday_counts = {}
        for record in frequency_data:
            day_name = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'][record.day_of_week]
            weekday_counts[day_name] = weekday_counts.get(day_name, 0) + 1
        
        print(f"\nWeekday Pattern:")
        for day, count in weekday_counts.items():
            percentage = (count / frequency_data.count() * 100)
            print(f"   • {day}: {count} times ({percentage:.1f}%)")

def test_companion_analysis():
    """Test finding companion numbers"""
    print("\n" + "="*50)
    print("TESTING COMPANION NUMBER ANALYSIS")
    print("="*50)
    
    # Get dates when number "23" appeared
    appearance_dates = NumberFrequencyStats.objects.filter(
        number="23"
    ).values_list('date', flat=True)
    
    print(f"Number '23' appeared on {len(appearance_dates)} dates")
    
    # Find other numbers that appeared on the same dates
    companion_counts = {}
    
    for date in appearance_dates:
        other_numbers = NumberFrequencyStats.objects.filter(
            date=date
        ).exclude(number="23").values_list('number', flat=True)
        
        for other_number in other_numbers:
            companion_counts[other_number] = companion_counts.get(other_number, 0) + 1
    
    if companion_counts:
        print(f"\nCompanion Numbers (appeared together with '23'):")
        # Sort by frequency
        sorted_companions = sorted(companion_counts.items(), key=lambda x: x[1], reverse=True)
        
        for i, (number, count) in enumerate(sorted_companions[:10]):
            percentage = (count / len(appearance_dates) * 100)
            print(f"   {i+1}. Number '{number}': {count} times ({percentage:.1f}%)")
    else:
        print("No companion numbers found")

def main():
    """Main demo function"""
    print("🎰 BASIC LOTTERY FREQUENCY ANALYSIS DEMO")
    print("=" * 50)
    
    try:
        # Create sample data
        sample_dates = create_sample_data()
        
        # Test basic analysis
        test_basic_analysis()
        
        # Test companion analysis
        test_companion_analysis()
        
        print("\n" + "="*50)
        print("✅ BASIC DEMO COMPLETED SUCCESSFULLY!")
        print("="*50)
        print("\nBasic Features Demonstrated:")
        print("• ✅ Sample data creation")
        print("• ✅ Basic frequency analysis")
        print("• ✅ Gap calculation")
        print("• ✅ Weekday pattern analysis")
        print("• ✅ Companion number detection")
        
        print(f"\nNext steps:")
        print("• Run migrations to enable advanced caching")
        print("• Test advanced analysis features")
        print("• Integrate with web interface")
        
    except Exception as e:
        print(f"\n❌ Error during demo: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
