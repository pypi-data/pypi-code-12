from intervaltree.rb_tree_node import RBTreeNode
from intervaltree.bs_tree import BSTree
from intervaltree.print_tree import *


# 1: every node is either red or black
# 2: the root is black
# 3: every leaf (nil) is black
# 4: if a node is red then both its children are black
# 5: for each node, all simple paths from the node to the leaves contain the same number of black nodes

class RBTree(BSTree):
    """
    RedBlack Tree
    """

    def __init__(self, root=None):
        self.nil = RBTreeNode()
        self.nil.black = True
        self.nil.tree = self

        super().__init__(root)

    def add_node(self, a_node: RBTreeNode):
        a_node.tree = self
        a_node.left_child = a_node.right_child = self.nil

        result = super().add_node(a_node)
        if a_node is self.root:
            a_node.black = True
            a_node.parent = self.nil

        from intervaltree import rb_tree_funcs
        rb_tree_funcs.redblack_insert_fixup(self, a_node)

        return result

    @staticmethod
    def transplant(tree, a_node: RBTreeNode, a_replacement: RBTreeNode):
        from .rb_tree_funcs import transplant
        transplant(tree, a_node, a_replacement)

    @staticmethod
    def delete_node(tree, node: RBTreeNode):
        from .rb_tree_funcs import delete_node
        delete_node(tree, node)

    @staticmethod
    def rb_delete_fixup(node, tree):
        from .rb_tree_funcs import rb_delete_fixup
        return rb_delete_fixup(tree, node)

