"""
Quick data check for Phase 2A APIs
"""

import os
import sys

import django

# Setup Django
sys.path.append(os.path.abspath("."))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "xoso_crawler.settings")
django.setup()

from datetime import datetime, timedelta

from results.models import KetQuaXoSo


def check_lottery_data():
    """Check available lottery data"""
    total_records = KetQuaXoSo.objects.count()
    print(f"📊 Total lottery records: {total_records}")

    if total_records > 0:
        # Recent records
        recent = KetQuaXoSo.objects.order_by("-ngay")[:5]
        print(f"📅 Recent records:")
        for record in recent:
            print(f"  - {record.ngay}: {record.giai_db}")

        # Date range
        earliest = KetQuaXoSo.objects.order_by("ngay").first()
        latest = KetQuaXoSo.objects.order_by("-ngay").first()
        print(f"📈 Date range: {earliest.ngay} to {latest.ngay}")

        # Last 30 days
        thirty_days_ago = datetime.now().date() - timedelta(days=30)
        recent_count = KetQuaXoSo.objects.filter(ngay__gte=thirty_days_ago).count()
        print(f"🗓️  Records in last 30 days: {recent_count}")

    else:
        print("❌ No lottery data found!")
        print("💡 Need to populate database with lottery results first")


if __name__ == "__main__":
    check_lottery_data()
