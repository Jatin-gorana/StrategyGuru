"""
DSL Lexer - Tokenizes DSL strategy strings into tokens.

Supported syntax:
  strategy {
    buy: RSI(14) < 30 AND PRICE > SMA(200)
    sell: RSI(14) > 70
  }
"""

import re
from enum import Enum
from dataclasses import dataclass
from typing import List, Optional


class TokenType(Enum):
    """Token types for DSL."""
    # Keywords
    STRATEGY = "STRATEGY"
    BUY = "BUY"
    SELL = "SELL"
    
    # Indicators
    INDICATOR = "INDICATOR"  # RSI, SMA, EMA, MACD, etc.
    
    # Literals
    NUMBER = "NUMBER"
    IDENTIFIER = "IDENTIFIER"
    
    # Operators
    LT = "LT"          # <
    GT = "GT"          # >
    LTE = "LTE"        # <=
    GTE = "GTE"        # >=
    EQ = "EQ"          # ==
    NEQ = "NEQ"        # !=
    
    # Logical
    AND = "AND"
    OR = "OR"
    NOT = "NOT"
    
    # Delimiters
    LPAREN = "LPAREN"      # (
    RPAREN = "RPAREN"      # )
    LBRACE = "LBRACE"      # {
    RBRACE = "RBRACE"      # }
    COLON = "COLON"        # :
    COMMA = "COMMA"        # ,
    
    # Special
    EOF = "EOF"
    WHITESPACE = "WHITESPACE"


@dataclass
class Token:
    """Represents a single token."""
    type: TokenType
    value: str
    line: int = 1
    column: int = 1


class DSLLexer:
    """Tokenizes DSL strategy strings."""
    
    # Supported indicators
    INDICATORS = {
        'RSI', 'SMA', 'EMA', 'MACD', 'PRICE', 'CLOSE',
        'BOLLINGER', 'ATR', 'STOCHASTIC', 'ADX'
    }
    
    # Keywords
    KEYWORDS = {
        'strategy': TokenType.STRATEGY,
        'buy': TokenType.BUY,
        'sell': TokenType.SELL,
        'AND': TokenType.AND,
        'OR': TokenType.OR,
        'NOT': TokenType.NOT,
    }
    
    def __init__(self, text: str):
        """Initialize lexer with input text."""
        self.text = text
        self.pos = 0
        self.line = 1
        self.column = 1
        self.tokens: List[Token] = []
    
    def tokenize(self) -> List[Token]:
        """Tokenize the input text."""
        while self.pos < len(self.text):
            self._skip_whitespace()
            
            if self.pos >= len(self.text):
                break
            
            char = self.text[self.pos]
            
            # Single character tokens
            if char == '(':
                self._add_token(TokenType.LPAREN, '(')
                self.pos += 1
            elif char == ')':
                self._add_token(TokenType.RPAREN, ')')
                self.pos += 1
            elif char == '{':
                self._add_token(TokenType.LBRACE, '{')
                self.pos += 1
            elif char == '}':
                self._add_token(TokenType.RBRACE, '}')
                self.pos += 1
            elif char == ':':
                self._add_token(TokenType.COLON, ':')
                self.pos += 1
            elif char == ',':
                self._add_token(TokenType.COMMA, ',')
                self.pos += 1
            
            # Operators
            elif char == '<':
                if self._peek() == '=':
                    self._add_token(TokenType.LTE, '<=')
                    self.pos += 2
                else:
                    self._add_token(TokenType.LT, '<')
                    self.pos += 1
            elif char == '>':
                if self._peek() == '=':
                    self._add_token(TokenType.GTE, '>=')
                    self.pos += 2
                else:
                    self._add_token(TokenType.GT, '>')
                    self.pos += 1
            elif char == '=':
                if self._peek() == '=':
                    self._add_token(TokenType.EQ, '==')
                    self.pos += 2
                else:
                    self.pos += 1  # Skip single =
            elif char == '!':
                if self._peek() == '=':
                    self._add_token(TokenType.NEQ, '!=')
                    self.pos += 2
                else:
                    self.pos += 1
            
            # Numbers
            elif char.isdigit():
                self._tokenize_number()
            
            # Identifiers and keywords
            elif char.isalpha() or char == '_':
                self._tokenize_identifier()
            
            else:
                self.pos += 1
        
        self._add_token(TokenType.EOF, '')
        return self.tokens
    
    def _skip_whitespace(self):
        """Skip whitespace characters."""
        while self.pos < len(self.text) and self.text[self.pos].isspace():
            if self.text[self.pos] == '\n':
                self.line += 1
                self.column = 1
            else:
                self.column += 1
            self.pos += 1
    
    def _peek(self, offset: int = 1) -> Optional[str]:
        """Peek at character ahead."""
        pos = self.pos + offset
        if pos < len(self.text):
            return self.text[pos]
        return None
    
    def _tokenize_number(self):
        """Tokenize a number."""
        start = self.pos
        while self.pos < len(self.text) and self.text[self.pos].isdigit():
            self.pos += 1
        
        value = self.text[start:self.pos]
        self._add_token(TokenType.NUMBER, value)
    
    def _tokenize_identifier(self):
        """Tokenize an identifier or keyword."""
        start = self.pos
        while self.pos < len(self.text) and (self.text[self.pos].isalnum() or self.text[self.pos] == '_'):
            self.pos += 1
        
        value = self.text[start:self.pos]
        value_upper = value.upper()
        
        # Check if it's a keyword
        if value_upper in self.KEYWORDS:
            self._add_token(self.KEYWORDS[value_upper], value)
        # Check if it's an indicator
        elif value_upper in self.INDICATORS:
            self._add_token(TokenType.INDICATOR, value_upper)
        else:
            self._add_token(TokenType.IDENTIFIER, value)
    
    def _add_token(self, token_type: TokenType, value: str):
        """Add a token to the list."""
        token = Token(token_type, value, self.line, self.column)
        self.tokens.append(token)
        self.column += len(value)
