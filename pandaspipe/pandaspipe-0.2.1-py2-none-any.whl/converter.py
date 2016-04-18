# -*- coding:utf-8 -*-
import inspect
import logging
from base import PipelineEntity

_log = logging.getLogger(__name__)


def converter(func=None, target=None):
    def process(dec_func):
        dec_func.is_converter = True
        dec_func.type = 'column'
        if not getattr(dec_func, 'column_converter_info', False):
            dec_func.column_converter_info = []
        dec_func.column_converter_info.append(
            target if target is not None else dec_func.__name__
        )
        return dec_func
    if func:
        return process(func)
    return process


class Converter(PipelineEntity):
    """
    Pipeline entity, that used to convert data in dataframe
    Can convert only one series with one method
    """

    def __init__(self):
        super(Converter, self).__init__()
        self.priority = 6
        self.column_converters = []

    def register(self, pipeline):
        _log.info('Register Converter %s in %s pipeline' % (self.__class__.__name__, pipeline.name))
        map_functions = inspect.getmembers(self, predicate=lambda func: isinstance(func, inspect.types.MethodType)
                                                                        and getattr(func, 'is_converter', False))
        for name, condition_function in map_functions:
            if condition_function.type == 'column':
                _log.debug('Add function %s to Converter %s' % (name, self.__class__.__name__))
                for target in condition_function.column_converter_info:
                    self.column_converters.append((condition_function, target))
            else:
                _log.info('Ignore converter function %s in class %s with unknown type %s' % (
                    name, self.__class__.__name__, condition_function.type))

    def __call__(self, df):
        """(Mapper, type(df)) -> type(new_df)
        """
        if len(df) == 0:
            return df
        for convert_function, target in self.column_converters:
            if target in df.columns:
                df[target] = df[target].apply(convert_function)
        return df

