from intervaltree.bs_tree_node import *


class RBTreeNode(BSTreeNode):

    def __init__(self, key=None,
                 parent=None,
                 left_child=None,
                 right_child=None,
                 tree=None):
        self.black = None
        super().__init__(key, parent, left_child, right_child, tree)

    @property
    def color(self) -> str:
        return self.black and "black" or "red"

    @color.setter
    def color(self, value:str):
        self.black = value is "black"

    @property
    def is_root(self):
        return self is self.tree.root

    @property
    def red(self) -> bool:
        return not self.black

    @red.setter
    def red(self, value:bool):
        self.black = not value

    @staticmethod
    def left_rotate(tree, node):
        from intervaltree import rb_tree_funcs
        rb_tree_funcs.left_rotate(tree, node)

    @staticmethod
    def right_rotate(tree, node):
        from intervaltree import rb_tree_funcs
        rb_tree_funcs.right_rotate(tree, node)

    def __bool__(self) -> bool:
        return self is not self.tree.nil
