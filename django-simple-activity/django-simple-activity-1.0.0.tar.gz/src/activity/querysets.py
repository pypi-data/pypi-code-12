from __future__ import unicode_literals

from django.db.models.query import QuerySet


class ActionQueryset(QuerySet):

    def public(self):
        return self.filter(is_public=True)

    def private(self):
        return self.filter(is_public=False)
