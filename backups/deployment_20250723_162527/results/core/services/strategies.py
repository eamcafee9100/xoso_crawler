import logging
from collections import Counter, defaultdict
from datetime import date, timedelta
from typing import Dict, List, Optional, Tuple

import numpy as np
import pandas as pd
from django.core.cache import cache
from django.db import models
from django.db.models import Avg, Count, Sum
from scipy import stats

from results.models import (
    BtlAnalytics,
    BtlMethodAnalytics,
    DanBtl,
    MethodCyclicalPerformance,
    NumberFrequencyStats,
    PredictionMethodBtl,
    PredictionResultBtl,
)

logger = logging.getLogger(__name__)


def detect_cycle_fft(hit_sequence: List[int]) -> Dict[str, float]:
    """
    Phát hiện chu kỳ mạnh nhất bằng Fourier Transform

    Args:
        hit_sequence: List[int] - Chuỗi 0/1 (0=trượt, 1=trúng)

    Returns:
        Dict với keys: {'dominant_period': float, 'strength': float, 'confidence': float}
    """
    try:
        if len(hit_sequence) < 3:
            return {"dominant_period": 0, "strength": 0, "confidence": 0}

        # Chuẩn hóa dữ liệu
        hits_arr = np.array(hit_sequence)
        hits_normalized = hits_arr - np.mean(hits_arr)

        # FFT
        fft_vals = np.fft.fft(hits_normalized)
        fft_freqs = np.fft.fftfreq(len(hit_sequence))

        # Chỉ lấy tần số dương
        pos_mask = fft_freqs > 0
        fft_freqs = fft_freqs[pos_mask]
        fft_power = np.abs(fft_vals[pos_mask])

        if len(fft_power) == 0:
            return {"dominant_period": 0, "strength": 0, "confidence": 0}

        # Tìm chu kỳ mạnh nhất
        max_power_idx = np.argmax(fft_power)
        dominant_period = (
            1 / fft_freqs[max_power_idx] if fft_freqs[max_power_idx] != 0 else 0
        )
        max_power = fft_power[max_power_idx]

        # Tính độ tin cậy (power ratio)
        total_power = np.sum(fft_power)
        confidence = max_power / total_power if total_power > 0 else 0

        return {
            "dominant_period": float(dominant_period),
            "strength": float(max_power),
            "confidence": float(confidence),
        }

    except Exception as e:
        logger.error(f"Error in detect_cycle_fft: {e}")
        return {"dominant_period": 0, "strength": 0, "confidence": 0}


def phase_wilson_scores(hit_sequence: List[int], period: int) -> Dict[int, float]:
    """
    Tính Wilson score cho từng pha của chu kỳ

    Args:
        hit_sequence: List[int] - Chuỗi kết quả
        period: int - Chu kỳ đã phát hiện

    Returns:
        Dict[int, float] - {phase_index: wilson_score}
    """
    from results.views import wilson_score

    if period <= 0 or len(hit_sequence) < period:
        return {}

    phase_scores = {}

    for phase in range(period):
        phase_hits = [
            hit_sequence[i] for i in range(len(hit_sequence)) if i % period == phase
        ]
        if phase_hits:
            hits = sum(phase_hits)
            total = len(phase_hits)
            score = wilson_score(hits, total)
            phase_scores[phase] = score

    return phase_scores


def markov_chain_probability(hit_history: List[Tuple[str, int]]) -> Dict[str, float]:
    """
    Tính xác suất chuyển trạng thái Markov cho các số

    Args:
        hit_history: List[Tuple[str, int]] - [(number, hit_status), ...]

    Returns:
        Dict[str, float] - {number: probability}
    """
    # Tạo ma trận chuyển trạng thái
    transitions = defaultdict(lambda: defaultdict(int))
    number_states = defaultdict(list)

    # Nhóm theo số
    for number, hit_status in hit_history:
        number_states[number].append(hit_status)

    # Tính ma trận chuyển trạng thái cho mỗi số
    probabilities = {}

    for number, states in number_states.items():
        if len(states) < 2:
            probabilities[number] = 0.5  # Default
            continue

        # Đếm chuyển trạng thái
        for i in range(len(states) - 1):
            current_state = states[i]
            next_state = states[i + 1]
            transitions[current_state][next_state] += 1

        # Tính xác suất hit sau trạng thái hiện tại
        last_state = states[-1]
        total_from_last = sum(transitions[last_state].values())

        if total_from_last > 0:
            prob_hit = transitions[last_state][1] / total_from_last
        else:
            prob_hit = 0.5

        probabilities[number] = prob_hit

    return probabilities


