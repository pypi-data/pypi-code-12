import platform
if 'Darwin' not in platform.system():  # noqa
    from .linux import recording  # noqa
else:  # noqa
    from .mac import recording  # noqa
