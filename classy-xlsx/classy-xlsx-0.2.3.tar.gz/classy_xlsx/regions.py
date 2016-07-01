# -*- coding: utf-8 -*-
from collections import OrderedDict

from .columns import XlsxColumn, XlsxColumnFabric
from .core import XlsxField, ClassyXlsxException, Bunch


class XlsxRegion(XlsxField):
    PARENT_ATTR_NAME = 'worksheet'

    def __init__(self, relative_pos=(0, 0), **kwargs):
        self.relative_pos = relative_pos
        super(XlsxRegion, self).__init__(**kwargs)
        self.worksheet = None  # injected by worksheet

    def to_xlsx(self):
        self.before_to_xls()
        self._to_xlsx()
        self.after_to_xls()

    def before_to_xls(self):
        pass

    def after_to_xls(self):
        pass

    def _to_xlsx(self):
        raise NotImplementedError()


class XlsxTable(XlsxRegion):
    # columns here
    # clicks = IntegerXlsxColumn(u'Клики', width=27)
    # etc.
    # TODO поместить все параметры в контекст  - можно будет переопределять при вызове
    table_style = None  # 'Table Style Medium 2'
    need_total = True
    total_row_format = None

    def __init__(self, **kwargs):
        super(XlsxTable, self).__init__(**kwargs)
        self.columns = OrderedDict()
        self.start_row = 0
        self.end_row = 0
        self._depended_columns = None
        self._undepended_columns = None
        self.extra_init()

    def extra_init(self):
        pass

    def remove_columns(self, *names):
        for name in names:
            try:
                del self.columns[name]
                delattr(self, name)
            except KeyError:
                raise ClassyXlsxException("No column {} in {}".format(name, self.__class__.__name__))

    def _humanize_row(self, res_row):
        if not res_row:
            return
        for name, col in self.columns.iteritems():
            val = res_row[name]
            if val is None:
                res_row[name] = '--'
            else:
                res_row[name] = col.humanize(val)

    @property
    def depended_columns(self):
        if self._depended_columns is None:
            self._depended_columns = []
            for name, col in self.columns.iteritems():
                if col.is_depended:
                    self._depended_columns.append(col)
        return self._depended_columns

    @property
    def undepended_columns(self):
        if self._undepended_columns is None:
            self._undepended_columns = []
            for name, col in self.columns.iteritems():
                if not col.is_depended:
                    self._undepended_columns.append(col)
        return self._undepended_columns

    def get_data(self, humanize=False):
        self.before_get_data()
        res = []
        for col in self.columns.values():
            col._total = 0
        for db_row in self.get_queryset():
            if isinstance(db_row, dict):
                db_row = Bunch(db_row)
            res_row = Bunch()
            for col in self.undepended_columns:
                value = col.calc_value(source_row=db_row)
                res_row[col.name] = value
                if self.need_total:
                    col.calc_total(source_row=db_row, my_value=value, )
            for col in self.depended_columns:
                value = col.calc_value(source_row=db_row, res_row=res_row)
                res_row[col.name] = value
                if self.need_total:
                    col.calc_total(source_row=db_row, my_value=value, res_row=res_row)
            if humanize:
                self._humanize_row(res_row)
            res.append(res_row)

        if self.need_total and res:
            total_row = Bunch()
            for col in self.undepended_columns:
                total_row[col.name] = col.get_total()
            for col in self.depended_columns:
                total_row[col.name] = col.get_total(res_row=total_row)
            if humanize:
                self._humanize_row(total_row)
            res.append(total_row)

        return res

    def get_queryset(self):
        raise NotImplementedError()

    def _get_format(self, obj, format_attr, extra_fmt=None):
        cell_format = getattr(obj, format_attr, {}).copy()
        if extra_fmt:
            cell_format.update(extra_fmt)
        return self.worksheet.workbook.get_format(cell_format)

    def expand_columns(self):
        self.before_expand_columns()
        self.columns = OrderedDict()
        raw_columns = XlsxColumn.copy_fields_to_instance(instance=self)
        for name, column in raw_columns.iteritems():
            if isinstance(column, XlsxColumnFabric):
                for sub_column in column.get_columns():
                    sub_column.region = self
                    self.columns[sub_column.name] = sub_column
            else:
                self.columns[name] = column

    def before_expand_columns(self):
        pass

    def _to_xlsx(self):
        self.expand_columns()
        table_data = [[row[name] for name, col in self.columns.iteritems()] for row in self.get_data()]

        total_row = None
        if table_data and self.total_row_format:
            total_row = table_data[-1]
            table_data = table_data[:-1]
        options = {'data': table_data}
        if self.table_style:
            options.update({'style': self.table_style})
        columns = []
        for name, col in self.columns.iteritems():
            fmt = self._get_format(obj=col, format_attr='cell_format')
            columns.append(dict(header=col.title, format=fmt))
        options['columns'] = columns

        row_num, col_num = self.relative_pos
        self.worksheet.row_num += row_num

        self.start_row = self.worksheet.row_num
        self.worksheet.row_num += len(table_data)
        if self.total_row_format:
            self.worksheet.row_num += 1
        self.end_row = self.worksheet.row_num
        last_col = col_num + len(columns) - 1
        self.worksheet.out_ws.add_table(
            first_row=self.start_row,
            first_col=col_num,
            last_row=self.end_row,
            last_col=last_col,
            options=options
        )
        if total_row:
            for i, name in enumerate(self.columns):
                col = self.columns[name]
                fmt = self._get_format(obj=col, format_attr='cell_format', extra_fmt=self.total_row_format)
                self.worksheet.out_ws.write(self.worksheet.row_num, col_num + i, total_row[i], fmt)

    def set_column_width(self):
        for i, name in enumerate(self.columns):
            col = self.columns[name]
            self.worksheet.out_ws.set_column(i, i, col.width)

            # # старый код - м.б. пригодидзе для автоширины колонок
            # widths = [10 for col in table['header']]
            # for row in table['rows']:
            # for i, w in enumerate(widths):
            #         val = row[i]
            #         if isinstance(val, dict):
            #             continue
            #         cell_len = len(unicode(val))
            #         if w < cell_len:
            #             widths[i] = cell_len
            # for i, w in enumerate(widths):
            #     width = (w + 1) * 256
            #     if width > 65535:
            #         width = 65535
            #     sheet.col(i).width = width
            # sheet.set_panes_frozen(True)
            # sheet.set_horz_split_pos(1)
            # sheet.set_remove_splits(True)

    def before_get_data(self):
        pass


