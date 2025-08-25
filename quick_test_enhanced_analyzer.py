#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
🚀 DEMO: QUICK TEST Enhanced Deep Frequency Analyzer
Test với threshold thấp hơn để xem hot/cold numbers
"""

import json
import os
import sys
from datetime import date, datetime, timedelta


# Setup Django environment
def setup_django():
    """Setup Django environment safely"""
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


# Try to setup Django
if not setup_django():
    print("❌ Không thể khởi tạo Django environment")
    sys.exit(1)

try:
    import numpy as np
    from django.db import models
    from scipy.stats import chisquare

    from analytic_frequence.enhanced_deep_frequency_analyzer import (
        EnhancedDeepFrequencyAnalyzer,
        get_enhanced_frequency_insights,
    )
    from results.models import NumberFrequencyStats
except ImportError as e:
    print(f"❌ Import error: {e}")
    sys.exit(1)


def quick_hot_cold_analysis():
    """
    🔥 Quick test để tìm hot/cold numbers với threshold relaxed
    """
    print("🔥 QUICK HOT/COLD ANALYSIS")
    print("=" * 50)

    # Get data for last 3 months
    end_date = date.today()
    start_date = end_date - timedelta(days=90)

    queryset = NumberFrequencyStats.objects.filter(date__range=[start_date, end_date])

    total_records = queryset.count()
    total_days = queryset.values("date").distinct().count()

    print(f"📊 Data: {total_records} records over {total_days} days")

    if total_days == 0:
        print("❌ No data found")
        return

    # Expected frequency per number
    expected_freq = total_days * 0.01  # Assuming 1% chance per number per day
    print(f"📈 Expected frequency per number: {expected_freq:.2f}")

    hot_numbers = {}
    cold_numbers = {}

    # Analyze each number with RELAXED thresholds
    for number in range(100):
        num_str = str(number).zfill(2)

        number_stats = queryset.filter(number=num_str)
        observed_freq = number_stats.count()

        if observed_freq == 0:
            # Very cold number
            cold_numbers[num_str] = {
                "frequency": 0,
                "expected": expected_freq,
                "days_absent": total_days,
                "coldness_score": expected_freq,  # High coldness for zero frequency
            }
            continue

        # Calculate ratio
        freq_ratio = observed_freq / expected_freq if expected_freq > 0 else 0

        # RELAXED Hot number criteria (15% above expected)
        if freq_ratio > 1.15:
            recent_count = number_stats.filter(
                date__gte=end_date - timedelta(days=30)
            ).count()

            hot_numbers[num_str] = {
                "frequency": observed_freq,
                "expected": round(expected_freq, 2),
                "ratio": round(freq_ratio, 2),
                "recent_30_days": recent_count,
                "hotness_score": round(freq_ratio * (1 + recent_count / 30), 2),
            }

        # RELAXED Cold number criteria (15% below expected)
        elif freq_ratio < 0.85:
            last_appearance = number_stats.order_by("-date").first()
            days_absent = (
                (end_date - last_appearance.date).days
                if last_appearance
                else total_days
            )

            cold_numbers[num_str] = {
                "frequency": observed_freq,
                "expected": round(expected_freq, 2),
                "ratio": round(freq_ratio, 2),
                "days_absent": days_absent,
                "coldness_score": round(
                    (expected_freq - observed_freq) * (1 + days_absent / 30), 2
                ),
            }

    # Display results
    print(f"\n🔥 HOT NUMBERS (Top 10):")
    sorted_hot = sorted(
        hot_numbers.items(), key=lambda x: x[1]["hotness_score"], reverse=True
    )[:10]
    for num, data in sorted_hot:
        print(
            f"   {num}: {data['frequency']} times (expected: {data['expected']}) - Ratio: {data['ratio']}"
        )

    print(f"\n❄️ COLD NUMBERS (Top 10):")
    sorted_cold = sorted(
        cold_numbers.items(), key=lambda x: x[1]["coldness_score"], reverse=True
    )[:10]
    for num, data in sorted_cold:
        print(
            f"   {num}: {data['frequency']} times (expected: {data['expected']}) - Ratio: {data['ratio']}"
        )

    # Prize position analysis for hot numbers
    if sorted_hot:
        print(f"\n🏆 PRIZE POSITION ANALYSIS (Hot Numbers):")
        for num, _ in sorted_hot[:5]:
            num_stats = queryset.filter(number=num)
            total = num_stats.count()
            special = num_stats.filter(appeared_in_special=True).count()
            first = num_stats.filter(appeared_in_first=True).count()
            other = num_stats.filter(appeared_in_other=True).count()

            print(
                f"   {num} ({total} times): Special={special}, First={first}, Other={other}"
            )

    return {
        "hot_numbers": dict(sorted_hot),
        "cold_numbers": dict(sorted_cold),
        "summary": {
            "total_records": total_records,
            "total_days": total_days,
            "expected_freq": expected_freq,
            "hot_count": len(hot_numbers),
            "cold_count": len(cold_numbers),
        },
    }


def test_seasonal_patterns():
    """
    📅 Test seasonal patterns
    """
    print(f"\n📅 SEASONAL PATTERNS TEST")
    print("=" * 50)

    end_date = date.today()
    start_date = end_date - timedelta(days=180)  # 6 months

    queryset = NumberFrequencyStats.objects.filter(date__range=[start_date, end_date])

    # Monthly distribution
    monthly_stats = {}
    for month in range(1, 13):
        month_data = queryset.filter(month=month)
        count = month_data.count()
        if count > 0:
            monthly_stats[month] = {
                "total": count,
                "unique_numbers": month_data.values("number").distinct().count(),
            }

    print("📊 Monthly Distribution:")
    for month, data in monthly_stats.items():
        month_names = [
            "",
            "Jan",
            "Feb",
            "Mar",
            "Apr",
            "May",
            "Jun",
            "Jul",
            "Aug",
            "Sep",
            "Oct",
            "Nov",
            "Dec",
        ]
        print(
            f"   {month_names[month]}: {data['total']} records, {data['unique_numbers']} unique numbers"
        )

    # Day of week patterns
    dow_stats = {}
    for dow in range(7):
        dow_data = queryset.filter(day_of_week=dow)
        count = dow_data.count()
        if count > 0:
            dow_stats[dow] = count

    if dow_stats:
        print(f"\n📅 Day of Week Distribution:")
        days = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
        for dow, count in dow_stats.items():
            day_name = days[dow] if dow < len(days) else f"Day{dow}"
            print(f"   {day_name}: {count} records")

    return {"monthly": monthly_stats, "day_of_week": dow_stats}


def main():
    """
    🎬 Main quick test
    """
    print("🚀 QUICK TEST: Enhanced Frequency Analyzer")
    print("=" * 80)

    # 1. Database check
    total_records = NumberFrequencyStats.objects.count()
    print(f"📊 Total database records: {total_records:,}")

    if total_records == 0:
        print("❌ No data in NumberFrequencyStats")
        return

    # 2. Quick hot/cold analysis
    hc_results = quick_hot_cold_analysis()

    # 3. Seasonal patterns test
    seasonal_results = test_seasonal_patterns()

    # 4. Save results
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"quick_test_results_{timestamp}.json"

    results = {
        "timestamp": datetime.now().isoformat(),
        "hot_cold_analysis": hc_results,
        "seasonal_patterns": seasonal_results,
    }

    with open(filename, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False, default=str)

    print(f"\n💾 Results saved to: {filename}")
    print("✅ Quick test completed!")


if __name__ == "__main__":
    main()
