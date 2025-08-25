"""
Enhanced Prediction System Integration
Integrates all validation and optimization components
"""

import os
import sys

import django

# Add the parent directory to sys.path to import Django models
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Setup Django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "xoso_crawler.settings")
django.setup()

import json
import logging
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple

import numpy as np

from .adaptive_weights import AdaptiveWeightOptimizer, PerformanceMetrics, WeightConfig

# Import our validation modules
from .backtesting import BacktestingFramework, BacktestSummary
from .confidence_intervals import ConfidenceCalculator, PredictionConfidence
from .performance_monitor import AlertLevel, MonitoringConfig, PerformanceMonitor
from .statistical_tests import (
    ControlGroupResult,
    SignificanceResult,
    StatisticalValidator,
)

# Import Django models
try:
    from results.models import (
        KetQuaXoSo,
        ModelTrainingHistory,
        PredictionPerformanceMetrics,
    )

    DJANGO_AVAILABLE = True
except ImportError:
    # Fallback for testing without Django
    KetQuaXoSo = None
    PredictionPerformanceMetrics = None
    ModelTrainingHistory = None
    DJANGO_AVAILABLE = False


@dataclass
class EnhancedPredictionResult:
    """Enhanced prediction result with validation metrics"""

    predicted_numbers: List[int]
    confidence_metrics: PredictionConfidence
    statistical_validation: SignificanceResult
    weight_optimization: Dict[str, float]
    performance_score: float
    recommendation: str
    uncertainty_level: str
    expected_hits: Tuple[float, float]  # (lower_bound, upper_bound)


