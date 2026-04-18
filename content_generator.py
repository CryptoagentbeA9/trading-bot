"""
Content Generator for Trading Posts
Generates engaging social media content from trade data
"""

import random
from typing import Dict, List
from datetime import datetime


class ContentGenerator:
    """Generate formatted content for trading updates"""

    def __init__(self, use_emojis: bool = True):
        self.use_emojis = use_emojis

        self.profit_emojis = ["🚀", "💰", "📈", "✅", "🎯", "💪", "🔥"]
        self.loss_emojis = ["📉", "⚠️", "🔴"]

        self.opening_phrases = [
            "Just closed a trade",
            "Trade update",
            "Position closed",
            "Latest trade result",
            "Trade execution complete"
        ]

        self.profit_phrases = [
            "Solid profit secured",
            "Green candles all the way",
            "Another win in the books",
            "Profitable exit",
            "Target hit successfully"
        ]

    def generate_trade_post(self, trade_data: Dict) -> str:
        """
        Generate a post for a single trade

        Args:
            trade_data: Dict with keys: symbol, entry_price, exit_price,
                       profit_pct, amount, timestamp

        Returns:
            Formatted post text
        """
        symbol = trade_data['symbol'].replace('/USDT', '')
        entry = trade_data['entry_price']
        exit_price = trade_data['exit_price']
        profit_pct = trade_data['profit_pct']

        is_profit = profit_pct > 0
        emoji = random.choice(self.profit_emojis if is_profit else self.loss_emojis) if self.use_emojis else ""

        opening = random.choice(self.opening_phrases)

        lines = []
        lines.append(f"{emoji} {opening}!" if emoji else f"{opening}!")
        lines.append("")
        lines.append(f"Symbol: #{symbol}")
        lines.append(f"Entry: ${entry:.4f}")
        lines.append(f"Exit: ${exit_price:.4f}")
        lines.append(f"Profit: {profit_pct:+.2f}%")

        if is_profit and profit_pct > 5:
            lines.append("")
            lines.append(random.choice(self.profit_phrases) + ("! " + random.choice(self.profit_emojis) if self.use_emojis else "!"))

        lines.append("")
        lines.append("#crypto #trading #binance")

        return "\n".join(lines)

    def generate_daily_summary(self, summary_data: Dict) -> str:
        """
        Generate daily performance summary

        Args:
            summary_data: Dict with keys: date, total_trades, winning_trades,
                         total_profit_pct, best_trade, worst_trade

        Returns:
            Formatted summary post
        """
        date = summary_data['date']
        total = summary_data['total_trades']
        wins = summary_data['winning_trades']
        profit = summary_data['total_profit_pct']

        win_rate = (wins / total * 100) if total > 0 else 0

        emoji = "📊" if self.use_emojis else ""
        profit_emoji = "💰" if profit > 0 and self.use_emojis else ""

        lines = []
        lines.append(f"{emoji} Daily Trading Summary - {date}")
        lines.append("")
        lines.append(f"Total Trades: {total}")
        lines.append(f"Winning Trades: {wins}")
        lines.append(f"Win Rate: {win_rate:.1f}%")
        lines.append(f"Total P&L: {profit:+.2f}% {profit_emoji}")

        if 'best_trade' in summary_data:
            best = summary_data['best_trade']
            lines.append("")
            lines.append(f"Best Trade: {best['symbol']} ({best['profit_pct']:+.2f}%)")

        lines.append("")
        lines.append("#cryptotrading #daytrading #tradingsummary")

        return "\n".join(lines)

    def generate_weekly_summary(self, summary_data: Dict) -> str:
        """Generate weekly performance summary"""
        week = summary_data['week']
        total = summary_data['total_trades']
        wins = summary_data['winning_trades']
        profit = summary_data['total_profit_pct']

        win_rate = (wins / total * 100) if total > 0 else 0

        emoji = "📈" if self.use_emojis else ""

        lines = []
        lines.append(f"{emoji} Weekly Trading Report - Week {week}")
        lines.append("")
        lines.append(f"Trades Executed: {total}")
        lines.append(f"Success Rate: {win_rate:.1f}%")
        lines.append(f"Weekly Return: {profit:+.2f}%")

        if 'top_performers' in summary_data:
            lines.append("")
            lines.append("Top Performers:")
            for i, trade in enumerate(summary_data['top_performers'][:3], 1):
                lines.append(f"{i}. {trade['symbol']}: {trade['profit_pct']:+.2f}%")

        lines.append("")
        lines.append("#weeklyreport #cryptotrading #tradingbot")

        return "\n".join(lines)
