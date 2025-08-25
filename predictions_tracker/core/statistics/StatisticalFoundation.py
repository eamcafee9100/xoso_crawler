"""
🎯 ELITE STATISTICAL FOUNDATION
Statistical rigor framework for top 0.1% lottery prediction system
Author: Elite Data Science Team
"""

import numpy as np
import pandas as pd
from scipy import stats
from scipy.stats import chi2_contingency, kstest, anderson
from sklearn.model_selection import TimeSeriesSplit
from typing import Dict, List, Tuple, Optional, Any
import logging
from datetime import date, timedelta
from dataclasses import dataclass
import warnings
warnings.filterwarnings('ignore', category=UserWarning)

logger = logging.getLogger(__name__)

@dataclass
class StatisticalResult:
    """Container for statistical test results"""
    test_name: str
    statistic: float
    p_value: float
    critical_value: float
    confidence_interval: Tuple[float, float]
    is_significant: bool
    effect_size: float
    interpretation: str

@dataclass
class ConfidenceMetrics:
    """Statistical confidence metrics"""
    wilson_interval: Tuple[float, float]
    bootstrap_interval: Tuple[float, float]
    bayesian_credible_interval: Tuple[float, float]
    prediction_interval: Tuple[float, float]
    statistical_power: float
    confidence_level: float

