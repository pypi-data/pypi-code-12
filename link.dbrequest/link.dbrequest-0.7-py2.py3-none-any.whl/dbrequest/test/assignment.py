# -*- coding: utf-8 -*-

from b3j0f.utils.ut import UTCase
from unittest import main

from link.dbrequest.expression import E
from link.dbrequest.assignment import A


class ExpressionTest(UTCase):
    def test_simple_assign(self):
        a = A('foo', 'bar')
        ast = a.get_ast()

        self.assertEqual(
            ast,
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
        )

    def test_assign_expr(self):
        a = A('foo', E('bar'))
        ast = a.get_ast()

        self.assertEqual(
            ast,
            [
                {
                    'name': 'prop',
                    'val': 'foo'
                },
                {
                    'name': 'assign',
                    'val': {
                        'name': 'ref',
                        'val': 'bar'
                    }
                }
            ]
        )

    def test_unassign(self):
        a = A('foo', unset=True)
        ast = a.get_ast()

        self.assertEqual(
            ast,
            [
                {
                    'name': 'prop',
                    'val': 'foo'
                },
                {
                    'name': 'assign',
                    'val': None
                }
            ]
        )


if __name__ == '__main__':
    main()
