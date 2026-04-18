"""
Alerting System
Monitors critical events and sends notifications
"""

import logging
from typing import List, Dict, Optional, Callable
from datetime import datetime, timedelta
from dataclasses import dataclass
from enum import Enum


class AlertLevel(Enum):
    """Alert severity levels"""
    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"


@dataclass
class Alert:
    """Alert data structure"""
    level: AlertLevel
    title: str
    message: str
    timestamp: str
    metadata: Dict = None


class AlertingSystem:
    """Monitor conditions and trigger alerts"""

    def __init__(self, logger: logging.Logger):
        self.logger = logger
        self.alerts: List[Alert] = []
        self.alert_handlers: List[Callable] = []

        # Alert thresholds
        self.daily_loss_limit = 50.0  # USD
        self.consecutive_loss_limit = 3
        self.api_error_threshold = 10
        self.position_limit = 500.0  # USD

        # State tracking
        self.consecutive_losses = 0
        self.api_errors_count = 0
        self.last_api_error_reset = datetime.utcnow()

    def register_handler(self, handler: Callable):
        """Register alert handler (e.g., email, Telegram)"""
        self.alert_handlers.append(handler)

    def check_daily_loss(self, daily_pnl: float):
        """Check if daily loss limit exceeded"""
        if daily_pnl < -self.daily_loss_limit:
            self._trigger_alert(
                AlertLevel.CRITICAL,
                "Daily Loss Limit Exceeded",
                f"Daily P&L: ${daily_pnl:.2f} (Limit: -${self.daily_loss_limit})",
                {'daily_pnl': daily_pnl}
            )

    def check_consecutive_losses(self, trade_pnl: float):
        """Track consecutive losing trades"""
        if trade_pnl < 0:
            self.consecutive_losses += 1

            if self.consecutive_losses >= self.consecutive_loss_limit:
                self._trigger_alert(
                    AlertLevel.CRITICAL,
                    "Consecutive Loss Limit Reached",
                    f"{self.consecutive_losses} consecutive losing trades",
                    {'consecutive_losses': self.consecutive_losses}
                )
        else:
            self.consecutive_losses = 0

    def check_position_exposure(self, total_exposure: float):
        """Check if total position exposure exceeds limit"""
        if total_exposure > self.position_limit:
            self._trigger_alert(
                AlertLevel.CRITICAL,
                "Position Limit Exceeded",
                f"Total exposure: ${total_exposure:.2f} (Limit: ${self.position_limit})",
                {'total_exposure': total_exposure}
            )

    def check_api_health(self, endpoint: str, success: bool):
        """Monitor API health"""
        if not success:
            self.api_errors_count += 1

            if self.api_errors_count >= self.api_error_threshold:
                self._trigger_alert(
                    AlertLevel.WARNING,
                    "High API Error Rate",
                    f"{self.api_errors_count} API errors detected for {endpoint}",
                    {'endpoint': endpoint, 'error_count': self.api_errors_count}
                )

        # Reset counter every hour
        if datetime.utcnow() - self.last_api_error_reset > timedelta(hours=1):
            self.api_errors_count = 0
            self.last_api_error_reset = datetime.utcnow()

    def check_trade_execution_failure(self, symbol: str, reason: str):
        """Alert on trade execution failure"""
        self._trigger_alert(
            AlertLevel.WARNING,
            "Trade Execution Failed",
            f"Failed to execute trade for {symbol}: {reason}",
            {'symbol': symbol, 'reason': reason}
        )

    def check_performance_anomaly(self, win_rate: float, expected_min: float = 40.0):
        """Detect performance anomalies"""
        if win_rate < expected_min:
            self._trigger_alert(
                AlertLevel.WARNING,
                "Low Win Rate Detected",
                f"Current win rate: {win_rate:.2f}% (Expected: >{expected_min}%)",
                {'win_rate': win_rate, 'expected_min': expected_min}
            )

    def _trigger_alert(self, level: AlertLevel, title: str, message: str, metadata: Dict = None):
        """Trigger an alert and notify handlers"""
        alert = Alert(
            level=level,
            title=title,
            message=message,
            timestamp=datetime.utcnow().isoformat(),
            metadata=metadata or {}
        )

        self.alerts.append(alert)

        # Log alert
        log_method = {
            AlertLevel.INFO: self.logger.info,
            AlertLevel.WARNING: self.logger.warning,
            AlertLevel.CRITICAL: self.logger.critical
        }[level]

        log_method(f"[ALERT] {title}: {message}")

        # Notify handlers
        for handler in self.alert_handlers:
            try:
                handler(alert)
            except Exception as e:
                self.logger.error(f"Alert handler failed: {e}")

    def get_recent_alerts(self, limit: int = 50) -> List[Alert]:
        """Get recent alerts"""
        return self.alerts[-limit:]

    def get_critical_alerts(self) -> List[Alert]:
        """Get all critical alerts"""
        return [a for a in self.alerts if a.level == AlertLevel.CRITICAL]

    def clear_alerts(self):
        """Clear all alerts"""
        self.alerts.clear()


def console_alert_handler(alert: Alert):
    """Simple console alert handler"""
    print(f"\n{'='*60}")
    print(f"[{alert.level.value.upper()}] {alert.title}")
    print(f"Time: {alert.timestamp}")
    print(f"Message: {alert.message}")
    if alert.metadata:
        print(f"Details: {alert.metadata}")
    print(f"{'='*60}\n")
