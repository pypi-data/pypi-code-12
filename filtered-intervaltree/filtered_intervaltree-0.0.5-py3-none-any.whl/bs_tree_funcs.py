from .bs_tree import BSTree
from .bs_tree_node import BSTreeNode
from typing import Generator
from queue import LifoQueue


_node_relationships = [
    ("left_child", lambda x, y: x == y.left_child),
    ("right_child", lambda x, y: x == y.right_child),
    ("parent", lambda x, y: x == y.parent),
    ("left_sibling", lambda x, y: x.parent and x.parent.left_child == x and x.parent.right_child == y),
    ("right_sibling", lambda x, y: x.parent and x.parent.right_child == x and x.parent.left_child == y)
]


def get_relationship_between_nodes(node_to_evaluate: BSTreeNode, node_relative: BSTreeNode, max_depth=3) -> str:
    """
    Returns the relationship of a a_node to its relative
    :param node_to_evaluate: node being evaluated
    :param node_relative: node reference
    :param max_depth: number of relationships to evaluate before returning none
    :return: "left_child" if node_to_evaluate is node_relative's left_child
    """
    i = 0
    if node_relative:
        for k, v in _node_relationships:
            if v(node_to_evaluate, node_relative):
                return k
            i += 1
            if i >= max_depth:
                return None
    return None


def add_node(tree: BSTree, node: BSTreeNode) -> BSTreeNode:
    current_parent = last_parent = tree.root
    while current_parent and current_parent.key:
        last_parent = current_parent
        operative_child_string = node.key <= current_parent.key \
                                 and "left_child" or "right_child"
        current_parent = getattr(current_parent, operative_child_string)
    setattr(last_parent, operative_child_string, node)
    node.parent = last_parent
    return node


def transplant(tree: BSTree, a_node_to_replace: BSTreeNode, a_replacing_node: BSTreeNode):
    parent = a_node_to_replace.parent
    if not a_node_to_replace.parent:
        tree.root = a_replacing_node
    elif a_node_to_replace is parent.left_child:
        parent.left_child = a_replacing_node
    else:
        parent.right_child = a_replacing_node
    if a_replacing_node:
        a_replacing_node.parent = parent


def get_extreme_from_node(a_node: BSTreeNode, direction: str ="min") -> BSTreeNode:
    """
    gets the extreme node in a node's subtree or itself
    :param a_node: node to start from
    :param direction: "min" or "max"
    :return: a node
    """
    direction_key = direction == "min" and "left_child" or "right_child"
    current_node = result = a_node
    while current_node:
        next_item = getattr(current_node, direction_key)
        result = current_node
        current_node = next_item
    return result


def delete_node(tree: BSTree, node: BSTreeNode):
    if not node.left_child:
        transplant(tree, node, node.right_child)
    elif not node.right_child:
        transplant(tree, node, node.left_child)
    else:
        op_child = get_extreme_from_node(node.right_child)
        if op_child.parent is not node:
            transplant(tree, op_child, op_child.right_child)
            op_child.right_child = node.right_child
            op_child.right_child.parent = op_child
        transplant(tree, node, op_child)
        op_child.left_child = node.left_child
        op_child.left_child.parent = op_child


def search_node(tree: BSTree, key, recursive=False) -> Generator[BSTreeNode, None, None]:
    if recursive:
        yield from _search_node_recursive(tree.root, key)
    else:
        yield from _search_node_non_recursive(tree.root, key)


def _search_node_recursive(a_node: BSTreeNode, a_key) -> Generator[BSTreeNode, None, None]:
    if not a_node:
        return

    if a_node.key == a_key:
        yield a_node

    # TODO this will change when switching to tuples

    direction_key = a_key <= a_node.key and "left_child" or "right_child"
    next_node = getattr(a_node, direction_key)
    yield from search_node(next_node, a_key)


def _search_node_non_recursive(a_node: BSTreeNode, a_key) -> Generator[BSTreeNode, None, None]:
    current_node = a_node

    while current_node:
        if current_node.key == a_key:
            yield current_node

        # TODO this will change when switching to tuples

        direction_key = a_key <= current_node.key and "left_child" or "right_child"
        current_node = getattr(current_node, direction_key)


def inorder_walk(a_root_node: BSTreeNode):
    node_stack = LifoQueue()
    current_item = a_root_node
    while True:
        while current_item:
            node_stack.put(current_item)
            current_item = current_item.left_child
        if node_stack.empty():
            break
        tmp_item = node_stack.get()
        yield tmp_item

        current_item = tmp_item.right_child