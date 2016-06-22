from .. core import Component, implements, ExtensionPoint
from . api import (
    IndexAPI,
    IndexAPIConfigurationProvider,
    IndexPipelineConfig,
    IndexAPIProvider,
)


class IndexPipelineProvider(Component):
    """ This implementation of :py:class:`docido_sdk.index.IndexAPIProvider`
    provides pipelines of :py:class:`docido_sdk.index.IndexAPIProcessor`
    """
    implements(IndexAPIProvider)
    config = ExtensionPoint(
        IndexAPIConfigurationProvider,
        unique=True
    )
    pipeline = ExtensionPoint(
        IndexPipelineConfig,
        unique=True
    )

    def get_index_api(self, service, docido_user_id, account_login, config):
        """ Create a pipeline of :py:class:`docido_sdk.index.IndexAPIProcessor`
        based on:

        - The :py:class:`docido_sdk.index.IndexAPIConfigurationProvider`
          which provides configuration to created
          :py:class:`docido_sdk.index.IndexAPIProcessor`
        - The :py:class:`docido_sdk.index.IndexPipelineConfig` which
          provides the :py:class:`docido_sdk.index.IndexAPIProcessor`
          list to link together.

        :param basestring: service:
          account service name (gmail, trello, ...)

        :param basestring: docido_user_id:
          the Docido user identifier for which the IndexAPI is meant form

        :param basestring: account_login
          the user account login for which the IndexAPI is meant for

        :param :py:class:`docido_sdk.toolbox.collections_ext.nameddict`

        :return: new pipeline of processors
        :rtype: :py:class:`docido_sdk.index.IndexAPI`
        """
        config = self.config.get_index_api_conf(
            service, docido_user_id, account_login, config
        )
        index_providers = self.pipeline.get_pipeline(service)
        index_api = IndexAPI()
        for provider in reversed(index_providers):
            index_api = provider.get_index_api(parent=index_api, **config)
        return index_api
