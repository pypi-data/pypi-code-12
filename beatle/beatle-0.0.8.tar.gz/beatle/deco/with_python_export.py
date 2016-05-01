# -*- coding: utf-8 -*-

"""
This decorator applies to python operations that successfully transact for export files.
This decorator only applies on views that operate over selected elements
"""


def with_python_export(function):
    """method decorator that provides self name access"""
    def wrap(self, *args, **kwargs):
        """wrapped calls"""
        if function(self, *args, **kwargs):
            try:
                s = self.selected
                r = s.inner_module or s.inner_package
                if r:
                    r.ExportPythonCodeFiles()
            except:
                raise ValueError('with_python_export decorator only works on views with selected item')
    return wrap

