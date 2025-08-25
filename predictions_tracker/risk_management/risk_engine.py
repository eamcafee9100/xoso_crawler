"""
🚀 PHASE 2B: Risk Management Engine
==================================

Core risk management system for lottery predictions with:
- Portfolio risk assessment
- Loss scenario analysis
- Risk-adjusted performance metrics
- Dynamic risk limits
"""

import json
import logging
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Tuple

import numpy as np
import pandas as pd

logger = logging.getLogger(__name__)


@dataclass
class RiskMetrics:
    """Risk metrics container"""

    var_95: float
    var_99: float
    expected_shortfall: float
    max_drawdown: float
    sharpe_ratio: float
    calmar_ratio: float
    volatility: float
    beta: float
    alpha: float
    correlation_risk: float

    def to_dict(self) -> Dict[str, float]:
        """Convert to dictionary for JSON serialization"""
        return {
            "var_95": self.var_95,
            "var_99": self.var_99,
            "expected_shortfall": self.expected_shortfall,
            "max_drawdown": self.max_drawdown,
            "sharpe_ratio": self.sharpe_ratio,
            "calmar_ratio": self.calmar_ratio,
            "volatility": self.volatility,
            "beta": self.beta,
            "alpha": self.alpha,
            "correlation_risk": self.correlation_risk,
        }


@dataclass
class RiskLimits:
    """Risk limit configuration"""

    max_var_95: float = 0.05  # 5% daily VaR limit
    max_var_99: float = 0.10  # 10% extreme VaR limit
    max_drawdown: float = 0.20  # 20% maximum drawdown
    min_sharpe_ratio: float = 0.5  # Minimum acceptable Sharpe ratio
    max_correlation: float = 0.8  # Maximum correlation with benchmark
    position_limit: float = 0.25  # 25% maximum position size


