"""
signal_generator.py

Robust signal generation from natural language strategy conditions.
Handles:
    - Operator normalization: "falls below" → "<", "above" → ">"
    - RSI with any threshold
    - EMA / SMA with any period
    - MACD crossover
    - Bollinger Bands
    - Compound conditions joined by AND / OR
"""

import re
import logging
import pandas as pd

logger = logging.getLogger(__name__)


# ─────────────────────────────────────────────────────────────────────────────
# NLP Normalizer
# ─────────────────────────────────────────────────────────────────────────────

def normalize_nlp(text: str) -> str:
    """Convert natural language phrases into operator notation."""
    t = text.lower().strip()

    # Directional verb phrases → comparison operators
    t = re.sub(r'\b(falls?\s+below|drops?\s+below|goes?\s+below|crosses?\s+below|is\s+below|below)\b', '<', t)
    t = re.sub(r'\b(rises?\s+above|goes?\s+above|crosses?\s+above|breaks?\s+above|is\s+above|above)\b', '>', t)
    t = re.sub(r'\b(is\s+greater\s+than|greater\s+than)\b', '>', t)
    t = re.sub(r'\b(is\s+less\s+than|less\s+than)\b', '<', t)
    t = re.sub(r'\b(at\s+least)\b', '>=', t)
    t = re.sub(r'\b(at\s+most)\b', '<=', t)

    # Common threshold keywords
    t = re.sub(r'\boversold\b', '< 30', t)
    t = re.sub(r'\boverbought\b', '> 70', t)

    # Collapse whitespace
    t = re.sub(r'\s+', ' ', t).strip()
    return t


# ─────────────────────────────────────────────────────────────────────────────
# Indicator helpers (lazy computation into df)
# ─────────────────────────────────────────────────────────────────────────────

def _get_rsi(df: pd.DataFrame, period: int = 14) -> pd.Series:
    col = f'RSI{period}'
    if col not in df.columns:
        delta = df['close'].diff()
        gain = delta.where(delta > 0, 0).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        rs = gain / loss.replace(0, 1e-9)
        df[col] = (100 - 100 / (1 + rs)).fillna(50)
    return df[col]


def _get_ema(df: pd.DataFrame, period: int) -> pd.Series:
    col = f'EMA{period}'
    if col not in df.columns:
        df[col] = df['close'].ewm(span=period, adjust=False).mean()
    return df[col].fillna(df['close'])


def _get_sma(df: pd.DataFrame, period: int) -> pd.Series:
    col = f'SMA{period}'
    if col not in df.columns:
        df[col] = df['close'].rolling(window=period).mean()
    return df[col].fillna(df['close'])


def _get_macd(df: pd.DataFrame):
    if 'MACD' not in df.columns:
        ema12 = df['close'].ewm(span=12, adjust=False).mean()
        ema26 = df['close'].ewm(span=26, adjust=False).mean()
        df['MACD'] = ema12 - ema26
        df['MACD_Signal'] = df['MACD'].ewm(span=9, adjust=False).mean()
    return df['MACD'], df['MACD_Signal']


# ─────────────────────────────────────────────────────────────────────────────
# Single clause evaluator
# ─────────────────────────────────────────────────────────────────────────────

