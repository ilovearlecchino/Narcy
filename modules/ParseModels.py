from dataclasses import dataclass
from typing import Optional, List

@dataclass
class ExpressionNode:
    value : list

@dataclass
class LiteralNode:
    value : object

@dataclass
class VariableNode:
    name: str

@dataclass
class BinaryOperationNode:
    operation : str
    left : object
    right : object

@dataclass
class AssignNode:
    name : str
    value : object

@dataclass
class OutputNode:
    value : object

@dataclass
class IfNode:
    condition : object
    body : list
    else_body: Optional[List] = None

Nodes = {
    ExpressionNode,
    LiteralNode,
    VariableNode,
    BinaryOperationNode,
    AssignNode,
    OutputNode,
    IfNode
}

def NodesRepr() -> dict:
    MAP = {}
    for node in Nodes:
        MAP[node.__name__] = node
    return MAP