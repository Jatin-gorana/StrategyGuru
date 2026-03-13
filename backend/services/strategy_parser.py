import json
import re
import os
from typing import Dict, Any, Optional, Tuple
from abc import ABC, abstractmethod
from dataclasses import dataclass, asdict
import pandas as pd
import logging

logger = logging.getLogger(__name__)


@dataclass
class StrategyRules:
    """Structured trading strategy rules."""
    buy_condition: str
    sell_condition: str
    indicators_required: list
    parameters: Dict[str, Any]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return asdict(self)
    
    def to_json(self) -> str:
        """Convert to JSON string."""
        return json.dumps(self.to_dict(), indent=2)


class LLMProvider(ABC):
    """Abstract base class for LLM providers."""
    
    @abstractmethod
    def parse_strategy(self, strategy_text: str) -> StrategyRules:
        """Parse strategy text using LLM."""
        pass


class OpenAIProvider(LLMProvider):
    """OpenAI API provider for strategy parsing."""
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize OpenAI provider.
        
        Args:
            api_key: OpenAI API key (defaults to OPENAI_API_KEY env var)
        """
        self.api_key = api_key or os.getenv('OPENAI_API_KEY')
        if not self.api_key:
            raise ValueError("OPENAI_API_KEY not provided or set in environment")
        
        try:
            from openai import OpenAI
            self.client = OpenAI(api_key=self.api_key)
        except ImportError:
            raise ImportError("openai package not installed. Install with: pip install openai")
    
    def parse_strategy(self, strategy_text: str) -> StrategyRules:
        """
        Parse strategy text using OpenAI API.
        
        Args:
            strategy_text: Natural language strategy description
            
        Returns:
            StrategyRules object with parsed conditions
        """
        prompt = self._build_prompt(strategy_text)
        
        response = self.client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a trading strategy expert. Extract trading rules from natural language descriptions and return valid JSON."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3,
            response_format={"type": "json_object"}
        )
        
        response_text = response.choices[0].message.content
        return self._parse_response(response_text)
    
    def _build_prompt(self, strategy_text: str) -> str:
        """Build the prompt for OpenAI."""
        return f"""
Extract trading rules from the following strategy description and return a JSON object.

Strategy: {strategy_text}

Return a JSON object with this exact structure:
{{
    "buy_condition": "condition description",
    "sell_condition": "condition description",
    "indicators_required": ["list", "of", "indicators"],
    "parameters": {{
        "rsi_period": 14,
        "ma_short": 50,
        "ma_long": 200,
        "other_params": "as needed"
    }}
}}

Supported indicators: RSI, SMA, EMA, MACD, Bollinger Bands, ATR, Stochastic, ADX
Supported operators: <, >, <=, >=, ==, !=, and, or, not

Examples:
- "RSI < 30" for oversold
- "RSI > 70" for overbought
- "SMA(50) > SMA(200)" for moving average crossover
- "MACD > Signal" for MACD crossover
- "Price > Bollinger Upper Band" for breakout

