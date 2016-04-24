# -*- coding: utf-8 -*-

from csv import register_dialect
from os.path import dirname, exists, expanduser

from pandas import read_csv

def csv2df(config):
    """Read CSV file into DataFrame"""

    csv_abs_path = expanduser(config["csv_abs_path"])
    quoting = config["input_csv_quoting"].strip().lower()
    try:
        quoting = int(quoting)
    except ValueError:
        if quoting == "quote_minimal":
            quoting = 0
        elif quoting == "quote_all":
            quoting = 1
        elif quoting == "quote_nonnumeric":
            quoting = 2
        elif quoting == "quote_none":
            quoting = 3
    register_dialect(
            "cash", delimiter=',', doublequote=True, escapechar=None,
            quotechar='"', quoting=quoting, skipinitialspace=True,
            strict=False)
    df = read_csv(
            csv_abs_path, squeeze=False, mangle_dupe_cols=False,
            na_filter=True, skip_blank_lines=True, compression="infer",
            decimal='.', encoding="utf-8", dialect="cash",
            error_bad_lines=False, warn_bad_lines=True)
    return df
