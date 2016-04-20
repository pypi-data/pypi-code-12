from __future__ import print_function
from sys import stdin, stderr, exit
from pandas import read_table


def read_indata(input_file, noheader, sep="\t"):
    """Reads a sep-delimited file and returns a dataframe.

    Utility function to account for the fact that there are three types
    of possible delimited files you want to handle: those with a full header,
    those with no header and those lacking a header in the index column.
    """

    infile = stdin if input_file == "-" else input_file

    header_row = None if noheader else 0

    # # if there is only one line it cannot be the header
    # if not _check_that_file_contains_more_than_one_line(infile):
    #     header_row = None

    try:
        df = read_table(infile, header=header_row, dtype=str, sep=sep)
    except AttributeError:
        print(
            """If the infile only contains one line you must use the --noheader flag.""",
            file=stderr)
        exit(1)

    df = _turn_index_into_regular_column_if_it_contains_data(df)

    return df


def _turn_index_into_regular_column_if_it_contains_data(df):

    if not all(df.index == range(len(df))):
        df = df.reset_index()

    return df

# def _check_that_file_contains_more_than_one_line(infile):

#     try:
#         lines = open(infile).readlines()
#     except TypeError:  # was not file but stdin
#         lines = infile.readlines()

#     more_than_one_line = len([l for l in lines if l.strip() != ""]) > 1

#     return more_than_one_line
