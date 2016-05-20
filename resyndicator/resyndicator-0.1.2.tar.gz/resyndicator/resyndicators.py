import requests
import xmltodict
from datetime import datetime
from operator import attrgetter
from slugify import slugify
from utilofies.stdlib import isoformat
from . import settings
from .logger import logger
from .utils import urn_from_string, FeedTemplate
from .models import Session, Entry


class Resyndicator(object):

    def __init__(self, title, query, past=None, length=settings.DEFAULT_LENGTH, **kwargs):
        self.title = title  # Don't ever change it!
        self.slug = slugify(title, to_lower=True)
        self.length = length
        self.metadata = kwargs
        self.id = urn_from_string(self.title)
        self.query = query
        self.past = past
        self.url = settings.BASE_URL + 'feeds/' + self.slug
        self.session = Session()

    def get_entries(self):
        query = self.session.query(Entry)
        if self.past:
            query = query.filter(Entry.updated > datetime.utcnow() - self.past)
        return query.filter(self.query) \
            .order_by(Entry.updated.desc()) \
            [:settings.DEFAULT_LENGTH]

    @property
    def feed(self):
        entries = self.get_entries()
        feed = FeedTemplate.feed()
        feed['feed']['id'] = self.id
        feed['feed']['title'] = self.title
        feed['feed']['updated'] = isoformat(entries[0].updated) if entries else None
        feed['feed']['link'][0]['@href'] = self.url
        feed['feed'].update(self.metadata)
        for entry in entries[:self.length]:
            feed_entry = FeedTemplate.entry()
            feed_entry['id'] = urn_from_string(entry.id)
            feed_entry['updated'] = isoformat(entry.updated)
            feed_entry['published'] = isoformat(entry.published)
            feed_entry['title'] = entry.title
            feed_entry['author']['name'] = entry.author
            feed_entry['link']['@href'] = entry.link
            feed_entry['summary']['@type'] = entry.summary_type
            feed_entry['summary']['#text'] = entry.summary
            feed_entry['content']['@type'] = entry.content_type
            feed_entry['content']['#text'] = entry.content
            feed_entry['source']['id'] = entry.source_id
            feed_entry['source']['title'] = entry.source_title
            feed_entry['source']['link']['@href'] = entry.source_link
            feed['feed']['entry'].append(feed_entry)
        return xmltodict.unparse(feed, pretty=True)

    def publish(self):
        with open(settings.WEBROOT + self.slug + '.atom', 'w') as feedfile:
            feedfile.write(self.feed)

    def pubsub(self, fresh_entries):
        entry_ids = set(map(attrgetter('id'), self.get_entries()))
        fresh_entry_ids = set(map(attrgetter('id'), fresh_entries))
        if entry_ids & fresh_entry_ids:
            logger.info('Publishing %s to %s', self.title, settings.HUB)
            try:
                response = requests.post(
                    settings.HUB,
                    data={'hub.mode': 'publish', 'hub.url': self.url})
            except (IOError, requests.RequestException) as excp:
                logger.error('Request exception %r for %s while publishing %s',
                             excp, settings.HUB, self.title)
            else:
                if response.status_code != 204:
                    logger.error('Publishing %s to %s failed: %s',
                                 self.title, settings.HUB, response.text)
