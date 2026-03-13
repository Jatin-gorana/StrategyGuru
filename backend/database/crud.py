from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import func, desc
from datetime import date
from uuid import UUID
from typing import Optional, List

from database.models import User, Strategy, Backtest, Trade, EquityCurve
from database.schemas import (
    UserCreate, StrategyCreate, BacktestCreate,
    UserResponse, StrategyResponse, BacktestResponse
)


# User CRUD
async def create_user(db: AsyncSession, user: UserCreate, password_hash: str) -> User:
    """Create a new user"""
    db_user = User(
        name=user.name,
        email=user.email,
        password_hash=password_hash
    )
    db.add(db_user)
    await db.commit()
    await db.refresh(db_user)
    return db_user


async def get_user_by_email(db: AsyncSession, email: str) -> Optional[User]:
    """Get user by email"""
    result = await db.execute(select(User).where(User.email == email))
    return result.scalars().first()


async def get_user_by_id(db: AsyncSession, user_id: UUID) -> Optional[User]:
    """Get user by ID"""
    result = await db.execute(select(User).where(User.id == user_id))
    return result.scalars().first()


# Strategy CRUD
async def create_strategy(db: AsyncSession, user_id: UUID, strategy_text: str) -> Strategy:
    """Create a new strategy"""
    db_strategy = Strategy(
        user_id=user_id,
        strategy_text=strategy_text
    )
    db.add(db_strategy)
    await db.commit()
    await db.refresh(db_strategy)
    return db_strategy


async def get_user_strategies(db: AsyncSession, user_id: UUID) -> List[Strategy]:
    """Get all strategies for a user"""
    result = await db.execute(
        select(Strategy).where(Strategy.user_id == user_id).order_by(desc(Strategy.created_at))
    )
    return result.scalars().all()


async def get_strategy_by_id(db: AsyncSession, strategy_id: UUID) -> Optional[Strategy]:
    """Get strategy by ID"""
    result = await db.execute(select(Strategy).where(Strategy.id == strategy_id))
    return result.scalars().first()


# Backtest CRUD
async def create_backtest(
    db: AsyncSession,
    user_id: UUID,
    strategy_id: UUID,
    stock_symbol: str,
    start_date: date,
    end_date: date,
    initial_capital: float
) -> Backtest:
    """Create a new backtest record"""
    db_backtest = Backtest(
        user_id=user_id,
        strategy_id=strategy_id,
        stock_symbol=stock_symbol,
        start_date=start_date,
        end_date=end_date,
        initial_capital=initial_capital
    )
    db.add(db_backtest)
    await db.commit()
    await db.refresh(db_backtest)
    return db_backtest


async def update_backtest_metrics(
    db: AsyncSession,
    backtest_id: UUID,
    total_return: float,
    return_percent: float,
    sharpe_ratio: float,
    max_drawdown: float,
    max_drawdown_percent: float,
    win_rate: float,
    profit_factor: float,
    total_trades: int
) -> Backtest:
    """Update backtest with metrics"""
    result = await db.execute(select(Backtest).where(Backtest.id == backtest_id))
    db_backtest = result.scalars().first()
    
    if db_backtest:
        db_backtest.total_return = total_return
        db_backtest.return_percent = return_percent
        db_backtest.sharpe_ratio = sharpe_ratio
        db_backtest.max_drawdown = max_drawdown
        db_backtest.max_drawdown_percent = max_drawdown_percent
        db_backtest.win_rate = win_rate
        db_backtest.profit_factor = profit_factor
        db_backtest.total_trades = total_trades
        
        await db.commit()
        await db.refresh(db_backtest)
    
    return db_backtest


async def get_user_backtests(db: AsyncSession, user_id: UUID) -> List[Backtest]:
    """Get all backtests for a user"""
    result = await db.execute(
        select(Backtest).where(Backtest.user_id == user_id).order_by(desc(Backtest.created_at))
    )
    return result.scalars().all()


async def get_backtest_by_id(db: AsyncSession, backtest_id: UUID) -> Optional[Backtest]:
    """Get backtest by ID"""
    result = await db.execute(select(Backtest).where(Backtest.id == backtest_id))
    return result.scalars().first()


async def get_backtest_details(db: AsyncSession, backtest_id: UUID) -> Optional[Backtest]:
    """Get backtest with all related data (trades and equity curve)"""
    result = await db.execute(
        select(Backtest).where(Backtest.id == backtest_id)
    )
    return result.scalars().first()


# Trade CRUD
async def create_trade(
    db: AsyncSession,
    backtest_id: UUID,
    entry_date: date,
    exit_date: date,
    entry_price: float,
    exit_price: float,
    profit: float,
    profit_percent: float
) -> Trade:
    """Create a new trade record"""
    db_trade = Trade(
        backtest_id=backtest_id,
        entry_date=entry_date,
        exit_date=exit_date,
        entry_price=entry_price,
        exit_price=exit_price,
        profit=profit,
        profit_percent=profit_percent
    )
    db.add(db_trade)
    await db.commit()
    await db.refresh(db_trade)
    return db_trade


async def get_backtest_trades(db: AsyncSession, backtest_id: UUID) -> List[Trade]:
    """Get all trades for a backtest"""
    result = await db.execute(
        select(Trade).where(Trade.backtest_id == backtest_id)
    )
    return result.scalars().all()


# Equity Curve CRUD
async def create_equity_point(
    db: AsyncSession,
    backtest_id: UUID,
    date_val: date,
    equity_value: float
) -> EquityCurve:
    """Create an equity curve point"""
    db_equity = EquityCurve(
        backtest_id=backtest_id,
        date=date_val,
        equity_value=equity_value
    )
    db.add(db_equity)
    await db.commit()
    await db.refresh(db_equity)
    return db_equity


async def get_backtest_equity_curve(db: AsyncSession, backtest_id: UUID) -> List[EquityCurve]:
    """Get equity curve for a backtest"""
    result = await db.execute(
        select(EquityCurve).where(EquityCurve.backtest_id == backtest_id).order_by(EquityCurve.date)
    )
    return result.scalars().all()


# User Profile Statistics
async def get_user_statistics(db: AsyncSession, user_id: UUID) -> dict:
    """Get user statistics for profile"""
    # Total strategies
    strategies_result = await db.execute(
        select(func.count(Strategy.id)).where(Strategy.user_id == user_id)
    )
    total_strategies = strategies_result.scalar() or 0
    
    # Total backtests
    backtests_result = await db.execute(
        select(func.count(Backtest.id)).where(Backtest.user_id == user_id)
    )
    total_backtests = backtests_result.scalar() or 0
    
    # Average return
    avg_return_result = await db.execute(
        select(func.avg(Backtest.return_percent)).where(Backtest.user_id == user_id)
    )
    average_return = avg_return_result.scalar()
    
    # Best Sharpe ratio
    best_sharpe_result = await db.execute(
        select(func.max(Backtest.sharpe_ratio)).where(Backtest.user_id == user_id)
    )
    best_sharpe_ratio = best_sharpe_result.scalar()
    
    return {
        "total_strategies": total_strategies,
        "total_backtests": total_backtests,
        "average_return": average_return,
        "best_sharpe_ratio": best_sharpe_ratio
    }
