class OpenStruct(object):
    def __init__(self, adict):
        self.__dict__.update(adict)

    def __getattr__(self, name):
        return self.__dict__.get(name)

    def __repr__(self):
        return str({k: v for k, v in self.__dict__.iteritems() if k[0] != '_'})
