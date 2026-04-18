"""
Auto-Posting Module
Main module for automated social media posting of trading updates
"""

import logging
import time
from typing import Dict, List, Optional
from datetime import datetime, timedelta
import json
import os

from content_generator import ContentGenerator
from image_generator import ImageGenerator
from social_platforms import BinanceSquarePoster, TwitterPoster, TelegramPoster
from posting_config import PostingConfig

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class AutoPoster:
    """Automated posting system for trading updates"""

    def __init__(self, config: PostingConfig):
        self.config = config
        self.content_gen = ContentGenerator(use_emojis=config.use_emojis)
        self.image_gen = ImageGenerator()

        # Initialize platform clients
        self.platforms = {}
        self._init_platforms()

        # Rate limiting
        self.post_history = []
        self.last_post_time = None

        # Trade history for summaries
        self.trade_history_file = "trade_history.json"
        self.trade_history = self._load_trade_history()

    def _init_platforms(self):
        """Initialize social platform clients"""
        if self.config.binance_square_enabled:
            try:
                self.platforms['binance_square'] = BinanceSquarePoster(
                    email=self.config.binance_square_email,
                    password=self.config.binance_square_password
                )
                logger.info("Binance Square poster initialized")
            except Exception as e:
                logger.error(f"Failed to init Binance Square: {e}")

        if self.config.twitter_enabled:
            try:
                self.platforms['twitter'] = TwitterPoster(
                    api_key=self.config.twitter_api_key,
                    api_secret=self.config.twitter_api_secret,
                    access_token=self.config.twitter_access_token,
                    access_secret=self.config.twitter_access_secret
                )
                logger.info("Twitter poster initialized")
            except Exception as e:
                logger.error(f"Failed to init Twitter: {e}")

        if self.config.telegram_enabled:
            try:
                self.platforms['telegram'] = TelegramPoster(
                    bot_token=self.config.telegram_bot_token,
                    channel_id=self.config.telegram_channel_id
                )
                logger.info("Telegram poster initialized")
            except Exception as e:
                logger.error(f"Failed to init Telegram: {e}")

    def _load_trade_history(self) -> List[Dict]:
        """Load trade history from file"""
        if os.path.exists(self.trade_history_file):
            try:
                with open(self.trade_history_file, 'r') as f:
                    return json.load(f)
            except Exception as e:
                logger.error(f"Failed to load trade history: {e}")
        return []

    def _save_trade_history(self):
        """Save trade history to file"""
        try:
            with open(self.trade_history_file, 'w') as f:
                json.dump(self.trade_history, f, indent=2, default=str)
        except Exception as e:
            logger.error(f"Failed to save trade history: {e}")

    def _can_post(self) -> bool:
        """Check if posting is allowed based on rate limits"""
        now = datetime.now()

        # Check daily limit
        today_posts = [p for p in self.post_history if p['date'].date() == now.date()]
        if len(today_posts) >= self.config.max_posts_per_day:
            logger.warning("Daily post limit reached")
            return False

        # Check time between posts
        if self.last_post_time:
            hours_since_last = (now - self.last_post_time).total_seconds() / 3600
            if hours_since_last < self.config.min_hours_between_posts:
                logger.warning(f"Too soon since last post ({hours_since_last:.1f}h)")
                return False

        return True

    def _record_post(self):
        """Record a post in history"""
        self.post_history.append({'date': datetime.now()})
        self.last_post_time = datetime.now()

        # Keep only last 30 days
        cutoff = datetime.now() - timedelta(days=30)
        self.post_history = [p for p in self.post_history if p['date'] > cutoff]

    def post_trade_update(self, trade_data: Dict, generate_image: bool = True) -> bool:
        """
        Post a single trade update

        Args:
            trade_data: Trade information with keys:
                       symbol, entry_price, exit_price, profit_pct, amount, timestamp
            generate_image: Whether to generate and attach an image

        Returns:
            True if posted successfully to at least one platform
        """
        # Check if should post
        profit_pct = trade_data.get('profit_pct', 0)
        if not self.config.post_on_profitable_trade:
            return False
        if profit_pct < self.config.min_profit_percent_to_post:
            logger.info(f"Profit {profit_pct:.2f}% below threshold, skipping post")
            return False

        # Check rate limits
        if not self._can_post():
            return False

        # Generate content
        content = self.content_gen.generate_trade_post(trade_data)

        # Generate image
        image_path = None
        if generate_image:
            try:
                image_path = self.image_gen.generate_trade_card(trade_data)
            except Exception as e:
                logger.error(f"Failed to generate image: {e}")

        # Post to platforms
        success = False
        for platform_name, platform in self.platforms.items():
            try:
                if platform.post(content, image_path):
                    logger.info(f"Posted to {platform_name}")
                    success = True
                time.sleep(2)  # Delay between platforms
            except Exception as e:
                logger.error(f"Failed to post to {platform_name}: {e}")

        if success:
            self._record_post()
            # Add to trade history
            trade_data['posted'] = True
            trade_data['posted_at'] = datetime.now()
            self.trade_history.append(trade_data)
            self._save_trade_history()

        return success

    def post_daily_summary(self) -> bool:
        """Post daily trading summary"""
        if not self.config.post_daily_summary or not self._can_post():
            return False

        # Calculate daily stats
        today = datetime.now().date()
        today_trades = [t for t in self.trade_history
                       if isinstance(t.get('timestamp'), datetime) and
                       t['timestamp'].date() == today]

        if not today_trades:
            logger.info("No trades today, skipping daily summary")
            return False

        summary_data = {
            'date': today.strftime('%Y-%m-%d'),
            'total_trades': len(today_trades),
            'winning_trades': len([t for t in today_trades if t.get('profit_pct', 0) > 0]),
            'total_profit_pct': sum(t.get('profit_pct', 0) for t in today_trades),
            'best_trade': max(today_trades, key=lambda t: t.get('profit_pct', 0))
        }

        # Generate content and image
        content = self.content_gen.generate_daily_summary(summary_data)
        image_path = None
        try:
            image_path = self.image_gen.generate_summary_card(summary_data, "Daily")
        except Exception as e:
            logger.error(f"Failed to generate summary image: {e}")

        # Post to platforms
        success = False
        for platform_name, platform in self.platforms.items():
            try:
                if platform.post(content, image_path):
                    logger.info(f"Posted daily summary to {platform_name}")
                    success = True
                time.sleep(2)
            except Exception as e:
                logger.error(f"Failed to post daily summary to {platform_name}: {e}")

        if success:
            self._record_post()

        return success

    def post_weekly_summary(self) -> bool:
        """Post weekly trading summary"""
        if not self.config.post_weekly_summary or not self._can_post():
            return False

        # Calculate weekly stats
        now = datetime.now()
        week_start = now - timedelta(days=7)
        week_trades = [t for t in self.trade_history
                      if isinstance(t.get('timestamp'), datetime) and
                      t['timestamp'] >= week_start]

        if not week_trades:
            logger.info("No trades this week, skipping weekly summary")
            return False

        # Get top performers
        sorted_trades = sorted(week_trades, key=lambda t: t.get('profit_pct', 0), reverse=True)

        summary_data = {
            'week': now.isocalendar()[1],
            'total_trades': len(week_trades),
            'winning_trades': len([t for t in week_trades if t.get('profit_pct', 0) > 0]),
            'total_profit_pct': sum(t.get('profit_pct', 0) for t in week_trades),
            'top_performers': sorted_trades[:5]
        }

        # Generate content and image
        content = self.content_gen.generate_weekly_summary(summary_data)
        image_path = None
        try:
            image_path = self.image_gen.generate_pnl_chart(week_trades, "Weekly P&L")
        except Exception as e:
            logger.error(f"Failed to generate weekly chart: {e}")

        # Post to platforms
        success = False
        for platform_name, platform in self.platforms.items():
            try:
                if platform.post(content, image_path):
                    logger.info(f"Posted weekly summary to {platform_name}")
                    success = True
                time.sleep(2)
            except Exception as e:
                logger.error(f"Failed to post weekly summary to {platform_name}: {e}")

        if success:
            self._record_post()

        return success

    def cleanup(self):
        """Cleanup resources"""
        if 'binance_square' in self.platforms:
            self.platforms['binance_square'].close()
