"""
PHASE 4 - CAU CHAY CYCLE ANALYZER
=================================
Advanced Cầu Chảy (Bridge Flow) analysis with cycle prediction and pattern detection.
Integrates with Phase 3 architecture for ensemble predictions.

Author: Phase 4 Development Team
Created: January 2025
Version: 4.0.0
"""

import json
import logging
import math
from collections import Counter, defaultdict, deque
from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum
from typing import Dict, List, Optional, Tuple, Union

import numpy as np
import pandas as pd
from django.core.cache import cache
from django.db.models import Avg, Count, Q

# Django imports
from django.utils import timezone

# Project imports
from lokhung.models import KetQuaXoSo, PhanTichSo
from lottery_prediction.models import PredictionResult

# Configure logging
logger = logging.getLogger(__name__)


class CauChayType(Enum):
    """Các loại Cầu Chảy"""

    DANG_VE = "dang_ve"  # Đang về
    SAP_VE = "sap_ve"  # Sắp về
    QUA_HAN = "qua_han"  # Quá hạn
    NONG_LANH = "nong_lanh"  # Nóng lạnh
    CYCLE_PATTERN = "cycle_pattern"  # Chu kỳ đặc biệt


class CauChayPattern(Enum):
    """Các pattern của Cầu Chảy"""

    ASCENDING = "ascending"  # Tăng dần
    DESCENDING = "descending"  # Giảm dần
    OSCILLATING = "oscillating"  # Dao động
    BREAKING = "breaking"  # Đang phá
    FORMING = "forming"  # Đang hình thành


@dataclass
class CauChayData:
    """Dữ liệu Cầu Chảy cho một số"""

    number: int
    last_appearance: datetime
    days_absent: int
    cycle_length: int
    pattern_type: CauChayPattern
    heat_level: float  # Mức độ nóng/lạnh (0-1)
    prediction_weight: float
    historical_cycles: List[int]
    confidence: float


@dataclass
class CauChayAnalysisResult:
    """Kết quả phân tích Cầu Chảy"""

    numbers: List[int]
    confidence: float
    cau_chay_data: List[CauChayData]
    analysis_details: Dict
    method_weight: float
    processing_time: float
    timestamp: datetime
    heat_map: Dict[int, float]


