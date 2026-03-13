# Strategy Parser Setup Guide

The `strategy_parser.py` module converts natural language trading strategies into structured JSON rules using LLM APIs or simple regex patterns.

## Features

- **Multiple Providers**: OpenAI GPT-3.5 or Google Gemini
- **Simple Parser**: Regex-based parser (no API required)
- **Structured Output**: JSON format with buy/sell conditions, indicators, and parameters
- **Flexible Input**: Natural language strategy descriptions
- **Error Handling**: Graceful fallback and validation

## Installation

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Set Up API Keys (Optional)

#### For OpenAI API:

```bash
# Set environment variable
export OPENAI_API_KEY="your-openai-api-key"

# Or on Windows:
set OPENAI_API_KEY=your-openai-api-key
```

Get your API key from: https://platform.openai.com/api-keys

#### For Google Gemini API:

```bash
# Set environment variable
export GOOGLE_API_KEY="your-google-api-key"

# Or on Windows:
set GOOGLE_API_KEY=your-google-api-key
```

Get your API key from: https://makersuite.google.com/app/apikey

## Usage

### 1. Simple Regex-Based Parser (No API Required)

```python
from backend.services.strategy_parser import SimpleStrategyParser

strategy_text = "Buy when RSI < 30 and sell when RSI > 70"
rules = SimpleStrategyParser.parse(strategy_text)

print(rules.buy_condition)      # "rsi < 30"
print(rules.sell_condition)     # "rsi > 70"
print(rules.indicators_required) # ["RSI"]
print(rules.parameters)         # {"rsi_period": 14}
```

### 2. OpenAI API Parser

```python
from backend.services.strategy_parser import StrategyParser

parser = StrategyParser(provider='openai')
rules = parser.parse("Buy when RSI is below 30 and sell when it exceeds 70")

print(rules.to_json())  # Pretty JSON output
```

### 3. Google Gemini API Parser

```python
from backend.services.strategy_parser import StrategyParser

parser = StrategyParser(provider='gemini')
rules = parser.parse("Buy on golden cross and sell on death cross")

print(rules.to_dict())  # Dictionary output
```

## Supported Indicators

- **RSI**: Relative Strength Index
- **SMA**: Simple Moving Average
- **EMA**: Exponential Moving Average
- **MACD**: Moving Average Convergence Divergence
- **Bollinger Bands**: Volatility bands
- **ATR**: Average True Range
- **Stochastic**: Stochastic Oscillator
- **ADX**: Average Directional Index

## Supported Operators

- `<`, `>`, `<=`, `>=`, `==`, `!=`
- `and`, `or`, `not`

## Example Strategies

### RSI Strategy
```
"Buy when RSI < 30 and sell when RSI > 70"
```

Output:
```json
{
  "buy_condition": "rsi < 30",
  "sell_condition": "rsi > 70",
  "indicators_required": ["RSI"],
  "parameters": {
    "rsi_period": 14
  }
}
```

### Moving Average Crossover
```
"Buy when SMA(50) > SMA(200) and sell when SMA(50) < SMA(200)"
```

Output:
```json
{
  "buy_condition": "sma(50) > sma(200)",
  "sell_condition": "sma(50) < sma(200)",
  "indicators_required": ["SMA"],
  "parameters": {
    "ma_short": 50,
    "ma_long": 200
  }
}
```

### MACD Strategy
```
"Buy when MACD > Signal and sell when MACD < Signal"
```

Output:
```json
{
  "buy_condition": "macd > signal",
  "sell_condition": "macd < signal",
  "indicators_required": ["MACD"],
  "parameters": {}
}
```

### Combined Strategy
```
"Buy when RSI < 30 and SMA(50) > SMA(200) and sell when RSI > 70 or SMA(50) < SMA(200)"
```

Output:
```json
{
  "buy_condition": "rsi < 30 and sma(50) > sma(200)",
  "sell_condition": "rsi > 70 or sma(50) < sma(200)",
  "indicators_required": ["RSI", "SMA"],
  "parameters": {
    "rsi_period": 14,
    "ma_short": 50,
    "ma_long": 200
  }
}
```

