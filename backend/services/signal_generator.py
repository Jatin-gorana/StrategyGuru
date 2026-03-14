"""
signal_generator.py

Robust signal generation from natural language strategy conditions.
Handles:
    - Operator normalization: "falls below" → "<", "exceeds" → ">"
    - RSI with any threshold
    - EMA / SMA / MA with any period, including "50-day MA" format
    - MA crossover detection (actual crossover, not just above/below)
    - MACD crossover
    - Bollinger Bands
    - Volume conditions
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

    # Strip trailing punctuation (periods, exclamation marks, etc.)
    t = re.sub(r'[.!?;]+$', '', t)
    # Also strip trailing punctuation from sub-clauses
    t = re.sub(r'[.!?;]+(\s|$)', r'\1', t)

    # Remove filler words: "the", "a", "an"
    t = re.sub(r'\b(the|a|an)\b', '', t)

    # Normalize "N-day MA/EMA/SMA" → "ma(N)" / "ema(N)" / "sma(N)"
    # Must happen BEFORE operator normalization so "crosses above" still exists
    t = re.sub(r'(\d+)[- ]?day\s+moving\s+average', r'ma(\1)', t, flags=re.IGNORECASE)
    t = re.sub(r'(\d+)[- ]?day\s+ema', r'ema(\1)', t, flags=re.IGNORECASE)
    t = re.sub(r'(\d+)[- ]?day\s+sma', r'sma(\1)', t, flags=re.IGNORECASE)
    t = re.sub(r'(\d+)[- ]?day\s+ma', r'ma(\1)', t, flags=re.IGNORECASE)
    t = re.sub(r'(\d+)[- ]?(?:period|week|bar)\s+(?:ma|sma|ema)', lambda m: f'ma({m.group(1)})', t)

    # Common threshold keywords (BEFORE removing "is" so "is oversold" → "< 30")
    t = re.sub(r'\b(?:is\s+)?oversold\b', '< 30', t)
    t = re.sub(r'\b(?:is\s+)?overbought\b', '> 70', t)

    # Directional verb phrases → comparison operators
    t = re.sub(r'\b(falls?\s+below|drops?\s+below|goes?\s+below|crosses?\s+below|dips?\s+below|is\s+below|moves?\s+below|below)\b', '<', t)
    t = re.sub(r'\b(rises?\s+above|goes?\s+above|crosses?\s+above|breaks?\s+above|climbs?\s+above|moves?\s+above|is\s+above|above)\b', '>', t)
    t = re.sub(r'\b(is\s+greater\s+than|greater\s+than)\b', '>', t)
    t = re.sub(r'\b(is\s+less\s+than|less\s+than)\b', '<', t)
    t = re.sub(r'\b(exceeds?|surpass(?:es)?|is\s+over|over)\b', '>', t)
    t = re.sub(r'\b(at\s+least)\b', '>=', t)
    t = re.sub(r'\b(at\s+most)\b', '<=', t)

    # Remove remaining standalone "is" that wasn't part of a phrase above
    t = re.sub(r'\bis\b', '', t)

    # Collapse whitespace
    t = re.sub(r'\s+', ' ', t).strip()
    return t


# ─────────────────────────────────────────────────────────────────────────────
# Period extractor — handles ALL naming formats
# ─────────────────────────────────────────────────────────────────────────────

def _extract_ma_periods(clause: str) -> list:
    """
    Extract MA/SMA period numbers from any format:
      - ma(50), ma50, ma 50
      - sma(200), sma200
      - 50-day ma  (already normalized to ma(50) by normalize_nlp)
      - ma(50)
    Returns list of ints found.
    """
    # Standard: ma(50), ma50, ma 50, sma(200), sma200
    periods = [int(x) for x in re.findall(r'(?:sma|ma)\s*\(?\s*(\d+)\s*\)?', clause)]
    return periods


def _extract_ema_periods(clause: str) -> list:
    """Extract EMA period numbers from any format."""
    periods = [int(x) for x in re.findall(r'ema\s*\(?\s*(\d+)\s*\)?', clause)]
    return periods


# ─────────────────────────────────────────────────────────────────────────────
# Indicator helpers (lazy computation into df)
# ─────────────────────────────────────────────────────────────────────────────

def _get_rsi(df: pd.DataFrame, period: int = 14) -> pd.Series:
    col = f'RSI{period}'
    # Also check for 'RSI' column (default name from add_all_indicators)
    if col not in df.columns:
        if period == 14 and 'RSI' in df.columns:
            return df['RSI'].fillna(50)
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
    """Get SMA/MA for a given period. Checks MA{n}, SMA{n}, and computes if needed."""
    col = f'SMA{period}'
    if col in df.columns:
        return df[col].fillna(df['close'])
    # Check for MA-prefixed columns (from add_all_indicators)
    ma_col = f'MA{period}'
    if ma_col in df.columns:
        return df[ma_col].fillna(df['close'])
    # Compute and cache
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
    logger.info(f"evaluate_single_clause: '{clause}'")
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
                result = compare[op].fillna(False)
                logger.info(f"  RSI {op} {val}: {result.sum()} signals")
                return result
        # Try reversed format: "30 > rsi"
        for op in ['>=', '<=', '>', '<']:
            m = re.search(rf'(\d+(?:\.\d+)?)\s*{re.escape(op)}\s*rsi', clause)
            if m:
                val = float(m.group(1))
                reverse_op = {'>': '<', '<': '>', '>=': '<=', '<=': '>='}
                rop = reverse_op[op]
                compare = {'>=': rsi >= val, '<=': rsi <= val, '>': rsi > val, '<': rsi < val}
                result = compare[rop].fillna(False)
                logger.info(f"  RSI (reversed) {rop} {val}: {result.sum()} signals")
                return result
        logger.warning(f"RSI clause '{clause}' — no operator/value found")
        return false_series

    # ── MACD ─────────────────────────────────────────────────────────────────
    if 'macd' in clause:
        macd, signal = _get_macd(df)
        if 'cross' in clause.lower():
            # Actual crossover detection
            if '>' in clause:
                result = ((macd > signal) & (macd.shift(1) <= signal.shift(1))).fillna(False)
            else:
                result = ((macd < signal) & (macd.shift(1) >= signal.shift(1))).fillna(False)
        else:
            result = (macd > signal if '>' in clause else macd < signal).fillna(False)
        logger.info(f"  MACD clause: {result.sum()} signals")
        return result

    # ── EMA ──────────────────────────────────────────────────────────────────
    if 'ema' in clause and 'sma' not in clause:
        periods = _extract_ema_periods(clause)
        if len(periods) >= 2:
            a, b = _get_ema(df, periods[0]), _get_ema(df, periods[1])
            if 'cross' in clause.lower():
                if '>' in clause:
                    result = ((a > b) & (a.shift(1) <= b.shift(1))).fillna(False)
                else:
                    result = ((a < b) & (a.shift(1) >= b.shift(1))).fillna(False)
            else:
                result = (a > b if '>' in clause else a < b).fillna(False)
            logger.info(f"  EMA crossover {periods}: {result.sum()} signals")
            return result
        elif len(periods) == 1:
            ema_val = _get_ema(df, periods[0])
            if '>' in clause:
                result = (df['close'] > ema_val).fillna(False)
            elif '<' in clause:
                result = (df['close'] < ema_val).fillna(False)
            else:
                return false_series
            logger.info(f"  Price vs EMA{periods[0]}: {result.sum()} signals")
            return result
        return false_series

    # ── SMA / MA ─────────────────────────────────────────────────────────────
    if 'sma' in clause or ('ma' in clause and 'macd' not in clause):
        periods = _extract_ma_periods(clause)
        if len(periods) >= 2:
            a, b = _get_sma(df, periods[0]), _get_sma(df, periods[1])
            # Detect if this is a crossover request
            original_lower = clause.lower()
            is_crossover = any(w in original_lower for w in ['cross', 'crosses', 'crossed'])
            if is_crossover:
                if '>' in clause:
                    result = ((a > b) & (a.shift(1) <= b.shift(1))).fillna(False)
                else:
                    result = ((a < b) & (a.shift(1) >= b.shift(1))).fillna(False)
                logger.info(f"  MA CROSSOVER {periods[0]} vs {periods[1]}: {result.sum()} signals")
            else:
                result = (a > b if '>' in clause else a < b).fillna(False)
                logger.info(f"  MA {periods[0]} {'>' if '>' in clause else '<'} MA {periods[1]}: {result.sum()} signals")
            return result
        elif len(periods) == 1:
            sma_val = _get_sma(df, periods[0])
            if '>' in clause:
                result = (df['close'] > sma_val).fillna(False)
            elif '<' in clause:
                result = (df['close'] < sma_val).fillna(False)
            else:
                return false_series
            logger.info(f"  Price vs SMA{periods[0]}: {result.sum()} signals")
            return result
        return false_series

    # ── Bollinger Bands ───────────────────────────────────────────────────────
    if 'bollinger' in clause or 'bband' in clause or ('band' in clause and ('upper' in clause or 'lower' in clause)):
        sma20 = df['close'].rolling(20).mean()
        std20 = df['close'].rolling(20).std()
        upper = (sma20 + 2 * std20).fillna(df['close'])
        lower = (sma20 - 2 * std20).fillna(df['close'])
        if 'lower' in clause or ('<' in clause and 'upper' not in clause):
            return (df['close'] < lower).fillna(False)
        return (df['close'] > upper).fillna(False)

    # ── Volume ────────────────────────────────────────────────────────────────
    if 'volume' in clause:
        m = re.search(r'volume\s*([<>]=?)\s*(\d+(?:\.\d+)?)', clause)
        if m:
            op, val = m.group(1), float(m.group(2))
            ops = {'>': df['volume'] > val, '<': df['volume'] < val,
                   '>=': df['volume'] >= val, '<=': df['volume'] <= val}
            return ops.get(op, false_series).fillna(False)
        # "volume above average" or "high volume"
        if 'average' in clause or 'avg' in clause:
            avg_vol = df['volume'].rolling(20).mean()
            if '>' in clause or 'high' in clause:
                return (df['volume'] > avg_vol).fillna(False)
            return (df['volume'] < avg_vol).fillna(False)

    # ── Generic price vs number ───────────────────────────────────────────────
    m = re.search(r'(?:price|close)\s*([<>]=?)\s*(\d+(?:\.\d+)?)', clause)
    if m:
        op, val = m.group(1), float(m.group(2))
        ops = {'>': df['close'] > val, '<': df['close'] < val,
               '>=': df['close'] >= val, '<=': df['close'] <= val}
        return ops.get(op, false_series).fillna(False)

    # ── Last resort: try to find ANY indicator pattern ────────────────────────
    # Check for standalone number comparison: "something > 70"
    m = re.search(r'([<>]=?)\s*(\d+(?:\.\d+)?)', clause)
    if m:
        op, val = m.group(1), float(m.group(2))
        # If RSI is likely (val between 0-100 and no other indicator mentioned)
        if 0 < val <= 100 and not any(ind in clause for ind in ['ma', 'ema', 'sma', 'macd', 'volume', 'price', 'close']):
            rsi = _get_rsi(df, 14)
            compare = {'>=': rsi >= val, '<=': rsi <= val, '>': rsi > val, '<': rsi < val}
            result = compare.get(op, false_series)
            if hasattr(result, 'fillna'):
                result = result.fillna(False)
                logger.info(f"  Fallback RSI {op} {val}: {result.sum()} signals")
                return result

    logger.warning(f"Unrecognized clause: '{clause}' -> returning all False")
    return false_series


# ─────────────────────────────────────────────────────────────────────────────
# Full compound condition evaluator
# ─────────────────────────────────────────────────────────────────────────────

def evaluate_condition(df: pd.DataFrame, condition_text: str) -> pd.Series:
    """
    Evaluate a full condition string (possibly compound with AND/OR) against df.

    Examples:
        "RSI falls below 30 and price above EMA20"
        "50-day MA crosses above 200-day MA"
        "MACD > Signal"
        "EMA(12) > EMA(26) OR RSI < 35"
    """
    if not condition_text or not condition_text.strip():
        return pd.Series([False] * len(df), index=df.index)

    # Strip trailing punctuation from the entire condition
    cleaned = re.sub(r'[.!?;]+\s*$', '', condition_text.strip())

    normalized = normalize_nlp(cleaned)
    logger.info(f"Condition: '{condition_text}' -> '{normalized}'")

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
        logger.info(f"  Clause '{part}': {clause_result.sum()} signals")

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
    Also handles sentence-separated buy/sell conditions.
    """
    text = strategy_text
    text = re.sub(r'\b(enter\s+long|go\s+long|long\s+position|open\s+long)\b', 'buy', text, flags=re.IGNORECASE)
    text = re.sub(r'\b(exit\s+long|exit\s+trade|exit\s+position|close\s+position)\b', 'sell', text, flags=re.IGNORECASE)
    # Handle standalone "exit" (when not already part of "exit long" etc.)
    text = re.sub(r'\bexit\b', 'sell', text, flags=re.IGNORECASE)
    return text
