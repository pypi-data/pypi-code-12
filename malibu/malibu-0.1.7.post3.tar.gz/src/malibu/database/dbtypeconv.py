# -*- coding: utf-8 -*-
import json
import sqlite3

__doc__ = """
malibu.database.dbtypeconv
--------------------------

This module contains small functions for installing and performing JSON
conversion on data coming out from a SQLite database.

Pretty much useless-ish without DBMapper.
"""


def install_json_converter():
    """ Installs a json object converter into the sqlite3 module for
        quick type conversions.
    """

    sqlite3.register_converter("json", __convert_json)


def __convert_json(string):
    """ Converts a string into JSON format.  If the conversion fails,
        returns None.
    """

    try:
        return json.loads(string)
    except:
        return None
