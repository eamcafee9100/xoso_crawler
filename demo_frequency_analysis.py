#!/usr/bin/env python
"""
Demo script to test frequency analysis functionality
"""
import os
import sys
import django
from datetime import datetime, timedelta

# Setup Django
sys.path.insert(0, os.path.abspath('.'))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'xoso_crawler.settings')
django.setup()

# Now import Django models and services
from results.models import NumberFrequencyStats, NumberAnalysisCache
from results.services.frequency_analysis_service import get_frequency_analysis_service
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

def test_frequency_analysis():
    """Test the frequency analysis service"""
    print("\n" + "="*50)
    print("TESTING FREQUENCY ANALYSIS SERVICE")
    print("="*50)
    
    # Get the frequency analysis service
    service = get_frequency_analysis_service()
    
    # Test analysis for number "23"
    print("\nAnalyzing number '23'...")
    analysis = service.get_comprehensive_analysis("23")
    
    print(f"\nAnalysis Results for Number {analysis['number']}:")
    print("-" * 40)
    
    # Basic stats
    basic = analysis['basic_stats']
    print(f"📊 BASIC STATISTICS:")
    print(f"   • Last 30 days: {basic['appearances_30d']} appearances")
    print(f"   • Total appearances: {basic['total_appearances']}")
    print(f"   • Last appearance: {basic.get('last_appearance', 'None')}")
    
    # Gan analysis
    gan = analysis['gan_analysis']
    print(f"\n⏰ GAN ANALYSIS:")
    print(f"   • Current gan: {gan['current_gan_days']} days")
    print(f"   • Max gan ever: {gan['max_gan_days']} days")
    print(f"   • Average gan: {gan.get('avg_gan_days', 0)} days")
    
    # Cycle analysis
    cycle = analysis['cycle_analysis']
    print(f"\n🔄 CYCLE ANALYSIS:")
    print(f"   • Average cycle: {cycle['avg_cycle']} days")
    print(f"   • Median cycle: {cycle['median_cycle']} days")
    if 'min_cycle' in cycle:
        print(f"   • Min cycle: {cycle['min_cycle']} days")
        print(f"   • Max cycle: {cycle['max_cycle']} days")
    
    # Prediction probabilities
    prob = analysis['prediction_probabilities']
    print(f"\n🎯 PREDICTION PROBABILITIES:")
    print(f"   • Combined probability: {prob['combined']}%")
    print(f"   • Max gan based: {prob['max_gan_based']}%")
    
    # Weekday patterns
    weekday = analysis['weekday_patterns']
    if weekday:
        print(f"\n📅 WEEKDAY PATTERNS:")
        for day, data in weekday.items():
            print(f"   • {day}: {data['count']} times ({data['percentage']}%)")
    
    # Companion numbers
    companions = analysis['companion_numbers']
    if companions:
        print(f"\n👫 COMPANION NUMBERS (Top 5):")
        for comp in companions[:5]:
            print(f"   • {comp['number']}: {comp['co_occurrences']} times ({comp['percentage']}%)")
    
    return analysis

def test_cache_functionality():
    """Test the caching functionality"""
    print("\n" + "="*50)
    print("TESTING CACHE FUNCTIONALITY")
    print("="*50)
    
    # Check if cache was created
    cache_count = NumberAnalysisCache.objects.count()
    print(f"\nCache entries in database: {cache_count}")
    
    if cache_count > 0:
        latest_cache = NumberAnalysisCache.objects.latest('updated_at')
        print(f"Latest cache entry:")
        print(f"   • Number: {latest_cache.number}")
        print(f"   • Analysis date: {latest_cache.analysis_date}")
        print(f"   • Current gan: {latest_cache.current_gan_days} days")
        print(f"   • Appearances (30d): {latest_cache.appearances_30d}")
        print(f"   • Probability: {latest_cache.probability_next_appearance}%")

def test_batch_analysis():
    """Test batch analysis for multiple numbers"""
    print("\n" + "="*50)
    print("TESTING BATCH ANALYSIS")
    print("="*50)
    
    service = get_frequency_analysis_service()
    
    # Test with a few numbers
    test_numbers = ["00", "01", "23", "45", "67", "99"]
    print(f"\nAnalyzing numbers: {', '.join(test_numbers)}")
    
    batch_results = service.get_batch_analysis_summary(test_numbers)
    
    print(f"\nBatch Analysis Results:")
    print("-" * 40)
    for number, data in batch_results.items():
        print(f"Number {number}:")
        print(f"   • Gan: {data['current_gan_days']} days")
        print(f"   • Probability: {data['probability']}%")
        print(f"   • Appearances (30d): {data['appearances_30d']}")

def main():
    """Main demo function"""
    print("🎰 LOTTERY FREQUENCY ANALYSIS DEMO")
    print("=" * 50)
    
    try:
        # Create sample data
        sample_dates = create_sample_data()
        
        # Test frequency analysis
        analysis = test_frequency_analysis()
        
        # Test cache functionality
        test_cache_functionality()
        
        # Test batch analysis
        test_batch_analysis()
        
        print("\n" + "="*50)
        print("✅ DEMO COMPLETED SUCCESSFULLY!")
        print("="*50)
        print("\nKey Features Demonstrated:")
        print("• ✅ Frequency analysis calculation")
        print("• ✅ Gan (absence) period tracking")
        print("• ✅ Cycle pattern analysis")
        print("• ✅ Prediction probability calculation")
        print("• ✅ Weekday pattern analysis")
        print("• ✅ Companion number detection")
        print("• ✅ Cache functionality")
        print("• ✅ Batch analysis")
        
        print(f"\nReady for integration with Django views and templates!")
        
    except Exception as e:
        print(f"\n❌ Error during demo: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
