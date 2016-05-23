import json
import socket
import time
import feedparser
import requests
from functools import wraps
from html.parser import HTMLParser
from operator import attrgetter, itemgetter
from random import randrange
from datetime import datetime
from sqlalchemy.sql import or_
from twython import Twython, TwythonStreamer
from dateutil.parser import parse as parse_date
from dateutil.tz import tzutc
from readability import Document
from utilofies.bslib import intelligent_decode
from utilofies.stdlib import canonicalized
from . import settings
from .logger import logger
from .utils import urn_from_string, sub_slices, itertimeout, lgroupby
from .models import Session, Entry
from .sitemapparser import SitemapIndex, Sitemap

# In accordance with
# https://dev.twitter.com/docs/streaming-apis/connecting#Stalls
socket.setdefaulttimeout(90)

unescape = HTMLParser().unescape


def stopwatch(func):
    @wraps(func)
    def wrapper(self, *args, **kwargs):
        start = time.time()
        results = func(self, *args, **kwargs)
        logger.info('%r executed in %s', func, time.time() - start)
        return results
    return wrapper


def process_time(raw_date, default=None, default_tz=tzutc):
    if not raw_date:
        return default
    if type(raw_date) != time.struct_time:
        try:
            date = parse_date(raw_date)
        except (ValueError, AttributeError):
            return default
    else:
        date = datetime.fromtimestamp(time.mktime(raw_date))
    if date.tzinfo is None and default_tz is not None:
        date = date.replace(tzinfo=default_tz())
    return date.astimezone(tzutc()).replace(tzinfo=None)


def decode_response(response):
    if not 'charset' in response.headers.get('content-type', '').lower():
        # Reset default encoding
        # http://www.w3.org/International/O-HTTP-charset.en.php
        response.encoding = None
    dammit = intelligent_decode(
        markup=response.content, override_encodings=(response.encoding,))
    return dammit.unicode_markup


class UnchangedException(Exception):
    pass


class ContentFetcher(object):

    def __init__(self, past=None, **kwargs):
        self.past = past
        self.kwargs = kwargs
        self.session = Session()

    def entries(self):  # Not a property to discourage redundant querying
        # Sorted newest first so that if content vanishes we at least get to
        # fetch some of it. Minimal risk rather than all or nothing.
        query = self.session.query(Entry) \
            .filter(or_(Entry.content==None, Entry.content==''),
                    Entry.link!=None)
        if self.past:
            query = query.filter(Entry.updated > datetime.utcnow() - self.past)
        return query.order_by(Entry.updated.desc())

    def fetch(self, entry):
        logger.info('Fetching %s', entry.link)
        response = requests.get(entry.link, **self.kwargs)
        response.raise_for_status()
        html = decode_response(response)
        return Document(html, url=response.url).summary(), 'html'

    def set(self, entry, content, content_type='html'):
        if not content.strip():
            content = 'No content'
            content_type = 'text'
        entry.content = content
        entry.content_type = content_type
        self.session.commit()


class BaseEntryInterface(object):

    def __init__(self, fetcher, raw_entry):
        self.fetcher = fetcher
        self.raw_entry = raw_entry

    @property
    def summary(self):
        pass

    @property
    def summary_type(self):
        pass

    @property
    def content(self):
        pass

    @property
    def content_type(self):
        pass

    @property
    def source(self):
        pass

    @property
    def id(self):
        pass

    @property
    def title(self):
        pass

    @property
    def updated(self):
        pass

    @property
    def published(self):
        pass

    @property
    def link(self):
        pass

    @property
    def author(self):
        pass

    @property
    def entry(self):
        summary, summary_type = self.summary, self.summary_type
        content, content_type = self.content, self.content_type
        if settings.INCLUDE_SOURCE:
            if content:
                content = '{}\n\n{}'.format(content, self.source)
                content_type = 'html'
            else:
                # It is recommended that summary be nonempty
                # if there is no content. This is also useful
                # for the separate content fetching.
                summary = '{}\n\n{}'.format(summary, self.source)
                summary_type = 'html'
        return Entry(
            id=self.id,
            title=self.title or self.fetcher.title,
            updated=self.updated or datetime.utcnow(),
            published=self.published,
            link=self.link or self.fetcher.link or self.fetcher.url,
            summary=summary,
            summary_type=summary_type,
            content=content,
            content_type=content_type,
            author=self.author or self.fetcher.author,
            source_id=self.fetcher.id,
            source_title=self.fetcher.title,
            source_link=self.fetcher.url)


