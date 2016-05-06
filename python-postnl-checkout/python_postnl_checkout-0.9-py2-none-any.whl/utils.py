""" Common helpers. """


def contains_any(key, values):
    """ Returns True if any of values is in key. """

    for value in values:
        if value in key:
            return True

    return False
