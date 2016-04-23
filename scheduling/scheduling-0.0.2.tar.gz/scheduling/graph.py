#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Authors:
#   Alex Vinyals <alevinval@gmail.com> - 2015
#
""" Graph utilities
"""
from collections import deque


def expansion_all(node):
    return node.all


def expansion_children(node):
    return node.children


class DependencyGraphNode:
    """ A node can have only one parent ( the one who wraps the task ),
    multiple relatives or dependencies to wait for,
    multiple siblings or wrapped tasks,
    multiple children or dependants on it
    """

    def __init__(self, task):
        # Task stored in the node
        self.task = task

        # Node visiting stats
        self.visits = 0
        self.pruned = False

        # Node links
        self.parent = None
        self.all = set()
        self.relatives = set()
        self.siblings = set()
        self.children = set()

    def add_relative(self, parent):
        self.relatives.add(parent)
        self.all.add(parent)

    def add_children(self, children):
        self.children.add(children)
        self.all.add(children)

    def add_sibling(self, sibling):
        self.siblings.add(sibling)
        self.all.add(sibling)

    def set_parent(self, parent):
        self.parent = parent

    def reset_visits(self):
        self.visits = 0

    def depends(self, *nodes):
        """ Adds nodes as relatives to this one, and
        updates the relatives with self as children.
        :param nodes: GraphNode(s)
        """
        for node in nodes:
            self.add_relative(node)
            node.add_children(self)

    def then(self, *nodes):
        """ Inverse of the `depends` method
        :param nodes: GraphNode(s)
        """
        for node in nodes:
            node.depends(self)

    def add(self, *nodes):
        """ Adds nodes as siblings
        :param nodes: GraphNode(s)
        """
        for node in nodes:
            node.set_parent(self)
            self.add_sibling(node)

    def prune(self):
        self.pruned = True


def dfs(node, expand=expansion_all, callback=None, silent=True):
    """ Perform a depth-first search on the node graph
    :param node: GraphNode
    :param expand: Returns the list of Nodes to explore from a Node
    :param callback: Callback to run in each node
    :param silent: Don't throw exception on circular dependency
    :return:
    """
    nodes = deque()
    for n in expand(node):
        nodes.append(n)

    while nodes:
        n = nodes.pop()
        n.visits += 1
        if callback:
            callback(n)
        for k in expand(n):
            if k.visits < 1:
                nodes.append(k)
            else:
                if not silent:
                    raise CircularDependency('Circular Dependency')


def explore(node):
    """ Given a node, explores on relatives, siblings and children
    :param node: GraphNode from which to explore
    :return: set of explored GraphNodes
    """
    explored = set()
    explored.add(node)
    dfs(node, callback=lambda n: explored.add(n))
    return explored


def detect_cycles(nodes):
    for node in nodes:
        if not node.pruned:
            explored = []
            dfs(node,
                callback=lambda n: explored.append(n) and n.prune(),
                expand=expansion_children,
                silent=False)
            reset_visits(explored)


def reset_visits(nodes):
    """ Resets the visitor counter in a set of nodes
    :param nodes: GraphNodes
    :return:
    """
    for node in nodes:
        node.visits = 0


class CircularDependency(Exception):
    """ Exception raised when there is a circular dependency in the
    dependency graph
    """
    pass
