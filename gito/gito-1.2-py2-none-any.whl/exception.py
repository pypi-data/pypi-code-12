import sys

class GitoException(Exception):
    def __init__(self, message):
        print message
        sys.exit(0)
