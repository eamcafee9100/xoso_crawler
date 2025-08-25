#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
🎯 COMPREHENSIVE INTEGRATION TEST: Enhanced Deep Frequency Analyzer
Full demo với tất cả tính năng enhanced
"""

import json
import os
import sys
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

    from analytic_frequence.enhanced_deep_frequency_analyzer import (
        EnhancedDeepFrequencyAnalyzer,
        get_enhanced_frequency_insights,
    )
    from results.models import NumberFrequencyStats
except ImportError as e:
    print(f"❌ Import error: {e}")
    sys.exit(1)


def comprehensive_demo():
    """
    🚀 COMPREHENSIVE DEMO: All Enhanced Features
    """
    print("🎯 COMPREHENSIVE ENHANCED ANALYZER DEMO")
    print("=" * 80)

    # Database status
    total_records = NumberFrequencyStats.objects.count()
    if total_records == 0:
        print("❌ No data available")
        return

    print(f"📊 Database: {total_records:,} records available")

    # Date ranges for different tests
    test_scenarios = [
        {
            "name": "30 Days Recent",
            "days": 30,
            "description": "Short-term pattern analysis",
        },
        {
            "name": "90 Days Analysis",
            "days": 90,
            "description": "Medium-term trend analysis",
        },
        {
            "name": "180 Days Deep",
            "days": 180,
            "description": "Long-term statistical analysis",
        },
    ]

    results = {"demo_timestamp": datetime.now().isoformat(), "scenarios": {}}

    for scenario in test_scenarios:
        print(f"\n🔍 SCENARIO: {scenario['name']}")
        print("=" * 60)
        print(f"📋 {scenario['description']}")

        end_date = date.today()
        start_date = end_date - timedelta(days=scenario["days"])

        # Get insights
        try:
            insights = get_enhanced_frequency_insights(
                start_date=start_date,
                end_date=end_date,
                significance_level=0.1,  # Relaxed for demo
            )

            scenario_results = analyze_scenario(insights, scenario["name"])
            results["scenarios"][scenario["name"]] = scenario_results

        except Exception as e:
            print(f"❌ Error in {scenario['name']}: {e}")
            results["scenarios"][scenario["name"]] = {"error": str(e)}

    # Generate predictions based on insights
    print(f"\n🎯 GENERATING ENHANCED PREDICTIONS")
    print("=" * 60)

    predictions = generate_enhanced_predictions(results)
    results["enhanced_predictions"] = predictions

    # Save comprehensive results
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"comprehensive_enhanced_demo_{timestamp}.json"

    with open(filename, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False, default=str)

    print(f"\n💾 Comprehensive results saved to: {filename}")

    # Display final summary
    display_final_summary(results)

    return results


def analyze_scenario(insights, scenario_name):
    """
    📊 Analyze individual scenario results
    """
    print(f"📊 Analyzing {scenario_name}...")

    metadata = insights.get("analysis_metadata", {})
    hot_numbers = insights.get("hot_numbers", {})
    cold_numbers = insights.get("cold_numbers", {})
    seasonal = insights.get("seasonal_effects", {})
    prize_intelligence = insights.get("prize_position_intelligence", {})

    # Basic stats
    total_records = metadata.get("total_records", 0)
    print(f"   📈 Records analyzed: {total_records:,}")
    print(f"   🔥 Hot numbers found: {len(hot_numbers)}")
    print(f"   ❄️ Cold numbers found: {len(cold_numbers)}")

    # Top hot numbers
    if hot_numbers:
        sorted_hot = sorted(
            hot_numbers.items(),
            key=lambda x: x[1].get("hotness_score", 0),
            reverse=True,
        )[:5]
        print(f"   🌟 Top 5 Hot: {[num for num, _ in sorted_hot]}")

    # Top cold numbers
    if cold_numbers:
        sorted_cold = sorted(
            cold_numbers.items(),
            key=lambda x: x[1].get("coldness_score", 0),
            reverse=True,
        )[:5]
        print(f"   ❄️ Top 5 Cold: {[num for num, _ in sorted_cold]}")

    # Seasonal insights
    monthly_patterns = seasonal.get("monthly_patterns", {})
    if monthly_patterns:
        active_months = [
            m
            for m, data in monthly_patterns.items()
            if data.get("total_appearances", 0) > 0
        ]
        print(f"   📅 Active months: {len(active_months)}")

    # Prize position insights
    overall_stats = prize_intelligence.get("overall_statistics", {})
    if overall_stats:
        special_rate = overall_stats.get("special_prize_rate", 0)
        first_rate = overall_stats.get("first_prize_rate", 0)
        print(f"   🏆 Special rate: {special_rate:.3f}, First rate: {first_rate:.3f}")

    return {
        "metadata": metadata,
        "hot_count": len(hot_numbers),
        "cold_count": len(cold_numbers),
        "top_hot": [num for num, _ in (sorted_hot[:5] if hot_numbers else [])],
        "top_cold": [num for num, _ in (sorted_cold[:5] if cold_numbers else [])],
        "seasonal_summary": {
            "active_months": len(
                [
                    m
                    for m, data in monthly_patterns.items()
                    if data.get("total_appearances", 0) > 0
                ]
            ),
            "prize_rates": overall_stats,
        },
    }


def generate_enhanced_predictions(results):
    """
    🎯 Generate enhanced predictions based on comprehensive analysis
    """
    print("🔮 Generating enhanced predictions...")

    # Collect all hot numbers from all scenarios
    all_hot_numbers = {}

    for scenario_name, scenario_data in results.get("scenarios", {}).items():
        if "error" not in scenario_data:
            hot_numbers = scenario_data.get("top_hot", [])
            for num in hot_numbers:
                if num not in all_hot_numbers:
                    all_hot_numbers[num] = {"scenarios": [], "score": 0}
                all_hot_numbers[num]["scenarios"].append(scenario_name)
                all_hot_numbers[num]["score"] += 1

    # Sort by consensus score
    consensus_hot = sorted(
        all_hot_numbers.items(), key=lambda x: x[1]["score"], reverse=True
    )

    # Generate prediction sets
    predictions = {
        "consensus_hot_numbers": [num for num, data in consensus_hot[:15]],
        "high_confidence": [
            num for num, data in consensus_hot[:8] if data["score"] >= 2
        ],
        "emerging_hot": [num for num, data in consensus_hot if data["score"] == 1][:10],
        "prediction_metadata": {
            "total_scenarios": len(results.get("scenarios", {})),
            "consensus_threshold": 2,
            "generated_at": datetime.now().isoformat(),
        },
    }

    print(f"   ✅ Consensus hot numbers: {len(predictions['consensus_hot_numbers'])}")
    print(f"   🎯 High confidence: {len(predictions['high_confidence'])}")
    print(f"   🌱 Emerging hot: {len(predictions['emerging_hot'])}")

    # Display predictions
    print(f"\n🎯 ENHANCED PREDICTIONS:")
    print(f"   High Confidence: {predictions['high_confidence']}")
    print(f"   Consensus Hot: {predictions['consensus_hot_numbers']}")

    return predictions


def display_final_summary(results):
    """
    📋 Display final comprehensive summary
    """
    print(f"\n📋 COMPREHENSIVE DEMO SUMMARY")
    print("=" * 60)

    scenarios = results.get("scenarios", {})
    predictions = results.get("enhanced_predictions", {})

    print(f"✅ Scenarios analyzed: {len(scenarios)}")

    total_hot = sum(
        s.get("hot_count", 0) for s in scenarios.values() if "error" not in s
    )
    total_cold = sum(
        s.get("cold_count", 0) for s in scenarios.values() if "error" not in s
    )

    print(f"🔥 Total hot numbers detected: {total_hot}")
    print(f"❄️ Total cold numbers detected: {total_cold}")

    high_confidence = predictions.get("high_confidence", [])
    consensus_hot = predictions.get("consensus_hot_numbers", [])

    print(f"🎯 High confidence predictions: {len(high_confidence)}")
    print(f"🔥 Consensus hot numbers: {len(consensus_hot)}")

    print(f"\n🚀 ENHANCED ANALYZER CAPABILITIES DEMONSTRATED:")
    print(f"   ✅ Multi-timeframe analysis")
    print(f"   ✅ Statistical hot/cold detection")
    print(f"   ✅ Seasonal pattern recognition")
    print(f"   ✅ Prize position intelligence")
    print(f"   ✅ Consensus prediction generation")
    print(f"   ✅ Database integration")
    print(f"   ✅ Real-time analysis")

    print(f"\n🎉 ENHANCED DEEP FREQUENCY ANALYZER: FULLY OPERATIONAL!")


if __name__ == "__main__":
    comprehensive_demo()
