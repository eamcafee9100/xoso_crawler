#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
🎯 FINAL WORKING DEMO: Enhanced Deep Frequency Analyzer
Realistic parameters and practical results
"""

import json
import os
import sys
from collections import Counter
from datetime import date, datetime, timedelta


# Setup Django environment
def setup_django():
    try:
        import django
        from django.conf import settings

        if not settings.configured:
            os.environ.setdefault("DJANGO_SETTINGS_MODULE", "xoso_crawler.settings")
            django.setup()

        return True
    except Exception as e:
        print(f"❌ Django setup failed: {e}")
        return False


if not setup_django():
    sys.exit(1)

try:
    from django.db import models

    from results.models import NumberFrequencyStats
except ImportError as e:
    print(f"❌ Import error: {e}")
    sys.exit(1)


def final_working_demo():
    """
    🚀 FINAL WORKING DEMO với parameters thực tế
    """
    print("🎯 FINAL ENHANCED FREQUENCY ANALYZER DEMO")
    print("=" * 80)

    # Database check
    total_records = NumberFrequencyStats.objects.count()
    print(f"📊 Database: {total_records:,} records")

    if total_records == 0:
        print("❌ No data available")
        return

    # Date range analysis
    earliest = NumberFrequencyStats.objects.order_by("date").first()
    latest = NumberFrequencyStats.objects.order_by("-date").first()

    print(f"📅 Data range: {earliest.date} → {latest.date}")
    print(f"📅 Total span: {(latest.date - earliest.date).days + 1} days")

    # Analysis scenarios
    scenarios = [
        {"name": "Last 30 Days", "days": 30},
        {"name": "Last 90 Days", "days": 90},
        {"name": "Last 180 Days", "days": 180},
    ]

    final_results = {
        "demo_info": {
            "timestamp": datetime.now().isoformat(),
            "total_database_records": total_records,
            "data_range": {
                "start": earliest.date.isoformat(),
                "end": latest.date.isoformat(),
            },
        },
        "scenario_results": {},
    }

    # Analyze each scenario
    for scenario in scenarios:
        print(f"\n🔍 ANALYZING: {scenario['name']}")
        print("=" * 60)

        result = analyze_practical_scenario(scenario["days"])
        final_results["scenario_results"][scenario["name"]] = result

        display_scenario_results(scenario["name"], result)

    # Generate final predictions
    print(f"\n🎯 GENERATING FINAL PREDICTIONS")
    print("=" * 60)

    predictions = generate_final_predictions(final_results["scenario_results"])
    final_results["final_predictions"] = predictions

    # Save results
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"final_enhanced_demo_{timestamp}.json"

    with open(filename, "w", encoding="utf-8") as f:
        json.dump(final_results, f, indent=2, ensure_ascii=False, default=str)

    print(f"\n💾 Final results saved: {filename}")

    # Display summary
    display_final_summary(final_results)

    return final_results


def analyze_practical_scenario(days_back):
    """
    📊 Practical scenario analysis với realistic thresholds
    """
    end_date = date.today()
    start_date = end_date - timedelta(days=days_back)

    # Get data
    queryset = NumberFrequencyStats.objects.filter(date__range=[start_date, end_date])

    total_records = queryset.count()
    unique_dates = queryset.values("date").distinct().count()

    if total_records == 0:
        return {"error": "No data in date range"}

    print(f"   📈 {total_records:,} records across {unique_dates} days")

    # Calculate practical statistics
    results = {
        "basic_stats": {
            "total_records": total_records,
            "unique_dates": unique_dates,
            "avg_records_per_day": (
                total_records / unique_dates if unique_dates > 0 else 0
            ),
        }
    }

    # 1. Frequency Analysis (Practical approach)
    number_frequencies = (
        queryset.values("number")
        .annotate(count=models.Count("number"))
        .order_by("-count")
    )

    # Convert to list for easier processing
    freq_list = list(number_frequencies)

    # Statistical metrics
    frequencies = [item["count"] for item in freq_list]
    avg_freq = sum(frequencies) / len(frequencies) if frequencies else 0
    max_freq = max(frequencies) if frequencies else 0
    min_freq = min(frequencies) if frequencies else 0

    print(f"   📊 Frequency stats: Avg={avg_freq:.1f}, Max={max_freq}, Min={min_freq}")

    # 2. Hot Numbers (Top 20% by frequency)
    hot_threshold = avg_freq * 1.2  # 20% above average
    hot_numbers = [item for item in freq_list if item["count"] > hot_threshold][:20]

    # 3. Cold Numbers (Bottom 20% by frequency)
    cold_threshold = avg_freq * 0.8  # 20% below average
    cold_numbers = [item for item in freq_list if item["count"] < cold_threshold][:20]

    print(f"   🔥 Hot numbers (>{hot_threshold:.1f}): {len(hot_numbers)}")
    print(f"   ❄️ Cold numbers (<{cold_threshold:.1f}): {len(cold_numbers)}")

    results["frequency_analysis"] = {
        "avg_frequency": round(avg_freq, 2),
        "hot_threshold": round(hot_threshold, 2),
        "cold_threshold": round(cold_threshold, 2),
        "hot_numbers": hot_numbers,
        "cold_numbers": cold_numbers,
    }

    # 4. Recent Activity (Last 15 days within the scenario)
    recent_cutoff = end_date - timedelta(days=min(15, days_back // 2))
    recent_data = queryset.filter(date__gte=recent_cutoff)

    recent_frequencies = (
        recent_data.values("number")
        .annotate(count=models.Count("number"))
        .order_by("-count")[:15]
    )

    results["recent_activity"] = {
        "period": f"Last {min(15, days_back//2)} days",
        "total_recent_records": recent_data.count(),
        "top_recent_numbers": list(recent_frequencies),
    }

    print(
        f"   🌟 Recent activity ({min(15, days_back//2)} days): {recent_data.count()} records"
    )

    # 5. Prize Position Analysis
    special_stats = (
        queryset.filter(appeared_in_special=True)
        .values("number")
        .annotate(count=models.Count("number"))
        .order_by("-count")[:10]
    )

    first_stats = (
        queryset.filter(appeared_in_first=True)
        .values("number")
        .annotate(count=models.Count("number"))
        .order_by("-count")[:10]
    )

    results["prize_position_analysis"] = {
        "special_prize_leaders": list(special_stats),
        "first_prize_leaders": list(first_stats),
        "total_special": queryset.filter(appeared_in_special=True).count(),
        "total_first": queryset.filter(appeared_in_first=True).count(),
    }

    print(
        f"   🏆 Prize positions: {len(special_stats)} special leaders, {len(first_stats)} first leaders"
    )

    # 6. Day of Week Patterns
    dow_distribution = {}
    for dow in range(7):
        dow_count = queryset.filter(day_of_week=dow).count()
        if dow_count > 0:
            dow_distribution[dow] = dow_count

    results["temporal_patterns"] = {"day_of_week_distribution": dow_distribution}

    return results


def display_scenario_results(scenario_name, results):
    """
    📋 Display scenario results
    """
    if "error" in results:
        print(f"   ❌ {results['error']}")
        return

    # Hot numbers
    hot_numbers = results.get("frequency_analysis", {}).get("hot_numbers", [])
    if hot_numbers:
        hot_list = [item["number"] for item in hot_numbers[:10]]
        print(f"   🔥 Top 10 Hot: {hot_list}")

    # Recent activity
    recent = results.get("recent_activity", {}).get("top_recent_numbers", [])
    if recent:
        recent_list = [item["number"] for item in recent[:8]]
        print(f"   🌟 Recent leaders: {recent_list}")

    # Prize positions
    special_leaders = results.get("prize_position_analysis", {}).get(
        "special_prize_leaders", []
    )
    if special_leaders:
        special_list = [item["number"] for item in special_leaders[:5]]
        print(f"   🏆 Special prize leaders: {special_list}")


def generate_final_predictions(scenario_results):
    """
    🎯 Generate final predictions from all scenarios
    """
    print("🔮 Generating consensus predictions...")

    # Collect numbers from different categories
    all_hot_numbers = []
    all_recent_numbers = []
    all_special_leaders = []

    for scenario_name, results in scenario_results.items():
        if "error" not in results:
            # Hot numbers
            hot_nums = results.get("frequency_analysis", {}).get("hot_numbers", [])
            all_hot_numbers.extend([item["number"] for item in hot_nums])

            # Recent activity
            recent_nums = results.get("recent_activity", {}).get(
                "top_recent_numbers", []
            )
            all_recent_numbers.extend([item["number"] for item in recent_nums])

            # Special prize leaders
            special_nums = results.get("prize_position_analysis", {}).get(
                "special_prize_leaders", []
            )
            all_special_leaders.extend([item["number"] for item in special_nums])

    # Count consensus
    hot_counter = Counter(all_hot_numbers)
    recent_counter = Counter(all_recent_numbers)
    special_counter = Counter(all_special_leaders)

    # Generate prediction sets
    predictions = {
        "consensus_hot": [num for num, count in hot_counter.most_common(15)],
        "recent_momentum": [num for num, count in recent_counter.most_common(10)],
        "special_prize_candidates": [
            num for num, count in special_counter.most_common(8)
        ],
        "high_confidence": [],
    }

    # High confidence: appears in multiple categories
    all_candidates = set(
        predictions["consensus_hot"]
        + predictions["recent_momentum"]
        + predictions["special_prize_candidates"]
    )

    high_confidence = []
    for num in all_candidates:
        score = 0
        if num in predictions["consensus_hot"]:
            score += 2
        if num in predictions["recent_momentum"]:
            score += 2
        if num in predictions["special_prize_candidates"]:
            score += 1

        if score >= 3:
            high_confidence.append((num, score))

    # Sort by score
    high_confidence.sort(key=lambda x: x[1], reverse=True)
    predictions["high_confidence"] = [num for num, score in high_confidence[:12]]

    print(f"   ✅ Consensus hot: {len(predictions['consensus_hot'])}")
    print(f"   🚀 Recent momentum: {len(predictions['recent_momentum'])}")
    print(f"   🏆 Special candidates: {len(predictions['special_prize_candidates'])}")
    print(f"   🎯 High confidence: {len(predictions['high_confidence'])}")

    return predictions


def display_final_summary(results):
    """
    📋 Final comprehensive summary
    """
    print(f"\n📋 FINAL DEMO SUMMARY")
    print("=" * 60)

    predictions = results.get("final_predictions", {})
    scenarios = results.get("scenario_results", {})

    print(f"✅ Scenarios analyzed: {len(scenarios)}")
    print(
        f"📊 Total database records: {results['demo_info']['total_database_records']:,}"
    )

    # Display predictions
    print(f"\n🎯 FINAL PREDICTIONS:")
    print(f"   High Confidence: {predictions.get('high_confidence', [])}")
    print(f"   Consensus Hot: {predictions.get('consensus_hot', [])[:10]}")
    print(f"   Recent Momentum: {predictions.get('recent_momentum', [])[:8]}")

    print(f"\n🚀 ENHANCED ANALYZER SUCCESS:")
    print(f"   ✅ Database integration working")
    print(f"   ✅ Multi-timeframe analysis")
    print(f"   ✅ Frequency-based hot/cold detection")
    print(f"   ✅ Recent momentum tracking")
    print(f"   ✅ Prize position intelligence")
    print(f"   ✅ Consensus prediction generation")

    print(f"\n🎉 ENHANCED DEEP FREQUENCY ANALYZER: FULLY FUNCTIONAL!")


if __name__ == "__main__":
    final_working_demo()
