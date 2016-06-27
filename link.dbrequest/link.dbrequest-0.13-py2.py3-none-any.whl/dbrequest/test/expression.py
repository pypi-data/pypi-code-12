# -*- coding: utf-8 -*-

from b3j0f.utils.ut import UTCase
from unittest import main

from link.dbrequest.expression import E, F
from link.dbrequest.comparison import C


class ExpressionTest(UTCase):
    def test_simple_expr(self):
        e = E('propname')
        ast = e.get_ast()

        self.assertEqual(
            ast,
            {
                'name': 'ref',
                'val': 'propname'
            }
        )

    def test_expr_add(self):
        e = E('propname') + 5
        ast = e.get_ast()

        self.assertEqual(
            ast,
            [
                {
                    'name': 'ref',
                    'val': 'propname'
                },
                {
                    'name': 'op',
                    'val': '+'
                },
                {
                    'name': 'val',
                    'val': 5
                }
            ]
        )

        e = 5 + E('propname')
        ast = e.get_ast()

        self.assertEqual(
            ast,
            [
                {
                    'name': 'val',
                    'val': 5
                },
                {
                    'name': 'op',
                    'val': '+'
                },
                {
                    'name': 'ref',
                    'val': 'propname'
                }
            ]
        )

    def test_expr_sub(self):
        e = E('propname') - 5
        ast = e.get_ast()

        self.assertEqual(
            ast,
            [
                {
                    'name': 'ref',
                    'val': 'propname'
                },
                {
                    'name': 'op',
                    'val': '-'
                },
                {
                    'name': 'val',
                    'val': 5
                }
            ]
        )

        e = 5 - E('propname')
        ast = e.get_ast()

        self.assertEqual(
            ast,
            [
                {
                    'name': 'val',
                    'val': 5
                },
                {
                    'name': 'op',
                    'val': '-'
                },
                {
                    'name': 'ref',
                    'val': 'propname'
                }
            ]
        )

    def test_expr_mul(self):
        e = E('propname') * 5
        ast = e.get_ast()

        self.assertEqual(
            ast,
            [
                {
                    'name': 'ref',
                    'val': 'propname'
                },
                {
                    'name': 'op',
                    'val': '*'
                },
                {
                    'name': 'val',
                    'val': 5
                }
            ]
        )

        e = 5 * E('propname')
        ast = e.get_ast()

        self.assertEqual(
            ast,
            [
                {
                    'name': 'val',
                    'val': 5
                },
                {
                    'name': 'op',
                    'val': '*'
                },
                {
                    'name': 'ref',
                    'val': 'propname'
                }
            ]
        )

    def test_expr_div(self):
        e = E('propname') / 5
        ast = e.get_ast()

        self.assertEqual(
            ast,
            [
                {
                    'name': 'ref',
                    'val': 'propname'
                },
                {
                    'name': 'op',
                    'val': '/'
                },
                {
                    'name': 'val',
                    'val': 5
                }
            ]
        )

        e = 5 / E('propname')
        ast = e.get_ast()

        self.assertEqual(
            ast,
            [
                {
                    'name': 'val',
                    'val': 5
                },
                {
                    'name': 'op',
                    'val': '/'
                },
                {
                    'name': 'ref',
                    'val': 'propname'
                }
            ]
        )

    def test_expr_pow(self):
        e = E('propname') ** 5
        ast = e.get_ast()

        self.assertEqual(
            ast,
            [
                {
                    'name': 'ref',
                    'val': 'propname'
                },
                {
                    'name': 'op',
                    'val': '**'
                },
                {
                    'name': 'val',
                    'val': 5
                }
            ]
        )

        e = 5 ** E('propname')
        ast = e.get_ast()

        self.assertEqual(
            ast,
            [
                {
                    'name': 'val',
                    'val': 5
                },
                {
                    'name': 'op',
                    'val': '**'
                },
                {
                    'name': 'ref',
                    'val': 'propname'
                }
            ]
        )

    def test_expr_lshift(self):
        e = E('propname') << 5
        ast = e.get_ast()

        self.assertEqual(
            ast,
            [
                {
                    'name': 'ref',
                    'val': 'propname'
                },
                {
                    'name': 'op',
                    'val': '<<'
                },
                {
                    'name': 'val',
                    'val': 5
                }
            ]
        )

        e = 5 << E('propname')
        ast = e.get_ast()

        self.assertEqual(
            ast,
            [
                {
                    'name': 'val',
                    'val': 5
                },
                {
                    'name': 'op',
                    'val': '<<'
                },
                {
                    'name': 'ref',
                    'val': 'propname'
                }
            ]
        )

    def test_expr_rshift(self):
        e = E('propname') >> 5
        ast = e.get_ast()

        self.assertEqual(
            ast,
            [
                {
                    'name': 'ref',
                    'val': 'propname'
                },
                {
                    'name': 'op',
                    'val': '>>'
                },
                {
                    'name': 'val',
                    'val': 5
                }
            ]
        )

        e = 5 >> E('propname')
        ast = e.get_ast()

        self.assertEqual(
            ast,
            [
                {
                    'name': 'val',
                    'val': 5
                },
                {
                    'name': 'op',
                    'val': '>>'
                },
                {
                    'name': 'ref',
                    'val': 'propname'
                }
            ]
        )

    def test_expr_and(self):
        e = E('propname') & 5
        ast = e.get_ast()

        self.assertEqual(
            ast,
            [
                {
                    'name': 'ref',
                    'val': 'propname'
                },
                {
                    'name': 'op',
                    'val': '&'
                },
                {
                    'name': 'val',
                    'val': 5
                }
            ]
        )

        e = 5 & E('propname')
        ast = e.get_ast()

        self.assertEqual(
            ast,
            [
                {
                    'name': 'val',
                    'val': 5
                },
                {
                    'name': 'op',
                    'val': '&'
                },
                {
                    'name': 'ref',
                    'val': 'propname'
                }
            ]
        )

    def test_expr_or(self):
        e = E('propname') | 5
        ast = e.get_ast()

        self.assertEqual(
            ast,
            [
                {
                    'name': 'ref',
                    'val': 'propname'
                },
                {
                    'name': 'op',
                    'val': '|'
                },
                {
                    'name': 'val',
                    'val': 5
                }
            ]
        )

        e = 5 | E('propname')
        ast = e.get_ast()

        self.assertEqual(
            ast,
            [
                {
                    'name': 'val',
                    'val': 5
                },
                {
                    'name': 'op',
                    'val': '|'
                },
                {
                    'name': 'ref',
                    'val': 'propname'
                }
            ]
        )

    def test_expr_xor(self):
        e = E('propname') ^ 5
        ast = e.get_ast()

        self.assertEqual(
            ast,
            [
                {
                    'name': 'ref',
                    'val': 'propname'
                },
                {
                    'name': 'op',
                    'val': '^'
                },
                {
                    'name': 'val',
                    'val': 5
                }
            ]
        )

        e = 5 ^ E('propname')
        ast = e.get_ast()

        self.assertEqual(
            ast,
            [
                {
                    'name': 'val',
                    'val': 5
                },
                {
                    'name': 'op',
                    'val': '^'
                },
                {
                    'name': 'ref',
                    'val': 'propname'
                }
            ]
        )

    def test_expr_func(self):
        e = F('funcname', E('propname'), E('propname') * 5)
        ast = e.get_ast()

        self.assertEqual(
            ast,
            {
                'name': 'func',
                'val': {
                    'func': 'funcname',
                    'args': [
                        {
                            'name': 'ref',
                            'val': 'propname'
                        },
                        [
                            {
                                'name': 'ref',
                                'val': 'propname'
                            },
                            {
                                'name': 'op',
                                'val': '*'
                            },
                            {
                                'name': 'val',
                                'val': 5
                            }
                        ]
                    ]
                }
            }
        )

    def test_in_condition(self):
        c = C('prop1') == E('prop2')
        ast = c.get_ast()

        self.assertEqual(
            ast,
            [
                {
                    'name': 'prop',
                    'val': 'prop1'
                },
                {
                    'name': 'cond',
                    'val': '=='
                },
                {
                    'name': 'ref',
                    'val': 'prop2'
                }
            ]
        )

        c = C('prop1') == (E('prop2') + E('prop3'))
        ast = c.get_ast()

        self.assertEqual(
            ast,
            [
                {
                    'name': 'prop',
                    'val': 'prop1'
                },
                {
                    'name': 'cond',
                    'val': '=='
                },
                [
                    {
                        'name': 'ref',
                        'val': 'prop2'
                    },
                    {
                        'name': 'op',
                        'val': '+'
                    },
                    {
                        'name': 'ref',
                        'val': 'prop3'
                    }
                ]
            ]
        )

    def test_complex_expr(self):
        e = (E('foo') + E('bar')) + (E('baz') + E('biz'))
        ast = e.get_ast()

        self.assertEqual(
            ast,
            [
                [
                    {
                        'name': 'ref',
                        'val': 'foo'
                    },
                    {
                        'name': 'op',
                        'val': '+'
                    },
                    {
                        'name': 'ref',
                        'val': 'bar'
                    }
                ],
                {
                    'name': 'op',
                    'val': '+'
                },
                [
                    {
                        'name': 'ref',
                        'val': 'baz'
                    },
                    {
                        'name': 'op',
                        'val': '+'
                    },
                    {
                        'name': 'ref',
                        'val': 'biz'
                    }
                ]
            ]
        )


if __name__ == '__main__':
    main()
