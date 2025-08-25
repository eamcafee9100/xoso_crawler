"""
PHASE 4 - BAC NHO PATTERN ENGINE
===============================
Advanced Bạc Nhớ analysis with pattern recognition and historical cycle tracking.
Integrates with Phase 3 architecture for ensemble predictions.

Author: Phase 4 Development Team
Created: January 2025
Version: 4.0.0
"""

import json
import logging
from collections import Counter, defaultdict
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


class BacNhoPatternType(Enum):
    """Các loại pattern trong Bạc Nhớ"""

    SEQUENCE_PATTERN = "sequence_pattern"
    CYCLE_PATTERN = "cycle_pattern"
    FREQUENCY_PATTERN = "frequency_pattern"
    POSITION_PATTERN = "position_pattern"
    COMBINATION_PATTERN = "combination_pattern"


@dataclass
class BacNhoPattern:
    """Data class để lưu trữ thông tin pattern Bạc Nhớ"""

    pattern_type: BacNhoPatternType
    pattern_data: Dict
    confidence: float
    frequency: int
    last_occurrence: datetime
    expected_next: Optional[datetime]
    strength: float
    numbers: List[int]


@dataclass
class BacNhoAnalysisResult:
    """Kết quả phân tích Bạc Nhớ"""

    numbers: List[int]
    confidence: float
    patterns_found: List[BacNhoPattern]
    analysis_details: Dict
    method_weight: float
    processing_time: float
    timestamp: datetime


