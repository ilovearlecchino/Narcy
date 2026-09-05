"""
Default tokenizer for Narcy.
Coded by Ali Nafea Al-kazzaz.
Integrated into Narcy by PyroByte.

A rather primitive implementation. Reliable, however.
"""

import json
from dataclasses import dataclass
from modules.Debug import Log
from modules.DatatypeModel import Model, Token
from modules.Errors import *

"""Version 0.7
Added 'IsNumeric' to include numbers.
"""

N_LOG_CALLED_FROM = None
N_LOG_REASON = None
STOP_CHARS = [" ", "\t", "\n"]

def SetLogContext(called_from: str, reason: str):
    global N_LOG_CALLED_FROM, N_LOG_REASON
    N_LOG_CALLED_FROM = called_from
    N_LOG_REASON = reason

@Log(lambda: N_LOG_CALLED_FROM, lambda: N_LOG_REASON)
def N_IsNumeric(token : str) -> bool:
    SetLogContext("Registry.resolve_type", "Check if token is numeric")
    try:
        float(token)
        return True
    except ValueError:
        return False


# --- Dynamic Token Registry ---
class TokenTypeRegistry:
    def __init__(self, config_path: str):
        try:
            with open(config_path, 'r') as f:
                data = json.load(f)
        except FileNotFoundError:
            raise NoDataTypes(f"Missing critical data. Couldn't fetch '{config_path}'.")

        # Models (Delimited types)
        self.models = [
            Model(m['identifier'], m['start'], m.get('end', m['start']), m.get('double', False))
            for m in data.get('models', [])
        ]
        
        # Categorized string lookups (keywords, operators, etc.)
        self.categories = {
            key: set(values) 
            for key, values in data.items() 
            if key != 'models'
        }

    def resolve_type(self, token: str) -> str:
        """Matches a token string against all JSON categories dynamically."""
        for category_name, token_set in self.categories.items():
            if token in token_set:
                # Strip plural 's' if standard naming (e.g. keywords -> keyword)
                return category_name[:-1] if category_name.endswith('s') else category_name
        if N_IsNumeric(token):
            return 'numeric'
        return 'statement'

# Initialize Registry
REGISTRY = TokenTypeRegistry('types.json')
N_TYPES = REGISTRY.models

@Log(lambda: N_LOG_CALLED_FROM, lambda: N_LOG_REASON)
def N_GetTokenType(token: str) -> str:
    SetLogContext("N_GetTokenType", f"Determining token type for '{token}'")
    return REGISTRY.resolve_type(token)

@Log(lambda: N_LOG_CALLED_FROM, lambda: N_LOG_REASON)
def N_FetchModelByStart(char: str):
    SetLogContext("N_FetchModelByStart", f"Fetching model matching start character '{char}'")
    for model in N_TYPES:
        if char == model.start:
            return model
    raise UnexpectedCharacterDuringFetch(
        "Called to fetch for a model whose start couldn't be found."
    )

@Log(lambda: N_LOG_CALLED_FROM, lambda: N_LOG_REASON)
def N_EmitToken(tokens: list, token_text: str, token_type: str):
    SetLogContext("N_EmitToken", f"Emitting token '{token_text}' as type '{token_type}'")
    tokens.append(Token(token_text, token_type))

@Log(lambda: N_LOG_CALLED_FROM, lambda: N_LOG_REASON)
def module_execute(source):
    SetLogContext("Tokenize", "Starting lexical analysis of source string")
    
    AlertChars = [model.start for model in N_TYPES]
    tokens = []
    CurrentToken = ""
    CurrentModel = None
    depth = 0

    if type(source) == list:
        _STR_source = source[0]
    else:
        _STR_source = source
    for idx, char in enumerate(_STR_source):
        # --- Inside a Model/Literal Block ---
        if CurrentModel:
            if CurrentModel.start != CurrentModel.end and char == CurrentModel.start:
                depth += 1
                CurrentToken += char
                SetLogContext("Tokenize", f"Nested model start '{char}' at index {idx}, depth increased to {depth}")
                continue
            
            if char == CurrentModel.end:
                if depth > 0:
                    depth -= 1
                    CurrentToken += char
                    SetLogContext("Tokenize", f"Nested model end '{char}' at index {idx}, depth decreased to {depth}")
                else:
                    SetLogContext("Tokenize", f"Model block closed for '{CurrentModel.identifier}' at index {idx}")
                    N_EmitToken(tokens, CurrentToken, CurrentModel.identifier)
                    CurrentToken = ""
                    CurrentModel = None
                continue

            CurrentToken += char
            continue

        # --- Whitespace Delimiters ---
        if char in STOP_CHARS:
            if CurrentToken != "":
                token_type = N_GetTokenType(CurrentToken)
                N_EmitToken(tokens, CurrentToken, token_type)
                CurrentToken = ""
            SetLogContext("Tokenize", f"Skipped whitespace character at index {idx}")
            continue

        # --- Model Start (Strings / Brackets) ---
        if char in AlertChars:
            if CurrentToken != "":
                token_type = N_GetTokenType(CurrentToken)
                N_EmitToken(tokens, CurrentToken, token_type)
                CurrentToken = ""
            
            CurrentModel = N_FetchModelByStart(char)
            depth = 0
            SetLogContext("Tokenize", f"Entered model '{CurrentModel.identifier}' via char '{char}' at index {idx}")
            continue

        # --- Standard Character ---
        CurrentToken += char

    # Flush remaining token at EOF
    if CurrentToken != "":
        token_type = N_GetTokenType(CurrentToken)
        N_EmitToken(tokens, CurrentToken, token_type)
        SetLogContext("Tokenize", "Flushed final remaining token at end of source")

    return tokens
