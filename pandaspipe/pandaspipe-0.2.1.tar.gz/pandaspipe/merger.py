# -*- coding:utf-8 -*-
import inspect
import logging
import pandas as pd
from base import PipelineEntity
_log = logging.getLogger(__name__)


def simple_merger(func):
    func.is_merger = True
    func.type = 'simple'
    return func


def merger(func=None, required_channels=None, output_channels=None):
    def process(dec_func):
        dec_func.is_merger = True
        dec_func.type = 'normal'
        dec_func.required_channels = required_channels if required_channels else dec_func.func_code.co_varnames[1:]
        dec_func.output_channels = output_channels if output_channels else [dec_func.__name__]
        return dec_func

    if func:
        return process(func)
    return process


class Merger(PipelineEntity):

    def __init__(self):
        super(Merger, self).__init__()
        self.type = 'bignode'
        self.priority = 10
        self._mergers = []
        self._simple_merger = None

    def __call__(self, *dfs):
        df_map = {}
        new_df_map = {}
        for i in xrange(0, len(self.input_channels)):
            df_map[self.input_channels[i]] = dfs[i]
        for merger_function, required_channels, output_channels in self._mergers:
            result = merger_function(*[df_map.pop(required_channel) for required_channel in required_channels])
            if not isinstance(result, list):
                result = [result]
            for i in xrange(0, len(result)):
                new_df_map[output_channels[i]] = result[i]
        rest_channels = df_map.keys()
        if len(rest_channels) != 0 and self._simple_merger:
            output_simple_channel = filter(lambda output_channel: len(
                filter(lambda merger_tuple: output_channel in merger_tuple[2], self._mergers)) == 0,
                                           self.output_channels)[0]
            new_df_map[output_simple_channel] = self._simple_merger(*df_map.values())
        return new_df_map

    def register(self, pipeline):
        _log.info('Register Mapper %s in %s pipeline' % (self.__class__.__name__, pipeline.name))
        merge_functions = inspect.getmembers(self, predicate=lambda func: isinstance(func, inspect.types.MethodType)
                                                                          and getattr(func, 'is_merger', False))
        for name, merge_function in merge_functions:
            if merge_function.type == 'simple':
                if self._simple_merger:
                    raise Exception('Merger %s has to many simple mergers' % self.__class__.__name__)
                _log.debug('Add %s simple merger to Merger %s' % (merge_function.__name__, self.__class__.__name__))
                self._simple_merger = merge_function
            elif merge_function.type == 'normal':
                _log.debug('Add %s merger to Merger %s' % (merge_function.__name__, self.__class__.__name__))
                self._mergers.append((merge_function, merge_function.required_channels, merge_function.output_channels))
                self.input_channels.extend(merge_function.required_channels)
                self.output_channels.extend(merge_function.output_channels)


class SimpleMerger(Merger):
    @simple_merger
    def merge(self, *dfs):
        return pd.concat(dfs, axis=1)
