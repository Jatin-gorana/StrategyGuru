import pandas as pd
import numpy as np

class Indicators:
    @staticmethod
    def calculate_rsi(data: pd.DataFrame, period: int = 14) -> pd.Series:
        """Calculate Relative Strength Index."""
        delta = data['close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        return rsi
    
    @staticmethod
    def calculate_sma(data: pd.DataFrame, period: int) -> pd.Series:
        """Calculate Simple Moving Average."""
        return data['close'].rolling(window=period).mean()
    
    @staticmethod
    def calculate_ema(data: pd.DataFrame, period: int) -> pd.Series:
        """Calculate Exponential Moving Average."""
        return data['close'].ewm(span=period, adjust=False).mean()
    
    @staticmethod
    def calculate_macd(data: pd.DataFrame) -> tuple:
        """Calculate MACD (12, 26, 9)."""
        ema12 = data['close'].ewm(span=12, adjust=False).mean()
        ema26 = data['close'].ewm(span=26, adjust=False).mean()
        macd = ema12 - ema26
        signal = macd.ewm(span=9, adjust=False).mean()
        histogram = macd - signal
        return macd, signal, histogram
    
    @staticmethod
    def calculate_bollinger_bands(data: pd.DataFrame, period: int = 20, std_dev: int = 2) -> tuple:
        """Calculate Bollinger Bands."""
        sma = data['close'].rolling(window=period).mean()
        std = data['close'].rolling(window=period).std()
        upper = sma + (std * std_dev)
        lower = sma - (std * std_dev)
        return upper, sma, lower
    
    @staticmethod
    def calculate_atr(data: pd.DataFrame, period: int = 14) -> pd.Series:
        """Calculate Average True Range."""
        high_low = data['high'] - data['low']
        high_close = abs(data['high'] - data['close'].shift())
        low_close = abs(data['low'] - data['close'].shift())
        
        tr = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)
        atr = tr.rolling(window=period).mean()
        return atr
import pandas as pd
import numpy as np
from typing import Tuple, Optional


def calculate_rsi(data: pd.DataFrame, period: int = 14) -> pd.Series:
    """
    Calculate Relative Strength Index (RSI).
    
    RSI measures the magnitude of recent price changes to evaluate
    overbought or oversold conditions. Range: 0-100
    - RSI > 70: Overbought
    - RSI < 30: Oversold
    
    Args:
        data: DataFrame with 'close' column
        period: RSI period (default: 14)
        
    Returns:
        Series with RSI values
    """
    delta = data['close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
    
    rs = gain / loss
    rsi = 100 - (100 / (1 + rs))
    return rsi


def calculate_ma(data: pd.DataFrame, period: int) -> pd.Series:
    """
    Calculate Simple Moving Average (SMA).
    
    Args:
        data: DataFrame with 'close' column
        period: MA period
        
    Returns:
        Series with SMA values
    """
    return data['close'].rolling(window=period).mean()


def calculate_ema(data: pd.DataFrame, period: int) -> pd.Series:
    """
    Calculate Exponential Moving Average (EMA).
    
    EMA gives more weight to recent prices.
    
    Args:
        data: DataFrame with 'close' column
        period: EMA period
        
    Returns:
        Series with EMA values
    """
    return data['close'].ewm(span=period, adjust=False).mean()


def calculate_macd(data: pd.DataFrame, fast: int = 12, slow: int = 26, signal: int = 9) -> Tuple[pd.Series, pd.Series, pd.Series]:
    """
    Calculate MACD (Moving Average Convergence Divergence).
    
    MACD is a trend-following momentum indicator that shows the relationship
    between two moving averages.
    
    Args:
        data: DataFrame with 'close' column
        fast: Fast EMA period (default: 12)
        slow: Slow EMA period (default: 26)
        signal: Signal line period (default: 9)
        
    Returns:
        Tuple of (MACD line, Signal line, Histogram)
    """
    ema_fast = data['close'].ewm(span=fast, adjust=False).mean()
    ema_slow = data['close'].ewm(span=slow, adjust=False).mean()
    macd_line = ema_fast - ema_slow
    signal_line = macd_line.ewm(span=signal, adjust=False).mean()
    histogram = macd_line - signal_line
    
    return macd_line, signal_line, histogram


def calculate_bollinger_bands(
    data: pd.DataFrame,
    period: int = 20,
    std_dev: float = 2
) -> Tuple[pd.Series, pd.Series, pd.Series]:
    """
    Calculate Bollinger Bands.
    
    Bollinger Bands consist of a middle band (SMA) and upper/lower bands
    (SMA ± standard deviations).
    
    Args:
        data: DataFrame with 'close' column
        period: Period for SMA (default: 20)
        std_dev: Number of standard deviations (default: 2)
        
    Returns:
        Tuple of (Upper band, Middle band, Lower band)
    """
    sma = data['close'].rolling(window=period).mean()
    std = data['close'].rolling(window=period).std()
    upper_band = sma + (std * std_dev)
    lower_band = sma - (std * std_dev)
    
    return upper_band, sma, lower_band


def calculate_atr(data: pd.DataFrame, period: int = 14) -> pd.Series:
    """
    Calculate Average True Range (ATR).
    
    ATR measures market volatility by calculating the average of true ranges.
    
    Args:
        data: DataFrame with 'high', 'low', 'close' columns
        period: ATR period (default: 14)
        
    Returns:
        Series with ATR values
    """
    high_low = data['high'] - data['low']
    high_close = abs(data['high'] - data['close'].shift())
    low_close = abs(data['low'] - data['close'].shift())
    
    true_range = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)
    atr = true_range.rolling(window=period).mean()
    
    return atr