## API Response Format

All parsers return a `StrategyRules` object with:

```python
@dataclass
class StrategyRules:
    buy_condition: str              # Buy signal condition
    sell_condition: str             # Sell signal condition
    indicators_required: list       # List of required indicators
    parameters: Dict[str, Any]      # Indicator parameters
```

## Methods

### Parse to Dictionary
```python
rules_dict = parser.parse_to_dict(strategy_text)
```

### Parse to JSON
```python
rules_json = parser.parse_to_json(strategy_text)
```

### Parse to Object
```python
rules = parser.parse(strategy_text)
```

## Error Handling

```python
try:
    parser = StrategyParser(provider='openai')
    rules = parser.parse(strategy_text)
except ValueError as e:
    print(f"API key not found: {e}")
except Exception as e:
    print(f"Parsing error: {e}")
```

## Running Examples

```bash
python example_strategy_parser.py
```

This will run 10 examples demonstrating:
1. Simple regex-based parsing
2. OpenAI API parsing
3. Google Gemini API parsing
4. JSON output format
5. Complex multi-indicator strategies
6. StrategyRules objects
7. Batch parsing
8. Parameter extraction
9. Indicator detection
10. Error handling

## Performance Notes

- **Simple Parser**: Instant (no API calls)
- **OpenAI API**: ~1-2 seconds per request
- **Gemini API**: ~1-2 seconds per request

## Cost Considerations

- **OpenAI**: ~$0.0005 per request (GPT-3.5-turbo)
- **Gemini**: Free tier available with rate limits

## Troubleshooting

### "OPENAI_API_KEY not provided"
```bash
export OPENAI_API_KEY="your-key"
```

### "GOOGLE_API_KEY not provided"
```bash
export GOOGLE_API_KEY="your-key"
```

### "openai package not installed"
```bash
pip install openai
```

### "google-generativeai package not installed"
```bash
pip install google-generativeai
```

## Integration with Backtest Engine

```python
from backend.services.strategy_parser import StrategyParser
from backend.services.data_fetcher import get_stock_data
from backend.services.indicators import add_all_indicators
from backend.services.backtest_engine import BacktestEngine

# Parse strategy
parser = StrategyParser(provider='openai')
rules = parser.parse("Buy when RSI < 30 and sell when RSI > 70")

# Fetch data
df = get_stock_data('AAPL', '2023-01-01', '2024-01-01')

# Add indicators
df = add_all_indicators(df)

# Create conditions from parsed rules
buy_condition = eval(f"df['RSI'] < 30")
sell_condition = eval(f"df['RSI'] > 70")

# Run backtest
engine = BacktestEngine(df, initial_capital=10000)
trades, equity_curve, metrics = engine.run_backtest(buy_condition, sell_condition)
```

## Best Practices

1. **Use Simple Parser First**: For common patterns, use `SimpleStrategyParser` to avoid API costs
2. **Validate Output**: Always check the parsed rules make sense
3. **Test Strategies**: Backtest parsed strategies before trading
4. **Cache Results**: Store parsed strategies to avoid repeated API calls
5. **Error Handling**: Implement proper error handling for API failures

## Advanced Usage

### Custom Provider

Extend `LLMProvider` to add custom LLM providers:

```python
from backend.services.strategy_parser import LLMProvider, StrategyRules

class CustomProvider(LLMProvider):
    def parse_strategy(self, strategy_text: str) -> StrategyRules:
        # Your implementation
        pass
```

### Batch Processing

```python
strategies = [
    "Buy when RSI < 30 and sell when RSI > 70",
    "Buy when SMA(50) > SMA(200) and sell when SMA(50) < SMA(200)",
]

parser = StrategyParser(provider='openai')
results = [parser.parse(s) for s in strategies]
```

## Support

For issues or questions:
1. Check the examples in `example_strategy_parser.py`
2. Review the docstrings in `strategy_parser.py`
3. Verify API keys are set correctly
4. Check API rate limits and quotas
