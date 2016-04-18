# -*- coding: utf-8 -*-
import os
import json
import time
import uuid
from abc import ABCMeta, abstractmethod
from urllib import urlencode
from urllib2 import Request, urlopen
from oauth2client.client import AccessTokenCredentials
from googleapiclient.http import MediaFileUpload, MediaIoBaseDownload
from googleapiclient.discovery import build


class AbsGoogleServices(object):
    __metaclass__ = ABCMeta

    def __init__(self, client_id, client_secret, refresh_token):
        credentials = self.__get_credentials(client_id, client_secret, refresh_token)
        self.service = build(self.get_service_name(), self.get_api_version(), credentials=credentials)

    @abstractmethod
    def get_service_name(self):
        raise NotImplementedError()

    @abstractmethod
    def get_api_version(self):
        raise NotImplementedError()

    def __get_credentials(self, client_id, client_secret, refresh_token):
        google_account_config = {
            "client_id": client_id,
            "client_secret": client_secret,
            "refresh_token": refresh_token
        }
        access_token = self.__get_access_token_from_refresh_token(google_account_config)
        return AccessTokenCredentials(access_token, "MyAgent/1.0", None)

    @classmethod
    def __get_access_token_from_refresh_token(cls, google_config):
        google_config["grant_type"] = "refresh_token"
        request = Request('https://accounts.google.com/o/oauth2/token',
                          data=urlencode(google_config),
                          headers={
                              'Content-Type': 'application/x-www-form-urlencoded',
                              'Accept': 'application/json'
                          }
                          )
        response = json.load(urlopen(request))
        return response['access_token']


class BigQuery(AbsGoogleServices):
    def __init__(self, project_id, client_id, client_secret, refresh_token, retry_cnt=3, interval=3):
        super(BigQuery, self).__init__(client_id, client_secret, refresh_token)
        self.__project_id = project_id
        self.__retry_cnt = retry_cnt
        self.__interval = interval

    def get_service_name(self):
        return 'bigquery'

    def get_api_version(self):
        return 'v2'

    def has_table(self, data_set_id, table_id):
        for table in self.get_table_list(data_set_id):
            if table == table_id:
                return True
        return False

    def delete_table(self, data_set_id, table_id):
        self.service.tables().delete(projectId=self.__project_id, datasetId=data_set_id, tableId=table_id).execute()

    def create_table(self, source_csv_path, source_schema, data_set_id, table_id):
        body = self.__create_table_data(source_csv_path, source_schema, data_set_id, table_id)
        return self.__wait_job(body)

    def create_view(self, data_set_id, view_name, query):
        body = {
            'tableReference': {
                'tableId': view_name,
                'projectId': self.__project_id,
                'datasetId': data_set_id
            },
            'view': {
                'query': query
            }
        }
        self.service.tables().insert(projectId=self.__project_id, datasetId=data_set_id, body=body).execute()

    def get_record_count(self, data_set_id, table_name):
        query = 'SELECT COUNT(*) FROM {0}.{1}'.format(data_set_id, table_name)
        for data_dict in self.query(query):
            return int(data_dict['rows'][0][0])

    def import_csv_from_storage(self, storage_path, source_schema, data_set_id, table_id,
                                write_disposition='WRITE_EMPTY'):
        body = self.__create_load_data(storage_path, data_set_id, table_id, source_schema, write_disposition)
        return self.__wait_job(body)

    def query(self, query, time_out=60000, allow_large_results=False):
        def create_record_dict(rows):
            return {
                'rows': rows,
                'totalRows': page['totalRows'],
                'totalBytesProcessed': page['totalBytesProcessed']
            }

        query_data = {
            'query': query,
            'timeoutMs': time_out,
            'allowLargeResults': allow_large_results
        }
        response = self.service.jobs().query(
            projectId=self.__project_id,
            body=query_data).execute(num_retries=self.__retry_cnt)
        for page in self.__paging(self.service.jobs().getQueryResults,
                                  num_retries=self.__retry_cnt,
                                  **response['jobReference']):
            if page['jobComplete'] is False:
                raise Exception('job is not complete')
            if page['totalRows'] == '0':
                yield create_record_dict([])
                return
            row_list = []
            for row in page['rows']:
                value_list = []
                for value in row['f']:
                    value_list.append(value['v'])
                row_list.append(value_list)
            yield create_record_dict(row_list)

    def get_table_list(self, data_set_id):
        token = None
        while True:
            if token is None:
                result = self.service.tables().list(projectId=self.__project_id, datasetId=data_set_id).execute()
            else:
                result = self.service.tables().list(projectId=self.__project_id, datasetId=data_set_id,
                                                    pageToken=token).execute()
            token = result.get('nextPageToken', None)
            if token is None or len(token) == 0:
                break
            for table in result['tables']:
                if table['type'] != 'TABLE':
                    continue
                yield table['tableReference']['tableId']

    def __create_table_data(self, source_csv_path, source_schema, data_set_id, table_id):
        return {
            'jobReference': {
                'projectId': self.__project_id,
                'job_id': str(uuid.uuid4())
            },
            'configuration': {
                'load': {
                    'sourceUris': [source_csv_path],
                    'schema': {
                        'fields': source_schema
                    },
                    'destinationTable': {
                        'projectId': self.__project_id,
                        'datasetId': data_set_id,
                        'tableId': table_id
                    }
                }
            }
        }

    def __wait_job(self, body):
        job = self.service.jobs().insert(
            projectId=self.__project_id,
            body=body).execute(
            num_retries=self.__retry_cnt)
        job_get = self.service.jobs().get(projectId=self.__project_id, jobId=job['jobReference']['jobId'])
        while True:
            time.sleep(float(self.__interval))
            job_resource = job_get.execute(num_retries=self.__retry_cnt)
            if job_resource['status']['state'] == 'DONE':
                return job_resource

    @classmethod
    def __paging(cls, request_func, num_retries=5, **kwargs):
        has_next = True
        while has_next:
            response = request_func(**kwargs).execute(num_retries=num_retries)
            if 'pageToken' in response:
                kwargs['pageToken'] = response['pageToken']
            else:
                has_next = False
            yield response

    def __create_load_data(self, storage_path, data_set_id, table_id, source_schema, write_disposition):
        return {
            "jobReference": {
                "projectId": self.__project_id,
                "job_id": str(uuid.uuid4())
            },
            'configuration': {
                'load': {
                    'sourceUris': ["gs:" + storage_path],
                    'schema': {
                        'fields': source_schema
                    },
                    'destinationTable': {
                        'projectId': self.__project_id,
                        'datasetId': data_set_id,
                        'tableId': table_id
                    },
                    'writeDisposition': write_disposition
                }
            }
        }


