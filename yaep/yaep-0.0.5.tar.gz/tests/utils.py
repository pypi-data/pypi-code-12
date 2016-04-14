import contextlib


@contextlib.contextmanager
def monkey_patch(module, function_name, patch):
    original = getattr(module, function_name, None)
    setattr(module, function_name, patch)
    try:
        yield
    finally:
        if original:
            setattr(module, function_name, original)
