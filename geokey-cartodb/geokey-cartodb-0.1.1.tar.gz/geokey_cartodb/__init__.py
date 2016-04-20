from geokey.extensions.base import register


VERSION = (0, 1, 1)
__version__ = '.'.join(map(str, VERSION))

register(
    'geokey_cartodb',
    'CartoDB',
    display_admin=True,
    superuser=False
)
