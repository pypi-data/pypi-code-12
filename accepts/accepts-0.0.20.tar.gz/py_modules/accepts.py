#!/usr/bin/env python
from objectname import objectname
from public import public
from tolist import tolist


@public
def accepts(*types):
    def check_accepts(f):
        # assert len(types) == f.func_code.co_argcount
        def new_f(*args, **kwargs):
            for i, (a, t) in enumerate(zip(args, types), 1):
                if t is None or None in tolist(t):
                    if a is None:
                        continue
                _t = tuple(filter(None, tuple(tolist(t))))  # exclude None
                if not isinstance(a, _t):
                    name = objectname(f, fullname=True)
                    lines = [
                        "%s() argument #%s is not instance of %s" %
                        (name, i, t)]
                    lines += ["args: %s" % str(list(args))]
                    lines += ["arg#%s: %s" % (i, a)]
                    msg = "\n".join(lines)
                    raise TypeError(msg)
            return f(*args, **kwargs)
        try:  # python2
            new_f.func_name = f.func_name
        except AttributeError:  # python3
            new_f.__name__ = f.__name__
        return new_f
    return check_accepts
