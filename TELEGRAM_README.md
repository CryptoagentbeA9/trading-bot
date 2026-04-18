# Telegram Bot Setup Guide

This guide will help you set up the Telegram bot for real-time trading monitoring and notifications.

## Prerequisites

- Python 3.8+
- Telegram account
- Trading bot running

## Step 1: Create Telegram Bot

1. Open Telegram and search for `@BotFather`
2. Start a chat and send `/newbot`
3. Follow the prompts to create your bot:
   - Choose a name (e.g., "My Trading Bot")
   - Choose a username (must end in 'bot', e.g., "my_trading_bot")
4. BotFather will give you a **bot token** - save this!

## Step 2: Get Your User ID

1. Search for `@userinfobot` on Telegram
2. Start a chat and it will send you your user ID
3. Save this number - you'll need it for authorization

## Step 3: Configure Environment Variables

Add these variables to your `.env` file:

```bash
# Telegram Bot Configuration
TELEGRAM_BOT_TOKEN=your_bot_token_here
TELEGRAM_ALLOWED_USERS=your_user_id_here

# Notification Settings (optional)
TELEGRAM_NOTIFY_TRADES=true
TELEGRAM_NOTIFY_POSITIONS=true
TELEGRAM_NOTIFY_ALERTS=true
TELEGRAM_NOTIFY_MILESTONES=true
```

### Multiple Users

To allow multiple users, separate IDs with commas:

```bash
TELEGRAM_ALLOWED_USERS=123456789,987654321
```

## Step 4: Install Dependencies

```bash
pip install python-telegram-bot
```

Or update from requirements.txt:

```bash
pip install -r requirements.txt
```

## Step 5: Start the Bot

### Standalone Mode

```python
from telegram_bot import create_bot
from metrics_tracker import MetricsTracker
from alerting import AlertingSystem
import logging

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

metrics = MetricsTracker()
alerting = AlertingSystem(logger)

bot = create_bot(metrics, alerting, logger)
bot.run()
```

### Integrated Mode

```python
# In your main trading bot
from telegram_bot import create_bot

# Create bot instance
telegram_bot = create_bot(metrics_tracker, alerting_system, logger)

# Start in background
import asyncio
asyncio.create_task(telegram_bot.start_async())
```

## Step 6: Test the Bot

1. Open Telegram and search for your bot username
2. Start a chat and send `/start`
3. You should see the welcome message with available commands

## Available Commands

- `/start` - Welcome message and help
- `/status` - Bot running status and metrics
- `/balance` - Account balance
- `/positions` - Current open positions
- `/trades` - Recent trade history
- `/pnl` - Profit & Loss summary
- `/alerts` - Recent system alerts
- `/subscribe` - Enable automated notifications
- `/unsubscribe` - Disable automated notifications
- `/help` - Show help message

## Automated Notifications

Once subscribed with `/subscribe`, you'll receive:

### Trade Notifications
- 🟢 Buy orders executed
- 🔴 Sell orders executed
- P&L for each trade

### Position Notifications
- ✅ Profitable position closures
- ❌ Loss position closures
- Stop-loss and take-profit triggers

### Milestone Notifications
- 🎉 Profit milestones (10%, 20%, 30%, 50%, 100%)
- Total P&L updates

### Alert Notifications
- ℹ️ Info alerts
- ⚠️ Warning alerts
- 🚨 Critical alerts (daily loss limit, API errors, etc.)

## Security Best Practices

1. **Keep your bot token secret** - Never commit it to version control
2. **Restrict user access** - Only add trusted user IDs to `TELEGRAM_ALLOWED_USERS`
3. **Use environment variables** - Store sensitive data in `.env` file
4. **Monitor unauthorized access** - Check logs for unauthorized access attempts

## Troubleshooting

### Bot doesn't respond

1. Check bot token is correct in `.env`
2. Verify bot is running (check logs)
3. Ensure your user ID is in `TELEGRAM_ALLOWED_USERS`

### Not receiving notifications

1. Send `/subscribe` to enable notifications
2. Check notification settings in `.env`
3. Verify alerting system is properly integrated

### "Unauthorized access" message

1. Verify your user ID is correct
2. Check `TELEGRAM_ALLOWED_USERS` in `.env`
3. Restart the bot after updating `.env`

## Integration Example

```python
from telegram_bot import create_bot
from telegram_notifier import TelegramNotifier
from metrics_tracker import MetricsTracker
from alerting import AlertingSystem
import logging

# Setup
logger = logging.getLogger(__name__)
metrics = MetricsTracker()
alerting = AlertingSystem(logger)

# Create bot
bot = create_bot(metrics, alerting, logger)

# Start bot in background
import asyncio
asyncio.create_task(bot.start_async())

# In your trading logic
def on_trade_executed(symbol, side, amount, price, pnl):
    # Record metrics
    metrics.record_trade(symbol, side, amount, price, pnl)
    
    # Notification sent automatically via alert handler

def on_position_closed(symbol, reason, pnl, pnl_pct):
    # Send notification
    bot.notifier.notify_position_closed(symbol, reason, pnl, pnl_pct)

def on_alert_triggered(alert):
    # Alert notification sent automatically via registered handler
    pass
```

## Advanced Configuration

### Custom Profit Milestones

Edit `telegram_config.py`:

```python
PROFIT_MILESTONES = [5, 10, 25, 50, 75, 100, 200]
```

### Disable Emojis

```python
USE_EMOJIS = False
```

### Disable Markdown Formatting

```python
USE_MARKDOWN = False
```

## Support

For issues or questions:
1. Check the logs for error messages
2. Verify configuration in `.env`
3. Review Telegram Bot API documentation: https://core.telegram.org/bots/api
