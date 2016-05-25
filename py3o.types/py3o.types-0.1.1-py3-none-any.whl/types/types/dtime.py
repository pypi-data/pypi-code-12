# -*- encoding: utf-8 -*-

from datetime import datetime
from py3o.types.types import Py3oTypeMixin


class Py3oDatetime(datetime, Py3oTypeMixin):

    datetime_format = None

    @classmethod
    def get_config_attributes(cls, config):
        res = super(Py3oDatetime, cls).get_config_attributes(config)
        if 'datetime_format' in config:
            res['datetime_format'] = config['datetime_format']
        elif 'date_format' in config and 'time_format' in config:
            res['datetime_format'] = '{date} {time}'.format(
                date=config['date_format'], time=config['time_format']
            )
        return res

    def __str__(self):
        res = super(Py3oDatetime, self).__str__()
        if self.datetime_format:
            res = self.strftime(self.datetime_format)
        return res

    @property
    def odt_value(self):  # pragma: no cover
        raise NotImplementedError

    @classmethod
    def strptime(cls, date_string, format):
        return super(Py3oDatetime, cls).strptime(date_string, format)
