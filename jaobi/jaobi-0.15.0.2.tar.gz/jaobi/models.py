# -*- coding: utf-8 -*-

import datetime
from uuid import uuid4
from tornado import gen, ioloop
from mongomotor import signals
from mongomotor import Document, EmbeddedDocument
from mongomotor.fields import (StringField, ReferenceField, BooleanField,
                               DateTimeField, ListField, UUIDField,
                               EmbeddedDocumentField, URLField)
from pyrocumulus.conf import settings
import resumeai
from jaobi.fields import SanitizedStringField, ImageURLField
from jaobi.scheduler import scheduler
from jaobi.utils import generate_collection_scores, log


class BaseContent(Document):
    url = URLField(required=True, unique=True)
    uuid = UUIDField()

    @gen.coroutine
    def save(self, *args, **kwargs):
        if not self.uuid:
            self.uuid = str(uuid4())
        yield super(BaseContent, self).save(*args, **kwargs)

    def __repr__(self):  # pragma no cover
        return 'content: %s' % self.url

    meta = {'allow_inheritance': True}


class Content(BaseContent):
    image = ImageURLField()
    themes = ListField(StringField())
    title = SanitizedStringField(required=True)
    description = SanitizedStringField()
    publication_date = DateTimeField(required=True)
    # wich site published this content
    origin = StringField()
    # what organization produced it. A producer can be a
    # 'hub' of origins
    producer = StringField()
    body = SanitizedStringField()
    recomends = BooleanField(default=True, required=True)
    last_consumers = ListField(StringField())

    @gen.coroutine
    def save(self, *args, **kwargs):
        if not self.publication_date:
            self.publication_date = datetime.datetime.now()

        yield super().save(*args, **kwargs)

    def get_last_consumers(self):
        """
        Returns the last consumers of a content
        """

        consumers = Consumer.objects.filter(id__in=self.last_consumers)
        return consumers

    @classmethod
    @gen.coroutine
    def post_content_consumption_save(cls, sender, document, **kwargs):
        consumer = yield document.consumer
        content = yield document.content
        last_consumers = content.last_consumers

        if str(consumer.id) not in last_consumers:
            last_consumers.insert(0, str(consumer.id))

        last_consumers = last_consumers[:settings.CONSUMPTION_HISTORY_SIZE]
        yield content.update(set__last_consumers=last_consumers)

    @classmethod
    @gen.coroutine
    def bulk_post_content_consumption_save(cls, sender, documents, **kwargs):

        for document in documents:
            yield cls.post_content_consumption_save(sender, document, **kwargs)


class ConsumerProfile(EmbeddedDocument):
    parent_doc = ReferenceField('Consumer', required=True)
    similar_consumers = ListField(ReferenceField('Consumer'))

    @gen.coroutine
    def get_preferred_themes(self):
        themes_hits = {}
        queryset = (yield self.parent_doc).consumption()
        total_hits = yield queryset.count()
        for c in queryset:
            # coverage does not feel good with coroutines, I think.
            # It show this line as not cover, but the next one yes.
            content = yield c  # pragma: no cover
            if not content:  # pragma: no cover
                continue
            themes = content.themes
            for theme in themes:
                theme_hits = themes_hits.get(str(theme)) or 0
                theme_hits += 1
                themes_hits[str(theme)] = theme_hits
        preferred = generate_collection_scores(themes_hits, total_hits)
        return preferred


