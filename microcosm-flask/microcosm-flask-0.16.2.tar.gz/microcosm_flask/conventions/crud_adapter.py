"""
Adapter between conventional crud functions and the `microcosm_postgres.store.Store` interface.

"""
from microcosm_flask.naming import name_for


class CRUDStoreAdapter(object):
    """
    Adapt the CRUD conventions callbacks to the `Store` interface.

    Does NOT impose transactions; use the `microcosm_postgres.context.transactional` decorator.

    """
    def __init__(self, graph, store):
        self.graph = graph
        self.store = store

    @property
    def identifier_key(self):
        return "{}_id".format(name_for(self.store.model_class))

    def create(self, **kwargs):
        model = self.store.model_class(**kwargs)
        return self.store.create(model)

    def delete(self, **kwargs):
        identifier = kwargs.pop(self.identifier_key)
        return self.store.delete(identifier)

    def replace(self, **kwargs):
        identifier = kwargs.pop(self.identifier_key)
        model = self.store.model_class(id=identifier, **kwargs)
        return self.store.replace(identifier, model)

    def retrieve(self, **kwargs):
        identifier = kwargs.pop(self.identifier_key)
        return self.store.retrieve(identifier)

    def search(self, offset, limit, **kwargs):
        items = self.store.search(offset=offset, limit=limit, **kwargs)
        count = self.store.count(**kwargs)
        return items, count

    def update(self, **kwargs):
        identifier = kwargs.pop(self.identifier_key)
        model = self.store.model_class(id=identifier, **kwargs)
        return self.store.update(identifier, model)
