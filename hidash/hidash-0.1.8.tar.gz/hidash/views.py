import xml.etree.ElementTree as ET
import json
import copy
import xlwt
import datetime

from django.contrib.auth.decorators import user_passes_test
from django.shortcuts import render
from django.db import connections
from decimal import Decimal
from django.http import HttpResponse
from django.conf import settings
from operator import indexOf
from datetime import date

try:
    from collections import OrderedDict
except ImportError:
    from ordereddict import OrderedDict


def authenticate_url(user):
    if 'api_authenticator' in settings.HIDASH_SETTINGS:
        return settings.HIDASH_SETTINGS['api_authenticator'](user)
    else:
        return True


def group_reports_as_json(request):
    group_id = request.GET.get('group', 'default')
    params = _augment_params(request)
    charts = _load_charts()
    data = []
    for chart_id, chart in charts.iteritems():
        if chart.group == group_id:
            if check_permissions(chart, request) and check_groups(chart, request):
                chartdata = {}
                handler = _handler_selector(chart)
                chartdata['chart_data'] = handler(chart,
                                                  chart.query,
                                                  params)
                chartdata['chart_id'] = chart_id
                chartdata['handler_type'] = chart.lib
                data.append(chartdata)
    return data


@user_passes_test(authenticate_url)
def dispatch_group_reports_as_json(request):
    data = group_reports_as_json(request)
    return HttpResponse(content=json.dumps(data), content_type="application/json")


@user_passes_test(authenticate_url)
def dispatch_group_reports(request):
    data = group_reports_as_json(request)
    return render(request, 'reports.html', {'data': data})


@user_passes_test(authenticate_url)
def dispatch_xls(request, chart_id):
    '''
    Function to render reports in spreadsheet format available for download
    '''
    chart_id = chart_id.split('.')[0]
    params = _augment_params(request)
    wb = xlwt.Workbook()
    ws = wb.add_sheet(chart_id)
    font_style = xlwt.easyxf('font: name Times New Roman, color-index green, bold on;align: wrap on', num_format_str='#,##0.00')
    charts = _load_charts()
    for key, chart in charts.iteritems():
        if key == chart_id:
            if check_permissions(chart, request) and check_groups(chart, request):
                cols = []
                cols.append(chart.dimension.asdict())
                cols.extend(map(lambda c: c.asdict(), chart.metrics))
                for col in cols:
                    ws.col(indexOf(cols, col)).width = int(13 * 260)

                with connections[chart.database].cursor() as cursor:
                    cursor.execute(chart.query, params)
                    for desc in cursor.description:
                        ws.write(0, indexOf(cursor.description, desc), desc[0], font_style)

                    for db_row in cursor:
                        for col_index, chart_col in enumerate(cols):
                            value = db_row[col_index]
                            value = _convert_to_type(value, chart_col['type'])
                            ws.write(indexOf(cursor, db_row) + 1, col_index, value)
                response = HttpResponse(content_type='application/vnd.ms-excel')
                response['Content-Disposition'] = 'attachment; filename=Report.xls'
                wb.save(response)
                return response
            else:
                return HttpResponse("User Not Authorized", status=401)


def check_groups(chart, request):
    user_groups = []
    for group in request.user.groups.all():
        user_groups.append(group.name)
    for group_name in chart.groups_list:
        if group_name not in user_groups:
            return False
    return True


def check_permissions(chart, request):
    for permission in chart.permissions_list:
        if not request.user.has_perm(permission):
            return False
    return True


def _handler_selector(chart):
    if chart.lib == "googlechart":
        handler = globals()['multiple_series_row']
        if chart.chart_type == "MapChart":
            handler = globals()['google_map_chart']
        elif chart.separator is None:
            handler = globals()['report']
            if chart.dimension.id == "extract":
                handler = globals()['col_to_series_handler']
            elif len(chart.metrics) >= 1:
                handler = globals()['default_handler']
    elif chart.lib == "highcharts":
        handler = globals()['multiple_series_row_highcharts_handler']
        if chart.separator is None:
            if chart.dimension.id == "extract":
                    handler = globals()['col_to_series_highcharts_handler']
            elif len(chart.metrics) == 1:
                handler = globals()['single_series_highcharts_handler']
            elif len(chart.metrics) >= 1:
                handler = globals()['multiple_series_column_highcharts_handler']
    return handler


