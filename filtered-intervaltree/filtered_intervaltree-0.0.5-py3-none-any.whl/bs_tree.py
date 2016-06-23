from intervaltree.bs_tree_node import BSTreeNode


class BSTree:
    """
    BinarySearchTree
    """
    def __init__(self, root=None):
        self.root = root

    def add_node(self, a_node: BSTreeNode):
        from .bs_tree_funcs import add_node
        if self.root:
            return add_node(self, a_node)
        else:
            self.root = a_node
            return a_node

    def search_for_key(self, a_key):
        from .bs_tree_funcs import search_node
        yield from search_node(self, a_key)

    def delete_node(self, a_node):
        BSTreeNode.delete_node(a_node, self)

    def inorder_walk(self):
        yield from BSTreeNode.inorder_walk(self.root, False)
