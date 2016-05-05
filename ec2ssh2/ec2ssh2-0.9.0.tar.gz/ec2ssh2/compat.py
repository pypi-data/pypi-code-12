import sys
if sys.version_info[0] < 3:
    IS_PYTHON_2 = True
else:
    IS_PYTHON_2 = False


def iteritems(thing):
    if IS_PYTHON_2:
        return thing.iteritems()
    return thing.items()

def iterkeys(thing):
    if IS_PYTHON_2:
        return thing.iterkeys()
    return thing.keys()

def list_keys(thing):
    if IS_PYTHON_2:
        return thing.keys()
    return list(thing.keys())
