import pandas as pd
import numpy as np
from datetime import datetime, date, timedelta
from typing import Optional, Union
import time
import logging
import requests
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

logger = logging.getLogger(__name__)

def _fetch_from_alpha_vantage(
    symbol: str,
    start_date: date,
    end_date: date,
    api_key: str = "demo"
) -> Optional[pd.DataFrame]:
    """
    Fetch daily data from Alpha Vantage TIME_SERIES_DAILY endpoint.
    Works with both US stocks (AAPL) and international stocks (RELIANCE.BSE).
    
    Note: Demo API key has 5 requests per minute limit. For production, use a paid API key.
    """
    try:
        logger.info(f"Fetching daily data for {symbol} from Alpha Vantage (API key: {api_key[:4]}...)")
        
        url = "https://www.alphavantage.co/query"
        params = {
            "function": "TIME_SERIES_DAILY",
            "symbol": symbol,
            "outputsize": "full",
            "apikey": api_key
        }
        
        # Retry logic for rate limiting
        max_retries = 3
        for attempt in range(max_retries):
            try:
                logger.info(f"Fetching daily data (attempt {attempt + 1}/{max_retries})")
                response = requests.get(url, params=params, timeout=30)
                response.raise_for_status()
                data = response.json()
                
                # Check for errors
                if "Error Message" in data:
                    logger.error(f"Alpha Vantage error: {data.get('Error Message')}")
                    return None
                
                if "Note" in data:
                    logger.warning(f"Alpha Vantage rate limit: {data.get('Note')}")
                    if attempt < max_retries - 1:
                        wait_time = 15 * (attempt + 1)  # Increased wait time for demo key
                        logger.info(f"Rate limited, waiting {wait_time} seconds...")
                        time.sleep(wait_time)
                        continue
                    return None
                
                # Check for Information key (indicates demo key limitation)
                if "Information" in data and len(data) == 1:
                    logger.warning(f"Alpha Vantage returned only Information: {data.get('Information')}")
                    if attempt < max_retries - 1:
                        wait_time = 15 * (attempt + 1)
                        logger.info(f"Waiting {wait_time} seconds before retry...")
                        time.sleep(wait_time)
                        continue
                    return None
                
                # Check for time series data - handle both US and international formats
                time_series_key = None
                for key in data.keys():
                    if "Time Series" in key and "Daily" in key:
                        time_series_key = key
                        break
                
                if time_series_key is None:
                    logger.warning(f"No daily time series data found. Response keys: {list(data.keys())}")
                    return None
                
                time_series = data[time_series_key]
                logger.info(f"Found {len(time_series)} daily data points")
                
                # Convert to DataFrame
                df_data = []
                for date_str, values in time_series.items():
                    try:
                        # Parse date
                        date_obj = pd.to_datetime(date_str).date()
                        
                        # Extract OHLCV - handle both formats
                        open_price = float(values.get('1. open', 0))
                        high_price = float(values.get('2. high', 0))
                        low_price = float(values.get('3. low', 0))
                        close_price = float(values.get('4. close', 0))
                        volume = int(float(values.get('5. volume', 0)))
                        
                        # Skip if any price is 0
                        if open_price == 0 or close_price == 0:
                            continue
                        
                        df_data.append({
                            'date': pd.to_datetime(date_str),
                            'open': open_price,
                            'high': high_price,
                            'low': low_price,
                            'close': close_price,
                            'volume': volume
                        })
                    
                    except (KeyError, ValueError) as e:
                        logger.debug(f"Error parsing daily row {date_str}: {e}")
                        continue
                
                if not df_data:
                    logger.warning("No valid data from Alpha Vantage")
                    return None
                
                df = pd.DataFrame(df_data)
                df = df.sort_values('date')
                
                # Filter by date range
                df = df[(df['date'].dt.date >= start_date) & (df['date'].dt.date <= end_date)]
                
                if df.empty:
                    logger.warning(f"No data in date range {start_date} to {end_date}")
                    return None
                
                df = df.set_index('date')
                logger.info(f"✓ Successfully fetched {len(df)} daily bars for {symbol}")
                return df
                
            except requests.exceptions.Timeout:
                logger.warning(f"Timeout on attempt {attempt + 1}/{max_retries}")
                if attempt < max_retries - 1:
                    time.sleep(2 ** attempt)
                    continue
                return None
            except requests.exceptions.RequestException as e:
                logger.warning(f"Request error: {str(e)}")
                if attempt < max_retries - 1:
                    time.sleep(2 ** attempt)
                    continue
                return None
        
        return None
        
    except Exception as e:
        logger.error(f"Alpha Vantage fetch failed: {str(e)}")
        return None

def get_stock_data(
    symbol: str,
    start_date: Union[str, date],
    end_date: Union[str, date]
) -> pd.DataFrame:
    """
    Fetch historical stock data from Alpha Vantage TIME_SERIES_DAILY.
    Works with US stocks (AAPL, GOOGL) and international stocks (RELIANCE.BSE).
    
    Args:
        symbol: Stock ticker symbol (e.g., 'AAPL', 'RELIANCE.BSE')
        start_date: Start date (YYYY-MM-DD format or date object)
        end_date: End date (YYYY-MM-DD format or date object)
        
    Returns:
        pandas DataFrame with columns: date, open, high, low, close, volume
        Indexed by date and sorted chronologically
    
    Note: Demo API key has 5 requests per minute limit. For production, get a free API key at:
    https://www.alphavantage.co/support/#api-key
    """
    try:
        # Convert string dates to datetime if needed
        if isinstance(start_date, str):
            start_date = pd.to_datetime(start_date).date()
        if isinstance(end_date, str):
            end_date = pd.to_datetime(end_date).date()
        
        # Validate dates
        if start_date >= end_date:
            raise ValueError("Start date must be before end date")
        
        # Normalize symbol to uppercase
        symbol = symbol.upper().strip()
        
        logger.info(f"Fetching {symbol} from {start_date} to {end_date}")
        
        # Get API key from environment
        av_api_key = os.getenv("ALPHA_VANTAGE_API_KEY", "demo").strip()
        if not av_api_key:
            av_api_key = "demo"
        
        logger.info(f"Using API key: {av_api_key[:4]}...")
        av_data = _fetch_from_alpha_vantage(symbol, start_date, end_date, api_key=av_api_key)
        
        if av_data is not None and not av_data.empty:
            return av_data
        
        # All methods failed
        raise ValueError(f"Failed to fetch data for {symbol}. Check: 1) Symbol exists, 2) Date range valid, 3) API rate limits (demo key: 5 req/min)")
    
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
    """Validate DataFrame structure."""
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
    """Fetch data for multiple stocks."""
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
        """Fetch historical OHLCV data."""
        data = get_stock_data(symbol, start_date, end_date)
        data = data.reset_index()
        return data
    
    @staticmethod
    def validate_data(df: pd.DataFrame) -> bool:
        """Validate that data has required columns."""
        required_cols = ['date', 'open', 'high', 'low', 'close', 'volume']
        return all(col in df.columns for col in required_cols)
