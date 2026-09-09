from dataclasses import dataclass
from typing import Optional, List

@dataclass
class ExpressionNode:
    value : list
    type : str = "expression"

@dataclass
class ValueHolderNode:
    value : object
    type : str = "valueholder"

    
    def __post_init__(self):
        """I noticed that the chunker returns a list of items due to the way it is designed
        this function ensures that the value is not a list as it's not meant to hold a list.
        """
        if isinstance(self.value, list) and len(self.value) == 1:
            self.value = self.value[0]

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
    BinaryOperationNode,
    AssignNode,
    OutputNode,
    ValueHolderNode,
    IfNode
}

def NodesRepr() -> dict:
    MAP = {}
    for node in Nodes:
        MAP[node.__name__] = node
    return MAP