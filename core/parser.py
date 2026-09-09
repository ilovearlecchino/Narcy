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
    
class AbstractParser:
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

class Chunker(AbstractParser):
    def __init__(self, tokens, allowed_types, result_node, min_length=2):
        super().__init__(tokens)
        self.allowed_types = allowed_types
        self.result_node = result_node
        self.min_length = min_length

    def get_token_type(self, tok):
        if hasattr(tok, 'get_type'):
            return tok.get_type()
        return getattr(tok, 'type', None)

    def _flush_expr(self, expr_list, target_list):
        """Wraps in result_node if min_length is met; otherwise unpacks directly."""
        if not expr_list:
            return
        if len(expr_list) >= self.min_length:
            target_list.append(self.result_node(expr_list.copy()))
        else:
            # Below min_length: restore original items directly
            target_list.extend(expr_list)

    def chunk(self):
        _TOKS = []
        _EXPR = []
        _TOK = self.advance()

        while self.get_token_type(_TOK) != 'eof':
            tok_type = self.get_token_type(_TOK)

            if tok_type in self.allowed_types:
                _EXPR.append(_TOK)
                # If next item stops matching, attempt flush
                if self.get_token_type(self.peek()) not in self.allowed_types:
                    self._flush_expr(_EXPR, _TOKS)
                    _EXPR = []
            else:
                if _EXPR:
                    self._flush_expr(_EXPR, _TOKS)
                    _EXPR = []
                _TOKS.append(_TOK)

            _TOK = self.advance()

        # Handle any remaining buffer at end of sequence
        if _EXPR:
            self._flush_expr(_EXPR, _TOKS)

        return _TOKS

_ABSTRACTIONS = [
    (_EXPRESSION_ALLOWED_TYPES, ExpressionNode, 2),
    (_EXPRESSION_ALLOWED_TYPES | {'expression'}, ValueHolderNode, 1)
]

def module_execute(args):
    CurrentNode = None
    args.append(Token('eof', 'eof'))
    for types, node, min in _ABSTRACTIONS:
        args = Chunker(args, types, node, min).chunk()
    pprint(args)
    return args