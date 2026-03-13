#!/usr/bin/env python
"""Verify database schema"""
import asyncio
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine
import os
from dotenv import load_dotenv

load_dotenv()
DATABASE_URL = os.getenv('DATABASE_URL')

async def verify():
    engine = create_async_engine(DATABASE_URL)
    async with engine.connect() as conn:
        # Get all tables
        result = await conn.execute(text("""
            SELECT table_name FROM information_schema.tables 
            WHERE table_schema = 'public'
        """))
        tables = result.fetchall()
        print('✅ Tables created:')
        for table in tables:
            print(f'  - {table[0]}')
        
        # Check backtests columns
        result = await conn.execute(text("""
            SELECT column_name FROM information_schema.columns 
            WHERE table_name = 'backtests'
        """))
        columns = result.fetchall()
        print('\n✅ Backtests columns:')
        for col in columns:
            print(f'  - {col[0]}')
    
    await engine.dispose()

asyncio.run(verify())
