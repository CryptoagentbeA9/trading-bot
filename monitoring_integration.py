"""
Monitoring Integration Module
Integrates logging, metrics, and alerting with existing trading components
"""

import time
from typing import Optional
from logger_config import setup_logging, log_trade, log_api_call, log_error
from metrics_tracker import MetricsTracker
from alerting import AlertingSystem, console_alert_handler
from binance_client import BinanceClient
from strategy_engine import StrategyEngine


class MonitoredBinanceClient(BinanceClient):
    """Binance client with integrated monitoring"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        loggers = setup_logging()
        self.api_logger = loggers['api']
        self.error_logger = loggers['errors']
        self.metrics_tracker = MetricsTracker()

    def _monitored_api_call(self, func, endpoint: str, *args, **kwargs):
        """Wrap API call with monitoring"""
        start_time = time.time()
        success = False

        try:
            result = func(*args, **kwargs)
            success = True
            return result
        except Exception as e:
            log_error(self.error_logger, 'API_ERROR', str(e), endpoint=endpoint)
            raise
        finally:
            response_time = time.time() - start_time
            log_api_call(self.api_logger, endpoint, 'GET', response_time,
                        status_code=200 if success else 500)
            self.metrics_tracker.record_api_call(endpoint, response_time, success)

    def get_account_balance(self):
        return self._monitored_api_call(
            super().get_account_balance,
            '/api/v3/account'
        )

    def get_top_gainers(self, limit: int = 10):
        return self._monitored_api_call(
            super().get_top_gainers,
            '/api/v3/ticker/24hr',
            limit
        )

    def execute_market_buy(self, symbol: str, amount: float):
        result = self._monitored_api_call(
            super().execute_market_buy,
            '/api/v3/order',
            symbol,
            amount
        )

        if result:
            price = result.get('average', result.get('price', 0))
            self.metrics_tracker.record_trade(symbol, 'BUY', amount, price)

        return result

    def execute_market_sell(self, symbol: str, amount: float):
        result = self._monitored_api_call(
            super().execute_market_sell,
            '/api/v3/order',
            symbol,
            amount
        )

        if result:
            price = result.get('average', result.get('price', 0))
            self.metrics_tracker.record_trade(symbol, 'SELL', amount, price)

        return result


class MonitoredStrategyEngine(StrategyEngine):
    """Strategy engine with integrated monitoring"""

    def __init__(self, client: MonitoredBinanceClient, config):
        super().__init__(client, config)

        loggers = setup_logging()
        self.trade_logger = loggers['trades']
        self.main_logger = loggers['main']

        self.alerting = AlertingSystem(self.main_logger)
        self.alerting.register_handler(console_alert_handler)

    def execute_buy(self, signal):
        """Execute buy with monitoring"""
        success = super().execute_buy(signal)

        if success:
            log_trade(
                self.trade_logger,
                'BUY',
                signal.symbol,
                self.positions[signal.symbol].amount,
                self.positions[signal.symbol].entry_price,
                confidence=signal.confidence,
                reason=signal.reason
            )
            self.main_logger.info(f"BUY executed: {signal.symbol} @ ${signal.price:.4f}")
        else:
            self.alerting.check_trade_execution_failure(signal.symbol, "Failed to execute buy order")

        return success

    def execute_sell(self, symbol: str, reason: str):
        """Execute sell with monitoring"""
        if symbol not in self.positions:
            return False

        position = self.positions[symbol]
        success = super().execute_sell(symbol, reason)

        if success:
            current_price = self.client.get_current_price(symbol)
            pnl_data = self.client.calculate_pnl(
                symbol, position.entry_price, current_price, position.amount
            )

            log_trade(
                self.trade_logger,
                'SELL',
                symbol,
                position.amount,
                current_price,
                pnl=pnl_data['pnl'],
                pnl_percentage=pnl_data['pnl_percentage'],
                reason=reason
            )

            # Update metrics and check alerts
            self.client.metrics_tracker.record_trade(
                symbol, 'SELL', position.amount, current_price,
                pnl=pnl_data['pnl'],
                pnl_percentage=pnl_data['pnl_percentage']
            )

            self.alerting.check_consecutive_losses(pnl_data['pnl'])
            self.alerting.check_daily_loss(self.metrics.daily_pnl)

            self.main_logger.info(
                f"SELL executed: {symbol} @ ${current_price:.4f}, "
                f"P&L: ${pnl_data['pnl']:.2f} ({pnl_data['pnl_percentage']:.2f}%)"
            )
        else:
            self.alerting.check_trade_execution_failure(symbol, "Failed to execute sell order")

        return success

    def run_strategy_cycle(self):
        """Run strategy cycle with monitoring"""
        self.main_logger.info("Starting strategy cycle")

        # Check position exposure
        total_exposure = sum(
            pos.entry_price * pos.amount
            for pos in self.positions.values()
        )
        self.alerting.check_position_exposure(total_exposure)

        # Check performance
        if self.metrics.total_trades > 10:
            self.alerting.check_performance_anomaly(self.metrics.win_rate)

        summary = super().run_strategy_cycle()

        self.main_logger.info(
            f"Strategy cycle complete: {summary['signals_generated']} signals, "
            f"{summary['positions_opened']} opened, {summary['positions_closed']} closed"
        )

        return summary


def create_monitored_bot(api_key: str = None, api_secret: str = None,
                        testnet: bool = True, config = None):
    """
    Factory function to create a fully monitored trading bot

    Returns:
        Tuple of (client, strategy_engine, metrics_tracker, alerting_system)
    """
    from strategy_config import StrategyConfig

    if config is None:
        config = StrategyConfig()

    # Create monitored client
    client = MonitoredBinanceClient(api_key, api_secret, testnet)

    # Create monitored strategy engine
    strategy = MonitoredStrategyEngine(client, config)

    return client, strategy, client.metrics_tracker, strategy.alerting
