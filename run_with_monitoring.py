"""
Example: Running the Trading Bot with Full Monitoring

This example demonstrates how to run the trading bot with:
- Structured logging (JSON format)
- Real-time metrics tracking
- Web dashboard
- Alerting system
"""

import time
from monitoring_integration import create_monitored_bot
from dashboard import TradingDashboard
from strategy_config import StrategyConfig


def main():
    print("Initializing Trading Bot with Monitoring...")

    # Create monitored bot components
    client, strategy, metrics_tracker, alerting = create_monitored_bot(
        testnet=True  # Use testnet for safety
    )

    # Create and start web dashboard
    dashboard = TradingDashboard(
        metrics_tracker=metrics_tracker,
        alerting_system=alerting,
        strategy_engine=strategy,
        port=5000
    )

    print("\nStarting web dashboard on http://localhost:5000")
    dashboard.run_background()

    print("\nBot is running. Press Ctrl+C to stop.")
    print("\nMonitoring Features:")
    print("  - Structured JSON logs in ./logs/")
    print("  - Real-time metrics tracking")
    print("  - Web dashboard at http://localhost:5000")
    print("  - Automatic alerting for critical events")
    print("\nLog Files:")
    print("  - logs/app.log       - Main application log")
    print("  - logs/trades.json   - Trade execution log (JSON)")
    print("  - logs/api.json      - API calls log (JSON)")
    print("  - logs/errors.log    - Error log")
    print("\nMetrics Files:")
    print("  - metrics/trades_YYYY-MM-DD.json - Daily trade metrics")

    try:
        # Main trading loop
        cycle_count = 0
        while True:
            cycle_count += 1
            print(f"\n{'='*60}")
            print(f"Strategy Cycle #{cycle_count}")
            print(f"{'='*60}")

            # Run strategy cycle
            summary = strategy.run_strategy_cycle()

            # Display summary
            print(f"\nCycle Summary:")
            print(f"  Signals Generated: {summary['signals_generated']}")
            print(f"  Positions Opened: {summary['positions_opened']}")
            print(f"  Positions Closed: {summary['positions_closed']}")

            if summary['actions']:
                print(f"\nActions Taken:")
                for action in summary['actions']:
                    print(f"  - {action}")

            # Display performance
            performance = strategy.get_performance_summary()
            print(f"\nPerformance:")
            print(f"  Total Trades: {performance['total_trades']}")
            print(f"  Win Rate: {performance['win_rate']}")
            print(f"  Total P&L: {performance['total_pnl']}")
            print(f"  Daily P&L: {performance['daily_pnl']}")
            print(f"  Open Positions: {performance['open_positions']}")

            # Display open positions
            positions = strategy.get_open_positions()
            if positions:
                print(f"\nOpen Positions:")
                for pos in positions:
                    print(f"  {pos['symbol']}: Entry {pos['entry_price']}, "
                          f"Current {pos['current_price']}, "
                          f"P&L {pos['unrealized_pnl']} ({pos['unrealized_pnl_pct']})")

            # Display recent alerts
            recent_alerts = alerting.get_recent_alerts(5)
            if recent_alerts:
                print(f"\nRecent Alerts:")
                for alert in recent_alerts[-3:]:
                    print(f"  [{alert.level.value.upper()}] {alert.title}: {alert.message}")

            # Wait before next cycle (e.g., 5 minutes)
            print(f"\nWaiting 5 minutes before next cycle...")
            time.sleep(300)

    except KeyboardInterrupt:
        print("\n\nShutting down bot...")

        # Final summary
        print("\n" + "="*60)
        print("Final Performance Summary")
        print("="*60)

        performance = strategy.get_performance_summary()
        for key, value in performance.items():
            print(f"{key.replace('_', ' ').title()}: {value}")

        # Export metrics
        print("\nExporting final metrics...")
        final_metrics = metrics_tracker.export_metrics()

        import json
        with open('final_metrics.json', 'w') as f:
            json.dump(final_metrics, f, indent=2)

        print("Metrics exported to final_metrics.json")
        print("\nBot stopped successfully.")


if __name__ == "__main__":
    main()
