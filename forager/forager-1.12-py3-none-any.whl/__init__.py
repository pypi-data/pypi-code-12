# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from builtins import object

import itertools
import logging
import re
import requests
import time

from bs4 import BeautifulSoup
from collections import namedtuple
from datetime import datetime, timedelta
from future.moves.urllib.parse import urlparse, urljoin
from future.utils import iteritems

from forager import exceptions

REQUEST_DELAY = timedelta(microseconds=200000)
REQUEST_TIMEOUT = 5
USER_AGENT = 'Forager Feed Finder'

# A default of 1 means that if the base url is html, we will search it for possible feeds
# Passing max_depth of 0 to find_feeds means we will only return a url if the base url itself is a feed
MAX_DEPTH = 1

logger = logging.getLogger(__name__)


def find_feeds(url, max_depth=MAX_DEPTH):
    return Forager(max_depth=max_depth).find_feeds(url)


def find_xmlrpc(url, soup_meta_filters=None):
    return Forager().find_xmlrpc(url, soup_meta_filters=soup_meta_filters)


FetchResult = namedtuple('FetchResult', ['soup', 'url'])


def _domains_base_url(url):
    url_parts = urlparse(url)

    return "{scheme}://{domain}/".format(
        scheme=url_parts.scheme,
        domain=url_parts.netloc
    )


