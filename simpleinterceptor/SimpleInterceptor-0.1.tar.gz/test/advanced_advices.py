"""Various advice formats for interceptor"""


def no_arg(_meth_signature, _ret=None, _exc=None):
    meth, meth_args, meth_kwargs = map(
        lambda attr: getattr(_meth_signature, attr), ('func', 'args', 'keywords'))
    print "No arg advice", meth, meth_args, meth_kwargs, _exc, _ret