class XlsxUnrefinedTable(XlsxTable):
    head_format = {'bold': 1}
    total_row_format = None

    def _to_xlsx(self):
        self.expand_columns()

        rel_row_num, col_num = self.relative_pos
        self.worksheet.row_num += rel_row_num
        self.start_row = self.worksheet.row_num

        head_fmt = self._get_format(obj=self, format_attr='head_format')
        for i, name in enumerate(self.columns):
            col = self.columns[name]
            self.worksheet.out_ws.write(self.start_row, col_num + i, col.title, head_fmt)
        self.worksheet.row_num += 1

        data = self.get_data()
        if self.total_row_format:
            total_row = data[-1]
            data = data[:-1]
        else:
            total_row = []

        for row in data:
            for i, name in enumerate(self.columns):
                col = self.columns[name]
                fmt = self._get_format(obj=col, format_attr='cell_format')
                self.worksheet.out_ws.write(self.worksheet.row_num, col_num + i, row[col.name], fmt)
            self.worksheet.row_num += 1
        if self.total_row_format:
            for i, name in enumerate(self.columns):
                col = self.columns[name]
                fmt = self._get_format(obj=col, format_attr='cell_format', extra_fmt=self.total_row_format)
                self.worksheet.out_ws.write(self.worksheet.row_num, col_num + i, total_row[col.name], fmt)
            self.worksheet.row_num += 1
        self.end_row = self.worksheet.row_num


class XlsxChart(XlsxRegion):
    categories_column = 'period'
    main_type = 'line'
    main_series = [
        # Bunch(column='clicks', type='line', options={'y2_axis': True, 'line': {'color': '#ED7D31'}}),
    ]
    combain_type = None
    combain_series = None

    legend = None
    # legend = Bunch(position='bottom')
    size = None
    # size = Bunch(width=1557, height=405)
    chartarea = None
    # chartarea = Bunch(border={'none': True})
    title = {
        'name': u'Some name here',
        # 'name_font': {'size': 14, 'bold': False},
    }
    offset = None
    # offset = Bunch(x_offset25, y_offset=25)

    def __init__(self, source_region_name, **kwargs):
        super(XlsxChart, self).__init__(**kwargs)
        if not isinstance(source_region_name, str):
            raise Exception("Source must be name of region!")
        self.source_region_name = source_region_name
        self.source_region = None
        self.categories = None

    def _get_chart(self, chart_type, series):
        chart = self.worksheet.workbook.out_wb.add_chart({'type': chart_type})
        for dataset in series:
            serie_column = self.source_region.columns[dataset.column]
            options = dict(
                categories=self.categories,
                values=[self.worksheet.out_ws.name, self.source_region.start_row + 1, serie_column.position,
                        self.source_region.end_row, serie_column.position],
                name=serie_column.title,
            )
            if hasattr(dataset, 'options'):
                options.update(dataset.options)
            chart.add_series(options)
        return chart

    def _to_xlsx(self):
        try:
            self.source_region = self.worksheet.regions[self.source_region_name]
        except KeyError:
            raise Exception("Can't find region {} ".format(self.source_region_name))
        category_column = self.source_region.columns[self.categories_column]
        self.categories = [
            self.worksheet.out_ws.name,
            self.source_region.start_row + 1,
            category_column.position,
            self.source_region.end_row,
            category_column.position
        ]
        main_chart = self._get_chart(chart_type=self.main_type, series=self.main_series)
        if self.combain_series:
            combain_chart = self._get_chart(chart_type=self.combain_type, series=self.combain_series)
            main_chart.combine(combain_chart)

        if self.size:
            main_chart.set_size(self.size)
        if self.chartarea:
            main_chart.set_chartarea(self.chartarea)
        if self.legend:
            main_chart.set_legend(self.legend)
        if self.title:
            main_chart.set_title(self.title)

        chart_row = self.source_region.start_row + self.relative_pos[0]
        chart_col = category_column.position + self.relative_pos[1]
        offset = getattr(self, 'offset', {})
        self.worksheet.out_ws.insert_chart(chart_row, chart_col, main_chart, offset)

