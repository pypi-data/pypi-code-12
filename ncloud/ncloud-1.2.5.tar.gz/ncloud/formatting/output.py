# ----------------------------------------------------------------------------
# Copyright 2015 Nervana Systems Inc.
# ----------------------------------------------------------------------------
"""
Control the formatting and display of returned output.
"""
from __future__ import print_function
import json
import logging
import sys

# output formatting related
MIN_COL_LENGTH = 10
RIGHT_SPACE_MARGIN = 2


logger = logging.getLogger()


def get_key_values(json):
    if len(json) == 0:
        return [], []

    if isinstance(json, list):
        keys = list(json[0].keys())
        values = [list(row.values()) for row in json]
    else:
        keys = list(json.keys())
        values = [list(json.values())]
    return keys, values


def get_max_col_widths(headers, rows):
    all_rows = list(rows)
    all_rows.append(headers)

    num_col = len(headers)
    row_format = ("{:>%s}" % MIN_COL_LENGTH + " " * RIGHT_SPACE_MARGIN +
                  "|") * num_col

    max_col_widths = [MIN_COL_LENGTH] * num_col
    for row in all_rows:
        # str because None -> 'None' for python 3
        formatted_row = row_format.format(*(str(r) for r in row))
        for col_num, col in enumerate(formatted_row.split("|")[:-1]):
            max_col_widths[col_num] = max(max_col_widths[col_num], len(col))
    return max_col_widths


def get_max_row_width(max_col_widths):
    return sum(max_col_widths) + len(max_col_widths)*(RIGHT_SPACE_MARGIN+1)


def get_max_header_format(max_col_widths):
    row_format_builder = [("{:^%s}|") % (s + RIGHT_SPACE_MARGIN)
                          for s in max_col_widths]
    return "".join(row_format_builder)


def get_max_value_format(max_col_widths):
    row_format_builder = [("{:>%s}" + " " * RIGHT_SPACE_MARGIN + "|") % s
                          for s in max_col_widths]
    return "".join(row_format_builder)


def get_plus_row(max_col_widths):
    plus_row = "-"
    for col_width in max_col_widths:
        plus_row = plus_row + "-" * (col_width + RIGHT_SPACE_MARGIN) + "+"
    return plus_row[:-1] + "-"


def print_table(json):
    if json is None:
        return

    headers, rows = get_key_values(json)
    max_col_widths = get_max_col_widths(headers, rows)

    max_row_width = get_max_row_width(max_col_widths)
    max_header_format = get_max_header_format(max_col_widths)
    max_value_format = get_max_value_format(max_col_widths)

    if len(rows) > 0:
        print("-" * (max_row_width+1))
        print("|" + max_header_format.format(*headers))
        print(get_plus_row(max_col_widths))
        for row in rows:
            # str because None -> 'None' for python 3
            print("|" + max_value_format.format(*(str(r) for r in row)))
        print("-" * (max_row_width+1))


def print_error(err):
    if err is not None:
        msg = err.text.strip()
        try:
            json_msg = json.loads(msg)
            if "status" in json_msg:
                msg = json_msg["status"]
        except ValueError:
            pass
        print_table({"error_code": err.status_code, "message": msg})
    else:
        logger.error("No error message in response")
    sys.exit(1)
