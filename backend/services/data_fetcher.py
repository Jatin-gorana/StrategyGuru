import pandas as pd
import numpy as np
from datetime import datetime, date, timedelta
from typing import Optional, Union
import logging
from io import StringIO

logger = logging.getLogger(__name__)


def _format_symbol_for_stooq(symbol: str) -> str:
    """
    Convert symbol to Stooq format.
    
    Examples:
        AAPL -> aapl.us
        GOOGL -> googl.us
        RELIANCE.BSE -> reliance.in (or keep as is if already formatted)
    
    Args:
        symbol: Stock ticker symbol
        
    Returns:
        Formatted symbol for Stooq API
    """
    symbol = symbol.strip().upper()
    
    # If already has a dot (e.g., RELIANCE.BSE), convert to lowercase
    if '.' in symbol:
        return symbol.lower()
    
    # Otherwise, assume US stock and add .us suffix
    return f"{symbol.lower()}.us"


def _fetch_from_stooq(
    symbol: str,
    start_date: date,
    end_date: date
) -> Optional[pd.DataFrame]:
    """
    Fetch daily data from Stooq CSV endpoint.
    
    Args:
        symbol: Stock ticker symbol (will be formatted for Stooq)
        start_date: Start date (date object)
        end_date: End date (date object)
        
    Returns:
        DataFrame with OHLCV data or None if fetch fails
    """
    try:
        # Format symbol for Stooq
        stooq_symbol = _format_symbol_for_stooq(symbol)
        logger.info(f"Fetching data for {symbol} (Stooq: {stooq_symbol})")
        
        # Construct Stooq CSV URL
        url = f"https://stooq.com/q/d/l/?s={stooq_symbol}&i=d"
        logger.info(f"Fetching from: {url}")
        
        # Fetch CSV data
        df = pd.read_csv(url)
        
        if df.empty:
            logger.warning(f"No data returned from Stooq for {symbol}")
            return None
        
        logger.info(f"Fetched {len(df)} rows from Stooq")
        
        # Stooq CSV format: Date, Open, High, Low, Close, Volume
        # Column names are typically: Date, Open, High, Low, Close, Volume
        
        # Standardize column names to lowercase
        df.columns = [col.lower().strip() for col in df.columns]
        
        # Ensure required columns exist
        required_cols = ['date', 'open', 'high', 'low', 'close', 'volume']
        if not all(col in df.columns for col in required_cols):
            logger.error(f"Missing required columns. Found: {list(df.columns)}")
            return None
        
        # Convert date column to datetime
        df['date'] = pd.to_datetime(df['date'])
        
        # Filter by date range
        df = df[(df['date'].dt.date >= start_date) & (df['date'].dt.date <= end_date)]
        
        if df.empty:
            logger.warning(f"No data in date range {start_date} to {end_date}")
            return None
        
        # Sort by date in ascending order
        df = df.sort_values('date')
        
        # Select and reorder columns
        df = df[['date', 'open', 'high', 'low', 'close', 'volume']]
        
        # Convert data types
        df['open'] = pd.to_numeric(df['open'], errors='coerce')
        df['high'] = pd.to_numeric(df['high'], errors='coerce')
        df['low'] = pd.to_numeric(df['low'], errors='coerce')
        df['close'] = pd.to_numeric(df['close'], errors='coerce')
        df['volume'] = pd.to_numeric(df['volume'], errors='coerce').fillna(0).astype(int)
        
        # Remove rows with NaN prices
        df = df.dropna(subset=['open', 'high', 'low', 'close'])
        
        if df.empty:
            logger.warning("No valid data after cleaning")
            return None
        
        # Set date as index
        df = df.set_index('date')
        
        logger.info(f"✓ Successfully fetched {len(df)} daily bars for {symbol}")
        return df
        
    except Exception as e:
        logger.error(f"Stooq fetch failed for {symbol}: {str(e)}")
        return None


