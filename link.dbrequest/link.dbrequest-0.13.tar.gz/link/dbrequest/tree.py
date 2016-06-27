# -*- coding: utf-8 -*-

from link.dbrequest.ast import AST


class Node(object):
    """
    Base class for AST nodes.

    :param name: Node's value.
    """

    def __init__(self, name, *args, **kwargs):
        super(Node, self).__init__(*args, **kwargs)

        self.name = name

    def get_ast(self):
        """
        Returns simplified AST.

        :returns: AST node as dict
        :rtype: dict
        """

        return AST('node', self.name)


class Value(Node):
    """
    Node representing a value.
    """

    def get_ast(self):
        return AST('val', self.name)
