# -*- coding: utf-8 -*-

from b3j0f.utils.ut import UTCase
from unittest import main

from link.dbrequest.tree import Node, Value


class TreeTest(UTCase):
    def test_node(self):
        n = Node('foo')
        ast = n.get_ast()

        self.assertEqual(ast, {
            'name': 'node',
            'val': 'foo'
        })

    def test_value(self):
        v = Value(5)
        ast = v.get_ast()

        self.assertEqual(ast, {
            'name': 'val',
            'val': 5
        })


if __name__ == '__main__':
    main()
