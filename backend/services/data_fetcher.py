import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, date
from typing import Optional, Union

def get_stock_data(
    symbol: str,
    start_date: Union[str, date],
    end_date: Union[str, date]
) -> pd.DataFrame:
    """
    Fetch historical stock data from Yahoo Finance.
    
    Args:
        symbol: Stock ticker symbol (e.g., 'AAPL', 'GOOGL')
        start_date: Start date (YYYY-MM-DD format or date object)
        end_date: End date (YYYY-MM-DD format or date object)
        
    Returns:
        pandas DataFrame with columns: date, open, high, low, close, volume
        Indexed by date and sorted chronologically
        
    Raises:
        ValueError: If symbol not found or no data available
        Exception: If data fetch fails
        
    Example:
        >>> df = get_stock_data('AAPL', '2023-01-01', '2024-01-01')
        >>> print(df.head())
        >>> print(df.info())
    """
    try:
        # Convert string dates to datetime if needed
        if isinstance(start_date, str):
            start_date = pd.to_datetime(start_date).date()
        if isinstance(end_date, str):
            end_date = pd.to_datetime(end_date).date()
        
        # Fetch data from Yahoo Finance
        data = yf.download(
            symbol,
            start=start_date,
            end=end_date,
            progress=False
        )
        
        if data.empty:
            raise ValueError(f"No data found for symbol '{symbol}' in date range {start_date} to {end_date}")
        
        # Reset index to make date a column
        data = data.reset_index()
        
        # Standardize column names to lowercase
        data.columns = [col.lower() for col in data.columns]
        
        # Ensure date column is datetime
        data['date'] = pd.to_datetime(data['date'])
        
        # Select and reorder required columns
        required_cols = ['date', 'open', 'high', 'low', 'close', 'volume']
        data = data[required_cols]
        
        # Clean data: remove rows with NaN values
        data = data.dropna()
        
        # Set date as index
        data = data.set_index('date')
        
        # Sort by date (ascending)
        data = data.sort_index()
        
        # Convert volume to integer
        data['volume'] = data['volume'].astype(int)
        
        # Round price columns to 2 decimals
        for col in ['open', 'high', 'low', 'close']:
            data[col] = data[col].round(2)
        
        return data
    
    except ValueError as e:
        raise ValueError(f"Data validation error for {symbol}: {str(e)}")
    except Exception as e:
        raise Exception(f"Error fetching data for {symbol}: {str(e)}")


def validate_stock_data(df: pd.DataFrame) -> bool:
    """
    Validate that DataFrame has required columns and structure.
    
    Args:
        df: DataFrame to validate
        
    Returns:
        True if valid, False otherwise
    """
    required_cols = ['open', 'high', 'low', 'close', 'volume']
    
    # Check columns exist
    if not all(col in df.columns for col in required_cols):
        return False
    
    # Check index is datetime
    if not isinstance(df.index, pd.DatetimeIndex):
        return False
    
    # Check no NaN values
    if df.isnull().any().any():
        return False
    
    return True


def get_multiple_stocks(
    symbols: list,
    start_date: Union[str, date],
    end_date: Union[str, date]
) -> dict:
    """
    Fetch historical data for multiple stocks.
    
    Args:
        symbols: List of stock ticker symbols
        start_date: Start date
        end_date: End date
        
    Returns:
        Dictionary with symbol as key and DataFrame as value
    """
    data = {}
    for symbol in symbols:
        try:
            data[symbol] = get_stock_data(symbol, start_date, end_date)
        except Exception as e:
            print(f"Failed to fetch {symbol}: {str(e)}")
    
    return data


class DataFetcher:
    """Legacy class interface for backward compatibility."""
    
    @staticmethod
    def fetch_historical_data(
        symbol: str,
        start_date: date,
        end_date: date
    ) -> pd.DataFrame:
        """
        Fetch historical OHLCV data from Yahoo Finance.
        
        Args:
            symbol: Stock ticker symbol
            start_date: Start date for data
            end_date: End date for data
            
        Returns:
            DataFrame with OHLCV data
        """
        data = get_stock_data(symbol, start_date, end_date)
        data = data.reset_index()
        return data
    
    @staticmethod
    def validate_data(df: pd.DataFrame) -> bool:
        """Validate that data has required columns."""
        required_cols = ['date', 'open', 'high', 'low', 'close', 'volume']
        return all(col in df.columns for col in required_cols)