@user_passes_test(authenticate_url)
def dispatch_chart(request, chart_id):
    """
    This view renders the chart data in desirable format to the controller
    """
    chart_id = chart_id.split('.')[0]
    params = _augment_params(request)
    charts = _load_charts()
    for key, chart in charts.iteritems():
        if key == chart_id:
            if check_permissions(chart, request) and check_groups(chart, request):
                handler = _handler_selector(chart)
                data = handler(chart, chart.query, params)
                return HttpResponse(content=json.dumps(data), content_type="application/json")
            else:
                return HttpResponse("User Not Authorized", status=401)


@user_passes_test(authenticate_url)
def index(request):
    return render(request, 'index.html')


def report(chart, query, params=None):
    data = {}
    data['rows'] = rows = []
    data['cols'] = cols = []
    data['chart_type'] = 'Table'
    with connections[chart.database].cursor() as cursor:
        cursor.execute(chart.query, params)
        for desc in cursor.description:
            cols.append({'type': 'string', 'label': desc[0]})
        for db_row in cursor:
            row_list = []
            for col_index, chart_col in enumerate(cols):
                value = db_row[col_index]
                temp = {"v": str(value)}
                row_list.append(temp)
            rows.append({"c": row_list})
    return data


def google_map_chart(chart, query, params=None):
    data = {}
    data['rows'] = rows = []
    data['cols'] = cols = []
    with connections[chart.database].cursor() as cursor:
        cursor.execute(chart.query, params)
        for desc in cursor.description:
            if indexOf(cursor.description, desc) < 2:
                field_type = 'number'
            else:
                field_type = 'string'
            cols.append({'type': field_type, 'label': desc[0]})
        for db_row in cursor:
            row_list = []
            for col_index, chart_col in enumerate(cols):
                value = db_row[col_index]
                temp = {"v": str(value)}
                row_list.append(temp)
            rows.append({"c": row_list})
    return data


def multiple_series_row(chart, query, params=None):

    """
    Handles the multiple series data when the series name are
    to be extracted from the rows of query set
    """
    data = {}
    data['cols'] = cols = []
    data['rows'] = rows = []
    data['chart_type'] = chart.chart_type
    with connections[chart.database].cursor() as cursor:
        cursor.execute(chart.query, params)

        dimension_values = []
        separator_values = []
        temp_val = []
        for db_row in cursor:

            if db_row[0] not in dimension_values:
                dimension_values.append(db_row[0])
                rows.append({"c": [{"v":  _convert_to_type(db_row[0], chart.dimension.type)}]})
            if db_row[1] not in separator_values:
                separator_values.append(db_row[1])
                temp_val.append({"v": _fill_missing_values(chart.metrics[0].type)})

        for row in rows:
            row['c'].extend(copy.deepcopy(temp_val))

        for db_row in cursor:
            for row in rows:
                if row['c'][0]['v'] == _convert_to_type(db_row[0], chart.dimension.type):
                    index = 1 + separator_values.index(db_row[1])
                    rows[indexOf(rows, row)]['c'][index]['v'] = _convert_to_type(db_row[2], chart.metrics[0].type)

        cols.append(chart.dimension.asdict())
        for series in separator_values:
            cols.append({"id": series, "type": chart.metrics[0].type, "label": series})

    return data


def default_handler(chart, query, params=None):
    data = {}
    data['rows'] = rows = []
    data['cols'] = cols = []
    cols.append(chart.dimension.asdict())
    cols.extend(map(lambda c: c.asdict(), chart.metrics))
    data['chart_type'] = chart.chart_type
    with connections[chart.database].cursor() as cursor:

        cursor.execute(chart.query, params)
        for db_row in cursor:

            row_list = []
            for col_index, chart_col in enumerate(cols):
                row_list.append({"v": _convert_to_type(db_row[col_index], chart_col['type'])})
            rows.append({"c": row_list})
    return data


def single_series_highcharts_handler(chart, query, params=None):
    data = {'data': []}
    cols = []
    cols.append(chart.dimension.asdict())
    cols.extend(map(lambda c: c.asdict(), chart.metrics))
    with connections[chart.database].cursor() as cursor:

        cursor.execute(chart.query, params)
        for db_row in cursor:

            row_list = []
            for col_index, chart_col in enumerate(cols):
                row_list.append(_convert_to_type(db_row[col_index], chart_col['type']))
            data['data'].append(row_list)
    data['name'] = cols[1]['label']
    return [data]


