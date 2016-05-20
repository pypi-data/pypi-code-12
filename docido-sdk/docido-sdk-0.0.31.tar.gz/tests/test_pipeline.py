import unittest

from docido_sdk.core import Component, implements
from docido_sdk.env import Environment
from docido_sdk.index import (
    IndexAPI,
    IndexAPIConfigurationProvider,
    IndexAPIProcessor,
    IndexAPIProvider,
    IndexPipelineConfig,
)
from docido_sdk.index.pipeline import IndexPipelineProvider
from docido_sdk.test import cleanup_component, cleanup_components


class Processor1(IndexAPIProcessor):
    pass


@cleanup_component
class Processor1Provider(Component):
    implements(IndexAPIProvider)

    def get_index_api(self, parent=None, **config):
        return Processor1(parent, **config)


class Processor2(IndexAPIProcessor):
    pass


@cleanup_component
class Processor2Provider(Component):
    implements(IndexAPIProvider)

    def get_index_api(self, parent=None, **config):
        return Processor2(parent, **config)


@cleanup_component
class IndexPipelineConfig(Component):
    implements(IndexPipelineConfig)

    def get_pipeline(self):
        return [
            self.env[Processor1Provider],
            self.env[Processor2Provider],
        ]


@cleanup_component
class IndexAPIConfigurationProvider(Component):
    implements(IndexAPIConfigurationProvider)

    def get_index_api_conf(self, service, docido_user_id, account_login):
        return {
            'service': service,
            'docido_user_id': docido_user_id,
            'account_login': account_login,
        }


class TestPipeline(unittest.TestCase):
    def test_build_pipeline(self):
        env = Environment()
        env[Processor1Provider]
        env[Processor2Provider]
        env[IndexPipelineConfig]
        pipeline_provider = env[IndexPipelineProvider]
        index_api = pipeline_provider.get_index_api(
            'service1', 'user1', 'account1'
        )
        config = {
            'service': 'service1',
            'docido_user_id': 'user1',
            'account_login': 'account1',
        }
        self.assertIsNotNone(index_api)
        self.assertTrue(isinstance(index_api, Processor1))
        self.assertEqual(index_api._config, config)
        self.assertIsNotNone(index_api._parent)
        self.assertTrue(isinstance(index_api._parent, Processor2))
        self.assertEqual(index_api._parent._config, config)
        self.assertTrue(isinstance(
            index_api._parent._parent,
            IndexAPI
        ))

    @classmethod
    def tearDownClass(cls):
        cleanup_components()


if __name__ == '__main__':
    unittest.main()
