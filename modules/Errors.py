class NoDataTypes(Exception):
    """When the 'types.json' file is not found."""
    pass

class NoKeywords(Exception):
    """When 'keywords.json file is not found."""
    pass

class UnexpectedCharacterDuringFetch(Exception):
    """Normally a regular user wouldnt get this unless they tampered with the models."""
    pass