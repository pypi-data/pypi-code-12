class OpenStruct(object):
    def __init__(self, adict={}):
        self.__dict__.update(adict)

    def __getattr__(self, name):
        return self.__dict__.get(name)

    def __getitem__(self, key):
        return getattr(self, key)

    def __setitem__(self, key, val):
        return setattr(self, key, val)

    def __iter__(self):
        return self.__dict__.iteritems()

    def __repr__(self):
        return str({k: v for k, v in self if k[0] != '_'})