class CloudStorage(AbsGoogleServices):
    def get_service_name(self):
        return 'storage'

    def get_api_version(self):
        return 'v1'

    def upload_file(self, local_file_path, bucket_name, storage_file_path):
        media = MediaFileUpload(local_file_path, resumable=True)
        request = self.service.objects().insert(bucket=bucket_name, name=storage_file_path, media_body=media)
        base_name = os.path.basename(local_file_path)
        while True:
            try:
                progress, response = request.next_chunk()
                if progress:
                    print '{0} is uploading {1}/100'.format(base_name, int(100 * progress.progress()))
                else:
                    break
            except Exception, e:
                print '{0} \'s upload is error'.format(base_name)
                print str(e)
                return False
        return True

    def download_file(self, local_file_path, bucket_name, storage_file_path):
        f = file(local_file_path, 'wb')
        request = self.service.objects().get_media(bucket=bucket_name, object=storage_file_path)
        media = MediaIoBaseDownload(f, request)
        base_name = os.path.basename(local_file_path)
        done = False
        while not done:
            try:
                progress, done = media.next_chunk()
                if progress:
                    print '{0} is download {1}/100'.format(base_name, int(100 * progress.progress()))
            except Exception, e:
                print '{0} \'s download is error'.format(base_name)
                print str(e)
                return False
        return True

    def get_list(self, bucket_name, name_prefix=None, content_type=None):
        fields_to_return = 'nextPageToken,items(name,size,contentType,metadata(my-key))'
        req = self.service.objects().list(bucket=bucket_name, fields=fields_to_return)
        item_list = []
        while req is not None:
            resp = req.execute()
            if len(resp) == 0:
                break
            for item_info in resp['items']:
                if content_type is not None:
                    if item_info['contentType'] != content_type:
                        continue
                if name_prefix is not None:
                    if item_info['name'].startswith(name_prefix) is False:
                        continue
                item_list.append(item_info)
            req = self.service.objects().list_next(req, resp)
        return item_list
