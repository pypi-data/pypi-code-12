import datetime
from grimoire.django.tracked.reports import RichFormatTrackingReport
from django.utils.timezone import now
from django.utils.six import text_type, string_types, StringIO
import xlsxwriter
import pytz
import re

_REMOVE_INVALID_CHARS = re.compile(r'[^ daAmbByYpIHMSf%/:\.-]')
_REMOVE_INVALID_MARKS = re.compile(r'%[^daAmbByYpIHMSf%]')
_REMOVE_INVALID_EXTRA = re.compile(r'(?<!%)[daAmbByYpIHMSf]')
_UNIFY_SPACES = re.compile(r'\s{2,}')
_TRIM_SPACES = re.compile(r'\s*([/:\.-])\s*')
_MIN_AFTER_LHOURS = re.compile(r'(?<=%H:)%M')
_MIN_AFTER_SHOURS = re.compile(r'(?<=%I:)%M')
_MIN_BEFORE_SECONDS = re.compile(r'%M(?=:%S)')
_FRAC_AFTER_SECONDS = re.compile(r'(?=%S)\.%f')
_REMOVE_REMAINING_MARKS = re.compile(r'%[^%]')
_TRIM_NONALPHA_CHARS = re.compile(r'^\s*[/:\.-]*|[/:\.-]*\s*$')

def strftime2xls(fmt):
    """
    Converts a strftime format to an xls format.
    Discards specifiers which are not compatible to both formats.
    """

    fmt = _REMOVE_INVALID_CHARS.sub('', fmt)
    fmt = _REMOVE_INVALID_MARKS.sub('', fmt)
    fmt = _REMOVE_INVALID_EXTRA.sub('', fmt)
    fmt = _UNIFY_SPACES.sub(' ', fmt)
    fmt = _TRIM_SPACES.sub(r'\1', fmt)
    fmt = fmt.replace('%d', 'dd').replace('%a', 'ddd').replace('%A', 'dddd')
    fmt = fmt.replace('%m', 'mm').replace('%b', 'mmm').replace('%B', 'mmmm')
    fmt = fmt.replace('%y', 'yy').replace('%Y', 'yyyy')
    fmt = _MIN_AFTER_LHOURS.sub('mm', fmt)
    fmt = _MIN_AFTER_SHOURS.sub('mm', fmt)
    fmt = _MIN_BEFORE_SECONDS.sub('mm', fmt)
    fmt = _FRAC_AFTER_SECONDS.sub('.00', fmt)
    fmt = fmt.replace('%S', 'ss').replace('%h', 'h').replace('%H', 'hh')
    fmt = fmt.replace('%p', 'AM/PM').replace('.%f', '')
    fmt = _REMOVE_REMAINING_MARKS.sub('', fmt)
    fmt = fmt.replace('%%', '%')
    fmt = _TRIM_NONALPHA_CHARS.sub('', fmt)
    return fmt