def col_to_series_highcharts_handler(chart, query, params=None):
    data = []
    with connections[chart.database].cursor() as cursor:
        cursor.execute(chart.query, params)
        for db_row in cursor:
            temp = {'data': [], 'name': str(db_row[0])}
            for col_name in cursor.description:
                if indexOf(cursor.description, col_name) != 0:
                    temp_list = []
                    temp_list.append(col_name[0])
                    temp_list.append(db_row[indexOf(cursor.description,
                                                    col_name)])
                    temp['data'].append(temp_list)
            data.append(temp)

    return data


def col_to_series_handler(chart, query, params=None):
    data = {}
    data['cols'] = cols = []
    data['chart_type'] = chart.chart_type
    with connections[chart.database].cursor() as cursor:
        cursor.execute(chart.query, params)
        rows = [None] * (len(cursor.description) - 1)
        for i in range(0, len(rows)):
            temp = {"c": []}
            rows[i] = temp
        for index, desc in enumerate(cursor.description):
            if index == 0:
                cols.append({'type': 'string', 'label': desc[0]})
            else:
                rows[index-1]["c"].append({"v": desc[0]})

        for db_row in cursor:
            for index, val in enumerate(db_row):
                if index == 0:
                    cols.append({'type': 'number', 'label': val})
                else:
                    rows[index-1]["c"].append({"v": val})

        data['rows'] = rows
        return data


def multiple_series_column_highcharts_handler(chart, query, params=None):
    """
    Handles the multiple series chart when the table has series names in
    the columns
    """
    data = []
    cols = []
    cols.append(chart.dimension.asdict())
    cols.extend(map(lambda c: c.asdict(), chart.metrics))
    with connections[chart.database].cursor() as cursor:
        cursor.execute(chart.query, params)
        for i in range(len(cursor.description)-1):
            data.append({'data': []})

        for db_row in cursor:
            for col_index, chart_col in enumerate(cols):
                data_list = []
                if col_index is not 0:
                    data_list.append(_convert_to_type(db_row[0], cols[0]['type']))
                    data_list.append(_convert_to_type(db_row[col_index], chart_col['type']))
                    data[col_index-1]['data'].append(copy.deepcopy(data_list))
                    data[col_index-1]['name'] = chart_col['label']
    return data


def multiple_series_row_highcharts_handler(chart, query, params=None):
    """
    Handles the multiple series data when the series name are
    to be extracted from the rows of query set
    """
    chart_data = []
    with connections[chart.database].cursor() as cursor:
        cursor.execute(chart.query, params)
        dimension_values = []
        separator_values = []
        for db_row in cursor:
            if [db_row[0], _fill_missing_values(chart.metrics[0].type)] not in dimension_values:
                dimension_values.append([db_row[0], _fill_missing_values(chart.metrics[0].type)])
            if db_row[1] not in separator_values:
                separator_values.append(db_row[1])

        for series in separator_values:
            single_chart_data = {'data': []}
            single_chart_data['data'] = copy.deepcopy(dimension_values)
            single_chart_data['name'] = series
            chart_data.append(single_chart_data)

        for dbrow in cursor:
            for single_series_obj in chart_data:
                if dbrow[1] == single_series_obj['name']:
                    for data in single_series_obj['data']:
                        if [dbrow[0], _fill_missing_values(chart.metrics[0].type)] == data:
                            data[1] = dbrow[2]
        return chart_data


def _fill_missing_values(data_type):
    if data_type == "string":
        return ""
    elif data_type == "number":
        return 0


def _convert_to_type(value, type_desired):
    if not value:
        return_value = None
    elif type_desired == 'string':
        if isinstance(value, basestring):
            return_value = value
        elif isinstance(value, (date, datetime)):
            return_value = "%s.0" % str(value)
        else:
            return_value = str(value)
    elif type_desired == 'number':
        return_value = _coerce_number(value)
    elif type_desired == 'timeofday':
        return_value = _to_time_of_day(value)
    elif type_desired == 'date':
        return_value = 'Date(' + str(value.year) + ', ' + str(value.month) + ', ' + str(value.day) + ')'
    else:
        assert False, "Invalid column type %s" % type_desired
    return return_value


def _coerce_number(possibly_number, default=0):
    if isinstance(possibly_number, Decimal):
        return float(possibly_number)
    if isinstance(possibly_number, (int, float)):
        return possibly_number
    try:
        if isinstance(possibly_number, basestring):
            return float(possibly_number.strip())
        else:
            return int(possibly_number)
    except:
        return default


