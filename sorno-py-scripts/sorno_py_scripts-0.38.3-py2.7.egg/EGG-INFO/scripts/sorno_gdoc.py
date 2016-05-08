#!/Library/Frameworks/Python.framework/Versions/2.7/Resources/Python.app/Contents/MacOS/Python
"""A command line client for Google Docs.

The API doc used to implement this is in
https://developers.google.com/drive/web/quickstart/quickstart-python

You can search for a file and download its content (only if it's a doc).

In order to use this script, please look at the "Using scripts involve Google
App API" section of the sorno-py-scripts README (can be found in
https://github.com/hermantai/sorno-scripts/tree/master/sorno-py-scripts). The
API needed for this script is "Drive API" with the scope
'https://www.googleapis.com/auth/drive.readonly'


    Copyright 2014 Heung Ming Tai

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

import argparse
import os
import pprint
import re
import subprocess
import sys

from lxml import html

import apiclient
from apiclient.discovery import build
import httplib2
from oauth2client.client import OAuth2WebServerFlow
from oauth2client.file import Storage


# Check https://developers.google.com/drive/scopes for all available scopes
OAUTH_SCOPE = 'https://www.googleapis.com/auth/drive.readonly'

# Redirect URI for installed apps
REDIRECT_URI = 'urn:ietf:wg:oauth:2.0:oob'

CREDENTIALS_FILE = os.path.expanduser("~/.sorno_gdoc-google-drive-api.cred")


class App(object):
    def search_action(self, args):
        query = args.query
        output_file = args.output

        # Copy your credentials from the console
        client_id = os.getenv('GOOGLE_APP_PROJECT_CLIENT_ID')
        client_secret = os.getenv('GOOGLE_APP_PROJECT_CLIENT_SECRET')

        if not client_id:
            print(
                "Please set the environment variable"
                " GOOGLE_APP_PROJECT_CLIENT_ID")
            sys.exit(1)

        if not client_secret:
            print(
                "Please set the environment variable"
                " GOOGLE_APP_PROJECT_CLIENT_SECRET"
            )
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
            elif args.lucky_number:
                chosen = int(args.lucky_number) - 1  # from 1-based to 0-based
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

    def view_html_action(self, args):
        with open(args.file) as f:
            dom = html.fromstring(f.read())
            sections = self._get_sections(dom)

            for section in sections:
                header = section['header']
                if args.header_tag:
                    if section['tag'] in args.header_tag:
                        print(header.encode("utf8"))
                else:
                    print(header.encode("utf8"))

                if args.section_for_header_regex:
                    for header_regex in args.section_for_header_regex:
                        if re.match(header_regex, header, re.I):
                            for node in section['body']:
                                print(node.text_content())
                        break
                else:
                    for node in section['body']:
                        print(node.text_content())
        return 0

    def _get_sections(self, dom):
        sections = []
        current_section = None
        header_tags = ["h%d" % i for i in range(1, 7)]
        body = dom.xpath("//body")[0]
        for node in body:
            if node.tag in header_tags and node.text_content():
                current_section = []
                sections.append(
                    {
                        'header': node.text_content(),
                        'tag': node.tag,
                        'body': current_section,
                    }
                )
            elif current_section is not None:
                current_section.append(node)
        return sections


def main():
    app = App()
    args = parse_args(app, sys.argv[1:])
    args.func(args)


def parse_args(app_obj, cmd_args):
    description = __doc__.split("Copyright 2014")[0].strip()
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

    subparsers = parser.add_subparsers(title="Subcommands")

    parser_search = subparsers.add_parser(
        "search",
        help="Search a doc",
        description="Search a doc")

    parser_search.add_argument(
        "query",
        help="The search query, which only applies on the titles of the files",
    )

    parser_search.add_argument(
        "--lucky",
        action="store_true",
        help="Choose the first result from the query without prompting",
    )

    parser_search.add_argument(
        "--lucky-number",
        help="Choose the lucky-number'th result instead of the first without"
            " prompting",
    )

    parser_search.add_argument(
        "--metadata-only",
        action="store_true",
        help="Only show the metadata of the file",
    )

    parser_search.add_argument(
        "--open-with",
        help="This option can be used to run the command"
        " specified with the filepath being the first command line argument"
        " to invoke the command after the file is written if --output is"
        " specified. If --output is not specified, the standard input of"
        " the process created by the command is filled with the content of"
        " the file instead."
        " Some useful commands for this option are less, sed, cat, etc."
    )

    parser_search.add_argument(
        "--output",
        help="Output to a file instead of printing the content of the file"
            "out",
    )

    parser_search.set_defaults(func=app_obj.search_action)

    view_html_help = (
        "View a Google doc html file in a way that you can filter"
        " information easily"
    )
    parser_view_html = subparsers.add_parser(
        "view_html",
        description=view_html_help,
        help=view_html_help,
    )
    parser_view_html.add_argument(
        "--header-tag",
        help="HTML header tags to print out. Print out every tag if not"
        " specified.",
        action="append",
    )
    parser_view_html.add_argument(
        "--section-for-header-regex",
        help="The portion of text to print out following the header that"
        " matches one of the regex specified with this option. Default to"
        " print out everything",
        action="append",
    )
    parser_view_html.add_argument("file")
    parser_view_html.set_defaults(func=app_obj.view_html_action)

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
    main()