class RiskManagementEngine:
    """
    🎯 PHASE 2B: Advanced Risk Management Engine

    Comprehensive risk management for lottery prediction strategies:
    - Real-time risk monitoring
    - VaR and Expected Shortfall calculations
    - Portfolio optimization with risk constraints
    - Dynamic position sizing based on risk metrics
    """

    def __init__(self, lookback_days: int = 90):
        """
        Initialize Risk Management Engine

        Args:
            lookback_days: Historical data window for risk calculations
        """
        self.lookback_days = lookback_days
        self.risk_limits = RiskLimits()
        self.risk_cache = {}

        logger.info(
            f"🚀 Risk Management Engine initialized (lookback: {lookback_days} days)"
        )

    def calculate_portfolio_risk(
        self,
        returns: np.ndarray,
        weights: Optional[np.ndarray] = None,
        confidence_levels: List[float] = [0.95, 0.99],
    ) -> RiskMetrics:
        """
        Calculate comprehensive portfolio risk metrics

        Args:
            returns: Historical returns array
            weights: Portfolio weights (equal weight if None)
            confidence_levels: VaR confidence levels

        Returns:
            RiskMetrics: Complete risk assessment
        """
        try:
            if len(returns) < 10:
                logger.warning("⚠️ Insufficient data for risk calculation")
                return self._default_risk_metrics()

            # Equal weights if not provided
            if weights is None:
                weights = np.ones(len(returns)) / len(returns)

            # Portfolio returns
            portfolio_returns = returns @ weights if len(returns.shape) > 1 else returns

            # VaR calculations
            var_95 = np.percentile(portfolio_returns, (1 - 0.95) * 100)
            var_99 = np.percentile(portfolio_returns, (1 - 0.99) * 100)

            # Expected Shortfall (Conditional VaR)
            expected_shortfall = np.mean(portfolio_returns[portfolio_returns <= var_95])

            # Performance metrics
            volatility = np.std(portfolio_returns) * np.sqrt(252)  # Annualized
            mean_return = np.mean(portfolio_returns) * 252  # Annualized

            # Sharpe ratio (assuming risk-free rate = 0)
            sharpe_ratio = mean_return / volatility if volatility > 0 else 0

            # Maximum drawdown
            cumulative_returns = np.cumprod(1 + portfolio_returns)
            peak = np.maximum.accumulate(cumulative_returns)
            drawdown = (cumulative_returns - peak) / peak
            max_drawdown = np.min(drawdown)

            # Calmar ratio
            calmar_ratio = mean_return / abs(max_drawdown) if max_drawdown != 0 else 0

            # Market beta (using market proxy)
            market_returns = self._get_market_proxy_returns(len(portfolio_returns))
            beta = self._calculate_beta(portfolio_returns, market_returns)
            alpha = mean_return - beta * np.mean(market_returns) * 252

            # Correlation risk
            correlation_risk = self._calculate_correlation_risk(returns)

            risk_metrics = RiskMetrics(
                var_95=abs(var_95),
                var_99=abs(var_99),
                expected_shortfall=abs(expected_shortfall),
                max_drawdown=abs(max_drawdown),
                sharpe_ratio=sharpe_ratio,
                calmar_ratio=calmar_ratio,
                volatility=volatility,
                beta=beta,
                alpha=alpha,
                correlation_risk=correlation_risk,
            )

            logger.info(
                f"✅ Portfolio risk calculated: VaR95={var_95:.3f}, Sharpe={sharpe_ratio:.2f}"
            )
            return risk_metrics

        except Exception as e:
            logger.error(f"❌ Portfolio risk calculation failed: {e}")
            return self._default_risk_metrics()

    def assess_risk_limits(self, risk_metrics: RiskMetrics) -> Dict[str, Any]:
        """
        Assess current risk metrics against defined limits

        Args:
            risk_metrics: Current portfolio risk metrics

        Returns:
            Dict: Risk limit assessment with breach indicators
        """
        assessment = {
            "timestamp": datetime.now().isoformat(),
            "overall_risk_level": "LOW",
            "breaches": [],
            "warnings": [],
            "recommendations": [],
        }

        # Check VaR limits
        if risk_metrics.var_95 > self.risk_limits.max_var_95:
            assessment["breaches"].append(
                {
                    "metric": "VaR_95",
                    "current": risk_metrics.var_95,
                    "limit": self.risk_limits.max_var_95,
                    "severity": "HIGH",
                }
            )
            assessment["overall_risk_level"] = "HIGH"

        if risk_metrics.var_99 > self.risk_limits.max_var_99:
            assessment["breaches"].append(
                {
                    "metric": "VaR_99",
                    "current": risk_metrics.var_99,
                    "limit": self.risk_limits.max_var_99,
                    "severity": "CRITICAL",
                }
            )
            assessment["overall_risk_level"] = "CRITICAL"

        # Check drawdown limits
        if risk_metrics.max_drawdown > self.risk_limits.max_drawdown:
            assessment["breaches"].append(
                {
                    "metric": "Max_Drawdown",
                    "current": risk_metrics.max_drawdown,
                    "limit": self.risk_limits.max_drawdown,
                    "severity": "HIGH",
                }
            )

        # Check performance metrics
        if risk_metrics.sharpe_ratio < self.risk_limits.min_sharpe_ratio:
            assessment["warnings"].append(
                {
                    "metric": "Sharpe_Ratio",
                    "current": risk_metrics.sharpe_ratio,
                    "threshold": self.risk_limits.min_sharpe_ratio,
                    "message": "Poor risk-adjusted performance",
                }
            )

        # Generate recommendations
        if len(assessment["breaches"]) > 0:
            assessment["recommendations"].append("Reduce position sizes immediately")
            assessment["recommendations"].append("Review and tighten risk controls")

        if risk_metrics.correlation_risk > self.risk_limits.max_correlation:
            assessment["recommendations"].append("Diversify strategy portfolio")

        logger.info(
            f"🔍 Risk assessment: {assessment['overall_risk_level']} risk level"
        )
        return assessment

    def optimize_position_sizes(
        self,
        expected_returns: np.ndarray,
        covariance_matrix: np.ndarray,
        risk_budget: float = 0.05,
    ) -> np.ndarray:
        """
        Optimize position sizes using risk budgeting approach

        Args:
            expected_returns: Expected returns for each strategy
            covariance_matrix: Return covariance matrix
            risk_budget: Maximum portfolio risk budget

        Returns:
            np.ndarray: Optimized position weights
        """
        try:
            n_strategies = len(expected_returns)

            # Risk parity baseline
            inv_vol = 1 / np.sqrt(np.diag(covariance_matrix))
            risk_parity_weights = inv_vol / np.sum(inv_vol)

            # Adjust for expected returns and risk budget
            portfolio_vol = np.sqrt(
                risk_parity_weights.T @ covariance_matrix @ risk_parity_weights
            )

            # Scale to risk budget
            scaling_factor = risk_budget / portfolio_vol
            optimal_weights = risk_parity_weights * min(scaling_factor, 1.0)

            # Apply position limits
            optimal_weights = np.minimum(
                optimal_weights, self.risk_limits.position_limit
            )
            optimal_weights = optimal_weights / np.sum(optimal_weights)  # Renormalize

            logger.info(
                f"✅ Position sizes optimized with {risk_budget:.1%} risk budget"
            )
            return optimal_weights

        except Exception as e:
            logger.error(f"❌ Position optimization failed: {e}")
            # Return equal weights as fallback
            return np.ones(len(expected_returns)) / len(expected_returns)

    def generate_risk_report(
        self, risk_metrics: RiskMetrics, assessment: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Generate comprehensive risk management report

        Args:
            risk_metrics: Current risk metrics
            assessment: Risk limit assessment

        Returns:
            Dict: Detailed risk report
        """
        report = {
            "report_timestamp": datetime.now().isoformat(),
            "risk_metrics": risk_metrics.to_dict(),
            "risk_assessment": assessment,
            "executive_summary": {
                "overall_risk_level": assessment["overall_risk_level"],
                "key_risks": [],
                "action_required": len(assessment["breaches"]) > 0,
            },
            "detailed_analysis": {
                "var_analysis": self._analyze_var_metrics(risk_metrics),
                "performance_analysis": self._analyze_performance_metrics(risk_metrics),
                "correlation_analysis": self._analyze_correlation_risk(risk_metrics),
            },
            "recommendations": assessment["recommendations"],
        }

        # Identify key risks
        if risk_metrics.var_95 > 0.03:
            report["executive_summary"]["key_risks"].append("High daily loss potential")

        if risk_metrics.max_drawdown > 0.15:
            report["executive_summary"]["key_risks"].append("Significant drawdown risk")

        if risk_metrics.sharpe_ratio < 0.5:
            report["executive_summary"]["key_risks"].append(
                "Poor risk-adjusted returns"
            )

        logger.info("📊 Risk management report generated")
        return report

    def _default_risk_metrics(self) -> RiskMetrics:
        """Return default risk metrics for insufficient data"""
        return RiskMetrics(
            var_95=0.01,
            var_99=0.02,
            expected_shortfall=0.015,
            max_drawdown=0.05,
            sharpe_ratio=0.0,
            calmar_ratio=0.0,
            volatility=0.1,
            beta=1.0,
            alpha=0.0,
            correlation_risk=0.5,
        )

    def _get_market_proxy_returns(self, n_periods: int) -> np.ndarray:
        """Generate market proxy returns for beta calculation"""
        # Simulate market returns (in practice, use actual market data)
        np.random.seed(42)
        return np.random.normal(0.0005, 0.02, n_periods)  # Daily market returns

    def _calculate_beta(
        self, portfolio_returns: np.ndarray, market_returns: np.ndarray
    ) -> float:
        """Calculate portfolio beta"""
        if len(portfolio_returns) != len(market_returns) or len(portfolio_returns) < 10:
            return 1.0

        covariance = np.cov(portfolio_returns, market_returns)[0, 1]
        market_variance = np.var(market_returns)

        return covariance / market_variance if market_variance > 0 else 1.0

    def _calculate_correlation_risk(self, returns: np.ndarray) -> float:
        """Calculate correlation-based risk measure"""
        if len(returns.shape) < 2 or returns.shape[1] < 2:
            return 0.0

        correlation_matrix = np.corrcoef(returns.T)
        # Average absolute correlation as risk measure
        n = correlation_matrix.shape[0]
        total_correlation = np.sum(np.abs(correlation_matrix)) - n  # Exclude diagonal
        avg_correlation = total_correlation / (n * (n - 1))

        return avg_correlation

    def _analyze_var_metrics(self, risk_metrics: RiskMetrics) -> Dict[str, Any]:
        """Analyze VaR metrics"""
        return {
            "var_95_assessment": "HIGH" if risk_metrics.var_95 > 0.05 else "NORMAL",
            "var_99_assessment": (
                "CRITICAL" if risk_metrics.var_99 > 0.10 else "ACCEPTABLE"
            ),
            "tail_risk_ratio": (
                risk_metrics.var_99 / risk_metrics.var_95
                if risk_metrics.var_95 > 0
                else 1.0
            ),
            "expected_shortfall_multiple": (
                risk_metrics.expected_shortfall / risk_metrics.var_95
                if risk_metrics.var_95 > 0
                else 1.0
            ),
        }

    def _analyze_performance_metrics(self, risk_metrics: RiskMetrics) -> Dict[str, Any]:
        """Analyze performance metrics"""
        return {
            "sharpe_assessment": (
                "EXCELLENT"
                if risk_metrics.sharpe_ratio > 2.0
                else (
                    "GOOD"
                    if risk_metrics.sharpe_ratio > 1.0
                    else "ACCEPTABLE" if risk_metrics.sharpe_ratio > 0.5 else "POOR"
                )
            ),
            "volatility_assessment": (
                "HIGH" if risk_metrics.volatility > 0.3 else "NORMAL"
            ),
            "drawdown_assessment": (
                "SEVERE"
                if risk_metrics.max_drawdown > 0.3
                else "MODERATE" if risk_metrics.max_drawdown > 0.15 else "ACCEPTABLE"
            ),
        }

    def _analyze_correlation_risk(self, risk_metrics: RiskMetrics) -> Dict[str, Any]:
        """Analyze correlation risk"""
        return {
            "correlation_level": (
                "HIGH"
                if risk_metrics.correlation_risk > 0.8
                else "MODERATE" if risk_metrics.correlation_risk > 0.5 else "LOW"
            ),
            "diversification_benefit": 1 - risk_metrics.correlation_risk,
            "beta_assessment": (
                "HIGH BETA"
                if risk_metrics.beta > 1.5
                else "MARKET-LIKE" if 0.8 <= risk_metrics.beta <= 1.2 else "LOW BETA"
            ),
        }