def _to_time_of_day(str_or_int):
#TODO: Use Python time    
    if isinstance(str_or_int, int):
        seconds = str_or_int
        minutes = seconds / 60
        seconds = seconds % 60
        hours = minutes / 60
        minutes = minutes % 60
        return (hours, minutes, seconds, 0)
    elif isinstance(str_or_int, float):
        seconds = str_or_int
        minutes = seconds / 60
        seconds = seconds % 60
        hours = minutes / 60
        minutes = minutes % 60
        return (hours, minutes, seconds, 0)
    elif isinstance(str_or_int, basestring):
        tokens = str_or_int.split(":")
        if len(tokens) > 1:
            hour = _coerce_number(tokens[0], 0)
            minute = _coerce_number(tokens[1], 0)
            return (hour, minute, 0, 0)
        else:
            return (0, 0, 0, 0)
    else:
        assert False


class Dimension(object):
    '''Represents a <dimension> from charts.xml'''

    dimension_types = ['string', 'number', 'timeofday', 'date']

    def __init__(self, dimension_id, dim_type):
        assert dim_type in Dimension.dimension_types, 'Unsupported dimension type %s' % dim_type
        self.id = dimension_id.replace(" ", "_")
        self.type = dim_type

    def asdict(self):
        return {"id": self.id, "label": self.id, "type": self.type}


class Metric(object):
    '''Represents a <dimension> from charts.xml'''

    metric_types = ['string', 'number', 'timeofday', 'date']

    def __init__(self, id, metric_type="number"):
        assert metric_type in Metric.metric_types, 'Unsupported dimension type %s' % metric_type
        self.id = id.replace(" ", "_")
        self.type = metric_type

    def asdict(self):
        return {"id": self.id, "label": self.id, "type": self.type}


class ChartData(object):
    '''Represents a <chart> from charts.xml

        chart_handler is a function that handles generating chart data
        into an object that the client can understand.
        chart_handler must take the following parameters :
           1. The chart object
           2. A dictionary containing query parameters
        The method is expected to be defined in the module
    '''
    def __init__(self, chart_id, database, group, lib, permissions_list,
                 groups_list, query, dimension,
                 metrics, separator, chart_type):

        self.id = chart_id
        self.database = database
        #self.handler = globals()[chart_handler]
        self.query = query
        self.chart_type = chart_type
        self.group = group
        self.permissions_list = permissions_list
        self.groups_list = groups_list
        self.lib = lib
        self.dimension = dimension
        self.metrics = metrics
        if separator:
            self.separator = separator
        else:
            self.separator = None


def _parse_charts(charts_xml):
    doc = ET.parse(charts_xml)
    parsed_charts = OrderedDict()
    charts = doc.findall("chart")
    for chart in charts:
        if chart.get("id"):
            chart_id = chart.get("id")
        else:
            assert False, "id attribute missing in <chart> tag"
        db = chart.get("database", 'default')
        group = chart.get("group", 'default')
        lib = chart.get("lib", "googlechart")
        permissions_list = []
        if chart.find("permissions") is not None:
            chart_permissions = chart.find("permissions").text
            permissions_list = [str.strip(v) for v in chart_permissions.split(',')]
        groups_list = []
        if chart.find("auth_groups") is not None:
            chart_groups = chart.find("auth_groups").text
            groups_list = [str.strip(v) for v in chart_groups.split(',')]
        current_metrics = []
        if chart.find("dimension") is not None:
            dimension_id = chart.find("dimension").text
            dimension_type = chart.find("dimension").get("type", "string")
        dimension = Dimension(dimension_id, dimension_type)
        if chart.find("metric") is not None:
            metrics = chart.findall("metric")
            for m in metrics:
                metric = Metric(m.text, m.get("type", "number"))
                current_metrics.append(metric)
        separator = None
        if chart.find("separator") is not None:
            separator = chart.find("separator").text
        query = ""
        if chart.find("query") is not None:
            query = chart.find("query").text
        if chart.find("type") is not None:
            chart_type = chart.find("type").text
        else:
            chart_type = "Table"
        parsed_charts[chart_id] = ChartData(chart_id, db, group, lib,
                                            permissions_list, groups_list,
                                            query, dimension,
                                            current_metrics, separator,
                                            chart_type)
    return parsed_charts


def _augment_params(request):
    processors = []
    if 'parameter_processors' in settings.HIDASH_SETTINGS:
        processors = settings.HIDASH_SETTINGS['parameter_processors']
    params = request.GET.copy()
    for processor in processors:
        params.update(processor(request))
    return params


def _load_charts():
    if 'xml_file_path' in settings.HIDASH_SETTINGS:
        charts_xml = settings.HIDASH_SETTINGS['xml_file_path']
    else:
        return None

    return _parse_charts(charts_xml)
