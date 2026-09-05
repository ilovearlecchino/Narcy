from dataclasses import dataclass

class Model:
    def __init__(self, identifier : str, start : str, end : str = '', double : bool = False):
        self.identifier = identifier
        self.start = start
        self.end = end
        self.double = double

@dataclass
class Token:
    token: str
    type: str