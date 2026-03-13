# Architecture Diagrams - Trading Strategy Backtester

## 1. System Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         TRADING STRATEGY BACKTESTER                     │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  ┌──────────────────────────────────────────────────────────────────┐  │
│  │                      FRONTEND LAYER (Next.js 14)                 │  │
│  │                      Port: 3000                                  │  │
│  ├──────────────────────────────────────────────────────────────────┤  │
│  │                                                                  │  │
│  │  ┌─────────────────────────────────────────────────────────┐   │  │
│  │  │  Pages                                                  │   │  │
│  │  │  ├─ Home (/)              - Strategy input form        │   │  │
│  │  │  ├─ Dashboard (/dashboard) - Results display          │   │  │
│  │  │  └─ Results (/results)     - Detailed results         │   │  │
│  │  └─────────────────────────────────────────────────────────┘   │  │
│  │                                                                  │  │
│  │  ┌─────────────────────────────────────────────────────────┐   │  │
│  │  │  Components                                             │   │  │
│  │  │  ├─ StrategyInput          - Form input               │   │  │
│  │  │  ├─ EquityChart            - Line chart               │   │  │
│  │  │  ├─ TradesTable            - Trades list              │   │  │
│  │  │  ├─ MetricsCard            - Performance metrics      │   │  │
│  │  │  ├─ PerformanceChart       - Performance chart        │   │  │
│  │  │  ├─ DrawdownChart          - Drawdown analysis        │   │  │
│  │  │  └─ StrategyImprovementModal - LLM suggestions        │   │  │
│  │  └─────────────────────────────────────────────────────────┘   │  │
│  │                                                                  │  │
│  │  ┌─────────────────────────────────────────────────────────┐   │  │
│  │  │  API Client (lib/api.ts)                               │   │  │
│  │  │  ├─ runBacktest()                                      │   │  │
│  │  │  ├─ parseStrategy()                                    │   │  │
│  │  │  ├─ getIndicators()                                    │   │  │
│  │  │  ├─ getExamples()                                      │   │  │
│  │  │  └─ improveStrategy()                                  │   │  │
│  │  └─────────────────────────────────────────────────────────┘   │  │
│  │                                                                  │  │
│  └──────────────────────────────────────────────────────────────────┘  │
│                              │                                          │
│                              │ HTTP/REST                                │
│                              ▼                                          │
│  ┌──────────────────────────────────────────────────────────────────┐  │
│  │                      BACKEND LAYER (FastAPI)                     │  │
│  │                      Port: 8000                                  │  │
│  ├──────────────────────────────────────────────────────────────────┤  │
│  │                                                                  │  │
│  │  ┌─────────────────────────────────────────────────────────┐   │  │
│  │  │  API Routes (routers/backtest.py)                      │   │  │
│  │  │  ├─ POST /api/backtest                                 │   │  │
│  │  │  ├─ POST /api/backtest/parse-strategy                  │   │  │
│  │  │  ├─ GET /api/backtest/indicators                       │   │  │
│  │  │  ├─ GET /api/backtest/examples                         │   │  │
│  │  │  ├─ POST /api/backtest/improve-strategy                │   │  │
│  │  │  └─ GET /health                                        │   │  │
│  │  └─────────────────────────────────────────────────────────┘   │  │
│  │                              │                                  │  │
│  │                              ▼                                  │  │
│  │  ┌─────────────────────────────────────────────────────────┐   │  │
│  │  │  Data Models (models/)                                  │   │  │
│  │  │  ├─ BacktestRequest                                     │   │  │
│  │  │  ├─ BacktestResponse                                    │   │  │
│  │  │  ├─ Trade                                               │   │  │
│  │  │  ├─ BacktestMetrics                                     │   │  │
│  │  │  └─ EquityCurvePoint                                    │   │  │
│  │  └─────────────────────────────────────────────────────────┘   │  │
│  │                              │                                  │  │
│  │                              ▼                                  │  │
│  │  ┌─────────────────────────────────────────────────────────┐   │  │
│  │  │  Business Logic Services (services/)                    │   │  │
│  │  │                                                         │   │  │
│  │  │  ┌──────────────────────────────────────────────────┐  │   │  │
│  │  │  │ data_fetcher.py                                 │  │   │  │
│  │  │  │ ├─ _format_symbol_for_stooq()                   │  │   │  │
│  │  │  │ ├─ _fetch_from_stooq()                          │  │   │  │
│  │  │  │ ├─ get_stock_data()                             │  │   │  │
│  │  │  │ └─ validate_stock_data()                        │  │   │  │
│  │  │  └──────────────────────────────────────────────────┘  │   │  │
│  │  │                                                         │   │  │
│  │  │  ┌──────────────────────────────────────────────────┐  │   │  │
│  │  │  │ indicators.py                                   │  │   │  │
│  │  │  │ ├─ add_all_indicators()                         │  │   │  │
│  │  │  │ ├─ RSI, SMA, EMA, MACD                          │  │   │  │
│  │  │  │ ├─ Bollinger Bands, ATR                         │  │   │  │
│  │  │  │ └─ Stochastic, ADX                              │  │   │  │
│  │  │  └──────────────────────────────────────────────────┘  │   │  │
│  │  │                                                         │   │  │
│  │  │  ┌──────────────────────────────────────────────────┐  │   │  │
│  │  │  │ backtest_engine.py                              │  │   │  │
│  │  │  │ ├─ BacktestEngine class                         │  │   │  │
│  │  │  │ ├─ run_backtest()                               │  │   │  │
│  │  │  │ ├─ _execute_trade()                             │  │   │  │
│  │  │  │ └─ _calculate_metrics()                         │  │   │  │
│  │  │  └──────────────────────────────────────────────────┘  │   │  │
│  │  │                                                         │   │  │
│  │  │  ┌──────────────────────────────────────────────────┐  │   │  │
│  │  │  │ strategy_parser.py                              │  │   │  │
│  │  │  │ ├─ SimpleStrategyParser                         │  │   │  │
│  │  │  │ ├─ StrategyParser (LLM)                         │  │   │  │
│  │  │  │ └─ parse()                                      │  │   │  │
│  │  │  └──────────────────────────────────────────────────┘  │   │  │
│  │  │                                                         │   │  │
│  │  │  ┌──────────────────────────────────────────────────┐  │   │  │
│  │  │  │ strategy_improver.py                            │  │   │  │
│  │  │  │ ├─ OpenAIProvider                               │  │   │  │
│  │  │  │ ├─ GeminiProvider                               │  │   │  │
│  │  │  │ └─ improve_strategy()                           │  │   │  │
│  │  │  └──────────────────────────────────────────────────┘  │   │  │
│  │  │                                                         │   │  │
│  │  └─────────────────────────────────────────────────────────┘   │  │
│  │                              │                                  │  │
│  │                              ▼                                  │  │
│  │  ┌─────────────────────────────────────────────────────────┐   │  │
│  │  │  External APIs                                          │   │  │
│  │  │  ├─ Stooq (CSV)                                         │   │  │
│  │  │  ├─ OpenAI (LLM)                                        │   │  │
│  │  │  └─ Google Gemini (LLM)                                 │   │  │
│  │  └─────────────────────────────────────────────────────────┘   │  │
│  │                                                                  │  │
│  └──────────────────────────────────────────────────────────────────┘  │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## 2. Data Flow Diagram

