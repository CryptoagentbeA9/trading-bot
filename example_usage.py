"""
Example usage of the Binance API client
"""

import asyncio
from binance_client import BinanceClient
from dotenv import load_dotenv

load_dotenv()


def main():
    # Initialize client (uses testnet by default)
    client = BinanceClient(testnet=True)

    # Get account balance
    print("\n=== Account Balance ===")
    balance = client.get_account_balance()
    for asset, amount in balance.items():
        print(f"{asset}: {amount}")

    # Get top gainers
    print("\n=== Top 10 Gainers (24h) ===")
    gainers = client.get_top_gainers(limit=10)
    for i, gainer in enumerate(gainers, 1):
        print(f"{i}. {gainer['symbol']}: +{gainer['change_24h']:.2f}% | Price: ${gainer['price']:.4f}")

    # Get current price
    print("\n=== Current Prices ===")
    btc_price = client.get_current_price('BTC/USDT')
    eth_price = client.get_current_price('ETH/USDT')
    print(f"BTC/USDT: ${btc_price}")
    print(f"ETH/USDT: ${eth_price}")

    # Example: Execute a small test trade (uncomment to use)
    # order = client.execute_market_buy('BTC/USDT', 0.001)
    # if order:
    #     print(f"\nOrder executed: {order}")

    # Calculate hypothetical P&L
    print("\n=== P&L Calculation Example ===")
    pnl = client.calculate_pnl(
        symbol='BTC/USDT',
        entry_price=50000,
        exit_price=52000,
        amount=0.1
    )
    print(f"Entry: ${pnl['entry_price']}, Exit: ${pnl['exit_price']}")
    print(f"P&L: ${pnl['pnl']:.2f} ({pnl['pnl_percentage']:.2f}%)")

    # Get open orders
    print("\n=== Open Orders ===")
    open_orders = client.get_open_orders()
    if open_orders:
        for order in open_orders:
            print(f"{order['symbol']}: {order['side']} {order['amount']} @ {order['price']}")
    else:
        print("No open orders")


async def websocket_example():
    """Example of WebSocket streaming"""
    client = BinanceClient(testnet=True)

    async def handle_ticker(data):
        print(f"BTC/USDT Price: ${float(data['c']):.2f} | 24h Change: {float(data['P']):.2f}%")

    # Stream BTC/USDT ticker (runs indefinitely)
    await client.stream_ticker('btcusdt', handle_ticker)


if __name__ == '__main__':
    # Run basic examples
    main()

    # Uncomment to run WebSocket streaming example
    # asyncio.run(websocket_example())
