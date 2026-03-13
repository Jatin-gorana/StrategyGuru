# FastAPI Backtest Endpoint Documentation

## Overview

The FastAPI backend provides a comprehensive REST API for backtesting trading strategies. The main endpoint accepts natural language strategy descriptions, fetches historical data, calculates indicators, and returns detailed performance metrics.

## Base URL

```
http://localhost:8000
```

## Interactive API Documentation

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## Endpoints

### 1. POST /api/backtest

Run a backtest on a trading strategy.

#### Request

```json
{
  "strategy_text": "Buy when RSI < 30 and sell when RSI > 70",
  "stock_symbol": "AAPL",
  "start_date": "2023-01-01",
  "end_date": "2024-01-01",
  "initial_capital": 10000
}
```

#### Request Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| strategy_text | string | Yes | Natural language strategy description |
| stock_symbol | string | Yes | Stock ticker symbol (e.g., AAPL, GOOGL) |
| start_date | string | Yes | Start date in YYYY-MM-DD format |
| end_date | string | Yes | End date in YYYY-MM-DD format |
| initial_capital | number | No | Starting capital in USD (default: 10000) |

#### Response

```json
{
  "success": true,
  "message": "Backtest completed successfully. 45 trades executed.",
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
      "equity": 10000.00
    },
    {
      "date": "2023-01-02T00:00:00",
      "equity": 10050.25
    }
  ],
  "metrics": {
    "total_return": 1250.50,
    "total_return_percent": 12.51,
    "sharpe_ratio": 1.45,
    "max_drawdown": -0.08,
    "max_drawdown_percent": -8.0,
    "win_rate": 65.0,
    "total_trades": 45,
    "winning_trades": 29,
    "losing_trades": 16,
    "avg_win": 125.50,
    "avg_loss": 45.25,
    "profit_factor": 2.77
  }
}
```

#### Response Fields

| Field | Type | Description |
|-------|------|-------------|
| success | boolean | Whether the backtest completed successfully |
| message | string | Status message |
| trades | array | List of executed trades |
| equity_curve | array | Daily equity values |
| metrics | object | Performance metrics |

#### Metrics Explanation

| Metric | Description |
|--------|-------------|
| total_return | Absolute profit/loss in USD |
| total_return_percent | Return as percentage of initial capital |
| sharpe_ratio | Risk-adjusted return (higher is better) |
| max_drawdown | Largest peak-to-trough decline (decimal) |
| max_drawdown_percent | Max drawdown as percentage |
| win_rate | Percentage of profitable trades |
| total_trades | Total number of trades executed |
| winning_trades | Number of profitable trades |
| losing_trades | Number of losing trades |
| avg_win | Average profit per winning trade |
| avg_loss | Average loss per losing trade |
| profit_factor | Ratio of gross profit to gross loss |

#### Example cURL Request

```bash
curl -X POST "http://localhost:8000/api/backtest" \
  -H "Content-Type: application/json" \
  -d '{
    "strategy_text": "Buy when RSI < 30 and sell when RSI > 70",
    "stock_symbol": "AAPL",
    "start_date": "2023-01-01",
    "end_date": "2024-01-01",
    "initial_capital": 10000
  }'
```

#### Example Python Request

```python
import requests

url = "http://localhost:8000/api/backtest"
payload = {
    "strategy_text": "Buy when RSI < 30 and sell when RSI > 70",
    "stock_symbol": "AAPL",
    "start_date": "2023-01-01",
    "end_date": "2024-01-01",
    "initial_capital": 10000
}

response = requests.post(url, json=payload)
result = response.json()

print(f"Total Return: {result['metrics']['total_return_percent']:.2f}%")
print(f"Sharpe Ratio: {result['metrics']['sharpe_ratio']:.4f}")
print(f"Win Rate: {result['metrics']['win_rate']:.2f}%")
```

#### Error Responses

**400 Bad Request** - Invalid input
```json
{
  "detail": "No data found for INVALID in the specified date range"
}
```

**500 Internal Server Error** - Server error
```json
{
  "detail": "Backtest failed: [error details]"
}
```

---

