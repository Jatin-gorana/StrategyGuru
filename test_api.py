import requests
import json
from typing import Dict, Any
import time


class BacktestAPIClient:
    """Client for interacting with the backtest API."""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        """Initialize the API client."""
        self.base_url = base_url
        self.session = requests.Session()
    
    def run_backtest(
        self,
        strategy_text: str,
        symbol: str,
        start_date: str,
        end_date: str,
        initial_capital: float = 10000
    ) -> Dict[str, Any]:
        """Run a backtest."""
        url = f"{self.base_url}/api/backtest"
        payload = {
            "strategy_text": strategy_text,
            "stock_symbol": symbol,
            "start_date": start_date,
            "end_date": end_date,
            "initial_capital": initial_capital
        }
        
        response = self.session.post(url, json=payload)
        response.raise_for_status()
        return response.json()
    
    def parse_strategy(self, strategy_text: str) -> Dict[str, Any]:
        """Parse a strategy."""
        url = f"{self.base_url}/api/backtest/parse-strategy"
        response = self.session.post(url, json={"strategy_text": strategy_text})
        response.raise_for_status()
        return response.json()
    
    def get_indicators(self) -> Dict[str, Any]:
        """Get supported indicators."""
        url = f"{self.base_url}/api/backtest/indicators"
        response = self.session.get(url)
        response.raise_for_status()
        return response.json()
    
    def get_examples(self) -> Dict[str, Any]:
        """Get example strategies."""
        url = f"{self.base_url}/api/backtest/examples"
        response = self.session.get(url)
        response.raise_for_status()
        return response.json()
    
    def health_check(self) -> Dict[str, Any]:
        """Check API health."""
        url = f"{self.base_url}/health"
        response = self.session.get(url)
        response.raise_for_status()
        return response.json()


def print_section(title: str):
    """Print a formatted section header."""
    print("\n" + "=" * 70)
    print(f"  {title}")
    print("=" * 70)


def print_metrics(metrics: Dict[str, Any]):
    """Print backtest metrics in a formatted way."""
    print(f"\n  Performance Metrics:")
    print(f"    Total Return: ${metrics['total_return']:,.2f} ({metrics['total_return_percent']:.2f}%)")
    print(f"    Sharpe Ratio: {metrics['sharpe_ratio']:.4f}")
    print(f"    Max Drawdown: {metrics['max_drawdown_percent']:.2f}%")
    print(f"    Win Rate: {metrics['win_rate']:.2f}%")
    print(f"    Total Trades: {metrics['total_trades']}")
    print(f"    Winning Trades: {metrics['winning_trades']}")
    print(f"    Losing Trades: {metrics['losing_trades']}")
    print(f"    Avg Win: ${metrics['avg_win']:,.2f}")
    print(f"    Avg Loss: ${metrics['avg_loss']:,.2f}")
    print(f"    Profit Factor: {metrics['profit_factor']:.2f}")


def test_health_check(client: BacktestAPIClient):
    """Test health check endpoint."""
    print_section("Test 1: Health Check")
    
    try:
        result = client.health_check()
        print(f"  Status: {result['status']}")
        print("  ✓ Health check passed")
    except Exception as e:
        print(f"  ✗ Health check failed: {e}")


def test_get_indicators(client: BacktestAPIClient):
    """Test get indicators endpoint."""
    print_section("Test 2: Get Supported Indicators")
    
    try:
        result = client.get_indicators()
        indicators = result['indicators']
        print(f"  Found {len(indicators)} indicators:")
        for name, info in indicators.items():
            print(f"    - {name}: {info['name']}")
        print("  ✓ Indicators retrieved successfully")
    except Exception as e:
        print(f"  ✗ Failed to get indicators: {e}")


def test_get_examples(client: BacktestAPIClient):
    """Test get examples endpoint."""
    print_section("Test 3: Get Example Strategies")
    
    try:
        result = client.get_examples()
        examples = result['examples']
        print(f"  Found {len(examples)} example strategies:")
        for example in examples:
            print(f"    - {example['name']}: {example['strategy']}")
        print("  ✓ Examples retrieved successfully")
    except Exception as e:
        print(f"  ✗ Failed to get examples: {e}")


def test_parse_strategy(client: BacktestAPIClient):
    """Test strategy parsing."""
    print_section("Test 4: Parse Strategy")
    
    strategies = [
        "Buy when RSI < 30 and sell when RSI > 70",
        "Buy when SMA(50) > SMA(200) and sell when SMA(50) < SMA(200)",
    ]
    
    for strategy in strategies:
        try:
            print(f"\n  Strategy: {strategy}")
            result = client.parse_strategy(strategy)
            print(f"    Buy: {result['buy_condition']}")
            print(f"    Sell: {result['sell_condition']}")
            print(f"    Indicators: {', '.join(result['indicators_required'])}")
            print("    ✓ Parsed successfully")
        except Exception as e:
            print(f"    ✗ Failed to parse: {e}")


def test_rsi_strategy(client: BacktestAPIClient):
    """Test RSI strategy backtest."""
    print_section("Test 5: RSI Strategy Backtest")
    
    try:
        print("\n  Running backtest: Buy when RSI < 30, Sell when RSI > 70")
        print("  Symbol: AAPL, Period: 2023-01-01 to 2024-01-01")
        
        start_time = time.time()
        result = client.run_backtest(
            strategy_text="Buy when RSI < 30 and sell when RSI > 70",
            symbol="AAPL",
            start_date="2023-01-01",
            end_date="2024-01-01"
        )
        elapsed = time.time() - start_time
        
        print(f"  Execution time: {elapsed:.2f}s")
        print(f"  Message: {result['message']}")
        print_metrics(result['metrics'])
        
        if result['trades']:
            print(f"\n  First Trade:")
            trade = result['trades'][0]
            print(f"    Entry: {trade['entry_date'][:10]} @ ${trade['entry_price']:.2f}")
            print(f"    Exit: {trade['exit_date'][:10]} @ ${trade['exit_price']:.2f}")
            print(f"    P&L: ${trade['pnl']:.2f} ({trade['pnl_percent']:.2f}%)")
        
        print("  ✓ Backtest completed successfully")
    except Exception as e:
        print(f"  ✗ Backtest failed: {e}")


