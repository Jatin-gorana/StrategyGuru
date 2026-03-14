from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from datetime import datetime, date
import logging
from typing import Optional, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession

from models.request_models import BacktestRequest, ImproveStrategyRequest
from models.response_models import BacktestResponse, Trade, EquityCurvePoint, BacktestMetrics
from services.data_fetcher import get_stock_data
from services.strategy_parser import SimpleStrategyParser, StrategyParser, DSLConverter
from services.signal_generator import evaluate_condition, preprocess_strategy_text
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
        
        # Step 3: Parse strategy and generate signals using robust NLP signal generator
        logger.info(f"[STRATEGY] Raw input: '{request.strategy_text}'")

        # Pre-process natural language keywords to standard form
        processed_text = preprocess_strategy_text(request.strategy_text)
        logger.info(f"[STRATEGY] After preprocess: '{processed_text}'")

        # Parse buy/sell conditions using SimpleStrategyParser (regex-based)
        try:
            strategy_rules = _parse_strategy(request.strategy_text)
            logger.info(f"[PARSED] buy_condition='{strategy_rules.buy_condition}'")
            logger.info(f"[PARSED] sell_condition='{strategy_rules.sell_condition}'")
        except Exception as parse_err:
            logger.error(f"[PARSE ERROR] {parse_err}")
            raise HTTPException(status_code=400, detail=f"Could not parse strategy: {parse_err}")

        # Validate we got at least a buy condition
        if not strategy_rules.buy_condition or not strategy_rules.buy_condition.strip():
            logger.error(f"[EMPTY BUY] Parser extracted empty buy_condition from: '{request.strategy_text}'")
            raise HTTPException(
                status_code=400,
                detail=f"Could not extract buy condition from your strategy. "
                       f"Please start with 'Buy when...' or 'Enter long when...'"
            )

        # Generate buy/sell signals using our robust NLP evaluator
        try:
            logger.info(f"[SIGNAL GEN] Evaluating buy: '{strategy_rules.buy_condition}'")
            buy_condition = evaluate_condition(df, strategy_rules.buy_condition)
            logger.info(f"[SIGNAL GEN] buy signals count: {buy_condition.sum()}")

            logger.info(f"[SIGNAL GEN] Evaluating sell: '{strategy_rules.sell_condition}'")
            sell_condition = evaluate_condition(df, strategy_rules.sell_condition)
            logger.info(f"[SIGNAL GEN] sell signals count: {sell_condition.sum()}")

            # Log DataFrame columns for debugging
            logger.info(f"[DF COLUMNS] {list(df.columns)}")
            logger.info(f"[DF SHAPE] {df.shape}")
            if 'RSI' in df.columns:
                logger.info(f"[RSI SAMPLE] RSI min={df['RSI'].min():.1f} max={df['RSI'].max():.1f} mean={df['RSI'].mean():.1f}")

        except Exception as sig_err:
            logger.error(f"[SIGNAL ERROR] {sig_err}", exc_info=True)
            raise HTTPException(status_code=500, detail=f"Signal generation failed: {sig_err}")

        # SAFETY FALLBACK: If zero buy signals and strategy has compound conditions,
        # try simplifying the strategy by removing compound clauses
        if buy_condition.sum() == 0 and ' and ' in strategy_rules.buy_condition.lower():
            logger.warning(f"[ZERO BUY SIGNALS] Compound condition produced 0 signals. Attempting simplification...")
            
            simplified_text = _simplify_strategy_text(processed_text)
            logger.info(f"[SIMPLIFIED] Original: '{processed_text}' → Simplified: '{simplified_text}'")
            
            if simplified_text:
                try:
                    simplified_rules = SimpleStrategyParser.parse(simplified_text)
                    logger.info(f"[SIMPLIFIED PARSED] buy='{simplified_rules.buy_condition}', sell='{simplified_rules.sell_condition}'")
                    
                    if simplified_rules.buy_condition:
                        simplified_buy = evaluate_condition(df, simplified_rules.buy_condition)
                        logger.info(f"[SIMPLIFIED] buy signals: {simplified_buy.sum()}")
                        
                        if simplified_buy.sum() > 0:
                            buy_condition = simplified_buy
                            # Also use simplified sell if available, otherwise keep original
                            if simplified_rules.sell_condition:
                                simplified_sell = evaluate_condition(df, simplified_rules.sell_condition)
                                if simplified_sell.sum() > 0:
                                    sell_condition = simplified_sell
                            logger.info(f"[FALLBACK SUCCESS] Using simplified strategy. Buy: {buy_condition.sum()}, Sell: {sell_condition.sum()}")
                except Exception as simp_err:
                    logger.warning(f"[SIMPLIFIED FAILED] {simp_err}")
        
        # Log final signal counts
        if buy_condition.sum() == 0:
            logger.warning(f"[ZERO BUY SIGNALS] No buy signals generated for: '{strategy_rules.buy_condition}'")
        if sell_condition.sum() == 0:
            logger.warning(f"[ZERO SELL SIGNALS] No sell signals generated for: '{strategy_rules.sell_condition}'")

        
        # Step 4: Run backtest
        logger.info(f"Running backtest engine with {buy_condition.sum()} buy and {sell_condition.sum()} sell signals")
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
    Parse strategy text, normalizing natural language before parsing.
    'Enter long' -> 'buy', 'exit' -> 'sell', etc.
    Falls back to simplified parsing if compound conditions fail.
    """
    text = preprocess_strategy_text(strategy_text)
    try:
        rules = SimpleStrategyParser.parse(text)
        logger.info(f"Parsed strategy: buy='{rules.buy_condition}', sell='{rules.sell_condition}'")
        return rules
    except Exception as e:
        logger.error(f"Strategy parsing failed: {str(e)}")
        raise ValueError(f"Failed to parse strategy: {str(e)}")


def _generate_signals(df, strategy_rules):
    """
    Generate buy/sell signals from parsed strategy rules.
    Uses the robust signal_generator.evaluate_condition function.
    """
    try:
        buy_condition = evaluate_condition(df, strategy_rules.buy_condition)
        sell_condition = evaluate_condition(df, strategy_rules.sell_condition)
        logger.info(f"Buy signals: {buy_condition.sum()} days | Sell signals: {sell_condition.sum()} days")
        return buy_condition, sell_condition
    except Exception as e:
        logger.error(f"Signal generation failed: {str(e)}")
        raise ValueError(f"Failed to generate signals: {str(e)}")


def _simplify_strategy_text(strategy_text: str) -> str:
    """
    Simplify a compound strategy into individual indicator conditions.
    Removes compound clauses that might cause zero signals when combined.
    
    For example:
      "buy when RSI < 30 and price above EMA20" → "buy when RSI < 30"
    
    The idea: keep only the primary indicator condition to ensure signals.
    """
    import re
    text = strategy_text.lower()
    
    # Try to extract just the first condition from compound buy
    # Look for "buy when X and Y" → keep just X
    buy_match = re.search(
        r'buy\s+(?:when|if)?\s*(.+?)(?:\s+and\s+|\s+or\s+)',
        text, re.IGNORECASE
    )
    sell_match = re.search(
        r'sell\s+(?:when|if)?\s*(.+?)$',
        text, re.IGNORECASE
    )
    
    simplified_buy = buy_match.group(1).strip() if buy_match else ''
    simplified_sell = sell_match.group(1).strip() if sell_match else ''
    
    # Clean up punctuation
    simplified_buy = re.sub(r'[.!?;,]+$', '', simplified_buy).strip()
    simplified_sell = re.sub(r'[.!?;,]+$', '', simplified_sell).strip()
    
    result = ''
    if simplified_buy:
        result += f"buy when {simplified_buy}"
    if simplified_sell:
        result += f" sell when {simplified_sell}"
    
    return result.strip()


def _evaluate_condition(df, condition_text: str):
    """
    Wrapper around signal_generator.evaluate_condition for backward compatibility.
    """
    return evaluate_condition(df, condition_text)



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
