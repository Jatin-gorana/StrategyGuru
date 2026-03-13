#!/usr/bin/env python
"""
Script to recreate the database with the correct schema
"""
import asyncio
import os
import sys
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql+asyncpg://postgres:1234@localhost:5432/trading_backtester")

# Connection string for dropping database (without the database name)
ADMIN_URL = "postgresql+asyncpg://postgres:1234@localhost:5432/postgres"

async def recreate_database():
    """Drop and recreate the database"""
    
    # Connect to postgres database to drop trading_backtester
    admin_engine = create_async_engine(ADMIN_URL, isolation_level="AUTOCOMMIT")
    
    try:
        async with admin_engine.connect() as conn:
            # Terminate existing connections
            await conn.execute(text("""
                SELECT pg_terminate_backend(pg_stat_activity.pid)
                FROM pg_stat_activity
                WHERE pg_stat_activity.datname = 'trading_backtester'
                AND pid <> pg_backend_pid();
            """))
            
            # Drop database
            await conn.execute(text("DROP DATABASE IF EXISTS trading_backtester;"))
            print("✅ Dropped old database")
            
            # Create new database
            await conn.execute(text("CREATE DATABASE trading_backtester;"))
            print("✅ Created new database")
    finally:
        await admin_engine.dispose()
    
    # Now create tables in the new database
    sys.path.insert(0, os.path.dirname(__file__))
    from database.database import engine, Base
    from database import models  # Import to register models
    
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        print("✅ Created all tables with correct schema")
    
    await engine.dispose()
    print("✅ Database recreated successfully!")

if __name__ == "__main__":
    asyncio.run(recreate_database())
