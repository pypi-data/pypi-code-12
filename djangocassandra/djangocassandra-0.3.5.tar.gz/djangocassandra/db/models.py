from django.db.models import (
    Model as DjangoModel,
    Manager
)

from .fields import TokenPartitionKeyField
from .query import QuerySet


class ColumnFamilyManager(Manager.from_queryset(QuerySet)):
    pass


class ColumnFamilyModel(DjangoModel):
    class Meta:
        abstract = True

    pk_token = TokenPartitionKeyField()

    def __init__(
        self,
        *args,
        **kwargs
    ):
        super(ColumnFamilyModel, self).__init__(
            *args,
            **kwargs
        )

    def _get_pk_val(
        self,
        meta
    ):
        if (
            not hasattr(self, 'Cassandra') or
            not hasattr(self.Cassandra, 'partition_keys')
        ):
            return super(ColumnFamilyModel, self)._get_pk_val(meta)

        else:
            primary_keys = self.Cassandra.partition_keys
            if hasattr(self.Cassandra, 'clustering_keys'):
                primary_keys += self.Cassandra.clustering_keys

            pk = ''
            for key in primary_keys:
                pk += str(getattr(self, key))

            return pk

    def save(
            self,
            *args,
            **kwargs
    ):
        kwargs['force_insert'] = True
        kwargs['force_update'] = False

        return super(ColumnFamilyModel, self).save(
            *args,
            **kwargs
        )

    objects = ColumnFamilyManager()
