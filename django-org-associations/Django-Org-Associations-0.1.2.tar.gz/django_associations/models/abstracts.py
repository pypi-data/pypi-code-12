"""
The Abstracted base for the models.
"""
from django.db import models
from django.utils.timezone import now
# pylint: disable=too-few-public-methods, no-member

class QueryManager(models.Manager):
    "Query Manager to restrict returning data"
    def get_queryset(self):
        "get_queryset override"
        query = models.Manager.get_queryset(self)
        query.filter(dts_delete__isnull=False)
        return query


class Abstract(models.Model):
    "Abstract share by all subsequent models."
    objects = QueryManager()

    class Meta:
        "Meta section to identify this is abstract"
        abstract = True

    dts_insert = models.DateTimeField(auto_now_add=True)
    dts_update = models.DateTimeField(null=True, blank=True)
    dts_delete = models.DateTimeField(null=True, blank=True)

    def save(self, force_insert=False, force_update=False, using=None,
        update_fields=None):
        if self.id not in [0, None]:
            self.dts_update = now()
        returns = super().save(force_insert=force_insert,
                               force_update=force_update,
                               using=using, update_fields=update_fields)
        return returns

    def __str__(self):
        text = str(self.id)
        if hasattr(self, 'label'):
            text = str(self.label)

        return text
