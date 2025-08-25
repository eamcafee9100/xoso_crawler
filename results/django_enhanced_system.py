"""
Enhanced Django Integration for Prediction System
Integrates with actual Django models and provides production-ready configuration
"""

import logging
import os
import sys
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple

import django

# Setup Django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "xoso_crawler.settings")
try:
    django.setup()
    from results.models import (
        KetQuaXoSo,
        ModelTrainingHistory,
        PredictionPerformanceMetrics,
    )

    DJANGO_AVAILABLE = True
except Exception as e:
    logging.warning(f"Django setup failed: {e}")
    KetQuaXoSo = None
    PredictionPerformanceMetrics = None
    ModelTrainingHistory = None
    DJANGO_AVAILABLE = False


@dataclass
class ProductionConfig:
    """Production configuration for the enhanced system"""

    # Performance thresholds
    accuracy_threshold: float = 0.18  # 18% accuracy threshold for XSMB
    hit_rate_threshold: float = 0.45  # 45% hit rate threshold
    confidence_threshold: float = 60.0  # 60% confidence threshold

    # System performance
    response_time_threshold: float = 3.0  # 3 seconds max response time
    memory_threshold: float = 800.0  # 800MB memory limit

    # Data requirements
    min_historical_days: int = 90  # Minimum 90 days historical data
    training_data_size: int = 200  # Minimum 200 records for training

    # Monitoring
    snapshot_interval: int = 300  # 5 minutes snapshot interval
    alert_cooldown: int = 600  # 10 minutes alert cooldown

    # Validation
    backtesting_days: int = 45  # 45 days backtesting period
    validation_frequency: int = 3  # Validate every 3 days