Be precise and use standard indicator notation.
"""
    
    def _parse_response(self, response_text: str) -> StrategyRules:
        """Parse JSON response from OpenAI."""
        try:
            data = json.loads(response_text)
            return StrategyRules(
                buy_condition=data.get('buy_condition', ''),
                sell_condition=data.get('sell_condition', ''),
                indicators_required=data.get('indicators_required', []),
                parameters=data.get('parameters', {})
            )
        except json.JSONDecodeError as e:
            raise ValueError(f"Failed to parse LLM response as JSON: {e}")


class GeminiProvider(LLMProvider):
    """Google Gemini API provider for strategy parsing."""
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize Gemini provider.
        
        Args:
            api_key: Google API key (defaults to GOOGLE_API_KEY env var)
        """
        self.api_key = api_key or os.getenv('GOOGLE_API_KEY')
        if not self.api_key:
            raise ValueError("GOOGLE_API_KEY not provided or set in environment")
        
        try:
            import google.generativeai as genai
            genai.configure(api_key=self.api_key)
            self.model = genai.GenerativeModel('gemini-pro')
        except ImportError:
            raise ImportError("google-generativeai package not installed. Install with: pip install google-generativeai")
    
    def parse_strategy(self, strategy_text: str) -> StrategyRules:
        """
        Parse strategy text using Google Gemini API.
        
        Args:
            strategy_text: Natural language strategy description
            
        Returns:
            StrategyRules object with parsed conditions
        """
        prompt = self._build_prompt(strategy_text)
        
        response = self.model.generate_content(prompt)
        response_text = response.text
        
        return self._parse_response(response_text)
    
    def _build_prompt(self, strategy_text: str) -> str:
        """Build the prompt for Gemini."""
        return f"""
Extract trading rules from the following strategy description and return a JSON object.

Strategy: {strategy_text}

Return ONLY a valid JSON object with this exact structure (no markdown, no extra text):
{{
    "buy_condition": "condition description",
    "sell_condition": "condition description",
    "indicators_required": ["list", "of", "indicators"],
    "parameters": {{
        "rsi_period": 14,
        "ma_short": 50,
        "ma_long": 200,
        "other_params": "as needed"
    }}
}}

Supported indicators: RSI, SMA, EMA, MACD, Bollinger Bands, ATR, Stochastic, ADX
Supported operators: <, >, <=, >=, ==, !=, and, or, not

Examples:
- "RSI < 30" for oversold
- "RSI > 70" for overbought
- "SMA(50) > SMA(200)" for moving average crossover
- "MACD > Signal" for MACD crossover
- "Price > Bollinger Upper Band" for breakout

Be precise and use standard indicator notation. Return only the JSON object.
"""
    
    def _parse_response(self, response_text: str) -> StrategyRules:
        """Parse JSON response from Gemini."""
        try:
            # Extract JSON from response (in case there's extra text)
            json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
            if not json_match:
                raise ValueError("No JSON found in response")
            
            json_str = json_match.group(0)
            data = json.loads(json_str)
            
            return StrategyRules(
                buy_condition=data.get('buy_condition', ''),
                sell_condition=data.get('sell_condition', ''),
                indicators_required=data.get('indicators_required', []),
                parameters=data.get('parameters', {})
            )
        except json.JSONDecodeError as e:
            raise ValueError(f"Failed to parse LLM response as JSON: {e}")


class GroqProvider(LLMProvider):
    """Groq API provider for strategy parsing."""
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize Groq provider.
        
        Args:
            api_key: Groq API key (defaults to GROQ_API_KEY env var)
        """
        self.api_key = api_key or os.getenv('GROQ_API_KEY')
        if not self.api_key:
            raise ValueError("GROQ_API_KEY not provided or set in environment")
        
        try:
            from groq import Groq
            self.client = Groq(api_key=self.api_key)
        except ImportError:
            raise ImportError("groq package not installed. Install with: pip install groq")
    
    def parse_strategy(self, strategy_text: str) -> StrategyRules:
        """
        Parse strategy text using Groq API.
        
        Args:
            strategy_text: Natural language strategy description
            
        Returns:
            StrategyRules object with parsed conditions
        """
        prompt = self._build_prompt(strategy_text)
        
        response = self.client.chat.completions.create(
            model="mixtral-8x7b-32768",
            messages=[
                {"role": "system", "content": "You are a trading strategy expert. Extract trading rules from natural language descriptions and return valid JSON."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3
        )
        
        response_text = response.choices[0].message.content
        return self._parse_response(response_text)
    
    def _build_prompt(self, strategy_text: str) -> str:
        """Build the prompt for Groq."""
        return f"""
Extract trading rules from the following strategy description and return a JSON object.

Strategy: {strategy_text}

Return ONLY a valid JSON object with this exact structure (no markdown, no extra text):
{{
    "buy_condition": "condition description",
    "sell_condition": "condition description",
    "indicators_required": ["list", "of", "indicators"],
    "parameters": {{
        "rsi_period": 14,
        "ma_short": 50,
        "ma_long": 200,
        "other_params": "as needed"
    }}
}}

Supported indicators: RSI, SMA, EMA, MACD, Bollinger Bands, ATR, Stochastic, ADX, HIGH, LOW, VOLUME
Supported operators: <, >, <=, >=, ==, !=, and, or, not

