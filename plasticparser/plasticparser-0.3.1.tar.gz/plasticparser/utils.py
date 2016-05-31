def deprecated(func):
    def deprecated_func(*args, **kwargs):
        import logging
        log = logging.getLogger()
        log.warn("{} is deprecated!".format(func))
        return func(*args, **kwargs)
    return deprecated_func
