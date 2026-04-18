"""
Telegram Notification System
Sends automated notifications to subscribed users
"""

import logging
from typing import List, Optional, Dict
from datetime import datetime
from telegram import Bot
from telegram.error import TelegramError

from telegram_config import TelegramConfig
from alerting import Alert, AlertLevel


class TelegramNotifier:
    """Send notifications via Telegram"""

    def __init__(self, bot_token: str, logger: logging.Logger):
        self.bot = Bot(token=bot_token)
        self.logger = logger
        self.subscribers: List[int] = []

    def add_subscriber(self, user_id: int):
        """Add a user to notification list"""
        if user_id not in self.subscribers:
            self.subscribers.append(user_id)
            self.logger.info(f"Added subscriber: {user_id}")

    def remove_subscriber(self, user_id: int):
        """Remove a user from notification list"""
        if user_id in self.subscribers:
            self.subscribers.remove(user_id)
            self.logger.info(f"Removed subscriber: {user_id}")

    def notify_trade(self, symbol: str, side: str, amount: float,
                    price: float, pnl: Optional[float] = None):
        """Notify about trade execution"""
        if not TelegramConfig.NOTIFY_TRADES:
            return

        emoji = "🟢" if side == "BUY" else "🔴"
        message = f"{emoji} *Trade Executed*\n\n"
        message += f"Symbol: `{symbol}`\n"
        message += f"Side: *{side}*\n"
        message += f"Amount: `{amount:.8f}`\n"
        message += f"Price: `${price:.2f}`\n"

        if pnl is not None:
            pnl_emoji = "💰" if pnl > 0 else "📉"
            message += f"\n{pnl_emoji} P&L: `${pnl:.2f}`"

        message += f"\n\n🕐 {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')} UTC"

        self._send_to_subscribers(message)

    def notify_position_closed(self, symbol: str, reason: str,
                              pnl: float, pnl_percentage: float):
        """Notify about position closure"""
        if not TelegramConfig.NOTIFY_POSITIONS:
            return

        emoji = "✅" if pnl > 0 else "❌"
        message = f"{emoji} *Position Closed*\n\n"
        message += f"Symbol: `{symbol}`\n"
        message += f"Reason: *{reason}*\n"
        message += f"P&L: `${pnl:.2f}` ({pnl_percentage:+.2f}%)\n"
        message += f"\n🕐 {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')} UTC"

        self._send_to_subscribers(message)

    def notify_milestone(self, milestone: float, total_pnl: float):
        """Notify about profit milestone"""
        if not TelegramConfig.NOTIFY_MILESTONES:
            return

        message = f"🎉 *Milestone Reached!*\n\n"
        message += f"Profit: *{milestone}%*\n"
        message += f"Total P&L: `${total_pnl:.2f}`\n"
        message += f"\n🕐 {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')} UTC"

        self._send_to_subscribers(message)

    def notify_alert(self, alert: Alert):
        """Notify about system alert"""
        if not TelegramConfig.NOTIFY_ALERTS:
            return

        emoji_map = {
            AlertLevel.INFO: "ℹ️",
            AlertLevel.WARNING: "⚠️",
            AlertLevel.CRITICAL: "🚨"
        }

        emoji = emoji_map.get(alert.level, "ℹ️")
        message = f"{emoji} *{alert.title}*\n\n"
        message += f"{alert.message}\n"

        if alert.metadata:
            message += f"\nDetails:\n"
            for key, value in alert.metadata.items():
                message += f"• {key}: `{value}`\n"

        message += f"\n🕐 {alert.timestamp}"

        self._send_to_subscribers(message)

    def send_message(self, user_id: int, message: str,
                    parse_mode: str = 'Markdown') -> bool:
        """Send message to specific user"""
        try:
            self.bot.send_message(
                chat_id=user_id,
                text=message,
                parse_mode=parse_mode if TelegramConfig.USE_MARKDOWN else None
            )
            return True
        except TelegramError as e:
            self.logger.error(f"Failed to send message to {user_id}: {e}")
            return False

    def _send_to_subscribers(self, message: str):
        """Send message to all subscribers"""
        for user_id in self.subscribers:
            self.send_message(user_id, message)

    def format_balance(self, balance: Dict) -> str:
        """Format balance information"""
        message = "💰 *Account Balance*\n\n"

        for currency, amount in balance.items():
            message += f"{currency}: `{amount:.8f}`\n"

        return message

    def format_positions(self, positions: List[Dict]) -> str:
        """Format positions information"""
        if not positions:
            return "📊 *Current Positions*\n\nNo open positions"

        message = "📊 *Current Positions*\n\n"

        for pos in positions:
            symbol = pos.get('symbol', 'N/A')
            side = pos.get('side', 'N/A')
            amount = pos.get('amount', 0)
            entry_price = pos.get('entry_price', 0)
            current_price = pos.get('current_price', 0)
            pnl = pos.get('pnl', 0)
            pnl_pct = pos.get('pnl_percentage', 0)

            emoji = "🟢" if pnl > 0 else "🔴"
            message += f"{emoji} `{symbol}` ({side})\n"
            message += f"  Amount: `{amount:.8f}`\n"
            message += f"  Entry: `${entry_price:.2f}`\n"
            message += f"  Current: `${current_price:.2f}`\n"
            message += f"  P&L: `${pnl:.2f}` ({pnl_pct:+.2f}%)\n\n"

        return message

    def format_trades(self, trades: List[Dict]) -> str:
        """Format recent trades"""
        if not trades:
            return "📈 *Recent Trades*\n\nNo recent trades"

        message = "📈 *Recent Trades*\n\n"

        for trade in trades[-10:]:
            symbol = trade.get('symbol', 'N/A')
            side = trade.get('side', 'N/A')
            amount = trade.get('amount', 0)
            price = trade.get('price', 0)
            pnl = trade.get('pnl')
            timestamp = trade.get('timestamp', '')

            emoji = "🟢" if side == "BUY" else "🔴"
            message += f"{emoji} `{symbol}` {side}\n"
            message += f"  Amount: `{amount:.8f}` @ `${price:.2f}`\n"

            if pnl is not None:
                pnl_emoji = "💰" if pnl > 0 else "📉"
                message += f"  {pnl_emoji} P&L: `${pnl:.2f}`\n"

            if timestamp:
                dt = datetime.fromisoformat(timestamp)
                message += f"  🕐 {dt.strftime('%m-%d %H:%M')}\n"

            message += "\n"

        return message

    def format_pnl_summary(self, total_pnl: float, daily_pnl: float,
                          win_rate: float, profit_factor: float) -> str:
        """Format P&L summary"""
        total_emoji = "💰" if total_pnl > 0 else "📉"
        daily_emoji = "💰" if daily_pnl > 0 else "📉"

        message = "📊 *P&L Summary*\n\n"
        message += f"{total_emoji} Total P&L: `${total_pnl:.2f}`\n"
        message += f"{daily_emoji} Daily P&L: `${daily_pnl:.2f}`\n"
        message += f"🎯 Win Rate: `{win_rate:.2f}%`\n"
        message += f"📈 Profit Factor: `{profit_factor:.2f}`\n"

        return message

    def format_alerts(self, alerts: List[Alert]) -> str:
        """Format recent alerts"""
        if not alerts:
            return "🔔 *Recent Alerts*\n\nNo recent alerts"

        message = "🔔 *Recent Alerts*\n\n"

        emoji_map = {
            AlertLevel.INFO: "ℹ️",
            AlertLevel.WARNING: "⚠️",
            AlertLevel.CRITICAL: "🚨"
        }

        for alert in alerts[-10:]:
            emoji = emoji_map.get(alert.level, "ℹ️")
            dt = datetime.fromisoformat(alert.timestamp)

            message += f"{emoji} *{alert.title}*\n"
            message += f"  {alert.message}\n"
            message += f"  🕐 {dt.strftime('%m-%d %H:%M')}\n\n"

        return message
