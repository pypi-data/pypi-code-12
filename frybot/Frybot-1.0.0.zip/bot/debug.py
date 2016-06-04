"""Debug file
prints system messages in console for debug purposes"""
from conf.config import DEBUG


def print_debug(message):
    """debug function
    :param: message
    :return: """
    if DEBUG:
        print(message)
