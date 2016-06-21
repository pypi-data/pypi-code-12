# coding=utf-8
from django.db import models
from django.db.models.query import QuerySet
from django.utils import timezone


class ContentMixin(object):
    def by_author(self, user):
        return self.filter(author=user)

    def by_category(self, category):
        return self.filter(category=category)

    def published(self):
        return self.filter(
            status__gte=self.model.PUBLIC, publish__lte=timezone.now()
        )

    def static_pages(self):
        return self.filter(category__id=1)

    def blog_posts(self):
        return self.exclude(category__id=1)


class ContentQuerySet(QuerySet, ContentMixin):
    pass


class ContentManager(models.Manager, ContentMixin):
    def get_queryset(self):
        return ContentQuerySet(self.model, using=self._db)
