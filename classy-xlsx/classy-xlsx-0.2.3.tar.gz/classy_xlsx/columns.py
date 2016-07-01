# -*- coding: utf-8 -*-

from .core import XlsxField, Bunch


class XlsxColumn(XlsxField):
    _dependent = False
    PARENT_ATTR_NAME = 'region'
    quiet = False

    def __init__(self, title='', width=10, quiet=None, **kwargs):
        self.title = title
        self.width = width
        self.quiet = quiet if quiet is not None else self.__class__.quiet
        super(XlsxColumn, self).__init__(**kwargs)
        self.region = None  # injected by region
        self._kwargs = Bunch(kwargs)
        self._total = 0

    @property
    def is_depended(self):
        return self._dependent

    def calc_value(self, source_row, res_row=None):
        val = source_row
        for name in self.name.split('__'):
            try:
                val = getattr(val, name, None)
                # if val.__class__.__name__ == 'RelatedManager':
                # val = val.first()
                # elif callable(val):
                #     val = val()
            except:
                if self.quiet:
                    return ''
                raise
        return val

    def calc_total(self, source_row, my_value, res_row=None):
        if my_value is not None:
            self._total += my_value

    def get_total(self, res_row=None):
        return self._total

    def __repr__(self):
        return self.name

    def humanize(self, value):
        return value

    def get_html_type(self):
        return 'text'


class FloatXlsxColumn(XlsxColumn):
    precision = 2
    cell_format = {'num_format': '# ##0.00'}

    def humanize(self, value):
        return round(float(value), self.precision)

    def get_html_type(self):
        return 'number'


class IntegerXlsxColumn(FloatXlsxColumn):
    precision = 0
    cell_format = {'num_format': '# ##0'}

    def humanize(self, value):
        return int(value)


class PercentXlsxColumn(FloatXlsxColumn):
    precision = 2
    cell_format = {'num_format': '0.00%'}

    def humanize(self, value):
        return round(float(value) * 100, self.precision)


class TextXlsxColumn(XlsxColumn):
    def calc_total(self, source_row, my_value, res_row=None):
        pass

    def get_total(self, res_row=None):
        return u''


class RatioColumn(XlsxColumn):
    dividend = 'redefine_me'  # делимое
    divisor = 'redefine_me'  # делитель
    _dependent = True

    def _get_value(self, res_row):
        if not res_row:
            return 0
        try:
            dividend = getattr(res_row, self.dividend)
            divisor = getattr(res_row, self.divisor)
        except AttributeError:
            return 0
        if divisor:
            return float(dividend) / float(divisor)
        return 0

    def calc_value(self, source_row, res_row=None):
        return self._get_value(res_row)

    def get_total(self, res_row=None):
        return self._get_value(res_row)


class WeightedAverageColumn(XlsxColumn):
    divisor = 'redefine_me'
    _dependent = True
    _total = 0  # PyCharm dummy

    def calc_total(self, source_row, my_value, res_row=None):
        if not res_row:
            return 0
        if my_value is None:
            return 0
        try:
            divisor = getattr(res_row, self.divisor)
        except AttributeError:
            return 0
        if divisor:
            self._total += float(my_value) * divisor

    def get_total(self, res_row=None):
        if not res_row:
            return 0
        try:
            divisor = getattr(res_row, self.divisor)
        except AttributeError:
            return 0
        if divisor:
            return self._total / float(divisor)
        return 0


class DateXlsxColumn(TextXlsxColumn):
    DATE_FORMAT = '%d.%m.%Y'

    def calc_value(self, source_row, res_row=None):
        value = super(DateXlsxColumn, self).calc_value(source_row, res_row)
        if value:
            return value.strftime(self.DATE_FORMAT)
        return value


class DateTimeXlsxColumn(DateXlsxColumn):
    DATE_FORMAT = '%d.%m.%Y %H:%M:%S'


class UnicodeXlsxColumn(TextXlsxColumn):
    def calc_value(self, source_row, res_row=None):
        value = super(UnicodeXlsxColumn, self).calc_value(source_row, res_row)
        return unicode(value)


class XlsxColumnFabric(XlsxColumn):
    def get_columns(self):
        raise NotImplementedError()
