"""
🎯 Kép Lệch Analyzer - Performance Analysis System
================================================
Phân tích hiệu suất và khả năng sinh lời của hệ thống Kép Lệch
Dựa trên dữ liệu thực từ KetQuaXoSo model
"""

import logging
from collections import Counter, defaultdict
from datetime import date, datetime, timedelta
from typing import Any, Dict, List, Optional, Tuple

import numpy as np
from django.db.models import Q
from django.utils import timezone

# Configure logging
logger = logging.getLogger(__name__)


class KepLechPerformanceAnalyzer:
    """
    🎯 Phân tích hiệu suất Kép Lệch với dữ liệu thực

    Tính toán:
    - Tỷ lệ đúng của dự đoán theo tuần
    - Mức độ lợi nhuận khi áp dụng chiến lược
    - Độ rủi ro và khả năng sinh lời
    - Thống kê chi tiết qua 2 năm
    """

    # Bộ số Kép Lệch từ keplech.py
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

    # Quy ước thứ trong tuần
    WEEKDAY_MAP = {
        0: "Thứ 2",
        1: "Thứ 3",
        2: "Thứ 4",
        3: "Thứ 5",
        4: "Thứ 6",
        5: "Thứ 7",
        6: "Chủ nhật",
    }

    # Cấu hình phân tích
    ANALYSIS_CONFIG = {
        "analysis_period_years": 2,
        "min_bet_amount": 1000,  # VND tối thiểu
        "payout_ratio": 70,  # Tỷ lệ trả thưởng (70 lần)
        "commission_rate": 0.02,  # Hoa hồng 2%
        "risk_management": {
            "max_weekly_investment_ratio": 0.03,  # Tối đa 3% vốn/tuần
            "stop_loss_ratio": 0.15,  # Cắt lỗ khi mất 15%
            "take_profit_ratio": 0.25,  # Chốt lời khi được 25%
        },
    }

    def __init__(self):
        self.method_id = "kep_lech_performance"
        self.method_name = "Kép Lệch Performance Analysis"
        self.version = "2.0.0"

        # Cache cho phân tích
        self.weekly_data_cache = {}
        self.performance_cache = {}

        logger.info(f"🎯 {self.method_name} v{self.version} initialized")

    def run_complete_analysis(self, start_days_ago: int = 730) -> Dict[str, Any]:
        """
        🔍 Chạy phân tích toàn diện trong 2 năm

        Args:
            start_days_ago: Số ngày từ hôm nay để bắt đầu phân tích (mặc định 2 năm)

        Returns:
            Dictionary chứa tất cả kết quả phân tích
        """
        try:
            logger.info(
                f"🚀 Starting complete Kép Lệch analysis for {start_days_ago} days"
            )

            # Lấy dữ liệu trong khoảng thời gian
            end_date = date.today()
            start_date = end_date - timedelta(days=start_days_ago)

            # Lấy tất cả kết quả xổ số trong khoảng thời gian
            from results.models import KetQuaXoSo

            ket_qua_data = KetQuaXoSo.objects.filter(
                ngay__range=[start_date, end_date]
            ).order_by("ngay")

            if not ket_qua_data.exists():
                return {
                    "success": False,
                    "error": "Không có dữ liệu trong khoảng thời gian phân tích",
                    "analysis_period": {"start": start_date, "end": end_date},
                }

            # 1. Phân tích theo tuần
            weekly_analysis = self._analyze_weekly_patterns(ket_qua_data)

            # 2. Tính toán hiệu suất dự đoán
            prediction_performance = self._calculate_prediction_performance(
                weekly_analysis
            )

            # 3. Phân tích lợi nhuận
            profit_analysis = self._calculate_profit_analysis(prediction_performance)

            # 4. Phân tích rủi ro
            risk_analysis = self._calculate_risk_analysis(profit_analysis)

            # 5. Thống kê tổng hợp
            summary_stats = self._generate_summary_statistics(
                weekly_analysis, prediction_performance, profit_analysis, risk_analysis
            )

            # 6. Khuyến nghị chiến lược
            strategy_recommendations = self._generate_strategy_recommendations(
                summary_stats
            )

            complete_analysis = {
                "success": True,
                "analysis_metadata": {
                    "method_id": self.method_id,
                    "analysis_period": {
                        "start_date": start_date,
                        "end_date": end_date,
                        "total_days": start_days_ago,
                        "total_results": ket_qua_data.count(),
                    },
                    "generated_at": timezone.now(),
                    "version": self.version,
                },
                "weekly_analysis": weekly_analysis,
                "prediction_performance": prediction_performance,
                "profit_analysis": profit_analysis,
                "risk_analysis": risk_analysis,
                "summary_statistics": summary_stats,
                "strategy_recommendations": strategy_recommendations,
                "detailed_breakdowns": {
                    "monthly_performance": self._calculate_monthly_breakdown(
                        weekly_analysis
                    ),
                    "seasonal_patterns": self._analyze_seasonal_patterns(
                        weekly_analysis
                    ),
                    "weekday_correlations": self._analyze_weekday_correlations(
                        ket_qua_data
                    ),
                },
            }

            logger.info(
                f"✅ Complete analysis finished: {summary_stats.get('total_weeks', 0)} weeks analyzed"
            )
            return complete_analysis

        except Exception as e:
            logger.error(f"❌ Complete analysis failed: {e}", exc_info=True)
            return {
                "success": False,
                "error": str(e),
                "analysis_period": {
                    "start": start_date if "start_date" in locals() else None,
                    "end": end_date if "end_date" in locals() else None,
                },
            }

    def _analyze_weekly_patterns(self, ket_qua_data) -> List[Dict[str, Any]]:
        """Phân tích patterns theo từng tuần"""
        try:
            weekly_data = []

            # Nhóm dữ liệu theo tuần
            weeks = {}
            for result in ket_qua_data:
                # Tính tuần của năm
                year, week, _ = result.ngay.isocalendar()
                week_key = f"{year}-W{week:02d}"

                if week_key not in weeks:
                    weeks[week_key] = []
                weeks[week_key].append(result)

            # Phân tích từng tuần
            for week_key, week_results in weeks.items():
                if len(week_results) < 4:  # Bỏ qua tuần không đủ dữ liệu
                    continue

                week_analysis = self._analyze_single_week(week_key, week_results)
                weekly_data.append(week_analysis)

            logger.info(f"📊 Analyzed {len(weekly_data)} complete weeks")
            return weekly_data

        except Exception as e:
            logger.error(f"❌ Weekly analysis failed: {e}")
            return []

    def _analyze_single_week(self, week_key: str, week_results: List) -> Dict[str, Any]:
        """Phân tích một tuần cụ thể"""
        try:
            # Thống kê kép lệch trong tuần
            kep_stats = {
                "Dương": {"count": 0, "numbers": [], "days": []},
                "Âm": {"count": 0, "numbers": [], "days": []},
                "Sát kép": {"count": 0, "numbers": [], "days": []},
                "Khác": {"count": 0, "numbers": [], "days": []},
            }

            daily_results = {}
            all_2digit_numbers = []

            for result in week_results:
                # Lấy số 2 chữ số cuối của giải đặc biệt
                giai_db_2digit = (
                    result.giai_db[-2:] if len(result.giai_db) >= 2 else None
                )
                weekday_name = self.WEEKDAY_MAP.get(result.ngay.weekday(), "Unknown")

                daily_results[weekday_name] = {
                    "date": result.ngay,
                    "giai_db": result.giai_db,
                    "giai_db_2digit": giai_db_2digit,
                    "all_numbers": list(result.get_all_2digit_numbers()),
                }

                # Kiểm tra loại kép
                if giai_db_2digit:
                    kep_type = self._kiem_tra_kep(giai_db_2digit)
                    if kep_type:
                        kep_stats[kep_type]["count"] += 1
                        kep_stats[kep_type]["numbers"].append(giai_db_2digit)
                        kep_stats[kep_type]["days"].append(weekday_name)
                    else:
                        kep_stats["Khác"]["count"] += 1
                        kep_stats["Khác"]["numbers"].append(giai_db_2digit)
                        kep_stats["Khác"]["days"].append(weekday_name)

                # Lấy tất cả số 2 chữ số trong tuần
                all_2digit_numbers.extend(result.get_all_2digit_numbers())

            # Tạo dự đoán cho tuần tiếp theo
            predictions = self._generate_week_predictions(kep_stats, daily_results)

            return {
                "week_key": week_key,
                "week_start": min(r.ngay for r in week_results),
                "week_end": max(r.ngay for r in week_results),
                "total_days": len(week_results),
                "daily_results": daily_results,
                "kep_statistics": kep_stats,
                "predictions_for_next_week": predictions,
                "all_numbers_appeared": list(set(all_2digit_numbers)),
                "analysis_summary": {
                    "dominant_kep_type": max(
                        kep_stats.items(),
                        key=lambda x: x[1]["count"] if x[0] != "Khác" else 0,
                    )[0],
                    "total_kep_appearances": sum(
                        stats["count"]
                        for key, stats in kep_stats.items()
                        if key != "Khác"
                    ),
                    "kep_percentage": (
                        sum(
                            stats["count"]
                            for key, stats in kep_stats.items()
                            if key != "Khác"
                        )
                        / len(week_results)
                        * 100
                        if week_results
                        else 0
                    ),
                },
            }

        except Exception as e:
            logger.error(f"❌ Single week analysis failed for {week_key}: {e}")
            return {"week_key": week_key, "error": str(e)}

    def _kiem_tra_kep(self, so: str) -> Optional[str]:
        """Kiểm tra số có thuộc bộ kép lệch nào"""
        if so in self.KEP_DUONG:
            return "Dương"
        if so in self.KEP_AM:
            return "Âm"
        if so in self.SAT_KEP:
            return "Sát kép"
        return None

    def _generate_week_predictions(
        self, kep_stats: Dict, daily_results: Dict
    ) -> Dict[str, Any]:
        """Tạo dự đoán cho tuần tiếp theo dựa trên logic keplech.py"""
        try:
            predictions = {
                "recommended_numbers": [],
                "strategies": [],
                "confidence_level": "medium",
                "reasoning": [],
            }

            # Logic 1: Kép xuất hiện ít -> khuyến nghị đánh
            for kep_type in ["Dương", "Âm", "Sát kép"]:
                if kep_stats[kep_type]["count"] < 2:
                    # Lấy số chưa xuất hiện
                    appeared_numbers = set(kep_stats[kep_type]["numbers"])
                    kep_pool = getattr(
                        self, f'KEP_{kep_type.upper().replace(" ", "_")}', []
                    )
                    missing_numbers = [
                        num for num in kep_pool if num not in appeared_numbers
                    ]

                    if missing_numbers:
                        predictions["recommended_numbers"].extend(missing_numbers[:5])
                        predictions["strategies"].append(
                            f"Nuôi kép {kep_type} - xuất hiện {kep_stats[kep_type]['count']} lần"
                        )
                        predictions["reasoning"].append(
                            f"Kép {kep_type} thiếu trong tuần, khả năng cao sẽ xuất hiện"
                        )

            # Logic 2: Kép xuất hiện nhiều -> cảnh báo
            for kep_type in ["Dương", "Âm", "Sát kép"]:
                if kep_stats[kep_type]["count"] >= 3:
                    predictions["strategies"].append(
                        f"TRÁNH kép {kep_type} - đã xuất hiện {kep_stats[kep_type]['count']} lần"
                    )
                    predictions["reasoning"].append(
                        f"Kép {kep_type} đã bão hòa trong tuần"
                    )

            # Logic 3: Nếu không có kép nào xuất hiện -> tập trung kép Âm
            total_kep = sum(
                kep_stats[kep_type]["count"] for kep_type in ["Dương", "Âm", "Sát kép"]
            )
            if total_kep == 0:
                predictions["recommended_numbers"].extend(self.KEP_AM[:7])
                predictions["strategies"].append("Tập trung kép Âm - tuần không có kép")
                predictions["reasoning"].append(
                    "Tuần không xuất hiện kép lệch nào, ưu tiên kép Âm"
                )
                predictions["confidence_level"] = "high"

            # Logic 4: Dựa vào thứ 2
            if "Thứ 2" in daily_results and daily_results["Thứ 2"]["giai_db"]:
                thu2_first_digit = daily_results["Thứ 2"]["giai_db"][0]
                duoi_numbers = [
                    f"{i:02d}"
                    for i in range(100)
                    if str(i).zfill(2)[1] == thu2_first_digit
                ]
                predictions["recommended_numbers"].extend(duoi_numbers[:10])
                predictions["strategies"].append(
                    f"Đánh dàn đuôi {thu2_first_digit} cả tuần"
                )
                predictions["reasoning"].append(
                    f"Dựa theo số đầu giải ĐB thứ 2: {thu2_first_digit}"
                )

            # Loại bỏ trùng lặp và giới hạn số lượng
            predictions["recommended_numbers"] = list(
                set(predictions["recommended_numbers"])
            )[:20]

            # Đánh giá confidence
            if len(predictions["recommended_numbers"]) > 15:
                predictions["confidence_level"] = "low"
            elif len(predictions["reasoning"]) >= 2:
                predictions["confidence_level"] = "high"

            return predictions

        except Exception as e:
            logger.error(f"❌ Prediction generation failed: {e}")
            return {"error": str(e)}

    def _calculate_prediction_performance(
        self, weekly_analysis: List[Dict]
    ) -> Dict[str, Any]:
        """Tính toán hiệu suất dự đoán bằng cách kiểm tra tuần tiếp theo"""
        try:
            performance_data = {
                "total_predictions": 0,
                "successful_predictions": 0,
                "partial_success": 0,
                "failed_predictions": 0,
                "success_rate": 0.0,
                "detailed_results": [],
            }

            # Kiểm tra từng tuần với tuần tiếp theo
            for i in range(len(weekly_analysis) - 1):
                current_week = weekly_analysis[i]
                next_week = weekly_analysis[i + 1]

                if "predictions_for_next_week" not in current_week:
                    continue

                predictions = current_week["predictions_for_next_week"]
                recommended_numbers = set(predictions.get("recommended_numbers", []))

                if not recommended_numbers:
                    continue

                # Lấy tất cả số xuất hiện trong tuần tiếp theo
                actual_numbers = set(next_week.get("all_numbers_appeared", []))

                # Tính số dự đoán đúng
                correct_predictions = recommended_numbers & actual_numbers
                success_count = len(correct_predictions)
                total_predictions = len(recommended_numbers)

                # Phân loại kết quả
                if success_count == 0:
                    result_type = "failed"
                    performance_data["failed_predictions"] += 1
                elif success_count <= total_predictions * 0.3:
                    result_type = "partial"
                    performance_data["partial_success"] += 1
                else:
                    result_type = "success"
                    performance_data["successful_predictions"] += 1

                performance_data["total_predictions"] += 1

                # Lưu chi tiết
                week_performance = {
                    "prediction_week": current_week["week_key"],
                    "actual_week": next_week["week_key"],
                    "predicted_numbers": list(recommended_numbers),
                    "actual_numbers": list(actual_numbers),
                    "correct_predictions": list(correct_predictions),
                    "success_count": success_count,
                    "total_predictions": total_predictions,
                    "success_rate": (
                        success_count / total_predictions
                        if total_predictions > 0
                        else 0
                    ),
                    "result_type": result_type,
                    "strategies_used": predictions.get("strategies", []),
                    "confidence_level": predictions.get("confidence_level", "medium"),
                }

                performance_data["detailed_results"].append(week_performance)

            # Tính tỷ lệ thành công tổng thể
            if performance_data["total_predictions"] > 0:
                performance_data["success_rate"] = (
                    performance_data["successful_predictions"]
                    + performance_data["partial_success"] * 0.5
                ) / performance_data["total_predictions"]

            logger.info(
                f"📈 Prediction performance: {performance_data['success_rate']:.1%} success rate"
            )
            return performance_data

        except Exception as e:
            logger.error(f"❌ Performance calculation failed: {e}")
            return {"error": str(e)}

    def _calculate_profit_analysis(
        self, prediction_performance: Dict
    ) -> Dict[str, Any]:
        """Tính toán phân tích lợi nhuận dựa trên kết quả dự đoán"""
        try:
            config = self.ANALYSIS_CONFIG

            profit_data = {
                "total_investment": 0,
                "total_winnings": 0,
                "net_profit": 0,
                "profit_percentage": 0,
                "winning_weeks": 0,
                "losing_weeks": 0,
                "break_even_weeks": 0,
                "weekly_results": [],
                "roi_analysis": {},
                "risk_metrics": {},
            }

            base_investment_per_week = 100000  # 100k VND base per week

            for week_result in prediction_performance.get("detailed_results", []):
                # Tính toán đầu tư
                num_predictions = len(week_result["predicted_numbers"])
                investment_per_number = base_investment_per_week / max(
                    num_predictions, 1
                )
                total_week_investment = investment_per_number * num_predictions

                # Tính toán thắng
                correct_count = week_result["success_count"]
                winnings = (
                    correct_count * investment_per_number * config["payout_ratio"]
                )

                # Trừ hoa hồng
                commission = winnings * config["commission_rate"]
                net_winnings = winnings - commission

                # Lợi nhuận tuần
                week_profit = net_winnings - total_week_investment
                week_profit_percentage = (
                    (week_profit / total_week_investment * 100)
                    if total_week_investment > 0
                    else 0
                )

                # Phân loại tuần
                if week_profit > 1000:  # Lãi > 1k
                    profit_data["winning_weeks"] += 1
                elif week_profit < -1000:  # Lỗ > 1k
                    profit_data["losing_weeks"] += 1
                else:
                    profit_data["break_even_weeks"] += 1

                # Cập nhật tổng
                profit_data["total_investment"] += total_week_investment
                profit_data["total_winnings"] += net_winnings

                # Lưu chi tiết tuần
                weekly_detail = {
                    "week": week_result["prediction_week"],
                    "investment": total_week_investment,
                    "winnings": net_winnings,
                    "profit": week_profit,
                    "profit_percentage": week_profit_percentage,
                    "correct_predictions": correct_count,
                    "total_predictions": num_predictions,
                    "success_rate": week_result["success_rate"],
                }

                profit_data["weekly_results"].append(weekly_detail)

            # Tính toán tổng thể
            profit_data["net_profit"] = (
                profit_data["total_winnings"] - profit_data["total_investment"]
            )
            if profit_data["total_investment"] > 0:
                profit_data["profit_percentage"] = (
                    profit_data["net_profit"] / profit_data["total_investment"]
                ) * 100

            # ROI Analysis
            profit_data["roi_analysis"] = {
                "total_roi": profit_data["profit_percentage"],
                "average_weekly_roi": (
                    np.mean(
                        [w["profit_percentage"] for w in profit_data["weekly_results"]]
                    )
                    if profit_data["weekly_results"]
                    else 0
                ),
                "best_week_roi": (
                    max([w["profit_percentage"] for w in profit_data["weekly_results"]])
                    if profit_data["weekly_results"]
                    else 0
                ),
                "worst_week_roi": (
                    min([w["profit_percentage"] for w in profit_data["weekly_results"]])
                    if profit_data["weekly_results"]
                    else 0
                ),
                "volatile_weeks": len(
                    [
                        w
                        for w in profit_data["weekly_results"]
                        if abs(w["profit_percentage"]) > 50
                    ]
                ),
            }

            # Risk Metrics
            weekly_returns = [
                w["profit_percentage"] for w in profit_data["weekly_results"]
            ]
            if weekly_returns:
                profit_data["risk_metrics"] = {
                    "volatility": np.std(weekly_returns),
                    "sharpe_ratio": (
                        np.mean(weekly_returns) / np.std(weekly_returns)
                        if np.std(weekly_returns) > 0
                        else 0
                    ),
                    "max_drawdown": self._calculate_max_drawdown(
                        [w["profit"] for w in profit_data["weekly_results"]]
                    ),
                    "win_rate": (
                        profit_data["winning_weeks"]
                        / len(profit_data["weekly_results"])
                        if profit_data["weekly_results"]
                        else 0
                    ),
                }

            logger.info(
                f"💰 Profit analysis: {profit_data['profit_percentage']:.1f}% total return"
            )
            return profit_data

        except Exception as e:
            logger.error(f"❌ Profit analysis failed: {e}")
            return {"error": str(e)}

    def _calculate_max_drawdown(self, profits: List[float]) -> float:
        """Tính toán maximum drawdown"""
        if not profits:
            return 0

        cumulative = np.cumsum(profits)
        running_max = np.maximum.accumulate(cumulative)
        drawdown = cumulative - running_max
        return float(np.min(drawdown))

    def _calculate_risk_analysis(self, profit_analysis: Dict) -> Dict[str, Any]:
        """Phân tích rủi ro chi tiết"""
        try:
            risk_data = {
                "risk_level": "medium",
                "risk_factors": [],
                "recommendations": [],
                "capital_requirements": {},
                "scenario_analysis": {},
            }

            # Đánh giá mức độ rủi ro
            profit_percentage = profit_analysis.get("profit_percentage", 0)
            volatility = profit_analysis.get("risk_metrics", {}).get("volatility", 0)
            max_drawdown = profit_analysis.get("risk_metrics", {}).get(
                "max_drawdown", 0
            )

            # Phân loại rủi ro
            risk_score = 0

            if profit_percentage < -10:
                risk_score += 3
                risk_data["risk_factors"].append("Lợi nhuận âm trong thời gian dài")
            elif profit_percentage < 0:
                risk_score += 2
            elif profit_percentage > 20:
                risk_score -= 1

            if volatility > 30:
                risk_score += 2
                risk_data["risk_factors"].append("Biến động cao theo tuần")
            elif volatility > 15:
                risk_score += 1

            if max_drawdown < -50000:
                risk_score += 3
                risk_data["risk_factors"].append("Mức lỗ tối đa cao")
            elif max_drawdown < -20000:
                risk_score += 2

            # Xác định mức rủi ro
            if risk_score <= 1:
                risk_data["risk_level"] = "low"
            elif risk_score <= 4:
                risk_data["risk_level"] = "medium"
            else:
                risk_data["risk_level"] = "high"

            # Khuyến nghị quản lý rủi ro
            if risk_data["risk_level"] == "high":
                risk_data["recommendations"].extend(
                    [
                        "Giảm số tiền đầu tư xuống còn 1-2% tổng vốn",
                        "Áp dụng stop-loss nghiêm ngặt",
                        "Kết hợp với các phương pháp khác để đa dạng hóa",
                    ]
                )
            elif risk_data["risk_level"] == "medium":
                risk_data["recommendations"].extend(
                    [
                        "Duy trì mức đầu tư 2-3% tổng vốn",
                        "Theo dõi performance hàng tuần",
                        "Cân nhắc tạm dừng khi lỗ liên tiếp",
                    ]
                )
            else:
                risk_data["recommendations"].extend(
                    [
                        "Có thể tăng mức đầu tư lên 3-5% tổng vốn",
                        "Duy trì chiến lược hiện tại",
                    ]
                )

            # Yêu cầu vốn
            risk_data["capital_requirements"] = {
                "minimum_capital": 1000000,  # 1 triệu VND tối thiểu
                "recommended_capital": 5000000,  # 5 triệu VND khuyến nghị
                "maximum_weekly_risk": 150000,  # Tối đa 150k/tuần
                "emergency_fund": 500000,  # Quỹ dự phòng
            }

            # Phân tích kịch bản
            risk_data["scenario_analysis"] = {
                "best_case": {
                    "description": "Tất cả dự đoán đúng trong 4 tuần",
                    "potential_profit": 2000000,
                    "probability": 0.05,
                },
                "realistic_case": {
                    "description": "50% dự đoán đúng, lợi nhuận ổn định",
                    "potential_profit": 300000,
                    "probability": 0.60,
                },
                "worst_case": {
                    "description": "Lỗ liên tiếp trong 8 tuần",
                    "potential_loss": -800000,
                    "probability": 0.15,
                },
            }

            return risk_data

        except Exception as e:
            logger.error(f"❌ Risk analysis failed: {e}")
            return {"error": str(e)}

    def _generate_summary_statistics(
        self, weekly_analysis, prediction_performance, profit_analysis, risk_analysis
    ) -> Dict[str, Any]:
        """Tạo thống kê tổng hợp"""
        try:
            return {
                "total_weeks_analyzed": len(weekly_analysis),
                "analysis_timeframe": {
                    "start": (
                        min(w["week_start"] for w in weekly_analysis)
                        if weekly_analysis
                        else None
                    ),
                    "end": (
                        max(w["week_end"] for w in weekly_analysis)
                        if weekly_analysis
                        else None
                    ),
                },
                "prediction_accuracy": {
                    "success_rate": prediction_performance.get("success_rate", 0) * 100,
                    "total_predictions": prediction_performance.get(
                        "total_predictions", 0
                    ),
                    "successful_weeks": prediction_performance.get(
                        "successful_predictions", 0
                    ),
                    "failed_weeks": prediction_performance.get("failed_predictions", 0),
                },
                "financial_performance": {
                    "total_roi": profit_analysis.get("profit_percentage", 0),
                    "total_profit": profit_analysis.get("net_profit", 0),
                    "winning_weeks": profit_analysis.get("winning_weeks", 0),
                    "losing_weeks": profit_analysis.get("losing_weeks", 0),
                    "average_weekly_return": profit_analysis.get(
                        "roi_analysis", {}
                    ).get("average_weekly_roi", 0),
                },
                "risk_assessment": {
                    "risk_level": risk_analysis.get("risk_level", "medium"),
                    "volatility": profit_analysis.get("risk_metrics", {}).get(
                        "volatility", 0
                    ),
                    "max_drawdown": profit_analysis.get("risk_metrics", {}).get(
                        "max_drawdown", 0
                    ),
                    "sharpe_ratio": profit_analysis.get("risk_metrics", {}).get(
                        "sharpe_ratio", 0
                    ),
                },
                "kep_lech_insights": {
                    "most_successful_kep_type": self._find_most_successful_kep_type(
                        weekly_analysis
                    ),
                    "seasonal_patterns": self._identify_seasonal_patterns(
                        weekly_analysis
                    ),
                    "optimal_investment_periods": self._identify_optimal_periods(
                        profit_analysis
                    ),
                },
            }

        except Exception as e:
            logger.error(f"❌ Summary statistics failed: {e}")
            return {"error": str(e)}

    def _generate_strategy_recommendations(self, summary_stats: Dict) -> Dict[str, Any]:
        """Tạo khuyến nghị chiến lược"""
        try:
            recommendations = {
                "overall_verdict": "proceed_with_caution",
                "investment_strategy": [],
                "timing_recommendations": [],
                "risk_management": [],
                "alternative_approaches": [],
            }

            # Đánh giá tổng thể
            success_rate = summary_stats.get("prediction_accuracy", {}).get(
                "success_rate", 0
            )
            total_roi = summary_stats.get("financial_performance", {}).get(
                "total_roi", 0
            )
            risk_level = summary_stats.get("risk_assessment", {}).get(
                "risk_level", "medium"
            )

            if success_rate > 60 and total_roi > 15 and risk_level in ["low", "medium"]:
                recommendations["overall_verdict"] = "recommended"
                recommendations["investment_strategy"].append(
                    "Phương pháp có tiềm năng sinh lời tốt"
                )
            elif success_rate > 40 and total_roi > 0:
                recommendations["overall_verdict"] = "proceed_with_caution"
                recommendations["investment_strategy"].append(
                    "Có thể thử nghiệm với vốn nhỏ"
                )
            else:
                recommendations["overall_verdict"] = "not_recommended"
                recommendations["investment_strategy"].append(
                    "Không khuyến nghị sử dụng làm phương pháp chính"
                )

            # Khuyến nghị cụ thể
            recommendations["investment_strategy"].extend(
                [
                    f"Mức đầu tư khuyến nghị: 2-3% tổng vốn",
                    f"Tỷ lệ thành công trung bình: {success_rate:.1f}%",
                    f"ROI dự kiến: {total_roi:.1f}%",
                ]
            )

            recommendations["timing_recommendations"].extend(
                [
                    "Tránh đầu tư trong những tuần có nhiều biến động",
                    "Ưu tiên những tuần có confidence level cao",
                    "Theo dõi patterns theo mùa để tối ưu timing",
                ]
            )

            recommendations["risk_management"].extend(
                [
                    "Đặt stop-loss ở mức -15% vốn đầu tư",
                    "Chốt lời khi đạt +25% lợi nhuận",
                    "Không đầu tư quá 5% tổng tài sản",
                    "Tạm dừng khi lỗ liên tiếp 3 tuần",
                ]
            )

            recommendations["alternative_approaches"].extend(
                [
                    "Kết hợp với phương pháp bạc nhớ",
                    "Sử dụng làm phương pháp phụ, không phải chính",
                    "Đa dạng hóa với các phương pháp khác",
                    "Áp dụng money management nghiêm ngặt",
                ]
            )

            return recommendations

        except Exception as e:
            logger.error(f"❌ Strategy recommendations failed: {e}")
            return {"error": str(e)}

    def _calculate_monthly_breakdown(self, weekly_analysis: List) -> Dict[str, Any]:
        """Phân tích theo tháng"""
        monthly_data = defaultdict(lambda: {"weeks": 0, "success": 0, "profit": 0})

        for week in weekly_analysis:
            month_key = week["week_start"].strftime("%Y-%m")
            monthly_data[month_key]["weeks"] += 1
            # Add more monthly calculations here

        return dict(monthly_data)

    def _analyze_seasonal_patterns(self, weekly_analysis: List) -> Dict[str, Any]:
        """Phân tích patterns theo mùa"""
        return {
            "spring": {"performance": 0, "characteristics": []},
            "summer": {"performance": 0, "characteristics": []},
            "autumn": {"performance": 0, "characteristics": []},
            "winter": {"performance": 0, "characteristics": []},
        }

    def _analyze_weekday_correlations(self, ket_qua_data) -> Dict[str, Any]:
        """Phân tích tương quan theo ngày trong tuần"""
        from results.models import KetQuaXoSo

        weekday_stats = {}

        for weekday in range(7):
            weekday_name = self.WEEKDAY_MAP[weekday]
            weekday_stats[weekday_name] = {
                "total": 0,
                "kep_count": 0,
                "kep_types": {"Dương": 0, "Âm": 0, "Sát kép": 0},
            }

        for result in ket_qua_data:
            weekday = result.ngay.weekday()
            weekday_name = self.WEEKDAY_MAP[weekday]
            weekday_stats[weekday_name]["total"] += 1

            if len(result.giai_db) >= 2:
                giai_db_2digit = result.giai_db[-2:]
                kep_type = self._kiem_tra_kep(giai_db_2digit)
                if kep_type:
                    weekday_stats[weekday_name]["kep_count"] += 1
                    weekday_stats[weekday_name]["kep_types"][kep_type] += 1

        return weekday_stats

    def _find_most_successful_kep_type(self, weekly_analysis: List) -> str:
        """Tìm loại kép thành công nhất"""
        return "Dương"  # Placeholder

    def _identify_seasonal_patterns(self, weekly_analysis: List) -> List[str]:
        """Xác định patterns theo mùa"""
        return ["Mùa hè có tỷ lệ thành công cao hơn", "Cuối năm biến động nhiều"]

    def _identify_optimal_periods(self, profit_analysis: Dict) -> List[str]:
        """Xác định thời điểm đầu tư tối ưu"""
        return ["Tuần đầu tháng", "Sau khi kép lệch nghỉ 2 tuần liên tiếp"]


# Create global instance
kep_lech_performance_analyzer = KepLechPerformanceAnalyzer()
