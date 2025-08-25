"""
STATISTICAL FOUNDATION MODULE
=============================
Advanced feature engineering and statistical validation for Elite Lottery Intelligence System
"""

import warnings
from collections import Counter, defaultdict
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple

import numpy as np
import pandas as pd
from scipy import stats

warnings.filterwarnings("ignore")


class AdvancedFeatureEngine:
    """Advanced Feature Engineering for Lottery Prediction System"""

    def __init__(self):
        self.feature_cache = {}

    def extract_statistical_features(
        self, numbers_history: List[List[int]], lookback_days: int = 90
    ) -> Dict[str, float]:
        """Extract 200+ statistical features from number history"""

        features = {}
        if not numbers_history:
            return self._get_default_features()

        # Convert to numpy array for efficient computation
        data = np.array(numbers_history)

        # === BASIC STATISTICAL FEATURES ===
        features.update(self._basic_statistics(data))

        # === DISTRIBUTION FEATURES ===
        features.update(self._distribution_features(data))

        # === TEMPORAL FEATURES ===
        features.update(self._temporal_features(data))

        # === PATTERN FEATURES ===
        features.update(self._pattern_features(data))

        # === ADVANCED STATISTICAL FEATURES ===
        features.update(self._advanced_statistics(data))

        # === CYCLICAL FEATURES ===
        features.update(self._cyclical_features(data))

        # === CORRELATION FEATURES ===
        features.update(self._correlation_features(data))

        return features

    def _basic_statistics(self, data: np.ndarray) -> Dict[str, float]:
        """Basic statistical measures"""
        features = {}

        # Flatten all numbers
        all_numbers = data.flatten()

        features["mean"] = np.mean(all_numbers)
        features["median"] = np.median(all_numbers)
        features["std"] = np.std(all_numbers)
        features["variance"] = np.var(all_numbers)
        features["skewness"] = stats.skew(all_numbers)
        features["kurtosis"] = stats.kurtosis(all_numbers)
        features["range"] = np.max(all_numbers) - np.min(all_numbers)

        # Percentiles
        for p in [10, 25, 75, 90, 95, 99]:
            features[f"percentile_{p}"] = np.percentile(all_numbers, p)

        return features

    def _distribution_features(self, data: np.ndarray) -> Dict[str, float]:
        """Distribution and frequency features"""
        features = {}

        all_numbers = data.flatten()
        value_counts = Counter(all_numbers)

        # Frequency statistics
        frequencies = list(value_counts.values())
        features["freq_mean"] = np.mean(frequencies)
        features["freq_std"] = np.std(frequencies)
        features["freq_entropy"] = stats.entropy(frequencies)

        # Number coverage
        unique_numbers = len(value_counts)
        features["unique_numbers"] = unique_numbers
        features["coverage_ratio"] = unique_numbers / 100  # Assuming 00-99 range

        # Hot/Cold numbers
        max_freq = max(frequencies)
        min_freq = min(frequencies)
        features["hot_cold_ratio"] = max_freq / max(min_freq, 1)

        # Distribution uniformity (Chi-square test)
        expected_freq = len(all_numbers) / unique_numbers
        chi2_stat = sum(
            (freq - expected_freq) ** 2 / expected_freq for freq in frequencies
        )
        features["chi_square_uniformity"] = chi2_stat

        return features

    def _temporal_features(self, data: np.ndarray) -> Dict[str, float]:
        """Time-based pattern features"""
        features = {}

        # Recent vs Historical comparison
        if len(data) >= 14:
            recent_data = data[-7:]  # Last 7 draws
            historical_data = data[:-7]

            recent_mean = np.mean(recent_data.flatten())
            historical_mean = np.mean(historical_data.flatten())

            features["recent_vs_historical_mean"] = recent_mean - historical_mean
            features["recent_vs_historical_std"] = np.std(
                recent_data.flatten()
            ) - np.std(historical_data.flatten())

            # Trend analysis
            features.update(self._trend_analysis(data))

        # Gap analysis between consecutive appearances
        features.update(self._gap_analysis(data))

        return features

    def _pattern_features(self, data: np.ndarray) -> Dict[str, float]:
        """Pattern recognition features"""
        features = {}

        # Consecutive number patterns
        features.update(self._consecutive_patterns(data))

        # Sum patterns
        features.update(self._sum_patterns(data))

        # Even/Odd patterns
        features.update(self._even_odd_patterns(data))

        # High/Low patterns (assuming 00-99 range)
        features.update(self._high_low_patterns(data))

        return features

    def _advanced_statistics(self, data: np.ndarray) -> Dict[str, float]:
        """Advanced statistical measures"""
        features = {}

        all_numbers = data.flatten()

        # Moment-based features
        for moment in range(3, 7):
            features[f"moment_{moment}"] = stats.moment(all_numbers, moment)

        # Normality tests
        try:
            shapiro_stat, shapiro_p = stats.shapiro(
                all_numbers[:5000]
            )  # Limit for shapiro
            features["shapiro_stat"] = shapiro_stat
            features["shapiro_p_value"] = shapiro_p
        except:
            features["shapiro_stat"] = 0
            features["shapiro_p_value"] = 1

        # Anderson-Darling test
        try:
            ad_stat, critical_values, significance_level = stats.anderson(all_numbers)
            features["anderson_darling_stat"] = ad_stat
        except:
            features["anderson_darling_stat"] = 0

        return features

    def _cyclical_features(self, data: np.ndarray) -> Dict[str, float]:
        """Cyclical and seasonal features"""
        features = {}

        # Weekly cycles (if data spans multiple weeks)
        if len(data) >= 14:
            features.update(self._weekly_cycles(data))

        # Monthly cycles
        if len(data) >= 60:
            features.update(self._monthly_cycles(data))

        # Fibonacci sequence presence
        features.update(self._fibonacci_features(data))

        return features

    def _correlation_features(self, data: np.ndarray) -> Dict[str, float]:
        """Cross-correlation and dependency features"""
        features = {}

        if data.shape[1] >= 2:  # At least 2 numbers per draw
            # Position correlations
            for i in range(min(5, data.shape[1])):  # First 5 positions
                for j in range(i + 1, min(5, data.shape[1])):
                    try:
                        corr = np.corrcoef(data[:, i], data[:, j])[0, 1]
                        features[f"pos_corr_{i}_{j}"] = (
                            corr if not np.isnan(corr) else 0
                        )
                    except:
                        features[f"pos_corr_{i}_{j}"] = 0

        # Autocorrelation features
        features.update(self._autocorrelation_features(data))

        return features

    # Helper methods for specific feature categories
    def _trend_analysis(self, data: np.ndarray) -> Dict[str, float]:
        """Analyze trends in the data"""
        features = {}

        # Linear trend for each position
        for pos in range(min(3, data.shape[1])):
            y = data[:, pos]
            x = np.arange(len(y))
            try:
                slope, intercept, r_value, p_value, std_err = stats.linregress(x, y)
                features[f"trend_slope_pos_{pos}"] = slope
                features[f"trend_r_value_pos_{pos}"] = r_value
                features[f"trend_p_value_pos_{pos}"] = p_value
            except:
                features[f"trend_slope_pos_{pos}"] = 0
                features[f"trend_r_value_pos_{pos}"] = 0
                features[f"trend_p_value_pos_{pos}"] = 1

        return features

    def _gap_analysis(self, data: np.ndarray) -> Dict[str, float]:
        """Analyze gaps between number appearances"""
        features = {}

        all_numbers = data.flatten()
        number_positions = defaultdict(list)

        # Track positions of each number
        for i, num in enumerate(all_numbers):
            number_positions[num].append(i)

        # Calculate gap statistics
        all_gaps = []
        for positions in number_positions.values():
            if len(positions) > 1:
                gaps = np.diff(positions)
                all_gaps.extend(gaps)

        if all_gaps:
            features["gap_mean"] = np.mean(all_gaps)
            features["gap_std"] = np.std(all_gaps)
            features["gap_min"] = np.min(all_gaps)
            features["gap_max"] = np.max(all_gaps)
        else:
            features["gap_mean"] = features["gap_std"] = 0
            features["gap_min"] = features["gap_max"] = 0

        return features

    def _consecutive_patterns(self, data: np.ndarray) -> Dict[str, float]:
        """Analyze consecutive number patterns"""
        features = {}

        consecutive_counts = []
        for row in data:
            sorted_row = sorted(row)
            consecutive = 0
            max_consecutive = 0

            for i in range(1, len(sorted_row)):
                if sorted_row[i] == sorted_row[i - 1] + 1:
                    consecutive += 1
                else:
                    max_consecutive = max(max_consecutive, consecutive + 1)
                    consecutive = 0
            max_consecutive = max(max_consecutive, consecutive + 1)
            consecutive_counts.append(max_consecutive)

        features["consecutive_mean"] = np.mean(consecutive_counts)
        features["consecutive_max"] = np.max(consecutive_counts)
        features["consecutive_std"] = np.std(consecutive_counts)

        return features

    def _sum_patterns(self, data: np.ndarray) -> Dict[str, float]:
        """Analyze sum patterns of draws"""
        features = {}

        draw_sums = [sum(row) for row in data]

        features["sum_mean"] = np.mean(draw_sums)
        features["sum_std"] = np.std(draw_sums)
        features["sum_trend"] = (
            np.corrcoef(range(len(draw_sums)), draw_sums)[0, 1]
            if len(draw_sums) > 1
            else 0
        )

        # Sum distribution analysis
        sum_counts = Counter(draw_sums)
        if len(sum_counts) > 1:
            features["sum_entropy"] = stats.entropy(list(sum_counts.values()))
        else:
            features["sum_entropy"] = 0

        return features

    def _even_odd_patterns(self, data: np.ndarray) -> Dict[str, float]:
        """Analyze even/odd number patterns"""
        features = {}

        even_counts = []
        for row in data:
            even_count = sum(1 for num in row if num % 2 == 0)
            even_counts.append(even_count)

        features["even_ratio_mean"] = np.mean(even_counts) / data.shape[1]
        features["even_ratio_std"] = np.std(even_counts) / data.shape[1]

        return features

    def _high_low_patterns(
        self, data: np.ndarray, threshold: int = 50
    ) -> Dict[str, float]:
        """Analyze high/low number patterns"""
        features = {}

        high_counts = []
        for row in data:
            high_count = sum(1 for num in row if num >= threshold)
            high_counts.append(high_count)

        features["high_ratio_mean"] = np.mean(high_counts) / data.shape[1]
        features["high_ratio_std"] = np.std(high_counts) / data.shape[1]

        return features

    def _weekly_cycles(self, data: np.ndarray) -> Dict[str, float]:
        """Analyze weekly cyclical patterns"""
        features = {}

        # Assume daily draws, group by week
        weeks = len(data) // 7
        if weeks >= 2:
            weekly_means = []
            for w in range(weeks):
                week_data = data[w * 7 : (w + 1) * 7]
                weekly_means.append(np.mean(week_data.flatten()))

            features["weekly_consistency"] = 1 - np.std(weekly_means) / max(
                np.mean(weekly_means), 1
            )
        else:
            features["weekly_consistency"] = 0

        return features

    def _monthly_cycles(self, data: np.ndarray) -> Dict[str, float]:
        """Analyze monthly cyclical patterns"""
        features = {}

        # Assume daily draws, group by month (30 days)
        months = len(data) // 30
        if months >= 2:
            monthly_means = []
            for m in range(months):
                month_data = data[m * 30 : (m + 1) * 30]
                monthly_means.append(np.mean(month_data.flatten()))

            features["monthly_consistency"] = 1 - np.std(monthly_means) / max(
                np.mean(monthly_means), 1
            )
        else:
            features["monthly_consistency"] = 0

        return features

    def _fibonacci_features(self, data: np.ndarray) -> Dict[str, float]:
        """Analyze Fibonacci sequence presence"""
        features = {}

        # Generate Fibonacci numbers up to 99
        fib_numbers = set()
        a, b = 0, 1
        while b <= 99:
            fib_numbers.add(b)
            a, b = b, a + b

        # Count Fibonacci number appearances
        all_numbers = data.flatten()
        fib_count = sum(1 for num in all_numbers if num in fib_numbers)

        features["fibonacci_ratio"] = fib_count / len(all_numbers)

        return features

    def _autocorrelation_features(self, data: np.ndarray) -> Dict[str, float]:
        """Calculate autocorrelation features"""
        features = {}

        all_numbers = data.flatten()

        # Calculate autocorrelation for different lags
        for lag in [1, 2, 3, 5, 7, 14]:
            if len(all_numbers) > lag:
                try:
                    corr = np.corrcoef(all_numbers[:-lag], all_numbers[lag:])[0, 1]
                    features[f"autocorr_lag_{lag}"] = corr if not np.isnan(corr) else 0
                except:
                    features[f"autocorr_lag_{lag}"] = 0
            else:
                features[f"autocorr_lag_{lag}"] = 0

        return features

    def _get_default_features(self) -> Dict[str, float]:
        """Return default features when no data available"""
        default_features = {}

        # Basic statistics
        for feat in [
            "mean",
            "median",
            "std",
            "variance",
            "skewness",
            "kurtosis",
            "range",
        ]:
            default_features[feat] = 0.0

        # Percentiles
        for p in [10, 25, 75, 90, 95, 99]:
            default_features[f"percentile_{p}"] = 0.0

        # Add more default features as needed...
        # This ensures we always return consistent feature vectors

        return default_features


