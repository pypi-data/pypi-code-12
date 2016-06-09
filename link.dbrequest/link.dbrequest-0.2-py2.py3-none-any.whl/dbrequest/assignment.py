# -*- coding: utf-8 -*-

from link.dbrequest.tree import Node, Value
from link.dbrequest.ast import AST


class A(Node):
    def __init__(self, propname, val=None, unset=False, *args, **kwargs):
        super(A, self).__init__(propname, *args, **kwargs)

        if unset:
            val = None

        elif not isinstance(val, Node):
            val = Value(val)

        self.value = val

    def get_ast(self):
        return [
            AST('prop', self.name),
            AST(
                'assign',
                self.value.get_ast() if self.value is not None else self.value
            )
        ]
