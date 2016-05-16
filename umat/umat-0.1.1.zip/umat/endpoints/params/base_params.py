# -*- coding: utf-8 -*-
from datetime import date
from .date import (
    dt_max,
    dt_min,
    from_string
)


class Params(dict):
    def __init__(self, api_key, *args, **kwargs):
        super(Params, self).__init__(*args, **kwargs)
        self['api_key'] = api_key

    @property
    def start_date(self):
        return self.get('start_date')

    @property
    def end_date(self):
        return self.get('end_date')

    @property
    def fields(self):
        return self.get('fields')

    @start_date.setter
    def start_date(self, start_date):
        if isinstance(start_date, (str, unicode)):
            start_date = from_string(str(start_date))
        if type(start_date) == date:
            start_date = dt_min(start_date)
        self['start_date'] = start_date.strftime(self._MAT_DATE_FORMAT)

    @end_date.setter
    def end_date(self, end_date):
        if isinstance(end_date, (str, unicode)):
            end_date = from_string(str(end_date))
        if type(end_date) == date:
            end_date = dt_max(end_date)
        self['end_date'] = end_date.strftime(self._MAT_DATE_FORMAT)

    @fields.setter
    def fields(self, fields):
        self['fields'] = ','.join(map(str, fields))
