import datetime
from grimoire.django.tracked.reports import RichFormatTrackingReport
from django.utils.timezone import now
from django.utils.six import text_type, string_types, StringIO
import pytz
import xlsxwriter


class XLSReport(RichFormatTrackingReport):

    xls_worksheet_name = 'Records'
    xls_worksheet_start_row = 0
    xls_worksheet_start_col = 0
    xls_timezone = pytz.utc

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
                        columns_spec):
        """
        Performs extra processing in the report's workbook/worksheet.
        :param request: Request being processed.
        :param headers: Headers being dumped.
        :param rows: Rows being dumped.
        :param workbook: Current file being dumped.
        :param worksheet: Current worksheet being dumped.
        :param header_format_func: Function(col) to get a format object. Relies on get_cell_format().
        :param cell_format_func: Function(row, col, value, svalue) to get a format object. Relies on get_cell_format().
        :param columns_spec: Already calculated value from get_list_report()
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

        def preprocess_format(format):
            return formats.setdefault(repr(format), workbook.add_format(format))

        def header_format(col):
            return preprocess_format(
                self.get_cell_format(request, columns_spec[col], headers[col], col, None, None, None)
            )

        def cell_format(row, col, value, svalue):
            return preprocess_format(
                self.get_cell_format(request, columns_spec[col], headers[col], col, row, value, svalue)
            )

        def write(row, col, data, format):
            if isinstance(data, datetime.datetime):
                data = data if data.tzinfo is None else data.astimezone(timezone).replace(tzinfo=None)
                worksheet.write_datetime(row, col, data, format)
            elif isinstance(data, string_types):
                return worksheet.write_string(row, col, data, format)
            else:
                return worksheet.write(row, col, data, format)

        for col, header in enumerate(headers):
            # Header cell_processing.
            write(start_row, start_col + col, header, header_format(col))

        start_row += 1
        for row, data in enumerate(rows):
            for col, (value, serialized_value) in enumerate(data):
                write(start_row + row, start_col + col, value, cell_format(row, col, value, serialized_value))

        self._xls_extra_dump(request, headers, rows, workbook, worksheet, header_format, cell_format, columns_spec)

        workbook.close()
        return stream.getvalue()