#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
🚀 DEMO: Enhanced Deep Frequency Analyzer với dữ liệu thực
Test comprehensive frequency analysis với NumberFrequencyStats model
"""

import json
import os
import sys
from datetime import date, datetime, timedelta
from typing import Any, Dict


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
    print("💡 Hãy đảm bảo rằng:")
    print("   1. Virtual environment đã được activate")
    print("   2. Django và dependencies đã được cài đặt")
    print("   3. Settings file tồn tại và hợp lệ")
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
    print("💡 Hãy đảm bảo enhanced_deep_frequency_analyzer.py tồn tại")
    sys.exit(1)


class EnhancedFrequencyAnalyzerDemo:
    """
    🎯 Demo class cho Enhanced Deep Frequency Analyzer
    """

    def __init__(self):
        self.analyzer = EnhancedDeepFrequencyAnalyzer()

    def check_database_status(self) -> Dict[str, Any]:
        """
        🔍 Kiểm tra trạng thái database và dữ liệu
        """
        print("🔍 KIỂM TRA DATABASE STATUS...")
        print("=" * 60)

        status = {}

        try:
            # Tổng số records
            total_records = NumberFrequencyStats.objects.count()
            status["total_records"] = total_records
            print(f"📊 Tổng số records: {total_records:,}")

            if total_records == 0:
                print("❌ KHÔNG CÓ DỮ LIỆU trong NumberFrequencyStats!")
                return status

            # Date range
            earliest = NumberFrequencyStats.objects.order_by("date").first()
            latest = NumberFrequencyStats.objects.order_by("-date").first()

            if earliest and latest:
                status["date_range"] = {
                    "earliest": earliest.date.isoformat(),
                    "latest": latest.date.isoformat(),
                    "total_days": (latest.date - earliest.date).days + 1,
                }
                print(f"📅 Date range: {earliest.date} → {latest.date}")
                print(f"📅 Tổng số ngày: {(latest.date - earliest.date).days + 1} ngày")

            # Recent data (30 ngày gần đây)
            recent_cutoff = date.today() - timedelta(days=30)
            recent_count = NumberFrequencyStats.objects.filter(
                date__gte=recent_cutoff
            ).count()
            status["recent_30_days"] = recent_count
            print(f"📈 Dữ liệu 30 ngày gần đây: {recent_count:,} records")

            # Unique numbers
            unique_numbers = (
                NumberFrequencyStats.objects.values("number").distinct().count()
            )
            status["unique_numbers"] = unique_numbers
            print(f"🔢 Số lượng numbers unique: {unique_numbers}")

            # Sample numbers and their frequencies
            sample_numbers = (
                NumberFrequencyStats.objects.values("number")
                .annotate(count=models.Count("number"))
                .order_by("-count")[:10]
            )

            status["top_numbers"] = list(sample_numbers)
            print(f"\n🔥 Top 10 numbers xuất hiện nhiều nhất:")
            for item in sample_numbers:
                print(f"   {item['number']}: {item['count']} lần")

            # Prize position stats
            special_count = NumberFrequencyStats.objects.filter(
                appeared_in_special=True
            ).count()
            first_count = NumberFrequencyStats.objects.filter(
                appeared_in_first=True
            ).count()
            other_count = NumberFrequencyStats.objects.filter(
                appeared_in_other=True
            ).count()

            status["prize_positions"] = {
                "special": special_count,
                "first": first_count,
                "other": other_count,
            }

            print(f"\n🏆 Prize Position Distribution:")
            print(
                f"   Special: {special_count:,} ({special_count/total_records*100:.1f}%)"
            )
            print(f"   First: {first_count:,} ({first_count/total_records*100:.1f}%)")
            print(f"   Other: {other_count:,} ({other_count/total_records*100:.1f}%)")

            return status

        except Exception as e:
            print(f"❌ LỖI kiểm tra database: {e}")
            status["error"] = str(e)
            return status

    def run_basic_analysis_demo(self, days_back: int = 90) -> Dict[str, Any]:
        """
        🚀 Demo phân tích cơ bản với enhanced analyzer
        """
        print(f"\n🚀 DEMO PHÂN TÍCH CƠ BẢN ({days_back} ngày gần đây)...")
        print("=" * 60)

        try:
            # Set date range
            end_date = date.today()
            start_date = end_date - timedelta(days=days_back)

            print(f"📅 Phân tích từ {start_date} đến {end_date}")

            # Run enhanced analysis
            print("🔄 Đang chạy enhanced analysis...")
            insights = get_enhanced_frequency_insights(
                start_date=start_date, end_date=end_date, significance_level=0.05
            )

            # Display metadata
            metadata = insights.get("analysis_metadata", {})
            print(f"\n📊 METADATA:")
            print(f"   Records analyzed: {metadata.get('total_records', 'N/A')}")
            print(f"   Analysis timestamp: {metadata.get('analysis_timestamp', 'N/A')}")
            print(f"   Significance level: {metadata.get('significance_level', 'N/A')}")

            # Hot numbers analysis
            hot_numbers = insights.get("hot_numbers", {})
            print(f"\n🔥 HOT NUMBERS (Top 5):")
            if hot_numbers:
                sorted_hot = sorted(
                    hot_numbers.items(),
                    key=lambda x: x[1].get("hotness_score", 0),
                    reverse=True,
                )[:5]
                for num, data in sorted_hot:
                    print(
                        f"   {num}: Score={data.get('hotness_score', 0):.2f}, "
                        f"Freq={data.get('frequency', 0)}, "
                        f"P-value={data.get('p_value', 0):.4f}"
                    )
            else:
                print("   Không có hot numbers được phát hiện")

            # Cold numbers analysis
            cold_numbers = insights.get("cold_numbers", {})
            print(f"\n❄️ COLD NUMBERS (Top 5):")
            if cold_numbers:
                sorted_cold = sorted(
                    cold_numbers.items(),
                    key=lambda x: x[1].get("coldness_score", 0),
                    reverse=True,
                )[:5]
                for num, data in sorted_cold:
                    print(
                        f"   {num}: Score={data.get('coldness_score', 0):.2f}, "
                        f"Days absent={data.get('days_absent', 0)}, "
                        f"Reversion pressure={data.get('reversion_pressure', 0):.2f}"
                    )
            else:
                print("   Không có cold numbers được phát hiện")

            # Seasonal effects
            seasonal = insights.get("seasonal_effects", {})
            monthly_patterns = seasonal.get("monthly_patterns", {})

            if monthly_patterns:
                print(f"\n📅 SEASONAL PATTERNS (Monthly):")
                for month, data in list(monthly_patterns.items())[
                    :6
                ]:  # Show first 6 months
                    print(
                        f"   Tháng {month}: {data.get('total_appearances', 0)} appearances, "
                        f"Diversity: {data.get('diversity_score', 0):.2f}"
                    )

            # Prize position intelligence
            prize_intelligence = insights.get("prize_position_intelligence", {})
            overall_stats = prize_intelligence.get("overall_statistics", {})

            if overall_stats:
                print(f"\n🏆 PRIZE POSITION INTELLIGENCE:")
                print(
                    f"   Special prize rate: {overall_stats.get('special_prize_rate', 0):.3f}"
                )
                print(
                    f"   First prize rate: {overall_stats.get('first_prize_rate', 0):.3f}"
                )
                print(
                    f"   Other prize rate: {overall_stats.get('other_prize_rate', 0):.3f}"
                )

            return insights

        except Exception as e:
            print(f"❌ LỖI trong basic analysis: {e}")
            import traceback

            traceback.print_exc()
            return {"error": str(e)}

    def run_advanced_features_demo(self) -> Dict[str, Any]:
        """
        🎯 Demo các tính năng advanced mới
        """
        print(f"\n🎯 DEMO ADVANCED FEATURES...")
        print("=" * 60)

        try:
            # Test với dữ liệu 6 tháng gần đây
            end_date = date.today()
            start_date = end_date - timedelta(days=180)

            insights = get_enhanced_frequency_insights(
                start_date=start_date,
                end_date=end_date,
                significance_level=0.01,  # Stricter significance
            )

            # 1. Prize Position Specialists
            prize_intelligence = insights.get("prize_position_intelligence", {})
            specialized = prize_intelligence.get("specialized_numbers", {})

            print("🏆 PRIZE POSITION SPECIALISTS:")

            # Special specialists
            special_specialists = specialized.get("special_specialists", [])
            if special_specialists:
                print("   🌟 Special Prize Specialists:")
                for num, data in special_specialists[:3]:
                    print(
                        f"      {num}: {data['special_prize_rate']*100:.1f}% special rate, "
                        f"{data['total_appearances']} appearances"
                    )

            # First specialists
            first_specialists = specialized.get("first_specialists", [])
            if first_specialists:
                print("   🥇 First Prize Specialists:")
                for num, data in first_specialists[:3]:
                    print(
                        f"      {num}: {data['first_prize_rate']*100:.1f}% first rate, "
                        f"{data['total_appearances']} appearances"
                    )

            # 2. Day of Week Patterns
            seasonal = insights.get("seasonal_effects", {})
            dow_patterns = seasonal.get("day_of_week_patterns", {})

            if dow_patterns:
                print(f"\n📅 DAY OF WEEK PATTERNS:")
                days = [
                    "Monday",
                    "Tuesday",
                    "Wednesday",
                    "Thursday",
                    "Friday",
                    "Saturday",
                    "Sunday",
                ]
                for dow, data in dow_patterns.items():
                    day_name = data.get("day_name", f"Day {dow}")
                    print(
                        f"   {day_name}: {data.get('total_appearances', 0)} appearances, "
                        f"Special rate: {data.get('special_prize_rate', 0)*100:.1f}%"
                    )

            # 3. Statistical Tests Results
            statistical_tests = insights.get("statistical_tests", {})
            if statistical_tests:
                print(f"\n📊 STATISTICAL TESTS:")
                for test_name, results in statistical_tests.items():
                    print(f"   {test_name}: {results}")

            return insights

        except Exception as e:
            print(f"❌ LỖI trong advanced features demo: {e}")
            import traceback

            traceback.print_exc()
            return {"error": str(e)}

    def save_demo_results(self, results: Dict[str, Any], filename: str = ""):
        """
        💾 Lưu kết quả demo ra file JSON
        """
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"enhanced_frequency_demo_results_{timestamp}.json"

        try:
            # Convert date objects to strings for JSON serialization
            def json_serializer(obj):
                if isinstance(obj, (date, datetime)):
                    return obj.isoformat()
                raise TypeError(f"Object of type {type(obj)} is not JSON serializable")

            with open(filename, "w", encoding="utf-8") as f:
                json.dump(
                    results, f, indent=2, ensure_ascii=False, default=json_serializer
                )

            print(f"\n💾 Đã lưu kết quả demo vào: {filename}")
            print(f"   File size: {os.path.getsize(filename):,} bytes")

        except Exception as e:
            print(f"❌ LỖI lưu file: {e}")

    def run_performance_benchmark(self):
        """
        ⚡ Benchmark performance của enhanced analyzer
        """
        print(f"\n⚡ PERFORMANCE BENCHMARK...")
        print("=" * 60)

        import time

        test_cases = [
            {"days": 30, "name": "30 ngày"},
            {"days": 90, "name": "3 tháng"},
            {"days": 180, "name": "6 tháng"},
        ]

        for test_case in test_cases:
            try:
                print(f"\n🔄 Testing {test_case['name']}...")

                start_time = time.time()
                end_date = date.today()
                start_date = end_date - timedelta(days=test_case["days"])

                # Count records first
                record_count = NumberFrequencyStats.objects.filter(
                    date__range=[start_date, end_date]
                ).count()

                # Run analysis
                insights = get_enhanced_frequency_insights(
                    start_date=start_date, end_date=end_date
                )

                end_time = time.time()
                duration = end_time - start_time

                print(f"   ✅ {test_case['name']}: {duration:.2f}s")
                print(f"      Records processed: {record_count:,}")
                print(f"      Speed: {record_count/duration:.0f} records/second")

                # Memory usage estimation
                hot_count = len(insights.get("hot_numbers", {}))
                cold_count = len(insights.get("cold_numbers", {}))
                print(f"      Hot numbers found: {hot_count}")
                print(f"      Cold numbers found: {cold_count}")

            except Exception as e:
                print(f"   ❌ {test_case['name']}: {e}")


def main():
    """
    🎬 Main demo function
    """
    print("🚀 ENHANCED DEEP FREQUENCY ANALYZER DEMO")
    print("=" * 80)
    print(f"⏰ Demo started at: {datetime.now()}")
    print("=" * 80)

    demo = EnhancedFrequencyAnalyzerDemo()

    # 1. Check database status
    db_status = demo.check_database_status()

    if db_status.get("total_records", 0) == 0:
        print("\n❌ KHÔNG THỂ TIẾP TỤC: Không có dữ liệu trong NumberFrequencyStats")
        print("💡 Hãy đảm bảo rằng dữ liệu đã được import vào database")
        return

    # 2. Basic analysis demo
    print("\n" + "=" * 80)
    basic_results = demo.run_basic_analysis_demo(days_back=90)

    # 3. Advanced features demo
    print("\n" + "=" * 80)
    advanced_results = demo.run_advanced_features_demo()

    # 4. Performance benchmark
    print("\n" + "=" * 80)
    demo.run_performance_benchmark()

    # 5. Save results
    print("\n" + "=" * 80)
    all_results = {
        "demo_metadata": {
            "timestamp": datetime.now().isoformat(),
            "database_status": db_status,
        },
        "basic_analysis": basic_results,
        "advanced_features": advanced_results,
    }

    demo.save_demo_results(all_results)

    # 6. Summary
    print("\n" + "=" * 80)
    print("✅ DEMO COMPLETED SUCCESSFULLY!")
    print("=" * 80)
    print("📊 Summary:")
    print(f"   Database records: {db_status.get('total_records', 0):,}")
    print(f"   Hot numbers found: {len(basic_results.get('hot_numbers', {}))}")
    print(f"   Cold numbers found: {len(basic_results.get('cold_numbers', {}))}")
    print(
        f"   Analysis features: {len([k for k in basic_results.keys() if not k.startswith('analysis_')])}"
    )

    print("\n🎯 Next Steps:")
    print("   1. Review saved JSON results file")
    print("   2. Analyze hot/cold numbers for predictions")
    print("   3. Use seasonal patterns for timing")
    print("   4. Apply prize position intelligence")
    print("   5. Monitor statistical significance")


if __name__ == "__main__":
    main()