```
┌──────────────────────────────────────────────────────────────────────┐
│                    USER INTERACTION FLOW                             │
└──────────────────────────────────────────────────────────────────────┘

1. USER SUBMITS FORM
   ├─ Strategy: "Buy when RSI < 30 and sell when RSI > 70"
   ├─ Symbol: "AAPL"
   ├─ Start Date: "2024-01-01"
   ├─ End Date: "2024-12-31"
   └─ Initial Capital: 10000

                              │
                              ▼

2. FRONTEND VALIDATION
   ├─ Check strategy not empty
   ├─ Check symbol not empty
   ├─ Check start_date < end_date
   ├─ Check capital > 0
   └─ Send POST /api/backtest

                              │
                              ▼

3. BACKEND RECEIVES REQUEST
   ├─ Parse BacktestRequest
   ├─ Validate input data
   └─ Start processing

                              │
                              ▼

4. PARSE STRATEGY
   ├─ Input: "Buy when RSI < 30 and sell when RSI > 70"
   ├─ Extract indicators: [RSI]
   ├─ Extract conditions:
   │  ├─ buy_condition: "rsi < 30"
   │  └─ sell_condition: "rsi > 70"
   └─ Return StrategyRules

                              │
                              ▼

5. FETCH HISTORICAL DATA
   ├─ Format symbol: AAPL → aapl.us
   ├─ Construct URL: https://stooq.com/q/d/l/?s=aapl.us&i=d
   ├─ Fetch CSV from Stooq
   ├─ Parse CSV data
   ├─ Convert to DataFrame
   ├─ Filter by date range
   └─ Return: 252 rows of OHLCV data

                              │
                              ▼

6. CALCULATE INDICATORS
   ├─ Input: DataFrame with OHLCV
   ├─ Calculate:
   │  ├─ RSI (14)
   │  ├─ SMA (50, 200)
   │  ├─ EMA (12, 26)
   │  ├─ MACD
   │  ├─ Bollinger Bands
   │  ├─ ATR
   │  ├─ Stochastic
   │  ├─ ADX
   │  └─ ... (15+ indicators)
   └─ Return: DataFrame with all indicators

                              │
                              ▼

7. GENERATE SIGNALS
   ├─ Evaluate buy_condition: df['RSI'] < 30
   ├─ Evaluate sell_condition: df['RSI'] > 70
   ├─ Create boolean Series
   └─ Return: buy_signals, sell_signals

                              │
                              ▼

8. RUN BACKTEST
   ├─ Initialize BacktestEngine
   ├─ For each row in DataFrame:
   │  ├─ Check buy signal
   │  │  └─ If true: Execute BUY trade
   │  ├─ Check sell signal
   │  │  └─ If true: Execute SELL trade
   │  ├─ Update equity
   │  └─ Track equity curve
   ├─ Calculate metrics:
   │  ├─ Total trades
   │  ├─ Win rate
   │  ├─ Total return
   │  ├─ Sharpe ratio
   │  ├─ Max drawdown
   │  └─ Profit factor
   └─ Return: trades, equity_curve, metrics

                              │
                              ▼

9. RETURN RESPONSE
   ├─ BacktestResponse:
   │  ├─ success: true
   │  ├─ message: "Backtest completed successfully"
   │  ├─ trades: [Trade1, Trade2, ...]
   │  ├─ equity_curve: [Point1, Point2, ...]
   │  └─ metrics: BacktestMetrics
   └─ Send to frontend

                              │
                              ▼

10. FRONTEND DISPLAYS RESULTS
    ├─ EquityChart: Plot equity curve
    ├─ MetricsCard: Show performance metrics
    ├─ TradesTable: List all trades
    ├─ PerformanceChart: Show performance
    └─ DrawdownChart: Show drawdown analysis
```