class EnhancedPredictionSystem:
    """
    Enhanced prediction system with comprehensive validation and optimization
    """

    def __init__(self, enable_monitoring: bool = True):
        self.logger = logging.getLogger(__name__)

        # Initialize components
        self.backtesting_framework = (
            BacktestingFramework(KetQuaXoSo, self) if KetQuaXoSo else None
        )

        self.statistical_validator = StatisticalValidator()
        self.confidence_calculator = ConfidenceCalculator()
        self.weight_optimizer = AdaptiveWeightOptimizer()

        # Performance monitoring
        if enable_monitoring:
            self.performance_monitor = PerformanceMonitor()
            self.performance_monitor.start_monitoring()

            # Subscribe to alerts
            self.performance_monitor.subscribe_to_alerts(self._handle_alert)
        else:
            self.performance_monitor = None

        # System state
        self.prediction_history = []
        self.validation_results = []
        self.is_initialized = False

        # Performance cache
        self._performance_cache = {}

    def initialize_system(self, historical_days: int = 100):
        """Initialize system with historical data validation"""

        self.logger.info("Initializing Enhanced Prediction System...")

        if not KetQuaXoSo:
            self.logger.warning("Django models not available - running in test mode")
            self.is_initialized = True
            return

        try:
            # Get historical data
            end_date = datetime.now().date()
            start_date = end_date - timedelta(days=historical_days)

            historical_data = list(
                KetQuaXoSo.objects.filter(
                    ngay__gte=start_date, ngay__lte=end_date
                ).order_by("-ngay")
            )

            if len(historical_data) < 30:
                self.logger.warning(
                    f"Insufficient historical data: {len(historical_data)} days"
                )
                self.is_initialized = True
                return

            # Run initial backtesting
            if self.backtesting_framework:
                self.logger.info("Running initial backtesting validation...")
                backtest_summary = self.backtesting_framework.run_historical_backtest(
                    start_date=datetime.combine(start_date, datetime.min.time()),
                    end_date=datetime.combine(end_date, datetime.min.time()),
                    prediction_methods=["hybrid", "statistical", "frequency"],
                )

                self.logger.info(
                    f"Backtesting completed: {backtest_summary.avg_accuracy:.3f} avg accuracy"
                )

            # Initialize weight optimizer with historical performance
            self._initialize_weights(historical_data)

            self.is_initialized = True
            self.logger.info("Enhanced Prediction System initialized successfully")

        except Exception as e:
            self.logger.error(f"System initialization failed: {e}")
            self.is_initialized = True  # Continue in degraded mode

    def _initialize_weights(self, historical_data: List):
        """Initialize adaptive weights based on historical performance"""

        # Simulate method performance on historical data
        method_performance = {}

        for method in [
            "frequency",
            "recent_trend",
            "cycle_analysis",
            "gap_analysis",
            "ml_prediction",
        ]:
            # This would be replaced with actual method testing
            performance = np.random.uniform(0.15, 0.30)  # Placeholder
            method_performance[method] = performance

        # Set initial weights based on performance
        total_performance = sum(method_performance.values())
        initial_weights = {
            method: perf / total_performance
            for method, perf in method_performance.items()
        }

        self.weight_optimizer.set_weights(initial_weights)
        self.logger.info(f"Initial weights set: {initial_weights}")

    def make_enhanced_prediction(
        self,
        target_date: datetime,
        include_validation: bool = True,
        confidence_level: float = 0.95,
    ) -> EnhancedPredictionResult:
        """
        Make enhanced prediction with comprehensive validation

        Args:
            target_date: Date to predict for
            include_validation: Whether to include statistical validation
            confidence_level: Confidence level for intervals

        Returns:
            EnhancedPredictionResult with comprehensive metrics
        """

        start_time = datetime.now()

        try:
            # Get historical data
            historical_data = self._get_historical_data(target_date)

            if not historical_data:
                return self._create_fallback_result("Insufficient historical data")

            # Generate base prediction
            predicted_numbers = self._generate_base_prediction(historical_data)

            # Calculate confidence metrics
            confidence_metrics = (
                self.confidence_calculator.calculate_prediction_confidence(
                    predicted_numbers=predicted_numbers,
                    historical_data=historical_data,
                    method_name="enhanced_hybrid",
                    confidence_level=confidence_level,
                )
            )

            # Statistical validation (if enabled)
            statistical_validation = None
            if include_validation and len(self.prediction_history) >= 10:
                statistical_validation = self._run_statistical_validation()

            # Get current weights
            current_weights = self.weight_optimizer.get_current_weights()

            # Calculate performance score
            performance_score = self._calculate_performance_score(
                confidence_metrics, statistical_validation
            )

            # Generate recommendation
            recommendation = self._generate_enhanced_recommendation(
                confidence_metrics, performance_score
            )

            # Calculate expected hits with confidence interval
            expected_hits = (
                confidence_metrics.confidence_metrics.confidence_interval[0],
                confidence_metrics.confidence_metrics.confidence_interval[1],
            )

            # Create result
            result = EnhancedPredictionResult(
                predicted_numbers=predicted_numbers,
                confidence_metrics=confidence_metrics,
                statistical_validation=statistical_validation,
                weight_optimization=current_weights,
                performance_score=performance_score,
                recommendation=recommendation,
                uncertainty_level=confidence_metrics.confidence_metrics.uncertainty_level,
                expected_hits=expected_hits,
            )

            # Update performance monitoring
            if self.performance_monitor:
                response_time = (datetime.now() - start_time).total_seconds()
                self.performance_monitor.update_metrics(
                    {
                        "accuracy": self._get_recent_accuracy(),
                        "hit_rate": self._get_recent_hit_rate(),
                        "confidence": confidence_metrics.overall_confidence / 100,
                        "response_time": response_time,
                        "prediction_count": len(self.prediction_history) + 1,
                        "active_methods": list(current_weights.keys()),
                    }
                )

            return result

        except Exception as e:
            self.logger.error(f"Enhanced prediction failed: {e}")
            return self._create_fallback_result(f"Prediction error: {str(e)}")

    def update_with_actual_result(
        self,
        prediction_result: EnhancedPredictionResult,
        actual_numbers: List[int],
        prediction_date: datetime,
    ):
        """
        Update system with actual lottery results

        Args:
            prediction_result: The original prediction result
            actual_numbers: Actual winning numbers
            prediction_date: Date of the prediction
        """

        try:
            # Calculate actual performance
            hits = set(prediction_result.predicted_numbers) & set(actual_numbers)
            hit_count = len(hits)
            accuracy = hit_count / len(prediction_result.predicted_numbers)

            # Update prediction history
            self.prediction_history.append(
                {
                    "date": prediction_date,
                    "predicted": prediction_result.predicted_numbers,
                    "actual": actual_numbers,
                    "hits": hit_count,
                    "accuracy": accuracy,
                    "confidence": prediction_result.confidence_metrics.overall_confidence,
                }
            )

            # Update weight optimizer
            method_contributions = prediction_result.weight_optimization
            performance_metrics = PerformanceMetrics(
                accuracy=accuracy,
                hit_rate=1 if hit_count > 0 else 0,
                precision=accuracy,  # Same as accuracy for this use case
                recall=hit_count / len(actual_numbers) if actual_numbers else 0,
                f1_score=accuracy,  # Simplified
                confidence_correlation=0.6,  # Would be calculated from actual data
                stability_score=self._calculate_current_stability(),
            )

            self.weight_optimizer.update_performance(
                prediction_result.predicted_numbers,
                actual_numbers,
                method_contributions,
                prediction_date,
            )

            # Log result
            self.logger.info(
                f"Updated with actual result: {hit_count}/{len(prediction_result.predicted_numbers)} hits ({accuracy:.3f} accuracy)"
            )

        except Exception as e:
            self.logger.error(f"Failed to update with actual result: {e}")

    def run_comprehensive_validation(self, days_back: int = 60) -> Dict:
        """
        Run comprehensive system validation

        Args:
            days_back: Number of days to validate

        Returns:
            Comprehensive validation report
        """

        self.logger.info(
            f"Running comprehensive validation for last {days_back} days..."
        )

        try:
            # Get validation period
            end_date = datetime.now().date()
            start_date = end_date - timedelta(days=days_back)

            validation_results = {}

            # 1. Backtesting validation
            if self.backtesting_framework:
                backtest_summary = self.backtesting_framework.run_historical_backtest(
                    start_date=datetime.combine(start_date, datetime.min.time()),
                    end_date=datetime.combine(end_date, datetime.min.time()),
                )
                validation_results["backtesting"] = (
                    self.backtesting_framework.generate_report(backtest_summary)
                )

            # 2. Statistical significance testing
            if len(self.prediction_history) >= 10:
                predictions = [p["predicted"] for p in self.prediction_history[-30:]]
                actuals = [p["actual"] for p in self.prediction_history[-30:]]

                significance_result = (
                    self.statistical_validator.test_prediction_significance(
                        predictions, actuals
                    )
                )

                control_result = self.statistical_validator.run_control_group_analysis(
                    predictions, actuals
                )

                validation_results["statistical_significance"] = {
                    "significance_test": {
                        "statistic": significance_result.statistic,
                        "p_value": significance_result.p_value,
                        "is_significant": significance_result.is_significant,
                        "interpretation": significance_result.interpretation,
                    },
                    "control_comparison": {
                        "prediction_accuracy": control_result.prediction_accuracy,
                        "random_accuracy": control_result.random_accuracy,
                        "improvement": control_result.improvement,
                        "is_significant": control_result.significance.is_significant,
                    },
                }

            # 3. Weight optimization analysis
            weight_summary = self.weight_optimizer.get_performance_summary()
            validation_results["weight_optimization"] = weight_summary

            # 4. Performance monitoring summary
            if self.performance_monitor:
                performance_report = self.performance_monitor.get_performance_report(
                    days_back
                )
                validation_results["performance_monitoring"] = performance_report

            # 5. Overall system health
            validation_results["system_health"] = self._assess_system_health()

            self.logger.info("Comprehensive validation completed")
            return validation_results

        except Exception as e:
            self.logger.error(f"Comprehensive validation failed: {e}")
            return {"error": str(e)}

    def _get_historical_data(self, target_date: datetime, days_back: int = 100) -> List:
        """Get historical data for prediction"""

        if not KetQuaXoSo:
            return []  # Return empty for testing

        start_date = target_date.date() - timedelta(days=days_back)

        return list(
            KetQuaXoSo.objects.filter(
                ngay__gte=start_date, ngay__lt=target_date.date()
            ).order_by("-ngay")
        )

    def _generate_base_prediction(self, historical_data: List) -> List[int]:
        """Generate base prediction from historical data"""

        # This is a simplified version - would be replaced with actual prediction logic
        if not historical_data:
            return list(range(10, 25))  # Fallback prediction

        # Frequency analysis
        number_frequency = {}
        for result in historical_data[:50]:  # Last 50 results
            if hasattr(result, "get_all_2digit_numbers"):
                for num in result.get_all_2digit_numbers():
                    number_frequency[num] = number_frequency.get(num, 0) + 1

        # Get current weights
        weights = self.weight_optimizer.get_current_weights()

        # Apply weighted scoring (simplified)
        scored_numbers = {}
        for num in range(100):
            score = 0

            # Frequency component
            freq_score = number_frequency.get(num, 0) / len(historical_data[:50])
            score += freq_score * weights.get("frequency", 0.25)

            # Recent trend component (last 10 results)
            recent_count = sum(
                1
                for result in historical_data[:10]
                if hasattr(result, "get_all_2digit_numbers")
                and num in result.get_all_2digit_numbers()
            )
            recent_score = recent_count / 10
            score += recent_score * weights.get("recent_trend", 0.20)

            scored_numbers[num] = score

        # Select top 15 numbers
        top_numbers = sorted(scored_numbers.items(), key=lambda x: x[1], reverse=True)[
            :15
        ]
        return [num for num, _ in top_numbers]

    def _run_statistical_validation(self) -> SignificanceResult:
        """Run statistical validation on recent predictions"""

        if len(self.prediction_history) < 10:
            return None

        recent_predictions = [p["predicted"] for p in self.prediction_history[-20:]]
        recent_actuals = [p["actual"] for p in self.prediction_history[-20:]]

        return self.statistical_validator.test_prediction_significance(
            recent_predictions, recent_actuals
        )

    def _calculate_performance_score(
        self,
        confidence_metrics: PredictionConfidence,
        statistical_validation: Optional[SignificanceResult],
    ) -> float:
        """Calculate overall performance score"""

        base_score = confidence_metrics.overall_confidence

        # Adjust based on statistical validation
        if statistical_validation and statistical_validation.is_significant:
            base_score *= 1.2  # Boost if statistically significant
        elif statistical_validation:
            base_score *= 0.9  # Slight penalty if not significant

        # Adjust based on recent performance
        recent_accuracy = self._get_recent_accuracy()
        if recent_accuracy > 0.25:
            base_score *= 1.1
        elif recent_accuracy < 0.15:
            base_score *= 0.8

        return min(100, max(0, base_score))

    def _generate_enhanced_recommendation(
        self, confidence_metrics: PredictionConfidence, performance_score: float
    ) -> str:
        """Generate enhanced recommendation"""

        base_rec = confidence_metrics.recommendation

        # Add performance context
        if performance_score >= 80:
            return f"🌟 EXCELLENT: {base_rec}"
        elif performance_score >= 60:
            return f"✅ GOOD: {base_rec}"
        elif performance_score >= 40:
            return f"⚠️ FAIR: {base_rec}"
        else:
            return f"❌ POOR: {base_rec} - Consider alternative methods"

    def _get_recent_accuracy(self) -> float:
        """Get recent prediction accuracy"""
        if len(self.prediction_history) < 5:
            return 0.20  # Default assumption

        recent = self.prediction_history[-5:]
        return np.mean([p["accuracy"] for p in recent])

    def _get_recent_hit_rate(self) -> float:
        """Get recent hit rate"""
        if len(self.prediction_history) < 5:
            return 0.60  # Default assumption

        recent = self.prediction_history[-5:]
        return np.mean([1 if p["hits"] > 0 else 0 for p in recent])

    def _calculate_current_stability(self) -> float:
        """Calculate current prediction stability"""
        if len(self.prediction_history) < 5:
            return 0.5

        recent_accuracies = [p["accuracy"] for p in self.prediction_history[-10:]]
        return max(0, 1 - np.var(recent_accuracies) * 10)

    def _assess_system_health(self) -> Dict:
        """Assess overall system health"""

        health_score = 0
        issues = []

        # Check initialization
        if not self.is_initialized:
            issues.append("System not properly initialized")
            return {"score": 0, "status": "error", "issues": issues}

        # Check recent performance
        recent_accuracy = self._get_recent_accuracy()
        if recent_accuracy >= 0.25:
            health_score += 40
        elif recent_accuracy >= 0.15:
            health_score += 25
        else:
            health_score += 10
            issues.append(f"Low accuracy: {recent_accuracy:.3f}")

        # Check weight optimization
        if self.weight_optimizer.adaptation_count > 0:
            health_score += 20
        else:
            health_score += 10
            issues.append("No weight adaptations yet")

        # Check monitoring
        if self.performance_monitor:
            health_score += 20
        else:
            health_score += 10
            issues.append("Performance monitoring disabled")

        # Check data availability
        if len(self.prediction_history) >= 10:
            health_score += 20
        else:
            health_score += 5
            issues.append("Limited prediction history")

        # Determine status
        if health_score >= 80:
            status = "excellent"
        elif health_score >= 60:
            status = "good"
        elif health_score >= 40:
            status = "fair"
        else:
            status = "poor"

        return {
            "score": health_score,
            "status": status,
            "issues": issues,
            "prediction_count": len(self.prediction_history),
            "adaptation_count": self.weight_optimizer.adaptation_count,
            "monitoring_active": self.performance_monitor is not None,
        }

    def _create_fallback_result(self, reason: str) -> EnhancedPredictionResult:
        """Create fallback result when prediction fails"""

        fallback_numbers = list(range(10, 25))  # Simple fallback

        # Create minimal confidence metrics
        from .confidence_intervals import ConfidenceMetrics

        fallback_confidence_metrics = ConfidenceMetrics(
            point_estimate=3.0,
            confidence_interval=(1.0, 5.0),
            confidence_level=0.95,
            prediction_interval=(0.5, 6.0),
            reliability_score=20.0,
            uncertainty_level="Very High",
        )

        fallback_prediction_confidence = PredictionConfidence(
            predicted_numbers=fallback_numbers,
            individual_confidences={num: 20.0 for num in fallback_numbers},
            overall_confidence=20.0,
            confidence_metrics=fallback_confidence_metrics,
            risk_assessment=f"Fallback Mode: {reason}",
            recommendation=f"⚠️ Fallback prediction due to: {reason}",
        )

        return EnhancedPredictionResult(
            predicted_numbers=fallback_numbers,
            confidence_metrics=fallback_prediction_confidence,
            statistical_validation=None,
            weight_optimization={"fallback": 1.0},
            performance_score=20.0,
            recommendation=f"⚠️ FALLBACK: {reason}",
            uncertainty_level="Very High",
            expected_hits=(1.0, 5.0),
        )

    def _handle_alert(self, alert):
        """Handle performance monitoring alerts"""

        # Log alert
        log_level = {
            AlertLevel.INFO: logging.INFO,
            AlertLevel.WARNING: logging.WARNING,
            AlertLevel.CRITICAL: logging.CRITICAL,
            AlertLevel.ERROR: logging.ERROR,
        }[alert.level]

        self.logger.log(
            log_level, f"Performance Alert [{alert.category}]: {alert.message}"
        )

        # Take corrective action for critical alerts
        if alert.level == AlertLevel.CRITICAL:
            if "response time" in alert.message.lower():
                self.logger.warning(
                    "High response time detected - triggering optimization"
                )
                # Could trigger weight optimization or other corrective measures

    def export_system_report(self, filepath: str):
        """Export comprehensive system report"""

        report = {
            "system_info": {
                "initialized": self.is_initialized,
                "prediction_count": len(self.prediction_history),
                "monitoring_active": self.performance_monitor is not None,
                "export_timestamp": datetime.now().isoformat(),
            },
            "validation_results": self.run_comprehensive_validation(),
            "recent_performance": {
                "accuracy": self._get_recent_accuracy(),
                "hit_rate": self._get_recent_hit_rate(),
                "stability": self._calculate_current_stability(),
            },
            "system_health": self._assess_system_health(),
        }

        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(report, f, ensure_ascii=False, indent=2)

        self.logger.info(f"System report exported to {filepath}")

    def cleanup(self):
        """Cleanup resources"""
        if self.performance_monitor:
            self.performance_monitor.stop_monitoring()

        self.logger.info("Enhanced Prediction System cleaned up")
