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


def generate_collection_response(
    href,
    links=None,
    items=None,
    queries=None,
    template=None,
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

    :param template: Optional item template
    :type template: dict

    :param error: Optional error
    :type error: dict

    :return: Collection+JSON object
    :rtype: dict
    """

    resp = CollectionJSONResponse(
        href,
        links=links,
        items=items,
        queries=queries,
        template=template,
        error=error
    )

    return resp.json()
