import pandas as pd
import numpy as np
from datetime import datetime
from typing import List, Tuple, Callable, Optional, Dict, Any
from dataclasses import dataclass


@dataclass
class Trade:
    """Represents a single trade."""
    entry_date: datetime
    entry_price: float
    exit_date: datetime
    exit_price: float
    quantity: int
    pnl: float
    pnl_percent: float
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert trade to dictionary."""
        return {
            'entry_date': self.entry_date,
            'entry_price': self.entry_price,
            'exit_date': self.exit_date,
            'exit_price': self.exit_price,
            'quantity': self.quantity,
            'pnl': round(self.pnl, 2),
            'pnl_percent': round(self.pnl_percent, 2)
        }


@dataclass
class EquityCurvePoint:
    """Represents a point in the equity curve."""
    date: datetime
    equity: float
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'date': self.date,
            'equity': round(self.equity, 2)
        }


@dataclass
class BacktestMetrics:
    """Performance metrics from backtest."""
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
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert metrics to dictionary."""
        return {
            'total_return': round(self.total_return, 2),
            'total_return_percent': round(self.total_return_percent, 2),
            'sharpe_ratio': round(self.sharpe_ratio, 4),
            'max_drawdown': round(self.max_drawdown, 4),
            'max_drawdown_percent': round(self.max_drawdown_percent, 2),
            'win_rate': round(self.win_rate, 2),
            'total_trades': self.total_trades,
            'winning_trades': self.winning_trades,
            'losing_trades': self.losing_trades,
            'avg_win': round(self.avg_win, 2),
            'avg_loss': round(self.avg_loss, 2),
            'profit_factor': round(self.profit_factor, 2)
        }