class Consumer(Document):
    uuid = UUIDField()
    profile = EmbeddedDocumentField(ConsumerProfile)
    creation_date = DateTimeField()
    last_consumption = ListField(StringField())
    last_access = DateTimeField()

    def __repr__(self):  # pragma: no cover
        return 'consumer: %s' % self.id

    @gen.coroutine
    def save(self, *args, **kwargs):
        if not self.uuid:
            self.uuid = str(uuid4())
        if not self.creation_date:
            self.creation_date = datetime.datetime.now()
        if not self.last_access:
            self.last_access = datetime.datetime.now()

        yield super(Consumer, self).save(*args, **kwargs)
        if not self.profile:
            self.profile = ConsumerProfile(parent_doc=self)
            yield super(Consumer, self).save(*args, **kwargs)

    def consumption_history(self):
        return ContentConsumption.objects.filter(consumer=self, consumed=True)

    def future_consumption(self):
        return ContentConsumption.objects.filter(consumer=self, consumed=False)

    def consumption(self):
        return Content.objects.filter(url__in=self.last_consumption)

    @gen.coroutine
    def get_suggestions(self, quantity=20, depth=50, profile_depth=5,
                        exclude=None, similar_ids=[]):
        """Returns content suggestions.

        :param quantity: How many suggestions should be returned
        :param depth: How many contents will be considered in each consumer
          profile
        :param profile_depth: How many profiles will be checked
        :param exclude: An url of a content to be excluded.
        :param similar_ids: A list of consumer ids."""

        similar_consumers = yield type(self).objects.filter(
            id__in=similar_ids).to_list()

        candidate_content = yield self.get_candidate_content(
            similar_consumers, quantity, exclude=exclude)
        return candidate_content

    @gen.coroutine
    def get_candidate_content(self, similar_consumers, quantity, exclude=None):
        """ Returns content that may be suggested.

        :param similar_consumers: A list with consumers ids with similar
          profile.
        :param quantity: How many contents should be returned.
        :param exclude: An url of a content to be excluded."""

        candidate_content = []

        # Trying to get suggestions based on similar consumers
        for consumer in similar_consumers:
            consumption = consumer.consumption()
            if exclude:
                consumption = consumption.filter(url__ne=exclude)
            for content in (yield self.consumption().to_list()):
                consumption = consumption.filter(url__ne=content.url)

            ordered_consumption = yield consumption.order_by(
                '-consumption_date').to_list()

            for content in ordered_consumption:
                if not content.recomends:
                    continue
                if content not in candidate_content:  # pragma: no cover
                    candidate_content.append(content)
                if len(candidate_content) == quantity:
                    break

        # here I complete the list with the latest content
        if len(candidate_content) < quantity:

            content = Content.objects.all()
            my_consumption = yield self.consumption().to_list()
            for c in my_consumption:
                content = content.filter(url__ne=c.url)
            content = yield content.order_by('-publication_date').limit(
                quantity)
            content = yield content.to_list()
            i = 0
            try:
                while len(candidate_content) < quantity:
                    candidate_content.append(content[i])
                    i += 1
            except IndexError:
                pass

        return candidate_content

    @gen.coroutine
    def generate_similar_consumers(self, quantity, depth):
        consumers = {}
        total = 0
        consumption = yield self.consumption().limit(depth)
        consumers = yield consumption.item_frequencies('last_consumers')

        try:
            del consumers[str(self.id)]
        except KeyError:
            pass
        total = sum([v for k, v in consumers.items()])

        similar_consumers = generate_collection_scores(consumers, total)
        similar_consumers = [s[1] for s in similar_consumers[:quantity]]
        similar = yield type(self).objects.filter(
            id__in=similar_consumers).to_list()
        similar = sorted(similar,
                         key=lambda s: similar_consumers.index(str(s.id)))

        try:
            self.profile.similar_consumers = similar
        except AttributeError:
            log('consumer as dbref for generate_similar_consumers',
                level='error')

        yield self.save()

        return similar

    def get_similar_consumers(self):
        similar = self.profile.similar_consumers
        return similar

    @classmethod
    @gen.coroutine
    def post_content_consumption_save(cls, sender, document, **kwargs):
        consumer = yield document.consumer
        content = yield document.content
        try:
            last_consumption = consumer.last_consumption
        except AttributeError:
            log('consumer as dbref for consumer last consumption',
                level='error')
            return

        if content.url not in last_consumption:
            last_consumption.insert(0, content.url)

        last_consumption = last_consumption[:settings.CONSUMPTION_HISTORY_SIZE]
        last_access = document.inclusion_date
        yield consumer.update(set__last_consumption=last_consumption,
                              set__last_access=last_access)

    @classmethod
    @gen.coroutine
    def bulk_post_content_consumption_save(cls, sender, documents, **kwargs):
        for document in documents:
            yield cls.post_content_consumption_save(sender, document, **kwargs)

    @classmethod
    @gen.coroutine
    def clean_old_consumers(cls):
        timedelta = settings.CLEAN_DB_TIMEDELTA
        now = datetime.datetime.now()
        date = now - timedelta
        qs = cls.objects.filter(last_access__lte=date)
        yield qs.delete()
        qs = cls.objects.filter(last_access=None)
        yield qs.delete()


class ContentConsumption(Document):
    content = ReferenceField(Content, required=True)
    # themes and origin are here to easy reports.
    themes = ListField(StringField())
    origin = StringField()
    consumer = ReferenceField(Consumer, required=True)
    referrer = StringField()
    inclusion_date = DateTimeField()
    consumption_date = DateTimeField()
    unload_date = DateTimeField()
    consumed = BooleanField()

    @gen.coroutine
    def save(self, *args, **kwargs):
        if not self.inclusion_date:
            self.inclusion_date = datetime.datetime.now()
        if self.consumed and not self.consumption_date:
            self.consumption_date = datetime.datetime.now()

        self.themes = (yield self.content).themes
        self.origin = (yield self.content).origin

        yield super(ContentConsumption, self).save(*args, **kwargs)

    @classmethod
    @gen.coroutine
    def clean_old_consumption(cls):
        timedelta = settings.CLEAN_DB_TIMEDELTA
        now = datetime.datetime.now()
        date = now - timedelta
        qs = cls.objects.filter(inclusion_date__lte=date)

        yield qs.delete()


loop = ioloop.IOLoop.instance()


@gen.coroutine
def ensure_index():
    yield ContentConsumption.ensure_index('consumer')
    yield ContentConsumption.ensure_index('content')
    yield ContentConsumption.ensure_index('-inclusion_date')
    yield ContentConsumption.ensure_index('origin')
    yield ContentConsumption.ensure_index('themes')
    yield ContentConsumption.ensure_index('referrer')


loop.run_sync(ensure_index)


signals.post_save.connect(Consumer.post_content_consumption_save,
                          sender=ContentConsumption)


signals.post_bulk_insert.connect(Consumer.bulk_post_content_consumption_save,
                                 sender=ContentConsumption)

signals.post_save.connect(Content.post_content_consumption_save,
                          sender=ContentConsumption)


signals.post_bulk_insert.connect(Content.bulk_post_content_consumption_save,
                                 sender=ContentConsumption)


if hasattr(settings, 'CLEAN_DB') and settings.CLEAN_DB:  # pragma no cover
    # one day
    secs = 3600 * 24
    print('adding clean_db stuff to scheduler')
    scheduler.add(ContentConsumption.clean_old_consumption, secs)
    scheduler.add(Consumer.clean_old_consumers, secs)
