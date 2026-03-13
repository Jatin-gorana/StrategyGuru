#!/usr/bin/env python
"""
Script to check the current database status and schema
"""
import asyncio
import os
from sqlalchemy import text, inspect
from sqlalchemy.ext.asyncio import create_async_engine
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql+asyncpg://postgres:1234@localhost:5432/trading_backtester")

async def check_database_status():
    """Check database status and schema"""
    
    engine = create_async_engine(DATABASE_URL)
    
    try:
        async with engine.connect() as conn:
            print("=" * 60)
            print("DATABASE STATUS CHECK")
            print("=" * 60)
            
            # Check if database exists
            try:
                result = await conn.execute(text("SELECT 1"))
                print("✅ Database connection: OK")
            except Exception as e:
                print(f"❌ Database connection: FAILED - {e}")
                return
            
            # Check tables
            print("\n📋 Tables:")
            result = await conn.execute(text("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public'
                ORDER BY table_name
            """))
            
            tables = [row[0] for row in result.fetchall()]
            if tables:
                for table in tables:
                    print(f"  ✅ {table}")
            else:
                print("  ❌ No tables found")
            
            # Check backtests table columns
            if 'backtests' in tables:
                print("\n📊 Backtests Table Columns:")
                result = await conn.execute(text("""
                    SELECT column_name, data_type, is_nullable
                    FROM information_schema.columns 
                    WHERE table_name='backtests'
                    ORDER BY ordinal_position
                """))
                
                columns = result.fetchall()
                required_columns = {
                    'id', 'user_id', 'strategy_id', 'stock_symbol',
                    'start_date', 'end_date', 'initial_capital',
                    'total_return', 'return_percent', 'sharpe_ratio',
                    'max_drawdown', 'max_drawdown_percent', 'win_rate',
                    'profit_factor', 'total_trades', 'created_at'
                }
                
                existing_columns = set()
                for col_name, col_type, is_nullable in columns:
                    existing_columns.add(col_name)
                    nullable = "NULL" if is_nullable == 'YES' else "NOT NULL"
                    print(f"  ✅ {col_name}: {col_type} ({nullable})")
                
                missing = required_columns - existing_columns
                if missing:
                    print(f"\n  ⚠️  Missing columns: {', '.join(sorted(missing))}")
                else:
                    print(f"\n  ✅ All required columns present")
            
            # Check row counts
            print("\n📈 Row Counts:")
            for table in tables:
                result = await conn.execute(text(f"SELECT COUNT(*) FROM {table}"))
                count = result.scalar()
                print(f"  {table}: {count} rows")
            
            print("\n" + "=" * 60)
    
    finally:
        await engine.dispose()

if __name__ == "__main__":
    asyncio.run(check_database_status())
