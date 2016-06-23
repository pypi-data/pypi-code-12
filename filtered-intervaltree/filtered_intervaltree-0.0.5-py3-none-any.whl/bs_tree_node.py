from queue import LifoQueue


class BSTreeNode():
    # __slots__ = ()

    # TODO refactor into namedtuple for better memory usage

    def __init__(self,
                 key=None,
                 parent=None,
                 left_child=None,
                 right_child=None,
                 tree=None):
        self.key = key
        self.parent = parent
        self.left_child = left_child
        self.right_child = right_child
        self.tree = tree

    @property
    def parent_relationship(self) -> str:
        """
        gets the relationship between the parent and this child
        :return: "left_child" if the node is the left child, else "right_child"
        """
        return BSTreeNode.get_relationship_between_nodes(self, self.parent)

    @property
    def depth(self):
        return BSTreeNode.get_depth(self)

    @staticmethod
    def get_depth(a_node):
        depth = 0
        tmp = a_node
        while tmp.parent:
            tmp = tmp.parent
            depth += 1
        return depth

    @staticmethod
    def preorder_walk(a_root_node, recursive=True):
        yield from BSTreeNode._preorder_walk_recursive(a_root_node)

    @staticmethod
    def _preorder_walk_recursive(a_root_node):
        if not a_root_node:
            return
        yield a_root_node
        yield from BSTreeNode._preorder_walk_recursive(a_root_node.left_child)
        yield from BSTreeNode._preorder_walk_recursive(a_root_node.right_child)

    @staticmethod
    def inorder_walk(a_root_node, recursive=False):
        if recursive:
            yield from BSTreeNode._inorder_walk_recursive(a_root_node)
        else:
            from .bs_tree_funcs import inorder_walk
            yield from inorder_walk(a_root_node)

    @staticmethod
    def _inorder_walk_recursive(a_node):
        if not a_node:
            return
        yield from BSTreeNode._inorder_walk_recursive(a_node.left_child)
        yield a_node
        yield from BSTreeNode._inorder_walk_recursive(a_node.right_child)

    @staticmethod
    def get_minimum(a_node):
        from .bs_tree_funcs import get_extreme_from_node
        return get_extreme_from_node(a_node)

    @staticmethod
    def get_maximum(a_node):
        from .bs_tree_funcs import get_extreme_from_node
        return get_extreme_from_node(a_node, "max")

    @staticmethod
    def get_successor_for_node(a_node):
        if a_node.right_child:
            return BSTreeNode.get_minimum(a_node.right_child)
        current_node = a_node
        result = a_node.parent
        while result and current_node == result.right_child:
            current_node = result
            result = current_node.parent
        return result

    @staticmethod
    def get_predecessor_for_node(a_node):
        if a_node.left_child:
            return BSTreeNode.get_minimum(a_node.left_child)
        current_node = a_node
        result = a_node.parent
        while result and current_node == result.left_child:
            current_node = result
            result = current_node.parent
        return result

    @staticmethod
    def get_relationship_between_nodes(node_to_evaluate, node_relative):
        from .bs_tree_funcs import get_relationship_between_nodes
        return get_relationship_between_nodes(node_to_evaluate, node_relative)

    @staticmethod
    def delete_node(a_node, a_tree=None):
        from .bs_tree_funcs import delete_node
        delete_node(a_tree, a_node)




