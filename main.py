import re
from dataclasses import dataclass
from typing import Any, Dict

from rich import print
from rich.style import Style
from rich.text import Text
from math import pi

# These keywords are for testing purposes, likely not to use them.
KEYWORDS = ['int', 'float', 'double', 'char', 'void', 'if', 'else', 'while', 'for', 'return']
BINARY_OPERATORS = ['+', '-', '*', '/', '%']

@dataclass
class Token:
    type: str
    value: str

class Tokenizer:
    def __init__(self, source: str):
        self.source = source
        self.tokens = self.tokenize()

    def tokenize(self):
        tokens = []
        pattern = r'\w+|=|;|[\+\-\*\/\%]'
        for match in re.findall(pattern, self.source):
            token_type = self.match_token_type(match)
            tokens.append(Token(token_type, match))
        return tokens

    def match_token_type(self, token):
        match token:
            case token if token in KEYWORDS:
                return 'Keyword'
            case token if token.isdigit():
                return 'Number'
            case token if token in BINARY_OPERATORS:
                return 'BinaryOperator'
            case '=':
                return 'Operator'
            case ';':
                return 'Semicolon'
            case _:
                return 'Identifier'

@dataclass
class Node:
    """Base class for AST nodes"""
    pass

@dataclass
class Expression(Node):
    """AST node for representing an expression"""
    op: str
    left: Any = None
    right: Any = None

    def evaluate(self, environment):
        if self.op in ['+', '-', '*', '/', '%']:
            left_value = self.left.evaluate(environment) if self.left else 0
            right_value = self.right.evaluate(environment) if self.right else 0

            if self.op == '+':
                return left_value + right_value
            elif self.op == '-':
                return left_value - right_value
            elif self.op == '*':
                return left_value * right_value
            elif self.op == '%':
                return left_value % right_value
            elif self.op == '/':
                if right_value == 0:
                    raise ZeroDivisionError("Division by zero")
                return left_value / right_value
        elif self.op.isdigit():
            return int(self.op)
        elif self.op in environment.variables:
            return environment.variables[self.op]
        else:
            raise ValueError(f"Invalid expression: {self.op}")

    def __rich__(self):
        node_style = Style(color="green", bold=True)
        node_text = Text(f"[{node_style}]{self.op}[/{node_style}]", justify="left")

        if self.left:
            node_text.append(self.left.__rich__())
        if self.right:
            node_text.append(self.right.__rich__())

        return node_text

class Parser:
    def __init__(self, tokens: list[Token]):
        self.tokens = tokens

    def parse_expression(self) -> Expression:
        """Parse an expression from a list of tokens"""
        if not self.tokens:
            raise ValueError("Tokens parameter is none.")

        op_token = next((token for token in self.tokens if token.type == 'BinaryOperator'), None)
        if not op_token:
            value = self.tokens[0]
            if value.type not in ('Number', 'Identifier'):
                raise ValueError(f"Invalid expression: {value.value}")
            return Expression(op=value.value)

        op_index = self.tokens.index(op_token)
        left = self.tokens[:op_index]
        right = self.tokens[op_index + 1:]

        lnode = Parser(left).parse_expression()
        rnode = Parser(right).parse_expression()

        return Expression(op=op_token.value, left=lnode, right=rnode)

class Environment:
    def __init__(self):
        self.variables = {}

    def declare_variable(self, tokens: list[Token]):
        keyword_token = tokens[0]
        if keyword_token.type != 'Keyword':
            raise ValueError(f"Expected keyword, got {keyword_token.value}")

        identifier_token = tokens[1]
        if identifier_token.type != 'Identifier':
            raise ValueError(f"Expected identifier, got {identifier_token.value}")

        if identifier_token.value in self.variables:
            raise ValueError(f"Variable '{identifier_token.value}' already declared")

        if len(tokens) < 4 or tokens[2].type != 'Operator' or tokens[2].value != '=':
            raise ValueError(f"Expected '=' after identifier")

        expression_tokens = tokens[3:-1] 
        parser = Parser(expression_tokens)
        expression = parser.parse_expression()
        value = expression.evaluate(self)

        self.variables[identifier_token.value] = value

    def MAKE_NUM(self, identifier: str, value: int):
        if identifier in self.variables:
            raise ValueError(f"Variable '{identifier}' already declared")
        
        self.variables[identifier] = value

def repl():
    environment = Environment()
    environment.MAKE_NUM("x", 23)
    environment.MAKE_NUM("pi", pi)
    while True:
        source = input(">> ")
        tokenizer = Tokenizer(source)
        tokens = tokenizer.tokens
        parser = Parser(tokens)
        ast = parser.parse_expression()
        result = ast.evaluate(environment)

        print(result)

if __name__ == "__main__":
    repl()
