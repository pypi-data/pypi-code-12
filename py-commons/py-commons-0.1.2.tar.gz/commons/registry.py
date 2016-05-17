
class Registry(object):
    def __init__(self):
        self.__registry = {}
        self.get = self.__registry.get

    def register(self, name):
        def registrar(obj):
            self.__registry[name] = obj
            return obj

        return registrar

    def __getitem__(self, item):
        if not item in self.__registry.keys():
            raise KeyError('%s was not found. Available entries: %s' % (item, list(self.__registry.keys())))
        return self.__registry[item]

    def construct(self, name, args=None, kwargs=None):
        if args is None:
            args = []
        if kwargs is None:
            kwargs = dict()
        return self[name](*args, **kwargs)