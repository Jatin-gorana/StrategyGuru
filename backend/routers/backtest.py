from fastapi import APIRouter, HTTPException
from datetime import datetime
import logging
from typing import Optional, Dict, Any

from models.request_models import BacktestRequest
from models.response_models import BacktestResponse, Trade, EquityCurvePoint, BacktestMetrics
from services.data_fetcher import get_stock_data
from services.strategy_parser import SimpleStrategyParser, StrategyParser
from services.indicators import add_all_indicators
from services.backtest_engine import BacktestEngine

# Configure logging
logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/backtest", response_model=BacktestResponse)
async def run_backtest(request: BacktestRequest):
    """
    Run a backtest on a trading strategy.
    
    This endpoint:
    1. Parses the natural language strategy
    2. Fetches historical stock data
    3. Calculates technical indicators
    4. Runs the backtest engine
    5. Returns performance metrics and equity curve
    
    Args:
        request: BacktestRequest containing:
            - strategy_text: Natural language strategy description
            - stock_symbol: Stock ticker symbol (e.g., 'AAPL')
            - start_date: Start date (YYYY-MM-DD)
            - end_date: End date (YYYY-MM-DD)
            - initial_capital: Starting capital (default: $10,000)
    
    Returns:
        BacktestResponse with:
            - success: Boolean indicating success
            - message: Status message
            - trades: List of executed trades
            - equity_curve: Daily equity values
            - metrics: Performance metrics
    
    Raises:
        HTTPException: 400 for validation errors, 500 for server errors
    """
    try:
        logger.info(f"Starting backtest for {request.stock_symbol}")
        
        # Step 1: Parse strategy
        logger.info(f"Parsing strategy: {request.strategy_text[:50]}...")
        strategy_rules = _parse_strategy(request.strategy_text)
        
        # Step 2: Fetch historical data
        logger.info(f"Fetching data for {request.stock_symbol} from {request.start_date} to {request.end_date}")
        df = get_stock_data(
            request.stock_symbol,
            request.start_date,
            request.end_date
        )
        
        if df.empty:
            raise ValueError(f"No data found for {request.stock_symbol} in the specified date range")
        
        logger.info(f"Fetched {len(df)} days of data")
        
        # Step 3: Calculate indicators
        logger.info("Calculating technical indicators")
        df = add_all_indicators(df)
        
        # Step 4: Generate buy/sell signals from parsed strategy
        logger.info("Generating trading signals")
        buy_condition, sell_condition = _generate_signals(df, strategy_rules)
        
        # Step 5: Run backtest
        logger.info("Running backtest engine")
        engine = BacktestEngine(
            df,
            initial_capital=request.initial_capital,
            commission=0.001,  # 0.1% commission
            slippage=0.0
        )
        trades, equity_curve, metrics = engine.run_backtest(buy_condition, sell_condition)
        
        logger.info(f"Backtest completed: {metrics.total_trades} trades, {metrics.total_return_percent:.2f}% return")
        
        # Convert to response models
        response_trades = [
            Trade(
                entry_date=t.entry_date,
                entry_price=t.entry_price,
                exit_date=t.exit_date,
                exit_price=t.exit_price,
                quantity=t.quantity,
                pnl=t.pnl,
                pnl_percent=t.pnl_percent
            )
            for t in trades
        ]
        
        response_equity = [
            EquityCurvePoint(date=ec.date, equity=ec.equity)
            for ec in equity_curve
        ]
        
        response_metrics = BacktestMetrics(
            total_return=metrics.total_return,
            total_return_percent=metrics.total_return_percent,
            sharpe_ratio=metrics.sharpe_ratio,
            max_drawdown=metrics.max_drawdown,
            max_drawdown_percent=metrics.max_drawdown_percent,
            win_rate=metrics.win_rate,
            total_trades=metrics.total_trades,
            winning_trades=metrics.winning_trades,
            losing_trades=metrics.losing_trades,
            avg_win=metrics.avg_win,
            avg_loss=metrics.avg_loss,
            profit_factor=metrics.profit_factor
        )
        
        return BacktestResponse(
            success=True,
            message=f"Backtest completed successfully. {metrics.total_trades} trades executed.",
            trades=response_trades,
            equity_curve=response_equity,
            metrics=response_metrics
        )
    
    except ValueError as e:
        logger.error(f"Validation error: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Backtest error: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Backtest failed: {str(e)}")


