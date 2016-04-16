# -*- coding: utf-8 -*-
# Time-stamp: < lod.py (2016-02-14 11:37) >

# Copyright (C) 2009-2016 Martin Slouf <martin.slouf@sourceforge.net>
#
# This file is a part of Summer.
#
# Summer is free software; you can redistribute it and/or modify it under
# the terms of the GNU Lesser General Public License as published by the Free
# Software Foundation; either version 3 of the License, or (at your option)
# any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA 02111-1307 USA
"""List of dictionaries (*lod*) -- simple yet powerfull in memory data
structure, ie. *grid*.

Thanks to: http://stackoverflow.com/questions/1038160/python-data-structure-for-maintaing-tabular-data-in-memory

This module is not imported into public *summer* namespace, so you should
import it directly::

    from summer import lod

"""
import csv
import logging
import io

logger = logging.getLogger(__name__)


def lod_populate(lod: list, fin: io.IOBase):
    """Populate lod using CSV file.

    Args:

        lod (list): list to be extended with data

        fin (io.IOBase): file-like object in CSV format

    """
    rdr = csv.DictReader(fin, delimiter=";", quotechar='"')
    lod.extend(rdr)


def lod_query(lod: list, filter_obj=None, sort_keys=None):
    """Lookup in lod based on query.

    Args:

        lod (list): lod to be used

        filter_obj: filter to be used

        sort_keys: sort criteria

    Returns:

        list: collection of matching rows
    """
    if filter_obj is not None:
        tmp = (r for r in lod if list(filter_obj(r)))
    if sort_keys is not None:
        tmp = sorted(lod, key=lambda r: [r[k] for k in sort_keys])
    else:
        tmp = list(lod)
    return tmp


def lod_lookup(lod: list, **kw):
    """Lookup in lod by attribute values.

    Args:

        lod (list): lod to be used

        **kw (dict): use keyword arguments.  keys are column names, their
                     value is attribute value

    Returns:

        list: first matching row
    """
    for row in lod:
        for k, v in kw.items():
            if row[k] != str(v):
                break
        else:
            return row
    return None
