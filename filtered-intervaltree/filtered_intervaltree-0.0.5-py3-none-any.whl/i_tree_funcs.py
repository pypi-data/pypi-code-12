from intervaltree.interval import Interval, interval_overlaps, interval_contains
from .rb_tree import RBTree
from .rb_tree import RBTreeNode
from .rb_tree_funcs import redblack_insert_fixup, left_rotate as rb_lr, right_rotate as rb_rr, \
    rb_delete_fixup as rb_df, tree_successor
from .easy_hashes import hash_to_64
import math
from typing import Generator
from collections import deque


def check_contains(node: 'FilterableIntervalTreeNode', content: 'FilterableIntervalTreeNode'):
    """
    checks to see if the specified content is available in the node's subtrees
    :param node: node root to search
    :param content: content to search for, cand be a filterablenode, a filter vector, or content that generates a filter vector
    :return: true if available
    """
    is_contained = content.filter_vector & node.subtree_filter_vector == content.filter_vector

    return is_contained


def generate_query_node(begin: int=-math.inf, end: int=math.inf, payload=None, filter_vector: int=None):
    tmp_interval = Interval(begin, end)
    vector = None
    if filter_vector is None:
        if hasattr(payload, 'filter_vector'):
            vector = payload.filter_vector
    elif isinstance(filter_vector, int):
        vector = filter_vector
    tmp_node = FilterableIntervalTreeNode(tmp_interval, payload, vector)
    return tmp_node


class FilterableIntervalTreeNode(RBTreeNode):

    def __init__(self, key: Interval, payload=None, filter_vector: int = None):
        self.key = key,
        self.payload = payload or None
        if key is not None:
            self.subtree_maximum = key.end

        if hasattr(payload, 'qualifies'):
            self.qualifies = payload.qualifies
        else:
            self.qualifies = payload.__eq__

        if filter_vector is None:
            if hasattr(payload, 'filter_vector'):
                self.filter_vector = payload.filter_vector
            else:
                self.filter_vector = generate_basic_filter_vector(str(payload))
        else:
            self.filter_vector = filter_vector
        self.subtree_filter_vector = self.filter_vector
        super().__init__(key)

    def __contains__(self, item: 'FilterableIntervalTreeNode'):
        return check_contains(self, item)


class FilterableIntervalTree(RBTree):

    def __init__(self):
        super().__init__()
        self.nil = FilterableIntervalTreeNode(None, None, 0)
        self.nil.black = True
        self.nil.tree = self
        self.nil.subtree_maximum = -math.inf
        self.root = self.nil


def generate_basic_filter_vector(value: str):
    bit_indexes = hash_to_64(value, 5)
    result = 0
    for i in bit_indexes:
        result |= 1 << i
    return result


def update_subtree_filter_vector(node: FilterableIntervalTreeNode):
    a = node.left_child
    b = node.right_child
    node.subtree_filter_vector = a.subtree_filter_vector | b.subtree_filter_vector | node.filter_vector


def update_subtree_max_after_rotate(node: FilterableIntervalTreeNode):
    pm = node.parent.subtree_maximum
    p_less = pm < node.subtree_maximum
    if p_less:
        node.parent.subtree_maximum = node.subtree_maximum
    else:
        gsm = node.left_child.subtree_maximum
        asm = node.right_child.subtree_maximum
        node.subtree_maximum = max(
            node.key.end,
            gsm,
            asm
        )


def left_rotate(tree: FilterableIntervalTree, node: FilterableIntervalTreeNode):
    result = rb_lr(tree, node)
    update_subtree_filter_vector(node)
    update_subtree_filter_vector(node.parent)
    update_subtree_max_after_rotate(node)
    return node


def right_rotate(tree: FilterableIntervalTree, node: FilterableIntervalTreeNode):
    result = rb_rr(tree, node)
    update_subtree_filter_vector(node)
    update_subtree_filter_vector(node.parent)
    update_subtree_max_after_rotate(node)
    return node


def add_node(tree: FilterableIntervalTree, node: FilterableIntervalTreeNode) -> FilterableIntervalTreeNode:
    node.tree = tree
    node.left_child = node.right_child = tree.nil
    end = node.key.end
    begin = node.key.begin
    if tree.root is tree.nil:
        tree.root = node
        node.parent = tree.nil
        node.black = True
        return node

    current_node = last_parent = tree.root
    going_left = None
    while current_node is not tree.nil:
        last_parent = current_node
        going_left = begin <= current_node.key.begin
        if end > current_node.subtree_maximum:
            current_node.subtree_maximum = end
        current_node.subtree_filter_vector |= node.filter_vector
        current_node = last_parent.left_child if going_left else last_parent.right_child

    if going_left:
        last_parent.left_child = node
    else:
        last_parent.right_child = node
    node.parent = last_parent
    redblack_insert_fixup(tree, node, left_rotate_func=left_rotate, right_rotate_func=right_rotate)


