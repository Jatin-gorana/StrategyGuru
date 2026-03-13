"""
Example usage of the indicators module.

This script demonstrates how to calculate various trading indicators
using the indicators module with real stock data.
"""

from backend.services.data_fetcher import get_stock_data
from backend.services.indicators import (
    calculate_rsi,
    calculate_ma,
    calculate_ema,
    calculate_macd,
    calculate_bollinger_bands,
    calculate_atr,
    calculate_stochastic,
    calculate_adx,
    add_all_indicators
)
import pandas as pd


def example_basic_indicators():
    """Example 1: Calculate basic indicators (RSI, MA50, MA200)."""
    print("=" * 70)
    print("Example 1: Basic Indicators (RSI, MA50, MA200)")
    print("=" * 70)
    
    try:
        # Fetch data
        df = get_stock_data('AAPL', '2023-01-01', '2024-01-01')
        print(f"\nFetched {len(df)} days of AAPL data")
        
        # Calculate indicators
        df['RSI'] = calculate_rsi(df, period=14)
        df['MA50'] = calculate_ma(df, period=50)
        df['MA200'] = calculate_ma(df, period=200)
        
        # Display results
        print("\nIndicator values (last 10 rows):")
        print(df[['close', 'RSI', 'MA50', 'MA200']].tail(10))
        
        print("\nRSI Statistics:")
        print(f"  Mean: {df['RSI'].mean():.2f}")
        print(f"  Min: {df['RSI'].min():.2f}")
        print(f"  Max: {df['RSI'].max():.2f}")
        
        print("\nMA50 vs MA200 Analysis:")
        df['MA_Signal'] = (df['MA50'] > df['MA200']).astype(int)
        bullish_days = (df['MA_Signal'] == 1).sum()
        print(f"  Days MA50 > MA200 (Bullish): {bullish_days}")
        print(f"  Days MA50 <= MA200 (Bearish): {len(df) - bullish_days}")
        
    except Exception as e:
        print(f"Error: {e}")


def example_moving_averages():
    """Example 2: Compare different moving averages."""
    print("\n" + "=" * 70)
    print("Example 2: Moving Averages Comparison")
    print("=" * 70)
    
    try:
        df = get_stock_data('GOOGL', '2023-06-01', '2024-01-01')
        
        # Calculate different MAs
        df['SMA20'] = calculate_ma(df, period=20)
        df['SMA50'] = calculate_ma(df, period=50)
        df['SMA200'] = calculate_ma(df, period=200)
        df['EMA12'] = calculate_ema(df, period=12)
        df['EMA26'] = calculate_ema(df, period=26)
        
        print(f"\nFetched {len(df)} days of GOOGL data")
        print("\nMoving Averages (last 5 rows):")
        print(df[['close', 'SMA20', 'SMA50', 'SMA200', 'EMA12', 'EMA26']].tail(5))
        
        # Analyze crossovers
        print("\nCrossover Analysis:")
        ema_crossover = (df['EMA12'] > df['EMA26']).astype(int).diff()
        bullish_crosses = (ema_crossover == 1).sum()
        bearish_crosses = (ema_crossover == -1).sum()
        print(f"  EMA12/EMA26 Bullish Crosses: {bullish_crosses}")
        print(f"  EMA12/EMA26 Bearish Crosses: {bearish_crosses}")
        
    except Exception as e:
        print(f"Error: {e}")


def example_macd():
    """Example 3: MACD indicator."""
    print("\n" + "=" * 70)
    print("Example 3: MACD (Moving Average Convergence Divergence)")
    print("=" * 70)
    
    try:
        df = get_stock_data('MSFT', '2023-01-01', '2024-01-01')
        
        macd_line, signal_line, histogram = calculate_macd(df)
        df['MACD'] = macd_line
        df['MACD_Signal'] = signal_line
        df['MACD_Histogram'] = histogram
        
        print(f"\nFetched {len(df)} days of MSFT data")
        print("\nMACD Values (last 10 rows):")
        print(df[['close', 'MACD', 'MACD_Signal', 'MACD_Histogram']].tail(10))
        
        # Analyze MACD signals
        print("\nMACD Signal Analysis:")
        macd_signal = (df['MACD'] > df['MACD_Signal']).astype(int).diff()
        bullish_signals = (macd_signal == 1).sum()
        bearish_signals = (macd_signal == -1).sum()
        print(f"  Bullish Signals (MACD crosses above Signal): {bullish_signals}")
        print(f"  Bearish Signals (MACD crosses below Signal): {bearish_signals}")
        
    except Exception as e:
        print(f"Error: {e}")


