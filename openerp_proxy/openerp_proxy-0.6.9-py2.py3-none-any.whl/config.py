# from .utils import AttrDict
__all__ = ('config',)


class Config(dict):
    def get(self, opt, default):
        self.default(opt, default)
        return self[opt]

    def set(self, opt, val):
        self[opt] = val
        return val

    def default(self, opt, val):
        if opt not in self:
            self[opt] = val
        return self[opt]


config = Config()
