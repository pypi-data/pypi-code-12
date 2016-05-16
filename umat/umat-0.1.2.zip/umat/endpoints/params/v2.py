# -*- coding: utf-8 -*-
from base_params import Params as BaseParams


class Params(BaseParams):
    _MAT_DATE_FORMAT = '%Y-%m-%d %H:%M:%S'

    @property
    def group(self):
        return self['group']

    @property
    def response_timezone(self):
        return self['response_timezone']

    @property
    def sort(self):
        return self['sort']

    @group.setter
    def group(self, fields):
        self['group'] = ','.join(map(str, fields))

    @response_timezone.setter
    def response_timezone(self, response_timezone):
        self['response_timezone'] = str(response_timezone)

    @sort.setter
    def sort(self, fields_dict):
        fields_dict = {str(k): str(v) for k, v in fields_dict.items()}
        self['sort'] = fields_dict

    @property
    def sorts(self):
        print (
            'WARNING! '
            'Parameter `sorts` appeared only in API v3. '
            'Replaced by `sort`.'
        )
        return self.sort

    @property
    def timezone(self):
        print (
            'WARNING! '
            'Parameter `timezone` appeared only in API v3. '
            'Replaced by `response_timezone`.'
        )
        return self.response_timezone

    @sorts.setter
    def sorts(self, sorts):
        print (
            'WARNING! '
            'Parameter `sorts` appeared only in API v3. '
            'Replaced by `sort`.'
        )
        self.sort = sorts

    @timezone.setter
    def timezone(self, timezone):
        print (
            'WARNING! '
            'Parameter `timezone` appeared only in API v3. '
            'Replaced by `response_timezone`.'
        )
        self.response_timezone = timezone
