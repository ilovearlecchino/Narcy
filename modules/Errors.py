class NoDataTypes(Exception):
    """When the 'types.json' file is not found."""
    pass

class NoKeywords(Exception):
    """When 'keywords.json file is not found."""
    pass

class UnexpectedCharacterDuringFetch(Exception):
    """Normally a regular user wouldnt get this unless they tampered with the models."""
    pass

class BadToken(Exception):
    """When the parser receives an unexpectd token. Usually due to a bug in the code."""
    pass

class BadTree(Exception):
    """When a badly configured tree is passed into the parser"""

class UnregisteredKeyword(Exception):
    """Regular users will virtually never experience this error.
    However, if one attempts to add new keyword methods without registering them-
    then this error will be thrown."""
    pass

class UnregisteredTreeModel(Exception):
    """Similar to the above. An unregistered tree configuration was accessed."""
    pass

class InvalidSyntax(Exception):
    """Raised due to bad code"""
    pass