def example_bollinger_bands():
    """Example 4: Bollinger Bands."""
    print("\n" + "=" * 70)
    print("Example 4: Bollinger Bands")
    print("=" * 70)
    
    try:
        df = get_stock_data('AMZN', '2023-06-01', '2024-01-01')
        
        upper_bb, middle_bb, lower_bb = calculate_bollinger_bands(df, period=20, std_dev=2)
        df['BB_Upper'] = upper_bb
        df['BB_Middle'] = middle_bb
        df['BB_Lower'] = lower_bb
        
        print(f"\nFetched {len(df)} days of AMZN data")
        print("\nBollinger Bands (last 5 rows):")
        print(df[['close', 'BB_Upper', 'BB_Middle', 'BB_Lower']].tail(5))
        
        # Analyze band touches
        print("\nBollinger Bands Analysis:")
        touches_upper = (df['close'] >= df['BB_Upper']).sum()
        touches_lower = (df['close'] <= df['BB_Lower']).sum()
        print(f"  Days price touched upper band: {touches_upper}")
        print(f"  Days price touched lower band: {touches_lower}")
        
        # Calculate band width
        df['BB_Width'] = df['BB_Upper'] - df['BB_Lower']
        print(f"\nBand Width Statistics:")
        print(f"  Mean: ${df['BB_Width'].mean():.2f}")
        print(f"  Min: ${df['BB_Width'].min():.2f}")
        print(f"  Max: ${df['BB_Width'].max():.2f}")
        
    except Exception as e:
        print(f"Error: {e}")


def example_volatility_indicators():
    """Example 5: Volatility indicators (ATR, Bollinger Bands)."""
    print("\n" + "=" * 70)
    print("Example 5: Volatility Indicators")
    print("=" * 70)
    
    try:
        df = get_stock_data('TSLA', '2023-01-01', '2024-01-01')
        
        df['ATR'] = calculate_atr(df, period=14)
        upper_bb, middle_bb, lower_bb = calculate_bollinger_bands(df, period=20, std_dev=2)
        df['BB_Upper'] = upper_bb
        df['BB_Lower'] = lower_bb
        
        print(f"\nFetched {len(df)} days of TSLA data")
        print("\nVolatility Indicators (last 10 rows):")
        print(df[['close', 'ATR', 'BB_Upper', 'BB_Lower']].tail(10))
        
        print("\nATR Statistics:")
        print(f"  Mean: ${df['ATR'].mean():.2f}")
        print(f"  Min: ${df['ATR'].min():.2f}")
        print(f"  Max: ${df['ATR'].max():.2f}")
        
        # Calculate volatility percentage
        df['ATR_Percent'] = (df['ATR'] / df['close']) * 100
        print(f"\nATR as % of Close Price:")
        print(f"  Mean: {df['ATR_Percent'].mean():.2f}%")
        print(f"  Min: {df['ATR_Percent'].min():.2f}%")
        print(f"  Max: {df['ATR_Percent'].max():.2f}%")
        
    except Exception as e:
        print(f"Error: {e}")


def example_stochastic():
    """Example 6: Stochastic Oscillator."""
    print("\n" + "=" * 70)
    print("Example 6: Stochastic Oscillator")
    print("=" * 70)
    
    try:
        df = get_stock_data('AAPL', '2023-06-01', '2024-01-01')
        
        k_line, d_line = calculate_stochastic(df, period=14, smooth_k=3, smooth_d=3)
        df['Stoch_K'] = k_line
        df['Stoch_D'] = d_line
        
        print(f"\nFetched {len(df)} days of AAPL data")
        print("\nStochastic Oscillator (last 10 rows):")
        print(df[['close', 'Stoch_K', 'Stoch_D']].tail(10))
        
        print("\nStochastic Analysis:")
        overbought = (df['Stoch_K'] > 80).sum()
        oversold = (df['Stoch_K'] < 20).sum()
        print(f"  Days Overbought (K > 80): {overbought}")
        print(f"  Days Oversold (K < 20): {oversold}")
        
    except Exception as e:
        print(f"Error: {e}")


