"""
🎯 Kép Lệch Weekly Detailed Analysis
==================================
Phân tích chi tiết từng tuần với thông số đầu tư thực tế:
- Vốn ban đầu: 1,000,000 VND
- Đánh mỗi con: 10,000 VND
- Tỷ lệ thắng: x90 (900,000 VND/con trúng)
- Phân tích 3 tháng gần nhất
"""

import json
import os
import sys
from collections import defaultdict
from datetime import date, datetime, timedelta

import django

# Setup Django
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "xoso_crawler.settings")
django.setup()

from results.models import KetQuaXoSo


class KepLechWeeklyDetailedAnalysis:
    """
    🎯 Phân tích chi tiết Kép Lệch theo tuần với thông số thực tế
    """

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

    # Thông số đầu tư
    INITIAL_CAPITAL = 1000000  # 1 triệu VND
    BET_PER_NUMBER = 10000  # 10k VND/con
    WIN_MULTIPLIER = 90  # x90
    WIN_AMOUNT = BET_PER_NUMBER * WIN_MULTIPLIER  # 900k VND/con trúng

    def __init__(self):
        self.analysis_period_days = 90  # 3 tháng
        self.weekday_mapping = {
            0: "Thứ 2",
            1: "Thứ 3",
            2: "Thứ 4",
            3: "Thứ 5",
            4: "Thứ 6",
            5: "Thứ 7",
            6: "Chủ nhật",
        }

    def kiem_tra_kep(self, so):
        """Kiểm tra số có thuộc bộ kép lệch nào"""
        if so in self.KEP_DUONG:
            return "Dương"
        if so in self.KEP_AM:
            return "Âm"
        if so in self.SAT_KEP:
            return "Sát kép"
        return None

    def generate_weekly_recommendations(self, week_data):
        """Tạo số đề cử cho tuần dựa trên logic keplech.py"""
        recommendations = []

        # Đếm kép đã xuất hiện trong tuần
        kep_count = {"Dương": 0, "Âm": 0, "Sát kép": 0}
        appeared_numbers = set()

        for day_result in week_data:
            if len(day_result["giai_db"]) >= 2:
                so_2digit = day_result["giai_db"][-2:]
                kep_type = self.kiem_tra_kep(so_2digit)
                if kep_type:
                    kep_count[kep_type] += 1
                    appeared_numbers.add(so_2digit)

        # Logic 1: Kép xuất hiện ít -> đề cử
        for kep_type in ["Dương", "Âm", "Sát kép"]:
            if kep_count[kep_type] < 2:
                kep_pool = getattr(self, f'KEP_{kep_type.upper().replace(" ", "_")}')
                missing_numbers = [
                    num for num in kep_pool if num not in appeared_numbers
                ]
                recommendations.extend(missing_numbers[:5])  # Top 5 chưa xuất hiện

        # Logic 2: Nếu không có kép nào -> tập trung kép Âm
        total_kep = sum(kep_count.values())
        if total_kep == 0:
            recommendations.extend(self.KEP_AM[:7])

        # Logic 3: Dựa vào thứ 2 (nếu có)
        thu2_data = next((d for d in week_data if d["weekday"] == "Thứ 2"), None)
        if thu2_data and thu2_data["giai_db"]:
            first_digit = thu2_data["giai_db"][0]
            duoi_numbers = [
                f"{i:02d}" for i in range(100) if str(i).zfill(2)[1] == first_digit
            ]
            recommendations.extend(duoi_numbers[:8])

        # Loại bỏ trùng lặp và giới hạn
        unique_recommendations = list(dict.fromkeys(recommendations))[:15]

        return {
            "recommended_numbers": unique_recommendations,
            "kep_analysis": kep_count,
            "reasoning": self._generate_reasoning(kep_count, total_kep, thu2_data),
        }

    def _generate_reasoning(self, kep_count, total_kep, thu2_data):
        """Tạo lý do đề cử"""
        reasons = []

        for kep_type, count in kep_count.items():
            if count == 0:
                reasons.append(f"Kép {kep_type} chưa xuất hiện")
            elif count < 2:
                reasons.append(f"Kép {kep_type} chỉ xuất hiện {count} lần")

        if total_kep == 0:
            reasons.append("Tuần không có kép lệch -> ưu tiên kép Âm")

        if thu2_data:
            reasons.append(f"Dựa theo số đầu thứ 2: {thu2_data['giai_db'][0]}")

        return reasons

    def analyze_3_months_performance(self):
        """Phân tích hiệu suất 3 tháng gần nhất"""
        print("🎯 KÉP LỆCH - PHÂN TÍCH CHI TIẾT 3 THÁNG")
        print("=" * 60)

        # Lấy dữ liệu 3 tháng gần nhất
        end_date = date.today()
        start_date = end_date - timedelta(days=self.analysis_period_days)

        results = KetQuaXoSo.objects.filter(
            ngay__range=[start_date, end_date]
        ).order_by("ngay")

        if not results.exists():
            print("❌ Không có dữ liệu trong 3 tháng gần nhất!")
            return

        print(f"📊 Thời gian phân tích: {start_date} đến {end_date}")
        print(f"📊 Tổng số kết quả: {results.count()}")
        print()

        # Nhóm dữ liệu theo tuần
        weekly_data = self._group_by_week(results)

        # Phân tích từng tuần
        weekly_analysis = []
        total_capital = self.INITIAL_CAPITAL
        total_investment = 0
        total_winnings = 0
        winning_weeks = 0
        losing_weeks = 0

        print("📅 PHÂN TÍCH TỪNG TUẦN:")
        print("-" * 80)
        print(
            f"{'Tuần':<12} {'Số đề cử':<15} {'Số trúng':<15} {'Thứ trúng':<12} {'Đầu tư':<12} {'Thắng':<12} {'Lãi/Lỗ':<12}"
        )
        print("-" * 80)

        for week_key, week_results in weekly_data.items():
            # Tạo đề cử cho tuần tiếp theo (simulation)
            recommendations = self.generate_weekly_recommendations(week_results)
            recommended_numbers = recommendations["recommended_numbers"]

            # Kiểm tra số trúng trong tuần tiếp theo
            next_week_results = self._get_next_week_results(week_key, weekly_data)
            if not next_week_results:
                continue

            # Tính toán kết quả đầu tư
            week_investment = len(recommended_numbers) * self.BET_PER_NUMBER
            winning_numbers = []
            winning_days = []

            for day_result in next_week_results:
                if len(day_result["giai_db"]) >= 2:
                    so_2digit = day_result["giai_db"][-2:]
                    if so_2digit in recommended_numbers:
                        winning_numbers.append(so_2digit)
                        winning_days.append(day_result["weekday"])

            # Tính lãi/lỗ
            week_winnings = len(winning_numbers) * self.WIN_AMOUNT
            week_profit = week_winnings - week_investment

            # Cập nhật vốn
            total_capital += week_profit
            total_investment += week_investment
            total_winnings += week_winnings

            if week_profit > 0:
                winning_weeks += 1
            elif week_profit < 0:
                losing_weeks += 1

            # Hiển thị kết quả tuần
            recommended_str = f"{len(recommended_numbers)} số"
            winning_str = f"{len(winning_numbers)} số" if winning_numbers else "0 số"
            winning_days_str = ", ".join(winning_days[:3]) if winning_days else "Không"
            profit_str = f"{week_profit:+,}" if week_profit != 0 else "0"

            print(
                f"{week_key:<12} {recommended_str:<15} {winning_str:<15} {winning_days_str:<12} {week_investment:,}đ{'':<2} {week_winnings:,}đ{'':<2} {profit_str}đ"
            )

            # Lưu chi tiết tuần
            weekly_analysis.append(
                {
                    "week": week_key,
                    "recommended_numbers": recommended_numbers,
                    "recommended_count": len(recommended_numbers),
                    "winning_numbers": winning_numbers,
                    "winning_count": len(winning_numbers),
                    "winning_days": winning_days,
                    "investment": week_investment,
                    "winnings": week_winnings,
                    "profit": week_profit,
                    "capital_after": total_capital,
                    "reasoning": recommendations["reasoning"],
                }
            )

        print("-" * 80)

        # Tóm tắt tổng thể
        self._print_summary(
            weekly_analysis,
            total_capital,
            total_investment,
            total_winnings,
            winning_weeks,
            losing_weeks,
        )

        # Phân tích chi tiết
        self._print_detailed_analysis(weekly_analysis)

        return weekly_analysis

    def _group_by_week(self, results):
        """Nhóm kết quả theo tuần"""
        weekly_data = defaultdict(list)

        for result in results:
            # Tính tuần của năm
            year, week, _ = result.ngay.isocalendar()
            week_key = f"{year}-W{week:02d}"

            weekly_data[week_key].append(
                {
                    "date": result.ngay,
                    "weekday": self.weekday_mapping[result.ngay.weekday()],
                    "giai_db": result.giai_db,
                    "giai_db_2digit": (
                        result.giai_db[-2:] if len(result.giai_db) >= 2 else None
                    ),
                    "all_2digit": list(result.get_all_2digit_numbers()),
                }
            )

        # Sắp xếp theo ngày trong tuần
        for week_key in weekly_data:
            weekly_data[week_key].sort(key=lambda x: x["date"])

        return dict(weekly_data)

    def _get_next_week_results(self, current_week, weekly_data):
        """Lấy kết quả tuần tiếp theo"""
        weeks = sorted(weekly_data.keys())
        try:
            current_index = weeks.index(current_week)
            if current_index < len(weeks) - 1:
                next_week = weeks[current_index + 1]
                return weekly_data[next_week]
        except (ValueError, IndexError):
            pass
        return None

    def _print_summary(
        self,
        weekly_analysis,
        total_capital,
        total_investment,
        total_winnings,
        winning_weeks,
        losing_weeks,
    ):
        """In tóm tắt tổng thể"""
        print()
        print("💰 TÓM TẮT TỔNG THỂ 3 THÁNG:")
        print("=" * 50)

        total_weeks = len(weekly_analysis)
        net_profit = total_capital - self.INITIAL_CAPITAL
        roi_percent = (net_profit / self.INITIAL_CAPITAL) * 100
        win_rate = (winning_weeks / total_weeks) * 100 if total_weeks > 0 else 0

        print(f"📊 Tổng số tuần phân tích: {total_weeks}")
        print(f"💵 Vốn ban đầu: {self.INITIAL_CAPITAL:,} VND")
        print(f"💵 Vốn cuối kỳ: {total_capital:,} VND")
        print(f"📈 Lợi nhuận ròng: {net_profit:+,} VND")
        print(f"📈 ROI: {roi_percent:+.1f}%")
        print()
        print(f"💸 Tổng đầu tư: {total_investment:,} VND")
        print(f"💰 Tổng thắng: {total_winnings:,} VND")
        print(f"📊 Tỷ lệ thắng: {win_rate:.1f}% ({winning_weeks}/{total_weeks} tuần)")
        print()
        print(f"✅ Tuần thắng: {winning_weeks}")
        print(f"❌ Tuần thua: {losing_weeks}")
        print(f"⚖️ Tuần hòa: {total_weeks - winning_weeks - losing_weeks}")

    def _print_detailed_analysis(self, weekly_analysis):
        """In phân tích chi tiết"""
        print()
        print("🔍 PHÂN TÍCH CHI TIẾT:")
        print("=" * 50)

        # Phân tích ngày trúng thường xuyên nhất
        winning_days_count = defaultdict(int)
        total_wins = 0

        for week in weekly_analysis:
            for day in week["winning_days"]:
                winning_days_count[day] += 1
                total_wins += 1

        if winning_days_count:
            print("📅 Thống kê ngày trúng:")
            for day, count in sorted(
                winning_days_count.items(), key=lambda x: x[1], reverse=True
            ):
                percentage = (count / total_wins) * 100
                print(f"   {day}: {count} lần ({percentage:.1f}%)")

        # Phân tích số đề cử trung bình
        avg_recommended = sum(w["recommended_count"] for w in weekly_analysis) / len(
            weekly_analysis
        )
        avg_winning = sum(w["winning_count"] for w in weekly_analysis) / len(
            weekly_analysis
        )

        print(f"\n📊 Số đề cử trung bình mỗi tuần: {avg_recommended:.1f}")
        print(f"📊 Số trúng trung bình mỗi tuần: {avg_winning:.1f}")
        print(f"📊 Tỷ lệ trúng trung bình: {(avg_winning/avg_recommended)*100:.1f}%")

        # Top 5 tuần thắng lớn nhất
        top_winning_weeks = sorted(
            weekly_analysis, key=lambda x: x["profit"], reverse=True
        )[:5]
        print(f"\n🏆 TOP 5 TUẦN THẮNG LỚN:")
        for i, week in enumerate(top_winning_weeks, 1):
            if week["profit"] > 0:
                print(
                    f"   {i}. {week['week']}: +{week['profit']:,} VND ({week['winning_count']} số trúng)"
                )

        # Top 5 tuần thua lớn nhất
        top_losing_weeks = sorted(weekly_analysis, key=lambda x: x["profit"])[:5]
        print(f"\n💸 TOP 5 TUẦN THUA LỚN:")
        for i, week in enumerate(top_losing_weeks, 1):
            if week["profit"] < 0:
                print(f"   {i}. {week['week']}: {week['profit']:,} VND (0 số trúng)")

        # Xu hướng vốn theo thời gian
        print(f"\n📈 XU HƯỚNG VỐN:")
        capital_changes = []
        for week in weekly_analysis[-10:]:  # 10 tuần gần nhất
            capital_changes.append(week["capital_after"])

        if len(capital_changes) >= 2:
            if capital_changes[-1] > capital_changes[0]:
                trend = "📈 Tăng"
            elif capital_changes[-1] < capital_changes[0]:
                trend = "📉 Giảm"
            else:
                trend = "➡️ Ổn định"
            print(f"   10 tuần gần nhất: {trend}")

    def export_to_json(
        self, weekly_analysis, filename="kep_lech_3months_analysis.json"
    ):
        """Export kết quả ra file JSON"""
        export_data = {
            "analysis_period": {
                "start_date": (
                    date.today() - timedelta(days=self.analysis_period_days)
                ).isoformat(),
                "end_date": date.today().isoformat(),
                "days": self.analysis_period_days,
            },
            "investment_parameters": {
                "initial_capital": self.INITIAL_CAPITAL,
                "bet_per_number": self.BET_PER_NUMBER,
                "win_multiplier": self.WIN_MULTIPLIER,
                "win_amount": self.WIN_AMOUNT,
            },
            "weekly_analysis": weekly_analysis,
            "summary": {
                "total_weeks": len(weekly_analysis),
                "winning_weeks": sum(1 for w in weekly_analysis if w["profit"] > 0),
                "losing_weeks": sum(1 for w in weekly_analysis if w["profit"] < 0),
                "total_profit": sum(w["profit"] for w in weekly_analysis),
                "total_investment": sum(w["investment"] for w in weekly_analysis),
                "total_winnings": sum(w["winnings"] for w in weekly_analysis),
            },
        }

        with open(filename, "w", encoding="utf-8") as f:
            json.dump(export_data, f, ensure_ascii=False, indent=2, default=str)

        print(f"\n💾 Đã export kết quả ra file: {filename}")


def main():
    """Chạy phân tích chính"""
    analyzer = KepLechWeeklyDetailedAnalysis()
    weekly_analysis = analyzer.analyze_3_months_performance()

    # Export kết quả
    if weekly_analysis:
        analyzer.export_to_json(weekly_analysis)

    print(f"\n✅ PHÂN TÍCH HOÀN THÀNH!")
    print("=" * 60)


if __name__ == "__main__":
    main()
