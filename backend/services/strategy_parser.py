import json
import re
import os
from typing import Dict, Any, Optional, Tuple
from abc import ABC, abstractmethod
from dataclasses import dataclass, asdict
import pandas as pd


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


class StrategyParser:
    """
    Parse natural language trading strategies into structured rules.
    
    Supports both OpenAI and Google Gemini APIs for NLP processing.
    """
    
    def __init__(self, provider: str = 'openai', api_key: Optional[str] = None):
        """
        Initialize strategy parser.
        
        Args:
            provider: 'openai' or 'gemini'
            api_key: API key for the provider
        """
        if provider.lower() == 'openai':
            self.provider = OpenAIProvider(api_key)
        elif provider.lower() == 'gemini':
            self.provider = GeminiProvider(api_key)
        else:
            raise ValueError(f"Unknown provider: {provider}. Use 'openai' or 'gemini'")
    
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
