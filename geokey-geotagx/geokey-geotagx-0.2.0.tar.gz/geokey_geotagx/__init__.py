from geokey.extensions.base import register


VERSION = (0, 2, 0)
__version__ = '.'.join(map(str, VERSION))

register(
    'geokey_geotagx',
    'GeoTag-X',
    display_admin=False,
    superuser=False
)
