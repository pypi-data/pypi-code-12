
def resolve_name(name, module=None):
    """Resolve a dotted name to a module and its parts. This is stolen
    wholesale from unittest.TestLoader.loadTestByName.
    """
    parts = name.split('.')
    parts_copy = parts[:]
    if module is None:
        while parts_copy:  # pragma: no cover
            try:
                module = __import__('.'.join(parts_copy))
                break
            except ImportError:
                del parts_copy[-1]
                if not parts_copy:
                    raise
        parts = parts[1:]
    obj = module
    for part in parts:
        obj = getattr(obj, part)
    return obj