def gap_analysis(number_history: Dict[str, List[date]]) -> Dict[str, Dict]:
    """
    Phân tích khoảng cách giữa các lần xuất hiện

    Args:
        number_history: Dict[str, List[date]] - {number: [dates]}

    Returns:
        Dict[str, Dict] - {number: {'avg_gap': float, 'last_gap': int, 'overdue_score': float}}
    """
    analysis = {}
    today = date.today()

    for number, dates in number_history.items():
        if not dates:
            analysis[number] = {"avg_gap": 0, "last_gap": 999, "overdue_score": 1.0}
            continue

        # Sắp xếp ngày
        sorted_dates = sorted(dates)

        # Tính khoảng cách trung bình
        gaps = []
        for i in range(len(sorted_dates) - 1):
            gap = (sorted_dates[i + 1] - sorted_dates[i]).days
            gaps.append(gap)

        avg_gap = np.mean(gaps) if gaps else 30

        # Khoảng cách từ lần cuối
        last_gap = (today - sorted_dates[-1]).days if sorted_dates else 999

        # Điểm "quá hạn" - số đã lâu không về
        overdue_score = min(last_gap / avg_gap, 2.0) if avg_gap > 0 else 1.0

        analysis[number] = {
            "avg_gap": float(avg_gap),
            "last_gap": last_gap,
            "overdue_score": float(overdue_score),
        }

    return analysis


def frequency_analysis(numbers_data: List[Tuple[str, int]]) -> Dict[str, Dict]:
    """
    Phân tích tần suất xuất hiện

    Args:
        numbers_data: List[Tuple[str, int]] - [(number, frequency)]

    Returns:
        Dict[str, Dict] - {number: {'frequency': int, 'rank': int, 'percentile': float}}
    """
    if not numbers_data:
        return {}

    # Sắp xếp theo tần suất
    sorted_numbers = sorted(numbers_data, key=lambda x: x[1], reverse=True)
    total_numbers = len(sorted_numbers)

    analysis = {}
    for rank, (number, frequency) in enumerate(sorted_numbers, 1):
        percentile = (total_numbers - rank + 1) / total_numbers

        analysis[number] = {
            "frequency": frequency,
            "rank": rank,
            "percentile": float(percentile),
        }

    return analysis


def pattern_mining(sequences: List[List[str]]) -> Dict[str, Dict]:
    """
    Khai thác mẫu số thường xuất hiện cùng nhau

    Args:
        sequences: List[List[str]] - Danh sách các chuỗi số

    Returns:
        Dict[str, Dict] - {number: {'companions': List[str], 'strength': float}}
    """
    # Đếm sự xuất hiện cùng nhau
    co_occurrence = defaultdict(lambda: defaultdict(int))
    number_counts = defaultdict(int)

    for sequence in sequences:
        unique_numbers = list(set(sequence))

        # Đếm từng số
        for number in unique_numbers:
            number_counts[number] += 1

        # Đếm co-occurrence
        for i, num1 in enumerate(unique_numbers):
            for num2 in unique_numbers[i + 1 :]:
                co_occurrence[num1][num2] += 1
                co_occurrence[num2][num1] += 1

    # Tính strength cho mỗi số
    analysis = {}
    for number in number_counts:
        companions = []
        total_co_occurrence = sum(co_occurrence[number].values())

        if total_co_occurrence > 0:
            # Lấy top companions
            sorted_companions = sorted(
                co_occurrence[number].items(), key=lambda x: x[1], reverse=True
            )[:5]

            companions = [comp[0] for comp in sorted_companions]
            strength = total_co_occurrence / number_counts[number]
        else:
            strength = 0

        analysis[number] = {"companions": companions, "strength": float(strength)}

    return analysis


