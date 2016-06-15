#!/usr/bin/python
"""
sorno_gdoc_cli.py

Dependency:
You need to install the Google Client library before using the script:
https://developers.google.com/drive/web/quickstart/quickstart-python#step_2_install_the_google_client_library

See the script description by running "sorno_gdoc_cli.py --help" for detail.
"""

import argparse
import os
import pprint
import subprocess
import sys

import apiclient
from apiclient.discovery import build
import httplib2
from oauth2client.client import OAuth2WebServerFlow
from oauth2client.file import Storage


# Check https://developers.google.com/drive/scopes for all available scopes
OAUTH_SCOPE = 'https://www.googleapis.com/auth/drive.readonly'

# Redirect URI for installed apps
REDIRECT_URI = 'urn:ietf:wg:oauth:2.0:oob'

CREDENTIALS_FILE = "/tmp/google-drive-api.cred"


def _main():
    args = _parse_args(sys.argv[1:])

    query = args.query
    output_file = args.output

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

    if os.path.exists(CREDENTIALS_FILE) and args.use_credentials_cache:
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

    drive_service = build('drive', 'v2', http=http)

    results = retrieve_all_files(drive_service, query)

    if not results:
        print("No results")
        sys.exit(1)
    elif len(results) != 1:
        for i, res in enumerate(results):
            print("%d: %s" % (i, res['title']))

        if args.lucky:
            chosen = 0
        else:
            chosen = int(raw_input("Choose file: "))

        chosen_file = results[chosen]
        print("Chosen: %s" % chosen_file['title'])
    else:
        chosen_file = results[0]

    pprint.pprint(chosen_file)

    print("File path: ")
    path = []
    parents = chosen_file['parents']
    while parents:
        parent = parents[0]
        parent_file = drive_service.files().get(fileId=parent['id']).execute()
        path.append(parent_file['title'])
        parents = parent_file['parents']

    path.reverse()
    path.append(chosen_file['title'])

    print(" > ".join(path))

    if args.metadata_only:
        return

    links = chosen_file.get('exportLinks')

    if not links or "text/plain" not in links:
        print("No text/plain links available")
        sys.exit(1)

    content = download_file(drive_service, links['text/plain'])

    if output_file:
        with open(output_file, "w") as f:
            f.write(content)
        print("The file content is written in [%s]" % output_file)

        if args.open_with:
            subprocess.check_call(
                args.open_with + " " + output_file,
                shell=True,
            )
    else:
        if args.open_with:
            p = subprocess.Popen(args.open_with, stdin=subprocess.PIPE, shell=True)
            p.communicate(content)
            p.wait()
        else:
            print(content)


def _parse_args(cmd_args):
    description = """
A command line client for accessing google docs. The API doc is in
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

    Then run "sorno_gdoc_cli.py <query-string>", following the instruction and you
    will get the file content.
    """
    parser = argparse.ArgumentParser(
        description=description,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    parser.add_argument(
        "query",
        help="The search query, which only applies on the titles of the files",
    )

    parser.add_argument(
        "--lucky",
        action="store_true",
        help="Choose the first result from the query without prompting",
    )

    parser.add_argument(
        "--metadata-only",
        action="store_true",
        help="Only show the metadata of the file",
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
        "--open-with",
        help="This option can be used to run the command"
        " specified with the filepath being the first command line argument"
        " to invoke the command after the file is written if --output is"
        " specified. If --output is not specified, the standard input of"
        " the process created by the command is filled with the content of"
        " the file instead."
        " Some useful commands for this option are less, vi, cat, etc."
    )

    parser.add_argument(
        "--output",
        help="Output to a file instead of printing the content of the file"
            "out",
    )

    args = parser.parse_args(cmd_args)
    return args


def download_file(service, download_url):
  """Download a file's content.

  Args:
    service: Drive API service instance.
    drive_file: Drive File instance.

  Returns:
    File's content if successful, None otherwise.
  """
  resp, content = service._http.request(download_url)
  if resp.status == 200:
      print 'Status: %s' % resp
      return content
  else:
      print 'An error occurred: %s' % resp
      return None


def retrieve_all_files(service, query):
  """Retrieve a list of File resources.

  Args:
    service: Drive API service instance.
  Returns:
    List of File resources.
  """
  result = []
  page_token = None
  while True:
      try:
          param = {'q': "title contains '%s'" % query}
          if page_token:
              param['pageToken'] = page_token
          files = service.files().list(**param).execute()

          result.extend(files['items'])
          page_token = files.get('nextPageToken')
          if not page_token:
              break
      except apiclient.errors.HttpError, error:
          print 'An error occurred: %s' % error
          break
  return result


if __name__ == '__main__':
    _main()

