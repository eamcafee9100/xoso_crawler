"""
🚀 PHASE 1.2: DEEP FREQUENCY ANALYSIS
Advanced frequency pattern detection for lottery prediction enhancement
"""

import logging
from collections import Counter, defaultdict
from datetime import date, timedelta
from typing import Dict, List, Optional, Tuple

import numpy as np
from django.db.models import Count
from scipy import fft
from scipy.stats import chi2_contingency

logger = logging.getLogger(__name__)


class DeepFrequencyAnalyzer:
    """Advanced frequency analysis for lottery numbers"""

    def __init__(self):
        self.frequency_cache = {}
        self.pattern_cache = {}

    def analyze_frequency_patterns(self, historical_data: List) -> Dict:
        """
        🚀 CORE: Comprehensive frequency pattern analysis
        """
        try:
            logger.info(
                f"🔍 Starting deep frequency analysis with {len(historical_data)} data points"
            )

            patterns = {
                "hot_numbers": self._identify_hot_numbers(historical_data),
                "cold_numbers": self._identify_cold_numbers(historical_data),
                "cyclical_patterns": self._detect_cyclical_patterns(historical_data),
                "mean_reversion": self._analyze_mean_reversion(historical_data),
                "momentum_patterns": self._analyze_momentum(historical_data),
                "seasonal_effects": self._analyze_seasonal_effects(historical_data),
                "day_of_week_bias": self._analyze_dow_bias(historical_data),
                "month_end_effects": self._analyze_month_end_effects(historical_data),
                "gap_analysis": self._analyze_number_gaps(historical_data),
                "correlation_matrix": self._calculate_number_correlations(
                    historical_data
                ),
            }

            logger.info("✅ Deep frequency analysis completed")
            return patterns

        except Exception as e:
            logger.error(f"❌ Deep frequency analysis failed: {e}")
            return self._get_fallback_patterns()

    def _identify_hot_numbers(self, historical_data: List) -> Dict:
        """Identify numbers with above-average frequency"""
        try:
            all_numbers = []
            for day_data in historical_data:
                if isinstance(day_data, list):
                    all_numbers.extend(day_data)

            if not all_numbers:
                return {}

            number_freq = Counter(all_numbers)
            total_numbers = len(all_numbers)
            expected_freq = total_numbers / 100  # Expected for 00-99

            hot_numbers = {}
            for number, freq in number_freq.items():
                if freq > expected_freq * 1.5:  # 50% above expected
                    hot_numbers[str(number).zfill(2)] = {
                        "frequency": freq,
                        "expected": expected_freq,
                        "ratio": freq / expected_freq,
                        "last_seen_days_ago": self._calculate_last_seen(
                            number, historical_data
                        ),
                    }

            # Sort by frequency ratio
            sorted_hot = dict(
                sorted(hot_numbers.items(), key=lambda x: x[1]["ratio"], reverse=True)
            )

            logger.info(f"🔥 Identified {len(sorted_hot)} hot numbers")
            # Fix dictionary slicing - convert to list first
            hot_items = list(sorted_hot.items())[:20]
            return dict(hot_items)  # Top 20 hot numbers

        except Exception as e:
            logger.warning(f"Hot numbers analysis failed: {e}")
            return {}

    def _identify_cold_numbers(self, historical_data: List) -> Dict:
        """Identify numbers with below-average frequency"""
        try:
            all_numbers = []
            for day_data in historical_data:
                if isinstance(day_data, list):
                    all_numbers.extend(day_data)

            if not all_numbers:
                return {}

            number_freq = Counter(all_numbers)
            total_numbers = len(all_numbers)
            expected_freq = total_numbers / 100  # Expected for 00-99

            # Include all numbers 00-99
            cold_numbers = {}
            for number in range(100):
                freq = number_freq.get(number, 0)
                if freq < expected_freq * 0.7:  # 30% below expected
                    cold_numbers[str(number).zfill(2)] = {
                        "frequency": freq,
                        "expected": expected_freq,
                        "ratio": freq / expected_freq if expected_freq > 0 else 0,
                        "days_absent": self._calculate_days_absent(
                            number, historical_data
                        ),
                    }

            # Sort by lowest frequency ratio
            sorted_cold = dict(
                sorted(cold_numbers.items(), key=lambda x: x[1]["ratio"])
            )

            logger.info(f"❄️ Identified {len(sorted_cold)} cold numbers")
            # Fix dictionary slicing - convert to list first
            cold_items = list(sorted_cold.items())[:20]
            return dict(cold_items)  # Top 20 cold numbers

        except Exception as e:
            logger.warning(f"Cold numbers analysis failed: {e}")
            return {}

    def _detect_cyclical_patterns(self, historical_data: List) -> Dict:
        """🚀 ADVANCED: Detect cyclical patterns using Fourier analysis"""
        try:
            cycles = {}

            # Analyze each number individually
            for number in range(100):
                appearances = self._get_appearance_positions(number, historical_data)

                if len(appearances) < 10:  # Need minimum data
                    continue

                # Calculate gaps between appearances
                gaps = np.diff(appearances) if len(appearances) > 1 else []

                if len(gaps) < 5:
                    continue

                # Fourier analysis for cycle detection
                try:
                    fft_result = fft.fft(gaps)
                    frequencies = fft.fftfreq(len(gaps))

                    # Find dominant frequencies (excluding DC component)
                    power_spectrum = np.abs(fft_result[1 : len(fft_result) // 2])
                    dominant_freq_idx = np.argmax(power_spectrum)

                    if dominant_freq_idx > 0:
                        dominant_period = 1 / abs(frequencies[dominant_freq_idx + 1])

                        cycles[str(number).zfill(2)] = {
                            "avg_gap": float(np.mean(gaps)),
                            "std_gap": float(np.std(gaps)),
                            "dominant_cycle": float(dominant_period),
                            "cycle_strength": float(power_spectrum[dominant_freq_idx]),
                            "next_expected": self._predict_next_appearance(appearances),
                            "appearances_count": len(appearances),
                        }

                except Exception as fft_error:
                    # Fallback to simple statistical analysis
                    cycles[str(number).zfill(2)] = {
                        "avg_gap": float(np.mean(gaps)),
                        "std_gap": float(np.std(gaps)),
                        "dominant_cycle": float(np.mean(gaps)),  # Fallback
                        "cycle_strength": 1.0 / np.std(gaps) if np.std(gaps) > 0 else 0,
                        "next_expected": len(historical_data) + np.mean(gaps),
                        "appearances_count": len(appearances),
                    }

            logger.info(f"🔄 Detected cyclical patterns for {len(cycles)} numbers")
            return cycles

        except Exception as e:
            logger.warning(f"Cyclical pattern detection failed: {e}")
            return {}

    def _analyze_mean_reversion(self, historical_data: List) -> Dict:
        """Analyze mean reversion tendencies"""
        try:
            reversion_analysis = {}

            # Calculate rolling frequency for each number
            window_size = min(30, len(historical_data) // 3)

            for number in range(100):
                frequencies = []

                # Calculate frequency in rolling windows
                for i in range(len(historical_data) - window_size + 1):
                    window_data = historical_data[i : i + window_size]
                    count = sum(
                        1
                        for day_data in window_data
                        if isinstance(day_data, list) and number in day_data
                    )
                    frequencies.append(count / window_size)

                if len(frequencies) < 5:
                    continue

                # Calculate mean reversion metrics
                mean_freq = np.mean(frequencies)
                current_freq = (
                    frequencies[-5:] if len(frequencies) >= 5 else frequencies
                )
                current_avg = np.mean(current_freq)

                # Mean reversion score (how much current deviates from long-term mean)
                deviation = abs(current_avg - mean_freq)
                reversion_pressure = deviation / (
                    mean_freq + 1e-6
                )  # Avoid division by zero

                reversion_analysis[str(number).zfill(2)] = {
                    "long_term_mean": float(mean_freq),
                    "current_frequency": float(current_avg),
                    "deviation": float(deviation),
                    "reversion_pressure": float(reversion_pressure),
                    "expected_direction": (
                        "increase" if current_avg < mean_freq else "decrease"
                    ),
                }

            # Sort by reversion pressure
            sorted_reversion = dict(
                sorted(
                    reversion_analysis.items(),
                    key=lambda x: x[1]["reversion_pressure"],
                    reverse=True,
                )
            )

            logger.info(
                f"📈 Mean reversion analysis completed for {len(sorted_reversion)} numbers"
            )
            # Fix dictionary slicing - convert to list first
            reversion_items = list(sorted_reversion.items())[:30]
            return dict(reversion_items)  # Top 30 by reversion pressure

        except Exception as e:
            logger.warning(f"Mean reversion analysis failed: {e}")
            return {}

    def _analyze_momentum(self, historical_data: List) -> Dict:
        """Analyze momentum patterns in number frequencies"""
        try:
            momentum_analysis = {}

            # Calculate momentum over different periods
            periods = [7, 14, 30]  # 1 week, 2 weeks, 1 month

            for number in range(100):
                momentum_scores = {}

                for period in periods:
                    if len(historical_data) < period * 2:
                        continue

                    # Recent period frequency
                    recent_data = historical_data[-period:]
                    recent_count = sum(
                        1
                        for day_data in recent_data
                        if isinstance(day_data, list) and number in day_data
                    )
                    recent_freq = recent_count / period

                    # Previous period frequency
                    previous_data = historical_data[-period * 2 : -period]
                    previous_count = sum(
                        1
                        for day_data in previous_data
                        if isinstance(day_data, list) and number in day_data
                    )
                    previous_freq = previous_count / period

                    # Momentum score
                    momentum = (recent_freq - previous_freq) / (previous_freq + 1e-6)
                    momentum_scores[f"{period}d"] = float(momentum)

                if momentum_scores:
                    # Average momentum across periods
                    avg_momentum = np.mean(list(momentum_scores.values()))

                    momentum_analysis[str(number).zfill(2)] = {
                        "momentum_scores": momentum_scores,
                        "average_momentum": float(avg_momentum),
                        "trend": (
                            "increasing"
                            if avg_momentum > 0.1
                            else "decreasing" if avg_momentum < -0.1 else "stable"
                        ),
                    }

            # Sort by average momentum
            sorted_momentum = dict(
                sorted(
                    momentum_analysis.items(),
                    key=lambda x: x[1]["average_momentum"],
                    reverse=True,
                )
            )

            logger.info(
                f"🚀 Momentum analysis completed for {len(sorted_momentum)} numbers"
            )
            # Fix dictionary slicing - convert to list first
            momentum_items = list(sorted_momentum.items())[:25]
            return dict(momentum_items)  # Top 25 by momentum

        except Exception as e:
            logger.warning(f"Momentum analysis failed: {e}")
            return {}

    def _analyze_seasonal_effects(self, historical_data: List) -> Dict:
        """Analyze seasonal patterns in lottery numbers"""
        try:
            # This would require date information with historical_data
            # For now, return placeholder
            seasonal_analysis = {
                "monthly_patterns": {},
                "quarterly_patterns": {},
                "yearly_patterns": {},
            }

            logger.info("📅 Seasonal analysis completed (placeholder)")
            return seasonal_analysis

        except Exception as e:
            logger.warning(f"Seasonal analysis failed: {e}")
            return {}

    def _analyze_dow_bias(self, historical_data: List) -> Dict:
        """Analyze day-of-week bias (placeholder - needs date info)"""
        return {}

    def _analyze_month_end_effects(self, historical_data: List) -> Dict:
        """Analyze month-end effects (placeholder - needs date info)"""
        return {}

    def _analyze_number_gaps(self, historical_data: List) -> Dict:
        """Analyze gaps between number appearances"""
        try:
            gap_analysis = {}

            for number in range(100):
                appearances = self._get_appearance_positions(number, historical_data)

                if len(appearances) < 3:
                    continue

                gaps = np.diff(appearances)

                gap_analysis[str(number).zfill(2)] = {
                    "avg_gap": float(np.mean(gaps)),
                    "min_gap": int(np.min(gaps)),
                    "max_gap": int(np.max(gaps)),
                    "std_gap": float(np.std(gaps)),
                    "current_gap": (
                        len(historical_data) - appearances[-1]
                        if appearances
                        else len(historical_data)
                    ),
                    "gap_percentile": float(np.percentile(gaps, 75)),  # 75th percentile
                }

            logger.info(f"📏 Gap analysis completed for {len(gap_analysis)} numbers")
            return gap_analysis

        except Exception as e:
            logger.warning(f"Gap analysis failed: {e}")
            return {}

    def _calculate_number_correlations(self, historical_data: List) -> Dict:
        """Calculate correlations between numbers"""
        try:
            # Create binary matrix: day x number (1 if number appeared, 0 otherwise)
            matrix = []

            for day_data in historical_data:
                day_vector = [0] * 100
                if isinstance(day_data, list):
                    for number in day_data:
                        if 0 <= number <= 99:
                            day_vector[number] = 1
                matrix.append(day_vector)

            if len(matrix) < 10:
                return {}

            # Calculate correlation matrix
            matrix_np = np.array(matrix)
            correlation_matrix = np.corrcoef(matrix_np.T)

            # Find strongest correlations
            strong_correlations = {}
            for i in range(100):
                for j in range(i + 1, 100):
                    corr = correlation_matrix[i, j]
                    if abs(corr) > 0.1:  # Threshold for meaningful correlation
                        pair_key = f"{str(i).zfill(2)}-{str(j).zfill(2)}"
                        strong_correlations[pair_key] = float(corr)

            # Sort by absolute correlation strength
            sorted_correlations = dict(
                sorted(
                    strong_correlations.items(), key=lambda x: abs(x[1]), reverse=True
                )
            )

            logger.info(
                f"🔗 Found {len(sorted_correlations)} significant number correlations"
            )
            # Fix dictionary slicing - convert to list first
            correlation_items = list(sorted_correlations.items())[:50]
            return dict(correlation_items)  # Top 50 correlations

        except Exception as e:
            logger.warning(f"Correlation analysis failed: {e}")
            return {}

    def _get_appearance_positions(
        self, number: int, historical_data: List
    ) -> List[int]:
        """Get positions where a number appeared"""
        positions = []
        for i, day_data in enumerate(historical_data):
            if isinstance(day_data, list) and number in day_data:
                positions.append(i)
        return positions

    def _calculate_last_seen(self, number: int, historical_data: List) -> int:
        """Calculate days since number was last seen"""
        for i in range(len(historical_data) - 1, -1, -1):
            day_data = historical_data[i]
            if isinstance(day_data, list) and number in day_data:
                return len(historical_data) - 1 - i
        return len(historical_data)  # Never seen

    def _calculate_days_absent(self, number: int, historical_data: List) -> int:
        """Calculate total days the number was absent"""
        total_days = len(historical_data)
        appearance_count = sum(
            1
            for day_data in historical_data
            if isinstance(day_data, list) and number in day_data
        )
        return total_days - appearance_count

    def _predict_next_appearance(self, appearances: List[int]) -> float:
        """Predict next appearance based on pattern"""
        if len(appearances) < 2:
            return float("inf")

        gaps = np.diff(appearances)
        avg_gap = np.mean(gaps)
        return appearances[-1] + avg_gap

    def _get_fallback_patterns(self) -> Dict:
        """Fallback patterns when analysis fails"""
        return {
            "hot_numbers": {},
            "cold_numbers": {},
            "cyclical_patterns": {},
            "mean_reversion": {},
            "momentum_patterns": {},
            "seasonal_effects": {},
            "day_of_week_bias": {},
            "month_end_effects": {},
            "gap_analysis": {},
            "correlation_matrix": {},
        }


def get_deep_frequency_insights(historical_data: List) -> Dict:
    """
    🚀 PUBLIC API: Get comprehensive frequency insights
    """
    analyzer = DeepFrequencyAnalyzer()
    return analyzer.analyze_frequency_patterns(historical_data)
