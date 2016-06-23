from termcolor import colored
from intervaltree.bs_tree import *


def get_diagram_elements(a_root_node):
    result = [
        (
            _.key,
            _.depth,
            BSTreeNode.get_relationship_between_nodes(_, _.parent),
            _.color,
        )
        for _ in BSTreeNode.preorder_walk(a_root_node, False)
        ]
    return result


def print_tree_diagram(a_tree):
    print('***')
    for node in get_diagram_elements(a_tree.root):
        color = node[3]
        if color == "black":
            color = "blue"
        relationship = node[2][0] if node[2] else "root"
        prefix = '+' * node[1]
        print(prefix + relationship, colored(node[0], color))
    print('***')
