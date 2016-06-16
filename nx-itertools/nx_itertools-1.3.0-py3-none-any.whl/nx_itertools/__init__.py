"""A drop-in replacement for itertools that adds the Python recipes from the
itertools documentation page along with some extras.
"""
from itertools import *         # pylint: disable=wildcard-import
from .recipes import (
    all_equal, consume, dotproduct, first_true, flatten, grouper, iter_except,
    ncycles, nth, padnone, quantify, random_combination,
    random_combination_with_replacement, random_permutation, random_product,
    repeatfunc, roundrobin, tabulate, tail, take, unique_everseen,
    unique_justseen)
from .extra import (
    chunk, divide, divide_sizes, multi_map, pairwise, partition, powerset,
    split)