### 2. POST /api/backtest/parse-strategy

Parse a natural language strategy into structured rules.

#### Request

```json
{
  "strategy_text": "Buy when RSI < 30 and sell when RSI > 70"
}
```

#### Response

```json
{
  "success": true,
  "buy_condition": "rsi < 30",
  "sell_condition": "rsi > 70",
  "indicators_required": ["RSI"],
  "parameters": {
    "rsi_period": 14
  }
}
```

#### Example cURL Request

```bash
curl -X POST "http://localhost:8000/api/backtest/parse-strategy" \
  -H "Content-Type: application/json" \
  -d '{"strategy_text": "Buy when RSI < 30 and sell when RSI > 70"}'
```

---

### 3. GET /api/backtest/indicators

Get list of supported indicators.

#### Response

```json
{
  "success": true,
  "indicators": {
    "RSI": {
      "name": "Relative Strength Index",
      "description": "Measures momentum and overbought/oversold conditions",
      "default_period": 14,
      "range": "0-100"
    },
    "SMA": {
      "name": "Simple Moving Average",
      "description": "Average price over a specified period",
      "default_period": 50,
      "common_periods": [20, 50, 200]
    },
    "EMA": {
      "name": "Exponential Moving Average",
      "description": "Weighted moving average giving more weight to recent prices",
      "default_period": 12,
      "common_periods": [12, 26]
    },
    "MACD": {
      "name": "Moving Average Convergence Divergence",
      "description": "Trend-following momentum indicator",
      "parameters": {"fast": 12, "slow": 26, "signal": 9}
    },
    "Bollinger Bands": {
      "name": "Bollinger Bands",
      "description": "Volatility bands around a moving average",
      "parameters": {"period": 20, "std_dev": 2}
    },
    "ATR": {
      "name": "Average True Range",
      "description": "Measures market volatility",
      "default_period": 14
    },
    "Stochastic": {
      "name": "Stochastic Oscillator",
      "description": "Compares closing price to price range",
      "parameters": {"period": 14, "smooth_k": 3, "smooth_d": 3}
    },
    "ADX": {
      "name": "Average Directional Index",
      "description": "Measures trend strength",
      "default_period": 14
    }
  }
}
```

#### Example cURL Request

```bash
curl -X GET "http://localhost:8000/api/backtest/indicators"
```

---

### 4. GET /api/backtest/examples

Get example strategies.

#### Response

```json
{
  "success": true,
  "examples": [
    {
      "name": "RSI Oversold/Overbought",
      "description": "Buy when RSI drops below 30 (oversold), sell when it rises above 70 (overbought)",
      "strategy": "Buy when RSI < 30 and sell when RSI > 70",
      "indicators": ["RSI"],
      "risk_level": "Medium"
    },
    {
      "name": "Golden Cross",
      "description": "Buy when 50-day MA crosses above 200-day MA (bullish), sell on opposite crossover",
      "strategy": "Buy when SMA(50) > SMA(200) and sell when SMA(50) < SMA(200)",
      "indicators": ["SMA"],
      "risk_level": "Low"
    }
  ]
}
```

#### Example cURL Request

```bash
curl -X GET "http://localhost:8000/api/backtest/examples"
```

---

### 5. GET /health

Health check endpoint.

#### Response

```json
{
  "status": "healthy"
}
```

---

## Supported Strategies

### RSI Strategy
```
"Buy when RSI < 30 and sell when RSI > 70"
```

### Moving Average Crossover
```
"Buy when SMA(50) > SMA(200) and sell when SMA(50) < SMA(200)"
```

### MACD Strategy
```
"Buy when MACD > Signal and sell when MACD < Signal"
```

### EMA Trend Following
```
"Buy when EMA(12) > EMA(26) and sell when EMA(12) < EMA(26)"
```

### Combined Strategy
```
"Buy when RSI < 30 and SMA(50) > SMA(200) and sell when RSI > 70 or SMA(50) < SMA(200)"
```

---

## Usage Examples

### Example 1: Simple RSI Strategy

