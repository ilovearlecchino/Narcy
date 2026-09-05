from dataclasses import dataclass
from modules.ParseModels import Nodes, NodesRepr
import json

@dataclass
class Registry:
    keyword: str
    node : object

def LoadRegistry() -> dict:
    MAP = NodesRepr()
    _REGISTRY = {}
    with open('registry.json', 'r') as f:
        UnassignedMap = json.loads(f.read())['KeywordRegistry']
        for keyword in UnassignedMap:
            _REGISTRY[keyword] = MAP[UnassignedMap[keyword]]
    return _REGISTRY