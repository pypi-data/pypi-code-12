def page(name, by, locator):

    def decorator(cls):
        setattr(cls, 'name', name)
        setattr(cls, 'by', by)
        setattr(cls, 'locator', locator)
        return cls

    return decorator
