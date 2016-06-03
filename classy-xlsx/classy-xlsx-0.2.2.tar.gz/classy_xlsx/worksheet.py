# -*- coding: utf-8 -*-

from .core import XlsxField
from .regions import XlsxRegion


class XlsxSheet(XlsxField):
    # regions here
    # top_table = XlsxTable()
    # pretty_table = OtherXlsxTable()
    # pretty_chart = XlsxChart()
    # etc.

    PARENT_ATTR_NAME = 'workbook'
    columns_width_region = None
    fill_priority = None

    def __init__(self, **kwargs):
        super(XlsxSheet, self).__init__(**kwargs)
        self.workbook = None  # injected by workbook
        self.regions = XlsxRegion.copy_fields_to_instance(instance=self)
        self.row_num = 0
        self.out_ws = None

    def get_name(self):
        return self.name

    def to_xlsx(self):
        self.row_num = 0
        self.prepare_to_xlsx()
        self.before_to_xlsx()
        for i, name in enumerate(self.regions):
            region = self.regions[name]
            region.to_xlsx()
            if name == self.columns_width_region or i == 0:
                region.set_column_width()
        self.after_to_xlsx()

    def prepare_to_xlsx(self):
        if not self.out_ws:
            sheet_name = self.get_name()
            self.out_ws = self.workbook.get_result_ws(sheet_name=sheet_name)

    def before_to_xlsx(self):
        pass

    def after_to_xlsx(self):
        pass


class XlsxSheetFabric(XlsxSheet):
    def get_sheets(self):
        raise NotImplementedError()


class OneRegionXlsxSheet(XlsxSheet):
    region_class = None
    autoadded_region = None

    def __init__(self, **kwargs):
        if 'region_class' in kwargs:
            self.region_class = kwargs['region_class']
            del kwargs['region_class']
        elif not self.region_class:
            raise Exception('OneRegionXlsxSheet need region_class as attribute or in kwargs!')
        self.__class__.autoadded_region = self.region_class(**kwargs)
        super(OneRegionXlsxSheet, self).__init__(**kwargs)
