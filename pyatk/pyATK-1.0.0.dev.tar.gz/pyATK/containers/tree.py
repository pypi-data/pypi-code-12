# -*- coding: utf-8 -*-


class Node:
    def __init__(self, value):
        self.children = []
        self.value = value


class BinaryNode(Node):
    LEFT = 0
    RIGHT = 1

    def __init__(self, value):
        self.children = [None, None]
        self.value = value
    
    def left_child(self):
        return self.children[BinaryNode.LEFT]

    def right_child(self):
        return self.children[BinaryNode.RIGHT]


class BinaryTree:
    def __init__(self, root=None):
        self.root = root

    def insert(self, val):
        if self.root is None:
            self.root = BinaryNode(val)
        else:
            self._insert(self.root, val)

    def _insert(self, node, value):
        if value < node.value:
            if node.left_child() is not None:
                self._insert(value, node.left_child())
            else:
                node.left_child = Node(value)
        else:
            if node.right_child is not None:
                self._insert(value, node.right_child)
            else:
                node.right_child = Node(value)

    def remove(self, val):
        pass

    def find(self, val):
        if self.root is not None:
            return self._find(val, self.root)
        else:
            return None

    def _find(self, val, node):
        if val == node.value:
            return node
        elif val < node.value and node.children[BinaryNode.LEFT] is not None:
            self._find(val, node.children[BinaryNode.LEFT])
        elif val > node.value and node.children[BinaryNode.RIGHT] is not None:
            self._find(val, node.children[BinaryNode.RIGHT])

    def delete_tree(self):
        self.root = None

    def print_tree(self):
        if self.root is not None:
            self._print_tree(self.root)

    def _print_tree(self, node):
        if node is not None:
            self._print_tree(node.l)
            print(str(node.v) + ' ')
            self._print_tree(node.r)
