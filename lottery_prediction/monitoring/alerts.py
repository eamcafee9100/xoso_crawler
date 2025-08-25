# lottery_prediction/monitoring/alerts.py
import requests
import logging
from django.conf import settings
from datetime import datetime
from enum import Enum

class AlertLevel(Enum):
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"

class AlertManager:
    def __init__(self):
        self.slack_webhook = settings.SLACK_WEBHOOK_URL
        self.email_enabled = settings.EMAIL_ALERTS_ENABLED
        self.logger = logging.getLogger(__name__)

    def send_alert(self, title, message, level=AlertLevel.INFO, metadata=None):
        """Send alert through multiple channels"""
        alert_data = {
            'title': title,
            'message': message,
            'level': level.value,
            'timestamp': datetime.now().isoformat(),
            'metadata': metadata or {}
        }

        # Send to Slack
        if self.slack_webhook:
            self._send_slack_alert(alert_data)

        # Send email for critical alerts
        if self.email_enabled and level in [AlertLevel.ERROR, AlertLevel.CRITICAL]:
            self._send_email_alert(alert_data)

        # Log the alert
        log_level = {
            AlertLevel.INFO: logging.INFO,
            AlertLevel.WARNING: logging.WARNING,
            AlertLevel.ERROR: logging.ERROR,
            AlertLevel.CRITICAL: logging.CRITICAL
        }
        self.logger.log(log_level[level], f"{title}: {message}")

    def _send_slack_alert(self, alert_data):
        """Send alert to Slack"""
        color_map = {
            'info': '#36a64f',      # Green
            'warning': '#ffaa00',   # Orange  
            'error': '#ff0000',     # Red
            'critical': '#800080'   # Purple
        }

        slack_payload = {
            "attachments": [{
                "color": color_map.get(alert_data['level'], '#36a64f'),
                "title": f"🚨 {alert_data['title']}",
                "text": alert_data['message'],
                "fields": [
                    {
                        "title": "Level",
                        "value": alert_data['level'].upper(),
                        "short": True
                    },
                    {
                        "title": "Time",
                        "value": alert_data['timestamp'],
                        "short": True
                    }
                ],
                "footer": "Lottery Prediction System",
                "ts": int(datetime.now().timestamp())
            }]
        }

        # Add metadata fields
        if alert_data['metadata']:
            for key, value in alert_data['metadata'].items():
                slack_payload["attachments"][0]["fields"].append({
                    "title": key.replace('_', ' ').title(),
                    "value": str(value),
                    "short": True
                })

        try:
            response = requests.post(self.slack_webhook, json=slack_payload, timeout=10)
            response.raise_for_status()
        except Exception as e:
            self.logger.error(f"Failed to send Slack alert: {e}")

    def _send_email_alert(self, alert_data):
        """Send email alert"""
        from django.core.mail import send_mail
        
        subject = f"[{alert_data['level'].upper()}] {alert_data['title']}"
        message = f"""
        Alert: {alert_data['title']}
        Level: {alert_data['level'].upper()}
        Time: {alert_data['timestamp']}
        
        Message:
        {alert_data['message']}
        
        Metadata:
        {alert_data['metadata']}
        """
        
        try:
            send_mail(
                subject=subject,
                message=message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=settings.ALERT_EMAIL_RECIPIENTS,
                fail_silently=False
            )
        except Exception as e:
            self.logger.error(f"Failed to send email alert: {e}")

# Alert conditions and monitoring
class AlertMonitor:
    def __init__(self):
        self.alert_manager = AlertManager()

    def check_model_performance(self):
        """Monitor model performance and alert if degraded"""
        from lottery_prediction.models import MethodCyclicalPerformance
        from datetime import datetime, timedelta
        
        # Check recent performance
        recent_performance = MethodCyclicalPerformance.objects.filter(
            year=datetime.now().year,
            month=datetime.now().month
        ).first()
        
        if recent_performance and recent_performance.hit_rate < 0.3:  # Below 30%
            self.alert_manager.send_alert(
                title="Model Performance Degradation",
                message=f"Model hit rate dropped to {recent_performance.hit_rate:.1%}",
                level=AlertLevel.ERROR,
                metadata={
                    'hit_rate': recent_performance.hit_rate,
                    'method': recent_performance.method_name,
                    'month': f"{recent_performance.month}/{recent_performance.year}"
                }
            )

    def check_system_resources(self):
        """Monitor system resources"""
        import psutil
        
        # Memory usage
        memory = psutil.virtual_memory()
        if memory.percent > 85:
            self.alert_manager.send_alert(
                title="High Memory Usage",
                message=f"System memory usage at {memory.percent:.1f}%",
                level=AlertLevel.WARNING,
                metadata={'memory_percent': memory.percent}
            )

        # Disk usage
        disk = psutil.disk_usage('/')
        disk_percent = (disk.used / disk.total) * 100
        if disk_percent > 90:
            self.alert_manager.send_alert(
                title="High Disk Usage",
                message=f"Disk usage at {disk_percent:.1f}%",
                level=AlertLevel.ERROR,
                metadata={'disk_percent': disk_percent}
            )

    def check_prediction_failures(self):
        """Monitor prediction API failures"""
        from lottery_prediction.models import PredictionResult
        from datetime import datetime, timedelta
        
        # Check for failed predictions in last hour
        failed_predictions = PredictionResult.objects.filter(
            created_at__gte=datetime.now() - timedelta(hours=1),
            status='failed'
        ).count()
        
        if failed_predictions > 5:
            self.alert_manager.send_alert(
                title="High Prediction Failure Rate",
                message=f"{failed_predictions} prediction failures in the last hour",
                level=AlertLevel.ERROR,
                metadata={'failed_count': failed_predictions}
            )