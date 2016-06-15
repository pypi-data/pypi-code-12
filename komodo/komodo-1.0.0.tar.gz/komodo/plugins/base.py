

class PluginBase(object):
    def flask_init(self, app):
        raise NotImplementedError
