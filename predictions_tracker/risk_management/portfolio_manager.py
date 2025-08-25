"""
🚀 PHASE 2B: Portfolio Risk Manager
==================================

Advanced portfolio risk management system for lottery prediction strategies:
- Dynamic position sizing
- Risk budgeting and allocation
- Portfolio optimization under risk constraints
- Real-time risk monitoring and alerts
- Automated risk-based rebalancing
"""

import logging
import warnings
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Tuple, Union

import numpy as np
import pandas as pd
from scipy.optimize import minimize

logger = logging.getLogger(__name__)


@dataclass
class PortfolioPosition:
    """Portfolio position information"""

    strategy_id: str
    strategy_name: str
    current_weight: float
    target_weight: float
    expected_return: float
    volatility: float
    var_contribution: float
    last_updated: datetime

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "strategy_id": self.strategy_id,
            "strategy_name": self.strategy_name,
            "current_weight": self.current_weight,
            "target_weight": self.target_weight,
            "expected_return": self.expected_return,
            "volatility": self.volatility,
            "var_contribution": self.var_contribution,
            "last_updated": self.last_updated.isoformat(),
        }


@dataclass
class RiskBudget:
    """Risk budget configuration"""

    total_risk_budget: float = 0.05  # 5% portfolio VaR limit
    max_individual_contribution: float = 0.4  # 40% max VaR contribution
    min_individual_contribution: float = 0.05  # 5% min VaR contribution
    concentration_limit: float = 0.3  # 30% max weight in single strategy
    max_strategies: int = 10
    rebalancing_frequency: str = "daily"  # daily, weekly, monthly


