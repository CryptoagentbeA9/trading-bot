"""
Example Usage: Auto-Posting Module
Demonstrates how to use the auto-posting system
"""

import os
from datetime import datetime
from auto_poster import AutoPoster
from posting_config import PostingConfig

# Example 1: Basic configuration with Telegram only
def example_telegram_posting():
    """Simple example with Telegram"""
    config = PostingConfig(
        # Enable Telegram
        telegram_enabled=True,
        telegram_bot_token=os.getenv('TELEGRAM_BOT_TOKEN'),
        telegram_channel_id=os.getenv('TELEGRAM_CHANNEL_ID'),

        # Posting triggers
        post_on_profitable_trade=True,
        min_profit_percent_to_post=3.0,

        # Rate limits
        max_posts_per_day=10,
        min_hours_between_posts=1.0
    )

    poster = AutoPoster(config)

    # Post a trade update
    trade_data = {
        'symbol': 'BTC/USDT',
        'entry_price': 45000.0,
        'exit_price': 46800.0,
        'profit_pct': 4.0,
        'amount': 0.1,
        'timestamp': datetime.now()
    }

    poster.post_trade_update(trade_data)
    poster.cleanup()


# Example 2: Multi-platform configuration
def example_multi_platform():
    """Post to multiple platforms"""
    config = PostingConfig(
        # Binance Square
        binance_square_enabled=True,
        binance_square_email=os.getenv('BINANCE_EMAIL'),
        binance_square_password=os.getenv('BINANCE_PASSWORD'),

        # Twitter
        twitter_enabled=True,
        twitter_api_key=os.getenv('TWITTER_API_KEY'),
        twitter_api_secret=os.getenv('TWITTER_API_SECRET'),
        twitter_access_token=os.getenv('TWITTER_ACCESS_TOKEN'),
        twitter_access_secret=os.getenv('TWITTER_ACCESS_SECRET'),

        # Telegram
        telegram_enabled=True,
        telegram_bot_token=os.getenv('TELEGRAM_BOT_TOKEN'),
        telegram_channel_id=os.getenv('TELEGRAM_CHANNEL_ID'),

        # Content settings
        use_emojis=True,
        include_trade_details=True,

        # Rate limits
        max_posts_per_day=5,
        min_hours_between_posts=2.0
    )

    poster = AutoPoster(config)

    # Post trade update
    trade_data = {
        'symbol': 'ETH/USDT',
        'entry_price': 2500.0,
        'exit_price': 2650.0,
        'profit_pct': 6.0,
        'amount': 2.0,
        'timestamp': datetime.now()
    }

    poster.post_trade_update(trade_data, generate_image=True)
    poster.cleanup()


# Example 3: Integration with trading bot
def example_bot_integration():
    """How to integrate with the trading bot"""
    from binance_client import BinanceClient

    # Initialize clients
    binance = BinanceClient(testnet=True)

    config = PostingConfig(
        telegram_enabled=True,
        telegram_bot_token=os.getenv('TELEGRAM_BOT_TOKEN'),
        telegram_channel_id=os.getenv('TELEGRAM_CHANNEL_ID'),
        post_on_profitable_trade=True,
        min_profit_percent_to_post=5.0
    )

    poster = AutoPoster(config)

    # Simulate a trade
    symbol = 'BTC/USDT'
    entry_price = 45000.0

    # Execute buy
    buy_order = binance.execute_market_buy(symbol, 0.01)

    # Wait for price movement (in real bot, this would be strategy logic)
    # ...

    # Execute sell
    exit_price = 46500.0
    sell_order = binance.execute_market_sell(symbol, 0.01)

    # Calculate P&L
    pnl = binance.calculate_pnl(symbol, entry_price, exit_price, 0.01)

    # Post update if profitable
    trade_data = {
        'symbol': symbol,
        'entry_price': entry_price,
        'exit_price': exit_price,
        'profit_pct': pnl['pnl_percentage'],
        'amount': 0.01,
        'timestamp': datetime.now()
    }

    poster.post_trade_update(trade_data)
    poster.cleanup()


# Example 4: Scheduled summaries
def example_scheduled_summaries():
    """Post daily and weekly summaries"""
    config = PostingConfig(
        telegram_enabled=True,
        telegram_bot_token=os.getenv('TELEGRAM_BOT_TOKEN'),
        telegram_channel_id=os.getenv('TELEGRAM_CHANNEL_ID'),
        post_daily_summary=True,
        post_weekly_summary=True
    )

    poster = AutoPoster(config)

    # Post daily summary (call this once per day, e.g., at end of trading day)
    poster.post_daily_summary()

    # Post weekly summary (call this once per week, e.g., Sunday evening)
    poster.post_weekly_summary()

    poster.cleanup()


if __name__ == '__main__':
    # Run example
    print("Auto-Posting Module Examples")
    print("=" * 50)
    print("\n1. Telegram posting")
    print("2. Multi-platform posting")
    print("3. Bot integration")
    print("4. Scheduled summaries")
    print("\nUncomment the example you want to run in the code.")

    # Uncomment to run:
    # example_telegram_posting()
    # example_multi_platform()
    # example_bot_integration()
    # example_scheduled_summaries()