def calculate_stochastic(
    data: pd.DataFrame,
    period: int = 14,
    smooth_k: int = 3,
    smooth_d: int = 3
) -> Tuple[pd.Series, pd.Series]:
    """
    Calculate Stochastic Oscillator.
    
    Stochastic compares a particular closing price to a range of prices
    over a set period.
    
    Args:
        data: DataFrame with 'high', 'low', 'close' columns
        period: Lookback period (default: 14)
        smooth_k: K line smoothing (default: 3)
        smooth_d: D line smoothing (default: 3)
        
    Returns:
        Tuple of (K line, D line)
    """
    low_min = data['low'].rolling(window=period).min()
    high_max = data['high'].rolling(window=period).max()
    
    k_percent = 100 * ((data['close'] - low_min) / (high_max - low_min))
    k_line = k_percent.rolling(window=smooth_k).mean()
    d_line = k_line.rolling(window=smooth_d).mean()
    
    return k_line, d_line


def calculate_adx(data: pd.DataFrame, period: int = 14) -> pd.Series:
    """
    Calculate Average Directional Index (ADX).
    
    ADX measures trend strength without regard to direction.
    
    Args:
        data: DataFrame with 'high', 'low', 'close' columns
        period: ADX period (default: 14)
        
    Returns:
        Series with ADX values
    """
    # Calculate directional movements
    up_move = data['high'].diff()
    down_move = -data['low'].diff()
    
    pos_dm = up_move.where((up_move > down_move) & (up_move > 0), 0)
    neg_dm = down_move.where((down_move > up_move) & (down_move > 0), 0)
    
    # Calculate true range
    high_low = data['high'] - data['low']
    high_close = abs(data['high'] - data['close'].shift())
    low_close = abs(data['low'] - data['close'].shift())
    tr = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)
    
    # Calculate directional indicators
    atr_val = tr.rolling(window=period).mean()
    pos_di = 100 * (pos_dm.rolling(window=period).mean() / atr_val)
    neg_di = 100 * (neg_dm.rolling(window=period).mean() / atr_val)
    
    # Calculate ADX
    di_diff = abs(pos_di - neg_di)
    di_sum = pos_di + neg_di
    dx = 100 * (di_diff / di_sum)
    adx = dx.rolling(window=period).mean()
    
    return adx


def add_all_indicators(data: pd.DataFrame) -> pd.DataFrame:
    """
    Add all common indicators to DataFrame.
    
    Args:
        data: DataFrame with OHLCV data
        
    Returns:
        DataFrame with added indicator columns
    """
    df = data.copy()
    
    # Momentum indicators
    df['RSI'] = calculate_rsi(df, period=14)
    df['MA50'] = calculate_ma(df, period=50)
    df['MA200'] = calculate_ma(df, period=200)
    
    # Trend indicators
    df['EMA12'] = calculate_ema(df, period=12)
    df['EMA20'] = calculate_ema(df, period=20)
    df['EMA26'] = calculate_ema(df, period=26)
    df['SMA20'] = calculate_ma(df, period=20)
    
    macd, signal, histogram = calculate_macd(df)
    df['MACD'] = macd
    df['MACD_Signal'] = signal
    df['MACD_Histogram'] = histogram
    
    # Volatility indicators
    upper_bb, middle_bb, lower_bb = calculate_bollinger_bands(df, period=20, std_dev=2)
    df['BB_Upper'] = upper_bb
    df['BB_Middle'] = middle_bb
    df['BB_Lower'] = lower_bb
    df['ATR'] = calculate_atr(df, period=14)
    
    # Oscillators
    k_line, d_line = calculate_stochastic(df, period=14)
    df['Stoch_K'] = k_line
    df['Stoch_D'] = d_line
    
    df['ADX'] = calculate_adx(df, period=14)
    
    return df


class Indicators:
    """Legacy class interface for backward compatibility."""
    
    @staticmethod
    def calculate_rsi(data: pd.DataFrame, period: int = 14) -> pd.Series:
        """Calculate Relative Strength Index."""
        return calculate_rsi(data, period)
    
    @staticmethod
    def calculate_sma(data: pd.DataFrame, period: int) -> pd.Series:
        """Calculate Simple Moving Average."""
        return calculate_ma(data, period)
    
    @staticmethod
    def calculate_ema(data: pd.DataFrame, period: int) -> pd.Series:
        """Calculate Exponential Moving Average."""
        return calculate_ema(data, period)
    
    @staticmethod
    def calculate_macd(data: pd.DataFrame) -> tuple:
        """Calculate MACD (12, 26, 9)."""
        return calculate_macd(data)
    
    @staticmethod
    def calculate_bollinger_bands(data: pd.DataFrame, period: int = 20, std_dev: int = 2) -> tuple:
        """Calculate Bollinger Bands."""
        return calculate_bollinger_bands(data, period, std_dev)
    
    @staticmethod
    def calculate_atr(data: pd.DataFrame, period: int = 14) -> pd.Series:
        """Calculate Average True Range."""
        return calculate_atr(data, period)
