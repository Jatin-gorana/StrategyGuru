"""
Example usage of the backtest_engine module.

This script demonstrates how to run backtests with different strategies
and analyze the results.
"""

from backend.services.data_fetcher import get_stock_data
from backend.services.indicators import (
    calculate_rsi,
    calculate_ma,
    calculate_ema,
    calculate_macd,
    add_all_indicators
)
from backend.services.backtest_engine import BacktestEngine, StrategyBacktester
import pandas as pd
import numpy as np


def example_simple_rsi_strategy():
    """Example 1: Simple RSI-based strategy."""
    print("=" * 70)
    print("Example 1: Simple RSI Strategy")
    print("=" * 70)
    
    try:
        # Fetch data
        df = get_stock_data('AAPL', '2023-01-01', '2024-01-01')
        print(f"\nFetched {len(df)} days of AAPL data")
        
        # Calculate RSI
        df['RSI'] = calculate_rsi(df, period=14)
        
        # Define strategy
        buy_condition = df['RSI'] < 30
        sell_condition = df['RSI'] > 70
        
        # Run backtest
        engine = BacktestEngine(df, initial_capital=10000)
        trades, equity_curve, metrics = engine.run_backtest(buy_condition, sell_condition)
        
        # Display results
        print(f"\nBacktest Results:")
        print(f"  Initial Capital: ${engine.initial_capital:,.2f}")
        print(f"  Final Equity: ${metrics.total_return + engine.initial_capital:,.2f}")
        print(f"  Total Return: ${metrics.total_return:,.2f} ({metrics.total_return_percent:.2f}%)")
        print(f"  Total Trades: {metrics.total_trades}")
        print(f"  Winning Trades: {metrics.winning_trades}")
        print(f"  Losing Trades: {metrics.losing_trades}")
        print(f"  Win Rate: {metrics.win_rate:.2f}%")
        print(f"  Sharpe Ratio: {metrics.sharpe_ratio:.4f}")
        print(f"  Max Drawdown: {metrics.max_drawdown_percent:.2f}%")
        print(f"  Profit Factor: {metrics.profit_factor:.2f}")
        
        if trades:
            print(f"\nFirst 5 Trades:")
            for i, trade in enumerate(trades[:5], 1):
                print(f"  Trade {i}:")
                print(f"    Entry: {trade.entry_date.date()} @ ${trade.entry_price:.2f}")
                print(f"    Exit: {trade.exit_date.date()} @ ${trade.exit_price:.2f}")
                print(f"    P&L: ${trade.pnl:.2f} ({trade.pnl_percent:.2f}%)")
        
    except Exception as e:
        print(f"Error: {e}")


def example_moving_average_crossover():
    """Example 2: Moving Average Crossover strategy."""
    print("\n" + "=" * 70)
    print("Example 2: Moving Average Crossover Strategy")
    print("=" * 70)
    
    try:
        # Fetch data
        df = get_stock_data('GOOGL', '2023-01-01', '2024-01-01')
        print(f"\nFetched {len(df)} days of GOOGL data")
        
        # Calculate moving averages
        df['MA50'] = calculate_ma(df, period=50)
        df['MA200'] = calculate_ma(df, period=200)
        
        # Define strategy: Buy when MA50 > MA200, Sell when MA50 < MA200
        buy_condition = (df['MA50'] > df['MA200']) & (df['MA50'].shift(1) <= df['MA200'].shift(1))
        sell_condition = (df['MA50'] < df['MA200']) & (df['MA50'].shift(1) >= df['MA200'].shift(1))
        
        # Run backtest
        engine = BacktestEngine(df, initial_capital=10000)
        trades, equity_curve, metrics = engine.run_backtest(buy_condition, sell_condition)
        
        # Display results
        print(f"\nBacktest Results:")
        print(f"  Initial Capital: ${engine.initial_capital:,.2f}")
        print(f"  Final Equity: ${metrics.total_return + engine.initial_capital:,.2f}")
        print(f"  Total Return: ${metrics.total_return:,.2f} ({metrics.total_return_percent:.2f}%)")
        print(f"  Total Trades: {metrics.total_trades}")
        print(f"  Win Rate: {metrics.win_rate:.2f}%")
        print(f"  Sharpe Ratio: {metrics.sharpe_ratio:.4f}")
        print(f"  Max Drawdown: {metrics.max_drawdown_percent:.2f}%")
        print(f"  Avg Win: ${metrics.avg_win:.2f}")
        print(f"  Avg Loss: ${metrics.avg_loss:.2f}")
        print(f"  Profit Factor: {metrics.profit_factor:.2f}")
        
    except Exception as e:
        print(f"Error: {e}")


