from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import timedelta

from database.database import get_db
from database.schemas import UserCreate, UserLogin, UserResponse, Token, UserProfileResponse
from database.crud import (
    create_user, get_user_by_email, get_user_by_id,
    get_user_strategies, get_user_backtests, get_user_statistics
)
from database.auth import (
    hash_password, verify_password, create_access_token,
    get_current_user, ACCESS_TOKEN_EXPIRE_MINUTES
)
from database.models import User

router = APIRouter(prefix="/users", tags=["users"])


@router.post("/register", response_model=Token)
async def register(user: UserCreate, db: AsyncSession = Depends(get_db)):
    """Register a new user"""
    # Check if user already exists
    existing_user = await get_user_by_email(db, user.email)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Hash password and create user
    password_hash = hash_password(user.password)
    db_user = await create_user(db, user, password_hash)
    
    # Create access token
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": db_user.email},
        expires_delta=access_token_expires
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": UserResponse.from_orm(db_user)
    }


@router.post("/login", response_model=Token)
async def login(credentials: UserLogin, db: AsyncSession = Depends(get_db)):
    """Login user and return JWT token"""
    # Get user by email
    user = await get_user_by_email(db, credentials.email)
    
    if not user or not verify_password(credentials.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )
    
    # Create access token
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.email},
        expires_delta=access_token_expires
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": UserResponse.from_orm(user)
    }


@router.get("/profile", response_model=UserProfileResponse)
async def get_profile(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get current user profile with statistics"""
    stats = await get_user_statistics(db, current_user.id)
    
    return {
        "user": UserResponse.from_orm(current_user),
        "total_strategies": stats["total_strategies"],
        "total_backtests": stats["total_backtests"],
        "average_return": stats["average_return"],
        "best_sharpe_ratio": stats["best_sharpe_ratio"]
    }


@router.get("/strategies")
async def get_strategies(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get all strategies for current user"""
    strategies = await get_user_strategies(db, current_user.id)
    
    return {
        "strategies": [
            {
                "id": str(s.id),
                "user_id": str(s.user_id),
                "strategy_text": s.strategy_text,
                "created_at": s.created_at
            }
            for s in strategies
        ],
        "total_count": len(strategies)
    }


@router.get("/backtests")
async def get_backtests(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get all backtests for current user"""
    backtests = await get_user_backtests(db, current_user.id)
    
    return {
        "backtests": [
            {
                "id": str(b.id),
                "user_id": str(b.user_id),
                "strategy_id": str(b.strategy_id),
                "stock_symbol": b.stock_symbol,
                "start_date": b.start_date,
                "end_date": b.end_date,
                "initial_capital": b.initial_capital,
                "total_return": b.total_return,
                "return_percent": b.return_percent,
                "sharpe_ratio": b.sharpe_ratio,
                "max_drawdown": b.max_drawdown,
                "max_drawdown_percent": b.max_drawdown_percent,
                "win_rate": b.win_rate,
                "profit_factor": b.profit_factor,
                "total_trades": b.total_trades,
                "created_at": b.created_at
            }
            for b in backtests
        ],
        "total_count": len(backtests)
    }


@router.get("/backtests/{backtest_id}")
async def get_backtest_detail(
    backtest_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get detailed backtest information with trades and equity curve"""
    from database.crud import get_backtest_by_id, get_backtest_trades, get_backtest_equity_curve
    from uuid import UUID
    
    try:
        backtest_uuid = UUID(backtest_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid backtest ID"
        )
    
    backtest = await get_backtest_by_id(db, backtest_uuid)
    
    if not backtest:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Backtest not found"
        )
    
    # Check if backtest belongs to current user
    if backtest.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )
    
    trades = await get_backtest_trades(db, backtest_uuid)
    equity_curve = await get_backtest_equity_curve(db, backtest_uuid)
    
    return {
        "id": str(backtest.id),
        "user_id": str(backtest.user_id),
        "strategy_id": str(backtest.strategy_id),
        "stock_symbol": backtest.stock_symbol,
        "start_date": backtest.start_date,
        "end_date": backtest.end_date,
        "initial_capital": backtest.initial_capital,
        "total_return": backtest.total_return,
        "return_percent": backtest.return_percent,
        "sharpe_ratio": backtest.sharpe_ratio,
        "max_drawdown": backtest.max_drawdown,
        "max_drawdown_percent": backtest.max_drawdown_percent,
        "win_rate": backtest.win_rate,
        "profit_factor": backtest.profit_factor,
        "total_trades": backtest.total_trades,
        "created_at": backtest.created_at,
        "trades": [
            {
                "id": str(t.id),
                "entry_date": t.entry_date,
                "exit_date": t.exit_date,
                "entry_price": t.entry_price,
                "exit_price": t.exit_price,
                "profit": t.profit,
                "profit_percent": t.profit_percent
            }
            for t in trades
        ],
        "equity_curve": [
            {
                "id": str(e.id),
                "date": e.date,
                "equity_value": e.equity_value
            }
            for e in equity_curve
        ]
    }
