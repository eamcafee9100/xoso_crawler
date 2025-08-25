"""
🎯 Kép Lệch Simple Performance Test
=================================
Test đơn giản để kiểm tra hệ thống
"""

import os
import sys
from datetime import date, timedelta

import django

# Setup Django
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "xoso_crawler.settings")
django.setup()

from results.models import KetQuaXoSo


def simple_kep_lech_test():
    """Test đơn giản cho Kép Lệch"""
    print("🎯 SIMPLE KÉP LỆCH TEST")
    print("=" * 40)

    # Bộ số Kép Lệch
    KEP_DUONG = [
        "05",
        "50",
        "16",
        "61",
        "27",
        "72",
        "38",
        "83",
        "49",
        "94",
        "06",
        "60",
        "07",
        "70",
        "08",
        "80",
        "09",
        "90",
        "15",
        "51",
        "26",
        "62",
        "37",
        "73",
        "48",
        "84",
        "59",
        "95",
        "13",
        "31",
        "24",
        "42",
        "35",
        "53",
        "46",
        "64",
        "57",
        "75",
        "68",
        "86",
    ]

    KEP_AM = ["07", "70", "14", "41", "29", "92", "36", "63", "58", "85"]

    SAT_KEP = [
        "04",
        "40",
        "06",
        "60",
        "15",
        "51",
        "95",
        "59",
        "17",
        "71",
        "14",
        "41",
        "28",
        "82",
        "26",
        "62",
        "37",
        "73",
        "36",
        "63",
        "39",
        "93",
        "48",
        "84",
    ]

    def kiem_tra_kep(so):
        if so in KEP_DUONG:
            return "Dương"
        if so in KEP_AM:
            return "Âm"
        if so in SAT_KEP:
            return "Sát kép"
        return None

    # Kiểm tra dữ liệu
    total_results = KetQuaXoSo.objects.count()
    print(f"📊 Tổng số kết quả: {total_results}")

    if total_results == 0:
        print("❌ Không có dữ liệu!")
        return

    # Lấy 30 kết quả gần nhất
    recent_results = KetQuaXoSo.objects.all().order_by("-ngay")[:30]

    # Phân tích đơn giản
    kep_count = {"Dương": 0, "Âm": 0, "Sát kép": 0, "Khác": 0}
    total_predictions = 0
    correct_predictions = 0

    print(f"📈 Phân tích {len(recent_results)} kết quả gần nhất:")
    print("-" * 40)

    for i, result in enumerate(recent_results):
        if len(result.giai_db) >= 2:
            so_2digit = result.giai_db[-2:]
            kep_type = kiem_tra_kep(so_2digit)

            if kep_type:
                kep_count[kep_type] += 1
                print(f"{result.ngay}: {result.giai_db} -> {so_2digit} ({kep_type})")
            else:
                kep_count["Khác"] += 1
                print(f"{result.ngay}: {result.giai_db} -> {so_2digit} (Khác)")

    print("\n📊 THỐNG KÊ:")
    print("-" * 20)
    for kep_type, count in kep_count.items():
        percentage = (count / len(recent_results)) * 100 if recent_results else 0
        print(f"{kep_type}: {count} lần ({percentage:.1f}%)")

    # Tính hiệu suất giả định
    total_kep = sum(kep_count[key] for key in ["Dương", "Âm", "Sát kép"])
    kep_percentage = (total_kep / len(recent_results)) * 100 if recent_results else 0

    print(f"\n🎯 KẾT LUẬN:")
    print(f"- Tỷ lệ kép lệch: {kep_percentage:.1f}%")

    if kep_percentage > 50:
        print("✅ Kép lệch xuất hiện thường xuyên - có tiềm năng")
    elif kep_percentage > 30:
        print("⚠️ Kép lệch xuất hiện vừa phải - cần thận trọng")
    else:
        print("❌ Kép lệch xuất hiện ít - rủi ro cao")

    # Đề xuất đơn giản
    print(f"\n💡 ĐỀ XUẤT:")
    if kep_count["Dương"] < 3:
        print("- Có thể thử kép Dương")
    if kep_count["Âm"] < 2:
        print("- Có thể thử kép Âm")
    if kep_count["Sát kép"] < 2:
        print("- Có thể thử Sát kép")

    print("\n✅ Test hoàn thành!")


if __name__ == "__main__":
    simple_kep_lech_test()