---

## 3. Component Interaction Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                    FRONTEND COMPONENTS                          │
└─────────────────────────────────────────────────────────────────┘

                    ┌──────────────────┐
                    │   Home Page      │
                    │   (page.tsx)     │
                    └────────┬─────────┘
                             │
                ┌────────────┼────────────┐
                │            │            │
                ▼            ▼            ▼
        ┌──────────────┐ ┌──────────────┐ ┌──────────────┐
        │ Strategy     │ │ Examples     │ │ API Client   │
        │ Input        │ │ Loader       │ │ (lib/api.ts) │
        │ Component    │ │              │ │              │
        └──────┬───────┘ └──────────────┘ └──────┬───────┘
               │                                  │
               └──────────────┬───────────────────┘
                              │
                    POST /api/backtest
                              │
                              ▼
                    ┌──────────────────┐
                    │  Dashboard Page  │
                    │  (page.tsx)      │
                    └────────┬─────────┘
                             │
        ┌────────────────────┼────────────────────┐
        │                    │                    │
        ▼                    ▼                    ▼
    ┌──────────────┐  ┌──────────────┐  ┌──────────────┐
    │ Equity Chart │  │ Metrics Card │  │ Trades Table │
    │              │  │              │  │              │
    │ Recharts     │  │ Performance  │  │ Sortable     │
    │ Line Chart   │  │ Metrics      │  │ Paginated    │
    └──────────────┘  └──────────────┘  └──────────────┘
        │                    │                    │
        └────────────────────┼────────────────────┘
                             │
                    ┌────────▼────────┐
                    │ Performance     │
                    │ Chart           │
                    └─────────────────┘
                             │
                    ┌────────▼────────┐
                    │ Drawdown Chart  │
                    └─────────────────┘
                             │
                    ┌────────▼────────────────┐
                    │ Strategy Improvement    │
                    │ Modal (Optional)        │
                    │ - LLM Suggestions       │
                    └─────────────────────────┘
