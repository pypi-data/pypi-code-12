# -*- encoding: utf-8 -*-

import datetime
from py3o.types.types import Py3oTypeMixin


class Py3oDate(datetime.date, Py3oTypeMixin):

    date_format = None

    @classmethod
    def get_config_attributes(cls, config):
        res = super(Py3oDate, cls).get_config_attributes(config)
        if 'date_format' in config:
            res['date_format'] = config['date_format']
        return res

    def __str__(self):
        res = super(Py3oDate, self).__str__()
        if self.date_format:
            res = self.strftime(self.date_format)
        return res

    def odt_value(self):  # pragma: no cover
        raise NotImplementedError

    @classmethod
    def strptime(cls, date_string, format):
        dt = datetime.datetime.strptime(date_string, format)
        return cls(dt.year, dt.month, dt.day)