def test_ma_crossover_strategy(client: BacktestAPIClient):
    """Test moving average crossover strategy."""
    print_section("Test 6: Moving Average Crossover Strategy")
    
    try:
        print("\n  Running backtest: Golden Cross (SMA 50/200)")
        print("  Symbol: GOOGL, Period: 2023-01-01 to 2024-01-01")
        
        start_time = time.time()
        result = client.run_backtest(
            strategy_text="Buy when SMA(50) > SMA(200) and sell when SMA(50) < SMA(200)",
            symbol="GOOGL",
            start_date="2023-01-01",
            end_date="2024-01-01"
        )
        elapsed = time.time() - start_time
        
        print(f"  Execution time: {elapsed:.2f}s")
        print(f"  Message: {result['message']}")
        print_metrics(result['metrics'])
        print("  ✓ Backtest completed successfully")
    except Exception as e:
        print(f"  ✗ Backtest failed: {e}")


def test_macd_strategy(client: BacktestAPIClient):
    """Test MACD strategy."""
    print_section("Test 7: MACD Strategy Backtest")
    
    try:
        print("\n  Running backtest: MACD Crossover")
        print("  Symbol: MSFT, Period: 2023-01-01 to 2024-01-01")
        
        start_time = time.time()
        result = client.run_backtest(
            strategy_text="Buy when MACD > Signal and sell when MACD < Signal",
            symbol="MSFT",
            start_date="2023-01-01",
            end_date="2024-01-01"
        )
        elapsed = time.time() - start_time
        
        print(f"  Execution time: {elapsed:.2f}s")
        print(f"  Message: {result['message']}")
        print_metrics(result['metrics'])
        print("  ✓ Backtest completed successfully")
    except Exception as e:
        print(f"  ✗ Backtest failed: {e}")


def test_combined_strategy(client: BacktestAPIClient):
    """Test combined indicator strategy."""
    print_section("Test 8: Combined Indicators Strategy")
    
    try:
        print("\n  Running backtest: RSI + Moving Averages")
        print("  Symbol: AMZN, Period: 2023-01-01 to 2024-01-01")
        
        start_time = time.time()
        result = client.run_backtest(
            strategy_text="Buy when RSI < 30 and SMA(50) > SMA(200) and sell when RSI > 70 or SMA(50) < SMA(200)",
            symbol="AMZN",
            start_date="2023-01-01",
            end_date="2024-01-01"
        )
        elapsed = time.time() - start_time
        
        print(f"  Execution time: {elapsed:.2f}s")
        print(f"  Message: {result['message']}")
        print_metrics(result['metrics'])
        print("  ✓ Backtest completed successfully")
    except Exception as e:
        print(f"  ✗ Backtest failed: {e}")


def test_different_capital(client: BacktestAPIClient):
    """Test backtest with different initial capital."""
    print_section("Test 9: Different Initial Capital")
    
    capitals = [5000, 10000, 50000]
    
    for capital in capitals:
        try:
            print(f"\n  Testing with ${capital:,} initial capital")
            result = client.run_backtest(
                strategy_text="Buy when RSI < 30 and sell when RSI > 70",
                symbol="AAPL",
                start_date="2023-01-01",
                end_date="2024-01-01",
                initial_capital=capital
            )
            
            final_equity = capital + result['metrics']['total_return']
            print(f"    Final Equity: ${final_equity:,.2f}")
            print(f"    Return: {result['metrics']['total_return_percent']:.2f}%")
        except Exception as e:
            print(f"    ✗ Failed: {e}")


def test_error_handling(client: BacktestAPIClient):
    """Test error handling."""
    print_section("Test 10: Error Handling")
    
    # Test invalid symbol
    print("\n  Test: Invalid stock symbol")
    try:
        result = client.run_backtest(
            strategy_text="Buy when RSI < 30 and sell when RSI > 70",
            symbol="INVALID",
            start_date="2023-01-01",
            end_date="2024-01-01"
        )
        print("    ✗ Should have raised an error")
    except requests.exceptions.HTTPError as e:
        print(f"    ✓ Correctly raised error: {e.response.json()['detail'][:50]}...")
    except Exception as e:
        print(f"    ✓ Correctly raised error: {str(e)[:50]}...")


def main():
    """Run all tests."""
    print("\n" + "=" * 70)
    print("  FASTAPI BACKTEST ENDPOINT - TEST SUITE")
    print("=" * 70)
    
    # Initialize client
    client = BacktestAPIClient()
    
    # Run tests
    test_health_check(client)
    test_get_indicators(client)
    test_get_examples(client)
    test_parse_strategy(client)
    test_rsi_strategy(client)
    test_ma_crossover_strategy(client)
    test_macd_strategy(client)
    test_combined_strategy(client)
    test_different_capital(client)
    test_error_handling(client)
    
    print("\n" + "=" * 70)
    print("  TEST SUITE COMPLETED")
    print("=" * 70 + "\n")


if __name__ == "__main__":
    main()
