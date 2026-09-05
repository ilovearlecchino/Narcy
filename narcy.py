import sys
import importlib

DEFAULT_TOKENIZER = "core.tokenizer"
DEFAULT_PARSER = "core.parser"


PIPELINE = [ # Best for quick interception
    DEFAULT_TOKENIZER,
    DEFAULT_PARSER,
] 

if __name__ == "__main__":
    # Default namespacing : module_execute
    args = ['']
    FUNCTION_PIPELINE = []
    for module in PIPELINE:
        FUNCTION_PIPELINE.append(importlib.import_module(module).module_execute)
        #print(module)
    

    if sys.argv[1] == '-s':
        _ARG1 = input(' > ')
        args[0] = _ARG1
    else:
        with open(sys.argv[1], 'r') as f:
            args[0] = f.read()
    CurrentPayload = args[0]
    for function in FUNCTION_PIPELINE:
        
        CurrentPayload = function(CurrentPayload)

    #print(CurrentPayload)