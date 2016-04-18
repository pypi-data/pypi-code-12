# -*- coding:utf-8 -*-
import inspect
import logging
import pandas as pd
from base import PipelineEntity

_log = logging.getLogger(__name__)


def mapping(func=None, result=None, required_columns=(), external_pipe=()):
    def process(dec_func):
        dec_func.is_mapping = True
        dec_func.type = 'reduce'
        if not getattr(dec_func, 'mapping_info', False):
            dec_func.mapping_info = []
        dec_func.mapping_info.append([
            result if result else dec_func.__name__,
            required_columns if len(required_columns) != 0 else dec_func.func_code.co_varnames[1:]
        ])
        dec_func.external_pipe = external_pipe
        return dec_func

    if func:
        return process(func)
    return process


def mixin(func=None, result=None, external_pipe=()):
    def process(dec_func):
        dec_func.is_mapping = True
        dec_func.type = 'mixin'
        dec_func.result = result if result else dec_func.__name__
        dec_func.external_pipe = external_pipe
        return dec_func
    if func:
        return process(func)
    return process


class Mapper(PipelineEntity):

    def __init__(self):
        super(Mapper, self).__init__()
        self.priority = 20
        self.reduce_mapping = []
        self.mixin_mapping = []
        self.flat_mapping = []

    def register(self, pipeline):
        _log.info('Register Mapper %s in %s pipeline' % (self.__class__.__name__, pipeline.name))
        map_functions = inspect.getmembers(self, predicate=lambda func: isinstance(func, inspect.types.MethodType)
                                                                        and getattr(func, 'is_mapping', False))
        for name, map_function in map_functions:
            self.external_dependencies.extend(map_function.external_pipe)
            if map_function.type == 'reduce':
                _log.debug('Add function %s to mapper %s' % (name, self.__class__.__name__))
                for mapping_info in map_function.mapping_info:
                    self.reduce_mapping.append((map_function, mapping_info[0], mapping_info[1]))
            elif map_function.type == 'mixin':
                _log.debug('Add function %s to mapper %s' % (name, self.__class__.__name__))
                self.mixin_mapping.append((map_function, map_function.result))
            else:
                _log.info('Ignore mapping function %s in class %s with unknown type %s' % (
                    name, self.__class__.__name__, map_function.type))

    def __call__(self, df):
        """(Mapper, type(df)) -> type(new_df)
        """
        new_df = pd.DataFrame()
        if len(df) != 0:
            for map_function, result, map_columns in self.reduce_mapping:
                args = [df[column] for column in map_columns]
                new_df[result] = map(map_function,
                                     *args)
        for map_function, result in self.mixin_mapping:
            mixin_value = map_function()
            new_df[result] = mixin_value
        return new_df
