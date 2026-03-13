"""
DSL Parser - Parses tokenized DSL into Abstract Syntax Tree (AST).

Converts tokens into a structured format that can be safely evaluated.
"""

from dataclasses import dataclass
from typing import List, Dict, Any, Optional, Union
from .dsl_lexer import Token, TokenType, DSLLexer


@dataclass
class ASTNode:
    """Base class for AST nodes."""
    pass


@dataclass
class NumberNode(ASTNode):
    """Represents a number literal."""
    value: int


@dataclass
class IndicatorNode(ASTNode):
    """Represents an indicator call like RSI(14)."""
    name: str
    period: Optional[int] = None


@dataclass
class ComparisonNode(ASTNode):
    """Represents a comparison like RSI(14) < 30."""
    left: ASTNode
    operator: str
    right: ASTNode


@dataclass
class BinaryOpNode(ASTNode):
    """Represents a binary operation like AND, OR."""
    left: ASTNode
    operator: str
    right: ASTNode


@dataclass
class UnaryOpNode(ASTNode):
    """Represents a unary operation like NOT."""
    operator: str
    operand: ASTNode


@dataclass
class StrategyNode(ASTNode):
    """Represents the entire strategy."""
    buy_condition: Optional[ASTNode] = None
    sell_condition: Optional[ASTNode] = None


class DSLParser:
    """Parses DSL tokens into AST."""
    
    def __init__(self, tokens: List[Token]):
        """Initialize parser with tokens."""
        self.tokens = tokens
        self.pos = 0
    
    def parse(self) -> StrategyNode:
        """Parse tokens into AST."""
        return self._parse_strategy()
    
    def _current_token(self) -> Token:
        """Get current token."""
        if self.pos < len(self.tokens):
            return self.tokens[self.pos]
        return self.tokens[-1]  # EOF
    
    def _peek_token(self, offset: int = 1) -> Token:
        """Peek at token ahead."""
        pos = self.pos + offset
        if pos < len(self.tokens):
            return self.tokens[pos]
        return self.tokens[-1]  # EOF
    
    def _advance(self):
        """Move to next token."""
        if self.pos < len(self.tokens) - 1:
            self.pos += 1
    
    def _expect(self, token_type: TokenType) -> Token:
        """Expect a specific token type."""
        token = self._current_token()
        if token.type != token_type:
            raise SyntaxError(f"Expected {token_type}, got {token.type} at line {token.line}")
        self._advance()
        return token
    
    def _parse_strategy(self) -> StrategyNode:
        """Parse: strategy { buy: ..., sell: ... }"""
        self._expect(TokenType.STRATEGY)
        self._expect(TokenType.LBRACE)
        
        buy_condition = None
        sell_condition = None
        
        while self._current_token().type != TokenType.RBRACE:
            if self._current_token().type == TokenType.BUY:
                self._advance()
                self._expect(TokenType.COLON)
                buy_condition = self._parse_expression()
            
            elif self._current_token().type == TokenType.SELL:
                self._advance()
                self._expect(TokenType.COLON)
                sell_condition = self._parse_expression()
            
            # Skip commas
            if self._current_token().type == TokenType.COMMA:
                self._advance()
        
        self._expect(TokenType.RBRACE)
        
        return StrategyNode(buy_condition, sell_condition)
    
    def _parse_expression(self) -> ASTNode:
        """Parse logical expression (OR level)."""
        left = self._parse_and_expression()
        
        while self._current_token().type == TokenType.OR:
            op = self._current_token().value
            self._advance()
            right = self._parse_and_expression()
            left = BinaryOpNode(left, op, right)
        
        return left
    
    def _parse_and_expression(self) -> ASTNode:
        """Parse AND expression."""
        left = self._parse_not_expression()
        
        while self._current_token().type == TokenType.AND:
            op = self._current_token().value
            self._advance()
            right = self._parse_not_expression()
            left = BinaryOpNode(left, op, right)
        
        return left
    
    def _parse_not_expression(self) -> ASTNode:
        """Parse NOT expression."""
        if self._current_token().type == TokenType.NOT:
            op = self._current_token().value
            self._advance()
            operand = self._parse_not_expression()
            return UnaryOpNode(op, operand)
        
        return self._parse_comparison()
    
    def _parse_comparison(self) -> ASTNode:
        """Parse comparison expression."""
        left = self._parse_primary()
        
        if self._current_token().type in [TokenType.LT, TokenType.GT, TokenType.LTE, TokenType.GTE, TokenType.EQ, TokenType.NEQ]:
            op = self._current_token().value
            self._advance()
            right = self._parse_primary()
            return ComparisonNode(left, op, right)
        
        return left
    
    def _parse_primary(self) -> ASTNode:
        """Parse primary expression."""
        token = self._current_token()
        
        # Number
        if token.type == TokenType.NUMBER:
            self._advance()
            return NumberNode(int(token.value))
        
        # Indicator
        if token.type == TokenType.INDICATOR:
            return self._parse_indicator()
        
        # Parenthesized expression
        if token.type == TokenType.LPAREN:
            self._advance()
            expr = self._parse_expression()
            self._expect(TokenType.RPAREN)
            return expr
        
        raise SyntaxError(f"Unexpected token: {token.type} at line {token.line}")
    
    def _parse_indicator(self) -> IndicatorNode:
        """Parse indicator call like RSI(14) or PRICE."""
        name = self._current_token().value
        self._advance()
        
        period = None
        
        # Check for period parameter
        if self._current_token().type == TokenType.LPAREN:
            self._advance()
            if self._current_token().type == TokenType.NUMBER:
                period = int(self._current_token().value)
                self._advance()
            self._expect(TokenType.RPAREN)
        
        return IndicatorNode(name, period)


def parse_dsl(dsl_text: str) -> StrategyNode:
    """Parse DSL text into AST."""
    lexer = DSLLexer(dsl_text)
    tokens = lexer.tokenize()
    parser = DSLParser(tokens)
    return parser.parse()
