#
# -*- coding: utf-8 -*-
#
# Copyright (c) 2016 Esther Kruis and Anselm Kruis
#
# This library is free software; you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public
# License as published by the Free Software Foundation; either
# version 2.1 of the License, or (at your option) any later version.
#
# This library is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
# Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public
# License along with this library; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA
#

import importlib
import pkgutil
import inspect

_modules = None


def _load_submodules():
    global _modules
    if _modules is None:
        _modules = [importlib.import_module(t[1]) for t in pkgutil.iter_modules(__path__, __name__ + '.')]
    return _modules


def get_subclasses_of(cls):
    classes = []
    for mod in _load_submodules():
        classes.extend(c[1]
                       for c in inspect.getmembers(mod, inspect.isclass) if issubclass(c[1], cls) and c[1] is not cls)
    return classes
