#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🎯 Kép Lệch 3-Day Prediction Template
Template tính toán dự đoán Kép Lệch với chiến lược "nuôi trong 3 ngày"

Features:
- Lấy dữ liệu thực từ KetQuaXoSo database (30 ngày)
- Phân tích kết hợp Giải Đặc Biệt + Giải 7
- Dự đoán 10 con số cho 3 ngày liên tiếp
- Dừng ngay khi trúng 1 con
- Xuất kết quả JSON + Console
- Tính toán Win Rate, ROI, Pattern Analysis
"""

import json
import logging
import os
import sys
from dataclasses import asdict, dataclass
from datetime import date, datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

# Add Django setup
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'xoso_crawler.settings')

try:
    import django
    django.setup()
    from django.utils import timezone

    from results.models import KetQuaXoSo
    DJANGO_AVAILABLE = True
    print("✅ Django setup completed")
except Exception as e:
    print(f"❌ Django setup failed: {e}")
    DJANGO_AVAILABLE = False

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

@dataclass
class PredictionResult:
    """Kết quả dự đoán cho 1 ngày"""
    date: str
    predicted_numbers: List[str]
    actual_giai_db: Optional[str] = None
    actual_giai_7: Optional[List[str]] = None
    winning_numbers: List[str] = None
    hit_count: int = 0
    hit_rate: float = 0.0
    is_winning_day: bool = False
    confidence_score: float = 0.0
    strategy_used: str = ""

@dataclass
class ThreeDaySession:
    """Phiên nuôi 3 ngày"""
    session_id: str
    start_date: str
    analysis_date: str
    predicted_numbers: List[str]
    confidence_score: float
    strategy_analysis: Dict[str, Any]
    
    # Kết quả 3 ngày
    day1_result: Optional[PredictionResult] = None
    day2_result: Optional[PredictionResult] = None
    day3_result: Optional[PredictionResult] = None
    
    # Tổng kết
    total_hit_count: int = 0
    total_numbers_played: int = 0
    win_rate: float = 0.0
    winning_day: Optional[int] = None  # 1, 2, 3 hoặc None
    session_success: bool = False
    roi_percentage: float = 0.0
    profit_loss: int = 0
    stopped_early: bool = False

class KepLech3DayPredictor:
    """
    🎯 Kép Lệch 3-Day Prediction System
    """
    
    # Định nghĩa Kép Lệch theo kep_lech_analyzer.py
    KEP_DUONG = [
        "05", "50", "16", "61", "27", "72", "38", "83", "49", "94",
        "06", "60", "17", "71", "28", "82", "39", "93", "40", "04",
        "15", "51", "26", "62", "37", "73", "48", "84", "59", "95",
        "24", "42", "35", "53", "46", "64", "57", "75", "68", "86",
        "19", "91", "20", "02", "31", "13", "79", "97", "80", "08"
    ]
    
    KEP_AM = [
        "07", "70", "14", "41", "29", "92", "36", "63", "58", "85"
    ]
    
    SAT_KEP = [
        "04", "40", "06", "60", "15", "51", "95", "59", "17", "71",
        "28", "82", "26", "62", "37", "73", "39", "93", "48", "84",
        "24", "42", "35", "53"
    ]
    
    def __init__(self):
        self.analysis_history_days = 30
        self.prediction_numbers_count = 10
        self.investment_per_number = 10000  # 10k VND/con
        self.win_multiplier = 90  # x90
        self.win_amount = 900000  # 900k VND/con trúng
        
        # Internal state
        self.historical_data = {}
        self.sessions = []
        
    def get_historical_data(self, from_date: date, to_date: date) -> Dict[str, Any]:
        """
        🔄 Lấy dữ liệu lịch sử từ KetQuaXoSo database
        """
        try:
            if not DJANGO_AVAILABLE:
                logger.error("Django not available")
                return self._get_mock_data()
            
            # Lấy dữ liệu từ database
            records = KetQuaXoSo.objects.filter(
                ngay__gte=from_date,
                ngay__lte=to_date
            ).order_by('-ngay')
            
            data = {
                "giai_dac_biet": {},
                "giai_7": {},
                "raw_records": []
            }
            
            for record in records:
                date_str = record.ngay.strftime('%Y-%m-%d')
                
                # Giải đặc biệt
                data["giai_dac_biet"][date_str] = {
                    "full_number": record.giai_db,
                    "last_2_digits": record.giai_db[-2:] if len(record.giai_db) >= 2 else "",
                    "thu": record.thu,
                    "ngay": record.ngay
                }
                
                # Giải 7
                giai_7_numbers = self._extract_giai_7_numbers(record)
                data["giai_7"][date_str] = {
                    "full": record.giai_7,
                    "numbers": giai_7_numbers,
                    "thu": record.thu,
                    "ngay": record.ngay
                }
                
                data["raw_records"].append({
                    "ngay": date_str,
                    "thu": record.thu,
                    "giai_db": record.giai_db,
                    "giai_7": giai_7_numbers
                })
            
            logger.info(f"✅ Loaded {len(data['raw_records'])} records from {from_date} to {to_date}")
            return data
            
        except Exception as e:
            logger.error(f"❌ Error loading historical data: {e}")
            return self._get_mock_data()
    
    def _extract_giai_7_numbers(self, record) -> List[str]:
        """Trích xuất số 2 chữ số từ giải 7"""
        try:
            numbers = []
            
            # Từ giải 7 đầy đủ
            if record.giai_7:
                for num_str in str(record.giai_7).replace(",", " ").replace("-", " ").split():
                    if num_str.isdigit() and len(num_str) >= 2:
                        numbers.append(num_str[-2:].zfill(2))
            
            # Từ các trường riêng lẻ
            for field in [record.giai_7_1, record.giai_7_2, record.giai_7_3, record.giai_7_4]:
                if field and str(field).isdigit():
                    numbers.append(str(field)[-2:].zfill(2))
            
            return list(set(numbers))  # Loại bỏ trùng lặp
            
        except Exception as e:
            logger.warning(f"Error extracting giải 7: {e}")
            return []
    
    def _get_mock_data(self) -> Dict[str, Any]:
        """Dữ liệu mock cho testing"""
        return {
            "giai_dac_biet": {},
            "giai_7": {},
            "raw_records": []
        }
    
    def analyze_kep_lech_patterns(self, historical_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        🔍 Phân tích pattern Kép Lệch từ dữ liệu lịch sử
        Kết hợp Giải Đặc Biệt + Giải 7
        """
        try:
            analysis = {
                "giai_dac_biet_analysis": self._analyze_giai_dac_biet(historical_data["giai_dac_biet"]),
                "giai_7_analysis": self._analyze_giai_7(historical_data["giai_7"]),
                "combined_analysis": {},
                "frequency_patterns": {},
                "trend_analysis": {},
                "confidence_factors": []
            }
            
            # Kết hợp phân tích từ cả 2 giải
            analysis["combined_analysis"] = self._combine_analyses(
                analysis["giai_dac_biet_analysis"],
                analysis["giai_7_analysis"]
            )
            
            # Phân tích tần suất
            analysis["frequency_patterns"] = self._analyze_frequency_patterns(historical_data)
            
            # Phân tích xu hướng
            analysis["trend_analysis"] = self._analyze_trend_patterns(historical_data)
            
            # Tính confidence factors
            analysis["confidence_factors"] = self._calculate_confidence_factors(analysis)
            
            return analysis
            
        except Exception as e:
            logger.error(f"❌ Pattern analysis failed: {e}")
            return {"error": str(e)}
    
    def _analyze_giai_dac_biet(self, giai_db_data: Dict[str, Any]) -> Dict[str, Any]:
        """Phân tích Kép Lệch từ Giải Đặc Biệt"""
        analysis = {
            "kep_duong_count": 0,
            "kep_am_count": 0,
            "sat_kep_count": 0,
            "other_count": 0,
            "kep_candidates": [],
            "frequency_map": {}
        }
        
        for date_str, data in giai_db_data.items():
            last_2 = data["last_2_digits"]
            
            if last_2 in self.KEP_DUONG:
                analysis["kep_duong_count"] += 1
                analysis["kep_candidates"].append(last_2)
            elif last_2 in self.KEP_AM:
                analysis["kep_am_count"] += 1
                analysis["kep_candidates"].append(last_2)
            elif last_2 in self.SAT_KEP:
                analysis["sat_kep_count"] += 1
                analysis["kep_candidates"].append(last_2)
            else:
                analysis["other_count"] += 1
            
            # Frequency mapping
            if last_2 not in analysis["frequency_map"]:
                analysis["frequency_map"][last_2] = 0
            analysis["frequency_map"][last_2] += 1
        
        return analysis
    
    def _analyze_giai_7(self, giai_7_data: Dict[str, Any]) -> Dict[str, Any]:
        """Phân tích Kép Lệch từ Giải 7"""
        analysis = {
            "kep_duong_count": 0,
            "kep_am_count": 0,
            "sat_kep_count": 0,
            "kep_candidates": [],
            "frequency_map": {}
        }
        
        for date_str, data in giai_7_data.items():
            for number in data["numbers"]:
                if number in self.KEP_DUONG:
                    analysis["kep_duong_count"] += 1
                    analysis["kep_candidates"].append(number)
                elif number in self.KEP_AM:
                    analysis["kep_am_count"] += 1
                    analysis["kep_candidates"].append(number)
                elif number in self.SAT_KEP:
                    analysis["sat_kep_count"] += 1
                    analysis["kep_candidates"].append(number)
                
                # Frequency mapping
                if number not in analysis["frequency_map"]:
                    analysis["frequency_map"][number] = 0
                analysis["frequency_map"][number] += 1
        
        return analysis
    
    def _combine_analyses(self, db_analysis: Dict, g7_analysis: Dict) -> Dict[str, Any]:
        """Kết hợp phân tích từ cả 2 giải"""
        combined = {
            "total_kep_candidates": set(),
            "priority_scores": {},
            "weighted_frequencies": {}
        }
        
        # Kết hợp candidates
        combined["total_kep_candidates"].update(db_analysis["kep_candidates"])
        combined["total_kep_candidates"].update(g7_analysis["kep_candidates"])
        
        # Tính priority scores (Giải DB = 0.7, Giải 7 = 0.3)
        for candidate in combined["total_kep_candidates"]:
            db_freq = db_analysis["frequency_map"].get(candidate, 0)
            g7_freq = g7_analysis["frequency_map"].get(candidate, 0)
            
            combined_score = (db_freq * 0.7) + (g7_freq * 0.3)
            combined["priority_scores"][candidate] = combined_score
            combined["weighted_frequencies"][candidate] = {
                "giai_db": db_freq,
                "giai_7": g7_freq,
                "combined": combined_score
            }
        
        return combined
    
    def _analyze_frequency_patterns(self, historical_data: Dict[str, Any]) -> Dict[str, Any]:
        """Phân tích pattern tần suất"""
        patterns = {
            "missing_kep_duong": [],
            "missing_kep_am": [],
            "missing_sat_kep": [],
            "hot_numbers": [],
            "cold_numbers": []
        }
        
        # Tìm số chưa xuất hiện
        all_appeared = set()
        for record in historical_data["raw_records"]:
            all_appeared.add(record["giai_db"][-2:])
            all_appeared.update(record["giai_7"])
        
        patterns["missing_kep_duong"] = [num for num in self.KEP_DUONG if num not in all_appeared]
        patterns["missing_kep_am"] = [num for num in self.KEP_AM if num not in all_appeared]
        patterns["missing_sat_kep"] = [num for num in self.SAT_KEP if num not in all_appeared]
        
        return patterns
    
    def _analyze_trend_patterns(self, historical_data: Dict[str, Any]) -> Dict[str, Any]:
        """Phân tích xu hướng"""
        trends = {
            "recent_kep_types": [],
            "consecutive_patterns": [],
            "day_preferences": {}
        }
        
        # Phân tích 7 ngày gần nhất
        recent_records = sorted(historical_data["raw_records"], 
                               key=lambda x: x["ngay"], reverse=True)[:7]
        
        for record in recent_records:
            last_2 = record["giai_db"][-2:]
            if last_2 in self.KEP_DUONG:
                trends["recent_kep_types"].append("DUONG")
            elif last_2 in self.KEP_AM:
                trends["recent_kep_types"].append("AM")
            elif last_2 in self.SAT_KEP:
                trends["recent_kep_types"].append("SAT_KEP")
            else:
                trends["recent_kep_types"].append("OTHER")
        
        return trends
    
    def _calculate_confidence_factors(self, analysis: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Tính toán các yếu tố confidence"""
        factors = []
        
        # Factor 1: Data completeness
        total_candidates = len(analysis["combined_analysis"]["total_kep_candidates"])
        factors.append({
            "factor": "data_completeness",
            "score": min(total_candidates / 20.0, 1.0),
            "description": f"Found {total_candidates} kep candidates"
        })
        
        # Factor 2: Pattern consistency
        kep_types = analysis["trend_analysis"]["recent_kep_types"]
        consistency = len(set(kep_types)) / len(kep_types) if kep_types else 0
        factors.append({
            "factor": "pattern_consistency",
            "score": 1.0 - consistency,  # Consistent = good
            "description": f"Pattern consistency: {consistency:.2f}"
        })
        
        # Factor 3: Frequency distribution
        frequencies = analysis["combined_analysis"]["priority_scores"]
        if frequencies:
            avg_freq = sum(frequencies.values()) / len(frequencies)
            max_freq = max(frequencies.values())
            freq_score = min(avg_freq / max_freq, 1.0) if max_freq > 0 else 0
            factors.append({
                "factor": "frequency_distribution",
                "score": freq_score,
                "description": f"Frequency balance: {freq_score:.2f}"
            })
        
        return factors
    
    def generate_3day_predictions(self, analysis: Dict[str, Any], analysis_date: date) -> Dict[str, Any]:
        """
        🎯 Tạo dự đoán cho 3 ngày liên tiếp
        """
        try:
            # Chọn top 10 số có priority score cao nhất
            priority_scores = analysis["combined_analysis"]["priority_scores"]
            
            # Nếu không đủ số từ analysis, bổ sung từ missing numbers
            top_candidates = sorted(priority_scores.items(), 
                                  key=lambda x: x[1], reverse=True)[:self.prediction_numbers_count]
            
            predicted_numbers = [candidate[0] for candidate in top_candidates]
            
            # Nếu vẫn không đủ, bổ sung từ missing numbers
            if len(predicted_numbers) < self.prediction_numbers_count:
                missing_numbers = (analysis["frequency_patterns"]["missing_kep_duong"][:3] +
                                 analysis["frequency_patterns"]["missing_kep_am"][:2] +
                                 analysis["frequency_patterns"]["missing_sat_kep"][:2])
                
                for num in missing_numbers:
                    if num not in predicted_numbers and len(predicted_numbers) < self.prediction_numbers_count:
                        predicted_numbers.append(num)
            
            # Tính confidence score
            confidence_factors = analysis["confidence_factors"]
            confidence_score = sum(factor["score"] for factor in confidence_factors) / len(confidence_factors) if confidence_factors else 0.5
            
            # Tạo session
            session = ThreeDaySession(
                session_id=f"session_{analysis_date.strftime('%Y%m%d')}",
                start_date=(analysis_date + timedelta(days=1)).strftime('%Y-%m-%d'),
                analysis_date=analysis_date.strftime('%Y-%m-%d'),
                predicted_numbers=predicted_numbers[:self.prediction_numbers_count],
                confidence_score=confidence_score,
                strategy_analysis={
                    "method": "combined_giai_db_giai_7",
                    "top_candidates": dict(top_candidates),
                    "confidence_factors": confidence_factors,
                    "analysis_summary": {
                        "giai_db_kep_count": (analysis["giai_dac_biet_analysis"]["kep_duong_count"] +
                                            analysis["giai_dac_biet_analysis"]["kep_am_count"] +
                                            analysis["giai_dac_biet_analysis"]["sat_kep_count"]),
                        "giai_7_kep_count": (analysis["giai_7_analysis"]["kep_duong_count"] +
                                           analysis["giai_7_analysis"]["kep_am_count"] +
                                           analysis["giai_7_analysis"]["sat_kep_count"]),
                        "total_candidates": len(analysis["combined_analysis"]["total_kep_candidates"])
                    }
                }
            )
            
            return {
                "session": session,
                "success": True,
                "message": f"Generated predictions for 3 days starting {session.start_date}"
            }
            
        except Exception as e:
            logger.error(f"❌ Prediction generation failed: {e}")
            return {"success": False, "error": str(e)}
    
    def evaluate_session_results(self, session: ThreeDaySession, 
                                actual_results: List[Dict[str, Any]]) -> ThreeDaySession:
        """
        📊 Đánh giá kết quả phiên nuôi 3 ngày
        """
        try:
            day_results = []
            total_investment = 0
            total_winnings = 0
            winning_day = None
            
            for day_idx, actual_data in enumerate(actual_results, 1):
                # Tạo result cho ngày
                day_result = PredictionResult(
                    date=actual_data["ngay"],
                    predicted_numbers=session.predicted_numbers.copy(),
                    actual_giai_db=actual_data.get("giai_db"),
                    actual_giai_7=actual_data.get("giai_7", []),
                    strategy_used=session.strategy_analysis["method"]
                )
                
                # Tìm số trúng
                winning_numbers = []
                if day_result.actual_giai_db and len(day_result.actual_giai_db) >= 2:
                    giai_db_last2 = day_result.actual_giai_db[-2:]
                    if giai_db_last2 in day_result.predicted_numbers:
                        winning_numbers.append(giai_db_last2)
                
                for g7_num in day_result.actual_giai_7:
                    if g7_num in day_result.predicted_numbers and g7_num not in winning_numbers:
                        winning_numbers.append(g7_num)
                
                day_result.winning_numbers = winning_numbers
                day_result.hit_count = len(winning_numbers)
                day_result.hit_rate = day_result.hit_count / len(day_result.predicted_numbers)
                day_result.is_winning_day = day_result.hit_count > 0
                
                # Tính toán tài chính
                daily_investment = len(session.predicted_numbers) * self.investment_per_number
                daily_winnings = day_result.hit_count * self.win_amount
                
                total_investment += daily_investment
                total_winnings += daily_winnings
                
                # Nếu thắng và chưa có ngày thắng trước đó
                if day_result.is_winning_day and winning_day is None:
                    winning_day = day_idx
                
                day_results.append(day_result)
                
                # Dừng sớm nếu thắng (theo yêu cầu)
                if day_result.is_winning_day:
                    session.stopped_early = True
                    break
            
            # Cập nhật session results
            if len(day_results) >= 1:
                session.day1_result = day_results[0]
            if len(day_results) >= 2:
                session.day2_result = day_results[1]
            if len(day_results) >= 3:
                session.day3_result = day_results[2]
            
            # Tính tổng kết
            session.total_hit_count = sum(result.hit_count for result in day_results)
            session.total_numbers_played = total_investment // self.investment_per_number
            session.win_rate = session.total_hit_count / session.total_numbers_played if session.total_numbers_played > 0 else 0
            session.winning_day = winning_day
            session.session_success = winning_day is not None
            session.profit_loss = total_winnings - total_investment
            session.roi_percentage = (session.profit_loss / total_investment * 100) if total_investment > 0 else 0
            
            return session
            
        except Exception as e:
            logger.error(f"❌ Session evaluation failed: {e}")
            return session
    
    def create_analysis_report(self, sessions: List[ThreeDaySession]) -> Dict[str, Any]:
        """
        📈 Tạo báo cáo phân tích tổng hợp
        """
        if not sessions:
            return {"error": "No sessions to analyze"}
        
        # Tính toán metrics tổng hợp
        total_sessions = len(sessions)
        successful_sessions = sum(1 for s in sessions if s.session_success)
        total_investment = sum(abs(s.profit_loss) + (s.profit_loss if s.profit_loss > 0 else 0) 
                             for s in sessions)
        total_profit_loss = sum(s.profit_loss for s in sessions)
        
        # Win rates
        overall_success_rate = successful_sessions / total_sessions if total_sessions > 0 else 0
        average_win_rate = sum(s.win_rate for s in sessions) / total_sessions if total_sessions > 0 else 0
        average_roi = sum(s.roi_percentage for s in sessions) / total_sessions if total_sessions > 0 else 0
        
        # Pattern analysis
        winning_day_distribution = {"day1": 0, "day2": 0, "day3": 0, "no_win": 0}
        confidence_vs_success = []
        
        for session in sessions:
            if session.winning_day == 1:
                winning_day_distribution["day1"] += 1
            elif session.winning_day == 2:
                winning_day_distribution["day2"] += 1
            elif session.winning_day == 3:
                winning_day_distribution["day3"] += 1
            else:
                winning_day_distribution["no_win"] += 1
            
            confidence_vs_success.append({
                "confidence": session.confidence_score,
                "success": session.session_success,
                "roi": session.roi_percentage
            })
        
        # Top performing strategies
        strategy_performance = {}
        for session in sessions:
            strategy = session.strategy_analysis.get("method", "unknown")
            if strategy not in strategy_performance:
                strategy_performance[strategy] = {"count": 0, "success": 0, "total_roi": 0}
            
            strategy_performance[strategy]["count"] += 1
            if session.session_success:
                strategy_performance[strategy]["success"] += 1
            strategy_performance[strategy]["total_roi"] += session.roi_percentage
        
        # Calculate strategy success rates
        for strategy in strategy_performance:
            perf = strategy_performance[strategy]
            perf["success_rate"] = perf["success"] / perf["count"] if perf["count"] > 0 else 0
            perf["average_roi"] = perf["total_roi"] / perf["count"] if perf["count"] > 0 else 0
        
        report = {
            "summary": {
                "total_sessions": total_sessions,
                "successful_sessions": successful_sessions,
                "overall_success_rate": overall_success_rate,
                "average_win_rate": average_win_rate,
                "average_roi_percentage": average_roi,
                "total_profit_loss": total_profit_loss,
                "total_investment": total_investment
            },
            "performance_analysis": {
                "winning_day_distribution": winning_day_distribution,
                "confidence_vs_success": confidence_vs_success,
                "strategy_performance": strategy_performance
            },
            "detailed_sessions": [asdict(session) for session in sessions],
            "recommendations": self._generate_recommendations(sessions),
            "risk_analysis": self._analyze_risk_factors(sessions)
        }
        
        return report
    
    def _generate_recommendations(self, sessions: List[ThreeDaySession]) -> List[str]:
        """Tạo khuyến nghị dựa trên kết quả"""
        recommendations = []
        
        if not sessions:
            return ["No data available for recommendations"]
        
        success_rate = sum(1 for s in sessions if s.session_success) / len(sessions)
        avg_roi = sum(s.roi_percentage for s in sessions) / len(sessions)
        
        if success_rate < 0.3:
            recommendations.append("⚠️ Tỷ lệ thành công thấp (<30%). Cần xem xét lại chiến lược.")
        elif success_rate > 0.6:
            recommendations.append("✅ Tỷ lệ thành công cao (>60%). Chiến lược hiệu quả.")
        
        if avg_roi < -20:
            recommendations.append("💸 ROI âm cao. Cân nhắc giảm số con đánh hoặc dừng lỗ.")
        elif avg_roi > 20:
            recommendations.append("💰 ROI tích cực. Có thể duy trì chiến lược hiện tại.")
        
        # Analyze winning day patterns
        day1_wins = sum(1 for s in sessions if s.winning_day == 1)
        if day1_wins / len(sessions) > 0.5:
            recommendations.append("🎯 Thường thắng ngày đầu. Có thể giảm số ngày nuôi.")
        
        return recommendations
    
    def _analyze_risk_factors(self, sessions: List[ThreeDaySession]) -> Dict[str, Any]:
        """Phân tích các yếu tố rủi ro"""
        if not sessions:
            return {}
        
        losing_streaks = []
        current_streak = 0
        
        for session in sessions:
            if not session.session_success:
                current_streak += 1
            else:
                if current_streak > 0:
                    losing_streaks.append(current_streak)
                current_streak = 0
        
        if current_streak > 0:
            losing_streaks.append(current_streak)
        
        max_losing_streak = max(losing_streaks) if losing_streaks else 0
        avg_losing_streak = sum(losing_streaks) / len(losing_streaks) if losing_streaks else 0
        
        return {
            "max_losing_streak": max_losing_streak,
            "average_losing_streak": avg_losing_streak,
            "total_losing_streaks": len(losing_streaks),
            "risk_level": "HIGH" if max_losing_streak >= 5 else "MEDIUM" if max_losing_streak >= 3 else "LOW"
        }
    
    def save_results_to_json(self, report: Dict[str, Any], filename: str = None) -> str:
        """
        💾 Lưu kết quả ra file JSON
        """
        if filename is None:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"kep_lech_3day_report_{timestamp}.json"
        
        filepath = Path(filename)
        
        try:
            # Convert datetime objects to strings for JSON serialization
            json_report = json.loads(json.dumps(report, default=str, ensure_ascii=False, indent=2))
            
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(json_report, f, ensure_ascii=False, indent=2)
            
            logger.info(f"✅ Report saved to {filepath}")
            return str(filepath)
            
        except Exception as e:
            logger.error(f"❌ Failed to save report: {e}")
            return ""
    
    def run_analysis_demo(self, analysis_date: date = None) -> Dict[str, Any]:
        """
        🚀 Chạy demo phân tích hoàn chỉnh
        """
        try:
            if analysis_date is None:
                analysis_date = date.today() - timedelta(days=4)  # Đảm bảo có dữ liệu thực tế
            
            print(f"🚀 Starting Kép Lệch 3-Day Analysis Demo")
            print(f"📅 Analysis Date: {analysis_date}")
            print("=" * 70)
            
            # 1. Lấy dữ liệu lịch sử
            print("📊 Step 1: Loading historical data...")
            from_date = analysis_date - timedelta(days=self.analysis_history_days)
            historical_data = self.get_historical_data(from_date, analysis_date)
            
            if not historical_data["raw_records"]:
                print("❌ No historical data available")
                return {"success": False, "error": "No data"}
            
            print(f"✅ Loaded {len(historical_data['raw_records'])} historical records")
            
            # 2. Phân tích patterns
            print("🔍 Step 2: Analyzing Kép Lệch patterns...")
            pattern_analysis = self.analyze_kep_lech_patterns(historical_data)
            
            if "error" in pattern_analysis:
                print(f"❌ Pattern analysis failed: {pattern_analysis['error']}")
                return {"success": False, "error": pattern_analysis["error"]}
            
            print("✅ Pattern analysis completed")
            
            # 3. Tạo dự đoán 3 ngày
            print("🎯 Step 3: Generating 3-day predictions...")
            prediction_result = self.generate_3day_predictions(pattern_analysis, analysis_date)
            
            if not prediction_result["success"]:
                print(f"❌ Prediction failed: {prediction_result['error']}")
                return prediction_result
            
            session = prediction_result["session"]
            print(f"✅ Generated predictions: {session.predicted_numbers}")
            print(f"📈 Confidence Score: {session.confidence_score:.2f}")
            
            # 4. Lấy kết quả thực tế cho 3 ngày tiếp theo (nếu có)
            print("📋 Step 4: Loading actual results for evaluation...")
            future_dates = [analysis_date + timedelta(days=i) for i in range(1, 4)]
            actual_results = []
            
            for future_date in future_dates:
                try:
                    if DJANGO_AVAILABLE:
                        record = KetQuaXoSo.objects.filter(ngay=future_date).first()
                        if record:
                            actual_results.append({
                                "ngay": future_date.strftime('%Y-%m-%d'),
                                "giai_db": record.giai_db,
                                "giai_7": self._extract_giai_7_numbers(record)
                            })
                        else:
                            print(f"⚠️ No actual data for {future_date}")
                            break
                    else:
                        break
                except Exception as e:
                    print(f"⚠️ Could not load data for {future_date}: {e}")
                    break
            
            # 5. Đánh giá kết quả
            if actual_results:
                print(f"📊 Step 5: Evaluating results for {len(actual_results)} days...")
                session = self.evaluate_session_results(session, actual_results)
                
                print("\n📈 EVALUATION RESULTS:")
                print(f"   Success: {'✅ YES' if session.session_success else '❌ NO'}")
                print(f"   Winning Day: {session.winning_day if session.winning_day else 'None'}")
                print(f"   Total Hits: {session.total_hit_count}")
                print(f"   Win Rate: {session.win_rate:.2%}")
                print(f"   ROI: {session.roi_percentage:.1f}%")
                print(f"   Profit/Loss: {session.profit_loss:,} VND")
            else:
                print("⚠️ Step 5: No actual results available for evaluation")
            
            # 6. Tạo báo cáo
            print("📋 Step 6: Creating analysis report...")
            report = self.create_analysis_report([session])
            
            # 7. Lưu kết quả
            print("💾 Step 7: Saving results...")
            saved_file = self.save_results_to_json(report)
            
            print("\n" + "=" * 70)
            print("🎉 DEMO COMPLETED SUCCESSFULLY!")
            print(f"📄 Report saved to: {saved_file}")
            print("=" * 70)
            
            return {
                "success": True,
                "session": session,
                "report": report,
                "saved_file": saved_file
            }
            
        except Exception as e:
            logger.error(f"❌ Demo failed: {e}")
            print(f"❌ Demo failed: {e}")
            return {"success": False, "error": str(e)}

def main():
    """
    🎯 Main function - chạy demo
    """
    predictor = KepLech3DayPredictor()
    
    # Chạy demo với ngày phân tích cụ thể
    demo_date = date(2025, 7, 28)  # Có thể thay đổi ngày này
    
    result = predictor.run_analysis_demo(demo_date)
    
    if result["success"]:
        print("\n🎊 Demo completed successfully!")
        if "session" in result:
            session = result["session"]
            print(f"\n📊 QUICK SUMMARY:")
            print(f"   Analysis Date: {session.analysis_date}")
            print(f"   Predicted Numbers: {', '.join(session.predicted_numbers)}")
            print(f"   Confidence: {session.confidence_score:.2f}")
            if hasattr(session, 'session_success'):
                print(f"   Success: {'✅' if session.session_success else '❌'}")
                print(f"   ROI: {session.roi_percentage:.1f}%")
    else:
        print(f"\n❌ Demo failed: {result.get('error', 'Unknown error')}")

if __name__ == "__main__":
    main()
