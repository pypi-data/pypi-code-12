#!/usr/bin/env python
import os
import time
import json
import Queue

import click
import requests

from opbeat import Client
from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer

MAX_BACKOFF = 300


class EBAPostEventHandler(FileSystemEventHandler):

    ARCHIVE_MAGIC_NAME = " - Archive"
    errors = Queue.Queue()

    def __init__(self, archive_path, config, silent):
        self.archive_path = archive_path
        self.config = config

        if silent:
            self.opbeat_client = Client()
        else:
            self.opbeat_client = Client(
                organization_id='ef2e42e717494d91b3e7ed69c46d0415',
                app_id='3762432b73',
                secret_token='f13fd6f6e9b6998053adcb94409de0844ce80f4b',
            )

    def upload_file(self, src_file):
        config = self.config
        url = config["url"]

        click.echo("Uploading to: {}".format(url))

        try:
            r = requests.post(
                url,
                data={
                    "key": config["key"],
                    "user": config["user"],
                    "delimiter": config["delimiter"],
                    "bulk_format": config["bulk_format"],
                    "upload_type": config["upload_type"],
                    "organization": config["organization"],
                },
                files={"upload_file": open(src_file, "rb")}
            )

            click.echo("Uploaded {}".format(src_file))
            click.echo("{} {}".format(r.status_code, r.reason))

            self.archive_file(src_file)
        except Exception as e:
            message = "Upload of {} failed".format(src_file) + ". Error: %s" % e
            self.errors.put(message)
            self.opbeat_client.captureMessage(message)

    def archive_file(self, src_file):
        try:
            os.rename(
                src_file,
                os.path.join(self.archive_path, os.path.basename(src_file))
            )
            click.echo("Archived {}".format(src_file))
        except Exception as e:
            click.echo("Did not archive {}".format(src_file) + ". Error: %s" % e)
            if os.path.exists(src_file):
                try:
                    os.rename(src_file, src_file + self.ARCHIVE_MAGIC_NAME)
                except Exception as e:
                    message = "Could not rename {}".format(src_file) + ". Error: %s" % e
                    click.echo(message)
                    self.opbeat_client.captureMessage(message)

    def dispatch(self, event):
        if event.is_directory:
            return
        return super(EBAPostEventHandler, self).dispatch(event)

    def detect_file_modification(self, path, backoff_period=None):
        previous_change = os.stat(path).st_ctime
        backoff_period = backoff(backoff_period)
        current_change = os.stat(path).st_ctime

        # check that the file has not been modified since the last status change
        if current_change > previous_change:
            click.echo("Detected file modification for {}".format(path))
            click.echo("Re-checking modification in {} seconds".format(backoff_period))

            self.detect_file_modification(path, backoff_period)
        else:
            click.echo("No further file modification detected")

    def on_created(self, event):
        self.process_file(event.src_path)

    def process_file(self, src_path):
        if self.ARCHIVE_MAGIC_NAME not in src_path:
            self.detect_file_modification(src_path)
            self.upload_file(src_path)

    def reprocess_existing_files(self, watch_path):
        for file_name in os.listdir(watch_path):
            self.process_file(watch_path + "/" + file_name)


@click.command()
@click.option("--watch-path", type=click.Path(), required=True, help="path to watch")
@click.option("--archive-path", type=click.Path(), required=True, help="path to archive files to")
@click.option("--config", type=click.File(), required=True, help="JSON config file downloaded from EBAS")
@click.option("--silent", is_flag=True, required=False, help="Set this flag to not report errors to Maize")
@click.version_option()
def main(watch_path, archive_path, config, silent):
    """
    watches a folder and auto-uploads files to an EBAS node with the given
    configuration for processing
    """
    config_data = json.load(config)
    event_handler = EBAPostEventHandler(archive_path, config_data, silent)
    stop = False
    backoff_period = 1
    observer = None

    while not stop:
        try:
            error = None

            event_handler.reprocess_existing_files(watch_path)

            observer = Observer()
            observer.schedule(event_handler, watch_path, recursive=False)
            observer.start()

            while not error:
                try:
                    error = event_handler.errors.get(block=False)
                    backoff_period = restart(observer, error, backoff_period)
                except Queue.Empty:
                    time.sleep(1)
                    backoff_period = 1
        except KeyboardInterrupt:
            if observer:
                observer.stop()
                observer.join()

            stop = True
        except Exception as e:
            backoff_period = restart(observer, e, backoff_period)


def restart(observer, e, backoff_period):
    if observer:
        observer.stop()
        observer.join()

    click.echo("Error: %s" % e)
    click.echo("Retrying uploads in {} seconds".format(backoff_period))
    backoff_period = backoff(backoff_period)

    return backoff_period


def backoff(backoff_period=None):
    if backoff_period is None:
        backoff_period = 1

    # wait
    time.sleep(backoff_period)

    backoff_period *= 2

    if backoff_period > MAX_BACKOFF:
        backoff_period = MAX_BACKOFF

    return backoff_period

if __name__ == "__main__":
    main()
