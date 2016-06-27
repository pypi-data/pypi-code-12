from pylib.misc import functions
import itertools
import re


class Engine(list):
    """Stores a list of search handlers"""
    pass


def search_with(engine, criteria):
    """
    Adds a search handler that handles only queries that pass the given
    criteria.
    """
    def decorator(f):
        engine.append(functions.maybe(f, criteria))
        return f
    return decorator


def search_all(engine):
    """Handles queries with no query parameter. Can only be set once."""
    def decorator(f):
        setattr(engine, 'all_handler', f)
        return f
    return decorator


def search(engine, query, *args, **kwargs):
    """
    Generates a reduced result of all the results of all the handlers that of
    which the query pass their criteria.
    """
    if query is None:
        if hasattr(engine, 'all_handler'):
            return engine.all_handler(*args, **kwargs)
        else:
            return []

    # mapping the mapped results in cases of None
    results = [[] if x is None else x for x in [f(query.strip(), *args, **kwargs) for f in engine]]
    return list(itertools.chain(*results))


def regex_criteria(regex, match=False):
    """Create a function to test queries based on the given regex."""
    regex = re.compile(regex)

    def criteria(query):
        return bool(regex.match(query) if match else regex.search(query))
    return criteria