class CauChayCycleAnalyzer:
    """
    Analyzer chuyên sâu về Cầu Chảy với thuật toán cycle prediction
    """

    def __init__(self):
        self.name = "Cau Chay Cycle Analyzer"
        self.version = "4.0.0"
        self.method_weight = 0.18  # 18% weight trong ensemble
        self.cache_timeout = 300  # 5 minutes

        # Cycle analysis parameters
        self.max_cycle_length = 50  # Tối đa 50 ngày
        self.min_cycle_length = 3  # Tối thiểu 3 ngày
        self.heat_threshold_hot = 0.7  # Ngưỡng nóng
        self.heat_threshold_cold = 0.3  # Ngưỡng lạnh
        self.analysis_window = 120  # 120 ngày phân tích

        # Pattern detection parameters
        self.pattern_sensitivity = 0.15
        self.confidence_threshold = 0.6
        self.cycle_variance_threshold = 0.3

        logger.info(f"🌊 {self.name} v{self.version} initialized")

    def analyze(
        self, region: str, date: datetime, historical_data: Optional[List] = None
    ) -> CauChayAnalysisResult:
        """
        Phân tích Cầu Chảy cho region và date cụ thể

        Args:
            region: Tên miền (MB, MT, MN)
            date: Ngày cần dự đoán
            historical_data: Dữ liệu lịch sử (optional)

        Returns:
            CauChayAnalysisResult: Kết quả phân tích đầy đủ
        """
        start_time = datetime.now()

        try:
            # Check cache
            cache_key = f"cau_chay_analysis_{region}_{date.strftime('%Y%m%d')}"
            cached_result = cache.get(cache_key)

            if cached_result:
                logger.info(f"🎯 Cache hit for Cau Chay analysis: {cache_key}")
                return CauChayAnalysisResult(**cached_result)

            # Get historical data
            if not historical_data:
                historical_data = self._get_historical_data(region, date)

            # Perform comprehensive cycle analysis
            cau_chay_data = self._analyze_all_numbers(historical_data, date)
            heat_map = self._generate_heat_map(cau_chay_data)
            numbers = self._select_predictions(cau_chay_data, heat_map)
            confidence = self._calculate_overall_confidence(cau_chay_data, numbers)
            analysis_details = self._generate_analysis_details(cau_chay_data, heat_map)

            # Create result
            result = CauChayAnalysisResult(
                numbers=numbers,
                confidence=confidence,
                cau_chay_data=cau_chay_data,
                analysis_details=analysis_details,
                method_weight=self.method_weight,
                processing_time=(datetime.now() - start_time).total_seconds(),
                timestamp=timezone.now(),
                heat_map=heat_map,
            )

            # Cache result
            cache.set(cache_key, result.__dict__, self.cache_timeout)

            logger.info(
                f"🌊 Cau Chay analysis completed: {len(numbers)} numbers, "
                f"confidence {confidence:.2f}"
            )

            return result

        except Exception as e:
            logger.error(f"❌ Error in Cau Chay analysis: {str(e)}")
            return self._create_fallback_result(start_time)

    def _get_historical_data(self, region: str, date: datetime) -> List[Dict]:
        """Lấy dữ liệu lịch sử cho phân tích"""
        try:
            end_date = date - timedelta(days=1)
            start_date = end_date - timedelta(days=self.analysis_window)

            queryset = KetQuaXoSo.objects.filter(
                ngay__range=[start_date, end_date], mien__icontains=region
            ).order_by("-ngay")

            historical_data = []
            for record in queryset:
                numbers = self._extract_all_numbers(record)
                historical_data.append(
                    {"date": record.ngay, "numbers": numbers, "record": record}
                )

            logger.info(
                f"📊 Retrieved {len(historical_data)} records for Cau Chay analysis"
            )
            return historical_data

        except Exception as e:
            logger.error(f"❌ Error getting historical data: {str(e)}")
            return []

    def _extract_all_numbers(self, record) -> List[int]:
        """Trích xuất tất cả số từ kết quả"""
        numbers = []
        prize_fields = [
            "giai_dac_biet",
            "giai_nhat",
            "giai_nhi",
            "giai_ba",
            "giai_tu",
            "giai_nam",
            "giai_sau",
            "giai_bay",
        ]

        for field in prize_fields:
            value = getattr(record, field, None)
            if value:
                if isinstance(value, str):
                    parts = value.replace(" ", "").split(",")
                    for part in parts:
                        if part.isdigit():
                            numbers.append(int(part) % 100)
                elif isinstance(value, int):
                    numbers.append(value % 100)

        return list(set(numbers))

    def _analyze_all_numbers(
        self, historical_data: List[Dict], target_date: datetime
    ) -> List[CauChayData]:
        """Phân tích tất cả các số từ 00-99"""
        cau_chay_data = []

        try:
            # Analyze each number from 00 to 99
            for number in range(100):
                data = self._analyze_single_number(number, historical_data, target_date)
                if data:
                    cau_chay_data.append(data)

            # Sort by prediction weight and confidence
            cau_chay_data.sort(
                key=lambda x: x.prediction_weight * x.confidence, reverse=True
            )

            logger.info(
                f"🔍 Analyzed {len(cau_chay_data)} numbers for Cau Chay patterns"
            )
            return cau_chay_data

        except Exception as e:
            logger.error(f"❌ Error analyzing numbers: {str(e)}")
            return []

    def _analyze_single_number(
        self, number: int, historical_data: List[Dict], target_date: datetime
    ) -> Optional[CauChayData]:
        """Phân tích chi tiết một số cụ thể"""
        try:
            # Find all appearances of this number
            appearances = []
            for record in historical_data:
                if number in record["numbers"]:
                    appearances.append(record["date"])

            if len(appearances) < 2:
                return None  # Not enough data

            # Sort appearances (newest first)
            appearances.sort(reverse=True)

            # Calculate basic metrics
            last_appearance = appearances[0]
            days_absent = (target_date.date() - last_appearance).days

            # Calculate historical cycles
            cycles = []
            for i in range(len(appearances) - 1):
                cycle_length = (appearances[i] - appearances[i + 1]).days
                if self.min_cycle_length <= cycle_length <= self.max_cycle_length:
                    cycles.append(cycle_length)

            if not cycles:
                return None

            # Calculate average cycle and pattern
            avg_cycle = np.mean(cycles)
            cycle_variance = np.var(cycles) if len(cycles) > 1 else 0

            # Determine pattern type
            pattern_type = self._determine_pattern_type(cycles, days_absent, avg_cycle)

            # Calculate heat level
            heat_level = self._calculate_heat_level(
                number, historical_data, days_absent, avg_cycle
            )

            # Calculate prediction weight
            prediction_weight = self._calculate_prediction_weight(
                days_absent, avg_cycle, cycle_variance, heat_level, len(cycles)
            )

            # Calculate confidence
            confidence = self._calculate_number_confidence(
                cycles, days_absent, avg_cycle, cycle_variance
            )

            return CauChayData(
                number=number,
                last_appearance=last_appearance,
                days_absent=days_absent,
                cycle_length=int(avg_cycle),
                pattern_type=pattern_type,
                heat_level=heat_level,
                prediction_weight=prediction_weight,
                historical_cycles=cycles,
                confidence=confidence,
            )

        except Exception as e:
            logger.error(f"❌ Error analyzing number {number}: {str(e)}")
            return None

    def _determine_pattern_type(
        self, cycles: List[int], days_absent: int, avg_cycle: float
    ) -> CauChayPattern:
        """Xác định loại pattern của số"""
        try:
            if len(cycles) < 3:
                return CauChayPattern.FORMING

            # Analyze recent trend
            recent_cycles = cycles[: min(5, len(cycles))]

            # Check for ascending pattern (cycles getting longer)
            if len(recent_cycles) >= 3:
                ascending_count = sum(
                    1
                    for i in range(len(recent_cycles) - 1)
                    if recent_cycles[i] > recent_cycles[i + 1]
                )
                descending_count = sum(
                    1
                    for i in range(len(recent_cycles) - 1)
                    if recent_cycles[i] < recent_cycles[i + 1]
                )

                if ascending_count >= len(recent_cycles) * 0.6:
                    return CauChayPattern.ASCENDING
                elif descending_count >= len(recent_cycles) * 0.6:
                    return CauChayPattern.DESCENDING

            # Check if breaking pattern (overdue)
            if days_absent > avg_cycle * 1.5:
                return CauChayPattern.BREAKING

            # Check for oscillating pattern
            if len(cycles) >= 4:
                oscillations = 0
                for i in range(1, len(cycles) - 1):
                    if (cycles[i - 1] < cycles[i] > cycles[i + 1]) or (
                        cycles[i - 1] > cycles[i] < cycles[i + 1]
                    ):
                        oscillations += 1

                if oscillations >= len(cycles) * 0.4:
                    return CauChayPattern.OSCILLATING

            return CauChayPattern.FORMING

        except Exception as e:
            return CauChayPattern.FORMING

    def _calculate_heat_level(
        self,
        number: int,
        historical_data: List[Dict],
        days_absent: int,
        avg_cycle: float,
    ) -> float:
        """Tính mức độ nóng/lạnh của số"""
        try:
            # Count recent appearances
            recent_data = historical_data[:20]  # Last 20 draws
            recent_appearances = sum(
                1 for record in recent_data if number in record["numbers"]
            )

            # Calculate base heat from recent frequency
            recent_heat = min(
                1.0, recent_appearances / 5
            )  # Max 5 appearances in 20 draws = hot

            # Adjust based on cycle position
            cycle_position = days_absent / avg_cycle if avg_cycle > 0 else 1

            # Cold if overdue, hot if recently appeared
            if cycle_position > 1.2:  # Overdue
                cycle_heat = min(1.0, (cycle_position - 1) * 0.5)
            elif days_absent <= 3:  # Very recent
                cycle_heat = 0.8
            else:
                cycle_heat = max(0.1, 1 - cycle_position)

            # Combine heats
            final_heat = (recent_heat * 0.4) + (cycle_heat * 0.6)

            return round(final_heat, 3)

        except Exception as e:
            return 0.5

    def _calculate_prediction_weight(
        self,
        days_absent: int,
        avg_cycle: float,
        cycle_variance: float,
        heat_level: float,
        cycle_count: int,
    ) -> float:
        """Tính trọng số dự đoán cho số"""
        try:
            # Base weight from cycle analysis
            if avg_cycle > 0:
                cycle_ratio = days_absent / avg_cycle

                # Peak weight when close to expected return
                if 0.8 <= cycle_ratio <= 1.3:
                    cycle_weight = 1.0 - abs(cycle_ratio - 1.0) * 0.5
                elif cycle_ratio > 1.3:  # Overdue bonus
                    cycle_weight = min(1.0, 0.7 + (cycle_ratio - 1.3) * 0.3)
                else:
                    cycle_weight = cycle_ratio * 0.6
            else:
                cycle_weight = 0.5

            # Consistency bonus (lower variance = higher bonus)
            if cycle_count > 2:
                consistency_bonus = max(0, 1 - (cycle_variance / (avg_cycle**2)))
            else:
                consistency_bonus = 0.5

            # Heat level adjustment
            heat_adjustment = heat_level * 0.3

            # Experience bonus (more cycles = more reliable)
            experience_bonus = min(0.3, cycle_count * 0.05)

            # Combine weights
            final_weight = (
                (cycle_weight * 0.5)
                + (consistency_bonus * 0.2)
                + (heat_adjustment * 0.2)
                + (experience_bonus * 0.1)
            )

            return round(min(1.0, final_weight), 3)

        except Exception as e:
            return 0.5

    def _calculate_number_confidence(
        self,
        cycles: List[int],
        days_absent: int,
        avg_cycle: float,
        cycle_variance: float,
    ) -> float:
        """Tính confidence cho một số"""
        try:
            # Base confidence from cycle consistency
            if len(cycles) > 1 and avg_cycle > 0:
                consistency = 1 - min(1, cycle_variance / (avg_cycle**2))
                base_confidence = 0.4 + consistency * 0.4
            else:
                base_confidence = 0.5

            # Cycle count bonus
            count_bonus = min(0.2, len(cycles) * 0.02)

            # Timing bonus (close to expected return)
            if avg_cycle > 0:
                cycle_ratio = days_absent / avg_cycle
                if 0.9 <= cycle_ratio <= 1.1:
                    timing_bonus = 0.1
                elif 0.8 <= cycle_ratio <= 1.3:
                    timing_bonus = 0.05
                else:
                    timing_bonus = 0
            else:
                timing_bonus = 0

            final_confidence = base_confidence + count_bonus + timing_bonus
            return round(min(0.95, final_confidence), 3)

        except Exception as e:
            return 0.6

    def _generate_heat_map(self, cau_chay_data: List[CauChayData]) -> Dict[int, float]:
        """Tạo heat map cho tất cả các số"""
        heat_map = {}

        try:
            for data in cau_chay_data:
                heat_map[data.number] = data.heat_level

            # Fill missing numbers with neutral heat
            for number in range(100):
                if number not in heat_map:
                    heat_map[number] = 0.5

            return heat_map

        except Exception as e:
            logger.error(f"❌ Error generating heat map: {str(e)}")
            return {i: 0.5 for i in range(100)}

    def _select_predictions(
        self, cau_chay_data: List[CauChayData], heat_map: Dict[int, float]
    ) -> List[int]:
        """Chọn số dự đoán dựa trên phân tích"""
        try:
            # Score each number
            scored_numbers = []

            for data in cau_chay_data:
                # Combine multiple factors
                cycle_score = data.prediction_weight
                confidence_score = data.confidence
                heat_score = data.heat_level

                # Pattern bonuses
                pattern_bonus = 0
                if data.pattern_type == CauChayPattern.BREAKING:
                    pattern_bonus = 0.15  # Breaking patterns get bonus
                elif data.pattern_type == CauChayPattern.OSCILLATING:
                    pattern_bonus = 0.1
                elif data.pattern_type == CauChayPattern.DESCENDING:
                    pattern_bonus = 0.05

                # Overdue bonus
                overdue_bonus = 0
                if data.days_absent > data.cycle_length * 1.2:
                    overdue_bonus = min(
                        0.2, (data.days_absent / data.cycle_length - 1.2) * 0.1
                    )

                # Calculate final score
                final_score = (
                    (cycle_score * 0.4)
                    + (confidence_score * 0.3)
                    + (heat_score * 0.2)
                    + pattern_bonus
                    + overdue_bonus
                )

                scored_numbers.append((data.number, final_score, data))

            # Sort by score
            scored_numbers.sort(key=lambda x: x[1], reverse=True)

            # Select top numbers with diversity
            selected_numbers = []

            # Always include top scorers
            for number, score, data in scored_numbers[:5]:
                selected_numbers.append(number)

            # Add numbers with specific patterns
            pattern_targets = {
                CauChayPattern.BREAKING: 3,
                CauChayPattern.OSCILLATING: 2,
                CauChayPattern.DESCENDING: 2,
            }

            for number, score, data in scored_numbers[5:]:
                if len(selected_numbers) >= 15:
                    break

                if data.pattern_type in pattern_targets:
                    if pattern_targets[data.pattern_type] > 0:
                        selected_numbers.append(number)
                        pattern_targets[data.pattern_type] -= 1

            # Fill remaining slots with highest scorers
            for number, score, data in scored_numbers:
                if len(selected_numbers) >= 12:  # Target 10-12 numbers
                    break
                if number not in selected_numbers:
                    selected_numbers.append(number)

            logger.info(
                f"🎯 Selected {len(selected_numbers)} numbers from Cau Chay analysis"
            )
            return selected_numbers

        except Exception as e:
            logger.error(f"❌ Error selecting predictions: {str(e)}")
            return []

    def _calculate_overall_confidence(
        self, cau_chay_data: List[CauChayData], numbers: List[int]
    ) -> float:
        """Tính confidence tổng thể"""
        try:
            if not numbers or not cau_chay_data:
                return 0.5

            # Get confidence scores for selected numbers
            selected_data = [data for data in cau_chay_data if data.number in numbers]

            if not selected_data:
                return 0.5

            # Calculate weighted average confidence
            total_weight = sum(data.prediction_weight for data in selected_data)
            if total_weight > 0:
                weighted_confidence = (
                    sum(
                        data.confidence * data.prediction_weight
                        for data in selected_data
                    )
                    / total_weight
                )
            else:
                weighted_confidence = np.mean(
                    [data.confidence for data in selected_data]
                )

            # Pattern diversity bonus
            pattern_types = set(data.pattern_type for data in selected_data)
            diversity_bonus = min(0.1, len(pattern_types) * 0.02)

            # Heat balance bonus
            heat_levels = [data.heat_level for data in selected_data]
            heat_balance = 1 - np.std(heat_levels) if len(heat_levels) > 1 else 0.5
            balance_bonus = heat_balance * 0.05

            final_confidence = weighted_confidence + diversity_bonus + balance_bonus
            return round(min(0.95, final_confidence), 3)

        except Exception as e:
            logger.error(f"❌ Error calculating overall confidence: {str(e)}")
            return 0.6

    def _generate_analysis_details(
        self, cau_chay_data: List[CauChayData], heat_map: Dict[int, float]
    ) -> Dict:
        """Tạo chi tiết phân tích"""
        try:
            # Pattern distribution
            pattern_distribution = {}
            for pattern in CauChayPattern:
                count = sum(1 for data in cau_chay_data if data.pattern_type == pattern)
                pattern_distribution[pattern.value] = count

            # Heat level statistics
            heat_levels = list(heat_map.values())
            heat_stats = {
                "hot_numbers": sum(
                    1 for h in heat_levels if h >= self.heat_threshold_hot
                ),
                "cold_numbers": sum(
                    1 for h in heat_levels if h <= self.heat_threshold_cold
                ),
                "avg_heat": np.mean(heat_levels),
                "heat_variance": np.var(heat_levels),
            }

            # Top patterns
            top_patterns = []
            sorted_data = sorted(
                cau_chay_data, key=lambda x: x.prediction_weight, reverse=True
            )
            for data in sorted_data[:10]:
                top_patterns.append(
                    {
                        "number": data.number,
                        "pattern": data.pattern_type.value,
                        "days_absent": data.days_absent,
                        "cycle_length": data.cycle_length,
                        "heat_level": data.heat_level,
                        "weight": data.prediction_weight,
                    }
                )

            return {
                "total_numbers_analyzed": len(cau_chay_data),
                "pattern_distribution": pattern_distribution,
                "heat_statistics": heat_stats,
                "top_patterns": top_patterns,
                "analysis_window_days": self.analysis_window,
                "method_version": self.version,
                "avg_cycle_length": (
                    np.mean([data.cycle_length for data in cau_chay_data])
                    if cau_chay_data
                    else 0
                ),
                "confidence_threshold": self.confidence_threshold,
            }

        except Exception as e:
            logger.error(f"❌ Error generating analysis details: {str(e)}")
            return {"error": str(e)}

    def _create_fallback_result(self, start_time: datetime) -> CauChayAnalysisResult:
        """Tạo kết quả dự phòng"""
        return CauChayAnalysisResult(
            numbers=list(range(20, 30)),
            confidence=0.5,
            cau_chay_data=[],
            analysis_details={"error": "Fallback result"},
            method_weight=self.method_weight,
            processing_time=(datetime.now() - start_time).total_seconds(),
            timestamp=timezone.now(),
            heat_map={i: 0.5 for i in range(100)},
        )

    def get_cycle_info(
        self, number: int, region: str, date: datetime
    ) -> Optional[Dict]:
        """Lấy thông tin chu kỳ chi tiết cho một số"""
        try:
            historical_data = self._get_historical_data(region, date)
            data = self._analyze_single_number(number, historical_data, date)

            if not data:
                return None

            return {
                "number": data.number,
                "last_appearance": data.last_appearance.strftime("%Y-%m-%d"),
                "days_absent": data.days_absent,
                "average_cycle": data.cycle_length,
                "pattern_type": data.pattern_type.value,
                "heat_level": data.heat_level,
                "confidence": data.confidence,
                "historical_cycles": data.historical_cycles,
                "prediction_weight": data.prediction_weight,
            }

        except Exception as e:
            logger.error(f"❌ Error getting cycle info for number {number}: {str(e)}")
            return None

    def get_api_info(self) -> Dict:
        """Trả về thông tin API"""
        return {
            "name": self.name,
            "version": self.version,
            "method_weight": self.method_weight,
            "endpoints": {
                "analyze": "Phân tích Cầu Chảy patterns",
                "get_cycle_info": "Lấy thông tin chu kỳ cho số cụ thể",
                "generate_heat_map": "Tạo heat map nóng/lạnh",
            },
            "supported_regions": ["MB", "MT", "MN"],
            "pattern_types": [pattern.value for pattern in CauChayPattern],
            "cau_chay_types": [ctype.value for ctype in CauChayType],
            "analysis_window": self.analysis_window,
            "cache_timeout": self.cache_timeout,
        }


# Export main class
__all__ = [
    "CauChayCycleAnalyzer",
    "CauChayAnalysisResult",
    "CauChayData",
    "CauChayPattern",
    "CauChayType",
]

if __name__ == "__main__":
    # Quick test
    analyzer = CauChayCycleAnalyzer()
    print(f"🌊 {analyzer.name} v{analyzer.version} - Ready for Phase 4!")
    print(f"📊 Method weight: {analyzer.method_weight}")
    print(f"🎯 Pattern types: {len(CauChayPattern)} types")
    print(
        f"🔥 Heat thresholds: Hot={analyzer.heat_threshold_hot}, Cold={analyzer.heat_threshold_cold}"
    )
    print(f"⚡ Analysis window: {analyzer.analysis_window} days")
