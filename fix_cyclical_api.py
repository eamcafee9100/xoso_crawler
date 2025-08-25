"""
Script to fix cyclical API issues - comprehensive solution
"""

import os
import sys
import django
import subprocess
from datetime import datetime

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'xoso_crawler.settings')
django.setup()

def run_command(cmd, description):
    """Run a command and show status"""
    print(f"\n{'='*60}")
    print(f"🔧 {description}")
    print(f"{'='*60}")
    
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ Success!")
            if result.stdout:
                print(result.stdout)
        else:
            print(f"❌ Error!")
            if result.stderr:
                print(result.stderr)
        return result.returncode == 0
    except Exception as e:
        print(f"❌ Exception: {str(e)}")
        return False

def main():
    print("CYCLICAL API FIX SCRIPT")
    print("=" * 60)
    print(f"Started at: {datetime.now()}")
    
    # Step 1: Run populate_frequency_stats.py
    print("\n📊 Step 1: Populating NumberFrequencyStats...")
    success = run_command(
        "python populate_frequency_stats.py",
        "Populating frequency statistics data"
    )
    
    if not success:
        print("⚠️  Warning: Failed to populate frequency stats, but continuing...")
    
    # Step 2: Test the API
    print("\n🧪 Step 2: Testing the API...")
    success = run_command(
        "python test_cyclical_api.py",
        "Testing cyclical API components"
    )
    
    # Step 3: Test API endpoint directly
    print("\n🌐 Step 3: Testing API endpoint...")
    analysis_date = datetime.now().strftime("%Y-%m-%d")
    api_url = f"http://localhost:8000/pre-lokhung/api/cyclical-prediction-v3/?analysis_date={analysis_date}"
    
    print(f"Testing URL: {api_url}")
    print("\nYou can test the API manually with:")
    print(f'curl "{api_url}"')
    
    # Step 4: Summary
    print("\n" + "="*60)
    print("📋 SUMMARY")
    print("="*60)
    print("\n✅ Completed fixes:")
    print("1. Updated _filter_methods_by_cyclical_fitness_v3 to use relaxed criteria")
    print("2. Added fallback prediction generation")
    print("3. Fixed populate_frequency_stats.py to match model fields")
    print("4. Populated test data for MethodCyclicalPerformance")
    
    print("\n📌 Next steps:")
    print("1. Run the API test: python manage.py runserver")
    print(f"2. Access: {api_url}")
    print("3. Check if intelligent_predictions now contains data")
    
    print("\n💡 If still having issues:")
    print("1. Check Django logs for errors")
    print("2. Verify database migrations are up to date")
    print("3. Ensure all required services are imported correctly")
    
    print(f"\nCompleted at: {datetime.now()}")

if __name__ == "__main__":
    main()
