# -*- encoding: utf-8 -*-

import datetime
from py3o.types.types import Py3oTypeMixin


class Py3oTime(datetime.time, Py3oTypeMixin):

    time_format = None

    @classmethod
    def get_config_attributes(cls, config):
        res = super(Py3oTime, cls).get_config_attributes(config)
        if 'time_format' in config:
            res['time_format'] = config['time_format']
        return res

    def __str__(self):
        res = super(Py3oTime, self).__str__()
        if self.time_format:
            res = self.strftime(self.time_format)
        return res

    @property
    def odt_value(self):  # pragma: no cover
        raise NotImplementedError

    @classmethod
    def strptime(cls, date_string, format):
        dt = datetime.datetime.strptime(date_string, format)
        return cls(dt.hour, dt.minute, dt.second, dt.microsecond, dt.tzinfo)
