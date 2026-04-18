# Trading Bot - Auto-Posting Module

## Overview
Automated social media posting system for sharing trading updates, profits, and performance summaries.

## Features

### 1. Content Generation
- Trade update posts with entry/exit prices and profit percentage
- Daily performance summaries
- Weekly trading reports
- Customizable content with emoji support

### 2. Image Generation
- Trade result cards with visual profit indicators
- P&L charts showing cumulative performance
- Summary cards with key metrics
- Professional dark theme design

### 3. Platform Support
- **Binance Square**: Web automation using Selenium
- **Twitter/X**: API integration using Tweepy
- **Telegram**: Bot API for channel posting

### 4. Smart Posting
- Rate limiting (configurable posts per day)
- Minimum time between posts
- Profit threshold filtering
- Automatic scheduling for summaries

## Installation

### Required Dependencies
```bash
pip install matplotlib pillow selenium tweepy requests
```

### Optional Dependencies
- **Chrome WebDriver**: Required for Binance Square posting
  - Download from: https://chromedriver.chromium.org/
  - Add to system PATH

## Configuration

### Environment Variables
Create a `.env` file:
```env
# Binance Square
BINANCE_EMAIL=your_email@example.com
BINANCE_PASSWORD=your_password

# Twitter/X API
TWITTER_API_KEY=your_api_key
TWITTER_API_SECRET=your_api_secret
TWITTER_ACCESS_TOKEN=your_access_token
TWITTER_ACCESS_SECRET=your_access_secret

# Telegram
TELEGRAM_BOT_TOKEN=your_bot_token
TELEGRAM_CHANNEL_ID=@your_channel
```

### PostingConfig Options
```python
from posting_config import PostingConfig

config = PostingConfig(
    # Triggers
    post_on_profitable_trade=True,
    min_profit_percent_to_post=5.0,
    post_daily_summary=True,
    post_weekly_summary=True,
    
    # Rate limits
    max_posts_per_day=5,
    min_hours_between_posts=2.0,
    
    # Content
    use_emojis=True,
    include_trade_details=True,
    include_account_balance=False,  # Privacy
    
    # Platforms
    telegram_enabled=True,
    twitter_enabled=False,
    binance_square_enabled=False
)
```

## Usage

### Basic Trade Posting
```python
from auto_poster import AutoPoster
from posting_config import PostingConfig
from datetime import datetime

config = PostingConfig(telegram_enabled=True)
poster = AutoPoster(config)

trade_data = {
    'symbol': 'BTC/USDT',
    'entry_price': 45000.0,
    'exit_price': 46800.0,
    'profit_pct': 4.0,
    'amount': 0.1,
    'timestamp': datetime.now()
}

poster.post_trade_update(trade_data, generate_image=True)
poster.cleanup()
```

### Integration with Trading Bot
```python
from binance_client import BinanceClient
from auto_poster import AutoPoster

# Initialize
binance = BinanceClient()
poster = AutoPoster(config)

# After closing a trade
pnl = binance.calculate_pnl(symbol, entry_price, exit_price, amount)

trade_data = {
    'symbol': symbol,
    'entry_price': entry_price,
    'exit_price': exit_price,
    'profit_pct': pnl['pnl_percentage'],
    'amount': amount,
    'timestamp': datetime.now()
}

# Auto-post if profitable enough
poster.post_trade_update(trade_data)
```

### Scheduled Summaries
```python
# Daily summary (run at end of trading day)
poster.post_daily_summary()

# Weekly summary (run on Sunday)
poster.post_weekly_summary()
```

## Module Structure

```
trading-bot/
├── auto_poster.py           # Main posting orchestrator
├── content_generator.py     # Text content generation
├── image_generator.py       # Chart and card generation
├── social_platforms.py      # Platform integrations
├── posting_config.py        # Configuration dataclass
├── example_auto_posting.py  # Usage examples
└── post_images/            # Generated images (auto-created)
```

## Rate Limiting

The module includes built-in rate limiting to prevent spam:
- Maximum posts per day (default: 5)
- Minimum hours between posts (default: 2.0)
- Profit threshold for trade posts (default: 5%)

Posts are tracked in memory and only recent history is kept.

## Image Generation

Images are automatically generated and saved to `./post_images/`:
- Trade cards: 800x600px with profit indicators
- P&L charts: Line charts showing cumulative performance
- Summary cards: Daily/weekly metrics visualization

All images use a professional dark theme with green/red profit indicators.

## Platform-Specific Notes

### Binance Square
- Uses Selenium for web automation
- Requires Chrome/ChromeDriver
- Login credentials needed
- Headless mode supported
- May require CAPTCHA handling

### Twitter/X
- Requires Twitter Developer account
- API v2 with OAuth 1.0a
- 280 character limit enforced
- Image uploads supported

### Telegram
- Easiest to set up
- Create bot via @BotFather
- Add bot to channel as admin
- Supports HTML formatting
- No character limits

## Security Considerations

1. **Credentials**: Store in environment variables, never commit
2. **Account Balance**: Disabled by default in posts
3. **Rate Limiting**: Prevents account suspension
4. **Error Handling**: Graceful failures, no data loss

## Troubleshooting

### Selenium Issues
```bash
# Install Chrome WebDriver
# Windows: Download and add to PATH
# Linux: sudo apt-get install chromium-chromedriver
```

### Twitter API Errors
- Verify API credentials
- Check rate limits
- Ensure elevated access if needed

### Image Generation Fails
- Install fonts: `sudo apt-get install fonts-liberation`
- Check write permissions on `./post_images/`

## Future Enhancements

- Discord integration
- Instagram posting
- Advanced chart types
- A/B testing for content
- Analytics tracking
- Multi-language support

## Examples

See `example_auto_posting.py` for complete working examples:
1. Telegram-only posting
2. Multi-platform posting
3. Trading bot integration
4. Scheduled summaries
