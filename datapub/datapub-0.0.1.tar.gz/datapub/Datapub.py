import requests
import json
import csv

def num(s):
    try:
        return int(s)
    except ValueError:
        try:
            return float(s)
        except ValueError:
            return s

def to_nums(xs):
    return [num(x) for x in xs]

def request_text(url):
    try:
        r = requests.get(url)
    except:
        print('Error requesting URL: {0}'.format(url))
        
    if r.status_code != 200:
        print('Failed to load URL (Error {0}): {1}'.format(r.status_code, url))
        return None
    
    try:
        text = r.text
    except:
        print('Failed to load URL text: {0}'.format(url))
        return None

    return text

def request_json(url):
    try:
        r = requests.get(url)
    except:
        print('Error requesting URL: {0}'.format(url))
        
    if r.status_code != 200:
        print('Failed to load URL (Error {0}): {1}'.format(r.status_code, url))
        return None
    
    try:
        j = r.json()
    except:
        print('Failed to load URL JSON: {0}'.format(url))
        return None

    return j

def parse_ds(text):
    try:
        lines = text.splitlines()
        c = csv.reader(lines, dialect='datapub')
        return [to_nums(list(row)) for row in c]
    except:
        print('Failed to parse CSV data')
        return None

class Datapub:
    def __init__(self, host = 'datapub.io', port = 3000):
        self.host = host
        self.port = port
        self.url_base = 'http://{0}:{1}'.format(host, port)
        csv.register_dialect(
            'datapub',
            delimiter=',',
            doublequote=False,
            escapechar='\\',
            lineterminator='\n',
            quotechar='"',
            strict=True,
            quoting=csv.QUOTE_MINIMAL)
        
    def get_ds(self, dsId):
        url = '{0}/dataset/{1}/download'.format(self.url_base, dsId)
        text = request_text(url)
        if text == None:
            return None
        else:
            return parse_ds(text)

    def get_paper_ds(self, paperId, dsIndex):
        url = '{0}/dataset/{1}/{2}/download'.format(
            self.url_base, paperId, dsIndex)
        text = request_text(url)
        if text == None:
            return None
        else:
            return parse_ds(text)

    def paper_datasets(self, paperId):
        url = '{0}/api/json/v1/paper_datasets/{1}'.format(
            self.url_base, paperId)
        return request_json(url)
