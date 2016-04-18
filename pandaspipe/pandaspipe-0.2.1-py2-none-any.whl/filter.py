# -*- coding:utf-8 -*-
import logging
import inspect
from base import PipelineEntity

_log = logging.getLogger(__name__)


def columns_condition(func=None, required_columns=()):
    def process(dec_func):
        dec_func.is_condition = True
        dec_func.type = 'columns'
        if not getattr(dec_func, 'columns_condition_info', False):
            dec_func.columns_condition_info = []
        dec_func.columns_condition_info.append(
            required_columns if len(required_columns) != 0 else dec_func.func_code.co_varnames[1:])
        return dec_func
    if func:
        return process(func)
    return process


def column_condition(func=None, target=None, direct_use=True):
    def process(dec_func):
        dec_func.is_condition = True
        dec_func.type = 'column'
        if not getattr(dec_func, 'column_condition_info', False):
            dec_func.column_condition_info = []
        dec_func.column_condition_info.append([
            target if target is not None else dec_func.func_code.co_varnames[1],
            direct_use
        ])
        return dec_func
    if func:
        return process(func)
    return process


def type_condition(func=None, target_columns=()):
    def process(dec_func):
        dec_func.is_condition = True
        dec_func.type = 'type'
        dec_func.target_columns = target_columns
        return dec_func
    if func:
        return process(func)
    return process


class Filter(PipelineEntity):

    def __init__(self):
        super(Filter, self).__init__()
        self.priority = 10
        self.columns_conditions = []
        self.column_conditions = []
        self.type_conditions = []

    def register(self, pipeline):
        _log.info('Register Filter %s in %s pipeline' % (self.__class__.__name__, pipeline.name))
        map_functions = inspect.getmembers(self, predicate=lambda func: isinstance(func, inspect.types.MethodType)
                                                                        and getattr(func, 'is_condition', False))
        for name, condition_function in map_functions:
            if condition_function.type == 'columns':
                _log.debug('Add function %s to Filter %s' % (name, self.__class__.__name__))
                for required_columns in condition_function.columns_condition_info:
                    self.columns_conditions.append((condition_function, required_columns))
            elif condition_function.type == 'column':
                _log.debug('Add function %s to Filter %s' % (name, self.__class__.__name__))
                for target, direct_use in condition_function.column_condition_info:
                    self.column_conditions.append((condition_function, target, direct_use))
            elif condition_function.type == 'type':
                self.type_conditions.append(condition_function)
                _log.debug('Add function %s to Filter %s' % (name, self.__class__.__name__))
            else:
                _log.info('Ignore condition function %s in class %s with unknown type %s' % (
                    name, self.__class__.__name__, condition_function.type))

    def __call__(self, df):
        columns = df.columns.tolist()
        if len(df) == 0:
            return df
        for condition_function in self.type_conditions:
            target_columns = condition_function.target_columns
            if len(target_columns) == 0:
                target_columns = columns
            for target_column in target_columns:
                if not condition_function(df.dtypes[target_column]):
                    df = df.drop(target_column, axis=1)
        for condition_function, target, direct_use in self.column_conditions:
            if direct_use:
                df = df[condition_function(df[target])]
            else:
                new_index = filter(lambda i: i is not None,
                               map(lambda i, *args: i if condition_function(*args) else None, df.index, df[target]))
                df = df.loc[new_index]
        for condition_function, condition_columns in self.columns_conditions:
            new_index = filter(lambda i: i is not None,
                               map(lambda i, *args: i if condition_function(*args) else None, df.index,
                                   *[df[column] for column in columns if
                                     column in condition_columns]))
            df = df.iloc[new_index]
        return df


class NumberFilter(Filter):

    @type_condition
    def number_condition(self, type):
        return type in ['float', 'float64', 'int', 'int64']