class XLSReport(RichFormatTrackingReport):

    xls_worksheet_name = 'Records'
    xls_worksheet_start_row = 0
    xls_worksheet_start_col = 0
    xls_timezone = pytz.utc

    def get_cell_format(self, request, column_spec, column_display, column_index, row_index, cell_value):
        """
        Gets data for the format to be used when formatting the cell. For XLS formats, we will pass a
          dictionary suitable for workbook.Format constructor.
        :param request: The request being processed.
        :param column_spec: The current column, as returned as item in by `get_list_report()`.
        :param column_display: The current column display text.
        :param column_index: The current column index.
        :param row_index: The 0-based row index. None if processing a header cell.
        :param cell_value: The cell value (not serialized). None if processing a header cell..
        :return: The returned data is arbitrary, and according to the underlying
          report class.
        """

        return {}

    def get_col_width(self, request, column_spec, column_display, column_index):
        """
        Gets the width for the column.
        :param request: The request being processed.
        :param column_spec: The current column, as returned as item in by `get_list_report()`.
        :param column_display: The current column display text.
        :param column_index: The current column index.
        :return: A positive integer value, or None for not setting width.
        """

        return None

    def get_row_height(self, request, row_index, row_data):
        """
        Gets the height for the row.
        :param request: The request being processed.
        :param row_index: The 0-based row index. None if processing a header cell.
        :param row_data: The data row being processed.
        :return: A positive integer value, or None for not setting height.
        """

        return None

    def get_xls_timezone(self, request):
        """
        Timezone to use for date calculation. Aware dates are converted to this timezone and then
          the timezone information is removed from the result.
        :param request: Request being processed.
        :return: timezone object, like pytz.utc
        """

        return self.xls_timezone

    def get_attachment_filename(self, request, period):
        """
        Filename to be used for the attachment
        :param request: Requset being processed.
        :param period: Period being queried.
        :return: A string with the filename.
        """

        return 'report-%s.xlsx' % now().strftime("%Y%m%d%H%M%S")

    def get_xls_worksheet_name(self, request):
        """
        Name for the worksheet.
        :param request: Requeset being processed.
        :return: String with worksheet name.
        """

        return self.xls_worksheet_name

    def get_xls_worksheet_start_row(self, request):
        """
        Starting row in the worksheet.
        :param request: Requeset being processed.
        :return: integer with worksheet name.
        """

        return self.xls_worksheet_start_row

    def get_xls_worksheet_start_col(self, request):
        """
        Starting col in the worksheet.
        :param request: Requeset being processed.
        :return: integer with worksheet name.
        """

        return self.xls_worksheet_start_col

    def _xls_extra_dump(self, request, headers, rows, workbook, worksheet, header_format_func, cell_format_func,
                        writer_func, columns_spec):
        """
        Performs extra processing in the report's workbook/worksheet.
        :param request: Request being processed.
        :param headers: Headers being dumped.
        :param rows: Rows being dumped.
        :param workbook: Current file being dumped.
        :param worksheet: Current worksheet being dumped.
        :param header_format_func: Function(col) to get a format object. Relies on get_cell_format().
        :param cell_format_func: Function(row, col, value, svalue) to get a format object. Relies on get_cell_format().
        :param writer_func: Function(row, col, value, format) to use when reading. Ideally.
        :param columns_spec: Already calculated value from get_list_report().
        :return: Nothing.
        """

    def dump_report_content(self, request, result):
        """
        Dumps the content to a string, suitable to being written on a file.
        :param result:
        :return: string
        """

        stream = StringIO()
        workbook = xlsxwriter.Workbook(stream, {'in_memory': True})
        worksheet = workbook.add_worksheet(self.get_xls_worksheet_name(request))
        formats = {}
        headers = result.headers
        rows = result.values
        start_row = self.get_xls_worksheet_start_row(request)
        start_col = self.get_xls_worksheet_start_col(request)
        columns_spec = self.get_list_report(request)
        timezone = self.get_xls_timezone(request)

        datetime_format = strftime2xls(self.datetime_format)
        date_format = strftime2xls(self.date_format)
        time_format = strftime2xls(self.time_format)

        def preprocess_format(format):
            return formats.setdefault(repr(format), workbook.add_format(format))

        def header_format(col):
            return self.get_cell_format(request, columns_spec[col], headers[col], col, None, None)

        def cell_format(row, col, value):
            return self.get_cell_format(request, columns_spec[col], headers[col], col, row, value)

        def write(row, col, data, format):
            if isinstance(data, datetime.datetime):
                data = data if data.tzinfo is None else data.astimezone(timezone).replace(tzinfo=None)
                format = dict(format, num_format=datetime_format)
                worksheet.write_datetime(row, col, data, preprocess_format(format))
            elif isinstance(data, datetime.time):
                format = dict(format, num_format=time_format)
                worksheet.write_datetime(row, col, data, preprocess_format(format))
            elif isinstance(data, datetime.date):
                format = dict(format, num_format=date_format)
                worksheet.write_datetime(row, col, data, preprocess_format(format))
            elif isinstance(data, string_types):
                return worksheet.write_string(row, col, data, preprocess_format(format))
            else:
                return worksheet.write(row, col, data, preprocess_format(format))

        for col, header in enumerate(headers):
            # Header cell_processing.
            width = self.get_col_width(request, columns_spec[col], headers[col], col)
            if width is not None:
                worksheet.set_column(col, col, width)
            write(start_row, start_col + col, header, header_format(col))

        start_row += 1
        for row, data in enumerate(rows):
            height = self.get_row_height(request, row, data)
            if height is not None:
                worksheet.set_row(row, height)
            for col, value in enumerate(data):
                write(start_row + row, start_col + col, value, cell_format(row, col, value))

        self._xls_extra_dump(request, headers, rows, workbook, worksheet, header_format, cell_format, write,
                             columns_spec)

        workbook.close()
        return stream.getvalue()