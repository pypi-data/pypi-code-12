#!/usr/bin/env python

def main():

    import argparse

    parser = argparse.ArgumentParser(description='placeholder')

    parser.add_argument('--out', required=False,
                        help='sqlite file to save result in')
    parser.add_argument('--sql', required=False,
                        help='sql to run')
    parser.add_argument('files', nargs='*')

    args = parser.parse_args()

    import sqlite3
    import os
    import re
    import sys

    if args.out:
        conn = sqlite3.connect(args.out)
    else:
        conn = sqlite3.connect(":memory:")

    db = conn.cursor()

    name = "sheet"

    if args.sql:
        if args.out:
            name = os.path.split(os.path.splitext(args.out)[0])[1]
            name = re.sub(r'/[^a-zA-Z0-9]/_/', '_', name)

    if args.sql:
        db.execute("drop table if exists {}".format(name))

    for idx, f in enumerate(args.files):
        db.execute('attach database ? as ?', [f, "_db{}_".format(idx)])

    if args.sql:
        success = False
        first_error = None
        pattern ["{}", "select {}"]
        for p in pattern:
            try:
                cmd = p.format(args.sql)
                db.execute("create table {} as {}".format(name, cmd))
                success = True
            except sqlite3.OperationalError as e:
                if not first_error:
                    first_error = e
                if "syntax error" in e:
                    continue
                raise first_error
        if not success:
            if first_error:
                raise first_error

        try:
            import unicodecsv as csv
        except ImportError:
            import csv

        data = db.execute("SELECT * FROM {}".format(name))
        names = [description[0] for description in data.description]
        writer = csv.writer(sys.stdout)
        writer.writerow(names)
        writer.writerows(data)

    conn.close()