def evaluate_single_clause(df: pd.DataFrame, clause: str) -> pd.Series:
    """
    Evaluate one atomic condition clause (no 'and'/'or') against the DataFrame.
    Returns a boolean Series the same length as df.
    """
    clause = normalize_nlp(clause)
    logger.debug(f"Evaluating clause: '{clause}'")
    false_series = pd.Series([False] * len(df), index=df.index)

    # ── RSI ─────────────────────────────────────────────────────────────────
    if 'rsi' in clause:
        # Try to find period like rsi(14) or rsi14, default 14
        period_match = re.search(r'rsi\s*\(?\s*(\d+)\s*\)?', clause)
        period = int(period_match.group(1)) if period_match else 14
        rsi = _get_rsi(df, period)
        for op in ['>=', '<=', '>', '<']:
            m = re.search(rf'rsi(?:\s*\(?\s*\d+\s*\)?)?\s*{re.escape(op)}\s*(\d+(?:\.\d+)?)', clause)
            if m:
                val = float(m.group(1))
                compare = {'>=': rsi >= val, '<=': rsi <= val, '>': rsi > val, '<': rsi < val}
                return compare[op].fillna(False)
        return false_series

    # ── MACD ─────────────────────────────────────────────────────────────────
    if 'macd' in clause:
        macd, signal = _get_macd(df)
        return (macd > signal if '>' in clause else macd < signal).fillna(False)

    # ── EMA ──────────────────────────────────────────────────────────────────
    if 'ema' in clause:
        periods = [int(x) for x in re.findall(r'ema\s*\(?\s*(\d+)\s*\)?', clause)]
        if len(periods) >= 2:
            a, b = _get_ema(df, periods[0]), _get_ema(df, periods[1])
            return (a > b if '>' in clause else a < b).fillna(False)
        elif len(periods) == 1:
            ema_val = _get_ema(df, periods[0])
            # Check which side price is on
            if re.search(r'(price|close)\s*>', clause) or re.search(r'>\s*ema', clause):
                return (df['close'] > ema_val).fillna(False)
            elif re.search(r'(price|close)\s*<', clause) or re.search(r'<\s*ema', clause):
                return (df['close'] < ema_val).fillna(False)
        return false_series

    # ── SMA ──────────────────────────────────────────────────────────────────
    if 'sma' in clause or ('ma' in clause and 'macd' not in clause):
        periods = [int(x) for x in re.findall(r'(?:sma|ma)\s*\(?\s*(\d+)\s*\)?', clause)]
        if len(periods) >= 2:
            a, b = _get_sma(df, periods[0]), _get_sma(df, periods[1])
            return (a > b if '>' in clause else a < b).fillna(False)
        elif len(periods) == 1:
            sma_val = _get_sma(df, periods[0])
            if re.search(r'(price|close)\s*>|>\s*(?:sma|ma)', clause):
                return (df['close'] > sma_val).fillna(False)
            elif re.search(r'(price|close)\s*<|<\s*(?:sma|ma)', clause):
                return (df['close'] < sma_val).fillna(False)
        return false_series

    # ── Bollinger Bands ───────────────────────────────────────────────────────
    if 'bollinger' in clause or 'band' in clause:
        sma20 = df['close'].rolling(20).mean()
        std20 = df['close'].rolling(20).std()
        upper = (sma20 + 2 * std20).fillna(df['close'])
        lower = (sma20 - 2 * std20).fillna(df['close'])
        if 'lower' in clause or ('<' in clause and 'upper' not in clause):
            return (df['close'] < lower).fillna(False)
        return (df['close'] > upper).fillna(False)

    # ── Generic price vs number ───────────────────────────────────────────────
    m = re.search(r'(?:price|close)\s*([<>]=?)\s*(\d+(?:\.\d+)?)', clause)
    if m:
        op, val = m.group(1), float(m.group(2))
        ops = {'>': df['close'] > val, '<': df['close'] < val,
               '>=': df['close'] >= val, '<=': df['close'] <= val}
        return ops.get(op, false_series).fillna(False)

    logger.warning(f"Unrecognized clause: '{clause}' → returning all False")
    return false_series


# ─────────────────────────────────────────────────────────────────────────────
# Full compound condition evaluator
# ─────────────────────────────────────────────────────────────────────────────

def evaluate_condition(df: pd.DataFrame, condition_text: str) -> pd.Series:
    """
    Evaluate a full condition string (possibly compound with AND/OR) against df.

    Examples:
        "RSI falls below 30 and price above EMA20"
        "RSI < 30 AND PRICE > EMA(20)"
        "MACD > Signal"
        "EMA(12) > EMA(26) OR RSI < 35"
    """
    if not condition_text or not condition_text.strip():
        return pd.Series([False] * len(df), index=df.index)

    normalized = normalize_nlp(condition_text)
    logger.info(f"Condition: '{condition_text}' → '{normalized}'")

    # Split into clauses on 'and' / 'or'
    parts = re.split(r'\b(and|or)\b', normalized, flags=re.IGNORECASE)

    result = None
    pending_op = 'and'

    for part in parts:
        part = part.strip()
        if not part:
            continue
        if part.lower() == 'and':
            pending_op = 'and'
            continue
        if part.lower() == 'or':
            pending_op = 'or'
            continue

        clause_result = evaluate_single_clause(df, part).fillna(False)

        if result is None:
            result = clause_result
        elif pending_op == 'and':
            result = result & clause_result
        else:
            result = result | clause_result

    if result is None:
        return pd.Series([False] * len(df), index=df.index)
    return result.astype(bool)


# ─────────────────────────────────────────────────────────────────────────────
# Strategy text pre-processor
# ─────────────────────────────────────────────────────────────────────────────

def preprocess_strategy_text(strategy_text: str) -> str:
    """
    Normalize strategy keywords before feeding to the parser:
      - 'enter long' / 'go long' → 'buy'
      - 'exit' / 'close position' → 'sell'
    """
    text = strategy_text
    text = re.sub(r'\b(enter\s+long|go\s+long|long\s+position|open\s+long)\b', 'buy', text, flags=re.IGNORECASE)
    text = re.sub(r'\b(exit|close\s+position|exit\s+long|exit\s+trade)\b', 'sell', text, flags=re.IGNORECASE)
    return text
