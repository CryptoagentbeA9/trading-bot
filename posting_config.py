"""
Auto-Posting Configuration
Settings for social media posting and content generation
"""

from dataclasses import dataclass
from typing import List, Optional


@dataclass
class PostingConfig:
    """Configuration for auto-posting module"""

    # Posting triggers
    post_on_profitable_trade: bool = True
    min_profit_percent_to_post: float = 5.0
    post_daily_summary: bool = True
    post_weekly_summary: bool = True

    # Posting frequency limits
    max_posts_per_day: int = 5
    min_hours_between_posts: float = 2.0

    # Content settings
    include_trade_details: bool = True
    include_profit_percentage: bool = True
    include_account_balance: bool = False  # Privacy consideration
    use_emojis: bool = True

    # Platform settings
    platforms: List[str] = None

    # Binance Square
    binance_square_enabled: bool = False
    binance_square_email: Optional[str] = None
    binance_square_password: Optional[str] = None

    # Twitter/X
    twitter_enabled: bool = False
    twitter_api_key: Optional[str] = None
    twitter_api_secret: Optional[str] = None
    twitter_access_token: Optional[str] = None
    twitter_access_secret: Optional[str] = None

    # Telegram
    telegram_enabled: bool = False
    telegram_bot_token: Optional[str] = None
    telegram_channel_id: Optional[str] = None

    def __post_init__(self):
        if self.platforms is None:
            self.platforms = []
            if self.binance_square_enabled:
                self.platforms.append('binance_square')
            if self.twitter_enabled:
                self.platforms.append('twitter')
            if self.telegram_enabled:
                self.platforms.append('telegram')
