# -*- coding: utf-8 -*-

from b3j0f.conf import Configurable, category, Parameter

from link.json.schema import JsonSchema
from link.json import CONF_BASE_PATH


DEFAULT_SCHEMA = 'http://hyperschema.org/mediatypes/collection-json.json'


@Configurable(
    paths='{0}/collection.conf'.format(CONF_BASE_PATH),
    conf=category(
        'JSONCOLLECTION',
        Parameter(name='version', value='1.0'),
        Parameter(name='schema', value=DEFAULT_SCHEMA)
    )
)
class CollectionJSONResponse(object):
    """
    Helper class used to generate valid Collection+JSON objects.
    """

    ITEM_ID = 'id'

    def __init__(
        self,
        href,
        links=None,
        items=None,
        queries=None,
        template=None,
        error=None,
        *args, **kwargs
    ):
        """
        :param href: Base URL
        :type href: str

        :param links: Optional list of links
        :type links: list

        :param items: Optional list of items
        :type items: list

        :param queries: Optional list of queries
        :type queries: list

        :param template: Optional item template
        :type template: dict

        :param error: Optional error
        :type error: dict
        """

        super(CollectionJSONResponse, self).__init__(*args, **kwargs)

        self.href = href
        self.links = links
        self.items = items
        self.queries = queries
        self.template = template
        self.error = error

        self.validator = JsonSchema()

    def json(self):
        """
        Generate JSON object.

        :return: Collection+JSON object
        :rtype: dict
        """

        base = {
            'collection': {
                'version': self.version,
                'href': self.href
            }
        }

        if self.links is not None:
            base['collection']['links'] = self.links

        if self.items is not None:
            base['collection']['items'] = self.items

        if self.queries is not None:
            base['collection']['queries'] = self.queries

        if self.template is not None:
            base['collection']['template'] = self.template

        if self.error is not None:
            base['collection']['error'] = self.error

        self.validator.validate(self.schema, base)

        return base

    @staticmethod
    def template_from_schema(schema):
        tmpl = {
            'template': {
                'data': []
            }
        }

        if 'properties' in schema:
            for propname in schema['properties']:
                prop = schema['properties'][propname]

                data = {
                    'name': propname
                }

                if 'default' in prop:
                    data['value'] = prop['default']

                if 'title' in prop:
                    data['prompt'] = prop['title']

                elif 'description' in prop:
                    data['prompt'] = prop['description']

                tmpl['template']['data'].append(data)

        return tmpl

    @classmethod
    def make_item(cls, href, document, schema=None):
        item = {
            'href': '{0}/{1}'.format(href, document.get(cls.ITEM_ID, '')),
            'data': []
        }

        if schema is not None and 'links' in schema:
            item['links'] = []

            for link in schema['links']:
                itemlink = {
                    'href': link['href'].format(**document),
                    'rel': link['rel']
                }

                if 'title' in link:
                    itemlink['name'] = link['title']

                if 'description' in link:
                    itemlink['prompt'] = link['description']

                item['links'].append(itemlink)

        for key in document:
            data = {
                'name': key,
                'value': document[key]
            }

            if schema is not None and key in schema.get('properties', {}):
                prop = schema['properties'][key]

                if 'title' in prop:
                    data['prompt'] = prop['title']

                elif 'description' in prop:
                    data['prompt'] = prop['description']

            item['data'].append(data)

        return item


def generate_collection_response(
    href,
    links=None,
    items=None,
    queries=None,
    schema=None,
    error=None
):
    """
    Helper instantiating a ``CollectionJSONResponse`` class using the default
    schema.

    :param href: Base URL
    :type href: str

    :param links: Optional list of links
    :type links: list

    :param items: Optional list of items
    :type items: list

    :param queries: Optional list of queries
    :type queries: list

    :param schema: Optional item schema
    :type schema: dict

    :param error: Optional error
    :type error: dict

    :return: Collection+JSON object
    :rtype: dict
    """

    resp = CollectionJSONResponse(
        href,
        links=links,
        items=[
            CollectionJSONResponse.make_item(href, item, schema=schema)
            for item in items
        ],
        queries=queries,
        template=CollectionJSONResponse.template_from_schema(schema),
        error=error
    )

    return resp.json()
