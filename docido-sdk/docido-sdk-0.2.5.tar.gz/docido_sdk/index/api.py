
from docido_sdk.core import Interface

__all__ = [
    'IndexAPI',
    'IndexAPIConfigurationProvider',
    'IndexAPIProcessor',
    'IndexAPIProvider',
    'IndexPipelineConfig',
    'PullCrawlerIndexingConfig',
]


class IndexAPIProvider(Interface):  # pragma: no cover
    """ Provide an implementation of IndexAPI
    """
    def get_index_api(self, **config):
        """ Create a new instance of :py:class:`docido_sdk.index.IndexAPI`

        :param dict: config:
          extra configuration given to the object to create

        :return: new instance
        :rtype: :py:class:`docido_sdk.index.IndexAPI`
        """


class IndexAPI(object):
    """Read/write access to Docido index.

    :An IndexAPI object can manipulate 3 kind of data:
        :cards:
          a searchable item in Docido index.
        :thumbnails:
          a binary item in Docido index, for thumbnails of
          card's attachments. Used to improve user-experience by providing
          fast preview of binary files attached to cards.
        :a key value store:
          provides crawlers a way to persist their synchronization state.

    :Error Handling:
        Every bulk operation that modifies Docido index returns the list of
        operations that failed. Every item is a `dict` providing
        the following key:

        :status:
          http error code
        :error:
          reason in string format
        :id:
          error identifier
        :card:
          original card

    :Filtering:
        Index enumeration and deletion operations allow you to restrict
        the target scope by providing a `query` in parameter.
        The `query` parameters follows the Elasticsearch Query DSL.
    """
    def get_user_identifier(self):
        """Retrieve unique resource identifier of the user that owns
        the crawled data"""

    def push_cards(self, cards):
        """Send a synchronous bulk indexing request

        :param list cards: collections of cards to index.

        :return: collection of items whose insertion failed.
        """

    def delete_cards(self, query=None):
        """Send a synchronous deletion by query

        :param list query: a search definition using the Elasticsearch
            Query DSL to restrict the scope of cards to delete.

        :raise IndexAPIError: if a problem occur while deleting cards
        """

    def delete_cards_by_id(self, ids):
        """ Send a bulk deletion request

        :param list ids: a list of card ids to delete.

        :return: collection of items whose deletion failed.
        """

    def search_cards(self, query=None):
        """Enumerate cards in Docido index.

        :param list query: a search definition using the
            Elasticsearch Query DSL

        :return: FIXME
        """

    def push_thumbnails(self, thumbnails):
        """Add or update thumbnails in dedicated Docido index.

        :param list thumbnails: Collection of tuples
                                `(identifier, encoded_bytes, mime_type)`

        :return: collection of items whose insertion failed.
        """

    def delete_thumbnails(self, query=None):
        """Delete thumbnails from dedicated Docido index.

        :param query: a search definition using the Elasticsearch Query DSL to
                    restrict the scope of thumbnails to delete.

        :raise IndexAPIError: if a problem occur while deleting thumbnails
        """

    def delete_thumbnails_by_id(self, ids):
        """Delete thumbnails from dedicated Docido index.

        :param query: a search definition using the Elasticsearch Query DSL to
                    restrict the scope of thumbnails to delete.

        :raise IndexAPIError: if a problem occur while deleting thumbnails
        """

    def get_kv(self, key):
        """Retrieve value from persistence layer

        :param string key: input key

        :return: the value is present, `None` otherwise.
        :rtype: string
        """

    def set_kv(self, key, value):
        """Insert or update existing key in persistence layer.

        :param string key: input key
        :param string value: value to store
        """

    def delete_kv(self, key):
        """Remove key from persistent storage.

        :param key: the key to remove
        """

    def delete_kvs(self):
        """Remove all crawler persisted data.
        """

    def get_kvs(self):
        """Retrieve all crawler persisted data.

        :return: collection of tuple `(key, value)`
        :rtype: list
        """

    def ping(self):
        """Test availability of Docido index

        :raises SystemError: if Docido index is unreachable
        """

    def crawl_terminated(self):
        """Called by framework when crawl is over

        Helpful to flush buffers
        """

    def task_terminated(self):
        """Called by the framework when a crawl task terminates

        Helpful to flush buffers
        """


class IndexAPIProcessor(IndexAPI):
    """ Allows creation of :py:class:`docido_sdk.index.IndexAPI` pipelines
    """
    def __init__(self, parent=None, **config):
        """
        :param :py:class:`docido_sdk.index.IndexAPI`: parent:
          next pipeline object

        :param dict: config:
          extra processor configuration
        """
        self._parent = parent
        self._config = config

    def get_user_identifier(self):
        return self._parent.get_user_identifier()

    def push_cards(self, cards):
        return self._parent.push_cards(cards)

    def delete_cards(self, query=None):
        return self._parent.delete_cards(query)

    def delete_cards_by_id(self, ids):
        return self._parent.delete_cards_by_id(ids)

    def search_cards(self, query=None):
        return self._parent.search_cards(query)

    def push_thumbnails(self, thumbnails):
        return self._parent.push_thumbnails(thumbnails)

    def delete_thumbnails(self, query=None):
        return self._parent.delete_thumbnails(query)

    def get_kv(self, key):
        return self._parent.get_kv(key)

    def set_kv(self, key, value):
        return self._parent.set_kv(key, value)

    def delete_kv(self, key):
        return self._parent.delete_kv(key)

    def delete_kvs(self):
        return self._parent.delete_kvs()

    def get_kvs(self):
        return self._parent.get_kvs()

    def ping(self):
        return self._parent.ping()

    def crawl_terminated(self):
        return self._parent.crawl_terminated()

    def task_terminated(self):
        return self._parent.task_terminated()


class IndexAPIConfigurationProvider(Interface):  # pragma: no cover
    """ An interface to provide a configuration consumed by
    :py:class:`docido_sdk.index.IndexAPIProcessor`
    """
    def get_index_api_conf(service, docido_user_id, account_login, config):
        """ Provides a configuration object given to every index processors

        :param: basestring: service:
          account service name (gmail, trello, ...)

        :param: basestring: docido_user_id:
          the Docido user identifier for which the IndexAPI is meant form

        :param: basestring: account_login
          the user account login for which the IndexAPI is meant for

        :param nameddict: config
          optional crawl configuration

        :return: IndexAPI Configuration
        :rtype: dict
        """
        pass


class IndexPipelineConfig(Interface):  # pragma: no cover
    """ Provides list of :py:class:`docido_sdk.index.IndexAPIProvider`
    to link together in order to create the indexing pipeline.
    """
    def get_pipeline(service):
        """

        :param: basestring service:

        :return:
          description of the index pipeline to create
        :rtype: :py:class:`docido_sdk.index.IndexAPIProvider`
        """
        pass


class PullCrawlerIndexingConfig(Interface):
    def core(self):
        """ Providers common pull-crawlers indexing configuration

        :return:
          description of pull-crawlers indexing Configuration
        :rtype: dict
        """

    def service(service):
        """ Provides crawler specific indexing configuration.

        :param: basestring service:

        :return:
          description of the crawler custom indexing Configuration
        :rtype: dict
        """
