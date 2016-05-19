# -*- coding: utf-8 -*-
from __future__ import print_function

from collections import deque


class CircularDependencyException(Exception):
    pass


class Graph(object):

    def __init__(self):
        self._nodes = []
        self._edges = {}

    @property
    def nodes(self):
        return self._nodes

    @property
    def edges(self):
        return self._edges

    def add_node(self, node):
        self._nodes.append(node)
        self._edges[node] = []

    def add_edge(self, node1, node2):
        self._edges[node1].append(node2)

    def predecessors(self, node):
        return [predecessor for predecessor in self._edges if node in self._edges[predecessor]]

    def add_nodes_from(self, iterable):
        for node in iterable:
            self.add_node(node)


class DependencyGraph(object):

    def __init__(self, tasks):
        super(DependencyGraph, self).__init__()
        self.tasks = tasks
        self._graph = Graph()
        self._build_graph()

    def _build_graph(self):
        """ Produce a dependency graph based on a list
            of tasks produced by the parser.
        """
        self._graph.add_nodes_from(self.tasks)
        for node1 in self._graph.nodes:
            for node2 in self._graph.nodes:
                for input_file in node1.inputs:
                    for output_file in node2.outputs:
                        if output_file == input_file:
                            self._graph.add_edge(node2, node1)
        for order, task in enumerate(topological_sort(self._graph)):
            task.predecessors = self._graph.predecessors(task)
            task.order = order

    def show_tasks(self):
        for task in topological_sort(self._graph):
            print("Task {0}  ******************************".format(task.order))
            print("Predecessors: {0}".format(task.predecessors))
            print("options: {0}".format(task.options))
            print("Interpreter: {0}".format(task.interpreter))
            print("Environment: {0}".format(task.environment))
            print("Inputs: {0}".format(task.inputs))
            print("Outputs: {0}".format(task.outputs))
            print("Code:")
            for line in task.code:
                print("{0}".format(line))
        print("**************************************")

    def execute(self):
        """
        Execute tasks in the graph (already in order).
        """
        for task in self.tasks:
            print(80 * "*")
            task()
            print(80 * "*")


def topological_sort(graph):
    def visit(node):
        if node in tmp:
            raise CircularDependencyException("Circular dependency found.")
        elif node not in visited:
            tmp.append(node)
            for child_node in graph.edges[node]:
                visit(child_node)
            visited.append(node)
            tmp.remove(node)
            result.appendleft(node)
    result = deque()
    visited = []
    tmp = []
    n = 0
    while len(visited) < len(graph.nodes):
        node = graph.nodes[n]
        visit(node)
        n += 1
    return result

