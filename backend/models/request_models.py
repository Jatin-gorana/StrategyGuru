from pydantic import BaseModel, Field
from datetime import date

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