class DjangoEnhancedPredictionSystem:
    """
    Enhanced prediction system integrated with Django models
    """

    def __init__(self, config: ProductionConfig = None):
        self.config = config or ProductionConfig()
        self.logger = logging.getLogger(__name__)

        # Check Django availability
        if not DJANGO_AVAILABLE:
            raise RuntimeError(
                "Django models not available. Please check Django setup."
            )

        # Initialize components
        from ml_validation.adaptive_weights import AdaptiveWeightOptimizer
        from ml_validation.backtesting import BacktestingFramework
        from ml_validation.confidence_intervals import ConfidenceCalculator
        from ml_validation.performance_monitor import (
            MonitoringConfig,
            PerformanceMonitor,
        )
        from ml_validation.statistical_tests import StatisticalValidator

        self.backtesting_framework = BacktestingFramework(KetQuaXoSo, self)
        self.statistical_validator = StatisticalValidator()
        self.confidence_calculator = ConfidenceCalculator()
        self.weight_optimizer = AdaptiveWeightOptimizer()

        # Configure performance monitoring for production
        monitoring_config = MonitoringConfig(
            accuracy_threshold=self.config.accuracy_threshold,
            hit_rate_threshold=self.config.hit_rate_threshold,
            response_time_threshold=self.config.response_time_threshold,
            memory_threshold=self.config.memory_threshold,
            alert_cooldown=self.config.alert_cooldown,
            snapshot_interval=self.config.snapshot_interval,
        )

        self.performance_monitor = PerformanceMonitor(monitoring_config)

        # System state
        self.is_initialized = False
        self.prediction_history = []
        self.current_model_training = None

    def initialize_with_real_data(self):
        """Initialize system with real historical data from Django models"""

        self.logger.info("Initializing Enhanced System with real Django data...")

        try:
            # Check data availability
            total_records = KetQuaXoSo.objects.count()
            if total_records < self.config.training_data_size:
                raise ValueError(
                    f"Insufficient data: {total_records} < {self.config.training_data_size}"
                )

            # Get recent data for validation
            end_date = datetime.now().date()
            start_date = end_date - timedelta(days=self.config.min_historical_days)

            recent_data = KetQuaXoSo.objects.filter(
                ngay__gte=start_date, ngay__lte=end_date
            ).order_by("-ngay")

            recent_count = recent_data.count()
            self.logger.info(f"Found {recent_count} recent records for analysis")

            if recent_count < 30:
                self.logger.warning(f"Limited recent data: {recent_count} days")

            # Initialize weight optimizer with historical performance
            self._initialize_weights_with_real_data(recent_data)

            # Create or get model training record
            self.current_model_training = self._create_model_training_record()

            # Start performance monitoring
            self.performance_monitor.start_monitoring()

            # Run initial validation
            if recent_count >= 30:
                self._run_initial_validation(recent_data)

            self.is_initialized = True
            self.logger.info("✅ System initialized successfully with real data")

        except Exception as e:
            self.logger.error(f"Initialization failed: {e}")
            raise

    def _initialize_weights_with_real_data(self, historical_data):
        """Initialize weights based on real historical performance"""

        self.logger.info("Analyzing historical data for weight initialization...")

        # Test different methods on historical data
        method_performance = {}

        # Sample last 50 records for testing
        sample_data = list(historical_data[:50])

        for method_name in [
            "frequency",
            "recent_trend",
            "cycle_analysis",
            "gap_analysis",
        ]:
            accuracies = []

            # Test method on sample data
            for i in range(10, min(30, len(sample_data))):  # Test on 20 records
                try:
                    # Use data up to index i for prediction
                    train_data = sample_data[i:]
                    target_result = sample_data[i - 1]

                    # Generate prediction using method
                    predicted_numbers = self._test_method_on_data(
                        method_name, train_data
                    )
                    actual_numbers = list(target_result.get_all_2digit_numbers())

                    # Calculate accuracy
                    hits = len(set(predicted_numbers) & set(actual_numbers))
                    accuracy = hits / len(predicted_numbers) if predicted_numbers else 0
                    accuracies.append(accuracy)

                except Exception as e:
                    self.logger.warning(f"Method {method_name} test failed: {e}")
                    continue

            # Calculate average performance
            if accuracies:
                avg_performance = sum(accuracies) / len(accuracies)
                method_performance[method_name] = avg_performance
                self.logger.info(
                    f"Method {method_name}: {avg_performance:.3f} avg accuracy"
                )
            else:
                method_performance[method_name] = 0.20  # Default

        # Add ML method with conservative weight
        method_performance["ml_prediction"] = 0.15  # Conservative for new ML

        # Ensure minimum performance for all methods
        min_performance = 0.10  # Minimum base performance
        for method in method_performance:
            if method_performance[method] < min_performance:
                method_performance[method] = min_performance

        # Normalize weights and ensure they're within valid range
        total_performance = sum(method_performance.values())
        if total_performance > 0:
            raw_weights = {
                method: perf / total_performance
                for method, perf in method_performance.items()
            }
        else:
            # Fallback equal weights
            raw_weights = {method: 0.2 for method in method_performance.keys()}

        # Ensure weights are within valid range (0.01 to 0.8) and adjust
        adjusted_weights = {}
        for method, weight in raw_weights.items():
            # Ensure weight is at least 0.05 and at most 0.6 for better balance
            adjusted_weight = max(0.05, min(0.6, weight))
            adjusted_weights[method] = adjusted_weight

        # Re-normalize after adjustment to ensure sum = 1.0
        total_adjusted = sum(adjusted_weights.values())
        if total_adjusted > 0:
            final_weights = {
                method: weight / total_adjusted
                for method, weight in adjusted_weights.items()
            }
        else:
            # Final fallback with safe weights
            final_weights = {
                "frequency": 0.30,
                "recent_trend": 0.25,
                "cycle_analysis": 0.20,
                "gap_analysis": 0.15,
                "ml_prediction": 0.10,
            }

        # Set weights
        self.weight_optimizer.set_weights(final_weights)
        self.logger.info(f"Initialized weights: {final_weights}")

    def _test_method_on_data(
        self, method_name: str, historical_data: List
    ) -> List[int]:
        """Test a specific method on historical data"""

        if len(historical_data) < 5:
            return list(range(10, 25))  # Fallback

        if method_name == "frequency":
            # Frequency-based prediction
            number_freq = {}
            for result in historical_data[:30]:
                for num in result.get_all_2digit_numbers():
                    number_freq[int(num)] = number_freq.get(int(num), 0) + 1

            # Get top 15 frequent numbers
            top_numbers = sorted(number_freq.items(), key=lambda x: x[1], reverse=True)[
                :15
            ]
            return [num for num, _ in top_numbers]

        elif method_name == "recent_trend":
            # Recent trend analysis (last 10 days)
            recent_numbers = {}
            for result in historical_data[:10]:
                for num in result.get_all_2digit_numbers():
                    recent_numbers[int(num)] = recent_numbers.get(int(num), 0) + 2

            top_numbers = sorted(
                recent_numbers.items(), key=lambda x: x[1], reverse=True
            )[:15]
            return [num for num, _ in top_numbers]

        elif method_name == "cycle_analysis":
            # Simple cycle analysis
            cycle_numbers = set()
            # Check 7-day cycles
            for i in range(0, min(21, len(historical_data)), 7):
                week_data = historical_data[i : i + 7]
                for result in week_data:
                    cycle_numbers.update(
                        [int(num) for num in result.get_all_2digit_numbers()]
                    )

            return list(cycle_numbers)[:15]

        elif method_name == "gap_analysis":
            # Gap analysis - numbers not seen recently
            recent_numbers = set()
            for result in historical_data[:5]:  # Last 5 days
                recent_numbers.update(
                    [int(num) for num in result.get_all_2digit_numbers()]
                )

            # Find numbers not in recent set
            all_numbers = set(range(100))
            gap_numbers = all_numbers - recent_numbers
            return list(gap_numbers)[:15]

        else:
            return list(range(10, 25))  # Default fallback

    def _create_model_training_record(self):
        """Create or get model training record"""

        model_id = f"enhanced_system_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

        training_record = ModelTrainingHistory.objects.create(
            model_id=model_id,
            model_type="enhanced_cycle",
            version="2.0",
            data_size=KetQuaXoSo.objects.count(),
            feature_count=5,  # 5 main methods
            training_params={
                "methods": [
                    "frequency",
                    "recent_trend",
                    "cycle_analysis",
                    "gap_analysis",
                    "ml_prediction",
                ],
                "weights": self.weight_optimizer.get_current_weights(),
                "config": {
                    "accuracy_threshold": self.config.accuracy_threshold,
                    "min_historical_days": self.config.min_historical_days,
                },
            },
            status="completed",
            is_active=True,
        )

        self.logger.info(f"Created model training record: {model_id}")
        return training_record

    def _run_initial_validation(self, historical_data):
        """Run initial validation on historical data"""

        self.logger.info("Running initial validation...")

        try:
            # Run backtesting on recent data
            start_date = datetime.now() - timedelta(days=self.config.backtesting_days)
            end_date = datetime.now() - timedelta(days=1)

            backtest_summary = self.backtesting_framework.run_historical_backtest(
                start_date=start_date, end_date=end_date, prediction_methods=["hybrid"]
            )

            # Update model training record with validation results
            if self.current_model_training:
                self.current_model_training.validation_accuracy = (
                    backtest_summary.avg_accuracy / 100
                )
                self.current_model_training.cross_val_score = backtest_summary.hit_rate
                self.current_model_training.save()

            self.logger.info(
                f"Initial validation: {backtest_summary.avg_accuracy:.1f}% accuracy"
            )

        except Exception as e:
            self.logger.warning(f"Initial validation failed: {e}")

    def make_production_prediction(self, target_date: datetime) -> Dict:
        """Make production-ready prediction with full validation"""

        if not self.is_initialized:
            raise RuntimeError(
                "System not initialized. Call initialize_with_real_data() first."
            )

        start_time = datetime.now()

        try:
            # Get historical data
            historical_data = self._get_real_historical_data(target_date)

            if len(historical_data) < 30:
                raise ValueError(
                    f"Insufficient historical data: {len(historical_data)} days"
                )

            # Generate prediction
            predicted_numbers = self._generate_production_prediction(historical_data)

            # Calculate confidence
            confidence_result = (
                self.confidence_calculator.calculate_prediction_confidence(
                    predicted_numbers=predicted_numbers,
                    historical_data=historical_data,
                    method_name="enhanced_production",
                    confidence_level=0.95,
                )
            )

            # Create performance record
            performance_record = self._create_performance_record(
                target_date.date(), predicted_numbers, confidence_result
            )

            # Update monitoring
            response_time = (datetime.now() - start_time).total_seconds()
            self._update_monitoring_metrics(confidence_result, response_time)

            # Format response
            result = {
                "success": True,
                "prediction_date": target_date.date().isoformat(),
                "predicted_numbers": predicted_numbers,
                "confidence": {
                    "overall": confidence_result.overall_confidence,
                    "expected_hits": {
                        "lower": confidence_result.confidence_metrics.confidence_interval[
                            0
                        ],
                        "upper": confidence_result.confidence_metrics.confidence_interval[
                            1
                        ],
                    },
                    "uncertainty_level": confidence_result.confidence_metrics.uncertainty_level,
                    "reliability_score": confidence_result.confidence_metrics.reliability_score,
                },
                "system_info": {
                    "weights": self.weight_optimizer.get_current_weights(),
                    "response_time": response_time,
                    "data_quality": len(historical_data),
                    "model_version": (
                        self.current_model_training.version
                        if self.current_model_training
                        else "2.0"
                    ),
                },
                "recommendation": confidence_result.recommendation,
                "performance_record_id": (
                    performance_record.id if performance_record else None
                ),
            }

            return result

        except Exception as e:
            self.logger.error(f"Production prediction failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "fallback_prediction": list(range(10, 25)),
            }

    def _get_real_historical_data(self, target_date: datetime) -> List:
        """Get real historical data from Django models"""

        start_date = target_date.date() - timedelta(
            days=self.config.min_historical_days
        )

        return list(
            KetQuaXoSo.objects.filter(
                ngay__gte=start_date, ngay__lt=target_date.date()
            ).order_by("-ngay")
        )

    def _generate_production_prediction(self, historical_data: List) -> List[int]:
        """Generate production prediction using optimized weights"""

        weights = self.weight_optimizer.get_current_weights()
        scored_numbers = {}

        # Initialize all numbers with zero score
        for num in range(100):
            scored_numbers[num] = 0.0

        # Apply each method with its weight
        for method, weight in weights.items():
            method_numbers = self._test_method_on_data(method, historical_data)

            # Score numbers from this method
            for i, num in enumerate(method_numbers[:20]):  # Top 20 from each method
                # Higher score for higher rank
                score = (20 - i) / 20 * weight
                scored_numbers[num] += score

        # Select top 15 numbers
        top_numbers = sorted(scored_numbers.items(), key=lambda x: x[1], reverse=True)[
            :15
        ]
        return [num for num, _ in top_numbers]

    def _create_performance_record(
        self, prediction_date, predicted_numbers, confidence_result
    ):
        """Create performance record in database"""

        if not self.current_model_training:
            return None

        try:
            performance_record = PredictionPerformanceMetrics.objects.create(
                model_training=self.current_model_training,
                prediction_date=prediction_date,
                analysis_date=datetime.now().date(),
                prediction_count=len(predicted_numbers),
                predicted_numbers=predicted_numbers,
                avg_confidence=confidence_result.overall_confidence,
                confidence_distribution={
                    "high": len(
                        [
                            c
                            for c in confidence_result.individual_confidences.values()
                            if c > 70
                        ]
                    ),
                    "medium": len(
                        [
                            c
                            for c in confidence_result.individual_confidences.values()
                            if 40 <= c <= 70
                        ]
                    ),
                    "low": len(
                        [
                            c
                            for c in confidence_result.individual_confidences.values()
                            if c < 40
                        ]
                    ),
                },
            )

            return performance_record

        except Exception as e:
            self.logger.error(f"Failed to create performance record: {e}")
            return None

    def _update_monitoring_metrics(self, confidence_result, response_time):
        """Update performance monitoring metrics"""

        metrics = {
            "accuracy": self._get_recent_accuracy(),
            "hit_rate": self._get_recent_hit_rate(),
            "confidence": confidence_result.overall_confidence / 100,
            "response_time": response_time,
            "prediction_count": len(self.prediction_history) + 1,
            "active_methods": list(self.weight_optimizer.get_current_weights().keys()),
        }

        self.performance_monitor.update_metrics(metrics)

    def update_with_real_result(
        self, prediction_date: datetime, performance_record_id: int = None
    ):
        """Update prediction with actual lottery result"""

        try:
            # Get actual result
            actual_result = KetQuaXoSo.objects.filter(
                ngay=prediction_date.date()
            ).first()

            if not actual_result:
                self.logger.warning(
                    f"No actual result found for {prediction_date.date()}"
                )
                return False

            actual_numbers = [
                int(num) for num in actual_result.get_all_2digit_numbers()
            ]

            # Update performance record
            if performance_record_id:
                try:
                    performance_record = PredictionPerformanceMetrics.objects.get(
                        id=performance_record_id
                    )

                    # Calculate metrics
                    predicted_numbers = performance_record.predicted_numbers
                    hits = list(set(predicted_numbers) & set(actual_numbers))

                    performance_record.actual_numbers = actual_numbers
                    performance_record.hit_numbers = hits
                    performance_record.miss_numbers = list(
                        set(predicted_numbers) - set(actual_numbers)
                    )
                    performance_record.total_hits = len(hits)
                    performance_record.total_misses = len(predicted_numbers) - len(hits)
                    performance_record.accuracy = (
                        len(hits) / len(predicted_numbers) if predicted_numbers else 0
                    )
                    performance_record.hit_rate = 1.0 if len(hits) > 0 else 0.0

                    # Calculate precision, recall, F1
                    if len(predicted_numbers) > 0:
                        performance_record.precision = len(hits) / len(
                            predicted_numbers
                        )

                    if len(actual_numbers) > 0:
                        performance_record.recall = len(hits) / len(actual_numbers)

                    if performance_record.precision + performance_record.recall > 0:
                        performance_record.f1_score = (
                            2
                            * (performance_record.precision * performance_record.recall)
                            / (performance_record.precision + performance_record.recall)
                        )

                    performance_record.save()

                    # Update model training stats
                    if self.current_model_training:
                        self.current_model_training.update_performance(len(hits) > 0)

                    # Update weight optimizer
                    method_contributions = self.weight_optimizer.get_current_weights()
                    self.weight_optimizer.update_performance(
                        predicted_numbers,
                        actual_numbers,
                        method_contributions,
                        prediction_date,
                    )

                    self.logger.info(
                        f"Updated result: {len(hits)}/{len(predicted_numbers)} hits ({performance_record.accuracy:.3f} accuracy)"
                    )
                    return True

                except PredictionPerformanceMetrics.DoesNotExist:
                    self.logger.error(
                        f"Performance record {performance_record_id} not found"
                    )
                    return False

        except Exception as e:
            self.logger.error(f"Failed to update with real result: {e}")
            return False

    def _get_recent_accuracy(self) -> float:
        """Get recent accuracy from database"""

        if not self.current_model_training:
            return 0.20

        recent_records = PredictionPerformanceMetrics.objects.filter(
            model_training=self.current_model_training,
            accuracy__gt=0,  # Only records with actual results
        ).order_by("-prediction_date")[:10]

        if not recent_records:
            return 0.20

        accuracies = [record.accuracy for record in recent_records]
        return sum(accuracies) / len(accuracies)

    def _get_recent_hit_rate(self) -> float:
        """Get recent hit rate from database"""

        if not self.current_model_training:
            return 0.60

        recent_records = PredictionPerformanceMetrics.objects.filter(
            model_training=self.current_model_training,
            total_hits__gte=0,  # Records with results
        ).order_by("-prediction_date")[:10]

        if not recent_records:
            return 0.60

        hit_rates = [record.hit_rate for record in recent_records]
        return sum(hit_rates) / len(hit_rates)

    def get_production_dashboard_data(self) -> Dict:
        """Get dashboard data for production monitoring"""

        if not self.current_model_training:
            return {"error": "No active model training"}

        # Get recent performance data
        recent_records = PredictionPerformanceMetrics.objects.filter(
            model_training=self.current_model_training
        ).order_by("-prediction_date")[:30]

        # Calculate stats
        total_predictions = recent_records.count()
        if total_predictions == 0:
            return {"message": "No prediction data available"}

        accuracies = [r.accuracy for r in recent_records if r.accuracy > 0]
        hit_rates = [r.hit_rate for r in recent_records if r.hit_rate >= 0]

        dashboard_data = {
            "model_info": {
                "model_id": self.current_model_training.model_id,
                "version": self.current_model_training.version,
                "training_date": self.current_model_training.training_date.isoformat(),
                "total_predictions": self.current_model_training.total_predictions,
                "success_rate": self.current_model_training.success_rate,
            },
            "recent_performance": {
                "total_predictions": total_predictions,
                "avg_accuracy": sum(accuracies) / len(accuracies) if accuracies else 0,
                "avg_hit_rate": sum(hit_rates) / len(hit_rates) if hit_rates else 0,
                "accuracy_trend": (
                    accuracies[-5:] if len(accuracies) >= 5 else accuracies
                ),
            },
            "current_weights": self.weight_optimizer.get_current_weights(),
            "system_health": self._assess_system_health(),
            "monitoring_data": (
                self.performance_monitor.get_dashboard_data()
                if self.performance_monitor
                else {}
            ),
        }

        return dashboard_data

    def _assess_system_health(self) -> Dict:
        """Assess system health for production"""

        health_score = 0
        issues = []

        # Check model training
        if self.current_model_training and self.current_model_training.is_active:
            health_score += 25
        else:
            issues.append("No active model training")

        # Check recent performance
        recent_accuracy = self._get_recent_accuracy()
        if recent_accuracy >= self.config.accuracy_threshold:
            health_score += 25
        elif recent_accuracy >= self.config.accuracy_threshold * 0.8:
            health_score += 15
            issues.append(f"Accuracy below target: {recent_accuracy:.3f}")
        else:
            health_score += 5
            issues.append(f"Low accuracy: {recent_accuracy:.3f}")

        # Check data availability
        total_records = KetQuaXoSo.objects.count()
        if total_records >= self.config.training_data_size:
            health_score += 25
        else:
            health_score += 10
            issues.append(f"Limited data: {total_records} records")

        # Check monitoring
        if self.performance_monitor and self.performance_monitor.is_monitoring:
            health_score += 25
        else:
            health_score += 10
            issues.append("Performance monitoring inactive")

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
            "total_records": total_records,
            "recent_accuracy": recent_accuracy,
            "monitoring_active": (
                self.performance_monitor.is_monitoring
                if self.performance_monitor
                else False
            ),
        }

    def cleanup(self):
        """Cleanup resources for production"""
        if self.performance_monitor:
            self.performance_monitor.stop_monitoring()

        self.logger.info("Enhanced Django system cleaned up")
