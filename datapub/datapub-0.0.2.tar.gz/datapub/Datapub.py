#!/usr/bin/env python3
import requests
import csv
import pandas as pd
from io import StringIO


def _num(s):
    try:
        return int(s)
    except ValueError:
        try:
            return float(s)
        except ValueError:
            return s


def _to_nums(xs):
    return [_num(x) for x in xs]


def _request_text(url):
    try:
        r = requests.get(url)
    except Exception as e:
        print(e)
        print('Error requesting URL: {0}'.format(url))

    if r.status_code != 200:
        print('Failed to load URL (Error {0}): {1}'.format(r.status_code, url))
        return None

    try:
        text = r.text
    except Exception as e:
        print(e)
        print('Failed to load URL text: {0}'.format(url))
        return None

    return text


def _request_json(url):
    try:
        r = requests.get(url)
    except Exception as e:
        print(e)
        print('Error requesting URL: {0}'.format(url))

    if r.status_code != 200:
        print('Failed to load URL (Error {0}): {1}'.format(r.status_code, url))
        return None

    try:
        j = r.json()
    except Exception as e:
        print(e)
        print('Failed to load URL JSON: {0}'.format(url))
        return None

    return j


def _parse_ds(text):
    try:
        return pd.read_csv(StringIO(text), dialect='datapub')
    except Exception as e:
        print(e)
        return None


class Datapub:
    def __init__(self, host='datapub.io', port=3000):
        self.host = host
        self.port = port
        self.urlBase = 'http://{0}:{1}'.format(host, port)
        csv.register_dialect(
            'datapub',
            delimiter=',',
            doublequote=False,
            escapechar='\\',
            lineterminator='\n',
            quotechar='"',
            strict=True,
            quoting=csv.QUOTE_NONNUMERIC)

    def get_ds(self, ds_id):
        url = '{0}/dataset/{1}/download'.format(self.urlBase, ds_id)
        text = _request_text(url)

        if text is None:
            return None
        else:
            return _parse_ds(text)

    def get_paper_ds(self, paperId, dsIndex):
        url = '{0}/dataset/{1}/{2}/download'.format(
            self.urlBase, paperId, dsIndex)
        text = _request_text(url)
        if text is None:
            return None
        else:
            return _parse_ds(text)

    def paper_datasets(self, paperId):
        url = '{0}/api/json/v1/paper_datasets/{1}'.format(
            self.urlBase, paperId)
        return _request_json(url)


def print_usage():
    print("Usage:\n" +
          "import datapub\n" +
          "Datapub = datapub.Datapub()\n" +
          "ds = Datapub.get_ds(\'c9fa7898a7\')\n" +
          "ds = Datapub.get_paper_ds(\'pmid26111164\', 0)\n" +
          "print(Datapub.paper_datasets(\'4339fcd7ac\'))"
          )
