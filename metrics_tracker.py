"""
Metrics Tracking System
Tracks trading performance, API health, and system metrics
"""

import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from dataclasses import dataclass, field, asdict
from collections import defaultdict, deque
import json
from pathlib import Path


@dataclass
class TradeMetrics:
    """Metrics for individual trades"""
    trade_id: str
    symbol: str
    side: str  # 'BUY' or 'SELL'
    amount: float
    price: float
    pnl: Optional[float] = None
    pnl_percentage: Optional[float] = None
    timestamp: str = field(default_factory=lambda: datetime.utcnow().isoformat())


@dataclass
class APIMetrics:
    """API performance metrics"""
    endpoint: str
    response_time: float
    success: bool
    timestamp: str = field(default_factory=lambda: datetime.utcnow().isoformat())


@dataclass
class SystemMetrics:
    """System-level metrics"""
    uptime_seconds: float
    active_positions: int
    total_trades: int
    win_rate: float
    total_pnl: float
    daily_pnl: float
    timestamp: str = field(default_factory=lambda: datetime.utcnow().isoformat())


class MetricsTracker:
    """Central metrics tracking and aggregation"""

    def __init__(self, metrics_dir: str = 'metrics'):
        self.metrics_dir = Path(metrics_dir)
        self.metrics_dir.mkdir(exist_ok=True)

        self.start_time = time.time()
        self.trades: List[TradeMetrics] = []
        self.api_calls: deque = deque(maxlen=1000)  # Keep last 1000 API calls

        # Aggregated metrics
        self.total_trades = 0
        self.winning_trades = 0
        self.losing_trades = 0
        self.total_pnl = 0.0
        self.daily_pnl = 0.0

        # API health tracking
        self.api_response_times: Dict[str, deque] = defaultdict(lambda: deque(maxlen=100))
        self.api_error_counts: Dict[str, int] = defaultdict(int)
        self.api_success_counts: Dict[str, int] = defaultdict(int)

        # Performance tracking
        self.daily_trades = 0
        self.weekly_trades = 0
        self.monthly_trades = 0

        self.last_reset = datetime.utcnow()

    def record_trade(self, symbol: str, side: str, amount: float,
                    price: float, pnl: Optional[float] = None,
                    pnl_percentage: Optional[float] = None):
        """Record a trade execution"""
        trade = TradeMetrics(
            trade_id=f"{symbol}_{int(time.time())}",
            symbol=symbol,
            side=side,
            amount=amount,
            price=price,
            pnl=pnl,
            pnl_percentage=pnl_percentage
        )

        self.trades.append(trade)
        self.total_trades += 1
        self.daily_trades += 1
        self.weekly_trades += 1
        self.monthly_trades += 1

        if pnl is not None:
            self.total_pnl += pnl
            self.daily_pnl += pnl

            if pnl > 0:
                self.winning_trades += 1
            else:
                self.losing_trades += 1

        self._save_trade(trade)

    def record_api_call(self, endpoint: str, response_time: float, success: bool):
        """Record API call metrics"""
        metric = APIMetrics(
            endpoint=endpoint,
            response_time=response_time,
            success=success
        )

        self.api_calls.append(metric)
        self.api_response_times[endpoint].append(response_time)

        if success:
            self.api_success_counts[endpoint] += 1
        else:
            self.api_error_counts[endpoint] += 1

    def get_win_rate(self) -> float:
        """Calculate win rate percentage"""
        if self.total_trades == 0:
            return 0.0
        return (self.winning_trades / self.total_trades) * 100

    def get_profit_factor(self) -> float:
        """Calculate profit factor (gross profit / gross loss)"""
        gross_profit = sum(t.pnl for t in self.trades if t.pnl and t.pnl > 0)
        gross_loss = abs(sum(t.pnl for t in self.trades if t.pnl and t.pnl < 0))

        if gross_loss == 0:
            return float('inf') if gross_profit > 0 else 0.0

        return gross_profit / gross_loss

    def get_api_health(self) -> Dict[str, Dict]:
        """Get API health metrics"""
        health = {}

        for endpoint, times in self.api_response_times.items():
            if times:
                avg_time = sum(times) / len(times)
                max_time = max(times)
                min_time = min(times)
            else:
                avg_time = max_time = min_time = 0

            total_calls = self.api_success_counts[endpoint] + self.api_error_counts[endpoint]
            success_rate = (self.api_success_counts[endpoint] / total_calls * 100) if total_calls > 0 else 0

            health[endpoint] = {
                'avg_response_time_ms': avg_time * 1000,
                'max_response_time_ms': max_time * 1000,
                'min_response_time_ms': min_time * 1000,
                'total_calls': total_calls,
                'success_rate': success_rate,
                'error_count': self.api_error_counts[endpoint]
            }

        return health

    def get_system_metrics(self, active_positions: int) -> SystemMetrics:
        """Get current system metrics"""
        return SystemMetrics(
            uptime_seconds=time.time() - self.start_time,
            active_positions=active_positions,
            total_trades=self.total_trades,
            win_rate=self.get_win_rate(),
            total_pnl=self.total_pnl,
            daily_pnl=self.daily_pnl
        )

    def get_daily_summary(self) -> Dict:
        """Get daily performance summary"""
        return {
            'date': datetime.utcnow().strftime('%Y-%m-%d'),
            'trades': self.daily_trades,
            'pnl': self.daily_pnl,
            'win_rate': self.get_win_rate(),
            'profit_factor': self.get_profit_factor()
        }

    def get_weekly_summary(self) -> Dict:
        """Get weekly performance summary"""
        week_ago = datetime.utcnow() - timedelta(days=7)
        recent_trades = [t for t in self.trades
                        if datetime.fromisoformat(t.timestamp) > week_ago]

        weekly_pnl = sum(t.pnl for t in recent_trades if t.pnl)

        return {
            'week_start': week_ago.strftime('%Y-%m-%d'),
            'trades': len(recent_trades),
            'pnl': weekly_pnl
        }

    def get_monthly_summary(self) -> Dict:
        """Get monthly performance summary"""
        month_ago = datetime.utcnow() - timedelta(days=30)
        recent_trades = [t for t in self.trades
                        if datetime.fromisoformat(t.timestamp) > month_ago]

        monthly_pnl = sum(t.pnl for t in recent_trades if t.pnl)

        return {
            'month_start': month_ago.strftime('%Y-%m-%d'),
            'trades': len(recent_trades),
            'pnl': monthly_pnl
        }

    def reset_daily_metrics(self):
        """Reset daily metrics (call at start of each day)"""
        self.daily_pnl = 0.0
        self.daily_trades = 0
        self.last_reset = datetime.utcnow()

    def _save_trade(self, trade: TradeMetrics):
        """Save trade to metrics file"""
        date_str = datetime.utcnow().strftime('%Y-%m-%d')
        metrics_file = self.metrics_dir / f'trades_{date_str}.json'

        with open(metrics_file, 'a') as f:
            f.write(json.dumps(asdict(trade)) + '\n')

    def export_metrics(self) -> Dict:
        """Export all metrics for dashboard"""
        return {
            'system': asdict(self.get_system_metrics(0)),
            'daily': self.get_daily_summary(),
            'weekly': self.get_weekly_summary(),
            'monthly': self.get_monthly_summary(),
            'api_health': self.get_api_health(),
            'recent_trades': [asdict(t) for t in self.trades[-20:]]
        }
