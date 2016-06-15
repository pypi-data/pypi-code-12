#!/Library/Frameworks/Python.framework/Versions/2.7/Resources/Python.app/Contents/MacOS/Python
"""sorno_gcloud_bigquery.py demos the use of Google Cloud BigQuery

The script can be run to get the result of a query.

You need to get the json credentials file before using this script. See https://developers.google.com/identity/protocols/application-default-credentials#howtheywork.

Quickstart:

    sorno_gcloud_bigquery.py --google-json-credentials <your-json-credentials-file> "SELECT author,text FROM [bigquery-public-data:hacker_news.comments] where text is not null LIMIT 10"

Reference: https://cloud.google.com/bigquery/create-simple-app-api#authorizing

    Copyright 2016 Heung Ming Tai

    Licensed under the Apache License, Version 2.0 (the "License");
    you may not use this file except in compliance with the License.
    You may obtain a copy of the License at

        http://www.apache.org/licenses/LICENSE-2.0

    Unless required by applicable law or agreed to in writing, software
    distributed under the License is distributed on an "AS IS" BASIS,
    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
    See the License for the specific language governing permissions and
    limitations under the License.
"""
from __future__ import print_function
from __future__ import absolute_import
from __future__ import division
from __future__ import unicode_literals

import argparse
import base64
import json
import logging
import os

import sys

import httplib2

from apiclient import discovery
from oauth2client import client as oauth2client
import googleapiclient

from sorno import loggingutil
from sorno import datetimeutil

BIGQUERY_SCOPES = ['https://www.googleapis.com/auth/cloud-platform']
_log = logging.getLogger()


def create_bigquery_client(http=None):
    """
    https://developers.google.com/identity/protocols/application-default-credentials#howtheywork
    """
    credentials = oauth2client.GoogleCredentials.get_application_default()
    credentials = credentials.create_scoped(BIGQUERY_SCOPES)
    if not http:
        http = httplib2.Http()
    credentials.authorize(http)

    return discovery.build('bigquery', 'v2', http=http)

class App(object):
    def __init__(self, args):
        self.args = args

    def run(self):
        if self.args.google_json_credentials:
            os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = (
                self.args.google_json_credentials
            )

        client = create_bigquery_client()
        project_id = self._get_project_id()

        query_request = client.jobs()
        query_data = {
            'query': self.args.query
        }
        query_response = query_request.query(
            projectId=project_id,
            body=query_data).execute()

        for row in query_response['rows']:
            print(row)

        return 0

    def _get_project_id(self):
        project_id = self.args.project_id
        if not project_id:
            # try to get it from credentials
            credentials_filename = oauth2client._get_environment_variable_file()
            if not credentials_filename:
                credentials_filename = oauth2client._get_well_known_file()

            if credentials_filename:
                with open(credentials_filename) as file_obj:
                    client_credentials = json.load(file_obj)
                    project_id = client_credentials['project_id']
        return project_id


def parse_args(cmd_args):
    description = __doc__.split("Copyright 2016")[0].strip()

    parser = argparse.ArgumentParser(
        description=description,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "--debug",
        action="store_true",
    )
    parser.add_argument(
        "--google-json-credentials",
        help="Path to the google json credentials file. See https://developers.google.com/identity/protocols/application-default-credentials#howtheywork",
    )
    parser.add_argument(
        "--project-id",
    )
    parser.add_argument(
        "query",
    )

    args = parser.parse_args(cmd_args)
    return args


def main():
    args = parse_args(sys.argv[1:])
    loggingutil.setup_logger(_log, debug=args.debug)

    app = App(args)
    sys.exit(app.run())


if __name__ == '__main__':
    main()
