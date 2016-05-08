"""

Copyright 2014 Heung Ming Tai

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

   http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""
from __future__ import print_function
from __future__ import absolute_import
from __future__ import division

import sys

import six


def input(prompt, file=None):
    """
    Just like raw_input in python2 or input in python3, but can optionally
    redirect the prompt to other file objects.
    Args:
        prompt: A string for the prompt.
        file: Optional. A file object to the prompt is written to.
    """
    if file is None:
        return six.moves.input(prompt)
    else:
        old_stdout = sys.stdout
        try:
            sys.stdout = file
            return six.moves.input(prompt)
        finally:
            sys.stdout = old_stdout


class DataPrinter(object):
    PRINT_STYLE_HTML_TABLE = 'html'
    PRINT_STYLE_PLAIN = 'plain'
    PRINT_STYLE_R = 'R'
    PRINT_STYLE_TABLE = 'table'
    PRINT_STYLE_VERBOSE = 'verbose'
    NICETABLE_COL_LEN = 80
    PRINT_STYLE_R = 'R'
    PRINT_STYLE_NICETABLE = 'nicetable'

    OPTION_TITLE = 'title'
    OPTION_ADDITIONAL_TRAILING_CONTENT = 'additional-trailing-content'

    def __init__(
        self,
        data,
        headers=(),
        header_types=None,
        delimiter='\t',
        max_col_len=NICETABLE_COL_LEN,
        print_func=print,
    ):
        """Constructs a DataPrinter object

        Args:
          data: A list of dict's or a list of lists. Each dict or list
              represents a row of data. If it's a dict, the keys are the
              column names in strings and the values are the column values in
              strings.  If it's a list, then each item is the value of a
              column of the row. Each value should be a string properly
              formatted, since DataPrinter does not do any special formatting
              of each value.

          headers: Optionally supply a list of headers in strings to control
              what columns are printed out and what order are the columns
              printed.

          header_types: A list of strings representing the types of the
              headers. It's currently used for PRINT_STYLE_R form. This is not
              needed if you are not using PRINT_STYLE_R.

          delimiter: The delimiter in string for separating column values. By
              default it's a tab character.

          max_col_len: An integer to indicate the maximum column length when
              the data is printed in PRINT_STYLE_NICETABLE. By default it's
              80.

          print_func: A function that takes a string as an argument. The
              function is used for printing the data. By default it uses the
              built-in print function.
        """
        if not hasattr(data, "__getitem__"):
            data = list(data)

        if not headers and data and isinstance(data[0], dict):
            # infer headers from data
            headers = sorted(data[0].keys())

        self.headers = headers

        if data and isinstance(data[0], dict):
            self.data = self._convert_list_of_dicts(headers, data)
        else:
            self.data = data

        self.header_types = header_types
        self.delimiter = delimiter
        self.max_col_len = max_col_len
        self.print_func = print_func

    def _convert_list_of_dicts(self, headers, ls_of_dicts):
        """
        Convert list of dicts to list of lists.
        """
        data = [[d[header] for header in headers] for d in ls_of_dicts]
        return data

    def print_result(self, style=PRINT_STYLE_TABLE, options=None):
        if options is None:
            options = {}

        if style == DataPrinter.PRINT_STYLE_R:
            json_headers = []
            for header, t in zip(self.headers, self.header_types):
                h = {'name': header, 'type': t}
                json_headers.append(
                    json.dumps(h).replace('\t', '').replace('\n', '')
                    )
            self.print_func(self.delimiter.join(json_headers))
            self.print_data()
        elif style == DataPrinter.PRINT_STYLE_PLAIN:
            self.print_data()
        elif style == DataPrinter.PRINT_STYLE_VERBOSE:
            self.print_verbose()
        elif style == DataPrinter.PRINT_STYLE_HTML_TABLE:
            self.print_html_table(options)
        elif style == DataPrinter.PRINT_STYLE_NICETABLE:
            self.print_table(is_nicetable=True)
        else:
            self.print_table()

    def print_data(self):
        # Each value is a row with ^A as delimiter
        for row in self.data:
            self.print_func(self.delimiter.join(row))

    def print_table(self, is_nicetable=False):
        max_widths = [len(header) for header in self.headers]
        for row in self.data:
            for i, col in enumerate(row):
                max_widths[i] = max(max_widths[i], self.get_len(col))

        if is_nicetable:
            max_widths = [
                min(self.max_col_len, width) for width in max_widths]
            print_data_row = self.print_nice_data_row
        else:
            print_data_row = self.print_data_row

        self.print_horizontal_line(max_widths)
        # print header
        print_data_row(max_widths, self.headers)
        self.print_horizontal_line(max_widths)

        for row in self.data:
            print_data_row(max_widths, row)
        self.print_horizontal_line(max_widths)

    def print_horizontal_line(self, widths):
        segments = ['-' * (width + 2) for width in widths]
        self.print_func("+%s+" % '+'.join(segments))

    def print_data_row(self, widths, data_row):
        formatted_row = [" %-*s " % (width, col)
                            for width, col in zip(widths, data_row)]
        self.print_func("|%s|" % '|'.join(formatted_row))

    def print_verbose(self):
        if self.headers:
            max_header_len = max([len(header) for header in self.headers])
        else:
            max_header_len = 0

        for i, row in enumerate(self.data):
            self.print_func("*" * 27 + " %1d. row " % (i + 1) + "*" * 27)
            for header, col in zip(self.headers, row):
                self.print_func("%*s: %s" % (max_header_len, header, col))

    def print_nice_data_row(self, widths, data_row):
        # calculate the maximum of lines need for this row
        count_line = 1
        for width, col in zip(widths, data_row):
            col_len = self.get_len(col)
            if col_len > width:
                tmp = int(col_len / width)
                if col_len % width != 0:
                    tmp += 1
                count_line = max(count_line, tmp)

        # print them out
        for i in range(count_line):
            cells = []
            for width, col in zip(widths, data_row):
                col_len = self.get_len(col)
                spaces_used = i * width
                if col_len > spaces_used:
                    # We display the maximum number of characters for this
                    # column, or the number of characters still left to
                    # display if it's smaller
                    len_to_display = min(col_len - width * i, width)
                    text = col[spaces_used:spaces_used + len_to_display]
                    cells.append(text.replace('\t', ' ').replace('\n', ' '))
                else:
                    cells.append("")
            formatted = [" %-*s " % (width, col)
                            for width, col in zip(widths, cells)]
            self.print_func("|%s|" % '|'.join(formatted))

    def print_html_table(self, options):
        # print everything before the table
        html = """