class Forager(object):
    def __init__(self,
                 max_depth=MAX_DEPTH,
                 user_agent=USER_AGENT,
                 request_delay=REQUEST_DELAY,
                 request_timeout=REQUEST_TIMEOUT,
                 auths=None,
                 raise_to_depth=None):
        self._max_depth = max_depth
        self._user_agent = user_agent
        self._request_delay = request_delay
        self._request_timeout = request_timeout
        self._auths = auths or {}
        self._raise_to_depth = raise_to_depth if raise_to_depth is not None else -1
        self._request_previous = datetime.now() - (self._request_delay * 2)
        self._seen_urls = set()

    def find_feeds(self, url):
        url = self._fix_url(url)

        found_feeds = set()

        found_feeds.update(self._find_feeds_worker(url))

        for predicted_url in self._predicted_urls(url):
            found_feeds.update(self._find_feeds_worker(predicted_url))

        return found_feeds

    def find_xmlrpc(self, url, soup_meta_filters=None):
        url = self._fix_url(url)

        try:
            if self._is_xmlrpc(url):
                return self._find_apis(
                    self._apply_rsd_query_param(url),
                    soup_meta_filters
                )
        except requests.RequestException:
            pass

        soup = self._fetch_and_parse(url).soup
        if not soup:
            return set()

        rsd_urls = self._find_rsds(soup)

        rsd_urls.add(_domains_base_url(url) + 'rsd.xml')

        found_endpoints = set()

        for rsd_url in rsd_urls:
            try:
                found_endpoints.update(self._find_apis(rsd_url, soup_meta_filters))
            except requests.RequestException:
                pass

        return found_endpoints

    @staticmethod
    def _find_rsds(soup):
        rpc_urls = itertools.chain(
            soup.findAll('link', rel='EditURI'),
            soup.findAll('link', type='application/rsd+xml')
        )

        rpc_urls = {rpc_url['href'] for rpc_url in rpc_urls if rpc_url.get('href')}

        return rpc_urls

    def _find_apis(self, url, soup_meta_filters=None):
        soup_meta_filters = soup_meta_filters or {}

        soup = self._fetch_and_parse(url, ignore_fetch_history=True).soup
        if not soup:
            return set()

        try:
            apis = soup.findChild('rsd') \
                .findChild('service') \
                .findChild('apis') \
                .findChildren('api', soup_meta_filters)
            return set(api.attrs['apilink'] for api in apis if 'apilink' in api.attrs)
        except AttributeError:
            return set()

    @staticmethod
    def _apply_rsd_query_param(url):
        url_parts = urlparse(url)

        return "{}://{}{}?rsd".format(url_parts.scheme, url_parts.netloc, url_parts.path)

    def _is_xmlrpc(self, url):
        url = self._apply_rsd_query_param(url)

        soup, _ = self._fetch_and_parse(url)
        if not soup:
            return False

        return bool(soup.findAll('rsd'))

    def _find_feeds_worker(self, url, curr_depth=0, soup=None):
        try:
            soup, url = self._fetch_and_parse(url)
        except (requests.RequestException, exceptions.ForagerException):
            if curr_depth <= self._raise_to_depth:
                raise

        if not soup:
            return set()

        if Forager._soup_contains_feed(soup):
            return {url}

        if not Forager._soup_contains_html(soup):
            return set()

        links_to_crawl = self._get_relevant_links(soup, curr_depth)

        found_feeds = set()

        for new_url in links_to_crawl:
            new_url = urljoin(url, new_url)
            new_url = self._fix_url(new_url)
            found_feeds.update(self._find_feeds_worker(new_url, curr_depth=curr_depth + 1))

        return found_feeds

    def _get_relevant_links(self, soup, curr_depth):
        def _find_linked_resources_to_crawl():
            return curr_depth < self._max_depth

        def _find_linked_feeds_to_crawl():
            return curr_depth < (self._max_depth - 1)

        links_to_crawl = set()

        if _find_linked_resources_to_crawl():
            links_to_crawl.update(Forager._find_feed_hrefs(soup))

        if _find_linked_feeds_to_crawl():
            links_to_crawl.update(Forager._find_all_hrefs(soup))

        return links_to_crawl

    def _fetch_and_parse(self, url, ignore_fetch_history=False):
        if url in self._seen_urls and not ignore_fetch_history:
            return FetchResult(None, url)

        response = self._requests_get(url)

        if response.status_code == 401:
            raise exceptions.Unauthorized(response)

        if response.status_code == 403:
            raise exceptions.Forbidden(response)

        self._seen_urls.add(url)

        soup = BeautifulSoup(response.text, 'html.parser')

        return FetchResult(soup, response.url)

    @staticmethod
    def _fix_url(url):
        def _schemify(domain):
            return 'http://{}'.format(domain)

        if url.startswith('http://') or url.startswith('https://'):
            corrected_url = url

        elif url.startswith('feed://'):
            corrected_url = _schemify(url[7:])

        else:
            corrected_url = _schemify(url)

        return corrected_url

    @staticmethod
    def _predicted_urls(url):
        domain = urlparse(url).netloc
        return {
            'http://{}/rss/'.format(domain),
            'http://{}/feeds/'.format(domain),
            'http://{}/feed/'.format(domain)
        }

    def _ratelimit(self):
        delay = self._request_delay - (datetime.now() - self._request_previous)
        delay = delay.total_seconds()
        time.sleep(delay if delay > 0 else 0)
        self._request_previous = datetime.now()

    def _find_auth_for_url(self, url):
        # Try first by matching the URL directly
        url_auth = self._auths.get(url)
        if url_auth:
            return url_auth

        # Try again by matching the domain directly
        url_auth = self._auths.get(urlparse(url).netloc)
        if url_auth:
            return url_auth

        # Finally, try matching with regex. Return the first match if > 1
        re_matches = [auth_method for pattern, auth_method in iteritems(self._auths) if re.match(pattern, url)]
        if re_matches:
            return re_matches[0]

        return None

    def _requests_get(self, url):
        self._ratelimit()

        request_kwargs = {
            'headers': {'User-Agent': self._user_agent},
            'timeout': self._request_timeout,
            'verify': False
        }

        auth_for_url = self._find_auth_for_url(url)

        if auth_for_url:
            request_kwargs['auth'] = auth_for_url

        return requests.get(url, **request_kwargs)

    @staticmethod
    def _url_looks_feedish(url):
        hints = ['atom', 'feed', 'rss', 'rdf', 'xml']
        return any(hint in url for hint in hints)

    @staticmethod
    def _url_looks_irrelevant(url):
        extensions = ['css', 'jpg', 'js', 'gif', 'jpeg', 'png', 'ico']
        hints = [r'.*?\.{}'.format(ext) for ext in extensions]
        hints.append('^.*?mailto:.*@.*$')
        hints.append('^javascript:.*$')
        return any([re.match(pat, url) for pat in hints])

    @staticmethod
    def _type_is_feedish(link_type):
        feed_types = [
            'application/rss+xml',
            'text/xml',
            'application/atom+xml',
            'application/x.atom+xml',
            'application/x-atom+xml'
        ]
        return any([feed_type == link_type for feed_type in feed_types])

    @staticmethod
    def _find_resources(soup):
        return {
            resource
            for resource
            in soup.findAll(['link', 'a'])
            if resource.get('href')
            }

    @staticmethod
    def _find_all_hrefs(soup):
        return {
            resource.get('href')
            for resource
            in Forager._find_resources(soup)
            if not Forager._url_looks_irrelevant(resource.get('href'))
            }

    @staticmethod
    def _find_feed_hrefs(soup):
        return {
            resource.get('href')
            for resource
            in Forager._find_resources(soup)
            if Forager._type_is_feedish(resource.get('type')) or Forager._url_looks_feedish(resource.get('href'))
            }

    @staticmethod
    def _soup_contains_html(soup):
        return bool(soup.findAll('html'))

    @staticmethod
    def _soup_contains_feed(soup):
        return bool(
                soup.findAll('rss') or
                soup.findAll('rdf') or soup.findAll('rdf:rdf') or
                soup.findAll('feed')
        )
