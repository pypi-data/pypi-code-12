import json
import logging

import pandas as pd

from .helpers import SerenyticsException, make_request
from . import settings

logger = logging.getLogger(__name__)


class UnknownDataSource(SerenyticsException):
    def __init__(self, uuid_or_name):
        super(UnknownDataSource, self).__init__(u'Source with uuid or name "{}" does not exist'.format(uuid_or_name))


class DataSource(object):
    """
    Serenytics data source
    """

    def __init__(self, config, headers):
        self._config = config
        self._headers = headers

    def _check_is_storage_source(self):
        if self._config['type'] != 'Storage':
            raise SerenyticsException('Error: You can only reload the data of a storage data source.')

    @property
    def name(self):
        return self._config['name']

    @property
    def uuid(self):
        return self._config['uuid']

    def reload_data(self, new_data):
        """
        Reset data of a Storage data source.

        It erases old data and loads new data instead.

        Notes:
            - current data source must be a Storage data source
            - new data doesn't have to have the same structure as old data.
        """
        self._check_is_storage_source()

        reload_url = settings.SERENYTICS_API_DOMAIN + '/api/data_source/' + self.uuid + '/reload'
        make_request('post', reload_url, data=json.dumps(new_data), headers=self._headers,
                     expected_json_status='ok')

    def reload_data_from_array(self, columns, rows):
        """
        Reset data of a Storage data source.

        It erases old data and loads new data instead.

        :param columns: list of string, each string is a column name
        :param rows: list of list of values, each list of values is a row

        Notes:
            - current data source must be a Storage data source
            - new data doesn't have to have the same structure as old data.
        """
        self._check_is_storage_source()

        new_data = []
        for r in rows:
            new_row = {}
            for idx, column in enumerate(columns):
                column_name = column if column != '$$count$$' else '__count__'
                new_row[column_name] = r[idx]
            new_data.append(new_row)

        self.reload_data(new_data)

    def reload_data_from_dataframe(self, df):
        """
        Reset data of a Storage data source.

        It erases old data and loads new data instead.

        :param df: pandas dataframe to load in the source

        Notes:
            - current data source must be a Storage data source
            - new data doesn't have to have the same structure as old data.
        """
        self._check_is_storage_source()

        rows = df.values.tolist()
        self.reload_data_from_array(df.columns, rows)

    def reload_data_from_file(self, filename, separator=',', force_types=None):
        """
        Reset data of a Storage data source.

        It erases old data and loads new data from the given file instead.

        :param filename: path of the file to load. The file must be a csv file (.csv) and can be gzipped (.csv.gz) for
        better transfer speed and shorter script execution times.
        :param separator: CSV field separator, usually a comma or a semicolon.
        :param force_types: Dict of column names with types ('int', 'float', 'datetime', 'str') to force column type in
        our storage.

        Notes:
            - current data source must be a Storage data source
            - new data doesn't have to have the same structure as old data.
        """
        self._check_is_storage_source()

        if not filename.endswith(('.csv', '.csv.gz')):
            raise SerenyticsException('filename must end with ".csv" or ".csv.gz"')

        self._upload_new_file(filename, separator, force_types)
        self._load_data_from_file()

    def update_data_from_file(self, filename, primary_key):
        """
        Update data of a Storage data source.

        Inserts new data from filename in current source and replace rows with same primary key as in given file.

        :param filename: path of the file to load. The file must be a csv file (.csv) and can be gzipped (.csv.gz) for
        better transfer speed and shorter script execution times.
        :param primary_key: column name of the primary key (the key used to uniquely define the data rows, such as an id
        or a guid).

        Notes:
            - current data source must be a Storage data source
            - new data has to have the same structure as old data
        """
        self._check_is_storage_source()

        if not filename.endswith(('.csv', '.csv.gz')):
            raise SerenyticsException('filename must end with ".csv" or ".csv.gz"')

        self._upload_new_file(filename)
        self._update_data_from_file(primary_key)

    def _upload_new_file(self, filename, separator=None, force_types=None):
        self._config['originalFileName'] = filename

        if separator is not None:
            self._config['jsonContent']['separator'] = separator

        if force_types is not None:
            self._config['jsonContent']['advanced_options'] = json.dumps({'force_types': force_types})

        self._save()

        response = make_request('GET', settings.SERENYTICS_API_DOMAIN + '/api/data_source/sign_s3/',
                                params={'s3_object_type': 'csv/gz', 's3_object_name': self.uuid},
                                headers=self._headers)

        with open(filename, 'r') as file_to_upload:
            make_request('PUT', response.json()['signed_request'], data=file_to_upload.read(),
                         headers={'Content-Type': 'csv/gz', 'x-amz-acl': 'private'})

    def _load_data_from_file(self):
        response = make_request('POST',
                                settings.SERENYTICS_API_DOMAIN + '/api/data_source/' + self.uuid + '/reload_from_file',
                                headers=self._headers)
        logger.info('import status: %s' % response.json())

    def _update_data_from_file(self, primary_key):
        make_request('POST',
                     settings.SERENYTICS_API_DOMAIN + '/api/data_source/' + self.uuid + '/update_from_file',
                     data=json.dumps({'primary_key': primary_key}),
                     headers=self._headers)

    def batch(self,
              rows_to_insert=None,
              rows_to_insert_or_update=None,
              rows_to_delete=None,
              primary_key=None,
              async=True):
        """
        Run batch operations on data source (insert/update/delete).

        Note: either `rows_to_insert`, `rows_to_insert_or_update` or `rows_to_delete` must be supplied to the function
        as a list of rows.

        :param operations: list of dict, each dict being a single row of data

        Notes:
            - current data source must be a Storage data source
            - new data has to have the same structure as old data.
        """
        self._check_is_storage_source()

        operations = []
        if rows_to_insert is None and rows_to_insert_or_update is None and rows_to_delete is None:
            raise SerenyticsException('at least one argument in `rows_to_insert`, `rows_to_insert_or_update` and'
                                      ' `rows_to_delete` must be not None')
        if (rows_to_insert_or_update or rows_to_delete) and primary_key is None:
            raise SerenyticsException('`primary_key`argument must be not None when updating or deleting rows')

        if rows_to_insert:
            operations.append({
                'action': 'insert',
                'rows': rows_to_insert
            })

        if rows_to_insert_or_update:
            operations.append({
                'action': 'insertOrUpdate',
                'rows': rows_to_insert_or_update,
                'primaryKey': primary_key
            })

        if rows_to_delete:
            operations.append({
                'action': 'delete',
                'rows': rows_to_delete,
                'primaryKey': primary_key
            })

        batch_url = settings.SERENYTICS_API_DOMAIN + '/api/data_source/' + self.uuid + '/batch'
        make_request('post', batch_url, headers=self._headers,
                     data=json.dumps({
                         'async': async,
                         'operations': operations
                     }),
                     expected_json_status='ok')

    def push_data(self, data):
        """
        Append `data` to current storage data source.

        Warning: this call is not blocking and doesn't wait for the data to be imported into serenytics datawarehouse.
        Then you won't have any guarantee that the data has really been imported. If you need a guarantee, at the
        expense of a longer function call, please use method `batch_push_data` and regroup all your rows of data
        in a list.
        """
        self._check_is_storage_source()
        token = self._config['jsonContent']['token']
        push_url = settings.SERENYTICS_API_DOMAIN + '/api/data_source/' + self.uuid + '/push/' + token
        make_request('post', push_url, data=json.dumps(data), headers={'Content-type': 'application/json'})

    def get_data(self, options=None):
        """
        Extract data from the data source
        """
        no_options = options is None

        if no_options:
            options = {'only_headers': True}

        response = make_request('post', settings.SERENYTICS_API_DOMAIN + '/api/formatted_data/' + self.uuid,
                                data=json.dumps(options),
                                headers=self._headers)
        response_content = response.json()

        if response_content['status'] == 'error':
            raise SerenyticsException(response_content['errors'][0])

        if not no_options:
            return Data(response_content)

        # make second API call to retrieve actual data
        headers = response_content['columns_titles']
        new_options = {
            'order': 'row_by_row',
            'data_processing_pipeline': [{
                'select': [header['name'] for header in headers]
            }]
        }
        response = make_request('post', settings.SERENYTICS_API_DOMAIN + '/api/formatted_data/' + self.uuid,
                                data=json.dumps(new_options),
                                headers=self._headers)
        response_content = response.json()

        if response_content['status'] == 'error':
            raise SerenyticsException(response_content['errors'][0])

        return Data(response_content)

    def _save(self):
        make_request('PUT', settings.SERENYTICS_API_DOMAIN + '/api/data_source/' + self.uuid,
                     data=json.dumps(self._config),
                     headers=self._headers)


class Data(object):
    """
    Handles data extracted from a data source
    """

    def __init__(self, raw_data):
        self._raw_data = raw_data

    @property
    def headers(self):
        return self._raw_data.get('columns_titles', [])

    @property
    def columns(self):
        return [header['name'] for header in self.headers]

    @property
    def rows(self):
        return self._raw_data.get('data', [])

    def get_as_dataframe(self):
        return pd.DataFrame(self.rows, columns=self.columns)
