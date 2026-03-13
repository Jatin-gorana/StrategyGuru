"""
Example usage of the strategy_parser module.

This script demonstrates how to parse natural language trading strategies
into structured JSON rules using LLM APIs or simple regex patterns.
"""

from backend.services.strategy_parser import (
    StrategyParser,
    SimpleStrategyParser,
    StrategyRules
)
import json


def example_simple_parser():
    """Example 1: Simple regex-based parser (no API required)."""
    print("=" * 70)
    print("Example 1: Simple Regex-Based Parser")
    print("=" * 70)
    
    strategies = [
        "Buy when RSI < 30 and sell when RSI > 70",
        "Buy when SMA(50) > SMA(200) and sell when SMA(50) < SMA(200)",
        "Buy when MACD > Signal and sell when MACD < Signal",
        "Buy when price > SMA(200) and sell when price < SMA(200)",
    ]
    
    for strategy_text in strategies:
        print(f"\nStrategy: {strategy_text}")
        
        try:
            rules = SimpleStrategyParser.parse(strategy_text)
            
            print(f"  Buy Condition: {rules.buy_condition}")
            print(f"  Sell Condition: {rules.sell_condition}")
            print(f"  Indicators: {', '.join(rules.indicators_required)}")
            print(f"  Parameters: {rules.parameters}")
            
        except Exception as e:
            print(f"  Error: {e}")


def example_openai_parser():
    """Example 2: OpenAI API parser."""
    print("\n" + "=" * 70)
    print("Example 2: OpenAI API Parser")
    print("=" * 70)
    
    strategies = [
        "Buy when RSI is below 30 indicating oversold conditions, and sell when RSI exceeds 70 indicating overbought",
        "Buy when the 50-day moving average crosses above the 200-day moving average, sell on the opposite crossover",
        "Buy when MACD line crosses above the signal line, sell when it crosses below",
    ]
    
    try:
        parser = StrategyParser(provider='openai')
        
        for strategy_text in strategies:
            print(f"\nStrategy: {strategy_text}")
            
            try:
                rules = parser.parse(strategy_text)
                
                print(f"  Buy Condition: {rules.buy_condition}")
                print(f"  Sell Condition: {rules.sell_condition}")
                print(f"  Indicators: {', '.join(rules.indicators_required)}")
                print(f"  Parameters: {json.dumps(rules.parameters, indent=4)}")
                
            except Exception as e:
                print(f"  Error: {e}")
    
    except ValueError as e:
        print(f"Skipping OpenAI example: {e}")
        print("Set OPENAI_API_KEY environment variable to use OpenAI API")


def example_gemini_parser():
    """Example 3: Google Gemini API parser."""
    print("\n" + "=" * 70)
    print("Example 3: Google Gemini API Parser")
    print("=" * 70)
    
    strategies = [
        "Buy when RSI drops below 30 and sell when it rises above 70",
        "Buy on golden cross (50 MA > 200 MA) and sell on death cross",
        "Buy when MACD histogram turns positive and sell when it turns negative",
    ]
    
    try:
        parser = StrategyParser(provider='gemini')
        
        for strategy_text in strategies:
            print(f"\nStrategy: {strategy_text}")
            
            try:
                rules = parser.parse(strategy_text)
                
                print(f"  Buy Condition: {rules.buy_condition}")
                print(f"  Sell Condition: {rules.sell_condition}")
                print(f"  Indicators: {', '.join(rules.indicators_required)}")
                print(f"  Parameters: {json.dumps(rules.parameters, indent=4)}")
                
            except Exception as e:
                print(f"  Error: {e}")
    
    except ValueError as e:
        print(f"Skipping Gemini example: {e}")
        print("Set GOOGLE_API_KEY environment variable to use Gemini API")


def example_json_output():
    """Example 4: JSON output format."""
    print("\n" + "=" * 70)
    print("Example 4: JSON Output Format")
    print("=" * 70)
    
    strategy_text = "Buy when RSI < 30 and sell when RSI > 70"
    
    print(f"\nStrategy: {strategy_text}")
    
    try:
        rules = SimpleStrategyParser.parse(strategy_text)
        
        print("\nJSON Output:")
        print(rules.to_json())
        
        print("\nDictionary Output:")
        print(json.dumps(rules.to_dict(), indent=2))
        
    except Exception as e:
        print(f"Error: {e}")


def example_complex_strategies():
    """Example 5: Complex multi-indicator strategies."""
    print("\n" + "=" * 70)
    print("Example 5: Complex Multi-Indicator Strategies")
    print("=" * 70)
    
    complex_strategies = [
        "Buy when RSI < 30 and SMA(50) > SMA(200) and sell when RSI > 70 or SMA(50) < SMA(200)",
        "Buy when MACD > Signal and price > SMA(200) and sell when MACD < Signal",
        "Buy when EMA(12) > EMA(26) and RSI < 70 and sell when EMA(12) < EMA(26) or RSI > 80",
    ]
    
    for strategy_text in complex_strategies:
        print(f"\nStrategy: {strategy_text}")
        
        try:
            rules = SimpleStrategyParser.parse(strategy_text)
            
            print(f"  Buy: {rules.buy_condition}")
            print(f"  Sell: {rules.sell_condition}")
            print(f"  Indicators: {', '.join(rules.indicators_required)}")
            print(f"  Parameters: {rules.parameters}")
            
        except Exception as e:
            print(f"  Error: {e}")


