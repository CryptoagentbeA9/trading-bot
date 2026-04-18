"""
Trading Strategy Engine
Core engine for analyzing market data, generating signals, and managing positions
"""

import logging
from typing import Dict, List, Optional, Tuple
from datetime import datetime
from dataclasses import dataclass, field
from binance_client import BinanceClient
from strategy_config import StrategyConfig

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class Position:
    """Represents an open trading position"""
    symbol: str
    entry_price: float
    amount: float
    entry_time: datetime
    stop_loss: float
    take_profit: float
    highest_price: float = 0.0

    def __post_init__(self):
        if self.highest_price == 0.0:
            self.highest_price = self.entry_price


@dataclass
class TradeSignal:
    """Trading signal with action and reasoning"""
    symbol: str
    action: str  # 'BUY', 'SELL', 'HOLD'
    confidence: float
    reason: str
    price: float
    volume: float


@dataclass
class PerformanceMetrics:
    """Track strategy performance"""
    total_trades: int = 0
    winning_trades: int = 0
    losing_trades: int = 0
    total_pnl: float = 0.0
    daily_pnl: float = 0.0
    win_rate: float = 0.0
    trades_today: int = 0


class StrategyEngine:
    """Main trading strategy engine"""

    def __init__(self, client: BinanceClient, config: StrategyConfig):
        self.client = client
        self.config = config
        self.positions: Dict[str, Position] = {}
        self.metrics = PerformanceMetrics()
        self.daily_start_balance = 0.0
        logger.info("Strategy engine initialized")

    def analyze_market_data(self, gainers: List[Dict]) -> List[TradeSignal]:
        """
        Analyze market data and generate trading signals

        Args:
            gainers: List of top gaining cryptocurrencies

        Returns:
            List of trade signals
        """
        signals = []

        for i, gainer in enumerate(gainers):
            symbol = gainer['symbol']
            price = gainer['price']
            change_24h = gainer['change_24h']
            volume = gainer['volume']

            if change_24h < self.config.min_gain_percent:
                continue

            if volume < self.config.min_volume_usdt:
                continue

            confidence = self._calculate_confidence(i, change_24h, volume)

            signal = TradeSignal(
                symbol=symbol,
                action='BUY',
                confidence=confidence,
                reason=f"Rank #{i+1}, +{change_24h:.2f}%, Vol: ${volume:,.0f}",
                price=price,
                volume=volume
            )
            signals.append(signal)

        signals.sort(key=lambda x: x.confidence, reverse=True)
        return signals

    def _calculate_confidence(self, rank: int, change_percent: float, volume: float) -> float:
        """Calculate signal confidence score (0-1)"""
        rank_score = max(0, 1 - (rank / 20))
        change_score = min(1, change_percent / 20)
        volume_score = min(1, volume / 5000000)

        confidence = (rank_score * 0.4) + (change_score * 0.4) + (volume_score * 0.2)
        return round(confidence, 3)

    def check_position_exits(self) -> List[Tuple[str, str]]:
        """
        Check open positions for stop-loss or take-profit triggers

        Returns:
            List of (symbol, reason) tuples for positions to exit
        """
        exits = []

        for symbol, position in list(self.positions.items()):
            current_price = self.client.get_current_price(symbol)
            if not current_price:
                continue

            position.highest_price = max(position.highest_price, current_price)

            trailing_stop = position.highest_price * (1 - self.config.trailing_stop_percent / 100)

            if current_price <= position.stop_loss:
                exits.append((symbol, f"Stop-loss hit: ${current_price:.4f}"))
            elif current_price >= position.take_profit:
                exits.append((symbol, f"Take-profit hit: ${current_price:.4f}"))
            elif current_price <= trailing_stop:
                exits.append((symbol, f"Trailing stop: ${current_price:.4f}"))

        return exits

    def calculate_position_size(self, symbol: str, price: float) -> Optional[float]:
        """
        Calculate position size based on risk management rules

        Args:
            symbol: Trading pair
            price: Current price

        Returns:
            Amount to trade in base currency, or None if cannot trade
        """
        balance = self.client.get_account_balance()
        usdt_balance = balance.get('USDT', 0)

        if usdt_balance < self.config.min_trade_amount_usdt:
            logger.warning(f"Insufficient balance: ${usdt_balance:.2f}")
            return None

        if len(self.positions) >= self.config.max_concurrent_positions:
            logger.warning(f"Max positions reached: {len(self.positions)}")
            return None

        if self._check_daily_loss_limit():
            logger.warning("Daily loss limit reached")
            return None

        position_value = usdt_balance * (self.config.position_size_percent / 100)
        position_value = min(position_value, self.config.max_trade_amount_usdt)
        position_value = max(position_value, self.config.min_trade_amount_usdt)

        amount = position_value / price
        return amount

    def _check_daily_loss_limit(self) -> bool:
        """Check if daily loss limit has been reached"""
        if self.daily_start_balance == 0:
            return False

        loss_percent = abs(self.metrics.daily_pnl / self.daily_start_balance) * 100
        return self.metrics.daily_pnl < 0 and loss_percent >= self.config.daily_loss_limit_percent

    def execute_buy(self, signal: TradeSignal) -> bool:
        """
        Execute buy order and open position

        Args:
            signal: Trade signal to execute

        Returns:
            True if successful, False otherwise
        """
        amount = self.calculate_position_size(signal.symbol, signal.price)
        if not amount:
            return False

        order = self.client.execute_market_buy(signal.symbol, amount)
        if not order:
            return False

        entry_price = order.get('average') or signal.price
        stop_loss = entry_price * (1 - self.config.stop_loss_percent / 100)
        take_profit = entry_price * (1 + self.config.take_profit_percent / 100)

        position = Position(
            symbol=signal.symbol,
            entry_price=entry_price,
            amount=amount,
            entry_time=datetime.now(),
            stop_loss=stop_loss,
            take_profit=take_profit
        )

        self.positions[signal.symbol] = position
        logger.info(f"Position opened: {signal.symbol} @ ${entry_price:.4f}, SL: ${stop_loss:.4f}, TP: ${take_profit:.4f}")
        return True

    def execute_sell(self, symbol: str, reason: str) -> bool:
        """
        Execute sell order and close position

        Args:
            symbol: Trading pair to sell
            reason: Reason for selling

        Returns:
            True if successful, False otherwise
        """
        if symbol not in self.positions:
            logger.warning(f"No position found for {symbol}")
            return False

        position = self.positions[symbol]
        order = self.client.execute_market_sell(symbol, position.amount)

        if not order:
            return False

        exit_price = order.get('average') or self.client.get_current_price(symbol)
        pnl_data = self.client.calculate_pnl(
            symbol, position.entry_price, exit_price, position.amount
        )

        self._update_metrics(pnl_data)
        del self.positions[symbol]

        logger.info(f"Position closed: {symbol} @ ${exit_price:.4f}, PnL: ${pnl_data['pnl']:.2f} ({pnl_data['pnl_percentage']:.2f}%) - {reason}")
        return True

    def _update_metrics(self, pnl_data: Dict):
        """Update performance metrics after trade"""
        self.metrics.total_trades += 1
        self.metrics.trades_today += 1
        self.metrics.total_pnl += pnl_data['pnl']
        self.metrics.daily_pnl += pnl_data['pnl']

        if pnl_data['pnl'] > 0:
            self.metrics.winning_trades += 1
        else:
            self.metrics.losing_trades += 1

        if self.metrics.total_trades > 0:
            self.metrics.win_rate = (self.metrics.winning_trades / self.metrics.total_trades) * 100

    def get_performance_summary(self) -> Dict:
        """Get current performance metrics"""
        return {
            'total_trades': self.metrics.total_trades,
            'winning_trades': self.metrics.winning_trades,
            'losing_trades': self.metrics.losing_trades,
            'win_rate': f"{self.metrics.win_rate:.2f}%",
            'total_pnl': f"${self.metrics.total_pnl:.2f}",
            'daily_pnl': f"${self.metrics.daily_pnl:.2f}",
            'open_positions': len(self.positions),
            'trades_today': self.metrics.trades_today
        }

    def get_open_positions(self) -> List[Dict]:
        """Get details of all open positions"""
        positions_data = []

        for symbol, position in self.positions.items():
            current_price = self.client.get_current_price(symbol)
            if current_price:
                unrealized_pnl = (current_price - position.entry_price) * position.amount
                unrealized_pnl_pct = ((current_price - position.entry_price) / position.entry_price) * 100
            else:
                unrealized_pnl = 0
                unrealized_pnl_pct = 0

            positions_data.append({
                'symbol': symbol,
                'entry_price': f"${position.entry_price:.4f}",
                'current_price': f"${current_price:.4f}" if current_price else "N/A",
                'amount': position.amount,
                'unrealized_pnl': f"${unrealized_pnl:.2f}",
                'unrealized_pnl_pct': f"{unrealized_pnl_pct:.2f}%",
                'stop_loss': f"${position.stop_loss:.4f}",
                'take_profit': f"${position.take_profit:.4f}",
                'entry_time': position.entry_time.strftime('%Y-%m-%d %H:%M:%S')
            })

        return positions_data

    def reset_daily_metrics(self):
        """Reset daily metrics (call at start of each trading day)"""
        balance = self.client.get_account_balance()
        self.daily_start_balance = balance.get('USDT', 0)
        self.metrics.daily_pnl = 0.0
        self.metrics.trades_today = 0
        logger.info(f"Daily metrics reset. Starting balance: ${self.daily_start_balance:.2f}")

    def run_strategy_cycle(self) -> Dict:
        """
        Execute one complete strategy cycle

        Returns:
            Summary of actions taken
        """
        summary = {
            'signals_generated': 0,
            'positions_opened': 0,
            'positions_closed': 0,
            'actions': []
        }

        exits = self.check_position_exits()
        for symbol, reason in exits:
            if self.execute_sell(symbol, reason):
                summary['positions_closed'] += 1
                summary['actions'].append(f"SELL {symbol}: {reason}")

        gainers = self.client.get_top_gainers(self.config.top_gainers_limit)
        if not gainers:
            logger.warning("No gainers data available")
            return summary

        signals = self.analyze_market_data(gainers)
        summary['signals_generated'] = len(signals)

        for signal in signals[:3]:
            if len(self.positions) >= self.config.max_concurrent_positions:
                break

            if signal.symbol in self.positions:
                continue

            if self.execute_buy(signal):
                summary['positions_opened'] += 1
                summary['actions'].append(f"BUY {signal.symbol}: {signal.reason}")

        return summary