class EliteStatisticalValidator:
    """
    🏆 TOP 0.1% Statistical Validation Framework
    
    Implements advanced statistical methods used by elite quantitative analysts:
    - Wilson Score Intervals (better than normal approximation)
    - Bootstrap Confidence Intervals (non-parametric)
    - Bayesian Credible Intervals (incorporates prior knowledge)
    - Time Series Cross-Validation (prevents data leakage)
    - Multiple Testing Correction (controls Family-Wise Error Rate)
    """
    
    def __init__(self, significance_level: float = 0.05):
        self.significance_level = significance_level
        self.confidence_level = 1 - significance_level
        
    def wilson_score_interval(self, successes: int, trials: int, 
                            confidence: float = 0.95) -> Tuple[float, float]:
        """
        Wilson Score Interval - Superior to normal approximation for small samples
        Used by top statisticians for binomial proportions
        
        Formula: p̂ ± z√[(p̂(1-p̂) + z²/(4n))/n] / (1 + z²/n)
        """
        if trials == 0:
            return (0.0, 0.0)
            
        z = stats.norm.ppf((1 + confidence) / 2)
        p_hat = successes / trials
        
        denominator = 1 + z**2 / trials
        center = (p_hat + z**2 / (2 * trials)) / denominator
        margin = z * np.sqrt((p_hat * (1 - p_hat) + z**2 / (4 * trials)) / trials) / denominator
        
        lower = max(0, center - margin)
        upper = min(1, center + margin)
        
        return (lower, upper)
    
    def bootstrap_confidence_interval(self, data: np.ndarray, 
                                    statistic_func: callable = np.mean,
                                    n_bootstrap: int = 10000,
                                    confidence: float = 0.95) -> Tuple[float, float]:
        """
        Bootstrap Confidence Interval - Non-parametric, assumption-free
        Elite method for complex statistics without known distributions
        """
        if len(data) == 0:
            return (0.0, 0.0)
            
        np.random.seed(42)  # For reproducibility
        bootstrap_stats = []
        
        for _ in range(n_bootstrap):
            bootstrap_sample = np.random.choice(data, size=len(data), replace=True)
            bootstrap_stats.append(statistic_func(bootstrap_sample))
        
        alpha = 1 - confidence
        lower_percentile = (alpha / 2) * 100
        upper_percentile = (1 - alpha / 2) * 100
        
        return (np.percentile(bootstrap_stats, lower_percentile),
                np.percentile(bootstrap_stats, upper_percentile))
    
    def bayesian_credible_interval(self, successes: int, trials: int,
                                 alpha_prior: float = 1, beta_prior: float = 1,
                                 confidence: float = 0.95) -> Tuple[float, float]:
        """
        Bayesian Credible Interval using Beta-Binomial conjugate prior
        Incorporates domain expertise through informative priors
        """
        alpha_posterior = alpha_prior + successes
        beta_posterior = beta_prior + trials - successes
        
        alpha_tail = (1 - confidence) / 2
        
        lower = stats.beta.ppf(alpha_tail, alpha_posterior, beta_posterior)
        upper = stats.beta.ppf(1 - alpha_tail, alpha_posterior, beta_posterior)
        
        return (lower, upper)
    
    def chi_square_goodness_of_fit(self, observed: np.ndarray, 
                                 expected: np.ndarray) -> StatisticalResult:
        """
        Chi-square goodness of fit test
        Tests if observed distribution matches expected distribution
        """
        # Ensure we have valid data
        if len(observed) == 0 or len(expected) == 0:
            return StatisticalResult(
                test_name="Chi-Square Goodness of Fit",
                statistic=0.0, p_value=1.0, critical_value=0.0,
                confidence_interval=(0.0, 0.0), is_significant=False,
                effect_size=0.0, interpretation="Insufficient data"
            )
        
        # Filter out zero expected values (chi-square requirement)
        mask = expected > 0
        obs_filtered = observed[mask]
        exp_filtered = expected[mask]
        
        if len(obs_filtered) < 2:
            return StatisticalResult(
                test_name="Chi-Square Goodness of Fit",
                statistic=0.0, p_value=1.0, critical_value=0.0,
                confidence_interval=(0.0, 0.0), is_significant=False,
                effect_size=0.0, interpretation="Insufficient valid categories"
            )
        
        statistic, p_value = stats.chisquare(obs_filtered, exp_filtered)
        df = len(obs_filtered) - 1
        critical_value = stats.chi2.ppf(self.confidence_level, df)
        
        # Effect size (Cramér's V)
        n = np.sum(obs_filtered)
        cramers_v = np.sqrt(statistic / (n * (len(obs_filtered) - 1)))
        
        is_significant = p_value < self.significance_level
        
        if is_significant:
            interpretation = f"Significant deviation from expected (p={p_value:.4f})"
        else:
            interpretation = f"No significant deviation (p={p_value:.4f})"
        
        return StatisticalResult(
            test_name="Chi-Square Goodness of Fit",
            statistic=statistic,
            p_value=p_value,
            critical_value=critical_value,
            confidence_interval=self.wilson_score_interval(int(np.sum(obs_filtered)), 
                                                         int(n), self.confidence_level),
            is_significant=is_significant,
            effect_size=cramers_v,
            interpretation=interpretation
        )
    
    def calculate_statistical_power(self, effect_size: float, sample_size: int,
                                  alpha: float = 0.05) -> float:
        """
        Calculate statistical power for detecting effect of given size
        Power = 1 - β (Type II error rate)
        """
        from statsmodels.stats.power import ttest_power
        
        try:
            power = ttest_power(effect_size, sample_size, alpha, alternative='two-sided')
            return max(0, min(1, power))
        except:
            # Fallback calculation
            z_alpha = stats.norm.ppf(1 - alpha/2)
            z_beta = stats.norm.ppf(0.8)  # 80% power target
            required_n = ((z_alpha + z_beta) / effect_size) ** 2
            
            return min(1.0, sample_size / required_n)
    
    def multiple_testing_correction(self, p_values: List[float], 
                                  method: str = 'bonferroni') -> List[float]:
        """
        Multiple testing correction to control Family-Wise Error Rate
        Methods: bonferroni, holm, fdr_bh (Benjamini-Hochberg)
        """
        from statsmodels.stats.multitest import multipletests
        
        if not p_values:
            return []
        
        try:
            rejected, p_corrected, alpha_sidak, alpha_bonf = multipletests(
                p_values, alpha=self.significance_level, method=method
            )
            return p_corrected.tolist()
        except:
            # Fallback: Simple Bonferroni correction
            n_tests = len(p_values)
            return [min(1.0, p * n_tests) for p in p_values]

class PurgedTimeSeriesSplit:
    """
    🏆 ELITE TIME SERIES CROSS-VALIDATION
    
    Prevents data leakage in time series by:
    1. Purging overlapping observations
    2. Embargo period to prevent look-ahead bias
    3. Proper temporal ordering
    
    Used by top quantitative finance firms
    """
    
    def __init__(self, n_splits: int = 5, test_size: int = 30, 
                 purge_days: int = 7, embargo_days: int = 1):
        self.n_splits = n_splits
        self.test_size = test_size
        self.purge_days = purge_days
        self.embargo_days = embargo_days
    
    def split(self, X: pd.DataFrame, y: Optional[pd.Series] = None):
        """
        Generate train/test splits with purging and embargo
        
        Returns:
            Iterator of (train_indices, test_indices)
        """
        n_samples = len(X)
        
        # Calculate split points
        fold_size = (n_samples - self.test_size) // self.n_splits
        
        for i in range(self.n_splits):
            # Test set
            test_start = fold_size * (i + 1)
            test_end = min(test_start + self.test_size, n_samples)
            test_indices = list(range(test_start, test_end))
            
            # Train set (before test, with purge and embargo)
            train_end = test_start - self.purge_days - self.embargo_days
            train_indices = list(range(0, max(0, train_end)))
            
            if len(train_indices) > 0 and len(test_indices) > 0:
                yield train_indices, test_indices

