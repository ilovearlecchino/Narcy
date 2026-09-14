import sys
import importlib
from datetime import datetime



VERSION = "0.6.8-P-B"
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

    # Reset log file (it keeps appending instead)
    with open('.log', 'w') as f:
        f.write(f"""
Compiler started; timestamp: {datetime.now()}. Version {VERSION}.\n\n\n\n
""")
    

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