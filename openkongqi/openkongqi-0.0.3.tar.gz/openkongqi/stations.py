# -*- coding: utf-8 -*-

from __future__ import absolute_import, print_function, unicode_literals

from .conf import settings
from .exceptions import UUIDNotFoundError
from .utils import load_tree, passthrough_loader

_STATIONS_MAP = load_tree(settings['STATIONS_MAP_DIR'],
                          data_loader=passthrough_loader)


def get_station_map(uuid=None):
    """Get the entire station map, given a UUID

    Usage::
        >>> from openkongqi.stations import get_station_map
        >>> get_uuid_map('cn-shanghai')
        ...

    :param uuid: a UUID key
    :type uuid: str
    """
    try:
        id_map = _STATIONS_MAP[uuid]
    except KeyError:
        raise UUIDNotFoundError("Unknown UUID ({})".format(uuid))
    return id_map
