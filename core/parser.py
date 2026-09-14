from modules.DatatypeModel import Token
from modules.ParseModels import *
from modules.Errors import BadToken
from modules.Errors import UnregisteredKeyword
from modules.Errors import InvalidSyntax
from modules.Errors import BadTree
from modules.KeywordRegistry import LoadRegistry
from modules.KeywordRegistry import GetStaticTypes
from modules.KeywordRegistry import GetTreeConfig
from modules.KeywordRegistry import GetTDRDPMatchLookup
from pprint import pprint
from colorama import Fore, init

init(autoreset=True)

_TDRDP_MATCH_LOOKUP = GetTDRDPMatchLookup()
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

_CONDITIONAL_ABSTRACTION =  {
    "keyword"
}

_STATIC_TYPES= GetStaticTypes()

def Eof_Safe(func):
    def wrapper(self, *args, **kwargs):
        try:
            return func(self, *args, **kwargs)
        except IndexError:
            return Token('eof', 'eof')
    return wrapper

def SpecializeToken(token : Token):
    if token.type in _STATIC_TYPES:
        return token.token
    else:
        return getattr(token, 'type')

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
    def __init__(
        self, 
        tokens, 
        allowed_types, 
        result_node, 
        min_length=2, 
        specific_matches=None, 
        match_sequence=None
    ):
        super().__init__(tokens)
        self.allowed_types = set(allowed_types) if allowed_types else set()
        self.result_node = result_node
        self.min_length = min_length
        
        # specific_matches: Set/List of (type, value) tuples or values, e.g. {("keyword", "elif"), ("keyword", "if")}
        self.specific_matches = set(specific_matches) if specific_matches else set()
        
        # match_sequence: Optional ordered list of matchers to start a chunk, e.g. [("keyword", "elif"), "parentheses"]
        self.match_sequence = match_sequence

    def get_token_type(self, tok):
        if hasattr(tok, 'get_type'):
            return tok.get_type()
        return getattr(tok, 'type', None)

    def get_token_value(self, tok):
        if hasattr(tok, 'get_value'):
            return tok.get_value()
        return getattr(tok, 'value', None)

    def _matches_rule(self, tok, rule):
        """Helper to match a token against a type, a (type, value) tuple, or a raw value."""
        tok_type = self.get_token_type(tok)
        tok_val = self.get_token_value(tok)

        if isinstance(rule, tuple):  # Matches (type, value)
            return tok_type == rule[0] and tok_val == rule[1]
        elif rule in self.allowed_types: # Matches token type
            return tok_type == rule
        else: # Matches direct value
            return tok_val == rule

    def is_match(self, tok):
        if tok is None or self.get_token_type(tok) == 'eof':
            return False

        tok_type = self.get_token_type(tok)
        tok_val = self.get_token_value(tok)

        # 1. Match against allowed general types
        if tok_type in self.allowed_types:
            return True

        # 2. Match against specific (type, value) or direct values
        if tok_val in self.specific_matches or (tok_type, tok_val) in self.specific_matches:
            return True

        return False

    def _flush_expr(self, expr_list, target_list):
        """Wraps in result_node if min_length is met; otherwise unpacks directly."""
        if not expr_list:
            return
        if len(expr_list) >= self.min_length:
            target_list.append(self.result_node(expr_list.copy()))
        else:
            target_list.extend(expr_list)

    def _check_sequence_start(self):
        """Verifies if current cursor position starts an exact required sequence."""
        if not self.match_sequence:
            return True
        
        for i, rule in enumerate(self.match_sequence):
            # Look ahead relative to current token
            peek_tok = self.peek_at(self.index + i)
            if not self._matches_rule(peek_tok, rule):
                return False
        return True

    def peek_at(self, idx):
        if idx < len(self.tokens):
            return self.tokens[idx]
        return Token('eof', 'eof')

    def chunk(self):
        _TOKS = []
        _EXPR = []
        _TOK = self.advance()

        while self.get_token_type(_TOK) != 'eof':
            # Check sequence requirement if chunk isn't active yet
            sequence_valid = True
            if not _EXPR and self.match_sequence:
                # Need to rewind index by 1 because self.advance() already took _TOK
                self.index -= 1
                sequence_valid = self._check_sequence_start()
                self.index += 1

            if sequence_valid and self.is_match(_TOK):
                _EXPR.append(_TOK)
                
                # Check if the next token continues the match
                next_tok = self.peek()
                if not self.is_match(next_tok):
                    self._flush_expr(_EXPR, _TOKS)
                    _EXPR = []
            else:
                if _EXPR:
                    self._flush_expr(_EXPR, _TOKS)
                    _EXPR = []
                _TOKS.append(_TOK)

            _TOK = self.advance()

        if _EXPR:
            self._flush_expr(_EXPR, _TOKS)

        return _TOKS

