"""
Sample data check for lottery results
"""

import os

import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "xoso_crawler.settings")
django.setup()

from datetime import date, timedelta

from results.models import KetQuaXoSo


def check_sample_data():
    print("🔍 CHECKING LOTTERY RESULT DATA STRUCTURE")
    print("=" * 50)

    # Get recent data
    recent_results = KetQuaXoSo.objects.order_by("-ngay")[:3]

    for result in recent_results:
        numbers = list(result.get_all_2digit_numbers())
        unique_numbers = list(set(numbers))
        unique_numbers.sort()

        print(f"📅 Date: {result.ngay} ({result.thu})")
        print(f"🔢 All 2-digit numbers: {numbers[:20]}... (total: {len(numbers)})")
        print(
            f"🎯 Unique numbers: {unique_numbers[:20]}... (total: {len(unique_numbers)})"
        )
        print(f"📊 Coverage: {len(unique_numbers)}/100 possible 2-digit numbers")
        print("---")

    print(f"\n📈 TOTAL RECORDS IN DATABASE: {KetQuaXoSo.objects.count()}")


if __name__ == "__main__":
    check_sample_data()
