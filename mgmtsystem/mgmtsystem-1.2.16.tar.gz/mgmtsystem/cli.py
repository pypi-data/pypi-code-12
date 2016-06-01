# -*- coding: utf-8 -*-
import inspect
import re
import sys

import mgmtsystem

def convert(name):
    s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', name)
    return re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1).lower()

PROVIDER_CLASSES = {}
for item in dir(mgmtsystem):
    if re.match(r'^[A-Z]', item) is None:
        continue
    cls = getattr(mgmtsystem, item)
    if not inspect.isclass(cls):
        continue

    if (issubclass(cls, mgmtsystem.MgmtSystemAPIBase) and cls is not mgmtsystem.MgmtSystemAPIBase
            and 'apibase' not in cls.__name__.lower()):
        PROVIDER_CLASSES[convert(cls.__name__)] = cls

def main():
    pass