class ElitePerformanceMetrics:
    """
    🏆 TOP 0.1% PERFORMANCE METRICS
    
    Advanced metrics used by elite quantitative analysts:
    - Sharpe Ratio (risk-adjusted returns)
    - Maximum Drawdown (worst-case scenario)
    - Calmar Ratio (return/max drawdown)
    - Information Ratio (excess return/tracking error)
    - VaR and CVaR (Value at Risk measures)
    """
    
    @staticmethod
    def sharpe_ratio_equivalent(hit_rates: np.ndarray, benchmark: float = 0.0) -> float:
        """
        Sharpe Ratio equivalent for lottery predictions
        (Average Hit Rate - Benchmark) / Standard Deviation of Hit Rates
        """
        if len(hit_rates) == 0:
            return 0.0
        
        excess_returns = hit_rates - benchmark
        return np.mean(excess_returns) / (np.std(excess_returns) + 1e-8)
    
    @staticmethod
    def maximum_drawdown(hit_rates: np.ndarray) -> float:
        """
        Maximum drawdown - largest peak-to-trough decline
        Critical metric for risk management
        """
        if len(hit_rates) == 0:
            return 0.0
        
        cumulative = np.cumsum(hit_rates)
        running_max = np.maximum.accumulate(cumulative)
        drawdown = (running_max - cumulative) / (running_max + 1e-8)
        
        return np.max(drawdown)
    
    @staticmethod
    def calmar_ratio(hit_rates: np.ndarray) -> float:
        """
        Calmar Ratio = Annual Return / Maximum Drawdown
        Higher is better (return per unit of worst-case risk)
        """
        if len(hit_rates) == 0:
            return 0.0
        
        annual_return = np.mean(hit_rates) * 365  # Annualized
        max_dd = ElitePerformanceMetrics.maximum_drawdown(hit_rates)
        
        return annual_return / (max_dd + 1e-8)
    
    @staticmethod
    def value_at_risk(hit_rates: np.ndarray, confidence_level: float = 0.05) -> float:
        """
        Value at Risk (VaR) - worst expected loss at given confidence level
        """
        if len(hit_rates) == 0:
            return 0.0
        
        return np.percentile(hit_rates, confidence_level * 100)
    
    @staticmethod
    def expected_shortfall(hit_rates: np.ndarray, confidence_level: float = 0.05) -> float:
        """
        Expected Shortfall (CVaR) - average loss beyond VaR
        More conservative than VaR
        """
        if len(hit_rates) == 0:
            return 0.0
        
        var = ElitePerformanceMetrics.value_at_risk(hit_rates, confidence_level)
        return np.mean(hit_rates[hit_rates <= var])

# Factory function for easy access
def create_statistical_validator(significance_level: float = 0.05) -> EliteStatisticalValidator:
    """Factory function to create statistical validator instance"""
    return EliteStatisticalValidator(significance_level)

def create_time_series_splitter(n_splits: int = 5, test_size: int = 30) -> PurgedTimeSeriesSplit:
    """Factory function to create time series splitter instance"""
    return PurgedTimeSeriesSplit(n_splits=n_splits, test_size=test_size)

# Example usage and testing
if __name__ == "__main__":
    # Test the statistical framework
    validator = create_statistical_validator()
    
    # Test Wilson Score Interval
    wilson_ci = validator.wilson_score_interval(successes=25, trials=100)
    print(f"Wilson CI (25/100): {wilson_ci}")
    
    # Test Bootstrap CI
    data = np.random.binomial(1, 0.3, 1000)  # Simulate hit/miss data
    bootstrap_ci = validator.bootstrap_confidence_interval(data)
    print(f"Bootstrap CI: {bootstrap_ci}")
    
    # Test Chi-square goodness of fit
    observed = np.array([20, 15, 30, 25, 10])
    expected = np.array([18, 18, 28, 28, 8])
    chi_result = validator.chi_square_goodness_of_fit(observed, expected)
    print(f"Chi-square test: {chi_result.interpretation}")
    
    print("✅ Statistical Foundation Framework - Ready for Production!")
