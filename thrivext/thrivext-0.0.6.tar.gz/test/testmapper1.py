#! /usr/bin/python

import sys
import json

DELIM = "\x01"


def main():
    JSON_KEYS = ["boolean_t", "int_t", "bigint_t", "float_t",
                 "char_t", "varchar_t", "timestamp_t", "date_t"]
    for line in sys.stdin:
        dct = json.loads(line)
        row = map(dct.get, JSON_KEYS)
        print DELIM.join(map(str, row))

    # Put some message on stderr
    sys.stderr.write("error message")
if __name__ == "__main__":
    main()
