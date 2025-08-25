"""
🚀 PHASE 2B: RISK MANAGEMENT & ADVANCED ANALYTICS
===========================================================

Risk Management Package for Lottery Prediction System

Components:
- Value at Risk (VaR) calculations
- Expected Shortfall analysis
- Correlation monitoring
- Portfolio risk management
"""

__version__ = "2.1.0"
__author__ = "xoso_crawler"
__package_name__ = "Risk Management & Advanced Analytics"

from .correlation_monitor import CorrelationMonitor
from .portfolio_manager import PortfolioRiskManager
from .risk_engine import RiskManagementEngine
from .var_calculator import VaRCalculator

__all__ = [
    "RiskManagementEngine",
    "VaRCalculator",
    "CorrelationMonitor",
    "PortfolioRiskManager",
]