def example_macd_strategy():
    """Example 3: MACD-based strategy."""
    print("\n" + "=" * 70)
    print("Example 3: MACD Strategy")
    print("=" * 70)
    
    try:
        # Fetch data
        df = get_stock_data('MSFT', '2023-01-01', '2024-01-01')
        print(f"\nFetched {len(df)} days of MSFT data")
        
        # Calculate MACD
        from backend.services.indicators import calculate_macd
        macd, signal, histogram = calculate_macd(df)
        df['MACD'] = macd
        df['MACD_Signal'] = signal
        
        # Define strategy: Buy when MACD > Signal, Sell when MACD < Signal
        buy_condition = (df['MACD'] > df['MACD_Signal']) & (df['MACD'].shift(1) <= df['MACD_Signal'].shift(1))
        sell_condition = (df['MACD'] < df['MACD_Signal']) & (df['MACD'].shift(1) >= df['MACD_Signal'].shift(1))
        
        # Run backtest
        engine = BacktestEngine(df, initial_capital=10000)
        trades, equity_curve, metrics = engine.run_backtest(buy_condition, sell_condition)
        
        # Display results
        print(f"\nBacktest Results:")
        print(f"  Initial Capital: ${engine.initial_capital:,.2f}")
        print(f"  Final Equity: ${metrics.total_return + engine.initial_capital:,.2f}")
        print(f"  Total Return: ${metrics.total_return:,.2f} ({metrics.total_return_percent:.2f}%)")
        print(f"  Total Trades: {metrics.total_trades}")
        print(f"  Win Rate: {metrics.win_rate:.2f}%")
        print(f"  Sharpe Ratio: {metrics.sharpe_ratio:.4f}")
        print(f"  Max Drawdown: {metrics.max_drawdown_percent:.2f}%")
        
    except Exception as e:
        print(f"Error: {e}")


def example_combined_strategy():
    """Example 4: Combined indicators strategy."""
    print("\n" + "=" * 70)
    print("Example 4: Combined Indicators Strategy")
    print("=" * 70)
    
    try:
        # Fetch data
        df = get_stock_data('AMZN', '2023-01-01', '2024-01-01')
        print(f"\nFetched {len(df)} days of AMZN data")
        
        # Calculate indicators
        df['RSI'] = calculate_rsi(df, period=14)
        df['MA50'] = calculate_ma(df, period=50)
        df['MA200'] = calculate_ma(df, period=200)
        
        # Define strategy:
        # Buy: RSI < 30 AND MA50 > MA200
        # Sell: RSI > 70 OR MA50 < MA200
        buy_condition = (df['RSI'] < 30) & (df['MA50'] > df['MA200'])
        sell_condition = (df['RSI'] > 70) | (df['MA50'] < df['MA200'])
        
        # Run backtest
        engine = BacktestEngine(df, initial_capital=10000)
        trades, equity_curve, metrics = engine.run_backtest(buy_condition, sell_condition)
        
        # Display results
        print(f"\nBacktest Results:")
        print(f"  Initial Capital: ${engine.initial_capital:,.2f}")
        print(f"  Final Equity: ${metrics.total_return + engine.initial_capital:,.2f}")
        print(f"  Total Return: ${metrics.total_return:,.2f} ({metrics.total_return_percent:.2f}%)")
        print(f"  Total Trades: {metrics.total_trades}")
        print(f"  Winning Trades: {metrics.winning_trades}")
        print(f"  Losing Trades: {metrics.losing_trades}")
        print(f"  Win Rate: {metrics.win_rate:.2f}%")
        print(f"  Sharpe Ratio: {metrics.sharpe_ratio:.4f}")
        print(f"  Max Drawdown: {metrics.max_drawdown_percent:.2f}%")
        print(f"  Profit Factor: {metrics.profit_factor:.2f}")
        
    except Exception as e:
        print(f"Error: {e}")


