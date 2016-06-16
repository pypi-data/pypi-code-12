"""
Lookup ids
"""
from functools import lru_cache
# pylint: disable=no-member

class RelationsError(ValueError):
    "A relation value error"
    pass

@lru_cache()
def get_linked_ids(item_id, upwards=False):
    "get the ids of the items that are linked as item two."
    from ..tools import models
    query = models.Item.objects.filter(id=item_id)
    if not query.exists():
        raise RelationsError("Item id '%s' does not exist." % item_id)

    values = list()
    if upwards:
        values.append('linked_as_two__item_one')
    else:
        values.append('linked_as_one__item_two')

    ids = query.values_list(*values, flat=True)
    ids = list(ids)
    while None in ids:
        ids.remove(None)

    return ids

def get_work(temp, index):
    "Go through the index and return the last indexed one."
    path = index[::]
    work = temp
    while len(path) > 0:
        work = work[path.pop(0)]

    return work


def _process_todo(todo, done, work, upwards=False):
    "process the todo list."
    symbol_infinity = '∞'
    # The symbols ^ and $ are inspired from Regular Expressions where they
    # represent the beginning and end of a line.
    if upwards:
        symbol_endpoint = '^'
    else:
        symbol_endpoint = '$'

    index = todo.pop(0)
    item_id = index[-1]
    done.add(item_id)

    links = get_linked_ids(item_id, upwards)

    if len(links) == 0:
        # This link is an end point, e.g. no further connections.
        work = get_work(work, index[:-1])
        work[item_id] = symbol_endpoint
    else:
        # This link has connected nodes, process each node and append the new
        # nodes to the todo list.
        work = get_work(work, index)
        for link in links:
            if link in done:
                # Already saw this item earlier, thus it is an infinite loop.
                work[link] = symbol_infinity
                continue

            work[link] = dict()
            append_index = index[::] + [link]
            todo.append(append_index)

@lru_cache()
def get_nodes_recursive_from(base_id, upwards=False):
    "Return connected nodes recursively starting from base_id."
    # But using a non-recursive process to prevent max recursion error.
    # By default we go forwards, i.e. return nodes that have this node as a
    # parent, specifying upwards=True, makes it go the other way, i.e. nodes
    # that have this node as a child.
    work = {}
    done = set()
    todo = list() # Todo is a list of index lists, see 'get_work' function.

    # Set up the first working item
    todo.append([base_id,])
    work[base_id] = dict()

    while len(todo) > 0:
        # The _process_todo will add items to the todo list when it finds
        # related nodes. This is the way we can recursively walk through the
        # dependencies without resorting to recursive function calling.
        _process_todo(todo, done, work, upwards)

    return work