@router.post("/backtest/parse-strategy")
async def parse_strategy_endpoint(strategy_text: str):
    """
    Parse a natural language strategy into structured rules.
    
    Args:
        strategy_text: Natural language strategy description
    
    Returns:
        Parsed strategy rules as JSON
    """
    try:
        logger.info(f"Parsing strategy: {strategy_text[:50]}...")
        rules = SimpleStrategyParser.parse(strategy_text)
        
        return {
            "success": True,
            "buy_condition": rules.buy_condition,
            "sell_condition": rules.sell_condition,
            "indicators_required": rules.indicators_required,
            "parameters": rules.parameters
        }
    except Exception as e:
        logger.error(f"Strategy parsing error: {str(e)}")
        raise HTTPException(status_code=400, detail=f"Failed to parse strategy: {str(e)}")


@router.get("/backtest/indicators")
async def get_supported_indicators():
    """
    Get list of supported indicators.
    
    Returns:
        List of supported indicators with descriptions
    """
    indicators = {
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
    
    return {
        "success": True,
        "indicators": indicators
    }


@router.get("/backtest/examples")
async def get_strategy_examples():
    """
    Get example strategies.
    
    Returns:
        List of example strategies with descriptions
    """
    examples = [
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
        },
        {
            "name": "MACD Crossover",
            "description": "Buy when MACD line crosses above signal line, sell on opposite crossover",
            "strategy": "Buy when MACD > Signal and sell when MACD < Signal",
            "indicators": ["MACD"],
            "risk_level": "Medium"
        },
        {
            "name": "EMA Trend Following",
            "description": "Buy when fast EMA crosses above slow EMA, sell on opposite crossover",
            "strategy": "Buy when EMA(12) > EMA(26) and sell when EMA(12) < EMA(26)",
            "indicators": ["EMA"],
            "risk_level": "Medium"
        },
        {
            "name": "Combined RSI and MA",
            "description": "Buy when RSI is oversold AND price is above 200-day MA, sell when RSI is overbought OR price falls below MA",
            "strategy": "Buy when RSI < 30 and SMA(50) > SMA(200) and sell when RSI > 70 or SMA(50) < SMA(200)",
            "indicators": ["RSI", "SMA"],
            "risk_level": "Low"
        },
        {
            "name": "Bollinger Bands Breakout",
            "description": "Buy when price breaks above upper Bollinger Band, sell when it breaks below lower band",
            "strategy": "Buy when price > Bollinger Upper Band and sell when price < Bollinger Lower Band",
            "indicators": ["Bollinger Bands"],
            "risk_level": "High"
        }
    ]
    
    return {
        "success": True,
        "examples": examples
    }


def _parse_strategy(strategy_text: str):
    """
    Parse strategy text using SimpleStrategyParser.
    
    Args:
        strategy_text: Natural language strategy description
    
    Returns:
        StrategyRules object
    """
    try:
        rules = SimpleStrategyParser.parse(strategy_text)
        return rules
    except Exception as e:
        logger.error(f"Strategy parsing failed: {str(e)}")
        raise ValueError(f"Failed to parse strategy: {str(e)}")


def _generate_signals(df, strategy_rules):
    """
    Generate buy/sell signals from parsed strategy rules.
    
    Args:
        df: DataFrame with indicators
        strategy_rules: Parsed strategy rules
    
    Returns:
        Tuple of (buy_condition, sell_condition) as boolean Series
    """
    try:
        # Convert strategy conditions to pandas boolean Series
        buy_condition = _evaluate_condition(df, strategy_rules.buy_condition)
        sell_condition = _evaluate_condition(df, strategy_rules.sell_condition)
        
        return buy_condition, sell_condition
    except Exception as e:
        logger.error(f"Signal generation failed: {str(e)}")
        raise ValueError(f"Failed to generate signals: {str(e)}")


