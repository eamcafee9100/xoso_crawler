#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
🚀 ENHANCED DEEP FREQUENCY ANALYZER V2
Integration with NumberFrequencyStats model for advanced analysis
"""

import logging
from collections import Counter, defaultdict
from datetime import date, datetime, timedelta
from typing import Dict, List, Optional, Tuple

import numpy as np
from django.db.models import Avg, Count, Q
from scipy import fft
from scipy.stats import chi2_contingency, chisquare

from results.models import NumberFrequencyStats

logger = logging.getLogger(__name__)


class EnhancedDeepFrequencyAnalyzer:
    """
    🚀 ENHANCED VERSION: Advanced frequency analysis with database integration
    """

    def __init__(self):
        self.frequency_cache = {}
        self.pattern_cache = {}
        self.statistical_cache = {}

    def analyze_frequency_patterns_enhanced(
        self,
        start_date: date = None,
        end_date: date = None,
        significance_level: float = 0.05,
    ) -> Dict:
        """
        🚀 ENHANCED CORE: Comprehensive frequency pattern analysis with DB integration

        Args:
            start_date: Analysis start date (default: 6 months ago)
            end_date: Analysis end date (default: today)
            significance_level: Statistical significance threshold (default: 0.05)

        Returns:
            Dict: Comprehensive frequency analysis results
        """
        try:
            # Set default date range
            if not end_date:
                end_date = date.today()
            if not start_date:
                start_date = end_date - timedelta(days=180)  # 6 months

            logger.info(
                f"🔍 Starting enhanced frequency analysis: {start_date} to {end_date}"
            )

            # Get base dataset
            base_queryset = NumberFrequencyStats.objects.filter(
                date__range=[start_date, end_date]
            )

            total_records = base_queryset.count()
            if total_records < 30:
                logger.warning(f"⚠️ Insufficient data: only {total_records} records")
                return self._get_fallback_patterns()

            logger.info(f"📊 Analyzing {total_records} frequency records")

            # Comprehensive analysis suite
            patterns = {
                "analysis_metadata": {
                    "start_date": start_date.isoformat(),
                    "end_date": end_date.isoformat(),
                    "total_records": total_records,
                    "significance_level": significance_level,
                    "analysis_timestamp": datetime.now().isoformat(),
                },
                # ✅ Enhanced core analyses
                "hot_numbers": self._identify_hot_numbers_statistical(
                    base_queryset, significance_level
                ),
                "cold_numbers": self._identify_cold_numbers_statistical(
                    base_queryset, significance_level
                ),
                "cyclical_patterns": self._detect_cyclical_patterns_enhanced(
                    base_queryset
                ),
                "mean_reversion": self._analyze_mean_reversion_enhanced(base_queryset),
                "momentum_patterns": self._analyze_momentum_enhanced(base_queryset),
                # 🚀 NEW: Date-aware analyses (previously impossible)
                "seasonal_effects": self._analyze_seasonal_effects_enhanced(
                    base_queryset
                ),
                "day_of_week_bias": self._analyze_dow_bias_enhanced(base_queryset),
                "month_end_effects": self._analyze_month_end_effects_enhanced(
                    base_queryset
                ),
                "prize_position_intelligence": self._analyze_prize_position_patterns(
                    base_queryset
                ),
                # ✅ Enhanced correlation analysis
                "gap_analysis": self._analyze_number_gaps_enhanced(base_queryset),
                "correlation_matrix": self._calculate_number_correlations_enhanced(
                    base_queryset
                ),
                # 🆕 Advanced statistical analyses
                "statistical_tests": self._perform_statistical_tests(
                    base_queryset, significance_level
                ),
                "trend_analysis": self._analyze_trends_enhanced(base_queryset),
                "risk_assessment": self._assess_prediction_risks(base_queryset),
            }

            logger.info("✅ Enhanced deep frequency analysis completed")
            return patterns

        except Exception as e:
            logger.error(f"❌ Enhanced frequency analysis failed: {e}")
            return self._get_fallback_patterns()

    def _identify_hot_numbers_statistical(
        self, queryset, significance_level: float = 0.05
    ) -> Dict:
        """
        🔥 ENHANCED: Statistical hot number identification with chi-square testing
        """
        try:
            hot_numbers = {}
            total_days = queryset.values("date").distinct().count()

            if total_days == 0:
                return {}

            # Expected frequency per number (assuming uniform distribution)
            expected_freq_per_number = total_days * 0.01  # 1% chance per number per day

            for number in range(100):
                num_str = str(number).zfill(2)

                # Count actual appearances
                number_stats = queryset.filter(number=num_str)
                observed_freq = number_stats.count()

                if observed_freq == 0:
                    continue

                # Chi-square goodness of fit test
                try:
                    chi2_stat, p_value = chisquare(
                        [observed_freq], [expected_freq_per_number]
                    )

                    # Statistical significance test
                    is_significant = p_value < significance_level
                    is_hot = (
                        observed_freq > expected_freq_per_number * 1.2
                    )  # 20% above expected

                    if is_significant and is_hot:
                        # Additional metrics
                        recent_appearances = number_stats.filter(
                            date__gte=date.today() - timedelta(days=30)
                        ).count()

                        last_appearance = number_stats.order_by("-date").first()
                        days_since_last = (
                            (date.today() - last_appearance.date).days
                            if last_appearance
                            else 999
                        )

                        # Prize position analysis
                        special_appearances = number_stats.filter(
                            appeared_in_special=True
                        ).count()
                        first_appearances = number_stats.filter(
                            appeared_in_first=True
                        ).count()

                        hot_numbers[num_str] = {
                            "frequency": observed_freq,
                            "expected_frequency": round(expected_freq_per_number, 2),
                            "frequency_ratio": round(
                                observed_freq / expected_freq_per_number, 2
                            ),
                            "chi2_statistic": round(chi2_stat, 4),
                            "p_value": round(p_value, 6),
                            "statistical_significance": (
                                "significant" if is_significant else "not_significant"
                            ),
                            "recent_momentum": recent_appearances,
                            "days_since_last_appearance": days_since_last,
                            "special_prize_rate": (
                                round(special_appearances / observed_freq, 2)
                                if observed_freq > 0
                                else 0
                            ),
                            "first_prize_rate": (
                                round(first_appearances / observed_freq, 2)
                                if observed_freq > 0
                                else 0
                            ),
                            "hotness_score": round(
                                (observed_freq / expected_freq_per_number)
                                * (1 - p_value)
                                * (1 + recent_appearances / 30),
                                2,
                            ),
                        }

                except Exception as chi2_error:
                    logger.warning(
                        f"Chi-square test failed for number {num_str}: {chi2_error}"
                    )
                    continue

            # Sort by hotness score
            sorted_hot = dict(
                sorted(
                    hot_numbers.items(),
                    key=lambda x: x[1]["hotness_score"],
                    reverse=True,
                )
            )

            logger.info(
                f"🔥 Identified {len(sorted_hot)} statistically significant hot numbers"
            )
            return dict(list(sorted_hot.items())[:20])  # Top 20

        except Exception as e:
            logger.warning(f"Statistical hot numbers analysis failed: {e}")
            return {}

    def _identify_cold_numbers_statistical(
        self, queryset, significance_level: float = 0.05
    ) -> Dict:
        """
        ❄️ ENHANCED: Statistical cold number identification
        """
        try:
            cold_numbers = {}
            total_days = queryset.values("date").distinct().count()

            if total_days == 0:
                return {}

            expected_freq_per_number = total_days * 0.01

            for number in range(100):
                num_str = str(number).zfill(2)

                number_stats = queryset.filter(number=num_str)
                observed_freq = number_stats.count()

                # Chi-square test for under-representation
                try:
                    if expected_freq_per_number > 0:
                        chi2_stat, p_value = chisquare(
                            [max(1, observed_freq)],  # Avoid zero for chi-square
                            [expected_freq_per_number],
                        )

                        is_significant = p_value < significance_level
                        is_cold = (
                            observed_freq < expected_freq_per_number * 0.8
                        )  # 20% below expected

                        if is_cold:  # Don't require significance for cold numbers
                            # Days since last appearance
                            last_appearance = number_stats.order_by("-date").first()
                            days_absent = (
                                (date.today() - last_appearance.date).days
                                if last_appearance
                                else total_days
                            )

                            # Absence streak analysis
                            absence_periods = self._calculate_absence_periods(
                                num_str, queryset
                            )

                            cold_numbers[num_str] = {
                                "frequency": observed_freq,
                                "expected_frequency": round(
                                    expected_freq_per_number, 2
                                ),
                                "frequency_ratio": (
                                    round(observed_freq / expected_freq_per_number, 2)
                                    if expected_freq_per_number > 0
                                    else 0
                                ),
                                "chi2_statistic": round(chi2_stat, 4),
                                "p_value": round(p_value, 6),
                                "days_absent": days_absent,
                                "absence_streak": absence_periods["current_streak"],
                                "max_absence_period": absence_periods["max_period"],
                                "avg_absence_period": absence_periods["avg_period"],
                                "reversion_pressure": (
                                    round(
                                        (expected_freq_per_number - observed_freq)
                                        / expected_freq_per_number
                                        * (1 + days_absent / total_days),
                                        2,
                                    )
                                    if expected_freq_per_number > 0
                                    else 0
                                ),
                                "coldness_score": (
                                    round(
                                        (expected_freq_per_number - observed_freq)
                                        / expected_freq_per_number
                                        * (1 + days_absent / 30),
                                        2,
                                    )
                                    if expected_freq_per_number > 0
                                    else 0
                                ),
                            }

                except Exception as chi2_error:
                    logger.warning(
                        f"Chi-square test failed for cold number {num_str}: {chi2_error}"
                    )
                    continue

            # Sort by coldness score
            sorted_cold = dict(
                sorted(
                    cold_numbers.items(),
                    key=lambda x: x[1]["coldness_score"],
                    reverse=True,
                )
            )

            logger.info(f"❄️ Identified {len(sorted_cold)} cold numbers")
            return dict(list(sorted_cold.items())[:20])  # Top 20

        except Exception as e:
            logger.warning(f"Statistical cold numbers analysis failed: {e}")
            return {}

    def _analyze_seasonal_effects_enhanced(self, queryset) -> Dict:
        """
        📅 NEW FEATURE: Comprehensive seasonal analysis (previously impossible)
        """
        try:
            seasonal_patterns = {
                "monthly_patterns": {},
                "quarterly_patterns": {},
                "day_of_week_patterns": {},
                "day_of_month_patterns": {},
                "week_of_month_patterns": {},
            }

            # Monthly patterns
            for month in range(1, 13):
                month_stats = queryset.filter(month=month)
                month_count = month_stats.count()
                unique_numbers = month_stats.values("number").distinct().count()

                # Top numbers for this month
                top_numbers = (
                    month_stats.values("number")
                    .annotate(count=Count("number"))
                    .order_by("-count")[:10]
                )

                seasonal_patterns["monthly_patterns"][month] = {
                    "total_appearances": month_count,
                    "unique_numbers": unique_numbers,
                    "diversity_score": unique_numbers / 100.0,  # 0-1 score
                    "top_numbers": [
                        {
                            "number": item["number"],
                            "count": item["count"],
                            "month_dominance": round(item["count"] / month_count, 3),
                        }
                        for item in top_numbers
                    ],
                }

            # Day of week patterns
            for dow in range(7):
                dow_stats = queryset.filter(day_of_week=dow)
                dow_count = dow_stats.count()

                if dow_count > 0:
                    # Prize position bias by day of week
                    special_rate = (
                        dow_stats.filter(appeared_in_special=True).count() / dow_count
                    )
                    first_rate = (
                        dow_stats.filter(appeared_in_first=True).count() / dow_count
                    )

                    seasonal_patterns["day_of_week_patterns"][dow] = {
                        "total_appearances": dow_count,
                        "special_prize_rate": round(special_rate, 3),
                        "first_prize_rate": round(first_rate, 3),
                        "day_name": [
                            "Monday",
                            "Tuesday",
                            "Wednesday",
                            "Thursday",
                            "Friday",
                            "Saturday",
                            "Sunday",
                        ][dow],
                    }

            # Day of month patterns (month-end effects)
            for day_range in [(1, 10), (11, 20), (21, 31)]:
                range_stats = queryset.filter(
                    day_of_month__gte=day_range[0], day_of_month__lte=day_range[1]
                )
                range_count = range_stats.count()

                range_name = f"days_{day_range[0]}_to_{day_range[1]}"
                seasonal_patterns["day_of_month_patterns"][range_name] = {
                    "total_appearances": range_count,
                    "period": f"{day_range[0]}-{day_range[1]}",
                    "intensity": (
                        range_count / queryset.count() if queryset.count() > 0 else 0
                    ),
                }

            logger.info("📅 Seasonal effects analysis completed")
            return seasonal_patterns

        except Exception as e:
            logger.warning(f"Seasonal effects analysis failed: {e}")
            return {
                "monthly_patterns": {},
                "quarterly_patterns": {},
                "day_of_week_patterns": {},
            }

    def _analyze_prize_position_patterns(self, queryset) -> Dict:
        """
        🏆 NEW FEATURE: Prize position intelligence analysis
        """
        try:
            position_intelligence = {}

            # Overall position statistics
            total_records = queryset.count()
            special_total = queryset.filter(appeared_in_special=True).count()
            first_total = queryset.filter(appeared_in_first=True).count()
            other_total = queryset.filter(appeared_in_other=True).count()

            overall_stats = {
                "special_prize_rate": (
                    round(special_total / total_records, 3) if total_records > 0 else 0
                ),
                "first_prize_rate": (
                    round(first_total / total_records, 3) if total_records > 0 else 0
                ),
                "other_prize_rate": (
                    round(other_total / total_records, 3) if total_records > 0 else 0
                ),
            }

            # Per-number position analysis
            number_position_patterns = {}

            for number in range(100):
                num_str = str(number).zfill(2)
                number_stats = queryset.filter(number=num_str)
                number_count = number_stats.count()

                if number_count < 3:  # Minimum threshold
                    continue

                special_count = number_stats.filter(appeared_in_special=True).count()
                first_count = number_stats.filter(appeared_in_first=True).count()
                other_count = number_stats.filter(appeared_in_other=True).count()

                # Position preferences
                special_rate = special_count / number_count
                first_rate = first_count / number_count
                other_rate = other_count / number_count

                # Determine preferred position
                preferred_position = (
                    "special"
                    if special_rate > first_rate and special_rate > other_rate
                    else "first" if first_rate > other_rate else "other"
                )

                # Position diversification (entropy-like measure)
                rates = [special_rate, first_rate, other_rate]
                non_zero_rates = [r for r in rates if r > 0]
                diversification = (
                    len(non_zero_rates) / 3.0
                )  # Simple diversification measure

                number_position_patterns[num_str] = {
                    "total_appearances": number_count,
                    "special_prize_rate": round(special_rate, 3),
                    "first_prize_rate": round(first_rate, 3),
                    "other_prize_rate": round(other_rate, 3),
                    "preferred_position": preferred_position,
                    "position_diversification": round(diversification, 3),
                    "position_specialization": round(
                        max(rates), 3
                    ),  # How specialized in one position
                }

            position_intelligence["overall_statistics"] = overall_stats
            position_intelligence["number_patterns"] = number_position_patterns

            # Top specialized numbers for each position
            specialized_numbers = {
                "special_specialists": sorted(
                    [
                        (k, v)
                        for k, v in number_position_patterns.items()
                        if v["preferred_position"] == "special"
                    ],
                    key=lambda x: x[1]["special_prize_rate"],
                    reverse=True,
                )[:10],
                "first_specialists": sorted(
                    [
                        (k, v)
                        for k, v in number_position_patterns.items()
                        if v["preferred_position"] == "first"
                    ],
                    key=lambda x: x[1]["first_prize_rate"],
                    reverse=True,
                )[:10],
                "other_specialists": sorted(
                    [
                        (k, v)
                        for k, v in number_position_patterns.items()
                        if v["preferred_position"] == "other"
                    ],
                    key=lambda x: x[1]["other_prize_rate"],
                    reverse=True,
                )[:10],
            }

            position_intelligence["specialized_numbers"] = specialized_numbers

            logger.info(
                f"🏆 Prize position analysis completed for {len(number_position_patterns)} numbers"
            )
            return position_intelligence

        except Exception as e:
            logger.warning(f"Prize position analysis failed: {e}")
            return {}

    def _perform_statistical_tests(self, queryset, significance_level: float) -> Dict:
        """
        📊 NEW FEATURE: Comprehensive statistical testing suite
        """
        try:
            statistical_results = {
                "uniformity_test": self._test_number_uniformity(
                    queryset, significance_level
                ),
                "independence_test": self._test_number_independence(
                    queryset, significance_level
                ),
                "randomness_test": self._test_sequence_randomness(
                    queryset, significance_level
                ),
                "trend_test": self._test_temporal_trends(queryset, significance_level),
            }

            logger.info("📊 Statistical testing suite completed")
            return statistical_results

        except Exception as e:
            logger.warning(f"Statistical tests failed: {e}")
            return {}

    def _calculate_absence_periods(self, number: str, queryset) -> Dict:
        """
        Helper method to calculate absence periods for a number
        """
        try:
            number_appearances = queryset.filter(number=number).order_by("date")

            if not number_appearances.exists():
                return {"current_streak": 999, "max_period": 999, "avg_period": 999}

            appearance_dates = list(number_appearances.values_list("date", flat=True))

            # Calculate gaps between appearances
            gaps = []
            for i in range(1, len(appearance_dates)):
                gap = (
                    appearance_dates[i] - appearance_dates[i - 1]
                ).days - 1  # -1 because gap is exclusive
                gaps.append(max(0, gap))

            # Current absence streak
            if appearance_dates:
                current_streak = (date.today() - appearance_dates[-1]).days
            else:
                current_streak = 999

            return {
                "current_streak": current_streak,
                "max_period": max(gaps) if gaps else 0,
                "avg_period": round(np.mean(gaps), 1) if gaps else 0,
            }

        except Exception as e:
            logger.warning(f"Absence period calculation failed for {number}: {e}")
            return {"current_streak": 0, "max_period": 0, "avg_period": 0}

    def _get_fallback_patterns(self) -> Dict:
        """Enhanced fallback patterns with metadata"""
        return {
            "analysis_metadata": {
                "status": "fallback",
                "reason": "insufficient_data_or_error",
                "timestamp": datetime.now().isoformat(),
            },
            "hot_numbers": {},
            "cold_numbers": {},
            "cyclical_patterns": {},
            "mean_reversion": {},
            "momentum_patterns": {},
            "seasonal_effects": {},
            "day_of_week_bias": {},
            "month_end_effects": {},
            "prize_position_intelligence": {},
            "gap_analysis": {},
            "correlation_matrix": {},
            "statistical_tests": {},
            "trend_analysis": {},
            "risk_assessment": {},
        }

    # Placeholder methods for other enhanced analyses
    def _detect_cyclical_patterns_enhanced(self, queryset) -> Dict:
        """Enhanced cyclical pattern detection with real dates"""
        # Implementation would go here
        return {}

    def _analyze_mean_reversion_enhanced(self, queryset) -> Dict:
        """Enhanced mean reversion analysis"""
        # Implementation would go here
        return {}

    def _analyze_momentum_enhanced(self, queryset) -> Dict:
        """Enhanced momentum analysis"""
        # Implementation would go here
        return {}

    def _analyze_dow_bias_enhanced(self, queryset) -> Dict:
        """Enhanced day-of-week bias analysis"""
        # Implementation would go here
        return {}

    def _analyze_month_end_effects_enhanced(self, queryset) -> Dict:
        """Enhanced month-end effects analysis"""
        # Implementation would go here
        return {}

    def _analyze_number_gaps_enhanced(self, queryset) -> Dict:
        """Enhanced gap analysis"""
        # Implementation would go here
        return {}

    def _calculate_number_correlations_enhanced(self, queryset) -> Dict:
        """Enhanced correlation analysis"""
        # Implementation would go here
        return {}

    def _analyze_trends_enhanced(self, queryset) -> Dict:
        """Enhanced trend analysis"""
        # Implementation would go here
        return {}

    def _assess_prediction_risks(self, queryset) -> Dict:
        """Risk assessment for predictions"""
        # Implementation would go here
        return {}

    # Statistical test helper methods
    def _test_number_uniformity(self, queryset, significance_level) -> Dict:
        """Test if number distribution is uniform"""
        # Implementation would go here
        return {}

    def _test_number_independence(self, queryset, significance_level) -> Dict:
        """Test if number appearances are independent"""
        # Implementation would go here
        return {}

    def _test_sequence_randomness(self, queryset, significance_level) -> Dict:
        """Test if sequence is random"""
        # Implementation would go here
        return {}

    def _test_temporal_trends(self, queryset, significance_level) -> Dict:
        """Test for temporal trends"""
        # Implementation would go here
        return {}


# Public API function
def get_enhanced_frequency_insights(
    start_date: date = None, end_date: date = None, significance_level: float = 0.05
) -> Dict:
    """
    🚀 PUBLIC API: Get enhanced comprehensive frequency insights

    Args:
        start_date: Analysis start date (default: 6 months ago)
        end_date: Analysis end date (default: today)
        significance_level: Statistical significance threshold (default: 0.05)

    Returns:
        Dict: Enhanced frequency analysis results
    """
    analyzer = EnhancedDeepFrequencyAnalyzer()
    return analyzer.analyze_frequency_patterns_enhanced(
        start_date, end_date, significance_level
    )
