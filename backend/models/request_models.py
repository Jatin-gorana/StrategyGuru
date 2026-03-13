from pydantic import BaseModel, Field
from datetime import date
from typing import Dict, Any

class BacktestRequest(BaseModel):
    strategy_text: str = Field(..., description="Strategy logic in text format")
    stock_symbol: str = Field(..., description="Stock ticker symbol (e.g., AAPL)")
    start_date: str = Field(..., description="Start date for backtest (YYYY-MM-DD)")
    end_date: str = Field(..., description="End date for backtest (YYYY-MM-DD)")
    initial_capital: float = Field(default=10000, description="Initial capital in USD")
    
    class Config:
        json_schema_extra = {
            "example": {
                "strategy_text": "Buy when RSI < 30, Sell when RSI > 70",
                "stock_symbol": "AAPL",
                "start_date": "2023-01-01",
                "end_date": "2024-01-01",
                "initial_capital": 10000
            }
        }


class ImproveStrategyRequest(BaseModel):
    strategy_text: str = Field(..., description="Current strategy description")
    metrics: Dict[str, Any] = Field(..., description="Backtest metrics dictionary")
    trades_count: int = Field(default=0, description="Number of trades executed")
    
    class Config:
        json_schema_extra = {
            "example": {
                "strategy_text": "Buy when RSI < 30, Sell when RSI > 70",
                "metrics": {
                    "total_return_percent": 15.5,
                    "sharpe_ratio": 1.2,
                    "max_drawdown_percent": -10.5,
                    "win_rate": 55.0,
                    "profit_factor": 1.8,
                    "avg_win": 100.0,
                    "avg_loss": -50.0
                },
                "trades_count": 25
            }
        }