def example_strategy_rules_object():
    """Example 6: Working with StrategyRules objects."""
    print("\n" + "=" * 70)
    print("Example 6: StrategyRules Object")
    print("=" * 70)
    
    # Create a StrategyRules object manually
    rules = StrategyRules(
        buy_condition="RSI < 30 and SMA(50) > SMA(200)",
        sell_condition="RSI > 70 or SMA(50) < SMA(200)",
        indicators_required=["RSI", "SMA"],
        parameters={
            "rsi_period": 14,
            "ma_short": 50,
            "ma_long": 200
        }
    )
    
    print("\nStrategyRules Object:")
    print(f"  Buy: {rules.buy_condition}")
    print(f"  Sell: {rules.sell_condition}")
    print(f"  Indicators: {rules.indicators_required}")
    print(f"  Parameters: {rules.parameters}")
    
    print("\nAs Dictionary:")
    print(json.dumps(rules.to_dict(), indent=2))
    
    print("\nAs JSON:")
    print(rules.to_json())


def example_batch_parsing():
    """Example 7: Batch parsing multiple strategies."""
    print("\n" + "=" * 70)
    print("Example 7: Batch Parsing Multiple Strategies")
    print("=" * 70)
    
    strategies = {
        "RSI Oversold": "Buy when RSI < 30 and sell when RSI > 70",
        "Golden Cross": "Buy when SMA(50) > SMA(200) and sell when SMA(50) < SMA(200)",
        "MACD Crossover": "Buy when MACD > Signal and sell when MACD < Signal",
        "EMA Trend": "Buy when EMA(12) > EMA(26) and sell when EMA(12) < EMA(26)",
    }
    
    print("\nParsing strategies:")
    results = {}
    
    for name, strategy_text in strategies.items():
        try:
            rules = SimpleStrategyParser.parse(strategy_text)
            results[name] = rules.to_dict()
            print(f"  ✓ {name}")
        except Exception as e:
            print(f"  ✗ {name}: {e}")
    
    print("\nResults Summary:")
    print(json.dumps(results, indent=2, default=str))


def example_parameter_extraction():
    """Example 8: Parameter extraction from strategies."""
    print("\n" + "=" * 70)
    print("Example 8: Parameter Extraction")
    print("=" * 70)
    
    strategies = [
        "Buy when RSI(14) < 30 and sell when RSI(14) > 70",
        "Buy when SMA(20) > SMA(50) and sell when SMA(20) < SMA(50)",
        "Buy when EMA(12) > EMA(26) and sell when EMA(12) < EMA(26)",
        "Buy when RSI(21) < 25 and SMA(100) > SMA(300)",
    ]
    
    for strategy_text in strategies:
        print(f"\nStrategy: {strategy_text}")
        
        try:
            rules = SimpleStrategyParser.parse(strategy_text)
            
            print(f"  Extracted Parameters:")
            for param, value in rules.parameters.items():
                print(f"    {param}: {value}")
            
        except Exception as e:
            print(f"  Error: {e}")


def example_indicator_detection():
    """Example 9: Automatic indicator detection."""
    print("\n" + "=" * 70)
    print("Example 9: Automatic Indicator Detection")
    print("=" * 70)
    
    strategies = [
        "Buy when RSI is low and sell when it's high",
        "Use moving averages for trend following",
        "MACD crossovers signal momentum changes",
        "Bollinger Bands show volatility extremes",
        "ATR helps with position sizing",
        "Stochastic oscillator for overbought/oversold",
        "ADX measures trend strength",
    ]
    
    for strategy_text in strategies:
        print(f"\nStrategy: {strategy_text}")
        
        try:
            rules = SimpleStrategyParser.parse(strategy_text)
            
            if rules.indicators_required:
                print(f"  Detected Indicators: {', '.join(rules.indicators_required)}")
            else:
                print(f"  No indicators detected")
            
        except Exception as e:
            print(f"  Error: {e}")


def example_error_handling():
    """Example 10: Error handling."""
    print("\n" + "=" * 70)
    print("Example 10: Error Handling")
    print("=" * 70)
    
    invalid_strategies = [
        "",  # Empty strategy
        "Some random text",  # No buy/sell conditions
        "Buy when unknown_indicator > 50",  # Unknown indicator
    ]
    
    for strategy_text in invalid_strategies:
        print(f"\nStrategy: '{strategy_text}'")
        
        try:
            rules = SimpleStrategyParser.parse(strategy_text)
            
            if not rules.buy_condition and not rules.sell_condition:
                print(f"  Warning: No buy/sell conditions found")
            else:
                print(f"  Buy: {rules.buy_condition}")
                print(f"  Sell: {rules.sell_condition}")
            
        except Exception as e:
            print(f"  Error: {e}")


if __name__ == "__main__":
    print("\n" + "=" * 70)
    print("STRATEGY PARSER - USAGE EXAMPLES")
    print("=" * 70)
    
    # Run all examples
    example_simple_parser()
    example_json_output()
    example_complex_strategies()
    example_strategy_rules_object()
    example_batch_parsing()
    example_parameter_extraction()
    example_indicator_detection()
    example_error_handling()
    
    # Optional: Run LLM examples if API keys are available
    print("\n" + "=" * 70)
    print("Optional LLM Examples (requires API keys)")
    print("=" * 70)
    example_openai_parser()
    example_gemini_parser()
    
    print("\n" + "=" * 70)
    print("Examples completed!")
    print("=" * 70)
