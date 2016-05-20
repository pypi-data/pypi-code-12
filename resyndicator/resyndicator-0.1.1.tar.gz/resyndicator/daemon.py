import importlib
import requests
import argparse
from time import sleep, time
from xml.sax import SAXException
from . import settings
from resyndicator.logger import logger
from resyndicator.fetchers import UnchangedException

resources = importlib.import_module(settings.RESOURCES)


def run(args):
    parser = argparse.ArgumentParser(description='Run a daemon.')
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('--fetchers', action='store_true')
    group.add_argument('--content', action='store_true')
    group.add_argument('--stream', type=int)
    args, rest = parser.parse_known_args(args)
    if args.fetchers:
        fetchers()
    elif args.content:
        content()
    else:
        stream(resources.STREAMS[args.stream])


def fetchers():
    while True:
        cycle_start = time()
        pending_feeds = (feed for feed in resources.FETCHERS
                         if feed.needs_update)
        for feed in pending_feeds:
            logger.info('Updating %s (%.2f seconds behind schedule)',
                        feed.url, time() - feed.next_check)
            try:
                feed.update()
            except (IOError, requests.RequestException) as excp:
                logger.error('Request exception %r for %s',
                             excp, feed.url)
            except SAXException as excp:
                logger.error('Parser exception %r for %s',
                             excp, feed.url)
            except UnchangedException:
                logger.info('Source unchanged')
            else:
                logger.info('Updating storage')
                fresh_entries = feed.persist()
                if fresh_entries:
                    for resyndicator in resources.RESYNDICATORS:
                        resyndicator.publish()
                        if settings.HUB:
                            resyndicator.pubsub(fresh_entries)
            feed.clean()
            feed.touch()
        sleep_time = cycle_start + settings.TIMEOUT - time()
        if sleep_time > 0:
            logger.info('Sleeping %.2f s', sleep_time)
            sleep(sleep_time)


def content():
    fetcher = resources.CONTENT_FETCHER
    while True:
        entries = fetcher.entries()
        logger.info('%s entries queued', entries.count())
        if entries.count():
            entry = entries[0]
            try:
                content, content_type = fetcher.fetch(entry)
            except (IOError, requests.RequestException) as excp:
                logger.error('Request exception %r', excp)
                content = 'Exception: {!r}'.format(excp)
                content_type = 'text'
            except SAXException as excp:
                logger.error('Parser exception %r', excp)
                content = 'Exception: {!r}'.format(excp)
                content_type = 'text'
            except Exception as excp:
                content = 'Unexpected exception: {!r}'.format(excp)
                content_type = 'text'
            finally:
                fetcher.set(entry, content, content_type)
        sleep(settings.CONTENT_FETCHER_SLEEP)


def stream(stream):
    for entries in stream.run():
        for resyndicator in resources.RESYNDICATORS:
            resyndicator.maybe_publish(entries)
