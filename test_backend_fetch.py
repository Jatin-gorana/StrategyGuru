import sys
sys.path.insert(0, 'backend')

from services.data_fetcher import get_stock_data
from datetime import datetime
import time

print("Testing backend data fetcher with delays...")

try:
    print("\n1. Testing RELIANCE.BSE (international stock)...")
    df = get_stock_data("RELIANCE.BSE", "2024-01-01", "2024-12-31")
    print(f"✓ Successfully fetched {len(df)} rows for RELIANCE.BSE")
    print(f"  Date range: {df.index.min()} to {df.index.max()}")
except Exception as e:
    print(f"✗ Failed: {e}")

print("\nWaiting 20 seconds before next request (demo key rate limit: 5 req/min)...")
time.sleep(20)

try:
    print("\n2. Testing AAPL (US stock)...")
    df = get_stock_data("AAPL", "2024-01-01", "2024-12-31")
    print(f"✓ Successfully fetched {len(df)} rows for AAPL")
    print(f"  Date range: {df.index.min()} to {df.index.max()}")
except Exception as e:
    print(f"✗ Failed: {e}")

print("\nDone!")
