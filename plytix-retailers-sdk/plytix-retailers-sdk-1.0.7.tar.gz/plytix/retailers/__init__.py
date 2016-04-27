__version__ = '1.0.7'

API_VERSION = 'v0.2'
API_URL = 'https://analytics.plytix.com/api/retailers/{version}'.format(version=API_VERSION)


def enum(**enums):
    return type('Enum', (), enums)

from .fields import INFO_SYNC_PICTURES, INFO_PLATFORM_NAME, INFO_PLATFORM_VERSION, \
    INFO_SUBPLATFORM_NAME, INFO_SUBPLATFORM_VERSION, INFO_PLYTIX_PLUGIN_VERSION, INFO_USE_CDN
