"""
DSL Sandbox - Safely executes DSL AST in an isolated environment.

Only allows specific, safe operations. Blocks all dangerous operations.
"""

import pandas as pd
import numpy as np
from typing import Union, Callable, Dict, Any
import logging

from .dsl_parser import (
    ASTNode, NumberNode, IndicatorNode, ComparisonNode,
    BinaryOpNode, UnaryOpNode, StrategyNode
)

logger = logging.getLogger(__name__)


class SecurityError(Exception):
    """Raised when a security violation is detected."""
    pass


class SandboxExecutor:
    """Safely executes DSL AST in a sandbox."""
    
    # Allowed indicators
    ALLOWED_INDICATORS = {
        'RSI', 'SMA', 'EMA', 'MACD', 'PRICE', 'CLOSE',
        'BOLLINGER', 'ATR', 'STOCHASTIC', 'ADX', 'HIGH', 'LOW',
        'VOLUME'
    }
    
    # Allowed operators
    ALLOWED_OPERATORS = {
        '<', '>', '<=', '>=', '==', '!=',
        'AND', 'OR', 'NOT'
    }
    
    def __init__(self, df: pd.DataFrame):
        """
        Initialize sandbox with dataframe.
        
        Args:
            df: DataFrame with OHLCV data
        """
        self.df = df.copy()
        self._validate_dataframe()
        self._calculate_indicators()
    
    def _validate_dataframe(self):
        """Validate dataframe has required columns."""
        required = ['open', 'high', 'low', 'close', 'volume']
        for col in required:
            if col not in self.df.columns:
                raise ValueError(f"DataFrame missing required column: {col}")
    
    def _calculate_indicators(self):
        """Pre-calculate all indicators."""
        logger.info("Calculating indicators for sandbox")
        
        # RSI
        self.df['RSI'] = self._calc_rsi(14)
        
        # SMAs
        for period in [20, 50, 100, 200]:
            self.df[f'SMA{period}'] = self.df['close'].rolling(window=period).mean()
        
        # EMAs
        for period in [12, 26, 50]:
            self.df[f'EMA{period}'] = self.df['close'].ewm(span=period).mean()
        
        # MACD
        ema12 = self.df['close'].ewm(span=12).mean()
        ema26 = self.df['close'].ewm(span=26).mean()
        self.df['MACD'] = ema12 - ema26
        self.df['MACD_Signal'] = self.df['MACD'].ewm(span=9).mean()
        
        # Bollinger Bands
        sma20 = self.df['close'].rolling(window=20).mean()
        std20 = self.df['close'].rolling(window=20).std()
        self.df['BB_Upper'] = sma20 + (std20 * 2)
        self.df['BB_Lower'] = sma20 - (std20 * 2)
        
        # ATR
        self.df['ATR'] = self._calc_atr(14)
        
        # HIGH and LOW (N-day high/low)
        for period in [5, 10, 20, 50]:
            self.df[f'HIGH{period}'] = self.df['high'].rolling(window=period).max()
            self.df[f'LOW{period}'] = self.df['low'].rolling(window=period).min()
        
        # Volume indicators
        self.df['VOLUME_MA'] = self.df['volume'].rolling(window=20).mean()
        self.df['VOLUME_HIGH'] = self.df['volume'] > self.df['VOLUME_MA']
        self.df['VOLUME_LOW'] = self.df['volume'] < self.df['VOLUME_MA']
        
        logger.info("Indicators calculated successfully")
    
    def execute(self, strategy: StrategyNode) -> tuple:
        """
        Execute strategy and return buy/sell signals.
        
        Args:
            strategy: StrategyNode AST
            
        Returns:
            (buy_signals, sell_signals) as boolean arrays
        """
        logger.info("Executing strategy in sandbox")
        
        buy_signals = pd.Series([False] * len(self.df), index=self.df.index)
        sell_signals = pd.Series([False] * len(self.df), index=self.df.index)
        
        if strategy.buy_condition:
            buy_signals = self._eval_node(strategy.buy_condition)
        
        if strategy.sell_condition:
            sell_signals = self._eval_node(strategy.sell_condition)
        
        logger.info(f"Buy signals: {buy_signals.sum()} days")
        logger.info(f"Sell signals: {sell_signals.sum()} days")
        
        return buy_signals, sell_signals
    
    def _eval_node(self, node: ASTNode) -> Union[pd.Series, bool, float]:
        """Recursively evaluate AST node."""
        if isinstance(node, NumberNode):
            return node.value
        
        elif isinstance(node, IndicatorNode):
            return self._eval_indicator(node)
        
        elif isinstance(node, ComparisonNode):
            return self._eval_comparison(node)
        
        elif isinstance(node, BinaryOpNode):
            return self._eval_binary_op(node)
        
        elif isinstance(node, UnaryOpNode):
            return self._eval_unary_op(node)
        
        else:
            raise SecurityError(f"Unknown node type: {type(node)}")
    
    def _eval_indicator(self, node: IndicatorNode) -> pd.Series:
        """Evaluate indicator node."""
        name = node.name
        period = node.period
        
        # Validate indicator is allowed
        if name not in self.ALLOWED_INDICATORS:
            raise SecurityError(f"Indicator not allowed: {name}")
        
        logger.debug(f"Evaluating indicator: {name}({period})")
        
        if name == 'RSI':
            return self.df['RSI']
        elif name == 'SMA':
            col = f'SMA{period}' if period else 'SMA200'
            return self.df[col]
        elif name == 'EMA':
            col = f'EMA{period}' if period else 'EMA12'
            return self.df[col]
        elif name == 'MACD':
            return self.df['MACD']
        elif name == 'PRICE' or name == 'CLOSE':
            return self.df['close']
        elif name == 'BOLLINGER':
            return self.df['BB_Upper']
        elif name == 'ATR':
            return self.df['ATR']
        elif name == 'HIGH':
            col = f'HIGH{period}' if period else 'HIGH20'
            return self.df[col]
        elif name == 'LOW':
            col = f'LOW{period}' if period else 'LOW20'
            return self.df[col]
        elif name == 'VOLUME':
            # Return volume high/low based on context
            # Default to high volume (above average)
            return self.df['VOLUME_HIGH']
        else:
            raise SecurityError(f"Indicator not implemented: {name}")
    
    def _eval_comparison(self, node: ComparisonNode) -> pd.Series:
        """Evaluate comparison node."""
        left = self._eval_node(node.left)
        right = self._eval_node(node.right)
        op = node.operator
        
        # Validate operator is allowed
        if op not in self.ALLOWED_OPERATORS:
            raise SecurityError(f"Operator not allowed: {op}")
        
        logger.debug(f"Comparison: {op}")
        
        if op == '<':
            return left < right
        elif op == '>':
            return left > right
        elif op == '<=':
            return left <= right
        elif op == '>=':
            return left >= right
        elif op == '==':
            return left == right
        elif op == '!=':
            return left != right
        else:
            raise SecurityError(f"Unknown operator: {op}")
    
    def _eval_binary_op(self, node: BinaryOpNode) -> pd.Series:
        """Evaluate binary operation node."""
        left = self._eval_node(node.left)
        right = self._eval_node(node.right)
        op = node.operator
        
        # Validate operator is allowed
        if op not in self.ALLOWED_OPERATORS:
            raise SecurityError(f"Operator not allowed: {op}")
        
        logger.debug(f"Binary op: {op}")
        
        if op == 'AND':
            return left & right
        elif op == 'OR':
            return left | right
        else:
            raise SecurityError(f"Unknown binary operator: {op}")
    
    def _eval_unary_op(self, node: UnaryOpNode) -> pd.Series:
        """Evaluate unary operation node."""
        operand = self._eval_node(node.operand)
        op = node.operator
        
        # Validate operator is allowed
        if op not in self.ALLOWED_OPERATORS:
            raise SecurityError(f"Operator not allowed: {op}")
        
        logger.debug(f"Unary op: {op}")
        
        if op == 'NOT':
            return ~operand
        else:
            raise SecurityError(f"Unknown unary operator: {op}")
    
    def _calc_rsi(self, period: int = 14) -> pd.Series:
        """Calculate RSI indicator."""
        delta = self.df['close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        return rsi.fillna(50)  # Fill NaN with neutral value
    
    def _calc_atr(self, period: int = 14) -> pd.Series:
        """Calculate ATR indicator."""
        high_low = self.df['high'] - self.df['low']
        high_close = abs(self.df['high'] - self.df['close'].shift())
        low_close = abs(self.df['low'] - self.df['close'].shift())
        
        tr = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)
        atr = tr.rolling(window=period).mean()
        return atr.fillna(tr.mean())