def example_strategy_backtester():
    """Example 5: Using StrategyBacktester class."""
    print("\n" + "=" * 70)
    print("Example 5: StrategyBacktester Class")
    print("=" * 70)
    
    try:
        # Define a strategy function
        def rsi_strategy(data):
            """RSI-based strategy function."""
            rsi = calculate_rsi(data, period=14)
            buy = rsi < 30
            sell = rsi > 70
            return buy, sell
        
        # Fetch data
        df = get_stock_data('TSLA', '2023-01-01', '2024-01-01')
        print(f"\nFetched {len(df)} days of TSLA data")
        
        # Run backtest using StrategyBacktester
        backtester = StrategyBacktester(df, initial_capital=10000)
        trades, equity_curve, metrics = backtester.backtest(rsi_strategy)
        
        # Display results
        print(f"\nBacktest Results:")
        print(f"  Total Return: ${metrics.total_return:,.2f} ({metrics.total_return_percent:.2f}%)")
        print(f"  Total Trades: {metrics.total_trades}")
        print(f"  Win Rate: {metrics.win_rate:.2f}%")
        print(f"  Sharpe Ratio: {metrics.sharpe_ratio:.4f}")
        print(f"  Max Drawdown: {metrics.max_drawdown_percent:.2f}%")
        
    except Exception as e:
        print(f"Error: {e}")


def example_with_commission_slippage():
    """Example 6: Backtest with commission and slippage."""
    print("\n" + "=" * 70)
    print("Example 6: Backtest with Commission and Slippage")
    print("=" * 70)
    
    try:
        # Fetch data
        df = get_stock_data('AAPL', '2023-01-01', '2024-01-01')
        print(f"\nFetched {len(df)} days of AAPL data")
        
        # Calculate RSI
        df['RSI'] = calculate_rsi(df, period=14)
        
        # Define strategy
        buy_condition = df['RSI'] < 30
        sell_condition = df['RSI'] > 70
        
        # Run backtest WITHOUT commission/slippage
        engine1 = BacktestEngine(df, initial_capital=10000, commission=0, slippage=0)
        trades1, _, metrics1 = engine1.run_backtest(buy_condition, sell_condition)
        
        # Run backtest WITH commission/slippage
        engine2 = BacktestEngine(df, initial_capital=10000, commission=0.001, slippage=0.001)
        trades2, _, metrics2 = engine2.run_backtest(buy_condition, sell_condition)
        
        # Compare results
        print(f"\nComparison:")
        print(f"  Without Commission/Slippage:")
        print(f"    Total Return: ${metrics1.total_return:,.2f} ({metrics1.total_return_percent:.2f}%)")
        print(f"    Sharpe Ratio: {metrics1.sharpe_ratio:.4f}")
        
        print(f"\n  With Commission (0.1%) and Slippage (0.1%):")
        print(f"    Total Return: ${metrics2.total_return:,.2f} ({metrics2.total_return_percent:.2f}%)")
        print(f"    Sharpe Ratio: {metrics2.sharpe_ratio:.4f}")
        
        print(f"\n  Impact:")
        print(f"    Return Difference: ${metrics1.total_return - metrics2.total_return:,.2f}")
        print(f"    Sharpe Difference: {metrics1.sharpe_ratio - metrics2.sharpe_ratio:.4f}")
        
    except Exception as e:
        print(f"Error: {e}")


