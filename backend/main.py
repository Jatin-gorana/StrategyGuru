from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers import backtest

app = FastAPI(
    title="AI Trading Strategy Backtester",
    description="Backtest trading strategies using historical stock data",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(backtest.router, prefix="/api", tags=["backtest"])

@app.get("/health")
def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
