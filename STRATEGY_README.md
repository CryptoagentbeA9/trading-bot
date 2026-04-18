# Trading Strategy Engine

## Overview
The strategy engine analyzes market data from Binance, generates trading signals, manages positions, and executes trades with comprehensive risk management.

## Components

### 1. Strategy Configuration (`strategy_config.py`)
Centralized configuration for all strategy parameters:

**Market Analysis:**
- `min_gain_percent`: Minimum 24h gain to consider (default: 5%)
- `min_volume_usdt`: Minimum volume in USDT (default: 1M)
- `top_gainers_limit`: Number of top gainers to analyze (default: 20)

**Risk Management:**
- `position_size_percent`: Portfolio % per trade (default: 2%)
- `max_concurrent_positions`: Max open positions (default: 3)
- `daily_loss_limit_percent`: Daily loss limit (default: 5%)

**Stop Loss / Take Profit:**
- `stop_loss_percent`: Stop loss % (default: 3%)
- `take_profit_percent`: Take profit % (default: 8%)
- `trailing_stop_percent`: Trailing stop % (default: 2%)

**Trade Execution:**
- `min_trade_amount_usdt`: Min trade size (default: $10)
- `max_trade_amount_usdt`: Max trade size (default: $1000)

### 2. Strategy Engine (`strategy_engine.py`)

#### Core Classes

**Position:**
- Tracks open positions with entry price, amount, stop-loss, take-profit
- Monitors highest price for trailing stops

**TradeSignal:**
- Generated signals with action (BUY/SELL/HOLD), confidence, and reasoning

**PerformanceMetrics:**
- Tracks total trades, win rate, P&L, daily performance

**StrategyEngine:**
Main engine with the following methods:

#### Key Methods

**`analyze_market_data(gainers)`**
- Analyzes top gainers from Binance
- Filters by min gain % and volume requirements
- Calculates confidence scores based on rank, price change, and volume
- Returns sorted list of trade signals

**`check_position_exits()`**
- Monitors all open positions
- Checks stop-loss, take-profit, and trailing stop triggers
- Returns list of positions to exit

**`calculate_position_size(symbol, price)`**
- Calculates trade size based on portfolio %
- Enforces min/max trade limits
- Checks max concurrent positions
- Validates daily loss limits

**`execute_buy(signal)`**
- Executes market buy order
- Opens position with calculated stop-loss and take-profit levels
- Tracks position in internal state

**`execute_sell(symbol, reason)`**
- Executes market sell order
- Closes position and calculates P&L
- Updates performance metrics

**`run_strategy_cycle()`**
- Complete strategy execution cycle:
  1. Check and close positions hitting exit conditions
  2. Fetch top gainers from Binance
  3. Generate trading signals
  4. Execute buy orders for top signals (respecting position limits)
- Returns summary of actions taken

**`get_performance_summary()`**
- Returns current performance metrics

**`get_open_positions()`**
- Returns detailed info on all open positions with unrealized P&L

**`reset_daily_metrics()`**
- Resets daily counters (call at start of trading day)

## Usage Example

```python
from binance_client import BinanceClient
from strategy_engine import StrategyEngine
from strategy_config import StrategyConfig

# Initialize
client = BinanceClient(testnet=True)
config = StrategyConfig()
engine = StrategyEngine(client, config)

# Reset daily metrics
engine.reset_daily_metrics()

# Run strategy cycle
summary = engine.run_strategy_cycle()
print(f"Signals: {summary['signals_generated']}")
print(f"Opened: {summary['positions_opened']}")
print(f"Closed: {summary['positions_closed']}")

# Check performance
metrics = engine.get_performance_summary()
print(f"Win rate: {metrics['win_rate']}")
print(f"Total P&L: {metrics['total_pnl']}")

# View open positions
positions = engine.get_open_positions()
for pos in positions:
    print(f"{pos['symbol']}: {pos['unrealized_pnl']}")
```

## Strategy Logic

### Signal Generation
1. Fetch top gainers by 24h % change
2. Filter by minimum gain % and volume thresholds
3. Calculate confidence score:
   - 40% weight: Rank position (higher rank = higher confidence)
   - 40% weight: Price change % (higher change = higher confidence)
   - 20% weight: Volume (higher volume = higher confidence)
4. Sort signals by confidence

### Position Management
- **Entry**: Market buy at current price
- **Stop Loss**: Set at entry price - stop_loss_percent
- **Take Profit**: Set at entry price + take_profit_percent
- **Trailing Stop**: Adjusts as price increases, locks in profits

### Risk Controls
- Position sizing: Fixed % of portfolio per trade
- Max concurrent positions: Limits exposure
- Daily loss limit: Stops trading if daily loss exceeds threshold
- Min/max trade amounts: Prevents too small or too large trades

## Testing

Run the test script:
```bash
python test_strategy.py
```

Note: Binance testnet API may be unavailable. For production testing, use real API credentials with caution.

## Integration

The strategy engine integrates with:
- `binance_client.py`: For market data and trade execution
- Configuration file: For strategy parameters
- Monitoring system: For performance tracking
- Auto-posting module: For trade notifications
