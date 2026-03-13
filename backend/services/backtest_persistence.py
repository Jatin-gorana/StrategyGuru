"""
Background persistence service for backtest results.

Handles asynchronous saving of backtest results to PostgreSQL
using bulk inserts for optimal performance.
"""

import logging
from datetime import date
from uuid import UUID
from typing import List, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from database.models import Strategy, Backtest, Trade, EquityCurve
from database.database import DATABASE_URL

logger = logging.getLogger(__name__)


# Create async engine for background tasks
async_engine = create_async_engine(DATABASE_URL, echo=False)
AsyncSessionLocal = sessionmaker(
    async_engine, class_=AsyncSession, expire_on_commit=False
)


async def save_backtest_results(
    trades: List[Dict[str, Any]],
    equity_curve: List[Dict[str, Any]],
    metrics: Dict[str, Any],
    user_id: UUID,
    strategy_text: str,
    stock_symbol: str,
    start_date: date,
    end_date: date,
    initial_capital: float
) -> None:
    """
    Save backtest results to database asynchronously.
    
    This function runs in the background and performs bulk inserts
    to minimize database queries and improve performance.
    
    Args:
        trades: List of trade dictionaries
        equity_curve: List of equity curve point dictionaries
        metrics: Dictionary of backtest metrics
        user_id: UUID of the user
        strategy_text: Strategy description
        stock_symbol: Stock ticker symbol
        start_date: Backtest start date
        end_date: Backtest end date
        initial_capital: Initial capital amount
    """
    db = None
    try:
        # Create new database session for background task
        db = AsyncSessionLocal()
        
        logger.info(f"Starting background persistence for user {user_id}")
        
        # 1. Create strategy record
        strategy = Strategy(
            user_id=user_id,
            strategy_text=strategy_text
        )
        db.add(strategy)
        await db.flush()  # Flush to get strategy ID without committing
        
        # 2. Create backtest record
        backtest = Backtest(
            user_id=user_id,
            strategy_id=strategy.id,
            stock_symbol=stock_symbol,
            start_date=start_date,
            end_date=end_date,
            initial_capital=initial_capital,
            total_return=metrics.get('total_return'),
            return_percent=metrics.get('total_return_percent'),
            sharpe_ratio=metrics.get('sharpe_ratio'),
            max_drawdown=metrics.get('max_drawdown'),
            max_drawdown_percent=metrics.get('max_drawdown_percent'),
            win_rate=metrics.get('win_rate'),
            profit_factor=metrics.get('profit_factor'),
            total_trades=metrics.get('total_trades')
        )
        db.add(backtest)
        await db.flush()  # Flush to get backtest ID
        
        # 3. Bulk insert trades
        if trades:
            trade_objects = [
                Trade(
                    backtest_id=backtest.id,
                    entry_date=t['entry_date'],
                    exit_date=t['exit_date'],
                    entry_price=t['entry_price'],
                    exit_price=t['exit_price'],
                    profit=t['pnl'],
                    profit_percent=t['pnl_percent']
                )
                for t in trades
            ]
            db.add_all(trade_objects)
            logger.info(f"Added {len(trade_objects)} trades for bulk insert")
        
        # 4. Bulk insert equity curve (with reduced density)
        if equity_curve:
            # Store every 5th point to reduce storage (250 points → 50 points)
            # This keeps charts visually identical while reducing database size
            equity_objects = [
                EquityCurve(
                    backtest_id=backtest.id,
                    date=ec['date'],
                    equity_value=ec['equity']
                )
                for ec in equity_curve[::5]  # Every 5th point
            ]
            db.add_all(equity_objects)
            logger.info(f"Added {len(equity_objects)} equity curve points for bulk insert")
        
        # 5. Single commit for all operations
        await db.commit()
        logger.info(f"Successfully saved backtest {backtest.id} to database")
        
    except Exception as e:
        logger.error(f"Error saving backtest results: {str(e)}", exc_info=True)
        if db:
            await db.rollback()
    finally:
        if db:
            await db.close()


async def save_backtest_results_with_session(
    trades: List[Dict[str, Any]],
    equity_curve: List[Dict[str, Any]],
    metrics: Dict[str, Any],
    user_id: UUID,
    strategy_text: str,
    stock_symbol: str,
    start_date: date,
    end_date: date,
    initial_capital: float,
    db: AsyncSession
) -> None:
    """
    Save backtest results using an existing database session.
    
    This version is used when called from within a request context
    where a session is already available.
    
    Args:
        trades: List of trade dictionaries
        equity_curve: List of equity curve point dictionaries
        metrics: Dictionary of backtest metrics
        user_id: UUID of the user
        strategy_text: Strategy description
        stock_symbol: Stock ticker symbol
        start_date: Backtest start date
        end_date: Backtest end date
        initial_capital: Initial capital amount
        db: Existing AsyncSession
    """
    try:
        logger.info(f"Starting persistence for user {user_id}")
        
        # 1. Create strategy record
        strategy = Strategy(
            user_id=user_id,
            strategy_text=strategy_text
        )
        db.add(strategy)
        await db.flush()
        
        # 2. Create backtest record
        backtest = Backtest(
            user_id=user_id,
            strategy_id=strategy.id,
            stock_symbol=stock_symbol,
            start_date=start_date,
            end_date=end_date,
            initial_capital=initial_capital,
            total_return=metrics.get('total_return'),
            return_percent=metrics.get('total_return_percent'),
            sharpe_ratio=metrics.get('sharpe_ratio'),
            max_drawdown=metrics.get('max_drawdown'),
            max_drawdown_percent=metrics.get('max_drawdown_percent'),
            win_rate=metrics.get('win_rate'),
            profit_factor=metrics.get('profit_factor'),
            total_trades=metrics.get('total_trades')
        )
        db.add(backtest)
        await db.flush()
        
        # 3. Bulk insert trades
        if trades:
            trade_objects = [
                Trade(
                    backtest_id=backtest.id,
                    entry_date=t['entry_date'],
                    exit_date=t['exit_date'],
                    entry_price=t['entry_price'],
                    exit_price=t['exit_price'],
                    profit=t['pnl'],
                    profit_percent=t['pnl_percent']
                )
                for t in trades
            ]
            db.add_all(trade_objects)
            logger.info(f"Added {len(trade_objects)} trades")
        
        # 4. Bulk insert equity curve (reduced density)
        if equity_curve:
            equity_objects = [
                EquityCurve(
                    backtest_id=backtest.id,
                    date=ec['date'],
                    equity_value=ec['equity']
                )
                for ec in equity_curve[::5]
            ]
            db.add_all(equity_objects)
            logger.info(f"Added {len(equity_objects)} equity curve points")
        
        # 5. Single commit
        await db.commit()
        logger.info(f"Successfully saved backtest {backtest.id}")
        
    except Exception as e:
        logger.error(f"Error saving backtest: {str(e)}", exc_info=True)
        await db.rollback()
        raise
