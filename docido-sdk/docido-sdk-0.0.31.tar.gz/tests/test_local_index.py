from contextlib import contextmanager
from itertools import repeat
import os.path as osp
import shutil
import tempfile
import unittest

from docido_sdk.env import Environment
from docido_sdk.core import (
    Component,
    implements,
)
from docido_sdk.index import (
    IndexPipelineConfig,
    IndexAPIConfigurationProvider,
)
from docido_sdk.index.pipeline import IndexPipelineProvider
from docido_sdk.index.test import LocalDumbIndex
from docido_sdk.toolbox.contextlib_ext import unregister_component


class TestLocalIndex(unittest.TestCase):
    TEST_CARD = {
        'id': 12345
    }

    def test_push_and_get_card(self):
        with self.index() as index:
            index.push_cards(repeat(self.TEST_CARD, 1))
            self.assertListEqual(index.search_cards(), [self.TEST_CARD])

    def test_push_and_delete_card(self):
        with self.index() as index:
            index.push_cards(repeat(self.TEST_CARD, 1))
            index.delete_cards({'query': {'match_all': {}}})
            self.assertListEqual(index.search_cards(), [])

    def test_push_and_delete_by_id(self):
        with self.index() as index:
            index.push_cards([self.TEST_CARD, {'id': 54321}])
            delete_result = index.delete_cards_by_id([54321])
            self.assertListEqual(delete_result, [])
            self.assertListEqual(index.search_cards(), [self.TEST_CARD])

    def test_delete_invalid_id_card(self):
        with self.index() as index:
            delete_result = index.delete_cards_by_id(['aFakeId'])
            self.assertListEqual(
                delete_result, [{'status': 404, 'id': 'aFakeId'}]
            )

    def test_push_and_delete_thumbnails(self):
        thumb = ('testid', '\x13\x13', 'png')
        with self.index() as index:
            index.push_thumbnails([thumb])
            delete_result = index.delete_thumbnails_by_id(['testid'])
            self.assertListEqual(delete_result, [])

    def test_delete_invalid_thumbnail(self):
        with self.index() as index:
            delete_result = index.delete_thumbnails_by_id(['aFakeId'])
            self.assertListEqual(
                delete_result, [{'status': 404, 'id': 'aFakeId'}]
            )

    @contextmanager
    def index(self):
        """ Create new environment, fill it, and create an IndexAPI
        """
        from docido_sdk.index.config import YamlPullCrawlersIndexingConfig
        with unregister_component(YamlPullCrawlersIndexingConfig):
            # `YamlPullCrawlersIndexingConfig` is hidden from Environment
            # instances in this context thanks to `unregister_component`.
            # This is required because this class uses a custom component
            # implementing `IndexPipelineConfig`, which is also the case of
            # `YamlPullCrawlersIndexingConfig`. But there must be only one.
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
        """ Define custom Component classes required for this test"""
        class ForcePipeline(Component):
            implements(IndexPipelineConfig)

            def get_pipeline(self):
                return [env[LocalDumbIndex]]

        class ForceConfig(Component):
            implements(IndexAPIConfigurationProvider)

            def get_index_api_conf(self, service, docido_user_id,
                                   account_login):
                return {
                    'local_storage': {
                        'documents': {
                            'path': env.temp_dir,
                        },
                        'kv': {
                            'path': env.temp_dir,
                        },
                    }
                }
        return ForcePipeline, ForceConfig


if __name__ == '__main___':
    unittest.main()
