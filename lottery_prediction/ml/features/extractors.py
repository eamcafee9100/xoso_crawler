# ml/features/extractors.py

import logging
from collections import Counter, defaultdict
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple

import numpy as np
import pandas as pd
from django.db.models import Avg, Count, Max, Q
from django.utils import timezone

from results.models import KetQuaXoSo, NumberFrequencyStats

logger = logging.getLogger(__name__)


class LotteryFeatureExtractor:
    """
    Extract comprehensive features for lottery number prediction
    Prevents data leakage by only using data before target_date
    """

    def __init__(self, target_date: datetime.date, context: str = "prediction"):
        """
        Initialize feature extractor for a specific target date

        Args:
            target_date: Date to predict for
            context: 'prediction', 'training', 'evaluation', 'backtesting', 'validation'
        """
        self.target_date = target_date
        self.context = context
        self.reference_date = target_date - timedelta(days=1)

        # Context-aware validation
        if context == "prediction":
            # Only validate for real predictions
            DataLeakageValidator.validate_prediction_request(
                target_date, context=context
            )
        elif context in ["training", "evaluation", "backtesting"]:
            # Light validation for historical analysis
            if target_date > datetime.now().date():
                logger.info(f"Future date analysis: {target_date}")
        # 'validation' context skips all validation

        self._feature_cache = {}

    def _validate_date_constraints(self):
        """Context-aware validation to prevent data leakage"""
        # Only strict validation for real predictions
        if self.context == "prediction":
            latest_available = (
                KetQuaXoSo.objects.values_list("ngay", flat=True)
                .order_by("-ngay")
                .first()
            )

            if latest_available and latest_available >= self.target_date:
                raise ValueError(
                    f"Data leakage detected! Target date {self.target_date} has data available. "
                    f"Latest available: {latest_available}"
                )
        elif self.context in ["evaluation", "backtesting", "training"]:
            # Allow historical dates for evaluation
            logger.debug(
                f"Historical analysis for {self.target_date} in {self.context} context"
            )
        # No validation for 'validation' context

        logger.info(
            f"Feature extraction for {self.target_date}, using data up to {self.reference_date}"
        )

    def extract_features_for_date(self, use_cache: bool = True) -> pd.DataFrame:
        """Extract all features for the target date with context awareness"""
        if use_cache and "complete_features" in self._feature_cache:
            return self._feature_cache["complete_features"]

        # Context-aware logging
        if self.context == "validation":
            logger.debug(f"Extracting features for validation: {self.target_date}")
        elif self.context in ["evaluation", "backtesting"]:
            logger.debug(f"Extracting features for {self.context}: {self.target_date}")
        else:
            logger.info(f"Extracting features for {self.context}: {self.target_date}")

        # Initialize feature matrix
        numbers = [f"{i:02d}" for i in range(100)]
        features_dict = {number: {} for number in numbers}

        try:
            # Extract different types of features
            self._extract_frequency_features(features_dict)
            self._extract_temporal_features(features_dict)
            self._extract_sequential_features(features_dict)
            self._extract_statistical_features(features_dict)
            self._extract_cyclical_features(features_dict)
            self._extract_position_features(features_dict)

        except Exception as e:
            logger.error(f"Error extracting features for {self.target_date}: {e}")
            # Return minimal features on error
            for number in numbers:
                features_dict[number] = {
                    "frequency_7d": 0.01,
                    "day_of_week": self.target_date.weekday(),
                }

        # Convert to DataFrame
        feature_df = pd.DataFrame.from_dict(features_dict, orient="index")
        feature_df.index.name = "number"
        feature_df = feature_df.fillna(0)

        # Cache results
        if use_cache:
            self._feature_cache["complete_features"] = feature_df

        return feature_df

    def _extract_features_without_validation(self) -> pd.DataFrame:
        """
        Extract features without data leakage validation
        Used for training data preparation where we know the data is historical
        """
        logger.info(
            f"Extracting features for training date: {self.target_date} (validation skipped)"
        )

        # Initialize feature matrix for all numbers 00-99
        numbers = [f"{i:02d}" for i in range(100)]
        features_dict = {number: {} for number in numbers}

        try:
            # Extract different types of features (same as extract_features_for_date but skip validation)
            self._extract_frequency_features(features_dict)
            self._extract_temporal_features(features_dict)
            self._extract_sequential_features(features_dict)
            self._extract_statistical_features(features_dict)
            self._extract_cyclical_features(features_dict)
            self._extract_position_features(features_dict)

            # Convert to DataFrame
            feature_df = pd.DataFrame.from_dict(features_dict, orient="index")
            feature_df.index.name = "number"

            # Fill NaN values
            feature_df = feature_df.fillna(0)

            logger.info(
                f"Extracted {len(feature_df.columns)} features for {len(feature_df)} numbers (training mode)"
            )
            return feature_df

        except Exception as e:
            logger.warning(
                f"Error extracting features for training date {self.target_date}: {e}"
            )
            # Return minimal fallback features
            fallback_features = {}
            for number in numbers:
                if len(number) == 2:
                    first_digit = int(number[0])
                    second_digit = int(number[1])
                    fallback_features[number] = {
                        "target_day_of_week": self.target_date.weekday(),
                        "target_day_of_month": self.target_date.day,
                        "target_month": self.target_date.month,
                        "first_digit": first_digit,
                        "second_digit": second_digit,
                        "digit_sum": first_digit + second_digit,
                        "number_value": int(number),
                        "default_feature": 1.0,
                    }

            return pd.DataFrame.from_dict(fallback_features, orient="index").fillna(0)

    def _extract_frequency_features(self, features_dict: Dict):
        """Extract frequency-based features"""
        logger.debug("Extracting frequency features...")

        # Get historical data for different time windows
        time_windows = [7, 15, 30, 60, 90, 180, 365]

        for window in time_windows:
            start_date = self.reference_date - timedelta(days=window)

            # Query frequency stats
            freq_stats = (
                NumberFrequencyStats.objects.filter(
                    date__gte=start_date, date__lte=self.reference_date
                )
                .values("number")
                .annotate(
                    count=Count("id"),
                    special_count=Count("id", filter=Q(appeared_in_special=True)),
                    first_count=Count("id", filter=Q(appeared_in_first=True)),
                    other_count=Count("id", filter=Q(appeared_in_other=True)),
                )
            )

            # Convert to dict for quick lookup
            freq_dict = {stat["number"]: stat for stat in freq_stats}

            for number in features_dict.keys():
                stat = freq_dict.get(
                    number,
                    {
                        "count": 0,
                        "special_count": 0,
                        "first_count": 0,
                        "other_count": 0,
                    },
                )

                features_dict[number][f"freq_{window}d"] = stat["count"]
                features_dict[number][f"freq_rate_{window}d"] = stat["count"] / window
                features_dict[number][f"special_freq_{window}d"] = stat["special_count"]
                features_dict[number][f"first_freq_{window}d"] = stat["first_count"]
                features_dict[number][f"other_freq_{window}d"] = stat["other_count"]

    def _extract_temporal_features(self, features_dict: Dict):
        """Extract time-based features"""
        logger.debug("Extracting temporal features...")

        target_day_of_week = self.target_date.weekday()
        target_day_of_month = self.target_date.day
        target_week_of_month = ((self.target_date.day - 1) // 7) + 1
        target_month = self.target_date.month

        # Day of week patterns (look at same day of week historically)
        same_day_stats = (
            NumberFrequencyStats.objects.filter(
                date__lte=self.reference_date, day_of_week=target_day_of_week
            )
            .values("number")
            .annotate(count=Count("id"), avg_count=Avg("id"))
        )

        same_day_dict = {stat["number"]: stat for stat in same_day_stats}

        # Month patterns
        same_month_stats = (
            NumberFrequencyStats.objects.filter(
                date__lte=self.reference_date, month=target_month
            )
            .values("number")
            .annotate(count=Count("id"))
        )

        same_month_dict = {stat["number"]: stat for stat in same_month_stats}

        for number in features_dict.keys():
            # Day of week features
            same_day_stat = same_day_dict.get(number, {"count": 0})
            features_dict[number]["same_weekday_freq"] = same_day_stat["count"]

            # Month features
            same_month_stat = same_month_dict.get(number, {"count": 0})
            features_dict[number]["same_month_freq"] = same_month_stat["count"]

            # Calendar features
            features_dict[number]["target_day_of_week"] = target_day_of_week
            features_dict[number]["target_day_of_month"] = target_day_of_month
            features_dict[number]["target_week_of_month"] = target_week_of_month
            features_dict[number]["target_month"] = target_month
            features_dict[number]["is_month_start"] = (
                1 if target_day_of_month <= 5 else 0
            )
            features_dict[number]["is_month_end"] = (
                1 if target_day_of_month >= 25 else 0
            )

    def _extract_sequential_features(self, features_dict: Dict):
        """Extract sequence-based features"""
        logger.debug("Extracting sequential features...")

        # Get recent lottery results
        recent_results = KetQuaXoSo.objects.filter(
            ngay__lte=self.reference_date
        ).order_by("-ngay")[
            :30
        ]  # Last 30 results

        # Track last appearance and gaps
        number_last_seen = {}
        number_streaks = defaultdict(int)
        number_gaps = defaultdict(list)

        for i, result in enumerate(recent_results):
            numbers_today = result.get_all_2digit_numbers()
            days_ago = i

            for number in numbers_today:
                if number not in number_last_seen:
                    number_last_seen[number] = days_ago

            # Track consecutive appearances
            if i > 0:
                prev_result = recent_results[i - 1]
                prev_numbers = prev_result.get_all_2digit_numbers()

                for number in numbers_today:
                    if number in prev_numbers:
                        number_streaks[number] += 1
                    else:
                        number_streaks[number] = 1

        # Calculate gap statistics
        for number in features_dict.keys():
            features_dict[number]["days_since_last"] = number_last_seen.get(number, 999)
            features_dict[number]["recent_streak"] = number_streaks.get(number, 0)
            features_dict[number]["appeared_recently"] = (
                1 if number_last_seen.get(number, 999) <= 7 else 0
            )

    def _extract_statistical_features(self, features_dict: Dict):
        """Extract statistical pattern features"""
        logger.debug("Extracting statistical features...")

        # Get comprehensive historical data
        historical_data = KetQuaXoSo.objects.filter(
            ngay__lte=self.reference_date
        ).order_by("-ngay")[
            :365
        ]  # Last year of data

        # Collect all number appearances with dates
        number_appearances = defaultdict(list)
        all_daily_numbers = []

        for result in historical_data:
            numbers = result.get_all_2digit_numbers()
            all_daily_numbers.append(numbers)

            for number in numbers:
                number_appearances[number].append(result.ngay)

        # Calculate statistical features for each number
        for number in features_dict.keys():
            appearances = number_appearances.get(number, [])
            appearances.sort(reverse=True)  # Most recent first

            if len(appearances) >= 2:
                # Calculate gaps between appearances
                gaps = [
                    (appearances[i - 1] - appearances[i]).days
                    for i in range(1, len(appearances))
                ]

                features_dict[number]["avg_gap"] = np.mean(gaps) if gaps else 0
                features_dict[number]["gap_std"] = np.std(gaps) if gaps else 0
                features_dict[number]["min_gap"] = min(gaps) if gaps else 0
                features_dict[number]["max_gap"] = max(gaps) if gaps else 0
                features_dict[number]["gap_consistency"] = (
                    1 / (np.std(gaps) + 1) if gaps else 0
                )
            else:
                features_dict[number]["avg_gap"] = 0
                features_dict[number]["gap_std"] = 0
                features_dict[number]["min_gap"] = 0
                features_dict[number]["max_gap"] = 0
                features_dict[number]["gap_consistency"] = 0

            # Trend analysis (is frequency increasing or decreasing?)
            recent_30d = sum(
                1 for date in appearances if (self.reference_date - date).days <= 30
            )
            older_30d = sum(
                1
                for date in appearances
                if 30 < (self.reference_date - date).days <= 60
            )

            features_dict[number]["trend_30d"] = recent_30d - older_30d
            features_dict[number]["momentum"] = recent_30d / max(older_30d, 1)

    def _extract_cyclical_features(self, features_dict: Dict):
        """Extract cyclical pattern features"""
        logger.debug("Extracting cyclical features...")

        # Analyze if numbers follow cyclical patterns
        for number in features_dict.keys():
            appearances = NumberFrequencyStats.objects.filter(
                number=number, date__lte=self.reference_date
            ).order_by("-date")[
                :50
            ]  # Last 50 appearances

            if len(appearances) >= 3:
                gaps = []
                prev_date = None

                for appearance in appearances:
                    if prev_date:
                        gap = (prev_date - appearance.date).days
                        gaps.append(gap)
                    prev_date = appearance.date

                if gaps:
                    # Cyclical indicators
                    features_dict[number]["cycle_regularity"] = 1 / (np.std(gaps) + 1)
                    features_dict[number]["predicted_next_gap"] = np.mean(gaps)

                    # Check if we're in expected appearance window
                    if appearances:
                        days_since = (self.reference_date - appearances[0].date).days
                        expected_gap = np.mean(gaps)
                        features_dict[number]["cycle_probability"] = (
                            max(0, 1 - abs(days_since - expected_gap) / expected_gap)
                            if expected_gap > 0
                            else 0
                        )
                    else:
                        features_dict[number]["cycle_probability"] = 0
                else:
                    features_dict[number]["cycle_regularity"] = 0
                    features_dict[number]["predicted_next_gap"] = 0
                    features_dict[number]["cycle_probability"] = 0
            else:
                features_dict[number]["cycle_regularity"] = 0
                features_dict[number]["predicted_next_gap"] = 0
                features_dict[number]["cycle_probability"] = 0

    def _extract_position_features(self, features_dict: Dict):
        """Extract features based on number position and digit analysis"""
        logger.debug("Extracting position-based features...")

        for number in features_dict.keys():
            if len(number) == 2:
                first_digit = int(number[0])
                second_digit = int(number[1])

                # Digit-based features
                features_dict[number]["first_digit"] = first_digit
                features_dict[number]["second_digit"] = second_digit
                features_dict[number]["digit_sum"] = first_digit + second_digit
                features_dict[number]["digit_diff"] = abs(first_digit - second_digit)
                features_dict[number]["is_double"] = (
                    1 if first_digit == second_digit else 0
                )
                features_dict[number]["is_ascending"] = (
                    1 if first_digit < second_digit else 0
                )
                features_dict[number]["is_descending"] = (
                    1 if first_digit > second_digit else 0
                )

                # Number properties
                features_dict[number]["is_even"] = 1 if int(number) % 2 == 0 else 0
                features_dict[number]["is_prime"] = (
                    1 if self._is_prime(int(number)) else 0
                )
                features_dict[number]["number_value"] = int(number)

                # Digit frequency in historical data
                first_digit_freq = NumberFrequencyStats.objects.filter(
                    number__startswith=str(first_digit), date__lte=self.reference_date
                ).count()

                second_digit_freq = NumberFrequencyStats.objects.filter(
                    number__endswith=str(second_digit), date__lte=self.reference_date
                ).count()

                features_dict[number]["first_digit_popularity"] = first_digit_freq
                features_dict[number]["second_digit_popularity"] = second_digit_freq

    def _is_prime(self, n: int) -> bool:
        """Check if a number is prime"""
        if n < 2:
            return False
        for i in range(2, int(n**0.5) + 1):
            if n % i == 0:
                return False
        return True

    def get_feature_names(self) -> List[str]:
        """Get list of all feature names"""
        if "complete_features" in self._feature_cache:
            return list(self._feature_cache["complete_features"].columns)

        # Generate sample to get feature names
        sample_df = self.extract_features_for_date(use_cache=False)
        return list(sample_df.columns)

    def get_feature_importance_groups(self) -> Dict[str, List[str]]:
        """Group features by type for analysis"""
        feature_names = self.get_feature_names()

        groups = {
            "frequency": [f for f in feature_names if "freq" in f],
            "temporal": [
                f
                for f in feature_names
                if any(x in f for x in ["day", "month", "week"])
            ],
            "sequential": [
                f
                for f in feature_names
                if any(x in f for x in ["since", "streak", "gap"])
            ],
            "statistical": [
                f
                for f in feature_names
                if any(x in f for x in ["avg", "std", "trend", "momentum"])
            ],
            "cyclical": [f for f in feature_names if "cycle" in f],
            "positional": [
                f
                for f in feature_names
                if any(x in f for x in ["digit", "prime", "even", "double"])
            ],
        }

        return groups


class DataLeakageValidator:
    """Validate that no data leakage occurs in feature extraction"""

    @staticmethod
    def validate_prediction_request(target_date, context="prediction"):
        """
        Validate prediction request based on context

        Args:
            target_date: Target date to validate
            context: 'prediction', 'training', 'evaluation', 'backtesting', 'validation'
        """
        current_date = datetime.now().date()

        # Get data availability first
        from results.models import KetQuaXoSo

        try:
            latest_available = (
                KetQuaXoSo.objects.values_list("ngay", flat=True)
                .order_by("-ngay")
                .first()
            )
        except Exception:
            latest_available = None

        # Context-specific validation
        if context == "prediction":
            # Real predictions - strict enforcement
            if target_date <= current_date:
                logger.warning(f"Predicting for past/current date {target_date}")

            if latest_available and target_date <= latest_available:
                raise ValueError(
                    f"Data leakage detected! Target date {target_date} has data available. "
                    f"Latest available: {latest_available}"
                )

        elif context in ["evaluation", "backtesting", "training"]:
            # Historical evaluation - allow with info logging only
            if latest_available and target_date <= latest_available:
                logger.debug(
                    f"Historical evaluation for {target_date} (data available until {latest_available})"
                )

        elif context == "validation":
            # Model validation during training - suppress warnings completely
            pass

        else:
            # Unknown context - log warning
            logger.warning(f"Unknown validation context: {context}")

    @staticmethod
    def validate_training_date(prediction_date, latest_available):
        if prediction_date <= latest_available:  # Ngày dự đoán phải LỚN Hơn ngày có sẵn
            raise ValueError(
                f"Data leakage detected! Prediction date {prediction_date} must be AFTER "
                f"latest training data ({latest_available})"
            )

    @staticmethod
    def validate_training_data(start_date, end_date):
        current_date = datetime.now().date()
        if end_date > current_date:
            raise ValueError(f"Training end date {end_date} cannot be in the future")

        # Kiểm tra tính liên tục của dữ liệu
        from results.models import KetQuaXoSo

        date_counts = (
            KetQuaXoSo.objects.filter(ngay__gte=start_date, ngay__lte=end_date)
            .dates("ngay", "day")
            .count()
        )

        expected_days = (end_date - start_date).days + 1
        if date_counts < expected_days * 0.9:  # Cho phép thiếu tối đa 10% ngày
            logger.warning(
                f"Data missing for {(expected_days - date_counts)} days in training period"
            )

    @staticmethod
    def get_safe_reference_date(prediction_date: datetime.date) -> datetime.date:
        """Get the latest safe date to use as reference for features"""
        # Find the latest available data before prediction date
        latest_safe = KetQuaXoSo.objects.filter(ngay__lt=prediction_date).aggregate(
            latest=Max("ngay")
        )["latest"]

        if not latest_safe:
            raise ValueError("No historical data available for feature extraction")

        return latest_safe
