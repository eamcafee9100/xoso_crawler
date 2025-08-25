"""
Real-time Performance Monitoring System
Provides comprehensive monitoring, alerts, and dashboard for prediction system
"""

import json
import logging
import threading
import time
from collections import defaultdict, deque
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Callable, Dict, List, Optional, Tuple

import numpy as np
import pandas as pd


class AlertLevel(Enum):
    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"
    ERROR = "error"


@dataclass
class Alert:
    """System alert"""

    level: AlertLevel
    message: str
    timestamp: datetime
    category: str
    data: Dict = field(default_factory=dict)
    resolved: bool = False


@dataclass
class PerformanceSnapshot:
    """Performance snapshot at a point in time"""

    timestamp: datetime
    accuracy: float
    hit_rate: float
    confidence_score: float
    prediction_count: int
    response_time: float
    memory_usage: float
    active_methods: List[str]


@dataclass
class MonitoringConfig:
    """Configuration for performance monitoring"""

    accuracy_threshold: float = 0.15  # Alert if accuracy drops below 15%
    hit_rate_threshold: float = 0.30  # Alert if hit rate drops below 30%
    response_time_threshold: float = 5.0  # Alert if response time > 5 seconds
    memory_threshold: float = 500.0  # Alert if memory usage > 500MB
    alert_cooldown: int = 300  # 5 minutes between similar alerts
    snapshot_interval: int = 60  # Take snapshot every 60 seconds
    history_retention: int = 30  # Keep history for 30 days


