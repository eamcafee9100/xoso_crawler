"""
🚀 PHASE 2B: Value at Risk (VaR) Calculator
==========================================

Advanced VaR calculation methods for lottery prediction risk management:
- Historical Simulation VaR
- Parametric VaR (Normal & Student-t)
- Monte Carlo VaR
- Expected Shortfall (Conditional VaR)
- Backtesting and validation
"""

import logging
import warnings
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Tuple

import numpy as np
import pandas as pd
from scipy import stats
from scipy.optimize import minimize

logger = logging.getLogger(__name__)


class VaRCalculator:
    """
    🎯 PHASE 2B: Value at Risk Calculator

    Comprehensive VaR calculation engine supporting multiple methodologies:
    - Historical Simulation (non-parametric)
    - Parametric approaches (Normal, Student-t)
    - Monte Carlo simulation
    - Expected Shortfall calculations
    - Model validation and backtesting
    """

    def __init__(self, lookback_days: int = 252):
        """
        Initialize VaR Calculator

        Args:
            lookback_days: Historical data window for calculations
        """
        self.lookback_days = lookback_days
        self.confidence_levels = [0.90, 0.95, 0.99]
        self.var_cache = {}

        logger.info(f"🚀 VaR Calculator initialized (lookback: {lookback_days} days)")

    def calculate_historical_var(
        self, returns: np.ndarray, confidence_levels: Optional[List[float]] = None
    ) -> Dict[str, float]:
        """
        Calculate VaR using Historical Simulation method

        Args:
            returns: Historical returns array
            confidence_levels: Confidence levels for VaR calculation

        Returns:
            Dict: VaR values for each confidence level
        """
        try:
            if confidence_levels is None:
                confidence_levels = self.confidence_levels

            if len(returns) < 30:
                logger.warning("⚠️ Insufficient historical data for reliable VaR")
                return {f"var_{int(cl*100)}": 0.01 for cl in confidence_levels}

            # Sort returns in ascending order
            sorted_returns = np.sort(returns)
            n_obs = len(sorted_returns)

            var_results = {}

            for confidence_level in confidence_levels:
                # Calculate percentile position
                alpha = 1 - confidence_level
                position = alpha * n_obs

                # Interpolate if position is not integer
                if position == int(position):
                    var_value = sorted_returns[int(position) - 1]
                else:
                    lower_idx = int(np.floor(position)) - 1
                    upper_idx = int(np.ceil(position)) - 1
                    weight = position - np.floor(position)
                    var_value = (1 - weight) * sorted_returns[
                        lower_idx
                    ] + weight * sorted_returns[upper_idx]

                var_results[f"var_{int(confidence_level*100)}"] = abs(var_value)

            logger.info(
                f"✅ Historical VaR calculated for {len(confidence_levels)} confidence levels"
            )
            return var_results

        except Exception as e:
            logger.error(f"❌ Historical VaR calculation failed: {e}")
            return {
                f"var_{int(cl*100)}": 0.01
                for cl in confidence_levels or self.confidence_levels
            }

    def calculate_parametric_var(
        self,
        returns: np.ndarray,
        distribution: str = "normal",
        confidence_levels: Optional[List[float]] = None,
    ) -> Dict[str, float]:
        """
        Calculate VaR using parametric approach

        Args:
            returns: Historical returns array
            distribution: 'normal' or 'student_t'
            confidence_levels: Confidence levels for VaR calculation

        Returns:
            Dict: VaR values for each confidence level
        """
        try:
            if confidence_levels is None:
                confidence_levels = self.confidence_levels

            if len(returns) < 10:
                logger.warning("⚠️ Insufficient data for parametric VaR")
                return {
                    f"var_{int(cl*100)}_{distribution}": 0.01
                    for cl in confidence_levels
                }

            # Calculate sample statistics
            mean_return = np.mean(returns)
            std_return = np.std(returns, ddof=1)

            var_results = {}

            if distribution == "normal":
                # Normal distribution VaR
                for confidence_level in confidence_levels:
                    z_score = stats.norm.ppf(1 - confidence_level)
                    var_value = mean_return + z_score * std_return
                    var_results[f"var_{int(confidence_level*100)}_normal"] = abs(
                        var_value
                    )

            elif distribution == "student_t":
                # Student-t distribution VaR
                # Fit degrees of freedom
                with warnings.catch_warnings():
                    warnings.simplefilter("ignore")
                    df, loc, scale = stats.t.fit(returns)

                for confidence_level in confidence_levels:
                    t_score = stats.t.ppf(1 - confidence_level, df=df)
                    var_value = loc + t_score * scale
                    var_results[f"var_{int(confidence_level*100)}_student_t"] = abs(
                        var_value
                    )

            logger.info(f"✅ Parametric VaR ({distribution}) calculated")
            return var_results

        except Exception as e:
            logger.error(f"❌ Parametric VaR calculation failed: {e}")
            return {
                f"var_{int(cl*100)}_{distribution}": 0.01
                for cl in confidence_levels or self.confidence_levels
            }

    def calculate_monte_carlo_var(
        self,
        returns: np.ndarray,
        n_simulations: int = 10000,
        confidence_levels: Optional[List[float]] = None,
        distribution_params: Optional[Dict] = None,
    ) -> Dict[str, float]:
        """
        Calculate VaR using Monte Carlo simulation

        Args:
            returns: Historical returns for parameter estimation
            n_simulations: Number of Monte Carlo simulations
            confidence_levels: Confidence levels for VaR calculation
            distribution_params: Custom distribution parameters

        Returns:
            Dict: VaR values for each confidence level
        """
        try:
            if confidence_levels is None:
                confidence_levels = self.confidence_levels

            if len(returns) < 10:
                logger.warning("⚠️ Insufficient data for Monte Carlo VaR")
                return {f"var_{int(cl*100)}_mc": 0.01 for cl in confidence_levels}

            # Estimate distribution parameters
            if distribution_params is None:
                mean_return = np.mean(returns)
                std_return = np.std(returns, ddof=1)
            else:
                mean_return = distribution_params.get("mean", np.mean(returns))
                std_return = distribution_params.get("std", np.std(returns, ddof=1))

            # Generate Monte Carlo simulations
            np.random.seed(42)  # For reproducibility
            simulated_returns = np.random.normal(mean_return, std_return, n_simulations)

            # Calculate VaR from simulated returns
            var_results = {}
            for confidence_level in confidence_levels:
                var_value = np.percentile(
                    simulated_returns, (1 - confidence_level) * 100
                )
                var_results[f"var_{int(confidence_level*100)}_mc"] = abs(var_value)

            logger.info(
                f"✅ Monte Carlo VaR calculated ({n_simulations:,} simulations)"
            )
            return var_results

        except Exception as e:
            logger.error(f"❌ Monte Carlo VaR calculation failed: {e}")
            return {
                f"var_{int(cl*100)}_mc": 0.01
                for cl in confidence_levels or self.confidence_levels
            }

    def calculate_expected_shortfall(
        self,
        returns: np.ndarray,
        confidence_levels: Optional[List[float]] = None,
        method: str = "historical",
    ) -> Dict[str, float]:
        """
        Calculate Expected Shortfall (Conditional VaR)

        Args:
            returns: Historical returns array
            confidence_levels: Confidence levels for ES calculation
            method: 'historical' or 'parametric'

        Returns:
            Dict: Expected Shortfall values
        """
        try:
            if confidence_levels is None:
                confidence_levels = self.confidence_levels

            if len(returns) < 10:
                logger.warning("⚠️ Insufficient data for Expected Shortfall")
                return {f"es_{int(cl*100)}": 0.015 for cl in confidence_levels}

            es_results = {}

            if method == "historical":
                # Historical Expected Shortfall
                for confidence_level in confidence_levels:
                    var_threshold = np.percentile(returns, (1 - confidence_level) * 100)
                    tail_losses = returns[returns <= var_threshold]

                    if len(tail_losses) > 0:
                        es_value = np.mean(tail_losses)
                    else:
                        es_value = var_threshold

                    es_results[f"es_{int(confidence_level*100)}"] = abs(es_value)

            elif method == "parametric":
                # Parametric Expected Shortfall (Normal distribution)
                mean_return = np.mean(returns)
                std_return = np.std(returns, ddof=1)

                for confidence_level in confidence_levels:
                    alpha = 1 - confidence_level
                    z_alpha = stats.norm.ppf(alpha)

                    # Expected Shortfall formula for normal distribution
                    es_value = (
                        mean_return - std_return * stats.norm.pdf(z_alpha) / alpha
                    )
                    es_results[f"es_{int(confidence_level*100)}_parametric"] = abs(
                        es_value
                    )

            logger.info(f"✅ Expected Shortfall calculated using {method} method")
            return es_results

        except Exception as e:
            logger.error(f"❌ Expected Shortfall calculation failed: {e}")
            return {
                f"es_{int(cl*100)}": 0.015
                for cl in confidence_levels or self.confidence_levels
            }

    def calculate_comprehensive_var(self, returns: np.ndarray) -> Dict[str, Any]:
        """
        Calculate comprehensive VaR using all methodologies

        Args:
            returns: Historical returns array

        Returns:
            Dict: Complete VaR analysis results
        """
        try:
            results = {
                "calculation_timestamp": datetime.now().isoformat(),
                "data_points": len(returns),
                "return_statistics": {
                    "mean": float(np.mean(returns)),
                    "std": float(np.std(returns, ddof=1)),
                    "skewness": float(stats.skew(returns)),
                    "kurtosis": float(stats.kurtosis(returns)),
                    "min": float(np.min(returns)),
                    "max": float(np.max(returns)),
                },
                "var_methods": {},
                "expected_shortfall": {},
                "model_comparison": {},
            }

            # Calculate VaR using different methods
            results["var_methods"]["historical"] = self.calculate_historical_var(
                returns
            )
            results["var_methods"]["parametric_normal"] = self.calculate_parametric_var(
                returns, "normal"
            )
            results["var_methods"]["parametric_student_t"] = (
                self.calculate_parametric_var(returns, "student_t")
            )
            results["var_methods"]["monte_carlo"] = self.calculate_monte_carlo_var(
                returns
            )

            # Calculate Expected Shortfall
            results["expected_shortfall"]["historical"] = (
                self.calculate_expected_shortfall(returns, method="historical")
            )
            results["expected_shortfall"]["parametric"] = (
                self.calculate_expected_shortfall(returns, method="parametric")
            )

            # Model comparison
            results["model_comparison"] = self._compare_var_models(
                results["var_methods"]
            )

            logger.info("✅ Comprehensive VaR analysis completed")
            return results

        except Exception as e:
            logger.error(f"❌ Comprehensive VaR calculation failed: {e}")
            return {
                "error": str(e),
                "calculation_timestamp": datetime.now().isoformat(),
            }

    def backtest_var_model(
        self,
        returns: np.ndarray,
        var_estimates: np.ndarray,
        confidence_level: float = 0.95,
    ) -> Dict[str, Any]:
        """
        Backtest VaR model performance

        Args:
            returns: Actual historical returns
            var_estimates: VaR estimates for same period
            confidence_level: VaR confidence level

        Returns:
            Dict: Backtesting results and statistics
        """
        try:
            if len(returns) != len(var_estimates):
                raise ValueError("Returns and VaR estimates must have same length")

            # Count VaR violations
            violations = returns < -var_estimates
            n_violations = np.sum(violations)
            total_observations = len(returns)
            violation_rate = n_violations / total_observations
            expected_violations = (1 - confidence_level) * total_observations

            # Unconditional coverage test (Kupiec test)
            if expected_violations > 0:
                lr_uc = -2 * np.log(
                    (confidence_level ** (total_observations - n_violations))
                    * ((1 - confidence_level) ** n_violations)
                ) + 2 * np.log(
                    ((1 - violation_rate) ** (total_observations - n_violations))
                    * (violation_rate**n_violations)
                )
                p_value_uc = 1 - stats.chi2.cdf(lr_uc, df=1)
            else:
                lr_uc = 0
                p_value_uc = 1

            # Calculate average loss during violations
            violation_losses = returns[violations]
            avg_violation_loss = (
                np.mean(violation_losses) if len(violation_losses) > 0 else 0
            )

            backtest_results = {
                "test_period": f"{len(returns)} observations",
                "confidence_level": confidence_level,
                "violations": {
                    "count": int(n_violations),
                    "rate": float(violation_rate),
                    "expected_count": float(expected_violations),
                    "expected_rate": float(1 - confidence_level),
                },
                "kupiec_test": {
                    "lr_statistic": float(lr_uc),
                    "p_value": float(p_value_uc),
                    "reject_model": p_value_uc < 0.05,
                },
                "loss_statistics": {
                    "avg_violation_loss": float(avg_violation_loss),
                    "max_violation_loss": (
                        float(np.min(violation_losses))
                        if len(violation_losses) > 0
                        else 0
                    ),
                    "total_violation_loss": float(np.sum(violation_losses)),
                },
                "model_assessment": self._assess_var_model_performance(
                    violation_rate, confidence_level, p_value_uc
                ),
            }

            logger.info(
                f"✅ VaR backtesting completed: {n_violations}/{total_observations} violations"
            )
            return backtest_results

        except Exception as e:
            logger.error(f"❌ VaR backtesting failed: {e}")
            return {"error": str(e)}

    def _compare_var_models(
        self, var_methods: Dict[str, Dict[str, float]]
    ) -> Dict[str, Any]:
        """Compare different VaR calculation methods"""
        comparison = {}

        # Extract VaR95 values for comparison
        var_95_values = {}
        for method, results in var_methods.items():
            for key, value in results.items():
                if "var_95" in key:
                    var_95_values[method] = value
                    break

        if len(var_95_values) > 1:
            values = list(var_95_values.values())
            comparison["var_95_range"] = {
                "min": float(np.min(values)),
                "max": float(np.max(values)),
                "std": float(np.std(values)),
                "coefficient_of_variation": float(np.std(values) / np.mean(values)),
            }

            # Identify most conservative and aggressive models
            comparison["model_ranking"] = {
                "most_conservative": max(var_95_values, key=var_95_values.get),
                "most_aggressive": min(var_95_values, key=var_95_values.get),
            }

        return comparison

    def _assess_var_model_performance(
        self, violation_rate: float, confidence_level: float, p_value: float
    ) -> Dict[str, str]:
        """Assess VaR model performance based on backtesting"""
        expected_rate = 1 - confidence_level

        assessment = {
            "overall": "ACCEPTABLE",
            "coverage": "ADEQUATE",
            "statistical_significance": "PASS",
        }

        # Check violation rate
        if violation_rate > expected_rate * 1.5:
            assessment["coverage"] = "INADEQUATE"
            assessment["overall"] = "POOR"
        elif violation_rate < expected_rate * 0.5:
            assessment["coverage"] = "OVERLY_CONSERVATIVE"

        # Check statistical significance
        if p_value < 0.05:
            assessment["statistical_significance"] = "FAIL"
            assessment["overall"] = "POOR"

        return assessment
