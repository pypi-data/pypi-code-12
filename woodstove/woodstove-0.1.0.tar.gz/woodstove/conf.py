import os


class EnvProvider(object):
    def get(self, section, name, default):
        return os.environ.get('%s_%s' % (section.upper(), name.upper()), default) 


__provider__ = EnvProvider()


def get(section, name, default):
    return __provider__.get(section, name, default) 
