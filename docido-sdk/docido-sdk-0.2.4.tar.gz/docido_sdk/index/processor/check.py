import copy
import sys

import voluptuous
from yamlious import from_dict, merge_dicts
from docido_sdk.index import (
    IndexAPIError,
    IndexAPIErrorBuilder,
    IndexAPIProcessor,
    IndexAPIProvider,
    PullCrawlerIndexingConfig,
)
from docido_sdk.core import (
    Component,
    ExtensionPoint,
    implements,
    Interface,
)
from docido_sdk.toolbox.decorators import lazy


__all__ = ['CheckProcessor']


class Check(IndexAPIProcessor):
    """ An index api processor responsible for document and query structure
    checks

    Based on predefined voluptuous Schema, every document will be checked or
    an IndexAPIError will be raised
    """
    def __init__(self, default_schema, card_schemas, query_schema, **kwargs):
        super(Check, self).__init__(**kwargs)
        assert isinstance(default_schema, voluptuous.Schema)
        for schema in card_schemas.values():
            assert isinstance(schema, voluptuous.Schema)
        assert isinstance(query_schema, voluptuous.Schema)
        self.default_schema = default_schema
        self.card_schemas = card_schemas
        self.query_schema = query_schema

    def push_cards(self, cards):
        for i in range(len(cards)):
            try:
                c = cards[i]
                if 'kind' not in c:
                    raise IndexAPIErrorBuilder(c)\
                        .message("Missing 'kind' field")\
                        .exception()
                self._check_attachments(c)
                if c['kind'] in self.card_schemas:
                    cards[i] = self.card_schemas[c['kind']](c)
                else:
                    cards[i] = self.default_schema(c)
            except voluptuous.MultipleInvalid as e:
                traceback = sys.exc_info()[2]
                raise IndexAPIErrorBuilder(c)\
                    .message(e)\
                    .exception(), None, traceback
            self.check_identifier(c)
        return super(Check, self).push_cards(cards)

    def check_identifier(self, card):
        uri = card['id']
        if '//' in uri:
            msg = "'id' field cannot contain 2 consecutive '/' characters"
            raise IndexAPIErrorBuilder(card)\
                .message(msg)\
                .exception(), None, sys.exc_info()[2]

    def _check_attachments(self, card):
        origin_ids = set()
        # add 'attachments' field if missing, otherwise voluptuous yells
        for attachment in card.setdefault('attachments', []):
            if 'origin_id' not in attachment:
                continue
            origin_id = attachment['origin_id']
            if origin_id in origin_ids:
                raise IndexAPIError.build(card).message(
                    "Cannot have 2 attachments with "
                    "the same 'origin_id'").exception()
            origin_ids.add(origin_id)

    def search_cards(self, query=None):
        try:
            self.query_schema(query)
        except voluptuous.MultipleInvalid as e:
            raise IndexAPIError(e)
        return super(Check, self).search_cards(query)

    def delete_thumbnails(self, query):
        try:
            self.query_schema(query)
        except voluptuous.MultipleInvalid as e:
            raise IndexAPIError(e)
        return super(Check, self).delete_thumbnails(query)

    def delete_cards(self, query):
        try:
            self.query_schema(query)
        except voluptuous.MultipleInvalid as e:
            raise IndexAPIError(e)
        return super(Check, self).delete_cards(query)


class CheckProcessorSchemaProvider(Interface):  # pragma: no cover
    def default_schema(service):
        pass

    def card_schemas(service):
        pass

    def query_schema(service):
        pass


class CheckProcessor(Component):
    implements(IndexAPIProvider)
    schema_provider = ExtensionPoint(CheckProcessorSchemaProvider, unique=True)

    def get_index_api(self, **config):
        service = config['service']
        default_schema = self.schema_provider.default_schema(service)
        query_schema = self.schema_provider.query_schema(service)
        card_schemas = self.schema_provider.card_schemas(service)
        return Check(default_schema, card_schemas, query_schema, **config)


class DocidoCheckProcessorSchemaProvider(Component):
    implements(CheckProcessorSchemaProvider)
    indexing_config = ExtensionPoint(PullCrawlerIndexingConfig, unique=True)

    def _get_config(self, indexing_config):
        check_processor = indexing_config.get('check_processor', {})
        return check_processor.get('schemas', {})

    @lazy
    def _core_config(self):
        return self._get_config(self.indexing_config.core())

    def _crawler_config(self, service):
        return self._get_config(self.indexing_config.service(service))

    def _schema_from_dicts(self, core_conf, crawler_conf):
        schema, options = from_dict(merge_dicts(
            copy.deepcopy(core_conf),
            copy.deepcopy(crawler_conf)
        ))
        return voluptuous.Schema(schema, **options)

    def _get_schemas(self, service):
        kind_schemas = self._core_config.get('card', {}).get('kind', {}) or {}
        return {
            k: self._schema_from_dicts(
                v,
                copy.deepcopy(self._crawler_config(service).get(k, {}))
            )
            for k, v in kind_schemas.iteritems()
        }

    def card_schemas(self, service):
        return self._get_schemas(service)

    def default_schema(self, service):
        core_default = self._core_config.get('card', {}).get('default', {})
        crawler_config = self._crawler_config(service).get('card', {}).get(
            'default', {}
        )
        return self._schema_from_dicts(core_default, crawler_config)

    def query_schema(self, service):
        core_query = self._core_config.get('query', {})
        crawler_query = self._crawler_config(service).get('query', {})
        return self._schema_from_dicts(core_query, crawler_query)
