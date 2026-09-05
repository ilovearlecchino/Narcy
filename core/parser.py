from modules.ParseModels import *
from modules.Errors import BadToken
from modules.Errors import UnregisteredKeyword
from modules.KeywordRegistry import LoadRegistry

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
    "operator"
}

def infix_operator_bp(operator:object) -> tuple:
    if operator.type == 'operator':
        try:
            return _OPERATOR_BP[operator.token]
        except KeyError:
            raise BadToken(f"""Bad Token: Operator was either improperly pushed as a token
            or unregistered.""")
    else:
        raise BadToken(f"""Unexpected Token: Expected operator, got f{operator.type} instead.""")

def module_execute(args):
    CurrentNode = None
    Expression = [False, []]

    for index, item in enumerate(args):
        if args[index].type == 'keyword':
            try:
                CurrentNode = _KEYWORD_REGISTRY[args[index].token]
            except KeyError:
                if args[index].token not in _BLOCKED:
                    raise UnregisteredKeyword(
                                        f"""Keyword '{args[index].token}' not found in registry."""
                                        )
        # Come back here to finish reading
            
    return args