# -*- coding: utf-8 -*-
"""
functions.py is part of Coquery.

Copyright (c) 2016 Gero Kunter (gero.kunter@coquery.org)

Coquery is released under the terms of the GNU General Public License (v3).
For details, see the file LICENSE that you should have received along 
with Coquery. If not, see <http://www.gnu.org/licenses/>.
"""
from __future__ import unicode_literals

import hashlib

from .defines import *

class Function(object):
    """
    The Link class is used to link a table from one corpus to another corpus.
    """
    
    def __init__(self, resource):
        self.resource = resource
        
    def get_hash(self):
        l = []
        for x in sorted(dir(self)):
            if not x.startswith("_") and not hasattr(getattr(self, x), "__call__"):
                l.append(str(getattr(self, x)))
        return hashlib.md5(u"".join(l).encode()).hexdigest()
        
    def __repr__(self):
        return "Function(resource='{}')".format(self.resource)

    def

def get_function_by_hash(func_list, hash):
    for func in func_list:
        if func.get_hash() == hash:
            return func

def Length(Function)

def get_by_hash(hashed, link_list=None):
    """
    Return the link and the linked resource for the hash.
    
    Parameters
    ----------
    hashed : str 
        A hash string that has been produced by the get_hash() method.
    
    link_list : list of Link objects
        A list of links that is used to lookup the hash. If not provided,
        the link list for the current server and resource is used.
    
    Returns
    -------
    tup : tuple
        A tuple with the associated link as the first and the linked resource
        as the second element.
    """
    from . import options
    if not link_list:
        link_list = options.cfg.table_links[options.cfg.current_server]
    
    link = get_link_by_hash(link_list, hashed)
    res = options.get_resource(link.res_to)[0]
    return (link, res)