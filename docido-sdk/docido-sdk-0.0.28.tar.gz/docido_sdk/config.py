import sys

from . toolbox.collections_ext import Configuration, contextobj

sys.modules[__name__] = contextobj(Configuration.from_env(
    'DOCIDO_CONFIG',
    'settings.yml',
    Configuration()
))
# This module is now the configuration object itself.
