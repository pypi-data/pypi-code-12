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
from docido_sdk.index.pipeline import IndexPipelineProvider
import docido_sdk.config as docido_config

from docido_sdk.toolbox.collections_ext import Configuration
from docido_sdk.index.processor import Elasticsearch


class TestEsAPI(unittest.TestCase):
    TEST_DOC = {'id': 'a_test_id'}
    TEST_THUMB = ('thumb', '\x13', 'png')

    @contextmanager
    def index(self):
        """ Create new environment, fill it, and create an IndexAPI
        """
        from docido_sdk.index.config import YamlPullCrawlersIndexingConfig
        config_yaml = osp.splitext(__file__)[0] + '.yml'
        with docido_config:
            docido_config.clear()
            docido_config.update(Configuration.from_file(config_yaml))
            env = Environment()
            env.temp_dir = tempfile.mkdtemp()
            test_components = self._setup_test_components(env)
            pipeline = env[IndexPipelineProvider]
            env[Elasticsearch]
            try:
                # build and provide an IndexAPI
                env[YamlPullCrawlersIndexingConfig]
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
        class DumbIndexAPIConfiguration(Component):
            implements(IndexAPIConfigurationProvider)

            def get_index_api_conf(self, service, docido_user_id,
                                   account_login):
                return {
                    'service': service,
                    'docido_user_id': docido_user_id,
                    'account_login': account_login,
                    'elasticsearch': {
                        'routing': 'id'
                    }
                }

        return [
            DumbIndexAPIConfiguration
        ]

    def test_ping(self):
        with self.index() as index:
            index.ping()

    def test_push_and_delete_cards(self):
        with self.index() as index:
            result = index.push_cards([self.TEST_DOC])
            self.assertListEqual(result, [])
            self.assertListEqual(
                list(index.search_cards(
                    {'query': {'match_all': {}}})
                ), [self.TEST_DOC]
            )
            index.delete_cards({'query': {'match_all': {}}})
            self.assertListEqual(
                list(index.search_cards(
                    {'query': {'match_all': {}}})
                ), []
            )

    def test_push_invalid_doc(self):
        with self.index() as index:
            push_result = index.push_cards([[]])
            self.assertEqual(len(push_result), 1)

    def test_delete_invalid_doc(self):
        with self.index() as index:
            delete_result = index.delete_cards_by_id(['aFakeId'])
            self.assertEqual(delete_result, [{'status': 404, 'id': 'aFakeId'}])

    def test_push_and_delete_by_id(self):
        with self.index() as index:
            resp = index.push_cards([self.TEST_DOC])
            self.assertEqual(resp, [])
            del_result = index.delete_cards_by_id([self.TEST_DOC['id']])
            self.assertListEqual(del_result, [])
            self.assertListEqual(
                list(index.search_cards(
                    {'query': {'match_all': {}}})
                ), []
            )
            index.delete_cards({'query': {'match_all': {}}})

    def test_push_several(self):
        with self.index() as index:
            try:
                cards = [dict(id=42), dict(id=43)]
                index.push_cards(cards)
                cards_gen = index.search_cards({'query': {'match_all': {}}})
                self.assertEqual(cards, list(cards_gen))
            finally:
                index.delete_cards({'query': {'match_all': {}}})

    def test_push_and_get_card(self):
        with self.index() as index:
            index.push_cards([self.TEST_DOC])
            cards_gen = index.search_cards({'query': {'match_all': {}}})
            cards = list(cards_gen)
            self.assertIn(self.TEST_DOC, cards)
            index.delete_cards({'query': {'match_all': {}}})

    def test_push_and_delete_thumbnails(self):
        with self.index() as index:
            index.push_thumbnails([self.TEST_THUMB])
            index.delete_thumbnails({'query': {'match_all': {}}})

    def test_push_and_delete_thumbnails_by_id(self):
        with self.index() as index:
            index.push_thumbnails([self.TEST_THUMB])
            delete_result = index.delete_thumbnails_by_id([self.TEST_THUMB[0]])
            self.assertListEqual(delete_result, [])

    def test_delete_invalid_thumbnail(self):
        with self.index() as index:
            delete_result = index.delete_thumbnails_by_id(['aFakeId'])
            self.assertListEqual(delete_result, [
                {'status': 404, 'id': 'aFakeId'}
            ])