class BaseFetcher(object):

    type_mapping = {
        'text/plain': 'text',
        'text/html': 'html',
        'application/xhtml+xml': 'xhtml'}

    def __init__(self, url, interval, default_tz=tzutc, defaults=None,
                 update_existing=False, **kwargs):
        self.defaults = defaults or {}
        self.url = url
        # Fuzziness to spread updates out more evenly
        self.interval = interval - randrange(interval // 10 + 1)
        self.last_check = time.time() + self.interval
        self.default_tz = default_tz
        self.update_existing = update_existing
        self.kwargs = kwargs
        self.kwargs.setdefault('headers', {})
        self.kwargs['headers'].setdefault('user-agent', settings.USER_AGENT)
        self.kwargs.setdefault('timeout', settings.TIMEOUT)
        self.response_headers = {}

    def __hash__(self):
        return hash(self.url)

    def retrieve(self):
        self.kwargs['headers'].update(canonicalized({
            'if-modified-since': self.response_headers.get('last-modified'),
            'if-none-match': self.response_headers.get('etag')}))
        response = requests.get(self.url, **self.kwargs)
        response.raise_for_status()
        if response.url != self.url:
            logger.info('Redirects to %s', response.url)
        self.response_headers = response.headers
        if response.status_code == 304:
            raise UnchangedException
        return response

    def parse(self, response):
        raise NotImplementedError()

    @property
    def needs_update(self):
        return self.next_check < time.time()

    @property
    def next_check(self):
        return self.last_check + self.interval

    def touch(self):
        self.last_check = time.time()

    def clean(self):
        self.source = None
        self.raw_entries = None

    @property
    def id(self):
        pass

    @property
    def title(self):
        pass

    @property
    def subtitle(self):
        pass

    @property
    def link(self):
        pass

    @property
    def hub(self):
        pass

    @property
    def author(self):
        pass

    @property
    def generator(self):
        pass

    @property
    def entries(self):
        for raw_entry in self.raw_entries:
            entry = self.EntryInterface(
                fetcher=self, raw_entry=raw_entry).entry
            yield entry

    def persist(self):
        entries = sorted(self.entries, key=attrgetter('id'))
        if not entries:
            logger.warn('Feed seems empty')
            return
        session = Session()
        # Removing duplicates from feed
        nub = [(key, len(value), value[0])
               for key, value
               in lgroupby(entries, attrgetter('id'))]
        entries = list(zip(*nub))[2]
        for id_, count, entry in nub:
            if count > 1:
                logger.warn('Removed duplicate entry: %s', entry)
        # Removing known entries
        existing_ids = list(map(
            itemgetter(0),
            session.query(Entry.id)
                .filter(Entry.id.in_(map(attrgetter('id'), entries)))))
        fresh_entries = [entry for entry in entries
                         if entry.id not in existing_ids]
        if not self.update_existing:  # Don't update by default
            entries = fresh_entries
        try:
            if self.update_existing:
                for entry in entries:
                    session.merge(entry)
            else:
                for entry in entries:
                    session.add(entry)
            session.commit()
        except:
            session.rollback()
            raise
        if fresh_entries:
            logger.info('%s new entries', len(fresh_entries))
        return fresh_entries


################################ Sitemaps ################################


class SitemapEntryInterface(BaseEntryInterface):

    @property
    def source(self):
        return ('<details>\n'
                '<summary>JSON Source</summary>\n'
                '<div class="entry-source">{}</div>\n'
                '</details>').format(json.dumps(
                    self.raw_entry, indent=4, sort_keys=True, default=unicode))

    @property
    def id(self):
        return urn_from_string(self.raw_entry['loc'])

    @property
    def updated(self):
        return process_time(self.raw_entry.get('lastmod')
                or self.raw_entry.get('video', {}).get('publication_date')
                or self.raw_entry.get('news', {}).get('publication_date'),
            default_tz=self.fetcher.default_tz)

    @property
    def link(self):
        return self.raw_entry['loc']


class SitemapFetcher(BaseFetcher):

    EntryInterface = SitemapEntryInterface

    @staticmethod
    @stopwatch
    def parse(response):
        return Sitemap(response.content)

    def update(self):
        response = self.retrieve()
        self.raw_entries = self.parse(response)

    @property
    def id(self):
        return urn_from_string(self.url)

    @property
    def title(self):
        return self.defaults.get('title')

    @property
    def author(self):
        return self.defaults.get('author')


class SitemapIndexFetcher(BaseFetcher):

    EntryInterface = SitemapEntryInterface

    def __init__(self, *args, **kwargs):
        super(SitemapIndexFetcher, self).__init__(*args, **kwargs)
        self.response_headers = {}

    @stopwatch
    def parse(self, response):
        return SitemapIndex(response.content)

    def clean(self):
        self.index = None

    def update(self):
        response = self.retrieve()
        self.index = self.parse(response)

    @property
    def id(self):
        return urn_from_string(self.url)

    @property
    def title(self):
        return self.defaults.get('title')

    @property
    def author(self):
        return self.defaults.get('author')

    def _retrieve_sitemap(self, url):
        self.kwargs['headers'].update(canonicalized({
            'if-modified-since': self.response_headers.get('last-modified'),
            'if-none-match': self.response_headers.get('etag')}))
        response = requests.get(url, **self.kwargs)
        response.raise_for_status()
        if response.url != url:
            logger.info('Redirects to %s', response.url)
        if response.status_code == 304:
            raise UnchangedException
        self.response_headers[url] = response.headers
        return response

    @property
    def raw_entries(self):
        for sitemap in self.index:
            try:
                response = self._retrieve_sitemap(sitemap['loc'])
            except (IOError, requests.RequestException) as excp:
                logger.error('Request exception %r for %s in index %s',
                             excp, sitemap['loc'], self.url)
            except UnchangedException:
                logger.info('Sitemap unchanged')
            else:
                for url in SitemapFetcher.parse(response):
                    yield url


################################# Feeds ##################################


class FeedEntryInterface(BaseEntryInterface):

    @property
    def updated(self):
        # Wordpress, notably, does not treat publishing as update,
        # which may cause articles schedule some time ago to pop up
        # too far in the past to make it onto the feed.
        raw_updated = self.raw_entry.get('updated_parsed') \
            or self.raw_entry.get('updated')
        raw_published = self.raw_entry.get('published_parsed') \
            or self.raw_entry.get('published')
        updated = process_time(
            raw_updated, default_tz=self.fetcher.default_tz)
        published = process_time(
            raw_published, default_tz=self.fetcher.default_tz)
        if updated and published:
            updated = max(updated, published)
        return updated or published

    @property
    def published(self):
        raw_date = self.raw_entry.get('published_parsed') or self.raw_entry.get('published')
        return process_time(
            raw_date, default_tz=self.fetcher.default_tz)

    @property
    def id(self):
        if self.raw_entry.has_key('id'):
            return self.raw_entry['id']
        # “… at least one of title or description must be present.”
        # http://www.rssboard.org/rss-specification/
        return urn_from_string(
            self.raw_entry.get('updated', '') +
            self.raw_entry.get('link', '') +
            self.raw_entry.get('title', self.raw_entry.get('summary', '')))

    @property
    def source(self):
        entry = {key: value for key, value in self.raw_entry.items()
                 if key not in ('summary', 'summary_detail', 'content')}
        return ('<details>\n'
                '<summary>JSON Source</summary>\n'
                '<div class="entry-source">{}</div>\n'
                '</details>').format(json.dumps(
                    entry, indent=4, sort_keys=True, default=str))

    @property
    def content(self):
        content = u'\n\n'.join(
            content.get('value', u'')
            for content in self.raw_entry.get('content', [])).strip()
        return content or None


    @property
    def content_type(self):
        # Ignores default if content missing. That’s correct, I think.
        if self.raw_entry.has_key('content'):
            return self.fetcher.type_mapping.get(
                self.raw_entry['content'][0]['type'], 'text')

    @property
    def title(self):
        return self.raw_entry.get('title')

    @property
    def link(self):
        return self.raw_entry.get('link')

    @property
    def summary_type(self):
        # See above.
        if self.raw_entry.has_key('summary_detail'):
            return self.fetcher.type_mapping.get(
                self.raw_entry['summary_detail']['type'], 'text')

    @property
    def summary(self):
        summary = self.raw_entry.get('summary', '').strip()
        if summary == self.content:
            return
        return summary or None

    @property
    def author(self):
        return '; '.join([author['name']
                          for author in self.raw_entry.get('authors', [])
                          if author.has_key('name')]) \
               or self.raw_entry.get('author')


class FeedFetcher(BaseFetcher):

    EntryInterface = FeedEntryInterface
    type_mapping = {
        'text/plain': 'text',
        'text/html': 'html',
        'application/xhtml+xml': 'xhtml'}

    @stopwatch
    def parse(self, response):
        raw_feed = decode_response(response)
        # This issue introduces encoding errors:
        # http://code.google.com/p/feedparser/issues/detail?id=378
        # This issue leads to broken URLs:
        # http://code.google.com/p/feedparser/issues/detail?id=357
        return feedparser.parse(raw_feed)

    def update(self):
        response = self.retrieve()
        self.source = self.parse(response)
        self.raw_entries = self.source.entries

    @property
    def id(self):
        if self.source.feed.has_key('id'):
            return self.source.feed['id']
        return urn_from_string(
            self.source.feed.get('link', self.source.feed.get('title', '')))

    @property
    def title(self):
        return self.source.feed.get('title') \
            or self.defaults.get('title')

    @property
    def subtitle(self):
        return self.source.feed.get('subtitle') \
            or self.defaults.get('subtitle')

    @property
    def link(self):
        return self.source.feed.get('link') \
            or self.defaults.get('link')

    @property
    def hub(self):
        for link in self.source.get('links', []):
            if link.get('rel') == 'hub':
                return link['href']
        return self.defaults.get('hub')

    @property
    def author(self):
        return '; '.join([author['name']
                          for author in self.source.feed.get('authors', [])
                          if author.has_key('name')]) \
               or self.source.feed.get('author') \
               or self.defaults.get('author')

    @property
    def generator(self):
        return self.source.feed.get('generator') \
            or self.defaults.get('generator')

################################ Twitter #################################

class TweetInterface(object):

    def __init__(self, tweet):
        self.tweet = tweet

    @property
    def tweet_text(self):
        if self.tweet.has_key('retweeted_status'):
            tweet = self.tweet['retweeted_status']
            prefix = 'RT @{screen_name}: '.format(
                screen_name=tweet['user']['screen_name'])
        else:
            tweet = self.tweet
            prefix = ''
        replacements = {}
        for url in tweet['entities']['urls']:
            replacements[tuple(url['indices'])] = \
                url.get('display_url', url['expanded_url'])
        for medium in tweet['entities'].get('media', []):
            replacements[tuple(medium['indices'])] = \
                medium.get('display_url', medium['expanded_url'])
        # Purging possible None values
        replacements = dict((key, value)
                            for key, value in replacements.items()
                            if value)
        return prefix + sub_slices(tweet['text'], replacements)

    @property
    def tweet_html(self):
        # TODO: Embed replies
        if self.tweet.has_key('retweeted_status'):
            tweet = self.tweet['retweeted_status']
            prefix = (
                'RT <a href="https://twitter.com/{screen_name}"'
                ' title="{name}">@{screen_name}</a>: ').format(
                    screen_name=tweet['user']['screen_name'],
                    name=tweet['user']['name'])
        else:
            tweet = self.tweet
            prefix = ''
        images = []
        replacements = {}
        for url in tweet['entities']['urls']:
            replacements[tuple(url['indices'])] = (
                '<a href="{expanded_url}">{display_url}</a>'.format(
                    expanded_url=url['expanded_url'],
                    display_url=url.get('display_url',
                                        url['expanded_url'])))
            if any(map((url['expanded_url'] or '').endswith,
                       ('.png', '.jpg', '.jpeg', '.gif', '.svg'))):
                images.append(url['expanded_url'])
        for hashtag in tweet['entities']['hashtags']:
            replacements[tuple(hashtag['indices'])] = (
                ('<a href="https://twitter.com/#!/search/'
                 '?q=%23{hashtag}&src=hash">#{hashtag}</a>').format(
                    hashtag=hashtag['text']))
        for mention in tweet['entities']['user_mentions']:
            # Case insensitive
            verbatim = tweet['text'][slice(*mention['indices'])]
            replacements[tuple(mention['indices'])] = (
                ('<a href="https://twitter.com/{screen_name}" title="{name}">'
                 '{verbatim}</a>').format(
                    screen_name=mention['screen_name'],
                    name=mention['name'],
                    verbatim=verbatim))
        for medium in tweet['entities'].get('media', []):
            replacements[tuple(medium['indices'])] = (
                '<a href="{expanded_url}">{display_url}</a>'.format(
                    expanded_url=medium['expanded_url'],
                    display_url=medium.get('display_url',
                                           medium['expanded_url'])))
            if medium['type'] == 'photo':
                images.append(medium['media_url'])
        # Purging possible None values
        replacements = dict((key, value)
                            for key, value in replacements.items()
                            if value)
        text = prefix + sub_slices(tweet['text'], replacements)
        images = '<br />'.join('<img src="{url}" alt="" />'.format(url=url)
                               for url in images)
        return '<p>{text}</p><p>{images}</p>'.format(text=text, images=images)

    @property
    def id(self):
        return unicode(self.tweet['id'])

    @property
    def updated(self):
        date = parse_date(self.tweet['created_at'])
        return date.astimezone(tzutc()).replace(tzinfo=None)

    @property
    def title(self):
        tweet_text = self.tweet_text
        if len(tweet_text) > settings.TWITTER_TITLE_LENGTH:
            return tweet_text[:settings.TWITTER_TITLE_LENGTH - 1] + '…'
        return tweet_text

    @property
    def author(self):
        return '{screen_name} ({name})'.format(
            screen_name=self.tweet['user']['screen_name'],
            name=self.tweet['user']['name'])

    @property
    def link(self):
        return 'https://twitter.com/{screen_name}/statuses/{id}'.format(
            screen_name=self.tweet['user']['screen_name'],
            id=self.tweet['id'])

    @property
    def content(self):
        return self.tweet_html

    @property
    def source_id(self):
        return 'urn:twitter:user:{id}'.format(id=self.tweet['user']['id'])

    @property
    def source_title(self):
        return '{author} on Twitter'.format(author=self.author)

    @property
    def source_link(self):
        return 'https://twitter.com/{screen_name}'.format(
            screen_name=self.tweet['user']['screen_name'])

    @property
    def entry(self):
        return Entry(
            id=self.id,
            title=self.title,
            updated=self.updated,
            published=self.updated,
            link=self.link,
            content=self.content,
            content_type='html',
            author=self.author,
            source_id=self.source_id,
            source_title=self.source_title,
            source_link=self.source_link)


class TwitterStreamer(object):

    def __init__(self, oauth_token, oauth_secret, timeout=0, **kwargs):
        self.oauth_token = oauth_token
        self.oauth_secret = oauth_secret
        self.timeout = timeout
        self.kwargs = kwargs
        self.friends = None

    def store(self, entries, new=False):
        session = Session()
        if not new:
            existing_ids = map(
                itemgetter(0),
                session.query(Entry.id)
                    .filter(Entry.id.in_(map(attrgetter('id'), entries))))
            entries = [entry for entry in entries
                       if entry.id not in existing_ids]
        try:
            for entry in entries:
                session.merge(entry)
            session.commit()
        except:
            session.rollback()
            raise
        return entries

    @property
    def stream(self):
        return TwythonStreamer(
            settings.CONSUMER_KEY,
            settings.CONSUMER_SECRET,
            self.oauth_token,
            self.oauth_secret,
            **self.kwargs)

    @property
    def rest(self):
        return Twython(
            settings.CONSUMER_KEY,
            settings.CONSUMER_SECRET,
            settings.OAUTH_TOKEN,
            settings.OAUTH_SECRET)

    def retrieve_home_timeline(self, count=200):
        return self.rest.get_home_timeline(
            count=count, exclude_replies=False, include_entities=True)

    def run(self):
        for i, tweet in enumerate(itertimeout(
                self.stream.user(**{'replies': 'all', 'with': 'followings'}),
                timeout=self.timeout)):
            fresh_entries = []
            if i % settings.TWITTER_STREAM_GET_INTERVAL == 0:
                # i == 0: Initial fetch in case we missed something
                # i != 0: Additional fetch in case the streaming API
                #         missed something.
                try:
                    get_tweets = self.retrieve_home_timeline()
                except Exception as excp:
                    logger.exception('Error during initial fetch: %r', excp)
                else:
                    entries = [TweetInterface(get_tweet).entry
                               for get_tweet in get_tweets]
                    fresh_entries = self.store(entries)
                    logger.info(
                        'Stored %s missed tweets by %s',
                        len(fresh_entries),
                        ', '.join(entry.author for entry in fresh_entries)
                            or 'everyone')
            logger.debug(json.dumps(tweet, indent=4))
            if tweet.has_key('id'):
                if tweet['user']['id'] in self.friends:
                    entry = TweetInterface(tweet).entry
                    self.store([entry], new=True)
                    logger.info('Stored tweet %s by %s',
                                tweet['id'], tweet['user']['screen_name'])
                    fresh_entries.append(entry)
                else:
                    # Unfortunately Twitter also streams replies to tweets by
                    # people we’re following regardless of whether we’re
                    # following the author.
                    logger.info('Skipping foreign tweet by %s',
                                tweet['user']['screen_name'])
            elif tweet.has_key('friends'):
                # Should be the first item to be streamed
                self.friends = tweet['friends']
                logger.info('Received list of %s friends',
                            len(tweet['friends']))
            elif tweet.get('event') == 'follow':
                self.friends.append(tweet['target']['id'])
                logger.info('Received follow event for %s',
                            tweet['target']['screen_name'])
            else:
                logger.info('Skipping weird object: %s', tweet)
            # Final yield
            if fresh_entries:
                yield fresh_entries
