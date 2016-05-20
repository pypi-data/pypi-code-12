import unittest
import os.path as osp

import tempfile
import shutil
from contextlib import contextmanager
from docido_sdk.core import (
    Component,
    implements,
)
from docido_sdk.env import Environment
from docido_sdk.index import IndexAPIConfigurationProvider
from docido_sdk.index.pipeline import (
    IndexPipelineProvider, IndexPipelineConfig
)
from docido_sdk.index.test import LocalDumbIndex
from docido_sdk.index.test import LocalKV
from docido_sdk.index.api import IndexAPIProcessor, IndexAPIProvider
from docido_sdk.toolbox.contextlib_ext import unregister_component


class TestForwardProcessor(unittest.TestCase):
    TEST_DOC = {'id': 'a_test_id'}
    TEST_THUMB = ('thumb', '\x13', 'png')

    @contextmanager
    def index(self):
        """ Create new environment, fill it, and create an IndexAPI
        """
        from docido_sdk.index.config import YamlPullCrawlersIndexingConfig
        with unregister_component(YamlPullCrawlersIndexingConfig):
            env = Environment()
            env.temp_dir = tempfile.mkdtemp()
            test_components = self._setup_test_components(env)
            pipeline = env[IndexPipelineProvider]
            try:
                # build and provide an IndexAPI
                yield pipeline.get_index_api(None, None, None)
            finally:
                # Hide from Environment the Component classes defined
                # for this test only.
                for test_component in test_components:
                    test_component.unregister()
                    # Remove temporary directory previously created
                    if osp.isdir(env.temp_dir):
                        shutil.rmtree(env.temp_dir)

    @classmethod
    def _setup_test_components(cls, env):
        class ForcePipeline(Component):
            implements(IndexPipelineConfig)

            def get_pipeline(self):
                return [
                    env[IndexAPIForward],
                    env[LocalDumbIndex],
                    env[LocalKV],
                ]

        class ForceConfig(Component):
            implements(IndexAPIConfigurationProvider)

            def get_index_api_conf(self, service,
                                   docido_user_id, account_login):
                return {
                    'local_storage': {
                        'documents': {
                            'path': env.temp_dir,
                        },
                        'kv': {
                            'path': env.temp_dir,
                        },
                    },
                }

        class IndexAPIForwardProcessor(Component):
            implements(IndexAPIProcessor)

        class IndexAPIForward(Component):
            implements(IndexAPIProvider)

            def get_index_api(self, **config):
                return IndexAPIProcessor(**config)

        return [
            ForcePipeline,
            ForceConfig,
            IndexAPIForwardProcessor
        ]

    def test_push_cards_forward(self):
        with self.index() as index:
            index.push_cards([self.TEST_DOC])

    def test_delete_cards_forward(self):
        with self.index() as index:
            index.delete_cards({'query': {'match_all': {}}})

    def test_delete_cards_by_id(self):
        with self.index() as index:
            index.delete_cards_by_id([])

    def test_delete_thumbnails_forward(self):
        with self.index() as index:
            index.delete_thumbnails({'query': {'match_all': {}}})

    def test_search_cards_forward(self):
        with self.index() as index:
            index.search_cards({'query': {'match_all': {}}})

    def test_push_thumbnails_forward(self):
        with self.index() as index:
            index.push_thumbnails([self.TEST_THUMB])

    def test_get_kv_forward(self):
        with self.index() as index:
            index.get_kv('key')

    def test_set_kv_forward(self):
        with self.index() as index:
            index.set_kv('key', 'value')

    def test_delete_kv_forward(self):
        with self.index() as index:
            index.delete_kv('key')

    def test_delete_kvs_forward(self):
        with self.index() as index:
            index.delete_kvs()

    def test_get_kvs_forward(self):
        with self.index() as index:
            index.get_kvs()

    def test_ping_forward(self):
        with self.index() as index:
            index.ping()