class BacktestEngine:
    """
    Backtesting engine for trading strategies.
    
    Executes trading strategies on historical data and calculates
    performance metrics including returns, Sharpe ratio, drawdown, and win rate.
    """
    
    def __init__(
        self,
        data: pd.DataFrame,
        initial_capital: float = 10000,
        commission: float = 0.001,
        slippage: float = 0.0
    ):
        """
        Initialize backtest engine.
        
        Args:
            data: DataFrame with OHLCV data (must have 'close' column)
            initial_capital: Starting capital in USD (default: $10,000)
            commission: Commission per trade as decimal (default: 0.1%)
            slippage: Slippage per trade as decimal (default: 0%)
        """
        self.data = data.copy()
        self.initial_capital = initial_capital
        self.commission = commission
        self.slippage = slippage
        
        # State tracking
        self.trades: List[Trade] = []
        self.equity_curve: List[EquityCurvePoint] = []
        self.position: Optional[Dict[str, Any]] = None
        self.cash = initial_capital
        self.equity = initial_capital
        self.peak_equity = initial_capital
    
    def run_backtest(
        self,
        buy_condition: pd.Series,
        sell_condition: pd.Series
    ) -> Tuple[List[Trade], List[EquityCurvePoint], BacktestMetrics]:
        """
        Run backtest with buy and sell conditions.
        
        Args:
            buy_condition: Boolean Series indicating buy signals
            sell_condition: Boolean Series indicating sell signals
            
        Returns:
            Tuple of (trades, equity_curve, metrics)
        """
        if len(buy_condition) != len(self.data):
            raise ValueError("buy_condition length must match data length")
        if len(sell_condition) != len(self.data):
            raise ValueError("sell_condition length must match data length")
        
        # Reset state
        self.trades = []
        self.equity_curve = []
        self.position = None
        self.cash = self.initial_capital
        self.equity = self.initial_capital
        self.peak_equity = self.initial_capital
        
        # Execute backtest
        for i in range(len(self.data)):
            row = self.data.iloc[i]
            close_price = row['close']
            date = row.name if isinstance(row.name, datetime) else row.get('date', datetime.now())
            
            # Handle buy signal
            if buy_condition.iloc[i] and self.position is None:
                self._enter_position(date, close_price)
            
            # Handle sell signal
            elif sell_condition.iloc[i] and self.position is not None:
                self._exit_position(date, close_price)
            
            # Update equity
            self._update_equity(close_price, date)
        
        # Close any open position at end
        if self.position is not None:
            last_row = self.data.iloc[-1]
            close_price = last_row['close']
            date = last_row.name if isinstance(last_row.name, datetime) else last_row.get('date', datetime.now())
            self._exit_position(date, close_price)
        
        # Calculate metrics
        metrics = self._calculate_metrics()
        
        return self.trades, self.equity_curve, metrics
    
    def _enter_position(self, date: datetime, price: float) -> None:
        """Enter a long position."""
        # Apply slippage
        entry_price = price * (1 + self.slippage)
        
        # Calculate quantity
        quantity = int(self.cash / entry_price)
        
        if quantity > 0:
            cost = quantity * entry_price
            commission = cost * self.commission
            total_cost = cost + commission
            
            if total_cost <= self.cash:
                self.position = {
                    'entry_date': date,
                    'entry_price': entry_price,
                    'quantity': quantity,
                    'entry_cost': total_cost
                }
                self.cash -= total_cost
    
    def _exit_position(self, date: datetime, price: float) -> None:
        """Exit the current position."""
        if self.position is None:
            return
        
        # Apply slippage
        exit_price = price * (1 - self.slippage)
        
        # Calculate P&L
        gross_pnl = (exit_price - self.position['entry_price']) * self.position['quantity']
        commission = (exit_price * self.position['quantity']) * self.commission
        net_pnl = gross_pnl - commission
        pnl_percent = (net_pnl / self.position['entry_cost']) * 100 if self.position['entry_cost'] > 0 else 0
        
        # Record trade
        trade = Trade(
            entry_date=self.position['entry_date'],
            entry_price=self.position['entry_price'],
            exit_date=date,
            exit_price=exit_price,
            quantity=self.position['quantity'],
            pnl=net_pnl,
            pnl_percent=pnl_percent
        )
        self.trades.append(trade)
        
        # Update cash
        proceeds = exit_price * self.position['quantity'] - commission
        self.cash += proceeds
        self.position = None
    
    def _update_equity(self, close_price: float, date: datetime) -> None:
        """Update current equity value."""
        if self.position is not None:
            position_value = self.position['quantity'] * close_price
            self.equity = self.cash + position_value
        else:
            self.equity = self.cash
        
        # Track peak equity for drawdown calculation
        if self.equity > self.peak_equity:
            self.peak_equity = self.equity
        
        # Record equity curve point
        self.equity_curve.append(EquityCurvePoint(date=date, equity=self.equity))
    
    def _calculate_metrics(self) -> BacktestMetrics:
        """Calculate comprehensive performance metrics."""
        final_equity = self.equity
        total_return = final_equity - self.initial_capital
        total_return_percent = (total_return / self.initial_capital) * 100
        
        # Sharpe Ratio (annualized)
        sharpe_ratio = self._calculate_sharpe_ratio()
        
        # Max Drawdown
        max_drawdown, max_drawdown_percent = self._calculate_max_drawdown()
        
        # Trade statistics
        if len(self.trades) > 0:
            winning_trades = sum(1 for t in self.trades if t.pnl > 0)
            losing_trades = len(self.trades) - winning_trades
            win_rate = (winning_trades / len(self.trades)) * 100
            
            winning_pnls = [t.pnl for t in self.trades if t.pnl > 0]
            losing_pnls = [abs(t.pnl) for t in self.trades if t.pnl < 0]
            
            avg_win = np.mean(winning_pnls) if winning_pnls else 0
            avg_loss = np.mean(losing_pnls) if losing_pnls else 0
            profit_factor = avg_win / avg_loss if avg_loss > 0 else 0
        else:
            winning_trades = 0
            losing_trades = 0
            win_rate = 0
            avg_win = 0
            avg_loss = 0
            profit_factor = 0
        
        return BacktestMetrics(
            total_return=total_return,
            total_return_percent=total_return_percent,
            sharpe_ratio=sharpe_ratio,
            max_drawdown=max_drawdown,
            max_drawdown_percent=max_drawdown_percent,
            win_rate=win_rate,
            total_trades=len(self.trades),
            winning_trades=winning_trades,
            losing_trades=losing_trades,
            avg_win=avg_win,
            avg_loss=avg_loss,
            profit_factor=profit_factor
        )
    
    def _calculate_sharpe_ratio(self, risk_free_rate: float = 0.02) -> float:
        """
        Calculate annualized Sharpe ratio.
        
        Args:
            risk_free_rate: Annual risk-free rate (default: 2%)
            
        Returns:
            Sharpe ratio
        """
        if len(self.equity_curve) < 2:
            return 0
        
        equity_values = [ec.equity for ec in self.equity_curve]
        returns = pd.Series(equity_values).pct_change().dropna()
        
        if len(returns) == 0 or returns.std() == 0:
            return 0
        
        excess_return = returns.mean() - (risk_free_rate / 252)
        sharpe = (excess_return / returns.std()) * np.sqrt(252)
        
        return sharpe
    
    def _calculate_max_drawdown(self) -> Tuple[float, float]:
        """
        Calculate maximum drawdown.
        
        Returns:
            Tuple of (max_drawdown_decimal, max_drawdown_percent)
        """
        if len(self.equity_curve) == 0:
            return 0, 0
        
        equity_values = np.array([ec.equity for ec in self.equity_curve])
        running_max = np.maximum.accumulate(equity_values)
        drawdown = (equity_values - running_max) / running_max
        max_drawdown = np.min(drawdown)
        max_drawdown_percent = max_drawdown * 100
        
        return max_drawdown, max_drawdown_percent
    
    def get_summary(self) -> Dict[str, Any]:
        """Get backtest summary as dictionary."""
        metrics = self._calculate_metrics()
        
        return {
            'initial_capital': self.initial_capital,
            'final_equity': round(self.equity, 2),
            'total_trades': len(self.trades),
            'trades': [t.to_dict() for t in self.trades],
            'equity_curve': [ec.to_dict() for ec in self.equity_curve],
            'metrics': metrics.to_dict()
        }


class StrategyBacktester:
    """
    High-level interface for backtesting strategies.
    
    Simplifies running backtests with custom strategy functions.
    """
    
    def __init__(self, data: pd.DataFrame, initial_capital: float = 10000):
        """
        Initialize strategy backtester.
        
        Args:
            data: DataFrame with OHLCV data
            initial_capital: Starting capital
        """
        self.data = data
        self.initial_capital = initial_capital
    
    def backtest(
        self,
        strategy_func: Callable[[pd.DataFrame], Tuple[pd.Series, pd.Series]]
    ) -> Tuple[List[Trade], List[EquityCurvePoint], BacktestMetrics]:
        """
        Run backtest with a strategy function.
        
        Args:
            strategy_func: Function that takes DataFrame and returns
                          (buy_signals, sell_signals) as boolean Series
        
        Returns:
            Tuple of (trades, equity_curve, metrics)
        """
        buy_signals, sell_signals = strategy_func(self.data)
        
        engine = BacktestEngine(self.data, self.initial_capital)
        return engine.run_backtest(buy_signals, sell_signals)
