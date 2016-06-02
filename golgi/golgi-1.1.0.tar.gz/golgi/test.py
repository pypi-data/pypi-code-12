import tryp.test

from golgi import Config

Config.enable_lazy_class_attr = False


class SpecConfigConcern:

    def setup(self, configs=['golgi'], allow_files=False, *a, **kw):
        super().setup(*a, **kw)
        Config.allow_files = allow_files
        Config.setup(*configs, files=allow_files)
        Config.override('general', debug=True)


class Spec(SpecConfigConcern, tryp.test.Spec):
    pass

__all__ = ('SpecConfigConcern',)
