from functools import wraps

def lua_object_method(func, lua):
    """
    Wraps python method into a lua-wrapper which looks like "function"
    in lua to be determined as a method.
    """
    return lua.eval('''
        function(func)
            return function(...) return func(...) end
        end
    ''')(func)
