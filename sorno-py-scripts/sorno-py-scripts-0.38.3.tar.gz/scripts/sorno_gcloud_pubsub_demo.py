#!/usr/bin/env python
"""sorno_gcloud_pubsub_demo.py demos the use of Google Cloud Pub/Sub.

The script can be run as a publisher or a subscriber for a Pub/Sub topic.

You need to get the json credentials file before using this script. See https://developers.google.com/identity/protocols/application-default-credentials#howtheywork.

Quickstart:

    To run as a publisher:

        sorno_gcloud_pubsub_demo.py --google-json-credentials <your-json-credentials-file> --publisher

    To run as a subscriber:

        sorno_gcloud_pubsub_demo.py --google-json-credentials <your-json-credentials-file>  --subscriber

Reference: https://cloud.google.com/pubsub/configure

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

PUBSUB_SCOPES = ['https://www.googleapis.com/auth/pubsub']
_log = logging.getLogger()


def create_pubsub_client(http=None):
    """
    https://developers.google.com/identity/protocols/application-default-credentials#howtheywork
    """
    credentials = oauth2client.GoogleCredentials.get_application_default()
    if credentials.create_scoped_required():
        credentials = credentials.create_scoped(PUBSUB_SCOPES)
    if not http:
        http = httplib2.Http()
    credentials.authorize(http)

    return discovery.build('pubsub', 'v1', http=http)

class App(object):
    def __init__(self, args):
        self.args = args

    def run(self):
        if self.args.google_json_credentials:
            os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = (
                self.args.google_json_credentials
            )

        if self.args.publisher:
            self.run_as_publisher()
        elif self.args.subscriber:
            self.run_as_subscriber()

        return 0

    def run_as_publisher(self):
        _log.info("I am a publisher")

        client = create_pubsub_client()

        project_id = self._get_project_id()
        if not project_id:
            _log.error("Cannot find project_id, please specify --project-id")
            return
        _log.info("Project id: %s", project_id)

        full_topic_name = self._get_topic_name(project_id)
        _log.info("Full topic name: %s", full_topic_name)

        topic = None
        _log.info("Find or create topic %s...", full_topic_name)
        try:
            topic = client.projects().topics().get(topic=full_topic_name).execute()
        except googleapiclient.errors.HttpError as error:
            # error probably means the topic does not exist
            _log.debug("Error: %s", error)

        if not topic:
            topic = client.projects().topics().create(
                    name=full_topic_name,
                    body={}).execute()
            _log.info("Created: %s", topic.get('name'))

        _log.info("Topic resource: %s", topic)

        if self.args.publish_hello_message:
            message = "Hello from sorno_gcloud_pubsub_demo.py"

            message_body = {
                'messages': [
                    {'data': base64.b64encode(message)},
                ]
            }
            _log.info("Publishing message: %s", message_body)

            resp = client.projects().topics().publish(
                topic=full_topic_name, body=message_body). execute()

            _log.info("Response: %s", resp)

    def run_as_subscriber(self):
        _log.info("I am a subscriber")

        client = create_pubsub_client()

        project_id = self._get_project_id()
        if not project_id:
            _log.error("Cannot find project_id, please specify --project-id")
            return
        _log.info("Project id: %s", project_id)

        full_topic_name = self._get_topic_name(project_id)
        _log.info("Full topic name: %s", full_topic_name)

        full_subscription_name = self._get_subscription_name(project_id)
        _log.info("Full subscription name: %s", full_subscription_name)

        # Create a POST body for the Pub/Sub request
        subscription_body = {
            # The name of the topic from which this subscription receives messages
            'topic': full_topic_name,
            # Only needed if you are using push delivery
            # 'pushConfig': {
                # 'pushEndpoint': push_endpoint
            # }
        }

        subscription = None
        _log.info("Find or create subscription %s...", full_subscription_name)
        try:
            subscription = client.projects().subscriptions().get(
                subscription=full_subscription_name
            ).execute()
        except googleapiclient.errors.HttpError as error:
            # error probably means the subscription does not exist
            _log.debug("Error: %s", error)

        if not subscription:
            subscription = client.projects().subscriptions().create(
                name=full_subscription_name,
                body=subscription_body,
            ).execute()
            _log.info("Created: %s", subscription.get('name'))

        _log.info("Subscription resource: %s", subscription)

        # Create a POST body for the Pub/Sub request
        body = {
            # Setting ReturnImmediately to false instructs the API to wait
            # to collect the message up to the size of MaxEvents, or until
            # the timeout.
            'returnImmediately': False,
            'maxMessages': 1,
        }

        while True:
            _log.info("Pull one message...")
            try:
                resp = client.projects().subscriptions().pull(
                    subscription=full_subscription_name, body=body
                ).execute()
            except KeyboardInterrupt:
                break

            _log.info("Response: %s", resp)

            received_messages = resp.get('receivedMessages')
            if received_messages is not None:
                ack_ids = []
                for received_message in received_messages:
                    pubsub_message = received_message.get('message')
                    if pubsub_message:
                        # Process messages
                        _log.info(
                            "Message decoded: %s",
                            base64.b64decode(str(pubsub_message.get('data'))),
                        )
                        _log.info(
                            "Published local time: %s",
                            datetimeutil.guess_local_datetime(
                                pubsub_message.get('publishTime')
                            ).strftime("%Y-%m-%d %H:%M:%S"),
                        )
                        # Get the message's ack ID
                        ack_ids.append(received_message.get('ackId'))

                # Create a POST body for the acknowledge request
                ack_body = {'ackIds': ack_ids}

                # Acknowledge the message.
                _log.info("Ack the message")
                client.projects().subscriptions().acknowledge(
                    subscription=full_subscription_name, body=ack_body).execute()

    def _get_topic_name(self, project_id):
        topic_name = self.args.topic_name
        full_topic_name = "projects/{project_id}/topics/{topic_name}".format(
            **locals())
        return full_topic_name

    def _get_subscription_name(self, project_id):
        name = self.args.subscription_name
        full_subscription_name = "projects/{project_id}/subscriptions/{name}".format(
            **locals()
        )
        return full_subscription_name

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
        "--topic-name",
        default="sorno_gcloud_pubsub_demo_topic",
    )

    #
    # publisher-specific arguments
    #

    parser.add_argument(
        "--publisher",
        action="store_true",
        help="This script is running as the publisher of a Google Cloud Pubsub topic",
    )
    parser.add_argument(
        "--skip-publisher-hello-message",
        dest="publish_hello_message",
        action="store_false",
        default=True,
    )

    #
    # subscriber-specific arguments
    #

    parser.add_argument(
        "--subscriber",
        action="store_true",
        help="This script is running as the subscriber of a Google Cloud Pubsub topic",
    )

    parser.add_argument(
        "--subscription-name",
        default="sorno_gcloud_pubsub_demo_subscription",
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
