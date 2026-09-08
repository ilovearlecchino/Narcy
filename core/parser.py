from modules.DatatypeModel import Token
from modules.ParseModels import *
from modules.Errors import BadToken
from modules.Errors import UnregisteredKeyword
from modules.KeywordRegistry import LoadRegistry
from pprint import pprint

_KEYWORD_REGISTRY = LoadRegistry()
_BLOCKED = {"else"}

_OPERATOR_BP = {
    '+' : (1, 2),
    '-' : (1, 2),
    '*' : (3, 4),
    '/' : (3, 4),
}

_EXPRESSION_ALLOWED_TYPES = {
    "string",
    "numeric",
    "operator",
    "statement"
}

def Eof_Safe(func):
    def wrapper(self, *args, **kwargs):
        try:
            return func(self, *args, **kwargs)
        except IndexError:
            return Token('eof', 'eof')
    return wrapper
    
class BaseParser:
    def __init__(self, tokens):
        self.index = 0
        self.tokens = tokens

    @Eof_Safe
    def peek_next(self):
        return self.tokens[self.index + 1]

    @Eof_Safe
    def peek(self):
        return self.tokens[self.index]

    @Eof_Safe
    def advance(self):
        tok = self.tokens[self.index]
        self.index += 1
        return tok

class ExpressionAnalyzer(BaseParser):
    def convert_into_expressions(self):
        _TOKS = []
        _EXPR = []
        _TOK = self.advance()

        while _TOK.type != 'eof':
            if _TOK.type in _EXPRESSION_ALLOWED_TYPES:
                if self.peek().type in _EXPRESSION_ALLOWED_TYPES:
                    _EXPR.append(_TOK)
                else:
                    if not _EXPR:
                        # Single isolated token, append directly
                        _TOKS.append(_TOK)
                    else:
                        # Append final token in sequence and create expression node
                        _EXPR.append(_TOK)
                        _TOKS.append(ExpressionNode(_EXPR))
                        _EXPR = []
            else:
                _TOKS.append(_TOK)

            _TOK = self.advance()

        _TOKS.append(Token('eof', 'eof'))
        return _TOKS
                    

def _INFIX_BP(operator : Token):
    try:
        return _OPERATOR_BP[operator.token]
    except KeyError:
        raise BadToken(f"""Unrecognized operator: {operator.token}""")

    

def module_execute(args):
    CurrentNode = None
    args.append(Token('eof', 'eof'))
    args = ExpressionAnalyzer(args).convert_into_expressions()
    pprint(args)
    return args