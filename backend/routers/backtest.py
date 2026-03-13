from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from datetime import datetime, date
import logging
from typing import Optional, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession

from models.request_models import BacktestRequest, ImproveStrategyRequest
from models.response_models import BacktestResponse, Trade, EquityCurvePoint, BacktestMetrics
from services.data_fetcher import get_stock_data
from services.strategy_parser import SimpleStrategyParser, StrategyParser, DSLConverter
from services.indicators import add_all_indicators
from services.backtest_engine import BacktestEngine
from services.dsl_sandbox import SandboxExecutor
from services.dsl_parser import parse_dsl
from services.backtest_persistence import save_backtest_results
from database.database import get_db
from database.auth import get_current_user
from database.models import User
from database.crud import (
    create_strategy, create_backtest, update_backtest_metrics,
    create_trade, create_equity_point
)

# Configure logging
logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/backtest", response_model=BacktestResponse)
async def run_backtest(
    request: BacktestRequest,
    background_tasks: BackgroundTasks,
    current_user: Optional[User] = Depends(get_current_user),
    db: Optional[AsyncSession] = Depends(get_db)
):
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
        
        # Step 1: Fetch historical data
        logger.info(f"Fetching data for {request.stock_symbol} from {request.start_date} to {request.end_date}")
        df = get_stock_data(
            request.stock_symbol,
            request.start_date,
            request.end_date
        )
        
        if df.empty:
            raise ValueError(f"No data found for {request.stock_symbol} in the specified date range")
        
        logger.info(f"Fetched {len(df)} days of data")
        
        # Step 2: Calculate indicators
        logger.info("Calculating technical indicators")
        df = add_all_indicators(df)
        
        # Step 3: Parse strategy and generate signals using smart routing
        logger.info(f"Parsing strategy: {request.strategy_text[:50]}...")
        
        # SECURITY CHECK: Detect malicious patterns before processing
        malicious_patterns = [
            'import ', 'from ', 'exec(', 'eval(', '__import__',
            'os.system', 'os.remove', 'os.rmdir', 'os.unlink',
            'subprocess.', 'socket.', 'requests.', 'urllib.',
            'open(', '.read(', '.write(', '.delete(',
            'drop table', 'delete from', 'truncate',
            '__getattr__', '__setattr__', '__delattr__',
            'globals(', 'locals(', 'vars(', 'dir(',
            'compile(', 'getattr(', 'setattr(', 'delattr(',
            'lambda:', 'def ', 'class ', 'import',
            'password =', 'secret =', 'token =', 'key =',
            'db_password', 'db_secret', 'api_key', 'api_secret'
        ]
        
        strategy_lower = request.strategy_text.lower()
        for pattern in malicious_patterns:
            if pattern in strategy_lower:
                logger.error(f"SECURITY VIOLATION: Malicious pattern detected: {pattern}")
                raise HTTPException(
                    status_code=400,
                    detail=f"Security violation: Malicious pattern detected in strategy. Pattern: '{pattern}' is not allowed."
                )
        
        # SMART ROUTING: Detect complex keywords to decide which parser to use
        complex_keywords = [
            'break', 'breakout', 'cross', 'crosses', 'touch', 'touches',
            'volume', 'high volume', 'low volume', 'increasing volume', 'decreasing volume',
            'support', 'resistance', 'trend', 'momentum', 'divergence',
            'confirmation', 'filter', 'condition'
        ]
        
        is_complex_strategy = any(keyword in strategy_lower for keyword in complex_keywords)
        
        try:
            if is_complex_strategy:
                # Complex strategy → Use Groq LLM parser (primary provider)
                logger.info("🧠 Complex strategy detected, using Groq LLM parser for better understanding")
                strategy_rules = _parse_strategy(request.strategy_text)
                buy_condition, sell_condition = _generate_signals(df, strategy_rules)
                logger.info("✅ Using Groq LLM parser (SMART ROUTING - COMPLEX)")
            else:
                # Simple strategy → Use DSL (fast and secure)
                logger.info("⚡ Simple strategy detected, using DSL parser for speed")
                dsl_text = DSLConverter.to_dsl(request.strategy_text)
                logger.info(f"Converted to DSL: {dsl_text[:100]}...")
                
                strategy_ast = parse_dsl(dsl_text)
                sandbox = SandboxExecutor(df)
                buy_condition, sell_condition = sandbox.execute(strategy_ast)
                logger.info("✅ Using DSL sandbox executor (SMART ROUTING - SIMPLE)")
        
        except Exception as e:
            logger.error(f"Parser execution failed: {str(e)}")
            # Only fallback if it's a parsing error, not a security error
            if "not allowed" in str(e).lower() or "security" in str(e).lower():
                raise HTTPException(status_code=400, detail=str(e))
            
            # If DSL failed, try Groq as fallback
            if not is_complex_strategy:
                logger.warning(f"DSL failed, falling back to Groq LLM parser: {str(e)}")
                try:
                    strategy_rules = _parse_strategy(request.strategy_text)
                    buy_condition, sell_condition = _generate_signals(df, strategy_rules)
                    logger.info("✅ Using Groq LLM parser (FALLBACK FROM DSL)")
                except Exception as llm_error:
                    logger.error(f"Groq parser also failed: {str(llm_error)}")
                    raise HTTPException(status_code=400, detail=f"Failed to parse strategy: {str(llm_error)}")
            else:
                logger.error(f"Groq parser failed: {str(e)}")
                raise HTTPException(status_code=400, detail=f"Failed to parse strategy: {str(e)}")
        
        # Step 4: Run backtest
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
        
        # Schedule database persistence as background task
        # This ensures the API response is returned immediately
        if current_user:
            # Convert trades to dictionaries for background task
            trades_data = [
                {
                    'entry_date': t.entry_date,
                    'exit_date': t.exit_date,
                    'entry_price': t.entry_price,
                    'exit_price': t.exit_price,
                    'pnl': t.pnl,
                    'pnl_percent': t.pnl_percent
                }
                for t in trades
            ]
            
            # Convert equity curve to dictionaries for background task
            equity_data = [
                {
                    'date': ec.date,
                    'equity': ec.equity
                }
                for ec in equity_curve
            ]
            
            # Add background task for database persistence
            background_tasks.add_task(
                save_backtest_results,
                trades=trades_data,
                equity_curve=equity_data,
                metrics={
                    'total_return': metrics.total_return,
                    'total_return_percent': metrics.total_return_percent,
                    'sharpe_ratio': metrics.sharpe_ratio,
                    'max_drawdown': metrics.max_drawdown,
                    'max_drawdown_percent': metrics.max_drawdown_percent,
                    'win_rate': metrics.win_rate,
                    'profit_factor': metrics.profit_factor,
                    'total_trades': metrics.total_trades
                },
                user_id=current_user.id,
                strategy_text=request.strategy_text,
                stock_symbol=request.stock_symbol,
                start_date=date.fromisoformat(request.start_date),
                end_date=date.fromisoformat(request.end_date),
                initial_capital=request.initial_capital
            )
            logger.info(f"Scheduled background persistence for user {current_user.email}")
        
        # Return response immediately (database save happens in background)
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
async def improve_strategy(request: ImproveStrategyRequest):
    """
    Get LLM suggestions to improve a trading strategy.
    
    Args:
        request: ImproveStrategyRequest with:
            - strategy_text: Current strategy description
            - metrics: Backtest metrics dictionary
            - trades_count: Number of trades executed (optional)
    
    Returns:
        Strategy improvement suggestions
    """
    try:
        strategy_text = request.strategy_text
        metrics = request.metrics
        trades_count = request.trades_count
        
        if not strategy_text:
            raise ValueError("strategy_text is required")
        if not metrics:
            raise ValueError("metrics is required")
        
        logger.info(f"Improving strategy: {strategy_text[:50]}...")
        
        from services.strategy_improver import StrategyImprover
        
        # Use Groq as the primary (and only) provider
        try:
            improver = StrategyImprover(provider='groq')
            logger.info("Using Groq for strategy improvement")
        except ValueError as e:
            logger.error(f"Groq not available: {str(e)}")
            raise ValueError(
                "Groq API key not configured. Set GROQ_API_KEY environment variable."
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