def transplant(tree, a_node: FilterableIntervalTreeNode, a_replacement: FilterableIntervalTreeNode):
    u = a_node
    u_parent = u.parent
    v = a_replacement
    if u.subtree_maximum == u.key.end:
        v.subtree_maximum = max(u.left_child.subtree_maximum, u.right_child.subtree_maximum, v.subtree_maximum)
    else:
        v.subtree_maximum = max(u.subtree_maximum, v.subtree_maximum)
    if u is tree.root:
        tree.root = v
    elif u is u_parent.left_child:
        u_parent.left_child = v
    else:
        u_parent.right_child = v
    v.parent = u_parent
    if u_parent is not tree.nil:
        update_subtree_filter_vector(u_parent)


def update_statistics_in_chain(tree: FilterableIntervalTree, node: FilterableIntervalTreeNode):
    parent = node.parent
    no_updates = 0
    while parent is not tree.nil and no_updates < 400:
        expected_max = max(
            parent.key.end,
            parent.left_child.subtree_maximum,
            parent.right_child.subtree_maximum
        )

        expected_sfv = \
            parent.left_child.subtree_filter_vector | \
            parent.right_child.subtree_filter_vector | \
            parent.filter_vector

        needs_update = (expected_max != parent.subtree_maximum) or \
                       (expected_sfv != parent.subtree_filter_vector)

        if needs_update:
            parent.subtree_maximum = expected_max
            parent.subtree_filter_vector = expected_sfv
        else:
            no_updates += 1

        parent = parent.parent


def delete_node(tree: FilterableIntervalTree, node: FilterableIntervalTreeNode):
    z = node
    y = z
    y_original_color = y.color

    if z.left_child is tree.nil:
        x = z.right_child
        transplant(tree, z, z.right_child)
    elif z.right_child is tree.nil:
        x = z.left_child
        transplant(tree, z, z.left_child)
    else:
        y = tree_successor(tree, z)
        y_original_color = y.color
        x = y.right_child
        if y.parent is z:
            x.parent = y
        else:
            transplant(tree, y, y.right_child)
            y.right_child = z.right_child
            y.right_child.parent = y
            # TODO figure out how to update SFV and max only when a node is removed from a particular subtree
            # y.subtree_filter_vector = z.right_child.subtree_filter_vector | y.filter_vector

        y.left_child = z.left_child
        y.left_child.parent = y
        # y.subtree_filter_vector |= z.left_child.subtree_filter_vector
        transplant(tree, z, y)
        y.color = z.color
    if y_original_color is "black":
        rb_df(tree, x, left_rotate, right_rotate)

    update_statistics_in_chain(tree, x)
    tree.nil.parent = None


def search_interval(tree: FilterableIntervalTree, interval: Interval) -> FilterableIntervalTreeNode:
    x = tree.root
    while x and not interval.overlaps(x.key):
        if x.left_child and x.left_child.subtree_maximum > interval.begin:
            x = x.left_child
        else:
            x = x.right_child
    return x


def query_tree(
        tree: FilterableIntervalTree,
        query_node: FilterableIntervalTreeNode,
        must_contain=True,
        ) -> Generator[FilterableIntervalTreeNode, None, None]:

    query_interval = query_node.key
    query_interval_begin = query_interval.begin
    query_interval_end = query_interval.end
    query_fv = query_node.filter_vector
    qualifier = query_node.qualifies

    track = 0

    search_queue = deque()
    search_queue.append(tree.root)
    interval_operation = interval_contains if must_contain else interval_overlaps
    not_root = False
    while search_queue:
        track += 1
        current_node = search_queue.pop()
        current_node_qualifies = interval_operation(current_node.key, query_interval) \
            and qualifier(current_node.payload)
        if current_node_qualifies:
            yield current_node

        left_child = current_node.left_child
        right_child = current_node.right_child

        left_ok = left_child is not tree.nil and \
            left_child.subtree_maximum >= query_interval_begin

        left_ok &= (query_fv & left_child.subtree_filter_vector == query_fv)

        right_ok = right_child is not tree.nil and \
            right_child.subtree_maximum >= query_interval_begin

        if must_contain and not_root:
            # TODO there's another relationship that can be used to filter here
            right_ok &= right_child.subtree_maximum >= query_interval_end

        right_ok &= (query_fv & right_child.subtree_filter_vector == query_fv)

        if right_ok:
            search_queue.append(right_child)

        if left_ok:
            search_queue.append(left_child)

        not_root = True
