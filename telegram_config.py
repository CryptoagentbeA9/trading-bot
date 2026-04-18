"""
Telegram Bot Configuration
"""

import os
from dotenv import load_dotenv

load_dotenv()


class TelegramConfig:
    """Telegram bot configuration"""

    # Bot token from BotFather
    BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN', '')

    # Allowed user IDs (comma-separated in .env)
    ALLOWED_USERS = [
        int(uid.strip())
        for uid in os.getenv('TELEGRAM_ALLOWED_USERS', '').split(',')
        if uid.strip()
    ]

    # Notification settings
    NOTIFY_TRADES = os.getenv('TELEGRAM_NOTIFY_TRADES', 'true').lower() == 'true'
    NOTIFY_POSITIONS = os.getenv('TELEGRAM_NOTIFY_POSITIONS', 'true').lower() == 'true'
    NOTIFY_ALERTS = os.getenv('TELEGRAM_NOTIFY_ALERTS', 'true').lower() == 'true'
    NOTIFY_MILESTONES = os.getenv('TELEGRAM_NOTIFY_MILESTONES', 'true').lower() == 'true'

    # Milestone thresholds (%)
    PROFIT_MILESTONES = [10, 20, 30, 50, 100]

    # Message formatting
    USE_MARKDOWN = True
    USE_EMOJIS = True

    @classmethod
    def is_valid(cls) -> bool:
        """Check if configuration is valid"""
        return bool(cls.BOT_TOKEN and cls.ALLOWED_USERS)

    @classmethod
    def is_user_allowed(cls, user_id: int) -> bool:
        """Check if user is allowed to use the bot"""
        return user_id in cls.ALLOWED_USERS
