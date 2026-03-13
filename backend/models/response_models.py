from pydantic import BaseModel
from typing import List
from datetime import datetime

class Trade(BaseModel):
    entry_date: datetime
    entry_price: float
    exit_date: datetime
    exit_price: float
    quantity: int
    pnl: float
    pnl_percent: float

class EquityCurvePoint(BaseModel):
    date: datetime
    equity: float

class BacktestMetrics(BaseModel):
    total_return: float
    total_return_percent: float
    sharpe_ratio: float
    max_drawdown: float
    max_drawdown_percent: float
    win_rate: float
    total_trades: int
    winning_trades: int
    losing_trades: int
    avg_win: float
    avg_loss: float
    profit_factor: float

class BacktestResponse(BaseModel):
    success: bool
    message: str
    trades: List[Trade]
    equity_curve: List[EquityCurvePoint]
    metrics: BacktestMetrics
