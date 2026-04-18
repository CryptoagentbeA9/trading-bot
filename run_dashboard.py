"""
Launch script for real-time trading dashboard
"""

import sys
import json
from pathlib import Path
from dashboard_realtime import RealtimeDashboard
from binance_client import BinanceClient
from metrics_tracker import MetricsTracker
from alerting import AlertingSystem
from strategy_engine import StrategyEngine
from strategy_config import StrategyConfig


def load_config():
    """Load dashboard configuration"""
    config_path = Path(__file__).parent / 'config_dashboard.json'
    if config_path.exists():
        with open(config_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {
        'dashboard': {
            'port': 5000,
            'host': '0.0.0.0',
            'debug': False
        }
    }


def main():
    """Main entry point"""
    print("🚀 啟動交易機器人即時監控面板...")

    config = load_config()
    port = config['dashboard']['port']

    print("📊 初始化組件...")
    client = BinanceClient(testnet=True)
    metrics_tracker = MetricsTracker()
    alerting_system = AlertingSystem()
    strategy_config = StrategyConfig()
    strategy_engine = StrategyEngine(client, strategy_config)

    print("🌐 創建儀表板...")
    dashboard = RealtimeDashboard(
        metrics_tracker=metrics_tracker,
        alerting_system=alerting_system,
        strategy_engine=strategy_engine,
        binance_client=client,
        port=port
    )

    print(f"\n✅ 儀表板已啟動！")
    print(f"📱 訪問地址: http://localhost:{port}")
    print(f"🌍 網絡訪問: http://0.0.0.0:{port}")
    print(f"\n💡 功能特性:")
    print(f"   • WebSocket 即時更新 (每2秒)")
    print(f"   • 即時盈虧曲線圖表")
    print(f"   • 持倉和交易記錄")
    print(f"   • 漲幅榜監控")
    print(f"   • 系統警報通知")
    print(f"   • 響應式設計 (支持手機)")
    print(f"\n按 Ctrl+C 停止服務器\n")

    try:
        dashboard.run(debug=config['dashboard']['debug'])
    except KeyboardInterrupt:
        print("\n\n⏹️  正在停止儀表板...")
        dashboard.stop()
        print("✅ 已安全關閉")
        sys.exit(0)


if __name__ == '__main__':
    main()