class BacNhoPatternEngine:
    """
    Engine phân tích Bạc Nhớ với các thuật toán pattern recognition tiên tiến
    """

    def __init__(self):
        self.name = "Bac Nho Pattern Engine"
        self.version = "4.0.0"
        self.method_weight = 0.15  # 15% weight trong ensemble
        self.cache_timeout = 300  # 5 minutes cache

        # Pattern configuration
        self.min_pattern_length = 3
        self.max_pattern_length = 10
        self.min_confidence_threshold = 0.6
        self.pattern_lookback_days = 90

        # Analysis parameters
        self.sequence_analysis_depth = 50
        self.cycle_detection_window = 30
        self.frequency_analysis_window = 100

        logger.info(f"🧮 {self.name} v{self.version} initialized")

    def analyze(
        self, region: str, date: datetime, historical_data: Optional[List] = None
    ) -> BacNhoAnalysisResult:
        """
        Phân tích Bạc Nhớ cho region và date cụ thể

        Args:
            region: Tên miền (MB, MT, MN)
            date: Ngày cần dự đoán
            historical_data: Dữ liệu lịch sử (optional)

        Returns:
            BacNhoAnalysisResult: Kết quả phân tích đầy đủ
        """
        start_time = datetime.now()

        try:
            # Generate cache key
            cache_key = f"bac_nho_analysis_{region}_{date.strftime('%Y%m%d')}"
            cached_result = cache.get(cache_key)

            if cached_result:
                logger.info(f"🎯 Cache hit for Bac Nho analysis: {cache_key}")
                return BacNhoAnalysisResult(**cached_result)

            # Get historical data
            if not historical_data:
                historical_data = self._get_historical_data(region, date)

            # Perform comprehensive analysis
            patterns = self._detect_patterns(historical_data, region, date)
            numbers = self._generate_predictions(patterns, historical_data)
            confidence = self._calculate_confidence(patterns, numbers)
            analysis_details = self._generate_analysis_details(
                patterns, historical_data
            )

            # Create result
            result = BacNhoAnalysisResult(
                numbers=numbers,
                confidence=confidence,
                patterns_found=patterns,
                analysis_details=analysis_details,
                method_weight=self.method_weight,
                processing_time=(datetime.now() - start_time).total_seconds(),
                timestamp=timezone.now(),
            )

            # Cache result
            cache.set(cache_key, result.__dict__, self.cache_timeout)

            logger.info(
                f"🧮 Bac Nho analysis completed: {len(numbers)} numbers, "
                f"confidence {confidence:.2f}, {len(patterns)} patterns"
            )

            return result

        except Exception as e:
            logger.error(f"❌ Error in Bac Nho analysis: {str(e)}")
            return self._create_fallback_result(start_time)

    def _get_historical_data(self, region: str, date: datetime) -> List[Dict]:
        """Lấy dữ liệu lịch sử để phân tích"""
        try:
            end_date = date - timedelta(days=1)
            start_date = end_date - timedelta(days=self.pattern_lookback_days)

            queryset = KetQuaXoSo.objects.filter(
                ngay__range=[start_date, end_date], mien__icontains=region
            ).order_by("-ngay")

            historical_data = []
            for record in queryset:
                # Extract all numbers from the record
                numbers = self._extract_all_numbers(record)
                historical_data.append(
                    {
                        "date": record.ngay,
                        "numbers": numbers,
                        "giai_dac_biet": record.giai_dac_biet,
                        "giai_nhat": record.giai_nhat,
                        "giai_nhi": record.giai_nhi,
                        "region": region,
                    }
                )

            logger.info(
                f"📊 Retrieved {len(historical_data)} historical records for Bac Nho analysis"
            )
            return historical_data

        except Exception as e:
            logger.error(f"❌ Error getting historical data: {str(e)}")
            return []

    def _extract_all_numbers(self, record) -> List[int]:
        """Trích xuất tất cả số từ kết quả xổ số"""
        numbers = []

        # Extract from all prize levels
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
                # Handle both single numbers and comma-separated lists
                if isinstance(value, str):
                    parts = value.replace(" ", "").split(",")
                    for part in parts:
                        if part.isdigit():
                            numbers.append(int(part) % 100)  # Get last 2 digits
                elif isinstance(value, int):
                    numbers.append(value % 100)

        return list(set(numbers))  # Remove duplicates

    def _detect_patterns(
        self, historical_data: List[Dict], region: str, target_date: datetime
    ) -> List[BacNhoPattern]:
        """Phát hiện các patterns trong dữ liệu lịch sử"""
        patterns = []

        try:
            # 1. Sequence Patterns - Phát hiện chuỗi số liên tiếp
            sequence_patterns = self._detect_sequence_patterns(historical_data)
            patterns.extend(sequence_patterns)

            # 2. Cycle Patterns - Phát hiện chu kỳ xuất hiện
            cycle_patterns = self._detect_cycle_patterns(historical_data, target_date)
            patterns.extend(cycle_patterns)

            # 3. Frequency Patterns - Phân tích tần suất xuất hiện
            frequency_patterns = self._detect_frequency_patterns(historical_data)
            patterns.extend(frequency_patterns)

            # 4. Position Patterns - Phân tích vị trí xuất hiện
            position_patterns = self._detect_position_patterns(historical_data)
            patterns.extend(position_patterns)

            # 5. Combination Patterns - Phát hiện kết hợp số
            combination_patterns = self._detect_combination_patterns(historical_data)
            patterns.extend(combination_patterns)

            # Filter patterns by confidence
            patterns = [
                p for p in patterns if p.confidence >= self.min_confidence_threshold
            ]

            # Sort by confidence and strength
            patterns.sort(key=lambda x: (x.confidence * x.strength), reverse=True)

            logger.info(f"🔍 Detected {len(patterns)} high-confidence Bac Nho patterns")
            return patterns

        except Exception as e:
            logger.error(f"❌ Error detecting patterns: {str(e)}")
            return []

    def _detect_sequence_patterns(
        self, historical_data: List[Dict]
    ) -> List[BacNhoPattern]:
        """Phát hiện patterns chuỗi số liên tiếp"""
        patterns = []

        try:
            # Analyze recent sequences
            recent_data = historical_data[: self.sequence_analysis_depth]

            for i in range(len(recent_data) - self.min_pattern_length + 1):
                window_data = recent_data[i : i + self.min_pattern_length]

                # Extract number sequences
                sequences = []
                for record in window_data:
                    sequences.extend(record["numbers"])

                # Find sequential patterns
                for seq_len in range(
                    self.min_pattern_length,
                    min(len(sequences), self.max_pattern_length) + 1,
                ):
                    for start_idx in range(len(sequences) - seq_len + 1):
                        sequence = sequences[start_idx : start_idx + seq_len]

                        # Check if it's a meaningful sequence
                        if self._is_meaningful_sequence(sequence):
                            confidence = self._calculate_sequence_confidence(
                                sequence, historical_data
                            )

                            if confidence >= self.min_confidence_threshold:
                                pattern = BacNhoPattern(
                                    pattern_type=BacNhoPatternType.SEQUENCE_PATTERN,
                                    pattern_data={
                                        "sequence": sequence,
                                        "length": seq_len,
                                    },
                                    confidence=confidence,
                                    frequency=self._count_sequence_frequency(
                                        sequence, historical_data
                                    ),
                                    last_occurrence=window_data[0]["date"],
                                    expected_next=None,
                                    strength=confidence * 0.8,
                                    numbers=self._predict_next_in_sequence(sequence),
                                )
                                patterns.append(pattern)

            return patterns[:10]  # Return top 10 sequence patterns

        except Exception as e:
            logger.error(f"❌ Error detecting sequence patterns: {str(e)}")
            return []

    def _detect_cycle_patterns(
        self, historical_data: List[Dict], target_date: datetime
    ) -> List[BacNhoPattern]:
        """Phát hiện patterns chu kỳ"""
        patterns = []

        try:
            # Group data by number and find cycles
            number_occurrences = defaultdict(list)

            for record in historical_data:
                for number in record["numbers"]:
                    number_occurrences[number].append(record["date"])

            # Analyze cycles for each number
            for number, dates in number_occurrences.items():
                if len(dates) >= 3:  # Need at least 3 occurrences for cycle analysis
                    cycles = self._find_cycles_in_dates(dates)

                    for cycle in cycles:
                        if cycle["confidence"] >= self.min_confidence_threshold:
                            expected_next = self._calculate_next_cycle_date(
                                dates, cycle["period"], target_date
                            )

                            pattern = BacNhoPattern(
                                pattern_type=BacNhoPatternType.CYCLE_PATTERN,
                                pattern_data={
                                    "number": number,
                                    "cycle_period": cycle["period"],
                                    "cycle_type": cycle["type"],
                                },
                                confidence=cycle["confidence"],
                                frequency=len(dates),
                                last_occurrence=max(dates),
                                expected_next=expected_next,
                                strength=cycle["confidence"] * 0.9,
                                numbers=[number],
                            )
                            patterns.append(pattern)

            return patterns[:15]  # Return top 15 cycle patterns

        except Exception as e:
            logger.error(f"❌ Error detecting cycle patterns: {str(e)}")
            return []

    def _detect_frequency_patterns(
        self, historical_data: List[Dict]
    ) -> List[BacNhoPattern]:
        """Phát hiện patterns tần suất"""
        patterns = []

        try:
            # Count frequency of each number
            number_counts = Counter()
            total_draws = len(historical_data)

            for record in historical_data:
                for number in record["numbers"]:
                    number_counts[number] += 1

            # Calculate frequency statistics
            frequencies = {}
            for number, count in number_counts.items():
                frequencies[number] = {
                    "count": count,
                    "frequency": count / total_draws,
                    "expected_frequency": 1 / 100,  # Assuming 100 possible numbers
                    "deviation": (count / total_draws) - (1 / 100),
                }

            # Find significant frequency patterns
            for number, stats in frequencies.items():
                # Hot numbers (appearing more frequently)
                if stats["deviation"] > 0.01 and stats["count"] >= 5:
                    confidence = min(0.95, 0.6 + stats["deviation"] * 10)

                    pattern = BacNhoPattern(
                        pattern_type=BacNhoPatternType.FREQUENCY_PATTERN,
                        pattern_data={
                            "number": number,
                            "frequency_type": "hot",
                            "frequency": stats["frequency"],
                            "deviation": stats["deviation"],
                        },
                        confidence=confidence,
                        frequency=stats["count"],
                        last_occurrence=self._get_last_occurrence(
                            number, historical_data
                        ),
                        expected_next=None,
                        strength=confidence * 0.7,
                        numbers=[number],
                    )
                    patterns.append(pattern)

                # Due numbers (haven't appeared recently)
                elif stats["count"] > 0:
                    last_occurrence = self._get_last_occurrence(number, historical_data)
                    days_since = (timezone.now().date() - last_occurrence).days

                    if days_since > 14:  # Haven't appeared in 2 weeks
                        confidence = min(0.9, 0.5 + (days_since - 14) / 30)

                        pattern = BacNhoPattern(
                            pattern_type=BacNhoPatternType.FREQUENCY_PATTERN,
                            pattern_data={
                                "number": number,
                                "frequency_type": "due",
                                "days_since": days_since,
                                "frequency": stats["frequency"],
                            },
                            confidence=confidence,
                            frequency=stats["count"],
                            last_occurrence=last_occurrence,
                            expected_next=None,
                            strength=confidence * 0.6,
                            numbers=[number],
                        )
                        patterns.append(pattern)

            return patterns[:20]  # Return top 20 frequency patterns

        except Exception as e:
            logger.error(f"❌ Error detecting frequency patterns: {str(e)}")
            return []

    def _detect_position_patterns(
        self, historical_data: List[Dict]
    ) -> List[BacNhoPattern]:
        """Phát hiện patterns vị trí xuất hiện"""
        patterns = []

        try:
            # Analyze position preferences for numbers
            position_analysis = {}

            for record in historical_data:
                # Analyze different prize positions
                positions = {
                    "special": (
                        [record.get("giai_dac_biet", 0) % 100]
                        if record.get("giai_dac_biet")
                        else []
                    ),
                    "first": [
                        int(x) % 100
                        for x in str(record.get("giai_nhat", "")).split(",")
                        if x.isdigit()
                    ],
                    "second": [
                        int(x) % 100
                        for x in str(record.get("giai_nhi", "")).split(",")
                        if x.isdigit()
                    ],
                    "others": [],
                }

                # Extract numbers from other prizes
                other_fields = [
                    "giai_ba",
                    "giai_tu",
                    "giai_nam",
                    "giai_sau",
                    "giai_bay",
                ]
                for field in other_fields:
                    value = record.get(field, "")
                    if value:
                        positions["others"].extend(
                            [int(x) % 100 for x in str(value).split(",") if x.isdigit()]
                        )

                # Record position preferences
                for position_type, numbers in positions.items():
                    for number in numbers:
                        if number not in position_analysis:
                            position_analysis[number] = defaultdict(int)
                        position_analysis[number][position_type] += 1

            # Find significant position patterns
            for number, position_counts in position_analysis.items():
                total_appearances = sum(position_counts.values())

                if total_appearances >= 3:
                    for position, count in position_counts.items():
                        position_preference = count / total_appearances

                        if position_preference >= 0.4:  # Strong position preference
                            confidence = min(0.9, 0.6 + position_preference * 0.3)

                            pattern = BacNhoPattern(
                                pattern_type=BacNhoPatternType.POSITION_PATTERN,
                                pattern_data={
                                    "number": number,
                                    "preferred_position": position,
                                    "position_preference": position_preference,
                                    "total_appearances": total_appearances,
                                },
                                confidence=confidence,
                                frequency=count,
                                last_occurrence=self._get_last_occurrence(
                                    number, historical_data
                                ),
                                expected_next=None,
                                strength=confidence * 0.75,
                                numbers=[number],
                            )
                            patterns.append(pattern)

            return patterns[:12]  # Return top 12 position patterns

        except Exception as e:
            logger.error(f"❌ Error detecting position patterns: {str(e)}")
            return []

    def _detect_combination_patterns(
        self, historical_data: List[Dict]
    ) -> List[BacNhoPattern]:
        """Phát hiện patterns kết hợp số"""
        patterns = []

        try:
            # Analyze number combinations
            pair_counts = Counter()
            triple_counts = Counter()

            for record in historical_data:
                numbers = sorted(record["numbers"])

                # Analyze pairs
                for i in range(len(numbers)):
                    for j in range(i + 1, len(numbers)):
                        pair = (numbers[i], numbers[j])
                        pair_counts[pair] += 1

                # Analyze triples
                for i in range(len(numbers)):
                    for j in range(i + 1, len(numbers)):
                        for k in range(j + 1, len(numbers)):
                            triple = (numbers[i], numbers[j], numbers[k])
                            triple_counts[triple] += 1

            # Find significant pair patterns
            total_records = len(historical_data)
            for pair, count in pair_counts.items():
                frequency = count / total_records

                if (
                    count >= 3 and frequency > 0.03
                ):  # Appeared at least 3 times and > 3% frequency
                    confidence = min(0.85, 0.5 + frequency * 5)

                    pattern = BacNhoPattern(
                        pattern_type=BacNhoPatternType.COMBINATION_PATTERN,
                        pattern_data={
                            "combination_type": "pair",
                            "combination": list(pair),
                            "frequency": frequency,
                        },
                        confidence=confidence,
                        frequency=count,
                        last_occurrence=self._get_combination_last_occurrence(
                            pair, historical_data
                        ),
                        expected_next=None,
                        strength=confidence * 0.8,
                        numbers=list(pair),
                    )
                    patterns.append(pattern)

            # Find significant triple patterns
            for triple, count in triple_counts.items():
                frequency = count / total_records

                if (
                    count >= 2 and frequency > 0.02
                ):  # Appeared at least 2 times and > 2% frequency
                    confidence = min(0.8, 0.5 + frequency * 8)

                    pattern = BacNhoPattern(
                        pattern_type=BacNhoPatternType.COMBINATION_PATTERN,
                        pattern_data={
                            "combination_type": "triple",
                            "combination": list(triple),
                            "frequency": frequency,
                        },
                        confidence=confidence,
                        frequency=count,
                        last_occurrence=self._get_combination_last_occurrence(
                            triple, historical_data
                        ),
                        expected_next=None,
                        strength=confidence * 0.85,
                        numbers=list(triple),
                    )
                    patterns.append(pattern)

            return patterns[:10]  # Return top 10 combination patterns

        except Exception as e:
            logger.error(f"❌ Error detecting combination patterns: {str(e)}")
            return []

    def _generate_predictions(
        self, patterns: List[BacNhoPattern], historical_data: List[Dict]
    ) -> List[int]:
        """Tạo dự đoán dựa trên patterns"""
        try:
            # Collect numbers from all patterns with weighted scoring
            number_scores = defaultdict(float)

            for pattern in patterns:
                weight = pattern.confidence * pattern.strength
                for number in pattern.numbers:
                    number_scores[number] += weight

            # Add frequency-based adjustments
            recent_data = historical_data[:10]  # Last 10 draws
            recent_numbers = []
            for record in recent_data:
                recent_numbers.extend(record["numbers"])

            recent_counter = Counter(recent_numbers)

            # Adjust scores based on recent frequency
            for number, score in number_scores.items():
                recent_freq = recent_counter.get(number, 0)

                # Boost numbers that haven't appeared recently (due numbers)
                if recent_freq == 0:
                    number_scores[number] *= 1.2
                elif recent_freq == 1:
                    number_scores[number] *= 1.1
                elif recent_freq >= 3:
                    number_scores[number] *= 0.8  # Reduce hot numbers slightly

            # Sort by score and select top numbers
            sorted_numbers = sorted(
                number_scores.items(), key=lambda x: x[1], reverse=True
            )

            # Select top 8-12 numbers for final prediction
            prediction_count = min(12, max(8, len(sorted_numbers) // 3))
            predictions = [num for num, score in sorted_numbers[:prediction_count]]

            # Ensure we have valid predictions
            if not predictions:
                # Fallback: select most frequent numbers from recent history
                all_numbers = []
                for record in historical_data[:20]:
                    all_numbers.extend(record["numbers"])

                counter = Counter(all_numbers)
                predictions = [num for num, count in counter.most_common(10)]

            logger.info(f"🎯 Generated {len(predictions)} Bac Nho predictions")
            return predictions

        except Exception as e:
            logger.error(f"❌ Error generating predictions: {str(e)}")
            return []

    def _calculate_confidence(
        self, patterns: List[BacNhoPattern], numbers: List[int]
    ) -> float:
        """Tính toán confidence tổng thể"""
        try:
            if not patterns or not numbers:
                return 0.5

            # Base confidence from patterns
            pattern_confidences = [p.confidence * p.strength for p in patterns]
            avg_pattern_confidence = (
                np.mean(pattern_confidences) if pattern_confidences else 0.5
            )

            # Pattern diversity bonus
            pattern_types = set(p.pattern_type for p in patterns)
            diversity_bonus = min(0.1, len(pattern_types) * 0.02)

            # Pattern count bonus
            count_bonus = min(0.1, len(patterns) * 0.005)

            # Calculate final confidence
            final_confidence = min(
                0.95, avg_pattern_confidence + diversity_bonus + count_bonus
            )

            return round(final_confidence, 3)

        except Exception as e:
            logger.error(f"❌ Error calculating confidence: {str(e)}")
            return 0.6

    def _generate_analysis_details(
        self, patterns: List[BacNhoPattern], historical_data: List[Dict]
    ) -> Dict:
        """Tạo chi tiết phân tích"""
        try:
            pattern_summary = {}
            for pattern_type in BacNhoPatternType:
                type_patterns = [p for p in patterns if p.pattern_type == pattern_type]
                pattern_summary[pattern_type.value] = {
                    "count": len(type_patterns),
                    "avg_confidence": (
                        np.mean([p.confidence for p in type_patterns])
                        if type_patterns
                        else 0
                    ),
                    "patterns": [
                        p.pattern_data for p in type_patterns[:3]
                    ],  # Top 3 patterns
                }

            return {
                "total_patterns": len(patterns),
                "pattern_summary": pattern_summary,
                "historical_data_points": len(historical_data),
                "analysis_method": "Advanced Bac Nho Pattern Recognition",
                "pattern_types_detected": len(set(p.pattern_type for p in patterns)),
                "strongest_pattern": patterns[0].pattern_data if patterns else None,
                "method_version": self.version,
            }

        except Exception as e:
            logger.error(f"❌ Error generating analysis details: {str(e)}")
            return {"error": str(e)}

    # Helper methods
    def _is_meaningful_sequence(self, sequence: List[int]) -> bool:
        """Kiểm tra xem sequence có ý nghĩa không"""
        if len(sequence) < 2:
            return False

        # Check for arithmetic progression
        diffs = [sequence[i + 1] - sequence[i] for i in range(len(sequence) - 1)]
        return len(set(diffs)) <= 2  # Allow some variation

    def _calculate_sequence_confidence(
        self, sequence: List[int], historical_data: List[Dict]
    ) -> float:
        """Tính confidence cho sequence pattern"""
        try:
            appearances = self._count_sequence_frequency(sequence, historical_data)
            total_possible = len(historical_data) - len(sequence) + 1

            if total_possible <= 0:
                return 0.5

            frequency = appearances / total_possible
            confidence = min(0.9, 0.4 + frequency * 2)

            return confidence

        except Exception as e:
            return 0.5

    def _count_sequence_frequency(
        self, sequence: List[int], historical_data: List[Dict]
    ) -> int:
        """Đếm tần suất xuất hiện của sequence"""
        count = 0

        try:
            for record in historical_data:
                numbers = record["numbers"]

                # Check if sequence appears in this record
                for i in range(len(numbers) - len(sequence) + 1):
                    if numbers[i : i + len(sequence)] == sequence:
                        count += 1
                        break

            return count

        except Exception as e:
            return 0

    def _predict_next_in_sequence(self, sequence: List[int]) -> List[int]:
        """Dự đoán số tiếp theo trong sequence"""
        try:
            if len(sequence) < 2:
                return sequence

            # Calculate differences
            diffs = [sequence[i + 1] - sequence[i] for i in range(len(sequence) - 1)]

            # Predict next difference (simple: use last difference)
            next_diff = diffs[-1] if diffs else 1
            next_number = (sequence[-1] + next_diff) % 100

            return sequence + [next_number]

        except Exception as e:
            return sequence

    def _find_cycles_in_dates(self, dates: List[datetime]) -> List[Dict]:
        """Tìm chu kỳ trong danh sách dates"""
        cycles = []

        try:
            if len(dates) < 3:
                return cycles

            # Sort dates
            sorted_dates = sorted(dates, reverse=True)

            # Calculate intervals between consecutive dates
            intervals = []
            for i in range(len(sorted_dates) - 1):
                interval = (sorted_dates[i] - sorted_dates[i + 1]).days
                intervals.append(interval)

            if not intervals:
                return cycles

            # Find common intervals (cycles)
            interval_counter = Counter(intervals)

            for interval, count in interval_counter.items():
                if count >= 2 and 3 <= interval <= 30:  # Reasonable cycle length
                    confidence = min(0.9, 0.5 + (count / len(intervals)) * 0.5)

                    cycles.append(
                        {
                            "period": interval,
                            "type": "regular",
                            "confidence": confidence,
                            "occurrences": count,
                        }
                    )

            return cycles

        except Exception as e:
            return []

    def _calculate_next_cycle_date(
        self, dates: List[datetime], period: int, target_date: datetime
    ) -> Optional[datetime]:
        """Tính toán ngày tiếp theo trong chu kỳ"""
        try:
            if not dates:
                return None

            last_date = max(dates)
            days_since = (target_date.date() - last_date).days

            # Calculate next expected occurrence
            cycles_passed = days_since // period
            next_occurrence = last_date + timedelta(days=(cycles_passed + 1) * period)

            return next_occurrence

        except Exception as e:
            return None

    def _get_last_occurrence(
        self, number: int, historical_data: List[Dict]
    ) -> datetime:
        """Lấy lần xuất hiện cuối cùng của một số"""
        try:
            for record in historical_data:
                if number in record["numbers"]:
                    return record["date"]

            # If not found, return a date far in the past
            return datetime.now().date() - timedelta(days=365)

        except Exception as e:
            return datetime.now().date() - timedelta(days=365)

    def _get_combination_last_occurrence(
        self, combination: tuple, historical_data: List[Dict]
    ) -> datetime:
        """Lấy lần xuất hiện cuối cùng của một combination"""
        try:
            for record in historical_data:
                if all(num in record["numbers"] for num in combination):
                    return record["date"]

            return datetime.now().date() - timedelta(days=365)

        except Exception as e:
            return datetime.now().date() - timedelta(days=365)

    def _create_fallback_result(self, start_time: datetime) -> BacNhoAnalysisResult:
        """Tạo kết quả dự phòng khi có lỗi"""
        return BacNhoAnalysisResult(
            numbers=list(range(10, 20)),  # Simple fallback numbers
            confidence=0.5,
            patterns_found=[],
            analysis_details={"error": "Fallback result due to analysis error"},
            method_weight=self.method_weight,
            processing_time=(datetime.now() - start_time).total_seconds(),
            timestamp=timezone.now(),
        )

    def get_api_info(self) -> Dict:
        """Trả về thông tin API cho integration"""
        return {
            "name": self.name,
            "version": self.version,
            "method_weight": self.method_weight,
            "endpoints": {
                "analyze": "Phân tích Bạc Nhớ patterns",
                "get_patterns": "Lấy danh sách patterns đã phát hiện",
                "get_confidence": "Tính toán confidence score",
            },
            "supported_regions": ["MB", "MT", "MN"],
            "pattern_types": [ptype.value for ptype in BacNhoPatternType],
            "cache_timeout": self.cache_timeout,
            "min_confidence": self.min_confidence_threshold,
        }


# Export main class
__all__ = [
    "BacNhoPatternEngine",
    "BacNhoAnalysisResult",
    "BacNhoPattern",
    "BacNhoPatternType",
]

if __name__ == "__main__":
    # Quick test
    engine = BacNhoPatternEngine()
    print(f"🧮 {engine.name} v{engine.version} - Ready for Phase 4!")
    print(f"📊 Method weight: {engine.method_weight}")
    print(f"🎯 Pattern types: {len(BacNhoPatternType)} types supported")
    print(f"⚡ Cache timeout: {engine.cache_timeout}s")
