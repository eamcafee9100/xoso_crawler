#!/usr/bin/env python
"""
🔧 DEBUG SEPARATION ANALYSIS SCRIPT
"""

import os

import django

# Setup Django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "xoso_crawler.settings")
django.setup()

from datetime import datetime, timedelta

from predictions_tracker.views import (
    _analyze_methods_comprehensive,
    _filter_low_risk_methods_by_day_enhanced,
    _get_comprehensive_historical_data,
)


def debug_separation():
    print("🔧 DEBUGGING SEPARATION ANALYSIS")
    print("=" * 60)

    analysis_date = datetime.strptime("2025-07-15", "%Y-%m-%d").date()
    end_date = analysis_date - timedelta(days=1)

    print(f"Analysis date: {analysis_date}")
    print(f"End date: {end_date}")

    # Step 1: Get historical data
    print("\n📊 Step 1: Getting historical data...")
    historical_data = _get_comprehensive_historical_data(
        target_date=end_date.strftime("%Y-%m-%d"), method_ids=None, months_back=3
    )

    if not historical_data:
        print("❌ No historical data found!")
        return

    total_methods = len(historical_data.get("hit_day_1", {}))
    print(f"✅ Historical data found: {total_methods} methods")

    # Step 2: Analyze methods
    print("\n🔍 Step 2: Analyzing methods...")
    method_analysis_results = _analyze_methods_comprehensive(
        historical_data, analysis_date, end_date
    )

    print(f"✅ Methods analyzed: {len(method_analysis_results)}")

    # Check risk levels distribution
    risk_levels = {}
    for method_id, analysis in method_analysis_results.items():
        risk_level = analysis["risk_level"]
        risk_levels[risk_level] = risk_levels.get(risk_level, 0) + 1

    print(f"📊 Risk level distribution: {risk_levels}")

    # Step 3: Filter methods
    print("\n🎯 Step 3: Filtering low risk methods...")
    filtered_methods = _filter_low_risk_methods_by_day_enhanced(
        method_analysis_results, min_evaluations=10, limit=15
    )

    # Step 4: Analyze separation
    print("\n=== SEPARATION ANALYSIS ===")
    print(f"Day 1 methods: {len(filtered_methods['day_1_methods'])}")
    day_1_best_days = [m["best_day"] for m in filtered_methods["day_1_methods"]]
    print(f"Day 1 best_days: {day_1_best_days}")

    print(f"Day 2 methods: {len(filtered_methods['day_2_methods'])}")
    day_2_best_days = [m["best_day"] for m in filtered_methods["day_2_methods"]]
    print(f"Day 2 best_days: {day_2_best_days}")

    print(f"Day 3 methods: {len(filtered_methods['day_3_methods'])}")
    day_3_best_days = [m["best_day"] for m in filtered_methods["day_3_methods"]]
    print(f"Day 3 best_days: {day_3_best_days}")

    # Check strict separation
    day_1_strict = all(bd == 1 for bd in day_1_best_days)
    day_2_strict = all(bd == 2 for bd in day_2_best_days)
    day_3_strict = all(bd == 3 for bd in day_3_best_days)

    print(f"\n🔍 STRICT SEPARATION CHECK:")
    print(f"Day 1 strict (all best_day=1): {day_1_strict}")
    print(f"Day 2 strict (all best_day=2): {day_2_strict}")
    print(f"Day 3 strict (all best_day=3): {day_3_strict}")
    print(
        f"Overall strict separation: {day_1_strict and day_2_strict and day_3_strict}"
    )

    # Show some examples
    if filtered_methods["day_1_methods"]:
        print(f"\n📋 Day 1 Examples:")
        for i, method in enumerate(filtered_methods["day_1_methods"][:3]):
            print(
                f"  {i+1}. Method {method['method_id']}: best_day={method['best_day']}, hit_rates={method['hit_rates']}"
            )

    if filtered_methods["day_2_methods"]:
        print(f"\n📋 Day 2 Examples:")
        for i, method in enumerate(filtered_methods["day_2_methods"][:3]):
            print(
                f"  {i+1}. Method {method['method_id']}: best_day={method['best_day']}, hit_rates={method['hit_rates']}"
            )

    if filtered_methods["day_3_methods"]:
        print(f"\n📋 Day 3 Examples:")
        for i, method in enumerate(filtered_methods["day_3_methods"][:3]):
            print(
                f"  {i+1}. Method {method['method_id']}: best_day={method['best_day']}, hit_rates={method['hit_rates']}"
            )


if __name__ == "__main__":
    debug_separation()