```bash
curl -X POST "http://localhost:8000/api/backtest" \
  -H "Content-Type: application/json" \
  -d '{
    "strategy_text": "Buy when RSI < 30 and sell when RSI > 70",
    "stock_symbol": "AAPL",
    "start_date": "2023-01-01",
    "end_date": "2024-01-01"
  }'
```

### Example 2: Golden Cross Strategy

```bash
curl -X POST "http://localhost:8000/api/backtest" \
  -H "Content-Type: application/json" \
  -d '{
    "strategy_text": "Buy when SMA(50) > SMA(200) and sell when SMA(50) < SMA(200)",
    "stock_symbol": "GOOGL",
    "start_date": "2023-01-01",
    "end_date": "2024-01-01",
    "initial_capital": 50000
  }'
```

### Example 3: MACD Strategy

```bash
curl -X POST "http://localhost:8000/api/backtest" \
  -H "Content-Type: application/json" \
  -d '{
    "strategy_text": "Buy when MACD > Signal and sell when MACD < Signal",
    "stock_symbol": "MSFT",
    "start_date": "2023-06-01",
    "end_date": "2024-01-01"
  }'
```

---

## Python Client Example

```python
import requests
import json

class BacktestClient:
    def __init__(self, base_url="http://localhost:8000"):
        self.base_url = base_url
    
    def run_backtest(self, strategy_text, symbol, start_date, end_date, capital=10000):
        """Run a backtest."""
        url = f"{self.base_url}/api/backtest"
        payload = {
            "strategy_text": strategy_text,
            "stock_symbol": symbol,
            "start_date": start_date,
            "end_date": end_date,
            "initial_capital": capital
        }
        
        response = requests.post(url, json=payload)
        return response.json()
    
    def parse_strategy(self, strategy_text):
        """Parse a strategy."""
        url = f"{self.base_url}/api/backtest/parse-strategy"
        response = requests.post(url, json={"strategy_text": strategy_text})
        return response.json()
    
    def get_indicators(self):
        """Get supported indicators."""
        url = f"{self.base_url}/api/backtest/indicators"
        response = requests.get(url)
        return response.json()
    
    def get_examples(self):
        """Get example strategies."""
        url = f"{self.base_url}/api/backtest/examples"
        response = requests.get(url)
        return response.json()

# Usage
client = BacktestClient()

# Run backtest
result = client.run_backtest(
    strategy_text="Buy when RSI < 30 and sell when RSI > 70",
    symbol="AAPL",
    start_date="2023-01-01",
    end_date="2024-01-01"
)

print(f"Total Return: {result['metrics']['total_return_percent']:.2f}%")
print(f"Sharpe Ratio: {result['metrics']['sharpe_ratio']:.4f}")
print(f"Win Rate: {result['metrics']['win_rate']:.2f}%")
print(f"Total Trades: {result['metrics']['total_trades']}")
```

---

## Error Handling

### Common Errors

**Invalid Stock Symbol**
```json
{
  "detail": "No data found for INVALID in the specified date range"
}
```

**Invalid Date Format**
```json
{
  "detail": "time data '2023-13-01' does not match format '%Y-%m-%d'"
}
```

**Strategy Parsing Error**
```json
{
  "detail": "Failed to parse strategy: [error details]"
}
```

---

## Rate Limiting

Currently, there are no rate limits. For production use, consider implementing:
- Request throttling
- API key authentication
- Usage quotas

---

## Performance Notes

- Backtest execution time depends on:
  - Date range (more data = longer execution)
  - Number of indicators
  - Strategy complexity
- Typical backtest: 1-5 seconds
- Large backtests (5+ years): 5-15 seconds

---

## Best Practices

1. **Start with small date ranges** to test strategies quickly
2. **Use realistic initial capital** for meaningful metrics
3. **Check equity curve** for drawdown patterns
4. **Validate strategies** before trading with real money
5. **Monitor Sharpe ratio** for risk-adjusted returns
6. **Consider profit factor** for trade quality

---

## Support

For issues or questions:
1. Check the interactive API docs at `/docs`
2. Review example strategies at `/api/backtest/examples`
3. Check supported indicators at `/api/backtest/indicators`
4. Review logs for detailed error messages