class ComplexParser():
    def __init__(self, tokens, special_sequence, result_node, node_name):
        self.tokens= tokens
        self.special_sequence = special_sequence
        self.result_node = result_node.__new__(result_node)
        self.node_attr_config = GetTreeConfig(node_name)

    def validate_syntax(self):
        _=[]
        _I = 0
        while _I < len(self.tokens):
            _SPECIAL_TOKEN = SpecializeToken(self.tokens[_I])
            if self.special_sequence[_I] != _SPECIAL_TOKEN:
                _INV_SYNTAX_OUT = ""
                for i in range(0, _I):
                    if SpecializeToken(self.tokens[i]) == _SPECIAL_TOKEN:
                        _INV_SYNTAX_OUT += (Fore.RED + self.tokens[i].type)
                    else:
                        _INV_SYNTAX_OUT += (Fore.WHITE + self.tokens[i].type)
                raise InvalidSyntax(
                    f"""Syntax Error; Invalid Syntax""",
                    _INV_SYNTAX_OUT
                )
            _I += 1

    def parse(self):
        self.validate_syntax()
        self.node_attr_config = self.node_attr_config['attributes']
        for attribute in self.node_attr_config:
            try:
                setattr(self.result_node, attribute, self.tokens[self.node_attr_config[attribute]])
            except AttributeError:
                raise BadTree(
                    f"""Improperly configured tree: {getattr(self.result_node, 'type')}"""
                )
        return self.result_node

_ABSTRACTIONS = [
    (_EXPRESSION_ALLOWED_TYPES, ExpressionNode, 2),
    (_EXPRESSION_ALLOWED_TYPES | {'expression'}, ValueHolderNode, 1)
]

def module_execute(args):
    args.append(Token('eof', 'eof'))

#    print("\n========== PARSER INPUT ==========")
    pprint(args)
    # pre pass
#    print("\n========== CHUNKING ==========")

    for types, node, min_length in _ABSTRACTIONS:
#        print(f"\nChunker: {node.__name__}")
#        print(f"Allowed types: {types}")
#        print(f"Minimum length: {min_length}")

        args = Chunker(
            args,
            types,
            node,
            min_length
        ).chunk()

        pprint(args)

#    print("\n========== COMPLEX PARSER ==========")

    output = []
    index = 0

    while index < len(args):

        token = args[index]

        # EOF
        if token.type == 'eof':
            break

        # Non-keyword tokens shouldn't start a complex node
        if token.type != 'keyword':
            print(f"[PASS] Non-keyword token: {token}")
            output.append(token)
            index += 1
            continue

        keyword = token.token

#        print(f"\n[KEYWORD] {keyword}")

        if keyword not in _KEYWORD_REGISTRY:
            raise UnregisteredKeyword(
                f"Unregistered keyword: {keyword}"
            )

        node_class = _KEYWORD_REGISTRY[keyword]
        node_name = node_class.__name__

#        print(f"  Node: {node_name}")

        # --------------------------------
        # Look up node -> expected sequence
        # --------------------------------

        special_sequence = None

        for match in _TDRDP_MATCH_LOOKUP:
            if node_name in match:
                special_sequence = match[node_name]
                break

        if special_sequence is None:
            raise BadTree(
                f"No TDRDP match configuration for {node_name}"
            )

 #       print(f"  Expected sequence: {special_sequence}")

        argument_count = len(special_sequence)

        node_tokens = args[
            index + 1:
            index + 1 + argument_count
        ]

#        print("  Tokens passed to ComplexParser:")
#        pprint(node_tokens)

        parser = ComplexParser(
            node_tokens,
            special_sequence,
            node_class,
            node_name
        )

        node = parser.parse()

#        print("  Result:")
#        pprint(node)

        output.append(node)

        index += 1 + argument_count

#    print("\n========== PARSER OUTPUT ==========")
    pprint(output)

    return output