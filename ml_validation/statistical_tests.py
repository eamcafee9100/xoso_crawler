"""
Statistical Significance Testing for Lottery Predictions
Implements rigorous statistical validation methods
"""

import logging
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple

import numpy as np
import pandas as pd
from scipy import stats


@dataclass
class SignificanceResult:
    """Statistical significance test result"""

    test_name: str
    statistic: float
    p_value: float
    is_significant: bool
    confidence_interval: Tuple[float, float]
    interpretation: str


@dataclass
class ControlGroupResult:
    """Control group comparison result"""

    prediction_accuracy: float
    random_accuracy: float
    improvement: float
    significance: SignificanceResult


class StatisticalValidator:
    """
    Comprehensive statistical validation for prediction systems
    """

    def __init__(self, alpha: float = 0.05):
        self.alpha = alpha  # Significance level
        self.logger = logging.getLogger(__name__)

    def test_prediction_significance(
        self, predictions: List[List[int]], actual_results: List[List[int]]
    ) -> SignificanceResult:
        """
        Test if predictions are significantly better than random

        Args:
            predictions: List of predicted number sets
            actual_results: List of actual result sets

        Returns:
            SignificanceResult with statistical test results
        """
        if len(predictions) != len(actual_results):
            raise ValueError("Predictions and actual results must have same length")

        # Calculate hit rates for each prediction
        hit_rates = []
        for pred, actual in zip(predictions, actual_results):
            hits = len(set(pred) & set(actual))
            hit_rate = hits / len(pred) if pred else 0
            hit_rates.append(hit_rate)

        # Expected random hit rate for lottery
        # For XSMB: ~27 winning numbers out of 100 possible
        expected_random = 0.27  # 27% for 2-digit lottery

        # One-sample t-test against random expectation
        statistic, p_value = stats.ttest_1samp(hit_rates, expected_random)

        # Confidence interval
        mean_hit_rate = np.mean(hit_rates)
        sem = stats.sem(hit_rates)
        ci = stats.t.interval(
            1 - self.alpha, len(hit_rates) - 1, loc=mean_hit_rate, scale=sem
        )

        is_significant = p_value < self.alpha and statistic > 0

        interpretation = self._interpret_significance_test(
            mean_hit_rate, expected_random, p_value, is_significant
        )

        return SignificanceResult(
            test_name="One-sample t-test vs Random",
            statistic=statistic,
            p_value=p_value,
            is_significant=is_significant,
            confidence_interval=ci,
            interpretation=interpretation,
        )

    def run_control_group_analysis(
        self,
        predictions: List[List[int]],
        actual_results: List[List[int]],
        n_control_iterations: int = 1000,
    ) -> ControlGroupResult:
        """
        Compare prediction performance against random control group

        Args:
            predictions: Prediction results
            actual_results: Actual lottery results
            n_control_iterations: Number of random control iterations

        Returns:
            ControlGroupResult with comparison analysis
        """
        # Calculate prediction accuracy
        prediction_accuracies = []
        for pred, actual in zip(predictions, actual_results):
            hits = len(set(pred) & set(actual))
            accuracy = hits / len(pred) if pred else 0
            prediction_accuracies.append(accuracy)

        avg_prediction_accuracy = np.mean(prediction_accuracies)

        # Generate random control group results
        control_accuracies = []

        for _ in range(n_control_iterations):
            iteration_accuracies = []

            for actual in actual_results:
                # Generate random prediction of same size as original predictions
                pred_size = len(predictions[0]) if predictions else 15
                random_pred = np.random.choice(100, size=pred_size, replace=False)

                hits = len(set(random_pred) & set(actual))
                accuracy = hits / len(random_pred)
                iteration_accuracies.append(accuracy)

            control_accuracies.append(np.mean(iteration_accuracies))

        avg_control_accuracy = np.mean(control_accuracies)
        improvement = avg_prediction_accuracy - avg_control_accuracy

        # Statistical test: Mann-Whitney U test
        # Comparing prediction accuracies vs control group accuracies
        statistic, p_value = stats.mannwhitneyu(
            prediction_accuracies,
            control_accuracies[: len(prediction_accuracies)],
            alternative="greater",
        )

        # Confidence interval for improvement
        pooled_std = np.sqrt(
            (np.var(prediction_accuracies) + np.var(control_accuracies)) / 2
        )
        sem_diff = pooled_std * np.sqrt(2 / len(prediction_accuracies))

        ci_low = (
            improvement
            - stats.t.ppf(1 - self.alpha / 2, len(prediction_accuracies) - 1) * sem_diff
        )
        ci_high = (
            improvement
            + stats.t.ppf(1 - self.alpha / 2, len(prediction_accuracies) - 1) * sem_diff
        )

        significance = SignificanceResult(
            test_name="Mann-Whitney U vs Control",
            statistic=statistic,
            p_value=p_value,
            is_significant=p_value < self.alpha,
            confidence_interval=(ci_low, ci_high),
            interpretation=self._interpret_control_test(
                improvement, p_value, p_value < self.alpha
            ),
        )

        return ControlGroupResult(
            prediction_accuracy=avg_prediction_accuracy,
            random_accuracy=avg_control_accuracy,
            improvement=improvement,
            significance=significance,
        )

    def test_multiple_methods(
        self, method_results: Dict[str, List[float]]
    ) -> Dict[str, SignificanceResult]:
        """
        Test multiple prediction methods with Bonferroni correction

        Args:
            method_results: Dict mapping method names to accuracy lists

        Returns:
            Dict of significance results for each method
        """
        results = {}
        n_methods = len(method_results)
        corrected_alpha = self.alpha / n_methods  # Bonferroni correction

        for method, accuracies in method_results.items():
            # Test against random baseline
            expected_random = 0.27
            statistic, p_value = stats.ttest_1samp(accuracies, expected_random)

            mean_accuracy = np.mean(accuracies)
            sem = stats.sem(accuracies)
            ci = stats.t.interval(
                1 - corrected_alpha, len(accuracies) - 1, loc=mean_accuracy, scale=sem
            )

            is_significant = p_value < corrected_alpha and statistic > 0

            interpretation = f"""
            Method: {method}
            Mean accuracy: {mean_accuracy:.3f}
            Corrected p-value: {p_value:.6f} (α = {corrected_alpha:.6f})
            Significant: {is_significant}
            """

            results[method] = SignificanceResult(
                test_name=f"Bonferroni-corrected t-test ({method})",
                statistic=statistic,
                p_value=p_value,
                is_significant=is_significant,
                confidence_interval=ci,
                interpretation=interpretation.strip(),
            )

        return results

    def calculate_confidence_intervals(
        self, accuracies: List[float], confidence_level: float = 0.95
    ) -> Dict:
        """
        Calculate various confidence intervals for accuracy measurements

        Args:
            accuracies: List of accuracy measurements
            confidence_level: Confidence level (default 95%)

        Returns:
            Dict with different confidence interval methods
        """
        alpha = 1 - confidence_level
        n = len(accuracies)
        mean_acc = np.mean(accuracies)
        std_acc = np.std(accuracies, ddof=1)
        sem = std_acc / np.sqrt(n)

        # t-distribution CI
        t_critical = stats.t.ppf(1 - alpha / 2, n - 1)
        t_ci = (mean_acc - t_critical * sem, mean_acc + t_critical * sem)

        # Bootstrap CI
        bootstrap_means = []
        for _ in range(1000):
            bootstrap_sample = np.random.choice(accuracies, size=n, replace=True)
            bootstrap_means.append(np.mean(bootstrap_sample))

        bootstrap_ci = (
            np.percentile(bootstrap_means, 100 * alpha / 2),
            np.percentile(bootstrap_means, 100 * (1 - alpha / 2)),
        )

        # Wilson score interval (for proportions)
        z = stats.norm.ppf(1 - alpha / 2)
        p = mean_acc
        wilson_center = (p + z**2 / (2 * n)) / (1 + z**2 / n)
        wilson_width = z * np.sqrt(p * (1 - p) / n + z**2 / (4 * n**2)) / (1 + z**2 / n)
        wilson_ci = (wilson_center - wilson_width, wilson_center + wilson_width)

        return {
            "mean": mean_acc,
            "standard_error": sem,
            "t_interval": t_ci,
            "bootstrap_interval": bootstrap_ci,
            "wilson_interval": wilson_ci,
            "sample_size": n,
            "confidence_level": confidence_level,
        }

    def _interpret_significance_test(
        self,
        observed_rate: float,
        expected_rate: float,
        p_value: float,
        is_significant: bool,
    ) -> str:
        """Interpret significance test results"""
        improvement = (observed_rate - expected_rate) / expected_rate * 100

        if is_significant:
            return f"""
            SIGNIFICANT RESULT:
            Observed accuracy: {observed_rate:.3f} ({observed_rate*100:.1f}%)
            Expected random: {expected_rate:.3f} ({expected_rate*100:.1f}%)
            Improvement: {improvement:.1f}% over random
            p-value: {p_value:.6f} (< {self.alpha})
            
            The prediction system performs significantly better than random chance.
            """
        else:
            return f"""
            NOT SIGNIFICANT:
            Observed accuracy: {observed_rate:.3f} ({observed_rate*100:.1f}%)
            Expected random: {expected_rate:.3f} ({expected_rate*100:.1f}%)
            Improvement: {improvement:.1f}% over random
            p-value: {p_value:.6f} (≥ {self.alpha})
            
            Cannot conclude that prediction system outperforms random chance.
            """

    def _interpret_control_test(
        self, improvement: float, p_value: float, is_significant: bool
    ) -> str:
        """Interpret control group test results"""
        if is_significant:
            return f"""
            SIGNIFICANT IMPROVEMENT:
            Improvement over control: {improvement:.3f} ({improvement*100:.1f} percentage points)
            p-value: {p_value:.6f} (< {self.alpha})
            
            The prediction system significantly outperforms random selection.
            """
        else:
            return f"""
            NO SIGNIFICANT IMPROVEMENT:
            Improvement over control: {improvement:.3f} ({improvement*100:.1f} percentage points)
            p-value: {p_value:.6f} (≥ {self.alpha})
            
            No statistically significant improvement over random selection detected.
            """

    def generate_validation_report(
        self,
        significance_results: List[SignificanceResult],
        control_result: ControlGroupResult,
        confidence_intervals: Dict,
    ) -> Dict:
        """Generate comprehensive validation report"""

        significant_tests = [r for r in significance_results if r.is_significant]

        return {
            "summary": {
                "total_tests": len(significance_results),
                "significant_tests": len(significant_tests),
                "significance_rate": len(significant_tests) / len(significance_results),
                "overall_significant": len(significant_tests) > 0,
            },
            "control_comparison": {
                "prediction_accuracy": f"{control_result.prediction_accuracy:.3f}",
                "random_accuracy": f"{control_result.random_accuracy:.3f}",
                "improvement": f"{control_result.improvement:.3f}",
                "is_significant": control_result.significance.is_significant,
            },
            "confidence_intervals": confidence_intervals,
            "detailed_results": [
                {
                    "test": r.test_name,
                    "statistic": r.statistic,
                    "p_value": r.p_value,
                    "significant": r.is_significant,
                    "ci_lower": r.confidence_interval[0],
                    "ci_upper": r.confidence_interval[1],
                }
                for r in significance_results
            ],
            "recommendations": self._generate_validation_recommendations(
                significance_results, control_result
            ),
        }

    def _generate_validation_recommendations(
        self,
        significance_results: List[SignificanceResult],
        control_result: ControlGroupResult,
    ) -> List[str]:
        """Generate recommendations based on validation results"""
        recommendations = []

        significant_count = sum(1 for r in significance_results if r.is_significant)

        if significant_count == 0:
            recommendations.append("⚠️ No statistically significant results found")
            recommendations.append("🔄 Consider revising prediction methodology")
            recommendations.append("📊 Increase sample size for more reliable testing")

        elif significant_count == len(significance_results):
            recommendations.append("✅ All tests show statistical significance")
            recommendations.append("🚀 System appears to be performing well")
            recommendations.append("📈 Consider optimizing further for production")

        else:
            recommendations.append(
                f"⚡ {significant_count}/{len(significance_results)} tests significant"
            )
            recommendations.append("🔍 Focus on improving weaker prediction methods")

        if control_result.significance.is_significant:
            improvement_pct = control_result.improvement * 100
            recommendations.append(
                f"📊 System shows {improvement_pct:.1f}pp improvement over random"
            )
        else:
            recommendations.append(
                "⚠️ System does not significantly outperform random selection"
            )

        return recommendations
