from contextlib import contextmanager
import copy
import os.path as osp
import unittest

import docido_sdk.config as docido_config
from docido_sdk.core import (
    Component,
    implements,
)
from docido_sdk.toolbox.collections_ext import Configuration
from docido_sdk.env import Environment
from docido_sdk.index.pipeline import IndexPipelineProvider
import docido_sdk.index.processor as processor
from docido_sdk.index.test import LocalDumbIndex
from docido_sdk.index import IndexAPIConfigurationProvider, IndexAPIError


class TestCheckProcessor(unittest.TestCase):
    VALID_CARD = {
        'id': '12345',
        'title': 'title1',
        'description': 'description1',
        'date': 12345,
        'kind': 'kind1',
        'author': {
            'name': 'author.name1',
        },
        'attachments': [],
    }

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
                }
        return [DumbIndexAPIConfiguration]

    @contextmanager
    def index(self):
        from docido_sdk.index.config import YamlPullCrawlersIndexingConfig
        config_yaml = osp.splitext(__file__)[0] + '.yml'
        with docido_config:
            docido_config.clear()
            docido_config.update(Configuration.from_file(config_yaml))
            env = Environment()
            test_components = self._setup_test_components(env)
            env[IndexPipelineProvider]
            env[LocalDumbIndex]
            env[processor.CheckProcessor]
            try:
                env[YamlPullCrawlersIndexingConfig]
                index_builder = env[IndexPipelineProvider]
                yield index_builder.get_index_api(
                    'check-processor-test', 'user2', 'account3'
                )
            finally:
                for test_component in test_components:
                    test_component.unregister()

    def test_push_valid_document(self):
        with self.index() as index:
            index.push_cards([self.VALID_CARD])
            self.assertEqual(
                [self.VALID_CARD],
                index.search_cards({'query': {'match_all': {}}})
            )

    def test_push_extra_field(self):
        card = copy.deepcopy(self.VALID_CARD)
        with self.index() as index:
            index.push_cards([card])
            self.assertEqual(
                [card],
                index.search_cards({'query': {'match_all': {}}})
            )

    def test_push_invalid_field_type(self):
        card = copy.deepcopy(self.VALID_CARD)
        card['description'] = 12345
        with self.index() as index, self.assertRaises(IndexAPIError):
            index.push_cards([card])

    def test_push_without_attachments_field(self):
        card = copy.deepcopy(self.VALID_CARD)
        card.pop('attachments')
        with self.index() as index:
            index.push_cards([card])

    def test_push_one_attachment(self):
        card = copy.deepcopy(self.VALID_CARD)
        card['attachments'].append({
            'title': 'title1',
            'origin_id': 'origin_id1',
            'type': 'type1',
            'description': 'description1',
        })
        with self.index() as index:
            index.push_cards([card])

    def test_push_other_kind(self):
        with self.index() as index:
            index.push_cards([{'id': u'my_test_id', 'kind': u'test'}])

    def test_push_without_kind(self):
        card = copy.deepcopy(self.VALID_CARD)
        del card['kind']
        with self.index() as index, self.assertRaises(IndexAPIError):
            index.push_cards([card])

    def test_push_three_attachments(self):
        card = copy.deepcopy(self.VALID_CARD)
        card['attachments'] = [{
            'title': 'title' + str(i),
            'origin_id': 'origin_id' + str(i),
            'type': 'type' + str(i),
            'description': 'description' + str(i),
        } for i in range(1, 4)]
        with self.index() as index:
            index.push_cards([card])

    def test_push_invalid_identifier(self):
        card = self.VALID_CARD.copy()
        card['id'] = 'http://foo/bar'
        with self.index() as index, self.assertRaises(IndexAPIError):
            index.push_cards([card])

    def test_push_invalid_attachment(self):
        card = copy.deepcopy(self.VALID_CARD)
        card['attachments'].append({
            'title': 'title1',
            'origin_id': 'origin_id1',
            'type': 'type1',
            'description': 'description1',
        })
        card['attachments'].append({
            'title': 'title2',
            # missing origin_id field
            'type': 'type2',
            'description': 'description2',
        })
        with self.index() as index, self.assertRaises(IndexAPIError):
            index.push_cards([card])

    def test_attachments_with_same_name(self):
        card = copy.deepcopy(self.VALID_CARD)
        attachment = {
            'title': 'title1',
            'origin_id': 'origin_id1',
            'type': 'type1',
            'description': 'description1',
        }
        card['attachments'].append(attachment)
        card['attachments'].append(attachment)
        with self.index() as index, self.assertRaises(IndexAPIError):
            index.push_cards([card])

    def test_search_invalid_query(self):
        with self.index() as index, self.assertRaises(IndexAPIError):
            index.search_cards({})

    def test_delete_thumbnails_invalid_query(self):
        with self.index() as index, self.assertRaises(IndexAPIError):
            index.delete_thumbnails({})

    def test_delete_thumbnails_valid_query(self):
        with self.index() as index:
            index.delete_thumbnails({'query': {'match_all': {}}})

    def test_delete_cards_valid_query(self):
        with self.index() as index:
            index.delete_cards({'query': {'match_all': {}}})

    def test_delete_cards_invalid_query(self):
        with self.index() as index, self.assertRaises(IndexAPIError):
            index.delete_cards([])

if __name__ == '__main__':
    unittest.main()
