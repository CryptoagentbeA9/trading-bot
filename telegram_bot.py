"""
Telegram Bot for Trading Monitoring
Provides real-time updates and commands for trading bot status
"""

import logging
import asyncio
from typing import Optional
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters
)

from telegram_config import TelegramConfig
from telegram_notifier import TelegramNotifier
from metrics_tracker import MetricsTracker
from alerting import AlertingSystem


class TradingTelegramBot:
    """Telegram bot for trading monitoring"""

    def __init__(self, metrics_tracker: MetricsTracker,
                 alerting_system: AlertingSystem,
                 logger: logging.Logger):
        self.metrics = metrics_tracker
        self.alerting = alerting_system
        self.logger = logger

        if not TelegramConfig.is_valid():
            raise ValueError("Invalid Telegram configuration")

        self.notifier = TelegramNotifier(TelegramConfig.BOT_TOKEN, logger)
        self.app = Application.builder().token(TelegramConfig.BOT_TOKEN).build()

        # Register alert handler
        self.alerting.register_handler(self.notifier.notify_alert)

        # Register command handlers
        self._register_handlers()

    def _register_handlers(self):
        """Register bot command handlers"""
        self.app.add_handler(CommandHandler("start", self.cmd_start))
        self.app.add_handler(CommandHandler("help", self.cmd_help))
        self.app.add_handler(CommandHandler("status", self.cmd_status))
        self.app.add_handler(CommandHandler("balance", self.cmd_balance))
        self.app.add_handler(CommandHandler("positions", self.cmd_positions))
        self.app.add_handler(CommandHandler("trades", self.cmd_trades))
        self.app.add_handler(CommandHandler("pnl", self.cmd_pnl))
        self.app.add_handler(CommandHandler("alerts", self.cmd_alerts))
        self.app.add_handler(CommandHandler("subscribe", self.cmd_subscribe))
        self.app.add_handler(CommandHandler("unsubscribe", self.cmd_unsubscribe))

        # Handle unauthorized access
        self.app.add_handler(MessageHandler(filters.ALL, self.handle_unauthorized))

    def _check_auth(self, update: Update) -> bool:
        """Check if user is authorized"""
        user_id = update.effective_user.id
        return TelegramConfig.is_user_allowed(user_id)

    async def cmd_start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /start command"""
        if not self._check_auth(update):
            await update.message.reply_text("❌ Unauthorized access")
            return

        message = "🤖 *Trading Bot Monitor*\n\n"
        message += "Welcome! I'll help you monitor your trading bot.\n\n"
        message += "Available commands:\n"
        message += "/status - Bot status\n"
        message += "/balance - Account balance\n"
        message += "/positions - Current positions\n"
        message += "/trades - Recent trades\n"
        message += "/pnl - P&L summary\n"
        message += "/alerts - Recent alerts\n"
        message += "/subscribe - Enable notifications\n"
        message += "/unsubscribe - Disable notifications\n"
        message += "/help - Show this help\n"

        await update.message.reply_text(message, parse_mode='Markdown')

    async def cmd_help(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /help command"""
        if not self._check_auth(update):
            return

        await self.cmd_start(update, context)

    async def cmd_status(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /status command"""
        if not self._check_auth(update):
            return

        system_metrics = self.metrics.get_system_metrics(0)

        uptime_hours = system_metrics.uptime_seconds / 3600
        message = "🤖 *Bot Status*\n\n"
        message += f"✅ Running\n"
        message += f"⏱️ Uptime: `{uptime_hours:.2f}` hours\n"
        message += f"📊 Total Trades: `{system_metrics.total_trades}`\n"
        message += f"🎯 Win Rate: `{system_metrics.win_rate:.2f}%`\n"
        message += f"💰 Total P&L: `${system_metrics.total_pnl:.2f}`\n"
        message += f"📈 Daily P&L: `${system_metrics.daily_pnl:.2f}`\n"

        await update.message.reply_text(message, parse_mode='Markdown')

    async def cmd_balance(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /balance command"""
        if not self._check_auth(update):
            return

        # Placeholder - integrate with actual exchange balance
        balance = {"USDT": 1000.0, "BTC": 0.05}
        message = self.notifier.format_balance(balance)

        await update.message.reply_text(message, parse_mode='Markdown')

    async def cmd_positions(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /positions command"""
        if not self._check_auth(update):
            return

        # Placeholder - integrate with actual position tracking
        positions = []
        message = self.notifier.format_positions(positions)

        await update.message.reply_text(message, parse_mode='Markdown')

    async def cmd_trades(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /trades command"""
        if not self._check_auth(update):
            return

        trades = [
            {
                'symbol': t.symbol,
                'side': t.side,
                'amount': t.amount,
                'price': t.price,
                'pnl': t.pnl,
                'timestamp': t.timestamp
            }
            for t in self.metrics.trades
        ]

        message = self.notifier.format_trades(trades)
        await update.message.reply_text(message, parse_mode='Markdown')

    async def cmd_pnl(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /pnl command"""
        if not self._check_auth(update):
            return

        system_metrics = self.metrics.get_system_metrics(0)
        profit_factor = self.metrics.get_profit_factor()

        message = self.notifier.format_pnl_summary(
            system_metrics.total_pnl,
            system_metrics.daily_pnl,
            system_metrics.win_rate,
            profit_factor
        )

        await update.message.reply_text(message, parse_mode='Markdown')

    async def cmd_alerts(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /alerts command"""
        if not self._check_auth(update):
            return

        alerts = self.alerting.get_recent_alerts(10)
        message = self.notifier.format_alerts(alerts)

        await update.message.reply_text(message, parse_mode='Markdown')

    async def cmd_subscribe(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /subscribe command"""
        if not self._check_auth(update):
            return

        user_id = update.effective_user.id
        self.notifier.add_subscriber(user_id)

        message = "✅ *Subscribed to notifications*\n\n"
        message += "You will receive:\n"
        message += "• Trade executions\n"
        message += "• Position closures\n"
        message += "• Profit milestones\n"
        message += "• System alerts\n"

        await update.message.reply_text(message, parse_mode='Markdown')

    async def cmd_unsubscribe(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /unsubscribe command"""
        if not self._check_auth(update):
            return

        user_id = update.effective_user.id
        self.notifier.remove_subscriber(user_id)

        message = "✅ *Unsubscribed from notifications*\n\n"
        message += "You will no longer receive automated notifications."

        await update.message.reply_text(message, parse_mode='Markdown')

    async def handle_unauthorized(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle unauthorized access attempts"""
        if not self._check_auth(update):
            user_id = update.effective_user.id
            username = update.effective_user.username or "Unknown"
            self.logger.warning(f"Unauthorized access attempt: {user_id} ({username})")
            await update.message.reply_text("❌ Unauthorized access")

    def run(self):
        """Start the bot"""
        self.logger.info("Starting Telegram bot...")
        self.app.run_polling(allowed_updates=Update.ALL_TYPES)

    async def start_async(self):
        """Start bot asynchronously"""
        await self.app.initialize()
        await self.app.start()
        await self.app.updater.start_polling()

    async def stop_async(self):
        """Stop bot asynchronously"""
        await self.app.updater.stop()
        await self.app.stop()
        await self.app.shutdown()


def create_bot(metrics_tracker: MetricsTracker,
               alerting_system: AlertingSystem,
               logger: Optional[logging.Logger] = None) -> TradingTelegramBot:
    """Factory function to create bot instance"""
    if logger is None:
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        logger = logging.getLogger(__name__)

    return TradingTelegramBot(metrics_tracker, alerting_system, logger)


if __name__ == "__main__":
    # Example usage
    logger = logging.getLogger(__name__)
    logging.basicConfig(level=logging.INFO)

    metrics = MetricsTracker()
    alerting = AlertingSystem(logger)

    bot = create_bot(metrics, alerting, logger)
    bot.run()
