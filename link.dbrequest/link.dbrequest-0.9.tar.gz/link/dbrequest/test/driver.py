# -*- coding: utf-8 -*-

from b3j0f.utils.ut import UTCase
from mock import MagicMock, Mock
from unittest import main

from link.dbrequest.model import Model, Cursor
from link.dbrequest.driver import Driver


class DriverTest(UTCase):
    def setUp(self):
        self.conn = 'myconn'

        self.driver = Driver()
        self.driver._connect = MagicMock(return_value=self.conn)
        self.driver._disconnect = MagicMock()
        self.driver._isconnected = MagicMock(
            side_effect=lambda conn: conn is not None
        )

    def tearDown(self):
        self.driver.disconnect()

        self.driver._connect.assert_called_once_with()
        self.driver._disconnect.assert_called_once_with(self.conn)
        self.driver._isconnected.assert_any_call(self.conn)

    def test_count_elements(self):
        self.driver._process_query = MagicMock(return_value=3)
        ast = [
            {
                'name': 'filter',
                'val': [
                    {
                        'name': 'prop',
                        'val': 'foo'
                    },
                    {
                        'name': 'cond',
                        'val': '=='
                    },
                    {
                        'name': 'val',
                        'val': 'bar'
                    }
                ]
            }
        ]

        result = self.driver.count_elements(ast)

        self.assertEqual(result, 3)
        self.driver._process_query.assert_called_with(self.conn, {
            'type': Driver.QUERY_COUNT,
            'filter': ast
        })

    def test_put_elements(self):
        expected = {
            '_id': 'some id',
            'foo': 'bar'
        }

        self.driver._process_query = MagicMock(return_value=expected)
        ast = [
            [
                {
                    'name': 'prop',
                    'val': 'foo'
                },
                {
                    'name': 'assign',
                    'val': {
                        'name': 'val',
                        'val': 'bar'
                    }
                }
            ]
        ]

        result = self.driver.put_element(ast)

        self.assertIsInstance(result, Model)
        self.assertEqual(result.data, expected)
        self.driver._process_query.assert_called_with(self.conn, {
            'type': Driver.QUERY_CREATE,
            'update': ast
        })

    def test_find_elements(self):
        expected = [
            {'_id': 'some id 1', 'foo': 'bar', 'i': 5},
            {'_id': 'some id 2', 'foo': 'bar', 'i': 9},
            {'_id': 'some id 3', 'foo': 'bar', 'i': 15}
        ]
        iterator = iter(expected)

        fake_cursor = Mock()
        fake_cursor_next = lambda self: next(iterator)
        attrs = {
            'next.side_effect': fake_cursor_next,  # Python2 compatiblity
        }
        fake_cursor.configure_mock(**attrs)
        fake_cursor.__next__ = fake_cursor_next
        fake_cursor.__len__ = lambda self: len(expected)
        fake_cursor.__getitem__ = lambda self, idx: expected.__getitem__(idx)

        self.driver._process_query = MagicMock(return_value=fake_cursor)
        ast = [
            {
                'name': 'filter',
                'val': [
                    {
                        'name': 'prop',
                        'val': 'foo'
                    },
                    {
                        'name': 'cond',
                        'val': '=='
                    },
                    {
                        'name': 'val',
                        'val': 'bar'
                    }
                ]
            }
        ]

        cursor = self.driver.find_elements(ast)

        self.assertIsInstance(cursor, Cursor)
        self.assertIsInstance(cursor[0], Model)
        self.assertEqual(len(cursor), len(expected))
        self.assertEqual([model.data for model in cursor], expected)

        self.driver._process_query.assert_called_with(self.conn, {
            'type': Driver.QUERY_READ,
            'filter': ast
        })

    def test_update_elements(self):
        self.driver._process_query = MagicMock(return_value=3)
        filter_ast = [
            {
                'name': 'filter',
                'val': [
                    {
                        'name': 'prop',
                        'val': 'foo'
                    },
                    {
                        'name': 'cond',
                        'val': '=='
                    },
                    {
                        'name': 'val',
                        'val': 'bar'
                    }
                ]
            }
        ]
        update_ast = [
            [
                {
                    'name': 'prop',
                    'val': 'foo'
                },
                {
                    'name': 'assign',
                    'val': {
                        'name': 'val',
                        'val': 'bar'
                    }
                }
            ]
        ]

        result = self.driver.update_elements(filter_ast, update_ast)

        self.assertEqual(result, 3)
        self.driver._process_query.assert_called_with(self.conn, {
            'type': Driver.QUERY_UPDATE,
            'filter': filter_ast,
            'update': update_ast
        })

    def test_remove_elements(self):
        self.driver._process_query = MagicMock(return_value=3)
        ast = [
            {
                'name': 'filter',
                'val': [
                    {
                        'name': 'prop',
                        'val': 'foo'
                    },
                    {
                        'name': 'cond',
                        'val': '=='
                    },
                    {
                        'name': 'val',
                        'val': 'bar'
                    }
                ]
            }
        ]

        result = self.driver.remove_elements(ast)

        self.assertEqual(result, 3)
        self.driver._process_query.assert_called_with(self.conn, {
            'type': Driver.QUERY_DELETE,
            'filter': ast
        })


if __name__ == '__main__':
    main()
