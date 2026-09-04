def Log(coming_from = None, reason = None, *args, **kwargs):
    def INTERNAL_DECORATOR(logged : function):
        def WRAPPER(*args, **kwargs):
            logstr = f"Function {logged.__name__} was called"
            with open('.log', 'a') as f:

                if (coming_from() != None):
                    logstr += f" by function {coming_from()}"
                if (reason() != None):
                    logstr += f" for reason: {reason()}"
                logstr += f" with payload: {args};\n"
                f.write(logstr)
                result = logged(*args, **kwargs)
                return result
        return WRAPPER
    return INTERNAL_DECORATOR
