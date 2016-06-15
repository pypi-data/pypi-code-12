#!/usr/bin/python
"""
sorno_gdrive_cli.py

Dependency:
You need to install the Google Client library before using the script:
https://developers.google.com/drive/web/quickstart/quickstart-python#step_2_install_the_google_client_library

See the script description by running "sorno_gdrive_cli.py --help" for detail.
"""

import argparse
import logging
import os
import pprint
import subprocess
import sys

import apiclient
from apiclient.discovery import build
from apiclient.http import MediaFileUpload

import httplib2

from oauth2client.client import OAuth2WebServerFlow
from oauth2client.file import Storage

from sorno import logging as sorno_logging


_LOG = logging.getLogger(__name__)

# Check https://developers.google.com/drive/scopes for all available scopes
OAUTH_SCOPE = 'https://www.googleapis.com/auth/drive'

# Redirect URI for installed apps
REDIRECT_URI = 'urn:ietf:wg:oauth:2.0:oob'

CREDENTIALS_FILE = "/tmp/sorno_gdrive_cli-google-drive-api.cred"


class App(object):
    def __init__(self):
        self.drive_service = None

    def auth(self, use_credentials_cache=True):
        # Copy your credentials from the console
        client_id = os.getenv('GOOGLE_CLOUD_CLIENT_ID')
        client_secret = os.getenv('GOOGLE_CLOUD_CLIENT_SECRET')

        if not client_id:
            print("Please set the environment variable GOOGLE_CLOUD_CLIENT_ID")
            sys.exit(1)

        if not client_secret:
            print("Please set the environment variable GOOGLE_CLOUD_CLIENT_SECRET")
            sys.exit(1)

        # Run through the OAuth flow and retrieve credentials
        flow = OAuth2WebServerFlow(client_id, client_secret, OAUTH_SCOPE,
                                   redirect_uri=REDIRECT_URI)

        # Indicate we need the user to grant us permissions and give the auth code or
        # not
        need_get_code = True

        if os.path.exists(CREDENTIALS_FILE) and use_credentials_cache:
            storage = Storage(CREDENTIALS_FILE)
            credentials = storage.get()
            print("Use old credentials")
            need_get_code = False

        if need_get_code:
            authorize_url = flow.step1_get_authorize_url()
            print 'Go to the following link in your browser: ' + authorize_url
            code = raw_input('Enter verification code: ').strip()

            credentials = flow.step2_exchange(code)

            storage = Storage(CREDENTIALS_FILE)
            storage.put(credentials)

        # Create an httplib2.Http object and authorize it with our credentials
        http = httplib2.Http()
        http = credentials.authorize(http)

        self.drive_service = build('drive', 'v2', http=http)

    def upload_action(self, args):
        self.auth(args.use_credentials_cache)
        self.upload_files(args.files)

    def upload_files(self, filepaths):
        _LOG.info("Will upload files: %s" , ", ".join(filepaths))

        for filepath in filepaths:
            _LOG.info("Upload file: %s", filepath)
            media = MediaFileUpload(
                filepath,
            )

            file_title = os.path.basename(filepath)
            response = self.drive_service.files().insert(
                media_body=media,
                body={
                    'title': file_title,
                },
            ).execute()

            pprint.pprint(response)

    def download_action(self, args):
        _LOG.error("Not implemented, yet")
        sys.exit(1)


def main():
    app = App()
    args = parse_args(app, sys.argv[1:])

    sorno_logging.setup_logger(_LOG, debug=args.debug)
    args.func(args)


def parse_args(app_obj, cmd_args):
    description = """
A command line client for managing Google Drive. The API doc is in
https://developers.google.com/drive/web/quickstart/quickstart-python

Usage:

    Follow step 1 (Enable the Drive API) in
    https://developers.google.com/drive/web/quickstart/quickstart-python to
    get the client id and secret. Export them as environment variables
    "GOOGLE_CLOUD_CLIENT_ID" and "GOOGLE_CLOUD_CLIENT_SECRET" (replace "xxx"
    and "yyy" with your corresponding values:

      export GOOGLE_CLOUD_CLIENT_ID='xxx'
      export GOOGLE_CLOUD_CLIENT_SECRET='yyy'

    You probably want to put the two lines above in your bashrc file.

    Then, you can upload files by running:
        sorno_gdrive_cli.py upload <file1> [file2, file3...]
    """
    parser = argparse.ArgumentParser(
        description=description,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "--no-credentials-cache",
        dest="use_credentials_cache",
        action="store_false",
        default=True,
        help="If specified, old credentials are not reused and you have to"
            " follow the instruction from this script to get the code every"
            " time you use this script.",
    )
    parser.add_argument(
        "--debug",
        action="store_true",
    )

    subparsers = parser.add_subparsers(title="Subcommands")

    parser_upload = subparsers.add_parser("upload")
    parser_upload.add_argument(
        "files",
        nargs="+",
        help="Local filepaths for files to be uploaded",
    )
    parser_upload.set_defaults(func=app_obj.upload_action)

    parser_download = subparsers.add_parser("download")
    parser_download.set_defaults(func=app_obj.download_action)

    args = parser.parse_args(cmd_args)
    return args


if __name__ == '__main__':
    main()

