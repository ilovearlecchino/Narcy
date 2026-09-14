from dataclasses import dataclass
from modules.ParseModels import Nodes, NodesRepr
from modules.Errors import UnregisteredTreeModel
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

def GetStaticTypes():
    with open('registry.json', 'r') as f:
        _RET = json.loads(f.read())['StaticTypes']
    return _RET

def GetTreeConfig(keyword):
    with open('treemodels.json', 'r') as f:
        _MODS = json.loads(f.read())['TreeModels']
        for model in _MODS:
            if model['ID'] == keyword:
                return model['InputConfig']
        return UnregisteredTreeModel(
            f"""Unregistered tree configuration: {keyword}""",
            """If you've added a new tree model make sure to register it in treemodels.json"""
        )

def GetTDRDPMatchLookup():
    with open('registry.json', 'r') as f:
        return json.loads(f.read())['TDRDPMatchLookup']