def example_adx():
    """Example 7: Average Directional Index (ADX)."""
    print("\n" + "=" * 70)
    print("Example 7: Average Directional Index (ADX)")
    print("=" * 70)
    
    try:
        df = get_stock_data('GOOGL', '2023-01-01', '2024-01-01')
        
        df['ADX'] = calculate_adx(df, period=14)
        
        print(f"\nFetched {len(df)} days of GOOGL data")
        print("\nADX Values (last 10 rows):")
        print(df[['close', 'ADX']].tail(10))
        
        print("\nADX Analysis:")
        strong_trend = (df['ADX'] > 25).sum()
        weak_trend = (df['ADX'] <= 25).sum()
        print(f"  Days with Strong Trend (ADX > 25): {strong_trend}")
        print(f"  Days with Weak Trend (ADX <= 25): {weak_trend}")
        
    except Exception as e:
        print(f"Error: {e}")


def example_all_indicators():
    """Example 8: Add all indicators at once."""
    print("\n" + "=" * 70)
    print("Example 8: All Indicators Combined")
    print("=" * 70)
    
    try:
        df = get_stock_data('MSFT', '2023-06-01', '2024-01-01')
        
        # Add all indicators
        df = add_all_indicators(df)
        
        print(f"\nFetched {len(df)} days of MSFT data")
        print(f"Total columns: {len(df.columns)}")
        print(f"\nColumns: {list(df.columns)}")
        
        print("\nSample data with all indicators (last 3 rows):")
        print(df.tail(3))
        
        print("\nIndicator Summary (last row):")
        last_row = df.iloc[-1]
        print(f"  Close: ${last_row['close']:.2f}")
        print(f"  RSI: {last_row['RSI']:.2f}")
        print(f"  MA50: ${last_row['MA50']:.2f}")
        print(f"  MA200: ${last_row['MA200']:.2f}")
        print(f"  MACD: {last_row['MACD']:.4f}")
        print(f"  ATR: ${last_row['ATR']:.2f}")
        print(f"  ADX: {last_row['ADX']:.2f}")
        
    except Exception as e:
        print(f"Error: {e}")


def example_indicator_signals():
    """Example 9: Generate trading signals from indicators."""
    print("\n" + "=" * 70)
    print("Example 9: Trading Signals from Indicators")
    print("=" * 70)
    
    try:
        df = get_stock_data('AAPL', '2023-01-01', '2024-01-01')
        
        # Calculate indicators
        df['RSI'] = calculate_rsi(df, period=14)
        df['MA50'] = calculate_ma(df, period=50)
        df['MA200'] = calculate_ma(df, period=200)
        
        # Generate signals
        df['RSI_Oversold'] = df['RSI'] < 30
        df['RSI_Overbought'] = df['RSI'] > 70
        df['MA_Bullish'] = df['MA50'] > df['MA200']
        
        # Combined signal
        df['Buy_Signal'] = df['RSI_Oversold'] & df['MA_Bullish']
        df['Sell_Signal'] = df['RSI_Overbought'] & ~df['MA_Bullish']
        
        print(f"\nFetched {len(df)} days of AAPL data")
        
        print("\nSignal Summary:")
        print(f"  Buy signals (RSI < 30 AND MA50 > MA200): {df['Buy_Signal'].sum()}")
        print(f"  Sell signals (RSI > 70 AND MA50 <= MA200): {df['Sell_Signal'].sum()}")
        
        print("\nRecent signals (last 20 rows):")
        signal_df = df[['close', 'RSI', 'MA50', 'MA200', 'Buy_Signal', 'Sell_Signal']].tail(20)
        print(signal_df)
        
    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    print("\n" + "=" * 70)
    print("INDICATORS MODULE - USAGE EXAMPLES")
    print("=" * 70)
    
    # Run all examples
    example_basic_indicators()
    example_moving_averages()
    example_macd()
    example_bollinger_bands()
    example_volatility_indicators()
    example_stochastic()
    example_adx()
    example_all_indicators()
    example_indicator_signals()
    
    print("\n" + "=" * 70)
    print("Examples completed!")
    print("=" * 70)