def _evaluate_condition(df, condition_text: str):
    """
    Evaluate a condition string against DataFrame.
    
    Args:
        df: DataFrame with indicators
        condition_text: Condition string (e.g., "RSI < 30")
    
    Returns:
        Boolean Series
    """
    if not condition_text:
        return df.index.to_series().apply(lambda x: False)
    
    condition_lower = condition_text.lower().strip()
    
    # Handle RSI conditions
    if 'rsi' in condition_lower:
        if 'rsi < 30' in condition_lower or 'rsi<30' in condition_lower:
            return df['RSI'] < 30
        elif 'rsi > 70' in condition_lower or 'rsi>70' in condition_lower:
            return df['RSI'] > 70
        elif 'rsi <' in condition_lower:
            import re
            match = re.search(r'rsi\s*<\s*(\d+)', condition_lower)
            if match:
                threshold = int(match.group(1))
                return df['RSI'] < threshold
        elif 'rsi >' in condition_lower:
            import re
            match = re.search(r'rsi\s*>\s*(\d+)', condition_lower)
            if match:
                threshold = int(match.group(1))
                return df['RSI'] > threshold
    
    # Handle SMA conditions
    if 'sma' in condition_lower:
        if 'sma(50) > sma(200)' in condition_lower or 'sma50 > sma200' in condition_lower:
            return df['MA50'] > df['MA200']
        elif 'sma(50) < sma(200)' in condition_lower or 'sma50 < sma200' in condition_lower:
            return df['MA50'] < df['MA200']
    
    # Handle EMA conditions
    if 'ema' in condition_lower:
        if 'ema(12) > ema(26)' in condition_lower or 'ema12 > ema26' in condition_lower:
            return df['EMA12'] > df['EMA26']
        elif 'ema(12) < ema(26)' in condition_lower or 'ema12 < ema26' in condition_lower:
            return df['EMA12'] < df['EMA26']
    
    # Handle MACD conditions
    if 'macd' in condition_lower:
        if 'macd > signal' in condition_lower:
            return df['MACD'] > df['MACD_Signal']
        elif 'macd < signal' in condition_lower:
            return df['MACD'] < df['MACD_Signal']
    
    # Handle price conditions
    if 'price' in condition_lower or 'close' in condition_lower:
        if 'price > sma(200)' in condition_lower or 'close > sma200' in condition_lower:
            return df['close'] > df['MA200']
        elif 'price < sma(200)' in condition_lower or 'close < sma200' in condition_lower:
            return df['close'] < df['MA200']
    
    # Default: no signal
    logger.warning(f"Could not parse condition: {condition_text}")
    return df.index.to_series().apply(lambda x: False)


@router.post("/backtest/improve-strategy")
async def improve_strategy(
    strategy_text: str,
    metrics: Dict[str, Any],
    trades_count: int = 0
):
    """
    Get LLM suggestions to improve a trading strategy.
    
    Args:
        strategy_text: Current strategy description
        metrics: Backtest metrics dictionary
        trades_count: Number of trades executed
    
    Returns:
        Strategy improvement suggestions
    """
    try:
        logger.info(f"Improving strategy: {strategy_text[:50]}...")
        
        from services.strategy_improver import StrategyImprover
        
        # Try OpenAI first, fall back to Gemini
        try:
            improver = StrategyImprover(provider='openai')
        except ValueError:
            try:
                improver = StrategyImprover(provider='gemini')
            except ValueError:
                raise ValueError(
                    "No LLM API key configured. Set OPENAI_API_KEY or GOOGLE_API_KEY environment variable."
                )
        
        improvement = improver.improve_strategy(
            strategy_text=strategy_text,
            metrics=metrics,
            trades_count=trades_count
        )
        
        logger.info("Strategy improvement generated successfully")
        
        return {
            "success": True,
            "original_strategy": improvement.original_strategy,
            "improved_strategy": improvement.improved_strategy,
            "improvements": improvement.improvements,
            "reasoning": improvement.reasoning,
            "risk_level": improvement.risk_level
        }
    
    except ValueError as e:
        logger.error(f"Validation error: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Strategy improvement error: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to improve strategy: {str(e)}")
