# -*- coding: utf-8 -*-
from .base_params import Params as BaseParams


class Params(BaseParams):
    _MAT_DATE_FORMAT = '%Y-%m-%dT%H:%M:%S'

    @property
    def sorts(self):
        return self['sorts']

    @sorts.setter
    def sorts(self, fields_dict):
        sorts = set()
        for field, order in fields_dict.items():
            order = str(order).lower()
            sorts.add('{} {}'.format(field, order))
        self['sorts'] = ','.join(sorts)

    @property
    def timezone(self):
        return self['timezone']

    @timezone.setter
    def timezone(self, timezone):
        self['timezone'] = str(timezone)

    @property
    def response_timezone(self):
        print (
            'WARNING! '
            'Parameter `response_timezone` was used only in API v2. '
            'Replaced by `timezone`.'
        )
        return self.timezone

    @property
    def sort(self):
        print (
            'WARNING! '
            'Parameter `sort` was used only in API v2. '
            'Replaced by `sorts`.'
        )
        return self.sorts

    @response_timezone.setter
    def response_timezone(self, response_timezone):
        print (
            'WARNING! '
            'Parameter `response_timezone` was used only in API v2. '
            'Replaced by `timezone`.'
        )
        self.timezone = response_timezone

    @sort.setter
    def sort(self, sort):
        print (
            'WARNING! '
            'Parameter `sort` was used only in API v2. '
            'Replaced by `sorts`.'
        )
        self.sorts = sort
