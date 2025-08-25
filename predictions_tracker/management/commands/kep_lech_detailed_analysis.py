"""
🎯 Kép Lệch Performance Report - Sử dụng Management Command
========================================================

Báo cáo chi tiết hiệu suất Kép Lệch với thông số đầu tư thực tế:
- Vốn ban đầu: 1,000,000 VND
- Đánh mỗi con: 10,000 VND
- Tỷ lệ thắng: x90 (900,000 VND/con trúng)
- Phân tích 3 tháng gần nhất

Dựa trên logic từ keplech.py và kết quả thực tế từ KetQuaXoSo model.
"""

import json
from collections import defaultdict
from datetime import date, timedelta

from django.core.management.base import BaseCommand
from django.utils import timezone

from results.models import KetQuaXoSo


class Command(BaseCommand):
    help = (
        "Kép Lệch detailed weekly performance analysis with real investment parameters"
    )

    # Bộ số Kép Lệch (từ keplech.py)
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

    # Thông số đầu tư thực tế
    INITIAL_CAPITAL = 1000000  # 1 triệu VND
    BET_PER_NUMBER = 10000  # 10k VND/con
    WIN_MULTIPLIER = 90  # x90
    WIN_AMOUNT = BET_PER_NUMBER * WIN_MULTIPLIER  # 900k VND/con trúng

    def add_arguments(self, parser):
        parser.add_argument(
            "--days",
            type=int,
            default=90,
            help="Number of days to analyze (default: 90 for 3 months)",
        )
        parser.add_argument(
            "--format",
            choices=["simple", "detailed", "json"],
            default="detailed",
            help="Output format",
        )
        parser.add_argument(
            "--export", action="store_true", help="Export results to JSON file"
        )

    def handle(self, *args, **options):
        self.stdout.write("🎯 KÉP LỆCH - PHÂN TÍCH HIỆU SUẤT CHI TIẾT")
        self.stdout.write("=" * 60)

        days = options["days"]
        format_type = options["format"]

        # Lấy dữ liệu
        end_date = date.today()
        start_date = end_date - timedelta(days=days)

        results = KetQuaXoSo.objects.filter(
            ngay__range=[start_date, end_date]
        ).order_by("ngay")

        if not results.exists():
            self.stdout.write(
                self.style.ERROR(f"❌ Không có dữ liệu trong {days} ngày gần nhất!")
            )
            return

        self.stdout.write(f"📊 Thời gian: {start_date} đến {end_date} ({days} ngày)")
        self.stdout.write(f"📊 Tổng kết quả: {results.count()}")
        self.stdout.write("")

        # Phân tích theo tuần
        weekly_analysis = self.analyze_weekly_performance(results)

        # Hiển thị kết quả theo format
        if format_type == "simple":
            self.print_simple_summary(weekly_analysis)
        elif format_type == "detailed":
            self.print_detailed_analysis(weekly_analysis)
        elif format_type == "json":
            self.print_json_analysis(weekly_analysis)

        # Export nếu được yêu cầu
        if options["export"]:
            self.export_to_json(weekly_analysis, days)

        self.stdout.write(self.style.SUCCESS("\n✅ PHÂN TÍCH HOÀN THÀNH!"))

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
        for kep_type, kep_list in [
            ("Dương", self.KEP_DUONG),
            ("Âm", self.KEP_AM),
            ("Sát kép", self.SAT_KEP),
        ]:
            if kep_count[kep_type] < 2:
                missing_numbers = [
                    num for num in kep_list if num not in appeared_numbers
                ]
                recommendations.extend(missing_numbers[:5])  # Top 5 chưa xuất hiện

        # Logic 2: Nếu không có kép nào -> tập trung kép Âm
        total_kep = sum(kep_count.values())
        if total_kep == 0:
            recommendations.extend(self.KEP_AM[:7])

        # Logic 3: Dựa vào thứ 2 (nếu có)
        thu2_data = next(
            (d for d in week_data if d["weekday"] == 1), None
        )  # Monday = 1
        if thu2_data and len(thu2_data["giai_db"]) > 0:
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

    def analyze_weekly_performance(self, results):
        """Phân tích hiệu suất theo tuần"""
        # Nhóm dữ liệu theo tuần
        weekly_data = defaultdict(list)
        weekday_names = [
            "Chủ nhật",
            "Thứ 2",
            "Thứ 3",
            "Thứ 4",
            "Thứ 5",
            "Thứ 6",
            "Thứ 7",
        ]

        for result in results:
            year, week, _ = result.ngay.isocalendar()
            week_key = f"{year}-W{week:02d}"

            weekly_data[week_key].append(
                {
                    "date": result.ngay,
                    "weekday": result.ngay.weekday(),
                    "weekday_name": weekday_names[result.ngay.weekday()],
                    "giai_db": result.giai_db,
                    "giai_db_2digit": (
                        result.giai_db[-2:] if len(result.giai_db) >= 2 else None
                    ),
                    "all_2digit": list(result.get_all_2digit_numbers()),
                }
            )

        # Sắp xếp dữ liệu trong tuần
        for week_key in weekly_data:
            weekly_data[week_key].sort(key=lambda x: x["date"])

        # Phân tích từng tuần
        weekly_analysis = []
        total_capital = self.INITIAL_CAPITAL
        total_investment = 0
        total_winnings = 0
        winning_weeks = 0
        losing_weeks = 0

        weeks = sorted(weekly_data.keys())

        for i, week_key in enumerate(
            weeks[:-1]
        ):  # Bỏ tuần cuối vì không có tuần sau để so sánh
            current_week = weekly_data[week_key]
            next_week = weekly_data[weeks[i + 1]]

            # Tạo đề cử dựa trên tuần hiện tại
            recommendations = self.generate_weekly_recommendations(current_week)
            recommended_numbers = recommendations["recommended_numbers"]

            # Kiểm tra kết quả tuần tiếp theo - TÍNH TOÁN ĐÚNG THEO THỰC TẾ
            # Logic: Đánh từ thứ 2, dừng ngay khi thắng lần đầu để tối ưu lợi nhuận
            # Nếu không thắng thì đánh hết tuần (7 ngày)
            winning_numbers = []
            winning_days = []
            first_winning_day = None
            days_played = 0

            # Đánh từ thứ 2 đến khi thắng hoặc hết tuần
            for day_result in next_week:
                days_played += 1
                if (
                    day_result["giai_db_2digit"]
                    and day_result["giai_db_2digit"] in recommended_numbers
                ):
                    winning_numbers.append(day_result["giai_db_2digit"])
                    winning_days.append(day_result["weekday_name"])
                    if first_winning_day is None:
                        first_winning_day = days_played
                        # STOP sau khi thắng lần đầu (chiến lược tối ưu)
                        break

            # Nếu không thắng, đánh cả tuần (7 ngày)
            if not winning_numbers:
                days_played = 7

            # Tính toán đầu tư thực tế: (số con đề cử) × (10k/con) × (số ngày đánh)
            week_investment = (
                len(recommended_numbers) * self.BET_PER_NUMBER * days_played
            )
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

            # Lưu thông tin tuần
            weekly_analysis.append(
                {
                    "week": week_key,
                    "recommended_numbers": recommended_numbers,
                    "recommended_count": len(recommended_numbers),
                    "winning_numbers": winning_numbers,
                    "winning_count": len(winning_numbers),
                    "winning_days": winning_days,
                    "days_played": days_played,  # Thêm số ngày đã đánh
                    "first_winning_day": first_winning_day,  # Ngày thắng đầu tiên
                    "investment": week_investment,
                    "winnings": week_winnings,
                    "profit": week_profit,
                    "capital_after": total_capital,
                    "reasoning": recommendations["reasoning"],
                }
            )

        return {
            "weekly_details": weekly_analysis,
            "summary": {
                "total_weeks": len(weekly_analysis),
                "initial_capital": self.INITIAL_CAPITAL,
                "final_capital": total_capital,
                "net_profit": total_capital - self.INITIAL_CAPITAL,
                "roi_percent": (
                    (total_capital - self.INITIAL_CAPITAL) / self.INITIAL_CAPITAL
                )
                * 100,
                "total_investment": total_investment,
                "total_winnings": total_winnings,
                "winning_weeks": winning_weeks,
                "losing_weeks": losing_weeks,
                "win_rate": (
                    (winning_weeks / len(weekly_analysis)) * 100
                    if weekly_analysis
                    else 0
                ),
            },
        }

    def print_simple_summary(self, analysis):
        """In tóm tắt đơn giản"""
        summary = analysis["summary"]

        self.stdout.write("💰 TÓM TẮT NHANH:")
        self.stdout.write(f"📊 Số tuần: {summary['total_weeks']}")
        self.stdout.write(
            f"💵 Vốn: {summary['initial_capital']:,} → {summary['final_capital']:,} VND"
        )
        self.stdout.write(
            f"📈 Lãi/lỗ: {summary['net_profit']:+,} VND ({summary['roi_percent']:+.1f}%)"
        )
        self.stdout.write(
            f"📊 Tỷ lệ thắng: {summary['win_rate']:.1f}% ({summary['winning_weeks']}/{summary['total_weeks']})"
        )

    def print_detailed_analysis(self, analysis):
        """In phân tích chi tiết"""
        weekly_details = analysis["weekly_details"]
        summary = analysis["summary"]

        # Bảng chi tiết từng tuần
        self.stdout.write("📅 CHI TIẾT TỪUNG TUẦN:")
        self.stdout.write("-" * 120)
        self.stdout.write(
            f"{'Tuần':<12} {'Đề cử':<8} {'Trúng':<8} {'Ngày trúng':<15} {'Ngày đánh':<10} {'Đầu tư':<12} {'Thắng':<12} {'Lãi/Lỗ':<12}"
        )
        self.stdout.write("-" * 120)

        for week in weekly_details:
            winning_days_str = (
                ", ".join(week["winning_days"][:2]) if week["winning_days"] else "Không"
            )
            if len(week["winning_days"]) > 2:
                winning_days_str += "..."

            profit_str = f"{week['profit']:+,}đ"
            days_played_str = f"{week['days_played']}/7"

            self.stdout.write(
                f"{week['week']:<12} "
                f"{week['recommended_count']:<8} "
                f"{week['winning_count']:<8} "
                f"{winning_days_str:<15} "
                f"{days_played_str:<10} "
                f"{week['investment']:,}đ{'':<2} "
                f"{week['winnings']:,}đ{'':<2} "
                f"{profit_str}"
            )

        self.stdout.write("-" * 120)

        # Tóm tắt
        self.stdout.write("")
        self.stdout.write("💰 TÓM TẮT TỔNG THỂ:")
        self.stdout.write("=" * 50)
        self.stdout.write(f"📊 Tổng số tuần: {summary['total_weeks']}")
        self.stdout.write(f"💵 Vốn ban đầu: {summary['initial_capital']:,} VND")
        self.stdout.write(f"💵 Vốn cuối kỳ: {summary['final_capital']:,} VND")
        self.stdout.write(f"📈 Lợi nhuận ròng: {summary['net_profit']:+,} VND")
        self.stdout.write(f"📈 ROI: {summary['roi_percent']:+.1f}%")
        self.stdout.write("")
        self.stdout.write(f"💸 Tổng đầu tư: {summary['total_investment']:,} VND")
        self.stdout.write(f"💰 Tổng thắng: {summary['total_winnings']:,} VND")
        self.stdout.write(
            f"📊 Tỷ lệ thắng: {summary['win_rate']:.1f}% ({summary['winning_weeks']}/{summary['total_weeks']} tuần)"
        )
        self.stdout.write("")
        self.stdout.write(f"✅ Tuần thắng: {summary['winning_weeks']}")
        self.stdout.write(f"❌ Tuần thua: {summary['losing_weeks']}")
        self.stdout.write(
            f"⚖️ Tuần hòa: {summary['total_weeks'] - summary['winning_weeks'] - summary['losing_weeks']}"
        )

        # Phân tích ngày trúng
        self.analyze_winning_days(weekly_details)

        # Top tuần thắng/thua
        self.analyze_top_weeks(weekly_details)

    def analyze_winning_days(self, weekly_details):
        """Phân tích ngày trúng"""
        winning_days_count = defaultdict(int)
        total_wins = 0

        for week in weekly_details:
            for day in week["winning_days"]:
                winning_days_count[day] += 1
                total_wins += 1

        if winning_days_count:
            self.stdout.write("")
            self.stdout.write("📅 THỐNG KÊ NGÀY TRÚNG:")
            for day, count in sorted(
                winning_days_count.items(), key=lambda x: x[1], reverse=True
            ):
                percentage = (count / total_wins) * 100
                self.stdout.write(f"   {day}: {count} lần ({percentage:.1f}%)")

    def analyze_top_weeks(self, weekly_details):
        """Phân tích top tuần thắng/thua"""
        # Top 3 tuần thắng lớn nhất
        top_winning = sorted(weekly_details, key=lambda x: x["profit"], reverse=True)[
            :3
        ]
        winning_weeks = [w for w in top_winning if w["profit"] > 0]

        if winning_weeks:
            self.stdout.write("")
            self.stdout.write("🏆 TOP TUẦN THẮNG LỚN:")
            for i, week in enumerate(winning_weeks, 1):
                self.stdout.write(
                    f"   {i}. {week['week']}: +{week['profit']:,} VND ({week['winning_count']} số trúng)"
                )

        # Top 3 tuần thua lớn nhất
        top_losing = sorted(weekly_details, key=lambda x: x["profit"])[:3]
        losing_weeks = [w for w in top_losing if w["profit"] < 0]

        if losing_weeks:
            self.stdout.write("")
            self.stdout.write("💸 TOP TUẦN THUA LỚN:")
            for i, week in enumerate(losing_weeks, 1):
                self.stdout.write(
                    f"   {i}. {week['week']}: {week['profit']:,} VND (0 số trúng)"
                )

    def print_json_analysis(self, analysis):
        """In kết quả dạng JSON"""
        self.stdout.write(
            json.dumps(analysis, indent=2, ensure_ascii=False, default=str)
        )

    def export_to_json(self, analysis, days):
        """Export kết quả ra file JSON"""
        filename = (
            f"kep_lech_analysis_{days}days_{date.today().strftime('%Y%m%d')}.json"
        )

        export_data = {
            "analysis_date": date.today().isoformat(),
            "analysis_period_days": days,
            "parameters": {
                "initial_capital": self.INITIAL_CAPITAL,
                "bet_per_number": self.BET_PER_NUMBER,
                "win_multiplier": self.WIN_MULTIPLIER,
                "win_amount": self.WIN_AMOUNT,
            },
            "results": analysis,
        }

        with open(filename, "w", encoding="utf-8") as f:
            json.dump(export_data, f, ensure_ascii=False, indent=2, default=str)

        self.stdout.write(f"\n💾 Đã export kết quả ra file: {filename}")
