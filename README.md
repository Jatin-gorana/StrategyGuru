# AI Trading Strategy Backtester

A FastAPI backend for backtesting trading strategies using historical stock data.

## Project Structure

```
backend/
├── main.py                 # FastAPI application entry point
├── routers/
│   └── backtest.py        # Backtest endpoints
├── services/
│   ├── data_fetcher.py    # Yahoo Finance data fetching
│   ├── indicators.py      # Technical indicators (RSI, SMA, MACD, etc.)
│   ├── strategy_parser.py # Strategy text parsing
│   └── backtest_engine.py # Backtest execution engine
└── models/
    ├── request_models.py  # Request schemas
    └── response_models.py # Response schemas
```

## Installation

```bash
pip install -r requirements.txt
```

## Running the Server

```bash
python backend/main.py
```

The API will be available at `http://localhost:8000`

## API Documentation

Interactive API docs available at `http://localhost:8000/docs`

## Endpoints

### POST /api/backtest

Run a backtest on a trading strategy.

**Request Body:**
```json
{
  "strategy_text": "Buy when RSI < 30, Sell when RSI > 70",
  "stock_symbol": "AAPL",
  "start_date": "2023-01-01",
  "end_date": "2024-01-01",
  "initial_capital": 10000
}
```

**Response:**
```json
{
  "success": true,
  "message": "Backtest completed successfully",
  "trades": [
    {
      "entry_date": "2023-01-15T00:00:00",
      "entry_price": 150.25,
      "exit_date": "2023-02-10T00:00:00",
      "exit_price": 155.50,
      "quantity": 66,
      "pnl": 347.50,
      "pnl_percent": 3.48
    }
  ],
  "equity_curve": [
    {
      "date": "2023-01-01T00:00:00",
      "equity": 10000
    }
  ],
  "metrics": {
    "total_return": 1250.50,
    "total_return_percent": 12.51,
    "sharpe_ratio": 1.45,
    "max_drawdown": -0.08,
    "max_drawdown_percent": -8.0,
    "win_rate": 65.0,
    "total_trades": 20,
    "winning_trades": 13,
    "losing_trades": 7,
    "avg_win": 125.50,
    "avg_loss": 45.25,
    "profit_factor": 2.77
  }
}
```

## Supported Strategy Patterns

- **RSI**: `RSI < 30` (buy), `RSI > 70` (sell)
- **SMA Crossover**: `SMA(20) > SMA(50)`, `SMA(50) > SMA(200)`
- **Price vs SMA**: `Price > SMA(200)`
- **MACD**: `MACD > Signal`

## Example Usage

```bash
curl -X POST "http://localhost:8000/api/backtest" \
  -H "Content-Type: application/json" \
  -d '{
    "strategy_text": "Buy when RSI < 30, Sell when RSI > 70",
    "stock_symbol": "AAPL",
    "start_date": "2023-01-01",
    "end_date": "2024-01-01",
    "initial_capital": 10000
  }'
```

## Features

- Historical data fetching from Yahoo Finance
- Technical indicators: RSI, SMA, EMA, MACD, Bollinger Bands, ATR
- Strategy parsing from text descriptions
- Trade execution simulation
- Performance metrics calculation:
  - Total return and return percentage
  - Sharpe ratio
  - Maximum drawdown
  - Win rate
  - Profit factor
- Equity curve tracking
