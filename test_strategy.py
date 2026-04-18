"""
Test script for strategy engine
"""

from binance_client import BinanceClient
from strategy_engine import StrategyEngine
from strategy_config import StrategyConfig

def test_strategy_engine():
    """Test the strategy engine functionality"""

    print("=== Testing Strategy Engine ===\n")

    # Initialize client and engine
    client = BinanceClient(testnet=True)
    config = StrategyConfig()
    engine = StrategyEngine(client, config)

    print("1. Configuration:")
    print(f"   - Min gain: {config.min_gain_percent}%")
    print(f"   - Position size: {config.position_size_percent}%")
    print(f"   - Max positions: {config.max_concurrent_positions}")
    print(f"   - Stop loss: {config.stop_loss_percent}%")
    print(f"   - Take profit: {config.take_profit_percent}%\n")

    # Test market data analysis
    print("2. Fetching top gainers...")
    gainers = client.get_top_gainers(limit=10)

    if gainers:
        print(f"   Found {len(gainers)} gainers:")
        for i, g in enumerate(gainers[:5], 1):
            print(f"   {i}. {g['symbol']}: +{g['change_24h']:.2f}% (Vol: ${g['volume']:,.0f})")
    else:
        print("   No gainers data available")

    # Test signal generation
    print("\n3. Generating trading signals...")
    signals = engine.analyze_market_data(gainers)

    if signals:
        print(f"   Generated {len(signals)} signals:")
        for sig in signals[:3]:
            print(f"   - {sig.action} {sig.symbol} @ ${sig.price:.4f}")
            print(f"     Confidence: {sig.confidence:.2f}, Reason: {sig.reason}")
    else:
        print("   No signals generated")

    # Test performance metrics
    print("\n4. Performance metrics:")
    metrics = engine.get_performance_summary()
    for key, value in metrics.items():
        print(f"   - {key}: {value}")

    # Test position management
    print("\n5. Open positions:")
    positions = engine.get_open_positions()
    if positions:
        for pos in positions:
            print(f"   - {pos['symbol']}: Entry ${pos['entry_price']}, PnL: {pos['unrealized_pnl']}")
    else:
        print("   No open positions")

    print("\n=== Test Complete ===")

if __name__ == "__main__":
    test_strategy_engine()
