import json
import os
from typing import Dict, Any, Optional
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)


@dataclass
class StrategyImprovement:
    """Strategy improvement suggestion from LLM."""
    original_strategy: str
    improved_strategy: str
    improvements: list
    reasoning: str
    risk_level: str


class StrategyImprover:
    """Improve trading strategies using LLM."""
    
    def __init__(self, provider: str = 'groq', api_key: Optional[str] = None):
        """
        Initialize strategy improver.
        
        Args:
            provider: 'groq', 'openai', or 'gemini'
            api_key: API key for the provider
        """
        self.provider = provider.lower()
        
        # Determine which API key to use
        if self.provider == 'groq':
            self.api_key = api_key or os.getenv('GROQ_API_KEY')
        elif self.provider == 'openai':
            self.api_key = api_key or os.getenv('OPENAI_API_KEY')
        elif self.provider == 'gemini':
            self.api_key = api_key or os.getenv('GOOGLE_API_KEY')
        else:
            raise ValueError(f"Unknown provider: {provider}")
        
        if not self.api_key:
            raise ValueError(f"{provider.upper()}_API_KEY not provided or set in environment")
        
        if self.provider == 'groq':
            self._init_groq()
        elif self.provider == 'openai':
            self._init_openai()
        elif self.provider == 'gemini':
            self._init_gemini()
        else:
            raise ValueError(f"Unknown provider: {provider}")
    
    def _init_groq(self):
        """Initialize Groq client."""
        try:
            from groq import Groq
            self.client = Groq(api_key=self.api_key)
        except ImportError:
            raise ImportError("groq package not installed. Install with: pip install groq")
    
    def _init_openai(self):
        """Initialize OpenAI client."""
        try:
            from openai import OpenAI
            self.client = OpenAI(api_key=self.api_key)
        except ImportError:
            raise ImportError("openai package not installed. Install with: pip install openai")
    
    def _init_gemini(self):
        """Initialize Gemini client."""
        try:
            import google.generativeai as genai
            genai.configure(api_key=self.api_key)
            self.model = genai.GenerativeModel('gemini-pro')
        except ImportError:
            raise ImportError("google-generativeai package not installed. Install with: pip install google-generativeai")
    
    def improve_strategy(
        self,
        strategy_text: str,
        metrics: Dict[str, Any],
        trades_count: int = 0
    ) -> StrategyImprovement:
        """
        Suggest improvements to a trading strategy.
        
        Args:
            strategy_text: Current strategy description
            metrics: Backtest metrics (return, sharpe, drawdown, win_rate, etc.)
            trades_count: Number of trades executed
            
        Returns:
            StrategyImprovement object with suggestions
        """
        prompt = self._build_improvement_prompt(strategy_text, metrics, trades_count)
        
        if self.provider == 'groq':
            return self._improve_with_groq(prompt, strategy_text)
        elif self.provider == 'openai':
            return self._improve_with_openai(prompt, strategy_text)
        else:
            return self._improve_with_gemini(prompt, strategy_text)
    
    def _build_improvement_prompt(
        self,
        strategy_text: str,
        metrics: Dict[str, Any],
        trades_count: int
    ) -> str:
        """Build the improvement prompt for LLM."""
        return f"""
You are an expert trading strategy analyst. Analyze the following trading strategy and its backtest results, then suggest specific improvements.

CURRENT STRATEGY:
{strategy_text}

BACKTEST RESULTS:
- Total Return: {metrics.get('total_return_percent', 0):.2f}%
- Sharpe Ratio: {metrics.get('sharpe_ratio', 0):.4f}
- Max Drawdown: {metrics.get('max_drawdown_percent', 0):.2f}%
- Win Rate: {metrics.get('win_rate', 0):.2f}%
- Profit Factor: {metrics.get('profit_factor', 0):.2f}
- Total Trades: {trades_count}
- Avg Win: ${metrics.get('avg_win', 0):.2f}
- Avg Loss: ${metrics.get('avg_loss', 0):.2f}

ANALYSIS GUIDELINES:
1. Identify weaknesses in the current strategy
2. Suggest specific improvements (e.g., add stop loss, adjust thresholds, combine indicators)
3. Explain the reasoning behind each suggestion
4. Consider risk management improvements
5. Suggest indicator combinations that might work better

PROVIDE YOUR RESPONSE IN THIS EXACT JSON FORMAT:
{{
    "improved_strategy": "The improved strategy description",
    "improvements": [
        "Specific improvement 1",
        "Specific improvement 2",
        "Specific improvement 3"
    ],
    "reasoning": "Detailed explanation of why these improvements would help",
    "risk_level": "Low/Medium/High",
    "expected_impact": "Expected improvement in performance"
}}

Focus on practical, implementable improvements that address the specific weaknesses shown in the backtest results.
"""
    
    def _improve_with_groq(self, prompt: str, strategy_text: str) -> StrategyImprovement:
        """Get improvements from Groq."""
        try:
            response = self.client.chat.completions.create(
                model="openai/gpt-oss-120b",
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert trading strategy analyst. Provide specific, actionable improvements to trading strategies based on backtest results. Always respond with valid JSON."
                    },
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=2000
            )
            
            response_text = response.choices[0].message.content
            
            # Extract JSON from response
            import re
            json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
            if not json_match:
                raise ValueError("No JSON found in response")
            
            json_str = json_match.group(0)
            data = json.loads(json_str)
            
            return StrategyImprovement(
                original_strategy=strategy_text,
                improved_strategy=data.get('improved_strategy', ''),
                improvements=data.get('improvements', []),
                reasoning=data.get('reasoning', ''),
                risk_level=data.get('risk_level', 'Medium')
            )
        except Exception as e:
            logger.error(f"Groq improvement failed: {str(e)}")
            raise
    
    def _improve_with_openai(self, prompt: str, strategy_text: str) -> StrategyImprovement:
        """Get improvements from OpenAI."""
        try:
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert trading strategy analyst. Provide specific, actionable improvements to trading strategies based on backtest results."
                    },
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                response_format={"type": "json_object"}
            )
            
            response_text = response.choices[0].message.content
            data = json.loads(response_text)
            
            return StrategyImprovement(
                original_strategy=strategy_text,
                improved_strategy=data.get('improved_strategy', ''),
                improvements=data.get('improvements', []),
                reasoning=data.get('reasoning', ''),
                risk_level=data.get('risk_level', 'Medium')
            )
        except Exception as e:
            logger.error(f"OpenAI improvement failed: {str(e)}")
            raise
    
    def _improve_with_gemini(self, prompt: str, strategy_text: str) -> StrategyImprovement:
        """Get improvements from Gemini."""
        try:
            response = self.model.generate_content(prompt)
            response_text = response.text
            
            # Extract JSON from response
            import re
            json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
            if not json_match:
                raise ValueError("No JSON found in response")
            
            json_str = json_match.group(0)
            data = json.loads(json_str)
            
            return StrategyImprovement(
                original_strategy=strategy_text,
                improved_strategy=data.get('improved_strategy', ''),
                improvements=data.get('improvements', []),
                reasoning=data.get('reasoning', ''),
                risk_level=data.get('risk_level', 'Medium')
            )
        except Exception as e:
            logger.error(f"Gemini improvement failed: {str(e)}")
            raise