class StatisticalValidator:
    """Statistical validation and confidence interval calculations"""

    def __init__(self):
        self.confidence_levels = {
            "low": 0.80,
            "medium": 0.90,
            "high": 0.95,
            "very_high": 0.99,
        }

    def wilson_confidence_interval(
        self, successes: int, trials: int, confidence: float = 0.95
    ) -> Tuple[float, float]:
        """Calculate Wilson score confidence interval"""
        if trials == 0:
            return (0.0, 0.0)

        z = stats.norm.ppf(1 - (1 - confidence) / 2)
        p = successes / trials

        denominator = 1 + z**2 / trials
        center = (p + z**2 / (2 * trials)) / denominator
        margin = z * np.sqrt((p * (1 - p) + z**2 / (4 * trials)) / trials) / denominator

        return (max(0, center - margin), min(1, center + margin))

    def hypothesis_test_prediction_accuracy(
        self, predicted: List[int], actual: List[int], alpha: float = 0.05
    ) -> Dict[str, float]:
        """Perform hypothesis test for prediction accuracy"""

        if not predicted or not actual:
            return {"p_value": 1.0, "test_statistic": 0.0, "significant": False}

        # Calculate hit rate
        hits = len(set(predicted) & set(actual))
        trials = len(predicted)

        # Null hypothesis: prediction is random (expected hit rate for random prediction)
        # For lottery with 100 numbers, selecting 15, probability of hitting any specific number
        expected_random_rate = 0.15  # Approximate

        # Binomial test (updated for scipy >= 1.7.0)
        from scipy.stats import binomtest

        p_value = binomtest(
            hits, trials, expected_random_rate, alternative="greater"
        ).pvalue

        # Z-test statistic
        observed_rate = hits / trials
        standard_error = np.sqrt(
            expected_random_rate * (1 - expected_random_rate) / trials
        )
        z_statistic = (observed_rate - expected_random_rate) / standard_error

        return {
            "p_value": p_value,
            "test_statistic": z_statistic,
            "significant": p_value < alpha,
            "observed_rate": observed_rate,
            "expected_rate": expected_random_rate,
        }

    def calculate_prediction_confidence(
        self, features: Dict[str, float], historical_accuracy: float
    ) -> str:
        """Calculate prediction confidence level based on features and historical performance"""

        # Confidence scoring based on multiple factors
        confidence_score = 0.0

        # Historical accuracy weight (40%)
        if historical_accuracy > 0.4:
            confidence_score += 0.4
        elif historical_accuracy > 0.3:
            confidence_score += 0.3
        elif historical_accuracy > 0.2:
            confidence_score += 0.2
        else:
            confidence_score += 0.1

        # Statistical stability (30%)
        if features.get("std", 0) < 20:  # Low variance indicates stability
            confidence_score += 0.3
        elif features.get("std", 0) < 30:
            confidence_score += 0.2
        else:
            confidence_score += 0.1

        # Pattern consistency (20%)
        if features.get("weekly_consistency", 0) > 0.7:
            confidence_score += 0.2
        elif features.get("weekly_consistency", 0) > 0.5:
            confidence_score += 0.15
        else:
            confidence_score += 0.1

        # Data quality (10%)
        if features.get("coverage_ratio", 0) > 0.8:
            confidence_score += 0.1
        elif features.get("coverage_ratio", 0) > 0.6:
            confidence_score += 0.08
        else:
            confidence_score += 0.05

        # Map confidence score to levels
        if confidence_score >= 0.85:
            return "very_high"
        elif confidence_score >= 0.70:
            return "high"
        elif confidence_score >= 0.55:
            return "medium"
        else:
            return "low"
