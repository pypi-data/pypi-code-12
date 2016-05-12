# -*- coding: utf-8 -*-

import ast
import types
import collections

class ChurnVisitor(ast.NodeVisitor):

    def __init__(self, path, changes):
        self.path = path
        self.changes = changes
        self.nodes = []

    def visit_FunctionDef(self, node, parent=None):
        self.report(node, parent=parent)

    def visit_ClassDef(self, node):
        self.report(node)
        for child in node.body:
            if isinstance(child, ast.FunctionDef):
                self.visit_FunctionDef(child, parent=node)

    def report(self, node, parent=None):
        node.parent = parent
        node.lineno_end = get_lineno_end(node)
        if self.changes.intersection(range(node.lineno, node.lineno_end + 1)):
            self.nodes.append(
                Node(
                    self.path,
                    get_type(node),
                    node.name,
                    node.parent.name if parent else None,
                )
            )

    @classmethod
    def extract(cls, path, node, changes):
        instance = cls(path, changes)
        instance.visit(node)
        return instance.nodes

def get_lineno_end(node):
    return max(
        child.lineno
        for child in iter_terminal(node)
        if hasattr(child, 'lineno')
    )

def iter_terminal(node):
    children = list(ast.iter_child_nodes(node))
    if children:
        yield children[-1]
        for grandchild in iter_terminal(children[-1]):
            yield grandchild

Node = collections.namedtuple(
    'Node',
    ['file', 'type', 'name', 'parent'],
)

def get_type(node):
    if isinstance(node, ast.ClassDef):
        return type
    assert isinstance(node, ast.FunctionDef)
    return types.MethodType if node.parent else types.FunctionType