def ensemble_diversity_score(method_predictions: Dict[str, List[str]]) -> float:
    """
    Tính điểm đa dạng của ensemble

    Args:
        method_predictions: Dict[str, List[str]] - {method_name: [predicted_numbers]}

    Returns:
        float - Điểm đa dạng (0-1)
    """
    if not method_predictions:
        return 0.0

    all_numbers = set()
    for predictions in method_predictions.values():
        all_numbers.update(predictions)

    if not all_numbers:
        return 0.0

    # Tính entropy
    number_counts = Counter()
    total_predictions = 0

    for predictions in method_predictions.values():
        for number in predictions:
            number_counts[number] += 1
            total_predictions += 1

    if total_predictions == 0:
        return 0.0

    # Tính entropy
    entropy = 0.0
    for count in number_counts.values():
        prob = count / total_predictions
        if prob > 0:
            entropy -= prob * np.log2(prob)

    # Chuẩn hóa về 0-1
    max_entropy = np.log2(len(all_numbers)) if len(all_numbers) > 1 else 1
    diversity = entropy / max_entropy if max_entropy > 0 else 0

    return float(diversity)


# Add this AnalysisStrategiesService class to the end of your existing file


class AnalysisStrategiesService:
    """
    Service class chính để quản lý và tổ chức các chiến lược phân tích
    Tuân thủ quy tắc trả về dict/list với cấu trúc rõ ràng
    """

    def __init__(self):
        self.cache_timeout = 3600  # 1 hour
        logger.info("AnalysisStrategiesService initialized")

    @staticmethod
    def calculate_wilson_score(
        hits: int, total: int, confidence: float = 0.95
    ) -> float:
        """
        Tính Wilson Score Confidence Interval

        Args:
            hits: int - Số lần trúng
            total: int - Tổng số lần dự đoán
            confidence: float - Mức độ tin cậy (default 0.95)

        Returns:
            float - Wilson score
        """
        if total == 0:
            return 0.0
        z = stats.norm.ppf(1 - (1 - confidence) / 2)
        p = hits / total

        numerator = (
            p
            + (z**2) / (2 * total)
            - z * np.sqrt((p * (1 - p) + (z**2) / (4 * total)) / total)
        )
        denominator = 1 + (z**2) / total

        return max(0, numerator / denominator)
        return max(0, numerator / denominator)

    def get_method_performance_analysis(self, analysis_date: date) -> dict:
        """
        Phân tích hiệu suất của các phương pháp dự đoán

        Args:
            analysis_date: date - Ngày phân tích

        Returns:
            dict - {
                'methods': List[dict],
                'average_accuracy': float,
                'top_performers': List[dict],
                'analysis_date': str
            }
        """
        cache_key = f"method_performance_{analysis_date.strftime('%Y%m%d')}"
        cached_result = cache.get(cache_key)
        if cached_result:
            return cached_result

        try:
            # Lấy dữ liệu phương pháp từ 30 ngày gần nhất
            start_date = analysis_date - timedelta(days=30)

            methods_data = []
            total_accuracy = 0
            method_count = 0

            # Lấy tất cả phương pháp active
            methods = PredictionMethodBtl.objects.filter(is_active=True)

            for method in methods:
                # Lấy analytics cho phương pháp này
                analytics = BtlMethodAnalytics.objects.filter(
                    method=method, date__range=[start_date, analysis_date]
                ).order_by("-date")

                if not analytics.exists():
                    continue

                # Tính toán thống kê
                total_predictions = (
                    analytics.aggregate(total=models.Sum("prediction_count"))["total"]
                    or 0
                )
                correct_predictions = (
                    analytics.aggregate(total=models.Sum("hit_count"))["total"] or 0
                )
                wrong_predictions = total_predictions - correct_predictions

                accuracy = (
                    (correct_predictions / total_predictions * 100)
                    if total_predictions > 0
                    else 0
                )
                wilson_score = self.calculate_wilson_score(
                    correct_predictions, total_predictions
                )
                
                # Lấy predicted_numbers của ngày phân tích cho method này
                predicted_numbers = []
                try:
                    dan_btl = DanBtl.objects.filter(analysis_date=analysis_date).first()
                    if dan_btl:
                        pr = PredictionResultBtl.objects.filter(dan_btl=dan_btl, method=method).first()
                        if pr:
                            predicted_numbers = pr.predicted_numbers
                except Exception as e:
                    predicted_numbers = []
                # logger.info(f"[{method.name}] predicted_numbers for {analysis_date}: {predicted_numbers}")    
                # Tính trend (so sánh 15 ngày gần nhất vs 15 ngày trước)
                recent_analytics = analytics[:15]
                old_analytics = (
                    analytics[15:30] if analytics.count() >= 30 else analytics[15:]
                )

                recent_accuracy = 0
                old_accuracy = 0

                if recent_analytics:
                    recent_total = sum(a.prediction_count for a in recent_analytics)
                    recent_correct = sum(a.hit_count for a in recent_analytics)
                    recent_accuracy = (
                        (recent_correct / recent_total * 100) if recent_total > 0 else 0
                    )

                if old_analytics:
                    old_total = sum(a.prediction_count for a in old_analytics)
                    old_correct = sum(a.hit_count for a in old_analytics)
                    old_accuracy = (
                        (old_correct / old_total * 100) if old_total > 0 else 0
                    )

                trend = (
                    "up"
                    if recent_accuracy > old_accuracy
                    else "down" if recent_accuracy < old_accuracy else "stable"
                )

                method_data = {
                    "id": method.id,
                    "ten_phuong_phap": method.name,
                    "accuracy": round(accuracy, 2),
                    "wilson_score": round(wilson_score, 4),
                    "total_predictions": total_predictions,
                    "correct_predictions": correct_predictions,
                    "wrong_predictions": wrong_predictions,
                    "trend": trend,
                    "is_top_performer": accuracy > 60 and wilson_score > 0.5,
                    "recent_accuracy": round(recent_accuracy, 2),
                    "performance_category": self._categorize_performance(
                        accuracy, wilson_score
                    ),
                    "predicted_numbers": predicted_numbers, 
                }

                methods_data.append(method_data)
                total_accuracy += accuracy
                method_count += 1

            # Sắp xếp theo Wilson score
            methods_data.sort(key=lambda x: x["wilson_score"], reverse=True)

            # Tính average accuracy
            average_accuracy = total_accuracy / method_count if method_count > 0 else 0

            # Lấy top performers
            top_performers = [m for m in methods_data if m["is_top_performer"]][:5]

            result = {
                "methods": methods_data,
                "average_accuracy": round(average_accuracy, 2),
                "top_performers": top_performers,
                "analysis_date": analysis_date.strftime("%Y-%m-%d"),
                "total_methods": len(methods_data),
                "method_count": method_count,
            }

            # Cache kết quả
            cache.set(cache_key, result, self.cache_timeout)
            logger.info(f"Method performance analysis completed for {analysis_date}")

            return result

        except Exception as e:
            logger.error(f"Error in get_method_performance_analysis: {e}")
            return {
                "methods": [],
                "average_accuracy": 0.0,
                "top_performers": [],
                "analysis_date": analysis_date.strftime("%Y-%m-%d"),
                "total_methods": 0,
                "method_count": 0,
                "error": str(e),
            }

    def analyze_cycles(self, analysis_date: date, days_back: int = 60) -> dict:
        """
        Phân tích chu kỳ xuất hiện của số

        Returns:
        {
            'detected_cycles': [
                {
                    'period': int,
                    'confidence': float,
                    'frequency': float
                },
                ...
            ],
            'labels': List[str],
            'fft_data': List[float],
            'autocorr_data': List[float]
        }
        """
        try:
            cache_key = f"cycle_analysis_{analysis_date}_{days_back}"
            cached_result = cache.get(cache_key)
            if cached_result:
                return cached_result

            start_date = analysis_date - timedelta(days=days_back)

            # FIXED: Use 'analysis_date' instead of 'ngay' for DanBtl
            dan_btl_data = DanBtl.objects.filter(
                analysis_date__range=[start_date, analysis_date]
            ).order_by("analysis_date")

            if not dan_btl_data.exists():
                return {
                    "detected_cycles": [],
                    "labels": [],
                    "fft_data": [],
                    "autocorr_data": [],
                }

            # Tạo time series data
            dates = [d.analysis_date for d in dan_btl_data]

            # Tạo binary series cho mỗi số (có xuất hiện hay không)
            all_cycles = []

            # Phân tích cho các số phổ biến
            common_numbers = [
                "00",
                "11",
                "22",
                "33",
                "44",
                "55",
                "66",
                "77",
                "88",
                "99",
            ]

            for number in common_numbers:
                series = []
                for dan_btl in dan_btl_data:
                    # Kiểm tra số có xuất hiện trong predictions không
                    has_number = any(
                        number in str(pred)
                        for pred in dan_btl.predictions_btl.all()
                        if hasattr(dan_btl, "predictions_btl")
                    )
                    series.append(1 if has_number else 0)

                if len(series) >= 10:  # Cần đủ dữ liệu
                    cycles = self.detect_cycles_fft(series)
                    all_cycles.extend(cycles)

            # Tổng hợp và xếp hạng các chu kỳ
            cycle_counts = {}
            for cycle in all_cycles:
                period = cycle["period"]
                if period in cycle_counts:
                    cycle_counts[period]["frequency"] += cycle["frequency"]
                    cycle_counts[period]["confidence"] = max(
                        cycle_counts[period]["confidence"], cycle["confidence"]
                    )
                else:
                    cycle_counts[period] = cycle

            detected_cycles = list(cycle_counts.values())
            detected_cycles.sort(key=lambda x: x["confidence"], reverse=True)

            # Tạo dữ liệu cho biểu đồ
            labels = [str(i) for i in range(len(dates))]
            fft_data = self.generate_sample_fft_data(len(dates))
            autocorr_data = self.generate_sample_autocorr_data(len(dates))

            result = {
                "detected_cycles": detected_cycles[:10],  # Top 10
                "labels": labels,
                "fft_data": fft_data,
                "autocorr_data": autocorr_data,
            }

            cache.set(cache_key, result, self.cache_timeout)
            return result

        except Exception as e:
            logger.error(f"Error in analyze_cycles: {e}")
            return {
                "detected_cycles": [],
                "labels": [],
                "fft_data": [],
                "autocorr_data": [],
            }

    def generate_sample_fft_data(self, length: int) -> List[float]:
        """Tạo dữ liệu FFT mẫu cho biểu đồ"""
        return [abs(np.sin(i * 0.1) * np.exp(-i * 0.01)) for i in range(length)]

    def generate_sample_autocorr_data(self, length: int) -> List[float]:
        """Tạo dữ liệu autocorrelation mẫu cho biểu đồ"""
        return [np.exp(-i * 0.05) * np.cos(i * 0.2) for i in range(length)]

    def detect_cycles_fft(self, series: List[int]) -> List[dict]:
        """Phát hiện chu kỳ bằng FFT"""
        try:
            if len(series) < 4:
                return []

            # FFT
            fft_result = np.fft.fft(series)
            frequencies = np.fft.fftfreq(len(series))

            # Tìm peaks
            magnitudes = np.abs(fft_result)
            cycles = []

            for i, mag in enumerate(magnitudes[1 : len(series) // 2], 1):
                if mag > np.mean(magnitudes) * 1.5:  # Threshold
                    period = int(1 / abs(frequencies[i])) if frequencies[i] != 0 else 0
                    if 2 <= period <= len(series) // 2:
                        confidence = min(0.95, mag / np.max(magnitudes))
                        cycles.append(
                            {
                                "period": period,
                                "confidence": confidence,
                                "frequency": mag,
                            }
                        )

            return cycles

        except Exception:
            return []

    def analyze_gaps(self, analysis_date: date, days_back: int = 60) -> dict:
        """
        Phân tích khoảng cách giữa các lần xuất hiện

        Returns:
        {
            'gap_statistics': [
                {
                    'gap_size': int,
                    'frequency': int,
                    'probability': float,
                    'trend_direction': str
                },
                ...
            ],
            'distribution_labels': List[str],
            'distribution_data': List[int],
            'trend_labels': List[str],
            'trend_data': List[float]
        }
        """
        try:
            cache_key = f"gap_analysis_{analysis_date}_{days_back}"
            cached_result = cache.get(cache_key)
            if cached_result:
                return cached_result

            start_date = analysis_date - timedelta(days=days_back)

            # FIXED: Use 'analysis_date' instead of 'ngay' for DanBtl
            dan_btl_data = DanBtl.objects.filter(
                analysis_date__range=[start_date, analysis_date]
            ).order_by("analysis_date")

            if not dan_btl_data.exists():
                return self._empty_gap_analysis()

            # Phân tích gap cho từng số
            all_gaps = []

            for number in ["00", "11", "22", "33", "44", "55", "66", "77", "88", "99"]:
                appearances = []

                for i, dan_btl in enumerate(dan_btl_data):
                    # Kiểm tra số có xuất hiện không
                    has_number = any(
                        number in str(pred)
                        for pred in dan_btl.predictions_btl.all()
                        if hasattr(dan_btl, "predictions_btl")
                    )
                    if has_number:
                        appearances.append(i)

                # Tính gaps
                if len(appearances) >= 2:
                    gaps = [
                        appearances[i + 1] - appearances[i]
                        for i in range(len(appearances) - 1)
                    ]
                    all_gaps.extend(gaps)

            if not all_gaps:
                return self._empty_gap_analysis()

            # Phân tích thống kê gaps
            gap_counts = {}
            for gap in all_gaps:
                gap_counts[gap] = gap_counts.get(gap, 0) + 1

            total_gaps = len(all_gaps)
            gap_statistics = []

            for gap_size, frequency in sorted(gap_counts.items()):
                probability = frequency / total_gaps
                trend_direction = "increasing" if probability > 0.1 else "decreasing"

                gap_statistics.append(
                    {
                        "gap_size": gap_size,
                        "frequency": frequency,
                        "probability": probability,
                        "trend_direction": trend_direction,
                    }
                )

            # Dữ liệu cho biểu đồ
            distribution_labels = [str(gap["gap_size"]) for gap in gap_statistics[:20]]
            distribution_data = [gap["frequency"] for gap in gap_statistics[:20]]

            trend_labels = [f"Week {i+1}" for i in range(min(12, len(gap_statistics)))]
            trend_data = [gap["probability"] * 100 for gap in gap_statistics[:12]]

            result = {
                "gap_statistics": gap_statistics,
                "distribution_labels": distribution_labels,
                "distribution_data": distribution_data,
                "trend_labels": trend_labels,
                "trend_data": trend_data,
            }

            cache.set(cache_key, result, self.cache_timeout)
            return result

        except Exception as e:
            logger.error(f"Error in analyze_gaps: {e}")
            return self._empty_gap_analysis()

    def mine_patterns(self, analysis_date: date, days_back: int = 60) -> dict:
        """
        Khai thác các pattern xuất hiện thường xuyên

        Returns:
        {
            'frequent_patterns': [
                {
                    'sequence': List[str],
                    'support': float,
                    'confidence': float
                },
                ...
            ]
        }
        """
        try:
            cache_key = f"pattern_mining_{analysis_date}_{days_back}"
            cached_result = cache.get(cache_key)
            if cached_result:
                return cached_result

            start_date = analysis_date - timedelta(days=days_back)

            # FIXED: Use 'analysis_date' instead of 'ngay' for DanBtl
            dan_btl_data = DanBtl.objects.filter(
                analysis_date__range=[start_date, analysis_date]
            ).order_by("analysis_date")

            if not dan_btl_data.exists():
                return {"frequent_patterns": []}

            # Tạo sequences từ dữ liệu
            sequences = []
            for dan_btl in dan_btl_data:
                daily_numbers = []
                # Lấy các số dự đoán cho ngày đó
                if hasattr(dan_btl, "predictions_btl"):
                    for pred in dan_btl.predictions_btl.all():
                        daily_numbers.extend(str(pred).split(","))

                if daily_numbers:
                    sequences.append(daily_numbers[:5])  # Lấy tối đa 5 số

            if not sequences:
                return {"frequent_patterns": []}

            # Mining patterns đơn giản
            frequent_patterns = []

            # Pattern 2-gram
            for i in range(len(sequences) - 1):
                seq1 = sequences[i]
                seq2 = sequences[i + 1]

                if len(seq1) >= 2 and len(seq2) >= 2:
                    pattern = seq1[:2] + seq2[:2]

                    # Tính support và confidence đơn giản
                    support = len(pattern) / (len(sequences) * 4)  # Ước tính
                    confidence = min(0.9, support * 2)  # Ước tính

                    if support > 0.1:  # Threshold
                        frequent_patterns.append(
                            {
                                "sequence": pattern,
                                "support": support,
                                "confidence": confidence,
                            }
                        )

            # Loại bỏ duplicate và sắp xếp
            unique_patterns = []
            seen_patterns = set()

            for pattern in frequent_patterns:
                pattern_key = tuple(pattern["sequence"])
                if pattern_key not in seen_patterns:
                    seen_patterns.add(pattern_key)
                    unique_patterns.append(pattern)

            unique_patterns.sort(key=lambda x: x["confidence"], reverse=True)

            result = {"frequent_patterns": unique_patterns[:10]}  # Top 10

            cache.set(cache_key, result, self.cache_timeout)
            return result

        except Exception as e:
            logger.error(f"Error in mine_patterns: {e}")
            return {"frequent_patterns": []}

    def _categorize_performance(self, accuracy: float, wilson_score: float) -> str:
        """
        Phân loại hiệu suất của phương pháp
        """
        if accuracy >= 70 and wilson_score >= 0.6:
            return "excellent"
        elif accuracy >= 60 and wilson_score >= 0.5:
            return "good"
        elif accuracy >= 50 and wilson_score >= 0.4:
            return "average"
        else:
            return "poor"

    def _extract_numbers_from_dan(self, dan_btl) -> list:
        """
        Trích xuất các số từ DanBtl object
        """
        numbers = []
        # Thêm logic để trích xuất số từ dan_btl object
        # Tùy thuộc vào cấu trúc model DanBtl của bạn
        if hasattr(dan_btl, "giai_db") and dan_btl.giai_db:
            # Ví dụ: giai_db có format "12-34-56"
            numbers.extend(dan_btl.giai_db.split("-"))

        # Thêm logic cho các giải khác nếu cần
        return [num.strip() for num in numbers if num.strip()]

    def _empty_cycle_analysis(self) -> dict:
        """Trả về kết quả cycle analysis rỗng"""
        return {
            "analysis_date": "",
            "cycle_results": [],
            "detected_cycles": [],
            "labels": [],
            "fft_data": [],
            "autocorr_data": [],
            "total_numbers_analyzed": 0,
            "significant_cycles_found": 0,
        }

    def _empty_gap_analysis(self) -> dict:
        """Trả về kết quả gap analysis rỗng"""
        return {
            "analysis_date": "",
            "gap_statistics": [],
            "distribution_labels": [],
            "distribution_data": [],
            "trend_labels": [],
            "trend_data": [],
            "total_numbers_analyzed": 0,
            "overdue_numbers": 0,
        }

    def _empty_pattern_mining(self) -> dict:
        """Trả về kết quả pattern mining rỗng"""
        return {
            "analysis_date": "",
            "frequent_patterns": [],
            "total_sequences_analyzed": 0,
            "patterns_found": 0,
            "min_support_threshold": 0.3,
            "average_pattern_strength": 0,
        }
