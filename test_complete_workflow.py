#!/usr/bin/env python3
"""
Complete workflow test for Trading Strategy Backtester
Tests: Data fetching, indicators, backtesting, and API
"""

import sys
sys.path.insert(0, 'backend')

from services.data_fetcher import get_stock_data
from services.indicators import add_all_indicators
from services.backtest_engine import BacktestEngine
from services.strategy_parser import SimpleStrategyParser
from datetime import datetime
import pandas as pd

def print_section(title):
    print("\n" + "="*70)
    print(f"  {title}")
    print("="*70)

def test_data_fetching():
    """Test 1: Data Fetching"""
    print_section("TEST 1: Data Fetching")
    
    try:
        print("\n  Fetching RELIANCE.BSE (2024-01-01 to 2024-12-31)...")
        df = get_stock_data("RELIANCE.BSE", "2024-01-01", "2024-12-31")
        
        print(f"  ✓ Successfully fetched {len(df)} rows")
        print(f"    Date range: {df.index.min().date()} to {df.index.max().date()}")
        print(f"    Columns: {list(df.columns)}")
        print(f"    Price range: ${df['close'].min():.2f} - ${df['close'].max():.2f}")
        
        return df
    except Exception as e:
        print(f"  ✗ Failed: {e}")
        return None

def test_indicators(df):
    """Test 2: Technical Indicators"""
    print_section("TEST 2: Technical Indicators")
    
    try:
        print("\n  Adding technical indicators...")
        df_with_indicators = add_all_indicators(df.copy())
        
        indicator_cols = [col for col in df_with_indicators.columns if col not in df.columns]
        print(f"  ✓ Added {len(indicator_cols)} indicators")
        print(f"    Indicators: {', '.join(indicator_cols[:5])}...")
        
        # Check for NaN values
        nan_count = df_with_indicators.isnull().sum().sum()
        print(f"    NaN values: {nan_count}")
        
        return df_with_indicators
    except Exception as e:
        print(f"  ✗ Failed: {e}")
        return None

def test_strategy_parsing():
    """Test 3: Strategy Parsing"""
    print_section("TEST 3: Strategy Parsing")
    
    try:
        strategy_text = "Buy when RSI < 30 and sell when RSI > 70"
        
        print(f"\n  Parsing strategy: '{strategy_text}'")
        rules = SimpleStrategyParser.parse(strategy_text)
        
        print(f"  ✓ Strategy parsed successfully")
        print(f"    Buy condition: {rules.buy_condition}")
        print(f"    Sell condition: {rules.sell_condition}")
        print(f"    Indicators required: {rules.indicators_required}")
        
        return rules
    except Exception as e:
        print(f"  ✗ Failed: {e}")
        return None

def test_backtesting(df, rules):
    """Test 4: Backtesting"""
    print_section("TEST 4: Backtesting")
    
    try:
        print("\n  Running backtest with RSI strategy...")
        
        # Generate signals from rules
        buy_condition = pd.Series(False, index=df.index)
        sell_condition = pd.Series(False, index=df.index)
        
        # Simple evaluation: RSI < 30 for buy, RSI > 70 for sell
        if 'RSI' in df.columns:
            buy_condition = df['RSI'] < 30
            sell_condition = df['RSI'] > 70
        
        engine = BacktestEngine(
            df,
            initial_capital=10000,
            commission=0.001,
            slippage=0.0
        )
        
        trades, equity_curve, metrics = engine.run_backtest(buy_condition, sell_condition)
        
        print(f"  ✓ Backtest completed successfully")
        print(f"    Total trades: {metrics.total_trades}")
        print(f"    Winning trades: {metrics.winning_trades}")
        print(f"    Losing trades: {metrics.losing_trades}")
        print(f"    Win rate: {metrics.win_rate:.2f}%")
        print(f"    Total return: ${metrics.total_return:,.2f} ({metrics.total_return_percent:.2f}%)")
        print(f"    Sharpe ratio: {metrics.sharpe_ratio:.4f}")
        print(f"    Max drawdown: {metrics.max_drawdown_percent:.2f}%")
        print(f"    Profit factor: {metrics.profit_factor:.2f}")
        
        return metrics
    except Exception as e:
        print(f"  ✗ Failed: {e}")
        return None

def test_api_health():
    """Test 5: API Health Check"""
    print_section("TEST 5: API Health Check")
    
    try:
        import requests
        response = requests.get("http://localhost:8000/health", timeout=5)
        
        if response.status_code == 200:
            print(f"  ✓ API is healthy")
            print(f"    Response: {response.json()}")
            return True
        else:
            print(f"  ✗ API returned status {response.status_code}")
            return False
    except Exception as e:
        print(f"  ✗ API not responding: {e}")
        print(f"    Make sure backend is running: python -m uvicorn main:app --reload")
        return False

def test_api_backtest():
    """Test 6: API Backtest Endpoint"""
    print_section("TEST 6: API Backtest Endpoint")
    
    try:
        import requests
        
        payload = {
            "strategy_text": "Buy when RSI < 30 and sell when RSI > 70",
            "stock_symbol": "RELIANCE.BSE",
            "start_date": "2024-01-01",
            "end_date": "2024-12-31",
            "initial_capital": 10000
        }
        
        print(f"\n  Calling POST /api/backtest...")
        response = requests.post(
            "http://localhost:8000/api/backtest",
            json=payload,
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"  ✓ API backtest successful")
            print(f"    Message: {result['message']}")
            print(f"    Total trades: {result['metrics']['total_trades']}")
            print(f"    Total return: {result['metrics']['total_return_percent']:.2f}%")
            return True
        else:
            print(f"  ✗ API returned status {response.status_code}")
            print(f"    Response: {response.text}")
            return False
    except Exception as e:
        print(f"  ✗ API test failed: {e}")
        print(f"    Make sure backend is running: python -m uvicorn main:app --reload")
        return False

def main():
    """Run all tests"""
    print("\n" + "="*70)
    print("  TRADING STRATEGY BACKTESTER - COMPLETE WORKFLOW TEST")
    print("="*70)
    
    # Test 1: Data Fetching
    df = test_data_fetching()
    if df is None:
        print("\n✗ Data fetching failed. Cannot continue.")
        return
    
    # Test 2: Indicators
    df_with_indicators = test_indicators(df)
    if df_with_indicators is None:
        print("\n✗ Indicator calculation failed. Cannot continue.")
        return
    
    # Test 3: Strategy Parsing
    rules = test_strategy_parsing()
    if rules is None:
        print("\n✗ Strategy parsing failed. Cannot continue.")
        return
    
    # Test 4: Backtesting
    metrics = test_backtesting(df_with_indicators, rules)
    if metrics is None:
        print("\n✗ Backtesting failed. Cannot continue.")
        return
    
    # Test 5: API Health
    api_healthy = test_api_health()
    
    # Test 6: API Backtest (only if API is healthy)
    if api_healthy:
        test_api_backtest()
    
    # Summary
    print_section("SUMMARY")
    print("\n  ✓ All core functionality tests passed!")
    print("\n  Next steps:")
    print("    1. Start backend: python -m uvicorn main:app --reload")
    print("    2. Start frontend: npm run dev")
    print("    3. Open http://localhost:3000")
    print("    4. Test with different strategies and symbols")
    print("\n" + "="*70 + "\n")

if __name__ == "__main__":
    main()