```

---

## 4. Service Layer Interaction Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                    BACKEND SERVICES                             │
└─────────────────────────────────────────────────────────────────┘

                    ┌──────────────────┐
                    │  API Endpoint    │
                    │  /api/backtest   │
                    └────────┬─────────┘
                             │
                ┌────────────┼────────────┐
                │            │            │
                ▼            ▼            ▼
        ┌──────────────┐ ┌──────────────┐ ┌──────────────┐
        │ Strategy     │ │ Data Fetcher │ │ Indicators   │
        │ Parser       │ │              │ │              │
        │              │ │ - Format     │ │ - RSI        │
        │ - Parse      │ │   symbol     │ │ - SMA        │
        │   strategy   │ │ - Fetch CSV  │ │ - EMA        │
        │ - Extract    │ │ - Validate   │ │ - MACD       │
        │   conditions │ │   data       │ │ - Bollinger  │
        │              │ │              │ │ - ATR        │
        └──────┬───────┘ └──────┬───────┘ │ - Stochastic │
               │                │         │ - ADX        │
               │                │         └──────┬───────┘
               │                │                │
               └────────────────┼────────────────┘
                                │
                    ┌───────────▼───────────┐
                    │  Backtest Engine      │
                    │                       │
                    │ - Execute trades      │
                    │ - Calculate P&L       │
                    │ - Track equity        │
                    │ - Calculate metrics   │
                    └───────────┬───────────┘
                                │
                    ┌───────────▼───────────┐
                    │  Strategy Improver    │
                    │  (Optional)           │
                    │                       │
                    │ - OpenAI Provider     │
                    │ - Gemini Provider     │
                    │ - Get suggestions     │
                    └───────────────────────┘
```

---

## 5. Database Schema (Conceptual)

```
Note: Current implementation is stateless (no database)
Future enhancement: Add PostgreSQL

┌─────────────────────────────────────────────────────────────────┐
│                    PROPOSED DATABASE SCHEMA                     │
└─────────────────────────────────────────────────────────────────┘

users
├─ id (PK)
├─ email (UNIQUE)
├─ password_hash
├─ created_at
└─ updated_at

strategies
├─ id (PK)
├─ user_id (FK)
├─ name
├─ description
├─ strategy_text
├─ created_at
└─ updated_at

backtests
├─ id (PK)
├─ user_id (FK)
├─ strategy_id (FK)
├─ stock_symbol
├─ start_date
├─ end_date
├─ initial_capital
├─ total_return
├─ sharpe_ratio
├─ max_drawdown
├─ win_rate
├─ created_at
└─ updated_at

trades
├─ id (PK)
├─ backtest_id (FK)
├─ entry_date
├─ entry_price
├─ exit_date
├─ exit_price
├─ quantity
├─ pnl
├─ pnl_percent
└─ created_at
```

---

## 6. Deployment Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    DEPLOYMENT OPTIONS                           │
└─────────────────────────────────────────────────────────────────┘

DEVELOPMENT
├─ Frontend: npm run dev (localhost:3000)
├─ Backend: uvicorn main:app --reload (localhost:8000)
└─ Database: None

PRODUCTION - OPTION 1 (Vercel + Railway)
├─ Frontend
│  └─ Vercel
│     ├─ Auto-deploy from GitHub
│     ├─ CDN for static assets
│     └─ HTTPS enabled
├─ Backend
│  └─ Railway
│     ├─ Docker container
│     ├─ Auto-scaling
│     └─ Environment variables
└─ Database (Optional)
   └─ Railway PostgreSQL

