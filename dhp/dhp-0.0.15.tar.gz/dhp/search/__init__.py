"""search type utilities"""
# https://gist.github.com/kirbyfan64/5fad06f7a70e6420bb8c
# http://blog.amjith.com/fuzzyfinder-in-10-lines-of-python

# std py3k stanza
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals


def fuzzy_distance(needle, straw):
    '''calculate distance between needle and a straw from the haystack.

    Args:
        needle (str): The thing to match
        straw (str): The thing to match against

    Returns:
        (int): A distance of 0 indicates a search failure on one or more chars
        in needle.  The lower the distance the closer the match, matching
        earlier and closer together results in a shorter distance.'''
    # finding complete needle term together is closer than seperated
    try:
        return straw.lower().index(needle.lower()) + 1
    except ValueError:
        pass

    last_match = 0
    distance = len(straw)  # penalty for not being adjoining
    for char in needle:
        try:
            last_match += straw[last_match:].lower().index(char.lower())
            distance += last_match
        except ValueError:
            return 0
    return distance


def fuzzy_search(needle, haystack):
    '''Return a list of elements from haystack, ranked by distance from
    needle.

    Args:
        needle (str): The thing to match.
        haystack (list): A list of strings to match against.

    Returns:
        (list): Of strings, ranked by distance, that fuzzy match needle to one
            degree or another.

    Example::

        corpus = ['django_migrations.py',
                  'django_admin_log.py',
                  'main_generator.py',
                  'migrations.py',
                  'api_user.doc',
                  'user_group.doc',
                  'accounts.txt',
                  ]
        assert fuzzy_search('mig', corpus) == ['migrations.py',
                                               'django_migrations.py',
                                               'main_generator.py',
                                               'django_admin_log.py']

    '''
    # decorate
    intermediate = []
    for straw in haystack:
        distance = fuzzy_distance(needle, straw)
        if distance:
            intermediate.append((distance, straw))
    # sort by distance
    intermediate.sort(key=lambda x: x[0])
    # undecorate and return
    return [x[1] for x in intermediate]
