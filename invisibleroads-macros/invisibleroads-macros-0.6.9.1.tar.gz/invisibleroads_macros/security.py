import random
import string


def make_random_string(length, with_punctuation=False, with_spaces=False):
    alphabet = string.digits + string.letters
    if with_punctuation:
        alphabet += string.punctuation
    if with_spaces:
        alphabet += ' '
    return ''.join(random.choice(alphabet) for x in xrange(length))
