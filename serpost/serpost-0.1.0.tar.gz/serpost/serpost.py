# coding: utf-8

from datetime import datetime
import sys
from bs4 import BeautifulSoup

if sys.version_info >= (3, 0):
    from urllib.request import urlopen
    from urllib.parse import urlencode
else:
    from urllib2 import urlopen
    from urllib import urlencode

url = 'http://clientes.serpost.com.pe/prj_tracking/seguimientolinea.aspx'
DATE_FORMAT = '%d/%m/%Y %H:%M'


def prepare_payload():
    response = urlopen(url)
    soup = BeautifulSoup(response.read(), 'lxml')
    form = soup.find('form')
    data = {}
    for input_tag in form.find_all('input'):
        data[input_tag['name']] = input_tag.get('value')
    return data


def query_tracking_code(tracking_code):
    payload = prepare_payload()
    payload['txtTracking'] = tracking_code
    response = urlopen(url, urlencode(payload).encode('utf-8'))
    soup = BeautifulSoup(response.read(), 'lxml')
    table = soup.find(id='gvSegEnvio')
    if table is None:
        return []
    result = []
    for tr in table.find_all('tr'):
        tds = tr.find_all('td')
        if not tds or len(tds) != 2:
            continue
        cleaned_date = tds[0].text.strip()[:16]
        result.append({
            'date': datetime.strptime(cleaned_date, DATE_FORMAT),
            'message': tds[1].text
        })
    return sorted(result, key=lambda x: x['date'])
