#!/usr/bin/env python
"""sorno_cloud_vision.py makes using the Google Cloud Vision API easier.

Doc: https://cloud.google.com/vision/docs

The script generates requests for the given photos, sends the requests to Cloud
Vision, then puts the results into the corresponding response files.

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
import httplib2
import json
import logging
import os
import sys

from apiclient import discovery
from oauth2client import client as oauthclient

from sorno import loggingutil


_log = logging.getLogger()
_plain_logger = None  # will be created in main()
_plain_error_logger = None  # will be created in main()


class CloudVisionApp(object):
    """A console application to do work"""
    def __init__(
        self,
        args,
    ):
        """
        Args:
            args (argparse.Namespace): The flags for the script.
        """
        self.args = args
        self.http = None
        # Endpoint for accessing the cloud vision api with api key
        self.endpoint = None
        # Google api client
        self.service = None

    def run(self):
        use_api_key = False

        self.http = httplib2.Http()

        if self.args.api_key:
            self.endpoint = (
                "https://vision.googleapis.com/v1/images:annotate?key=" +
                    self.args.api_key
            )
            use_api_key = True

        if not use_api_key:
            if not os.getenv("GOOGLE_APPLICATION_CREDENTIALS"):
                _plain_error_logger.fatal(
                    "You need to specify --api-key or set the"
                    " environment variable GOOGLE_APPLICATION_CREDENTIALS."
                    " See https://cloud.google.com/vision/docs/getting-started."
                )
                sys.exit(1)

            credentials = oauthclient.GoogleCredentials.get_application_default(
            ).create_scoped(
                 ['https://www.googleapis.com/auth/cloud-platform']
            )
            credentials.authorize(self.http)

            api_discovery_file = (
                'https://vision.googleapis.com/$discovery/rest?version=v1'
            )
            self.service = discovery.build(
                'vision',
                'v1',
                http=self.http,
                discoveryServiceUrl=api_discovery_file,
            )

        for f in self.args.files:
            _log.info("Process photo: %s", f)
            with open(f, "rb") as image:
                image_content = base64.b64encode(image.read())
                if use_api_key:
                    resp_content = self._process_with_api_key(image_content)
                else:
                    resp_content = self._process_with_credentials(image_content)
                output_filepath = f + ".output.txt"
                _log.info("Writing output for %s to %s", f, output_filepath)
                with open(output_filepath, "w") as output:
                    output.write(
                        resp_content.decode("unicode-escape").encode("utf8")
                    )

        return 0

    def _process_with_api_key(self, image_content):
        service_request_json = json.dumps(
            self._create_request_body(image_content)
        )
        if self.args.debug:
            self._write_request_for_debug(service_request_json)

        (resp, content) = self.http.request(
            self.endpoint,
            "POST",
            headers={
                'Content-Type': "application/json",
            },
            body=service_request_json,
        )
        _log.info("Response: %s", resp)
        return content

    def _process_with_credentials(self, image_content):
        request = self._create_request_body(image_content)
        if self.args.debug:
            self._write_request_for_debug(json.dumps(request, indent=4))

        client_request = self.service.images().annotate(body=request)

        response = client_request.execute()
        return json.dumps(response, indent=4)

    def _write_request_for_debug(self, request_json):
        request_filepath = "cloud-vision-request.json"
        _log.info("Writing request to %s", request_filepath)
        with open(request_filepath, "w") as f:
            f.write(request_json)

    def _create_request_body(self, image_content):
        return {
            'requests': [
                {
                    'image': {
                        'content': image_content
                    },
                    'features': [
                        {
                            'type': "LABEL_DETECTION",
                            "maxResults": 20,
                        },
                        {
                            'type': "TEXT_DETECTION",
                            "maxResults": 5,
                        },
                        # {
                        #     'type': "FACE_DETECTION",
                        #     "maxResults": 10,
                        # },
                        {
                            'type': "LANDMARK_DETECTION",
                            "maxResults": 3,
                        },
                        {
                            'type': "LOGO_DETECTION",
                            "maxResults": 5,
                        },
                        {
                            'type': "SAFE_SEARCH_DETECTION",
                            "maxResults": 10,
                        },
                        # {
                        #     'type': "IMAGE_PROPERTIES",
                        #     "maxResults": 10,
                        # },
                    ]
                },
            ]
        }


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
        "--api-key",
    )

    parser.add_argument(
        "files",
        metavar='file',
        nargs="+",
    )

    args = parser.parse_args(cmd_args)
    return args


def main():
    global _plain_logger, _plain_error_logger

    args = parse_args(sys.argv[1:])

    loggingutil.setup_logger(_log, debug=args.debug)
    _plain_logger = loggingutil.create_plain_logger(
        "PLAIN",
        debug=args.debug,
    )
    _plain_error_logger = loggingutil.create_plain_logger(
        "PLAIN_ERROR",
        debug=args.debug,
        stdout=False,
    )

    app = CloudVisionApp(
        args,
    )
    sys.exit(app.run())


if __name__ == '__main__':
    main()