PRODUCTION - OPTION 2 (AWS)
├─ Frontend
│  └─ S3 + CloudFront
│     ├─ Static site hosting
│     ├─ CDN distribution
│     └─ HTTPS enabled
├─ Backend
│  └─ EC2 / ECS
│     ├─ Load balancer
│     ├─ Auto-scaling group
│     └─ Environment variables
└─ Database (Optional)
   └─ RDS PostgreSQL

PRODUCTION - OPTION 3 (Heroku)
├─ Frontend
│  └─ Heroku
│     ├─ Buildpack: Node.js
│     └─ Auto-deploy from GitHub
├─ Backend
│  └─ Heroku
│     ├─ Buildpack: Python
│     ├─ Procfile: web: uvicorn main:app --host 0.0.0.0
│     └─ Environment variables
└─ Database (Optional)
   └─ Heroku PostgreSQL
```

---

## 7. API Request/Response Flow

```
┌─────────────────────────────────────────────────────────────────┐
│                    API FLOW DIAGRAM                             │
└─────────────────────────────────────────────────────────────────┘

REQUEST:
┌──────────────────────────────────────────────────────────────┐
│ POST /api/backtest                                           │
│ Content-Type: application/json                               │
│                                                              │
│ {                                                            │
│   "strategy_text": "Buy when RSI < 30 and sell when RSI > 70",
│   "stock_symbol": "AAPL",                                    │
│   "start_date": "2024-01-01",                                │
│   "end_date": "2024-12-31",                                  │
│   "initial_capital": 10000                                   │
│ }                                                            │
└──────────────────────────────────────────────────────────────┘
                              │
                              ▼
                    ┌──────────────────┐
                    │  Backend Process │
                    │  (5-10 seconds)  │
                    └──────────────────┘
                              │
                              ▼
RESPONSE:
┌──────────────────────────────────────────────────────────────┐
│ 200 OK                                                       │
│ Content-Type: application/json                               │
│                                                              │
│ {                                                            │
│   "success": true,                                           │
│   "message": "Backtest completed successfully",              │
│   "trades": [                                                │
│     {                                                        │
│       "entry_date": "2024-02-13",                            │
│       "entry_price": 183.54,                                 │
│       "exit_date": "2024-05-07",                             │
│       "exit_price": 180.92,                                  │
│       "quantity": 54,                                        │
│       "pnl": -151.20,                                        │
│       "pnl_percent": -1.52                                   │
│     },                                                       │
│     ...                                                      │
│   ],                                                         │
│   "equity_curve": [                                          │
│     {"date": "2024-01-02", "equity": 10000},                 │
│     {"date": "2024-01-03", "equity": 10050},                 │
│     ...                                                      │
│   ],                                                         │
│   "metrics": {                                               │
│     "total_trades": 3,                                       │
│     "winning_trades": 2,                                     │
│     "losing_trades": 1,                                      │
│     "win_rate": 66.67,                                       │
│     "total_return": 1034.92,                                 │
│     "total_return_percent": 10.35,                           │
│     "sharpe_ratio": 0.5667,                                  │
│     "max_drawdown_percent": -10.87,                          │
│     "profit_factor": 4.02,                                   │
│     "avg_win": 517.46,                                       │
│     "avg_loss": -151.20                                      │
│   }                                                          │
│ }                                                            │
└──────────────────────────────────────────────────────────────┘
```

---

## Summary

This architecture provides:

✅ **Clear Separation of Concerns**
- Frontend: UI and user interaction
- Backend: Business logic and data processing
- Services: Modular, reusable components

✅ **Scalability**
- Stateless backend (horizontal scaling)
- No database (can add later)
- Modular service architecture

✅ **Maintainability**
- Clean code structure
- Well-documented components
- Easy to extend

✅ **Performance**
- Fast API responses (5-10 seconds)
- Efficient data processing
- Optimized calculations

✅ **Reliability**
- Error handling
- Input validation
- Logging and monitoring
