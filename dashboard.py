"""
Web Dashboard for Trading Bot Monitoring
Real-time monitoring dashboard using Flask
"""

from flask import Flask, render_template, jsonify, request
from flask_cors import CORS
import json
from datetime import datetime
from typing import Dict, Optional
import threading
import time


class TradingDashboard:
    """Web dashboard for monitoring trading bot"""

    def __init__(self, metrics_tracker, alerting_system, strategy_engine, port: int = 5000):
        self.app = Flask(__name__)
        CORS(self.app)

        self.metrics_tracker = metrics_tracker
        self.alerting_system = alerting_system
        self.strategy_engine = strategy_engine
        self.port = port

        self._setup_routes()

    def _setup_routes(self):
        """Setup Flask routes"""

        @self.app.route('/')
        def index():
            """Main dashboard page"""
            return render_template('dashboard.html')

        @self.app.route('/api/status')
        def get_status():
            """Get bot status"""
            uptime = time.time() - self.metrics_tracker.start_time
            hours = int(uptime // 3600)
            minutes = int((uptime % 3600) // 60)

            return jsonify({
                'status': 'running',
                'uptime': f"{hours}h {minutes}m",
                'timestamp': datetime.utcnow().isoformat()
            })

        @self.app.route('/api/metrics')
        def get_metrics():
            """Get current metrics"""
            active_positions = len(self.strategy_engine.positions)
            system_metrics = self.metrics_tracker.get_system_metrics(active_positions)

            return jsonify({
                'total_trades': system_metrics.total_trades,
                'win_rate': f"{system_metrics.win_rate:.2f}%",
                'total_pnl': f"${system_metrics.total_pnl:.2f}",
                'daily_pnl': f"${system_metrics.daily_pnl:.2f}",
                'active_positions': system_metrics.active_positions,
                'uptime_seconds': system_metrics.uptime_seconds
            })

        @self.app.route('/api/performance')
        def get_performance():
            """Get performance summary"""
            return jsonify({
                'daily': self.metrics_tracker.get_daily_summary(),
                'weekly': self.metrics_tracker.get_weekly_summary(),
                'monthly': self.metrics_tracker.get_monthly_summary(),
                'profit_factor': self.metrics_tracker.get_profit_factor()
            })

        @self.app.route('/api/positions')
        def get_positions():
            """Get open positions"""
            positions = self.strategy_engine.get_open_positions()
            return jsonify({'positions': positions})

        @self.app.route('/api/trades')
        def get_trades():
            """Get recent trades"""
            limit = request.args.get('limit', 20, type=int)
            recent_trades = self.metrics_tracker.trades[-limit:]

            trades_data = []
            for trade in recent_trades:
                trades_data.append({
                    'symbol': trade.symbol,
                    'side': trade.side,
                    'amount': trade.amount,
                    'price': f"${trade.price:.4f}",
                    'pnl': f"${trade.pnl:.2f}" if trade.pnl else "N/A",
                    'pnl_percentage': f"{trade.pnl_percentage:.2f}%" if trade.pnl_percentage else "N/A",
                    'timestamp': trade.timestamp
                })

            return jsonify({'trades': trades_data})

        @self.app.route('/api/alerts')
        def get_alerts():
            """Get recent alerts"""
            limit = request.args.get('limit', 50, type=int)
            alerts = self.alerting_system.get_recent_alerts(limit)

            alerts_data = []
            for alert in alerts:
                alerts_data.append({
                    'level': alert.level.value,
                    'title': alert.title,
                    'message': alert.message,
                    'timestamp': alert.timestamp,
                    'metadata': alert.metadata
                })

            return jsonify({'alerts': alerts_data})

        @self.app.route('/api/api-health')
        def get_api_health():
            """Get API health metrics"""
            health = self.metrics_tracker.get_api_health()
            return jsonify({'api_health': health})

        @self.app.route('/api/export')
        def export_metrics():
            """Export all metrics"""
            return jsonify(self.metrics_tracker.export_metrics())

    def run(self, debug: bool = False):
        """Run the dashboard server"""
        self.app.run(host='0.0.0.0', port=self.port, debug=debug, use_reloader=False)

    def run_background(self):
        """Run dashboard in background thread"""
        thread = threading.Thread(target=self.run, daemon=True)
        thread.start()
        return thread


def create_dashboard_html():
    """Create HTML template for dashboard"""
    html_content = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Trading Bot Dashboard</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: #0f172a;
            color: #e2e8f0;
            padding: 20px;
        }
        .container { max-width: 1400px; margin: 0 auto; }
        h1 { margin-bottom: 30px; color: #60a5fa; }
        .grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 20px; margin-bottom: 30px; }
        .card {
            background: #1e293b;
            border-radius: 8px;
            padding: 20px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.3);
        }
        .card h2 { color: #94a3b8; font-size: 14px; margin-bottom: 10px; text-transform: uppercase; }
        .metric { font-size: 32px; font-weight: bold; color: #60a5fa; }
        .positive { color: #10b981; }
        .negative { color: #ef4444; }
        .status-badge {
            display: inline-block;
            padding: 4px 12px;
            border-radius: 12px;
            font-size: 12px;
            font-weight: 600;
        }
        .status-running { background: #10b981; color: white; }
        table { width: 100%; border-collapse: collapse; margin-top: 10px; }
        th, td { padding: 12px; text-align: left; border-bottom: 1px solid #334155; }
        th { color: #94a3b8; font-weight: 600; font-size: 12px; text-transform: uppercase; }
        .alert { padding: 12px; margin: 8px 0; border-radius: 6px; font-size: 14px; }
        .alert-critical { background: #7f1d1d; border-left: 4px solid #ef4444; }
        .alert-warning { background: #78350f; border-left: 4px solid #f59e0b; }
        .alert-info { background: #1e3a8a; border-left: 4px solid #3b82f6; }
        .refresh-btn {
            background: #3b82f6;
            color: white;
            border: none;
            padding: 10px 20px;
            border-radius: 6px;
            cursor: pointer;
            font-size: 14px;
            margin-bottom: 20px;
        }
        .refresh-btn:hover { background: #2563eb; }
    </style>
</head>
<body>
    <div class="container">
        <h1>Trading Bot Dashboard</h1>

        <button class="refresh-btn" onclick="refreshData()">Refresh Data</button>

        <div class="grid">
            <div class="card">
                <h2>Bot Status</h2>
                <div class="metric">
                    <span class="status-badge status-running" id="status">RUNNING</span>
                </div>
                <p style="margin-top: 10px; color: #94a3b8;">Uptime: <span id="uptime">-</span></p>
            </div>

            <div class="card">
                <h2>Total Trades</h2>
                <div class="metric" id="total-trades">0</div>
            </div>

            <div class="card">
                <h2>Win Rate</h2>
                <div class="metric" id="win-rate">0%</div>
            </div>

            <div class="card">
                <h2>Total P&L</h2>
                <div class="metric" id="total-pnl">$0.00</div>
            </div>

            <div class="card">
                <h2>Daily P&L</h2>
                <div class="metric" id="daily-pnl">$0.00</div>
            </div>

            <div class="card">
                <h2>Active Positions</h2>
                <div class="metric" id="active-positions">0</div>
            </div>
        </div>

        <div class="card" style="margin-bottom: 20px;">
            <h2>Open Positions</h2>
            <div id="positions-table"></div>
        </div>

        <div class="card" style="margin-bottom: 20px;">
            <h2>Recent Trades</h2>
            <div id="trades-table"></div>
        </div>

        <div class="card">
            <h2>Alerts</h2>
            <div id="alerts-list"></div>
        </div>
    </div>

    <script>
        async function fetchData(endpoint) {
            const response = await fetch(`/api/${endpoint}`);
            return await response.json();
        }

        async function updateDashboard() {
            try {
                const [status, metrics, positions, trades, alerts] = await Promise.all([
                    fetchData('status'),
                    fetchData('metrics'),
                    fetchData('positions'),
                    fetchData('trades?limit=10'),
                    fetchData('alerts?limit=10')
                ]);

                document.getElementById('status').textContent = status.status.toUpperCase();
                document.getElementById('uptime').textContent = status.uptime;
                document.getElementById('total-trades').textContent = metrics.total_trades;
                document.getElementById('win-rate').textContent = metrics.win_rate;

                const totalPnl = parseFloat(metrics.total_pnl.replace('$', ''));
                const totalPnlEl = document.getElementById('total-pnl');
                totalPnlEl.textContent = metrics.total_pnl;
                totalPnlEl.className = 'metric ' + (totalPnl >= 0 ? 'positive' : 'negative');

                const dailyPnl = parseFloat(metrics.daily_pnl.replace('$', ''));
                const dailyPnlEl = document.getElementById('daily-pnl');
                dailyPnlEl.textContent = metrics.daily_pnl;
                dailyPnlEl.className = 'metric ' + (dailyPnl >= 0 ? 'positive' : 'negative');

                document.getElementById('active-positions').textContent = metrics.active_positions;

                updatePositionsTable(positions.positions);
                updateTradesTable(trades.trades);
                updateAlertsList(alerts.alerts);
            } catch (error) {
                console.error('Error updating dashboard:', error);
            }
        }

        function updatePositionsTable(positions) {
            const container = document.getElementById('positions-table');
            if (positions.length === 0) {
                container.innerHTML = '<p style="color: #94a3b8;">No open positions</p>';
                return;
            }

            let html = '<table><thead><tr><th>Symbol</th><th>Entry</th><th>Current</th><th>Amount</th><th>P&L</th><th>Stop Loss</th><th>Take Profit</th></tr></thead><tbody>';
            positions.forEach(pos => {
                html += `<tr>
                    <td>${pos.symbol}</td>
                    <td>${pos.entry_price}</td>
                    <td>${pos.current_price}</td>
                    <td>${pos.amount.toFixed(4)}</td>
                    <td>${pos.unrealized_pnl} (${pos.unrealized_pnl_pct})</td>
                    <td>${pos.stop_loss}</td>
                    <td>${pos.take_profit}</td>
                </tr>`;
            });
            html += '</tbody></table>';
            container.innerHTML = html;
        }

        function updateTradesTable(trades) {
            const container = document.getElementById('trades-table');
            if (trades.length === 0) {
                container.innerHTML = '<p style="color: #94a3b8;">No recent trades</p>';
                return;
            }

            let html = '<table><thead><tr><th>Symbol</th><th>Side</th><th>Price</th><th>Amount</th><th>P&L</th><th>Time</th></tr></thead><tbody>';
            trades.forEach(trade => {
                html += `<tr>
                    <td>${trade.symbol}</td>
                    <td>${trade.side}</td>
                    <td>${trade.price}</td>
                    <td>${trade.amount.toFixed(4)}</td>
                    <td>${trade.pnl}</td>
                    <td>${new Date(trade.timestamp).toLocaleString()}</td>
                </tr>`;
            });
            html += '</tbody></table>';
            container.innerHTML = html;
        }

        function updateAlertsList(alerts) {
            const container = document.getElementById('alerts-list');
            if (alerts.length === 0) {
                container.innerHTML = '<p style="color: #94a3b8;">No alerts</p>';
                return;
            }

            let html = '';
            alerts.forEach(alert => {
                html += `<div class="alert alert-${alert.level}">
                    <strong>${alert.title}</strong><br>
                    ${alert.message}<br>
                    <small>${new Date(alert.timestamp).toLocaleString()}</small>
                </div>`;
            });
            container.innerHTML = html;
        }

        function refreshData() {
            updateDashboard();
        }

        updateDashboard();
        setInterval(updateDashboard, 5000);
    </script>
</body>
</html>"""
    return html_content
