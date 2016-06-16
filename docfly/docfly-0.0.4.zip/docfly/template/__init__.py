#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
try:
    from ..packages.dataIO import textfile
except:
    from docfly.packages.dataIO import textfile


class TemplateCollection(object):
    def __init__(self):
        data = dict()
        dir_path = os.path.dirname(__file__)
        for basename in os.listdir(dir_path):
            if basename.endswith(".tpl"):
                fname, ext = os.path.splitext(basename)
                abspath = os.path.join(dir_path, basename)
                data[fname] = textfile.read(abspath)        
        
        self.module = data["module"]
        self.package = data["package"]
        self.index = data["index"]


template_collection = TemplateCollection()