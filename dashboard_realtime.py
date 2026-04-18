"""
Real-time Web Dashboard with WebSocket Support
Enhanced monitoring dashboard with live updates, charts, and mobile support
"""

from flask import Flask, render_template, jsonify
from flask_socketio import SocketIO, emit
from flask_cors import CORS
import json
import time
import threading
from datetime import datetime
from typing import Dict, Optional
from pathlib import Path


class RealtimeDashboard:
    """Enhanced real-time dashboard with WebSocket support"""

    def __init__(self, metrics_tracker, alerting_system, strategy_engine,
                 binance_client, port: int = 5000):
        self.app = Flask(__name__)
        self.app.config['SECRET_KEY'] = 'trading-bot-secret'
        CORS(self.app)
        self.socketio = SocketIO(self.app, cors_allowed_origins="*")

        self.metrics_tracker = metrics_tracker
        self.alerting_system = alerting_system
        self.strategy_engine = strategy_engine
        self.binance_client = binance_client
        self.port = port

        self.is_running = False
        self.update_thread = None

        self._setup_routes()
        self._setup_socketio()

    def _setup_routes(self):
        """Setup Flask routes"""

        @self.app.route('/')
        def index():
            """Main dashboard page"""
            html_path = Path(__file__).parent / 'templates' / 'dashboard_realtime.html'
            if html_path.exists():
                return render_template('dashboard_realtime.html')
            return get_dashboard_html()

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
                'total_pnl': system_metrics.total_pnl,
                'daily_pnl': system_metrics.daily_pnl,
                'active_positions': system_metrics.active_positions,
                'uptime_seconds': system_metrics.uptime_seconds
            })

        @self.app.route('/api/balance')
        def get_balance():
            """Get account balance"""
            try:
                balance = self.binance_client.get_balance()
                return jsonify({'balance': balance})
            except Exception as e:
                return jsonify({'error': str(e)}), 500

        @self.app.route('/api/positions')
        def get_positions():
            """Get open positions"""
            positions = self.strategy_engine.get_open_positions()
            return jsonify({'positions': positions})

        @self.app.route('/api/trades')
        def get_trades():
            """Get recent trades"""
            limit = 20
            recent_trades = self.metrics_tracker.trades[-limit:]
            trades_data = [{
                'symbol': t.symbol,
                'side': t.side,
                'amount': t.amount,
                'price': t.price,
                'pnl': t.pnl,
                'pnl_percentage': t.pnl_percentage,
                'timestamp': t.timestamp
            } for t in recent_trades]
            return jsonify({'trades': trades_data})

        @self.app.route('/api/alerts')
        def get_alerts():
            """Get recent alerts"""
            alerts = self.alerting_system.get_recent_alerts(50)
            alerts_data = [{
                'level': a.level.value,
                'title': a.title,
                'message': a.message,
                'timestamp': a.timestamp
            } for a in alerts]
            return jsonify({'alerts': alerts_data})

        @self.app.route('/api/gainers')
        def get_gainers():
            """Get current top gainers being monitored"""
            try:
                gainers = self.binance_client.get_top_gainers(limit=10)
                return jsonify({'gainers': gainers})
            except Exception as e:
                return jsonify({'error': str(e)}), 500

        @self.app.route('/api/chart-data')
        def get_chart_data():
            """Get data for charts"""
            trades = self.metrics_tracker.trades[-50:]
            pnl_data = []
            cumulative_pnl = 0

            for trade in trades:
                if trade.pnl:
                    cumulative_pnl += trade.pnl
                    pnl_data.append({
                        'timestamp': trade.timestamp,
                        'pnl': trade.pnl,
                        'cumulative': cumulative_pnl
                    })

            return jsonify({'pnl_history': pnl_data})

    def _setup_socketio(self):
        """Setup WebSocket event handlers"""

        @self.socketio.on('connect')
        def handle_connect():
            """Handle client connection"""
            print(f"Client connected: {datetime.utcnow().isoformat()}")
            emit('connection_response', {'status': 'connected'})

        @self.socketio.on('disconnect')
        def handle_disconnect():
            """Handle client disconnection"""
            print(f"Client disconnected: {datetime.utcnow().isoformat()}")

        @self.socketio.on('request_update')
        def handle_update_request():
            """Handle manual update request"""
            self._broadcast_updates()

    def _broadcast_updates(self):
        """Broadcast real-time updates to all connected clients"""
        try:
            active_positions = len(self.strategy_engine.positions)
            system_metrics = self.metrics_tracker.get_system_metrics(active_positions)

            uptime = time.time() - self.metrics_tracker.start_time
            hours = int(uptime // 3600)
            minutes = int((uptime % 3600) // 60)

            balance = None
            try:
                balance = self.binance_client.get_balance()
            except:
                pass

            positions = self.strategy_engine.get_open_positions()

            recent_trades = self.metrics_tracker.trades[-10:]
            trades_data = [{
                'symbol': t.symbol,
                'side': t.side,
                'amount': t.amount,
                'price': t.price,
                'pnl': t.pnl,
                'pnl_percentage': t.pnl_percentage,
                'timestamp': t.timestamp
            } for t in recent_trades]

            alerts = self.alerting_system.get_recent_alerts(10)
            alerts_data = [{
                'level': a.level.value,
                'title': a.title,
                'message': a.message,
                'timestamp': a.timestamp
            } for a in alerts]

            gainers = []
            try:
                gainers = self.binance_client.get_top_gainers(limit=10)
            except:
                pass

            update_data = {
                'timestamp': datetime.utcnow().isoformat(),
                'status': {
                    'status': 'running',
                    'uptime': f"{hours}h {minutes}m"
                },
                'metrics': {
                    'total_trades': system_metrics.total_trades,
                    'win_rate': system_metrics.win_rate,
                    'total_pnl': system_metrics.total_pnl,
                    'daily_pnl': system_metrics.daily_pnl,
                    'active_positions': system_metrics.active_positions
                },
                'balance': balance,
                'positions': positions,
                'trades': trades_data,
                'alerts': alerts_data,
                'gainers': gainers
            }

            self.socketio.emit('dashboard_update', update_data)

        except Exception as e:
            print(f"Error broadcasting updates: {e}")

    def _update_loop(self):
        """Background thread for periodic updates"""
        while self.is_running:
            self._broadcast_updates()
            time.sleep(2)

    def run(self, debug: bool = False):
        """Run the dashboard server"""
        self.is_running = True
        self.update_thread = threading.Thread(target=self._update_loop, daemon=True)
        self.update_thread.start()
        print(f"Dashboard running on http://0.0.0.0:{self.port}")
        self.socketio.run(self.app, host='0.0.0.0', port=self.port, debug=debug, allow_unsafe_werkzeug=True)

    def stop(self):
        """Stop the dashboard"""
        self.is_running = False
        if self.update_thread:
            self.update_thread.join(timeout=5)


def get_dashboard_html():
    """Generate enhanced HTML dashboard with charts and WebSocket"""
    return """<!DOCTYPE html>
<html lang="zh-TW">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>交易機器人即時監控</title>
    <script src="https://cdn.socket.io/4.5.4/socket.io.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.min.js"></script>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Microsoft JhengHei', sans-serif;
            background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);
            color: #e2e8f0;
            padding: 15px;
            min-height: 100vh;
        }
        .container { max-width: 1600px; margin: 0 auto; }
        .header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 25px;
            flex-wrap: wrap;
            gap: 15px;
        }
        h1 { color: #60a5fa; font-size: 28px; }
        .connection-status {
            display: flex;
            align-items: center;
            gap: 8px;
            padding: 8px 16px;
            background: #1e293b;
            border-radius: 20px;
            font-size: 14px;
        }
        .status-dot {
            width: 10px;
            height: 10px;
            border-radius: 50%;
            background: #10b981;
            animation: pulse 2s infinite;
        }
        @keyframes pulse {
            0%, 100% { opacity: 1; }
            50% { opacity: 0.5; }
        }
        .grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
            gap: 15px;
            margin-bottom: 20px;
        }
        .card {
            background: rgba(30, 41, 59, 0.8);
            backdrop-filter: blur(10px);
            border-radius: 12px;
            padding: 20px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.3);
            border: 1px solid rgba(148, 163, 184, 0.1);
            transition: transform 0.2s;
        }
        .card:hover { transform: translateY(-2px); }
        .card h2 {
            color: #94a3b8;
            font-size: 13px;
            margin-bottom: 12px;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }
        .metric {
            font-size: 32px;
            font-weight: bold;
            color: #60a5fa;
            line-height: 1.2;
        }
        .metric-small { font-size: 24px; }
        .positive { color: #10b981; }
        .negative { color: #ef4444; }
        .neutral { color: #94a3b8; }
        .sub-metric {
            font-size: 14px;
            color: #94a3b8;
            margin-top: 8px;
        }
        .status-badge {
            display: inline-block;
            padding: 6px 14px;
            border-radius: 16px;
            font-size: 13px;
            font-weight: 600;
            background: #10b981;
            color: white;
        }
        .chart-container {
            position: relative;
            height: 300px;
            margin-top: 15px;
        }
        table {
            width: 100%;
            border-collapse: collapse;
            margin-top: 12px;
            font-size: 14px;
        }
        th, td {
            padding: 12px 8px;
            text-align: left;
            border-bottom: 1px solid rgba(51, 65, 85, 0.5);
        }
        th {
            color: #94a3b8;
            font-weight: 600;
            font-size: 12px;
            text-transform: uppercase;
        }
        td { color: #e2e8f0; }
        .alert {
            padding: 12px;
            margin: 8px 0;
            border-radius: 8px;
            font-size: 13px;
            border-left: 4px solid;
        }
        .alert-critical {
            background: rgba(127, 29, 29, 0.3);
            border-color: #ef4444;
        }
        .alert-warning {
            background: rgba(120, 53, 15, 0.3);
            border-color: #f59e0b;
        }
        .alert-info {
            background: rgba(30, 58, 138, 0.3);
            border-color: #3b82f6;
        }
        .wide-card {
            grid-column: 1 / -1;
        }
        @media (max-width: 768px) {
            .grid { grid-template-columns: 1fr; }
            h1 { font-size: 22px; }
            .metric { font-size: 26px; }
            .chart-container { height: 250px; }
        }
        .loading {
            text-align: center;
            padding: 40px;
            color: #94a3b8;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🤖 交易機器人即時監控</h1>
            <div class="connection-status">
                <div class="status-dot" id="status-dot"></div>
                <span id="connection-text">連接中...</span>
            </div>
        </div>

        <div class="grid">
            <div class="card">
                <h2>機器人狀態</h2>
                <div class="metric">
                    <span class="status-badge" id="bot-status">運行中</span>
                </div>
                <div class="sub-metric">運行時間: <span id="uptime">-</span></div>
            </div>

            <div class="card">
                <h2>帳戶餘額</h2>
                <div class="metric metric-small" id="balance">$0.00</div>
                <div class="sub-metric">USDT</div>
            </div>

            <div class="card">
                <h2>總交易次數</h2>
                <div class="metric" id="total-trades">0</div>
            </div>

            <div class="card">
                <h2>勝率</h2>
                <div class="metric" id="win-rate">0%</div>
            </div>

            <div class="card">
                <h2>總盈虧</h2>
                <div class="metric" id="total-pnl">$0.00</div>
            </div>

            <div class="card">
                <h2>今日盈虧</h2>
                <div class="metric" id="daily-pnl">$0.00</div>
            </div>

            <div class="card">
                <h2>持倉數量</h2>
                <div class="metric" id="active-positions">0</div>
            </div>
        </div>

        <div class="grid">
            <div class="card wide-card">
                <h2>📈 盈虧曲線</h2>
                <div class="chart-container">
                    <canvas id="pnl-chart"></canvas>
                </div>
            </div>
        </div>

        <div class="grid">
            <div class="card wide-card">
                <h2>💼 當前持倉</h2>
                <div id="positions-table" class="loading">載入中...</div>
            </div>
        </div>

        <div class="grid">
            <div class="card wide-card">
                <h2>🔥 監控中的漲幅榜</h2>
                <div id="gainers-table" class="loading">載入中...</div>
            </div>
        </div>

        <div class="grid">
            <div class="card wide-card">
                <h2>📊 最近交易</h2>
                <div id="trades-table" class="loading">載入中...</div>
            </div>
        </div>

        <div class="grid">
            <div class="card wide-card">
                <h2>🔔 系統警報</h2>
                <div id="alerts-list" class="loading">載入中...</div>
            </div>
        </div>
    </div>

    <script>
        const socket = io();
        let pnlChart = null;
        let pnlData = [];

        socket.on('connect', () => {
            document.getElementById('connection-text').textContent = '已連接';
            document.getElementById('status-dot').style.background = '#10b981';
        });

        socket.on('disconnect', () => {
            document.getElementById('connection-text').textContent = '連接中斷';
            document.getElementById('status-dot').style.background = '#ef4444';
        });

        socket.on('dashboard_update', (data) => {
            updateDashboard(data);
        });

        function updateDashboard(data) {
            if (data.status) {
                document.getElementById('uptime').textContent = data.status.uptime;
            }

            if (data.metrics) {
                const m = data.metrics;
                document.getElementById('total-trades').textContent = m.total_trades;
                document.getElementById('win-rate').textContent = m.win_rate.toFixed(2) + '%';

                const totalPnlEl = document.getElementById('total-pnl');
                totalPnlEl.textContent = '$' + m.total_pnl.toFixed(2);
                totalPnlEl.className = 'metric ' + (m.total_pnl >= 0 ? 'positive' : 'negative');

                const dailyPnlEl = document.getElementById('daily-pnl');
                dailyPnlEl.textContent = '$' + m.daily_pnl.toFixed(2);
                dailyPnlEl.className = 'metric ' + (m.daily_pnl >= 0 ? 'positive' : 'negative');

                document.getElementById('active-positions').textContent = m.active_positions;
            }

            if (data.balance) {
                const totalBalance = Object.values(data.balance).reduce((sum, val) => sum + val, 0);
                document.getElementById('balance').textContent = '$' + totalBalance.toFixed(2);
            }

            if (data.positions) {
                updatePositionsTable(data.positions);
            }

            if (data.trades) {
                updateTradesTable(data.trades);
                updatePnlChart(data.trades);
            }

            if (data.alerts) {
                updateAlertsList(data.alerts);
            }

            if (data.gainers) {
                updateGainersTable(data.gainers);
            }
        }

        function updatePositionsTable(positions) {
            const container = document.getElementById('positions-table');
            if (!positions || positions.length === 0) {
                container.innerHTML = '<p class="sub-metric">目前無持倉</p>';
                return;
            }

            let html = '<table><thead><tr><th>幣種</th><th>入場價</th><th>當前價</th><th>數量</th><th>盈虧</th><th>止損</th><th>止盈</th></tr></thead><tbody>';
            positions.forEach(pos => {
                const pnlClass = parseFloat(pos.unrealized_pnl_pct) >= 0 ? 'positive' : 'negative';
                html += `<tr>
                    <td><strong>${pos.symbol}</strong></td>
                    <td>$${pos.entry_price}</td>
                    <td>$${pos.current_price}</td>
                    <td>${pos.amount.toFixed(4)}</td>
                    <td class="${pnlClass}">${pos.unrealized_pnl} (${pos.unrealized_pnl_pct})</td>
                    <td>$${pos.stop_loss}</td>
                    <td>$${pos.take_profit}</td>
                </tr>`;
            });
            html += '</tbody></table>';
            container.innerHTML = html;
        }

        function updateGainersTable(gainers) {
            const container = document.getElementById('gainers-table');
            if (!gainers || gainers.length === 0) {
                container.innerHTML = '<p class="sub-metric">暫無數據</p>';
                return;
            }

            let html = '<table><thead><tr><th>排名</th><th>幣種</th><th>價格</th><th>24h漲幅</th><th>交易量</th></tr></thead><tbody>';
            gainers.forEach((g, i) => {
                html += `<tr>
                    <td><strong>#${i + 1}</strong></td>
                    <td>${g.symbol}</td>
                    <td>$${g.price.toFixed(6)}</td>
                    <td class="positive">+${g.change_24h.toFixed(2)}%</td>
                    <td>$${g.volume.toLocaleString()}</td>
                </tr>`;
            });
            html += '</tbody></table>';
            container.innerHTML = html;
        }

        function updateTradesTable(trades) {
            const container = document.getElementById('trades-table');
            if (!trades || trades.length === 0) {
                container.innerHTML = '<p class="sub-metric">暫無交易記錄</p>';
                return;
            }

            let html = '<table><thead><tr><th>幣種</th><th>方向</th><th>價格</th><th>數量</th><th>盈虧</th><th>時間</th></tr></thead><tbody>';
            trades.reverse().forEach(trade => {
                const pnlClass = trade.pnl && trade.pnl >= 0 ? 'positive' : 'negative';
                const pnlText = trade.pnl ? `$${trade.pnl.toFixed(2)} (${trade.pnl_percentage.toFixed(2)}%)` : 'N/A';
                html += `<tr>
                    <td><strong>${trade.symbol}</strong></td>
                    <td>${trade.side === 'BUY' ? '買入' : '賣出'}</td>
                    <td>$${trade.price.toFixed(6)}</td>
                    <td>${trade.amount.toFixed(4)}</td>
                    <td class="${pnlClass}">${pnlText}</td>
                    <td>${new Date(trade.timestamp).toLocaleString('zh-TW')}</td>
                </tr>`;
            });
            html += '</tbody></table>';
            container.innerHTML = html;
        }

        function updateAlertsList(alerts) {
            const container = document.getElementById('alerts-list');
            if (!alerts || alerts.length === 0) {
                container.innerHTML = '<p class="sub-metric">暫無警報</p>';
                return;
            }

            let html = '';
            alerts.forEach(alert => {
                html += `<div class="alert alert-${alert.level}">
                    <strong>${alert.title}</strong><br>
                    ${alert.message}<br>
                    <small>${new Date(alert.timestamp).toLocaleString('zh-TW')}</small>
                </div>`;
            });
            container.innerHTML = html;
        }

        function updatePnlChart(trades) {
            if (!trades || trades.length === 0) return;

            const tradesWithPnl = trades.filter(t => t.pnl !== null);
            if (tradesWithPnl.length === 0) return;

            let cumulative = 0;
            pnlData = tradesWithPnl.map(t => {
                cumulative += t.pnl;
                return {
                    x: new Date(t.timestamp),
                    y: cumulative
                };
            });

            if (!pnlChart) {
                const ctx = document.getElementById('pnl-chart').getContext('2d');
                pnlChart = new Chart(ctx, {
                    type: 'line',
                    data: {
                        datasets: [{
                            label: '累計盈虧',
                            data: pnlData,
                            borderColor: '#10b981',
                            backgroundColor: 'rgba(16, 185, 129, 0.1)',
                            borderWidth: 2,
                            fill: true,
                            tension: 0.4
                        }]
                    },
                    options: {
                        responsive: true,
                        maintainAspectRatio: false,
                        plugins: {
                            legend: { display: false }
                        },
                        scales: {
                            x: {
                                type: 'time',
                                time: { unit: 'minute' },
                                grid: { color: 'rgba(148, 163, 184, 0.1)' },
                                ticks: { color: '#94a3b8' }
                            },
                            y: {
                                grid: { color: 'rgba(148, 163, 184, 0.1)' },
                                ticks: {
                                    color: '#94a3b8',
                                    callback: (value) => '$' + value.toFixed(2)
                                }
                            }
                        }
                    }
                });
            } else {
                pnlChart.data.datasets[0].data = pnlData;
                pnlChart.update('none');
            }
        }

        socket.emit('request_update');
    </script>
</body>
</html>"""
