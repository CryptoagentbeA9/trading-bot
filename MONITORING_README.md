# Trading Bot Monitoring System

Comprehensive monitoring and logging system for the Binance trading bot with real-time dashboard, structured logging, metrics tracking, and alerting.

## Features

### 1. Structured Logging
- **JSON Format**: Machine-readable logs for easy parsing and analysis
- **Log Rotation**: Automatic rotation with 10MB file size limit
- **Separate Log Files**:
  - `logs/app.log` - Main application log (text format)
  - `logs/trades.json` - Trade execution log (JSON)
  - `logs/api.json` - API calls with performance metrics (JSON)
  - `logs/errors.log` - Error log with stack traces

### 2. Real-Time Web Dashboard
- **Live Metrics**: Auto-refreshes every 5 seconds
- **Bot Status**: Uptime and current status
- **Performance Metrics**: Total trades, win rate, P&L
- **Open Positions**: Real-time position tracking
- **Trade History**: Recent trade executions
- **Alerts**: Critical events and warnings

Access at: `http://localhost:5000`

### 3. Metrics Tracking
- **Trade Metrics**: Total trades, win rate, profit factor
- **P&L Tracking**: Daily, weekly, monthly summaries
- **API Health**: Response times, success rates, error counts
- **System Metrics**: Uptime, active positions

### 4. Alerting System
- **Critical Alerts**:
  - Daily loss limit exceeded
  - Consecutive loss limit reached
  - Position exposure limit exceeded
  - Trade execution failures
  
- **Warning Alerts**:
  - High API error rate
  - Low win rate detected
  - Performance anomalies

## Installation

```bash
pip install -r requirements.txt
```

## Usage

### Basic Usage with Monitoring

```python
from monitoring_integration import create_monitored_bot
from dashboard import TradingDashboard

# Create monitored bot
client, strategy, metrics_tracker, alerting = create_monitored_bot(testnet=True)

# Start web dashboard
dashboard = TradingDashboard(
    metrics_tracker=metrics_tracker,
    alerting_system=alerting,
    strategy_engine=strategy,
    port=5000
)
dashboard.run_background()

# Run trading strategy
while True:
    summary = strategy.run_strategy_cycle()
    time.sleep(300)  # 5 minutes
```

### Run Complete Example

```bash
python run_with_monitoring.py
```

## Dashboard API Endpoints

- `GET /api/status` - Bot status and uptime
- `GET /api/metrics` - Current performance metrics
- `GET /api/performance` - Daily/weekly/monthly summaries
- `GET /api/positions` - Open positions
- `GET /api/trades?limit=20` - Recent trades
- `GET /api/alerts?limit=50` - Recent alerts
- `GET /api/api-health` - API health metrics
- `GET /api/export` - Export all metrics

## Log Format Examples

### Trade Log (JSON)
```json
{
  "timestamp": "2026-04-18T10:30:00.000Z",
  "level": "INFO",
  "logger": "trading_bot.trades",
  "message": "BUY BTC/USDT @ $65000.0000",
  "trade_data": {
    "type": "BUY",
    "symbol": "BTC/USDT",
    "amount": 0.001,
    "price": 65000.0,
    "timestamp": "2026-04-18T10:30:00.000Z"
  }
}
```

### API Log (JSON)
```json
{
  "timestamp": "2026-04-18T10:30:00.000Z",
  "level": "DEBUG",
  "logger": "trading_bot.api",
  "message": "API GET /api/v3/ticker/24hr - 150.25ms",
  "api_data": {
    "endpoint": "/api/v3/ticker/24hr",
    "method": "GET",
    "response_time_ms": 150.25,
    "status_code": 200,
    "timestamp": "2026-04-18T10:30:00.000Z"
  }
}
```

## Alert Configuration

Default alert thresholds (configurable in `alerting.py`):

```python
daily_loss_limit = 50.0  # USD
consecutive_loss_limit = 3
api_error_threshold = 10
position_limit = 500.0  # USD
```

## Metrics Export

Export all metrics to JSON:

```python
metrics = metrics_tracker.export_metrics()

# Includes:
# - System metrics (uptime, trades, P&L)
# - Daily/weekly/monthly summaries
# - API health statistics
# - Recent trades
```

## Directory Structure

```
trading-bot/
├── logs/                      # Log files
│   ├── app.log               # Main application log
│   ├── trades.json           # Trade execution log
│   ├── api.json              # API calls log
│   └── errors.log            # Error log
├── metrics/                   # Metrics data
│   └── trades_YYYY-MM-DD.json
├── templates/                 # Dashboard HTML
│   └── dashboard.html
├── logger_config.py          # Logging configuration
├── metrics_tracker.py        # Metrics tracking
├── alerting.py               # Alerting system
├── dashboard.py              # Web dashboard
├── monitoring_integration.py # Integration module
└── run_with_monitoring.py    # Example usage
```

## Monitoring Best Practices

1. **Log Retention**: Logs rotate automatically, keep backups for compliance
2. **Alert Tuning**: Adjust thresholds based on your risk tolerance
3. **Dashboard Access**: Secure the dashboard in production (add authentication)
4. **Metrics Analysis**: Review daily summaries to optimize strategy
5. **API Health**: Monitor API response times to detect issues early

## Troubleshooting

### Dashboard Not Loading
- Check if Flask is running: `netstat -an | grep 5000`
- Verify no port conflicts
- Check logs in `logs/app.log`

### Missing Logs
- Ensure `logs/` directory exists and is writable
- Check disk space
- Verify logging configuration

### High Memory Usage
- Reduce log retention (decrease `backupCount`)
- Limit metrics history (adjust `deque` maxlen)
- Clear old metrics files

## Performance Impact

The monitoring system is designed to be lightweight:
- **CPU**: <1% overhead
- **Memory**: ~50MB for metrics tracking
- **Disk I/O**: Minimal (async logging)
- **Network**: Dashboard only (no external calls)

## Security Considerations

1. **Dashboard Access**: Add authentication in production
2. **Log Sanitization**: PII and API keys are not logged
3. **Metrics Privacy**: Store metrics locally, no external transmission
4. **Alert Handlers**: Secure notification channels (HTTPS, encrypted)

## Future Enhancements

- [ ] Prometheus/Grafana integration
- [ ] Email/SMS alert handlers
- [ ] Advanced analytics and ML insights
- [ ] Historical data visualization
- [ ] Multi-bot monitoring
- [ ] Cloud metrics export (CloudWatch, Datadog)
