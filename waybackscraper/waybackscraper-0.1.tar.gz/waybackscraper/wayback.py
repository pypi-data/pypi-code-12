# -*- coding: utf-8 -*-

import logging
import re
import asyncio
import aiohttp
from urllib.request import urlopen, Request
from urllib.error import HTTPError
from datetime import datetime
from .exceptions import ScrapeError

logger = logging.getLogger('waybackscraper')

MEMENTO_TEMPLATE = "https://web.archive.org/web/timemap/link/{url}"
MEMENTO_ARCHIVE_PAT = '^<(http://web.archive.org/web/\d+/.*)>; rel="(first\s|last\s)?memento"; datetime="(.+)",?$'
MEMENTO_DATE_FORMAT = "%a, %d %b %Y %H:%M:%S GMT"


class Archive:
    """
    A website archive on the wayback machine
    """

    def __init__(self, date, url):
        self.date = date
        self.url = url


def scrape_archives(url, scrape_function, min_date, max_date, timedelta=None, concurrency=5):
    """
    Scrape the archives of the given URL.
    The min_date and start_date parameters allow to restrict the archives to a given period.
    A minimum time delta between two archives can be specified with the timedelta parameter.
    The concurrency parameter limits the number of concurrent connections to the web archive.
    """
    # Get the list of archive available for the given url
    archives = list_archives(url)

    # Filter the archives to keep only the one between min_date and max_date and to have a minimum timedelta between
    # each archive
    archives = [archive for archive in archive_period_filter(archives, min_date, max_date, timedelta)]

    # Scrape each archives asynchronously and gather the results
    loop = asyncio.get_event_loop()
    future = asyncio.ensure_future(run_scraping(archives, scrape_function, concurrency))
    result = loop.run_until_complete(future)

    return result


async def run_scraping(archives, scrape_function, concurrency):
    """
    Run the scraping function asynchronously on the given archives.
    The concurrency parameter limits the number of concurrent connections to the web archive.
    """
    # Use a semaphore to limit the number of concurrent connections to the web archive
    sem = asyncio.Semaphore(concurrency)

    # Create scraping tasks for each archive
    tasks = [scrape_archive(archive, scrape_function, sem) for archive in archives]

    # Gather each scraping result
    responses = await asyncio.gather(*tasks)

    # Compile each valid scraping results in a dictionary
    return {response[0]: response[1] for response in responses if response[1] is not None}


async def scrape_archive(archive, scrape_function, sem):
    """
    Download the archive and run the scraping function on the archive content.
    Returns a tuple containing the scraped archive and the result of the scraping. If the scraping failed, the result
    is None
    """
    scrape_result = None

    try:
        # Limit the number of concurrent connections
        with (await sem):
            logger.info('Scraping the archive {archive_url}'.format(archive_url=archive.url))

            # Download the archive content
            async with aiohttp.ClientSession() as session:
                async with session.get(archive.url) as response:
                    response = await response.read()

                    # Scrape the archive content
                    scrape_result = scrape_function(response)

    except ScrapeError as e:
        logger.warn('Could not scrape the archive {url} : {msg}'.format(url=archive.url, msg=str(e)))
    except HTTPError as e:
        logger.warn('Could not download the archive {url} : {msg}'.format(url=archive.url, msg=str(e)))
    except Exception as e:
        logger.exception('Error while scraping the archive {url}'.format(url=archive.url, msg=str(e)))

    return archive, scrape_result


def list_archives(url):
    """
    List the available archive between min_date and max_date for the given URL
    """
    logger.info('Listing the archives for the url {url}'.format(url=url))

    # Download the memento list
    memento_list_url = MEMENTO_TEMPLATE.format(url=url)
    req = Request(memento_list_url, None, {'User-Agent': 'Mozilla/5.0'})
    memento_list = urlopen(req).read().decode("utf-8")

    # Read each line of the memento to find the archives
    lines = memento_list.split("\n")
    prog = re.compile(MEMENTO_ARCHIVE_PAT.format(url=url))
    matches = filter(None, (re.search(prog, line) for line in lines))

    # For each archive found, extract its date and url
    archive_list = [Archive(datetime.strptime(m.group(3), MEMENTO_DATE_FORMAT), m.group(1)) for m in matches]

    logger.info('Found {count} archives for the url {url}'.format(count=len(archive_list), url=url))

    return archive_list


def archive_period_filter(archive_list, min_date, max_date, timedelta):
    """
    Filter the archive to keep only the one between min_date and max_date
    Make sure there is a minimum time delta between each archive
    """
    # Sort the list of archive by their date
    archive_list.sort(key=lambda x: x.date)

    # For each archive, make sure there is a minimum of days between the archive and the previous archive in the list
    prev_date = None
    for archive in archive_list:
        if min_date <= archive.date <= max_date \
                and (prev_date is None or archive.date - prev_date > timedelta):
            yield archive
            prev_date = archive.date