def example_equity_curve_analysis():
    """Example 7: Analyze equity curve."""
    print("\n" + "=" * 70)
    print("Example 7: Equity Curve Analysis")
    print("=" * 70)
    
    try:
        # Fetch data
        df = get_stock_data('GOOGL', '2023-01-01', '2024-01-01')
        print(f"\nFetched {len(df)} days of GOOGL data")
        
        # Calculate indicators
        df['MA50'] = calculate_ma(df, period=50)
        df['MA200'] = calculate_ma(df, period=200)
        
        # Define strategy
        buy_condition = (df['MA50'] > df['MA200']) & (df['MA50'].shift(1) <= df['MA200'].shift(1))
        sell_condition = (df['MA50'] < df['MA200']) & (df['MA50'].shift(1) >= df['MA200'].shift(1))
        
        # Run backtest
        engine = BacktestEngine(df, initial_capital=10000)
        trades, equity_curve, metrics = engine.run_backtest(buy_condition, sell_condition)
        
        # Analyze equity curve
        print(f"\nEquity Curve Analysis:")
        equity_values = [ec.equity for ec in equity_curve]
        print(f"  Starting Equity: ${equity_values[0]:,.2f}")
        print(f"  Ending Equity: ${equity_values[-1]:,.2f}")
        print(f"  Peak Equity: ${max(equity_values):,.2f}")
        print(f"  Lowest Equity: ${min(equity_values):,.2f}")
        
        # Calculate monthly returns
        print(f"\nMonthly Performance:")
        equity_df = pd.DataFrame({
            'date': [ec.date for ec in equity_curve],
            'equity': equity_values
        })
        equity_df['date'] = pd.to_datetime(equity_df['date'])
        equity_df['month'] = equity_df['date'].dt.to_period('M')
        
        monthly_returns = equity_df.groupby('month')['equity'].agg(['first', 'last'])
        monthly_returns['return'] = ((monthly_returns['last'] - monthly_returns['first']) / monthly_returns['first'] * 100)
        
        for month, row in monthly_returns.iterrows():
            print(f"  {month}: {row['return']:.2f}%")
        
    except Exception as e:
        print(f"Error: {e}")


def example_multiple_strategies_comparison():
    """Example 8: Compare multiple strategies."""
    print("\n" + "=" * 70)
    print("Example 8: Multiple Strategies Comparison")
    print("=" * 70)
    
    try:
        # Fetch data
        df = get_stock_data('AAPL', '2023-01-01', '2024-01-01')
        print(f"\nFetched {len(df)} days of AAPL data")
        
        strategies = {}
        
        # Strategy 1: RSI
        df['RSI'] = calculate_rsi(df, period=14)
        buy1 = df['RSI'] < 30
        sell1 = df['RSI'] > 70
        engine1 = BacktestEngine(df, initial_capital=10000)
        _, _, metrics1 = engine1.run_backtest(buy1, sell1)
        strategies['RSI'] = metrics1
        
        # Strategy 2: Moving Average Crossover
        df['MA50'] = calculate_ma(df, period=50)
        df['MA200'] = calculate_ma(df, period=200)
        buy2 = (df['MA50'] > df['MA200']) & (df['MA50'].shift(1) <= df['MA200'].shift(1))
        sell2 = (df['MA50'] < df['MA200']) & (df['MA50'].shift(1) >= df['MA200'].shift(1))
        engine2 = BacktestEngine(df, initial_capital=10000)
        _, _, metrics2 = engine2.run_backtest(buy2, sell2)
        strategies['MA Crossover'] = metrics2
        
        # Strategy 3: MACD
        from backend.services.indicators import calculate_macd
        macd, signal, _ = calculate_macd(df)
        df['MACD'] = macd
        df['MACD_Signal'] = signal
        buy3 = (df['MACD'] > df['MACD_Signal']) & (df['MACD'].shift(1) <= df['MACD_Signal'].shift(1))
        sell3 = (df['MACD'] < df['MACD_Signal']) & (df['MACD'].shift(1) >= df['MACD_Signal'].shift(1))
        engine3 = BacktestEngine(df, initial_capital=10000)
        _, _, metrics3 = engine3.run_backtest(buy3, sell3)
        strategies['MACD'] = metrics3
        
        # Compare strategies
        print(f"\nStrategy Comparison:")
        print(f"{'Strategy':<20} {'Return %':<12} {'Sharpe':<10} {'Win Rate':<12} {'Max DD %':<12}")
        print("-" * 66)
        
        for name, metrics in strategies.items():
            print(f"{name:<20} {metrics.total_return_percent:>10.2f}% {metrics.sharpe_ratio:>9.4f} {metrics.win_rate:>10.2f}% {metrics.max_drawdown_percent:>10.2f}%")
        
    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    print("\n" + "=" * 70)
    print("BACKTEST ENGINE - USAGE EXAMPLES")
    print("=" * 70)
    
    # Run all examples
    example_simple_rsi_strategy()
    example_moving_average_crossover()
    example_macd_strategy()
    example_combined_strategy()
    example_strategy_backtester()
    example_with_commission_slippage()
    example_equity_curve_analysis()
    example_multiple_strategies_comparison()
    
    print("\n" + "=" * 70)
    print("Examples completed!")
    print("=" * 70)
