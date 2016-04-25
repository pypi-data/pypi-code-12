# -*- coding: utf-8 -*-
"""easyxlsx.excel."""

import io
import datetime

import xlsxwriter


class Dict2Object(object):
    """Dict to object."""

    def __init__(self, **entries):
        self.__dict__.update(entries)


class BaseExport(object):
    """
    :功能描述: Export基类
    """
    header_font_size = 12
    body_font_size = 12
    datetime_style = 'yyyy-m-d hh:mm:ss'
    date_style = 'yyyy-m-d'
    rows_index = 0

    def __init__(self, sources, bookname=None, footer_data=None):
        self.output = io.BytesIO()
        self.bookname = bookname if bookname else 'excel.xls'
        self.sources = sources
        self.footer_data = footer_data
        self.book = xlsxwriter.Workbook(self.output)
        self.fmt_datetime = self.book.add_format(
            {'num_format': self.datetime_style})
        self.fmt_date = self.book.add_format(
            {'num_format': self.date_style})
        self.bodyfmt = self.book.add_format({'font_size': self.body_font_size})
        self.headerfmt = self.book.add_format(
            {'font_size': self.header_font_size})
        self.headerfmt.set_bold()

    def export_book(self):
        """Export book."""
        for source in self.sources:
            sheet = self.book.add_worksheet(source['name'])
            self.rows_index = 0
            self.write_header(sheet)
            self.write_dataset(sheet, source['dataset'], self.bodyfmt)
            if hasattr(self, 'write_footer'):
                self.write_footer(sheet, source['footer_data'])

        return self.close()

    def export(self, sheet_name=None):
        bodyfmt = self.book.add_format({'font_size': self.body_font_size})

        sheet = self.book.add_worksheet(sheet_name)
        self.write_header(sheet)
        self.write_dataset(sheet, self.sources, bodyfmt)
        if hasattr(self, 'write_footer'):
            self.write_footer(sheet, self.footer_data)
        return self.close()

    def write_header(self, sheet, headerfmt):
        headers = [self.headers[key] for key in self.Meta.fields]
        if hasattr(self.Meta, 'extra_fields'):
            func_name = getattr(self.Meta, 'func_name')
            extra_fields = self.Meta.extra_fields[func_name]
            extra = [self.headers[key] for key in extra_fields]
            headers.extend(extra)

        for index, value in enumerate(headers):
            sheet.write(self.rows_index, index, value, headerfmt)
        self.rows_index += 1

    def close(self):
        self.book.close()
        self.output.seek(0)
        iodata = self.output.read()
        self.output.close()
        return iodata

    def write_dataset(self, sheet, dataset, bodyfmt):
        for row, data in enumerate(dataset):
            for col, field in enumerate(self.Meta.fields):
                if '.' in field:
                    name, related_name = field.split('.')
                    obj = getattr(data, name)
                    value = getattr(obj, related_name)
                else:
                    value = getattr(data, field)
                sheet.write(self.rows_index, col, value, bodyfmt)
            self.rows_index += 1


class ModelExport(BaseExport):
    """
    :功能描述: ModelExport 根据 model导出
    :开发责任人: mzj@abstack.com
    :最后修改时间: 2015-06-10 19:50:02
    :评审责任人: mzj@abstack.com
    :最后评审时间: 2015-06-10 19:50:05
    """

    def write_header(self, sheet):
        model = self.Meta.model
        has_headers = hasattr(self, 'headers')

        for col, field in enumerate(self.Meta.fields):
            if has_headers and field in self.headers:
                value = self.headers[field]
            else:
                value = model._meta.get_field(field).verbose_name.title()
            sheet.write(self.rows_index, col, value, self.headerfmt)
        self.rows_index += 1

    def get_fmt(self, value):
        if isinstance(value, datetime.datetime):
            return self.fmt_datetime
        else:
            return self.bodyfmt

    def write_dataset(self, sheet, dataset, bodyfmt):
        for row, obj in enumerate(dataset):
            self.move_rows = None
            for col, field in enumerate(self.Meta.fields):

                if hasattr(self, field):
                    value = getattr(self, field)(obj)
                    sheet.write(self.rows_index, col, value,
                                self.get_fmt(value))
                else:
                    self.write_data(sheet, col, obj, field)

            self.rows_index += self.move_rows if self.move_rows else 1

    def write_data(self, sheet, col, obj, field):
        if '.' in field:
            o, related_name = field.split('.')
            o = getattr(obj, o)
            value = getattr(o, related_name)

            sheet.write(self.rows_index, col, value,
                        self.get_fmt(value))
        elif hasattr(self, field):
            value = getattr(self, field)()
            sheet.write(self.rows_index, col, value, self.get_fmt(value))
        else:
            value = getattr(obj, field)
            if isinstance(value, datetime.datetime):
                value = value.replace(tzinfo=None)
            if (hasattr(self, 'fields_choices')
                and field in self.fields_choices):
                value = self.fields_choices[field][value]
            sheet.write(self.rows_index, col, value, self.get_fmt(value))
