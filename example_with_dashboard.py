"""
完整整合範例：交易機器人 + 即時監控面板
演示如何將即時監控面板整合到交易機器人中
"""

import time
import threading
from binance_client import BinanceClient
from strategy_engine import StrategyEngine
from strategy_config import StrategyConfig
from metrics_tracker import MetricsTracker
from alerting import AlertingSystem, AlertLevel
from dashboard_realtime import RealtimeDashboard


def run_trading_bot(client, strategy_engine, metrics_tracker, alerting_system):
    """交易機器人主循環"""
    print("🤖 交易機器人開始運行...")

    while True:
        try:
            # 獲取漲幅榜
            gainers = client.get_top_gainers(limit=10)
            print(f"📊 發現 {len(gainers)} 個漲幅幣種")

            # 分析市場數據
            signals = strategy_engine.analyze_market_data(gainers)

            # 處理交易信號
            for signal in signals:
                if signal.action == 'BUY' and signal.confidence > 0.7:
                    print(f"💰 買入信號: {signal.symbol} @ ${signal.price:.6f}")
                    # 這裡可以執行實際交易
                    # result = strategy_engine.execute_trade(signal)

                    # 記錄交易
                    metrics_tracker.record_trade(
                        symbol=signal.symbol,
                        side='BUY',
                        amount=0.01,
                        price=signal.price
                    )

                    # 發送警報
                    alerting_system.send_alert(
                        level=AlertLevel.INFO,
                        title=f"買入 {signal.symbol}",
                        message=f"價格: ${signal.price:.6f}, 信心度: {signal.confidence:.2%}"
                    )

            # 檢查持倉
            strategy_engine.check_positions()

            # 等待下一輪
            time.sleep(60)

        except KeyboardInterrupt:
            print("\n⏹️  停止交易機器人...")
            break
        except Exception as e:
            print(f"❌ 錯誤: {e}")
            alerting_system.send_alert(
                level=AlertLevel.CRITICAL,
                title="系統錯誤",
                message=str(e)
            )
            time.sleep(10)


def main():
    """主程序"""
    print("=" * 60)
    print("🚀 啟動交易機器人系統")
    print("=" * 60)

    # 初始化組件
    print("\n📦 初始化組件...")
    client = BinanceClient(testnet=True)
    strategy_config = StrategyConfig()
    metrics_tracker = MetricsTracker()
    alerting_system = AlertingSystem()
    strategy_engine = StrategyEngine(client, strategy_config)

    print("✅ 組件初始化完成")

    # 創建即時監控面板
    print("\n🌐 啟動即時監控面板...")
    dashboard = RealtimeDashboard(
        metrics_tracker=metrics_tracker,
        alerting_system=alerting_system,
        strategy_engine=strategy_engine,
        binance_client=client,
        port=5000
    )

    # 在背景執行緒運行儀表板
    dashboard_thread = threading.Thread(
        target=lambda: dashboard.run(debug=False),
        daemon=True
    )
    dashboard_thread.start()

    print("✅ 儀表板已啟動")
    print(f"📱 訪問地址: http://localhost:5000")

    # 等待儀表板啟動
    time.sleep(3)

    print("\n" + "=" * 60)
    print("✅ 系統啟動完成！")
    print("=" * 60)
    print("\n💡 功能:")
    print("   • 交易機器人: 自動監控漲幅榜並執行交易")
    print("   • 即時監控: WebSocket 即時更新交易數據")
    print("   • 圖表分析: 盈虧曲線和交易歷史")
    print("   • 警報系統: 重要事件即時通知")
    print("\n按 Ctrl+C 停止系統\n")

    # 運行交易機器人
    try:
        run_trading_bot(client, strategy_engine, metrics_tracker, alerting_system)
    except KeyboardInterrupt:
        print("\n\n⏹️  正在關閉系統...")
        dashboard.stop()
        print("✅ 系統已安全關閉")


if __name__ == '__main__':
    main()
