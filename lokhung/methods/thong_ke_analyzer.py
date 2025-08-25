"""
PHASE 4 - THONG KE FREQUENCY ANALYZER
====================================
Advanced statistical frequency analysis with machine learning enhancements.
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
import scipy.stats as stats
from django.core.cache import cache
from django.db.models import Avg, Count, Q

# Django imports
from django.utils import timezone
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler

# Project imports
from lokhung.models import KetQuaXoSo, PhanTichSo
from lottery_prediction.models import PredictionResult

# Configure logging
logger = logging.getLogger(__name__)


class FrequencyAnalysisType(Enum):
    """Các loại phân tích tần suất"""

    BASIC_FREQUENCY = "basic_frequency"
    ROLLING_FREQUENCY = "rolling_frequency"
    WEIGHTED_FREQUENCY = "weighted_frequency"
    STATISTICAL_ANALYSIS = "statistical_analysis"
    CLUSTER_ANALYSIS = "cluster_analysis"
    TREND_ANALYSIS = "trend_analysis"


class FrequencyPattern(Enum):
    """Các pattern tần suất"""

    STABLE = "stable"  # Ổn định
    INCREASING = "increasing"  # Tăng dần
    DECREASING = "decreasing"  # Giảm dần
    VOLATILE = "volatile"  # Biến động
    OUTLIER = "outlier"  # Ngoại lệ
    CYCLICAL = "cyclical"  # Chu kỳ


@dataclass
class FrequencyData:
    """Dữ liệu tần suất cho một số"""

    number: int
    absolute_frequency: int
    relative_frequency: float
    expected_frequency: float
    deviation: float
    z_score: float
    trend: FrequencyPattern
    rolling_averages: List[float]
    statistical_measures: Dict
    cluster_group: int
    prediction_score: float
    confidence: float


@dataclass
class ThongKeAnalysisResult:
    """Kết quả phân tích thống kê"""

    numbers: List[int]
    confidence: float
    frequency_data: List[FrequencyData]
    analysis_details: Dict
    method_weight: float
    processing_time: float
    timestamp: datetime
    statistical_summary: Dict


class ThongKeFrequencyAnalyzer:
    """
    Analyzer thống kê tần suất với machine learning
    """

    def __init__(self):
        self.name = "Thong Ke Frequency Analyzer"
        self.version = "4.0.0"
        self.method_weight = 0.16  # 16% weight trong ensemble
        self.cache_timeout = 300  # 5 minutes

        # Analysis parameters
        self.analysis_periods = [30, 60, 90, 180]  # Multiple analysis windows
        self.rolling_windows = [7, 14, 30]  # Rolling average windows
        self.significance_level = 0.05  # Statistical significance
        self.outlier_threshold = 2.5  # Z-score threshold for outliers

        # ML parameters
        self.n_clusters = 5  # Number of clusters for grouping
        self.trend_window = 14  # Days for trend analysis

        # Prediction parameters
        self.confidence_threshold = 0.6
        self.prediction_count_range = (8, 15)

        logger.info(f"📊 {self.name} v{self.version} initialized")

    def analyze(
        self, region: str, date: datetime, historical_data: Optional[List] = None
    ) -> ThongKeAnalysisResult:
        """
        Phân tích thống kê tần suất cho region và date cụ thể

        Args:
            region: Tên miền (MB, MT, MN)
            date: Ngày cần dự đoán
            historical_data: Dữ liệu lịch sử (optional)

        Returns:
            ThongKeAnalysisResult: Kết quả phân tích đầy đủ
        """
        start_time = datetime.now()

        try:
            # Check cache
            cache_key = f"thong_ke_analysis_{region}_{date.strftime('%Y%m%d')}"
            cached_result = cache.get(cache_key)

            if cached_result:
                logger.info(f"🎯 Cache hit for Thong Ke analysis: {cache_key}")
                return ThongKeAnalysisResult(**cached_result)

            # Get historical data for multiple periods
            historical_datasets = self._get_multi_period_data(region, date)

            # Perform comprehensive frequency analysis
            frequency_data = self._analyze_all_frequencies(historical_datasets, date)
            statistical_summary = self._generate_statistical_summary(
                frequency_data, historical_datasets
            )
            numbers = self._select_predictions(frequency_data)
            confidence = self._calculate_overall_confidence(frequency_data, numbers)
            analysis_details = self._generate_analysis_details(
                frequency_data, statistical_summary
            )

            # Create result
            result = ThongKeAnalysisResult(
                numbers=numbers,
                confidence=confidence,
                frequency_data=frequency_data,
                analysis_details=analysis_details,
                method_weight=self.method_weight,
                processing_time=(datetime.now() - start_time).total_seconds(),
                timestamp=timezone.now(),
                statistical_summary=statistical_summary,
            )

            # Cache result
            cache.set(cache_key, result.__dict__, self.cache_timeout)

            logger.info(
                f"📊 Thong Ke analysis completed: {len(numbers)} numbers, "
                f"confidence {confidence:.2f}"
            )

            return result

        except Exception as e:
            logger.error(f"❌ Error in Thong Ke analysis: {str(e)}")
            return self._create_fallback_result(start_time)

    def _get_multi_period_data(
        self, region: str, date: datetime
    ) -> Dict[int, List[Dict]]:
        """Lấy dữ liệu cho nhiều khoảng thời gian khác nhau"""
        datasets = {}

        try:
            for period in self.analysis_periods:
                end_date = date - timedelta(days=1)
                start_date = end_date - timedelta(days=period)

                queryset = KetQuaXoSo.objects.filter(
                    ngay__range=[start_date, end_date], mien__icontains=region
                ).order_by("-ngay")

                period_data = []
                for record in queryset:
                    numbers = self._extract_all_numbers(record)
                    period_data.append(
                        {"date": record.ngay, "numbers": numbers, "record": record}
                    )

                datasets[period] = period_data
                logger.info(
                    f"📊 Retrieved {len(period_data)} records for {period}-day period"
                )

            return datasets

        except Exception as e:
            logger.error(f"❌ Error getting multi-period data: {str(e)}")
            return {}

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

    def _analyze_all_frequencies(
        self, datasets: Dict[int, List[Dict]], target_date: datetime
    ) -> List[FrequencyData]:
        """Phân tích tần suất cho tất cả các số"""
        frequency_data = []

        try:
            # Use longest period for main analysis
            main_period = max(self.analysis_periods)
            main_dataset = datasets.get(main_period, [])

            if not main_dataset:
                return []

            # Analyze each number
            for number in range(100):
                data = self._analyze_single_number_frequency(
                    number, datasets, target_date
                )
                if data:
                    frequency_data.append(data)

            # Perform cluster analysis
            frequency_data = self._perform_cluster_analysis(frequency_data)

            # Sort by prediction score
            frequency_data.sort(key=lambda x: x.prediction_score, reverse=True)

            logger.info(f"📊 Analyzed frequency for {len(frequency_data)} numbers")
            return frequency_data

        except Exception as e:
            logger.error(f"❌ Error analyzing frequencies: {str(e)}")
            return []

    def _analyze_single_number_frequency(
        self, number: int, datasets: Dict[int, List[Dict]], target_date: datetime
    ) -> Optional[FrequencyData]:
        """Phân tích tần suất chi tiết cho một số"""
        try:
            main_period = max(self.analysis_periods)
            main_dataset = datasets[main_period]

            # Count appearances in main dataset
            appearances = [
                record for record in main_dataset if number in record["numbers"]
            ]
            absolute_frequency = len(appearances)

            if absolute_frequency == 0:
                return None  # Skip numbers that never appeared

            # Calculate basic frequency metrics
            total_draws = len(main_dataset)
            relative_frequency = (
                absolute_frequency / total_draws if total_draws > 0 else 0
            )
            expected_frequency = 1 / 100  # Assuming equal probability for all numbers
            deviation = relative_frequency - expected_frequency

            # Calculate Z-score for statistical significance
            if total_draws > 0:
                expected_count = total_draws * expected_frequency
                variance = total_draws * expected_frequency * (1 - expected_frequency)
                if variance > 0:
                    z_score = (absolute_frequency - expected_count) / np.sqrt(variance)
                else:
                    z_score = 0
            else:
                z_score = 0

            # Calculate rolling averages
            rolling_averages = self._calculate_rolling_averages(number, main_dataset)

            # Determine trend pattern
            trend = self._determine_frequency_trend(rolling_averages, z_score)

            # Calculate statistical measures
            statistical_measures = self._calculate_statistical_measures(
                number, datasets, appearances
            )

            # Calculate prediction score
            prediction_score = self._calculate_prediction_score(
                relative_frequency,
                deviation,
                z_score,
                trend,
                rolling_averages,
                statistical_measures,
            )

            # Calculate confidence
            confidence = self._calculate_frequency_confidence(
                absolute_frequency, z_score, trend, len(rolling_averages)
            )

            return FrequencyData(
                number=number,
                absolute_frequency=absolute_frequency,
                relative_frequency=relative_frequency,
                expected_frequency=expected_frequency,
                deviation=deviation,
                z_score=z_score,
                trend=trend,
                rolling_averages=rolling_averages,
                statistical_measures=statistical_measures,
                cluster_group=0,  # Will be set in cluster analysis
                prediction_score=prediction_score,
                confidence=confidence,
            )

        except Exception as e:
            logger.error(f"❌ Error analyzing frequency for number {number}: {str(e)}")
            return None

    def _calculate_rolling_averages(
        self, number: int, dataset: List[Dict]
    ) -> List[float]:
        """Tính rolling average cho số"""
        rolling_averages = []

        try:
            for window in self.rolling_windows:
                if len(dataset) >= window:
                    # Calculate rolling frequency for each window
                    frequencies = []
                    for i in range(len(dataset) - window + 1):
                        window_data = dataset[i : i + window]
                        appearances = sum(
                            1 for record in window_data if number in record["numbers"]
                        )
                        frequency = appearances / window
                        frequencies.append(frequency)

                    # Calculate average of rolling frequencies
                    if frequencies:
                        rolling_averages.append(np.mean(frequencies))
                    else:
                        rolling_averages.append(0)
                else:
                    rolling_averages.append(0)

            return rolling_averages

        except Exception as e:
            logger.error(f"❌ Error calculating rolling averages: {str(e)}")
            return [0] * len(self.rolling_windows)

    def _determine_frequency_trend(
        self, rolling_averages: List[float], z_score: float
    ) -> FrequencyPattern:
        """Xác định trend pattern của tần suất"""
        try:
            if not rolling_averages or len(rolling_averages) < 2:
                return FrequencyPattern.STABLE

            # Check for outliers first
            if abs(z_score) > self.outlier_threshold:
                return FrequencyPattern.OUTLIER

            # Analyze trend in rolling averages
            changes = []
            for i in range(1, len(rolling_averages)):
                if rolling_averages[i - 1] != 0:
                    change = (
                        rolling_averages[i] - rolling_averages[i - 1]
                    ) / rolling_averages[i - 1]
                    changes.append(change)

            if not changes:
                return FrequencyPattern.STABLE

            # Calculate trend metrics
            avg_change = np.mean(changes)
            change_std = np.std(changes) if len(changes) > 1 else 0

            # Determine pattern
            if change_std > 0.3:  # High variance
                return FrequencyPattern.VOLATILE
            elif avg_change > 0.1:  # Consistent increase
                return FrequencyPattern.INCREASING
            elif avg_change < -0.1:  # Consistent decrease
                return FrequencyPattern.DECREASING
            elif self._detect_cyclical_pattern(rolling_averages):
                return FrequencyPattern.CYCLICAL
            else:
                return FrequencyPattern.STABLE

        except Exception as e:
            return FrequencyPattern.STABLE

    def _detect_cyclical_pattern(self, values: List[float]) -> bool:
        """Phát hiện pattern chu kỳ"""
        try:
            if len(values) < 4:
                return False

            # Simple cycle detection: look for alternating increases/decreases
            direction_changes = 0
            for i in range(2, len(values)):
                if (values[i - 2] < values[i - 1] > values[i]) or (
                    values[i - 2] > values[i - 1] < values[i]
                ):
                    direction_changes += 1

            # If more than half the points show alternating pattern
            return direction_changes >= len(values) // 2

        except Exception as e:
            return False

    def _calculate_statistical_measures(
        self, number: int, datasets: Dict[int, List[Dict]], appearances: List[Dict]
    ) -> Dict:
        """Tính các chỉ số thống kê"""
        try:
            measures = {}

            # Multi-period analysis
            for period, dataset in datasets.items():
                period_appearances = sum(
                    1 for record in dataset if number in record["numbers"]
                )
                period_frequency = period_appearances / len(dataset) if dataset else 0
                measures[f"frequency_{period}d"] = period_frequency

            # Time-based analysis
            if appearances:
                dates = [record["date"] for record in appearances]
                dates.sort()

                # Calculate intervals between appearances
                intervals = []
                for i in range(1, len(dates)):
                    interval = (dates[i] - dates[i - 1]).days
                    intervals.append(interval)

                if intervals:
                    measures.update(
                        {
                            "avg_interval": np.mean(intervals),
                            "std_interval": np.std(intervals),
                            "min_interval": min(intervals),
                            "max_interval": max(intervals),
                            "last_appearance_days": (
                                datetime.now().date() - dates[-1]
                            ).days,
                        }
                    )
                else:
                    measures.update(
                        {
                            "avg_interval": 0,
                            "std_interval": 0,
                            "min_interval": 0,
                            "max_interval": 0,
                            "last_appearance_days": (
                                datetime.now().date() - dates[0]
                            ).days,
                        }
                    )

            # Chi-square goodness of fit test
            main_dataset = datasets[max(self.analysis_periods)]
            observed = sum(1 for record in main_dataset if number in record["numbers"])
            expected = len(main_dataset) / 100

            if expected > 0:
                chi_square = ((observed - expected) ** 2) / expected
                measures["chi_square"] = chi_square
                measures["chi_square_p_value"] = 1 - stats.chi2.cdf(chi_square, 1)

            return measures

        except Exception as e:
            logger.error(f"❌ Error calculating statistical measures: {str(e)}")
            return {}

    def _calculate_prediction_score(
        self,
        relative_frequency: float,
        deviation: float,
        z_score: float,
        trend: FrequencyPattern,
        rolling_averages: List[float],
        statistical_measures: Dict,
    ) -> float:
        """Tính điểm dự đoán"""
        try:
            score = 0.0

            # Base score from frequency deviation
            if abs(deviation) > 0.005:  # Significant deviation
                score += min(0.3, abs(deviation) * 10)

            # Z-score contribution
            if abs(z_score) > 1.0:  # Statistically significant
                score += min(0.25, abs(z_score) * 0.1)

            # Trend pattern bonuses
            trend_bonuses = {
                FrequencyPattern.INCREASING: 0.2,
                FrequencyPattern.DECREASING: 0.15,
                FrequencyPattern.VOLATILE: 0.1,
                FrequencyPattern.OUTLIER: 0.25,
                FrequencyPattern.CYCLICAL: 0.15,
                FrequencyPattern.STABLE: 0.05,
            }
            score += trend_bonuses.get(trend, 0)

            # Rolling average trend
            if len(rolling_averages) >= 2:
                recent_trend = rolling_averages[-1] - rolling_averages[0]
                if recent_trend > 0:
                    score += min(0.15, recent_trend * 2)

            # Statistical significance bonus
            chi_square_p = statistical_measures.get("chi_square_p_value", 1)
            if chi_square_p < self.significance_level:
                score += 0.1

            # Due number bonus (haven't appeared recently)
            last_appearance_days = statistical_measures.get("last_appearance_days", 0)
            if last_appearance_days > 14:
                score += min(0.2, last_appearance_days / 50)

            return round(min(1.0, score), 3)

        except Exception as e:
            return 0.5

    def _calculate_frequency_confidence(
        self,
        absolute_frequency: int,
        z_score: float,
        trend: FrequencyPattern,
        data_points: int,
    ) -> float:
        """Tính confidence cho frequency analysis"""
        try:
            base_confidence = 0.5

            # Frequency count bonus
            if absolute_frequency >= 3:
                base_confidence += min(0.1, absolute_frequency * 0.02)

            # Statistical significance
            if abs(z_score) > 1.5:
                base_confidence += 0.1
            elif abs(z_score) > 1.0:
                base_confidence += 0.05

            # Trend reliability
            trend_confidence = {
                FrequencyPattern.STABLE: 0.8,
                FrequencyPattern.INCREASING: 0.75,
                FrequencyPattern.DECREASING: 0.7,
                FrequencyPattern.OUTLIER: 0.85,
                FrequencyPattern.VOLATILE: 0.6,
                FrequencyPattern.CYCLICAL: 0.65,
            }
            base_confidence *= trend_confidence.get(trend, 0.7)

            # Data quality adjustment
            if data_points >= len(self.rolling_windows):
                base_confidence += 0.05

            return round(min(0.95, base_confidence), 3)

        except Exception as e:
            return 0.6

    def _perform_cluster_analysis(
        self, frequency_data: List[FrequencyData]
    ) -> List[FrequencyData]:
        """Thực hiện cluster analysis để nhóm các số"""
        try:
            if len(frequency_data) < self.n_clusters:
                return frequency_data

            # Prepare features for clustering
            features = []
            for data in frequency_data:
                feature_vector = [
                    data.relative_frequency,
                    data.deviation,
                    data.z_score,
                    data.prediction_score,
                    np.mean(data.rolling_averages) if data.rolling_averages else 0,
                ]
                features.append(feature_vector)

            # Standardize features
            scaler = StandardScaler()
            features_scaled = scaler.fit_transform(features)

            # Perform K-means clustering
            kmeans = KMeans(n_clusters=self.n_clusters, random_state=42, n_init=10)
            clusters = kmeans.fit_predict(features_scaled)

            # Assign cluster groups
            for i, data in enumerate(frequency_data):
                data.cluster_group = int(clusters[i])

            logger.info(
                f"🎯 Clustered {len(frequency_data)} numbers into {self.n_clusters} groups"
            )
            return frequency_data

        except Exception as e:
            logger.error(f"❌ Error in cluster analysis: {str(e)}")
            return frequency_data

    def _select_predictions(self, frequency_data: List[FrequencyData]) -> List[int]:
        """Chọn số dự đoán dựa trên frequency analysis"""
        try:
            # Score and rank all numbers
            scored_numbers = []

            for data in frequency_data:
                # Multi-factor scoring
                frequency_score = data.prediction_score
                confidence_score = data.confidence

                # Trend bonuses
                trend_bonus = {
                    FrequencyPattern.OUTLIER: 0.2,
                    FrequencyPattern.INCREASING: 0.15,
                    FrequencyPattern.VOLATILE: 0.1,
                    FrequencyPattern.CYCLICAL: 0.1,
                    FrequencyPattern.DECREASING: 0.05,
                    FrequencyPattern.STABLE: 0.0,
                }.get(data.trend, 0)

                # Statistical significance bonus
                if abs(data.z_score) > 2.0:
                    significance_bonus = 0.15
                elif abs(data.z_score) > 1.5:
                    significance_bonus = 0.1
                else:
                    significance_bonus = 0

                # Cluster diversity (prefer different clusters)
                cluster_bonus = 0.05 if data.cluster_group in [0, 1, 2] else 0

                final_score = (
                    (frequency_score * 0.4)
                    + (confidence_score * 0.3)
                    + trend_bonus
                    + significance_bonus
                    + cluster_bonus
                )

                scored_numbers.append((data.number, final_score, data))

            # Sort by score
            scored_numbers.sort(key=lambda x: x[1], reverse=True)

            # Select diverse predictions
            selected_numbers = []
            cluster_counts = defaultdict(int)

            # Ensure cluster diversity
            for number, score, data in scored_numbers:
                if len(selected_numbers) >= self.prediction_count_range[1]:
                    break

                # Limit numbers per cluster to ensure diversity
                if cluster_counts[data.cluster_group] < 3:
                    selected_numbers.append(number)
                    cluster_counts[data.cluster_group] += 1

            # Fill remaining slots with highest scorers
            for number, score, data in scored_numbers:
                if len(selected_numbers) >= self.prediction_count_range[1]:
                    break
                if number not in selected_numbers:
                    selected_numbers.append(number)
                    if len(selected_numbers) >= self.prediction_count_range[0]:
                        # Have minimum, can stop if quality threshold met
                        if score < 0.4:  # Quality threshold
                            break

            logger.info(
                f"📊 Selected {len(selected_numbers)} numbers from frequency analysis"
            )
            return selected_numbers

        except Exception as e:
            logger.error(f"❌ Error selecting predictions: {str(e)}")
            return []

    def _calculate_overall_confidence(
        self, frequency_data: List[FrequencyData], numbers: List[int]
    ) -> float:
        """Tính confidence tổng thể"""
        try:
            if not numbers or not frequency_data:
                return 0.5

            # Get data for selected numbers
            selected_data = [data for data in frequency_data if data.number in numbers]

            if not selected_data:
                return 0.5

            # Calculate weighted confidence
            total_weight = sum(data.prediction_score for data in selected_data)
            if total_weight > 0:
                weighted_confidence = (
                    sum(
                        data.confidence * data.prediction_score
                        for data in selected_data
                    )
                    / total_weight
                )
            else:
                weighted_confidence = np.mean(
                    [data.confidence for data in selected_data]
                )

            # Statistical significance bonus
            significant_count = sum(
                1 for data in selected_data if abs(data.z_score) > 1.5
            )
            significance_bonus = min(0.1, significant_count / len(selected_data) * 0.1)

            # Cluster diversity bonus
            clusters_used = len(set(data.cluster_group for data in selected_data))
            diversity_bonus = min(0.05, clusters_used / self.n_clusters * 0.05)

            final_confidence = (
                weighted_confidence + significance_bonus + diversity_bonus
            )
            return round(min(0.95, final_confidence), 3)

        except Exception as e:
            logger.error(f"❌ Error calculating overall confidence: {str(e)}")
            return 0.6

    def _generate_statistical_summary(
        self, frequency_data: List[FrequencyData], datasets: Dict[int, List[Dict]]
    ) -> Dict:
        """Tạo tóm tắt thống kê"""
        try:
            # Overall statistics
            frequencies = [data.relative_frequency for data in frequency_data]
            z_scores = [data.z_score for data in frequency_data]

            summary = {
                "total_numbers_analyzed": len(frequency_data),
                "frequency_statistics": {
                    "mean": np.mean(frequencies),
                    "std": np.std(frequencies),
                    "min": min(frequencies),
                    "max": max(frequencies),
                },
                "z_score_statistics": {
                    "mean": np.mean(z_scores),
                    "std": np.std(z_scores),
                    "outliers": sum(
                        1 for z in z_scores if abs(z) > self.outlier_threshold
                    ),
                },
            }

            # Pattern distribution
            pattern_counts = Counter(data.trend for data in frequency_data)
            summary["pattern_distribution"] = {
                pattern.value: count for pattern, count in pattern_counts.items()
            }

            # Cluster analysis
            if frequency_data:
                cluster_counts = Counter(data.cluster_group for data in frequency_data)
                summary["cluster_distribution"] = dict(cluster_counts)

                # Top numbers by cluster
                summary["top_by_cluster"] = {}
                for cluster_id in range(self.n_clusters):
                    cluster_data = [
                        data
                        for data in frequency_data
                        if data.cluster_group == cluster_id
                    ]
                    if cluster_data:
                        top_in_cluster = sorted(
                            cluster_data, key=lambda x: x.prediction_score, reverse=True
                        )[:3]
                        summary["top_by_cluster"][cluster_id] = [
                            {"number": data.number, "score": data.prediction_score}
                            for data in top_in_cluster
                        ]

            return summary

        except Exception as e:
            logger.error(f"❌ Error generating statistical summary: {str(e)}")
            return {}

    def _generate_analysis_details(
        self, frequency_data: List[FrequencyData], statistical_summary: Dict
    ) -> Dict:
        """Tạo chi tiết phân tích"""
        try:
            # Top performers by different criteria
            top_by_frequency = sorted(
                frequency_data, key=lambda x: x.relative_frequency, reverse=True
            )[:10]
            top_by_deviation = sorted(
                frequency_data, key=lambda x: abs(x.deviation), reverse=True
            )[:10]
            top_by_z_score = sorted(
                frequency_data, key=lambda x: abs(x.z_score), reverse=True
            )[:10]
            top_by_score = sorted(
                frequency_data, key=lambda x: x.prediction_score, reverse=True
            )[:10]

            return {
                "analysis_periods": self.analysis_periods,
                "rolling_windows": self.rolling_windows,
                "statistical_summary": statistical_summary,
                "top_performers": {
                    "by_frequency": [
                        {"number": d.number, "frequency": d.relative_frequency}
                        for d in top_by_frequency
                    ],
                    "by_deviation": [
                        {"number": d.number, "deviation": d.deviation}
                        for d in top_by_deviation
                    ],
                    "by_z_score": [
                        {"number": d.number, "z_score": d.z_score}
                        for d in top_by_z_score
                    ],
                    "by_prediction_score": [
                        {"number": d.number, "score": d.prediction_score}
                        for d in top_by_score
                    ],
                },
                "method_parameters": {
                    "n_clusters": self.n_clusters,
                    "significance_level": self.significance_level,
                    "outlier_threshold": self.outlier_threshold,
                    "confidence_threshold": self.confidence_threshold,
                },
                "method_version": self.version,
            }

        except Exception as e:
            logger.error(f"❌ Error generating analysis details: {str(e)}")
            return {"error": str(e)}

    def _create_fallback_result(self, start_time: datetime) -> ThongKeAnalysisResult:
        """Tạo kết quả dự phòng"""
        return ThongKeAnalysisResult(
            numbers=list(range(30, 40)),
            confidence=0.5,
            frequency_data=[],
            analysis_details={"error": "Fallback result"},
            method_weight=self.method_weight,
            processing_time=(datetime.now() - start_time).total_seconds(),
            timestamp=timezone.now(),
            statistical_summary={},
        )

    def get_api_info(self) -> Dict:
        """Trả về thông tin API"""
        return {
            "name": self.name,
            "version": self.version,
            "method_weight": self.method_weight,
            "endpoints": {
                "analyze": "Phân tích tần suất thống kê",
                "get_frequency_details": "Chi tiết tần suất cho số cụ thể",
                "get_statistical_summary": "Tóm tắt thống kê",
            },
            "supported_regions": ["MB", "MT", "MN"],
            "analysis_types": [atype.value for atype in FrequencyAnalysisType],
            "pattern_types": [pattern.value for pattern in FrequencyPattern],
            "analysis_periods": self.analysis_periods,
            "rolling_windows": self.rolling_windows,
            "cache_timeout": self.cache_timeout,
        }


# Export main class
__all__ = [
    "ThongKeFrequencyAnalyzer",
    "ThongKeAnalysisResult",
    "FrequencyData",
    "FrequencyPattern",
    "FrequencyAnalysisType",
]

if __name__ == "__main__":
    # Quick test
    analyzer = ThongKeFrequencyAnalyzer()
    print(f"📊 {analyzer.name} v{analyzer.version} - Ready for Phase 4!")
    print(f"📈 Method weight: {analyzer.method_weight}")
    print(f"🎯 Analysis periods: {analyzer.analysis_periods}")
    print(f"📊 Clusters: {analyzer.n_clusters}")
    print(f"⚡ Rolling windows: {analyzer.rolling_windows}")
