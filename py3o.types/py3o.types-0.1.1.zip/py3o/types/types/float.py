# -*- encoding: utf-8 -*-

from py3o.types.types import Py3oTypeMixin


class Py3oFloat(float, Py3oTypeMixin):

    digit_separator = None
    digit_format = 3
    decimal_separator = '.'

    @classmethod
    def get_config_attributes(cls, config):
        res = super(Py3oFloat, cls).get_config_attributes(config)
        if 'digit_separator' in config:
            res['digit_separator'] = config['digit_separator']
        digit_format = config.get('digit_format', None)
        if digit_format is not None:
            res['digit_format'] = int(digit_format)
        if 'decimal_separator' in config:
            res['decimal_separator'] = config['decimal_separator']
        return res

    def __str__(self):

        res = super(Py3oFloat, self).__str__()
        integer, decimal = res.split('.')

        if self.digit_separator is not None:
            integer = self.digit_separator.join(reversed([
                integer[max(x - self.digit_format, 0):x]
                for x in range(len(integer), 0, -self.digit_format)
            ]))

        return self.decimal_separator.join((integer, decimal))

    @property
    def odt_value(self):
        return float(self)