Examples:
- "RSI < 30" for oversold
- "RSI > 70" for overbought
- "SMA(50) > SMA(200)" for moving average crossover
- "MACD > Signal" for MACD crossover
- "Price > Bollinger Upper Band" for breakout
- "Price breaks above 20 day high with high volume" for breakout with volume confirmation
- "Price drops below 20 day moving average" for support break

Be precise and use standard indicator notation. Return only the JSON object.
"""
    
    def _parse_response(self, response_text: str) -> StrategyRules:
        """Parse JSON response from Groq."""
        try:
            # Extract JSON from response (in case there's extra text)
            json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
            if not json_match:
                raise ValueError("No JSON found in response")
            
            json_str = json_match.group(0)
            data = json.loads(json_str)
            
            return StrategyRules(
                buy_condition=data.get('buy_condition', ''),
                sell_condition=data.get('sell_condition', ''),
                indicators_required=data.get('indicators_required', []),
                parameters=data.get('parameters', {})
            )
        except json.JSONDecodeError as e:
            raise ValueError(f"Failed to parse LLM response as JSON: {e}")


class StrategyParser:
    """
    Parse natural language trading strategies into structured rules.
    
    Uses Groq API for NLP processing (primary provider).
    """
    
    def __init__(self, provider: str = 'groq', api_key: Optional[str] = None):
        """
        Initialize strategy parser.
        
        Args:
            provider: 'groq' (default and only supported provider)
            api_key: API key for the provider
        """
        if provider.lower() == 'groq':
            self.provider = GroqProvider(api_key)
        else:
            raise ValueError(f"Unknown provider: {provider}. Only 'groq' is supported")
    
    def parse(self, strategy_text: str) -> StrategyRules:
        """
        Parse natural language strategy into structured rules.
        
        Args:
            strategy_text: Natural language strategy description
            
        Returns:
            StrategyRules object
        """
        return self.provider.parse_strategy(strategy_text)
    
    def parse_to_json(self, strategy_text: str) -> str:
        """
        Parse strategy and return as JSON string.
        
        Args:
            strategy_text: Natural language strategy description
            
        Returns:
            JSON string with strategy rules
        """
        rules = self.parse(strategy_text)
        return rules.to_json()
    
    def parse_to_dict(self, strategy_text: str) -> Dict[str, Any]:
        """
        Parse strategy and return as dictionary.
        
        Args:
            strategy_text: Natural language strategy description
            
        Returns:
            Dictionary with strategy rules
        """
        rules = self.parse(strategy_text)
        return rules.to_dict()


class DSLConverter:
    """Convert natural language strategies to DSL format."""
    
    # Forbidden keywords that should never appear in strategies
    # NOTE: Removed trading terms like 'drop', 'delete', 'high', 'volume' - these are legitimate
    FORBIDDEN_KEYWORDS = {
        'import', 'from', 'exec', 'eval', '__import__',
        'os', 'sys', 'subprocess', 'socket', 'requests',
        'urllib', 'http', 'ftp', 'ssh', 'password', 'secret', 'token', 'key',
        'credential', 'database', 'db', 'sql', 'query', 'table', 'column',
        'file', 'directory', 'path', 'system', 'command', 'shell', 'bash',
        'python', 'code', 'script', 'function', 'class', 'lambda', 'def'
    }
    
    @staticmethod
    def to_dsl(strategy_text: str) -> str:
        """
        Convert natural language strategy to DSL format.
        
        Args:
            strategy_text: Natural language strategy
            
        Returns:
            DSL formatted strategy
            
        Raises:
            ValueError: If forbidden keywords are detected
        """
        # Security check: detect forbidden keywords
        text_lower = strategy_text.lower()
        for keyword in DSLConverter.FORBIDDEN_KEYWORDS:
            if keyword in text_lower:
                raise ValueError(f"Security violation: Forbidden keyword '{keyword}' detected in strategy")
        
        # Extract buy and sell conditions
        buy_match = re.search(r'buy\s+(?:when|if)?\s*(.+?)(?=sell|$)', strategy_text, re.IGNORECASE)
        sell_match = re.search(r'sell\s+(?:when|if)?\s*(.+?)(?=buy|$)', strategy_text, re.IGNORECASE)
        
        buy_condition = buy_match.group(1).strip() if buy_match else ""
        sell_condition = sell_match.group(1).strip() if sell_match else ""
        
        # Normalize conditions
        buy_condition = DSLConverter._normalize_condition(buy_condition)
        sell_condition = DSLConverter._normalize_condition(sell_condition)
        
        # Build DSL
        dsl = "strategy {\n"
        if buy_condition:
            dsl += f"  buy: {buy_condition}\n"
        if sell_condition:
            dsl += f"  sell: {sell_condition}\n"
        dsl += "}"
        
        return dsl
    
    @staticmethod
    def _normalize_condition(condition: str) -> str:
        """Normalize condition text to DSL format."""
        # Replace common patterns
        condition = re.sub(r'\bcrosses?\s+below\b', '<', condition, flags=re.IGNORECASE)
        condition = re.sub(r'\bcrosses?\s+above\b', '>', condition, flags=re.IGNORECASE)
        condition = re.sub(r'\bbelow\b', '<', condition, flags=re.IGNORECASE)
        condition = re.sub(r'\babove\b', '>', condition, flags=re.IGNORECASE)
        condition = re.sub(r'\boversold\b', '< 30', condition, flags=re.IGNORECASE)
        condition = re.sub(r'\boverbought\b', '> 70', condition, flags=re.IGNORECASE)
        
        # Handle "20 day high" -> "HIGH(20)"
        condition = re.sub(r'(\d+)\s*day\s+high', r'HIGH(\1)', condition, flags=re.IGNORECASE)
        # Handle "20 day low" -> "LOW(20)"
        condition = re.sub(r'(\d+)\s*day\s+low', r'LOW(\1)', condition, flags=re.IGNORECASE)
        # Handle "20 day moving average" -> "SMA(20)"
        condition = re.sub(r'(\d+)\s*day\s+(?:moving\s+)?average', r'SMA(\1)', condition, flags=re.IGNORECASE)
        # Handle "20 day EMA" -> "EMA(20)"
        condition = re.sub(r'(\d+)\s*day\s+EMA', r'EMA(\1)', condition, flags=re.IGNORECASE)
        # Handle "20 day SMA" -> "SMA(20)"
        condition = re.sub(r'(\d+)\s*day\s+SMA', r'SMA(\1)', condition, flags=re.IGNORECASE)
        
        # Handle volume conditions - PRESERVE them instead of removing
        # "with high volume" -> "AND VOLUME"
        condition = re.sub(r'\s+with\s+high\s+volume', ' AND VOLUME', condition, flags=re.IGNORECASE)
        # "and high volume" -> "AND VOLUME"
        condition = re.sub(r'\s+and\s+high\s+volume', ' AND VOLUME', condition, flags=re.IGNORECASE)
        # "with low volume" -> "AND NOT VOLUME"
        condition = re.sub(r'\s+with\s+low\s+volume', ' AND NOT VOLUME', condition, flags=re.IGNORECASE)
        # "and low volume" -> "AND NOT VOLUME"
        condition = re.sub(r'\s+and\s+low\s+volume', ' AND NOT VOLUME', condition, flags=re.IGNORECASE)
        # "with increasing volume" -> "AND VOLUME"
        condition = re.sub(r'\s+with\s+increasing\s+volume', ' AND VOLUME', condition, flags=re.IGNORECASE)
        # "with decreasing volume" -> "AND NOT VOLUME"
        condition = re.sub(r'\s+with\s+decreasing\s+volume', ' AND NOT VOLUME', condition, flags=re.IGNORECASE)
        
        # Replace logical operators
        condition = re.sub(r'\band\b', 'AND', condition, flags=re.IGNORECASE)
        condition = re.sub(r'\bor\b', 'OR', condition, flags=re.IGNORECASE)
        condition = re.sub(r'\bnot\b', 'NOT', condition, flags=re.IGNORECASE)
        condition = re.sub(r'\bprice\b', 'PRICE', condition, flags=re.IGNORECASE)
        condition = re.sub(r'\bclose\b', 'CLOSE', condition, flags=re.IGNORECASE)
        
        return condition.strip()


class SimpleStrategyParser:
    """
    Simple regex-based strategy parser (no LLM required).
    
    Handles common patterns without external API calls.
    """
    
    PATTERNS = {
        'rsi_oversold': r'RSI\s*<\s*(\d+)',
        'rsi_overbought': r'RSI\s*>\s*(\d+)',
        'sma_crossover': r'SMA\s*\(\s*(\d+)\s*\)\s*>\s*SMA\s*\(\s*(\d+)\s*\)',
        'price_above_sma': r'(?:price|close)\s*>\s*SMA\s*\(\s*(\d+)\s*\)',
        'macd_crossover': r'MACD\s*>\s*Signal',
        'ema_crossover': r'EMA\s*\(\s*(\d+)\s*\)\s*>\s*EMA\s*\(\s*(\d+)\s*\)',
    }
    
    @staticmethod
    def parse(strategy_text: str) -> StrategyRules:
        """
        Parse strategy using regex patterns.
        
        Args:
            strategy_text: Strategy description
            
        Returns:
            StrategyRules object
        """
        text_lower = strategy_text.lower()
        
        # Extract buy and sell conditions
        buy_match = re.search(r'buy\s+(?:when|if)?\s*(.+?)(?=sell|$)', text_lower, re.IGNORECASE)
        sell_match = re.search(r'sell\s+(?:when|if)?\s*(.+?)(?=buy|$)', text_lower, re.IGNORECASE)
        
        buy_condition = buy_match.group(1).strip() if buy_match else ''
        sell_condition = sell_match.group(1).strip() if sell_match else ''
        
        # Extract indicators
        indicators = SimpleStrategyParser._extract_indicators(strategy_text)
        
        # Extract parameters
        parameters = SimpleStrategyParser._extract_parameters(strategy_text)
        
        return StrategyRules(
            buy_condition=buy_condition,
            sell_condition=sell_condition,
            indicators_required=indicators,
            parameters=parameters
        )
    
    @staticmethod
    def _extract_indicators(text: str) -> list:
        """Extract indicator names from strategy text."""
        indicators = set()
        text_upper = text.upper()
        
        if 'RSI' in text_upper:
            indicators.add('RSI')
        if 'SMA' in text_upper or 'SIMPLE MOVING AVERAGE' in text_upper:
            indicators.add('SMA')
        if 'EMA' in text_upper or 'EXPONENTIAL MOVING AVERAGE' in text_upper:
            indicators.add('EMA')
        if 'MACD' in text_upper:
            indicators.add('MACD')
        if 'BOLLINGER' in text_upper:
            indicators.add('Bollinger Bands')
        if 'ATR' in text_upper or 'AVERAGE TRUE RANGE' in text_upper:
            indicators.add('ATR')
        if 'STOCHASTIC' in text_upper:
            indicators.add('Stochastic')
        if 'ADX' in text_upper or 'AVERAGE DIRECTIONAL' in text_upper:
            indicators.add('ADX')
        
        return sorted(list(indicators))
    
    @staticmethod
    def _extract_parameters(text: str) -> Dict[str, Any]:
        """Extract parameters from strategy text."""
        parameters = {}
        
        # RSI period
        rsi_match = re.search(r'RSI\s*\(\s*(\d+)\s*\)', text, re.IGNORECASE)
        if rsi_match:
            parameters['rsi_period'] = int(rsi_match.group(1))
        else:
            parameters['rsi_period'] = 14
        
        # SMA periods
        sma_matches = re.findall(r'SMA\s*\(\s*(\d+)\s*\)', text, re.IGNORECASE)
        if sma_matches:
            sma_periods = sorted([int(m) for m in sma_matches])
            if len(sma_periods) >= 2:
                parameters['ma_short'] = sma_periods[0]
                parameters['ma_long'] = sma_periods[1]
            elif len(sma_periods) == 1:
                parameters['ma_period'] = sma_periods[0]
        
        # EMA periods
        ema_matches = re.findall(r'EMA\s*\(\s*(\d+)\s*\)', text, re.IGNORECASE)
        if ema_matches:
            ema_periods = sorted([int(m) for m in ema_matches])
            if len(ema_periods) >= 2:
                parameters['ema_short'] = ema_periods[0]
                parameters['ema_long'] = ema_periods[1]
        
        return parameters