class PerformanceMonitor:
    """
    Comprehensive real-time performance monitoring system
    """

    def __init__(self, config: MonitoringConfig = None):
        self.config = config or MonitoringConfig()
        self.logger = logging.getLogger(__name__)

        # Performance data storage
        self.snapshots = deque(maxlen=10000)  # Keep last 10k snapshots
        self.alerts = deque(maxlen=1000)  # Keep last 1k alerts
        self.alert_history = defaultdict(datetime)  # Track alert cooldowns

        # Real-time metrics
        self.current_metrics = {}
        self.is_monitoring = False
        self.monitor_thread = None

        # Performance thresholds and trends
        self.performance_trends = {}
        self.baseline_metrics = {}

        # Alert subscribers
        self.alert_callbacks = []

        # Dashboard data
        self.dashboard_data = {}

    def start_monitoring(self):
        """Start real-time monitoring"""
        if self.is_monitoring:
            return

        self.is_monitoring = True
        self.monitor_thread = threading.Thread(
            target=self._monitoring_loop, daemon=True
        )
        self.monitor_thread.start()

        self.logger.info("Performance monitoring started")

    def stop_monitoring(self):
        """Stop real-time monitoring"""
        self.is_monitoring = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=5)

        self.logger.info("Performance monitoring stopped")

    def _monitoring_loop(self):
        """Main monitoring loop"""
        while self.is_monitoring:
            try:
                # Take performance snapshot
                snapshot = self._take_snapshot()
                self.snapshots.append(snapshot)

                # Check for alerts
                self._check_alerts(snapshot)

                # Update trends
                self._update_trends()

                # Update dashboard data
                self._update_dashboard()

                # Sleep until next interval
                time.sleep(self.config.snapshot_interval)

            except Exception as e:
                self.logger.error(f"Error in monitoring loop: {e}")
                time.sleep(10)  # Wait longer on error

    def _take_snapshot(self) -> PerformanceSnapshot:
        """Take a performance snapshot"""
        import psutil

        # Get current metrics
        timestamp = datetime.now()

        # Performance metrics (would be updated by prediction system)
        accuracy = self.current_metrics.get("accuracy", 0.0)
        hit_rate = self.current_metrics.get("hit_rate", 0.0)
        confidence_score = self.current_metrics.get("confidence", 0.0)
        prediction_count = self.current_metrics.get("prediction_count", 0)
        response_time = self.current_metrics.get("response_time", 0.0)

        # System metrics
        process = psutil.Process()
        memory_usage = process.memory_info().rss / 1024 / 1024  # MB

        # Active methods
        active_methods = self.current_metrics.get("active_methods", [])

        return PerformanceSnapshot(
            timestamp=timestamp,
            accuracy=accuracy,
            hit_rate=hit_rate,
            confidence_score=confidence_score,
            prediction_count=prediction_count,
            response_time=response_time,
            memory_usage=memory_usage,
            active_methods=active_methods,
        )

    def _check_alerts(self, snapshot: PerformanceSnapshot):
        """Check for alert conditions"""

        # Accuracy alert
        if snapshot.accuracy < self.config.accuracy_threshold:
            self._create_alert(
                AlertLevel.WARNING,
                f"Low accuracy detected: {snapshot.accuracy:.3f} (threshold: {self.config.accuracy_threshold:.3f})",
                "performance",
                {
                    "accuracy": snapshot.accuracy,
                    "threshold": self.config.accuracy_threshold,
                },
            )

        # Hit rate alert
        if snapshot.hit_rate < self.config.hit_rate_threshold:
            self._create_alert(
                AlertLevel.WARNING,
                f"Low hit rate detected: {snapshot.hit_rate:.3f} (threshold: {self.config.hit_rate_threshold:.3f})",
                "performance",
                {
                    "hit_rate": snapshot.hit_rate,
                    "threshold": self.config.hit_rate_threshold,
                },
            )

        # Response time alert
        if snapshot.response_time > self.config.response_time_threshold:
            self._create_alert(
                AlertLevel.CRITICAL,
                f"High response time: {snapshot.response_time:.2f}s (threshold: {self.config.response_time_threshold:.2f}s)",
                "system",
                {
                    "response_time": snapshot.response_time,
                    "threshold": self.config.response_time_threshold,
                },
            )

        # Memory usage alert
        if snapshot.memory_usage > self.config.memory_threshold:
            self._create_alert(
                AlertLevel.WARNING,
                f"High memory usage: {snapshot.memory_usage:.1f}MB (threshold: {self.config.memory_threshold:.1f}MB)",
                "system",
                {
                    "memory_usage": snapshot.memory_usage,
                    "threshold": self.config.memory_threshold,
                },
            )

        # Trend-based alerts
        self._check_trend_alerts(snapshot)

    def _check_trend_alerts(self, snapshot: PerformanceSnapshot):
        """Check for trend-based alerts"""

        if len(self.snapshots) < 10:
            return

        recent_snapshots = list(self.snapshots)[-10:]

        # Check accuracy trend
        accuracies = [s.accuracy for s in recent_snapshots]
        if len(accuracies) >= 5:
            trend_slope = np.polyfit(range(len(accuracies)), accuracies, 1)[0]

            if trend_slope < -0.05:  # Declining accuracy
                self._create_alert(
                    AlertLevel.WARNING,
                    f"Declining accuracy trend detected: {trend_slope:.4f} per snapshot",
                    "trend",
                    {"trend_slope": trend_slope, "recent_accuracies": accuracies},
                )

        # Check response time trend
        response_times = [s.response_time for s in recent_snapshots]
        if len(response_times) >= 5:
            trend_slope = np.polyfit(range(len(response_times)), response_times, 1)[0]

            if trend_slope > 0.5:  # Increasing response times
                self._create_alert(
                    AlertLevel.WARNING,
                    f"Increasing response time trend: {trend_slope:.3f}s per snapshot",
                    "trend",
                    {"trend_slope": trend_slope, "recent_times": response_times},
                )

    def _create_alert(
        self, level: AlertLevel, message: str, category: str, data: Dict = None
    ):
        """Create and process an alert"""

        # Check cooldown
        alert_key = f"{level.value}_{category}_{hash(message) % 1000}"
        now = datetime.now()

        if alert_key in self.alert_history:
            last_alert = self.alert_history[alert_key]
            if (now - last_alert).seconds < self.config.alert_cooldown:
                return  # Skip alert due to cooldown

        # Create alert
        alert = Alert(
            level=level,
            message=message,
            timestamp=now,
            category=category,
            data=data or {},
        )

        self.alerts.append(alert)
        self.alert_history[alert_key] = now

        # Notify subscribers
        for callback in self.alert_callbacks:
            try:
                callback(alert)
            except Exception as e:
                self.logger.error(f"Error in alert callback: {e}")

        # Log alert
        log_level = {
            AlertLevel.INFO: logging.INFO,
            AlertLevel.WARNING: logging.WARNING,
            AlertLevel.CRITICAL: logging.CRITICAL,
            AlertLevel.ERROR: logging.ERROR,
        }[level]

        self.logger.log(log_level, f"[{category.upper()}] {message}")

    def _update_trends(self):
        """Update performance trends"""

        if len(self.snapshots) < 5:
            return

        recent_snapshots = list(self.snapshots)[-50:]  # Last 50 snapshots

        # Calculate trends
        trends = {}

        for metric in [
            "accuracy",
            "hit_rate",
            "confidence_score",
            "response_time",
            "memory_usage",
        ]:
            values = [getattr(s, metric) for s in recent_snapshots]

            if len(values) >= 5:
                # Linear trend
                x = np.arange(len(values))
                slope, intercept = np.polyfit(x, values, 1)

                # Moving average
                window = min(10, len(values))
                moving_avg = np.convolve(values, np.ones(window) / window, mode="valid")

                trends[metric] = {
                    "slope": slope,
                    "current_value": values[-1],
                    "moving_average": (
                        moving_avg[-1] if len(moving_avg) > 0 else values[-1]
                    ),
                    "variance": np.var(values),
                    "trend_direction": (
                        "up"
                        if slope > 0.001
                        else "down" if slope < -0.001 else "stable"
                    ),
                }

        self.performance_trends = trends

    def _update_dashboard(self):
        """Update dashboard data"""

        if not self.snapshots:
            return

        recent_snapshots = list(self.snapshots)[-100:]  # Last 100 snapshots

        # Current status
        latest = recent_snapshots[-1]

        # Historical data for charts
        timestamps = [s.timestamp.isoformat() for s in recent_snapshots]
        accuracies = [s.accuracy for s in recent_snapshots]
        hit_rates = [s.hit_rate for s in recent_snapshots]
        response_times = [s.response_time for s in recent_snapshots]

        # Statistics
        stats = {
            "accuracy": {
                "current": latest.accuracy,
                "average": np.mean(accuracies),
                "min": np.min(accuracies),
                "max": np.max(accuracies),
                "std": np.std(accuracies),
            },
            "hit_rate": {
                "current": latest.hit_rate,
                "average": np.mean(hit_rates),
                "min": np.min(hit_rates),
                "max": np.max(hit_rates),
                "std": np.std(hit_rates),
            },
            "response_time": {
                "current": latest.response_time,
                "average": np.mean(response_times),
                "min": np.min(response_times),
                "max": np.max(response_times),
                "std": np.std(response_times),
            },
        }

        # Recent alerts
        recent_alerts = [
            {
                "level": alert.level.value,
                "message": alert.message,
                "timestamp": alert.timestamp.isoformat(),
                "category": alert.category,
                "resolved": alert.resolved,
            }
            for alert in list(self.alerts)[-10:]  # Last 10 alerts
        ]

        self.dashboard_data = {
            "current_status": {
                "accuracy": latest.accuracy,
                "hit_rate": latest.hit_rate,
                "confidence": latest.confidence_score,
                "response_time": latest.response_time,
                "memory_usage": latest.memory_usage,
                "prediction_count": latest.prediction_count,
                "active_methods": latest.active_methods,
                "timestamp": latest.timestamp.isoformat(),
            },
            "historical_data": {
                "timestamps": timestamps,
                "accuracies": accuracies,
                "hit_rates": hit_rates,
                "response_times": response_times,
            },
            "statistics": stats,
            "trends": self.performance_trends,
            "recent_alerts": recent_alerts,
            "system_health": self._calculate_system_health(),
        }

    def _calculate_system_health(self) -> Dict:
        """Calculate overall system health score"""

        if not self.snapshots:
            return {"score": 0, "status": "unknown", "issues": []}

        latest = list(self.snapshots)[-1]
        issues = []

        # Performance score (0-100)
        performance_score = 0

        # Accuracy component (40% weight)
        if latest.accuracy >= 0.25:
            accuracy_score = 100
        elif latest.accuracy >= 0.15:
            accuracy_score = 50 + (latest.accuracy - 0.15) / 0.1 * 50
        else:
            accuracy_score = latest.accuracy / 0.15 * 50
            issues.append(f"Low accuracy: {latest.accuracy:.3f}")

        performance_score += accuracy_score * 0.4

        # Hit rate component (30% weight)
        if latest.hit_rate >= 0.5:
            hit_rate_score = 100
        elif latest.hit_rate >= 0.3:
            hit_rate_score = 50 + (latest.hit_rate - 0.3) / 0.2 * 50
        else:
            hit_rate_score = latest.hit_rate / 0.3 * 50
            issues.append(f"Low hit rate: {latest.hit_rate:.3f}")

        performance_score += hit_rate_score * 0.3

        # Response time component (20% weight)
        if latest.response_time <= 2.0:
            response_score = 100
        elif latest.response_time <= 5.0:
            response_score = 100 - (latest.response_time - 2.0) / 3.0 * 50
        else:
            response_score = max(0, 50 - (latest.response_time - 5.0) * 10)
            issues.append(f"Slow response time: {latest.response_time:.2f}s")

        performance_score += response_score * 0.2

        # Memory usage component (10% weight)
        if latest.memory_usage <= 200:
            memory_score = 100
        elif latest.memory_usage <= 500:
            memory_score = 100 - (latest.memory_usage - 200) / 300 * 50
        else:
            memory_score = max(0, 50 - (latest.memory_usage - 500) / 100 * 10)
            issues.append(f"High memory usage: {latest.memory_usage:.1f}MB")

        performance_score += memory_score * 0.1

        # Determine status
        if performance_score >= 80:
            status = "excellent"
        elif performance_score >= 60:
            status = "good"
        elif performance_score >= 40:
            status = "fair"
        elif performance_score >= 20:
            status = "poor"
        else:
            status = "critical"

        return {
            "score": round(performance_score, 1),
            "status": status,
            "issues": issues,
            "components": {
                "accuracy": round(accuracy_score, 1),
                "hit_rate": round(hit_rate_score, 1),
                "response_time": round(response_score, 1),
                "memory_usage": round(memory_score, 1),
            },
        }

    def update_metrics(self, metrics: Dict):
        """Update current metrics (called by prediction system)"""
        self.current_metrics.update(metrics)

    def subscribe_to_alerts(self, callback: Callable[[Alert], None]):
        """Subscribe to alerts"""
        self.alert_callbacks.append(callback)

    def get_dashboard_data(self) -> Dict:
        """Get current dashboard data"""
        return self.dashboard_data.copy()

    def get_recent_alerts(self, hours: int = 24) -> List[Alert]:
        """Get recent alerts within specified hours"""
        cutoff = datetime.now() - timedelta(hours=hours)
        return [alert for alert in self.alerts if alert.timestamp >= cutoff]

    def get_performance_report(self, days: int = 7) -> Dict:
        """Generate comprehensive performance report"""

        cutoff = datetime.now() - timedelta(days=days)
        recent_snapshots = [s for s in self.snapshots if s.timestamp >= cutoff]

        if not recent_snapshots:
            return {"message": "No data available for the specified period"}

        # Calculate statistics
        accuracies = [s.accuracy for s in recent_snapshots]
        hit_rates = [s.hit_rate for s in recent_snapshots]
        response_times = [s.response_time for s in recent_snapshots]

        report = {
            "period": f"Last {days} days",
            "total_snapshots": len(recent_snapshots),
            "metrics": {
                "accuracy": {
                    "mean": np.mean(accuracies),
                    "median": np.median(accuracies),
                    "std": np.std(accuracies),
                    "min": np.min(accuracies),
                    "max": np.max(accuracies),
                    "percentiles": {
                        "25th": np.percentile(accuracies, 25),
                        "75th": np.percentile(accuracies, 75),
                        "95th": np.percentile(accuracies, 95),
                    },
                },
                "hit_rate": {
                    "mean": np.mean(hit_rates),
                    "median": np.median(hit_rates),
                    "std": np.std(hit_rates),
                },
                "response_time": {
                    "mean": np.mean(response_times),
                    "median": np.median(response_times),
                    "std": np.std(response_times),
                    "p95": np.percentile(response_times, 95),
                    "p99": np.percentile(response_times, 99),
                },
            },
            "trends": self.performance_trends,
            "alerts_summary": self._get_alerts_summary(days),
            "recommendations": self._generate_performance_recommendations(
                recent_snapshots
            ),
        }

        return report

    def _get_alerts_summary(self, days: int) -> Dict:
        """Get alerts summary for specified period"""
        cutoff = datetime.now() - timedelta(days=days)
        recent_alerts = [alert for alert in self.alerts if alert.timestamp >= cutoff]

        summary = {
            "total_alerts": len(recent_alerts),
            "by_level": {},
            "by_category": {},
            "resolved_count": sum(1 for alert in recent_alerts if alert.resolved),
        }

        for alert in recent_alerts:
            # Count by level
            level = alert.level.value
            summary["by_level"][level] = summary["by_level"].get(level, 0) + 1

            # Count by category
            category = alert.category
            summary["by_category"][category] = (
                summary["by_category"].get(category, 0) + 1
            )

        return summary

    def _generate_performance_recommendations(
        self, snapshots: List[PerformanceSnapshot]
    ) -> List[str]:
        """Generate performance improvement recommendations"""
        recommendations = []

        if not snapshots:
            return recommendations

        # Analyze performance patterns
        accuracies = [s.accuracy for s in snapshots]
        response_times = [s.response_time for s in snapshots]

        avg_accuracy = np.mean(accuracies)
        avg_response_time = np.mean(response_times)

        # Accuracy recommendations
        if avg_accuracy < 0.15:
            recommendations.append(
                "🎯 Consider implementing ensemble methods to improve accuracy"
            )
            recommendations.append(
                "📊 Increase training data size or improve data quality"
            )
        elif avg_accuracy < 0.20:
            recommendations.append(
                "⚡ Fine-tune prediction algorithms for better performance"
            )

        # Response time recommendations
        if avg_response_time > 3.0:
            recommendations.append(
                "🚀 Optimize prediction algorithms for faster response times"
            )
            recommendations.append("💾 Consider implementing prediction caching")

        # Memory recommendations
        memory_usages = [s.memory_usage for s in snapshots]
        if np.mean(memory_usages) > 400:
            recommendations.append(
                "🧹 Implement memory optimization and garbage collection"
            )

        # Stability recommendations
        if np.std(accuracies) > 0.05:
            recommendations.append(
                "📈 Improve prediction consistency - high variance detected"
            )

        return recommendations

    def export_monitoring_data(self, filepath: str, days: int = 30):
        """Export monitoring data for analysis"""

        cutoff = datetime.now() - timedelta(days=days)

        # Filter data by date
        filtered_snapshots = [s for s in self.snapshots if s.timestamp >= cutoff]
        filtered_alerts = [a for a in self.alerts if a.timestamp >= cutoff]

        export_data = {
            "export_timestamp": datetime.now().isoformat(),
            "period_days": days,
            "snapshots": [
                {
                    "timestamp": s.timestamp.isoformat(),
                    "accuracy": s.accuracy,
                    "hit_rate": s.hit_rate,
                    "confidence_score": s.confidence_score,
                    "prediction_count": s.prediction_count,
                    "response_time": s.response_time,
                    "memory_usage": s.memory_usage,
                    "active_methods": s.active_methods,
                }
                for s in filtered_snapshots
            ],
            "alerts": [
                {
                    "level": a.level.value,
                    "message": a.message,
                    "timestamp": a.timestamp.isoformat(),
                    "category": a.category,
                    "data": a.data,
                    "resolved": a.resolved,
                }
                for a in filtered_alerts
            ],
            "performance_report": self.get_performance_report(days),
        }

        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(export_data, f, ensure_ascii=False, indent=2)

        self.logger.info(f"Monitoring data exported to {filepath}")
