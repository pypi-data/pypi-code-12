from .rb_tree import RBTree
from .rb_tree_node import RBTreeNode
from types import FunctionType
from .bs_tree_funcs import BSTree, add_node as bst_add_node, get_extreme_from_node


def left_rotate(tree: RBTree, a_node: RBTreeNode):

    x = a_node
    y = x.right_child
    x.right_child = y.left_child
    if y.left_child:
        y.left_child.parent = x
    y.parent = x.parent
    if x.parent is tree.nil:
        tree.root = y
    elif x is x.parent.left_child:
        x.parent.left_child = y
    else:
        x.parent.right_child = y
    y.left_child = x
    x.parent = y
    return a_node


def right_rotate(tree: RBTree, a_node: RBTreeNode):
    y = a_node
    x = y.left_child
    y_parent_relationship = RBTreeNode.get_relationship_between_nodes(y, y.parent)
    if x:
        y.left_child = x.right_child
        if y.left_child:
            y.left_child.parent = y
        x.parent = y.parent
        if x.parent is tree.nil:
            tree.root = x
        if y_parent_relationship:
            setattr(y.parent, y_parent_relationship, x)
        y.parent = x
        x.right_child = y
    return a_node


def redblack_insert_fixup(tree: RBTree,
                          a_node: RBTreeNode,
                          left_rotate_func: FunctionType = left_rotate,
                          right_rotate_func: FunctionType = right_rotate):
    z = a_node
    while z.parent.red:
        if z.parent is z.parent.parent.left_child:
            y = z.parent.parent.right_child
            if y.red:
                z.parent.black = True
                y.black = True
                z.parent.parent.red = True
                z = z.parent.parent
            else:
                if z is z.parent.right_child:
                    z = z.parent
                    left_rotate_func(tree, z)
                z.parent.black = True
                z.parent.parent.red = True
                right_rotate_func(tree, z.parent.parent)
        else:
            y = z.parent.parent.left_child
            if y.red:
                z.parent.black = True
                y.black = True
                z.parent.parent.red = True
                z = z.parent.parent
            else:
                if z is z.parent.left_child:
                    z = z.parent
                    right_rotate_func(tree, z)
                z.parent.black = True
                z.parent.parent.red = True
                left_rotate_func(tree, z.parent.parent)
    tree.root.black = True


def rb_delete_fixup(tree: RBTree, node: RBTreeNode,
                    left_rotate_func=left_rotate, right_rotate_func=right_rotate):
    x = node
    while x is not tree.root and x.black:
        if x is x.parent.left_child:
            w = x.parent.right_child
            if w.red:
                w.black = True
                x.parent.red = True
                left_rotate_func(tree, x.parent)
                w = x.parent.right_child
            if w.left_child.black and w.right_child.black:
                w.red = True
                x = x.parent
            else:
                if w.right_child.black:
                    w.left_child.black = True
                    w.red = True
                    right_rotate_func(tree, w)
                    w = x.parent.right_child
                w.color = x.parent.color
                x.parent.black = True
                w.right_child.black = True
                left_rotate_func(tree, x.parent)
                x = tree.root
        else:
            w = x.parent.left_child
            if w.red:
                w.black = True
                x.parent.red = True
                right_rotate_func(tree, x.parent)
                w = x.parent.left_child

            if w.right_child.black and w.left_child.black:
                w.red = True
                x = x.parent
            else:
                if w.left_child.black:
                    w.right_child.black = True
                    w.red = True
                    left_rotate_func(tree, w)
                    w = x.parent.left_child
                w.color = x.parent.color
                x.parent.black = True
                w.left_child.black = True
                right_rotate_func(tree, x.parent)
                x = tree.root
    x.black = True


def transplant(tree, a_node: RBTreeNode, a_replacement: RBTreeNode):
    u = a_node
    v = a_replacement
    if u.parent is tree.nil:
        tree.root = v
    elif u is u.parent.left_child:
        u.parent.left_child = v
    else:
        u.parent.right_child = v
    v.parent = u.parent


def tree_successor(tree: RBTree, node: RBTreeNode) -> RBTreeNode:
    return node.right_child and tree_minimum(tree, node.right_child)


def tree_minimum(tree: RBTree, node: RBTreeNode) -> RBTreeNode:
    tree_nil = tree.nil
    last = node
    current = node.left_child
    while current is not tree_nil:
        last = current
        current = current.left_child
    return last


def delete_node(tree: RBTree, node: RBTreeNode, transplant_func=transplant, fixup_func=rb_delete_fixup):
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
            z.right_child.parent = y
        transplant(tree, z, y)
        y.left_child = z.left_child
        y.left_child.parent = y
        y.color = z.color
    if y_original_color is "black":
        fixup_func(tree, x)
    tree.nil.parent = None