def get_stock_data(
    symbol: str,
    start_date: Union[str, date],
    end_date: Union[str, date]
) -> pd.DataFrame:
    """
    Fetch historical stock data from Stooq.
    
    Args:
        symbol: Stock ticker symbol (e.g., 'AAPL', 'GOOGL', 'RELIANCE.BSE')
        start_date: Start date (YYYY-MM-DD format or date object)
        end_date: End date (YYYY-MM-DD format or date object)
        
    Returns:
        pandas DataFrame with columns: open, high, low, close, volume
        Indexed by date and sorted chronologically
        
    Raises:
        ValueError: If data cannot be fetched or is invalid
    """
    try:
        # Convert string dates to date objects if needed
        if isinstance(start_date, str):
            start_date = pd.to_datetime(start_date).date()
        if isinstance(end_date, str):
            end_date = pd.to_datetime(end_date).date()
        
        # Validate dates
        if start_date >= end_date:
            raise ValueError("Start date must be before end date")
        
        # Normalize symbol
        symbol = symbol.strip()
        
        logger.info(f"Fetching {symbol} from {start_date} to {end_date}")
        
        # Fetch data from Stooq
        df = _fetch_from_stooq(symbol, start_date, end_date)
        
        if df is not None and not df.empty:
            return df
        
        # If fetch failed
        raise ValueError(f"Failed to fetch data for {symbol}. Check: 1) Symbol exists, 2) Date range valid, 3) Internet connection")
    
    except ValueError as e:
        raise ValueError(f"Data validation error for {symbol}: {str(e)}")
    except Exception as e:
        raise Exception(f"Error fetching data for {symbol}: {str(e)}")


def _process_data(data: pd.DataFrame, symbol: str) -> pd.DataFrame:
    """Process raw data into standard format."""
    try:
        data = data.reset_index()
        data.columns = [col.lower() for col in data.columns]
        
        if 'date' in data.columns:
            data['date'] = pd.to_datetime(data['date'])
        
        required_cols = ['date', 'open', 'high', 'low', 'close', 'volume']
        data = data[required_cols]
        data = data.dropna()
        
        if data.empty:
            raise ValueError("No valid data after cleaning")
        
        data = data.set_index('date')
        data = data.sort_index()
        data['volume'] = data['volume'].astype(int)
        
        for col in ['open', 'high', 'low', 'close']:
            data[col] = data[col].round(2)
        
        return data
    
    except Exception as e:
        raise ValueError(f"Error processing data for {symbol}: {str(e)}")


def validate_stock_data(df: pd.DataFrame) -> bool:
    """
    Validate DataFrame structure.
    
    Args:
        df: DataFrame to validate
        
    Returns:
        True if valid, False otherwise
    """
    required_cols = ['open', 'high', 'low', 'close', 'volume']
    
    if not all(col in df.columns for col in required_cols):
        return False
    
    if not isinstance(df.index, pd.DatetimeIndex):
        return False
    
    if df.isnull().any().any():
        return False
    
    return True


def get_multiple_stocks(
    symbols: list,
    start_date: Union[str, date],
    end_date: Union[str, date]
) -> dict:
    """
    Fetch data for multiple stocks.
    
    Args:
        symbols: List of stock symbols
        start_date: Start date
        end_date: End date
        
    Returns:
        Dictionary mapping symbols to DataFrames
    """
    data = {}
    for symbol in symbols:
        try:
            data[symbol] = get_stock_data(symbol, start_date, end_date)
        except Exception as e:
            logger.warning(f"Failed to fetch {symbol}: {str(e)}")
    
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
        Fetch historical OHLCV data.
        
        Args:
            symbol: Stock ticker symbol
            start_date: Start date
            end_date: End date
            
        Returns:
            DataFrame with date, open, high, low, close, volume columns
        """
        data = get_stock_data(symbol, start_date, end_date)
        data = data.reset_index()
        return data
    
    @staticmethod
    def validate_data(df: pd.DataFrame) -> bool:
        """
        Validate that data has required columns.
        
        Args:
            df: DataFrame to validate
            
        Returns:
            True if valid, False otherwise
        """
        required_cols = ['date', 'open', 'high', 'low', 'close', 'volume']
        return all(col in df.columns for col in required_cols)
