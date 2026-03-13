#!/usr/bin/env python
"""
Script to fix the database by adding missing columns or recreating if needed
"""
import asyncio
import os
import sys
from sqlalchemy import text, inspect
from sqlalchemy.ext.asyncio import create_async_engine
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql+asyncpg://postgres:1234@localhost:5432/trading_backtester")

async def check_and_fix_database():
    """Check if return_percent column exists, add it if missing"""
    
    engine = create_async_engine(DATABASE_URL)
    
    try:
        async with engine.connect() as conn:
            # Check if return_percent column exists
            result = await conn.execute(text("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name='backtests' AND column_name='return_percent'
            """))
            
            column_exists = result.fetchone() is not None
            
            if column_exists:
                print("✅ return_percent column already exists")
            else:
                print("❌ return_percent column missing, adding it...")
                await conn.execute(text("""
                    ALTER TABLE backtests 
                    ADD COLUMN return_percent FLOAT NULL
                """))
                await conn.commit()
                print("✅ Added return_percent column successfully")
            
            # Check other required columns
            required_columns = [
                'id', 'user_id', 'strategy_id', 'stock_symbol', 
                'start_date', 'end_date', 'initial_capital',
                'total_return', 'sharpe_ratio', 'max_drawdown',
                'max_drawdown_percent', 'win_rate', 'profit_factor',
                'total_trades', 'created_at'
            ]
            
            result = await conn.execute(text("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name='backtests'
            """))
            
            existing_columns = {row[0] for row in result.fetchall()}
            missing_columns = [col for col in required_columns if col not in existing_columns]
            
            if missing_columns:
                print(f"⚠️  Missing columns: {missing_columns}")
                print("Consider running recreate_db.py to fully recreate the database")
            else:
                print("✅ All required columns exist")
    
    finally:
        await engine.dispose()

if __name__ == "__main__":
    asyncio.run(check_and_fix_database())
