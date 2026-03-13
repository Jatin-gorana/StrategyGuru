"""
Test DSL Security - Verify malicious code is blocked
"""

import requests
import json

BASE_URL = "http://localhost:8000"

def test_strategy(strategy_text, description):
    """Test a strategy and print results"""
    print(f"\n{'='*70}")
    print(f"TEST: {description}")
    print(f"{'='*70}")
    print(f"Strategy: {strategy_text}")
    print(f"-" * 70)
    
    payload = {
        "strategy_text": strategy_text,
        "stock_symbol": "AAPL",
        "start_date": "2023-01-01",
        "end_date": "2024-01-01",
        "initial_capital": 10000
    }
    
    try:
        response = requests.post(f"{BASE_URL}/api/backtest", json=payload, timeout=30)
        
        if response.status_code == 200:
            print("✅ SUCCESS - Strategy executed")
            data = response.json()
            print(f"   Return: {data['metrics']['total_return_percent']:.2f}%")
            print(f"   Trades: {data['metrics']['total_trades']}")
        else:
            print(f"❌ ERROR - Status: {response.status_code}")
            print(f"   Message: {response.json()['detail']}")
    
    except Exception as e:
        print(f"❌ EXCEPTION: {str(e)}")

# Test Cases
print("\n" + "="*70)
print("DSL SECURITY TESTS")
print("="*70)

# Test 1: Legitimate strategy
test_strategy(
    "Buy when RSI < 30, Sell when RSI > 70",
    "Legitimate Strategy (Should Work)"
)

# Test 2: Malicious - import
test_strategy(
    "Buy when RSI < 30 and sell when RSI > 70, import os",
    "Malicious: import statement (Should Block)"
)

# Test 3: Malicious - password
test_strategy(
    "Buy when RSI < 30 and sell when RSI > 70, get db password",
    "Malicious: password keyword (Should Block)"
)

# Test 4: Malicious - os.system
test_strategy(
    "Buy when RSI < 30, os.system('delete all files')",
    "Malicious: os.system call (Should Block)"
)

# Test 5: Malicious - exec
test_strategy(
    "Buy when RSI < 30, exec('malicious code')",
    "Malicious: exec call (Should Block)"
)

# Test 6: Complex legitimate strategy
test_strategy(
    "Buy when RSI < 30 AND price > SMA(200), Sell when RSI > 70 OR MACD > Signal",
    "Complex Legitimate Strategy (Should Work)"
)

# Test 7: Malicious - database
test_strategy(
    "Buy when RSI < 30, query database for password",
    "Malicious: database keyword (Should Block)"
)

# Test 8: Malicious - eval
test_strategy(
    "Buy when RSI < 30, eval('malicious')",
    "Malicious: eval call (Should Block)"
)

print("\n" + "="*70)
print("TESTS COMPLETE")
print("="*70)
