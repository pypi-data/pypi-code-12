# -*- coding:utf-8 -*-
import pandas as pd
import sys
import logging
import inspect
from base import PipelineEntity

_log = logging.getLogger(__name__)


def importing(func):
    func.is_importing = True
    return func


def exporting(func):
    func.is_exporting = True
    return func


class DataSource(PipelineEntity):

    def __init__(self, name='NoName DataSource', **kwargs):
        PipelineEntity.__init__(self)
        self.priority = 0
        self.type = 'source'
        self.name = name
        self._config = kwargs
        self._import_functions = []

    def __call__(self):
        dfs = [import_function() for import_function in self._import_functions]
        if len(dfs) > 1:
            result = pd.concat(dfs, axis=1)
        else:
            result = dfs[0]
        return result

    def register(self, pipeline):
        _log.info('Register DataSource %s in %s pipeline' % (self.__class__.__name__, pipeline.name))
        import_functions = inspect.getmembers(self, predicate=lambda func: isinstance(func, inspect.types.MethodType)
                                                                        and getattr(func, 'is_importing', False))
        for name, import_function in import_functions:
            self._import_functions.append(import_function)


class DataOutlet(PipelineEntity):

    def __init__(self, name='NoName DataOutlet', **kwargs):
        PipelineEntity.__init__(self)
        self.priority = sys.maxint
        self.type = 'outlet'
        self.name = name
        self._config = kwargs
        self._export_functions = []

    def __call__(self, df):
        [export_function(df) for export_function in self._export_functions]
        return df

    def register(self, pipeline):
        _log.info('Register DataSource %s in %s pipeline' % (self.__class__.__name__, pipeline.name))
        export_functions = inspect.getmembers(self, predicate=lambda func: isinstance(func, inspect.types.MethodType)
                                                                        and getattr(func, 'is_exporting', False))
        for name, export_function in export_functions:
            self._export_functions.append(export_function)


class CSVDataSource(DataSource):

    def __init__(self, source, **kwargs):
        DataSource.__init__(self, 'CSVDataSource', **kwargs)
        self._source = source

    @importing
    def load(self):
        return pd.read_csv(self._source, **self._config)


class ConstantDataSource(DataSource):

    def __init__(self, df, **kwargs):
        DataSource.__init__(self, 'ConstantDataSource', **kwargs)
        self.df = df

    @importing
    def const(self):
        return self.df
