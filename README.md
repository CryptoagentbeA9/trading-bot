# Binance Trading Bot API Integration

Comprehensive Binance API integration module for automated trading with support for REST API, WebSocket streams, and complete trade execution capabilities.

## Features

- **REST API Integration**: Full access to Binance spot trading API
- **WebSocket Streaming**: Real-time market data and trade streams
- **Trade Execution**: Market and limit orders (buy/sell)
- **Account Management**: Balance tracking and P&L calculations
- **Rate Limiting**: Built-in rate limit compliance
- **Error Handling**: Automatic retry logic with exponential backoff
- **Testnet Support**: Safe testing environment before production

## Installation

```bash
pip install -r requirements.txt
```

## Configuration

1. Copy `.env.example` to `.env`:
```bash
cp .env.example .env
```

2. Add your Binance API credentials:
```
BINANCE_API_KEY=your_api_key_here
BINANCE_API_SECRET=your_api_secret_here
USE_TESTNET=true
```

## Usage

### Basic Example

```python
from binance_client import BinanceClient

# Initialize client
client = BinanceClient(testnet=True)

# Get account balance
balance = client.get_account_balance()
print(balance)

# Get top gainers
gainers = client.get_top_gainers(limit=10)
for gainer in gainers:
    print(f"{gainer['symbol']}: +{gainer['change_24h']:.2f}%")

# Execute market buy
order = client.execute_market_buy('BTC/USDT', 0.001)

# Get current price
price = client.get_current_price('BTC/USDT')
```

### WebSocket Streaming

```python
import asyncio

async def handle_ticker(data):
    print(f"Price: ${float(data['c']):.2f}")

async def main():
    client = BinanceClient(testnet=True)
    await client.stream_ticker('btcusdt', handle_ticker)

asyncio.run(main())
```

## API Methods

### Account & Balance
- `get_account_balance()` - Retrieve all asset balances
- `calculate_pnl()` - Calculate profit/loss for trades

### Market Data
- `get_top_gainers(limit)` - Fetch top gaining cryptocurrencies
- `get_current_price(symbol)` - Get current market price
- `get_trading_fees(symbol)` - Get trading fees

### Order Execution
- `execute_market_buy(symbol, amount)` - Market buy order
- `execute_market_sell(symbol, amount)` - Market sell order
- `execute_limit_buy(symbol, amount, price)` - Limit buy order
- `execute_limit_sell(symbol, amount, price)` - Limit sell order

### Order Management
- `get_order_status(order_id, symbol)` - Check order status
- `cancel_order(order_id, symbol)` - Cancel open order
- `get_open_orders(symbol)` - Get all open orders
- `get_order_history(symbol, limit)` - Get order history

### WebSocket Streams
- `stream_ticker(symbol, callback)` - Real-time ticker updates
- `stream_trades(symbol, callback)` - Real-time trade stream

## Rate Limiting

The client automatically handles Binance rate limits using ccxt's built-in rate limiting (`enableRateLimit=True`). Failed requests are automatically retried with exponential backoff.

## Error Handling

All methods include comprehensive error handling:
- Network errors trigger automatic retries
- Exchange errors are logged and raised
- Failed operations return `None` or empty collections

## Binance Square Monitoring

Note: Binance Square does not have a public API. For monitoring Square posts, you would need to implement web scraping using tools like Selenium or Playwright. This is not included in the current implementation due to potential ToS violations.

## Security Best Practices

1. Never commit `.env` file with real credentials
2. Use testnet for development and testing
3. Start with small amounts when testing on production
4. Enable IP whitelist on Binance API keys
5. Use read-only API keys when possible
6. Regularly rotate API keys

## Testing

Run the example script:
```bash
python example_usage.py
```

## Production Deployment

To switch to production:
1. Set `USE_TESTNET=false` in `.env`
2. Update API keys to production keys
3. Test thoroughly with small amounts first
4. Monitor rate limits and error logs

## License

MIT
