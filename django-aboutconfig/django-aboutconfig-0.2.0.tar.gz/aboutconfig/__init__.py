"""A firefox-like about:config implementation for one-off settings in Django apps."""

__version__ = (0, 2, 0)
default_app_config = 'aboutconfig.apps.AboutconfigConfig' # pylint: disable=invalid-name


def get_config(key, value_only=True):
    """Get configured value by key.

    By default returns value only. If `value_only` is `False`, returns an instance of
    aboutconfig.utils.DataTuple which also contains the `allow_template_use` value.

    This is a lazy wrapper around `utils.get_config()`."""

    from . import utils

    return utils.get_config(key, value_only)
