#!/usr/bin/env python3
"""
Test script để kiểm tra hệ thống prediction index badges
"""

import os
import sys
from datetime import date, datetime

import django

# ✅ SETUP DJANGO
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "xoso_crawler.settings")
django.setup()

from predictions_tracker.templatetags.pre_xs_tags import get_hit_badges_data


def test_prediction_index_badges():
    """Test prediction index badge generation"""
    print("🚀 Testing Prediction Index Badge System")
    print("=" * 50)

    # ✅ TEST DATA 1: Prediction index 0 trúng (priority cao)
    test_data_1 = {
        "has_data": True,
        "predicted_numbers": ["23", "45"],
        "tracking_results": [
            {
                "day": 1,
                "has_result": True,
                "hit_count": 2,
                "hit_numbers": [
                    "23",
                    "45",
                ],  # Cả 2 số đều trúng -> chỉ hiển thị index 0
                "results": {"db": "23456", "giai_nhat": "12345", "giai_2": "67890"},
            },
            {
                "day": 2,
                "has_result": True,
                "hit_count": 1,
                "hit_numbers": ["23"],  # Chỉ index 0 trúng
                "results": {"db": "23456", "giai_nhat": "67890", "giai_2": "12345"},
            },
            {
                "day": 3,
                "has_result": True,
                "hit_count": 0,
                "hit_numbers": [],  # Không có số nào trúng
                "results": {"db": "12345", "giai_nhat": "67890", "giai_2": "11111"},
            },
        ],
    }

    print("\n📋 Test Case 1: Priority Index 0 > Index 1")
    print(f"Predicted Numbers: {test_data_1['predicted_numbers']}")

    badges_1 = get_hit_badges_data(test_data_1)
    print(f"Found {len(badges_1)} badges (should be 2: day 1 and day 2)")
    for badge in badges_1:
        print(
            f"Day {badge['day']}: Index {badge['prediction_index']} - Number {badge['prediction_number']} - {badge['bg_color']}"
        )

    # ✅ TEST DATA 2: Chỉ prediction index 1 trúng (fallback)
    test_data_2 = {
        "has_data": True,
        "predicted_numbers": ["67", "23"],
        "tracking_results": [
            {
                "day": 1,
                "has_result": True,
                "hit_count": 1,
                "hit_numbers": ["23"],  # Chỉ index 1 trúng (index 0 không trúng)
                "results": {"db": "23456", "giai_nhat": "12345", "giai_2": "67890"},
            },
            {
                "day": 2,
                "has_result": True,
                "hit_count": 0,
                "hit_numbers": [],  # Không có số nào trúng
                "results": {"db": "11111", "giai_nhat": "22222", "giai_2": "33333"},
            },
        ],
    }

    print("\n📋 Test Case 2: Chỉ Index 1 trúng (fallback)")
    print(f"Predicted Numbers: {test_data_2['predicted_numbers']}")

    badges_2 = get_hit_badges_data(test_data_2)
    print(f"Found {len(badges_2)} badges (should be 1: day 1 with index 1)")
    for badge in badges_2:
        print(
            f"Day {badge['day']}: Index {badge['prediction_index']} - Number {badge['prediction_number']} - {badge['bg_color']}"
        )

    # ✅ TEST DATA 3: Không có số nào trúng
    test_data_3 = {
        "has_data": True,
        "predicted_numbers": ["12", "67"],
        "tracking_results": [
            {
                "day": 1,
                "has_result": True,
                "hit_count": 0,
                "hit_numbers": [],  # Không có số nào trúng
                "results": {"db": "33333", "giai_nhat": "44444", "giai_2": "55555"},
            }
        ],
    }

    print("\n📋 Test Case 3: Không có số nào trúng")
    print(f"Predicted Numbers: {test_data_3['predicted_numbers']}")

    badges_3 = get_hit_badges_data(test_data_3)
    print(f"Found {len(badges_3)} badges (should be 0: no hits)")
    for badge in badges_3:
        print(
            f"Day {badge['day']}: Index {badge['prediction_index']} - Number {badge['prediction_number']} - {badge['bg_color']}"
        )

    print("\n✅ All tests completed!")


if __name__ == "__main__":
    test_prediction_index_badges()
