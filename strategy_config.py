"""
Trading Strategy Configuration
Centralized configuration for strategy parameters
"""

from dataclasses import dataclass
from typing import Dict


@dataclass
class StrategyConfig:
    """Configuration parameters for trading strategy"""

    # Market Analysis
    min_gain_percent: float = 5.0
    min_volume_usdt: float = 1000000.0
    top_gainers_limit: int = 20

    # Risk Management
    position_size_percent: float = 2.0
    max_concurrent_positions: int = 3
    daily_loss_limit_percent: float = 5.0

    # Stop Loss / Take Profit
    stop_loss_percent: float = 3.0
    take_profit_percent: float = 8.0
    trailing_stop_percent: float = 2.0

    # Trade Execution
    min_trade_amount_usdt: float = 10.0
    max_trade_amount_usdt: float = 1000.0

    def to_dict(self) -> Dict:
        """Convert config to dictionary"""
        return {
            'market_analysis': {
                'min_gain_percent': self.min_gain_percent,
                'min_volume_usdt': self.min_volume_usdt,
                'top_gainers_limit': self.top_gainers_limit
            },
            'risk_management': {
                'position_size_percent': self.position_size_percent,
                'max_concurrent_positions': self.max_concurrent_positions,
                'daily_loss_limit_percent': self.daily_loss_limit_percent
            },
            'stop_loss_take_profit': {
                'stop_loss_percent': self.stop_loss_percent,
                'take_profit_percent': self.take_profit_percent,
                'trailing_stop_percent': self.trailing_stop_percent
            },
            'trade_execution': {
                'min_trade_amount_usdt': self.min_trade_amount_usdt,
                'max_trade_amount_usdt': self.max_trade_amount_usdt
            }
        }
