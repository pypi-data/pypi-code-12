'''
Created on 23 Jun 2016

@author: martin
'''
import json
import zipfile
import os
from io import StringIO
import requests

_STATE = {'mlsd':False}
# pylint: disable=missing-docstring, no-self-use, unused-argument
# pylint: disable=protected-access, too-few-public-methods


def make_data_path(name):
    "Make the data path."
    _ = os.path.dirname(os.path.abspath(__file__))
    _ = os.path.join(_, 'data', name)
    return _


def bulk_json_insert(data):
    "Bulk insert json"
    tmp = dict()
    data = json.loads(data)
    from django.apps import apps
    from ..tools import models
    for item in data:
        model_name = item['model']
        model = apps.get_model(*model_name.rsplit('.', 1))
        fields = item['fields']
        fields['id'] = item['pk']

        for key in list(fields):
            field = model._meta.get_field(key)
            if field.is_relation:
                fields[key+'_id'] = fields.pop(key)

        if model not in tmp:
            tmp[model] = list()

        tmp[model].append(model(**fields))

    for model in list(tmp.keys()):
        model.objects.bulk_create(tmp[model])


def setup_ipranges_all():
    "Setup all ip's."
    from ..tools import models
    path = make_data_path('country.json')
    with open(path, 'r') as file_open:
        data = ''.join(file_open.readlines())
        bulk_json_insert(data)

    name = 'iprange_2016_06_23.json.zip'
    path = make_data_path(name)
    unzip = zipfile.ZipFile(path)
    data = unzip.read(name.rsplit('.', 1)[0]).decode('UTF-8')
    bulk_json_insert(data)


def call_command_returns(*args, **kwargs):
    "call command but wich returns the output."
    from django.core.management import call_command
    stdout = StringIO()
    kwargs['stdout'] = stdout
    call_command(*args, **kwargs)
    return stdout.getvalue().strip()


class RequestsMock(object):
    "Mock the request module"
    def __init__(self):
        self._restores = dict()
        self._response = dict()
        self.text = None

    def add_response_text_from_data(self, url, file_name):
        "If url is called the content of file_name is returned"
        _ = make_data_path(file_name)
        with open(_, 'r') as file_open:
            self._response[url] = ''.join(file_open.readlines())

    def insert_mock(self):
        "Insert the mock"
        self._restores['get'] = requests.get
        requests.get = self.get

    def remove_mock(self):
        "Remove the mock"
        requests.get = self._restores['get']

    def get(self, url):
        "Mocked request get function"
        self.text = self._response[url]
        return self


def setup_currencies():
    "Insert all currencies"
    from django.core.management import call_command
    call_command('update_countries')

    mock = RequestsMock()
    url = 'http://www.currency-iso.org/dam/downloads/lists/list_one.xml'
    file_name = 'list_one.xml'
    mock.add_response_text_from_data(url, file_name)
    mock.insert_mock()
    mock.remove_mock()
    call_command('update_currencies')


class MockFTP():
    def __init__(self, host):
        self._host = host
        self._path = None
        self._mlsd_called = False

        tmp = {'size':'91',
               'modify':'x_remove_x'}
        self._files = [
            ['delegated-arin-extended-latest', tmp],
            ['delegated-ripencc-extended-latest', tmp],
            ['delegated-afrinic-extended-latest', tmp],
            ['delegated-apnic-extended-latest', tmp],
            ['delegated-lacnic-extended-latest', tmp],]

    def login(self):
        pass

    def cwd(self, path):
        self._path = path

    def mlsd(self):
        if _STATE['mlsd']:
            _STATE['mlsd'] = False
            raise ValueError()
        else:
            _STATE['mlsd'] = True

        return self._files

    def retrbinary(self, retr, callback):
        ip4 = 'arin|US|ipv4|12.0.0.0|16777216|19830823|allocated|99e9610432f009e0e177ba0c274bb288\n'
        ip6 = 'arin|US|ipv6|2001:418::|32|20000524|allocated|9f14454567a6c23e60bfd4fec24d1438\n'
        nic = 'arin||ipv4|13.0.0.0|16777216|19830823|allocated|99e9610432f009e0e177ba0c274bb288\n'
        asn = 'arin|US|asn|14.0.0.0|16777216|19830823|allocated|99e9610432f009e0e177ba0c274bb288\n'
        for entry in [ip4, ip6, nic, asn]:
            callback(entry.encode('ASCII'))

    def retrlines(self, command, callback):
        if not 'second' in command:
            callback('-> second')
        else:
            callback('one two three four five six seven eight')



class FTPMock(object):
    FTP = MockFTP
    error_perm = ValueError


