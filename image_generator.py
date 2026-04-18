"""
Image Generator for Trading Posts
Creates visual content including charts and P&L summaries
"""

import matplotlib
matplotlib.use('Agg')  # Non-interactive backend
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import io
from PIL import Image, ImageDraw, ImageFont
import os


class ImageGenerator:
    """Generate images for trading posts"""

    def __init__(self, output_dir: str = "./post_images"):
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)

        # Color scheme
        self.profit_color = '#00C853'
        self.loss_color = '#FF1744'
        self.bg_color = '#1E1E1E'
        self.text_color = '#FFFFFF'
        self.grid_color = '#333333'

    def generate_trade_card(self, trade_data: Dict) -> str:
        """
        Generate a visual card for a single trade

        Args:
            trade_data: Trade information

        Returns:
            Path to generated image
        """
        width, height = 800, 600
        img = Image.new('RGB', (width, height), self.bg_color)
        draw = ImageDraw.Draw(img)

        try:
            title_font = ImageFont.truetype("arial.ttf", 48)
            label_font = ImageFont.truetype("arial.ttf", 32)
            value_font = ImageFont.truetype("arialbd.ttf", 40)
        except:
            title_font = ImageFont.load_default()
            label_font = ImageFont.load_default()
            value_font = ImageFont.load_default()

        symbol = trade_data['symbol'].replace('/USDT', '')
        profit_pct = trade_data['profit_pct']
        is_profit = profit_pct > 0

        # Title
        draw.text((50, 50), f"{symbol} Trade", fill=self.text_color, font=title_font)

        # Profit/Loss indicator
        pnl_color = self.profit_color if is_profit else self.loss_color
        pnl_text = f"{profit_pct:+.2f}%"
        draw.text((50, 150), pnl_text, fill=pnl_color, font=value_font)

        # Trade details
        y_pos = 250
        details = [
            ("Entry", f"${trade_data['entry_price']:.4f}"),
            ("Exit", f"${trade_data['exit_price']:.4f}"),
            ("Amount", f"{trade_data.get('amount', 0):.4f}")
        ]

        for label, value in details:
            draw.text((50, y_pos), label, fill=self.text_color, font=label_font)
            draw.text((300, y_pos), value, fill=self.text_color, font=value_font)
            y_pos += 80

        # Timestamp
        timestamp = trade_data.get('timestamp', datetime.now())
        if isinstance(timestamp, str):
            timestamp_str = timestamp
        else:
            timestamp_str = timestamp.strftime("%Y-%m-%d %H:%M")
        draw.text((50, height - 60), timestamp_str, fill=self.grid_color, font=label_font)

        filename = f"trade_{symbol}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
        filepath = os.path.join(self.output_dir, filename)
        img.save(filepath)

        return filepath

    def generate_pnl_chart(self, trades: List[Dict], title: str = "P&L History") -> str:
        """
        Generate a line chart showing cumulative P&L

        Args:
            trades: List of trade dictionaries with timestamp and profit_pct
            title: Chart title

        Returns:
            Path to generated image
        """
        fig, ax = plt.subplots(figsize=(12, 6), facecolor=self.bg_color)
        ax.set_facecolor(self.bg_color)

        if not trades:
            # Empty chart
            ax.text(0.5, 0.5, 'No trades yet', ha='center', va='center',
                   color=self.text_color, fontsize=20)
        else:
            # Calculate cumulative P&L
            timestamps = [t.get('timestamp', datetime.now()) for t in trades]
            profits = [t['profit_pct'] for t in trades]
            cumulative_pnl = []
            total = 0
            for p in profits:
                total += p
                cumulative_pnl.append(total)

            # Plot
            color = self.profit_color if cumulative_pnl[-1] >= 0 else self.loss_color
            ax.plot(timestamps, cumulative_pnl, color=color, linewidth=2, marker='o')
            ax.axhline(y=0, color=self.grid_color, linestyle='--', linewidth=1)

            # Formatting
            ax.set_xlabel('Date', color=self.text_color, fontsize=12)
            ax.set_ylabel('Cumulative P&L (%)', color=self.text_color, fontsize=12)
            ax.set_title(title, color=self.text_color, fontsize=16, pad=20)

            ax.tick_params(colors=self.text_color)
            ax.grid(True, color=self.grid_color, alpha=0.3)
            ax.spines['bottom'].set_color(self.text_color)
            ax.spines['top'].set_color(self.text_color)
            ax.spines['left'].set_color(self.text_color)
            ax.spines['right'].set_color(self.text_color)

            # Format x-axis dates
            ax.xaxis.set_major_formatter(mdates.DateFormatter('%m/%d'))
            plt.xticks(rotation=45)

        plt.tight_layout()

        filename = f"pnl_chart_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
        filepath = os.path.join(self.output_dir, filename)
        plt.savefig(filepath, facecolor=self.bg_color, dpi=150)
        plt.close()

        return filepath

    def generate_summary_card(self, summary_data: Dict, period: str = "Daily") -> str:
        """
        Generate a summary card with key metrics

        Args:
            summary_data: Summary statistics
            period: "Daily" or "Weekly"

        Returns:
            Path to generated image
        """
        width, height = 800, 600
        img = Image.new('RGB', (width, height), self.bg_color)
        draw = ImageDraw.Draw(img)

        try:
            title_font = ImageFont.truetype("arial.ttf", 44)
            metric_font = ImageFont.truetype("arialbd.ttf", 36)
            label_font = ImageFont.truetype("arial.ttf", 28)
        except:
            title_font = ImageFont.load_default()
            metric_font = ImageFont.load_default()
            label_font = ImageFont.load_default()

        # Title
        date_str = summary_data.get('date', datetime.now().strftime('%Y-%m-%d'))
        draw.text((50, 40), f"{period} Summary", fill=self.text_color, font=title_font)
        draw.text((50, 100), date_str, fill=self.grid_color, font=label_font)

        # Metrics
        total_trades = summary_data.get('total_trades', 0)
        wins = summary_data.get('winning_trades', 0)
        profit = summary_data.get('total_profit_pct', 0)
        win_rate = (wins / total_trades * 100) if total_trades > 0 else 0

        metrics = [
            ("Total Trades", str(total_trades), self.text_color),
            ("Win Rate", f"{win_rate:.1f}%", self.profit_color if win_rate >= 50 else self.loss_color),
            ("Total P&L", f"{profit:+.2f}%", self.profit_color if profit >= 0 else self.loss_color)
        ]

        y_pos = 200
        for label, value, color in metrics:
            draw.text((50, y_pos), label, fill=self.text_color, font=label_font)
            draw.text((50, y_pos + 40), value, fill=color, font=metric_font)
            y_pos += 120

        filename = f"summary_{period.lower()}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
        filepath = os.path.join(self.output_dir, filename)
        img.save(filepath)

        return filepath
