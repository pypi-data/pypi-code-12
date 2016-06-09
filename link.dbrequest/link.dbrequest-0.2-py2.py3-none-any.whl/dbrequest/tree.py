# -*- coding: utf-8 -*-

from link.dbrequest.ast import AST


class Node(object):
    def __init__(self, name, *args, **kwargs):
        super(Node, self).__init__(*args, **kwargs)

        self.name = name

    def get_ast(self):
        return AST('node', self.name)


class Value(Node):
    def get_ast(self):
        return AST('val', self.name)
