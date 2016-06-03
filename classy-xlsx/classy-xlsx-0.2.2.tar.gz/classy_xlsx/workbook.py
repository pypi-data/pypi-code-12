# -*- coding: utf-8 -*-
from collections import OrderedDict
from shutil import rmtree

import xlsxwriter

from classy_xlsx.core import XlsxContext
from .worksheet import XlsxSheetFabric, OneRegionXlsxSheet, XlsxSheet


class XlsxWorkbook(XlsxContext):
    file_name = '/tmp/workbook.xlsx'

    def __init__(self, context=None, file_name=None):
        super(XlsxWorkbook, self).__init__(context=context)
        if file_name:
            self.file_name = file_name
        self.sheets = []
        self._dest_file = self.get_filename()
        self.out_wb = xlsxwriter.Workbook(self._dest_file)
        self.formats = {}
        self.tmp_dir = None

        raw_sheets = XlsxSheet.copy_fields_to_instance(instance=self)
        self.sheets = OrderedDict()
        for name, sheet in raw_sheets.iteritems():
            if isinstance(sheet, XlsxSheetFabric):
                i = 0
                for sub_sheet in sheet.get_sheets():
                    # TODO имя можно вынести в фабрику
                    sub_sheet_name = '{}_{}'.format(name, i)
                    sub_sheet.workbook = self
                    sub_sheet.name = sub_sheet_name
                    self.sheets[sub_sheet_name] = sub_sheet
                    i += 1
            else:
                self.sheets[name] = sheet

    def get_format(self, fmt):
        key = repr(fmt)
        if key not in self.formats:
            self.formats[key] = self.out_wb.add_format(fmt)
        return self.formats[key]

    def get_filename(self):
        return self.file_name

    def get_result_ws(self, sheet_name):
        sheet_name = self._refine_sheet_name(sheet_name)
        for ws in self.out_wb.worksheets():
            ws_name = ws.get_name()
            if ws_name == sheet_name:
                break
        else:
            ws = self.out_wb.add_worksheet(sheet_name)
        return ws

    def make_report(self, context=None, file_name=None):
        if context:
            self._context = context
        if file_name:
            self.file_name = file_name
        self.before_make_report()
        sheets_by_priority = []
        for sheet in self.sheets.values():
            if sheet.fill_priority:
                sheet.prepare_to_xlsx()
                sheets_by_priority.append(sheet)
            else:
                sheet.to_xlsx()
        sheets_by_priority.sort(key=lambda x: x.fill_priority)
        for sheet in sheets_by_priority:
            sheet.to_xlsx()
        self.save()
        self.after_make_report()
        return self._dest_file

    def save(self):
        self.out_wb.close()
        if self.tmp_dir:
            rmtree(self.tmp_dir)
            self.tmp_dir = None

    def before_make_report(self):
        pass

    def after_make_report(self):
        pass

    def _refine_sheet_name(self, sheet_name):
        res = u''
        for char in sheet_name:
            if char in ('[', ']'):
                res += '_'
            else:
                res += char
        return res


class OneTableXlsxWorkbook(XlsxWorkbook):
    region_class = None
    list_name = 'list1'

    def __init__(self, **kwargs):
        if 'region_class' in kwargs:
            self.region_class = kwargs['region_class']
            del kwargs['region_class']
        elif not self.region_class:
            raise Exception('OneTableXlsxWorkbook need region_class as attribute or in kwargs!')
        sheet = OneRegionXlsxSheet(region_class=self.region_class)
        setattr(self.__class__, self.list_name, sheet)
        super(OneTableXlsxWorkbook, self).__init__(**kwargs)
