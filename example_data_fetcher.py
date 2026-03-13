"""
Example usage of the data_fetcher module.

This script demonstrates how to use the get_stock_data function
to fetch and analyze historical stock data.
"""

from backend.services.data_fetcher import (
    get_stock_data,
    validate_stock_data,
    get_multiple_stocks
)
import pandas as pd


def example_single_stock():
    """Example 1: Fetch data for a single stock."""
    print("=" * 60)
    print("Example 1: Fetch Single Stock Data")
    print("=" * 60)
    
    try:
        # Fetch Apple stock data for 2023
        df = get_stock_data('AAPL', '2023-01-01', '2023-12-31')
        
        print(f"\nData shape: {df.shape}")
        print(f"Date range: {df.index.min()} to {df.index.max()}")
        print(f"\nFirst 5 rows:")
        print(df.head())
        print(f"\nLast 5 rows:")
        print(df.tail())
        print(f"\nData info:")
        print(df.info())
        print(f"\nBasic statistics:")
        print(df.describe())
        
    except Exception as e:
        print(f"Error: {e}")


def example_data_validation():
    """Example 2: Validate fetched data."""
    print("\n" + "=" * 60)
    print("Example 2: Data Validation")
    print("=" * 60)
    
    try:
        df = get_stock_data('GOOGL', '2023-06-01', '2023-12-31')
        
        is_valid = validate_stock_data(df)
        print(f"\nData validation result: {is_valid}")
        print(f"Columns: {list(df.columns)}")
        print(f"Index type: {type(df.index)}")
        print(f"Missing values: {df.isnull().sum().sum()}")
        
    except Exception as e:
        print(f"Error: {e}")


def example_multiple_stocks():
    """Example 3: Fetch data for multiple stocks."""
    print("\n" + "=" * 60)
    print("Example 3: Fetch Multiple Stocks")
    print("=" * 60)
    
    symbols = ['AAPL', 'GOOGL', 'MSFT', 'AMZN']
    
    try:
        data_dict = get_multiple_stocks(symbols, '2023-01-01', '2023-12-31')
        
        print(f"\nFetched data for {len(data_dict)} stocks:")
        for symbol, df in data_dict.items():
            print(f"\n{symbol}:")
            print(f"  Rows: {len(df)}")
            print(f"  Date range: {df.index.min().date()} to {df.index.max().date()}")
            print(f"  Close price range: ${df['close'].min():.2f} - ${df['close'].max():.2f}")
        
    except Exception as e:
        print(f"Error: {e}")


def example_data_analysis():
    """Example 4: Analyze stock data."""
    print("\n" + "=" * 60)
    print("Example 4: Data Analysis")
    print("=" * 60)
    
    try:
        df = get_stock_data('AAPL', '2023-01-01', '2023-12-31')
        
        # Calculate daily returns
        df['daily_return'] = df['close'].pct_change() * 100
        
        # Calculate price range
        df['price_range'] = df['high'] - df['low']
        
        # Calculate volume moving average
        df['volume_ma_20'] = df['volume'].rolling(window=20).mean()
        
        print(f"\nDaily return statistics:")
        print(f"  Mean: {df['daily_return'].mean():.4f}%")
        print(f"  Std Dev: {df['daily_return'].std():.4f}%")
        print(f"  Min: {df['daily_return'].min():.4f}%")
        print(f"  Max: {df['daily_return'].max():.4f}%")
        
        print(f"\nPrice range statistics:")
        print(f"  Mean: ${df['price_range'].mean():.2f}")
        print(f"  Max: ${df['price_range'].max():.2f}")
        
        print(f"\nVolume statistics:")
        print(f"  Mean: {df['volume'].mean():,.0f}")
        print(f"  Max: {df['volume'].max():,.0f}")
        
        print(f"\nSample data with calculated columns:")
        print(df[['close', 'daily_return', 'price_range', 'volume_ma_20']].head(10))
        
    except Exception as e:
        print(f"Error: {e}")


def example_date_formats():
    """Example 5: Different date format inputs."""
    print("\n" + "=" * 60)
    print("Example 5: Different Date Format Inputs")
    print("=" * 60)
    
    try:
        # String format
        print("\nUsing string dates (YYYY-MM-DD):")
        df1 = get_stock_data('MSFT', '2023-01-01', '2023-03-31')
        print(f"  Rows: {len(df1)}")
        
        # Date object format
        from datetime import date
        print("\nUsing date objects:")
        df2 = get_stock_data('MSFT', date(2023, 1, 1), date(2023, 3, 31))
        print(f"  Rows: {len(df2)}")
        
        print("\nBoth methods return identical data:", df1.equals(df2))
        
    except Exception as e:
        print(f"Error: {e}")


def example_error_handling():
    """Example 6: Error handling."""
    print("\n" + "=" * 60)
    print("Example 6: Error Handling")
    print("=" * 60)
    
    # Invalid symbol
    print("\nTrying invalid symbol 'INVALID':")
    try:
        df = get_stock_data('INVALID', '2023-01-01', '2023-12-31')
    except Exception as e:
        print(f"  Caught error: {e}")
    
    # Invalid date range
    print("\nTrying future date range:")
    try:
        df = get_stock_data('AAPL', '2025-01-01', '2025-12-31')
    except Exception as e:
        print(f"  Caught error: {e}")


if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("DATA FETCHER MODULE - USAGE EXAMPLES")
    print("=" * 60)
    
    # Run all examples
    example_single_stock()
    example_data_validation()
    example_multiple_stocks()
    example_data_analysis()
    example_date_formats()
    example_error_handling()
    
    print("\n" + "=" * 60)
    print("Examples completed!")
    print("=" * 60)