<html>
<head>
    <title>{title}</title>
    <style>
    table {{
        border-collapse:collapse;
    }}
    table, tr, td, th {{
        border: 1px solid black;
        padding: 3px;
    }}
    th {{
        background: #333;
        color: white;
        font-size: 80%;
    }}
    tr:nth-child(even) {{
        background: #ccc;
    }}
    tr:nth-child(odd) {{
        background: #fff;
    }}

    </style>
</head>
<body>
<table style="border: 1px solid black">
{headers}
{rows}
</table>
{trailing_content}
<p>Created at {timestamp}</p>
</body>
</html>
        """

        title = options.get(self.OPTION_TITLE, "")
        trailing_content = options.get(
            self.OPTION_ADDITIONAL_TRAILING_CONTENT,
            "",
        )
        headers = "<tr><th>" + "</th><th>".join(self.headers) + "</th></tr>\n"

        html_rows = []
        for row in self.data:
            partial_html_row = "</td><td>".join(row)
            html_row = "<tr><td>" + partial_html_row + "</td></tr>"
            html_rows.append(html_row)

        rows = "\n".join(html_rows)

        timestamp = time.ctime()

        self.print_func(html.format(**locals()))

    def get_len(self, value):
        if not value:
            return 0
        else:
            return len(value)

if __name__ == "__main__":
    rows = [
        {'a': "apple", 'b': "boy"},
        {'a': "one", 'b': "two"},
    ]
    DataPrinter(rows).print_result()
