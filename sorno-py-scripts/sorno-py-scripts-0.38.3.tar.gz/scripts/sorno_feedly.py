#!/usr/bin/env python
"""sorno_feedly.py manages feeds stored in Feedly.

This script does not implement an oauth flow, so just get a developer token
from https://developer.feedly.com/v3/developer to use this script.

Quickstart:

    First, get a developer access token through
    https://developer.feedly.com/v3/developer, then set the environment
    variable SORNO_FEEDLY_ACCESS_TOKEN.

        $ export SORNO_FEEDLY_ACCESS_TOKEN='YOUR ACCESS TOKEN HERE'

    Print all categories:

        $ sorno_feedly.py categories

    Print all feeds:

        $ sorno_feedly.py categories

    Print all entries, duplicated entries, and get prompted for marking
    duplicated entries to read:

        $ sorno_feedly.py entries

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
import logging
import json
import os
import sys

import requests
import six

from sorno import consoleutil
from sorno import datetimeutil
from sorno import loggingutil


ENV_VAR_FEEDLY_ACCESS_TOKEN = "SORNO_FEEDLY_ACCESS_TOKEN"

_log = logging.getLogger()
_plain_logger = None  # will be created in main()
_plain_error_logger = None  # will be created in main()


class FeedlyApp(object):
    """A console application for Feedly."""
    def __init__(self):
        self.access_token = None

    def process_args(self, parser, args):
        if args.access_token:
            self.access_token = args.access_token
        else:
            self.access_token = os.getenv(ENV_VAR_FEEDLY_ACCESS_TOKEN)

        if not self.access_token:
            # find the action of the access_token
            raise argparse.ArgumentError(
                self._find_action_from_parser(parser, "--access-token"),
                "Either specify your access token through --access-token"
                    " or set the environment variable " +
                    ENV_VAR_FEEDLY_ACCESS_TOKEN,
            )

    def _find_action_from_parser(self, parser, *option):
        s = "/".join(option)
        for action in parser._actions:
            if "--access-token" == argparse._get_action_name(action):
                return action
        return None

    def categories_action(self, args):
        """Prints out all the categories"""
        categories = self.get_categories()
        categories.sort(key=lambda c: c['label'].lower())
        for category in categories:
            print("Label:", category['label'])
            print("Id:", category['id'])
            print("Description:", category.get('description'))
            print("")
        return 0

    def get_categories(self):
        endpoint = self._get_endpoint("/categories")
        headers = self._get_headers()
        resp = requests.get(endpoint, headers=headers)
        _log.debug("Response: %s", resp.__dict__)

        return json.loads(resp.text)

    def feeds_action(self, args):
        self.feeds()
        return 0

    def feeds(self):
        """Prints out all the feeds"""
        endpoint = self._get_endpoint("/subscriptions")
        headers = self._get_headers()
        resp = requests.get(endpoint, headers=headers)
        _log.debug("Response: %s", resp.__dict__)

        result = json.loads(resp.text)
        for feed in result:
            id_line = "Id: %s" % feed['id']
            if "state" in feed:
                id_line += " (State: %s)" % feed["state"]
            print(id_line)
            print("Website:", feed.get('website'))
            print(
                "Categories:",
                ", ".join([c['label'] for c in feed['categories']]),
            )
            print("")

    def entries_action(self, args):
        self.entries(do_cleanup=args.do_cleanup)
        return 0

    def entries(self, do_cleanup=False):
        """Prints out all the entries for all the feeds"""
        _log.debug("Get all the category ids first")
        categories = self.get_categories()

        duplicated_entries = []
        seen_fingerprints = set()
        total_num_entries = 0

        endpoint = self._get_endpoint("/streams/contents")
        for category in categories:
            headers = self._get_headers()
            params = {
                'streamId': category['id'],
                'count': 1000,  # max is 1000
                'unreadOnly': "true"
            }
            resp = requests.get(endpoint, headers=headers, params=params)
            _log.debug("Response: %s", resp.__dict__)

            content = json.loads(resp.text)
            #from sorno import debuggingutil
            #debuggingutil.ipython_here()

            title = None
            if 'title' in content:
                title = content['title']
            else:
                title = content['id']
                if '/' in title:
                    title = title.split('/')[-1]

            print("Title:", title)
            updated = datetimeutil.timestamp_to_local_datetime(
                content['updated'] / 1000
            )
            print("Updated:", updated.strftime("%Y/%m/%d %H:%M"))
            print("Id:", content['id'])
            if 'items' in content:
                num_entries = len(content['items'])
                total_num_entries += num_entries
                for i, entry in enumerate(content['items']):
                    print(" " * 4 + "(%d/%d)" % (i + 1, num_entries))
                    self._print_entry(entry, indent=" " * 4)
                    print("")

                    if entry['fingerprint'] in seen_fingerprints:
                        duplicated_entries.append(entry)
                    else:
                        seen_fingerprints.add(entry['fingerprint'])

        print("\nTotal of %d entries\n" % total_num_entries)

        print("Duplicated entries:")
        num_entries = len(duplicated_entries)
        for i, duplicated_entry in enumerate(duplicated_entries):
            print(" " * 4 + "(%d/%d)" % (i + 1, num_entries))
            self._print_entry(duplicated_entry, indent=" " * 4)
            print("")

        if num_entries == 0:
            print("None")
        elif do_cleanup:
            ans = consoleutil.confirm(
                "Mark %d duplicated entries as read?" % num_entries)
            if ans:
                resp = self.mark_entries_as_read(
                    [entry['id'] for entry in duplicated_entries]
                )

                if resp.status_code == 200:
                    print("Done")
                else:
                    print(resp.status_code, resp.reason)

    def mark_entries_as_read(self, entry_ids):
        endpoint = self._get_endpoint("/markers")
        headers = self._get_headers_for_json_input()
        params = {
            'type': "entries",
            'entryIds': entry_ids,
            'action': "markAsRead",
        }
        resp = requests.post(endpoint, headers=headers, data=json.dumps(params))
        _log.debug("Response: %s", resp.__dict__)

        return resp

    def _print_entry(self, entry, indent=""):
        print(indent + "Title:", entry['title'].encode('utf8'))
        if 'updated' not in entry:
            entry['updated'] = entry['published']

        updated = datetimeutil.timestamp_to_local_datetime(
            entry['updated'] / 1000
        )
        print(
            indent + "Updated:",
            updated.strftime("%Y/%m/%d %H:%M"),
        )
        published = datetimeutil.timestamp_to_local_datetime(
            entry['published'] / 1000
        )
        print(
            indent + "Published:",
            published.strftime("%Y/%m/%d %H:%M"),
        )
        crawled = datetimeutil.timestamp_to_local_datetime(
            entry['crawled'] / 1000
        )
        print(
            indent + "Crawled:",
            crawled.strftime("%Y/%m/%d %H:%M"),
        )
        origin = self._get_null_safe(entry, 'origin', 'title')
        if origin:
            origin = origin.encode("utf8")
        print(indent + "Origin:", origin)
        print(
            indent + "Source:",
            self._get_null_safe(entry, 'alternate', 'href'),
        )
        print(indent + "Fingerprint:", entry['fingerprint'])
        print(indent + "Id:", entry['id'])

    def _get_endpoint(self, path):
        return "https://cloud.feedly.com/v3" + path

    def _get_headers(self):
        return {'Authorization': 'OAuth ' + self.access_token}

    def _get_headers_for_json_input(self):
        headers = self._get_headers()
        headers['content-type'] = "application/json"
        return headers

    def _get_null_safe(self, mixed, *keys):
        val = mixed
        for key in keys:
            if val is None:
                return val

            if type(val) is dict:
                val = val.get(key)
            elif type(val) is list:
                if type(key) in six.integer_types:
                    if key < len(val):
                        val = val[key]
                    else:
                        val = None
                else:
                    new_val = None
                    for item in val:
                        new_val = self._get_null_safe(item, key)
                        if new_val is not None:
                            break
                    val = new_val

        return val


def parse_args(app_obj, cmd_args):
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
        "--access-token",
        help="Feedly access token. You can get a developer access token from"
            " https://developer.feedly.com/v3/developer/. You have to specify"
            " this option or set the environment variable " +
            ENV_VAR_FEEDLY_ACCESS_TOKEN,
    )

    subparsers = parser.add_subparsers(
        title="Subcommands",
        description="Some description for subcommands",
    )

    parser_categories = subparsers.add_parser(
        "categories",
        help="Print out all categories",
        description="Print out all categories",
    )
    parser_categories.set_defaults(func=app_obj.categories_action)

    parser_feeds = subparsers.add_parser(
        "feeds",
        help="Print out all feeds",
        description="Print out all feeds",
    )
    parser_feeds.set_defaults(func=app_obj.feeds_action)

    parser_entries = subparsers.add_parser(
        "entries",
        help="Print out all entries for each category",
        description="Print out all entries for each category",
    )
    parser_entries.add_argument(
        "--skip-cleanup",
        action="store_false",
        default=True,
        dest="do_cleanup",
        help="Skip the prompt for marking entries as read",
    )
    parser_entries.set_defaults(func=app_obj.entries_action)

    args = parser.parse_args(cmd_args)
    return parser, args


def main():
    global _plain_logger, _plain_error_logger

    app = FeedlyApp()
    parser, args = parse_args(app, sys.argv[1:])

    loggingutil.setup_logger(_log, debug=args.debug)
    if not args.debug:
        # suppress noisy modules
        _log.getChild("requests").setLevel(logging.WARN)

    _plain_logger = loggingutil.create_plain_logger(
        "PLAIN",
        debug=args.debug,
    )
    _plain_error_logger = loggingutil.create_plain_logger(
        "PLAIN_ERROR",
        debug=args.debug,
        stdout=False,
    )

    app.process_args(parser, args)
    code = args.func(args)
    if code is not None:
        sys.exit(code)


if __name__ == '__main__':
    main()
