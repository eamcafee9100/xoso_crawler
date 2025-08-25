#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🎯 Kép Lệch 3-Day Multi-Session Demo
Demo chạy nhiều phiên phân tích để đánh giá hiệu quả tổng hợp
"""

import os
import sys
from datetime import date, timedelta

# Add Django setup
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "xoso_crawler.settings")

try:
    import django

    django.setup()
    from results.models import KetQuaXoSo

    DJANGO_AVAILABLE = True
    print("✅ Django setup completed")
except Exception as e:
    print(f"❌ Django setup failed: {e}")
    DJANGO_AVAILABLE = False

from kep_lech_3day_prediction_template import KepLech3DayPredictor


def run_multi_session_demo():
    """
    🚀 Chạy demo với nhiều phiên phân tích
    """
    predictor = KepLech3DayPredictor()
    all_sessions = []

    # Chạy demo cho 5 phiên khác nhau
    demo_dates = [
        date(2025, 7, 15),  # Phiên 1
        date(2025, 7, 20),  # Phiên 2
        date(2025, 7, 25),  # Phiên 3
        date(2025, 7, 28),  # Phiên 4
        date(2025, 8, 1),  # Phiên 5
    ]

    print("🎯 STARTING MULTI-SESSION DEMO")
    print("=" * 70)

    for i, demo_date in enumerate(demo_dates, 1):
        print(f"\n📅 SESSION {i}: {demo_date}")
        print("-" * 50)

        try:
            # Chạy phân tích cho phiên này
            result = predictor.run_analysis_demo(demo_date)

            if result["success"] and "session" in result:
                session = result["session"]
                all_sessions.append(session)

                print(f"✅ Session {i} completed")
                print(f"   Predictions: {', '.join(session.predicted_numbers[:5])}...")
                print(f"   Confidence: {session.confidence_score:.2f}")
                if hasattr(session, "session_success"):
                    success_icon = "✅" if session.session_success else "❌"
                    print(
                        f"   Result: {success_icon} {'WIN' if session.session_success else 'LOSE'}"
                    )
                    print(f"   ROI: {session.roi_percentage:.1f}%")
                    if session.winning_day:
                        print(f"   Winning Day: {session.winning_day}")
            else:
                print(f"❌ Session {i} failed: {result.get('error', 'Unknown error')}")

        except Exception as e:
            print(f"❌ Session {i} error: {e}")

    # Tạo báo cáo tổng hợp
    if all_sessions:
        print("\n" + "=" * 70)
        print("📊 CREATING COMPREHENSIVE REPORT")
        print("=" * 70)

        comprehensive_report = predictor.create_analysis_report(all_sessions)

        # Hiển thị tóm tắt
        summary = comprehensive_report["summary"]
        print(f"\n📈 OVERALL PERFORMANCE:")
        print(f"   Total Sessions: {summary['total_sessions']}")
        print(f"   Successful Sessions: {summary['successful_sessions']}")
        print(f"   Success Rate: {summary['overall_success_rate']:.2%}")
        print(f"   Average Win Rate: {summary['average_win_rate']:.2%}")
        print(f"   Average ROI: {summary['average_roi_percentage']:.1f}%")
        print(f"   Total Profit/Loss: {summary['total_profit_loss']:,} VND")

        # Hiển thị phân tích winning day
        winning_dist = comprehensive_report["performance_analysis"][
            "winning_day_distribution"
        ]
        print(f"\n🎯 WINNING DAY DISTRIBUTION:")
        print(f"   Day 1: {winning_dist['day1']} sessions")
        print(f"   Day 2: {winning_dist['day2']} sessions")
        print(f"   Day 3: {winning_dist['day3']} sessions")
        print(f"   No Win: {winning_dist['no_win']} sessions")

        # Hiển thị khuyến nghị
        recommendations = comprehensive_report["recommendations"]
        print(f"\n💡 RECOMMENDATIONS:")
        for rec in recommendations:
            print(f"   {rec}")

        # Lưu báo cáo
        filename = (
            f"kep_lech_comprehensive_report_{date.today().strftime('%Y%m%d')}.json"
        )
        saved_file = predictor.save_results_to_json(comprehensive_report, filename)

        print(f"\n💾 Comprehensive report saved to: {saved_file}")

        return {
            "success": True,
            "total_sessions": len(all_sessions),
            "report": comprehensive_report,
            "saved_file": saved_file,
        }
    else:
        print("\n❌ No successful sessions to analyze")
        return {"success": False, "error": "No sessions completed"}


if __name__ == "__main__":
    result = run_multi_session_demo()

    if result["success"]:
        print(f"\n🎉 Multi-session demo completed!")
        print(f"📊 Analyzed {result['total_sessions']} sessions")
        print(f"📄 Report: {result['saved_file']}")
    else:
        print(f"\n❌ Demo failed: {result.get('error', 'Unknown error')}")
