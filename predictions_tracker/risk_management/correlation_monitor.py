"""
🚀 PHASE 2B: Correlation Monitor
==============================

Advanced correlation monitoring system for lottery prediction strategies:
- Real-time correlation tracking
- Regime change detection
- Rolling correlation analysis
- Cross-strategy correlation monitoring
- Dynamic correlation-based risk adjustments
"""

import logging
import warnings
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Tuple

import numpy as np
import pandas as pd
from scipy import stats
from sklearn.covariance import LedoitWolf

logger = logging.getLogger(__name__)


class CorrelationMonitor:
    """
    🎯 PHASE 2B: Correlation Monitoring System

    Comprehensive correlation analysis and monitoring for lottery prediction strategies:
    - Dynamic correlation tracking
    - Regime change detection
    - Correlation breakdown alerts
    - Portfolio diversification monitoring
    """

    def __init__(self, lookback_window: int = 90, min_observations: int = 20):
        """
        Initialize Correlation Monitor

        Args:
            lookback_window: Rolling window for correlation calculation
            min_observations: Minimum observations required for correlation
        """
        self.lookback_window = lookback_window
        self.min_observations = min_observations
        self.correlation_history = {}
        self.regime_thresholds = {
            "low_correlation": 0.3,
            "moderate_correlation": 0.6,
            "high_correlation": 0.8,
        }

        logger.info(
            f"🚀 Correlation Monitor initialized (window: {lookback_window} days)"
        )

    def calculate_rolling_correlations(
        self,
        returns_matrix: np.ndarray,
        strategy_names: List[str],
        window_size: Optional[int] = None,
    ) -> Dict[str, Any]:
        """
        Calculate rolling correlations between strategies

        Args:
            returns_matrix: Returns matrix (time x strategies)
            strategy_names: Names of strategies
            window_size: Rolling window size

        Returns:
            Dict: Rolling correlation analysis results
        """
        try:
            if window_size is None:
                window_size = self.lookback_window

            n_periods, n_strategies = returns_matrix.shape

            if n_periods < self.min_observations:
                logger.warning("⚠️ Insufficient data for correlation analysis")
                return self._default_correlation_results(strategy_names)

            # Calculate rolling correlations
            rolling_correlations = []
            correlation_dates = []

            for i in range(window_size - 1, n_periods):
                window_data = returns_matrix[i - window_size + 1 : i + 1]

                # Calculate correlation matrix for this window
                with warnings.catch_warnings():
                    warnings.simplefilter("ignore")
                    corr_matrix = np.corrcoef(window_data.T)

                # Handle NaN values
                if np.any(np.isnan(corr_matrix)):
                    corr_matrix = np.nan_to_num(corr_matrix, nan=0.0)
                    np.fill_diagonal(corr_matrix, 1.0)

                rolling_correlations.append(corr_matrix)
                correlation_dates.append(i)

            # Analyze correlation patterns
            results = {
                "calculation_timestamp": datetime.now().isoformat(),
                "analysis_period": f"{n_periods} periods",
                "window_size": window_size,
                "strategy_names": strategy_names,
                "current_correlations": self._extract_current_correlations(
                    rolling_correlations[-1], strategy_names
                ),
                "correlation_statistics": self._calculate_correlation_statistics(
                    rolling_correlations, strategy_names
                ),
                "regime_analysis": self._analyze_correlation_regimes(
                    rolling_correlations
                ),
                "diversification_metrics": self._calculate_diversification_metrics(
                    rolling_correlations[-1]
                ),
            }

            # Store in history
            self.correlation_history[datetime.now().isoformat()] = results

            logger.info(
                f"✅ Rolling correlations calculated for {n_strategies} strategies"
            )
            return results

        except Exception as e:
            logger.error(f"❌ Rolling correlation calculation failed: {e}")
            return self._default_correlation_results(strategy_names)

    def detect_correlation_regime_changes(
        self, correlation_history: List[np.ndarray], lookback_periods: int = 20
    ) -> Dict[str, Any]:
        """
        Detect correlation regime changes

        Args:
            correlation_history: Historical correlation matrices
            lookback_periods: Periods to look back for regime change detection

        Returns:
            Dict: Regime change detection results
        """
        try:
            if len(correlation_history) < lookback_periods:
                return {"regime_changes": [], "current_regime": "STABLE"}

            # Calculate average correlations over time
            avg_correlations = []
            for corr_matrix in correlation_history:
                # Extract upper triangular correlations (excluding diagonal)
                mask = np.triu(np.ones_like(corr_matrix, dtype=bool), k=1)
                avg_corr = np.mean(corr_matrix[mask])
                avg_correlations.append(avg_corr)

            # Detect significant changes
            regime_changes = []
            current_regime = self._classify_correlation_regime(avg_correlations[-1])

            # Look for significant changes in recent periods
            if len(avg_correlations) >= lookback_periods:
                recent_period = avg_correlations[-lookback_periods:]
                historical_period = avg_correlations[
                    -2 * lookback_periods : -lookback_periods
                ]

                if len(historical_period) > 0:
                    recent_avg = np.mean(recent_period)
                    historical_avg = np.mean(historical_period)

                    # Statistical test for regime change
                    t_stat, p_value = stats.ttest_ind(recent_period, historical_period)

                    if p_value < 0.05 and abs(recent_avg - historical_avg) > 0.1:
                        regime_changes.append(
                            {
                                "change_type": "CORRELATION_SHIFT",
                                "direction": (
                                    "INCREASE"
                                    if recent_avg > historical_avg
                                    else "DECREASE"
                                ),
                                "magnitude": abs(recent_avg - historical_avg),
                                "t_statistic": t_stat,
                                "p_value": p_value,
                                "detection_timestamp": datetime.now().isoformat(),
                            }
                        )

            results = {
                "regime_changes": regime_changes,
                "current_regime": current_regime,
                "correlation_trend": self._analyze_correlation_trend(
                    avg_correlations[-10:]
                ),
                "regime_stability": len(regime_changes) == 0,
            }

            logger.info(
                f"✅ Regime change detection: {current_regime} regime, {len(regime_changes)} changes"
            )
            return results

        except Exception as e:
            logger.error(f"❌ Regime change detection failed: {e}")
            return {"regime_changes": [], "current_regime": "UNKNOWN", "error": str(e)}

    def monitor_correlation_breakdown(
        self,
        current_correlations: np.ndarray,
        baseline_correlations: np.ndarray,
        threshold: float = 0.2,
    ) -> Dict[str, Any]:
        """
        Monitor for correlation breakdown events

        Args:
            current_correlations: Current correlation matrix
            baseline_correlations: Baseline/historical correlation matrix
            threshold: Threshold for significant correlation change

        Returns:
            Dict: Correlation breakdown analysis
        """
        try:
            # Calculate correlation differences
            correlation_diff = current_correlations - baseline_correlations

            # Find significant changes
            n_strategies = current_correlations.shape[0]
            breakdown_events = []

            for i in range(n_strategies):
                for j in range(i + 1, n_strategies):
                    current_corr = current_correlations[i, j]
                    baseline_corr = baseline_correlations[i, j]
                    diff = abs(current_corr - baseline_corr)

                    if diff > threshold:
                        breakdown_events.append(
                            {
                                "strategy_pair": (i, j),
                                "current_correlation": float(current_corr),
                                "baseline_correlation": float(baseline_corr),
                                "change": float(current_corr - baseline_corr),
                                "change_magnitude": float(diff),
                                "severity": (
                                    "HIGH"
                                    if diff > 0.4
                                    else "MODERATE" if diff > 0.3 else "LOW"
                                ),
                            }
                        )

            # Overall breakdown assessment
            max_change = np.max(np.abs(correlation_diff))
            avg_change = np.mean(
                np.abs(correlation_diff[np.triu_indices(n_strategies, k=1)])
            )

            breakdown_analysis = {
                "breakdown_detected": len(breakdown_events) > 0,
                "breakdown_events": breakdown_events,
                "overall_assessment": {
                    "max_correlation_change": float(max_change),
                    "avg_correlation_change": float(avg_change),
                    "affected_pairs": len(breakdown_events),
                    "breakdown_severity": self._assess_breakdown_severity(
                        breakdown_events
                    ),
                },
                "risk_implications": self._assess_breakdown_risk_implications(
                    breakdown_events
                ),
                "recommended_actions": self._recommend_breakdown_actions(
                    breakdown_events
                ),
            }

            logger.info(
                f"✅ Correlation breakdown monitoring: {len(breakdown_events)} events detected"
            )
            return breakdown_analysis

        except Exception as e:
            logger.error(f"❌ Correlation breakdown monitoring failed: {e}")
            return {"breakdown_detected": False, "error": str(e)}

    def calculate_dynamic_correlations(
        self, returns_matrix: np.ndarray, method: str = "ewma", alpha: float = 0.94
    ) -> np.ndarray:
        """
        Calculate dynamic/time-varying correlations

        Args:
            returns_matrix: Returns matrix (time x strategies)
            method: 'ewma' (exponentially weighted) or 'dcc' (dynamic conditional correlation)
            alpha: Decay factor for EWMA

        Returns:
            np.ndarray: Dynamic correlation matrix
        """
        try:
            n_periods, n_strategies = returns_matrix.shape

            if method == "ewma":
                # Exponentially Weighted Moving Average correlations
                weights = np.array([(1 - alpha) * (alpha**i) for i in range(n_periods)])
                weights = weights / np.sum(weights)  # Normalize

                # Calculate weighted covariance matrix
                mean_returns = np.average(returns_matrix, weights=weights, axis=0)
                centered_returns = returns_matrix - mean_returns

                weighted_cov = np.zeros((n_strategies, n_strategies))
                for t in range(n_periods):
                    outer_product = np.outer(centered_returns[t], centered_returns[t])
                    weighted_cov += weights[t] * outer_product

                # Convert to correlation matrix
                std_devs = np.sqrt(np.diag(weighted_cov))
                correlation_matrix = weighted_cov / np.outer(std_devs, std_devs)

            elif method == "ledoit_wolf":
                # Ledoit-Wolf shrinkage estimator
                lw = LedoitWolf()
                shrunk_cov = lw.fit(returns_matrix).covariance_

                # Convert to correlation
                std_devs = np.sqrt(np.diag(shrunk_cov))
                correlation_matrix = shrunk_cov / np.outer(std_devs, std_devs)

            else:
                # Fallback to simple correlation
                correlation_matrix = np.corrcoef(returns_matrix.T)

            # Handle NaN values
            correlation_matrix = np.nan_to_num(correlation_matrix, nan=0.0)
            np.fill_diagonal(correlation_matrix, 1.0)

            logger.info(f"✅ Dynamic correlations calculated using {method} method")
            return correlation_matrix

        except Exception as e:
            logger.error(f"❌ Dynamic correlation calculation failed: {e}")
            # Return identity matrix as fallback
            return np.eye(returns_matrix.shape[1])

    def generate_correlation_report(
        self, correlation_analysis: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Generate comprehensive correlation monitoring report

        Args:
            correlation_analysis: Results from correlation analysis

        Returns:
            Dict: Detailed correlation report
        """
        try:
            report = {
                "report_timestamp": datetime.now().isoformat(),
                "executive_summary": {
                    "overall_correlation_level": self._assess_overall_correlation_level(
                        correlation_analysis
                    ),
                    "diversification_status": correlation_analysis.get(
                        "diversification_metrics", {}
                    ).get("effective_diversification", "UNKNOWN"),
                    "regime_stability": correlation_analysis.get(
                        "regime_analysis", {}
                    ).get("current_regime", "STABLE"),
                    "key_concerns": [],
                },
                "detailed_analysis": {
                    "current_correlations": correlation_analysis.get(
                        "current_correlations", {}
                    ),
                    "correlation_statistics": correlation_analysis.get(
                        "correlation_statistics", {}
                    ),
                    "regime_analysis": correlation_analysis.get("regime_analysis", {}),
                    "diversification_metrics": correlation_analysis.get(
                        "diversification_metrics", {}
                    ),
                },
                "risk_assessment": {
                    "correlation_risk_level": self._assess_correlation_risk_level(
                        correlation_analysis
                    ),
                    "portfolio_concentration": self._assess_portfolio_concentration(
                        correlation_analysis
                    ),
                    "regime_change_risk": self._assess_regime_change_risk(
                        correlation_analysis
                    ),
                },
                "recommendations": [],
            }

            # Generate key concerns
            current_corrs = correlation_analysis.get("current_correlations", {})
            if any(corr > 0.8 for corr in current_corrs.values()):
                report["executive_summary"]["key_concerns"].append(
                    "High correlation detected between strategies"
                )

            # Generate recommendations
            report["recommendations"] = self._generate_correlation_recommendations(
                correlation_analysis
            )

            logger.info("📊 Correlation monitoring report generated")
            return report

        except Exception as e:
            logger.error(f"❌ Correlation report generation failed: {e}")
            return {"error": str(e), "report_timestamp": datetime.now().isoformat()}

    def _default_correlation_results(self, strategy_names: List[str]) -> Dict[str, Any]:
        """Return default correlation results for insufficient data"""
        n_strategies = len(strategy_names)
        return {
            "calculation_timestamp": datetime.now().isoformat(),
            "analysis_period": "Insufficient data",
            "strategy_names": strategy_names,
            "current_correlations": {
                f"{strategy_names[i]}_vs_{strategy_names[j]}": 0.5
                for i in range(n_strategies)
                for j in range(i + 1, n_strategies)
            },
            "correlation_statistics": {
                "avg_correlation": 0.5,
                "max_correlation": 0.6,
                "min_correlation": 0.4,
            },
            "regime_analysis": {"current_regime": "STABLE"},
            "diversification_metrics": {"effective_strategies": n_strategies * 0.7},
        }

    def _extract_current_correlations(
        self, corr_matrix: np.ndarray, strategy_names: List[str]
    ) -> Dict[str, float]:
        """Extract current correlations as labeled dictionary"""
        correlations = {}
        n_strategies = len(strategy_names)

        for i in range(n_strategies):
            for j in range(i + 1, n_strategies):
                key = f"{strategy_names[i]}_vs_{strategy_names[j]}"
                correlations[key] = float(corr_matrix[i, j])

        return correlations

    def _calculate_correlation_statistics(
        self, correlation_history: List[np.ndarray], strategy_names: List[str]
    ) -> Dict[str, float]:
        """Calculate correlation statistics over time"""
        # Extract upper triangular correlations from all periods
        all_correlations = []
        for corr_matrix in correlation_history:
            mask = np.triu(np.ones_like(corr_matrix, dtype=bool), k=1)
            all_correlations.extend(corr_matrix[mask])

        return {
            "avg_correlation": float(np.mean(all_correlations)),
            "std_correlation": float(np.std(all_correlations)),
            "max_correlation": float(np.max(all_correlations)),
            "min_correlation": float(np.min(all_correlations)),
            "median_correlation": float(np.median(all_correlations)),
        }

    def _analyze_correlation_regimes(
        self, correlation_history: List[np.ndarray]
    ) -> Dict[str, Any]:
        """Analyze correlation regimes"""
        avg_correlations = []
        for corr_matrix in correlation_history:
            mask = np.triu(np.ones_like(corr_matrix, dtype=bool), k=1)
            avg_corr = np.mean(corr_matrix[mask])
            avg_correlations.append(avg_corr)

        current_regime = self._classify_correlation_regime(avg_correlations[-1])
        regime_stability = (
            np.std(avg_correlations[-10:]) < 0.1
            if len(avg_correlations) >= 10
            else True
        )

        return {
            "current_regime": current_regime,
            "regime_stability": regime_stability,
            "avg_correlation_trend": float(np.mean(avg_correlations)),
            "correlation_volatility": float(np.std(avg_correlations)),
        }

    def _calculate_diversification_metrics(
        self, corr_matrix: np.ndarray
    ) -> Dict[str, float]:
        """Calculate diversification metrics"""
        n_strategies = corr_matrix.shape[0]

        # Effective number of strategies (based on correlation)
        avg_correlation = np.mean(corr_matrix[np.triu_indices(n_strategies, k=1)])
        effective_strategies = 1 + (n_strategies - 1) * (1 - avg_correlation) / (
            1 + (n_strategies - 1) * avg_correlation
        )

        # Diversification ratio
        diversification_ratio = effective_strategies / n_strategies

        return {
            "effective_strategies": float(effective_strategies),
            "diversification_ratio": float(diversification_ratio),
            "avg_pairwise_correlation": float(avg_correlation),
            "max_correlation": float(np.max(corr_matrix - np.eye(n_strategies))),
            "effective_diversification": (
                "HIGH"
                if diversification_ratio > 0.8
                else "MODERATE" if diversification_ratio > 0.6 else "LOW"
            ),
        }

    def _classify_correlation_regime(self, avg_correlation: float) -> str:
        """Classify correlation regime"""
        if avg_correlation < self.regime_thresholds["low_correlation"]:
            return "LOW_CORRELATION"
        elif avg_correlation < self.regime_thresholds["moderate_correlation"]:
            return "MODERATE_CORRELATION"
        elif avg_correlation < self.regime_thresholds["high_correlation"]:
            return "HIGH_CORRELATION"
        else:
            return "EXTREME_CORRELATION"

    def _analyze_correlation_trend(self, recent_correlations: List[float]) -> str:
        """Analyze recent correlation trend"""
        if len(recent_correlations) < 2:
            return "STABLE"

        slope = np.polyfit(range(len(recent_correlations)), recent_correlations, 1)[0]

        if slope > 0.01:
            return "INCREASING"
        elif slope < -0.01:
            return "DECREASING"
        else:
            return "STABLE"

    def _assess_breakdown_severity(self, breakdown_events: List[Dict]) -> str:
        """Assess overall breakdown severity"""
        if not breakdown_events:
            return "NONE"

        high_severity_count = sum(
            1 for event in breakdown_events if event["severity"] == "HIGH"
        )

        if high_severity_count > 0:
            return "HIGH"
        elif len(breakdown_events) > 3:
            return "MODERATE"
        else:
            return "LOW"

    def _assess_breakdown_risk_implications(
        self, breakdown_events: List[Dict]
    ) -> List[str]:
        """Assess risk implications of correlation breakdown"""
        implications = []

        if breakdown_events:
            implications.append("Reduced diversification benefits")
            implications.append("Increased portfolio volatility risk")

            high_severity_events = [
                e for e in breakdown_events if e["severity"] == "HIGH"
            ]
            if high_severity_events:
                implications.append("Potential concentration risk")
                implications.append("Strategy correlation regime change")

        return implications

    def _recommend_breakdown_actions(self, breakdown_events: List[Dict]) -> List[str]:
        """Recommend actions for correlation breakdown"""
        recommendations = []

        if breakdown_events:
            recommendations.append("Monitor correlation patterns closely")
            recommendations.append("Consider rebalancing portfolio weights")

            high_severity_events = [
                e for e in breakdown_events if e["severity"] == "HIGH"
            ]
            if high_severity_events:
                recommendations.append(
                    "Reduce position sizes in highly correlated strategies"
                )
                recommendations.append("Seek additional uncorrelated strategies")

        return recommendations

    def _assess_overall_correlation_level(
        self, correlation_analysis: Dict[str, Any]
    ) -> str:
        """Assess overall correlation level"""
        stats = correlation_analysis.get("correlation_statistics", {})
        avg_corr = stats.get("avg_correlation", 0.5)

        return self._classify_correlation_regime(avg_corr)

    def _assess_correlation_risk_level(
        self, correlation_analysis: Dict[str, Any]
    ) -> str:
        """Assess correlation risk level"""
        stats = correlation_analysis.get("correlation_statistics", {})
        avg_corr = stats.get("avg_correlation", 0.5)
        max_corr = stats.get("max_correlation", 0.6)

        if max_corr > 0.9 or avg_corr > 0.8:
            return "HIGH"
        elif max_corr > 0.7 or avg_corr > 0.6:
            return "MODERATE"
        else:
            return "LOW"

    def _assess_portfolio_concentration(
        self, correlation_analysis: Dict[str, Any]
    ) -> str:
        """Assess portfolio concentration risk"""
        diversification = correlation_analysis.get("diversification_metrics", {})
        div_ratio = diversification.get("diversification_ratio", 0.7)

        if div_ratio < 0.5:
            return "HIGH_CONCENTRATION"
        elif div_ratio < 0.7:
            return "MODERATE_CONCENTRATION"
        else:
            return "WELL_DIVERSIFIED"

    def _assess_regime_change_risk(self, correlation_analysis: Dict[str, Any]) -> str:
        """Assess regime change risk"""
        regime = correlation_analysis.get("regime_analysis", {})
        stability = regime.get("regime_stability", True)

        return "LOW" if stability else "HIGH"

    def _generate_correlation_recommendations(
        self, correlation_analysis: Dict[str, Any]
    ) -> List[str]:
        """Generate correlation-based recommendations"""
        recommendations = []

        # Check correlation levels
        stats = correlation_analysis.get("correlation_statistics", {})
        avg_corr = stats.get("avg_correlation", 0.5)

        if avg_corr > 0.8:
            recommendations.append(
                "High correlation detected - consider strategy diversification"
            )

        # Check diversification
        diversification = correlation_analysis.get("diversification_metrics", {})
        if diversification.get("effective_diversification") == "LOW":
            recommendations.append("Low diversification - add uncorrelated strategies")

        # Check regime stability
        regime = correlation_analysis.get("regime_analysis", {})
        if not regime.get("regime_stability", True):
            recommendations.append(
                "Correlation regime instability - increase monitoring frequency"
            )

        return recommendations