class PortfolioRiskManager:
    """
    🎯 PHASE 2B: Portfolio Risk Management System

    Comprehensive portfolio risk management for lottery prediction strategies:
    - Risk-based position sizing
    - Dynamic portfolio optimization
    - Real-time risk monitoring
    - Automated rebalancing
    - Performance attribution analysis
    """

    def __init__(self, risk_budget: Optional[RiskBudget] = None):
        """
        Initialize Portfolio Risk Manager

        Args:
            risk_budget: Risk budget configuration
        """
        self.risk_budget = risk_budget or RiskBudget()
        self.positions = {}
        self.portfolio_history = []
        self.rebalancing_history = []

        logger.info("🚀 Portfolio Risk Manager initialized")

    def optimize_portfolio_weights(
        self,
        expected_returns: np.ndarray,
        covariance_matrix: np.ndarray,
        strategy_names: List[str],
        optimization_method: str = "risk_parity",
    ) -> Dict[str, Any]:
        """
        Optimize portfolio weights using specified method

        Args:
            expected_returns: Expected returns for each strategy
            covariance_matrix: Return covariance matrix
            strategy_names: Strategy names
            optimization_method: 'risk_parity', 'min_variance', 'max_sharpe', 'risk_budgeting'

        Returns:
            Dict: Optimization results with weights and metrics
        """
        try:
            n_strategies = len(expected_returns)

            if n_strategies != covariance_matrix.shape[0]:
                raise ValueError(
                    "Dimension mismatch between returns and covariance matrix"
                )

            # Initialize optimization results
            optimization_results = {
                "optimization_timestamp": datetime.now().isoformat(),
                "method": optimization_method,
                "n_strategies": n_strategies,
                "strategy_names": strategy_names,
                "optimal_weights": {},
                "portfolio_metrics": {},
                "optimization_details": {},
            }

            if optimization_method == "risk_parity":
                weights = self._optimize_risk_parity(covariance_matrix)
            elif optimization_method == "min_variance":
                weights = self._optimize_min_variance(covariance_matrix)
            elif optimization_method == "max_sharpe":
                weights = self._optimize_max_sharpe(expected_returns, covariance_matrix)
            elif optimization_method == "risk_budgeting":
                weights = self._optimize_risk_budgeting(
                    expected_returns, covariance_matrix
                )
            else:
                # Equal weight fallback
                weights = np.ones(n_strategies) / n_strategies
                logger.warning(
                    f"⚠️ Unknown optimization method {optimization_method}, using equal weights"
                )

            # Create weight dictionary
            for i, strategy_name in enumerate(strategy_names):
                optimization_results["optimal_weights"][strategy_name] = float(
                    weights[i]
                )

            # Calculate portfolio metrics
            portfolio_return = np.dot(weights, expected_returns)
            portfolio_variance = np.dot(weights, np.dot(covariance_matrix, weights))
            portfolio_volatility = np.sqrt(portfolio_variance)
            sharpe_ratio = (
                portfolio_return / portfolio_volatility
                if portfolio_volatility > 0
                else 0
            )

            optimization_results["portfolio_metrics"] = {
                "expected_return": float(portfolio_return),
                "volatility": float(portfolio_volatility),
                "variance": float(portfolio_variance),
                "sharpe_ratio": float(sharpe_ratio),
            }

            # Calculate risk contributions
            risk_contributions = self._calculate_risk_contributions(
                weights, covariance_matrix
            )
            optimization_results["risk_contributions"] = {
                strategy_names[i]: float(risk_contributions[i])
                for i in range(n_strategies)
            }

            logger.info(
                f"✅ Portfolio optimization completed using {optimization_method}"
            )
            return optimization_results

        except Exception as e:
            logger.error(f"❌ Portfolio optimization failed: {e}")
            # Return equal weights as fallback
            equal_weights = {name: 1.0 / len(strategy_names) for name in strategy_names}
            return {
                "optimization_timestamp": datetime.now().isoformat(),
                "method": optimization_method,
                "optimal_weights": equal_weights,
                "error": str(e),
            }

    def calculate_position_sizing(
        self,
        strategy_metrics: Dict[str, Dict[str, float]],
        current_portfolio_value: float,
        risk_scaling: float = 1.0,
    ) -> Dict[str, PortfolioPosition]:
        """
        Calculate optimal position sizing for strategies

        Args:
            strategy_metrics: Dictionary of strategy performance metrics
            current_portfolio_value: Current portfolio value
            risk_scaling: Risk scaling factor (0.5 = half risk, 2.0 = double risk)

        Returns:
            Dict: Calculated positions for each strategy
        """
        try:
            strategy_names = list(strategy_metrics.keys())
            n_strategies = len(strategy_names)

            if n_strategies == 0:
                return {}

            # Extract expected returns and volatilities
            expected_returns = np.array(
                [
                    strategy_metrics[name].get("expected_return", 0.0)
                    for name in strategy_names
                ]
            )
            volatilities = np.array(
                [
                    strategy_metrics[name].get("volatility", 0.1)
                    for name in strategy_names
                ]
            )

            # Create covariance matrix (simplified approach)
            correlations = (
                np.ones((n_strategies, n_strategies)) * 0.5
            )  # Assume 0.5 correlation
            np.fill_diagonal(correlations, 1.0)
            covariance_matrix = np.outer(volatilities, volatilities) * correlations

            # Optimize portfolio weights
            optimization_result = self.optimize_portfolio_weights(
                expected_returns, covariance_matrix, strategy_names, "risk_budgeting"
            )

            # Calculate positions
            positions = {}
            optimal_weights = optimization_result.get("optimal_weights", {})

            for strategy_name in strategy_names:
                target_weight = optimal_weights.get(strategy_name, 1.0 / n_strategies)

                # Apply risk scaling
                target_weight = target_weight * risk_scaling

                # Apply risk budget constraints
                target_weight = min(target_weight, self.risk_budget.concentration_limit)

                # Calculate VaR contribution
                strategy_volatility = strategy_metrics[strategy_name].get(
                    "volatility", 0.1
                )
                var_contribution = (
                    target_weight * strategy_volatility * 1.65
                )  # Approximate 95% VaR

                position = PortfolioPosition(
                    strategy_id=f"strategy_{hash(strategy_name) % 10000}",
                    strategy_name=strategy_name,
                    current_weight=0.0,  # To be updated with actual positions
                    target_weight=float(target_weight),
                    expected_return=strategy_metrics[strategy_name].get(
                        "expected_return", 0.0
                    ),
                    volatility=strategy_volatility,
                    var_contribution=float(var_contribution),
                    last_updated=datetime.now(),
                )

                positions[strategy_name] = position

            # Renormalize weights to sum to 1
            total_weight = sum(pos.target_weight for pos in positions.values())
            if total_weight > 0:
                for position in positions.values():
                    position.target_weight = position.target_weight / total_weight

            logger.info(f"✅ Position sizing calculated for {n_strategies} strategies")
            return positions

        except Exception as e:
            logger.error(f"❌ Position sizing calculation failed: {e}")
            return {}

    def monitor_portfolio_risk(
        self,
        current_positions: Dict[str, PortfolioPosition],
        returns_data: Optional[np.ndarray] = None,
    ) -> Dict[str, Any]:
        """
        Monitor real-time portfolio risk

        Args:
            current_positions: Current portfolio positions
            returns_data: Historical returns data for risk calculation

        Returns:
            Dict: Portfolio risk monitoring results
        """
        try:
            risk_monitoring = {
                "monitoring_timestamp": datetime.now().isoformat(),
                "portfolio_summary": self._calculate_portfolio_summary(
                    current_positions
                ),
                "risk_metrics": {},
                "risk_limit_status": {},
                "alerts": [],
                "recommendations": [],
            }

            # Calculate portfolio risk metrics
            if returns_data is not None and len(returns_data) > 0:
                risk_monitoring["risk_metrics"] = (
                    self._calculate_portfolio_risk_metrics(
                        current_positions, returns_data
                    )
                )

            # Check risk limits
            risk_monitoring["risk_limit_status"] = self._check_risk_limits(
                current_positions
            )

            # Generate alerts
            risk_monitoring["alerts"] = self._generate_risk_alerts(
                current_positions, risk_monitoring["risk_limit_status"]
            )

            # Generate recommendations
            risk_monitoring["recommendations"] = self._generate_risk_recommendations(
                current_positions, risk_monitoring["risk_limit_status"]
            )

            logger.info("✅ Portfolio risk monitoring completed")
            return risk_monitoring

        except Exception as e:
            logger.error(f"❌ Portfolio risk monitoring failed: {e}")
            return {"error": str(e), "monitoring_timestamp": datetime.now().isoformat()}

    def execute_rebalancing(
        self,
        current_positions: Dict[str, PortfolioPosition],
        target_positions: Dict[str, PortfolioPosition],
        rebalancing_threshold: float = 0.05,
    ) -> Dict[str, Any]:
        """
        Execute portfolio rebalancing

        Args:
            current_positions: Current portfolio positions
            target_positions: Target portfolio positions
            rebalancing_threshold: Minimum weight difference to trigger rebalancing

        Returns:
            Dict: Rebalancing execution results
        """
        try:
            rebalancing_result = {
                "rebalancing_timestamp": datetime.now().isoformat(),
                "rebalancing_triggered": False,
                "trades": [],
                "rebalancing_cost": 0.0,
                "portfolio_changes": {},
                "rebalancing_summary": {},
            }

            # Calculate weight differences
            weight_differences = {}
            for strategy_name in target_positions.keys():
                current_weight = current_positions.get(
                    strategy_name,
                    PortfolioPosition(
                        strategy_id="",
                        strategy_name=strategy_name,
                        current_weight=0.0,
                        target_weight=0.0,
                        expected_return=0.0,
                        volatility=0.0,
                        var_contribution=0.0,
                        last_updated=datetime.now(),
                    ),
                ).current_weight

                target_weight = target_positions[strategy_name].target_weight
                weight_diff = target_weight - current_weight
                weight_differences[strategy_name] = weight_diff

            # Determine if rebalancing is needed
            max_weight_diff = max(abs(diff) for diff in weight_differences.values())

            if max_weight_diff > rebalancing_threshold:
                rebalancing_result["rebalancing_triggered"] = True

                # Generate trades
                for strategy_name, weight_diff in weight_differences.items():
                    if abs(weight_diff) > rebalancing_threshold:
                        trade = {
                            "strategy_name": strategy_name,
                            "current_weight": current_positions.get(
                                strategy_name, target_positions[strategy_name]
                            ).current_weight,
                            "target_weight": target_positions[
                                strategy_name
                            ].target_weight,
                            "weight_change": weight_diff,
                            "trade_direction": "BUY" if weight_diff > 0 else "SELL",
                            "trade_size": abs(weight_diff),
                        }
                        rebalancing_result["trades"].append(trade)

                # Estimate rebalancing cost (simplified)
                total_turnover = (
                    sum(abs(diff) for diff in weight_differences.values()) / 2
                )
                rebalancing_result["rebalancing_cost"] = (
                    total_turnover * 0.001
                )  # 0.1% transaction cost

                # Update position weights (simulation)
                for strategy_name, position in target_positions.items():
                    if strategy_name in current_positions:
                        current_positions[strategy_name].current_weight = (
                            position.target_weight
                        )
                    else:
                        current_positions[strategy_name] = position
                        current_positions[strategy_name].current_weight = (
                            position.target_weight
                        )

            rebalancing_result["rebalancing_summary"] = {
                "strategies_rebalanced": len(rebalancing_result["trades"]),
                "max_weight_change": float(max_weight_diff),
                "total_portfolio_turnover": sum(
                    abs(diff) for diff in weight_differences.values()
                )
                / 2,
                "rebalancing_needed": rebalancing_result["rebalancing_triggered"],
            }

            # Store rebalancing history
            self.rebalancing_history.append(rebalancing_result)

            logger.info(
                f"✅ Rebalancing {'executed' if rebalancing_result['rebalancing_triggered'] else 'not needed'}"
            )
            return rebalancing_result

        except Exception as e:
            logger.error(f"❌ Portfolio rebalancing failed: {e}")
            return {
                "error": str(e),
                "rebalancing_timestamp": datetime.now().isoformat(),
            }

    def generate_portfolio_report(
        self,
        current_positions: Dict[str, PortfolioPosition],
        risk_monitoring: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Generate comprehensive portfolio risk management report

        Args:
            current_positions: Current portfolio positions
            risk_monitoring: Risk monitoring results

        Returns:
            Dict: Detailed portfolio report
        """
        try:
            report = {
                "report_timestamp": datetime.now().isoformat(),
                "executive_summary": {
                    "total_strategies": len(current_positions),
                    "portfolio_risk_level": self._assess_portfolio_risk_level(
                        risk_monitoring
                    ),
                    "diversification_status": self._assess_diversification_status(
                        current_positions
                    ),
                    "rebalancing_needed": self._assess_rebalancing_need(
                        current_positions
                    ),
                    "key_risks": [],
                },
                "position_details": {
                    name: pos.to_dict() for name, pos in current_positions.items()
                },
                "risk_analysis": risk_monitoring,
                "performance_attribution": self._calculate_performance_attribution(
                    current_positions
                ),
                "recommendations": [],
            }

            # Identify key risks
            risk_limit_status = risk_monitoring.get("risk_limit_status", {})
            if risk_limit_status.get("concentration_risk", False):
                report["executive_summary"]["key_risks"].append(
                    "Portfolio concentration risk detected"
                )

            # Generate recommendations
            report["recommendations"] = self._generate_portfolio_recommendations(
                current_positions, risk_monitoring
            )

            logger.info("📊 Portfolio risk management report generated")
            return report

        except Exception as e:
            logger.error(f"❌ Portfolio report generation failed: {e}")
            return {"error": str(e), "report_timestamp": datetime.now().isoformat()}

    def _optimize_risk_parity(self, covariance_matrix: np.ndarray) -> np.ndarray:
        """Optimize for risk parity portfolio"""
        n = covariance_matrix.shape[0]

        def risk_budget_objective(weights):
            portfolio_vol = np.sqrt(np.dot(weights, np.dot(covariance_matrix, weights)))
            marginal_contrib = np.dot(covariance_matrix, weights) / portfolio_vol
            contrib = weights * marginal_contrib
            return np.sum((contrib - contrib.mean()) ** 2)

        constraints = {"type": "eq", "fun": lambda x: np.sum(x) - 1}
        bounds = tuple((0.01, 0.5) for _ in range(n))  # Min 1%, max 50%

        result = minimize(
            risk_budget_objective,
            np.ones(n) / n,
            method="SLSQP",
            bounds=bounds,
            constraints=constraints,
        )

        return result.x if result.success else np.ones(n) / n

    def _optimize_min_variance(self, covariance_matrix: np.ndarray) -> np.ndarray:
        """Optimize for minimum variance portfolio"""
        n = covariance_matrix.shape[0]

        def objective(weights):
            return np.dot(weights, np.dot(covariance_matrix, weights))

        constraints = {"type": "eq", "fun": lambda x: np.sum(x) - 1}
        bounds = tuple((0.0, 1.0) for _ in range(n))

        result = minimize(
            objective,
            np.ones(n) / n,
            method="SLSQP",
            bounds=bounds,
            constraints=constraints,
        )

        return result.x if result.success else np.ones(n) / n

    def _optimize_max_sharpe(
        self, expected_returns: np.ndarray, covariance_matrix: np.ndarray
    ) -> np.ndarray:
        """Optimize for maximum Sharpe ratio portfolio"""
        n = len(expected_returns)

        def negative_sharpe(weights):
            portfolio_return = np.dot(weights, expected_returns)
            portfolio_vol = np.sqrt(np.dot(weights, np.dot(covariance_matrix, weights)))
            return (
                -portfolio_return / portfolio_vol
                if portfolio_vol > 0
                else -portfolio_return
            )

        constraints = {"type": "eq", "fun": lambda x: np.sum(x) - 1}
        bounds = tuple((0.0, 1.0) for _ in range(n))

        result = minimize(
            negative_sharpe,
            np.ones(n) / n,
            method="SLSQP",
            bounds=bounds,
            constraints=constraints,
        )

        return result.x if result.success else np.ones(n) / n

    def _optimize_risk_budgeting(
        self, expected_returns: np.ndarray, covariance_matrix: np.ndarray
    ) -> np.ndarray:
        """Optimize using risk budgeting approach"""
        n = len(expected_returns)

        # Start with risk parity and adjust for expected returns
        risk_parity_weights = self._optimize_risk_parity(covariance_matrix)

        # Adjust for expected returns (tilt towards higher expected returns)
        return_scores = (
            expected_returns - expected_returns.mean()
        ) / expected_returns.std()
        adjusted_weights = risk_parity_weights * (1 + 0.2 * return_scores)  # 20% tilt

        # Renormalize
        return adjusted_weights / np.sum(adjusted_weights)

    def _calculate_risk_contributions(
        self, weights: np.ndarray, covariance_matrix: np.ndarray
    ) -> np.ndarray:
        """Calculate risk contributions for each position"""
        portfolio_vol = np.sqrt(np.dot(weights, np.dot(covariance_matrix, weights)))
        marginal_contrib = np.dot(covariance_matrix, weights) / portfolio_vol
        return weights * marginal_contrib / portfolio_vol

    def _calculate_portfolio_summary(
        self, positions: Dict[str, PortfolioPosition]
    ) -> Dict[str, Any]:
        """Calculate portfolio summary statistics"""
        if not positions:
            return {"total_strategies": 0, "total_weight": 0.0}

        return {
            "total_strategies": len(positions),
            "total_weight": sum(pos.current_weight for pos in positions.values()),
            "max_position_weight": max(
                pos.current_weight for pos in positions.values()
            ),
            "min_position_weight": min(
                pos.current_weight for pos in positions.values()
            ),
            "avg_position_weight": np.mean(
                [pos.current_weight for pos in positions.values()]
            ),
            "weight_concentration": (
                max(pos.current_weight for pos in positions.values())
                / sum(pos.current_weight for pos in positions.values())
                if sum(pos.current_weight for pos in positions.values()) > 0
                else 0
            ),
        }

    def _calculate_portfolio_risk_metrics(
        self, positions: Dict[str, PortfolioPosition], returns_data: np.ndarray
    ) -> Dict[str, float]:
        """Calculate portfolio risk metrics"""
        # Simplified risk metrics calculation
        weights = np.array([pos.current_weight for pos in positions.values()])

        if len(returns_data.shape) == 1:
            # Single strategy returns
            portfolio_returns = returns_data
        else:
            # Multiple strategy returns
            portfolio_returns = np.dot(returns_data, weights)

        return {
            "portfolio_volatility": float(np.std(portfolio_returns) * np.sqrt(252)),
            "portfolio_var_95": float(np.percentile(portfolio_returns, 5)),
            "portfolio_var_99": float(np.percentile(portfolio_returns, 1)),
            "max_drawdown": float(self._calculate_max_drawdown(portfolio_returns)),
            "sharpe_ratio": float(
                np.mean(portfolio_returns) / np.std(portfolio_returns) * np.sqrt(252)
            ),
        }

    def _calculate_max_drawdown(self, returns: np.ndarray) -> float:
        """Calculate maximum drawdown"""
        cumulative = np.cumprod(1 + returns)
        peak = np.maximum.accumulate(cumulative)
        drawdown = (cumulative - peak) / peak
        return np.min(drawdown)

    def _check_risk_limits(
        self, positions: Dict[str, PortfolioPosition]
    ) -> Dict[str, bool]:
        """Check portfolio against risk limits"""
        if not positions:
            return {}

        max_weight = max(pos.current_weight for pos in positions.values())
        total_var_contribution = sum(pos.var_contribution for pos in positions.values())

        return {
            "concentration_risk": max_weight > self.risk_budget.concentration_limit,
            "var_budget_exceeded": total_var_contribution
            > self.risk_budget.total_risk_budget,
            "too_many_strategies": len(positions) > self.risk_budget.max_strategies,
            "individual_var_limit": any(
                pos.var_contribution > self.risk_budget.max_individual_contribution
                for pos in positions.values()
            ),
        }

    def _generate_risk_alerts(
        self,
        positions: Dict[str, PortfolioPosition],
        risk_limit_status: Dict[str, bool],
    ) -> List[Dict[str, Any]]:
        """Generate risk alerts"""
        alerts = []

        for risk_type, exceeded in risk_limit_status.items():
            if exceeded:
                alerts.append(
                    {
                        "alert_type": risk_type.upper(),
                        "severity": "HIGH",
                        "message": f"{risk_type.replace('_', ' ').title()} limit exceeded",
                        "timestamp": datetime.now().isoformat(),
                    }
                )

        return alerts

    def _generate_risk_recommendations(
        self,
        positions: Dict[str, PortfolioPosition],
        risk_limit_status: Dict[str, bool],
    ) -> List[str]:
        """Generate risk management recommendations"""
        recommendations = []

        if risk_limit_status.get("concentration_risk", False):
            recommendations.append("Reduce concentration in largest positions")

        if risk_limit_status.get("var_budget_exceeded", False):
            recommendations.append("Reduce overall portfolio risk exposure")

        if not positions:
            recommendations.append("Establish initial portfolio positions")

        return recommendations

    def _assess_portfolio_risk_level(self, risk_monitoring: Dict[str, Any]) -> str:
        """Assess overall portfolio risk level"""
        alerts = risk_monitoring.get("alerts", [])

        if len(alerts) > 2:
            return "HIGH"
        elif len(alerts) > 0:
            return "MODERATE"
        else:
            return "LOW"

    def _assess_diversification_status(
        self, positions: Dict[str, PortfolioPosition]
    ) -> str:
        """Assess portfolio diversification status"""
        if not positions:
            return "NO_POSITIONS"

        max_weight = (
            max(pos.current_weight for pos in positions.values()) if positions else 0
        )

        if max_weight > 0.5:
            return "POOR"
        elif max_weight > 0.3:
            return "MODERATE"
        else:
            return "GOOD"

    def _assess_rebalancing_need(self, positions: Dict[str, PortfolioPosition]) -> bool:
        """Assess if rebalancing is needed"""
        if not positions:
            return False

        # Check if any position deviates significantly from target
        return any(
            abs(pos.current_weight - pos.target_weight) > 0.05
            for pos in positions.values()
        )

    def _calculate_performance_attribution(
        self, positions: Dict[str, PortfolioPosition]
    ) -> Dict[str, float]:
        """Calculate performance attribution"""
        if not positions:
            return {}

        total_expected_return = sum(
            pos.current_weight * pos.expected_return for pos in positions.values()
        )

        return {
            "total_expected_return": float(total_expected_return),
            "strategy_contributions": {
                name: float(pos.current_weight * pos.expected_return)
                for name, pos in positions.items()
            },
        }

    def _generate_portfolio_recommendations(
        self, positions: Dict[str, PortfolioPosition], risk_monitoring: Dict[str, Any]
    ) -> List[str]:
        """Generate comprehensive portfolio recommendations"""
        recommendations = []

        # Add risk-based recommendations
        risk_recommendations = risk_monitoring.get("recommendations", [])
        recommendations.extend(risk_recommendations)

        # Add position-specific recommendations
        if positions:
            max_position = max(positions.values(), key=lambda x: x.current_weight)
            if max_position.current_weight > 0.4:
                recommendations.append(
                    f"Consider reducing exposure to {max_position.strategy_name}"
                )

        return recommendations
