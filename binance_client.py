"""
Binance API Integration Module
Provides comprehensive trading bot functionality including:
- REST API and WebSocket connections
- Real-time market data streaming
- Trade execution (buy/sell)
- Account balance and P&L tracking
- Rate limiting and error handling
"""

import ccxt
import os
import time
import logging
from typing import Dict, List, Optional, Tuple
from datetime import datetime
import asyncio
import websockets
import json

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class BinanceClient:
    """Binance API client with comprehensive trading functionality"""

    def __init__(self, api_key: Optional[str] = None, api_secret: Optional[str] = None, testnet: bool = True):
        """
        Initialize Binance client

        Args:
            api_key: Binance API key (defaults to BINANCE_API_KEY env var)
            api_secret: Binance API secret (defaults to BINANCE_API_SECRET env var)
            testnet: Use testnet if True, production if False
        """
        self.api_key = api_key or os.getenv('BINANCE_API_KEY')
        self.api_secret = api_secret or os.getenv('BINANCE_API_SECRET')

        if testnet:
            self.exchange = ccxt.binance({
                'apiKey': self.api_key,
                'secret': self.api_secret,
                'enableRateLimit': True,
                'options': {'defaultType': 'spot'},
                'urls': {
                    'api': {
                        'public': 'https://testnet.binance.vision/api',
                        'private': 'https://testnet.binance.vision/api',
                    }
                }
            })
        else:
            self.exchange = ccxt.binance({
                'apiKey': self.api_key,
                'secret': self.api_secret,
                'enableRateLimit': True,
                'options': {'defaultType': 'spot'}
            })

        self.ws_url = 'wss://stream.binance.com:9443/ws' if not testnet else 'wss://testnet.binance.vision/ws'
        self.retry_count = 3
        self.retry_delay = 2

        logger.info(f"Binance client initialized ({'testnet' if testnet else 'production'})")

    def _retry_on_failure(self, func, *args, **kwargs):
        """Retry logic for API calls"""
        for attempt in range(self.retry_count):
            try:
                return func(*args, **kwargs)
            except ccxt.NetworkError as e:
                logger.warning(f"Network error (attempt {attempt + 1}/{self.retry_count}): {e}")
                if attempt < self.retry_count - 1:
                    time.sleep(self.retry_delay * (attempt + 1))
            except ccxt.ExchangeError as e:
                logger.error(f"Exchange error: {e}")
                raise
        raise Exception(f"Failed after {self.retry_count} attempts")

    def get_account_balance(self) -> Dict[str, float]:
        """
        Retrieve account balance for all assets

        Returns:
            Dict mapping asset symbols to available balances
        """
        try:
            balance = self._retry_on_failure(self.exchange.fetch_balance)
            return {k: v['free'] for k, v in balance.items() if v['free'] > 0}
        except Exception as e:
            logger.error(f"Error fetching balance: {e}")
            return {}

    def get_top_gainers(self, limit: int = 10) -> List[Dict]:
        """
        Fetch top gaining cryptocurrencies by 24h price change

        Args:
            limit: Number of top gainers to return

        Returns:
            List of dicts with symbol, price, and percentage change
        """
        try:
            tickers = self._retry_on_failure(self.exchange.fetch_tickers)

            gainers = []
            for symbol, ticker in tickers.items():
                if ticker.get('percentage') and '/USDT' in symbol:
                    gainers.append({
                        'symbol': symbol,
                        'price': ticker['last'],
                        'change_24h': ticker['percentage'],
                        'volume': ticker.get('quoteVolume', 0)
                    })

            gainers.sort(key=lambda x: x['change_24h'], reverse=True)
            return gainers[:limit]
        except Exception as e:
            logger.error(f"Error fetching top gainers: {e}")
            return []

    def execute_market_buy(self, symbol: str, amount: float) -> Optional[Dict]:
        """
        Execute market buy order

        Args:
            symbol: Trading pair (e.g., 'BTC/USDT')
            amount: Amount of base currency to buy

        Returns:
            Order details or None if failed
        """
        try:
            order = self._retry_on_failure(
                self.exchange.create_market_buy_order,
                symbol,
                amount
            )
            logger.info(f"Market buy executed: {symbol} amount={amount}")
            return order
        except Exception as e:
            logger.error(f"Error executing market buy: {e}")
            return None

    def execute_market_sell(self, symbol: str, amount: float) -> Optional[Dict]:
        """
        Execute market sell order

        Args:
            symbol: Trading pair (e.g., 'BTC/USDT')
            amount: Amount of base currency to sell

        Returns:
            Order details or None if failed
        """
        try:
            order = self._retry_on_failure(
                self.exchange.create_market_sell_order,
                symbol,
                amount
            )
            logger.info(f"Market sell executed: {symbol} amount={amount}")
            return order
        except Exception as e:
            logger.error(f"Error executing market sell: {e}")
            return None

    def execute_limit_buy(self, symbol: str, amount: float, price: float) -> Optional[Dict]:
        """Execute limit buy order"""
        try:
            order = self._retry_on_failure(
                self.exchange.create_limit_buy_order,
                symbol,
                amount,
                price
            )
            logger.info(f"Limit buy executed: {symbol} amount={amount} price={price}")
            return order
        except Exception as e:
            logger.error(f"Error executing limit buy: {e}")
            return None

    def execute_limit_sell(self, symbol: str, amount: float, price: float) -> Optional[Dict]:
        """Execute limit sell order"""
        try:
            order = self._retry_on_failure(
                self.exchange.create_limit_sell_order,
                symbol,
                amount,
                price
            )
            logger.info(f"Limit sell executed: {symbol} amount={amount} price={price}")
            return order
        except Exception as e:
            logger.error(f"Error executing limit sell: {e}")
            return None

    def get_order_status(self, order_id: str, symbol: str) -> Optional[Dict]:
        """Check order status"""
        try:
            order = self._retry_on_failure(
                self.exchange.fetch_order,
                order_id,
                symbol
            )
            return order
        except Exception as e:
            logger.error(f"Error fetching order status: {e}")
            return None

    def cancel_order(self, order_id: str, symbol: str) -> bool:
        """Cancel an open order"""
        try:
            self._retry_on_failure(
                self.exchange.cancel_order,
                order_id,
                symbol
            )
            logger.info(f"Order cancelled: {order_id}")
            return True
        except Exception as e:
            logger.error(f"Error cancelling order: {e}")
            return False

    def get_current_price(self, symbol: str) -> Optional[float]:
        """Get current market price for a symbol"""
        try:
            ticker = self._retry_on_failure(self.exchange.fetch_ticker, symbol)
            return ticker['last']
        except Exception as e:
            logger.error(f"Error fetching price: {e}")
            return None

    def calculate_pnl(self, symbol: str, entry_price: float, exit_price: float, amount: float) -> Dict:
        """
        Calculate profit/loss for a trade

        Args:
            symbol: Trading pair
            entry_price: Entry price
            exit_price: Exit price
            amount: Trade amount

        Returns:
            Dict with PnL details
        """
        pnl = (exit_price - entry_price) * amount
        pnl_percentage = ((exit_price - entry_price) / entry_price) * 100

        return {
            'symbol': symbol,
            'entry_price': entry_price,
            'exit_price': exit_price,
            'amount': amount,
            'pnl': pnl,
            'pnl_percentage': pnl_percentage
        }

    async def stream_ticker(self, symbol: str, callback):
        """
        Stream real-time ticker data via WebSocket

        Args:
            symbol: Trading pair (e.g., 'btcusdt')
            callback: Function to call with ticker updates
        """
        stream = f"{symbol.lower().replace('/', '')}@ticker"
        uri = f"{self.ws_url}/{stream}"

        while True:
            try:
                async with websockets.connect(uri) as websocket:
                    logger.info(f"WebSocket connected: {symbol}")
                    while True:
                        msg = await websocket.recv()
                        data = json.loads(msg)
                        await callback(data)
            except Exception as e:
                logger.error(f"WebSocket error: {e}")
                await asyncio.sleep(5)

    async def stream_trades(self, symbol: str, callback):
        """Stream real-time trade data"""
        stream = f"{symbol.lower().replace('/', '')}@trade"
        uri = f"{self.ws_url}/{stream}"

        while True:
            try:
                async with websockets.connect(uri) as websocket:
                    logger.info(f"Trade stream connected: {symbol}")
                    while True:
                        msg = await websocket.recv()
                        data = json.loads(msg)
                        await callback(data)
            except Exception as e:
                logger.error(f"Trade stream error: {e}")
                await asyncio.sleep(5)

    def get_trading_fees(self, symbol: str) -> Optional[Dict]:
        """Get trading fees for a symbol"""
        try:
            fees = self._retry_on_failure(self.exchange.fetch_trading_fees)
            return fees.get(symbol, {})
        except Exception as e:
            logger.error(f"Error fetching fees: {e}")
            return None

    def get_open_orders(self, symbol: Optional[str] = None) -> List[Dict]:
        """Get all open orders"""
        try:
            orders = self._retry_on_failure(self.exchange.fetch_open_orders, symbol)
            return orders
        except Exception as e:
            logger.error(f"Error fetching open orders: {e}")
            return []

    def get_order_history(self, symbol: str, limit: int = 50) -> List[Dict]:
        """Get order history"""
        try:
            orders = self._retry_on_failure(
                self.exchange.fetch_orders,
                symbol,
                None,
                limit
            )
            return orders
        except Exception as e:
            logger.error(f"Error fetching order history: {e}")
            return []
