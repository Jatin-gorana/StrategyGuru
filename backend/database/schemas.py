from pydantic import BaseModel, EmailStr
from datetime import datetime, date
from typing import Optional, List
from uuid import UUID


# User Schemas
class UserCreate(BaseModel):
    name: str
    email: EmailStr
    password: str


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserResponse(BaseModel):
    id: UUID
    name: str
    email: str
    created_at: datetime

    class Config:
        from_attributes = True


# Strategy Schemas
class StrategyCreate(BaseModel):
    strategy_text: str


class StrategyResponse(BaseModel):
    id: UUID
    user_id: UUID
    strategy_text: str
    created_at: datetime

    class Config:
        from_attributes = True


# Trade Schemas
class TradeResponse(BaseModel):
    id: UUID
    entry_date: date
    exit_date: date
    entry_price: float
    exit_price: float
    profit: float
    profit_percent: float

    class Config:
        from_attributes = True


# Equity Curve Schemas
class EquityCurveResponse(BaseModel):
    id: UUID
    date: date
    equity_value: float

    class Config:
        from_attributes = True


# Backtest Schemas
class BacktestCreate(BaseModel):
    strategy_id: UUID
    stock_symbol: str
    start_date: date
    end_date: date
    initial_capital: float


class BacktestResponse(BaseModel):
    id: UUID
    user_id: UUID
    strategy_id: UUID
    stock_symbol: str
    start_date: date
    end_date: date
    initial_capital: float
    total_return: Optional[float]
    return_percent: Optional[float]
    sharpe_ratio: Optional[float]
    max_drawdown: Optional[float]
    max_drawdown_percent: Optional[float]
    win_rate: Optional[float]
    profit_factor: Optional[float]
    total_trades: Optional[int]
    created_at: datetime

    class Config:
        from_attributes = True


class BacktestDetailResponse(BacktestResponse):
    trades: List[TradeResponse]
    equity_curve: List[EquityCurveResponse]


# Token Schemas
class Token(BaseModel):
    access_token: str
    token_type: str
    user: UserResponse


class TokenData(BaseModel):
    email: Optional[str] = None


# Profile Schemas
class UserProfileResponse(BaseModel):
    user: UserResponse
    total_strategies: int
    total_backtests: int
    average_return: Optional[float]
    best_sharpe_ratio: Optional[float]


class UserStrategiesResponse(BaseModel):
    strategies: List[StrategyResponse]
    total_count: int


class UserBacktestsResponse(BaseModel):
    backtests: List[BacktestResponse]
    total_count: int
